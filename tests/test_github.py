# -*- coding: utf-8 -*-
"""Tests de l'onglet GitHub (github.py), sans toucher au vrai compte GitHub :
les appels à l'API sont simulés, git travaille sur des dépôts temporaires.

Lancer depuis la racine du projet :  python -m unittest discover -s tests
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.parse
import uuid
from http.server import ThreadingHTTPServer
from unittest import mock
import http.client

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outil"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # aide.py
import coffre_windows  # noqa: E402
from aide import ConfigTemporaire, ServeurTest  # noqa: E402
import github  # noqa: E402
import systeme  # noqa: E402

PROFIL_API = {"login": "testeur", "name": "Testeur", "avatar_url": "https://exemple/a.png", "id": 42}


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout


class FauxCoffre:
    """Remplace le coffre de Windows le temps d'un test."""

    def __init__(self, valeur=None):
        self.valeurs = {github.CIBLE_COFFRE: valeur} if valeur else {}

    def __enter__(self):
        self.patchs = [
            mock.patch.object(coffre_windows, "lire", side_effect=lambda c: self.valeurs.get(c)),
            mock.patch.object(coffre_windows, "ecrire", side_effect=lambda c, u, s: self.valeurs.__setitem__(c, s) or True),
            mock.patch.object(coffre_windows, "supprimer", side_effect=lambda c: self.valeurs.pop(c, None)),
        ]
        for p in self.patchs:
            p.start()
        github._cache["profil"] = None
        return self

    def __exit__(self, *exc):
        for p in self.patchs:
            p.stop()
        github._cache["profil"] = None


class TestAdresses(unittest.TestCase):
    def test_adresses_github_reconnues(self):
        self.assertEqual(github.depot_github("https://github.com/Moi/Projet.git"), "moi/projet")
        self.assertEqual(github.depot_github("git@github.com:moi/projet"), "moi/projet")
        self.assertEqual(github.depot_github("https://github.com/moi/mes-outils/"), "moi/mes-outils")
        self.assertIsNone(github.depot_github("https://gitlab.com/moi/projet.git"), "GitLab n'est pas GitHub")
        self.assertIsNone(github.depot_github(None))

    def test_nom_suggere(self):
        self.assertEqual(github.nom_suggere(r"C:\x\Mes outils"), "mes-outils")
        self.assertEqual(github.nom_suggere(r"C:\x\Projet été 2026\\"), "projet-t-2026")


class TestDepotsLocaux(unittest.TestCase):
    def setUp(self):
        self.racine = tempfile.mkdtemp()
        for nom, url in (("caisse", "https://github.com/moi/caisse.git"), ("autre", "https://gitlab.com/x/y.git")):
            chemin = os.path.join(self.racine, nom)
            os.makedirs(chemin)
            git("init", "-q", cwd=chemin)
            git("remote", "add", "origin", url, cwd=chemin)
        os.makedirs(os.path.join(self.racine, "pas-git"))

    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def test_retrouve_les_depots_github_du_dossier(self):
        trouves = github.depots_locaux([self.racine, r"Z:\n-existe-pas"])
        self.assertEqual(trouves, {"moi/caisse": os.path.join(self.racine, "caisse")},
                         "seul le dépôt GitHub doit être trouvé, le dossier absent ignoré")


class TestConnexion(unittest.TestCase):
    def setUp(self):
        github._attente.update(code=None)

    def test_sans_client_id(self):
        with self.assertRaises(github.ErreurGitHub):
            github.connexion_debut("")

    def test_parcours_complet(self):
        reponses = {
            github.URL_CODE: (200, {"device_code": "dc", "user_code": "ABCD-1234", "interval": 5,
                                    "verification_uri": "https://github.com/login/device", "expires_in": 900}),
        }
        jetons = iter([(200, {"error": "authorization_pending"}), (200, {"error": "slow_down", "interval": 10}),
                       (200, {"access_token": "gho_test", "token_type": "bearer"})])

        def faux_requete(methode, url, jeton=None, donnees=None, formulaire=None, delai=20):
            if url == github.URL_JETON:
                self.assertEqual(formulaire["device_code"], "dc")
                return next(jetons)
            if url == github.API + "/user":
                self.assertEqual(jeton, "gho_test")
                return 200, PROFIL_API
            return reponses[url]

        with FauxCoffre() as coffre, mock.patch.object(github, "_requete", side_effect=faux_requete), \
                mock.patch.object(github.webbrowser, "open") as ouvrir, mock.patch.object(github.time, "time") as horloge:
            horloge.return_value = 1000.0
            r = github.connexion_debut("client123")
            self.assertEqual(r["code"], "ABCD-1234")
            ouvrir.assert_called_once_with("https://github.com/login/device")
            self.assertEqual(github.connexion_suite()["etat"], "attente", "trop tôt : GitHub ne doit pas être appelé")
            horloge.return_value = 1006.0
            self.assertEqual(github.connexion_suite()["etat"], "attente")  # authorization_pending
            horloge.return_value = 1012.0
            self.assertEqual(github.connexion_suite()["etat"], "attente")  # slow_down → intervalle 10 s
            horloge.return_value = 1015.0
            self.assertEqual(github.connexion_suite()["etat"], "attente", "slow_down doit espacer les appels")
            horloge.return_value = 1023.0
            r = github.connexion_suite()
            self.assertEqual(r["etat"], "connecte")
            self.assertEqual(r["login"], "testeur")
            self.assertEqual(coffre.valeurs[github.CIBLE_COFFRE], "gho_test", "le jeton doit aller dans le coffre")
            self.assertEqual(github.connexion_suite()["etat"], "aucune")

    def test_code_expire_et_refus(self):
        with FauxCoffre(), mock.patch.object(github, "_requete", return_value=(200, {"error": "access_denied"})), \
                mock.patch.object(github.time, "time", return_value=5000.0):
            github._attente.update(code="dc", client_id="c", intervalle=5, prochain=0, expire=9999)
            self.assertEqual(github.connexion_suite()["etat"], "refuse")
            github._attente.update(code="dc", client_id="c", intervalle=5, prochain=0, expire=10)
            self.assertEqual(github.connexion_suite()["etat"], "expire")

    def test_device_flow_desactive(self):
        with mock.patch.object(github, "_requete", return_value=(400, {"error": "device_flow_disabled"})):
            with self.assertRaisesRegex(github.ErreurGitHub, "Device Flow"):
                github.connexion_debut("client123")

    def test_jeton_retire_chez_github(self):
        with FauxCoffre("gho_vieux") as coffre, mock.patch.object(github, "_requete", return_value=(401, {"message": "Bad credentials"})):
            with self.assertRaisesRegex(github.ErreurGitHub, "reconnectez"):
                github.etat()
            self.assertNotIn(github.CIBLE_COFFRE, coffre.valeurs, "un jeton refusé doit être retiré du coffre")


class TestListe(unittest.TestCase):
    def test_pagination_et_depots_locaux(self):
        page1 = [{"name": f"d{i}", "full_name": f"testeur/d{i}", "html_url": f"https://github.com/testeur/d{i}",
                  "private": i % 2 == 0, "pushed_at": f"2026-01-{(i % 28) + 1:02d}T00:00:00Z"} for i in range(100)]
        page2 = [{"name": "Caisse", "full_name": "testeur/Caisse", "html_url": "https://github.com/testeur/Caisse",
                  "private": True, "pushed_at": "2026-11-01T00:00:00Z", "language": "TypeScript"}]
        appels = []

        def faux_appel(methode, chemin, donnees=None):
            appels.append(chemin)
            return page1 if "page=1&" in chemin else page2

        with mock.patch.object(github, "_appel", side_effect=faux_appel), \
                mock.patch.object(github, "depots_locaux", return_value={"testeur/caisse": r"F:\Projets\caisse"}):
            r = github.lister_depots([r"F:\Projets"])
        self.assertEqual(len(appels), 2, "deux pages : 100 dépôts puis 1")
        self.assertEqual(len(r["depots"]), 101)
        self.assertEqual(r["depots"][0]["nom"], "Caisse", "le plus récent en premier")
        self.assertEqual(r["depots"][0]["local"], r"F:\Projets\caisse", "repéré sur ce PC malgré les majuscules")
        self.assertIsNone(r["depots"][1]["local"])


class TestEnvoi(unittest.TestCase):
    """Création d'un dépôt à partir d'un dossier : le « GitHub » est ici un
    dépôt nu local, pour vérifier les vraies commandes git."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.projet = os.path.join(self.tmp, "Mon Projet")
        os.makedirs(os.path.join(self.projet, "src"))
        os.makedirs(os.path.join(self.projet, "node_modules"))
        for chemin, contenu in (("src/app.py", "print('ok')\n"), (".gitignore", "secret.txt\nnode_modules/\n"),
                                ("secret.txt", "ne pas envoyer"), (".env", "CLE=123"), (".env.example", "CLE="),
                                ("node_modules/x.js", "x")):
            with open(os.path.join(self.projet, chemin.replace("/", os.sep)), "w", encoding="utf-8") as f:
                f.write(contenu)
        self.distant = os.path.join(self.tmp, "distant.git")
        git("init", "-q", "--bare", self.distant, cwd=self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_apercu_ne_modifie_rien_et_signale_les_risques(self):
        a = github.apercu(self.projet)
        self.assertFalse(os.path.exists(os.path.join(self.projet, ".git")), "l'aperçu ne doit rien créer")
        self.assertEqual(a["nombre"], 4, ".gitignore, .env, .env.example et src/app.py")
        self.assertEqual(a["sensibles"], [".env"], ".env signalé, .env.example non")
        self.assertEqual(a["nom_suggere"], "mon-projet")
        self.assertFalse(a["existant"])

    def test_fichier_trop_gros_refuse(self):
        with mock.patch.object(github, "TAILLE_MAX", 5):
            a = github.apercu(self.projet)
            self.assertIn("src/app.py", a["trop_gros"])
            with FauxCoffre("gho_test"), self.assertRaisesRegex(github.ErreurGitHub, "100 Mo"):
                github.creer_et_envoyer(self.projet, "mon-projet")

    def test_creer_et_envoyer(self):
        os.remove(os.path.join(self.projet, ".env"))
        cree = {}

        def faux_requete(methode, url, jeton=None, donnees=None, formulaire=None, delai=20):
            if url == github.API + "/user":
                return 200, PROFIL_API
            if url == github.API + "/user/repos" and methode == "POST":
                cree.update(donnees)
                return 201, {"html_url": "https://github.com/testeur/mon-projet", "full_name": "testeur/mon-projet",
                             "clone_url": self.distant}
            raise AssertionError(url)

        # Sans identité git : l'adresse « noreply » de GitHub doit être utilisée.
        env = {k: v for k, v in os.environ.items()}
        env.update(GIT_CONFIG_GLOBAL=os.path.join(self.tmp, "vide.gitconfig"), GIT_CONFIG_NOSYSTEM="1")
        with FauxCoffre("gho_test"), mock.patch.object(github, "_requete", side_effect=faux_requete), \
                mock.patch.dict(os.environ, env, clear=True):
            r = github.creer_et_envoyer(self.projet, "mon-projet", "Un test", prive=True)
        self.assertEqual(cree, {"name": "mon-projet", "description": "Un test", "private": True, "auto_init": False})
        self.assertEqual(r["nombre"], 3)
        envoyes = sorted(git("ls-tree", "-r", "--name-only", "main", cwd=self.distant).split())
        self.assertEqual(envoyes, [".env.example", ".gitignore", "src/app.py"], "secret.txt et node_modules exclus")
        auteur = git("log", "-1", "--format=%an <%ae>", "main", cwd=self.distant).strip()
        self.assertEqual(auteur, "testeur <42+testeur@users.noreply.github.com>")
        self.assertEqual(git("remote", "get-url", "origin", cwd=self.projet).strip(), self.distant)
        with open(os.path.join(self.projet, ".git", "config"), encoding="utf-8") as f:
            config = f.read()
        self.assertNotIn("gho_test", config, "le jeton ne doit jamais être écrit dans .git/config")
        # Un second envoi du même dossier est refusé (déjà relié).
        with FauxCoffre("gho_test"), self.assertRaisesRegex(github.ErreurGitHub, "déjà relié"):
            github.creer_et_envoyer(self.projet, "mon-projet")

    def test_nom_invalide(self):
        with self.assertRaisesRegex(github.ErreurGitHub, "invalide"):
            github.creer_et_envoyer(self.projet, "mon projet/../x")

    def test_jeton_passe_par_l_environnement(self):
        with FauxCoffre("gho_test"):
            github._cache["profil"] = {"login": "testeur", "id": 42}
            env = github._env_git(True)
        self.assertEqual(env["GIT_CONFIG_KEY_0"], "http.https://github.com/.extraheader")
        self.assertTrue(env["GIT_CONFIG_VALUE_0"].startswith("AUTHORIZATION: basic "))
        self.assertEqual(env["GIT_CONFIG_VALUE_1"], "", "le gestionnaire d'identifiants doit être écarté")


class TestCoffreWindows(unittest.TestCase):
    @unittest.skipUnless(sys.platform == "win32", "vrai coffre de Windows (pas de trousseau sur la machine de test Linux)")
    def test_aller_retour(self):
        cible = f"MesOutils:test:{uuid.uuid4()}"
        try:
            self.assertTrue(coffre_windows.ecrire(cible, "testeur", "secret-é-123"))
            self.assertEqual(coffre_windows.lire(cible), "secret-é-123")
        finally:
            coffre_windows.supprimer(cible)
        self.assertIsNone(coffre_windows.lire(cible))


class TestRoutes(ServeurTest):
    """Les routes /api/github/* du serveur local."""

    def test_etat_deconnecte(self):
        with FauxCoffre(), ConfigTemporaire({"dossiers_projets": ["X"]}):
            statut, r = self.post("/api/github/etat", {})
        self.assertEqual((statut, r), (200, {"connecte": False, "dossiers": ["X"]}))

    def test_ancien_emplacement_des_dossiers(self):
        with FauxCoffre(), ConfigTemporaire({"github": {"dossiers": ["Y"]}}):
            statut, r = self.post("/api/github/etat", {})
        self.assertEqual(r["dossiers"], ["Y"], "github > dossiers doit encore être lu")

    def test_ordre_sans_entete_refuse(self):
        statut, _ = self.post("/api/github/deconnexion", {}, entete=False)
        self.assertEqual(statut, 403, "une page d'un autre site ne doit pas pouvoir donner d'ordre")

    def test_erreur_github_renvoyee_en_400(self):
        with ConfigTemporaire({"github": {}}), mock.patch.object(github, "CLIENT_ID", ""):
            statut, r = self.post("/api/github/connexion/debut", {})
        self.assertEqual(statut, 400)
        self.assertIn("client_id", r["erreur"])

    def test_dossier_inexistant_refuse(self):
        with ConfigTemporaire({"github": {}}) as cfg:
            statut, r = self.post("/api/github/dossiers", {"dossiers": [r"Z:\n-existe-pas"]})
            self.assertEqual(statut, 400)
            self.assertNotIn("dossiers_projets", cfg.lire(), "rien ne doit être enregistré")

    def test_dossiers_enregistres(self):
        with ConfigTemporaire({"github": {"dossiers": ["ancien"]}}) as cfg:
            statut, r = self.post("/api/github/dossiers", {"dossiers": [cfg.dossier, cfg.dossier]})
            self.assertEqual((statut, r["dossiers"]), (200, [cfg.dossier]), "doublon retiré")
            contenu = cfg.lire()
        self.assertEqual(contenu["dossiers_projets"], [cfg.dossier])
        self.assertNotIn("dossiers", contenu["github"], "l'ancien emplacement est nettoyé")


# ---------------------------------------------------------------------------
# Pull requests, issues et GitHub Actions (API simulée)
# ---------------------------------------------------------------------------
def element_recherche(depot, numero, titre, brouillon=False, auteur="testeur"):
    return {"repository_url": f"https://api.github.com/repos/{depot}", "number": numero, "title": titre,
            "user": {"login": auteur, "avatar_url": ""}, "draft": brouillon,
            "updated_at": "2026-11-02T10:00:00Z", "created_at": "2026-11-01T10:00:00Z",
            "html_url": f"https://github.com/{depot}/pull/{numero}", "comments": 2,
            "labels": [{"name": "bug", "color": "d73a4a"}], "pull_request": {}}


def run(nom, statut, conclusion, date, workflow_id=None):
    return {"name": nom, "workflow_id": workflow_id or nom, "status": statut, "conclusion": conclusion,
            "updated_at": date, "display_title": "Un commit", "run_number": 7, "event": "push",
            "html_url": f"https://github.com/x/runs/{nom}"}


class FausseAPI:
    """Répond aux chemins de l'API comme GitHub ; compte les appels."""

    def __init__(self, reponses):
        self.reponses = reponses  # liste de (début du chemin, réponse ou exception)
        self.appels = []
        self.verrou = threading.Lock()

    def __call__(self, methode, chemin, donnees=None):
        with self.verrou:
            self.appels.append(chemin)
        for debut, reponse in self.reponses:
            if chemin.startswith(debut):
                if isinstance(reponse, Exception):
                    raise reponse
                return reponse
        raise github.ErreurGitHub("GitHub a refusé la demande (404) : Not Found.")


def api_pr_issues():
    return FausseAPI([
        ("/search/issues?q=" + urllib.parse.quote("is:pr is:open archived:false author:@me"),
         {"total_count": 2, "items": [element_recherche("moi/caisse", 12, "Ajout du ticket"),
                                      element_recherche("moi/site", 3, "Brouillon", brouillon=True)]}),
        ("/search/issues?q=" + urllib.parse.quote("is:pr is:open archived:false review-requested:@me"),
         {"total_count": 1, "items": [element_recherche("equipe/api", 40, "Revue SVP", auteur="collegue")]}),
        ("/issues?filter=assigned", [
            {**element_recherche("moi/caisse", 5, "Bug du total"), "pull_request": None,
             "repository": {"full_name": "moi/caisse"}},
            {**element_recherche("moi/caisse", 6, "Une PR assignée"), "pull_request": {"url": "x"}}]),
    ])


class BaseAPI(unittest.TestCase):
    def setUp(self):
        github._memoire.clear()
        self.coffre = FauxCoffre("gho_test")
        self.coffre.__enter__()

    def tearDown(self):
        self.coffre.__exit__()
        github._memoire.clear()


class TestPullRequestsEtIssues(BaseAPI):
    def test_pull_requests(self):
        with mock.patch.object(github, "_appel", side_effect=api_pr_issues()):
            r = github.pull_requests()
        self.assertEqual(r["nombre"], 3, "2 miennes + 1 revue demandée")
        self.assertEqual([p["numero"] for p in r["miennes"]], [12, 3])
        self.assertEqual(r["miennes"][0]["depot"], "moi/caisse", "dépôt tiré de repository_url")
        self.assertTrue(r["miennes"][1]["brouillon"], "le brouillon doit être signalé")
        self.assertEqual(r["revues"][0]["auteur"], "collegue")
        self.assertEqual(r["revues"][0]["url"], "https://github.com/equipe/api/pull/40")
        self.assertEqual(r["miennes"][0]["etiquettes"], [{"nom": "bug", "couleur": "d73a4a"}])

    def test_pull_requests_en_memoire(self):
        api = api_pr_issues()
        with mock.patch.object(github, "_appel", side_effect=api):
            github.pull_requests()
            github.pull_requests()
            self.assertEqual(len(api.appels), 2, "le second appel doit venir de la mémoire")
            github.pull_requests(forcer=True)
            self.assertEqual(len(api.appels), 4, "« forcer » doit relire GitHub")

    def test_issues_sans_les_pull_requests(self):
        with mock.patch.object(github, "_appel", side_effect=api_pr_issues()):
            r = github.issues_assignees()
        self.assertEqual(r["nombre"], 1, "la PR assignée doit être écartée")
        self.assertEqual(r["issues"][0]["titre"], "Bug du total")
        self.assertEqual(r["issues"][0]["depot"], "moi/caisse")
        self.assertEqual(r["issues"][0]["etiquettes"][0]["nom"], "bug")


class TestActions(BaseAPI):
    def api(self, en_plus=()):
        recents = [{"full_name": n, "html_url": f"https://github.com/{n}", "default_branch": b, "archived": a}
                   for n, b, a in (("moi/vert", "main", False), ("moi/rouge", "master", False),
                                   ("moi/encours", "main", False), ("moi/sans-ci", "main", False),
                                   ("moi/ferme", "main", False), ("moi/vieux", "main", True))]
        return FausseAPI([
            *en_plus,
            ("/user/repos", recents),
            ("/repos/moi/vert/actions/runs?per_page=10&branch=main",
             {"workflow_runs": [run("CI", "completed", "success", "2026-11-05T10:00:00Z")]}),
            # Le déploiement, plus récent, réussit ; mais le dernier « CI » a échoué.
            ("/repos/moi/rouge/actions/runs?per_page=10&branch=master",
             {"workflow_runs": [run("Deploy", "completed", "success", "2026-11-06T10:00:00Z"),
                                run("CI", "completed", "failure", "2026-11-05T09:00:00Z"),
                                run("CI", "completed", "success", "2026-11-01T09:00:00Z")]}),
            ("/repos/moi/encours/actions/runs",
             {"workflow_runs": [run("CI", "in_progress", None, "2026-11-07T10:00:00Z")]}),
            ("/repos/moi/sans-ci/actions/runs", {"total_count": 0, "workflow_runs": []}),
            ("/repos/moi/ferme/actions/runs", github.ErreurGitHub("GitHub a refusé la demande (404) : Not Found.")),
            ("/repos/autre/local/actions/runs?per_page=10&branch=dev",
             {"workflow_runs": [run("Tests", "completed", "timed_out", "2026-11-04T10:00:00Z")]}),
            ("/repos/Autre/Local/actions/runs?per_page=10&branch=dev",
             {"workflow_runs": [run("Tests", "completed", "timed_out", "2026-11-04T10:00:00Z")]}),
            ("/repos/autre/local", {"full_name": "Autre/Local", "default_branch": "dev",
                                    "html_url": "https://github.com/Autre/Local", "archived": False}),
        ])

    def lancer(self, api):
        locaux = {"moi/vert": r"X:\vert", "autre/local": r"X:\local"}
        with mock.patch.object(github, "_appel", side_effect=api), \
                mock.patch.object(github, "depots_locaux", return_value=locaux), \
                mock.patch.object(github.config, "dossiers_projets", return_value=["X:\\"]):
            return github.actions()

    def test_etat_des_runs(self):
        self.assertEqual(github.etat_run({"status": "completed", "conclusion": "success"}), "succes")
        self.assertEqual(github.etat_run({"status": "completed", "conclusion": "failure"}), "echec")
        self.assertEqual(github.etat_run({"status": "completed", "conclusion": "timed_out"}), "echec")
        self.assertEqual(github.etat_run({"status": "queued", "conclusion": None}), "en_cours")
        self.assertEqual(github.etat_run({"status": "completed", "conclusion": "cancelled"}), "annule")

    def test_dernier_run_par_depot(self):
        r = self.lancer(self.api())
        par_nom = {d["complet"].lower(): d for d in r["depots"]}
        self.assertNotIn("moi/vieux", par_nom, "un dépôt archivé n'est pas surveillé")
        self.assertEqual(par_nom["moi/vert"]["etat"], "succes")
        self.assertEqual(par_nom["moi/vert"]["local"], r"X:\vert")
        self.assertEqual(par_nom["moi/rouge"]["etat"], "echec", "un succès d'un autre workflow ne cache pas l'échec")
        self.assertEqual(par_nom["moi/rouge"]["workflow"], "CI")
        self.assertEqual(len(par_nom["moi/rouge"]["workflows"]), 2, "un résumé par workflow")
        self.assertEqual(par_nom["moi/encours"]["etat"], "en_cours")
        self.assertEqual(par_nom["moi/sans-ci"]["etat"], "aucun")
        self.assertEqual(par_nom["moi/ferme"]["etat"], "inconnu", "une erreur sur un dépôt ne bloque pas les autres")
        self.assertEqual(par_nom["autre/local"]["complet"], "Autre/Local", "dépôt du PC : nom exact lu chez GitHub")
        self.assertEqual(par_nom["autre/local"]["etat"], "echec", "branche par défaut « dev » utilisée")
        self.assertEqual(r["depots"][0]["etat"], "echec", "les échecs d'abord")
        self.assertEqual(sorted(r["echecs"]), ["Autre/Local", "moi/rouge"])

    def test_quota_sur_un_depot_remonte(self):
        api = self.api(en_plus=[("/repos/moi/vert/actions", github.ErreurQuotaGitHub(github.MESSAGE_QUOTA))])
        with self.assertRaises(github.ErreurQuotaGitHub, msg="le quota ne doit pas être pris pour « inconnu »"):
            self.lancer(api)

    def test_acces_retire_remonte(self):
        def faux_appel(methode, chemin, donnees=None):
            if chemin.startswith("/user/repos"):
                return [{"full_name": "moi/a", "html_url": "https://github.com/moi/a", "default_branch": "main"}]
            github.deconnecter()  # ce que fait _appel sur une réponse 401
            raise github.ErreurGitHub("L'accès à GitHub a été retiré : reconnectez GitHub.")
        with mock.patch.object(github, "_appel", side_effect=faux_appel), \
                mock.patch.object(github, "depots_locaux", return_value={}), \
                self.assertRaisesRegex(github.ErreurGitHub, "reconnectez"):
            github.actions()

    def test_quota_detecte(self):
        reponse = (403, {"message": "API rate limit exceeded for user ID 1."})
        with mock.patch.object(github, "_requete", return_value=reponse):
            with self.assertRaisesRegex(github.ErreurQuotaGitHub, "Limite"):
                github.pull_requests()
        with mock.patch.object(github, "_requete", return_value=(429, None)):
            with self.assertRaises(github.ErreurQuotaGitHub):
                github.issues_assignees()
        with mock.patch.object(github, "_requete", return_value=(403, {"message": "Resource not accessible"})):
            with self.assertRaises(github.ErreurGitHub) as e:
                github.issues_assignees()
        self.assertNotIsInstance(e.exception, github.ErreurQuotaGitHub, "un simple 403 n'est pas le quota")


class TestEchecsCI(BaseAPI):
    def faux_calcul(self):
        self.calculs += 1
        return {"depots": [], "echecs": ["moi/rouge"], "nombre_echecs": 1, "heure": ""}

    def test_memoire_de_5_minutes(self):
        self.calculs = 0
        with mock.patch.object(github, "_calcul_actions", side_effect=self.faux_calcul), \
                mock.patch.object(github.time, "time") as horloge:
            horloge.return_value = 10000.0
            self.assertEqual(github.echecs_ci(), {"nombre": 1, "depots": ["moi/rouge"]})
            horloge.return_value = 10000.0 + 290
            github.echecs_ci()
            self.assertEqual(self.calculs, 1, "pas de nouvel appel à GitHub avant 5 min")
            horloge.return_value = 10000.0 + 301
            github.echecs_ci()
            self.assertEqual(self.calculs, 2, "après 5 min, GitHub est relu")

    def test_partage_la_memoire_de_la_page(self):
        self.calculs = 0
        with mock.patch.object(github, "_calcul_actions", side_effect=self.faux_calcul):
            github.actions()
            github.echecs_ci()
        self.assertEqual(self.calculs, 1, "la bulle réutilise ce que la page vient de lire")

    def test_hors_connexion(self):
        self.coffre.valeurs.clear()
        with mock.patch.object(github, "_appel") as appel:
            self.assertEqual(github.echecs_ci(), {"nombre": 0, "depots": []})
        appel.assert_not_called()

    def test_hors_ligne(self):
        erreur = github.ErreurGitHub("GitHub ne répond pas : vérifiez la connexion internet.")
        with mock.patch.object(github, "_requete", side_effect=erreur):
            r = github.echecs_ci()
        self.assertEqual(r["nombre"], 0, "hors ligne : 0, sans exception")
        self.assertIn("ne répond pas", r["erreur"])

    def test_quota_atteint(self):
        with mock.patch.object(github, "_requete", return_value=(403, {"message": "API rate limit exceeded"})):
            r = github.echecs_ci()
        self.assertEqual((r["nombre"], r["depots"]), (0, []))
        self.assertEqual(r["erreur"], github.MESSAGE_QUOTA)

    def test_deconnexion_vide_la_memoire(self):
        self.calculs = 0
        with mock.patch.object(github, "_calcul_actions", side_effect=self.faux_calcul):
            github.actions()
            github.deconnecter()
            self.coffre.valeurs[github.CIBLE_COFFRE] = "gho_autre"
            github.actions()
        self.assertEqual(self.calculs, 2, "un autre compte ne doit pas voir la mémoire du précédent")


class TestRoutesNouvelles(ServeurTest):
    def setUp(self):
        github._memoire.clear()

    def test_routes_declarees(self):
        self.assertEqual(sorted(github.ROUTES), ["actions", "echecs_ci", "issues", "prs"])

    def test_prs_par_le_serveur(self):
        with FauxCoffre("gho_test"), ConfigTemporaire({"github": {}}), \
                mock.patch.object(github, "_appel", side_effect=api_pr_issues()):
            statut, r = self.post("/api/github/prs", {"forcer": True})
        self.assertEqual((statut, r["nombre"]), (200, 3))

    def test_quota_en_400(self):
        with FauxCoffre("gho_test"), ConfigTemporaire({"github": {}}), \
                mock.patch.object(github, "_requete", return_value=(429, None)):
            statut, r = self.post("/api/github/issues", {})
        self.assertEqual((statut, r["erreur"]), (400, github.MESSAGE_QUOTA))

    def test_echecs_ci_non_connecte(self):
        with FauxCoffre(), ConfigTemporaire({"github": {}}):
            statut, r = self.post("/api/github/echecs_ci", {})
        self.assertEqual((statut, r), (200, {"nombre": 0, "depots": []}))


class TestOuvrirPortable(unittest.TestCase):
    """Dossier et VS Code par la couche systeme (branches Linux simulées)."""

    def setUp(self):
        self.dossier = tempfile.mkdtemp(prefix="mo-gh-")

    def tearDown(self):
        shutil.rmtree(self.dossier, ignore_errors=True)

    def test_dossier(self):
        with mock.patch.object(systeme, "ouvrir") as ouvrir:
            github.ouvrir_dossier(self.dossier)
        ouvrir.assert_called_once_with(self.dossier)
        with self.assertRaises(github.ErreurGitHub):
            github.ouvrir_dossier(os.path.join(self.dossier, "absent"))

    def test_vscode_linux(self):
        with mock.patch.object(systeme, "WINDOWS", False), \
                mock.patch.object(systeme, "code_vscode", return_value="/usr/bin/code"), \
                mock.patch.object(systeme, "lancer_detache") as lancer, \
                mock.patch.object(github.subprocess, "Popen") as popen:
            github.ouvrir_vscode(self.dossier)
        lancer.assert_called_once_with(["/usr/bin/code", self.dossier])
        popen.assert_not_called()
        with mock.patch.object(systeme, "code_vscode", return_value=None), \
                self.assertRaisesRegex(github.ErreurGitHub, "VS Code est introuvable"):
            github.ouvrir_vscode(self.dossier)

    def test_git_sans_drapeaux_windows(self):
        fini = subprocess.CompletedProcess([], 0, "ok", "")
        with mock.patch.object(systeme, "WINDOWS", False), \
                mock.patch.object(github.subprocess, "run", return_value=fini) as run:
            self.assertEqual(github._git(["status"], self.dossier), "ok")
        self.assertNotIn("creationflags", run.call_args.kwargs, "jamais creationflags hors de Windows")


if __name__ == "__main__":
    unittest.main()
