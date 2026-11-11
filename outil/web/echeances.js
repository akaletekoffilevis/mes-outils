"use strict";
/* Application « Échéances » : abonnements, contrats, assurances, noms de
   domaine, licences, loyers… tout ce qui se renouvelle ou expire
   (voir echeances.py). Lignes compactes par date, coûts ramenés au mois,
   filtres par catégorie, recherche, export CSV, rappels par la bulle. */
(() => {
  I18N.ajouter({
    "Échéances": "Due dates",
    "Abonnements, contrats, assurances, noms de domaine, loyers : tout ce qui se renouvelle ou expire, avec un rappel avant chaque échéance et avant la date limite de résiliation.":
      "Subscriptions, contracts, insurance, domain names, rent: everything that renews or expires, with a reminder before each due date and before the cancellation deadline.",
    "Nouvelle échéance": "New due date",
    "Modifier l'échéance": "Edit due date",
    "Exporter CSV": "Export CSV",
    "Pour Excel (séparateur « ; »)": "For Excel (“;” separator)",
    "Rechercher…": "Search…",
    "Toutes": "All",
    "Cette semaine": "This week",
    "Ce mois-ci": "This month",
    "Plus tard": "Later",
    "Résiliés et terminés": "Cancelled and completed",
    "Aucune échéance pour l'instant.": "No due dates yet.",
    "Ajoutez vos abonnements, contrats, assurances, noms de domaine… pour être prévenu avant chaque échéance.":
      "Add your subscriptions, contracts, insurance, domain names… to be reminded before each due date.",
    "Aucun résultat.": "No results.",
    "Coûts": "Costs",
    "Par mois": "Per month",
    "Par an": "Per year",
    "Ramenés au mois, abonnements actifs et à résilier.": "Converted to a monthly amount, active subscriptions and those to cancel.",
    "Aucun abonnement actif.": "No active subscription.",
    "Catégorie": "Category", "Fournisseur": "Provider", "Montant": "Amount", "Devise": "Currency",
    "Fréquence": "Frequency", "Tous les … mois": "Every … months", "Prochaine échéance": "Next due date",
    "Rappel (jours avant)": "Reminder (days before)", "Reconduction tacite": "Automatic renewal",
    "Préavis de résiliation (jours)": "Cancellation notice (days)", "Statut": "Status",
    "Moyen de paiement": "Payment method", "Espace client (adresse)": "Customer portal (address)",
    "Note": "Note", "Nom": "Name",
    "ex. Hébergement du site": "e.g. Website hosting",
    "ex. Carte pro (fin 1234), prélèvement": "e.g. Business card (ending 1234), direct debit",
    "Jamais le numéro complet d'une carte ou d'un compte.": "Never the full number of a card or account.",
    "Choisi dans vos contacts, ou texte libre": "Picked from your contacts, or free text",
    "Annuler": "Cancel", "Enregistrer": "Save", "Ajouter": "Add", "Supprimer": "Delete", "Modifier": "Edit",
    "Mensuelle": "Monthly", "Trimestrielle": "Quarterly", "Annuelle": "Yearly", "Tous les N mois": "Every N months",
    "Date unique": "One-off", "Mensuel": "Monthly", "Trimestriel": "Quarterly", "Annuel": "Yearly",
    "Actif": "Active", "À résilier": "To cancel", "Résilié": "Cancelled", "Terminé": "Done",
    "Logiciel": "Software", "Téléphone et Internet": "Phone and Internet", "Assurance": "Insurance",
    "Contrat": "Contract", "Nom de domaine": "Domain name", "Licence": "Licence", "Loyer": "Rent",
    "Énergie": "Energy", "Banque": "Bank", "Autre": "Other",
    "Payé / renouvelé": "Paid / renewed",
    "Ouvrir l'espace client": "Open customer portal",
    "Aujourd'hui": "Today", "Demain": "Tomorrow", "Hier": "Yesterday",
    "En retard d'un jour": "1 day overdue",
    "Tacite": "Auto-renewal",
    "Préavis dépassé": "Notice period passed",
    "Marquer à résilier": "Mark to cancel",
    "Marquer résilié": "Mark as cancelled",
    "Réactiver": "Reactivate",
    "Annuler le dernier paiement": "Undo last payment",
    "Derniers paiements": "Latest payments",
    "Aucun paiement enregistré.": "No payment recorded.",
    "Limite de résiliation": "Cancellation deadline",
    "Rappel": "Reminder",
    "Sans reconduction tacite": "No automatic renewal",
    "Supprimer cette échéance ?": "Delete this due date?",
    "Son historique de paiements disparaît aussi.": "Its payment history is deleted too.",
    "Échéance supprimée": "Due date deleted",
    "Échéance enregistrée": "Due date saved",
    "Échéance terminée": "Due date completed",
    "Paiement annulé": "Payment undone",
    "Statut modifié": "Status changed",
    "Coût mensuel": "Monthly cost",
    "Rien dans les 14 prochains jours.": "Nothing in the next 14 days.",
    "Ouvrir les échéances": "Open due dates",
    "0,00": "0.00",
    // Messages du serveur
    "Indiquez un nom.": "Enter a name.",
    "Catégorie inconnue.": "Unknown category.",
    "Fréquence inconnue.": "Unknown frequency.",
    "Indiquez la prochaine échéance.": "Enter the next due date.",
    "Date d'échéance invalide.": "Invalid due date.",
    "Devise invalide (code à trois lettres, ex. EUR).": "Invalid currency (three-letter code, e.g. EUR).",
    "Montant invalide.": "Invalid amount.",
    "Montant invalide : deux décimales au plus.": "Invalid amount: two decimals at most.",
    "Montant trop élevé.": "Amount too high.",
    "Statut inconnu.": "Unknown status.",
    "N'indiquez jamais de numéro de carte ou de compte : par exemple « Carte pro (fin 1234) ».":
      "Never enter a card or account number: for example “Business card (ending 1234)”.",
    "Lien invalide : il doit commencer par https://": "Invalid link: it must start with https://",
    "Échéance introuvable.": "Due date not found.",
    "Cette échéance n'est plus active.": "This due date is no longer active.",
    "Aucun paiement à annuler.": "No payment to undo.",
    "Nombre de mois invalide.": "Invalid number of months.",
    "Préavis invalide.": "Invalid notice period.",
    "Rappel invalide.": "Invalid reminder.",
  });
  I18N.ajouter({
    "Dans {n} jours": "In {n} days",
    "En retard de {n} jours": "{n} days overdue",
    "Prochaine échéance : {date}": "Next due date: {date}",
    "Résilier avant le {date}": "Cancel by {date}",
    "Tous les {n} mois": "Every {n} months",
    "{n} jours avant": "{n} days before",
    "{n} jours de préavis": "{n} days' notice",
    "Marquer payé : {nom}": "Mark as paid: {nom}",
  });
  I18N.motifs([
    [/^Nombre de mois : de (\d+) à (\d+)\.$/, "Number of months: $1 to $2."],
    [/^Préavis : de (\d+) à (\d+)\.$/, "Notice period: $1 to $2."],
    [/^Rappel : de (\d+) à (\d+)\.$/, "Reminder: $1 to $2."],
  ]);

  const CATEGORIES = {
    logiciel: ["Logiciel", "app-window"], telephonie: ["Téléphone et Internet", "smartphone"],
    assurance: ["Assurance", "shield"], contrat: ["Contrat", "file-text"], domaine: ["Nom de domaine", "globe"],
    licence: ["Licence", "key-round"], loyer: ["Loyer", "house"], energie: ["Énergie", "zap"],
    banque: ["Banque", "landmark"], autre: ["Autre", "tag"],
  };
  const FREQUENCES = { mensuelle: "Mensuelle", trimestrielle: "Trimestrielle", annuelle: "Annuelle", mois: "Tous les N mois", unique: "Date unique" };
  const STATUTS = { actif: "Actif", a_resilier: "À résilier", resilie: "Résilié", termine: "Terminé" };
  const GROUPES = [["semaine", "Cette semaine"], ["mois", "Ce mois-ci"], ["plus_tard", "Plus tard"], ["resilies", "Résiliés et terminés"]];
  const DEVISES = ["EUR", "USD", "GBP", "CHF", "CAD", "MGA", "XOF", "MAD", "TND"];
  const E = { r: null, filtre: "toutes", recherche: "", ouverts: new Set(), contacts: [] };

  const style = document.createElement("style");
  style.textContent = `
    .ech-corps { display: grid; grid-template-columns: minmax(0, 1fr) 290px; gap: 18px; align-items: start; }
    @media (max-width: 1050px) { .ech-corps { grid-template-columns: 1fr; } }
    .ech-filtres { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin: 0 0 14px; }
    .ech-filtres .espace { flex: 1; }
    .ech-liste .titre-lignes { display: flex; justify-content: space-between; }
    .ech-liste .titre-lignes span:last-child { font-variant-numeric: tabular-nums; }
    .ech-liste .ligne { cursor: pointer; }
    .ech-liste .ligne.eteinte .ligne-titre, .ech-liste .ligne.eteinte .ech-montant { color: var(--gris); }
    .ech-liste .ligne-actions { width: 94px; justify-content: flex-end; }
    .ech-quand { display: flex; flex-direction: column; align-items: flex-end; min-width: 150px; line-height: 1.35; }
    .ech-date { font-size: 12px; color: var(--gris); font-variant-numeric: tabular-nums; }
    .ech-montant { min-width: 96px; text-align: right; color: var(--encre); font-weight: 500; font-variant-numeric: tabular-nums; }
    .ech-detail { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 10px 22px; font-size: 13px; }
    .ech-detail .lib { font-size: 11.5px; color: var(--gris); margin-bottom: 1px; }
    .ech-detail .val { color: var(--encre); overflow-wrap: anywhere; }
    .ech-detail .large { grid-column: 1 / -1; }
    .ech-detail .note { white-space: pre-wrap; color: var(--doux); }
    .ech-historique { display: flex; flex-wrap: wrap; gap: 4px 14px; color: var(--doux); font-variant-numeric: tabular-nums; }
    .ech-boutons { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 12px; }
    .ech-couts h3 { margin: 0 0 2px; font-size: 13px; font-weight: 600; }
    .ech-couts .aide { color: var(--gris); font-size: 12px; margin: 0 0 12px; }
    .ech-devise + .ech-devise { border-top: 1px solid var(--ligne); margin-top: 14px; padding-top: 14px; }
    .ech-totaux { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; }
    .ech-totaux .lib { font-size: 11.5px; color: var(--gris); }
    .ech-totaux .grand { font-size: 19px; font-weight: 500; letter-spacing: -.01em; font-variant-numeric: tabular-nums; }
    .ech-cat { display: grid; grid-template-columns: minmax(0, 1fr) auto auto; gap: 10px; align-items: center; padding: 5px 0; font-size: 13px; border-top: 1px solid var(--ligne); }
    .ech-cat .nom { display: flex; align-items: center; gap: 7px; min-width: 0; color: var(--doux); }
    .ech-cat .nom span { overflow-wrap: anywhere; line-height: 1.3; }
    .ech-cat .nom svg.ico { color: var(--gris); }
    .ech-cat .m { font-variant-numeric: tabular-nums; text-align: right; }
    .ech-cat .a { font-variant-numeric: tabular-nums; text-align: right; color: var(--gris); min-width: 82px; }
    .ech-grille { display: grid; grid-template-columns: 1fr 1fr; gap: 0 12px; }
    .ech-grille .large { grid-column: 1 / -1; }
    .ech-case { display: flex; align-items: center; gap: 8px; font-size: 13.5px; color: var(--encre); cursor: pointer; margin: 22px 0 14px; }
    .ech-case input { width: 16px; height: 16px; margin: 0; }
    .ech-carte .ligne-jour .heure { min-width: 54px; }
    .ech-carte .ligne-jour .nom { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .ech-carte .ligne-jour .mt { color: var(--doux); font-variant-numeric: tabular-nums; }
    .ech-carte .total { margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--ligne); font-size: 12.5px; color: var(--doux); }
    .ech-carte .total b { color: var(--encre); font-weight: 500; font-variant-numeric: tabular-nums; }
  `;
  document.head.append(style);

  // --------------------------------------------------------------- outils
  const racine = () => $("#vue-echeances");
  function jourIso(iso) { return new Date(iso + "T00:00"); }
  function dateCourte(iso) {
    const d = jourIso(iso), auj = E.r ? jourIso(E.r.aujourdhui) : new Date();
    const opts = { day: "numeric", month: "short" };
    if (d.getFullYear() !== auj.getFullYear()) opts.year = "numeric";
    return d.toLocaleDateString(I18N.locale(), opts);
  }
  function dateLongue(iso) {
    return jourIso(iso).toLocaleDateString(I18N.locale(), { day: "numeric", month: "long", year: "numeric" });
  }
  /** Centimes entiers → texte monétaire de la langue choisie. */
  function argent(centimes, devise) {
    const valeur = centimes / 100;
    try { return new Intl.NumberFormat(I18N.locale(), { style: "currency", currency: devise, minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(valeur); }
    catch { return valeur.toFixed(2) + " " + devise; }
  }
  function frequence(x) {
    return x.frequence === "mois" ? t("Tous les {n} mois", { n: x.mois }) : t(FREQUENCES[x.frequence]);
  }
  function libCategorie(c) { return (CATEGORIES[c] || CATEGORIES.autre)[0]; }
  function icCategorie(c) { return icone((CATEGORIES[c] || CATEGORIES.autre)[1]); }
  function dansJours(n) {
    if (n === 0) return t("Aujourd'hui");
    if (n === 1) return t("Demain");
    if (n === -1) return t("En retard d'un jour");
    return n < 0 ? t("En retard de {n} jours", { n: -n }) : t("Dans {n} jours", { n });
  }
  /** L'état affiché d'une fiche : [texte, couleur]. La couleur est réservée aux états. */
  function etat(x) {
    if (x.statut === "resilie" || x.statut === "termine") return [t(STATUTS[x.statut]), "gris"];
    if (x.statut === "a_resilier" && x.jours_limite !== null) {
      if (x.jours_limite < 0) return [t("Préavis dépassé"), "rouge"];
      return [t("Résilier avant le {date}", { date: dateCourte(x.limite_resiliation) }), "ambre"];
    }
    if (x.jours < 0) return [dansJours(x.jours), "rouge"];
    if (x.jours_limite !== null && x.jours_limite >= 0 && x.jours_limite <= x.rappel_jours)
      return [t("Résilier avant le {date}", { date: dateCourte(x.limite_resiliation) }), "ambre"];
    if (x.statut === "a_resilier") return [t("À résilier"), "ambre"];
    return [dansJours(x.jours), x.jours <= x.rappel_jours ? "ambre" : "gris"];
  }
  const sansAccents = s => (s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  function correspond(x) {
    if (E.filtre !== "toutes" && x.categorie !== E.filtre) return false;
    const q = sansAccents(E.recherche.trim());
    if (!q) return true;
    return sansAccents([x.nom, x.fournisseur, x.note, x.paiement, t(libCategorie(x.categorie))].join(" ")).includes(q);
  }

  // -------------------------------------------------------------- données
  async function charger() {
    E.r = await api("/api/echeances/liste", {});
    dessiner();
  }
  const recharger = () => charger().catch(e => toast(e.message, "erreur"));

  /** Les contacts (application Contacts), s'ils existent : sinon texte libre. */
  async function chargerContacts() {
    try {
      const r = await api("/api/contacts/liste", {});
      E.contacts = (r.contacts || []).filter(c => c && (c.entreprise || c.nom)).slice(0, 500);
    } catch { E.contacts = []; }
  }
  const nomContact = c => c.entreprise || c.nom;

  // -------------------------------------------------------------- dessin
  function dessiner() {
    const vue = racine();
    if (!vue || !E.r) return;
    const tous = E.r.elements;
    const lesPuces = tous.length ? puces() : null;
    const recherche = el("input", { type: "search", placeholder: "Rechercher…", value: E.recherche,
      oninput: ev => { E.recherche = ev.target.value; dessinerListe(); } });
    vue.replaceChildren(
      el("div", { class: "barre-vue" },
        el("h2", {}, icone("calendar-clock"), "Échéances"),
        el("div", { class: "espace" }),
        tous.length ? el("label", { class: "champ-recherche" }, el("span", {}, icone("search")), recherche) : null,
        tous.length ? el("button", { class: "btn", title: "Pour Excel (séparateur « ; »)", onclick: exporter }, icone("download"), "Exporter CSV") : null,
        el("button", { class: "btn principal", onclick: () => editer(null) }, icone("plus"), "Nouvelle échéance")),
      tous.length
        ? el("div", { class: "ech-corps" },
            el("div", {},
              lesPuces ? el("div", { class: "ech-filtres" }, lesPuces) : null,
              el("div", { id: "ech-liste", class: "ech-liste" })),
            panneauCouts())
        : el("div", { class: "vide" }, icone("calendar-clock"),
            el("div", { style: "font-weight:500;color:var(--encre)" }, "Aucune échéance pour l'instant."),
            el("div", { style: "margin:4px 0 14px" }, "Ajoutez vos abonnements, contrats, assurances, noms de domaine… pour être prévenu avant chaque échéance."),
            el("button", { class: "btn principal", onclick: () => editer(null) }, icone("plus"), "Nouvelle échéance")));
    dessinerListe();
  }

  function puces() {
    const presentes = Object.keys(CATEGORIES).filter(c => E.r.elements.some(x => x.categorie === c));
    if (presentes.length < 2) { E.filtre = "toutes"; return null; }
    if (E.filtre !== "toutes" && !presentes.includes(E.filtre)) E.filtre = "toutes";
    return el("div", { class: "puces" },
      [["toutes", "Toutes"], ...presentes.map(c => [c, libCategorie(c)])].map(([v, lib]) =>
        el("button", { class: "puce" + (E.filtre === v ? " actif" : ""), onclick: () => { E.filtre = v; dessiner(); } }, lib)));
  }

  function dessinerListe() {
    const zone = $("#ech-liste");
    if (!zone) return;
    const choisis = E.r.elements.filter(correspond);
    if (!choisis.length) { zone.replaceChildren(el("div", { class: "vide" }, icone("search"), "Aucun résultat.")); return; }
    zone.replaceChildren(...GROUPES.map(([g, titre]) => {
      const liste = choisis.filter(x => x.groupe === g);
      if (!liste.length) return null;
      return el("div", { class: "lignes" },
        el("div", { class: "titre-lignes" }, el("span", {}, titre), el("span", {}, String(liste.length))),
        liste.map(ligne));
    }));
  }

  function ligne(x) {
    const ouverte = E.ouverts.has(x.id);
    const [texteEtat, couleur] = etat(x);
    const actif = x.statut === "actif" || x.statut === "a_resilier";
    const meta = [x.fournisseur, frequence(x), x.paiement].filter(Boolean).join(" · ");
    const stop = f => ev => { ev.stopPropagation(); f(); };
    const corps = el("div", { class: "ligne" + (ouverte ? " ouverte" : "") + (actif ? "" : " eteinte"),
      onclick: () => { ouverte ? E.ouverts.delete(x.id) : E.ouverts.add(x.id); dessinerListe(); } },
      el("span", { class: "ligne-ic", title: libCategorie(x.categorie) }, icCategorie(x.categorie)),
      el("div", { class: "ligne-corps" },
        el("div", { class: "ligne-titre" }, el("span", {}, x.nom),
          x.tacite ? el("span", { class: "tag", title: "Reconduction tacite" }, "Tacite") : null),
        el("div", { class: "ligne-meta" }, meta)),
      el("div", { class: "ligne-cote" },
        el("div", { class: "ech-quand" },
          el("span", { class: "etat-txt " + couleur }, texteEtat),
          el("span", { class: "ech-date" }, dateCourte(x.prochaine))),
        el("span", { class: "ech-montant" }, argent(x.montant_centimes, x.devise))),
      el("div", { class: "ligne-actions" },
        actif ? el("button", { class: "icone-btn go", title: "Payé / renouvelé", onclick: stop(() => payer(x)) }, icone("check")) : null,
        el("button", { class: "icone-btn", title: "Modifier", onclick: stop(() => editer(x)) }, icone("pencil")),
        el("button", { class: "icone-btn danger", title: "Supprimer", onclick: stop(() => supprimer(x)) }, icone("trash-2"))));
    return ouverte ? [corps, detail(x)] : corps;
  }

  function detail(x) {
    const champ = (lib, val, classe = "") => val ? el("div", { class: classe }, el("div", { class: "lib" }, lib), el("div", { class: "val" }, val)) : null;
    const historique = (x.historique || []).slice(-6).reverse();
    const statuts = [];
    if (x.statut === "actif") statuts.push(["a_resilier", "Marquer à résilier", "circle-alert"]);
    if (x.statut === "actif" || x.statut === "a_resilier") statuts.push(["resilie", "Marquer résilié", "circle-x"]);
    if (x.statut !== "actif") statuts.push(["actif", "Réactiver", "undo-2"]);
    return el("div", { class: "ligne-detail" },
      el("div", { class: "ech-detail" },
        champ("Prochaine échéance", dateLongue(x.prochaine)),
        champ("Fréquence", frequence(x)),
        champ("Catégorie", libCategorie(x.categorie)),
        champ("Coût mensuel", x.cout_mensuel_centimes ? argent(x.cout_mensuel_centimes, x.devise) : null),
        champ("Reconduction tacite", x.tacite
          ? t("{n} jours de préavis", { n: x.preavis_jours }) + " · " + t("Résilier avant le {date}", { date: dateLongue(x.limite_resiliation) })
          : (x.frequence === "unique" ? null : t("Sans reconduction tacite"))),
        champ("Rappel", t("{n} jours avant", { n: x.rappel_jours })),
        champ("Statut", t(STATUTS[x.statut])),
        champ("Moyen de paiement", x.paiement),
        champ("Espace client (adresse)", x.lien ? el("a", { href: x.lien, target: "_blank", rel: "noopener" }, x.lien.replace(/^https?:\/\//, "")) : null),
        x.note ? el("div", { class: "large" }, el("div", { class: "lib" }, "Note"), el("div", { class: "note" }, x.note)) : null,
        el("div", { class: "large" }, el("div", { class: "lib" }, "Derniers paiements"),
          historique.length
            ? el("div", { class: "ech-historique" }, historique.map(h =>
                el("span", {}, dateCourte(h.echeance) + " · " + argent(h.montant_centimes, x.devise))))
            : el("div", { class: "val", style: "color:var(--gris)" }, "Aucun paiement enregistré."))),
      el("div", { class: "ech-boutons" },
        x.lien ? el("button", { class: "btn petit", onclick: () => window.open(x.lien, "_blank", "noopener") }, icone("external-link"), "Ouvrir l'espace client") : null,
        statuts.map(([s, lib, ic]) => el("button", { class: "btn petit", onclick: () => changerStatut(x, s) }, icone(ic), lib)),
        historique.length ? el("button", { class: "btn petit discret", onclick: () => annulerPaiement(x) }, icone("undo-2"), "Annuler le dernier paiement") : null));
  }

  function panneauCouts() {
    const devises = Object.entries(E.r.couts);
    return el("div", { class: "carte ech-couts" },
      el("h3", {}, "Coûts"),
      el("p", { class: "aide" }, "Ramenés au mois, abonnements actifs et à résilier."),
      devises.length
        ? devises.map(([devise, c]) => el("div", { class: "ech-devise" },
            el("div", { class: "ech-totaux" },
              el("div", {}, el("div", { class: "lib" }, "Par mois"), el("div", { class: "grand" }, argent(c.mensuel, devise))),
              el("div", {}, el("div", { class: "lib" }, "Par an"), el("div", { class: "grand" }, argent(c.annuel, devise)))),
            c.categories.map(k => el("div", { class: "ech-cat" },
              el("div", { class: "nom", title: libCategorie(k.categorie) }, icCategorie(k.categorie), el("span", {}, libCategorie(k.categorie))),
              el("div", { class: "m" }, argent(k.mensuel, devise)),
              el("div", { class: "a" }, argent(k.annuel, devise))))))
        : el("div", { style: "color:var(--gris);font-size:13px" }, "Aucun abonnement actif."));
  }

  // ------------------------------------------------------------- actions
  async function payer(x) {
    try {
      const r = await api("/api/echeances/payer", { id: x.id });
      toast(r.statut === "termine" ? "Échéance terminée" : t("Prochaine échéance : {date}", { date: dateLongue(r.prochaine) }), "succes", 2200);
      recharger();
    } catch (e) { toast(e.message, "erreur"); }
  }

  async function annulerPaiement(x) {
    try { await api("/api/echeances/annuler_paiement", { id: x.id }); toast("Paiement annulé", "succes", 1600); recharger(); }
    catch (e) { toast(e.message, "erreur"); }
  }

  async function changerStatut(x, statut) {
    try { await api("/api/echeances/statut", { id: x.id, statut }); toast("Statut modifié", "succes", 1400); recharger(); }
    catch (e) { toast(e.message, "erreur"); }
  }

  async function supprimer(x) {
    if (!(await confirmer(icone("trash-2"), "Supprimer cette échéance ?", "Son historique de paiements disparaît aussi.", "Supprimer"))) return;
    try { await api("/api/echeances/supprimer", { id: x.id }); E.ouverts.delete(x.id); toast("Échéance supprimée"); recharger(); }
    catch (e) { toast(e.message, "erreur"); }
  }

  async function exporter() {
    try {
      const r = await api("/api/echeances/export", {});
      const lien = el("a", { href: URL.createObjectURL(new Blob([r.csv], { type: "text/csv;charset=utf-8" })), download: r.nom });
      document.body.append(lien); lien.click(); lien.remove();
      setTimeout(() => URL.revokeObjectURL(lien.href), 5000);
    } catch (e) { toast(e.message, "erreur"); }
  }

  function editer(x) {
    const derniereDevise = E.r?.elements?.at(-1)?.devise || "EUR";
    const b = x ? { ...x } : { nom: "", categorie: "logiciel", fournisseur: "", montant: "", devise: derniereDevise, frequence: "mensuelle",
      mois: 2, prochaine: E.r?.aujourdhui || "", tacite: false, preavis_jours: 30, rappel_jours: 7, statut: "actif", paiement: "", lien: "", note: "" };
    const champ = (lib, entree, classe = "", aide = null) => el("label", { class: "champ " + classe }, lib, entree, aide ? el("small", {}, aide) : null);
    const options = (dico, choisi) => Object.entries(dico).map(([v, lib]) =>
      el("option", { value: v, selected: v === choisi ? "" : null }, Array.isArray(lib) ? lib[0] : lib));
    const nom = el("input", { value: b.nom, maxlength: 80, placeholder: "ex. Hébergement du site" });
    const categorie = el("select", {}, options(CATEGORIES, b.categorie));
    const fournisseur = el("input", { value: b.fournisseur || "", maxlength: 120, list: "ech-contacts",
      placeholder: E.contacts.length ? "Choisi dans vos contacts, ou texte libre" : "" });
    const montant = el("input", { value: x ? String(b.montant).replace(".", I18N.langue === "en" ? "." : ",") : "", inputmode: "decimal", placeholder: "0,00" });
    const devise = el("input", { value: b.devise, maxlength: 3, list: "ech-devises", style: "text-transform:uppercase" });
    const freq = el("select", {}, options(FREQUENCES, b.frequence));
    const mois = el("input", { type: "number", min: 1, max: 120, value: b.mois || 2 });
    const champMois = champ("Tous les … mois", mois);
    const prochaine = el("input", { type: "date", value: b.prochaine });
    const rappel = el("input", { type: "number", min: 0, max: 365, value: b.rappel_jours ?? 7 });
    const tacite = el("input", { type: "checkbox", checked: b.tacite ? "" : null });
    const caseTacite = el("label", { class: "ech-case" }, tacite, "Reconduction tacite");
    const preavis = el("input", { type: "number", min: 0, max: 730, value: b.preavis_jours || (x ? 0 : 30) });
    const champPreavis = champ("Préavis de résiliation (jours)", preavis);
    const statut = el("select", {}, options(STATUTS, b.statut));
    const paiement = el("input", { value: b.paiement || "", maxlength: 120, placeholder: "ex. Carte pro (fin 1234), prélèvement" });
    const lien = el("input", { type: "url", value: b.lien || "", maxlength: 400, placeholder: "https://" });
    const note = el("textarea", { rows: 3, maxlength: 1000, value: b.note || "" });
    const majVisibles = () => {
      champMois.hidden = freq.value !== "mois";
      caseTacite.hidden = freq.value === "unique";
      champPreavis.hidden = freq.value === "unique" || !tacite.checked;
    };
    freq.addEventListener("change", majVisibles);
    tacite.addEventListener("change", majVisibles);
    majVisibles();
    const valider = async () => {
      const nomF = fournisseur.value.trim();
      const contact = E.contacts.find(c => nomContact(c) === nomF);
      const element = { id: x?.id, nom: nom.value, categorie: categorie.value, fournisseur: nomF, contact_id: contact ? contact.id : null,
        montant: montant.value, devise: devise.value, frequence: freq.value, mois: freq.value === "mois" ? mois.value : null,
        prochaine: prochaine.value, tacite: freq.value !== "unique" && tacite.checked, preavis_jours: preavis.value, rappel_jours: rappel.value,
        statut: statut.value, paiement: paiement.value, lien: lien.value, note: note.value };
      try {
        await api("/api/echeances/enregistrer", { element });
        fermer(); toast("Échéance enregistrée", "succes", 1600); recharger();
      } catch (e) { toast(e.message, "erreur"); }
    };
    fenetre([
      el("h3", {}, x ? "Modifier l'échéance" : "Nouvelle échéance"),
      el("div", { class: "ech-grille" },
        champ("Nom", nom, "large"),
        champ("Catégorie", categorie), champ("Fournisseur", fournisseur),
        champ("Montant", montant), champ("Devise", devise),
        champ("Fréquence", freq), champMois,
        champ("Prochaine échéance", prochaine), champ("Rappel (jours avant)", rappel),
        caseTacite, champPreavis,
        champ("Statut", statut), champ("Moyen de paiement", paiement, "", "Jamais le numéro complet d'une carte ou d'un compte."),
        champ("Espace client (adresse)", lien, "large"),
        champ("Note", note, "large")),
      el("datalist", { id: "ech-contacts" }, E.contacts.map(c => el("option", { value: nomContact(c) }))),
      el("datalist", { id: "ech-devises" }, DEVISES.map(d => el("option", { value: d }))),
      el("div", { class: "actions" },
        el("button", { class: "btn", onclick: fermer }, "Annuler"),
        el("button", { class: "btn principal", onclick: valider }, x ? "Enregistrer" : "Ajouter"))]);
    setTimeout(() => nom.focus(), 60);
  }

  // ------------------------------------------------------ accueil, palette
  async function carteAccueil() {
    let r;
    try { r = await api("/api/echeances/accueil", {}); } catch { return null; }
    const devises = Object.entries(r.couts || {});
    if (!r.prochaines.length && !devises.length) return null;
    const auj = new Date();
    const court = iso => {
      const d = jourIso(iso);
      return d.toLocaleDateString(I18N.locale(), d.getFullYear() === auj.getFullYear() ? { day: "numeric", month: "short" } : { day: "numeric", month: "short", year: "2-digit" });
    };
    return el("div", { class: "carte-jour ech-carte", onclick: () => montrerVue("echeances") },
      el("h4", {}, icone("calendar-clock"), "Échéances"),
      r.prochaines.length
        ? r.prochaines.map(x => el("div", { class: "ligne-jour" },
            el("span", { class: "heure", style: x.jours < 0 ? "color:var(--rouge-texte)" : "" }, court(x.prochaine)),
            el("span", { class: "nom" }, x.nom),
            el("span", { class: "mt" }, argent(x.montant_centimes, x.devise))))
        : el("div", { class: "rien" }, "Rien dans les 14 prochains jours."),
      devises.length ? el("div", { class: "total" }, t("Coût mensuel") + " ",
        el("b", {}, devises.map(([d, c]) => argent(c.mensuel, d)).join(" · "))) : null);
  }

  function commandes() {
    const liste = [{ icone: icone("plus"), titre: "Nouvelle échéance", detail: "Échéances",
      action: () => { montrerVue("echeances"); setTimeout(() => editer(null), 80); } }];
    for (const x of (E.r?.elements || []).filter(x => x.groupe === "semaine" && (x.statut === "actif" || x.statut === "a_resilier")).slice(0, 5)) {
      liste.push({ icone: icone("check"), titre: t("Marquer payé : {nom}", { nom: x.nom }),
        detail: dateCourte(x.prochaine) + " · " + argent(x.montant_centimes, x.devise), action: () => payer(x) });
    }
    return liste;
  }

  VUES.echeances = {
    afficher: async () => { await chargerContacts(); recharger(); },
    titre: "Échéances", icone: icone("calendar-clock"), groupe: "organisation", ordre: 30,
    description: "Abonnements, contrats, assurances, noms de domaine, loyers : tout ce qui se renouvelle ou expire, avec un rappel avant chaque échéance et avant la date limite de résiliation.",
    profils: ["freelance", "assistant_virtuel", "assistant_direction", "developpeur"],
    carteAccueil, commandes,
  };
  // La palette (Ctrl + K) propose les échéances de la semaine dès le démarrage.
  api("/api/echeances/liste", {}).then(r => { if (!E.r) E.r = r; }).catch(() => {});
})();
