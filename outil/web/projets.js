"use strict";
/* Onglet « Projets » : les projets de développement de ce PC, leurs serveurs
   de dev (démarrer, arrêter, journal), leur état Git et leurs fichiers .env
   (sauvegardés dans le coffre chiffré). Voir projets.py.

   Affichage en lignes compactes : une ligne par projet (nom, type, branche et
   état Git en texte court), un clic déplie le détail (chemin, commandes,
   .env, fetch, masquer). Un seul projet ouvert à la fois. */
(() => {
  I18N.ajouter({
    "Aucune commande de dev": "No dev command",
    "Pas de branche distante : rien à comparer": "No remote branch: nothing to compare",
    "Pas de dépôt Git": "No Git repository",
    "Lecture de l'état Git…": "Reading Git status…",
    "Projets": "Projects",
    "Rechercher un projet…": "Search a project…",
    "Tous": "All",
    "En marche": "Running",
    "Démarrage…": "Starting…",
    "À envoyer": "To push",
    "Modifiés": "Changed",
    "En retard": "Behind",
    "Masqués": "Hidden",
    "Masqué": "Hidden",
    "Ajouter un projet": "Add a project",
    "Choisir le dossier du projet": "Choose the project folder",
    "Projet ajouté": "Project added",
    "Tout vérifier": "Check all",
    "Vérification…": "Checking…",
    "Récupère les nouveautés de tous les dépôts (git fetch)": "Fetch news from all repositories (git fetch)",
    "Relire": "Reload",
    "Lecture des projets…": "Reading projects…",
    "Aucun projet trouvé pour l'instant.": "No project found yet.",
    "Indiquez vos dossiers de projets dans les Réglages : l'outil y cherche les dossiers qui contiennent un projet (.git, package.json, manage.py…).":
      "Set your project folders in Settings: the tool looks there for folders that contain a project (.git, package.json, manage.py…).",
    "Ouvrir les Réglages": "Open Settings",
    "Aucun projet ne correspond.": "No project matches.",
    "Dossier": "Folder",
    "VS Code": "VS Code",
    "Terminal": "Terminal",
    "Commandes": "Commands",
    "Ouvrir le dossier": "Open the folder",
    "Ouvrir dans VS Code": "Open in VS Code",
    "Ouvrir un terminal dans le dossier": "Open a terminal in the folder",
    "Serveurs de dev et autres commandes": "Dev servers and other commands",
    "Fichiers .env": ".env files",
    "Fichiers .env ↔ coffre": ".env files ↔ vault",
    "Récupérer (fetch)": "Fetch",
    "Masquer": "Hide",
    "Afficher": "Show",
    "Masquer ce projet": "Hide this project",
    "Afficher ce projet": "Show this project",
    "Retirer de la liste": "Remove from the list",
    "Projet masqué": "Project hidden",
    "Projet de nouveau affiché": "Project shown again",
    "Retirer ce projet ?": "Remove this project?",
    "Il disparaît de la liste. Le dossier n'est pas touché.": "It disappears from the list. The folder is not touched.",
    "Retirer": "Remove",
    "Dossier ouvert": "Folder opened",
    "VS Code s'ouvre…": "VS Code is opening…",
    "Terminal ouvert": "Terminal opened",
    "Ajouté à la main": "Added manually",
    // Git
    "à jour": "up to date",
    "local": "local",
    "{n} à envoyer": "{n} to push",
    "{n} à récupérer": "{n} to pull",
    "{n} modifié": "{n} changed",
    "{n} modifiés": "{n} changed",
    "{n} non suivi": "{n} untracked",
    "{n} non suivis": "{n} untracked",
    "{n} conflit": "{n} conflict",
    "{n} conflits": "{n} conflicts",
    "fetch en échec": "fetch failed",
    "erreur Git": "Git error",
    "pas de branche distante": "no remote branch",
    "aucun commit": "no commit",
    "HEAD détachée": "detached HEAD",
    "Commits à envoyer (push)": "Commits to push",
    "Commits à récupérer (pull)": "Commits to pull",
    "Fichiers modifiés ou nouveaux": "Changed or new files",
    "Récupération…": "Fetching…",
    "{nom} : à jour": "{nom}: up to date",
    "{nom} : {n} commit(s) à récupérer": "{nom}: {n} commit(s) to pull",
    "{n} dépôts vérifiés": "{n} repositories checked",
    "{n} dépôts vérifiés, {e} en erreur": "{n} repositories checked, {e} with errors",
    "Vérifié à {h}": "Checked at {h}",
    // Commandes
    "Démarrer": "Start",
    "Arrêter": "Stop",
    "Redémarrer": "Restart",
    "Journal": "Logs",
    "Ouvrir le site": "Open the site",
    "en marche": "running",
    "démarrage…": "starting…",
    "arrêté": "stopped",
    "port occupé": "port in use",
    "Le port répond, mais le programme n'a pas été lancé par Mes outils.": "The port answers, but the program was not started by Mes outils.",
    "arrêté (code {c})": "stopped (code {c})",
    "{nom} démarre…": "{nom} is starting…",
    "{nom} arrêté": "{nom} stopped",
    "Arrêter « {nom} » ?": "Stop “{nom}”?",
    "Le processus lancé par Mes outils et tous ses sous-processus sont arrêtés.": "The process started by Mes outils and all its subprocesses are stopped.",
    "{n} commande proposée": "{n} suggested command",
    "{n} commandes proposées": "{n} suggested commands",
    "Configurer": "Set up",
    "Commandes de « {nom} »": "Commands of “{nom}”",
    "Chaque commande est lancée dans le dossier du projet, sans fenêtre. Sa sortie va dans le journal.":
      "Each command runs in the project folder, without a window. Its output goes to the logs.",
    "Nom": "Name",
    "Commande": "Command",
    "Port": "Port",
    "Adresse": "Address",
    "ex. npm run dev": "e.g. npm run dev",
    "ex. Front": "e.g. Front",
    "ex. 5173": "e.g. 5173",
    "ex. http://localhost:5173": "e.g. http://localhost:5173",
    "Supprimer": "Delete",
    "Ajouter une commande": "Add a command",
    "Proposées d'après le projet :": "Suggested from the project:",
    "Aucune commande pour l'instant.": "No command yet.",
    "Annuler": "Cancel",
    "Enregistrer": "Save",
    "Commandes enregistrées": "Commands saved",
    "Journal de {nom}": "Logs of {nom}",
    "300 dernières lignes, mises à jour toutes les 2 secondes": "Last 300 lines, refreshed every 2 seconds",
    "Journal vide.": "Empty log.",
    "Copier": "Copy",
    "Lecture…": "Loading…",
    "Fermer": "Close",
    // .env
    "Fichiers .env de « {nom} »": ".env files of “{nom}”",
    "Le contenu est rangé, chiffré, dans le coffre de l'onglet Mots de passe (catégorie « env »).":
      "The content is stored, encrypted, in the vault of the Passwords tab (category “env”).",
    "Sauvegarder dans le coffre": "Save to the vault",
    "Restaurer": "Restore",
    "Aucun fichier .env dans ce projet.": "No .env file in this project.",
    "absent du dossier": "missing from the folder",
    "sauvegardé le {d}": "saved on {d}",
    "pas encore sauvegardé": "not saved yet",
    "Le coffre est verrouillé.": "The vault is locked.",
    "Ouvrez d'abord le coffre dans l'onglet Mots de passe.": "First open the vault in the Passwords tab.",
    "Ouvrir l'onglet Mots de passe": "Open the Passwords tab",
    "{n} fichier(s) sauvegardé(s) dans le coffre": "{n} file(s) saved to the vault",
    "Restaurer {f} ?": "Restore {f}?",
    "Le fichier est réécrit avec la version du coffre. L'ancien est gardé en {f}.bak.":
      "The file is rewritten with the vault version. The old one is kept as {f}.bak.",
    "Le fichier est recréé avec la version du coffre.": "The file is recreated with the vault version.",
    "{f} restauré": "{f} restored",
    // Messages du serveur
    "Projet inconnu.": "Unknown project.",
    "Projet introuvable : le dossier a peut-être été déplacé.": "Project not found: the folder may have been moved.",
    "Dossier introuvable.": "Folder not found.",
    "Commande inconnue.": "Unknown command.",
    "Commande invalide.": "Invalid command.",
    "Donnez un nom à chaque commande.": "Give each command a name.",
    "Liste de commandes invalide.": "Invalid command list.",
    "Adresse invalide : elle doit commencer par http:// ou https://.": "Invalid address: it must start with http:// or https://.",
    "Aucune adresse pour cette commande.": "No address for this command.",
    "Arrêtez d'abord une commande en marche avant de la supprimer.": "Stop a running command before deleting it.",
    "Le dossier du projet est introuvable.": "The project folder was not found.",
    "Cette commande est déjà en marche.": "This command is already running.",
    "Cette commande n'est pas en marche (ou n'a pas été lancée par Mes outils).": "This command is not running (or was not started by Mes outils).",
    "Ce processus n'a pas été lancé par Mes outils : il n'est pas arrêté.": "This process was not started by Mes outils: it is not stopped.",
    "Action inconnue.": "Unknown action.",
    "Ce projet n'est pas un dépôt Git.": "This project is not a Git repository.",
    "Git n'est pas installé sur ce PC.": "Git is not installed on this PC.",
    "Git met trop de temps à répondre.": "Git takes too long to answer.",
    "git a échoué.": "git failed.",
    "git fetch a échoué.": "git fetch failed.",
    "Le serveur Git ne répond pas (délai dépassé).": "The Git server is not responding (timeout).",
    "Serveur Git injoignable ou accès refusé.": "Git server unreachable or access denied.",
    "Accès refusé : connectez-vous une fois avec git dans un terminal.": "Access denied: sign in once with git in a terminal.",
    "Fichier .env invalide.": "Invalid .env file.",
    "Le dossier de ce fichier n'existe plus.": "The folder of this file no longer exists.",
    "VS Code est introuvable sur ce PC.": "VS Code was not found on this PC.",
  });
  I18N.motifs([
    [/^Commande invalide : (.*)$/, "Invalid command: $1"],
    [/^Port invalide : (.*)$/, "Invalid port: $1"],
    [/^Le port (\d+) est déjà utilisé par un autre programme\.$/, "Port $1 is already used by another program."],
    [/^Impossible de lancer la commande : (.*)$/, "Unable to start the command: $1"],
    [/^Fichier introuvable : (.*)$/, "File not found: $1"],
    [/^Fichier trop gros pour le coffre : (.*)$/, "File too big for the vault: $1"],
    [/^Fichier illisible \(pas en UTF-8\) : (.*)$/, "Unreadable file (not UTF-8): $1"],
    [/^Aucune sauvegarde de (.*) dans le coffre\.$/, "No backup of $1 in the vault."],
  ]);

  const style = document.createElement("style");
  style.textContent = `
    /* Lignes : classes communes de hub.html (.lignes, .ligne…) ; ici seulement
       les compléments propres à l'onglet. */
    .pj-barre { margin-bottom: 12px; }
    .pj-puces { margin: 0 0 14px; }
    .pj-puce-n { color: var(--gris); font-variant-numeric: tabular-nums; }
    .puce.actif .pj-puce-n { color: var(--doux); }
    .pj-ligne:focus-visible { outline: 2px solid var(--violet); outline-offset: -2px; border-radius: 0; }
    .pj-ligne .ligne-ic { color: var(--gris); }
    .pj-ligne.ouverte .ligne-ic, .pj-ligne:hover .ligne-ic { color: var(--doux); }
    .pj-ligne.masque .ligne-corps, .pj-ligne.masque .ligne-ic { opacity: .55; }
    .pj-ligne .ligne-meta { display: flex; align-items: center; gap: 0; }
    .pj-ligne .ligne-meta > span { white-space: nowrap; }
    .pj-ligne .ligne-meta .etat-txt { font-size: inherit; }
    .pj-sep { color: var(--gris); padding: 0 6px; }
    .pj-fleche { color: var(--gris); display: grid; place-items: center; width: 16px; flex: none; transition: transform .15s; }
    .pj-fleche svg.ico { margin: 0; width: 14px; height: 14px; }
    .pj-ligne.ouverte .pj-fleche { transform: rotate(90deg); color: var(--doux); }
    .pj-ligne .ligne-actions .icone-btn:hover { background: var(--carte); }
    /* Détail déplié */
    .pj-detail { display: flex; flex-direction: column; gap: 12px; }
    .pj-info { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; font-size: 12.5px; color: var(--doux); min-width: 0; }
    .pj-chemin { font-family: var(--mono); font-size: 12px; color: var(--doux); user-select: text; overflow-wrap: anywhere; }
    .pj-info .etat-txt { font-size: 12.5px; }
    .pj-titre-bloc { font-size: 11.5px; font-weight: 600; color: var(--gris); text-transform: uppercase; letter-spacing: .04em; margin-bottom: 6px; }
    .pj-cmds { background: var(--carte); border: 1px solid var(--ligne); border-radius: 8px; overflow: hidden; }
    .pj-cmd { display: flex; align-items: center; gap: 10px; min-height: 38px; padding: 3px 6px 3px 12px; border-top: 1px solid var(--ligne); min-width: 0; }
    .pj-cmd:first-child { border-top: 0; }
    .pj-cmd .n { font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width: 150px; flex: none; }
    .pj-cmd .c { flex: 1; min-width: 0; font-family: var(--mono); font-size: 12px; color: var(--gris); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .pj-cmd .etat-txt { width: 130px; flex: none; }
    .pj-ligne .ligne-meta .etat-txt, .pj-info .etat-txt { gap: 3px; }
    .pj-ligne .ligne-meta .etat-txt svg.ico, .pj-info .etat-txt svg.ico { width: 12px; height: 12px; margin: 0; stroke-width: 2.2; }
    .pj-cmd .p { font-size: 12.5px; color: var(--doux); font-variant-numeric: tabular-nums; min-width: 48px; }
    .pj-cmd .b { display: flex; gap: 2px; flex: none; width: 94px; }
    .pj-aucune { font-size: 12.5px; color: var(--doux); display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
    .pj-boutons { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
    .pj-boutons .espace { flex: 1; }
    .pj-boutons .btn { box-shadow: none; }
    .pj-tourne svg.ico, svg.ico.pj-tourne { animation: pj-tourne 1s linear infinite; }
    @keyframes pj-tourne { to { transform: rotate(360deg); } }
    /* Fenêtres (commandes, journal, .env) */
    .pj-edit { display: grid; grid-template-columns: 1.1fr 2fr .7fr 1.6fr auto; gap: 6px; align-items: center; margin-bottom: 6px; }
    .pj-edit input { font-size: 13px; min-width: 0; }
    .pj-edit input.mono { font-family: var(--mono); font-size: 12.5px; }
    .pj-entetes { display: grid; grid-template-columns: 1.1fr 2fr .7fr 1.6fr 30px; gap: 6px; font-size: 11.5px; font-weight: 600; color: var(--doux); margin-bottom: 4px; }
    .pj-sugg { display: flex; gap: 6px; flex-wrap: wrap; margin: 8px 0 4px; }
    .pj-sugg button { border: 1px dashed var(--ligne-forte); background: transparent; color: var(--encre); border-radius: 7px; padding: 4px 10px; cursor: pointer; font-size: 12.5px; font-family: var(--mono); display: inline-flex; align-items: center; gap: 6px; }
    .pj-sugg button svg.ico { margin: 0; color: var(--gris); }
    .pj-sugg button:hover { border-color: var(--violet); color: var(--violet); }
    .pj-journal { background: var(--code); color: var(--code-texte); font-family: var(--mono); font-size: 12px; line-height: 1.45; border: 1px solid var(--ligne); border-radius: 8px; padding: 10px 12px; height: min(58vh, 520px); overflow: auto; white-space: pre-wrap; word-break: break-all; margin: 0; text-align: left; }
    .pj-sous { font-size: 12.5px; color: var(--doux); margin: -4px 0 10px; display: flex; gap: 8px; align-items: center; }
    .pj-env { margin: 6px 0 4px; }
    .pj-env .ligne { min-height: 42px; }
    .pj-env code { font-weight: 600; color: var(--encre); }
    .pj-alerte { border: 1px solid var(--ligne); border-left: 3px solid var(--ambre); background: var(--surface); color: var(--encre); border-radius: 8px; padding: 10px 12px; font-size: 13.5px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin-bottom: 10px; }
    .pj-alerte > svg.ico { color: var(--ambre-texte); margin: 0; }
  `;
  document.head.append(style);

  const P = { projets: null, git: {}, filtre: "tous", recherche: "", minuterie: null, verification: false, ouvert: null };
  const racine = () => $("#vue-projets");
  const actif = () => racine()?.classList.contains("actif");
  const heure = iso => iso ? new Date(iso).toLocaleTimeString(I18N.locale(), { hour: "2-digit", minute: "2-digit" }) : "";
  const date = iso => iso ? new Date(iso).toLocaleString(I18N.locale(), { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" }) : "";
  /** Une icône suivie d'un texte (bouton, titre). */
  const avec = (nom, texte) => [icone(nom, "av"), texte];
  const attente = () => icone("loader", "pj-tourne");
  /** Singulier ou pluriel selon n. */
  const pl = (n, un, plusieurs) => t(n > 1 ? plusieurs : un, { n });

  // Icône discrète selon le type principal du projet.
  const ICONE_TYPE = {
    "Odoo": "puzzle", "Django": "server", "Python": "file-code", "React": "atom", "Vue": "layers", "Angular": "hexagon",
    "Next.js": "zap", "Nuxt": "zap", "Vite": "zap", "NestJS": "server", "Tauri": "monitor", "Electron": "monitor",
    "Node": "package", "Docker": "container", "Laravel": "layers", "PHP": "code", "Java": "coffee", "Go": "code",
    "Rust": "cog", ".NET": "hexagon", "Flutter": "smartphone", "Ruby": "gem", "Git": "git-branch",
  };
  const iconeType = p => ICONE_TYPE[p.types[0]] || "folder";

  async function appel(action, donnees, message) {
    try {
      const r = await api("/api/projets/" + action, donnees || {});
      if (message) toast(message, "succes");
      return r;
    } catch (e) { toast(e.message, "erreur", 7000); return null; }
  }

  // -- affichage ---------------------------------------------------------------
  async function afficher() {
    if (!P.projets) racine().replaceChildren(el("div", { class: "vide" }, attente(), "Lecture des projets…"));
    let r;
    try { r = await api("/api/projets/liste", {}); }
    catch (e) { racine().replaceChildren(el("div", { class: "vide" }, icone("triangle-alert"), e.message)); return; }
    P.projets = r.projets;
    P.infos = r;
    if (P.ouvert && !P.projets.some(p => p.id === P.ouvert)) P.ouvert = null;
    dessiner();
    suivre();
    try { Object.assign(P.git, (await api("/api/projets/git/etats", {})).git); dessinerListe(); } catch {}
  }

  /** Tant que l'onglet est affiché : état des commandes toutes les 3 secondes. */
  function suivre() {
    clearInterval(P.minuterie);
    P.minuterie = setInterval(async () => {
      if (!actif()) { clearInterval(P.minuterie); return; }
      let r;
      try { r = await api("/api/projets/etats", {}); } catch { return; }
      let change = false;
      for (const s of r.serveurs) {
        const p = P.projets.find(x => x.id === s.projet_id);
        const c = p?.commandes.find(x => x.id === s.id);
        if (c && c.etat.etat !== s.etat) { c.etat = { etat: s.etat }; change = true; }
      }
      if (change) dessinerListe();
    }, 3000);
  }

  const gitDe = p => P.git[p.id] || null;
  const vivant = c => ["marche", "demarrage"].includes(c.etat.etat);
  const enMarche = p => p.commandes.some(vivant);
  const modifsDe = g => (g?.modifies || 0) + (g?.non_suivis || 0) + (g?.conflits || 0);
  const FILTRES = [
    ["tous", "Tous", p => !p.masque],
    ["marche", "En marche", p => !p.masque && enMarche(p)],
    ["envoi", "À envoyer", p => !p.masque && (gitDe(p)?.avance > 0)],
    ["modifs", "Modifiés", p => !p.masque && modifsDe(gitDe(p)) > 0],
    ["retard", "En retard", p => !p.masque && (gitDe(p)?.retard > 0)],
    ["masques", "Masqués", p => p.masque],
  ];

  function dessiner() {
    const recherche = el("input", { placeholder: "Rechercher un projet…", value: P.recherche,
      oninput: e => { P.recherche = e.target.value; dessinerListe(); } });
    const verifier = el("button", { class: "btn", id: "pj-verifier", title: "Récupère les nouveautés de tous les dépôts (git fetch)", onclick: toutVerifier },
      P.verification ? [icone("loader", "av pj-tourne"), t("Vérification…")] : avec("download", "Tout vérifier"));
    verifier.disabled = P.verification;
    racine().replaceChildren(
      el("div", { class: "barre-vue pj-barre" },
        el("h2", {}, icone("package"), t("Projets"), el("span", { class: "compte" }, String(P.projets.filter(p => !p.masque).length))),
        el("div", { class: "champ-recherche" }, el("span", {}, icone("search")), recherche),
        el("div", { class: "espace" }),
        el("button", { class: "icone-btn", title: "Relire", onclick: afficher }, icone("refresh-cw")),
        verifier,
        el("button", { class: "btn principal", onclick: ajouterProjet }, avec("plus", "Ajouter un projet"))),
      el("div", { class: "puces pj-puces", id: "pj-puces" }),
      el("div", { id: "pj-zone" }));
    dessinerListe();
  }

  function dessinerListe() {
    const puces = $("#pj-puces"), zone = $("#pj-zone");
    if (!puces || !zone) return;
    puces.replaceChildren(...FILTRES.filter(([v, , f]) => v !== "masques" || P.projets.some(f)).map(([v, libelle, f]) => {
      const n = P.projets.filter(f).length;
      return el("button", { class: "puce" + (P.filtre === v ? " actif" : ""), onclick: () => { P.filtre = v; dessinerListe(); } },
        libelle, v !== "tous" && n ? el("span", { class: "pj-puce-n" }, String(n)) : null);
    }));
    if (!P.projets.length) {
      zone.replaceChildren(el("div", { class: "vide" },
        icone("folder"),
        el("p", { style: "margin-top:0" }, "Aucun projet trouvé pour l'instant."),
        el("p", {}, "Indiquez vos dossiers de projets dans les Réglages : l'outil y cherche les dossiers qui contiennent un projet (.git, package.json, manage.py…)."),
        el("button", { class: "btn principal", onclick: () => montrerVue("reglages") }, "Ouvrir les Réglages")));
      return;
    }
    const filtre = (FILTRES.find(f => f[0] === P.filtre) || FILTRES[0])[2];
    const q = P.recherche.trim().toLowerCase();
    const liste = P.projets.filter(filtre).filter(p => !q || `${p.nom} ${p.chemin} ${p.types.join(" ")} ${gitDe(p)?.branche || ""}`.toLowerCase().includes(q));
    zone.replaceChildren(liste.length
      ? el("div", { class: "lignes" }, liste.flatMap(p => P.ouvert === p.id ? [ligne(p), detail(p)] : [ligne(p)]))
      : el("div", { class: "vide" }, "Aucun projet ne correspond."));
  }

  function basculer(p) {
    P.ouvert = P.ouvert === p.id ? null : p.id;
    dessinerListe();
    const l = $(`#pj-zone .pj-ligne[data-id="${CSS.escape(p.id)}"]`);
    if (l) l.focus({ preventScroll: true });
  }

  // -- ligne -------------------------------------------------------------------
  /** État Git en texte court : « main · 2 modifiés · ↑2 à envoyer ». */
  function metaGit(p) {
    const g = gitDe(p);
    if (!p.git) return [el("span", {}, t("Pas de dépôt Git"))];
    if (!g) return [el("span", {}, t("Lecture de l'état Git…"))];
    if (g.erreur) return [el("span", { class: "etat-txt rouge", title: I18N.traduire(g.erreur) }, t("erreur Git"))];
    const m = [el("span", {}, g.branche || t("HEAD détachée"))];
    const modifs = (g.modifies || 0) + (g.non_suivis || 0);
    if (g.conflits) m.push(el("span", { class: "etat-txt rouge" }, pl(g.conflits, "{n} conflit", "{n} conflits")));
    if (modifs) m.push(el("span", { title: "Fichiers modifiés ou nouveaux" }, pl(modifs, "{n} modifié", "{n} modifiés")));
    if (g.avance) m.push(el("span", { class: "etat-txt ambre", title: "Commits à envoyer (push)" }, icone("arrow-up"), t("{n} à envoyer", { n: g.avance })));
    if (g.retard) m.push(el("span", { class: "etat-txt ambre", title: "Commits à récupérer (pull)" }, icone("arrow-down"), t("{n} à récupérer", { n: g.retard })));
    if (g.erreur_fetch) m.push(el("span", { class: "etat-txt rouge", title: I18N.traduire(g.erreur_fetch) }, t("fetch en échec")));
    if (m.length === 1) {
      if (g.sans_commit) m.push(el("span", {}, t("aucun commit")));
      else if (g.amont) m.push(el("span", { class: "etat-txt gris" }, t("à jour")));
      else m.push(el("span", { class: "etat-txt gris", title: "Pas de branche distante : rien à comparer" }, t("local")));
    }
    return m.flatMap((x, i) => i ? [el("span", { class: "pj-sep" }, "·"), x] : [x]);
  }

  function etatCote(p) {
    const vivantes = p.commandes.filter(vivant);
    if (!vivantes.length) return null;
    const marche = vivantes.some(c => c.etat.etat === "marche");
    return el("span", { class: "etat-txt " + (marche ? "vert" : "ambre"), title: vivantes.map(c => c.nom).join(", ") },
      el("span", { class: "point " + (marche ? "marche" : "demarrage") }), marche ? t("En marche") : t("Démarrage…"));
  }

  /** Boutons d'ouverture (dossier, VS Code, terminal) : icônes seules. */
  function boutonsOuvrir(p) {
    const b = (nom, titre, action, message) => el("button", { class: "icone-btn", title: titre,
      onclick: ev => { ev.stopPropagation(); appel(action, { projet: p.id }, message); } }, icone(nom));
    return [
      b("folder-open", "Ouvrir le dossier", "ouvrir/dossier", "Dossier ouvert"),
      P.infos.vscode ? b("code", "Ouvrir dans VS Code", "ouvrir/vscode", "VS Code s'ouvre…") : null,
      b("terminal", "Ouvrir un terminal dans le dossier", "ouvrir/terminal", "Terminal ouvert")];
  }

  function ligne(p) {
    const ouverte = P.ouvert === p.id;
    return el("div", { class: "ligne cliquable pj-ligne" + (ouverte ? " ouverte" : "") + (p.masque ? " masque" : ""),
        "data-id": p.id, tabindex: "0", role: "button", "aria-expanded": ouverte ? "true" : "false",
        onclick: () => basculer(p),
        onkeydown: ev => { if (ev.target === ev.currentTarget && (ev.key === "Enter" || ev.key === " ")) { ev.preventDefault(); basculer(p); } } },
      el("span", { class: "ligne-ic" }, icone(iconeType(p))),
      el("div", { class: "ligne-corps" },
        el("div", { class: "ligne-titre" }, el("span", {}, p.nom),
          p.types[0] ? el("span", { class: "tag" }, p.types[0]) : null,
          p.masque ? el("span", { class: "tag" }, "Masqué") : null),
        el("div", { class: "ligne-meta" }, metaGit(p))),
      el("div", { class: "ligne-cote" }, etatCote(p)),
      el("div", { class: "ligne-actions" }, boutonsOuvrir(p)),
      el("span", { class: "pj-fleche" }, icone("chevron-right")));
  }

  // -- détail ------------------------------------------------------------------
  /** L'état Git complet, pour le détail. */
  function infosGit(p) {
    const g = gitDe(p);
    if (!p.git || !g || g.erreur) return null;
    const m = [el("span", {}, avec("git-branch", g.branche || t("HEAD détachée")))];
    if (g.sans_commit) m.push(el("span", {}, t("aucun commit")));
    else if (!g.amont) m.push(el("span", {}, t("pas de branche distante")));
    if (g.avance) m.push(el("span", { class: "etat-txt ambre" }, icone("arrow-up"), t("{n} à envoyer", { n: g.avance })));
    if (g.retard) m.push(el("span", { class: "etat-txt ambre" }, icone("arrow-down"), t("{n} à récupérer", { n: g.retard })));
    if (g.modifies) m.push(el("span", {}, pl(g.modifies, "{n} modifié", "{n} modifiés")));
    if (g.non_suivis) m.push(el("span", {}, pl(g.non_suivis, "{n} non suivi", "{n} non suivis")));
    if (g.conflits) m.push(el("span", { class: "etat-txt rouge" }, pl(g.conflits, "{n} conflit", "{n} conflits")));
    if (!g.avance && !g.retard && !modifsDe(g) && g.amont && !g.sans_commit) m.push(el("span", {}, t("à jour")));
    if (g.erreur_fetch) m.push(el("span", { class: "etat-txt rouge" }, icone("triangle-alert"), I18N.traduire(g.erreur_fetch)));
    else if (g.verifie) m.push(el("span", { style: "color:var(--gris)" }, t("Vérifié à {h}", { h: heure(g.verifie) })));
    return el("div", { class: "pj-info" }, m.flatMap((x, i) => i ? [el("span", { class: "pj-sep", style: "padding:0" }, "·"), x] : [x]));
  }

  const LIBELLES = { marche: "en marche", demarrage: "démarrage…", arrete: "arrêté", occupe: "port occupé" };

  function ligneCommande(p, c) {
    const e = c.etat.etat;
    const enRoute = e === "marche" || e === "demarrage";
    const code = e === "arrete" && c.etat.code_sortie;
    const texte = code ? t("arrêté (code {c})", { c: c.etat.code_sortie }) : t(LIBELLES[e] || e);
    const couleur = e === "marche" ? "vert" : e === "demarrage" ? "ambre" : e === "occupe" || code ? "rouge" : "gris";
    return el("div", { class: "pj-cmd" },
      el("span", { class: "n", title: c.nom }, c.nom),
      el("span", { class: "c", title: c.commande }, c.commande),
      el("span", { class: "etat-txt " + couleur, ...(e === "occupe" ? { title: "Le port répond, mais le programme n'a pas été lancé par Mes outils." } : {}) },
        enRoute || e === "occupe" ? el("span", { class: "point " + e }) : null, texte),
      el("span", { class: "p" }, c.port ? `:${c.port}` : ""),
      el("span", { class: "b" },
        enRoute
          ? el("button", { class: "icone-btn stop", title: "Arrêter", onclick: () => arreter(p, c) }, icone("square"))
          : el("button", { class: "icone-btn go", title: "Démarrer", disabled: e === "occupe", onclick: () => demarrer(p, c) }, icone("play")),
        el("button", { class: "icone-btn", title: "Journal", onclick: () => journal(p, c) }, icone("scroll-text")),
        c.url ? el("button", { class: "icone-btn", title: "Ouvrir le site", disabled: !(e === "marche" || e === "occupe"),
          onclick: () => appel("ouvrir/site", { projet: p.id, commande: c.id }) }, icone("external-link")) : null));
  }

  function detail(p) {
    const cmds = p.commandes.length
      ? el("div", { class: "pj-cmds" }, p.commandes.map(c => ligneCommande(p, c)))
      : el("div", { class: "pj-aucune" },
          p.proposees.length ? pl(p.proposees.length, "{n} commande proposée", "{n} commandes proposées") : t("Aucune commande de dev"),
          el("button", { class: "btn petit", onclick: () => editerCommandes(p) }, avec("settings", "Configurer")));
    const fetchBtn = p.git ? el("button", { class: "btn petit", onclick: ev => fetch1(p, ev.currentTarget) }, avec("download", "Récupérer (fetch)")) : null;
    return el("div", { class: "ligne-detail pj-detail" },
      el("div", { class: "pj-info" },
        el("span", { class: "pj-chemin", title: p.chemin }, p.chemin),
        ...p.types.slice(1, 5).map(ty => el("span", { class: "tag" }, ty)),
        p.manuel ? el("span", { class: "tag" }, "Ajouté à la main") : null),
      infosGit(p),
      el("div", {}, el("div", { class: "pj-titre-bloc" }, "Commandes"), cmds),
      el("div", { class: "pj-boutons" },
        p.commandes.length ? el("button", { class: "btn petit", title: "Serveurs de dev et autres commandes", onclick: () => editerCommandes(p) }, avec("settings", "Configurer")) : null,
        p.env ? el("button", { class: "btn petit", title: "Fichiers .env ↔ coffre", onclick: () => fenetreEnv(p) }, avec("lock", "Fichiers .env")) : null,
        fetchBtn,
        el("span", { class: "espace" }),
        el("button", { class: "btn petit discret", title: p.masque ? "Afficher ce projet" : "Masquer ce projet", onclick: () => masquer(p) },
          avec(p.masque ? "eye" : "eye-off", p.masque ? "Afficher" : "Masquer")),
        p.manuel ? el("button", { class: "btn petit discret", title: "Retirer de la liste", onclick: () => retirer(p) }, avec("x", "Retirer")) : null));
  }

  // -- actions -----------------------------------------------------------------
  async function ajouterProjet() {
    const chemin = await choisirDossier("Choisir le dossier du projet");
    if (!chemin) return;
    if (await appel("ajouter", { chemin }, "Projet ajouté")) afficher();
  }

  async function masquer(p) {
    const r = await appel("masquer", { projet: p.id, masque: !p.masque });
    if (!r) return;
    p.masque = r.masque;
    toast(r.masque ? "Projet masqué" : "Projet de nouveau affiché", "succes");
    dessiner();
  }

  async function retirer(p) {
    if (!(await confirmer(icone("x"), "Retirer ce projet ?", "Il disparaît de la liste. Le dossier n'est pas touché.", "Retirer"))) return;
    if (P.ouvert === p.id) P.ouvert = null;
    if (await appel("retirer", { projet: p.id })) afficher();
  }

  async function fetch1(p, bouton) {
    bouton.disabled = true;
    bouton.replaceChildren(icone("loader", "av pj-tourne"), t("Récupération…"));
    const r = await appel("git/fetch", { projet: p.id });
    if (r) {
      P.git[p.id] = r.git;
      if (r.git.erreur_fetch) toast(I18N.traduire(r.git.erreur_fetch), "erreur", 7000);
      else if (r.git.retard) toast(t("{nom} : {n} commit(s) à récupérer", { nom: p.nom, n: r.git.retard }), "succes", 4000);
      else toast(t("{nom} : à jour", { nom: p.nom }), "succes");
    }
    dessinerListe();
  }

  async function toutVerifier() {
    P.verification = true;
    dessiner();
    const r = await appel("git/tout_verifier", {});
    P.verification = false;
    if (r) {
      Object.assign(P.git, r.git);
      const n = Object.keys(r.git).length;
      if (r.erreurs) toast(t("{n} dépôts vérifiés, {e} en erreur", { n, e: r.erreurs }), "erreur", 6000);
      else toast(t("{n} dépôts vérifiés", { n }), "succes");
    }
    if (actif()) dessiner();
  }

  async function demarrer(p, c) {
    const r = await appel("commande", { projet: p.id, commande: c.id, action: "demarrer" });
    if (!r) return;
    c.etat = { etat: r.etat, code_sortie: r.code_sortie };
    toast(t("{nom} démarre…", { nom: c.nom }), "succes");
    dessinerListe();
  }

  async function arreter(p, c, apres) {
    if (!(await confirmer(icone("square"), t("Arrêter « {nom} » ?", { nom: c.nom }),
      "Le processus lancé par Mes outils et tous ses sous-processus sont arrêtés.", "Arrêter"))) { if (apres) apres(); return; }
    const r = await appel("commande", { projet: p.id, commande: c.id, action: "arreter" });
    if (r) { c.etat = { etat: "arrete" }; toast(t("{nom} arrêté", { nom: c.nom }), "succes"); }
    dessinerListe();
    if (apres) apres();
  }

  // -- commandes ---------------------------------------------------------------
  function editerCommandes(p) {
    let lignes = p.commandes.map(c => ({ ...c }));
    if (!lignes.length && p.proposees.length) lignes = [{ ...p.proposees[0] }];
    const zone = el("div");
    const champ = (obj, cle, attrs) => el("input", { value: obj[cle] ?? "", spellcheck: "false", ...attrs,
      oninput: e => { obj[cle] = e.target.value; } });
    const redessiner = () => {
      zone.replaceChildren(...(lignes.length ? [
        el("div", { class: "pj-entetes" }, el("span", {}, "Nom"), el("span", {}, "Commande"), el("span", {}, "Port"), el("span", {}, "Adresse"), el("span")),
        ...lignes.map((c, i) => el("div", { class: "pj-edit" },
          champ(c, "nom", { placeholder: "ex. Front" }),
          champ(c, "commande", { placeholder: "ex. npm run dev", class: "mono" }),
          champ(c, "port", { placeholder: "ex. 5173", inputmode: "numeric" }),
          champ(c, "url", { placeholder: "ex. http://localhost:5173" }),
          el("button", { class: "icone-btn danger", title: "Supprimer", onclick: () => { lignes.splice(i, 1); redessiner(); } }, icone("x"))))]
        : [el("p", {}, "Aucune commande pour l'instant.")]));
    };
    redessiner();
    const enregistrer = el("button", { class: "btn principal", onclick: async () => {
      enregistrer.disabled = true;
      const r = await appel("commandes/enregistrer", { projet: p.id, commandes: lignes }, "Commandes enregistrées");
      enregistrer.disabled = false;
      if (!r) return;
      p.commandes = r.commandes;
      fermer();
      dessinerListe();
    } }, "Enregistrer");
    fenetre([
      el("h3", {}, t("Commandes de « {nom} »", { nom: p.nom })),
      el("p", {}, "Chaque commande est lancée dans le dossier du projet, sans fenêtre. Sa sortie va dans le journal."),
      zone,
      el("button", { class: "btn discret", onclick: () => { lignes.push({ nom: "", commande: "", port: "", url: "" }); redessiner(); } }, avec("plus", "Ajouter une commande")),
      p.proposees.length ? el("div", {},
        el("div", { class: "pj-sous", style: "margin:12px 0 0" }, "Proposées d'après le projet :"),
        el("div", { class: "pj-sugg" }, p.proposees.map(s => el("button", { title: s.nom,
          onclick: () => { lignes.push({ ...s, id: lignes.some(l => l.id === s.id) ? "" : s.id }); redessiner(); } }, icone("plus"), s.commande)))) : null,
      el("div", { class: "actions" }, el("button", { class: "btn", onclick: fermer }, "Annuler"), enregistrer)]);
    $("#fenetre").style.width = "min(860px, 96vw)";
  }

  // -- journal -----------------------------------------------------------------
  function journal(p, c) {
    const pre = el("pre", { class: "pj-journal" }, t("Lecture…"));
    const point = el("span", { class: "point" });
    const etat = el("span", {});
    const boutons = el("span", { style: "display:flex;gap:8px" });
    let lignes = [], ouvert = true;
    const fenetreActuelle = () => $("#voile").classList.contains("visible") && $("#fenetre").contains(pre);

    async function lire() {
      if (!ouvert || !fenetreActuelle()) { ouvert = false; return; }
      let r;
      try { r = await api("/api/projets/journal", { projet: p.id, commande: c.id }); }
      catch (e) { pre.textContent = e.message; return; }
      const enBas = pre.scrollHeight - pre.scrollTop - pre.clientHeight < 30;
      if (r.lignes.join("\n") !== lignes.join("\n")) {
        lignes = r.lignes;
        pre.textContent = lignes.length ? lignes.join("\n") : t("Journal vide.");
        if (enBas) pre.scrollTop = pre.scrollHeight;
      }
      c.etat = { etat: r.etat, code_sortie: r.code_sortie };
      point.className = "point " + (r.etat === "arrete" ? "" : r.etat);
      etat.textContent = r.etat === "arrete" && r.code_sortie ? t("arrêté (code {c})", { c: r.code_sortie }) : t(LIBELLES[r.etat] || r.etat);
      const enRoute = r.etat === "marche" || r.etat === "demarrage";
      boutons.replaceChildren(
        enRoute
          ? el("button", { class: "btn", onclick: () => arreter(p, c, () => journal(p, c)) }, avec("square", "Arrêter"))
          : el("button", { class: "btn", disabled: r.etat === "occupe", onclick: async () => { await demarrer(p, c); lire(); } }, avec("play", "Démarrer")),
        el("button", { class: "btn", onclick: () => copier(lignes.join("\n")) }, avec("clipboard", "Copier")),
        el("button", { class: "btn principal", onclick: () => { ouvert = false; fermer(); dessinerListe(); } }, "Fermer"));
      setTimeout(lire, 2000);
    }

    fenetre([
      el("h3", {}, t("Journal de {nom}", { nom: `${p.nom} · ${c.nom}` })),
      el("div", { class: "pj-sous" }, point, etat, "·", el("span", {}, "300 dernières lignes, mises à jour toutes les 2 secondes")),
      pre,
      el("div", { class: "actions" }, boutons)]);
    $("#fenetre").style.width = "min(980px, 96vw)";
    lire();
  }

  // -- .env --------------------------------------------------------------------
  async function fenetreEnv(p) {
    const r = await appel("env/liste", { projet: p.id });
    if (!r) return;
    const blocs = [];
    if (!r.coffre.ouvert) {
      blocs.push(el("div", { class: "pj-alerte" }, icone("lock"), t("Ouvrez d'abord le coffre dans l'onglet Mots de passe."),
        el("button", { class: "btn petit", onclick: () => { fermer(); montrerVue("motsdepasse"); } }, "Ouvrir l'onglet Mots de passe")));
    }
    blocs.push(r.fichiers.length
      ? el("div", { class: "lignes pj-env" }, r.fichiers.map(f => el("div", { class: "ligne" },
          el("span", { class: "ligne-ic" }, icone("file")),
          el("div", { class: "ligne-corps" },
            el("div", { class: "ligne-titre" }, el("code", {}, f.fichier)),
            el("div", { class: "ligne-meta" }, [f.existe ? null : t("absent du dossier"),
              r.coffre.ouvert ? (f.sauvegarde ? t("sauvegardé le {d}", { d: date(f.sauvegarde) }) : t("pas encore sauvegardé")) : null]
              .filter(Boolean).join(" · "))),
          f.sauvegarde ? el("button", { class: "btn petit", onclick: () => restaurer(p, f) }, avec("undo-2", "Restaurer")) : null)))
      : el("p", {}, "Aucun fichier .env dans ce projet."));
    const sauver = el("button", { class: "btn principal", disabled: !r.coffre.ouvert || !r.fichiers.some(f => f.existe), onclick: async () => {
      sauver.disabled = true;
      const s = await appel("env/sauvegarder", { projet: p.id });
      if (s) { toast(t("{n} fichier(s) sauvegardé(s) dans le coffre", { n: s.sauvegardes.length }), "succes"); fenetreEnv(p); }
      else sauver.disabled = false;
    } }, avec("lock", "Sauvegarder dans le coffre"));
    fenetre([
      el("h3", {}, t("Fichiers .env de « {nom} »", { nom: p.nom })),
      el("p", {}, "Le contenu est rangé, chiffré, dans le coffre de l'onglet Mots de passe (catégorie « env »)."),
      ...blocs,
      el("div", { class: "actions" }, el("button", { class: "btn", onclick: fermer }, "Fermer"), sauver)]);
  }

  async function restaurer(p, f) {
    const oui = await confirmer(icone("undo-2"), t("Restaurer {f} ?", { f: f.fichier }),
      f.existe ? t("Le fichier est réécrit avec la version du coffre. L'ancien est gardé en {f}.bak.", { f: f.fichier })
               : t("Le fichier est recréé avec la version du coffre."), "Restaurer");
    if (!oui) { fenetreEnv(p); return; }
    const r = await appel("env/restaurer", { projet: p.id, fichier: f.fichier });
    if (r) toast(t("{f} restauré", { f: r.restaure }), "succes");
    fenetreEnv(p);
  }

  VUES.projets = { afficher, titre: "Projets", icone: icone("package"), groupe: "dev", ordre: 10 };
})();
