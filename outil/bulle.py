# -*- coding: utf-8 -*-
"""La bulle « Mes outils » : flotte sur l'écran, sans bouton dans la barre des
tâches.

- clic : ouvre le tableau de bord (ou le ramène devant s'il est déjà ouvert) ;
- glisser : la déplace, la position est retenue ;
- clic droit : accès direct aux onglets, outils, serveurs (projets et Odoo),
  extraits, presse-papiers, chrono, Masquer, Quitter ;
- pastille verte : nombre de serveurs en marche (projets et Odoo) ;
- pastille corail : mails non lus ; pastille rouge : tests GitHub en échec ;
- un peu transparente au repos, pleine au survol.

Elle fait aussi tourner le petit serveur du tableau de bord (hub.py) : un seul
programme, invisible, suffit.
"""
import ctypes
import json
import os
import re
import sys
import threading
import tkinter as tk
from ctypes import wintypes
from http.server import ThreadingHTTPServer
from tkinter import messagebox

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hub  # noqa: E402

FICHIER_POSITION = hub.config.FICHIER_BULLE
TITRE_TABLEAU = "Mes outils"          # titre de la page du tableau de bord
CLE = "#010203"                       # couleur rendue transparente autour de la bulle
TAILLE = 64                           # diamètre à 100 % d'affichage
OPACITE_REPOS, OPACITE_SURVOL = 0.62, 1.0
user32 = ctypes.windll.user32

# Textes de la bulle en anglais (langue choisie dans les Réglages).
ANGLAIS = {
    "Ouvrir le tableau de bord": "Open the dashboard", "Note rapide": "Quick note", "Mails": "Mail",
    "non lus": "unread", "Agenda": "Calendar", "Notes": "Notes", "Mots de passe": "Passwords",
    "Projets": "Projects", "GitHub": "GitHub", "en échec": "failing", "Serveurs locaux": "Local servers",
    "Serveurs Odoo": "Odoo servers", "Ouvrir": "Open", "Arrêter": "Stop", "Démarrer": "Start",
    "Extraits": "Snippets", "Presse-papiers": "Clipboard", "(vide)": "(empty)",
    "Arrêter le chrono": "Stop the timer", "Démarrer un chrono…": "Start a timer…",
    "Masquer 15 minutes": "Hide for 15 minutes", "Quitter la bulle": "Quit the bubble",
    "Rappel": "Reminder", "Plus tard": "Later", "OK": "OK", "Pomodoro": "Pomodoro",
    "Quitter la bulle ?\n\nLes serveurs et les outils déjà lancés continuent de tourner.":
        "Quit the bubble?\n\nServers and tools already launched keep running.",
    "Arrêter {nom} ?": "Stop {nom}?", "Base de référence": "Reference database",
    "« {base} » ne doit pas être modifiée.\n\nDémarrer quand même son serveur ?":
        "“{base}” must not be modified.\n\nStart its server anyway?",
    "Arrêter le serveur {base} (port {port}) ?": "Stop the {base} server (port {port})?",
    "Note rapide · 1re ligne = titre · Ctrl + Entrée pour enregistrer": "Quick note · 1st line = title · Ctrl + Enter to save",
    "1re ligne = titre · Ctrl + Entrée pour enregistrer": "1st line = title · Ctrl + Enter to save",
    "Annuler": "Cancel", "Enregistrer": "Save", "Copié : {texte}": "Copied: {texte}",
    "Tâche": "Task", "Relance": "Follow-up", "Facture": "Invoice", "Budget": "Budget", "Document": "Document",
    "Échéance": "Due date", "Réunion": "Meeting", "Tâches": "Tasks", "Contacts": "Contacts",
    "Devis et factures": "Quotes & invoices", "Dépenses": "Expenses",
}


# Applications qui peuvent envoyer des rappels par la bulle (alertes_dues),
# avec le titre de la carte de rappel.
APPS_ALERTES = {"temps": "Pomodoro", "taches": "Tâche", "contacts": "Relance", "factures": "Facture",
                "depenses": "Budget", "documents": "Document", "echeances": "Échéance", "reunions": "Réunion"}


def tr(texte, **valeurs):
    """Le texte dans la langue des Réglages."""
    try:
        anglais = hub.config.langue() == "en"
    except Exception:
        anglais = False
    texte = ANGLAIS.get(texte, texte) if anglais else texte
    return texte.format(**valeurs) if valeurs else texte


def module(nom):
    """Un module facultatif (projets, temps…), ou None s'il manque."""
    try:
        return __import__(nom)
    except Exception as erreur:  # noqa: BLE001
        hub.journal(f"Bulle : module {nom} indisponible ({erreur})")
        return None


# ---------------------------------------------------------------------------
# Une seule bulle à la fois
# ---------------------------------------------------------------------------
_noyau = ctypes.WinDLL("kernel32", use_last_error=True)
_verrou_instance = None


def deja_lancee():
    """Vrai si une bulle tourne déjà. Le verrou reste tenu tant que celle-ci vit."""
    global _verrou_instance
    # Nom connu de l'installateur (AppMutex) ; une copie d'essai sur un autre
    # port (MES_OUTILS_PORT) a son propre verrou.
    nom = "MesOutils.Bulle" if hub.PORT == 8760 else f"MesOutils.Bulle.{hub.PORT}"
    _verrou_instance = _noyau.CreateMutexW(None, False, nom)
    return ctypes.get_last_error() == 183  # ERROR_ALREADY_EXISTS


# ---------------------------------------------------------------------------
# Fenêtre du tableau de bord : la ramener devant, ou l'ouvrir
# ---------------------------------------------------------------------------
def trouver_fenetre(titre):
    trouvee = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def visite(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            longueur = user32.GetWindowTextLengthW(hwnd)
            tampon = ctypes.create_unicode_buffer(longueur + 1)
            user32.GetWindowTextW(hwnd, tampon, longueur + 1)
            if tampon.value == titre:
                trouvee.append(hwnd)
                return False
        return True

    user32.EnumWindows(visite, 0)
    return trouvee[0] if trouvee else None


def ouvrir_tableau(onglet=None):
    """Ramener le tableau de bord devant (ou l'ouvrir), sur un onglet donné."""
    if onglet:
        hub.demander_onglet(onglet)  # la page déjà ouverte le lit d'elle-même
    hwnd = trouver_fenetre(TITRE_TABLEAU)
    if hwnd:
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        user32.SetForegroundWindow(hwnd)
        return
    hub.ouvrir_fenetre_appli(f"http://{hub.HOTE}:{hub.PORT}/" + (f"#{onglet}" if onglet else ""), 1180, 800)


# ---------------------------------------------------------------------------
# Image de la bulle
# ---------------------------------------------------------------------------
def image_bulle(diametre):
    """Bulle ronde, couleur d'accent unie, avec le logo de Mes outils (quatre
    carrés au trait), posée sur la couleur clé : bords nets, sans halo."""
    from PIL import Image, ImageDraw, ImageTk

    s = 4  # sur-échantillonnage
    d = diametre * s
    bulle = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    dessin = ImageDraw.Draw(bulle)
    dessin.ellipse((0, 0, d - 1, d - 1), fill=(91, 91, 214, 255))
    dessin.ellipse((s, s, d - 1 - s, d - 1 - s), outline=(255, 255, 255, 220), width=2 * s)
    # Logo : 2 x 2 carrés arrondis au trait, comme l'icône de l'application.
    cote, ecart, trait = d * 0.17, d * 0.07, max(2, int(d * 0.035))
    debut = (d - (2 * cote + ecart)) / 2
    for ligne in range(2):
        for colonne in range(2):
            x = debut + colonne * (cote + ecart)
            y = debut + ligne * (cote + ecart)
            dessin.rounded_rectangle((x, y, x + cote, y + cote), radius=cote * 0.22,
                                     outline=(255, 255, 255, 255), width=trait)
    bulle = bulle.resize((diametre, diametre), Image.LANCZOS)
    fond = Image.new("RGBA", (diametre, diametre), (1, 2, 3, 255))
    alpha = bulle.split()[3].point(lambda a: 255 if a > 140 else 0)
    fond.paste(bulle.convert("RGB"), (0, 0), alpha)
    return ImageTk.PhotoImage(fond.convert("RGB"))


# Pas d'emoji dans les menus et les cartes de la bulle : texte seul.
_EMOJI = re.compile("[🀀-🫿☀-➿⬀-⯿⌀-⏿■-◿]️?")


def sobre(texte):
    return " ".join(_EMOJI.sub("", str(texte)).split())


class MenuSobre(tk.Menu):
    """Menu dont les libellés perdent leurs emojis (ceux des tuiles, par exemple)."""

    def add_command(self, cnf=None, **kw):
        if "label" in kw:
            kw["label"] = sobre(kw["label"])
        return super().add_command(cnf or {}, **kw)

    def add_cascade(self, cnf=None, **kw):
        if "label" in kw:
            kw["label"] = sobre(kw["label"])
        return super().add_cascade(cnf or {}, **kw)


# ---------------------------------------------------------------------------
# La bulle
# ---------------------------------------------------------------------------
class Bulle:
    def __init__(self):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
        self.racine = r = tk.Tk()
        r.title("Mes outils · bulle")
        r.overrideredirect(True)            # sans bordure, sans barre des tâches
        r.attributes("-topmost", True)
        r.attributes("-transparentcolor", CLE)
        r.attributes("-alpha", OPACITE_REPOS)
        r.configure(bg=CLE)

        self.echelle = r.winfo_fpixels("1i") / 96
        self.d = int(TAILLE * self.echelle)
        marge = int(10 * self.echelle)
        self.largeur = self.d + 2 * marge     # place pour les pastilles des deux côtés
        self.toile = tk.Canvas(r, width=self.largeur, height=self.d + marge, bg=CLE,
                               highlightthickness=0, bd=0, cursor="hand2")
        self.toile.pack()
        self.image = image_bulle(self.d)
        self.toile.create_image(marge, marge, image=self.image, anchor="nw")
        self.marge = marge
        self.pastille = None
        self.nb_marche = None
        self.pastille_mail = None
        self.nb_mails = None
        self.pastille_ci = None
        self.nb_ci = None
        self.serveurs_projets = []
        self.rappels_affiches = {}

        self.toile.bind("<ButtonPress-1>", self.appui)
        self.toile.bind("<B1-Motion>", self.glisse)
        self.toile.bind("<ButtonRelease-1>", self.relache)
        self.toile.bind("<Button-3>", self.menu)
        self.toile.bind("<Enter>", lambda _e: r.attributes("-alpha", OPACITE_SURVOL))
        self.toile.bind("<Leave>", lambda _e: r.attributes("-alpha", OPACITE_REPOS))

        self.placer()
        r.after(50, self.hors_barre_des_taches)
        self.demarrer_tableau()
        self.suivre_serveurs()
        r.after(3000, self.suivre_mails)
        r.after(5000, self.suivre_rappels)
        r.after(10000, self.suivre_ci)
        r.after(1500, self.demarrer_presse_papiers)

    def hors_barre_des_taches(self):
        """Style « fenêtre d'outil » : jamais de bouton dans la barre des
        tâches ni dans Alt+Tab, même si Windows hésite pour une fenêtre sans
        bordure."""
        GWL_EXSTYLE, WS_EX_TOOLWINDOW, WS_EX_APPWINDOW = -20, 0x00000080, 0x00040000
        hwnd = user32.GetParent(self.racine.winfo_id()) or self.racine.winfo_id()
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, (style | WS_EX_TOOLWINDOW) & ~WS_EX_APPWINDOW)
        self.racine.withdraw()
        self.racine.deiconify()  # le nouveau style ne s'applique qu'au réaffichage

    # -- position ----------------------------------------------------------
    def placer(self):
        r = self.racine
        x = y = None
        try:
            with open(FICHIER_POSITION, encoding="utf-8") as f:
                x, y = json.load(f)["position"]
        except (OSError, ValueError, KeyError, TypeError):
            pass
        gauche, haut = user32.GetSystemMetrics(76), user32.GetSystemMetrics(77)
        larg, haute = user32.GetSystemMetrics(78), user32.GetSystemMetrics(79)
        if x is None or not (gauche <= x <= gauche + larg - 40 and haut <= y <= haut + haute - 40):
            x = r.winfo_screenwidth() - self.largeur - int(24 * self.echelle)
            y = int(r.winfo_screenheight() * 0.62)
        r.geometry(f"+{x}+{y}")

    def memoriser(self):
        try:
            with open(FICHIER_POSITION, "w", encoding="utf-8") as f:
                json.dump({"position": [self.racine.winfo_x(), self.racine.winfo_y()]}, f)
        except OSError:
            pass

    # -- clic et glisser ---------------------------------------------------
    def appui(self, e):
        self.depart = (e.x_root, e.y_root, self.racine.winfo_x(), self.racine.winfo_y())
        self.deplacee = False

    def glisse(self, e):
        x0, y0, wx, wy = self.depart
        dx, dy = e.x_root - x0, e.y_root - y0
        if abs(dx) + abs(dy) > 4:
            self.deplacee = True
        if self.deplacee:
            self.racine.geometry(f"+{wx + dx}+{wy + dy}")

    def relache(self, _e):
        if self.deplacee:
            self.memoriser()
        else:
            self.rebond()
            ouvrir_tableau()

    def rebond(self):
        # Petit « plop » : la bulle s'enfonce puis revient.
        self.toile.move("all", 0, 3)
        self.racine.after(90, lambda: self.toile.move("all", 0, -3))

    # -- serveur du tableau de bord -----------------------------------------
    def demarrer_tableau(self):
        if hub.port_ouvert(hub.PORT):
            return  # déjà servi (tableau de bord lancé à part)
        hub.BULLE_ACTIVE = True
        serveur = ThreadingHTTPServer((hub.HOTE, hub.PORT), hub.Gestionnaire)
        threading.Thread(target=serveur.serve_forever, daemon=True).start()
        hub.journal("Démarrage par la bulle sur port %d" % hub.PORT)

    # -- pastille des serveurs Odoo ------------------------------------------
    def suivre_serveurs(self):
        def lire():
            try:
                etats = hub.etats_serveurs()
                nb = sum(1 for s in etats["serveurs"] if s["etat"] == "En marche") if etats["disponible"] else 0
            except Exception:
                nb = 0
            projets = module("projets")
            try:
                self.serveurs_projets = projets.serveurs() if projets else []
            except Exception:
                self.serveurs_projets = []
            nb += sum(1 for s in self.serveurs_projets if s.get("etat") == "marche")
            self.racine.after(0, lambda: self.dessiner_pastille(nb))
        threading.Thread(target=lire, daemon=True).start()
        self.racine.after(6000, self.suivre_serveurs)

    def dessiner_pastille(self, nb):
        if nb == self.nb_marche:
            return
        self.nb_marche = nb
        if self.pastille:
            for element in self.pastille:
                self.toile.delete(element)
            self.pastille = None
        if not nb:
            return
        p = int(22 * self.echelle)
        x1, y1 = self.largeur - p - 1, 0
        self.pastille = (
            self.toile.create_oval(x1, y1, x1 + p, y1 + p, fill="#18b597", outline="#ffffff", width=max(2, int(2 * self.echelle))),
            self.toile.create_text(x1 + p / 2, y1 + p / 2, text=str(nb), fill="#ffffff",
                                   font=("Segoe UI", max(8, int(9 * self.echelle) // 1), "bold")),
        )

    # -- pastille des mails non lus ------------------------------------------
    def suivre_mails(self):
        def lire():
            try:
                b = hub.boite()
                nb = b.non_lus() if b.configuree() else 0
            except Exception:
                nb = 0  # pas d'Internet, mot de passe révoqué… : pas de pastille
            self.racine.after(0, lambda: self.dessiner_pastille_mail(nb))
        threading.Thread(target=lire, daemon=True).start()
        self.racine.after(120000, self.suivre_mails)

    def dessiner_pastille_mail(self, nb):
        if nb == self.nb_mails:
            return
        self.nb_mails = nb
        if self.pastille_mail:
            for element in self.pastille_mail:
                self.toile.delete(element)
            self.pastille_mail = None
        if not nb:
            return
        p = int(22 * self.echelle)
        texte = str(nb) if nb < 100 else "99+"
        largeur = p if nb < 10 else int(p * 1.4)
        self.pastille_mail = (
            self.toile.create_oval(1, 0, 1 + largeur, p, fill="#ff7a59", outline="#ffffff", width=max(2, int(2 * self.echelle))),
            self.toile.create_text(1 + largeur / 2, p / 2, text=texte, fill="#ffffff",
                                   font=("Segoe UI", max(8, int(9 * self.echelle)), "bold")),
        )

    # -- pastille rouge : tests GitHub (Actions) en échec ---------------------
    def suivre_ci(self):
        def lire():
            github = module("github")
            try:
                nb = github.echecs_ci()["nombre"] if github and hasattr(github, "echecs_ci") else 0
            except Exception:
                nb = 0  # pas connecté, hors ligne… : pas de pastille
            self.racine.after(0, lambda: self.dessiner_pastille_ci(nb))
        threading.Thread(target=lire, daemon=True).start()
        self.racine.after(5 * 60 * 1000, self.suivre_ci)

    def dessiner_pastille_ci(self, nb):
        if nb == self.nb_ci:
            return
        self.nb_ci = nb
        if self.pastille_ci:
            for element in self.pastille_ci:
                self.toile.delete(element)
            self.pastille_ci = None
        if not nb:
            return
        p = int(20 * self.echelle)
        y1 = self.d + self.marge - p - 1
        self.pastille_ci = (
            self.toile.create_oval(1, y1, 1 + p, y1 + p, fill="#e5484d", outline="#ffffff", width=max(2, int(2 * self.echelle))),
            self.toile.create_text(1 + p / 2, y1 + p / 2, text=str(nb) if nb < 10 else "9+", fill="#ffffff",
                                   font=("Segoe UI", max(7, int(8 * self.echelle)), "bold")),
        )

    # -- historique du presse-papiers (en mémoire seulement) -----------------
    def demarrer_presse_papiers(self):
        presse_papiers = module("presse_papiers")
        if presse_papiers:
            try:
                presse_papiers.demarrer_surveillance()
            except Exception as erreur:  # noqa: BLE001
                hub.journal(f"Presse-papiers : {erreur}")

    # -- rappels des notes et de l'agenda ---------------------------------
    def suivre_rappels(self):
        try:
            for rappel in hub.donnees.rappels_dus():
                cle = (rappel["genre"], rappel["id"])
                if cle not in self.rappels_affiches:
                    self.afficher_rappel(rappel)
        except Exception as erreur:  # noqa: BLE001
            hub.journal(f"Rappels : {erreur}")
        # Rappels des applications (fin de Pomodoro, tâche, relance, échéance…) :
        # chaque application active qui a alertes_dues(). Les applications
        # connues d'abord (ordre fixe), puis toute nouvelle application.
        try:
            noms = list(APPS_ALERTES) + sorted(hub.modules_connus() - set(APPS_ALERTES) - {"config"})
        except Exception:  # noqa: BLE001
            noms = list(APPS_ALERTES)
        for nom in noms:
            try:
                if not hub.config.app_active(nom):
                    continue
                mod = module(nom)
                if not mod or not hasattr(mod, "alertes_dues"):
                    continue
                for alerte in mod.alertes_dues():
                    if (nom, alerte["id"]) not in self.rappels_affiches:
                        self.afficher_rappel({"genre": nom, "id": alerte["id"], "titre": alerte.get("titre", ""),
                                              "detail": alerte.get("detail")})
            except Exception as erreur:  # noqa: BLE001
                hub.journal(f"Rappels de {nom} : {erreur}")
        self.racine.after(30000, self.suivre_rappels)

    def afficher_rappel(self, rappel):
        """Une petite carte à côté de la bulle, qui reste jusqu'à ce qu'on
        réponde : Ouvrir, Plus tard (10 min) ou OK."""
        cle = (rappel["genre"], rappel["id"])
        f = tk.Toplevel(self.racine)
        f.overrideredirect(True)
        f.attributes("-topmost", True)
        f.configure(bg="#5b5bd6")
        self.rappels_affiches[cle] = f
        cadre = tk.Frame(f, bg="#ffffff", padx=16, pady=12)
        cadre.pack(padx=2, pady=2)
        entete = tr(APPS_ALERTES.get(rappel["genre"], "Rappel"))
        tk.Label(cadre, text=entete.upper(), bg="#ffffff", fg="#5f5f68",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(cadre, text=sobre(rappel["titre"]), bg="#ffffff", fg="#18181b", font=("Segoe UI", 12, "bold"),
                 wraplength=int(300 * self.echelle), justify="left").pack(anchor="w", pady=(2, 0))
        if rappel.get("detail"):
            tk.Label(cadre, text=rappel["detail"], bg="#ffffff", fg="#6b6790", font=("Segoe UI", 10),
                     wraplength=int(300 * self.echelle), justify="left").pack(anchor="w", pady=(2, 0))
        boutons = tk.Frame(cadre, bg="#ffffff")
        boutons.pack(anchor="e", pady=(10, 0))

        def fin(action):
            try:
                if rappel["genre"] in APPS_ALERTES:
                    mod = module(rappel["genre"])
                    if mod and hasattr(mod, "marquer_alerte"):
                        mod.marquer_alerte(rappel["id"])
                elif action == "plus_tard":
                    hub.donnees.marquer_rappel(rappel["genre"], rappel["id"], reporter_minutes=10)
                else:
                    hub.donnees.marquer_rappel(rappel["genre"], rappel["id"])
            finally:
                self.rappels_affiches.pop(cle, None)
                f.destroy()
            if action == "ouvrir":
                ouvrir_tableau(rappel["genre"])

        choix = (("Plus tard", "plus_tard", "#f2f2f4", "#6b6790"),
                 ("OK", "ok", "#f2f2f4", "#1f1a3a"),
                 ("Ouvrir", "ouvrir", "#5b5bd6", "#ffffff"))
        if rappel["genre"] in APPS_ALERTES:
            choix = choix[1:]  # rappel d'une application : pas de report
        for texte, action, fond, encre in choix:
            tk.Button(boutons, text=tr(texte), command=lambda a=action: fin(a), bg=fond, fg=encre, activebackground=fond,
                      relief="flat", bd=0, padx=12, pady=4, font=("Segoe UI", 10, "bold"), cursor="hand2").pack(side="left", padx=(6, 0))

        # À gauche de la bulle (ou à droite si elle est collée au bord gauche),
        # les cartes s'empilant vers le haut.
        f.update_idletasks()
        rang = len(self.rappels_affiches) - 1
        x = self.racine.winfo_x() - f.winfo_reqwidth() - int(8 * self.echelle)
        if x < 0:
            x = self.racine.winfo_x() + self.largeur + int(8 * self.echelle)
        y = max(0, self.racine.winfo_y() - rang * (f.winfo_reqheight() + 8))
        f.geometry(f"+{x}+{y}")
        try:
            import winsound
            winsound.MessageBeep(0x40)  # son « information » de Windows
        except Exception:
            pass
        self.secouer()

    def secouer(self, n=6):
        """La bulle frétille pour attirer l'œil."""
        if n <= 0:
            return
        self.toile.move("all", 3 if n % 2 else -3, 0)
        self.racine.after(70, lambda: self.secouer(n - 1))

    # -- note rapide ---------------------------------------------------------
    def note_rapide(self):
        f = tk.Toplevel(self.racine)
        f.title("Note rapide")
        f.attributes("-topmost", True)
        f.attributes("-toolwindow", True)   # pas de bouton dans la barre des tâches
        f.configure(bg="#fff4c2", padx=12, pady=10)
        f.resizable(False, False)
        tk.Label(f, text=tr("Note rapide"), bg="#fff4c2", fg="#6b6790", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        zone = tk.Text(f, width=40, height=7, wrap="word", relief="flat", bg="#fffbe6", fg="#18181b",
                       font=("Segoe UI", 11), padx=8, pady=6, insertbackground="#5b5bd6")
        zone.pack(pady=(4, 8))
        aide = tk.Label(f, text=tr("1re ligne = titre · Ctrl + Entrée pour enregistrer"), bg="#fff4c2", fg="#a7a3bd", font=("Segoe UI", 8))
        aide.pack(anchor="w")

        def enregistrer(_e=None):
            texte = zone.get("1.0", "end").strip()
            if not texte:
                f.destroy()
                return "break"
            lignes = texte.split("\n")
            titre = lignes[0][:80] if len(lignes) > 1 or len(lignes[0]) <= 60 else ""
            corps = "\n".join(lignes[1:]).strip() if titre else texte
            hub.donnees.enregistrer("notes", {"genre": "texte", "titre": titre, "texte": corps, "couleur": "#fff4c2"})
            f.destroy()
            self.secouer(4)
            return "break"

        boutons = tk.Frame(f, bg="#fff4c2")
        boutons.pack(anchor="e", pady=(6, 0))
        tk.Button(boutons, text=tr("Annuler"), command=f.destroy, relief="flat", bg="#fff4c2", fg="#6b6790",
                  font=("Segoe UI", 10), cursor="hand2").pack(side="left", padx=4)
        tk.Button(boutons, text=tr("Enregistrer"), command=enregistrer, relief="flat", bg="#5b5bd6", fg="#ffffff",
                  activebackground="#4c4cc4", activeforeground="#ffffff", padx=12, pady=3,
                  font=("Segoe UI", 10, "bold"), cursor="hand2").pack(side="left")
        zone.bind("<Control-Return>", enregistrer)
        f.bind("<Escape>", lambda _e: f.destroy())
        f.update_idletasks()
        x = max(0, self.racine.winfo_x() - f.winfo_reqwidth() - 10)
        y = max(0, self.racine.winfo_y() - f.winfo_reqheight() + self.largeur)
        f.geometry(f"+{x}+{y}")
        f.focus_force()
        zone.focus_set()

    # -- menu clic droit ---------------------------------------------------
    # -- menu clic droit ---------------------------------------------------
    def menu(self, e):
        police = ("Segoe UI", 10)
        m = MenuSobre(self.racine, tearoff=False, font=police)
        m.add_command(label="🧰  " + tr("Ouvrir le tableau de bord"), command=ouvrir_tableau)
        m.add_command(label="📝  " + tr("Note rapide"), command=self.note_rapide)
        mails = f"  ({self.nb_mails} {tr('non lus')})" if self.nb_mails else ""
        # Les applications actives seulement (page Applications).
        actif = hub.config.app_active
        if actif("mails"):
            m.add_command(label=f"{tr('Mails')}{mails}", command=lambda: ouvrir_tableau("mails"))
        for nom, libelle in (("agenda", "Agenda"), ("taches", "Tâches"), ("notes", "Notes"), ("motsdepasse", "Mots de passe"),
                             ("contacts", "Contacts"), ("factures", "Devis et factures"), ("depenses", "Dépenses")):
            if actif(nom):
                m.add_command(label=tr(libelle), command=lambda n=nom: ouvrir_tableau(n))
        m.add_separator()
        if actif("projets"):
            m.add_command(label=tr("Projets"), command=lambda: ouvrir_tableau("projets"))
        ci = f"  ({self.nb_ci} {tr('en échec')})" if self.nb_ci else ""
        if actif("github"):
            m.add_command(label=f"GitHub{ci}", command=lambda: ouvrir_tableau("github"))

        # Serveurs : ceux des projets (derniers états connus, relus toutes
        # les 6 s) puis ceux du gadget Odoo. Le menu s'ouvre sans attendre.
        sous = MenuSobre(m, tearoff=False, font=police)
        for s in self.serveurs_projets:
            nom = f"{s.get('projet', '')} · {s.get('nom', '')}"
            if s.get("etat") in ("marche", "demarrage"):
                rond = "🟢" if s.get("etat") == "marche" else "🟡"
                sous.add_command(label=f"{rond}  {tr('Ouvrir')} {nom}",
                                 command=lambda s=s: self.action_projet(s, "ouvrir"))
                sous.add_command(label=f"      {tr('Arrêter')} {nom}", command=lambda s=s: self.action_projet(s, "arreter"))
            else:
                sous.add_command(label=f"⚪  {tr('Démarrer')} {nom}", command=lambda s=s: self.action_projet(s, "demarrer"))
        etats = hub._cache_etats["valeur"] or {"disponible": False}
        if etats.get("disponible") and etats["serveurs"]:
            if self.serveurs_projets:
                sous.add_separator()
            for s in etats["serveurs"]:
                marche = s["etat"] in ("En marche", "Démarrage…")
                rond = "🟢" if s["etat"] == "En marche" else "🟡" if marche else "⚪"
                if marche:
                    sous.add_command(label=f"{rond}  {tr('Ouvrir')} 🐘 {s['base']}",
                                     command=lambda s=s: self.en_fond(hub.action_serveur, "ouvrir", s["port"]))
                    sous.add_command(label=f"      {tr('Arrêter')} 🐘 {s['base']}", command=lambda s=s: self.arreter(s))
                else:
                    sous.add_command(label=f"{rond}  {tr('Démarrer')} 🐘 {s['base']}", command=lambda s=s: self.demarrer(s))
        if sous.index("end") is not None and actif("serveurs"):
            m.add_cascade(label="🖥️  " + tr("Serveurs locaux"), menu=sous)

        # Chrono (onglet Temps)
        temps = module("temps") if actif("temps") else None
        try:
            chrono = temps.etat() if temps else {"en_cours": False}
        except Exception:
            chrono = {"en_cours": False}
        if chrono.get("en_cours"):
            minutes = int(chrono.get("secondes", 0)) // 60
            m.add_command(label=f"⏹️  {tr('Arrêter le chrono')} ({chrono.get('projet', '')}, {minutes} min)",
                          command=lambda: self.en_fond(temps.arreter))
        elif temps:
            m.add_command(label="⏱️  " + tr("Démarrer un chrono…"), command=lambda: ouvrir_tableau("temps"))

        # Extraits favoris et presse-papiers : un clic = copié.
        extraits = module("extraits") if actif("extraits") else None
        try:
            favoris = extraits.lister()[:10] if extraits else []
        except Exception:
            favoris = []
        if favoris:
            sous_e = MenuSobre(m, tearoff=False, font=police)
            for x in favoris:
                sous_e.add_command(label=self.court(x.get("titre") or x.get("contenu", "")),
                                   command=lambda x=x: self.en_fond(extraits.copier, x["id"]))
            m.add_cascade(label="✂️  " + tr("Extraits"), menu=sous_e)
        presse_papiers = module("presse_papiers") if actif("presse_papiers") else None
        try:
            historique = presse_papiers.lister()[:10] if presse_papiers else []
        except Exception:
            historique = []
        if presse_papiers:
            sous_p = MenuSobre(m, tearoff=False, font=police)
            for x in historique:
                sous_p.add_command(label=("📌 " if x.get("epingle") else "") + self.court(x.get("texte", "")),
                                   command=lambda x=x: self.en_fond(presse_papiers.recopier, x["id"]))
            if not historique:
                sous_p.add_command(label=tr("(vide)"), state="disabled")
            m.add_cascade(label="📋  " + tr("Presse-papiers"), menu=sous_p)

        try:
            outils = hub.lire_outils()["outils"]
        except Exception:
            outils = []
        if outils:
            m.add_separator()
        for outil in outils:
            m.add_command(label=f"{outil.get('emoji', '•')}  {outil.get('nom', '')}",
                          command=lambda o=outil: self.en_fond(hub.lancer_outil, o["id"]))
        m.add_separator()
        m.add_command(label="🙈  " + tr("Masquer 15 minutes"), command=self.masquer)
        m.add_command(label="🚪  " + tr("Quitter la bulle"), command=self.quitter)
        try:
            m.tk_popup(e.x_root, e.y_root)
        finally:
            m.grab_release()

    @staticmethod
    def court(texte, n=48):
        """Une ligne courte pour un menu (sans retour à la ligne)."""
        texte = " ".join(str(texte).split())
        return texte if len(texte) <= n else texte[:n - 1] + "…"

    def action_projet(self, s, action):
        projets = module("projets")
        if not projets:
            return
        if action == "arreter" and not messagebox.askyesno(
                tr("Arrêter"), tr("Arrêter {nom} ?", nom=f"{s.get('projet', '')} · {s.get('nom', '')}"),
                default="no", parent=self.racine):
            return
        self.en_fond(projets.action_commande, s["projet_id"], s["id"], action)

    def en_fond(self, fonction, *args):
        def tache():
            try:
                fonction(*args)
            except Exception as erreur:  # noqa: BLE001
                self.racine.after(0, lambda: messagebox.showerror("Mes outils", str(erreur), parent=self.racine))
        threading.Thread(target=tache, daemon=True).start()

    def demarrer(self, s):
        if s["reference"] and not messagebox.askyesno(
                tr("Base de référence"),
                tr("« {base} » ne doit pas être modifiée.\n\nDémarrer quand même son serveur ?", base=s["base"]),
                icon="warning", default="no", parent=self.racine):
            return
        self.en_fond(hub.action_serveur, "demarrer", s["port"])

    def arreter(self, s):
        if messagebox.askyesno(tr("Arrêter"), tr("Arrêter le serveur {base} (port {port}) ?", base=s["base"], port=s["port"]),
                               default="no", parent=self.racine):
            self.en_fond(hub.action_serveur, "arreter", s["port"])

    def masquer(self):
        self.racine.withdraw()
        self.racine.after(15 * 60 * 1000, self.racine.deiconify)

    def quitter(self):
        if messagebox.askyesno("Mes outils", tr("Quitter la bulle ?\n\nLes serveurs et les outils déjà lancés continuent de tourner."),
                               parent=self.racine):
            self.memoriser()
            self.racine.destroy()


def main():
    if deja_lancee():
        # Raccourci relancé alors que la bulle est là : ouvrir le tableau de bord.
        ouvrir_tableau()
        return
    # Premier lancement du programme installé : reprise des réglages et des
    # données d'une ancienne copie « code source » (copiés, pas déplacés).
    try:
        reprise = hub.config.premier_lancement()
        if reprise:
            hub.journal(f"Données reprises depuis {reprise}")
    except Exception as erreur:  # noqa: BLE001
        hub.journal(f"Reprise des anciennes données impossible : {erreur}")
    Bulle().racine.mainloop()


if __name__ == "__main__":
    main()
