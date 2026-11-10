# -*- coding: utf-8 -*-
"""Tests de l'application Contacts : fiches personne / entreprise, validation,
recherche, historique, relances (Accueil et bulle), import / export CSV,
routes (dont le contrat fixe de /api/contacts/liste)."""
import csv
import datetime
import io
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # aide.py, quel que soit le lancement

from aide import ConfigTemporaire, ServeurTest  # noqa: E402

import contacts  # noqa: E402

JOUR = datetime.date(2026, 3, 10)
HEURE = datetime.datetime(2026, 3, 10, 9, 30)


class BaseContacts(unittest.TestCase):
    def setUp(self):
        self.cfg = ConfigTemporaire({"outils": [], "langue": "fr"})
        self.cfg.__enter__()
        self.patchs = [mock.patch.object(contacts, "aujourdhui", lambda: JOUR),
                       mock.patch.object(contacts, "maintenant", lambda: HEURE)]
        for p in self.patchs:
            p.start()

    def tearDown(self):
        for p in self.patchs:
            p.stop()
        self.cfg.__exit__(None, None, None)

    def personne(self, **valeurs):
        return contacts.enregistrer({"type": "personne", "prenom": "Alice", "nom": "Exemple", **valeurs})


class TestFiches(BaseContacts):
    def test_creer_personne_et_entreprise(self):
        p = self.personne(entreprise="Société Démo", email="alice@exemple.test", telephone="+33 1 23 45 67 89",
                          site="www.exemple.test", etiquettes="vip, Web, #vip, ", statut="client")
        self.assertEqual(p["nom_affiche"], "Alice Exemple")
        self.assertEqual(p["entreprise"], "Société Démo", "entreprise créée à partir de son nom")
        self.assertEqual(p["site"], "https://www.exemple.test", "https:// ajouté")
        self.assertEqual(p["etiquettes"], ["vip", "Web"], "étiquettes sans doublon ni #")
        e = contacts.fiche(p["entreprise_id"])
        self.assertEqual((e["type"], e["nom"], e["statut"]), ("entreprise", "Société Démo", "client"))
        self.assertEqual([m["nom"] for m in e["membres"]], ["Alice Exemple"])
        # Une deuxième personne de la même entreprise (accents et casse ignorés) : pas de doublon.
        b = self.personne(prenom="Bruno", entreprise="societe demo")
        self.assertEqual(b["entreprise_id"], p["entreprise_id"])
        self.assertEqual(len(contacts.tout()["contacts"]), 3)

    def test_modifier(self):
        p = self.personne()
        m = contacts.enregistrer({**p, "poste": "Gérante", "statut": "ancien"})
        self.assertEqual((m["id"], m["poste"], m["statut"]), (p["id"], "Gérante", "ancien"))
        self.assertEqual(m["cree"], "2026-03-10T09:30")
        with self.assertRaisesRegex(ValueError, "introuvable"):
            contacts.enregistrer({**p, "id": "inconnu"})

    def test_refus(self):
        for mauvais, message in (({"nom": "", "prenom": ""}, "Indiquez un nom"),
                                 ({"email": "pas-un-mail"}, "e-mail invalide"),
                                 ({"telephone": "appeler le standard"}, "téléphone invalide"),
                                 ({"site": "ftp://exemple.test"}, "site invalide"),
                                 ({"statut": "vip"}, "Statut inconnu"),
                                 ({"type": "robot"}, "Type de contact inconnu"),
                                 ({"relance": "demain"}, "Date de relance invalide"),
                                 ({"entreprise_id": "inconnu"}, "Entreprise introuvable")):
            with self.subTest(mauvais=mauvais), self.assertRaisesRegex(ValueError, message):
                self.personne(**mauvais)
        self.assertEqual(contacts.tout()["contacts"], [], "rien n'est enregistré après un refus")

    def test_supprimer_entreprise_detache_les_membres(self):
        p = self.personne(entreprise="Démo SARL")
        self.assertEqual(contacts.supprimer(p["entreprise_id"]), 1)
        self.assertEqual(contacts.fiche(p["id"])["entreprise"], "")
        self.assertEqual(contacts.fiche(p["id"])["entreprise_id"], "")
        self.assertEqual(contacts.supprimer("inconnu"), 0)

    def test_recherche_publique(self):
        self.personne(entreprise="Démo SARL", email="alice@exemple.test", telephone="06 12 34 56 78", statut="client")
        contacts.enregistrer({"type": "personne", "prenom": "Élodie", "nom": "Test", "etiquettes": ["presse"]})
        noms = lambda r: [c["nom"] for c in contacts.lister(r)]  # noqa: E731
        self.assertEqual(noms(""), ["Alice Exemple", "Démo SARL", "Élodie Test"], "triés sans tenir compte des accents")
        self.assertEqual(noms("elodie"), ["Élodie Test"])
        self.assertEqual(noms("demo"), ["Alice Exemple", "Démo SARL"], "recherche aussi dans l'entreprise")
        self.assertEqual(noms("0612"), ["Alice Exemple"], "numéro sans espaces")
        self.assertEqual(noms("exemple.test"), ["Alice Exemple"])
        self.assertEqual(noms("alice inconnu"), [])
        alice = contacts.lister("alice")[0]
        self.assertEqual(set(alice), {"id", "nom", "entreprise", "email", "telephone", "statut"}, "contrat fixe")
        self.assertEqual((alice["entreprise"], alice["statut"]), ("Démo SARL", "client"))


class TestHistorique(BaseContacts):
    def test_notes(self):
        p = self.personne()
        f = contacts.ajouter_note(p["id"], {"type": "appel", "texte": "Devis demandé"})
        self.assertEqual((f["notes"][0]["type"], f["notes"][0]["date"]), ("appel", "2026-03-10T09:30"))
        f = contacts.ajouter_note(p["id"], {"type": "rdv", "texte": "Réunion", "date": "2026-03-12T14:00:00"})
        self.assertEqual([n["texte"] for n in f["notes"]], ["Réunion", "Devis demandé"], "plus récentes en tête")
        for mauvaise in ({"type": "fax", "texte": "x"}, {"type": "note", "texte": "  "},
                         {"type": "note", "texte": "x", "date": "hier"}):
            with self.assertRaises(ValueError):
                contacts.ajouter_note(p["id"], mauvaise)
        f = contacts.supprimer_note(p["id"], f["notes"][0]["id"])
        self.assertEqual(len(f["notes"]), 1)
        with self.assertRaisesRegex(ValueError, "Note introuvable"):
            contacts.supprimer_note(p["id"], "inconnue")


class TestRelances(BaseContacts):
    def test_a_relancer_et_alertes(self):
        a = self.personne(relance="2026-03-08", relance_motif="Envoyer le devis")
        b = self.personne(prenom="Bruno", relance="10/03/2026")
        self.personne(prenom="Chloé", relance="2026-03-11")
        self.personne(prenom="David")
        dues = contacts.a_relancer()
        self.assertEqual([(x["nom"], x["retard"]) for x in dues], [("Alice Exemple", 2), ("Bruno Exemple", 0)],
                         "aujourd'hui et en retard, les plus anciennes d'abord ; pas demain")
        self.assertEqual(len(contacts.a_relancer(1)), 1)
        self.assertEqual(contacts.tout()["compteurs"]["relancer"], 2)
        alertes = contacts.alertes_dues()
        self.assertEqual([x["titre"] for x in alertes], ["Relancer Alice Exemple", "Relancer Bruno Exemple"])
        self.assertEqual(alertes[0]["detail"], "Envoyer le devis")
        self.assertEqual(alertes[1]["detail"], "Relance prévue le 10/03/2026.")
        self.assertTrue(contacts.marquer_alerte(alertes[0]["id"]))
        self.assertEqual([x["titre"] for x in contacts.alertes_dues()], ["Relancer Bruno Exemple"], "vue : plus montrée")
        self.assertEqual(len(contacts.a_relancer()), 2, "l'Accueil la montre tant qu'elle n'est pas faite")
        self.assertFalse(contacts.marquer_alerte("inconnu:2026-03-08"))
        # Reportée : nouvelle alerte le jour venu.
        contacts.relancer(a["id"], "2026-03-09")
        self.assertIn("Relancer Alice Exemple", [x["titre"] for x in contacts.alertes_dues()])
        # Faite : plus de date, plus de motif.
        f = contacts.relancer(a["id"], "")
        self.assertEqual((f["relance"], f["relance_motif"]), ("", ""))
        contacts.relancer(b["id"], "")
        self.assertEqual(contacts.alertes_dues(), [])

    def test_alerte_en_anglais(self):
        self.cfg.__exit__(None, None, None)
        self.cfg = ConfigTemporaire({"outils": [], "langue": "en"})
        self.cfg.__enter__()
        self.personne(relance="2026-03-10")
        self.assertEqual(contacts.alertes_dues()[0]["titre"], "Follow up with Alice Exemple")
        self.assertEqual(contacts.alertes_dues()[0]["detail"], "Follow-up planned for 2026-03-10.")


class TestCsv(BaseContacts):
    def test_export(self):
        p = self.personne(entreprise="Démo; SARL", email="alice@exemple.test", etiquettes=["vip", "web"],
                          poste="=1+1", statut="ancien")
        contacts.ajouter_note(p["id"], {"texte": "Premier appel", "date": "2026-03-01T10:00"})
        r = contacts.export_csv()
        self.assertEqual(r["nom"], "contacts-2026-03-10.csv")
        self.assertTrue(r["csv"].startswith("﻿"), "BOM UTF-8 pour Excel")
        self.assertIn("\r\n", r["csv"])
        lignes = list(csv.reader(io.StringIO(r["csv"][1:]), delimiter=";"))
        self.assertEqual(lignes[0][:4], ["Type", "Prénom", "Nom", "Entreprise"])
        self.assertEqual(lignes[1][:3], ["Entreprise", "", "Démo; SARL"], "les entreprises d'abord")
        alice = dict(zip(lignes[0], lignes[2]))
        self.assertEqual((alice["Entreprise"], alice["Poste"], alice["Statut"], alice["Étiquettes"], alice["Dernier échange"]),
                         ("Démo; SARL", "'=1+1", "Ancien client", "vip, web", "2026-03-01"))

    def test_aller_retour(self):
        p = self.personne(entreprise="Démo SARL", email="alice@exemple.test", poste="=1+1", relance="2026-04-01",
                          etiquettes=["vip"])
        texte = contacts.export_csv()["csv"]
        contacts.supprimer(p["id"])
        contacts.supprimer(p["entreprise_id"])
        bilan = contacts.importer_csv(texte)
        self.assertEqual((bilan["ajoutes"], bilan["ignores"], bilan["erreurs"]), (2, 0, []))
        alice = next(c for c in contacts.tout()["contacts"] if c["type"] == "personne")
        self.assertEqual((alice["entreprise"], alice["poste"], alice["relance"], alice["etiquettes"]),
                         ("Démo SARL", "=1+1", "2026-04-01", ["vip"]), "apostrophe anti-formule retirée")
        # Réimporté : rien de nouveau.
        self.assertEqual(contacts.importer_csv(texte)["ajoutes"], 0)
        self.assertEqual(len(contacts.tout()["contacts"]), 2)

    def test_import_autre_format(self):
        self.personne(email="alice@exemple.test")
        texte = ("First Name,Last Name,E-mail Address,Company,Phone,Status,Tags,Notes\n"
                 "Alice,Exemple,ALICE@exemple.test,,01 02 03 04 05,customer,presse,Rencontrée au salon\n"
                 "Bruno,Test,bruno@exemple.test,Démo SARL,,lead,,\n"
                 ",,,Seule Entreprise,,,,\n"
                 "Chloé,Erreur,pas-un-mail,,,,,\n"
                 "\n")
        bilan = contacts.importer_csv(texte)
        self.assertEqual((bilan["ajoutes"], bilan["completes"], bilan["ignores"]), (3, 1, 1))
        self.assertEqual(bilan["erreurs"], ["Ligne 5 : Adresse e-mail invalide."])
        tous = {c["nom_affiche"]: c for c in contacts.tout()["contacts"]}
        self.assertEqual(sorted(tous), ["Alice Exemple", "Bruno Test", "Démo SARL", "Seule Entreprise"])
        alice = tous["Alice Exemple"]
        self.assertEqual((alice["telephone"], alice["etiquettes"], alice["notes"][0]["texte"], alice["statut"]),
                         ("01 02 03 04 05", ["presse"], "Rencontrée au salon", "prospect"),
                         "fiche existante complétée, son statut n'est pas changé")
        self.assertEqual((tous["Bruno Test"]["entreprise"], tous["Bruno Test"]["statut"]), ("Démo SARL", "prospect"))
        self.assertEqual(tous["Seule Entreprise"]["type"], "entreprise")

    def test_import_refuse(self):
        with self.assertRaisesRegex(ValueError, "vide"):
            contacts.importer_csv("﻿  ")
        with self.assertRaisesRegex(ValueError, "Colonnes introuvables"):
            contacts.importer_csv("a;b\n1;2\n")


class TestRoutes(ServeurTest):
    def test_routes(self):
        with ConfigTemporaire({"outils": [], "langue": "fr"}), \
                mock.patch.object(contacts, "aujourdhui", lambda: JOUR), \
                mock.patch.object(contacts, "maintenant", lambda: HEURE):
            statut, r = self.post("/api/contacts/liste", {})
            self.assertEqual((statut, r), (200, {"contacts": []}))
            statut, r = self.post("/api/contacts/enregistrer", {"contact": {
                "prenom": "Alice", "nom": "Exemple", "entreprise": "Démo SARL", "email": "alice@exemple.test",
                "statut": "client", "relance": "2026-03-10"}})
            self.assertEqual(statut, 200)
            ident = r["id"]
            statut, r = self.post("/api/contacts/enregistrer", {"contact": {"nom": "X", "email": "faux"}})
            self.assertEqual((statut, r.get("erreur")), (400, "Adresse e-mail invalide."))
            statut, r = self.post("/api/contacts/liste", {"recherche": "alice"})
            self.assertEqual(r, {"contacts": [{"id": ident, "nom": "Alice Exemple", "entreprise": "Démo SARL",
                                               "email": "alice@exemple.test", "telephone": "", "statut": "client"}]})
            statut, r = self.post("/api/contacts/fiche", {"id": ident})
            self.assertEqual((statut, r["prenom"]), (200, "Alice"))
            statut, r = self.post("/api/contacts/fiche", {"id": "inconnu"})
            self.assertEqual(statut, 400)
            statut, r = self.post("/api/contacts/note/ajouter", {"id": ident, "note": {"type": "mail", "texte": "Devis envoyé"}})
            self.assertEqual((statut, len(r["notes"])), (200, 1))
            statut, r = self.post("/api/contacts/note/supprimer", {"id": ident, "note_id": r["notes"][0]["id"]})
            self.assertEqual((statut, r["notes"]), (200, []))
            statut, r = self.post("/api/contacts/a_relancer", {"limite": 5})
            self.assertEqual([x["nom"] for x in r["relances"]], ["Alice Exemple"])
            statut, r = self.post("/api/contacts/alertes", {})
            self.assertEqual(len(r["alertes"]), 1)
            statut, r = self.post("/api/contacts/marquer_alerte", {"id": r["alertes"][0]["id"]})
            self.assertEqual(r, {"ok": True})
            statut, r = self.post("/api/contacts/relance", {"id": ident, "date": ""})
            self.assertEqual((statut, r["relance"]), (200, ""))
            statut, r = self.post("/api/contacts/tout", {})
            self.assertEqual((statut, len(r["contacts"]), r["compteurs"]["client"]), (200, 2, 2))
            statut, r = self.post("/api/contacts/export", {})
            self.assertEqual((statut, r["nom"]), (200, "contacts-2026-03-10.csv"))
            statut, r = self.post("/api/contacts/import", {"csv": "Nom;E-mail\nBruno;bruno@exemple.test\n"})
            self.assertEqual((statut, r["ajoutes"]), (200, 1))
            statut, r = self.post("/api/contacts/supprimer", {"id": ident})
            self.assertEqual((statut, r), (200, {"supprimes": 1}))


if __name__ == "__main__":
    unittest.main()
