# -*- coding: utf-8 -*-
"""Tout ce qui dépend du système d'exploitation (Windows ou Linux), au même endroit.

Les autres modules n'appellent jamais Windows ou Linux directement : ils passent
par les fonctions ci-dessous, qui ont le même comportement sur les deux.

- Lancer un programme sans fenêtre de console, détaché de Mes outils.
- Ouvrir un fichier, un dossier ou une adresse avec le programme habituel.
- Montrer un fichier dans le gestionnaire de fichiers.
- Fenêtres « Ouvrir » et « Choisir un dossier ».
- Navigateur de la famille Chromium (Edge, Chrome, Chromium, Brave) : fenêtre
  « application » sans barre d'adresse, et PDF sans fenêtre.
- Secrets (mots de passe de mail, jeton GitHub) : coffre de Windows
  (Gestionnaire d'identification), ou trousseau du bureau sous Linux (Secret
  Service : GNOME Keyring, KWallet).
- Notifications du bureau, terminal, arrêt d'un processus et de ses enfants.

Sous Linux, aucune bibliothèque n'est obligatoire : les secrets passent par
« secretstorage » si elle est là (incluse dans l'AppImage), sinon par la
commande « secret-tool ».
"""
import os
import shutil
import signal
import subprocess
import sys
import time
import webbrowser

WINDOWS = sys.platform == "win32"
LINUX = sys.platform.startswith("linux")
MAC = sys.platform == "darwin"

# Drapeaux de création de processus (Windows seulement ; 0 ailleurs, car
# subprocess refuse creationflags non nul hors de Windows).
SANS_FENETRE = 0x08000000 if WINDOWS else 0           # CREATE_NO_WINDOW
NOUVEAU_GROUPE = 0x00000200 if WINDOWS else 0         # CREATE_NEW_PROCESS_GROUP
NOUVELLE_CONSOLE = 0x00000010 if WINDOWS else 0       # CREATE_NEW_CONSOLE
DETACHE = (0x00000008 | 0x00000200) if WINDOWS else 0  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP

NOM_APPLI = "Mes outils"
ID_APPLI = "mes-outils"


# ---------------------------------------------------------------------------
# Processus
# ---------------------------------------------------------------------------
def options_sans_fenetre():
    """Arguments de subprocess pour une commande sans fenêtre de console."""
    return {"creationflags": SANS_FENETRE} if WINDOWS else {}


def options_detache(console=False):
    """Arguments de subprocess.Popen pour un programme qui vit sa vie, même
    si Mes outils s'arrête. console=True : garder une console (Windows)."""
    if WINDOWS:
        drapeaux = NOUVEAU_GROUPE | (NOUVELLE_CONSOLE if console else (0x00000008 | SANS_FENETRE))
        return {"creationflags": drapeaux, "close_fds": True}
    return {"start_new_session": True, "close_fds": True}


def lancer_detache(commande, dossier=None, env=None):
    """Lance un programme détaché, sans console, sans rien attendre."""
    return subprocess.Popen(commande, cwd=dossier, env=env, stdin=subprocess.DEVNULL,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **options_detache())


def processus_vivant(pid):
    """Vrai si ce processus existe encore (et n'est pas un zombie sous Linux)."""
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    if WINDOWS:
        import ctypes
        from ctypes import wintypes
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.OpenProcess.restype = wintypes.HANDLE
        k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        k32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        k32.CloseHandle.argtypes = [wintypes.HANDLE]
        h = k32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return False
        try:
            code = wintypes.DWORD()
            return bool(k32.GetExitCodeProcess(h, ctypes.byref(code))) and code.value == 259  # STILL_ACTIVE
        finally:
            k32.CloseHandle(h)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    try:
        with open(f"/proc/{pid}/stat", encoding="utf-8", errors="replace") as f:
            return f.read().rsplit(")", 1)[-1].split()[0] != "Z"
    except OSError:
        return True


def enfants_linux(pid):
    """Les PID des descendants d'un processus (Linux, d'après /proc)."""
    parents = {}
    for nom in os.listdir("/proc"):
        if not nom.isdigit():
            continue
        try:
            with open(f"/proc/{nom}/stat", encoding="utf-8", errors="replace") as f:
                ppid = int(f.read().rsplit(")", 1)[-1].split()[1])
        except (OSError, ValueError, IndexError):
            continue
        parents.setdefault(ppid, []).append(int(nom))
    resultat, a_voir = [], [int(pid)]
    while a_voir:
        for enfant in parents.get(a_voir.pop(), []):
            if enfant not in resultat:
                resultat.append(enfant)
                a_voir.append(enfant)
    return resultat


def arreter_processus(pid, arbre=True, delai=3.0):
    """Arrête un processus (et ses enfants si arbre). Renvoie (ok, message)."""
    pid = int(pid)
    if WINDOWS:
        commande = ["taskkill", "/PID", str(pid), "/F"] + (["/T"] if arbre else [])
        r = subprocess.run(commande, capture_output=True, timeout=30, stdin=subprocess.DEVNULL,
                           **options_sans_fenetre())
        sortie = (r.stdout or b"") + (r.stderr or b"")
        return r.returncode == 0, sortie.decode("utf-8", "replace").strip()
    cibles = (enfants_linux(pid) if arbre else []) + [pid]
    for sig in (signal.SIGTERM, signal.SIGKILL):
        for p in cibles:
            try:
                os.kill(p, sig)
            except ProcessLookupError:
                pass
            except PermissionError:
                return False, "Permission refusée : ce processus appartient à un autre utilisateur."
        fin = time.time() + delai
        while time.time() < fin and any(processus_vivant(p) for p in cibles):
            time.sleep(0.1)
        if not any(processus_vivant(p) for p in cibles):
            return True, ""
    return not processus_vivant(pid), ""


def nom_processus(pid):
    """Le nom court du programme d'un PID (Linux : /proc/<pid>/comm), ou ""."""
    if WINDOWS:
        return ""
    try:
        with open(f"/proc/{int(pid)}/comm", encoding="utf-8", errors="replace") as f:
            return f.read().strip()
    except (OSError, ValueError):
        return ""


# ---------------------------------------------------------------------------
# Ouvrir, montrer
# ---------------------------------------------------------------------------
def ouvrir(cible):
    """Ouvre un fichier, un dossier ou une adresse (mailto:, https:…) avec le
    programme habituel du système."""
    cible = str(cible)
    if WINDOWS:
        os.startfile(cible)  # noqa: S606
        return
    commande = "open" if MAC else "xdg-open"
    if not shutil.which(commande):
        if "://" in cible or cible.startswith("mailto:"):
            webbrowser.open(cible)
            return
        raise RuntimeError("Impossible d'ouvrir : la commande xdg-open est absente.")
    lancer_detache([commande, cible])


def montrer_dans_dossier(chemin):
    """Ouvre le gestionnaire de fichiers sur le dossier, fichier sélectionné
    quand c'est possible."""
    chemin = os.path.abspath(str(chemin))
    if WINDOWS:
        subprocess.Popen(f'explorer.exe /select,"{chemin}"', **options_sans_fenetre())
        return
    if os.path.isfile(chemin):
        # Nautilus, Nemo, Dolphin et Caja savent sélectionner un fichier.
        for programme, args in (("nautilus", ["--select"]), ("nemo", []), ("dolphin", ["--select"]),
                                ("caja", ["--select"])):
            if shutil.which(programme):
                lancer_detache([programme, *args, chemin])
                return
        chemin = os.path.dirname(chemin)
    ouvrir(chemin)


# ---------------------------------------------------------------------------
# Navigateur (famille Chromium)
# ---------------------------------------------------------------------------
def _candidats_windows():
    candidats = []
    for variable in ("ProgramFiles(x86)", "ProgramFiles", "LOCALAPPDATA"):
        racine = os.environ.get(variable)
        if racine:
            candidats.append(os.path.join(racine, "Microsoft", "Edge", "Application", "msedge.exe"))
    candidats += [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                  r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]
    for variable in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"):
        racine = os.environ.get(variable)
        if racine:
            candidats.append(os.path.join(racine, "Google", "Chrome", "Application", "chrome.exe"))
    candidats.append(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    return candidats


NOMS_CHROMIUM_LINUX = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
                       "microsoft-edge", "microsoft-edge-stable", "brave-browser", "brave")


def navigateur_chromium():
    """Edge, Chrome, Chromium ou Brave (chemin de l'exécutable), ou None."""
    if WINDOWS:
        for c in _candidats_windows():
            if os.path.isfile(c):
                return c
        return shutil.which("msedge") or shutil.which("chrome")
    for nom in NOMS_CHROMIUM_LINUX:
        trouve = shutil.which(nom)
        if trouve:
            return trouve
    # Paquets snap et flatpak d'Ubuntu.
    for chemin in ("/snap/bin/chromium", "/var/lib/flatpak/exports/bin/com.google.Chrome",
                   os.path.expanduser("~/.local/share/flatpak/exports/bin/com.google.Chrome")):
        if os.path.isfile(chemin):
            return chemin
    return None


def nom_navigateur():
    """Pour les messages : « Edge », « Chrome »… ou « Chrome ou Chromium »."""
    chemin = (navigateur_chromium() or "").lower()
    for cle, nom in (("edge", "Edge"), ("brave", "Brave"), ("chromium", "Chromium"), ("chrome", "Chrome")):
        if cle in chemin:
            return nom
    return "Edge" if WINDOWS else "Chrome ou Chromium"


def ouvrir_fenetre_appli(url, largeur=1360, hauteur=860):
    """Une fenêtre sans barre d'adresse, comme un logiciel. À défaut d'un
    navigateur Chromium, un onglet du navigateur par défaut."""
    navigateur = navigateur_chromium()
    if navigateur:
        args = [navigateur, f"--app={url}", f"--window-size={largeur},{hauteur}"]
        if LINUX:
            # Une icône et un nom à part dans le dock de GNOME.
            args.append(f"--class={ID_APPLI}")
        proc = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, **(
                             {"creationflags": DETACHE, "close_fds": True} if WINDOWS
                             else {"start_new_session": True, "close_fds": True}))
        return proc
    webbrowser.open(url)
    return None


def html_vers_pdf(source_html, sortie_pdf, profil, delai=90):
    """Imprime un fichier HTML en PDF avec le navigateur sans fenêtre.
    Lève ValueError si aucun navigateur ne convient ou si le PDF est vide."""
    navigateur = navigateur_chromium()
    if not navigateur:
        raise ValueError("Microsoft Edge est introuvable : impossible de créer le PDF." if WINDOWS else
                         "Google Chrome ou Chromium est introuvable : impossible de créer le PDF.")
    bac = dossier_snap(navigateur)
    if bac:
        # Navigateur en snap (Chromium d'Ubuntu) : il ne voit ni /tmp ni les
        # dossiers cachés. Il travaille dans son propre dossier ~/snap/<nom>/common.
        travail = os.path.join(bac, f"mes-outils-pdf-{os.getpid()}-{int(time.time() * 1000)}")
        os.makedirs(travail, exist_ok=True)
        try:
            source_snap = os.path.join(travail, "document.html")
            shutil.copyfile(source_html, source_snap)
            sortie_snap = os.path.join(travail, "document.pdf")
            _imprimer(navigateur, source_snap, sortie_snap, os.path.join(travail, "profil"), delai)
            shutil.move(sortie_snap, sortie_pdf)
        finally:
            shutil.rmtree(travail, ignore_errors=True)
    else:
        _imprimer(navigateur, source_html, sortie_pdf, profil, delai)
    if not os.path.isfile(sortie_pdf) or os.path.getsize(sortie_pdf) == 0:
        raise ValueError(f"{nom_navigateur()} n'a pas pu créer le PDF.")


def _imprimer(navigateur, source_html, sortie_pdf, profil, delai):
    url = "file:///" + os.path.abspath(source_html).replace("\\", "/").lstrip("/")
    commande = [navigateur, "--headless", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                "--disable-extensions", f"--user-data-dir={profil}",
                "--no-pdf-header-footer", "--print-to-pdf-no-header", f"--print-to-pdf={sortie_pdf}", url]
    subprocess.run(commande, timeout=delai, capture_output=True, stdin=subprocess.DEVNULL,
                   **options_sans_fenetre())


def dossier_snap(navigateur):
    """~/snap/<nom>/common si le navigateur est un paquet snap, sinon None."""
    if WINDOWS or not navigateur:
        return None
    chemin = os.path.realpath(navigateur)
    if not (chemin.startswith("/snap/") or navigateur.startswith("/snap/bin/")):
        return None
    nom = os.path.basename(navigateur) if navigateur.startswith("/snap/bin/") else chemin.split("/")[2]
    nom = {"chromium-browser": "chromium"}.get(nom, nom)
    return os.path.join(os.path.expanduser("~"), "snap", nom, "common")


# ---------------------------------------------------------------------------
# Fenêtres « Ouvrir » et « Choisir un dossier »
# ---------------------------------------------------------------------------
_PS_FICHIERS = r"""
Add-Type -AssemblyName System.Windows.Forms
$p = New-Object System.Windows.Forms.Form
$p.TopMost = $true
$d = New-Object System.Windows.Forms.OpenFileDialog
$d.Title = $env:MO_TITRE
$d.Multiselect = ($env:MO_MULTI -eq "1")
$d.CheckFileExists = $true
$d.Filter = $env:MO_FILTRE
if ($env:MO_DEPART -and (Test-Path -LiteralPath $env:MO_DEPART)) { $d.InitialDirectory = $env:MO_DEPART }
if ($d.ShowDialog($p) -eq [System.Windows.Forms.DialogResult]::OK) {
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  foreach ($f in $d.FileNames) { Write-Output $f }
}
"""

_PS_DOSSIER = r"""
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

TOUS_LES_FICHIERS = "Tous les fichiers (*.*)|*.*"


def lire_filtre(filtre):
    """Filtre au format Windows (« Images (*.png;*.jpg)|*.png;*.jpg|… ») →
    [(libellé, [motifs])]."""
    morceaux = [m for m in str(filtre or TOUS_LES_FICHIERS).split("|")]
    paires = []
    for i in range(0, len(morceaux) - 1, 2):
        motifs = [m.strip() for m in morceaux[i + 1].split(";") if m.strip()]
        if motifs:
            paires.append((morceaux[i].strip(), motifs))
    return paires or [("Tous les fichiers", ["*"])]


def depart_existant(chemin):
    """Le dossier existant le plus proche (pour ouvrir la fenêtre au bon endroit)."""
    chemin = os.path.normpath(str(chemin or "")) if chemin else ""
    while chemin and not os.path.isdir(chemin):
        parent = os.path.dirname(chemin)
        if parent == chemin:
            return ""
        chemin = parent
    return chemin


def _lignes(sortie, separateur="\n"):
    return [x.strip() for x in (sortie or "").split(separateur) if x.strip()]


def _zenity_fichiers(titre, depart, multi, filtre):
    args = ["zenity", "--file-selection", f"--title={titre}", "--separator=\n"]
    if multi:
        args.append("--multiple")
    if depart:
        args.append(f"--filename={depart.rstrip('/')}/")
    for libelle, motifs in lire_filtre(filtre):
        motifs = ["*" if m == "*.*" else m for m in motifs]
        args.append(f"--file-filter={libelle} | {' '.join(motifs)}")
    return args


def _kdialog_fichiers(titre, depart, multi, filtre):
    filtres = "\n".join(f"{' '.join('*' if m == '*.*' else m for m in motifs)}|{libelle}"
                        for libelle, motifs in lire_filtre(filtre))
    args = ["kdialog", "--title", titre, "--getopenfilename", depart or os.path.expanduser("~"), filtres]
    if multi:
        args[3:3] = ["--multiple", "--separate-output"]
    return args


def _executer_fenetre(args, env=None):
    r = subprocess.run(args, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=600, stdin=subprocess.DEVNULL, **options_sans_fenetre())
    return r.stdout or ""


def outil_de_fenetres():
    """« zenity », « kdialog » ou None (Linux)."""
    bureau = (os.environ.get("XDG_CURRENT_DESKTOP") or "").upper()
    ordre = ("kdialog", "zenity") if "KDE" in bureau else ("zenity", "kdialog")
    return next((o for o in ordre if shutil.which(o)), None)


def choisir_fichiers(titre="Choisir des fichiers", depart="", multi=True, filtre=None):
    """Fenêtre « Ouvrir » du système. Renvoie la liste des fichiers choisis
    (vide si annulé). filtre : format Windows (voir lire_filtre)."""
    titre = str(titre or "Choisir des fichiers")[:120]
    depart = depart_existant(depart)
    if WINDOWS:
        env = dict(os.environ, MO_TITRE=titre, MO_DEPART=depart, MO_MULTI="1" if multi else "0",
                   MO_FILTRE=str(filtre or TOUS_LES_FICHIERS)[:200])
        sortie = _executer_fenetre(["powershell", "-NoProfile", "-NonInteractive", "-STA", "-Command", _PS_FICHIERS],
                                   env)
    else:
        outil = outil_de_fenetres()
        if not outil:
            raise RuntimeError("Aucune fenêtre de choix de fichiers : installez zenity "
                               "(sudo apt install zenity).")
        args = (_zenity_fichiers if outil == "zenity" else _kdialog_fichiers)(titre, depart, multi, filtre)
        sortie = _executer_fenetre(args)
    return [x for x in _lignes(sortie) if os.path.isfile(x)]


def choisir_dossier(titre="Choisir un dossier", depart=""):
    """Fenêtre « Choisir un dossier » du système. Renvoie le chemin ou None."""
    titre = str(titre or "Choisir un dossier")[:120]
    depart = depart_existant(depart)
    if WINDOWS:
        env = dict(os.environ, MO_TITRE=titre, MO_DEPART=depart)
        sortie = _executer_fenetre(["powershell", "-NoProfile", "-NonInteractive", "-STA", "-Command", _PS_DOSSIER],
                                   env)
    else:
        outil = outil_de_fenetres()
        if not outil:
            raise RuntimeError("Aucune fenêtre de choix de dossier : installez zenity "
                               "(sudo apt install zenity).")
        if outil == "zenity":
            args = ["zenity", "--file-selection", "--directory", f"--title={titre}"]
            if depart:
                args.append(f"--filename={depart.rstrip('/')}/")
        else:
            args = ["kdialog", "--title", titre, "--getexistingdirectory", depart or os.path.expanduser("~")]
        sortie = _executer_fenetre(args)
    lignes = _lignes(sortie)
    return lignes[-1] if lignes and os.path.isdir(lignes[-1]) else None


# ---------------------------------------------------------------------------
# Secrets : coffre de Windows ou trousseau du bureau (Secret Service)
# ---------------------------------------------------------------------------
class ErreurSecret(RuntimeError):
    pass


_win_cred = None


def _cred_windows():
    """Les fonctions advapi32 du Gestionnaire d'identification (chargées une fois)."""
    global _win_cred
    if _win_cred is None:
        import ctypes
        from ctypes import wintypes

        class CREDENTIAL(ctypes.Structure):
            _fields_ = [
                ("Flags", wintypes.DWORD), ("Type", wintypes.DWORD), ("TargetName", wintypes.LPWSTR),
                ("Comment", wintypes.LPWSTR), ("LastWritten", wintypes.FILETIME),
                ("CredentialBlobSize", wintypes.DWORD), ("CredentialBlob", ctypes.POINTER(ctypes.c_char)),
                ("Persist", wintypes.DWORD), ("AttributeCount", wintypes.DWORD), ("Attributes", ctypes.c_void_p),
                ("TargetAlias", wintypes.LPWSTR), ("UserName", wintypes.LPWSTR),
            ]

        advapi = ctypes.WinDLL("advapi32", use_last_error=True)
        advapi.CredReadW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                     ctypes.POINTER(ctypes.POINTER(CREDENTIAL))]
        advapi.CredWriteW.argtypes = [ctypes.POINTER(CREDENTIAL), wintypes.DWORD]
        advapi.CredDeleteW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD]
        advapi.CredFree.argtypes = [ctypes.c_void_p]
        _win_cred = (ctypes, CREDENTIAL, advapi)
    return _win_cred


def _secretstorage():
    """(module, collection) du Secret Service, ou None si indisponible."""
    try:
        import secretstorage  # noqa: PLC0415
    except ImportError:
        return None
    try:
        connexion = secretstorage.dbus_init()
        collection = secretstorage.get_default_collection(connexion)
        if collection.is_locked():
            collection.unlock()  # le trousseau demande son mot de passe s'il le faut
        if collection.is_locked():
            raise ErreurSecret("Le trousseau du bureau est verrouillé.")
        return secretstorage, collection
    except ErreurSecret:
        raise
    except Exception as erreur:  # noqa: BLE001
        raise ErreurSecret(f"Trousseau du bureau inaccessible ({erreur}).") from erreur


def _attributs(cible):
    return {"application": ID_APPLI, "cible": str(cible)}


def secret_ecrire(cible, utilisateur, secret):
    """Range (ou remplace) le secret de cette cible. Renvoie False en cas d'échec."""
    if WINDOWS:
        ctypes, CREDENTIAL, advapi = _cred_windows()
        blob = str(secret).encode("utf-16-le")
        tampon = ctypes.create_string_buffer(blob, len(blob))
        cred = CREDENTIAL()
        cred.Type = 1  # CRED_TYPE_GENERIC
        cred.TargetName = cible
        cred.UserName = utilisateur
        cred.CredentialBlobSize = len(blob)
        cred.CredentialBlob = ctypes.cast(tampon, ctypes.POINTER(ctypes.c_char))
        cred.Persist = 2  # CRED_PERSIST_LOCAL_MACHINE
        return bool(advapi.CredWriteW(ctypes.byref(cred), 0))
    try:
        ss = _secretstorage()
    except ErreurSecret:
        return False
    if ss:
        _, collection = ss
        try:
            collection.create_item(f"{NOM_APPLI} : {cible}", dict(_attributs(cible), utilisateur=str(utilisateur)),
                                   str(secret).encode("utf-8"), replace=True)
            return True
        except Exception:  # noqa: BLE001
            return False
    if shutil.which("secret-tool"):
        args = ["secret-tool", "store", f"--label={NOM_APPLI} : {cible}"]
        for cle, valeur in _attributs(cible).items():
            args += [cle, valeur]
        r = subprocess.run(args, input=str(secret), text=True, capture_output=True, timeout=60)
        return r.returncode == 0
    return False


def secret_lire(cible):
    """Le secret de cette cible, ou None s'il n'y en a pas."""
    if WINDOWS:
        ctypes, CREDENTIAL, advapi = _cred_windows()
        pcred = ctypes.POINTER(CREDENTIAL)()
        if not advapi.CredReadW(cible, 1, 0, ctypes.byref(pcred)):
            return None
        try:
            c = pcred.contents
            return ctypes.string_at(c.CredentialBlob, c.CredentialBlobSize).decode("utf-16-le")
        finally:
            advapi.CredFree(pcred)
    try:
        ss = _secretstorage()
    except ErreurSecret:
        return None
    if ss:
        _, collection = ss
        try:
            for item in collection.search_items(_attributs(cible)):
                return item.get_secret().decode("utf-8")
        except Exception:  # noqa: BLE001
            return None
        return None
    if shutil.which("secret-tool"):
        args = ["secret-tool", "lookup"]
        for cle, valeur in _attributs(cible).items():
            args += [cle, valeur]
        r = subprocess.run(args, capture_output=True, text=True, timeout=60)
        return r.stdout if r.returncode == 0 and r.stdout else None
    return None


def secret_supprimer(cible):
    if WINDOWS:
        _, _, advapi = _cred_windows()
        advapi.CredDeleteW(cible, 1, 0)
        return
    try:
        ss = _secretstorage()
    except ErreurSecret:
        return
    if ss:
        _, collection = ss
        try:
            for item in list(collection.search_items(_attributs(cible))):
                item.delete()
        except Exception:  # noqa: BLE001
            pass
        return
    if shutil.which("secret-tool"):
        args = ["secret-tool", "clear"]
        for cle, valeur in _attributs(cible).items():
            args += [cle, valeur]
        subprocess.run(args, capture_output=True, timeout=60)


def nom_du_coffre():
    """Pour les messages : où sont rangés les secrets."""
    return "le coffre de Windows" if WINDOWS else "le trousseau du bureau"


# ---------------------------------------------------------------------------
# Bureau : notifications, terminal, éditeur
# ---------------------------------------------------------------------------
def notifier(titre, texte="", icone=None):
    """Une notification du bureau (Linux : notify-send). Sans effet ailleurs."""
    if WINDOWS or not shutil.which("notify-send"):
        return False
    args = ["notify-send", f"--app-name={NOM_APPLI}"]
    if icone:
        args.append(f"--icon={icone}")
    args += [str(titre)[:200], str(texte or "")[:500]]
    try:
        lancer_detache(args)
        return True
    except OSError:
        return False


TERMINAUX_LINUX = (
    # (programme, options pour le dossier de départ, option qui précède la commande)
    ("x-terminal-emulator", [], "-e"),
    ("gnome-terminal", ["--working-directory={dossier}"], "--"),
    ("ptyxis", ["--working-directory={dossier}"], "--"),
    ("kgx", ["--working-directory={dossier}"], "-e"),
    ("konsole", ["--workdir", "{dossier}"], "-e"),
    ("xfce4-terminal", ["--working-directory={dossier}"], "-x"),
    ("tilix", ["--working-directory={dossier}"], "-e"),
    ("xterm", [], "-e"),
)


def ouvrir_terminal(dossier=None, commande=None, titre=None):
    """Ouvre un terminal dans ce dossier ; commande (liste) : à lancer dedans.
    Renvoie False si aucun terminal n'a été trouvé."""
    dossier = dossier or os.path.expanduser("~")
    if WINDOWS:
        wt = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WindowsApps", "wt.exe")
        if os.path.isfile(wt):
            args = [wt, "-d", dossier] + (["--title", titre] if titre else []) + (list(commande) if commande else [])
            subprocess.Popen(args, close_fds=True, **options_detache())
        elif commande:
            subprocess.Popen(["cmd.exe", "/c", "start", titre or "Terminal", *commande], cwd=dossier, close_fds=True)
        else:
            subprocess.Popen(["powershell.exe", "-NoExit", "-NoLogo"], cwd=dossier,
                             creationflags=NOUVELLE_CONSOLE, close_fds=True)
        return True
    bureau = (os.environ.get("XDG_CURRENT_DESKTOP") or "").upper()
    ordre = list(TERMINAUX_LINUX)
    if "GNOME" in bureau or "UNITY" in bureau:  # le terminal du bureau d'abord
        ordre.sort(key=lambda t: t[0] not in ("gnome-terminal", "ptyxis", "kgx"))
    elif "KDE" in bureau:
        ordre.sort(key=lambda t: t[0] != "konsole")
    for programme, options, avant_commande in ordre:
        if not shutil.which(programme):
            continue
        args = [programme] + [o.format(dossier=dossier) for o in options]
        if commande:
            args += [avant_commande, *commande]
        lancer_detache(args, dossier=dossier)
        return True
    return False


def code_vscode():
    """La commande de VS Code (code, code-insiders, codium) ou None."""
    if WINDOWS:
        candidats = [os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
                     r"C:\Program Files\Microsoft VS Code\Code.exe",
                     r"C:\Program Files (x86)\Microsoft VS Code\Code.exe"]
        commande = shutil.which("code")
        if commande:  # …\Microsoft VS Code\bin\code.cmd → …\Microsoft VS Code\Code.exe
            candidats.append(os.path.join(os.path.dirname(os.path.dirname(commande)), "Code.exe"))
        return next((c for c in candidats if os.path.isfile(c)), None)
    for nom in ("code", "code-insiders", "codium"):
        trouve = shutil.which(nom)
        if trouve:
            return trouve
    for chemin in ("/snap/bin/code", "/usr/share/code/code"):
        if os.path.isfile(chemin):
            return chemin
    return None


# ---------------------------------------------------------------------------
# Dossiers
# ---------------------------------------------------------------------------
def dossier_donnees_utilisateur():
    """Où vont les réglages et données du programme installé :
    %APPDATA%\\Mes outils, ou ~/.config/mes-outils sous Linux."""
    if WINDOWS:
        return os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), NOM_APPLI)
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, ID_APPLI)


def dossier_documents():
    """Le dossier Documents de l'utilisateur (XDG sous Linux, en français
    « Documents » aussi)."""
    if WINDOWS:
        try:
            import ctypes
            tampon = ctypes.create_unicode_buffer(260)
            if ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, tampon) == 0 and tampon.value:  # CSIDL_PERSONAL
                return tampon.value
        except Exception:  # noqa: BLE001
            pass
        return os.path.join(os.path.expanduser("~"), "Documents")
    if shutil.which("xdg-user-dir"):
        try:
            r = subprocess.run(["xdg-user-dir", "DOCUMENTS"], capture_output=True, text=True, timeout=5)
            chemin = (r.stdout or "").strip()
            if chemin and chemin != os.path.expanduser("~") and os.path.isdir(chemin):
                return chemin
        except (OSError, subprocess.SubprocessError):
            pass
    return os.path.join(os.path.expanduser("~"), "Documents")


def encodage_console():
    """Encodage des sorties des commandes de la console."""
    if WINDOWS:
        try:
            import ctypes
            return f"cp{ctypes.windll.kernel32.GetOEMCP()}"
        except Exception:  # noqa: BLE001
            return "cp850"
    return "utf-8"
