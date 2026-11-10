# -*- coding: utf-8 -*-
"""Installation de « Mes outils » : vérifications et raccourcis.

Windows : raccourcis « Mes outils.lnk » sur le Bureau et dans le dossier
Démarrage.
Linux (freedesktop : Ubuntu, Fedora…) : entrée dans le menu des applications
(~/.local/share/applications/mes-outils.desktop), démarrage avec la session
(~/.config/autostart/mes-outils.desktop) et icône
(~/.local/share/icons/hicolor/256x256/apps/mes-outils.png). Elles lancent
l'AppImage ($APPIMAGE) ou, depuis le code source, python outil/bulle.py.

Utilisé par installer.bat (python outil\\installation.py --installer), par la
bulle (premier lancement sous Linux) et par l'onglet Réglages.
"""
import ctypes
import importlib.util
import os
import shutil
import subprocess
import sys

import systeme

# Programme installé (Mes outils.exe ou AppImage, sans Python) ou code source.
GELE = bool(getattr(sys, "frozen", False))
ICI = getattr(sys, "_MEIPASS", None) or os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(sys.executable) if GELE else os.path.dirname(ICI)
NOM_RACCOURCI = "Mes outils.lnk"
ICONE = sys.executable if GELE else os.path.join(ICI, "mes_outils.ico")
ICONE_PNG = os.path.join(ICI, "mes_outils.png")
BULLE = os.path.join(ICI, "bulle.py")
CREATE_NO_WINDOW = 0x08000000
# Dossiers spéciaux de Windows (SHGetFolderPathW)
CSIDL = {"bureau": 0x0010, "demarrage": 0x0007}
# Linux : entrée du menu des applications, démarrage avec la session.
GENRES_LINUX = ("menu", "demarrage")
NOM_DESKTOP = systeme.ID_APPLI + ".desktop"
BIBLIOTHEQUES = {"cryptography": "cryptography", "PIL": "Pillow"}


def genres():
    """Les raccourcis possibles sur ce système."""
    return tuple(CSIDL) if systeme.WINDOWS else GENRES_LINUX


# ---------------------------------------------------------------------------
# Windows
# ---------------------------------------------------------------------------
def dossier_special(genre):
    """Le vrai dossier du Bureau ou du Démarrage (le Bureau peut être dans
    OneDrive)."""
    tampon = ctypes.create_unicode_buffer(260)
    if ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL[genre], None, 0, tampon) != 0:
        raise RuntimeError(f"Dossier Windows introuvable : {genre}")
    return tampon.value


def chemin_raccourci(genre):
    if not systeme.WINDOWS:
        return chemin_desktop(genre)
    return os.path.join(dossier_special(genre), NOM_RACCOURCI)


def python_fenetre():
    """pythonw.exe (sans fenêtre noire) : celui de MES_OUTILS_PYTHON, sinon
    celui qui fait tourner ce programme (sous Linux : python lui-même)."""
    if GELE:
        return sys.executable  # Mes outils.exe lance lui-même la bulle
    choisi = os.environ.get("MES_OUTILS_PYTHON")
    if choisi and os.path.isfile(choisi):
        return choisi
    if not systeme.WINDOWS:
        return sys.executable
    dossier = os.path.dirname(sys.executable)
    pythonw = os.path.join(dossier, "pythonw.exe")
    return pythonw if os.path.isfile(pythonw) else sys.executable


def creer_raccourci(genre):
    """Raccourci « Mes outils » qui lance la bulle. Les chemins passent par
    l'environnement de PowerShell, jamais dans le texte de la commande."""
    if not systeme.WINDOWS:
        return creer_desktop(genre)
    cible = chemin_raccourci(genre)
    env = dict(os.environ, MO_LNK=cible, MO_CIBLE=python_fenetre(), MO_ARGS="" if GELE else f'"{BULLE}"',
               MO_DOSSIER=RACINE, MO_ICONE=ICONE)
    script = ("$r = (New-Object -ComObject WScript.Shell).CreateShortcut($env:MO_LNK); "
              "$r.TargetPath = $env:MO_CIBLE; $r.Arguments = $env:MO_ARGS; "
              "$r.WorkingDirectory = $env:MO_DOSSIER; $r.IconLocation = $env:MO_ICONE; "
              "$r.Description = 'Mes outils'; $r.Save()")
    r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script], env=env,
                       capture_output=True, text=True, timeout=30, creationflags=CREATE_NO_WINDOW)
    if r.returncode != 0 or not os.path.isfile(cible):
        raise RuntimeError("Raccourci impossible à créer : " + (r.stderr or "").strip()[:200])
    return cible


def supprimer_raccourci(genre):
    cible = chemin_raccourci(genre)
    if os.path.isfile(cible):
        os.remove(cible)


def etat():
    resultat = {}
    for genre in genres():
        try:
            resultat[genre] = os.path.isfile(chemin_raccourci(genre))
        except RuntimeError:
            resultat[genre] = False
    return resultat


# ---------------------------------------------------------------------------
# Linux : fichiers .desktop (freedesktop.org)
# ---------------------------------------------------------------------------
def _donnees_xdg():
    return os.environ.get("XDG_DATA_HOME") or os.path.join(os.path.expanduser("~"), ".local", "share")


def _config_xdg():
    return os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")


def chemin_desktop(genre):
    """~/.local/share/applications/mes-outils.desktop (menu) ou
    ~/.config/autostart/mes-outils.desktop (démarrage)."""
    if genre == "menu":
        return os.path.join(_donnees_xdg(), "applications", NOM_DESKTOP)
    if genre == "demarrage":
        return os.path.join(_config_xdg(), "autostart", NOM_DESKTOP)
    raise ValueError("Raccourci inconnu.")


def chemin_icone_linux():
    return os.path.join(_donnees_xdg(), "icons", "hicolor", "256x256", "apps", systeme.ID_APPLI + ".png")


def commande_linux():
    """Ce que lancent les entrées : l'AppImage (là où elle est maintenant),
    le programme gelé, ou python + outil/bulle.py (code source)."""
    appimage = os.environ.get("APPIMAGE")
    if appimage and os.path.isfile(appimage):
        return [os.path.abspath(appimage)]
    if GELE:
        return [sys.executable]
    return [python_fenetre(), BULLE]


def argument_exec(argument):
    """Un argument de la ligne Exec= (spécification Desktop Entry) : entre
    guillemets si besoin, « % » doublé."""
    argument = str(argument).replace("%", "%%")
    if argument and not any(c in argument for c in ' \t\n"\'\\><~|&;$*?#()`'):
        return argument
    for c in ("\\", '"', "`", "$"):
        argument = argument.replace(c, "\\" + c)
    return f'"{argument}"'


def contenu_desktop(genre, commande=None, icone=None):
    """Le texte du fichier .desktop."""
    commande = commande or commande_linux()
    icone = icone or (chemin_icone_linux() if os.path.isfile(chemin_icone_linux()) else systeme.ID_APPLI)
    lignes = [
        "[Desktop Entry]",
        "Type=Application",
        "Version=1.0",
        f"Name={systeme.NOM_APPLI}",
        "GenericName=Tableau de bord",
        "GenericName[en]=Dashboard",
        "Comment=Tableau de bord : outils, mails, agenda, notes, projets",
        "Comment[en]=Dashboard: tools, mail, calendar, notes, projects",
        "Exec=" + " ".join(argument_exec(a) for a in commande),
        f"Icon={icone}",
        "Terminal=false",
        "Categories=Utility;Office;",
        # Relie la fenêtre du tableau de bord (--class) et la bulle à cette entrée.
        f"StartupWMClass={systeme.ID_APPLI}",
        "StartupNotify=false",
    ]
    if not GELE:
        lignes.append("Path=" + RACINE)
    if genre == "demarrage":
        lignes += ["X-GNOME-Autostart-enabled=true", "X-GNOME-Autostart-Delay=3"]
    return "\n".join(lignes) + "\n"


def installer_icone_linux():
    """Copie l'icône (PNG 256 x 256) dans le thème de l'utilisateur."""
    if not os.path.isfile(ICONE_PNG):
        return None
    cible = chemin_icone_linux()
    os.makedirs(os.path.dirname(cible), exist_ok=True)
    shutil.copyfile(ICONE_PNG, cible)
    return cible


def creer_desktop(genre):
    """Crée (ou remplace) l'entrée « Mes outils » de ce genre."""
    cible = chemin_desktop(genre)
    try:
        installer_icone_linux()
    except OSError:
        pass  # sans icône : l'entrée garde le nom du thème
    try:
        os.makedirs(os.path.dirname(cible), exist_ok=True)
        provisoire = cible + ".tmp"
        with open(provisoire, "w", encoding="utf-8", newline="\n") as f:
            f.write(contenu_desktop(genre))
        os.chmod(provisoire, 0o755)  # certains bureaux exigent un .desktop exécutable
        os.replace(provisoire, cible)
    except OSError as erreur:
        raise RuntimeError(f"Raccourci impossible à créer : {erreur}") from None
    return cible


def preparer_linux():
    """Au lancement de la bulle sous Linux : au tout premier lancement,
    l'entrée du menu des applications est créée ; ensuite, les entrées
    existantes sont réécrites si leur contenu a changé (AppImage déplacée ou
    renommée). Une entrée retirée dans les Réglages n'est pas recréée.
    Renvoie les genres écrits."""
    import config  # noqa: PLC0415

    faites = []
    if not config.lire().get("menu_linux_propose"):
        creer_desktop("menu")
        config.modifier(menu_linux_propose=True)
        faites.append("menu")
    for genre in GENRES_LINUX:
        chemin = chemin_desktop(genre)
        if genre in faites or not os.path.isfile(chemin):
            continue
        try:
            with open(chemin, encoding="utf-8") as f:
                actuel = f.read()
        except OSError:
            continue
        if actuel != contenu_desktop(genre):
            creer_desktop(genre)
            faites.append(genre)
    return faites


# ---------------------------------------------------------------------------
# Vérifications et installation depuis le code source
# ---------------------------------------------------------------------------
def verifier():
    """Ce qui manque pour faire tourner « Mes outils » (liste vide = tout va bien)."""
    manque = []
    if GELE:
        return manque  # tout est déjà dans le programme installé
    if sys.version_info < (3, 10):
        manque.append(f"Python 3.10 ou plus récent (ici {sys.version.split()[0]})")
    if importlib.util.find_spec("tkinter") is None:
        manque.append("tkinter (cocher « tcl/tk » dans l'installateur de python.org)" if systeme.WINDOWS
                      else "tkinter (sudo apt install python3-tk)")
    for module, paquet in BIBLIOTHEQUES.items():
        if importlib.util.find_spec(module) is None:
            manque.append(f"la bibliothèque {paquet} (pip install -r requirements.txt)")
    return manque


def installer():
    print("Mes outils : vérification…")
    manque = verifier()
    if manque:
        print("Il manque :")
        for m in manque:
            print("  -", m)
        return 1
    noms = (("bureau", "Bureau"), ("demarrage", "Démarrage de Windows")) if systeme.WINDOWS else \
        (("menu", "Menu des applications"), ("demarrage", "Démarrage avec la session"))
    for genre, nom in noms:
        try:
            creer_raccourci(genre)
            print(f"  Raccourci créé : {nom}")
        except RuntimeError as e:
            print(f"  {nom} : {e}")
    print("Installation terminée. La bulle 🧰 va apparaître." if systeme.WINDOWS
          else "Installation terminée. La bulle va apparaître.")
    return 0


def lancer():
    """Démarre la bulle, détachée de la fenêtre d'installation."""
    if not systeme.WINDOWS:
        systeme.lancer_detache(commande_linux(), dossier=RACINE)
        return
    subprocess.Popen([python_fenetre()] + ([] if GELE else [BULLE]), cwd=RACINE, close_fds=True,
                     creationflags=0x00000008 | 0x00000200)  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP


if __name__ == "__main__":
    if "--lancer" in sys.argv:
        lancer()
        sys.exit(0)
    if "--verifier" in sys.argv:
        problemes = verifier()
        print("\n".join(problemes) if problemes else "ok")
        sys.exit(1 if problemes else 0)
    if "--installer" in sys.argv:
        sys.exit(installer())
    print("Usage : python outil\\installation.py --installer | --verifier" if systeme.WINDOWS
          else "Usage : python3 outil/installation.py --installer | --verifier")
