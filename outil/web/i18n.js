"use strict";
/* Traduction de l'interface (français → anglais).

   Le texte source est écrit en français. Chaque onglet ajoute ses traductions :
     I18N.ajouter({ "Texte en français": "English text", ... });
     I18N.motifs([[/^(\d+) dépôts?$/, "$1 repositories"], ...]);   // textes variables
   Puis :
     t("Bonjour {nom}", { nom })   → traduit, puis remplace {nom}
   el() (hub.html) traduit tout seul les textes simples, title et placeholder ;
   toast() et confirmer() aussi. La langue vient des Réglages (outils.json). */
window.I18N = (() => {
  const dico = {};
  const listeMotifs = [];
  let langue = "fr";

  const PICTO = /[\p{Extended_Pictographic}←-⇿■-◿⌀-⏿]️?/gu;
  const sansPicto = x => typeof x === "string" ? x.replace(PICTO, "").replace(/\s{2,}/g, " ").trim() : x;
  // Début d'un texte qui n'est pas à traduire : emojis, espaces, ponctuation.
  const PREFIXE = /^[^\p{L}\p{N}«"(]+/u;

  function chercher(texte) {
    if (dico[texte] !== undefined) return dico[texte];
    for (const [motif, remplacement] of listeMotifs) {
      if (motif.test(texte)) return texte.replace(motif, remplacement);
    }
    return undefined;
  }

  function traduire(texte) {
    if (langue === "fr" || typeof texte !== "string" || !texte.trim()) return texte;
    const direct = chercher(texte);
    if (direct !== undefined) return direct;
    // «  Message » : on traduit la partie après l'emoji.
    const m = texte.match(PREFIXE);
    if (m && m[0].length < texte.length) {
      const reste = chercher(texte.slice(m[0].length));
      if (reste !== undefined) return m[0] + reste;
    }
    // « Titre : détail » : chaque moitié séparément (messages d'erreur).
    const i = texte.indexOf(" : ");
    if (i > 0) {
      const a = traduire(texte.slice(0, i)), b = traduire(texte.slice(i + 3));
      if (a !== texte.slice(0, i) || b !== texte.slice(i + 3)) return `${a}: ${b}`;
    }
    return texte;
  }

  function t(texte, vars) {
    let s = traduire(texte);
    if (vars) s = s.replace(/\{(\w+)\}/g, (tout, k) => (vars[k] !== undefined ? vars[k] : tout));
    return s;
  }

  return {
    ajouter(d) {
      Object.assign(dico, d);
      // Les emojis des textes sont remplacés par des icônes à l'affichage
      // (hub.html) : chaque traduction existe aussi sans eux.
      for (const [k, v] of Object.entries(d)) {
        const k2 = sansPicto(k), v2 = sansPicto(v);
        if (k2 && k2 !== k && dico[k2] === undefined) dico[k2] = v2;
      }
    },
    motifs(liste) { listeMotifs.push(...liste); },
    t, traduire,
    get langue() { return langue; },
    set langue(v) { langue = v === "en" ? "en" : "fr"; document.documentElement.lang = langue; },
    /** Locale des dates et des nombres. */
    locale() { return langue === "en" ? "en-GB" : "fr-FR"; },
    /** Traduit les textes déjà écrits dans la page (hub.html). */
    traduirePage(racine = document.body) {
      if (langue === "fr") return;
      const marcheur = document.createTreeWalker(racine, NodeFilter.SHOW_TEXT);
      const noeuds = [];
      while (marcheur.nextNode()) noeuds.push(marcheur.currentNode);
      for (const n of noeuds) {
        const brut = n.nodeValue, coupe = brut.trim();
        // translate="no" : un nom propre (le nom de l'application) ne se traduit pas.
        if (!coupe || n.parentElement?.closest("script,style,[translate='no']")) continue;
        const tr = traduire(coupe);
        if (tr !== coupe) n.nodeValue = brut.replace(coupe, tr);
      }
      const attributs = ["title", "placeholder", "aria-label"];
      [racine, ...racine.querySelectorAll("[title],[placeholder],[aria-label]")].forEach(e => {
        for (const a of attributs) if (e.hasAttribute?.(a)) e.setAttribute(a, traduire(e.getAttribute(a)));
      });
    },
  };
})();
window.t = window.I18N.t;

/* ---------------------------------------------------------------------------
   hub.html : en-tête, accueil, tuiles, serveurs Odoo, fenêtres communes.
   (Les onglets ont leur propre dictionnaire dans outil/web/<nom>.js.)
   --------------------------------------------------------------------------- */
I18N.ajouter({
  // descriptions des applications (page Applications, assistant de démarrage)
  "Votre boîte mail (Gmail, Yahoo, OVH…) : lire, répondre, écrire.": "Your mailbox (Gmail, Yahoo, OVH…): read, reply, write.",
  "Notes en cartes ou listes à cocher, épinglées, avec rappel.": "Notes as cards or checklists, pinned, with reminders.",
  "Rendez-vous de la semaine et du mois, rappels par la bulle.": "Appointments for the week and month, reminders from the bubble.",
  "Coffre chiffré pour vos mots de passe et codes.": "Encrypted vault for your passwords and codes.",
  "Chrono par projet ou client, Pomodoro, export pour la facturation.": "Timer per project or client, Pomodoro, export for invoicing.",
  "Les derniers textes copiés, pour les retrouver en un clic.": "Your latest copied texts, one click away.",
  "Vos commandes et bouts de code favoris.": "Your favourite commands and code snippets.",
  "JWT, JSON, Base64, UUID, expressions régulières…": "JWT, JSON, Base64, UUID, regular expressions…",
  "Vos serveurs de dev et vos serveurs Odoo : démarrer, arrêter, journal.": "Your dev servers and Odoo servers: start, stop, log.",
  "Vos projets : VS Code, terminal, serveurs de dev, état Git.": "Your projects: VS Code, terminal, dev servers, Git status.",
  "Dépôts, pull requests, issues, état des tests GitHub.": "Repositories, pull requests, issues, GitHub test status.",
  "Quel programme occupe tel port, et l'arrêter.": "Which program uses a port, and stop it.",
  "Conteneurs Docker : démarrer, arrêter, journaux.": "Docker containers: start, stop, logs.",
  "Tester une API : requêtes, réponses, historique.": "Test an API: requests, responses, history.",
  "Une clé par serveur, posée en un clic.": "One key per server, installed in one click.",
  "Réunions et trajets": "Meetings and trips",
  "{n} mails non lus": "{n} unread emails",
  // en-tête
  "Coucou !": "Hi there!",
  "Bonjour": "Hello",
  "Bonne nuit": "Good night",
  "Bon après-midi": "Good afternoon",
  "Bonsoir": "Good evening",
  "Arrêter le tableau de bord": "Close the dashboard",
  "Que fait-on aujourd'hui ?": "What are we doing today?",
  "Tout est prêt, à vous de jouer ✨": "Everything is ready, over to you ✨",
  "Une facture à envoyer ? 🧾": "An invoice to send? 🧾",
  "Les serveurs vous attendent 🐘": "The servers are waiting for you 🐘",
  "Un café, et c'est parti ☕": "A coffee, and off we go ☕",
  "Belle journée de code ! 🚀": "Have a great coding day! 🚀",
  // menu
  "Accueil": "Home",
  "Mails": "Mail",
  "Notes": "Notes",
  "Agenda": "Calendar",
  "Mots de passe": "Passwords",
  "GitHub": "GitHub",
  "SSH": "SSH",
  "Au quotidien": "Everyday",
  "Développement": "Development",
  "Petits outils": "Handy tools",
  // accueil
  "Mes outils": "My tools",
  "Mes outils · tout tourne sur ce PC ·": "Mes outils · everything runs on this PC ·",
  "Ajouter, modifier ou retirer des outils": "Add, edit or remove tools",
  "✏️ Modifier": "✏️ Edit",
  "✅ Terminé": "✅ Done",
  "Aujourd'hui": "Today",
  "Demain": "Tomorrow",
  "Jour": "Day",
  "Rendez-vous": "Appointment",
  "Rien de prévu": "Nothing planned",
  "Notes épinglées": "Pinned notes",
  "Note": "Note",
  "Épinglez une note pour la retrouver ici": "Pin a note to find it here",
  "mail non lu": "unread email",
  "mails non lus": "unread emails",
  // tuiles
  "En marche": "Running",
  "Prêt à lancer": "Ready to launch",
  "Introuvable": "Not found",
  "Introuvable.": "Not found.",
  "Sans nom": "Untitled",
  "Modifier": "Edit",
  "Retirer": "Remove",
  "Ajouter un outil": "Add a tool",
  "{nom} lancé": "{nom} launched",
  "Retirer « {nom} » ?": "Remove “{nom}”?",
  "La tuile disparaît du tableau de bord. Le dossier ou le programme n'est pas touché.":
    "The tile disappears from the dashboard. The folder or program is not touched.",
  "Tuile retirée": "Tile removed",
  "Dossier": "Folder",
  "Fichier / programme": "File / program",
  "Page web": "Web page",
  "Appli locale": "Local app",
  "Chemin du dossier, ex. C:\\Users\\vous\\Documents": "Folder path, e.g. C:\\Users\\you\\Documents",
  "Chemin d'un fichier, d'un .exe ou d'un .bat": "Path of a file, an .exe or a .bat",
  "Adresse, ex. https://www.odoo.com": "Address, e.g. https://www.odoo.com",
  "Adresse de l'appli, ex. http://127.0.0.1:8765/": "App address, e.g. http://127.0.0.1:8765/",
  "Adresse": "Address",
  "Chemin": "Path",
  "Ouvrir dans sa propre fenêtre (sans barre d'adresse), comme une application":
    "Open in its own window (no address bar), like an app",
  "Port de l'appli": "App port",
  "ex. 8765": "e.g. 8765",
  "Commande de démarrage (un élément par ligne)": "Start command (one item per line)",
  "Lancée seulement si rien ne répond sur le port.": "Only run if nothing answers on the port.",
  "✏️ Modifier l'outil": "✏️ Edit the tool",
  "✨ Nouvel outil": "✨ New tool",
  "Nom": "Name",
  "ex. Comptes rendus": "e.g. Meeting minutes",
  "Petite description": "Short description",
  "ex. Mes notes de réunion": "e.g. My meeting notes",
  "Emoji": "Emoji",
  "Couleur": "Colour",
  "Ce qu'il ouvre": "What it opens",
  "Indiquez un nom": "Enter a name",
  "Indiquez ce qu'il faut ouvrir": "Say what to open",
  "✏️ Outil modifié": "✏️ Tool updated",
  "🎉 Nouvel outil ajouté !": "🎉 New tool added!",
  "WhatsApp Web dans sa propre fenêtre": "WhatsApp Web in its own window",
  // serveurs Odoo
  "Serveurs Odoo": "Odoo servers",
  "Ouvrir le gadget « Serveurs Odoo » (ajouter un serveur, comptes…)": "Open the “Odoo servers” gadget (add a server, accounts…)",
  "🧩 Gadget complet": "🧩 Full gadget",
  "Lecture des serveurs…": "Reading the servers…",
  "serveurs vérifiés à {heure}": "servers checked at {heure}",
  "Impossible de lire les serveurs": "Unable to read the servers",
  "Aucun serveur : ajoutez-en depuis le gadget complet.": "No server: add some from the full gadget.",
  "{n} / {total} en marche": "{n} / {total} running",
  "Démarrage…": "Starting…",
  "Arrêté": "Stopped",
  "Port occupé (autre programme)": "Port in use (another program)",
  "référence": "reference",
  "Fichier de configuration": "Configuration file",
  "Démarrer": "Start",
  "Arrêter": "Stop",
  "Ouvrir dans le navigateur": "Open in browser",
  "Journal": "Log",
  "Base de référence": "Reference database",
  "« {base} » ne doit pas être modifiée. Démarrer quand même son serveur ?": "“{base}” must not be modified. Start its server anyway?",
  "Arrêter {base} ?": "Stop {base}?",
  "Seul le serveur Odoo du port {port} est arrêté.": "Only the Odoo server on port {port} is stopped.",
  "Serveur pas prêt": "Server not ready",
  "Il ne répond pas encore. Ouvrir quand même ?": "It is not answering yet. Open anyway?",
  "Ouvrir": "Open",
  "{base} démarre…": "{base} is starting…",
  "{base} arrêté": "{base} stopped",
  // fermeture
  "Fermer le tableau de bord ?": "Close the dashboard?",
  "Les serveurs Odoo et les outils déjà lancés continuent de tourner.": "Odoo servers and tools already launched keep running.",
  "Fermer": "Close",
  "À bientôt !": "See you soon!",
  "Vous pouvez fermer cette fenêtre.": "You can close this window.",
  // fenêtres et messages communs
  "Annuler": "Cancel",
  "Oui": "Yes",
  "Enregistrer": "Save",
  "Ajouter": "Add",
  "Choisir un dossier": "Choose a folder",
  "📋 Copié": "📋 Copied",
  "Copie impossible": "Copy failed",
  "Accès refusé.": "Access denied.",
  "Erreur inattendue": "Unexpected error",
});
I18N.motifs([[/^Erreur (\d+)$/, "Error $1"]]);
