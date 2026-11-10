# -*- coding: utf-8 -*-
"""Tests de l'application Échéances : dates (fin de mois, années
bissextiles), montants au centime, coûts ramenés au mois, « payé /
renouvelé », rappels de la bulle avec une horloge simulée, export CSV, routes."""
import csv
import datetime
import io
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # aide.py, quel que soit le lancement

from aide import ConfigTemporaire, ServeurTest  # noqa: E402

import echeances  # noqa: E402

D = datetime.date


class Horloge:
    """Date du jour simulée : avancer(jours=…)."""

    def __init__(self, depart="2026-03-04"):     # un mercredi
        self.jour = D.fromisoformat(depart)

    def __call__(self):
        return self.jour

    def avancer(self, jours):
        self.jour += datetime.timedelta(days=jours)


def fiche(**valeurs):
    base = {"nom": "Hébergement", "categorie": "logiciel", "montant": "10,00", "devise": "EUR",
            "frequence": "mensuelle", "prochaine": "2026-03-10"}
    base.update(valeurs)
    return base


class Base(unittest.TestCase):
    def setUp(self):
        self.cfg = ConfigTemporaire({"outils": [], "langue": "fr"})
        self.cfg.__enter__()
        self.horloge = Horloge()
        self.patch = mock.patch.object(echeances, "aujourdhui", self.horloge)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.cfg.__exit__(None, None, None)


class TestDates(unittest.TestCase):
    def test_fin_de_mois_et_bissextile(self):
        a = echeances.ajouter_mois
        self.assertEqual(a(D(2026, 1, 31), 1), D(2026, 2, 28), "31 janvier → dernier jour de février")
        self.assertEqual(a(D(2028, 1, 31), 1), D(2028, 2, 29), "année bissextile")
        self.assertEqual(a(D(2026, 2, 28), 1, 31), D(2026, 3, 31), "le jour d'origine revient")
        self.assertEqual(a(D(2026, 10, 31), 3), D(2027, 1, 31), "changement d'année")
        self.assertEqual(a(D(2024, 2, 29), 12), D(2025, 2, 28))
        self.assertEqual(a(D(2027, 2, 28), 12, 29), D(2028, 2, 29), "29 février retrouvé")
        self.assertEqual(a(D(2026, 12, 15), 1), D(2027, 1, 15))
        self.assertEqual(a(D(2026, 5, 31), 1), D(2026, 6, 30))


class TestMontants(unittest.TestCase):
    def test_centimes(self):
        c = echeances.centimes
        self.assertEqual(c("1 234,56"), 123456)
        self.assertEqual(c("12.5"), 1250)
        self.assertEqual(c(" 0,1 "), 10)
        self.assertEqual(c(12), 1200)
        self.assertEqual(c("1 000"), 100000)
        self.assertEqual(c("1,234.56"), 123456, "écriture anglaise")
        self.assertEqual(c("1.234,56"), 123456)
        self.assertEqual(c(""), 0)
        for mauvais in ("12,345", "1.2.3", "abc", "-5", "1e400", "NaN", True):
            with self.assertRaises(ValueError, msg=f"refusé : {mauvais!r}"):
                c(mauvais)

    def test_couts_exacts(self):
        elements = [
            {"devise": "EUR", "categorie": "logiciel", "montant_centimes": 1000, "frequence": "trimestrielle", "statut": "actif"},
            {"devise": "EUR", "categorie": "logiciel", "montant_centimes": 1000, "frequence": "trimestrielle", "statut": "actif"},
            {"devise": "EUR", "categorie": "logiciel", "montant_centimes": 1000, "frequence": "trimestrielle", "statut": "a_resilier"},
            {"devise": "EUR", "categorie": "domaine", "montant_centimes": 1199, "frequence": "annuelle", "statut": "actif"},
            {"devise": "EUR", "categorie": "loyer", "montant_centimes": 50000, "frequence": "mensuelle", "statut": "resilie"},
            {"devise": "EUR", "categorie": "contrat", "montant_centimes": 9999, "frequence": "unique", "statut": "actif"},
            {"devise": "USD", "categorie": "licence", "montant_centimes": 1000, "frequence": "mois", "mois": 7, "statut": "actif"},
        ]
        r = echeances.couts(elements)
        # 3 × 10,00 / 3 = 10,00 exactement (et non 3 × 3,33 = 9,99) ; 11,99 / 12 = 0,999… ; total 10,999… → 11,00.
        self.assertEqual(r["EUR"]["mensuel"], 1100, "somme exacte, arrondi une seule fois")
        self.assertEqual(r["EUR"]["annuel"], 12000 + 1199)
        self.assertEqual(r["EUR"]["categories"], [{"categorie": "logiciel", "mensuel": 1000, "annuel": 12000},
                                                  {"categorie": "domaine", "mensuel": 100, "annuel": 1199}])
        self.assertEqual(r["USD"], {"mensuel": 143, "annuel": 1714,
                                    "categories": [{"categorie": "licence", "mensuel": 143, "annuel": 1714}]})
        self.assertEqual(echeances.arrondi(echeances.Fraction(1, 2)), 1, "0,5 vers le haut")


class TestFiches(Base):
    def test_validation(self):
        mauvaises = [fiche(nom=" "), fiche(categorie="x"), fiche(frequence="hebdo"), fiche(prochaine=""),
                     fiche(prochaine="31/02/2026"), fiche(devise="euro"), fiche(montant="1,234"),
                     fiche(statut="pause"), fiche(frequence="mois", mois=0), fiche(rappel_jours=-1),
                     fiche(paiement="Carte 4970 1012 3456 7890"), fiche(paiement="FR76 3000 6000 0112 3456 7890 189"),
                     fiche(lien="javascript:alert(1)"), fiche(tacite=True, preavis_jours="abc")]
        for f in mauvaises:
            with self.assertRaises(ValueError, msg=f"fiche refusée : {f}"):
                echeances.enregistrer(f)
        self.assertEqual(echeances.liste()["elements"], [])

    def test_ajout_modification(self):
        e = echeances.enregistrer(fiche(nom="  Suite   bureautique ", paiement="Carte pro (fin 1234)",
                                        lien="https://exemple.test/compte", devise="usd", tacite=True,
                                        preavis_jours=30, fournisseur="Éditeur Exemple", contact_id="c1"))
        self.assertEqual((e["nom"], e["devise"], e["montant_centimes"], e["jour_ancre"], e["rappel_jours"]),
                         ("Suite bureautique", "USD", 1000, 10, 7))
        m = echeances.enregistrer({**e, "montant": "12,99", "fournisseur": ""})
        self.assertEqual((m["montant_centimes"], m["contact_id"]), (1299, None), "plus de fournisseur : plus de contact")
        u = echeances.enregistrer(fiche(frequence="unique", tacite=True, preavis_jours=10))
        self.assertEqual((u["tacite"], u["preavis_jours"]), (False, 0), "pas de reconduction pour une date unique")
        with self.assertRaisesRegex(ValueError, "introuvable"):
            echeances.enregistrer({**e, "id": "inconnu"})
        self.assertTrue(echeances.supprimer(e["id"]))
        with self.assertRaises(ValueError):
            echeances.supprimer(e["id"])

    def test_payer_avance_et_annuler(self):
        e = echeances.enregistrer(fiche(prochaine="2026-01-31"))
        e = echeances.payer(e["id"])
        self.assertEqual(e["prochaine"], "2026-02-28")
        e = echeances.payer(e["id"])
        self.assertEqual(e["prochaine"], "2026-03-31", "le 31 revient après février")
        self.assertEqual(len(e["historique"]), 2)
        e = echeances.annuler_paiement(e["id"])
        self.assertEqual(e["prochaine"], "2026-02-28")
        # Modifier la fiche sans toucher à la date garde le jour d'origine.
        e = echeances.enregistrer({**e, "note": "à revoir"})
        self.assertEqual(echeances.payer(e["id"])["prochaine"], "2026-03-31")

        a = echeances.enregistrer(fiche(frequence="annuelle", prochaine="2028-02-29"))
        self.assertEqual(echeances.payer(a["id"])["prochaine"], "2029-02-28")
        t = echeances.enregistrer(fiche(frequence="mois", mois=4, prochaine="2026-11-30"))
        self.assertEqual(echeances.payer(t["id"])["prochaine"], "2027-03-30")

        u = echeances.enregistrer(fiche(frequence="unique", prochaine="2026-03-20"))
        u = echeances.payer(u["id"])
        self.assertEqual((u["statut"], u["prochaine"]), ("termine", "2026-03-20"))
        with self.assertRaisesRegex(ValueError, "plus active"):
            echeances.payer(u["id"])
        self.assertEqual(echeances.annuler_paiement(u["id"])["statut"], "actif")
        with self.assertRaisesRegex(ValueError, "Aucun paiement"):
            echeances.annuler_paiement(t["id"]) and echeances.annuler_paiement(t["id"])

    def test_groupes_et_accueil(self):
        # Mercredi 4 mars 2026 : semaine jusqu'au dimanche 8.
        for nom, date, statut in (("Retard", "2026-03-01", "actif"), ("Dimanche", "2026-03-08", "actif"),
                                  ("Lundi", "2026-03-09", "a_resilier"), ("Avril", "2026-04-02", "actif"),
                                  ("Fini", "2026-03-05", "resilie")):
            echeances.enregistrer(fiche(nom=nom, prochaine=date, statut=statut))
        r = echeances.liste()
        self.assertEqual([(e["nom"], e["groupe"], e["jours"]) for e in r["elements"]],
                         [("Retard", "semaine", -3), ("Fini", "resilies", 1), ("Dimanche", "semaine", 4),
                          ("Lundi", "mois", 5), ("Avril", "plus_tard", 29)])
        self.assertEqual(r["couts"]["EUR"]["mensuel"], 4000, "le résilié ne compte pas")
        a = echeances.accueil()
        self.assertEqual([e["nom"] for e in a["prochaines"]], ["Retard", "Dimanche", "Lundi"])
        self.assertEqual(a["couts"], {"EUR": {"mensuel": 4000}})
        for i in range(6):
            echeances.enregistrer(fiche(nom=f"N{i}", prochaine="2026-03-12"))
        a = echeances.accueil()
        self.assertEqual((len(a["prochaines"]), a["nombre"]), (5, 9), "au plus 5")


class TestAlertes(Base):
    def test_rappel_echeance(self):
        e = echeances.enregistrer(fiche(nom="Assurance pro", prochaine="2026-03-15", montant="1 234,5", rappel_jours=7))
        self.assertEqual(echeances.alertes_dues(), [], "11 jours avant : rien")
        self.horloge.avancer(4)                                  # 8 mars : 7 jours avant
        dues = echeances.alertes_dues()
        self.assertEqual(len(dues), 1)
        self.assertEqual(dues[0]["titre"], "Échéance : Assurance pro")
        self.assertEqual(dues[0]["detail"], "1 234,50 EUR le 15/03/2026 (dans 7 jours).")
        self.assertEqual(echeances.alertes_dues(), dues, "toujours due tant qu'elle n'est pas vue")
        self.assertTrue(echeances.marquer_alerte(dues[0]["id"]))
        self.assertEqual(echeances.alertes_dues(), [])
        self.assertFalse(echeances.marquer_alerte("inconnue"))
        # Payée : la période suivante aura son propre rappel.
        echeances.payer(e["id"])
        self.horloge.avancer(31)                                 # 8 avril
        dues = echeances.alertes_dues()
        self.assertEqual([a["id"] for a in dues], [f"{e['id']}:echeance:2026-04-15"])

    def test_retard_et_statuts(self):
        e = echeances.enregistrer(fiche(nom="Forfait", prochaine="2026-03-01"))
        dues = echeances.alertes_dues()
        self.assertEqual(dues[0]["titre"], "Échéance dépassée : Forfait")
        self.assertIn("en retard de 3 jours", dues[0]["detail"])
        echeances.changer_statut(e["id"], "resilie")
        self.assertEqual(echeances.alertes_dues(), [], "résilié : plus de rappel")
        with self.assertRaises(ValueError):
            echeances.changer_statut(e["id"], "inconnu")

    def test_preavis_tacite(self):
        # Échéance le 30 avril, préavis 30 jours : limite le 31 mars, rappel 7 jours avant.
        e = echeances.enregistrer(fiche(nom="Contrat ménage", frequence="annuelle", prochaine="2026-04-30",
                                        tacite=True, preavis_jours=30, rappel_jours=7))
        self.assertEqual(echeances.liste()["elements"][0]["limite_resiliation"], "2026-03-31")
        self.horloge.jour = D(2026, 3, 23)
        self.assertEqual(echeances.alertes_dues(), [])
        self.horloge.jour = D(2026, 3, 24)
        dues = echeances.alertes_dues()
        self.assertEqual([a["titre"] for a in dues], ["Résiliation : Contrat ménage"])
        self.assertIn("au plus tard le 31/03/2026 (dans 7 jours)", dues[0]["detail"])
        self.horloge.jour = D(2026, 4, 1)
        self.assertEqual(echeances.alertes_dues(), [], "limite passée : plus de rappel de résiliation")
        self.horloge.jour = D(2026, 4, 23)
        self.assertEqual([a["id"] for a in echeances.alertes_dues()], [f"{e['id']}:echeance:2026-04-30"])

    def test_alertes_en_anglais(self):
        with ConfigTemporaire({"outils": [], "langue": "en"}):
            echeances.enregistrer(fiche(nom="Domain", prochaine="2026-03-05", montant="1234.5"))
            dues = echeances.alertes_dues()
        self.assertEqual((dues[0]["titre"], dues[0]["detail"]), ("Due date: Domain", "1,234.50 EUR on 05/03/2026 (tomorrow)."))


class TestExport(Base):
    def test_export_csv(self):
        echeances.enregistrer(fiche(nom="=Formule", note="-2+3", montant="1 000,5", frequence="trimestrielle",
                                    tacite=True, preavis_jours=15, fournisseur="Fournisseur; Exemple"))
        echeances.enregistrer(fiche(nom="Domaine", categorie="domaine", montant="11,99", frequence="annuelle", prochaine="2026-03-05"))
        r = echeances.export_csv()
        self.assertEqual(r["nom"], "echeances-2026-03-04.csv")
        self.assertTrue(r["csv"].startswith("﻿"), "BOM UTF-8 pour Excel")
        lignes = list(csv.reader(io.StringIO(r["csv"][1:]), delimiter=";"))
        self.assertEqual(lignes[0][:4], ["Nom", "Catégorie", "Fournisseur", "Montant"])
        self.assertEqual(lignes[1][:7], ["Domaine", "Nom de domaine", "", "11,99", "EUR", "Annuelle", "2026-03-05"])
        self.assertEqual(lignes[1][-1], "1,00")
        self.assertEqual(lignes[2][0], "'=Formule", "pas de formule Excel")
        self.assertEqual(lignes[2][2], "Fournisseur; Exemple")
        self.assertEqual(lignes[2][7:10], ["Oui", "15", "2026-02-23"])
        self.assertEqual(lignes[2][14], "'-2+3")
        self.assertEqual(lignes[2][-1], "333,50")
        self.assertIn("\r\n", r["csv"])


class TestRoutes(ServeurTest):
    def test_routes(self):
        horloge = Horloge()
        with ConfigTemporaire(), mock.patch.object(echeances, "aujourdhui", horloge):
            statut, e = self.post("/api/echeances/enregistrer", {"element": fiche(prochaine="2026-03-06")})
            self.assertEqual((statut, e["montant_centimes"]), (200, 1000))
            statut, r = self.post("/api/echeances/enregistrer", {"element": fiche(montant="abc")})
            self.assertEqual((statut, r.get("erreur")), (400, "Montant invalide."))
            statut, r = self.post("/api/echeances/liste", {})
            self.assertEqual((statut, len(r["elements"]), r["elements"][0]["groupe"], r["couts"]["EUR"]["mensuel"]),
                             (200, 1, "semaine", 1000))
            statut, r = self.post("/api/echeances/alertes", {})
            self.assertEqual(len(r["alertes"]), 1)
            statut, r = self.post("/api/echeances/marquer_alerte", {"id": r["alertes"][0]["id"]})
            self.assertEqual(r, {"ok": True})
            statut, r = self.post("/api/echeances/payer", {"id": e["id"]})
            self.assertEqual((statut, r["prochaine"]), (200, "2026-04-06"))
            statut, r = self.post("/api/echeances/annuler_paiement", {"id": e["id"]})
            self.assertEqual(r["prochaine"], "2026-03-06")
            statut, r = self.post("/api/echeances/statut", {"id": e["id"], "statut": "a_resilier"})
            self.assertEqual(r["statut"], "a_resilier")
            statut, r = self.post("/api/echeances/accueil", {})
            self.assertEqual((statut, len(r["prochaines"])), (200, 1))
            statut, r = self.post("/api/echeances/export", {})
            self.assertEqual((statut, r["nom"]), (200, "echeances-2026-03-04.csv"))
            statut, r = self.post("/api/echeances/supprimer", {"id": e["id"]})
            self.assertEqual((statut, r), (200, {"ok": True}))
            statut, r = self.post("/api/echeances/payer", {"id": e["id"]})
            self.assertEqual(statut, 400)


if __name__ == "__main__":
    unittest.main()
