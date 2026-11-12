# -*- coding: utf-8 -*-
"""« Mes outils » : le tableau de bord de mes outils personnels.

Un petit serveur local (127.0.0.1, ce PC seulement) et une page affichée dans
une fenêtre en mode application (Edge sous Windows, Chrome ou Chromium sous
Linux, voir systeme.py). Les outils sont décrits dans
outils.json (créé depuis outils.exemple.json au premier lancement) ; les
serveurs Odoo sont ceux d'un gadget « Serveurs Odoo » externe, facultatif
(chemin dans outils.json, clé serveurs_odoo.gadget), dont on réutilise le
code tel quel.
"""
import importlib
import importlib.util
import json
import os
import re
import shlex
import socket
import sys
import threading
import time
import traceback
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config  # noqa: E402  (outils.json et dossier donnees)
import donnees  # noqa: E402  (notes et agenda)
import systeme  # noqa: E402  (tout ce qui dépend de Windows ou de Linux)

# MES_OUTILS_PORT : un autre port (essais, seconde copie à côté de la vraie).
HOTE, PORT = "127.0.0.1", int(os.environ.get("MES_OUTILS_PORT") or 8760)
ICI = config.ICI
RACINE = config.RACINE
PAGE = os.path.join(ICI, "hub.html")
JOURNAL = config.JOURNAL

# Vrai quand le serveur tourne dans la bulle (bulle.py) : fermer la fenêtre
# du tableau de bord ne doit alors rien arrêter.
BULLE_ACTIVE = False


def journal(message):
    os.makedirs(os.path.dirname(JOURNAL), exist_ok=True)
    with open(JOURNAL, "a", encoding="utf-8") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + message + "\n")


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
def lire_outils():
    """outils.json (voir config.py)."""
    return config.lire()


def ecrire_outils(contenu):
    config.ecrire(contenu)


# ---------------------------------------------------------------------------
# Modules : chaque fichier outil/<nom>.py qui définit ROUTES = {"action":
# fonction(donnees)} répond tout seul sur POST /api/<nom>/<action>.
# ---------------------------------------------------------------------------
MODULE_VALIDE = re.compile(r"^[a-z][a-z0-9_]{1,30}$")


def modules_connus():
    """Les modules de « Mes outils » (jamais un module quelconque de Python).
    Depuis le code source : les fichiers outil/*.py ; dans le programme
    installé : la liste écrite au moment de la construction (modules.json)."""
    liste = os.path.join(ICI, "modules.json")
    if config.GELE and os.path.isfile(liste):
        with open(liste, encoding="utf-8") as f:
            return set(json.load(f))
    return {n[:-3] for n in os.listdir(ICI) if n.endswith(".py")} - {"hub", "bulle"}


def routes_module(nom):
    if not MODULE_VALIDE.match(nom) or nom not in modules_connus():
        return None
    routes = getattr(importlib.import_module(nom), "ROUTES", None)
    return routes if isinstance(routes, dict) else None


def onglets_web():
    """Les fichiers des onglets (outil/web/*.js), chargés par la page."""
    dossier = os.path.join(ICI, "web")
    # i18n.js et icones.js sont chargés à part, en premier (hub.html).
    return sorted(n for n in os.listdir(dossier) if n.endswith(".js") and n not in ("i18n.js", "icones.js"))


# ---------------------------------------------------------------------------
# Serveurs Odoo : le module du gadget, chargé depuis son dossier
# ---------------------------------------------------------------------------
_gadget = None


def gadget():
    """Le module gestion_serveurs.py, ou None s'il est introuvable."""
    global _gadget
    if _gadget is None:
        chemin = (lire_outils().get("serveurs_odoo") or {}).get("gadget") or ""
        if not chemin or not os.path.exists(chemin):
            return None
        spec = importlib.util.spec_from_file_location("gestion_serveurs", chemin)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _gadget = module
    return _gadget


_cache_etats = {"heure": 0, "valeur": None}
_verrou_etats = threading.Lock()


def etats_serveurs(forcer=False):
    """État de chaque serveur Odoo. Relu au plus toutes les 3 secondes : la
    liste des processus passe par PowerShell, qui prend une seconde."""
    try:
        g = gadget()
    except Exception as erreur:  # noqa: BLE001
        # Gadget présent mais illisible : le dire sur l'Accueil plutôt que
        # de faire disparaître la section.
        return {"disponible": False, "serveurs": [], "erreur": f"{type(erreur).__name__} : {erreur}"}
    if not g:
        return {"disponible": False, "serveurs": []}
    with _verrou_etats:
        if not forcer and _cache_etats["valeur"] and time.time() - _cache_etats["heure"] < 3:
            return _cache_etats["valeur"]
        reglages = g.charger_reglages()
        processus = g.lister_processus_python()
        serveurs = []
        for s in reglages["serveurs"]:
            serveurs.append({
                "base": s["base"],
                "port": s["port"],
                "reference": g.est_reference(s),
                "conf": os.path.basename(g.chemin_conf(s)) if s.get("conf") else None,
                "etat": g.etat_serveur(s["port"], processus),
                "adresse": g.adresse_navigateur(s["port"]),
            })
        valeur = {"disponible": True, "serveurs": serveurs,
                  "etats": [g.ETAT_MARCHE, g.ETAT_DEMARRAGE, g.ETAT_ARRETE, g.ETAT_OCCUPE]}
        _cache_etats.update(heure=time.time(), valeur=valeur)
        return valeur


def serveur_par_port(port):
    g = gadget()
    for s in g.charger_reglages()["serveurs"]:
        if s["port"] == int(port):
            return g, s
    raise ValueError(f"Aucun serveur sur le port {port} dans la liste.")


def action_serveur(action, port):
    g, s = serveur_par_port(port)
    if action == "demarrer":
        g.demarrer(s["base"], s["port"], g.chemin_conf(s))
    elif action == "arreter":
        g.arreter(s["port"])
    elif action == "ouvrir":
        webbrowser.open(g.adresse_navigateur(s["port"]))
    elif action == "journal":
        g.ouvrir_journal(g.fichier_journal(s["port"]))
    else:
        raise ValueError("Action inconnue.")
    _cache_etats["heure"] = 0  # relire les états au prochain appel


# ---------------------------------------------------------------------------
# Lancer les outils
# ---------------------------------------------------------------------------
def port_ouvert(port):
    try:
        with socket.create_connection((HOTE, int(port)), timeout=0.4):
            return True
    except OSError:
        return False


def ouvrir_fenetre_appli(url, largeur=1360, hauteur=860):
    """Une fenêtre sans barre d'adresse, comme un logiciel (Edge, Chrome ou
    Chromium). À défaut, un onglet du navigateur par défaut."""
    systeme.ouvrir_fenetre_appli(url, largeur, hauteur)


def commande_systeme(commande):
    """La commande telle que le système la lance. Une commande écrite en une
    seule ligne reste telle quelle sous Windows ; sous Linux, elle est
    découpée comme dans un terminal (jamais passée à un shell)."""
    if isinstance(commande, str) and not systeme.WINDOWS:
        return shlex.split(commande)
    return commande


def lancer_detache(commande, dossier=None):
    """Lance une commande détachée, sans console, sans rien attendre."""
    systeme.lancer_detache(commande_systeme(commande), dossier=dossier or None)


# Linux : fichiers exécutables lancés directement (sans extension, scripts,
# AppImage…) ; les autres sont ouverts par leur programme habituel.
EXTENSIONS_PROGRAMMES_LINUX = ("", ".sh", ".appimage", ".run", ".bin", ".py")


def ouvrir_cible(cible):
    """Dossier, fichier ou programme d'une tuile. Sous Linux, un programme
    exécutable est lancé directement (xdg-open l'ouvrirait dans un éditeur)."""
    if (not systeme.WINDOWS and os.path.isfile(cible) and os.access(cible, os.X_OK)
            and os.path.splitext(cible)[1].lower() in EXTENSIONS_PROGRAMMES_LINUX):
        lancer_detache([cible], os.path.dirname(cible))
        return
    systeme.ouvrir(cible)


def lancer_outil(identifiant):
    outil = next((o for o in lire_outils()["outils"] if o["id"] == identifiant), None)
    if not outil:
        raise ValueError("Outil introuvable.")
    genre, cible = outil.get("type"), outil.get("cible", "")

    if genre == "appli_web":
        # Un outil avec son propre petit serveur (ex. Mes factures) : on le
        # démarre s'il ne tourne pas, puis on ouvre sa fenêtre.
        port = outil.get("port")
        if port and not port_ouvert(port):
            commande = outil.get("commande") or []
            if not commande:
                raise ValueError("Aucune commande de démarrage pour cet outil.")
            lancer_detache(commande, outil.get("dossier"))
            for _ in range(40):
                if port_ouvert(port):
                    break
                time.sleep(0.25)
            else:
                raise RuntimeError(f"L'outil ne répond pas sur le port {port}.")
        if outil.get("fenetre_appli", True):
            ouvrir_fenetre_appli(cible)
        else:
            webbrowser.open(cible)
    elif genre == "lien":
        # « fenetre_appli » : le site s'ouvre dans sa propre fenêtre, sans
        # barre d'adresse (WhatsApp Web…).
        if outil.get("fenetre_appli"):
            ouvrir_fenetre_appli(cible)
        else:
            webbrowser.open(cible)
    elif genre in ("dossier", "fichier", "programme"):
        if not os.path.exists(cible):
            raise FileNotFoundError(f"Introuvable : {cible}")
        ouvrir_cible(cible)
    elif genre == "commande":
        lancer_detache(cible if isinstance(cible, list) else cible, outil.get("dossier"))
    else:
        raise ValueError(f"Type d'outil inconnu : {genre}")


def etat_outils():
    outils = lire_outils()
    for outil in outils["outils"]:
        if outil.get("type") == "appli_web" and outil.get("port"):
            outil["en_marche"] = port_ouvert(outil["port"])
        elif outil.get("type") in ("dossier", "fichier", "programme"):
            outil["introuvable"] = not os.path.exists(outil.get("cible", ""))
    outils["bulle"] = BULLE_ACTIVE
    return outils


# ---------------------------------------------------------------------------
# Mail, onglet demandé par la bulle
# ---------------------------------------------------------------------------
_boite = None


def boite():
    global _boite
    if _boite is None:
        import mail
        _boite = mail.Boite(lire_outils().get("mail", {}).get("adresse", ""))
    return _boite


def memoriser_adresse_mail(adresse):
    actuel = lire_outils()
    actuel.setdefault("mail", {})["adresse"] = adresse
    ecrire_outils(actuel)


def le_coffre():
    """Le coffre à mots de passe, partagé par tous les onglets."""
    import coffre
    return coffre.partage()


_onglet = {"nom": None, "heure": 0}


def demander_onglet(nom):
    """La bulle demande d'afficher un onglet (rappel, note rapide…) : la page
    le lit à son prochain passage."""
    _onglet.update(nom=nom, heure=time.time())


# ---------------------------------------------------------------------------
# Serveur HTTP
# ---------------------------------------------------------------------------
TYPES_FICHIERS = {".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8"}
HOTES_AUTORISES = {f"{HOTE}:{PORT}", f"localhost:{PORT}"}
ORIGINE = f"http://{HOTE}:{PORT}"


class Gestionnaire(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def requete_sure(self, ecriture):
        """Refuser ce qui ne vient pas de la page elle-même.

        - Host : une autre adresse pointant sur 127.0.0.1 (détournement DNS)
          ne peut pas lire les réponses.
        - Origin : une page d'un autre site ne peut pas envoyer d'ordre.
        - X-Mes-Outils : en-tête que seule notre page ajoute ; un formulaire
          caché sur un site malveillant ne peut pas le poser sans que le
          navigateur ne demande d'abord la permission, que ce serveur ne
          donne jamais.
        """
        if self.headers.get("Host", "") not in HOTES_AUTORISES:
            return False
        origine = self.headers.get("Origin")
        if origine and origine != ORIGINE:
            return False
        if ecriture and self.headers.get("X-Mes-Outils") != "1":
            return False
        return True

    def repondre(self, code, corps, type_mime="application/json; charset=utf-8"):
        if isinstance(corps, (dict, list)):
            corps = json.dumps(corps, ensure_ascii=False).encode("utf-8")
        elif isinstance(corps, str):
            corps = corps.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", type_mime)
        self.send_header("Content-Length", str(len(corps)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(corps)
        except (ConnectionAbortedError, BrokenPipeError):
            pass

    def do_GET(self):
        chemin = urllib.parse.urlparse(self.path).path
        if not self.requete_sure(ecriture=chemin.startswith("/api/")):
            return self.repondre(403, {"erreur": "Accès refusé."})
        try:
            if chemin in ("/", "/index.html"):
                with open(PAGE, "rb") as f:
                    return self.repondre(200, f.read(), "text/html; charset=utf-8")
            if chemin == "/api/outils":
                return self.repondre(200, etat_outils())
            if chemin == "/api/onglets":
                contenu = lire_outils()
                return self.repondre(200, {"fichiers": onglets_web(), "langue": config.langue(), "theme": config.theme(),
                                           "accent": config.accent(),
                                           "masques": contenu.get("onglets_masques") or [],
                                           # None : jamais choisies (anciennes installations : tout est actif)
                                           "apps_actives": contenu.get("apps_actives"),
                                           "profil": contenu.get("profil") or "",
                                           # False seulement pour une installation neuve (outils.exemple.json)
                                           "assistant": contenu.get("assistant_fait") is False,
                                           # Pour adapter les textes de la page (Explorateur, Edge…)
                                           "systeme": "windows" if systeme.WINDOWS else "linux"})
            if chemin == "/api/serveurs":
                return self.repondre(200, etats_serveurs())
            if chemin == "/api/notes":
                return self.repondre(200, donnees.lister("notes"))
            if chemin == "/api/agenda":
                return self.repondre(200, donnees.lister("agenda"))
            if chemin == "/api/mail/etat":
                return self.repondre(200, boite().etat())
            if chemin == "/api/mail/non_lus":
                b = boite()
                return self.repondre(200, {"non_lus": b.non_lus() if b.configuree() else None})
            if chemin == "/api/onglet":
                # Une demande de plus de 30 s est périmée.
                nom = _onglet["nom"] if time.time() - _onglet["heure"] < 30 else None
                _onglet["nom"] = None
                return self.repondre(200, {"onglet": nom})
            if chemin.startswith("/js/") or chemin.startswith("/css/"):
                nom = os.path.basename(chemin)
                fichier = os.path.join(ICI, "web", nom)
                if os.path.isfile(fichier) and os.path.splitext(nom)[1] in TYPES_FICHIERS:
                    with open(fichier, "rb") as f:
                        return self.repondre(200, f.read(), TYPES_FICHIERS[os.path.splitext(nom)[1]])
            self.repondre(404, {"erreur": "Introuvable."})
        except Exception as e:  # noqa: BLE001
            journal(traceback.format_exc())
            self.repondre(500, {"erreur": str(e)})

    def do_POST(self):
        chemin = urllib.parse.urlparse(self.path).path
        # Toujours lire la requête avant de répondre, même pour la refuser :
        # sinon Windows coupe brutalement la connexion (erreur 10053).
        try:
            longueur = min(int(self.headers.get("Content-Length") or 0), 50 * 1024 * 1024)
        except ValueError:
            longueur = 0
        corps = self.rfile.read(longueur) if longueur > 0 else b""
        if not self.requete_sure(ecriture=True):
            return self.repondre(403, {"erreur": "Accès refusé."})
        try:
            donnees_requete = json.loads(corps.decode("utf-8") or "{}")
            if chemin == "/api/lancer":
                lancer_outil(donnees_requete["id"])
                return self.repondre(200, {"ok": True})
            if chemin == "/api/enregistrer":
                actuel = lire_outils()
                actuel.pop("bulle", None)
                actuel["outils"] = donnees_requete["outils"]
                if "prenom" in donnees_requete:
                    actuel["prenom"] = donnees_requete["prenom"]
                ecrire_outils(actuel)
                return self.repondre(200, {"ok": True})
            if chemin == "/api/serveur":
                action_serveur(donnees_requete["action"], donnees_requete["port"])
                return self.repondre(200, {"ok": True})
            for genre in ("notes", "agenda"):
                if chemin == f"/api/{genre}/enregistrer":
                    return self.repondre(200, donnees.enregistrer(genre, donnees_requete["element"]))
                if chemin == f"/api/{genre}/supprimer":
                    return self.repondre(200, {"supprimes": donnees.supprimer(genre, donnees_requete["id"])})
            if chemin.startswith("/api/mail/"):
                return self.mail(chemin[len("/api/mail/"):], donnees_requete)
            if chemin.startswith("/api/coffre/"):
                return self.coffre(chemin[len("/api/coffre/"):], donnees_requete)
            if chemin.startswith("/api/ssh/"):
                return self.ssh(chemin[len("/api/ssh/"):], donnees_requete)
            if chemin.startswith("/api/github/"):
                return self.github(chemin[len("/api/github/"):], donnees_requete)
            if chemin == "/api/gadget":
                # Le gadget complet est un .bat : Windows seulement.
                if not systeme.WINDOWS:
                    raise ValueError("Le gadget « Serveurs Odoo » complet ne fonctionne que sous Windows.")
                g = gadget()
                bat = os.path.join(os.path.dirname(g.__file__), "Gestion serveurs Odoo.bat")
                systeme.ouvrir(bat)
                return self.repondre(200, {"ok": True})
            morceaux = chemin[len("/api/"):].split("/", 1) if chemin.startswith("/api/") else []
            if len(morceaux) == 2:
                routes = routes_module(morceaux[0])
                if routes is not None:
                    fonction = routes.get(morceaux[1])
                    if fonction is None:
                        return self.repondre(404, {"erreur": "Introuvable."})
                    return self.repondre(200, fonction(donnees_requete))
            if chemin == "/api/quitter":
                self.repondre(200, {"ok": True})
                if not BULLE_ACTIVE:  # avec la bulle, on ferme seulement la fenêtre
                    threading.Thread(target=self.server.shutdown, daemon=True).start()
                return None
            self.repondre(404, {"erreur": "Introuvable."})
        except (ValueError, RuntimeError, FileNotFoundError, PermissionError) as e:
            self.repondre(400, {"erreur": str(e)})
        except Exception as e:  # noqa: BLE001
            # Les erreurs « prévues » des modules (ErreurMail, ErreurGitHub…)
            # sont des messages pour l'utilisateur.
            if type(e).__name__.startswith("Erreur"):
                return self.repondre(400, {"erreur": str(e)})
            journal(traceback.format_exc())
            self.repondre(500, {"erreur": f"Erreur inattendue : {e}"})

    def coffre(self, action, d):
        """Le coffre à mots de passe. Le mot de passe maître passe par ici le
        temps de dériver la clé ; il n'est ni enregistré ni journalisé."""
        c = le_coffre()
        if action == "etat":
            return self.repondre(200, c.etat())
        if action == "creer":
            c.creer(d.get("maitre", ""))
            return self.repondre(200, c.etat())
        if action == "ouvrir":
            c.ouvrir(d.get("maitre", ""))
            return self.repondre(200, c.etat())
        if action == "fermer":
            c.fermer()
            return self.repondre(200, c.etat())
        if action == "changer":
            c.changer_maitre(d.get("ancien", ""), d.get("nouveau", ""))
            return self.repondre(200, c.etat())
        if action == "liste":
            return self.repondre(200, {"entrees": c.lister(), **c.etat()})
        if action == "reveler":
            return self.repondre(200, {"valeur": c.reveler(d["id"], d["champ"]), **c.etat()})
        if action == "copier":
            c.copier(d["id"], d["champ"])
            return self.repondre(200, c.etat())
        if action == "enregistrer":
            return self.repondre(200, {"entree": c.enregistrer(d["entree"]), **c.etat()})
        if action == "presse_papiers":
            # Mot de passe généré (pas encore dans le coffre) : même copie sûre.
            import coffre
            coffre.copier_presse_papiers(d.get("texte", ""), effacer_apres=coffre.DELAI_PRESSE_PAPIERS)
            return self.repondre(200, c.etat())
        if action == "supprimer":
            return self.repondre(200, {"supprimes": c.supprimer(d["id"]), **c.etat()})
        return self.repondre(404, {"erreur": "Introuvable."})

    def ssh(self, action, d):
        """Serveurs SSH (voir ssh_cles.py). Le mot de passe de « creer » ne
        sert qu'à la première connexion : il n'est ni enregistré ni journalisé."""
        import ssh_cles
        if action == "liste":
            return self.repondre(200, {"serveurs": ssh_cles.lister()})
        if action == "creer":
            return self.repondre(200, ssh_cles.creer(d.get("nom"), d.get("hote"), d.get("port"),
                                                     d.get("utilisateur"), d.get("mot_de_passe", "")))
        if action == "tester":
            return self.repondre(200, ssh_cles.tester(d["alias"]))
        if action == "terminal":
            return self.repondre(200, ssh_cles.ouvrir_terminal(d["alias"]))
        if action == "retirer":
            return self.repondre(200, ssh_cles.retirer(d["alias"]))
        return self.repondre(404, {"erreur": "Introuvable."})

    def github(self, action, d):
        """GitHub (voir github.py). Le jeton reste dans le coffre de Windows :
        il ne passe jamais par la page."""
        import github
        reglages = lire_outils().get("github") or {}
        dossiers = config.dossiers_projets()
        if action == "etat":
            return self.repondre(200, {**github.etat(), "dossiers": dossiers})
        if action == "connexion/debut":
            return self.repondre(200, github.connexion_debut(reglages.get("client_id") or github.CLIENT_ID))
        if action == "connexion/suite":
            return self.repondre(200, github.connexion_suite())
        if action == "deconnexion":
            github.deconnecter()
            return self.repondre(200, {"connecte": False})
        if action == "depots":
            return self.repondre(200, github.lister_depots(dossiers))
        if action == "dossiers":
            return self.repondre(200, {"dossiers": config.enregistrer_dossiers_projets(d.get("dossiers"))})
        if action == "cloner":
            return self.repondre(200, github.cloner(d.get("complet"), d.get("dossier"), dossiers))
        if action == "ouvrir_page":
            github.ouvrir_page(d.get("url"))
            return self.repondre(200, {"ok": True})
        if action == "ouvrir_dossier":
            github.ouvrir_dossier(d.get("chemin"))
            return self.repondre(200, {"ok": True})
        if action == "vscode":
            github.ouvrir_vscode(d.get("chemin"))
            return self.repondre(200, {"ok": True})
        if action == "apercu":
            return self.repondre(200, github.apercu(d.get("dossier")))
        if action == "creer":
            return self.repondre(200, github.creer_et_envoyer(d.get("dossier"), d.get("nom"),
                                                              d.get("description", ""), d.get("prive", True)))
        # Actions plus récentes (pull requests, issues, Actions…) : github.ROUTES.
        fonction = (getattr(github, "ROUTES", None) or {}).get(action)
        if fonction:
            return self.repondre(200, fonction(d))
        return self.repondre(404, {"erreur": "Introuvable."})

    def mail(self, action, d):
        b = boite()
        if action == "connexion":
            # Le mot de passe d'application, saisi par l'utilisateur, part
            # directement dans le coffre Windows ; il n'est ni journalisé ni
            # renvoyé.
            b.tester_et_enregistrer(d.get("adresse", "").strip(), d.get("secret", ""), d.get("reglages"))
            memoriser_adresse_mail(b.adresse)
            return self.repondre(200, {"configuree": True, "adresse": b.adresse})
        if action == "deconnexion":
            b.deconnecter()
            return self.repondre(200, {"configuree": False})
        if action == "liste":
            return self.repondre(200, b.lister(d.get("dossier", "recus"), d.get("recherche", "")))
        if action == "lire":
            return self.repondre(200, b.lire(d["uid"], d.get("dossier", "recus")))
        if action == "envoyer":
            b.envoyer(d.get("a", ""), d.get("sujet", ""), d.get("corps", ""), d.get("cc", ""),
                      d.get("reponse_a"), d.get("references"))
            return self.repondre(200, {"ok": True})
        return self.repondre(404, {"erreur": "Introuvable."})


def main():
    adresse = f"http://{HOTE}:{PORT}/"
    if port_ouvert(PORT):
        # Déjà lancé (au démarrage de Windows, par exemple) : juste la fenêtre.
        ouvrir_fenetre_appli(adresse, 1180, 800)
        return
    serveur = ThreadingHTTPServer((HOTE, PORT), Gestionnaire)
    threading.Timer(0.5, lambda: ouvrir_fenetre_appli(adresse, 1180, 800)).start()
    journal("Démarrage sur " + adresse)
    try:
        serveur.serve_forever()
    finally:
        serveur.server_close()
        journal("Arrêt")


if __name__ == "__main__":
    main()
