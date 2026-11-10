# -*- coding: utf-8 -*-
"""Génère outil/web/icones.js : icônes Lucide (ISC) + table emoji -> icône."""
import json
import os
import re
import sys

LUCIDE = sys.argv[1]          # dossier package/ de lucide-static
SORTIE = sys.argv[2]          # outil/web/icones.js

# Emoji -> nom d'icône Lucide ; None = décoratif, retiré.
TABLE = {
    "😕": None, "✨": None, "🎉": None, "😉": None, "👍": None, "👋": None, "🌴": None, "😟": None, "😐": None,
    "🙂": None, "💪": None, "🙏": None, "🎈": None, "😴": None, "🍅": "timer",
    "✅": "check", "✓": "check", "☑": "list-checks", "📋": "clipboard", "✏": "pencil", "✎": "pencil", "✍": "pencil",
    "🗑": "trash-2", "🔒": "lock", "🔐": "lock", "🔓": "lock-open", "🗝": "key-round", "🔑": "key-round",
    "⏳": "loader", "⌛": "loader", "❌": "circle-x", "🔄": "refresh-cw", "🔁": "arrow-left-right",
    "⚠": "triangle-alert", "🚧": "triangle-alert", "📦": "package", "💾": "hard-drive", "⬇": "arrow-down",
    "⬆": "arrow-up", "🌐": "globe", "🌍": "globe", "▶": "play", "💻": "laptop", "↩": "undo-2", "↪": "corner-down-right",
    "🚀": "rocket", "🧩": "puzzle", "✕": "x", "📅": "calendar", "🗓": "calendar", "⚙": "settings",
    "✉": "mail", "📬": "mail", "📨": "send", "📤": "send", "📥": "inbox", "🔍": "search", "🔎": "search",
    "📁": "folder", "📂": "folder-open", "🗂": "folders", "⏱": "timer", "🎲": "dices", "🔌": "plug", "💡": "lightbulb",
    "📌": "pin", "📍": "pin", "🐳": "container", "⛔": "octagon-x", "🌙": "moon", "💤": "moon", "☀": "sun",
    "🌗": "sun-moon", "🐙": "git-branch", "🌿": "git-branch", "✂": "scissors", "⏹": "square", "■": "square",
    "⏸": "pause", "🧰": "toolbox", "🧾": "receipt", "🐘": "database", "🗄": "database", "📝": "notebook-pen",
    "🗒": "sticky-note", "📄": "file", "🧹": "eraser", "👤": "user", "👁": "eye", "👀": "eye", "🙈": "eye-off",
    "🖥": "monitor", "🧪": "flask-conical", "☕": "coffee", "📜": "scroll-text", "☰": "scroll-text",
    "⌨": "terminal", "↗": "external-link", "✋": "hand", "🤔": "circle-help", "❔": "circle-help", "🐛": "bug",
    "➡": "forward", "🖼": "image", "📡": "radio-tower", "🚪": "log-out", "🎨": "palette", "🛡": "shield",
    "⚡": "zap", "💽": "hard-drive", "➖": "minus", "🔀": "git-pull-request", "⏰": "alarm-clock", "🎁": "download",
    "📱": "smartphone", "🛠": "wrench", "🔧": "wrench", "📊": "chart-column", "📈": "trending-up",
    "💼": "briefcase", "🧮": "calculator", "🎯": "target", "🧠": "brain", "📚": "book-open", "📖": "book-open",
    "➕": "plus", "🏠": "house", "🎫": "ticket", "🔤": "type", "🆔": "id-card", "🔗": "link", "🧬": "hash",
    "🗜": "minimize-2", "🕒": "clock", "🕘": "history", "🧊": "box", "⏭": "skip-forward", "⭐": "star",
    "👥": "users", "💬": "message-square", "🙋": "user", "📎": "paperclip", "🐍": "code", "▶️": "play",
    # Types de projets (projets.py)
    "🎸": "code", "⚛": "atom", "💚": "code", "🅰": "code", "🐈": "server", "🧱": "layers", "🐹": "code",
    "🦀": "cog", "🔷": "hexagon", "🐦": "smartphone", "💎": "gem", "🟢": "circle", "🟡": "circle", "⚪": "circle",
}
# Icônes de plus pour les tuiles et l'interface (sans emoji d'origine).
EN_PLUS = ["app-window", "layout-grid", "info", "circle-check", "circle-alert", "loader-circle", "chevron-right", "chevron-down", "ellipsis",
           "server", "files", "file-code", "code", "kanban", "notebook", "music", "camera", "shopping-cart",
           "cloud", "gamepad-2", "graduation-cap", "heart", "home", "printer", "video", "github"]

noms = sorted({n for n in TABLE.values() if n} | set(EN_PLUS))
icones, manquantes = {}, []
for nom in noms:
    chemin = os.path.join(LUCIDE, "icons", nom + ".svg")
    if not os.path.isfile(chemin):
        manquantes.append(nom)
        continue
    svg = open(chemin, encoding="utf-8").read()
    corps = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S).group(1)
    corps = re.sub(r"<!--.*?-->", "", corps, flags=re.S)
    icones[nom] = re.sub(r"\s+", " ", corps).strip()
if manquantes:
    print("absentes de Lucide (ignorées) :", manquantes)
table = {k: (v if (v is None or v in icones) else None) for k, v in TABLE.items()}

js = f'''"use strict";
/* Icônes au trait de « Mes outils » : un sous-ensemble de Lucide
   (https://lucide.dev, licence ISC, © Lucide Contributors), intégré pour
   marcher sans Internet. Fichier généré : ne pas modifier à la main.

   - icone("folder") : un élément <svg> (taille 1em, couleur du texte) ;
   - les emojis écrits dans l'interface sont remplacés par l'icône
     correspondante (EMOJI_ICONE), ou retirés s'ils n'étaient que décoratifs,
     partout dans la page (voir hub.html, nettoyerEmojis). */
window.ICONES = {json.dumps(icones, ensure_ascii=False, indent=0)};
window.EMOJI_ICONE = {json.dumps(table, ensure_ascii=False, indent=0)};
'''
open(SORTIE, "w", encoding="utf-8").write(js)
print(len(icones), "icônes,", len(table), "emojis dans la table ->", SORTIE, f"({len(js) // 1024} Ko)")
