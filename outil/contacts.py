# -*- coding: utf-8 -*-
"""Application Contacts : un petit carnet de clients (mini-CRM).

- Fiches « personne » ou « entreprise » ; une personne peut appartenir à une
  entreprise (entreprise_id).
- Coordonnées (e-mail, téléphone, adresse, site), statut (prospect, client,
  ancien client, fournisseur, autre), étiquettes.
- Historique des échanges : notes datées (appel, mail, rendez-vous, note).
- Date de relance (« relancer le … ») : la bulle prévient le jour venu
  (alertes_dues / marquer_alerte), l'Accueil montre les relances à faire.
- Import et export CSV pour Excel (séparateur « ; », UTF-8 avec BOM).

Données : donnees\\contacts.json = {"contacts": [...]}, dates locales ISO
(« YYYY-MM-DD » pour la relance, « YYYY-MM-DDTHH:MM » pour les notes).

Pour les autres applications (contrat fixe) :
- POST /api/contacts/liste {recherche?}
  → {contacts: [{id, nom, entreprise, email, telephone, statut}]}
- POST /api/contacts/fiche {id} → la fiche complète.
"""
import csv
import datetime
import io
import re
import threading
import unicodedata
import uuid

import config

NOM = "contacts"
TYPES = ("personne", "entreprise")
STATUTS = ("prospect", "client", "ancien", "fournisseur", "autre")
TYPES_NOTES = ("appel", "mail", "rdv", "note")
FORMAT_NOTE = "%Y-%m-%dT%H:%M"
MAX_COURT = 120
MAX_ADRESSE = 300
MAX_NOTE = 4000
MAX_ETIQUETTE = 30
MAX_ETIQUETTES = 20
MAX_CSV = 5 * 1024 * 1024
MAX_ERREURS_IMPORT = 10

_verrou = threading.RLock()

# Textes de la bulle et de l'export (la bulle n'a pas le dictionnaire de la page).
_ANGLAIS = {
    "Relancer {nom}": "Follow up with {nom}",
    "Relance prévue le {date}.": "Follow-up planned for {date}.",
    "Personne": "Person", "Entreprise": "Company",
    "Prospect": "Prospect", "Client": "Client", "Ancien client": "Former client",
    "Fournisseur": "Supplier", "Autre": "Other",
    "Type": "Type", "Prénom": "First name", "Nom": "Last name", "Poste": "Job title",
    "Statut": "Status", "E-mail": "Email", "Téléphone": "Phone", "Adresse": "Address",
    "Site web": "Website", "Étiquettes": "Tags", "Relance": "Follow-up",
    "Motif de relance": "Follow-up reason", "Dernier échange": "Last contact",
}
LIBELLES_STATUTS = {"prospect": "Prospect", "client": "Client", "ancien": "Ancien client",
                    "fournisseur": "Fournisseur", "autre": "Autre"}
LIBELLES_TYPES = {"personne": "Personne", "entreprise": "Entreprise"}
COLONNES = (("type", "Type"), ("prenom", "Prénom"), ("nom", "Nom"), ("entreprise", "Entreprise"),
            ("poste", "Poste"), ("statut", "Statut"), ("email", "E-mail"), ("telephone", "Téléphone"),
            ("adresse", "Adresse"), ("site", "Site web"), ("etiquettes", "Étiquettes"),
            ("relance", "Relance"), ("relance_motif", "Motif de relance"), ("dernier_echange", "Dernier échange"))


def _texte(fr, **valeurs):
    texte = _ANGLAIS.get(fr, fr) if config.langue() == "en" else fr
    return texte.format(**valeurs) if valeurs else texte


def aujourdhui():
    """La date locale (remplacée par une date simulée dans les tests)."""
    return datetime.date.today()


def maintenant():
    """L'heure locale, à la minute (remplacée dans les tests)."""
    return datetime.datetime.now().replace(second=0, microsecond=0)


def _sans_accents(texte):
    texte = unicodedata.normalize("NFD", str(texte or ""))
    return "".join(c for c in texte if unicodedata.category(c) != "Mn").lower()


def _chiffres(texte):
    return re.sub(r"\D", "", str(texte or ""))


# ---------------------------------------------------------------------------
# Fichier
# ---------------------------------------------------------------------------
def _lire():
    d = config.lire_donnees(NOM, {})
    if not isinstance(d, dict):
        d = {}
    if not isinstance(d.get("contacts"), list):
        d["contacts"] = []
    return d


def _ecrire(d):
    config.ecrire_donnees(NOM, d)


def _trouver(d, identifiant):
    return next((c for c in d["contacts"] if c.get("id") == identifiant), None)


def nom_affiche(c):
    """« Prénom Nom » pour une personne, le nom pour une entreprise."""
    if c.get("type") == "entreprise":
        return c.get("nom") or ""
    return " ".join(x for x in (c.get("prenom"), c.get("nom")) if x)


def _nom_entreprise(d, c):
    if c.get("type") != "personne" or not c.get("entreprise_id"):
        return ""
    e = _trouver(d, c["entreprise_id"])
    return nom_affiche(e) if e else ""


def _cle_tri(c):
    return _sans_accents(nom_affiche(c))


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
RE_EMAIL = re.compile(r"^[^@\s<>\"',;]+@[^@\s<>\"',;]+\.[^@\s<>\"',;]{2,}$")
RE_TELEPHONE = re.compile(r"^\+?[0-9 ().\-/]{3,30}$")


def _court(valeur, limite=MAX_COURT):
    return " ".join(str(valeur or "").split())[:limite]


def _email(valeur):
    email = str(valeur or "").strip()
    if email.lower().startswith("mailto:"):
        email = email[7:]
    if email and not RE_EMAIL.match(email):
        raise ValueError("Adresse e-mail invalide.")
    return email[:MAX_COURT]


def _telephone(valeur):
    tel = " ".join(str(valeur or "").split())
    if tel.lower().startswith("tel:"):
        tel = tel[4:]
    if tel and (not RE_TELEPHONE.match(tel) or len(_chiffres(tel)) < 3):
        raise ValueError("Numéro de téléphone invalide.")
    return tel


def _site(valeur):
    site = str(valeur or "").strip()
    if not site:
        return ""
    if not re.match(r"^https?://", site, re.I):
        if "://" in site or ":" in site.split("/")[0]:
            raise ValueError("Adresse du site invalide.")
        site = "https://" + site
    if re.search(r"\s", site) or "." not in site.split("//", 1)[1].split("/")[0]:
        raise ValueError("Adresse du site invalide.")
    return site[:MAX_ADRESSE]


def _adresse(valeur):
    lignes = [" ".join(x.split()) for x in str(valeur or "").replace("\r", "").split("\n")]
    return "\n".join(x for x in lignes if x)[:MAX_ADRESSE]


def _date(valeur, nom="Date de relance"):
    """« YYYY-MM-DD » (ou « JJ/MM/AAAA »), ou "" si vide."""
    texte = str(valeur or "").strip()
    if not texte:
        return ""
    for format_ in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.datetime.strptime(texte[:10], format_).date().isoformat()
        except ValueError:
            continue
    raise ValueError(f"{nom} invalide.")


def _etiquettes(valeur):
    if isinstance(valeur, str):
        valeur = re.split(r"[,;]", valeur)
    propres, vues = [], set()
    for e in valeur or []:
        e = _court(e, MAX_ETIQUETTE).lstrip("#")
        if e and _sans_accents(e) not in vues:
            vues.add(_sans_accents(e))
            propres.append(e)
    return propres[:MAX_ETIQUETTES]


def _statut(valeur):
    statut = str(valeur or "prospect").strip()
    if statut not in STATUTS:
        raise ValueError("Statut inconnu.")
    return statut


# ---------------------------------------------------------------------------
# Lecture
# ---------------------------------------------------------------------------
def _resume(d, c):
    """Le format public (contrat fixe des autres applications)."""
    return {"id": c["id"], "nom": nom_affiche(c), "entreprise": _nom_entreprise(d, c),
            "email": c.get("email", ""), "telephone": c.get("telephone", ""), "statut": c.get("statut", "autre")}


def _correspond(d, c, mots, avec_tout=False):
    if not mots:
        return True
    champs = [nom_affiche(c), _nom_entreprise(d, c), c.get("email"), c.get("telephone")]
    if avec_tout:
        champs += [c.get("poste"), c.get("adresse"), c.get("site"), " ".join(c.get("etiquettes") or [])]
    texte = _sans_accents(" ".join(x for x in champs if x))
    tel = _chiffres(c.get("telephone"))
    return all(m in texte or (m.isdigit() and len(m) >= 3 and m in tel) for m in mots)


def lister(recherche=""):
    """Les contacts (format public), triés par nom, filtrés par la recherche
    (nom, entreprise, e-mail, téléphone ; sans tenir compte des accents)."""
    with _verrou:
        d = _lire()
    mots = _sans_accents(recherche).split()
    # Un numéro tapé autrement (« 0612 » pour « 06 12 ») : comparé chiffre à chiffre.
    chiffres = _chiffres(recherche) if RE_TELEPHONE.match(str(recherche or "").strip()) else ""
    choisis = [c for c in d["contacts"]
               if _correspond(d, c, mots) or (len(chiffres) >= 4 and chiffres in _chiffres(c.get("telephone")))]
    return [_resume(d, c) for c in sorted(choisis, key=_cle_tri)]


def _complet(d, c):
    r = dict(c)
    r["nom_affiche"] = nom_affiche(c)
    r["entreprise"] = _nom_entreprise(d, c)
    r["notes"] = sorted(c.get("notes") or [], key=lambda n: n.get("date", ""), reverse=True)
    if c.get("type") == "entreprise":
        r["membres"] = [{"id": p["id"], "nom": nom_affiche(p), "poste": p.get("poste", ""),
                         "email": p.get("email", ""), "telephone": p.get("telephone", "")}
                        for p in sorted(d["contacts"], key=_cle_tri)
                        if p.get("type") == "personne" and p.get("entreprise_id") == c["id"]]
    return r


def fiche(identifiant):
    """La fiche complète : coordonnées, notes (les plus récentes en tête),
    nom de l'entreprise, et pour une entreprise ses membres."""
    with _verrou:
        d = _lire()
        c = _trouver(d, identifiant)
        if c is None:
            raise ValueError("Contact introuvable.")
        return _complet(d, c)


def tout():
    """Pour la page : toutes les fiches, les étiquettes, les compteurs."""
    with _verrou:
        d = _lire()
    contacts = [_complet(d, c) for c in sorted(d["contacts"], key=_cle_tri)]
    etiquettes = sorted({e for c in d["contacts"] for e in c.get("etiquettes") or []}, key=_sans_accents)
    jour = aujourdhui().isoformat()
    compteurs = {s: 0 for s in STATUTS}
    for c in d["contacts"]:
        compteurs[c.get("statut", "autre")] = compteurs.get(c.get("statut", "autre"), 0) + 1
    compteurs["relancer"] = sum(1 for c in d["contacts"] if c.get("relance") and c["relance"] <= jour)
    return {"contacts": contacts, "etiquettes": etiquettes, "compteurs": compteurs, "aujourdhui": jour}


# ---------------------------------------------------------------------------
# Écriture
# ---------------------------------------------------------------------------
def _entreprise_par_nom(d, nom):
    cle = _sans_accents(_court(nom))
    return next((c for c in d["contacts"] if c.get("type") == "entreprise" and _sans_accents(c.get("nom")) == cle), None)


def _nouvelle_entreprise(d, nom, statut):
    a_l_heure = maintenant().strftime(FORMAT_NOTE)
    e = {"id": uuid.uuid4().hex[:12], "type": "entreprise", "prenom": "", "nom": _court(nom), "entreprise_id": "",
         "poste": "", "email": "", "telephone": "", "adresse": "", "site": "", "statut": statut,
         "etiquettes": [], "notes": [], "relance": "", "relance_motif": "", "cree": a_l_heure, "modifie": a_l_heure}
    d["contacts"].append(e)
    return e


def _valider(d, brut, existant=None):
    """Les champs propres d'une fiche (ValueError sinon)."""
    type_ = brut.get("type") or (existant or {}).get("type") or "personne"
    if type_ not in TYPES:
        raise ValueError("Type de contact inconnu.")
    propre = {"type": type_, "prenom": _court(brut.get("prenom")) if type_ == "personne" else "",
              "nom": _court(brut.get("nom")), "poste": _court(brut.get("poste")) if type_ == "personne" else "",
              "email": _email(brut.get("email")), "telephone": _telephone(brut.get("telephone")),
              "adresse": _adresse(brut.get("adresse")), "site": _site(brut.get("site")),
              "statut": _statut(brut.get("statut")), "etiquettes": _etiquettes(brut.get("etiquettes")),
              "relance": _date(brut.get("relance")), "relance_motif": _court(brut.get("relance_motif"), 200)}
    if not propre["nom"] and not propre["prenom"]:
        raise ValueError("Indiquez un nom.")
    if not propre["relance"]:
        propre["relance_motif"] = ""
    # Entreprise : par son identifiant, ou par son nom (créée si besoin).
    propre["entreprise_id"] = ""
    if type_ == "personne":
        ident = str(brut.get("entreprise_id") or "").strip()
        nom_e = _court(brut.get("entreprise"))
        if ident:
            e = _trouver(d, ident)
            if e is None or e.get("type") != "entreprise":
                raise ValueError("Entreprise introuvable.")
            propre["entreprise_id"] = ident
        elif nom_e:
            e = _entreprise_par_nom(d, nom_e) or _nouvelle_entreprise(d, nom_e, propre["statut"])
            propre["entreprise_id"] = e["id"]
    return propre


def enregistrer(brut):
    """Créer (sans id) ou modifier (avec id) une fiche. Renvoie la fiche complète."""
    if not isinstance(brut, dict):
        raise ValueError("Fiche invalide.")
    with _verrou:
        d = _lire()
        existant = _trouver(d, brut.get("id")) if brut.get("id") else None
        if brut.get("id") and existant is None:
            raise ValueError("Contact introuvable.")
        propre = _valider(d, brut, existant)
        if existant and propre["entreprise_id"] == existant["id"]:
            raise ValueError("Une fiche ne peut pas appartenir à elle-même.")
        a_l_heure = maintenant().strftime(FORMAT_NOTE)
        if existant is None:
            existant = {"id": uuid.uuid4().hex[:12], "notes": [], "cree": a_l_heure}
            d["contacts"].append(existant)
        else:
            if existant.get("type") == "entreprise" and propre["type"] == "personne":
                # Une entreprise devenue personne : ses membres sont détachés.
                for p in d["contacts"]:
                    if p.get("entreprise_id") == existant["id"]:
                        p["entreprise_id"] = ""
            if propre["relance"] != existant.get("relance"):
                existant.pop("relance_vue", None)
        existant.update(propre)
        existant["modifie"] = a_l_heure
        _ecrire(d)
        return _complet(d, existant)


def supprimer(identifiant):
    """Supprime une fiche et son historique. Les membres d'une entreprise
    supprimée restent, sans entreprise. Renvoie le nombre de fiches supprimées."""
    with _verrou:
        d = _lire()
        avant = len(d["contacts"])
        d["contacts"] = [c for c in d["contacts"] if c.get("id") != identifiant]
        if len(d["contacts"]) == avant:
            return 0
        for c in d["contacts"]:
            if c.get("entreprise_id") == identifiant:
                c["entreprise_id"] = ""
        _ecrire(d)
        return 1


def ajouter_note(identifiant, note):
    """Ajoute un échange à l'historique : {type, texte, date?}."""
    note = note if isinstance(note, dict) else {}
    type_ = note.get("type") or "note"
    if type_ not in TYPES_NOTES:
        raise ValueError("Type d'échange inconnu.")
    texte = str(note.get("texte") or "").strip()[:MAX_NOTE]
    if not texte:
        raise ValueError("Écrivez le contenu de la note.")
    quand = str(note.get("date") or "").strip()
    if quand:
        try:
            quand = datetime.datetime.strptime(quand[:16], FORMAT_NOTE).strftime(FORMAT_NOTE)
        except ValueError:
            raise ValueError("Date de la note invalide.") from None
    else:
        quand = maintenant().strftime(FORMAT_NOTE)
    with _verrou:
        d = _lire()
        c = _trouver(d, identifiant)
        if c is None:
            raise ValueError("Contact introuvable.")
        propre = {"id": uuid.uuid4().hex[:12], "type": type_, "date": quand, "texte": texte}
        c.setdefault("notes", []).append(propre)
        c["modifie"] = maintenant().strftime(FORMAT_NOTE)
        _ecrire(d)
        return _complet(d, c)


def supprimer_note(identifiant, note_id):
    with _verrou:
        d = _lire()
        c = _trouver(d, identifiant)
        if c is None:
            raise ValueError("Contact introuvable.")
        avant = len(c.get("notes") or [])
        c["notes"] = [n for n in c.get("notes") or [] if n.get("id") != note_id]
        if len(c["notes"]) == avant:
            raise ValueError("Note introuvable.")
        _ecrire(d)
        return _complet(d, c)


def relancer(identifiant, date="", motif=None):
    """Fixe la date de relance (« » : relance faite, plus de date)."""
    jour = _date(date)
    with _verrou:
        d = _lire()
        c = _trouver(d, identifiant)
        if c is None:
            raise ValueError("Contact introuvable.")
        if jour != c.get("relance"):
            c.pop("relance_vue", None)
        c["relance"] = jour
        if motif is not None:
            c["relance_motif"] = _court(motif, 200)
        if not jour:
            c["relance_motif"] = ""
        c["modifie"] = maintenant().strftime(FORMAT_NOTE)
        _ecrire(d)
        return _complet(d, c)


# ---------------------------------------------------------------------------
# Relances (Accueil et bulle)
# ---------------------------------------------------------------------------
def a_relancer(limite=None):
    """Les relances d'aujourd'hui ou en retard, les plus anciennes d'abord :
    [{id, nom, entreprise, relance, motif, retard (jours)}]."""
    jour = aujourdhui()
    with _verrou:
        d = _lire()
    dues = []
    for c in d["contacts"]:
        if c.get("relance") and c["relance"] <= jour.isoformat():
            retard = (jour - datetime.date.fromisoformat(c["relance"])).days
            dues.append({"id": c["id"], "nom": nom_affiche(c), "entreprise": _nom_entreprise(d, c),
                         "relance": c["relance"], "motif": c.get("relance_motif", ""), "retard": retard})
    dues.sort(key=lambda x: (x["relance"], _sans_accents(x["nom"])))
    return dues[:limite] if limite else dues


def _id_alerte(c):
    return f"{c['id']}:{c['relance']}"


def alertes_dues():
    """Les relances arrivées à échéance et pas encore montrées par la bulle :
    [{id, titre, detail}]."""
    jour = aujourdhui().isoformat()
    with _verrou:
        d = _lire()
    dues = []
    for c in sorted(d["contacts"], key=lambda c: c.get("relance") or ""):
        if c.get("relance") and c["relance"] <= jour and c.get("relance_vue") != c["relance"]:
            date_locale = datetime.date.fromisoformat(c["relance"])
            date_txt = date_locale.strftime("%d/%m/%Y") if config.langue() == "fr" else date_locale.strftime("%Y-%m-%d")
            dues.append({"id": _id_alerte(c), "titre": _texte("Relancer {nom}", nom=nom_affiche(c)),
                         "detail": c.get("relance_motif") or _texte("Relance prévue le {date}.", date=date_txt)})
    return dues


def marquer_alerte(identifiant):
    """Relance montrée par la bulle (elle ne revient plus pour cette date).
    Renvoie True si elle existait."""
    cid, _, jour = str(identifiant or "").partition(":")
    with _verrou:
        d = _lire()
        c = _trouver(d, cid)
        if c is None or not c.get("relance") or (jour and jour != c["relance"]):
            return False
        c["relance_vue"] = c["relance"]
        _ecrire(d)
        return True


# ---------------------------------------------------------------------------
# Export et import CSV (Excel en français : « ; », UTF-8 avec BOM)
# ---------------------------------------------------------------------------
_FORMULE = re.compile(r"^[=+@\t\r]|^-[^\s\-\d]")


def _cellule(valeur):
    """Un texte qu'Excel ne prendra pas pour une formule."""
    valeur = str(valeur or "")
    return "'" + valeur if _FORMULE.match(valeur) else valeur


def export_csv():
    """{nom, csv} : le texte commence par le BOM UTF-8 (\\ufeff)."""
    with _verrou:
        d = _lire()
    sortie = io.StringIO()
    ecrivain = csv.writer(sortie, delimiter=";", lineterminator="\r\n")
    ecrivain.writerow([_texte(lib) for _, lib in COLONNES])
    # Les entreprises d'abord : un nouvel import retrouve ainsi chaque entreprise.
    for c in sorted(d["contacts"], key=lambda c: (c.get("type") != "entreprise", _cle_tri(c))):
        notes = sorted(c.get("notes") or [], key=lambda n: n.get("date", ""))
        valeurs = {"type": _texte(LIBELLES_TYPES.get(c.get("type"), "Personne")),
                   "entreprise": _nom_entreprise(d, c),
                   "statut": _texte(LIBELLES_STATUTS.get(c.get("statut"), "Autre")),
                   "etiquettes": ", ".join(c.get("etiquettes") or []),
                   "dernier_echange": notes[-1]["date"][:10] if notes else ""}
        ecrivain.writerow([_cellule(valeurs[cle] if cle in valeurs else c.get(cle, "")) for cle, _ in COLONNES])
    return {"nom": f"contacts-{aujourdhui().isoformat()}.csv", "csv": "﻿" + sortie.getvalue()}


# En-têtes reconnus (français, anglais, exports courants), sans accents.
_ENTETES = {
    "type": "type", "genre": "type",
    "prenom": "prenom", "first name": "prenom", "firstname": "prenom", "given name": "prenom",
    "nom": "nom", "last name": "nom", "lastname": "nom", "surname": "nom", "family name": "nom",
    "name": "nom", "nom complet": "nom", "full name": "nom", "raison sociale": "nom",
    "entreprise": "entreprise", "societe": "entreprise", "company": "entreprise", "organisation": "entreprise",
    "organization": "entreprise", "company name": "entreprise",
    "poste": "poste", "fonction": "poste", "job title": "poste", "title": "poste", "position": "poste",
    "statut": "statut", "status": "statut",
    "e-mail": "email", "email": "email", "mail": "email", "courriel": "email", "adresse e-mail": "email",
    "adresse email": "email", "e-mail address": "email", "email address": "email",
    "telephone": "telephone", "tel": "telephone", "tel.": "telephone", "phone": "telephone", "mobile": "telephone",
    "portable": "telephone", "phone number": "telephone", "numero de telephone": "telephone",
    "adresse": "adresse", "address": "adresse",
    "site": "site", "site web": "site", "site internet": "site", "website": "site", "web": "site",
    "etiquettes": "etiquettes", "etiquette": "etiquettes", "tags": "etiquettes", "labels": "etiquettes",
    "relance": "relance", "relancer le": "relance", "follow-up": "relance", "follow up": "relance",
    "motif de relance": "relance_motif", "follow-up reason": "relance_motif",
    "note": "note", "notes": "note", "commentaire": "note", "commentaires": "note", "comment": "note",
}
_STATUTS_LUS = {
    "prospect": "prospect", "client": "client", "ancien client": "ancien", "ancien": "ancien",
    "former client": "ancien", "fournisseur": "fournisseur", "supplier": "fournisseur",
    "autre": "autre", "other": "autre", "customer": "client", "lead": "prospect",
}
_TYPES_LUS = {"personne": "personne", "person": "personne", "contact": "personne",
              "entreprise": "entreprise", "company": "entreprise", "societe": "entreprise", "organisation": "entreprise"}


def _sans_apostrophe(valeur):
    """Retire l'apostrophe ajoutée devant une formule par l'export."""
    valeur = str(valeur or "").strip()
    return valeur[1:] if valeur.startswith("'") and _FORMULE.match(valeur[1:]) else valeur


def _lire_csv(texte):
    texte = str(texte or "").lstrip("﻿")
    if not texte.strip():
        raise ValueError("Le fichier est vide.")
    if len(texte) > MAX_CSV:
        raise ValueError("Fichier trop gros (5 Mo au plus).")
    premiere = texte.split("\n", 1)[0]
    separateur = max((";", ",", "\t"), key=premiere.count)
    lignes = list(csv.reader(io.StringIO(texte), delimiter=separateur))
    entete = [_ENTETES.get(_sans_accents(x).strip()) for x in lignes[0]]
    if "nom" not in entete and "prenom" not in entete and "entreprise" not in entete:
        raise ValueError("Colonnes introuvables : il faut au moins « Nom » ou « Entreprise ».")
    for numero, valeurs in enumerate(lignes[1:], start=2):
        if not any(v.strip() for v in valeurs):
            continue
        ligne = {}
        for cle, v in zip(entete, valeurs):
            if cle and cle not in ligne:
                ligne[cle] = _sans_apostrophe(v)
        yield numero, ligne


def _doublon(d, propre):
    """La fiche existante qui correspond : même e-mail, sinon même nom (et même type)."""
    if propre["email"]:
        trouve = next((c for c in d["contacts"] if (c.get("email") or "").lower() == propre["email"].lower()), None)
        if trouve:
            return trouve
    cle = _sans_accents(nom_affiche(propre))
    return next((c for c in d["contacts"] if c.get("type") == propre["type"]
                 and _sans_accents(nom_affiche(c)) == cle
                 and (propre["type"] == "entreprise" or not propre["email"] or not c.get("email"))), None)


def importer_csv(texte):
    """Importe un fichier CSV (« ; » ou « , », en-têtes français ou anglais).
    Une fiche déjà présente (même e-mail, sinon même nom) est complétée :
    ses champs vides sont remplis, ses étiquettes ajoutées, rien n'est
    effacé. Renvoie {ajoutes, completes, ignores, erreurs: ["Ligne 3 : …"]}."""
    bilan = {"ajoutes": 0, "completes": 0, "ignores": 0, "erreurs": []}
    lignes = list(_lire_csv(texte))
    with _verrou:
        d = _lire()
        avant = len(d["contacts"])
        a_l_heure = maintenant().strftime(FORMAT_NOTE)
        for numero, ligne in lignes:
            try:
                type_ = _TYPES_LUS.get(_sans_accents(ligne.get("type")).strip())
                if type_ is None:
                    seule_entreprise = ligne.get("entreprise") and not ligne.get("nom") and not ligne.get("prenom")
                    type_ = "entreprise" if seule_entreprise else "personne"
                if type_ == "entreprise" and not ligne.get("nom"):
                    ligne["nom"], ligne["entreprise"] = ligne.get("entreprise", ""), ""
                statut = _STATUTS_LUS.get(_sans_accents(ligne.get("statut")).strip(), "prospect")
                brut = {**ligne, "type": type_, "statut": statut}
                # Ligne d'abord validée sans son entreprise : celle-ci n'est
                # créée que si le reste de la ligne est correct.
                propre = _valider(d, dict(brut, entreprise=""))
                if type_ == "personne" and ligne.get("entreprise"):
                    propre["entreprise_id"] = _valider(d, brut)["entreprise_id"]
            except ValueError as erreur:
                bilan["ignores"] += 1
                if len(bilan["erreurs"]) < MAX_ERREURS_IMPORT:
                    bilan["erreurs"].append(f"Ligne {numero} : {erreur}")
                continue
            note = str(ligne.get("note") or "").strip()[:MAX_NOTE]
            existant = _doublon(d, propre)
            if existant is None:
                c = {"id": uuid.uuid4().hex[:12], **propre, "notes": [], "cree": a_l_heure, "modifie": a_l_heure}
                if note:
                    c["notes"].append({"id": uuid.uuid4().hex[:12], "type": "note", "date": a_l_heure, "texte": note})
                d["contacts"].append(c)
                continue
            change = False
            for cle in ("prenom", "poste", "email", "telephone", "adresse", "site", "entreprise_id", "relance", "relance_motif"):
                if propre.get(cle) and not existant.get(cle):
                    existant[cle] = propre[cle]
                    change = True
            etiquettes = _etiquettes((existant.get("etiquettes") or []) + propre["etiquettes"])
            if etiquettes != (existant.get("etiquettes") or []):
                existant["etiquettes"] = etiquettes
                change = True
            if note and not any(n.get("texte") == note for n in existant.get("notes") or []):
                existant.setdefault("notes", []).append({"id": uuid.uuid4().hex[:12], "type": "note", "date": a_l_heure, "texte": note})
                change = True
            if change:
                existant["modifie"] = a_l_heure
                bilan["completes"] += 1
            else:
                bilan["ignores"] += 1
        # Ajoutées : les lignes nouvelles et les entreprises créées en chemin.
        bilan["ajoutes"] = len(d["contacts"]) - avant
        _ecrire(d)
    return bilan


# ---------------------------------------------------------------------------
# Routes de la page
# ---------------------------------------------------------------------------
def _limite(valeur):
    try:
        return max(1, min(int(valeur), 500)) if valeur else None
    except (TypeError, ValueError):
        return None


ROUTES = {
    "liste": lambda d: {"contacts": lister(d.get("recherche") or "")},
    "fiche": lambda d: fiche(d.get("id")),
    "tout": lambda d: tout(),
    "enregistrer": lambda d: enregistrer(d.get("contact")),
    "supprimer": lambda d: {"supprimes": supprimer(d.get("id"))},
    "note/ajouter": lambda d: ajouter_note(d.get("id"), d.get("note")),
    "note/supprimer": lambda d: supprimer_note(d.get("id"), d.get("note_id")),
    "relance": lambda d: relancer(d.get("id"), d.get("date") or "", d.get("motif")),
    "a_relancer": lambda d: {"relances": a_relancer(_limite(d.get("limite")))},
    "export": lambda d: export_csv(),
    "import": lambda d: importer_csv(d.get("csv")),
    "alertes": lambda d: {"alertes": alertes_dues()},
    "marquer_alerte": lambda d: {"ok": marquer_alerte(d.get("id"))},
}
