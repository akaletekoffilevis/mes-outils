# -*- coding: utf-8 -*-
"""Coffre du système : un secret par « cible ».

Le nom du module est resté « coffre_windows » (github.py s'en sert), mais le
travail est fait par systeme.py :
- sous Windows, le Gestionnaire d'identification : on retrouve le secret dans
  Panneau de configuration > Gestionnaire d'identification > Informations
  d'identification Windows, sous le nom de sa cible (ex. « MesOutils:github ») ;
- sous Linux, le trousseau du bureau (Secret Service : GNOME Keyring, KWallet).

Le secret n'est jamais écrit dans un fichier de l'outil.
"""
import systeme


def ecrire(cible, utilisateur, secret):
    """Range (ou remplace) le secret de cette cible. Renvoie False en cas d'échec."""
    return systeme.secret_ecrire(cible, utilisateur, secret)


def lire(cible):
    """Le secret de cette cible, ou None s'il n'y en a pas."""
    return systeme.secret_lire(cible)


def supprimer(cible):
    """Retire le secret de cette cible (sans erreur s'il n'existe pas)."""
    systeme.secret_supprimer(cible)
