# Mes outils : guide d'utilisation

**Français** · [English](GUIDE.en.md)

Mes outils est un outil de travail pour Windows. Une petite bulle flotte sur
l'écran ; un clic ouvre votre tableau de bord : tâches, clients, devis et
factures, dépenses, agenda, mails, documents, et des outils pour les
développeurs. Au premier lancement, vous choisissez votre métier et les
applications dont vous avez besoin, comme dans un ERP. Tout tourne sur votre
PC, sans compte ni service en ligne.

![Accueil de Mes outils](images/fr/accueil.webp)

## Sommaire

- [Installation](#installation)
- [Premier lancement : votre métier et vos applications](#premier-lancement--votre-métier-et-vos-applications)
- [La page Applications](#la-page-applications)
- [La bulle](#la-bulle)
- [Se déplacer](#se-déplacer)
- [Accueil](#accueil)
- Au quotidien : [Mails](#mails) · [Notes](#notes) · [Tâches](#tâches) ·
  [Agenda](#agenda) · [Mots de passe](#mots-de-passe)
- Clients et ventes : [Missions](#missions) · [Contacts](#contacts) · [Devis et factures](#devis-et-factures) ·
  [Dépenses](#dépenses) · [Temps](#temps)
- Organisation : [Documents](#documents) · [Réunions et déplacements](#réunions-et-déplacements) ·
  [Échéances](#échéances) · [Modèles de messages](#modèles-de-messages) ·
  [Presse-papiers](#presse-papiers)
- Développement : [Serveurs](#serveurs) · [Projets](#projets) · [GitHub](#github) ·
  [Ports](#ports) · [Docker](#docker) · [Testeur d'API](#testeur-dapi) · [SSH](#ssh)
- Petits outils : [Boîte à outils](#boîte-à-outils) · [Extraits](#extraits)
- [Réglages](#réglages)
- [Sécurité et vie privée](#sécurité-et-vie-privée)
- [Questions fréquentes](#questions-fréquentes)
- [Ajouter une application](#ajouter-une-application)

## Installation

### Le plus simple : l'installateur (rien d'autre à installer)

1. Téléchargez **[Mes-outils-Setup.exe](https://github.com/rarianaAina/mes-outils/releases/latest/download/Mes-outils-Setup.exe)** (Windows 10 ou 11).
2. Lancez-le. Windows peut afficher « Windows a protégé votre ordinateur » :
   l'installateur n'est pas signé (c'est payant). Cliquez sur
   **Informations complémentaires**, puis **Exécuter quand même**.
3. Choisissez les options (raccourci sur le Bureau, démarrage avec Windows),
   puis **Installer**. La bulle apparaît.

Pas besoin de droits administrateur ni de Python : tout est inclus. Le
programme s'installe dans `%LOCALAPPDATA%\Programs\Mes outils`. Vos réglages
et vos données sont dans `%APPDATA%\Mes outils` et restent sur votre PC : ils
sont gardés lors des mises à jour, et même après une désinstallation.
Désinstaller : Paramètres de Windows › Applications › Mes outils.

### Sous Linux (Ubuntu 24.04 et autres)

1. Téléchargez **[Mes-outils-x86_64.AppImage](https://github.com/rarianaAina/mes-outils/releases/latest/download/Mes-outils-x86_64.AppImage)**.
2. Rendez-le exécutable : clic droit › Propriétés › « Exécutable comme
   programme », ou `chmod +x Mes-outils-x86_64.AppImage`.
3. Double-cliquez dessus. La bulle apparaît, ainsi qu'une icône en haut à
   droite de l'écran ; « Mes outils » s'ajoute au menu des applications.

Un seul fichier, sans installation ni droits administrateur. Vos réglages et
vos données sont dans `~/.config/mes-outils`. Les mots de passe des mails et
l'accès GitHub vont dans le trousseau du bureau (GNOME Keyring, KWallet).
Pour la fenêtre sans barre d'adresse et les PDF des factures, il faut Google
Chrome ou Chromium (`sudo snap install chromium`) ; sans eux, Mes outils
s'ouvre dans le navigateur par défaut. Les fenêtres de choix de fichiers
utilisent zenity (déjà présent sous Ubuntu). Sous GNOME avec Wayland, la bulle
peut passer derrière les autres fenêtres : l'icône en haut à droite reste
toujours accessible (Réglages › Linux : bulle et icône, bulle seule ou icône
seule).

### Pour les développeurs : depuis le code source

Il faut Python 3.10 ou plus récent (avec tkinter) et Git.

```bat
git clone https://github.com/rarianaAina/mes-outils.git
cd mes-outils
installer.bat
```

`installer.bat` vérifie Python, installe les bibliothèques
(`requirements.txt`), crée les raccourcis et lance la bulle. Les données sont
alors à côté du code (`outils.json`, `donnees\`) et ne partent jamais sur
GitHub. Si vous passez ensuite à l'installateur, vos réglages et données sont
repris au premier lancement (ils sont copiés, l'original reste).

Sous Linux : `sudo apt install python3-tk zenity`, puis
`pip install -r requirements.txt` et `python3 outil/bulle.py`.

## Premier lancement : votre métier et vos applications

Au premier lancement, un assistant en trois étapes prépare l'outil pour vous.

1. **Votre prénom et la langue** (français ou anglais).
2. **Votre métier** : Freelance, Assistant(e) virtuel(le), Assistant(e) de
   direction, Développeur, ou « Je choisis moi-même ». Le métier sert
   seulement à cocher d'office les applications utiles.

![Assistant : choix du métier](images/fr/assistant-metier.webp)

3. **Vos applications** : cochez celles dont vous vous servez. Les autres
   restent disponibles plus tard, dans la page Applications.

![Assistant : choix des applications](images/fr/assistant-applications.webp)

Le menu ne montre ensuite que vos applications. Rien n'est perdu si vous vous
trompez : tout se change en un clic.

## La page Applications

Menu › **Applications** (en bas du menu). Toutes les applications de Mes
outils, rangées comme dans le menu, avec une phrase qui dit à quoi chacune
sert.

![Page Applications](images/fr/applications.webp)

- Un **interrupteur** par application : allumé, elle apparaît dans le menu, sur
  l'Accueil, dans Ctrl + K et dans le clic droit de la bulle.
- Une application éteinte disparaît de partout, mais **ses données restent**.
  Rallumez-la : tout est là.
- Filtres **Toutes / Actives / Inactives**.
- **Repartir d'un métier…** : recoche les applications prévues pour un métier.

L'Accueil, la page Applications et les Réglages sont toujours là.

## La bulle

Une bulle flotte au-dessus des autres fenêtres, sans bouton dans la barre des
tâches. Elle démarre avec Windows.

| Geste | Effet |
|---|---|
| **Clic** | ouvre le tableau de bord (ou le ramène devant s'il est déjà ouvert) |
| **Glisser** | déplace la bulle ; elle revient au même endroit la fois suivante |
| **Clic droit** | accès direct à vos applications actives (note rapide, mails, agenda, tâches, contacts, factures, projets, serveurs…), vos outils, « Masquer 15 minutes », « Quitter la bulle » |

Les pastilles autour de la bulle :

- **verte** (en haut à droite) : nombre de serveurs de dev en marche ;
- **corail** (en haut à gauche) : nombre de mails non lus ;
- **rouge** (en bas) : tests GitHub Actions en échec.

**Rappels.** À l'heure d'un rappel, une carte apparaît à côté de la bulle avec
un son : note, rendez-vous, Pomodoro, tâche à l'heure, client à relancer,
facture en retard, budget dépassé, document qui expire, échéance à payer ou
préavis de résiliation, réunion qui commence, départ en déplacement le
lendemain. Seules les applications actives envoient des rappels.

Le tableau de bord s'ouvre dans une fenêtre Edge sans barre d'adresse. Le
fermer ne coupe rien : la bulle reste là. Si vous avez quitté la bulle,
relancez-la avec le raccourci « Mes outils » du Bureau.

## Se déplacer

- **Menu à gauche** : les applications sont rangées par groupe (Au quotidien,
  Clients et ventes, Organisation, Développement, Petits outils) ; Applications
  et Réglages sont en bas. Quand il y en
  a beaucoup, le menu se resserre en icônes ; le nom s'affiche au survol.
- **Ctrl + K** (ou « Rechercher… » en haut) : la palette de commandes. Tapez
  quelques lettres pour aller à une application, créer une tâche, une facture,
  un contact, ouvrir un document, lancer un de vos outils ou changer de thème,
  puis Entrée.
- **Thème** : clair, sombre ou automatique (comme Windows).
- **Langue** : français ou anglais, dans les Réglages.

![Palette de commandes (Ctrl + K)](images/fr/palette.webp)

Le même tableau de bord en thème sombre :

![Accueil en thème sombre](images/fr/accueil-sombre.webp)

## Accueil

La page d'arrivée (voir la capture en haut de ce guide). Chaque application
active y ajoute sa carte, seulement quand elle a quelque chose à dire :

- **Aujourd'hui** : rendez-vous du jour et du lendemain ;
- **Notes épinglées**, **mails non lus**, **chrono en cours** ;
- **Tâches** en retard et du jour ; **À relancer** (contacts) ;
- **Factures** : montant à encaisser, factures en retard ;
- **Dépenses** : dépensé ce mois-ci par rapport au budget, notes de frais ;
- **Documents à renouveler**, **Échéances** de la semaine, prochaine
  **réunion** et prochain **départ** ;
- pour les développeurs, **Code** : projets à envoyer, modifiés, en retard,
  tests GitHub en échec.

En bas, **Mes outils** : vos tuiles (dossier, fichier, programme, page web ou
appli locale). « Modifier » pour en ajouter, modifier ou retirer.

![Accueil avec le métier Développeur](images/fr/accueil-dev.webp)

## Au quotidien

### Mails

Votre boîte mail : Gmail, Yahoo, iCloud, Zoho, Fastmail, GMX, OVH, Orange,
Free, La Poste ou tout serveur IMAP/SMTP.

![Mails](images/fr/mails.webp)

- Lire les mails reçus et envoyés, chercher.
- Répondre, transférer, écrire un nouveau mail.
- Bouton **Modèle** dans la fenêtre d'écriture : insère un de vos
  [modèles de messages](#modèles-de-messages), avec ses variables remplies. Le
  mail en cours est gardé.
- Les images distantes sont bloquées (elles servent à savoir si vous avez lu
  le mail) : bouton « Afficher les images ».
- Le guide du fournisseur s'affiche à la première connexion ; le mot de passe
  est rangé dans le coffre de Windows.

![Nouveau mail rempli depuis un modèle](images/fr/mails-modele.webp)

### Notes

![Notes](images/fr/notes.webp)

- Notes en cartes colorées ou **listes à cocher**.
- **Épingler** une note : elle apparaît sur l'Accueil.
- **Rappel** à une date et une heure : la bulle vous prévient.
- Recherche et filtres. Enregistrement automatique pendant la frappe.

### Tâches

Vos choses à faire, avec échéance, priorité et client.

![Tâches en liste](images/fr/taches.webp)

- **Liste** groupée : En retard, Aujourd'hui, Cette semaine, Plus tard, Sans
  échéance. Ajout rapide : tapez le titre, puis Entrée.
- Une tâche a une échéance (avec ou sans heure), une priorité (basse, normale,
  haute), des étiquettes, un client, une description et des **sous-étapes** à
  cocher.
- **Répétition** chaque jour, semaine ou mois : cochée « Fait », la tâche
  revient à la date suivante.
- **Tableau** : colonnes À faire, En cours et Fait, avec glisser-déposer.
- Filtres par étiquette, client et priorité.
- Rappel par la bulle 15 minutes avant une tâche qui a une heure.

![Tâches en tableau](images/fr/taches-tableau.webp)

### Agenda

![Agenda](images/fr/agenda.webp)

- Vue **semaine** et vue **mois**.
- Cliquer sur un créneau pour créer un rendez-vous.
- **Glisser** un rendez-vous pour le déplacer ; **Ctrl + glisser** pour le
  dupliquer.
- Rappel par la bulle : à l'heure, 5, 15, 30 minutes ou 1 heure avant, ou la
  veille.

### Mots de passe

Un coffre chiffré, ouvert avec un mot de passe maître.

![Mots de passe](images/fr/motsdepasse.webp)

- Ranger vos identifiants par catégorie, avec une note chiffrée.
- **Copier** un mot de passe : il est effacé du presse-papiers après
  30 secondes et n'entre pas dans l'historique de Windows (Win + V).
- **Afficher** un mot de passe pendant 15 secondes.
- **Générateur** de mots de passe solides.
- Le coffre se verrouille seul après 5 minutes sans utilisation.

> Le mot de passe maître n'est enregistré nulle part : s'il est oublié, le
> coffre est perdu. Notez-le sur papier.

## Clients et ventes

### Missions

Des offres de missions freelance et de postes en télétravail, triées selon ce
que vous cherchez, et le suivi de vos candidatures.

![Missions : la sélection d'une recherche](images/fr/missions.webp)

- **Sources** : Remotive, Remote OK, Himalayas, Jobicy et We Work Remotely,
  lues depuis votre PC deux fois par jour au plus. Chaque offre renvoie à sa
  page d'origine. Bouton **Sources** pour en désactiver une.
- **Recherches enregistrées** : une par type de mission (par exemple
  « Missions Odoo » et « Développement React »), chacune avec sa liste et son
  compteur de nouvelles offres. Au premier passage, un modèle est proposé selon
  votre métier.
- **Ce que vous cherchez** : domaines (développement, support client,
  assistanat, rédaction…), types (freelance, contrat, temps plein, temps
  partiel), zones d'où vous pouvez postuler, niveau, salaire minimum, mots
  importants (+5), utiles (+2) et à éviter (−5), score minimum.

![Réglage d'une recherche](images/fr/missions-recherche.webp)

- **Sélection** : chaque offre a un score et les mots qui l'ont fait remonter.
  Les nouvelles sont en haut, celles déjà vues en dessous. Un clic déplie
  l'offre : technologies, expérience demandée, **Ouvrir l'offre**,
  **Postuler**, **Ajouter l'entreprise aux contacts**, **Masquer**.
- **Postuler** : un message à copier, ou un de vos modèles (application
  Modèles), avec le poste, l'entreprise et le lien déjà remplis. L'offre passe
  ensuite dans **Candidatures**.
- **Candidatures** : à voir, postulé, entretien, refus, retenu, avec une note et
  une date de relance (une tâche est créée si Tâches est active).
- **Chercher aussi sur** : Malt, Codeur.com, ComeUp, Upwork, LinkedIn et Indeed
  s'ouvrent dans le navigateur avec vos mots-clés.
- La bulle prévient quand de nouvelles offres correspondent à une recherche.

Vous aviez un profil `profil.json` (outil metiers-tension) ? Il s'importe en
une recherche « Mon profil ».

### Contacts

Vos clients, prospects et fournisseurs : personnes et entreprises.

![Contacts, avec une fiche ouverte](images/fr/contacts.webp)

- Une fiche par personne ou entreprise ; une personne peut être rattachée à
  son entreprise.
- Coordonnées, statut (prospect, client, ancien client, fournisseur, autre)
  et étiquettes.
- **Historique des échanges** : appel, mail, rendez-vous ou note, datés.
- **Relance** : une date et un motif. « Fait », ou « Dans 3 jours / 1 semaine /
  1 mois ». La bulle prévient le jour venu.
- Filtres par statut, « À relancer » et étiquette. La recherche trouve aussi
  un numéro tapé sans espaces.
- Au survol d'une ligne : écrire, appeler, copier, modifier, supprimer.
- **Import et export CSV** (compatible Excel). À l'import, une fiche déjà
  présente est complétée, jamais écrasée.

Les autres applications (Tâches, Factures, Dépenses, Documents, Échéances,
Réunions, Modèles) proposent vos contacts dans leurs champs « Client ».

### Devis et factures

Des devis, factures et avoirs numérotés, avec des totaux exacts au centime.

![Devis et factures](images/fr/factures.webp)

- **Premier lancement** : indiquez votre entreprise (nom, adresse,
  identifiants comme le SIRET, logo, TVA, devise, conditions de paiement).
- **Numérotation** automatique à l'émission : `DEV-2026-001`, `FAC-2026-001`,
  `AV-2026-001`, remise à 1 chaque année. Les préfixes se changent dans les
  réglages (roue dentée).
- Lignes avec quantité, prix et taux de TVA ; remise en pourcentage ou en
  montant ; plusieurs taux de TVA dans un même document.
- **Émettre** : le document reçoit son numéro et sa date, puis il est figé. Le
  PDF est créé dans `Documents\Mes outils\Factures\<année>\`.
- Devis : accepté, refusé, puis **Transformer en facture** en un clic.
- Factures : paiements partiels, état (envoyée, payée partiellement, payée,
  en retard). Pour corriger une facture émise, créez un **avoir**.
- **Importer des heures** depuis l'application Temps, au taux horaire choisi.
- **Envoyer par mail** : votre messagerie s'ouvre avec le texte ; le PDF est
  à joindre (le dossier s'ouvre en même temps).
- En haut : facturé et encaissé ce mois-ci, impayés, retards. **Export CSV**.

![Un devis émis](images/fr/factures-document.webp)

### Dépenses

Votre budget et vos notes de frais.

![Dépenses : tableau de bord](images/fr/depenses.webp)

- **Tableau de bord** : dépensé ce mois-ci, budget, reste par jour,
  projection de fin de mois, dernières dépenses, top des catégories.
- **Charges fixes** (loyer, abonnements…) : ajoutées seules chaque mois.
- **Budget** mensuel, reconduit tant que vous ne le changez pas.
- **Épargne** : en cas de dépassement, vous pouvez puiser dans l'épargne des
  mois passés, ou ajouter la dépense sans y toucher.
- **Statistiques** : par période, par catégorie, évolution sur 6 mois.
- **Pour les pros** : case « Dépense professionnelle », client à refacturer,
  statut (à rembourser, remboursée, refacturée), **justificatif** photo ou
  PDF. L'onglet **Notes de frais** fait les totaux.
- Catégories modifiables. Devises : euro, dollar, ariary. Export CSV.
- La bulle prévient une fois par mois si le budget est dépassé.

### Temps

Le temps passé sur chaque projet ou client.

![Temps](images/fr/temps.webp)

- **Chrono** par projet (un seul à la fois), avec une note.
- **Pomodoro** : la bulle prévient à la fin de chaque période.
- Sessions par jour, semaine ou mois, totaux par projet.
- Ajouter une session oubliée, modifier ou supprimer une session.
- **Export CSV**, et import des heures dans une facture.

## Organisation

### Documents

Un classeur de vos documents importants : contrats, devis signés,
attestations, assurances…

![Documents](images/fr/documents.webp)

- **Ajouter un fichier** (plusieurs à la fois) ou **un dossier**. Le fichier
  reste où il est : le classeur garde seulement son adresse. Vous pouvez aussi
  en faire une copie dans `Documents\Mes outils\Classeur\<client>\`.
- Type, client ou projet, étiquettes, date du document, **date
  d'expiration**.
- Vue par client ou par type ; filtres « Expirent bientôt » et
  « Introuvables ».
- Rappel par la bulle avant l'expiration (30 jours par défaut, réglable).
- Ouvrir le fichier, ou le montrer dans l'Explorateur. « Retirer de la liste »
  ne supprime jamais le fichier. Un fichier déplacé est signalé
  « Introuvable », avec « Retrouver… ».

### Réunions et déplacements

Préparer, suivre et résumer vos réunions ; organiser vos déplacements.

![Une réunion passée, avec ses notes](images/fr/reunions.webp)

- **Réunion** : date, durée, lieu, lien de visio, participants (pris dans
  Contacts), ordre du jour à cocher, notes, décisions et **actions** (qui,
  quoi, pour quand).
- **Créer la tâche** d'une action en un clic (si Tâches est active).
- **Compte rendu** : le texte est prêt, à copier ou à envoyer par mail aux
  participants.
- **Ajouter à l'agenda** : la réunion, ou les trajets d'un déplacement.
- Rappel par la bulle 15 minutes avant.

![Un déplacement](images/fr/deplacements.webp)

- **Déplacement** : destination, dates, voyageurs, trajets (avion, train,
  voiture), hébergements, documents (billets, réservations), liste de choses à
  emporter, budget.
- **Feuille de route** imprimable.
- La bulle prévient la veille du départ.

### Échéances

Tout ce qui se renouvelle ou expire : abonnements, contrats, assurances, noms
de domaine, loyer…

![Échéances](images/fr/echeances.webp)

- Groupées en Cette semaine, Ce mois-ci, Plus tard ; les retards en rouge.
- Fréquence mensuelle, trimestrielle, annuelle, tous les N mois, ou date
  unique.
- **Payé / renouvelé** : la prochaine échéance avance d'une période (le
  31 janvier passe au 28 février, puis revient au 31 mars).
- **Reconduction tacite** avec préavis : un second rappel arrive avant la
  date limite de résiliation.
- Panneau **Coûts** : par mois et par an, par devise et par catégorie.
- Statuts actif, à résilier, résilié, terminé. Export CSV.
- Un numéro de carte ou un IBAN est refusé dans « Moyen de paiement » : notez
  plutôt « Carte pro (fin 1234) ».

### Modèles de messages

Des textes prêts à l'emploi : réponses types, relances, confirmations de
rendez-vous, comptes rendus… Douze exemples sont fournis.

![Modèles de messages](images/fr/modeles.webp)

- Des **variables** entre accolades : `{prenom}`, `{date}`, `{montant}`, ou
  celles que vous inventez.
- **Utiliser** : choisissez un contact (son prénom, son entreprise et son
  adresse se remplissent seuls), complétez le reste, regardez l'aperçu.
  Puis **Copier** ou **Écrire le mail**.
- Favoris, catégories, tri par usage. Import et export.
- Depuis Mails : bouton **Modèle** dans la fenêtre d'écriture.

![Utiliser un modèle](images/fr/modeles-utiliser.webp)

### Presse-papiers

Les 50 derniers textes copiés.

![Presse-papiers](images/fr/presse-papiers.webp)

- Recopier un ancien texte en un clic ; épingler les textes à garder.
- Chercher dans l'historique ; **Pause** pour ne plus rien enregistrer un
  moment.
- L'historique est gardé **en mémoire seulement** et effacé à la fermeture ;
  les mots de passe copiés depuis le coffre n'y entrent pas.

## Développement

Ces applications sont cochées d'office avec le métier « Développeur ».

### Serveurs

![Serveurs : serveurs Odoo et serveurs de dev des projets](images/fr/serveurs.webp)

Tous vos serveurs au même endroit : les serveurs de dev de vos projets (les
commandes définies dans Projets) et, si vous l'utilisez, les serveurs Odoo
d'un gadget externe (`gestion_serveurs.py`, chemin dans `outils.json`, clé
`serveurs_odoo` › `gadget`).

- Démarrer, arrêter, ouvrir dans le navigateur, lire le journal.
- Pastille verte : en marche ; orange : démarrage ; rouge : port pris par un
  autre programme.
- Une base Odoo marquée « référence » demande une confirmation avant d'être
  démarrée.

### Projets

Les projets trouvés dans vos dossiers de projets, avec leur type (Node,
Next.js, Vite, Python, Django, Docker, Odoo…).

![Projets](images/fr/projets.webp)

- Ouvrir un projet en un clic : **Dossier**, **VS Code**, **Terminal**.
- Voir l'**état Git** : à envoyer, à récupérer, modifié. « Tout vérifier »
  fait un `git fetch` de tous les projets.
- **Configurer** les commandes de dev : l'outil en propose d'après le projet
  (`npm run dev`, `manage.py runserver`, `docker compose up`…).
- **Démarrer** et **Arrêter** un serveur de dev, ouvrir le site, lire son
  **journal** en direct.
- Sauvegarder les fichiers **.env** dans le coffre chiffré et les restaurer en
  un clic.

![Commandes d'un projet](images/fr/projets-commandes.webp)

![Journal d'un serveur de dev](images/fr/projets-journal.webp)

### GitHub

Tous vos dépôts (publics, privés, ceux de vos organisations). La connexion se
fait une seule fois, avec un code à valider sur github.com, sans mot de passe.

![GitHub : dépôts](images/fr/github.webp)

- Chercher et filtrer vos dépôts (privés, publics, sur ce PC ou non).
- **Cloner** un dépôt, ou l'ouvrir dans son dossier ou dans VS Code.
- **Nouveau dépôt** à partir d'un dossier : le contenu est vérifié avant
  l'envoi (`.gitignore` respecté, fichiers sensibles comme `.env` signalés,
  fichiers de plus de 100 Mo refusés).
- **Pull requests** : les vôtres et celles où votre relecture est demandée.
- **Issues** qui vous sont assignées.
- **Actions** : l'état des derniers tests ; un échec allume la pastille rouge
  de la bulle.

![Actions (thème sombre)](images/fr/github-actions-sombre.webp)

### Ports

Quel programme occupe le port 3000 ? La réponse en un coup d'œil.

![Ports](images/fr/ports.webp)

- Tous les ports en écoute, avec le programme, sa ligne de commande et sa
  mémoire.
- Chercher un port ou un programme ; filtre « Développement ».
- Ouvrir un port web dans le navigateur.
- **Arrêter** un programme après confirmation. Les processus système et Mes
  outils lui-même sont protégés.

### Docker

Vos conteneurs, groupés par projet compose.

![Docker (thème sombre)](images/fr/docker-sombre.webp)

- Démarrer, arrêter, redémarrer ou supprimer un conteneur.
- « Tout démarrer » ou « Tout arrêter » pour un projet compose entier.
- Lire le journal d'un conteneur ; ouvrir les ports publiés.
- « Images et espace disque » : la place occupée par Docker.

### Testeur d'API

Un mini Postman, directement dans le tableau de bord.

![Testeur d'API](images/fr/api.webp)

- Méthode, adresse, paramètres, en-têtes, corps (JSON, texte, formulaire) et
  authentification (Bearer, Basic).
- Réponse mise en forme, avec son statut, sa durée et ses en-têtes.
- **Variables** (`{{base_url}}`), **historique** (sans les secrets) et
  requêtes enregistrées.
- Copier une requête en commande **cURL**.

### SSH

Une clé par serveur, posée en un clic.

![SSH](images/fr/ssh.webp)

- « Nouveau serveur » : nom, adresse, port, identifiant et mot de passe.
  L'outil crée la clé, la dépose sur le serveur, puis vérifie la connexion.
- Le mot de passe ne sert qu'à cette fois : il n'est enregistré nulle part.
- Ensuite, dans un terminal : `ssh <nom-court>` (un clic sur la ligne le
  copie).
- Tester la connexion, ouvrir un terminal sur le serveur, retirer la clé.

## Petits outils

### Boîte à outils

Les petits outils de tous les jours. Rien ne quitte la page.

![Boîte à outils](images/fr/boite.webp)

- **JWT** : lire l'en-tête, le contenu et les dates d'un jeton.
- **Base64**, **JSON** (mise en forme, tri), **encodage URL**.
- **Horodatage** Unix et date, **UUID**.
- **Expressions régulières** testées en direct.
- **Hachage** (SHA) d'un texte ou d'un fichier, **couleurs**.

### Extraits

Vos commandes et bouts de code favoris.

![Extraits](images/fr/extraits.webp)

- Un clic sur **Copier** : l'extrait est dans le presse-papiers.
- Classer par langage et par étiquette, épingler les plus utiles.
- Trier par usage, par titre ou par date. Aussi depuis le clic droit sur la
  bulle.

## Réglages

![Réglages](images/fr/reglages.webp)

- Prénom (pour la salutation), **langue** (français, anglais), **thème**.
- **Applications** : votre métier et le bouton « Choisir mes applications »,
  qui ouvre la page Applications.
- **Dossiers de projets** : là où Projets et GitHub cherchent vos projets.
- Démarrage avec Windows, raccourci sur le Bureau.
- **À propos** : « Rechercher une mise à jour ».

## Sécurité et vie privée

- **Tout reste sur votre PC.** Le serveur du tableau de bord n'écoute que sur
  `127.0.0.1` (ce PC seulement). Aucun compte, aucun service en ligne, aucune
  statistique envoyée.
- **Le serveur refuse les ordres venant d'autres sites** : une page web ouverte
  dans votre navigateur ne peut pas lui parler.
- **Coffre à mots de passe chiffré** en AES-256-GCM ; la clé est tirée du mot
  de passe maître par scrypt. Le mot de passe maître n'est enregistré nulle
  part.
- **Jeton GitHub et mots de passe des mails** rangés dans le coffre de Windows
  (Gestionnaire d'identification), jamais dans un fichier en clair.
- **Clients, factures, dépenses, documents** : des fichiers sur votre PC, dans
  `%APPDATA%\Mes outils`. Les documents restent à leur place ; seuls leurs
  chemins sont enregistrés.
- **Échéances** : un numéro de carte ou un IBAN est refusé.
- **Presse-papiers** : l'historique reste en mémoire, il n'est jamais écrit sur
  le disque.
- **Testeur d'API** : les jetons et mots de passe sont masqués dans
  l'historique.
- **SSH** : le mot de passe du serveur ne sert qu'à déposer la clé ; il n'est
  pas enregistré.

## Questions fréquentes

**Je ne vois plus une application dans le menu.**
Elle est sans doute éteinte : Menu › Applications, allumez son interrupteur.
Ses données sont intactes.

**Je me suis trompé de métier au premier lancement.**
Menu › Applications › « Repartir d'un métier… », ou Réglages › Applications.

**Où sont les PDF de mes devis et factures ?**
Dans `Documents\Mes outils\Factures\<année>\`. Sur un devis ou une facture :
« Ouvrir le PDF » ou « Ouvrir le dossier ».

**Le PDF d'une facture n'a pas été créé.**
Il est fabriqué avec Microsoft Edge. Si Edge est absent, la facture est quand
même émise : installez Edge, puis recréez le PDF depuis la facture.

**Outlook ou Hotmail ne se connectent pas.**
Ils ne sont pas encore pris en charge : Microsoft exige une autre méthode de
connexion. Les autres fournisseurs (Gmail, Yahoo, iCloud…) fonctionnent avec
un mot de passe d'application ou le mot de passe habituel, selon le guide
affiché.

**Comment mettre à jour Mes outils ?**
Réglages › À propos › « Rechercher une mise à jour ». Avec l'installateur,
cliquez sur **Installer** : la nouvelle version se télécharge, s'installe et
Mes outils redémarre tout seul (vos réglages et données sont gardés). Avec une
installation faite avec `git clone`, la mise à jour fait un `git pull` ;
relancez ensuite la bulle (clic droit › « Quitter la bulle », puis le
raccourci).

**La bulle a disparu.**
Elle est peut-être masquée pour 15 minutes, ou vous l'avez quittée : relancez
le raccourci « Mes outils » du Bureau.

**Mes projets n'apparaissent pas.**
Ajoutez leur dossier dans Réglages › Dossiers de projets. L'outil regarde ce
dossier et ses sous-dossiers directs ; un projet ailleurs s'ajoute avec
« Ajouter un projet ».

**L'application Docker dit que Docker est absent.**
Installez Docker Desktop et démarrez-le ; l'application propose de le
télécharger ou de le lancer. Sans Docker, le reste fonctionne normalement.

**Où sont mes données ?**
Avec l'installateur : `%APPDATA%\Mes outils`. Depuis le code source : à côté
du code, `outils.json` (réglages et tuiles) et `donnees\` (notes, tâches,
contacts, factures, coffre chiffré…). Pensez à les sauvegarder.

## Ajouter une application

Une application = un fichier Python et un fichier JavaScript, sans toucher au
reste. Elle apparaît d'elle-même dans le menu, dans la page Applications et,
si elle le souhaite, sur l'Accueil. Tout est expliqué dans
[MODULES.md](MODULES.md).

---

Anciennes versions de ce guide : [version 1.7](archives/v1.7/GUIDE.md) · [version 1.5](archives/v1.5/GUIDE.md) · [version 1.4](archives/v1.4/GUIDE.md) · [version 1.3](archives/v1.3/GUIDE.md).
