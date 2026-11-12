"use strict";
/* Application « Contacts » : petit carnet de clients (voir contacts.py).
   Fiches personne ou entreprise, coordonnées, statut, étiquettes, historique
   des échanges, date de relance, import / export CSV. La liste est filtrée
   dans la page (recherche, statut, étiquette, relances). */
(() => {
  I18N.ajouter({
    "Contacts": "Contacts",
    "Contacts et clients : fiches, historique des échanges, relances, import et export CSV.":
      "Contacts and clients: records, history of exchanges, follow-ups, CSV import and export.",
    "Rechercher un contact": "Search a contact",
    "Nouveau contact": "New contact",
    "Importer": "Import", "Exporter": "Export",
    "Exporter en CSV (Excel, séparateur « ; »)": "Export as CSV (Excel, “;” separator)",
    "Importer un fichier CSV": "Import a CSV file",
    "Tous": "All",
    "À relancer": "To follow up",
    "Toutes les étiquettes": "All tags",
    "Personne": "Person", "Entreprise": "Company",
    "Aucun contact pour l'instant.": "No contact yet.",
    "Ajoutez vos clients et prospects, ou importez un fichier CSV.": "Add your clients and prospects, or import a CSV file.",
    "Aucun contact ne correspond.": "No matching contact.",
    "Effacer les filtres": "Clear filters",
    "Écrire": "Write", "Appeler": "Call", "Copier les coordonnées": "Copy contact details",
    "Modifier": "Edit", "Supprimer": "Delete", "Annuler": "Cancel", "Enregistrer": "Save", "Ajouter": "Add",
    "Pas d'adresse e-mail": "No email address", "Pas de numéro": "No phone number",
    "Coordonnées copiées": "Contact details copied",
    "Copier": "Copy", "Copié": "Copied",
    "E-mail": "Email", "Téléphone": "Phone", "Adresse": "Address", "Site web": "Website", "Poste": "Job title",
    "Prénom": "First name", "Nom": "Name", "Nom de l'entreprise": "Company name",
    "Statut": "Status", "Étiquettes": "Tags", "Relancer le": "Follow up on", "Motif de la relance": "Follow-up reason",
    "séparées par des virgules": "comma-separated",
    "ex. envoyer le devis": "e.g. send the quote",
    "ex. Gérante": "e.g. Manager", "ex. Société Exemple": "e.g. Example Ltd",
    "Aucune coordonnée": "No contact details",
    "{n} personne": "{n} person", "{n} personnes": "{n} people",
    "Personnes": "People",
    "Relance": "Follow-up",
    "Relancer aujourd'hui": "Follow up today", "Relancer demain": "Follow up tomorrow",
    "Relancer le {date}": "Follow up on {date}", "En retard · {date}": "Overdue · {date}",
    "Fait": "Done", "Relance faite": "Follow-up done",
    "Dans 3 jours": "In 3 days", "Dans 1 semaine": "In 1 week", "Dans 1 mois": "In 1 month",
    "Relance enregistrée": "Follow-up saved",
    "Historique des échanges": "History of exchanges",
    "Appel": "Call", "Mail": "Email", "Rendez-vous": "Appointment", "Note": "Note",
    "Compte rendu de l'appel, du mail, du rendez-vous…": "Summary of the call, email, meeting…",
    "Aucun échange noté pour l'instant.": "No exchange recorded yet.",
    "Supprimer cette note ?": "Delete this note?",
    "Elle disparaît de l'historique.": "It disappears from the history.",
    "Note ajoutée": "Note added", "Note supprimée": "Note deleted",
    "Contact enregistré": "Contact saved", "Contact ajouté": "Contact added", "Contact supprimé": "Contact deleted",
    "Modifier le contact": "Edit contact",
    "Supprimer « {nom} » ?": "Delete “{nom}”?",
    "La fiche et son historique sont effacés.": "The record and its history are erased.",
    "La fiche et son historique sont effacés. Les personnes de cette entreprise restent, sans entreprise.":
      "The record and its history are erased. The people of this company remain, without a company.",
    "Fiche créée le {date}": "Record created on {date}",
    "Ouvrir la fiche": "Open the record",
    "Importer des contacts": "Import contacts",
    "Fichier CSV (Excel, Google Contacts, Outlook…). Colonnes reconnues : Nom, Prénom, Entreprise, Poste, E-mail, Téléphone, Adresse, Site web, Statut, Étiquettes, Notes.":
      "CSV file (Excel, Google Contacts, Outlook…). Recognised columns: Last name, First name, Company, Job title, Email, Phone, Address, Website, Status, Tags, Notes.",
    "Une fiche déjà présente (même e-mail, sinon même nom) est complétée : rien n'est effacé.":
      "A record already present (same email, otherwise same name) is completed: nothing is erased.",
    "Choisir un fichier": "Choose a file",
    "Import terminé": "Import finished",
    "Ajoutés : {n}": "Added: {n}", "Complétés : {n}": "Completed: {n}", "Ignorés : {n}": "Skipped: {n}",
    "Fichier illisible": "Unreadable file",
    "Contacts à relancer": "Contacts to follow up",
    "Auj.": "Today",
    // Messages du serveur
    "Adresse e-mail invalide.": "Invalid email address.",
    "Numéro de téléphone invalide.": "Invalid phone number.",
    "Adresse du site invalide.": "Invalid website address.",
    "Date de relance invalide.": "Invalid follow-up date.",
    "Statut inconnu.": "Unknown status.",
    "Type de contact inconnu.": "Unknown contact type.",
    "Indiquez un nom.": "Enter a name.",
    "Entreprise introuvable.": "Company not found.",
    "Contact introuvable.": "Contact not found.",
    "Fiche invalide.": "Invalid record.",
    "Une fiche ne peut pas appartenir à elle-même.": "A record cannot belong to itself.",
    "Type d'échange inconnu.": "Unknown exchange type.",
    "Écrivez le contenu de la note.": "Write the content of the note.",
    "Date de la note invalide.": "Invalid note date.",
    "Note introuvable.": "Note not found.",
    "Le fichier est vide.": "The file is empty.",
    "Fichier trop gros (5 Mo au plus).": "File too large (5 MB maximum).",
    "Colonnes introuvables : il faut au moins « Nom » ou « Entreprise ».": "Columns not found: at least “Name” or “Company” is needed.",
  });
  I18N.motifs([[/^Ligne (\d+)$/, "Line $1"]]);

  const C = { r: null, recherche: "", statut: "tous", etiquette: "", relancer: false, ouvert: null, pret: null, typeNote: "note" };
  const STATUTS = [
    ["prospect", "Prospect", "Prospects", "ct-bleu"], ["client", "Client", "Clients", "vert"],
    ["ancien", "Ancien client", "Anciens clients", "gris"], ["fournisseur", "Fournisseur", "Fournisseurs", "ct-neutre"],
    ["autre", "Autre", "Autres", "gris"]];
  // Libellés des statuts : traduits ici (« Fournisseur » a un autre sens
  // ailleurs dans le dictionnaire commun de la page).
  const STATUTS_EN = { prospect: ["Prospect", "Prospects"], client: ["Client", "Clients"], ancien: ["Former client", "Former clients"],
    fournisseur: ["Supplier", "Suppliers"], autre: ["Other", "Others"] };
  const libStatut = (cle, pluriel = false) => {
    const s = STATUTS.find(x => x[0] === cle) || STATUTS[4];
    return txt(I18N.langue === "en" ? STATUTS_EN[s[0]][pluriel ? 1 : 0] : s[pluriel ? 2 : 1]);
  };
  const INFOS_STATUT = Object.fromEntries(STATUTS.map(s => [s[0], { classe: s[3] }]));
  const TYPES_NOTES = { appel: ["phone", "Appel"], mail: ["mail", "Mail"], rdv: ["calendar-days", "Rendez-vous"], note: ["sticky-note", "Note"] };

  const style = document.createElement("style");
  style.textContent = `
    .ct-filtres { display: flex; align-items: center; gap: 10px; margin: -6px 0 14px; flex-wrap: wrap; }
    .ct-filtres select { height: 34px; padding-top: 0 !important; padding-bottom: 0 !important; max-width: 220px; }
    .ct-nb { color: var(--gris); font-size: 11.5px; font-variant-numeric: tabular-nums; }
    .puce.actif .ct-nb { color: var(--doux); }
    .ct-sep { width: 1px; height: 20px; background: var(--ligne); }
    .etat-txt.ct-bleu { color: var(--bleu-texte); }
    .etat-txt.ct-neutre { color: var(--doux); }
    #vue-contacts .ligne-cote .ct-statut { min-width: 92px; justify-content: flex-end; }
    #vue-contacts .ligne-titre .ct-nom { overflow: hidden; text-overflow: ellipsis; }
    .ct-detail { display: grid; grid-template-columns: minmax(240px, 320px) minmax(0, 1fr); gap: 28px; padding-top: 14px; padding-bottom: 16px; }
    @media (max-width: 900px) { .ct-detail { grid-template-columns: 1fr; } }
    #vue-contacts .ligne { user-select: none; cursor: grab; }
    #vue-contacts .ligne.glisse { opacity: .5; }
    #vue-contacts .ligne.survol { background: var(--violet-clair); }
    .ct-titre { font-size: 11.5px; font-weight: 600; color: var(--gris); text-transform: uppercase; letter-spacing: .04em; margin: 0 0 8px; }
    .ct-titre + * { margin-top: 0; }
    .ct-bloc + .ct-bloc { margin-top: 18px; }
    .ct-info { display: flex; align-items: flex-start; gap: 10px; padding: 4px 0; min-height: 28px; }
    .ct-info > svg.ico { color: var(--gris); margin-top: 3px; }
    .ct-info .ct-val { flex: 1; min-width: 0; overflow-wrap: anywhere; white-space: pre-line; padding-top: 1px; }
    .ct-info .ct-val a { color: var(--encre); text-decoration: none; }
    .ct-info .ct-val a:hover { color: var(--violet); text-decoration: underline; }
    .ct-info .icone-btn { width: 26px; height: 26px; opacity: 0; }
    .ct-info:hover .icone-btn, .ct-info .icone-btn:focus-visible { opacity: 1; }
    .ct-info .icone-btn svg.ico { width: 14px; height: 14px; }
    .ct-membre { display: flex; align-items: center; gap: 8px; padding: 4px 0; cursor: pointer; }
    .ct-membre:hover .ct-n { color: var(--violet); }
    .ct-membre small { color: var(--gris); }
    .ct-relance { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; }
    .ct-relance input { width: 160px; }
    .ct-motif { width: 100%; }
    .ct-rapides { display: flex; gap: 4px; flex-wrap: wrap; margin-top: 8px; }
    .ct-cree { color: var(--gris); font-size: 12px; margin-top: 18px; }
    .ct-saisie { border: 1px solid var(--ligne); border-radius: 8px; background: var(--carte); padding: 8px; margin-bottom: 12px; }
    .ct-saisie textarea { width: 100%; border: 0 !important; box-shadow: none !important; background: transparent !important; resize: vertical; min-height: 48px; padding: 4px 6px !important; }
    .ct-saisie .ct-bas { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; border-top: 1px solid var(--ligne); padding-top: 8px; margin-top: 4px; }
    .ct-saisie .ct-bas .espace { flex: 1; }
    .ct-saisie .puces { background: var(--surface); }
    .ct-saisie .puce { height: 26px; padding: 0 9px; font-size: 12.5px; }
    .ct-saisie input[type=datetime-local] { height: 28px; padding: 0 8px !important; font-size: 12.5px; }
    .ct-notes { display: flex; flex-direction: column; }
    .ct-note { display: flex; gap: 10px; padding: 8px 0; border-top: 1px solid var(--ligne); }
    .ct-note:first-child { border-top: 0; }
    .ct-note > svg.ico { color: var(--gris); margin-top: 3px; }
    .ct-note .ct-corps { flex: 1; min-width: 0; }
    .ct-note .ct-quand { color: var(--gris); font-size: 12px; }
    .ct-note .ct-texte { white-space: pre-wrap; overflow-wrap: anywhere; }
    .ct-note .icone-btn { width: 26px; height: 26px; opacity: 0; }
    .ct-note:hover .icone-btn, .ct-note .icone-btn:focus-visible { opacity: 1; }
    .ct-note .icone-btn svg.ico { width: 14px; height: 14px; }
    .ct-rien { color: var(--gris); font-size: 13px; padding: 4px 0; }
    .ct-deux { display: grid; grid-template-columns: 1fr 1fr; gap: 0 12px; }
    .ct-form .puces { margin-bottom: 14px; }
    .ct-form label.champ { margin-bottom: 11px; }
    .ct-sugg { display: flex; gap: 4px; flex-wrap: wrap; margin-top: -5px; margin-bottom: 11px; }
    .ct-sugg:empty { display: none; }
    .ct-sugg button { cursor: pointer; background: transparent; }
    .ct-sugg button:hover { color: var(--encre); border-color: var(--ligne-forte); }
    .ct-bilan { display: flex; gap: 18px; margin: 4px 0 10px; font-variant-numeric: tabular-nums; }
    .ct-erreurs { margin: 0; padding-left: 18px; color: var(--rouge-texte); font-size: 13px; }
    .ct-carte-nom { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; }
    .carte-jour .ligne-jour .heure.ct-retard { color: var(--rouge-texte); }
  `;
  document.head.append(style);

  // --------------------------------------------------------------- outils
  const racine = () => $("#vue-contacts");
  /** Une donnée de l'utilisateur : du texte, jamais traduit. */
  const txt = s => document.createTextNode(s === null || s === undefined ? "" : String(s));
  const sansAccents = s => String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const chiffres = s => String(s || "").replace(/\D/g, "");
  const deux = n => String(n).padStart(2, "0");
  const isoJour = d => `${d.getFullYear()}-${deux(d.getMonth() + 1)}-${deux(d.getDate())}`;
  const isoMinute = d => `${isoJour(d)}T${deux(d.getHours())}:${deux(d.getMinutes())}`;
  const jour = iso => new Date(iso.slice(0, 10) + "T00:00");
  const aujourdhui = () => C.r?.aujourdhui || isoJour(new Date());
  function dateCourte(iso) {
    const d = jour(iso), opts = { day: "numeric", month: "short" };
    if (d.getFullYear() !== jour(aujourdhui()).getFullYear()) opts.year = "numeric";
    return d.toLocaleDateString(I18N.locale(), opts);
  }
  function dans(jours) {
    const d = jour(aujourdhui());
    d.setDate(d.getDate() + jours);
    return isoJour(d);
  }
  const ecarts = iso => Math.round((jour(iso) - jour(aujourdhui())) / 864e5);
  const erreur = e => toast(e.message, "erreur", 5000);

  function ouvrirLien(href) {
    const a = el("a", { href, rel: "noopener" });
    if (/^https?:/.test(href)) a.target = "_blank";
    document.body.append(a); a.click(); a.remove();
  }

  // -------------------------------------------------------------- données
  async function charger() {
    C.r = await api("/api/contacts/tout", {});
    if (C.ouvert && !C.r.contacts.some(c => c.id === C.ouvert)) C.ouvert = null;
  }
  async function recharger() {
    try { await charger(); dessinerListe(); } catch (e) { erreur(e); }
  }
  const parId = id => C.r?.contacts.find(c => c.id === id);
  const entreprises = () => (C.r?.contacts || []).filter(c => c.type === "entreprise");

  function visibles() {
    const mots = sansAccents(C.recherche).split(/\s+/).filter(Boolean);
    const num = chiffres(C.recherche);
    const parTel = num.length >= 4 && /^[\d\s+().\-/]+$/.test(C.recherche.trim());
    const jourIso = aujourdhui();
    const liste = C.r.contacts.filter(c => {
      if (C.statut !== "tous" && c.statut !== C.statut) return false;
      if (C.relancer && !(c.relance && c.relance <= jourIso)) return false;
      if (C.etiquette && !(c.etiquettes || []).includes(C.etiquette)) return false;
      if (!mots.length) return true;
      if (parTel && chiffres(c.telephone).includes(num)) return true;
      const texte = sansAccents([c.nom_affiche, c.entreprise, c.email, c.telephone, c.poste, c.adresse, c.site,
        ...(c.etiquettes || [])].filter(Boolean).join(" "));
      return mots.every(m => texte.includes(m));
    });
    if (C.relancer) liste.sort((a, b) => a.relance.localeCompare(b.relance));
    else {
      const ordre = S.config?.ordre_contacts;
      if (Array.isArray(ordre) && !C.recherche && C.statut === "tous" && !C.etiquette) {
        liste.sort((a, b) => {
          const ia = ordre.indexOf(a.id), ib = ordre.indexOf(b.id);
          if (ia >= 0 && ib >= 0) return ia - ib;
          if (ia >= 0) return -1;
          if (ib >= 0) return 1;
          return 0;
        });
      }
    }
    return liste;
  }

  // -------------------------------------------------------------- dessin
  function dessiner() {
    const recherche = el("input", { type: "search", placeholder: "Rechercher un contact", value: C.recherche,
      oninput: e => { C.recherche = e.target.value; dessinerListe(); } });
    racine().replaceChildren(
      el("div", { class: "barre-vue" },
        el("h2", {}, icone("contact"), "Contacts", el("span", { class: "compte", id: "ct-total" }, String(C.r.contacts.length))),
        el("div", { class: "espace" }),
        el("label", { class: "champ-recherche" }, el("span", {}, icone("search")), recherche),
        el("button", { class: "btn", title: "Importer un fichier CSV", onclick: fenetreImport }, icone("upload"), "Importer"),
        el("button", { class: "btn", title: "Exporter en CSV (Excel, séparateur « ; »)", onclick: exporter }, icone("download"), "Exporter"),
        el("button", { class: "btn principal", onclick: () => editer(null) }, icone("user-plus"), "Nouveau contact")),
      el("div", { class: "ct-filtres", id: "ct-filtres" }),
      el("div", { id: "ct-liste" }));
    dessinerListe();
  }

  function dessinerFiltres() {
    const n = C.r.compteurs;
    const puce = (actif, lib, nombre, action) =>
      el("button", { class: "puce " + (actif ? " actif" : ""), onclick: action }, lib,
        nombre !== null ? el("span", { class: "ct-nb" }, String(nombre)) : null);
    const filtres = [
      el("div", { class: "puces" },
        puce(C.statut === "tous", "Tous", C.r.contacts.length, () => { C.statut = "tous"; dessinerListe(); }),
        STATUTS.filter(([cle]) => n[cle] || C.statut === cle).map(([cle]) =>
          puce(C.statut === cle, libStatut(cle, true), n[cle], () => { C.statut = cle; dessinerListe(); }))),
      n.relancer || C.relancer ? el("div", { class: "puces" },
        el("button", { class: "puce " + (C.relancer ? " actif" : ""), onclick: () => { C.relancer = !C.relancer; dessinerListe(); } },
          icone("bell"), "À relancer", el("span", { class: "ct-nb" }, String(n.relancer)))) : null,
    ];
    if (C.r.etiquettes.length) {
      if (C.etiquette && !C.r.etiquettes.includes(C.etiquette)) C.etiquette = "";
      filtres.push(el("select", { title: "Étiquettes", onchange: e => { C.etiquette = e.target.value; dessinerListe(); } },
        el("option", { value: "" }, "Toutes les étiquettes"),
        C.r.etiquettes.map(e => { const o = el("option", { value: e }, txt(e)); o.selected = e === C.etiquette; return o; })));
    }
    $("#ct-filtres").replaceChildren(...filtres);
  }

  function dessinerListe() {
    if (!racine() || !C.r) return;
    $("#ct-total").textContent = C.r.contacts.length;
    dessinerFiltres();
    const boite = $("#ct-liste");
    if (!C.r.contacts.length) {
      boite.replaceChildren(el("div", { class: "vide" }, icone("contact"), el("div", {}, "Aucun contact pour l'instant."),
        el("div", { style: "margin-top:4px;color:var(--gris)" }, "Ajoutez vos clients et prospects, ou importez un fichier CSV."),
        el("div", { style: "margin-top:14px;display:flex;gap:8px;justify-content:center" },
          el("button", { class: "btn principal", onclick: () => editer(null) }, icone("user-plus"), "Nouveau contact"),
          el("button", { class: "btn", onclick: fenetreImport }, icone("upload"), "Importer"))));
      return;
    }
    const liste = visibles();
    if (!liste.length) {
      boite.replaceChildren(el("div", { class: "vide" }, icone("search"), el("div", {}, "Aucun contact ne correspond."),
        el("button", { class: "btn discret", style: "margin-top:10px", onclick: () => {
          Object.assign(C, { recherche: "", statut: "tous", etiquette: "", relancer: false });
          dessiner();
        } }, "Effacer les filtres")));
      return;
    }
    const lignes = el("div", { class: "lignes" });
    liste.forEach(c => {
      const l = ligne(c);
      l.setAttribute("draggable", "true");
      l.addEventListener("dragstart", ev => { ev.dataTransfer.effectAllowed = "move"; ev.dataTransfer.setData("text/plain", c.id); l.classList.add("glisse"); });
      l.addEventListener("dragend", () => { l.classList.remove("glisse"); lignes.querySelectorAll(".ligne").forEach(x => x.classList.remove("survol")); });
      l.addEventListener("dragover", ev => { ev.preventDefault(); ev.dataTransfer.dropEffect = "move"; l.classList.add("survol"); });
      l.addEventListener("dragleave", () => l.classList.remove("survol"));
      l.addEventListener("drop", ev => {
        ev.preventDefault();
        l.classList.remove("survol");
        const fromId = ev.dataTransfer.getData("text/plain");
        const toId = c.id;
        if (fromId === toId) return;
        const contacts = [...C.r.contacts];
        const fromIdx = contacts.findIndex(x => x.id === fromId);
        const toIdx = contacts.findIndex(x => x.id === toId);
        if (fromIdx < 0 || toIdx < 0) return;
        const moved = contacts.splice(fromIdx, 1)[0];
        contacts.splice(toIdx, 0, moved);
        C.r.contacts = contacts;
        const ordre = contacts.map(x => x.id);
        if (S.config) S.config.ordre_contacts = ordre;
        api("/api/reglages/enregistrer", { ordre_contacts: ordre }).catch(e => toast(e.message, "erreur"));
        dessinerListe();
      });
      lignes.append(l);
    });
    boite.replaceChildren(lignes);
  }

  function texteRelance(c) {
    if (!c.relance) return null;
    const e = ecarts(c.relance);
    if (e < 0) return el("span", { class: "etat-txt rouge" }, icone("bell"), t("En retard · {date}", { date: dateCourte(c.relance) }));
    if (e === 0) return el("span", { class: "etat-txt ambre" }, icone("bell"), "Relancer aujourd'hui");
    if (e === 1) return el("span", { class: "etat-txt gris" }, "Relancer demain");
    return el("span", { class: "etat-txt gris" }, t("Relancer le {date}", { date: dateCourte(c.relance) }));
  }

  function texteStatut(statut) {
    const s = INFOS_STATUT[statut] || INFOS_STATUT.autre;
    return el("span", { class: "etat-txt ct-statut " + s.classe }, libStatut(statut));
  }

  function meta(c) {
    const morceaux = c.type === "entreprise"
      ? [(c.membres || []).length ? t((c.membres.length > 1 ? "{n} personnes" : "{n} personne"), { n: c.membres.length }) : ""]
      : [[c.poste, c.entreprise].filter(Boolean).join(", ")];
    morceaux.push(c.email, c.telephone);
    const texte = morceaux.filter(Boolean).join(" · ");
    return texte ? txt(texte) : el("span", { style: "color:var(--gris)" }, "Aucune coordonnée");
  }

  function ligne(c) {
    const ouvert = C.ouvert === c.id;
    const stop = f => e => { e.stopPropagation(); f(); };
    return [
      el("div", { class: "ligne cliquable " + (ouvert ? " ouverte" : ""), "data-id": c.id, onclick: () => basculer(c.id) },
        el("span", { class: "ligne-ic" }, icone(c.type === "entreprise" ? "building-2" : "user")),
        el("div", { class: "ligne-corps" },
          el("div", { class: "ligne-titre" }, el("span", { class: "ct-nom sans-icone" }, txt(c.nom_affiche)),
            (c.etiquettes || []).slice(0, 4).map(e => el("span", { class: "tag sans-icone" }, txt(e)))),
          el("div", { class: "ligne-meta sans-icone" }, meta(c))),
        el("div", { class: "ligne-cote" }, texteRelance(c), texteStatut(c.statut)),
        el("div", { class: "ligne-actions" },
          el("button", { class: "icone-btn", title: c.email ? "Écrire" : "Pas d'adresse e-mail", disabled: c.email ? null : "",
            onclick: stop(() => ouvrirLien("mailto: " + c.email)) }, icone("mail")),
          el("button", { class: "icone-btn", title: c.telephone ? "Appeler" : "Pas de numéro", disabled: c.telephone ? null : "",
            onclick: stop(() => ouvrirLien("tel: " + c.telephone.replace(/[^\d+]/g, ""))) }, icone("phone")),
          el("button", { class: "icone-btn", title: "Copier les coordonnées", onclick: stop(() => copier(coordonnees(c), "Coordonnées copiées")) }, icone("copy")),
          el("button", { class: "icone-btn", title: "Modifier", onclick: stop(() => editer(c)) }, icone("pencil")),
          el("button", { class: "icone-btn danger", title: "Supprimer", onclick: stop(() => supprimer(c)) }, icone("trash-2")))),
      ouvert ? detail(c) : null,
    ];
  }

  function coordonnees(c) {
    return [c.nom_affiche, [c.poste, c.entreprise].filter(Boolean).join(", "), c.email, c.telephone, c.adresse, c.site]
      .filter(Boolean).join("\n");
  }

  function basculer(id) {
    C.ouvert = C.ouvert === id ? null : id;
    dessinerListe();
  }

  /** Ouvre la fiche d'un autre contact (membre, entreprise) et la montre. */
  function allerA(id) {
    Object.assign(C, { ouvert: id, recherche: "", statut: "tous", etiquette: "", relancer: false });
    dessiner();
    requestAnimationFrame(() => racine().querySelector(`.ligne[data-id="${id}"]`)?.scrollIntoView({ block: "center", behavior: "smooth" }));
  }

  // -------------------------------------------------------- fiche dépliée
  function info(nomIcone, valeur, lien, copiable = true) {
    if (!valeur) return null;
    return el("div", { class: "ct-info" }, icone(nomIcone),
      el("div", { class: "ct-val sans-icone" }, lien ? el("a", { href: lien, rel: "noopener", target: /^https?:/.test(lien) ? "_blank" : null }, txt(valeur)) : txt(valeur)),
      copiable ? el("button", { class: "icone-btn", title: "Copier", onclick: () => copier(valeur, "Copié") }, icone("copy")) : null);
  }

  function detail(c) {
    const membres = c.type === "entreprise" && c.membres?.length
      ? el("div", { class: "ct-bloc" }, el("div", { class: "ct-titre" }, "Personnes"),
        c.membres.map(m => el("div", { class: "ct-membre", title: "Ouvrir la fiche", onclick: () => allerA(m.id) },
          icone("user"), el("span", { class: "ct-n sans-icone" }, txt(m.nom)), m.poste ? el("small", { class: "sans-icone" }, txt(m.poste)) : null)))
      : null;
    const entreprise = c.entreprise_id
      ? el("div", { class: "ct-info" }, icone("building-2"),
        el("div", { class: "ct-val" }, el("a", { href: "#contacts", title: "Ouvrir la fiche", onclick: e => { e.preventDefault(); allerA(c.entreprise_id); } }, txt(c.entreprise))))
      : null;
    const coord = [entreprise, info("briefcase", c.poste, null, false), info("mail", c.email, "mailto: " + c.email),
      info("phone", c.telephone, "tel: " + chiffresTel(c.telephone)), info("map-pin", c.adresse), info("globe", c.site, c.site)].filter(Boolean);
    return el("div", { class: "ligne-detail ct-detail" },
      el("div", {},
        el("div", { class: "ct-bloc" }, coord.length ? coord : el("div", { class: "ct-rien" }, "Aucune coordonnée")),
        membres,
        blocRelance(c),
        c.cree ? el("div", { class: "ct-cree" }, t("Fiche créée le {date}", { date: dateCourte(c.cree) })) : null),
      blocHistorique(c));
  }
  const chiffresTel = s => String(s || "").replace(/[^\d+]/g, "");

  function blocRelance(c) {
    const date = el("input", { type: "date", value: c.relance || "", "aria-label": "Relancer le" });
    const motif = el("input", { value: c.relance_motif || "", class: "ct-motif", placeholder: "ex. envoyer le devis", maxlength: 200, "aria-label": "Motif de la relance" });
    const envoyer = async (valeur, message = "Relance enregistrée") => {
      try {
        await api("/api/contacts/relance", { id: c.id, date: valeur, motif: motif.value });
        toast(message, "succes", 1400);
        await recharger();
      } catch (e) { erreur(e); }
    };
    date.addEventListener("change", () => envoyer(date.value));
    motif.addEventListener("change", () => { if (date.value) envoyer(date.value); });
    motif.addEventListener("keydown", e => { if (e.key === "Enter") motif.blur(); });
    return el("div", { class: "ct-bloc" },
      el("div", { class: "ct-titre" }, "Relance"),
      el("div", { class: "ct-relance" }, date,
        c.relance ? el("button", { class: "btn", onclick: () => envoyer("", "Relance faite") }, icone("check"), "Fait") : null),
      motif,
      el("div", { class: "ct-rapides" },
        [[3, "Dans 3 jours"], [7, "Dans 1 semaine"], [30, "Dans 1 mois"]].map(([n, lib]) =>
          el("button", { class: "btn petit discret", onclick: () => envoyer(dans(n)) }, lib))));
  }

  function blocHistorique(c) {
    const texte = el("textarea", { rows: 2, placeholder: "Compte rendu de l'appel, du mail, du rendez-vous…", maxlength: 4000 });
    const quand = el("input", { type: "datetime-local", value: isoMinute(new Date()), "aria-label": "Date" });
    const types = el("div", { class: "puces" });
    const dessinerTypes = () => types.replaceChildren(...Object.entries(TYPES_NOTES).map(([cle, [ic, lib]]) =>
      el("button", { class: "puce " + (C.typeNote === cle ? " actif" : ""), onclick: () => { C.typeNote = cle; dessinerTypes(); } }, icone(ic), lib)));
    dessinerTypes();
    const ajouter = async () => {
      try {
        await api("/api/contacts/note/ajouter", { id: c.id, note: { type: C.typeNote, texte: texte.value, date: quand.value } });
        toast("Note ajoutée", "succes", 1400);
        await recharger();
      } catch (e) { erreur(e); texte.focus(); }
    };
    texte.addEventListener("keydown", e => { if (e.key === "Enter" && e.ctrlKey) ajouter(); });
    const notes = c.notes || [];
    return el("div", {},
      el("div", { class: "ct-titre" }, "Historique des échanges"),
      el("div", { class: "ct-saisie" }, texte,
        el("div", { class: "ct-bas" }, types, el("span", { class: "espace" }), quand,
          el("button", { class: "btn principal petit", title: "Ctrl + Entrée", onclick: ajouter }, "Ajouter"))),
      notes.length
        ? el("div", { class: "ct-notes" }, notes.map(n => {
          const [ic, lib] = TYPES_NOTES[n.type] || TYPES_NOTES.note;
          const d = new Date(n.date);
          return el("div", { class: "ct-note" }, icone(ic),
            el("div", { class: "ct-corps" },
              el("div", { class: "ct-quand" }, t(lib) + "· " + d.toLocaleString(I18N.locale(),
                { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" })),
              el("div", { class: "ct-texte sans-icone" }, txt(n.texte))),
            el("button", { class: "icone-btn danger", title: "Supprimer", onclick: () => supprimerNote(c, n) }, icone("trash-2")));
        }))
        : el("div", { class: "ct-rien" }, "Aucun échange noté pour l'instant."));
  }

  // ------------------------------------------------------------- actions
  async function supprimer(c) {
    const texte = c.type === "entreprise" && c.membres?.length
      ? "La fiche et son historique sont effacés. Les personnes de cette entreprise restent, sans entreprise."
      : "La fiche et son historique sont effacés.";
    if (!(await confirmer(icone("trash-2"), t("Supprimer « {nom} » ?", { nom: c.nom_affiche }), texte, "Supprimer"))) return;
    try {
      await api("/api/contacts/supprimer", { id: c.id });
      toast("Contact supprimé");
      await recharger();
    } catch (e) { erreur(e); }
  }

  async function supprimerNote(c, n) {
    if (!(await confirmer(icone("trash-2"), "Supprimer cette note ?", "Elle disparaît de l'historique.", "Supprimer"))) return;
    try {
      await api("/api/contacts/note/supprimer", { id: c.id, note_id: n.id });
      toast("Note supprimée");
      await recharger();
    } catch (e) { erreur(e); }
  }

  function editer(c) {
    const b = c ? { ...c } : { type: "personne", statut: "prospect", etiquettes: [] };
    const champ = (lib, entree, aide) => el("label", { class: "champ" }, lib, entree, aide ? el("small", {}, aide) : null);
    const entree = (cle, attrs = {}) => el("input", { value: b[cle] || "", maxlength: 120, ...attrs });
    const prenom = entree("prenom"), nom = entree("nom");
    const entreprise = entree("entreprise", { list: "ct-entreprises", placeholder: "ex. Société Exemple" });
    const poste = entree("poste", { placeholder: "ex. Gérante" });
    const email = entree("email", { type: "email" }), telephone = entree("telephone", { type: "tel", maxlength: 30 });
    const adresse = el("textarea", { rows: 2, maxlength: 300 }); adresse.value = b.adresse || "";
    const site = entree("site", { placeholder: "www.exemple.com", maxlength: 300 });
    const statut = el("select", {}, STATUTS.map(([cle]) => { const o = el("option", { value: cle }, libStatut(cle)); o.selected = cle === b.statut; return o; }));
    const etiquettes = el("input", { value: (b.etiquettes || []).join(", "), maxlength: 400, placeholder: "séparées par des virgules" });
    const relance = el("input", { type: "date", value: b.relance || "" });
    const motif = entree("relance_motif", { placeholder: "ex. envoyer le devis", maxlength: 200 });
    const libNom = el("label", { class: "champ" }, "Nom", nom);
    const blocPrenom = champ("Prénom", prenom), blocEntreprise = champ("Entreprise", entreprise,
      null), blocPoste = champ("Poste", poste);
    const lignePersonne = el("div", { class: "ct-deux" }, blocEntreprise, blocPoste);
    const ligneNom = el("div", { class: "ct-deux" }, blocPrenom, libNom);
    const types = el("div", { class: "puces" });
    const majType = () => {
      types.replaceChildren(...[["personne", "user", "Personne"], ["entreprise", "building-2", "Entreprise"]].map(([cle, ic, lib]) =>
        el("button", { type: "button", class: "puce " + (b.type === cle ? " actif" : ""), onclick: () => { b.type = cle; majType(); } }, icone(ic), lib)));
      const personne = b.type === "personne";
      blocPrenom.hidden = !personne;
      lignePersonne.hidden = !personne;
      ligneNom.style.gridTemplateColumns = personne ? "" : "1fr";
      libNom.firstChild.textContent = t(personne ? "Nom" : "Nom de l'entreprise");
    };
    majType();
    // Étiquettes déjà utilisées : un clic les ajoute.
    const suggestions = el("div", { class: "ct-sugg" });
    const majSuggestions = () => {
      const deja = new Set(etiquettes.value.split(",").map(x => sansAccents(x.trim())).filter(Boolean));
      suggestions.replaceChildren(...C.r.etiquettes.filter(e => !deja.has(sansAccents(e))).slice(0, 12).map(e =>
        el("button", { type: "button", class: "tag", onclick: () => {
          etiquettes.value = [...etiquettes.value.split(",").map(x => x.trim()).filter(Boolean), e].join(", ");
          majSuggestions();
        } }, txt(e))));
    };
    etiquettes.addEventListener("input", majSuggestions);
    majSuggestions();

    const valider = async () => {
      const nomEntreprise = entreprise.value.trim();
      const contact = {
        id: c?.id, type: b.type, prenom: prenom.value, nom: nom.value, poste: poste.value,
        email: email.value, telephone: telephone.value, adresse: adresse.value, site: site.value,
        statut: statut.value, etiquettes: etiquettes.value, relance: relance.value, relance_motif: motif.value,
      };
      // Même entreprise qu'avant : par son identifiant ; sinon par son nom (créée si besoin).
      if (b.type === "personne" && nomEntreprise) {
        if (c?.entreprise_id && nomEntreprise === c.entreprise) contact.entreprise_id = c.entreprise_id;
        else contact.entreprise = nomEntreprise;
      }
      try {
        const r = await api("/api/contacts/enregistrer", { contact });
        fermer();
        toast(c ? "Contact enregistré" : "Contact ajouté", "succes", 1600);
        C.ouvert = r.id;
        await recharger();
        requestAnimationFrame(() => racine().querySelector(`.ligne[data-id="${r.id}"]`)?.scrollIntoView({ block: "nearest" }));
      } catch (e) { erreur(e); }
    };
    // Entrée dans un champ : enregistrer (écouteur posé sur le formulaire,
    // remplacé avec lui à la prochaine fenêtre).
    const enter = e => {
      if (e.key === "Enter" && e.target.tagName === "INPUT") { e.preventDefault(); valider(); }
    };
    fenetre([
      el("h3", {}, c ? "Modifier le contact" : "Nouveau contact"),
      el("div", { class: "ct-form", onkeydown: enter },
        types, ligneNom, lignePersonne,
        el("datalist", { id: "ct-entreprises" }, entreprises().filter(e => e.id !== c?.id).map(e => el("option", { value: e.nom_affiche }))),
        el("div", { class: "ct-deux" }, champ("E-mail", email), champ("Téléphone", telephone)),
        champ("Adresse", adresse),
        el("div", { class: "ct-deux" }, champ("Site web", site), champ("Statut", statut)),
        champ("Étiquettes", etiquettes), suggestions,
        el("div", { class: "ct-deux" }, champ("Relancer le", relance), champ("Motif de la relance", motif))),
      el("div", { class: "actions" },
        el("button", { class: "btn", onclick: fermer }, "Annuler"),
        el("button", { class: "btn principal", onclick: valider }, c ? "Enregistrer" : "Ajouter"))]);
    setTimeout(() => (b.type === "personne" ? prenom : nom).focus(), 60);
  }

  // ----------------------------------------------------- import / export
  async function exporter() {
    try {
      const r = await api("/api/contacts/export", {});
      const lien = el("a", { href: URL.createObjectURL(new Blob([r.csv], { type: "text/csv;charset=utf-8" })), download: r.nom });
      document.body.append(lien); lien.click(); lien.remove();
      setTimeout(() => URL.revokeObjectURL(lien.href), 5000);
    } catch (e) { erreur(e); }
  }

  /** Le texte d'un fichier : UTF-8, sinon Windows-1252 (ancien Excel). */
  async function lireFichier(fichier) {
    const octets = await fichier.arrayBuffer();
    try { return new TextDecoder("utf-8", { fatal: true }).decode(octets); }
    catch { return new TextDecoder("windows-1252").decode(octets); }
  }

  function fenetreImport() {
    const choix = el("input", { type: "file", accept: ".csv,text/csv", hidden: "" });
    choix.addEventListener("change", async () => {
      const fichier = choix.files[0];
      if (!fichier) return;
      let texte;
      try { texte = await lireFichier(fichier); } catch { toast("Fichier illisible", "erreur"); return; }
      try {
        const r = await api("/api/contacts/import", { csv: texte });
        await charger(); dessiner();
        fenetre([
          el("div", { class: "gros" }, icone("circle-check")),
          el("h3", {}, "Import terminé"),
          el("div", { class: "ct-bilan" },
            el("span", {}, t("Ajoutés : {n}", { n: r.ajoutes })), el("span", {}, t("Complétés : {n}", { n: r.completes })),
            el("span", { style: r.ignores ? "color:var(--doux)" : "color:var(--gris)" }, t("Ignorés : {n}", { n: r.ignores }))),
          r.erreurs.length ? el("ul", { class: "ct-erreurs" }, r.erreurs.map(x => el("li", {}, x))) : null,
          el("div", { class: "actions" }, el("button", { class: "btn principal", onclick: fermer }, "OK"))], true);
      } catch (e) { erreur(e); }
    });
    fenetre([
      el("div", { class: "gros" }, icone("upload")),
      el("h3", {}, "Importer des contacts"),
      el("p", {}, "Fichier CSV (Excel, Google Contacts, Outlook…). Colonnes reconnues : Nom, Prénom, Entreprise, Poste, E-mail, Téléphone, Adresse, Site web, Statut, Étiquettes, Notes."),
      el("p", {}, "Une fiche déjà présente (même e-mail, sinon même nom) est complétée : rien n'est effacé."),
      choix,
      el("div", { class: "actions" },
        el("button", { class: "btn", onclick: fermer }, "Annuler"),
        el("button", { class: "btn principal", onclick: () => choix.click() }, icone("file-up"), "Choisir un fichier"))]);
  }

  // -------------------------------------------------------- application
  async function afficher() {
    C.pret = charger();
    try { await C.pret; dessiner(); } catch (e) { erreur(e); }
  }

  async function ouvrirAvec(action) {
    montrerVue("contacts");
    try { await C.pret; } catch { return; }
    action();
  }

  async function carteAccueil() {
    let r;
    try { r = await api("/api/contacts/a_relancer", { limite: 5 }); } catch { return null; }
    if (!r.relances?.length) return null;
    return el("div", { class: "carte-jour", onclick: () => ouvrirAvec(() => { Object.assign(C, { relancer: true, statut: "tous" }); dessiner(); }) },
      el("h4", {}, icone("bell"), "À relancer"),
      r.relances.map(x => el("div", { class: "ligne-jour" },
        el("span", { class: "heure " + (x.retard > 0 ? " ct-retard" : "") }, x.retard > 0 ? dateCourte(x.relance) : t("Auj.")),
        el("span", { class: "ct-carte-nom sans-icone" }, txt(x.nom + (x.entreprise ? "· " + x.entreprise : ""))))));
  }

  VUES.contacts = {
    afficher,
    titre: "Contacts", icone: icone("contact"), groupe: "clients", ordre: 10,
    description: "Contacts et clients : fiches, historique des échanges, relances, import et export CSV.",
    profils: ["freelance", "assistant_virtuel", "assistant_direction"],
    carteAccueil,
    commandes: () => [
      { icone: icone("user-plus"), titre: "Nouveau contact", detail: "Contacts", action: () => ouvrirAvec(() => editer(null)) },
      { icone: icone("bell"), titre: "Contacts à relancer", detail: "Contacts",
        action: () => ouvrirAvec(() => { Object.assign(C, { relancer: true, statut: "tous" }); dessiner(); }) },
      { icone: icone("upload"), titre: "Importer des contacts", detail: "Contacts", action: () => ouvrirAvec(fenetreImport) },
    ],
  };
})();
