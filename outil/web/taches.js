"use strict";
/* Application « Tâches » : liste groupée par échéance ou tableau Kanban
   (glisser-déposer), recherche et filtres, liste de contrôle, récurrence,
   client issu de l'application Contacts si elle est là (voir taches.py). */
(() => {
  I18N.ajouter({
    "Tâches": "Tasks",
    "Tâches avec échéances, priorités, étiquettes, sous-étapes et répétitions, en liste ou en tableau.":
      "Tasks with due dates, priorities, tags, sub-steps and repeats, as a list or a board.",
    "Liste": "List", "Tableau": "Board",
    "Nouvelle tâche": "New task", "Modifier la tâche": "Edit task",
    "Ajouter une tâche… (Entrée)": "Add a task… (Enter)",
    "Rechercher une tâche": "Search tasks",
    "Toutes les étiquettes": "All tags", "Tous les clients": "All clients", "Toutes les priorités": "All priorities",
    "Effacer les filtres": "Clear filters",
    "En retard": "Overdue", "Aujourd'hui": "Today", "Cette semaine": "This week", "Plus tard": "Later",
    "Sans échéance": "No due date", "Faites": "Done", "Demain": "Tomorrow", "Hier": "Yesterday",
    "À faire": "To do", "En cours": "In progress", "Fait": "Done",
    "Aucune tâche pour l'instant. Écrivez-en une ci-dessus.": "No task yet. Type one above.",
    "Aucune tâche ne correspond à la recherche.": "No task matches your search.",
    "Glissez une tâche ici": "Drag a task here",
    "{n} plus anciennes": "{n} older",
    "Titre": "Title", "Description (facultatif)": "Description (optional)",
    "Échéance": "Due date", "Heure (facultatif)": "Time (optional)",
    "Priorité": "Priority", "Basse": "Low", "Normale": "Normal", "Haute": "High",
    "Priorité haute": "High priority", "Priorité basse": "Low priority",
    "Répétition": "Repeat", "Aucune": "None", "Chaque jour": "Every day", "Chaque semaine": "Every week", "Chaque mois": "Every month",
    "Client (facultatif)": "Client (optional)", "Aucun": "None",
    "Étiquettes": "Tags", "Ajouter une étiquette": "Add a tag",
    "Liste de contrôle": "Checklist", "Ajouter une étape… (Entrée)": "Add a step… (Enter)", "Retirer": "Remove",
    "Statut": "Status",
    "Annuler": "Cancel", "Enregistrer": "Save", "Ajouter": "Add", "Supprimer": "Delete", "Modifier": "Edit",
    "Supprimer cette tâche ?": "Delete this task?",
    "Elle disparaît définitivement.": "It is removed for good.",
    "Tâche supprimée": "Task deleted", "Tâche enregistrée": "Task saved", "Tâche ajoutée": "Task added",
    "Prochaine fois : {date}": "Next time: {date}",
    "Ajoutée par {app}": "Added by {app}",
    "Une fois par jour, semaine ou mois : une fois faite, la tâche revient à la date suivante.":
      "Daily, weekly or monthly: once done, the task comes back on the next date.",
    "Marquer comme faite": "Mark as done", "Marquer à faire": "Mark as to do",
    "{n} autres": "{n} more", "Retard": "Late", "Jour": "Day",
    "Ouvrir les tâches": "Open tasks",
    // Messages du serveur
    "Indiquez un titre.": "Enter a title.",
    "Échéance invalide.": "Invalid due date.",
    "Heure invalide.": "Invalid time.",
    "Indiquez une date pour l'heure.": "Enter a date for the time.",
    "Priorité inconnue.": "Unknown priority.",
    "Répétition inconnue.": "Unknown repeat.",
    "Statut inconnu.": "Unknown status.",
    "Tâche introuvable.": "Task not found.",
    "Étape introuvable.": "Step not found.",
  });
  I18N.motifs([
    [/^(\d+) étiquettes au plus\.$/, "$1 tags at most."],
    [/^(\d+) étapes au plus\.$/, "$1 steps at most."],
  ]);

  const GROUPES = [["retard", "En retard"], ["aujourdhui", "Aujourd'hui"], ["semaine", "Cette semaine"],
    ["plus_tard", "Plus tard"], ["sans_echeance", "Sans échéance"]];
  const COLONNES = [["a_faire", "À faire"], ["en_cours", "En cours"], ["fait", "Fait"]];
  const RECURRENCES = { "": "Aucune", jour: "Chaque jour", semaine: "Chaque semaine", mois: "Chaque mois" };
  const PRIORITES = { basse: "Basse", normale: "Normale", haute: "Haute" };
  const MAX_FAITES = 30;
  let vueChoisie = "liste";
  try { vueChoisie = localStorage.getItem("mes-outils-taches-vue") || "liste"; } catch {}
  const T = { r: null, vue: vueChoisie, recherche: "", etiquette: "", client: "", priorite: "", contacts: null,
    ouvertes: new Set(), faitesOuvertes: false, glisse: null, glisseListe: null };

  const style = document.createElement("style");
  style.textContent = `
    .tc-filtres { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin: -4px 0 16px; }
    .tc-filtres select { height: 32px; padding: 0 8px !important; font-size: 13px; max-width: 190px; }
    .tc-case { width: 18px; height: 18px; border-radius: 5px; border: 1.5px solid var(--ligne-forte); background: var(--champ); padding: 0;
      display: grid; place-items: center; cursor: pointer; flex: none; color: var(--sur-violet); transition: border-color .12s, background .12s; }
    .tc-case:hover { border-color: var(--violet); }
    .tc-case svg.ico { width: 12px; height: 12px; margin: 0; stroke-width: 3; opacity: 0; }
    .tc-case.fait { background: var(--violet); border-color: var(--violet); }
    .tc-case.fait svg.ico { opacity: 1; }
    .tc-case.petite { width: 15px; height: 15px; border-radius: 4px; }
    .tc-case.petite svg.ico { width: 10px; height: 10px; }
    .ligne.tc-faite .ligne-titre > span:first-child { text-decoration: line-through; color: var(--gris); }
    .ligne .ligne-ic.tc-ic { width: 22px; }
    .tc-meta { display: inline-flex; align-items: center; gap: 4px; }
    .tc-meta + .tc-meta::before { content: "·"; margin: 0 1px 0 4px; color: var(--gris); }
    .tc-meta svg.ico { width: 13px; height: 13px; margin: 0; }
    .tc-prio { display: inline-flex; }
    .tc-prio svg.ico { width: 14px; height: 14px; margin: 0; }
    .tc-carte-titre .tc-prio { margin-top: 2px; }
    .tc-prio.haute { color: var(--rouge-texte); } .tc-prio.basse { color: var(--gris); }
    .tc-encours { color: var(--bleu-texte); }
    .tc-ajout { cursor: text; }
    .tc-ajout .ligne-ic { color: var(--gris); }
    .tc-ajout input { flex: 1; border: 0 !important; background: transparent !important; box-shadow: none !important; padding: 6px 0 !important; font-size: 14px; }
    .tc-ajout kbd { opacity: 0; transition: opacity .12s; }
    .tc-ajout:focus-within kbd { opacity: 1; }
    .tc-ajout-bloc { margin-bottom: 14px; }
    .tc-titre-groupe { display: flex; align-items: center; gap: 8px; }
    .tc-titre-groupe .n { font-weight: 500; color: var(--gris); letter-spacing: 0; }
    .tc-titre-groupe.rouge { color: var(--rouge-texte); }
    .tc-titre-groupe.plie { cursor: pointer; user-select: none; }
    .tc-titre-groupe.plie svg.ico { width: 13px; height: 13px; margin: 0; transition: transform .12s; }
    .tc-titre-groupe.plie.ouvert svg.ico { transform: rotate(90deg); }
    .tc-desc { white-space: pre-wrap; margin: 0 0 10px; font-size: 13.5px; color: var(--encre); overflow-wrap: anywhere; }
    .tc-etape { display: flex; align-items: center; gap: 9px; padding: 3px 0; font-size: 13.5px; cursor: pointer; width: fit-content; }
    .tc-etape.fait > span { text-decoration: line-through; color: var(--gris); }
    .tc-origine { font-size: 12px; color: var(--gris); margin-top: 8px; }
    .tc-detail-pied { display: flex; gap: 6px; margin-top: 10px; }

    .tc-tableau { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; align-items: start; }
    @media (max-width: 900px) { .tc-tableau { grid-template-columns: 1fr; } }
    .tc-col { background: var(--surface); border: 1px solid var(--ligne); border-radius: var(--rayon); padding: 8px; min-height: 340px; transition: border-color .12s; }
    .tc-col.survol { border-color: var(--violet); }
    .tc-col-titre { display: flex; align-items: center; gap: 8px; padding: 4px 6px 10px; font-size: 12px; font-weight: 600; color: var(--gris);
      text-transform: uppercase; letter-spacing: .04em; }
    .tc-col-titre .n { color: var(--doux); font-weight: 500; letter-spacing: 0; }
    .tc-carte { background: var(--carte); border: 1px solid var(--ligne); border-radius: 8px; padding: 9px 11px; margin-bottom: 6px; cursor: grab;
      box-shadow: var(--ombre); transition: border-color .12s; }
    .tc-carte:hover { border-color: var(--ligne-forte); }
    .tc-carte.glisse { opacity: .4; }
    .tc-ligne-draggable { cursor: grab; }
    .tc-ligne-draggable.glisse { opacity: .4; }
    .tc-ligne-draggable.survol { outline: 2px solid var(--violet); outline-offset: -2px; }
    .tc-carte-titre { font-weight: 500; display: flex; gap: 6px; align-items: flex-start; overflow-wrap: anywhere; }
    .tc-carte-titre > span:first-child { flex: 1; min-width: 0; }
    .tc-carte.tc-faite .tc-carte-titre > span:first-child { text-decoration: line-through; color: var(--gris); }
    .tc-infos { display: flex; flex-wrap: wrap; gap: 3px 10px; margin-top: 6px; font-size: 12px; color: var(--doux); }
    .tc-infos .etat-txt { font-size: 12px; }
    .tc-infos .tc-meta + .tc-meta::before { content: none; }
    .tc-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 7px; }
    .tc-repere { height: 2px; background: var(--violet); border-radius: 2px; margin: -3px 2px 3px; }
    .tc-col-vide { color: var(--gris); font-size: 12.5px; text-align: center; padding: 18px 6px; border: 1px dashed var(--ligne-forte); border-radius: 8px; }
    .tc-col-pied { color: var(--gris); font-size: 12px; text-align: center; padding: 4px; }

    .tc-grille { display: grid; grid-template-columns: 1fr 1fr; gap: 0 12px; }
    .tc-etiq { display: flex; flex-wrap: wrap; gap: 5px; align-items: center; border: 1px solid var(--ligne); border-radius: 7px; background: var(--champ);
      padding: 3px 6px; min-height: 36px; cursor: text; }
    .tc-etiq:focus-within { border-color: var(--violet); box-shadow: 0 0 0 3px color-mix(in srgb, var(--violet) 18%, transparent); }
    .tc-etiq input { flex: 1; min-width: 120px; border: 0 !important; box-shadow: none !important; background: transparent !important; padding: 4px 2px !important; }
    .tc-etiq .tag { display: inline-flex; align-items: center; gap: 3px; color: var(--encre); }
    .tc-etiq .tag button { border: 0; background: transparent; color: var(--gris); padding: 0; cursor: pointer; display: grid; }
    .tc-etiq .tag button:hover { color: var(--encre); }
    .tc-etiq .tag button svg.ico { width: 11px; height: 11px; margin: 0; }
    .tc-etape-ed { display: flex; gap: 8px; align-items: center; margin-bottom: 6px; }
    .tc-etape-ed input:not([type=checkbox]) { flex: 1; padding: 5px 8px !important; }
    .tc-etape-ed input[type=checkbox] { width: 15px; height: 15px; }
    .tc-champ { display: flex; flex-direction: column; gap: 6px; font-size: 12.5px; font-weight: 500; color: var(--doux); margin-bottom: 14px; }
    .tc-champ .puces { align-self: flex-start; }
    .tc-pied-fenetre { display: flex; align-items: center; gap: 8px; margin-top: 18px; }
    .tc-pied-fenetre .espace { flex: 1; }
  `;
  document.head.append(style);

  // --------------------------------------------------------------- outils
  const txt = s => document.createTextNode(String(s ?? ""));   // texte saisi : jamais traduit
  const racine = () => $("#vue-taches");
  const visible = () => racine()?.classList.contains("actif") && document.visibilityState === "visible";
  const sansAccents = s => String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const deux = n => String(n).padStart(2, "0");
  const isoJour = d => `${d.getFullYear()}-${deux(d.getMonth() + 1)}-${deux(d.getDate())}`;
  const decaler = (iso, jours) => { const d = new Date(iso + "T00:00"); d.setDate(d.getDate() + jours); return isoJour(d); };
  const erreur = e => toast(e.message, "erreur");

  function dateCourte(iso, avecJour) {
    const d = new Date(iso + "T00:00");
    const o = { day: "numeric", month: "short" };
    if (avecJour) o.weekday = "short";
    if (d.getFullYear() !== new Date().getFullYear()) o.year = "numeric";
    return d.toLocaleDateString(I18N.locale(), o);
  }

  /** Le texte de l'échéance et sa couleur d'état. */
  function echeance(x) {
    if (!x.echeance) return null;
    const auj = T.r?.aujourdhui || isoJour(new Date());
    let texte;
    if (x.echeance === auj) texte = x.heure || t("Aujourd'hui");
    else if (x.echeance === decaler(auj, 1)) texte = t("Demain") + (x.heure ? " " + x.heure : "");
    else if (x.echeance === decaler(auj, -1)) texte = t("Hier") + (x.heure ? " " + x.heure : "");
    else {
      const proche = Math.abs(new Date(x.echeance + "T00:00") - new Date(auj + "T00:00")) < 7 * 864e5;
      texte = dateCourte(x.echeance, proche) + (x.heure ? ", " + x.heure : "");
    }
    const couleur = x.statut === "fait" ? "gris" : x.groupe === "retard" ? "rouge" : x.groupe === "aujourdhui" ? "ambre" : "gris";
    return el("span", { class: "etat-txt " + couleur }, txt(texte));
  }

  function priorite(x) {
    if (x.priorite === "haute") return el("span", { class: "tc-prio haute", title: "Priorité haute" }, icone("flag"));
    if (x.priorite === "basse") return el("span", { class: "tc-prio basse", title: "Priorité basse" }, icone("arrow-down"));
    return null;
  }

  function etapes(x) {
    const n = (x.liste || []).length;
    if (!n) return null;
    return el("span", { class: "tc-meta" }, icone("list-checks"), txt(`${x.liste.filter(e => e.fait).length}/${n}`));
  }

  function nomApplication(nom) {
    return VUES[nom]?.titre ? I18N.traduire(VUES[nom].titre) : nom;
  }

  // -------------------------------------------------------------- données
  async function charger() {
    if (!localStorage.getItem("mes-outils-taches-vue") && S.config?.vue_taches) {
      T.vue = S.config.vue_taches;
    }
    T.r = await api("/api/taches/liste", {});
    dessiner();
  }
  const recharger = () => charger().catch(erreur);

  /** Les contacts de l'application Contacts, ou null si elle est absente. */
  async function chargerContacts() {
    try {
      const r = await api("/api/contacts/liste", {});
      const liste = Array.isArray(r) ? r : r.contacts;
      T.contacts = Array.isArray(liste) ? liste.filter(c => c && c.id != null) : null;
    } catch { T.contacts = null; }
  }

  // Les groupes changent avec l'heure (une tâche passe « en retard »).
  setInterval(() => { if (visible() && T.r && !T.glisse && !$("#voile").classList.contains("visible")) recharger(); }, 60000);

  function filtrees() {
    const mots = sansAccents(T.recherche).split(/\s+/).filter(Boolean);
    return (T.r?.taches || []).filter(x => {
      if (T.etiquette && !(x.etiquettes || []).includes(T.etiquette)) return false;
      if (T.client && x.client !== T.client) return false;
      if (T.priorite && x.priorite !== T.priorite) return false;
      if (!mots.length) return true;
      const tout = sansAccents([x.titre, x.description, x.client, ...(x.etiquettes || []), ...(x.liste || []).map(e => e.texte)].join(" "));
      return mots.every(m => tout.includes(m));
    });
  }
  const filtreActif = () => !!(T.recherche || T.etiquette || T.client || T.priorite);

  // -------------------------------------------------------------- dessin
  function dessiner() {
    const ouvertes = (T.r.taches || []).filter(x => x.statut !== "fait").length;
    const ancienneRecherche = $(".tc-recherche", racine());
    const avaitFocus = ancienneRecherche && document.activeElement === ancienneRecherche;
    racine().replaceChildren(
      el("div", { class: "barre-vue" },
        el("h2", {}, icone("list-checks"), "Tâches", el("span", { class: "compte" }, String(ouvertes))),
        el("div", { class: "espace" }),
        el("div", { class: "puces" }, [["liste", "Liste", "list"], ["tableau", "Tableau", "kanban"]].map(([v, lib, ic]) =>
          el("button", { class: "puce" + (T.vue === v ? " actif" : ""), onclick: () => changerVue(v) }, icone(ic), lib))),
        el("button", { class: "btn principal", onclick: () => editer(null) }, icone("plus"), "Nouvelle tâche")),
      barreFiltres(),
      el("div", { class: "tc-contenu" }, T.vue === "tableau" ? tableau() : liste()));
    if (avaitFocus) { const r = $(".tc-recherche", racine()); r.focus(); r.setSelectionRange(r.value.length, r.value.length); }
  }

  function changerVue(v) {
    T.vue = v;
    try { localStorage.setItem("mes-outils-taches-vue", v); } catch {}
    dessiner();
  }

  /** Redessine seulement le contenu (la recherche garde le focus). */
  function redessinerContenu() {
    const c = $(".tc-contenu", racine());
    if (c) c.replaceChildren(...[T.vue === "tableau" ? tableau() : liste()].flat(Infinity));
    const effacer = $(".tc-effacer", racine());
    if (effacer) effacer.hidden = !filtreActif();
  }

  function barreFiltres() {
    const choix = (valeur, tous, options, onchange) => {
      const s = el("select", { onchange: e => { onchange(e.target.value); redessinerContenu(); } },
        el("option", { value: "" }, tous), options.map(([v, lib]) => el("option", { value: v }, lib)));
      s.value = valeur;
      return s;
    };
    const etiquettes = T.r.etiquettes || [], clients = T.r.clients || [];
    if (T.etiquette && !etiquettes.includes(T.etiquette)) T.etiquette = "";
    if (T.client && !clients.includes(T.client)) T.client = "";
    const recherche = el("input", { class: "tc-recherche", type: "search", placeholder: "Rechercher une tâche", value: T.recherche,
      oninput: e => { T.recherche = e.target.value; redessinerContenu(); } });
    return el("div", { class: "tc-filtres" },
      el("label", { class: "champ-recherche" }, el("span", {}, icone("search")), recherche),
      etiquettes.length ? choix(T.etiquette, "Toutes les étiquettes", etiquettes.map(e => [e, txt("#" + e)]), v => (T.etiquette = v)) : null,
      clients.length ? choix(T.client, "Tous les clients", clients.map(c => [c, txt(c)]), v => (T.client = v)) : null,
      choix(T.priorite, "Toutes les priorités", [["haute", t("Haute")], ["normale", t("Normale")], ["basse", t("Basse")]], v => (T.priorite = v)),
      el("button", { class: "btn discret tc-effacer", hidden: filtreActif() ? null : "", onclick: () => {
        T.recherche = T.etiquette = T.client = T.priorite = ""; dessiner(); } }, icone("x"), "Effacer les filtres"));
  }

  // ---------------------------------------------------------- affichage Liste
  function liste() {
    const toutes = filtrees();
    const blocs = [ajoutRapide()];
    const ouvertes = toutes.filter(x => x.statut !== "fait");
    for (const [g, titre] of GROUPES) {
      const du = ouvertes.filter(x => x.groupe === g);
      if (!du.length) continue;
      blocs.push(el("div", { class: "lignes" },
        el("div", { class: "titre-lignes tc-titre-groupe" + (g === "retard" ? " rouge" : "") }, titre, el("span", { class: "n" }, String(du.length))),
        du.map(ligne)));
    }
    const faites = toutes.filter(x => x.statut === "fait").sort((a, b) => (b.fait_le || "").localeCompare(a.fait_le || ""));
    if (!ouvertes.length && !faites.length) {
      blocs.push(el("div", { class: "vide" }, icone("list-checks"),
        filtreActif() ? "Aucune tâche ne correspond à la recherche." : "Aucune tâche pour l'instant. Écrivez-en une ci-dessus."));
    }
    if (faites.length) {
      const montrees = faites.slice(0, MAX_FAITES);
      blocs.push(el("div", { class: "lignes" },
        el("div", { class: "titre-lignes tc-titre-groupe plie" + (T.faitesOuvertes ? " ouvert" : ""),
          onclick: () => { T.faitesOuvertes = !T.faitesOuvertes; redessinerContenu(); } },
          icone("chevron-right"), "Faites", el("span", { class: "n" }, String(faites.length))),
        T.faitesOuvertes ? [montrees.map(ligne),
          faites.length > montrees.length ? el("div", { class: "ligne" }, el("div", { class: "ligne-meta" },
            t("{n} plus anciennes", { n: faites.length - montrees.length }))) : null] : null));
    }
    return blocs;
  }

  function ajoutRapide() {
    const saisie = el("input", { placeholder: "Ajouter une tâche… (Entrée)", maxlength: 200, onkeydown: async e => {
      if (e.key !== "Enter" || !saisie.value.trim()) return;
      try {
        await api("/api/taches/creer", { titre: saisie.value, etiquettes: T.etiquette ? [T.etiquette] : [],
          client: T.client || "", priorite: S.config?.priorite_taches || "normale" });
        saisie.value = "";
        T.r = await api("/api/taches/liste", {});
        dessiner();
        $(".tc-ajout input", racine())?.focus();
      } catch (err) { erreur(err); }
    } });
    return el("div", { class: "lignes tc-ajout-bloc" },
      el("div", { class: "ligne tc-ajout", onclick: () => saisie.focus() },
        el("span", { class: "ligne-ic tc-ic" }, icone("plus")), saisie, el("kbd", {}, "Entrée")));
  }

  function caseFait(x, petite = false) {
    const fait = x.statut === "fait";
    return el("button", { class: "tc-case" + (fait ? " fait" : "") + (petite ? " petite" : ""), title: fait ? "Marquer à faire" : "Marquer comme faite",
      onclick: e => { e.stopPropagation(); cocher(x, !fait); } }, icone("check"));
  }

  function ligne(x) {
    const ouverte = T.ouvertes.has(x.id);
    const aDetail = !!(x.description || (x.liste || []).length || x.origine);
    const meta = [
      x.statut === "en_cours" ? el("span", { class: "tc-meta tc-encours" }, icone("circle-dot"), "En cours") : null,
      x.client ? el("span", { class: "tc-meta" }, icone("user"), txt(x.client)) : null,
      etapes(x),
      x.recurrence ? el("span", { class: "tc-meta", title: RECURRENCES[x.recurrence] }, icone("repeat"), RECURRENCES[x.recurrence]) : null,
      x.description ? el("span", { class: "tc-meta" }, txt(x.description.split("\n")[0])) : null,
    ].filter(Boolean);
    const rangee = el("div", { class: "ligne cliquable tc-ligne-draggable" + (x.statut === "fait" ? " tc-faite" : "") + (ouverte ? " ouverte" : ""), draggable: "true", "data-id": x.id,
      onclick: () => {
        if (!aDetail) { editer(x); return; }
        ouverte ? T.ouvertes.delete(x.id) : T.ouvertes.add(x.id);
        redessinerContenu();
      } },
      el("span", { class: "ligne-ic tc-ic" }, caseFait(x)),
      el("div", { class: "ligne-corps" },
        el("div", { class: "ligne-titre" }, el("span", { title: x.titre }, txt(x.titre)),
          (x.etiquettes || []).map(e => el("span", { class: "tag" }, txt("#" + e)))),
        meta.length ? el("div", { class: "ligne-meta" }, meta) : null),
      el("div", { class: "ligne-cote" }, priorite(x), echeance(x)),
      el("div", { class: "ligne-actions" },
        el("button", { class: "icone-btn", title: "Modifier", onclick: e => { e.stopPropagation(); editer(x); } }, icone("pencil")),
        el("button", { class: "icone-btn danger", title: "Supprimer", onclick: e => { e.stopPropagation(); supprimer(x); } }, icone("trash-2"))));
    rangee.addEventListener("dragstart", e => {
      e.dataTransfer.effectAllowed = "move";
      try { e.dataTransfer.setData("text/plain", x.id); } catch {}
      rangee.classList.add("glisse");
      T.glisseListe = x.id;
    });
    rangee.addEventListener("dragend", () => {
      rangee.classList.remove("glisse");
      document.querySelectorAll(".tc-ligne-draggable").forEach(el => el.classList.remove("survol"));
      T.glisseListe = null;
    });
    rangee.addEventListener("dragover", e => {
      if (!T.glisseListe || T.glisseListe === x.id) return;
      e.preventDefault();
      e.dataTransfer.dropEffect = "move";
      rangee.classList.add("survol");
    });
    rangee.addEventListener("dragleave", () => rangee.classList.remove("survol"));
    rangee.addEventListener("drop", e => {
      e.preventDefault();
      rangee.classList.remove("survol");
      const fromId = T.glisseListe;
      const toId = x.id;
      if (!fromId || fromId === toId) return;
      const container = rangee.closest(".lignes");
      if (!container) return;
      const ids = [...container.querySelectorAll(".tc-ligne-draggable")].map(el => el.dataset.id).filter(i => i && i !== fromId);
      const pos = ids.indexOf(toId);
      ids.splice(pos < 0 ? ids.length : pos, 0, fromId);
      T.glisseListe = null;
      api("/api/taches/reorganiser_liste", { ordre: ids })
        .then(() => recharger())
        .catch(err => { erreur(err); recharger(); });
    });
    if (!ouverte || !aDetail) return rangee;
    return [rangee, el("div", { class: "ligne-detail" },
      x.description ? el("p", { class: "tc-desc" }, txt(x.description)) : null,
      (x.liste || []).map(e => el("div", { class: "tc-etape" + (e.fait ? " fait" : ""), onclick: () => cocherEtape(x, e) },
        el("span", { class: "tc-case petite" + (e.fait ? " fait" : "") }, icone("check")), el("span", {}, txt(e.texte)))),
      x.origine ? el("div", { class: "tc-origine" }, t("Ajoutée par {app}", { app: nomApplication(x.origine) })) : null,
      el("div", { class: "tc-detail-pied" },
        el("button", { class: "btn petit", onclick: () => editer(x) }, icone("pencil"), "Modifier")))];
  }

  // -------------------------------------------------------- affichage Tableau
  function tableau() {
    const toutes = filtrees();
    return el("div", { class: "tc-tableau" }, COLONNES.map(([statut, titre]) => {
      let cartes = toutes.filter(x => x.statut === statut);
      let reste = 0;
      if (statut === "fait") {
        cartes.sort((a, b) => (b.fait_le || "").localeCompare(a.fait_le || ""));
        reste = Math.max(0, cartes.length - MAX_FAITES);
        cartes = cartes.slice(0, MAX_FAITES);
      } else cartes.sort((a, b) => (a.ordre ?? 0) - (b.ordre ?? 0));
      const corps = el("div", { class: "tc-cartes" },
        cartes.length ? cartes.map(carte) : el("div", { class: "tc-col-vide" }, "Glissez une tâche ici"));
      const col = el("div", { class: "tc-col", "data-statut": statut },
        el("div", { class: "tc-col-titre" }, titre, el("span", { class: "n" }, String(toutes.filter(x => x.statut === statut).length))),
        corps, reste ? el("div", { class: "tc-col-pied" }, t("{n} plus anciennes", { n: reste })) : null);
      col.addEventListener("dragover", e => survoler(e, col, corps));
      col.addEventListener("dragleave", e => { if (!col.contains(e.relatedTarget)) quitter(col); });
      col.addEventListener("drop", e => deposer(e, col, corps, statut));
      return col;
    }));
  }

  function carte(x) {
    const c = el("div", { class: "tc-carte" + (x.statut === "fait" ? " tc-faite" : ""), draggable: "true", "data-id": x.id,
      onclick: () => editer(x) },
      el("div", { class: "tc-carte-titre" }, el("span", {}, txt(x.titre)), priorite(x)),
      el("div", { class: "tc-infos" },
        echeance(x),
        x.client ? el("span", { class: "tc-meta" }, icone("user"), txt(x.client)) : null,
        etapes(x),
        x.recurrence ? el("span", { class: "tc-meta", title: RECURRENCES[x.recurrence] }, icone("repeat")) : null),
      (x.etiquettes || []).length ? el("div", { class: "tc-tags" }, x.etiquettes.map(e => el("span", { class: "tag" }, txt("#" + e)))) : null);
    if (!c.querySelector(".tc-infos").children.length) c.querySelector(".tc-infos").remove();
    c.addEventListener("dragstart", e => {
      T.glisse = x.id;
      e.dataTransfer.effectAllowed = "move";
      try { e.dataTransfer.setData("text/plain", x.id); } catch {}
      requestAnimationFrame(() => c.classList.add("glisse"));
    });
    c.addEventListener("dragend", () => {
      T.glisse = null;
      c.classList.remove("glisse");
      document.querySelectorAll(".tc-repere").forEach(r => r.remove());
      document.querySelectorAll(".tc-col.survol").forEach(r => r.classList.remove("survol"));
    });
    return c;
  }

  /** La carte avant laquelle déposer (selon la hauteur de la souris), ou null. */
  function carteSuivante(corps, y) {
    for (const c of corps.querySelectorAll(".tc-carte:not(.glisse)")) {
      const b = c.getBoundingClientRect();
      if (y < b.top + b.height / 2) return c;
    }
    return null;
  }

  function survoler(e, col, corps) {
    if (!T.glisse) return;
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    col.classList.add("survol");
    const avant = carteSuivante(corps, e.clientY);
    let repere = $(".tc-repere", corps);
    if (!repere) {
      document.querySelectorAll(".tc-repere").forEach(r => r.remove());
      repere = el("div", { class: "tc-repere" });
    }
    if (avant) { if (repere.nextSibling !== avant) corps.insertBefore(repere, avant); }
    else if (corps.lastChild !== repere) corps.append(repere);
  }

  function quitter(col) {
    col.classList.remove("survol");
    col.querySelectorAll(".tc-repere").forEach(r => r.remove());
  }

  async function deposer(e, col, corps, statut) {
    if (!T.glisse) return;
    e.preventDefault();
    const id = T.glisse;
    const avant = carteSuivante(corps, e.clientY);
    const ids = [...corps.querySelectorAll(".tc-carte")].map(c => c.dataset.id).filter(i => i !== id);
    const position = avant ? ids.indexOf(avant.dataset.id) : ids.length;
    ids.splice(position < 0 ? ids.length : position, 0, id);
    quitter(col);
    T.glisse = null;
    try {
      const r = await api("/api/taches/deplacer", { id, statut, ordre: ids });
      if (r.suivante) annoncerSuivante(r.suivante);
      recharger();
    } catch (err) { erreur(err); recharger(); }
  }

  // ------------------------------------------------------------- actions
  function annoncerSuivante(s) {
    toast(t("Prochaine fois : {date}", { date: dateCourte(s.echeance, true) }), "succes", 2600);
  }

  async function cocher(x, fait) {
    try {
      const r = await api("/api/taches/cocher", { id: x.id, fait });
      if (r.suivante) annoncerSuivante(r.suivante);
      recharger();
    } catch (e) { erreur(e); }
  }

  async function cocherEtape(x, etape) {
    try {
      const maj = await api("/api/taches/etape", { id: x.id, etape_id: etape.id, fait: !etape.fait });
      T.r.taches = T.r.taches.map(y => (y.id === maj.id ? maj : y));
      redessinerContenu();
    } catch (e) { erreur(e); }
  }

  async function supprimer(x) {
    if (!(await confirmer(icone("trash-2"), "Supprimer cette tâche ?", "Elle disparaît définitivement.", "Supprimer"))) return;
    try {
      await api("/api/taches/supprimer", { id: x.id });
      T.ouvertes.delete(x.id);
      toast("Tâche supprimée");
      recharger();
    } catch (e) { erreur(e); }
  }

  // ------------------------------------------------------ fenêtre d'édition
  function champEtiquettes(depart) {
    const valeurs = [...depart];
    const boite = el("div", { class: "tc-etiq" });
    const saisie = el("input", { placeholder: "Ajouter une étiquette", list: "tc-etiquettes", maxlength: 30 });
    const ajouter = () => {
      for (const morceau of saisie.value.split(",")) {
        const v = morceau.trim().replace(/^#/, "");
        if (v && !valeurs.some(x => x.toLowerCase() === v.toLowerCase())) valeurs.push(v);
      }
      saisie.value = "";
      dessinerEtiq();
    };
    const dessinerEtiq = () => boite.replaceChildren(
      ...valeurs.map((v, i) => el("span", { class: "tag" }, txt("#" + v),
        el("button", { type: "button", title: "Retirer", onclick: e => { e.stopPropagation(); valeurs.splice(i, 1); dessinerEtiq(); saisie.focus(); } }, icone("x")))),
      saisie,
      el("datalist", { id: "tc-etiquettes" }, (T.r?.etiquettes || []).filter(e => !valeurs.includes(e)).map(e => el("option", { value: e }))));
    saisie.addEventListener("keydown", e => {
      if (e.key === "Enter" || e.key === ",") { e.preventDefault(); ajouter(); }
      else if (e.key === "Backspace" && !saisie.value && valeurs.length) { valeurs.pop(); dessinerEtiq(); saisie.focus(); }
    });
    saisie.addEventListener("change", () => { if (saisie.value && (T.r?.etiquettes || []).includes(saisie.value)) ajouter(); });
    boite.addEventListener("click", () => saisie.focus());
    dessinerEtiq();
    return { boite, valeurs: () => { ajouter(); return valeurs; } };
  }

  function champEtapes(depart) {
    const etapesEd = depart.map(e => ({ ...e }));
    const boite = el("div", { class: "tc-etapes-ed" });
    const nouvelle = el("input", { placeholder: "Ajouter une étape… (Entrée)", maxlength: 200, onkeydown: e => {
      if (e.key !== "Enter") return;
      e.preventDefault();
      if (!nouvelle.value.trim()) return;
      etapesEd.push({ texte: nouvelle.value.trim(), fait: false });
      nouvelle.value = "";
      dessinerEtapes();
      nouvelle.focus();
    } });
    const dessinerEtapes = () => boite.replaceChildren(
      ...etapesEd.map((e, i) => el("div", { class: "tc-etape-ed" },
        el("input", { type: "checkbox", checked: e.fait ? "" : null, onchange: ev => { e.fait = ev.target.checked; } }),
        el("input", { type: "text", value: e.texte, maxlength: 200, oninput: ev => { e.texte = ev.target.value; } }),
        el("button", { type: "button", class: "icone-btn danger", title: "Retirer", onclick: () => { etapesEd.splice(i, 1); dessinerEtapes(); } }, icone("x")))),
      el("div", { class: "tc-etape-ed" }, el("span", { class: "ligne-ic", style: "width:15px;color:var(--gris)" }, icone("plus")), nouvelle));
    dessinerEtapes();
    return { boite, valeurs: () => {
      if (nouvelle.value.trim()) etapesEd.push({ texte: nouvelle.value.trim(), fait: false });
      return etapesEd.filter(e => e.texte.trim());
    } };
  }

  /** Le choix du client : liste de Contacts si l'application est là, sinon texte libre. */
  function champClient(x) {
    if (T.contacts && T.contacts.length) {
      const s = el("select", {}, el("option", { value: "" }, "Aucun"),
        T.contacts.map(c => el("option", { value: "c:" + c.id }, txt([c.nom, c.entreprise].filter(Boolean).join(" · ") || c.email || c.id))));
      const connu = x.contact_id && T.contacts.some(c => String(c.id) === String(x.contact_id));
      if (x.client && !connu) s.append(el("option", { value: "x:" + x.client }, txt(x.client)));
      s.value = connu ? "c:" + x.contact_id : x.client ? "x:" + x.client : "";
      return { champ: s, valeurs: () => {
        if (s.value.startsWith("c:")) {
          const c = T.contacts.find(y => "c:" + y.id === s.value);
          return { contact_id: String(c.id), client: c.nom || c.entreprise || "" };
        }
        return { contact_id: s.value.startsWith("x:") ? (x.contact_id || "") : "", client: s.value.startsWith("x:") ? s.value.slice(2) : "" };
      } };
    }
    const i = el("input", { value: x.client || "", list: "tc-clients", maxlength: 120 });
    return { champ: el("span", { style: "display:contents" }, i, el("datalist", { id: "tc-clients" }, (T.r?.clients || []).map(c => el("option", { value: c })))),
      valeurs: () => ({ client: i.value.trim(), contact_id: i.value.trim() === (x.client || "") ? (x.contact_id || "") : "" }) };
  }

  function editer(x) {
    const nouveau = !x;
    const b = x ? structuredClone(x) : { titre: "", description: "", echeance: "", heure: "", priorite: S.config?.priorite_taches || "normale",
      etiquettes: T.etiquette ? [T.etiquette] : [], liste: [], recurrence: "", statut: "a_faire", client: T.client || "", contact_id: "" };
    const titre = el("input", { value: b.titre, maxlength: 200 });
    const description = el("textarea", { rows: 2, maxlength: 2000 });
    description.value = b.description || "";
    const date = el("input", { type: "date", value: b.echeance || "" });
    const heure = el("input", { type: "time", value: b.heure || "" });
    const prio = el("select", {}, Object.entries(PRIORITES).map(([v, lib]) => el("option", { value: v }, lib)));
    prio.value = b.priorite || "normale";
    const rec = el("select", { title: "Une fois par jour, semaine ou mois : une fois faite, la tâche revient à la date suivante." },
      Object.entries(RECURRENCES).map(([v, lib]) => el("option", { value: v }, lib)));
    rec.value = b.recurrence || "";
    let statut = b.statut || "a_faire";
    const puces = el("div", { class: "puces tc-puces-statut" }, COLONNES.map(([v, lib]) =>
      el("button", { type: "button", class: "puce" + (v === statut ? " actif" : ""), onclick: e => {
        statut = v; [...puces.children].forEach(p => p.classList.toggle("actif", p === e.currentTarget)); } }, lib)));
    const etiq = champEtiquettes(b.etiquettes || []);
    const etapesEd = champEtapes(b.liste || []);
    const client = champClient(b);

    const valider = async () => {
      const donnees = { titre: titre.value, description: description.value, echeance: date.value, heure: date.value ? heure.value : "",
        priorite: prio.value, recurrence: rec.value, statut, etiquettes: etiq.valeurs(), liste: etapesEd.valeurs(), ...client.valeurs() };
      try {
        let r;
        if (nouveau) r = { tache: await api("/api/taches/creer", donnees) };
        else r = await api("/api/taches/modifier", { tache: { id: x.id, ...donnees } });
        fermer();
        toast(nouveau ? "Tâche ajoutée" : "Tâche enregistrée", "succes", 1600);
        if (r.suivante) annoncerSuivante(r.suivante);
        recharger();
      } catch (e) { erreur(e); titre.focus(); }
    };
    titre.addEventListener("keydown", e => { if (e.key === "Enter") valider(); });

    fenetre([
      el("h3", {}, nouveau ? "Nouvelle tâche" : "Modifier la tâche"),
      el("label", { class: "champ" }, "Titre", titre),
      el("label", { class: "champ" }, "Description (facultatif)", description),
      el("div", { class: "tc-grille" },
        el("label", { class: "champ" }, "Échéance", date),
        el("label", { class: "champ" }, "Heure (facultatif)", heure),
        el("label", { class: "champ" }, "Priorité", prio),
        el("label", { class: "champ" }, "Répétition", rec),
        el("label", { class: "champ" }, "Client (facultatif)", client.champ),
        el("div", { class: "tc-champ" }, "Statut", puces)),
      el("div", { class: "tc-champ" }, "Étiquettes", etiq.boite),
      el("div", { class: "tc-champ" }, "Liste de contrôle", etapesEd.boite),
      x?.origine ? el("div", { class: "tc-origine" }, t("Ajoutée par {app}", { app: nomApplication(x.origine) })) : null,
      el("div", { class: "tc-pied-fenetre" },
        nouveau ? null : el("button", { class: "btn discret", onclick: async () => { fermer(); await supprimer(x); } }, icone("trash-2"), "Supprimer"),
        el("div", { class: "espace" }),
        el("button", { class: "btn", onclick: fermer }, "Annuler"),
        el("button", { class: "btn principal", onclick: valider }, nouveau ? "Ajouter" : "Enregistrer"))]);
    $("#fenetre").style.width = "min(600px, 94vw)";
    setTimeout(() => titre.focus(), 60);
  }

  // ------------------------------------------------------------- accueil
  async function carteAccueil() {
    let r;
    try { r = await api("/api/taches/jour", { limite: 5 }); } catch { return null; }
    if (!r || !r.total) return null;
    return el("div", { class: "carte-jour", onclick: () => montrerVue("taches") },
      el("h4", {}, icone("list-checks"), "Tâches"),
      r.taches.map(x => el("div", { class: "ligne-jour" },
        el("span", { class: "heure", style: x.groupe === "retard" ? "color:var(--rouge-texte)" : "" },
          x.groupe === "retard" ? "Retard" : x.heure ? txt(x.heure) : "Jour"),
        el("span", { style: "overflow:hidden;text-overflow:ellipsis;white-space:nowrap" }, txt(x.titre)))),
      r.total > r.taches.length ? el("div", { class: "rien" }, t("{n} autres", { n: r.total - r.taches.length })) : null);
  }

  function commandes() {
    const ouvrir = x => { montrerVue("taches"); setTimeout(() => editer(x), 80); };
    const liste = [{ icone: icone("plus"), titre: "Nouvelle tâche", detail: "Tâches", action: () => ouvrir(null) }];
    for (const x of (T.r?.taches || []).filter(y => y.statut !== "fait").slice(0, 30)) {
      liste.push({ icone: icone("list-checks"), titre: x.titre, detail: "Tâches", action: () => ouvrir(x) });
    }
    return liste;
  }

  VUES.taches = {
    afficher: async () => { await chargerContacts(); await charger().catch(erreur); },
    titre: "Tâches", icone: icone("list-checks"), groupe: "quotidien", ordre: 25,
    description: "Tâches avec échéances, priorités, étiquettes, sous-étapes et répétitions, en liste ou en tableau.",
    profils: ["freelance", "assistant_virtuel", "assistant_direction", "developpeur"],
    carteAccueil, commandes,
  };
})();
