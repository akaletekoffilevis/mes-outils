# -*- coding: utf-8 -*-
"""Application « Modèles de messages » : des textes prêts à l'emploi
(réponses types, relances de paiement, confirmations de rendez-vous, prises
de contact, refus poli, mails récurrents).

Chaque modèle : titre, catégorie, objet (pour un mail, facultatif), texte avec
des variables entre accolades ({prenom}, {nom}, {entreprise}, {date},
{montant} et toute autre variable libre), langue (fr, en, autre), favori,
nombre d'utilisations.

Fichier donnees\\modeles.json : {"modeles": [...], "exemples": true}. Les
exemples sont créés au premier usage seulement (fichier absent) : supprimés,
ils ne reviennent que si on le demande (route « exemples »).

Routes POST /api/modeles/<action>.
"""
import re
import threading
import time
import unicodedata
import uuid
from urllib.parse import quote

import config
import systeme

NOM = "modeles"
FORMAT_EXPORT = "mes-outils/modeles"
LANGUES = ("fr", "en", "autre")
TRIS = ("favoris", "usage", "titre")
MAX_TITRE = 120
MAX_CATEGORIE = 40
MAX_OBJET = 250
MAX_TEXTE = 20_000
MAX_IMPORT = 2_000
# Au-delà, le système et les logiciels de messagerie coupent le lien mailto :
# le texte est alors copié à part, le lien ne garde que l'objet.
MAX_LIEN_MAIL = 1_900

# {prenom}, {date_rdv}, {numéro} : une lettre (ou _) puis lettres, chiffres, _ ou -.
RE_VARIABLE = re.compile(r"\{([^\W\d][\w-]{0,39})\}")
RE_ADRESSE = re.compile(r"^[^@\s,;<>\"]+@[^@\s,;<>\"]+\.[^@\s,;<>\"]+$")

_verrou = threading.RLock()


# ---------------------------------------------------------------------------
# Exemples livrés avec l'application (neutres, sans donnée personnelle)
# ---------------------------------------------------------------------------
EXEMPLES = [
    {"titre": "Accusé de réception", "categorie": "Réponses types", "favori": True,
     "objet": "Bien reçu : votre message",
     "texte": "Bonjour {prenom},\n\nMerci pour votre message, que j'ai bien reçu. Je reviens vers vous "
              "au plus tard le {date_de_réponse} avec une réponse complète.\n\nBien cordialement,"},
    {"titre": "Absence et délai de réponse", "categorie": "Réponses types",
     "objet": "Absent(e) jusqu'au {date_de_retour}",
     "texte": "Bonjour,\n\nMerci pour votre message. Je suis absent(e) jusqu'au {date_de_retour} inclus "
              "et je vous répondrai dès mon retour.\n\nPour toute urgence, vous pouvez contacter "
              "{personne_à_contacter}.\n\nBien cordialement,"},
    {"titre": "Relance de paiement (rappel aimable)", "categorie": "Relances", "favori": True,
     "objet": "Facture {numéro_de_facture} : petit rappel",
     "texte": "Bonjour {prenom},\n\nSauf erreur de ma part, la facture {numéro_de_facture} d'un montant de "
              "{montant}, arrivée à échéance le {échéance}, n'a pas encore été réglée.\n\nPourriez-vous "
              "me confirmer la date prévue du paiement ? Si le règlement a déjà été effectué, merci de ne "
              "pas tenir compte de ce message.\n\nBien cordialement,"},
    {"titre": "Relance de paiement (second rappel)", "categorie": "Relances",
     "objet": "Facture {numéro_de_facture} : second rappel",
     "texte": "Bonjour {prenom},\n\nMalgré mon précédent rappel, la facture {numéro_de_facture} de {montant}, "
              "échue depuis le {échéance}, reste impayée à ce jour.\n\nJe vous remercie de bien vouloir "
              "procéder au règlement sous {délai}. Si une difficulté vous en empêche, parlons-en : nous "
              "trouverons une solution.\n\nCordialement,"},
    {"titre": "Relance après un devis", "categorie": "Relances",
     "objet": "Votre devis {numéro_de_devis}",
     "texte": "Bonjour {prenom},\n\nJe reviens vers vous au sujet du devis {numéro_de_devis} envoyé le "
              "{envoyé_le}. Avez-vous eu le temps d'en prendre connaissance ?\n\nJe peux l'adapter si "
              "besoin, ou en discuter de vive voix.\n\nBien cordialement,"},
    {"titre": "Confirmation de rendez-vous", "categorie": "Rendez-vous", "favori": True,
     "objet": "Confirmation de notre rendez-vous du {date_du_rendez-vous}",
     "texte": "Bonjour {prenom},\n\nJe vous confirme notre rendez-vous le {date_du_rendez-vous} à {heure}, {lieu}."
              "\n\nEn cas d'empêchement, merci de me prévenir dès que possible afin que nous puissions "
              "convenir d'un autre créneau.\n\nÀ bientôt,"},
    {"titre": "Rappel de rendez-vous (la veille)", "categorie": "Rendez-vous",
     "objet": "Rappel : rendez-vous demain à {heure}",
     "texte": "Bonjour {prenom},\n\nPetit rappel : nous avons rendez-vous demain à {heure}, {lieu}.\n\n"
              "À demain,"},
    {"titre": "Prise de contact", "categorie": "Prise de contact",
     "objet": "Prise de contact : {sujet}",
     "texte": "Bonjour {prenom},\n\nJe me permets de vous écrire au sujet de {sujet}. J'accompagne des "
              "entreprises comme {entreprise} sur ce type de besoin et je serais ravi(e) d'en parler avec "
              "vous quelques minutes.\n\nSeriez-vous disponible pour un court appel la semaine prochaine ?"
              "\n\nBien cordialement,"},
    {"titre": "Envoi d'un devis", "categorie": "Suivi client",
     "objet": "Devis {numéro_de_devis} pour {entreprise}",
     "texte": "Bonjour {prenom},\n\nComme convenu, vous trouverez ci-joint le devis {numéro_de_devis} d'un "
              "montant de {montant}, valable jusqu'au {fin_de_validité}.\n\nJe reste à votre disposition pour toute "
              "question ou ajustement.\n\nBien cordialement,"},
    {"titre": "Paiement bien reçu", "categorie": "Suivi client",
     "objet": "Paiement reçu, merci",
     "texte": "Bonjour {prenom},\n\nJe vous confirme la bonne réception de votre paiement de {montant} "
              "le {date}. Merci pour votre confiance !\n\nBien cordialement,"},
    {"titre": "Refus poli d'une proposition", "categorie": "Refus",
     "objet": "Votre proposition",
     "texte": "Bonjour {prenom},\n\nMerci pour votre proposition et pour la confiance que vous m'accordez."
              "\n\nAprès réflexion, je ne suis malheureusement pas en mesure d'y donner suite pour le moment. "
              "N'hésitez pas à revenir vers moi pour un prochain projet.\n\nBien cordialement,"},
    {"titre": "Compte rendu de réunion", "categorie": "Mails récurrents",
     "objet": "Compte rendu : {sujet} ({date})",
     "texte": "Bonjour à tous,\n\nVoici le compte rendu de notre réunion du {date}.\n\nPoints abordés :\n"
              "- \n\nDécisions :\n- \n\nProchaines étapes :\n- \n\nBonne journée,"},
]

# Mêmes exemples en anglais, créés quand la langue de l'application est l'anglais.
EXAMPLES_EN = [
    {"titre": "Acknowledgement of receipt", "categorie": "Standard replies", "favori": True,
     "objet": "Received: your message",
     "texte": "Hello {first_name},\n\nThank you for your message, which I have received. I will get back to you "
              "by {reply_date} at the latest with a full answer.\n\nKind regards,"},
    {"titre": "Out of office", "categorie": "Standard replies",
     "objet": "Away until {return_date}",
     "texte": "Hello,\n\nThank you for your message. I am away until {return_date} and will reply as soon as "
              "I am back.\n\nFor anything urgent, please contact {contact_person}.\n\nKind regards,"},
    {"titre": "Payment reminder (friendly)", "categorie": "Follow-ups", "favori": True,
     "objet": "Invoice {invoice_number}: a quick reminder",
     "texte": "Hello {first_name},\n\nUnless I am mistaken, invoice {invoice_number} for {amount}, due on "
              "{due_date}, has not been paid yet.\n\nCould you confirm the expected payment date? If payment "
              "has already been made, please disregard this message.\n\nKind regards,"},
    {"titre": "Payment reminder (second notice)", "categorie": "Follow-ups",
     "objet": "Invoice {invoice_number}: second reminder",
     "texte": "Hello {first_name},\n\nDespite my previous reminder, invoice {invoice_number} for {amount}, "
              "due since {due_date}, remains unpaid.\n\nPlease settle it within {deadline}. If something is "
              "preventing you from doing so, let's talk: we will find a solution.\n\nRegards,"},
    {"titre": "Quote follow-up", "categorie": "Follow-ups",
     "objet": "Your quote {quote_number}",
     "texte": "Hello {first_name},\n\nI am following up on quote {quote_number} sent on {sent_on}. Have you "
              "had time to look at it?\n\nI can adjust it if needed, or discuss it with you.\n\nKind regards,"},
    {"titre": "Appointment confirmation", "categorie": "Appointments", "favori": True,
     "objet": "Confirming our appointment on {appointment_date}",
     "texte": "Hello {first_name},\n\nI confirm our appointment on {appointment_date} at {time}, {place}."
              "\n\nIf you cannot make it, please let me know as soon as possible so we can find another "
              "slot.\n\nSee you soon,"},
    {"titre": "Appointment reminder (day before)", "categorie": "Appointments",
     "objet": "Reminder: appointment tomorrow at {time}",
     "texte": "Hello {first_name},\n\nA quick reminder: we are meeting tomorrow at {time}, {place}.\n\n"
              "See you tomorrow,"},
    {"titre": "First contact", "categorie": "First contact",
     "objet": "Getting in touch: {subject}",
     "texte": "Hello {first_name},\n\nI am writing to you about {subject}. I help companies like {company} "
              "with this kind of need and would be glad to talk with you for a few minutes.\n\nWould you be "
              "available for a short call next week?\n\nKind regards,"},
    {"titre": "Sending a quote", "categorie": "Client follow-up",
     "objet": "Quote {quote_number} for {company}",
     "texte": "Hello {first_name},\n\nAs agreed, please find attached quote {quote_number} for {amount}, "
              "valid until {valid_until}.\n\nI remain available for any question or adjustment.\n\nKind regards,"},
    {"titre": "Payment received", "categorie": "Client follow-up",
     "objet": "Payment received, thank you",
     "texte": "Hello {first_name},\n\nI confirm receipt of your payment of {amount} on {date}. Thank you for "
              "your trust!\n\nKind regards,"},
    {"titre": "Politely declining a proposal", "categorie": "Declines",
     "objet": "Your proposal",
     "texte": "Hello {first_name},\n\nThank you for your proposal and for your trust.\n\nAfter consideration, "
              "I am unfortunately unable to take it forward at the moment. Feel free to come back to me for a "
              "future project.\n\nKind regards,"},
    {"titre": "Meeting minutes", "categorie": "Recurring emails",
     "objet": "Minutes: {subject} ({date})",
     "texte": "Hello everyone,\n\nHere are the minutes of our meeting on {date}.\n\nTopics discussed:\n"
              "- \n\nDecisions:\n- \n\nNext steps:\n- \n\nHave a good day,"},
]
for _e in EXAMPLES_EN:
    _e["langue"] = "en"


def _exemples():
    """Les exemples dans la langue de l'application."""
    try:
        anglais = config.lire().get("langue") == "en"
    except Exception:
        anglais = False
    return EXAMPLES_EN if anglais else EXEMPLES


# ---------------------------------------------------------------------------
# Outils
# ---------------------------------------------------------------------------
def _maintenant():
    return time.strftime("%Y-%m-%dT%H:%M")


def _sans_accents(texte):
    """Minuscules sans accents, pour chercher et comparer."""
    texte = unicodedata.normalize("NFD", str(texte or "").lower())
    return "".join(c for c in texte if unicodedata.category(c) != "Mn")


def cle_variable(nom):
    """La clé d'une variable : {Prénom} et {prenom} sont la même variable."""
    return _sans_accents(nom)


def variables(*textes):
    """Les variables d'un ou plusieurs textes, dans l'ordre d'apparition, sans
    doublon (clés : minuscules sans accents)."""
    vues = []
    for texte in textes:
        for m in RE_VARIABLE.finditer(str(texte or "")):
            cle = cle_variable(m.group(1))
            if cle not in vues:
                vues.append(cle)
    return vues


def remplir(texte, valeurs):
    """Remplace chaque variable par sa valeur. Une variable sans valeur (ou
    vide) reste entre accolades, pour qu'on la voie."""
    propres = {cle_variable(k): str(v) for k, v in (valeurs or {}).items() if v is not None and str(v) != ""}

    def remplacer(m):
        return propres.get(cle_variable(m.group(1)), m.group(0))
    return RE_VARIABLE.sub(remplacer, str(texte or ""))


def _lire():
    """Le contenu du fichier, ou None s'il n'existe pas encore."""
    contenu = config.lire_donnees(NOM, {"absent": True})
    if isinstance(contenu, list):  # forme simple écrite à la main : une liste de modèles
        return {"modeles": contenu, "exemples": True}
    if not isinstance(contenu, dict) or contenu.get("absent"):
        return None
    if not isinstance(contenu.get("modeles"), list):
        contenu["modeles"] = []
    return contenu


def _tous():
    """Les modèles enregistrés (sans créer les exemples)."""
    contenu = _lire()
    return list(contenu["modeles"]) if contenu else []


def _ecrire(modeles):
    config.ecrire_donnees(NOM, {"modeles": modeles, "exemples": True})


def _propre(modele):
    """Les champs modifiables d'un modèle, vérifiés. Lève ValueError."""
    if not isinstance(modele, dict):
        raise ValueError("Modèle invalide.")
    titre = " ".join(str(modele.get("titre") or "").split())
    texte = str(modele.get("texte") or "").replace("\r\n", "\n")
    objet = " ".join(str(modele.get("objet") or "").split())
    categorie = " ".join(str(modele.get("categorie") or "").split())
    langue = str(modele.get("langue") or "fr").strip().lower()
    if not titre:
        raise ValueError("Donnez un titre au modèle.")
    if not texte.strip():
        raise ValueError("Le texte du modèle est vide.")
    if len(titre) > MAX_TITRE:
        raise ValueError("Titre trop long (120 caractères au plus).")
    if len(categorie) > MAX_CATEGORIE:
        raise ValueError("Catégorie trop longue (40 caractères au plus).")
    if len(objet) > MAX_OBJET:
        raise ValueError("Objet trop long (250 caractères au plus).")
    if len(texte) > MAX_TEXTE:
        raise ValueError("Texte trop long (20 000 caractères au plus).")
    return {
        "titre": titre,
        "categorie": categorie,
        "objet": objet,
        "texte": texte,
        "langue": langue if langue in LANGUES else "autre",
        "favori": bool(modele.get("favori")),
    }


def _nouveau(propre):
    maintenant = _maintenant()
    return {"id": uuid.uuid4().hex[:12], **propre, "utilisations": 0, "dernier_usage": "",
            "cree": maintenant, "modifie": maintenant}


def _avec_variables(m):
    return {**m, "variables": variables(m.get("objet"), m.get("texte"))}


def _inverse(texte):
    """Clé de tri décroissante pour une date ISO (texte)."""
    return [-ord(c) for c in texte]


def _cle_tri(tri):
    titre = lambda m: _sans_accents(m.get("titre"))  # noqa: E731
    if tri == "titre":
        return titre
    if tri == "usage":
        return lambda m: (-int(m.get("utilisations") or 0), _inverse(m.get("dernier_usage") or ""), titre(m))
    # « favoris » : les favoris d'abord, puis les plus utilisés.
    return lambda m: (not m.get("favori"), -int(m.get("utilisations") or 0), titre(m))


def _empreinte(m):
    """Deux modèles de même titre et même texte sont des doublons."""
    return (_sans_accents(m.get("titre")).strip(), " ".join(str(m.get("texte") or "").split()))


def _trouver(modeles, identifiant):
    m = next((x for x in modeles if x.get("id") == identifiant), None) if identifiant else None
    if m is None:
        raise ValueError("Modèle introuvable.")
    return m


# ---------------------------------------------------------------------------
# Fonctions
# ---------------------------------------------------------------------------
def preparer():
    """Premier usage (fichier absent) : crée les exemples. Renvoie les modèles."""
    with _verrou:
        contenu = _lire()
        if contenu is not None:
            return list(contenu["modeles"])
        modeles = [_nouveau(_propre(e)) for e in _exemples()]
        _ecrire(modeles)
        return modeles


def ajouter_exemples():
    """Remet les exemples absents (même titre et même texte). Renvoie leur nombre."""
    with _verrou:
        modeles = _tous()
        vus = {_empreinte(m) for m in modeles}
        ajoutes = [_nouveau(_propre(e)) for e in _exemples() if _empreinte(e) not in vus]
        _ecrire(modeles + ajoutes)
        return len(ajoutes)


def lister(recherche="", categorie="", tri="favoris"):
    """Les modèles filtrés et triés. recherche : tous les mots doivent se
    trouver dans le titre, la catégorie, l'objet ou le texte (casse et accents
    ignorés)."""
    mots = _sans_accents(recherche).split()
    categorie = _sans_accents(categorie).strip()
    with _verrou:
        modeles = preparer()
    resultat = []
    for m in modeles:
        if categorie and _sans_accents(m.get("categorie")).strip() != categorie:
            continue
        if mots:
            botte = _sans_accents(" ".join(str(m.get(c) or "") for c in ("titre", "categorie", "objet", "texte")))
            if not all(x in botte for x in mots):
                continue
        resultat.append(_avec_variables(m))
    resultat.sort(key=_cle_tri(tri if tri in TRIS else "favoris"))
    return resultat


def categories(modeles=None):
    """Les catégories utilisées, sans doublon (casse ignorée), de A à Z."""
    vues = {}
    for m in _tous() if modeles is None else modeles:
        c = m.get("categorie") or ""
        if c and _sans_accents(c) not in vues:
            vues[_sans_accents(c)] = c
    return [vues[k] for k in sorted(vues)]


def enregistrer(modele):
    """Créer (sans id) ou modifier (avec id) un modèle. Renvoie le modèle."""
    propre = _propre(modele)
    with _verrou:
        modeles = preparer()
        if modele.get("id"):
            existant = _trouver(modeles, modele["id"])
            existant.update(propre, modifie=_maintenant())
            resultat = existant
        else:
            resultat = _nouveau(propre)
            modeles.append(resultat)
        _ecrire(modeles)
        return _avec_variables(resultat)


def supprimer(identifiant):
    """Supprimer un modèle. Renvoie le nombre de modèles supprimés (0 ou 1)."""
    with _verrou:
        modeles = _tous()
        restants = [m for m in modeles if m.get("id") != identifiant]
        if len(restants) != len(modeles):
            _ecrire(restants)
        return len(modeles) - len(restants)


def dupliquer(identifiant):
    """Une copie du modèle (« (copie) » ajouté au titre), placée juste après."""
    with _verrou:
        modeles = _tous()
        source = _trouver(modeles, identifiant)
        suffixe = " (copie)"
        propre = _propre({**source, "titre": source["titre"][:MAX_TITRE - len(suffixe)] + suffixe, "favori": False})
        copie = _nouveau(propre)
        modeles.insert(modeles.index(source) + 1, copie)
        _ecrire(modeles)
        return _avec_variables(copie)


def marquer_favori(identifiant, valeur=True):
    with _verrou:
        modeles = _tous()
        m = _trouver(modeles, identifiant)
        m["favori"] = bool(valeur)
        _ecrire(modeles)
        return _avec_variables(m)


def utiliser(identifiant):
    """Compter une utilisation (copie ou mail). Renvoie le modèle."""
    with _verrou:
        modeles = _tous()
        m = _trouver(modeles, identifiant)
        m["utilisations"] = int(m.get("utilisations") or 0) + 1
        m["dernier_usage"] = _maintenant()
        _ecrire(modeles)
        return _avec_variables(m)


def favoris():
    """Les favoris (pour la palette Ctrl + K), sans créer les exemples."""
    with _verrou:
        modeles = [m for m in _tous() if m.get("favori")]
    return sorted(modeles, key=_cle_tri("favoris"))


def exporter():
    """Tous les modèles, dans un format que importer() relit."""
    champs = ("titre", "categorie", "objet", "texte", "langue", "favori", "utilisations")
    with _verrou:
        modeles = _tous()
    return {"format": FORMAT_EXPORT, "version": 1, "exporte": _maintenant(),
            "modeles": [{c: m.get(c) for c in champs} for m in modeles]}


def importer(contenu):
    """Ajoute les modèles d'un export (ou d'une simple liste). Les doublons
    (même titre et même texte) et les modèles invalides sont ignorés.
    Renvoie {ajoutes, doublons, invalides}."""
    if isinstance(contenu, dict):
        if contenu.get("format") not in (None, FORMAT_EXPORT):
            raise ValueError("Ce fichier n'est pas un export de modèles de messages.")
        contenu = contenu.get("modeles")
    if not isinstance(contenu, list):
        raise ValueError("Ce fichier n'est pas un export de modèles de messages.")
    if len(contenu) > MAX_IMPORT:
        raise ValueError("Trop de modèles dans ce fichier (2 000 au plus).")
    with _verrou:
        modeles = preparer()
        vus = {_empreinte(m) for m in modeles}
        ajoutes = doublons = invalides = 0
        for brut in contenu:
            try:
                propre = _propre(brut)
            except ValueError:
                invalides += 1
                continue
            if _empreinte(propre) in vus:
                doublons += 1
                continue
            vus.add(_empreinte(propre))
            nouveau = _nouveau(propre)
            try:
                nouveau["utilisations"] = max(0, int(brut.get("utilisations") or 0))
            except (TypeError, ValueError):
                pass
            modeles.append(nouveau)
            ajoutes += 1
        if ajoutes:
            _ecrire(modeles)
    return {"ajoutes": ajoutes, "doublons": doublons, "invalides": invalides}


# ---------------------------------------------------------------------------
# Écrire le mail (lien mailto: ouvert par la messagerie du système)
# ---------------------------------------------------------------------------
def adresses(texte):
    """Les adresses d'un champ « À » (séparées par , ou ;). Lève ValueError."""
    liste = [a.strip() for a in re.split(r"[,;]", str(texte or "")) if a.strip()]
    for a in liste:
        if not RE_ADRESSE.match(a):
            raise ValueError(f"Adresse e-mail invalide : {a}")
    return liste


def lien_mail(a="", objet="", texte=""):
    """Le lien mailto: (RFC 6068). Si le texte le rend trop long, le lien ne
    garde que l'objet. Renvoie (lien, texte_retire)."""
    destinataires = ",".join(quote(x, safe="@") for x in adresses(a))

    def construire(avec_texte):
        parties = []
        if objet:
            parties.append("subject=" + quote(" ".join(str(objet).split()), safe=""))
        if avec_texte and texte:
            parties.append("body=" + quote(str(texte).replace("\r\n", "\n").replace("\n", "\r\n"), safe=""))
        return "mailto:" + destinataires + ("?" + "&".join(parties) if parties else "")

    lien = construire(True)
    if len(lien) <= MAX_LIEN_MAIL:
        return lien, False
    return construire(False), True


def ecrire_mail(a="", objet="", texte=""):
    """Ouvre un nouveau mail dans la messagerie du système."""
    lien, retire = lien_mail(a, objet, texte)
    try:
        systeme.ouvrir(lien)  # lien construit ici : toujours « mailto: », tout encodé
    except (OSError, RuntimeError):
        raise ValueError("Aucune messagerie n'est associée aux liens e-mail sur ce PC.")
    return {"lien": lien, "texte_retire": retire}


# ---------------------------------------------------------------------------
# Routes de la page
# ---------------------------------------------------------------------------
def _route_liste(d):
    modeles = lister(d.get("recherche") or "", d.get("categorie") or "", d.get("tri") or "favoris")
    tous = _tous()
    return {"modeles": modeles, "total": len(tous), "categories": categories(tous)}


ROUTES = {
    "liste": _route_liste,
    "favoris": lambda d: {"modeles": favoris()},
    "enregistrer": lambda d: enregistrer(d.get("modele") or {}),
    "supprimer": lambda d: {"supprimes": supprimer(d.get("id"))},
    "dupliquer": lambda d: dupliquer(d.get("id")),
    "favori": lambda d: marquer_favori(d.get("id"), d.get("favori", True)),
    "utiliser": lambda d: utiliser(d.get("id")),
    "exporter": lambda d: exporter(),
    "importer": lambda d: importer(d.get("contenu")),
    "exemples": lambda d: {"ajoutes": ajouter_exemples()},
    "mail": lambda d: ecrire_mail(d.get("a") or "", d.get("objet") or "", d.get("texte") or ""),
}
