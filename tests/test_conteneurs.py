# -*- coding: utf-8 -*-
"""Tests de l'onglet « Docker » (conteneurs.py) : la commande docker est
toujours simulée (absente, démon arrêté, en marche)."""
import json
import subprocess
import unittest
from unittest import mock

from aide import ServeurTest

import conteneurs  # noqa: E402
import systeme  # noqa: E402

DOCKER = r"C:\Docker\docker.exe"


def ps_json():
    lignes = [
        {"ID": "a1b2c3d4e5f6" + "0" * 52, "Names": "boutique-db-1", "Image": "postgres:16", "State": "running",
         "Status": "Up 2 hours", "Ports": "0.0.0.0:5433->5432/tcp, :::5433->5432/tcp",
         "Labels": "com.docker.compose.project=boutique,com.docker.compose.service=db,"
                   "com.docker.compose.project.config_files=a.yml,b.yml", "CreatedAt": "2026-01-01"},
        {"ID": "b1b2c3d4e5f6" + "0" * 52, "Names": "boutique-web-1", "Image": "node:20", "State": "exited",
         "Status": "Exited (0) 3 days ago", "Ports": "",
         "Labels": "com.docker.compose.project=boutique,com.docker.compose.service=web", "CreatedAt": "2026-01-01"},
        {"ID": "c1b2c3d4e5f6" + "0" * 52, "Names": "cache", "Image": "redis:7", "State": "running",
         "Status": "Up 5 minutes", "Ports": "6379/tcp", "Labels": "", "CreatedAt": "2026-01-02"},
    ]
    return "\n".join(json.dumps(x) for x in lignes) + "\n"


class FauxDocker:
    """Remplace subprocess.run : répond selon les arguments, garde les appels."""

    def __init__(self, demarre=True, en_marche="false", compose_ok=True):
        self.demarre, self.en_marche, self.compose_ok = demarre, en_marche, compose_ok
        self.appels = []

    def __call__(self, commande, **kw):
        self.appels.append(commande[1:])
        a = commande[1:]

        def rep(code=0, sortie="", erreurs=""):
            return subprocess.CompletedProcess(commande, code, sortie.encode(), erreurs.encode())

        if a[0] == "version":
            return rep(0, "27.1.1\n") if self.demarre else rep(1, "", "error during connect: daemon not running")
        if a[:2] == ["ps", "-a"] and "-q" in a:
            return rep(0, "a1b2c3d4e5f6\nb1b2c3d4e5f6\n")
        if a[0] == "ps":
            return rep(0, ps_json())
        if a[0] == "inspect":
            return rep(0, self.en_marche + "\n")
        if a[0] == "logs":
            return rep(0, "2026-01-01T10:00:02.000000000Z b\n", "2026-01-01T10:00:01.000000000Z a\n")
        if a[0] == "compose":
            return rep(0) if self.compose_ok else rep(1, "", "no configuration file provided")
        if a[0] == "images":
            return rep(0, json.dumps({"Repository": "postgres", "Tag": "16", "ID": "abc", "Size": "432MB", "CreatedSince": "2 weeks ago"}))
        if a[:2] == ["system", "df"]:
            return rep(0, json.dumps({"Type": "Images", "TotalCount": "1", "Active": "1", "Size": "432MB", "Reclaimable": "0B"}))
        if a[0] in ("start", "stop", "restart", "rm"):
            return rep(0, a[-1] + "\n")
        return rep(1, "", "commande inconnue")


def avec_docker(faux, desktop=None):
    return [mock.patch.object(conteneurs, "chemin_docker", return_value=DOCKER),
            mock.patch.object(conteneurs, "chemin_desktop", return_value=desktop),
            mock.patch.object(conteneurs.subprocess, "run", side_effect=faux)]


class Patchs:
    def __init__(self, patchs):
        self.patchs = patchs

    def __enter__(self):
        for p in self.patchs:
            p.start()

    def __exit__(self, *exc):
        for p in self.patchs:
            p.stop()


class TestLecture(unittest.TestCase):
    def test_etiquettes(self):
        e = conteneurs.lire_etiquettes("a=1,fichiers=x.yml,y.yml,b=")
        self.assertEqual(e, {"a": "1", "fichiers": "x.yml,y.yml", "b": ""})
        self.assertEqual(conteneurs.lire_etiquettes(""), {})

    def test_ports(self):
        p = conteneurs.lire_ports("0.0.0.0:8080->80/tcp, :::8080->80/tcp, 5432/tcp, 127.0.0.1:9000-9001->9000-9001/tcp")
        self.assertEqual(p, [{"hote": 8080, "conteneur": 80, "proto": "tcp"},
                             {"hote": None, "conteneur": 5432, "proto": "tcp"},
                             {"hote": 9000, "conteneur": 9000, "proto": "tcp"}])
        self.assertEqual(conteneurs.lire_ports(""), [])

    def test_conteneurs_groupes(self):
        groupes = conteneurs.grouper(conteneurs.lire_conteneurs(ps_json() + "pas du json\n"))
        self.assertEqual([g["projet"] for g in groupes], ["boutique", ""], "les conteneurs sans projet à la fin")
        boutique = groupes[0]
        self.assertEqual([c["service"] for c in boutique["conteneurs"]], ["db", "web"])
        self.assertEqual(boutique["en_marche"], 1)
        self.assertEqual(boutique["conteneurs"][0]["ports"], [{"hote": 5433, "conteneur": 5432, "proto": "tcp"}])

    def test_identifiants(self):
        for bon in ("a1b2c3d4e5f6", "f" * 64, "boutique-db-1", "mon_conteneur.2"):
            self.assertEqual(conteneurs.valider_id(bon), bon)
        for mauvais in ("", "-rm", "--help", "a b", "a;b", "a&b", "../x", "a/b", "x" * 200, None, "é"):
            with self.assertRaises(ValueError, msg=repr(mauvais)):
                conteneurs.valider_id(mauvais)
        self.assertEqual(conteneurs.valider_projet("boutique_2-dev"), "boutique_2-dev")
        for mauvais in ("", "-p", "Boutique", "a b", "a;b"):
            with self.assertRaises(ValueError, msg=repr(mauvais)):
                conteneurs.valider_projet(mauvais)


class TestEtats(unittest.TestCase):
    def test_absent(self):
        with mock.patch.object(conteneurs, "chemin_docker", return_value=None), \
                mock.patch.object(conteneurs.subprocess, "run") as run:
            r = conteneurs.liste({})
            self.assertEqual((r["installe"], r["demarre"], r["groupes"]), (False, False, []))
            with self.assertRaisesRegex(conteneurs.ErreurDocker, "pas installé"):
                conteneurs.ROUTES["demarrer"]({"id": "abc123"})
        run.assert_not_called()

    def test_demon_arrete(self):
        faux = FauxDocker(demarre=False)
        with Patchs(avec_docker(faux, desktop=r"C:\Docker\Docker Desktop.exe")):
            r = conteneurs.liste({})
            self.assertEqual((r["installe"], r["demarre"], r["desktop"]), (True, False, True))
            with self.assertRaisesRegex(conteneurs.ErreurDocker, "pas démarré"):
                conteneurs.ROUTES["arreter"]({"id": "abc123"})
        self.assertEqual([a[0] for a in faux.appels], ["version", "version"], "aucune autre commande sans démon")

    def test_delai_depasse(self):
        with mock.patch.object(conteneurs, "chemin_docker", return_value=DOCKER), \
                mock.patch.object(conteneurs.subprocess, "run", side_effect=subprocess.TimeoutExpired("docker", 10)):
            self.assertFalse(conteneurs.etat()["demarre"])

    def test_lancer_desktop(self):
        with mock.patch.object(conteneurs, "chemin_desktop", return_value=None), \
                self.assertRaisesRegex(conteneurs.ErreurDocker, "introuvable"):
            conteneurs.lancer_desktop({})
        with mock.patch.object(conteneurs, "chemin_desktop", return_value=r"C:\Docker\Docker Desktop.exe"), \
                mock.patch.object(systeme, "WINDOWS", True), \
                mock.patch.object(conteneurs.os, "startfile", create=True) as startfile:
            conteneurs.lancer_desktop({})
        startfile.assert_called_once_with(r"C:\Docker\Docker Desktop.exe")


class TestActions(unittest.TestCase):
    def test_liste(self):
        faux = FauxDocker()
        with Patchs(avec_docker(faux)):
            r = conteneurs.liste({})
        self.assertEqual((r["demarre"], r["version"], r["nombre"]), (True, "27.1.1", 3))
        self.assertEqual(r["groupes"][0]["conteneurs"][0]["id"], "a1b2c3d4e5f6", "identifiant court")

    def test_actions_simples(self):
        faux = FauxDocker()
        with Patchs(avec_docker(faux)):
            for route, commande in (("demarrer", "start"), ("arreter", "stop"), ("redemarrer", "restart")):
                conteneurs.ROUTES[route]({"id": "a1b2c3d4e5f6"})
                self.assertEqual(faux.appels[-1], [commande, "a1b2c3d4e5f6"])
            nb = len(faux.appels)
            with self.assertRaises(ValueError):
                conteneurs.ROUTES["arreter"]({"id": "--all"})
        self.assertFalse([a for a in faux.appels[nb:] if a[0] != "version"], "identifiant refusé : docker n'est pas appelé")

    def test_supprimer_seulement_arrete(self):
        faux = FauxDocker(en_marche="true")
        with Patchs(avec_docker(faux)), self.assertRaisesRegex(conteneurs.ErreurDocker, "Arrêtez"):
            conteneurs.supprimer({"id": "a1b2c3d4e5f6"})
        self.assertFalse([a for a in faux.appels if a[0] == "rm"])
        faux = FauxDocker(en_marche="false")
        with Patchs(avec_docker(faux)):
            conteneurs.supprimer({"id": "a1b2c3d4e5f6"})
        self.assertEqual(faux.appels[-1], ["rm", "a1b2c3d4e5f6"], "jamais de rm -f")

    def test_journal(self):
        faux = FauxDocker()
        with Patchs(avec_docker(faux)):
            r = conteneurs.journal({"id": "boutique-db-1"})
        self.assertEqual(faux.appels[-1], ["logs", "--tail", "300", "--timestamps", "boutique-db-1"])
        self.assertEqual([x[-1] for x in r["texte"].splitlines()], ["a", "b"], "sortie et erreurs dans l'ordre")

    def test_projet(self):
        faux = FauxDocker()
        with Patchs(avec_docker(faux)):
            conteneurs.ROUTES["projet/arreter"]({"projet": "boutique"})
        self.assertEqual(faux.appels[-1], ["compose", "-p", "boutique", "stop"])
        faux = FauxDocker(compose_ok=False)
        with Patchs(avec_docker(faux)):
            conteneurs.ROUTES["projet/demarrer"]({"projet": "boutique"})
        self.assertEqual(faux.appels[-1], ["start", "a1b2c3d4e5f6", "b1b2c3d4e5f6"], "repli sans fichier compose")
        with Patchs(avec_docker(FauxDocker())), self.assertRaises(ValueError):
            conteneurs.ROUTES["projet/arreter"]({"projet": "-f x"})

    def test_ressources(self):
        with Patchs(avec_docker(FauxDocker())):
            r = conteneurs.ressources({})
        self.assertEqual(r["images"][0]["taille"], "432MB")
        self.assertEqual(r["place"][0]["type"], "Images")

    def test_erreur_docker(self):
        def echec(commande, **kw):
            if commande[1] == "version":
                return subprocess.CompletedProcess(commande, 0, b"27.1.1\n", b"")
            return subprocess.CompletedProcess(commande, 1, b"", b"Error response from daemon: No such container: x1\n")
        with mock.patch.object(conteneurs, "chemin_docker", return_value=DOCKER), \
                mock.patch.object(conteneurs.subprocess, "run", side_effect=echec), \
                self.assertRaisesRegex(conteneurs.ErreurDocker, "No such container"):
            conteneurs.ROUTES["demarrer"]({"id": "x1"})


class TestLinux(unittest.TestCase):
    """Branches Linux, simulées (passent aussi sous Windows)."""

    def setUp(self):
        self.linux = mock.patch.object(systeme, "WINDOWS", False)
        self.linux.start()

    def tearDown(self):
        self.linux.stop()

    def test_chemins(self):
        with mock.patch.object(conteneurs.shutil, "which", return_value=None), \
                mock.patch.object(conteneurs.os.path, "isfile", side_effect=lambda c: c == "/snap/bin/docker"):
            self.assertEqual(conteneurs.chemin_docker(), "/snap/bin/docker")
        with mock.patch.object(conteneurs.os.path, "isfile", side_effect=lambda c: c == conteneurs.DESKTOP_LINUX):
            self.assertEqual(conteneurs.chemin_desktop(), "/opt/docker-desktop/bin/docker-desktop")
        with mock.patch.object(conteneurs.os.path, "isfile", return_value=False):
            self.assertIsNone(conteneurs.chemin_desktop())

    def test_sans_drapeaux_windows(self):
        faux = FauxDocker()
        options = []

        def run(commande, **kw):
            options.append(kw)
            return faux(commande, **kw)

        with mock.patch.object(conteneurs, "chemin_docker", return_value="/usr/bin/docker"), \
                mock.patch.object(conteneurs.subprocess, "run", side_effect=run):
            self.assertEqual(conteneurs.liste({})["nombre"], 3)
        self.assertTrue(options and all("creationflags" not in kw for kw in options),
                        "jamais creationflags hors de Windows")

    def test_messages(self):
        refus = ("permission denied while trying to connect to the Docker daemon socket at "
                 "unix:///var/run/docker.sock: Get \"http://%2Fvar%2Frun%2Fdocker.sock/v1.45/version\"")

        def run(commande, **kw):
            return subprocess.CompletedProcess(commande, 1, b"", refus.encode())

        with mock.patch.object(conteneurs, "chemin_docker", return_value="/usr/bin/docker"), \
                mock.patch.object(conteneurs, "chemin_desktop", return_value=None), \
                mock.patch.object(conteneurs.subprocess, "run", side_effect=run):
            e = conteneurs.etat()
            self.assertFalse(e["demarre"])
            self.assertIn("groupe docker", e["erreur"])
            with self.assertRaisesRegex(conteneurs.ErreurDocker, "groupe docker"):
                conteneurs.ROUTES["arreter"]({"id": "abc123"})
        self.assertIn("systemctl start docker", conteneurs.message_linux("Cannot connect to the Docker daemon"))
        self.assertEqual(conteneurs.message_linux("", desktop=True), "Docker Desktop n'est pas démarré.")

    def test_lancer_desktop(self):
        with mock.patch.object(conteneurs, "chemin_desktop", return_value=conteneurs.DESKTOP_LINUX), \
                mock.patch.object(conteneurs.shutil, "which", return_value="/usr/bin/systemctl"), \
                mock.patch.object(systeme, "lancer_detache") as lancer:
            conteneurs.lancer_desktop({})
        lancer.assert_called_once_with(["systemctl", "--user", "start", "docker-desktop"])
        with mock.patch.object(conteneurs, "chemin_desktop", return_value=conteneurs.DESKTOP_LINUX), \
                mock.patch.object(conteneurs.shutil, "which", return_value=None), \
                mock.patch.object(systeme, "lancer_detache") as lancer:
            conteneurs.lancer_desktop({})
        lancer.assert_called_once_with([conteneurs.DESKTOP_LINUX])


class TestRoutes(ServeurTest):
    def test_docker_absent(self):
        with mock.patch.object(conteneurs, "chemin_docker", return_value=None):
            statut, r = self.post("/api/conteneurs/liste", {})
            self.assertEqual((statut, r["installe"]), (200, False))
            self.assertTrue(r["adresse"].startswith("https://www.docker.com/"))
            statut, r = self.post("/api/conteneurs/arreter", {"id": "abc"})
        self.assertEqual(statut, 400)
        self.assertIn("pas installé", r["erreur"])

    def test_en_marche(self):
        faux = FauxDocker()
        with Patchs(avec_docker(faux)):
            statut, r = self.post("/api/conteneurs/liste", {})
            self.assertEqual((statut, len(r["groupes"])), (200, 2))
            statut, r = self.post("/api/conteneurs/arreter", {"id": "a1b2c3d4e5f6"})
            self.assertEqual(statut, 200)
            statut, r = self.post("/api/conteneurs/arreter", {"id": "a b; rm"})
            self.assertEqual(statut, 400)
            statut, _ = self.post("/api/conteneurs/projet/demarrer", {"projet": "boutique"})
            self.assertEqual(statut, 200)

    def test_ouvrir(self):
        with mock.patch.object(conteneurs.webbrowser, "open") as ouvrir:
            self.assertEqual(self.post("/api/conteneurs/ouvrir", {"port": 5433})[0], 200)
            self.assertEqual(self.post("/api/conteneurs/ouvrir", {"port": 0})[0], 400)
        ouvrir.assert_called_once_with("http://localhost:5433/")


if __name__ == "__main__":
    unittest.main()
