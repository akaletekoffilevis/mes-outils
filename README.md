# Mes outils

**[Télécharger Mes outils pour Windows (Setup.exe)](https://github.com/rarianaAina/mes-outils/releases/latest/download/Mes-outils-Setup.exe)** · rien d'autre à installer

**[Guide d'utilisation illustré](docs/GUIDE.md)** · **[Illustrated guide (English)](docs/GUIDE.en.md)**

![Accueil de Mes outils](docs/images/fr/accueil.webp)

Un tableau de bord de travail pour Windows, pour tous ceux qui gèrent leur
activité seuls : freelances, assistants virtuels, assistants de direction,
développeurs. Une petite bulle flotte sur l'écran et ouvre, d'un clic, vos
tâches, contacts, devis et factures, dépenses, mails, agenda et le reste.

Au premier lancement, vous choisissez votre métier et les applications qui
vous servent, comme dans un ERP. Les autres restent disponibles dans la page
**Applications** : les activer ou les désactiver ne supprime aucune donnée.

Tout tourne sur votre PC : un petit serveur local (`127.0.0.1:8760`, inaccessible
depuis l'extérieur) et une page affichée dans une fenêtre Edge sans barre
d'adresse. Aucun compte, aucun service en ligne. Interface en français ou en
anglais, thème clair ou sombre, palette de commandes (Ctrl + K).

## Les applications

**Au quotidien**
- **Mails** : Gmail, Yahoo, iCloud, Zoho, Fastmail, GMX, OVH, Orange, Free,
  La Poste ou tout serveur IMAP/SMTP ; mot de passe dans le coffre de Windows.
  Bouton « Modèle » pour insérer un texte prêt à l'emploi.
- **Tâches** : échéances, priorités, étiquettes, sous-étapes, répétitions ;
  en liste ou en tableau (glisser-déposer) ; rappel par la bulle.
- **Notes**, **Agenda** (rappels par la bulle), **Mots de passe** (coffre
  chiffré AES-256-GCM, clé tirée du mot de passe maître par scrypt).

**Clients et ventes**
- **Contacts** : personnes et entreprises, historique des échanges, relances,
  import et export CSV.
- **Devis et factures** : numérotation automatique, TVA multi-taux, remises,
  avoirs, paiements partiels, PDF, relance des impayés, import des heures de
  Temps. Montants calculés au centime près.
- **Dépenses** : budget du mois, charges fixes, épargne, statistiques, notes
  de frais avec justificatifs, export CSV.
- **Temps** : chrono par projet ou client, Pomodoro, export pour la facturation.

**Organisation**
- **Documents** : un classeur des documents importants (contrats, devis
  signés, attestations), rangés par client, avec rappel avant expiration.
- **Réunions et déplacements** : ordre du jour, compte rendu envoyé par mail,
  actions transformées en tâches, trajets et feuille de route.
- **Échéances** : abonnements, contrats, assurances, noms de domaine ; rappel
  avant chaque échéance et avant la date limite de résiliation.
- **Modèles de messages** : réponses types, relances, confirmations, avec
  variables remplies au moment de l'envoi.
- **Presse-papiers** : les 50 derniers textes copiés (en mémoire seulement).

**Développement**
- **Projets** : projets détectés (Node, Python, Django, Docker, Odoo…),
  ouverts dans VS Code, un terminal ou le navigateur ; serveurs de dev ;
  état Git ; fichiers `.env` sauvegardés dans le coffre chiffré.
- **Serveurs**, **GitHub** (dépôts, pull requests, issues, GitHub Actions),
  **Ports**, **Docker**, **Testeur d'API**, **SSH**.

**Petits outils**
- **Boîte à outils** (JWT, Base64, JSON, UUID, expressions régulières…) et
  **Extraits** (commandes favorites copiées en un clic).

## Installation

**Le plus simple** : téléchargez **[Mes-outils-Setup.exe](https://github.com/rarianaAina/mes-outils/releases/latest/download/Mes-outils-Setup.exe)** et
lancez-le. Python et tout le nécessaire sont inclus, sans droits
administrateur. Windows peut afficher « Windows a protégé votre ordinateur »
(installateur non signé) : **Informations complémentaires › Exécuter quand
même**. Vos réglages et données sont dans `%APPDATA%\Mes outils`.

**Depuis le code source** (pour contribuer) : Python 3.10+ avec tkinter, puis

```bat
git clone https://github.com/rarianaAina/mes-outils.git
cd mes-outils
installer.bat
```

Les données sont alors à côté du code (`outils.json`, `donnees\`, exclus du
dépôt). Pour utiliser un autre Python que celui du PATH : variable
`MES_OUTILS_PYTHON` (chemin de `pythonw.exe`).

**Construire l'installateur** : `pip install pyinstaller`, Inno Setup 6, puis
`powershell -ExecutionPolicy Bypass -File packaging\construire.ps1`. Une
étiquette `vX.Y.Z` poussée sur GitHub le construit et le publie tout seul
(`.github/workflows/version.yml`).

## Ajouter une application

Une application = un fichier Python et un fichier JavaScript, sans toucher au
reste : voir [docs/MODULES.md](docs/MODULES.md).

## Tests

```bat
python -m unittest discover -s tests
```

## Mode d'emploi

- [Guide d'utilisation illustré](docs/GUIDE.md) ([English](docs/GUIDE.en.md))
- Tout le détail, onglet par onglet : [LISEZMOI.txt](LISEZMOI.txt)

## Licence

[MIT](LICENSE)
