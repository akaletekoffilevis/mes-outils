# -*- coding: utf-8 -*-
"""Réglages et fichiers de données de « Mes outils », partagés par tous les
modules.

- outils.json : les réglages personnels (prénom, langue, tuiles, dossiers de
  projets…), créé depuis outils.exemple.json au premier lancement, jamais
  envoyé sur GitHub ;
- donnees\\<nom>.json : les données de chaque module (écriture sûre, copie
  .bak de la version précédente).

Où sont les données ?
- installé avec Setup.exe (programme « gelé » par PyInstaller) : dans
  %APPDATA%\\Mes outils (elles survivent aux mises à jour et à la
  désinstallation) ; sous Linux (AppImage) : ~/.config/mes-outils ;
- lancé depuis le code source (git clone) : à côté du code, comme avant ;
- la variable d'environnement MES_OUTILS_DONNEES force un autre dossier.

Les tests remplacent FICHIER_OUTILS et DONNEES par des chemins temporaires.
"""
import json
import os
import shutil
import sys
import threading

VERSION = "1.8.0"
DEPOT = "https://github.com/rarianaAina/mes-outils"
API_VERSIONS = "https://api.github.com/repos/rarianaAina/mes-outils/releases/latest"
# Vrai dans le programme installé (Mes outils.exe) : pas de Python sur le PC.
GELE = bool(getattr(sys, "frozen", False))
# Le code et les pages (dans le programme installé : son dossier interne).
ICI = getattr(sys, "_MEIPASS", None) or os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(sys.executable) if GELE else os.path.dirname(ICI)


def dossier_utilisateur():
    """Le dossier des réglages et des données de l'utilisateur."""
    choisi = os.environ.get("MES_OUTILS_DONNEES")
    if choisi:
        return choisi
    if GELE:
        import systeme  # noqa: PLC0415 (évite un import circulaire au chargement)
        return systeme.dossier_donnees_utilisateur()
    return RACINE


BASE = dossier_utilisateur()
FICHIER_OUTILS = os.path.join(BASE, "outils.json")
FICHIER_EXEMPLE = os.path.join(ICI if GELE else RACINE, "outils.exemple.json")
DONNEES = os.path.join(BASE, "donnees")
FICHIER_BULLE = os.path.join(BASE, "bulle.json")
JOURNAL = os.path.join(BASE if GELE else ICI, "hub.log")
LANGUES = ("fr", "en")
THEMES = ("auto", "clair", "sombre")
# Métiers proposés au premier lancement (ils pré-cochent des applications).
PROFILS = ("freelance", "assistant_virtuel", "assistant_direction", "developpeur", "personnalise")
# Toujours présentes, jamais désactivables.
APPS_FIXES = ("accueil", "applications", "reglages")

_verrou = threading.RLock()


# ---------------------------------------------------------------------------
# outils.json
# ---------------------------------------------------------------------------
def anciennes_installations():
    """Les copies « code source » de Mes outils déjà utilisées sur ce PC (un
    dossier avec outil/hub.py et outils.json), là où on les installe d'habitude."""
    profil = os.path.expanduser("~")
    parents = [os.path.join(profil, "Documents"), os.path.join(profil, "Desktop"), profil]
    if os.environ.get("OneDrive"):
        parents.insert(1, os.path.join(os.environ["OneDrive"], "Documents"))
    trouvees = []
    for parent in parents:
        for nom in ("Mes outils", "mes-outils"):
            dossier = os.path.join(parent, nom)
            if os.path.isfile(os.path.join(dossier, "outils.json")) and \
                    os.path.isfile(os.path.join(dossier, "outil", "hub.py")) and dossier not in trouvees:
                trouvees.append(dossier)
    return trouvees


def premier_lancement():
    """Si outils.json n'existe pas encore : reprendre les réglages et les
    données d'une ancienne copie « code source » (copiés, jamais déplacés),
    sinon partir de l'exemple. Renvoie le dossier repris, ou None."""
    with _verrou:
        if os.path.exists(FICHIER_OUTILS):
            return None
        os.makedirs(os.path.dirname(FICHIER_OUTILS), exist_ok=True)
        if GELE:
            for ancienne in anciennes_installations():
                if os.path.normcase(ancienne) == os.path.normcase(BASE):
                    continue
                anciennes_donnees = os.path.join(ancienne, "donnees")
                if os.path.isdir(anciennes_donnees):
                    shutil.copytree(anciennes_donnees, DONNEES, dirs_exist_ok=True)
                position = os.path.join(ancienne, "bulle.json")
                if os.path.isfile(position):
                    shutil.copyfile(position, FICHIER_BULLE)
                # outils.json en dernier : sa présence signifie « reprise finie ».
                shutil.copyfile(os.path.join(ancienne, "outils.json"), FICHIER_OUTILS)
                return ancienne
        if os.path.exists(FICHIER_EXEMPLE):
            shutil.copyfile(FICHIER_EXEMPLE, FICHIER_OUTILS)
        return None


def lire():
    """Le contenu d'outils.json (créé au premier lancement : voir premier_lancement)."""
    with _verrou:
        if not os.path.exists(FICHIER_OUTILS):
            premier_lancement()
        try:
            with open(FICHIER_OUTILS, encoding="utf-8-sig") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"outils": []}


def ecrire(contenu):
    with _verrou:
        contenu = {k: v for k, v in contenu.items() if k != "bulle"}
        os.makedirs(os.path.dirname(FICHIER_OUTILS), exist_ok=True)
        tmp = FICHIER_OUTILS + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(contenu, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp, FICHIER_OUTILS)


def modifier(**valeurs):
    """Change quelques clés d'outils.json sans toucher au reste."""
    with _verrou:
        contenu = lire()
        contenu.update(valeurs)
        ecrire(contenu)
        return contenu


def section(nom):
    """Une section d'outils.json (dictionnaire vide si absente)."""
    valeur = lire().get(nom)
    return valeur if isinstance(valeur, dict) else {}


def modifier_section(nom, **valeurs):
    with _verrou:
        contenu = lire()
        sec = contenu.get(nom) if isinstance(contenu.get(nom), dict) else {}
        sec.update(valeurs)
        contenu[nom] = sec
        ecrire(contenu)
        return sec


def langue():
    valeur = lire().get("langue") or "fr"
    return valeur if valeur in LANGUES else "fr"


def theme():
    valeur = lire().get("theme") or "auto"
    return valeur if valeur in THEMES else "auto"


def app_active(nom):
    """Vrai si l'application est active (page Applications). Anciennes
    installations sans choix : tout est actif sauf les onglets masqués."""
    if nom in APPS_FIXES:
        return True
    contenu = lire()
    choisies = contenu.get("apps_actives")
    if isinstance(choisies, list):
        return nom in choisies
    return nom not in (contenu.get("onglets_masques") or [])


def dossiers_projets():
    """Les dossiers où chercher les projets (GitHub, Projets, État Git).
    Ancien emplacement : github > dossiers."""
    contenu = lire()
    dossiers = contenu.get("dossiers_projets")
    if dossiers is None:
        dossiers = (contenu.get("github") or {}).get("dossiers") or []
    return [d for d in dossiers if isinstance(d, str) and d.strip()]


def enregistrer_dossiers_projets(dossiers):
    nouveaux = []
    for chemin in dossiers or []:
        chemin = os.path.normpath(str(chemin).strip().strip('"'))
        if not os.path.isdir(chemin):
            raise ValueError(f"Dossier introuvable : {chemin}")
        if chemin not in nouveaux:
            nouveaux.append(chemin)
    with _verrou:
        contenu = lire()
        contenu["dossiers_projets"] = nouveaux
        if isinstance(contenu.get("github"), dict):
            contenu["github"].pop("dossiers", None)
        ecrire(contenu)
    return nouveaux


# ---------------------------------------------------------------------------
# donnees\<nom>.json
# ---------------------------------------------------------------------------
def chemin_donnees(nom):
    return os.path.join(DONNEES, nom + ".json")


def lire_donnees(nom, defaut=None):
    """Le contenu de donnees\\<nom>.json, ou « defaut » s'il n'existe pas."""
    with _verrou:
        try:
            with open(chemin_donnees(nom), encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return [] if defaut is None else defaut


def ecrire_donnees(nom, valeur):
    """Écriture sûre : fichier temporaire puis remplacement, copie .bak."""
    with _verrou:
        os.makedirs(DONNEES, exist_ok=True)
        chemin = chemin_donnees(nom)
        if os.path.exists(chemin):
            shutil.copyfile(chemin, chemin + ".bak")
        tmp = chemin + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(valeur, f, ensure_ascii=False, indent=1)
        os.replace(tmp, chemin)
