# -*- coding: utf-8 -*-
"""Application Tâches : tâches avec échéance, priorité, étiquettes, client,
liste de contrôle et récurrence simple.

Données : donnees\\taches.json = {"taches": [...]}. Une tâche :
    {id, titre, description, echeance: "YYYY-MM-DD" | "", heure: "HH:MM" | "",
     priorite: "basse" | "normale" | "haute", etiquettes: [texte],
     contact_id: texte | "", client: texte | "",
     liste: [{id, texte, fait}], recurrence: "" | "jour" | "semaine" | "mois",
     statut: "a_faire" | "en_cours" | "fait", ordre: entier,
     origine: texte, cree: "YYYY-MM-DDTHH:MM", fait_le: "YYYY-MM-DDTHH:MM" | "",
     rappel_vu: "YYYY-MM-DDTHH:MM" | "", suivante_id, precedente_id}

- Récurrence : une tâche répétée passée à « Fait » reste dans l'historique et
  renaît (copie, étapes décochées) à la prochaine date strictement après
  aujourd'hui. Rouvrir la tâche faite retire cette copie si elle n'a pas été
  commencée (annulation d'un clic de trop).
- Groupes de l'affichage Liste : retard, aujourdhui, semaine (jusqu'au
  dimanche), plus_tard, sans_echeance ; « fait » pour les tâches faites.
- Rappels (bulle) : alertes_dues() / marquer_alerte(id), pour les tâches à
  heure précise, AVANCE_RAPPEL avant l'échéance et jusqu'à RAPPEL_PERIME après.

Pour les autres applications : creer_tache(...) (route « creer »),
taches_du_jour(limite).
"""
import calendar
import datetime
import importlib
import threading
import uuid

import config

NOM = "taches"
FORMAT_JOUR = "%Y-%m-%d"
FORMAT_MINUTE = "%Y-%m-%dT%H:%M"
PRIORITES = ("basse", "normale", "haute")
RECURRENCES = ("", "jour", "semaine", "mois")
STATUTS = ("a_faire", "en_cours", "fait")
GROUPES = ("retard", "aujourdhui", "semaine", "plus_tard", "sans_echeance")
MAX_TITRE = 200
MAX_DESCRIPTION = 2000
MAX_ETIQUETTE = 30
MAX_ETIQUETTES = 10
MAX_ETAPE = 200
MAX_ETAPES = 50
MAX_ORIGINE = 60
MAX_CLIENT = 120
AVANCE_RAPPEL = datetime.timedelta(minutes=15)
RAPPEL_PERIME = datetime.timedelta(hours=6)

_verrou = threading.RLock()

# Textes de la bulle (elle n'a pas le dictionnaire de la page).
_ANGLAIS = {
    "Échéance à {heure}": "Due at {heure}",
    "Échéance dépassée ({heure})": "Overdue ({heure})",
}


def _texte(fr, **valeurs):
    texte = _ANGLAIS.get(fr, fr) if config.langue() == "en" else fr
    return texte.format(**valeurs) if valeurs else texte


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
    if not isinstance(d.get("taches"), list):
        d["taches"] = []
    return d


def _ecrire(d):
    config.ecrire_donnees(NOM, d)


def _trouver(d, identifiant):
    t = next((x for x in d["taches"] if x.get("id") == identifiant), None)
    if t is None:
        raise ValueError("Tâche introuvable.")
    return t


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def _espaces(valeur, maxi):
    return " ".join(str(valeur or "").split())[:maxi]


def _titre(valeur):
    titre = _espaces(valeur, MAX_TITRE)
    if not titre:
        raise ValueError("Indiquez un titre.")
    return titre


def _jour(valeur):
    """« YYYY-MM-DD » ou « » ; accepte aussi « YYYY-MM-DDTHH:MM » (renvoie
    alors l'heure à part)."""
    texte = str(valeur or "").strip()
    if not texte:
        return "", ""
    try:
        jour = datetime.datetime.strptime(texte[:10], FORMAT_JOUR).date()
    except ValueError:
        raise ValueError("Échéance invalide.") from None
    heure = texte[11:16] if len(texte) >= 16 and texte[10] in "T " else ""
    return jour.isoformat(), heure


def _heure(valeur):
    texte = str(valeur or "").strip()[:5]
    if not texte:
        return ""
    try:
        return datetime.datetime.strptime(texte, "%H:%M").strftime("%H:%M")
    except ValueError:
        raise ValueError("Heure invalide.") from None


def _etiquettes(valeur):
    if isinstance(valeur, str):
        valeur = valeur.split(",")
    propres, vues = [], set()
    for e in valeur or []:
        e = _espaces(e, MAX_ETIQUETTE).lstrip("#")
        if e and e.lower() not in vues:
            vues.add(e.lower())
            propres.append(e)
    if len(propres) > MAX_ETIQUETTES:
        raise ValueError(f"{MAX_ETIQUETTES} étiquettes au plus.")
    return propres


def _liste(valeur):
    etapes = []
    for e in valeur or []:
        if isinstance(e, str):
            e = {"texte": e}
        if not isinstance(e, dict):
            continue
        texte = _espaces(e.get("texte"), MAX_ETAPE)
        if texte:
            etapes.append({"id": str(e.get("id") or _nouvel_id())[:20], "texte": texte, "fait": bool(e.get("fait"))})
    if len(etapes) > MAX_ETAPES:
        raise ValueError(f"{MAX_ETAPES} étapes au plus.")
    return etapes


def _choix(valeur, possibles, defaut, message):
    valeur = defaut if valeur is None else str(valeur)
    if valeur not in possibles:
        raise ValueError(message)
    return valeur


def _nom_contact(contact_id):
    """Le nom d'un contact de l'application Contacts, ou « » si elle est
    absente ou si le contact n'existe pas."""
    try:
        contacts = importlib.import_module("contacts")
        r = contacts.ROUTES["liste"]({})
        for c in (r.get("contacts") if isinstance(r, dict) else r) or []:
            if str(c.get("id")) == str(contact_id):
                return _espaces(c.get("nom") or c.get("entreprise"), MAX_CLIENT)
    except Exception:  # noqa: BLE001 - application absente ou différente : rien
        pass
    return ""


def _champs(valeurs, existante=None):
    """Les champs modifiables, validés. « existante » : la tâche avant
    modification (les champs absents de « valeurs » sont gardés)."""
    base = existante or {}
    v = dict(valeurs or {})
    propre = {"titre": _titre(v.get("titre", base.get("titre")))}
    propre["description"] = str(v.get("description", base.get("description", "")) or "").strip()[:MAX_DESCRIPTION]
    if "echeance" in v or "heure" in v or not existante:
        jour, heure_jointe = _jour(v.get("echeance", base.get("echeance")))
        heure = _heure(v["heure"]) if v.get("heure") else heure_jointe
        if heure and not jour:
            raise ValueError("Indiquez une date pour l'heure.")
        propre["echeance"], propre["heure"] = jour, _heure(heure)
    propre["priorite"] = _choix(v.get("priorite", base.get("priorite")) or None, PRIORITES, "normale", "Priorité inconnue.")
    propre["etiquettes"] = _etiquettes(v.get("etiquettes", base.get("etiquettes")))
    propre["liste"] = _liste(v.get("liste", base.get("liste")))
    propre["recurrence"] = _choix(v.get("recurrence", base.get("recurrence")) or "", RECURRENCES, "", "Répétition inconnue.")
    if "contact_id" in v or "client" in v or not existante:
        contact_id = str(v.get("contact_id") or "").strip()[:60]
        client = _espaces(v.get("client"), MAX_CLIENT)
        if contact_id and not client:
            client = _nom_contact(contact_id)
        propre["contact_id"], propre["client"] = contact_id, client
    if "statut" in v:
        propre["statut"] = _choix(v["statut"], STATUTS, "a_faire", "Statut inconnu.")
    # Une tâche répétée a toujours une date : aujourd'hui par défaut.
    echeance = propre.get("echeance", base.get("echeance"))
    if propre["recurrence"] and not echeance:
        propre["echeance"] = maintenant().date().isoformat()
        propre.setdefault("heure", base.get("heure", ""))
    return propre


# ---------------------------------------------------------------------------
# Dates
# ---------------------------------------------------------------------------
def _ajouter_mois(jour, n, jour_du_mois):
    mois = jour.month - 1 + n
    annee, mois = jour.year + mois // 12, mois % 12 + 1
    return datetime.date(annee, mois, min(jour_du_mois, calendar.monthrange(annee, mois)[1]))


def prochaine_date(echeance, recurrence, aujourdhui, jour_du_mois=None):
    """La prochaine échéance d'une tâche répétée : strictement après
    aujourd'hui (une tâche faite en retard ne renaît pas déjà en retard)."""
    depart = datetime.date.fromisoformat(echeance) if echeance else aujourdhui
    jour_du_mois = jour_du_mois or depart.day
    suivante, n = depart, 0
    while suivante <= aujourdhui or n == 0:
        n += 1
        if recurrence == "jour":
            suivante = depart + datetime.timedelta(days=n)
        elif recurrence == "semaine":
            suivante = depart + datetime.timedelta(weeks=n)
        elif recurrence == "mois":
            suivante = _ajouter_mois(depart, n, jour_du_mois)
        else:
            raise ValueError("Répétition inconnue.")
        if n > 5000:  # garde-fou : jamais de boucle sans fin
            break
    return suivante.isoformat()


def _moment(t):
    """L'échéance en datetime (heure ou fin de journée), ou None."""
    if not t.get("echeance"):
        return None
    jour = datetime.date.fromisoformat(t["echeance"])
    if t.get("heure"):
        h, m = (int(x) for x in t["heure"].split(":"))
        return datetime.datetime.combine(jour, datetime.time(h, m))
    return None


def groupe(t, a_l_heure):
    """Le groupe de la tâche dans l'affichage Liste."""
    if t.get("statut") == "fait":
        return "fait"
    if not t.get("echeance"):
        return "sans_echeance"
    jour = datetime.date.fromisoformat(t["echeance"])
    aujourdhui = a_l_heure.date()
    moment = _moment(t)
    if jour < aujourdhui or (moment is not None and moment < a_l_heure):
        return "retard"
    if jour == aujourdhui:
        return "aujourdhui"
    dimanche = aujourdhui + datetime.timedelta(days=6 - aujourdhui.weekday())
    return "semaine" if jour <= dimanche else "plus_tard"


def _cle_tri(t):
    """Échéance (sans échéance à la fin), heure, priorité haute d'abord, ordre."""
    rang = {"haute": 0, "normale": 1, "basse": 2}.get(t.get("priorite"), 1)
    return (t.get("echeance") or "9999-99-99", t.get("heure") or "99:99", rang, t.get("ordre", 0))


def _vue(t, a_l_heure):
    """La tâche telle que la page la reçoit (copie + groupe)."""
    v = dict(t)
    v["groupe"] = groupe(t, a_l_heure)
    return v


# ---------------------------------------------------------------------------
# Création, modification
# ---------------------------------------------------------------------------
def _premier_ordre(d, statut):
    ordres = [x.get("ordre", 0) for x in d["taches"] if x.get("statut") == statut]
    return (min(ordres) - 1) if ordres else 0


def creer_tache(titre, echeance="", description="", contact_id="", origine="", **autres):
    """Crée une tâche et la renvoie. Utilisable par les autres applications
    (route « creer ») : seul le titre est obligatoire."""
    valeurs = {"titre": titre, "echeance": echeance, "description": description,
               "contact_id": contact_id, **autres}
    with _verrou:
        propre = _champs(valeurs)
        statut = propre.pop("statut", "a_faire")
        d = _lire()
        a_l_heure = maintenant()
        tache = {"id": _nouvel_id(), **propre, "statut": statut, "ordre": _premier_ordre(d, statut),
                 "origine": _espaces(origine, MAX_ORIGINE), "cree": a_l_heure.strftime(FORMAT_MINUTE),
                 "fait_le": a_l_heure.strftime(FORMAT_MINUTE) if statut == "fait" else "", "rappel_vu": ""}
        d["taches"].append(tache)
        _ecrire(d)
        return _vue(tache, a_l_heure)


def _renaitre(d, t, a_l_heure):
    """Crée l'occurrence suivante d'une tâche répétée qui vient d'être faite."""
    if not t.get("recurrence") or t.get("suivante_id"):
        return None
    jour_du_mois = t.get("jour_du_mois") or (int(t["echeance"][8:10]) if t.get("echeance") else None)
    suivante = {**{k: v for k, v in t.items() if k not in ("suivante_id", "precedente_id")},
                "id": _nouvel_id(), "statut": "a_faire", "fait_le": "", "rappel_vu": "",
                "echeance": prochaine_date(t.get("echeance"), t["recurrence"], a_l_heure.date(), jour_du_mois),
                "liste": [{**e, "fait": False} for e in t.get("liste", [])],
                "ordre": _premier_ordre(d, "a_faire"), "cree": a_l_heure.strftime(FORMAT_MINUTE),
                "precedente_id": t["id"]}
    if t["recurrence"] == "mois" and jour_du_mois:
        suivante["jour_du_mois"] = jour_du_mois
    t["suivante_id"] = suivante["id"]
    d["taches"].append(suivante)
    return suivante


def _rouvrir(d, t):
    """Une tâche faite qu'on rouvre : sa copie suivante, si elle n'a pas été
    commencée, disparaît (sinon elle ferait double)."""
    sid = t.pop("suivante_id", None)
    if not sid:
        return
    suivante = next((x for x in d["taches"] if x.get("id") == sid), None)
    if suivante and suivante.get("statut") == "a_faire" and not any(e.get("fait") for e in suivante.get("liste", [])):
        d["taches"].remove(suivante)
    elif suivante:
        t["suivante_id"] = sid  # déjà commencée : on la garde, toujours liée


def _changer_statut(d, t, statut, a_l_heure):
    """Change le statut ; renvoie l'occurrence suivante créée, ou None."""
    avant = t.get("statut", "a_faire")
    if statut == avant:
        return None
    t["statut"] = statut
    if statut == "fait":
        t["fait_le"] = a_l_heure.strftime(FORMAT_MINUTE)
        return _renaitre(d, t, a_l_heure)
    t["fait_le"] = ""
    if avant == "fait":
        _rouvrir(d, t)
    return None


def modifier_tache(valeurs):
    """Modifie une tâche ({id, ...champs}). Renvoie {tache, suivante}."""
    valeurs = valeurs or {}
    with _verrou:
        d = _lire()
        t = _trouver(d, valeurs.get("id"))
        propre = _champs(valeurs, t)
        statut = propre.pop("statut", None)
        if propre.get("echeance", t.get("echeance")) != t.get("echeance") or \
                propre.get("heure", t.get("heure")) != t.get("heure"):
            t["rappel_vu"] = ""
        if propre.get("echeance") and propre.get("echeance") != t.get("echeance"):
            t.pop("jour_du_mois", None)
        t.update(propre)
        a_l_heure = maintenant()
        suivante = _changer_statut(d, t, statut, a_l_heure) if statut else None
        _ecrire(d)
        return {"tache": _vue(t, a_l_heure), "suivante": _vue(suivante, a_l_heure) if suivante else None}


def cocher(identifiant, fait=True):
    """Case à cocher de la liste : fait ou à faire. Renvoie {tache, suivante}."""
    return deplacer(identifiant, "fait" if fait else "a_faire")


def deplacer(identifiant, statut, ordre=None):
    """Tableau : la tâche passe dans la colonne « statut » ; « ordre » (liste
    d'id) donne le nouvel ordre de la colonne. Renvoie {tache, suivante}."""
    statut = _choix(statut, STATUTS, "a_faire", "Statut inconnu.")
    with _verrou:
        d = _lire()
        t = _trouver(d, identifiant)
        a_l_heure = maintenant()
        suivante = _changer_statut(d, t, statut, a_l_heure)
        if isinstance(ordre, list):
            par_id = {x["id"]: x for x in d["taches"]}
            for rang, i in enumerate(ordre):
                x = par_id.get(i)
                if x is not None and x.get("statut") == statut:
                    x["ordre"] = rang
        _ecrire(d)
        return {"tache": _vue(t, a_l_heure), "suivante": _vue(suivante, a_l_heure) if suivante else None}


def cocher_etape(identifiant, etape_id, fait=True):
    """Coche ou décoche une étape de la liste de contrôle."""
    with _verrou:
        d = _lire()
        t = _trouver(d, identifiant)
        etape = next((e for e in t.get("liste", []) if e.get("id") == etape_id), None)
        if etape is None:
            raise ValueError("Étape introuvable.")
        etape["fait"] = bool(fait)
        _ecrire(d)
        return _vue(t, maintenant())


def supprimer_tache(identifiant):
    with _verrou:
        d = _lire()
        avant = len(d["taches"])
        d["taches"] = [x for x in d["taches"] if x.get("id") != identifiant]
        for x in d["taches"]:
            if x.get("suivante_id") == identifiant:
                x.pop("suivante_id", None)
        if len(d["taches"]) != avant:
            _ecrire(d)
        return avant - len(d["taches"])


# ---------------------------------------------------------------------------
# Lecture
# ---------------------------------------------------------------------------
def toutes():
    """Toutes les tâches (copies, avec leur groupe), triées par échéance."""
    with _verrou:
        d = _lire()
    a_l_heure = maintenant()
    return [_vue(t, a_l_heure) for t in sorted(d["taches"], key=_cle_tri)]


def taches_du_jour(limite=5):
    """Les tâches en retard puis celles du jour (au plus « limite »), pour
    l'Accueil : {retard, aujourdhui, total, taches}."""
    liste = [t for t in toutes() if t["groupe"] in ("retard", "aujourdhui")]
    liste.sort(key=lambda t: (t["groupe"] != "retard", *_cle_tri(t)))
    return {"retard": sum(1 for t in liste if t["groupe"] == "retard"),
            "aujourdhui": sum(1 for t in liste if t["groupe"] == "aujourdhui"),
            "total": len(liste), "taches": liste[:max(0, int(limite or 0))]}


def _route_liste(_d):
    liste = toutes()
    etiquettes = sorted({e for t in liste for e in t.get("etiquettes", [])}, key=str.lower)
    clients = sorted({t["client"] for t in liste if t.get("client")}, key=str.lower)
    a_l_heure = maintenant()
    return {"taches": liste, "etiquettes": etiquettes, "clients": clients,
            "aujourdhui": a_l_heure.date().isoformat(), "maintenant": a_l_heure.strftime(FORMAT_MINUTE)}


# ---------------------------------------------------------------------------
# Rappels (bulle)
# ---------------------------------------------------------------------------
def alertes_dues():
    """Les tâches à heure précise dont l'échéance arrive (AVANCE_RAPPEL
    avant) ou vient de passer (moins de RAPPEL_PERIME) : [{id, titre, detail}]."""
    with _verrou:
        d = _lire()
    a_l_heure = maintenant()
    dues = []
    for t in sorted(d["taches"], key=_cle_tri):
        moment = _moment(t)
        if moment is None or t.get("statut") == "fait":
            continue
        cle = moment.strftime(FORMAT_MINUTE)
        if t.get("rappel_vu") == cle or not (moment - AVANCE_RAPPEL <= a_l_heure <= moment + RAPPEL_PERIME):
            continue
        heure = moment.strftime("%H:%M")
        detail = _texte("Échéance à {heure}", heure=heure) if a_l_heure <= moment \
            else _texte("Échéance dépassée ({heure})", heure=heure)
        if t.get("client"):
            detail += " · " + t["client"]
        dues.append({"id": t["id"], "titre": t["titre"], "detail": detail})
    return dues


def marquer_alerte(identifiant):
    """Rappel vu (pour l'échéance actuelle de la tâche). Renvoie True si la
    tâche existe."""
    with _verrou:
        d = _lire()
        t = next((x for x in d["taches"] if x.get("id") == identifiant), None)
        moment = _moment(t) if t else None
        if moment is None:
            return False
        t["rappel_vu"] = moment.strftime(FORMAT_MINUTE)
        _ecrire(d)
        return True


# ---------------------------------------------------------------------------
# Routes de la page
# ---------------------------------------------------------------------------
def _route_creer(d):
    autres = {k: d[k] for k in ("heure", "priorite", "etiquettes", "liste", "recurrence", "client", "statut") if k in d}
    return creer_tache(d.get("titre"), d.get("echeance") or "", d.get("description") or "",
                       d.get("contact_id") or "", d.get("origine") or "", **autres)


ROUTES = {
    "liste": _route_liste,
    "creer": _route_creer,
    "modifier": lambda d: modifier_tache(d.get("tache") or d),
    "cocher": lambda d: cocher(d.get("id"), bool(d.get("fait", True))),
    "deplacer": lambda d: deplacer(d.get("id"), d.get("statut"), d.get("ordre")),
    "etape": lambda d: cocher_etape(d.get("id"), d.get("etape_id"), bool(d.get("fait", True))),
    "supprimer": lambda d: {"supprimes": supprimer_tache(d.get("id"))},
    "jour": lambda d: taches_du_jour(d.get("limite", 5)),
    "alertes": lambda d: {"alertes": alertes_dues()},
    "marquer_alerte": lambda d: {"ok": marquer_alerte(d.get("id"))},
}
