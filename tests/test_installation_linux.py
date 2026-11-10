# -*- coding: utf-8 -*-
"""Tests de l'installation sous Linux : entrée du menu des applications,
démarrage avec la session, icône, commande lancée (AppImage ou code source).
Tout est écrit dans des dossiers XDG temporaires ; la branche Linux est
simulée (systeme.WINDOWS) pour tourner aussi sous Windows."""
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

from aide import ConfigTemporaire

import installation  # noqa: E402
import systeme  # noqa: E402


class LinuxTemporaire(unittest.TestCase):
    """Dossiers ~/.local/share et ~/.config temporaires, branche Linux."""

    def setUp(self):
        self.dossier = tempfile.mkdtemp(prefix="mes-outils-xdg-")
        self.donnees = os.path.join(self.dossier, "share")
        self.config = os.path.join(self.dossier, "config")
        self.patchs = [mock.patch.multiple(systeme, WINDOWS=False, LINUX=True),
                       mock.patch.dict(os.environ, {"XDG_DATA_HOME": self.donnees, "XDG_CONFIG_HOME": self.config}),
                       mock.patch.object(installation, "GELE", False)]
        for p in self.patchs:
            p.start()
        os.environ.pop("APPIMAGE", None)

    def tearDown(self):
        for p in reversed(self.patchs):
            p.stop()
        shutil.rmtree(self.dossier, ignore_errors=True)

    def lire(self, chemin):
        with open(chemin, encoding="utf-8") as f:
            return f.read()


class TestEntrees(LinuxTemporaire):
    def test_genres_linux(self):
        self.assertEqual(installation.genres(), ("menu", "demarrage"))
        self.assertEqual(installation.etat(), {"menu": False, "demarrage": False})

    def test_entree_du_menu(self):
        chemin = installation.creer_raccourci("menu")
        self.assertEqual(chemin, os.path.join(self.donnees, "applications", "mes-outils.desktop"))
        texte = self.lire(chemin)
        self.assertTrue(texte.startswith("[Desktop Entry]\n"))
        self.assertIn("Name=Mes outils\n", texte)
        self.assertIn("StartupWMClass=mes-outils\n", texte, "relie la fenêtre du tableau de bord à l'entrée")
        self.assertIn("Exec=" + installation.argument_exec(installation.python_fenetre()) + " "
                      + installation.argument_exec(installation.BULLE), texte, "code source : python bulle.py")
        icone = os.path.join(self.donnees, "icons", "hicolor", "256x256", "apps", "mes-outils.png")
        self.assertTrue(os.path.isfile(icone), "l'icône est installée dans le thème de l'utilisateur")
        self.assertIn(f"Icon={icone}\n", texte)
        self.assertNotIn("X-GNOME-Autostart", texte)
        self.assertEqual(installation.etat(), {"menu": True, "demarrage": False})
        installation.supprimer_raccourci("menu")
        self.assertFalse(os.path.exists(chemin))

    def test_demarrage_avec_la_session(self):
        chemin = installation.creer_raccourci("demarrage")
        self.assertEqual(chemin, os.path.join(self.config, "autostart", "mes-outils.desktop"))
        self.assertIn("X-GNOME-Autostart-enabled=true\n", self.lire(chemin))

    def test_appimage(self):
        appimage = os.path.join(self.dossier, "Mes outils", "Mes-outils-x86_64.AppImage")
        os.makedirs(os.path.dirname(appimage))
        with open(appimage, "wb") as f:
            f.write(b"\x7fELF")
        with mock.patch.dict(os.environ, {"APPIMAGE": appimage}):
            self.assertEqual(installation.commande_linux(), [os.path.abspath(appimage)])
            texte = installation.contenu_desktop("menu")
        exec_ = installation.argument_exec(os.path.abspath(appimage))
        self.assertTrue(exec_.startswith('"'), "chemin avec espace : entre guillemets")
        self.assertIn(f"Exec={exec_}\n", texte, "l'entrée lance l'AppImage, là où elle est")

    def test_genre_inconnu(self):
        with self.assertRaises(ValueError):
            installation.chemin_desktop("bureau")

    def test_argument_exec(self):
        self.assertEqual(installation.argument_exec("/usr/bin/python3"), "/usr/bin/python3")
        self.assertEqual(installation.argument_exec("/home/a/Mes outils/bulle.py"), '"/home/a/Mes outils/bulle.py"')
        self.assertEqual(installation.argument_exec("100%"), "100%%", "« % » est réservé aux codes de champ")
        self.assertEqual(installation.argument_exec('/a/$b"c'), '"/a/\\$b\\"c"')


class TestPremierLancement(LinuxTemporaire):
    def test_entree_creee_une_seule_fois(self):
        with ConfigTemporaire({"outils": []}) as cfg:
            self.assertEqual(installation.preparer_linux(), ["menu"])
            self.assertTrue(cfg.lire()["menu_linux_propose"])
            self.assertEqual(installation.preparer_linux(), [], "rien à refaire")
            installation.supprimer_raccourci("menu")
            self.assertEqual(installation.preparer_linux(), [], "retirée dans les Réglages : pas recréée")
            self.assertFalse(os.path.exists(installation.chemin_desktop("menu")))

    def test_appimage_deplacee(self):
        with ConfigTemporaire({"outils": [], "menu_linux_propose": True}):
            installation.creer_raccourci("demarrage")
            appimage = os.path.join(self.dossier, "Nouvelle.AppImage")
            with open(appimage, "wb") as f:
                f.write(b"\x7fELF")
            with mock.patch.dict(os.environ, {"APPIMAGE": appimage}):
                self.assertEqual(installation.preparer_linux(), ["demarrage"], "la commande a changé : réécrite")
                self.assertIn(installation.argument_exec(appimage), self.lire(installation.chemin_desktop("demarrage")))
                self.assertEqual(installation.preparer_linux(), [])


class TestCodeSource(LinuxTemporaire):
    def test_python_sous_linux(self):
        os.environ.pop("MES_OUTILS_PYTHON", None)
        self.assertEqual(installation.python_fenetre(), sys.executable, "pas de pythonw sous Linux")

    def test_lancer_detache(self):
        with mock.patch.object(systeme, "lancer_detache") as lancer:
            installation.lancer()
        commande = lancer.call_args.args[0]
        self.assertEqual(commande[-1], installation.BULLE)


if __name__ == "__main__":
    unittest.main()
