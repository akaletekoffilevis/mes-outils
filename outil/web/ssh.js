"use strict";
/* Onglet « Serveurs SSH » : une clé par serveur, posée en un clic (voir
   ssh_cles.py). Le mot de passe saisi part une seule fois au serveur local,
   pour la première connexion ; il n'est ni gardé ni réaffiché. */
(() => {
  I18N.ajouter({
    "SSH": "SSH",
    "Serveurs SSH": "SSH servers",
    "＋ Nouveau serveur": "＋ New server",
    "Aucun serveur pour l'instant. « ＋ Nouveau serveur » : saisissez l'adresse, l'utilisateur et le mot de passe, la clé est créée et installée pour vous.":
      "No server yet. “＋ New server”: enter the address, the user and the password; the key is created and installed for you.",
    "{date} à {heure}": "{date} at {heure}",
    "⚠️ Clé absente de ce PC": "⚠️ Key missing from this PC",
    "✅ Connexion vérifiée le {date}": "✅ Connection checked on {date}",
    "Pas encore testé": "Not tested yet",
    "Tester la connexion": "Test the connection",
    "Ouvrir un terminal sur ce serveur": "Open a terminal on this server",
    "Retirer la clé du serveur et de ce PC": "Remove the key from the server and from this PC",
    "Copier la commande": "Copy the command",
    "📋 « {texte} » copié": "📋 “{texte}” copied",
    "Copie impossible": "Copy failed",
    "Connexion…": "Connecting…",
    "✅ Connexion réussie, sans mot de passe": "✅ Connected, without a password",
    "✅ Connexion réussie à {machine}, sans mot de passe": "✅ Connected to {machine}, without a password",
    "💻 Terminal ouvert": "💻 Terminal opened",
    "Retirer « {nom} » ?": "Remove “{nom}”?",
    "La clé est retirée du serveur, puis supprimée de ce PC. Pour y revenir sans mot de passe, il faudra recréer une clé.":
      "The key is removed from the server, then deleted from this PC. To connect again without a password, you will need to create a new key.",
    "Retirer": "Remove",
    "🗑️ Clé retirée du serveur et de ce PC": "🗑️ Key removed from the server and from this PC",
    "ex. Serveur web": "e.g. Web server",
    "ex. 203.0.113.10": "e.g. 203.0.113.10",
    "Afficher": "Show",
    "Installation…": "Installing…",
    "Clé installée": "Key installed",
    "Connexion vérifiée, sans mot de passe. Désormais, dans un terminal :": "Connection checked, without a password. From now on, in a terminal:",
    "Connexion vérifiée sur « {machine} », sans mot de passe. Désormais, dans un terminal :": "Connection checked on “{machine}”, without a password. From now on, in a terminal:",
    "📋 Copier": "📋 Copy",
    "🔑 Créer et installer la clé": "🔑 Create and install the key",
    "🔑 Nouveau serveur SSH": "🔑 New SSH server",
    "Une clé est créée pour ce serveur et déposée avec le mot de passe. Le mot de passe ne sert qu'à cette première connexion : il n'est pas enregistré.":
      "A key is created for this server and installed with the password. The password is only used for this first connection: it is not stored.",
    "Nom du serveur": "Server name",
    "Adresse IP ou nom": "IP address or name",
    "Port SSH": "SSH port",
    "Utilisateur": "Username",
    "Mot de passe du serveur": "Server password",
    "Annuler": "Cancel",
    // messages du serveur (ssh_cles.py)
    "Serveur introuvable dans la liste.": "Server not found in the list.",
    "Donnez un nom au serveur (lettres ou chiffres).": "Give the server a name (letters or digits).",
    "Donnez un nom au serveur.": "Give the server a name.",
    "Adresse du serveur invalide (IP ou nom, sans espace).": "Invalid server address (IP or name, no spaces).",
    "Utilisateur invalide (lettres, chiffres, . _ -).": "Invalid user (letters, digits, . _ -).",
    "Le port doit être un nombre.": "The port must be a number.",
    "Le port doit être entre 1 et 65535.": "The port must be between 1 and 65535.",
    "Le serveur ne répond pas (délai dépassé). Vérifiez l'adresse et le port.": "The server is not responding (timeout). Check the address and the port.",
    "La clé de ce serveur n'est plus sur ce PC.": "This server's key is no longer on this PC.",
    "Saisissez le mot de passe du serveur (il ne sert qu'une fois).": "Enter the server password (it is used only once).",
    "choisissez un autre nom.": "choose another name.",
    "Création de la clé impossible": "Unable to create the key",
    "Clé publique inattendue : rien n'a été envoyé.": "Unexpected public key: nothing was sent.",
    "Connexion refusée : mot de passe ou utilisateur incorrect (ou connexion par mot de passe désactivée sur le serveur).":
      "Connection refused: wrong password or user (or password login disabled on the server).",
    "Le serveur refuse la connexion sur ce port : vérifiez le port SSH.": "The server refuses the connection on this port: check the SSH port.",
    "Adresse du serveur introuvable.": "Server address not found.",
    "Le serveur ne répond pas : vérifiez l'adresse et le port.": "The server is not responding: check the address and the port.",
    "L'empreinte du serveur a changé depuis la dernière connexion. Par prudence, rien n'a été fait.":
      "The server fingerprint has changed since the last connection. To be safe, nothing was done.",
    "Erreur inconnue.": "Unknown error.",
  });
  I18N.motifs([
    [/^Un serveur s'appelle déjà « (.+) »$/, "A server is already called “$1”"],
    [/^La clé n'a pas pu être retirée du serveur \((.*)\)\. Elle a été retirée de ce PC ; retirez la ligne « (.+) » du fichier authorized_keys du serveur\.$/s,
      "The key could not be removed from the server ($1). It was removed from this PC; remove the line “$2” from the server's authorized_keys file."],
  ]);

  const X = { serveurs: [] };
  const COULEURS_SSH = ["#2f8cff", "#6c4cf5", "#18b597", "#ff7a59", "#e5488d", "#ffb020", "#0ea5a4"];

  const style = document.createElement("style");
  style.textContent = `
    .liste-ssh { display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 12px; }
    .srv { background: var(--carte); border-radius: var(--rayon); box-shadow: var(--ombre); padding: 14px 16px; display: flex; gap: 12px; align-items: center; animation: apparait .3s both; }
    .srv .av { width: 46px; height: 46px; border-radius: 15px; display: grid; place-items: center; font-size: 22px; flex: none; color: #fff; }
    .srv .infos { flex: 1; min-width: 0; }
    .srv .t { font-weight: 600; font-size: 15px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .srv .u { font-size: 13px; color: var(--doux); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .srv .cmd { font-family: var(--mono); font-size: 13px; background: var(--code); color: var(--code-texte); border-radius: 8px; padding: 2px 8px; margin-top: 5px; display: inline-block; cursor: pointer; }
    .srv .cmd:hover { background: var(--violet-clair); color: var(--violet); }
    .srv .etat-test { font-size: 12px; margin-top: 4px; color: var(--doux); }
    .srv .etat-test.ok { color: var(--vert-texte); }
    .srv .etat-test.ko { color: var(--rouge); }
    .srv .actions-srv { display: flex; gap: 4px; }
    .note-ssh { background: var(--bleu-clair); border-radius: 14px; padding: 12px 14px; font-size: 13.5px; color: var(--bleu-texte); margin: 4px 0 14px; text-align: left; }
    .ligne-champs { display: grid; grid-template-columns: 1fr 110px; gap: 10px; }
    .attente { display: inline-block; animation: tourne 1s linear infinite; }
    @keyframes tourne { to { transform: rotate(360deg); } }
  `;
  document.head.append(style);
  const racine = () => $("#vue-ssh");
  // Données de l'utilisateur (noms, adresses) : jamais traduites.
  const brut = s => document.createTextNode(s ?? "");

  async function charger() {
    const { serveurs } = await api("/api/ssh/liste", {});
    X.serveurs = serveurs;
  }

  async function afficher() {
    try { await charger(); } catch (e) { toast(e.message, "erreur"); }
    const r = racine();
    const barre = el("div", { class: "barre-vue" },
      el("h2", {}, "🔑 " + t("Serveurs SSH") + " ", el("span", { class: "compte" }, String(X.serveurs.length))),
      el("div", { class: "espace" }),
      el("button", { class: "btn principal", onclick: nouveau }, "＋ Nouveau serveur"));
    const liste = X.serveurs.length
      ? el("div", { class: "liste-ssh" }, X.serveurs.map(carte))
      : el("div", { class: "vide" }, "Aucun serveur pour l'instant. « ＋ Nouveau serveur » : saisissez l'adresse, l'utilisateur et le mot de passe, la clé est créée et installée pour vous.");
    r.replaceChildren(barre, liste);
  }

  // « 2026-11-06 19:23 » → « 06/11/2026 à 19:23 » (ou « 06/11/2026 at 19:23 »)
  function dateLisible(texte) {
    const m = /^(\d{4})-(\d{2})-(\d{2}) (\d{2}:\d{2})/.exec(texte || "");
    if (!m) return texte;
    const date = new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3])).toLocaleDateString(I18N.locale());
    return t("{date} à {heure}", { date, heure: m[4] });
  }

  function carte(s, i) {
    const etat = el("div", { class: "etat-test" + (s.dernier_resultat === "ok" ? " ok" : "") },
      !s.cle_presente ? "⚠️ Clé absente de ce PC" : s.dernier_test ? t("✅ Connexion vérifiée le {date}", { date: dateLisible(s.dernier_test) }) : "Pas encore testé");
    const boutons = el("div", { class: "actions-srv" },
      el("button", { class: "icone-btn", title: "Tester la connexion", onclick: e => tester(s, etat, e.currentTarget) }, "🧪"),
      el("button", { class: "icone-btn", title: "Ouvrir un terminal sur ce serveur", onclick: () => terminal(s) }, "💻"),
      el("button", { class: "icone-btn", title: "Retirer la clé du serveur et de ce PC", onclick: () => retirer(s) }, "🗑️"));
    return el("div", { class: "srv", style: `animation-delay:${i * 40}ms` },
      el("div", { class: "av", style: `background:${COULEURS_SSH[i % COULEURS_SSH.length]}` }, "🖥️"),
      el("div", { class: "infos" },
        el("div", { class: "t", title: s.nom }, brut(s.nom)),
        el("div", { class: "u" }, brut(`${s.utilisateur}@${s.hote} · port ${s.port}`)),
        el("span", { class: "cmd", title: "Copier la commande", onclick: () => copier(`ssh ${s.alias}`) }, brut(`ssh ${s.alias}`)),
        etat),
      boutons);
  }

  async function copier(texte) {
    try { await navigator.clipboard.writeText(texte); toast(t("📋 « {texte} » copié", { texte }), "succes"); }
    catch { toast("Copie impossible", "erreur"); }
  }

  async function tester(s, etat, bouton) {
    bouton.disabled = true;
    etat.className = "etat-test";
    etat.replaceChildren(el("span", { class: "attente" }, "⏳"), " " + t("Connexion…"));
    try {
      const r = await api("/api/ssh/tester", { alias: s.alias });
      toast(r.machine ? t("✅ Connexion réussie à {machine}, sans mot de passe", { machine: r.machine }) : t("✅ Connexion réussie, sans mot de passe"), "succes");
      await afficher();
    } catch (e) {
      etat.className = "etat-test ko";
      etat.textContent = "❌ " + e.message;
    } finally { bouton.disabled = false; }
  }

  async function terminal(s) {
    try { await api("/api/ssh/terminal", { alias: s.alias }); toast("Terminal ouvert", "succes"); }
    catch (e) { toast(e.message, "erreur"); }
  }

  async function retirer(s) {
    const oui = await confirmer("🗑️", t("Retirer « {nom} » ?", { nom: s.nom }),
      "La clé est retirée du serveur, puis supprimée de ce PC. Pour y revenir sans mot de passe, il faudra recréer une clé.",
      "Retirer");
    if (!oui) return;
    try {
      const r = await api("/api/ssh/retirer", { alias: s.alias });
      if (r.avertissement) toast(r.avertissement, "erreur", 9000);
      else toast("Clé retirée du serveur et de ce PC", "succes");
      afficher();
    } catch (e) { toast(e.message, "erreur"); }
  }

  function nouveau() {
    const champ = (attrs) => el("input", { autocomplete: "off", spellcheck: "false", ...attrs });
    const nom = champ({ placeholder: "ex. Serveur web" });
    const hote = champ({ placeholder: "ex. 203.0.113.10" });
    const port = champ({ value: "22", inputmode: "numeric" });
    const utilisateur = champ({ value: "root" });
    const mdp = champ({ type: "password", autocomplete: "new-password" });
    const oeil = el("button", { class: "icone-btn", type: "button", title: "Afficher", onclick: () => { mdp.type = mdp.type === "password" ? "text" : "password"; } }, "👁️");
    const message = el("div");
    const bouton = el("button", { class: "btn principal", onclick: async () => {
      bouton.disabled = true;
      bouton.replaceChildren(el("span", { class: "attente" }, "⏳"), " " + t("Installation…"));
      message.replaceChildren();
      try {
        const r = await api("/api/ssh/creer", { nom: nom.value, hote: hote.value, port: port.value, utilisateur: utilisateur.value, mot_de_passe: mdp.value });
        mdp.value = "";
        fenetre([
          el("div", { class: "gros" }, "✅"),
          el("h3", {}, "Clé installée"),
          el("p", {}, r.machine ? t("Connexion vérifiée sur « {machine} », sans mot de passe. Désormais, dans un terminal :", { machine: r.machine })
            : t("Connexion vérifiée, sans mot de passe. Désormais, dans un terminal :")),
          el("div", { class: "genere", style: "font-size:17px" }, brut(`ssh ${r.serveur.alias}`)),
          el("div", { class: "actions" },
            el("button", { class: "btn", onclick: () => copier(`ssh ${r.serveur.alias}`) }, "📋 Copier"),
            el("button", { class: "btn principal", onclick: () => { fermer(); afficher(); } }, "OK"))], true);
      } catch (e) {
        message.replaceChildren(el("div", { class: "alerte" }, "❌ " + e.message));
        bouton.disabled = false;
        bouton.textContent = t("🔑 Créer et installer la clé");
      }
    } }, "🔑 Créer et installer la clé");
    mdp.addEventListener("keydown", e => { if (e.key === "Enter") bouton.click(); });
    fenetre([
      el("h3", {}, "🔑 Nouveau serveur SSH"),
      el("div", { class: "note-ssh" }, "Une clé est créée pour ce serveur et déposée avec le mot de passe. Le mot de passe ne sert qu'à cette première connexion : il n'est pas enregistré."),
      el("label", { class: "champ" }, "Nom du serveur", nom),
      el("div", { class: "ligne-champs" },
        el("label", { class: "champ" }, "Adresse IP ou nom", hote),
        el("label", { class: "champ" }, "Port SSH", port)),
      el("label", { class: "champ" }, "Utilisateur", utilisateur),
      el("label", { class: "champ" }, "Mot de passe du serveur", el("div", { class: "avec-oeil" }, mdp, oeil)),
      message,
      el("div", { class: "actions" },
        el("button", { class: "btn", onclick: fermer }, "Annuler"),
        bouton)]);
    nom.focus();
  }

  VUES.ssh = { afficher, titre: "SSH", icone: "🔑", groupe: "dev", ordre: 60 };
})();
