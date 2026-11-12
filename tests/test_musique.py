# -*- coding: utf-8 -*-
"""Tests de l'onglet Musique (outil/musique.py)."""
import os
import tempfile
import unittest

from aide import ConfigTemporaire, ServeurTest
import musique


class TestRoutes(ServeurTest):
    def test_lister_vide(self):
        with ConfigTemporaire():
            statut, r = self.post("/api/musique/lister", {})
        self.assertEqual(statut, 200)
        self.assertEqual(r["pistes"], [])

    def test_ajouter_et_supprimer(self):
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(b"audio")
            chemin = f.name
        try:
            with ConfigTemporaire():
                statut, r = self.post("/api/musique/ajouter", {"chemin": chemin})
                self.assertEqual(statut, 200)
                self.assertEqual(r["titre"], os.path.splitext(os.path.basename(chemin))[0])
                pid = r["id"]
                statut, r = self.post("/api/musique/lister", {})
                self.assertEqual(len(r["pistes"]), 1)
                statut, r = self.post("/api/musique/supprimer", {"id": pid})
                self.assertEqual(statut, 200)
                statut, r = self.post("/api/musique/lister", {})
                self.assertEqual(r["pistes"], [])
        finally:
            os.remove(chemin)

    def test_ajouter_fichier_inexistant(self):
        with ConfigTemporaire():
            statut, r = self.post("/api/musique/ajouter", {"chemin": "/tmp/inexistant.mp3"})
        self.assertEqual(statut, 400)

    def test_ajouter_format_non_pris_en_charge(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"texte")
            chemin = f.name
        try:
            with ConfigTemporaire():
                statut, r = self.post("/api/musique/ajouter", {"chemin": chemin})
            self.assertEqual(statut, 400)
        finally:
            os.remove(chemin)

    def test_ajouter_doublon(self):
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(b"audio")
            chemin = f.name
        try:
            with ConfigTemporaire():
                self.post("/api/musique/ajouter", {"chemin": chemin})
                statut, r = self.post("/api/musique/ajouter", {"chemin": chemin})
            self.assertEqual(statut, 400)
        finally:
            os.remove(chemin)

    def test_vider(self):
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(b"audio")
            chemin = f.name
        try:
            with ConfigTemporaire():
                self.post("/api/musique/ajouter", {"chemin": chemin})
                statut, r = self.post("/api/musique/vider", {})
                self.assertEqual(statut, 200)
                statut, r = self.post("/api/musique/lister", {})
                self.assertEqual(r["pistes"], [])
        finally:
            os.remove(chemin)


if __name__ == "__main__":
    unittest.main()