# -*- coding: utf-8 -*-
"""Onglet « Docker » : les conteneurs de ce PC, groupés par projet compose,
avec démarrer / arrêter / redémarrer / supprimer et le journal.

Le module s'appelle « conteneurs » (et non « docker ») pour ne pas masquer
un éventuel paquet Python « docker ».

Tout passe par la commande docker, toujours en liste d'arguments, avec un
délai maximum. Les identifiants reçus de la page sont vérifiés avant.
"""
import json
import os
import re
import shutil
import subprocess
import webbrowser

import systeme

SANS_FENETRE = systeme.SANS_FENETRE  # 0 hors de Windows
# Linux : Docker Engine (service systemd) ou Docker Desktop pour Linux.
DESKTOP_LINUX = "/opt/docker-desktop/bin/docker-desktop"
DOCKER_LINUX = ("/usr/bin/docker", "/usr/local/bin/docker", "/snap/bin/docker")

# Identifiant (hexadécimal) ou nom de conteneur : jamais de « - » au début.
ID_VALIDE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,127}$")
PROJET_VALIDE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
ETIQUETTE_PROJET = "com.docker.compose.project"
ETIQUETTE_SERVICE = "com.docker.compose.service"
ADRESSE_DOCKER = "https://www.docker.com/products/docker-desktop/"


class ErreurDocker(Exception):
    """Message pour l'utilisateur (réponse 400)."""


# ---------------------------------------------------------------------------
# Où est Docker ?
# ---------------------------------------------------------------------------
def _programmes():
    return os.environ.get("ProgramFiles", r"C:\Program Files")


def chemin_docker():
    """Le programme docker.exe, ou None."""
    trouve = shutil.which("docker")
    if trouve:
        return trouve
    if not systeme.WINDOWS:
        return next((c for c in DOCKER_LINUX if os.path.isfile(c)), None)
    standard = os.path.join(_programmes(), "Docker", "Docker", "resources", "bin", "docker.exe")
    return standard if os.path.isfile(standard) else None


def chemin_desktop():
    """Docker Desktop dans son dossier standard, ou None."""
    if not systeme.WINDOWS:
        return DESKTOP_LINUX if os.path.isfile(DESKTOP_LINUX) else None
    chemin = os.path.join(_programmes(), "Docker", "Docker", "Docker Desktop.exe")
    return chemin if os.path.isfile(chemin) else None


def _docker(*arguments, delai=30):
    """Lance « docker <arguments> » ; rend (code, sortie, erreurs)."""
    programme = chemin_docker()
    if not programme:
        raise ErreurDocker("Docker n'est pas installé.")
    try:
        r = subprocess.run([programme, *arguments], capture_output=True, timeout=delai,
                           **systeme.options_sans_fenetre())
    except subprocess.TimeoutExpired:
        raise ErreurDocker("Docker ne répond pas (délai dépassé).") from None
    sortie = (r.stdout or b"").decode("utf-8", errors="replace")
    erreurs = (r.stderr or b"").decode("utf-8", errors="replace")
    return r.returncode, sortie, erreurs


def _docker_ok(*arguments, delai=30):
    """Comme _docker, mais lève ErreurDocker si la commande échoue."""
    code, sortie, erreurs = _docker(*arguments, delai=delai)
    if code != 0:
        lignes = [x.strip() for x in (erreurs or sortie).splitlines() if x.strip()]
        raise ErreurDocker("Docker : " + (lignes[0] if lignes else f"erreur {code}"))
    return sortie


def etat():
    """{"installe", "demarre", "desktop", "version"}."""
    resultat = {"installe": bool(chemin_docker()), "demarre": False,
                "desktop": bool(chemin_desktop()), "version": "", "adresse": ADRESSE_DOCKER}
    if not resultat["installe"]:
        return resultat
    try:
        code, sortie, erreurs = _docker("version", "--format", "{{.Server.Version}}", delai=10)
    except (ErreurDocker, OSError):
        return resultat
    version = sortie.strip()
    resultat["demarre"] = code == 0 and bool(version)
    resultat["version"] = version if resultat["demarre"] else ""
    if not systeme.WINDOWS and not resultat["demarre"]:
        resultat["erreur"] = message_linux(erreurs, resultat["desktop"])
    return resultat


def message_linux(erreurs, desktop=False):
    """Pourquoi Docker ne répond pas sous Linux : droits sur la socket, ou
    service arrêté."""
    if "permission denied" in (erreurs or "").lower():
        return ("Accès refusé à Docker : ajoutez votre compte au groupe docker "
                "(sudo usermod -aG docker $USER), puis rouvrez la session.")
    if desktop:
        return "Docker Desktop n'est pas démarré."
    return "Le service Docker n'est pas démarré (sudo systemctl start docker)."


# ---------------------------------------------------------------------------
# Lecture des sorties JSON de docker
# ---------------------------------------------------------------------------
def lignes_json(sortie):
    """Une sortie « --format '{{json .}}' » : un objet JSON par ligne."""
    objets = []
    for ligne in sortie.splitlines():
        ligne = ligne.strip()
        if not ligne:
            continue
        try:
            objet = json.loads(ligne)
        except ValueError:
            continue
        if isinstance(objet, dict):
            objets.append(objet)
    return objets


def lire_etiquettes(texte):
    """« a=1,b=x,y » → {"a": "1", "b": "x,y"} (une valeur peut contenir des virgules)."""
    etiquettes, derniere = {}, None
    for morceau in (texte or "").split(","):
        if "=" in morceau:
            cle, _, valeur = morceau.partition("=")
            derniere = cle.strip()
            etiquettes[derniere] = valeur
        elif derniere is not None:
            etiquettes[derniere] += "," + morceau
    return etiquettes


def lire_ports(texte):
    """« 0.0.0.0:8080->80/tcp, :::8080->80/tcp, 5432/tcp » →
    [{"hote": 8080, "conteneur": 80, "proto": "tcp"}, {"hote": None, "conteneur": 5432, …}]."""
    ports, vus = [], set()
    for morceau in (texte or "").split(","):
        morceau = morceau.strip()
        if not morceau:
            continue
        hote = None
        if "->" in morceau:
            gauche, _, morceau = morceau.partition("->")
            m = re.search(r":(\d+)(?:-\d+)?$", gauche)
            hote = int(m.group(1)) if m else None
        m = re.match(r"^(\d+)(?:-\d+)?/(\w+)$", morceau)
        if not m:
            continue
        cle = (hote, int(m.group(1)), m.group(2))
        if cle in vus:
            continue
        vus.add(cle)
        ports.append({"hote": hote, "conteneur": int(m.group(1)), "proto": m.group(2)})
    return ports


def lire_conteneurs(sortie):
    conteneurs = []
    for c in lignes_json(sortie):
        etiquettes = lire_etiquettes(c.get("Labels", ""))
        conteneurs.append({
            "id": c.get("ID", ""),
            "nom": (c.get("Names") or "").split(",")[0],
            "image": c.get("Image", ""),
            "etat": (c.get("State") or "").lower(),
            "statut": c.get("Status", ""),
            "ports": lire_ports(c.get("Ports", "")),
            "projet": etiquettes.get(ETIQUETTE_PROJET, ""),
            "service": etiquettes.get(ETIQUETTE_SERVICE, ""),
            "cree": c.get("CreatedAt", ""),
        })
    return conteneurs


def grouper(conteneurs):
    """Les conteneurs par projet compose ; ceux sans projet à la fin."""
    groupes = {}
    for c in conteneurs:
        groupes.setdefault(c["projet"], []).append(c)
    noms = sorted(n for n in groupes if n) + ([""] if "" in groupes else [])
    return [{"projet": n, "conteneurs": sorted(groupes[n], key=lambda c: (c["service"] or c["nom"]).lower()),
             "en_marche": sum(1 for c in groupes[n] if c["etat"] == "running")} for n in noms]


# ---------------------------------------------------------------------------
# Vérifications
# ---------------------------------------------------------------------------
def valider_id(valeur):
    valeur = str(valeur or "").strip()
    if not ID_VALIDE.match(valeur):
        raise ValueError("Identifiant de conteneur invalide.")
    return valeur


def valider_projet(valeur):
    valeur = str(valeur or "").strip()
    if not PROJET_VALIDE.match(valeur):
        raise ValueError("Nom de projet invalide.")
    return valeur


def _demarre():
    e = etat()
    if not e["installe"]:
        raise ErreurDocker("Docker n'est pas installé.")
    if not e["demarre"]:
        raise ErreurDocker(e.get("erreur") or "Docker Desktop n'est pas démarré.")
    return e


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
def liste(d):
    e = etat()
    if not e["demarre"]:
        return {**e, "groupes": []}
    sortie = _docker_ok("ps", "-a", "--no-trunc", "--format", "{{json .}}", delai=20)
    conteneurs = lire_conteneurs(sortie)
    for c in conteneurs:
        c["id"] = c["id"][:12]
    return {**e, "groupes": grouper(conteneurs), "nombre": len(conteneurs)}


def _action(commande, message):
    def faire(d):
        _demarre()
        ident = valider_id(d.get("id"))
        _docker_ok(commande, ident, delai=90)
        return {"ok": True, "message": message}
    return faire


def supprimer(d):
    """Supprime un conteneur arrêté (jamais « -f »)."""
    _demarre()
    ident = valider_id(d.get("id"))
    en_marche = _docker_ok("inspect", "--format", "{{.State.Running}}", ident, delai=20).strip().lower()
    if en_marche != "false":
        raise ErreurDocker("Arrêtez d'abord le conteneur.")
    _docker_ok("rm", ident, delai=60)
    return {"ok": True}


def journal(d):
    _demarre()
    ident = valider_id(d.get("id"))
    code, sortie, erreurs = _docker("logs", "--tail", "300", "--timestamps", ident, delai=20)
    if code != 0:
        lignes = [x for x in erreurs.splitlines() if x.strip()]
        raise ErreurDocker("Docker : " + (lignes[0] if lignes else f"erreur {code}"))
    # docker logs renvoie la sortie d'erreur du conteneur sur stderr : on
    # remet tout dans l'ordre de l'horodatage.
    lignes = sorted([x for x in (sortie + "\n" + erreurs).splitlines() if x.strip()], key=lambda x: x[:35])
    return {"texte": "\n".join(lignes[-300:])}


def projet(action):
    def faire(d):
        _demarre()
        nom = valider_projet(d.get("projet"))
        code, _, _ = _docker("compose", "-p", nom, action, delai=180)
        if code != 0:
            # Sans fichier compose : les conteneurs du projet un par un.
            ids = _docker_ok("ps", "-a", "-q", "--filter", f"label={ETIQUETTE_PROJET}={nom}", delai=20).split()
            ids = [valider_id(i) for i in ids]
            if not ids:
                raise ErreurDocker("Aucun conteneur dans ce projet.")
            _docker_ok(action, *ids, delai=180)
        return {"ok": True}
    return faire


def ressources(d):
    """Images (taille) et place occupée (docker system df)."""
    _demarre()
    images = [{"depot": i.get("Repository", ""), "tag": i.get("Tag", ""), "id": i.get("ID", ""),
               "taille": i.get("Size", ""), "cree": i.get("CreatedSince", "")}
              for i in lignes_json(_docker_ok("images", "--format", "{{json .}}", delai=30))]
    place = [{"type": x.get("Type", ""), "nombre": x.get("TotalCount", ""), "actifs": x.get("Active", ""),
              "taille": x.get("Size", ""), "recuperable": x.get("Reclaimable", "")}
             for x in lignes_json(_docker_ok("system", "df", "--format", "{{json .}}", delai=60))]
    return {"images": images, "place": place}


def ouvrir(d):
    try:
        port = int(d.get("port"))
    except (TypeError, ValueError):
        raise ValueError("Numéro de port invalide.") from None
    if not 1 <= port <= 65535:
        raise ValueError("Numéro de port invalide.")
    webbrowser.open(f"http://localhost:{port}/")
    return {"ok": True}


def lancer_desktop(d):
    chemin = chemin_desktop()
    if not chemin:
        raise ErreurDocker("Docker Desktop est introuvable sur ce PC.")
    if systeme.WINDOWS:
        systeme.ouvrir(chemin)
    elif shutil.which("systemctl"):
        # Docker Desktop pour Linux est un service de l'utilisateur.
        systeme.lancer_detache(["systemctl", "--user", "start", "docker-desktop"])
    else:
        systeme.lancer_detache([chemin])
    return {"ok": True}


def page_docker(d):
    webbrowser.open(ADRESSE_DOCKER)
    return {"ok": True}


ROUTES = {
    "liste": liste,
    "demarrer": _action("start", "Conteneur démarré"),
    "arreter": _action("stop", "Conteneur arrêté"),
    "redemarrer": _action("restart", "Conteneur redémarré"),
    "supprimer": supprimer,
    "journal": journal,
    "projet/demarrer": projet("start"),
    "projet/arreter": projet("stop"),
    "ressources": ressources,
    "ouvrir": ouvrir,
    "desktop": lancer_desktop,
    "telecharger": page_docker,
}
