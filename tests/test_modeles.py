# -*- coding: utf-8 -*-
"""Tests de l'application Modèles de messages : exemples au premier usage,
variables, ajout, modification, duplication, recherche, tri, export / import,
lien mailto et routes."""
import os
import sys
import unittest
from unittest import mock
from urllib.parse import unquote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # aide.py, quel que soit le lancement

from aide import ConfigTemporaire, ServeurTest  # noqa: E402

import config  # noqa: E402
import modeles  # noqa: E402


def _vider():
    """Part d'une liste vide (sans les exemples)."""
    config.ecrire_donnees("modeles", {"modeles": [], "exemples": True})


class TestVariables(unittest.TestCase):
    def test_detection(self):
        texte = "Bonjour {prenom}, facture {numero_facture} de {montant}. {Prénom} {date-rdv} {1abc} { x } {prenom}"
        self.assertEqual(modeles.variables("Objet {sujet}", texte),
                         ["sujet", "prenom", "numero_facture", "montant", "date-rdv"],
                         "ordre d'apparition, sans doublon, {Prénom} = {prenom}, {1abc} et { x } ignorés")

    def test_remplir(self):
        texte = "Bonjour {Prénom}, {montant} pour {entreprise}."
        self.assertEqual(modeles.remplir(texte, {"prenom": "Alex", "montant": "120 €", "entreprise": ""}),
                         "Bonjour Alex, 120 € pour {entreprise}.", "une variable vide reste visible")
        self.assertEqual(modeles.remplir("{a}", {"a": "{b}", "b": "x"}), "{b}", "pas de remplacement en cascade")


class TestModeles(unittest.TestCase):
    def test_exemples_au_premier_usage_seulement(self):
        with ConfigTemporaire():
            self.assertEqual(modeles.favoris(), [], "la palette ne crée pas les exemples")
            liste = modeles.lister()
            self.assertGreaterEqual(len(liste), 10, "une dizaine d'exemples")
            self.assertTrue(all(m["texte"] and m["titre"] for m in liste))
            self.assertTrue(liste[0]["favori"], "tri par défaut : favoris en tête")
            for m in liste:
                modeles.supprimer(m["id"])
            self.assertEqual(modeles.lister(), [], "les exemples supprimés ne reviennent pas tout seuls")
            self.assertEqual(modeles.ajouter_exemples(), len(modeles.EXEMPLES))
            self.assertEqual(modeles.ajouter_exemples(), 0, "pas de doublon")

    def test_creer_modifier_dupliquer_supprimer(self):
        with ConfigTemporaire():
            _vider()
            a = modeles.enregistrer({"titre": "  Relance   ", "categorie": "Relances", "objet": "Facture {numero}",
                                     "texte": "Bonjour {prenom},\r\nmerci.", "langue": "EN", "favori": 1})
            self.assertEqual((a["titre"], a["langue"], a["favori"], a["utilisations"]), ("Relance", "en", True, 0))
            self.assertEqual(a["texte"], "Bonjour {prenom},\nmerci.", "fins de ligne Windows normalisées")
            self.assertEqual(a["variables"], ["numero", "prenom"])
            b = modeles.enregistrer({**a, "titre": "Relance aimable", "langue": "klingon"})
            self.assertEqual((b["id"], b["titre"], b["langue"]), (a["id"], "Relance aimable", "autre"))
            c = modeles.dupliquer(a["id"])
            self.assertNotEqual(c["id"], a["id"])
            self.assertEqual((c["titre"], c["favori"], c["texte"]), ("Relance aimable (copie)", False, a["texte"]))
            self.assertEqual(len(modeles.lister()), 2, "pas de doublon après modification")
            self.assertEqual(modeles.supprimer(a["id"]), 1)
            self.assertEqual(modeles.supprimer(a["id"]), 0)
            with self.assertRaises(ValueError):
                modeles.dupliquer("inconnu")

    def test_valeurs_refusees(self):
        with ConfigTemporaire():
            _vider()
            for mauvais in ({"titre": "", "texte": "x"}, {"titre": "x", "texte": "  \n "},
                            {"titre": "x" * 200, "texte": "x"}, {"titre": "x", "texte": "y", "objet": "o" * 300},
                            {"titre": "x", "texte": "y", "categorie": "c" * 50},
                            {"id": "inconnu", "titre": "x", "texte": "y"}, "pas un dict"):
                with self.assertRaises(ValueError, msg=str(mauvais)[:60]):
                    modeles.enregistrer(mauvais)
            self.assertEqual(modeles.lister(), [], "rien n'est enregistré après un refus")

    def test_recherche_filtre_et_tris(self):
        with ConfigTemporaire():
            _vider()
            a = modeles.enregistrer({"titre": "Zèbre", "categorie": "Relances", "texte": "Échéance dépassée"})
            b = modeles.enregistrer({"titre": "Abeille", "categorie": "relances", "texte": "Rendez-vous confirmé"})
            c = modeles.enregistrer({"titre": "Merle", "categorie": "Refus", "objet": "Votre devis", "texte": "Non merci"})
            ids = lambda **f: [m["id"] for m in modeles.lister(**f)]  # noqa: E731
            self.assertEqual(set(ids(recherche="ECHEANCE")), {a["id"]}, "casse et accents ignorés")
            self.assertEqual(ids(recherche="devis merci"), [c["id"]], "objet cherché, tous les mots")
            self.assertEqual(set(ids(categorie="RELANCES")), {a["id"], b["id"]}, "catégorie sans casse")
            self.assertEqual(modeles.categories(), ["Refus", "Relances"], "catégories sans doublon, A → Z")
            self.assertEqual(ids(tri="titre"), [b["id"], c["id"], a["id"]])
            for _ in range(2):
                modeles.utiliser(c["id"])
            modeles.utiliser(a["id"])
            self.assertEqual(ids(tri="usage"), [c["id"], a["id"], b["id"]], "les plus utilisés en tête")
            modeles.marquer_favori(b["id"], True)
            self.assertEqual(ids(tri="favoris")[0], b["id"], "les favoris d'abord")
            self.assertEqual([m["id"] for m in modeles.favoris()], [b["id"]])
            self.assertEqual(modeles.lister(tri="usage")[0]["utilisations"], 2)

    def test_export_import(self):
        with ConfigTemporaire():
            _vider()
            modeles.enregistrer({"titre": "Un", "texte": "Texte un", "categorie": "A", "favori": True})
            modeles.utiliser(modeles.lister()[0]["id"])
            export = modeles.exporter()
            self.assertEqual(export["format"], modeles.FORMAT_EXPORT)
            self.assertNotIn("id", export["modeles"][0], "pas d'identifiant interne dans l'export")
            r = modeles.importer(export)
            self.assertEqual(r, {"ajoutes": 0, "doublons": 1, "invalides": 0}, "doublon ignoré")
            r = modeles.importer([{"titre": "Deux", "texte": "Texte deux", "utilisations": 4},
                                  {"titre": "", "texte": "sans titre"}, "n'importe quoi",
                                  {"titre": "Deux", "texte": "Texte  deux"}])
            self.assertEqual(r, {"ajoutes": 1, "doublons": 1, "invalides": 2})
            deux = next(m for m in modeles.lister() if m["titre"] == "Deux")
            self.assertEqual(deux["utilisations"], 4, "compteur repris")
            for mauvais in ({"format": "autre", "modeles": []}, {"rien": 1}, "texte", None):
                with self.assertRaises(ValueError, msg=str(mauvais)):
                    modeles.importer(mauvais)

    def test_import_premier_usage_garde_exemples(self):
        with ConfigTemporaire():
            r = modeles.importer([{"titre": "Perso", "texte": "Bonjour"}])
            self.assertEqual(r["ajoutes"], 1)
            self.assertEqual(len(modeles.lister()), len(modeles.EXEMPLES) + 1)


class TestMail(unittest.TestCase):
    def test_lien(self):
        lien, retire = modeles.lien_mail("alex@exemple.com; b@exemple.org", "Facture n°12 & suite",
                                         "Bonjour,\nligne 2 ?=&")
        self.assertFalse(retire)
        self.assertTrue(lien.startswith("mailto:alex@exemple.com,b@exemple.org?subject="))
        self.assertIn("%0D%0A", lien, "retours à la ligne en CRLF encodés")
        self.assertNotIn(" ", lien)
        corps = lien.split("body=")[1]
        self.assertEqual(unquote(corps), "Bonjour,\r\nligne 2 ?=&")
        self.assertEqual(modeles.lien_mail("", "", ""), ("mailto:", False))

    def test_texte_trop_long(self):
        lien, retire = modeles.lien_mail("a@exemple.com", "Objet", "x" * 5000)
        self.assertTrue(retire)
        self.assertNotIn("body=", lien)
        self.assertIn("subject=Objet", lien)

    def test_adresse_invalide(self):
        for mauvaise in ("pas-une-adresse", "a@b", "x@y.z?cc=autre@ex.com", "a b@c.d"):
            with self.assertRaises(ValueError, msg=mauvaise):
                modeles.lien_mail(mauvaise, "o", "t")

    def test_ouverture(self):
        with mock.patch.object(modeles.systeme, "ouvrir") as ouvrir:
            r = modeles.ecrire_mail("a@exemple.com", "Objet", "Texte")
        ouvrir.assert_called_once_with(r["lien"])
        with mock.patch.object(modeles.systeme, "ouvrir", side_effect=OSError("aucune")):
            with self.assertRaises(ValueError):
                modeles.ecrire_mail("a@exemple.com", "Objet", "Texte")

    @unittest.skipUnless(sys.platform == "win32", "os.startfile n'existe que sous Windows")
    def test_ouverture_sous_windows(self):
        with mock.patch.object(modeles.systeme.os, "startfile") as ouvrir:
            r = modeles.ecrire_mail("a@exemple.com", "Objet", "Texte")
        ouvrir.assert_called_once_with(r["lien"])
        with mock.patch.object(modeles.systeme.os, "startfile", side_effect=OSError("aucune")):
            with self.assertRaisesRegex(ValueError, "Aucune messagerie"):
                modeles.ecrire_mail("a@exemple.com", "Objet", "Texte")

    def test_ouverture_sous_linux(self):
        """Branche Linux simulée : xdg-open, sinon le navigateur, sinon un message clair."""
        with mock.patch.object(modeles.systeme, "WINDOWS", False), \
                mock.patch.object(modeles.systeme.shutil, "which", return_value="/usr/bin/xdg-open"), \
                mock.patch.object(modeles.systeme, "lancer_detache") as lancer:
            r = modeles.ecrire_mail("a@exemple.com", "Objet", "Texte")
        lancer.assert_called_once_with(["xdg-open", r["lien"]])
        with mock.patch.object(modeles.systeme, "WINDOWS", False), \
                mock.patch.object(modeles.systeme.shutil, "which", return_value=None), \
                mock.patch.object(modeles.systeme.webbrowser, "open") as navigateur:
            r = modeles.ecrire_mail("a@exemple.com", "Objet", "Texte")
        navigateur.assert_called_once_with(r["lien"])
        with mock.patch.object(modeles.systeme, "WINDOWS", False), \
                mock.patch.object(modeles.systeme.shutil, "which", return_value="/usr/bin/xdg-open"), \
                mock.patch.object(modeles.systeme, "lancer_detache", side_effect=FileNotFoundError("xdg-open")):
            with self.assertRaisesRegex(ValueError, "Aucune messagerie"):
                modeles.ecrire_mail("a@exemple.com", "Objet", "Texte")


class TestRoutes(ServeurTest):
    def test_routes(self):
        with ConfigTemporaire():
            statut, r = self.post("/api/modeles/favoris", {})
            self.assertEqual((statut, r["modeles"]), (200, []))
            statut, r = self.post("/api/modeles/liste", {})
            self.assertEqual(statut, 200)
            self.assertEqual(r["total"], len(modeles.EXEMPLES))
            self.assertIn("Relances", r["categories"])
            statut, m = self.post("/api/modeles/enregistrer",
                                  {"modele": {"titre": "Merci", "categorie": "Suivi", "texte": "Merci {prenom}"}})
            self.assertEqual((statut, m["variables"]), (200, ["prenom"]))
            statut, r = self.post("/api/modeles/enregistrer", {"modele": {"titre": "", "texte": "x"}})
            self.assertEqual((statut, r["erreur"]), (400, "Donnez un titre au modèle."))
            statut, r = self.post("/api/modeles/utiliser", {"id": m["id"]})
            self.assertEqual((statut, r["utilisations"]), (200, 1))
            statut, r = self.post("/api/modeles/favori", {"id": m["id"], "favori": True})
            self.assertEqual((statut, r["favori"]), (200, True))
            statut, r = self.post("/api/modeles/liste", {"recherche": "merci prenom", "categorie": "suivi"})
            self.assertEqual([x["id"] for x in r["modeles"]], [m["id"]])
            statut, copie = self.post("/api/modeles/dupliquer", {"id": m["id"]})
            self.assertEqual((statut, copie["titre"]), (200, "Merci (copie)"))
            statut, export = self.post("/api/modeles/exporter", {})
            self.assertEqual(len(export["modeles"]), len(modeles.EXEMPLES) + 2)
            statut, r = self.post("/api/modeles/importer", {"contenu": export})
            self.assertEqual((statut, r["ajoutes"], r["doublons"]), (200, 0, len(modeles.EXEMPLES) + 2))
            statut, r = self.post("/api/modeles/importer", {"contenu": {"format": "autre"}})
            self.assertEqual(statut, 400)
            with mock.patch.object(modeles.systeme, "ouvrir") as ouvrir:
                statut, r = self.post("/api/modeles/mail", {"a": "a@exemple.com", "objet": "O", "texte": "T"})
            self.assertEqual((statut, r["texte_retire"]), (200, False))
            ouvrir.assert_called_once()
            statut, r = self.post("/api/modeles/mail", {"a": "invalide", "texte": "T"})
            self.assertEqual((statut, r["erreur"]), (400, "Adresse e-mail invalide : invalide"))
            statut, r = self.post("/api/modeles/supprimer", {"id": m["id"]})
            self.assertEqual((statut, r["supprimes"]), (200, 1))
            statut, r = self.post("/api/modeles/exemples", {})
            self.assertEqual((statut, r["ajoutes"]), (200, 0))


if __name__ == "__main__":
    unittest.main()
