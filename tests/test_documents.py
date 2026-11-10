# -*- coding: utf-8 -*-
"""Tests de l'application Documents : ajout de fichiers et de dossiers,
copie dans le classeur (jamais d'écrasement, l'original ne bouge pas),
retrait sans suppression du fichier, fichiers introuvables et « Retrouver »,
rappels avant expiration, fenêtre Windows simulée, routes du serveur.
Tout se passe dans des dossiers temporaires."""
import datetime
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # aide.py, quel que soit le lancement

from aide import ConfigTemporaire, ServeurTest  # noqa: E402

import documents  # noqa: E402

AUJOURDHUI = datetime.date(2026, 3, 2)


class BaseDocuments(unittest.TestCase):
    def setUp(self):
        self.cfg = ConfigTemporaire({"outils": [], "langue": "fr"})
        self.cfg.__enter__()
        self.dossier = tempfile.mkdtemp(prefix="mes-outils-docs-")
        self.classeur = os.path.join(self.dossier, "Documents", "Mes outils", "Classeur")
        self.patchs = [mock.patch.object(documents, "aujourdhui", lambda: AUJOURDHUI),
                       mock.patch.object(documents, "dossier_classeur", lambda: self.classeur)]
        for p in self.patchs:
            p.start()

    def tearDown(self):
        for p in self.patchs:
            p.stop()
        self.cfg.__exit__(None, None, None)
        shutil.rmtree(self.dossier, ignore_errors=True)

    def fichier(self, nom, contenu="exemple", sous_dossier="pc"):
        dossier = os.path.join(self.dossier, sous_dossier)
        os.makedirs(dossier, exist_ok=True)
        chemin = os.path.join(dossier, nom)
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(contenu)
        return chemin

    def ajouter_un(self, chemin, **champs):
        return documents.ajouter({"chemins": [chemin], **champs})["ajoutes"][0]


class TestAjout(BaseDocuments):
    def test_ajouter_un_fichier(self):
        chemin = self.fichier("Contrat Studio Exemple.pdf")
        os.utime(chemin, (datetime.datetime(2026, 1, 15, 10).timestamp(),) * 2)
        f = self.ajouter_un(chemin, type="contrat", client="  Studio   Exemple ", etiquettes="signé, #original, Signé")
        self.assertEqual(f["titre"], "Contrat Studio Exemple", "titre par défaut : le nom du fichier sans extension")
        self.assertEqual((f["genre"], f["type"], f["client"]), ("fichier", "contrat", "Studio Exemple"))
        self.assertEqual(f["etiquettes"], ["signé", "original"], "étiquettes nettoyées, sans doublon")
        self.assertEqual(f["date_document"], "2026-01-15", "date par défaut : celle du fichier")
        self.assertTrue(f["existe"])
        self.assertFalse(f["copie"])
        self.assertEqual(f["chemin"], chemin, "le fichier est référencé, pas déplacé")
        self.assertEqual(len(documents.lister()["fiches"]), 1)

    def test_plusieurs_fichiers_champs_communs(self):
        a, b = self.fichier("a.pdf"), self.fichier("b.pdf")
        r = documents.ajouter({"chemins": [a, b], "titre": "ignoré", "projet": "Site vitrine",
                               "type": "attestation", "date_document": "2026-02-01"})
        self.assertEqual([f["titre"] for f in r["ajoutes"]], ["a", "b"], "plusieurs fichiers : chacun son nom")
        self.assertTrue(all(f["projet"] == "Site vitrine" and f["type"] == "attestation" for f in r["ajoutes"]))
        self.assertTrue(all(f["date_document"] == "2026-02-01" for f in r["ajoutes"]))
        r = documents.ajouter({"chemins": [a]})
        self.assertEqual((r["ajoutes"], r["deja"]), ([], 1), "un fichier déjà présent n'est pas ajouté deux fois")
        self.assertEqual(documents.lister()["projets"], ["Site vitrine"])

    def test_ajouter_un_dossier(self):
        dossier = os.path.join(self.dossier, "Dossier client")
        os.makedirs(dossier)
        f = self.ajouter_un(dossier, genre="dossier", type="autre")
        self.assertEqual((f["genre"], f["titre"], f["date_document"]), ("dossier", "Dossier client", ""))
        with self.assertRaisesRegex(ValueError, "Choisissez un dossier"):
            documents.ajouter({"chemins": [self.fichier("x.txt")], "genre": "dossier"})
        with self.assertRaisesRegex(ValueError, "Seuls les fichiers"):
            documents.ajouter({"chemins": [dossier], "copier": True})

    def test_chemins_refuses(self):
        with self.assertRaisesRegex(ValueError, "Aucun fichier"):
            documents.ajouter({"chemins": []})
        with self.assertRaisesRegex(ValueError, "introuvable"):
            documents.ajouter({"chemins": [os.path.join(self.dossier, "absent.pdf")]})
        with self.assertRaisesRegex(ValueError, "Chemin invalide"):
            documents.ajouter({"chemins": ["relatif.pdf"]})
        ok = self.fichier("ok.pdf")
        with self.assertRaises(ValueError):
            documents.ajouter({"chemins": [ok, os.path.join(self.dossier, "absent.pdf")]})
        self.assertEqual(documents.lister()["fiches"], [], "rien n'est ajouté si un chemin est mauvais")
        with self.assertRaisesRegex(ValueError, "Type de document inconnu"):
            documents.ajouter({"chemins": [ok], "type": "facture_client"})


class TestCopie(BaseDocuments):
    def test_copie_dans_le_classeur(self):
        source = self.fichier("Devis.pdf", "original")
        f = self.ajouter_un(source, copier=True, client="Studio Exemple", type="devis_signe")
        attendu = os.path.join(self.classeur, "Studio Exemple", "Devis.pdf")
        self.assertEqual(f["chemin"], attendu)
        self.assertTrue(f["copie"])
        self.assertTrue(os.path.isfile(source), "l'original ne bouge pas")
        with open(attendu, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "original")
        # Même nom une seconde fois : jamais d'écrasement.
        autre = self.fichier("Devis.pdf", "autre version", sous_dossier="pc2")
        g = self.ajouter_un(autre, copier=True, client="Studio Exemple")
        self.assertEqual(os.path.basename(g["chemin"]), "Devis (2).pdf")
        with open(attendu, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "original", "la première copie n'est pas écrasée")

    def test_rubrique_sure(self):
        source = self.fichier("a.txt")
        f = self.ajouter_un(source, copier=True, client='..\\..\\Clients: "A/B"')
        self.assertTrue(f["chemin"].startswith(self.classeur + os.sep), "la copie reste dans le classeur")
        g = self.ajouter_un(self.fichier("b.txt"), copier=True)
        self.assertEqual(os.path.basename(os.path.dirname(g["chemin"])), "Non classé")
        self.assertEqual(documents.nom_de_dossier("CON"), "Non classé")
        self.assertEqual(documents.nom_de_dossier(" Projet  X. "), "Projet X")

    def test_fichier_deja_dans_le_classeur(self):
        dedans = os.path.join(self.classeur, "A")
        os.makedirs(dedans)
        chemin = os.path.join(dedans, "c.pdf")
        open(chemin, "w").close()
        f = self.ajouter_un(chemin, copier=True, client="A")
        self.assertEqual(f["chemin"], chemin, "pas de seconde copie d'un fichier déjà rangé")
        self.assertEqual(os.listdir(dedans), ["c.pdf"])


class TestFiches(BaseDocuments):
    def test_retirer_ne_supprime_pas_le_fichier(self):
        chemin = self.fichier("Attestation.pdf")
        f = self.ajouter_un(chemin)
        documents.retirer({"id": f["id"]})
        self.assertEqual(documents.lister()["fiches"], [])
        self.assertTrue(os.path.isfile(chemin), "retirer de la liste ne supprime jamais le fichier")
        with self.assertRaisesRegex(ValueError, "introuvable dans la liste"):
            documents.retirer({"id": f["id"]})

    def test_modifier(self):
        f = self.ajouter_un(self.fichier("x.pdf"))
        g = documents.modifier({"id": f["id"], "titre": "Assurance RC Pro", "type": "assurance",
                                "expiration": "2027-01-31", "rappel_jours": 60, "note": "Échéance annuelle",
                                "chemin": "C:\\ailleurs.pdf"})
        self.assertEqual((g["titre"], g["type"], g["expiration"], g["rappel_jours"]),
                         ("Assurance RC Pro", "assurance", "2027-01-31", 60))
        self.assertEqual(g["chemin"], f["chemin"], "le chemin ne change que par « Retrouver »")
        with self.assertRaisesRegex(ValueError, "Indiquez un titre"):
            documents.modifier({"id": f["id"], "titre": "  "})
        with self.assertRaisesRegex(ValueError, "Date d'expiration invalide"):
            documents.modifier({"id": f["id"], "expiration": "31/01/2027"})
        with self.assertRaisesRegex(ValueError, "après la date du document"):
            documents.modifier({"id": f["id"], "date_document": "2026-01-01", "expiration": "2025-12-31"})

    def test_introuvable_puis_retrouver(self):
        chemin = self.fichier("Kbis.pdf")
        f = self.ajouter_un(chemin)
        nouveau = os.path.join(self.dossier, "rangé", "Kbis.pdf")
        os.makedirs(os.path.dirname(nouveau))
        os.replace(chemin, nouveau)
        v = documents.lister()["fiches"][0]
        self.assertFalse(v["existe"], "un fichier déplacé est signalé introuvable")
        with self.assertRaisesRegex(ValueError, "Introuvable"):
            documents.ouvrir({"id": f["id"]})
        with self.assertRaisesRegex(ValueError, "Choisissez un fichier"):
            documents.retrouver({"id": f["id"], "chemin": os.path.dirname(nouveau)})
        g = documents.retrouver({"id": f["id"], "chemin": nouveau})
        self.assertTrue(g["existe"])
        self.assertEqual(g["chemin"], nouveau)
        # Un autre document déjà dans la liste ne peut pas être « retrouvé » à sa place.
        h = self.ajouter_un(self.fichier("autre.pdf"))
        with self.assertRaisesRegex(ValueError, "déjà dans la liste"):
            documents.retrouver({"id": h["id"], "chemin": nouveau})

    def test_ouvrir_et_ouvrir_le_dossier(self):
        chemin = self.fichier("Facture fournisseur.pdf")
        f = self.ajouter_un(chemin, type="facture_fournisseur")
        with mock.patch.object(documents.systeme, "ouvrir") as ouvre:
            documents.ouvrir({"id": f["id"]})
        ouvre.assert_called_once_with(chemin)
        with mock.patch.object(documents.systeme, "montrer_dans_dossier") as montrer:
            documents.ouvrir_dossier({"id": f["id"]})
        montrer.assert_called_once_with(chemin)
        # Fichier disparu : on ouvre au moins son dossier.
        os.remove(chemin)
        with mock.patch.object(documents.systeme, "ouvrir") as ouvre:
            documents.ouvrir_dossier({"id": f["id"]})
        ouvre.assert_called_once_with(os.path.dirname(chemin))

    @unittest.skipUnless(sys.platform == "win32", "Explorateur de Windows")
    def test_ouvrir_le_dossier_sous_windows(self):
        chemin = self.fichier("Contrat.pdf")
        f = self.ajouter_un(chemin)
        with mock.patch.object(documents.systeme.subprocess, "Popen") as explorer:
            documents.ouvrir_dossier({"id": f["id"]})
        self.assertEqual(explorer.call_args[0][0], f'explorer.exe /select,"{chemin}"')
        with mock.patch.object(documents.systeme.os, "startfile", create=True) as ouvre:
            documents.ouvrir({"id": f["id"]})
        ouvre.assert_called_once_with(chemin)

    def test_ouvrir_le_dossier_sous_linux(self):
        """Branche Linux simulée : Nautilus sélectionne le fichier, sinon xdg-open sur le dossier."""
        chemin = self.fichier("Contrat.pdf")
        f = self.ajouter_un(chemin)
        trouve = {"nautilus": "/usr/bin/nautilus", "xdg-open": "/usr/bin/xdg-open"}
        with mock.patch.object(documents.systeme, "WINDOWS", False), \
                mock.patch.object(documents.systeme.shutil, "which", side_effect=trouve.get), \
                mock.patch.object(documents.systeme, "lancer_detache") as lancer:
            documents.ouvrir_dossier({"id": f["id"]})
            documents.ouvrir({"id": f["id"]})
        self.assertEqual(lancer.call_args_list[0][0][0], ["nautilus", "--select", os.path.abspath(chemin)])
        self.assertEqual(lancer.call_args_list[1][0][0], ["xdg-open", chemin])

    def test_choisir_fichiers(self):
        present = self.fichier("présent.pdf")
        with mock.patch.object(documents.systeme, "choisir_fichiers", return_value=[present]) as choisir:
            r = documents.choisir_fichiers({"titre": "Choisir", "depart": os.path.join(self.dossier, "pc", "x", "y")})
        self.assertEqual(r["chemins"], [present])
        titre, depart = choisir.call_args[0]
        self.assertEqual((titre, depart), ("Choisir", os.path.join(self.dossier, "pc", "x", "y")))
        self.assertTrue(choisir.call_args.kwargs["multi"])
        self.assertEqual(choisir.call_args.kwargs["filtre"], "Tous les fichiers (*.*)|*.*")
        with mock.patch.object(documents.systeme, "choisir_fichiers", return_value=[]) as choisir:
            self.assertEqual(documents.choisir_fichiers({"multi": False})["chemins"], [])
        self.assertFalse(choisir.call_args.kwargs["multi"])

    def test_choisir_fichiers_fenetre_windows(self):
        """La fenêtre de Windows (PowerShell simulé) : départ = dossier existant le plus proche."""
        present = self.fichier("présent.pdf")
        sortie = mock.Mock(stdout=f"{present}\r\n{os.path.join(self.dossier, 'absent.pdf')}\r\n")
        with mock.patch.object(documents.systeme, "WINDOWS", True), \
                mock.patch.object(documents.systeme.subprocess, "run", return_value=sortie) as run:
            r = documents.choisir_fichiers({"titre": "Choisir", "depart": os.path.join(self.dossier, "pc", "x", "y")})
        self.assertEqual(r["chemins"], [present], "seuls les fichiers qui existent sont rendus")
        self.assertEqual(run.call_args[0][0][0], "powershell")
        env = run.call_args.kwargs["env"]
        self.assertEqual(env["MO_MULTI"], "1")
        self.assertEqual(env["MO_DEPART"], os.path.join(self.dossier, "pc"), "départ : le dossier existant le plus proche")
        self.assertNotIn("shell", run.call_args.kwargs)

    def test_choisir_fichiers_linux(self):
        """Branche Linux simulée : zenity, et un message clair s'il n'y a aucune fenêtre."""
        present = self.fichier("présent.pdf")
        with mock.patch.object(documents.systeme, "WINDOWS", False), \
                mock.patch.object(documents.systeme, "outil_de_fenetres", return_value="zenity"), \
                mock.patch.object(documents.systeme.subprocess, "run", return_value=mock.Mock(stdout=present + "\n")) as run:
            r = documents.choisir_fichiers({"titre": "Choisir"})
        self.assertEqual(r["chemins"], [present])
        args = run.call_args[0][0]
        self.assertEqual(args[:2], ["zenity", "--file-selection"])
        self.assertIn("--multiple", args)
        self.assertNotIn("creationflags", run.call_args.kwargs, "jamais de creationflags hors de Windows")
        with mock.patch.object(documents.systeme, "WINDOWS", False), \
                mock.patch.object(documents.systeme, "outil_de_fenetres", return_value=None):
            with self.assertRaisesRegex(ValueError, "zenity"):
                documents.choisir_fichiers({"titre": "Choisir"})

    def test_dossier_documents_du_systeme(self):
        with mock.patch.object(documents.systeme, "dossier_documents", return_value="/home/moi/Documents"):
            self.assertEqual(documents.dossier_documents(), "/home/moi/Documents")


class TestAlertes(BaseDocuments):
    def fiche_expirant(self, expiration, **champs):
        return self.ajouter_un(self.fichier(f"doc-{expiration}.pdf"), titre="Assurance", expiration=expiration,
                               date_document="2025-01-01", **champs)

    def test_rappel_avant_expiration(self):
        f = self.fiche_expirant("2026-03-22")            # dans 20 jours
        self.fiche_expirant("2026-04-11")                 # dans 40 jours : trop tôt
        dues = documents.alertes_dues()
        self.assertEqual([a["id"] for a in dues], [f"{f['id']}:2026-03-22"])
        self.assertEqual(dues[0]["titre"], "Document qui expire : Assurance")
        self.assertIn("dans 20 jours", dues[0]["detail"])
        self.assertTrue(documents.marquer_alerte(dues[0]["id"]))
        self.assertEqual(documents.alertes_dues(), [], "une alerte vue ne revient pas")
        self.assertFalse(documents.marquer_alerte("inconnue"))
        # Nouvelle date d'expiration : le rappel est réarmé.
        documents.modifier({"id": f["id"], "expiration": "2026-03-03"})
        dues = documents.alertes_dues()
        self.assertEqual(len(dues), 1)
        self.assertIn("demain", dues[0]["detail"])

    def test_rappel_personnalise_et_expires(self):
        self.fiche_expirant("2026-04-11", rappel_jours=60)     # 40 jours, rappel 60 : dû
        self.fiche_expirant("2026-02-20")                      # expiré depuis 10 jours
        self.fiche_expirant("2026-01-01")                      # expiré depuis 60 jours : oublié
        self.fiche_expirant("2026-03-12", rappel_jours=0)      # aucun rappel
        titres = sorted(a["titre"] for a in documents.alertes_dues())
        self.assertEqual(titres, ["Document expiré : Assurance", "Document qui expire : Assurance"])

    def test_alertes_en_anglais(self):
        self.cfg.contenu["langue"] = "en"
        import json
        with open(self.cfg.fichier, "w", encoding="utf-8") as fh:
            json.dump(self.cfg.contenu, fh)
        self.fiche_expirant("2026-03-02")
        a = documents.alertes_dues()[0]
        self.assertEqual(a["titre"], "Document expiring: Assurance")
        self.assertTrue(a["detail"].startswith("Expires today"))

    def test_jours_restants_dans_la_liste(self):
        self.fiche_expirant("2026-03-12")
        self.assertEqual(documents.lister()["fiches"][0]["jours"], 10)


class TestRoutes(ServeurTest):
    def test_routes(self):
        with ConfigTemporaire({"outils": []}), tempfile.TemporaryDirectory() as dossier, \
                mock.patch.object(documents, "dossier_classeur", lambda: os.path.join(dossier, "Classeur")):
            chemin = os.path.join(dossier, "Contrat.pdf")
            open(chemin, "w").close()
            statut, r = self.post("/api/documents/liste", {})
            self.assertEqual((statut, r["fiches"]), (200, []))
            self.assertIn("contrat", r["types"])
            statut, r = self.post("/api/documents/ajouter", {"chemins": [chemin], "type": "contrat", "client": "Client A"})
            self.assertEqual(statut, 200, r)
            ident = r["ajoutes"][0]["id"]
            statut, r = self.post("/api/documents/ajouter", {"chemins": [os.path.join(dossier, "absent.pdf")]})
            self.assertEqual(statut, 400)
            self.assertIn("introuvable", r["erreur"])
            statut, r = self.post("/api/documents/alertes", {})
            self.assertEqual((statut, r), (200, {"alertes": []}))
            statut, r = self.post("/api/documents/retirer", {"id": ident})
            self.assertEqual(statut, 200)
            self.assertTrue(os.path.isfile(chemin), "le fichier reste sur le disque")
            statut, r = self.post("/api/documents/liste", {}, entete=False)
            self.assertEqual(statut, 403, "sans l'en-tête X-Mes-Outils, le serveur refuse")


if __name__ == "__main__":
    unittest.main()
