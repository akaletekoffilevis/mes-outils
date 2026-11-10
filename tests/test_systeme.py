# -*- coding: utf-8 -*-
"""Tests de la couche système commune (Windows et Linux)."""
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outil"))
import systeme  # noqa: E402


class TestFiltres(unittest.TestCase):
    def test_filtre_windows_lu(self):
        paires = systeme.lire_filtre("Images (*.png;*.jpg)|*.png;*.jpg|Tous les fichiers (*.*)|*.*")
        self.assertEqual(paires, [("Images (*.png;*.jpg)", ["*.png", "*.jpg"]), ("Tous les fichiers (*.*)", ["*.*"])])

    def test_filtre_vide(self):
        self.assertEqual(systeme.lire_filtre(None), [("Tous les fichiers (*.*)", ["*.*"])])
        self.assertEqual(systeme.lire_filtre("|"), [("Tous les fichiers", ["*"])])

    def test_depart_existant(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(systeme.depart_existant(os.path.join(d, "absent", "x.pdf")), os.path.normpath(d))
        self.assertEqual(systeme.depart_existant(""), "")


class TestFenetresLinux(unittest.TestCase):
    def test_commande_zenity(self):
        args = systeme._zenity_fichiers("Choisir", "/home/alex/Documents", True,
                                         "Images (*.png;*.jpg)|*.png;*.jpg|Tous|*.*")
        self.assertEqual(args[:2], ["zenity", "--file-selection"])
        self.assertIn("--multiple", args)
        self.assertIn("--filename=/home/alex/Documents/", args)
        self.assertIn("--file-filter=Images (*.png;*.jpg) | *.png *.jpg", args)
        self.assertIn("--file-filter=Tous | *", args, "le motif *.* devient * sous Linux")

    def test_commande_kdialog(self):
        args = systeme._kdialog_fichiers("Choisir", "", False, "PDF (*.pdf)|*.pdf")
        self.assertEqual(args[0], "kdialog")
        self.assertNotIn("--multiple", args)
        self.assertEqual(args[-1], "*.pdf|PDF (*.pdf)")

    def test_choisir_fichiers_linux_garde_les_fichiers_existants(self):
        with tempfile.TemporaryDirectory() as d:
            vrai = os.path.join(d, "a.pdf")
            open(vrai, "w").close()
            with mock.patch.object(systeme, "WINDOWS", False), \
                    mock.patch.object(systeme, "outil_de_fenetres", return_value="zenity"), \
                    mock.patch.object(systeme, "_executer_fenetre", return_value=vrai + "\n/absent/b.pdf\n") as ex:
                self.assertEqual(systeme.choisir_fichiers("Titre", d), [vrai])
            self.assertEqual(ex.call_args[0][0][0], "zenity")

    def test_sans_outil_de_fenetre_message_clair(self):
        with mock.patch.object(systeme, "WINDOWS", False), mock.patch.object(systeme, "outil_de_fenetres", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "zenity"):
                systeme.choisir_fichiers()
            with self.assertRaisesRegex(RuntimeError, "zenity"):
                systeme.choisir_dossier()

    def test_kde_prefere_kdialog(self):
        with mock.patch.dict(os.environ, {"XDG_CURRENT_DESKTOP": "KDE"}), \
                mock.patch.object(systeme.shutil, "which", side_effect=lambda n: "/usr/bin/" + n):
            self.assertEqual(systeme.outil_de_fenetres(), "kdialog")
        with mock.patch.dict(os.environ, {"XDG_CURRENT_DESKTOP": "ubuntu:GNOME"}), \
                mock.patch.object(systeme.shutil, "which", side_effect=lambda n: "/usr/bin/" + n):
            self.assertEqual(systeme.outil_de_fenetres(), "zenity")


class TestProcessus(unittest.TestCase):
    def test_processus_vivant(self):
        self.assertTrue(systeme.processus_vivant(os.getpid()))
        self.assertFalse(systeme.processus_vivant(0))
        self.assertFalse(systeme.processus_vivant("pas un nombre"))

    def test_options_hors_windows_sans_creationflags(self):
        with mock.patch.object(systeme, "WINDOWS", False):
            self.assertEqual(systeme.options_sans_fenetre(), {})
            self.assertEqual(systeme.options_detache(), {"start_new_session": True, "close_fds": True})

    def test_options_windows(self):
        with mock.patch.object(systeme, "WINDOWS", True):
            self.assertIn("creationflags", systeme.options_detache())

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux seulement")
    def test_enfants_et_arret_linux(self):
        import subprocess
        p = subprocess.Popen(["sh", "-c", "sleep 30 & sleep 30"], start_new_session=True)
        try:
            import time
            time.sleep(0.3)
            self.assertTrue(systeme.enfants_linux(p.pid))
            ok, _ = systeme.arreter_processus(p.pid)
            self.assertTrue(ok)
        finally:
            p.kill()
            p.wait()


class TestNavigateur(unittest.TestCase):
    def test_linux_cherche_chrome_puis_chromium(self):
        trouves = {"chromium": "/usr/bin/chromium"}
        with mock.patch.object(systeme, "WINDOWS", False), \
                mock.patch.object(systeme.shutil, "which", side_effect=trouves.get):
            self.assertEqual(systeme.navigateur_chromium(), "/usr/bin/chromium")
            self.assertEqual(systeme.nom_navigateur(), "Chromium")

    def test_linux_sans_navigateur_pdf_impossible(self):
        with mock.patch.object(systeme, "WINDOWS", False), mock.patch.object(systeme, "navigateur_chromium", return_value=None):
            with self.assertRaisesRegex(ValueError, "Chrome ou Chromium"):
                systeme.html_vers_pdf("a.html", "a.pdf", "profil")

    def test_dossier_snap(self):
        with mock.patch.object(systeme, "WINDOWS", False):
            self.assertEqual(systeme.dossier_snap("/snap/bin/chromium"),
                             os.path.join(os.path.expanduser("~"), "snap", "chromium", "common"))
            self.assertIsNone(systeme.dossier_snap("/usr/bin/google-chrome"))
            self.assertIsNone(systeme.dossier_snap(None))

    def test_pdf_snap_travaille_dans_son_dossier(self):
        with tempfile.TemporaryDirectory() as d:
            source = os.path.join(d, "facture.html")
            with open(source, "w", encoding="utf-8") as f:
                f.write("<p>Facture</p>")
            bac = os.path.join(d, "snap", "chromium", "common")
            vus = {}

            def faux_imprimer(navigateur, src, sortie, profil, delai):
                vus["src"], vus["profil"] = src, profil
                with open(sortie, "wb") as f:
                    f.write(b"%PDF-1.7")
            sortie = os.path.join(d, "Factures", "FAC-1.pdf")
            os.makedirs(os.path.dirname(sortie))
            with mock.patch.object(systeme, "WINDOWS", False), \
                    mock.patch.object(systeme, "navigateur_chromium", return_value="/snap/bin/chromium"), \
                    mock.patch.object(systeme, "dossier_snap", return_value=bac), \
                    mock.patch.object(systeme, "_imprimer", side_effect=faux_imprimer):
                systeme.html_vers_pdf(source, sortie, os.path.join(d, "profil"))
            self.assertTrue(vus["src"].startswith(bac), "le snap ne lit que dans son dossier")
            self.assertTrue(vus["profil"].startswith(bac))
            self.assertTrue(os.path.isfile(sortie))
            self.assertEqual(os.listdir(bac), [], "dossier de travail nettoyé")

    def test_fenetre_appli_linux_classe(self):
        with mock.patch.object(systeme, "WINDOWS", False), mock.patch.object(systeme, "LINUX", True), \
                mock.patch.object(systeme, "navigateur_chromium", return_value="/usr/bin/google-chrome"), \
                mock.patch.object(systeme.subprocess, "Popen") as popen:
            systeme.ouvrir_fenetre_appli("http://127.0.0.1:8760/")
        args, kwargs = popen.call_args
        self.assertIn("--app=http://127.0.0.1:8760/", args[0])
        self.assertIn("--class=mes-outils", args[0])
        self.assertNotIn("creationflags", kwargs)


class TestSecretsLinux(unittest.TestCase):
    def test_secret_tool_sans_secretstorage(self):
        appels = []

        def faux_run(args, **kw):
            appels.append((args, kw))
            return mock.Mock(returncode=0, stdout="jeton" if args[1] == "lookup" else "")
        with mock.patch.object(systeme, "WINDOWS", False), mock.patch.object(systeme, "_secretstorage", return_value=None), \
                mock.patch.object(systeme.shutil, "which", return_value="/usr/bin/secret-tool"), \
                mock.patch.object(systeme.subprocess, "run", side_effect=faux_run):
            self.assertTrue(systeme.secret_ecrire("MesOutils:github", "alex", "jeton"))
            self.assertEqual(systeme.secret_lire("MesOutils:github"), "jeton")
            systeme.secret_supprimer("MesOutils:github")
        self.assertEqual([a[0][1] for a in appels], ["store", "lookup", "clear"])
        self.assertEqual(appels[0][1]["input"], "jeton", "le secret passe par l'entrée standard, jamais en argument")
        self.assertNotIn("jeton", appels[0][0])

    def test_trousseau_verrouille_lecture_vide(self):
        with mock.patch.object(systeme, "WINDOWS", False), \
                mock.patch.object(systeme, "_secretstorage", side_effect=systeme.ErreurSecret("verrouillé")):
            self.assertIsNone(systeme.secret_lire("x"))
            self.assertFalse(systeme.secret_ecrire("x", "u", "s"))

    def test_nom_du_coffre(self):
        with mock.patch.object(systeme, "WINDOWS", False):
            self.assertEqual(systeme.nom_du_coffre(), "le trousseau du bureau")


class TestTerminal(unittest.TestCase):
    def test_gnome_terminal_avec_commande(self):
        with mock.patch.object(systeme, "WINDOWS", False), \
                mock.patch.dict(os.environ, {"XDG_CURRENT_DESKTOP": "ubuntu:GNOME"}), \
                mock.patch.object(systeme.shutil, "which",
                                  side_effect=lambda n: "/usr/bin/" + n if n in ("gnome-terminal", "xterm") else None), \
                mock.patch.object(systeme, "lancer_detache") as lance:
            self.assertTrue(systeme.ouvrir_terminal("/home/alex/projet", ["ssh", "serveur"]))
        args = lance.call_args[0][0]
        self.assertEqual(args, ["gnome-terminal", "--working-directory=/home/alex/projet", "--", "ssh", "serveur"])

    def test_aucun_terminal(self):
        with mock.patch.object(systeme, "WINDOWS", False), mock.patch.object(systeme.shutil, "which", return_value=None):
            self.assertFalse(systeme.ouvrir_terminal("/tmp"))


class TestDossiers(unittest.TestCase):
    def test_donnees_linux_xdg(self):
        with mock.patch.object(systeme, "WINDOWS", False), mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": "/home/alex/.config"}):
            self.assertEqual(systeme.dossier_donnees_utilisateur(), os.path.join("/home/alex/.config", "mes-outils"))


if __name__ == "__main__":
    unittest.main()
