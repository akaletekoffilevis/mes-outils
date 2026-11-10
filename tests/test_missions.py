# -*- coding: utf-8 -*-
"""Tests de l'application Missions : normalisation des cinq sources
(réponses simulées, aucun appel réseau, erreurs et flux RSS compris),
notation et filtres (domaines, types, zones, niveau, salaire, mots), délai
de collecte, offres expirées, import d'un profil.json, suivi des
candidatures, alertes de la bulle et routes."""
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # aide.py, quel que soit le lancement

from aide import ConfigTemporaire, ServeurTest  # noqa: E402

import config  # noqa: E402
import missions  # noqa: E402

DT = datetime.datetime
WEB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outil", "web")


def epoch(texte):
    return int(DT.fromisoformat(texte).replace(tzinfo=datetime.timezone.utc).timestamp())


class Horloge:
    """Heure simulée : avancer(heures=…, minutes=…, jours=…)."""

    def __init__(self, depart="2026-03-04T09:00:00"):
        self.moment = DT.fromisoformat(depart)

    def __call__(self):
        return self.moment

    def avancer(self, jours=0, heures=0, minutes=0):
        self.moment += datetime.timedelta(days=jours, hours=heures, minutes=minutes)


# ---------------------------------------------------------------------------
# Réponses simulées des cinq sources
# ---------------------------------------------------------------------------
def reponses():
    remotive = {"jobs": [
        {"id": 1, "url": "https://remotive.com/remote-jobs/software-dev/freelance-react-1?utm_source=x",
         "title": "Freelance React Developer", "company_name": "Exemple SA", "category": "Software Development",
         "tags": ["react", "typescript"], "job_type": "freelance", "publication_date": "2026-03-03T10:00:00",
         "candidate_required_location": "Worldwide", "salary": "$50 - $60 /hour",
         "description": "<p>Texte confidentiel : 3+ years of experience with React &amp; Node.js.</p>"},
        {"id": 2, "url": "https://remotive.com/remote-jobs/customer-support/agent-2", "title": "Customer Support Agent",
         "company_name": "Service Exemple", "category": "Customer Service", "tags": [], "job_type": "part_time",
         "publication_date": "2026-03-02T10:00:00", "candidate_required_location": "Europe, Africa",
         "salary": "", "description": "This is a hybrid role, two days a week in the office."},
    ]}
    remoteok = [
        {"legal": "Mention légale de la source"},
        {"id": "101", "position": "Python Backend Engineer", "company": "Société Test", "location": "USA",
         "tags": ["python", "backend"], "salary_min": 90000, "salary_max": 120000,
         "date": "2026-03-02T08:00:00+00:00", "url": "https://remoteok.com/remote-jobs/101",
         "description": "Python and Django. 6 years of experience required."},
    ]
    himalayas_monde = {"totalCount": 1, "jobs": [
        {"title": "Virtual Assistant", "companyName": "Aide Plus", "employmentType": "Part Time",
         "minSalary": "800", "maxSalary": "1200", "currency": "USD", "salaryPeriod": "monthly",
         "locationRestrictions": [], "categories": [], "parentCategories": ["Admin"],
         "pubDate": epoch("2026-03-03T12:00:00"), "expiryDate": epoch("2026-03-20T00:00:00"),
         "applicationLink": "https://himalayas.app/companies/aide-plus/jobs/virtual-assistant",
         "guid": "https://himalayas.app/companies/aide-plus/jobs/virtual-assistant", "description": "Email, agenda."},
        {"title": "Old Assistant", "companyName": "Expirée", "employmentType": "Part Time",
         "locationRestrictions": [], "pubDate": epoch("2026-02-10T12:00:00"), "expiryDate": epoch("2026-03-01T00:00:00"),
         "applicationLink": "https://himalayas.app/companies/expiree/jobs/old", "guid": "g-old"},
    ]}
    himalayas_flux = {"nextCursor": None, "jobs": [
        {"title": "Executive Assistant", "companyName": "Direction Exemple", "employmentType": "Full Time",
         "locationRestrictions": [{"name": "France"}, {"name": "Belgium"}], "parentCategories": ["Admin"],
         "pubDate": str(epoch("2026-03-01T12:00:00")),
         "applicationLink": "https://himalayas.app/companies/direction/jobs/ea", "guid": "g-ea"},
    ]}
    jobicy = {"jobs": [
        {"id": 501, "url": "https://jobicy.com/jobs/501-data-analyst", "jobTitle": "Data Analyst",
         "companyName": "Données & Co", "jobIndustry": ["Data Science"], "jobType": ["Full-Time"], "jobGeo": "Anywhere",
         "pubDate": "2026-03-01 12:00:00", "annualSalaryMin": 40000, "annualSalaryMax": 50000, "salaryCurrency": "EUR",
         "jobDescription": "SQL and Python."},
        {"id": 502, "url": "https://jobicy.com/jobs/502-ancienne", "jobTitle": "Ancienne offre",
         "companyName": "Vieux", "jobType": ["Full-Time"], "jobGeo": "Anywhere", "pubDate": "2025-12-01 12:00:00"},
    ]}
    rss = """<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>WWR</title>
<item><title><![CDATA[Studio Exemple: Freelance Copywriter &amp; Translator]]></title>
<region>Anywhere in the World</region><country></country><type>Contract</type><category>Copywriting</category>
<pubDate>Tue, 03 Mar 2026 10:00:00 +0000</pubDate>
<link>https://weworkremotely.com/remote-jobs/studio-exemple-freelance-copywriter</link>
<guid>https://weworkremotely.com/remote-jobs/studio-exemple-freelance-copywriter</guid>
<description><![CDATA[<p>Longs textes à écrire. 2 years of experience in copywriting.</p>]]></description></item>
<item><title>Sans lien</title><link>ftp://exemple.test</link></item>
</channel></rss>"""
    return {"remotive": remotive, "remoteok": remoteok, "himalayas_monde": himalayas_monde,
            "himalayas_flux": himalayas_flux, "jobicy": jobicy, "wwr": rss}


class Reseau:
    """Remplace missions._telecharger : réponses simulées, appels comptés,
    sources en panne au choix (pannes = {"jobicy"})."""

    def __init__(self):
        self.donnees = reponses()
        self.appels = []
        self.pannes = set()

    def cle(self, url):
        if "remotive.com" in url:
            return "remotive"
        if "remoteok.com" in url:
            return "remoteok"
        if "himalayas.app/jobs/api/search" in url:
            return "himalayas_monde"
        if "himalayas.app/jobs/api" in url:
            return "himalayas_flux"
        if "jobicy.com" in url:
            return "jobicy"
        if "weworkremotely.com" in url:
            return "wwr"
        raise AssertionError(f"adresse inattendue : {url}")

    def __call__(self, url, accept="application/json"):
        cle = self.cle(url)
        self.appels.append(cle)
        source = "himalayas" if cle.startswith("himalayas") else cle
        if source in self.pannes:
            raise missions.ErreurSource("HTTP 503")
        valeur = self.donnees[cle]
        if cle == "himalayas_monde" and "page=1" not in url:
            valeur = {"jobs": [], "totalCount": 1}
        return (valeur if isinstance(valeur, str) else json.dumps(valeur)).encode("utf-8")

    def sources_appelees(self):
        return sorted({"himalayas" if c.startswith("himalayas") else c for c in self.appels})


def recherche(**valeurs):
    base = {"nom": "Dev", "domaines": ["dev"], "types": ["freelance", "contrat", "temps_plein", "temps_partiel"],
            "zones": ["monde"], "niveau": "senior", "importants": [], "utiles": [], "eviter": [], "score_min": 3}
    base.update(valeurs)
    return missions.valider_recherche(base)


def offre(**valeurs):
    base = {"id": "remotive-1", "source": "remotive", "titre": "React Developer", "entreprise": "Exemple",
            "zones": ["monde"], "type": "freelance", "categorie": "dev", "tags": [], "date": "2026-03-03",
            "url": "https://exemple.test/1", "salaire": None}
    base.update(valeurs)
    return base


class Base(unittest.TestCase):
    """Données temporaires, heure simulée et réseau simulé."""

    def setUp(self):
        self.cfg = ConfigTemporaire({"outils": [], "langue": "fr", "profil": "developpeur"})
        self.cfg.__enter__()
        self.horloge = Horloge()
        self.reseau = Reseau()
        self.patchs = [mock.patch.object(missions, "maintenant", self.horloge),
                       mock.patch.object(missions, "_telecharger", self.reseau),
                       mock.patch.object(missions, "_pause", lambda s: None),
                       mock.patch.object(missions, "lancer_collecte_fond", lambda: False)]
        for p in self.patchs:
            p.start()

    def tearDown(self):
        for p in self.patchs:
            p.stop()
        self.cfg.__exit__(None, None, None)


# ---------------------------------------------------------------------------
# Normalisation
# ---------------------------------------------------------------------------
class TestNormalisation(unittest.TestCase):
    def test_type_zone_categorie(self):
        t = missions.type_contrat
        self.assertEqual([t("freelance"), t(["Contract"]), t("part_time"), t("Internship"), t("full_time"), t(None)],
                         ["freelance", "contrat", "temps_partiel", "stage", "temps_plein", "temps_plein"])
        z = missions.zones
        self.assertEqual(z("Worldwide"), ["monde"])
        self.assertEqual(z("Anywhere in the World"), ["monde"])
        self.assertEqual(z(""), ["inconnue"])
        self.assertEqual(z("Europe, Africa"), ["afrique", "europe"], "plusieurs zones possibles")
        self.assertEqual(z("EMEA"), ["afrique", "europe"])
        self.assertEqual(z("USA only"), ["amerique"])
        self.assertEqual(z("India, Philippines"), ["asie"])
        self.assertEqual(z("Madagascar"), ["afrique"])
        self.assertEqual(z("Warsaw"), ["autre"])
        c = missions.categorie
        self.assertEqual(c("Business Development Manager"), "ventes", "le développement commercial n'est pas du code")
        self.assertEqual(c("Executive Assistant"), "assistanat")
        self.assertEqual(c("Virtual Assistant (part-time)"), "assistanat")
        self.assertEqual(c("Office Manager"), "assistanat")
        self.assertEqual(c("Finance Admin"), "assistanat", "admin sort de la finance")
        self.assertEqual(c("Linux System Admin"), "dev", "un administrateur système reste du développement")
        self.assertEqual(c("Senior Accountant"), "finance")
        self.assertEqual(c("Project Manager"), "finance")
        self.assertEqual(c("German Interpreter (audio/video)"), "redaction")
        self.assertEqual(c("Video Editor"), "design")
        self.assertEqual(c("Customer Success Manager"), "support")
        self.assertEqual(c("Full Stack Developer"), "dev")
        self.assertEqual(c("Machine Learning Engineer"), "data")
        self.assertEqual(c("Chef cuisinier"), "autres")
        self.assertEqual(missions.categorie_offre("Health Expert", ["Customer Support"]), "support",
                         "titre muet : catégorie de la source")
        self.assertEqual(missions.categorie_offre("Marketing Designer", ["Sales and Marketing"]), "design",
                         "le titre l'emporte sur la catégorie du site")

    def test_dates_et_salaires(self):
        d = missions.date_iso
        self.assertEqual(d("2026-03-03T10:00:00"), "2026-03-03")
        self.assertEqual(d("Tue, 03 Mar 2026 10:00:00 +0000"), "2026-03-03")
        self.assertEqual(d(epoch("2026-03-03T12:00:00")), "2026-03-03")
        self.assertEqual(d(str(epoch("2026-03-03T12:00:00"))), "2026-03-03")
        self.assertEqual(d(epoch("2026-03-03T12:00:00") * 1000), "2026-03-03", "millisecondes")
        self.assertIsNone(d("n'importe quoi"))
        self.assertIsNone(d(None))
        s = missions.salaire_texte
        self.assertEqual(s("$60,000 - $80,000"), {"min": 60000, "max": 80000, "devise": "USD", "periode": "an"})
        self.assertEqual(s("40-50k EUR per year"), {"min": 40000, "max": 50000, "devise": "EUR", "periode": "an"})
        self.assertEqual(s("€35/hour"), {"min": 35, "max": 35, "devise": "EUR", "periode": "heure"})
        self.assertEqual(s("£3,000 monthly")["periode"], "mois")
        self.assertIsNone(s("70K-80K"), "sans devise : pas de montant comparable")
        self.assertIsNone(s("Competitive"))
        self.assertEqual(missions.salaire("3000", "6000", "usd", "monthly"),
                         {"min": 3000, "max": 6000, "devise": "USD", "periode": "mois"})
        self.assertIsNone(missions.salaire(None, 0, "USD"))
        self.assertIsNone(missions.salaire(100, 200, "dollars"))

    def test_analyse_et_mots(self):
        a = missions.analyser("<p>We use React, Node.js and PostgreSQL. 5+ years of professional experience.</p>")
        self.assertEqual(a, {"techs": ["React", "Node.js", "PostgreSQL"], "experience": 5})
        self.assertEqual(missions.analyser("JavaScript only")["techs"], ["JavaScript"], "Java n'est pas JavaScript")
        self.assertTrue(missions.analyser("This is a hybrid role in Paris.")["hors_teletravail"])
        self.assertTrue(missions.analyser("Work from our office three days a week.").get("hors_teletravail"))
        self.assertNotIn("hors_teletravail", missions.analyser("Very few office-based roles; no on-site work."),
                         "les négations ne comptent pas")
        self.assertEqual(missions.analyser(""), {})
        n = missions.norm
        self.assertTrue(missions.contient_mot(n("Senior Java Developer"), "java"))
        self.assertFalse(missions.contient_mot(n("JavaScript Developer"), "java"), "mot entier")
        self.assertTrue(missions.contient_mot(n("Développeur .NET / C#"), "c#"))
        self.assertTrue(missions.contient_mot(n("Développeur Odoo"), "developpeur"), "sans accents")
        self.assertTrue(missions.contient_mot(n("Full Stack Engineer"), "full stack"))


# ---------------------------------------------------------------------------
# Collecte
# ---------------------------------------------------------------------------
class TestCollecte(Base):
    def test_cinq_sources(self):
        r = missions.collecter()
        self.assertEqual(r, {"collectees": ["himalayas", "jobicy", "remoteok", "remotive", "wwr"], "erreurs": {}})
        cache = missions._lire_offres()
        par_id = {o["id"]: o for o in cache["offres"]}
        f = par_id["remotive-1"]
        self.assertEqual(f["url"], "https://remotive.com/remote-jobs/software-dev/freelance-react-1?utm_source=x",
                         "lien d'origine inchangé")
        self.assertEqual((f["type"], f["zones"], f["categorie"], f["experience"], f["techs"]),
                         ("freelance", ["monde"], "dev", 3, ["React", "Node.js"]))
        self.assertEqual(f["salaire"], {"min": 50, "max": 60, "devise": "USD", "periode": "heure"})
        self.assertTrue(par_id["remotive-2"]["hors_teletravail"])
        self.assertEqual(par_id["remotive-2"]["zones"], ["afrique", "europe"])
        p = par_id["remoteok-101"]
        self.assertEqual((p["zones"], p["experience"], p["salaire"]["max"], p["date"]), (["amerique"], 6, 120000, "2026-03-02"))
        va = next(o for o in cache["offres"] if o["titre"] == "Virtual Assistant")
        self.assertEqual((va["type"], va["categorie"], va["zones"], va["expire"], va["salaire"]["periode"]),
                         ("temps_partiel", "assistanat", ["monde"], "2026-03-20", "mois"))
        ea = next(o for o in cache["offres"] if o["titre"] == "Executive Assistant")
        self.assertEqual((ea["zones"], ea["lieu"], ea["date"]), (["europe"], "France, Belgium", "2026-03-01"))
        self.assertEqual(par_id["jobicy-501"]["salaire"], {"min": 40000, "max": 50000, "devise": "EUR", "periode": "an"})
        w = next(o for o in cache["offres"] if o["source"] == "wwr")
        self.assertEqual((w["titre"], w["entreprise"], w["type"], w["zones"], w["categorie"], w["experience"], w["date"]),
                         ("Freelance Copywriter & Translator", "Studio Exemple", "contrat", ["monde"], "redaction", 2,
                          "2026-03-03"))
        self.assertEqual(len([o for o in cache["offres"] if o["source"] == "wwr"]), 1, "lien non https écarté")
        titres = {o["titre"] for o in cache["offres"]}
        self.assertNotIn("Old Assistant", titres, "offre expirée retirée")
        self.assertNotIn("Ancienne offre", titres, "offre de plus de 60 jours retirée")
        with open(config.chemin_donnees("missions_offres"), encoding="utf-8") as fic:
            brut = fic.read()
        for morceau in ("Texte confidentiel", "Longs textes", "Email, agenda", "description"):
            self.assertNotIn(morceau, brut, "les descriptions ne sont jamais stockées")
        self.assertEqual(self.reseau.appels.count("himalayas_monde"), 1, "pagination arrêtée au total annoncé")

    def test_une_source_en_panne(self):
        self.reseau.pannes = {"jobicy"}
        r = missions.collecter()
        self.assertEqual(r["collectees"], ["himalayas", "remoteok", "remotive", "wwr"])
        self.assertEqual(r["erreurs"], {"jobicy": "HTTP 503"})
        etat = missions._lire_offres()["sources"]["jobicy"]
        self.assertEqual((etat["ok"], etat["erreur"]), (False, "HTTP 503"))
        # Échec : nouvel essai permis après 5 minutes, pas avant ; les autres attendent 12 heures.
        self.reseau.appels.clear()
        self.reseau.pannes = set()
        self.horloge.avancer(minutes=2)
        missions.collecter()
        self.assertEqual(self.reseau.appels, [])
        self.horloge.avancer(minutes=3)
        r = missions.collecter()
        self.assertEqual((r["collectees"], self.reseau.sources_appelees()), (["jobicy"], ["jobicy"]))
        self.assertTrue(any(o["source"] == "jobicy" for o in missions._lire_offres()["offres"]))

    def test_panne_garde_les_anciennes_offres(self):
        missions.collecter()
        self.horloge.avancer(heures=12)
        self.reseau.pannes = {"remoteok"}
        self.reseau.donnees["remoteok"] = "pas du json"
        missions.collecter()
        self.assertTrue(any(o["source"] == "remoteok" for o in missions._lire_offres()["offres"]),
                        "les offres d'une source en panne restent")
        self.horloge.avancer(minutes=6)
        self.reseau.pannes = set()
        r = missions.collecter()
        self.assertEqual(r["erreurs"], {"remoteok": "réponse illisible"})

    def test_delai_deux_fois_par_jour(self):
        missions.collecter()
        self.assertFalse(missions.collecte_due())
        self.reseau.appels.clear()
        self.horloge.avancer(heures=11, minutes=59)
        self.assertEqual(missions.collecter(), {"collectees": [], "erreurs": {}})
        self.assertEqual(self.reseau.appels, [], "au plus deux collectes par jour")
        self.horloge.avancer(minutes=1)
        self.assertTrue(missions.collecte_due())
        self.assertEqual(len(missions.collecter()["collectees"]), 5)

    def test_source_desactivee(self):
        missions.collecter()
        missions.changer_source("wwr", False)
        self.horloge.avancer(heures=12)
        self.reseau.appels.clear()
        missions.collecter()
        self.assertNotIn("wwr", self.reseau.sources_appelees(), "source désactivée : jamais interrogée")
        missions.enregistrer_recherche(recherche(nom="Rédaction", domaines=["redaction"], types=["contrat"]))
        r = missions.liste()
        self.assertEqual(r["recherches"][0]["total"], 0, "ses offres sont cachées")
        self.assertFalse(next(s for s in r["sources"] if s["id"] == "wwr")["active"])
        missions.changer_source("wwr", True)
        self.assertEqual(missions.liste()["recherches"][0]["total"], 1)
        for s in ("remotive", "remoteok", "himalayas", "jobicy"):
            missions.changer_source(s, False)
        with self.assertRaisesRegex(ValueError, "au moins une source"):
            missions.changer_source("wwr", False)
        with self.assertRaisesRegex(ValueError, "Source inconnue"):
            missions.changer_source("indeed", True)

    def test_expiree_apres_collecte(self):
        missions.collecter()
        missions.enregistrer_recherche(recherche(nom="Assistanat", domaines=["assistanat"], zones=["monde", "europe"]))
        self.assertEqual(missions.liste()["recherches"][0]["total"], 2)
        self.horloge.avancer(jours=17)               # 21 mars : l'offre expirée le 20 disparaît
        self.assertEqual(missions.liste()["recherches"][0]["total"], 1)

    def test_collecte_de_fond(self):
        self.patchs[-1].stop()
        try:
            self.assertFalse(missions.lancer_collecte_fond(), "aucune recherche : rien à collecter")
            missions.enregistrer_recherche(recherche())
            self.assertTrue(missions.lancer_collecte_fond())
            for fil in threading.enumerate():
                if fil.name == "missions-collecte":
                    fil.join(10)
            self.assertEqual(len(missions._lire_offres()["sources"]), 5)
            self.assertFalse(missions.lancer_collecte_fond(), "déjà collecté : rien avant 12 heures")
        finally:
            self.patchs[-1].start()


# ---------------------------------------------------------------------------
# Notation et filtres
# ---------------------------------------------------------------------------
class TestNotation(unittest.TestCase):
    def test_points(self):
        r = recherche(importants=["react"], utiles=["node.js"], eviter=["senior"])
        e = missions.evaluer(offre(techs=["Node.js"]), r)
        self.assertEqual((e["score"], e["raisons"]), (3 + 5 + 2 + 2, ["react", "node.js"]),
                         "domaine, important, utile (technologie), bonus freelance")
        self.assertEqual(missions.evaluer(offre(titre="Senior React Developer"), r)["score"], 3 + 5 - 5 + 2)
        self.assertEqual(missions.evaluer(offre(titre="React Developer", tags=["senior"]), r)["score"], 10,
                         "mot à éviter cherché dans le titre seulement")
        self.assertEqual(missions.evaluer(offre(type="contrat"), r)["score"], 3 + 5 + 1)
        self.assertEqual(missions.evaluer(offre(type="temps_plein"), r)["score"], 3 + 5)
        self.assertEqual(missions.evaluer(offre(titre="Ruby Developer", tags=["react"]), r)["raisons"], ["react"],
                         "étiquettes lues")

    def test_domaine_ou_mot_important(self):
        r = recherche(importants=["react"])
        e = missions.evaluer(offre(categorie="design", titre="React UI Designer"), r)
        self.assertEqual((e["score"], e["domaine"]), (5 + 2, False), "hors domaine mais mot important")
        self.assertIsNone(missions.evaluer(offre(categorie="design", titre="Logo Designer"), r))
        self.assertIsNone(missions.evaluer(offre(categorie="design", titre="Logo Designer", tags=["node"]),
                                           recherche(utiles=["node"])), "un mot utile ne suffit pas")
        r2 = recherche(domaines=[], importants=["java"])
        self.assertIsNone(missions.evaluer(offre(titre="JavaScript Developer"), r2), "mot entier")

    def test_bonus_seulement_si_pertinent(self):
        r = recherche(eviter=["lead"])
        self.assertEqual(missions.evaluer(offre(titre="Lead Developer"), r)["score"], -2, "pas de bonus de type")
        self.assertEqual(missions.evaluer(offre(titre="Developer"), r)["score"], 5)
        self.assertEqual(missions.evaluer(offre(titre="Lead Developer", type="contrat"),
                                          recherche(eviter=["lead", "developer"]))["score"], -7)

    def test_filtres(self):
        ev = missions.evaluer
        self.assertIsNone(ev(offre(type="stage"), recherche()), "stage exclu par défaut")
        self.assertIsNotNone(ev(offre(type="stage"), recherche(types=["stage"])))
        self.assertIsNone(ev(offre(hors_teletravail=True), recherche()), "faux télétravail écarté")
        # Zones
        self.assertIsNotNone(ev(offre(zones=["europe", "afrique"]), recherche(zones=["afrique"])))
        self.assertIsNone(ev(offre(zones=["europe", "afrique"]), recherche(zones=["monde"])))
        self.assertIsNone(ev(offre(zones=["inconnue"]), recherche(zones=["monde"])))
        self.assertIsNotNone(ev(offre(zones=["inconnue"]), recherche(zones=["monde", "inconnue"])))
        # Niveau
        for niveau, annees, garde in (("debutant", 2, True), ("debutant", 3, False), ("confirme", 5, True),
                                      ("confirme", 6, False), ("senior", 15, True), ("debutant", None, True)):
            resultat = ev(offre(experience=annees), recherche(niveau=niveau))
            self.assertEqual(resultat is not None, garde, f"{niveau}, {annees} ans")

    def test_salaire(self):
        ev = missions.evaluer
        r = recherche(salaire_min=50000, devise="USD", periode="an")
        usd = lambda mini, maxi, periode="an": {"min": mini, "max": maxi, "devise": "USD", "periode": periode}  # noqa: E731
        self.assertIsNone(ev(offre(salaire=usd(40000, 45000)), r))
        self.assertIsNotNone(ev(offre(salaire=usd(45000, 60000)), r), "le haut de la fourchette compte")
        self.assertIsNotNone(ev(offre(salaire=usd(30, 30, "heure")), r), "30 $/h ≈ 52 800 $/an")
        self.assertIsNone(ev(offre(salaire=usd(20, 20, "heure")), r))
        eur = {"min": 100000, "max": None, "devise": "EUR", "periode": "an"}
        self.assertIsNotNone(ev(offre(salaire=eur), r), "autre devise : non comparée, gardée")
        self.assertIsNotNone(ev(offre(), r), "sans salaire : gardée")
        r2 = recherche(salaire_min=50000, devise="USD", garder_sans_salaire=False)
        self.assertIsNone(ev(offre(salaire=eur), r2))
        self.assertIsNone(ev(offre(), r2))
        self.assertIsNotNone(ev(offre(salaire=usd(60000, 70000)), r2))
        mois = recherche(salaire_min=4000, devise="USD", periode="mois")
        self.assertIsNotNone(ev(offre(salaire=usd(50000, 50000)), mois))
        self.assertIsNone(ev(offre(salaire=usd(45000, 45000)), mois))

    def test_validation_recherche(self):
        v = missions.valider_recherche
        mauvaises = [{"nom": " "}, {"nom": "x", "domaines": [], "importants": []},
                     {"nom": "x", "domaines": ["dev"], "types": []}, {"nom": "x", "domaines": ["dev"], "zones": []},
                     {"nom": "x", "domaines": ["dev"], "niveau": "expert"}, {"nom": "x", "domaines": ["dev"], "devise": "euro"},
                     {"nom": "x", "domaines": ["dev"], "score_min": "abc"}, {"nom": "x", "domaines": ["dev"], "score_min": 500},
                     {"nom": "x", "domaines": ["dev"], "salaire_min": "-3"}, {"nom": "x", "domaines": ["dev"], "periode": "siecle"},
                     "pas un dictionnaire"]
        for m in mauvaises:
            if isinstance(m, dict):
                m.setdefault("types", ["freelance"])
                m.setdefault("zones", ["monde"])
            with self.assertRaises(ValueError, msg=f"refusée : {m}"):
                v(m)
        r = v({"nom": "  Mes   missions ", "domaines": ["dev", "inconnu"], "types": ["freelance"], "zones": ["monde"],
               "importants": "React, react , Odoo;; python", "devise": "eur", "salaire_min": "45 000"})
        self.assertEqual((r["nom"], r["domaines"], r["importants"], r["devise"], r["salaire_min"], r["niveau"]),
                         ("Mes missions", ["dev"], ["React", "Odoo", "python"], "EUR", 45000, "senior"))
        self.assertTrue(r["garder_sans_salaire"])

    def test_liens_manuels(self):
        liens = missions.liens_manuels(recherche(importants=["react native", "odoo"]))
        self.assertEqual([x["nom"] for x in liens], ["Malt", "Codeur.com", "ComeUp", "Upwork", "LinkedIn", "Indeed"])
        self.assertTrue(all("react+native+odoo" in x["url"] and x["url"].startswith("https://") for x in liens))
        self.assertIn("virtual+assistant", missions.liens_manuels(recherche(domaines=["assistanat"]))[0]["url"],
                      "sans mot-clé : le domaine en anglais")


# ---------------------------------------------------------------------------
# Listes, vues, masquées
# ---------------------------------------------------------------------------
class TestListes(Base):
    def test_selection_tri_vues(self):
        missions.collecter()
        r = missions.enregistrer_recherche(recherche(nom="Code", domaines=["dev", "data"], importants=["python"],
                                                     zones=["monde", "amerique"]))
        res = missions.offres(r["id"])
        self.assertEqual([o["titre"] for o in res["offres"]],
                         ["Python Backend Engineer", "Data Analyst", "Freelance React Developer"],
                         "score puis date")
        self.assertEqual([o["score"] for o in res["offres"]], [8, 8, 5], "python trouvé aussi dans les technologies")
        self.assertTrue(all(o["nouvelle"] for o in res["offres"]))
        self.assertEqual(len(res["liens"]), 6)
        self.assertEqual(missions.liste()["recherches"][0]["nouvelles"], 3)
        missions.marquer_vues(r["id"], [o["id"] for o in res["offres"][:2]])
        self.assertEqual([o["nouvelle"] for o in missions.offres(r["id"])["offres"]], [False, False, True])
        self.assertEqual(missions.liste()["recherches"][0]["nouvelles"], 1)
        # Masquer, réafficher.
        missions.masquer("remoteok-101")
        self.assertEqual(missions.offres(r["id"])["total"], 2)
        self.assertEqual(missions.liste()["masquees"], 1)
        self.assertEqual(missions.demasquer(), 1)
        self.assertEqual(missions.offres(r["id"])["total"], 3)
        with self.assertRaises(ValueError):
            missions.offres("inconnue")

    def test_doublons_entre_sources(self):
        self.reseau.donnees["jobicy"]["jobs"].append(
            {"id": 777, "url": "https://jobicy.com/jobs/777", "jobTitle": "Freelance React Developer",
             "companyName": "Exemple SA", "jobType": ["Freelance"], "jobGeo": "Anywhere", "pubDate": "2026-03-01 08:00:00"})
        missions.collecter()
        r = missions.enregistrer_recherche(recherche(importants=["react"]))
        titres = [o["titre"] for o in missions.offres(r["id"])["offres"]]
        self.assertEqual(titres.count("Freelance React Developer"), 1, "même offre sur deux sites : une seule ligne")

    def test_recherches_crud_et_premier_ecran(self):
        l = missions.liste()
        self.assertEqual((l["recherches"], l["profil"], l["a_collecter"]), ([], "developpeur", True))
        self.assertEqual(l["modeles"]["developpeur"]["domaines"], ["dev"])
        self.assertEqual(l["modeles"]["assistant_virtuel"]["types"], ["freelance", "temps_partiel"])
        self.assertEqual(l["modeles"]["assistant_virtuel"]["domaines"], ["support", "assistanat"])
        r = missions.enregistrer_recherche(recherche(nom="A") | {"id": None})
        r2 = missions.enregistrer_recherche({**r, "nom": "B", "score_min": 8})
        self.assertEqual((r2["id"], r2["nom"], r2["score_min"]), (r["id"], "B", 8))
        with self.assertRaisesRegex(ValueError, "introuvable"):
            missions.enregistrer_recherche({**r, "id": "inconnue"})
        missions.marquer_vues(r["id"], ["x-1"])
        self.assertTrue(missions.supprimer_recherche(r["id"]))
        self.assertNotIn(r["id"], missions._lire()["vues"], "ses vues sont oubliées")
        with self.assertRaises(ValueError):
            missions.supprimer_recherche(r["id"])


# ---------------------------------------------------------------------------
# Import d'un profil.json
# ---------------------------------------------------------------------------
PROFIL = {
    "_aide": "Profil d'exemple",
    "motsCles": {"odoo": 6, "react": 4, "python": 3, "developer": 1, "bizarre": "x"},
    "techs": {"Odoo": 4, "React": 2, "Docker": 1},
    "motsAEviter": {"senior": -2, "manager": -6},
    "experienceMaxSouhaitee": 4, "penaliteParAnneeEnTrop": 2,
    "zones": ["monde", "afrique", "lune"],
    "bonusType": {"freelance": 6, "contrat": 5, "temps-partiel": 1, "temps-plein": 0, "stage": -5},
    "scoreMinimum": 6,
}


class TestImportProfil(Base):
    def test_conversion(self):
        c = missions.recherche_depuis_profil(PROFIL)
        self.assertEqual(c["importants"], ["odoo", "react"], "poids 4 ou plus, sans doublon")
        self.assertEqual(c["utiles"], ["python", "developer", "Docker"])
        self.assertEqual(c["eviter"], ["senior", "manager"])
        self.assertEqual(c["types"], ["freelance", "contrat", "temps_partiel"], "bonusType > 0")
        self.assertEqual(c["zones"], ["monde", "afrique"])
        self.assertEqual((c["niveau"], c["score_min"], c["nom"], c["domaines"]), ("confirme", 6, "Mon profil", []))
        self.assertEqual(missions.recherche_depuis_profil({"motsCles": {"x": 5}, "experienceMaxSouhaitee": 2})["niveau"],
                         "debutant")
        self.assertEqual(missions.recherche_depuis_profil({"motsCles": {"x": 5}})["niveau"], "senior")

    def test_fichier_et_contenu(self):
        dossier = tempfile.mkdtemp(prefix="mes-outils-profil-")
        try:
            chemin = os.path.join(dossier, "profil.json")
            with open(chemin, "w", encoding="utf-8-sig") as f:
                json.dump(PROFIL, f)
            r = missions.importer_profil(chemin=chemin)
            self.assertEqual((r["nom"], r["score_min"]), ("Mon profil", 6))
            r2 = missions.importer_profil(profil={**PROFIL, "scoreMinimum": 4})
            self.assertEqual((r2["id"], r2["score_min"]), (r["id"], 4), "nouvel import : même recherche mise à jour")
            self.assertEqual(len(missions.liste()["recherches"]), 1)
            mauvais = os.path.join(dossier, "mauvais.json")
            with open(mauvais, "w", encoding="utf-8") as f:
                f.write("{pas du json")
            with self.assertRaisesRegex(ValueError, "pas un profil JSON valide"):
                missions.importer_profil(chemin=mauvais)
            with self.assertRaisesRegex(ValueError, "introuvable"):
                missions.importer_profil(chemin=os.path.join(dossier, "absent.json"))
            with self.assertRaisesRegex(ValueError, "introuvable"):
                missions.importer_profil(chemin="")
            with self.assertRaisesRegex(ValueError, "aucun mot-clé important"):
                missions.importer_profil(profil={"motsCles": {"web": 2}})
            with self.assertRaisesRegex(ValueError, "pas un profil"):
                missions.importer_profil(profil=["liste"])
        finally:
            shutil.rmtree(dossier, ignore_errors=True)

    def test_nom_en_anglais(self):
        with ConfigTemporaire({"outils": [], "langue": "en"}):
            self.assertEqual(missions.importer_profil(profil=PROFIL)["nom"], "My profile")


# ---------------------------------------------------------------------------
# Suivi des candidatures
# ---------------------------------------------------------------------------
class TestSuivi(Base):
    def test_depuis_une_offre_et_a_la_main(self):
        missions.collecter()
        s = missions.enregistrer_suivi({"id": "remoteok-101", "statut": "postule", "recherche_id": "r1"})
        self.assertEqual((s["titre"], s["entreprise"], s["url"], s["source"], s["statut"], s["date"]),
                         ("Python Backend Engineer", "Société Test", "https://remoteok.com/remote-jobs/101", "remoteok",
                          "postule", "2026-03-04"))
        self.horloge.avancer(jours=3)
        s = missions.enregistrer_suivi({"id": s["id"], "statut": "entretien", "note": " Appel mardi ", "relance": "2026-03-10"})
        self.assertEqual((s["statut"], s["date"], s["note"], s["relance"]), ("entretien", "2026-03-07", "Appel mardi", "2026-03-10"),
                         "changement de statut : date du jour")
        s = missions.enregistrer_suivi({"id": s["id"], "statut": "entretien", "tache_id": "t42"})
        self.assertEqual((s["tache_id"], s["relance_tache"], s["date"]), ("t42", "2026-03-10", "2026-03-07"))
        s = missions.enregistrer_suivi({"id": s["id"], "statut": "retenu", "date": "2026-03-08"})
        self.assertEqual(s["date"], "2026-03-08", "date choisie")
        # L'offre disparaît du cache : le suivi reste.
        self.horloge.avancer(jours=70)
        missions.collecter()
        self.assertEqual(missions.liste()["suivi"][0]["titre"], "Python Backend Engineer")
        m = missions.enregistrer_suivi({"statut": "a_voir", "titre": "Mission trouvée ailleurs", "entreprise": "Agence",
                                        "url": "https://exemple.test/mission"})
        self.assertTrue(m["id"].startswith("manuel-"))
        self.assertEqual(m["source"], "manuel")
        m = missions.enregistrer_suivi({"id": m["id"], "statut": "postule", "titre": "Mission renommée"})
        self.assertEqual(m["titre"], "Mission renommée")
        for mauvais in ({"statut": "a_voir"}, {"statut": "pause", "titre": "x"}, {"titre": "x", "url": "javascript:alert(1)"},
                        {"id": m["id"], "statut": "postule", "date": "31/02"}, "texte"):
            with self.assertRaises(ValueError, msg=f"refusé : {mauvais}"):
                missions.enregistrer_suivi(mauvais)
        self.assertTrue(missions.supprimer_suivi(m["id"]))
        with self.assertRaises(ValueError):
            missions.supprimer_suivi(m["id"])


# ---------------------------------------------------------------------------
# Accueil et alertes de la bulle
# ---------------------------------------------------------------------------
class TestAlertes(Base):
    def test_une_alerte_par_jour_et_par_recherche(self):
        self.assertEqual(missions.alertes_dues(), [])
        r = missions.enregistrer_recherche(recherche(nom="Code", domaines=["dev", "data"], importants=["python"],
                                                     zones=["monde", "amerique"]))
        self.assertEqual(missions.alertes_dues(), [], "pas encore d'offre")
        missions.collecter()
        dues = missions.alertes_dues()
        self.assertEqual(dues, [{"id": f"{r['id']}:2026-03-04", "titre": "3 nouvelles offres : Code",
                                 "detail": "Python Backend Engineer chez Société Test (8 points)"}])
        self.assertTrue(missions.marquer_alerte(dues[0]["id"]))
        self.assertFalse(missions.marquer_alerte(dues[0]["id"]), "déjà vue")
        self.assertEqual(missions.alertes_dues(), [])
        # Nouvelle offre le même jour : attendre demain.
        self.reseau.donnees["remoteok"].append(
            {"id": "102", "position": "Data Engineer Python", "company": "Autre", "location": "Worldwide",
             "date": "2026-03-04T08:00:00+00:00", "url": "https://remoteok.com/remote-jobs/102"})
        self.horloge.avancer(heures=12)                      # 21 h, même jour
        missions.collecter()
        self.assertEqual(missions.alertes_dues(), [], "au plus une alerte par jour")
        self.horloge.avancer(heures=4)                       # lendemain
        dues = missions.alertes_dues()
        self.assertEqual([a["titre"] for a in dues], ["Nouvelle offre : Code"], "seulement l'offre arrivée depuis")
        missions.marquer_alerte(dues[0]["id"])
        self.horloge.avancer(jours=1)
        self.assertEqual(missions.alertes_dues(), [], "rien de neuf")
        # Offres déjà vues dans la page : pas d'alerte.
        accueil = missions.accueil()
        self.assertEqual(accueil["recherches"], [{"id": r["id"], "nom": "Code", "nouvelles": 4}])
        self.assertEqual([o["titre"] for o in accueil["meilleures"]],
                         ["Data Engineer Python", "Python Backend Engineer", "Data Analyst"])
        missions.marquer_vues(r["id"], [o["id"] for o in missions.offres(r["id"])["offres"]])
        self.assertEqual(missions.accueil(), {"recherches": [], "meilleures": []})
        self.assertFalse(missions.marquer_alerte("inconnue:2026-03-06"))

    def test_score_minimum_et_anglais(self):
        missions.collecter()
        missions.enregistrer_recherche(recherche(nom="Haut", importants=["python"], zones=["monde", "amerique"], score_min=20))
        self.assertEqual(missions.alertes_dues(), [], "aucune offre au-dessus du score minimum")
        with ConfigTemporaire({"outils": [], "langue": "en"}):
            missions.collecter()
            missions.enregistrer_recherche(recherche(nom="Assist", domaines=["assistanat"]))
            dues = missions.alertes_dues()
        self.assertEqual((dues[0]["titre"], dues[0]["detail"]), ("New offer: Assist", "Virtual Assistant at Aide Plus (3 points)"))

    def test_la_bulle_lance_la_collecte(self):
        with mock.patch.object(missions, "lancer_collecte_fond") as lancer:
            missions.alertes_dues()
        lancer.assert_called_once_with()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
class TestRoutes(ServeurTest):
    def test_routes(self):
        horloge, reseau = Horloge(), Reseau()
        with ConfigTemporaire({"outils": [], "profil": "assistant_virtuel"}), \
                mock.patch.object(missions, "maintenant", horloge), mock.patch.object(missions, "_telecharger", reseau), \
                mock.patch.object(missions, "_pause", lambda s: None), \
                mock.patch.object(missions, "lancer_collecte_fond", lambda: False), \
                mock.patch.object(missions.systeme, "ouvrir") as ouvrir:
            statut, r = self.post("/api/missions/liste", {})
            self.assertEqual((statut, r["recherches"], r["profil"], r["a_collecter"]), (200, [], "assistant_virtuel", True))
            statut, r = self.post("/api/missions/recherche/enregistrer", {"recherche": {"nom": "x", "types": ["freelance"]}})
            self.assertEqual((statut, r.get("erreur")), (400, "Choisissez au moins un domaine ou un mot-clé important."))
            statut, rech = self.post("/api/missions/recherche/enregistrer", {"recherche": recherche(
                nom="Code", domaines=["dev", "data"], importants=["python"], zones=["monde", "amerique"]) | {"id": None}})
            self.assertEqual(statut, 200)
            statut, r = self.post("/api/missions/actualiser", {})
            self.assertEqual((statut, len(r["collectees"]), r["nombre_offres"], r["recherches"][0]["nouvelles"]), (200, 5, 7, 3))
            statut, r = self.post("/api/missions/actualiser", {})
            self.assertEqual((r["collectees"], r["a_collecter"]), ([], False), "délai respecté")
            statut, o = self.post("/api/missions/offres", {"recherche_id": rech["id"]})
            self.assertEqual((statut, o["total"], o["offres"][0]["id"]), (200, 3, "remoteok-101"))
            statut, r = self.post("/api/missions/voir", {"recherche_id": rech["id"], "ids": ["remoteok-101"]})
            self.assertEqual(r, {"ok": True})
            statut, r = self.post("/api/missions/ouvrir", {"id": "remotive-1"})
            self.assertEqual(statut, 200)
            ouvrir.assert_called_with("https://remotive.com/remote-jobs/software-dev/freelance-react-1?utm_source=x")
            statut, r = self.post("/api/missions/ouvrir", {"recherche_id": rech["id"], "site": "upwork"})
            self.assertEqual(r["url"], "https://www.upwork.com/nx/search/jobs/?q=python")
            statut, r = self.post("/api/missions/ouvrir", {"recherche_id": rech["id"], "site": "javascript:alert(1)"})
            self.assertEqual(statut, 400)
            statut, r = self.post("/api/missions/ouvrir", {"id": "https://exemple.test/piege"})
            self.assertEqual((statut, r.get("erreur")), (400, "Offre introuvable."), "jamais une adresse venue de la page")
            self.assertEqual(ouvrir.call_count, 2)
            statut, r = self.post("/api/missions/masquer", {"id": "jobicy-501"})
            self.assertEqual(r, {"ok": True})
            statut, r = self.post("/api/missions/demasquer", {})
            self.assertEqual(r, {"reaffichees": 1})
            statut, r = self.post("/api/missions/sources", {"id": "wwr", "actif": False})
            self.assertEqual(r, {"ok": True})
            statut, s = self.post("/api/missions/suivi/enregistrer", {"suivi": {"id": "remotive-1", "statut": "postule"}})
            self.assertEqual((statut, s["titre"]), (200, "Freelance React Developer"))
            statut, r = self.post("/api/missions/suivi/supprimer", {"id": s["id"]})
            self.assertEqual(r, {"ok": True})
            statut, r = self.post("/api/missions/importer_profil", {"profil": PROFIL})
            self.assertEqual((statut, r["nom"]), (200, "Mon profil"))
            statut, r = self.post("/api/missions/importer_profil", {"chemin": "absent-123.json"})
            self.assertEqual((statut, r.get("erreur")), (400, "Fichier introuvable."))
            statut, r = self.post("/api/missions/accueil", {})
            self.assertEqual((statut, r["recherches"][0]["nouvelles"]), (200, 2))
            statut, r = self.post("/api/missions/alertes", {})
            self.assertEqual(len(r["alertes"]), 2, "une par recherche : Code et Mon profil")
            statut, r = self.post("/api/missions/marquer_alerte", {"id": r["alertes"][0]["id"]})
            self.assertEqual(r, {"ok": True})
            statut, r = self.post("/api/missions/recherche/supprimer", {"id": rech["id"]})
            self.assertEqual(r, {"ok": True})
            statut, r = self.post("/api/missions/offres", {"recherche_id": rech["id"]})
            self.assertEqual((statut, r.get("erreur")), (400, "Recherche introuvable."))


class TestCode(unittest.TestCase):
    def test_aucun_appel_systeme_direct(self):
        with open(missions.__file__, encoding="utf-8") as f:
            source = f.read()
        for interdit in ("os.startfile", "creationflags", "subprocess", "shell=True", "ctypes"):
            self.assertNotIn(interdit, source, f"{interdit} : passer par systeme.py")
        with open(os.path.join(WEB, "missions.js"), encoding="utf-8") as f:
            page = f.read()
        self.assertNotIn("localStorage", page, "rien n'est gardé dans le navigateur")
        self.assertNotIn("innerHTML", page)
        self.assertIsNone(__import__("re").search(r"#[0-9a-fA-F]{3,6}\b", page), "aucune couleur en dur")

    @unittest.skipUnless(shutil.which("node"), "node absent")
    def test_syntaxe_js(self):
        r = subprocess.run(["node", "--check", os.path.join(WEB, "missions.js")], capture_output=True, text=True,
                           timeout=30, creationflags=0x08000000 if sys.platform == "win32" else 0)
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
