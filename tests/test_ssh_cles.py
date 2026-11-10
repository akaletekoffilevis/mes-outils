# -*- coding: utf-8 -*-
"""Tests des serveurs SSH (ssh_cles.py) : vérification des saisies, blocs du
fichier ~/.ssh/config, petit programme « askpass » et commandes ssh, sous
Windows et sous Linux (branches Linux simulées). ssh n'est jamais lancé pour
de vrai : subprocess.run est remplacé, et ~/.ssh par un dossier temporaire."""
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from aide import ConfigTemporaire  # noqa: F401  (ajoute outil/ au chemin)

import ssh_cles  # noqa: E402
import systeme  # noqa: E402

LINUX = sys.platform.startswith("linux")
SERVEUR = {"nom": "Serveur Web", "alias": "serveur-web", "hote": "192.0.2.10", "port": 2222,
           "utilisateur": "deploy", "cle": "/home/test/.ssh/mesoutils_serveur-web"}


class BaseSSH(unittest.TestCase):
    """~/.ssh et le dossier des données dans un dossier temporaire."""

    def setUp(self):
        self.dossier = tempfile.mkdtemp(prefix="mo-ssh-")
        ssh = os.path.join(self.dossier, ".ssh")
        self.patchs = [mock.patch.object(ssh_cles, "DOSSIER_SSH", ssh),
                       mock.patch.object(ssh_cles, "CONFIG_SSH", os.path.join(ssh, "config")),
                       mock.patch.object(ssh_cles, "ASKPASS_CMD", os.path.join(self.dossier, "ssh_askpass.cmd")),
                       mock.patch.object(ssh_cles, "ASKPASS_SH", os.path.join(self.dossier, "ssh_askpass.sh"))]
        for p in self.patchs:
            p.start()

    def tearDown(self):
        for p in self.patchs:
            p.stop()
        shutil.rmtree(self.dossier, ignore_errors=True)


class TestSaisies(unittest.TestCase):
    def test_verifier(self):
        self.assertEqual(ssh_cles._verifier(" Web ", "http://192.0.2.10:1901/", "", "deploy"),
                         ("Web", "192.0.2.10", 22, "deploy"), "adresse web collée telle quelle")
        for nom, hote, port, utilisateur in (("", "h", 22, "u"), ("a", "h b", 22, "u"), ("a", "h", 70000, "u"),
                                             ("a", "h", "x", "u"), ("a", "h", 22, "u;rm")):
            with self.assertRaises(ssh_cles.ErreurSSH, msg=repr((nom, hote, port, utilisateur))):
                ssh_cles._verifier(nom, hote, port, utilisateur)

    def test_alias(self):
        self.assertEqual(ssh_cles.alias_depuis("Serveur Élégant n°2"), "serveur-elegant-n-2")
        with self.assertRaises(ssh_cles.ErreurSSH):
            ssh_cles.alias_depuis("!!!")


class TestConfig(BaseSSH):
    def test_bloc_pose_et_retire_sans_toucher_au_reste(self):
        os.makedirs(ssh_cles.DOSSIER_SSH)
        with open(ssh_cles.CONFIG_SSH, "w", encoding="utf-8", newline="\n") as f:
            f.write("Host perso\n    HostName exemple.invalid")
        ssh_cles._poser_bloc(SERVEUR)
        ssh_cles._poser_bloc(SERVEUR)  # une seconde fois : remplacé, pas doublé
        texte = ssh_cles._lire_config()
        self.assertTrue(texte.startswith("Host perso\n    HostName exemple.invalid\n"))
        self.assertEqual(texte.count("Host serveur-web"), 1)
        self.assertIn("    Port 2222\n", texte)
        self.assertIn("    IdentityFile ~/.ssh/mesoutils_serveur-web\n", texte)
        ssh_cles._ecrire_config(ssh_cles._retirer_bloc(texte, "serveur-web"))
        self.assertEqual(ssh_cles._lire_config(), "Host perso\n    HostName exemple.invalid\n")

    def test_droits_600_sous_linux(self):
        with mock.patch.object(systeme, "WINDOWS", False), \
                mock.patch.object(ssh_cles.os, "chmod") as chmod:
            ssh_cles._ecrire_config("Host x\n")
        chmod.assert_called_once_with(ssh_cles.CONFIG_SSH + ".tmp", 0o600)
        with mock.patch.object(systeme, "WINDOWS", True), \
                mock.patch.object(ssh_cles.os, "chmod") as chmod:
            ssh_cles._ecrire_config("Host x\n")
        chmod.assert_not_called()

    @unittest.skipUnless(LINUX, "droits Unix : vrai Linux seulement")
    def test_droits_reels(self):
        ssh_cles._ecrire_config("Host x\n")
        self.assertEqual(stat.S_IMODE(os.stat(ssh_cles.CONFIG_SSH).st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(os.stat(ssh_cles.DOSSIER_SSH).st_mode) & 0o077, 0)


class TestAskpass(BaseSSH):
    def test_linux(self):
        with mock.patch.object(systeme, "WINDOWS", False), \
                mock.patch.object(ssh_cles.os, "chmod") as chmod:
            chemin = ssh_cles._preparer_askpass()
        self.assertEqual(chemin, ssh_cles.ASKPASS_SH)
        with open(chemin, "rb") as f:
            contenu = f.read()
        self.assertEqual(contenu, ssh_cles.CONTENU_ASKPASS_SH.encode("utf-8"), "fins de ligne Unix")
        self.assertTrue(contenu.startswith(b"#!/bin/sh\n"))
        self.assertNotIn(b"python", contenu.lower())
        self.assertNotIn(b"echo", contenu, "printf : la variable n'est pas interprétée")
        chmod.assert_called_once_with(chemin, 0o700)

    def test_windows(self):
        with mock.patch.object(systeme, "WINDOWS", True):
            chemin = ssh_cles._preparer_askpass()
        self.assertEqual(chemin, ssh_cles.ASKPASS_CMD)
        with open(chemin, "rb") as f:
            self.assertIn(b"$env:MESOUTILS_SSH_SECRET)\"\r\n", f.read(), "fins de ligne Windows")

    @unittest.skipUnless(LINUX, "sh : vrai Linux seulement")
    def test_rend_le_secret_tel_quel(self):
        chemin = ssh_cles._preparer_askpass()
        self.assertEqual(stat.S_IMODE(os.stat(chemin).st_mode), 0o700)
        secret = "-n a'b\"c $HOME `id` \\x %s é"
        r = subprocess.run([chemin, "Password:"], env={"MESOUTILS_SSH_SECRET": secret, "PATH": "/usr/bin:/bin"},
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.stdout, secret + "\n")


class TestCommandes(BaseSSH):
    def _executer(self, windows, secret):
        fini = subprocess.CompletedProcess([], 0, "ok\n", "")
        with mock.patch.object(systeme, "WINDOWS", windows), \
                mock.patch.object(ssh_cles.os, "chmod"), \
                mock.patch.dict(os.environ, {"MESOUTILS_SSH_SECRET": "ancien"}), \
                mock.patch.object(ssh_cles.subprocess, "run", return_value=fini) as run:
            ssh_cles._executer(["ssh", "hote"], secret=secret)
        return run.call_args.kwargs

    def test_mot_de_passe_linux(self):
        kw = self._executer(False, "secret-é")
        env = kw["env"]
        self.assertEqual(env["SSH_ASKPASS"], ssh_cles.ASKPASS_SH)
        self.assertEqual(env["SSH_ASKPASS_REQUIRE"], "force")
        self.assertEqual(env["MESOUTILS_SSH_SECRET"], "secret-é")
        self.assertNotEqual(env.get("DISPLAY"), "mes-outils", "DISPLAY inutile sous Linux")
        self.assertNotIn("creationflags", kw, "jamais creationflags hors de Windows")
        self.assertEqual(kw["stdin"], subprocess.DEVNULL)

    def test_mot_de_passe_windows(self):
        kw = self._executer(True, "secret")
        self.assertEqual((kw["env"]["SSH_ASKPASS"], kw["env"]["DISPLAY"]), (ssh_cles.ASKPASS_CMD, "mes-outils"))
        if sys.platform == "win32":
            self.assertEqual(kw["creationflags"], 0x08000000)

    def test_sans_mot_de_passe(self):
        env = self._executer(False, None)["env"]
        self.assertNotIn("MESOUTILS_SSH_SECRET", env, "aucun secret hérité")
        self.assertNotIn("SSH_ASKPASS_REQUIRE", env)

    def test_delai(self):
        with mock.patch.object(ssh_cles.subprocess, "run", side_effect=subprocess.TimeoutExpired("ssh", 25)), \
                self.assertRaisesRegex(ssh_cles.ErreurSSH, "ne répond pas"):
            ssh_cles._executer(["ssh", "hote"])

    def test_terminal_linux(self):
        with mock.patch.object(systeme, "WINDOWS", False), \
                mock.patch.object(ssh_cles, "_trouver", return_value=SERVEUR), \
                mock.patch.object(systeme, "ouvrir_terminal", return_value=True) as terminal, \
                mock.patch.object(ssh_cles.subprocess, "Popen") as popen:
            self.assertEqual(ssh_cles.ouvrir_terminal("serveur-web"), {"ok": True})
        terminal.assert_called_once_with(commande=[ssh_cles.SSH, "serveur-web"], titre="Serveur Web")
        popen.assert_not_called()
        with mock.patch.object(systeme, "WINDOWS", False), \
                mock.patch.object(ssh_cles, "_trouver", return_value=SERVEUR), \
                mock.patch.object(systeme, "ouvrir_terminal", return_value=False), \
                self.assertRaisesRegex(ssh_cles.ErreurSSH, "Aucun terminal"):
            ssh_cles.ouvrir_terminal("serveur-web")

    def test_messages(self):
        self.assertIn("mot de passe", ssh_cles._message_erreur("deploy@192.0.2.10: Permission denied (publickey,password)."))
        self.assertIn("introuvable", ssh_cles._message_erreur(
            "ssh: Could not resolve hostname x: Name or service not known"))
        self.assertIn("port", ssh_cles._message_erreur("ssh: connect to host 192.0.2.10 port 22: Connection refused"))

    @unittest.skipUnless(LINUX, "vrai Linux seulement")
    def test_programmes_openssh(self):
        self.assertTrue(os.path.basename(ssh_cles.SSH) == "ssh" and os.path.basename(ssh_cles.SSH_KEYGEN) == "ssh-keygen")


if __name__ == "__main__":
    unittest.main()
