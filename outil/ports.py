# -*- coding: utf-8 -*-
"""Onglet « Ports » : quels programmes écoutent sur quels ports, et arrêt
d'un programme qui occupe un port.

Sans dépendance externe. Sous Windows :
- netstat -ano : les ports en écoute (TCP LISTENING, UDP en option) et le PID ;
- tasklist /fo csv /nh : le nom du programme et sa mémoire ;
- PowerShell Get-CimInstance Win32_Process : la ligne de commande (en
  parallèle de tasklist, gardée en mémoire tant que le PID garde le même nom).

Sous Linux :
- ss -H -ltnp (et -lunp pour UDP) : les ports en écoute et le PID ;
- /proc/<pid>/comm, status et cmdline : nom, mémoire et ligne de commande.
  Sans droits root, ss ne donne pas le PID des programmes des autres
  utilisateurs (services du système) : ils sont listés sans PID
  (« pid_inconnu »), et protégés.

L'arrêt (taskkill, ou systeme.arreter_processus sous Linux) refuse les
processus système, « Mes outils » lui-même et un PID qui ne correspond plus
au programme affiché dans la page.

Fonction utile aux autres modules : qui_ecoute(port) → dict ou None.
"""
import csv
import io
import json
import os
import re
import subprocess
import threading
import time
import webbrowser
from concurrent.futures import ThreadPoolExecutor

import systeme

SANS_FENETRE = systeme.SANS_FENETRE  # 0 hors de Windows
DUREE_CACHE = 2.0  # secondes

# Ports de développement courants : surlignés dans la page.
PORTS_DEV = {
    80: "HTTP", 443: "HTTPS", 1433: "SQL Server", 3000: "Node / React", 3001: "Node", 3306: "MySQL",
    4200: "Angular", 5000: "Flask", 5173: "Vite", 5174: "Vite", 5432: "PostgreSQL", 5672: "RabbitMQ",
    6379: "Redis", 8000: "Django / Python", 8069: "Odoo", 8072: "Odoo (longpolling)", 8080: "HTTP",
    8081: "HTTP", 8443: "HTTPS", 8888: "Jupyter", 9000: "PHP / Portainer", 9200: "Elasticsearch",
    11434: "Ollama", 27017: "MongoDB",
}
# Ports qui ne servent pas de pages web (bases de données, files…).
PORTS_NON_WEB = {135, 139, 445, 1433, 1521, 3306, 3389, 5432, 5672, 6379, 9200, 11211, 27017}
PORTS_WEB = {80, 443, 3000, 3001, 4200, 5000, 5173, 5174, 8000, 8069, 8080, 8081, 8443, 8888, 9000}
PROGRAMMES_WEB = {"node", "python", "pythonw", "php", "java", "ruby", "nginx", "httpd", "deno", "bun",
                  "dotnet", "go", "uvicorn", "gunicorn", "caddy", "code", "ollama"}

# Processus que l'on n'arrête jamais (Windows en a besoin pour tenir debout).
PROTEGES = {
    "system", "system idle process", "idle", "registry", "memory compression", "secure system",
    "smss", "csrss", "wininit", "winlogon", "services", "lsass", "lsaiso", "svchost", "explorer",
    "dwm", "msmpeng", "nissrv", "securityhealthservice", "sgrmbroker", "fontdrvhost", "spoolsv",
    "sihost", "taskhostw", "searchindexer", "wudfhost", "audiodg", "ctfmon", "conhost",
}
PID_PROTEGES = {0, 4}

# Linux : le système, la session graphique, le son, l'accès à distance.
# Noms exacts (comm, en minuscules) et débuts de noms.
PROTEGES_LINUX = {
    "init", "systemd", "kthreadd", "xwayland", "xorg", "gnome-shell", "gdm", "gdm3", "dbus-daemon",
    "dbus-broker", "pipewire", "pipewire-pulse", "wireplumber", "pulseaudio", "networkmanager", "polkitd",
    "udisksd", "accounts-daemon", "upowerd", "sshd", "login", "agetty", "snapd", "cron", "rsyslogd",
    "avahi-daemon", "mes-outils", "mes outils",
}
PREFIXES_PROTEGES_LINUX = ("systemd", "dbus", "pipewire", "gnome-session", "gdm-", "kworker", "ksoftirqd")
PID_ROOT_PROTEGES = 300  # Linux : un PID plus petit appartenant à root est un service du démarrage
NOM_INCONNU = "Autre utilisateur"

_verrou = threading.Lock()
_cache = {"udp": None, "instant": 0.0, "resultat": None}
_commandes = {}  # pid → (nom, ligne de commande)


def _executer(commande, delai=15):
    """Lance un programme sans fenêtre et rend sa sortie (texte)."""
    r = subprocess.run(commande, capture_output=True, timeout=delai, **systeme.options_sans_fenetre())
    sortie = r.stdout or b""
    if isinstance(sortie, str):
        return sortie
    return sortie.decode("oem" if systeme.WINDOWS else "utf-8", errors="replace")


def nom_court(nom):
    """« Python.EXE » → « python » (pour comparer et protéger)."""
    nom = (nom or "").strip().lower()
    return nom[:-4] if nom.endswith(".exe") else nom


def est_protege_linux(pid, nom, uid=None):
    """Vrai pour un processus Linux à ne jamais arrêter : PID inconnu ou 1,
    système, session graphique, son, ou petit PID appartenant à root."""
    if pid is None:
        return True
    court = nom_court(nom)
    if pid in (0, 1) or court in PROTEGES_LINUX or court.startswith(PREFIXES_PROTEGES_LINUX):
        return True
    return uid == 0 and pid < PID_ROOT_PROTEGES


# ---------------------------------------------------------------------------
# Lecture des sorties de netstat et tasklist
# ---------------------------------------------------------------------------
def separer_adresse(texte):
    """« 0.0.0.0:3000 » → ("0.0.0.0", 3000) ; « [::1]:5432 » → ("::1", 5432)."""
    texte = texte.strip()
    if ":" not in texte:
        return None, None
    hote, _, port = texte.rpartition(":")
    if "%" in hote:  # fe80::1%12, [fe80::1]%enp0s3 ou 127.0.0.53%lo : l'interface n'intéresse personne
        hote = hote.split("%", 1)[0]
    hote = hote.strip("[]")
    try:
        return hote, int(port)
    except ValueError:
        return hote, None


def lire_netstat(sortie, udp=False):
    """Les ports en écoute d'une sortie « netstat -ano ».
    TCP : état LISTENING (ou adresse distante 0.0.0.0:0 / [::]:0, quelle que
    soit la langue de Windows). UDP : seulement si udp=True."""
    vus, resultat = set(), []
    for ligne in sortie.splitlines():
        morceaux = ligne.split()
        if len(morceaux) < 4:
            continue
        proto = morceaux[0].upper()
        if proto == "TCP" and len(morceaux) >= 5:
            distante, etat, pid = morceaux[2], morceaux[3], morceaux[4]
            if etat.upper() != "LISTENING" and distante not in ("0.0.0.0:0", "[::]:0"):
                continue
        elif proto == "UDP" and udp:
            pid = morceaux[-1]
        else:
            continue
        hote, port = separer_adresse(morceaux[1])
        if port is None or not pid.isdigit():
            continue
        cle = (proto, hote, port, int(pid))
        if cle in vus:
            continue
        vus.add(cle)
        resultat.append({"proto": proto, "adresse": hote, "port": port, "pid": int(pid)})
    return resultat


RE_PROCESSUS_SS = re.compile(r'\("((?:[^"\\]|\\.)*)",pid=(\d+)')


def lire_ss(sortie, proto="TCP"):
    """Les ports en écoute d'une sortie « ss -H -ltnp » (ou -lunp, proto="UDP").
    Le champ users:(("nom",pid=…,fd=…),…) manque pour les programmes des autres
    utilisateurs : pid et nom valent alors None. Plusieurs processus sur la
    même socket (un serveur et ses ouvriers) : le plus petit PID est gardé."""
    vus, resultat = set(), []
    for ligne in (sortie or "").splitlines():
        debut = ligne.find("users:(")
        colonnes = (ligne[:debut] if debut >= 0 else ligne).split()
        proto_ligne = proto.upper()
        if colonnes and colonnes[0].lower() in ("tcp", "udp"):  # colonne Netid (-t et -u ensemble)
            proto_ligne, colonnes = colonnes[0].upper(), colonnes[1:]
        if len(colonnes) < 5 or colonnes[0].upper() not in ("LISTEN", "UNCONN"):
            continue
        hote, port = separer_adresse(colonnes[3])
        if port is None:
            continue
        trouves = [(n, int(p)) for n, p in RE_PROCESSUS_SS.findall(ligne[debut:])] if debut >= 0 else []
        nom, pid = min(trouves, key=lambda x: x[1]) if trouves else (None, None)
        cle = (proto_ligne, hote, port, pid)
        if cle in vus:
            continue
        vus.add(cle)
        resultat.append({"proto": proto_ligne, "adresse": hote, "port": port, "pid": pid, "nom_ss": nom})
    return resultat


def lire_status_linux(texte):
    """(mémoire en Ko, uid réel) depuis le contenu de /proc/<pid>/status."""
    memoire, uid = None, None
    for ligne in (texte or "").splitlines():
        if ligne.startswith("VmRSS:"):
            chiffres = re.sub(r"\D", "", ligne)
            memoire = int(chiffres) if chiffres else None
        elif ligne.startswith("Uid:"):
            morceaux = ligne.split()
            if len(morceaux) > 1 and morceaux[1].isdigit():
                uid = int(morceaux[1])
    return memoire, uid


def lire_tasklist(sortie):
    """{pid: {"nom", "memoire_ko"}} depuis « tasklist /fo csv /nh »."""
    processus = {}
    for ligne in csv.reader(io.StringIO(sortie)):
        if len(ligne) < 5 or not ligne[1].strip().isdigit():
            continue
        chiffres = re.sub(r"\D", "", ligne[4])
        processus[int(ligne[1])] = {"nom": ligne[0].strip(), "memoire_ko": int(chiffres) if chiffres else None}
    return processus


def lire_commandes(sortie):
    """{pid: ligne de commande} depuis le JSON de Get-CimInstance."""
    try:
        donnees = json.loads(sortie or "null")
    except ValueError:
        return {}
    if isinstance(donnees, dict):
        donnees = [donnees]
    resultat = {}
    for p in donnees or []:
        if isinstance(p, dict) and isinstance(p.get("ProcessId"), int):
            resultat[p["ProcessId"]] = p.get("CommandLine") or ""
    return resultat


# ---------------------------------------------------------------------------
# Programmes externes
# ---------------------------------------------------------------------------
def _lire_proc(pid, fichier):
    """Le contenu de /proc/<pid>/<fichier> (Linux), ou None."""
    try:
        with open(f"/proc/{int(pid)}/{fichier}", "rb") as f:
            return f.read(256 * 1024).decode("utf-8", errors="replace")
    except (OSError, ValueError):
        return None


def info_linux(pid):
    """{"nom", "memoire_ko", "commande", "uid"} d'un processus Linux, ou None
    s'il n'existe plus."""
    nom = _lire_proc(pid, "comm")
    if nom is None:
        return None
    memoire, uid = lire_status_linux(_lire_proc(pid, "status"))
    commande = (_lire_proc(pid, "cmdline") or "").replace("\0", " ").strip()
    return {"nom": nom.strip(), "memoire_ko": memoire, "commande": commande, "uid": uid}


def processus():
    return lire_tasklist(_executer(["tasklist", "/fo", "csv", "/nh"]))


def processus_pid(pid):
    """Le processus « pid » tel qu'il est maintenant, ou None."""
    if not systeme.WINDOWS:
        return info_linux(pid)
    sortie = _executer(["tasklist", "/fo", "csv", "/nh", "/fi", f"PID eq {int(pid)}"], delai=10)
    return lire_tasklist(sortie).get(int(pid))


def commandes(pids):
    """Les lignes de commande des PID demandés (un seul appel à PowerShell)."""
    pids = sorted({int(p) for p in pids if int(p) not in PID_PROTEGES})
    if not pids:
        return {}
    filtre = " OR ".join(f"ProcessId={p}" for p in pids)
    script = ("[Console]::OutputEncoding=[Text.Encoding]::UTF8; "
              f"Get-CimInstance Win32_Process -Filter '{filtre}' | "
              "Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress")
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
                           capture_output=True, timeout=10, **systeme.options_sans_fenetre())
    except (OSError, subprocess.SubprocessError):
        return {}
    return lire_commandes((r.stdout or b"").decode("utf-8", errors="replace"))


# ---------------------------------------------------------------------------
# Liste
# ---------------------------------------------------------------------------
def est_web(port, nom):
    if port in PORTS_NON_WEB:
        return False
    court = nom_court(nom)
    if not systeme.WINDOWS:  # python3.12, php-fpm8.3 → python, php
        court = re.sub(r"(-fpm)?[\d.]*$", "", court)
    return port in PORTS_WEB or (port >= 1024 and court in PROGRAMMES_WEB)


def nos_pids():
    """Les PID de « Mes outils » : ce serveur et le programme qui l'a lancé."""
    return {os.getpid(), os.getppid()}


def lister_ports(udp=False, forcer=False):
    """Les ports en écoute, avec le programme qui les occupe (cache court)."""
    with _verrou:
        if (not forcer and _cache["resultat"] is not None and _cache["udp"] == udp
                and time.monotonic() - _cache["instant"] < DUREE_CACHE):
            return _cache["resultat"]
    if not systeme.WINDOWS:
        return _lister_linux(udp)
    ecoutes = lire_netstat(_executer(["netstat", "-ano"]), udp=udp)
    pids = {e["pid"] for e in ecoutes}
    manquants = {p for p in pids if p not in _commandes}
    with ThreadPoolExecutor(max_workers=2) as pool:
        f_proc = pool.submit(processus)
        f_cmd = pool.submit(commandes, manquants) if manquants else None
        procs = f_proc.result()
        nouvelles = f_cmd.result() if f_cmd else {}
    nous = nos_pids()
    with _verrou:
        for pid, cmd in nouvelles.items():
            if pid in procs:
                _commandes[pid] = (procs[pid]["nom"], cmd)
        resultat = []
        for e in ecoutes:
            p = procs.get(e["pid"]) or {}
            nom = p.get("nom") or ("System" if e["pid"] == 4 else "?")
            memo = _commandes.get(e["pid"])
            commande = memo[1] if memo and memo[0] == nom else ""
            resultat.append({
                **e, "nom": nom, "memoire_ko": p.get("memoire_ko"), "commande": commande,
                "dev": PORTS_DEV.get(e["port"], ""), "web": e["proto"] == "TCP" and est_web(e["port"], nom),
                "protege": e["pid"] in PID_PROTEGES or nom_court(nom) in PROTEGES,
                "soi": e["pid"] in nous,
            })
        resultat.sort(key=lambda x: (x["port"], x["proto"], x["adresse"]))
        # Les PID disparus sont oubliés.
        for pid in [p for p in _commandes if p not in procs]:
            del _commandes[pid]
        _cache.update(udp=udp, instant=time.monotonic(), resultat=resultat)
        return resultat


def _ss(options):
    try:
        return _executer(["ss", "-H", options])
    except FileNotFoundError:
        raise ValueError("La commande ss est introuvable : installez le paquet iproute2.") from None


def _lister_linux(udp):
    """lister_ports sous Linux : ss, puis /proc pour chaque PID."""
    ecoutes = lire_ss(_ss("-ltnp"), "TCP")
    if udp:
        ecoutes += lire_ss(_ss("-lunp"), "UDP")
    infos = {pid: info_linux(pid) for pid in {e["pid"] for e in ecoutes if e["pid"] is not None}}
    nous = nos_pids()
    resultat = []
    for e in ecoutes:
        e = dict(e)
        nom_ss = e.pop("nom_ss", None)
        info = infos.get(e["pid"]) or {}
        inconnu = e["pid"] is None
        nom = NOM_INCONNU if inconnu else (info.get("nom") or nom_ss or "?")
        resultat.append({
            **e, "nom": nom, "memoire_ko": info.get("memoire_ko"), "commande": info.get("commande") or "",
            "dev": PORTS_DEV.get(e["port"], ""),
            "web": e["proto"] == "TCP" and est_web(e["port"], "" if inconnu else nom),
            "protege": est_protege_linux(e["pid"], nom, info.get("uid")),
            "soi": e["pid"] in nous, "pid_inconnu": inconnu,
        })
    resultat.sort(key=lambda x: (x["port"], x["proto"], x["adresse"]))
    with _verrou:
        _cache.update(udp=udp, instant=time.monotonic(), resultat=resultat)
    return resultat


def oublier_cache():
    with _verrou:
        _cache["resultat"] = None


def qui_ecoute(port):
    """Le programme qui écoute sur ce port TCP (dict), ou None.
    Ex. qui_ecoute(3000) → {"port": 3000, "pid": 1234, "nom": "node.exe", …}."""
    try:
        port = int(port)
    except (TypeError, ValueError):
        return None
    trouves = [e for e in lister_ports(udp=False) if e["port"] == port and e["proto"] == "TCP"]
    return dict(trouves[0]) if trouves else None


# ---------------------------------------------------------------------------
# Parenté des processus (pour ne pas arrêter l'arbre qui contient Mes outils)
# ---------------------------------------------------------------------------
_structure_entree = None


def _classe_entree():
    """La structure PROCESSENTRY32W de Windows (créée au premier appel :
    ctypes n'est pas chargé sous Linux)."""
    global _structure_entree
    if _structure_entree is None:
        import ctypes  # noqa: PLC0415
        from ctypes import wintypes  # noqa: PLC0415

        class _Entree(ctypes.Structure):
            _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD),
                        ("th32ProcessID", wintypes.DWORD), ("th32DefaultHeapID", ctypes.c_size_t),
                        ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
                        ("th32ParentProcessID", wintypes.DWORD), ("pcPriClassBase", ctypes.c_long),
                        ("dwFlags", wintypes.DWORD), ("szExeFile", ctypes.c_wchar * 260)]
        _structure_entree = _Entree
    return _structure_entree


def parents_linux():
    """{pid: pid du parent} d'après /proc/<pid>/stat (Linux)."""
    resultat = {}
    for nom in os.listdir("/proc"):
        if not nom.isdigit():
            continue
        texte = _lire_proc(nom, "stat")
        try:  # le nom (entre parenthèses) peut contenir des espaces : lire après la dernière « ) »
            resultat[int(nom)] = int(texte.rsplit(")", 1)[-1].split()[1])
        except (AttributeError, ValueError, IndexError):
            continue
    return resultat


def parents():
    """{pid: pid du parent} pour tous les processus (photo de Windows, ou /proc)."""
    if not systeme.WINDOWS:
        return parents_linux()
    import ctypes  # noqa: PLC0415
    from ctypes import wintypes  # noqa: PLC0415
    _Entree = _classe_entree()
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    k32.Process32FirstW.argtypes = k32.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(_Entree)]
    k32.CloseHandle.argtypes = [wintypes.HANDLE]
    photo = k32.CreateToolhelp32Snapshot(0x2, 0)
    if not photo or photo == wintypes.HANDLE(-1).value:
        return {}
    resultat = {}
    try:
        entree = _Entree()
        entree.dwSize = ctypes.sizeof(_Entree)
        ok = k32.Process32FirstW(photo, ctypes.byref(entree))
        while ok:
            resultat[entree.th32ProcessID] = entree.th32ParentProcessID
            ok = k32.Process32NextW(photo, ctypes.byref(entree))
    finally:
        k32.CloseHandle(photo)
    return resultat


def ancetres(pid):
    """Les PID de « pid », de son parent, de son grand-parent…"""
    liens = parents()
    chaine, courant = [], pid
    while courant and courant not in chaine and len(chaine) < 64:
        chaine.append(courant)
        courant = liens.get(courant)
    return set(chaine)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
def _pid(d):
    try:
        pid = int(d.get("pid"))
    except (TypeError, ValueError):
        raise ValueError("Numéro de processus invalide.") from None
    if pid < 0:
        raise ValueError("Numéro de processus invalide.")
    return pid


def _port(d):
    try:
        port = int(d.get("port"))
    except (TypeError, ValueError):
        raise ValueError("Numéro de port invalide.") from None
    if not 1 <= port <= 65535:
        raise ValueError("Numéro de port invalide.")
    return port


def liste(d):
    udp = bool(d.get("udp"))
    return {"ports": lister_ports(udp=udp, forcer=bool(d.get("forcer"))), "udp": udp}


def chercher(d):
    """Qui occupe ce port ? (TCP)"""
    return {"port": _port(d), "resultat": qui_ecoute(_port(d))}


def verifier_arret(pid, nom_attendu, arbre=False):
    """Lève ValueError si le processus ne doit pas être arrêté. Rend son nom."""
    if pid in (PID_PROTEGES if systeme.WINDOWS else {0, 1}):
        raise ValueError("Processus système : arrêt refusé.")
    nous = nos_pids()
    if pid in nous:
        raise ValueError("C'est « Mes outils » lui-même : arrêt refusé.")
    actuel = processus_pid(pid)
    if not actuel:
        raise ValueError("Ce processus n'existe plus.")
    if nom_court(actuel["nom"]) in PROTEGES:
        raise ValueError("Processus système : arrêt refusé.")
    if not systeme.WINDOWS and est_protege_linux(pid, actuel["nom"], actuel.get("uid")):
        raise ValueError("Processus système : arrêt refusé.")
    if not nom_attendu or nom_court(actuel["nom"]) != nom_court(nom_attendu):
        raise ValueError("Ce numéro de processus correspond maintenant à un autre programme : actualisez la liste.")
    if arbre and pid in ancetres(os.getpid()):
        raise ValueError("Cet arbre de processus contient « Mes outils » : arrêt refusé.")
    return actuel["nom"]


def arreter(d):
    pid = _pid(d)
    arbre = bool(d.get("arbre"))
    nom = verifier_arret(pid, str(d.get("nom") or ""), arbre)
    if not systeme.WINDOWS:
        ok, message = systeme.arreter_processus(pid, arbre=arbre)
        if not ok:
            raise ValueError("Arrêt impossible : " + (message or "le processus ne s'arrête pas."))
        oublier_cache()
        return {"ok": True, "pid": pid, "nom": nom}
    commande = ["taskkill", "/PID", str(pid), "/F"] + (["/T"] if arbre else [])
    r = subprocess.run(commande, capture_output=True, timeout=20, **systeme.options_sans_fenetre())
    if r.returncode != 0:
        detail = (r.stderr or r.stdout or b"").decode("oem", errors="replace").strip().splitlines()
        raise ValueError("Arrêt impossible : " + (detail[0] if detail else f"code {r.returncode}"))
    oublier_cache()
    return {"ok": True, "pid": pid, "nom": nom}


def ouvrir(d):
    port = _port(d)
    webbrowser.open(f"http://localhost:{port}/")
    return {"ok": True}


ROUTES = {"liste": liste, "chercher": chercher, "arreter": arreter, "ouvrir": ouvrir}
