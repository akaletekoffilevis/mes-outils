"use strict";
/* Application « Documents » : un classeur des documents importants (contrats,
   devis signés, attestations…), rangés par client ou projet, sans déplacer
   les fichiers de la personne (voir documents.py). Retirer une fiche ne
   supprime jamais le fichier. */
(() => {
  I18N.ajouter({
    "Documents": "Documents",
    "Un classeur des documents importants (contrats, devis signés, attestations…), rangés par client ou projet, avec un rappel avant expiration.":
      "A binder for important documents (contracts, signed quotes, certificates…), filed by client or project, with a reminder before they expire.",
    "Ajouter un fichier": "Add a file",
    "Ajouter un dossier": "Add a folder",
    "Ajouter des fichiers au classeur": "Add files to the binder",
    "Ajouter un dossier au classeur": "Add a folder to the binder",
    "Choisir des documents": "Choose documents",
    "Choisir le dossier à ajouter": "Choose the folder to add",
    "Titre, fichier, étiquette…": "Title, file, tag…",
    "Par client": "By client", "Par type": "By type",
    "Tous": "All", "Expirent bientôt": "Expiring soon", "Introuvables": "Missing",
    "Tous les types": "All types",
    "Contrat": "Contract", "Devis signé": "Signed quote", "Facture fournisseur": "Supplier invoice",
    "Attestation": "Certificate", "Pièce d'identité": "ID document", "Assurance": "Insurance", "Autre": "Other",
    "Non classé": "Unfiled",
    "Dossier": "Folder",
    "Aucun document pour l'instant.": "No documents yet.",
    "Ajoutez un contrat, un devis signé, une attestation… Le fichier reste où il est : le classeur garde seulement son adresse.":
      "Add a contract, a signed quote, a certificate… The file stays where it is: the binder only keeps its location.",
    "Aucun document ne correspond.": "No matching document.",
    "Introuvable": "Missing",
    "Retrouver…": "Locate…",
    "Le fichier a été déplacé ou supprimé. Choisissez son nouvel emplacement.": "The file was moved or deleted. Choose its new location.",
    "Expiré": "Expired",
    "Expire aujourd'hui": "Expires today",
    "Expire demain": "Expires tomorrow",
    "Aujourd'hui": "Today",
    "{n} j": "{n} d",
    "Expire dans {n} j": "Expires in {n} d",
    "Expire le {date}": "Expires on {date}",
    "Expiré le {date}": "Expired on {date}",
    "Ouvrir": "Open",
    "Ouvrir le dossier": "Open folder",
    "Copier le chemin": "Copy path",
    "Modifier": "Edit",
    "Retirer de la liste": "Remove from list",
    "Chemin copié": "Path copied",
    "Emplacement": "Location",
    "Ajouté le {date}": "Added on {date}",
    "Copié dans le classeur": "Copied to the binder",
    "Daté du {date}": "Dated {date}",
    "Titre": "Title",
    "Type": "Type",
    "Client": "Client",
    "Projet": "Project",
    "Étiquettes": "Tags",
    "séparées par des virgules": "comma-separated",
    "Date du document": "Document date",
    "vide : date du fichier": "empty: file date",
    "Expiration": "Expiry",
    "facultatif": "optional",
    "Rappel": "Reminder",
    "Aucun rappel": "No reminder",
    "{n} jours avant": "{n} days before",
    "Note": "Note",
    "Note (facultatif)": "Note (optional)",
    "Copier dans le classeur": "Copy to the binder",
    "Une copie va dans {dossier}. L'original ne bouge pas.": "A copy goes to {dossier}. The original stays where it is.",
    "ex. Contrat de prestation 2026": "e.g. Service agreement 2026",
    "ex. Site vitrine": "e.g. Company website",
    "ex. signé, original papier": "e.g. signed, paper original",
    "Nom du client": "Client name",
    "Annuler": "Cancel", "Enregistrer": "Save", "Ajouter": "Add",
    "Modifier le document": "Edit document",
    "Ajouter un document": "Add a document",
    "Ajouter {n} documents": "Add {n} documents",
    "et {n} autres": "and {n} more",
    "Retirer ce document de la liste ?": "Remove this document from the list?",
    "Le fichier n'est pas supprimé : il reste à sa place sur le PC.": "The file is not deleted: it stays where it is on the PC.",
    "Retirer": "Remove",
    "Rechercher un document": "Search a document",
    "Document retiré de la liste": "Document removed from the list",
    "Document ajouté": "Document added",
    "{n} documents ajoutés": "{n} documents added",
    "Déjà dans le classeur": "Already in the binder",
    "{n} déjà dans le classeur": "{n} already in the binder",
    "Enregistré": "Saved",
    "Emplacement mis à jour": "Location updated",
    "Documents à renouveler": "Documents to renew",
    "Ouvrir : {titre}": "Open: {titre}",
    "{n} documents": "{n} documents",
    "1 document": "1 document",
    "Aucun fichier choisi.": "No file chosen.",
    "Choisissez un dossier.": "Choose a folder.",
    "Choisissez un fichier.": "Choose a file.",
    "Document introuvable dans la liste.": "Document not found in the list.",
    "Type de document inconnu.": "Unknown document type.",
    "Indiquez un titre.": "Enter a title.",
    "Date du document invalide.": "Invalid document date.",
    "Date d'expiration invalide.": "Invalid expiry date.",
    "L'expiration doit être après la date du document.": "The expiry must be after the document date.",
    "Seuls les fichiers peuvent être copiés dans le classeur.": "Only files can be copied to the binder.",
    "Nom de client invalide pour le classeur.": "Invalid client name for the binder.",
    "Introuvable : le fichier a été déplacé ou supprimé. Utilisez « Retrouver… ».": "Missing: the file was moved or deleted. Use “Locate…”.",
    "Introuvable : le dossier du document n'existe plus.": "Missing: the document's folder no longer exists.",
  });
  I18N.motifs([
    [/^Fichier introuvable : (.*)$/, "File not found: $1"],
    [/^Chemin invalide : (.*)$/, "Invalid path: $1"],
    [/^Ce fichier est déjà dans la liste : (.*)$/, "This file is already in the list: $1"],
    [/^Trop de fichiers d'un coup \(maximum (\d+)\)\.$/, "Too many files at once (maximum $1)."],
  ]);

  // Icône de chaque type (web/icones.js).
  const ICONES_TYPES = {
    contrat: "handshake", devis_signe: "file-check", facture_fournisseur: "receipt", attestation: "file-text",
    piece_identite: "id-card", assurance: "shield", autre: "file",
  };
  const RAPPELS = [0, 7, 15, 30, 60, 90];
  const SEUIL_ACCUEIL = 30;
  const D = { r: null, recherche: "", groupe: "client", etat: "tous", type: "", ouverts: new Set(), contacts: [] };

  const style = document.createElement("style");
  style.textContent = `
    .dc-filtres { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin: -6px 0 16px; }
    .dc-filtres select { height: 34px; padding: 0 10px; }
    .dc-filtres .puce .n { color: var(--gris); font-weight: 500; font-variant-numeric: tabular-nums; }
    .dc-titre-groupe { display: flex; align-items: center; gap: 8px; }
    .dc-titre-groupe .n { color: var(--gris); font-weight: 500; text-transform: none; letter-spacing: 0; }
    .dc-ligne.perdu .ligne-titre > span:first-child { color: var(--doux); }
    .dc-ligne .tag { max-width: 140px; overflow: hidden; text-overflow: ellipsis; }
    .dc-ligne .ligne-cote .btn { height: 26px; }
    .dc-detail { display: grid; grid-template-columns: 110px minmax(0, 1fr); gap: 4px 14px; font-size: 13px; }
    .dc-detail dt { color: var(--gris); }
    .dc-detail dd { margin: 0; min-width: 0; overflow-wrap: anywhere; }
    .dc-detail .mono { font-size: 12px; color: var(--doux); }
    .dc-detail .note { white-space: pre-wrap; }
    .dc-detail .dc-ajoute { color: var(--gris); font-size: 12px; margin-top: 4px; }
    .dc-grille { display: grid; grid-template-columns: 1fr 1fr; gap: 0 12px; }
    .dc-fichiers { background: var(--surface); border: 1px solid var(--ligne); border-radius: 8px; padding: 8px 10px; margin: 0 0 14px; font-size: 13px; color: var(--doux); }
    .dc-fichiers div { display: flex; align-items: center; gap: 7px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .dc-fichiers svg.ico { margin: 0; color: var(--gris); }
    .dc-case { display: flex; align-items: flex-start; gap: 9px; font-size: 13.5px; cursor: pointer; margin: 2px 0 4px; }
    .dc-case input { margin-top: 3px; }
    .dc-case small { display: block; color: var(--gris); font-size: 12px; overflow-wrap: anywhere; }
    .dc-vide .btn { margin: 14px 4px 0; }
    .dc-vide .btn svg.ico { width: 1.1em; height: 1.1em; display: inline-block; margin: 0; color: inherit; }
    .carte-jour .dc-jours { min-width: 52px; white-space: nowrap; }
  `;
  document.head.append(style);

  // --------------------------------------------------------------- outils
  const typeLib = cle => (D.r?.types || {})[cle] || "Autre";
  const iconeFiche = f => icone(f.genre === "dossier" ? "folder" : ICONES_TYPES[f.type] || "file");
  function dateCourte(iso) {
    if (!iso) return "";
    return new Date(iso + "T00:00").toLocaleDateString(I18N.locale(), { day: "numeric", month: "short", year: "numeric" });
  }
  /** Rubrique de classement : le client, sinon le projet, sinon « Non classé ». */
  const rubrique = f => f.client || f.projet || t("Non classé");
  const bientot = f => f.jours !== null && f.jours !== undefined && f.jours <= Math.max(f.rappel_jours ?? 30, 0) && f.jours >= -30;
  function normaliser(s) { return String(s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); }

  /** L'état d'expiration en texte coloré (ou null). */
  function etatExpiration(f) {
    if (f.jours === null || f.jours === undefined) return null;
    const date = dateCourte(f.expiration);
    if (f.jours < 0) return el("span", { class: "etat-txt rouge", title: t("Expiré le {date}", { date }) }, icone("triangle-alert"), "Expiré");
    if (bientot(f)) {
      const texte = f.jours === 0 ? t("Expire aujourd'hui") : f.jours === 1 ? t("Expire demain") : t("Expire dans {n} j", { n: f.jours });
      return el("span", { class: "etat-txt ambre", title: t("Expire le {date}", { date }) }, icone("calendar-clock"), texte);
    }
    return el("span", { class: "etat-txt gris" }, t("Expire le {date}", { date }));
  }

  async function action(chemin, donnees, message) {
    try {
      const r = await api(chemin, donnees);
      if (message) toast(message, "succes", 1600);
      return r;
    } catch (e) { toast(e.message, "erreur", 5000); return null; }
  }

  async function charger() {
    D.r = await api("/api/documents/liste", {});
    return D.r;
  }

  async function chargerContacts() {
    // Application Contacts : facultative (absente ou désactivée → liste vide).
    try { D.contacts = (await api("/api/contacts/liste", {})).contacts || []; } catch { D.contacts = []; }
  }

  // ------------------------------------------------------------ affichage
  async function afficher() {
    const vue = $("#vue-documents");
    if (!vue.querySelector(".barre-vue")) construire(vue);
    try { await Promise.all([charger(), chargerContacts()]); }
    catch (e) { toast(e.message, "erreur", 5000); return; }
    dessiner();
  }

  function construire(vue) {
    const recherche = el("input", { type: "search", placeholder: "Titre, fichier, étiquette…", title: "Rechercher un document", value: D.recherche,
      oninput: e => { D.recherche = e.target.value; dessiner(); } });
    vue.replaceChildren(
      el("div", { class: "barre-vue" },
        el("h2", {}, icone("folders", "av"), "Documents", el("span", { class: "compte", id: "dc-compte" }, "0")),
        el("span", { class: "espace" }),
        el("label", { class: "champ-recherche" }, el("span", {}, icone("search")), recherche),
        el("button", { class: "btn", onclick: ajouterDossier }, icone("folder-open", "av"), "Ajouter un dossier"),
        el("button", { class: "btn principal", onclick: ajouterFichiers }, icone("file-plus", "av"), "Ajouter un fichier")),
      el("div", { class: "dc-filtres", id: "dc-filtres" }),
      el("div", { id: "dc-liste" }));
  }

  function puces(options, valeur, choisir) {
    return el("div", { class: "puces" }, options.map(([cle, lib, n]) =>
      el("button", { class: "puce" + (cle === valeur ? " actif" : ""), onclick: () => { choisir(cle); dessiner(); } },
        lib, n ? el("span", { class: "n" }, String(n)) : null)));
  }

  function filtrees() {
    const q = normaliser(D.recherche.trim());
    return D.r.fiches.filter(f => {
      if (D.type && (f.genre === "dossier" ? "dossier" : f.type) !== D.type) return false;
      if (D.etat === "bientot" && !bientot(f)) return false;
      if (D.etat === "perdus" && f.existe) return false;
      if (!q) return true;
      return normaliser([f.titre, f.nom, f.client, f.projet, f.note, ...(f.etiquettes || [])].join(" ")).includes(q);
    });
  }

  function dessiner() {
    if (!D.r) return;
    const toutes = D.r.fiches;
    $("#dc-compte").textContent = String(toutes.length);
    const nBientot = toutes.filter(bientot).length, nPerdus = toutes.filter(f => !f.existe).length;
    if (D.etat === "bientot" && !nBientot) D.etat = "tous";
    if (D.etat === "perdus" && !nPerdus) D.etat = "tous";
    const typesPresents = new Set(toutes.map(f => (f.genre === "dossier" ? "dossier" : f.type)));
    const selectType = el("select", { title: "Type", onchange: e => { D.type = e.target.value; dessiner(); } },
      el("option", { value: "" }, "Tous les types"),
      Object.entries(D.r.types).filter(([k]) => typesPresents.has(k)).map(([k, lib]) => el("option", { value: k }, lib)),
      typesPresents.has("dossier") ? el("option", { value: "dossier" }, "Dossier") : null);
    selectType.value = typesPresents.has(D.type) ? D.type : (D.type = "");
    $("#dc-filtres").replaceChildren(...(toutes.length ? [
      puces([["client", "Par client"], ["type", "Par type"]], D.groupe, v => (D.groupe = v)),
      puces([["tous", "Tous"], nBientot ? ["bientot", "Expirent bientôt", nBientot] : null,
        nPerdus ? ["perdus", "Introuvables", nPerdus] : null].filter(Boolean), D.etat, v => (D.etat = v)),
      typesPresents.size > 1 ? selectType : null] : []));

    const liste = $("#dc-liste");
    if (!toutes.length) {
      liste.replaceChildren(el("div", { class: "vide dc-vide" }, icone("folders"),
        el("div", {}, el("b", {}, "Aucun document pour l'instant.")),
        el("div", {}, "Ajoutez un contrat, un devis signé, une attestation… Le fichier reste où il est : le classeur garde seulement son adresse."),
        el("button", { class: "btn principal", onclick: ajouterFichiers }, icone("file-plus", "av"), "Ajouter un fichier"),
        el("button", { class: "btn", onclick: ajouterDossier }, icone("folder-open", "av"), "Ajouter un dossier")));
      return;
    }
    const fiches = filtrees();
    if (!fiches.length) { liste.replaceChildren(el("div", { class: "vide" }, icone("search"), "Aucun document ne correspond.")); return; }

    // Groupes : par client / projet, ou par type (ordre du catalogue des types).
    const groupes = new Map();
    const cleGroupe = f => (D.groupe === "type" ? (f.genre === "dossier" ? "dossier" : f.type || "autre") : rubrique(f));
    for (const f of fiches) {
      const k = cleGroupe(f);
      if (!groupes.has(k)) groupes.set(k, []);
      groupes.get(k).push(f);
    }
    const ordreTypes = [...Object.keys(D.r.types), "dossier"];
    const nonClasse = t("Non classé");
    const cles = [...groupes.keys()].sort((a, b) => D.groupe === "type" ? ordreTypes.indexOf(a) - ordreTypes.indexOf(b)
      : (a === nonClasse) - (b === nonClasse) || a.localeCompare(b, I18N.locale(), { sensitivity: "base" }));
    const titreGroupe = k => (D.groupe === "type" ? (k === "dossier" ? "Dossier" : typeLib(k)) : k);
    liste.replaceChildren(...cles.map(k => {
      const lignes = groupes.get(k).sort((a, b) =>
        (a.existe - b.existe) || ((bientot(b) - bientot(a))) || a.titre.localeCompare(b.titre, I18N.locale(), { sensitivity: "base" }));
      return el("div", { class: "lignes" },
        el("div", { class: "titre-lignes dc-titre-groupe" }, titreGroupe(k), el("span", { class: "n" }, String(lignes.length))),
        lignes.map(ligne));
    }));
  }

  function ligne(f) {
    const ouverte = D.ouverts.has(f.id);
    const meta = [f.nom !== f.titre ? f.nom : null];
    if (D.groupe === "type") { if (f.client || f.projet) meta.push(rubrique(f)); }
    else { meta.push(f.genre === "dossier" ? t("Dossier") : t(typeLib(f.type))); if (f.client && f.projet) meta.push(f.projet); }
    if (f.date_document) meta.push(dateCourte(f.date_document));
    const bouton = (nom, titre, fn, classe = "") => el("button", { class: "icone-btn " + classe, title: titre,
      onclick: e => { e.stopPropagation(); fn(); } }, icone(nom));
    const cote = f.existe ? etatExpiration(f) : [
      el("span", { class: "etat-txt rouge", title: "Le fichier a été déplacé ou supprimé. Choisissez son nouvel emplacement." },
        icone("circle-alert"), "Introuvable"),
      el("button", { class: "btn petit", onclick: e => { e.stopPropagation(); retrouver(f); } }, "Retrouver…")];
    const bloc = el("div", { class: "ligne cliquable dc-ligne" + (ouverte ? " ouverte" : "") + (f.existe ? "" : " perdu"),
      ondblclick: () => f.existe && ouvrir(f),
      onclick: () => { ouverte ? D.ouverts.delete(f.id) : D.ouverts.add(f.id); dessiner(); } },
      el("span", { class: "ligne-ic" }, iconeFiche(f)),
      el("div", { class: "ligne-corps" },
        el("div", { class: "ligne-titre" }, el("span", {}, f.titre), (f.etiquettes || []).slice(0, 3).map(e => el("span", { class: "tag" }, e))),
        el("div", { class: "ligne-meta" }, meta.filter(Boolean).join(" · "))),
      el("div", { class: "ligne-cote" }, cote),
      el("div", { class: "ligne-actions" },
        f.existe ? bouton("external-link", "Ouvrir", () => ouvrir(f)) : null,
        bouton("folder-open", "Ouvrir le dossier", () => action("/api/documents/ouvrir_dossier", { id: f.id })),
        bouton("copy", "Copier le chemin", () => copier(f.chemin, t("Chemin copié"))),
        bouton("pencil", "Modifier", () => formulaire({ fiche: f })),
        bouton("x", "Retirer de la liste", () => retirer(f), "danger")));
    if (!ouverte) return bloc;
    return [bloc, el("div", { class: "ligne-detail" }, el("dl", { class: "dc-detail" },
      el("dt", {}, "Emplacement"), el("dd", { class: "mono sans-icone" }, f.chemin),
      f.client && f.projet ? [el("dt", {}, "Projet"), el("dd", {}, f.projet)] : null,
      (f.etiquettes || []).length ? [el("dt", {}, "Étiquettes"), el("dd", {}, f.etiquettes.join(", "))] : null,
      f.date_document ? [el("dt", {}, "Date du document"), el("dd", {}, dateCourte(f.date_document))] : null,
      f.expiration ? [el("dt", {}, "Expiration"), el("dd", {}, dateCourte(f.expiration))] : null,
      f.note ? [el("dt", {}, "Note"), el("dd", { class: "note" }, f.note)] : null,
      el("dt", {}, ""), el("dd", { class: "dc-ajoute" }, t("Ajouté le {date}", { date: dateCourte(f.ajoute) }) + (f.copie ? " · " + t("Copié dans le classeur") : ""))))];
  }

  // -------------------------------------------------------------- actions
  async function ouvrir(f) { await action("/api/documents/ouvrir", { id: f.id }); }

  async function retirer(f) {
    if (!(await confirmer(icone("x"), "Retirer ce document de la liste ?", "Le fichier n'est pas supprimé : il reste à sa place sur le PC.", "Retirer"))) return;
    if (await action("/api/documents/retirer", { id: f.id }, "Document retiré de la liste")) { D.ouverts.delete(f.id); await afficher(); }
  }

  async function retrouver(f) {
    let chemin = null;
    const depart = f.dossier_parent || D.r?.dernier_dossier || "";
    if (f.genre === "dossier") chemin = await choisirDossier("Retrouver…", depart);
    else {
      const r = await action("/api/documents/choisir_fichiers", { titre: I18N.traduire("Retrouver…") + " " + f.nom, depart, multi: false });
      chemin = r?.chemins?.[0] || null;
    }
    if (!chemin) return;
    if (await action("/api/documents/retrouver", { id: f.id, chemin }, "Emplacement mis à jour")) await afficher();
  }

  async function ajouterFichiers() {
    const r = await action("/api/documents/choisir_fichiers", { titre: I18N.traduire("Choisir des documents") });
    if (r?.chemins?.length) formulaire({ chemins: r.chemins, genre: "fichier" });
  }

  async function ajouterDossier() {
    const chemin = await choisirDossier("Choisir le dossier à ajouter", D.r?.dernier_dossier || "");
    if (chemin) formulaire({ chemins: [chemin], genre: "dossier" });
  }

  /** Libellé d'un contact pour le champ Client : son entreprise, sinon son nom. */
  const libelleContact = c => c.entreprise || c.nom || "";

  /** Fenêtre d'ajout (chemins choisis) ou de modification (fiche). */
  function formulaire({ chemins = null, genre = "fichier", fiche = null }) {
    if (!D.r) return;
    const f = fiche || {};
    const plusieurs = chemins && chemins.length > 1;
    const nomDe = c => c.split(/[\\/]/).filter(Boolean).pop() || c;
    const sansExt = n => (genre === "dossier" ? n : n.replace(/\.[^.]+$/, ""));
    const titre = el("input", { value: f.titre ?? (chemins && !plusieurs ? sansExt(nomDe(chemins[0])) : ""), placeholder: "ex. Contrat de prestation 2026", maxlength: 120 });
    const type = el("select", {}, Object.entries(D.r.types).map(([k, lib]) => el("option", { value: k }, lib)));
    type.value = f.type || "autre";
    const listeClients = [...new Set([...D.contacts.map(libelleContact), ...D.r.clients].filter(Boolean))]
      .sort((a, b) => a.localeCompare(b, I18N.locale(), { sensitivity: "base" }));
    const client = el("input", { value: f.client || "", list: "dc-clients", placeholder: "Nom du client", maxlength: 80 });
    const projet = el("input", { value: f.projet || "", list: "dc-projets", placeholder: "ex. Site vitrine", maxlength: 80 });
    const etiquettes = el("input", { value: (f.etiquettes || []).join(", "), list: "dc-etiquettes", placeholder: "ex. signé, original papier" });
    const dateDoc = el("input", { type: "date", value: f.date_document || "" });
    const expiration = el("input", { type: "date", value: f.expiration || "" });
    const rappel = el("select", {}, RAPPELS.map(n => el("option", { value: n }, n ? t("{n} jours avant", { n }) : t("Aucun rappel"))));
    rappel.value = String(f.rappel_jours ?? D.r.rappel_defaut ?? 30);
    const majRappel = () => { rappel.disabled = !expiration.value; };
    expiration.addEventListener("input", majRappel); majRappel();
    const note = el("textarea", { rows: 2, maxlength: 2000 }, f.note || "");
    const copie = el("input", { type: "checkbox" });
    const dossierCopie = el("small", { class: "sans-icone" });
    const majCopie = () => {
      const rub = (client.value.trim() || projet.value.trim() || t("Non classé")).replace(/[<>:"/\\|?*]/g, " ");
      dossierCopie.textContent = t("Une copie va dans {dossier}. L'original ne bouge pas.", { dossier: D.r.classeur + selonSysteme("\\", "/") + rub });
    };
    client.addEventListener("input", majCopie); projet.addEventListener("input", majCopie); majCopie();

    const valider = async () => {
      const contact = D.contacts.find(c => libelleContact(c) && libelleContact(c) === client.value.trim());
      const valeurs = {
        type: type.value, client: client.value, contact_id: contact ? String(contact.id) : null, projet: projet.value,
        etiquettes: etiquettes.value, date_document: dateDoc.value, expiration: expiration.value,
        rappel_jours: Number(rappel.value), note: note.value,
      };
      if (!plusieurs) valeurs.titre = titre.value;
      if (fiche) {
        if (!(await action("/api/documents/modifier", { id: fiche.id, ...valeurs }, "Enregistré"))) return;
      } else {
        const r = await action("/api/documents/ajouter", { ...valeurs, chemins, genre, copier: copie.checked });
        if (!r) return;
        const n = r.ajoutes.length;
        if (n) toast(n > 1 ? t("{n} documents ajoutés", { n }) : t("Document ajouté"), "succes", 1800);
        if (r.deja) toast(n ? t("{n} déjà dans le classeur", { n: r.deja }) : t("Déjà dans le classeur"), "", 3000);
      }
      fermer();
      await afficher();
    };
    const apercu = chemins ? el("div", { class: "dc-fichiers" },
      chemins.slice(0, 4).map(c => el("div", { title: c }, icone(genre === "dossier" ? "folder" : "file"), el("span", { class: "sans-icone" }, nomDe(c)))),
      chemins.length > 4 ? el("div", {}, t("et {n} autres", { n: chemins.length - 4 })) : null) : null;
    fenetre([
      el("div", { class: "gros" }, icone(fiche ? "pencil" : "file-plus")),
      el("h3", {}, fiche ? "Modifier le document" : plusieurs ? t("Ajouter {n} documents", { n: chemins.length }) : "Ajouter un document"),
      apercu,
      plusieurs ? null : el("label", { class: "champ" }, "Titre", titre),
      el("div", { class: "dc-grille" },
        el("label", { class: "champ" }, "Type", type),
        el("label", { class: "champ" }, el("span", {}, t("Date du document"), " ", genre === "fichier" && !fiche ? el("small", {}, "vide : date du fichier") : null), dateDoc)),
      el("div", { class: "dc-grille" },
        el("label", { class: "champ" }, "Client", client), el("label", { class: "champ" }, "Projet", projet)),
      el("datalist", { id: "dc-clients" }, listeClients.map(c => el("option", { value: c }))),
      el("datalist", { id: "dc-projets" }, D.r.projets.map(p => el("option", { value: p }))),
      el("datalist", { id: "dc-etiquettes" }, D.r.etiquettes.map(p => el("option", { value: p }))),
      el("label", { class: "champ" }, el("span", {}, t("Étiquettes"), " ", el("small", {}, "séparées par des virgules")), etiquettes),
      el("div", { class: "dc-grille" },
        el("label", { class: "champ" }, el("span", {}, t("Expiration"), " ", el("small", {}, "facultatif")), expiration),
        el("label", { class: "champ" }, "Rappel", rappel)),
      el("label", { class: "champ" }, "Note (facultatif)", note),
      !fiche && genre === "fichier" ? el("label", { class: "dc-case" }, copie,
        el("span", {}, el("span", {}, "Copier dans le classeur"), dossierCopie)) : null,
      el("div", { class: "actions" },
        el("button", { class: "btn", onclick: fermer }, "Annuler"),
        el("button", { class: "btn principal", onclick: valider }, fiche ? "Enregistrer" : "Ajouter"))]);
    setTimeout(() => (plusieurs ? type : titre).focus(), 60);
  }

  // ------------------------------------------------------ accueil, palette
  async function carteAccueil() {
    const r = await api("/api/documents/liste", {});
    const proches = r.fiches.filter(f => f.jours !== null && f.jours !== undefined && f.jours <= SEUIL_ACCUEIL && f.jours >= -SEUIL_ACCUEIL)
      .sort((a, b) => a.jours - b.jours);
    if (!proches.length) return null;
    const delai = f => (f.jours < 0 ? t("Expiré") : f.jours === 0 ? t("Aujourd'hui") : t("{n} j", { n: f.jours }));
    return el("div", { class: "carte-jour", onclick: () => montrerVue("documents") },
      el("h4", {}, icone("folders"), "Documents à renouveler"),
      proches.slice(0, 4).map(f => el("div", { class: "ligne-jour" },
        el("span", { class: "heure dc-jours", style: f.jours < 0 ? "color:var(--rouge-texte)" : "color:var(--ambre-texte)" }, delai(f)),
        el("span", { class: "sans-icone" }, f.titre))),
      proches.length > 4 ? el("div", { class: "rien" }, t("et {n} autres", { n: proches.length - 4 })) : null);
  }

  function commandes() {
    const liste = [
      { icone: icone("file-plus"), titre: t("Ajouter des fichiers au classeur"), detail: t("Documents"), action: () => { montrerVue("documents"); ajouterFichiers(); } },
      { icone: icone("folder-open"), titre: t("Ajouter un dossier au classeur"), detail: t("Documents"), action: () => { montrerVue("documents"); ajouterDossier(); } },
    ];
    for (const f of (D.r?.fiches || []).filter(f => f.existe).slice(0, 60)) {
      liste.push({ icone: iconeFiche(f), titre: t("Ouvrir : {titre}", { titre: f.titre }), detail: [rubrique(f), f.nom].join(" · "), action: () => ouvrir(f) });
    }
    return liste;
  }

  VUES.documents = {
    afficher,
    titre: "Documents", icone: icone("folders"), groupe: "organisation", ordre: 10,
    description: "Un classeur des documents importants (contrats, devis signés, attestations…), rangés par client ou projet, avec un rappel avant expiration.",
    profils: ["freelance", "assistant_virtuel", "assistant_direction"],
    carteAccueil, commandes,
  };
})();
