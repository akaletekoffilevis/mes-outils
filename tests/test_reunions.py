# -*- coding: utf-8 -*-
"""Tests de l'application « Réunions et déplacements » : validation,
enregistrement, compte rendu (texte et mailto), feuille de route, documents
liés, rendez-vous de l'agenda, rappels de la bulle, carte de l'accueil,
routes HTTP et dictionnaire de traduction de la page."""
import datetime
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import urllib.parse
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # aide.py, quel que soit le lancement

from aide import ConfigTemporaire, ServeurTest  # noqa: E402

import reunions  # noqa: E402

WEB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outil", "web")


class Horloge:
    """Horloge simulée : avancer(minutes=…, jours=…)."""

    def __init__(self, depart="2026-03-02T09:00"):
        self.t = datetime.datetime.strptime(depart, reunions.FORMAT_MINUTE)

    def __call__(self):
        return self.t

    def aller(self, quand):
        self.t = datetime.datetime.strptime(quand, reunions.FORMAT_MINUTE)


def reunion(**valeurs):
    base = {"titre": "Point d'équipe", "debut": "2026-03-03T14:30", "duree": 45, "lieu": "Salle B",
            "participants": [{"nom": "Alex Exemple", "email": "alex@exemple.test"}, {"nom": "Sam Test"}],
            "ordre_du_jour": [{"texte": "Planning"}, {"texte": "Budget", "fait": True}],
            "notes": "Rien de bloquant.", "decisions": ["Livrer vendredi"],
            "actions": [{"qui": "Sam Test", "quoi": "Envoyer le devis", "echeance": "2026-03-05"}]}
    base.update(valeurs)
    return base


def deplacement(**valeurs):
    base = {"destination": "Lyon", "depart": "2026-03-10", "retour": "2026-03-11", "voyageurs": ["Alex Exemple"],
            "etapes": [{"type": "train", "de": "Paris", "vers": "Lyon", "depart": "2026-03-10T08:12",
                        "arrivee": "2026-03-10T10:05", "numero": "6601", "reference": "ABC123"},
                       {"type": "train", "de": "Lyon", "vers": "Paris", "depart": "2026-03-11T07:30",
                        "arrivee": "2026-03-11T09:30"}],
            "hebergements": [{"nom": "Hôtel Exemple", "adresse": "1 rue de l'Essai", "arrivee": "2026-03-10",
                              "depart": "2026-03-11", "reference": "H-42"}],
            "controle": [{"texte": "Billets", "fait": True}, {"texte": "Chargeur"}, {"texte": "Badge"}],
            "budget": "1 234,50", "devise": "EUR", "note": "Prévoir un parapluie."}
    base.update(valeurs)
    return base


class Base(unittest.TestCase):
    langue = "fr"

    def setUp(self):
        self.cfg = ConfigTemporaire({"outils": [], "langue": self.langue})
        self.cfg.__enter__()
        self.horloge = Horloge()
        self.patch = mock.patch.object(reunions, "maintenant", self.horloge)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.cfg.__exit__(None, None, None)


class TestReunions(Base):
    def test_creer_puis_modifier(self):
        r = reunions.enregistrer_reunion(reunion(titre="  Point   d'équipe "))
        self.assertEqual(r["titre"], "Point d'équipe", "espaces en trop retirés")
        self.assertEqual(r["fin"], "2026-03-03T15:15", "fin = début + durée")
        self.assertEqual(r["agenda_ids"], {})
        self.assertTrue(r["actions"][0]["id"], "chaque action reçoit un identifiant")
        reunions.lier_agenda("reunion", r["id"], {"reunion": "rdv1"})
        self.horloge.aller("2026-03-02T10:00")
        r2 = reunions.enregistrer_reunion({**r, "titre": "Autre", "agenda_ids": {"x": "y"}})
        self.assertEqual(r2["id"], r["id"])
        self.assertEqual(r2["cree"], "2026-03-02T09:00", "date de création conservée")
        self.assertEqual(r2["modifie"], "2026-03-02T10:00")
        self.assertEqual(r2["agenda_ids"], {"reunion": "rdv1"}, "les liens d'agenda ne viennent pas de la page")
        self.assertEqual(r2["actions"][0]["id"], r["actions"][0]["id"], "identifiant d'action conservé")
        self.assertEqual(len(reunions.liste()["reunions"]), 1)

    def test_validation(self):
        cas = [({"titre": " "}, "titre"), ({"debut": "demain"}, "invalide"), ({"debut": ""}, "manquante"),
               ({"duree": 2}, "durée"), ({"duree": "abc"}, "Durée invalide"),
               ({"lien": "teams.example/abc"}, "visio"), ({"participants": [{"nom": "X", "email": "pas-une-adresse"}]}, "e-mail")]
        for valeurs, motif in cas:
            with self.subTest(valeurs=valeurs), self.assertRaisesRegex(ValueError, "(?i)" + motif):
                reunions.enregistrer_reunion(reunion(**valeurs))
        with self.assertRaisesRegex(ValueError, "introuvable"):
            reunions.enregistrer_reunion(reunion(id="inconnu"))

    def test_lignes_vides_retirees(self):
        r = reunions.enregistrer_reunion(reunion(
            participants=[{"nom": ""}, "Camille", {"email": "c@exemple.test"}, None],
            ordre_du_jour=[{"texte": " "}, "Point libre"], decisions=["", "  Oui "],
            actions=[{"qui": "", "quoi": ""}, {"qui": "Camille", "quoi": ""}], lien="https://visio.exemple.test/abc"))
        self.assertEqual([p["nom"] or p["email"] for p in r["participants"]], ["Camille", "c@exemple.test"])
        self.assertEqual(r["ordre_du_jour"], [{"texte": "Point libre", "fait": False}])
        self.assertEqual(r["decisions"], ["Oui"])
        self.assertEqual(len(r["actions"]), 1, "une action à moitié remplie reste (saisie en cours)")

    def test_liste_triee_et_supprimer(self):
        b = reunions.enregistrer_reunion(reunion(titre="B", debut="2026-03-05T09:00"))
        reunions.enregistrer_reunion(reunion(titre="A", debut="2026-03-04T09:00"))
        self.assertEqual([r["titre"] for r in reunions.liste()["reunions"]], ["A", "B"])
        self.assertEqual(reunions._supprimer("reunions", b["id"]), 1)
        self.assertEqual(reunions._supprimer("reunions", b["id"]), 0)
        self.assertEqual([r["titre"] for r in reunions.liste()["reunions"]], ["A"])


class TestCompteRendu(Base):
    def test_texte_et_mailto(self):
        r = reunions.enregistrer_reunion(reunion())
        cr = reunions.compte_rendu(r["id"])
        texte = cr["texte"]
        self.assertTrue(texte.startswith("Compte rendu : Point d'équipe\n"))
        self.assertIn("Date : mardi 3 mars 2026, 14:30 – 15:15", texte)
        self.assertIn("Participants : Alex Exemple, Sam Test", texte)
        self.assertIn("Ordre du jour\n- Planning\n- Budget", texte)
        self.assertIn("Décisions\n- Livrer vendredi", texte)
        self.assertIn("- Sam Test : Envoyer le devis (pour le 05/03/2026)", texte)
        self.assertEqual(cr["destinataires"], ["alex@exemple.test"], "seuls les participants avec une adresse")
        self.assertEqual(cr["sujet"], "Compte rendu : Point d'équipe (03/03/2026)")
        self.assertTrue(cr["mailto"].startswith("mailto:alex@exemple.test?subject="))
        corps = urllib.parse.parse_qs(urllib.parse.urlparse(cr["mailto"]).query)["body"][0]
        self.assertEqual(corps, texte.replace("\n", "\r\n"), "corps du mail = compte rendu complet")
        self.assertFalse(cr["tronque"])

    def test_sections_vides_absentes(self):
        r = reunions.enregistrer_reunion({"titre": "Court", "debut": "2026-03-03T09:00"})
        texte = reunions.compte_rendu(r["id"])["texte"]
        for absent in ("Ordre du jour", "Décisions", "Actions", "Participants", "Lieu"):
            self.assertNotIn(absent, texte)

    def test_mailto_raccourci(self):
        r = reunions.enregistrer_reunion(reunion(notes="très long " * 400))
        cr = reunions.compte_rendu(r["id"])
        self.assertTrue(cr["tronque"])
        self.assertLessEqual(len(cr["mailto"]), reunions.MAX_MAILTO)
        self.assertIn(urllib.parse.quote("[…]"), cr["mailto"])

    def test_introuvable(self):
        with self.assertRaisesRegex(ValueError, "Réunion introuvable"):
            reunions.compte_rendu("rien")


class TestCompteRenduAnglais(Base):
    langue = "en"

    def test_anglais(self):
        r = reunions.enregistrer_reunion(reunion())
        texte = reunions.compte_rendu(r["id"])["texte"]
        self.assertIn("Minutes: Point d'équipe", texte)
        self.assertIn("Date: Tuesday 3 March 2026, 14:30 – 15:15", texte)
        self.assertIn("- Sam Test: Envoyer le devis (due 05/03/2026)", texte)


class TestDeplacements(Base):
    def test_creer_et_valider(self):
        d = reunions.enregistrer_deplacement(deplacement())
        self.assertEqual(d["budget"], 1234.5, "budget saisi à la française")
        self.assertEqual([e["type"] for e in d["etapes"]], ["train", "train"])
        self.assertTrue(all(e["id"] for e in d["etapes"] + d["hebergements"]))
        cas = [({"destination": ""}, "destination"), ({"depart": "2026-13-01"}, "invalide"),
               ({"retour": "2026-03-09"}, "retour"), ({"budget": "beaucoup"}, "Budget"), ({"budget": -5}, "Budget"),
               ({"etapes": [{"type": "avion", "depart": "2026-03-10T10:00", "arrivee": "2026-03-10T09:00"}]}, "arrivée"),
               ({"hebergements": [{"nom": "H", "arrivee": "2026-03-11", "depart": "2026-03-10"}]}, "Hébergement"),
               ({"documents": [{"chemin": r"C:\Temp\installe.exe"}]}, "type de fichier")]
        for valeurs, motif in cas:
            with self.subTest(valeurs=valeurs), self.assertRaisesRegex(ValueError, "(?i)" + motif):
                reunions.enregistrer_deplacement(deplacement(**valeurs))

    def test_type_inconnu_et_doublons(self):
        d = reunions.enregistrer_deplacement(deplacement(
            etapes=[{"type": "fusee", "de": "A"}], hebergements=[{"nom": ""}],
            documents=[r"C:\Docs\billet.pdf", {"chemin": r"c:\docs\BILLET.pdf"}, ""], budget=""))
        self.assertEqual(d["etapes"][0]["type"], "autre")
        self.assertEqual(d["hebergements"], [])
        self.assertEqual(len(d["documents"]), 1, "même fichier une seule fois")
        self.assertEqual(d["documents"][0]["nom"], "billet.pdf")
        self.assertIsNone(d["budget"])

    def test_feuille_de_route(self):
        d = reunions.enregistrer_deplacement(deplacement())
        f = reunions.feuille_de_route(d["id"])
        self.assertEqual([j["date"] for j in f["jours"]], ["2026-03-10", "2026-03-11"])
        jour1 = [e["titre"] for e in f["jours"][0]["evenements"]]
        self.assertEqual(jour1, ["Train Paris → Lyon", "Arrivée à l'hébergement : Hôtel Exemple"],
                         "l'arrivée à l'hôtel après le trajet")
        jour2 = [e["titre"] for e in f["jours"][1]["evenements"]]
        self.assertEqual(jour2, ["Départ de l'hébergement : Hôtel Exemple", "Train Lyon → Paris"],
                         "le départ de l'hôtel avant le train du matin")
        e1 = f["jours"][0]["evenements"][0]
        self.assertEqual((e1["heure"], e1["type"]), ("08:12", "train"))
        self.assertEqual(e1["detail"], "arrivée 10:05 · n° 6601 · réf. ABC123")
        texte = f["texte"]
        self.assertIn("Du 10/03/2026 au 11/03/2026 · Voyageurs : Alex Exemple", texte)
        self.assertIn("Mardi 10 mars 2026", texte)
        self.assertIn("[x] Billets\n[ ] Chargeur", texte)
        self.assertIn("Budget prévu : 1 234,50 EUR", texte)

    def test_feuille_sans_etape(self):
        d = reunions.enregistrer_deplacement({"destination": "Nantes", "depart": "2026-03-10", "retour": "2026-03-12",
                                              "etapes": [{"type": "voiture", "de": "Maison"}]})
        f = reunions.feuille_de_route(d["id"])
        self.assertEqual([j["date"] for j in f["jours"]], ["2026-03-10", "2026-03-12", ""],
                         "départ, retour, puis les trajets sans date")
        self.assertEqual(f["jours"][0]["evenements"][0]["titre"], "Départ pour Nantes")
        self.assertEqual(f["jours"][1]["evenements"][0]["titre"], "Retour de Nantes")
        self.assertEqual(f["jours"][2]["libelle"], "Sans date")


class TestDocuments(Base):
    def setUp(self):
        super().setUp()
        self.dossier = tempfile.mkdtemp(prefix="reunions-test-")
        self.fichier = os.path.join(self.dossier, "billet.pdf")
        with open(self.fichier, "w", encoding="utf-8") as f:
            f.write("x")

    def tearDown(self):
        shutil.rmtree(self.dossier, ignore_errors=True)
        super().tearDown()

    def test_ouvrir_seulement_les_documents_lies(self):
        d = reunions.enregistrer_deplacement(deplacement(documents=[self.fichier]))
        with mock.patch.object(reunions.os, "startfile", create=True) as ouvrir:
            reunions.ouvrir_document(d["id"], self.fichier)
            ouvrir.assert_called_once_with(os.path.normpath(self.fichier))
            with self.assertRaisesRegex(ValueError, "pas lié"):
                reunions.ouvrir_document(d["id"], os.path.join(self.dossier, "autre.pdf"))
            os.remove(self.fichier)
            with self.assertRaisesRegex(ValueError, "introuvable"):
                reunions.ouvrir_document(d["id"], self.fichier)
            self.assertEqual(ouvrir.call_count, 1)

    def test_montrer_dans_l_explorateur(self):
        d = reunions.enregistrer_deplacement(deplacement(documents=[self.fichier]))
        with mock.patch.object(reunions.subprocess, "Popen") as popen:
            reunions.montrer_document(d["id"], self.fichier)
        self.assertEqual(popen.call_args[0][0], ["explorer", "/select,", os.path.normpath(self.fichier)])

    def test_choisir_fichiers(self):
        sortie = subprocess.CompletedProcess([], 0, stdout=f"{self.fichier}\r\nC:\\absent\\x.pdf\r\n", stderr="")
        with mock.patch.object(reunions.subprocess, "run", return_value=sortie) as run:
            r = reunions.choisir_fichiers("Billets")
        self.assertEqual(r, {"chemins": [self.fichier]}, "seuls les fichiers qui existent")
        self.assertEqual(run.call_args.kwargs["env"]["MO_TITRE"], "Billets")
        self.assertNotIn("shell", run.call_args.kwargs)


class TestAgenda(Base):
    def test_reunion(self):
        r = reunions.enregistrer_reunion(reunion(lieu="", lien="https://visio.exemple.test/x"))
        e = reunions.elements_agenda("reunion", r["id"])
        self.assertEqual(len(e["elements"]), 1)
        el = e["elements"][0]["element"]
        self.assertEqual((el["debut"], el["fin"], el["journee"], el["lieu"]), ("2026-03-03T14:30", "2026-03-03T15:15", False, "Visio"))
        self.assertIsNone(el["rappel_minutes"], "pas de second rappel : la bulle prévient déjà")
        self.assertNotIn("id", el)
        self.assertIn("- Planning", el["notes"])
        reunions.lier_agenda("reunion", r["id"], {"reunion": "rdv-1"})
        self.assertEqual(reunions.elements_agenda("reunion", r["id"])["elements"][0]["element"]["id"], "rdv-1",
                         "deuxième ajout : mise à jour du même rendez-vous")

    def test_deplacement_et_obsoletes(self):
        d = reunions.enregistrer_deplacement(deplacement(etapes=[
            {"type": "avion", "de": "Paris", "vers": "Montréal", "depart": "2026-03-10T22:00", "arrivee": "2026-03-11T01:00"}]))
        e = reunions.elements_agenda("deplacement", d["id"])
        cles = [x["cle"] for x in e["elements"]]
        self.assertEqual(cles[:2], ["aller", "retour"])
        etape = e["elements"][2]["element"]
        self.assertEqual((etape["titre"], etape["fin"]), ("Avion Paris → Montréal", "2026-03-10T23:59"),
                         "le rendez-vous reste dans sa journée")
        self.assertTrue(e["elements"][0]["element"]["journee"])
        reunions.lier_agenda("deplacement", d["id"], {x["cle"]: "id-" + x["cle"] for x in e["elements"]})
        sans_etape = reunions.enregistrer_deplacement({**reunions.liste()["deplacements"][0], "etapes": [], "retour": ""})
        e2 = reunions.elements_agenda("deplacement", sans_etape["id"])
        self.assertEqual([x["cle"] for x in e2["elements"]], ["aller"])
        self.assertEqual(sorted(e2["obsoletes"]), sorted(["id-retour", "id-" + cles[2]]))

    def test_erreurs(self):
        with self.assertRaisesRegex(ValueError, "Genre"):
            reunions.elements_agenda("autre", "x")
        with self.assertRaisesRegex(ValueError, "introuvable"):
            reunions.lier_agenda("deplacement", "x", {})


class TestAlertes(Base):
    def test_rappel_15_minutes_avant(self):
        r = reunions.enregistrer_reunion(reunion())                 # mardi 14:30
        self.horloge.aller("2026-03-03T14:14")
        self.assertEqual(reunions.alertes_dues(), [])
        self.horloge.aller("2026-03-03T14:15")
        a = reunions.alertes_dues()
        self.assertEqual(len(a), 1)
        self.assertEqual(a[0]["titre"], "Réunion : Point d'équipe")
        self.assertEqual(a[0]["detail"], "Dans 15 min · 14:30 · Salle B")
        self.assertTrue(reunions.marquer_alerte(a[0]["id"]))
        self.assertEqual(reunions.alertes_dues(), [], "vue : elle ne revient pas")
        # Réunion déplacée : nouveau rappel.
        reunions.enregistrer_reunion({**r, "debut": "2026-03-03T14:25"})
        self.assertEqual(len(reunions.alertes_dues()), 1)
        self.horloge.aller("2026-03-03T14:26")
        self.assertEqual(reunions.alertes_dues(), [], "réunion commencée : plus de rappel")

    def test_veille_du_depart(self):
        d = reunions.enregistrer_deplacement(deplacement())        # départ le 10, train 08:12
        self.horloge.aller("2026-03-09T08:59")
        self.assertEqual(reunions.alertes_dues(), [])
        self.horloge.aller("2026-03-09T18:00")
        a = reunions.alertes_dues()
        self.assertEqual(len(a), 1)
        self.assertEqual(a[0]["titre"], "Départ demain : Lyon")
        self.assertEqual(a[0]["detail"], "08:12 Train Paris → Lyon · réf. ABC123 · 2 élément(s) à cocher dans la liste")
        self.horloge.aller("2026-03-10T07:00")
        self.assertEqual(reunions.alertes_dues()[0]["titre"], "Départ aujourd'hui : Lyon", "PC éteint la veille")
        self.horloge.aller("2026-03-10T08:13")
        self.assertEqual(reunions.alertes_dues(), [], "parti : plus de rappel")
        self.horloge.aller("2026-03-09T18:00")
        reunions.marquer_alerte(f"depart:{d['id']}:2026-03-10")
        self.assertEqual(reunions.alertes_dues(), [])
        self.assertFalse(reunions.marquer_alerte(""))


class TestAccueil(Base):
    def test_prochains(self):
        self.assertEqual((reunions.prochains()["reunion"], reunions.prochains()["deplacement"]), (None, None))
        reunions.enregistrer_reunion(reunion(titre="Loin", debut="2026-03-20T09:00"))
        reunions.enregistrer_reunion(reunion(titre="Passée", debut="2026-03-01T09:00"))
        reunions.enregistrer_deplacement(deplacement(destination="Loin", depart="2026-03-20", retour=""))
        self.assertIsNone(reunions.prochains()["reunion"], "au-delà de 7 jours : rien")
        self.assertIsNone(reunions.prochains()["deplacement"])
        reunions.enregistrer_reunion(reunion(titre="Bientôt", debut="2026-03-04T09:00"))
        reunions.enregistrer_deplacement(deplacement(destination="En cours", depart="2026-03-01", retour="2026-03-03"))
        p = reunions.prochains()
        self.assertEqual(p["reunion"]["titre"], "Bientôt")
        self.assertEqual(p["deplacement"]["destination"], "En cours", "un déplacement en cours compte")


class TestRoutes(ServeurTest):
    def test_parcours(self):
        with ConfigTemporaire({"outils": []}):
            statut, r = self.post("/api/reunions/reunion/enregistrer", {"reunion": reunion()})
            self.assertEqual(statut, 200, r)
            statut, l = self.post("/api/reunions/liste", {})
            self.assertEqual((statut, len(l["reunions"]), l["deplacements"]), (200, 1, []))
            statut, cr = self.post("/api/reunions/reunion/compte_rendu", {"id": r["id"]})
            self.assertEqual(statut, 200)
            self.assertIn("Compte rendu", cr["texte"])
            statut, e = self.post("/api/reunions/reunion/enregistrer", {"reunion": {"titre": ""}})
            self.assertEqual(statut, 400)
            self.assertEqual(e["erreur"], "Donnez un titre à la réunion.")
            statut, d = self.post("/api/reunions/deplacement/enregistrer", {"deplacement": deplacement()})
            self.assertEqual(statut, 200, d)
            statut, f = self.post("/api/reunions/deplacement/feuille_de_route", {"id": d["id"]})
            self.assertEqual((statut, len(f["jours"])), (200, 2))
            statut, a = self.post("/api/reunions/accueil", {})
            self.assertEqual(statut, 200)
            self.assertIn("reunion", a)
            self.assertEqual(self.post("/api/reunions/alertes", {})[0], 200)
            statut, s = self.post("/api/reunions/reunion/supprimer", {"id": r["id"]})
            self.assertEqual(s, {"supprimes": 1})
            self.assertEqual(self.post("/api/reunions/inconnue", {})[0], 404)

    def test_sans_entete_refuse(self):
        with ConfigTemporaire({"outils": []}):
            statut, _ = self.post("/api/reunions/liste", {}, entete=False)
        self.assertEqual(statut, 403)


BLOC = re.compile(r"I18N\.ajouter\(\{(.*?)\}\);", re.S)
PAIRE = re.compile(r'"((?:[^"\\]|\\.)*)"\s*:\s*"((?:[^"\\]|\\.)*)"')


def paires(nom):
    with open(os.path.join(WEB, nom), encoding="utf-8") as f:
        texte = f.read()
    for bloc in BLOC.findall(texte):
        bloc = re.sub(r"^\s*//.*$", "", bloc, flags=re.M)
        yield from PAIRE.findall(bloc)


class TestPage(unittest.TestCase):
    def test_dictionnaire(self):
        mes_paires = list(paires("reunions.js"))
        self.assertGreater(len(mes_paires), 50)
        for cle, valeur in mes_paires:
            self.assertEqual(set(re.findall(r"\{(\w+)\}", cle)), set(re.findall(r"\{(\w+)\}", valeur)),
                             f"variables différentes entre « {cle} » et « {valeur} »")
        miennes = dict(mes_paires)
        for nom in sorted(os.listdir(WEB)):
            if not nom.endswith(".js") or nom == "reunions.js":
                continue
            for cle, valeur in paires(nom):
                if cle in miennes:
                    self.assertEqual(miennes[cle], valeur, f"« {cle} » traduit autrement dans {nom}")

    def test_sans_emoji_ni_innerhtml(self):
        with open(os.path.join(WEB, "reunions.js"), encoding="utf-8") as f:
            code = f.read()
        self.assertIsNone(re.search(r"[\U0001F000-\U0001FAFF\u2600-\u27BF]", code), "aucun emoji dans l'interface")
        self.assertNotIn("innerHTML", code)
        self.assertIsNone(re.search(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b", code), "aucune couleur en dur")

    @unittest.skipUnless(shutil.which("node"), "node absent")
    def test_syntaxe_js(self):
        r = subprocess.run(["node", "--check", os.path.join(WEB, "reunions.js")], capture_output=True, text=True,
                           timeout=30, creationflags=0x08000000)
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
