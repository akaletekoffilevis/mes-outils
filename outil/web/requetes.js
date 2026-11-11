"use strict";
/* Onglet « Testeur d'API » : un petit Postman. La requête part du serveur
   Python (requetes.py, route envoyer) : pas de souci de CORS.
   Aucun secret n'est écrit sur le disque : l'authentification et les en-têtes
   sensibles sont masqués (« •••• ») dans l'historique et retirés des requêtes
   enregistrées. */
(() => {
  I18N.ajouter({
    "Testeur d'API": "API tester", "Méthode": "Method",
    "Envoyer": "Send", "Envoi…": "Sending…", "Nouvelle requête": "New request", "Nouvelle": "New",
    "Enregistrer": "Save", "Enregistrer la requête": "Save request", "Enregistrer comme nouvelle": "Save as new",
    "Copier en cURL (bash)": "Copy as cURL (bash)", "cURL": "cURL",
    "📋 Commande cURL copiée": "📋 cURL command copied",
    "Adresse, ex. https://api.exemple.com/v1/clients ou {{base_url}}/clients": "URL, e.g. https://api.example.com/v1/customers or {{base_url}}/customers",
    "Paramètres": "Parameters", "En-têtes": "Headers", "Corps": "Body", "Authentification": "Auth", "Options": "Options", "Variables": "Variables",
    "Clé": "Key", "Valeur": "Value", "Nom": "Name", "Retirer la ligne": "Remove line", "Activer / désactiver": "Enable / disable",
    "Ajoutés à l'adresse (?cle=valeur), en plus de ceux déjà écrits dedans.": "Appended to the URL (?key=value), on top of those already in it.",
    "Aucun": "None", "JSON": "JSON", "Texte": "Text", "Formulaire": "Form",
    "Cette requête n'a pas de corps.": "This request has no body.",
    "✨ Mettre en forme": "✨ Format", "✅ JSON valide": "✅ Valid JSON", "Champs envoyés en application/x-www-form-urlencoded.": "Fields sent as application/x-www-form-urlencoded.",
    "Aucune": "None", "Jeton": "Token", "Utilisateur": "Username", "Mot de passe": "Password",
    "Aucune authentification.": "No authentication.",
    "🔒 Ces valeurs ne sont jamais écrites sur le disque : masquées (••••) dans l'historique, retirées des requêtes enregistrées.":
      "🔒 These values are never written to disk: masked (••••) in the history, removed from saved requests.",
    "Délai d'attente (secondes)": "Timeout (seconds)", "Suivre les redirections": "Follow redirects",
    "Ignorer les erreurs de certificat (TLS)": "Ignore certificate errors (TLS)",
    "⚠️ À réserver à un serveur de développement : la connexion n'est plus protégée.": "⚠️ Only for a development server: the connection is no longer protected.",
    "Utilisez {{nom}} dans l'adresse, les en-têtes, les paramètres, le corps et l'authentification.":
      "Use {{name}} in the URL, headers, params, body and auth.",
    "⚠️ Enregistrées en clair dans donnees\\requetes.json : n'y mettez pas de secret.": "⚠️ Stored in plain text in donnees\\requetes.json: do not put secrets here.",
    "Enregistrer les variables": "Save variables", "💾 Variables enregistrées": "💾 Variables saved",
    "Historique": "History", "Enregistrées": "Saved", "Vider": "Clear", "Vider l'historique ?": "Clear the history?",
    "Les 50 dernières requêtes envoyées sont effacées.": "The last 50 sent requests are deleted.",
    "Aucune requête envoyée pour l'instant.": "No request sent yet.",
    "Aucune requête enregistrée. Bouton 💾 pour garder la requête en cours.": "No saved request. Use 💾 to keep the current request.",
    "Sans collection": "No collection", "Supprimer": "Delete", "Supprimer « {nom} » ?": "Delete “{nom}”?",
    "La requête enregistrée disparaît.": "The saved request is removed.",
    "Collection (facultatif)": "Collection (optional)", "ex. API clients": "e.g. Customers API", "ex. Liste des clients": "e.g. List customers",
    "🔒 L'authentification (jeton, mot de passe) n'est pas enregistrée et les en-têtes sensibles sont masqués : il faudra les ressaisir.":
      "🔒 Authentication (token, password) is not saved and sensitive headers are masked: you will need to enter them again.",
    "💾 Requête enregistrée": "💾 Request saved", "🗑️ Requête supprimée": "🗑️ Request deleted",
    "🔒 Valeurs masquées (••••) à ressaisir avant l'envoi": "🔒 Masked values (••••) must be re-entered before sending",
    "🔒 Authentification à ressaisir (elle n'est pas enregistrée)": "🔒 Authentication must be re-entered (it is not saved)",
    "Réponse": "Response", "Envoyez une requête pour voir la réponse ici.": "Send a request to see the response here.",
    "Ctrl + Entrée pour envoyer": "Ctrl + Enter to send",
    "Copier le corps": "Copy body", "Copier": "Copy",
    "{n} redirection(s)": "{n} redirect(s)", "Réponse vide.": "Empty response.",
    "📦 Contenu binaire, {n} octets": "📦 Binary content, {n} bytes",
    "✂️ Réponse tronquée : seuls les 5 premiers Mo sont affichés (taille totale : {taille}).": "✂️ Truncated response: only the first 5 MB are shown (total size: {taille}).",
    "inconnue": "unknown", "Adresse finale": "Final URL",
    "Indiquez une adresse": "Enter a URL",
    "Échec de la requête": "Request failed",
    "o": "B", "Ko": "KB", "Mo": "MB",
    // Messages du serveur
    "Seules les adresses http:// et https:// sont acceptées.": "Only http:// and https:// URLs are accepted.",
    "Adresse incomplète : il manque le nom du serveur.": "Incomplete URL: the server name is missing.",
    "Une valeur masquée (••••) reste dans la requête : saisissez-la à nouveau.": "A masked value (••••) is still in the request: enter it again.",
    "Jeton (Bearer) vide.": "Empty (Bearer) token.", "Jeton invalide.": "Invalid token.",
    "Connexion refusée : rien n'écoute à cette adresse.": "Connection refused: nothing is listening at this address.",
    "Donnez un nom à la requête.": "Give the request a name.", "Requête introuvable.": "Request not found.",
    "Corps trop gros (10 Mo au plus).": "Body too large (10 MB max).", "Texte trop long.": "Text too long.",
    "Requête invalide.": "Invalid request.", "Variables invalides.": "Invalid variables.",
    "Trop de requêtes enregistrées : supprimez-en quelques-unes.": "Too many saved requests: delete some.",
    "Délai d'attente invalide.": "Invalid timeout.",
  });
  I18N.motifs([
    [/^Pas de réponse après (.+) s \(délai dépassé\)\.$/, "No response after $1 s (timeout)."],
    [/^Variable inconnue : (.+)$/, "Unknown variable: $1"],
    [/^Nom de variable invalide : (.+)$/, "Invalid variable name: $1"],
    [/^Nom d'en-tête invalide : (.+)$/, "Invalid header name: $1"],
    [/^Valeur d'en-tête invalide : (.+)$/, "Invalid header value: $1"],
    [/^Caractère non permis dans l'en-tête (.+) \(accents, emojis…\)\.$/, "Character not allowed in header $1 (accents, emojis…)."],
    [/^Serveur introuvable \(nom inconnu\) : (.*)$/, "Server not found (unknown name): $1"],
    [/^Échec de la connexion : (.*)$/, "Connection failed: $1"],
    [/^Erreur TLS : (.*)$/, "TLS error: $1"],
    [/^Certificat refusé : (.*)\. Pour un serveur de développement, cochez « Ignorer les erreurs de certificat »\.$/,
      "Certificate rejected: $1. For a development server, tick “Ignore certificate errors”."],
    [/^Méthode non prise en charge : (.+)$/, "Unsupported method: $1"],
  ]);

  const METHODES = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"];
  const COULEUR_METHODE = { GET: "vert", POST: "ambre", PUT: "bleu", PATCH: "violet", DELETE: "rouge", HEAD: "gris", OPTIONS: "gris" };
  const ENTETES_CONNUS = ["Accept", "Accept-Language", "Authorization", "Cache-Control", "Content-Type", "Cookie", "If-None-Match",
    "If-Modified-Since", "Origin", "Referer", "User-Agent", "X-Requested-With", "X-Api-Key"];
  const MASQUE = "••••";

  const style = document.createElement("style");
  style.textContent = `
    .rq-grille { display: grid; grid-template-columns: 230px minmax(0, 1fr); gap: 16px; align-items: start; }
    .rq-cote .rq-puces { flex-wrap: nowrap; gap: 4px; }
    .rq-cote .rq-puces .puce { padding: 6px 9px; font-size: 12px; white-space: nowrap; }
    .rq-champs input, .rq-champs select { font-weight: 500; }
    .rq-ligne > select.rq-methode { width: 118px; flex: none; }
    .rq-puces .icone-btn { width: 32px; height: 32px; background: var(--surface); }
    @media (max-width: 1000px) { .rq-grille { grid-template-columns: minmax(0, 1fr); } }
    .rq-carte { background: var(--carte); border-radius: var(--rayon); box-shadow: var(--ombre); padding: 14px 16px; min-width: 0; }
    .rq-carte + .rq-carte { margin-top: 14px; }
    .rq-ligne { display: flex; gap: 8px; align-items: center; }
    .rq-ligne .rq-url { flex: 1; min-width: 0; }
    .rq-saisie, .rq-carte select, .rq-carte textarea {
      border: 1.5px solid var(--ligne); border-radius: 12px; padding: 8px 11px; background: var(--champ); color: var(--encre);
      outline: none; font-size: 14px; min-width: 0; }
    .rq-saisie:focus, .rq-carte select:focus, .rq-carte textarea:focus { border-color: var(--violet); background: var(--champ-focus); }
    .rq-mono { font-family: var(--mono); font-size: 13px; }
    .rq-methode { font-weight: 600; font-family: var(--mono); }
    .rq-m-vert { color: var(--vert-texte); } .rq-m-ambre { color: var(--ambre-texte); } .rq-m-bleu { color: var(--bleu-texte); }
    .rq-m-violet { color: var(--violet); } .rq-m-rouge { color: var(--rouge-texte); } .rq-m-gris { color: var(--doux); }
    .rq-puces { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; margin: 12px 0 10px; }
    .rq-puces .puce { background: var(--surface); }
    .rq-puces .puce.actif { background: var(--encre); color: var(--carte); }
    .rq-puces .puce small { opacity: .7; margin-left: 4px; }
    .rq-lignes { display: flex; flex-direction: column; gap: 6px; }
    .rq-kv { display: grid; grid-template-columns: 22px minmax(0, 1fr) minmax(0, 1.4fr) 30px; gap: 6px; align-items: center; }
    .rq-kv input[type=checkbox] { width: 17px; height: 17px; accent-color: var(--violet); }
    .rq-kv.off .rq-saisie { opacity: .5; }
    .rq-kv .icone-btn { width: 30px; height: 30px; font-size: 13px; background: var(--surface); }
    .rq-aide { color: var(--doux); font-size: 12.5px; margin: 8px 0 0; }
    .rq-alerte { border-radius: 12px; padding: 9px 12px; font-size: 13px; margin: 8px 0; }
    .rq-alerte.ambre { background: var(--ambre-clair); color: var(--ambre-texte); }
    .rq-alerte.rouge { background: var(--rouge-clair); color: var(--rouge-texte); }
    .rq-alerte.bleu { background: var(--bleu-clair); color: var(--bleu-texte); }
    .rq-carte textarea { width: 100%; resize: vertical; min-height: 160px; font-family: var(--mono); font-size: 13px; tab-size: 2; }
    .rq-champs { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px; }
    .rq-champs label { display: flex; flex-direction: column; gap: 5px; font-size: 12.5px; font-weight: 700; color: var(--doux); }
    .rq-coche { display: flex; gap: 8px; align-items: center; font-size: 14px; margin: 8px 0; cursor: pointer; }
    .rq-coche input { width: 17px; height: 17px; accent-color: var(--violet); }
    .rq-statut { font-weight: 600; border-radius: 999px; padding: 3px 12px; font-family: var(--mono); font-size: 13.5px; }
    .rq-s2 { background: var(--vert-clair); color: var(--vert-texte); }
    .rq-s3 { background: var(--ambre-clair); color: var(--ambre-texte); }
    .rq-s4, .rq-s5 { background: var(--rouge-clair); color: var(--rouge-texte); }
    .rq-s1 { background: var(--bleu-clair); color: var(--bleu-texte); }
    .rq-info { color: var(--doux); font-size: 13px; font-weight: 600; }
    .rq-code { background: var(--code); color: var(--code-texte); font-family: var(--mono); font-size: 12.5px; border-radius: 12px; padding: 12px 14px;
      margin: 10px 0 0; max-height: 520px; overflow: auto; white-space: pre-wrap; word-break: break-word; }
    .rq-cle { color: var(--violet); } .rq-chaine { color: var(--vert-texte); } .rq-nombre { color: var(--bleu-texte); } .rq-mot { color: var(--ambre-texte); }
    .rq-table { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 10px; }
    .rq-table td { border-bottom: 1px solid var(--ligne); padding: 6px 8px; vertical-align: top; word-break: break-word; }
    .rq-table td:first-child { font-weight: 700; white-space: nowrap; color: var(--doux); width: 1%; }
    .rq-table td:last-child { font-family: var(--mono); font-size: 12.5px; }
    .rq-cote { position: sticky; top: 16px; max-height: calc(100vh - 40px); display: flex; flex-direction: column; }
    .rq-cote .rq-puces { margin-top: 0; }
    .rq-liste { overflow-y: auto; display: flex; flex-direction: column; gap: 3px; margin: 0 -6px; padding: 0 6px; }
    .rq-elt { display: flex; gap: 8px; align-items: center; padding: 7px 8px; border-radius: 10px; cursor: pointer; font-size: 13px; min-width: 0; }
    .rq-elt:hover { background: var(--violet-clair); }
    .rq-elt .rq-methode { font-size: 10.5px; width: 50px; flex: none; }
    .rq-elt .rq-texte { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .rq-elt .rq-texte small { display: block; color: var(--gris); font-size: 11px; overflow: hidden; text-overflow: ellipsis; }
    .rq-elt .rq-mini { font-size: 11px; font-weight: 600; border-radius: 99px; padding: 0 6px; flex: none; }
    .rq-elt .icone-btn { width: 24px; height: 24px; font-size: 11px; opacity: 0; background: transparent; }
    .rq-elt:hover .icone-btn { opacity: 1; }
    .rq-groupe { font-size: 11px; text-transform: uppercase; letter-spacing: .8px; font-weight: 600; color: var(--gris); margin: 10px 8px 2px; }
    .rq-tete { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
    .rq-tete .espace { flex: 1; }
    .rq-vide { color: var(--doux); text-align: center; padding: 26px 10px; font-size: 14px; }
  `;
  document.head.append(style);

  const nouvelle = () => ({
    methode: "GET", url: "", params: [], entetes: [], corps: { type: "aucun", texte: "", champs: [] },
    auth: { type: "aucune", jeton: "", utilisateur: "", mot_de_passe: "" },
    options: { timeout: 30, redirections: true, ignorer_tls: false },
  });
  const R = {
    req: nouvelle(), rep: null, erreur: null, envoi: false, charge: false,
    historique: [], enregistrees: [], variables: [],
    ongletReq: "params", ongletRep: "corps", ongletListe: "historique", idEnregistree: null, nomEnregistree: "",
  };
  const racine = () => $("#vue-requetes");
  const ligneVide = () => ({ cle: "", valeur: "", actif: true });

  /** Toujours une ligne vide en fin de liste (pour en ajouter en tapant). */
  function avecLigneVide(liste) {
    const der = liste[liste.length - 1];
    if (!der || der.cle || der.valeur) liste.push(ligneVide());
    return liste;
  }
  /** La requête à envoyer : sans les lignes vides. */
  function propre(r) {
    const c = structuredClone(r);
    const filtre = l => l.filter(x => x.cle.trim() || x.valeur);
    c.params = filtre(c.params); c.entetes = filtre(c.entetes); c.corps.champs = filtre(c.corps.champs);
    return c;
  }
  function completer(r) {
    const base = nouvelle();
    const c = { ...base, ...structuredClone(r) };
    c.corps = { ...base.corps, ...(c.corps || {}) };
    c.auth = { ...base.auth, ...(c.auth || {}) };
    c.options = { ...base.options, ...(c.options || {}) };
    for (const l of [c.params, c.entetes, c.corps.champs]) avecLigneVide(l);
    return c;
  }

  const taille = n => {
    if (n === null || n === undefined) return t("inconnue");
    const loc = I18N.locale();
    if (n < 1024) return `${n} ${t("o")}`;
    if (n < 1048576) return `${(n / 1024).toLocaleString(loc, { maximumFractionDigits: 1 })} ${t("Ko")}`;
    return `${(n / 1048576).toLocaleString(loc, { maximumFractionDigits: 1 })} ${t("Mo")}`;
  };
  const duree = ms => ms < 1000 ? `${Math.round(ms)} ms` : `${(ms / 1000).toLocaleString(I18N.locale(), { maximumFractionDigits: 2 })} s`;
  const classeStatut = s => "rq-statut rq-s" + String(s)[0];
  const badgeMethode = m => el("span", { class: "rq-methode rq-m-" + (COULEUR_METHODE[m] || "gris") }, m);

  /** JSON coloré, construit en nœuds (jamais d'innerHTML). */
  function colorerJson(texte) {
    const frag = document.createDocumentFragment();
    if (texte.length > 300000) { frag.append(texte); return frag; }
    const motif = /("(?:\\.|[^"\\])*")(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?/g;
    let i = 0, m;
    while ((m = motif.exec(texte))) {
      if (m.index > i) frag.append(texte.slice(i, m.index));
      const classe = m[1] ? (m[2] ? "rq-cle" : "rq-chaine") : m[3] ? "rq-mot" : "rq-nombre";
      frag.append(el("span", { class: classe }, m[1] || m[0]));
      if (m[2]) frag.append(m[2]);
      i = motif.lastIndex;
    }
    frag.append(texte.slice(i));
    return frag;
  }

  // -- données -------------------------------------------------------------------
  function prendreEtat(e) {
    R.historique = e.historique || [];
    R.enregistrees = e.enregistrees || [];
    R.variables = avecLigneVide(Object.entries(e.variables || {}).map(([cle, valeur]) => ({ cle, valeur, actif: true })));
  }

  async function afficher() {
    if (!R.charge) {
      try { prendreEtat(await api("/api/requetes/etat", {})); R.charge = true; }
      catch (e) { racine().replaceChildren(el("div", { class: "vide" }, "😕 " + e.message)); return; }
      R.req = completer(R.req);
    }
    dessiner();
  }

  // -- page ------------------------------------------------------------------------
  function dessiner() {
    racine().replaceChildren(
      el("div", { class: "barre-vue" }, el("h2", {}, "📡 " + t("Testeur d'API")), el("div", { class: "espace" }),
        el("span", { class: "rq-info" }, "Ctrl + Entrée pour envoyer"),
        el("button", { class: "btn", title: "Nouvelle requête", onclick: () => {
          R.req = completer(nouvelle()); R.idEnregistree = null; R.rep = null; R.erreur = null; dessinerRequete(); dessinerReponse(); } }, "✨ " + t("Nouvelle")),
        el("button", { class: "btn", title: "Enregistrer la requête", onclick: enregistrer }, "💾 " + t("Enregistrer")),
        el("button", { class: "btn", title: "Copier en cURL (bash)", onclick: copierCurl }, "📋 cURL")),
      el("div", { class: "rq-grille" },
        el("div", { class: "rq-carte rq-cote", id: "rq-cote" }),
        el("div", {}, el("div", { class: "rq-carte", id: "rq-requete" }), el("div", { class: "rq-carte", id: "rq-reponse" }))));
    dessinerCote();
    dessinerRequete();
    dessinerReponse();
  }

  // -- requête ---------------------------------------------------------------------
  function dessinerRequete() {
    const r = R.req;
    const methode = el("select", { class: "rq-methode rq-m-" + COULEUR_METHODE[r.methode], title: "Méthode",
      onchange: e => { r.methode = e.target.value; e.target.className = "rq-methode rq-m-" + COULEUR_METHODE[r.methode]; } },
      METHODES.map(m => el("option", { value: m }, m)));
    methode.value = r.methode;
    const url = el("input", { class: "rq-saisie rq-mono rq-url", value: r.url, spellcheck: "false",
      placeholder: "Adresse, ex. https://api.exemple.com/v1/clients ou {{base_url}}/clients",
      oninput: e => { r.url = e.target.value; },
      onkeydown: e => { if (e.key === "Enter") { e.preventDefault(); envoyer(); } } });
    const bouton = el("button", { class: "btn principal", id: "rq-envoyer", onclick: envoyer, disabled: R.envoi ? "" : null },
      R.envoi ? "⏳ " + t("Envoi…") : "🚀 " + t("Envoyer"));
    const compte = l => l.filter(x => x.actif && x.cle.trim()).length;
    const onglets = [
      ["params", "Paramètres", compte(r.params)], ["entetes", "En-têtes", compte(r.entetes)],
      ["corps", "Corps", r.corps.type !== "aucun" ? "•" : 0], ["auth", "Authentification", r.auth.type !== "aucune" ? "•" : 0],
      ["options", "Options", 0], ["variables", "Variables", compte(R.variables)]];
    const puces = el("div", { class: "rq-puces" }, onglets.map(([cle, titre, n]) =>
      el("button", { class: "puce" + (R.ongletReq === cle ? " actif" : ""), onclick: () => { R.ongletReq = cle; dessinerRequete(); } },
        titre, n ? el("small", {}, String(n)) : null)));
    const titre = R.idEnregistree ? el("div", { class: "rq-info", style: "margin-bottom:8px" }, "💾 " + R.nomEnregistree) : null;
    $("#rq-requete").replaceChildren(...[titre,
      el("div", { class: "rq-ligne" }, methode, url, bouton),
      puces, editeur()].filter(Boolean));
  }

  function editeur() {
    const r = R.req;
    switch (R.ongletReq) {
      case "params":
        return el("div", {}, lignes(r.params, "Clé", "Valeur"),
          el("p", { class: "rq-aide" }, "Ajoutés à l'adresse (?cle=valeur), en plus de ceux déjà écrits dedans."));
      case "entetes":
        return lignes(r.entetes, "Nom", "Valeur", "rq-entetes-connus");
      case "corps": return editeurCorps();
      case "auth": return editeurAuth();
      case "options": return editeurOptions();
      case "variables": return editeurVariables();
    }
    return el("div");
  }

  /** Lignes clé / valeur activables ; une ligne vide reste toujours en bas. */
  function lignes(liste, phCle, phValeur, listeSuggestions) {
    avecLigneVide(liste);
    const boite = el("div", { class: "rq-lignes" });
    if (listeSuggestions && !document.getElementById(listeSuggestions)) {
      document.body.append(el("datalist", { id: listeSuggestions }, ENTETES_CONNUS.map(n => el("option", { value: n }))));
    }
    const ligneDom = l => {
      const dom = el("div", { class: "rq-kv" + (l.actif ? "" : " off") });
      const suite = () => {
        if (l === liste[liste.length - 1] && (l.cle || l.valeur)) {
          const n = ligneVide(); liste.push(n); boite.append(ligneDom(n));
        }
      };
      dom.append(
        el("input", { type: "checkbox", title: "Activer / désactiver", checked: l.actif ? "" : null,
          onchange: e => { l.actif = e.target.checked; dom.classList.toggle("off", !l.actif); } }),
        el("input", { class: "rq-saisie rq-mono", value: l.cle, placeholder: phCle, spellcheck: "false", list: listeSuggestions || null,
          oninput: e => { l.cle = e.target.value; suite(); } }),
        el("input", { class: "rq-saisie rq-mono", value: l.valeur, placeholder: phValeur, spellcheck: "false",
          oninput: e => { l.valeur = e.target.value; suite(); } }),
        el("button", { class: "icone-btn", title: "Retirer la ligne", onclick: () => {
          const i = liste.indexOf(l);
          if (i >= 0) liste.splice(i, 1);
          dom.remove();
          if (!liste.length || liste[liste.length - 1].cle || liste[liste.length - 1].valeur) {
            const n = ligneVide(); liste.push(n); boite.append(ligneDom(n));
          }
        } }, "✕"));
      return dom;
    };
    boite.append(...liste.map(ligneDom));
    return boite;
  }

  function editeurCorps() {
    const c = R.req.corps;
    const choix = el("div", { class: "rq-puces", style: "margin-top:0" },
      [["aucun", "Aucun"], ["json", "JSON"], ["texte", "Texte"], ["formulaire", "Formulaire"]].map(([v, titre]) =>
        el("button", { class: "puce" + (c.type === v ? " actif" : ""), onclick: () => { c.type = v; dessinerRequete(); } }, titre)));
    if (c.type === "aucun") return el("div", {}, choix, el("p", { class: "rq-aide" }, "Cette requête n'a pas de corps."));
    if (c.type === "formulaire") {
      return el("div", {}, choix, lignes(c.champs, "Clé", "Valeur"),
        el("p", { class: "rq-aide" }, "Champs envoyés en application/x-www-form-urlencoded."));
    }
    const etat = el("span", { class: "rq-info" });
    const verifier = () => {
      if (c.type !== "json" || !c.texte.trim()) { etat.textContent = ""; return; }
      try { JSON.parse(c.texte); etat.textContent = t("✅ JSON valide"); etat.style.color = "var(--vert-texte)"; }
      catch (e) { etat.textContent = "❌ " + e.message; etat.style.color = "var(--rouge-texte)"; }
    };
    const zone = el("textarea", { value: c.texte, spellcheck: "false", rows: 10,
      placeholder: c.type === "json" ? '{\n  "nom": "valeur"\n}' : "",
      oninput: e => { c.texte = e.target.value; verifier(); },
      onkeydown: e => {
        if (e.key === "Tab" && !e.shiftKey) {
          e.preventDefault();
          const z = e.target, d = z.selectionStart;
          z.setRangeText("  ", d, z.selectionEnd, "end"); c.texte = z.value;
        }
      } });
    verifier();
    return el("div", {}, choix, zone,
      c.type === "json" ? el("div", { class: "rq-tete", style: "margin-top:8px" },
        el("button", { class: "btn", onclick: () => {
          try { c.texte = JSON.stringify(JSON.parse(c.texte), null, 2); zone.value = c.texte; verifier(); }
          catch (e) { toast("❌ " + e.message, "erreur", 5000); }
        } }, "✨ Mettre en forme"), etat) : null);
  }

  function editeurAuth() {
    const a = R.req.auth;
    const choix = el("select", { onchange: e => { a.type = e.target.value; dessinerRequete(); } },
      [["aucune", "Aucune"], ["bearer", "Bearer"], ["basic", "Basic"]].map(([v, titre]) => el("option", { value: v }, titre)));
    choix.value = a.type;
    const champ = (titre, cle, type = "text") => el("label", {}, titre,
      el("input", { class: "rq-saisie rq-mono", type, value: a[cle], spellcheck: "false", autocomplete: "off",
        oninput: e => { a[cle] = e.target.value; } }));
    const champs = a.type === "bearer" ? [champ("Jeton", "jeton", "password")]
      : a.type === "basic" ? [champ("Utilisateur", "utilisateur"), champ("Mot de passe", "mot_de_passe", "password")] : [];
    return el("div", {},
      el("div", { class: "rq-champs" }, el("label", {}, "Authentification", choix), ...champs),
      a.type === "aucune" ? el("p", { class: "rq-aide" }, "Aucune authentification.")
        : el("div", { class: "rq-alerte bleu" }, "🔒 Ces valeurs ne sont jamais écrites sur le disque : masquées (••••) dans l'historique, retirées des requêtes enregistrées."));
  }

  function editeurOptions() {
    const o = R.req.options;
    const coche = (titre, cle) => el("label", { class: "rq-coche" },
      el("input", { type: "checkbox", checked: o[cle] ? "" : null, onchange: e => { o[cle] = e.target.checked; dessinerRequete(); } }), titre);
    return el("div", {},
      el("div", { class: "rq-champs" }, el("label", {}, "Délai d'attente (secondes)",
        el("input", { class: "rq-saisie", type: "number", min: "1", max: "600", value: o.timeout,
          oninput: e => { o.timeout = Number(e.target.value) || 30; } }))),
      coche("Suivre les redirections", "redirections"),
      coche("Ignorer les erreurs de certificat (TLS)", "ignorer_tls"),
      o.ignorer_tls ? el("div", { class: "rq-alerte ambre" }, "⚠️ À réserver à un serveur de développement : la connexion n'est plus protégée.") : null);
  }

  function editeurVariables() {
    return el("div", {},
      lignes(R.variables, "Nom", "Valeur"),
      el("p", { class: "rq-aide" }, "Utilisez {{nom}} dans l'adresse, les en-têtes, les paramètres, le corps et l'authentification."),
      el("div", { class: "rq-alerte ambre" }, "⚠️ Enregistrées en clair dans donnees\\requetes.json : n'y mettez pas de secret."),
      el("button", { class: "btn", onclick: async () => {
        const variables = {};
        for (const l of R.variables) if (l.actif && l.cle.trim()) variables[l.cle.trim()] = l.valeur;
        try { prendreEtat(await api("/api/requetes/variables", { variables })); toast("💾 Variables enregistrées", "succes"); dessinerRequete(); }
        catch (e) { toast("😕 " + e.message, "erreur", 6000); }
      } }, "💾 " + t("Enregistrer les variables")));
  }

  // -- actions ---------------------------------------------------------------------
  async function envoyer() {
    if (R.envoi) return;
    if (!R.req.url.trim()) { toast("Indiquez une adresse", "erreur"); return; }
    R.envoi = true; R.erreur = null;
    dessinerRequete(); dessinerReponse();
    try {
      const r = await api("/api/requetes/envoyer", { requete: propre(R.req) });
      R.rep = r.reponse; R.historique = r.historique;
    } catch (e) { R.rep = null; R.erreur = e.message; }
    R.envoi = false;
    dessinerRequete(); dessinerReponse(); dessinerCote();
  }

  async function copierCurl() {
    if (!R.req.url.trim()) { toast("Indiquez une adresse", "erreur"); return; }
    try { const r = await api("/api/requetes/curl", { requete: propre(R.req) }); copier(r.commande, "📋 Commande cURL copiée"); }
    catch (e) { toast("😕 " + e.message, "erreur", 6000); }
  }

  function charger(requete, ident = null, nom = "") {
    R.req = completer(requete);
    // Un champ mot de passe rempli de « •••• » ressemblerait à une vraie valeur : on le vide.
    for (const cle of ["jeton", "utilisateur", "mot_de_passe"]) if (R.req.auth[cle] === MASQUE) R.req.auth[cle] = "";
    R.idEnregistree = ident; R.nomEnregistree = nom;
    const texte = JSON.stringify(requete);
    if (texte.includes(MASQUE)) toast("🔒 Valeurs masquées (••••) à ressaisir avant l'envoi", "", 4500);
    else if (ident && requete.auth && requete.auth.type !== "aucune") toast("🔒 Authentification à ressaisir (elle n'est pas enregistrée)", "", 4500);
    if (R.req.auth.type !== "aucune" && (texte.includes(MASQUE) || ident)) R.ongletReq = "auth";
    dessinerRequete();
  }

  function enregistrer() {
    if (!R.req.url.trim()) { toast("Indiquez une adresse", "erreur"); return; }
    const existante = R.enregistrees.find(e => e.id === R.idEnregistree);
    let suggestion = existante?.nom || "";
    if (!suggestion) { try { suggestion = `${R.req.methode} ${new URL(R.req.url).pathname}`; } catch { suggestion = R.req.methode + " " + R.req.url; } }
    const nom = el("input", { value: suggestion, placeholder: "ex. Liste des clients" });
    const collections = [...new Set(R.enregistrees.map(e => e.collection).filter(Boolean))];
    const collection = el("input", { value: existante?.collection || "", placeholder: "ex. API clients", list: "rq-collections" });
    const valider = async ident => {
      try {
        const r = await api("/api/requetes/enregistrer", { id: ident, nom: nom.value, collection: collection.value, requete: propre(R.req) });
        prendreEtatSansVariables(r);
        R.idEnregistree = r.enregistree.id; R.nomEnregistree = r.enregistree.nom;
        R.ongletListe = "enregistrees";
        fermer(); toast("💾 Requête enregistrée", "succes");
        dessinerRequete(); dessinerCote();
      } catch (e) { toast("😕 " + e.message, "erreur", 6000); }
    };
    fenetre([
      el("h3", {}, "💾 " + t("Enregistrer la requête")),
      el("label", { class: "champ" }, "Nom", nom),
      el("label", { class: "champ" }, "Collection (facultatif)", collection,
        el("datalist", { id: "rq-collections" }, collections.map(c => el("option", { value: c })))),
      el("div", { class: "rq-alerte bleu" }, "🔒 L'authentification (jeton, mot de passe) n'est pas enregistrée et les en-têtes sensibles sont masqués : il faudra les ressaisir."),
      el("div", { class: "actions" },
        el("button", { class: "btn", onclick: fermer }, "Annuler"),
        existante ? el("button", { class: "btn", onclick: () => valider(null) }, "Enregistrer comme nouvelle") : null,
        el("button", { class: "btn principal", onclick: () => valider(existante ? existante.id : null) }, "Enregistrer"))]);
    nom.focus(); nom.select();
  }
  function prendreEtatSansVariables(e) { R.historique = e.historique || []; R.enregistrees = e.enregistrees || []; }

  // -- colonne de gauche -----------------------------------------------------------
  function dessinerCote() {
    const zone = $("#rq-cote");
    if (!zone) return;
    const puces = el("div", { class: "rq-puces" },
      el("button", { class: "puce" + (R.ongletListe === "historique" ? " actif" : ""), onclick: () => { R.ongletListe = "historique"; dessinerCote(); } },
        "🕘 " + t("Historique")),
      el("button", { class: "puce" + (R.ongletListe === "enregistrees" ? " actif" : ""), onclick: () => { R.ongletListe = "enregistrees"; dessinerCote(); } },
        "💾 " + t("Enregistrées")));
    const liste = el("div", { class: "rq-liste" });
    if (R.ongletListe === "historique") {
      if (!R.historique.length) liste.append(el("div", { class: "rq-vide" }, "Aucune requête envoyée pour l'instant."));
      for (const h of R.historique) {
        const d = new Date(h.date);
        const quand = d.toDateString() === new Date().toDateString()
          ? d.toLocaleTimeString(I18N.locale(), { hour: "2-digit", minute: "2-digit" })
          : d.toLocaleDateString(I18N.locale(), { day: "numeric", month: "short" });
        liste.append(el("div", { class: "rq-elt", title: h.requete.url, onclick: () => charger(h.requete) },
          badgeMethode(h.requete.methode),
          el("div", { class: "rq-texte" }, cheminCourt(h.requete.url), el("small", {}, quand + " · " + duree(h.duree_ms))),
          el("span", { class: "rq-mini " + classeStatut(h.statut).replace("rq-statut ", "") }, String(h.statut))));
      }
      zone.replaceChildren(...[puces, liste, R.historique.length ? el("div", { style: "margin-top:8px;text-align:right" },
        el("button", { class: "btn discret", onclick: viderHistorique }, "🗑️ " + t("Vider"))) : null].filter(Boolean));
      return;
    }
    if (!R.enregistrees.length) liste.append(el("div", { class: "rq-vide" }, "Aucune requête enregistrée. Bouton 💾 pour garder la requête en cours."));
    const groupes = {};
    for (const e of R.enregistrees) (groupes[e.collection || ""] ||= []).push(e);
    const noms = Object.keys(groupes).sort((a, b) => (a === "") - (b === "") || a.localeCompare(b));
    for (const g of noms) {
      liste.append(el("div", { class: "rq-groupe" }, g ? "📁 " + g : t("Sans collection")));
      for (const e of groupes[g].sort((a, b) => a.nom.localeCompare(b.nom))) {
        liste.append(el("div", { class: "rq-elt", title: e.requete.url, style: e.id === R.idEnregistree ? "background:var(--violet-clair)" : "",
          onclick: () => charger(e.requete, e.id, e.nom) },
          badgeMethode(e.requete.methode),
          el("div", { class: "rq-texte" }, e.nom, el("small", {}, cheminCourt(e.requete.url))),
          el("button", { class: "icone-btn", title: "Supprimer", onclick: ev => { ev.stopPropagation(); supprimer(e); } }, "✕")));
      }
    }
    zone.replaceChildren(puces, liste);
  }

  function cheminCourt(url) {
    try { const u = new URL(url); return u.host + u.pathname + u.search; } catch { return url; }
  }

  async function viderHistorique() {
    if (!(await confirmer("🗑️", "Vider l'historique ?", "Les 50 dernières requêtes envoyées sont effacées.", "Vider"))) return;
    try { prendreEtatSansVariables(await api("/api/requetes/historique/vider", {})); dessinerCote(); }
    catch (e) { toast("😕 " + e.message, "erreur"); }
  }

  async function supprimer(e) {
    if (!(await confirmer("🗑️", t("Supprimer « {nom} » ?", { nom: e.nom }), "La requête enregistrée disparaît.", "Supprimer"))) return;
    try {
      prendreEtatSansVariables(await api("/api/requetes/supprimer", { id: e.id }));
      if (R.idEnregistree === e.id) { R.idEnregistree = null; dessinerRequete(); }
      toast("🗑️ Requête supprimée"); dessinerCote();
    } catch (err) { toast("😕 " + err.message, "erreur"); }
  }

  // -- réponse ---------------------------------------------------------------------
  function dessinerReponse() {
    const zone = $("#rq-reponse");
    if (!zone) return;
    if (R.envoi) { zone.replaceChildren(el("div", { class: "rq-vide" }, "⏳ " + t("Envoi…"))); return; }
    if (R.erreur) {
      zone.replaceChildren(el("div", { class: "rq-tete" }, el("b", {}, "Réponse")),
        el("div", { class: "rq-alerte rouge" }, "❌ " + t("Échec de la requête") + " : " + R.erreur));
      return;
    }
    const rep = R.rep;
    if (!rep) { zone.replaceChildren(el("div", { class: "rq-vide" }, "📡 " + t("Envoyez une requête pour voir la réponse ici."))); return; }
    const puces = el("div", { class: "puces" },
      el("button", { class: "puce" + (R.ongletRep === "corps" ? " actif" : ""), onclick: () => { R.ongletRep = "corps"; dessinerReponse(); } }, "Corps"),
      el("button", { class: "puce" + (R.ongletRep === "entetes" ? " actif" : ""), onclick: () => { R.ongletRep = "entetes"; dessinerReponse(); } },
        t("En-têtes") + " (" + rep.entetes.length + ")"));
    const tete = el("div", { class: "rq-tete" },
      el("span", { class: classeStatut(rep.statut) }, `${rep.statut} ${rep.raison || ""}`.trim()),
      el("span", { class: "rq-info" }, "⏱️ " + duree(rep.duree_ms)),
      el("span", { class: "rq-info" }, "📦 " + taille(rep.taille)),
      rep.redirections ? el("span", { class: "rq-info", title: t("Adresse finale") + " : " + rep.url_finale }, "↪️ " + t("{n} redirection(s)", { n: rep.redirections })) : null,
      el("span", { class: "espace" }), puces,
      R.ongletRep === "corps" && rep.corps ? el("button", { class: "btn", onclick: () => copier(rep.corps) }, "📋 " + t("Copier")) : null);
    const blocs = [tete];
    if (R.ongletRep === "entetes") {
      blocs.push(el("table", { class: "rq-table" }, rep.entetes.map(([k, v]) => el("tr", {}, el("td", {}, k), el("td", {}, v)))));
    } else {
      if (rep.tronque) blocs.push(el("div", { class: "rq-alerte ambre" }, t("✂️ Réponse tronquée : seuls les 5 premiers Mo sont affichés (taille totale : {taille}).", { taille: taille(rep.taille) })));
      if (rep.type === "binaire") blocs.push(el("div", { class: "rq-vide" }, t("📦 Contenu binaire, {n} octets", { n: rep.octets.toLocaleString(I18N.locale()) })
        + (rep.type_contenu ? ` (${rep.type_contenu})` : "")));
      else if (rep.type === "vide") blocs.push(el("div", { class: "rq-vide" }, "Réponse vide."));
      else {
        const pre = el("pre", { class: "rq-code" });
        if (rep.type === "json") pre.append(colorerJson(rep.corps)); else pre.textContent = rep.corps;
        blocs.push(pre);
      }
    }
    zone.replaceChildren(...blocs);
  }

  // Ctrl + Entrée : envoyer, où que soit le curseur dans l'onglet.
  document.addEventListener("keydown", e => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey) && racine()?.classList.contains("actif") && !$("#voile").classList.contains("visible")) {
      e.preventDefault(); envoyer();
    }
  });

  VUES.requetes = { afficher, titre: "Testeur d'API", icone: "📡", groupe: "dev", ordre: 50 };
})();
