"use strict";
/* Application « Dépenses et notes de frais » (voir depenses.py) : tableau de
   bord, dépenses par mois, charges fixes automatiques, budget, épargne
   (reprise confirmée en cas de dépassement), statistiques, notes de frais
   (justificatif, client refacturable, statut, export CSV), réglages.
   Les montants arrivent du serveur en texte (« 12.50 ») : la page ne fait
   que les afficher, tous les calculs sont faits côté PC en Decimal. */
(() => {
  I18N.ajouter({
    "Dépenses": "Expenses",
    "Dépenses et notes de frais": "Expenses and expense reports",
    "Budget du mois, charges fixes, épargne, statistiques et notes de frais avec justificatifs.":
      "Monthly budget, fixed costs, savings, statistics and expense reports with receipts.",
    "Tableau de bord": "Dashboard", "Charges fixes": "Fixed costs", "Budget": "Budget", "Épargne": "Savings",
    "Statistiques": "Statistics", "Notes de frais": "Expense reports", "Réglages": "Settings",
    "Ajouter une dépense": "Add an expense", "Nouvelle dépense": "New expense", "Modifier la dépense": "Edit expense",
    "Nouvelle charge fixe": "New fixed cost", "Modifier la charge fixe": "Edit fixed cost",
    "Alimentation": "Food", "Transport": "Transport", "Logement": "Housing", "Santé": "Health", "Loisirs": "Leisure",
    "Shopping": "Shopping", "Abonnements": "Subscriptions", "Éducation": "Education",
    "Autres": "Others", "Sans catégorie": "No category",
    "Carte bancaire": "Card", "Espèces": "Cash", "Virement": "Bank transfer", "PayPal": "PayPal",
    "Mobile Money": "Mobile Money", "Autre": "Other",
    "À rembourser": "To be reimbursed", "Remboursée": "Reimbursed", "Refacturée": "Re-invoiced",
    "Remboursées": "Reimbursed", "Refacturées": "Re-invoiced", "Toutes": "All",
    "Sur la bonne voie": "On track", "À surveiller": "Keep an eye on it", "Presque atteint": "Almost reached",
    "Budget dépassé": "Budget exceeded",
    "Tout va bien, vos dépenses restent maîtrisées.": "All good, your spending is under control.",
    "Vous avez utilisé une bonne partie du budget, gardez un œil dessus.": "You have used a good part of the budget, keep an eye on it.",
    "Le budget est presque atteint. Encore un petit effort jusqu'à la fin du mois.": "The budget is almost reached. A little more effort until the end of the month.",
    "Le budget est dépassé ce mois-ci. Ce n'est pas grave, il repart à zéro le mois prochain.": "The budget is exceeded this month. Don't worry, it starts again from zero next month.",
    "Dépensé ce mois-ci": "Spent this month", "Dépensé": "Spent",
    "sur {budget}": "of {budget}", "dont {montant} de charges fixes": "including {montant} of fixed costs",
    "{montant} couverts par l'épargne": "{montant} covered by savings",
    "{pct} utilisé": "{pct} used", "{montant} restants": "{montant} left", "{montant} au-delà": "{montant} over",
    "Fixez-vous un objectif": "Set yourself a goal",
    "Un budget mensuel vous aide à savoir où vous en êtes en un coup d'œil.": "A monthly budget shows you where you stand at a glance.",
    "Définir un budget": "Set a budget", "Budget mensuel": "Monthly budget",
    "Reconduit chaque mois tant qu'il n'est pas modifié. 0 : pas de budget.": "Carried over every month until changed. 0: no budget.",
    "Budget enregistré": "Budget saved",
    "Restant": "Left", "Dépassement": "Overrun", "Par jour restant": "Per remaining day",
    "Projection fin de mois": "End-of-month projection", "au rythme actuel": "at the current pace",
    "{n} jours restants": "{n} days left", "1 jour restant": "1 day left",
    "Historique": "History", "6 derniers mois": "Last 6 months", "12 derniers mois": "Last 12 months",
    "Dépenses variables": "Variable expenses", "{n} par mois": "{n} per month", "Aucune pour l'instant": "None yet",
    "{n} ce mois-ci": "{n} this month", "{montant} disponibles": "{montant} available", "Créer mon épargne": "Start saving",
    "Mise de côté chaque mois, à n'utiliser qu'en cas d'imprévu": "Set aside every month, only for emergencies",
    "{montant} épargnés ce mois-ci": "{montant} saved this month",
    "{montant} épargnés ce mois-ci, {repris} repris": "{montant} saved this month, {repris} taken back",
    "{montant} repris ce mois-ci, au-delà de l'épargne du mois": "{montant} taken back this month, beyond this month's savings",
    "Notes de frais à rembourser": "Expense reports to be reimbursed", "Rien à rembourser": "Nothing to reimburse",
    "{n} notes de frais": "{n} expense reports", "1 note de frais": "1 expense report",
    "Dernières dépenses": "Latest expenses", "Tout voir": "See all", "Par catégorie": "By category", "Ce mois-ci": "This month",
    "Pas encore de dépenses.": "No expenses yet.",
    "Pour commencer": "Getting started",
    "Ajoutez vos charges fixes (loyer, abonnements…) : elles reviendront toutes seules chaque mois.": "Add your fixed costs (rent, subscriptions…): they come back on their own every month.",
    "Ajoutez une dépense du quotidien en quelques secondes.": "Add an everyday expense in a few seconds.",
    "Fixez un budget mensuel pour savoir où vous en êtes.": "Set a monthly budget to know where you stand.",
    "Ajouter une charge fixe": "Add a fixed cost",
    "Aucune dépense ce mois-ci pour l'instant. Ajoutez-en une en quelques secondes.": "No expenses this month yet. Add one in a few seconds.",
    "Vous avez dépassé votre budget de {montant}. Pas de panique, le mois prochain repart à zéro.": "You have exceeded your budget by {montant}. Don't panic, next month starts from zero.",
    "Il vous reste {reste} pour le mois, soit environ {jour} par jour.": "You have {reste} left for the month, about {jour} per day.",
    "Vous avez utilisé {pct} % de votre budget. Il vous reste {reste}.": "You have used {pct}% of your budget. You have {reste} left.",
    "Vos dépenses variables sont {pct} % plus faibles que le mois dernier à la même date.": "Your variable expenses are {pct}% lower than last month at the same date.",
    "Vos dépenses variables sont {pct} % plus élevées que le mois dernier à la même date.": "Your variable expenses are {pct}% higher than last month at the same date.",
    "Vos dépenses variables sont stables par rapport au mois dernier.": "Your variable expenses are stable compared with last month.",
    "Votre principale catégorie de dépenses est « {cat} ».": "Your main spending category is “{cat}”.",
    "Rechercher dans tous les mois…": "Search all months…", "Toutes les catégories": "All categories",
    "Plus récent": "Newest", "Plus ancien": "Oldest", "Montant décroissant": "Amount, high to low", "Montant croissant": "Amount, low to high",
    "Pro seulement": "Business only", "Export CSV": "CSV export",
    "Pour Excel (séparateur « ; »)": "For Excel (“;” separator)",
    "{n} dépenses": "{n} expenses", "1 dépense": "1 expense", "Résultats dans tous les mois": "Results from all months",
    "Aucune dépense ce mois-ci.": "No expenses this month.", "Aucun résultat.": "No results.",
    "Mois précédent": "Previous month", "Mois suivant": "Next month",
    "Charge fixe": "Fixed cost", "Pro": "Business", "Justificatif": "Receipt",
    "{montant} pris sur l'épargne": "{montant} taken from savings",
    "Ouvrir le justificatif": "Open the receipt", "Montant": "Amount", "Catégorie": "Category",
    "Description (facultatif)": "Description (optional)", "Nom de la charge": "Name of the cost",
    "ex. Courses de la semaine": "e.g. Weekly groceries", "Loyer, Internet, Assurance…": "Rent, Internet, Insurance…",
    "Date": "Date", "Jour du mois": "Day of the month", "Le {n}": "On the {n}", "Paiement": "Payment",
    "Note (facultatif)": "Note (optional)", "Un détail à retenir…": "A detail to remember…",
    "Ajoutée automatiquement chaque mois": "Added automatically every month",
    "Loyer, abonnement… revient chaque mois": "Rent, subscription… comes back every month",
    "Versée sur votre épargne. Retrouvez-la dans « Épargne ».": "Paid into your savings. Find it in “Savings”.",
    "Mise de côté chaque mois sur votre épargne. En cas d'imprévu, vous pourrez y puiser.": "Set aside every month in your savings. In an emergency, you can draw on it.",
    "Ajoutée automatiquement par une charge fixe. La modifier ici ne change que ce mois-ci.": "Added automatically by a fixed cost. Editing it here only changes this month.",
    "Dépense professionnelle": "Business expense", "Note de frais : à rembourser ou à refacturer à un client": "Expense report: to be reimbursed or re-invoiced to a client",
    "Client refacturable (facultatif)": "Client to re-invoice (optional)", "Nom du client": "Client name",
    "Statut": "Status", "Joindre un justificatif": "Attach a receipt", "Changer": "Change",
    "Photo ou PDF, copié dans les données de Mes outils.": "Photo or PDF, copied into Mes outils data.",
    "Choisir un justificatif": "Choose a receipt", "Retirer": "Remove", "Ouvrir": "Open",
    "Ajouter": "Add", "Enregistrer": "Save", "Annuler": "Cancel", "Modifier": "Edit", "Supprimer": "Delete",
    "Dépense ajoutée": "Expense added", "Dépense modifiée": "Expense updated", "Dépense supprimée": "Expense deleted",
    "Dépense ajoutée, {montant} pris sur l'épargne": "Expense added, {montant} taken from savings",
    "Charge fixe ajoutée, elle reviendra chaque mois": "Fixed cost added, it will come back every month",
    "Charge fixe modifiée": "Fixed cost updated", "Charge fixe arrêtée": "Fixed cost stopped",
    "Cette dépense dépasse votre budget du mois de {montant}. Vous allez devoir toucher à votre épargne ({dispo} disponibles).":
      "This expense exceeds your monthly budget by {montant}. You will have to dip into your savings ({dispo} available).",
    "Montant pris sur l'épargne": "Amount taken from savings", "Entre 0 et {max}": "Between 0 and {max}",
    "Confirmer": "Confirm", "Ajouter sans toucher à l'épargne": "Add without touching savings",
    "Supprimer cette dépense ?": "Delete this expense?",
    "Elle disparaît des totaux. Ce qui a été pris sur l'épargne pour elle y revient.": "It disappears from the totals. What was taken from savings for it goes back.",
    "Arrêter cette charge fixe ?": "Stop this fixed cost?",
    "Elle ne sera plus ajoutée les mois suivants. Les dépenses déjà enregistrées sont conservées.": "It will no longer be added in the following months. Expenses already recorded are kept.",
    "Arrêter": "Stop", "Arrêter la charge fixe": "Stop the fixed cost",
    "Total par mois": "Total per month", "Reste pour le variable": "Left for variable spending",
    "Ajoutées automatiquement à vos dépenses au début de chaque mois.": "Added automatically to your expenses at the start of each month.",
    "Aucune charge fixe pour l'instant": "No fixed costs yet",
    "Ajoutez une fois pour toutes ce que vous payez chaque mois : loyer, électricité, internet, téléphone, assurance, abonnements… Elles s'ajouteront toutes seules à vos dépenses.":
      "Add once and for all what you pay every month: rent, electricity, internet, phone, insurance, subscriptions… They will be added to your expenses automatically.",
    "Le {n} de chaque mois": "On the {n} of every month", "Suivi de mon épargne": "My savings",
    "Mettre de côté chaque mois : choisissez la catégorie Épargne": "Save every month: choose the Savings category",
    "Épargne disponible": "Available savings", "{montant} mis de côté depuis le début": "{montant} set aside since the start",
    "{montant} repris": "{montant} taken back",
    "{nom} : {montant} mis de côté le {jour} de chaque mois": "{nom}: {montant} set aside on the {jour} of every month",
    "Prévu ce mois-ci": "Planned this month", "Repris ce mois-ci": "Taken back this month", "Épargné ce mois-ci": "Saved this month",
    "pour couvrir un dépassement": "to cover an overrun", "rien n'a été touché": "nothing was touched",
    "pris sur l'épargne des mois passés": "taken from previous months' savings",
    "Reprises sur l'épargne": "Withdrawals from savings", "Chaque fois que l'épargne a couvert un dépassement": "Each time savings covered an overrun",
    "Vous n'avez jamais eu à toucher à votre épargne. Bravo !": "You have never had to touch your savings. Well done!",
    "Annuler cette reprise": "Cancel this withdrawal", "Annuler cette reprise ?": "Cancel this withdrawal?",
    "{montant} reviendront dans l'épargne. La dépense est conservée : le dépassement du budget qu'elle couvrait réapparaîtra.":
      "{montant} will go back to savings. The expense is kept: the budget overrun it covered will reappear.",
    "Annuler la reprise": "Cancel the withdrawal", "{montant} remis dans l'épargne": "{montant} put back into savings",
    "Dépense de {montant}": "Expense of {montant}",
    "Aucune épargne pour l'instant": "No savings yet",
    "Ajoutez une charge fixe dans la catégorie « Épargne » : elle sera mise de côté chaque mois, dans votre budget. En cas d'imprévu, vous pourrez y puiser, et tout sera suivi ici.":
      "Add a fixed cost in the “Savings” category: it will be set aside every month, within your budget. In an emergency, you can draw on it, and everything is tracked here.",
    "Prévu": "Planned", "Repris": "Taken back", "Épargné": "Saved",
    "Ce mois": "This month", "Mois dernier": "Last month", "3 mois": "3 months", "12 mois": "12 months",
    "Comparaison avec le mois précédent": "Comparison with the previous month", "Évolution": "Change", "à date égale": "at the same date",
    "Au {date}, vous aviez dépensé {montant}.": "On {date}, you had spent {montant}.",
    "Bonne nouvelle : vous dépensez moins que le mois dernier à la même période.": "Good news: you are spending less than last month over the same period.",
    "Vous dépensez un peu plus que le mois dernier à la même période.": "You are spending a little more than last month over the same period.",
    "Vos dépenses sont identiques au mois dernier à la même période.": "Your spending is the same as last month over the same period.",
    "Moyenne quotidienne": "Daily average", "{montant} / jour": "{montant} / day", "Plus grosse dépense": "Largest expense",
    "Aucune dépense": "No expenses", "Dépenses par catégorie": "Spending by category", "Top catégories": "Top categories",
    "Total : {montant}": "Total: {montant}", "Aucune dépense sur cette période.": "No expenses in this period.",
    "Évolution des dépenses": "Spending over time", "Par jour": "Per day", "Par semaine": "Per week", "Par mois": "Per month",
    "Dépenses mensuelles": "Monthly spending", "en cours": "in progress",
    "Pas encore de statistiques": "No statistics yet",
    "Ajoutez quelques dépenses : vos graphiques apparaîtront ici automatiquement.": "Add a few expenses: your charts will appear here automatically.",
    "Semaine du {date}": "Week of {date}",
    "Toutes les notes": "All reports", "Exporter pour la comptabilité": "Export for accounting",
    "Aucune note de frais.": "No expense reports.",
    "Cochez « Dépense professionnelle » dans une dépense pour la suivre ici.": "Tick “Business expense” on an expense to track it here.",
    "{n} sans justificatif": "{n} without receipt", "Sans justificatif": "No receipt",
    "Statut modifié": "Status changed", "Justificatif joint": "Receipt attached", "Justificatif retiré": "Receipt removed",
    "Devise": "Currency", "Changer la devise ne convertit pas les montants : seul l'affichage change.": "Changing the currency does not convert amounts: only the display changes.",
    "Catégories": "Categories", "Nouvelle catégorie": "New category", "Modifier la catégorie": "Edit category",
    "Nom de la catégorie": "Category name", "Icône": "Icon", "Couleur": "Colour",
    "Pas supprimable": "Cannot be deleted", "{n} utilisations": "used {n} times", "1 utilisation": "used once", "Inutilisée": "Unused",
    "Supprimer la catégorie « {nom} » ?": "Delete the “{nom}” category?",
    "Ses dépenses et charges fixes passent dans :": "Its expenses and fixed costs move to:",
    "Elle n'est utilisée par aucune dépense.": "It is not used by any expense.",
    "Catégorie supprimée": "Category deleted", "Catégorie enregistrée": "Category saved", "Devise enregistrée": "Currency saved",
    "Justificatifs": "Receipts", "Rangés dans : {dossier}": "Stored in: {dossier}",
    "Euro": "Euro", "Dollar américain": "US dollar", "Ariary": "Ariary",
    "Rien à exporter.": "Nothing to export.", "Fichier enregistré : {nom}": "File saved: {nom}",
    // Messages du serveur
    "Date invalide.": "Invalid date.", "Mois invalide.": "Invalid month.", "Choisissez une catégorie.": "Choose a category.",
    "Moyen de paiement invalide.": "Invalid payment method.", "Statut invalide.": "Invalid status.",
    "Donnez un nom à cette charge (ex. Loyer).": "Give this cost a name (e.g. Rent).", "Jour invalide.": "Invalid day.",
    "Charge fixe introuvable.": "Fixed cost not found.", "Catégorie introuvable.": "Category not found.",
    "Dépense introuvable.": "Expense not found.", "Reprise introuvable.": "Withdrawal not found.",
    "Donnez un nom à la catégorie.": "Give the category a name.", "Une catégorie porte déjà ce nom.": "A category already has this name.",
    "Icône invalide.": "Invalid icon.", "Couleur invalide.": "Invalid colour.",
    "La catégorie Épargne ne peut pas être supprimée.": "The Savings category cannot be deleted.",
    "Gardez au moins une catégorie.": "Keep at least one category.",
    "Choisissez une catégorie de remplacement.": "Choose a replacement category.",
    "Le montant pris sur l'épargne est invalide.": "The amount taken from savings is invalid.",
    "Votre épargne ne suffit pas pour ce montant.": "Your savings are not enough for this amount.",
    "Le montant ne peut pas être inférieur à ce qui a été pris sur l'épargne. Annulez d'abord la reprise.":
      "The amount cannot be lower than what was taken from savings. Cancel the withdrawal first.",
    "Ce n'est pas une dépense professionnelle.": "This is not a business expense.",
    "Justificatif introuvable.": "Receipt not found.", "Fichier introuvable.": "File not found.",
    "Justificatif : une photo ou un PDF seulement.": "Receipt: a photo or a PDF only.",
    "Justificatif trop lourd (25 Mo au plus).": "Receipt too large (25 MB max).",
    "Devise non prise en charge.": "Currency not supported.",
    "Montant : indiquez un montant valide.": "Amount: enter a valid amount.",
    "Montant : ce montant est trop élevé.": "Amount: this amount is too high.",
    "Montant : le montant doit être supérieur à 0.": "Amount: the amount must be greater than 0.",
    "Montant pris sur l'épargne : indiquez un montant valide.": "Amount taken from savings: enter a valid amount.",
    "Montant pris sur l'épargne : ce montant est trop élevé.": "Amount taken from savings: this amount is too high.",
    "Montant pris sur l'épargne : le montant doit être supérieur à 0.": "Amount taken from savings: the amount must be greater than 0.",
    "Nom : 120 caractères maximum.": "Name: 120 characters max.",
    "Nom : 40 caractères maximum.": "Name: 40 characters max.",
    "Description : 120 caractères maximum.": "Description: 120 characters max.",
    "Client : 64 caractères maximum.": "Client: 64 characters max.",
    "Client : 120 caractères maximum.": "Client: 120 characters max.",
  });
  I18N.motifs([
    [/^(.+) : indiquez un montant valide\.$/, "$1: enter a valid amount."],
    [/^(.+) : ce montant est trop élevé\.$/, "$1: this amount is too high."],
    [/^(.+) : le montant doit être supérieur à 0\.$/, "$1: the amount must be greater than 0."],
    [/^(.+) : (\d+) caractères maximum\.$/, "$1: $2 characters max."],
  ]);

  const PAIEMENTS = { carte: "Carte bancaire", especes: "Espèces", virement: "Virement", paypal: "PayPal",
    mobile_money: "Mobile Money", autre: "Autre" };
  const STATUTS = { a_rembourser: "À rembourser", remboursee: "Remboursée", refacturee: "Refacturée" };
  const COULEUR_STATUT = { a_rembourser: "ambre", remboursee: "vert", refacturee: "vert" };
  const NIVEAUX = {
    normal: { lib: "Sur la bonne voie", etat: "vert", barre: "var(--violet)", icone: "circle-check", msg: "Tout va bien, vos dépenses restent maîtrisées." },
    attention: { lib: "À surveiller", etat: "ambre", barre: "var(--ambre)", icone: "info", msg: "Vous avez utilisé une bonne partie du budget, gardez un œil dessus." },
    presque: { lib: "Presque atteint", etat: "ambre", barre: "var(--ambre)", icone: "circle-alert", msg: "Le budget est presque atteint. Encore un petit effort jusqu'à la fin du mois." },
    depasse: { lib: "Budget dépassé", etat: "rouge", barre: "var(--rouge)", icone: "triangle-alert", msg: "Le budget est dépassé ce mois-ci. Ce n'est pas grave, il repart à zéro le mois prochain." },
  };
  // Couleurs des catégories (graphiques seulement), dans un ordre fixe.
  const COULEURS = { violet: "var(--violet)", ambre: "var(--ambre)", bleu: "var(--bleu-texte)", corail: "var(--corail)",
    menthe: "var(--menthe)", rouge: "var(--rouge)", gris: "var(--gris)" };
  const ONGLETS = [["accueil", "Tableau de bord"], ["depenses", "Dépenses"], ["charges", "Charges fixes"], ["budget", "Budget"],
    ["epargne", "Épargne"], ["statistiques", "Statistiques"], ["notes", "Notes de frais"], ["reglages", "Réglages"]];
  const DEVISES = { EUR: "Euro", USD: "Dollar américain", MGA: "Ariary" };

  const D = { onglet: "accueil", ctx: { devise: "EUR", categories: [], mois: null, aujourdhui: null },
    mois: null, filtres: { q: "", categorie: "", tri: "date_desc", pro: false },
    periode: "mois", evolution: "jour", statut: "a_rembourser", contacts: [] };

  const style = document.createElement("style");
  style.textContent = `
    .dp-onglets { margin: -4px 0 18px; }
    .dp-grille { display: grid; gap: 12px; margin-bottom: 14px; }
    .dp-g2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .dp-g3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .dp-g4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
    .dp-g53 { grid-template-columns: minmax(0, 3fr) minmax(0, 2fr); align-items: start; }
    @media (max-width: 1000px) { .dp-g3, .dp-g4 { grid-template-columns: repeat(2, minmax(0, 1fr)); } .dp-g53, .dp-g2 { grid-template-columns: 1fr; } }
    .dp-hero { padding: 20px 22px; margin-bottom: 14px; }
    .dp-hero .dp-lib { color: var(--doux); font-size: 13px; }
    .dp-gros { font-size: 34px; font-weight: 600; font-variant-numeric: tabular-nums; line-height: 1.15; }
    .dp-sous { color: var(--doux); font-size: 13px; margin-top: 2px; font-variant-numeric: tabular-nums; }
    .dp-hero-haut { display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; flex-wrap: wrap; }
    .dp-piste { height: 8px; border-radius: 99px; background: var(--surface); overflow: hidden; margin-top: 16px; }
    .dp-piste.fine { height: 6px; margin-top: 6px; }
    .dp-piste > div { height: 100%; border-radius: 99px; }
    .dp-sous-barre { display: flex; justify-content: space-between; color: var(--doux); font-size: 12.5px; margin-top: 6px; font-variant-numeric: tabular-nums; }
    .dp-message { margin: 14px 0 0; font-size: 13.5px; }
    .dp-tuile { background: var(--carte); border: 1px solid var(--ligne); border-radius: var(--rayon); padding: 12px 14px; min-width: 0; }
    .dp-tuile.cliquable { cursor: pointer; transition: border-color .12s, background .12s; }
    .dp-tuile.cliquable:hover { border-color: var(--ligne-forte); background: var(--surface); }
    .dp-tuile .dp-t-lib { display: flex; align-items: center; gap: 6px; color: var(--doux); font-size: 12.5px; }
    .dp-tuile .dp-t-val { font-size: 19px; font-weight: 600; margin-top: 4px; font-variant-numeric: tabular-nums; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .dp-tuile .dp-t-aide { color: var(--gris); font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .dp-carte-titre { display: flex; align-items: center; gap: 8px; margin: 0 0 10px; }
    .dp-carte-titre h3 { margin: 0; font-size: 14px; font-weight: 600; flex: 1; }
    .dp-carte-titre small { color: var(--gris); font-weight: 400; margin-left: 6px; }
    .dp-info { display: flex; gap: 10px; align-items: flex-start; font-size: 13.5px; padding: 10px 14px; margin-bottom: 14px; }
    .dp-info svg.ico { color: var(--doux); margin-top: 2px; }
    .dp-montant { font-weight: 600; font-variant-numeric: tabular-nums; color: var(--encre); white-space: nowrap; min-width: 84px; text-align: right; }
    .dp-barres .dp-b { margin-bottom: 11px; }
    .dp-barres .dp-b:last-child { margin-bottom: 0; }
    .dp-b-haut { display: flex; align-items: center; gap: 8px; font-size: 13px; }
    .dp-b-haut .nom { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: flex; align-items: center; gap: 6px; }
    .dp-b-haut .nom svg.ico { color: var(--doux); }
    .dp-b-haut .val { font-variant-numeric: tabular-nums; color: var(--doux); }
    .dp-b-haut .val b { color: var(--encre); font-weight: 600; }
    .dp-nav { display: flex; align-items: center; gap: 4px; }
    .dp-nav .lib { font-weight: 600; min-width: 150px; text-align: center; }
    .dp-filtres { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-bottom: 12px; }
    .dp-filtres select { height: 34px; }
    .dp-case { display: inline-flex; align-items: center; gap: 7px; font-size: 13px; color: var(--doux); cursor: pointer; white-space: nowrap; }
    .dp-case input { width: 16px; height: 16px; margin: 0; }
    .dp-resume { display: flex; gap: 14px; flex-wrap: wrap; align-items: center; color: var(--doux); font-size: 13px; margin: 0 2px 10px; }
    .dp-resume b { color: var(--encre); font-variant-numeric: tabular-nums; }
    .dp-jour { display: flex; justify-content: space-between; }
    .dp-guide ol { margin: 0; padding: 0; list-style: none; display: grid; gap: 8px; }
    .dp-guide li { display: flex; align-items: center; gap: 10px; font-size: 13.5px; }
    .dp-guide li .n { width: 22px; height: 22px; border-radius: 50%; border: 1px solid var(--ligne-forte); display: grid; place-items: center; font-size: 12px; color: var(--doux); flex: none; }
    .dp-guide li.fait { color: var(--gris); }
    .dp-guide li.fait .n { border-color: var(--vert-texte); color: var(--vert-texte); }
    .dp-guide li .n svg.ico { margin: 0; width: 13px; height: 13px; }
    .dp-guide li .btn { margin-left: auto; }
    .dp-table { width: 100%; border-collapse: collapse; font-size: 13.5px; font-variant-numeric: tabular-nums; }
    .dp-table th { text-align: left; font-size: 11.5px; text-transform: uppercase; letter-spacing: .04em; color: var(--gris); font-weight: 600; padding: 0 8px 8px; }
    .dp-table td { padding: 8px; border-top: 1px solid var(--ligne); }
    .dp-table .d { text-align: right; }
    .dp-anneau-bloc { display: flex; gap: 20px; align-items: center; flex-wrap: wrap; }
    .dp-anneau { position: relative; width: 150px; height: 150px; flex: none; }
    .dp-anneau svg { width: 100%; height: 100%; transform: rotate(-90deg); }
    .dp-anneau circle { fill: none; stroke-width: 15; }
    .dp-anneau .centre { position: absolute; inset: 0; display: grid; place-content: center; text-align: center; pointer-events: none; }
    .dp-anneau .centre b { font-size: 15px; font-variant-numeric: tabular-nums; }
    .dp-anneau .centre small { color: var(--gris); font-size: 11.5px; }
    .dp-legende { flex: 1; min-width: 180px; display: grid; gap: 6px; font-size: 13px; }
    .dp-legende div { display: flex; align-items: center; gap: 8px; }
    .dp-legende .pt { width: 9px; height: 9px; border-radius: 50%; flex: none; }
    .dp-legende .nom { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .dp-legende .val { font-variant-numeric: tabular-nums; }
    .dp-legende .pc { color: var(--gris); width: 42px; text-align: right; font-variant-numeric: tabular-nums; }
    .dp-colonnes { display: flex; align-items: flex-end; gap: 2px; height: 170px; border-bottom: 1px solid var(--ligne); padding-top: 18px; position: relative; }
    .dp-colonnes .dp-col { flex: 1; height: 100%; display: flex; align-items: flex-end; cursor: default; min-width: 0; }
    .dp-colonnes .dp-col > div { width: 100%; max-width: 34px; margin: 0 auto; background: var(--violet); border-radius: 3px 3px 0 0; min-height: 0; }
    .dp-colonnes .dp-col:hover > div { background: var(--violet-2); }
    .dp-colonnes .dp-max { position: absolute; top: 0; left: 0; font-size: 11px; color: var(--gris); font-variant-numeric: tabular-nums; }
    .dp-etiquettes { display: flex; gap: 2px; margin-top: 5px; }
    .dp-etiquettes span { flex: 1; min-width: 0; text-align: center; font-size: 10.5px; color: var(--gris); white-space: nowrap; overflow: hidden; }
    .dp-comp { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
    .dp-comp .v { font-size: 20px; font-weight: 600; font-variant-numeric: tabular-nums; margin-top: 2px; }
    .dp-comp .l { color: var(--doux); font-size: 12.5px; }
    .dp-comp small { color: var(--gris); font-size: 11.5px; }
    .dp-p { color: var(--doux); font-size: 13px; margin: 12px 0 0; }
    .dp-actions { width: 96px; justify-content: flex-end; }
    .dp-pt { width: 9px; height: 9px; border-radius: 50%; display: inline-block; }
    .dp-pj { width: 16px; display: flex; justify-content: center; }
    .dp-champ { display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px; }
    .dp-champ > span { font-size: 12.5px; font-weight: 500; color: var(--doux); }
    .dp-champ small { color: var(--gris); font-size: 12px; }
    /* Formulaire */
    .dp-saisie { display: flex; align-items: baseline; justify-content: center; gap: 8px; background: var(--surface); border-radius: var(--rayon); padding: 14px; margin-bottom: 14px; }
    .fenetre .dp-saisie input { border: 0 !important; background: transparent !important; box-shadow: none !important; font-size: 34px; font-weight: 600; text-align: right; width: 240px; padding: 0 !important; font-variant-numeric: tabular-nums; }
    .dp-saisie span { font-size: 22px; color: var(--doux); font-weight: 600; }
    .dp-cats { display: grid; grid-template-columns: repeat(auto-fill, minmax(88px, 1fr)); gap: 6px; }
    .dp-cats button { border: 1px solid var(--ligne); background: var(--champ); border-radius: 8px; padding: 8px 4px 6px; cursor: pointer; display: flex; flex-direction: column; align-items: center; gap: 4px; font-size: 11.5px; color: var(--doux); min-width: 0; }
    .dp-cats button span { max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .dp-cats button svg.ico { width: 17px; height: 17px; margin: 0; }
    .dp-cats button:hover { border-color: var(--ligne-forte); color: var(--encre); }
    .dp-cats button.choisi { border-color: var(--violet); background: var(--violet-clair); color: var(--violet); }
    .dp-bascule { display: flex; align-items: center; gap: 10px; border: 1px solid var(--ligne); border-radius: 8px; padding: 9px 12px; margin-bottom: 14px; cursor: pointer; }
    .dp-bascule.actif { border-color: color-mix(in srgb, var(--violet) 45%, transparent); background: var(--violet-clair); }
    .dp-bascule input { width: 16px; height: 16px; margin: 0; flex: none; }
    .dp-bascule b { display: block; font-weight: 500; font-size: 13.5px; color: var(--encre); }
    .dp-bascule small { display: block; font-size: 12px; color: var(--doux); }
    .dp-deux { display: grid; grid-template-columns: 1fr 1fr; gap: 0 12px; }
    .dp-pro { border-left: 2px solid var(--ligne-forte); padding-left: 12px; margin-bottom: 6px; }
    .dp-fichier { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; font-size: 13px; color: var(--encre); }
    .dp-fichier .nom { display: inline-flex; align-items: center; gap: 6px; max-width: 260px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .dp-note-info { display: flex; gap: 8px; align-items: flex-start; background: var(--surface); border-radius: 8px; padding: 9px 12px; font-size: 13px; color: var(--doux); margin-bottom: 14px; }
    .dp-note-info svg.ico { margin-top: 2px; }
    .dp-alerte { border: 1px solid color-mix(in srgb, var(--ambre) 45%, transparent); background: var(--ambre-clair); border-radius: 10px; padding: 12px 14px; margin-top: 4px; }
    .dp-alerte h4 { margin: 0 0 6px; color: var(--ambre-texte); display: flex; gap: 6px; align-items: center; font-size: 14px; }
    .dp-alerte p { margin: 0 0 10px; color: var(--encre); font-size: 13.5px; }
    .dp-alerte .lien { border: 0; background: none; color: var(--doux); text-decoration: underline; cursor: pointer; font-size: 12.5px; padding: 0; margin-top: 8px; }
    .dp-alerte label.champ { margin-bottom: 0; }
    .dp-alerte small.err { color: var(--rouge-texte); font-weight: 400; }
    .dp-icones { display: grid; grid-template-columns: repeat(10, 1fr); gap: 4px; }
    .dp-icones button { border: 1px solid transparent; background: var(--surface); color: var(--doux); border-radius: 7px; height: 32px; cursor: pointer; display: grid; place-items: center; }
    .dp-icones button svg.ico { margin: 0; width: 16px; height: 16px; }
    .dp-icones button.choisi { background: var(--violet-clair); color: var(--violet); border-color: var(--violet); }
    .dp-couleurs { display: flex; gap: 8px; }
    .dp-couleurs button { width: 24px; height: 24px; border-radius: 50%; border: 2px solid var(--carte); box-shadow: 0 0 0 1px var(--ligne); cursor: pointer; }
    .dp-couleurs button.choisi { box-shadow: 0 0 0 2px var(--encre); }
    .dp-statut-sel { height: 28px; font-size: 12.5px; padding: 2px 6px !important; }
    .carte-jour .dp-acc-sous { color: var(--doux); font-size: 12.5px; font-variant-numeric: tabular-nums; }
    .carte-jour .dp-piste { margin-top: 8px; }
  `;
  document.head.append(style);

  // ------------------------------------------------------------- outils
  const racine = () => $("#vue-depenses");
  const tx = s => document.createTextNode(s ?? "");
  const nb = s => Number.parseFloat(s || "0");        // affichage seulement (largeurs, formats)
  const DECIMALES = { EUR: 2, USD: 2, MGA: 0 };
  function fmt(montant, devise = D.ctx.devise) {
    const chiffres = DECIMALES[devise] ?? 2;
    const v = nb(montant);
    const entier = Math.abs(v - Math.round(v)) < 0.005;
    try {
      return new Intl.NumberFormat(I18N.locale(), { style: "currency", currency: devise, currencyDisplay: "narrowSymbol",
        minimumFractionDigits: entier ? 0 : chiffres, maximumFractionDigits: entier ? 0 : chiffres }).format(v).replace(/ /g, " ");
    } catch { return `${v} ${devise}`; }
  }
  function symbole() {
    try { return new Intl.NumberFormat(I18N.locale(), { style: "currency", currency: D.ctx.devise, currencyDisplay: "narrowSymbol" })
      .formatToParts(0).find(p => p.type === "currency")?.value || D.ctx.devise; } catch { return D.ctx.devise; }
  }
  /** « 12,50 » → 1250 (centimes entiers), NaN si invalide : comparaisons sans float. */
  function centimes(texte) {
    const s = String(texte ?? "").replace(/[\s  ]/g, "").replace(",", ".");
    if (!/^\d*\.?\d*$/.test(s) || s === "" || s === ".") return NaN;
    const [e, f = ""] = s.split(".");
    return Number(e || "0") * 100 + Number((f + "00").slice(0, 2));
  }
  const pourcent = (v, chiffres = 0) => new Intl.NumberFormat(I18N.locale(), { style: "percent", maximumFractionDigits: chiffres }).format(v);
  const dateObj = iso => new Date(iso.length === 7 ? iso + "-01T00:00" : iso.slice(0, 10) + "T00:00");
  const majuscule = s => s.charAt(0).toUpperCase() + s.slice(1);
  const libMois = (m, court = false) => majuscule(dateObj(m).toLocaleDateString(I18N.locale(), court ? { month: "short" } : { month: "long", year: "numeric" }).replace(".", ""));
  const dateCourte = iso => dateObj(iso).toLocaleDateString(I18N.locale(), { day: "numeric", month: "short" });
  const dateJour = iso => majuscule(dateObj(iso).toLocaleDateString(I18N.locale(), { weekday: "long", day: "numeric", month: "long" }));
  function decalerMois(m, n) { const d = dateObj(m); d.setMonth(d.getMonth() + n); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`; }
  const categorie = id => D.ctx.categories.find(c => c.id === id) || { nom: "Sans catégorie", icone: "tag", couleur: "gris" };
  const nomCat = c => I18N.traduire(c.nom);   // les catégories d'origine sont traduites, les autres restent telles quelles
  const pluriel = (n, un, plusieurs) => n === 1 ? t(un) : t(plusieurs, { n });
  const erreur = e => toast(e.message, "erreur", 5000);

  function piste(ratio, couleur, fine = false) {
    return el("div", { class: "dp-piste" + (fine ? " fine" : "") },
      el("div", { style: `width:${Math.min(100, Math.max(0, ratio * 100)).toFixed(1)}%;background:${couleur}` }));
  }
  function tuile(ic, lib, valeur, aide, action) {
    return el("div", { class: "dp-tuile" + (action ? " cliquable" : ""), onclick: action || null },
      el("div", { class: "dp-t-lib" }, icone(ic), lib),
      el("div", { class: "dp-t-val" }, tx(valeur)),
      aide ? el("div", { class: "dp-t-aide" }, tx(aide)) : null);
  }
  function titreCarte(titre, sous, ...droite) {
    return el("div", { class: "dp-carte-titre" }, el("h3", {}, titre, sous ? el("small", {}, tx(sous)) : null), ...droite);
  }
  function vide(ic, titre, texte, ...boutons) {
    return el("div", { class: "vide" }, icone(ic), el("div", { style: "font-weight:600;color:var(--encre);margin-bottom:4px" }, titre),
      texte ? el("div", { style: "max-width:520px;margin:0 auto" }, texte) : null,
      boutons.length ? el("div", { style: "margin-top:14px;display:flex;gap:8px;justify-content:center" }, ...boutons) : null);
  }

  async function telecharger(r) {
    if (!r.lignes) { toast("Rien à exporter."); return; }
    const lien = el("a", { href: URL.createObjectURL(new Blob([r.csv], { type: "text/csv;charset=utf-8" })), download: r.nom });
    document.body.append(lien); lien.click(); lien.remove();
    setTimeout(() => URL.revokeObjectURL(lien.href), 5000);
    toast(t("Fichier enregistré : {nom}", { nom: r.nom }), "succes");
  }
  async function exporter(filtres) {
    try { telecharger(await api("/api/depenses/export", filtres)); } catch (e) { erreur(e); }
  }

  /** Contacts de l'application voisine, si elle est là (sinon : saisie libre). */
  async function chargerContacts() {
    try {
      const r = await api("/api/contacts/liste", {});
      D.contacts = (r.contacts || []).filter(c => c && c.nom).slice(0, 300);
    } catch { D.contacts = []; }
  }

  // ------------------------------------------------------------- cadre
  async function afficher() {
    chargerContacts();
    await dessiner();
  }
  function aller(onglet) { D.onglet = onglet; dessiner(); }

  async function dessiner() {
    const zone = el("div", {}, el("div", { class: "squelette", style: "height:180px" }));
    racine().replaceChildren(
      el("div", { class: "barre-vue" },
        el("h2", {}, icone("wallet", "av"), "Dépenses"),
        el("span", { class: "espace" }),
        el("button", { class: "btn principal", onclick: () => formulaire() }, icone("plus", "av"), "Ajouter une dépense")),
      el("div", { class: "puces dp-onglets" }, ONGLETS.map(([cle, lib]) =>
        el("button", { class: "puce" + (D.onglet === cle ? " actif" : ""), onclick: () => aller(cle) }, lib))),
      zone);
    const vues = { accueil: vueAccueil, depenses: vueDepenses, charges: vueCharges, budget: vueBudget, epargne: vueEpargne,
      statistiques: vueStatistiques, notes: vueNotes, reglages: vueReglages };
    try { zone.replaceChildren(...[].concat(await vues[D.onglet]())); }
    catch (e) { zone.replaceChildren(el("div", { class: "vide" }, icone("circle-alert"), tx(e.message))); }
  }
  const recharger = () => dessiner();
  function garder(r) { D.ctx = { devise: r.devise, categories: r.categories, mois: r.mois, aujourdhui: r.aujourdhui }; if (!D.mois) D.mois = r.mois; return r; }

  // --------------------------------------------------- lignes de dépense
  function ligneDepense(x, options = {}) {
    const c = categorie(x.categorie);
    const titre = x.description || nomCat(c);
    const meta = [nomCat(c), options.sansDate ? null : dateCourte(x.date), t(PAIEMENTS[x.paiement] || "Autre"),
      x.repris ? t("{montant} pris sur l'épargne", { montant: fmt(x.repris) }) : null].filter(Boolean).join(" · ");
    return el("div", { class: "ligne" },
      el("span", { class: "ligne-ic", title: nomCat(c) }, icone(c.icone)),
      el("div", { class: "ligne-corps" },
        el("div", { class: "ligne-titre" }, el("span", { title: titre }, tx(titre)),
          x.charge ? el("span", { class: "tag" }, "Charge fixe") : null,
          x.pro ? el("span", { class: "tag" }, "Pro") : null,
          x.pro && x.client_nom ? el("span", { class: "tag", title: x.client_nom }, tx(x.client_nom)) : null),
        el("div", { class: "ligne-meta" }, tx(meta))),
      el("div", { class: "ligne-cote" },
        el("span", { class: "dp-pj", title: x.justificatif ? "Justificatif" : null }, x.justificatif ? icone("paperclip") : null),
        x.pro && x.statut ? el("span", { class: "etat-txt " + COULEUR_STATUT[x.statut] }, STATUTS[x.statut]) : null,
        el("span", { class: "dp-montant" }, tx(fmt(x.montant)))),
      el("div", { class: "ligne-actions dp-actions" },
        x.justificatif ? el("button", { class: "icone-btn", title: "Ouvrir le justificatif", onclick: () => ouvrirJustificatif(x) }, icone("file-text")) : null,
        el("button", { class: "icone-btn", title: "Modifier", onclick: () => formulaire({ depense: x }) }, icone("pencil")),
        el("button", { class: "icone-btn danger", title: "Supprimer", onclick: () => supprimerDepense(x) }, icone("trash-2"))));
  }
  async function ouvrirJustificatif(x) {
    try { await api("/api/depenses/justificatif/ouvrir", { id: x.id }); } catch (e) { erreur(e); }
  }
  async function supprimerDepense(x) {
    if (!(await confirmer(icone("trash-2"), "Supprimer cette dépense ?", "Elle disparaît des totaux. Ce qui a été pris sur l'épargne pour elle y revient.", "Supprimer"))) return;
    try { await api("/api/depenses/supprimer", { id: x.id }); toast("Dépense supprimée", "succes"); recharger(); }
    catch (e) { erreur(e); }
  }

  function barresCategories(liste, limite) {
    const max = Math.max(...liste.map(x => nb(x.total)), 0.01);
    return el("div", { class: "dp-barres" }, liste.slice(0, limite).map(x =>
      el("div", { class: "dp-b" },
        el("div", { class: "dp-b-haut" },
          el("span", { class: "nom" }, icone(x.icone), tx(nomCat(x))),
          el("span", { class: "val" }, el("b", {}, tx(fmt(x.total))), tx(" · " + pourcent(x.part)))),
        piste(nb(x.total) / max, "var(--violet)", true))));
  }

  // ------------------------------------------------------ tableau de bord
  function message(r) {
    const b = r.budget;
    if (!b.nombre) return t("Aucune dépense ce mois-ci pour l'instant. Ajoutez-en une en quelques secondes.");
    if (b.niveau) {
      if (centimes(b.reste.replace("-", "")) && b.reste.startsWith("-"))
        return t("Vous avez dépassé votre budget de {montant}. Pas de panique, le mois prochain repart à zéro.", { montant: fmt(b.reste.slice(1)) });
      return b.ratio >= 0.7
        ? t("Il vous reste {reste} pour le mois, soit environ {jour} par jour.", { reste: fmt(b.reste), jour: fmt(b.par_jour || "0") })
        : t("Vous avez utilisé {pct} % de votre budget. Il vous reste {reste}.", { pct: Math.round(b.ratio * 100), reste: fmt(b.reste) });
    }
    const avant = centimes(r.comparaison.precedent_a_date);
    if (avant > 0) {
      const ecart = (centimes(r.comparaison.variable_a_date) - avant) / avant;
      const pct = Math.abs(Math.round(ecart * 100));
      if (pct >= 5) return t(ecart < 0 ? "Vos dépenses variables sont {pct} % plus faibles que le mois dernier à la même date."
        : "Vos dépenses variables sont {pct} % plus élevées que le mois dernier à la même date.", { pct });
      return t("Vos dépenses variables sont stables par rapport au mois dernier.");
    }
    return r.par_categorie[0] ? t("Votre principale catégorie de dépenses est « {cat} ».", { cat: nomCat(r.par_categorie[0]) }) : null;
  }

  function hero(b, avecEditeur = false) {
    const enfants = [];
    if (b.niveau) {
      const n = NIVEAUX[b.niveau];
      const sous = [t("sur {budget}", { budget: fmt(b.budget) }),
        centimes(b.fixes) ? t("dont {montant} de charges fixes", { montant: fmt(b.fixes) }) : null,
        centimes(b.repris) ? t("{montant} couverts par l'épargne", { montant: fmt(b.repris) }) : null].filter(Boolean).join(" · ");
      const depasse = b.reste.startsWith("-");
      enfants.push(
        el("div", { class: "dp-hero-haut" },
          el("div", {}, el("div", { class: "dp-lib" }, avecEditeur ? "Dépensé" : "Dépensé ce mois-ci"),
            el("div", { class: "dp-gros" }, tx(fmt(b.depense))), el("div", { class: "dp-sous" }, tx(sous))),
          el("span", { class: "etat-txt " + n.etat, style: "font-size:13.5px;font-weight:500" }, icone(n.icone), n.lib)),
        piste(b.ratio, n.barre),
        el("div", { class: "dp-sous-barre" }, el("span", {}, tx(t("{pct} utilisé", { pct: pourcent(b.ratio) }))),
          el("span", {}, tx(depasse ? t("{montant} au-delà", { montant: fmt(b.reste.slice(1)) }) : t("{montant} restants", { montant: fmt(b.reste) })))),
        avecEditeur ? el("p", { class: "dp-message" }, n.msg) : null);
    } else {
      enfants.push(el("div", { class: "dp-hero-haut" },
        el("div", {}, el("div", { class: "dp-lib" }, "Dépensé ce mois-ci"), el("div", { class: "dp-gros" }, tx(fmt(b.depense))),
          el("div", { class: "dp-sous" }, "Fixez-vous un objectif"),
          el("div", { class: "dp-sous" }, "Un budget mensuel vous aide à savoir où vous en êtes en un coup d'œil.")),
        avecEditeur ? null : el("button", { class: "btn", onclick: () => aller("budget") }, icone("target", "av"), "Définir un budget")));
    }
    return el("div", { class: "carte dp-hero" }, ...enfants);
  }

  async function vueAccueil() {
    const r = garder(await api("/api/depenses/tableau", {}));
    const b = r.budget, e = r.epargne, g = r.guide;
    const blocs = [];
    if (!g.charges || !g.variables) {
      const etape = (fait, n, texte, bouton) => el("li", { class: fait ? "fait" : "" },
        el("span", { class: "n" }, fait ? icone("check") : String(n)), texte, fait ? null : bouton);
      blocs.push(el("div", { class: "carte dp-guide", style: "margin-bottom:14px" }, titreCarte("Pour commencer"),
        el("ol", {},
          etape(g.charges, 1, "Ajoutez vos charges fixes (loyer, abonnements…) : elles reviendront toutes seules chaque mois.",
            el("button", { class: "btn petit", onclick: () => formulaire({ fixe: true }) }, "Ajouter une charge fixe")),
          etape(g.variables, 2, "Ajoutez une dépense du quotidien en quelques secondes.",
            el("button", { class: "btn petit", onclick: () => formulaire() }, "Ajouter une dépense")),
          etape(g.budget, 3, "Fixez un budget mensuel pour savoir où vous en êtes.",
            el("button", { class: "btn petit", onclick: () => aller("budget") }, "Définir un budget")))));
    }
    blocs.push(hero(b));
    const repris = centimes(e.repris_mois), net = centimes(e.epargne_mois);
    const aideEpargne = !e.existe ? t("Mise de côté chaque mois, à n'utiliser qu'en cas d'imprévu")
      : !repris ? t("{montant} épargnés ce mois-ci", { montant: fmt(e.epargne_mois) })
      : net >= 0 ? t("{montant} épargnés ce mois-ci, {repris} repris", { montant: fmt(e.epargne_mois), repris: fmt(e.repris_mois) })
      : t("{montant} repris ce mois-ci, au-delà de l'épargne du mois", { montant: fmt(e.repris_mois) });
    blocs.push(el("div", { class: "dp-grille dp-g4" },
      tuile("repeat", "Charges fixes", fmt(b.fixes), r.charges.nombre ? t("{n} par mois", { n: r.charges.nombre }) : t("Aucune pour l'instant"), () => aller("charges")),
      tuile("shopping-cart", "Dépenses variables", fmt(b.variables), t("{n} ce mois-ci", { n: r.variables_nombre }), () => aller("depenses")),
      tuile("piggy-bank", "Épargne", e.existe ? t("{montant} disponibles", { montant: fmt(e.disponible) }) : t("Créer mon épargne"), aideEpargne, () => aller("epargne")),
      tuile("briefcase-business", "Notes de frais à rembourser", r.notes.nombre ? fmt(r.notes.total) : t("Rien à rembourser"),
        r.notes.nombre ? pluriel(r.notes.nombre, "1 note de frais", "{n} notes de frais") : null, () => aller("notes"))));
    const msg = message(r);
    if (msg && b.nombre) blocs.push(el("div", { class: "carte dp-info" }, icone("lightbulb"), tx(msg)));
    blocs.push(el("div", { class: "dp-grille dp-g53" },
      el("div", { class: "carte" }, titreCarte("Dernières dépenses", null,
        r.dernieres.length ? el("button", { class: "btn discret petit", onclick: () => aller("depenses") }, "Tout voir", icone("chevron-right")) : null),
        r.dernieres.length ? el("div", { class: "lignes", style: "border:0" }, r.dernieres.map(x => ligneDepense(x)))
          : vide("receipt-text", "Pas encore de dépenses.", null, el("button", { class: "btn principal", onclick: () => formulaire() }, icone("plus", "av"), "Ajouter une dépense"))),
      r.par_categorie.length ? el("div", { class: "carte" }, titreCarte("Par catégorie", t("Ce mois-ci"),
        el("button", { class: "btn discret petit", onclick: () => aller("statistiques") }, icone("chart-pie", "av"), "Statistiques")),
        barresCategories(r.par_categorie, 4)) : null));
    return blocs;
  }

  // ------------------------------------------------------------ dépenses
  async function vueDepenses() {
    const f = D.filtres;
    const r = garder(await api("/api/depenses/liste", { mois: D.mois, ...f }));
    const recherche = el("input", { type: "search", value: f.q, placeholder: "Rechercher…", title: "Rechercher dans tous les mois…", style: "width:200px" });
    let delai;
    recherche.addEventListener("input", () => { clearTimeout(delai); delai = setTimeout(() => { f.q = recherche.value; dessinerGarderFocus(); }, 350); });
    const cats = el("select", { onchange: e => { f.categorie = e.target.value; recharger(); } },
      el("option", { value: "" }, "Toutes les catégories"),
      D.ctx.categories.map(c => { const o = el("option", { value: c.id }, tx(nomCat(c))); if (c.id === f.categorie) o.selected = true; return o; }));
    const tri = el("select", { onchange: e => { f.tri = e.target.value; recharger(); } },
      [["date_desc", "Plus récent"], ["date_asc", "Plus ancien"], ["montant_desc", "Montant décroissant"], ["montant_asc", "Montant croissant"]]
        .map(([v, l]) => { const o = el("option", { value: v }, l); if (v === f.tri) o.selected = true; return o; }));
    const pro = el("input", { type: "checkbox", checked: f.pro ? "" : null, onchange: e => { f.pro = e.target.checked; recharger(); } });
    const dernier = D.mois >= D.ctx.mois;
    const barre = el("div", { class: "dp-filtres" },
      r.recherche ? el("b", {}, "Résultats dans tous les mois") : el("div", { class: "dp-nav" },
        el("button", { class: "icone-btn", title: "Mois précédent", onclick: () => { D.mois = decalerMois(D.mois, -1); recharger(); } }, icone("chevron-left")),
        el("span", { class: "lib" }, tx(libMois(D.mois))),
        el("button", { class: "icone-btn", title: "Mois suivant", disabled: dernier ? "" : null, onclick: () => { D.mois = decalerMois(D.mois, 1); recharger(); } }, icone("chevron-right"))),
      el("span", { style: "flex:1" }),
      el("div", { class: "champ-recherche" }, el("span", {}, icone("search")), recherche),
      cats, tri, el("label", { class: "dp-case" }, pro, "Pro seulement"));
    const resume = el("div", { class: "dp-resume" },
      el("span", {}, tx(pluriel(r.nombre, "1 dépense", "{n} dépenses"))),
      el("span", {}, "Total", " ", el("b", {}, tx(fmt(r.total)))),
      centimes(r.fixes) ? el("span", {}, "Charges fixes", " ", el("b", {}, tx(fmt(r.fixes)))) : null,
      centimes(r.repris) ? el("span", {}, tx(t("{montant} couverts par l'épargne", { montant: fmt(r.repris) }))) : null,
      el("span", { style: "flex:1" }),
      el("button", { class: "btn petit", title: "Pour Excel (séparateur « ; »)", onclick: () => exporter({ mois: r.recherche ? "tout" : D.mois, pro: f.pro }) }, icone("download", "av"), "Export CSV"));
    if (!r.depenses.length) return [barre, vide("receipt-text", r.recherche || f.categorie || f.pro ? "Aucun résultat." : "Aucune dépense ce mois-ci.", null,
      el("button", { class: "btn principal", onclick: () => formulaire() }, icone("plus", "av"), "Ajouter une dépense"))];
    let liste;
    if (f.tri.startsWith("date")) {
      const jours = [];
      for (const x of r.depenses) { const j = jours.at(-1); if (j && j.date === x.date) j.liste.push(x); else jours.push({ date: x.date, liste: [x] }); }
      liste = el("div", { class: "lignes" }, jours.map(j => [
        el("div", { class: "titre-lignes dp-jour" }, el("span", {}, tx(dateJour(j.date) + (r.recherche ? " " + j.date.slice(0, 4) : ""))),
          el("span", {}, tx(fmt(j.liste.reduce((s, x) => s + centimes(x.montant), 0) / 100)))),
        j.liste.map(x => ligneDepense(x, { sansDate: true }))]));
    } else liste = el("div", { class: "lignes" }, r.depenses.map(x => ligneDepense(x)));
    return [barre, resume, liste];
  }
  /** Recherche : redessine sans perdre la saisie en cours. */
  async function dessinerGarderFocus() {
    await dessiner();
    const champ = racine().querySelector(".champ-recherche input");
    if (champ) { champ.focus(); champ.setSelectionRange(champ.value.length, champ.value.length); }
  }

  // ------------------------------------------------------- charges fixes
  async function vueCharges() {
    const r = garder(await api("/api/depenses/charges", {}));
    if (!r.charges.length) return vide("repeat", "Aucune charge fixe pour l'instant",
      "Ajoutez une fois pour toutes ce que vous payez chaque mois : loyer, électricité, internet, téléphone, assurance, abonnements… Elles s'ajouteront toutes seules à vos dépenses.",
      el("button", { class: "btn principal", onclick: () => formulaire({ fixe: true }) }, icone("plus", "av"), "Ajouter une charge fixe"));
    return [
      el("div", { class: "dp-grille dp-g2" },
        tuile("repeat", "Total par mois", fmt(r.total), null),
        r.reste_variable !== null ? tuile("wallet", "Reste pour le variable", fmt(r.reste_variable), null) : el("div")),
      el("div", { class: "carte" },
        titreCarte("Charges fixes", t("Ajoutées automatiquement à vos dépenses au début de chaque mois."),
          el("button", { class: "btn petit", onclick: () => formulaire({ fixe: true }) }, icone("plus", "av"), "Ajouter une charge fixe")),
        el("div", { class: "lignes" }, r.charges.map(c => {
          const cat = categorie(c.categorie);
          return el("div", { class: "ligne" },
            el("span", { class: "ligne-ic" }, icone(cat.icone)),
            el("div", { class: "ligne-corps" },
              el("div", { class: "ligne-titre" }, el("span", {}, tx(c.description)), cat.epargne ? el("span", { class: "tag" }, "Épargne") : null,
                c.pro ? el("span", { class: "tag" }, "Pro") : null),
              el("div", { class: "ligne-meta" }, tx([t("Le {n} de chaque mois", { n: c.jour }), nomCat(cat), t(PAIEMENTS[c.paiement])].join(" · ")))),
            el("div", { class: "ligne-cote" }, el("span", { class: "dp-montant" }, tx(fmt(c.montant)))),
            el("div", { class: "ligne-actions dp-actions" },
              el("button", { class: "icone-btn", title: "Modifier", onclick: () => formulaire({ charge: c }) }, icone("pencil")),
              el("button", { class: "icone-btn danger", title: "Arrêter la charge fixe", onclick: () => arreterCharge(c) }, icone("square"))));
        })),
        el("div", { style: "margin-top:12px" }, el("button", { class: "btn discret petit", onclick: () => aller("epargne") }, icone("piggy-bank", "av"),
          r.epargne ? "Suivi de mon épargne" : "Mettre de côté chaque mois : choisissez la catégorie Épargne")))];
  }
  async function arreterCharge(c) {
    if (!(await confirmer(icone("repeat"), "Arrêter cette charge fixe ?", "Elle ne sera plus ajoutée les mois suivants. Les dépenses déjà enregistrées sont conservées.", "Arrêter"))) return false;
    try { await api("/api/depenses/charges/arreter", { id: c.id }); toast("Charge fixe arrêtée", "succes"); recharger(); return true; }
    catch (e) { erreur(e); return false; }
  }

  // ------------------------------------------------------------- budget
  async function vueBudget() {
    const r = garder(await api("/api/depenses/budget", {}));
    const b = r.budget;
    const champ = el("input", { value: b.budget ? String(nb(b.budget)).replace(".", I18N.locale().startsWith("fr") ? "," : ".") : "", placeholder: "0",
      inputmode: "decimal", style: "width:160px", onkeydown: e => { if (e.key === "Enter") enregistrer(); } });
    const enregistrer = async () => {
      try { await api("/api/depenses/budget/definir", { montant: champ.value || "0" }); toast("Budget enregistré", "succes"); recharger(); }
      catch (e) { erreur(e); }
    };
    const carte = hero(b, true);
    carte.append(el("div", { style: "border-top:1px solid var(--ligne);margin-top:16px;padding-top:14px;display:flex;gap:10px;align-items:flex-end;flex-wrap:wrap" },
      el("label", { class: "champ", style: "margin:0" }, "Budget mensuel",
        el("span", { style: "display:flex;gap:8px;align-items:center" }, champ, el("span", { style: "color:var(--doux)" }, tx(symbole())))),
      el("button", { class: "btn principal", onclick: enregistrer }, "Enregistrer"),
      el("small", { style: "color:var(--gris);font-size:12px;padding-bottom:8px" }, "Reconduit chaque mois tant qu'il n'est pas modifié. 0 : pas de budget.")));
    const blocs = [carte];
    if (b.niveau) {
      const depasse = b.reste.startsWith("-");
      blocs.push(el("div", { class: "dp-grille dp-g3" },
        tuile("wallet", depasse ? "Dépassement" : "Restant", fmt(depasse ? b.reste.slice(1) : b.reste), null),
        tuile("calendar-days", "Par jour restant", b.par_jour ? fmt(b.par_jour) : "—", pluriel(b.jours_restants, "1 jour restant", "{n} jours restants")),
        tuile("trending-up", "Projection fin de mois", fmt(b.projection), t("au rythme actuel"))));
    }
    blocs.push(el("div", { class: "carte" }, titreCarte("Historique", t("6 derniers mois")),
      el("div", { class: "dp-barres" }, r.historique.map(h => el("div", { class: "dp-b" },
        el("div", { class: "dp-b-haut" }, el("span", { class: "nom", style: "font-weight:500" }, tx(libMois(h.mois))),
          el("span", { class: "val" }, el("b", {}, tx(fmt(h.depense))), h.budget ? tx(" / " + fmt(h.budget)) : null)),
        piste(h.ratio || 0, h.niveau ? NIVEAUX[h.niveau].barre : "var(--violet)", true))))));
    return blocs;
  }

  // ------------------------------------------------------------- épargne
  async function vueEpargne() {
    const r = garder(await api("/api/depenses/epargne", {}));
    if (!r.existe) return vide("piggy-bank", "Aucune épargne pour l'instant",
      "Ajoutez une charge fixe dans la catégorie « Épargne » : elle sera mise de côté chaque mois, dans votre budget. En cas d'imprévu, vous pourrez y puiser, et tout sera suivi ici.",
      el("button", { class: "btn principal", onclick: () => formulaire({ fixe: true, categorie: D.ctx.categories.find(c => c.epargne)?.id }) }, icone("plus", "av"), "Créer mon épargne"));
    const m = r.ce_mois;
    const net = centimes(m.net.replace("-", "")) && m.net.startsWith("-");
    return [
      el("div", { class: "carte dp-hero" },
        el("div", { class: "dp-lib" }, "Épargne disponible"),
        el("div", { class: "dp-gros" }, tx(fmt(r.disponible))),
        el("div", { class: "dp-sous" }, tx(t("{montant} mis de côté depuis le début", { montant: fmt(r.verse) }) +
          (centimes(r.repris) ? " · " + t("{montant} repris", { montant: fmt(r.repris) }) : ""))),
        r.charges.map(c => el("div", { class: "dp-note-info", style: "margin:12px 0 0" }, icone("repeat"),
          tx(t("{nom} : {montant} mis de côté le {jour} de chaque mois", { nom: c.description, montant: fmt(c.montant), jour: c.jour }))))),
      el("div", { class: "dp-grille dp-g3" },
        tuile("piggy-bank", "Prévu ce mois-ci", fmt(m.verse), null),
        tuile("arrow-down", "Repris ce mois-ci", fmt(m.repris), centimes(m.repris) ? t("pour couvrir un dépassement") : t("rien n'a été touché")),
        tuile("wallet", "Épargné ce mois-ci", fmt(m.net), net ? t("pris sur l'épargne des mois passés") : null)),
      el("div", { class: "carte", style: "margin-bottom:14px" }, titreCarte("Reprises sur l'épargne", t("Chaque fois que l'épargne a couvert un dépassement")),
        r.reprises.length ? el("div", { class: "lignes", style: "border:0" }, r.reprises.map(w => {
          const dep = w.depense_info;
          return el("div", { class: "ligne" },
            el("span", { class: "ligne-ic" }, icone("arrow-down")),
            el("div", { class: "ligne-corps" },
              el("div", { class: "ligne-titre" }, el("span", {}, tx(dep?.description || (dep ? nomCat(categorie(dep.categorie)) : t("Dépenses"))))),
              el("div", { class: "ligne-meta" }, tx(dep ? `${dateCourte(dep.date)} · ${t("Dépense de {montant}", { montant: fmt(dep.montant) })}` : libMois(w.mois)))),
            el("div", { class: "ligne-cote" }, el("span", { class: "dp-montant", style: "color:var(--rouge-texte)" }, tx("−" + fmt(w.montant)))),
            el("div", { class: "ligne-actions" }, el("button", { class: "icone-btn", title: "Annuler cette reprise", onclick: () => annulerReprise(w) }, icone("undo-2"))));
        })) : el("p", { class: "dp-p", style: "margin:0" }, "Vous n'avez jamais eu à toucher à votre épargne. Bravo !")),
      r.historique.length ? el("div", { class: "carte" }, titreCarte("Historique", t("12 derniers mois")),
        el("table", { class: "dp-table" },
          el("thead", {}, el("tr", {}, el("th", {}, "Mois"), el("th", { class: "d" }, "Prévu"), el("th", { class: "d" }, "Repris"), el("th", { class: "d" }, "Épargné"))),
          el("tbody", {}, r.historique.map(h => el("tr", {},
            el("td", {}, tx(libMois(h.mois))), el("td", { class: "d" }, tx(fmt(h.verse))),
            el("td", { class: "d", style: centimes(h.repris) ? "color:var(--rouge-texte)" : "color:var(--gris)" }, tx(centimes(h.repris) ? "−" + fmt(h.repris) : "—")),
            el("td", { class: "d", style: "font-weight:600" }, tx(fmt(h.net)))))))) : null];
  }
  async function annulerReprise(w) {
    if (!(await confirmer(icone("undo-2"), "Annuler cette reprise ?",
      t("{montant} reviendront dans l'épargne. La dépense est conservée : le dépassement du budget qu'elle couvrait réapparaîtra.", { montant: fmt(w.montant) }), "Annuler la reprise"))) return;
    try { await api("/api/depenses/epargne/annuler", { id: w.id }); toast(t("{montant} remis dans l'épargne", { montant: fmt(w.montant) }), "succes"); recharger(); }
    catch (e) { erreur(e); }
  }

  // ------------------------------------------------------- statistiques
  function anneau(liste, total) {
    // 5 catégories au plus, le reste dans « Autres » (couleurs dans un ordre fixe).
    const parts = liste.slice(0, 5).map(x => ({ nom: nomCat(x), total: x.total, part: x.part, couleur: COULEURS[x.couleur] || "var(--gris)" }));
    if (liste.length > 5) {
      const reste = liste.slice(5);
      parts.push({ nom: t("Autres"), total: (reste.reduce((s, x) => s + centimes(x.total), 0) / 100).toFixed(2),
        part: reste.reduce((s, x) => s + x.part, 0), couleur: "var(--gris)" });
    }
    const R = 50, C = 2 * Math.PI * R, ns = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(ns, "svg");
    svg.setAttribute("viewBox", "0 0 120 120");
    const fond = document.createElementNS(ns, "circle");
    for (const [k, v] of Object.entries({ cx: 60, cy: 60, r: R, style: "stroke:var(--surface)" })) fond.setAttribute(k, v);
    svg.append(fond);
    let deja = 0;
    for (const p of parts) {
      const long = Math.max(0, p.part * C - (parts.length > 1 ? 1.5 : 0));   // petit espace entre les parts
      const c = document.createElementNS(ns, "circle");
      for (const [k, v] of Object.entries({ cx: 60, cy: 60, r: R, style: `stroke:${p.couleur}`, "stroke-dasharray": `${long} ${C - long}`, "stroke-dashoffset": -deja * C })) c.setAttribute(k, v);
      const titre = document.createElementNS(ns, "title");
      titre.textContent = `${p.nom} : ${fmt(p.total)} (${pourcent(p.part)})`;
      c.append(titre);
      svg.append(c);
      deja += p.part;
    }
    return el("div", { class: "dp-anneau-bloc" },
      el("div", { class: "dp-anneau" }, svg, el("div", { class: "centre" }, el("b", {}, tx(fmt(total))), el("small", {}, "Total"))),
      el("div", { class: "dp-legende" }, parts.map(p => el("div", {},
        el("span", { class: "pt", style: `background:${p.couleur}` }), el("span", { class: "nom" }, tx(p.nom)),
        el("span", { class: "val" }, tx(fmt(p.total))), el("span", { class: "pc" }, tx(pourcent(p.part)))))));
  }
  function colonnes(serie, libelle, infobulle) {
    const max = Math.max(...serie.map(p => nb(p.total)), 0);
    const pas = Math.ceil(serie.length / 12);
    return el("div", {},
      el("div", { class: "dp-colonnes" },
        max ? el("span", { class: "dp-max" }, tx(fmt(max))) : null,
        serie.map(p => el("div", { class: "dp-col", title: `${infobulle(p)} : ${fmt(p.total)}` },
          el("div", { style: `height:${max ? (nb(p.total) / max) * 100 : 0}%` })))),
      el("div", { class: "dp-etiquettes" }, serie.map((p, i) => el("span", {}, tx(i % pas === 0 ? libelle(p) : "")))));
  }
  function badge(v) {
    if (v === null || v === undefined) return el("span", { class: "etat-txt gris" }, "—");
    const plat = Math.abs(v) < 0.005;
    return el("span", { class: "etat-txt " + (plat ? "gris" : v < 0 ? "vert" : "rouge") },
      icone(plat ? "minus" : v < 0 ? "trending-down" : "trending-up"), tx((v > 0 ? "+" : "") + pourcent(v, 1)));
  }
  async function vueStatistiques() {
    const r = garder(await api("/api/depenses/statistiques", { periode: D.periode }));
    if (r.vide) return vide("chart-pie", "Pas encore de statistiques", "Ajoutez quelques dépenses : vos graphiques apparaîtront ici automatiquement.",
      el("button", { class: "btn principal", onclick: () => formulaire() }, icone("plus", "av"), "Ajouter une dépense"));
    const PERIODES = [["mois", "Ce mois"], ["precedent", "Mois dernier"], ["3m", "3 mois"], ["12m", "12 mois"]];
    const c = r.comparaison;
    const v = c.variation;
    const g = r.plus_grosse;
    const serie = r.series[D.evolution];
    const libelles = {
      jour: [p => String(Number(p.cle.slice(8))), p => dateCourte(p.cle)],
      semaine: [p => dateCourte(p.cle), p => t("Semaine du {date}", { date: dateCourte(p.cle) })],
      mois: [p => libMois(p.cle, true), p => libMois(p.cle)],
    }[D.evolution];
    return [
      el("div", { class: "puces", style: "margin-bottom:14px" }, PERIODES.map(([cle, lib]) =>
        el("button", { class: "puce" + (D.periode === cle ? " actif" : ""), onclick: () => { D.periode = cle; recharger(); } }, lib))),
      el("div", { class: "carte", style: "margin-bottom:14px" }, titreCarte("Comparaison avec le mois précédent"),
        el("div", { class: "dp-comp" },
          el("div", {}, el("div", { class: "l" }, "Ce mois"), el("div", { class: "v" }, tx(fmt(c.ce_mois)))),
          el("div", {}, el("div", { class: "l" }, tx(libMois(c.mois_precedent))), el("div", { class: "v", style: "color:var(--doux)" }, tx(fmt(c.mois_dernier)))),
          el("div", {}, el("div", { class: "l" }, "Évolution"), el("div", { class: "v", style: "font-size:15px" }, badge(v)), el("small", {}, "à date égale"))),
        v !== null ? el("p", { class: "dp-p" }, tx(t("Au {date}, vous aviez dépensé {montant}.", { date: dateCourte(c.meme_jour), montant: fmt(c.dernier_a_date) }) + " " +
          t(v < 0 ? "Bonne nouvelle : vous dépensez moins que le mois dernier à la même période." : v > 0
            ? "Vous dépensez un peu plus que le mois dernier à la même période." : "Vos dépenses sont identiques au mois dernier à la même période."))) : null),
      el("div", { class: "dp-grille dp-g2" },
        tuile("calendar-days", "Moyenne quotidienne", t("{montant} / jour", { montant: fmt(r.moyenne) }), null),
        tuile("trending-up", "Plus grosse dépense", g ? fmt(g.montant) : "—",
          g ? `${I18N.traduire(g.description || "")} · ${dateCourte(g.date)}` : t("Aucune dépense"))),
      el("div", { class: "dp-grille dp-g2" },
        el("div", { class: "carte" }, titreCarte("Dépenses par catégorie", t(PERIODES.find(p => p[0] === D.periode)[1])),
          r.par_categorie.length ? anneau(r.par_categorie, r.total) : el("p", { class: "dp-p" }, "Aucune dépense sur cette période.")),
        el("div", { class: "carte" }, titreCarte("Top catégories", t("Total : {montant}", { montant: fmt(r.total) })),
          r.par_categorie.length ? barresCategories(r.par_categorie, 5) : el("p", { class: "dp-p" }, "Aucune dépense sur cette période."))),
      el("div", { class: "carte", style: "margin-bottom:14px" },
        titreCarte("Évolution des dépenses", null, el("div", { class: "puces" }, [["jour", "Par jour"], ["semaine", "Par semaine"], ["mois", "Par mois"]].map(([cle, lib]) =>
          el("button", { class: "puce" + (D.evolution === cle ? " actif" : ""), onclick: () => { D.evolution = cle; recharger(); } }, lib)))),
        colonnes(serie, libelles[0], libelles[1])),
      el("div", { class: "carte" }, titreCarte("Dépenses mensuelles", t("6 derniers mois")),
        el("table", { class: "dp-table" }, el("tbody", {}, r.derniers_mois.map(m => el("tr", {},
          el("td", { style: "font-weight:500" }, tx(libMois(m.mois))), el("td", { class: "d", style: "font-weight:600" }, tx(fmt(m.total))),
          el("td", { class: "d", style: "width:110px" }, m.en_cours ? el("span", { class: "etat-txt gris" }, "en cours") : badge(m.variation)))))))];
  }

  // ------------------------------------------------------ notes de frais
  async function vueNotes() {
    const r = garder(await api("/api/depenses/notes", { statut: D.statut }));
    const tot = r.totaux;
    const aucune = !Object.values(tot).some(x => x.nombre);
    if (aucune) return vide("briefcase-business", "Aucune note de frais.", "Cochez « Dépense professionnelle » dans une dépense pour la suivre ici.",
      el("button", { class: "btn principal", onclick: () => formulaire({ pro: true }) }, icone("plus", "av"), "Ajouter une dépense"));
    const choix = [["a_rembourser", "À rembourser"], ["remboursee", "Remboursées"], ["refacturee", "Refacturées"], ["", "Toutes les notes"]];
    return [
      el("div", { class: "dp-grille dp-g3" }, choix.slice(0, 3).map(([cle, lib]) =>
        tuile(cle === "a_rembourser" ? "hourglass" : "circle-check", lib, fmt(tot[cle].total),
          pluriel(tot[cle].nombre, "1 note de frais", "{n} notes de frais"), () => { D.statut = cle; recharger(); }))),
      el("div", { class: "dp-filtres" },
        el("div", { class: "puces" }, choix.map(([cle, lib]) =>
          el("button", { class: "puce" + (D.statut === cle ? " actif" : ""), onclick: () => { D.statut = cle; recharger(); } }, lib))),
        el("span", { style: "flex:1" }),
        r.sans_justificatif ? el("span", { class: "etat-txt ambre" }, icone("circle-alert"), tx(t("{n} sans justificatif", { n: r.sans_justificatif }))) : null,
        el("button", { class: "btn", title: "Pour Excel (séparateur « ; »)", onclick: () => exporter({ mois: "tout", pro: true, statut: D.statut || null }) },
          icone("download", "av"), "Exporter pour la comptabilité")),
      r.notes.length ? el("div", { class: "lignes" }, r.notes.map(x => ligneNote(x))) : el("div", { class: "vide" }, "Aucune note de frais."),
      r.notes.length ? el("div", { class: "dp-resume", style: "margin-top:10px;justify-content:flex-end" }, "Total", el("b", {}, tx(fmt(r.total)))) : null];
  }
  function ligneNote(x) {
    const ligne = ligneDepense(x);
    // Le statut se change directement dans la ligne.
    const sel = el("select", { class: "dp-statut-sel", title: "Statut", onchange: async e => {
      try { await api("/api/depenses/statut", { id: x.id, statut: e.target.value }); toast("Statut modifié", "succes"); recharger(); }
      catch (err) { erreur(err); }
    } }, Object.entries(STATUTS).map(([v, l]) => { const o = el("option", { value: v }, l); if (v === x.statut) o.selected = true; return o; }));
    const cote = ligne.querySelector(".ligne-cote");
    cote.querySelector(".etat-txt")?.remove();
    if (!x.justificatif) cote.querySelector(".dp-pj").replaceChildren(el("span", { class: "etat-txt ambre", title: "Sans justificatif" }, icone("circle-alert")));
    cote.prepend(sel);
    return ligne;
  }

  // ------------------------------------------------------------ réglages
  async function vueReglages() {
    const r = garder(await api("/api/depenses/reglages", {}));
    return [
      el("div", { class: "carte", style: "margin-bottom:14px" }, titreCarte("Devise"),
        el("div", { class: "puces" }, r.devises.map(code => el("button", { class: "puce" + (r.devise === code ? " actif" : ""), onclick: async () => {
          try { await api("/api/depenses/devise", { devise: code }); toast("Devise enregistrée", "succes"); recharger(); } catch (e) { erreur(e); }
        } }, tx(code + " · "), DEVISES[code]))),
        el("p", { class: "dp-p" }, "Changer la devise ne convertit pas les montants : seul l'affichage change.")),
      el("div", { class: "carte", style: "margin-bottom:14px" },
        titreCarte("Catégories", null, el("button", { class: "btn petit", onclick: () => editerCategorie(null, r) }, icone("plus", "av"), "Nouvelle catégorie")),
        el("div", { class: "lignes" }, r.categories.map(c => el("div", { class: "ligne" },
          el("span", { class: "ligne-ic" }, icone(c.icone)),
          el("div", { class: "ligne-corps" }, el("div", { class: "ligne-titre" }, el("span", {}, tx(nomCat(c))),
            c.epargne ? el("span", { class: "tag" }, "Pas supprimable") : null),
            el("div", { class: "ligne-meta" }, tx(c.utilisations ? pluriel(c.utilisations, "1 utilisation", "{n} utilisations") : t("Inutilisée")))),
          el("div", { class: "ligne-cote" }, el("span", { class: "dp-pt", style: `background:${COULEURS[c.couleur]}` })),
          el("div", { class: "ligne-actions dp-actions" },
            el("button", { class: "icone-btn", title: "Modifier", onclick: () => editerCategorie(c, r) }, icone("pencil")),
            c.epargne ? null : el("button", { class: "icone-btn danger", title: "Supprimer", onclick: () => supprimerCategorie(c, r) }, icone("trash-2"))))))),
      el("div", { class: "carte" }, titreCarte("Justificatifs"),
        el("p", { class: "dp-p", style: "margin:0" }, tx(t("Rangés dans : {dossier}", { dossier: r.dossier_justificatifs }))))];
  }
  function editerCategorie(c, r) {
    const b = c ? { ...c, nom: nomCat(c) } : { nom: "", icone: "tag", couleur: "violet" };
    const nom = el("input", { value: b.nom, maxlength: 40 });
    const icones = el("div", { class: "dp-icones" }, r.icones.map(n => el("button", { type: "button", title: n, class: n === b.icone ? "choisi" : "",
      onclick: e => { b.icone = n; [...icones.children].forEach(x => x.classList.toggle("choisi", x === e.currentTarget)); } }, icone(n))));
    const couleurs = el("div", { class: "dp-couleurs" }, r.couleurs.map(k => el("button", { type: "button", style: `background:${COULEURS[k]}`, class: k === b.couleur ? "choisi" : "",
      onclick: e => { b.couleur = k; [...couleurs.children].forEach(x => x.classList.toggle("choisi", x === e.currentTarget)); } })));
    fenetre([
      el("h3", {}, c ? "Modifier la catégorie" : "Nouvelle catégorie"),
      el("label", { class: "champ" }, "Nom de la catégorie", nom),
      el("div", { class: "dp-champ" }, el("span", {}, "Icône"), icones),
      el("div", { class: "dp-champ" }, el("span", {}, "Couleur"), couleurs),
      el("div", { class: "actions" },
        el("button", { class: "btn", onclick: fermer }, "Annuler"),
        el("button", { class: "btn principal", onclick: async () => {
          // Nom d'origine inchangé (affiché traduit) : on garde le nom enregistré.
          const valeur = c && nom.value === nomCat(c) ? c.nom : nom.value;
          try {
            await api(c ? "/api/depenses/categories/modifier" : "/api/depenses/categories/ajouter", { id: c?.id, nom: valeur, icone: b.icone, couleur: b.couleur });
            fermer(); toast("Catégorie enregistrée", "succes"); recharger();
          } catch (e) { erreur(e); }
        } }, "Enregistrer"))]);
    setTimeout(() => nom.focus(), 50);
  }
  function supprimerCategorie(c, r) {
    const autres = r.categories.filter(x => x.id !== c.id);
    const rempl = el("select", {}, autres.map(x => el("option", { value: x.id }, tx(nomCat(x)))));
    const defaut = autres.find(x => x.id === "autres");
    if (defaut) rempl.value = defaut.id;
    fenetre([el("div", { class: "gros" }, icone("trash-2")),
      el("h3", {}, tx(t("Supprimer la catégorie « {nom} » ?", { nom: nomCat(c) }))),
      c.utilisations ? el("label", { class: "champ" }, "Ses dépenses et charges fixes passent dans :", rempl) : el("p", {}, "Elle n'est utilisée par aucune dépense."),
      el("div", { class: "actions" },
        el("button", { class: "btn", onclick: fermer }, "Annuler"),
        el("button", { class: "btn principal", onclick: async () => {
          try { await api("/api/depenses/categories/supprimer", { id: c.id, remplacement: c.utilisations ? rempl.value : null }); fermer(); toast("Catégorie supprimée", "succes"); recharger(); }
          catch (e) { erreur(e); }
        } }, "Supprimer"))], true);
  }

  // ------------------------------------------------------- formulaire
  /** Une seule fenêtre pour : ajouter une dépense (ou une charge fixe),
      modifier une dépense, modifier une charge fixe. */
  async function formulaire(o = {}) {
    if (!D.ctx.categories.length) { try { garder(await api("/api/depenses/reglages", {})); } catch (e) { erreur(e); return; } }
    const dep = o.depense || null, charge = o.charge || null;
    const source = dep || charge;
    const creation = !source;
    const virgule = s => I18N.locale().startsWith("fr") ? String(nb(s)).replace(".", ",") : String(nb(s));
    const b = {
      montant: source ? virgule(source.montant) : "", categorie: source?.categorie || o.categorie || "",
      description: source?.description || "", fixe: Boolean(charge) || Boolean(o.fixe),
      date: dep?.date || (D.onglet === "depenses" && D.mois && D.mois !== D.ctx.mois ? D.mois + "-01" : D.ctx.aujourdhui),
      jour: charge?.jour || Number((D.ctx.aujourdhui || "2000-01-01").slice(8)), paiement: source?.paiement || (o.fixe ? "virement" : "carte"),
      note: dep?.note || "", pro: source ? Boolean(source.pro) : Boolean(o.pro), client_nom: source?.client_nom || "",
      client_id: source?.client_id || "", statut: dep?.statut || "a_rembourser", justificatif: dep?.justificatif || null, source_fichier: null,
    };
    const montant = el("input", { value: b.montant, placeholder: "0", inputmode: "decimal", autocomplete: "off", maxlength: 16,
      oninput: e => { e.target.value = e.target.value.replace(/[^\d.,\s]/g, ""); b.montant = e.target.value; masquerAlerte(); } });
    const infoCat = el("div");
    const cats = el("div", { class: "dp-cats" }, D.ctx.categories.map(c => el("button", { type: "button", class: c.id === b.categorie ? "choisi" : "", title: nomCat(c),
      onclick: e => { b.categorie = c.id; [...cats.children].forEach(x => x.classList.toggle("choisi", x === e.currentTarget)); majInfos(); } },
      icone(c.icone), el("span", {}, tx(nomCat(c))))));
    const description = el("input", { value: b.description, maxlength: 120, oninput: e => { b.description = e.target.value; } });
    const libDescription = el("span");
    const date = el("input", { type: "date", value: b.date, oninput: e => { b.date = e.target.value; } });
    const jour = el("select", { onchange: e => { b.jour = Number(e.target.value); } },
      Array.from({ length: 31 }, (_, i) => { const o2 = el("option", { value: i + 1 }, tx(t("Le {n}", { n: i + 1 }))); if (i + 1 === b.jour) o2.selected = true; return o2; }));
    const paiement = el("select", { onchange: e => { b.paiement = e.target.value; } },
      Object.entries(PAIEMENTS).map(([v, l]) => { const o2 = el("option", { value: v }, l); if (v === b.paiement) o2.selected = true; return o2; }));
    const note = el("textarea", { rows: 2, maxlength: 500, placeholder: "Un détail à retenir…", oninput: e => { b.note = e.target.value; } });
    note.value = b.note;
    const zoneDateJour = el("label", { class: "champ" });
    const zoneNote = el("label", { class: "champ" }, "Note (facultatif)", note);

    // Charge fixe (création seulement)
    const caseFixe = el("input", { type: "checkbox", checked: b.fixe ? "" : null });
    const basculeFixe = el("label", { class: "dp-bascule" + (b.fixe ? " actif" : "") }, caseFixe,
      el("span", {}, el("b", {}, "Charge fixe"), el("small", {})));
    caseFixe.addEventListener("change", () => { b.fixe = caseFixe.checked; majInfos(); });

    // Notes de frais
    const casePro = el("input", { type: "checkbox", checked: b.pro ? "" : null });
    const basculePro = el("label", { class: "dp-bascule" + (b.pro ? " actif" : "") }, casePro,
      el("span", {}, el("b", {}, "Dépense professionnelle"), el("small", {}, "Note de frais : à rembourser ou à refacturer à un client")));
    const client = el("input", { value: b.client_nom, maxlength: 120, placeholder: "Nom du client", list: "dp-contacts",
      oninput: e => { b.client_nom = e.target.value; const c = D.contacts.find(x => x.nom === b.client_nom); b.client_id = c ? String(c.id) : ""; } });
    const listeContacts = el("datalist", { id: "dp-contacts" }, D.contacts.map(c => el("option", { value: c.nom }, tx(c.entreprise || ""))));
    const statut = el("select", { onchange: e => { b.statut = e.target.value; } },
      Object.entries(STATUTS).map(([v, l]) => { const o2 = el("option", { value: v }, l); if (v === b.statut) o2.selected = true; return o2; }));
    const zoneFichier = el("div", { class: "dp-fichier" });
    const dessinerFichier = () => {
      const nomFichier = b.source_fichier ? b.source_fichier.nom : b.justificatif;
      zoneFichier.replaceChildren(
        nomFichier ? el("span", { class: "nom", title: nomFichier }, icone("paperclip"), tx(nomFichier)) : null,
        el("button", { type: "button", class: "btn petit", onclick: choisirFichier }, icone("upload", "av"), nomFichier ? "Changer" : "Joindre un justificatif"),
        !b.source_fichier && b.justificatif ? el("button", { type: "button", class: "btn discret petit", onclick: () => ouvrirJustificatif(dep) }, "Ouvrir") : null,
        nomFichier ? el("button", { type: "button", class: "btn discret petit", onclick: retirerFichier }, "Retirer") : null);
    };
    async function choisirFichier() {
      try {
        const r = await api("/api/depenses/justificatif/choisir", { titre: t("Choisir un justificatif") });
        if (r.chemin) { b.source_fichier = r; dessinerFichier(); }
      } catch (e) { erreur(e); }
    }
    async function retirerFichier() {
      if (b.source_fichier) { b.source_fichier = null; dessinerFichier(); return; }
      try { await api("/api/depenses/justificatif/retirer", { id: dep.id }); b.justificatif = null; dessinerFichier(); toast("Justificatif retiré", "succes"); recharger(); }
      catch (e) { erreur(e); }
    }
    const zonePro = el("div", { class: "dp-pro" });
    casePro.addEventListener("change", () => { b.pro = casePro.checked; majInfos(); });

    // Reprise sur l'épargne (dépassement du budget)
    const alerte = el("div", { class: "dp-alerte", hidden: "" });
    const actions = el("div", { class: "actions" });
    function masquerAlerte() { alerte.hidden = true; actions.hidden = false; }
    function montrerAlerte(p) {
      const reprise = el("input", { value: virgule(p.suggere), inputmode: "decimal", style: "width:140px" });
      const aide = el("small", { class: "err" });
      const max = Math.min(centimes(p.disponible), centimes(b.montant) || 0);
      const confirmerBtn = el("button", { class: "btn principal", onclick: () => envoyer(reprise.value) }, icone("piggy-bank", "av"), "Confirmer");
      const verifier = () => {
        const v = centimes(reprise.value);
        const ok = Number.isFinite(v) && v > 0 && v <= max;
        confirmerBtn.disabled = !ok;
        aide.textContent = ok ? "" : t("Entre 0 et {max}", { max: fmt(max / 100) });
      };
      reprise.addEventListener("input", verifier);
      alerte.replaceChildren(
        el("h4", {}, icone("triangle-alert"), "Budget dépassé"),
        el("p", {}, tx(t("Cette dépense dépasse votre budget du mois de {montant}. Vous allez devoir toucher à votre épargne ({dispo} disponibles).",
          { montant: fmt(p.depassement), dispo: fmt(p.disponible) }))),
        el("label", { class: "champ" }, "Montant pris sur l'épargne", el("span", { style: "display:flex;gap:8px;align-items:center" }, reprise, tx(symbole())), aide),
        el("div", { class: "actions", style: "margin-top:12px" },
          el("button", { class: "btn", onclick: masquerAlerte }, "Annuler"), confirmerBtn),
        el("button", { class: "lien", onclick: () => envoyer("0") }, "Ajouter sans toucher à l'épargne"));
      verifier();
      alerte.hidden = false; actions.hidden = true;
      alerte.scrollIntoView({ block: "nearest" });
      setTimeout(() => reprise.focus(), 30);
    }

    function majInfos() {
      basculeFixe.classList.toggle("actif", b.fixe);
      basculeFixe.querySelector("small").textContent = t(b.fixe ? "Ajoutée automatiquement chaque mois" : "Loyer, abonnement… revient chaque mois");
      basculePro.classList.toggle("actif", b.pro);
      libDescription.textContent = t(b.fixe ? "Nom de la charge" : "Description (facultatif)");
      description.placeholder = t(b.fixe ? "Loyer, Internet, Assurance…" : "ex. Courses de la semaine");
      zoneDateJour.replaceChildren(b.fixe ? t("Jour du mois") : t("Date"), b.fixe ? jour : date);
      zoneNote.hidden = b.fixe;
      const c = D.ctx.categories.find(x => x.id === b.categorie);
      const infos = [];
      if (c?.epargne) infos.push(el("div", { class: "dp-note-info" }, icone("piggy-bank"),
        b.fixe ? "Mise de côté chaque mois sur votre épargne. En cas d'imprévu, vous pourrez y puiser." : "Versée sur votre épargne. Retrouvez-la dans « Épargne »."));
      if (dep?.charge) infos.push(el("div", { class: "dp-note-info" }, icone("repeat"), "Ajoutée automatiquement par une charge fixe. La modifier ici ne change que ce mois-ci."));
      infoCat.replaceChildren(...infos);
      zonePro.hidden = !b.pro;
      zonePro.replaceChildren(
        el("label", { class: "champ" }, "Client refacturable (facultatif)", client, listeContacts),
        b.fixe ? null : el("div", { class: "dp-deux" },
          el("label", { class: "champ" }, "Statut", statut),
          el("div", { class: "dp-champ" }, el("span", {}, "Justificatif"), zoneFichier,
            el("small", {}, "Photo ou PDF, copié dans les données de Mes outils."))));
      dessinerFichier();
      masquerAlerte();
    }

    async function envoyer(reprise) {
      const donnees = { montant: b.montant, categorie: b.categorie, description: b.description, paiement: b.paiement,
        pro: b.pro, client_nom: b.client_nom, client_id: b.client_id };
      try {
        if (b.fixe) {
          const r = await api(charge ? "/api/depenses/charges/modifier" : "/api/depenses/charges/ajouter", { charge: { ...donnees, id: charge?.id, jour: b.jour } });
          fermer(); toast(charge ? "Charge fixe modifiée" : "Charge fixe ajoutée, elle reviendra chaque mois", "succes");
          return recharger(r);
        }
        Object.assign(donnees, { date: b.date, note: b.note, statut: b.statut, justificatif_source: b.source_fichier?.chemin || null });
        if (dep) {
          await api("/api/depenses/modifier", { depense: { ...donnees, id: dep.id } });
          fermer(); toast("Dépense modifiée", "succes"); return recharger();
        }
        const r = await api("/api/depenses/ajouter", { depense: donnees, reprise: reprise ?? null });
        if (!r.ajoutee) { montrerAlerte(r.epargne); return; }   // rien n'est enregistré : la reprise attend la confirmation
        fermer();
        toast(centimes(r.repris) ? t("Dépense ajoutée, {montant} pris sur l'épargne", { montant: fmt(r.repris) }) : t("Dépense ajoutée"), "succes");
        recharger();
      } catch (e) { erreur(e); }
    }
    function valider() {
      if (!(centimes(b.montant) > 0)) { toast(t("Montant : indiquez un montant valide."), "erreur"); montant.focus(); return; }
      if (!b.categorie) { toast("Choisissez une catégorie.", "erreur"); return; }
      if (b.fixe && !b.description.trim()) { toast("Donnez un nom à cette charge (ex. Loyer).", "erreur"); description.focus(); return; }
      envoyer();
    }
    actions.append(
      dep ? el("button", { class: "btn discret", style: "margin-right:auto;color:var(--rouge-texte)", onclick: async () => { fermer(); await supprimerDepense(dep); } }, icone("trash-2", "av"), "Supprimer") : null,
      charge ? el("button", { class: "btn discret", style: "margin-right:auto;color:var(--rouge-texte)", onclick: async () => { fermer(); await arreterCharge(charge); } }, icone("square", "av"), "Arrêter la charge fixe") : null,
      el("button", { class: "btn", onclick: fermer }, "Annuler"),
      el("button", { class: "btn principal", onclick: valider }, creation ? "Ajouter" : "Enregistrer"));
    montant.addEventListener("keydown", e => { if (e.key === "Enter") valider(); });

    fenetre([
      el("h3", {}, charge ? "Modifier la charge fixe" : dep ? "Modifier la dépense" : b.fixe ? "Nouvelle charge fixe" : "Nouvelle dépense"),
      el("div", { class: "dp-saisie" }, montant, el("span", {}, tx(symbole()))),
      el("div", { class: "dp-champ" }, el("span", {}, "Catégorie"), cats),
      creation ? basculeFixe : null,
      el("label", { class: "champ" }, libDescription, description),
      infoCat,
      el("div", { class: "dp-deux" }, zoneDateJour, el("label", { class: "champ" }, "Paiement", paiement)),
      zoneNote,
      basculePro, zonePro,
      alerte, actions]);
    $("#fenetre").style.width = "min(620px, 94vw)";
    majInfos();
    setTimeout(() => montant.focus(), 60);
  }

  // ------------------------------------------------- accueil, commandes
  async function carteAccueil() {
    let r;
    try { r = await api("/api/depenses/resume", {}); } catch { return null; }
    if (!r.budget && !r.nombre && !r.notes.nombre) return null;
    const n = r.niveau ? NIVEAUX[r.niveau] : null;
    return el("div", { class: "carte-jour", onclick: () => { D.onglet = "accueil"; montrerVue("depenses"); } },
      el("h4", {}, icone("wallet"), "Dépenses"),
      el("div", { class: "grand" }, tx(fmt(r.depense, r.devise))),
      el("div", { class: "dp-acc-sous" }, tx(r.budget && nb(r.budget) > 0 ? t("sur {budget}", { budget: fmt(r.budget, r.devise) }) : t("Dépensé ce mois-ci")),
        n ? el("span", { class: "etat-txt " + n.etat, style: "margin-left:8px" }, n.lib) : null),
      n ? piste(r.ratio, n.barre, true) : null,
      r.notes.nombre ? el("div", { class: "ligne-jour", style: "margin-top:8px" }, icone("briefcase-business"),
        tx(`${pluriel(r.notes.nombre, "1 note de frais", "{n} notes de frais")} · ${t("À rembourser").toLowerCase()} · ${fmt(r.notes.total, r.devise)}`)) : null);
  }

  VUES.depenses = {
    afficher,
    titre: "Dépenses", icone: icone("wallet"), groupe: "clients", ordre: 30,
    description: "Budget du mois, charges fixes, épargne, statistiques et notes de frais avec justificatifs.",
    profils: ["freelance", "assistant_virtuel", "assistant_direction", "developpeur"],
    carteAccueil,
    commandes: () => [
      { icone: icone("plus"), titre: "Ajouter une dépense", detail: "Dépenses", action: () => { montrerVue("depenses"); formulaire(); } },
      { icone: icone("briefcase-business"), titre: "Notes de frais à rembourser", detail: "Dépenses",
        action: () => { D.onglet = "notes"; D.statut = "a_rembourser"; montrerVue("depenses"); } },
      { icone: icone("download"), titre: "Exporter pour la comptabilité", detail: "Notes de frais", action: () => exporter({ mois: "tout", pro: true }) },
    ],
  };
})();
