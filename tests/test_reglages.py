# -*- coding: utf-8 -*-
"""Tests du socle : routes automatiques des modules, liste des onglets,
Réglages et installation (raccourcis créés dans un dossier temporaire)."""
import io
import json
import os
import shutil
import sys
import tempfile
import urllib.error
import unittest
from unittest import mock

from aide import ConfigTemporaire, ServeurTest

import config  # noqa: E402
import installation  # noqa: E402
import reglages  # noqa: E402


class TestSocle(ServeurTest):
    def test_onglets_listes(self):
        with ConfigTemporaire({"langue": "en", "onglets_masques": ["ssh"]}):
            statut, r = self.get("/api/onglets")
        self.assertEqual(statut, 200)
        self.assertIn("reglages.js", r["fichiers"])
        self.assertNotIn("i18n.js", r["fichiers"], "i18n.js est chargé à part, en premier")
        self.assertNotIn("icones.js", r["fichiers"], "icones.js est chargé à part, en premier")
        self.assertEqual((r["langue"], r["masques"]), ("en", ["ssh"]))

    def test_module_inconnu_ou_invalide(self):
        for chemin in ("/api/reglages/n_existe_pas", "/api/..%2Fhub/x", "/api/Hub/x", "/api/existe_pas_du_tout/x"):
            statut, _ = self.post(chemin, {})
            self.assertEqual(statut, 404, chemin)

    def test_module_sans_entete_refuse(self):
        statut, _ = self.post("/api/reglages/lire", {}, entete=False)
        self.assertEqual(statut, 403)

    def test_lire_et_enregistrer(self):
        with ConfigTemporaire({"prenom": "Aina", "outils": []}) as cfg:
            statut, r = self.post("/api/reglages/lire", {})
            self.assertEqual((statut, r["prenom"], r["langue"]), (200, "Aina", "fr"))
            statut, r = self.post("/api/reglages/enregistrer",
                                  {"prenom": "  Rado ", "langue": "en", "onglets_masques": ["ssh", "accueil", "reglages"]})
            self.assertEqual(statut, 200)
            contenu = cfg.lire()
        self.assertEqual(contenu["prenom"], "Rado")
        self.assertEqual(contenu["langue"], "en")
        self.assertEqual(contenu["onglets_masques"], ["ssh"], "Accueil et Réglages ne se masquent pas")
        self.assertEqual(contenu["outils"], [], "le reste d'outils.json est conservé")

    def test_valeurs_refusees(self):
        with ConfigTemporaire() as cfg:
            statut, r = self.post("/api/reglages/enregistrer", {"langue": "de"})
            self.assertEqual(statut, 400)
            statut, _ = self.post("/api/reglages/enregistrer", {"onglets_masques": ["<script>"]})
            self.assertEqual(statut, 400)
            self.assertNotIn("langue", cfg.lire(), "rien n'est enregistré après un refus")

    def test_dossiers_projets(self):
        with ConfigTemporaire() as cfg:
            statut, r = self.post("/api/reglages/dossiers", {"dossiers": [cfg.dossier]})
            self.assertEqual((statut, r["dossiers_projets"]), (200, [cfg.dossier]))
            statut, _ = self.post("/api/reglages/dossiers", {"dossiers": [r"Z:\n-existe-pas"]})
            self.assertEqual(statut, 400)
            self.assertEqual(config.dossiers_projets(), [cfg.dossier])

    def _reponse_github(self, donnees):
        """Une fausse réponse de l'API GitHub (Releases)."""
        r = mock.MagicMock()
        r.__enter__.return_value = io.BytesIO(json.dumps(donnees).encode())
        return r

    def test_mise_a_jour_programme_installe(self):
        """Programme installé : la version publiée sur GitHub est proposée
        si elle est plus récente, avec le lien de l'installateur."""
        sortie = {"tag_name": "v9.0.0", "html_url": "https://github.com/x/y/releases/tag/v9.0.0",
                  "assets": [{"name": "notes.txt", "browser_download_url": "https://github.com/x/y/n.txt"},
                             {"name": "Mes-outils-Setup.exe", "browser_download_url": "https://github.com/x/y/Setup.exe"}]}
        with mock.patch.object(config, "GELE", True),                 mock.patch.object(reglages.urllib.request, "urlopen", return_value=self._reponse_github(sortie)):
            r = reglages.mise_a_jour()
        self.assertEqual((r["nouvelle"], r["telecharger"]), ("9.0.0", "https://github.com/x/y/Setup.exe"))
        sortie["tag_name"] = "v" + config.VERSION
        with mock.patch.object(config, "GELE", True),                 mock.patch.object(reglages.urllib.request, "urlopen", return_value=self._reponse_github(sortie)):
            self.assertNotIn("nouvelle", reglages.mise_a_jour(), "même version : rien à proposer")

    def test_mise_a_jour_sans_version_publiee(self):
        erreur = urllib.error.HTTPError(config.API_VERSIONS, 404, "Not Found", {}, None)
        with mock.patch.object(config, "GELE", True),                 mock.patch.object(reglages.urllib.request, "urlopen", side_effect=erreur),                 self.assertRaisesRegex(ValueError, "Aucune version"):
            reglages.mise_a_jour()

    def test_installation_automatique(self):
        """Programme installé : la nouvelle version est téléchargée puis
        l'installateur est lancé (/SILENT /RELANCER) ; Mes outils se ferme."""
        url = config.DEPOT + "/releases/download/v9.0.0/Mes-outils-Setup.exe"
        sortie = {"tag_name": "v9.0.0", "html_url": "x", "assets": [{"name": "Mes-outils-Setup.exe", "browser_download_url": url}]}
        programme = b"MZ" + b"\0" * 1_200_000

        def fausse_connexion(requete, timeout=0):
            adresse = requete.full_url if hasattr(requete, "full_url") else requete
            return self._reponse_github(sortie) if "api.github.com" in adresse else self._fichier(programme)

        with mock.patch.object(config, "GELE", True),                 mock.patch.object(reglages.urllib.request, "urlopen", side_effect=fausse_connexion),                 mock.patch.object(reglages.subprocess, "Popen") as lancer,                 mock.patch.object(reglages.threading, "Timer") as minuterie:
            r = reglages.installer_mise_a_jour()
        self.assertEqual(r, {"installation": True, "version": "9.0.0"})
        env = lancer.call_args.kwargs["env"]
        self.assertTrue(os.path.isfile(env["MO_SETUP"]), "l'installateur est téléchargé")
        self.assertIn("/RELANCER", lancer.call_args.args[0][-1])
        self.assertFalse(lancer.call_args.kwargs["creationflags"] & 0x00000008,
                         "DETACHED_PROCESS empêche PowerShell de démarrer")
        minuterie.assert_called_once()
        minuterie.return_value.start.assert_called_once()
        os.remove(env["MO_SETUP"])

    def _fichier(self, contenu):
        r = mock.MagicMock()
        r.__enter__.return_value = io.BytesIO(contenu)
        return r

    def test_installateur_refuse(self):
        with self.assertRaisesRegex(ValueError, "introuvable"):
            reglages.telecharger_installateur("https://exemple.com/Setup.exe", "9.0.0")
        url = config.DEPOT + "/releases/download/v9.0.0/Mes-outils-Setup.exe"
        with mock.patch.object(reglages.urllib.request, "urlopen", return_value=self._fichier(b"<html>")),                 self.assertRaisesRegex(ValueError, "pas un installateur"):
            reglages.telecharger_installateur(url, "9.0.0")
        with mock.patch.object(config, "GELE", False), self.assertRaisesRegex(ValueError, "programme installé"):
            reglages.installer_mise_a_jour()

    def test_comparaison_des_versions(self):
        self.assertGreater(reglages._version("v1.10.0"), reglages._version("1.9.9"))
        self.assertEqual(reglages._version("v1.3.0"), (1, 3, 0))


class TestProgrammeInstalle(unittest.TestCase):
    """Mes outils.exe (PyInstaller) : pas de Python sur le PC, données dans
    le dossier « Mes outils » de %APPDATA%."""

    def test_donnees_dans_appdata(self):
        with mock.patch.object(config, "GELE", True), mock.patch.dict(os.environ, {"APPDATA": r"C:\Profil\AppData"}):
            os.environ.pop("MES_OUTILS_DONNEES", None)
            self.assertEqual(config.dossier_utilisateur(), os.path.join(r"C:\Profil\AppData", "Mes outils"))
        with mock.patch.object(config, "GELE", False), mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("MES_OUTILS_DONNEES", None)
            self.assertEqual(config.dossier_utilisateur(), config.RACINE, "code source : données à côté du code")
        with mock.patch.dict(os.environ, {"MES_OUTILS_DONNEES": r"D:\Ailleurs"}):
            self.assertEqual(config.dossier_utilisateur(), r"D:\Ailleurs")

    def test_premier_lancement_cree_le_dossier(self):
        with ConfigTemporaire() as cfg:
            dossier = os.path.join(cfg.dossier, "nouveau", "Mes outils")
            exemple = os.path.join(cfg.dossier, "exemple.json")
            with open(exemple, "w", encoding="utf-8") as f:
                f.write('{"outils": []}')
            with mock.patch.object(config, "FICHIER_OUTILS", os.path.join(dossier, "outils.json")),                     mock.patch.object(config, "FICHIER_EXEMPLE", exemple):
                self.assertEqual(config.lire(), {"outils": []})
                config.modifier(prenom="Alex")
            self.assertTrue(os.path.isfile(os.path.join(dossier, "outils.json")))

    def test_modules_autorises_seulement(self):
        import hub
        connus = hub.modules_connus()
        self.assertIn("reglages", connus)
        self.assertNotIn("hub", connus)
        self.assertNotIn("bulle", connus)
        self.assertIsNone(hub.routes_module("antigravity"), "un module de Python ne doit jamais être chargé")
        self.assertIsNone(hub.routes_module("json"))
        dossier = tempfile.mkdtemp()
        try:
            with open(os.path.join(dossier, "modules.json"), "w", encoding="utf-8") as f:
                json.dump(["reglages"], f)
            with mock.patch.object(config, "GELE", True), mock.patch.object(hub, "ICI", dossier):
                self.assertEqual(hub.modules_connus(), {"reglages"})
                self.assertIsNone(hub.routes_module("projets"), "hors de la liste : refusé")
                self.assertIsNotNone(hub.routes_module("reglages"))
        finally:
            shutil.rmtree(dossier, ignore_errors=True)

    def test_raccourci_du_programme_installe(self):
        with mock.patch.object(installation, "GELE", True):
            self.assertEqual(installation.python_fenetre(), sys.executable)
            self.assertEqual(installation.verifier(), [], "rien à installer en plus")

    def test_reprise_d_une_ancienne_installation(self):
        """Premier lancement du programme installé : les réglages et données
        d'une copie « code source » sont copiés (l'original reste intact)."""
        profil = tempfile.mkdtemp()
        try:
            ancienne = os.path.join(profil, "Documents", "Mes outils")
            os.makedirs(os.path.join(ancienne, "outil"))
            os.makedirs(os.path.join(ancienne, "donnees"))
            for chemin, texte in (("outil/hub.py", "#"), ("outils.json", '{"prenom": "Alex", "outils": []}'),
                                  ("bulle.json", '{"position": [10, 20]}'), ("donnees/notes.json", "[1]")):
                with open(os.path.join(ancienne, chemin), "w", encoding="utf-8") as f:
                    f.write(texte)
            nouvelle = os.path.join(profil, "AppData", "Mes outils")
            with mock.patch.dict(os.environ, {"USERPROFILE": profil, "HOME": profil}),                     mock.patch.object(config, "GELE", True), mock.patch.object(config, "BASE", nouvelle),                     mock.patch.object(config, "FICHIER_OUTILS", os.path.join(nouvelle, "outils.json")),                     mock.patch.object(config, "DONNEES", os.path.join(nouvelle, "donnees")),                     mock.patch.object(config, "FICHIER_BULLE", os.path.join(nouvelle, "bulle.json")):
                os.environ.pop("OneDrive", None)
                self.assertEqual(config.anciennes_installations(), [ancienne])
                self.assertEqual(config.premier_lancement(), ancienne)
                self.assertEqual(config.lire()["prenom"], "Alex")
                self.assertIsNone(config.premier_lancement(), "une seule fois")
            with open(os.path.join(nouvelle, "donnees", "notes.json"), encoding="utf-8") as f:
                self.assertEqual(f.read(), "[1]")
            self.assertTrue(os.path.isfile(os.path.join(nouvelle, "bulle.json")))
            self.assertTrue(os.path.isfile(os.path.join(ancienne, "donnees", "notes.json")), "l'original reste en place")
        finally:
            shutil.rmtree(profil, ignore_errors=True)

    def test_mot_de_passe_ssh_sans_python(self):
        import ssh_cles
        self.assertNotIn("python", ssh_cles.CONTENU_ASKPASS.lower())
        self.assertIn("$env:MESOUTILS_SSH_SECRET", ssh_cles.CONTENU_ASKPASS)


class TestApplications(ServeurTest):
    """Applications actives, métier et assistant du premier lancement."""

    def test_installation_neuve_passe_par_l_assistant(self):
        with ConfigTemporaire({"assistant_fait": False, "outils": []}):
            statut, r = self.get("/api/onglets")
        self.assertEqual((statut, r["assistant"], r["apps_actives"]), (200, True, None))
        with ConfigTemporaire({"prenom": "Alex", "outils": []}):
            statut, r = self.get("/api/onglets")
        self.assertFalse(r["assistant"], "une ancienne installation ne repasse pas par l'assistant")

    def test_choix_des_applications(self):
        with ConfigTemporaire({"assistant_fait": False, "outils": []}) as cfg:
            statut, r = self.post("/api/reglages/enregistrer", {"apps_actives": ["taches", "agenda", "taches", "reglages"],
                                                                 "profil": "freelance", "assistant_fait": True})
            self.assertEqual(statut, 200)
            contenu = cfg.lire()
            self.assertEqual(contenu["apps_actives"], ["agenda", "taches"], "doublons et applications fixes retirés")
            self.assertEqual((contenu["profil"], contenu["assistant_fait"]), ("freelance", True))
            self.assertTrue(config.app_active("taches"))
            self.assertFalse(config.app_active("github"))
            self.assertTrue(config.app_active("reglages"), "toujours présente")

    def test_valeurs_refusees(self):
        with ConfigTemporaire() as cfg:
            for valeurs in ({"profil": "pirate"}, {"apps_actives": "taches"}, {"apps_actives": ["<script>"]}):
                statut, _ = self.post("/api/reglages/enregistrer", valeurs)
                self.assertEqual(statut, 400, valeurs)
            self.assertNotIn("apps_actives", cfg.lire())

    def test_ancienne_installation_tout_actif_sauf_masques(self):
        with ConfigTemporaire({"onglets_masques": ["ssh"], "outils": []}):
            self.assertTrue(config.app_active("github"))
            self.assertFalse(config.app_active("ssh"))

    def test_page_applications_chargee(self):
        with ConfigTemporaire():
            statut, r = self.get("/api/onglets")
        self.assertIn("applications.js", r["fichiers"])


class TestDonnees(unittest.TestCase):
    def test_ecriture_sure_avec_copie(self):
        with ConfigTemporaire():
            self.assertEqual(config.lire_donnees("essai"), [])
            self.assertEqual(config.lire_donnees("essai", {}), {})
            config.ecrire_donnees("essai", [1])
            config.ecrire_donnees("essai", [1, 2])
            self.assertEqual(config.lire_donnees("essai"), [1, 2])
            self.assertTrue(os.path.exists(config.chemin_donnees("essai") + ".bak"))

    def test_premier_lancement_depuis_l_exemple(self):
        with ConfigTemporaire() as cfg:
            os.remove(cfg.fichier)
            exemple = os.path.join(cfg.dossier, "exemple.json")
            with open(exemple, "w", encoding="utf-8") as f:
                f.write('{"prenom": "", "outils": [{"id": "x"}]}')
            with mock.patch.object(config, "FICHIER_EXEMPLE", exemple):
                self.assertEqual(config.lire()["outils"], [{"id": "x"}])
            self.assertTrue(os.path.exists(cfg.fichier))


class TestInstallation(unittest.TestCase):
    def test_dependances_presentes(self):
        self.assertEqual(installation.verifier(), [], "lancer les tests avec le Python de Mes outils")

    def test_raccourci_cree_puis_retire(self):
        dossier = tempfile.mkdtemp()
        try:
            with mock.patch.object(installation, "dossier_special", return_value=dossier):
                self.assertEqual(installation.etat(), {"bureau": False, "demarrage": False})
                chemin = installation.creer_raccourci("bureau")
                self.assertTrue(os.path.isfile(chemin))
                self.assertEqual(installation.etat()["bureau"], True)
                installation.supprimer_raccourci("bureau")
                self.assertFalse(os.path.exists(chemin))
        finally:
            shutil.rmtree(dossier, ignore_errors=True)

    def test_vrais_dossiers_windows(self):
        for genre in ("bureau", "demarrage"):
            self.assertTrue(os.path.isdir(installation.dossier_special(genre)), genre)


if __name__ == "__main__":
    unittest.main()
