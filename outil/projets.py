# -*- coding: utf-8 -*-
"""Onglet « Projets » : les projets de développement de ce PC.

- Liste : les dossiers de projets (Réglages) et leurs sous-dossiers directs
  qui ressemblent à un projet (.git, package.json, manage.py, compose…), plus
  les projets ajoutés à la main ; type détecté (Node, Django, Odoo…).
- Commandes (serveurs de dev) : proposées d'après le projet, modifiables,
  démarrées sans fenêtre noire (cmd.exe /c sous Windows ; bash -c, ou sh -c,
  dans une nouvelle session sous Linux) ; la sortie va dans
  donnees\\journaux\\<projet>-<commande>.log. Arrêter tue l'arbre du seul
  processus que l'outil a lancé (PID + heure de création mémorisés : un PID
  réutilisé par un autre programme n'est jamais tué). Heure de création :
  GetProcessTimes sous Windows, champ 22 de /proc/<pid>/stat sous Linux.
- État Git : branche, fichiers modifiés, commits à envoyer / à récupérer
  (git status, sans réseau) ; « fetch » à la demande.
- Fichiers .env : sauvegarde dans le coffre chiffré (coffre.py), catégorie
  « env », et restauration.

Données : donnees\\projets.json (commandes, projets ajoutés, masqués, processus
lancés). Pour l'Accueil et la bulle : serveurs() et action_commande().
"""
import concurrent.futures
import hashlib
import json
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import uuid
import webbrowser

import config
import systeme

NOM = "projets"
# Drapeaux de Windows (0 ailleurs : subprocess refuse creationflags non nul hors Windows).
CREATE_NO_WINDOW = systeme.SANS_FENETRE
CREATE_NEW_PROCESS_GROUP = systeme.NOUVEAU_GROUPE
CREATE_NEW_CONSOLE = systeme.NOUVELLE_CONSOLE
DETACHED = systeme.DETACHE
LIGNES_JOURNAL = 300
MAX_COMMANDES = 20
TAILLE_ENV_MAX = 256 * 1024
FETCH_PARALLELE = 4
DELAI_FETCH = 60
DELAI_STATUS = 15

ID_PROJET = re.compile(r"^[0-9a-f]{10}$")
ID_COMMANDE = re.compile(r"^[a-z0-9-]{1,40}$")
NOM_SCRIPT = re.compile(r"^[A-Za-z0-9:_.@/-]{1,60}$")
FICHIER_ENV = re.compile(r"^\.env(\.[A-Za-z0-9_-]+)*$")
ENV_EXEMPLE = re.compile(r"\.(example|sample|template|dist|defaults?)$", re.I)
ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]|\x1b\][^\x07\x1b]*(\x07|\x1b\\)|\x1b[@-Z\\-_]")
IGNORES = {"node_modules", "venv", ".venv", "env", "__pycache__", "dist", "build", "vendor", "target"}

COMPOSE = ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml")
MARQUEURS = {".git", "package.json", "pyproject.toml", "requirements.txt", "manage.py", "setup.py", "Pipfile",
             "__manifest__.py", "odoo-bin", "composer.json", "pom.xml", "build.gradle", "build.gradle.kts",
             "go.mod", "Cargo.toml", "Gemfile", "pubspec.yaml", "Dockerfile", *COMPOSE}

ICONES = {"Odoo": "🧩", "Django": "🎸", "Python": "🐍", "React": "⚛️", "Vue": "💚", "Angular": "🅰️",
          "Next.js": "⚡", "Nuxt": "⚡", "Vite": "⚡", "NestJS": "🐈", "Tauri": "🖥️", "Electron": "🖥️",
          "Node": "📦", "Docker": "🐳", "Laravel": "🧱", "PHP": "🐘", "Java": "☕", "Go": "🐹", "Rust": "🦀",
          ".NET": "🔷", "Flutter": "🐦", "Ruby": "💎", "Git": "📁"}

_verrou = threading.RLock()
_popens = {}   # (projet_id, commande_id) → Popen (processus lancés depuis ce démarrage)
_fins = {}     # (projet_id, commande_id) → code de sortie du dernier lancement


class ErreurProjets(Exception):
    pass


# ---------------------------------------------------------------------------
# Données
# ---------------------------------------------------------------------------
def _donnees():
    d = config.lire_donnees(NOM, {})
    d = d if isinstance(d, dict) else {}
    for cle, defaut in (("ajoutes", []), ("masques", []), ("commandes", {}), ("lances", {})):
        if not isinstance(d.get(cle), type(defaut)):
            d[cle] = defaut
    return d


def _ecrire(d):
    config.ecrire_donnees(NOM, d)


def _norm(chemin):
    return os.path.normpath(str(chemin or "").strip().strip('"'))


def identifiant(chemin):
    """Identifiant stable d'un projet, tiré de son chemin."""
    return hashlib.sha1(os.path.normcase(_norm(chemin)).encode("utf-8")).hexdigest()[:10]


def _meme_chemin(a, b):
    return os.path.normcase(_norm(a)) == os.path.normcase(_norm(b))


# ---------------------------------------------------------------------------
# Détection
# ---------------------------------------------------------------------------
def _noms(dossier):
    try:
        with os.scandir(dossier) as entrees:
            return {e.name for e in entrees}
    except OSError:
        return set()


def _lire_json(chemin):
    try:
        if os.path.getsize(chemin) > 2 * 1024 * 1024:
            return {}
        with open(chemin, encoding="utf-8-sig") as f:
            valeur = json.load(f)
        return valeur if isinstance(valeur, dict) else {}
    except (OSError, ValueError):
        return {}


def _lire_texte(chemin, limite=512 * 1024):
    try:
        with open(chemin, encoding="utf-8", errors="replace") as f:
            return f.read(limite)
    except OSError:
        return ""


def _a_des_modules_odoo(dossier, noms):
    """Un dossier d'addons : des sous-dossiers avec __manifest__.py."""
    for n in sorted(noms)[:60]:
        if n.startswith(".") or n in IGNORES:
            continue
        if os.path.isfile(os.path.join(dossier, n, "__manifest__.py")):
            return True
    return False


def ressemble_a_un_projet(dossier, noms=None):
    noms = _noms(dossier) if noms is None else noms
    if noms & MARQUEURS or any(n.endswith((".sln", ".csproj")) for n in noms):
        return True
    return _a_des_modules_odoo(dossier, noms)


def detecter_types(dossier, noms=None):
    """Les technologies du projet, la principale d'abord."""
    noms = _noms(dossier) if noms is None else noms
    types = []

    def ajout(t):
        if t not in types:
            types.append(t)

    if "odoo-bin" in noms or "__manifest__.py" in noms or _a_des_modules_odoo(dossier, noms):
        ajout("Odoo")
    if "manage.py" in noms:
        ajout("Django")
    if "package.json" in noms:
        pj = _lire_json(os.path.join(dossier, "package.json"))
        deps = {**(pj.get("dependencies") or {}), **(pj.get("devDependencies") or {})} if pj else {}
        deps = deps if isinstance(deps, dict) else {}
        if "@nestjs/core" in deps:
            ajout("NestJS")
        if "next" in deps or any(n.startswith("next.config.") for n in noms):
            ajout("Next.js")
        if "nuxt" in deps or any(n.startswith("nuxt.config.") for n in noms):
            ajout("Nuxt")
        if "@angular/core" in deps or "angular.json" in noms:
            ajout("Angular")
        if "src-tauri" in noms or "@tauri-apps/api" in deps or "@tauri-apps/cli" in deps:
            ajout("Tauri")
        if "electron" in deps:
            ajout("Electron")
        if "react" in deps:
            ajout("React")
        if "vue" in deps:
            ajout("Vue")
        if "vite" in deps or any(n.startswith("vite.config.") for n in noms):
            ajout("Vite")
        ajout("Node")
    if noms & {"pyproject.toml", "requirements.txt", "setup.py", "Pipfile", "manage.py"}:
        ajout("Python")
    if "artisan" in noms:
        ajout("Laravel")
    if "composer.json" in noms:
        ajout("PHP")
    if noms & {"pom.xml", "build.gradle", "build.gradle.kts"}:
        ajout("Java")
    if "go.mod" in noms:
        ajout("Go")
    if "Cargo.toml" in noms:
        ajout("Rust")
    if any(n.endswith((".sln", ".csproj")) for n in noms):
        ajout(".NET")
    if "pubspec.yaml" in noms:
        ajout("Flutter")
    if "Gemfile" in noms:
        ajout("Ruby")
    if noms & set(COMPOSE) or "Dockerfile" in noms:
        ajout("Docker")
    if not types and ".git" in noms:
        ajout("Git")
    return types


def _python(dossier, noms):
    """Le Python du projet : son environnement virtuel s'il en a un."""
    for venv in (".venv", "venv", "env"):
        if not systeme.WINDOWS:
            if venv in noms and os.path.isfile(os.path.join(dossier, venv, "bin", "python")):
                return f"{venv}/bin/python"
        elif venv in noms and os.path.isfile(os.path.join(dossier, venv, "Scripts", "python.exe")):
            return f"{venv}\\Scripts\\python.exe"
    return "python" if systeme.WINDOWS else "python3"  # Ubuntu n'a pas de commande « python »


def _gestionnaire(noms):
    if "pnpm-lock.yaml" in noms:
        return "pnpm"
    if "yarn.lock" in noms:
        return "yarn"
    if "bun.lockb" in noms or "bun.lock" in noms:
        return "bun"
    return "npm"


def _port_script(nom, script):
    m = re.search(r"(?:--port[= ]|-p\s+|PORT=)(\d{2,5})\b", script)
    if m:
        return int(m.group(1))
    if nom not in ("dev", "start", "serve", "preview", "storybook", "develop") and not nom.startswith(("dev:", "start:", "serve:")):
        return None
    bas = script.lower()
    if "storybook" in bas:
        return 6006
    if "vite preview" in bas or (nom == "preview" and "vite" in bas):
        return 4173
    if "vite" in bas:
        return 5173
    if "ng serve" in bas or bas.strip() == "ng serve":
        return 4200
    if re.search(r"\b(next|nuxt|react-scripts|nest)\b", bas):
        return 3000
    return None


def _cmd(nom, commande, port=None):
    ident = re.sub(r"[^a-z0-9]+", "-", nom.lower()).strip("-")[:40] or "commande"
    return {"id": ident, "nom": nom, "commande": commande, "port": port,
            "url": f"http://localhost:{port}" if port else ""}


def commandes_proposees(dossier, noms=None):
    """Les commandes de dev devinées d'après les fichiers du projet. Les noms
    de scripts bizarres (caractères de commande) ne sont jamais proposés."""
    noms = _noms(dossier) if noms is None else noms
    proposees = []
    if "package.json" in noms:
        scripts = _lire_json(os.path.join(dossier, "package.json")).get("scripts") or {}
        scripts = scripts if isinstance(scripts, dict) else {}
        gest = _gestionnaire(noms)
        ordre = ["dev", "start", "serve", "preview", "storybook", "watch", "build", "test", "lint"]
        valides = [n for n in scripts if NOM_SCRIPT.match(n) and isinstance(scripts[n], str)
                   and not n.startswith(("pre", "post"))]
        valides.sort(key=lambda n: (ordre.index(n) if n in ordre else len(ordre), n))
        for n in valides[:12]:
            commande = f"yarn {n}" if gest == "yarn" else f"{gest} run {n}"
            proposees.append(_cmd(f"{gest} {n}", commande, _port_script(n, scripts[n])))
    py = _python(dossier, noms)
    if "manage.py" in noms:
        proposees.append(_cmd("Django", f"{py} manage.py runserver", 8000))
    elif noms & {"requirements.txt", "pyproject.toml"}:
        deps = (_lire_texte(os.path.join(dossier, "requirements.txt"))
                + _lire_texte(os.path.join(dossier, "pyproject.toml"))).lower()
        if "fastapi" in deps and ("main.py" in noms or os.path.isfile(os.path.join(dossier, "app", "main.py"))):
            appli = "main:app" if "main.py" in noms else "app.main:app"
            proposees.append(_cmd("FastAPI", f"{py} -m uvicorn {appli} --reload", 8000))
        elif "flask" in deps and "app.py" in noms:
            proposees.append(_cmd("Flask", f"{py} -m flask run", 5000))
    if "odoo-bin" in noms:
        confs = sorted(n for n in noms if n.endswith(".conf"))
        commande = f"{py} odoo-bin" + (f" -c {confs[0]}" if confs and " " not in confs[0] else "")
        proposees.append(_cmd("Odoo", commande, 8069))
    compose = next((n for n in COMPOSE if n in noms), None)
    if compose:
        m = re.search(r"-\s*[\"']?(?:\d+\.\d+\.\d+\.\d+:)?(\d{2,5}):\d+", _lire_texte(os.path.join(dossier, compose)))
        proposees.append(_cmd("Docker compose", "docker compose up", int(m.group(1)) if m else None))
    if "artisan" in noms:
        proposees.append(_cmd("Laravel", "php artisan serve", 8000))
    if "go.mod" in noms:
        proposees.append(_cmd("Go", "go run .", None))
    if "Cargo.toml" in noms and "src-tauri" not in noms:
        proposees.append(_cmd("Cargo", "cargo run", None))
    if "pom.xml" in noms:
        if systeme.WINDOWS:
            mvn = "mvnw.cmd" if "mvnw.cmd" in noms else "mvn"
        else:
            mvn = "./mvnw" if "mvnw" in noms else "mvn"
        spring = "spring-boot" in _lire_texte(os.path.join(dossier, "pom.xml"))
        proposees.append(_cmd("Maven", f"{mvn} spring-boot:run" if spring else f"{mvn} package", 8080 if spring else None))
    elif noms & {"build.gradle", "build.gradle.kts"}:
        if systeme.WINDOWS:
            gradle = "gradlew.bat" if "gradlew.bat" in noms else "gradle"
        else:
            gradle = "./gradlew" if "gradlew" in noms else "gradle"
        proposees.append(_cmd("Gradle", f"{gradle} bootRun", 8080))
    if any(n.endswith(".csproj") for n in noms):
        proposees.append(_cmd(".NET", "dotnet watch run", None))
    if "Gemfile" in noms and os.path.isfile(os.path.join(dossier, "bin", "rails")):
        proposees.append(_cmd("Rails", "ruby bin\\rails server" if systeme.WINDOWS else "ruby bin/rails server", 3000))
    # Identifiants uniques
    vus = set()
    for c in proposees:
        base, i = c["id"], 2
        while c["id"] in vus:
            c["id"] = f"{base}-{i}"
            i += 1
        vus.add(c["id"])
    return proposees


# ---------------------------------------------------------------------------
# Liste des projets
# ---------------------------------------------------------------------------
def _candidats():
    """(chemin, ajouté à la main) pour chaque projet trouvé, sans doublon."""
    d = _donnees()
    vus, resultat = set(), []

    def garder(chemin, manuel):
        cle = os.path.normcase(_norm(chemin))
        if cle not in vus:
            vus.add(cle)
            resultat.append((_norm(chemin), manuel))

    for racine in config.dossiers_projets():
        racine = _norm(racine)
        if not os.path.isdir(racine):
            continue
        if ressemble_a_un_projet(racine):
            garder(racine, False)
        try:
            with os.scandir(racine) as entrees:
                sous = sorted((e.path for e in entrees if not e.name.startswith((".", "$"))
                               and e.name not in IGNORES and _est_dossier(e)), key=str.lower)
        except OSError:
            sous = []
        for chemin in sous:
            if ressemble_a_un_projet(chemin):
                garder(chemin, False)
    for chemin in d["ajoutes"]:
        if isinstance(chemin, str) and os.path.isdir(chemin):
            garder(chemin, True)
    return resultat


def _est_dossier(entree):
    try:
        return entree.is_dir()
    except OSError:
        return False


def _commandes_projet(d, pid):
    bloc = d["commandes"].get(pid)
    return bloc.get("commandes", []) if isinstance(bloc, dict) else []


def _decrire(chemin, manuel, d):
    noms = _noms(chemin)
    types = detecter_types(chemin, noms)
    pid = identifiant(chemin)
    return {"id": pid, "nom": os.path.basename(chemin.rstrip("\\/")) or chemin, "chemin": chemin,
            "types": types, "icone": ICONES.get(types[0], "📁") if types else "📁",
            "git": ".git" in noms, "manuel": manuel,
            "masque": any(_meme_chemin(chemin, m) for m in d["masques"] if isinstance(m, str)),
            "env": bool(fichiers_env(chemin)),
            "commandes": [{**c, "etat": _etat_commande(d, pid, c)} for c in _commandes_projet(d, pid)],
            "proposees": commandes_proposees(chemin, noms)}


def lister(_d=None):
    d = _oublier_morts()
    projets = [_decrire(c, m, d) for c, m in _candidats()]
    projets.sort(key=lambda p: p["nom"].lower())
    if systeme.WINDOWS:
        terminal = "Windows Terminal" if shutil.which("wt") else "PowerShell"
    else:
        terminal = "Terminal"
    return {"projets": projets, "dossiers": config.dossiers_projets(), "vscode": _vscode_present(),
            "terminal": terminal}


def _projet(pid):
    """Le chemin d'un projet connu (jamais un chemin quelconque venu de la page)."""
    if not ID_PROJET.match(str(pid or "")):
        raise ErreurProjets("Projet inconnu.")
    d = _donnees()
    bloc = d["commandes"].get(pid)
    if isinstance(bloc, dict) and isinstance(bloc.get("chemin"), str) and identifiant(bloc["chemin"]) == pid \
            and os.path.isdir(bloc["chemin"]):
        return bloc["chemin"]
    for chemin, _ in _candidats():
        if identifiant(chemin) == pid:
            return chemin
    raise ErreurProjets("Projet introuvable : le dossier a peut-être été déplacé.")


def ajouter(d):
    chemin = _norm(d.get("chemin"))
    if not d.get("chemin") or not os.path.isdir(chemin):
        raise ErreurProjets("Dossier introuvable.")
    with _verrou:
        donnees = _donnees()
        if not any(_meme_chemin(chemin, a) for a in donnees["ajoutes"]):
            donnees["ajoutes"].append(chemin)
        donnees["masques"] = [m for m in donnees["masques"] if not _meme_chemin(chemin, m)]
        _ecrire(donnees)
    return {"id": identifiant(chemin), "chemin": chemin}


def retirer(d):
    """Retire un projet ajouté à la main (le dossier n'est pas touché)."""
    chemin = _projet(d.get("projet"))
    with _verrou:
        donnees = _donnees()
        donnees["ajoutes"] = [a for a in donnees["ajoutes"] if not _meme_chemin(chemin, a)]
        _ecrire(donnees)
    return {"ok": True}


def masquer(d):
    chemin = _projet(d.get("projet"))
    masque = bool(d.get("masque", True))
    with _verrou:
        donnees = _donnees()
        donnees["masques"] = [m for m in donnees["masques"] if not _meme_chemin(chemin, m)]
        if masque:
            donnees["masques"].append(chemin)
        _ecrire(donnees)
    return {"masque": masque}


# ---------------------------------------------------------------------------
# Ouvrir
# ---------------------------------------------------------------------------
def _vscode_present():
    try:
        import github
        return bool(github._vscode())
    except Exception:  # noqa: BLE001
        return False


def ouvrir_dossier(d):
    systeme.ouvrir(_projet(d.get("projet")))
    return {"ok": True}


def ouvrir_vscode(d):
    import github
    github.ouvrir_vscode(_projet(d.get("projet")))
    return {"ok": True}


def ouvrir_terminal(d):
    """Windows Terminal dans le dossier s'il est installé, sinon PowerShell.
    Linux : le terminal du bureau (systeme.ouvrir_terminal)."""
    chemin = _projet(d.get("projet"))
    if not systeme.WINDOWS:
        if not systeme.ouvrir_terminal(dossier=chemin):
            raise ErreurProjets("Aucun terminal trouvé sur ce PC (par exemple : sudo apt install gnome-terminal).")
        return {"ok": True}
    wt = shutil.which("wt")
    if wt and ";" not in chemin:  # « ; » sépare les commandes de wt
        subprocess.Popen([wt, "-d", chemin], creationflags=DETACHED, close_fds=True,
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.Popen(["powershell.exe", "-NoExit", "-NoLogo"], cwd=chemin, creationflags=CREATE_NEW_CONSOLE,
                         close_fds=True)
    return {"ok": True}


def _verifier_url(url):
    url = str(url or "").strip()
    if not re.match(r"^https?://[^\s\"'<>]+$", url, re.I):
        raise ErreurProjets("Adresse invalide : elle doit commencer par http:// ou https://.")
    return url


def ouvrir_site(d):
    pid, cid = d.get("projet"), d.get("commande")
    _, c = _commande(pid, cid)
    if not c.get("url"):
        raise ErreurProjets("Aucune adresse pour cette commande.")
    webbrowser.open(_verifier_url(c["url"]))
    return {"ok": True}


# ---------------------------------------------------------------------------
# Commandes : configuration
# ---------------------------------------------------------------------------
def _nettoyer_commande(c):
    if not isinstance(c, dict):
        raise ErreurProjets("Commande invalide.")
    nom = str(c.get("nom") or "").strip()[:60]
    commande = str(c.get("commande") or "").strip()
    if not nom:
        raise ErreurProjets("Donnez un nom à chaque commande.")
    if not commande or len(commande) > 500 or "\n" in commande or "\r" in commande:
        raise ErreurProjets(f"Commande invalide : {nom}")
    port = c.get("port")
    if port in ("", None):
        port = None
    else:
        try:
            port = int(port)
        except (TypeError, ValueError):
            port = 0
        if not 1 <= port <= 65535:
            raise ErreurProjets(f"Port invalide : {c.get('port')}")
    url = str(c.get("url") or "").strip()
    if url:
        url = _verifier_url(url)
    elif port:
        url = f"http://localhost:{port}"
    ident = str(c.get("id") or "")
    if not ID_COMMANDE.match(ident):
        ident = uuid.uuid4().hex[:8]
    return {"id": ident, "nom": nom, "commande": commande, "port": port, "url": url}


def enregistrer_commandes(d):
    """Remplace la liste des commandes d'un projet (saisies par l'utilisateur)."""
    pid = d.get("projet")
    chemin = _projet(pid)
    liste = d.get("commandes")
    if not isinstance(liste, list) or len(liste) > MAX_COMMANDES:
        raise ErreurProjets("Liste de commandes invalide.")
    propres, vus = [], set()
    for c in liste:
        c = _nettoyer_commande(c)
        while c["id"] in vus:
            c["id"] = uuid.uuid4().hex[:8]
        vus.add(c["id"])
        propres.append(c)
    with _verrou:
        donnees = _donnees()
        for cid in _commandes_lancees(donnees, pid):
            if cid not in vus:
                raise ErreurProjets("Arrêtez d'abord une commande en marche avant de la supprimer.")
        if propres:
            donnees["commandes"][pid] = {"chemin": chemin, "commandes": propres}
        else:
            donnees["commandes"].pop(pid, None)
        _ecrire(donnees)
    return {"commandes": [{**c, "etat": _etat_commande(_donnees(), pid, c)} for c in propres]}


def _commande(pid, cid):
    if not ID_PROJET.match(str(pid or "")) or not ID_COMMANDE.match(str(cid or "")):
        raise ErreurProjets("Commande inconnue.")
    d = _donnees()
    bloc = d["commandes"].get(pid)
    if not isinstance(bloc, dict):
        raise ErreurProjets("Commande inconnue.")
    c = next((x for x in bloc.get("commandes", []) if x.get("id") == cid), None)
    if not c:
        raise ErreurProjets("Commande inconnue.")
    return bloc.get("chemin"), c


def _commandes_lancees(d, pid):
    return [cle.split("/", 1)[1] for cle in d["lances"] if cle.startswith(pid + "/")]


# ---------------------------------------------------------------------------
# Processus
# ---------------------------------------------------------------------------
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
STILL_ACTIVE = 259
_k32_charge = None


def _kernel32():
    """kernel32 de Windows, préparé au premier appel (jamais sous Linux)."""
    global _k32_charge
    if _k32_charge is None:
        import ctypes  # noqa: PLC0415
        from ctypes import wintypes  # noqa: PLC0415
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        k32.OpenProcess.restype = wintypes.HANDLE
        k32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        k32.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
        k32.CloseHandle.argtypes = [wintypes.HANDLE]
        _k32_charge = (ctypes, wintypes, k32)
    return _k32_charge


def debut_stat_linux(texte):
    """Le champ 22 (starttime, en tops d'horloge depuis le démarrage) d'un
    contenu de /proc/<pid>/stat, ou None pour un zombie ou un texte illisible.
    Le nom (champ 2, entre parenthèses) peut contenir espaces et « ) » : on
    lit après la dernière parenthèse fermante (champ 3 = état)."""
    try:
        champs = (texte or "").rsplit(")", 1)[1].split()
        if champs[0] in ("Z", "X"):  # zombie ou mort : déjà terminé
            return None
        return int(champs[22 - 3])
    except (IndexError, ValueError):
        return None


def _lire_stat_linux(pid):
    try:
        with open(f"/proc/{int(pid)}/stat", encoding="utf-8", errors="replace") as f:
            return f.read()
    except (OSError, ValueError):
        return None


def heure_creation(pid):
    """L'heure de création d'un processus vivant (entier), ou None s'il est
    terminé. Sert à reconnaître « notre » processus : un PID peut resservir."""
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return None
    if pid <= 4:
        return None
    if not systeme.WINDOWS:
        return debut_stat_linux(_lire_stat_linux(pid))
    ctypes, wintypes, _k32 = _kernel32()
    h = _k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not h:
        return None
    try:
        code = wintypes.DWORD()
        if not _k32.GetExitCodeProcess(h, ctypes.byref(code)) or code.value != STILL_ACTIVE:
            return None
        temps = [wintypes.FILETIME() for _ in range(4)]
        if not _k32.GetProcessTimes(h, *[ctypes.byref(t) for t in temps]):
            return None
        return (temps[0].dwHighDateTime << 32) | temps[0].dwLowDateTime
    finally:
        _k32.CloseHandle(h)


def port_repond(port):
    """Vrai si quelque chose écoute sur ce port (IPv4 ou IPv6 local)."""
    if not port:
        return False
    for hote, famille in (("127.0.0.1", socket.AF_INET), ("::1", socket.AF_INET6)):
        try:
            with socket.socket(famille, socket.SOCK_STREAM) as s:
                s.settimeout(0.3)
                if s.connect_ex((hote, int(port))) == 0:
                    return True
        except OSError:
            pass
    return False


def _cle(pid, cid):
    return f"{pid}/{cid}"


def _lance_vivant(d, pid, cid):
    """L'entrée « lancé » si notre processus vit encore (même PID et même heure
    de création), sinon None."""
    info = d["lances"].get(_cle(pid, cid))
    if not isinstance(info, dict):
        return None
    if heure_creation(info.get("pid")) != info.get("cree"):
        return None
    return info


def _oublier_morts():
    """Retire les processus terminés de la liste (et note leur code de sortie)."""
    with _verrou:
        d = _donnees()
        morts = [cle for cle in d["lances"] if _lance_vivant(d, *cle.split("/", 1)) is None]
        for cle in morts:
            p = _popens.pop(tuple(cle.split("/", 1)), None)
            if p is not None:
                try:
                    _fins[tuple(cle.split("/", 1))] = p.wait(timeout=0.5)
                except subprocess.TimeoutExpired:
                    pass
            d["lances"].pop(cle, None)
        if morts:
            _ecrire(d)
        return d


def _etat_commande(d, pid, c):
    vivant = _lance_vivant(d, pid, c["id"])
    port = c.get("port")
    ecoute = port_repond(port) if port else False
    if vivant:
        etat = "marche" if (ecoute or not port) else "demarrage"
    else:
        etat = "occupe" if ecoute else "arrete"
    resultat = {"etat": etat}
    if vivant:
        resultat["depuis"] = vivant.get("debut")
    elif (pid, c["id"]) in _fins:
        resultat["code_sortie"] = _fins[(pid, c["id"])]
    return resultat


def chemin_journal(pid, cid, nom_projet=""):
    dossier = os.path.join(config.DONNEES, "journaux")
    base = re.sub(r"[^A-Za-z0-9_-]+", "-", nom_projet).strip("-")[:40]
    return os.path.join(dossier, f"{base + '-' if base else ''}{pid[:6]}-{cid}.log")


def _environnement():
    env = os.environ.copy()
    env.update(PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8", FORCE_COLOR="0", NO_COLOR="1",
               BROWSER="none", GIT_TERMINAL_PROMPT="0")
    return env


def _shell_linux():
    """bash s'il est là (source, &&, ~ : comme dans un terminal), sinon sh."""
    return shutil.which("bash") or "/bin/sh"


def _lancer(commande, chemin, sortie):
    """Lance la commande de l'utilisateur dans le dossier du projet, sortie
    vers le journal. Windows : cmd.exe /c, sans fenêtre, nouveau groupe.
    Linux : bash -c (ou sh -c) dans une nouvelle session (groupe = PID)."""
    if systeme.WINDOWS:
        ligne = f'cmd.exe /d /s /c "{commande}"'
        return subprocess.Popen(ligne, cwd=chemin, env=_environnement(), stdin=subprocess.DEVNULL,
                                stdout=sortie, stderr=subprocess.STDOUT,
                                creationflags=CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP)
    return subprocess.Popen([_shell_linux(), "-c", commande], cwd=chemin, env=_environnement(),
                            stdin=subprocess.DEVNULL, stdout=sortie, stderr=subprocess.STDOUT,
                            start_new_session=True, close_fds=True)


def demarrer(pid, cid):
    with _verrou:
        d = _oublier_morts()
        chemin, c = _commande(pid, cid)
        if not chemin or not os.path.isdir(chemin):
            raise ErreurProjets("Le dossier du projet est introuvable.")
        if _lance_vivant(d, pid, cid):
            raise ErreurProjets("Cette commande est déjà en marche.")
        if c.get("port") and port_repond(c["port"]):
            raise ErreurProjets(f"Le port {c['port']} est déjà utilisé par un autre programme.")
        journal = chemin_journal(pid, cid, os.path.basename(chemin.rstrip("\\/")))
        os.makedirs(os.path.dirname(journal), exist_ok=True)
        # La commande a été saisie (ou acceptée) par l'utilisateur dans SA
        # configuration : cmd /c (ou bash -c) l'exécute telle quelle, dans le
        # dossier du projet.
        with open(journal, "wb") as sortie:
            entete = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] > {c['commande']}\r\n"
            sortie.write(entete.encode("utf-8"))
            sortie.flush()
            try:
                p = _lancer(c["commande"], chemin, sortie)
            except OSError as e:
                raise ErreurProjets(f"Impossible de lancer la commande : {e}") from None
        cree = heure_creation(p.pid)
        if cree is None:  # déjà terminé
            _fins[(pid, cid)] = p.wait()
            return {"etat": "arrete", "code_sortie": _fins[(pid, cid)]}
        _popens[(pid, cid)] = p
        _fins.pop((pid, cid), None)
        d["lances"][_cle(pid, cid)] = {"pid": p.pid, "cree": cree, "debut": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                       "journal": journal}
        _ecrire(d)
        return {"etat": "demarrage" if c.get("port") else "marche", "pid": p.pid}


def _signal_groupe(groupe, sig):
    try:
        os.killpg(groupe, sig)
    except (ProcessLookupError, PermissionError, OSError):
        pass


def _tuer_arbre_linux(pid):
    """Linux : SIGTERM au groupe de la session lancée par l'outil, puis
    systeme.arreter_processus (descendants, SIGKILL si besoin), puis SIGKILL
    aux restes du groupe (enfants orphelins rattachés à init)."""
    try:
        groupe = pid if os.getpgid(pid) == pid else None  # start_new_session : groupe = PID
    except OSError:
        groupe = None
    if groupe:
        _signal_groupe(groupe, signal.SIGTERM)
    systeme.arreter_processus(pid, arbre=True, delai=5.0)
    if groupe:
        _signal_groupe(groupe, getattr(signal, "SIGKILL", 9))  # SIGKILL n'existe pas sous Windows


def _tuer_arbre(pid_processus, cree=None):
    """taskkill /T /F (ou, sous Linux, le groupe et les descendants),
    seulement pour un processus lancé par l'outil (présent dans la liste,
    même heure de création)."""
    with _verrou:
        d = _donnees()
        info = next((i for i in d["lances"].values() if isinstance(i, dict) and i.get("pid") == pid_processus), None)
        if not info or (cree is not None and info.get("cree") != cree) \
                or heure_creation(pid_processus) != info.get("cree"):
            raise ErreurProjets("Ce processus n'a pas été lancé par Mes outils : il n'est pas arrêté.")
        if not systeme.WINDOWS:
            _tuer_arbre_linux(int(pid_processus))
            return
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(int(pid_processus))], capture_output=True,
                       timeout=30, creationflags=CREATE_NO_WINDOW, stdin=subprocess.DEVNULL)


def arreter(pid, cid):
    with _verrou:
        _commande(pid, cid)
        d = _donnees()
        info = _lance_vivant(d, pid, cid)
        if not info:
            d["lances"].pop(_cle(pid, cid), None)
            _ecrire(d)
            raise ErreurProjets("Cette commande n'est pas en marche (ou n'a pas été lancée par Mes outils).")
        _tuer_arbre(info["pid"], info["cree"])
        p = _popens.pop((pid, cid), None)
        code = None
        if p is not None:
            try:
                code = p.wait(timeout=10)
            except subprocess.TimeoutExpired:
                pass
        else:
            for _ in range(40):
                if heure_creation(info["pid"]) != info["cree"]:
                    break
                time.sleep(0.25)
        _fins[(pid, cid)] = code
        d = _donnees()
        d["lances"].pop(_cle(pid, cid), None)
        _ecrire(d)
        try:
            with open(info["journal"], "ab") as f:
                f.write(f"\r\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Arrêté par Mes outils\r\n".encode("utf-8"))
        except OSError:
            pass
    return {"etat": "arrete"}


def _decoder(ligne, oem):
    try:
        return ligne.decode("utf-8")
    except UnicodeDecodeError:
        return ligne.decode(oem, errors="replace")


def lire_journal(pid, cid, lignes=LIGNES_JOURNAL):
    """Les dernières lignes de la sortie d'une commande (sans codes couleur)."""
    chemin, c = _commande(pid, cid)
    d = _donnees()
    info = d["lances"].get(_cle(pid, cid))
    fichier = info.get("journal") if isinstance(info, dict) else None
    if not fichier or not os.path.isfile(fichier):
        fichier = chemin_journal(pid, cid, os.path.basename((chemin or "").rstrip("\\/")))
    texte = []
    if os.path.isfile(fichier):
        with open(fichier, "rb") as f:
            f.seek(0, os.SEEK_END)
            taille = f.tell()
            f.seek(max(0, taille - 256 * 1024))
            brut = f.read()
        oem = systeme.encodage_console()
        morceaux = brut.replace(b"\r\n", b"\n").split(b"\n")
        if taille > 256 * 1024:
            morceaux = morceaux[1:]
        for m in morceaux:
            # Les barres de progression réécrivent la ligne avec « \r » : garder la dernière version.
            m = m.split(b"\r")[-1] if b"\r" in m.rstrip(b"\r") else m.rstrip(b"\r")
            texte.append(ANSI.sub("", _decoder(m, oem)))
        while texte and not texte[-1].strip():
            texte.pop()
    return {"lignes": texte[-lignes:], "fichier": fichier, **_etat_commande(d, pid, c)}


# ---------------------------------------------------------------------------
# Pour l'Accueil et la bulle
# ---------------------------------------------------------------------------
def serveurs():
    """Toutes les commandes configurées : [{projet, projet_id, id, nom, port,
    url, etat}]."""
    d = _oublier_morts()
    resultat = []
    for pid, bloc in d["commandes"].items():
        if not isinstance(bloc, dict):
            continue
        nom_projet = os.path.basename(str(bloc.get("chemin") or "").rstrip("\\/"))
        for c in bloc.get("commandes", []):
            resultat.append({"projet": nom_projet, "projet_id": pid, "id": c["id"], "nom": c["nom"],
                             "port": c.get("port"), "url": c.get("url") or "",
                             "etat": _etat_commande(d, pid, c)["etat"]})
    resultat.sort(key=lambda s: (s["projet"].lower(), s["nom"].lower()))
    return resultat


def action_commande(projet_id, commande_id, action):
    """demarrer, arreter, redemarrer ou ouvrir (le site) une commande."""
    if action == "demarrer":
        return demarrer(projet_id, commande_id)
    if action == "arreter":
        return arreter(projet_id, commande_id)
    if action == "redemarrer":
        if _lance_vivant(_donnees(), projet_id, commande_id):
            arreter(projet_id, commande_id)
        return demarrer(projet_id, commande_id)
    if action == "ouvrir":
        return ouvrir_site({"projet": projet_id, "commande": commande_id})
    raise ErreurProjets("Action inconnue.")


def _route_commande(d):
    return action_commande(d.get("projet"), d.get("commande"), d.get("action"))


def etats(_d=None):
    """États de toutes les commandes (rafraîchissement de la page)."""
    return {"serveurs": serveurs()}


# ---------------------------------------------------------------------------
# Git
# ---------------------------------------------------------------------------
def _env_git():
    env = os.environ.copy()
    env.update(GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never", LC_ALL="C", LANG="C")
    env.setdefault("GIT_SSH_COMMAND", "ssh -o BatchMode=yes -o ConnectTimeout=15")
    return env


def _git(args, dossier, delai):
    return subprocess.run(["git", "-c", "core.quotepath=false", *args], cwd=dossier, env=_env_git(),
                          stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=delai, **systeme.options_sans_fenetre())


def analyser_status(sortie):
    """Lit « git status --porcelain=v2 --branch »."""
    r = {"branche": None, "amont": None, "avance": 0, "retard": 0, "modifies": 0, "non_suivis": 0,
         "conflits": 0, "sans_commit": False}
    for ligne in (sortie or "").splitlines():
        if ligne.startswith("# branch.head "):
            r["branche"] = ligne[len("# branch.head "):].strip()
        elif ligne.startswith("# branch.oid ") and ligne.endswith("(initial)"):
            r["sans_commit"] = True
        elif ligne.startswith("# branch.upstream "):
            r["amont"] = ligne[len("# branch.upstream "):].strip()
        elif ligne.startswith("# branch.ab "):
            m = re.match(r"# branch\.ab \+(\d+) -(\d+)", ligne)
            if m:
                r["avance"], r["retard"] = int(m.group(1)), int(m.group(2))
        elif ligne.startswith(("1 ", "2 ")):
            r["modifies"] += 1
        elif ligne.startswith("u "):
            r["conflits"] += 1
        elif ligne.startswith("? "):
            r["non_suivis"] += 1
    if r["branche"] == "(detached)":
        r["branche"] = None
        r["detache"] = True
    return r


def etat_git(chemin):
    try:
        p = _git(["--no-optional-locks", "status", "--porcelain=v2", "--branch"], chemin, DELAI_STATUS)
    except FileNotFoundError:
        return {"erreur": "Git n'est pas installé sur ce PC."}
    except subprocess.TimeoutExpired:
        return {"erreur": "Git met trop de temps à répondre."}
    if p.returncode != 0:
        lignes = [x for x in (p.stderr or "").splitlines() if x.strip()]
        return {"erreur": lignes[-1] if lignes else "git a échoué."}
    return analyser_status(p.stdout)


def recuperer(chemin):
    """git fetch (sans fenêtre, sans demande de mot de passe), puis l'état."""
    try:
        p = _git(["fetch", "--prune", "--quiet"], chemin, DELAI_FETCH)
    except FileNotFoundError:
        return {"erreur": "Git n'est pas installé sur ce PC."}
    except subprocess.TimeoutExpired:
        return {**etat_git(chemin), "erreur_fetch": "Le serveur Git ne répond pas (délai dépassé)."}
    etat = etat_git(chemin)
    if p.returncode != 0:
        bas = (p.stderr or "").lower()
        if "could not resolve host" in bas or "unable to access" in bas or "could not read from remote" in bas:
            message = "Serveur Git injoignable ou accès refusé."
        elif "authentication" in bas or "permission denied" in bas or "terminal prompts disabled" in bas:
            message = "Accès refusé : connectez-vous une fois avec git dans un terminal."
        else:
            lignes = [x for x in (p.stderr or "").splitlines() if x.strip()]
            message = lignes[-1] if lignes else "git fetch a échoué."
        etat["erreur_fetch"] = message
    etat["verifie"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    return etat


def _projets_git():
    return [c for c, _ in _candidats() if os.path.isdir(os.path.join(c, ".git"))]


def etats_git(_d=None):
    """État Git de tous les projets git (en parallèle, sans réseau)."""
    chemins = _projets_git()
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        resultats = list(ex.map(etat_git, chemins))
    return {"git": {identifiant(c): r for c, r in zip(chemins, resultats)}}


def git_fetch(d):
    chemin = _projet(d.get("projet"))
    if not os.path.isdir(os.path.join(chemin, ".git")):
        raise ErreurProjets("Ce projet n'est pas un dépôt Git.")
    return {"git": recuperer(chemin)}


def tout_verifier(_d=None):
    """git fetch de tous les projets (4 à la fois), puis leur état."""
    chemins = _projets_git()
    with concurrent.futures.ThreadPoolExecutor(max_workers=FETCH_PARALLELE) as ex:
        resultats = list(ex.map(recuperer, chemins))
    return {"git": {identifiant(c): r for c, r in zip(chemins, resultats)},
            "erreurs": sum(1 for r in resultats if r.get("erreur_fetch") or r.get("erreur"))}


# ---------------------------------------------------------------------------
# Fichiers .env ↔ coffre chiffré
# ---------------------------------------------------------------------------
_coffre_local = None


def _le_coffre():
    """Le coffre déjà ouvert dans l'onglet Mots de passe (partagé)."""
    import coffre
    return coffre.partage()


def _coffre_ouvert():
    c = _le_coffre()
    if not c.ouvert():
        raise ErreurProjets("Ouvrez d'abord le coffre dans l'onglet Mots de passe.")
    return c


def fichiers_env(chemin):
    """Les fichiers .env du projet (racine et sous-dossiers directs), en
    chemins relatifs avec « / ». Les modèles (.env.example…) sont ignorés."""
    trouves = []
    for n in sorted(_noms(chemin)):
        complet = os.path.join(chemin, n)
        if FICHIER_ENV.match(n) and not ENV_EXEMPLE.search(n) and os.path.isfile(complet):
            trouves.append(n)
        elif not n.startswith(".") and n not in IGNORES and os.path.isdir(complet):
            for s in sorted(_noms(complet)):
                if FICHIER_ENV.match(s) and not ENV_EXEMPLE.search(s) and os.path.isfile(os.path.join(complet, s)):
                    trouves.append(f"{n}/{s}")
    return trouves


def _chemin_env(projet, relatif):
    """Le fichier .env visé, forcément dans le projet."""
    relatif = str(relatif or "").replace("\\", "/")
    morceaux = relatif.split("/")
    if not 1 <= len(morceaux) <= 2 or not FICHIER_ENV.match(morceaux[-1]) \
            or any(m in ("", ".", "..") for m in morceaux) or ":" in relatif:
        raise ErreurProjets("Fichier .env invalide.")
    complet = os.path.normpath(os.path.join(projet, *morceaux))
    if os.path.normcase(os.path.dirname(complet)) not in (os.path.normcase(projet),
                                                          os.path.normcase(os.path.join(projet, morceaux[0]))):
        raise ErreurProjets("Fichier .env invalide.")
    return complet, "/".join(morceaux)


def _entrees_env(c, projet):
    return [e for e in c.lister() if e.get("categorie") == "env" and _meme_chemin(e.get("site", ""), projet)]


def env_liste(d):
    projet = _projet(d.get("projet"))
    c = _le_coffre()
    ouvert = c.ouvert()
    sauvegardes = {e.get("identifiant"): e for e in _entrees_env(c, projet)} if ouvert else {}
    fichiers = []
    for rel in sorted(set(fichiers_env(projet)) | set(sauvegardes)):
        complet = os.path.join(projet, *rel.split("/"))
        e = sauvegardes.get(rel)
        fichiers.append({"fichier": rel, "existe": os.path.isfile(complet),
                         "sauvegarde": e.get("modifie") if e else None})
    return {"fichiers": fichiers, "coffre": {"existe": c.existe(), "ouvert": ouvert}}


def env_sauvegarder(d):
    """Range le contenu des fichiers .env dans le coffre (un par entrée)."""
    projet = _projet(d.get("projet"))
    c = _coffre_ouvert()
    voulus = [d["fichier"]] if d.get("fichier") else fichiers_env(projet)
    if not voulus:
        raise ErreurProjets("Aucun fichier .env dans ce projet.")
    existantes = {e.get("identifiant"): e for e in _entrees_env(c, projet)}
    nom = os.path.basename(projet.rstrip("\\/"))
    faits = []
    for rel in voulus:
        complet, rel = _chemin_env(projet, rel)
        if not os.path.isfile(complet):
            raise ErreurProjets(f"Fichier introuvable : {rel}")
        if os.path.getsize(complet) > TAILLE_ENV_MAX:
            raise ErreurProjets(f"Fichier trop gros pour le coffre : {rel}")
        with open(complet, "rb") as f:
            try:
                contenu = f.read().decode("utf-8")
            except UnicodeDecodeError:
                raise ErreurProjets(f"Fichier illisible (pas en UTF-8) : {rel}") from None
        entree = {"titre": f"{nom} · {rel}", "site": projet, "identifiant": rel, "categorie": "env",
                  "note": contenu, "mot_de_passe": ""}
        if rel in existantes:
            entree["id"] = existantes[rel]["id"]
        c.enregistrer(entree)
        faits.append(rel)
    return {"sauvegardes": faits}


def env_restaurer(d):
    """Réécrit un fichier .env depuis le coffre (copie .bak de l'ancien)."""
    projet = _projet(d.get("projet"))
    c = _coffre_ouvert()
    complet, rel = _chemin_env(projet, d.get("fichier"))
    e = next((x for x in _entrees_env(c, projet) if x.get("identifiant") == rel), None)
    if not e:
        raise ErreurProjets(f"Aucune sauvegarde de {rel} dans le coffre.")
    contenu = c.reveler(e["id"], "note")
    if not os.path.isdir(os.path.dirname(complet)):
        raise ErreurProjets("Le dossier de ce fichier n'existe plus.")
    if os.path.exists(complet):
        shutil.copyfile(complet, complet + ".bak")
    tmp = complet + ".tmp"
    with open(tmp, "wb") as f:
        f.write(contenu.encode("utf-8"))
    os.replace(tmp, complet)
    return {"restaure": rel, "bak": os.path.exists(complet + ".bak")}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
ROUTES = {
    "liste": lister,
    "ajouter": ajouter,
    "retirer": retirer,
    "masquer": masquer,
    "ouvrir/dossier": ouvrir_dossier,
    "ouvrir/vscode": ouvrir_vscode,
    "ouvrir/terminal": ouvrir_terminal,
    "ouvrir/site": ouvrir_site,
    "commandes/enregistrer": enregistrer_commandes,
    "commande": _route_commande,
    "journal": lambda d: lire_journal(d.get("projet"), d.get("commande")),
    "etats": etats,
    "git/etats": etats_git,
    "git/fetch": git_fetch,
    "git/tout_verifier": tout_verifier,
    "env/liste": env_liste,
    "env/sauvegarder": env_sauvegarder,
    "env/restaurer": env_restaurer,
}
