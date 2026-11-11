"use strict";
/* Onglet « GitHub » : tous vos dépôts, clonés ou ouverts en un clic, création
   d'un dépôt à partir d'un dossier, vos pull requests et issues, et l'état de
   GitHub Actions (voir github.py). Le jeton GitHub reste dans le coffre de
   Windows (ou le trousseau du bureau sous Linux) : il ne passe jamais par la page. */
(() => {
  I18N.ajouter({
    // Barre et sous-onglets
    "Dépôts": "Repositories", "Pull requests": "Pull requests", "Issues": "Issues", "Actions": "Actions",
    "Rechercher un dépôt…": "Search a repository…", "Filtrer…": "Filter…",
    "Tous": "All", "Privés": "Private", "Publics": "Public", "Sur ce PC": "On this PC", "Pas sur ce PC": "Not on this PC",
    "Nouveau dépôt": "New repository", "Dossiers de projets (où chercher et cloner)": "Project folders (where to look and clone)",
    "Relire": "Reload", "Relire depuis GitHub": "Reload from GitHub", "Déconnecter GitHub de ce PC": "Disconnect GitHub from this PC",
    "Lecture de vos dépôts…": "Reading your repositories…", "Lecture…": "Loading…",
    "Indiquez vos dossiers de projets pour voir quels dépôts sont déjà sur ce PC et pouvoir cloner : ":
      "Choose your project folders to see which repositories are already on this PC and to clone: ",
    "Choisir les dossiers": "Choose folders",
    // Dépôts
    "Aucun dépôt ne correspond.": "No repository matches.", "Aucun dépôt sur ce compte pour l'instant.": "No repository on this account yet.",
    "Ouvrir la page du dépôt": "Open the repository page", "Dossier": "Folder", "Ouvrir dans VS Code": "Open in VS Code",
    "Dossier ouvert": "Folder opened", "VS Code s'ouvre…": "VS Code is opening…",
    "Copier le dépôt sur ce PC": "Copy the repository to this PC", "Cloner": "Clone", "Clonage…": "Cloning…",
    "Archivé": "Archived", "Fork": "Fork", "Privé": "Private", "Public": "Public",
    "Mis à jour le {date}": "Updated {date}", "Sur ce PC : {chemin}": "On this PC: {chemin}",
    // Pull requests, issues
    "Revue demandée": "Review requested", "Mes pull requests ouvertes": "My open pull requests",
    "Aucune pull request ouverte.": "No open pull requests.", "Aucune revue en attente.": "No pending review.",
    "Aucune issue ne vous est assignée.": "No issue is assigned to you.", "Rien ne correspond.": "Nothing matches.",
    "Brouillon": "Draft", "Ouvrir": "Open", "Ouvrir sur GitHub": "Open on GitHub", "par {auteur}": "by {auteur}",
    "{n} affichées sur {total}": "{n} shown out of {total}",
    "Issues ouvertes qui vous sont assignées": "Open issues assigned to you",
    // Actions
    "Réussi": "Passed", "Échec": "Failed", "En cours": "In progress", "Annulé": "Cancelled",
    "Validation demandée": "Approval required", "Ignoré": "Skipped", "Illisible": "Unreadable", "Aucun workflow": "No workflow",
    "Voir le run": "View run", "Dépôt": "Repository",
    "{n} dépôt en échec : {depots}": "{n} repository failing: {depots}",
    "{n} dépôts en échec : {depots}": "{n} repositories failing: {depots}",
    "Tous les derniers runs ont réussi.": "All latest runs passed.",
    "{n} run en cours…": "{n} run in progress…", "{n} runs en cours…": "{n} runs in progress…",
    "Aucun run GitHub Actions sur vos dépôts récents.": "No GitHub Actions run on your recent repositories.",
    "Dernier run de la branche par défaut, pour vos 15 dépôts les plus récents et ceux de ce PC. Vérifié à {heure}.":
      "Latest run on the default branch, for your 15 most recent repositories and those on this PC. Checked at {heure}.",
    "Sans workflow : {depots}": "No workflow: {depots}",
    "Illisibles (Actions désactivé ou accès refusé) : {depots}": "Unreadable (Actions disabled or access denied): {depots}",
    "branche {branche}": "branch {branche}",
    // Connexion
    "Connecter GitHub": "Connect GitHub", "Connecter votre compte GitHub": "Connect your GitHub account",
    "Une seule fois. Aucun mot de passe à saisir ici : GitHub vous montre une page où valider un code.":
      "Only once. No password to type here: GitHub shows you a page where you confirm a code.",
    "Cliquez sur « Connecter GitHub » : un code de 8 caractères s'affiche et est copié.":
      "Click “Connect GitHub”: an 8-character code is shown and copied.",
    "La page github.com/login/device s'ouvre : collez le code, puis cliquez sur ":
      "The github.com/login/device page opens: paste the code, then click ",
    "Revenez ici : vos dépôts s'affichent tout seuls.": "Come back here: your repositories appear automatically.",
    "L'accès est rangé dans le coffre de Windows (Gestionnaire d'identification), jamais dans un fichier.":
      "Access is stored in the Windows vault (Credential Manager), never in a file.",
    "En attente de votre validation sur GitHub…": "Waiting for your confirmation on GitHub…",
    "Validez ce code sur GitHub": "Confirm this code on GitHub",
    "Il est déjà copié : collez-le sur la page github.com/login/device qui vient de s'ouvrir, puis cliquez sur Authorize.":
      "It is already copied: paste it on the github.com/login/device page that just opened, then click Authorize.",
    "Copier": "Copy", "Code copié": "Code copied", "Rouvrir la page": "Reopen the page", "Annuler": "Cancel",
    "GitHub connecté : {login}": "GitHub connected: {login}", "Accès refusé sur GitHub.": "Access denied on GitHub.",
    "Le code a expiré : fermez et recommencez.": "The code has expired: close and start again.",
    "Déconnecter GitHub ?": "Disconnect GitHub?", "Déconnecter": "Disconnect", "GitHub déconnecté": "GitHub disconnected",
    "L'accès est retiré de ce PC. Pour le révoquer aussi chez GitHub : Settings > Applications > Authorized OAuth Apps.":
      "Access is removed from this PC. To revoke it on GitHub too: Settings > Applications > Authorized OAuth Apps.",
    // Dossiers de projets
    "Dossiers de projets": "Project folders", "Retirer": "Remove", "Aucun dossier pour l'instant.": "No folder yet.",
    "ex. D:\\Projets": "e.g. D:\\Projects", "Enregistrer": "Save", "Dossiers enregistrés": "Folders saved", "Ajouter": "Add",
    "L'outil y cherche vos dépôts déjà présents sur ce PC (le dossier et ses sous-dossiers directs), et y clone les nouveaux.":
      "The tool looks there for repositories already on this PC (the folder and its direct subfolders), and clones new ones there.",
    // Cloner
    "Destination : {chemin}": "Destination: {chemin}", "Dans le dossier": "In folder",
    "{nom} cloné dans {chemin}": "{nom} cloned into {chemin}", "Cloner « {nom} »": "Clone “{nom}”",
    // Nouveau dépôt
    "ex. D:\\Projets\\mon-projet": "e.g. D:\\Projects\\my-project", "ex. mon-projet": "e.g. my-project",
    "Une phrase sur le projet (facultatif)": "One sentence about the project (optional)",
    "Créer et envoyer": "Create and upload", "Vérifier le contenu": "Check the content", "Lecture du dossier…": "Reading the folder…",
    "Ce dossier est déjà relié à {depot}.": "This folder is already linked to {depot}.",
    "{n} fichier · {taille}": "{n} file · {taille}", "{n} fichiers · {taille}": "{n} files · {taille}",
    " (les fichiers listés dans .gitignore sont exclus)": " (files listed in .gitignore are excluded)",
    "Ce dossier a des modifications non enregistrées (commit) : elles ne seront pas envoyées.":
      "This folder has uncommitted changes: they will not be uploaded.",
    "Fichiers lourds (plus de 50 Mo) :": "Large files (over 50 MB):",
    "GitHub refuse les fichiers de plus de 100 Mo. Ajoutez-les à .gitignore :": "GitHub refuses files over 100 MB. Add them to .gitignore:",
    "Fichiers qui contiennent souvent des mots de passe ou des clés :": "Files that often contain passwords or keys:",
    "Ajoutez-les à .gitignore puis vérifiez à nouveau, ou cochez ci-dessous si vous êtes sûr.":
      "Add them to .gitignore and check again, or tick below if you are sure.",
    "J'ai vérifié : ces fichiers peuvent être envoyés": "I checked: these files can be uploaded",
    "Envoi…": "Uploading…", "Dépôt créé et envoyé": "Repository created and uploaded",
    "{n} fichier envoyé sur {depot}.": "{n} file uploaded to {depot}.", "{n} fichiers envoyés sur {depot}.": "{n} files uploaded to {depot}.",
    "Voir sur GitHub": "View on GitHub", "Dépôt public ?": "Public repository?",
    "Tout le monde pourra voir ces fichiers sur GitHub.": "Everyone will be able to see these files on GitHub.", "Oui, public": "Yes, public",
    "Nouveau dépôt GitHub": "New GitHub repository",
    "Crée le dépôt sur votre compte et y envoie le contenu d'un dossier de ce PC.":
      "Creates the repository on your account and uploads the content of a folder from this PC.",
    "Dossier à envoyer": "Folder to upload", "Nom du dépôt": "Repository name", "Description": "Description",
    // Messages de github.py
    "GitHub ne répond pas : vérifiez la connexion internet.": "GitHub is not responding: check your internet connection.",
    "GitHub n'est pas connecté.": "GitHub is not connected.",
    "L'accès à GitHub a été retiré : reconnectez GitHub.": "Access to GitHub was revoked: reconnect GitHub.",
    "Limite d'appels à GitHub atteinte : réessayez dans quelques minutes.": "GitHub request limit reached: try again in a few minutes.",
    "Le « Device Flow » n'est pas activé dans l'application GitHub (github.com > Settings > Developer settings > OAuth Apps > Enable Device Flow).":
      "“Device Flow” is not enabled in the GitHub application (github.com > Settings > Developer settings > OAuth Apps > Enable Device Flow).",
    "L'identifiant de l'application GitHub (client_id) est invalide.": "The GitHub application ID (client_id) is invalid.",
    "Réponse inattendue de GitHub.": "Unexpected response from GitHub.",
    "La connexion à GitHub n'est pas encore configurée : il manque l'identifiant de l'application (client_id).":
      "The GitHub connection is not configured yet: the application ID (client_id) is missing.",
    "GitHub a donné un accès qui ne fonctionne pas : réessayez.": "GitHub granted an access that does not work: try again.",
    "Impossible de ranger l'accès GitHub dans le coffre de Windows.": "Could not store the GitHub access in the Windows vault.",
    // Linux : le trousseau du bureau (GNOME Keyring, KWallet) remplace le coffre de Windows.
    "L'accès est rangé dans le trousseau du bureau (GNOME Keyring, KWallet), jamais dans un fichier.":
      "Access is stored in the desktop keyring (GNOME Keyring, KWallet), never in a file.",
    "Impossible de ranger l'accès GitHub dans le trousseau du bureau.": "Could not store the GitHub access in the desktop keyring.",
    "GitHub refuse l'accès : reconnectez GitHub.": "GitHub denies access: reconnect GitHub.",
    "Le dossier de destination existe déjà.": "The destination folder already exists.",
    "git a échoué.": "git failed.",
    "Git n'est pas installé sur ce PC (https://git-scm.com).": "Git is not installed on this PC (https://git-scm.com).",
    "Git met trop de temps à répondre.": "Git is taking too long to respond.",
    "Dépôt invalide.": "Invalid repository.", "Choisissez un de vos dossiers de projets.": "Choose one of your project folders.",
    "Dossier introuvable.": "Folder not found.", "Dossier introuvable": "Folder not found",
    "Aucun fichier à envoyer dans ce dossier.": "No file to upload in this folder.",
    "Nom de dépôt invalide : lettres, chiffres, tirets, points et soulignés seulement.":
      "Invalid repository name: letters, digits, hyphens, dots and underscores only.",
    "Adresse refusée.": "Address refused.", "VS Code est introuvable sur ce PC.": "VS Code was not found on this PC.",
  });
  I18N.motifs([
    [/^GitHub a refusé la demande \((\d+)\) : ([\s\S]*)\.$/, "GitHub refused the request ($1): $2."],
    [/^GitHub a refusé la demande \((\d+)\)\.$/, "GitHub refused the request ($1)."],
    [/^GitHub a refusé la création \((\d+)\) : ([\s\S]*)\.$/, "GitHub refused to create the repository ($1): $2."],
    [/^GitHub a refusé la création \((\d+)\)\.$/, "GitHub refused to create the repository ($1)."],
    [/^Le dossier (.+) existe déjà\.$/, "The folder $1 already exists."],
    [/^Ce dossier est déjà relié à (.+)\.$/, "This folder is already linked to $1."],
    [/^GitHub refuse les fichiers de plus de 100 Mo : (.+)$/, "GitHub refuses files over 100 MB: $1"],
    [/^Un dépôt « (.+) » existe déjà sur votre compte\.$/, "A repository “$1” already exists on your account."],
    [/^Le dépôt (\S+) est créé, mais l'envoi a échoué \(([\s\S]*)\)\. Relancez « (.+) » dans le dossier\.$/,
      "The repository $1 was created, but the upload failed ($2). Run “$3” again in the folder."],
  ]);
  I18N.ajouter({
    // Affichage en lignes compactes
    "Plus d'actions": "More actions", "Ouvrir le dossier": "Open folder",
    "Dossiers de projets…": "Project folders…",
    "Ouvrir la page du dépôt sur GitHub": "Open the repository page on GitHub",
  });

  const G = { etat: null, depots: null, dossiers: [], recherche: "", filtre: "tous", sous: "depots",
    prs: null, issues: null, actions: null };
  // Couleurs officielles des langages sur GitHub (petit point devant le nom).
  const COULEURS_LANGUES = { JavaScript: "#f1e05a", TypeScript: "#3178c6", Python: "#3572A5", Java: "#b07219", HTML: "#e34c26",
    CSS: "#663399", Vue: "#41b883", PHP: "#4F5D95", "C#": "#178600", Rust: "#dea584", Go: "#00ADD8", Dart: "#00B4AB",
    Kotlin: "#A97BFF", Shell: "#89e051", PowerShell: "#012456", "Jupyter Notebook": "#DA5B0B", PLpgSQL: "#336790" };
  // État d'un run : une icône, et une couleur réservée à l'état.
  const ETATS = {
    succes: { icone: "circle-check", libelle: "Réussi", couleur: "vert" },
    echec: { icone: "circle-x", libelle: "Échec", couleur: "rouge" },
    en_cours: { icone: "loader", libelle: "En cours", couleur: "ambre" },
    action: { icone: "hand", libelle: "Validation demandée", couleur: "ambre" },
    annule: { icone: "octagon-x", libelle: "Annulé", couleur: "gris" },
    ignore: { icone: "skip-forward", libelle: "Ignoré", couleur: "gris" },
    inconnu: { icone: "circle-help", libelle: "Illisible", couleur: "gris" },
    aucun: { icone: "minus", libelle: "Aucun workflow", couleur: "gris" },
  };
  const infoEtat = e => ETATS[e] || ETATS.inconnu;

  const style = document.createElement("style");
  style.textContent = `
    /* Barre du haut */
    .profil-gh { display: flex; align-items: center; gap: 7px; color: var(--doux); font-size: 13px; }
    .profil-gh img { width: 22px; height: 22px; border-radius: 50%; }
    .plus-gh { position: relative; }
    .plus-liste { display: none; position: absolute; right: 0; top: calc(100% + 4px); min-width: 240px; z-index: 25; padding: 4px;
      background: var(--carte); border: 1px solid var(--ligne); border-radius: var(--rayon); box-shadow: var(--ombre-forte); }
    .plus-gh.ouvert .plus-liste { display: block; animation: pop .12s ease-out both; }
    .plus-gh.ouvert > .icone-btn { background: var(--surface); color: var(--encre); }
    .plus-liste button { display: flex; align-items: center; gap: 10px; width: 100%; border: 0; background: transparent; color: var(--encre);
      padding: 7px 10px; border-radius: 6px; cursor: pointer; font-size: 13.5px; text-align: left; white-space: nowrap; }
    .plus-liste button svg.ico { margin: 0; color: var(--doux); }
    .plus-liste button:hover { background: var(--surface); }
    .plus-liste button.danger:hover, .plus-liste button.danger:hover svg.ico { color: var(--rouge-texte); }
    .plus-liste .sep-gh { height: 1px; background: var(--ligne); margin: 4px 2px; }
    .sous-gh { margin: 0 0 14px; }
    .nb-gh { color: var(--gris); font-size: 12px; font-variant-numeric: tabular-nums; display: inline-flex; align-items: center; gap: 3px; }
    .puce.actif .nb-gh:not(.etat-txt) { color: var(--doux); }
    .nb-gh.etat-txt { font-size: 12px; }
    .nb-gh svg.ico { margin: 0; width: 13px; height: 13px; }
    .conseil-gh { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; color: var(--doux); font-size: 13px; margin: -4px 2px 12px; }
    .conseil-gh svg.ico { margin: 0; color: var(--gris); }

    /* Lignes */
    .ligne-titre .num-gh { color: var(--gris); font-weight: 400; flex: none; }
    .ligne-titre .proprio-gh { color: var(--doux); font-weight: 400; }
    .ligne.brouillon .ligne-titre > span:first-child { color: var(--doux); }
    .ligne-meta .sep { color: var(--gris); margin: 0 6px; }
    .langue-gh::before { content: ""; display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--c, var(--gris)); margin-right: 6px; vertical-align: .05em; }
    .tag .pt-gh { display: inline-block; width: 7px; height: 7px; border-radius: 50%; margin-right: 4px; vertical-align: .05em; }
    .ligne-cote .date-gh { min-width: 118px; text-align: right; }
    .ligne-cote .col-langue { min-width: 104px; color: var(--gris); }
    .ligne-cote .col-com { min-width: 34px; }
    .ligne-cote .info-gh { display: inline-flex; align-items: center; gap: 4px; color: var(--gris); }
    .ligne-cote .info-gh svg.ico { margin: 0; width: 14px; height: 14px; }
    .ligne-cote .local-gh { color: var(--doux); display: inline-flex; width: 16px; justify-content: center; }
    .ligne-cote .local-gh svg.ico { margin: 0; width: 15px; height: 15px; }
    .ligne-actions .icone-btn { width: 28px; height: 28px; }
    /* Trois places de bouton : les colonnes restent alignées, cloné ou non. */
    .ligne-actions.depot-gh { width: 88px; justify-content: flex-end; }
    .ligne-ic.etat-txt svg.ico { width: 17px; height: 17px; }
    .wf-gh { border: 0; background: transparent; padding: 2px; border-radius: 5px; cursor: pointer; display: inline-flex; }
    .wf-gh:hover { background: var(--ligne); }
    .wf-gh svg.ico { margin: 0; width: 14px; height: 14px; }
    .titre-lignes .nb-gh { margin-left: 6px; letter-spacing: 0; text-transform: none; font-weight: 500; }
    .titre-lignes .plus-gh-n { margin-left: 10px; font-weight: 400; text-transform: none; letter-spacing: 0; }
    .rien-gh { padding: 14px; color: var(--doux); font-size: 13px; }
    .bandeau-gh { margin: 0 2px 10px; font-size: 13px; }
    .bandeau-gh.etat-txt { font-size: 13px; white-space: normal; }
    .bandeau-gh svg.ico { margin: 0; }
    .notes-gh { margin: 12px 2px 0; display: flex; flex-direction: column; gap: 3px; }
    .note-gh { font-size: 12.5px; color: var(--gris); }
    .attente-gh { color: var(--doux); padding: 18px; text-align: center; }
    .tourne-gh { animation: tourne-gh 1.2s linear infinite; }
    @keyframes tourne-gh { to { transform: rotate(360deg); } }

    /* Connexion, fenêtres */
    .connexion-gh { max-width: 560px; margin: 24px auto; }
    .connexion-gh h3 { margin: 10px 0 4px; font-size: 16px; font-weight: 600; }
    .connexion-gh ol { padding-left: 20px; margin: 12px 0; }
    .connexion-gh li { margin: 4px 0; }
    .connexion-gh .cx-note { color: var(--doux); font-size: 13px; display: flex; gap: 6px; align-items: center; }
    .connexion-gh .cx-note svg.ico { margin: 0; }
    .connexion-gh .actions { display: flex; justify-content: flex-end; margin-top: 14px; }
    .gros-gh { width: 38px; height: 38px; border-radius: 9px; background: var(--surface); color: var(--doux); display: grid; place-items: center; }
    .gros-gh svg.ico { margin: 0; width: 20px; height: 20px; }
    .code-gh { font-family: var(--mono); font-size: 34px; font-weight: 600; letter-spacing: 4px; text-align: center; background: var(--violet-clair); color: var(--violet); border-radius: var(--rayon); padding: 14px; margin: 6px 0 14px; user-select: all; }
    .etat-attente-gh { display: flex; align-items: center; gap: 8px; }
    .etat-attente-gh svg.ico { margin: 0; }
    .dossiers-gh { display: flex; flex-direction: column; gap: 6px; margin: 4px 0 12px; }
    .dossiers-gh div { display: flex; align-items: center; gap: 8px; background: var(--surface); border-radius: 8px; padding: 5px 6px 5px 10px; font-size: 13.5px; }
    .dossiers-gh div > svg.ico { margin: 0; color: var(--doux); }
    .dossiers-gh div span { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .ajout-gh { display: flex; gap: 8px; }
    .ajout-gh input { flex: 1; }
    .bilan-gh { background: var(--surface); border-radius: 8px; padding: 10px 12px; font-size: 13.5px; margin: 8px 0; text-align: left; }
    .bilan-gh ul { margin: 6px 0 0; padding-left: 18px; }
    .bilan-gh.danger { background: var(--rouge-clair); color: var(--rouge-texte); }
    .bilan-gh code { font-size: 12.5px; font-family: var(--mono); background: var(--code); color: var(--code-texte); border-radius: 4px; padding: 0 4px; }
    .choix-gh { display: flex; gap: 14px; margin: 4px 0 10px; font-size: 14px; }
    .choix-gh label { display: flex; gap: 6px; align-items: center; cursor: pointer; }
    .choix-gh label svg.ico { margin: 0; color: var(--doux); }
  `;
  document.head.append(style);
  const racine = () => $("#vue-github");
  /** Texte venu de GitHub ou déjà traduit : el() ne le retraduit pas. */
  const brut = s => document.createTextNode(s == null ? "" : String(s));
  /** Icône suivie d'un texte (petite marge à droite). */
  const ic = nom => icone(nom, "av");
  const attente = texte => [icone("loader", "av tourne-gh"), t(texte)];
  /** Message d'erreur du serveur, dans un cadre vide. */
  const erreur = message => el("div", { class: "vide" }, icone("triangle-alert"), brut(message));
  const sep = () => el("span", { class: "sep" }, "·");

  // -- dates ---------------------------------------------------------------------
  const dateLongue = iso => iso ? new Date(iso).toLocaleString(I18N.locale(), { dateStyle: "medium", timeStyle: "short" }) : "";
  function ilYa(iso) {
    if (!iso) return "";
    const s = (new Date(iso) - Date.now()) / 1000;
    const rtf = new Intl.RelativeTimeFormat(I18N.locale(), { numeric: "auto" });
    for (const [unite, duree] of [["year", 31536000], ["month", 2592000], ["week", 604800], ["day", 86400], ["hour", 3600], ["minute", 60]]) {
      if (Math.abs(s) >= duree) return rtf.format(Math.round(s / duree), unite);
    }
    return rtf.format(0, "minute");
  }
  const quand = iso => el("span", { class: "date-gh", title: dateLongue(iso) }, brut(ilYa(iso)));

  // -- affichage ---------------------------------------------------------------
  async function afficher(relire = true, forcer = false) {
    if (relire || !G.etat) {
      try { G.etat = await api("/api/github/etat", {}); }
      catch (e) { racine().replaceChildren(erreur(e.message)); return; }
      G.dossiers = G.etat.dossiers || [];
    }
    if (!G.etat.connecte) return ecranConnexion();
    chargerSuivi(forcer);
    if (relire || !G.depots) {
      if (!G.depots) racine().replaceChildren(el("div", { class: "vide" }, icone("loader", "tourne-gh"), t("Lecture de vos dépôts…")));
      try { const r = await api("/api/github/depots", {}); G.depots = r.depots; }
      catch (e) { racine().replaceChildren(erreur(e.message)); return; }
    }
    dessiner();
  }

  /** Pull requests, issues et Actions : en parallèle, sans bloquer la liste
     des dépôts. Le serveur les garde quelques minutes (quota de GitHub). */
  function chargerSuivi(forcer) {
    for (const cle of ["prs", "issues", "actions"]) {
      if (forcer) G[cle] = null;
      api("/api/github/" + cle, { forcer })
        .then(r => { G[cle] = r; })
        .catch(e => { G[cle] = { erreur: e.message }; })
        .finally(() => { majPuces(); if (G.sous === cle) dessinerListe(); });
    }
  }

  /** Menu « … » : les actions moins fréquentes, rangées hors de la barre. */
  function menuPlus() {
    const choix = (nom, libelle, faire, classe = "") => el("button", { class: classe, role: "menuitem",
      onclick: () => { zone.classList.remove("ouvert"); faire(); } }, icone(nom), libelle);
    const bouton = el("button", { class: "icone-btn", title: "Plus d'actions", "aria-haspopup": "menu",
      onclick: () => zone.classList.toggle("ouvert") }, icone("ellipsis"));
    const zone = el("div", { class: "plus-gh" }, bouton,
      el("div", { class: "plus-liste", role: "menu" },
        choix("folders", "Dossiers de projets…", reglerDossiers),
        choix("refresh-cw", "Relire depuis GitHub", () => afficher(true, true)),
        el("div", { class: "sep-gh" }),
        choix("log-out", "Déconnecter GitHub de ce PC", deconnecter, "danger")));
    return zone;
  }
  // Le menu se ferme au clic ailleurs et avec Échap.
  document.addEventListener("mousedown", e => {
    for (const m of document.querySelectorAll(".plus-gh.ouvert")) if (!m.contains(e.target)) m.classList.remove("ouvert");
  });
  document.addEventListener("keydown", e => {
    if (e.key === "Escape") document.querySelectorAll(".plus-gh.ouvert").forEach(m => m.classList.remove("ouvert"));
  });

  function dessiner() {
    const surDepots = G.sous === "depots";
    const recherche = el("input", { placeholder: surDepots ? "Rechercher un dépôt…" : "Filtrer…", value: G.recherche,
      oninput: e => { G.recherche = e.target.value; dessinerListe(); } });
    const filtre = surDepots ? el("select", { onchange: e => { G.filtre = e.target.value; dessinerListe(); } },
      [["tous", "Tous"], ["prive", "Privés"], ["public", "Publics"], ["local", "Sur ce PC"], ["absent", "Pas sur ce PC"]]
        .map(([v, lib]) => el("option", { value: v, ...(G.filtre === v ? { selected: "" } : {}) }, lib))) : null;
    const barre = el("div", { class: "barre-vue" },
      el("h2", {}, icone("git-branch"), "GitHub"),
      el("div", { class: "profil-gh" }, G.etat.avatar ? el("img", { src: G.etat.avatar, alt: "" }) : null, brut(G.etat.login)),
      el("div", { class: "espace" }),
      el("div", { class: "champ-recherche" }, el("span", {}, icone("search")), recherche),
      filtre,
      el("button", { class: "btn principal", onclick: nouveauDepot }, ic("plus"), t("Nouveau dépôt")),
      menuPlus());
    const conseil = G.dossiers.length || !surDepots ? null : el("div", { class: "conseil-gh" },
      icone("folders"), t("Indiquez vos dossiers de projets pour voir quels dépôts sont déjà sur ce PC et pouvoir cloner : "),
      el("button", { class: "btn petit", onclick: reglerDossiers }, "Choisir les dossiers"));
    racine().replaceChildren(...[barre, el("div", { class: "puces sous-gh", id: "sous-gh" }), conseil, el("div", { id: "liste-gh" })].filter(Boolean));
    majPuces();
    dessinerListe();
  }

  function compte(donnees) {
    if (!donnees) return el("span", { class: "nb-gh" }, "…");
    if (donnees.erreur) return el("span", { class: "nb-gh etat-txt rouge", title: donnees.erreur }, "!");
    return el("span", { class: "nb-gh" }, String(donnees.nombre ?? 0));
  }

  function majPuces() {
    const zone = $("#sous-gh");
    if (!zone) return;
    const a = G.actions;
    const echecs = a && !a.erreur ? a.nombre_echecs : 0;
    const badgeActions = !a || a.erreur ? compte(a)
      : echecs ? el("span", { class: "nb-gh etat-txt rouge", title: t(echecs > 1 ? "{n} dépôts en échec : {depots}" : "{n} dépôt en échec : {depots}", { n: echecs, depots: a.echecs.join(", ") }) },
          icone("circle-x"), String(echecs))
      : a.depots.some(d => d.etat === "en_cours") ? el("span", { class: "nb-gh etat-txt ambre", title: "En cours" }, icone("loader"))
      : el("span", { class: "nb-gh etat-txt vert", title: "Tous les derniers runs ont réussi." }, icone("check"));
    const puce = (cle, libelle, badge) => el("button", {
      class: "puce" + (G.sous === cle ? " actif" : ""),
      onclick: () => { if (G.sous !== cle) { G.sous = cle; G.recherche = ""; dessiner(); } } }, libelle, badge);
    zone.replaceChildren(
      puce("depots", "Dépôts", el("span", { class: "nb-gh" }, String(G.depots ? G.depots.length : "…"))),
      puce("prs", "Pull requests", compte(G.prs)),
      puce("issues", "Issues", compte(G.issues)),
      puce("actions", "Actions", badgeActions));
  }

  function dessinerListe() {
    const zone = $("#liste-gh");
    if (!zone) return;
    if (G.sous === "prs") return zone.replaceChildren(...vuePRs());
    if (G.sous === "issues") return zone.replaceChildren(...vueIssues());
    if (G.sous === "actions") return zone.replaceChildren(...vueActions());
    const liste = visibles();
    zone.replaceChildren(liste.length
      ? el("div", { class: "lignes" }, liste.map(ligneDepot))
      : el("div", { class: "vide" }, G.depots.length ? "Aucun dépôt ne correspond." : "Aucun dépôt sur ce compte pour l'instant."));
  }

  const correspond = (...textes) => { const q = G.recherche.trim().toLowerCase(); return !q || textes.join(" ").toLowerCase().includes(q); };

  function visibles() {
    return G.depots.filter(d => correspond(d.complet, d.description, d.langue) &&
      (G.filtre === "tous" || (G.filtre === "prive" && d.prive) || (G.filtre === "public" && !d.prive) ||
       (G.filtre === "local" && d.local) || (G.filtre === "absent" && !d.local)));
  }

  /** En attente, ou l'erreur du serveur ; null quand les données sont là. */
  function etatChargement(donnees) {
    if (!donnees) return [el("div", { class: "attente-gh" }, attente("Lecture…"))];
    if (donnees.erreur) return [erreur(donnees.erreur)];
    return null;
  }

  /** « nom », précédé du propriétaire (atténué) quand ce n'est pas votre compte. */
  function nomDepot(complet) {
    const [proprio, nom] = complet.includes("/") ? complet.split("/") : ["", complet];
    const autre = proprio && proprio.toLowerCase() !== (G.etat.login || "").toLowerCase();
    return el("span", { title: complet }, autre ? el("span", { class: "proprio-gh" }, brut(proprio + " / ")) : null, brut(nom));
  }

  /** Petit indicateur « sur ce PC » (le chemin au survol), ou une place vide
     de même largeur : les dates restent alignées. */
  const surCePC = chemin => chemin
    ? el("span", { class: "local-gh", title: t("Sur ce PC : {chemin}", { chemin }) }, icone("laptop"))
    : el("span", { class: "local-gh" });

  const bouton = (nom, titre, faire) => el("button", { class: "icone-btn", title: titre, onclick: faire }, icone(nom));

  // -- dépôts --------------------------------------------------------------------
  function ligneDepot(d) {
    const actions = d.local
      ? [bouton("folder-open", "Ouvrir le dossier", () => action("ouvrir_dossier", { chemin: d.local }, t("Dossier ouvert"))),
         bouton("code", "Ouvrir dans VS Code", () => action("vscode", { chemin: d.local }, t("VS Code s'ouvre…")))]
      : [bouton("download", "Copier le dépôt sur ce PC", () => cloner(d))];
    actions.push(bouton("external-link", "Ouvrir la page du dépôt sur GitHub", () => ouvrirPage(d.url)));
    // Une seule information sous le nom : la description, sinon le langage.
    const meta = d.description
      ? el("div", { class: "ligne-meta", title: d.description }, brut(d.description))
      : d.langue ? el("div", { class: "ligne-meta" }, langue(d.langue)) : null;
    return el("div", { class: "ligne" },
      el("span", { class: "ligne-ic", title: d.langue || "" }, icone("book-open")),
      el("div", { class: "ligne-corps" },
        el("div", { class: "ligne-titre" }, nomDepot(d.complet),
          d.prive ? el("span", { class: "tag" }, "Privé") : null,
          d.archive ? el("span", { class: "tag" }, "Archivé") : null,
          d.fork ? el("span", { class: "tag" }, "Fork") : null),
        meta),
      el("div", { class: "ligne-cote" },
        d.description && d.langue ? langue(d.langue, "col-langue") : el("span", { class: "col-langue" }),
        surCePC(d.local),
        quand(d.maj)),
      el("div", { class: "ligne-actions depot-gh" }, actions));
  }

  const langue = (nom, classe = "") => el("span", { class: ("langue-gh " + classe).trim(), style: `--c:${COULEURS_LANGUES[nom] || "var(--gris)"}` }, brut(nom));

  // -- pull requests et issues -------------------------------------------------------
  /** Étiquette GitHub : neutre, avec un petit point de sa couleur. */
  function etiquette(e) {
    const c = /^[0-9a-f]{6}$/i.test(e.couleur) ? "#" + e.couleur : "var(--gris)";
    return el("span", { class: "tag" }, el("span", { class: "pt-gh", style: `background:${c}` }), brut(e.nom));
  }

  function ligneSuivi(x, nomIcone) {
    return el("div", { class: "ligne" + (x.brouillon ? " brouillon" : "") },
      el("span", { class: "ligne-ic" }, icone(nomIcone)),
      el("div", { class: "ligne-corps" },
        el("div", { class: "ligne-titre" },
          el("span", { title: x.titre }, brut(x.titre)),
          el("span", { class: "num-gh" }, brut("#" + x.numero)),
          x.brouillon ? el("span", { class: "tag" }, "Brouillon") : null,
          (x.etiquettes || []).slice(0, 3).map(etiquette)),
        el("div", { class: "ligne-meta" }, nomDepot(x.depot), sep(), brut(t("par {auteur}", { auteur: x.auteur })))),
      el("div", { class: "ligne-cote" },
        el("span", { class: "info-gh col-com" }, x.commentaires ? [icone("message-square"), String(x.commentaires)] : null),
        quand(x.date)),
      el("div", { class: "ligne-actions" }, bouton("external-link", "Ouvrir sur GitHub", () => ouvrirPage(x.url))));
  }

  function bloc(titre, liste, total, vide, nomIcone) {
    const filtres = liste.filter(x => correspond(x.depot, x.titre, x.auteur, ...(x.etiquettes || []).map(e => e.nom)));
    return el("div", { class: "lignes" },
      el("div", { class: "titre-lignes" }, titre, el("span", { class: "nb-gh" }, String(total)),
        total > liste.length ? el("span", { class: "plus-gh-n" }, brut(t("{n} affichées sur {total}", { n: liste.length, total }))) : null),
      filtres.length ? filtres.map(x => ligneSuivi(x, nomIcone))
        : el("div", { class: "rien-gh" }, liste.length ? "Rien ne correspond." : vide));
  }

  function vuePRs() {
    const p = G.prs;
    return etatChargement(p) || [
      bloc("Revue demandée", p.revues, p.nb_revues, "Aucune revue en attente.", "eye"),
      bloc("Mes pull requests ouvertes", p.miennes, p.nb_miennes, "Aucune pull request ouverte.", "git-pull-request")];
  }

  function vueIssues() {
    const r = G.issues;
    return etatChargement(r) || [bloc("Issues ouvertes qui vous sont assignées", r.issues, r.nombre, "Aucune issue ne vous est assignée.", "target")];
  }

  // -- GitHub Actions ------------------------------------------------------------------
  function ligneRun(d) {
    const e = infoEtat(d.etat);
    const autres = (d.workflows || []).filter(w => w.workflow !== d.workflow);
    return el("div", { class: "ligne" },
      el("span", { class: "ligne-ic etat-txt " + e.couleur, title: e.libelle }, icone(e.icone, d.etat === "en_cours" ? "tourne-gh" : "")),
      el("div", { class: "ligne-corps" },
        el("div", { class: "ligne-titre" }, nomDepot(d.complet)),
        el("div", { class: "ligne-meta", title: d.titre || "" },
          brut(`${d.workflow}${d.numero ? " #" + d.numero : ""}`), sep(), brut(t("branche {branche}", { branche: d.branche })))),
      el("div", { class: "ligne-cote" },
        // Les autres workflows du dépôt : une petite icône d'état chacun.
        autres.map(w => el("button", { class: "wf-gh etat-txt " + infoEtat(w.etat).couleur,
          title: `${w.workflow} · ${t(infoEtat(w.etat).libelle)} · ${dateLongue(w.date)}`, onclick: () => ouvrirPage(w.lien) }, icone(infoEtat(w.etat).icone))),
        surCePC(d.local),
        quand(d.date)),
      el("div", { class: "ligne-actions" },
        el("button", { class: "btn petit discret", onclick: () => ouvrirPage(d.lien) }, ic("external-link"), t("Voir le run")),
        bouton("book-open", "Ouvrir la page du dépôt", () => ouvrirPage(d.url))));
  }

  function vueActions() {
    const a = G.actions;
    const chargement = etatChargement(a);
    if (chargement) return chargement;
    const filtres = a.depots.filter(d => correspond(d.complet, d.workflow, d.titre));
    const avecRuns = filtres.filter(d => !["aucun", "inconnu"].includes(d.etat));
    const sans = filtres.filter(d => d.etat === "aucun").map(d => d.complet);
    const illisibles = filtres.filter(d => d.etat === "inconnu").map(d => d.complet);
    const enCours = a.depots.filter(d => d.etat === "en_cours").length;
    const n = a.nombre_echecs;
    // Une seule ligne discrète en haut : échecs, sinon runs en cours, sinon tout va bien.
    const bandeau = (couleur, nom, texte) => el("div", { class: "bandeau-gh etat-txt " + couleur }, icone(nom), brut(texte));
    const resume = n ? bandeau("rouge", "circle-x", t(n > 1 ? "{n} dépôts en échec : {depots}" : "{n} dépôt en échec : {depots}", { n, depots: a.echecs.join(", ") }))
      : enCours ? bandeau("ambre", "loader", t(enCours > 1 ? "{n} runs en cours…" : "{n} run en cours…", { n: enCours }))
      : avecRuns.length ? bandeau("vert", "circle-check", t("Tous les derniers runs ont réussi.")) : null;
    const heure = a.heure ? new Date(a.heure).toLocaleTimeString(I18N.locale(), { hour: "2-digit", minute: "2-digit" }) : "";
    return [
      resume,
      avecRuns.length ? el("div", { class: "lignes" }, avecRuns.map(ligneRun))
        : el("div", { class: "vide" }, a.depots.length && G.recherche.trim() ? "Rien ne correspond." : "Aucun run GitHub Actions sur vos dépôts récents."),
      el("div", { class: "notes-gh" },
        sans.length ? el("div", { class: "note-gh" }, brut(t("Sans workflow : {depots}", { depots: sans.join(", ") }))) : null,
        illisibles.length ? el("div", { class: "note-gh" }, brut(t("Illisibles (Actions désactivé ou accès refusé) : {depots}", { depots: illisibles.join(", ") }))) : null,
        el("div", { class: "note-gh" }, brut(t("Dernier run de la branche par défaut, pour vos 15 dépôts les plus récents et ceux de ce PC. Vérifié à {heure}.", { heure }))))]
      .filter(Boolean);
  }

  async function action(nom, donnees, message) {
    try { await api("/api/github/" + nom, donnees); if (message) toast(message, "succes"); }
    catch (e) { toast(e.message, "erreur", 6000); }
  }
  const ouvrirPage = url => action("ouvrir_page", { url });

  // -- connexion ---------------------------------------------------------------
  function ecranConnexion() {
    G.depots = null; G.prs = G.issues = G.actions = null;
    const bouton = el("button", { class: "btn principal", onclick: () => connecter(bouton) }, ic("git-branch"), t("Connecter GitHub"));
    racine().replaceChildren(el("div", { class: "carte connexion-gh" },
      el("div", { class: "gros-gh" }, icone("git-branch")),
      el("h3", {}, "Connecter votre compte GitHub"),
      el("p", { style: "color:var(--doux);margin-top:0" }, "Une seule fois. Aucun mot de passe à saisir ici : GitHub vous montre une page où valider un code."),
      el("ol", {},
        el("li", {}, "Cliquez sur « Connecter GitHub » : un code de 8 caractères s'affiche et est copié."),
        el("li", {}, "La page github.com/login/device s'ouvre : collez le code, puis cliquez sur ", el("b", {}, "Authorize"), "."),
        el("li", {}, "Revenez ici : vos dépôts s'affichent tout seuls.")),
      el("p", { class: "cx-note" }, icone("lock"), t(selonSysteme("L'accès est rangé dans le coffre de Windows (Gestionnaire d'identification), jamais dans un fichier.",
        "L'accès est rangé dans le trousseau du bureau (GNOME Keyring, KWallet), jamais dans un fichier."))),
      el("div", { class: "actions" }, bouton)));
  }

  async function connecter(bouton) {
    bouton.disabled = true;
    let r;
    try { r = await api("/api/github/connexion/debut", {}); }
    catch (e) { toast(e.message, "erreur", 9000); bouton.disabled = false; return; }
    finally { bouton.disabled = false; }
    try { await navigator.clipboard.writeText(r.code); } catch {}
    const etat = el("p", { class: "etat-attente-gh" }, attente("En attente de votre validation sur GitHub…"));
    const finir = (nom, texte) => etat.replaceChildren(icone(nom), brut(texte));
    fenetre([
      el("div", { class: "gros" }, icone("key-round")),
      el("h3", {}, "Validez ce code sur GitHub"),
      el("div", { class: "code-gh" }, brut(r.code)),
      el("p", {}, "Il est déjà copié : collez-le sur la page github.com/login/device qui vient de s'ouvrir, puis cliquez sur Authorize."),
      etat,
      el("div", { class: "actions" },
        el("button", { class: "btn", onclick: async () => { try { await navigator.clipboard.writeText(r.code); toast(t("Code copié"), "succes"); } catch {} } }, ic("clipboard"), t("Copier")),
        el("button", { class: "btn", onclick: () => ouvrirPage(r.adresse) }, ic("external-link"), t("Rouvrir la page")),
        el("button", { class: "btn", onclick: fermer }, "Annuler"))], true);
    const fin = Date.now() + r.expire_dans * 1000;
    while (Date.now() < fin && $("#voile").classList.contains("visible")) {
      await new Promise(ok => setTimeout(ok, 2000));
      if (!$("#voile").classList.contains("visible")) return;
      let s;
      try { s = await api("/api/github/connexion/suite", {}); }
      catch (e) { finir("circle-x", e.message); return; }
      if (s.etat === "connecte") { fermer(); toast(t("GitHub connecté : {login}", { login: s.login }), "succes"); afficher(true); return; }
      if (s.etat === "refuse") { finir("circle-x", t("Accès refusé sur GitHub.")); return; }
      if (s.etat === "expire" || s.etat === "aucune") { finir("clock", t("Le code a expiré : fermez et recommencez.")); return; }
    }
  }

  async function deconnecter() {
    const oui = await confirmer(icone("log-out"), "Déconnecter GitHub ?",
      "L'accès est retiré de ce PC. Pour le révoquer aussi chez GitHub : Settings > Applications > Authorized OAuth Apps.", "Déconnecter");
    if (!oui) return;
    await action("deconnexion", {}, t("GitHub déconnecté"));
    afficher(true);
  }

  // -- dossiers de projets -----------------------------------------------------
  function reglerDossiers() {
    let dossiers = [...G.dossiers];
    const liste = el("div", { class: "dossiers-gh" });
    const dessinerDossiers = () => liste.replaceChildren(...(dossiers.length
      ? dossiers.map((c, i) => el("div", {}, icone("folder"), el("span", { title: c }, brut(c)),
          el("button", { class: "icone-btn", title: "Retirer", onclick: () => { dossiers.splice(i, 1); dessinerDossiers(); } }, icone("x"))))
      : [el("p", {}, "Aucun dossier pour l'instant.")]));
    const champ = el("input", { placeholder: "ex. D:\\Projets", spellcheck: "false" });
    const ajouter = () => {
      const v = champ.value.trim().replace(/^"|"$/g, "");
      if (v && !dossiers.includes(v)) dossiers.push(v);
      champ.value = ""; dessinerDossiers(); champ.focus();
    };
    champ.addEventListener("keydown", e => { if (e.key === "Enter") ajouter(); });
    const enregistrer = el("button", { class: "btn principal", onclick: async () => {
      if (champ.value.trim()) ajouter();
      try {
        const r = await api("/api/github/dossiers", { dossiers });
        G.dossiers = r.dossiers; fermer(); toast(t("Dossiers enregistrés"), "succes"); afficher(true);
      } catch (e) { toast(e.message, "erreur", 6000); }
    } }, "Enregistrer");
    dessinerDossiers();
    fenetre([
      el("div", { class: "gros" }, icone("folders")),
      el("h3", {}, "Dossiers de projets"),
      el("p", {}, "L'outil y cherche vos dépôts déjà présents sur ce PC (le dossier et ses sous-dossiers directs), et y clone les nouveaux."),
      liste,
      el("div", { class: "ajout-gh" }, champ, el("button", { class: "btn", onclick: ajouter }, "Ajouter")),
      el("div", { class: "actions" }, el("button", { class: "btn", onclick: fermer }, "Annuler"), enregistrer)]);
    champ.focus();
  }

  // -- cloner ------------------------------------------------------------------
  function cloner(d) {
    if (!G.dossiers.length) { reglerDossiers(); return; }
    const choix = el("select", {}, G.dossiers.map(c => el("option", { value: c }, brut(c))));
    const destination = el("small", {});
    const maj = () => { destination.textContent = t("Destination : {chemin}", { chemin: `${choix.value.replace(/[\\/]+$/, "")}\\${d.nom}` }); };
    choix.addEventListener("change", maj); maj();
    const libelle = () => [ic("download"), t("Cloner")];
    const bouton = el("button", { class: "btn principal", onclick: async () => {
      bouton.disabled = true;
      bouton.replaceChildren(...attente("Clonage…"));
      try {
        const r = await api("/api/github/cloner", { complet: d.complet, dossier: choix.value });
        fermer(); toast(t("{nom} cloné dans {chemin}", { nom: d.nom, chemin: r.chemin }), "succes", 5000); afficher(true);
      } catch (e) { toast(e.message, "erreur", 8000); bouton.disabled = false; bouton.replaceChildren(...libelle()); }
    } }, libelle());
    fenetre([
      el("div", { class: "gros" }, icone("download")),
      el("h3", {}, brut(t("Cloner « {nom} »", { nom: d.nom }))),
      el("label", { class: "champ" }, "Dans le dossier", choix, destination),
      el("div", { class: "actions" }, el("button", { class: "btn", onclick: fermer }, "Annuler"), bouton)]);
  }

  // -- nouveau dépôt -----------------------------------------------------------
  function taille(o) {
    const [u0, u1, u2] = I18N.langue === "en" ? ["B", "KB", "MB"] : ["o", "Ko", "Mo"];
    const nombre = (x, chiffres) => x.toLocaleString(I18N.locale(), { maximumFractionDigits: chiffres });
    return o < 1024 ? `${o} ${u0}` : o < 1048576 ? `${nombre(o / 1024, 0)} ${u1}` : `${nombre(o / 1048576, 1)} ${u2}`;
  }

  function nouveauDepot() {
    const dossier = el("input", { placeholder: "ex. D:\\Projets\\mon-projet", spellcheck: "false" });
    const nom = el("input", { placeholder: "ex. mon-projet", spellcheck: "false" });
    const description = el("input", { placeholder: "Une phrase sur le projet (facultatif)" });
    const prive = el("input", { type: "radio", name: "visibilite-gh", checked: "" });
    const public_ = el("input", { type: "radio", name: "visibilite-gh" });
    const bilan = el("div");
    let apercu = null;
    const accord = el("input", { type: "checkbox" });
    const libelleEnvoyer = () => [ic("send"), t("Créer et envoyer")];
    const envoyer = el("button", { class: "btn principal", disabled: "", onclick: creer }, libelleEnvoyer());
    const verifier = el("button", { class: "btn", onclick: lireApercu }, ic("search"), t("Vérifier le contenu"));
    dossier.addEventListener("input", () => { apercu = null; envoyer.disabled = true; bilan.replaceChildren(); });
    accord.addEventListener("change", () => { envoyer.disabled = !apercu || !accord.checked; });
    const listeFichiers = fichiers => el("ul", {}, fichiers.map(f => el("li", {}, el("code", {}, brut(f)))));

    async function lireApercu() {
      verifier.disabled = true; envoyer.disabled = true;
      bilan.replaceChildren(el("p", { class: "etat-attente-gh" }, attente("Lecture du dossier…")));
      try {
        const a = await api("/api/github/apercu", { dossier: dossier.value });
        if (a.deja_relie) {
          apercu = null;
          bilan.replaceChildren(el("div", { class: "bilan-gh danger" }, brut(t("Ce dossier est déjà relié à {depot}.", { depot: a.deja_relie }))));
          return;
        }
        apercu = a;
        dossier.value = a.dossier;
        if (!nom.value.trim()) nom.value = a.nom_suggere;
        const blocs = [el("div", { class: "bilan-gh" },
          el("b", {}, brut(t(a.nombre > 1 ? "{n} fichiers · {taille}" : "{n} fichier · {taille}", { n: a.nombre, taille: taille(a.taille) }))),
          " (les fichiers listés dans .gitignore sont exclus)",
          el("ul", {}, a.exemples.map(f => el("li", {}, el("code", {}, brut(f)))), a.nombre > a.exemples.length ? el("li", {}, "…") : null))];
        if (a.modifs_non_enregistrees) blocs.push(el("div", { class: "bilan-gh" }, ic("info"), t("Ce dossier a des modifications non enregistrées (commit) : elles ne seront pas envoyées.")));
        if (a.lourds.length) blocs.push(el("div", { class: "bilan-gh" }, ic("triangle-alert"), t("Fichiers lourds (plus de 50 Mo) :"), listeFichiers(a.lourds)));
        if (a.trop_gros.length) blocs.push(el("div", { class: "bilan-gh danger" }, ic("octagon-x"), t("GitHub refuse les fichiers de plus de 100 Mo. Ajoutez-les à .gitignore :"), listeFichiers(a.trop_gros)));
        const risque = a.sensibles.length > 0;
        if (risque) blocs.push(el("div", { class: "bilan-gh danger" }, ic("lock"), t("Fichiers qui contiennent souvent des mots de passe ou des clés :"),
          listeFichiers(a.sensibles),
          "Ajoutez-les à .gitignore puis vérifiez à nouveau, ou cochez ci-dessous si vous êtes sûr."));
        if (risque) blocs.push(el("label", { class: "choix-gh" }, accord, "J'ai vérifié : ces fichiers peuvent être envoyés"));
        bilan.replaceChildren(...blocs);
        accord.checked = false;
        envoyer.disabled = a.trop_gros.length > 0 || risque;
      } catch (e) {
        apercu = null;
        bilan.replaceChildren(el("div", { class: "bilan-gh danger" }, ic("circle-x"), brut(e.message)));
      } finally { verifier.disabled = false; }
    }

    async function creer() {
      if (!apercu) return;
      if (public_.checked && !(await confirmerPublic())) return;
      envoyer.disabled = true; verifier.disabled = true;
      envoyer.replaceChildren(...attente("Envoi…"));
      try {
        const r = await api("/api/github/creer", { dossier: dossier.value, nom: nom.value, description: description.value, prive: prive.checked });
        fenetre([
          el("div", { class: "gros" }, icone("circle-check")),
          el("h3", {}, "Dépôt créé et envoyé"),
          el("p", {}, brut(t(r.nombre > 1 ? "{n} fichiers envoyés sur {depot}." : "{n} fichier envoyé sur {depot}.", { n: r.nombre, depot: r.complet }))),
          el("div", { class: "actions" },
            el("button", { class: "btn", onclick: () => ouvrirPage(r.url) }, ic("external-link"), t("Voir sur GitHub")),
            el("button", { class: "btn principal", onclick: () => { fermer(); afficher(true); } }, "OK"))], true);
      } catch (e) {
        toast(e.message, "erreur", 12000);
        envoyer.disabled = false; verifier.disabled = false; envoyer.replaceChildren(...libelleEnvoyer());
      }
    }

    // La fenêtre de confirmation remplace celle du formulaire : on garde ses
    // éléments pour la réafficher ensuite.
    let formulaire;
    async function confirmerPublic() {
      const oui = await confirmer(icone("globe"), "Dépôt public ?", "Tout le monde pourra voir ces fichiers sur GitHub.", "Oui, public");
      fenetre(formulaire);
      return oui;
    }

    formulaire = [
      el("div", { class: "gros" }, icone("plus")),
      el("h3", {}, "Nouveau dépôt GitHub"),
      el("p", {}, "Crée le dépôt sur votre compte et y envoie le contenu d'un dossier de ce PC."),
      el("label", { class: "champ" }, "Dossier à envoyer", dossier),
      el("label", { class: "champ" }, "Nom du dépôt", nom),
      el("label", { class: "champ" }, "Description", description),
      el("div", { class: "choix-gh" },
        el("label", {}, prive, icone("lock"), t("Privé")),
        el("label", {}, public_, icone("globe"), t("Public"))),
      bilan,
      el("div", { class: "actions" }, el("button", { class: "btn", onclick: fermer }, "Annuler"), verifier, envoyer)];
    fenetre(formulaire);
    dossier.focus();
  }

  VUES.github = { afficher, titre: "GitHub", icone: icone("git-branch"), groupe: "dev", ordre: 20 };
})();
