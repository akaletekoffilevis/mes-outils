# -*- coding: utf-8 -*-
"""Onglet Musique : lecteur audio local.

Playlist de fichiers audio (mp3, wav, ogg, m4a, flac, aac, opus) stockés
dans donnees/musique.json ; les fichiers restent où ils sont (on garde
seulement leur chemin). Routes POST /api/musique/<action>.
"""
import os
import uuid

import config

NOM = "musique"
EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac", ".opus", ".wma"}


def _tous():
    elements = config.lire_donnees(NOM, [])
    return elements if isinstance(elements, list) else []


def lister(d):
    return {"pistes": _tous()}


def ajouter(d):
    chemin = os.path.normpath(str(d.get("chemin") or "").strip().strip('"'))
    if not chemin or not os.path.isfile(chemin):
        raise ValueError("Fichier introuvable.")
    ext = os.path.splitext(chemin)[1].lower()
    if ext not in EXTENSIONS:
        raise ValueError(f"Format non pris en charge ({ext or 'sans extension'}).")
    elements = _tous()
    if any(e.get("chemin") == chemin for e in elements):
        raise ValueError("Cette piste est déjà dans la playlist.")
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
        raise ValueError("Piste introuvable.")
    config.ecrire_donnees(NOM, restants)
    return {"supprimes": 1}


def vider(d):
    config.ecrire_donnees(NOM, [])
    return {"ok": True}


ROUTES = {"lister": lister, "ajouter": ajouter, "supprimer": supprimer, "vider": vider}