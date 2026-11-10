# -*- coding: utf-8 -*-
"""Coffre du système et portage Linux de coffre_windows.py, coffre.py,
mail.py et presse_papiers.py.

- coffre_windows délègue à systeme.secret_* (Windows comme Linux) ;
- les quatre modules s'importent sans ctypes.WinDLL (comme sous Linux) ;
- coffre.copier_presse_papiers choisit la bonne branche selon le système.
La copie Linux d'un secret elle-même est testée dans test_presse_papiers.py.
"""
import os
import subprocess
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # aide.py, quel que soit le lancement

from aide import OUTIL  # noqa: E402

import coffre  # noqa: E402
import coffre_windows  # noqa: E402


class TestCoffreWindowsDelegue(unittest.TestCase):
    def test_delegation(self):
        with mock.patch.object(coffre_windows.systeme, "secret_ecrire", return_value=True) as ecrire, \
                mock.patch.object(coffre_windows.systeme, "secret_lire", return_value="jeton") as lire, \
                mock.patch.object(coffre_windows.systeme, "secret_supprimer") as supprimer:
            self.assertTrue(coffre_windows.ecrire("MesOutils:github", "moi", "jeton"))
            self.assertEqual(coffre_windows.lire("MesOutils:github"), "jeton")
            self.assertIsNone(coffre_windows.supprimer("MesOutils:github"))
        ecrire.assert_called_once_with("MesOutils:github", "moi", "jeton")
        lire.assert_called_once_with("MesOutils:github")
        supprimer.assert_called_once_with("MesOutils:github")

    def test_echec_renvoie_faux(self):
        with mock.patch.object(coffre_windows.systeme, "secret_ecrire", return_value=False):
            self.assertFalse(coffre_windows.ecrire("x", "u", "s"))


class TestImportSansWindows(unittest.TestCase):
    def test_import_sans_windll(self):
        """Comme sous Linux : ctypes.WinDLL et ctypes.windll absents au chargement."""
        script = (
            "import ctypes, sys\n"
            "for nom in ('WinDLL', 'windll', 'WINFUNCTYPE', 'oledll', 'OleDLL'):\n"
            "    if hasattr(ctypes, nom): delattr(ctypes, nom)\n"
            f"sys.path.insert(0, {OUTIL!r})\n"
            "import coffre_windows, mail, coffre, presse_papiers\n"
            "print('ok')\n"
        )
        r = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=60,
                           env=dict(os.environ, PYTHONUTF8="1"))
        self.assertEqual(r.returncode, 0, f"import impossible sans WinDLL :\n{r.stderr}")
        self.assertIn("ok", r.stdout)

    def test_coffre_sans_presse_papiers_windows_au_chargement(self):
        self.assertFalse(hasattr(coffre, "_u32"), "plus de user32 chargé au niveau du module")


class TestCopieSelonLeSysteme(unittest.TestCase):
    def test_branche_linux(self):
        with mock.patch.object(coffre.systeme, "WINDOWS", False), \
                mock.patch.object(coffre, "_copier_windows") as windows, \
                mock.patch.object(coffre, "_copier_linux") as linux:
            coffre.copier_presse_papiers("secret", effacer_apres=30)
        linux.assert_called_once_with("secret", 30)
        windows.assert_not_called()

    def test_branche_windows(self):
        with mock.patch.object(coffre.systeme, "WINDOWS", True), \
                mock.patch.object(coffre, "_copier_windows") as windows, \
                mock.patch.object(coffre, "_copier_linux") as linux:
            coffre.copier_presse_papiers("secret")
        windows.assert_called_once_with("secret", None)
        linux.assert_not_called()


if __name__ == "__main__":
    unittest.main()
