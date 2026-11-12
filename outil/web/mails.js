"use strict";
/* Onglet « Mails » : boîte mail par IMAP / SMTP (Gmail, Yahoo, iCloud, Zoho,
   Fastmail, GMX, OVH, Orange, Free, La Poste ou réglages manuels). Le mot de
   passe est rangé dans le coffre Windows, ou dans le trousseau du bureau sous
   Linux (voir mail.py). */
(() => {
  I18N.ajouter({
    // Linux : le trousseau du bureau (GNOME Keyring, KWallet) remplace le coffre de Windows.
    "Une seule fois. Le mot de passe est rangé dans le trousseau du bureau, jamais dans un fichier.":
      "Only once. The password is stored in the desktop keyring, never in a file.",
    "🔒 Il est rangé dans le trousseau du bureau (GNOME Keyring, KWallet), jamais dans un fichier.":
      "🔒 It is stored in the desktop keyring (GNOME Keyring, KWallet), never in a file.",
    "Le mot de passe est retiré du trousseau du bureau. Vos mails ne sont pas touchés.":
      "The password is removed from the desktop keyring. Your emails are not affected.",
    "Impossible d'enregistrer le mot de passe dans le trousseau du bureau.":
      "Unable to save the password in the desktop keyring.",
    "Modèle": "Template",
    "Mails": "Mail",
    "✉️ Mails": "✉️ Mail",
    // connexion
    "Connecter votre boîte mail": "Connect your mailbox",
    "Une seule fois. Le mot de passe est rangé dans le coffre de Windows, jamais dans un fichier.":
      "Only once. The password is stored in the Windows vault, never in a file.",
    "Adresse mail": "Email address",
    "Fournisseur": "Provider",
    "Autre (réglages manuels)": "Other (manual settings)",
    "Mot de passe d'application": "App password",
    "Mot de passe": "Password",
    "Mot de passe de la boîte mail": "Mailbox password",
    "🔒 Il est rangé dans le coffre de Windows (Gestionnaire d'identification), jamais dans un fichier.":
      "🔒 It is stored in the Windows vault (Credential Manager), never in a file.",
    "Connecter": "Connect",
    "16 lettres, ex. abcd efgh ijkl mnop": "16 letters, e.g. abcd efgh ijkl mnop",
    "prenom@exemple.com": "name@example.com",
    "Connexion…": "Connecting…",
    "🎉 Boîte mail connectée !": "🎉 Mailbox connected!",
    "{nom} demande un « mot de passe d'application » : un code réservé à cet outil, que vous pouvez révoquer à tout moment.":
      "{nom} requires an “app password”: a code reserved for this tool, which you can revoke at any time.",
    "La validation en deux étapes doit être activée sur votre compte.": "Two-step verification must be turned on for your account.",
    "Ouvrez": "Open",
    "puis créez un mot de passe d'application (nom : « Mes outils »).": "then create an app password (name: “Mes outils”).",
    "Copiez le code affiché et collez-le ci-dessous.": "Copy the code shown and paste it below.",
    "Utilisez le mot de passe habituel de votre boîte {nom}.": "Use the usual password of your {nom} mailbox.",
    "Utilisez le mot de passe de votre adresse mail (celui du webmail OVHcloud). Choisissez OVHcloud pour une adresse à votre nom de domaine hébergée chez OVH.":
      "Use the password of your email address (the OVHcloud webmail one). Choose OVHcloud for an address on your own domain hosted by OVH.",
    "Dans les paramètres de GMX, activez d'abord l'accès POP3/IMAP.": "In the GMX settings, first turn on POP3/IMAP access.",
    "Dans les réglages du webmail La Poste, autorisez d'abord l'accès par un logiciel de messagerie.":
      "In the La Poste webmail settings, first allow access from email software.",
    "Indiquez les serveurs donnés par votre fournisseur (dans son aide, cherchez « réglages IMAP / SMTP »).":
      "Enter the servers given by your provider (in its help pages, look for “IMAP / SMTP settings”).",
    "Outlook, Hotmail et Live ne sont pas encore pris en charge": "Outlook, Hotmail and Live are not supported yet",
    "Microsoft n'accepte plus les mots de passe pour les logiciels de messagerie : il faut une connexion « OAuth », que Mes outils ne sait pas encore faire.":
      "Microsoft no longer accepts passwords from email software: an “OAuth” sign-in is required, which Mes outils cannot do yet.",
    "Serveur IMAP (réception)": "IMAP server (incoming)",
    "Serveur SMTP (envoi)": "SMTP server (outgoing)",
    "Port": "Port",
    "Sécurité": "Security",
    "SSL (port 465)": "SSL (port 465)",
    "STARTTLS (port 587)": "STARTTLS (port 587)",
    "Identifiant": "Username",
    "ex. imap.exemple.com": "e.g. imap.example.com",
    "ex. smtp.exemple.com": "e.g. smtp.example.com",
    "l'adresse mail, en général": "usually the email address",
    // boîte
    "✏️ Nouveau mail": "✏️ New email",
    "Déconnecter la boîte (le mot de passe est retiré du coffre)": "Disconnect the mailbox (the password is removed from the vault)",
    "Déconnecter la boîte mail ?": "Disconnect the mailbox?",
    "Le mot de passe est retiré du coffre Windows. Vos mails ne sont pas touchés.": "The password is removed from the Windows vault. Your emails are not affected.",
    "Déconnecter": "Disconnect",
    "📥 Reçus": "📥 Inbox",
    "📤 Envoyés": "📤 Sent",
    "Actualiser": "Refresh",
    "Rechercher (expéditeur, objet, texte…)": "Search (sender, subject, text…)",
    "Chargement…": "Loading…",
    "Aucun mail 🎈": "No email 🎈",
    "Choisissez un mail à lire": "Choose an email to read",
    "Ouverture…": "Opening…",
    "À : ": "To: ",
    "À": "To",
    "Cc": "Cc",
    "Objet": "Subject",
    "Message": "Message",
    "Contenu du mail": "Email content",
    "(mail vide)": "(empty email)",
    "(sans objet)": "(no subject)",
    "pièce jointe": "attachment",
    "↩️ Répondre": "↩️ Reply",
    "↩️ Répondre à tous": "↩️ Reply all",
    "➡️ Transférer": "➡️ Forward",
    "🖼️ Afficher les images": "🖼️ Show images",
    "{pieces} — à ouvrir depuis votre webmail": "{pieces} — open them from your webmail",
    "{n} Ko": "{n} KB",
    "Le {date}, {qui} a écrit :": "On {date}, {qui} wrote:",
    "---------- Message transféré ----------": "---------- Forwarded message ----------",
    "De : ": "From: ",
    "Date : ": "Date: ",
    "Objet : ": "Subject: ",
    "Annuler": "Cancel",
    "📨 Envoyer": "📨 Send",
    "Envoi…": "Sending…",
    "🚀 Mail envoyé !": "🚀 Email sent!",
    "adresse@exemple.com, autre@exemple.com": "address@example.com, other@example.com",
    // messages du serveur (mail.py)
    "Boîte mail pas encore connectée.": "Mailbox not connected yet.",
    "Indiquez l'adresse et le mot de passe.": "Enter the address and the password.",
    "Adresse mail invalide.": "Invalid email address.",
    "Fournisseur inconnu.": "Unknown provider.",
    "Indiquez le serveur IMAP et le serveur SMTP.": "Enter the IMAP server and the SMTP server.",
    "Nom de serveur invalide.": "Invalid server name.",
    "Sécurité SMTP inconnue (SSL ou STARTTLS).": "Unknown SMTP security (SSL or STARTTLS).",
    "Port invalide.": "Invalid port.",
    "Outlook, Hotmail et Live ne sont pas encore pris en charge : Microsoft n'accepte plus les mots de passe pour les logiciels de messagerie.":
      "Outlook, Hotmail and Live are not supported yet: Microsoft no longer accepts passwords from email software.",
    "Le serveur refuse ce mot de passe (il faut un mot de passe d'application, pas votre mot de passe habituel)":
      "The server rejects this password (an app password is needed, not your usual password)",
    "Le serveur refuse l'identifiant ou le mot de passe": "The server rejects the username or the password",
    "Pas de connexion au serveur mail (Internet ? nom du serveur ?)": "Cannot reach the mail server (Internet? server name?)",
    "Envoi refusé par le serveur": "Sending refused by the server",
    "Dossier introuvable dans la boîte.": "Folder not found in the mailbox.",
    "Recherche refusée par le serveur.": "Search refused by the server.",
    "Mail introuvable.": "Email not found.",
    "Indiquez au moins un destinataire.": "Enter at least one recipient.",
    "Impossible d'enregistrer le mot de passe dans le coffre Windows.": "Unable to save the password in the Windows vault.",
  });

  // Textes du guide par fournisseur (les serveurs sont dans mail.py).
  // application : lien de la page où créer le code ; deuxEtapes : validation
  // en deux étapes obligatoire avant.
  const GUIDES = {
    gmail: { nom: "Gmail", application: "https://myaccount.google.com/apppasswords", deuxEtapes: true },
    yahoo: { nom: "Yahoo", application: "https://login.yahoo.com/account/security" },
    icloud: { nom: "iCloud", application: "https://account.apple.com/account/manage", deuxEtapes: true },
    zoho: { nom: "Zoho Mail", application: "https://accounts.zoho.com/home#security/app_password", deuxEtapes: true },
    fastmail: { nom: "Fastmail", application: "https://app.fastmail.com/settings/security" },
    gmx: { nom: "GMX", avant: "Dans les paramètres de GMX, activez d'abord l'accès POP3/IMAP." },
    ovh: { nom: "OVHcloud", texte: "Utilisez le mot de passe de votre adresse mail (celui du webmail OVHcloud). Choisissez OVHcloud pour une adresse à votre nom de domaine hébergée chez OVH." },
    orange: { nom: "Orange" },
    free: { nom: "Free" },
    laposte: { nom: "La Poste", avant: "Dans les réglages du webmail La Poste, autorisez d'abord l'accès par un logiciel de messagerie." },
    autre: { nom: "Autre (réglages manuels)", texte: "Indiquez les serveurs donnés par votre fournisseur (dans son aide, cherchez « réglages IMAP / SMTP »)." },
  };
  const MICROSOFT = /^(outlook\.|hotmail\.|live\.|msn\.com$|passport\.com$)/i;

  const M = { etat: null, dossier: "recus", recherche: "", liste: [], ouvert: null, images: false, charge: false };

  const style = document.createElement("style");
  style.textContent = `
    .boite { display: grid; grid-template-columns: 380px 1fr; gap: 16px; height: max(420px, calc(100vh - var(--entete, 74px) - 96px)); }
    .boite .colonne-liste, .boite .lecture { background: var(--carte); border-radius: var(--rayon); box-shadow: var(--ombre); overflow: hidden; display: flex; flex-direction: column; animation: apparait .35s both; }
    .liste-mails { overflow-y: auto; flex: 1; }
    .mail { padding: 11px 16px; border-bottom: 1px solid var(--ligne); cursor: pointer; display: flex; gap: 11px; transition: background .15s; }
    .mail:hover { background: var(--surface); }
    .mail.actif { background: var(--violet-clair); }
    .mail .av { width: 38px; height: 38px; border-radius: 13px; display: grid; place-items: center; color: #fff; font-weight: 600; flex: none; font-size: 14px; }
    .mail .contenu { min-width: 0; flex: 1; }
    .mail .l1 { display: flex; gap: 8px; align-items: baseline; }
    .mail .qui { font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex: 1; }
    .mail .quand { font-size: 12px; color: var(--doux); white-space: nowrap; }
    .mail .objet { font-size: 13.5px; color: var(--doux); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .mail.non-lu .qui, .mail.non-lu .objet { font-weight: 600; color: var(--encre); }
    .point-nonlu { width: 8px; height: 8px; border-radius: 50%; background: var(--corail); flex: none; margin-top: 6px; }
    .entete-liste { padding: 12px; display: flex; gap: 8px; align-items: center; border-bottom: 1px solid var(--ligne); flex-wrap: wrap; }
    .entete-liste input { flex: 1 1 100%; min-width: 0; border: 1.5px solid var(--ligne); border-radius: 12px; padding: 8px 11px; outline: none; background: var(--champ); color: var(--encre); }
    .entete-liste input:focus { border-color: var(--violet); background: var(--champ-focus); }
    .lecture .tete { padding: 18px 22px 12px; border-bottom: 1px solid var(--ligne); }
    .lecture .tete h3 { margin: 0 0 10px; font-size: 19px; }
    .lecture .meta { font-size: 13px; color: var(--doux); display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
    .lecture .actions-mail { display: flex; gap: 6px; margin-top: 12px; flex-wrap: wrap; }
    .lecture iframe { flex: 1; border: 0; width: 100%; background: #fff; }
    .lecture .texte-brut { flex: 1; overflow: auto; padding: 18px 22px; white-space: pre-wrap; font-size: 14.5px; line-height: 1.5; }
    .lecture .vide-lecture { flex: 1; display: grid; place-items: center; color: var(--doux); text-align: center; }
    .lecture .vide-lecture div div { font-size: 58px; }
    .pieces { padding: 8px 22px; font-size: 12.5px; color: var(--doux); border-top: 1px solid var(--ligne); }
    .connexion { max-width: 640px; margin: 10px auto; background: var(--carte); border-radius: var(--rayon); box-shadow: var(--ombre); padding: 28px; animation: apparait .35s both; }
    .connexion h3 { margin: 0 0 6px; font-size: 22px; }
    .connexion ol { padding-left: 20px; line-height: 1.7; color: var(--encre); }
    .connexion a { color: var(--violet); font-weight: 700; }
    .connexion .guide { background: var(--surface); border-radius: var(--rayon); padding: 4px 16px; margin: 0 0 16px; color: var(--encre); font-size: 14px; }
    .connexion .guide p { margin: 10px 0; }
    .connexion .alerte-ms { background: var(--ambre-clair); color: var(--ambre-texte); border-radius: var(--rayon); padding: 12px 16px; margin: 0 0 16px; font-size: 14px; }
    .connexion .alerte-ms b { display: block; margin-bottom: 4px; }
    .grille-mail { display: grid; grid-template-columns: 1fr 110px; gap: 0 12px; }
    .chargement-mails { padding: 30px; text-align: center; color: var(--doux); }
  `;
  document.head.append(style);

  const racine = () => $("#vue-mails");
  // Données de l'utilisateur (objets, noms, textes) : jamais traduites.
  const brut = s => document.createTextNode(s ?? "");
  const COULEURS_AV = ["#6c4cf5", "#ff7a59", "#18b597", "#ffb020", "#e5488d", "#2f8cff"];
  const couleur = x => { let h = 0; for (const c of x || "?") h = (h * 31 + c.charCodeAt(0)) >>> 0; return COULEURS_AV[h % COULEURS_AV.length]; };
  const initiale = x => (x || "?").replace(/[^\p{L}\p{N}]/gu, "").charAt(0).toUpperCase() || "?";
  function quand(iso) {
    if (!iso) return "";
    const d = new Date(iso), auj = new Date();
    if (d.toDateString() === auj.toDateString()) return d.toLocaleTimeString(I18N.locale(), { hour: "2-digit", minute: "2-digit" });
    if (d.getFullYear() === auj.getFullYear()) return d.toLocaleDateString(I18N.locale(), { day: "numeric", month: "short" });
    return d.toLocaleDateString(I18N.locale());
  }
  const sujet = s => (s === "(sans objet)" ? t(s) : s);
  const nomFournisseur = id => t(GUIDES[id]?.nom || (M.etat?.fournisseurs || []).find(f => f.id === id)?.nom || id || "");

  async function afficher() {
    try { M.etat = await api("/api/mail/etat"); }
    catch (e) { racine().replaceChildren(el("div", { class: "vide" }, "😕 " + e.message)); return; }
    if (!M.etat.configuree) return ecranConnexion();
    if (!M.charge) dessinerBoite();
    rafraichir();
  }

  // -- première connexion ------------------------------------------------------
  /** Fournisseur deviné d'après le domaine (liste envoyée par mail.py). */
  function detecter(adresse) {
    const d = (adresse.split("@")[1] || "").trim().toLowerCase();
    if (!d) return null;
    if (MICROSOFT.test(d)) return "outlook";
    return (M.etat.fournisseurs || []).find(f => (f.domaines || []).includes(d))?.id || null;
  }

  function ecranConnexion() {
    M.charge = false;
    const deja = M.etat.reglages || {};
    // Fournisseur choisi à la main (sinon : deviné d'après l'adresse).
    let choisi = deja.fournisseur && deja.fournisseur !== "outlook" && deja.fournisseur !== detecter(M.etat.adresse || "") ? deja.fournisseur : null;
    const adresse = el("input", { type: "email", value: M.etat.adresse || "", autocomplete: "username", placeholder: "prenom@exemple.com" });
    const secret = el("input", { type: "password", autocomplete: "new-password" });
    const liste = el("select", {}, Object.keys(GUIDES).map(id => el("option", { value: id }, nomFournisseur(id))));
    const imapHote = el("input", { value: deja.fournisseur === "autre" ? deja.imap_hote || "" : "", placeholder: "ex. imap.exemple.com", spellcheck: "false" });
    const imapPort = el("input", { type: "number", value: String(deja.fournisseur === "autre" ? deja.imap_port || 993 : 993) });
    const smtpHote = el("input", { value: deja.fournisseur === "autre" ? deja.smtp_hote || "" : "", placeholder: "ex. smtp.exemple.com", spellcheck: "false" });
    const securite = el("select", {}, el("option", { value: "ssl" }, "SSL (port 465)"), el("option", { value: "starttls" }, "STARTTLS (port 587)"));
    securite.value = deja.smtp_securite === "starttls" ? "starttls" : "ssl";
    const smtpPort = el("input", { type: "number", value: String(deja.fournisseur === "autre" ? deja.smtp_port || 465 : 465) });
    securite.onchange = () => { smtpPort.value = securite.value === "ssl" ? "465" : "587"; };
    const identifiant = el("input", { value: deja.fournisseur === "autre" && deja.identifiant !== M.etat.adresse ? deja.identifiant || "" : "",
      placeholder: "l'adresse mail, en général", autocomplete: "off", spellcheck: "false" });
    const manuels = el("div", {},
      el("div", { class: "grille-mail" },
        el("label", { class: "champ" }, "Serveur IMAP (réception)", imapHote), el("label", { class: "champ" }, "Port", imapPort)),
      el("div", { class: "grille-mail" },
        el("label", { class: "champ" }, "Serveur SMTP (envoi)", smtpHote), el("label", { class: "champ" }, "Port", smtpPort)),
      el("label", { class: "champ" }, "Sécurité", securite),
      el("label", { class: "champ" }, "Identifiant", identifiant));
    const guide = el("div");
    const libelleSecret = el("span");
    const zoneSecret = el("label", { class: "champ" }, libelleSecret, secret,
      el("small", {}, selonSysteme("🔒 Il est rangé dans le coffre de Windows (Gestionnaire d'identification), jamais dans un fichier.",
        "🔒 Il est rangé dans le trousseau du bureau (GNOME Keyring, KWallet), jamais dans un fichier.")));
    const bouton = el("button", { class: "btn principal", onclick: connecter }, "Connecter");
    const actions = el("div", { class: "actions" }, bouton);

    function fournisseur() {
      const auto = detecter(adresse.value);
      // Sans liste (ancienne version du serveur) : Gmail, comme avant.
      return auto === "outlook" ? "outlook" : choisi || auto || (M.etat.fournisseurs && adresse.value.includes("@") ? "autre" : "gmail");
    }
    function majGuide() {
      const id = fournisseur();
      const microsoft = id === "outlook";
      liste.disabled = microsoft;
      if (!microsoft) liste.value = id;
      manuels.hidden = microsoft || id !== "autre";
      zoneSecret.hidden = actions.hidden = microsoft;
      if (microsoft) {
        guide.replaceChildren(el("div", { class: "alerte-ms" },
          el("b", {}, "🚧 " + t("Outlook, Hotmail et Live ne sont pas encore pris en charge")),
          "Microsoft n'accepte plus les mots de passe pour les logiciels de messagerie : il faut une connexion « OAuth », que Mes outils ne sait pas encore faire."));
        return;
      }
      const g = GUIDES[id];
      if (g.application) {
        libelleSecret.textContent = t("Mot de passe d'application");
        secret.placeholder = id === "gmail" ? t("16 lettres, ex. abcd efgh ijkl mnop") : "";
        const lien = el("a", { href: g.application, target: "_blank", rel: "noopener" }, g.application.replace(/^https:\/\//, "").replace(/[#?].*$/, ""));
        guide.replaceChildren(el("div", { class: "guide" },
          el("p", {}, t("{nom} demande un « mot de passe d'application » : un code réservé à cet outil, que vous pouvez révoquer à tout moment.", { nom: g.nom })),
          el("ol", {},
            g.deuxEtapes ? el("li", {}, "La validation en deux étapes doit être activée sur votre compte.") : null,
            el("li", {}, t("Ouvrez"), " ", lien, ", ", t("puis créez un mot de passe d'application (nom : « Mes outils »).")),
            el("li", {}, "Copiez le code affiché et collez-le ci-dessous."))));
      } else {
        libelleSecret.textContent = t(id === "autre" ? "Mot de passe" : "Mot de passe de la boîte mail");
        secret.placeholder = "";
        guide.replaceChildren(el("div", { class: "guide" },
          g.avant ? el("p", {}, g.avant) : null,
          el("p", {}, g.texte || t("Utilisez le mot de passe habituel de votre boîte {nom}.", { nom: g.nom }))));
      }
    }
    // Domaine connu (gmail.com, orange.fr…) : il l'emporte sur un choix précédent.
    adresse.addEventListener("input", () => { if (detecter(adresse.value)) choisi = null; majGuide(); });
    liste.addEventListener("change", () => { choisi = liste.value; majGuide(); });

    async function connecter() {
      const id = fournisseur();
      if (id === "outlook") return;
      const reglages = { fournisseur: id };
      if (id === "autre") Object.assign(reglages, { imap_hote: imapHote.value.trim(), imap_port: Number(imapPort.value) || 993,
        smtp_hote: smtpHote.value.trim(), smtp_port: Number(smtpPort.value) || 465, smtp_securite: securite.value,
        identifiant: identifiant.value.trim() });
      bouton.disabled = true; bouton.textContent = t("Connexion…");
      try {
        await api("/api/mail/connexion", { adresse: adresse.value.trim(), secret: secret.value, reglages });
        secret.value = "";
        toast("Boîte mail connectée !", "succes");
        M.etat = await api("/api/mail/etat");
        dessinerBoite(); rafraichir(); compterMails();
      } catch (e) { toast(e.message, "erreur", 8000); }
      finally { bouton.disabled = false; bouton.textContent = t("Connecter"); }
    }
    secret.addEventListener("keydown", e => { if (e.key === "Enter") connecter(); });

    racine().replaceChildren(el("div", { class: "connexion" },
      el("div", { style: "font-size:48px" }, "✉️"),
      el("h3", {}, "Connecter votre boîte mail"),
      el("p", { style: "color:var(--doux);margin-top:0" }, selonSysteme("Une seule fois. Le mot de passe est rangé dans le coffre de Windows, jamais dans un fichier.",
        "Une seule fois. Le mot de passe est rangé dans le trousseau du bureau, jamais dans un fichier.")),
      el("div", { class: "grille-mail", style: "grid-template-columns:1fr 220px" },
        el("label", { class: "champ" }, "Adresse mail", adresse),
        el("label", { class: "champ" }, "Fournisseur", liste)),
      guide, manuels, zoneSecret, actions));
    majGuide();
  }

  // -- la boîte --------------------------------------------------------------
  function dessinerBoite() {
    M.charge = true;
    const recherche = el("input", { placeholder: "Rechercher (expéditeur, objet, texte…)", value: M.recherche,
      onkeydown: e => { if (e.key === "Enter") { M.recherche = e.target.value; rafraichir(true); } } });
    const fourn = M.etat.reglages?.fournisseur;
    racine().replaceChildren(
      el("div", { class: "barre-vue" },
        el("h2", {}, "✉️ Mails"),
        el("span", { style: "color:var(--doux);font-size:13px" }, brut(M.etat.adresse + (fourn && fourn !== "autre" ? " · " + nomFournisseur(fourn) : ""))),
        el("div", { class: "espace" }),
        el("button", { class: "btn principal", onclick: () => composer({}) }, "✏️ Nouveau mail"),
        el("button", { class: "btn discret", title: "Déconnecter la boîte (le mot de passe est retiré du coffre)", onclick: async () => {
          if (!(await confirmer("🔌", "Déconnecter la boîte mail ?", selonSysteme("Le mot de passe est retiré du coffre Windows. Vos mails ne sont pas touchés.",
            "Le mot de passe est retiré du trousseau du bureau. Vos mails ne sont pas touchés."), "Déconnecter"))) return;
          await api("/api/mail/deconnexion", {}); M.etat.configuree = false; ecranConnexion(); compterMails();
        } }, "🔌")),
      el("div", { class: "boite" },
        el("div", { class: "colonne-liste" },
          el("div", { class: "entete-liste" },
            el("div", { class: "puces" }, [["recus", "📥 Reçus"], ["envoyes", "📤 Envoyés"]].map(([d, libelle]) =>
              el("button", { class: "puce" + (M.dossier === d ? " actif" : ""), onclick: ev => {
                M.dossier = d; ev.currentTarget.parentNode.querySelectorAll(".puce").forEach(p => p.classList.toggle("actif", p === ev.currentTarget)); rafraichir(true);
              } }, libelle))),
            el("button", { class: "btn discret", title: "Actualiser", onclick: () => rafraichir(true) }, "⟳"),
            recherche),
          el("div", { class: "liste-mails", id: "liste-mails" }, el("div", { class: "chargement-mails" }, "Chargement…"))),
        el("div", { class: "lecture", id: "lecture" },
          el("div", { class: "vide-lecture" }, el("div", {}, el("div", {}, "📬"), "Choisissez un mail à lire")))));
  }

  async function rafraichir(montrerChargement = false) {
    const box = $("#liste-mails");
    if (!box) return;
    if (montrerChargement) box.replaceChildren(el("div", { class: "chargement-mails" }, "Chargement…"));
    try {
      M.liste = await api("/api/mail/liste", { dossier: M.dossier, recherche: M.recherche });
    } catch (e) { box.replaceChildren(el("div", { class: "chargement-mails" }, "😕 " + e.message)); return; }
    if (!M.liste.length) { box.replaceChildren(el("div", { class: "chargement-mails" }, "Aucun mail 🎈")); return; }
    box.replaceChildren(...M.liste.map(m => {
      const qui = M.dossier === "envoyes" ? m.a : m.de;
      return el("div", { class: "mail" + (m.lu ? "" : " non-lu") + (M.ouvert?.uid === m.uid ? " actif" : ""), onclick: () => ouvrir(m) },
        el("div", { class: "av", style: `background:${couleur(qui.adresse)}` }, brut(initiale(qui.nom))),
        el("div", { class: "contenu" },
          el("div", { class: "l1" }, el("span", { class: "qui" }, brut((M.dossier === "envoyes" ? t("À : ") : "") + (qui.nom || qui.adresse))), el("span", { class: "quand" }, quand(m.date))),
          el("div", { class: "objet" }, brut(sujet(m.sujet)))),
        m.lu ? null : el("span", { class: "point-nonlu" }));
    }));
  }

  async function ouvrir(m) {
    M.images = false;
    const zone = $("#lecture");
    zone.replaceChildren(el("div", { class: "vide-lecture" }, "Ouverture…"));
    try {
      M.ouvert = await api("/api/mail/lire", { uid: m.uid, dossier: M.dossier });
      m.lu = true;
      dessinerLecture();
      rafraichir(); compterMails();
    } catch (e) { zone.replaceChildren(el("div", { class: "vide-lecture" }, "😕 " + e.message)); }
  }

  function srcdoc(html, images) {
    // Pas de script, et pas d'image distante sans votre accord : une image
    // distante dit à l'expéditeur que vous avez ouvert son mail.
    const csp = `default-src 'none'; style-src 'unsafe-inline' data:; font-src data:; img-src ${images ? "* data: blob:" : "data: cid:"};`;
    return `<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="${csp}"><base target="_blank">
      <style>body{font-family:Segoe UI,sans-serif;font-size:14.5px;color:#1f1a3a;background:#fff;margin:18px 22px;word-wrap:break-word}img{max-width:100%;height:auto}</style></head><body>${html}</body></html>`;
  }

  const dateLongue = (iso, style = "medium") => iso ? new Date(iso).toLocaleString(I18N.locale(), { dateStyle: style, timeStyle: "short" }) : "";

  function dessinerLecture() {
    const m = M.ouvert;
    const zone = $("#lecture");
    const contenu = m.html
      ? el("iframe", { sandbox: "allow-popups allow-popups-to-escape-sandbox", title: "Contenu du mail" })
      : el("div", { class: "texte-brut" }, m.texte ? brut(m.texte) : t("(mail vide)"));
    if (m.html) contenu.srcdoc = srcdoc(m.html, M.images);
    const pieces = m.pieces.map(p => `${p.nom === "pièce jointe" ? t(p.nom) : p.nom} (${t("{n} Ko", { n: Math.max(1, Math.round(p.taille / 1024)) })})`).join(" · ");
    zone.replaceChildren(
      el("div", { class: "tete" },
        el("h3", {}, brut(sujet(m.sujet))),
        el("div", { class: "meta" },
          el("span", { class: "av", style: `background:${couleur(m.de.adresse)};width:30px;height:30px;border-radius:10px;display:grid;place-items:center;color:#fff;font-weight: 600` }, brut(initiale(m.de.nom))),
          el("b", { style: "color:var(--encre)" }, brut(m.de.nom)), el("span", {}, brut(`<${m.de.adresse}>`)),
          el("span", {}, "· " + dateLongue(m.date))),
        el("div", { class: "meta", style: "margin-top:4px" }, brut(t("À : ") + (m.a || "") + (m.cc ? " · Cc : " + m.cc : ""))),
        el("div", { class: "actions-mail" },
          el("button", { class: "btn principal", onclick: () => repondre(false) }, "↩️ Répondre"),
          m.cc || (m.a || "").includes(",") ? el("button", { class: "btn", onclick: () => repondre(true) }, "↩️ Répondre à tous") : null,
          el("button", { class: "btn", onclick: transferer }, "➡️ Transférer"),
          m.html && !M.images ? el("button", { class: "btn discret", onclick: () => { M.images = true; dessinerLecture(); } }, "🖼️ Afficher les images") : null)),
      contenu,
      m.pieces.length ? el("div", { class: "pieces" }, brut("📎 " + t("{pieces} — à ouvrir depuis votre webmail", { pieces }))) : null);
  }

  // -- écrire --------------------------------------------------------------------
  const texteDe = m => m.texte || (m.html ? new DOMParser().parseFromString(m.html, "text/html").body.innerText : "");
  function citation(m) {
    return "\n\n\n" + t("Le {date}, {qui} a écrit :", { date: dateLongue(m.date, "long"), qui: `${m.de.nom} <${m.de.adresse}>` }) + "\n"
      + texteDe(m).split("\n").map(l => "> " + l).join("\n");
  }
  function repondre(tous) {
    const m = M.ouvert;
    const moi = (M.etat.adresse || "").toLowerCase();
    const autres = tous ? [m.a, m.cc].join(",").split(",").map(x => x.trim()).filter(x => x && !x.toLowerCase().includes(moi)) : [];
    composer({ a: m.de.adresse, cc: autres.join(", "), sujet: /^re\s*:/i.test(m.sujet) ? m.sujet : "Re: " + m.sujet,
      corps: citation(m), reponse_a: m.message_id, references: m.references });
  }
  function transferer() {
    const m = M.ouvert;
    const prefixe = I18N.langue === "en" ? "Fwd: " : "Tr: ";
    composer({ sujet: /^(tr|fwd?)\s*:/i.test(m.sujet) ? m.sujet : prefixe + m.sujet,
      corps: `\n\n\n${t("---------- Message transféré ----------")}\n${t("De : ")}${m.de.nom} <${m.de.adresse}>\n${t("Date : ")}${dateLongue(m.date)}\n${t("Objet : ")}${m.sujet}\n${t("À : ")}${m.a}\n\n${texteDe(m)}` });
  }
  function composer(v) {
    const a = el("input", { value: v.a || "", placeholder: "adresse@exemple.com, autre@exemple.com" });
    const cc = el("input", { value: v.cc || "" });
    const objet = el("input", { value: v.sujet || "" });
    const corps = el("textarea", { rows: 12, value: v.corps || "", style: "font-family:inherit" });
    const envoyer = el("button", { class: "btn principal", onclick: async () => {
      envoyer.disabled = true; envoyer.textContent = t("Envoi…");
      try {
        await api("/api/mail/envoyer", { a: a.value, cc: cc.value, sujet: objet.value, corps: corps.value, reponse_a: v.reponse_a, references: v.references });
        fermer(); toast("Mail envoyé !", "succes");
        if (M.dossier === "envoyes") rafraichir();
      } catch (e) { toast(e.message, "erreur", 7000); envoyer.disabled = false; envoyer.textContent = t("📨 Envoyer"); }
    } }, "📨 Envoyer");
    // Application Modèles de messages : insérer un texte prêt à l'emploi.
    // Le mail en cours est gardé (la fenêtre est remplacée le temps du choix).
    const boutonModele = window.Modeles && appActive("modeles")
      ? el("button", { class: "btn", style: "margin-right:auto", onclick: () => {
          const enCours = { ...v, a: a.value, cc: cc.value, sujet: objet.value, corps: corps.value };
          Modeles.choisir(r => composer({ ...enCours,
            a: enCours.a || r.a || "",
            sujet: enCours.sujet || r.objet || "",
            corps: (r.texte || "") + (enCours.corps ? "\n\n" + enCours.corps : "") }));
        } }, icone("message-square-text"), "Modèle")
      : null;
    fenetre([
      el("h3", {}, v.reponse_a ? "↩️ Répondre" : "✏️ Nouveau mail"),
      el("label", { class: "champ" }, "À", a),
      el("label", { class: "champ" }, "Cc", cc),
      el("label", { class: "champ" }, "Objet", objet),
      el("label", { class: "champ" }, "Message", corps),
      el("div", { class: "actions" }, boutonModele, el("button", { class: "btn", onclick: fermer }, "Annuler"), envoyer)]);
    $("#fenetre").style.width = "min(720px, 94vw)";
    setTimeout(() => { (v.a ? corps : a).focus(); if (v.a) corps.setSelectionRange(0, 0); }, 60);
  }

  VUES.mails = { afficher, titre: "Mails", icone: "✉️", groupe: "quotidien", ordre: 10 };
})();
