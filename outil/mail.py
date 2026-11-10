# -*- coding: utf-8 -*-
"""Boîte mail de « Mes outils » : IMAP (lecture) et SMTP (envoi), pour Gmail,
Yahoo, iCloud, Zoho, Fastmail, GMX, OVH, Orange, Free, La Poste ou n'importe
quel serveur (réglages manuels).

- Le mot de passe (mot de passe d'application ou habituel, selon le
  fournisseur) est rangé dans le coffre du système (voir systeme.py) :
  Gestionnaire d'identification de Windows (chiffré par Windows, lié à votre
  session), ou trousseau du bureau sous Linux (GNOME Keyring, KWallet) ;
  jamais dans un fichier. Cible : « MesOutils:mail:<adresse> ».
- Les réglages des serveurs sont dans outils.json, section « mail » :
  adresse, fournisseur, imap_hote, imap_port, smtp_hote, smtp_port,
  smtp_securite (« ssl » ou « starttls »), identifiant.
- Ancienne configuration (seulement « adresse ») : c'était forcément Gmail.
- Outlook / Hotmail / Live / Office 365 : Microsoft exige une connexion OAuth,
  pas encore prise en charge (message clair, rien n'est tenté).
"""
import base64
import email
import email.policy
import email.utils
import imaplib
import re
import smtplib
import ssl
import threading
import time
import unicodedata
from email.header import decode_header, make_header
from email.message import EmailMessage

import config
import systeme

CIBLE_COFFRE = "MesOutils:mail:{adresse}"
SECTION = "mail"

# ---------------------------------------------------------------------------
# Fournisseurs
# ---------------------------------------------------------------------------
# mot_de_passe : « application » (code spécial créé dans le compte) ou
# « habituel ». Les textes des guides sont dans la page (mails.js).
FOURNISSEURS = {
    "gmail": {"nom": "Gmail", "imap": ("imap.gmail.com", 993), "smtp": ("smtp.gmail.com", 465, "ssl"),
              "mot_de_passe": "application", "domaines": ["gmail.com", "googlemail.com"]},
    "yahoo": {"nom": "Yahoo", "imap": ("imap.mail.yahoo.com", 993), "smtp": ("smtp.mail.yahoo.com", 465, "ssl"),
              "mot_de_passe": "application",
              "domaines": ["yahoo.com", "yahoo.fr", "yahoo.co.uk", "yahoo.de", "yahoo.es", "yahoo.it",
                           "yahoo.ca", "yahoo.com.au", "ymail.com", "rocketmail.com"]},
    "icloud": {"nom": "iCloud", "imap": ("imap.mail.me.com", 993), "smtp": ("smtp.mail.me.com", 587, "starttls"),
               "mot_de_passe": "application", "domaines": ["icloud.com", "me.com", "mac.com"]},
    "zoho": {"nom": "Zoho Mail", "imap": ("imap.zoho.com", 993), "smtp": ("smtp.zoho.com", 465, "ssl"),
             "mot_de_passe": "application", "domaines": ["zoho.com", "zohomail.com"]},
    "fastmail": {"nom": "Fastmail", "imap": ("imap.fastmail.com", 993), "smtp": ("smtp.fastmail.com", 465, "ssl"),
                 "mot_de_passe": "application", "domaines": ["fastmail.com", "fastmail.fm"]},
    "gmx": {"nom": "GMX", "imap": ("imap.gmx.com", 993), "smtp": ("mail.gmx.com", 587, "starttls"),
            "mot_de_passe": "habituel",
            "domaines": ["gmx.com", "gmx.us", "gmx.co.uk", "gmx.fr", "gmx.es", "gmx.net", "gmx.de", "gmx.at", "gmx.ch"],
            # gmx.net / .de / .at / .ch : serveurs allemands.
            "hotes_par_domaine": {d: ("imap.gmx.net", "mail.gmx.net") for d in ("gmx.net", "gmx.de", "gmx.at", "gmx.ch")}},
    "ovh": {"nom": "OVHcloud", "imap": ("ssl0.ovh.net", 993), "smtp": ("ssl0.ovh.net", 465, "ssl"),
            "mot_de_passe": "habituel", "domaines": []},
    "orange": {"nom": "Orange", "imap": ("imap.orange.fr", 993), "smtp": ("smtp.orange.fr", 465, "ssl"),
               "mot_de_passe": "habituel", "domaines": ["orange.fr", "wanadoo.fr"]},
    "free": {"nom": "Free", "imap": ("imap.free.fr", 993), "smtp": ("smtp.free.fr", 465, "ssl"),
             "mot_de_passe": "habituel", "domaines": ["free.fr"]},
    "laposte": {"nom": "La Poste", "imap": ("imap.laposte.net", 993), "smtp": ("smtp.laposte.net", 465, "ssl"),
                "mot_de_passe": "habituel", "domaines": ["laposte.net"]},
    "autre": {"nom": "Autre (réglages manuels)", "imap": ("", 993), "smtp": ("", 465, "ssl"),
              "mot_de_passe": "habituel", "domaines": []},
}
# Microsoft a coupé la connexion par mot de passe (IMAP/SMTP) : OAuth obligatoire.
DOMAINES_MICROSOFT = ("outlook.", "hotmail.", "live.", "msn.com", "passport.com")
MESSAGE_MICROSOFT = ("Outlook, Hotmail et Live ne sont pas encore pris en charge : Microsoft "
                     "n'accepte plus les mots de passe pour les logiciels de messagerie.")
SECURITES_SMTP = ("ssl", "starttls")


class ErreurMail(Exception):
    pass


def domaine(adresse):
    return (adresse or "").rsplit("@", 1)[-1].strip().lower() if "@" in (adresse or "") else ""


def est_microsoft(adresse):
    d = domaine(adresse)
    return bool(d) and any(d.startswith(m) or d == m for m in DOMAINES_MICROSOFT)


def detecter_fournisseur(adresse):
    """Le fournisseur deviné d'après le domaine de l'adresse : « outlook »
    (non pris en charge), un fournisseur connu, ou None (domaine personnel)."""
    if est_microsoft(adresse):
        return "outlook"
    d = domaine(adresse)
    for cle, f in FOURNISSEURS.items():
        if d in f["domaines"]:
            return cle
    return None


def prereglage(fournisseur, adresse=""):
    """Les réglages complets d'un fournisseur connu (sans mot de passe)."""
    if fournisseur == "outlook":
        raise ErreurMail(MESSAGE_MICROSOFT)
    f = FOURNISSEURS.get(fournisseur)
    if f is None:
        raise ErreurMail("Fournisseur inconnu.")
    imap_hote, smtp_hote = f.get("hotes_par_domaine", {}).get(domaine(adresse), (f["imap"][0], f["smtp"][0]))
    return {"fournisseur": fournisseur, "imap_hote": imap_hote, "imap_port": f["imap"][1],
            "smtp_hote": smtp_hote, "smtp_port": f["smtp"][1], "smtp_securite": f["smtp"][2],
            "identifiant": adresse}


def _port(valeur, defaut):
    if valeur in (None, ""):
        return defaut
    try:
        port = int(valeur)
    except (TypeError, ValueError):
        raise ErreurMail("Port invalide.") from None
    if not 1 <= port <= 65535:
        raise ErreurMail("Port invalide.")
    return port


_HOTE_VALIDE = re.compile(r"^[A-Za-z0-9.-]{1,253}$")


def normaliser(adresse, reglages=None):
    """Réglages complets et vérifiés pour une adresse.

    - reglages fourni (par la page) : fournisseur connu → son préréglage
      (identifiant éventuel conservé) ; « autre » → serveurs saisis.
    - sinon : détection d'après le domaine ; domaine inconnu → Gmail (c'était
      le seul fournisseur avant, ex. adresse Google Workspace).
    """
    adresse = (adresse or "").strip()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", adresse):
        raise ErreurMail("Adresse mail invalide.")
    if est_microsoft(adresse):
        raise ErreurMail(MESSAGE_MICROSOFT)
    reglages = dict(reglages or {})
    fournisseur = reglages.get("fournisseur") or detecter_fournisseur(adresse) or "gmail"
    identifiant = str(reglages.get("identifiant") or "").strip() or adresse
    if fournisseur != "autre":
        r = prereglage(fournisseur, adresse)
        r["identifiant"] = identifiant
        return r
    imap_hote = str(reglages.get("imap_hote") or "").strip()
    smtp_hote = str(reglages.get("smtp_hote") or "").strip()
    if not imap_hote or not smtp_hote:
        raise ErreurMail("Indiquez le serveur IMAP et le serveur SMTP.")
    if not _HOTE_VALIDE.match(imap_hote) or not _HOTE_VALIDE.match(smtp_hote):
        raise ErreurMail("Nom de serveur invalide.")
    securite = reglages.get("smtp_securite") or "ssl"
    if securite not in SECURITES_SMTP:
        raise ErreurMail("Sécurité SMTP inconnue (SSL ou STARTTLS).")
    return {"fournisseur": "autre", "imap_hote": imap_hote, "imap_port": _port(reglages.get("imap_port"), 993),
            "smtp_hote": smtp_hote, "smtp_port": _port(reglages.get("smtp_port"), 465 if securite == "ssl" else 587),
            "smtp_securite": securite, "identifiant": identifiant}


def reglages_enregistres(adresse):
    """Les réglages de l'adresse d'après outils.json. Une ancienne section
    sans « fournisseur » = Gmail."""
    sec = config.section(SECTION)
    if sec.get("adresse") and sec.get("adresse") != adresse:
        sec = {}
    if not sec.get("fournisseur"):
        if est_microsoft(adresse):
            return {"fournisseur": "outlook"}
        return prereglage(detecter_fournisseur(adresse) or "gmail", adresse)
    if sec["fournisseur"] == "outlook":
        return {"fournisseur": "outlook"}
    try:
        return normaliser(adresse, sec)
    except ErreurMail:
        return prereglage("gmail", adresse)


def enregistrer_reglages(adresse, reglages):
    """Écrit adresse + réglages serveur dans outils.json (jamais le mot de passe)."""
    propres = {k: reglages[k] for k in ("fournisseur", "imap_hote", "imap_port", "smtp_hote",
                                        "smtp_port", "smtp_securite", "identifiant")}
    return config.modifier_section(SECTION, adresse=adresse, **propres)


def fournisseurs_pour_page():
    """Liste des fournisseurs pour la page (sans les secrets, évidemment)."""
    return [{"id": cle, "nom": f["nom"], "mot_de_passe": f["mot_de_passe"], "domaines": f["domaines"],
             "imap": list(f["imap"]), "smtp": list(f["smtp"])} for cle, f in FOURNISSEURS.items()]


# ---------------------------------------------------------------------------
# Coffre du système (Windows : Gestionnaire d'identification ; Linux :
# trousseau du bureau). Les tests et la démo remplacent ces trois fonctions.
# ---------------------------------------------------------------------------
def _message_coffre_impossible():
    if systeme.WINDOWS:  # texte inchangé : la page le traduit tel quel
        return "Impossible d'enregistrer le mot de passe dans le coffre Windows."
    return f"Impossible d'enregistrer le mot de passe dans {systeme.nom_du_coffre()}."


def coffre_ecrire(adresse, secret):
    if not systeme.secret_ecrire(CIBLE_COFFRE.format(adresse=adresse), adresse, secret):
        raise ErreurMail(_message_coffre_impossible())


def coffre_lire(adresse):
    return systeme.secret_lire(CIBLE_COFFRE.format(adresse=adresse))


def coffre_supprimer(adresse):
    systeme.secret_supprimer(CIBLE_COFFRE.format(adresse=adresse))


# ---------------------------------------------------------------------------
# Outils de décodage
# ---------------------------------------------------------------------------
def _entete(valeur):
    if not valeur:
        return ""
    try:
        return str(make_header(decode_header(valeur)))
    except Exception:
        return str(valeur)


def _personne(valeur):
    nom, adresse = email.utils.parseaddr(_entete(valeur))
    return {"nom": nom or adresse, "adresse": adresse}


def _date(valeur):
    try:
        d = email.utils.parsedate_to_datetime(valeur)
        return d.astimezone().strftime("%Y-%m-%dT%H:%M")
    except Exception:
        return ""


def decoder_utf7_imap(nom):
    """Nom de dossier IMAP en « UTF-7 modifié » (RFC 3501, 5.1.3) → texte.
    Ex. « &AMk-l&AOk-ments envoy&AOk-s » → « Éléments envoyés »."""
    def morceau(m):
        code = m.group(1)
        if not code:
            return "&"
        code = code.replace(",", "/")
        code += "=" * (-len(code) % 4)
        try:
            return base64.b64decode(code).decode("utf-16-be")
        except Exception:
            return m.group(0)
    return re.sub(r"&([A-Za-z0-9+,]*)-", morceau, nom)


def _sans_accents(texte):
    return "".join(c for c in unicodedata.normalize("NFD", texte) if unicodedata.category(c) != "Mn").lower()


_LIGNE_LIST = re.compile(r'^\((?P<marques>[^)]*)\)\s+(?P<sep>"(?:[^"\\]|\\.)*"|NIL)\s+(?P<nom>.*)$', re.I)


def lire_liste_dossiers(lignes):
    """Réponse de LIST → [(marques, séparateur, nom brut)]. Gère les noms
    entre guillemets, les noms nus et les noms envoyés en « littéral »."""
    dossiers = []
    for ligne in lignes or []:
        if isinstance(ligne, tuple):  # nom en littéral : (b'(...) "/" {12}', b'Nom')
            tete = ligne[0].decode("utf-8", "replace")
            ligne_texte = re.sub(r"\{\d+\}$", "", tete).rstrip() + ' "' + \
                ligne[1].decode("utf-8", "replace").replace("\\", "\\\\").replace('"', '\\"') + '"'
        elif isinstance(ligne, bytes):
            ligne_texte = ligne.decode("utf-8", "replace")
        else:
            continue
        m = _LIGNE_LIST.match(ligne_texte.strip())
        if not m:
            continue
        nom = m.group("nom").strip()
        if nom.startswith('"') and nom.endswith('"') and len(nom) >= 2:
            nom = re.sub(r"\\(.)", r"\1", nom[1:-1])
        sep = m.group("sep")
        sep = None if sep.upper() == "NIL" else re.sub(r"\\(.)", r"\1", sep[1:-1])
        dossiers.append((m.group("marques").split(), sep, nom))
    return dossiers


# Noms courants du dossier des mails envoyés (sans accents, en minuscules),
# quand le serveur n'annonce pas la marque \Sent.
NOMS_ENVOYES = ("sent", "sent items", "sent messages", "sent mail", "envoyes", "elements envoyes",
                "messages envoyes", "mails envoyes", "courrier envoye", "gesendet", "gesendete objekte",
                "enviados", "inviati", "posta inviata", "verzonden")


def trouver_dossier(dossiers, marque, noms=()):
    """Nom brut du dossier qui porte la marque (RFC 6154), sinon du premier
    dossier dont le nom (ou la dernière partie) est dans « noms »."""
    for marques, _sep, nom in dossiers:
        if any(m.lower() == marque.lower() for m in marques):
            return nom
    for _marques, sep, nom in dossiers:
        lisible = _sans_accents(decoder_utf7_imap(nom))
        derniere = lisible.rsplit(sep, 1)[-1] if sep else lisible
        if lisible in noms or derniere in noms:
            return nom
    return None


def _guillemets(nom):
    return '"' + nom.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _court(e):
    texte = str(e)
    return texte if len(texte) < 160 else texte[:157] + "…"


def _message_refus(fournisseur, e):
    if FOURNISSEURS.get(fournisseur, {}).get("mot_de_passe") == "application":
        debut = ("Le serveur refuse ce mot de passe (il faut un mot de passe d'application, "
                 "pas votre mot de passe habituel)")
    else:
        debut = "Le serveur refuse l'identifiant ou le mot de passe"
    return f"{debut} : {_court(e)}"


# ---------------------------------------------------------------------------
# La boîte
# ---------------------------------------------------------------------------
class Boite:
    def __init__(self, adresse, reglages=None):
        self.adresse = adresse
        self._reglages = reglages  # None : relus dans outils.json à chaque connexion
        self._verrou = threading.Lock()
        self._cache_liste = {}
        self._non_lus = (0, None)  # (heure, nombre)
        self._dossiers = {}  # nom logique → nom brut IMAP

    # -- réglages ------------------------------------------------------------
    def reglages(self):
        return dict(self._reglages) if self._reglages else reglages_enregistres(self.adresse)

    def etat(self):
        """Pour la page : état, réglages (sans mot de passe) et fournisseurs."""
        r = self.reglages() if self.adresse else {}
        return {"configuree": self.configuree(), "adresse": self.adresse, "reglages": r,
                "fournisseurs": fournisseurs_pour_page()}

    # -- connexion -----------------------------------------------------------
    def configuree(self):
        return bool(self.adresse) and coffre_lire(self.adresse) is not None

    @staticmethod
    def _ouvrir_imap(reglages, secret):
        if reglages.get("fournisseur") == "outlook":
            raise ErreurMail(MESSAGE_MICROSOFT)
        try:
            c = imaplib.IMAP4_SSL(reglages["imap_hote"], reglages["imap_port"],
                                  ssl_context=ssl.create_default_context(), timeout=20)
        except OSError as e:
            raise ErreurMail("Pas de connexion au serveur mail (Internet ? nom du serveur ?) : " + _court(e))
        try:
            c.login(reglages["identifiant"], secret)
        except imaplib.IMAP4.error as e:
            try:
                c.logout()
            except Exception:  # noqa: BLE001
                pass
            raise ErreurMail(_message_refus(reglages.get("fournisseur"), e))
        except OSError as e:
            raise ErreurMail("Pas de connexion au serveur mail (Internet ? nom du serveur ?) : " + _court(e))
        return c

    def _imap(self):
        secret = coffre_lire(self.adresse)
        if not secret:
            raise ErreurMail("Boîte mail pas encore connectée.")
        return self._ouvrir_imap(self.reglages(), secret)

    def tester_et_enregistrer(self, adresse, secret, reglages=None):
        """Vérifie la connexion IMAP, puis range le mot de passe dans le coffre
        du système (Windows ou trousseau Linux) et les réglages serveur dans
        outils.json."""
        adresse = (adresse or "").strip()
        secret = (secret or "").strip()
        if not adresse or not secret:
            raise ErreurMail("Indiquez l'adresse et le mot de passe.")
        r = normaliser(adresse, reglages)
        if FOURNISSEURS[r["fournisseur"]]["mot_de_passe"] == "application":
            # Les codes d'application s'affichent souvent par groupes : « abcd efgh ».
            secret = re.sub(r"\s+", "", secret)
        c = self._ouvrir_imap(r, secret)
        try:
            c.logout()
        except Exception:  # noqa: BLE001
            pass
        coffre_ecrire(adresse, secret)
        if self.adresse and self.adresse != adresse:
            coffre_supprimer(self.adresse)
        enregistrer_reglages(adresse, r)
        self.adresse = adresse
        self._reglages = None
        self._dossiers.clear()
        self._cache_liste.clear()
        self._non_lus = (0, None)

    def deconnecter(self):
        if self.adresse:
            coffre_supprimer(self.adresse)
        self._cache_liste.clear()
        self._dossiers.clear()
        self._non_lus = (0, None)

    # -- lecture -----------------------------------------------------------
    # Les noms des dossiers dépendent du fournisseur et de la langue :
    # d'abord la marque officielle (RFC 6154), puis les noms courants.
    MARQUES = {"envoyes": ("\\Sent", NOMS_ENVOYES), "tous": ("\\All", ())}

    def _choisir(self, c, dossier, lecture_seule=True):
        nom = "INBOX"
        if dossier in self.MARQUES:
            nom = self._dossiers.get(dossier)
            if not nom:
                statut, lignes = c.list()
                marque, noms = self.MARQUES[dossier]
                nom = trouver_dossier(lire_liste_dossiers(lignes), marque, noms)
                if not nom:
                    raise ErreurMail("Dossier introuvable dans la boîte.")
                self._dossiers[dossier] = nom
        statut, _ = c.select(_guillemets(nom), readonly=lecture_seule)
        if statut != "OK":
            self._dossiers.pop(dossier, None)
            raise ErreurMail("Dossier introuvable dans la boîte.")

    @staticmethod
    def _capacites(c):
        try:
            statut, donnees = c.capability()
            if statut == "OK" and donnees and donnees[0]:
                return {x.upper() for x in donnees[0].decode("ascii", "replace").split()}
        except Exception:  # noqa: BLE001
            pass
        return {str(x).upper() for x in getattr(c, "capabilities", ())}

    def _rechercher(self, c, recherche):
        terme = re.sub(r'[\\"\r\n]', " ", recherche or "").strip()
        if not terme:
            return c.uid("SEARCH", None, "ALL")
        gmail = "X-GM-EXT-1" in self._capacites(c)
        if terme.isascii():
            if gmail:
                # Recherche façon Gmail (expéditeur, objet, texte…).
                return c.uid("SEARCH", None, "X-GM-RAW", f'"{terme}"')
            q = f'"{terme}"'
            return c.uid("SEARCH", None, "OR", "OR", "FROM", q, "SUBJECT", q, "TEXT", q)
        # Accents, autres alphabets : le terme part en UTF-8 dans un
        # « littéral » (un seul possible par commande) ; TEXT couvre aussi
        # l'expéditeur et l'objet (en-têtes).
        c.literal = terme.encode("utf-8")
        return c.uid("SEARCH", "CHARSET", "UTF-8", "X-GM-RAW" if gmail else "TEXT")

    def lister(self, dossier="recus", recherche="", nombre=40):
        cle = (dossier, recherche, nombre)
        en_cache = self._cache_liste.get(cle)
        if en_cache and time.time() - en_cache[0] < 45:
            return en_cache[1]
        with self._verrou:
            c = self._imap()
            try:
                self._choisir(c, dossier)
                statut, donnees = self._rechercher(c, recherche)
                if statut != "OK":
                    raise ErreurMail("Recherche refusée par le serveur.")
                uids = (donnees[0] or b"").split()[-nombre:]
                mails = []
                if uids:
                    statut, reponse = c.uid("FETCH", b",".join(uids),
                                            "(UID FLAGS BODY.PEEK[HEADER.FIELDS (FROM TO SUBJECT DATE)])")
                    for partie in reponse or []:
                        if not isinstance(partie, tuple):
                            continue
                        meta = partie[0].decode("utf-8", "replace")
                        uid = re.search(r"UID (\d+)", meta)
                        entetes = email.message_from_bytes(partie[1])
                        mails.append({
                            "uid": uid.group(1) if uid else "",
                            "de": _personne(entetes.get("From")),
                            "a": _personne(entetes.get("To")),
                            "sujet": _entete(entetes.get("Subject")) or "(sans objet)",
                            "date": _date(entetes.get("Date")),
                            "lu": "\\Seen" in meta,
                            "important": "\\Flagged" in meta,
                        })
                mails.sort(key=lambda m: int(m["uid"] or 0), reverse=True)
            finally:
                c.logout()
        self._cache_liste[cle] = (time.time(), mails)
        return mails

    def lire(self, uid, dossier="recus"):
        if not re.fullmatch(r"\d+", str(uid)):
            raise ErreurMail("Mail introuvable.")
        with self._verrou:
            c = self._imap()
            try:
                self._choisir(c, dossier, lecture_seule=False)
                statut, reponse = c.uid("FETCH", str(uid).encode(), "(BODY.PEEK[])")
                brut = next((p[1] for p in reponse or [] if isinstance(p, tuple)), None)
                if not brut:
                    raise ErreurMail("Mail introuvable.")
                c.uid("STORE", str(uid).encode(), "+FLAGS", "(\\Seen)")
            finally:
                c.logout()
        self._cache_liste.clear()
        self._non_lus = (0, None)
        msg = email.message_from_bytes(brut, policy=email.policy.default)
        texte = html = None
        pieces = []
        for partie in msg.walk():
            if partie.is_multipart():
                continue
            nom = partie.get_filename()
            if nom or partie.get_content_disposition() == "attachment":
                pieces.append({"nom": _entete(nom) or "pièce jointe",
                               "taille": len(partie.get_payload(decode=True) or b"")})
                continue
            try:
                if partie.get_content_type() == "text/plain" and texte is None:
                    texte = partie.get_content()
                elif partie.get_content_type() == "text/html" and html is None:
                    html = partie.get_content()
            except (LookupError, UnicodeError):  # jeu de caractères inconnu
                contenu = (partie.get_payload(decode=True) or b"").decode("utf-8", "replace")
                if partie.get_content_type() == "text/html":
                    html = html or contenu
                else:
                    texte = texte or contenu
        return {
            "uid": str(uid),
            "de": _personne(msg.get("From")),
            "a": _entete(msg.get("To")),
            "cc": _entete(msg.get("Cc")),
            "sujet": _entete(msg.get("Subject")) or "(sans objet)",
            "date": _date(msg.get("Date")),
            "texte": texte or "",
            "html": html or "",
            "pieces": pieces,
            "message_id": msg.get("Message-ID", ""),
            "references": msg.get("References", ""),
        }

    def non_lus(self):
        """Nombre de mails non lus dans la boîte de réception (relu au plus
        toutes les deux minutes)."""
        heure, nombre = self._non_lus
        if nombre is not None and time.time() - heure < 120:
            return nombre
        with self._verrou:
            c = self._imap()
            try:
                statut, donnees = c.status("INBOX", "(UNSEEN)")
                m = re.search(rb"UNSEEN (\d+)", (donnees or [b""])[0] or b"")
                nombre = int(m.group(1)) if m else 0
            finally:
                c.logout()
        self._non_lus = (time.time(), nombre)
        return nombre

    # -- envoi -------------------------------------------------------------
    @staticmethod
    def _ouvrir_smtp(r):
        contexte = ssl.create_default_context()
        if r["smtp_securite"] == "starttls":
            s = smtplib.SMTP(r["smtp_hote"], r["smtp_port"], timeout=30)
            try:
                s.ehlo()
                s.starttls(context=contexte)
                s.ehlo()
            except Exception:
                s.close()
                raise
            return s
        return smtplib.SMTP_SSL(r["smtp_hote"], r["smtp_port"], context=contexte, timeout=30)

    def envoyer(self, a, sujet, corps, cc="", reponse_a=None, references=None):
        if not (a or "").strip():
            raise ErreurMail("Indiquez au moins un destinataire.")
        secret = coffre_lire(self.adresse)
        if not secret:
            raise ErreurMail("Boîte mail pas encore connectée.")
        r = self.reglages()
        if r.get("fournisseur") == "outlook":
            raise ErreurMail(MESSAGE_MICROSOFT)
        msg = EmailMessage()
        msg["From"] = self.adresse
        msg["To"] = a
        if (cc or "").strip():
            msg["Cc"] = cc
        msg["Subject"] = sujet
        msg["Date"] = email.utils.formatdate(localtime=True)
        msg["Message-ID"] = email.utils.make_msgid(domain=self.adresse.split("@")[-1])
        if reponse_a:
            msg["In-Reply-To"] = reponse_a
            msg["References"] = f"{references or ''} {reponse_a}".strip()
        msg.set_content(corps)
        try:
            with self._ouvrir_smtp(r) as s:
                s.login(r["identifiant"], secret)
                s.send_message(msg)
        except smtplib.SMTPAuthenticationError as e:
            raise ErreurMail(_message_refus(r.get("fournisseur"), e))
        except smtplib.SMTPException as e:
            raise ErreurMail("Envoi refusé par le serveur : " + _court(e))
        except OSError as e:
            raise ErreurMail("Pas de connexion au serveur mail (Internet ? nom du serveur ?) : " + _court(e))
        self._cache_liste.clear()
