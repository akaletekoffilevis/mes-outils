# -*- coding: utf-8 -*-
"""Tests de la bulle sous Linux (sans l'afficher) : forme ronde, instance
unique, choix bulle / icône, menu de l'icône, ouverture du tableau de bord.
Les branches Linux sont simulées (systeme.WINDOWS) pour tourner aussi sous
Windows ; le verrou fcntl n'est testé que sous Linux."""
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

from aide import ConfigTemporaire

import bulle  # noqa: E402
import hub  # noqa: E402
import icone_linux  # noqa: E402
import systeme  # noqa: E402


def sous_linux():
    return mock.patch.multiple(systeme, WINDOWS=False, LINUX=True)


class FausseRacine:
    """Ce que la bulle demande à sa fenêtre Tk, sans fenêtre."""

    def __init__(self, visible=True):
        self.visible = visible
        self.appels = []

    def state(self):
        return "normal" if self.visible else "withdrawn"

    def withdraw(self):
        self.visible = False
        self.appels.append("withdraw")

    def deiconify(self):
        self.visible = True
        self.appels.append("deiconify")

    def after(self, _delai, fonction=None, *args):
        return "x"

    def winfo_x(self):
        return 100

    def winfo_y(self):
        return 200

    def winfo_screenwidth(self):
        return 1920

    def winfo_screenheight(self):
        return 1080


def fausse_bulle(visible=True):
    b = bulle.Bulle.__new__(bulle.Bulle)
    b.racine = FausseRacine(visible)
    b.nb_mails, b.nb_ci, b.serveurs_projets = 3, None, []
    b.icone, b.icone_depuis, b.pause_jusqua = None, 0.0, 0.0
    b.largeur, b.echelle, b.d, b.marge = 84, 1.0, 64, 10
    b.mettre_forme = lambda: None
    return b


class FausseIcone:
    """Remplace icone_linux.Icone : démarre toujours, inscrite à la demande."""
    creees = []

    def __init__(self, au_clic, executer, journal=None):
        self.enregistree = True
        self.menus = []
        self.arretee = False
        FausseIcone.creees.append(self)

    def demarrer(self):
        return True

    def actualiser(self, entrees):
        self.menus.append(entrees)

    def arreter(self):
        self.arretee = True


class TestForme(unittest.TestCase):
    def test_cercle(self):
        rectangles = bulle.bandes_ellipses(64, 64, [(0, 0, 64, 64)])
        self.assertTrue(all(0 <= x and x + l <= 64 and 0 <= y and y + h <= 64 for x, y, l, h in rectangles))
        lignes = {}
        for x, y, l, h in rectangles:
            for yy in range(y, y + h):
                lignes.setdefault(yy, []).append((x, l))
        self.assertEqual(lignes[32], [(0, 64)], "le milieu du cercle est plein")
        self.assertLess(lignes[0][0][1], 20, "le haut du cercle est étroit")
        self.assertGreater(lignes[0][0][0], 20, "les coins restent transparents")
        self.assertEqual(sorted(lignes), list(range(64)), "chaque ligne a sa bande")

    def test_bulle_et_pastille(self):
        rectangles = bulle.bandes_ellipses(84, 74, [(10, 10, 74, 74), (61, 0, 83, 22)])
        bandes_haut = [r for r in rectangles if r[1] <= 2 < r[1] + r[3]]
        self.assertEqual(len(bandes_haut), 1, "en haut, seule la pastille est visible")
        self.assertGreaterEqual(bandes_haut[0][0], 61)
        self.assertLess(len(rectangles), 74 * 2, "les lignes identiques sont regroupées")

    def test_ellipse_vide_ignoree(self):
        self.assertEqual(bulle.bandes_ellipses(10, 10, [(5, 5, 5, 5)]), [])


class TestInstanceUnique(unittest.TestCase):
    def tearDown(self):
        if isinstance(bulle._verrou_instance, int):
            os.close(bulle._verrou_instance)
        bulle._verrou_instance = None

    def test_sans_fcntl_le_port_decide(self):
        with sous_linux(), mock.patch.dict(sys.modules, {"fcntl": None}), \
                mock.patch.object(hub, "port_ouvert", return_value=True) as port:
            self.assertTrue(bulle.deja_lancee(), "port déjà pris : une bulle tourne")
            port.return_value = False
            self.assertFalse(bulle.deja_lancee())

    @unittest.skipUnless(sys.platform.startswith("linux"), "verrou fcntl : Linux seulement")
    def test_verrou_fcntl(self):
        dossier = tempfile.mkdtemp()
        try:
            with mock.patch.object(bulle, "chemin_verrou", return_value=os.path.join(dossier, "v.lock")):
                self.assertFalse(bulle.deja_lancee(), "première bulle : le verrou est libre")
                premier = bulle._verrou_instance
                bulle._verrou_instance = None
                self.assertTrue(bulle.deja_lancee(), "seconde bulle : le verrou est tenu")
                bulle._verrou_instance = premier
        finally:
            shutil.rmtree(dossier, ignore_errors=True)

    def test_verrou_par_port(self):
        with mock.patch.dict(os.environ, {"XDG_RUNTIME_DIR": "/run/user/1000"}):
            with mock.patch.object(hub, "PORT", 8760):
                self.assertEqual(os.path.basename(bulle.chemin_verrou()), "mes-outils-bulle.lock")
            with mock.patch.object(hub, "PORT", 8799):
                self.assertEqual(os.path.basename(bulle.chemin_verrou()), "mes-outils-bulle-8799.lock")


class TestOuvrirTableau(unittest.TestCase):
    def test_linux_ouvre_la_fenetre_appli(self):
        with sous_linux(), mock.patch.object(hub, "demander_onglet") as onglet, \
                mock.patch.object(bulle, "ramener_fenetre_linux", return_value=False), \
                mock.patch.object(systeme, "ouvrir_fenetre_appli") as ouvrir:
            bulle.ouvrir_tableau("mails")
        onglet.assert_called_once_with("mails")
        self.assertTrue(ouvrir.call_args.args[0].endswith(f":{hub.PORT}/#mails"))

    def test_linux_fenetre_deja_ouverte(self):
        with sous_linux(), mock.patch.object(bulle, "ramener_fenetre_linux", return_value=True), \
                mock.patch.object(systeme, "ouvrir_fenetre_appli") as ouvrir:
            bulle.ouvrir_tableau()
        ouvrir.assert_not_called()

    def test_sans_wmctrl(self):
        with mock.patch.object(bulle.shutil, "which", return_value=None):
            self.assertFalse(bulle.ramener_fenetre_linux("Mes outils"))


class TestPresence(unittest.TestCase):
    def setUp(self):
        FausseIcone.creees = []
        self.patchs = [sous_linux(), mock.patch.object(icone_linux, "Icone", FausseIcone),
                       mock.patch.dict(hub._cache_etats, {"valeur": None})]
        for p in self.patchs:
            p.start()

    def tearDown(self):
        for p in reversed(self.patchs):
            p.stop()

    def test_valeur_par_defaut(self):
        with ConfigTemporaire({"outils": []}):
            self.assertEqual(bulle.presence_choisie(), "bulle_icone")
        with ConfigTemporaire({"outils": [], "presence": "n_importe_quoi"}):
            self.assertEqual(bulle.presence_choisie(), "bulle_icone")

    def test_bulle_et_icone(self):
        b = fausse_bulle()
        with ConfigTemporaire({"outils": [], "apps_actives": []}):
            b.appliquer_presence()
        self.assertEqual(len(FausseIcone.creees), 1, "l'icône est créée")
        self.assertTrue(b.racine.visible, "la bulle reste affichée")
        libelles = [e.get("libelle") for e in FausseIcone.creees[0].menus[-1]]
        self.assertEqual(libelles[0], "Ouvrir Mes outils")
        self.assertIn("Masquer la bulle", libelles)
        self.assertEqual(libelles[-1], "Quitter")

    def test_icone_seule(self):
        b = fausse_bulle()
        with ConfigTemporaire({"outils": [], "presence": "icone"}):
            b.appliquer_presence()
            self.assertFalse(b.racine.visible, "icône seule : la bulle se cache")
            libelles = [e.get("libelle") for e in FausseIcone.creees[0].menus[-1]]
            b.icone.actualiser(b.entrees_menu(pour_icone=True))
            self.assertIn("Afficher la bulle", [e.get("libelle") for e in b.icone.menus[-1]])
        self.assertIn("Masquer la bulle", libelles)

    def test_icone_impossible_la_bulle_reste(self):
        b = fausse_bulle()
        with ConfigTemporaire({"outils": [], "presence": "icone"}), \
                mock.patch.object(FausseIcone, "demarrer", return_value=False):
            b.appliquer_presence()
        self.assertIs(b.icone, False, "pas de nouvel essai à chaque passage")
        self.assertTrue(b.racine.visible, "sans icône, la bulle ne doit jamais disparaître")

    def test_icone_pas_encore_inscrite(self):
        b = fausse_bulle(visible=False)
        with ConfigTemporaire({"outils": [], "presence": "icone"}), \
                mock.patch.object(FausseIcone, "__init__", lambda s, **k: (setattr(s, "enregistree", False),
                                                                          setattr(s, "menus", []))[0]):
            b.appliquer_presence()
            self.assertFalse(b.racine.visible, "quelques secondes pour s'inscrire avant de montrer la bulle")
            b.icone_depuis -= 10
            b.appliquer_presence()
            self.assertTrue(b.racine.visible, "toujours pas d'icône : la bulle revient")

    def test_bulle_seule(self):
        b = fausse_bulle()
        b.icone = FausseIcone(None, None)
        with ConfigTemporaire({"outils": [], "presence": "bulle"}):
            icone = b.icone
            b.appliquer_presence()
        self.assertTrue(icone.arretee, "bulle seule : l'icône s'en va")
        self.assertIsNone(b.icone)
        self.assertTrue(b.racine.visible)

    def test_basculer_retenu(self):
        b = fausse_bulle()
        with ConfigTemporaire({"outils": []}) as cfg:
            b.appliquer_presence()
            b.basculer_bulle()
            self.assertEqual(cfg.lire()["presence"], "icone")
            self.assertFalse(b.racine.visible)
            b.basculer_bulle()
            self.assertEqual(cfg.lire()["presence"], "bulle_icone")
            self.assertTrue(b.racine.visible)

    def test_masquer_15_minutes(self):
        b = fausse_bulle()
        with ConfigTemporaire({"outils": []}):
            b.masquer()
            b.appliquer_presence()
            self.assertFalse(b.racine.visible, "masquée 15 minutes : pas réaffichée tout de suite")
            b.pause_jusqua = 0
            b.appliquer_presence()
            self.assertTrue(b.racine.visible)


class TestMenu(unittest.TestCase):
    def test_menu_de_la_bulle_inchange(self):
        """Le clic droit de la bulle garde ses entrées (Windows comme avant)."""
        b = fausse_bulle()
        with ConfigTemporaire({"outils": [], "apps_actives": ["mails", "agenda", "notes"]}), \
                mock.patch.dict(hub._cache_etats, {"valeur": None}):
            entrees = b.entrees_menu()
        libelles = [bulle.sobre(e["libelle"]) for e in entrees if not e.get("separateur")]
        self.assertEqual(libelles, ["Ouvrir le tableau de bord", "Note rapide", "Mails (3 non lus)", "Agenda", "Notes",
                                    "Masquer 15 minutes", "Quitter la bulle"])

    def test_menu_de_l_icone_en_dbusmenu(self):
        b = fausse_bulle()
        b.icone = FausseIcone(None, None)
        with ConfigTemporaire({"outils": [{"id": "x", "nom": "Outil X", "emoji": "🧪"}],
                               "apps_actives": ["mails", "agenda", "notes"]}), \
                mock.patch.dict(hub._cache_etats, {"valeur": None}):
            menu = icone_linux.Menu(b.entrees_menu(pour_icone=True))
            ordinaire = [bulle.sobre(e.get("libelle", "")) for e in b.entrees_menu()]
        _, (_, _, enfants) = menu.disposition()
        libelles = [e[1][1].get("label", ("s", "-"))[1] for e in enfants]
        self.assertEqual(libelles[:5], ["Ouvrir Mes outils", "Note rapide", "Mails (3 non lus)", "Agenda", "Notes"])
        self.assertIn("Outil X", libelles, "les outils du tableau de bord sont aussi dans le menu")
        self.assertEqual(libelles[-2:], ["Masquer la bulle", "Quitter"])
        self.assertIn("Masquer la bulle", ordinaire, "icône affichée : la bulle peut se masquer pour de bon")


if __name__ == "__main__":
    unittest.main()
