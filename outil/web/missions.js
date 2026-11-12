"use strict";
/* Application « Missions » (voir missions.py) : offres freelance et
   télétravail de cinq sources publiques, notées selon chaque recherche
   enregistrée, et suivi des candidatures. Les offres restent dans leur langue ;
   la source est toujours citée et le lien d'origine ouvert tel quel.
   Utilise, si elles sont actives : Modèles (message de candidature), Contacts
   (ajouter l'entreprise), Tâches (relance d'une candidature). */
(() => {
  I18N.ajouter({
    "Missions": "Missions",
    "Offres freelance et télétravail de cinq sites publics, classées selon ce que vous cherchez, avec le suivi de vos candidatures.":
      "Freelance and remote offers from five public sites, ranked by what you are looking for, with your applications tracked.",
    "Actualiser": "Refresh",
    "Sources": "Sources",
    "Nouvelle recherche": "New search",
    "Modifier la recherche": "Edit search",
    "Candidatures": "Applications",
    "Suivi des candidatures": "Application tracking",
    "Collecte en cours…": "Collecting…",
    "Chargement…": "Loading…",
    "Jamais collectées": "Never collected",
    "Mis à jour à l'instant": "Updated just now",
    "Nouvelles": "New",
    "Déjà vues": "Already seen",
    "Aucune offre pour cette recherche.": "No offer for this search.",
    "Élargissez les domaines, les types ou les zones, ou baissez le score minimum.":
      "Widen the fields, types or zones, or lower the minimum score.",
    "Cliquez sur « Actualiser » pour collecter les offres.": "Click “Refresh” to collect offers.",
    "Afficher plus": "Show more",
    "Ouvrir l'offre": "Open offer",
    "Postuler": "Apply",
    "Suivre": "Track",
    "Ajouter l'entreprise aux contacts": "Add company to contacts",
    "Masquer": "Hide",
    "Score": "Score",
    "Localisation": "Location",
    "Domaine": "Field",
    "Technologies": "Technologies",
    "Expérience demandée": "Experience required",
    "Non précisée": "Not specified",
    "Salaire": "Salary",
    "Mots trouvés": "Matched words",
    "Mots à éviter trouvés": "Words to avoid found",
    "Publiée le": "Published on",
    "Expire le": "Expires on",
    "Source": "Source",
    "Aujourd'hui": "Today", "Hier": "Yesterday",
    "Chercher aussi sur": "Also search on",
    "Ces sites n'ont pas d'accès public : la recherche s'ouvre dans le navigateur avec vos mots-clés.":
      "These sites have no public access: the search opens in your browser with your keywords.",
    "Critères": "Criteria",
    "Domaines": "Fields", "Types": "Types", "Zones": "Zones", "Niveau": "Level",
    "Mots importants": "Important words", "Mots utiles": "Useful words", "Mots à éviter": "Words to avoid",
    "Score minimum": "Minimum score",
    "Aucun": "None",
    "Modifier": "Edit", "Supprimer": "Delete", "Annuler": "Cancel", "Enregistrer": "Save", "Fermer": "Close",
    "Supprimer cette recherche ?": "Delete this search?",
    "Ses offres déjà vues et ses alertes sont oubliées. Le suivi des candidatures reste.":
      "Its seen offers and alerts are forgotten. Application tracking is kept.",
    "Recherche supprimée": "Search deleted",
    "Offre masquée": "Offer hidden",
    "Déjà dans vos contacts": "Already in your contacts",
    "Entreprise ajoutée aux contacts": "Company added to contacts",
    "Ajoutée au suivi": "Added to tracking",
    "Message copié, candidature ajoutée au suivi": "Message copied, application added to tracking",
    "Message de candidature": "Application message",
    "À adapter, puis copié pour le coller sur le site de l'offre.": "Adapt it, then copy it to paste on the offer's site.",
    "Utiliser un modèle": "Use a template",
    "Copier le message": "Copy message",
    "votre entreprise": "your company",
    "Bonjour,\n\nVotre offre « {poste} » chez {entreprise}, vue sur {source}, a retenu toute mon attention : elle correspond à mon expérience.\n\nJe serais ravi(e) d'échanger avec vous sur vos besoins et de vous présenter mes réalisations.\n\nBien cordialement,\n\nOffre : {lien}":
      "Hello,\n\nYour offer “{poste}” at {entreprise}, seen on {source}, caught my attention: it matches my experience.\n\nI would be glad to discuss your needs and show you my previous work.\n\nBest regards,\n\nOffer: {lien}",
    // Recherche
    "Nom de la recherche": "Search name",
    "ex. Missions React": "e.g. React gigs",
    "Types de contrat": "Contract types",
    "Zones d'où vous pouvez postuler": "Zones you can apply from",
    "Salaire minimum": "Minimum salary",
    "Facultatif": "Optional",
    "Devise": "Currency", "Période": "Period",
    "Comparé seulement aux offres qui donnent un montant dans la même devise.":
      "Only compared with offers that give an amount in the same currency.",
    "Garder aussi les offres sans salaire comparable": "Also keep offers without a comparable salary",
    "Mots importants (+5)": "Important words (+5)",
    "Mots utiles (+2)": "Useful words (+2)",
    "Mots à éviter (−5)": "Words to avoid (−5)",
    "Séparés par des virgules. Cherchés dans le titre, les étiquettes et les technologies.":
      "Comma-separated. Searched in the title, tags and technologies.",
    "Cherchés dans le titre seulement.": "Searched in the title only.",
    "ex. react, odoo, python": "e.g. react, odoo, python",
    "ex. senior, lead, manager": "e.g. senior, lead, manager",
    "Domaine choisi +3, mot important +5, mot utile +2, à éviter −5 ; freelance +2 et contrat +1 si l'offre est déjà pertinente.":
      "Chosen field +3, important word +5, useful word +2, to avoid −5; freelance +2 and contract +1 if the offer is already relevant.",
    "Une offre doit correspondre à un domaine choisi ou à un mot important.":
      "An offer must match a chosen field or an important word.",
    "Recherche enregistrée": "Search saved",
    // Domaines, types, zones, niveaux, périodes
    "Développement": "Development", "Data et IA": "Data and AI", "Design": "Design", "Marketing": "Marketing",
    "Rédaction et traduction": "Writing and translation", "Support client": "Customer support",
    "Assistanat et administration": "Assistance and administration",
    "Finance et gestion de projet": "Finance and project management", "Ventes": "Sales", "Autres": "Others",
    "Freelance / mission": "Freelance / gig", "Contrat": "Contract", "Temps plein": "Full-time",
    "Temps partiel": "Part-time", "Stage": "Internship",
    "Monde entier": "Worldwide", "Afrique": "Africa", "Europe": "Europe", "Amérique": "Americas",
    "Asie et Océanie": "Asia and Oceania", "Autres pays": "Other countries",
    "Débutant (2 ans au plus)": "Junior (2 years at most)", "Confirmé (5 ans au plus)": "Intermediate (5 years at most)",
    "Senior (sans limite)": "Senior (no limit)",
    "par an": "per year", "par mois": "per month", "par jour": "per day", "par heure": "per hour",
    "/an": "/yr", "/mois": "/mo", "/jour": "/day", "/sem.": "/wk",
    // Suivi
    "À voir": "To review", "Postulé": "Applied", "Entretien": "Interview", "Refus": "Rejected", "Retenu": "Hired",
    "Statut": "Status", "Date": "Date", "Relancer le": "Follow up on", "Note": "Note",
    "Entreprise": "Company", "Lien de l'offre": "Offer link",
    "Ajouter une candidature": "Add an application",
    "Modifier la candidature": "Edit application",
    "Aucune candidature suivie.": "No application tracked.",
    "Depuis une offre : « Postuler » ou « Suivre ». Ou ajoutez une candidature trouvée ailleurs.":
      "From an offer: “Apply” or “Track”. Or add an application found elsewhere.",
    "Candidature enregistrée": "Application saved",
    "Supprimer cette candidature ?": "Delete this application?",
    "Elle disparaît du suivi. La tâche de relance éventuelle reste dans Tâches.":
      "It is removed from tracking. Any follow-up task stays in Tasks.",
    "Candidature supprimée": "Application deleted",
    "Tâche de relance créée": "Follow-up task created",
    "Une tâche est créée dans Tâches à cette date.": "A task is created in Tasks on that date.",
    "Saisie à la main": "Added manually",
    // Sources
    "Sources des offres": "Offer sources",
    "Offres publiques de ces sites, collectées au plus deux fois par jour. Seuls le titre, l'entreprise, le lieu, le salaire et quelques indices sont gardés, jamais la description. Le lien d'origine est ouvert tel quel.":
      "Public offers from these sites, collected at most twice a day. Only the title, company, location, salary and a few hints are kept, never the description. The original link is opened as is.",
    "Jamais collectée": "Never collected",
    "En erreur": "Failed",
    "Offres déjà à jour : une collecte au plus toutes les 12 heures par source.":
      "Offers already up to date: at most one collection every 12 hours per source.",
    "Source désactivée": "Source disabled", "Source activée": "Source enabled",
    "réponse illisible": "unreadable response", "pas de réponse": "no response",
    "réponse inattendue": "unexpected response", "flux RSS illisible": "unreadable RSS feed",
    // Premier écran
    "Créer votre première recherche": "Create your first search",
    "Missions rassemble les offres freelance et télétravail de cinq sites publics et les classe selon ce que vous cherchez. Partez d'un modèle : tout reste modifiable.":
      "Missions gathers freelance and remote offers from five public sites and ranks them by what you are looking for. Start from a template: everything can be changed.",
    "Conseillé": "Suggested",
    "Développeur": "Developer", "Assistant(e) virtuel(le)": "Virtual assistant",
    "Assistant(e) de direction": "Executive assistant", "Freelance : choisir le domaine": "Freelance: choose the field",
    "Recherche vide": "Blank search",
    "Développement · freelance et contrat": "Development · freelance and contract",
    "Support client et assistanat · freelance et temps partiel": "Customer support and assistance · freelance and part-time",
    "Assistanat et administration · tous les contrats": "Assistance and administration · all contracts",
    "Missions freelance et contrats, dans le domaine de votre choix": "Freelance gigs and contracts, in the field of your choice",
    "Tout est à choisir": "Everything to choose",
    "Assistanat virtuel": "Virtual assistance", "Assistanat de direction": "Executive assistance",
    "Missions freelance": "Freelance gigs",
    "Importer un profil (JSON)": "Import a profile (JSON)",
    "Fichier profil.json : mots-clés et poids, zones, types de contrat, expérience.":
      "profile.json file: weighted keywords, zones, contract types, experience.",
    "Mon profil": "My profile",
    // Accueil, palette
    "Actualiser les missions": "Refresh missions",
    // Messages du serveur
    "Indiquez un nom pour la recherche.": "Enter a name for the search.",
    "Devise invalide (code à trois lettres, ex. EUR).": "Invalid currency (three-letter code, e.g. EUR).",
    "Niveau inconnu.": "Unknown level.", "Période inconnue.": "Unknown period.",
    "Choisissez au moins un domaine ou un mot-clé important.": "Choose at least one field or one important keyword.",
    "Choisissez au moins un type de contrat.": "Choose at least one contract type.",
    "Choisissez au moins une zone.": "Choose at least one zone.",
    "Recherche introuvable.": "Search not found.", "Recherche invalide.": "Invalid search.",
    "Ce fichier n'est pas un profil de recherche.": "This file is not a search profile.",
    "Fichier introuvable.": "File not found.", "Fichier trop gros pour un profil.": "File too large for a profile.",
    "Ce fichier n'est pas un profil JSON valide.": "This file is not a valid JSON profile.",
    "Ce profil n'a aucun mot-clé important (poids 4 ou plus).": "This profile has no important keyword (weight 4 or more).",
    "Offre introuvable.": "Offer not found.", "Site inconnu.": "Unknown site.", "Source inconnue.": "Unknown source.",
    "Gardez au moins une source active.": "Keep at least one source enabled.",
    "Candidature invalide.": "Invalid application.", "Statut inconnu.": "Unknown status.",
    "Indiquez le poste.": "Enter the position.", "Lien invalide : il doit commencer par https://": "Invalid link: it must start with https://",
    "Candidature introuvable.": "Application not found.", "Date invalide.": "Invalid date.",
    "Date de relance invalide.": "Invalid follow-up date.",
    "Salaire minimum invalide.": "Invalid minimum salary.", "Score minimum invalide.": "Invalid minimum score.",
  });
  I18N.ajouter({
    "Il y a {n} jours": "{n} days ago",
    "Mis à jour il y a {n} min": "Updated {n} min ago",
    "Mis à jour il y a {n} h": "Updated {n} h ago",
    "{n} offres": "{n} offers",
    "{n} source en erreur": "{n} source failed",
    "{n} sources en erreur": "{n} sources failed",
    "{n} ans et plus": "{n}+ years",
    "Afficher les {n} autres": "Show the other {n}",
    "Réafficher les {n} offres masquées": "Show the {n} hidden offers again",
    "{n} offres réaffichées": "{n} offers shown again",
    "{n} nouvelle": "{n} new", "{n} nouvelles": "{n} new",
    "{n} sources mises à jour": "{n} sources updated",
    "Sans réponse : {noms}": "No response: {noms}",
    "Dernière collecte : {quand} · {n} offres": "Last collection: {quand} · {n} offers",
    "Recherche « {nom} » enregistrée": "Search “{nom}” saved",
    "Missions : {nom}": "Missions: {nom}",
    "Relancer : {poste}": "Follow up: {poste}",
    "Le {date}": "On {date}",
    "Dans le suivi : {statut}": "Tracked: {statut}",
    "Moins de {n} ans": "Under {n} years",
  });
  I18N.motifs([
    [/^Salaire minimum : de (\d+) à (\d+)\.$/, "Minimum salary: $1 to $2."],
    [/^Score minimum : de (-?\d+) à (\d+)\.$/, "Minimum score: $1 to $2."],
    [/^(\d+) recherches au plus\.$/, "$1 searches at most."],
    [/^(\d+) candidatures au plus\.$/, "$1 applications at most."],
  ]);

  const DOMAINES = {
    dev: "Développement", data: "Data et IA", design: "Design", marketing: "Marketing",
    redaction: "Rédaction et traduction", support: "Support client", assistanat: "Assistanat et administration",
    finance: "Finance et gestion de projet", ventes: "Ventes",
  };
  const TYPES = { freelance: "Freelance / mission", contrat: "Contrat", temps_plein: "Temps plein", temps_partiel: "Temps partiel", stage: "Stage" };
  const TYPES_DEFAUT = ["freelance", "contrat", "temps_plein", "temps_partiel"];
  const ZONES = { monde: "Monde entier", afrique: "Afrique", europe: "Europe", amerique: "Amérique", asie: "Asie et Océanie", autre: "Autres pays", inconnue: "Non précisée" };
  const NIVEAUX = { debutant: "Débutant (2 ans au plus)", confirme: "Confirmé (5 ans au plus)", senior: "Senior (sans limite)" };
  const PERIODES = { an: "par an", mois: "par mois", jour: "par jour", heure: "par heure" };
  const PERIODES_COURT = { an: "/an", mois: "/mois", jour: "/jour", heure: "/h", semaine: "/sem." };
  const STATUTS = {
    a_voir: ["À voir", "gris", "eye"], postule: ["Postulé", "bleu", "send"], entretien: ["Entretien", "ambre", "users"],
    retenu: ["Retenu", "vert", "circle-check"], refuse: ["Refus", "rouge", "circle-x"],
  };
  const MODELES = {
    developpeur: ["Développeur", "Développement · freelance et contrat", "code"],
    assistant_virtuel: ["Assistant(e) virtuel(le)", "Support client et assistanat · freelance et temps partiel", "headset"],
    assistant_direction: ["Assistant(e) de direction", "Assistanat et administration · tous les contrats", "calendar-check"],
    freelance: ["Freelance : choisir le domaine", "Missions freelance et contrats, dans le domaine de votre choix", "briefcase"],
    personnalise: ["Recherche vide", "Tout est à choisir", "file"],
  };
  const DEVISES = ["USD", "EUR", "GBP", "CAD", "AUD", "CHF", "MGA", "XOF", "MAD"];
  const MESSAGE = "Bonjour,\n\nVotre offre « {poste} » chez {entreprise}, vue sur {source}, a retenu toute mon attention : elle correspond à mon expérience.\n\nJe serais ravi(e) d'échanger avec vous sur vos besoins et de vous présenter mes réalisations.\n\nBien cordialement,\n\nOffre : {lien}";
  const DEJA_VUES_PAR_PAGE = 40;
  // r : réponse de /liste ; vue : "r:<id>" ou "suivi" ; offres : {id de recherche: réponse de /offres}.
  const M = { r: null, vue: null, offres: {}, ouverts: new Set(), plus: {}, collecte: false };

  const style = document.createElement("style");
  style.textContent = `
    .mi-onglets { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin: 0 0 14px; }
    .mi-onglets .espace { flex: 1; }
    .mi-compte { font-size: 11px; font-weight: 600; min-width: 18px; height: 18px; padding: 0 5px; border-radius: 9px; background: var(--violet-clair); color: var(--violet); display: inline-grid; place-items: center; font-variant-numeric: tabular-nums; }
    .mi-compte.neutre { background: transparent; color: var(--gris); border: 1px solid var(--ligne); }
    .mi-etat { font-size: 12.5px; color: var(--gris); display: inline-flex; gap: 8px; align-items: center; flex-wrap: wrap; }
    .mi-etat button { border: 0; background: none; padding: 0; font: inherit; cursor: pointer; }
    .mi-corps { display: grid; grid-template-columns: minmax(0, 1fr) 280px; gap: 18px; align-items: start; }
    @media (max-width: 1050px) { .mi-corps { grid-template-columns: 1fr; } }
    .mi-liste .ligne { cursor: pointer; }
    .mi-liste .titre-lignes, .mi-suivi .titre-lignes { display: flex; justify-content: space-between; }
    .mi-score { font-size: 12px; font-weight: 600; color: var(--encre); border: 1px solid var(--ligne); background: var(--carte); font-variant-numeric: tabular-nums; }
    .ligne:hover .mi-score, .ligne.ouverte .mi-score { background: var(--carte); }
    .mi-raisons { display: flex; gap: 4px; }
    .mi-raisons .tag { max-width: 110px; overflow: hidden; text-overflow: ellipsis; }
    @media (max-width: 1250px) { .mi-raisons { display: none; } }
    .mi-date { min-width: 78px; text-align: right; font-variant-numeric: tabular-nums; }
    .mi-liste .ligne-actions, .mi-suivi .ligne-actions { justify-content: flex-end; }
    .mi-detail { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 10px 22px; font-size: 13px; }
    .mi-detail .lib { font-size: 11.5px; color: var(--gris); margin-bottom: 1px; }
    .mi-detail .val { color: var(--encre); overflow-wrap: anywhere; }
    .mi-detail .large { grid-column: 1 / -1; }
    .mi-detail .note { white-space: pre-wrap; color: var(--doux); }
    .mi-boutons { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 12px; }
    .mi-plus { display: block; width: 100%; border: 0; border-top: 1px solid var(--ligne); background: var(--carte); color: var(--doux); padding: 9px; cursor: pointer; font: inherit; font-size: 12.5px; }
    .mi-plus:hover { background: var(--surface); color: var(--encre); }
    .mi-cote { display: flex; flex-direction: column; gap: 12px; }
    .mi-cote h3 { margin: 0 0 8px; font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 6px; }
    .mi-cote h3 .espace { flex: 1; }
    .mi-critere { display: grid; grid-template-columns: 96px minmax(0, 1fr); gap: 8px; font-size: 12.5px; padding: 5px 0; border-top: 1px solid var(--ligne); }
    .mi-critere .lib { color: var(--gris); }
    .mi-critere .val { color: var(--encre); overflow-wrap: anywhere; }
    .mi-liens { display: flex; flex-wrap: wrap; gap: 6px; }
    .mi-aide { color: var(--gris); font-size: 12px; margin: 0 0 10px; line-height: 1.45; }
    .mi-lien-discret { border: 0; background: none; padding: 0; color: var(--doux); font: inherit; font-size: 12.5px; cursor: pointer; text-decoration: underline; text-underline-offset: 2px; text-align: left; }
    .mi-lien-discret:hover { color: var(--encre); }
    .mi-groupe { margin: 0 0 14px; }
    .mi-groupe > .lib { font-size: 12.5px; font-weight: 500; color: var(--doux); margin-bottom: 6px; }
    .mi-groupe > small { display: block; color: var(--gris); font-size: 12px; margin-top: 5px; }
    .mi-cases { display: flex; flex-wrap: wrap; gap: 6px; }
    .mi-case { display: inline-flex; align-items: center; gap: 6px; font-size: 13px; padding: 4px 9px; border: 1px solid var(--ligne); border-radius: 6px; cursor: pointer; color: var(--doux); background: var(--carte); user-select: none; }
    .mi-case:has(input:checked) { border-color: var(--violet); color: var(--encre); background: var(--violet-clair); }
    .mi-case input { margin: 0; width: 14px; height: 14px; accent-color: var(--violet); }
    .mi-grille { display: grid; grid-template-columns: 1fr 1fr; gap: 0 14px; }
    .mi-grille .large { grid-column: 1 / -1; }
    .mi-salaire { display: grid; grid-template-columns: minmax(0, 1fr) 84px minmax(0, 1fr); gap: 0 8px; }
    .mi-coche { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--encre); cursor: pointer; margin: -4px 0 14px; }
    .mi-coche input { width: 15px; height: 15px; margin: 0; accent-color: var(--violet); }
    .etat-txt.bleu { color: var(--bleu-texte); }
    .mi-relance { display: inline-flex; align-items: center; gap: 4px; font-variant-numeric: tabular-nums; }
    .mi-relance.due { color: var(--ambre-texte); }
    .mi-premier { max-width: 760px; }
    .mi-premier h3 { margin: 0 0 4px; font-size: 16px; font-weight: 600; }
    .mi-premier .lignes { margin: 14px 0; }
    .mi-import { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
    .mi-import small { color: var(--gris); font-size: 12px; }
    .mi-message { width: 100%; min-height: 230px; font: inherit; font-size: 13.5px; line-height: 1.5; resize: vertical; }
    .mi-sources .ligne { cursor: default; }
    .mi-sources input[type=checkbox] { width: 16px; height: 16px; margin: 0; accent-color: var(--violet); }
    .mi-carte .ligne-jour .heure { min-width: 26px; }
    .mi-carte .ligne-jour .nom { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .mi-carte .total { margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--ligne); font-size: 12.5px; color: var(--doux); }
  `;
  document.head.append(style);

  // --------------------------------------------------------------- outils
  const racine = () => $("#vue-missions");
  const brut = s => document.createTextNode(s == null ? "" : String(s));
  const actif = nom => typeof appActive === "function" && appActive(nom) && !!VUES[nom];
  const stop = f => ev => { ev.stopPropagation(); f(); };
  const sansAccents = s => String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().trim();
  const nomSource = id => (M.r?.sources || []).find(s => s.id === id)?.nom || (id === "manuel" ? t("Saisie à la main") : id);
  const rechercheCourante = () => (M.vue || "").startsWith("r:") ? (M.r?.recherches || []).find(x => "r: " + x.id === M.vue) : null;

  function jour(iso) { return new Date(String(iso).slice(0, 10) + "T00:00"); }
  function dateCourte(iso) {
    if (!iso) return "";
    const d = jour(iso), opts = { day: "numeric", month: "short" };
    if (d.getFullYear() !== new Date().getFullYear()) opts.year = "numeric";
    return d.toLocaleDateString(I18N.locale(), opts);
  }
  function dateLongue(iso) { return iso ? jour(iso).toLocaleDateString(I18N.locale(), { day: "numeric", month: "long", year: "numeric" }) : ""; }
  /** « Aujourd'hui », « Hier », « Il y a 3 jours » (par rapport au jour du serveur). */
  function ilYa(iso) {
    if (!iso) return "";
    const n = Math.round((jour(M.r?.aujourdhui || new Date().toISOString()) - jour(iso)) / 864e5);
    if (n <= 0) return t("Aujourd'hui");
    if (n === 1) return t("Hier");
    return t("Il y a {n} jours", { n });
  }
  function depuis(isoHeure) {
    const min = Math.max(0, Math.round((new Date(M.r.maintenant) - new Date(isoHeure)) / 60000));
    if (min < 1) return t("Mis à jour à l'instant");
    if (min < 60) return t("Mis à jour il y a {n} min", { n: min });
    if (min < 48 * 60) return t("Mis à jour il y a {n} h", { n: Math.round(min / 60) });
    return t("Mis à jour le {date}", { date: dateCourte(isoHeure) });
  }
  function quand(isoHeure) {
    const d = new Date(isoHeure);
    return d.toLocaleDateString(I18N.locale(), { day: "numeric", month: "short" }) + d.toLocaleTimeString(I18N.locale(), { hour: "2-digit", minute: "2-digit" });
  }
  function salaireTexte(x) {
    const s = x.salaire;
    if (!s) return x.salaire_texte || "";
    const k = n => n >= 1000 ? (n % 1000 ? (n / 1000).toFixed(1).replace(/\.0$/, "") : String(n / 1000)) + "k" : String(n);
    const montant = s.min && s.max && k(s.min) !== k(s.max) ? k(s.min) + "– " + k(s.max) : k(s.min || s.max);
    return montant + s.devise + (s.periode ? " " + t(PERIODES_COURT[s.periode] || "") : "");
  }
  const zonesTexte = x => (x.zones || []).map(z => t(ZONES[z] || z)).join(", ");

  // -------------------------------------------------------------- données
  async function charger() {
    M.r = await api("/api/missions/liste", {});
    dessiner();
  }
  const recharger = () => charger().catch(e => toast(e.message, "erreur"));

  async function afficher() {
    try { M.r = await api("/api/missions/liste", {}); }
    catch (e) { toast(e.message, "erreur"); return; }
    M.offres = {};
    dessiner();
    if (M.r.a_collecter && M.r.recherches.length && !M.collecte) actualiser(true);
  }

  async function actualiser(auto = false) {
    if (M.collecte) return;
    M.collecte = true;
    majEtat();
    try {
      const r = await api("/api/missions/actualiser", {});
      M.r = r;
      M.offres = {};
      const erreurs = Object.keys(r.erreurs || {});
      if (erreurs.length) toast(t("Sans réponse : {noms}", { noms: erreurs.map(nomSource).join(", ") }), "erreur", 5000);
      else if (r.collectees.length) { if (!auto) toast(t("{n} sources mises à jour", { n: r.collectees.length }), "succes", 2200); }
      else if (!auto) toast("Offres déjà à jour : une collecte au plus toutes les 12 heures par source.", "", 4500);
    } catch (e) { toast(e.message, "erreur"); }
    M.collecte = false;
    if (S.vue === "missions") dessiner();
  }

  // -------------------------------------------------------------- dessin
  function dessiner() {
    const vue = racine();
    if (!vue || !M.r) return;
    const r = M.r;
    if (!r.recherches.length && M.vue !== "suivi") { premierEcran(); return; }
    if (M.vue !== "suivi" && !rechercheCourante()) M.vue = "r:" + r.recherches[0].id;
    vue.replaceChildren(
      el("div", { class: "barre-vue" },
        el("h2", {}, icone("briefcase"), "Missions"),
        el("div", { class: "espace" }),
        el("button", { class: "btn", onclick: () => actualiser(false), disabled: M.collecte ? "" : null }, icone("refresh-cw"), "Actualiser"),
        el("button", { class: "btn", onclick: reglerSources }, icone("settings"), "Sources"),
        el("button", { class: "btn principal", onclick: () => editer(null) }, icone("plus"), "Nouvelle recherche")),
      el("div", { class: "mi-onglets" },
        el("div", { class: "puces" },
          r.recherches.map(x => el("button", { class: "puce " + (M.vue === "r:" + x.id ? " actif" : ""), onclick: () => choisir("r: " + x.id) },
            brut(x.nom), x.nouvelles ? el("span", { class: "mi-compte", id: "mi-n- " + x.id }, String(x.nouvelles)) : null)),
          el("button", { class: "puce " + (M.vue === "suivi" ? " actif" : ""), onclick: () => choisir("suivi") },
            icone("list-checks"), "Candidatures", r.suivi.length ? el("span", { class: "mi-compte neutre" }, String(r.suivi.length)) : null)),
        el("div", { class: "espace" }),
        el("div", { class: "mi-etat", id: "mi-etat" })),
      el("div", { id: "mi-zone" }));
    majEtat();
    if (M.vue === "suivi") dessinerSuivi();
    else dessinerRecherche(rechercheCourante());
  }

  function choisir(vue) {
    M.vue = vue;
    dessiner();
  }

  /** L'état de la collecte, en haut à droite. */
  function majEtat() {
    const zone = $("#mi-etat");
    if (!zone || !M.r) return;
    if (M.collecte) { zone.replaceChildren(el("span", {}, icone("loader-circle"), "Collecte en cours…")); return; }
    const sources = M.r.sources.filter(s => s.active);
    const dates = sources.map(s => s.derniere).filter(Boolean).sort();
    const erreurs = sources.filter(s => s.ok === false);
    zone.replaceChildren(
      el("span", {}, dates.length ? depuis(dates[dates.length - 1]) : t("Jamais collectées")),
      el("span", {}, "·"),
      el("span", {}, t("{n} offres", { n: M.r.nombre_offres })),
      erreurs.length ? el("button", { class: "etat-txt rouge", onclick: reglerSources },
        t(erreurs.length > 1 ? "{n} sources en erreur" : "{n} source en erreur", { n: erreurs.length })) : null);
  }

  // ------------------------------------------------------ une recherche
  function dessinerRecherche(rech) {
    const zone = $("#mi-zone");
    zone.replaceChildren(el("div", { class: "mi-corps" },
      el("div", { id: "mi-liste", class: "mi-liste" }, el("div", { class: "vide" }, icone("loader-circle"), "Chargement…")),
      panneau(rech)));
    const deja = M.offres[rech.id];
    if (deja) dessinerListe(rech);
    else chargerOffres(rech);
  }

  async function chargerOffres(rech) {
    let o;
    try { o = await api("/api/missions/offres", { recherche_id: rech.id }); }
    catch (e) { toast(e.message, "erreur"); return; }
    M.offres[rech.id] = o;
    if (M.vue === "r: " + rech.id) dessinerListe(rech);
    // Les offres montrées passeront dans « Déjà vues » à la prochaine ouverture.
    const nouvelles = o.offres.filter(x => x.nouvelle).map(x => x.id);
    if (nouvelles.length) {
      api("/api/missions/voir", { recherche_id: rech.id, ids: nouvelles }).then(() => {
        rech.nouvelles = 0;
        $("#mi-n- " + rech.id)?.remove();
      }).catch(() => {});
    }
  }

  function dessinerListe(rech) {
    const zone = $("#mi-liste");
    const o = M.offres[rech.id];
    if (!zone || !o) return;
    if (!o.offres.length) {
      zone.replaceChildren(el("div", { class: "vide" }, icone("search"),
        el("div", { style: "font-weight:500;color:var(--encre)" }, "Aucune offre pour cette recherche."),
        el("div", { style: "margin-top:4px" }, M.r.nombre_offres
          ? "Élargissez les domaines, les types ou les zones, ou baissez le score minimum."
          : "Cliquez sur « Actualiser » pour collecter les offres.")));
      return;
    }
    const nouvelles = o.offres.filter(x => x.nouvelle), vues = o.offres.filter(x => !x.nouvelle);
    const limite = M.plus[rech.id] || DEJA_VUES_PAR_PAGE;
    zone.replaceChildren(
      nouvelles.length ? el("div", { class: "lignes" },
        el("div", { class: "titre-lignes" }, el("span", {}, "Nouvelles"), el("span", {}, String(nouvelles.length))),
        nouvelles.map(ligne)) : null,
      vues.length ? el("div", { class: "lignes" },
        el("div", { class: "titre-lignes" }, el("span", {}, "Déjà vues"), el("span", {}, String(vues.length))),
        vues.slice(0, limite).map(ligne),
        vues.length > limite ? el("button", { class: "mi-plus", onclick: () => { M.plus[rech.id] = limite + 60; dessinerListe(rech); } },
          t("Afficher les {n} autres", { n: vues.length - limite })) : null) : null);
  }

  function ligne(x) {
    const ouverte = M.ouverts.has(x.id);
    const meta = [x.entreprise, zonesTexte(x), salaireTexte(x), nomSource(x.source)].filter(Boolean).join(" · ");
    const st = x.suivi ? STATUTS[x.suivi] : null;
    const corps = el("div", { class: "ligne " + (ouverte ? " ouverte" : ""),
      onclick: () => { ouverte ? M.ouverts.delete(x.id) : M.ouverts.add(x.id); dessinerListe(rechercheCourante()); } },
      el("span", { class: "ligne-ic mi-score", title: "Score" }, String(x.score)),
      el("div", { class: "ligne-corps" },
        el("div", { class: "ligne-titre" }, el("span", { class: "sans-icone" }, brut(x.titre)), el("span", { class: "tag" }, TYPES[x.type] || x.type)),
        el("div", { class: "ligne-meta sans-icone" }, brut(meta))),
      el("div", { class: "ligne-cote" },
        x.raisons.length ? el("span", { class: "mi-raisons" }, x.raisons.slice(0, 3).map(m => el("span", { class: "tag", title: "Mots trouvés" }, brut(m)))) : null,
        st ? el("span", { class: "etat-txt " + st[1] }, st[0]) : null,
        el("span", { class: "mi-date", title: dateLongue(x.date) }, ilYa(x.date))),
      el("div", { class: "ligne-actions" },
        el("button", { class: "icone-btn", title: "Ouvrir l'offre", onclick: stop(() => ouvrirOffre(x)) }, icone("external-link")),
        el("button", { class: "icone-btn", title: "Masquer", onclick: stop(() => masquer(x)) }, icone("eye-off"))));
    return ouverte ? [corps, detail(x)] : corps;
  }

  function detail(x) {
    const champ = (lib, val, classe = "") => val ? el("div", { class: classe }, el("div", { class: "lib" }, lib),
      el("div", { class: "val sans-icone" }, typeof val === "string" ? brut(val) : val)) : null;
    const st = x.suivi ? STATUTS[x.suivi] : null;
    return el("div", { class: "ligne-detail" },
      el("div", { class: "mi-detail" },
        champ("Localisation", x.lieu || zonesTexte(x)),
        champ("Domaine", DOMAINES[x.categorie] ? t(DOMAINES[x.categorie]) : t("Autres")),
        champ("Technologies", (x.techs || []).join(", ")),
        champ("Expérience demandée", x.experience ? t("{n} ans et plus", { n: x.experience }) : t("Non précisée")),
        champ("Salaire", salaireTexte(x)),
        champ("Mots trouvés", x.raisons.join(", ")),
        champ("Mots à éviter trouvés", (x.evites || []).join(", ")),
        champ("Publiée le", dateLongue(x.date)),
        champ("Expire le", dateLongue(x.expire)),
        champ("Source", nomSource(x.source))),
      el("div", { class: "mi-boutons" },
        el("button", { class: "btn petit principal", onclick: () => ouvrirOffre(x) }, icone("external-link"), "Ouvrir l'offre"),
        el("button", { class: "btn petit", onclick: () => postuler(x) }, icone("send"), "Postuler"),
        st ? el("button", { class: "btn petit", onclick: () => { M.vue = "suivi"; dessiner(); } }, icone("list-checks"), t("Dans le suivi : {statut}", { statut: t(st[0]) }))
          : el("button", { class: "btn petit", onclick: () => suivre(x, "a_voir") }, icone("list-checks"), "Suivre"),
        actif("contacts") && x.entreprise ? el("button", { class: "btn petit", onclick: () => ajouterContact(x) }, icone("user-plus"), "Ajouter l'entreprise aux contacts") : null,
        el("button", { class: "btn petit discret", onclick: () => masquer(x) }, icone("eye-off"), "Masquer")));
  }

  /** Le panneau de droite : critères, recherche manuelle, offres masquées. */
  function panneau(rech) {
    const critere = (lib, val) => el("div", { class: "mi-critere" }, el("span", { class: "lib" }, lib), el("span", { class: "val sans-icone" }, brut(val || t("Aucun"))));
    const liste = (dico, ids) => ids.map(v => t(dico[v] || v)).join(", ");
    const salaire = rech.salaire_min ? rech.salaire_min.toLocaleString(I18N.locale()) + rech.devise + " " + t(PERIODES[rech.periode] || "") : "";
    const o = M.offres[rech.id];
    return el("aside", { class: "mi-cote" },
      el("div", { class: "carte" },
        el("h3", {}, "Critères", el("span", { class: "espace" }),
          el("button", { class: "icone-btn", title: "Modifier", onclick: () => editer(rech) }, icone("pencil")),
          el("button", { class: "icone-btn danger", title: "Supprimer", onclick: () => supprimerRecherche(rech) }, icone("trash-2"))),
        critere("Domaines", liste(DOMAINES, rech.domaines)),
        critere("Types", liste(TYPES, rech.types)),
        critere("Zones", liste(ZONES, rech.zones)),
        critere("Niveau", t(NIVEAUX[rech.niveau])),
        rech.salaire_min ? critere("Salaire minimum", salaire) : null,
        critere("Mots importants", rech.importants.join(", ")),
        rech.utiles.length ? critere("Mots utiles", rech.utiles.join(", ")) : null,
        rech.eviter.length ? critere("Mots à éviter", rech.eviter.join(", ")) : null,
        critere("Score minimum", String(rech.score_min))),
      el("div", { class: "carte" },
        el("h3", {}, "Chercher aussi sur"),
        el("p", { class: "mi-aide" }, "Ces sites n'ont pas d'accès public : la recherche s'ouvre dans le navigateur avec vos mots-clés."),
        el("div", { class: "mi-liens" }, (o?.liens || liensParDefaut()).map(l =>
          el("button", { class: "btn petit", onclick: () => ouvrirManuel(rech, l.site) }, icone("external-link"), brut(l.nom))))),
      M.r.masquees ? el("button", { class: "mi-lien-discret", onclick: demasquer }, t("Réafficher les {n} offres masquées", { n: M.r.masquees })) : null);
  }
  const liensParDefaut = () => [["malt", "Malt"], ["codeur", "Codeur.com"], ["comeup", "ComeUp"], ["upwork", "Upwork"],
    ["linkedin", "LinkedIn"], ["indeed", "Indeed"]].map(([site, nom]) => ({ site, nom }));

  // ------------------------------------------------------------ actions
  async function ouvrirOffre(x) {
    try { await api("/api/missions/ouvrir", { id: x.id }); }
    catch (e) { toast(e.message, "erreur"); }
  }
  async function ouvrirManuel(rech, site) {
    try { await api("/api/missions/ouvrir", { recherche_id: rech.id, site }); }
    catch (e) { toast(e.message, "erreur"); }
  }

  async function masquer(x) {
    try {
      await api("/api/missions/masquer", { id: x.id });
      for (const o of Object.values(M.offres)) o.offres = o.offres.filter(y => y.id !== x.id);
      M.r.masquees += 1;
      toast("Offre masquée", "", 1500);
      const rech = rechercheCourante();
      if (rech) { dessinerListe(rech); $(".mi-cote")?.replaceWith(panneau(rech)); }
    } catch (e) { toast(e.message, "erreur"); }
  }

  async function demasquer() {
    try {
      const r = await api("/api/missions/demasquer", {});
      toast(t("{n} offres réaffichées", { n: r.reaffichees }), "succes", 1800);
      M.offres = {};
      recharger();
    } catch (e) { toast(e.message, "erreur"); }
  }

  /** Ajoute l'offre au suivi (si elle n'y est pas déjà plus loin). */
  async function suivre(x, statut, silencieux = false) {
    if (x.suivi && (statut === "a_voir" || x.suivi !== "a_voir")) return;
    try {
      await api("/api/missions/suivi/enregistrer", { suivi: { id: x.id, statut, recherche_id: rechercheCourante()?.id || "" } });
      for (const o of Object.values(M.offres)) for (const y of o.offres) if (y.id === x.id) y.suivi = statut;
      if (!silencieux) toast("Ajoutée au suivi", "succes", 1500);
      const r = await api("/api/missions/liste", {});
      M.r = r;
      dessiner();
    } catch (e) { toast(e.message, "erreur"); }
  }

  /** Message de candidature : modèle de l'application Modèles si elle est
      active, sinon un texte par défaut ; copié, puis l'offre passe à « Postulé ». */
  function postuler(x, texteDepart = null) {
    const valeurs = { poste: x.titre, entreprise: x.entreprise || t("votre entreprise"), lien: x.url, source: nomSource(x.source) };
    const remplir = s => String(s || "").replace(/\{(poste|entreprise|lien|source)\}/g, (_, k) => valeurs[k]);
    const zone = el("textarea", { class: "mi-message", value: texteDepart ?? remplir(t(MESSAGE)) });
    const copierMessage = async () => {
      await copier(zone.value, "Message copié, candidature ajoutée au suivi");
      fermer();
      await suivre(x, "postule", true);
    };
    const modele = actif("modeles") && window.Modeles?.choisir
      ? el("button", { class: "btn", onclick: () => window.Modeles.choisir(f => postuler(x, remplir(f.texte))) }, icone("message-square-text"), "Utiliser un modèle")
      : null;
    fenetre([
      el("h3", {}, "Message de candidature"),
      el("p", { class: "mi-aide sans-icone" }, brut(x.titre + (x.entreprise ? "· " + x.entreprise : "") + "· " + nomSource(x.source))),
      el("p", { class: "mi-aide" }, "À adapter, puis copié pour le coller sur le site de l'offre."),
      zone,
      el("div", { class: "actions" },
        modele,
        el("div", { style: "flex:1" }),
        el("button", { class: "btn", onclick: fermer }, "Annuler"),
        el("button", { class: "btn", onclick: () => ouvrirOffre(x) }, icone("external-link"), "Ouvrir l'offre"),
        el("button", { class: "btn principal", onclick: copierMessage }, icone("copy"), "Copier le message"))]);
    $("#fenetre").style.width = "min(680px, 94vw)";
  }

  async function ajouterContact(x) {
    try {
      const r = await api("/api/contacts/liste", { recherche: x.entreprise });
      const cible = sansAccents(x.entreprise);
      if ((r.contacts || []).some(c => sansAccents(c.nom) === cible || sansAccents(c.entreprise) === cible)) { toast("Déjà dans vos contacts"); return; }
      await api("/api/contacts/enregistrer", { contact: { type: "entreprise", nom: x.entreprise, statut: "prospect", etiquettes: ["missions"] } });
      toast("Entreprise ajoutée aux contacts", "succes", 1800);
    } catch (e) { toast(e.message, "erreur"); }
  }

  async function supprimerRecherche(rech) {
    if (!(await confirmer(icone("trash-2"), "Supprimer cette recherche ?", "Ses offres déjà vues et ses alertes sont oubliées. Le suivi des candidatures reste.", "Supprimer"))) return;
    try {
      await api("/api/missions/recherche/supprimer", { id: rech.id });
      delete M.offres[rech.id];
      M.vue = null;
      toast("Recherche supprimée");
      recharger();
    } catch (e) { toast(e.message, "erreur"); }
  }

  // ------------------------------------------------- formulaire de recherche
  function cases(dico, choisis) {
    return el("div", { class: "mi-cases" }, Object.entries(dico).map(([v, lib]) =>
      el("label", { class: "mi-case" }, el("input", { type: "checkbox", value: v, checked: choisis.includes(v) ? "" : null }), el("span", {}, lib))));
  }
  const coches = bloc => [...bloc.querySelectorAll("input:checked")].map(i => i.value);

  function editer(x, modele = null) {
    const b = x ? { ...x } : {
      nom: modele?.nom ? t(modele.nom) : "", domaines: modele?.domaines || [], types: modele?.types || TYPES_DEFAUT,
      zones: ["monde"], niveau: "senior", salaire_min: "", devise: "USD", periode: "an", garder_sans_salaire: true,
      importants: [], utiles: [], eviter: [], score_min: 3 };
    const champ = (lib, entree, classe = "", aide = null) => el("label", { class: "champ " + classe }, lib, entree, aide ? el("small", {}, aide) : null);
    const groupe = (lib, contenu, aide = null) => el("div", { class: "mi-groupe large" }, el("div", { class: "lib" }, lib), contenu, aide ? el("small", {}, aide) : null);
    const nom = el("input", { value: b.nom, maxlength: 60, placeholder: "ex. Missions React" });
    const domaines = cases(DOMAINES, b.domaines), types = cases(TYPES, b.types), zones = cases(ZONES, b.zones);
    const niveau = el("select", {}, Object.entries(NIVEAUX).map(([v, lib]) => el("option", { value: v, selected: v === b.niveau ? "" : null }, lib)));
    const salaire = el("input", { type: "number", min: 0, step: 1, value: b.salaire_min || "", placeholder: "Facultatif" });
    const devise = el("input", { value: b.devise, maxlength: 3, list: "mi-devises", style: "text-transform:uppercase" });
    const periode = el("select", {}, Object.entries(PERIODES).map(([v, lib]) => el("option", { value: v, selected: v === b.periode ? "" : null }, lib)));
    const garder = el("input", { type: "checkbox", checked: b.garder_sans_salaire !== false ? "" : null });
    const mots = (liste, ph) => el("input", { value: (liste || []).join(", "), placeholder: ph });
    const importants = mots(b.importants, "ex. react, odoo, python"), utiles = mots(b.utiles, ""), eviter = mots(b.eviter, "ex. senior, lead, manager");
    const score = el("input", { type: "number", min: -20, max: 100, value: b.score_min ?? 3 });
    const valider = async () => {
      const recherche = { id: x?.id, nom: nom.value, domaines: coches(domaines), types: coches(types), zones: coches(zones),
        niveau: niveau.value, salaire_min: salaire.value, devise: devise.value, periode: periode.value,
        garder_sans_salaire: garder.checked, importants: importants.value, utiles: utiles.value, eviter: eviter.value,
        score_min: score.value };
      try {
        const r = await api("/api/missions/recherche/enregistrer", { recherche });
        fermer();
        toast(t("Recherche « {nom} » enregistrée", { nom: r.nom }), "succes", 1800);
        M.vue = "r:" + r.id;
        delete M.offres[r.id];
        await charger();
        if (M.r.a_collecter) actualiser(true);
      } catch (e) { toast(e.message, "erreur"); }
    };
    fenetre([
      el("h3", {}, x ? "Modifier la recherche" : "Nouvelle recherche"),
      el("div", { class: "mi-grille" },
        champ("Nom de la recherche", nom, "large"),
        groupe("Domaines", domaines, "Une offre doit correspondre à un domaine choisi ou à un mot important."),
        groupe("Types de contrat", types),
        groupe("Zones d'où vous pouvez postuler", zones),
        champ("Niveau", niveau),
        champ("Score minimum", score),
        el("div", { class: "large mi-salaire" }, champ("Salaire minimum", salaire), champ("Devise", devise), champ("Période", periode)),
        el("label", { class: "mi-coche large" }, garder, el("span", {}, "Garder aussi les offres sans salaire comparable")),
        el("small", { class: "large mi-aide", style: "margin-top:-8px" }, "Comparé seulement aux offres qui donnent un montant dans la même devise."),
        champ("Mots importants (+5)", importants, "large", "Séparés par des virgules. Cherchés dans le titre, les étiquettes et les technologies."),
        champ("Mots utiles (+2)", utiles),
        champ("Mots à éviter (−5)", eviter, "", "Cherchés dans le titre seulement."),
        el("p", { class: "large mi-aide" }, "Domaine choisi +3, mot important +5, mot utile +2, à éviter −5 ; freelance +2 et contrat +1 si l'offre est déjà pertinente.")),
      el("datalist", { id: "mi-devises" }, DEVISES.map(d => el("option", { value: d }))),
      el("div", { class: "actions" },
        el("button", { class: "btn", onclick: fermer }, "Annuler"),
        el("button", { class: "btn principal", onclick: valider }, "Enregistrer"))]);
    $("#fenetre").style.width = "min(760px, 94vw)";
    setTimeout(() => nom.focus(), 60);
  }

  // ------------------------------------------------------------- premier écran
  function premierEcran() {
    const r = M.r;
    const ordre = Object.keys(MODELES).sort((a, b) => (b === r.profil) - (a === r.profil));
    racine().replaceChildren(
      el("div", { class: "barre-vue" },
        el("h2", {}, icone("briefcase"), "Missions"),
        el("div", { class: "espace" }),
        el("button", { class: "btn", onclick: reglerSources }, icone("settings"), "Sources")),
      el("div", { class: "carte mi-premier" },
        el("h3", {}, "Créer votre première recherche"),
        el("p", { class: "mi-aide" }, "Missions rassemble les offres freelance et télétravail de cinq sites publics et les classe selon ce que vous cherchez. Partez d'un modèle : tout reste modifiable."),
        el("div", { class: "lignes" }, ordre.map(cle => {
          const [titre, texte, ic] = MODELES[cle];
          return el("div", { class: "ligne cliquable", onclick: () => editer(null, r.modeles[cle]) },
            el("span", { class: "ligne-ic" }, icone(ic)),
            el("div", { class: "ligne-corps" }, el("div", { class: "ligne-titre" }, el("span", {}, titre)), el("div", { class: "ligne-meta" }, texte)),
            el("div", { class: "ligne-cote" }, cle === r.profil ? el("span", { class: "tag" }, "Conseillé") : null, icone("chevron-right")));
        })),
        el("div", { class: "mi-import" },
          el("button", { class: "btn", onclick: importer }, icone("upload"), "Importer un profil (JSON)"),
          el("small", {}, "Fichier profil.json : mots-clés et poids, zones, types de contrat, expérience."))));
  }

  /** Lit un profil.json choisi dans la page (aucune fenêtre du système) et l'envoie au serveur. */
  function importer() {
    const entree = el("input", { type: "file", accept: ".json,application/json", style: "display:none" });
    entree.addEventListener("change", async () => {
      const f = entree.files[0];
      entree.remove();
      if (!f) return;
      if (f.size > 1e6) { toast("Fichier trop gros pour un profil.", "erreur"); return; }
      let profil;
      try { profil = JSON.parse(await f.text()); } catch { toast("Ce fichier n'est pas un profil JSON valide.", "erreur"); return; }
      try {
        const r = await api("/api/missions/importer_profil", { profil });
        toast(t("Recherche « {nom} » enregistrée", { nom: r.nom }), "succes", 2000);
        M.vue = "r:" + r.id;
        await charger();
        if (M.r.a_collecter) actualiser(true);
      } catch (e) { toast(e.message, "erreur"); }
    });
    document.body.append(entree);
    entree.click();
  }

  // ---------------------------------------------------------------- sources
  function reglerSources() {
    const lignes = M.r.sources.map(s => {
      const coche = el("input", { type: "checkbox", checked: s.active ? "" : null, onchange: async () => {
        try {
          await api("/api/missions/sources", { id: s.id, actif: coche.checked });
          toast(coche.checked ? "Source activée" : "Source désactivée", "", 1400);
          M.offres = {};
          M.r = await api("/api/missions/liste", {});
          reglerSources();
          if (M.r.recherches.length) dessiner();
        } catch (e) { coche.checked = !coche.checked; toast(e.message, "erreur"); }
      } });
      const etat = s.ok === false
        ? el("span", { class: "etat-txt rouge sans-icone" }, brut(t("En erreur") + ": " + t(s.erreur)))
        : el("span", {}, s.derniere ? t("Dernière collecte : {quand} · {n} offres", { quand: quand(s.derniere), n: s.nombre }) : t("Jamais collectée"));
      return el("label", { class: "ligne" },
        el("span", { class: "ligne-ic" }, coche),
        el("div", { class: "ligne-corps" },
          el("div", { class: "ligne-titre" }, el("span", {}, brut(s.nom)), el("span", { class: "tag" }, brut(s.url.replace(/^https:\/\//, "")))),
          el("div", { class: "ligne-meta" }, etat)));
    });
    fenetre([
      el("h3", {}, "Sources des offres"),
      el("p", { class: "mi-aide" }, "Offres publiques de ces sites, collectées au plus deux fois par jour. Seuls le titre, l'entreprise, le lieu, le salaire et quelques indices sont gardés, jamais la description. Le lien d'origine est ouvert tel quel."),
      el("div", { class: "lignes mi-sources" }, lignes),
      el("div", { class: "actions" }, el("button", { class: "btn principal", onclick: fermer }, "Fermer"))]);
    $("#fenetre").style.width = "min(600px, 94vw)";
  }

  // ------------------------------------------------------------------ suivi
  function dessinerSuivi() {
    const zone = $("#mi-zone");
    const tous = M.r.suivi;
    const ajouter = el("button", { class: "btn", onclick: () => editerSuivi(null) }, icone("plus"), "Ajouter une candidature");
    if (!tous.length) {
      zone.replaceChildren(el("div", { class: "vide" }, icone("list-checks"),
        el("div", { style: "font-weight:500;color:var(--encre)" }, "Aucune candidature suivie."),
        el("div", { style: "margin:4px 0 14px" }, "Depuis une offre : « Postuler » ou « Suivre ». Ou ajoutez une candidature trouvée ailleurs."),
        ajouter));
      return;
    }
    zone.replaceChildren(
      el("div", { class: "mi-suivi" }, Object.keys(STATUTS).map(statut => {
        const liste = tous.filter(s => s.statut === statut);
        if (!liste.length) return null;
        return el("div", { class: "lignes" },
          el("div", { class: "titre-lignes" }, el("span", {}, STATUTS[statut][0]), el("span", {}, String(liste.length))),
          liste.map(ligneSuivi));
      })),
      el("div", { style: "margin-top:12px" }, ajouter));
  }

  function ligneSuivi(s) {
    const [lib, couleur, ic] = STATUTS[s.statut] || STATUTS.a_voir;
    const due = s.relance && s.relance <= M.r.aujourdhui;
    const meta = [s.entreprise, nomSource(s.source), s.date ? t("Le {date}", { date: dateCourte(s.date) }) : ""].filter(Boolean).join(" · ");
    return el("div", { class: "ligne cliquable", onclick: () => editerSuivi(s) },
      el("span", { class: "ligne-ic" }, icone(ic)),
      el("div", { class: "ligne-corps" },
        el("div", { class: "ligne-titre" }, el("span", { class: "sans-icone" }, brut(s.titre))),
        el("div", { class: "ligne-meta sans-icone" }, brut(meta + (s.note ? "· " + s.note.split("\n")[0] : "")))),
      el("div", { class: "ligne-cote" },
        s.relance ? el("span", { class: "mi-relance " + (due ? " due" : ""), title: "Relancer le" }, icone("bell"), dateCourte(s.relance)) : null,
        el("span", { class: "etat-txt " + couleur }, lib)),
      el("div", { class: "ligne-actions" },
        s.url ? el("button", { class: "icone-btn", title: "Ouvrir l'offre", onclick: stop(() => ouvrirOffre(s)) }, icone("external-link")) : null,
        el("button", { class: "icone-btn", title: "Modifier", onclick: stop(() => editerSuivi(s)) }, icone("pencil")),
        el("button", { class: "icone-btn danger", title: "Supprimer", onclick: stop(() => supprimerSuivi(s)) }, icone("trash-2"))));
  }

  function editerSuivi(s) {
    const manuel = !s || s.source === "manuel";
    const champ = (lib, entree, classe = "", aide = null) => el("label", { class: "champ " + classe }, lib, entree, aide ? el("small", {}, aide) : null);
    const poste = el("input", { value: s?.titre || "", maxlength: 200 });
    const entreprise = el("input", { value: s?.entreprise || "", maxlength: 120 });
    const lien = el("input", { type: "url", value: s?.url || "", placeholder: "https://" });
    const statut = el("select", {}, Object.entries(STATUTS).map(([v, [lib]]) => el("option", { value: v, selected: v === (s?.statut || "postule") ? "" : null }, lib)));
    const date = el("input", { type: "date", value: s?.date || M.r.aujourdhui });
    const relance = el("input", { type: "date", value: s?.relance || "" });
    const note = el("textarea", { rows: 4, maxlength: 2000, value: s?.note || "" });
    const valider = async () => {
      const suivi = { id: s?.id, statut: statut.value, date: date.value, relance: relance.value, note: note.value };
      if (manuel) Object.assign(suivi, { titre: poste.value, entreprise: entreprise.value, url: lien.value });
      try {
        let r = await api("/api/missions/suivi/enregistrer", { suivi });
        // Relance : une tâche dans l'application Tâches, si elle est active (une par date).
        if (r.relance && r.relance !== (r.relance_tache || "") && actif("taches")) {
          try {
            const tache = await api("/api/taches/creer", {
              titre: t("Relancer : {poste}", { poste: r.titre }) + (r.entreprise ? "· " + r.entreprise : ""),
              echeance: r.relance, description: r.url || "", origine: "missions" });
            r = await api("/api/missions/suivi/enregistrer", { suivi: { id: r.id, statut: r.statut, tache_id: tache.id } });
            toast("Tâche de relance créée", "succes", 1800);
          } catch (e) { toast(e.message, "erreur"); }
        } else toast("Candidature enregistrée", "succes", 1500);
        fermer();
        M.r = await api("/api/missions/liste", {});
        for (const o of Object.values(M.offres)) for (const y of o.offres) if (y.id === r.id) y.suivi = r.statut;
        dessiner();
      } catch (e) { toast(e.message, "erreur"); }
    };
    fenetre([
      el("h3", {}, s ? "Modifier la candidature" : "Ajouter une candidature"),
      !manuel ? el("p", { class: "mi-aide sans-icone" }, brut(s.titre + (s.entreprise ? "· " + s.entreprise : "") + "· " + nomSource(s.source))) : null,
      el("div", { class: "mi-grille" },
        manuel ? [champ("Poste", poste, "large"), champ("Entreprise", entreprise), champ("Lien de l'offre", lien)] : null,
        champ("Statut", statut), champ("Date", date),
        champ("Relancer le", relance, "large", actif("taches") ? "Une tâche est créée dans Tâches à cette date." : null),
        champ("Note", note, "large")),
      el("div", { class: "actions" },
        el("button", { class: "btn", onclick: fermer }, "Annuler"),
        el("button", { class: "btn principal", onclick: valider }, "Enregistrer"))]);
    $("#fenetre").style.width = "min(600px, 94vw)";
    setTimeout(() => (manuel ? poste : statut).focus(), 60);
  }

  async function supprimerSuivi(s) {
    if (!(await confirmer(icone("trash-2"), "Supprimer cette candidature ?", "Elle disparaît du suivi. La tâche de relance éventuelle reste dans Tâches.", "Supprimer"))) return;
    try {
      await api("/api/missions/suivi/supprimer", { id: s.id });
      for (const o of Object.values(M.offres)) for (const y of o.offres) if (y.id === s.id) y.suivi = null;
      toast("Candidature supprimée");
      recharger();
    } catch (e) { toast(e.message, "erreur"); }
  }

  // ------------------------------------------------------ accueil, palette
  async function carteAccueil() {
    let r;
    try { r = await api("/api/missions/accueil", {}); } catch { return null; }
    if (!r.meilleures.length) return null;
    return el("div", { class: "carte-jour mi-carte", onclick: () => montrerVue("missions") },
      el("h4", {}, icone("briefcase"), "Missions"),
      r.meilleures.map(o => el("div", { class: "ligne-jour", onclick: ev => {
        ev.stopPropagation();
        M.vue = "r:" + o.recherche_id;
        M.ouverts.add(o.id);
        montrerVue("missions");
      } },
        el("span", { class: "heure", title: "Score" }, String(o.score)),
        el("span", { class: "nom sans-icone" }, brut(o.titre + (o.entreprise ? "· " + o.entreprise : ""))))),
      el("div", { class: "total sans-icone" }, brut(r.recherches.map(x =>
        x.nom + ": " + t(x.nouvelles > 1 ? "{n} nouvelles" : "{n} nouvelle", { n: x.nouvelles })).join(" · "))));
  }

  function commandes() {
    const ouvrir = (vue, apres) => () => { M.vue = vue; montrerVue("missions"); if (apres) setTimeout(apres, 80); };
    const liste = [
      { icone: icone("refresh-cw"), titre: "Actualiser les missions", detail: "Missions", action: () => { montrerVue("missions"); actualiser(false); } },
      { icone: icone("plus"), titre: "Nouvelle recherche", detail: "Missions", action: ouvrir(M.vue, () => editer(null)) },
    ];
    for (const x of M.r?.recherches || []) {
      liste.push({ icone: icone("briefcase"), titre: t("Missions : {nom}", { nom: x.nom }),
        detail: x.nouvelles ? t(x.nouvelles > 1 ? "{n} nouvelles" : "{n} nouvelle", { n: x.nouvelles }) : "", action: ouvrir("r: " + x.id) });
    }
    liste.push({ icone: icone("list-checks"), titre: "Suivi des candidatures", detail: "Missions", action: ouvrir("suivi") });
    return liste;
  }

  VUES.missions = {
    afficher,
    titre: "Missions", icone: icone("briefcase"), groupe: "clients", ordre: 5,
    description: "Offres freelance et télétravail de cinq sites publics, classées selon ce que vous cherchez, avec le suivi de vos candidatures.",
    profils: ["freelance", "developpeur", "assistant_virtuel"],
    carteAccueil, commandes,
  };
  // La palette (Ctrl + K) propose les recherches dès le démarrage.
  api("/api/missions/liste", {}).then(r => { if (!M.r) M.r = r; }).catch(() => {});
})();
