# -*- coding: utf-8 -*-
"""Onglet Vidéo : visionneuse locale.

Playlist de fichiers vidéo (mp4, webm, ogg, mov, avi, mkv, m4v) stockés
dans donnees/video.json ; les fichiers restent où ils sont. Routes POST
/api/video/<action>.
"""
import os
import uuid

import config

NOM = "video"
EXTENSIONS = {".mp4", ".webm", ".ogg", ".mov", ".avi", ".mkv", ".m4v", ".wmv"}


def _tous():
    elements = config.lire_donnees(NOM, [])
    return elements if isinstance(elements, list) else []


def lister(d):
    return {"videos": _tous()}


def ajouter(d):
    chemin = os.path.normpath(str(d.get("chemin") or "").strip().strip('"'))
    if not chemin or not os.path.isfile(chemin):
        raise ValueError("Fichier introuvable.")
    ext = os.path.splitext(chemin)[1].lower()
    if ext not in EXTENSIONS:
        raise ValueError(f"Format non pris en charge ({ext or 'sans extension'}).")
    elements = _tous()
    if any(e.get("chemin") == chemin for e in elements):
        raise ValueError("Cette vidéo est déjà dans la liste.")
    titre = os.path.splitext(os.path.basename(chemin))[0]
    element = {"id": uuid.uuid4().hex[:12], "titre": titre, "chemin": chemin}
    elements.append(element)
    config.ecrire_donnees(NOM, elements)
    return element


def supprimer(d):
    identifiant = d.get("id")
    elements = _tous()
    restants = [e for e in elements if e.get("id") != identifiant]
    if len(restants) == len(elements):
        raise ValueError("Vidéo introuvable.")
    config.ecrire_donnees(NOM, restants)
    return {"supprimes": 1}


def vider(d):
    config.ecrire_donnees(NOM, [])
    return {"ok": True}


ROUTES = {"lister": lister, "ajouter": ajouter, "supprimer": supprimer, "vider": vider}