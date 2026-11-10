# -*- coding: utf-8 -*-
"""Application « Dépenses et notes de frais ».

Reprise, pour un seul utilisateur et en local, de l'application web
« Mes dépenses » (Next.js + Supabase) :

- dépenses par mois, catégories (dont « Épargne », unique et non supprimable) ;
- charges fixes : ajoutées automatiquement chaque mois, au jour choisi (le 31
  devient le 30 ou le 28), dès le mois de leur création ; les mois manquants
  sont rattrapés (24 mois au plus) ; une dépense générée puis supprimée à la
  main n'est jamais recréée ;
- budget mensuel, reconduit tant qu'il n'est pas modifié ;
- épargne : tout ce qui est classé dans « Épargne » est mis de côté, dans le
  budget. Si une nouvelle dépense fait dépasser le budget, rien n'est
  enregistré tant que la personne n'a pas choisi : reprendre le dépassement
  sur l'épargne (montant modifiable, jamais plus que l'épargne disponible) ou
  ajouter sans y toucher.
      dépensé effectif du mois = dépenses du mois − reprises du mois
- statistiques, devise (EUR, USD, MGA : l'affichage seulement).

En plus, pour les professionnels : notes de frais (dépense professionnelle,
client refacturable, statut, justificatif copié dans
donnees\\depenses\\justificatifs) et export CSV pour la comptabilité.

Montants : Decimal, enregistrés en texte « 12.50 », jamais de float.
Dates : ISO « YYYY-MM-DD », mois « YYYY-MM ».

Pour la bulle : alertes_dues() (budget dépassé), marquer_alerte(id).
"""
import calendar
import csv
import datetime
import io
import os
import re
import shutil
import subprocess
import threading
import uuid
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

import config

NOM = "depenses"
CENT = Decimal("0.01")
ZERO = Decimal("0")
MAX_MONTANT = Decimal("999999999999")
# Devises proposées et leur nombre de décimales (MGA : sans centimes).
DEVISES = {"EUR": 2, "USD": 2, "MGA": 0}
SYMBOLES = {"EUR": "€", "USD": "$", "MGA": "Ar"}
PAIEMENTS = ("carte", "especes", "virement", "paypal", "mobile_money", "autre")
STATUTS = ("a_rembourser", "remboursee", "refacturee")
COULEURS = ("violet", "ambre", "bleu", "corail", "menthe", "rouge", "gris")
ICONES_CATEGORIES = (
    "shopping-cart", "car", "house", "heart", "gamepad-2", "tag", "repeat", "graduation-cap", "receipt",
    "piggy-bank", "plane", "train-front", "hotel", "coffee", "briefcase", "laptop", "smartphone",
    "package", "wrench", "banknote", "credit-card", "users", "book-open", "music", "camera", "zap", "landmark",
)
# Catégories créées au premier lancement (celles de l'application d'origine).
CATEGORIES_DEFAUT = (
    ("alimentation", "Alimentation", "shopping-cart", "ambre"),
    ("transport", "Transport", "car", "bleu"),
    ("logement", "Logement", "house", "violet"),
    ("sante", "Santé", "heart", "rouge"),
    ("loisirs", "Loisirs", "gamepad-2", "corail"),
    ("shopping", "Shopping", "tag", "menthe"),
    ("abonnements", "Abonnements", "repeat", "corail"),
    ("education", "Éducation", "graduation-cap", "menthe"),
    ("factures", "Factures", "receipt", "ambre"),
    ("epargne", "Épargne", "piggy-bank", "menthe"),
    ("autres", "Autres", "tag", "gris"),
)
NOMS_EPARGNE = ("épargne", "epargne", "épargnes", "epargnes")
RATTRAPAGE_MOIS = 24
EXTENSIONS_JUSTIFICATIF = (".pdf", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".heic", ".bmp", ".tif", ".tiff")
TAILLE_MAX_JUSTIFICATIF = 25 * 1024 * 1024
CREATE_NO_WINDOW = 0x08000000

_verrou = threading.RLock()

# Textes de l'export et de la bulle (la page a son propre dictionnaire).
_ANGLAIS = {
    "Date": "Date", "Description": "Description", "Catégorie": "Category", "Montant": "Amount",
    "Devise": "Currency", "Paiement": "Payment", "Professionnelle": "Business", "Client": "Client",
    "Statut": "Status", "Justificatif": "Receipt", "Note": "Note", "Total": "Total",
    "Oui": "Yes", "Non": "No",
    "À rembourser": "To be reimbursed", "Remboursée": "Reimbursed", "Refacturée": "Re-invoiced",
    "Carte bancaire": "Card", "Espèces": "Cash", "Virement": "Bank transfer", "PayPal": "PayPal",
    "Mobile Money": "Mobile Money", "Autre": "Other",
    "Budget dépassé": "Budget exceeded",
    "Dépensé {depense} sur {budget} ce mois-ci.": "Spent {depense} of {budget} this month.",
}
LIBELLES_STATUTS = {"a_rembourser": "À rembourser", "remboursee": "Remboursée", "refacturee": "Refacturée"}
LIBELLES_PAIEMENTS = {"carte": "Carte bancaire", "especes": "Espèces", "virement": "Virement", "paypal": "PayPal",
                      "mobile_money": "Mobile Money", "autre": "Autre"}


def _texte(fr, **valeurs):
    texte = _ANGLAIS.get(fr, fr) if config.langue() == "en" else fr
    return texte.format(**valeurs) if valeurs else texte


def aujourdhui():
    """La date du jour (remplacée par une date simulée dans les tests)."""
    return datetime.date.today()


def _maintenant():
    return datetime.datetime.now().replace(microsecond=0).isoformat()


def _nouvel_id():
    return uuid.uuid4().hex[:12]


# ---------------------------------------------------------------------------
# Montants, dates
# ---------------------------------------------------------------------------
def _dec(valeur):
    """Un montant enregistré (texte) en Decimal."""
    try:
        return Decimal(str(valeur or "0"))
    except InvalidOperation:
        return ZERO


def _s(montant):
    """Un Decimal en texte « 12.50 » (pour le fichier et la page)."""
    return str(Decimal(montant).quantize(CENT, rounding=ROUND_HALF_UP))


def devise():
    valeur = config.section(NOM).get("devise") or "EUR"
    return valeur if valeur in DEVISES else "EUR"


def _montant(valeur, zero_permis=False, nom="Montant"):
    """« 12,50 », « 1 250.5 », 12.5 → Decimal arrondi à la devise (MGA : à
    l'unité). Lève ValueError si le texte n'est pas un montant."""
    if isinstance(valeur, bool) or valeur is None:
        raise ValueError(f"{nom} : indiquez un montant valide.")
    texte = re.sub(r"[\s  ]", "", str(valeur)).replace(",", ".")
    if not re.fullmatch(r"\d*\.?\d*", texte) or texte in ("", "."):
        raise ValueError(f"{nom} : indiquez un montant valide.")
    montant = Decimal(texte).quantize(Decimal(1).scaleb(-DEVISES[devise()]), rounding=ROUND_HALF_UP)
    if montant > MAX_MONTANT:
        raise ValueError(f"{nom} : ce montant est trop élevé.")
    if montant < 0 or (montant == 0 and not zero_permis):
        raise ValueError(f"{nom} : le montant doit être supérieur à 0.")
    return montant.quantize(CENT)


def _date(valeur):
    try:
        jour = datetime.date.fromisoformat(str(valeur or "")[:10])
    except ValueError:
        raise ValueError("Date invalide.") from None
    if not datetime.date(2000, 1, 1) <= jour <= datetime.date(2100, 12, 31):
        raise ValueError("Date invalide.")
    return jour.isoformat()


def _mois(valeur=None):
    """« YYYY-MM » (mois courant par défaut)."""
    if not valeur:
        return aujourdhui().isoformat()[:7]
    texte = str(valeur)[:7]
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", texte):
        raise ValueError("Mois invalide.")
    return texte


def ajouter_mois(mois, n):
    annee, m = int(mois[:4]), int(mois[5:7]) - 1 + n
    return f"{annee + m // 12:04d}-{m % 12 + 1:02d}"


def jours_du_mois(mois):
    return calendar.monthrange(int(mois[:4]), int(mois[5:7]))[1]


def _fin_mois(mois):
    return f"{mois}-{jours_du_mois(mois):02d}"


def _lundi(jour_iso):
    jour = datetime.date.fromisoformat(jour_iso)
    return (jour - datetime.timedelta(days=jour.weekday())).isoformat()


def _texte_court(valeur, maxi, nom):
    texte = " ".join(str(valeur or "").split())
    if len(texte) > maxi:
        raise ValueError(f"{nom} : {maxi} caractères maximum.")
    return texte


# ---------------------------------------------------------------------------
# Fichier
# ---------------------------------------------------------------------------
def _categorie_defaut(cle, nom, icone, couleur, ordre):
    return {"id": cle, "nom": nom, "icone": icone, "couleur": couleur, "ordre": ordre, "epargne": cle == "epargne"}


def _lire():
    d = config.lire_donnees(NOM, {})
    if not isinstance(d, dict):
        d = {}
    for cle in ("categories", "depenses", "charges", "budgets", "reprises", "alertes_vues"):
        if not isinstance(d.get(cle), list):
            d[cle] = []
    if not d["categories"]:
        d["categories"] = [_categorie_defaut(*c, ordre=i + 1) for i, c in enumerate(CATEGORIES_DEFAUT)]
    # Une seule catégorie « Épargne », toujours présente (reprise d'une
    # catégorie déjà nommée ainsi s'il y en a une).
    epargnes = [c for c in d["categories"] if c.get("epargne")]
    for c in epargnes[1:]:
        c["epargne"] = False
    if not epargnes:
        existante = next((c for c in d["categories"] if c["nom"].strip().lower() in NOMS_EPARGNE), None)
        if existante:
            existante["epargne"] = True
        else:
            d["categories"].append(_categorie_defaut("epargne", "Épargne", "piggy-bank", "menthe",
                                                     max([c.get("ordre", 0) for c in d["categories"]] + [0]) + 1))
    return d


def _ecrire(d):
    config.ecrire_donnees(NOM, d)


def _charger():
    """Les données, charges fixes du mois appliquées (écrites si besoin)."""
    d = _lire()
    if appliquer_charges(d, aujourdhui()):
        _ecrire(d)
    return d


# ---------------------------------------------------------------------------
# Charges fixes
# ---------------------------------------------------------------------------
def appliquer_charges(d, jour):
    """Crée les dépenses des charges fixes jusqu'au mois de « jour » inclus.
    Seuls les mois jamais générés sont traités (rattrapage : 24 mois).
    Renvoie le nombre de dépenses créées."""
    courant = jour.isoformat()[:7]
    plus_ancien = ajouter_mois(courant, -RATTRAPAGE_MOIS)
    n = 0
    for c in d["charges"]:
        generes = c.setdefault("generes", [])
        mois = max(c["debut"], plus_ancien)
        while mois <= courant:
            if mois not in generes:
                generes.append(mois)
                j = min(int(c["jour"]), jours_du_mois(mois))
                d["depenses"].append(_depense_de_charge(c, f"{mois}-{j:02d}"))
                n += 1
            mois = ajouter_mois(mois, 1)
    return n


def _depense_de_charge(c, date):
    pro = bool(c.get("pro"))
    return {"id": _nouvel_id(), "montant": c["montant"], "categorie": c["categorie"], "description": c["description"],
            "date": date, "paiement": c["paiement"], "note": "", "charge": c["id"], "pro": pro,
            "client_id": c.get("client_id") or "", "client_nom": c.get("client_nom") or "",
            "statut": "a_rembourser" if pro else None, "justificatif": None, "cree": _maintenant()}


def _valider_charge(donnees, d):
    description = _texte_court(donnees.get("description"), 120, "Nom")
    if not description:
        raise ValueError("Donnez un nom à cette charge (ex. Loyer).")
    try:
        jour = int(donnees.get("jour"))
    except (TypeError, ValueError):
        raise ValueError("Jour invalide.") from None
    if not 1 <= jour <= 31:
        raise ValueError("Jour invalide.")
    pro = bool(donnees.get("pro"))
    return {"montant": _s(_montant(donnees.get("montant"))), "categorie": _categorie(d, donnees.get("categorie"))["id"],
            "description": description, "jour": jour, "paiement": _paiement(donnees.get("paiement") or "virement"),
            "pro": pro, "client_id": _texte_court(donnees.get("client_id"), 64, "Client") if pro else "",
            "client_nom": _texte_court(donnees.get("client_nom"), 120, "Client") if pro else ""}


def ajouter_charge(donnees):
    """Nouvelle charge fixe : elle compte dès le mois en cours."""
    with _verrou:
        d = _charger()
        charge = {"id": _nouvel_id(), **_valider_charge(donnees or {}, d), "debut": _mois(), "generes": [],
                  "cree": _maintenant()}
        d["charges"].append(charge)
        appliquer_charges(d, aujourdhui())
        _ecrire(d)
        return _charge_pour_page(charge)


def modifier_charge(donnees):
    """Modifie une charge fixe et la dépense déjà créée ce mois-ci ; les mois
    passés ne changent pas."""
    donnees = donnees or {}
    with _verrou:
        d = _charger()
        charge = next((c for c in d["charges"] if c["id"] == donnees.get("id")), None)
        if charge is None:
            raise ValueError("Charge fixe introuvable.")
        charge.update(_valider_charge(donnees, d))
        mois = _mois()
        j = min(charge["jour"], jours_du_mois(mois))
        for dep in d["depenses"]:
            if dep.get("charge") == charge["id"] and dep["date"][:7] == mois:
                dep.update({"montant": charge["montant"], "categorie": charge["categorie"],
                            "description": charge["description"], "paiement": charge["paiement"],
                            "date": f"{mois}-{j:02d}", "pro": charge["pro"], "client_id": charge["client_id"],
                            "client_nom": charge["client_nom"]})
                if not dep["pro"]:
                    dep["statut"] = None
                elif dep.get("statut") not in STATUTS:
                    dep["statut"] = "a_rembourser"
        _ecrire(d)
        return _charge_pour_page(charge)


def arreter_charge(identifiant):
    """La charge n'est plus ajoutée les mois suivants ; les dépenses déjà
    enregistrées sont conservées (comme dans l'application d'origine, elles
    ne sont plus rattachées à la charge)."""
    with _verrou:
        d = _charger()
        avant = len(d["charges"])
        d["charges"] = [c for c in d["charges"] if c["id"] != identifiant]
        if len(d["charges"]) == avant:
            raise ValueError("Charge fixe introuvable.")
        for dep in d["depenses"]:
            if dep.get("charge") == identifiant:
                dep["charge"] = None
        _ecrire(d)
        return {"ok": True}


def _charge_pour_page(c):
    return {k: v for k, v in c.items() if k != "generes"}


# ---------------------------------------------------------------------------
# Catégories
# ---------------------------------------------------------------------------
def _categorie(d, identifiant):
    c = next((c for c in d["categories"] if c["id"] == identifiant), None)
    if c is None:
        raise ValueError("Choisissez une catégorie.")
    return c


def _valider_categorie(donnees, d, identifiant=None):
    nom = _texte_court(donnees.get("nom"), 40, "Nom")
    if not nom:
        raise ValueError("Donnez un nom à la catégorie.")
    if any(c["nom"].lower() == nom.lower() and c["id"] != identifiant for c in d["categories"]):
        raise ValueError("Une catégorie porte déjà ce nom.")
    icone = donnees.get("icone") or "tag"
    if icone not in ICONES_CATEGORIES:
        raise ValueError("Icône invalide.")
    couleur = donnees.get("couleur") or "gris"
    if couleur not in COULEURS:
        raise ValueError("Couleur invalide.")
    return {"nom": nom, "icone": icone, "couleur": couleur}


def ajouter_categorie(donnees):
    with _verrou:
        d = _charger()
        c = {"id": _nouvel_id(), **_valider_categorie(donnees or {}, d),
             "ordre": max([x.get("ordre", 0) for x in d["categories"]] + [0]) + 1, "epargne": False}
        d["categories"].append(c)
        _ecrire(d)
        return c


def modifier_categorie(donnees):
    """Renommer, changer d'icône ou de couleur (Épargne comprise)."""
    donnees = donnees or {}
    with _verrou:
        d = _charger()
        c = next((c for c in d["categories"] if c["id"] == donnees.get("id")), None)
        if c is None:
            raise ValueError("Catégorie introuvable.")
        c.update(_valider_categorie(donnees, d, c["id"]))
        _ecrire(d)
        return c


def utilisations(d, identifiant):
    return sum(1 for x in d["depenses"] + d["charges"] if x["categorie"] == identifiant)


def supprimer_categorie(identifiant, remplacement=None):
    """Supprime une catégorie. Si des dépenses ou des charges fixes
    l'utilisent, elles passent d'abord dans « remplacement » (obligatoire)."""
    with _verrou:
        d = _charger()
        c = next((c for c in d["categories"] if c["id"] == identifiant), None)
        if c is None:
            raise ValueError("Catégorie introuvable.")
        if c.get("epargne"):
            raise ValueError("La catégorie Épargne ne peut pas être supprimée.")
        if len(d["categories"]) <= 1:
            raise ValueError("Gardez au moins une catégorie.")
        if utilisations(d, identifiant):
            if not remplacement or remplacement == identifiant or \
                    not any(x["id"] == remplacement for x in d["categories"]):
                raise ValueError("Choisissez une catégorie de remplacement.")
            for x in d["depenses"] + d["charges"]:
                if x["categorie"] == identifiant:
                    x["categorie"] = remplacement
        d["categories"] = [x for x in d["categories"] if x["id"] != identifiant]
        _ecrire(d)
        return {"ok": True}


def _ids_epargne(d):
    return {c["id"] for c in d["categories"] if c.get("epargne")}


# ---------------------------------------------------------------------------
# Budget et épargne
# ---------------------------------------------------------------------------
def budget_du_mois(d, mois):
    """Le dernier budget défini jusqu'à ce mois (reconduit), ou None."""
    valeur = None
    for b in sorted(d["budgets"], key=lambda b: b["mois"]):
        if b["mois"] <= mois:
            valeur = _dec(b["montant"])
    return valeur


def definir_budget(montant):
    """Budget du mois en cours (reconduit les mois suivants). 0 : pas de budget."""
    with _verrou:
        d = _charger()
        valeur = _s(_montant(montant, zero_permis=True))
        mois = _mois()
        existant = next((b for b in d["budgets"] if b["mois"] == mois), None)
        if existant:
            existant["montant"] = valeur
        else:
            d["budgets"].append({"mois": mois, "montant": valeur})
        _ecrire(d)
        return {"mois": mois, "montant": valeur}


def _somme(liste):
    return sum((_dec(x["montant"]) for x in liste), ZERO)


def _du_mois(d, mois):
    return [x for x in d["depenses"] if x["date"][:7] == mois]


def repris_du_mois(d, mois):
    return _somme([r for r in d["reprises"] if r["mois"] == mois])


def solde_epargne(d):
    """Versé sur l'épargne depuis le début, repris, disponible."""
    ids = _ids_epargne(d)
    verse = _somme([x for x in d["depenses"] if x["categorie"] in ids])
    repris = _somme(d["reprises"])
    return {"verse": verse, "repris": repris, "disponible": verse - repris}


def depense_effective(d, mois):
    """Dépenses du mois moins ce qui a été repris sur l'épargne."""
    return _somme(_du_mois(d, mois)) - repris_du_mois(d, mois)


def proposition_reprise(d, montant, mois, sauf=None):
    """La reprise à proposer avant d'ajouter une dépense, ou None : pas de
    budget, budget non dépassé, ou aucune épargne disponible."""
    budget = budget_du_mois(d, mois)
    if budget is None or budget <= 0:
        return None
    deja = _somme([x for x in _du_mois(d, mois) if x["id"] != sauf])
    reste = budget - (deja - repris_du_mois(d, mois))
    depassement = montant - max(reste, ZERO)
    if depassement <= 0:
        return None
    disponible = max(solde_epargne(d)["disponible"], ZERO)
    if disponible <= 0:
        return None
    return {"depassement": _s(depassement), "disponible": _s(disponible), "suggere": _s(min(depassement, disponible))}


def annuler_reprise(identifiant):
    """La somme revient dans l'épargne ; la dépense est conservée et le
    dépassement qu'elle couvrait réapparaît."""
    with _verrou:
        d = _charger()
        avant = len(d["reprises"])
        d["reprises"] = [r for r in d["reprises"] if r["id"] != identifiant]
        if len(d["reprises"]) == avant:
            raise ValueError("Reprise introuvable.")
        _ecrire(d)
        return {"ok": True}


# ---------------------------------------------------------------------------
# Dépenses
# ---------------------------------------------------------------------------
def _paiement(valeur):
    if valeur not in PAIEMENTS:
        raise ValueError("Moyen de paiement invalide.")
    return valeur


def _valider_depense(donnees, d):
    pro = bool(donnees.get("pro"))
    statut = donnees.get("statut") or "a_rembourser"
    if pro and statut not in STATUTS:
        raise ValueError("Statut invalide.")
    return {"montant": _s(_montant(donnees.get("montant"))),
            "categorie": _categorie(d, donnees.get("categorie"))["id"],
            "description": _texte_court(donnees.get("description"), 120, "Description"),
            "date": _date(donnees.get("date") or aujourdhui().isoformat()),
            "paiement": _paiement(donnees.get("paiement") or "carte"),
            "note": str(donnees.get("note") or "").strip()[:500],
            "pro": pro,
            "client_id": _texte_court(donnees.get("client_id"), 64, "Client") if pro else "",
            "client_nom": _texte_court(donnees.get("client_nom"), 120, "Client") if pro else "",
            "statut": statut if pro else None}


def ajouter_depense(donnees, reprise=None):
    """Ajoute une dépense.

    Sans « reprise », si la dépense fait dépasser le budget de son mois et
    qu'il reste de l'épargne, RIEN n'est enregistré : la réponse porte
    « epargne » (dépassement, disponible, suggéré). La page rappelle alors
    avec le montant repris confirmé (0 : sans toucher à l'épargne)."""
    donnees = donnees or {}
    with _verrou:
        d = _charger()
        propre = _valider_depense(donnees, d)
        montant = _dec(propre["montant"])
        mois = propre["date"][:7]
        if reprise is None or reprise == "":
            proposition = proposition_reprise(d, montant, mois)
            if proposition:
                return {"ajoutee": False, "epargne": proposition}
            reprise = 0
        repris = _montant(reprise, zero_permis=True, nom="Montant pris sur l'épargne")
        if repris > montant:
            raise ValueError("Le montant pris sur l'épargne est invalide.")
        if repris > 0 and repris > solde_epargne(d)["disponible"]:
            raise ValueError("Votre épargne ne suffit pas pour ce montant.")
        depense = {"id": _nouvel_id(), **propre, "charge": None, "justificatif": None, "cree": _maintenant()}
        if donnees.get("justificatif_source"):
            depense["justificatif"] = _copier_justificatif(donnees["justificatif_source"], depense["id"])
        d["depenses"].append(depense)
        if repris > 0:
            d["reprises"].append({"id": _nouvel_id(), "depense": depense["id"], "mois": mois, "montant": _s(repris),
                                  "cree": _maintenant()})
        _ecrire(d)
        return {"ajoutee": True, "depense": depense, "repris": _s(repris)}


def modifier_depense(donnees):
    """Modifie une dépense (une dépense de charge fixe : ce mois-là seulement)."""
    donnees = donnees or {}
    with _verrou:
        d = _charger()
        dep = next((x for x in d["depenses"] if x["id"] == donnees.get("id")), None)
        if dep is None:
            raise ValueError("Dépense introuvable.")
        propre = _valider_depense(donnees, d)
        liees = [r for r in d["reprises"] if r["depense"] == dep["id"]]
        repris = _somme(liees)
        if _dec(propre["montant"]) < repris:
            raise ValueError("Le montant ne peut pas être inférieur à ce qui a été pris sur l'épargne. "
                             "Annulez d'abord la reprise.")
        if donnees.get("justificatif_source"):
            ancien = dep.get("justificatif")
            propre["justificatif"] = _copier_justificatif(donnees["justificatif_source"], dep["id"])
            if ancien and ancien != propre["justificatif"]:
                _supprimer_fichier(ancien)
        dep.update(propre)
        # La reprise compense le mois de la dépense.
        for r in liees:
            r["mois"] = dep["date"][:7]
        _ecrire(d)
        return dep


def supprimer_depense(identifiant):
    """Supprime la dépense, sa reprise sur l'épargne et son justificatif.
    Une dépense de charge fixe supprimée n'est jamais recréée."""
    with _verrou:
        d = _charger()
        dep = next((x for x in d["depenses"] if x["id"] == identifiant), None)
        if dep is None:
            raise ValueError("Dépense introuvable.")
        d["depenses"].remove(dep)
        d["reprises"] = [r for r in d["reprises"] if r["depense"] != identifiant]
        _ecrire(d)
        if dep.get("justificatif"):
            _supprimer_fichier(dep["justificatif"])
        return {"ok": True}


def changer_statut(identifiant, statut):
    """Statut d'une note de frais (à rembourser, remboursée, refacturée)."""
    if statut not in STATUTS:
        raise ValueError("Statut invalide.")
    with _verrou:
        d = _charger()
        dep = next((x for x in d["depenses"] if x["id"] == identifiant), None)
        if dep is None:
            raise ValueError("Dépense introuvable.")
        if not dep.get("pro"):
            raise ValueError("Ce n'est pas une dépense professionnelle.")
        dep["statut"] = statut
        _ecrire(d)
        return dep


# ---------------------------------------------------------------------------
# Justificatifs
# ---------------------------------------------------------------------------
def dossier_justificatifs():
    return os.path.join(config.DONNEES, NOM, "justificatifs")


def _chemin_justificatif(nom):
    """Le chemin d'un justificatif, toujours dans son dossier."""
    if not nom or os.path.basename(nom) != nom:
        raise ValueError("Justificatif introuvable.")
    return os.path.join(dossier_justificatifs(), nom)


def _copier_justificatif(source, depense_id):
    chemin = os.path.normpath(str(source).strip().strip('"'))
    if not os.path.isfile(chemin):
        raise ValueError("Fichier introuvable.")
    base, ext = os.path.splitext(os.path.basename(chemin))
    ext = ext.lower()
    if ext not in EXTENSIONS_JUSTIFICATIF:
        raise ValueError("Justificatif : une photo ou un PDF seulement.")
    if os.path.getsize(chemin) > TAILLE_MAX_JUSTIFICATIF:
        raise ValueError("Justificatif trop lourd (25 Mo au plus).")
    propre = re.sub(r"[^\w.-]+", "-", base, flags=re.UNICODE).strip("-.")[:60] or "justificatif"
    nom = f"{depense_id}-{propre}{ext}"
    os.makedirs(dossier_justificatifs(), exist_ok=True)
    shutil.copyfile(chemin, os.path.join(dossier_justificatifs(), nom))
    return nom


def _supprimer_fichier(nom):
    try:
        os.remove(_chemin_justificatif(nom))
    except (OSError, ValueError):
        pass


def joindre_justificatif(identifiant, source):
    with _verrou:
        d = _charger()
        dep = next((x for x in d["depenses"] if x["id"] == identifiant), None)
        if dep is None:
            raise ValueError("Dépense introuvable.")
        ancien = dep.get("justificatif")
        dep["justificatif"] = _copier_justificatif(source, dep["id"])
        if ancien and ancien != dep["justificatif"]:
            _supprimer_fichier(ancien)
        _ecrire(d)
        return dep


def retirer_justificatif(identifiant):
    with _verrou:
        d = _charger()
        dep = next((x for x in d["depenses"] if x["id"] == identifiant), None)
        if dep is None:
            raise ValueError("Dépense introuvable.")
        if dep.get("justificatif"):
            _supprimer_fichier(dep["justificatif"])
        dep["justificatif"] = None
        _ecrire(d)
        return dep


def _ouvrir(chemin):
    os.startfile(chemin)  # noqa: S606 (fichier de notre dossier, ouvert par Windows)


def ouvrir_justificatif(identifiant):
    with _verrou:
        d = _lire()
        dep = next((x for x in d["depenses"] if x["id"] == identifiant), None)
    if dep is None or not dep.get("justificatif"):
        raise ValueError("Justificatif introuvable.")
    chemin = _chemin_justificatif(dep["justificatif"])
    if not os.path.isfile(chemin):
        raise ValueError("Justificatif introuvable.")
    _ouvrir(chemin)
    return {"ok": True}


SCRIPT_FICHIER = r"""
Add-Type -AssemblyName System.Windows.Forms
$p = New-Object System.Windows.Forms.Form
$p.TopMost = $true
$d = New-Object System.Windows.Forms.OpenFileDialog
$d.Title = $env:MO_TITRE
$d.Filter = $env:MO_FILTRE
$d.Multiselect = $false
$d.CheckFileExists = $true
if ($d.ShowDialog($p) -eq [System.Windows.Forms.DialogResult]::OK) {
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  Write-Output $d.FileName
}
"""


def choisir_fichier(d=None):
    """Ouvre la fenêtre « Ouvrir » de Windows (photo ou PDF), au premier plan.
    Renvoie {"chemin", "nom"} ou {"chemin": None} si annulé."""
    d = d or {}
    motifs = ";".join("*" + e for e in EXTENSIONS_JUSTIFICATIF)
    libelle = "Receipts" if config.langue() == "en" else "Justificatifs"
    env = dict(os.environ, MO_TITRE=str(d.get("titre") or "Choisir un justificatif")[:120],
               MO_FILTRE=f"{libelle} (photo, PDF)|{motifs}")
    r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-STA", "-Command", SCRIPT_FICHIER],
                       env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=600, creationflags=CREATE_NO_WINDOW)
    lignes = (r.stdout or "").strip().splitlines()
    chemin = lignes[-1].strip() if lignes else ""
    if not chemin or not os.path.isfile(chemin):
        return {"chemin": None}
    return {"chemin": chemin, "nom": os.path.basename(chemin)}


# ---------------------------------------------------------------------------
# Lectures pour la page
# ---------------------------------------------------------------------------
def _contexte(d):
    return {"devise": devise(), "aujourdhui": aujourdhui().isoformat(), "mois": _mois(),
            "categories": sorted(d["categories"], key=lambda c: (c.get("ordre", 0), c["nom"].lower()))}


def _avec_reprise(d, depenses):
    """Chaque dépense avec ce qui a été pris sur l'épargne pour elle."""
    par_depense = {}
    for r in d["reprises"]:
        par_depense[r["depense"]] = par_depense.get(r["depense"], ZERO) + _dec(r["montant"])
    return [{**x, "repris": _s(par_depense[x["id"]]) if x["id"] in par_depense else None} for x in depenses]


def _recentes(liste):
    return sorted(liste, key=lambda x: (x["date"], x.get("cree", "")), reverse=True)


def par_categorie(d, liste):
    """Totaux par catégorie, du plus gros au plus petit."""
    totaux = {}
    for x in liste:
        t = totaux.setdefault(x["categorie"], [ZERO, 0])
        t[0] += _dec(x["montant"])
        t[1] += 1
    total = sum((t[0] for t in totaux.values()), ZERO)
    cats = {c["id"]: c for c in d["categories"]}
    sortie = []
    for cid, (somme, nombre) in totaux.items():
        c = cats.get(cid) or {"nom": "Sans catégorie", "icone": "tag", "couleur": "gris"}
        sortie.append({"id": cid, "nom": c["nom"], "icone": c["icone"], "couleur": c["couleur"], "total": _s(somme),
                       "nombre": nombre, "part": round(float(somme / total), 4) if total else 0})
    return sorted(sortie, key=lambda x: (-_dec(x["total"]), x["nom"].lower()))


def niveau_budget(ratio):
    if ratio > 1:
        return "depasse"
    if ratio >= Decimal("0.9"):
        return "presque"
    if ratio >= Decimal("0.7"):
        return "attention"
    return "normal"


def _infos_budget(d, mois, jour):
    """Le budget du mois : dépensé effectif, reste, par jour, projection."""
    liste = _du_mois(d, mois)
    repris = repris_du_mois(d, mois)
    brut = _somme(liste)
    fixes = _somme([x for x in liste if x.get("charge")])
    depense = brut - repris
    budget = budget_du_mois(d, mois)
    jours = jours_du_mois(mois)
    jour_du_mois = int(jour[8:10]) if jour[:7] == mois else jours
    jours_restants = jours - jour_du_mois + 1
    # Charges fixes (connues) + variable réel au rythme actuel, moins ce que
    # l'épargne couvre déjà.
    variable_brut = brut - fixes
    projection = fixes + variable_brut / jour_du_mois * jours - repris
    infos = {"mois": mois, "depense": _s(depense), "brut": _s(brut), "fixes": _s(fixes),
             "variables": _s(variable_brut), "repris": _s(repris), "budget": _s(budget) if budget is not None else None,
             "jours_restants": jours_restants, "jour": jour_du_mois, "jours": jours, "projection": _s(projection),
             "nombre": len(liste)}
    if budget is not None and budget > 0:
        ratio = depense / budget
        reste = budget - depense
        infos.update({"ratio": round(float(ratio), 4), "niveau": niveau_budget(ratio), "reste": _s(reste),
                      "par_jour": _s(reste / jours_restants) if reste > 0 else None})
    return infos


def tableau(_d=None):
    """Accueil : total du mois, budget, fixe / variable, épargne, repères pour
    le message utile, dernières dépenses, par catégorie, notes de frais."""
    with _verrou:
        d = _charger()
    jour = aujourdhui().isoformat()
    mois, precedent = jour[:7], ajouter_mois(jour[:7], -1)
    infos = _infos_budget(d, mois, jour)
    liste = _du_mois(d, mois)
    ids = _ids_epargne(d)
    solde = solde_epargne(d)
    verse_mois = _somme([x for x in liste if x["categorie"] in ids])
    repris = repris_du_mois(d, mois)
    # Comparaison sur le variable uniquement : les charges fixes faussent la « même date ».
    meme_jour = f"{precedent}-{min(int(jour[8:10]), jours_du_mois(precedent)):02d}"
    precedent_a_date = _somme([x for x in _du_mois(d, precedent) if not x.get("charge") and x["date"] <= meme_jour])
    variable_a_date = _somme([x for x in liste if not x.get("charge") and x["date"] <= jour])
    cats = par_categorie(d, liste)
    a_rembourser = [x for x in d["depenses"] if x.get("pro") and x.get("statut") == "a_rembourser"]
    return {**_contexte(d), "budget": infos,
            "charges": {"nombre": len(d["charges"])},
            "variables_nombre": sum(1 for x in liste if not x.get("charge")),
            "epargne": {"disponible": _s(solde["disponible"]), "verse": _s(solde["verse"]),
                        "epargne_mois": _s(verse_mois - repris), "repris_mois": _s(repris),
                        "existe": solde["verse"] > 0 or any(c["categorie"] in ids for c in d["charges"])},
            "comparaison": {"precedent_a_date": _s(precedent_a_date), "variable_a_date": _s(variable_a_date)},
            "guide": {"charges": bool(d["charges"]), "variables": any(not x.get("charge") for x in d["depenses"]),
                      "budget": infos["budget"] is not None},
            "dernieres": _avec_reprise(d, _recentes([x for x in d["depenses"] if x["date"] <= _fin_mois(mois)])[:5]),
            "par_categorie": cats,
            "notes": {"nombre": len(a_rembourser), "total": _s(_somme(a_rembourser))}}


TRIS = ("date_desc", "date_asc", "montant_desc", "montant_asc")


def liste_mois(donnees):
    """Dépenses d'un mois (ou de tous les mois si recherche), filtres et tri."""
    donnees = donnees or {}
    with _verrou:
        d = _charger()
    mois = _mois(donnees.get("mois"))
    q = " ".join(str(donnees.get("q") or "").split())[:80].lower()
    liste = d["depenses"] if q else _du_mois(d, mois)
    if q:
        noms = {c["id"]: c["nom"].lower() for c in d["categories"]}
        liste = [x for x in liste if q in (x.get("description") or "").lower() or q in (x.get("note") or "").lower()
                 or q in (x.get("client_nom") or "").lower() or q in noms.get(x["categorie"], "")]
    if donnees.get("categorie"):
        liste = [x for x in liste if x["categorie"] == donnees["categorie"]]
    if donnees.get("pro"):
        liste = [x for x in liste if x.get("pro")]
    tri = donnees.get("tri") if donnees.get("tri") in TRIS else "date_desc"
    if tri.startswith("montant"):
        liste = sorted(liste, key=lambda x: (_dec(x["montant"]), x["date"]), reverse=tri.endswith("desc"))
    else:
        liste = sorted(liste, key=lambda x: (x["date"], x.get("cree", "")), reverse=tri.endswith("desc"))
    return {**_contexte(d), "mois_affiche": mois, "recherche": bool(q), "tri": tri,
            "depenses": _avec_reprise(d, liste), "total": _s(_somme(liste)),
            "fixes": _s(_somme([x for x in liste if x.get("charge")])), "nombre": len(liste),
            "repris": _s(repris_du_mois(d, mois)) if not q else "0.00"}


def liste_charges(_d=None):
    with _verrou:
        d = _charger()
    charges = sorted(d["charges"], key=lambda c: (c["jour"], c.get("cree", "")))
    total = _somme(charges)
    budget = budget_du_mois(d, _mois())
    ids = _ids_epargne(d)
    return {**_contexte(d), "charges": [_charge_pour_page(c) for c in charges], "total": _s(total),
            "reste_variable": _s(budget - total) if budget is not None and budget > 0 else None,
            "epargne": any(c["categorie"] in ids for c in charges)}


def page_budget(_d=None):
    """Budget du mois et historique des 6 derniers mois."""
    with _verrou:
        d = _charger()
    jour = aujourdhui().isoformat()
    mois = jour[:7]
    historique = []
    for i in range(6):
        m = ajouter_mois(mois, -i)
        b = budget_du_mois(d, m)
        depense = depense_effective(d, m)
        historique.append({"mois": m, "depense": _s(depense), "budget": _s(b) if b is not None else None,
                           "ratio": round(float(depense / b), 4) if b else None,
                           "niveau": niveau_budget(depense / b) if b else None})
    return {**_contexte(d), "budget": _infos_budget(d, mois, jour), "historique": historique}


def page_epargne(_d=None):
    """Épargne disponible, mois en cours (prévu, repris, épargné), reprises,
    historique sur 12 mois."""
    with _verrou:
        d = _charger()
    mois = _mois()
    ids = _ids_epargne(d)
    solde = solde_epargne(d)
    charges = [_charge_pour_page(c) for c in d["charges"] if c["categorie"] in ids]
    historique = []
    for i in range(12):
        m = ajouter_mois(mois, -i)
        verse = _somme([x for x in _du_mois(d, m) if x["categorie"] in ids])
        repris = repris_du_mois(d, m)
        if verse > 0 or repris > 0 or m == mois:
            historique.append({"mois": m, "verse": _s(verse), "repris": _s(repris), "net": _s(verse - repris)})
    deps = {x["id"]: x for x in d["depenses"]}
    reprises = []
    for r in sorted(d["reprises"], key=lambda r: r.get("cree", ""), reverse=True):
        dep = deps.get(r["depense"])
        reprises.append({**r, "depense_info": {"description": dep.get("description"), "date": dep["date"],
                                               "montant": dep["montant"], "categorie": dep["categorie"]} if dep else None})
    actuel = historique[0] if historique and historique[0]["mois"] == mois else \
        {"mois": mois, "verse": "0.00", "repris": "0.00", "net": "0.00"}
    return {**_contexte(d), "disponible": _s(solde["disponible"]), "verse": _s(solde["verse"]),
            "repris": _s(solde["repris"]), "charges": charges, "ce_mois": actuel,
            "reprises": reprises, "historique": [h for h in historique if h["verse"] != "0.00" or h["repris"] != "0.00"],
            "existe": solde["verse"] > 0 or bool(charges)}


PERIODES_STATS = ("mois", "precedent", "3m", "12m")


def _variation(actuel, precedent):
    if precedent <= 0:
        return None
    return round(float((actuel - precedent) / precedent), 4)


def statistiques(donnees):
    """Par catégorie, moyenne quotidienne, plus grosse dépense, comparaison
    avec le mois précédent à date égale, évolution jour / semaine / mois,
    6 derniers mois."""
    donnees = donnees or {}
    periode = donnees.get("periode") if donnees.get("periode") in PERIODES_STATS else "mois"
    with _verrou:
        d = _charger()
    jour = aujourdhui().isoformat()
    mois = jour[:7]
    precedent = ajouter_mois(mois, -1)
    debut_annee = ajouter_mois(mois, -11)
    bornes = {"mois": (mois, mois), "precedent": (precedent, precedent), "3m": (ajouter_mois(mois, -2), mois),
              "12m": (debut_annee, mois)}[periode]
    de, a = f"{bornes[0]}-01", _fin_mois(bornes[1])
    choisies = [x for x in d["depenses"] if de <= x["date"] <= a]
    total = _somme(choisies)
    fin_ecoulee = min(a, jour)
    nb_jours = max(1, (datetime.date.fromisoformat(fin_ecoulee) - datetime.date.fromisoformat(de)).days + 1)
    plus_grosse = max(choisies, key=lambda x: (_dec(x["montant"]), x["date"]), default=None)
    meme_jour = f"{precedent}-{min(int(jour[8:10]), jours_du_mois(precedent)):02d}"
    ce_mois = _somme(_du_mois(d, mois))
    mois_dernier = _somme(_du_mois(d, precedent))
    dernier_a_date = _somme([x for x in _du_mois(d, precedent) if x["date"] <= meme_jour])
    ce_mois_a_date = _somme([x for x in _du_mois(d, mois) if x["date"] <= jour])

    def serie_jours():
        totaux = {}
        for x in _du_mois(d, mois):
            totaux[x["date"]] = totaux.get(x["date"], ZERO) + _dec(x["montant"])
        return [{"cle": f"{mois}-{j:02d}", "total": _s(totaux.get(f"{mois}-{j:02d}", ZERO))}
                for j in range(1, jours_du_mois(mois) + 1)]

    def serie_semaines(n=12):
        premier = datetime.date.fromisoformat(_lundi(jour)) - datetime.timedelta(weeks=n - 1)
        totaux = {}
        for x in d["depenses"]:
            if premier.isoformat() <= x["date"] <= _fin_mois(mois):
                cle = _lundi(x["date"])
                totaux[cle] = totaux.get(cle, ZERO) + _dec(x["montant"])
        cles = [(premier + datetime.timedelta(weeks=i)).isoformat() for i in range(n)]
        return [{"cle": c, "total": _s(totaux.get(c, ZERO))} for c in cles]

    def serie_mois(n):
        return [{"cle": ajouter_mois(mois, i - n + 1), "total": _s(_somme(_du_mois(d, ajouter_mois(mois, i - n + 1))))}
                for i in range(n)]

    six = list(reversed(serie_mois(7)))
    derniers = []
    for i, m in enumerate(six[:6]):
        en_cours = m["cle"] == mois
        derniers.append({"mois": m["cle"], "total": m["total"], "en_cours": en_cours,
                         "variation": None if en_cours else _variation(_dec(m["total"]), _dec(six[i + 1]["total"]))})
    cats = {c["id"]: c["nom"] for c in d["categories"]}
    return {**_contexte(d), "periode": periode, "de": de, "a": a,
            "vide": not any(debut_annee + "-01" <= x["date"] <= _fin_mois(mois) for x in d["depenses"]),
            "total": _s(total), "par_categorie": par_categorie(d, choisies),
            "moyenne": _s(total / nb_jours),
            "plus_grosse": {"montant": plus_grosse["montant"], "date": plus_grosse["date"],
                            "description": plus_grosse.get("description") or cats.get(plus_grosse["categorie"], "")}
            if plus_grosse else None,
            "comparaison": {"ce_mois": _s(ce_mois), "mois_dernier": _s(mois_dernier), "mois_precedent": precedent,
                            "dernier_a_date": _s(dernier_a_date), "ce_mois_a_date": _s(ce_mois_a_date),
                            "meme_jour": meme_jour, "variation": _variation(ce_mois_a_date, dernier_a_date)},
            "series": {"jour": serie_jours(), "semaine": serie_semaines(), "mois": serie_mois(12)},
            "derniers_mois": derniers}


def notes_de_frais(donnees):
    """Les dépenses professionnelles, filtrées par statut et par mois."""
    donnees = donnees or {}
    with _verrou:
        d = _charger()
    pros = [x for x in d["depenses"] if x.get("pro")]
    totaux = {s: {"nombre": 0, "total": ZERO} for s in STATUTS}
    for x in pros:
        t = totaux.get(x.get("statut") or "a_rembourser")
        if t:
            t["nombre"] += 1
            t["total"] += _dec(x["montant"])
    liste = pros
    statut = donnees.get("statut")
    if statut in STATUTS:
        liste = [x for x in liste if x.get("statut") == statut]
    if donnees.get("mois"):
        mois = _mois(donnees["mois"])
        liste = [x for x in liste if x["date"][:7] == mois]
    return {**_contexte(d), "notes": _avec_reprise(d, _recentes(liste)), "total": _s(_somme(liste)),
            "totaux": {s: {"nombre": t["nombre"], "total": _s(t["total"])} for s, t in totaux.items()},
            "sans_justificatif": sum(1 for x in liste if not x.get("justificatif"))}


def reglages(_d=None):
    with _verrou:
        d = _charger()
    ctx = _contexte(d)
    ctx["categories"] = [{**c, "utilisations": utilisations(d, c["id"])} for c in ctx["categories"]]
    return {**ctx, "devises": list(DEVISES), "icones": list(ICONES_CATEGORIES), "couleurs": list(COULEURS),
            "dossier_justificatifs": dossier_justificatifs()}


def changer_devise(code):
    """Seul l'affichage change : les montants ne sont pas convertis."""
    if code not in DEVISES:
        raise ValueError("Devise non prise en charge.")
    config.modifier_section(NOM, devise=code)
    return {"devise": code}


def resume(_d=None):
    """Pour la carte de l'Accueil : dépensé ce mois, budget, notes de frais."""
    with _verrou:
        d = _charger()
    jour = aujourdhui().isoformat()
    infos = _infos_budget(d, jour[:7], jour)
    a_rembourser = [x for x in d["depenses"] if x.get("pro") and x.get("statut") == "a_rembourser"]
    return {"devise": devise(), "depense": infos["depense"], "budget": infos["budget"], "ratio": infos.get("ratio"),
            "niveau": infos.get("niveau"), "nombre": infos["nombre"],
            "notes": {"nombre": len(a_rembourser), "total": _s(_somme(a_rembourser))}}


# ---------------------------------------------------------------------------
# Export CSV (Excel en français : séparateur « ; », UTF-8 avec BOM)
# ---------------------------------------------------------------------------
_FORMULE = re.compile(r"^[=+@\t\r]|^-[^\s\-]")


def _cellule(valeur):
    """Un texte qu'Excel ne prendra pas pour une formule."""
    valeur = str(valeur or "")
    return "'" + valeur if _FORMULE.match(valeur) else valeur


def _montant_csv(montant):
    chiffres = DEVISES[devise()]
    return str(_dec(montant).quantize(Decimal(1).scaleb(-chiffres), rounding=ROUND_HALF_UP)).replace(".", ",")


def export_csv(donnees=None):
    """{nom, csv} : dépenses d'un mois (« YYYY-MM ») ou de tous les mois
    (« tout »), toutes ou les notes de frais seulement (pro=True), un statut
    au choix. Le texte commence par le BOM UTF-8."""
    donnees = donnees or {}
    periode = donnees.get("mois") or "tout"
    with _verrou:
        d = _charger()
    liste = d["depenses"]
    if periode != "tout":
        periode = _mois(periode)
        liste = [x for x in liste if x["date"][:7] == periode]
    pro = bool(donnees.get("pro"))
    if pro:
        liste = [x for x in liste if x.get("pro")]
    if donnees.get("statut") in STATUTS:
        liste = [x for x in liste if x.get("statut") == donnees["statut"]]
    liste = sorted(liste, key=lambda x: (x["date"], x.get("cree", "")))
    cats = {c["id"]: c["nom"] for c in d["categories"]}
    code = devise()
    sortie = io.StringIO()
    ecrivain = csv.writer(sortie, delimiter=";", lineterminator="\r\n")
    ecrivain.writerow([_texte(x) for x in ("Date", "Description", "Catégorie", "Montant", "Devise", "Paiement",
                                           "Professionnelle", "Client", "Statut", "Justificatif", "Note")])
    for x in liste:
        ecrivain.writerow([
            datetime.date.fromisoformat(x["date"]).strftime("%d/%m/%Y"), _cellule(x.get("description")),
            _cellule(cats.get(x["categorie"], "")), _montant_csv(x["montant"]), code,
            _texte(LIBELLES_PAIEMENTS.get(x.get("paiement"), "Autre")),
            _texte("Oui" if x.get("pro") else "Non"), _cellule(x.get("client_nom")),
            _texte(LIBELLES_STATUTS[x["statut"]]) if x.get("pro") and x.get("statut") in STATUTS else "",
            x.get("justificatif") or "", _cellule(x.get("note"))])
    ecrivain.writerow([])
    ecrivain.writerow([_texte("Total"), "", "", _montant_csv(_somme(liste)), code, "", "", "", "", "", ""])
    prefixe = "notes-de-frais" if pro else "depenses"
    return {"nom": f"{prefixe}-{periode}.csv", "csv": "﻿" + sortie.getvalue(), "lignes": len(liste)}


# ---------------------------------------------------------------------------
# Pour la bulle
# ---------------------------------------------------------------------------
def _format(montant, code):
    """« 1 250,50 € » (fr) ou « €1,250.50 » (en), sans centimes inutiles."""
    chiffres = DEVISES[code]
    valeur = _dec(montant).quantize(Decimal(1).scaleb(-chiffres), rounding=ROUND_HALF_UP)
    if chiffres and valeur == valeur.to_integral_value():
        chiffres = 0
    texte = f"{valeur:,.{chiffres}f}"
    if config.langue() == "en":
        return f"{SYMBOLES[code]}{texte}" if code != "MGA" else f"{texte} Ar"
    return texte.replace(",", " ").replace(".", ",") + " " + SYMBOLES[code]


def alertes_dues():
    """Budget du mois dépassé (une fois par mois) : [{id, titre, detail}]."""
    with _verrou:
        d = _charger()
        mois = _mois()
        budget = budget_du_mois(d, mois)
        if budget is None or budget <= 0:
            return []
        depense = depense_effective(d, mois)
        identifiant = f"budget-{mois}"
        if depense <= budget or identifiant in d["alertes_vues"]:
            return []
        code = devise()
        return [{"id": identifiant, "titre": _texte("Budget dépassé"),
                 "detail": _texte("Dépensé {depense} sur {budget} ce mois-ci.",
                                  depense=_format(depense, code), budget=_format(budget, code))}]


def marquer_alerte(identifiant):
    """Alerte vue. Renvoie True si elle est nouvelle."""
    if not re.fullmatch(r"budget-\d{4}-\d{2}", str(identifiant or "")):
        return False
    with _verrou:
        d = _lire()
        if identifiant in d["alertes_vues"]:
            return False
        d["alertes_vues"] = (d["alertes_vues"] + [identifiant])[-24:]
        _ecrire(d)
        return True


# ---------------------------------------------------------------------------
# Routes de la page
# ---------------------------------------------------------------------------
ROUTES = {
    "tableau": tableau,
    "resume": resume,
    "liste": liste_mois,
    "ajouter": lambda d: ajouter_depense(d.get("depense"), d.get("reprise")),
    "modifier": lambda d: modifier_depense(d.get("depense")),
    "supprimer": lambda d: supprimer_depense(d.get("id")),
    "statut": lambda d: changer_statut(d.get("id"), d.get("statut")),
    "charges": liste_charges,
    "charges/ajouter": lambda d: ajouter_charge(d.get("charge")),
    "charges/modifier": lambda d: modifier_charge(d.get("charge")),
    "charges/arreter": lambda d: arreter_charge(d.get("id")),
    "budget": page_budget,
    "budget/definir": lambda d: definir_budget(d.get("montant")),
    "epargne": page_epargne,
    "epargne/annuler": lambda d: annuler_reprise(d.get("id")),
    "statistiques": statistiques,
    "notes": notes_de_frais,
    "export": export_csv,
    "reglages": reglages,
    "devise": lambda d: changer_devise(d.get("devise")),
    "categories/ajouter": ajouter_categorie,
    "categories/modifier": modifier_categorie,
    "categories/supprimer": lambda d: supprimer_categorie(d.get("id"), d.get("remplacement")),
    "justificatif/choisir": choisir_fichier,
    "justificatif/joindre": lambda d: joindre_justificatif(d.get("id"), d.get("chemin")),
    "justificatif/retirer": lambda d: retirer_justificatif(d.get("id")),
    "justificatif/ouvrir": lambda d: ouvrir_justificatif(d.get("id")),
    "alertes": lambda d: {"alertes": alertes_dues()},
    "marquer_alerte": lambda d: {"ok": marquer_alerte(d.get("id"))},
}
