# -*- coding: utf-8 -*-
"""Application « Devis et factures ».

- Réglages de l'entreprise (nom, adresse, identifiants, TVA, logo,
  coordonnées de paiement, conditions, devise, préfixes) : donnees\\factures.json,
  logo copié dans donnees\\factures\\.
- Documents : devis, factures et avoirs. Un brouillon n'a pas de numéro ; le
  numéro est attribué à l'émission, chronologique et continu par année et par
  préfixe (DEV-2026-001, FAC-2026-001, AV-2026-001). Un document émis n'est
  plus modifiable : une facture se corrige par un avoir.
- Montants : Decimal uniquement (jamais de float), arrondis à la devise
  (centime, ou unité pour l'ariary), arrondi commercial (0,5 → au-dessus).
  Remise globale répartie au prorata entre les taux de TVA, au centime près.
- PDF : HTML imprimable converti par Microsoft Edge sans fenêtre, enregistré
  dans Documents\\Mes outils\\Factures\\<année>\\.
- Heures : importées de l'application Temps (sessions par projet).
- Bulle : alertes_dues() signale une fois chaque facture qui passe en retard.
"""
import base64
import csv
import datetime
import html
import io
import os
import re
import shutil
import subprocess
import tempfile
import threading
import urllib.parse
import uuid
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

import config

NOM = "factures"
TYPES = ("devis", "facture", "avoir")
DEVISES = {"EUR": ("€", 2), "USD": ("$", 2), "MGA": ("Ar", 0)}
MODES_TVA = ("assujetti", "franchise", "libre")
MENTION_293B = "TVA non applicable, art. 293 B du CGI"
MOYENS = ("virement", "especes", "cheque", "carte", "mobile_money", "paypal", "autre")
REMISES = ("aucune", "pourcent", "montant")
EXTENSIONS_LOGO = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp"}
MAX_LOGO = 1024 * 1024
MAX_LIGNES = 200
MAX_DOCUMENTS = 20000
LIMITE = Decimal("1e12")
CREATION_SANS_FENETRE = 0x08000000

_verrou = threading.RLock()

PENALITES_FR = ("En cas de retard de paiement : pénalités au taux de trois fois le taux d'intérêt légal et "
                "indemnité forfaitaire de 40 € pour frais de recouvrement (art. L441-10 du Code de commerce). "
                "Pas d'escompte pour paiement anticipé.")

ENTREPRISE_DEFAUT = {
    "nom": "", "adresse": "", "email": "", "telephone": "", "identifiants": [],
    "tva_mode": "assujetti", "tva_taux": "20", "tva_texte": "",
    "logo": "", "iban": "", "bic": "", "paiement_autre": "",
    "delai_jours": 30, "validite_jours": 30, "penalites": "",
    "devise": "EUR", "devise_symbole": "", "devise_decimales": 2,
    "prefixe_devis": "DEV", "prefixe_facture": "FAC", "prefixe_avoir": "AV",
    "pied": "",
}

# Textes du PDF, du mail, de l'export et de la bulle (sans le dictionnaire de la page).
_ANGLAIS = {
    "Devis": "Quote", "Facture": "Invoice", "Avoir": "Credit note",
    "DEVIS": "QUOTE", "FACTURE": "INVOICE", "AVOIR": "CREDIT NOTE",
    "N°": "No.", "Date": "Date", "Échéance": "Due date", "Valable jusqu'au": "Valid until",
    "Destinataire": "Bill to", "Désignation": "Description", "Qté": "Qty", "Unité": "Unit",
    "Prix unit. HT": "Unit price", "TVA": "VAT", "Total HT": "Total excl. VAT",
    "Montant": "Amount", "Prix unit.": "Unit price",
    "Sous-total HT": "Subtotal", "Sous-total": "Subtotal", "Remise": "Discount", "Remise ({p} %)": "Discount ({p}%)",
    "TVA {t} %": "VAT {t}%", "Total TTC": "Total incl. VAT", "Total": "Total", "Net à payer": "Amount due",
    "Total de l'avoir": "Credit total",
    "Avoir sur la facture {numero} du {date}.": "Credit note for invoice {numero} dated {date}.",
    "Prestation : {texte}": "Service period: {texte}",
    "Conditions de paiement : à réception.": "Payment terms: due on receipt.",
    "Conditions de paiement : {n} jours, soit au plus tard le {date}.": "Payment terms: {n} days, i.e. by {date} at the latest.",
    "Règlement": "Payment details", "IBAN": "IBAN", "BIC": "BIC",
    "Devis valable jusqu'au {date}.": "Quote valid until {date}.",
    "Bon pour accord (date et signature)": "Approved (date and signature)",
    "BROUILLON": "DRAFT", "à l'émission": "on issue",
    "Tél.": "Tel.", "Page": "Page",
    "Facture en retard": "Overdue invoice",
    "{projet} – du {debut} au {fin}": "{projet} – {debut} to {fin}",
    "{numero} · {client} : {reste} à encaisser (échéance du {date})": "{numero} · {client}: {reste} outstanding (due {date})",
    "Facture {numero}": "Invoice {numero}", "Devis {numero}": "Quote {numero}", "Avoir {numero}": "Credit note {numero}",
    "Bonjour,": "Hello,", "Cordialement,": "Kind regards,",
    "Veuillez trouver ci-joint la facture {numero} d'un montant de {montant}, à régler au plus tard le {date}.":
        "Please find attached invoice {numero} for {montant}, payable by {date} at the latest.",
    "Veuillez trouver ci-joint la facture {numero} d'un montant de {montant}.":
        "Please find attached invoice {numero} for {montant}.",
    "Veuillez trouver ci-joint notre devis {numero} d'un montant de {montant}, valable jusqu'au {date}.":
        "Please find attached our quote {numero} for {montant}, valid until {date}.",
    "Veuillez trouver ci-joint l'avoir {numero} d'un montant de {montant}.":
        "Please find attached credit note {numero} for {montant}.",
    "Type": "Type", "Numéro": "Number", "Client": "Client", "TTC": "Incl. VAT", "HT": "Excl. VAT",
    "Payé": "Paid", "Reste": "Outstanding", "Statut": "Status", "Devise": "Currency",
    "Brouillon": "Draft", "Envoyé": "Sent", "Envoyée": "Sent", "Accepté": "Accepted", "Refusé": "Declined",
    "Facturé": "Invoiced", "Expiré": "Expired", "Payée partiellement": "Partly paid", "Payée": "Paid",
    "En retard": "Overdue", "Annulée": "Cancelled", "Émis": "Issued",
    PENALITES_FR: "Late payment: interest at three times the legal interest rate and a fixed €40 recovery fee "
                  "(art. L441-10 of the French Commercial Code). No discount for early payment.",
    MENTION_293B: "VAT not applicable, art. 293 B of the French General Tax Code",
}

LIBELLES_ETATS = {
    "brouillon": "Brouillon", "envoye": "Envoyé", "envoyee": "Envoyée", "accepte": "Accepté", "refuse": "Refusé",
    "facture": "Facturé", "expire": "Expiré", "partielle": "Payée partiellement", "payee": "Payée",
    "retard": "En retard", "annulee": "Annulée", "emis": "Émis",
}


def _texte(fr, **valeurs):
    texte = _ANGLAIS.get(fr, fr) if config.langue() == "en" else fr
    return texte.format(**valeurs) if valeurs else texte


def aujourdhui():
    """La date locale (remplacée par une date simulée dans les tests)."""
    return datetime.date.today()


def maintenant():
    return datetime.datetime.now().replace(microsecond=0)


# ---------------------------------------------------------------------------
# Nombres et montants (Decimal uniquement)
# ---------------------------------------------------------------------------
def _decimal(valeur, nom, mini=None, maxi=None, places=4):
    """Un nombre saisi (« 1 234,50 » ou « 1234.5 ») → Decimal, ou ValueError."""
    if isinstance(valeur, float):
        valeur = repr(valeur)
    texte = str("" if valeur is None else valeur).strip()
    for espace in (" ", "\u00a0", "\u202f"):
        texte = texte.replace(espace, "")
    texte = texte.replace(",", ".")
    if not texte:
        raise ValueError(f"{nom} : nombre manquant.")
    try:
        d = Decimal(texte)
    except InvalidOperation:
        raise ValueError(f"{nom} : nombre invalide.") from None
    if not d.is_finite() or abs(d) >= LIMITE:
        raise ValueError(f"{nom} : nombre invalide.")
    if d != d.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP):
        raise ValueError(f"{nom} : {places} décimales au plus.")
    if mini is not None and d < mini:
        raise ValueError(f"{nom} : valeur trop petite.")
    if maxi is not None and d > maxi:
        raise ValueError(f"{nom} : valeur trop grande.")
    return d


def _txt(d):
    """Decimal → texte sans exposant ni zéros inutiles (« 12.5 », « 3 »)."""
    d = d.normalize()
    texte = format(d, "f")
    return "0" if texte in ("-0", "") else texte


def _pas(decimales):
    return Decimal(1).scaleb(-int(decimales))


def _arrondi(d, decimales):
    return d.quantize(_pas(decimales), rounding=ROUND_HALF_UP)


def _montant_txt(d, decimales):
    return format(_arrondi(d, decimales), "f")


def devise_de(entreprise):
    """{code, symbole, decimales} de l'entreprise (ou de la photo d'un document émis)."""
    code = entreprise.get("devise") or "EUR"
    if code in DEVISES:
        symbole, decimales = DEVISES[code]
    else:
        symbole = entreprise.get("devise_symbole") or code
        decimales = int(entreprise.get("devise_decimales", 2))
    return {"code": code, "symbole": symbole, "decimales": decimales}


def formater_montant(d, devise, langue=None):
    """1234.5 → « 1 234,50 € » (fr) ou « €1,234.50 » (en)."""
    langue = langue or config.langue()
    d = _arrondi(Decimal(d), devise["decimales"])
    signe = "-" if d < 0 else ""
    entier, _, fraction = format(abs(d), "f").partition(".")
    groupes = []
    while len(entier) > 3:
        groupes.insert(0, entier[-3:])
        entier = entier[:-3]
    groupes.insert(0, entier)
    symbole = devise["symbole"]
    if langue == "en":
        nombre = ",".join(groupes) + ("." + fraction if fraction else "")
        return f"{signe}{symbole}{nombre}" if len(symbole) == 1 else f"{signe}{nombre} {symbole}"
    nombre = "\u202f".join(groupes) + ("," + fraction if fraction else "")
    return f"{signe}{nombre}\u00a0{symbole}"


def _date_affichee(iso):
    if not iso:
        return ""
    try:
        return datetime.date.fromisoformat(iso[:10]).strftime("%d/%m/%Y")
    except ValueError:
        return ""


def _taux_affiche(texte):
    return texte.replace(".", ",") if config.langue() != "en" else texte


# ---------------------------------------------------------------------------
# Fichier
# ---------------------------------------------------------------------------
def _lire():
    d = config.lire_donnees(NOM, {})
    if not isinstance(d, dict):
        d = {}
    entreprise = dict(ENTREPRISE_DEFAUT)
    entreprise.update(d.get("entreprise") or {})
    d["entreprise"] = entreprise
    d.setdefault("documents", [])
    d.setdefault("alertes_vues", [])
    return d


def _ecrire(d):
    config.ecrire_donnees(NOM, d)


def dossier_fichiers():
    """donnees\\factures\\ : logo de l'entreprise."""
    return os.path.join(config.DONNEES, NOM)


def _trouver(d, identifiant):
    doc = next((x for x in d["documents"] if x.get("id") == identifiant), None)
    if doc is None:
        raise ValueError("Document introuvable.")
    return doc


def configuree(d=None):
    d = d or _lire()
    return bool(d["entreprise"].get("nom"))


# ---------------------------------------------------------------------------
# Réglages de l'entreprise
# ---------------------------------------------------------------------------
def _court(valeur, limite):
    return " ".join(str(valeur or "").split())[:limite]


def _long(valeur, limite):
    lignes = [ligne.rstrip() for ligne in str(valeur or "").replace("\r\n", "\n").split("\n")]
    return "\n".join(lignes).strip()[:limite]


def _entier(valeur, nom, mini, maxi):
    try:
        n = int(str(valeur).strip())
    except (TypeError, ValueError):
        raise ValueError(f"{nom} : nombre entier attendu.") from None
    if not mini <= n <= maxi:
        raise ValueError(f"{nom} : entre {mini} et {maxi}.")
    return n


def _iban(valeur):
    iban = re.sub(r"\s+", "", str(valeur or "")).upper()[:40]
    # Contrôle (modulo 97) seulement pour un vrai IBAN (« FR76… ») ; un RIB local passe tel quel.
    if re.match(r"^[A-Z]{2}\d{2}[A-Z0-9]{10,30}$", iban):
        chiffres = "".join(str(int(c, 36)) for c in iban[4:] + iban[:4])
        if int(chiffres) % 97 != 1:
            raise ValueError("IBAN invalide (clé de contrôle).")
    return iban


def valider_entreprise(brut):
    brut = brut or {}
    e = dict(ENTREPRISE_DEFAUT)
    e["nom"] = _court(brut.get("nom"), 120)
    if not e["nom"]:
        raise ValueError("Indiquez le nom de l'entreprise.")
    e["adresse"] = _long(brut.get("adresse"), 400)
    e["email"] = _court(brut.get("email"), 120)
    e["telephone"] = _court(brut.get("telephone"), 40)
    identifiants = []
    for x in (brut.get("identifiants") or [])[:8]:
        libelle, valeur = _court((x or {}).get("libelle"), 40), _court((x or {}).get("valeur"), 80)
        if valeur:  # un libellé sans numéro n'est pas imprimé
            identifiants.append({"libelle": libelle, "valeur": valeur})
    e["identifiants"] = identifiants
    mode = brut.get("tva_mode") or "assujetti"
    if mode not in MODES_TVA:
        raise ValueError("Mention de TVA inconnue.")
    e["tva_mode"] = mode
    e["tva_taux"] = _txt(_decimal(brut.get("tva_taux") if brut.get("tva_taux") not in (None, "") else "0",
                                  "Taux de TVA", Decimal(0), Decimal(100), 2))
    e["tva_texte"] = _long(brut.get("tva_texte"), 300)
    if mode == "libre" and not e["tva_texte"]:
        raise ValueError("Indiquez la mention de TVA.")
    e["logo"] = _lire()["entreprise"].get("logo", "")
    e["iban"] = _iban(brut.get("iban"))
    e["bic"] = re.sub(r"\s+", "", str(brut.get("bic") or "")).upper()[:15]
    e["paiement_autre"] = _long(brut.get("paiement_autre"), 400)
    e["delai_jours"] = _entier(brut.get("delai_jours", 30), "Délai de paiement", 0, 365)
    e["validite_jours"] = _entier(brut.get("validite_jours", 30), "Validité des devis", 1, 365)
    e["penalites"] = _long(brut.get("penalites"), 600)
    devise = str(brut.get("devise") or "EUR").upper()
    if devise not in DEVISES:
        if devise != "AUTRE":
            raise ValueError("Devise inconnue.")
        code = _court(brut.get("devise_code"), 8).upper()
        if not re.match(r"^[A-Z]{2,8}$", code):
            raise ValueError("Code de devise invalide (lettres, ex. CHF).")
        devise = code
        e["devise_symbole"] = _court(brut.get("devise_symbole"), 8) or code
        e["devise_decimales"] = _entier(brut.get("devise_decimales", 2), "Décimales", 0, 3)
    e["devise"] = devise
    prefixes = []
    for genre in TYPES:
        p = re.sub(r"\s+", "", str(brut.get("prefixe_" + genre) or ENTREPRISE_DEFAUT["prefixe_" + genre])).upper()
        if not re.match(r"^[A-Z0-9]{1,10}$", p):
            raise ValueError("Préfixe invalide (lettres et chiffres, 10 au plus).")
        prefixes.append(p)
        e["prefixe_" + genre] = p
    if len(set(prefixes)) != len(prefixes):
        raise ValueError("Les préfixes des devis, factures et avoirs doivent être différents.")
    e["pied"] = _long(brut.get("pied"), 400)
    return e


def enregistrer_entreprise(brut):
    with _verrou:
        propre = valider_entreprise(brut)
        d = _lire()
        d["entreprise"] = propre
        _ecrire(d)
        return reglages()


def _chemin_logo(nom):
    return os.path.join(dossier_fichiers(), os.path.basename(nom)) if nom else ""


def _logo_data(nom):
    """Le logo en adresse « data: » (pour la page et le PDF), ou ""."""
    chemin = _chemin_logo(nom)
    mime = EXTENSIONS_LOGO.get(os.path.splitext(nom or "")[1].lower())
    if not chemin or not mime or not os.path.isfile(chemin):
        return ""
    with open(chemin, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode("ascii")


def enregistrer_logo(nom, contenu):
    """Copie le logo (contenu en base64) dans donnees\\factures\\. Les anciens
    logos restent : les documents déjà émis s'en servent encore."""
    ext = os.path.splitext(str(nom or ""))[1].lower()
    if ext not in EXTENSIONS_LOGO:
        raise ValueError("Logo : image PNG, JPG, GIF ou WebP attendue.")
    texte = str(contenu or "")
    if texte.startswith("data:"):
        texte = texte.split(",", 1)[-1]
    try:
        octets = base64.b64decode(texte, validate=True)
    except ValueError:
        raise ValueError("Logo illisible.") from None
    if not octets:
        raise ValueError("Logo illisible.")
    if len(octets) > MAX_LOGO:
        raise ValueError("Logo trop lourd (1 Mo au plus).")
    signatures = {".png": [b"\x89PNG"], ".jpg": [b"\xff\xd8"], ".jpeg": [b"\xff\xd8"],
                  ".gif": [b"GIF8"], ".webp": [b"RIFF"]}
    if not any(octets.startswith(s) for s in signatures[ext]):
        raise ValueError("Logo : le fichier n'est pas une image valide.")
    with _verrou:
        os.makedirs(dossier_fichiers(), exist_ok=True)
        fichier = f"logo-{uuid.uuid4().hex[:8]}{'.jpg' if ext == '.jpeg' else ext}"
        with open(os.path.join(dossier_fichiers(), fichier), "wb") as f:
            f.write(octets)
        d = _lire()
        d["entreprise"]["logo"] = fichier
        _ecrire(d)
        return reglages()


def retirer_logo():
    with _verrou:
        d = _lire()
        d["entreprise"]["logo"] = ""
        _ecrire(d)
        return reglages()


def reglages():
    d = _lire()
    e = dict(d["entreprise"])
    if not e.get("nom") and not e.get("penalites"):
        e["penalites"] = _texte(PENALITES_FR)  # proposition au premier réglage
    return {"entreprise": e, "logo_data": _logo_data(e.get("logo")), "configuree": configuree(d),
            "devise": devise_de(e), "prochains": {t: _prochain_numero(d, t, aujourdhui().year, e) for t in TYPES},
            "mention_293b": MENTION_293B}


# ---------------------------------------------------------------------------
# Documents : validation et calcul
# ---------------------------------------------------------------------------
def _client(brut):
    brut = brut or {}
    return {"contact_id": _court(brut.get("contact_id"), 40), "nom": _court(brut.get("nom"), 120),
            "adresse": _long(brut.get("adresse"), 400), "email": _court(brut.get("email"), 120),
            "identifiant": _court(brut.get("identifiant"), 120)}


def _ligne(brut, numero, taux_defaut):
    brut = brut or {}
    nom = f"Ligne {numero}"
    designation = _long(brut.get("designation"), 600)
    quantite = _decimal(brut.get("quantite") if brut.get("quantite") not in (None, "") else "1",
                        f"{nom}, quantité", places=3)
    if quantite == 0:
        raise ValueError(f"{nom}, quantité : valeur trop petite.")
    prix = _decimal(brut.get("prix") if brut.get("prix") not in (None, "") else "0", f"{nom}, prix", places=4)
    tva = _decimal(brut.get("tva") if brut.get("tva") not in (None, "") else taux_defaut,
                   f"{nom}, TVA", Decimal(0), Decimal(100), 2)
    sessions = [str(s)[:40] for s in (brut.get("sessions") or [])[:1000] if s]
    return {"designation": designation, "quantite": _txt(quantite), "unite": _court(brut.get("unite"), 20),
            "prix": _txt(prix), "tva": _txt(tva), **({"sessions": sessions} if sessions else {})}


def _lignes(brut, taux_defaut):
    lignes = []
    for i, x in enumerate((brut or [])[:MAX_LIGNES + 50], 1):
        x = x or {}
        vide = not str(x.get("designation") or "").strip() and str(x.get("prix") or "").strip() in ("", "0")
        if vide:
            continue  # ligne laissée vide : ignorée
        lignes.append(_ligne(x, i, taux_defaut))
    if len(lignes) > MAX_LIGNES:
        raise ValueError(f"{MAX_LIGNES} lignes au plus.")
    return lignes


def _remise(brut):
    brut = brut or {}
    genre = brut.get("type") or "aucune"
    if genre not in REMISES:
        raise ValueError("Type de remise inconnu.")
    if genre == "aucune":
        return {"type": "aucune", "valeur": "0"}
    valeur = _decimal(brut.get("valeur") if brut.get("valeur") not in (None, "") else "0", "Remise", Decimal(0),
                      Decimal(100) if genre == "pourcent" else None, 2 if genre == "pourcent" else 4)
    return {"type": genre, "valeur": _txt(valeur)}


def _contexte(doc, d):
    """L'entreprise du document : sa photo s'il est émis, sinon les réglages actuels."""
    return doc.get("entreprise") if doc.get("numero") and doc.get("entreprise") else d["entreprise"]


def tva_applicable(entreprise):
    return entreprise.get("tva_mode", "assujetti") == "assujetti"


def calculer(doc, entreprise):
    """Totaux exacts, arrondis à la devise : {lignes: [total HT], sous_total,
    remise, total_ht, tva: [{taux, base, montant}], total_tva, total_ttc}."""
    devise = devise_de(entreprise)
    dec = devise["decimales"]
    avec_tva = tva_applicable(entreprise)
    totaux_lignes, bases = [], {}
    for ligne in doc.get("lignes") or []:
        ht = _arrondi(Decimal(ligne["quantite"]) * Decimal(ligne["prix"]), dec)
        taux = Decimal(ligne["tva"]) if avec_tva else Decimal(0)
        totaux_lignes.append(ht)
        bases[taux] = bases.get(taux, Decimal(0)) + ht
    sous_total = sum(bases.values(), Decimal(0))
    remise_doc = doc.get("remise") or {"type": "aucune"}
    remise = Decimal(0)
    if remise_doc.get("type") == "pourcent":
        remise = _arrondi(sous_total * Decimal(remise_doc["valeur"]) / 100, dec)
    elif remise_doc.get("type") == "montant":
        remise = _arrondi(Decimal(remise_doc["valeur"]), dec)
        if remise > sous_total:
            raise ValueError("La remise dépasse le sous-total.")
    # Remise répartie au prorata des bases ; le dernier taux reçoit le reste
    # pour que la somme des parts soit exactement la remise.
    tva, total_tva, reparti = [], Decimal(0), Decimal(0)
    taux_tries = sorted(bases)
    for i, taux in enumerate(taux_tries):
        if i == len(taux_tries) - 1:
            part = remise - reparti
        else:
            part = _arrondi(remise * bases[taux] / sous_total, dec) if sous_total else Decimal(0)
        reparti += part
        base = bases[taux] - part
        montant = _arrondi(base * taux / 100, dec)
        total_tva += montant
        if avec_tva:
            tva.append({"taux": _txt(taux), "base": format(base, "f"), "montant": format(montant, "f")})
    total_ht = sous_total - remise
    return {"lignes": [format(x, "f") for x in totaux_lignes], "sous_total": format(sous_total, "f"),
            "remise": format(remise, "f"), "total_ht": format(total_ht, "f"), "tva": tva,
            "total_tva": format(total_tva, "f"), "total_ttc": format(total_ht + total_tva, "f"),
            "avec_tva": avec_tva, "devise": devise}


def _valider_brouillon(brut, d, existant=None):
    """Le contenu modifiable d'un brouillon, propre."""
    brut = brut or {}
    entreprise = d["entreprise"]
    taux_defaut = entreprise.get("tva_taux", "20") if tva_applicable(entreprise) else "0"
    propre = {
        "client": _client(brut.get("client")),
        "lignes": _lignes(brut.get("lignes"), taux_defaut),
        "remise": _remise(brut.get("remise")),
        "notes": _long(brut.get("notes"), 2000),
        "objet": _court(brut.get("objet"), 160),
        "prestation": _court(brut.get("prestation"), 120),
    }
    genre = (existant or {}).get("type") or brut.get("type")
    if genre not in TYPES:
        raise ValueError("Type de document inconnu.")
    if genre == "facture":
        propre["delai_jours"] = _entier(brut.get("delai_jours", entreprise.get("delai_jours", 30)),
                                        "Délai de paiement", 0, 365)
    if genre == "devis":
        propre["validite_jours"] = _entier(brut.get("validite_jours", entreprise.get("validite_jours", 30)),
                                           "Validité", 1, 365)
    calculer(propre, entreprise)  # refuse une remise impossible dès l'enregistrement
    return genre, propre


# ---------------------------------------------------------------------------
# États
# ---------------------------------------------------------------------------
def _avoirs_de(d, facture):
    return [x for x in d["documents"] if x.get("type") == "avoir" and x.get("origine_id") == facture["id"]]


def _sommes(doc, d):
    """(total TTC, payé, avoirs émis, reste) d'un document, en Decimal."""
    entreprise = _contexte(doc, d)
    ttc = Decimal(calculer(doc, entreprise)["total_ttc"])
    paye = sum((Decimal(p["montant"]) for p in doc.get("paiements") or []), Decimal(0))
    avoirs = Decimal(0)
    if doc.get("type") == "facture":
        for a in _avoirs_de(d, doc):
            if a.get("numero"):
                avoirs += Decimal(calculer(a, _contexte(a, d))["total_ttc"])
    reste = max(ttc - avoirs - paye, Decimal(0)) if doc.get("type") == "facture" and doc.get("numero") else Decimal(0)
    return ttc, paye, avoirs, reste


def etat(doc, d, jour=None):
    """Code d'état affiché : brouillon, envoye/envoyee, accepte, refuse,
    facture, expire, partielle, payee, retard, annulee, emis."""
    jour = (jour or aujourdhui()).isoformat()
    if not doc.get("numero"):
        return "brouillon"
    genre = doc.get("type")
    if genre == "avoir":
        return "emis"
    if genre == "devis":
        if doc.get("statut") == "refuse":
            return "refuse"
        if doc.get("facture_id") and any(x.get("id") == doc["facture_id"] for x in d["documents"]):
            return "facture"
        if doc.get("statut") == "accepte":
            return "accepte"
        if doc.get("validite") and doc["validite"] < jour:
            return "expire"
        return "envoye"
    ttc, paye, avoirs, reste = _sommes(doc, d)
    if ttc - avoirs <= 0 and paye == 0:
        return "annulee"
    if reste == 0:
        return "payee"
    if doc.get("echeance") and doc["echeance"] < jour:
        return "retard"
    if paye > 0:
        return "partielle"
    return "envoyee"


def _resume_doc(doc, d, jour=None):
    entreprise = _contexte(doc, d)
    totaux = calculer(doc, entreprise)
    ttc, paye, avoirs, reste = _sommes(doc, d)
    origine = None
    if doc.get("origine_id"):
        o = next((x for x in d["documents"] if x.get("id") == doc["origine_id"]), None)
        origine = o.get("numero") if o else None
    return {"id": doc["id"], "type": doc["type"], "numero": doc.get("numero"), "etat": etat(doc, d, jour),
            "client": (doc.get("client") or {}).get("nom", ""), "objet": doc.get("objet", ""),
            "date": doc.get("date"), "echeance": doc.get("echeance"), "validite": doc.get("validite"),
            "total_ht": totaux["total_ht"], "total_ttc": totaux["total_ttc"], "paye": format(paye, "f"),
            "avoirs": format(avoirs, "f"), "reste": format(reste, "f"), "devise": totaux["devise"],
            "cree": doc.get("cree"), "modifie": doc.get("modifie"),
            "pdf": bool(doc.get("pdf") and os.path.isfile(doc["pdf"])),
            "origine": origine, "devis_id": doc.get("devis_id"), "facture_id": doc.get("facture_id")}


def _cle_tri(doc):
    # Brouillons d'abord (les plus récents), puis par date d'émission et numéro.
    if not doc.get("numero"):
        return (1, doc.get("modifie") or "", "")
    return (0, doc.get("date") or "", doc.get("numero") or "")


def resume(d=None, jour=None):
    """Chiffres de l'en-tête et de la carte d'accueil, par devise :
    facturé ce mois (factures − avoirs), encaissé ce mois, impayé, en retard."""
    d = d or _lire()
    jour = jour or aujourdhui()
    mois = jour.isoformat()[:7]
    par_devise = {}

    def compte(devise):
        return par_devise.setdefault(devise["code"], {"devise": devise, "facture_mois": Decimal(0),
                                                      "encaisse_mois": Decimal(0), "impaye": Decimal(0),
                                                      "retard": Decimal(0)})
    nb_retard, devis_attente = 0, 0
    for doc in d["documents"]:
        if not doc.get("numero"):
            continue
        devise = devise_de(_contexte(doc, d))
        if doc["type"] == "devis":
            if etat(doc, d, jour) == "envoye":
                devis_attente += 1
            continue
        c = compte(devise)
        ttc = Decimal(calculer(doc, _contexte(doc, d))["total_ttc"])
        if (doc.get("date") or "")[:7] == mois:
            c["facture_mois"] += ttc if doc["type"] == "facture" else -ttc
        if doc["type"] != "facture":
            continue
        for p in doc.get("paiements") or []:
            if p.get("date", "")[:7] == mois:
                c["encaisse_mois"] += Decimal(p["montant"])
        _, _, _, reste = _sommes(doc, d)
        c["impaye"] += reste
        if etat(doc, d, jour) == "retard":
            nb_retard += 1
            c["retard"] += reste
    devises = []
    for c in par_devise.values():
        dec = c["devise"]["decimales"]
        devises.append({"devise": c["devise"], **{k: _montant_txt(c[k], dec) for k in
                                                  ("facture_mois", "encaisse_mois", "impaye", "retard")}})
    principale = devise_de(d["entreprise"])["code"]
    devises.sort(key=lambda x: (x["devise"]["code"] != principale, x["devise"]["code"]))
    return {"devises": devises, "nb_retard": nb_retard, "devis_attente": devis_attente, "mois": mois}


# ---------------------------------------------------------------------------
# Documents : actions
# ---------------------------------------------------------------------------
def _complet(doc, d, jour=None):
    entreprise = _contexte(doc, d)
    r = dict(doc)
    r["resume"] = _resume_doc(doc, d, jour)
    r["totaux"] = calculer(doc, entreprise)
    r["avoirs_lies"] = [{"id": a["id"], "numero": a.get("numero")} for a in _avoirs_de(d, doc)]
    return r


def document(identifiant):
    with _verrou:
        d = _lire()
        return _complet(_trouver(d, identifiant), d)


def _nouveau(d, genre, contenu, **extra):
    if len(d["documents"]) >= MAX_DOCUMENTS:
        raise ValueError("Trop de documents.")
    horodatage = maintenant().isoformat()
    doc = {"id": uuid.uuid4().hex[:12], "type": genre, "numero": None, "statut": "brouillon",
           "cree": horodatage, "modifie": horodatage, "paiements": [], **contenu, **extra}
    d["documents"].append(doc)
    return doc


def enregistrer(brut):
    """Créer (sans id) ou modifier un brouillon."""
    brut = brut or {}
    with _verrou:
        d = _lire()
        existant = _trouver(d, brut["id"]) if brut.get("id") else None
        if existant and existant.get("numero"):
            raise ValueError("Document émis : il n'est plus modifiable. Pour corriger une facture, créez un avoir.")
        genre, propre = _valider_brouillon(brut, d, existant)
        if existant is None:
            extra = {}
            if genre == "avoir":
                raise ValueError("Un avoir se crée depuis la facture à corriger.")
            doc = _nouveau(d, genre, propre, **extra)
        else:
            existant.update(propre)
            existant["modifie"] = maintenant().isoformat()
            doc = existant
        _ecrire(d)
        return _complet(doc, d)


def calculer_brouillon(brut):
    """Totaux en direct pendant la saisie (sans rien enregistrer)."""
    d = _lire()
    existant = None
    if (brut or {}).get("id"):
        existant = next((x for x in d["documents"] if x.get("id") == brut["id"]), None)
    _, propre = _valider_brouillon({**(brut or {}), "type": (existant or {}).get("type") or (brut or {}).get("type")},
                                   d, existant)
    return calculer(propre, d["entreprise"])


def supprimer(identifiant):
    """Seul un brouillon se supprime (un document émis reste, numérotation continue)."""
    with _verrou:
        d = _lire()
        doc = _trouver(d, identifiant)
        if doc.get("numero"):
            raise ValueError("Un document émis ne se supprime pas.")
        d["documents"] = [x for x in d["documents"] if x["id"] != identifiant]
        # Brouillon de facture issu d'un devis : le devis (toujours accepté)
        # pourra être transformé à nouveau.
        for x in d["documents"]:
            if x.get("facture_id") == identifiant:
                x["facture_id"] = None
        _ecrire(d)
        return {"supprimes": 1}


def dupliquer(identifiant):
    with _verrou:
        d = _lire()
        source = _trouver(d, identifiant)
        genre = "facture" if source["type"] == "avoir" else source["type"]
        contenu = {k: source.get(k) for k in ("client", "lignes", "remise", "notes", "objet", "prestation")}
        contenu["lignes"] = [{k: v for k, v in ligne.items() if k != "sessions"} for ligne in contenu["lignes"] or []]
        doc = _nouveau(d, genre, contenu)
        _ecrire(d)
        return _complet(doc, d)


def _prochain_numero(d, genre, annee, entreprise=None):
    prefixe = (entreprise or d["entreprise"]).get("prefixe_" + genre) or ENTREPRISE_DEFAUT["prefixe_" + genre]
    motif = re.compile(rf"^{re.escape(prefixe)}-{annee}-(\d+)$")
    dernier = 0
    for doc in d["documents"]:
        m = motif.match(doc.get("numero") or "")
        if m:
            dernier = max(dernier, int(m.group(1)))
    return f"{prefixe}-{annee}-{dernier + 1:03d}"


def emettre(identifiant, generer=True):
    """Attribue le numéro et la date, fige le document (photo de l'entreprise)
    puis crée le PDF. Renvoie {document, pdf, pdf_erreur}."""
    with _verrou:
        d = _lire()
        doc = _trouver(d, identifiant)
        if doc.get("numero"):
            raise ValueError("Ce document est déjà émis.")
        if not configuree(d):
            raise ValueError("Renseignez d'abord votre entreprise (Réglages).")
        if not doc.get("client", {}).get("nom"):
            raise ValueError("Indiquez le client.")
        if not doc.get("lignes") or not any(ligne.get("designation") for ligne in doc["lignes"]):
            raise ValueError("Ajoutez au moins une ligne avec une désignation.")
        if any(not ligne.get("designation") for ligne in doc["lignes"]):
            raise ValueError("Chaque ligne doit avoir une désignation.")
        entreprise = dict(d["entreprise"])
        totaux = calculer(doc, entreprise)
        if Decimal(totaux["total_ttc"]) <= 0:
            raise ValueError("Le total doit être supérieur à zéro.")
        jour = aujourdhui()
        if doc["type"] == "avoir":
            facture = next((x for x in d["documents"] if x.get("id") == doc.get("origine_id")), None)
            if not facture or not facture.get("numero"):
                raise ValueError("Facture d'origine introuvable.")
            ttc_facture, _, avoirs, _ = _sommes(facture, d)
            if Decimal(totaux["total_ttc"]) > ttc_facture - avoirs:
                raise ValueError("L'avoir dépasse le montant restant de la facture.")
        prefixe = entreprise["prefixe_" + doc["type"]]
        # Numérotation chronologique : pas d'émission datée avant la précédente.
        for x in d["documents"]:
            if (x.get("numero") or "").startswith(f"{prefixe}-") and (x.get("date") or "") > jour.isoformat():
                raise ValueError("Un document de cette série porte une date postérieure à aujourd'hui : "
                                 "vérifiez la date de l'ordinateur.")
        doc["numero"] = _prochain_numero(d, doc["type"], jour.year, entreprise)
        doc["date"] = jour.isoformat()
        doc["statut"] = "emis"
        doc["entreprise"] = entreprise
        if doc["type"] == "facture":
            doc["echeance"] = (jour + datetime.timedelta(days=int(doc.get("delai_jours", entreprise["delai_jours"])))).isoformat()
        if doc["type"] == "devis":
            doc["validite"] = (jour + datetime.timedelta(days=int(doc.get("validite_jours", entreprise["validite_jours"])))).isoformat()
        doc["modifie"] = maintenant().isoformat()
        _ecrire(d)
    resultat = {"pdf": None, "pdf_erreur": None}
    if generer:
        try:
            resultat["pdf"] = generer_pdf(identifiant)
        except (ValueError, OSError, subprocess.SubprocessError) as e:
            resultat["pdf_erreur"] = str(e)
    return {"document": document(identifiant), **resultat}


def changer_statut(identifiant, statut):
    """Devis émis : accepté, refusé, ou de nouveau « envoyé »."""
    if statut not in ("accepte", "refuse", "emis"):
        raise ValueError("Statut inconnu.")
    with _verrou:
        d = _lire()
        doc = _trouver(d, identifiant)
        if doc["type"] != "devis" or not doc.get("numero"):
            raise ValueError("Seul un devis émis peut être accepté ou refusé.")
        if statut == "refuse" and doc.get("facture_id") and any(x["id"] == doc["facture_id"] for x in d["documents"]):
            raise ValueError("Ce devis a déjà été transformé en facture.")
        doc["statut"] = statut
        doc["modifie"] = maintenant().isoformat()
        _ecrire(d)
        return _complet(doc, d)


def transformer(identifiant):
    """Devis émis → nouvelle facture en brouillon (le devis passe « accepté »)."""
    with _verrou:
        d = _lire()
        devis = _trouver(d, identifiant)
        if devis["type"] != "devis" or not devis.get("numero"):
            raise ValueError("Émettez d'abord le devis.")
        if devis.get("statut") == "refuse":
            raise ValueError("Ce devis est refusé.")
        if devis.get("facture_id") and any(x["id"] == devis["facture_id"] for x in d["documents"]):
            raise ValueError("Ce devis a déjà été transformé en facture.")
        contenu = {k: devis.get(k) for k in ("client", "lignes", "remise", "objet", "prestation")}
        contenu["notes"] = devis.get("notes", "")
        contenu["delai_jours"] = d["entreprise"].get("delai_jours", 30)
        facture = _nouveau(d, "facture", contenu, devis_id=devis["id"], devis_numero=devis["numero"])
        devis["facture_id"] = facture["id"]
        devis["statut"] = "accepte"
        devis["modifie"] = maintenant().isoformat()
        _ecrire(d)
        return _complet(facture, d)


def creer_avoir(identifiant):
    """Facture émise → avoir en brouillon reprenant ses lignes (à ajuster)."""
    with _verrou:
        d = _lire()
        facture = _trouver(d, identifiant)
        if facture["type"] != "facture" or not facture.get("numero"):
            raise ValueError("Un avoir se crée sur une facture émise.")
        contenu = {k: facture.get(k) for k in ("client", "lignes", "remise", "objet", "prestation")}
        contenu["lignes"] = [{k: v for k, v in ligne.items() if k != "sessions"} for ligne in contenu["lignes"] or []]
        contenu["notes"] = ""
        avoir = _nouveau(d, "avoir", contenu, origine_id=facture["id"], origine_numero=facture["numero"],
                         origine_date=facture.get("date"))
        _ecrire(d)
        return _complet(avoir, d)


def ajouter_paiement(identifiant, brut):
    brut = brut or {}
    with _verrou:
        d = _lire()
        doc = _trouver(d, identifiant)
        if doc["type"] != "facture" or not doc.get("numero"):
            raise ValueError("Un paiement s'enregistre sur une facture émise.")
        devise = devise_de(_contexte(doc, d))
        try:
            jour = datetime.date.fromisoformat(str(brut.get("date") or "")[:10])
        except ValueError:
            raise ValueError("Date du paiement invalide.") from None
        montant = _decimal(brut.get("montant"), "Montant", places=devise["decimales"])
        if montant <= 0:
            raise ValueError("Montant : valeur trop petite.")
        _, _, _, reste = _sommes(doc, d)
        if montant > reste:
            raise ValueError(f"Le montant dépasse le reste à payer ({formater_montant(reste, devise)}).")
        moyen = brut.get("moyen") or "virement"
        if moyen not in MOYENS:
            raise ValueError("Moyen de paiement inconnu.")
        doc.setdefault("paiements", []).append({"id": uuid.uuid4().hex[:10], "date": jour.isoformat(),
                                                "montant": _montant_txt(montant, devise["decimales"]),
                                                "moyen": moyen, "note": _court(brut.get("note"), 120)})
        doc["paiements"].sort(key=lambda p: p["date"])
        doc["modifie"] = maintenant().isoformat()
        _ecrire(d)
        return _complet(doc, d)


def supprimer_paiement(identifiant, paiement_id):
    with _verrou:
        d = _lire()
        doc = _trouver(d, identifiant)
        avant = len(doc.get("paiements") or [])
        doc["paiements"] = [p for p in doc.get("paiements") or [] if p.get("id") != paiement_id]
        if len(doc["paiements"]) == avant:
            raise ValueError("Paiement introuvable.")
        doc["modifie"] = maintenant().isoformat()
        _ecrire(d)
        return _complet(doc, d)


def lister():
    with _verrou:
        d = _lire()
        jour = aujourdhui()
        docs = sorted(d["documents"], key=_cle_tri, reverse=True)
        clients = {}
        for doc in docs:
            c = doc.get("client") or {}
            if c.get("nom") and c["nom"].lower() not in clients:
                clients[c["nom"].lower()] = c
        e = d["entreprise"]
        return {"configuree": configuree(d), "documents": [_resume_doc(x, d, jour) for x in docs],
                "resume": resume(d, jour), "aujourdhui": jour.isoformat(),
                "devise": devise_de(e), "tva_applicable": tva_applicable(e), "tva_taux": e.get("tva_taux", "20"),
                "delai_jours": e.get("delai_jours", 30), "validite_jours": e.get("validite_jours", 30),
                "clients": list(clients.values())[:200], "temps": temps_disponible()}


# ---------------------------------------------------------------------------
# Bulle : factures en retard (une seule fois chacune)
# ---------------------------------------------------------------------------
def alertes_dues():
    with _verrou:
        d = _lire()
        jour = aujourdhui()
        vues = set(d["alertes_vues"])
        dues = []
        for doc in d["documents"]:
            if doc.get("type") != "facture" or not doc.get("numero"):
                continue
            ident = "retard-" + doc["id"]
            if ident in vues or etat(doc, d, jour) != "retard":
                continue
            _, _, _, reste = _sommes(doc, d)
            dues.append({"id": ident, "titre": _texte("Facture en retard"),
                         "detail": _texte("{numero} · {client} : {reste} à encaisser (échéance du {date})",
                                          numero=doc["numero"], client=doc["client"].get("nom", ""),
                                          reste=formater_montant(reste, devise_de(_contexte(doc, d))),
                                          date=_date_affichee(doc.get("echeance")))})
        return dues


def marquer_alerte(identifiant):
    with _verrou:
        d = _lire()
        if identifiant in d["alertes_vues"]:
            return True
        if not any("retard-" + x.get("id", "") == identifiant for x in d["documents"]):
            return False
        d["alertes_vues"].append(identifiant)
        _ecrire(d)
        return True


# ---------------------------------------------------------------------------
# Heures de l'application Temps
# ---------------------------------------------------------------------------
def _temps():
    try:
        import temps  # application voisine, facultative
        return temps
    except ImportError:
        return None


def temps_disponible():
    """Vrai si l'application Temps est là et active."""
    if _temps() is None:
        return False
    active = getattr(config, "app_active", None)
    return bool(active("temps")) if active else True


def _sessions_facturees(d):
    ids = set()
    for doc in d["documents"]:
        if doc.get("type") == "facture":
            for ligne in doc.get("lignes") or []:
                ids.update(ligne.get("sessions") or [])
    return ids


def heures(projet="", debut="", fin=""):
    """Sessions de Temps à facturer : {disponible, projets, sessions}."""
    temps = _temps()
    if temps is None:
        return {"disponible": False, "projets": [], "sessions": []}
    d = _lire()
    deja = _sessions_facturees(d)
    toutes = temps.sessions("tout")
    projets = sorted({s["projet"] for s in toutes}, key=str.lower)
    choisies = []
    for s in toutes:
        if projet and s["projet"] != projet:
            continue
        if debut and s["debut"][:10] < debut[:10]:
            continue
        if fin and s["debut"][:10] > fin[:10]:
            continue
        choisies.append({"id": s["id"], "projet": s["projet"], "note": s.get("note", ""), "debut": s["debut"],
                         "fin": s["fin"], "minutes": int(s.get("minutes") or 0), "facturee": s["id"] in deja})
    choisies.sort(key=lambda s: s["debut"])
    return {"disponible": True, "projets": projets, "sessions": choisies}


def _heures_decimales(minutes):
    """Minutes → heures au centième (10 min → 0,17 h), en Decimal."""
    return (Decimal(int(minutes)) / Decimal(60)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def lignes_heures(ids, taux_horaire, regrouper="projet"):
    """Les sessions choisies en lignes de facture (unité « h », prix = taux horaire)."""
    temps = _temps()
    if temps is None:
        raise ValueError("L'application Temps n'est pas disponible.")
    taux = _decimal(taux_horaire, "Taux horaire", Decimal(0), places=4)
    voulues = set(ids or [])
    if not voulues:
        raise ValueError("Choisissez au moins une session.")
    d = _lire()
    entreprise = d["entreprise"]
    tva = entreprise.get("tva_taux", "20") if tva_applicable(entreprise) else "0"
    sessions = sorted((s for s in temps.sessions("tout") if s["id"] in voulues), key=lambda s: s["debut"])
    if not sessions:
        raise ValueError("Sessions introuvables.")
    groupes = {}
    for s in sessions:
        cle = s["id"] if regrouper == "session" else (s["projet"], s["debut"][:10]) if regrouper == "jour" else s["projet"]
        groupes.setdefault(cle, []).append(s)
    lignes = []
    for liste in groupes.values():
        minutes = sum(int(s.get("minutes") or 0) for s in liste)
        projet = liste[0]["projet"]
        premier, dernier = _date_affichee(liste[0]["debut"]), _date_affichee(liste[-1]["debut"])
        if regrouper == "session":
            note = liste[0].get("note") or ""
            designation = f"{projet} – {premier}" + (f" : {note}" if note else "")
        elif premier == dernier:
            designation = f"{projet} – {premier}"
        else:
            designation = _texte("{projet} – du {debut} au {fin}", projet=projet, debut=premier, fin=dernier)
        lignes.append({"designation": designation, "quantite": _txt(_heures_decimales(minutes)), "unite": "h",
                       "prix": _txt(taux), "tva": tva, "sessions": [s["id"] for s in liste]})
    return {"lignes": lignes}


# ---------------------------------------------------------------------------
# HTML imprimable et PDF
# ---------------------------------------------------------------------------
def _e(texte):
    return html.escape(str(texte or ""))


def _multi(texte):
    return "<br>".join(_e(ligne) for ligne in str(texte or "").split("\n"))


STYLE_PDF = """
@page { size: A4; margin: 14mm 15mm 18mm; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font: 9.5pt/1.45 "Segoe UI", Arial, sans-serif; color: #1f1f23; background: #ffffff; }
@media screen { body { padding: 14mm 15mm; max-width: 210mm; margin: 0 auto; } }
.entete { display: flex; justify-content: space-between; align-items: flex-start; gap: 18mm; }
.emetteur { max-width: 95mm; color: #3f3f46; }
.emetteur img { display: block; max-height: 20mm; max-width: 60mm; margin-bottom: 4mm; }
.emetteur .nom { font-size: 12pt; font-weight: 600; color: #1f1f23; }
.titre { text-align: right; flex: none; }
.titre td, .nw { white-space: nowrap; }
.titre h1 { margin: 0 0 3mm; font-size: 19pt; font-weight: 600; letter-spacing: .12em; }
.titre table { margin-left: auto; border-collapse: collapse; }
.titre td { padding: .3mm 0 .3mm 5mm; text-align: right; }
.titre td:first-child { color: #6b6b74; }
.client { margin: 9mm 0 7mm auto; width: 82mm; padding: 3mm 4mm; border: 1px solid #d4d4d8; border-radius: 2mm; }
.client .lib { font-size: 7.5pt; text-transform: uppercase; letter-spacing: .08em; color: #6b6b74; margin-bottom: 1mm; }
.client .nom { font-weight: 600; font-size: 10.5pt; }
.objet { margin: 0 0 4mm; font-weight: 600; }
table.lignes { width: 100%; border-collapse: collapse; }
table.lignes th { text-align: left; font-size: 7.5pt; font-weight: 600; text-transform: uppercase; letter-spacing: .06em;
  color: #6b6b74; padding: 2mm 2mm; border-bottom: 1px solid #1f1f23; }
table.lignes td { padding: 2.2mm 2mm; border-bottom: 1px solid #e4e4e7; vertical-align: top; }
table.lignes tr { page-break-inside: avoid; }
.num { text-align: right !important; white-space: nowrap; font-variant-numeric: tabular-nums; }
.bas { display: flex; justify-content: space-between; gap: 10mm; margin-top: 5mm; page-break-inside: avoid; }
.notes { flex: 1; color: #3f3f46; }
table.totaux { width: 78mm; border-collapse: collapse; flex: none; }
table.totaux td { padding: 1.2mm 2mm; }
table.totaux td:first-child { color: #52525b; }
table.totaux tr.fort td { font-weight: 700; font-size: 11pt; color: #1f1f23; border-top: 1.5px solid #1f1f23; padding-top: 2mm; }
.mentions { margin-top: 9mm; font-size: 8pt; color: #52525b; page-break-inside: avoid; }
.mentions p { margin: 0 0 1.6mm; }
.mentions h3 { margin: 4mm 0 1mm; font-size: 7.5pt; text-transform: uppercase; letter-spacing: .08em; color: #6b6b74; font-weight: 600; }
.accord { margin-top: 8mm; margin-left: auto; width: 78mm; height: 28mm; border: 1px solid #d4d4d8; border-radius: 2mm;
  padding: 2.5mm 3mm; font-size: 8pt; color: #6b6b74; page-break-inside: avoid; }
.pied { margin-top: 12mm; text-align: center; font-size: 7.2pt; color: #8a8a93; }
@media print { .pied { display: none; } }
.filigrane { position: fixed; top: 38%; left: 0; right: 0; text-align: center; font-size: 80pt; font-weight: 700;
  color: rgba(0, 0, 0, .06); transform: rotate(-28deg); letter-spacing: .1em; }
"""


def _css_texte(texte):
    """Un texte en chaîne CSS sûre (pied de page imprimé par @page)."""
    sortie = []
    for c in str(texte or ""):
        if c == "\n":
            sortie.append("\\A ")
        elif c in '\\"<>' or ord(c) < 32:
            sortie.append(f"\\{ord(c):X} ")
        else:
            sortie.append(c)
    return '"' + "".join(sortie) + '"'


def html_document(doc, d, jour=None):
    """La page imprimable du document (texte échappé, logo intégré)."""
    entreprise = _contexte(doc, d)
    devise = devise_de(entreprise)
    totaux = calculer(doc, entreprise)
    avec_tva = totaux["avec_tva"]
    brouillon = not doc.get("numero")
    jour = jour or aujourdhui()

    def m(valeur):
        return _e(formater_montant(Decimal(valeur), devise))

    def qte(texte):
        return _e(_taux_affiche(texte))

    genre = doc["type"]
    titre = {"devis": "DEVIS", "facture": "FACTURE", "avoir": "AVOIR"}[genre]
    meta = [(_texte("N°"), doc.get("numero") or "—"),
            (_texte("Date"), _date_affichee(doc.get("date")) if doc.get("date") else _texte("à l'émission"))]
    if genre == "facture" and doc.get("echeance"):
        meta.append((_texte("Échéance"), _date_affichee(doc["echeance"])))
    if genre == "devis" and doc.get("validite"):
        meta.append((_texte("Valable jusqu'au"), _date_affichee(doc["validite"])))
    logo = _logo_data(entreprise.get("logo"))
    identifiants = [f"{_e(i['libelle'])} {_e(i['valeur'])}".strip() for i in entreprise.get("identifiants") or []]
    contacts = [x for x in (entreprise.get("email"), (_texte("Tél.") + " " + entreprise["telephone"]) if entreprise.get("telephone") else "") if x]
    client = doc.get("client") or {}

    entetes = [f"<th>{_e(_texte('Désignation'))}</th>", f"<th class='num'>{_e(_texte('Qté'))}</th>",
               f"<th>{_e(_texte('Unité'))}</th>",
               f"<th class='num'>{_e(_texte('Prix unit. HT' if avec_tva else 'Prix unit.'))}</th>"]
    if avec_tva:
        entetes.append(f"<th class='num'>{_e(_texte('TVA'))}</th>")
    entetes.append(f"<th class='num'>{_e(_texte('Total HT' if avec_tva else 'Montant'))}</th>")
    lignes_html = []
    for ligne, total in zip(doc.get("lignes") or [], totaux["lignes"]):
        cellules = [f"<td>{_multi(ligne.get('designation'))}</td>", f"<td class='num'>{qte(ligne['quantite'])}</td>",
                    f"<td>{_e(ligne.get('unite'))}</td>",
                    f"<td class='num'>{_e(formater_montant(Decimal(ligne['prix']), {**devise, 'decimales': max(devise['decimales'], len(ligne['prix'].partition('.')[2]))}))}</td>"]
        if avec_tva:
            cellules.append(f"<td class='num'>{qte(ligne['tva'])}{'%' if config.langue() == 'en' else ' %'}</td>")
        cellules.append(f"<td class='num'>{m(total)}</td>")
        lignes_html.append("<tr>" + "".join(cellules) + "</tr>")

    tot = []
    remise = Decimal(totaux["remise"])
    if remise:
        tot.append((_texte("Sous-total HT" if avec_tva else "Sous-total"), m(totaux["sous_total"])))
        r = doc.get("remise") or {}
        libelle = _texte("Remise ({p} %)", p=_taux_affiche(r["valeur"])) if r.get("type") == "pourcent" else _texte("Remise")
        tot.append((libelle, "−" + m(totaux["remise"])))
    if avec_tva:
        tot.append((_texte("Total HT"), m(totaux["total_ht"])))
        for t in totaux["tva"]:
            tot.append((_texte("TVA {t} %", t=_taux_affiche(t["taux"])), m(t["montant"])))
        dernier = _texte("Total de l'avoir") if genre == "avoir" else _texte("Total TTC")
    else:
        dernier = _texte("Total de l'avoir") if genre == "avoir" else _texte("Net à payer") if genre == "facture" else _texte("Total")
    totaux_html = "".join(f"<tr><td>{_e(a)}</td><td class='num'>{b}</td></tr>" for a, b in tot)
    totaux_html += f"<tr class='fort'><td>{_e(dernier)}</td><td class='num'>{m(totaux['total_ttc'])}</td></tr>"

    mentions = []
    if genre == "avoir" and doc.get("origine_numero"):
        mentions.append(_e(_texte("Avoir sur la facture {numero} du {date}.", numero=doc["origine_numero"],
                                  date=_date_affichee(doc.get("origine_date")))))
    if doc.get("prestation"):
        mentions.append(_e(_texte("Prestation : {texte}", texte=doc["prestation"])))
    mode = entreprise.get("tva_mode")
    if mode == "franchise":
        mentions.append(_e(_texte(MENTION_293B)))
    elif mode == "libre" and entreprise.get("tva_texte"):
        mentions.append(_multi(entreprise["tva_texte"]))
    if genre == "facture":
        delai = int(doc.get("delai_jours", entreprise.get("delai_jours", 30)))
        echeance = doc.get("echeance") or (jour + datetime.timedelta(days=delai)).isoformat()
        mentions.append(_e(_texte("Conditions de paiement : à réception.") if delai == 0 else
                           _texte("Conditions de paiement : {n} jours, soit au plus tard le {date}.",
                                  n=delai, date=_date_affichee(echeance))))
        if entreprise.get("penalites"):
            mentions.append(_multi(_texte(entreprise["penalites"])))
    if genre == "devis":
        validite = doc.get("validite") or (jour + datetime.timedelta(days=int(doc.get("validite_jours", 30)))).isoformat()
        mentions.append(_e(_texte("Devis valable jusqu'au {date}.", date=_date_affichee(validite))))
    reglement = []
    if genre != "avoir":
        if entreprise.get("iban"):
            iban = " ".join(entreprise["iban"][i:i + 4] for i in range(0, len(entreprise["iban"]), 4))
            reglement.append(f"{_e(_texte('IBAN'))} {_e(iban)}" + (f" · {_e(_texte('BIC'))} {_e(entreprise['bic'])}" if entreprise.get("bic") else ""))
        if entreprise.get("paiement_autre"):
            reglement.append(_multi(entreprise["paiement_autre"]))

    pied = " · ".join(x for x in [_e(entreprise.get("nom"))] + identifiants if x)
    if entreprise.get("pied"):
        pied += "<br>" + _multi(entreprise["pied"])
    # Pied de chaque page imprimée (marges de @page) et numéro de page.
    pied_texte = " · ".join(x for x in [entreprise.get("nom")] + [f"{i['libelle']} {i['valeur']}".strip()
                                                                   for i in entreprise.get("identifiants") or []] if x)
    if entreprise.get("pied"):
        pied_texte += "\n" + entreprise["pied"]
    style_pied = ("@page { @bottom-center { content: " + _css_texte(pied_texte) + "; font: 7pt 'Segoe UI', Arial, sans-serif; "
                  "color: #8a8a93; white-space: pre-wrap; text-align: center; vertical-align: top; padding-top: 3mm; } "
                  "@bottom-right { content: counter(page) ' / ' counter(pages); font: 7pt 'Segoe UI', Arial, sans-serif; "
                  "color: #8a8a93; vertical-align: top; padding-top: 3mm; } }")

    morceaux = [
        "<!doctype html><html lang='" + ("en" if config.langue() == "en" else "fr") + "'><head><meta charset='utf-8'>",
        f"<title>{_e(doc.get('numero') or _texte(titre.capitalize()))}</title><style>{STYLE_PDF}{style_pied}</style></head><body>",
        f"<div class='filigrane'>{_e(_texte('BROUILLON'))}</div>" if brouillon else "",
        "<div class='entete'><div class='emetteur'>",
        f"<img src='{logo}' alt=''>" if logo else "",
        f"<div class='nom'>{_e(entreprise.get('nom'))}</div>",
        f"<div>{_multi(entreprise.get('adresse'))}</div>" if entreprise.get("adresse") else "",
        f"<div>{' · '.join(f"<span class='nw'>{_e(x)}</span>" for x in contacts)}</div>" if contacts else "",
        f"<div>{'<br>'.join(identifiants)}</div>" if identifiants else "",
        "</div><div class='titre'>",
        f"<h1>{_e(_texte(titre))}</h1><table>",
        "".join(f"<tr><td>{_e(a)}</td><td>{_e(b)}</td></tr>" for a, b in meta),
        "</table></div></div>",
        "<div class='client'>",
        f"<div class='lib'>{_e(_texte('Destinataire'))}</div><div class='nom'>{_e(client.get('nom'))}</div>",
        f"<div>{_multi(client.get('adresse'))}</div>" if client.get("adresse") else "",
        f"<div>{_e(client.get('identifiant'))}</div>" if client.get("identifiant") else "",
        f"<div>{_e(client.get('email'))}</div>" if client.get("email") else "",
        "</div>",
        f"<div class='objet'>{_e(doc['objet'])}</div>" if doc.get("objet") else "",
        "<table class='lignes'><thead><tr>", "".join(entetes), "</tr></thead><tbody>", "".join(lignes_html),
        "</tbody></table>",
        "<div class='bas'>",
        f"<div class='notes'>{_multi(doc.get('notes'))}</div>",
        f"<table class='totaux'>{totaux_html}</table></div>",
        "<div class='mentions'>", "".join(f"<p>{x}</p>" for x in mentions),
        (f"<h3>{_e(_texte('Règlement'))}</h3>" + "".join(f"<p>{x}</p>" for x in reglement)) if reglement else "",
        "</div>",
        f"<div class='accord'>{_e(_texte('Bon pour accord (date et signature)'))}</div>" if genre == "devis" else "",
        f"<div class='pied'>{pied}</div>",
        "</body></html>",
    ]
    return "".join(morceaux)


def apercu(identifiant=None, brut=None):
    """L'HTML d'un document enregistré, ou d'un brouillon en cours de saisie."""
    d = _lire()
    if brut:
        existant = next((x for x in d["documents"] if x.get("id") == brut.get("id")), None) if brut.get("id") else None
        if existant and existant.get("numero"):
            return {"html": html_document(existant, d)}
        genre, propre = _valider_brouillon({**brut, "type": (existant or {}).get("type") or brut.get("type")}, d, existant)
        doc = {**(existant or {}), **propre, "type": genre, "numero": None}
        return {"html": html_document(doc, d)}
    return {"html": html_document(_trouver(d, identifiant), d)}


def dossier_documents():
    """Le dossier « Documents » réel de Windows (il peut être déplacé ou dans OneDrive)."""
    try:
        import ctypes
        tampon = ctypes.create_unicode_buffer(1024)
        if ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, tampon) == 0 and tampon.value:
            return tampon.value
    except (AttributeError, OSError):
        pass
    return os.path.join(os.path.expanduser("~"), "Documents")


def dossier_pdf(annee):
    return os.path.join(dossier_documents(), "Mes outils", "Factures", str(annee))


def chemin_edge():
    """msedge.exe aux emplacements habituels, ou None."""
    candidats = []
    for variable in ("ProgramFiles(x86)", "ProgramFiles", "LOCALAPPDATA"):
        racine = os.environ.get(variable)
        if racine:
            candidats.append(os.path.join(racine, "Microsoft", "Edge", "Application", "msedge.exe"))
    candidats += [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                  r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]
    for c in candidats:
        if os.path.isfile(c):
            return c
    return shutil.which("msedge")


def _nom_fichier(doc):
    nom = f"{doc['numero']} - {doc.get('client', {}).get('nom', '')}".strip(" -")
    nom = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", nom)
    nom = re.sub(r"\s+", " ", nom).strip(" .")[:90]
    return (nom or doc["numero"]) + ".pdf"


def html_vers_pdf(contenu_html, destination):
    """Convertit l'HTML en PDF avec Edge sans fenêtre (profil temporaire)."""
    edge = chemin_edge()
    if not edge:
        raise ValueError("Microsoft Edge est introuvable : impossible de créer le PDF.")
    travail = tempfile.mkdtemp(prefix="mes-outils-pdf-")
    try:
        source = os.path.join(travail, "document.html")
        with open(source, "w", encoding="utf-8") as f:
            f.write(contenu_html)
        sortie = os.path.join(travail, "document.pdf")
        commande = [edge, "--headless", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                    "--disable-extensions", f"--user-data-dir={os.path.join(travail, 'profil')}",
                    "--no-pdf-header-footer", "--print-to-pdf-no-header", f"--print-to-pdf={sortie}",
                    "file:///" + source.replace("\\", "/")]
        subprocess.run(commande, timeout=90, capture_output=True, creationflags=CREATION_SANS_FENETRE)
        if not os.path.isfile(sortie) or os.path.getsize(sortie) == 0:
            raise ValueError("Edge n'a pas pu créer le PDF.")
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        try:
            if os.path.exists(destination):
                os.remove(destination)
            shutil.move(sortie, destination)  # Documents peut être sur un autre disque
        except PermissionError:
            raise ValueError("Le PDF est ouvert dans un autre programme : fermez-le puis recommencez.") from None
        return destination
    finally:
        shutil.rmtree(travail, ignore_errors=True)


def generer_pdf(identifiant):
    """(Re)crée le PDF d'un document émis. Renvoie son chemin."""
    with _verrou:
        d = _lire()
        doc = _trouver(d, identifiant)
        if not doc.get("numero"):
            raise ValueError("Émettez d'abord le document (un brouillon n'a pas de numéro).")
        contenu = html_document(doc, d)
        destination = os.path.join(dossier_pdf(doc["date"][:4]), _nom_fichier(doc))
    html_vers_pdf(contenu, destination)
    with _verrou:
        d = _lire()
        doc = _trouver(d, identifiant)
        doc["pdf"] = destination
        _ecrire(d)
    return destination


def _ouvrir(chemin):
    os.startfile(chemin)  # noqa: S606 (chemin construit ici, jamais reçu de la page)


def ouvrir_pdf(identifiant):
    d = _lire()
    doc = _trouver(d, identifiant)
    chemin = doc.get("pdf")
    if not chemin or not os.path.isfile(chemin):
        chemin = generer_pdf(identifiant)
    _ouvrir(chemin)
    return {"ok": True, "chemin": chemin}


def ouvrir_dossier(identifiant=None):
    annee = str(aujourdhui().year)
    if identifiant:
        doc = _trouver(_lire(), identifiant)
        if doc.get("date"):
            annee = doc["date"][:4]
    dossier = dossier_pdf(annee)
    os.makedirs(dossier, exist_ok=True)
    _ouvrir(dossier)
    return {"ok": True, "chemin": dossier}


def preparer_mail(identifiant):
    """Le lien mailto (objet et texte prêts) ; le PDF est créé s'il manque.
    La pièce jointe s'ajoute à la main (mailto ne sait pas joindre de fichier)."""
    d = _lire()
    doc = _trouver(d, identifiant)
    if not doc.get("numero"):
        raise ValueError("Émettez d'abord le document.")
    chemin = doc.get("pdf")
    if not chemin or not os.path.isfile(chemin):
        chemin = generer_pdf(identifiant)
        d = _lire()
        doc = _trouver(d, identifiant)
    entreprise = _contexte(doc, d)
    devise = devise_de(entreprise)
    montant = formater_montant(Decimal(calculer(doc, entreprise)["total_ttc"]), devise)
    numero = doc["numero"]
    objet = {"devis": _texte("Devis {numero}", numero=numero), "facture": _texte("Facture {numero}", numero=numero),
             "avoir": _texte("Avoir {numero}", numero=numero)}[doc["type"]]
    if entreprise.get("nom"):
        objet += f" – {entreprise['nom']}"
    if doc["type"] == "facture":
        phrase = (_texte("Veuillez trouver ci-joint la facture {numero} d'un montant de {montant}, à régler au plus tard le {date}.",
                         numero=numero, montant=montant, date=_date_affichee(doc.get("echeance")))
                  if doc.get("echeance") and doc["echeance"] > doc.get("date", "") else
                  _texte("Veuillez trouver ci-joint la facture {numero} d'un montant de {montant}.", numero=numero, montant=montant))
    elif doc["type"] == "devis":
        phrase = _texte("Veuillez trouver ci-joint notre devis {numero} d'un montant de {montant}, valable jusqu'au {date}.",
                        numero=numero, montant=montant, date=_date_affichee(doc.get("validite")))
    else:
        phrase = _texte("Veuillez trouver ci-joint l'avoir {numero} d'un montant de {montant}.", numero=numero, montant=montant)
    texte = "\r\n".join([_texte("Bonjour,"), "", phrase, "", _texte("Cordialement,"), entreprise.get("nom", "")])
    email = (doc.get("client") or {}).get("email", "")
    lien = ("mailto:" + urllib.parse.quote(email, safe="@") + "?subject=" + urllib.parse.quote(objet, safe="")
            + "&body=" + urllib.parse.quote(texte, safe=""))
    return {"mailto": lien, "objet": objet, "texte": texte, "email": email, "pdf": chemin,
            "nom_pdf": os.path.basename(chemin)}


# ---------------------------------------------------------------------------
# Export CSV (Excel en français : « ; », UTF-8 avec BOM)
# ---------------------------------------------------------------------------
_FORMULE = re.compile(r"^[=+@\t\r]|^-[^\s\-]")


def _cellule(valeur):
    valeur = str(valeur or "")
    return "'" + valeur if _FORMULE.match(valeur) else valeur


def _nombre_csv(d):
    return format(d, "f").replace(".", ",")


def export_csv(ids=None):
    """Les documents (tous, ou ceux de la liste filtrée). Montants des avoirs en négatif."""
    d = _lire()
    jour = aujourdhui()
    voulus = set(ids) if ids is not None else None
    docs = [x for x in sorted(d["documents"], key=_cle_tri) if voulus is None or x["id"] in voulus]
    sortie = io.StringIO()
    ecrivain = csv.writer(sortie, delimiter=";", lineterminator="\r\n")
    ecrivain.writerow([_texte(x) for x in ("Type", "Numéro", "Date", "Échéance", "Client", "HT", "TVA", "TTC",
                                            "Payé", "Reste", "Devise", "Statut")])
    for doc in docs:
        r = _resume_doc(doc, d, jour)
        totaux = calculer(doc, _contexte(doc, d))
        signe = Decimal(-1) if doc["type"] == "avoir" else Decimal(1)
        libelle_etat = LIBELLES_ETATS["envoyee" if r["etat"] == "envoyee" else r["etat"]]
        ecrivain.writerow([_texte({"devis": "Devis", "facture": "Facture", "avoir": "Avoir"}[doc["type"]]),
                           _cellule(doc.get("numero") or ""), _date_affichee(doc.get("date")),
                           _date_affichee(doc.get("echeance") or doc.get("validite")),
                           _cellule((doc.get("client") or {}).get("nom")),
                           _nombre_csv(signe * Decimal(totaux["total_ht"])), _nombre_csv(signe * Decimal(totaux["total_tva"])),
                           _nombre_csv(signe * Decimal(totaux["total_ttc"])), _nombre_csv(Decimal(r["paye"])),
                           _nombre_csv(Decimal(r["reste"])), totaux["devise"]["code"], _texte(libelle_etat)])
    return {"nom": f"factures-{jour.isoformat()}.csv", "csv": "\ufeff" + sortie.getvalue()}


# ---------------------------------------------------------------------------
# Routes de la page
# ---------------------------------------------------------------------------
ROUTES = {
    "liste": lambda d: lister(),
    "resume": lambda d: {**resume(), "configuree": configuree()},
    "reglages": lambda d: reglages(),
    "reglages/enregistrer": lambda d: enregistrer_entreprise(d.get("entreprise")),
    "logo": lambda d: enregistrer_logo(d.get("nom"), d.get("contenu")),
    "logo/retirer": lambda d: retirer_logo(),
    "document": lambda d: document(d.get("id")),
    "enregistrer": lambda d: enregistrer(d.get("document")),
    "calculer": lambda d: calculer_brouillon(d.get("document")),
    "supprimer": lambda d: supprimer(d.get("id")),
    "dupliquer": lambda d: dupliquer(d.get("id")),
    "emettre": lambda d: emettre(d.get("id")),
    "statut": lambda d: changer_statut(d.get("id"), d.get("statut")),
    "transformer": lambda d: transformer(d.get("id")),
    "avoir": lambda d: creer_avoir(d.get("id")),
    "paiement/ajouter": lambda d: ajouter_paiement(d.get("id"), d.get("paiement")),
    "paiement/supprimer": lambda d: supprimer_paiement(d.get("id"), d.get("paiement_id")),
    "apercu": lambda d: apercu(d.get("id"), d.get("document")),
    "pdf": lambda d: {"pdf": generer_pdf(d.get("id"))},
    "pdf/ouvrir": lambda d: ouvrir_pdf(d.get("id")),
    "dossier/ouvrir": lambda d: ouvrir_dossier(d.get("id")),
    "mail": lambda d: preparer_mail(d.get("id")),
    "heures": lambda d: heures(d.get("projet") or "", d.get("debut") or "", d.get("fin") or ""),
    "heures/lignes": lambda d: lignes_heures(d.get("ids"), d.get("taux"), d.get("regrouper") or "projet"),
    "export": lambda d: export_csv(d.get("ids")),
    "alertes": lambda d: {"alertes": alertes_dues()},
    "marquer_alerte": lambda d: {"ok": marquer_alerte(d.get("id"))},
}
