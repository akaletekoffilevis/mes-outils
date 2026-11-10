# -*- coding: utf-8 -*-
"""Tests de l'icône Linux (icone_linux.py) : menu dbusmenu et réponses de
l'icône, sans bus D-Bus réel. Les tests de mise en forme des messages
(jeepney) ne tournent que si jeepney est installé (Linux)."""
import os
import unittest
from unittest import mock

import aide  # noqa: F401  (chemin vers outil/)

import icone_linux  # noqa: E402
from icone_linux import ErreurDBus, Menu, Service  # noqa: E402

try:
    import jeepney  # noqa: F401
    from jeepney import DBusAddress, HeaderFields, MessageType, new_method_call
    from jeepney.low_level import Parser
    JEEPNEY = True
except ImportError:
    JEEPNEY = False


def entrees_exemple(journal):
    return [
        {"libelle": "Ouvrir Mes outils", "action": lambda: journal.append("ouvrir")},
        {"libelle": "📝  Note_rapide", "action": lambda: journal.append("note")},
        {"separateur": True},
        {"libelle": "Presse-papiers", "enfants": [
            {"libelle": "abc", "action": lambda: journal.append("abc")},
            {"libelle": "(vide)", "actif": False},
        ]},
        {"libelle": "Quitter", "action": lambda: journal.append("quitter")},
    ]


class TestOutils(unittest.TestCase):
    def test_argb(self):
        self.assertEqual(icone_linux.argb(bytes([1, 2, 3, 4, 5, 6, 7, 8])), bytes([4, 1, 2, 3, 8, 5, 6, 7]),
                         "RGBA doit devenir ARGB, octet de poids fort d'abord")

    def test_libelles_sobres(self):
        self.assertEqual(icone_linux.sobre("🧰  Ouvrir   le tableau"), "Ouvrir le tableau")
        self.assertEqual(icone_linux.libelle_dbusmenu("Note_rapide"), "Note__rapide",
                         "« _ » est une touche d'accès pour dbusmenu : il faut le doubler")

    def test_images_de_l_icone(self):
        images = icone_linux.pixmaps((22, 32))
        self.assertEqual([(l, h) for l, h, _ in images], [(22, 22), (32, 32)])
        self.assertEqual(len(images[0][2]), 22 * 22 * 4)
        self.assertEqual(images[0][2][0], 0, "le coin de l'image est transparent")

    def test_pas_de_bus_pas_d_icone(self):
        with mock.patch.dict(os.environ, {"DBUS_SESSION_BUS_ADDRESS": "", "XDG_RUNTIME_DIR": ""}):
            self.assertFalse(icone_linux.disponible())
            icone = icone_linux.Icone(au_clic=lambda: None, executer=lambda f: f())
            self.assertFalse(icone.demarrer(), "sans bus de session : pas d'icône, sans erreur")
            self.assertFalse(icone.enregistree)


class TestMenu(unittest.TestCase):
    def test_revision_seulement_si_le_menu_change(self):
        journal = []
        menu = Menu()
        self.assertTrue(menu.charger(entrees_exemple(journal)))
        revision = menu.revision
        self.assertFalse(menu.charger(entrees_exemple(journal)), "même menu : pas de nouvelle révision")
        self.assertEqual(menu.revision, revision)
        autre = entrees_exemple(journal)
        autre[0]["libelle"] = "Mails (3 non lus)"
        self.assertTrue(menu.charger(autre))
        self.assertEqual(menu.revision, revision + 1)

    def test_disposition(self):
        menu = Menu(entrees_exemple([]))
        revision, (ident, props, enfants) = menu.disposition(0, -1, [])
        self.assertEqual((revision, ident), (menu.revision, 0))
        self.assertEqual(props, {"children-display": ("s", "submenu")})
        self.assertEqual(len(enfants), 5)
        self.assertTrue(all(sig == "(ia{sv}av)" for sig, _ in enfants), "chaque enfant est un variant")
        premier = enfants[0][1]
        self.assertEqual(premier[1]["label"], ("s", "Ouvrir Mes outils"))
        self.assertEqual(premier[1]["enabled"], ("b", True))
        self.assertEqual(enfants[1][1][1]["label"], ("s", "Note__rapide"), "emoji retiré, « _ » doublé")
        self.assertEqual(enfants[2][1][1], {"type": ("s", "separator")})
        sous_menu = enfants[3][1]
        self.assertEqual(sous_menu[1]["children-display"], ("s", "submenu"))
        self.assertEqual(len(sous_menu[2]), 2)
        self.assertEqual(sous_menu[2][1][1][1]["enabled"], ("b", False), "« (vide) » est grisé")

    def test_profondeur_et_noms(self):
        menu = Menu(entrees_exemple([]))
        _, (_, _, enfants) = menu.disposition(0, 0, [])
        self.assertEqual(enfants, [], "profondeur 0 : pas d'enfants")
        _, (_, _, enfants) = menu.disposition(0, 1, ["label"])
        self.assertEqual(enfants[3][1][2], [], "profondeur 1 : les sous-menus ne sont pas détaillés")
        self.assertEqual(set(enfants[0][1][1]), {"label"}, "seules les propriétés demandées")

    def test_proprietes_groupe(self):
        menu = Menu(entrees_exemple([]))
        tout = menu.proprietes_groupe([], [])
        self.assertEqual([i for i, _ in tout], list(range(0, 8)))
        self.assertEqual([i for i, _ in menu.proprietes_groupe([1, 99], [])], [1], "identifiant inconnu ignoré")

    def test_actions(self):
        journal = []
        menu = Menu(entrees_exemple(journal))
        menu.action(1)()
        menu.action(5)()
        self.assertEqual(journal, ["ouvrir", "abc"])
        self.assertIsNone(menu.action(3), "un séparateur ne fait rien")
        self.assertIsNone(menu.action(6), "une entrée grisée ne fait rien")
        self.assertIsNone(menu.action(0))


class TestService(unittest.TestCase):
    def setUp(self):
        self.journal = []
        self.service = Service(au_clic=lambda: self.journal.append("clic"), executer=lambda f: f(), icones=[])
        self.service.menu.charger(entrees_exemple(self.journal))

    def test_introspection(self):
        sig, (xml,) = self.service.repondre("/StatusNotifierItem", "org.freedesktop.DBus.Introspectable", "Introspect", ())
        self.assertEqual(sig, "s")
        self.assertIn('<method name="Activate">', xml, "le bureau ne gère le clic que si Activate est annoncé")
        _, (xml,) = self.service.repondre("/MenuBar", "org.freedesktop.DBus.Introspectable", "Introspect", ())
        self.assertIn("com.canonical.dbusmenu", xml)
        with self.assertRaises(ErreurDBus):
            self.service.repondre("/ailleurs", "org.freedesktop.DBus.Introspectable", "Introspect", ())

    def test_proprietes_de_l_icone(self):
        sig, (props,) = self.service.repondre("/StatusNotifierItem", "org.freedesktop.DBus.Properties", "GetAll",
                                              ("org.kde.StatusNotifierItem",))
        self.assertEqual(sig, "a{sv}")
        self.assertEqual(props["Menu"], ("o", "/MenuBar"))
        self.assertEqual(props["ItemIsMenu"], ("b", False), "clic = ouvrir le tableau de bord, pas le menu")
        self.assertEqual(props["IconName"], ("s", "mes-outils"), "sans image : l'icône du thème")
        sig, (valeur,) = self.service.repondre("/StatusNotifierItem", "org.freedesktop.DBus.Properties", "Get",
                                               ("org.kde.StatusNotifierItem", "Status"))
        self.assertEqual((sig, valeur), ("v", ("s", "Active")))
        with self.assertRaises(ErreurDBus):
            self.service.repondre("/StatusNotifierItem", "org.freedesktop.DBus.Properties", "Get",
                                  ("org.kde.StatusNotifierItem", "Inconnue"))
        sig, (props,) = self.service.repondre("/MenuBar", "org.freedesktop.DBus.Properties", "GetAll",
                                              ("com.canonical.dbusmenu",))
        self.assertEqual(props["Version"], ("u", 3))

    def test_clic_sur_l_icone(self):
        self.assertEqual(self.service.repondre("/StatusNotifierItem", "org.kde.StatusNotifierItem", "Activate", (5, 5)),
                         (None, ()))
        self.assertEqual(self.journal, ["clic"])
        self.service.repondre("/StatusNotifierItem", "org.kde.StatusNotifierItem", "ContextMenu", (5, 5))
        self.assertEqual(self.journal, ["clic"], "le menu est affiché par le bureau : rien à faire")

    def test_menu(self):
        sig, corps = self.service.repondre("/MenuBar", "com.canonical.dbusmenu", "GetLayout", (0, -1, []))
        self.assertEqual(sig, "u(ia{sv}av)")
        self.assertEqual(corps[0], self.service.menu.revision)
        self.service.repondre("/MenuBar", "com.canonical.dbusmenu", "Event", (2, "clicked", ("s", ""), 0))
        self.service.repondre("/MenuBar", "com.canonical.dbusmenu", "Event", (1, "hovered", ("s", ""), 0))
        self.assertEqual(self.journal, ["note"], "seul « clicked » déclenche l'action")
        sig, (erreurs,) = self.service.repondre("/MenuBar", "com.canonical.dbusmenu", "EventGroup",
                                                ([(7, "clicked", ("s", ""), 0), (99, "clicked", ("s", ""), 0)],))
        self.assertEqual((sig, erreurs, self.journal), ("ai", [99], ["note", "quitter"]))
        self.assertEqual(self.service.repondre("/MenuBar", "com.canonical.dbusmenu", "AboutToShow", (0,)), ("b", (False,)))
        self.assertEqual(self.service.repondre("/MenuBar", "com.canonical.dbusmenu", "AboutToShowGroup", ([0, 99],)),
                         ("aiai", ([], [99])))
        self.assertEqual(self.service.repondre("/MenuBar", "com.canonical.dbusmenu", "GetProperty", (1, "label")),
                         ("v", (("s", "Ouvrir Mes outils"),)))
        with self.assertRaises(ErreurDBus):
            self.service.repondre("/MenuBar", "com.canonical.dbusmenu", "Event", (99, "clicked", ("s", ""), 0))

    def test_methode_inconnue(self):
        with self.assertRaises(ErreurDBus) as cm:
            self.service.repondre("/StatusNotifierItem", "org.kde.StatusNotifierItem", "Supprimer", ())
        self.assertEqual(cm.exception.nom, "org.freedesktop.DBus.Error.UnknownMethod")


@unittest.skipUnless(JEEPNEY, "jeepney absent (installé sous Linux par requirements.txt)")
class TestMessagesJeepney(unittest.TestCase):
    """Les réponses passent par jeepney sans erreur de signature."""

    def appel(self, chemin, interface, membre, signature=None, corps=()):
        message = new_method_call(DBusAddress(chemin, bus_name=":1.42", interface=interface), membre, signature, corps)
        message.header.fields[HeaderFields.sender] = ":1.7"
        return message

    def aller_retour(self, message):
        parseur = Parser()
        parseur.add_data(message.serialise(serial=1))
        return parseur.get_next_message()

    def test_reponses_serialisees(self):
        journal = []

        class FausseConnexion:
            def __init__(self):
                self.envoyes = []

            def send(self, message, serial=None):
                self.envoyes.append(message)

        icone = icone_linux.Icone(au_clic=lambda: journal.append("clic"), executer=lambda f: f())
        icone.service.icones = icone_linux.pixmaps((22,))
        icone.actualiser(entrees_exemple(journal))
        conn = FausseConnexion()
        appels = [
            self.appel("/StatusNotifierItem", "org.freedesktop.DBus.Properties", "GetAll", "s",
                       ("org.kde.StatusNotifierItem",)),
            self.appel("/MenuBar", "com.canonical.dbusmenu", "GetLayout", "iias", (0, -1, [])),
            self.appel("/MenuBar", "com.canonical.dbusmenu", "GetGroupProperties", "aias", ([], [])),
            self.appel("/MenuBar", "com.canonical.dbusmenu", "Event", "isvu", (1, "clicked", ("s", ""), 0)),
            self.appel("/MenuBar", "com.canonical.dbusmenu", "AboutToShowGroup", "ai", ([0],)),
            self.appel("/StatusNotifierItem", "org.kde.StatusNotifierItem", "Activate", "ii", (0, 0)),
            self.appel("/StatusNotifierItem", "org.kde.StatusNotifierItem", "Inconnue"),
        ]
        for message in appels:
            icone._traiter(conn, self.aller_retour(message), HeaderFields, MessageType)
        self.assertEqual(len(conn.envoyes), len(appels), "une réponse par appel")
        for reponse in conn.envoyes:
            self.aller_retour(reponse)  # lève une erreur si signature et corps ne vont pas ensemble
        self.assertEqual([r.header.message_type for r in conn.envoyes][-1], MessageType.error)
        self.assertEqual(journal, ["ouvrir", "clic"])
        disposition = self.aller_retour(conn.envoyes[1]).body
        self.assertEqual(disposition[1][0], 0)

    def test_inscription_et_signal(self):
        icone = icone_linux.Icone(au_clic=lambda: None, executer=lambda f: f())

        class FausseConnexion:
            outgoing_serial = iter(range(10, 100))

            def __init__(self):
                self.envoyes = []

            def send(self, message, serial=None):
                self.envoyes.append((serial, message))

        conn = FausseConnexion()
        icone._inscrire(conn)
        numero, appel = conn.envoyes[0]
        self.assertEqual(appel.header.fields[HeaderFields.member], "RegisterStatusNotifierItem")
        reponse = jeepney.new_method_return(appel)
        reponse.header.fields[HeaderFields.reply_serial] = numero
        icone._traiter(conn, reponse, HeaderFields, MessageType)
        self.assertTrue(icone.enregistree, "l'observateur a accepté l'icône")
        icone.actualiser(entrees_exemple([]))
        icone._envoyer_signaux(conn)
        signal = conn.envoyes[-1][1]
        self.assertEqual(signal.header.fields[HeaderFields.member], "LayoutUpdated")
        self.aller_retour(signal)


if __name__ == "__main__":
    unittest.main()
