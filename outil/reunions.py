# -*- coding: utf-8 -*-
"""Application « Réunions et déplacements ».

Données dans donnees\\reunions.json :
    {"reunions": [...], "deplacements": [...], "alertes_vues": [...]}

Réunion :
    {id, titre, debut "YYYY-MM-DDTHH:MM", duree (minutes), lieu, lien,
     participants [{nom, email, contact_id}], ordre_du_jour [{texte, fait}],
     notes, decisions [texte], actions [{id, qui, quoi, echeance, tache_id}],
     agenda_ids {cle: id du rendez-vous}, cree, modifie}

Déplacement :
    {id, destination, depart "YYYY-MM-DD", retour "YYYY-MM-DD" | "",
     voyageurs [texte], etapes [{id, type, de, vers, depart, arrivee, numero,
     reference, note}], hebergements [{id, nom, adresse, arrivee, depart,
     reference}], documents [{chemin, nom}], controle [{texte, fait}],
     budget (nombre | None), devise, note, agenda_ids, cree, modifie}

Rappels par la bulle (alertes_dues / marquer_alerte) : 15 minutes avant une
réunion, et la veille d'un départ (à partir de 9 h).

L'ajout à l'agenda passe par la page : « agenda/elements » donne les
rendez-vous à enregistrer (POST /api/agenda/enregistrer), puis
« agenda/lier » garde leurs identifiants pour les mettre à jour ensuite.
"""
import datetime
import os
import re
import threading
import urllib.parse
import uuid

import config
import systeme

NOM = "reunions"
FORMAT_MINUTE = "%Y-%m-%dT%H:%M"
TYPES_ETAPES = ("avion", "train", "voiture", "autre")
RAPPEL_REUNION = datetime.timedelta(minutes=15)
HEURE_RAPPEL_VEILLE = 9
MAX_ALERTES_VUES = 300
MAX_MAILTO = 1900
# Fichiers que l'on ne lance jamais depuis la page (programmes, scripts).
EXTENSIONS_REFUSEES = {".exe", ".com", ".bat", ".cmd", ".ps1", ".psm1", ".vbs", ".vbe", ".js", ".jse", ".wsf",
                       ".wsh", ".msi", ".msp", ".scr", ".pif", ".hta", ".cpl", ".jar", ".reg", ".lnk", ".url"}
# Sous Linux, en plus : scripts, lanceurs (.desktop) et paquets, qu'un double
# clic peut démarrer.
EXTENSIONS_REFUSEES_LINUX = {".sh", ".bash", ".desktop", ".appimage", ".run", ".bin", ".deb", ".rpm", ".snap",
                             ".flatpakref"}
if not systeme.WINDOWS:
    EXTENSIONS_REFUSEES = EXTENSIONS_REFUSEES | EXTENSIONS_REFUSEES_LINUX
COULEUR_REUNION = "#2f8cff"
COULEUR_DEPLACEMENT = "#18b597"

_verrou = threading.RLock()

# ---------------------------------------------------------------------------
# Textes (compte rendu, feuille de route, rappels) : la langue des Réglages.
# ---------------------------------------------------------------------------
_ANGLAIS = {
    "Compte rendu : {titre}": "Minutes: {titre}",
    "Compte rendu : {titre} ({date})": "Minutes: {titre} ({date})",
    "Date : {valeur}": "Date: {valeur}",
    "Lieu : {valeur}": "Place: {valeur}",
    "Visio : {valeur}": "Video call: {valeur}",
    "Participants : {valeur}": "Attendees: {valeur}",
    "Ordre du jour": "Agenda",
    "Notes": "Notes",
    "Décisions": "Decisions",
    "Actions": "Action items",
    "pour le {date}": "due {date}",
    "Réunion : {titre}": "Meeting: {titre}",
    "Dans {n} min · {heure}": "In {n} min · {heure}",
    "Maintenant · {heure}": "Now · {heure}",
    "Départ demain : {destination}": "Leaving tomorrow: {destination}",
    "Départ aujourd'hui : {destination}": "Leaving today: {destination}",
    "{n} élément(s) à cocher dans la liste": "{n} item(s) left on the checklist",
    "Feuille de route : {destination}": "Itinerary: {destination}",
    "Du {debut} au {fin}": "From {debut} to {fin}",
    "Le {date}": "On {date}",
    "Voyageurs : {valeur}": "Travellers: {valeur}",
    "Départ pour {destination}": "Departure to {destination}",
    "Retour de {destination}": "Return from {destination}",
    "Déplacement : {destination}": "Trip: {destination}",
    "Retour : {destination}": "Return: {destination}",
    "Arrivée à l'hébergement : {nom}": "Check-in: {nom}",
    "Départ de l'hébergement : {nom}": "Check-out: {nom}",
    "Hébergement": "Accommodation",
    "arrivée {heure}": "arrives {heure}",
    "arrivée le {date} à {heure}": "arrives on {date} at {heure}",
    "n° {valeur}": "no. {valeur}",
    "réf. {valeur}": "ref. {valeur}",
    "Sans date": "No date",
    "Documents": "Documents",
    "Liste de contrôle": "Checklist",
    "Budget prévu : {valeur}": "Planned budget: {valeur}",
    "Note : {valeur}": "Note: {valeur}",
    "Avion": "Flight", "Train": "Train", "Voiture": "Car", "Trajet": "Journey",
    "Réunion": "Meeting",
    "{a} → {b}": "{a} → {b}",
}
LIBELLES_TYPES = {"avion": "Avion", "train": "Train", "voiture": "Voiture", "autre": "Trajet"}
JOURS = {"fr": ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"],
         "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
MOIS = {"fr": ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre",
               "octobre", "novembre", "décembre"],
        "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September",
               "October", "November", "December"]}


def _langue():
    try:
        return config.langue()
    except Exception:  # noqa: BLE001  (réglages illisibles : français)
        return "fr"


def _texte(fr, **valeurs):
    texte = _ANGLAIS.get(fr, fr) if _langue() == "en" else fr
    return texte.format(**valeurs) if valeurs else texte


def _date_longue(jour):
    """« mardi 10 novembre 2026 » / « Tuesday 10 November 2026 »."""
    langue = "en" if _langue() == "en" else "fr"
    return f"{JOURS[langue][jour.weekday()]} {jour.day} {MOIS[langue][jour.month - 1]} {jour.year}"


def _date_courte(jour):
    return jour.strftime("%d/%m/%Y")


def maintenant():
    """L'heure locale (remplacée par une horloge simulée dans les tests)."""
    return datetime.datetime.now().replace(second=0, microsecond=0)


def _nouvel_id():
    return uuid.uuid4().hex[:12]


# ---------------------------------------------------------------------------
# Fichier
# ---------------------------------------------------------------------------
def _lire():
    d = config.lire_donnees(NOM, {})
    if not isinstance(d, dict):
        d = {}
    for cle in ("reunions", "deplacements", "alertes_vues"):
        if not isinstance(d.get(cle), list):
            d[cle] = []
    return d


def _ecrire(d):
    config.ecrire_donnees(NOM, d)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def _txt(valeur, maxi, multiligne=False):
    texte = str(valeur if valeur is not None else "")
    if multiligne:
        texte = texte.replace("\r\n", "\n").strip()
    else:
        texte = " ".join(texte.split())
    return texte[:maxi]


def _minute(valeur, nom, obligatoire=True):
    texte = str(valeur or "").strip()
    if not texte:
        if obligatoire:
            raise ValueError(f"{nom} manquante.")
        return ""
    try:
        return datetime.datetime.strptime(texte[:16], FORMAT_MINUTE).strftime(FORMAT_MINUTE)
    except ValueError:
        raise ValueError(f"{nom} invalide.") from None


def _jour(valeur, nom, obligatoire=True):
    texte = str(valeur or "").strip()
    if not texte:
        if obligatoire:
            raise ValueError(f"{nom} manquante.")
        return ""
    try:
        return datetime.date.fromisoformat(texte[:10]).isoformat()
    except ValueError:
        raise ValueError(f"{nom} invalide.") from None


def _liste(valeur, maxi):
    return [x for x in valeur if x is not None][:maxi] if isinstance(valeur, list) else []


_EMAIL = re.compile(r"^[^@\s<>,;]+@[^@\s<>,;]+\.[^@\s<>,;]+$")


def _participant(p):
    if isinstance(p, str):
        p = {"nom": p}
    if not isinstance(p, dict):
        return None
    nom = _txt(p.get("nom"), 120)
    email = _txt(p.get("email"), 200)
    if email and not _EMAIL.match(email):
        raise ValueError(f"Adresse e-mail invalide : {email}")
    if not nom and not email:
        return None
    contact = p.get("contact_id")
    return {"nom": nom, "email": email, "contact_id": str(contact)[:60] if contact not in (None, "") else None}


def _points(valeur, maxi_texte=500):
    points = []
    for p in _liste(valeur, 100):
        if isinstance(p, str):
            p = {"texte": p}
        if not isinstance(p, dict):
            continue
        texte = _txt(p.get("texte"), maxi_texte)
        if texte:
            points.append({"texte": texte, "fait": bool(p.get("fait"))})
    return points


def _valider_reunion(r):
    if not isinstance(r, dict):
        raise ValueError("Réunion invalide.")
    titre = _txt(r.get("titre"), 200)
    if not titre:
        raise ValueError("Donnez un titre à la réunion.")
    try:
        duree = int(r.get("duree") if r.get("duree") not in (None, "") else 60)
    except (TypeError, ValueError):
        raise ValueError("Durée invalide.") from None
    if not 5 <= duree <= 24 * 60:
        raise ValueError("La durée doit être comprise entre 5 minutes et 24 heures.")
    lien = _txt(r.get("lien"), 500)
    if lien and not re.match(r"^https?://\S+$", lien, re.I):
        raise ValueError("Lien de visio invalide (il commence par https://).")
    participants = []
    for p in _liste(r.get("participants"), 100):
        propre = _participant(p)
        if propre:
            participants.append(propre)
    decisions = [_txt(x, 1000) for x in _liste(r.get("decisions"), 100)]
    actions = []
    for a in _liste(r.get("actions"), 100):
        if not isinstance(a, dict):
            continue
        qui, quoi = _txt(a.get("qui"), 120), _txt(a.get("quoi"), 500)
        if not qui and not quoi:
            continue
        tache = a.get("tache_id")
        actions.append({"id": _txt(a.get("id"), 40) or _nouvel_id(), "qui": qui, "quoi": quoi,
                        "echeance": _jour(a.get("echeance"), "Échéance", obligatoire=False),
                        "tache_id": str(tache)[:60] if tache not in (None, "") else None})
    return {
        "titre": titre,
        "debut": _minute(r.get("debut"), "Date de la réunion"),
        "duree": duree,
        "lieu": _txt(r.get("lieu"), 300),
        "lien": lien,
        "participants": participants,
        "ordre_du_jour": _points(r.get("ordre_du_jour")),
        "notes": _txt(r.get("notes"), 20000, multiligne=True),
        "decisions": [x for x in decisions if x],
        "actions": actions,
    }


def _chemin_document(chemin):
    chemin = str(chemin or "").strip().strip('"')
    if not chemin:
        return ""
    chemin = os.path.normpath(chemin)
    if os.path.splitext(chemin)[1].lower() in EXTENSIONS_REFUSEES:
        raise ValueError(f"Ce type de fichier ne peut pas être joint : {os.path.basename(chemin)}")
    return chemin[:1000]


def _valider_deplacement(dep):
    if not isinstance(dep, dict):
        raise ValueError("Déplacement invalide.")
    destination = _txt(dep.get("destination"), 200)
    if not destination:
        raise ValueError("Indiquez la destination.")
    depart = _jour(dep.get("depart"), "Date de départ")
    retour = _jour(dep.get("retour"), "Date de retour", obligatoire=False)
    if retour and retour < depart:
        raise ValueError("Le retour doit être après le départ.")
    etapes = []
    for e in _liste(dep.get("etapes"), 50):
        if not isinstance(e, dict):
            continue
        type_ = e.get("type") if e.get("type") in TYPES_ETAPES else "autre"
        propre = {"id": _txt(e.get("id"), 40) or _nouvel_id(), "type": type_,
                  "de": _txt(e.get("de"), 120), "vers": _txt(e.get("vers"), 120),
                  "depart": _minute(e.get("depart"), "Heure de départ", obligatoire=False),
                  "arrivee": _minute(e.get("arrivee"), "Heure d'arrivée", obligatoire=False),
                  "numero": _txt(e.get("numero"), 60), "reference": _txt(e.get("reference"), 60),
                  "note": _txt(e.get("note"), 300)}
        if propre["depart"] and propre["arrivee"] and propre["arrivee"] < propre["depart"]:
            raise ValueError("Une arrivée est avant son départ.")
        etapes.append(propre)
    hebergements = []
    for h in _liste(dep.get("hebergements"), 20):
        if not isinstance(h, dict):
            continue
        propre = {"id": _txt(h.get("id"), 40) or _nouvel_id(), "nom": _txt(h.get("nom"), 200),
                  "adresse": _txt(h.get("adresse"), 300),
                  "arrivee": _jour(h.get("arrivee"), "Date d'arrivée", obligatoire=False),
                  "depart": _jour(h.get("depart"), "Date de départ", obligatoire=False),
                  "reference": _txt(h.get("reference"), 60)}
        if not propre["nom"] and not propre["adresse"]:
            continue
        if propre["arrivee"] and propre["depart"] and propre["depart"] < propre["arrivee"]:
            raise ValueError("Hébergement : le départ doit être après l'arrivée.")
        hebergements.append(propre)
    documents, vus = [], set()
    for doc in _liste(dep.get("documents"), 50):
        chemin = _chemin_document(doc.get("chemin") if isinstance(doc, dict) else doc)
        if chemin and chemin.lower() not in vus:
            vus.add(chemin.lower())
            documents.append({"chemin": chemin, "nom": os.path.basename(chemin) or chemin})
    budget = dep.get("budget")
    if budget in (None, ""):
        budget = None
    else:
        try:
            budget = round(float(str(budget).replace(",", ".").replace(" ", "")), 2)
        except ValueError:
            raise ValueError("Budget invalide.") from None
        if budget < 0 or budget != budget or budget > 1e9:
            raise ValueError("Budget invalide.")
    return {
        "destination": destination, "depart": depart, "retour": retour,
        "voyageurs": [v for v in (_txt(x, 120) for x in _liste(dep.get("voyageurs"), 50)) if v],
        "etapes": etapes, "hebergements": hebergements, "documents": documents,
        "controle": _points(dep.get("controle"), 200),
        "budget": budget, "devise": _txt(dep.get("devise"), 10) or "EUR",
        "note": _txt(dep.get("note"), 5000, multiligne=True),
    }


# ---------------------------------------------------------------------------
# Enregistrer, supprimer
# ---------------------------------------------------------------------------
def _enregistrer(cle, element, propre):
    with _verrou:
        d = _lire()
        horodatage = maintenant().strftime(FORMAT_MINUTE)
        identifiant = (element or {}).get("id")
        if identifiant:
            existant = next((x for x in d[cle] if x.get("id") == identifiant), None)
            if existant is None:
                raise ValueError("Élément introuvable (supprimé entre-temps ?).")
            existant.update(propre)
            existant["modifie"] = horodatage
            resultat = existant
        else:
            resultat = {"id": _nouvel_id(), **propre, "agenda_ids": {}, "cree": horodatage, "modifie": horodatage}
            d[cle].append(resultat)
        _ecrire(d)
        return dict(resultat)


def enregistrer_reunion(reunion):
    """Créer ou mettre à jour une réunion. Renvoie la réunion enregistrée."""
    return _avec_fin(_enregistrer("reunions", reunion, _valider_reunion(reunion)))


def enregistrer_deplacement(deplacement):
    return _enregistrer("deplacements", deplacement, _valider_deplacement(deplacement))


def _supprimer(cle, identifiant):
    with _verrou:
        d = _lire()
        avant = len(d[cle])
        d[cle] = [x for x in d[cle] if x.get("id") != identifiant]
        if len(d[cle]) != avant:
            _ecrire(d)
        return avant - len(d[cle])


def _trouver(cle, identifiant):
    with _verrou:
        element = next((x for x in _lire()[cle] if x.get("id") == identifiant), None)
    if element is None:
        raise ValueError("Réunion introuvable." if cle == "reunions" else "Déplacement introuvable.")
    return element


def _debut(r):
    return datetime.datetime.strptime(r["debut"], FORMAT_MINUTE)


def _fin(r):
    return _debut(r) + datetime.timedelta(minutes=int(r.get("duree") or 60))


def _avec_fin(r):
    r = dict(r)
    r["fin"] = _fin(r).strftime(FORMAT_MINUTE)
    return r


def liste():
    """Toutes les réunions (les plus proches en tête) et tous les déplacements."""
    with _verrou:
        d = _lire()
    reunions = sorted((_avec_fin(r) for r in d["reunions"]), key=lambda r: r["debut"])
    deplacements = sorted(d["deplacements"], key=lambda x: x["depart"])
    return {"reunions": reunions, "deplacements": deplacements,
            "maintenant": maintenant().strftime(FORMAT_MINUTE)}


# ---------------------------------------------------------------------------
# Compte rendu
# ---------------------------------------------------------------------------
def _nom_participant(p):
    return p.get("nom") or p.get("email") or ""


def compte_rendu(identifiant):
    """{sujet, texte, destinataires, mailto, tronque} : un texte propre à
    copier ou à envoyer aux participants."""
    r = _trouver("reunions", identifiant)
    debut, fin = _debut(r), _fin(r)
    quand = f"{_date_longue(debut.date())}, {debut:%H:%M} – {fin:%H:%M}"
    lignes = [_texte("Compte rendu : {titre}", titre=r["titre"]), "",
              _texte("Date : {valeur}", valeur=quand)]
    if r.get("lieu"):
        lignes.append(_texte("Lieu : {valeur}", valeur=r["lieu"]))
    if r.get("lien"):
        lignes.append(_texte("Visio : {valeur}", valeur=r["lien"]))
    noms = [_nom_participant(p) for p in r.get("participants") or []]
    if noms:
        lignes.append(_texte("Participants : {valeur}", valeur=", ".join(noms)))

    def section(titre, elements):
        if elements:
            lignes.extend(["", titre, *elements])

    section(_texte("Ordre du jour"), [f"- {p['texte']}" for p in r.get("ordre_du_jour") or []])
    if r.get("notes"):
        lignes.extend(["", _texte("Notes"), r["notes"]])
    section(_texte("Décisions"), [f"- {x}" for x in r.get("decisions") or []])
    actions = []
    for a in r.get("actions") or []:
        deux_points = ":" if _langue() == "en" else " :"
        if a.get("qui") and a.get("quoi"):
            texte = f"- {a['qui']}{deux_points} {a['quoi']}"
        else:
            texte = f"- {a.get('quoi') or a.get('qui')}"
        if a.get("echeance"):
            texte += f" ({_texte('pour le {date}', date=_date_courte(datetime.date.fromisoformat(a['echeance'])))})"
        actions.append(texte)
    section(_texte("Actions"), actions)
    texte = "\n".join(lignes).strip() + "\n"
    sujet = _texte("Compte rendu : {titre} ({date})", titre=r["titre"], date=_date_courte(debut.date()))
    destinataires = [p["email"] for p in r.get("participants") or [] if p.get("email")]
    mailto, tronque = _mailto(destinataires, sujet, texte)
    return {"sujet": sujet, "texte": texte, "destinataires": destinataires, "mailto": mailto, "tronque": tronque}


def _mailto(destinataires, sujet, texte):
    """Lien mailto: (raccourci si trop long pour Windows : le texte entier est
    alors à coller depuis le presse-papiers)."""
    debut = "mailto:" + ",".join(urllib.parse.quote(a, safe="@") for a in destinataires) + \
        "?subject=" + urllib.parse.quote(sujet, safe="")
    corps = texte.replace("\n", "\r\n")
    lien = debut + "&body=" + urllib.parse.quote(corps, safe="")
    if len(lien) <= MAX_MAILTO:
        return lien, False
    while corps and len(debut + "&body=" + urllib.parse.quote(corps + "\r\n[…]", safe="")) > MAX_MAILTO:
        corps = corps[:max(0, len(corps) - max(20, len(corps) // 10))]
    return debut + "&body=" + urllib.parse.quote(corps.rstrip() + "\r\n[…]", safe=""), True


# ---------------------------------------------------------------------------
# Feuille de route d'un déplacement
# ---------------------------------------------------------------------------
def _titre_etape(e):
    titre = _texte(LIBELLES_TYPES.get(e["type"], "Trajet"))
    if e.get("de") and e.get("vers"):
        titre += " " + _texte("{a} → {b}", a=e["de"], b=e["vers"])
    elif e.get("de") or e.get("vers"):
        titre += " " + (e.get("de") or e.get("vers"))
    return titre


def _detail_etape(e):
    morceaux = []
    if e.get("arrivee"):
        arrivee = datetime.datetime.strptime(e["arrivee"], FORMAT_MINUTE)
        if e.get("depart") and e["depart"][:10] != e["arrivee"][:10]:
            morceaux.append(_texte("arrivée le {date} à {heure}", date=_date_courte(arrivee.date()),
                                   heure=arrivee.strftime("%H:%M")))
        else:
            morceaux.append(_texte("arrivée {heure}", heure=arrivee.strftime("%H:%M")))
    if e.get("numero"):
        morceaux.append(_texte("n° {valeur}", valeur=e["numero"]))
    if e.get("reference"):
        morceaux.append(_texte("réf. {valeur}", valeur=e["reference"]))
    if e.get("note"):
        morceaux.append(e["note"])
    return " · ".join(morceaux)


def _budget(dep):
    if dep.get("budget") is None:
        return ""
    montant = f"{dep['budget']:,.2f}".replace(",", " ")
    montant = montant.replace(".", ",") if _langue() != "en" else montant.replace(" ", ",")
    return f"{montant} {dep.get('devise') or 'EUR'}"


def chronologie(dep):
    """Les événements du déplacement rangés par jour :
    [{date, libelle, evenements: [{heure, type, titre, detail}]}]."""
    par_jour = {}

    def ajouter(jour, heure, type_, titre, detail="", rang=1):
        # rang : 0 = avant les trajets de la journée (départ de l'hôtel),
        # 2 = après (arrivée à l'hôtel) ; les trajets sont rangés par heure.
        par_jour.setdefault(jour or "", []).append({"heure": heure, "type": type_, "titre": titre,
                                                    "detail": detail, "_rang": rang})

    for e in dep.get("etapes") or []:
        jour = e["depart"][:10] if e.get("depart") else ""
        ajouter(jour, e["depart"][11:16] if e.get("depart") else "", e["type"], _titre_etape(e), _detail_etape(e))
    for h in dep.get("hebergements") or []:
        nom = h.get("nom") or h.get("adresse")
        details = " · ".join(x for x in (h.get("adresse") if h.get("nom") else "",
                                         _texte("réf. {valeur}", valeur=h["reference"]) if h.get("reference") else "") if x)
        ajouter(h.get("arrivee") or dep["depart"], "", "hotel", _texte("Arrivée à l'hébergement : {nom}", nom=nom),
                details, rang=2)
        fin = h.get("depart") or dep.get("retour")
        if fin:
            ajouter(fin, "", "hotel", _texte("Départ de l'hébergement : {nom}", nom=nom), rang=0)
    if dep["depart"] not in par_jour:
        ajouter(dep["depart"], "", "depart", _texte("Départ pour {destination}", destination=dep["destination"]), rang=0)
    if dep.get("retour") and dep["retour"] != dep["depart"] and dep["retour"] not in par_jour:
        ajouter(dep["retour"], "", "retour", _texte("Retour de {destination}", destination=dep["destination"]), rang=2)
    jours = []
    for jour in sorted(par_jour, key=lambda j: (j == "", j)):
        evenements = sorted(par_jour[jour], key=lambda x: (x["_rang"] if not x["heure"] else 1, x["heure"]))
        for x in evenements:
            del x["_rang"]
        libelle = _date_longue(datetime.date.fromisoformat(jour)) if jour else _texte("Sans date")
        jours.append({"date": jour, "libelle": libelle, "evenements": evenements})
    return jours


def feuille_de_route(identifiant):
    """{titre, jours, texte} : la feuille de route lisible, à copier ou imprimer."""
    dep = _trouver("deplacements", identifiant)
    jours = chronologie(dep)
    debut = datetime.date.fromisoformat(dep["depart"])
    titre = _texte("Feuille de route : {destination}", destination=dep["destination"])
    lignes = [titre]
    if dep.get("retour") and dep["retour"] != dep["depart"]:
        periode = _texte("Du {debut} au {fin}", debut=_date_courte(debut),
                         fin=_date_courte(datetime.date.fromisoformat(dep["retour"])))
    else:
        periode = _texte("Le {date}", date=_date_courte(debut))
    if dep.get("voyageurs"):
        periode += " · " + _texte("Voyageurs : {valeur}", valeur=", ".join(dep["voyageurs"]))
    lignes.append(periode)
    for j in jours:
        lignes.extend(["", j["libelle"][:1].upper() + j["libelle"][1:]])
        for e in j["evenements"]:
            ligne = f"  {e['heure'] or '     '}  {e['titre']}"
            if e.get("detail"):
                ligne += f" · {e['detail']}"
            lignes.append(ligne)
    if dep.get("documents"):
        lignes.extend(["", _texte("Documents"), *[f"- {doc['nom']}" for doc in dep["documents"]]])
    if dep.get("controle"):
        lignes.extend(["", _texte("Liste de contrôle"),
                       *[f"[{'x' if p['fait'] else ' '}] {p['texte']}" for p in dep["controle"]]])
    if dep.get("budget") is not None:
        lignes.extend(["", _texte("Budget prévu : {valeur}", valeur=_budget(dep))])
    if dep.get("note"):
        lignes.extend(["", _texte("Note : {valeur}", valeur=dep["note"])])
    return {"titre": titre, "periode": periode, "jours": jours, "texte": "\n".join(lignes) + "\n",
            "budget": _budget(dep)}


# ---------------------------------------------------------------------------
# Documents liés
# ---------------------------------------------------------------------------
def choisir_fichiers(titre=""):
    """La fenêtre « Ouvrir » du système (plusieurs fichiers possibles).
    Renvoie {"chemins": [...]} (liste vide si annulé)."""
    try:
        chemins = systeme.choisir_fichiers(str(titre or "Choisir des fichiers")[:120], "", multi=True)
    except RuntimeError as erreur:  # Linux sans zenity ni kdialog
        raise ValueError(str(erreur)) from None
    return {"chemins": [c for c in chemins if os.path.isfile(c)]}


def _document_du_deplacement(identifiant, chemin):
    """Seuls les documents déjà liés au déplacement peuvent être ouverts."""
    dep = _trouver("deplacements", identifiant)
    chemin = os.path.normpath(str(chemin or ""))
    if not any(os.path.normcase(doc["chemin"]) == os.path.normcase(chemin) for doc in dep.get("documents") or []):
        raise ValueError("Ce document n'est pas lié à ce déplacement.")
    if os.path.splitext(chemin)[1].lower() in EXTENSIONS_REFUSEES:
        raise ValueError(f"Ce type de fichier ne peut pas être joint : {os.path.basename(chemin)}")
    if not os.path.exists(chemin):
        raise ValueError(f"Fichier introuvable : {chemin}")
    return chemin


def ouvrir_document(identifiant, chemin):
    chemin = _document_du_deplacement(identifiant, chemin)
    systeme.ouvrir(chemin)  # chemin vérifié ci-dessus
    return {"ok": True}


def montrer_document(identifiant, chemin):
    """Ouvre le gestionnaire de fichiers (l'Explorateur sous Windows) sur le
    document, sélectionné (ou dans le dossier)."""
    chemin = _document_du_deplacement(identifiant, chemin)
    if os.path.isdir(chemin):
        systeme.ouvrir(chemin)
    else:
        systeme.montrer_dans_dossier(chemin)
    return {"ok": True}


# ---------------------------------------------------------------------------
# Agenda (rendez-vous enregistrés par la page via /api/agenda/enregistrer)
# ---------------------------------------------------------------------------
def elements_agenda(genre, identifiant):
    """{elements: [{cle, element}], obsoletes: [id]} : les rendez-vous à
    enregistrer dans l'agenda (avec l'id déjà connu pour une mise à jour) et
    ceux qui n'ont plus lieu d'être (étape supprimée…). Pas de rappel de
    l'agenda : cette application prévient déjà par la bulle."""
    if genre == "reunion":
        r = _trouver("reunions", identifiant)
        notes = []
        if r.get("participants"):
            notes.append(_texte("Participants : {valeur}", valeur=", ".join(_nom_participant(p) for p in r["participants"])))
        if r.get("ordre_du_jour"):
            notes.extend(["", _texte("Ordre du jour"), *[f"- {p['texte']}" for p in r["ordre_du_jour"]]])
        if r.get("lien"):
            notes.extend(["", r["lien"]])
        voulus = {"reunion": {"titre": r["titre"], "debut": r["debut"], "fin": _fin(r).strftime(FORMAT_MINUTE),
                              "journee": False, "couleur": COULEUR_REUNION, "rappel_minutes": None,
                              "lieu": r.get("lieu") or ("Visio" if r.get("lien") else ""),
                              "notes": "\n".join(notes).strip()}}
    elif genre == "deplacement":
        r = _trouver("deplacements", identifiant)
        resume = feuille_de_route(identifiant)["texte"]
        voulus = {"aller": {"titre": _texte("Déplacement : {destination}", destination=r["destination"]),
                            "debut": r["depart"] + "T08:00", "fin": r["depart"] + "T09:00", "journee": True,
                            "couleur": COULEUR_DEPLACEMENT, "rappel_minutes": None, "lieu": r["destination"],
                            "notes": resume[:4000]}}
        if r.get("retour") and r["retour"] != r["depart"]:
            voulus["retour"] = {"titre": _texte("Retour : {destination}", destination=r["destination"]),
                                "debut": r["retour"] + "T08:00", "fin": r["retour"] + "T09:00", "journee": True,
                                "couleur": COULEUR_DEPLACEMENT, "rappel_minutes": None, "lieu": r["destination"],
                                "notes": ""}
        for e in r.get("etapes") or []:
            if not e.get("depart"):
                continue
            debut = datetime.datetime.strptime(e["depart"], FORMAT_MINUTE)
            fin = datetime.datetime.strptime(e["arrivee"], FORMAT_MINUTE) if e.get("arrivee") else \
                debut + datetime.timedelta(hours=1)
            # Le rendez-vous reste dans sa journée (affichage de l'agenda).
            fin = min(fin, debut.replace(hour=23, minute=59))
            if fin <= debut:
                fin = debut + datetime.timedelta(minutes=1)
            voulus["etape:" + e["id"]] = {"titre": _titre_etape(e), "debut": e["depart"],
                                          "fin": fin.strftime(FORMAT_MINUTE), "journee": False,
                                          "couleur": COULEUR_DEPLACEMENT, "rappel_minutes": None,
                                          "lieu": e.get("de") or "", "notes": _detail_etape(e)}
    else:
        raise ValueError("Genre inconnu.")
    connus = r.get("agenda_ids") or {}
    elements = []
    for cle, element in voulus.items():
        if connus.get(cle):
            element = {"id": connus[cle], **element}
        elements.append({"cle": cle, "element": element})
    obsoletes = [v for k, v in connus.items() if k not in voulus and v]
    return {"elements": elements, "obsoletes": obsoletes}


def lier_agenda(genre, identifiant, ids):
    """Garde les identifiants des rendez-vous créés dans l'agenda."""
    cle = {"reunion": "reunions", "deplacement": "deplacements"}.get(genre)
    if not cle:
        raise ValueError("Genre inconnu.")
    if not isinstance(ids, dict):
        raise ValueError("Identifiants invalides.")
    propres = {str(k)[:60]: str(v)[:60] for k, v in ids.items() if v}
    with _verrou:
        d = _lire()
        element = next((x for x in d[cle] if x.get("id") == identifiant), None)
        if element is None:
            raise ValueError("Réunion introuvable." if cle == "reunions" else "Déplacement introuvable.")
        element["agenda_ids"] = propres
        _ecrire(d)
        return {"agenda_ids": propres}


# ---------------------------------------------------------------------------
# Accueil et rappels de la bulle
# ---------------------------------------------------------------------------
def prochains(jours=7):
    """La prochaine réunion et le prochain départ (ou déplacement en cours)
    dans les « jours » à venir : {reunion, deplacement} (None si rien)."""
    a_l_heure = maintenant()
    limite = a_l_heure + datetime.timedelta(days=jours)
    with _verrou:
        d = _lire()
    reunions = sorted((r for r in d["reunions"] if _fin(r) > a_l_heure and _debut(r) <= limite),
                      key=lambda r: r["debut"])
    aujourdhui = a_l_heure.date().isoformat()
    deplacements = sorted((x for x in d["deplacements"]
                           if (x.get("retour") or x["depart"]) >= aujourdhui and x["depart"] <= limite.date().isoformat()),
                          key=lambda x: x["depart"])
    return {"reunion": _avec_fin(reunions[0]) if reunions else None,
            "deplacement": deplacements[0] if deplacements else None,
            "maintenant": a_l_heure.strftime(FORMAT_MINUTE)}


def _premier_transport(dep):
    etapes = sorted((e for e in dep.get("etapes") or [] if e.get("depart")), key=lambda e: e["depart"])
    return etapes[0] if etapes else None


def alertes_dues():
    """Les rappels à montrer : [{id, titre, detail}].
    - réunion : dans les 15 minutes avant son début (jusqu'à son début) ;
    - déplacement : la veille du départ à partir de 9 h, jusqu'au départ."""
    a_l_heure = maintenant()
    with _verrou:
        d = _lire()
    vues = set(d["alertes_vues"])
    dues = []
    for r in d["reunions"]:
        try:
            debut = _debut(r)
        except (KeyError, ValueError):
            continue
        ident = f"reunion:{r['id']}:{r['debut']}"
        if ident in vues or not debut - RAPPEL_REUNION <= a_l_heure <= debut:
            continue
        minutes = int((debut - a_l_heure).total_seconds() // 60)
        quand = _texte("Dans {n} min · {heure}", n=minutes, heure=debut.strftime("%H:%M")) if minutes > 0 \
            else _texte("Maintenant · {heure}", heure=debut.strftime("%H:%M"))
        lieu = r.get("lieu") or ("Visio" if r.get("lien") else "")
        dues.append({"id": ident, "titre": _texte("Réunion : {titre}", titre=r["titre"]),
                     "detail": quand + (f" · {lieu}" if lieu else "")})
    for dep in d["deplacements"]:
        try:
            jour = datetime.date.fromisoformat(dep["depart"])
        except (KeyError, ValueError):
            continue
        ident = f"depart:{dep['id']}:{dep['depart']}"
        premier = _premier_transport(dep)
        if premier and premier["depart"][:10] == dep["depart"]:
            limite = datetime.datetime.strptime(premier["depart"], FORMAT_MINUTE)
        else:
            limite = datetime.datetime.combine(jour, datetime.time(23, 59))
        veille = datetime.datetime.combine(jour - datetime.timedelta(days=1), datetime.time(HEURE_RAPPEL_VEILLE))
        if ident in vues or not veille <= a_l_heure <= limite:
            continue
        cle = "Départ aujourd'hui : {destination}" if a_l_heure.date() == jour else "Départ demain : {destination}"
        morceaux = []
        if premier:
            morceaux.append(f"{premier['depart'][11:16]} {_titre_etape(premier)}")
            if premier.get("reference"):
                morceaux.append(_texte("réf. {valeur}", valeur=premier["reference"]))
        restants = sum(1 for p in dep.get("controle") or [] if not p.get("fait"))
        if restants:
            morceaux.append(_texte("{n} élément(s) à cocher dans la liste", n=restants))
        dues.append({"id": ident, "titre": _texte(cle, destination=dep["destination"]),
                     "detail": " · ".join(morceaux)})
    return dues


def marquer_alerte(identifiant):
    """Rappel vu (il ne revient plus). Renvoie True."""
    identifiant = str(identifiant or "")[:200]
    if not identifiant:
        return False
    with _verrou:
        d = _lire()
        if identifiant not in d["alertes_vues"]:
            d["alertes_vues"] = (d["alertes_vues"] + [identifiant])[-MAX_ALERTES_VUES:]
            _ecrire(d)
        return True


# ---------------------------------------------------------------------------
# Routes de la page
# ---------------------------------------------------------------------------
ROUTES = {
    "liste": lambda d: liste(),
    "accueil": lambda d: prochains(),
    "reunion/enregistrer": lambda d: enregistrer_reunion(d.get("reunion")),
    "reunion/supprimer": lambda d: {"supprimes": _supprimer("reunions", d.get("id"))},
    "reunion/compte_rendu": lambda d: compte_rendu(d.get("id")),
    "deplacement/enregistrer": lambda d: enregistrer_deplacement(d.get("deplacement")),
    "deplacement/supprimer": lambda d: {"supprimes": _supprimer("deplacements", d.get("id"))},
    "deplacement/feuille_de_route": lambda d: feuille_de_route(d.get("id")),
    "document/choisir": lambda d: choisir_fichiers(d.get("titre")),
    "document/ouvrir": lambda d: ouvrir_document(d.get("id"), d.get("chemin")),
    "document/montrer": lambda d: montrer_document(d.get("id"), d.get("chemin")),
    "agenda/elements": lambda d: elements_agenda(d.get("genre"), d.get("id")),
    "agenda/lier": lambda d: lier_agenda(d.get("genre"), d.get("id"), d.get("ids")),
    "alertes": lambda d: {"alertes": alertes_dues()},
    "marquer_alerte": lambda d: {"ok": marquer_alerte(d.get("id"))},
}
