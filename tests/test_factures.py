# -*- coding: utf-8 -*-
"""Tests de l'application Devis et factures : réglages, calculs exacts au
centime, numérotation, statuts, paiements, avoirs, retard et bulle, heures de
Temps, PDF (Edge simulé), mail, export CSV, routes."""
import base64
import csv
import datetime
import io
import os
import shutil
import sys
import tempfile
import unittest
from decimal import Decimal
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # aide.py, quel que soit le lancement

from aide import ConfigTemporaire, ServeurTest  # noqa: E402

import factures  # noqa: E402
import temps  # noqa: E402

ENTREPRISE = {"nom": "Studio Exemple", "adresse": "1 rue de l'Exemple\n75000 Paris",
              "identifiants": [{"libelle": "SIRET", "valeur": "000 000 000 00000"}],
              "tva_mode": "assujetti", "tva_taux": "20", "delai_jours": 30, "devise": "EUR",
              "iban": "FR76 3000 6000 0112 3456 7890 189", "bic": "AGRIFRPP", "penalites": factures.PENALITES_FR}

PNG = base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"\x00" * 40).decode()


def ligne(designation, quantite, prix, tva="20", unite=""):
    return {"designation": designation, "quantite": quantite, "prix": prix, "tva": tva, "unite": unite}


class BaseFactures(unittest.TestCase):
    def setUp(self):
        self.cfg = ConfigTemporaire({"outils": [], "langue": "fr"})
        self.cfg.__enter__()
        self.jour = datetime.date(2026, 3, 10)
        self.patchs = [mock.patch.object(factures, "aujourdhui", lambda: self.jour)]
        self.documents = tempfile.mkdtemp(prefix="mes-outils-docs-")
        self.patchs.append(mock.patch.object(factures, "dossier_documents", lambda: self.documents))
        for p in self.patchs:
            p.start()

    def tearDown(self):
        for p in self.patchs:
            p.stop()
        self.cfg.__exit__(None, None, None)
        shutil.rmtree(self.documents, ignore_errors=True)

    def configurer(self, **valeurs):
        return factures.enregistrer_entreprise({**ENTREPRISE, **valeurs})

    def facture(self, lignes=None, **valeurs):
        return factures.enregistrer({"type": "facture", "client": {"nom": "Client Alpha", "email": "client@example.com"},
                                     "lignes": lignes or [ligne("Développement", "2", "450")], **valeurs})

    def emettre(self, identifiant):
        return factures.emettre(identifiant, generer=False)["document"]


class TestReglages(BaseFactures):
    def test_premier_reglage(self):
        r = factures.reglages()
        self.assertFalse(r["configuree"])
        self.assertIn("40 €", r["entreprise"]["penalites"], "mention des pénalités proposée au premier réglage")
        r = self.configurer()
        self.assertTrue(r["configuree"])
        self.assertEqual(r["entreprise"]["iban"], "FR7630006000011234567890189")
        self.assertEqual(r["prochains"]["facture"], "FAC-2026-001")

    def test_refus(self):
        for mauvais in ({"nom": ""}, {"tva_mode": "libre", "tva_texte": ""}, {"tva_taux": "120"},
                        {"prefixe_devis": "FAC"}, {"prefixe_facture": "F-1"}, {"iban": "FR7630006000011234567890188"},
                        {"devise": "AUTRE", "devise_code": "1"}, {"delai_jours": "-3"}):
            with self.assertRaises(ValueError, msg=f"devrait être refusé : {mauvais}"):
                self.configurer(**mauvais)

    def test_devise_autre_et_mga(self):
        r = self.configurer(devise="AUTRE", devise_code="chf", devise_symbole="CHF", devise_decimales=2)
        self.assertEqual(r["devise"], {"code": "CHF", "symbole": "CHF", "decimales": 2})
        r = self.configurer(devise="MGA")
        self.assertEqual(r["devise"]["decimales"], 0)

    def test_logo(self):
        self.configurer()
        r = factures.enregistrer_logo("logo.png", PNG)
        self.assertTrue(r["logo_data"].startswith("data:image/png;base64,"))
        fichier = r["entreprise"]["logo"]
        self.assertTrue(os.path.isfile(os.path.join(factures.dossier_fichiers(), fichier)))
        with self.assertRaises(ValueError):
            factures.enregistrer_logo("logo.exe", PNG)
        with self.assertRaises(ValueError):
            factures.enregistrer_logo("logo.png", base64.b64encode(b"pas une image").decode())
        self.assertEqual(factures.retirer_logo()["logo_data"], "")


class TestCalculs(BaseFactures):
    def setUp(self):
        super().setUp()
        self.configurer()
        self.entreprise = factures._lire()["entreprise"]

    def totaux(self, lignes, remise=None):
        doc = {"lignes": [factures._ligne(x, i, "20") for i, x in enumerate(lignes, 1)],
               "remise": factures._remise(remise)}
        return factures.calculer(doc, self.entreprise)

    def test_pas_d_erreur_de_virgule_flottante(self):
        t = self.totaux([ligne("A", "3", "0.1"), ligne("B", "1", "0.2")])
        self.assertEqual((t["total_ht"], t["total_tva"], t["total_ttc"]), ("0.50", "0.10", "0.60"))
        t = self.totaux([ligne("A", "3", "19.99")])
        self.assertEqual((t["total_ht"], t["total_tva"], t["total_ttc"]), ("59.97", "11.99", "71.96"),
                         "11,994 arrondi à 11,99")
        t = self.totaux([ligne("A", "1", "1.005")])
        self.assertEqual(t["lignes"], ["1.01"], "arrondi commercial (0,5 vers le haut)")

    def test_plusieurs_taux_et_remise_repartie(self):
        t = self.totaux([ligne("A", "1", "100", "20"), ligne("B", "1", "50", "5.5"), ligne("C", "1", "33.33", "10")],
                        {"type": "pourcent", "valeur": "10"})
        self.assertEqual(t["sous_total"], "183.33")
        self.assertEqual(t["remise"], "18.33")
        self.assertEqual(t["total_ht"], "165.00")
        bases = sum(Decimal(x["base"]) for x in t["tva"])
        self.assertEqual(bases, Decimal("165.00"), "la remise répartie retombe exactement sur le total HT")
        self.assertEqual(Decimal(t["total_tva"]), sum(Decimal(x["montant"]) for x in t["tva"]))
        self.assertEqual(Decimal(t["total_ttc"]), Decimal(t["total_ht"]) + Decimal(t["total_tva"]))

    def test_remise_montant(self):
        t = self.totaux([ligne("A", "2", "40")], {"type": "montant", "valeur": "10"})
        self.assertEqual((t["total_ht"], t["total_tva"], t["total_ttc"]), ("70.00", "14.00", "84.00"))
        with self.assertRaisesRegex(ValueError, "remise dépasse"):
            self.totaux([ligne("A", "1", "5")], {"type": "montant", "valeur": "10"})

    def test_franchise_sans_tva(self):
        self.configurer(tva_mode="franchise")
        entreprise = factures._lire()["entreprise"]
        doc = {"lignes": [factures._ligne(ligne("A", "1,5", "1 000,00"), 1, "20")]}
        t = factures.calculer(doc, entreprise)
        self.assertEqual((t["total_ht"], t["total_tva"], t["total_ttc"], t["tva"]), ("1500.00", "0.00", "1500.00", []))

    def test_ariary_sans_decimales(self):
        self.configurer(devise="MGA", tva_taux="20")
        entreprise = factures._lire()["entreprise"]
        doc = {"lignes": [factures._ligne(ligne("A", "3", "3333"), 1, "20")]}
        t = factures.calculer(doc, entreprise)
        self.assertEqual((t["total_ht"], t["total_tva"], t["total_ttc"]), ("9999", "2000", "11999"))
        self.assertEqual(factures.formater_montant(Decimal("11999"), t["devise"], "fr"), "11 999 Ar")

    def test_saisies_refusees(self):
        for mauvaise in (ligne("A", "abc", "1"), ligne("A", "0", "1"), ligne("A", "1", "1.23456"), ligne("A", "1", "1", "150")):
            with self.assertRaises(ValueError, msg=f"devrait être refusée : {mauvaise}"):
                factures._ligne(mauvaise, 1, "20")

    def test_format(self):
        eur = {"code": "EUR", "symbole": "€", "decimales": 2}
        self.assertEqual(factures.formater_montant(Decimal("1234.5"), eur, "fr"), "1 234,50 €")
        self.assertEqual(factures.formater_montant(Decimal("1234.5"), eur, "en"), "€1,234.50")
        self.assertEqual(factures.formater_montant(Decimal("-12"), eur, "fr"), "-12,00 €")


class TestNumerotation(BaseFactures):
    def setUp(self):
        super().setUp()
        self.configurer()

    def test_brouillon_sans_numero_puis_numeros_continus(self):
        a = self.facture()
        self.assertIsNone(a["numero"], "un brouillon n'a pas de numéro")
        b = self.facture()
        devis = factures.enregistrer({"type": "devis", "client": {"nom": "Client Beta"}, "lignes": [ligne("Audit", "1", "800")]})
        # Émis dans l'ordre inverse de création : la numérotation suit l'émission.
        self.assertEqual(self.emettre(b["id"])["numero"], "FAC-2026-001")
        self.assertEqual(self.emettre(a["id"])["numero"], "FAC-2026-002")
        self.assertEqual(self.emettre(devis["id"])["numero"], "DEV-2026-001")
        self.jour = datetime.date(2027, 1, 2)
        c = self.facture()
        self.assertEqual(self.emettre(c["id"])["numero"], "FAC-2027-001", "nouvelle année : on repart à 1")

    def test_emis_non_modifiable_ni_supprimable(self):
        f = self.facture()
        emis = self.emettre(f["id"])
        self.assertEqual((emis["date"], emis["echeance"]), ("2026-03-10", "2026-04-09"))
        with self.assertRaisesRegex(ValueError, "plus modifiable"):
            factures.enregistrer({**f, "notes": "changé"})
        with self.assertRaises(ValueError):
            factures.supprimer(f["id"])
        with self.assertRaisesRegex(ValueError, "déjà émis"):
            self.emettre(f["id"])

    def test_photo_de_l_entreprise_a_l_emission(self):
        f = self.facture()
        self.emettre(f["id"])
        self.configurer(nom="Nouveau nom", tva_mode="franchise")
        doc = factures.document(f["id"])
        self.assertEqual(doc["entreprise"]["nom"], "Studio Exemple")
        self.assertEqual(doc["totaux"]["total_ttc"], "1080.00", "le document émis garde sa TVA d'origine")

    def test_emission_refusee(self):
        vide = factures.enregistrer({"type": "facture", "client": {"nom": ""}, "lignes": [ligne("A", "1", "10")]})
        with self.assertRaisesRegex(ValueError, "client"):
            self.emettre(vide["id"])
        sans_ligne = factures.enregistrer({"type": "facture", "client": {"nom": "X"}, "lignes": []})
        with self.assertRaisesRegex(ValueError, "ligne"):
            self.emettre(sans_ligne["id"])
        zero = factures.enregistrer({"type": "facture", "client": {"nom": "X"}, "lignes": [ligne("A", "1", "0.001")]})
        with self.assertRaisesRegex(ValueError, "supérieur à zéro"):
            self.emettre(zero["id"])

    def test_chronologie(self):
        f = self.facture()
        self.emettre(f["id"])
        self.jour = datetime.date(2026, 3, 1)   # horloge du PC reculée
        g = self.facture()
        with self.assertRaisesRegex(ValueError, "postérieure"):
            self.emettre(g["id"])


class TestCycle(BaseFactures):
    def setUp(self):
        super().setUp()
        self.configurer()

    def test_devis_transforme_en_facture(self):
        devis = factures.enregistrer({"type": "devis", "client": {"nom": "Client Beta"},
                                      "lignes": [ligne("Audit", "1", "800")], "remise": {"type": "pourcent", "valeur": "5"}})
        with self.assertRaisesRegex(ValueError, "Émettez"):
            factures.transformer(devis["id"])
        self.emettre(devis["id"])
        self.assertEqual(factures.document(devis["id"])["resume"]["etat"], "envoye")
        facture = factures.transformer(devis["id"])
        self.assertEqual((facture["type"], facture["numero"], facture["devis_id"]), ("facture", None, devis["id"]))
        self.assertEqual(facture["totaux"]["total_ht"], "760.00")
        self.assertEqual(factures.document(devis["id"])["resume"]["etat"], "facture")
        with self.assertRaisesRegex(ValueError, "déjà été transformé"):
            factures.transformer(devis["id"])
        factures.supprimer(facture["id"])
        self.assertEqual(factures.document(devis["id"])["resume"]["etat"], "accepte")

    def test_devis_refuse_et_expire(self):
        devis = factures.enregistrer({"type": "devis", "client": {"nom": "X"}, "lignes": [ligne("A", "1", "10")],
                                      "validite_jours": 15})
        self.emettre(devis["id"])
        self.assertEqual(factures.changer_statut(devis["id"], "refuse")["resume"]["etat"], "refuse")
        with self.assertRaises(ValueError):
            factures.transformer(devis["id"])
        factures.changer_statut(devis["id"], "emis")
        self.jour = datetime.date(2026, 4, 1)
        self.assertEqual(factures.document(devis["id"])["resume"]["etat"], "expire")

    def test_paiements_et_etats(self):
        f = self.facture()
        self.emettre(f["id"])
        self.assertEqual(factures.document(f["id"])["resume"]["etat"], "envoyee")
        r = factures.ajouter_paiement(f["id"], {"date": "2026-03-12", "montant": "300,10", "moyen": "virement"})
        self.assertEqual((r["resume"]["etat"], r["resume"]["reste"]), ("partielle", "779.90"))
        with self.assertRaisesRegex(ValueError, "dépasse le reste"):
            factures.ajouter_paiement(f["id"], {"date": "2026-03-12", "montant": "800", "moyen": "virement"})
        with self.assertRaisesRegex(ValueError, "décimales"):
            factures.ajouter_paiement(f["id"], {"date": "2026-03-12", "montant": "1.001", "moyen": "virement"})
        self.jour = datetime.date(2026, 4, 20)
        self.assertEqual(factures.document(f["id"])["resume"]["etat"], "retard")
        r = factures.ajouter_paiement(f["id"], {"date": "2026-04-20", "montant": "779.90", "moyen": "mobile_money"})
        self.assertEqual((r["resume"]["etat"], r["resume"]["reste"]), ("payee", "0.00"))
        r = factures.supprimer_paiement(f["id"], r["paiements"][0]["id"])
        self.assertEqual(r["resume"]["reste"], "300.10")

    def test_avoir(self):
        f = self.facture()
        self.emettre(f["id"])
        avoir = factures.creer_avoir(f["id"])
        self.assertEqual((avoir["type"], avoir["origine_numero"]), ("avoir", "FAC-2026-001"))
        avoir = factures.enregistrer({**avoir, "lignes": [ligne("Développement (annulation partielle)", "1", "450")]})
        doc = self.emettre(avoir["id"])
        self.assertEqual(doc["numero"], "AV-2026-001")
        r = factures.document(f["id"])["resume"]
        self.assertEqual((r["avoirs"], r["reste"]), ("540.00", "540.00"))
        avoir2 = factures.creer_avoir(f["id"])
        avoir2 = factures.enregistrer({**avoir2, "lignes": [ligne("Trop", "2", "450")]})
        with self.assertRaisesRegex(ValueError, "dépasse"):
            self.emettre(avoir2["id"])
        avoir2 = factures.enregistrer({**avoir2, "lignes": [ligne("Reste", "1", "450")]})
        self.emettre(avoir2["id"])
        self.assertEqual(factures.document(f["id"])["resume"]["etat"], "annulee")
        with self.assertRaises(ValueError):
            factures.enregistrer({"type": "avoir", "client": {"nom": "X"}, "lignes": []})

    def test_resume_et_alertes(self):
        f = self.facture()
        self.emettre(f["id"])
        g = self.facture([ligne("Maintenance", "1", "100")])
        self.emettre(g["id"])
        factures.ajouter_paiement(g["id"], {"date": "2026-03-11", "montant": "120", "moyen": "carte"})
        r = factures.resume()
        eur = r["devises"][0]
        self.assertEqual((eur["facture_mois"], eur["encaisse_mois"], eur["impaye"], r["nb_retard"]),
                         ("1200.00", "120.00", "1080.00", 0))
        self.assertEqual(factures.alertes_dues(), [])
        self.jour = datetime.date(2026, 4, 10)
        dues = factures.alertes_dues()
        self.assertEqual(len(dues), 1)
        self.assertEqual(dues[0]["titre"], "Facture en retard")
        self.assertIn("FAC-2026-001", dues[0]["detail"])
        self.assertIn("1 080,00", dues[0]["detail"])
        self.assertEqual(factures.resume()["nb_retard"], 1)
        self.assertTrue(factures.marquer_alerte(dues[0]["id"]))
        self.assertEqual(factures.alertes_dues(), [], "une seule fois")
        self.assertFalse(factures.marquer_alerte("retard-inconnu"))

    def test_dupliquer(self):
        f = self.facture(notes="Merci")
        self.emettre(f["id"])
        copie = factures.dupliquer(f["id"])
        self.assertEqual((copie["numero"], copie["notes"], copie["type"]), (None, "Merci", "facture"))


class TestHeures(BaseFactures):
    def test_import_des_sessions(self):
        self.configurer()
        a = temps.ajouter_session({"projet": "Site", "note": "maquette", "debut": "2026-03-02T09:00", "fin": "2026-03-02T10:10"})
        b = temps.ajouter_session({"projet": "Site", "debut": "2026-03-03T14:00", "fin": "2026-03-03T14:20"})
        temps.ajouter_session({"projet": "Autre", "debut": "2026-03-03T15:00", "fin": "2026-03-03T16:00"})
        r = factures.heures("Site")
        self.assertEqual((r["disponible"], len(r["sessions"]), r["projets"]), (True, 2, ["Autre", "Site"]))
        lignes = factures.lignes_heures([a["id"], b["id"]], "45", "projet")["lignes"]
        self.assertEqual(len(lignes), 1)
        self.assertEqual((lignes[0]["quantite"], lignes[0]["unite"], lignes[0]["prix"]), ("1.5", "h", "45"))
        self.assertEqual(lignes[0]["designation"], "Site – du 02/03/2026 au 03/03/2026")
        par_session = factures.lignes_heures([a["id"], b["id"]], "45", "session")["lignes"]
        self.assertEqual([x["quantite"] for x in par_session], ["1.17", "0.33"], "minutes → heures au centième")
        self.facture(lignes)
        self.assertTrue(all(s["facturee"] for s in factures.heures("Site")["sessions"]), "sessions déjà facturées")
        with self.assertRaises(ValueError):
            factures.lignes_heures([], "45")


class TestPdfMailExport(BaseFactures):
    def setUp(self):
        super().setUp()
        self.configurer()
        factures.enregistrer_logo("logo.png", PNG)

    def edge_simule(self, commande, **kw):
        sortie = next(a.split("=", 1)[1] for a in commande if a.startswith("--print-to-pdf="))
        self.commande = commande
        self.options = kw
        with open(sortie, "wb") as f:
            f.write(b"%PDF-1.4 simule")
        return mock.Mock(returncode=0)

    def test_html_echappe_et_mentions(self):
        f = self.facture([ligne("<script>alert(1)</script>", "1", "100")], prestation="mars 2026")
        html = factures.apercu(f["id"])["html"]
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("BROUILLON", html, "un brouillon est marqué")
        self.emettre(f["id"])
        html = factures.apercu(f["id"])["html"]
        for attendu in ("FAC-2026-001", "Studio Exemple", "SIRET", "FR76 3000", "40 €", "TVA 20 %", "120,00",
                        "Prestation : mars 2026", "data:image/png;base64,", "09/04/2026"):
            self.assertIn(attendu, html)
        self.assertNotIn("BROUILLON", html)

    def test_pied_de_page_sur(self):
        self.configurer(pied='Capital "1 000 €"</style><script>x</script>\nRCS Exemple')
        html = factures.apercu(self.facture()["id"])["html"]
        self.assertEqual(html.count("</style>"), 1, "le pied de page ne ferme pas la feuille de style")
        self.assertNotIn("<script>", html)
        self.assertIn("@bottom-center", html)
        self.assertIn("\\A RCS Exemple", html, "retour à la ligne dans le pied imprimé")

    def test_mention_franchise(self):
        self.configurer(tva_mode="franchise")
        f = self.facture()
        html = factures.apercu(f["id"])["html"]
        self.assertIn("art. 293 B du CGI", html)
        self.assertNotIn("TVA 20", html)

    def test_pdf_par_edge(self):
        f = self.facture()
        with mock.patch.object(factures.systeme, "WINDOWS", True), \
                mock.patch.object(factures.systeme, "navigateur_chromium", return_value="msedge.exe"), \
                mock.patch.object(factures.systeme.subprocess, "run", side_effect=self.edge_simule):
            r = factures.emettre(f["id"])
        self.assertIsNone(r["pdf_erreur"])
        attendu = os.path.join(self.documents, "Mes outils", "Factures", "2026", "FAC-2026-001 - Client Alpha.pdf")
        self.assertEqual(r["pdf"], attendu)
        self.assertTrue(os.path.isfile(attendu))
        self.assertEqual(self.commande[0], "msedge.exe")
        self.assertIn("--headless", self.commande)
        self.assertTrue(self.commande[-1].startswith("file:///"))
        if sys.platform == "win32":
            self.assertEqual(self.options.get("creationflags"), 0x08000000, "Windows : jamais de fenêtre noire")
        else:
            self.assertNotIn("creationflags", self.options, "creationflags est refusé hors de Windows")
        self.assertTrue(r["document"]["resume"]["pdf"])

    def test_pdf_par_chromium_sous_linux(self):
        """Branche Linux simulée : Chromium, sans creationflags."""
        f = self.facture()
        with mock.patch.object(factures.systeme, "WINDOWS", False), \
                mock.patch.object(factures.systeme, "navigateur_chromium", return_value="/usr/bin/chromium"), \
                mock.patch.object(factures.systeme.subprocess, "run", side_effect=self.edge_simule):
            r = factures.emettre(f["id"])
        self.assertIsNone(r["pdf_erreur"])
        self.assertTrue(os.path.isfile(r["pdf"]))
        self.assertEqual(self.commande[0], "/usr/bin/chromium")
        self.assertIn("--headless", self.commande)
        self.assertNotIn("creationflags", self.options, "jamais de creationflags hors de Windows")

    def test_sans_edge_l_emission_reste_valable(self):
        f = self.facture()
        with mock.patch.object(factures.systeme, "WINDOWS", True), \
                mock.patch.object(factures.systeme, "navigateur_chromium", return_value=None):
            r = factures.emettre(f["id"])
        self.assertEqual(r["document"]["numero"], "FAC-2026-001")
        self.assertIn("Edge est introuvable", r["pdf_erreur"])

    def test_sans_chrome_sous_linux(self):
        f = self.facture()
        with mock.patch.object(factures.systeme, "WINDOWS", False), \
                mock.patch.object(factures.systeme, "navigateur_chromium", return_value=None):
            r = factures.emettre(f["id"])
        self.assertEqual(r["document"]["numero"], "FAC-2026-001")
        self.assertEqual(r["pdf_erreur"], "Google Chrome ou Chromium est introuvable : impossible de créer le PDF.")

    def test_pdf_vide(self):
        f = self.facture()
        with mock.patch.object(factures.systeme, "navigateur_chromium", return_value="/usr/bin/chromium"), \
                mock.patch.object(factures.systeme.subprocess, "run", return_value=mock.Mock(returncode=1)):
            r = factures.emettre(f["id"])
        self.assertEqual(r["pdf_erreur"], "Chromium n'a pas pu créer le PDF.")

    def test_dossier_documents_du_systeme(self):
        self.patchs[-1].stop()  # le vrai dossier_documents, remis en place à la fin
        try:
            with mock.patch.object(factures.systeme, "dossier_documents", return_value="/home/moi/Documents"):
                self.assertEqual(factures.dossier_pdf("2026"),
                                 os.path.join("/home/moi/Documents", "Mes outils", "Factures", "2026"))
        finally:
            self.patchs[-1].start()

    def test_ouvrir_par_le_systeme(self):
        with mock.patch.object(factures.systeme, "ouvrir") as ouvrir:
            r = factures.ouvrir_dossier()
        ouvrir.assert_called_once_with(r["chemin"])

    def test_ouvrir_et_mail(self):
        f = self.facture()
        with mock.patch.object(factures.systeme, "navigateur_chromium", return_value="msedge.exe"), \
                mock.patch.object(factures.systeme.subprocess, "run", side_effect=self.edge_simule), \
                mock.patch.object(factures, "_ouvrir") as ouvrir:
            self.emettre(f["id"])
            r = factures.preparer_mail(f["id"])
            self.assertTrue(os.path.isfile(r["pdf"]), "le PDF est créé avant le mail")
            factures.ouvrir_pdf(f["id"])
            factures.ouvrir_dossier(f["id"])
        self.assertEqual(ouvrir.call_count, 2)
        self.assertTrue(r["mailto"].startswith("mailto:client@example.com?subject=Facture%20FAC-2026-001"))
        self.assertIn("09/04/2026", r["texte"])
        self.assertIn("1 080,00", r["texte"])

    def test_export_csv(self):
        f = self.facture(client={"nom": "=Client"})
        self.emettre(f["id"])
        avoir = factures.creer_avoir(f["id"])
        self.emettre(avoir["id"])
        self.facture()  # brouillon
        r = factures.export_csv()
        self.assertTrue(r["csv"].startswith("﻿"))
        lignes = list(csv.reader(io.StringIO(r["csv"][1:]), delimiter=";"))
        self.assertEqual(lignes[0][:3], ["Type", "Numéro", "Date"])
        par_numero = {x[1]: x for x in lignes[1:]}
        self.assertEqual(par_numero["FAC-2026-001"][4], "'=Client", "pas de formule Excel")
        self.assertEqual(par_numero["FAC-2026-001"][7], "1080,00")
        self.assertEqual(par_numero["AV-2026-001"][7], "-1080,00", "avoir en négatif")
        self.assertEqual(len(factures.export_csv([f["id"]])["csv"].strip().splitlines()), 2)

    def test_anglais(self):
        with open(self.cfg.fichier, "w", encoding="utf-8") as fichier:
            fichier.write('{"outils": [], "langue": "en"}')
        f = self.facture()
        self.emettre(f["id"])
        html = factures.apercu(f["id"])["html"]
        self.assertIn("INVOICE", html)
        self.assertIn("€1,080.00", html)


class TestRoutes(ServeurTest):
    def test_routes(self):
        jour = datetime.date(2026, 3, 10)
        documents = tempfile.mkdtemp(prefix="mes-outils-docs-")
        try:
            with ConfigTemporaire(), mock.patch.object(factures, "aujourdhui", lambda: jour), \
                    mock.patch.object(factures, "dossier_documents", lambda: documents), \
                    mock.patch.object(factures.systeme, "navigateur_chromium", return_value=None):
                statut, r = self.post("/api/factures/liste", {})
                self.assertEqual((statut, r["configuree"], r["documents"]), (200, False, []))
                statut, r = self.post("/api/factures/reglages/enregistrer", {"entreprise": {"nom": ""}})
                self.assertEqual(statut, 400)
                statut, r = self.post("/api/factures/reglages/enregistrer", {"entreprise": ENTREPRISE})
                self.assertEqual((statut, r["configuree"]), (200, True))
                doc = {"type": "facture", "client": {"nom": "Client Alpha"}, "lignes": [ligne("Conseil", "1", "100")]}
                statut, r = self.post("/api/factures/calculer", {"document": doc})
                self.assertEqual((statut, r["total_ttc"]), (200, "120.00"))
                statut, r = self.post("/api/factures/enregistrer", {"document": doc})
                self.assertEqual(statut, 200)
                identifiant = r["id"]
                statut, r = self.post("/api/factures/emettre", {"id": identifiant})
                self.assertEqual((statut, r["document"]["numero"]), (200, "FAC-2026-001"))
                self.assertTrue(r["pdf_erreur"])
                statut, r = self.post("/api/factures/paiement/ajouter",
                                      {"id": identifiant, "paiement": {"date": "2026-03-11", "montant": "20", "moyen": "especes"}})
                self.assertEqual((statut, r["resume"]["reste"]), (200, "100.00"))
                statut, r = self.post("/api/factures/resume", {})
                self.assertEqual((statut, r["devises"][0]["impaye"]), (200, "100.00"))
                statut, r = self.post("/api/factures/apercu", {"id": identifiant})
                self.assertIn("FAC-2026-001", r["html"])
                statut, r = self.post("/api/factures/export", {})
                self.assertEqual(statut, 200)
                statut, r = self.post("/api/factures/supprimer", {"id": identifiant})
                self.assertEqual(statut, 400)
                statut, r = self.post("/api/factures/document", {"id": "inconnu"})
                self.assertEqual(statut, 400)
        finally:
            shutil.rmtree(documents, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
