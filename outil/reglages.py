# -*- coding: utf-8 -*-
"""Onglet Réglages : prénom, langue, onglets affichés, dossiers de projets,
raccourcis Windows, mise à jour. Routes POST /api/reglages/<action>.

Aussi : la fenêtre « Choisir un dossier » de Windows, utilisée par tous les
onglets (POST /api/reglages/choisir_dossier).
"""
import json
import os
import re
import subprocess
import tempfile
import threading
import urllib.error
import urllib.request

import config
import installation

CREATE_NO_WINDOW = 0x08000000
NOUVEAU_GROUPE = 0x00000200  # CREATE_NEW_PROCESS_GROUP
HORS_DU_JOB = 0x01000000     # CREATE_BREAKAWAY_FROM_JOB


def _git(*args, delai=60):
    return subprocess.run(["git", "-C", config.RACINE, *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=delai, creationflags=CREATE_NO_WINDOW)


def lire(_d=None):
    contenu = config.lire()
    return {
        "prenom": contenu.get("prenom") or "",
        "langue": config.langue(),
        "theme": config.theme(),
        "onglets_masques": contenu.get("onglets_masques") or [],
        "apps_actives": contenu.get("apps_actives"),
        "profil": contenu.get("profil") or "",
        "dossiers_projets": config.dossiers_projets(),
        "version": config.VERSION,
        "depot": config.DEPOT,
        "raccourcis": installation.etat(),
        "maj_possible": True,
        "installe": config.GELE,
    }


def enregistrer(d):
    valeurs = {}
    if "prenom" in d:
        valeurs["prenom"] = str(d["prenom"] or "").strip()[:40]
    if "langue" in d:
        if d["langue"] not in config.LANGUES:
            raise ValueError("Langue inconnue.")
        valeurs["langue"] = d["langue"]
    if "theme" in d:
        if d["theme"] not in config.THEMES:
            raise ValueError("Thème inconnu.")
        valeurs["theme"] = d["theme"]
    if "apps_actives" in d:
        apps = d["apps_actives"]
        if apps is not None and (not isinstance(apps, list) or not all(isinstance(n, str) and n.isidentifier() for n in apps)):
            raise ValueError("Liste d'applications invalide.")
        valeurs["apps_actives"] = None if apps is None else sorted(set(apps) - set(config.APPS_FIXES))
    if "profil" in d:
        if d["profil"] not in config.PROFILS:
            raise ValueError("Profil inconnu.")
        valeurs["profil"] = d["profil"]
    if "assistant_fait" in d:
        valeurs["assistant_fait"] = bool(d["assistant_fait"])
    if "onglets_masques" in d:
        masques = d["onglets_masques"] or []
        if not isinstance(masques, list) or not all(isinstance(n, str) and n.isidentifier() for n in masques):
            raise ValueError("Liste d'onglets invalide.")
        valeurs["onglets_masques"] = [n for n in masques if n not in ("accueil", "reglages")]
    config.modifier(**valeurs)
    return lire()


def dossiers(d):
    config.enregistrer_dossiers_projets(d.get("dossiers"))
    return lire()


def raccourci(d):
    genre = d.get("genre")
    if genre not in installation.CSIDL:
        raise ValueError("Raccourci inconnu.")
    if d.get("actif"):
        installation.creer_raccourci(genre)
    else:
        installation.supprimer_raccourci(genre)
    return lire()


def _version(texte):
    """« v1.10.2 » → (1, 10, 2), pour comparer des versions."""
    return tuple(int(x) for x in re.findall(r"\d+", texte or "")[:3])


def derniere_version():
    """La dernière version publiée sur GitHub (page Releases) et son
    installateur (Mes-outils-Setup.exe)."""
    requete = urllib.request.Request(config.API_VERSIONS, headers={
        "Accept": "application/vnd.github+json", "User-Agent": "mes-outils"})
    try:
        with urllib.request.urlopen(requete, timeout=15) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise ValueError("Aucune version publiée pour l'instant.") from None
        raise ValueError(f"GitHub ne répond pas (erreur {e.code}).") from None
    except OSError:
        raise ValueError("Pas de connexion à GitHub (Internet ?).") from None
    setup = next((a.get("browser_download_url") for a in d.get("assets") or []
                  if str(a.get("name", "")).lower().endswith(".exe")), None)
    return {"version": str(d.get("tag_name") or "").lstrip("vV"), "page": d.get("html_url") or config.DEPOT + "/releases",
            "setup": setup}


def mise_a_jour(_d=None):
    """Programme installé (ou copie sans git) : compare avec la dernière
    version publiée sur GitHub et donne le lien de l'installateur.
    Copie installée avec git clone : git pull --ff-only, jamais par-dessus des
    modifications locales."""
    if config.GELE or not os.path.isdir(os.path.join(config.RACINE, ".git")):
        info = derniere_version()
        if _version(info["version"]) > _version(config.VERSION):
            return {"change": False, "nouvelle": info["version"], "telecharger": info["setup"] or info["page"],
                    "automatique": config.GELE and bool(info["setup"])}
        return {"change": False}
    if _git("status", "--porcelain", "--untracked-files=no").stdout.strip():
        raise ValueError("Des fichiers de « Mes outils » ont été modifiés sur ce PC : mise à jour annulée.")
    avant = _git("rev-parse", "HEAD").stdout.strip()
    r = _git("pull", "--ff-only", delai=120)
    if r.returncode != 0:
        raise RuntimeError("La mise à jour a échoué : " + (r.stderr or r.stdout).strip()[:300])
    apres = _git("rev-parse", "HEAD").stdout.strip()
    return {"change": avant != apres, "message": (r.stdout or "").strip()[:500]}


# L'installateur ne peut venir que des versions publiées du dépôt.
PREFIXE_SETUP = config.DEPOT + "/releases/download/"
# Une fois Mes outils fermé, l'installateur tourne seul (barre de progression,
# aucune question) puis relance Mes outils (/RELANCER, voir installateur.iss).
SCRIPT_MISE_A_JOUR = ("Start-Sleep -Seconds 3; Start-Process -FilePath $env:MO_SETUP "
                      "-ArgumentList '/SILENT','/SUPPRESSMSGBOXES','/NORESTART','/RELANCER'")


def telecharger_installateur(url, version):
    """Télécharge Mes-outils-Setup.exe dans le dossier temporaire et vérifie
    que c'est bien un programme Windows."""
    if not url or not url.startswith(PREFIXE_SETUP):
        raise ValueError("Installateur introuvable dans la dernière version publiée.")
    dossier = os.path.join(tempfile.gettempdir(), "mes-outils-mise-a-jour")
    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, f"Mes-outils-Setup-{re.sub(r'[^0-9.]', '', version)}.exe")
    partiel = chemin + ".part"
    requete = urllib.request.Request(url, headers={"User-Agent": "mes-outils"})
    try:
        with urllib.request.urlopen(requete, timeout=60) as r, open(partiel, "wb") as f:
            while True:
                bloc = r.read(1 << 16)
                if not bloc:
                    break
                f.write(bloc)
    except OSError:
        raise ValueError("Téléchargement de la mise à jour impossible (Internet ?).") from None
    with open(partiel, "rb") as f:
        debut = f.read(2)
    if debut != b"MZ" or os.path.getsize(partiel) < 1_000_000:
        os.remove(partiel)
        raise ValueError("Le fichier téléchargé n'est pas un installateur valide.")
    os.replace(partiel, chemin)
    return chemin


def lancer_apres_fermeture(chemin):
    """Lance la petite tâche PowerShell qui installera la mise à jour une fois
    Mes outils fermé. Pas de DETACHED_PROCESS : PowerShell a besoin d'une
    console (invisible ici) pour démarrer. Elle quitte si possible le groupe
    de processus de Mes outils pour lui survivre."""
    commande = ["powershell", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", SCRIPT_MISE_A_JOUR]
    options = dict(env=dict(os.environ, MO_SETUP=chemin), close_fds=True,
                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = CREATE_NO_WINDOW | NOUVEAU_GROUPE
    try:
        return subprocess.Popen(commande, creationflags=base | HORS_DU_JOB, **options)
    except OSError:
        return subprocess.Popen(commande, creationflags=base, **options)


def installer_mise_a_jour(_d=None):
    """Programme installé : télécharge la dernière version, ferme Mes outils
    et lance l'installateur, qui relance Mes outils à la fin. Les réglages et
    les données (dans %APPDATA%) ne sont pas touchés."""
    if not config.GELE:
        raise ValueError("Installation automatique réservée au programme installé (Setup.exe).")
    info = derniere_version()
    if _version(info["version"]) <= _version(config.VERSION):
        return {"a_jour": True}
    chemin = telecharger_installateur(info["setup"], info["version"])
    lancer_apres_fermeture(chemin)
    # La réponse part d'abord, puis Mes outils (bulle et serveur) se ferme
    # pour que l'installateur puisse remplacer le programme.
    threading.Timer(1.5, lambda: os._exit(0)).start()
    return {"installation": True, "version": info["version"]}


SCRIPT_DOSSIER = r"""
Add-Type -AssemblyName System.Windows.Forms
$p = New-Object System.Windows.Forms.Form
$p.TopMost = $true
$d = New-Object System.Windows.Forms.FolderBrowserDialog
$d.Description = $env:MO_TITRE
$d.ShowNewFolderButton = $true
if ($env:MO_DEPART -and (Test-Path -LiteralPath $env:MO_DEPART)) { $d.SelectedPath = $env:MO_DEPART }
if ($d.ShowDialog($p) -eq [System.Windows.Forms.DialogResult]::OK) {
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  Write-Output $d.SelectedPath
}
"""


def choisir_dossier(d):
    """Ouvre la fenêtre « Choisir un dossier » de Windows, au premier plan.
    Renvoie {"chemin": "..."} ou {"chemin": None} si annulé."""
    env = dict(os.environ, MO_TITRE=str(d.get("titre") or "Choisir un dossier")[:120],
               MO_DEPART=str(d.get("depart") or ""))
    r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-STA", "-Command", SCRIPT_DOSSIER],
                       env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=600, creationflags=CREATE_NO_WINDOW)
    chemin = (r.stdout or "").strip().splitlines()
    return {"chemin": chemin[-1] if chemin and os.path.isdir(chemin[-1]) else None}


ROUTES = {
    "lire": lire,
    "enregistrer": enregistrer,
    "dossiers": dossiers,
    "raccourci": raccourci,
    "mise_a_jour": mise_a_jour,
    "installer_mise_a_jour": installer_mise_a_jour,
    "choisir_dossier": choisir_dossier,
}
