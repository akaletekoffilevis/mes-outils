# -*- coding: utf-8 -*-
"""Application « Échéances » : abonnements, contrats, assurances, noms de
domaine, licences, loyers… tout ce qui se renouvelle ou expire.

Fiche (donnees\\echeances.json, clé « elements ») :
  {id, nom, categorie, fournisseur, contact_id, montant_centimes, devise,
   frequence, mois, prochaine, jour_ancre, tacite, preavis_jours,
   rappel_jours, statut, paiement, lien, note, historique}

- Montants en centimes entiers (jamais de nombre à virgule) ; les coûts
  ramenés au mois sont calculés en fractions exactes puis arrondis une seule
  fois, au centime, à la fin (arrondi « au plus proche », 0,5 vers le haut).
- Fréquences : mensuelle (1 mois), trimestrielle (3), annuelle (12),
  « mois » (tous les N mois) ou « unique » (une seule date).
- « Payé / renouvelé » avance la prochaine échéance d'une période. Le jour
  d'origine est gardé (jour_ancre) : 31 janvier → 28 ou 29 février → 31 mars ;
  29 février → 28 février l'année suivante → 29 février l'année bissextile.
  Une échéance unique payée passe au statut « terminé ».
- Statuts : actif, a_resilier, resilie (et termine pour une date unique réglée).
- Reconduction tacite : la date limite de résiliation est la prochaine
  échéance moins le préavis (en jours).

Pour la bulle : alertes_dues() et marquer_alerte(id). Deux rappels par fiche
active : « rappel_jours » avant l'échéance et, si la reconduction est tacite,
« rappel_jours » avant la date limite de résiliation. L'identifiant d'une
alerte contient la date visée : une fois l'échéance avancée, le rappel de la
période suivante est une nouvelle alerte.
"""
import calendar
import csv
import datetime
import io
import re
import threading
import uuid
from decimal import Decimal, InvalidOperation
from fractions import Fraction

import config

NOM = "echeances"
CATEGORIES = ("logiciel", "telephonie", "assurance", "contrat", "domaine", "licence",
              "loyer", "energie", "banque", "autre")
FREQUENCES = {"mensuelle": 1, "trimestrielle": 3, "annuelle": 12}
STATUTS = ("actif", "a_resilier", "resilie", "termine")
STATUTS_ACTIFS = ("actif", "a_resilier")
MAX_NOM = 80
MAX_TEXTE = 120
MAX_NOTE = 1000
MAX_LIEN = 400
MAX_MONTANT = 10 ** 11            # centimes : un milliard
MAX_HISTORIQUE = 24
MAX_VUES = 400
RAPPEL_DEFAUT = 7

_verrou = threading.RLock()

# Textes de la bulle et de l'export (la bulle n'a pas le dictionnaire de la page).
_ANGLAIS = {
    "Échéance : {nom}": "Due date: {nom}",
    "Échéance dépassée : {nom}": "Overdue: {nom}",
    "{montant} le {date} (aujourd'hui).": "{montant} on {date} (today).",
    "{montant} le {date} (demain).": "{montant} on {date} (tomorrow).",
    "{montant} le {date} (dans {n} jours).": "{montant} on {date} (in {n} days).",
    "{montant} le {date} (en retard de {n} jours).": "{montant} on {date} ({n} days overdue).",
    "Résiliation : {nom}": "Cancellation: {nom}",
    "Reconduction tacite : pour résilier, prévenir au plus tard le {date} ({quand}).":
        "Automatic renewal: to cancel, give notice by {date} ({quand}).",
    "aujourd'hui": "today", "demain": "tomorrow", "dans {n} jours": "in {n} days",
    "Nom": "Name", "Catégorie": "Category", "Fournisseur": "Provider", "Montant": "Amount",
    "Devise": "Currency", "Fréquence": "Frequency", "Prochaine échéance": "Next due date",
    "Reconduction tacite": "Automatic renewal", "Préavis (jours)": "Notice (days)",
    "Date limite de résiliation": "Cancellation deadline", "Rappel (jours avant)": "Reminder (days before)",
    "Statut": "Status", "Moyen de paiement": "Payment method", "Espace client": "Customer portal",
    "Note": "Note", "Coût mensuel": "Monthly cost", "Oui": "Yes", "Non": "No",
    "Mensuelle": "Monthly", "Trimestrielle": "Quarterly", "Annuelle": "Yearly",
    "Tous les {n} mois": "Every {n} months", "Date unique": "One-off",
    "Actif": "Active", "À résilier": "To cancel", "Résilié": "Cancelled", "Terminé": "Completed",
    "Logiciel": "Software", "Téléphone et Internet": "Phone and Internet", "Assurance": "Insurance",
    "Contrat": "Contract", "Nom de domaine": "Domain name", "Licence": "Licence", "Loyer": "Rent",
    "Énergie": "Energy", "Banque": "Banking", "Autre": "Other",
}
LIBELLES_CATEGORIES = {"logiciel": "Logiciel", "telephonie": "Téléphone et Internet", "assurance": "Assurance",
                       "contrat": "Contrat", "domaine": "Nom de domaine", "licence": "Licence", "loyer": "Loyer",
                       "energie": "Énergie", "banque": "Banque", "autre": "Autre"}
LIBELLES_STATUTS = {"actif": "Actif", "a_resilier": "À résilier", "resilie": "Résilié", "termine": "Terminé"}


def _texte(fr, **valeurs):
    texte = _ANGLAIS.get(fr, fr) if config.langue() == "en" else fr
    return texte.format(**valeurs) if valeurs else texte


def aujourdhui():
    """La date du jour (remplacée par une horloge simulée dans les tests)."""
    return datetime.date.today()


# ---------------------------------------------------------------------------
# Dates
# ---------------------------------------------------------------------------
def ajouter_mois(jour, n, ancre=None):
    """La date « jour » + n mois, au jour « ancre » (par défaut celui de
    « jour »), ramené au dernier jour du mois s'il n'existe pas."""
    ancre = ancre or jour.day
    total = jour.year * 12 + (jour.month - 1) + n
    annee, mois = divmod(total, 12)
    mois += 1
    return datetime.date(annee, mois, min(ancre, calendar.monthrange(annee, mois)[1]))


def _date(texte, nom="Date"):
    try:
        return datetime.date.fromisoformat(str(texte or "")[:10])
    except ValueError:
        raise ValueError(f"{nom} invalide.") from None


def periode_mois(e):
    """La durée d'une période en mois, ou None pour une date unique."""
    if e["frequence"] == "unique":
        return None
    return FREQUENCES.get(e["frequence"]) or int(e.get("mois") or 1)


def limite_resiliation(e):
    """La date limite pour résilier (reconduction tacite), ou None."""
    if not e.get("tacite") or e["frequence"] == "unique":
        return None
    return _date(e["prochaine"]) - datetime.timedelta(days=int(e.get("preavis_jours") or 0))


# ---------------------------------------------------------------------------
# Montants
# ---------------------------------------------------------------------------
def centimes(valeur):
    """« 1 234,56 », « 12.5 », 12 → centimes entiers (exacts). ValueError sinon."""
    if isinstance(valeur, bool):
        raise ValueError("Montant invalide.")
    if isinstance(valeur, int):
        texte = str(valeur)
    else:
        texte = re.sub(r"[\s  ']", "", str(valeur if valeur is not None else ""))
        if "," in texte and "." in texte:
            # « 1,234.56 » ou « 1.234,56 » : le dernier signe sépare les décimales.
            mille = "," if texte.rfind(",") < texte.rfind(".") else "."
            texte = texte.replace(mille, "")
        texte = texte.replace(",", ".")
    if not texte:
        return 0
    try:
        d = Decimal(texte)
    except InvalidOperation:
        raise ValueError("Montant invalide.") from None
    if not d.is_finite() or d < 0:
        raise ValueError("Montant invalide.")
    c = d * 100
    if c != c.to_integral_value():
        raise ValueError("Montant invalide : deux décimales au plus.")
    c = int(c)
    if c > MAX_MONTANT:
        raise ValueError("Montant trop élevé.")
    return c


def arrondi(fraction):
    """Une fraction de centimes arrondie au centime (0,5 vers le haut)."""
    entier, reste = divmod(fraction.numerator, fraction.denominator)
    return entier + (1 if 2 * reste >= fraction.denominator else 0)


def _cout_mensuel_exact(e):
    """Le coût ramené au mois, en fraction exacte de centimes (0 si unique ou inactif)."""
    n = periode_mois(e)
    if n is None or e["statut"] not in STATUTS_ACTIFS:
        return Fraction(0)
    return Fraction(int(e.get("montant_centimes") or 0), n)


def montant_texte(c, devise):
    """12345, "EUR" → « 123,45 EUR » (« 123.45 EUR » en anglais)."""
    entier, dec = divmod(int(c), 100)
    if config.langue() == "en":
        return f"{entier:,}.{dec:02d} {devise}"
    return f"{entier:,}".replace(",", " ") + f",{dec:02d} {devise}"


def _date_texte(jour):
    return jour.strftime("%d/%m/%Y")


# ---------------------------------------------------------------------------
# Fichier
# ---------------------------------------------------------------------------
def _lire():
    d = config.lire_donnees(NOM, {})
    if not isinstance(d, dict):
        d = {}
    d.setdefault("elements", [])
    d.setdefault("vues", [])
    return d


def _ecrire(d):
    config.ecrire_donnees(NOM, d)


def _trouver(d, identifiant):
    e = next((x for x in d["elements"] if x.get("id") == identifiant), None)
    if e is None:
        raise ValueError("Échéance introuvable.")
    return e


# ---------------------------------------------------------------------------
# Validation d'une fiche
# ---------------------------------------------------------------------------
_CARTE = re.compile(r"\d{12,}")


def _court(valeur, maxi=MAX_TEXTE):
    return " ".join(str(valeur or "").split())[:maxi]


def _entier(valeur, nom, mini, maxi, defaut):
    if valeur in (None, ""):
        return defaut
    try:
        n = int(valeur)
    except (TypeError, ValueError):
        raise ValueError(f"{nom} invalide.") from None
    if not mini <= n <= maxi:
        raise ValueError(f"{nom} : de {mini} à {maxi}.")
    return n


def valider(f, ancienne=None):
    """Une fiche propre à partir de ce qu'envoie la page. ValueError si invalide."""
    f = f or {}
    nom = _court(f.get("nom"), MAX_NOM)
    if not nom:
        raise ValueError("Indiquez un nom.")
    categorie = f.get("categorie") or "autre"
    if categorie not in CATEGORIES:
        raise ValueError("Catégorie inconnue.")
    frequence = f.get("frequence") or "mensuelle"
    if frequence not in (*FREQUENCES, "mois", "unique"):
        raise ValueError("Fréquence inconnue.")
    mois = _entier(f.get("mois"), "Nombre de mois", 1, 120, 1) if frequence == "mois" else None
    if not f.get("prochaine"):
        raise ValueError("Indiquez la prochaine échéance.")
    prochaine = _date(f.get("prochaine"), "Date d'échéance")
    devise = str(f.get("devise") or "EUR").strip().upper()
    if not re.fullmatch(r"[A-Z]{3}", devise):
        raise ValueError("Devise invalide (code à trois lettres, ex. EUR).")
    if f.get("montant") is None and f.get("montant_centimes") is not None:
        montant_centimes = _entier(f.get("montant_centimes"), "Montant", 0, MAX_MONTANT, 0)
    else:
        montant_centimes = centimes(f.get("montant"))
    statut = f.get("statut") or "actif"
    if statut not in STATUTS:
        raise ValueError("Statut inconnu.")
    paiement = _court(f.get("paiement"))
    if _CARTE.search(re.sub(r"[\s.\-]", "", paiement)):
        raise ValueError("N'indiquez jamais de numéro de carte ou de compte : par exemple « Carte pro (fin 1234) ».")
    lien = str(f.get("lien") or "").strip()[:MAX_LIEN]
    if lien and not re.match(r"^https?://[^\s/]+", lien, re.I):
        raise ValueError("Lien invalide : il doit commencer par https://")
    tacite = bool(f.get("tacite")) and frequence != "unique"
    propre = {
        "nom": nom, "categorie": categorie,
        "fournisseur": _court(f.get("fournisseur")),
        "contact_id": str(f.get("contact_id") or "")[:64] or None,
        "montant_centimes": montant_centimes, "devise": devise,
        "frequence": frequence, "mois": mois,
        "prochaine": prochaine.isoformat(),
        "tacite": tacite,
        "preavis_jours": _entier(f.get("preavis_jours"), "Préavis", 0, 730, 0) if tacite else 0,
        "rappel_jours": _entier(f.get("rappel_jours"), "Rappel", 0, 365, RAPPEL_DEFAUT),
        "statut": statut, "paiement": paiement, "lien": lien,
        "note": str(f.get("note") or "").strip()[:MAX_NOTE],
    }
    if not propre["fournisseur"]:
        propre["contact_id"] = None
    # Le jour d'origine ne change que si la date est modifiée à la main.
    if ancienne and ancienne.get("prochaine") == propre["prochaine"] and ancienne.get("jour_ancre"):
        propre["jour_ancre"] = ancienne["jour_ancre"]
    else:
        propre["jour_ancre"] = prochaine.day
    return propre


# ---------------------------------------------------------------------------
# Fiches
# ---------------------------------------------------------------------------
def enregistrer(fiche):
    """Ajoute (sans id) ou modifie (avec id) une fiche. Renvoie la fiche."""
    fiche = fiche or {}
    with _verrou:
        d = _lire()
        if fiche.get("id"):
            e = _trouver(d, fiche["id"])
            e.update(valider(fiche, e))
        else:
            e = {"id": uuid.uuid4().hex[:12], **valider(fiche), "historique": []}
            d["elements"].append(e)
        _ecrire(d)
        return dict(e)


def supprimer(identifiant):
    with _verrou:
        d = _lire()
        avant = len(d["elements"])
        d["elements"] = [e for e in d["elements"] if e.get("id") != identifiant]
        if len(d["elements"]) == avant:
            raise ValueError("Échéance introuvable.")
        d["vues"] = [v for v in d["vues"] if not v.startswith(identifiant + ":")]
        _ecrire(d)
        return True


def changer_statut(identifiant, statut):
    if statut not in STATUTS:
        raise ValueError("Statut inconnu.")
    with _verrou:
        d = _lire()
        e = _trouver(d, identifiant)
        e["statut"] = statut
        _ecrire(d)
        return dict(e)


def payer(identifiant):
    """« Payé / renouvelé » : la prochaine échéance avance d'une période
    (une date unique passe au statut « terminé »)."""
    with _verrou:
        d = _lire()
        e = _trouver(d, identifiant)
        if e["statut"] not in STATUTS_ACTIFS:
            raise ValueError("Cette échéance n'est plus active.")
        jour = _date(e["prochaine"])
        e.setdefault("historique", []).append({
            "echeance": e["prochaine"], "le": aujourdhui().isoformat(),
            "montant_centimes": e["montant_centimes"], "statut_avant": e["statut"]})
        e["historique"] = e["historique"][-MAX_HISTORIQUE:]
        n = periode_mois(e)
        if n is None:
            e["statut"] = "termine"
        else:
            e["prochaine"] = ajouter_mois(jour, n, e.get("jour_ancre") or jour.day).isoformat()
        _ecrire(d)
        return dict(e)


def annuler_paiement(identifiant):
    """Annule le dernier « payé / renouvelé » (retour à l'échéance d'avant)."""
    with _verrou:
        d = _lire()
        e = _trouver(d, identifiant)
        if not e.get("historique"):
            raise ValueError("Aucun paiement à annuler.")
        dernier = e["historique"].pop()
        e["prochaine"] = dernier["echeance"]
        e["statut"] = dernier.get("statut_avant") or "actif"
        _ecrire(d)
        return dict(e)


# ---------------------------------------------------------------------------
# Lecture enrichie pour la page
# ---------------------------------------------------------------------------
def _groupe(e, jour, ref):
    if e["statut"] not in STATUTS_ACTIFS:
        return "resilies"
    fin_semaine = ref + datetime.timedelta(days=6 - ref.weekday())
    if jour <= fin_semaine:
        return "semaine"
    if (jour.year, jour.month) == (ref.year, ref.month):
        return "mois"
    return "plus_tard"


def _enrichir(e, ref):
    jour = _date(e["prochaine"])
    limite = limite_resiliation(e)
    r = dict(e)
    r["jours"] = (jour - ref).days
    r["groupe"] = _groupe(e, jour, ref)
    r["limite_resiliation"] = limite.isoformat() if limite else None
    r["jours_limite"] = (limite - ref).days if limite else None
    r["cout_mensuel_centimes"] = arrondi(_cout_mensuel_exact(e))
    r["montant"] = f"{e['montant_centimes'] // 100}.{e['montant_centimes'] % 100:02d}"
    return r


def couts(elements):
    """Coûts ramenés au mois et à l'année, par devise puis par catégorie :
    {devise: {mensuel, annuel, categories: [{categorie, mensuel, annuel}]}}
    (en centimes). Sommes exactes, arrondi une seule fois à la fin."""
    par_devise = {}
    for e in elements:
        exact = _cout_mensuel_exact(e)
        if not exact:
            continue
        dev = par_devise.setdefault(e["devise"], {"total": Fraction(0), "categories": {}})
        dev["total"] += exact
        dev["categories"][e["categorie"]] = dev["categories"].get(e["categorie"], Fraction(0)) + exact
    r = {}
    for devise, dev in sorted(par_devise.items()):
        cats = [{"categorie": c, "mensuel": arrondi(v), "annuel": arrondi(v * 12)}
                for c, v in sorted(dev["categories"].items(), key=lambda x: (-x[1], x[0]))]
        r[devise] = {"mensuel": arrondi(dev["total"]), "annuel": arrondi(dev["total"] * 12), "categories": cats}
    return r


def liste():
    ref = aujourdhui()
    with _verrou:
        elements = _lire()["elements"]
    riches = sorted((_enrichir(e, ref) for e in elements), key=lambda x: (x["prochaine"], x["nom"].lower()))
    return {"elements": riches, "couts": couts(elements), "aujourdhui": ref.isoformat(),
            "categories": list(CATEGORIES)}


def accueil(jours=14, limite=5):
    """Pour la carte de l'Accueil : les échéances actives des 14 prochains
    jours (en retard comprises, au plus 5) et le coût mensuel total."""
    r = liste()
    proches = [e for e in r["elements"] if e["statut"] in STATUTS_ACTIFS and e["jours"] <= jours]
    return {"prochaines": proches[:limite], "nombre": len(proches),
            "couts": {d: {"mensuel": c["mensuel"]} for d, c in r["couts"].items()}}


# ---------------------------------------------------------------------------
# Pour la bulle
# ---------------------------------------------------------------------------
def _quand(n):
    if n == 0:
        return _texte("aujourd'hui")
    if n == 1:
        return _texte("demain")
    return _texte("dans {n} jours", n=n)


def _alertes_calculees(elements, ref):
    """Toutes les alertes à montrer aujourd'hui (vues ou non), par date."""
    alertes = []
    for e in elements:
        if e.get("statut") not in STATUTS_ACTIFS:
            continue
        try:
            jour = _date(e["prochaine"])
        except (KeyError, ValueError):
            continue
        rappel = int(e.get("rappel_jours") if e.get("rappel_jours") is not None else RAPPEL_DEFAUT)
        n = (jour - ref).days
        montant = montant_texte(e.get("montant_centimes") or 0, e.get("devise") or "EUR")
        if n <= rappel:
            if n < 0:
                titre = _texte("Échéance dépassée : {nom}", nom=e["nom"])
                detail = _texte("{montant} le {date} (en retard de {n} jours).", montant=montant, date=_date_texte(jour), n=-n)
            else:
                titre = _texte("Échéance : {nom}", nom=e["nom"])
                cle = {0: "{montant} le {date} (aujourd'hui).", 1: "{montant} le {date} (demain)."}.get(
                    n, "{montant} le {date} (dans {n} jours).")
                detail = _texte(cle, montant=montant, date=_date_texte(jour), n=n)
            alertes.append((jour, {"id": f"{e['id']}:echeance:{jour.isoformat()}", "titre": titre, "detail": detail}))
        limite = limite_resiliation(e)
        if limite and 0 <= (limite - ref).days <= rappel:
            alertes.append((limite, {
                "id": f"{e['id']}:preavis:{limite.isoformat()}",
                "titre": _texte("Résiliation : {nom}", nom=e["nom"]),
                "detail": _texte("Reconduction tacite : pour résilier, prévenir au plus tard le {date} ({quand}).",
                                 date=_date_texte(limite), quand=_quand((limite - ref).days))}))
    alertes.sort(key=lambda x: x[0])
    return [a for _, a in alertes]


def alertes_dues():
    """Les rappels pas encore vus : [{id, titre, detail}]."""
    with _verrou:
        d = _lire()
        vues = set(d["vues"])
        return [a for a in _alertes_calculees(d["elements"], aujourdhui()) if a["id"] not in vues]


def marquer_alerte(identifiant):
    """Rappel vu. Renvoie True s'il était dû."""
    with _verrou:
        d = _lire()
        if identifiant not in {a["id"] for a in _alertes_calculees(d["elements"], aujourdhui())}:
            return False
        if identifiant not in d["vues"]:
            ids = {e.get("id") for e in d["elements"]}
            # Les rappels d'échéances supprimées ne servent plus.
            d["vues"] = [v for v in d["vues"] if v.split(":", 1)[0] in ids][-(MAX_VUES - 1):] + [identifiant]
            _ecrire(d)
        return True


# ---------------------------------------------------------------------------
# Export CSV (Excel en français : séparateur « ; », UTF-8 avec BOM)
# ---------------------------------------------------------------------------
_FORMULE = re.compile(r"^[=+@\t\r]|^-[^\s\-]")


def _cellule(valeur):
    """Un texte qu'Excel ne prendra pas pour une formule."""
    valeur = str(valeur or "")
    return "'" + valeur if _FORMULE.match(valeur) else valeur


def _nombre(c):
    texte = f"{int(c) // 100}.{int(c) % 100:02d}"
    return texte if config.langue() == "en" else texte.replace(".", ",")


def _libelle_frequence(e):
    if e["frequence"] == "mois":
        return _texte("Tous les {n} mois", n=e.get("mois") or 1)
    return _texte({"mensuelle": "Mensuelle", "trimestrielle": "Trimestrielle", "annuelle": "Annuelle",
                   "unique": "Date unique"}[e["frequence"]])


def export_csv():
    """{nom, csv} : toutes les fiches, par date. Le texte commence par le BOM."""
    r = liste()
    sortie = io.StringIO()
    ecrivain = csv.writer(sortie, delimiter=";", lineterminator="\r\n")
    ecrivain.writerow([_texte(x) for x in (
        "Nom", "Catégorie", "Fournisseur", "Montant", "Devise", "Fréquence", "Prochaine échéance",
        "Reconduction tacite", "Préavis (jours)", "Date limite de résiliation", "Rappel (jours avant)",
        "Statut", "Moyen de paiement", "Espace client", "Note", "Coût mensuel")])
    for e in r["elements"]:
        ecrivain.writerow([
            _cellule(e["nom"]), _texte(LIBELLES_CATEGORIES[e["categorie"]]), _cellule(e.get("fournisseur")),
            _nombre(e["montant_centimes"]), e["devise"], _libelle_frequence(e), e["prochaine"],
            _texte("Oui" if e.get("tacite") else "Non"), e.get("preavis_jours") or 0,
            e.get("limite_resiliation") or "", e.get("rappel_jours"),
            _texte(LIBELLES_STATUTS[e["statut"]]), _cellule(e.get("paiement")), _cellule(e.get("lien")),
            _cellule(e.get("note")), _nombre(e["cout_mensuel_centimes"])])
    return {"nom": f"echeances-{aujourdhui().isoformat()}.csv", "csv": "﻿" + sortie.getvalue()}


# ---------------------------------------------------------------------------
# Routes de la page
# ---------------------------------------------------------------------------
ROUTES = {
    "liste": lambda d: liste(),
    "accueil": lambda d: accueil(),
    "enregistrer": lambda d: enregistrer(d.get("element")),
    "supprimer": lambda d: {"ok": supprimer(d.get("id"))},
    "payer": lambda d: payer(d.get("id")),
    "annuler_paiement": lambda d: annuler_paiement(d.get("id")),
    "statut": lambda d: changer_statut(d.get("id"), d.get("statut")),
    "export": lambda d: export_csv(),
    "alertes": lambda d: {"alertes": alertes_dues()},
    "marquer_alerte": lambda d: {"ok": marquer_alerte(d.get("id"))},
}
