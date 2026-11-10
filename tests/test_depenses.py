# -*- coding: utf-8 -*-
"""Tests de l'application Dépenses : montants exacts, charges fixes
(automatiques, rattrapage, jamais recréées), budget reconduit, épargne
(reprise confirmée, plafonnée, annulable), catégories, statistiques, notes de
frais (justificatif, statut, export CSV), alertes de la bulle, routes."""
import csv
import datetime
import io
import os
import sys
import unittest
from decimal import Decimal
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # aide.py, quel que soit le lancement

from aide import ConfigTemporaire, ServeurTest  # noqa: E402

import config  # noqa: E402
import depenses  # noqa: E402


class Jour:
    """Date du jour simulée."""

    def __init__(self, iso="2026-03-15"):
        self.d = datetime.date.fromisoformat(iso)

    def __call__(self):
        return self.d

    def aller(self, iso):
        self.d = datetime.date.fromisoformat(iso)


class Base(unittest.TestCase):
    def setUp(self):
        self.cfg = ConfigTemporaire({"outils": [], "langue": "fr"})
        self.cfg.__enter__()
        self.jour = Jour()
        self.patch = mock.patch.object(depenses, "aujourdhui", self.jour)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.cfg.__exit__(None, None, None)

    def ajouter(self, montant, categorie="alimentation", date="2026-03-10", reprise=None, **autres):
        return depenses.ajouter_depense({"montant": montant, "categorie": categorie, "date": date, **autres}, reprise)


class TestMontantsEtCategories(Base):
    def test_montants_au_centime(self):
        self.assertEqual(depenses._montant("1 250,5"), Decimal("1250.50"))
        self.assertEqual(depenses._montant("0,105"), Decimal("0.11"), "arrondi au centime supérieur")
        for mauvais in ("", "abc", "-3", "0", "1e5", None, True, "9999999999999"):
            with self.assertRaises(ValueError, msg=f"« {mauvais} » doit être refusé"):
                depenses._montant(mauvais)
        a = self.ajouter("0,10")["depense"]
        self.ajouter("0,20")
        r = depenses.liste_mois({"mois": "2026-03"})
        self.assertEqual(r["total"], "0.30", "0,10 + 0,20 = 0,30 exactement (jamais de float)")
        self.assertEqual(a["montant"], "0.10")

    def test_devise_mga_sans_centimes(self):
        depenses.changer_devise("MGA")
        self.assertEqual(depenses._montant("1250,6"), Decimal("1251"))
        with self.assertRaises(ValueError):
            depenses.changer_devise("GBP")
        self.assertEqual(depenses.devise(), "MGA")

    def test_categories_par_defaut_et_epargne(self):
        cats = depenses.reglages()["categories"]
        self.assertEqual(len(cats), 11)
        epargne = [c for c in cats if c["epargne"]]
        self.assertEqual([c["nom"] for c in epargne], ["Épargne"], "une seule catégorie Épargne")
        with self.assertRaisesRegex(ValueError, "Épargne ne peut pas être supprimée"):
            depenses.supprimer_categorie("epargne", "autres")
        depenses.modifier_categorie({"id": "epargne", "nom": "Mise de côté", "icone": "piggy-bank", "couleur": "menthe"})
        self.assertEqual(depenses._lire()["categories"][9]["nom"], "Mise de côté", "renommable")

    def test_supprimer_categorie_avec_remplacement(self):
        c = depenses.ajouter_categorie({"nom": "Voyages", "icone": "plane", "couleur": "bleu"})
        with self.assertRaisesRegex(ValueError, "porte déjà ce nom"):
            depenses.ajouter_categorie({"nom": "voyages"})
        with self.assertRaises(ValueError):
            depenses.ajouter_categorie({"nom": "X", "icone": "inconnue"})
        self.ajouter("50", categorie=c["id"])
        depenses.ajouter_charge({"montant": "10", "categorie": c["id"], "description": "Assurance", "jour": 3})
        with self.assertRaisesRegex(ValueError, "remplacement"):
            depenses.supprimer_categorie(c["id"])
        depenses.supprimer_categorie(c["id"], "autres")
        d = depenses._lire()
        self.assertTrue(all(x["categorie"] == "autres" for x in d["depenses"] + d["charges"]),
                        "dépenses et charges déplacées")


class TestChargesFixes(Base):
    def test_ajoutee_chaque_mois_rattrapage_et_jour_31(self):
        self.jour.aller("2026-01-20")
        c = depenses.ajouter_charge({"montant": "800", "categorie": "logement", "description": "Loyer", "jour": 31})
        self.assertEqual([x["date"] for x in depenses._lire()["depenses"]], ["2026-01-31"], "compte dès ce mois")
        self.jour.aller("2026-04-02")                       # appli pas ouverte pendant deux mois
        r = depenses.liste_mois({"mois": "2026-02"})
        self.assertEqual([x["date"] for x in r["depenses"]], ["2026-02-28"], "le 31 devient le 28")
        dates = sorted(x["date"] for x in depenses._lire()["depenses"])
        self.assertEqual(dates, ["2026-01-31", "2026-02-28", "2026-03-31", "2026-04-30"], "mois manquants rattrapés")
        depenses.liste_mois({})
        self.assertEqual(len(depenses._lire()["depenses"]), 4, "jamais en double")
        self.assertEqual(depenses.liste_mois({"mois": "2026-04"})["fixes"], "800.00")
        self.assertEqual(c["debut"], "2026-01")

    def test_supprimee_jamais_recreee_modifier_arreter(self):
        c = depenses.ajouter_charge({"montant": "30", "categorie": "abonnements", "description": "Internet", "jour": 5})
        dep = depenses._lire()["depenses"][0]
        depenses.supprimer_depense(dep["id"])
        depenses.tableau()
        self.assertEqual(depenses._lire()["depenses"], [], "supprimée à la main : jamais recréée")
        self.jour.aller("2026-04-10")
        depenses.tableau()
        avril = depenses._lire()["depenses"][0]
        self.assertEqual((avril["date"], avril["montant"]), ("2026-04-05", "30.00"))
        depenses.modifier_charge({**c, "montant": "35,90", "jour": 8})
        avril = depenses._lire()["depenses"][0]
        self.assertEqual((avril["date"], avril["montant"]), ("2026-04-08", "35.90"), "le mois en cours suit la charge")
        depenses.arreter_charge(c["id"])
        self.jour.aller("2026-05-10")
        depenses.tableau()
        self.assertEqual(len(depenses._lire()["depenses"]), 1, "arrêtée : plus ajoutée, l'ancienne est gardée")
        with self.assertRaises(ValueError):
            depenses.arreter_charge(c["id"])

    def test_charge_refusee(self):
        for mauvaise in ({"montant": "10", "categorie": "logement", "description": "", "jour": 1},
                         {"montant": "10", "categorie": "logement", "description": "X", "jour": 32},
                         {"montant": "10", "categorie": "inconnue", "description": "X", "jour": 1}):
            with self.assertRaises(ValueError):
                depenses.ajouter_charge(mauvaise)


class TestBudgetEtEpargne(Base):
    def preparer(self):
        """Budget 2 000, épargne 300 / mois (charge fixe), 1 650 déjà dépensés."""
        depenses.definir_budget("2000")
        depenses.ajouter_charge({"montant": "300", "categorie": "epargne", "description": "Livret", "jour": 1})
        self.ajouter("1350")

    def test_budget_reconduit(self):
        self.jour.aller("2026-01-05")
        depenses.definir_budget("1500")
        self.jour.aller("2026-03-15")
        b = depenses.page_budget()
        self.assertEqual(b["budget"]["budget"], "1500.00", "reconduit tant qu'il n'est pas modifié")
        depenses.definir_budget("0")
        self.assertNotIn("niveau", depenses.page_budget()["budget"], "0 : pas de budget")
        self.assertEqual(depenses.page_budget()["historique"][2]["budget"], "1500.00", "janvier inchangé")

    def test_depassement_propose_reprise_sans_rien_enregistrer(self):
        self.preparer()
        r = self.ajouter("400")
        self.assertEqual(r, {"ajoutee": False, "epargne": {"depassement": "50.00", "disponible": "300.00",
                                                           "suggere": "50.00"}})
        self.assertEqual(len(depenses._lire()["depenses"]), 2, "rien n'est enregistré sans confirmation")
        r = self.ajouter("400", reprise="40")
        self.assertTrue(r["ajoutee"])
        e = depenses.page_epargne()
        self.assertEqual((e["disponible"], e["ce_mois"]["verse"], e["ce_mois"]["repris"], e["ce_mois"]["net"]),
                         ("260.00", "300.00", "40.00", "260.00"))
        t = depenses.tableau()
        self.assertEqual(t["budget"]["depense"], "2010.00", "dépensé effectif = dépenses − reprises")
        self.assertEqual(t["budget"]["niveau"], "depasse")
        # Ajouter sans toucher à l'épargne
        r = self.ajouter("5", reprise=0)
        self.assertEqual((r["ajoutee"], r["repris"]), (True, "0.00"))

    def test_reprise_plafonnee_et_annulable(self):
        self.preparer()
        with self.assertRaisesRegex(ValueError, "ne suffit pas"):
            self.ajouter("500", reprise="301")
        with self.assertRaisesRegex(ValueError, "invalide"):
            self.ajouter("20", reprise="25")
        r = self.ajouter("400", reprise="50")
        self.assertEqual(depenses.page_budget()["budget"]["depense"], "2000.00", "le mois n'est plus dépassé")
        reprise = depenses.page_epargne()["reprises"][0]
        self.assertEqual(reprise["depense_info"]["montant"], "400.00")
        with self.assertRaisesRegex(ValueError, "inférieur"):
            depenses.modifier_depense({**r["depense"], "montant": "30"})
        depenses.annuler_reprise(reprise["id"])
        self.assertEqual(depenses.page_epargne()["disponible"], "300.00", "la somme revient dans l'épargne")
        self.assertEqual(len(depenses._lire()["depenses"]), 3, "la dépense est conservée")

    def test_epargne_des_mois_passes_jamais_au_dela(self):
        self.jour.aller("2026-01-10")
        depenses.ajouter_charge({"montant": "300", "categorie": "epargne", "description": "Livret", "jour": 1})
        self.jour.aller("2026-03-15")
        depenses.definir_budget("1000")
        self.ajouter("700")                                  # 700 + 300 = budget atteint
        r = self.ajouter("1000")
        self.assertEqual(r["epargne"], {"depassement": "1000.00", "disponible": "900.00", "suggere": "900.00"},
                         "on puise dans l'épargne des mois passés, jamais au-delà")
        self.ajouter("1000", reprise="900")
        e = depenses.page_epargne()
        self.assertEqual((e["disponible"], e["ce_mois"]["net"]), ("0.00", "-600.00"))
        self.assertIsNone(self.ajouter("10").get("epargne"), "plus d'épargne : plus de question")

    def test_supprimer_depense_annule_reprise(self):
        self.preparer()
        r = self.ajouter("400", reprise="50")
        depenses.supprimer_depense(r["depense"]["id"])
        self.assertEqual(depenses._lire()["reprises"], [])
        self.assertEqual(depenses.page_epargne()["disponible"], "300.00")

    def test_alertes_budget(self):
        self.assertEqual(depenses.alertes_dues(), [])
        depenses.definir_budget("100")
        self.ajouter("99,99")
        self.assertEqual(depenses.alertes_dues(), [])
        self.ajouter("0,02")
        dues = depenses.alertes_dues()
        self.assertEqual(dues[0]["id"], "budget-2026-03")
        self.assertEqual(dues[0]["detail"], "Dépensé 100,01 € sur 100 € ce mois-ci.")
        self.assertTrue(depenses.marquer_alerte("budget-2026-03"))
        self.assertEqual(depenses.alertes_dues(), [], "une fois par mois")
        self.assertFalse(depenses.marquer_alerte("../autre"))


class TestStatistiques(Base):
    def test_stats(self):
        self.ajouter("100", date="2026-02-10")
        self.ajouter("50", date="2026-02-20", categorie="transport")
        self.ajouter("80", date="2026-03-05")
        self.ajouter("40,50", date="2026-03-12", categorie="transport", description="Train")
        s = depenses.statistiques({"periode": "mois"})
        self.assertEqual(s["total"], "120.50")
        self.assertEqual(s["moyenne"], "8.03", "120,50 sur 15 jours écoulés")
        self.assertEqual(s["par_categorie"][0]["id"], "alimentation")
        self.assertEqual(s["plus_grosse"]["montant"], "80.00")
        c = s["comparaison"]
        self.assertEqual((c["dernier_a_date"], c["ce_mois_a_date"], c["variation"]), ("100.00", "120.50", 0.205))
        self.assertEqual(len(s["series"]["jour"]), 31)
        self.assertEqual(len(s["series"]["semaine"]), 12)
        self.assertEqual(s["series"]["mois"][-1], {"cle": "2026-03", "total": "120.50"})
        self.assertEqual(s["derniers_mois"][1]["mois"], "2026-02")
        self.assertTrue(s["derniers_mois"][0]["en_cours"])
        self.assertEqual(depenses.statistiques({"periode": "precedent"})["total"], "150.00")
        self.assertFalse(s["vide"])


class TestNotesDeFrais(Base):
    def test_justificatif_statut_export(self):
        source = os.path.join(self.cfg.dossier, "ticket taxi.pdf")
        with open(source, "wb") as f:
            f.write(b"%PDF-1.4 essai")
        r = self.ajouter("42,30", categorie="transport", description="Taxi gare", pro=True,
                         client_id="c1", client_nom="Société Exemple", justificatif_source=source)
        dep = r["depense"]
        self.assertEqual(dep["statut"], "a_rembourser")
        chemin = os.path.join(config.DONNEES, "depenses", "justificatifs", dep["justificatif"])
        self.assertTrue(os.path.isfile(chemin), "justificatif copié dans donnees/depenses/justificatifs")
        self.assertTrue(os.path.isfile(source), "l'original n'est pas touché")
        self.ajouter("12", description="=HYPERLIEN()")      # dépense personnelle
        n = depenses.notes_de_frais({})
        self.assertEqual((len(n["notes"]), n["totaux"]["a_rembourser"]["total"]), (1, "42.30"))
        depenses.changer_statut(dep["id"], "refacturee")
        self.assertEqual(depenses.notes_de_frais({"statut": "refacturee"})["total"], "42.30")
        with self.assertRaises(ValueError):
            depenses.changer_statut(dep["id"], "payee")
        r = depenses.export_csv({"mois": "2026-03"})
        self.assertTrue(r["csv"].startswith("﻿"), "BOM UTF-8 pour Excel")
        lignes = list(csv.reader(io.StringIO(r["csv"][1:]), delimiter=";"))
        self.assertEqual(lignes[0][:4], ["Date", "Description", "Catégorie", "Montant"])
        self.assertEqual(lignes[1], ["10/03/2026", "Taxi gare", "Transport", "42,30", "EUR", "Carte bancaire", "Oui",
                                     "Société Exemple", "Refacturée", dep["justificatif"], ""])
        self.assertEqual(lignes[2][1], "'=HYPERLIEN()", "pas de formule Excel")
        self.assertEqual(lignes[-1][:5], ["Total", "", "", "54,30", "EUR"])
        r = depenses.export_csv({"pro": True})
        self.assertEqual((r["nom"], r["lignes"]), ("notes-de-frais-tout.csv", 1))
        with mock.patch.object(depenses, "_ouvrir") as ouvrir:
            depenses.ouvrir_justificatif(dep["id"])
            ouvrir.assert_called_once_with(chemin)
        depenses.supprimer_depense(dep["id"])
        self.assertFalse(os.path.exists(chemin), "justificatif supprimé avec la dépense")

    def test_justificatif_refuse(self):
        source = os.path.join(self.cfg.dossier, "script.exe")
        with open(source, "wb") as f:
            f.write(b"MZ")
        with self.assertRaisesRegex(ValueError, "photo ou un PDF"):
            self.ajouter("10", justificatif_source=source)
        with self.assertRaisesRegex(ValueError, "introuvable"):
            self.ajouter("10", justificatif_source=os.path.join(self.cfg.dossier, "absent.pdf"))
        self.assertEqual(depenses._lire()["depenses"], [], "rien d'enregistré")
        with self.assertRaises(ValueError):
            depenses._chemin_justificatif("..\\outils.json")

    def test_joindre_retirer_et_fenetre(self):
        dep = self.ajouter("10", pro=True)["depense"]
        source = os.path.join(self.cfg.dossier, "photo.JPG")
        with open(source, "wb") as f:
            f.write(b"\xff\xd8")
        dep = depenses.joindre_justificatif(dep["id"], source)
        self.assertTrue(dep["justificatif"].endswith("-photo.jpg"))
        dep = depenses.retirer_justificatif(dep["id"])
        self.assertIsNone(dep["justificatif"])
        sortie = mock.Mock(stdout=source + "\n")
        with mock.patch.object(depenses.systeme, "WINDOWS", True), \
                mock.patch.object(depenses.systeme.subprocess, "run", return_value=sortie) as run:
            self.assertEqual(depenses.choisir_fichier({}), {"chemin": source, "nom": "photo.JPG"})
            self.assertNotIn("shell", run.call_args.kwargs)
            self.assertEqual(run.call_args[0][0][0], "powershell")
            env = run.call_args.kwargs["env"]
            self.assertEqual(env["MO_MULTI"], "0", "un seul justificatif à la fois")
            self.assertEqual(env["MO_FILTRE"], "Justificatifs (photo, PDF)|*.pdf;*.png;*.jpg;*.jpeg;*.webp;*.gif;"
                                               "*.heic;*.bmp;*.tif;*.tiff", "filtre de Windows inchangé")
        with mock.patch.object(depenses.systeme, "WINDOWS", True), \
                mock.patch.object(depenses.systeme.subprocess, "run", return_value=mock.Mock(stdout="")):
            self.assertEqual(depenses.choisir_fichier({}), {"chemin": None})

    def test_fenetre_et_ouverture_sous_linux(self):
        """Branche Linux simulée : zenity, motifs en majuscules aussi, xdg-open,
        et un message clair s'il n'y a aucune fenêtre."""
        source = os.path.join(self.cfg.dossier, "photo.JPG")
        with open(source, "wb") as f:
            f.write(b"\xff\xd8")
        with mock.patch.object(depenses.systeme, "WINDOWS", False), \
                mock.patch.object(depenses.systeme, "outil_de_fenetres", return_value="zenity"), \
                mock.patch.object(depenses.systeme.subprocess, "run", return_value=mock.Mock(stdout=source + "\n")) as run:
            self.assertEqual(depenses.choisir_fichier({}), {"chemin": source, "nom": "photo.JPG"})
        args = run.call_args[0][0]
        self.assertEqual(args[0], "zenity")
        self.assertNotIn("--multiple", args)
        filtre = next(a for a in args if a.startswith("--file-filter="))
        self.assertIn("*.jpg", filtre)
        self.assertIn("*.JPG", filtre, "Linux distingue les majuscules")
        self.assertNotIn("creationflags", run.call_args.kwargs)
        with mock.patch.object(depenses.systeme, "WINDOWS", False), \
                mock.patch.object(depenses.systeme, "outil_de_fenetres", return_value=None):
            with self.assertRaisesRegex(ValueError, "zenity"):
                depenses.choisir_fichier({})
        with mock.patch.object(depenses.systeme, "ouvrir") as ouvrir:
            depenses._ouvrir(source)
        ouvrir.assert_called_once_with(source)


class TestRoutes(ServeurTest):
    def test_routes(self):
        jour = Jour()
        with ConfigTemporaire(), mock.patch.object(depenses, "aujourdhui", jour):
            statut, r = self.post("/api/depenses/budget/definir", {"montant": "500"})
            self.assertEqual((statut, r["montant"]), (200, "500.00"))
            statut, r = self.post("/api/depenses/charges/ajouter", {"charge": {
                "montant": "100", "categorie": "epargne", "description": "Livret", "jour": 1}})
            self.assertEqual(statut, 200)
            statut, r = self.post("/api/depenses/ajouter", {"depense": {"montant": "450", "categorie": "alimentation",
                                                                        "date": "2026-03-14"}})
            self.assertEqual((statut, r["ajoutee"], r["epargne"]["suggere"]), (200, False, "50.00"))
            statut, r = self.post("/api/depenses/ajouter", {"depense": {"montant": "450", "categorie": "alimentation",
                                                                        "date": "2026-03-14"}, "reprise": "50"})
            self.assertEqual((statut, r["ajoutee"]), (200, True))
            statut, r = self.post("/api/depenses/tableau", {})
            self.assertEqual((statut, r["budget"]["depense"], r["epargne"]["disponible"]), (200, "500.00", "50.00"))
            statut, r = self.post("/api/depenses/resume", {})
            self.assertEqual((r["depense"], r["budget"], r["niveau"]), ("500.00", "500.00", "presque"))
            for route in ("liste", "charges", "budget", "epargne", "statistiques", "notes", "reglages", "export"):
                statut, r = self.post("/api/depenses/" + route, {})
                self.assertEqual(statut, 200, f"route {route}")
            statut, r = self.post("/api/depenses/ajouter", {"depense": {"montant": "abc", "categorie": "alimentation"}})
            self.assertEqual(statut, 400)
            statut, r = self.post("/api/depenses/categories/supprimer", {"id": "epargne"})
            self.assertEqual((statut, r["erreur"]), (400, "La catégorie Épargne ne peut pas être supprimée."))
            statut, r = self.post("/api/depenses/devise", {"devise": "USD"})
            self.assertEqual((statut, r["devise"]), (200, "USD"))


if __name__ == "__main__":
    unittest.main()
