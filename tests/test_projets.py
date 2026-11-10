# -*- coding: utf-8 -*-
"""Tests de l'onglet Projets : détection, commandes proposées, démarrage et
arrêt d'un vrai petit serveur, journal, état Git (dépôt nu comme remote),
fichiers .env vers un coffre temporaire, routes HTTP."""
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aide import ConfigTemporaire, ServeurTest  # noqa: E402

import coffre  # noqa: E402
import config  # noqa: E402
import projets  # noqa: E402
import systeme  # noqa: E402

LINUX = sys.platform.startswith("linux")
# Contenu réel de /proc/<pid>/stat (Ubuntu) : champ 22 (starttime) = 8231457.
# Le nom contient une espace et une parenthèse : il faut lire après la dernière « ) ».
STAT = ("48213 (node (dev) x) S 48200 48213 48213 0 -1 4194304 12000 0 0 0 150 30 0 0 20 0 11 0 "
        "8231457 1100000000 25000 18446744073709551615 1 1 0 0 0 0 0 4096 134234626 0 0 0 17 3 0 0 0 0 0\n")

SERVEUR = """import http.server, sys
port = int(sys.argv[1])
print("pret sur le port", port, flush=True)
print("\\x1b[32mcouleur\\x1b[0m", flush=True)
http.server.HTTPServer(("127.0.0.1", port), http.server.SimpleHTTPRequestHandler).serve_forever()
"""


def ecrire(chemin, contenu):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)


def port_libre():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def attendre(condition, delai=20):
    fin = time.time() + delai
    while time.time() < fin:
        if condition():
            return True
        time.sleep(0.2)
    return False


class Base(unittest.TestCase):
    def setUp(self):
        self.racine = tempfile.mkdtemp(prefix="mo-projets-")
        self.cfg = ConfigTemporaire({"dossiers_projets": [self.racine]})
        self.cfg.__enter__()
        projets._popens.clear()
        projets._fins.clear()

    def tearDown(self):
        # Rien ne doit rester en marche après un test.
        d = projets._donnees()
        for cle in list(d["lances"]):
            try:
                projets.arreter(*cle.split("/", 1))
            except Exception:  # noqa: BLE001
                pass
        self.cfg.__exit__(None, None, None)
        shutil.rmtree(self.racine, ignore_errors=True)

    def projet(self, nom, fichiers):
        dossier = os.path.join(self.racine, nom)
        os.makedirs(dossier, exist_ok=True)
        for rel, contenu in fichiers.items():
            ecrire(os.path.join(dossier, rel), contenu)
        return dossier


class TestDetection(Base):
    def test_types_et_liste(self):
        self.projet("vitrine", {"package.json": json.dumps({"dependencies": {"react": "1"}, "devDependencies": {"vite": "5"}}),
                                "pnpm-lock.yaml": ""})
        self.projet("site", {"manage.py": "", "requirements.txt": "django\n"})
        self.projet("addons", {"mon_module/__manifest__.py": "{}"})
        self.projet("infra", {"compose.yaml": "services:\n  web:\n    ports:\n      - \"8081:80\"\n"})
        self.projet("boutique", {"composer.json": "{}", "artisan": ""})
        self.projet("photos", {"vacances.txt": ""})
        r = projets.lister()
        par_nom = {p["nom"]: p for p in r["projets"]}
        self.assertNotIn("photos", par_nom, "un dossier ordinaire n'est pas un projet")
        self.assertEqual(par_nom["vitrine"]["types"][:3], ["React", "Vite", "Node"])
        self.assertEqual(par_nom["vitrine"]["icone"], "⚛️")
        self.assertEqual(par_nom["site"]["types"][0], "Django")
        self.assertEqual(par_nom["addons"]["types"], ["Odoo"])
        self.assertEqual(par_nom["infra"]["types"], ["Docker"])
        self.assertEqual(par_nom["boutique"]["types"][:2], ["Laravel", "PHP"])

    def test_commandes_proposees(self):
        node = self.projet("app", {"package.json": json.dumps({"scripts": {
            "dev": "vite", "build": "vite build", "predev": "x", "evil & calc": "x", "storybook": "storybook dev"}}),
            "yarn.lock": ""})
        cmds = {c["nom"]: c for c in projets.commandes_proposees(node)}
        self.assertEqual(cmds["yarn dev"]["commande"], "yarn dev")
        self.assertEqual(cmds["yarn dev"]["port"], 5173)
        self.assertEqual(cmds["yarn dev"]["url"], "http://localhost:5173")
        self.assertIsNone(cmds["yarn build"]["port"])
        self.assertEqual(cmds["yarn storybook"]["port"], 6006)
        self.assertNotIn("yarn predev", cmds, "les scripts pre/post ne sont pas proposés")
        self.assertFalse(any("calc" in c["commande"] for c in cmds.values()), "nom de script douteux refusé")
        self.assertEqual(list(cmds)[0], "yarn dev", "dev passe en premier")

        npm = self.projet("api", {"package.json": json.dumps({"scripts": {"start": "nest start"}})})
        self.assertEqual(projets.commandes_proposees(npm)[0]["commande"], "npm run start")

        dj = self.projet("dj", {"manage.py": "", ".venv/Scripts/python.exe": "", ".venv/bin/python": ""})
        c = projets.commandes_proposees(dj)[0]
        venv = ".venv\\Scripts\\python.exe" if systeme.WINDOWS else ".venv/bin/python"
        self.assertEqual((c["commande"], c["port"]), (f"{venv} manage.py runserver", 8000))

        infra = self.projet("infra", {"docker-compose.yml": "services:\n  w:\n    ports:\n      - 8081:80\n"})
        c = projets.commandes_proposees(infra)[0]
        self.assertEqual((c["commande"], c["port"]), ("docker compose up", 8081))

        odoo = self.projet("odoo", {"odoo-bin": "", "odoo.conf": ""})
        python = "python" if systeme.WINDOWS else "python3"
        self.assertEqual(projets.commandes_proposees(odoo)[0]["commande"], f"{python} odoo-bin -c odoo.conf")

    def test_commandes_proposees_linux(self):
        with mock.patch.object(systeme, "WINDOWS", False):
            dj = self.projet("dj", {"manage.py": "", "venv/bin/python": "", "venv/Scripts/python.exe": ""})
            self.assertEqual(projets.commandes_proposees(dj)[0]["commande"], "venv/bin/python manage.py runserver")
            seul = self.projet("seul", {"manage.py": ""})
            self.assertEqual(projets.commandes_proposees(seul)[0]["commande"], "python3 manage.py runserver",
                             "Ubuntu n'a pas de commande « python »")
            mvn = self.projet("mvn", {"pom.xml": "<artifactId>spring-boot</artifactId>", "mvnw": "", "mvnw.cmd": ""})
            self.assertEqual(projets.commandes_proposees(mvn)[0]["commande"], "./mvnw spring-boot:run")
            gradle = self.projet("gradle", {"build.gradle": "", "gradlew": "", "gradlew.bat": ""})
            self.assertEqual(projets.commandes_proposees(gradle)[0]["commande"], "./gradlew bootRun")
            sans = self.projet("sans", {"build.gradle": "", "gradlew.bat": ""})
            self.assertEqual(projets.commandes_proposees(sans)[0]["commande"], "gradle bootRun")
            rails = self.projet("rails", {"Gemfile": "", "bin/rails": ""})
            self.assertEqual(projets.commandes_proposees(rails)[0]["commande"], "ruby bin/rails server")
        with mock.patch.object(systeme, "WINDOWS", True):
            self.assertEqual(projets.commandes_proposees(mvn)[0]["commande"], "mvnw.cmd spring-boot:run")
            self.assertEqual(projets.commandes_proposees(gradle)[0]["commande"], "gradlew.bat bootRun")
            self.assertEqual(projets.commandes_proposees(rails)[0]["commande"], "ruby bin\\rails server")

    def test_ajout_manuel_et_masque(self):
        ailleurs = tempfile.mkdtemp(prefix="mo-ailleurs-")
        try:
            projets.ajouter({"chemin": ailleurs})
            p = next(p for p in projets.lister()["projets"] if p["chemin"] == os.path.normpath(ailleurs))
            self.assertTrue(p["manuel"])
            projets.masquer({"projet": p["id"]})
            p = next(p for p in projets.lister()["projets"] if p["id"] == p["id"])
            self.assertTrue(p["masque"])
            projets.retirer({"projet": p["id"]})
            self.assertFalse(any(x["id"] == p["id"] for x in projets.lister()["projets"]))
            with self.assertRaises(projets.ErreurProjets):
                projets.ajouter({"chemin": os.path.join(ailleurs, "n-existe-pas")})
        finally:
            shutil.rmtree(ailleurs, ignore_errors=True)


class TestCommandes(Base):
    def preparer(self):
        dossier = self.projet("mini", {"serveur.py": SERVEUR, "requirements.txt": ""})
        pid = projets.identifiant(dossier)
        self.port = port_libre()
        r = projets.enregistrer_commandes({"projet": pid, "commandes": [
            {"nom": "Serveur", "commande": f'"{sys.executable}" -u serveur.py {self.port}', "port": self.port}]})
        return pid, r["commandes"][0]["id"]

    def test_enregistrement_valide(self):
        dossier = self.projet("x", {"package.json": "{}"})
        pid = projets.identifiant(dossier)
        r = projets.enregistrer_commandes({"projet": pid, "commandes": [{"nom": "Dev", "commande": "npm run dev", "port": "3000"}]})
        c = r["commandes"][0]
        self.assertEqual((c["port"], c["url"], c["etat"]["etat"]), (3000, "http://localhost:3000", "arrete"))
        for mauvais in ({"nom": "", "commande": "a"}, {"nom": "a", "commande": "a\nb"}, {"nom": "a", "commande": "a", "port": 70000},
                        {"nom": "a", "commande": "a", "url": "javascript:alert(1)"}):
            with self.assertRaises(projets.ErreurProjets, msg=str(mauvais)):
                projets.enregistrer_commandes({"projet": pid, "commandes": [mauvais]})
        with self.assertRaises(projets.ErreurProjets):
            projets.enregistrer_commandes({"projet": "0123456789", "commandes": []})

    def test_demarrer_journal_arreter(self):
        pid, cid = self.preparer()
        r = projets.demarrer(pid, cid)
        self.assertIn(r["etat"], ("demarrage", "marche"))
        self.assertTrue(attendre(lambda: projets.port_repond(self.port)), "le petit serveur doit répondre")
        s = next(x for x in projets.serveurs() if x["id"] == cid)
        self.assertEqual((s["etat"], s["projet"], s["port"]), ("marche", "mini", self.port))
        with self.assertRaises(projets.ErreurProjets, msg="pas de second lancement"):
            projets.demarrer(pid, cid)

        self.assertTrue(attendre(lambda: any("pret sur le port" in l for l in projets.lire_journal(pid, cid)["lignes"])))
        j = projets.lire_journal(pid, cid)
        self.assertIn("couleur", j["lignes"])
        self.assertFalse(any("\x1b" in l for l in j["lignes"]), "les codes couleur sont retirés")
        self.assertTrue(j["fichier"].startswith(os.path.join(config.DONNEES, "journaux")))
        self.assertTrue(os.path.basename(j["fichier"]).startswith("mini-"))

        # Après un redémarrage de « Mes outils » : le PID mémorisé suffit.
        gardes = dict(projets._popens)
        projets._popens.clear()
        self.assertEqual(projets.serveurs()[0]["etat"], "marche")
        projets.action_commande(pid, cid, "arreter")
        for p in gardes.values():
            p.wait(timeout=10)
        self.assertTrue(attendre(lambda: not projets.port_repond(self.port), 10), "tout l'arbre est arrêté")
        self.assertEqual(projets.serveurs()[0]["etat"], "arrete")
        self.assertEqual(projets._donnees()["lances"], {})
        self.assertIn("Arrêté par Mes outils", projets.lire_journal(pid, cid)["lignes"][-1])
        with self.assertRaises(projets.ErreurProjets):
            projets.arreter(pid, cid)

    def test_port_deja_pris(self):
        pid, cid = self.preparer()
        with socket.socket() as s:
            s.bind(("127.0.0.1", self.port))
            s.listen()
            self.assertEqual(projets.serveurs()[0]["etat"], "occupe")
            with self.assertRaisesRegex(projets.ErreurProjets, "déjà utilisé"):
                projets.demarrer(pid, cid)

    def test_refus_de_tuer_un_processus_etranger(self):
        pid, cid = self.preparer()
        etranger = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"],
                                    creationflags=projets.CREATE_NO_WINDOW)
        try:
            with self.assertRaises(projets.ErreurProjets):
                projets._tuer_arbre(etranger.pid)
            with self.assertRaises(projets.ErreurProjets):
                projets._tuer_arbre(os.getpid())
            # Entrée falsifiée : bon PID, mauvaise heure de création (PID réutilisé).
            d = projets._donnees()
            d["lances"][f"{pid}/{cid}"] = {"pid": etranger.pid, "cree": 12345, "journal": ""}
            projets._ecrire(d)
            with self.assertRaises(projets.ErreurProjets):
                projets.arreter(pid, cid)
            with self.assertRaises(projets.ErreurProjets):
                projets._tuer_arbre(etranger.pid)
            self.assertIsNone(etranger.poll(), "le processus étranger est toujours vivant")
        finally:
            etranger.kill()
            etranger.wait()


class TestLinux(Base):
    """Branches Linux, simulées (passent aussi sous Windows)."""

    def test_debut_stat(self):
        self.assertEqual(projets.debut_stat_linux(STAT), 8231457)
        self.assertIsNone(projets.debut_stat_linux(STAT.replace(") S ", ") Z ")), "zombie : terminé")
        self.assertIsNone(projets.debut_stat_linux(""))
        self.assertIsNone(projets.debut_stat_linux(None))
        self.assertIsNone(projets.debut_stat_linux("12 (x) S 1 2"), "texte tronqué")
        with mock.patch.object(systeme, "WINDOWS", False), \
                mock.patch.object(projets, "_lire_stat_linux", return_value=STAT) as lire:
            self.assertEqual(projets.heure_creation(48213), 8231457)
            lire.assert_called_once_with(48213)
            self.assertIsNone(projets.heure_creation("abc"))
            self.assertIsNone(projets.heure_creation(1), "jamais le PID 1")
        with mock.patch.object(systeme, "WINDOWS", False), \
                mock.patch.object(projets, "_lire_stat_linux", return_value=None):
            self.assertIsNone(projets.heure_creation(48213), "processus disparu")

    def test_demarrer_et_arreter(self):
        dossier = self.projet("web", {"package.json": "{}"})
        pid = projets.identifiant(dossier)
        cid = projets.enregistrer_commandes({"projet": pid, "commandes": [
            {"nom": "Dev", "commande": "source .env && npm run dev"}]})["commandes"][0]["id"]
        faux = mock.Mock(pid=48213)
        with mock.patch.object(systeme, "WINDOWS", False), \
                mock.patch.object(projets.shutil, "which", return_value="/usr/bin/bash"), \
                mock.patch.object(projets.subprocess, "Popen", return_value=faux) as popen, \
                mock.patch.object(projets, "heure_creation", return_value=8231457):
            r = projets.demarrer(pid, cid)
            self.assertEqual((r["etat"], r["pid"]), ("marche", 48213))
            args, kw = popen.call_args
            self.assertEqual(args[0], ["/usr/bin/bash", "-c", "source .env && npm run dev"],
                             "bash -c avec la commande telle quelle")
            self.assertTrue(kw["start_new_session"], "nouvelle session : groupe = PID")
            self.assertNotIn("creationflags", kw, "jamais de drapeaux Windows sous Linux")
            self.assertEqual(kw["cwd"], dossier)
            self.assertEqual(projets._donnees()["lances"][f"{pid}/{cid}"]["cree"], 8231457)

            # Arrêt : le groupe, puis l'arbre par systeme.arreter_processus.
            faux.wait.return_value = -15
            with mock.patch.object(projets.os, "getpgid", create=True, return_value=48213), \
                    mock.patch.object(projets.os, "killpg", create=True) as killpg, \
                    mock.patch.object(systeme, "arreter_processus", return_value=(True, "")) as arret:
                projets.arreter(pid, cid)
            arret.assert_called_once_with(48213, arbre=True, delai=5.0)
            self.assertEqual([c.args for c in killpg.call_args_list],
                             [(48213, projets.signal.SIGTERM), (48213, getattr(projets.signal, "SIGKILL", 9))])
            self.assertEqual(projets._donnees()["lances"], {})

    def test_sh_sans_bash(self):
        with mock.patch.object(projets.shutil, "which", return_value=None):
            self.assertEqual(projets._shell_linux(), "/bin/sh")

    def test_jamais_un_processus_etranger(self):
        with mock.patch.object(systeme, "WINDOWS", False), \
                mock.patch.object(projets, "heure_creation", return_value=8231457), \
                mock.patch.object(projets.os, "killpg", create=True) as killpg, \
                mock.patch.object(systeme, "arreter_processus") as arret:
            with self.assertRaises(projets.ErreurProjets):
                projets._tuer_arbre(48213)
            d = projets._donnees()
            d["lances"]["0123456789/x"] = {"pid": 48213, "cree": 111, "journal": ""}
            projets._ecrire(d)
            with self.assertRaises(projets.ErreurProjets, msg="PID réutilisé : autre heure de création"):
                projets._tuer_arbre(48213)
        arret.assert_not_called()
        killpg.assert_not_called()
        d = projets._donnees()
        d["lances"] = {}
        projets._ecrire(d)

    def test_ouvrir(self):
        dossier = self.projet("app", {"package.json": "{}"})
        pid = projets.identifiant(dossier)
        with mock.patch.object(systeme, "WINDOWS", False), \
                mock.patch.object(systeme, "ouvrir_terminal", return_value=True) as terminal, \
                mock.patch.object(systeme, "ouvrir") as ouvrir, \
                mock.patch.object(projets.subprocess, "Popen") as popen:
            projets.ouvrir_terminal({"projet": pid})
            projets.ouvrir_dossier({"projet": pid})
            self.assertEqual(projets.lister()["terminal"], "Terminal")
        terminal.assert_called_once_with(dossier=dossier)
        ouvrir.assert_called_once_with(dossier)
        popen.assert_not_called()
        with mock.patch.object(systeme, "WINDOWS", False), \
                mock.patch.object(systeme, "ouvrir_terminal", return_value=False), \
                self.assertRaisesRegex(projets.ErreurProjets, "Aucun terminal"):
            projets.ouvrir_terminal({"projet": pid})

    @unittest.skipUnless(LINUX, "vrai Linux seulement")
    def test_heure_creation_reelle(self):
        self.assertIsInstance(projets.heure_creation(os.getpid()), int)
        p = subprocess.Popen([sys.executable, "-c", "pass"])
        p.wait()
        self.assertIsNone(projets.heure_creation(p.pid), "processus terminé")


class TestGit(Base):
    def git(self, dossier, *args):
        env = dict(os.environ, GIT_AUTHOR_NAME="Test", GIT_AUTHOR_EMAIL="test@example.invalid",
                   GIT_COMMITTER_NAME="Test", GIT_COMMITTER_EMAIL="test@example.invalid")
        subprocess.run(["git", *args], cwd=dossier, env=env, check=True, capture_output=True,
                       creationflags=projets.CREATE_NO_WINDOW)

    def test_avance_retard_modifies(self):
        nu = os.path.join(self.racine, "..", os.path.basename(self.racine) + "-nu.git")
        nu = os.path.normpath(nu)
        autre = tempfile.mkdtemp(prefix="mo-autre-")
        try:
            self.git(self.racine, "init", "-q", "--bare", "-b", "main", nu)
            a = os.path.join(self.racine, "a")
            self.git(self.racine, "clone", "-q", nu, a)
            ecrire(os.path.join(a, "lisez.txt"), "1")
            self.git(a, "add", ".")
            self.git(a, "commit", "-q", "-m", "un")
            self.git(a, "push", "-q", "-u", "origin", "main")
            b = os.path.join(autre, "b")
            self.git(autre, "clone", "-q", nu, b)
            ecrire(os.path.join(b, "autre.txt"), "2")
            self.git(b, "add", ".")
            self.git(b, "commit", "-q", "-m", "deux")
            self.git(b, "push", "-q")
            ecrire(os.path.join(a, "local.txt"), "3")
            self.git(a, "add", ".")
            self.git(a, "commit", "-q", "-m", "trois")
            ecrire(os.path.join(a, "lisez.txt"), "modifié")
            ecrire(os.path.join(a, "nouveau.txt"), "?")

            pid = projets.identifiant(a)
            e = projets.etats_git()["git"][pid]
            self.assertEqual((e["branche"], e["amont"], e["avance"], e["retard"]), ("main", "origin/main", 1, 0))
            self.assertEqual((e["modifies"], e["non_suivis"]), (1, 1))
            e = projets.git_fetch({"projet": pid})["git"]
            self.assertEqual((e["avance"], e["retard"]), (1, 1), "après fetch, le commit distant est vu")
            self.assertNotIn("erreur_fetch", e)
            r = projets.tout_verifier()
            self.assertEqual(r["erreurs"], 0)
            self.assertEqual(r["git"][pid]["retard"], 1)
        finally:
            shutil.rmtree(autre, ignore_errors=True)
            shutil.rmtree(nu, ignore_errors=True)

    def test_analyse_status(self):
        r = projets.analyser_status("# branch.oid (initial)\n# branch.head (detached)\nu UU x\n")
        self.assertTrue(r["sans_commit"] and r["detache"])
        self.assertEqual((r["branche"], r["conflits"]), (None, 1))

    def test_fetch_sans_remote_ne_bloque_pas(self):
        dossier = self.projet("seul", {})
        self.git(dossier, "init", "-q")
        e = projets.git_fetch({"projet": projets.identifiant(dossier)})["git"]
        self.assertIsNone(e["amont"])


class TestEnv(Base):
    def setUp(self):
        super().setUp()
        self.fichier_coffre = os.path.join(self.cfg.dossier, "coffre.json")
        self.coffre = coffre.Coffre(self.fichier_coffre)
        self.patch = mock.patch.object(projets, "_le_coffre", lambda: self.coffre)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        super().tearDown()

    def test_sauvegarder_restaurer(self):
        dossier = self.projet("app", {"package.json": "{}", ".env": "CLE=secret\r\nB=é\n",
                                      ".env.example": "CLE=", "backend/.env.local": "X=1"})
        pid = projets.identifiant(dossier)
        self.assertEqual(projets.fichiers_env(dossier), [".env", "backend/.env.local"])
        with self.assertRaisesRegex(projets.ErreurProjets, "Ouvrez d'abord le coffre"):
            projets.env_sauvegarder({"projet": pid})

        self.coffre.creer("phrase-de-test-assez-longue")
        r = projets.env_sauvegarder({"projet": pid})
        self.assertEqual(r["sauvegardes"], [".env", "backend/.env.local"])
        projets.env_sauvegarder({"projet": pid})
        entrees = self.coffre.lister()
        self.assertEqual(len(entrees), 2, "une seconde sauvegarde remplace la première")
        self.assertTrue(all(e["categorie"] == "env" for e in entrees))
        with open(self.fichier_coffre, encoding="utf-8") as f:
            self.assertNotIn("secret", f.read(), "le coffre est chiffré")

        ecrire(os.path.join(dossier, ".env"), "CASSÉ")
        r = projets.env_restaurer({"projet": pid, "fichier": ".env"})
        self.assertTrue(r["bak"])
        with open(os.path.join(dossier, ".env"), "rb") as f:
            self.assertEqual(f.read(), "CLE=secret\r\nB=é\n".encode("utf-8"), "contenu identique à l'octet près")
        with open(os.path.join(dossier, ".env.bak"), encoding="utf-8") as f:
            self.assertEqual(f.read(), "CASSÉ")

        os.remove(os.path.join(dossier, "backend", ".env.local"))
        liste = {f["fichier"]: f for f in projets.env_liste({"projet": pid})["fichiers"]}
        self.assertFalse(liste["backend/.env.local"]["existe"])
        self.assertTrue(liste["backend/.env.local"]["sauvegarde"])
        projets.env_restaurer({"projet": pid, "fichier": "backend/.env.local"})
        self.assertTrue(os.path.isfile(os.path.join(dossier, "backend", ".env.local")))

        for mauvais in ("../.env", "a/b/.env", "C:/x/.env", "config.py", ".env/../x"):
            with self.assertRaises(projets.ErreurProjets, msg=mauvais):
                projets.env_restaurer({"projet": pid, "fichier": mauvais})


class TestRoutes(ServeurTest):
    def test_routes(self):
        racine = tempfile.mkdtemp(prefix="mo-routes-")
        try:
            os.makedirs(os.path.join(racine, "web"))
            ecrire(os.path.join(racine, "web", "package.json"), json.dumps({"scripts": {"dev": "vite"}}))
            with ConfigTemporaire({"dossiers_projets": [racine]}):
                statut, r = self.post("/api/projets/liste", {})
                self.assertEqual(statut, 200)
                p = r["projets"][0]
                self.assertEqual((p["nom"], p["proposees"][0]["commande"]), ("web", "npm run dev"))
                statut, r = self.post("/api/projets/commandes/enregistrer",
                                      {"projet": p["id"], "commandes": [p["proposees"][0]]})
                self.assertEqual((statut, r["commandes"][0]["etat"]["etat"]), (200, "arrete"))
                statut, r = self.post("/api/projets/etats", {})
                self.assertEqual((statut, r["serveurs"][0]["nom"]), (200, "npm dev"))
                statut, r = self.post("/api/projets/commande", {"projet": p["id"], "commande": "inconnue", "action": "demarrer"})
                self.assertEqual(statut, 400)
                statut, r = self.post("/api/projets/commande", {"projet": p["id"], "commande": p["proposees"][0]["id"], "action": "arreter"})
                self.assertEqual(statut, 400, "rien à arrêter")
                statut, r = self.post("/api/projets/ouvrir/dossier", {"projet": "../../x"})
                self.assertEqual(statut, 400)
                statut, r = self.post("/api/projets/journal", {"projet": p["id"], "commande": p["proposees"][0]["id"]})
                self.assertEqual((statut, r["lignes"]), (200, []))
                statut, r = self.post("/api/projets/git/etats", {})
                self.assertEqual((statut, r["git"]), (200, {}))
                statut, _ = self.post("/api/projets/liste", {}, entete=False)
                self.assertEqual(statut, 403)
        finally:
            shutil.rmtree(racine, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
