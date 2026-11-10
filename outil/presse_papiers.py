# -*- coding: utf-8 -*-
"""Onglet Presse-papiers : historique des textes copiés, sans dépendance.

- Surveillance : un fil d'arrière-plan regarde toutes les 0,7 s le numéro de
  séquence du presse-papiers Windows (GetClipboardSequenceNumber) ; quand il
  change, le texte (CF_UNICODETEXT) est lu, avec quelques réessais si un
  autre programme tient le presse-papiers.
- Ignorés : les contenus marqués « ExcludeClipboardContentFromMonitorProcessing »
  ou « CanIncludeInClipboardHistory » = 0 (gestionnaires de mots de passe, le
  coffre de Mes outils), les textes vides, le doublon du dernier élément, et
  les textes de plus de 100 000 caractères (ignorés en entier : souvent un
  fichier entier, qui encombrerait la mémoire pour rien).
- Un texte déjà présent plus bas dans l'historique remonte en tête (pas de
  doublon dans la liste).
- Uniquement en mémoire, jamais sur disque (il peut contenir des secrets
  copiés ailleurs) : tout est effacé à la fermeture de Mes outils.
- 50 éléments non épinglés au plus ; les épinglés restent (dans la limite de
  50 épinglés).
- Pause / Reprendre : en mémoire, et réglage persistant
  config.section("presse_papiers")["actif"] (vrai par défaut).

Sous Linux, il n'y a pas de numéro de séquence : le « numéro » est une
empreinte du texte (calculée avec une clé tirée au hasard au démarrage, et
jamais écrite). Source choisie dans cet ordre :
1. Wayland (WAYLAND_DISPLAY) avec wl-paste et wl-copy (paquet wl-clipboard) ;
2. X11 ou XWayland (DISPLAY) avec xclip, sinon xsel ;
3. Tk, par la fenêtre de la bulle (utiliser_tk(racine), appelé par bulle.py).
Sous GNOME, Wayland passe en dernier (voir choisir_source_linux).
La variable d'environnement MES_OUTILS_PRESSE_PAPIERS (wayland, xclip, xsel,
tk) impose une source, pour les essais. Sans aucune source, l'onglet reste
utilisable : historique vide et message clair (etat()["message"]).
Ignorés aussi sous Linux : les secrets copiés par le coffre de Mes outils
(ecrire_secret) et les contenus marqués « x-kde-passwordManagerHint »
(KeePassXC et autres gestionnaires de mots de passe).

Pour la bulle : demarrer_surveillance(), lister(), recopier(id), supprimer(id),
vider(), pause(bool), epingler(id, bool), etat(), utiliser_tk(racine). Pour
les autres modules : ecrire_texte(texte), ecrire_secret(texte), effacer_si(empreinte).
"""
import ctypes
import datetime
import hashlib
import itertools
import os
import secrets
import shutil
import subprocess
import threading
import time

import config
import systeme

LIMITE = 50
MAX_EPINGLES = 50
TAILLE_MAX = 100_000
INTERVALLE = 0.7          # secondes entre deux coups d'œil
APERCU = 600              # caractères envoyés à la page pour l'aperçu
CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002


# ---------------------------------------------------------------------------
# Le vrai presse-papiers Windows (user32 / kernel32)
# ---------------------------------------------------------------------------
class SourceWindows:
    """Lecture et écriture du presse-papiers Windows par ctypes."""

    def __init__(self):
        from ctypes import wintypes  # noqa: PLC0415 — Windows seulement
        u32 = ctypes.WinDLL("user32", use_last_error=True)
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        u32.OpenClipboard.argtypes = [wintypes.HWND]
        u32.OpenClipboard.restype = wintypes.BOOL
        u32.CloseClipboard.restype = wintypes.BOOL
        u32.EmptyClipboard.restype = wintypes.BOOL
        u32.GetClipboardSequenceNumber.restype = wintypes.DWORD
        u32.IsClipboardFormatAvailable.argtypes = [wintypes.UINT]
        u32.IsClipboardFormatAvailable.restype = wintypes.BOOL
        u32.GetClipboardData.argtypes = [wintypes.UINT]
        u32.GetClipboardData.restype = wintypes.HANDLE
        u32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
        u32.SetClipboardData.restype = wintypes.HANDLE
        u32.RegisterClipboardFormatW.argtypes = [wintypes.LPCWSTR]
        u32.RegisterClipboardFormatW.restype = wintypes.UINT
        k32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
        k32.GlobalAlloc.restype = wintypes.HGLOBAL
        k32.GlobalFree.argtypes = [wintypes.HGLOBAL]
        k32.GlobalFree.restype = wintypes.HGLOBAL
        k32.GlobalLock.argtypes = [wintypes.HGLOBAL]
        k32.GlobalLock.restype = wintypes.LPVOID
        k32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
        k32.GlobalUnlock.restype = wintypes.BOOL
        k32.GlobalSize.argtypes = [wintypes.HGLOBAL]
        k32.GlobalSize.restype = ctypes.c_size_t
        self.u32, self.k32 = u32, k32
        self.fmt_exclu = u32.RegisterClipboardFormatW("ExcludeClipboardContentFromMonitorProcessing")
        self.fmt_historique = u32.RegisterClipboardFormatW("CanIncludeInClipboardHistory")

    def numero(self):
        return self.u32.GetClipboardSequenceNumber()

    def _ouvrir(self, essais=10):
        for _ in range(essais):
            if self.u32.OpenClipboard(None):
                return True
            time.sleep(0.05)
        return False

    def _dword(self, handle):
        if not handle or self.k32.GlobalSize(handle) < 4:
            return None
        p = self.k32.GlobalLock(handle)
        if not p:
            return None
        try:
            return ctypes.c_uint32.from_address(p).value
        finally:
            self.k32.GlobalUnlock(handle)

    def lire(self):
        """(texte, raison) : texte None si rien à prendre, raison parmi
        « occupe », « exclu », « pas_de_texte », « trop_long »."""
        if not self._ouvrir():
            return None, "occupe"
        try:
            u32 = self.u32
            if self.fmt_exclu and u32.IsClipboardFormatAvailable(self.fmt_exclu):
                return None, "exclu"
            if self.fmt_historique and u32.IsClipboardFormatAvailable(self.fmt_historique):
                if self._dword(u32.GetClipboardData(self.fmt_historique)) == 0:
                    return None, "exclu"
            if not u32.IsClipboardFormatAvailable(CF_UNICODETEXT):
                return None, "pas_de_texte"
            h = u32.GetClipboardData(CF_UNICODETEXT)
            if not h:
                return None, "pas_de_texte"
            nb = self.k32.GlobalSize(h) // 2
            if nb > TAILLE_MAX + 1:
                return None, "trop_long"
            p = self.k32.GlobalLock(h)
            if not p:
                return None, "pas_de_texte"
            try:
                texte = ctypes.wstring_at(p, nb)
            finally:
                self.k32.GlobalUnlock(h)
            return texte.split("\0", 1)[0], None
        finally:
            u32.CloseClipboard()

    def ecrire(self, texte):
        """Mettre un texte dans le presse-papiers (copie ordinaire)."""
        if not self._ouvrir(20):
            raise RuntimeError("Le presse-papiers est occupé par un autre programme.")
        try:
            self.u32.EmptyClipboard()
            octets = (str(texte) + "\0").encode("utf-16-le")
            h = self.k32.GlobalAlloc(GMEM_MOVEABLE, len(octets))
            if not h:
                raise RuntimeError("Mémoire insuffisante pour copier ce texte.")
            p = self.k32.GlobalLock(h)
            ctypes.memmove(p, octets, len(octets))
            self.k32.GlobalUnlock(h)
            if not self.u32.SetClipboardData(CF_UNICODETEXT, h):
                self.k32.GlobalFree(h)
                raise RuntimeError("Copie dans le presse-papiers impossible.")
        finally:
            self.u32.CloseClipboard()


# ---------------------------------------------------------------------------
# Linux : empreintes, secrets du coffre, sources Wayland / X11 / Tk
# ---------------------------------------------------------------------------
_CLE_EMPREINTE = secrets.token_bytes(32)   # tirée au démarrage, jamais écrite
_secrets = []                              # empreintes des secrets copiés par le coffre
_verrou_secrets = threading.Lock()
MAX_SECRETS = 20
INDICES_MOT_DE_PASSE = ("x-kde-passwordManagerHint",)
DELAI_COMMANDE = 2        # secondes pour lire avec wl-paste, xclip, xsel
DELAI_TK = 1.0            # secondes d'attente d'une réponse du fil de Tk
MESSAGE_INDISPONIBLE = ("Presse-papiers indisponible : installez wl-clipboard (Wayland) ou xclip "
                        "(sudo apt install wl-clipboard xclip).")


def empreinte(texte):
    """Empreinte d'un texte (sert de numéro de séquence sous Linux) ; None
    pour « pas de texte »."""
    if texte is None:
        return None
    return hashlib.blake2b(str(texte).encode("utf-8", "surrogatepass"), key=_CLE_EMPREINTE,
                           digest_size=16).hexdigest()


def _noter_secret(e):
    with _verrou_secrets:
        if e in _secrets:
            _secrets.remove(e)
        _secrets.append(e)
        del _secrets[:-MAX_SECRETS]


def est_secret(e):
    with _verrou_secrets:
        return e is not None and e in _secrets


class SourceLinux:
    """Base des sources Linux. Les sous-classes donnent _lire_texte() → texte
    ou None, _types() → types annoncés, ecrire(texte) et effacer()."""

    nom = "linux"

    def __init__(self):
        self._dernier_lu = (None, None)    # (empreinte, texte) du dernier coup d'œil

    def _lire_texte(self):
        raise NotImplementedError

    def _types(self):
        return ()

    def texte_actuel(self):
        return self._lire_texte()

    def numero(self):
        texte = self._lire_texte()
        e = empreinte(texte)
        self._dernier_lu = (e, texte)
        return e

    def lire(self):
        """(texte, raison), comme SourceWindows.lire()."""
        e, texte = self._dernier_lu
        if e is None:
            texte = self._lire_texte()
            e = empreinte(texte)
        self._dernier_lu = (None, None)    # le texte ne reste pas en mémoire ici
        if texte is None or texte == "":
            return None, "pas_de_texte"
        if est_secret(e):
            return None, "exclu"
        try:
            if any(t in INDICES_MOT_DE_PASSE for t in self._types()):
                return None, "exclu"
        except Exception:  # noqa: BLE001 — types illisibles : le texte reste pris
            pass
        if len(texte) > TAILLE_MAX:
            return None, "trop_long"
        return texte, None

    def ecrire(self, texte):
        raise NotImplementedError

    def effacer(self):
        raise NotImplementedError


def _lancer(args, delai=DELAI_COMMANDE):
    """Lance une commande de lecture ; renvoie (code, sortie en octets)."""
    r = subprocess.run(args, capture_output=True, timeout=delai, stdin=subprocess.DEVNULL,
                       **systeme.options_sans_fenetre())
    return r.returncode, r.stdout or b""


def _donner(args, texte):
    """Lance une commande d'écriture (wl-copy, xclip, xsel). Ces commandes
    restent en arrière-plan pour servir le presse-papiers : leurs sorties ne
    sont pas lues (sinon on attendrait leur fin)."""
    try:
        r = subprocess.run(args, input=str(texte).encode("utf-8"), stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=10, **systeme.options_sans_fenetre())
    except (OSError, subprocess.SubprocessError):
        raise RuntimeError("Copie dans le presse-papiers impossible.") from None
    if r.returncode != 0:
        raise RuntimeError("Copie dans le presse-papiers impossible.")


def _texte(code, sortie):
    return sortie.decode("utf-8", "replace") if code == 0 else None


class SourceWayland(SourceLinux):
    """wl-paste / wl-copy (paquet wl-clipboard)."""

    nom = "wayland"

    def _lire_texte(self):
        return _texte(*_lancer(["wl-paste", "--no-newline", "--type", "text"]))

    def _types(self):
        code, sortie = _lancer(["wl-paste", "--list-types"])
        return sortie.decode("utf-8", "replace").split() if code == 0 else ()

    def ecrire(self, texte):
        _donner(["wl-copy", "--type", "text/plain;charset=utf-8"], texte)

    def effacer(self):
        _donner(["wl-copy", "--clear"], "")


class SourceXclip(SourceLinux):
    """xclip (X11, ou XWayland sous GNOME)."""

    nom = "xclip"

    def _lire_texte(self):
        return _texte(*_lancer(["xclip", "-selection", "clipboard", "-o"]))

    def _types(self):
        code, sortie = _lancer(["xclip", "-selection", "clipboard", "-o", "-t", "TARGETS"])
        return sortie.decode("utf-8", "replace").split() if code == 0 else ()

    def ecrire(self, texte):
        _donner(["xclip", "-selection", "clipboard", "-i"], texte)

    def effacer(self):
        _donner(["xclip", "-selection", "clipboard", "-i"], "")


class SourceXsel(SourceLinux):
    """xsel (X11) ; il ne donne pas les types : pas de détection des
    gestionnaires de mots de passe."""

    nom = "xsel"

    def _lire_texte(self):
        texte = _texte(*_lancer(["xsel", "--clipboard", "--output"]))
        return texte or None

    def ecrire(self, texte):
        _donner(["xsel", "--clipboard", "--input"], texte)

    def effacer(self):
        _donner(["xsel", "--clipboard", "--clear"], "")


class SourceTk(SourceLinux):
    """Le presse-papiers de Tk, par la fenêtre de la bulle. Tk n'est pas sûr
    entre fils : chaque appel est fait dans le fil de Tk (racine.after), et
    on attend sa réponse au plus DELAI_TK secondes."""

    nom = "tk"

    def __init__(self, racine, fil=None):
        super().__init__()
        self.racine = racine
        self.fil = fil if fil is not None else threading.get_ident()

    def _dans_tk(self, fonction):
        if threading.get_ident() == self.fil:
            return fonction()
        fini = threading.Event()
        resultat = {}

        def tache():
            try:
                resultat["valeur"] = fonction()
            except BaseException as erreur:  # noqa: BLE001 — renvoyée au fil appelant
                resultat["erreur"] = erreur
            finally:
                fini.set()

        try:
            self.racine.after(0, tache)
        except Exception:  # noqa: BLE001 — fenêtre fermée, boucle de Tk arrêtée
            raise RuntimeError("Le presse-papiers ne répond pas.") from None
        if not fini.wait(DELAI_TK):
            raise RuntimeError("Le presse-papiers ne répond pas.")
        if "erreur" in resultat:
            raise resultat["erreur"]
        return resultat.get("valeur")

    def _lire_texte(self):
        def lire():
            for options in ({"type": "UTF8_STRING"}, {}):
                try:
                    return self.racine.clipboard_get(**options)
                except Exception:  # noqa: BLE001 — TclError : vide, ou pas du texte
                    continue
            return None
        return self._dans_tk(lire)

    def _types(self):
        def types():
            try:
                return str(self.racine.clipboard_get(type="TARGETS")).split()
            except Exception:  # noqa: BLE001
                return []
        return self._dans_tk(types)

    def ecrire(self, texte):
        def ecrire():
            self.racine.clipboard_clear()
            self.racine.clipboard_append(str(texte))
            self.racine.update_idletasks()
        try:
            self._dans_tk(ecrire)
        except RuntimeError:
            raise
        except Exception:  # noqa: BLE001
            raise RuntimeError("Copie dans le presse-papiers impossible.") from None

    def effacer(self):
        self._dans_tk(self.racine.clipboard_clear)


class SourceAbsente:
    """Aucun presse-papiers utilisable : rien n'est lu, la copie explique
    quoi installer. L'onglet reste utilisable (historique vide)."""

    nom = "aucune"

    def numero(self):
        return None

    def lire(self):
        return None, "pas_de_texte"

    def texte_actuel(self):
        return None

    def ecrire(self, texte):
        raise RuntimeError(MESSAGE_INDISPONIBLE)

    def effacer(self):
        pass


_racine_tk = None      # (racine, identifiant du fil de Tk), donné par utiliser_tk()


def choisir_source_linux():
    """La meilleure source disponible (voir l'ordre en tête du module), ou
    SourceAbsente."""
    force = (os.environ.get("MES_OUTILS_PRESSE_PAPIERS") or "").strip().lower()
    wayland = bool(os.environ.get("WAYLAND_DISPLAY")) and bool(shutil.which("wl-paste")) \
        and bool(shutil.which("wl-copy"))
    x11 = bool(os.environ.get("DISPLAY"))
    tk = _racine_tk is not None
    candidates = [
        ("wayland", wayland, lambda: SourceWayland()),
        ("xclip", x11 and bool(shutil.which("xclip")), lambda: SourceXclip()),
        ("xsel", x11 and bool(shutil.which("xsel")), lambda: SourceXsel()),
        ("tk", tk, lambda: SourceTk(*_racine_tk)),
    ]
    # GNOME (Mutter) n'a pas le protocole « data-control » : wl-paste y crée
    # une fenêtre furtive pour lire le presse-papiers, ce qui peut voler le
    # focus toutes les 0,7 s. Sous GNOME, Wayland passe donc en dernier
    # (XWayland partage le presse-papiers avec les applications Wayland).
    if "GNOME" in (os.environ.get("XDG_CURRENT_DESKTOP") or "").upper():
        candidates.append(candidates.pop(0))
    if force:
        candidates = [c for c in candidates if c[0] == force]
    for _nom, possible, fabrique in candidates:
        if possible:
            return fabrique()
    return SourceAbsente()


def nouvelle_source():
    """La source du système : SourceWindows, ou la meilleure source Linux."""
    if systeme.WINDOWS:
        return SourceWindows()
    return choisir_source_linux()


# ---------------------------------------------------------------------------
# L'historique (en mémoire)
# ---------------------------------------------------------------------------
def _heure():
    return datetime.datetime.now().isoformat(timespec="seconds")


class Historique:
    """Les textes copiés, le plus récent en tête. Rien n'est écrit sur disque."""

    def __init__(self, limite=LIMITE):
        self.limite = limite
        self._elements = []
        self._verrou = threading.RLock()
        self._compteur = itertools.count(1)

    def ajouter(self, texte, quand=None):
        """Ajoute un texte copié. Renvoie l'élément, ou None s'il est ignoré."""
        if not isinstance(texte, str) or not texte.strip() or len(texte) > TAILLE_MAX:
            return None
        with self._verrou:
            if self._elements and self._elements[0]["texte"] == texte:
                return None
            existant = next((e for e in self._elements if e["texte"] == texte), None)
            if existant:
                self._elements.remove(existant)
                existant["quand"] = quand or _heure()
                self._elements.insert(0, existant)
                return dict(existant)
            element = {"id": next(self._compteur), "texte": texte, "quand": quand or _heure(), "epingle": False}
            self._elements.insert(0, element)
            self._rogner()
            return dict(element)

    def _rogner(self):
        libres = [e for e in self._elements if not e["epingle"]]
        for e in libres[self.limite:]:
            self._elements.remove(e)

    def lister(self, recherche=""):
        mots = str(recherche or "").lower().split()
        with self._verrou:
            return [dict(e) for e in self._elements
                    if all(m in e["texte"].lower() for m in mots)]

    def trouver(self, identifiant):
        with self._verrou:
            return next((e for e in self._elements if e["id"] == identifiant), None)

    def remonter(self, identifiant):
        """Passer un élément en tête (il vient d'être recopié)."""
        with self._verrou:
            e = self.trouver(identifiant)
            if e is None:
                raise ValueError("Élément introuvable (déjà effacé ?).")
            self._elements.remove(e)
            e["quand"] = _heure()
            self._elements.insert(0, e)
            return dict(e)

    def supprimer(self, identifiant):
        with self._verrou:
            avant = len(self._elements)
            self._elements = [e for e in self._elements if e["id"] != identifiant]
            return avant - len(self._elements)

    def vider(self, garder_epingles=True):
        with self._verrou:
            avant = len(self._elements)
            self._elements = [e for e in self._elements if garder_epingles and e["epingle"]]
            return avant - len(self._elements)

    def epingler(self, identifiant, valeur=True):
        with self._verrou:
            e = self.trouver(identifiant)
            if e is None:
                raise ValueError("Élément introuvable (déjà effacé ?).")
            if valeur and not e["epingle"] and sum(x["epingle"] for x in self._elements) >= MAX_EPINGLES:
                raise ValueError("50 éléments épinglés au plus : désépinglez-en un d'abord.")
            e["epingle"] = bool(valeur)
            if not valeur:
                self._rogner()
            return dict(e)

    def __len__(self):
        return len(self._elements)


# ---------------------------------------------------------------------------
# La surveillance
# ---------------------------------------------------------------------------
class Surveillance:
    """Regarde le presse-papiers à intervalle régulier et remplit l'historique.

    source : objet avec numero(), lire() → (texte, raison) et ecrire(texte)
    (SourceWindows, une source Linux, ou une fausse source dans les tests)."""

    def __init__(self, historique, source, intervalle=INTERVALLE):
        self.historique = historique
        self.source = source
        self.intervalle = intervalle
        self.actif = True
        self._dernier = None
        self._fil = None
        self._arret = threading.Event()
        self._verrou = threading.Lock()

    def sonder(self):
        """Un coup d'œil. Renvoie l'élément ajouté, ou None."""
        numero = self.source.numero()
        if numero == self._dernier:
            return None
        if not self.actif:
            self._dernier = numero      # copié pendant la pause : jamais pris
            return None
        texte, raison = self.source.lire()
        if raison == "occupe":
            return None                 # on réessaiera au prochain coup d'œil
        self._dernier = numero
        if texte is None:
            return None
        return self.historique.ajouter(texte)

    def oublier_contenu_actuel(self):
        """Le contenu actuel ne sera pas pris (départ, reprise après pause)."""
        self._dernier = self.source.numero()

    def en_marche(self):
        return self._fil is not None and self._fil.is_alive()

    def demarrer(self):
        with self._verrou:
            if self.en_marche():
                return False
            self._arret.clear()
            self.oublier_contenu_actuel()
            self._fil = threading.Thread(target=self._boucle, name="presse-papiers", daemon=True)
            self._fil.start()
            return True

    def arreter(self):
        self._arret.set()
        if self._fil is not None:
            self._fil.join(timeout=3)

    def _boucle(self):
        while not self._arret.is_set():
            try:
                self.sonder()
            except Exception:  # noqa: BLE001 — la surveillance ne doit jamais mourir
                pass
            self._arret.wait(self.intervalle)


# ---------------------------------------------------------------------------
# Le module : un historique et une surveillance pour toute l'appli
# ---------------------------------------------------------------------------
_historique = Historique()
_surveillance = None
_verrou_module = threading.Lock()


def _la_surveillance():
    global _surveillance
    remplacee = False
    with _verrou_module:
        if _surveillance is None:
            _surveillance = Surveillance(_historique, nouvelle_source())
        elif isinstance(_surveillance.source, SourceAbsente):
            # Un outil a pu être installé depuis, ou la bulle a donné Tk.
            source = nouvelle_source()
            if not isinstance(source, SourceAbsente):
                _surveillance.source = source
                remplacee = True
        s = _surveillance
    if remplacee:
        _oublier(s)     # hors du verrou : la source Tk peut attendre son fil
    return s


def _oublier(s):
    try:
        s.oublier_contenu_actuel()
    except Exception:  # noqa: BLE001 — le prochain coup d'œil réessaiera
        pass


def utiliser_tk(racine):
    """Donne la fenêtre Tk de la bulle (à appeler depuis le fil de Tk). Sous
    Linux, elle sert de presse-papiers quand ni wl-clipboard ni xclip/xsel ne
    sont là ; sans effet sous Windows."""
    global _racine_tk
    if systeme.WINDOWS:
        return
    with _verrou_module:
        _racine_tk = (racine, threading.get_ident())
    _la_surveillance()      # remplace une SourceAbsente déjà créée


def source_disponible():
    return not isinstance(_la_surveillance().source, SourceAbsente)


def ecrire_secret(texte):
    """Copie d'un secret (coffre) sous Linux : il n'entre pas dans
    l'historique. Renvoie l'empreinte, pour effacer_si()."""
    e = empreinte(str(texte))
    _noter_secret(e)            # avant la copie : la surveillance ne doit jamais le prendre
    _la_surveillance().source.ecrire(texte)
    return e


def actif_par_reglage():
    return config.section("presse_papiers").get("actif", True) is not False


def demarrer_surveillance():
    """Lancer la surveillance (sans effet si elle tourne déjà). Renvoie etat()."""
    s = _la_surveillance()
    if not s.en_marche():
        s.actif = actif_par_reglage()
        s.demarrer()
    return etat()


def etat():
    s = _surveillance
    disponible = source_disponible()
    r = {"actif": bool(s.actif) if s else actif_par_reglage(),
         "surveille": bool(s and s.en_marche()) and disponible,
         "nombre": len(_la_surveillance().historique),
         "limite": LIMITE,
         "disponible": disponible}
    if not disponible:
        r["message"] = MESSAGE_INDISPONIBLE
    return r


def lister(recherche=""):
    """Les éléments, le plus récent en tête : [{id, texte, quand, epingle}]."""
    return _la_surveillance().historique.lister(recherche)


def recopier(identifiant):
    """Remettre un élément dans le presse-papiers ; il passe en tête."""
    s = _la_surveillance()
    e = s.historique.remonter(identifiant)
    s.source.ecrire(e["texte"])
    return e


def supprimer(identifiant):
    return _la_surveillance().historique.supprimer(identifiant)


def vider(garder_epingles=True):
    """« Tout effacer » : les épinglés sont gardés, sauf garder_epingles=False."""
    return _la_surveillance().historique.vider(garder_epingles)


def epingler(identifiant, valeur=True):
    return _la_surveillance().historique.epingler(identifiant, valeur)


def pause(valeur=True):
    """pause(True) : plus rien n'est pris ; pause(False) : reprise. Le choix
    est gardé dans les réglages."""
    s = _la_surveillance()
    s.actif = not valeur
    if s.actif:
        s.oublier_contenu_actuel()
    config.modifier_section("presse_papiers", actif=s.actif)
    return etat()


def ecrire_texte(texte):
    """Copie ordinaire d'un texte (utilisée aussi par l'onglet Extraits)."""
    _la_surveillance().source.ecrire(texte)


def effacer_si(e):
    """Vide le presse-papiers s'il contient encore le texte d'empreinte e
    (effacement d'un secret au bout de 30 s, Linux)."""
    source = _la_surveillance().source
    if e is not None and empreinte(source.texte_actuel()) == e:
        source.effacer()
        return True
    return False


# ---------------------------------------------------------------------------
# Routes de la page
# ---------------------------------------------------------------------------
def _pour_page(e):
    texte = e["texte"]
    return {"id": e["id"], "apercu": texte[:APERCU], "longueur": len(texte),
            "lignes": texte.count("\n") + 1, "quand": e["quand"], "epingle": e["epingle"]}


def _route_liste(d):
    demarrer_surveillance()     # sans la bulle (tableau de bord seul), la page la lance
    return {**etat(), "elements": [_pour_page(e) for e in lister(d.get("recherche") or "")]}


def _identifiant(d):
    try:
        return int(d.get("id"))
    except (TypeError, ValueError):
        raise ValueError("Élément introuvable (déjà effacé ?).") from None


ROUTES = {
    "liste": _route_liste,
    "recopier": lambda d: _pour_page(recopier(_identifiant(d))),
    "supprimer": lambda d: {"supprimes": supprimer(_identifiant(d))},
    "vider": lambda d: {"supprimes": vider(not d.get("tout"))},
    "epingler": lambda d: _pour_page(epingler(_identifiant(d), bool(d.get("epingle", True)))),
    "pause": lambda d: pause(bool(d.get("pause", True))),
    "etat": lambda d: etat(),
}
