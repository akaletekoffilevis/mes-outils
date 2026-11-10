# -*- coding: utf-8 -*-
"""Tests de l'historique du presse-papiers.

- Logique de l'historique avec une fausse source (doublons, limite de 50,
  épinglés, pause) ;
- lecture Windows avec de faux user32 / kernel32 (contenus marqués exclus) ;
- deux essais sur le vrai presse-papiers : un texte copié est capté, un mot
  de passe copié par le coffre ne l'est pas. Le contenu d'avant est remis
  ensuite ;
- branches Linux (Wayland, xclip, xsel, Tk, aucune source) avec des
  commandes et une fenêtre Tk simulées : ces tests passent aussi sous Windows.
"""
import ctypes
import subprocess
import threading
import time
import unittest
import uuid
from unittest import mock

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # aide.py, quel que soit le lancement

from aide import ConfigTemporaire, ServeurTest

import config  # noqa: E402
import presse_papiers as pp  # noqa: E402
from presse_papiers import Historique, SourceWindows, Surveillance  # noqa: E402


class FausseSource:
    """Un presse-papiers imaginaire : copier() change le numéro de séquence."""

    def __init__(self):
        self.n = 1
        self.contenu = (None, "pas_de_texte")
        self.occupe = False

    def numero(self):
        return self.n

    def copier(self, texte, raison=None):
        self.n += 1
        self.contenu = (None, raison) if raison else (texte, None)

    def lire(self):
        return (None, "occupe") if self.occupe else self.contenu

    def ecrire(self, texte):
        self.copier(texte)


def surveillance():
    s = Surveillance(Historique(), FausseSource())
    s.oublier_contenu_actuel()
    return s


def textes(s):
    return [e["texte"] for e in s.historique.lister()]


class TestHistorique(unittest.TestCase):
    def test_textes_captes_et_doublons(self):
        s = surveillance()
        self.assertIsNone(s.sonder(), "rien de nouveau")
        for t in ("un", "deux", "deux", "   ", "", "un"):
            s.source.copier(t)
            s.sonder()
        self.assertEqual(textes(s), ["un", "deux"],
                         "vides et doublon du dernier ignorés ; un texte déjà présent remonte en tête")

    def test_limite_et_epingles(self):
        s = surveillance()
        s.source.copier("garde-moi")
        s.sonder()
        s.historique.epingler(s.historique.lister()[0]["id"], True)
        for i in range(70):
            s.source.copier(f"texte {i}")
            s.sonder()
        liste = s.historique.lister()
        self.assertEqual(len(liste), 51, "50 éléments non épinglés + l'épinglé")
        self.assertIn("garde-moi", textes(s), "l'épinglé n'est jamais retiré par la limite")
        self.assertEqual(liste[0]["texte"], "texte 69")
        self.assertNotIn("texte 19", textes(s), "les plus anciens partent")
        self.assertEqual(s.historique.vider(), 50)
        self.assertEqual(textes(s), ["garde-moi"], "« Tout effacer » garde les épinglés")
        self.assertEqual(s.historique.vider(garder_epingles=False), 1)

    def test_pause(self):
        s = surveillance()
        s.actif = False
        s.source.copier("pendant la pause")
        s.sonder()
        s.actif = True
        s.sonder()
        self.assertEqual(textes(s), [], "un texte copié pendant la pause n'est jamais pris")
        s.source.copier("après")
        s.sonder()
        self.assertEqual(textes(s), ["après"])

    def test_exclus_trop_long_et_occupe(self):
        s = surveillance()
        s.source.copier(None, "exclu")
        s.sonder()
        s.historique.ajouter("x" * (pp.TAILLE_MAX + 1))
        self.assertEqual(textes(s), [], "contenu exclu et texte trop long ignorés")
        s.source.occupe = True
        s.source.copier("plus tard")
        s.sonder()
        self.assertEqual(textes(s), [])
        s.source.occupe = False
        s.sonder()
        self.assertEqual(textes(s), ["plus tard"], "presse-papiers occupé : réessayé au coup d'œil suivant")

    def test_fil_demarre_une_seule_fois(self):
        s = Surveillance(Historique(), FausseSource(), intervalle=0.01)
        try:
            self.assertTrue(s.demarrer())
            self.assertFalse(s.demarrer(), "idempotent")
            s.source.copier("par le fil")
            for _ in range(200):
                if len(s.historique):
                    break
                time.sleep(0.01)
            self.assertEqual(textes(s), ["par le fil"])
        finally:
            s.arreter()


# ---------------------------------------------------------------------------
# Lecture Windows simulée : faux user32 et kernel32
# ---------------------------------------------------------------------------
class FauxUser32:
    def __init__(self, formats, ouvrable=True):
        self.formats = formats          # {format: octets}
        self.ouvrable = ouvrable
        self.fermetures = 0

    def OpenClipboard(self, _hwnd):
        return self.ouvrable

    def CloseClipboard(self):
        self.fermetures += 1
        return True

    def IsClipboardFormatAvailable(self, fmt):
        return fmt in self.formats

    def GetClipboardData(self, fmt):
        return fmt if fmt in self.formats else None


class FauxKernel32:
    def __init__(self, user32):
        self.user32 = user32
        self.tampons = {}

    def GlobalSize(self, h):
        return len(self.user32.formats[h])

    def GlobalLock(self, h):
        tampon = ctypes.create_string_buffer(self.user32.formats[h], len(self.user32.formats[h]))
        self.tampons[h] = tampon
        return ctypes.addressof(tampon)

    def GlobalUnlock(self, h):
        return True


EXCLU, HISTORIQUE = 0xC101, 0xC102


def fausse_source(formats, ouvrable=True):
    src = object.__new__(SourceWindows)
    src.u32 = FauxUser32(formats, ouvrable)
    src.k32 = FauxKernel32(src.u32)
    src.fmt_exclu, src.fmt_historique = EXCLU, HISTORIQUE
    return src


def texte_windows(t):
    return (t + "\0").encode("utf-16-le")


@unittest.skipUnless(sys.platform == "win32", "presse-papiers Windows (wchar_t de 2 octets)")
class TestLectureWindows(unittest.TestCase):
    def test_texte_lu(self):
        src = fausse_source({pp.CF_UNICODETEXT: texte_windows("Bonjour é😀")})
        self.assertEqual(src.lire(), ("Bonjour é😀", None))
        self.assertEqual(src.u32.fermetures, 1, "le presse-papiers est toujours refermé")

    def test_contenus_exclus(self):
        texte = {pp.CF_UNICODETEXT: texte_windows("secret")}
        self.assertEqual(fausse_source({**texte, EXCLU: b"\0\0\0\0"}).lire(), (None, "exclu"))
        self.assertEqual(fausse_source({**texte, HISTORIQUE: b"\0\0\0\0"}).lire(), (None, "exclu"))
        self.assertEqual(fausse_source({**texte, HISTORIQUE: b"\1\0\0\0"}).lire(), ("secret", None),
                         "CanIncludeInClipboardHistory = 1 : accepté")

    def test_autres_cas(self):
        self.assertEqual(fausse_source({}).lire(), (None, "pas_de_texte"))
        long = {pp.CF_UNICODETEXT: texte_windows("x" * (pp.TAILLE_MAX + 5))}
        self.assertEqual(fausse_source(long).lire(), (None, "trop_long"))
        with mock.patch.object(pp.time, "sleep"):
            self.assertEqual(fausse_source({}, ouvrable=False).lire(), (None, "occupe"))


# ---------------------------------------------------------------------------
# Le vrai presse-papiers (contenu sauvegardé puis remis)
# ---------------------------------------------------------------------------
FORMATS_NON_COPIABLES = {2, 3, 9, 14, 0x80, 0x82, 0x83, 0x8E}   # bitmaps, métafichiers, palette…


def sauver_presse_papiers(src):
    """Copie de tous les formats « mémoire » du presse-papiers."""
    from ctypes import wintypes
    u32, k32 = src.u32, src.k32
    u32.EnumClipboardFormats.argtypes = [wintypes.UINT]
    u32.EnumClipboardFormats.restype = wintypes.UINT
    if not src._ouvrir(40):
        raise unittest.SkipTest("presse-papiers occupé")
    sauvegarde = []
    try:
        fmt = 0
        while True:
            fmt = u32.EnumClipboardFormats(fmt)
            if not fmt:
                break
            if fmt in FORMATS_NON_COPIABLES or 0x200 <= fmt <= 0x3FF:
                continue
            h = u32.GetClipboardData(fmt)
            if not h:
                continue
            taille = k32.GlobalSize(h)
            p = k32.GlobalLock(h)
            if not p:
                continue
            try:
                sauvegarde.append((fmt, ctypes.string_at(p, taille)))
            finally:
                k32.GlobalUnlock(h)
    finally:
        u32.CloseClipboard()
    return sauvegarde


def remettre_presse_papiers(src, sauvegarde):
    u32, k32 = src.u32, src.k32
    if not src._ouvrir(40):
        return
    try:
        u32.EmptyClipboard()
        for fmt, octets in sauvegarde:
            h = k32.GlobalAlloc(pp.GMEM_MOVEABLE, max(1, len(octets)))
            p = k32.GlobalLock(h)
            ctypes.memmove(p, octets, len(octets))
            k32.GlobalUnlock(h)
            if not u32.SetClipboardData(fmt, h):
                k32.GlobalFree(h)
    finally:
        u32.CloseClipboard()


@unittest.skipUnless(sys.platform == "win32", "vrai presse-papiers Windows")
class TestVraiPressePapiers(unittest.TestCase):
    def setUp(self):
        self.src = SourceWindows()
        self.sauvegarde = sauver_presse_papiers(self.src)
        self.surv = Surveillance(Historique(), self.src)
        self.surv.oublier_contenu_actuel()

    def tearDown(self):
        remettre_presse_papiers(self.src, self.sauvegarde)

    def sonder_jusqu_a_changement(self, numero_avant):
        for _ in range(40):
            if self.src.numero() != numero_avant and self.surv._dernier == self.src.numero():
                return
            self.surv.sonder()
            time.sleep(0.05)

    def test_texte_copie_capte(self):
        texte = "Mes outils : essai " + uuid.uuid4().hex
        avant = self.src.numero()
        self.src.ecrire(texte)
        self.sonder_jusqu_a_changement(avant)
        self.assertEqual([e["texte"] for e in self.surv.historique.lister()], [texte])

    def test_copie_du_coffre_ignoree(self):
        import coffre
        texte = "Mes outils : faux secret " + uuid.uuid4().hex
        avant = self.src.numero()
        coffre.copier_presse_papiers(texte)
        self.sonder_jusqu_a_changement(avant)
        self.assertNotEqual(self.src.numero(), avant, "le presse-papiers a bien changé")
        self.assertEqual(self.src.lire(), (None, "exclu"))
        self.assertEqual(self.surv.historique.lister(), [], "un mot de passe du coffre n'entre pas dans l'historique")


# ---------------------------------------------------------------------------
# Linux simulé : commandes wl-paste / wl-copy / xclip / xsel et fenêtre Tk
# ---------------------------------------------------------------------------
class FauxCommandes:
    """Remplace subprocess.run : un presse-papiers en mémoire, piloté par
    wl-paste, wl-copy, xclip et xsel."""

    def __init__(self, texte=None, types=("text/plain;charset=utf-8",)):
        self.texte = texte
        self.types = list(types)
        self.appels = []
        self.refuser_ecriture = False

    def run(self, args, **kw):
        self.appels.append((list(args), kw))
        nom = args[0]

        def ok(sortie=b""):
            return subprocess.CompletedProcess(args, 0, sortie, b"")

        def echec():
            return subprocess.CompletedProcess(args, 1, b"", b"Nothing is copied")

        lecture = (nom == "wl-paste") or (nom == "xclip" and "-o" in args) or (nom == "xsel" and "--output" in args)
        if lecture:
            if "--list-types" in args or "TARGETS" in args:
                return ok("\n".join(self.types).encode())
            if self.texte is None:
                return ok() if nom == "xsel" else echec()
            return ok(self.texte.encode("utf-8"))
        if self.refuser_ecriture:
            return echec()
        if "--clear" in args:
            self.texte = None
        else:
            self.texte = kw["input"].decode("utf-8")
        return ok()


class BaseLinux(unittest.TestCase):
    """systeme.WINDOWS faux, commandes simulées, secrets du coffre remis à zéro."""

    def setUp(self):
        self.faux = FauxCommandes()
        self.patchs = [mock.patch.object(pp.systeme, "WINDOWS", False),
                       mock.patch.object(pp.subprocess, "run", side_effect=self.faux.run),
                       mock.patch.object(pp, "_secrets", [])]
        for p in self.patchs:
            p.start()

    def tearDown(self):
        for p in self.patchs:
            p.stop()


def environnement(variables, outils, racine=None):
    """Patchs pour un bureau Linux imaginaire : variables d'environnement
    (les autres sont retirées), commandes installées, racine Tk éventuelle."""
    env = {k: v for k, v in os.environ.items()
           if k not in ("WAYLAND_DISPLAY", "DISPLAY", "MES_OUTILS_PRESSE_PAPIERS")}
    env.update(variables)
    return [mock.patch.dict(os.environ, env, clear=True),
            mock.patch.object(pp.shutil, "which", side_effect=lambda n: f"/usr/bin/{n}" if n in outils else None),
            mock.patch.object(pp, "_racine_tk", racine)]


class TestChoixSourceLinux(unittest.TestCase):
    def choisir(self, variables, outils, racine=None):
        patchs = environnement(variables, outils, racine)
        for p in patchs:
            p.start()
        try:
            return type(pp.choisir_source_linux())
        finally:
            for p in patchs:
                p.stop()

    def test_ordre(self):
        tous = {"wl-paste", "wl-copy", "xclip", "xsel"}
        bureau = {"WAYLAND_DISPLAY": "wayland-0", "DISPLAY": ":0"}
        racine = (object(), 1)
        self.assertIs(self.choisir(bureau, tous), pp.SourceWayland, "Wayland d'abord")
        self.assertIs(self.choisir(bureau, tous - {"wl-copy"}), pp.SourceXclip, "wl-copy manquant : xclip")
        self.assertIs(self.choisir({"DISPLAY": ":0"}, tous), pp.SourceXclip, "X11 sans Wayland : xclip")
        self.assertIs(self.choisir(bureau, {"xsel"}), pp.SourceXsel)
        self.assertIs(self.choisir({"WAYLAND_DISPLAY": "w"}, {"xclip", "xsel"}, racine), pp.SourceTk,
                      "xclip sans DISPLAY ne sert à rien : Tk")
        self.assertIs(self.choisir(bureau, set(), racine), pp.SourceTk)
        self.assertIs(self.choisir(bureau, set()), pp.SourceAbsente, "rien du tout : source absente")
        self.assertIs(self.choisir(dict(bureau, MES_OUTILS_PRESSE_PAPIERS="xsel"), tous), pp.SourceXsel,
                      "source imposée pour les essais")
        self.assertIs(self.choisir(dict(bureau, MES_OUTILS_PRESSE_PAPIERS="tk"), tous, racine), pp.SourceTk)

    def test_gnome_wayland_en_dernier(self):
        tous = {"wl-paste", "wl-copy", "xclip", "xsel"}
        gnome = {"WAYLAND_DISPLAY": "wayland-0", "DISPLAY": ":0", "XDG_CURRENT_DESKTOP": "ubuntu:GNOME"}
        racine = (object(), 1)
        self.assertIs(self.choisir(gnome, tous), pp.SourceXclip, "GNOME : xclip avant wl-paste")
        self.assertIs(self.choisir(gnome, {"wl-paste", "wl-copy"}, racine), pp.SourceTk, "GNOME : Tk avant wl-paste")
        self.assertIs(self.choisir(gnome, {"wl-paste", "wl-copy"}), pp.SourceWayland, "GNOME : wl-paste en dernier recours")


class TestSourcesCommandes(BaseLinux):
    def test_lecture_wayland_et_exclusions(self):
        s = Surveillance(Historique(), pp.SourceWayland())
        self.faux.texte = "déjà là"
        s.oublier_contenu_actuel()
        self.assertIsNone(s.sonder(), "le contenu présent au départ n'est pas pris")
        self.faux.texte = "Bonjour é😀\n"
        s.sonder()
        self.faux.texte = "mot de passe de KeePassXC"
        self.faux.types.append("x-kde-passwordManagerHint")
        s.sonder()
        self.assertEqual(textes(s), ["Bonjour é😀\n"], "texte exact ; gestionnaire de mots de passe ignoré")
        self.faux.types.pop()
        self.faux.texte = "x" * (pp.TAILLE_MAX + 1)
        s.sonder()
        self.faux.texte = None
        s.sonder()
        self.assertEqual(len(s.historique), 1, "trop long et presse-papiers vide ignorés")
        lectures = [a for a, _ in self.faux.appels if a[0] == "wl-paste" and "--list-types" not in a]
        self.assertIn("--no-newline", lectures[0], "wl-paste ne doit pas ajouter de saut de ligne")
        for args, kw in self.faux.appels:
            self.assertNotIn("creationflags", kw, f"pas de creationflags hors Windows : {args}")

    def test_ecriture_et_effacement(self):
        for classe in (pp.SourceWayland, pp.SourceXclip, pp.SourceXsel):
            with self.subTest(source=classe.__name__):
                self.faux.appels.clear()
                src = classe()
                src.ecrire("Texte é😀")
                self.assertEqual(self.faux.texte, "Texte é😀")
                args, kw = self.faux.appels[-1]
                self.assertEqual((kw["stdout"], kw["stderr"]), (subprocess.DEVNULL, subprocess.DEVNULL),
                                 "la commande reste en arrière-plan : ses sorties ne sont pas attendues")
                self.assertNotIn("creationflags", kw)
                self.assertEqual(src.texte_actuel(), "Texte é😀")
                src.effacer()
                src.numero()
                self.assertEqual(src.lire(), (None, "pas_de_texte"))

    def test_ecriture_refusee(self):
        self.faux.refuser_ecriture = True
        with self.assertRaisesRegex(RuntimeError, "Copie dans le presse-papiers impossible"):
            pp.SourceXclip().ecrire("x")
        with mock.patch.object(pp.subprocess, "run", side_effect=FileNotFoundError("xclip")):
            with self.assertRaisesRegex(RuntimeError, "Copie dans le presse-papiers impossible"):
                pp.SourceXclip().ecrire("x")

    def test_numero_est_une_empreinte(self):
        src = pp.SourceXsel()
        self.faux.texte = "un"
        n1 = src.numero()
        self.assertEqual(src.numero(), n1, "même texte, même numéro")
        self.faux.texte = "deux"
        self.assertNotEqual(src.numero(), n1)
        self.assertNotIn("deux", str(src.numero()), "l'empreinte ne contient pas le texte")
        self.faux.texte = None
        self.assertIsNone(src.numero(), "xsel vide : pas de texte")


class FausseRacine:
    """Une fenêtre Tk imaginaire : un fil à elle exécute les after(), comme la
    boucle de Tk. Chaque accès au presse-papiers note le fil qui l'a fait."""

    def __init__(self, contenu=None, bloquee=False):
        self.contenu = contenu
        self.bloquee = bloquee
        self.fils_utilises = set()
        self._taches = []
        self._reveil = threading.Condition()
        self._arret = False
        self.fil = threading.Thread(target=self._boucle, daemon=True)
        self.fil.start()

    def _boucle(self):
        while True:
            with self._reveil:
                while not self._taches and not self._arret:
                    self._reveil.wait()
                if self._arret:
                    return
                tache = self._taches.pop(0)
            tache()

    def after(self, _delai, fonction):
        if self.bloquee:
            return "après#0"       # la boucle de Tk ne tourne pas : rien ne se passe
        with self._reveil:
            self._taches.append(fonction)
            self._reveil.notify()
        return "après#1"

    def dans_le_fil(self, fonction):
        """Exécute fonction dans le fil de la fenêtre et renvoie son résultat."""
        fini, resultat = threading.Event(), {}

        def tache():
            try:
                resultat["v"] = fonction()
            except BaseException as e:  # noqa: BLE001
                resultat["e"] = e
            fini.set()
        self.after(0, tache)
        fini.wait(5)
        if "e" in resultat:
            raise resultat["e"]
        return resultat.get("v")

    def arreter(self):
        with self._reveil:
            self._arret = True
            self._reveil.notify()

    def _note(self):
        self.fils_utilises.add(threading.get_ident())

    def clipboard_get(self, type=None):  # noqa: A002 — même nom que Tk
        self._note()
        if type == "TARGETS":
            return "TARGETS UTF8_STRING STRING"
        if self.contenu is None:
            raise RuntimeError("CLIPBOARD selection doesn't exist")
        return self.contenu

    def clipboard_clear(self):
        self._note()
        self.contenu = None

    def clipboard_append(self, texte):
        self._note()
        self.contenu = (self.contenu or "") + texte

    def update_idletasks(self):
        self._note()


class TestSourceTk(BaseLinux):
    def setUp(self):
        super().setUp()
        self.racine = FausseRacine("début")
        self.addCleanup(self.racine.arreter)
        self.src = pp.SourceTk(self.racine, fil=self.racine.fil.ident)

    def test_appels_dans_le_fil_de_tk(self):
        s = Surveillance(Historique(), self.src)
        s.oublier_contenu_actuel()
        self.racine.contenu = "copié ailleurs"
        s.sonder()
        self.src.ecrire("par Mes outils")
        self.assertEqual(self.racine.contenu, "par Mes outils")
        s.sonder()
        self.assertEqual(textes(s), ["par Mes outils", "copié ailleurs"])
        self.assertEqual(self.racine.fils_utilises, {self.racine.fil.ident},
                         "Tk n'est touché que depuis son propre fil")
        self.src.effacer()
        self.assertIsNone(self.racine.contenu)
        self.assertIsNone(self.src.numero(), "presse-papiers vide (TclError) : pas de texte")

    def test_appel_depuis_le_fil_de_tk_sans_blocage(self):
        n = self.racine.dans_le_fil(self.src.numero)
        self.assertEqual(n, pp.empreinte("début"), "appel direct, sans attendre son propre fil")

    def test_tk_qui_ne_repond_pas(self):
        self.racine.bloquee = True
        with mock.patch.object(pp, "DELAI_TK", 0.05):
            debut = time.time()
            with self.assertRaisesRegex(RuntimeError, "ne répond pas"):
                self.src.numero()
            self.assertLess(time.time() - debut, 1, "délai court, pas de blocage")
        with mock.patch.object(self.racine, "after", side_effect=RuntimeError("main thread is not in main loop")):
            with self.assertRaisesRegex(RuntimeError, "ne répond pas"):
                self.src.ecrire("x")


class TestModuleLinux(BaseLinux):
    """Le module entier sous un Linux imaginaire (aucune vraie commande)."""

    def setUp(self):
        super().setUp()
        self.cfg = ConfigTemporaire()
        self.cfg.__enter__()
        self.addCleanup(self.cfg.__exit__, None, None, None)
        for p in [mock.patch.object(pp, "_surveillance", None), mock.patch.object(pp, "_historique", Historique())]:
            p.start()
            self.addCleanup(p.stop)

    def arreter_surveillance(self):
        if pp._surveillance is not None:
            pp._surveillance.arreter()

    def test_sans_aucune_source_puis_tk(self):
        patchs = environnement({}, set())
        for p in patchs:
            p.start()
            self.addCleanup(p.stop)
        self.addCleanup(self.arreter_surveillance)
        e = pp.demarrer_surveillance()
        self.assertEqual((e["disponible"], e["surveille"], e["message"]),
                         (False, False, pp.MESSAGE_INDISPONIBLE), "message clair, sans planter")
        self.assertEqual(pp.lister(), [])
        with self.assertRaisesRegex(RuntimeError, "wl-clipboard"):
            pp.ecrire_texte("x")
        racine = FausseRacine("avant Tk")
        self.addCleanup(racine.arreter)
        racine.dans_le_fil(lambda: pp.utiliser_tk(racine))      # la bulle l'appelle dans le fil de Tk
        self.assertIsInstance(pp._surveillance.source, pp.SourceTk)
        self.assertEqual(pp._surveillance.source.fil, racine.fil.ident, "le fil de Tk est celui de l'appel")
        e = pp.etat()
        self.assertTrue(e["disponible"])
        self.assertNotIn("message", e)
        pp.ecrire_texte("bonjour")
        self.assertEqual(racine.contenu, "bonjour")
        self.assertEqual(racine.fils_utilises, {racine.fil.ident})

    def test_utiliser_tk_sans_effet_sous_windows(self):
        with mock.patch.object(pp.systeme, "WINDOWS", True), mock.patch.object(pp, "_racine_tk", None):
            pp.utiliser_tk(object())
            self.assertIsNone(pp._racine_tk)

    def test_secret_du_coffre(self):
        import coffre
        s = Surveillance(pp._historique, pp.SourceWayland())
        pp._surveillance = s            # remis à None par le patch de setUp
        self.faux.texte = "avant"
        s.oublier_contenu_actuel()
        with mock.patch.object(coffre.systeme, "WINDOWS", False):
            coffre.copier_presse_papiers("Mot-de-passe-123", effacer_apres=0.05)
            self.assertEqual(self.faux.texte, "Mot-de-passe-123")
            s.sonder()
            self.assertEqual(textes(s), [], "un secret du coffre n'entre pas dans l'historique")
            for _ in range(100):
                if self.faux.texte is None:
                    break
                time.sleep(0.02)
            self.assertIsNone(self.faux.texte, "effacé après le délai")
            coffre.copier_presse_papiers("Autre-secret-456", effacer_apres=0.05)
            self.faux.texte = "copié ensuite par l'utilisateur"
            time.sleep(0.3)
            self.assertEqual(self.faux.texte, "copié ensuite par l'utilisateur",
                             "rien n'est effacé si autre chose a été copié entre-temps")
            s.sonder()
            self.assertEqual(textes(s), ["copié ensuite par l'utilisateur"])

    def test_secret_sans_presse_papiers(self):
        import coffre
        patchs = environnement({}, set())
        for p in patchs:
            p.start()
            self.addCleanup(p.stop)
        with mock.patch.object(coffre.systeme, "WINDOWS", False):
            with self.assertRaisesRegex(coffre.ErreurCoffre, "wl-clipboard"):
                coffre.copier_presse_papiers("secret")


@unittest.skipUnless(sys.platform.startswith("linux"), "vrai bureau Linux")
class TestVraiLinux(unittest.TestCase):
    def test_source_reelle(self):
        src = pp.nouvelle_source()
        if isinstance(src, pp.SourceAbsente):
            self.skipTest("aucun presse-papiers (ni wl-clipboard, ni xclip, ni xsel)")
        avant = src.texte_actuel()
        texte = "Mes outils : essai " + uuid.uuid4().hex
        try:
            src.ecrire(texte)
            for _ in range(20):
                if src.texte_actuel() == texte:
                    break
                time.sleep(0.05)
            src.numero()
            self.assertEqual(src.lire(), (texte, None))
        finally:
            if avant:
                src.ecrire(avant)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
class TestRoutes(ServeurTest):
    def test_routes(self):
        hist = Historique()
        surv = Surveillance(hist, FausseSource(), intervalle=0.01)
        with ConfigTemporaire() as cfg, mock.patch.object(pp, "_historique", hist), \
                mock.patch.object(pp, "_surveillance", surv):
            try:
                statut, r = self.post("/api/presse_papiers/liste", {})
                self.assertEqual((statut, r["surveille"], r["actif"], r["elements"]), (200, True, True, []))
                hist.ajouter("premier\nligne 2")
                hist.ajouter("second")
                statut, r = self.post("/api/presse_papiers/liste", {"recherche": "PREM"})
                self.assertEqual([e["apercu"] for e in r["elements"]], ["premier\nligne 2"])
                self.assertEqual(r["elements"][0]["lignes"], 2)
                premier = r["elements"][0]["id"]
                statut, r = self.post("/api/presse_papiers/recopier", {"id": premier})
                self.assertEqual(statut, 200)
                self.assertEqual(surv.source.contenu, ("premier\nligne 2", None), "remis dans le presse-papiers")
                time.sleep(0.05)
                self.assertEqual([e["texte"] for e in hist.lister()], ["premier\nligne 2", "second"],
                                 "recopié : en tête, sans doublon")
                statut, r = self.post("/api/presse_papiers/epingler", {"id": premier, "epingle": True})
                self.assertEqual((statut, r["epingle"]), (200, True))
                statut, r = self.post("/api/presse_papiers/pause", {"pause": True})
                self.assertEqual((statut, r["actif"]), (200, False))
                self.assertEqual(cfg.lire()["presse_papiers"], {"actif": False}, "réglage gardé")
                statut, r = self.post("/api/presse_papiers/vider", {})
                self.assertEqual((statut, r["supprimes"]), (200, 1))
                statut, r = self.post("/api/presse_papiers/supprimer", {"id": premier})
                self.assertEqual((statut, r["supprimes"]), (200, 1))
                statut, r = self.post("/api/presse_papiers/supprimer", {"id": "x"})
                self.assertEqual(statut, 400)
                self.post("/api/presse_papiers/pause", {"pause": False})
                self.assertTrue(config.section("presse_papiers")["actif"])
            finally:
                surv.arreter()


if __name__ == "__main__":
    unittest.main()
