# -*- coding: utf-8 -*-
"""Coffre à mots de passe de « Mes outils ».

- Le coffre entier (toutes les entrées) est chiffré en AES-256-GCM, avec une
  clé tirée du mot de passe maître par scrypt (lent exprès : chaque essai
  coûte, ce qui décourage les tentatives en série).
- Le mot de passe maître n'est jamais enregistré. La clé ne vit qu'en mémoire,
  tant que le coffre est ouvert ; il se referme après 5 minutes sans usage.
- Le fichier (donnees/coffre.json) ne contient que du chiffré : sans le mot de
  passe maître, il est illisible. Mot de passe maître oublié = coffre perdu.
- Copie dans le presse-papiers : exclue de l'historique Windows (Win + V) et
  de la synchronisation, puis effacée au bout de 30 secondes. Sous Linux, la
  copie passe par presse_papiers.py : elle n'entre pas dans l'historique de
  Mes outils et est effacée de même au bout de 30 secondes.
"""
import base64
import hashlib
import json
import os
import secrets
import threading
import time
import uuid

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

import config  # noqa: E402
import systeme  # noqa: E402

FICHIER = os.path.join(config.DONNEES, "coffre.json")
DELAI_VERROU = 5 * 60          # secondes sans usage avant verrouillage
DELAI_PRESSE_PAPIERS = 30      # secondes avant d'effacer une copie
SCRYPT = {"n": 2 ** 15, "r": 8, "p": 1}
TEMOIN = b"mes-outils-coffre-v1"


class ErreurCoffre(Exception):
    pass


def _b64(b):
    return base64.b64encode(b).decode("ascii")


def _deb64(t):
    return base64.b64decode(t.encode("ascii"))


def _cle(maitre, sel, p=SCRYPT):
    return hashlib.scrypt(maitre.encode("utf-8"), salt=sel, n=p["n"], r=p["r"], p=p["p"],
                          dklen=32, maxmem=128 * 1024 * 1024)


def _chiffrer(cle, clair, associe):
    nonce = secrets.token_bytes(12)
    return {"nonce": _b64(nonce), "chiffre": _b64(AESGCM(cle).encrypt(nonce, clair, associe))}


def _dechiffrer(cle, bloc, associe):
    return AESGCM(cle).decrypt(_deb64(bloc["nonce"]), _deb64(bloc["chiffre"]), associe)


class Coffre:
    def __init__(self, fichier=FICHIER):
        self.fichier = fichier
        self._cle = None
        self._entrees = None
        self._dernier_usage = 0
        self._verrou = threading.RLock()
        self._essais = []  # heures des derniers essais ratés

    # -- état -------------------------------------------------------------------
    def existe(self):
        return os.path.exists(self.fichier)

    def ouvert(self):
        with self._verrou:
            if self._cle is not None and time.time() - self._dernier_usage > DELAI_VERROU:
                self.fermer()
            return self._cle is not None

    def etat(self):
        ouvert = self.ouvert()
        return {"existe": self.existe(), "ouvert": ouvert,
                "restant": max(0, int(DELAI_VERROU - (time.time() - self._dernier_usage))) if ouvert else 0}

    def _toucher(self):
        if not self.ouvert():
            raise ErreurCoffre("Le coffre est verrouillé.")
        self._dernier_usage = time.time()

    # -- création, ouverture, fermeture --------------------------------------------
    def creer(self, maitre):
        with self._verrou:
            if self.existe():
                raise ErreurCoffre("Un coffre existe déjà.")
            _verifier_maitre(maitre)
            sel = secrets.token_bytes(16)
            self._cle = _cle(maitre, sel)
            self._sel = sel
            self._entrees = []
            self._dernier_usage = time.time()
            self._enregistrer()

    def ouvrir(self, maitre):
        with self._verrou:
            if not self.existe():
                raise ErreurCoffre("Aucun coffre : créez-le d'abord.")
            # Freiner les essais en série : après 5 échecs en 5 minutes, il faut attendre.
            maintenant = time.time()
            self._essais = [t for t in self._essais if maintenant - t < 300]
            if len(self._essais) >= 5:
                raise ErreurCoffre("Trop d'essais. Réessayez dans quelques minutes.")
            with open(self.fichier, encoding="utf-8") as f:
                contenu = json.load(f)
            sel = _deb64(contenu["sel"])
            cle = _cle(maitre, sel, contenu.get("scrypt", SCRYPT))
            try:
                if _dechiffrer(cle, contenu["temoin"], b"temoin") != TEMOIN:
                    raise InvalidTag()
                entrees = json.loads(_dechiffrer(cle, contenu["coffre"], b"coffre").decode("utf-8"))
            except InvalidTag:
                self._essais.append(maintenant)
                raise ErreurCoffre("Mot de passe maître incorrect.")
            self._cle, self._sel, self._entrees = cle, sel, entrees
            self._dernier_usage = time.time()

    def fermer(self):
        with self._verrou:
            self._cle = None
            self._entrees = None

    def changer_maitre(self, ancien, nouveau):
        with self._verrou:
            entrees = self._entrees
            self.fermer()
            self.ouvrir(ancien)          # vérifie l'ancien mot de passe
            _verifier_maitre(nouveau)
            self._sel = secrets.token_bytes(16)
            self._cle = _cle(nouveau, self._sel)
            self._entrees = self._entrees if entrees is None else entrees
            self._enregistrer()

    def _enregistrer(self):
        os.makedirs(os.path.dirname(self.fichier), exist_ok=True)
        contenu = {
            "version": 1,
            "algorithme": "AES-256-GCM, clé scrypt",
            "scrypt": SCRYPT,
            "sel": _b64(self._sel),
            "temoin": _chiffrer(self._cle, TEMOIN, b"temoin"),
            "coffre": _chiffrer(self._cle, json.dumps(self._entrees, ensure_ascii=False).encode("utf-8"), b"coffre"),
        }
        if os.path.exists(self.fichier):
            os.replace(self.fichier, self.fichier + ".bak")
        tmp = self.fichier + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(contenu, f, indent=1)
        os.replace(tmp, self.fichier)

    # -- entrées ------------------------------------------------------------------
    def lister(self):
        """Les entrées sans leurs secrets : le mot de passe et la note ne
        quittent le coffre qu'à la demande, un par un."""
        with self._verrou:
            self._toucher()
            return [{k: v for k, v in e.items() if k not in ("mot_de_passe", "note")}
                    | {"a_note": bool(e.get("note"))} for e in self._entrees]

    def reveler(self, identifiant, champ):
        if champ not in ("mot_de_passe", "note"):
            raise ErreurCoffre("Champ inconnu.")
        with self._verrou:
            self._toucher()
            e = next((x for x in self._entrees if x["id"] == identifiant), None)
            if not e:
                raise ErreurCoffre("Entrée introuvable.")
            return e.get(champ, "")

    def enregistrer(self, entree):
        with self._verrou:
            self._toucher()
            entree = {k: (v.strip() if isinstance(v, str) and k != "mot_de_passe" and k != "note" else v)
                      for k, v in entree.items() if k in ("id", "titre", "site", "identifiant", "mot_de_passe", "categorie", "note")}
            if not entree.get("titre"):
                raise ErreurCoffre("Donnez un nom à l'entrée.")
            entree["modifie"] = time.strftime("%Y-%m-%dT%H:%M")
            existante = next((x for x in self._entrees if x["id"] == entree.get("id")), None) if entree.get("id") else None
            if existante:
                # Un mot de passe non renvoyé par l'écran (champ laissé masqué)
                # n'est pas effacé pour autant.
                for champ in ("mot_de_passe", "note"):
                    if champ not in entree:
                        entree[champ] = existante.get(champ, "")
                existante.clear()
                existante.update(entree)
            else:
                entree["id"] = uuid.uuid4().hex[:12]
                entree["cree"] = entree["modifie"]
                self._entrees.append(entree)
            self._enregistrer()
            return {k: v for k, v in entree.items() if k not in ("mot_de_passe", "note")}

    def supprimer(self, identifiant):
        with self._verrou:
            self._toucher()
            avant = len(self._entrees)
            self._entrees = [e for e in self._entrees if e["id"] != identifiant]
            if len(self._entrees) != avant:
                self._enregistrer()
            return avant - len(self._entrees)

    def copier(self, identifiant, champ):
        """Copier un secret dans le presse-papiers, sans passer par la page."""
        valeur = self.reveler(identifiant, champ) if champ in ("mot_de_passe", "note") else None
        if valeur is None:
            with self._verrou:
                self._toucher()
                e = next((x for x in self._entrees if x["id"] == identifiant), None)
                valeur = (e or {}).get(champ, "")
        copier_presse_papiers(valeur, effacer_apres=DELAI_PRESSE_PAPIERS)


def _verifier_maitre(maitre):
    if len(maitre or "") < 10:
        raise ErreurCoffre("Le mot de passe maître doit faire au moins 10 caractères. "
                           "Une phrase de quelques mots est idéale.")


# ---------------------------------------------------------------------------
# Presse-papiers
# ---------------------------------------------------------------------------
CF_UNICODETEXT, GMEM_MOVEABLE = 13, 0x0002
_win = None


def _api_windows():
    """(ctypes, user32, kernel32) du presse-papiers Windows, chargés une fois."""
    global _win
    if _win is None:
        import ctypes  # noqa: PLC0415
        from ctypes import wintypes  # noqa: PLC0415
        u32 = ctypes.WinDLL("user32", use_last_error=True)
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        u32.OpenClipboard.argtypes = [wintypes.HWND]
        u32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
        u32.SetClipboardData.restype = wintypes.HANDLE
        u32.RegisterClipboardFormatW.argtypes = [wintypes.LPCWSTR]
        u32.RegisterClipboardFormatW.restype = wintypes.UINT
        u32.GetClipboardSequenceNumber.restype = wintypes.DWORD
        k32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
        k32.GlobalAlloc.restype = wintypes.HGLOBAL
        k32.GlobalLock.argtypes = [wintypes.HGLOBAL]
        k32.GlobalLock.restype = wintypes.LPVOID
        k32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
        _win = (ctypes, u32, k32)
    return _win


def _ouvrir_presse_papiers():
    _, u32, _ = _api_windows()
    for _ in range(20):
        if u32.OpenClipboard(None):
            return True
        time.sleep(0.05)
    return False


def _donnees_globales(octets):
    ctypes, _, k32 = _api_windows()
    h = k32.GlobalAlloc(GMEM_MOVEABLE, len(octets))
    p = k32.GlobalLock(h)
    ctypes.memmove(p, octets, len(octets))
    k32.GlobalUnlock(h)
    return h


def _copier_windows(texte, effacer_apres=None):
    _, u32, _ = _api_windows()
    if not _ouvrir_presse_papiers():
        raise ErreurCoffre("Le presse-papiers est occupé par un autre programme.")
    try:
        u32.EmptyClipboard()
        u32.SetClipboardData(CF_UNICODETEXT, _donnees_globales((texte + "\0").encode("utf-16-le")))
        # Ni historique (Win + V), ni synchronisation entre appareils.
        for nom in ("ExcludeClipboardContentFromMonitorProcessing", "CanIncludeInClipboardHistory", "CanUploadToCloudClipboard"):
            fmt = u32.RegisterClipboardFormatW(nom)
            u32.SetClipboardData(fmt, _donnees_globales(b"\0\0\0\0"))
    finally:
        u32.CloseClipboard()
    if effacer_apres:
        numero = u32.GetClipboardSequenceNumber()

        def effacer():
            time.sleep(effacer_apres)
            # Seulement si rien d'autre n'a été copié entre-temps.
            if u32.GetClipboardSequenceNumber() == numero and _ouvrir_presse_papiers():
                try:
                    u32.EmptyClipboard()
                finally:
                    u32.CloseClipboard()

        threading.Thread(target=effacer, daemon=True).start()


def _copier_linux(texte, effacer_apres=None):
    """Linux : la source du presse-papiers de presse_papiers.py (Wayland, X11
    ou Tk). Le secret est marqué pour ne pas entrer dans l'historique."""
    import presse_papiers  # noqa: PLC0415
    try:
        empreinte = presse_papiers.ecrire_secret(texte)
    except RuntimeError as erreur:
        raise ErreurCoffre(str(erreur)) from None
    if effacer_apres:
        def effacer():
            time.sleep(effacer_apres)
            # Seulement si le secret est toujours dans le presse-papiers.
            try:
                presse_papiers.effacer_si(empreinte)
            except Exception:  # noqa: BLE001 — rien à signaler à personne
                pass

        threading.Thread(target=effacer, daemon=True).start()


def copier_presse_papiers(texte, effacer_apres=None):
    """Copie un secret : hors historique, effacé après effacer_apres secondes
    si rien d'autre n'a été copié entre-temps."""
    if systeme.WINDOWS:
        _copier_windows(texte, effacer_apres)
    else:
        _copier_linux(texte, effacer_apres)


# ---------------------------------------------------------------------------
# Le coffre du tableau de bord, partagé par tous les onglets (Mots de passe,
# Projets…) : une fois ouvert dans l'un, il l'est pour les autres.
# ---------------------------------------------------------------------------
_partage = None
_verrou_partage = threading.Lock()


def partage():
    global _partage
    with _verrou_partage:
        if _partage is None:
            _partage = Coffre()
        return _partage
