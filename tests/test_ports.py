# -*- coding: utf-8 -*-
"""Tests de l'onglet « Ports » : lecture de netstat et tasklist (sorties
simulées), refus des arrêts dangereux, arrêt réel d'un petit programme
lancé par le test, et routes HTTP."""
import os
import socket
import subprocess
import sys
import time
import unittest
from unittest import mock

from aide import ServeurTest

import ports  # noqa: E402
import systeme  # noqa: E402

LINUX = sys.platform.startswith("linux")

# Sorties réelles de « ss -H -ltnp » et « ss -H -lunp » sur Ubuntu 24.04, sans
# droits root : les services des autres utilisateurs n'ont pas de champ users.
SS_TCP = """LISTEN 0      4096       127.0.0.54:53         0.0.0.0:*
LISTEN 0      4096    127.0.0.53%lo:53         0.0.0.0:*
LISTEN 0      4096        127.0.0.1:631        0.0.0.0:*
LISTEN 0      511           0.0.0.0:3000       0.0.0.0:*    users:(("node",pid=48213,fd=22))
LISTEN 0      244         127.0.0.1:5432       0.0.0.0:*
LISTEN 0      128         127.0.0.1:8000       0.0.0.0:*    users:(("python3",pid=50110,fd=5),("python3",pid=50101,fd=5))
LISTEN 0      4096            [::1]:631           [::]:*
LISTEN 0      511                 *:5173             *:*    users:(("node",pid=48300,fd=30))
LISTEN 0      4096                *:22               *:*
LISTEN 0      5    [fe80::1]%enp0s3:9999          [::]:*    users:(("Web Content",pid=6001,fd=3))
LISTEN 0      128         127.0.0.1:8765       0.0.0.0:*    users:(("mes-outils",pid=7000,fd=3))
LISTEN 0      128         127.0.0.1:8765       0.0.0.0:*    users:(("mes-outils",pid=7000,fd=3))
"""
SS_UDP = """UNCONN 0      0        127.0.0.54:53         0.0.0.0:*
UNCONN 0      0           0.0.0.0:5353       0.0.0.0:*    users:(("chrome",pid=7100,fd=120))
UNCONN 0      0              [::]:5353          [::]:*    users:(("chrome",pid=7100,fd=121))
"""
# /proc/<pid>/… simulés : comm, status (extrait) et cmdline (séparée par \\0).
PROC = {
    48213: ("node\n", "Name:\tnode\nUid:\t1000\t1000\t1000\t1000\nVmRSS:\t   95432 kB\n", "node\0server.js\0"),
    50101: ("python3\n", "Uid:\t1000\t1000\t1000\t1000\nVmRSS:\t   64000 kB\n", "python3\0-m\0http.server\0"),
    48300: ("node\n", "Uid:\t1000\t1000\t1000\t1000\nVmRSS:\t  120000 kB\n", "node\0vite\0"),
    6001: ("Web Content\n", "Uid:\t1000\t1000\t1000\t1000\nVmRSS:\t  210000 kB\n", ""),
    7000: ("mes-outils\n", "Uid:\t1000\t1000\t1000\t1000\nVmRSS:\t   40000 kB\n", ""),
    7100: ("chrome\n", "Uid:\t1000\t1000\t1000\t1000\nVmRSS:\t  300000 kB\n", "chrome\0"),
}


def faux_proc(pid, fichier):
    """Remplace ports._lire_proc : lit PROC au lieu de /proc."""
    entree = PROC.get(int(pid))
    if not entree:
        return None
    return dict(zip(("comm", "status", "cmdline"), entree)).get(fichier)

NETSTAT = """
Connexions actives

  Proto  Adresse locale         Adresse distante       État
  TCP    0.0.0.0:135            0.0.0.0:0              LISTENING       1260
  TCP    0.0.0.0:3000           0.0.0.0:0              LISTENING       5100
  TCP    127.0.0.1:5432         0.0.0.0:0              LISTENING       6200
  TCP    127.0.0.1:5432         0.0.0.0:0              LISTENING       6200
  TCP    127.0.0.1:50123        127.0.0.1:5432         ESTABLISHED     5100
  TCP    192.168.1.20:49800     93.184.216.34:443      TIME_WAIT       0
  TCP    0.0.0.0:445            0.0.0.0:0              LISTENING       4
  TCP    0.0.0.0:7000           0.0.0.0:0              ABHÖREN         7100
  TCP    [::]:3000              [::]:0                 LISTENING       5100
  TCP    [::1]:8069             [::]:0                 LISTENING       7200
  TCP    [fe80::1%12]:9999      [::]:0                 LISTENING       7200
  UDP    0.0.0.0:5353           *:*                                    8100
  UDP    [::]:5353              *:*                                    8100
"""

TASKLIST = (
    '"System Idle Process","0","Services","0","8 Ko"\r\n'
    '"System","4","Services","0","136 Ko"\r\n'
    '"svchost.exe","1260","Services","0","18\xa0280 Ko"\r\n'
    '"node.exe","5100","Console","1","95 432 K"\r\n'
    '"postgres.exe","6200","Services","0","12 000 Ko"\r\n'
    '"python.exe","7200","Console","1","64 000 Ko"\r\n'
    '"java.exe","7100","Console","1","N/A"\r\n'
    '"chrome.exe","8100","Console","1","210 000 Ko"\r\n'
)


class TestLecture(unittest.TestCase):
    def test_netstat_tcp(self):
        e = ports.lire_netstat(NETSTAT)
        cles = [(x["adresse"], x["port"], x["pid"]) for x in e]
        self.assertIn(("0.0.0.0", 3000, 5100), cles)
        self.assertIn(("::", 3000, 5100), cles, "IPv6 sans crochets")
        self.assertIn(("::1", 8069, 7200), cles)
        self.assertIn(("fe80::1", 9999, 7200), cles, "l'indice d'interface %12 est retiré")
        self.assertIn(("0.0.0.0", 7000, 7100), cles, "état dans une autre langue : reconnu par l'adresse distante")
        self.assertEqual(cles.count(("127.0.0.1", 5432, 6200)), 1, "doublon retiré")
        self.assertNotIn(50123, [x["port"] for x in e], "connexion établie ignorée")
        self.assertNotIn(49800, [x["port"] for x in e], "TIME_WAIT ignoré")
        self.assertFalse([x for x in e if x["proto"] == "UDP"], "UDP seulement sur demande")

    def test_netstat_udp(self):
        udp = [x for x in ports.lire_netstat(NETSTAT, udp=True) if x["proto"] == "UDP"]
        self.assertEqual([(x["adresse"], x["port"], x["pid"]) for x in udp], [("0.0.0.0", 5353, 8100), ("::", 5353, 8100)])

    def test_tasklist(self):
        p = ports.lire_tasklist(TASKLIST)
        self.assertEqual(p[1260], {"nom": "svchost.exe", "memoire_ko": 18280}, "espace insécable dans le nombre")
        self.assertEqual(p[5100]["memoire_ko"], 95432)
        self.assertIsNone(p[7100]["memoire_ko"])
        self.assertEqual(ports.lire_tasklist("Erreur : rien\r\n"), {})

    def test_commandes(self):
        self.assertEqual(ports.lire_commandes('{"ProcessId":5,"CommandLine":"node app.js"}'), {5: "node app.js"})
        self.assertEqual(ports.lire_commandes('[{"ProcessId":5,"CommandLine":null},{"ProcessId":6,"CommandLine":"x"}]'),
                         {5: "", 6: "x"})
        self.assertEqual(ports.lire_commandes(""), {})
        self.assertEqual(ports.lire_commandes("pas du json"), {})

    def test_separer_adresse(self):
        self.assertEqual(ports.separer_adresse("[::1]:5432"), ("::1", 5432))
        self.assertEqual(ports.separer_adresse("*:*"), ("*", None))
        self.assertEqual(ports.separer_adresse("rien"), (None, None))


class TestListe(unittest.TestCase):
    def setUp(self):
        ports.oublier_cache()
        ports._commandes.clear()

    def tearDown(self):
        ports.oublier_cache()
        ports._commandes.clear()

    def _simuler(self):
        def executer(commande, delai=15):
            return NETSTAT if commande[0] == "netstat" else TASKLIST
        return [mock.patch.object(systeme, "WINDOWS", True),  # sorties de Windows, même sous Linux
                mock.patch.object(ports, "_executer", side_effect=executer),
                mock.patch.object(ports, "commandes", return_value={5100: "node server.js", 7200: "python -m http.server"}),
                mock.patch.object(ports, "nos_pids", return_value={7200, 1})]

    def test_liste_enrichie(self):
        patchs = self._simuler()
        for p in patchs:
            p.start()
        try:
            liste = ports.lister_ports(forcer=True)
            appels_netstat = ports._executer.call_count
            ports.lister_ports()
            self.assertEqual(ports._executer.call_count, appels_netstat, "deuxième lecture servie par le cache")
        finally:
            for p in patchs:
                p.stop()
        par_port = {(x["port"], x["adresse"]): x for x in liste}
        node = par_port[(3000, "0.0.0.0")]
        self.assertEqual((node["nom"], node["memoire_ko"], node["commande"]), ("node.exe", 95432, "node server.js"))
        self.assertEqual(node["dev"], "Node / React")
        self.assertTrue(node["web"])
        self.assertFalse(node["protege"])
        self.assertFalse(par_port[(5432, "127.0.0.1")]["web"], "PostgreSQL n'est pas une page web")
        self.assertEqual(par_port[(5432, "127.0.0.1")]["dev"], "PostgreSQL")
        self.assertTrue(par_port[(135, "0.0.0.0")]["protege"], "svchost est protégé")
        self.assertTrue(par_port[(445, "0.0.0.0")]["protege"], "PID 4 est protégé")
        self.assertEqual(par_port[(445, "0.0.0.0")]["nom"], "System")
        self.assertTrue(par_port[(8069, "::1")]["soi"], "le processus de Mes outils est signalé")
        self.assertEqual([x["port"] for x in liste], sorted(x["port"] for x in liste), "liste triée par port")

    def test_qui_ecoute(self):
        patchs = self._simuler()
        for p in patchs:
            p.start()
        try:
            r = ports.qui_ecoute(3000)
            self.assertEqual((r["pid"], r["nom"]), (5100, "node.exe"))
            self.assertIsNone(ports.qui_ecoute(3999))
            self.assertIsNone(ports.qui_ecoute("abc"))
        finally:
            for p in patchs:
                p.stop()


class TestArretRefuse(unittest.TestCase):
    def _refus(self, pid, nom, actuel, motif, arbre=False):
        with mock.patch.object(ports, "processus_pid", return_value=actuel), \
                mock.patch.object(ports.subprocess, "run") as run, \
                self.assertRaisesRegex(ValueError, motif):
            ports.arreter({"pid": pid, "nom": nom, "arbre": arbre})
        run.assert_not_called()

    def test_pid_systeme(self):
        self._refus(0, "System Idle Process", {"nom": "System Idle Process"}, "système")
        self._refus(4, "System", {"nom": "System"}, "système")

    def test_programmes_proteges(self):
        for nom in ("svchost.exe", "csrss.exe", "lsass.exe", "explorer.exe", "MsMpEng.exe", "winlogon.exe", "dwm.exe"):
            self._refus(4321, nom, {"nom": nom}, "système")

    def test_mes_outils_lui_meme(self):
        self._refus(os.getpid(), "python.exe", {"nom": "python.exe"}, "Mes outils")
        self._refus(os.getppid(), "python.exe", {"nom": "python.exe"}, "Mes outils")

    def test_pid_reutilise(self):
        self._refus(4321, "node.exe", {"nom": "notepad.exe"}, "autre programme")
        self._refus(4321, "", {"nom": "node.exe"}, "autre programme")

    def test_processus_disparu(self):
        self._refus(4321, "node.exe", None, "n'existe plus")

    def test_arbre_qui_contient_mes_outils(self):
        with mock.patch.object(ports, "ancetres", return_value={os.getpid(), 4321}):
            self._refus(4321, "cmd.exe", {"nom": "cmd.exe"}, "arbre", arbre=True)

    def test_pid_invalide(self):
        for pid in (None, "abc", -3):
            with self.assertRaisesRegex(ValueError, "invalide"):
                ports.arreter({"pid": pid, "nom": "x"})

    @unittest.skipUnless(sys.platform == "win32", "taskkill : Windows seulement")
    def test_commande_taskkill(self):
        ok = subprocess.CompletedProcess([], 0, b"", b"")
        with mock.patch.object(ports, "processus_pid", return_value={"nom": "node.exe"}), \
                mock.patch.object(ports, "ancetres", return_value=set()), \
                mock.patch.object(ports.subprocess, "run", return_value=ok) as run:
            r = ports.arreter({"pid": 4321, "nom": "NODE.EXE", "arbre": True})
        self.assertEqual(r["nom"], "node.exe")
        self.assertEqual(run.call_args[0][0], ["taskkill", "/PID", "4321", "/F", "/T"])

    def test_ancetres_reels(self):
        chaine = ports.ancetres(os.getpid())
        self.assertIn(os.getpid(), chaine)
        self.assertIn(os.getppid(), chaine, "le parent fait partie des ancêtres")


class TestLinuxLecture(unittest.TestCase):
    """Lecture des sorties de ss et de /proc (testée aussi sous Windows)."""

    def test_ss_tcp(self):
        e = ports.lire_ss(SS_TCP)
        cles = [(x["adresse"], x["port"], x["pid"]) for x in e]
        self.assertIn(("0.0.0.0", 3000, 48213), cles)
        self.assertIn(("127.0.0.53", 53, None), cles, "l'interface %lo est retirée, PID inconnu sans root")
        self.assertIn(("::1", 631, None), cles, "IPv6 sans crochets")
        self.assertIn(("*", 5173, 48300), cles, "« * » : toutes les adresses")
        self.assertIn(("fe80::1", 9999, 6001), cles, "interface hors des crochets retirée")
        self.assertIn(("127.0.0.1", 8000, 50101), cles, "plusieurs processus : le plus petit PID (le parent)")
        self.assertEqual(cles.count(("127.0.0.1", 8765, 7000)), 1, "doublon retiré")
        web = next(x for x in e if x["port"] == 9999)
        self.assertEqual(web["nom_ss"], "Web Content", "nom avec une espace")
        self.assertTrue(all(x["proto"] == "TCP" for x in e))

    def test_ss_udp_et_netid(self):
        udp = ports.lire_ss(SS_UDP, "UDP")
        self.assertEqual([(x["proto"], x["adresse"], x["port"], x["pid"]) for x in udp],
                         [("UDP", "127.0.0.54", 53, None), ("UDP", "0.0.0.0", 5353, 7100), ("UDP", "::", 5353, 7100)])
        # « ss -H -ltunp » : une colonne Netid en plus.
        mixte = ports.lire_ss("udp UNCONN 0 0 0.0.0.0:5353 0.0.0.0:* users:((\"avahi\",pid=9,fd=1))\n"
                              "tcp LISTEN 0 511 0.0.0.0:3000 0.0.0.0:* users:((\"node\",pid=48213,fd=22))\n")
        self.assertEqual([(x["proto"], x["port"]) for x in mixte], [("UDP", 5353), ("TCP", 3000)])
        self.assertEqual(ports.lire_ss(""), [])
        self.assertEqual(ports.lire_ss("Cannot open netlink socket: Permission denied\n"), [])

    def test_status_et_info(self):
        self.assertEqual(ports.lire_status_linux(PROC[48213][1]), (95432, 1000))
        self.assertEqual(ports.lire_status_linux("Name:\tkthreadd\nUid:\t0\t0\t0\t0\n"), (None, 0),
                         "un fil du noyau n'a pas de VmRSS")
        self.assertEqual(ports.lire_status_linux(None), (None, None))
        with mock.patch.object(ports, "_lire_proc", side_effect=faux_proc):
            self.assertEqual(ports.info_linux(50101), {"nom": "python3", "memoire_ko": 64000,
                                                       "commande": "python3 -m http.server", "uid": 1000})
            self.assertIsNone(ports.info_linux(99999), "processus disparu")

    def test_separer_adresse_linux(self):
        self.assertEqual(ports.separer_adresse("127.0.0.53%lo:53"), ("127.0.0.53", 53))
        self.assertEqual(ports.separer_adresse("[fe80::1]%enp0s3:546"), ("fe80::1", 546))
        self.assertEqual(ports.separer_adresse("[fe80::1%12]:9999"), ("fe80::1", 9999), "forme Windows inchangée")

    def test_proteges_linux(self):
        for pid, nom, uid in ((1, "systemd", 0), (850, "systemd-resolve", 101), (2100, "Xwayland", 1000),
                              (2000, "gnome-shell", 1000), (900, "dbus-daemon", 102), (2300, "pipewire-pulse", 1000),
                              (120, "cupsd", 0), (5000, "kworker/u8:1", 0), (None, "Autre utilisateur", None)):
            self.assertTrue(ports.est_protege_linux(pid, nom, uid), f"{nom} ({pid}) doit être protégé")
        for pid, nom, uid in ((48213, "node", 1000), (120, "node", 1000), (900, "postgres", 0)):
            self.assertFalse(ports.est_protege_linux(pid, nom, uid), f"{nom} ({pid}) peut être arrêté")

    def test_web_linux(self):
        with mock.patch.object(systeme, "WINDOWS", False):
            self.assertTrue(ports.est_web(8001, "python3.12"), "python3.12 est un programme web")
            self.assertTrue(ports.est_web(9001, "php-fpm8.3"))
            self.assertFalse(ports.est_web(9002, "cupsd"))


class TestLinuxListe(unittest.TestCase):
    """lister_ports et arreter par la branche Linux (ss et /proc simulés)."""

    def setUp(self):
        ports.oublier_cache()
        self.patchs = [mock.patch.object(systeme, "WINDOWS", False),
                       mock.patch.object(ports, "_lire_proc", side_effect=faux_proc),
                       mock.patch.object(ports, "nos_pids", return_value={7000, 6999})]
        for p in self.patchs:
            p.start()

    def tearDown(self):
        for p in self.patchs:
            p.stop()
        ports.oublier_cache()

    def test_liste(self):
        appels = []

        def executer(commande, delai=15):
            appels.append(commande)
            return SS_UDP if commande[-1] == "-lunp" else SS_TCP

        with mock.patch.object(ports, "_executer", side_effect=executer):
            liste = ports.lister_ports(forcer=True)
            self.assertEqual(appels, [["ss", "-H", "-ltnp"]], "TCP seulement par défaut")
            avec_udp = ports.lister_ports(udp=True, forcer=True)
            self.assertEqual(appels[-1], ["ss", "-H", "-lunp"])
        par_port = {(x["port"], x["adresse"]): x for x in liste}
        node = par_port[(3000, "0.0.0.0")]
        self.assertEqual((node["nom"], node["memoire_ko"], node["commande"]), ("node", 95432, "node server.js"))
        self.assertTrue(node["web"] and not node["protege"] and not node["pid_inconnu"])
        self.assertEqual(node["dev"], "Node / React")
        py = par_port[(8000, "127.0.0.1")]
        self.assertEqual((py["pid"], py["nom"]), (50101, "python3"))
        self.assertTrue(py["web"], "python3 sur 8000 : page web")
        pg = par_port[(5432, "127.0.0.1")]
        self.assertEqual((pg["pid"], pg["nom"], pg["memoire_ko"], pg["commande"]),
                         (None, ports.NOM_INCONNU, None, ""), "programme d'un autre utilisateur, sans PID")
        self.assertTrue(pg["protege"] and pg["pid_inconnu"], "sans PID : jamais d'arrêt proposé")
        self.assertFalse(pg["web"])
        self.assertTrue(par_port[(8765, "127.0.0.1")]["soi"], "Mes outils se reconnaît")
        self.assertEqual(par_port[(9999, "fe80::1")]["nom"], "Web Content")
        self.assertEqual([x["port"] for x in liste], sorted(x["port"] for x in liste), "liste triée par port")
        self.assertTrue(any(x["proto"] == "UDP" and x["port"] == 5353 for x in avec_udp))
        with mock.patch.object(ports, "_executer", side_effect=executer):
            self.assertEqual(ports.qui_ecoute(5173)["pid"], 48300)

    def test_ss_absent(self):
        with mock.patch.object(ports, "_executer", side_effect=FileNotFoundError("ss")), \
                self.assertRaisesRegex(ValueError, "iproute2"):
            ports.lister_ports(forcer=True)

    def _refus(self, pid, nom, motif):
        with mock.patch.object(systeme, "arreter_processus") as arret, \
                self.assertRaisesRegex(ValueError, motif):
            ports.arreter({"pid": pid, "nom": nom})
        arret.assert_not_called()

    def test_arret_refuse(self):
        PROC[1] = ("systemd\n", "Uid:\t0\t0\t0\t0\n", "/sbin/init\0")
        PROC[150] = ("cupsd\n", "Uid:\t0\t0\t0\t0\n", "")
        PROC[2000] = ("gnome-shell\n", "Uid:\t1000\t1000\t1000\t1000\n", "")
        try:
            self._refus(1, "systemd", "système")
            self._refus(150, "cupsd", "système")
            self._refus(2000, "gnome-shell", "système")
            self._refus(7000, "mes-outils", "Mes outils")
            self._refus(48213, "python3", "autre programme")
            self._refus(99999, "node", "n'existe plus")
        finally:
            for pid in (1, 150, 2000):
                PROC.pop(pid, None)

    def test_arret(self):
        with mock.patch.object(ports, "ancetres", return_value={7000}), \
                mock.patch.object(systeme, "arreter_processus", return_value=(True, "")) as arret, \
                mock.patch.object(ports.subprocess, "run") as run:
            r = ports.arreter({"pid": 48213, "nom": "node", "arbre": True})
        self.assertEqual((r["pid"], r["nom"]), (48213, "node"))
        arret.assert_called_once_with(48213, arbre=True)
        run.assert_not_called()  # ni taskkill, ni autre commande
        with mock.patch.object(ports, "ancetres", return_value=set()), \
                mock.patch.object(systeme, "arreter_processus",
                                  return_value=(False, "Permission refusée : ce processus appartient à un autre utilisateur.")), \
                self.assertRaisesRegex(ValueError, "Arrêt impossible : Permission refusée"):
            ports.arreter({"pid": 48213, "nom": "node"})


@unittest.skipUnless(LINUX, "vrai Linux seulement")
class TestLinuxReel(unittest.TestCase):
    def test_se_voit_dans_ss(self):
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            s.listen()
            port = s.getsockname()[1]
            entree = next((e for e in ports.lister_ports(forcer=True) if e["port"] == port), None)
        self.assertIsNotNone(entree, "notre socket apparaît dans ss")
        self.assertEqual(entree["pid"], os.getpid())
        self.assertTrue(entree["soi"])
        self.assertTrue(entree["memoire_ko"], "mémoire lue dans /proc")
        self.assertIn(os.getppid(), ports.ancetres(os.getpid()))


class TestArretReel(unittest.TestCase):
    """Un petit serveur Python lancé par le test, trouvé dans la liste puis arrêté."""

    def test_arret_d_un_programme_de_test(self):
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        code = ("import socket,time\n"
                f"s=socket.socket();s.bind(('127.0.0.1',{port}));s.listen()\n"
                "time.sleep(120)\n")
        prog = subprocess.Popen([sys.executable, "-c", code], **systeme.options_sans_fenetre())
        try:
            entree = None
            for _ in range(50):
                entree = next((e for e in ports.lister_ports(forcer=True) if e["port"] == port), None)
                if entree:
                    break
                time.sleep(0.1)
            self.assertIsNotNone(entree, "le port du programme de test apparaît dans la liste")
            self.assertTrue(entree["nom"].lower().startswith("python"), entree["nom"])
            self.assertEqual(entree["adresse"], "127.0.0.1")
            self.assertEqual(ports.qui_ecoute(port)["pid"], entree["pid"])
            ports.arreter({"pid": entree["pid"], "nom": entree["nom"]})
            for _ in range(50):
                if not any(e["port"] == port for e in ports.lister_ports(forcer=True)):
                    break
                time.sleep(0.1)
            self.assertFalse(any(e["port"] == port for e in ports.lister_ports(forcer=True)),
                             "le port a disparu après l'arrêt")
            prog.wait(timeout=10)
        finally:
            if prog.poll() is None:
                if systeme.WINDOWS:
                    subprocess.run(["taskkill", "/PID", str(prog.pid), "/F", "/T"], capture_output=True,
                                   **systeme.options_sans_fenetre())
                else:
                    prog.kill()
                    prog.wait(timeout=10)


class TestRoutes(ServeurTest):
    def test_liste(self):
        t0 = time.monotonic()
        statut, r = self.post("/api/ports/liste", {"forcer": True})
        self.assertEqual(statut, 200)
        self.assertLess(time.monotonic() - t0, 8, "la liste reste rapide")
        self.assertTrue(any(e["soi"] for e in r["ports"]), "le serveur de test se voit lui-même")
        statut, r = self.post("/api/ports/liste", {"udp": True})
        self.assertEqual((statut, r["udp"]), (200, True))

    def test_arret_refuse(self):
        statut, r = self.post("/api/ports/arreter", {"pid": 4 if systeme.WINDOWS else 1, "nom": "System"})
        self.assertEqual(statut, 400)
        self.assertIn("système", r["erreur"])
        statut, r = self.post("/api/ports/arreter", {"pid": os.getpid(), "nom": "python.exe"})
        self.assertEqual(statut, 400)
        self.assertIn("Mes outils", r["erreur"])

    def test_chercher_et_ouvrir(self):
        with mock.patch.object(ports, "qui_ecoute", return_value=None):
            statut, r = self.post("/api/ports/chercher", {"port": 3999})
        self.assertEqual((statut, r["resultat"]), (200, None))
        self.assertEqual(self.post("/api/ports/chercher", {"port": 70000})[0], 400)
        with mock.patch.object(ports.webbrowser, "open") as ouvrir:
            statut, _ = self.post("/api/ports/ouvrir", {"port": 5173})
        self.assertEqual(statut, 200)
        ouvrir.assert_called_once_with("http://localhost:5173/")
        with mock.patch.object(ports.webbrowser, "open") as ouvrir:
            self.assertEqual(self.post("/api/ports/ouvrir", {"port": "x"})[0], 400)
        ouvrir.assert_not_called()


if __name__ == "__main__":
    unittest.main()
