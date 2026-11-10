# -*- coding: utf-8 -*-
"""Application « Missions » : offres freelance et télétravail de sources
publiques, notées selon ce que chaque utilisateur cherche, avec le suivi des
candidatures.

Sources (aucune clé, conditions respectées) : Remotive, Remote OK,
Himalayas, Jobicy (API JSON) et We Work Remotely (flux RSS).
- la source est toujours citée et le lien d'origine reste inchangé ;
- les offres expirées (ou publiées il y a plus de MAX_JOURS jours) sont
  retirées ;
- les descriptions ne sont PAS conservées : seuls quelques indices en sont
  tirés (technologies, années d'expérience demandées, faux télétravail) ;
- une source est interrogée au plus deux fois par jour (INTERVALLE), sauf si
  sa dernière collecte a échoué (nouvel essai après ATTENTE_ECHEC) ;
- chaque source peut être désactivée.

Fichiers :
- donnees\\missions.json : {recherches, suivi, vues, masquees, alertes,
  sources_off} ;
- donnees\\missions_offres.json : le cache des offres collectées
  {sources: {id: {derniere, essai, ok, erreur, nombre}}, offres: [...]}.

Une recherche enregistrée : {id, nom, domaines, types, zones, niveau,
salaire_min, devise, periode, garder_sans_salaire, importants, utiles,
eviter, score_min}. Une offre n'apparaît que si elle correspond à un domaine
choisi ou à un mot-clé important, à un type et à une zone choisis, au niveau
(années d'expérience demandées) et au salaire minimum.

Notation (règles fixes, sans IA) : domaine +3, mot important +5, mot utile
+2 (titre, étiquettes et technologies, mots entiers), mot à éviter −5 (titre
seulement) ; bonus de type (freelance +2, contrat +1) seulement si l'offre
est déjà pertinente (score ≥ 3), sinon le score est ramené à 0 au plus.

Pour la bulle : alertes_dues() (une alerte par recherche quand de nouvelles
offres au-dessus du score minimum sont arrivées depuis la dernière alerte,
au plus une par jour et par recherche ; la collecte due est lancée en fond)
et marquer_alerte(id).
"""
import concurrent.futures
import datetime
import email.utils
import hashlib
import html
import json
import os
import re
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import uuid

import config
import systeme

NOM = "missions"
NOM_OFFRES = "missions_offres"
UA = "Mes outils (usage personnel)"
INTERVALLE = datetime.timedelta(hours=12)        # au plus deux collectes par jour et par source
ATTENTE_ECHEC = datetime.timedelta(minutes=5)    # après un échec : nouvel essai permis
DELAI_PAGES = 1.5                                # secondes entre deux pages d'une même source
TIMEOUT = 30
ESSAIS = 3
MAX_OCTETS = 40 * 1024 * 1024
MAX_JOURS = 60
MAX_OFFRES_SOURCE = 1500
MAX_AFFICHEES = 300
MAX_RECHERCHES = 20
MAX_MOTS = 40
MAX_MOT = 50
MAX_NOM = 60
MAX_NOTE = 2000
MAX_VUES = 3000
MAX_SUIVI = 1000
MAX_PROFIL = 1_000_000
SCORE_DEFAUT = 3
PERTINENCE = 3

SOURCES = {
    "remotive": {"nom": "Remotive", "url": "https://remotive.com"},
    "remoteok": {"nom": "Remote OK", "url": "https://remoteok.com"},
    "himalayas": {"nom": "Himalayas", "url": "https://himalayas.app"},
    "jobicy": {"nom": "Jobicy", "url": "https://jobicy.com"},
    "wwr": {"nom": "We Work Remotely", "url": "https://weworkremotely.com"},
}
DOMAINES = ("dev", "data", "design", "marketing", "redaction", "support", "assistanat", "finance", "ventes")
TYPES = ("freelance", "contrat", "temps_plein", "temps_partiel", "stage")
TYPES_DEFAUT = ("freelance", "contrat", "temps_plein", "temps_partiel")
ZONES = ("monde", "afrique", "europe", "amerique", "asie", "autre", "inconnue")
NIVEAUX = {"debutant": 2, "confirme": 5, "senior": None}
PERIODES = ("an", "mois", "jour", "heure")
# Pour comparer des salaires de périodes différentes (ordre de grandeur).
PAR_AN = {"an": 1, "mois": 12, "semaine": 48, "jour": 220, "heure": 1760}
STATUTS = ("a_voir", "postule", "entretien", "refuse", "retenu")
SITES_MANUELS = {
    "malt": ("Malt", "https://www.malt.fr/s?q={q}"),
    "codeur": ("Codeur.com", "https://www.codeur.com/projects?q={q}"),
    "comeup": ("ComeUp", "https://comeup.com/fr/search?q={q}"),
    "upwork": ("Upwork", "https://www.upwork.com/nx/search/jobs/?q={q}"),
    "linkedin": ("LinkedIn", "https://www.linkedin.com/jobs/search/?keywords={q}&f_WT=2"),
    "indeed": ("Indeed", "https://www.indeed.com/jobs?q={q}&l=Remote"),
}
LIBELLES_DOMAINES = {"dev": "Développement", "data": "Data et IA", "design": "Design", "marketing": "Marketing",
                     "redaction": "Rédaction et traduction", "support": "Support client",
                     "assistanat": "Assistanat et administration", "finance": "Finance et gestion de projet",
                     "ventes": "Ventes"}

# Modèles de première recherche, selon le métier choisi au premier lancement.
MODELES = {
    "developpeur": {"nom": "Développement", "domaines": ["dev"], "types": ["freelance", "contrat"]},
    "assistant_virtuel": {"nom": "Assistanat virtuel", "domaines": ["support", "assistanat"],
                          "types": ["freelance", "temps_partiel"]},
    "assistant_direction": {"nom": "Assistanat de direction", "domaines": ["assistanat"],
                            "types": list(TYPES_DEFAUT)},
    "freelance": {"nom": "Missions freelance", "domaines": [], "types": ["freelance", "contrat"]},
    "personnalise": {"nom": "", "domaines": [], "types": list(TYPES_DEFAUT)},
}

_verrou = threading.RLock()
_verrou_collecte = threading.Lock()

# Textes de la bulle (la bulle n'a pas le dictionnaire de la page).
_ANGLAIS = {
    "{n} nouvelles offres : {nom}": "{n} new offers: {nom}",
    "Nouvelle offre : {nom}": "New offer: {nom}",
    "{titre} ({score} points)": "{titre} ({score} points)",
    "{titre} chez {entreprise} ({score} points)": "{titre} at {entreprise} ({score} points)",
    "Mon profil": "My profile",
}


def _texte(fr, **valeurs):
    texte = _ANGLAIS.get(fr, fr) if config.langue() == "en" else fr
    return texte.format(**valeurs) if valeurs else texte


class ErreurSource(Exception):
    """Une source n'a pas répondu correctement (n'arrête pas les autres)."""


def maintenant():
    """L'heure locale (remplacée par une horloge simulée dans les tests)."""
    return datetime.datetime.now().replace(microsecond=0)


def _pause(secondes):
    time.sleep(secondes)


# ---------------------------------------------------------------------------
# Texte
# ---------------------------------------------------------------------------
def norm(texte):
    """Minuscules, sans accents, espaces simples (comme norm() du site d'origine)."""
    s = unicodedata.normalize("NFD", str(texte or ""))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("’", "'").replace("`", "'")
    return " ".join(s.split()).lower()


def _propre(texte, maxi=300):
    return " ".join(html.unescape(str(texte or "")).split())[:maxi]


_motifs = {}


def contient_mot(texte_norm, mot):
    """Mot ou expression entière : « java » ne correspond pas à « javascript »."""
    m = _motifs.get(mot)
    if m is None:
        m = re.compile(r"(?:^|[^a-z0-9])" + re.escape(norm(mot)) + r"(?:[^a-z0-9]|$)")
        if len(_motifs) > 5000:
            _motifs.clear()
        _motifs[mot] = m
    return bool(m.search(texte_norm))


# ---------------------------------------------------------------------------
# Normalisation des offres
# ---------------------------------------------------------------------------
def type_contrat(brut):
    s = norm(" ".join(brut if isinstance(brut, (list, tuple)) else [str(brut or "")]))
    if re.search(r"freelance", s):
        return "freelance"
    if re.search(r"contract|contrat|temporary", s):
        return "contrat"
    if re.search(r"part[ _-]?time|partiel", s):
        return "temps_partiel"
    if re.search(r"intern|stage", s):
        return "stage"
    return "temps_plein"


_ZONES_RE = [
    ("monde", re.compile(r"worldwide|anywhere|global|world ?wide|international|^remote$|all countries")),
    ("afrique", re.compile(r"africa|afrique|madagascar|\bemea\b|middle east|nigeria|kenya|ghana|egypt|morocco|"
                           r"maroc|tunisia|senegal|cameroon|ethiopia|uganda|rwanda|mauritius")),
    ("europe", re.compile(r"europe|\beu\b|\beea\b|\bemea\b|\bcet\b|\bcest\b|united kingdom|\buk\b|france|germany|"
                          r"spain|portugal|ireland|netherlands|belgium|luxembourg|poland|italy|sweden|denmark|"
                          r"norway|finland|austria|switzerland|czech|romania|greece|hungary|bulgaria|croatia|"
                          r"estonia|latvia|lithuania|serbia|ukraine")),
    ("amerique", re.compile(r"america|\busa\b|\bu\.s\.?|\bus\b|united states|canada|latam|mexico|brazil|"
                            r"argentina|colombia|chile|peru|uruguay|costa rica")),
    ("asie", re.compile(r"\basia|apac|india|philippines|pakistan|japan|singapore|indonesia|vietnam|malaysia|"
                        r"thailand|china|korea|australia|new zealand|oceania")),
]


def zones(lieu):
    """Les zones d'où l'on peut postuler, d'après le lieu indiqué (plusieurs possibles)."""
    s = norm(lieu)
    if not s:
        return ["inconnue"]
    trouvees = [z for z, motif in _ZONES_RE if motif.search(s)]
    if "monde" in trouvees:
        return ["monde"]
    return trouvees or ["autre"]


# L'ordre compte : « Business Development » est un métier de vente ;
# « Executive Assistant » de l'assistanat, pas de la finance.
_CATEGORIES = [
    ("ventes", re.compile(r"sales|business development|account (executive|manager)|commercial")),
    ("assistanat", re.compile(r"virtual assistant|executive assistant|personal assistant|administrative|"
                              r"admin(istrative)? assistant|(?<!system )(?<!systems )(?<!database )(?<!sys )\badmin\b|"
                              r"office (manager|assistant|administrator|coordinator)|\bback office\b|"
                              r"\bassistant\b|secretar|receptionist|data entry")),
    ("data", re.compile(r"\bdata\b|machine learning|\bml\b|\bai\b|artificial intelligence|analytics|scientist")),
    ("redaction", re.compile(r"writ|copy(?!right)|(?<!video )editor|translat|transcri|journalis|interpret|"
                             r"proofread|locali[sz]ation")),
    ("design", re.compile(r"design|\bux\b|\bui\b|graphic|creative|illustrat|video|animation")),
    ("marketing", re.compile(r"marketing|seo|growth|social media|content|community|brand")),
    ("support", re.compile(r"customer|support|success|service client")),
    ("dev", re.compile(r"software|developer|engineer|programming|devops|backend|frontend|front-end|back-end|"
                       r"full[ -]?stack|mobile|\bqa\b|tester|sysadmin|systems? admin|cloud|security|\bweb\b")),
    ("finance", re.compile(r"finance|account(ing|ant)|bookkeep|legal|operations|project manag|product manag|"
                           r"program manag|\bhr\b|human resources|recruit")),
]


def categorie_offre(titre, *autres):
    """Le titre d'abord (plus précis que les catégories des sites), sinon les
    catégories et étiquettes de la source."""
    c = categorie(titre)
    return c if c != "autres" else categorie(*autres)


def categorie(*textes):
    morceaux = []
    for t in textes:
        if isinstance(t, (list, tuple)):
            morceaux += [str(x) for x in t if x]
        elif t:
            morceaux.append(str(t))
    s = norm(" ".join(morceaux))
    for ident, motif in _CATEGORIES:
        if motif.search(s):
            return ident
    return "autres"


def date_iso(valeur):
    """Nombre (secondes ou millisecondes), ISO ou date RSS → « YYYY-MM-DD » (ou None)."""
    if valeur in (None, "", 0):
        return None
    try:
        if isinstance(valeur, (int, float)) and not isinstance(valeur, bool):
            secondes = valeur / 1000 if valeur >= 1e12 else valeur
            return datetime.datetime.fromtimestamp(secondes, datetime.timezone.utc).date().isoformat()
        texte = str(valeur).strip()
        if re.fullmatch(r"\d{9,13}", texte):
            return date_iso(int(texte))
        if re.match(r"\d{4}-\d{2}-\d{2}", texte):
            return datetime.date.fromisoformat(texte[:10]).isoformat()
        return email.utils.parsedate_to_datetime(texte).date().isoformat()
    except (ValueError, TypeError, OverflowError, OSError, IndexError):
        return None


_PERIODES_SOURCE = {"hourly": "heure", "hour": "heure", "daily": "jour", "day": "jour", "weekly": "semaine",
                    "week": "semaine", "monthly": "mois", "month": "mois", "annual": "an", "annually": "an",
                    "yearly": "an", "year": "an"}


def _nombre(valeur):
    try:
        n = float(valeur)
    except (TypeError, ValueError):
        return None
    return int(round(n)) if n > 0 and n == n and n < 1e9 else None


def salaire(mini, maxi, devise, periode=None):
    """Salaire chiffré {min, max, devise, periode} ou None."""
    mini, maxi = _nombre(mini), _nombre(maxi)
    devise = str(devise or "").strip().upper()
    if not (mini or maxi) or not re.fullmatch(r"[A-Z]{3}", devise):
        return None
    if mini and maxi and mini > maxi:
        mini, maxi = maxi, mini
    return {"min": mini, "max": maxi, "devise": devise,
            "periode": _PERIODES_SOURCE.get(str(periode or "").lower()) or None}


_SYMBOLES = [("€", "EUR"), ("£", "GBP"), ("CA$", "CAD"), ("C$", "CAD"), ("A$", "AUD"), ("AU$", "AUD"), ("$", "USD")]


def salaire_texte(texte):
    """« $60,000 - $80,000 /year », « 40-50k EUR », « €35/hour » → salaire chiffré, sinon None."""
    s = str(texte or "")
    if not s.strip():
        return None
    devise = None
    m = re.search(r"\b(USD|EUR|GBP|CAD|AUD|CHF|INR|PLN|SGD|NZD)\b", s, re.I)
    if m:
        devise = m.group(1).upper()
    else:
        for symbole, code in _SYMBOLES:
            if symbole in s:
                devise = code
                break
    if not devise:
        return None
    lus = []
    for brut, k in re.findall(r"(\d{1,3}(?:[,\s]\d{3})+|\d+(?:\.\d+)?)\s*([kK])?", s):
        lus.append((float(re.sub(r"[,\s]", "", brut)), bool(k)))
    # « 40-50k » : le « k » vaut pour les deux bornes.
    milliers = any(k for _, k in lus)
    nombres = [n * 1000 if k or (milliers and n < 1000) else n for n, k in lus]
    nombres = [n for n in nombres if n >= 5][:2]
    if not nombres:
        return None
    b = norm(s)
    periode = None
    if re.search(r"hour|/ ?h\b|/hr|per hr|hourly", b):
        periode = "heure"
    elif re.search(r"month|/mo\b|monthly", b):
        periode = "mois"
    elif re.search(r"\bday\b|daily|/day", b):
        periode = "jour"
    elif re.search(r"year|annual|/yr|/y\b|\bpa\b|per annum", b) or max(nombres) >= 10000:
        periode = "an"
    sal = salaire(min(nombres), max(nombres), devise)
    if sal:
        sal["periode"] = periode
    return sal


TECHS = [
    (".NET", r"\.net\b|dotnet|asp\.net"), ("C#", r"c#|\bcsharp\b"), ("Java", r"\bjava\b(?!\s*script)"),
    ("Spring", r"\bspring\b"), ("Python", r"\bpython\b"), ("Django", r"\bdjango\b"), ("Odoo", r"\bodoo\b"),
    ("TypeScript", r"\btypescript\b"), ("JavaScript", r"\bjavascript\b"), ("React", r"\breact(?!\s*native)\b"),
    ("React Native", r"\breact\s*native\b"), ("Vue.js", r"\bvue(\.?js)?\b"), ("Angular", r"\bangular\b"),
    ("Node.js", r"\bnode(\.?js)?\b"), ("PHP", r"\bphp\b"), ("Laravel", r"\blaravel\b"), ("Ruby", r"\bruby\b|\brails\b"),
    ("Kotlin", r"\bkotlin\b"), ("Swift", r"\bswift\b"), ("Flutter", r"\bflutter\b"), ("Go", r"\bgolang\b"),
    ("SQL", r"\bsql\b"), ("PostgreSQL", r"\bpostgres(ql)?\b"), ("SQL Server", r"sql server|\bmssql\b"),
    ("MongoDB", r"\bmongo(db)?\b"), ("Docker", r"\bdocker\b"), ("Kubernetes", r"\bkubernetes\b|\bk8s\b"),
    ("AWS", r"\baws\b"), ("Azure", r"\bazure\b"), ("GCP", r"\bgcp\b|google cloud"), ("Supabase", r"\bsupabase\b"),
    ("Firebase", r"\bfirebase\b"), ("WordPress", r"\bwordpress\b"), ("Shopify", r"\bshopify\b"),
    ("Figma", r"\bfigma\b"), ("Excel", r"\bexcel\b"), ("Salesforce", r"\bsalesforce\b"), ("HubSpot", r"\bhubspot\b"),
]
TECHS = [(nom, re.compile(motif, re.I)) for nom, motif in TECHS]
# Offres présentées comme « remote » mais en réalité sur place ou hybrides.
# Les négations (« very few office-based roles », « no on-site work ») ne comptent pas.
FAUX_TELETRAVAIL = re.compile(
    r"(?<!few )(?<!no )(?<!non )(?<!not )(?<!without )"
    r"(hybrid (role|position|work|working|model|schedule)|on-?site (role|position|work)|office-based (role|position))"
    r"|\b(this|the) (role|position|job) is (office-based|on-?site|hybrid)"
    r"|work(ing)? (from|in|at) (our|the) office (\d|one|two|three|four) days"
    r"|\b(one|1|two|2|three|3|four|4) days? (a|per) week (in|at|from) (the |our )?office"
    r"|\b(one|1) day (a|per) week[^.]{0,30}(home|wfh|remote)|\bwfh[^.]{0,30}\b(one|1) day", re.I)
EXPERIENCE = re.compile(r"(\d{1,2})\s*\+?\s*(?:-\s*\d{1,2}\s*)?(?:years?|yrs)\b[^.]{0,40}experience", re.I)


def analyser(description):
    """Les seuls indices gardés d'une description (qui n'est jamais stockée)."""
    txt = re.sub(r"<[^>]+>", " ", str(description or ""))
    txt = " ".join(html.unescape(txt).split())
    if not txt:
        return {}
    r = {}
    techs = [nom for nom, motif in TECHS if motif.search(txt)]
    if techs:
        r["techs"] = techs
    if FAUX_TELETRAVAIL.search(txt):
        r["hors_teletravail"] = True
    m = EXPERIENCE.search(txt)
    if m and 0 < int(m.group(1)) <= 30:
        r["experience"] = int(m.group(1))
    return r


def _ident(source, brut):
    brut = str(brut or "").strip()
    if not brut:
        return None
    if len(brut) > 40 or not re.fullmatch(r"[\w.-]+", brut):
        brut = hashlib.sha1(brut.encode("utf-8")).hexdigest()[:16]
    return f"{source}-{brut}"


def offre(o):
    """Une offre propre à partir des champs d'une source (None si inutilisable)."""
    titre = _propre(o.get("titre"), 200)
    url = str(o.get("url") or "").strip()
    ident = _ident(o["source"], o.get("id") or url)
    if not titre or not re.match(r"^https://[^\s]+$", url) or not ident:
        return None
    lieu = _propre(o.get("lieu"), 160) or None
    zs = o.get("zones") or zones(lieu)
    a = analyser(o.get("description"))
    tags = o.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    r = {
        "id": ident, "source": o["source"], "titre": titre,
        "entreprise": _propre(o.get("entreprise"), 120) or None,
        "lieu": lieu, "zones": zs, "type": o.get("type") or "temps_plein",
        "categorie": o.get("categorie") or "autres",
        "salaire": o.get("salaire"), "salaire_texte": None,
        "tags": [t for t in (_propre(x, 40) for x in tags) if t][:6],
        "date": o.get("date"), "expire": o.get("expire"), "url": url,
    }
    if not r["salaire"] and o.get("salaire_texte"):
        r["salaire"] = salaire_texte(o["salaire_texte"])
        if not r["salaire"]:
            r["salaire_texte"] = _propre(o["salaire_texte"], 80)
    r.update(a)
    return r


# ---------------------------------------------------------------------------
# Réseau
# ---------------------------------------------------------------------------
def _telecharger(url, accept="application/json"):
    """Le contenu d'une adresse (octets). ErreurSource en cas d'échec,
    après quelques essais pour les erreurs passagères (429, 5xx, réseau)."""
    requete = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    derniere = None
    for essai in range(ESSAIS):
        if essai:
            _pause(2 * essai)
        try:
            with urllib.request.urlopen(requete, timeout=TIMEOUT) as r:  # noqa: S310 (adresses fixes en https)
                return r.read(MAX_OCTETS)
        except urllib.error.HTTPError as e:
            derniere = f"HTTP {e.code}"
            if e.code != 429 and e.code < 500:
                break
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            derniere = str(getattr(e, "reason", None) or e) or e.__class__.__name__
    raise ErreurSource(derniere or "pas de réponse")


def _json(url):
    try:
        return json.loads(_telecharger(url).decode("utf-8", "replace"))
    except ValueError:
        raise ErreurSource("réponse illisible") from None


def collecte_remotive():
    j = _json("https://remotive.com/api/remote-jobs")
    return [offre({
        "source": "remotive", "id": x.get("id"), "titre": x.get("title"), "entreprise": x.get("company_name"),
        "lieu": x.get("candidate_required_location"), "type": type_contrat(x.get("job_type")),
        "categorie": categorie_offre(x.get("title"), x.get("category")), "salaire_texte": x.get("salary"),
        "tags": x.get("tags"), "date": date_iso(x.get("publication_date")), "url": x.get("url"),
        "description": x.get("description")}) for x in (j.get("jobs") or []) if isinstance(x, dict)]


def collecte_remoteok():
    j = _json("https://remoteok.com/api")
    if not isinstance(j, list):
        raise ErreurSource("réponse inattendue")
    return [offre({
        "source": "remoteok", "id": x.get("id"), "titre": x.get("position"), "entreprise": x.get("company"),
        "lieu": x.get("location"), "type": type_contrat(x.get("tags") or []),
        "categorie": categorie_offre(x.get("position"), x.get("tags") or []),
        "salaire": salaire(x.get("salary_min"), x.get("salary_max"), "USD", "annual"), "tags": x.get("tags"),
        "date": date_iso(x.get("date") or x.get("epoch")), "url": x.get("url"),
        "description": x.get("description")}) for x in j if isinstance(x, dict) and x.get("id") and x.get("position")]


def _himalayas_offre(x):
    restr = []
    for r in x.get("locationRestrictions") or []:
        restr.append((r.get("name") or r.get("alpha2") or "") if isinstance(r, dict) else str(r or ""))
    restr = [r for r in restr if r]
    return offre({
        "source": "himalayas", "id": x.get("guid") or x.get("applicationLink"), "titre": x.get("title"),
        "entreprise": x.get("companyName"), "lieu": ", ".join(restr) if restr else "Worldwide",
        "zones": zones(", ".join(restr)) if restr else ["monde"],
        "type": type_contrat(x.get("employmentType")),
        "categorie": categorie_offre(x.get("title"), x.get("parentCategories") or [], (x.get("categories") or [])[:3]),
        "salaire": salaire(x.get("minSalary"), x.get("maxSalary"), x.get("currency"), x.get("salaryPeriod") or "annual"),
        "tags": x.get("parentCategories"), "date": date_iso(x.get("pubDate")),
        "expire": date_iso(x.get("expiryDate")), "url": x.get("applicationLink") or x.get("guid"),
        "description": x.get("description") or x.get("excerpt")})


def collecte_himalayas():
    sortie = []
    # 1) Offres ouvertes au monde entier (la recherche se pagine par « page », à partir de 1).
    for page in range(5):
        if page:
            _pause(DELAI_PAGES)
        j = _json(f"https://himalayas.app/jobs/api/search?worldwide=true&page={page + 1}")
        jobs = [x for x in (j.get("jobs") or []) if isinstance(x, dict)]
        sortie += [_himalayas_offre(x) for x in jobs]
        if not jobs or (page + 1) * 20 >= int(j.get("totalCount") or 0):
            break
    # 2) Dernières offres toutes zones (Europe, Amérique…).
    curseur = None
    for _page in range(3):
        _pause(DELAI_PAGES)
        suite = f"&cursor={urllib.parse.quote(str(curseur))}" if curseur else ""
        j = _json(f"https://himalayas.app/jobs/api?limit=20{suite}")
        sortie += [_himalayas_offre(x) for x in (j.get("jobs") or []) if isinstance(x, dict)]
        curseur = j.get("nextCursor")
        if not curseur:
            break
    return sortie


def collecte_jobicy():
    j = _json("https://jobicy.com/api/v2/remote-jobs?count=100&geo=anywhere")
    return [offre({
        "source": "jobicy", "id": x.get("id"), "titre": x.get("jobTitle"), "entreprise": x.get("companyName"),
        "lieu": x.get("jobGeo"), "type": type_contrat(x.get("jobType") or []),
        "categorie": categorie_offre(x.get("jobTitle"), x.get("jobIndustry") or []),
        "salaire": salaire(x.get("annualSalaryMin"), x.get("annualSalaryMax"), x.get("salaryCurrency"), "annual"),
        "tags": x.get("jobIndustry"), "date": date_iso(x.get("pubDate")), "url": x.get("url"),
        "description": x.get("jobDescription") or x.get("jobExcerpt")}) for x in (j.get("jobs") or [])
        if isinstance(x, dict)]


def _balise(item, nom):
    m = re.search(rf"<{nom}(?:\s[^>]*)?>([\s\S]*?)</{nom}>", item)
    if not m:
        return ""
    valeur = re.sub(r"^\s*<!\[CDATA\[|\]\]>\s*$", "", m.group(1))
    return html.unescape(valeur).strip()


def collecte_wwr():
    """We Work Remotely : flux RSS public (« attribute the links back to We Work Remotely »)."""
    xml = _telecharger("https://weworkremotely.com/remote-jobs.rss", "application/rss+xml").decode("utf-8", "replace")
    if "<rss" not in xml[:2000] and "<item>" not in xml:
        raise ErreurSource("flux RSS illisible")
    sortie = []
    for item in re.findall(r"<item>([\s\S]*?)</item>", xml):
        complet = _balise(item, "title")              # « Entreprise: Poste »
        i = complet.find(": ")
        region = _balise(item, "region")
        monde = bool(re.search(r"anywhere", region, re.I))
        sortie.append(offre({
            "source": "wwr", "id": _balise(item, "guid") or _balise(item, "link"),
            "titre": complet[i + 2:] if i > 0 else complet, "entreprise": complet[:i] if i > 0 else None,
            "lieu": region if monde else " – ".join(x for x in (region, _balise(item, "country")) if x),
            "zones": ["monde"] if monde else zones(region), "type": type_contrat(_balise(item, "type")),
            "categorie": categorie_offre(complet[i + 2:] if i > 0 else complet, _balise(item, "category")), "tags": [_balise(item, "category")],
            "date": date_iso(_balise(item, "pubDate")), "url": _balise(item, "link"),
            "description": _balise(item, "description")}))
    return sortie


COLLECTEURS = {"remotive": collecte_remotive, "remoteok": collecte_remoteok, "himalayas": collecte_himalayas,
               "jobicy": collecte_jobicy, "wwr": collecte_wwr}


# ---------------------------------------------------------------------------
# Fichiers
# ---------------------------------------------------------------------------
def _lire():
    d = config.lire_donnees(NOM, {})
    if not isinstance(d, dict):
        d = {}
    d.setdefault("recherches", [])
    for cle in ("suivi", "vues", "masquees", "alertes"):
        if not isinstance(d.get(cle), dict):
            d[cle] = {}
    if not isinstance(d.get("sources_off"), list):
        d["sources_off"] = []
    return d


def _ecrire(d):
    config.ecrire_donnees(NOM, d)


def _lire_offres():
    c = config.lire_donnees(NOM_OFFRES, {})
    if not isinstance(c, dict):
        c = {}
    if not isinstance(c.get("sources"), dict):
        c["sources"] = {}
    if not isinstance(c.get("offres"), list):
        c["offres"] = []
    return c


def _ecrire_offres(c):
    config.ecrire_donnees(NOM_OFFRES, c)


def _heure(texte):
    try:
        return datetime.datetime.fromisoformat(str(texte))
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Collecte
# ---------------------------------------------------------------------------
def sources_actives(d=None):
    d = d or _lire()
    return [s for s in SOURCES if s not in d["sources_off"]]


def prochaine_collecte(etat):
    """Le moment où la source pourra être interrogée de nouveau (None : tout de suite)."""
    if not etat:
        return None
    if etat.get("ok") is False:
        essai = _heure(etat.get("essai"))
        return essai + ATTENTE_ECHEC if essai else None
    derniere = _heure(etat.get("derniere"))
    return derniere + INTERVALLE if derniere else None


def source_due(etat, a_l_heure=None):
    quand = prochaine_collecte(etat)
    return quand is None or (a_l_heure or maintenant()) >= quand


def _encore_valide(o, jour):
    if o.get("expire") and o["expire"] < jour.isoformat():
        return False
    if o.get("date") and o["date"] < (jour - datetime.timedelta(days=MAX_JOURS)).isoformat():
        return False
    return True


def collecter():
    """Interroge les sources actives qui sont dues (en parallèle ; une source
    en erreur n'empêche pas les autres). Renvoie {collectees, erreurs}."""
    with _verrou_collecte:
        a_l_heure = maintenant()
        jour = a_l_heure.date()
        with _verrou:
            actives = sources_actives()
            cache = _lire_offres()
        dues = [s for s in actives if source_due(cache["sources"].get(s), a_l_heure)]
        resultats = {}
        if dues:
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(dues)) as pool:
                futurs = {s: pool.submit(COLLECTEURS[s]) for s in dues}
                for s, f in futurs.items():
                    try:
                        resultats[s] = [o for o in f.result() if o]
                    except Exception as e:  # noqa: BLE001 (une source en panne n'arrête pas les autres)
                        resultats[s] = e
        with _verrou:
            cache = _lire_offres()
            horodatage = a_l_heure.isoformat()
            erreurs = {}
            for s, r in resultats.items():
                ancien = cache["sources"].get(s) or {}
                if isinstance(r, Exception):
                    erreurs[s] = str(r)[:200] or r.__class__.__name__
                    cache["sources"][s] = {**ancien, "essai": horodatage, "ok": False, "erreur": erreurs[s]}
                    continue
                vues, propres = set(), []
                for o in sorted(r, key=lambda o: o.get("date") or "", reverse=True):
                    if o["id"] in vues or not _encore_valide(o, jour):
                        continue
                    vues.add(o["id"])
                    propres.append(o)
                propres = propres[:MAX_OFFRES_SOURCE]
                cache["offres"] = [o for o in cache["offres"] if o.get("source") != s] + propres
                cache["sources"][s] = {"derniere": horodatage, "essai": horodatage, "ok": True, "erreur": "",
                                       "nombre": len(propres)}
            cache["offres"] = [o for o in cache["offres"] if o.get("source") in SOURCES and _encore_valide(o, jour)]
            if resultats:
                _ecrire_offres(cache)
        return {"collectees": sorted(s for s, r in resultats.items() if not isinstance(r, Exception)),
                "erreurs": erreurs if resultats else {}}


def collecte_due():
    """Vrai si au moins une source active peut être interrogée maintenant."""
    with _verrou:
        actives = sources_actives()
        cache = _lire_offres()
    a_l_heure = maintenant()
    return any(source_due(cache["sources"].get(s), a_l_heure) for s in actives)


def _collecter_en_fond():
    if not _verrou_collecte.acquire(blocking=False):
        return
    _verrou_collecte.release()
    try:
        collecter()
    except Exception:  # noqa: BLE001 (silencieux : la page montre l'état des sources)
        pass


def lancer_collecte_fond():
    """Pour la bulle : collecte en fond si une recherche existe et qu'une source est due."""
    with _verrou:
        if not _lire()["recherches"]:
            return False
    if _verrou_collecte.locked() or not collecte_due():
        return False
    threading.Thread(target=_collecter_en_fond, daemon=True, name="missions-collecte").start()
    return True


# ---------------------------------------------------------------------------
# Recherches enregistrées
# ---------------------------------------------------------------------------
def _mots(valeur):
    if isinstance(valeur, str):
        valeur = re.split(r"[,;\n]", valeur)
    propres, vus = [], set()
    for m in valeur or []:
        m = " ".join(str(m or "").split())[:MAX_MOT]
        if m and norm(m) not in vus:
            vus.add(norm(m))
            propres.append(m)
    return propres[:MAX_MOTS]


def _sous_liste(valeur, possibles):
    if isinstance(valeur, str):
        valeur = [valeur]
    return [x for x in possibles if x in (valeur or [])]


def _entier(valeur, nom, mini, maxi, defaut):
    if valeur in (None, ""):
        return defaut
    try:
        n = int(float(str(valeur).replace(",", ".").replace(" ", "")))
    except (TypeError, ValueError):
        raise ValueError(f"{nom} invalide.") from None
    if not mini <= n <= maxi:
        raise ValueError(f"{nom} : de {mini} à {maxi}.")
    return n


def valider_recherche(b):
    """Une recherche propre à partir de ce qu'envoie la page. ValueError sinon."""
    if not isinstance(b, dict):
        raise ValueError("Recherche invalide.")
    nom = " ".join(str(b.get("nom") or "").split())[:MAX_NOM]
    if not nom:
        raise ValueError("Indiquez un nom pour la recherche.")
    devise = str(b.get("devise") or "USD").strip().upper()
    if not re.fullmatch(r"[A-Z]{3}", devise):
        raise ValueError("Devise invalide (code à trois lettres, ex. EUR).")
    niveau = b.get("niveau") or "senior"
    if niveau not in NIVEAUX:
        raise ValueError("Niveau inconnu.")
    periode = b.get("periode") or "an"
    if periode not in PERIODES:
        raise ValueError("Période inconnue.")
    r = {
        "nom": nom,
        "domaines": _sous_liste(b.get("domaines"), DOMAINES),
        "types": _sous_liste(b.get("types"), TYPES),
        "zones": _sous_liste(b.get("zones"), ZONES),
        "niveau": niveau,
        "salaire_min": _entier(b.get("salaire_min"), "Salaire minimum", 0, 10 ** 8, None) or None,
        "devise": devise, "periode": periode,
        "garder_sans_salaire": b.get("garder_sans_salaire") is not False,
        "importants": _mots(b.get("importants")),
        "utiles": _mots(b.get("utiles")),
        "eviter": _mots(b.get("eviter")),
        "score_min": _entier(b.get("score_min"), "Score minimum", -20, 100, SCORE_DEFAUT),
    }
    if not r["domaines"] and not r["importants"]:
        raise ValueError("Choisissez au moins un domaine ou un mot-clé important.")
    if not r["types"]:
        raise ValueError("Choisissez au moins un type de contrat.")
    if not r["zones"]:
        raise ValueError("Choisissez au moins une zone.")
    return r


def _trouver_recherche(d, ident):
    r = next((x for x in d["recherches"] if x.get("id") == ident), None)
    if r is None:
        raise ValueError("Recherche introuvable.")
    return r


def enregistrer_recherche(b):
    """Crée (sans id) ou modifie (avec id) une recherche. Renvoie la recherche."""
    b = b or {}
    with _verrou:
        d = _lire()
        if b.get("id"):
            r = _trouver_recherche(d, b["id"])
            r.update(valider_recherche(b))
        else:
            if len(d["recherches"]) >= MAX_RECHERCHES:
                raise ValueError(f"{MAX_RECHERCHES} recherches au plus.")
            r = {"id": uuid.uuid4().hex[:10], **valider_recherche(b), "cree": maintenant().isoformat()}
            d["recherches"].append(r)
        _ecrire(d)
        return dict(r)


def supprimer_recherche(ident):
    with _verrou:
        d = _lire()
        _trouver_recherche(d, ident)
        d["recherches"] = [r for r in d["recherches"] if r.get("id") != ident]
        d["vues"].pop(ident, None)
        d["alertes"].pop(ident, None)
        _ecrire(d)
        return True


# ---------------------------------------------------------------------------
# Import d'un profil.json (format du site « métiers en tension »)
# ---------------------------------------------------------------------------
_TYPES_PROFIL = {"freelance": "freelance", "contrat": "contrat", "temps-plein": "temps_plein",
                 "temps_plein": "temps_plein", "temps-partiel": "temps_partiel", "temps_partiel": "temps_partiel",
                 "stage": "stage"}


def _poids(valeur):
    try:
        return float(valeur)
    except (TypeError, ValueError):
        return None


def recherche_depuis_profil(p):
    """profil.json → champs d'une recherche : motsCles et techs (poids ≥ 4 →
    importants, sinon utiles), motsAEviter → à éviter, zones, bonusType > 0 →
    types, experienceMaxSouhaitee → niveau, scoreMinimum."""
    if not isinstance(p, dict):
        raise ValueError("Ce fichier n'est pas un profil de recherche.")
    importants, utiles, eviter = [], [], []
    for cle in ("motsCles", "techs"):
        bloc = p.get(cle)
        for mot, poids in (bloc.items() if isinstance(bloc, dict) else []):
            n = _poids(poids)
            if n is None or not str(mot).strip():
                continue
            (importants if n >= 4 else utiles if n > 0 else eviter).append(str(mot))
    bloc = p.get("motsAEviter")
    eviter += [str(m) for m in (bloc if isinstance(bloc, (dict, list)) else []) if str(m).strip()]
    bonus = p.get("bonusType") if isinstance(p.get("bonusType"), dict) else {}
    types = [_TYPES_PROFIL[t] for t, n in bonus.items() if t in _TYPES_PROFIL and (_poids(n) or 0) > 0]
    zs = [z for z in (p.get("zones") or []) if z in ZONES] if isinstance(p.get("zones"), list) else []
    exp = _poids(p.get("experienceMaxSouhaitee"))
    niveau = "senior" if exp is None else "debutant" if exp <= 2 else "confirme" if exp <= 5 else "senior"
    importants = _mots(importants)
    vus = {norm(m) for m in importants}
    utiles = [m for m in _mots(utiles) if norm(m) not in vus]
    score = _poids(p.get("scoreMinimum"))
    return {"nom": _texte("Mon profil"), "domaines": [], "types": list(dict.fromkeys(types)) or list(TYPES_DEFAUT),
            "zones": zs or ["monde"], "niveau": niveau, "importants": importants, "utiles": utiles,
            "eviter": _mots(eviter), "score_min": int(score) if score is not None else SCORE_DEFAUT,
            "garder_sans_salaire": True}


def importer_profil(chemin=None, profil=None):
    """Crée (ou remplace) la recherche « Mon profil » à partir d'un profil.json
    (chemin d'un fichier, ou son contenu déjà lu)."""
    if profil is None:
        chemin = os.path.normpath(str(chemin or "").strip().strip('"'))
        if not chemin or chemin == "." or not os.path.isfile(chemin):
            raise ValueError("Fichier introuvable.")
        if os.path.getsize(chemin) > MAX_PROFIL:
            raise ValueError("Fichier trop gros pour un profil.")
        try:
            with open(chemin, encoding="utf-8-sig") as f:
                profil = json.load(f)
        except (ValueError, UnicodeDecodeError):
            raise ValueError("Ce fichier n'est pas un profil JSON valide.") from None
    champs = recherche_depuis_profil(profil)
    if not champs["importants"]:
        raise ValueError("Ce profil n'a aucun mot-clé important (poids 4 ou plus).")
    with _verrou:
        d = _lire()
        existante = next((r for r in d["recherches"] if r.get("nom") == champs["nom"]), None)
    return enregistrer_recherche({**champs, "id": existante["id"]} if existante else champs)


# ---------------------------------------------------------------------------
# Filtres et notation
# ---------------------------------------------------------------------------
def _par_an(montant, periode):
    return montant * PAR_AN[periode] if periode in PAR_AN else None


def salaire_suffisant(o, r):
    """True / False si comparable (montant chiffré, même devise, période connue), None sinon."""
    s = o.get("salaire")
    if not r.get("salaire_min") or not s or s.get("devise") != r.get("devise"):
        return None
    montant = s.get("max") or s.get("min")
    offre_an = _par_an(montant, s.get("periode") or "an") if montant else None
    voulu_an = _par_an(r["salaire_min"], r.get("periode") or "an")
    if offre_an is None or voulu_an is None:
        return None
    return offre_an >= voulu_an


def evaluer(o, r):
    """{score, raisons, evites} si l'offre passe les filtres de la recherche, sinon None."""
    if o.get("hors_teletravail"):
        return None
    if o.get("type") not in r["types"]:
        return None
    if not set(o.get("zones") or ["inconnue"]) & set(r["zones"]):
        return None
    maxi = NIVEAUX.get(r.get("niveau") or "senior")
    if maxi is not None and o.get("experience") and o["experience"] > maxi:
        return None
    if r.get("salaire_min"):
        ok = salaire_suffisant(o, r)
        if ok is False or (ok is None and not r.get("garder_sans_salaire", True)):
            return None
    titre = norm(o.get("titre"))
    texte = norm(" ".join([o.get("titre") or "", *(o.get("tags") or [])]))
    techs = {norm(t) for t in o.get("techs") or []}
    score, raisons, evites = 0, [], []
    importants_trouves = False
    for mots, poids in ((r["importants"], 5), (r["utiles"], 2)):
        for mot in mots:
            if contient_mot(texte, mot) or norm(mot) in techs:
                score += poids
                raisons.append(mot)
                importants_trouves = importants_trouves or poids == 5
    for mot in r["eviter"]:
        if contient_mot(titre, mot):
            score -= 5
            evites.append(mot)
    domaine = o.get("categorie") in r["domaines"]
    if not domaine and not importants_trouves:
        return None
    if domaine:
        score += 3
    pertinent = score >= PERTINENCE
    if pertinent:
        score += {"freelance": 2, "contrat": 1}.get(o.get("type"), 0)
    else:
        score = min(score, 0)
    return {"score": score, "raisons": raisons[:8], "evites": evites, "domaine": domaine}


def _cle_doublon(o):
    return norm(o.get("titre")) + "|" + norm(o.get("entreprise"))


def _offres_visibles(d, cache, jour):
    """Les offres en cache encore valables, des sources actives, sans doublons ni masquées."""
    actives = set(sources_actives(d))
    vues, sortie = set(), []
    for o in sorted(cache["offres"], key=lambda o: o.get("date") or "", reverse=True):
        if o.get("source") not in actives or o.get("id") in d["masquees"] or not _encore_valide(o, jour):
            continue
        cle = _cle_doublon(o)
        if cle in vues:
            continue
        vues.add(cle)
        sortie.append(o)
    return sortie


def selection(r, offres, d):
    """Les offres retenues pour une recherche, triées par score puis date."""
    vues = d["vues"].get(r["id"]) or {}
    choisies = []
    for o in offres:
        e = evaluer(o, r)
        if e is None or e["score"] < r["score_min"]:
            continue
        choisies.append({**o, **e, "nouvelle": o["id"] not in vues})
    choisies.sort(key=lambda o: (o.get("date") or ""), reverse=True)
    choisies.sort(key=lambda o: o["score"], reverse=True)
    return choisies


def mots_recherche(r):
    """Les mots-clés d'une recherche pour les sites à chercher à la main."""
    mots = r["importants"][:3] or r["utiles"][:3]
    if not mots:
        anglais = {"dev": "developer", "data": "data", "design": "designer", "marketing": "marketing",
                   "redaction": "writer", "support": "customer support", "assistanat": "virtual assistant",
                   "finance": "project manager", "ventes": "sales"}
        mots = [anglais[x] for x in r["domaines"][:2]]
    return " ".join(mots)


def liens_manuels(r):
    q = urllib.parse.quote_plus(mots_recherche(r))
    return [{"site": s, "nom": nom, "url": modele.format(q=q)} for s, (nom, modele) in SITES_MANUELS.items()]


# ---------------------------------------------------------------------------
# Lecture pour la page
# ---------------------------------------------------------------------------
def _etat_sources(d, cache):
    a_l_heure = maintenant()
    sortie = []
    for s, info in SOURCES.items():
        e = cache["sources"].get(s) or {}
        quand = prochaine_collecte(e)
        sortie.append({"id": s, "nom": info["nom"], "url": info["url"], "active": s not in d["sources_off"],
                       "derniere": e.get("derniere"), "essai": e.get("essai"), "ok": e.get("ok"),
                       "erreur": e.get("erreur") or "", "nombre": e.get("nombre") or 0,
                       "prochaine": quand.isoformat() if quand and quand > a_l_heure else None})
    return sortie


def liste():
    """Tout ce qu'il faut à la page, sauf le détail des offres (voir offres())."""
    a_l_heure = maintenant()
    with _verrou:
        d = _lire()
        cache = _lire_offres()
    offres = _offres_visibles(d, cache, a_l_heure.date())
    recherches = []
    for r in d["recherches"]:
        choisies = selection(r, offres, d)
        recherches.append({**r, "total": len(choisies), "nouvelles": sum(1 for o in choisies if o["nouvelle"])})
    actives = sources_actives(d)
    return {"recherches": recherches, "suivi": sorted(d["suivi"].values(), key=lambda x: x.get("maj") or "",
                                                      reverse=True),
            "sources": _etat_sources(d, cache), "nombre_offres": len(offres),
            "a_collecter": any(source_due(cache["sources"].get(s), a_l_heure) for s in actives),
            "masquees": len(d["masquees"]), "profil": config.lire().get("profil") or "",
            "modeles": MODELES, "aujourdhui": a_l_heure.date().isoformat(), "maintenant": a_l_heure.isoformat()}


def offres(ident):
    """Les offres d'une recherche (au plus MAX_AFFICHEES) et les liens de recherche manuelle."""
    a_l_heure = maintenant()
    with _verrou:
        d = _lire()
        r = _trouver_recherche(d, ident)
        cache = _lire_offres()
    choisies = selection(r, _offres_visibles(d, cache, a_l_heure.date()), d)
    suivi = d["suivi"]
    for o in choisies:
        o["suivi"] = (suivi.get(o["id"]) or {}).get("statut")
    return {"recherche": r, "offres": choisies[:MAX_AFFICHEES], "total": len(choisies),
            "liens": liens_manuels(r), "aujourdhui": a_l_heure.date().isoformat()}


def marquer_vues(ident, ids):
    """Les offres montrées passent dans « Déjà vues » (à la prochaine ouverture)."""
    with _verrou:
        d = _lire()
        _trouver_recherche(d, ident)
        vues = d["vues"].setdefault(ident, {})
        jour = maintenant().date().isoformat()
        nouveau = False
        for oid in (ids or [])[:MAX_AFFICHEES]:
            if isinstance(oid, str) and oid not in vues:
                vues[oid] = jour
                nouveau = True
        if nouveau:
            if len(vues) > MAX_VUES:
                garder = sorted(vues.items(), key=lambda x: x[1])[-MAX_VUES:]
                d["vues"][ident] = dict(garder)
            _ecrire(d)
        return True


def masquer(ident):
    with _verrou:
        d = _lire()
        if not isinstance(ident, str) or not ident:
            raise ValueError("Offre introuvable.")
        d["masquees"][ident] = maintenant().date().isoformat()
        if len(d["masquees"]) > MAX_VUES:
            d["masquees"] = dict(sorted(d["masquees"].items(), key=lambda x: x[1])[-MAX_VUES:])
        _ecrire(d)
        return True


def demasquer(ident=None):
    """Réaffiche une offre masquée (ou toutes)."""
    with _verrou:
        d = _lire()
        n = len(d["masquees"])
        if ident:
            d["masquees"].pop(ident, None)
        else:
            d["masquees"] = {}
        _ecrire(d)
        return n - len(d["masquees"])


def changer_source(ident, actif):
    if ident not in SOURCES:
        raise ValueError("Source inconnue.")
    with _verrou:
        d = _lire()
        off = [s for s in d["sources_off"] if s != ident]
        if not actif:
            off.append(ident)
        if len(off) == len(SOURCES):
            raise ValueError("Gardez au moins une source active.")
        d["sources_off"] = off
        _ecrire(d)
        return True


def _offre_par_id(ident):
    with _verrou:
        cache = _lire_offres()
        d = _lire()
    o = next((x for x in cache["offres"] if x.get("id") == ident), None)
    return o or d["suivi"].get(ident)


def ouvrir(donnees):
    """Ouvre une offre (par son identifiant) ou une recherche manuelle (site +
    recherche) dans le navigateur. Jamais une adresse quelconque venue de la page."""
    if donnees.get("site"):
        if donnees["site"] not in SITES_MANUELS:
            raise ValueError("Site inconnu.")
        with _verrou:
            r = _trouver_recherche(_lire(), donnees.get("recherche_id"))
        url = next(x["url"] for x in liens_manuels(r) if x["site"] == donnees["site"])
    else:
        o = _offre_par_id(donnees.get("id"))
        if not o or not re.match(r"^https?://\S+$", str(o.get("url") or "")):
            raise ValueError("Offre introuvable.")
        url = o["url"]
    systeme.ouvrir(url)
    return {"ok": True, "url": url}


# ---------------------------------------------------------------------------
# Suivi des candidatures
# ---------------------------------------------------------------------------
def _jour(valeur, nom):
    valeur = str(valeur or "").strip()[:10]
    if not valeur:
        return ""
    try:
        return datetime.date.fromisoformat(valeur).isoformat()
    except ValueError:
        raise ValueError(f"{nom} invalide.") from None


def enregistrer_suivi(b):
    """Ajoute ou modifie une candidature. Une offre du cache est recopiée
    (titre, entreprise, lien, source) : le suivi reste après son expiration.
    Sans offre connue : candidature saisie à la main (titre obligatoire)."""
    if not isinstance(b, dict):
        raise ValueError("Candidature invalide.")
    statut = b.get("statut") or "a_voir"
    if statut not in STATUTS:
        raise ValueError("Statut inconnu.")
    with _verrou:
        d = _lire()
        cache = _lire_offres()
        ident = str(b.get("id") or "")
        s = d["suivi"].get(ident)
        if s is None:
            o = next((x for x in cache["offres"] if x.get("id") == ident), None) if ident else None
            if o:
                s = {"id": ident, "titre": o["titre"], "entreprise": o.get("entreprise") or "", "url": o["url"],
                     "source": o["source"]}
            else:
                titre = " ".join(str(b.get("titre") or "").split())[:200]
                if not titre:
                    raise ValueError("Indiquez le poste.")
                url = str(b.get("url") or "").strip()[:500]
                if url and not re.match(r"^https?://[^\s/]+", url, re.I):
                    raise ValueError("Lien invalide : il doit commencer par https://")
                s = {"id": "manuel-" + uuid.uuid4().hex[:10], "titre": titre,
                     "entreprise": " ".join(str(b.get("entreprise") or "").split())[:120], "url": url,
                     "source": "manuel"}
            if len(d["suivi"]) >= MAX_SUIVI:
                raise ValueError(f"{MAX_SUIVI} candidatures au plus.")
            s["recherche_id"] = str(b.get("recherche_id") or "")[:20]
            s["cree"] = maintenant().isoformat()
        elif s.get("source") == "manuel":
            if "titre" in b and " ".join(str(b.get("titre") or "").split()):
                s["titre"] = " ".join(str(b["titre"]).split())[:200]
            if "entreprise" in b:
                s["entreprise"] = " ".join(str(b.get("entreprise") or "").split())[:120]
        ancien = s.get("statut")
        s["statut"] = statut
        if "date" in b:
            s["date"] = _jour(b.get("date"), "Date")
        if not s.get("date") or (ancien and ancien != statut and "date" not in b):
            s["date"] = maintenant().date().isoformat()
        if "note" in b:
            s["note"] = str(b.get("note") or "").strip()[:MAX_NOTE]
        if "relance" in b:
            s["relance"] = _jour(b.get("relance"), "Date de relance")
        if "tache_id" in b:
            s["tache_id"] = str(b.get("tache_id") or "")[:40]
            s["relance_tache"] = s.get("relance") or ""
        s["maj"] = maintenant().isoformat()
        d["suivi"][s["id"]] = s
        _ecrire(d)
        return dict(s)


def supprimer_suivi(ident):
    with _verrou:
        d = _lire()
        if d["suivi"].pop(ident, None) is None:
            raise ValueError("Candidature introuvable.")
        _ecrire(d)
        return True


# ---------------------------------------------------------------------------
# Accueil et bulle
# ---------------------------------------------------------------------------
def _nouvelles_par_recherche(d, cache, jour):
    offres_ok = _offres_visibles(d, cache, jour)
    return [(r, [o for o in selection(r, offres_ok, d) if o["nouvelle"]]) for r in d["recherches"]]


def accueil():
    """Pour la carte de l'Accueil : nouvelles offres par recherche et les 3 meilleures."""
    with _verrou:
        d = _lire()
        cache = _lire_offres()
    parts = _nouvelles_par_recherche(d, cache, maintenant().date())
    meilleures = {}
    for r, nouvelles in parts:
        for o in nouvelles:
            if o["id"] not in meilleures or o["score"] > meilleures[o["id"]]["score"]:
                meilleures[o["id"]] = {"id": o["id"], "titre": o["titre"], "entreprise": o.get("entreprise"),
                                       "score": o["score"], "source": o["source"], "recherche_id": r["id"],
                                       "date": o.get("date")}
    top = sorted(meilleures.values(), key=lambda o: (o["score"], o.get("date") or ""), reverse=True)[:3]
    return {"recherches": [{"id": r["id"], "nom": r["nom"], "nouvelles": len(n)} for r, n in parts if n],
            "meilleures": top}


def _alertes_calculees(d, cache, a_l_heure):
    jour = a_l_heure.date().isoformat()
    alertes = []
    for r, nouvelles in _nouvelles_par_recherche(d, cache, a_l_heure.date()):
        deja = d["alertes"].get(r["id"]) or {}
        if deja.get("le") == jour:
            continue
        connues = set(deja.get("ids") or [])
        fraiches = [o for o in nouvelles if o["id"] not in connues]
        if not fraiches:
            continue
        o = fraiches[0]
        if o.get("entreprise"):
            detail = _texte("{titre} chez {entreprise} ({score} points)", titre=o["titre"],
                            entreprise=o["entreprise"], score=o["score"])
        else:
            detail = _texte("{titre} ({score} points)", titre=o["titre"], score=o["score"])
        titre = (_texte("{n} nouvelles offres : {nom}", n=len(fraiches), nom=r["nom"]) if len(fraiches) > 1
                 else _texte("Nouvelle offre : {nom}", nom=r["nom"]))
        alertes.append({"id": f"{r['id']}:{jour}", "titre": titre, "detail": detail,
                        "_ids": [x["id"] for x in fraiches]})
    return alertes


def alertes_dues():
    """Les alertes pas encore vues : [{id, titre, detail}]. Lance aussi la
    collecte en fond quand une source est due (au plus deux fois par jour)."""
    try:
        lancer_collecte_fond()
    except Exception:  # noqa: BLE001 (la bulle ne doit jamais tomber pour ça)
        pass
    with _verrou:
        d = _lire()
        cache = _lire_offres()
    return [{k: v for k, v in a.items() if k != "_ids"} for a in _alertes_calculees(d, cache, maintenant())]


def marquer_alerte(ident):
    """Alerte vue : plus d'autre alerte aujourd'hui pour cette recherche, et
    ces offres ne relancent plus d'alerte. Renvoie True si elle était due."""
    with _verrou:
        d = _lire()
        cache = _lire_offres()
        a_l_heure = maintenant()
        alerte = next((a for a in _alertes_calculees(d, cache, a_l_heure) if a["id"] == ident), None)
        if alerte is None:
            return False
        rid = ident.split(":", 1)[0]
        anciens = (d["alertes"].get(rid) or {}).get("ids") or []
        d["alertes"][rid] = {"le": a_l_heure.date().isoformat(), "ids": (anciens + alerte["_ids"])[-MAX_VUES:]}
        _ecrire(d)
        return True


# ---------------------------------------------------------------------------
# Routes de la page
# ---------------------------------------------------------------------------
def _route_actualiser(_d):
    r = collecter()
    return {**r, **liste()}


ROUTES = {
    "liste": lambda d: liste(),
    "offres": lambda d: offres(d.get("recherche_id")),
    "actualiser": _route_actualiser,
    "voir": lambda d: {"ok": marquer_vues(d.get("recherche_id"), d.get("ids"))},
    "masquer": lambda d: {"ok": masquer(d.get("id"))},
    "demasquer": lambda d: {"reaffichees": demasquer(d.get("id"))},
    "ouvrir": ouvrir,
    "sources": lambda d: {"ok": changer_source(d.get("id"), bool(d.get("actif")))},
    "recherche/enregistrer": lambda d: enregistrer_recherche(d.get("recherche")),
    "recherche/supprimer": lambda d: {"ok": supprimer_recherche(d.get("id"))},
    "importer_profil": lambda d: importer_profil(d.get("chemin"), d.get("profil")),
    "suivi/enregistrer": lambda d: enregistrer_suivi(d.get("suivi")),
    "suivi/supprimer": lambda d: {"ok": supprimer_suivi(d.get("id"))},
    "accueil": lambda d: accueil(),
    "alertes": lambda d: {"alertes": alertes_dues()},
    "marquer_alerte": lambda d: {"ok": marquer_alerte(d.get("id"))},
}
