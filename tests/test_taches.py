# -*- coding: utf-8 -*-
"""Tests de l'application Tâches : création, validation, groupes de la liste,
récurrence, liste de contrôle, tableau, rappels de la bulle et routes."""
import datetime
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # aide.py, quel que soit le lancement

from aide import ConfigTemporaire, ServeurTest  # noqa: E402

import taches  # noqa: E402


class Horloge:
    """Horloge simulée : mercredi 4 mars 2026, 10:00."""

    def __init__(self, depart="2026-03-04T10:00"):
        self.t = datetime.datetime.strptime(depart, taches.FORMAT_MINUTE)

    def __call__(self):
        return self.t

    def avancer(self, **duree):
        self.t += datetime.timedelta(**duree)


class BaseTaches(unittest.TestCase):
    def setUp(self):
        self.cfg = ConfigTemporaire({"outils": [], "langue": "fr"})
        self.cfg.__enter__()
        self.horloge = Horloge()
        self.patch = mock.patch.object(taches, "maintenant", self.horloge)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.cfg.__exit__(None, None, None)


class TestCreation(BaseTaches):
    def test_creer_minimal(self):
        t = taches.creer_tache("  Envoyer   le devis ")
        self.assertEqual(t["titre"], "Envoyer le devis", "espaces nettoyés")
        self.assertEqual((t["statut"], t["priorite"], t["echeance"], t["heure"], t["groupe"]),
                         ("a_faire", "normale", "", "", "sans_echeance"))
        self.assertEqual(len(taches.toutes()), 1)

    def test_creer_complet(self):
        t = taches.creer_tache("Relancer le client", "2026-03-05T14:30", "Facture de février",
                               origine="reunions", priorite="haute", etiquettes="compta, #Relance, compta",
                               liste=["Préparer le mail", "", {"texte": "Envoyer"}], client="Société Exemple")
        self.assertEqual((t["echeance"], t["heure"]), ("2026-03-05", "14:30"), "heure tirée de l'échéance")
        self.assertEqual(t["etiquettes"], ["compta", "Relance"], "doublons et # retirés")
        self.assertEqual([e["texte"] for e in t["liste"]], ["Préparer le mail", "Envoyer"])
        self.assertFalse(any(e["fait"] for e in t["liste"]))
        self.assertEqual((t["origine"], t["client"], t["groupe"]), ("reunions", "Société Exemple", "semaine"))

    def test_validation(self):
        with self.assertRaisesRegex(ValueError, "titre"):
            taches.creer_tache("   ")
        with self.assertRaisesRegex(ValueError, "Échéance invalide"):
            taches.creer_tache("A", "2026-02-30")
        with self.assertRaisesRegex(ValueError, "Heure invalide"):
            taches.creer_tache("A", "2026-03-05", heure="25:00")
        with self.assertRaisesRegex(ValueError, "date pour l'heure"):
            taches.creer_tache("A", "", heure="10:00")
        with self.assertRaisesRegex(ValueError, "Priorité"):
            taches.creer_tache("A", priorite="urgente")
        with self.assertRaisesRegex(ValueError, "Répétition"):
            taches.creer_tache("A", recurrence="annee")
        with self.assertRaisesRegex(ValueError, "étiquettes au plus"):
            taches.creer_tache("A", etiquettes=[f"e{i}" for i in range(11)])

    def test_contact_par_application_contacts(self):
        faux = mock.Mock(ROUTES={"liste": lambda d: {"contacts": [{"id": "c1", "nom": "Contact Fictif", "entreprise": "Ent"}]}})
        with mock.patch.dict(sys.modules, {"contacts": faux}):
            t = taches.creer_tache("Appeler", contact_id="c1")
        self.assertEqual((t["contact_id"], t["client"]), ("c1", "Contact Fictif"))

    def test_contact_sans_application_contacts(self):
        with mock.patch.dict(sys.modules, {"contacts": None}):
            t = taches.creer_tache("Appeler", contact_id="c9")
        self.assertEqual((t["contact_id"], t["client"]), ("c9", ""), "Contacts absente : pas d'erreur")


class TestGroupes(BaseTaches):
    def test_groupes(self):
        # Mercredi 4 mars 2026, 10:00 : la semaine finit le dimanche 8.
        cas = {"2026-03-02": "retard", "2026-03-04T09:00": "retard", "2026-03-04T18:00": "aujourdhui",
               "2026-03-04": "aujourdhui", "2026-03-08": "semaine", "2026-03-09": "plus_tard", "": "sans_echeance"}
        for echeance, attendu in cas.items():
            self.assertEqual(taches.creer_tache("T " + echeance, echeance)["groupe"], attendu, echeance)

    def test_tri_et_du_jour(self):
        taches.creer_tache("Basse", "2026-03-04", priorite="basse")
        taches.creer_tache("Haute", "2026-03-04", priorite="haute")
        taches.creer_tache("Vieille", "2026-03-01")
        taches.creer_tache("Demain", "2026-03-05")
        faite = taches.creer_tache("Faite", "2026-03-04")
        taches.cocher(faite["id"], True)
        j = taches.taches_du_jour(5)
        self.assertEqual([t["titre"] for t in j["taches"]], ["Vieille", "Haute", "Basse"],
                         "retard d'abord, puis priorité haute ; ni demain ni les faites")
        self.assertEqual((j["retard"], j["aujourdhui"], j["total"]), (1, 2, 3))
        self.assertEqual(len(taches.taches_du_jour(2)["taches"]), 2)


class TestRecurrence(BaseTaches):
    def test_prochaine_date(self):
        auj = datetime.date(2026, 3, 4)
        self.assertEqual(taches.prochaine_date("2026-03-04", "jour", auj), "2026-03-05")
        self.assertEqual(taches.prochaine_date("2026-02-25", "jour", auj), "2026-03-05", "faite en retard : demain")
        self.assertEqual(taches.prochaine_date("2026-03-02", "semaine", auj), "2026-03-09")
        self.assertEqual(taches.prochaine_date("2026-03-10", "semaine", auj), "2026-03-17", "faite en avance")
        self.assertEqual(taches.prochaine_date("2026-01-31", "mois", datetime.date(2026, 2, 1)), "2026-02-28")
        self.assertEqual(taches.prochaine_date("2026-02-28", "mois", datetime.date(2026, 3, 1), 31), "2026-03-31",
                         "le jour du mois d'origine est gardé")

    def test_tache_faite_renait(self):
        t = taches.creer_tache("Sauvegarde", "2026-03-04T17:00", recurrence="semaine",
                               liste=["Disque", "Cloud"], etiquettes=["admin"])
        etape = t["liste"][0]["id"]
        taches.cocher_etape(t["id"], etape, True)
        r = taches.cocher(t["id"], True)
        self.assertEqual((r["tache"]["statut"], r["tache"]["fait_le"]), ("fait", "2026-03-04T10:00"))
        s = r["suivante"]
        self.assertIsNotNone(s, "une tâche répétée renaît")
        self.assertEqual((s["echeance"], s["heure"], s["statut"], s["etiquettes"]), ("2026-03-11", "17:00", "a_faire", ["admin"]))
        self.assertFalse(any(e["fait"] for e in s["liste"]), "étapes décochées")
        self.assertEqual(len(taches.toutes()), 2)
        # Cocher deux fois ne crée pas deux copies.
        self.assertIsNone(taches.cocher(t["id"], True)["suivante"])
        self.assertEqual(len(taches.toutes()), 2)

    def test_rouvrir_retire_la_copie(self):
        t = taches.creer_tache("Point hebdo", "2026-03-04", recurrence="semaine")
        taches.cocher(t["id"], True)
        taches.cocher(t["id"], False)
        liste = taches.toutes()
        self.assertEqual(len(liste), 1, "la copie non commencée disparaît")
        self.assertEqual(liste[0]["statut"], "a_faire")

    def test_repetee_sans_date(self):
        t = taches.creer_tache("Boîte mail", recurrence="jour")
        self.assertEqual(t["echeance"], "2026-03-04", "date du jour par défaut")
        s = taches.deplacer(t["id"], "fait")["suivante"]
        self.assertEqual(s["echeance"], "2026-03-05")

    def test_non_repetee(self):
        t = taches.creer_tache("Une fois", "2026-03-04")
        self.assertIsNone(taches.cocher(t["id"])["suivante"])
        self.assertEqual(len(taches.toutes()), 1)


class TestModification(BaseTaches):
    def test_modifier(self):
        t = taches.creer_tache("A", "2026-03-06", etiquettes=["x"], client="Client A")
        r = taches.modifier_tache({"id": t["id"], "titre": "B", "priorite": "haute"})
        self.assertEqual((r["tache"]["titre"], r["tache"]["priorite"]), ("B", "haute"))
        self.assertEqual((r["tache"]["echeance"], r["tache"]["etiquettes"], r["tache"]["client"]),
                         ("2026-03-06", ["x"], "Client A"), "champs absents gardés")
        r = taches.modifier_tache({"id": t["id"], "echeance": "", "heure": "", "client": ""})
        self.assertEqual((r["tache"]["echeance"], r["tache"]["client"], r["tache"]["groupe"]), ("", "", "sans_echeance"))
        with self.assertRaisesRegex(ValueError, "introuvable"):
            taches.modifier_tache({"id": "nope", "titre": "C"})

    def test_etapes(self):
        t = taches.creer_tache("A", liste=["un", "deux"])
        r = taches.cocher_etape(t["id"], t["liste"][1]["id"], True)
        self.assertEqual([e["fait"] for e in r["liste"]], [False, True])
        with self.assertRaisesRegex(ValueError, "Étape introuvable"):
            taches.cocher_etape(t["id"], "zz", True)

    def test_deplacer_et_ordre(self):
        a, b, c = (taches.creer_tache(x) for x in "ABC")
        taches.deplacer(a["id"], "en_cours")
        taches.deplacer(b["id"], "en_cours", [b["id"], a["id"]])
        par_id = {t["id"]: t for t in taches.toutes()}
        self.assertEqual((par_id[a["id"]]["statut"], par_id[b["id"]]["statut"], par_id[c["id"]]["statut"]),
                         ("en_cours", "en_cours", "a_faire"))
        self.assertLess(par_id[b["id"]]["ordre"], par_id[a["id"]]["ordre"], "ordre de la colonne respecté")
        with self.assertRaisesRegex(ValueError, "Statut"):
            taches.deplacer(a["id"], "perdu")

    def test_supprimer(self):
        t = taches.creer_tache("A")
        self.assertEqual(taches.supprimer_tache(t["id"]), 1)
        self.assertEqual(taches.supprimer_tache(t["id"]), 0)
        self.assertEqual(taches.toutes(), [])


class TestRappels(BaseTaches):
    def test_alerte_avant_echeance(self):
        t = taches.creer_tache("Appel", "2026-03-04T10:30", client="Client B")
        taches.creer_tache("Sans heure", "2026-03-04")
        self.assertEqual(taches.alertes_dues(), [], "trop tôt")
        self.horloge.avancer(minutes=16)                       # 10:16
        a = taches.alertes_dues()
        self.assertEqual(a, [{"id": t["id"], "titre": "Appel", "detail": "Échéance à 10:30 · Client B"}])
        self.assertTrue(taches.marquer_alerte(t["id"]))
        self.assertEqual(taches.alertes_dues(), [], "rappel vu")
        # Nouvelle échéance : nouveau rappel.
        taches.modifier_tache({"id": t["id"], "echeance": "2026-03-04", "heure": "10:20"})
        self.assertEqual(len(taches.alertes_dues()), 1)
        self.assertFalse(taches.marquer_alerte("inconnue"))

    def test_alerte_depassee_et_perimee(self):
        taches.creer_tache("Passée", "2026-03-04T09:00")
        self.assertEqual(taches.alertes_dues()[0]["detail"], "Échéance dépassée (09:00)")
        self.horloge.avancer(hours=6)                          # 16:00 : plus de 6 h après
        self.assertEqual(taches.alertes_dues(), [])

    def test_alerte_en_anglais_et_faite(self):
        self.cfg.__exit__(None, None, None)
        self.cfg = ConfigTemporaire({"outils": [], "langue": "en"})
        self.cfg.__enter__()
        t = taches.creer_tache("Call", "2026-03-04T10:05")
        self.assertEqual(taches.alertes_dues()[0]["detail"], "Due at 10:05")
        taches.cocher(t["id"], True)
        self.assertEqual(taches.alertes_dues(), [], "tâche faite : pas de rappel")


class TestRoutes(ServeurTest):
    def test_routes(self):
        with ConfigTemporaire({"outils": []}):
            statut, t = self.post("/api/taches/creer", {"titre": "Compte rendu", "echeance": "2030-01-02",
                                                        "description": "Réunion", "origine": "reunions"})
            self.assertEqual(statut, 200)
            self.assertEqual((t["titre"], t["echeance"], t["origine"]), ("Compte rendu", "2030-01-02", "reunions"))
            statut, r = self.post("/api/taches/creer", {"titre": ""})
            self.assertEqual(statut, 400)
            self.assertEqual(r["erreur"], "Indiquez un titre.")
            statut, r = self.post("/api/taches/modifier", {"tache": {"id": t["id"], "etiquettes": ["client"]}})
            self.assertEqual((statut, r["tache"]["etiquettes"]), (200, ["client"]))
            statut, r = self.post("/api/taches/deplacer", {"id": t["id"], "statut": "en_cours", "ordre": [t["id"]]})
            self.assertEqual(r["tache"]["statut"], "en_cours")
            statut, r = self.post("/api/taches/liste", {})
            self.assertEqual((statut, len(r["taches"]), r["etiquettes"]), (200, 1, ["client"]))
            statut, r = self.post("/api/taches/cocher", {"id": t["id"], "fait": True})
            self.assertEqual(r["tache"]["statut"], "fait")
            statut, r = self.post("/api/taches/jour", {})
            self.assertEqual((statut, r["total"]), (200, 0))
            statut, r = self.post("/api/taches/alertes", {})
            self.assertEqual(r, {"alertes": []})
            statut, r = self.post("/api/taches/supprimer", {"id": t["id"]})
            self.assertEqual(r, {"supprimes": 1})

    def test_sans_entete_refuse(self):
        with ConfigTemporaire({"outils": []}):
            statut, _ = self.post("/api/taches/creer", {"titre": "X"}, entete=False)
            self.assertNotEqual(statut, 200, "un ordre sans l'en-tête de la page est refusé")


if __name__ == "__main__":
    unittest.main()
