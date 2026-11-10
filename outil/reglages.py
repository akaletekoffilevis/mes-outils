# -*- coding: utf-8 -*-
"""Onglet Réglages : prénom, langue, onglets affichés, dossiers de projets,
raccourcis (Windows : Bureau et démarrage ; Linux : menu des applications et
démarrage avec la session), bulle et icône (Linux), mise à jour. Routes
POST /api/reglages/<action>.

Aussi : la fenêtre « Choisir un dossier » du système, utilisée par tous les
onglets (POST /api/reglages/choisir_dossier).

Mise à jour du programme installé :
- Windows : Mes-outils-Setup.exe de la dernière version publiée, lancé en
  silencieux une fois Mes outils fermé ;
- Linux : Mes-outils-x86_64.AppImage, téléchargée à côté de l'AppImage en
  cours ($APPIMAGE), vérifiée, rendue exécutable, mise à sa place d'un coup,
  puis relancée.
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
import icone_linux
import installation
import systeme

CREATE_NO_WINDOW = 0x08000000
NOUVEAU_GROUPE = 0x00000200  # CREATE_NEW_PROCESS_GROUP
HORS_DU_JOB = 0x01000000     # CREATE_BREAKAWAY_FROM_JOB
# Linux : bulle et icône, bulle seule, icône seule (voir bulle.py).
PRESENCES = ("bulle_icone", "bulle", "icone")
NOM_APPIMAGE = "Mes-outils-x86_64.AppImage"


def _git(*args, delai=60):
    return subprocess.run(["git", "-C", config.RACINE, *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=delai, **systeme.options_sans_fenetre())


def nom_systeme():
    return "windows" if systeme.WINDOWS else "linux" if systeme.LINUX else "mac"


def appimage_courante():
    """Linux : le chemin de l'AppImage qui tourne ($APPIMAGE), ou None."""
    chemin = os.environ.get("APPIMAGE")
    return chemin if chemin and os.path.isfile(chemin) else None


def lire(_d=None):
    contenu = config.lire()
    infos = {
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
        "systeme": nom_systeme(),
    }
    if not systeme.WINDOWS:
        presence = contenu.get("presence")
        infos["presence"] = presence if presence in PRESENCES else "bulle_icone"
        infos["icone_possible"] = icone_linux.disponible()
        infos["appimage"] = bool(appimage_courante())
    return infos


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
    if "presence" in d:
        if d["presence"] not in PRESENCES:
            raise ValueError("Affichage inconnu.")
        valeurs["presence"] = d["presence"]
    config.modifier(**valeurs)
    return lire()


def dossiers(d):
    config.enregistrer_dossiers_projets(d.get("dossiers"))
    return lire()


def raccourci(d):
    genre = d.get("genre")
    if genre not in installation.genres():
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
    """La dernière version publiée sur GitHub (page Releases), son
    installateur Windows (Mes-outils-Setup.exe) et son AppImage Linux ;
    « fichier » : celui de ce système."""
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
    fichiers = [(str(a.get("name", "")), a.get("browser_download_url")) for a in d.get("assets") or []]
    setup = next((url for nom, url in fichiers if nom.lower().endswith(".exe")), None)
    appimage = next((url for nom, url in fichiers if nom == NOM_APPIMAGE), None) or \
        next((url for nom, url in fichiers if nom.lower().endswith("x86_64.appimage")), None)
    return {"version": str(d.get("tag_name") or "").lstrip("vV"), "page": d.get("html_url") or config.DEPOT + "/releases",
            "setup": setup, "appimage": appimage, "fichier": setup if systeme.WINDOWS else appimage}


def installation_automatique_possible(info):
    """Vrai si la mise à jour peut s'installer toute seule : programme
    installé avec Setup.exe (Windows), ou AppImage lancée en tant que telle
    (Linux)."""
    if not config.GELE or not info.get("fichier"):
        return False
    return systeme.WINDOWS or bool(appimage_courante())


def mise_a_jour(_d=None):
    """Programme installé (ou copie sans git) : compare avec la dernière
    version publiée sur GitHub et donne le lien du fichier de ce système
    (installateur Windows ou AppImage Linux).
    Copie installée avec git clone : git pull --ff-only, jamais par-dessus des
    modifications locales."""
    if config.GELE or not os.path.isdir(os.path.join(config.RACINE, ".git")):
        info = derniere_version()
        if _version(info["version"]) > _version(config.VERSION):
            return {"change": False, "nouvelle": info["version"], "telecharger": info["fichier"] or info["page"],
                    "automatique": installation_automatique_possible(info), "systeme": nom_systeme()}
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


def _telecharger(url, chemin):
    """Télécharge url dans chemin (le fichier doit déjà pouvoir être créé)."""
    requete = urllib.request.Request(url, headers={"User-Agent": "mes-outils"})
    with open(chemin, "wb") as f:
        try:
            with urllib.request.urlopen(requete, timeout=60) as r:
                while True:
                    bloc = r.read(1 << 16)
                    if not bloc:
                        break
                    f.write(bloc)
        except OSError:
            raise ValueError("Téléchargement de la mise à jour impossible (Internet ?).") from None


def telecharger_installateur(url, version):
    """Télécharge Mes-outils-Setup.exe dans le dossier temporaire et vérifie
    que c'est bien un programme Windows."""
    if not url or not url.startswith(PREFIXE_SETUP):
        raise ValueError("Installateur introuvable dans la dernière version publiée.")
    dossier = os.path.join(tempfile.gettempdir(), "mes-outils-mise-a-jour")
    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, f"Mes-outils-Setup-{re.sub(r'[^0-9.]', '', version)}.exe")
    partiel = chemin + ".part"
    try:
        _telecharger(url, partiel)
    except ValueError:
        if os.path.exists(partiel):
            os.remove(partiel)
        raise
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


# ---------------------------------------------------------------------------
# Linux : mise à jour de l'AppImage
# ---------------------------------------------------------------------------
def appimage_valide(chemin):
    """Vrai si le fichier est un programme Linux (en-tête ELF) au format
    AppImage (marque « AI » 1 ou 2) et d'une taille plausible."""
    try:
        with open(chemin, "rb") as f:
            debut = f.read(11)
        taille = os.path.getsize(chemin)
    except OSError:
        return False
    return debut[:4] == b"\x7fELF" and debut[8:10] == b"AI" and debut[10:11] in (b"\x01", b"\x02") \
        and taille >= 1_000_000


def telecharger_appimage(url, destination):
    """Télécharge la nouvelle AppImage à côté de l'actuelle (« .new »), la
    vérifie, la rend exécutable puis la met à la place de l'ancienne d'un
    seul coup (os.replace). L'AppImage en cours continue de tourner."""
    if not url or not url.startswith(PREFIXE_SETUP):
        raise ValueError("AppImage introuvable dans la dernière version publiée.")
    nouvelle = destination + ".new"
    try:
        _telecharger(url, nouvelle)
    except PermissionError:
        raise ValueError(f"Le dossier de l'AppImage n'est pas modifiable ({os.path.dirname(destination)}) : "
                         "téléchargez la nouvelle version depuis GitHub.") from None
    except ValueError:
        if os.path.exists(nouvelle):
            os.remove(nouvelle)
        raise
    if not appimage_valide(nouvelle):
        os.remove(nouvelle)
        raise ValueError("Le fichier téléchargé n'est pas une AppImage valide.")
    os.chmod(nouvelle, 0o755)
    os.replace(nouvelle, destination)
    return destination


def environnement_propre():
    """L'environnement d'un programme lancé hors de l'AppImage : sans les
    variables d'AppImage ni celles de PyInstaller (bibliothèques internes)."""
    env = dict(os.environ)
    for cle in list(env):
        if cle in ("APPIMAGE", "APPDIR", "ARGV0", "OWD", "APPIMAGE_UUID", "TCL_LIBRARY", "TK_LIBRARY") \
                or cle.startswith(("_PYI_", "_MEIPASS")):
            del env[cle]
    origine = env.pop("LD_LIBRARY_PATH_ORIG", None)
    if origine:
        env["LD_LIBRARY_PATH"] = origine
    else:
        env.pop("LD_LIBRARY_PATH", None)
    env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
    return env


def relancer_appimage(chemin):
    """Relance l'AppImage quelques secondes plus tard (Mes outils doit d'abord
    se fermer : verrou de la bulle, port du tableau de bord). Le chemin est
    passé en argument au shell, jamais dans le texte de la commande."""
    return systeme.lancer_detache(["/bin/sh", "-c", 'sleep 3; exec "$0"', chemin], env=environnement_propre())


def installer_mise_a_jour(_d=None):
    """Programme installé : télécharge la dernière version, ferme Mes outils
    et lance la nouvelle (Windows : son installateur, qui relance Mes outils
    à la fin ; Linux : la nouvelle AppImage, mise à la place de l'ancienne).
    Les réglages et les données ne sont pas touchés."""
    if not config.GELE:
        raise ValueError("Installation automatique réservée au programme installé (Setup.exe)." if systeme.WINDOWS else
                         "Installation automatique réservée au programme installé (AppImage).")
    appimage = None
    if not systeme.WINDOWS:
        appimage = appimage_courante()
        if not appimage:
            raise ValueError("Installation automatique réservée au programme installé (AppImage).")
    info = derniere_version()
    if _version(info["version"]) <= _version(config.VERSION):
        return {"a_jour": True}
    if systeme.WINDOWS:
        chemin = telecharger_installateur(info["setup"], info["version"])
        lancer_apres_fermeture(chemin)
    else:
        relancer_appimage(telecharger_appimage(info["appimage"], appimage))
    # La réponse part d'abord, puis Mes outils (bulle et serveur) se ferme
    # pour que l'installateur puisse remplacer le programme.
    threading.Timer(1.5, lambda: os._exit(0)).start()
    return {"installation": True, "version": info["version"]}


def choisir_dossier(d):
    """Ouvre la fenêtre « Choisir un dossier » du système, au premier plan.
    Renvoie {"chemin": "..."} ou {"chemin": None} si annulé."""
    try:
        chemin = systeme.choisir_dossier(str(d.get("titre") or "Choisir un dossier")[:120], str(d.get("depart") or ""))
    except RuntimeError as erreur:
        raise ValueError(str(erreur)) from None
    return {"chemin": chemin}


ROUTES = {
    "lire": lire,
    "enregistrer": enregistrer,
    "dossiers": dossiers,
    "raccourci": raccourci,
    "mise_a_jour": mise_a_jour,
    "installer_mise_a_jour": installer_mise_a_jour,
    "choisir_dossier": choisir_dossier,
}
