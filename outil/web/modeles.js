"use strict";
/* Application « Modèles de messages » (voir modeles.py) : textes prêts à
   l'emploi avec des variables entre accolades ({prenom}, {montant}…).
   Clic sur un modèle : on remplit les variables (depuis un contact si
   l'application Contacts est là), on voit le texte final, puis on le copie ou
   on écrit le mail. Recherche, catégories, tris, favoris, export / import.

   Pour les autres applications (ex. Mails) :
     Modeles.choisir(rappel)  → choisir un modèle, le remplir, puis
                                rappel({ a, objet, texte }) au lieu de copier. */
(() => {
  I18N.ajouter({
    "Modèles de messages": "Message templates",
    "Réponses types, relances, confirmations de rendez-vous : des textes prêts à l'emploi, avec variables.":
      "Standard replies, reminders, appointment confirmations: ready-to-use texts with variables.",
    "Nouveau modèle": "New template",
    "Modifier le modèle": "Edit template",
    "Chercher dans les modèles…": "Search templates…",
    "Toutes les catégories": "All categories",
    "Favoris": "Favourites",
    "Plus utilisés": "Most used",
    "A → Z": "A → Z",
    "Importer": "Import",
    "Exporter": "Export",
    "Importer des modèles (fichier JSON)": "Import templates (JSON file)",
    "Exporter les modèles (fichier JSON)": "Export templates (JSON file)",
    "Titre": "Title",
    "Catégorie": "Category",
    "Langue": "Language",
    "Français": "French",
    "Anglais": "English",
    "Autre": "Other",
    "Objet": "Subject",
    "facultatif, pour un mail": "optional, for an email",
    "Texte": "Text",
    "Insérer": "Insert",
    "Variable libre": "Custom variable",
    "Nom de la variable (lettres, chiffres, _ ou -)": "Variable name (letters, digits, _ or -)",
    "Variables détectées :": "Detected variables:",
    "Insérer :": "Insert:",
    "Variable libre :": "Custom variable:",
    "Aucune variable pour l'instant.": "No variable yet.",
    "Écrivez une variable entre accolades, par exemple {prenom} : elle sera demandée à chaque utilisation.":
      "Write a variable between braces, e.g. {prenom}: you will be asked for it each time.",
    "ex. Relance de paiement": "e.g. Payment reminder",
    "ex. Relances": "e.g. Reminders",
    "ex. Facture {numero_facture}": "e.g. Invoice {numero_facture}",
    "Favori (aussi dans Ctrl + K)": "Favourite (also in Ctrl + K)",
    "Annuler": "Cancel",
    "Enregistrer": "Save",
    "Ajouter": "Add",
    "Modifier": "Edit",
    "Dupliquer": "Duplicate",
    "Supprimer": "Delete",
    "Ajouter aux favoris": "Add to favourites",
    "Retirer des favoris": "Remove from favourites",
    "Favori": "Favourite",
    "Utiliser ce modèle": "Use this template",
    "Contact": "Contact",
    "Aucun contact": "No contact",
    "Destinataire": "Recipient",
    "pour « Écrire le mail »": "for “Write the email”",
    "Aperçu": "Preview",
    "Objet :": "Subject:",
    "Copier l'objet": "Copy the subject",
    "Les variables laissées vides restent entre accolades.": "Variables left empty stay between braces.",
    "Ce modèle n'a pas de variable.": "This template has no variable.",
    "Copier": "Copy",
    "Écrire le mail": "Write the email",
    "Insérer dans le mail": "Insert into the email",
    "Texte copié": "Text copied",
    "Objet copié": "Subject copied",
    "Mail ouvert dans votre messagerie": "Email opened in your mail app",
    "Texte trop long pour le lien : il est copié, collez-le dans le mail.":
      "Text too long for the link: it has been copied, paste it into the email.",
    "Modèle enregistré": "Template saved",
    "Modèle dupliqué": "Template duplicated",
    "Modèle supprimé": "Template deleted",
    "Supprimer ce modèle ?": "Delete this template?",
    "Il disparaît définitivement.": "It will be gone for good.",
    "Aucun modèle ne correspond.": "No template matches.",
    "Aucun modèle pour l'instant.": "No template yet.",
    "Créez le vôtre, ou remettez les exemples fournis.": "Create your own, or restore the examples provided.",
    "Remettre les exemples": "Restore the examples",
    "jamais utilisé": "never used",
    "1 utilisation": "used once",
    "{n} utilisations": "used {n} times",
    "{n} modèles": "{n} templates",
    "Utiliser le modèle : {titre}": "Use template: {titre}",
    "Choisir un modèle": "Choose a template",
    "{n} exemples ajoutés": "{n} examples added",
    "Les exemples sont déjà là": "The examples are already there",
    "{n} modèles importés": "{n} templates imported",
    "Aucun nouveau modèle dans ce fichier": "No new template in this file",
    "{n} déjà présents, ignorés": "{n} already there, skipped",
    "{n} invalides, ignorés": "{n} invalid, skipped",
    "Fichier illisible : ce n'est pas du JSON.": "Unreadable file: this is not JSON.",
    "Modèles exportés": "Templates exported",
    "Prénom": "First name",
    "Nom de famille": "Last name",
    "Entreprise": "Company",
    "Date": "Date",
    "Montant": "Amount",
    "E-mail": "Email",
    "Téléphone": "Phone",
    // Erreurs du serveur (modeles.py)
    "Modèle invalide.": "Invalid template.",
    "Donnez un titre au modèle.": "Give the template a title.",
    "Le texte du modèle est vide.": "The template text is empty.",
    "Titre trop long (120 caractères au plus).": "Title too long (120 characters max).",
    "Catégorie trop longue (40 caractères au plus).": "Category too long (40 characters max).",
    "Objet trop long (250 caractères au plus).": "Subject too long (250 characters max).",
    "Texte trop long (20 000 caractères au plus).": "Text too long (20,000 characters max).",
    "Modèle introuvable.": "Template not found.",
    "Ce fichier n'est pas un export de modèles de messages.": "This file is not a message templates export.",
    "Trop de modèles dans ce fichier (2 000 au plus).": "Too many templates in this file (2,000 max).",
    "Aucune messagerie n'est associée aux liens e-mail sur ce PC.": "No mail app is associated with email links on this PC.",
  });
  I18N.motifs([[/^Adresse e-mail invalide : (.*)$/, "Invalid email address: $1"]]);

  const style = document.createElement("style");
  style.textContent = `
    .mo-filtres { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin: -6px 0 14px; }
    .mo-filtres select { max-width: 220px; }
    .mo-filtres .espace { flex: 1; }
    .mo-favori { color: var(--ambre-texte); display: inline-flex; }
    .mo-favori svg.ico { fill: currentColor; }
    .icone-btn.mo-actif { color: var(--ambre-texte); }
    .icone-btn.mo-actif svg.ico { fill: currentColor; }
    .mo-vide { display: flex; flex-direction: column; align-items: center; gap: 10px; }
    .mo-vide p { margin: 0; }
    .mo-vide .mo-boutons { display: flex; gap: 8px; }
    .mo-vide .btn svg.ico { display: inline-block; width: 1.1em; height: 1.1em; margin: 0; color: inherit; }
    .mo-grille { display: grid; grid-template-columns: 1fr 1fr; gap: 0 12px; }
    .mo-grille .champ { margin-bottom: 10px; }
    .mo-grille .large { grid-column: 1 / -1; }
    .mo-editeur textarea { min-height: 220px; resize: vertical; font-family: inherit; font-weight: 400; line-height: 1.5; }
    .mo-inserer { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin: -6px 0 6px; font-size: 12.5px; color: var(--doux); }
    .mo-inserer .mo-var { font-family: var(--mono); font-size: 12px; font-weight: 400; }
    .ligne:hover .ligne-cote .mo-favori { display: none; }
    .mo-detectees { font-size: 12.5px; color: var(--doux); display: flex; gap: 6px; flex-wrap: wrap; align-items: center; min-height: 20px; margin-bottom: 12px; }
    .mo-detectees .tag { font-family: var(--mono); }
    .mo-case { display: flex; align-items: center; gap: 8px; font-size: 13.5px; color: var(--encre); cursor: pointer; }
    .mo-utiliser h3 { display: flex; align-items: center; gap: 8px; }
    .mo-sous-titre { color: var(--doux); font-size: 12.5px; margin: -2px 0 14px; display: flex; gap: 6px; align-items: center; }
    .mo-section { font-size: 11.5px; font-weight: 600; color: var(--gris); text-transform: uppercase; letter-spacing: .04em; margin: 4px 0 8px; }
    .mo-apercu { border: 1px solid var(--ligne); border-radius: 8px; background: var(--surface); padding: 12px 14px; max-height: 260px; overflow: auto; }
    .mo-apercu .mo-objet { display: flex; align-items: center; gap: 8px; padding-bottom: 8px; margin-bottom: 8px; border-bottom: 1px solid var(--ligne); font-weight: 500; }
    .mo-apercu .mo-objet .lib { color: var(--gris); font-weight: 400; flex: none; }
    .mo-apercu .mo-objet .val { flex: 1; min-width: 0; overflow-wrap: anywhere; }
    .mo-apercu .mo-objet .icone-btn { width: 24px; height: 24px; }
    .mo-apercu .mo-corps { white-space: pre-wrap; overflow-wrap: anywhere; line-height: 1.5; }
    .mo-manque { color: var(--ambre-texte); background: var(--ambre-clair); border-radius: 3px; padding: 0 2px; }
    .mo-note { font-size: 12px; color: var(--gris); margin-top: 6px; }
    .mo-choix { max-height: 50vh; overflow: auto; }
    @media (max-width: 720px) { .mo-grille { grid-template-columns: 1fr; } }
  `;
  document.head.append(style);

  const X = { modeles: [], total: 0, categories: [], recherche: "", categorie: "", tri: "favoris", favoris: [] };
  const STANDARD = ["prenom", "nom", "entreprise", "date", "montant"];
  const LIBELLES = { prenom: "Prénom", nom: "Nom de famille", entreprise: "Entreprise", date: "Date", montant: "Montant",
    email: "E-mail", telephone: "Téléphone" };
  const CATEGORIES_PROPOSEES = ["Réponses types", "Relances", "Rendez-vous", "Prise de contact", "Suivi client", "Refus", "Mails récurrents"];
  const RE_VARIABLE = /\{([\p{L}_][\p{L}\p{N}_-]{0,39})\}/gu;
  let minuterie = null;

  /** Texte venu des données : jamais traduit ni transformé par la page. */
  const brut = s => document.createTextNode(String(s ?? ""));
  const sansAccents = s => String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const cleVariable = nom => sansAccents(nom);

  /** Les variables d'un ou plusieurs textes : [{ cle, nom }] (même règle que modeles.py). */
  function variablesDe(...textes) {
    const vues = new Map();
    for (const texte of textes) for (const m of String(texte || "").matchAll(RE_VARIABLE)) {
      const cle = cleVariable(m[1]);
      if (!vues.has(cle)) vues.set(cle, m[1]);
    }
    return [...vues].map(([cle, nom]) => ({ cle, nom }));
  }
  /** Le texte final, en morceaux : chaînes et { manque } pour les variables vides. */
  function morceaux(texte, valeurs) {
    const sortie = [];
    let dernier = 0;
    for (const m of String(texte || "").matchAll(RE_VARIABLE)) {
      sortie.push(texte.slice(dernier, m.index));
      const v = valeurs[cleVariable(m[1])];
      sortie.push(v ? v : { manque: m[0] });
      dernier = m.index + m[0].length;
    }
    sortie.push(String(texte || "").slice(dernier));
    return sortie;
  }
  const remplir = (texte, valeurs) => morceaux(texte, valeurs).map(x => (typeof x === "string" ? x : x.manque)).join("");
  /** Le libellé d'une variable : « Prénom », ou {numéro_de_facture} → « Numéro de facture ». */
  const libelle = v => {
    if (LIBELLES[v.cle]) return t(LIBELLES[v.cle]);
    const s = v.nom.replace(/_+/g, " ").trim();
    return s.charAt(0).toUpperCase() + s.slice(1);
  };
  const usage = n => (n === 0 ? t("jamais utilisé") : n === 1 ? t("1 utilisation") : t("{n} utilisations", { n }));
  const erreur = e => toast(e.message, "erreur", 6000);

  // ------------------------------------------------------------ liste
  async function charger() {
    const r = await api("/api/modeles/liste", { recherche: X.recherche, categorie: X.categorie, tri: X.tri });
    Object.assign(X, r);
    if (X.categorie && !X.categories.some(c => sansAccents(c) === sansAccents(X.categorie))) { X.categorie = ""; return charger(); }
    if (X.recherche || X.categorie) chargerFavoris(); else X.favoris = X.modeles.filter(m => m.favori);
    dessiner();
  }
  const recharger = () => charger().catch(erreur);
  // La palette (Ctrl + K) a besoin des favoris avant la première ouverture.
  async function chargerFavoris() {
    try { X.favoris = (await api("/api/modeles/favoris", {})).modeles; } catch { X.favoris = []; }
  }

  function dessiner() {
    const vue = $("#vue-modeles");
    const ancienne = vue.querySelector(".mo-recherche");
    const avaitFocus = ancienne && document.activeElement === ancienne;
    const recherche = el("input", { class: "mo-recherche", type: "search", placeholder: "Chercher dans les modèles…", value: X.recherche,
      oninput: e => { X.recherche = e.target.value; clearTimeout(minuterie); minuterie = setTimeout(recharger, 200); } });
    const categorie = el("select", { onchange: e => { X.categorie = e.target.value; recharger(); } },
      el("option", { value: "" }, "Toutes les catégories"),
      X.categories.map(c => { const o = el("option", { value: c }, brut(c)); o.selected = c === X.categorie; return o; }));
    const tris = [["favoris", "Favoris"], ["usage", "Plus utilisés"], ["titre", "A → Z"]];
    vue.replaceChildren(
      el("div", { class: "barre-vue" },
        el("h2", {}, icone("message-square-text"), t("Modèles de messages"), el("span", { class: "compte" }, String(X.total))),
        el("div", { class: "espace" }),
        el("button", { class: "icone-btn", title: "Importer des modèles (fichier JSON)", onclick: importer }, icone("upload")),
        el("button", { class: "icone-btn", title: "Exporter les modèles (fichier JSON)", onclick: exporter, disabled: X.total ? null : "" }, icone("download")),
        el("button", { class: "btn principal", onclick: () => editer(null) }, icone("plus"), t("Nouveau modèle"))),
      X.total ? el("div", { class: "mo-filtres" },
        el("div", { class: "champ-recherche" }, el("span", {}, icone("search")), recherche),
        X.categories.length ? categorie : null,
        el("div", { class: "espace" }),
        el("div", { class: "puces" }, tris.map(([v, lib]) =>
          el("button", { class: "puce " + (X.tri === v ? " actif" : ""), onclick: () => { X.tri = v; recharger(); } }, lib)))) : null,
      liste());
    if (avaitFocus) { recherche.focus(); recherche.setSelectionRange(recherche.value.length, recherche.value.length); }
  }

  function liste() {
    if (!X.total) {
      return el("div", { class: "vide mo-vide" }, icone("message-square-text"),
        el("p", {}, el("b", {}, "Aucun modèle pour l'instant.")),
        el("p", {}, "Créez le vôtre, ou remettez les exemples fournis."),
        el("div", { class: "mo-boutons" },
          el("button", { class: "btn", onclick: remettreExemples }, "Remettre les exemples"),
          el("button", { class: "btn principal", onclick: () => editer(null) }, icone("plus"), t("Nouveau modèle"))));
    }
    if (!X.modeles.length) return el("div", { class: "vide" }, icone("search"), "Aucun modèle ne correspond.");
    return el("div", { class: "lignes" }, X.modeles.map(ligne));
  }

  function ligne(m) {
    const stop = f => e => { e.stopPropagation(); f(); };
    const apercu = (m.objet ? m.objet + "  ·  " : "") + m.texte.replace(/\s+/g, " ").trim();
    return el("div", { class: "ligne cliquable", title: "Utiliser ce modèle", onclick: () => utiliser(m) },
      el("span", { class: "ligne-ic" }, icone(m.objet ? "mail" : "message-square-text")),
      el("div", { class: "ligne-corps sans-icone" },
        el("div", { class: "ligne-titre" }, el("span", {}, brut(m.titre)),
          m.categorie ? el("span", { class: "tag" }, brut(m.categorie)) : null,
          m.langue !== "fr" ? el("span", { class: "tag" }, m.langue === "en" ? "EN" : t("Autre")) : null),
        el("div", { class: "ligne-meta" }, brut(apercu.slice(0, 220)))),
      el("div", { class: "ligne-cote" },
        el("span", {}, usage(m.utilisations || 0)),
        m.favori ? el("span", { class: "mo-favori", title: "Favori" }, icone("star")) : null),
      el("div", { class: "ligne-actions" },
        el("button", { class: "icone-btn " + (m.favori ? " mo-actif" : ""), title: m.favori ? "Retirer des favoris" : "Ajouter aux favoris",
          onclick: stop(() => basculerFavori(m)) }, icone("star")),
        el("button", { class: "icone-btn", title: "Modifier", onclick: stop(() => editer(m)) }, icone("pencil")),
        el("button", { class: "icone-btn", title: "Dupliquer", onclick: stop(() => dupliquer(m)) }, icone("files")),
        el("button", { class: "icone-btn danger", title: "Supprimer", onclick: stop(() => supprimer(m)) }, icone("trash-2"))));
  }

  // ------------------------------------------------------------ actions
  async function basculerFavori(m) {
    try { await api("/api/modeles/favori", { id: m.id, favori: !m.favori }); recharger(); } catch (e) { erreur(e); }
  }
  async function dupliquer(m) {
    try { await api("/api/modeles/dupliquer", { id: m.id }); toast("Modèle dupliqué", "succes", 1600); recharger(); } catch (e) { erreur(e); }
  }
  async function supprimer(m) {
    if (!(await confirmer(icone("trash-2"), "Supprimer ce modèle ?", "Il disparaît définitivement.", "Supprimer"))) return;
    try { await api("/api/modeles/supprimer", { id: m.id }); toast("Modèle supprimé"); recharger(); } catch (e) { erreur(e); }
  }
  async function remettreExemples() {
    try {
      const { ajoutes } = await api("/api/modeles/exemples", {});
      toast(ajoutes ? t("{n} exemples ajoutés", { n: ajoutes }) : t("Les exemples sont déjà là"), "succes");
      recharger();
    } catch (e) { erreur(e); }
  }

  async function exporter() {
    try {
      const donnees = await api("/api/modeles/exporter", {});
      const lien = el("a", { href: URL.createObjectURL(new Blob([JSON.stringify(donnees, null, 2)], { type: "application/json" })),
        download: `modeles-messages-${new Date().toISOString().slice(0, 10)}.json` });
      document.body.append(lien); lien.click(); lien.remove();
      setTimeout(() => URL.revokeObjectURL(lien.href), 5000);
      toast("Modèles exportés", "succes", 1800);
    } catch (e) { erreur(e); }
  }
  function importer() {
    const champ = el("input", { type: "file", accept: ".json,application/json", style: "display:none" });
    champ.addEventListener("change", async () => {
      const fichier = champ.files[0];
      champ.remove();
      if (!fichier) return;
      let contenu;
      try { contenu = JSON.parse(await fichier.text()); } catch { toast("Fichier illisible : ce n'est pas du JSON.", "erreur", 5000); return; }
      try {
        const r = await api("/api/modeles/importer", { contenu });
        const details = [r.doublons ? t("{n} déjà présents, ignorés", { n: r.doublons }) : "",
          r.invalides ? t("{n} invalides, ignorés", { n: r.invalides }) : ""].filter(Boolean).join(" · ");
        toast((r.ajoutes ? t("{n} modèles importés", { n: r.ajoutes }) : t("Aucun nouveau modèle dans ce fichier"))
          + (details ? "( " + details + ")" : ""), r.ajoutes ? "succes" : "", 4500);
        recharger();
      } catch (e) { erreur(e); }
    });
    document.body.append(champ);
    champ.click();
  }

  // ------------------------------------------------------------ éditeur
  function editer(m) {
    const b = m ? { ...m } : { titre: "", categorie: X.categorie || "", objet: "", texte: "", langue: "fr", favori: false };
    const titre = el("input", { value: b.titre, placeholder: "ex. Relance de paiement", maxlength: 120 });
    const categorie = el("input", { value: b.categorie, placeholder: "ex. Relances", maxlength: 40, list: "mo-categories" });
    const langue = el("select", {}, [["fr", "Français"], ["en", "Anglais"], ["autre", "Autre"]].map(([v, lib]) => {
      const o = el("option", { value: v }, lib); o.selected = v === b.langue; return o;
    }));
    const objet = el("input", { value: b.objet, placeholder: "ex. Facture {numero_facture}", maxlength: 250 });
    const texte = el("textarea", { value: b.texte, rows: 11 });
    const favori = el("input", { type: "checkbox" });
    favori.checked = !!b.favori;
    const detectees = el("div", { class: "mo-detectees" });
    let dernierChamp = texte;
    objet.addEventListener("focus", () => (dernierChamp = objet));
    texte.addEventListener("focus", () => (dernierChamp = texte));
    const majDetectees = () => {
      const vars = variablesDe(objet.value, texte.value);
      detectees.replaceChildren(el("span", {}, "Variables détectées :"),
        ...(vars.length ? vars.map(v => el("span", { class: "tag sans-icone" }, brut("{ " + v.nom + "}")))
          : [el("span", { style: "color:var(--gris)" }, "Aucune variable pour l'instant.")]));
    };
    objet.addEventListener("input", majDetectees);
    texte.addEventListener("input", majDetectees);
    majDetectees();
    const inserer = nom => {
      const champ = dernierChamp, debut = champ.selectionStart ?? champ.value.length;
      champ.setRangeText("{ " + nom + "}", debut, champ.selectionEnd ?? debut, "end");
      champ.focus(); majDetectees();
    };
    const libre = el("button", { class: "btn petit discret", type: "button", title: "Nom de la variable (lettres, chiffres, _ ou -)", onclick: () => {
      const champ = el("input", { placeholder: "ex. numero_facture", style: "width:100%" });
      const valider = () => {
        const nom = champ.value.trim().replace(/[{}\s]+/g, "_");
        if (!/^[\p{L}_][\p{L}\p{N}_-]{0,39}$/u.test(nom)) { champ.focus(); return; }
        ligneInserer.replaceChildren(...boutonsInserer());
        inserer(nom);
      };
      champ.addEventListener("keydown", e => { if (e.key === "Enter") { e.preventDefault(); valider(); } if (e.key === "Escape") { e.stopPropagation(); ligneInserer.replaceChildren(...boutonsInserer()); } });
      ligneInserer.replaceChildren(el("span", {}, "Variable libre :"), el("span", { style: "flex:1" }, champ),
        el("button", { class: "btn petit", type: "button", onclick: valider }, "Insérer"));
      setTimeout(() => champ.focus(), 20);
    } }, icone("plus"), t("Variable libre"));
    const boutonsInserer = () => [el("span", {}, "Insérer :"),
      STANDARD.map(v => el("button", { class: "btn petit mo-var", type: "button", title: LIBELLES[v], onclick: () => inserer(v) }, brut("{ " + v + "}"))), libre];
    const ligneInserer = el("div", { class: "mo-inserer" }, boutonsInserer());

    const valider = async () => {
      const modele = { ...b, titre: titre.value, categorie: categorie.value, langue: langue.value, objet: objet.value,
        texte: texte.value, favori: favori.checked };
      try {
        await api("/api/modeles/enregistrer", { modele });
        fermer(); toast("Modèle enregistré", "succes", 1600); recharger();
      } catch (e) { erreur(e); }
    };
    const categories = [...new Set([...X.categories, ...CATEGORIES_PROPOSEES])];
    fenetre([el("div", { class: "mo-editeur" },
      el("h3", {}, m ? "Modifier le modèle" : "Nouveau modèle"),
      el("div", { class: "mo-grille" },
        el("label", { class: "champ large" }, "Titre", titre),
        el("label", { class: "champ" }, "Catégorie", categorie,
          el("datalist", { id: "mo-categories" }, categories.map(c => el("option", { value: c })))),
        el("label", { class: "champ" }, "Langue", langue),
        el("label", { class: "champ large" }, el("span", {}, t("Objet") + " ", el("small", {}, "( " + t("facultatif, pour un mail") + ")")), objet),
        el("label", { class: "champ large" }, "Texte", texte)),
      ligneInserer,
      detectees,
      el("label", { class: "mo-case" }, favori, "Favori (aussi dans Ctrl + K)"),
      el("div", { class: "actions" },
        el("button", { class: "btn", onclick: fermer }, "Annuler"),
        el("button", { class: "btn principal", onclick: valider }, m ? "Enregistrer" : "Ajouter")))]);
    $("#fenetre").style.width = "min(720px, 94vw)";
    setTimeout(() => (m ? texte : titre).focus(), 60);
  }

  // ------------------------------------------------------------ utilisation
  /** Les contacts de l'application Contacts, ou [] si elle est absente. */
  async function contacts() {
    try { return (await api("/api/contacts/liste", {})).contacts || []; } catch { return []; }
  }
  /** Prénom, nom… d'un contact (format public : « nom » = « Prénom Nom »).
      Si Contacts donne aussi prenom ou type, on s'en sert. */
  function valeursContact(c) {
    const commun = { email: c.email || "", telephone: c.telephone || "", phone: c.telephone || "" };
    if (c.type === "entreprise") return { ...commun, entreprise: c.nom || "", company: c.nom || "" };
    const mots = String(c.nom || "").trim().split(/\s+/).filter(Boolean);
    const prenom = c.prenom || mots[0] || "";
    const nom = c.prenom ? mots.slice(String(c.prenom).split(/\s+/).length).join(" ") : mots.slice(1).join(" ");
    // Mêmes valeurs sous les noms anglais (modèles fournis en anglais).
    return { ...commun, prenom, nom, entreprise: c.entreprise || "",
             first_name: prenom, last_name: nom, name: String(c.nom || "").trim(), company: c.entreprise || "" };
  }
  function aujourdhui(langue) {
    const locale = langue === "en" ? "en-GB" : langue === "fr" ? "fr-FR" : I18N.locale();
    return new Date().toLocaleDateString(locale, { day: "numeric", month: "long", year: "numeric" });
  }

  /** La fenêtre « Utiliser ce modèle ». rappel : voir Modeles.choisir. */
  async function utiliser(m, rappel = null) {
    const vars = variablesDe(m.objet, m.texte);
    const valeurs = {};
    if (vars.some(v => v.cle === "date")) valeurs.date = aujourdhui(m.langue);
    const liste = await contacts();
    const entrees = {};
    const destinataire = el("input", { type: "email", placeholder: "adresse@exemple.com" });
    const apercuObjet = el("span", { class: "val" });
    const apercuCorps = el("div", { class: "mo-corps" });
    const peindre = (cible, texte) => cible.replaceChildren(...morceaux(texte, valeurs).map(x =>
      typeof x === "string" ? brut(x) : el("span", { class: "mo-manque" }, brut(x.manque))));
    const majApercu = () => { peindre(apercuObjet, m.objet); peindre(apercuCorps, m.texte); };
    const champs = vars.map(v => {
      const entree = el("input", { value: valeurs[v.cle] || "", oninput: e => { valeurs[v.cle] = e.target.value; majApercu(); } });
      entrees[v.cle] = entree;
      return el("label", { class: "champ" }, el("span", { class: "sans-icone" }, brut(libelle(v))), entree);
    });
    const choixContact = liste.length ? el("select", { onchange: e => {
      const c = liste.find(x => String(x.id) === e.target.value);
      if (!c) return;
      const v = valeursContact(c);
      for (const [cle, val] of Object.entries(v)) if (entrees[cle] && val) { entrees[cle].value = val; valeurs[cle] = val; }
      if (c.email) destinataire.value = c.email;
      majApercu();
    } }, el("option", { value: "" }, "Aucun contact"),
      liste.map(c => el("option", { value: String(c.id) }, brut(c.nom + (c.entreprise ? "· " + c.entreprise : ""))))) : null;
    majApercu();

    const final = () => ({ a: destinataire.value.trim(), objet: remplir(m.objet, valeurs), texte: remplir(m.texte, valeurs) });
    const compter = () => api("/api/modeles/utiliser", { id: m.id }).then(() => { if (S.vue === "modeles") recharger(); }).catch(() => {});
    const copierTexte = async () => { await copier(final().texte, "Texte copié"); compter(); fermer(); };
    const ecrireMail = async () => {
      const f = final();
      try {
        const r = await api("/api/modeles/mail", f);
        if (r.texte_retire) { await copier(f.texte, "Texte copié"); toast("Texte trop long pour le lien : il est copié, collez-le dans le mail.", "", 7000); }
        else toast("Mail ouvert dans votre messagerie", "succes", 2200);
        compter(); fermer();
      } catch (e) { erreur(e); }
    };
    const insererMail = () => { compter(); fermer(); rappel(final()); };

    fenetre([el("div", { class: "mo-utiliser" },
      el("h3", {}, icone(m.objet ? "mail" : "message-square-text"), el("span", { class: "sans-icone" }, brut(m.titre))),
      el("div", { class: "mo-sous-titre sans-icone" }, m.categorie ? el("span", { class: "tag" }, brut(m.categorie)) : null, usage(m.utilisations || 0)),
      choixContact || !rappel ? el("div", { class: "mo-grille" },
        choixContact ? el("label", { class: "champ" }, "Contact", choixContact) : null,
        !rappel ? el("label", { class: "champ " + (choixContact ? "" : " large") },
          el("span", {}, t("Destinataire") + " ", el("small", {}, "( " + t("pour « Écrire le mail »") + ")")), destinataire) : null) : null,
      vars.length ? el("div", { class: "mo-grille" }, champs) : el("p", { class: "mo-note" }, "Ce modèle n'a pas de variable."),
      el("div", { class: "mo-section" }, "Aperçu"),
      el("div", { class: "mo-apercu sans-icone" },
        m.objet ? el("div", { class: "mo-objet" }, el("span", { class: "lib" }, "Objet :"), apercuObjet,
          el("button", { class: "icone-btn", title: "Copier l'objet", onclick: () => copier(final().objet, "Objet copié") }, icone("copy"))) : null,
        apercuCorps),
      vars.length ? el("div", { class: "mo-note" }, "Les variables laissées vides restent entre accolades.") : null,
      el("div", { class: "actions" },
        el("button", { class: "btn", onclick: fermer }, "Annuler"),
        rappel ? el("button", { class: "btn principal", onclick: insererMail }, icone("corner-down-right"), t("Insérer dans le mail"))
          : [el("button", { class: m.objet ? "btn" : "btn principal", onclick: copierTexte }, icone("copy"), t("Copier")),
            el("button", { class: m.objet ? "btn principal" : "btn", onclick: ecrireMail }, icone("send"), t("Écrire le mail"))]))]);
    $("#fenetre").style.width = "min(680px, 94vw)";
    setTimeout(() => (choixContact || Object.values(entrees).find(e => !e.value) || $("#fenetre .actions .btn.principal"))?.focus(), 60);
  }

  /** Pour les autres applications : choisir un modèle, le remplir, puis
      rappel({ a, objet, texte }). */
  async function choisir(rappel) {
    let tous = [];
    try { tous = (await api("/api/modeles/liste", { tri: "favoris" })).modeles; } catch (e) { erreur(e); return; }
    fenetre([el("h3", {}, "Choisir un modèle"),
      tous.length ? el("div", { class: "lignes mo-choix" }, tous.map(m =>
        el("div", { class: "ligne cliquable", onclick: () => utiliser(m, rappel) },
          el("span", { class: "ligne-ic" }, icone(m.favori ? "star" : m.objet ? "mail" : "message-square-text")),
          el("div", { class: "ligne-corps sans-icone" }, el("div", { class: "ligne-titre" }, el("span", {}, brut(m.titre)),
            m.categorie ? el("span", { class: "tag" }, brut(m.categorie)) : null)))))
        : el("div", { class: "vide" }, "Aucun modèle pour l'instant."),
      el("div", { class: "actions" }, el("button", { class: "btn", onclick: fermer }, "Annuler"))]);
  }
  window.Modeles = { choisir, utiliser: id => { const m = X.favoris.find(x => x.id === id) || X.modeles.find(x => x.id === id); if (m) utiliser(m); } };

  chargerFavoris();

  VUES.modeles = {
    afficher: recharger,
    titre: "Modèles de messages",
    icone: icone("message-square-text"),
    groupe: "organisation",
    ordre: 40,
    description: "Réponses types, relances, confirmations de rendez-vous : des textes prêts à l'emploi, avec variables.",
    profils: ["assistant_virtuel", "assistant_direction", "freelance"],
    carteAccueil: null,
    commandes: () => X.favoris.map(m => ({
      icone: icone("message-square-text"),
      titre: t("Utiliser le modèle : {titre}", { titre: m.titre }),
      detail: m.categorie || "",
      action: () => utiliser(m),
    })),
  };
})();
