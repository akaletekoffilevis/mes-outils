#!/usr/bin/env bash
# Construit dist/Mes-outils-x86_64.AppImage : le programme (PyInstaller, un
# dossier) puis l'AppImage (appimagetool). Utilisé à la main et par GitHub
# Actions (Ubuntu 22.04 : l'AppImage marche aussi sur les Ubuntu plus récents).
#   bash packaging/construire_linux.sh
# Prérequis (seulement pour construire) : Python 3.10+ avec tkinter,
#   pip install -r requirements.txt pyinstaller
# appimagetool est téléchargé s'il n'est pas trouvé (variable APPIMAGETOOL
# pour en donner un autre).
set -euo pipefail

PYTHON="${PYTHON:-python3}"
racine="$(cd "$(dirname "$0")/.." && pwd)"
cd "$racine"

version="$(sed -n 's/^VERSION = "\([0-9.]*\)".*/\1/p' outil/config.py)"
echo "Mes outils $version"

# 1. Le programme : dist/Mes outils/Mes outils
rm -rf dist build
"$PYTHON" -m PyInstaller packaging/mes_outils.spec --noconfirm --distpath dist --workpath build/pyinstaller

# 2. Le dossier de l'AppImage
appdir="build/AppDir"
mkdir -p "$appdir/usr/lib"
cp -a "dist/Mes outils" "$appdir/usr/lib/mes-outils"
cp outil/mes_outils.png "$appdir/mes-outils.png"
ln -sf mes-outils.png "$appdir/.DirIcon"

cat > "$appdir/AppRun" <<'FIN'
#!/bin/sh
# Lance Mes outils depuis l'AppImage ($APPIMAGE : le fichier .AppImage lui-même).
ICI="$(dirname "$(readlink -f "$0")")"
exec "$ICI/usr/lib/mes-outils/Mes outils" "$@"
FIN
chmod 755 "$appdir/AppRun"

cat > "$appdir/mes-outils.desktop" <<FIN
[Desktop Entry]
Type=Application
Name=Mes outils
GenericName=Tableau de bord
GenericName[en]=Dashboard
Comment=Tableau de bord : outils, mails, agenda, notes, projets
Comment[en]=Dashboard: tools, mail, calendar, notes, projects
Exec=mes-outils
Icon=mes-outils
Terminal=false
Categories=Utility;Office;
StartupWMClass=mes-outils
X-AppImage-Version=$version
FIN

# 3. appimagetool (version « continuous » : moteur statique, l'AppImage
#    démarre aussi sans libfuse2, comme sur Ubuntu 24.04)
outil="${APPIMAGETOOL:-$(command -v appimagetool || true)}"
if [ -z "$outil" ]; then
  outil="build/appimagetool-x86_64.AppImage"
  curl -fsSL -o "$outil" "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"
  chmod 755 "$outil"
fi

# Sans FUSE (conteneur, GitHub Actions…), appimagetool se décompresse et tourne quand même.
APPIMAGE_EXTRACT_AND_RUN=1 ARCH=x86_64 "$outil" --no-appstream "$appdir" "dist/Mes-outils-x86_64.AppImage"
chmod 755 "dist/Mes-outils-x86_64.AppImage"

taille="$(du -m "dist/Mes-outils-x86_64.AppImage" | cut -f1)"
echo "Prêt : $racine/dist/Mes-outils-x86_64.AppImage ($taille Mo)"
