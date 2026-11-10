# -*- mode: python ; coding: utf-8 -*-
"""Construction de « Mes outils » avec PyInstaller (Python et toutes les
bibliothèques inclus : rien d'autre à installer sur le PC).

    pyinstaller packaging/mes_outils.spec --noconfirm

Résultat : dist/Mes outils/ (le programme et son dossier _internal).
- Windows : l'installateur (packaging/installateur.iss) l'emballe dans
  Mes-outils-Setup.exe (packaging/construire.ps1) ;
- Linux : packaging/construire_linux.sh en fait Mes-outils-x86_64.AppImage.
"""
import json
import os
import re
import sys

WINDOWS = sys.platform == "win32"

RACINE = os.path.abspath(os.path.join(SPECPATH, ".."))
OUTIL = os.path.join(RACINE, "outil")
TRAVAIL = os.path.join(RACINE, "build")
os.makedirs(TRAVAIL, exist_ok=True)

# Les modules de « Mes outils » : chargés par leur nom (routes /api/<nom>/…),
# PyInstaller ne peut pas les deviner. La liste sert aussi de liste blanche
# au serveur (hub.modules_connus).
# icone_linux : utilisé par la bulle seulement, pas de routes.
MODULES = sorted(n[:-3] for n in os.listdir(OUTIL)
                 if n.endswith(".py") and n not in ("hub.py", "bulle.py", "icone_linux.py"))
LISTE = os.path.join(TRAVAIL, "modules.json")
with open(LISTE, "w", encoding="utf-8") as f:
    json.dump(MODULES, f)

# Version affichée dans les propriétés du programme (clic droit > Propriétés).
with open(os.path.join(OUTIL, "config.py"), encoding="utf-8") as f:
    VERSION = re.search(r'^VERSION = "([\d.]+)"', f.read(), re.M).group(1)
NUMEROS = tuple(int(x) for x in VERSION.split(".")) + (0,) * (4 - len(VERSION.split(".")))
FICHIER_VERSION = os.path.join(TRAVAIL, "version.txt")
with open(FICHIER_VERSION, "w", encoding="utf-8") as f:
    f.write(f"""VSVersionInfo(
  ffi=FixedFileInfo(filevers={NUMEROS}, prodvers={NUMEROS}),
  kids=[StringFileInfo([StringTable('040C04B0', [
    StringStruct('CompanyName', 'Mes outils'),
    StringStruct('FileDescription', 'Mes outils - tableau de bord'),
    StringStruct('FileVersion', '{VERSION}'),
    StringStruct('InternalName', 'Mes outils'),
    StringStruct('LegalCopyright', 'Licence MIT'),
    StringStruct('OriginalFilename', 'Mes outils.exe'),
    StringStruct('ProductName', 'Mes outils'),
    StringStruct('ProductVersion', '{VERSION}')])]),
    VarFileInfo([VarStruct('Translation', [1036, 1200])])])
""")

# Toute la bibliothèque standard de Python : un script externe chargé par
# « Mes outils » (ex. le gadget Serveurs Odoo) peut en avoir besoin.
import importlib.util
SANS = {"idlelib", "turtledemo", "turtle", "test", "ensurepip", "lib2to3", "pydoc_data", "venv", "distutils", "this", "antigravity"}
STANDARD = sorted(n for n in sys.stdlib_module_names
                  if not n.startswith("_") and n not in SANS and importlib.util.find_spec(n) is not None)

ICONE = os.path.join(OUTIL, "mes_outils.ico")
ICONE_PNG = os.path.join(OUTIL, "mes_outils.png")

# Linux : icône de la zone de notification (jeepney, D-Bus en pur Python) et
# trousseau du bureau (secretstorage) ; facultatives, prises si installées.
# PIL._tkinter_finder : ImageTk (dessin de la bulle) le charge à la volée,
# PyInstaller ne le voit pas sous Linux.
EN_PLUS = ["icone_linux", "PIL.ImageTk", "PIL._tkinter_finder"]
if not WINDOWS:
    from PyInstaller.utils.hooks import collect_submodules
    for paquet in ("jeepney", "secretstorage"):
        if importlib.util.find_spec(paquet) is not None:
            EN_PLUS += collect_submodules(paquet, filter=lambda nom: ".tests" not in nom and not nom.endswith(".trio"))

a = Analysis(
    [os.path.join(OUTIL, "bulle.py")],
    pathex=[OUTIL],
    datas=[
        (os.path.join(OUTIL, "hub.html"), "."),
        (os.path.join(OUTIL, "web"), "web"),
        (ICONE, "."),
        (ICONE_PNG, "."),
        (os.path.join(RACINE, "outils.exemple.json"), "."),
        (LISTE, "."),
    ],
    hiddenimports=MODULES + STANDARD + EN_PLUS,
    excludes=sorted(SANS) + ["numpy", "IPython", "matplotlib"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Mes outils",
    icon=ICONE if WINDOWS else None,               # Linux : icône dans l'AppImage
    version=FICHIER_VERSION if WINDOWS else None,  # propriétés du programme (Windows)
    console=False,      # pas de fenêtre noire
    upx=False,          # UPX déclenche souvent les antivirus
)
coll = COLLECT(exe, a.binaries, a.datas, name="Mes outils", upx=False)
