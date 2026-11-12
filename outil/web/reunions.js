"use strict";
/* Application « Réunions et déplacements » (voir reunions.py).
   - Réunions : informations, participants (Contacts si présent), ordre du
     jour, notes, décisions, actions (« Créer la tâche » si Tâches est là),
     compte rendu à copier ou à envoyer, ajout à l'agenda.
   - Déplacements : trajets, hébergement, documents liés, liste de contrôle,
     budget, feuille de route chronologique (copier, imprimer), agenda.
   Les fiches s'enregistrent seules pendant la saisie. */
(() => {
  I18N.ajouter({
    "Réunions et déplacements": "Meetings and trips",
    "Réunions, comptes rendus, actions à suivre, déplacements et feuilles de route.":
      "Meetings, minutes, action items, trips and itineraries.",
    "Réunions": "Meetings",
    "Déplacements": "Trips",
    "Nouvelle réunion": "New meeting",
    "Nouveau déplacement": "New trip",
    "À venir": "Upcoming",
    "Passées": "Past",
    "Passés": "Past",
    "Rechercher une réunion…": "Search meetings…",
    "Rechercher un déplacement…": "Search trips…",
    "Aucune réunion à venir.": "No upcoming meetings.",
    "Aucune réunion passée.": "No past meetings.",
    "Aucun déplacement à venir.": "No upcoming trips.",
    "Aucun déplacement passé.": "No past trips.",
    "Rien ne correspond à la recherche.": "Nothing matches your search.",
    "En cours": "In progress",
    "Aujourd'hui": "Today",
    "Demain": "Tomorrow",
    "dans {n} min": "in {n} min",
    "dans {n} h": "in {n} h",
    "dans {n} j": "in {n} d",
    "il y a {n} j": "{n} d ago",
    "{n} participant": "{n} attendee",
    "{n} participants": "{n} attendees",
    "{n} action": "{n} action item",
    "{n} actions": "{n} action items",
    "{n} jour": "{n} day",
    "{n} jours": "{n} days",
    "{n} trajet": "{n} journey",
    "{n} trajets": "{n} journeys",
    "Liste {a}/{b}": "Checklist {a}/{b}",
    "Visio": "Video call",
    "Réunion": "Meeting",
    "Déplacement": "Trip",
    "Fini": "Finished",
    // Fiche réunion
    "Informations": "Details",
    "Titre": "Title",
    "Date": "Date",
    "Heure": "Time",
    "Durée": "Duration",
    "Lieu": "Place",
    "Lien de visio": "Video call link",
    "ex. Salle de réunion, bureaux du client…": "e.g. Meeting room, client's office…",
    "ex. Point hebdomadaire": "e.g. Weekly check-in",
    "Ouvrir le lien": "Open the link",
    "Participants": "Attendees",
    "Nom, ou Nom <adresse e-mail>": "Name, or Name <email address>",
    "Ajouter un participant (Entrée)": "Add an attendee (Enter)",
    "Retirer": "Remove",
    "Ordre du jour": "Agenda",
    "Ajouter un point (Entrée)": "Add an item (Enter)",
    "Notes": "Notes",
    "Notes prises pendant la réunion…": "Notes taken during the meeting…",
    "Décisions": "Decisions",
    "Ajouter une décision (Entrée)": "Add a decision (Enter)",
    "Actions": "Actions",
    "Qui": "Who",
    "Quoi": "What",
    "Pour quand": "Due",
    "Ajouter une action": "Add an action item",
    "Créer la tâche": "Create the task",
    "Tâche créée": "Task created",
    "Indiquez d'abord ce qu'il faut faire.": "First enter what needs to be done.",
    "Réunion « {titre} » du {date}": "Meeting “{titre}” on {date}",
    "Responsable : {qui}": "Owner: {qui}",
    "Réunion : {titre}": "Meeting: {titre}",
    "Tâche créée dans Tâches": "Task created in Tasks",
    "Ajouter à l'agenda": "Add to calendar",
    "Mettre à jour l'agenda": "Update the calendar",
    "Ajouté à l'agenda": "Added to the calendar",
    "Agenda mis à jour": "Calendar updated",
    "Compte rendu": "Minutes",
    "Copier": "Copy",
    "Envoyer par mail": "Send by email",
    "Fermer": "Close",
    "Compte rendu copié": "Minutes copied",
    "Texte complet copié : collez-le dans le mail": "Full text copied: paste it into the email",
    "Aucun participant n'a d'adresse e-mail : ajoutez les destinataires dans le mail.":
      "No attendee has an email address: add the recipients in the email.",
    "Enregistré": "Saved",
    "Enregistrement…": "Saving…",
    "Supprimer": "Delete",
    "Supprimer cette réunion ?": "Delete this meeting?",
    "Ses notes, décisions et actions sont effacées. Ses rendez-vous dans l'agenda sont retirés aussi.":
      "Its notes, decisions and action items are erased. Its calendar appointments are removed too.",
    "Réunion supprimée": "Meeting deleted",
    "Créer": "Create",
    "Annuler": "Cancel",
    "Enregistrer": "Save",
    "Ajouter": "Add",
    "Modifier": "Edit",
    // Fiche déplacement
    "Destination": "Destination",
    "ex. Lyon, Montréal…": "e.g. Lyon, Montreal…",
    "Aller": "Outbound",
    "Retour (facultatif)": "Return (optional)",
    "Voyageurs": "Travellers",
    "Ajouter un voyageur (Entrée)": "Add a traveller (Enter)",
    "Budget prévu": "Planned budget",
    "Devise": "Currency",
    "Note": "Note",
    "Informations utiles, contacts sur place…": "Useful information, local contacts…",
    "Détails": "Details",
    "Feuille de route": "Itinerary",
    "Transports": "Transport",
    "Ajouter un trajet": "Add a journey",
    "Aucun trajet pour l'instant.": "No journey yet.",
    "Hébergement": "Accommodation",
    "Ajouter un hébergement": "Add accommodation",
    "Aucun hébergement pour l'instant.": "No accommodation yet.",
    "Documents": "Documents",
    "Ajouter des fichiers": "Add files",
    "Ajouter un dossier": "Add a folder",
    "Billets, réservations, programme…": "Tickets, bookings, schedule…",
    "Aucun document lié.": "No linked documents.",
    "Choisir les documents du déplacement": "Choose the trip documents",
    "Choisir un dossier du déplacement": "Choose a trip folder",
    "Ouvrir": "Open",
    "Afficher dans le dossier": "Show in folder",
    "Liste de contrôle": "Checklist",
    "Ajouter un élément (Entrée)": "Add an item (Enter)",
    "Liste type": "Standard list",
    "Ajouter les éléments habituels (papiers, chargeur…)": "Add the usual items (ID, charger…)",
    "Pièce d'identité ou passeport": "ID card or passport",
    "Billets et réservations": "Tickets and bookings",
    "Chargeur de téléphone": "Phone charger",
    "Ordinateur et chargeur": "Laptop and charger",
    "Adaptateur de prise": "Plug adapter",
    "Carte bancaire et un peu d'espèces": "Bank card and some cash",
    "Trousse de toilette": "Toiletry bag",
    "Médicaments": "Medicines",
    "Supprimer ce déplacement ?": "Delete this trip?",
    "Ses trajets, sa liste et ses liens vers les documents sont effacés (les fichiers restent). Ses rendez-vous dans l'agenda sont retirés aussi.":
      "Its journeys, checklist and document links are erased (the files stay). Its calendar appointments are removed too.",
    "Déplacement supprimé": "Trip deleted",
    "Trajet": "Journey",
    "Avion": "Flight",
    "Train": "Train",
    "Voiture": "Car",
    "Autre": "Other",
    "Type": "Type",
    "De": "From",
    "Vers": "To",
    "Départ": "Departure",
    "Arrivée": "Arrival",
    "Numéro (vol, train)": "Number (flight, train)",
    "Référence de réservation": "Booking reference",
    "ex. AF1234": "e.g. AF1234",
    "Nouveau trajet": "New journey",
    "Nouvel hébergement": "New accommodation",
    "Nom de l'hébergement": "Accommodation name",
    "Adresse": "Address",
    "n° {valeur}": "no. {valeur}",
    "réf. {valeur}": "ref. {valeur}",
    "Imprimer": "Print",
    "Feuille de route copiée": "Itinerary copied",
    // Erreurs du serveur
    "Donnez un titre à la réunion.": "Give the meeting a title.",
    "Date de la réunion manquante.": "Meeting date missing.",
    "Date de la réunion invalide.": "Invalid meeting date.",
    "Durée invalide.": "Invalid duration.",
    "La durée doit être comprise entre 5 minutes et 24 heures.": "The duration must be between 5 minutes and 24 hours.",
    "Lien de visio invalide (il commence par https://).": "Invalid video call link (it starts with https://).",
    "Échéance invalide.": "Invalid due date.",
    "Indiquez la destination.": "Enter the destination.",
    "Date de départ manquante.": "Departure date missing.",
    "Date de départ invalide.": "Invalid departure date.",
    "Date de retour invalide.": "Invalid return date.",
    "Date d'arrivée invalide.": "Invalid arrival date.",
    "Heure de départ invalide.": "Invalid departure time.",
    "Heure d'arrivée invalide.": "Invalid arrival time.",
    "Le retour doit être après le départ.": "The return must be after the departure.",
    "Une arrivée est avant son départ.": "An arrival is before its departure.",
    "Hébergement : le départ doit être après l'arrivée.": "Accommodation: check-out must be after check-in.",
    "Budget invalide.": "Invalid budget.",
    "Réunion introuvable.": "Meeting not found.",
    "Déplacement introuvable.": "Trip not found.",
    "Élément introuvable (supprimé entre-temps ?).": "Item not found (deleted in the meantime?).",
    "Ce document n'est pas lié à ce déplacement.": "This document is not linked to this trip.",
    "Genre inconnu.": "Unknown kind.",
  });
  I18N.motifs([
    [/^Adresse e-mail invalide : (.*)$/, "Invalid email address: $1"],
    [/^Ce type de fichier ne peut pas être joint : (.*)$/, "This file type cannot be attached: $1"],
    [/^Fichier introuvable : (.*)$/, "File not found: $1"],
  ]);

  // ------------------------------------------------------------- style
  const style = document.createElement("style");
  style.textContent = `
    .rn-barre2 { display: flex; align-items: center; gap: 10px; margin: -6px 0 14px; flex-wrap: wrap; }
    .rn-barre2 .espace { flex: 1; }
    .rn-compte { color: var(--gris); font-weight: 500; font-variant-numeric: tabular-nums; }
    .rn-fiche { display: grid; grid-template-columns: minmax(280px, 360px) minmax(0, 1fr); gap: 14px; align-items: start; }
    @media (max-width: 1000px) { .rn-fiche { grid-template-columns: 1fr; } }
    .rn-col { display: flex; flex-direction: column; gap: 14px; min-width: 0; }
    .rn-bloc { background: var(--carte); border: 1px solid var(--ligne); border-radius: var(--rayon); padding: 14px 16px; }
    .rn-bloc h3 { margin: 0 0 10px; font-size: 12px; font-weight: 600; color: var(--gris); text-transform: uppercase; letter-spacing: .04em;
      display: flex; align-items: center; gap: 8px; }
    .rn-bloc h3 .espace { flex: 1; }
    .rn-bloc h3 .rn-compte { text-transform: none; letter-spacing: 0; }
    .rn-bloc label.champ { margin-bottom: 10px; }
    .rn-bloc label.champ:last-child { margin-bottom: 0; }
    .rn-deux { display: grid; grid-template-columns: 1fr 1fr; gap: 0 10px; }
    .rn-trois { display: grid; grid-template-columns: 1.2fr .8fr .9fr; gap: 0 10px; }
    .rn-avec-btn { display: flex; gap: 4px; align-items: center; }
    .rn-avec-btn input { flex: 1; min-width: 0; }
    .rn-titre-saisie { font-size: 18px !important; font-weight: 600; border-color: transparent !important; background: transparent !important;
      padding: 4px 8px !important; margin-left: -8px; min-width: 0; flex: 1; max-width: 640px; }
    .rn-titre-saisie:hover { border-color: var(--ligne) !important; }
    .rn-titre-saisie:focus { border-color: var(--violet) !important; background: var(--champ) !important; }
    .rn-etat { font-size: 12.5px; color: var(--gris); white-space: nowrap; }
    .rn-etat.erreur { color: var(--rouge-texte); white-space: normal; }
    /* Étiquettes de participants / voyageurs */
    .rn-gens { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
    .rn-gens:empty { display: none; }
    .rn-pers { display: inline-flex; align-items: center; gap: 6px; border: 1px solid var(--ligne); border-radius: 6px; padding: 2px 4px 2px 8px;
      font-size: 13px; background: var(--surface); max-width: 100%; }
    .rn-pers span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .rn-pers small { color: var(--gris); font-size: 11.5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .rn-pers button { border: 0; background: transparent; color: var(--gris); cursor: pointer; width: 20px; height: 20px; border-radius: 4px;
      display: grid; place-items: center; padding: 0; flex: none; }
    .rn-pers button:hover { background: var(--ligne); color: var(--encre); }
    .rn-pers button svg.ico { width: 13px; height: 13px; margin: 0; }
    /* Listes à puces éditables (ordre du jour, décisions, liste de contrôle) */
    .rn-points { display: flex; flex-direction: column; }
    .rn-point { display: flex; align-items: center; gap: 8px; padding: 1px 0; border-radius: 6px; }
    .rn-point:hover { background: var(--surface); }
    .rn-point .rn-puce { width: 16px; display: grid; place-items: center; color: var(--gris); flex: none; }
    .rn-point .rn-puce::before { content: ""; width: 5px; height: 5px; border-radius: 50%; background: currentColor; }
    .rn-point input[type=checkbox] { width: 16px; height: 16px; margin: 0; flex: none; }
    .rn-point input.rn-texte { flex: 1; min-width: 0; border-color: transparent !important; background: transparent !important; padding: 5px 6px !important; }
    .rn-point input.rn-texte:focus { border-color: var(--violet) !important; background: var(--champ) !important; }
    .rn-point.fait input.rn-texte { color: var(--gris); text-decoration: line-through; }
    .rn-point .icone-btn { width: 26px; height: 26px; opacity: 0; }
    .rn-point:hover .icone-btn, .rn-point:focus-within .icone-btn { opacity: 1; }
    .rn-ajout { margin-top: 6px; width: 100%; }
    .rn-notes { width: 100%; min-height: 160px; resize: vertical; line-height: 1.5; }
    /* Actions */
    .rn-actions { display: flex; flex-direction: column; gap: 6px; }
    .rn-action { display: grid; grid-template-columns: minmax(90px, 160px) minmax(0, 1fr) 150px 128px 28px; gap: 6px; align-items: center; }
    .rn-action input { min-width: 0; width: 100%; }
    .rn-action .icone-btn { width: 28px; height: 28px; }
    .rn-action > .btn, .rn-action > .etat-txt { justify-self: start; }
    .rn-entetes { display: grid; grid-template-columns: minmax(90px, 160px) minmax(0, 1fr) 150px 128px 28px; gap: 6px; font-size: 11.5px; color: var(--gris); padding: 0 2px; }
    @media (max-width: 1200px) { .rn-action, .rn-entetes { grid-template-columns: 1fr 1fr; } .rn-entetes { display: none; } }
    /* Choix du type de trajet */
    .rn-types { display: flex; gap: 6px; flex-wrap: wrap; }
    .rn-types button { border: 1px solid var(--ligne); background: var(--champ); color: var(--doux); border-radius: 7px; height: 32px; padding: 0 12px;
      cursor: pointer; display: inline-flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 500; }
    .rn-types button.choisi { border-color: var(--violet); background: var(--violet-clair); color: var(--violet); }
    .rn-bloc .lignes { border-radius: 8px; }
    .rn-bloc .ligne { min-height: 42px; }
    .rn-bloc .vide { padding: 14px; font-size: 13px; }
    .rn-boutons { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 10px; }
    /* Feuille de route */
    .rn-feuille { background: var(--carte); border: 1px solid var(--ligne); border-radius: var(--rayon); padding: 22px 26px; max-width: 860px; }
    .rn-feuille h3 { margin: 0; font-size: 19px; font-weight: 600; letter-spacing: -.01em; }
    .rn-feuille .rn-periode { color: var(--doux); margin: 2px 0 6px; }
    .rn-feuille h4 { margin: 20px 0 6px; font-size: 12px; font-weight: 600; color: var(--gris); text-transform: uppercase; letter-spacing: .04em;
      padding-bottom: 6px; border-bottom: 1px solid var(--ligne); }
    .rn-evt { display: grid; grid-template-columns: 52px 22px minmax(0, 1fr); gap: 8px; padding: 6px 0; align-items: start; }
    .rn-evt .h { font-variant-numeric: tabular-nums; color: var(--doux); font-weight: 500; padding-top: 1px; }
    .rn-evt .i { color: var(--doux); padding-top: 2px; }
    .rn-evt .i svg.ico { margin: 0; width: 16px; height: 16px; }
    .rn-evt .t { font-weight: 500; }
    .rn-evt .d { color: var(--doux); font-size: 13px; }
    .rn-feuille ul { margin: 4px 0 0; padding-left: 18px; }
    .rn-feuille li { margin: 2px 0; }
    .rn-feuille .rn-coche { list-style: none; margin-left: -18px; display: flex; gap: 8px; align-items: center; }
    .rn-feuille .rn-coche svg.ico { margin: 0; color: var(--doux); }
    .rn-feuille .rn-texte-libre { white-space: pre-wrap; margin: 4px 0 0; }
    .rn-cr { width: 100%; min-height: 320px; resize: vertical; font-size: 13.5px; line-height: 1.5; }
    @media print {
      body.rn-impression * { visibility: hidden !important; }
      body.rn-impression .rn-feuille, body.rn-impression .rn-feuille * { visibility: visible !important; color: black !important; }
      body.rn-impression .rn-feuille { position: absolute; left: 0; top: 0; width: 100%; max-width: none; border: 0; padding: 0; background: white; }
      body.rn-impression .rn-feuille h4 { border-color: silver; }
    }
  `;
  document.head.append(style);

  // ---------------------------------------------------------- état, outils
  const R = {
    onglet: "reunions", periode: "a_venir", recherche: "", donnees: null,
    fiche: null,           // { genre: "reunion" | "deplacement", objet, vue: "details" | "feuille" }
    contacts: null, minuterie: null, chaine: Promise.resolve(true),
  };
  const racine = () => $("#vue-reunions");
  const brut = s => document.createTextNode(s ?? "");
  const deux = n => String(n).padStart(2, "0");
  const isoJour = d => `${d.getFullYear()}-${deux(d.getMonth() + 1)}-${deux(d.getDate())}`;
  const isoMinute = d => `${isoJour(d)}T${deux(d.getHours())}:${deux(d.getMinutes())}`;
  const date = iso => new Date(iso.length === 10 ? iso + "T00:00" : iso);
  const nouvelId = () => Math.random().toString(16).slice(2, 10) + Date.now().toString(16).slice(-4);
  const loc = () => I18N.locale();
  const jourCourt = iso => date(iso).toLocaleDateString(loc(), { weekday: "short", day: "numeric", month: "short" });
  const jourLong = iso => { const s = date(iso).toLocaleDateString(loc(), { weekday: "long", day: "numeric", month: "long", year: "numeric" });
    return s.charAt(0).toUpperCase() + s.slice(1); };
  const jourMois = iso => date(iso).toLocaleDateString(loc(), { day: "numeric", month: "short", year: "numeric" });
  const hhmm = iso => (iso || "").slice(11, 16);
  const pluriel = (n, un, plusieurs) => t(n > 1 ? plusieurs : un, { n });
  function dureeTexte(minutes) {
    if (minutes < 60) return `${minutes} min`;
    const h = Math.floor(minutes / 60), m = minutes % 60;
    return m ? `${h} h ${deux(m)}` : `${h} h`;
  }
  const DUREES = [15, 30, 45, 60, 90, 120, 180, 240, 480];
  const ICONES_TYPES = { avion: "plane", train: "train-front", voiture: "car", autre: "map-pin", hotel: "hotel", depart: "luggage", retour: "house" };
  const LIBELLES_TYPES = { avion: "Avion", train: "Train", voiture: "Voiture", autre: "Autre" };
  const LISTE_TYPE = ["Pièce d'identité ou passeport", "Billets et réservations", "Chargeur de téléphone", "Ordinateur et chargeur",
    "Adaptateur de prise", "Carte bancaire et un peu d'espèces", "Trousse de toilette", "Médicaments"];
  const erreur = e => toast(e.message, "erreur", 5000);

  /** « dans 25 min », « dans 3 h », « Demain », « dans 4 j », « il y a 2 j ». */
  function relatif(debut, maintenant = new Date()) {
    const min = Math.round((debut - maintenant) / 60000);
    const jours = Math.round((date(isoJour(debut)) - date(isoJour(maintenant))) / 864e5);
    if (min >= 0 && min < 60) return t("dans {n} min", { n: min });
    if (jours === 0 && min > 0) return t("dans {n} h", { n: Math.round(min / 60) });
    if (jours === 0) return t("Aujourd'hui");
    if (jours === 1) return t("Demain");
    return jours > 0 ? t("dans {n} j", { n: jours }) : t("il y a {n} j", { n: -jours });
  }

  async function charger() {
    R.donnees = await api("/api/reunions/liste", {});
    return R.donnees;
  }
  async function chargerContacts() {
    if (R.contacts) return R.contacts;
    try { const r = await api("/api/contacts/liste", {}); R.contacts = Array.isArray(r.contacts) ? r.contacts : []; }
    catch { R.contacts = []; }
    return R.contacts;
  }
  /** L'application Tâches est-elle là (chargée et pas désactivée) ? */
  function tachesDispo() {
    if (!window.VUES?.taches) return false;
    let masques = [];
    try { masques = S.masques || []; } catch { masques = []; }
    return !masques.includes("taches");
  }

  // ------------------------------------------------------- enregistrement
  /** Enregistrement automatique de la fiche ouverte (après une pause de saisie). */
  function modifie(immediat = false) {
    clearTimeout(R.minuterie);
    R.minuterie = null;
    etat("Enregistrement…");
    if (immediat) return sauver();
    R.minuterie = setTimeout(sauver, 700);
    return null;
  }
  /** Les enregistrements partent l'un après l'autre, chacun avec l'état le
      plus récent de la fiche. Renvoie true si tout est enregistré. */
  function sauver() {
    clearTimeout(R.minuterie);
    R.minuterie = null;
    R.chaine = R.chaine.then(envoyer);
    return R.chaine;
  }
  async function envoyer() {
    const f = R.fiche;
    if (!f) return true;
    const chemin = f.genre === "reunion" ? "/api/reunions/reunion/enregistrer" : "/api/reunions/deplacement/enregistrer";
    try {
      const r = await api(chemin, f.genre === "reunion" ? { reunion: f.objet } : { deplacement: f.objet });
      f.objet.modifie = r.modifie;
      f.objet.agenda_ids = r.agenda_ids || {};
      if (f.genre === "deplacement") f.objet.documents = r.documents;
      if (R.fiche === f) etat("Enregistré");
      return true;
    } catch (e) {
      if (R.fiche === f) etat(e.message, true);
      return false;
    }
  }
  /** Avant de quitter la fiche ou d'appeler le serveur : tout est enregistré.
      Sinon le message d'erreur s'affiche et la suite est annulée. */
  async function vider() {
    const ok = await (R.minuterie ? sauver() : R.chaine);
    if (!ok && R.fiche) toast($(".rn-etat", racine())?.textContent || t("Enregistrement…"), "erreur", 5000);
    return ok;
  }
  /** Un changement refusé par le serveur : message, retour à l'état
      précédent, puis nouvel enregistrement (la fiche redevient valide). */
  async function annuler(defaire) {
    toast($(".rn-etat", racine())?.textContent || t("Enregistrement…"), "erreur", 5000);
    defaire();
    if (await sauver()) dessiner();
  }
  function etat(texte, estErreur = false) {
    const e = $(".rn-etat", racine());
    if (!e) return;
    e.textContent = t(texte);
    e.classList.toggle("erreur", estErreur);
  }

  // -------------------------------------------------------------- dessin
  async function afficher() {
    if (R.fiche) return dessiner();
    try { await charger(); } catch (e) { erreur(e); return; }
    dessiner();
  }
  function dessiner() {
    if (R.fiche) return R.fiche.genre === "reunion" ? ficheReunion() : ficheDeplacement();
    return dessinerListe();
  }

  function dessinerListe() {
    const estReunion = R.onglet === "reunions";
    const maintenant = new Date();
    const tous = estReunion ? R.donnees.reunions : R.donnees.deplacements;
    const fini = x => estReunion ? date(x.fin) < maintenant : (x.retour || x.depart) < isoJour(maintenant);
    const aVenir = tous.filter(x => !fini(x)), passes = tous.filter(fini).reverse();
    const mots = R.recherche.trim().toLowerCase().split(/\s+/).filter(Boolean);
    const texte = x => (estReunion
      ? [x.titre, x.lieu, ...(x.participants || []).map(p => p.nom + p.email), ...(x.actions || []).map(a => a.qui + a.quoi)]
      : [x.destination, x.note, ...(x.voyageurs || []), ...(x.etapes || []).map(e => [e.de, e.vers, e.numero, e.reference].join(" ")),
         ...(x.hebergements || []).map(h => h.nom + h.adresse)]).join(" ").toLowerCase();
    const choisis = (R.periode === "a_venir" ? aVenir : passes).filter(x => mots.every(m => texte(x).includes(m)));

    const recherche = el("input", { type: "search", value: R.recherche, placeholder: estReunion ? "Rechercher une réunion…" : "Rechercher un déplacement…",
      oninput: e => { R.recherche = e.target.value; const pos = e.target.selectionStart; dessinerListe();
        const n = $(".rn-recherche input", racine()); if (n) { n.focus(); n.setSelectionRange(pos, pos); } } });
    racine().replaceChildren(
      el("div", { class: "barre-vue" },
        el("h2", {}, icone("presentation"), "Réunions et déplacements"),
        el("div", { class: "puces" },
          el("button", { class: "puce " + (estReunion ? " actif" : ""), onclick: () => { R.onglet = "reunions"; R.recherche = ""; dessinerListe(); } },
            icone("presentation"), "Réunions"),
          el("button", { class: "puce " + (!estReunion ? " actif" : ""), onclick: () => { R.onglet = "deplacements"; R.recherche = ""; dessinerListe(); } },
            icone("plane"), "Déplacements")),
        el("span", { class: "espace" }),
        el("button", { class: "btn principal", onclick: () => estReunion ? nouvelleReunion() : nouveauDeplacement() },
          icone("plus"), estReunion ? "Nouvelle réunion" : "Nouveau déplacement")),
      el("div", { class: "rn-barre2" },
        el("div", { class: "puces" },
          el("button", { class: "puce " + (R.periode === "a_venir" ? " actif" : ""), onclick: () => { R.periode = "a_venir"; dessinerListe(); } },
            "À venir", el("span", { class: "rn-compte" }, String(aVenir.length))),
          el("button", { class: "puce " + (R.periode === "passes" ? " actif" : ""), onclick: () => { R.periode = "passes"; dessinerListe(); } },
            estReunion ? "Passées" : "Passés", el("span", { class: "rn-compte" }, String(passes.length)))),
        el("span", { class: "espace" }),
        el("div", { class: "champ-recherche rn-recherche" }, el("span", {}, icone("search")), recherche)),
      choisis.length ? (estReunion ? listeReunions(choisis) : listeDeplacements(choisis))
        : el("div", { class: "vide" }, icone(estReunion ? "presentation" : "luggage"),
          mots.length ? "Rien ne correspond à la recherche."
            : estReunion ? (R.periode === "a_venir" ? "Aucune réunion à venir." : "Aucune réunion passée.")
              : (R.periode === "a_venir" ? "Aucun déplacement à venir." : "Aucun déplacement passé.")));
  }

  /** Lignes groupées par jour (titre de groupe : « Mardi 3 mars 2026 »). */
  function parJour(liste, cleJour, ligne) {
    const bloc = el("div", { class: "lignes" });
    let jour = null;
    for (const x of liste) {
      const j = cleJour(x);
      if (j !== jour) { jour = j; bloc.append(el("div", { class: "titre-lignes" }, brut(jourLong(j)))); }
      bloc.append(ligne(x));
    }
    return bloc;
  }

  function listeReunions(liste) {
    const maintenant = new Date();
    return parJour(liste, r => r.debut.slice(0, 10), r => {
      const debut = date(r.debut), fin = date(r.fin);
      const enCours = debut <= maintenant && maintenant < fin;
      const meta = [`${hhmm(r.debut)} – ${hhmm(r.fin)}`, r.lieu || (r.lien ? t("Visio") : ""),
        r.participants?.length ? pluriel(r.participants.length, "{n} participant", "{n} participants") : ""].filter(Boolean).join(" · ");
      const ouvertes = (r.actions || []).length;
      return el("div", { class: "ligne cliquable", onclick: () => ouvrirFiche("reunion", r) },
        el("span", { class: "ligne-ic" }, icone(r.lien ? "video" : "presentation")),
        el("div", { class: "ligne-corps" },
          el("div", { class: "ligne-titre" }, el("span", {}, brut(r.titre)), r.lien ? el("span", { class: "tag" }, "Visio") : null),
          el("div", { class: "ligne-meta" }, brut(meta))),
        el("div", { class: "ligne-cote" },
          ouvertes ? el("span", { class: "tag" }, pluriel(ouvertes, "{n} action", "{n} actions")) : null,
          enCours ? el("span", { class: "etat-txt vert" }, "En cours")
            : debut > maintenant ? el("span", { class: "etat-txt " + (debut - maintenant < 36e5 ? "ambre" : "gris") }, relatif(debut, maintenant)) : null),
        el("div", { class: "ligne-actions" },
          el("button", { class: "icone-btn", title: Object.keys(r.agenda_ids || {}).length ? "Mettre à jour l'agenda" : "Ajouter à l'agenda",
            onclick: e => { e.stopPropagation(); ajouterAgenda("reunion", r); } }, icone("calendar-check")),
          el("button", { class: "icone-btn", title: "Compte rendu", onclick: e => { e.stopPropagation(); compteRendu(r); } }, icone("file-text")),
          el("button", { class: "icone-btn danger", title: "Supprimer", onclick: e => { e.stopPropagation(); supprimerReunion(r); } }, icone("trash-2"))));
    });
  }

  function listeDeplacements(liste) {
    const auj = isoJour(new Date());
    const bloc = el("div", { class: "lignes" });
    for (const d of liste) {
      const fin = d.retour || d.depart;
      const nbJours = Math.round((date(fin) - date(d.depart)) / 864e5) + 1;
      const premier = (d.etapes || []).find(e => e.type) || null;
      const dates = d.retour && d.retour !== d.depart ? `${jourCourt(d.depart)} – ${jourMois(d.retour)}` : jourMois(d.depart);
      const meta = [dates, pluriel(nbJours, "{n} jour", "{n} jours"), (d.voyageurs || []).join(", "),
        d.etapes?.length ? pluriel(d.etapes.length, "{n} trajet", "{n} trajets") : "", (d.hebergements || [])[0]?.nom || ""].filter(Boolean).join(" · ");
      const coches = (d.controle || []).filter(p => p.fait).length, total = (d.controle || []).length;
      const enCours = d.depart <= auj && auj <= fin;
      const proche = !enCours && d.depart > auj && date(d.depart) - date(auj) <= 2 * 864e5;
      bloc.append(el("div", { class: "ligne cliquable", onclick: () => ouvrirFiche("deplacement", d) },
        el("span", { class: "ligne-ic" }, icone(premier ? ICONES_TYPES[premier.type] : "luggage")),
        el("div", { class: "ligne-corps" },
          el("div", { class: "ligne-titre" }, el("span", {}, brut(d.destination))),
          el("div", { class: "ligne-meta" }, brut(meta))),
        el("div", { class: "ligne-cote" },
          total ? el("span", { class: "etat-txt " + (coches < total && (enCours || proche) ? "ambre" : "gris") },
            t("Liste {a}/{b}", { a: coches, b: total })) : null,
          enCours ? el("span", { class: "etat-txt vert" }, "En cours")
            : d.depart > auj ? el("span", { class: "etat-txt " + (proche ? "ambre" : "gris") }, relatif(date(d.depart + "T23:59"), new Date())) : null),
        el("div", { class: "ligne-actions" },
          el("button", { class: "icone-btn", title: "Feuille de route", onclick: e => { e.stopPropagation(); ouvrirFiche("deplacement", d, "feuille"); } },
            icone("scroll-text")),
          el("button", { class: "icone-btn", title: Object.keys(d.agenda_ids || {}).length ? "Mettre à jour l'agenda" : "Ajouter à l'agenda",
            onclick: e => { e.stopPropagation(); ajouterAgenda("deplacement", d); } }, icone("calendar-check")),
          el("button", { class: "icone-btn danger", title: "Supprimer", onclick: e => { e.stopPropagation(); supprimerDeplacement(d); } }, icone("trash-2")))));
    }
    return bloc;
  }

  // ------------------------------------------------------- ouvrir, créer
  function ouvrirFiche(genre, objet, vue = "details") {
    R.onglet = genre === "reunion" ? "reunions" : "deplacements";
    R.fiche = { genre, objet: structuredClone(objet), vue };
    dessiner();
    window.scrollTo(0, 0);
  }
  async function retourListe() {
    if (!(await vider())) return;
    R.fiche = null;
    try { await charger(); } catch (e) { erreur(e); }
    dessinerListe();
  }

  function nouvelleReunion() {
    const d = new Date(Date.now() + 30 * 60000);
    d.setMinutes(d.getMinutes() < 30 ? 30 : 60, 0, 0);
    const titre = el("input", { placeholder: "ex. Point hebdomadaire", maxlength: 200 });
    const jour = el("input", { type: "date", value: isoJour(d) });
    const heure = el("input", { type: "time", value: `${deux(d.getHours())}:${deux(d.getMinutes())}` });
    const duree = selectDuree(60);
    const creer = async () => {
      try {
        const r = await api("/api/reunions/reunion/enregistrer", { reunion: { titre: titre.value, debut: `${jour.value}T${heure.value}`, duree: Number(duree.value) } });
        fermer();
        ouvrirFiche("reunion", r);
      } catch (e) { erreur(e); }
    };
    titre.addEventListener("keydown", e => { if (e.key === "Enter") creer(); });
    fenetre([
      el("div", { class: "gros" }, icone("presentation")),
      el("h3", {}, "Nouvelle réunion"),
      el("label", { class: "champ" }, "Titre", titre),
      el("div", { class: "rn-trois" }, el("label", { class: "champ" }, "Date", jour), el("label", { class: "champ" }, "Heure", heure),
        el("label", { class: "champ" }, "Durée", duree)),
      el("div", { class: "actions" },
        el("button", { class: "btn", onclick: fermer }, "Annuler"),
        el("button", { class: "btn principal", onclick: creer }, "Créer"))]);
    setTimeout(() => titre.focus(), 60);
  }

  function nouveauDeplacement() {
    const destination = el("input", { placeholder: "ex. Lyon, Montréal…", maxlength: 200 });
    const demain = new Date(Date.now() + 864e5);
    const aller = el("input", { type: "date", value: isoJour(demain) });
    const retour = el("input", { type: "date" });
    aller.addEventListener("change", () => { if (retour.value && retour.value < aller.value) retour.value = aller.value; });
    const creer = async () => {
      try {
        const d = await api("/api/reunions/deplacement/enregistrer", { deplacement: { destination: destination.value, depart: aller.value, retour: retour.value } });
        fermer();
        ouvrirFiche("deplacement", d);
      } catch (e) { erreur(e); }
    };
    destination.addEventListener("keydown", e => { if (e.key === "Enter") creer(); });
    fenetre([
      el("div", { class: "gros" }, icone("plane")),
      el("h3", {}, "Nouveau déplacement"),
      el("label", { class: "champ" }, "Destination", destination),
      el("div", { class: "rn-deux" }, el("label", { class: "champ" }, "Aller", aller), el("label", { class: "champ" }, "Retour (facultatif)", retour)),
      el("div", { class: "actions" },
        el("button", { class: "btn", onclick: fermer }, "Annuler"),
        el("button", { class: "btn principal", onclick: creer }, "Créer"))]);
    setTimeout(() => destination.focus(), 60);
  }

  function selectDuree(valeur, onchange) {
    const valeurs = DUREES.includes(valeur) ? DUREES : [...DUREES, valeur].sort((a, b) => a - b);
    return el("select", { onchange }, valeurs.map(m => el("option", { value: m, selected: m === valeur ? "" : null }, dureeTexte(m))));
  }

  // ---------------------------------------------------- éléments communs
  /** Un champ texte relié à objet[cle], enregistré pendant la saisie. */
  function saisie(objet, cle, attrs = {}) {
    const tag = attrs.multiligne ? "textarea" : "input";
    const { multiligne, apres, ...reste } = attrs;
    return el(tag, { ...reste, value: objet[cle] ?? "", oninput: e => { objet[cle] = e.target.value; apres?.(); modifie(); } });
  }
  function bloc(titre, ic, ...contenu) {
    return el("section", { class: "rn-bloc" }, el("h3", {}, icone(ic), titre), ...contenu);
  }
  /** Liste éditable : [{texte, fait}] (cases à cocher) ou [texte] (puces). */
  function points(liste, { cases = false, placeholder = "Ajouter un point (Entrée)", apres } = {}) {
    const boite = el("div", { class: "rn-points" });
    const ligne = (p, i) => {
      const texte = cases || typeof p === "object" ? p.texte : p;
      const champ = el("input", { class: "rn-texte", value: texte, maxlength: 500,
        oninput: e => { if (typeof liste[i] === "object") liste[i].texte = e.target.value; else liste[i] = e.target.value; modifie(); },
        onkeydown: e => { if (e.key === "Enter") ajout.focus(); } });
      const rang = el("div", { class: "rn-point " + (cases && p.fait ? " fait" : "") },
        cases ? el("input", { type: "checkbox", checked: p.fait ? "" : null, onchange: e => {
          p.fait = e.target.checked; rang.classList.toggle("fait", p.fait); apres?.(); modifie(); } })
          : el("span", { class: "rn-puce" }),
        champ,
        el("button", { class: "icone-btn danger", title: "Retirer", onclick: () => { liste.splice(i, 1); redessiner(); apres?.(); modifie(); } }, icone("x")));
      return rang;
    };
    const redessiner = () => boite.replaceChildren(...liste.map(ligne));
    const ajout = el("input", { class: "rn-ajout", placeholder, maxlength: 500, onkeydown: e => {
      if (e.key !== "Enter" || !e.target.value.trim()) return;
      liste.push(cases || liste.some(x => typeof x === "object") ? { texte: e.target.value.trim(), fait: false } : e.target.value.trim());
      e.target.value = "";
      redessiner(); apres?.(); modifie();
    } });
    redessiner();
    const conteneur = el("div", {}, boite, ajout);
    conteneur.redessiner = redessiner;
    return conteneur;
  }
  /** Étiquettes de personnes (participants, voyageurs) + saisie. */
  function personnes(liste, { placeholder, versObjet, libelle, detail, datalist }) {
    const zone = el("div", { class: "rn-gens" });
    const redessiner = () => zone.replaceChildren(...liste.map((p, i) => el("span", { class: "rn-pers", title: detail?.(p) || libelle(p) },
      el("span", {}, brut(libelle(p))), detail?.(p) ? el("small", {}, brut(detail(p))) : null,
      el("button", { title: "Retirer", onclick: () => { liste.splice(i, 1); redessiner(); modifie(); } }, icone("x")))));
    const ajouter = champ => {
      const valeur = champ.value.trim();
      if (!valeur) return;
      liste.push(versObjet(valeur));
      champ.value = "";
      redessiner(); modifie();
    };
    const champ = el("input", { placeholder, maxlength: 200, list: datalist ? datalist.id : null,
      onkeydown: e => { if (e.key === "Enter") { e.preventDefault(); ajouter(e.target); } },
      onchange: e => { if (datalist && [...datalist.options].some(o => o.value === e.target.value)) ajouter(e.target); } });
    redessiner();
    return el("div", {}, zone, el("div", { class: "rn-avec-btn" }, champ,
      el("button", { class: "icone-btn", title: "Ajouter", onclick: () => ajouter(champ) }, icone("plus"))), datalist);
  }
  function enteteFiche(retour, titreChamp, ...boutons) {
    return el("div", { class: "barre-vue" },
      el("button", { class: "btn discret", onclick: retourListe }, icone("chevron-left"), t(retour)),
      titreChamp,
      el("span", { class: "rn-etat" }, ""),
      el("span", { class: "espace" }),
      ...boutons);
  }

  // ------------------------------------------------------- fiche réunion
  async function ficheReunion() {
    const r = R.fiche.objet;
    for (const cle of ["participants", "ordre_du_jour", "decisions", "actions"]) r[cle] ||= [];
    const contacts = await chargerContacts();
    if (R.fiche?.objet !== r) return;  // une autre fiche a été ouverte entre-temps

    const titre = saisie(r, "titre", { class: "rn-titre-saisie", maxlength: 200, placeholder: "Titre" });
    const jour = el("input", { type: "date", value: r.debut.slice(0, 10), onchange: e => { if (e.target.value) { r.debut = e.target.value + r.debut.slice(10); modifie(); } } });
    const heure = el("input", { type: "time", value: hhmm(r.debut), onchange: e => { if (e.target.value) { r.debut = r.debut.slice(0, 11) + e.target.value; modifie(); } } });
    const duree = selectDuree(r.duree || 60, e => { r.duree = Number(e.target.value); modifie(); });
    const lien = saisie(r, "lien", { placeholder: "https://…", maxlength: 500 });
    const ouvrirLien = el("button", { class: "icone-btn", title: "Ouvrir le lien", onclick: () => {
      if (/^https?:\/\//i.test(r.lien || "")) window.open(r.lien, "_blank", "noopener"); } }, icone("external-link"));

    // Participants : Contacts (si présent) ou saisie libre « Nom <adresse> ».
    const listeContacts = el("datalist", { id: "rn-contacts" },
      contacts.map(c => el("option", { value: c.nom || c.email || "" }, brut([c.entreprise, c.email].filter(Boolean).join(" · ")))));
    const versParticipant = valeur => {
      const c = contacts.find(x => (x.nom || "").toLowerCase() === valeur.toLowerCase() || (x.email || "").toLowerCase() === valeur.toLowerCase());
      if (c) return { nom: c.nom || "", email: c.email || "", contact_id: String(c.id) };
      const m = valeur.match(/^(.*?)\s*<([^<>\s]+@[^<>\s]+)>\s*$/);
      if (m) return { nom: m[1].trim(), email: m[2], contact_id: null };
      if (/^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(valeur)) return { nom: "", email: valeur, contact_id: null };
      return { nom: valeur, email: "", contact_id: null };
    };
    const participants = personnes(r.participants, {
      placeholder: "Nom, ou Nom <adresse e-mail>", versObjet: versParticipant, datalist: listeContacts,
      libelle: p => p.nom || p.email, detail: p => (p.nom && p.email ? p.email : ""),
    });

    const notes = saisie(r, "notes", { multiligne: true, class: "rn-notes", placeholder: "Notes prises pendant la réunion…", maxlength: 20000 });

    racine().replaceChildren(
      enteteFiche("Réunions", titre,
        el("button", { class: "btn", onclick: () => ajouterAgenda("reunion", r) }, icone("calendar-check"),
          Object.keys(r.agenda_ids || {}).length ? "Mettre à jour l'agenda" : "Ajouter à l'agenda"),
        el("button", { class: "btn", onclick: () => compteRendu(r) }, icone("file-text"), "Compte rendu"),
        el("button", { class: "icone-btn danger", title: "Supprimer", onclick: () => supprimerReunion(r) }, icone("trash-2"))),
      el("div", { class: "rn-fiche" },
        el("div", { class: "rn-col" },
          bloc("Informations", "info",
            el("div", { class: "rn-trois" },
              el("label", { class: "champ" }, "Date", jour), el("label", { class: "champ" }, "Heure", heure),
              el("label", { class: "champ" }, "Durée", duree)),
            el("label", { class: "champ" }, "Lieu", saisie(r, "lieu", { placeholder: "ex. Salle de réunion, bureaux du client…", maxlength: 300 })),
            el("label", { class: "champ" }, "Lien de visio", el("div", { class: "rn-avec-btn" }, lien, ouvrirLien))),
          bloc("Participants", "users", participants)),
        el("div", { class: "rn-col" },
          bloc("Ordre du jour", "list-checks", points(r.ordre_du_jour, { cases: true })),
          bloc("Notes", "notebook-pen", notes),
          bloc("Décisions", "flag", points(r.decisions, { placeholder: "Ajouter une décision (Entrée)" })),
          blocActions(r))));
    etat(r.modifie ? "Enregistré" : "");
  }

  function blocActions(r) {
    const boite = el("div", { class: "rn-actions" });
    const noms = el("datalist", { id: "rn-qui" });
    const majNoms = () => noms.replaceChildren(...r.participants.map(p => el("option", { value: p.nom || p.email })));
    const ligne = a => {
      const tache = a.tache_id
        ? el("span", { class: "etat-txt vert", title: "Tâche créée dans Tâches" }, icone("circle-check"), "Tâche créée")
        : tachesDispo() ? el("button", { class: "btn petit", onclick: () => creerTache(r, a, redessiner) }, icone("list-checks"), "Créer la tâche")
          : el("span");
      return el("div", { class: "rn-action" },
        el("input", { value: a.qui, placeholder: "Qui", list: "rn-qui", maxlength: 120, onfocus: majNoms, oninput: e => { a.qui = e.target.value; modifie(); } }),
        el("input", { value: a.quoi, placeholder: "Quoi", maxlength: 500, oninput: e => { a.quoi = e.target.value; modifie(); } }),
        el("input", { type: "date", value: a.echeance || "", title: "Pour quand", onchange: e => { a.echeance = e.target.value; modifie(); } }),
        tache,
        el("button", { class: "icone-btn danger", title: "Retirer", onclick: () => { r.actions.splice(r.actions.indexOf(a), 1); redessiner(); modifie(); } }, icone("x")));
    };
    const redessiner = () => boite.replaceChildren(
      r.actions.length ? el("div", { class: "rn-entetes" }, el("span", {}, "Qui"), el("span", {}, "Quoi"), el("span", {}, "Pour quand")) : null,
      ...r.actions.map(ligne));
    redessiner();
    return bloc("Actions", "square-check", boite, noms,
      el("div", { class: "rn-boutons" },
        el("button", { class: "btn petit", onclick: () => {
          r.actions.push({ id: nouvelId(), qui: "", quoi: "", echeance: "", tache_id: null });
          redessiner();
          boite.querySelector(".rn-action:last-child input")?.focus();
        } }, icone("plus"), "Ajouter une action")));
  }

  async function creerTache(r, a, redessiner) {
    if (!a.quoi.trim()) { toast("Indiquez d'abord ce qu'il faut faire.", "erreur"); return; }
    const participant = r.participants.find(p => p.contact_id && [p.nom, p.email].includes(a.qui.trim()));
    const description = t("Réunion « {titre} » du {date}", { titre: r.titre, date: jourMois(r.debut) }) +
      (a.qui.trim() ? "\n " + t("Responsable : {qui}", { qui: a.qui.trim() }) : "");
    try {
      const tache = await api("/api/taches/creer", { titre: a.quoi.trim(), echeance: a.echeance || "", description,
        contact_id: participant?.contact_id || "", origine: t("Réunion : {titre}", { titre: r.titre }) });
      a.tache_id = String(tache?.id ?? tache?.tache?.id ?? "1");
      redessiner();
      await modifie(true);
      toast("Tâche créée dans Tâches", "succes", 1800);
    } catch (e) { erreur(e); }
  }

  // ------------------------------------------------- compte rendu, agenda
  async function compteRendu(r) {
    if (R.fiche) { if (!(await vider())) return; }
    let cr;
    try { cr = await api("/api/reunions/reunion/compte_rendu", { id: r.id }); } catch (e) { erreur(e); return; }
    const zone = el("textarea", { class: "rn-cr", readonly: "", value: cr.texte });
    const envoyer = () => {
      if (cr.tronque) copier(cr.texte, "Texte complet copié : collez-le dans le mail");
      else if (!cr.destinataires.length) toast("Aucun participant n'a d'adresse e-mail : ajoutez les destinataires dans le mail.", "", 4500);
      const lien = el("a", { href: cr.mailto });
      document.body.append(lien); lien.click(); lien.remove();
    };
    fenetre([
      el("h3", {}, "Compte rendu"),
      el("p", {}, brut(cr.sujet)),
      zone,
      el("div", { class: "actions" },
        el("button", { class: "btn", onclick: fermer }, "Fermer"),
        el("button", { class: "btn", onclick: () => copier(cr.texte, "Compte rendu copié") }, icone("copy"), "Copier"),
        el("button", { class: "btn principal", onclick: envoyer }, icone("send"), "Envoyer par mail"))]);
    $("#fenetre").style.width = "min(720px, 94vw)";
  }

  async function ajouterAgenda(genre, objet) {
    if (R.fiche) { if (!(await vider())) return; }
    try {
      const r = await api("/api/reunions/agenda/elements", { genre, id: objet.id });
      const avant = Object.keys(objet.agenda_ids || {}).length;
      const ids = {};
      for (const { cle, element } of r.elements) ids[cle] = (await api("/api/agenda/enregistrer", { element })).id;
      for (const id of r.obsoletes) { try { await api("/api/agenda/supprimer", { id }); } catch { /* déjà retiré */ } }
      const lie = await api("/api/reunions/agenda/lier", { genre, id: objet.id, ids });
      objet.agenda_ids = lie.agenda_ids;
      if (R.fiche?.objet.id === objet.id) R.fiche.objet.agenda_ids = lie.agenda_ids;
      toast(avant ? "Agenda mis à jour" : "Ajouté à l'agenda", "succes", 1800);
      dessiner();
    } catch (e) { erreur(e); }
  }
  async function retirerDeLAgenda(objet) {
    for (const id of Object.values(objet.agenda_ids || {})) { try { await api("/api/agenda/supprimer", { id }); } catch { /* déjà retiré */ } }
  }

  async function supprimerReunion(r) {
    if (!(await confirmer(icone("trash-2"), "Supprimer cette réunion ?",
      "Ses notes, décisions et actions sont effacées. Ses rendez-vous dans l'agenda sont retirés aussi.", "Supprimer"))) return;
    clearTimeout(R.minuterie);
    try {
      await api("/api/reunions/reunion/supprimer", { id: r.id });
      await retirerDeLAgenda(r);
      toast("Réunion supprimée");
      R.fiche = null;
      await charger();
      dessinerListe();
    } catch (e) { erreur(e); }
  }
  async function supprimerDeplacement(d) {
    if (!(await confirmer(icone("trash-2"), "Supprimer ce déplacement ?",
      "Ses trajets, sa liste et ses liens vers les documents sont effacés (les fichiers restent). Ses rendez-vous dans l'agenda sont retirés aussi.", "Supprimer"))) return;
    clearTimeout(R.minuterie);
    try {
      await api("/api/reunions/deplacement/supprimer", { id: d.id });
      await retirerDeLAgenda(d);
      toast("Déplacement supprimé");
      R.fiche = null;
      await charger();
      dessinerListe();
    } catch (e) { erreur(e); }
  }

  // --------------------------------------------------- fiche déplacement
  function ficheDeplacement() {
    const d = R.fiche.objet;
    for (const cle of ["voyageurs", "etapes", "hebergements", "documents", "controle"]) d[cle] ||= [];
    const titre = saisie(d, "destination", { class: "rn-titre-saisie", maxlength: 200, placeholder: "Destination" });
    const vue = R.fiche.vue;
    const puces = el("div", { class: "puces" },
      el("button", { class: "puce " + (vue === "details" ? " actif" : ""), onclick: () => { R.fiche.vue = "details"; dessiner(); } }, "Détails"),
      el("button", { class: "puce " + (vue === "feuille" ? " actif" : ""), onclick: async () => { if (await vider()) { R.fiche.vue = "feuille"; dessiner(); } } },
        "Feuille de route"));
    const entete = enteteFiche("Déplacements", titre, puces,
      el("button", { class: "btn", onclick: () => ajouterAgenda("deplacement", d) }, icone("calendar-check"),
        Object.keys(d.agenda_ids || {}).length ? "Mettre à jour l'agenda" : "Ajouter à l'agenda"),
      el("button", { class: "icone-btn danger", title: "Supprimer", onclick: () => supprimerDeplacement(d) }, icone("trash-2")));
    if (vue === "feuille") return feuilleDeRoute(d, entete);

    const aller = el("input", { type: "date", value: d.depart, onchange: e => { d.depart = e.target.value; modifie(); } });
    const retour = el("input", { type: "date", value: d.retour || "", onchange: e => { d.retour = e.target.value; modifie(); } });
    const compteListe = el("span", { class: "rn-compte" });
    const majCompte = () => { compteListe.textContent = d.controle.length ? `${d.controle.filter(p => p.fait).length}/${d.controle.length}` : ""; };
    majCompte();
    const liste = points(d.controle, { cases: true, placeholder: "Ajouter un élément (Entrée)", apres: majCompte });
    const budget = el("input", { value: d.budget ?? "", inputmode: "decimal", maxlength: 20,
      oninput: e => { d.budget = e.target.value.trim() === "" ? null : e.target.value; modifie(); } });

    racine().replaceChildren(entete,
      el("div", { class: "rn-fiche" },
        el("div", { class: "rn-col" },
          bloc("Informations", "info",
            el("div", { class: "rn-deux" }, el("label", { class: "champ" }, "Aller", aller), el("label", { class: "champ" }, "Retour (facultatif)", retour)),
            el("label", { class: "champ" }, "Voyageurs", personnes(d.voyageurs, { placeholder: "Ajouter un voyageur (Entrée)", versObjet: v => v, libelle: v => v })),
            el("div", { class: "rn-deux", style: "grid-template-columns: 1fr 90px" },
              el("label", { class: "champ" }, "Budget prévu", budget),
              el("label", { class: "champ" }, "Devise", saisie(d, "devise", { maxlength: 10, placeholder: "EUR" }))),
            el("label", { class: "champ" }, "Note", saisie(d, "note", { multiligne: true, rows: 4, maxlength: 5000, placeholder: "Informations utiles, contacts sur place…" }))),
          el("section", { class: "rn-bloc" },
            el("h3", {}, icone("list-checks"), "Liste de contrôle", compteListe, el("span", { class: "espace" }),
              el("button", { class: "btn discret petit", title: "Ajouter les éléments habituels (papiers, chargeur…)", onclick: () => {
                const deja = new Set(d.controle.map(p => p.texte.toLowerCase()));
                for (const x of LISTE_TYPE) { const tx = t(x); if (!deja.has(tx.toLowerCase())) d.controle.push({ texte: tx, fait: false }); }
                liste.redessiner(); majCompte(); modifie();
              } }, icone("plus"), "Liste type")),
            liste)),
        el("div", { class: "rn-col" }, blocEtapes(d), blocHebergements(d), blocDocuments(d))));
    etat(d.modifie ? "Enregistré" : "");
  }

  function quandEtape(e) {
    if (!e.depart) return "";
    let s = `${jourCourt(e.depart)} ${hhmm(e.depart)}`;
    if (e.arrivee) s += "– " + (e.arrivee.slice(0, 10) === e.depart.slice(0, 10) ? hhmm(e.arrivee) : `${jourCourt(e.arrivee)} ${hhmm(e.arrivee)}`);
    return s;
  }
  function blocEtapes(d) {
    const tries = [...d.etapes].sort((a, b) => (a.depart || "9").localeCompare(b.depart || "9"));
    return bloc("Transports", "train-front",
      tries.length ? el("div", { class: "lignes" }, tries.map(e => el("div", { class: "ligne cliquable", onclick: () => editerEtape(d, e) },
        el("span", { class: "ligne-ic" }, icone(ICONES_TYPES[e.type] || "map-pin")),
        el("div", { class: "ligne-corps" },
          el("div", { class: "ligne-titre" }, el("span", {}, t(LIBELLES_TYPES[e.type] || "Autre"), brut(e.de || e.vers ? [e.de, e.vers].filter(Boolean).join(" → ") : ""))),
          el("div", { class: "ligne-meta" }, brut([quandEtape(e), e.numero ? t("n° {valeur}", { valeur: e.numero }) : "",
            e.reference ? t("réf. {valeur}", { valeur: e.reference }) : "", e.note].filter(Boolean).join(" · ")))),
        el("div", { class: "ligne-actions" },
          el("button", { class: "icone-btn", title: "Modifier", onclick: ev => { ev.stopPropagation(); editerEtape(d, e); } }, icone("pencil")),
          el("button", { class: "icone-btn danger", title: "Supprimer", onclick: ev => {
            ev.stopPropagation(); d.etapes.splice(d.etapes.indexOf(e), 1); modifie(true); dessiner(); } }, icone("trash-2"))))))
        : el("div", { class: "vide" }, "Aucun trajet pour l'instant."),
      el("div", { class: "rn-boutons" }, el("button", { class: "btn petit", onclick: () => editerEtape(d, null) }, icone("plus"), "Ajouter un trajet")));
  }

  function editerEtape(d, etape) {
    const precedente = [...d.etapes].filter(e => e.depart).sort((a, b) => b.depart.localeCompare(a.depart))[0];
    const b = etape ? { ...etape } : { id: nouvelId(), type: precedente?.type || "train", de: precedente?.vers || "", vers: "",
      depart: `${d.depart}T08:00`, arrivee: "", numero: "", reference: "", note: "" };
    const types = el("div", { class: "rn-types" }, Object.entries(LIBELLES_TYPES).map(([v, lib]) =>
      el("button", { type: "button", class: v === b.type ? "choisi" : "", onclick: ev => {
        b.type = v; [...types.children].forEach(x => x.classList.toggle("choisi", x === ev.currentTarget)); } }, icone(ICONES_TYPES[v]), lib)));
    const champ = (lib, cle, attrs = {}) => el("label", { class: "champ" }, lib,
      el("input", { ...attrs, value: b[cle] || "", oninput: e => { b[cle] = e.target.value; } }));
    const valider = async () => {
      const avant = etape ? { ...etape } : null;
      if (etape) Object.assign(etape, b); else d.etapes.push(b);
      if (!(await modifie(true))) return annuler(() => { if (etape) Object.assign(etape, avant); else d.etapes.pop(); });
      fermer(); dessiner();
    };
    fenetre([
      el("h3", {}, etape ? "Trajet" : "Nouveau trajet"),
      el("label", { class: "champ" }, "Type", types),
      el("div", { class: "rn-deux" }, champ("De", "de", { maxlength: 120 }), champ("Vers", "vers", { maxlength: 120 })),
      el("div", { class: "rn-deux" }, champ("Départ", "depart", { type: "datetime-local" }), champ("Arrivée", "arrivee", { type: "datetime-local" })),
      el("div", { class: "rn-deux" }, champ("Numéro (vol, train)", "numero", { maxlength: 60, placeholder: "ex. AF1234" }),
        champ("Référence de réservation", "reference", { maxlength: 60 })),
      champ("Note", "note", { maxlength: 300 }),
      el("div", { class: "actions" },
        el("button", { class: "btn", onclick: fermer }, "Annuler"),
        el("button", { class: "btn principal", onclick: valider }, etape ? "Enregistrer" : "Ajouter"))]);
  }

  function blocHebergements(d) {
    return bloc("Hébergement", "hotel",
      d.hebergements.length ? el("div", { class: "lignes" }, d.hebergements.map(h => el("div", { class: "ligne cliquable", onclick: () => editerHebergement(d, h) },
        el("span", { class: "ligne-ic" }, icone("hotel")),
        el("div", { class: "ligne-corps" },
          el("div", { class: "ligne-titre" }, el("span", {}, brut(h.nom || h.adresse))),
          el("div", { class: "ligne-meta" }, brut([h.nom ? h.adresse : "",
            h.arrivee ? (h.depart && h.depart !== h.arrivee ? `${jourCourt(h.arrivee)} – ${jourCourt(h.depart)}` : jourCourt(h.arrivee)) : "",
            h.reference ? t("réf. {valeur}", { valeur: h.reference }) : ""].filter(Boolean).join(" · ")))),
        el("div", { class: "ligne-actions" },
          el("button", { class: "icone-btn", title: "Modifier", onclick: ev => { ev.stopPropagation(); editerHebergement(d, h); } }, icone("pencil")),
          el("button", { class: "icone-btn danger", title: "Supprimer", onclick: ev => {
            ev.stopPropagation(); d.hebergements.splice(d.hebergements.indexOf(h), 1); modifie(true); dessiner(); } }, icone("trash-2"))))))
        : el("div", { class: "vide" }, "Aucun hébergement pour l'instant."),
      el("div", { class: "rn-boutons" }, el("button", { class: "btn petit", onclick: () => editerHebergement(d, null) }, icone("plus"), "Ajouter un hébergement")));
  }

  function editerHebergement(d, heb) {
    const b = heb ? { ...heb } : { id: nouvelId(), nom: "", adresse: "", arrivee: d.depart, depart: d.retour || "", reference: "" };
    const champ = (lib, cle, attrs = {}) => el("label", { class: "champ" }, lib,
      el("input", { ...attrs, value: b[cle] || "", oninput: e => { b[cle] = e.target.value; } }));
    const valider = async () => {
      const avant = heb ? { ...heb } : null;
      if (heb) Object.assign(heb, b); else d.hebergements.push(b);
      if (!(await modifie(true))) return annuler(() => { if (heb) Object.assign(heb, avant); else d.hebergements.pop(); });
      fermer(); dessiner();
    };
    fenetre([
      el("h3", {}, heb ? "Hébergement" : "Nouvel hébergement"),
      champ("Nom de l'hébergement", "nom", { maxlength: 200 }),
      champ("Adresse", "adresse", { maxlength: 300 }),
      el("div", { class: "rn-deux" }, champ("Arrivée", "arrivee", { type: "date" }), champ("Départ", "depart", { type: "date" })),
      champ("Référence de réservation", "reference", { maxlength: 60 }),
      el("div", { class: "actions" },
        el("button", { class: "btn", onclick: fermer }, "Annuler"),
        el("button", { class: "btn principal", onclick: valider }, heb ? "Enregistrer" : "Ajouter"))]);
  }

  function blocDocuments(d) {
    const ajouter = async chemins => {
      const connus = new Set(d.documents.map(x => x.chemin.toLowerCase())), avant = d.documents.length;
      for (const c of chemins) if (c && !connus.has(c.toLowerCase())) d.documents.push({ chemin: c, nom: c.split(/[\\/]/).pop() || c });
      if (await modifie(true)) dessiner();
      else annuler(() => d.documents.splice(avant));
    };
    const action = (route, doc) => api("/api/reunions/document/" + route, { id: d.id, chemin: doc.chemin }).catch(erreur);
    return bloc("Documents", "paperclip",
      d.documents.length ? el("div", { class: "lignes" }, d.documents.map(doc => el("div", { class: "ligne cliquable", title: doc.chemin, onclick: () => action("ouvrir", doc) },
        el("span", { class: "ligne-ic" }, icone(/\.[a-z0-9]{1,5}$/i.test(doc.nom) ? "file-text" : "folder")),
        el("div", { class: "ligne-corps" },
          el("div", { class: "ligne-titre" }, el("span", {}, brut(doc.nom))),
          el("div", { class: "ligne-meta" }, brut(doc.chemin))),
        el("div", { class: "ligne-actions" },
          el("button", { class: "icone-btn", title: "Ouvrir", onclick: ev => { ev.stopPropagation(); action("ouvrir", doc); } }, icone("external-link")),
          el("button", { class: "icone-btn", title: "Afficher dans le dossier", onclick: ev => { ev.stopPropagation(); action("montrer", doc); } }, icone("folder-open")),
          el("button", { class: "icone-btn danger", title: "Retirer", onclick: ev => {
            ev.stopPropagation(); d.documents.splice(d.documents.indexOf(doc), 1); modifie(true); dessiner(); } }, icone("x"))))))
        : el("div", { class: "vide" }, "Aucun document lié.", el("br"), el("small", {}, "Billets, réservations, programme…")),
      el("div", { class: "rn-boutons" },
        el("button", { class: "btn petit", onclick: async () => {
          try { const r = await api("/api/reunions/document/choisir", { titre: t("Choisir les documents du déplacement") }); if (r.chemins.length) ajouter(r.chemins); }
          catch (e) { erreur(e); }
        } }, icone("file-plus"), "Ajouter des fichiers"),
        el("button", { class: "btn petit", onclick: async () => {
          const c = await choisirDossier("Choisir un dossier du déplacement"); if (c) ajouter([c]);
        } }, icone("folder-open"), "Ajouter un dossier")));
  }

  // ----------------------------------------------------- feuille de route
  async function feuilleDeRoute(d, entete) {
    let f;
    try { f = await api("/api/reunions/deplacement/feuille_de_route", { id: d.id }); }
    catch (e) { erreur(e); R.fiche.vue = "details"; return dessiner(); }
    if (R.fiche?.objet !== d || R.fiche.vue !== "feuille") return;
    const feuille = el("article", { class: "rn-feuille" },
      el("h3", {}, brut(f.titre)),
      el("div", { class: "rn-periode" }, brut(f.periode)),
      f.jours.map(j => [
        el("h4", {}, brut(j.libelle.charAt(0).toUpperCase() + j.libelle.slice(1))),
        j.evenements.map(e => el("div", { class: "rn-evt" },
          el("span", { class: "h" }, brut(e.heure)),
          el("span", { class: "i" }, icone(ICONES_TYPES[e.type] || "map-pin")),
          el("div", {}, el("div", { class: "t" }, brut(e.titre)), e.detail ? el("div", { class: "d" }, brut(e.detail)) : null)))]),
      d.documents.length ? [el("h4", {}, "Documents"), el("ul", {}, d.documents.map(doc => el("li", {}, brut(doc.nom))))] : null,
      d.controle.length ? [el("h4", {}, "Liste de contrôle"), el("ul", {}, d.controle.map(p =>
        el("li", { class: "rn-coche" }, icone(p.fait ? "square-check" : "square"), brut(p.texte))))] : null,
      f.budget ? [el("h4", {}, "Budget prévu"), el("p", { class: "rn-texte-libre" }, brut(f.budget))] : null,
      d.note ? [el("h4", {}, "Note"), el("p", { class: "rn-texte-libre" }, brut(d.note))] : null);
    const imprimer = () => {
      document.body.classList.add("rn-impression");
      addEventListener("afterprint", () => document.body.classList.remove("rn-impression"), { once: true });
      window.print();
    };
    // Copier et Imprimer avant l'agenda et la corbeille.
    const agenda = entete.querySelector(".btn:not(.discret)");
    entete.insertBefore(el("button", { class: "btn", onclick: () => copier(f.texte, "Feuille de route copiée") }, icone("copy"), "Copier"), agenda);
    entete.insertBefore(el("button", { class: "btn", onclick: imprimer }, icone("printer"), "Imprimer"), agenda);
    racine().replaceChildren(entete, feuille);
    etat(d.modifie ? "Enregistré" : "");
  }

  // ---------------------------------------------------- accueil, palette
  async function carteAccueil() {
    let p;
    try { p = await api("/api/reunions/accueil", {}); } catch { return null; }
    if (!p.reunion && !p.deplacement) return null;
    const auj = isoJour(new Date());
    const ouvrir = (genre, objet) => ev => { ev.stopPropagation(); montrerVue("reunions"); ouvrirFiche(genre, objet); };
    return el("div", { class: "carte-jour", onclick: () => montrerVue("reunions") },
      el("h4", {}, icone("presentation"), "Réunions et déplacements"),
      p.reunion ? el("div", { class: "ligne-jour", onclick: ouvrir("reunion", p.reunion) },
        el("span", { class: "heure" }, brut(p.reunion.debut.slice(0, 10) === auj ? hhmm(p.reunion.debut) : `${jourCourt(p.reunion.debut)} ${hhmm(p.reunion.debut)}`)),
        brut(p.reunion.titre)) : null,
      p.deplacement ? el("div", { class: "ligne-jour", onclick: ouvrir("deplacement", p.deplacement) },
        el("span", { class: "heure" }, icone("plane"), brut(p.deplacement.depart <= auj ? t("En cours") : jourCourt(p.deplacement.depart))),
        brut(p.deplacement.destination)) : null);
  }

  function commandes() {
    const liste = [
      { icone: icone("presentation"), titre: "Nouvelle réunion", detail: "Réunions et déplacements",
        action: () => { montrerVue("reunions"); R.fiche = null; R.onglet = "reunions"; dessinerListe(); nouvelleReunion(); } },
      { icone: icone("plane"), titre: "Nouveau déplacement", detail: "Réunions et déplacements",
        action: () => { montrerVue("reunions"); R.fiche = null; R.onglet = "deplacements"; dessinerListe(); nouveauDeplacement(); } },
    ];
    // Les prochaines réunions et les prochains déplacements déjà chargés.
    const maintenant = isoMinute(new Date()), auj = isoJour(new Date());
    for (const r of (R.donnees?.reunions || []).filter(r => r.fin >= maintenant).slice(0, 5)) {
      liste.push({ icone: icone("presentation"), titre: r.titre, detail: `${jourCourt(r.debut)} ${hhmm(r.debut)}`,
        action: () => { montrerVue("reunions"); ouvrirFiche("reunion", r); } });
    }
    for (const d of (R.donnees?.deplacements || []).filter(d => (d.retour || d.depart) >= auj).slice(0, 5)) {
      liste.push({ icone: icone("plane"), titre: d.destination, detail: jourMois(d.depart),
        action: () => { montrerVue("reunions"); ouvrirFiche("deplacement", d); } });
    }
    return liste;
  }

  VUES.reunions = {
    afficher,
    titre: "Réunions et déplacements",
    icone: icone("presentation"),
    groupe: "organisation",
    ordre: 20,
    description: "Réunions, comptes rendus, actions à suivre, déplacements et feuilles de route.",
    profils: ["assistant_direction", "assistant_virtuel", "freelance"],
    carteAccueil,
    commandes,
  };
  // La palette (Ctrl + K) propose les prochaines réunions dès le départ.
  charger().catch(() => {});
})();
