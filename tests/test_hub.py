# -*- coding: utf-8 -*-
"""Tests du serveur du tableau de bord (hub.py) : ce qui dépend du système
(Windows ou Linux) passe par systeme.py. Fenêtre « application », programmes
lancés détachés, tuiles ouvertes, gadget Odoo réservé à Windows, et système
annoncé à la page. Les branches Linux sont simulées (sauf mention)."""
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # aide.py, quel que soit le lancement

from aide import ConfigTemporaire, ServeurTest  # noqa: E402

import hub  # noqa: E402
import systeme  # noqa: E402


class TestLancer(unittest.TestCase):
    def setUp(self):
        self.dossier = tempfile.mkdtemp(prefix="mes-outils-hub-")

    def tearDown(self):
        shutil.rmtree(self.dossier, ignore_errors=True)

    def fichier(self, nom):
        chemin = os.path.join(self.dossier, nom)
        with open(chemin, "w", encoding="utf-8") as f:
            f.write("x")
        return chemin

    def test_fenetre_appli_par_systeme(self):
        with mock.patch.object(hub.systeme, "ouvrir_fenetre_appli") as fenetre:
            hub.ouvrir_fenetre_appli("http://127.0.0.1:8760/", 1180, 800)
        fenetre.assert_called_once_with("http://127.0.0.1:8760/", 1180, 800)

    @unittest.skipUnless(sys.platform == "win32", "drapeaux de Windows (valent 0 ailleurs)")
    def test_fenetre_appli_sous_windows(self):
        """Windows simulé : Edge en mode --app, détaché, comme avant."""
        with mock.patch.object(systeme, "WINDOWS", True), mock.patch.object(systeme, "LINUX", False), \
                mock.patch.object(systeme, "navigateur_chromium", return_value=r"C:\Edge\msedge.exe"), \
                mock.patch.object(systeme.subprocess, "Popen") as popen:
            hub.ouvrir_fenetre_appli("http://127.0.0.1:8760/")
        args, options = popen.call_args
        self.assertEqual(args[0], [r"C:\Edge\msedge.exe", "--app=http://127.0.0.1:8760/", "--window-size=1360,860"])
        self.assertEqual(options["creationflags"], 0x00000008 | 0x00000200)

    def test_fenetre_appli_sous_linux(self):
        """Linux simulé : Chrome en mode --app avec sa classe pour le dock, sans creationflags."""
        with mock.patch.object(systeme, "WINDOWS", False), mock.patch.object(systeme, "LINUX", True), \
                mock.patch.object(systeme, "navigateur_chromium", return_value="/usr/bin/google-chrome"), \
                mock.patch.object(systeme.subprocess, "Popen") as popen:
            hub.ouvrir_fenetre_appli("http://127.0.0.1:8760/")
        args, options = popen.call_args
        self.assertEqual(args[0][:2], ["/usr/bin/google-chrome", "--app=http://127.0.0.1:8760/"])
        self.assertIn("--class=mes-outils", args[0])
        self.assertNotIn("creationflags", options)
        self.assertTrue(options["start_new_session"])
        # Aucun navigateur Chromium : un onglet du navigateur par défaut.
        with mock.patch.object(systeme, "navigateur_chromium", return_value=None), \
                mock.patch.object(systeme.webbrowser, "open") as ouvrir:
            hub.ouvrir_fenetre_appli("http://127.0.0.1:8760/")
        ouvrir.assert_called_once_with("http://127.0.0.1:8760/")

    @unittest.skipUnless(sys.platform == "win32", "drapeaux de Windows (valent 0 ailleurs)")
    def test_lancer_detache_sous_windows(self):
        """Windows simulé : mêmes drapeaux qu'avant (détaché, sans console), commande inchangée."""
        with mock.patch.object(systeme, "WINDOWS", True), mock.patch.object(systeme.subprocess, "Popen") as popen:
            hub.lancer_detache("serveur.exe --port 8765", "C:\\outil")
        args, options = popen.call_args
        self.assertEqual(args[0], "serveur.exe --port 8765", "Windows : la ligne de commande est gardée telle quelle")
        self.assertEqual(options["cwd"], "C:\\outil")
        self.assertEqual(options["creationflags"], 0x00000008 | 0x00000200 | 0x08000000)

    def test_lancer_detache_sous_linux(self):
        """Linux simulé : une commande en une ligne est découpée (jamais de shell), sans creationflags."""
        with mock.patch.object(systeme, "WINDOWS", False), mock.patch.object(systeme.subprocess, "Popen") as popen:
            hub.lancer_detache("python3 'mon serveur.py' --port 8765", "")
        args, options = popen.call_args
        self.assertEqual(args[0], ["python3", "mon serveur.py", "--port", "8765"])
        self.assertIsNone(options["cwd"])
        self.assertNotIn("creationflags", options)
        self.assertNotIn("shell", options)
        self.assertTrue(options["start_new_session"])
        with mock.patch.object(systeme, "WINDOWS", False), mock.patch.object(systeme.subprocess, "Popen") as popen:
            hub.lancer_detache(["/opt/outil/serveur", "--port", "8765"])
        self.assertEqual(popen.call_args[0][0], ["/opt/outil/serveur", "--port", "8765"], "une liste reste une liste")

    def test_tuile_fichier_ou_dossier(self):
        chemin = self.fichier("notes.pdf")
        outils = {"outils": [{"id": "a", "type": "fichier", "cible": chemin},
                             {"id": "b", "type": "dossier", "cible": self.dossier},
                             {"id": "c", "type": "fichier", "cible": os.path.join(self.dossier, "absent.pdf")}]}
        with ConfigTemporaire(outils), mock.patch.object(hub.systeme, "ouvrir") as ouvrir:
            hub.lancer_outil("a")
            hub.lancer_outil("b")
            with self.assertRaises(FileNotFoundError):
                hub.lancer_outil("c")
        self.assertEqual([c[0][0] for c in ouvrir.call_args_list], [chemin, self.dossier])

    def test_tuile_programme_sous_linux(self):
        """Linux simulé : un exécutable est lancé directement, un document ouvert par xdg-open."""
        programme = self.fichier("demarrer.sh")
        document = self.fichier("notes.pdf")
        with mock.patch.object(hub.systeme, "WINDOWS", False), \
                mock.patch.object(hub.os, "access", return_value=True), \
                mock.patch.object(hub.systeme, "lancer_detache") as lancer, \
                mock.patch.object(hub.systeme, "ouvrir") as ouvrir:
            hub.ouvrir_cible(programme)
            hub.ouvrir_cible(document)
            hub.ouvrir_cible(self.dossier)
        lancer.assert_called_once_with([programme], dossier=self.dossier)
        self.assertEqual([c[0][0] for c in ouvrir.call_args_list], [document, self.dossier])

    def test_tuile_programme_sous_windows(self):
        """Windows simulé : tout passe par l'ouverture habituelle (os.startfile)."""
        programme = self.fichier("outil.exe")
        with mock.patch.object(hub.systeme, "WINDOWS", True), \
                mock.patch.object(hub.systeme, "lancer_detache") as lancer, \
                mock.patch.object(hub.systeme, "ouvrir") as ouvrir:
            hub.ouvrir_cible(programme)
        lancer.assert_not_called()
        ouvrir.assert_called_once_with(programme)

    def test_tuile_commande(self):
        outils = {"outils": [{"id": "x", "type": "commande", "cible": ["outil", "--vite"], "dossier": self.dossier}]}
        with ConfigTemporaire(outils), mock.patch.object(hub.systeme, "lancer_detache") as lancer:
            hub.lancer_outil("x")
        lancer.assert_called_once_with(["outil", "--vite"], dossier=self.dossier)

    @unittest.skipUnless(sys.platform.startswith("linux"), "vrai Linux seulement")
    def test_vrai_linux_sans_creationflags(self):
        """Sur un vrai Linux : un programme détaché démarre (sans creationflags)."""
        processus = systeme.lancer_detache([sys.executable, "-c", "pass"])
        self.assertEqual(processus.wait(timeout=30), 0)


class TestRoutes(ServeurTest):
    def test_onglets_annonce_le_systeme(self):
        with ConfigTemporaire():
            statut, r = self.get("/api/onglets")
            self.assertEqual(statut, 200)
            self.assertEqual(r["systeme"], "windows" if sys.platform == "win32" else "linux")
            with mock.patch.object(hub.systeme, "WINDOWS", False):
                self.assertEqual(self.get("/api/onglets")[1]["systeme"], "linux")
            with mock.patch.object(hub.systeme, "WINDOWS", True):
                self.assertEqual(self.get("/api/onglets")[1]["systeme"], "windows")

    def test_gadget_odoo_windows_seulement(self):
        with ConfigTemporaire(), mock.patch.object(hub.systeme, "WINDOWS", False), \
                mock.patch.object(hub.systeme, "ouvrir") as ouvrir:
            statut, r = self.post("/api/gadget", {})
        self.assertEqual((statut, r["erreur"]), (400, "Le gadget « Serveurs Odoo » complet ne fonctionne que sous Windows."))
        ouvrir.assert_not_called()

    def test_gadget_odoo_sous_windows(self):
        dossier = tempfile.mkdtemp(prefix="mes-outils-gadget-")
        try:
            faux = mock.Mock(__file__=os.path.join(dossier, "gestion_serveurs.py"))
            with ConfigTemporaire(), mock.patch.object(hub.systeme, "WINDOWS", True), \
                    mock.patch.object(hub, "gadget", return_value=faux), \
                    mock.patch.object(hub.systeme, "ouvrir") as ouvrir:
                statut, _ = self.post("/api/gadget", {})
            self.assertEqual(statut, 200)
            ouvrir.assert_called_once_with(os.path.join(dossier, "Gestion serveurs Odoo.bat"))
        finally:
            shutil.rmtree(dossier, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
