# -*- coding: utf-8 -*-
"""Tests de la boîte mail (mail.py) : fournisseurs, recherche, dossier des
envoyés, envoi SSL / STARTTLS. Aucune vraie connexion : imaplib, smtplib et
le coffre du système (Windows ou trousseau Linux) sont simulés."""
import imaplib
import json
import os
import sys
import unittest
from unittest import mock

# Lancé par « python -m unittest tests.test_mail » comme par « discover -s tests ».
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aide import ConfigTemporaire  # noqa: E402

import mail  # noqa: E402

ADRESSE_GMAIL = "test.exemple@gmail.com"
SECRET = "abcd efgh ijkl mnop"


class FauxIMAP:
    """Faux serveur IMAP : enregistre les commandes reçues."""
    instances = []
    capacites = ("IMAP4REV1", "IDLE")
    liste = [b'(\\HasNoChildren) "/" "INBOX"']
    refuser = False

    def __init__(self, hote, port=993, ssl_context=None, timeout=None):
        self.hote, self.port = hote, port
        self.commandes = []
        self.literal = None
        self.capabilities = type(self).capacites
        FauxIMAP.instances.append(self)

    def login(self, identifiant, secret):
        self.identifiant, self.secret = identifiant, secret
        if type(self).refuser:
            raise imaplib.IMAP4.error("[AUTHENTICATIONFAILED] Invalid credentials")
        return "OK", [b"connecte"]

    def capability(self):
        return "OK", [" ".join(type(self).capacites).encode()]

    def list(self):
        return "OK", list(type(self).liste)

    def select(self, nom, readonly=True):
        self.commandes.append(("SELECT", nom))
        return "OK", [b"3"]

    def uid(self, commande, *args):
        self.commandes.append((commande, args, self.literal))
        self.literal = None
        if commande == "SEARCH":
            return "OK", [b"1 2"]
        return "OK", [(b'1 (UID 2 FLAGS (\\Seen) BODY[HEADER.FIELDS (FROM TO SUBJECT DATE)] {60}',
                       b"From: Alice <alice@exemple.com>\r\nSubject: Bonjour\r\n\r\n"), b")"]

    def status(self, boite, quoi):
        return "OK", [b'"INBOX" (UNSEEN 4)']

    def logout(self):
        return "BYE", []


class BaseMail(unittest.TestCase):
    def setUp(self):
        FauxIMAP.instances = []
        FauxIMAP.capacites = ("IMAP4REV1", "IDLE")
        FauxIMAP.liste = [b'(\\HasNoChildren) "/" "INBOX"']
        FauxIMAP.refuser = False
        self.coffre = {}
        self.patchs = [
            mock.patch.object(mail.imaplib, "IMAP4_SSL", FauxIMAP),
            mock.patch.object(mail, "coffre_lire", side_effect=lambda a: self.coffre.get(a)),
            mock.patch.object(mail, "coffre_ecrire", side_effect=lambda a, s: self.coffre.__setitem__(a, s)),
            mock.patch.object(mail, "coffre_supprimer", side_effect=lambda a: self.coffre.pop(a, None)),
        ]
        for p in self.patchs:
            p.start()

    def tearDown(self):
        for p in self.patchs:
            p.stop()

    def derniere_recherche(self):
        return [c for c in FauxIMAP.instances[-1].commandes if c[0] == "SEARCH"][-1]


class TestFournisseurs(BaseMail):
    def test_detection_par_domaine(self):
        attendus = {"x@gmail.com": "gmail", "x@yahoo.fr": "yahoo", "x@icloud.com": "icloud",
                    "x@me.com": "icloud", "x@zohomail.com": "zoho", "x@fastmail.com": "fastmail",
                    "x@gmx.fr": "gmx", "x@orange.fr": "orange", "x@wanadoo.fr": "orange",
                    "x@free.fr": "free", "x@laposte.net": "laposte", "x@hotmail.fr": "outlook",
                    "x@outlook.com": "outlook", "x@live.fr": "outlook", "x@societe-exemple.fr": None}
        for adresse, fournisseur in attendus.items():
            self.assertEqual(mail.detecter_fournisseur(adresse), fournisseur, f"mauvais fournisseur pour {adresse}")

    def test_prereglages(self):
        r = mail.normaliser("x@yahoo.fr")
        self.assertEqual((r["imap_hote"], r["imap_port"]), ("imap.mail.yahoo.com", 993))
        self.assertEqual((r["smtp_hote"], r["smtp_port"], r["smtp_securite"]), ("smtp.mail.yahoo.com", 465, "ssl"))
        self.assertEqual(r["identifiant"], "x@yahoo.fr", "l'identifiant par défaut doit être l'adresse")
        icloud = mail.normaliser("x@icloud.com")
        self.assertEqual((icloud["smtp_port"], icloud["smtp_securite"]), (587, "starttls"))
        ovh = mail.normaliser("contact@societe-exemple.fr", {"fournisseur": "ovh"})
        self.assertEqual((ovh["imap_hote"], ovh["smtp_hote"]), ("ssl0.ovh.net", "ssl0.ovh.net"))
        self.assertEqual(mail.normaliser("x@gmx.de")["imap_hote"], "imap.gmx.net")

    def test_reglages_manuels(self):
        r = mail.normaliser("moi@societe-exemple.fr", {"fournisseur": "autre", "imap_hote": "mail.exemple.org",
                                                       "smtp_hote": "smtp.exemple.org", "smtp_securite": "starttls",
                                                       "identifiant": "moi"})
        self.assertEqual(r["imap_port"], 993, "port IMAP par défaut : 993")
        self.assertEqual(r["smtp_port"], 587, "port STARTTLS par défaut : 587")
        self.assertEqual(r["identifiant"], "moi")
        with self.assertRaises(mail.ErreurMail):
            mail.normaliser("moi@societe-exemple.fr", {"fournisseur": "autre", "imap_hote": "", "smtp_hote": "x"})
        with self.assertRaises(mail.ErreurMail):
            mail.normaliser("moi@societe-exemple.fr", {"fournisseur": "autre", "imap_hote": "a b",
                                                       "smtp_hote": "smtp.exemple.org"})
        with self.assertRaises(mail.ErreurMail):
            mail.normaliser("moi@societe-exemple.fr", {"fournisseur": "autre", "imap_hote": "a.org",
                                                       "smtp_hote": "b.org", "imap_port": "99999"})

    def test_outlook_refuse_clairement(self):
        with ConfigTemporaire({"outils": []}):
            b = mail.Boite("")
            with self.assertRaises(mail.ErreurMail) as ctx:
                b.tester_et_enregistrer("x@hotmail.com", "secret")
            self.assertIn("pas encore pris en charge", str(ctx.exception))
            self.assertEqual(FauxIMAP.instances, [], "aucune connexion ne doit être tentée pour Outlook")
            self.assertEqual(self.coffre, {}, "rien ne doit entrer dans le coffre")
        with self.assertRaises(mail.ErreurMail):
            mail.normaliser("x@exemple.org", {"fournisseur": "outlook"})


class TestConnexion(BaseMail):
    def test_retrocompatibilite_gmail(self):
        # Ancienne configuration : seulement l'adresse (domaine Google Workspace).
        with ConfigTemporaire({"mail": {"adresse": "moi@societe-exemple.fr"}, "outils": []}):
            self.coffre["moi@societe-exemple.fr"] = "codeapplication"
            b = mail.Boite("moi@societe-exemple.fr")
            self.assertTrue(b.configuree())
            self.assertEqual(b.reglages()["imap_hote"], "imap.gmail.com", "ancienne config = Gmail")
            self.assertEqual(b.non_lus(), 4)
            self.assertEqual(FauxIMAP.instances[-1].hote, "imap.gmail.com")
            self.assertEqual(FauxIMAP.instances[-1].identifiant, "moi@societe-exemple.fr")

    def test_enregistrement_sans_mot_de_passe_dans_le_fichier(self):
        with ConfigTemporaire({"outils": []}) as cfg:
            b = mail.Boite("")
            b.tester_et_enregistrer(ADRESSE_GMAIL, SECRET)
            contenu = cfg.lire()
            self.assertEqual(self.coffre[ADRESSE_GMAIL], "abcdefghijklmnop", "espaces du code d'application retirés")
            self.assertEqual(contenu["mail"]["fournisseur"], "gmail")
            self.assertEqual(contenu["mail"]["adresse"], ADRESSE_GMAIL)
            texte = json.dumps(contenu)
            self.assertNotIn("abcdefghijklmnop", texte, "le mot de passe ne doit jamais être écrit dans outils.json")
            self.assertNotIn("abcd", texte, "le mot de passe ne doit jamais être écrit dans outils.json")
            self.assertEqual(b.adresse, ADRESSE_GMAIL)

    def test_mot_de_passe_habituel_garde_ses_espaces(self):
        with ConfigTemporaire({"outils": []}) as cfg:
            mail.Boite("").tester_et_enregistrer("x@orange.fr", "mot de passe")
            self.assertEqual(self.coffre["x@orange.fr"], "mot de passe")
            self.assertEqual(cfg.lire()["mail"]["imap_hote"], "imap.orange.fr")

    def test_reglages_manuels_enregistres(self):
        with ConfigTemporaire({"outils": []}) as cfg:
            b = mail.Boite("")
            b.tester_et_enregistrer("moi@societe-exemple.fr", "secret",
                                    {"fournisseur": "autre", "imap_hote": "mail.exemple.org", "imap_port": 993,
                                     "smtp_hote": "mail.exemple.org", "smtp_port": 587, "smtp_securite": "starttls"})
            self.assertEqual(FauxIMAP.instances[-1].hote, "mail.exemple.org")
            sec = cfg.lire()["mail"]
            self.assertEqual((sec["fournisseur"], sec["smtp_securite"], sec["smtp_port"]), ("autre", "starttls", 587))
            # Une nouvelle boîte (redémarrage) relit ces réglages.
            self.assertEqual(mail.Boite("moi@societe-exemple.fr").reglages()["imap_hote"], "mail.exemple.org")

    def test_refus_message_generique(self):
        FauxIMAP.refuser = True
        with ConfigTemporaire({"outils": []}) as cfg:
            with self.assertRaises(mail.ErreurMail) as ctx:
                mail.Boite("").tester_et_enregistrer("x@free.fr", "faux")
            self.assertNotIn("Gmail", str(ctx.exception))
            self.assertIn("refuse", str(ctx.exception))
            self.assertEqual(self.coffre, {})
            self.assertNotIn("mail", cfg.lire(), "rien n'est enregistré si la connexion échoue")
        with ConfigTemporaire({"outils": []}):
            with self.assertRaises(mail.ErreurMail) as ctx:
                mail.Boite("").tester_et_enregistrer("x@yahoo.com", "faux")
            self.assertIn("mot de passe d'application", str(ctx.exception))

    def test_etat_pour_la_page(self):
        with ConfigTemporaire({"mail": {"adresse": ADRESSE_GMAIL}, "outils": []}):
            etat = mail.Boite(ADRESSE_GMAIL).etat()
            self.assertFalse(etat["configuree"])
            self.assertEqual(etat["reglages"]["fournisseur"], "gmail")
            self.assertIn("ovh", [f["id"] for f in etat["fournisseurs"]])


class TestRecherche(BaseMail):
    def boite(self):
        self.coffre[ADRESSE_GMAIL] = "secret"
        return mail.Boite(ADRESSE_GMAIL, mail.prereglage("gmail", ADRESSE_GMAIL))

    def test_recherche_gmail(self):
        FauxIMAP.capacites = ("IMAP4REV1", "X-GM-EXT-1")
        mails = self.boite().lister("recus", "facture")
        self.assertEqual(mails[0]["sujet"], "Bonjour")
        _, args, _ = self.derniere_recherche()
        self.assertEqual(args, (None, "X-GM-RAW", '"facture"'))

    def test_recherche_standard(self):
        self.boite().lister("recus", "facture")
        _, args, _ = self.derniere_recherche()
        self.assertEqual(args, (None, "OR", "OR", "FROM", '"facture"', "SUBJECT", '"facture"', "TEXT", '"facture"'))

    def test_recherche_accents(self):
        self.boite().lister("recus", "réunion")
        _, args, litteral = self.derniere_recherche()
        self.assertEqual(args, ("CHARSET", "UTF-8", "TEXT"))
        self.assertEqual(litteral, "réunion".encode("utf-8"))

    def test_recherche_nettoyee(self):
        self.boite().lister("recus", 'a"b\\c')
        _, args, _ = self.derniere_recherche()
        self.assertNotIn('"a"b', " ".join(a for a in args if a))
        self.assertEqual(args[4], '"a b c"')

    def test_sans_recherche(self):
        self.boite().lister("recus", "")
        self.assertEqual(self.derniere_recherche()[1], (None, "ALL"))


class TestDossierEnvoyes(BaseMail):
    def selection(self):
        self.coffre[ADRESSE_GMAIL] = "secret"
        mail.Boite(ADRESSE_GMAIL, mail.prereglage("gmail", ADRESSE_GMAIL)).lister("envoyes")
        return [c for c in FauxIMAP.instances[-1].commandes if c[0] == "SELECT"][-1][1]

    def test_marque_sent(self):
        FauxIMAP.liste = [b'(\\HasNoChildren) "/" "INBOX"', b'(\\HasNoChildren \\Sent) "/" "[Gmail]/Messages envoy&AOk-s"',
                          b'(\\HasNoChildren) "/" "Sent"']
        self.assertEqual(self.selection(), '"[Gmail]/Messages envoy&AOk-s"', "la marque \\Sent passe avant le nom")

    def test_repli_par_nom_utf7(self):
        FauxIMAP.liste = [b'(\\HasNoChildren) "/" INBOX', b'(\\HasNoChildren) "/" "&AMk-l&AOk-ments envoy&AOk-s"']
        self.assertEqual(self.selection(), '"&AMk-l&AOk-ments envoy&AOk-s"')

    def test_repli_inbox_sent(self):
        FauxIMAP.liste = [b'(\\HasChildren) "." INBOX', b'(\\HasNoChildren) "." INBOX.Sent']
        self.assertEqual(self.selection(), '"INBOX.Sent"')

    def test_nom_en_litteral(self):
        FauxIMAP.liste = [(b'(\\HasNoChildren) "/" {10}', b"Sent Items")]
        self.assertEqual(self.selection(), '"Sent Items"')

    def test_introuvable(self):
        FauxIMAP.liste = [b'(\\HasNoChildren) "/" "INBOX"', b'(\\HasNoChildren) "/" "Archives"']
        with self.assertRaises(mail.ErreurMail):
            self.selection()

    def test_decodage_utf7(self):
        self.assertEqual(mail.decoder_utf7_imap("&AMk-l&AOk-ments envoy&AOk-s"), "Éléments envoyés")
        self.assertEqual(mail.decoder_utf7_imap("Tom &- Jerry"), "Tom & Jerry")
        self.assertEqual(mail.decoder_utf7_imap("INBOX"), "INBOX")


class TestEnvoi(BaseMail):
    def envoyer(self, reglages):
        self.coffre["x@exemple.org"] = "secret"
        b = mail.Boite("x@exemple.org", reglages)
        with mock.patch.object(mail.smtplib, "SMTP_SSL") as ssl_, mock.patch.object(mail.smtplib, "SMTP") as clair:
            b.envoyer("dest@exemple.org", "Objet", "Bonjour")
        return ssl_, clair

    def test_smtp_ssl(self):
        ssl_, clair = self.envoyer(mail.prereglage("gmail", "x@exemple.org"))
        self.assertEqual(ssl_.call_args[0], ("smtp.gmail.com", 465))
        clair.assert_not_called()
        session = ssl_.return_value.__enter__.return_value
        session.login.assert_called_once_with("x@exemple.org", "secret")
        session.send_message.assert_called_once()

    def test_smtp_starttls(self):
        ssl_, clair = self.envoyer(mail.prereglage("icloud", "x@exemple.org"))
        ssl_.assert_not_called()
        self.assertEqual(clair.call_args[0], ("smtp.mail.me.com", 587))
        clair.return_value.starttls.assert_called_once()
        clair.return_value.__enter__.return_value.login.assert_called_once_with("x@exemple.org", "secret")

    def test_envoi_refuse_message_generique(self):
        self.coffre["x@exemple.org"] = "secret"
        b = mail.Boite("x@exemple.org", mail.prereglage("free", "x@exemple.org"))
        with mock.patch.object(mail.smtplib, "SMTP_SSL") as ssl_:
            ssl_.return_value.__enter__.return_value.send_message.side_effect = mail.smtplib.SMTPRecipientsRefused({})
            with self.assertRaises(mail.ErreurMail) as ctx:
                b.envoyer("dest@exemple.org", "Objet", "Bonjour")
        self.assertTrue(str(ctx.exception).startswith("Envoi refusé par le serveur"))

    def test_destinataire_obligatoire(self):
        with self.assertRaises(mail.ErreurMail):
            mail.Boite("x@exemple.org").envoyer("  ", "Objet", "Bonjour")


class TestCoffreDuSysteme(unittest.TestCase):
    """Le mot de passe passe par systeme.secret_* (Windows comme Linux)."""

    def test_delegation(self):
        with mock.patch.object(mail.systeme, "secret_ecrire", return_value=True) as ecrire, \
                mock.patch.object(mail.systeme, "secret_lire", return_value="s3cret") as lire, \
                mock.patch.object(mail.systeme, "secret_supprimer") as supprimer:
            mail.coffre_ecrire("x@exemple.org", "s3cret")
            self.assertEqual(mail.coffre_lire("x@exemple.org"), "s3cret")
            mail.coffre_supprimer("x@exemple.org")
        ecrire.assert_called_once_with("MesOutils:mail:x@exemple.org", "x@exemple.org", "s3cret")
        lire.assert_called_once_with("MesOutils:mail:x@exemple.org")
        supprimer.assert_called_once_with("MesOutils:mail:x@exemple.org")

    def test_echec_message_selon_le_systeme(self):
        with mock.patch.object(mail.systeme, "secret_ecrire", return_value=False):
            with mock.patch.object(mail.systeme, "WINDOWS", True):
                with self.assertRaises(mail.ErreurMail) as ctx:
                    mail.coffre_ecrire("x@exemple.org", "s")
                self.assertEqual(str(ctx.exception),
                                 "Impossible d'enregistrer le mot de passe dans le coffre Windows.",
                                 "texte Windows inchangé (la page le traduit tel quel)")
            with mock.patch.object(mail.systeme, "WINDOWS", False):
                with self.assertRaises(mail.ErreurMail) as ctx:
                    mail.coffre_ecrire("x@exemple.org", "s")
                self.assertIn("trousseau du bureau", str(ctx.exception))
                self.assertNotIn("Windows", str(ctx.exception))

    def test_sans_ctypes_au_chargement(self):
        self.assertFalse(hasattr(mail, "_advapi"), "plus aucun appel Windows au chargement du module")


if __name__ == "__main__":
    unittest.main()
