# -*- coding: utf-8 -*-
"""Icône de « Mes outils » dans la zone de notification de Linux (en haut à
droite sur Ubuntu), avec son menu.

Protocoles du bureau, parlés en pur Python par D-Bus (bibliothèque jeepney) :
- org.kde.StatusNotifierItem : l'icône elle-même (clic = ouvrir le tableau
  de bord) ; affichée par l'extension « AppIndicator » d'Ubuntu, KDE, XFCE…
- com.canonical.dbusmenu : son menu (mêmes entrées que le clic droit de la
  bulle).

Sans jeepney, sans bus de session ou sans zone de notification : pas
d'icône, rien ne plante (la bulle reste affichée).

La boucle D-Bus tourne dans un fil à part ; les actions du menu sont
renvoyées au fil de Tk par la fonction « executer » (racine.after).

Le menu est décrit par une liste d'entrées (dictionnaires), la même que pour
le menu de la bulle :
    {"libelle": "Note rapide", "action": fonction}
    {"libelle": "(vide)", "actif": False}
    {"libelle": "Extraits", "enfants": [...]}
    {"separateur": True}
"""
import collections
import os
import re
import threading

NOM_APPLI = "Mes outils"
ID_APPLI = "mes-outils"
CHEMIN_ICONE = "/StatusNotifierItem"
CHEMIN_MENU = "/MenuBar"
INTERFACE_ICONE = "org.kde.StatusNotifierItem"
INTERFACE_OBSERVATEUR = "org.kde.StatusNotifierWatcher"
CHEMIN_OBSERVATEUR = "/StatusNotifierWatcher"
INTERFACE_MENU = "com.canonical.dbusmenu"
PROPRIETES = "org.freedesktop.DBus.Properties"
INTROSPECTION = "org.freedesktop.DBus.Introspectable"
PAIR = "org.freedesktop.DBus.Peer"

SEPARATEUR = {"separateur": True}

# Pas d'emoji dans les menus : texte seul (comme la bulle).
_EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿⌀-⏿■-◿]️?")


class ErreurDBus(Exception):
    """Réponse d'erreur D-Bus : nom de l'erreur et message."""

    def __init__(self, nom, message=""):
        super().__init__(message)
        self.nom = nom
        self.message = message


def sobre(texte):
    """Le libellé sans emoji ni espaces en trop."""
    return " ".join(_EMOJI.sub("", str(texte)).split())


def libelle_dbusmenu(texte):
    """dbusmenu lit « _ » comme une touche d'accès : on le double."""
    return sobre(texte).replace("_", "__")


def argb(rgba):
    """Pixels RGBA → ARGB 32 bits, octet de poids fort d'abord (format de
    IconPixmap)."""
    rgba = bytes(rgba)
    sortie = bytearray(len(rgba))
    sortie[0::4] = rgba[3::4]
    sortie[1::4] = rgba[0::4]
    sortie[2::4] = rgba[1::4]
    sortie[3::4] = rgba[2::4]
    return bytes(sortie)


def dessin_icone(diametre):
    """Le logo de la bulle (rond violet, quatre carrés au trait), en RGBA
    transparent autour (Pillow)."""
    from PIL import Image, ImageDraw  # noqa: PLC0415

    s = 4
    d = diametre * s
    image = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    dessin = ImageDraw.Draw(image)
    dessin.ellipse((0, 0, d - 1, d - 1), fill=(91, 91, 214, 255))
    cote, ecart, trait = d * 0.19, d * 0.08, max(2, int(d * 0.05))
    debut = (d - (2 * cote + ecart)) / 2
    for ligne in range(2):
        for colonne in range(2):
            x = debut + colonne * (cote + ecart)
            y = debut + ligne * (cote + ecart)
            dessin.rounded_rectangle((x, y, x + cote, y + cote), radius=cote * 0.22,
                                     outline=(255, 255, 255, 255), width=trait)
    return image.resize((diametre, diametre), Image.LANCZOS)


def pixmaps(tailles=(22, 32, 48, 64)):
    """Valeur de IconPixmap : [(largeur, hauteur, octets ARGB)], ou [] sans Pillow."""
    try:
        return [(t, t, argb(dessin_icone(t).tobytes())) for t in tailles]
    except Exception:  # noqa: BLE001
        return []


# ---------------------------------------------------------------------------
# Le menu (com.canonical.dbusmenu), sans D-Bus : structures prêtes à envoyer
# ---------------------------------------------------------------------------
class Menu:
    """Les entrées du menu, numérotées (0 = la racine), et leur révision.

    Les valeurs renvoyées ont la forme attendue par jeepney : un variant est
    un couple (signature, valeur)."""

    def __init__(self, entrees=()):
        self._verrou = threading.Lock()
        self.revision = 0
        self._elements = {0: {"enfants": []}}
        self._enfants = {0: []}
        self._empreinte = None
        self.charger(entrees)

    @staticmethod
    def empreinte(entrees):
        """Ce qui se voit du menu (sans les actions) : sert à savoir s'il a changé."""
        def une(e):
            if e.get("separateur"):
                return ("-",)
            return (sobre(e.get("libelle", "")), bool(e.get("actif", True)),
                    tuple(une(x) for x in e["enfants"]) if "enfants" in e else None)
        return tuple(une(e) for e in entrees)

    def charger(self, entrees):
        """Remplace les entrées. Renvoie True si le menu visible a changé (une
        nouvelle révision est alors à annoncer par LayoutUpdated)."""
        entrees = list(entrees or [])
        empreinte = self.empreinte(entrees)
        elements, enfants = {0: {"enfants": entrees}}, {0: []}
        compteur = [0]

        def numeroter(liste, parent):
            for e in liste:
                compteur[0] += 1
                ident = compteur[0]
                elements[ident] = e
                enfants[parent].append(ident)
                enfants[ident] = []
                if "enfants" in e:
                    numeroter(e["enfants"], ident)

        numeroter(entrees, 0)
        with self._verrou:
            change = empreinte != self._empreinte
            self._elements, self._enfants = elements, enfants
            if change:
                self._empreinte = empreinte
                self.revision += 1
        return change

    def identifiants(self):
        with self._verrou:
            return sorted(self._elements)

    def proprietes(self, ident, noms=()):
        """Les propriétés d'une entrée (a{sv}) ; noms vide = toutes."""
        with self._verrou:
            e = self._elements.get(ident)
            a_enfants = bool(self._enfants.get(ident))
        if e is None:
            raise ErreurDBus("org.freedesktop.DBus.Error.InvalidArgs", f"Entrée inconnue : {ident}")
        if ident == 0:
            props = {"children-display": ("s", "submenu")}
        elif e.get("separateur"):
            props = {"type": ("s", "separator")}
        else:
            props = {"label": ("s", libelle_dbusmenu(e.get("libelle", ""))),
                     "enabled": ("b", bool(e.get("actif", True))), "visible": ("b", True)}
            if "enfants" in e or a_enfants:
                props["children-display"] = ("s", "submenu")
        if noms:
            props = {k: v for k, v in props.items() if k in noms}
        return props

    def disposition(self, parent=0, profondeur=-1, noms=()):
        """Réponse de GetLayout : (révision, (id, propriétés, [enfants en variants]))."""
        with self._verrou:
            revision = self.revision

        def noeud(ident, reste):
            if reste == 0:
                fils = []
            else:
                with self._verrou:
                    ids = list(self._enfants.get(ident, []))
                fils = [("(ia{sv}av)", noeud(i, reste - 1)) for i in ids]
            return (ident, self.proprietes(ident, noms), fils)

        return revision, noeud(parent, profondeur)

    def proprietes_groupe(self, ids=(), noms=()):
        """Réponse de GetGroupProperties : [(id, propriétés)] (ids vide = toutes)."""
        ids = list(ids) or self.identifiants()
        resultat = []
        for ident in ids:
            try:
                resultat.append((ident, self.proprietes(ident, noms)))
            except ErreurDBus:
                continue
        return resultat

    def action(self, ident):
        """La fonction d'une entrée cliquable, ou None."""
        with self._verrou:
            e = self._elements.get(ident)
        if not e or ident == 0 or e.get("separateur") or not e.get("actif", True):
            return None
        return e.get("action")


# ---------------------------------------------------------------------------
# Réponses aux appels D-Bus (sans D-Bus : testables)
# ---------------------------------------------------------------------------
XML_ICONE = """<!DOCTYPE node PUBLIC "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"
 "http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd">
<node>
  <interface name="org.kde.StatusNotifierItem">
    <property name="Category" type="s" access="read"/>
    <property name="Id" type="s" access="read"/>
    <property name="Title" type="s" access="read"/>
    <property name="Status" type="s" access="read"/>
    <property name="WindowId" type="i" access="read"/>
    <property name="IconThemePath" type="s" access="read"/>
    <property name="IconName" type="s" access="read"/>
    <property name="IconPixmap" type="a(iiay)" access="read"/>
    <property name="OverlayIconName" type="s" access="read"/>
    <property name="OverlayIconPixmap" type="a(iiay)" access="read"/>
    <property name="AttentionIconName" type="s" access="read"/>
    <property name="AttentionIconPixmap" type="a(iiay)" access="read"/>
    <property name="AttentionMovieName" type="s" access="read"/>
    <property name="ToolTip" type="(sa(iiay)ss)" access="read"/>
    <property name="ItemIsMenu" type="b" access="read"/>
    <property name="Menu" type="o" access="read"/>
    <method name="ContextMenu"><arg name="x" type="i" direction="in"/><arg name="y" type="i" direction="in"/></method>
    <method name="Activate"><arg name="x" type="i" direction="in"/><arg name="y" type="i" direction="in"/></method>
    <method name="SecondaryActivate"><arg name="x" type="i" direction="in"/><arg name="y" type="i" direction="in"/></method>
    <method name="Scroll"><arg name="delta" type="i" direction="in"/><arg name="orientation" type="s" direction="in"/></method>
    <signal name="NewTitle"/>
    <signal name="NewIcon"/>
    <signal name="NewAttentionIcon"/>
    <signal name="NewOverlayIcon"/>
    <signal name="NewToolTip"/>
    <signal name="NewStatus"><arg name="status" type="s"/></signal>
  </interface>
  <interface name="org.freedesktop.DBus.Properties">
    <method name="Get"><arg type="s" direction="in"/><arg type="s" direction="in"/><arg type="v" direction="out"/></method>
    <method name="GetAll"><arg type="s" direction="in"/><arg type="a{sv}" direction="out"/></method>
  </interface>
  <interface name="org.freedesktop.DBus.Introspectable">
    <method name="Introspect"><arg type="s" direction="out"/></method>
  </interface>
</node>
"""

XML_MENU = """<!DOCTYPE node PUBLIC "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"
 "http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd">
<node>
  <interface name="com.canonical.dbusmenu">
    <property name="Version" type="u" access="read"/>
    <property name="TextDirection" type="s" access="read"/>
    <property name="Status" type="s" access="read"/>
    <property name="IconThemePath" type="as" access="read"/>
    <method name="GetLayout">
      <arg type="i" name="parentId" direction="in"/><arg type="i" name="recursionDepth" direction="in"/>
      <arg type="as" name="propertyNames" direction="in"/>
      <arg type="u" name="revision" direction="out"/><arg type="(ia{sv}av)" name="layout" direction="out"/>
    </method>
    <method name="GetGroupProperties">
      <arg type="ai" name="ids" direction="in"/><arg type="as" name="propertyNames" direction="in"/>
      <arg type="a(ia{sv})" name="properties" direction="out"/>
    </method>
    <method name="GetProperty">
      <arg type="i" name="id" direction="in"/><arg type="s" name="name" direction="in"/>
      <arg type="v" name="value" direction="out"/>
    </method>
    <method name="Event">
      <arg type="i" name="id" direction="in"/><arg type="s" name="eventId" direction="in"/>
      <arg type="v" name="data" direction="in"/><arg type="u" name="timestamp" direction="in"/>
    </method>
    <method name="EventGroup">
      <arg type="a(isvu)" name="events" direction="in"/><arg type="ai" name="idErrors" direction="out"/>
    </method>
    <method name="AboutToShow">
      <arg type="i" name="id" direction="in"/><arg type="b" name="needUpdate" direction="out"/>
    </method>
    <method name="AboutToShowGroup">
      <arg type="ai" name="ids" direction="in"/><arg type="ai" name="updatesNeeded" direction="out"/>
      <arg type="ai" name="idErrors" direction="out"/>
    </method>
    <signal name="ItemsPropertiesUpdated">
      <arg type="a(ia{sv})" name="updatedProps"/><arg type="a(ias)" name="removedProps"/>
    </signal>
    <signal name="LayoutUpdated"><arg type="u" name="revision"/><arg type="i" name="parent"/></signal>
    <signal name="ItemActivationRequested"><arg type="i" name="id"/><arg type="u" name="timestamp"/></signal>
  </interface>
  <interface name="org.freedesktop.DBus.Properties">
    <method name="Get"><arg type="s" direction="in"/><arg type="s" direction="in"/><arg type="v" direction="out"/></method>
    <method name="GetAll"><arg type="s" direction="in"/><arg type="a{sv}" direction="out"/></method>
  </interface>
  <interface name="org.freedesktop.DBus.Introspectable">
    <method name="Introspect"><arg type="s" direction="out"/></method>
  </interface>
</node>
"""

XML_RACINE = """<!DOCTYPE node PUBLIC "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"
 "http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd">
<node>
  <node name="StatusNotifierItem"/>
  <node name="MenuBar"/>
</node>
"""


class Service:
    """Les objets /StatusNotifierItem et /MenuBar : répond aux appels, sans
    rien savoir du transport (testable sans D-Bus).

    au_clic : fonction appelée au clic sur l'icône ;
    executer : reçoit une fonction et la fait tourner dans le fil de Tk."""

    def __init__(self, au_clic, executer, titre=NOM_APPLI, icones=None):
        self.au_clic = au_clic
        self.executer = executer
        self.titre = titre
        self.menu = Menu()
        self.icones = pixmaps() if icones is None else icones

    def proprietes_icone(self):
        return {
            "Category": ("s", "ApplicationStatus"),
            "Id": ("s", ID_APPLI),
            "Title": ("s", self.titre),
            "Status": ("s", "Active"),
            "WindowId": ("i", 0),
            "IconThemePath": ("s", ""),
            # Sans image dessinée : l'icône du thème installée par installation.py.
            "IconName": ("s", "" if self.icones else ID_APPLI),
            "IconPixmap": ("a(iiay)", self.icones),
            "OverlayIconName": ("s", ""),
            "OverlayIconPixmap": ("a(iiay)", []),
            "AttentionIconName": ("s", ""),
            "AttentionIconPixmap": ("a(iiay)", []),
            "AttentionMovieName": ("s", ""),
            "ToolTip": ("(sa(iiay)ss)", ("", [], self.titre, "")),
            "ItemIsMenu": ("b", False),
            "Menu": ("o", CHEMIN_MENU),
        }

    @staticmethod
    def proprietes_menu():
        return {"Version": ("u", 3), "TextDirection": ("s", "ltr"), "Status": ("s", "normal"),
                "IconThemePath": ("as", [])}

    def _proprietes(self, chemin, interface):
        if chemin == CHEMIN_ICONE and interface in (INTERFACE_ICONE, ""):
            return self.proprietes_icone()
        if chemin == CHEMIN_MENU and interface in (INTERFACE_MENU, ""):
            return self.proprietes_menu()
        raise ErreurDBus("org.freedesktop.DBus.Error.UnknownInterface", f"Interface inconnue : {interface}")

    def _lancer(self, fonction):
        if fonction:
            self.executer(fonction)

    def repondre(self, chemin, interface, membre, corps):
        """Un appel de méthode → (signature, corps de la réponse). Lève
        ErreurDBus pour une réponse d'erreur."""
        interface = interface or ""
        corps = tuple(corps or ())
        if membre == "Introspect" and interface in (INTROSPECTION, ""):
            xml = {CHEMIN_ICONE: XML_ICONE, CHEMIN_MENU: XML_MENU, "/": XML_RACINE}.get(chemin)
            if xml is None:
                raise ErreurDBus("org.freedesktop.DBus.Error.UnknownObject", f"Objet inconnu : {chemin}")
            return "s", (xml,)
        if interface == PAIR:
            if membre == "Ping":
                return None, ()
            if membre == "GetMachineId":
                try:
                    with open("/etc/machine-id", encoding="ascii") as f:
                        return "s", (f.read().strip(),)
                except OSError:
                    return "s", ("",)
        if interface == PROPRIETES:
            if membre == "Get":
                props = self._proprietes(chemin, corps[0])
                if corps[1] not in props:
                    raise ErreurDBus("org.freedesktop.DBus.Error.UnknownProperty", f"Propriété inconnue : {corps[1]}")
                return "v", (props[corps[1]],)
            if membre == "GetAll":
                return "a{sv}", (self._proprietes(chemin, corps[0]),)
            if membre == "Set":
                raise ErreurDBus("org.freedesktop.DBus.Error.PropertyReadOnly", "Propriété en lecture seule.")
        if chemin == CHEMIN_ICONE and interface in (INTERFACE_ICONE, ""):
            if membre in ("Activate", "SecondaryActivate"):
                self._lancer(self.au_clic)
                return None, ()
            if membre in ("ContextMenu", "Scroll"):
                return None, ()  # le menu est affiché par le bureau lui-même
        if chemin == CHEMIN_MENU and interface in (INTERFACE_MENU, ""):
            if membre == "GetLayout":
                parent, profondeur, noms = corps
                return "u(ia{sv}av)", self.menu.disposition(parent, profondeur, noms)
            if membre == "GetGroupProperties":
                ids, noms = corps
                return "a(ia{sv})", (self.menu.proprietes_groupe(ids, noms),)
            if membre == "GetProperty":
                ident, nom = corps
                props = self.menu.proprietes(ident)
                if nom not in props:
                    raise ErreurDBus("org.freedesktop.DBus.Error.InvalidArgs", f"Propriété inconnue : {nom}")
                return "v", (props[nom],)
            if membre == "Event":
                ident, evenement = corps[0], corps[1]
                if ident not in self.menu.identifiants():
                    raise ErreurDBus("org.freedesktop.DBus.Error.InvalidArgs", f"Entrée inconnue : {ident}")
                if evenement == "clicked":
                    self._lancer(self.menu.action(ident))
                return None, ()
            if membre == "EventGroup":
                connus, erreurs = self.menu.identifiants(), []
                for ident, evenement, _donnees, _heure in corps[0]:
                    if ident not in connus:
                        erreurs.append(ident)
                    elif evenement == "clicked":
                        self._lancer(self.menu.action(ident))
                return "ai", (erreurs,)
            if membre == "AboutToShow":
                return "b", (False,)
            if membre == "AboutToShowGroup":
                connus = self.menu.identifiants()
                return "aiai", ([], [i for i in corps[0] if i not in connus])
        raise ErreurDBus("org.freedesktop.DBus.Error.UnknownMethod", f"Méthode inconnue : {interface}.{membre}")


# ---------------------------------------------------------------------------
# L'icône : connexion au bus de session (jeepney), dans un fil à part
# ---------------------------------------------------------------------------
def adresse_bus():
    """L'adresse du bus de session, ou None."""
    adresse = os.environ.get("DBUS_SESSION_BUS_ADDRESS")
    if adresse:
        return adresse
    prise = os.path.join(os.environ.get("XDG_RUNTIME_DIR") or "/nonexistent", "bus")
    return f"unix:path={prise}" if os.path.exists(prise) else None


def disponible():
    """Vrai si jeepney est là et qu'un bus de session existe."""
    if not adresse_bus():
        return False
    try:
        import jeepney  # noqa: F401, PLC0415
        import jeepney.io.blocking  # noqa: F401, PLC0415
    except Exception:  # noqa: BLE001
        return False
    return True


class Icone:
    """L'icône de la zone de notification.

        icone = Icone(au_clic=ouvrir, executer=lambda f: racine.after(0, f))
        icone.demarrer()                 # False si impossible (pas de jeepney…)
        icone.actualiser(entrees)        # à chaque changement du menu
        icone.enregistree                # vrai quand le bureau l'affiche
        icone.arreter()
    """

    def __init__(self, au_clic, executer, titre=NOM_APPLI, journal=None):
        self.service = Service(au_clic, executer, titre)
        self.journal = journal or (lambda _m: None)
        self.enregistree = False
        self._arret = threading.Event()
        self._a_envoyer = collections.deque()
        self._attentes = {}
        self._fil = None
        self._nom = f"org.kde.StatusNotifierItem-{os.getpid()}-1"

    def actualiser(self, entrees):
        """Nouvelles entrées du menu ; annonce la nouvelle révision au bureau
        si le menu visible a changé."""
        if self.service.menu.charger(entrees):
            self._a_envoyer.append(("LayoutUpdated", self.service.menu.revision))

    def demarrer(self):
        if not disponible():
            return False
        self._fil = threading.Thread(target=self._boucle, name="icone-linux", daemon=True)
        self._fil.start()
        return True

    def arreter(self):
        self._arret.set()
        self.enregistree = False

    # -- fil D-Bus ---------------------------------------------------------
    def _boucle(self):
        from jeepney import HeaderFields, MatchRule, MessageType, message_bus  # noqa: PLC0415
        from jeepney.io.blocking import open_dbus_connection  # noqa: PLC0415

        try:
            conn = open_dbus_connection(bus=adresse_bus())
        except Exception as erreur:  # noqa: BLE001
            self.journal(f"Icône : bus de session indisponible ({erreur})")
            return
        try:
            conn.send_and_get_reply(message_bus.RequestName(self._nom, 4), timeout=5)  # 4 : ne pas attendre
            # Le bureau (ré)affiche sa zone de notification : se réinscrire.
            regle = MatchRule(type="signal", sender="org.freedesktop.DBus", interface="org.freedesktop.DBus",
                              member="NameOwnerChanged", path="/org/freedesktop/DBus")
            regle.add_arg_condition(0, INTERFACE_OBSERVATEUR)
            conn.send_and_get_reply(message_bus.AddMatch(regle), timeout=5)
            self._inscrire(conn)
            while not self._arret.is_set():
                self._envoyer_signaux(conn)
                try:
                    message = conn.receive(timeout=0.25)
                except TimeoutError:
                    continue
                self._traiter(conn, message, HeaderFields, MessageType)
        except Exception as erreur:  # noqa: BLE001
            self.journal(f"Icône : arrêt de la boucle D-Bus ({erreur})")
        finally:
            self.enregistree = False
            try:
                conn.close()
            except Exception:  # noqa: BLE001
                pass

    def _inscrire(self, conn):
        """Demande à l'observateur (la zone de notification) d'afficher
        l'icône. La réponse arrive dans la boucle : pendant ce temps, le
        bureau peut déjà lire nos propriétés."""
        from jeepney import DBusAddress, new_method_call  # noqa: PLC0415

        observateur = DBusAddress(CHEMIN_OBSERVATEUR, bus_name=INTERFACE_OBSERVATEUR, interface=INTERFACE_OBSERVATEUR)
        appel = new_method_call(observateur, "RegisterStatusNotifierItem", "s", (self._nom,))
        numero = next(conn.outgoing_serial)
        self._attentes[numero] = "inscription"
        conn.send(appel, serial=numero)

    def _envoyer_signaux(self, conn):
        from jeepney import DBusAddress, new_signal  # noqa: PLC0415

        while self._a_envoyer:
            nom, revision = self._a_envoyer.popleft()
            emetteur = DBusAddress(CHEMIN_MENU, interface=INTERFACE_MENU)
            conn.send(new_signal(emetteur, nom, "ui", (revision, 0)))

    def _traiter(self, conn, message, HeaderFields, MessageType):  # noqa: N803
        from jeepney import new_error, new_method_return  # noqa: PLC0415

        entete = message.header
        champs = entete.fields
        genre = entete.message_type
        if genre in (MessageType.method_return, MessageType.error):
            if self._attentes.pop(champs.get(HeaderFields.reply_serial), None) == "inscription":
                self.enregistree = genre == MessageType.method_return
                if not self.enregistree:
                    self.journal("Icône : pas de zone de notification (extension AppIndicator absente ?)")
            return
        if genre == MessageType.signal:
            if champs.get(HeaderFields.member) == "NameOwnerChanged" and len(message.body) == 3:
                nom, _ancien, nouveau = message.body
                if nom == INTERFACE_OBSERVATEUR:
                    self.enregistree = False
                    if nouveau:
                        self._inscrire(conn)
            return
        if genre != MessageType.method_call:
            return
        try:
            signature, corps = self.service.repondre(champs.get(HeaderFields.path, ""),
                                                     champs.get(HeaderFields.interface, ""),
                                                     champs.get(HeaderFields.member, ""), message.body)
            reponse = new_method_return(message, signature, corps)
        except ErreurDBus as erreur:
            reponse = new_error(message, erreur.nom, "s", (erreur.message,))
        except Exception as erreur:  # noqa: BLE001
            self.journal(f"Icône : {erreur}")
            reponse = new_error(message, "org.freedesktop.DBus.Error.Failed", "s", (str(erreur),))
        conn.send(reponse)
