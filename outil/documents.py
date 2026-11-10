# -*- coding: utf-8 -*-
"""Application Documents : un classeur des documents importants (contrats,
devis signés, factures fournisseurs, attestations, pièces d'identité,
assurances…), rangés par client ou par projet.

- Chaque fiche pointe vers un fichier (ou un dossier) du PC : le fichier
  reste où il est. Option « Copier dans le classeur » : une copie va dans
  Documents\\Mes outils\\Classeur\\<client>\\ (l'original ne bouge pas).
- Retirer une fiche ne supprime jamais le fichier : seule la fiche disparaît.
- Un fichier déplacé ou supprimé est signalé « Introuvable » ; « Retrouver… »
  enregistre son nouvel emplacement.
- Date d'expiration facultative : la bulle prévient N jours avant
  (alertes_dues / marquer_alerte), 30 jours par défaut.

Données : donnees\\documents.json = {"fiches": [...], "alertes_vues": [...],
"dernier_dossier": "..."}. Dates ISO « YYYY-MM-DD ».
Routes POST /api/documents/<action>.
"""
import datetime
import os
import re
import shutil
import threading
import uuid

import config
import systeme

NOM = "documents"

# Types de documents : clé → libellé (traduit dans la page).
TYPES = {
    "contrat": "Contrat",
    "devis_signe": "Devis signé",
    "facture_fournisseur": "Facture fournisseur",
    "attestation": "Attestation",
    "piece_identite": "Pièce d'identité",
    "assurance": "Assurance",
    "autre": "Autre",
}
GENRES = ("fichier", "dossier")
RAPPEL_DEFAUT = 30
MAX_TITRE = 120
MAX_CLIENT = 80
MAX_NOTE = 2000
MAX_ETIQUETTES = 10
MAX_ETIQUETTE = 30
MAX_AJOUT = 200
# Une alerte n'est plus montrée quand l'expiration est passée depuis plus longtemps.
ALERTE_PERIMEE = datetime.timedelta(days=30)
# Caractères interdits dans un nom de dossier Windows.
INTERDITS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
NOMS_RESERVES = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}

_verrou = threading.RLock()

# Textes de la bulle (elle n'a pas le dictionnaire de la page).
_ANGLAIS = {
    "Document qui expire : {titre}": "Document expiring: {titre}",
    "Document expiré : {titre}": "Document expired: {titre}",
    "Expire aujourd'hui ({date}).": "Expires today ({date}).",
    "Expire demain ({date}).": "Expires tomorrow ({date}).",
    "Expire le {date}, dans {n} jours.": "Expires on {date}, in {n} days.",
    "A expiré le {date}.": "Expired on {date}.",
    "Non classé": "Unfiled",
}


def _texte(fr, **valeurs):
    texte = _ANGLAIS.get(fr, fr) if config.langue() == "en" else fr
    return texte.format(**valeurs) if valeurs else texte


def aujourdhui():
    """La date du jour (remplacée par une date fixe dans les tests)."""
    return datetime.date.today()


def _date_lisible(iso):
    d = datetime.date.fromisoformat(iso)
    return d.strftime("%d/%m/%Y") if config.langue() != "en" else d.strftime("%d %b %Y")


# ---------------------------------------------------------------------------
# Fichier de données
# ---------------------------------------------------------------------------
def _lire():
    d = config.lire_donnees(NOM, {})
    if not isinstance(d, dict):
        d = {}
    if not isinstance(d.get("fiches"), list):
        d["fiches"] = []
    if not isinstance(d.get("alertes_vues"), list):
        d["alertes_vues"] = []
    return d


def _ecrire(d):
    config.ecrire_donnees(NOM, d)


def _trouver(d, identifiant):
    for f in d["fiches"]:
        if f.get("id") == identifiant:
            return f
    raise ValueError("Document introuvable dans la liste.")


# ---------------------------------------------------------------------------
# Dossier du classeur (copies)
# ---------------------------------------------------------------------------
def dossier_documents():
    """Le vrai dossier « Documents » (Windows : il peut être dans OneDrive ;
    Linux : celui du bureau, XDG)."""
    return systeme.dossier_documents()


def dossier_classeur():
    """Documents\\Mes outils\\Classeur (créé à la première copie)."""
    return os.path.join(dossier_documents(), "Mes outils", "Classeur")


def nom_de_dossier(texte):
    """Un nom de dossier Windows sûr à partir d'un client ou d'un projet."""
    nom = INTERDITS.sub(" ", str(texte or ""))
    nom = re.sub(r"\s+", " ", nom).strip().strip(".").strip()[:60].strip()
    if not nom or nom.upper() in NOMS_RESERVES:
        nom = _texte("Non classé")
    return nom


def _dans(chemin, dossier):
    try:
        return os.path.commonpath([os.path.normcase(chemin), os.path.normcase(dossier)]) == os.path.normcase(dossier)
    except ValueError:  # disques différents
        return False


def _copier_dans_classeur(source, rubrique):
    """Copie un fichier dans Classeur\\<rubrique>\\ sans jamais écraser un
    fichier existant (« nom (2).pdf »). Renvoie le chemin de la copie."""
    racine = dossier_classeur()
    if _dans(source, racine):
        return source  # déjà rangé dans le classeur
    cible_dossier = os.path.join(racine, nom_de_dossier(rubrique))
    if not _dans(cible_dossier, racine):
        raise ValueError("Nom de client invalide pour le classeur.")
    os.makedirs(cible_dossier, exist_ok=True)
    base, ext = os.path.splitext(os.path.basename(source))
    cible = os.path.join(cible_dossier, base + ext)
    n = 2
    while os.path.exists(cible):
        cible = os.path.join(cible_dossier, f"{base} ({n}){ext}")
        n += 1
    shutil.copy2(source, cible)
    return cible


# ---------------------------------------------------------------------------
# Champs d'une fiche
# ---------------------------------------------------------------------------
def _court(valeur, maxi):
    return re.sub(r"\s+", " ", str(valeur or "")).strip()[:maxi]


def _date(valeur, nom):
    valeur = str(valeur or "").strip()
    if not valeur:
        return ""
    try:
        return datetime.date.fromisoformat(valeur[:10]).isoformat()
    except ValueError:
        raise ValueError(f"{nom} invalide.") from None


def _etiquettes(valeur):
    if isinstance(valeur, str):
        valeur = valeur.split(",")
    if not isinstance(valeur, list):
        return []
    propres, vues = [], set()
    for e in valeur:
        e = _court(e, MAX_ETIQUETTE).lstrip("#").strip()
        if e and e.lower() not in vues:
            vues.add(e.lower())
            propres.append(e)
    return propres[:MAX_ETIQUETTES]


def _rappel(valeur):
    try:
        n = int(valeur)
    except (TypeError, ValueError):
        return RAPPEL_DEFAUT
    return min(max(n, 0), 365)


def _champs(d, existant=None):
    """Les champs modifiables, vérifiés. « existant » : valeurs actuelles
    (seules les clés présentes dans d sont changées)."""
    f = dict(existant or {})
    if "titre" in d:
        f["titre"] = _court(d["titre"], MAX_TITRE)
    if "type" in d:
        if d["type"] not in TYPES:
            raise ValueError("Type de document inconnu.")
        f["type"] = d["type"]
    if "client" in d:
        f["client"] = _court(d["client"], MAX_CLIENT)
    if "contact_id" in d:
        f["contact_id"] = _court(d["contact_id"], 60) or None
    if "projet" in d:
        f["projet"] = _court(d["projet"], MAX_CLIENT)
    if "etiquettes" in d:
        f["etiquettes"] = _etiquettes(d["etiquettes"])
    if "date_document" in d:
        f["date_document"] = _date(d["date_document"], "Date du document")
    if "expiration" in d:
        f["expiration"] = _date(d["expiration"], "Date d'expiration")
    if "rappel_jours" in d:
        f["rappel_jours"] = _rappel(d["rappel_jours"])
    if "note" in d:
        f["note"] = str(d["note"] or "").strip()[:MAX_NOTE]
    if f.get("expiration") and f.get("date_document") and f["expiration"] < f["date_document"]:
        raise ValueError("L'expiration doit être après la date du document.")
    return f


def _chemin_valide(chemin, genre=None):
    """Un chemin absolu qui existe (fichier ou dossier). Renvoie (chemin, genre)."""
    chemin = str(chemin or "").strip().strip('"')
    if not chemin:
        raise ValueError("Aucun fichier choisi.")
    chemin = os.path.normpath(chemin)
    if not os.path.isabs(chemin):
        raise ValueError(f"Chemin invalide : {chemin}")
    if os.path.isfile(chemin):
        trouve = "fichier"
    elif os.path.isdir(chemin):
        trouve = "dossier"
    else:
        raise ValueError(f"Fichier introuvable : {chemin}")
    if genre and genre != trouve:
        raise ValueError("Choisissez un dossier." if genre == "dossier" else "Choisissez un fichier.")
    return chemin, trouve


def _existe(f):
    chemin = f.get("chemin") or ""
    return os.path.isdir(chemin) if f.get("genre") == "dossier" else os.path.isfile(chemin)


def _jours_restants(f):
    if not f.get("expiration"):
        return None
    try:
        return (datetime.date.fromisoformat(f["expiration"]) - aujourdhui()).days
    except ValueError:
        return None


def _vue(f):
    """La fiche pour la page, avec son état calculé."""
    chemin = f.get("chemin") or ""
    v = dict(f)
    v.setdefault("etiquettes", [])
    v.setdefault("rappel_jours", RAPPEL_DEFAUT)
    v["nom"] = os.path.basename(chemin) or chemin
    v["dossier_parent"] = os.path.dirname(chemin)
    v["existe"] = _existe(f)
    v["jours"] = _jours_restants(f)
    return v


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------
def lister(_d=None):
    with _verrou:
        d = _lire()
    fiches = [_vue(f) for f in d["fiches"]]
    clients = sorted({f["client"] for f in fiches if f.get("client")}, key=str.lower)
    projets = sorted({f["projet"] for f in fiches if f.get("projet")}, key=str.lower)
    etiquettes = sorted({e for f in fiches for e in f.get("etiquettes") or []}, key=str.lower)
    return {"fiches": fiches, "types": TYPES, "clients": clients, "projets": projets, "etiquettes": etiquettes,
            "classeur": dossier_classeur(), "dernier_dossier": d.get("dernier_dossier") or "",
            "aujourdhui": aujourdhui().isoformat(), "rappel_defaut": RAPPEL_DEFAUT}


def ajouter(d):
    """Ajoute un ou plusieurs fichiers (ou dossiers) choisis dans la fenêtre
    « Ouvrir » du système, avec les mêmes champs. d = {chemins, genre, copier, titre, type,
    client, projet, etiquettes, date_document, expiration, rappel_jours, note}.
    Le titre n'est repris que pour un seul fichier ; sinon, le nom du fichier."""
    chemins = d.get("chemins")
    if isinstance(chemins, str):
        chemins = [chemins]
    if not isinstance(chemins, list) or not chemins:
        raise ValueError("Aucun fichier choisi.")
    if len(chemins) > MAX_AJOUT:
        raise ValueError(f"Trop de fichiers d'un coup (maximum {MAX_AJOUT}).")
    genre = d.get("genre") if d.get("genre") in GENRES else None
    communs = _champs({k: v for k, v in d.items() if k not in ("titre", "chemins", "genre", "copier")},
                      {"type": "autre", "client": "", "contact_id": None, "projet": "", "etiquettes": [],
                       "date_document": "", "expiration": "", "rappel_jours": RAPPEL_DEFAUT, "note": ""})
    copier = bool(d.get("copier"))
    valides = [_chemin_valide(c, genre) for c in chemins]  # tout est vérifié avant d'écrire
    if copier and any(g == "dossier" for _, g in valides):
        raise ValueError("Seuls les fichiers peuvent être copiés dans le classeur.")
    with _verrou:
        donnees = _lire()
        connus = {os.path.normcase(f.get("chemin") or "") for f in donnees["fiches"]}
        ajoutes, deja = [], 0
        for chemin, g in valides:
            if copier:
                chemin = _copier_dans_classeur(chemin, communs["client"] or communs["projet"])
            if os.path.normcase(chemin) in connus:
                deja += 1
                continue
            connus.add(os.path.normcase(chemin))
            fiche = dict(communs)
            titre = _court(d.get("titre"), MAX_TITRE) if len(valides) == 1 else ""
            if g == "fichier":
                titre = titre or os.path.splitext(os.path.basename(chemin))[0]
                if not fiche["date_document"]:
                    fiche["date_document"] = datetime.date.fromtimestamp(os.path.getmtime(chemin)).isoformat()
            fiche.update(id=uuid.uuid4().hex[:12], chemin=chemin, genre=g,
                         titre=titre or os.path.basename(chemin.rstrip("\\/")) or chemin,
                         copie=copier and g == "fichier", ajoute=aujourdhui().isoformat())
            donnees["fiches"].append(fiche)
            ajoutes.append(fiche)
        if valides:
            donnees["dernier_dossier"] = os.path.dirname(valides[-1][0]) if valides[-1][1] == "fichier" else valides[-1][0]
        _ecrire(donnees)
    return {"ajoutes": [_vue(f) for f in ajoutes], "deja": deja}


def modifier(d):
    with _verrou:
        donnees = _lire()
        f = _trouver(donnees, d.get("id"))
        nouveau = _champs({k: v for k, v in d.items() if k not in ("id", "chemin", "genre", "copie", "ajoute")}, f)
        if not nouveau.get("titre"):
            raise ValueError("Indiquez un titre.")
        f.clear()
        f.update(nouveau)
        _ecrire(donnees)
        return _vue(f)


def retirer(d):
    """Retire la fiche de la liste. Le fichier n'est jamais supprimé."""
    with _verrou:
        donnees = _lire()
        f = _trouver(donnees, d.get("id"))
        donnees["fiches"].remove(f)
        _ecrire(donnees)
    return {"retire": f["id"], "chemin": f.get("chemin")}


def retrouver(d):
    """Nouvel emplacement d'un document déplacé (choisi dans la fenêtre « Ouvrir »)."""
    with _verrou:
        donnees = _lire()
        f = _trouver(donnees, d.get("id"))
        chemin, _ = _chemin_valide(d.get("chemin"), f.get("genre") or "fichier")
        autre = next((x for x in donnees["fiches"] if x is not f
                      and os.path.normcase(x.get("chemin") or "") == os.path.normcase(chemin)), None)
        if autre:
            raise ValueError(f"Ce fichier est déjà dans la liste : {autre.get('titre')}")
        f["chemin"] = chemin
        _ecrire(donnees)
        return _vue(f)


def _fiche_existante(identifiant):
    with _verrou:
        f = _trouver(_lire(), identifiant)
    if not _existe(f):
        raise ValueError("Introuvable : le fichier a été déplacé ou supprimé. Utilisez « Retrouver… ».")
    return f


def ouvrir(d):
    """Ouvre le fichier (ou le dossier) avec le programme habituel du système."""
    f = _fiche_existante(d.get("id"))
    systeme.ouvrir(f["chemin"])  # chemin enregistré dans les fiches
    return {"ok": True}


def ouvrir_dossier(d):
    """Ouvre le gestionnaire de fichiers (l'Explorateur sous Windows) sur le
    dossier du document, fichier sélectionné."""
    with _verrou:
        f = _trouver(_lire(), d.get("id"))
    chemin = f.get("chemin") or ""
    if f.get("genre") == "dossier" and os.path.isdir(chemin):
        systeme.ouvrir(chemin)
    elif os.path.isfile(chemin):
        # Le chemin vient des fiches et existe.
        systeme.montrer_dans_dossier(chemin)
    elif os.path.isdir(os.path.dirname(chemin)):
        systeme.ouvrir(os.path.dirname(chemin))
    else:
        raise ValueError("Introuvable : le dossier du document n'existe plus.")
    return {"ok": True}


# ---------------------------------------------------------------------------
# Fenêtre « Ouvrir » du système (choix de fichiers)
# ---------------------------------------------------------------------------
def choisir_fichiers(d):
    """Ouvre la fenêtre « Ouvrir » du système (plusieurs fichiers possibles).
    Renvoie {"chemins": [...]} (liste vide si annulé)."""
    depart = d.get("depart")
    if not depart:
        with _verrou:
            depart = _lire().get("dernier_dossier") or ""
    try:
        chemins = systeme.choisir_fichiers(str(d.get("titre") or "Choisir des documents")[:120], depart,
                                           multi=d.get("multi") is not False,
                                           filtre=str(d.get("filtre") or systeme.TOUS_LES_FICHIERS)[:200])
    except RuntimeError as erreur:  # Linux sans zenity ni kdialog
        raise ValueError(str(erreur)) from None
    return {"chemins": chemins}


# ---------------------------------------------------------------------------
# Pour la bulle : rappels avant expiration
# ---------------------------------------------------------------------------
def _id_alerte(f):
    # La date fait partie de l'identifiant : une nouvelle expiration réarme le rappel.
    return f"{f['id']}:{f['expiration']}"


def alertes_dues():
    """Les documents qui expirent bientôt (selon leur rappel, 30 jours par
    défaut) ou viennent d'expirer, pas encore vus : [{id, titre, detail}]."""
    with _verrou:
        d = _lire()
    vues = set(d["alertes_vues"])
    jour = aujourdhui()
    dues = []
    for f in d["fiches"]:
        n = _jours_restants(f)
        if n is None or _id_alerte(f) in vues:
            continue
        if n > _rappel(f.get("rappel_jours", RAPPEL_DEFAUT)) or jour - datetime.date.fromisoformat(f["expiration"]) > ALERTE_PERIMEE:
            continue
        date = _date_lisible(f["expiration"])
        if n < 0:
            titre, detail = _texte("Document expiré : {titre}", titre=f.get("titre", "")), _texte("A expiré le {date}.", date=date)
        else:
            titre = _texte("Document qui expire : {titre}", titre=f.get("titre", ""))
            detail = (_texte("Expire aujourd'hui ({date}).", date=date) if n == 0 else
                      _texte("Expire demain ({date}).", date=date) if n == 1 else
                      _texte("Expire le {date}, dans {n} jours.", date=date, n=n))
        dues.append({"id": _id_alerte(f), "titre": titre, "detail": detail})
    return dues


def marquer_alerte(identifiant):
    """Alerte vue. Renvoie True si elle correspond à un document."""
    with _verrou:
        d = _lire()
        actuelles = {_id_alerte(f) for f in d["fiches"] if f.get("expiration")}
        if identifiant not in actuelles:
            return False
        # Les alertes de documents retirés ou d'anciennes dates sont oubliées.
        d["alertes_vues"] = [a for a in d["alertes_vues"] if a in actuelles and a != identifiant] + [identifiant]
        _ecrire(d)
        return True


ROUTES = {
    "liste": lister,
    "ajouter": ajouter,
    "modifier": modifier,
    "retirer": retirer,
    "retrouver": retrouver,
    "ouvrir": ouvrir,
    "ouvrir_dossier": ouvrir_dossier,
    "choisir_fichiers": choisir_fichiers,
    "alertes": lambda d: {"alertes": alertes_dues()},
    "marquer_alerte": lambda d: {"ok": marquer_alerte(d.get("id"))},
}
