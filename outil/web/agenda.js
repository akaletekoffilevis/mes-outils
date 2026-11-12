"use strict";
/* Onglet « Agenda » : vue semaine et vue mois, rendez-vous colorés,
   rappels par la bulle (donnees/agenda.json). */
(() => {
  I18N.ajouter({
    "Agenda": "Calendar",
    "Pas de rappel": "No reminder",
    "À l'heure": "At the time",
    "5 min avant": "5 min before",
    "15 min avant": "15 min before",
    "30 min avant": "30 min before",
    "1 h avant": "1 h before",
    "La veille": "The day before",
    "Aujourd'hui": "Today",
    "Précédent": "Previous",
    "Suivant": "Next",
    "Semaine": "Week",
    "Mois": "Month",
    "＋ Rendez-vous": "＋ Appointment",
    "Rendez-vous": "Appointment",
    "jour": "all day",
    "à {heure}": "at {heure}",
    "⧉ Copié au {quand}": "⧉ Copied to {quand}",
    " Déplacé au {quand}": " Moved to {quand}",
    "glisser pour déplacer, Ctrl + glisser pour dupliquer": "drag to move, Ctrl + drag to duplicate",
    "copie": "copy", " + {n} autres": "+ {n} more",
    " Glissez un rendez-vous pour le déplacer · Ctrl + glisser pour le dupliquer": " Drag an appointment to move it · Ctrl + drag to duplicate it",
    "Début": "Start",
    "Fin": "End",
    "Titre": "Title",
    "Jour": "Day",
    "Toute la journée": "All day",
    "Lieu": "Place",
    "Rappel (par la bulle)": "Reminder (from the bubble)",
    "Couleur": "Colour",
    "Répétition": "Repeat",
    "Aucune": "None",
    "Chaque jour": "Every day",
    "Chaque semaine": "Every week",
    "Chaque mois": "Every month",
    "Chaque année": "Every year",
    "Notes": "Notes",
    "ex. Réunion client": "e.g. Client meeting",
    "ex. Bureau, Teams…": "e.g. Office, Teams…",
    "Détails, ordre du jour…": "Details, agenda…",
    " Rendez-vous": " Appointment",
    "⧉ Copie du rendez-vous": "⧉ Copy of the appointment",
    " Nouveau rendez-vous": " New appointment",
    "Supprimer ce rendez-vous ?": "Delete this appointment?",
    "Supprimer": "Delete",
    " Supprimer": " Delete",
    " Rendez-vous supprimé": " Appointment deleted",
    "Créer une copie (choisissez ensuite le jour)": "Create a copy (then choose the day)",
    "⧉ Dupliquer": "⧉ Duplicate",
    "⧉ Copie prête : changez le jour si besoin, puis « Ajouter »": "⧉ Copy ready: change the day if needed, then “Add”",
    "Annuler": "Cancel",
    "Enregistrer": "Save",
    "Ajouter": "Add",
    "Indiquez un titre": "Enter a title",
    "La fin doit être après le début": "The end must be after the start",
    "Rendez-vous modifié": "Appointment updated",
    "Rendez-vous ajouté": "Appointment added",
  });

  const COULEURS_RDV = ["#6c4cf5", "#ff7a59", "#18b597", "#ffb020", "#e5488d", "#2f8cff", "#475569"];
  const RAPPELS = [["", "Pas de rappel"], ["0", "À l'heure"], ["5", "5 min avant"], ["15", "15 min avant"], ["30", "30 min avant"], ["60", "1 h avant"], ["1440", "La veille"]];
  const H0 = 6, H1 = 23, PX = 46;            // heures affichées, pixels par heure
  /** « Lun », « Mar »… (ou « Mon », « Tue »…) dans la langue choisie. */
  const nomsJours = () => [...Array(7)].map((_, i) => {
    // Le 1er janvier 2024 est un lundi.
    const j = new Date(2024, 0, 1 + i).toLocaleDateString(I18N.locale(), { weekday: "short" }).replace(/\.$/, "");
    return j.charAt(0).toUpperCase() + j.slice(1);
  });
  const A = { evenements: [], bruts: [], mode: "semaine", ref: new Date() };

  const style = document.createElement("style");
  style.textContent = `
    .agenda-carte { background: var(--carte); border-radius: var(--rayon); box-shadow: var(--ombre); overflow: hidden; animation: apparait .35s both; }
    .semaine { display: flex; flex-direction: column; }
    .entete-semaine { display: grid; grid-template-columns: 54px repeat(7, minmax(0, 1fr)); padding-right: 8px; }
    .entete-semaine .tete-jour { text-align: center; padding: 10px 4px; border-bottom: 1px solid var(--ligne); font-size: 13px; color: var(--doux); font-weight: 700; }
    .entete-semaine .tete-jour b { display: block; font-size: 20px; color: var(--encre); }
    .entete-semaine .tete-jour.auj b { background: var(--violet); color: var(--sur-violet); border-radius: 12px; width: 36px; margin: 2px auto 0; }
    .bande-jour { display: grid; grid-template-columns: 54px repeat(7, minmax(0, 1fr)); border-bottom: 1px solid var(--ligne); min-height: 30px; padding-right: 8px; }
    .bande-jour .case { padding: 3px; display: flex; flex-direction: column; gap: 3px; border-left: 1px solid var(--ligne); }
    .bande-jour .etiquette-h { font-size: 11px; color: var(--gris); text-align: right; padding: 8px 6px 0 0; }
    .defilement { max-height: max(320px, calc(100vh - var(--entete, 74px) - 210px)); overflow-y: scroll; }
    .defilement::-webkit-scrollbar { width: 8px; }
    .defilement::-webkit-scrollbar-thumb { background: var(--ligne); border-radius: 8px; }
    .corps-semaine { display: grid; grid-template-columns: 54px repeat(7, minmax(0, 1fr)); position: relative; }
    .heures div { height: ${PX}px; font-size: 11px; color: var(--gris); text-align: right; padding-right: 6px; transform: none; }
    .colonne { position: relative; border-left: 1px solid var(--ligne); background-image: repeating-linear-gradient(to bottom, transparent 0, transparent ${PX - 1}px, var(--ligne) ${PX - 1}px, var(--ligne) ${PX}px); cursor: copy; }
    .colonne.auj { background-color: var(--surface); }
    .rdv { position: absolute; left: 3px; right: 3px; border-radius: 10px; padding: 4px 7px; font-size: 12.5px; color: #fff; overflow: hidden; cursor: pointer;
           box-shadow: 0 6px 14px -8px rgba(0,0,0,.45); transition: transform .15s, filter .15s; animation: apparait .3s both; }
    .rdv:hover { transform: scale(1.02); filter: brightness(1.05); z-index: 3; }
    .rdv b { display: block; font-size: 12.5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .rdv span { opacity: .9; font-size: 11.5px; }
    .rdv.jour { position: static; padding: 3px 8px; }
    .maintenant { position: absolute; left: 0; right: 0; height: 2px; background: var(--rouge); z-index: 4; pointer-events: none; }
    .maintenant::before { content: ""; position: absolute; left: -5px; top: -4px; width: 10px; height: 10px; border-radius: 50%; background: var(--rouge); }
    .mois { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); }
    .mois .nom-jour { text-align: center; font-size: 12px; font-weight: 700; color: var(--doux); padding: 10px 0; border-bottom: 1px solid var(--ligne); }
    .mois .jour { min-height: 98px; border-left: 1px solid var(--ligne); border-bottom: 1px solid var(--ligne); padding: 6px; cursor: pointer; transition: background .15s; }
    .mois .jour:hover { background: var(--violet-clair); }
    .mois .jour.autre { background: var(--surface); color: var(--gris); }
    .mois .jour .num { font-weight: 600; font-size: 13px; margin-bottom: 4px; display: inline-block; min-width: 24px; text-align: center; border-radius: 8px; }
    .mois .jour.auj .num { background: var(--violet); color: var(--sur-violet); }
    .puce-rdv { font-size: 11.5px; border-radius: 7px; padding: 2px 6px; color: #fff; margin-bottom: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .plus-rdv { font-size: 11.5px; color: var(--doux); font-weight: 700; }
    .titre-periode { font-size: 19px; font-weight: 600; margin: 0 6px; min-width: 250px; }
    .grille-form { display: grid; grid-template-columns: 1fr 1fr; gap: 0 12px; }
    .rdv, .puce-rdv { cursor: grab; user-select: none; }
    .rdv.glisse { cursor: grabbing; opacity: .9; z-index: 10; transform: scale(1.03); box-shadow: 0 16px 30px -10px rgba(31,26,58,.55); transition: none; }
    .rdv.glisse.copie { outline: 2px dashed #fff; outline-offset: -4px; }
    .case.survol, .mois .jour.survol { background: var(--violet-clair) !important; box-shadow: inset 0 0 0 2px var(--violet); }
    .astuce-agenda { font-size: 12.5px; color: var(--doux); margin: -10px 0 12px; }
  `;
  document.head.append(style);

  // -- dates ---------------------------------------------------------------
  const pad = n => String(n).padStart(2, "0");
  const isoJour = d => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  const isoMinute = d => `${isoJour(d)}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
  const lundi = d => { const x = new Date(d); x.setHours(0, 0, 0, 0); x.setDate(x.getDate() - ((x.getDay() + 6) % 7)); return x; };
  const plusJours = (d, n) => { const x = new Date(d); x.setDate(x.getDate() + n); return x; };
  const debutDe = e => new Date(e.debut);
  const finDe = e => e.fin ? new Date(e.fin) : new Date(debutDe(e).getTime() + 3600e3);
  const memeJourA = (a, b) => a.toDateString() === b.toDateString();
  // Données de l'utilisateur (titres, lieux) : jamais traduites.
  const brut = s => document.createTextNode(s ?? "");
  const titreDe = e => (e.titre ? brut(e.titre) : t("Rendez-vous"));
  const astuce = e => (e.titre || "") + "— " + t("glisser pour déplacer, Ctrl + glisser pour dupliquer");

  /** Étend les rendez-vous récurrents en instances sur la plage visible
   *  (±2 mois autour de la date de référence), sans toucher aux données. */
  function etendreRecurrences(bruts, ref) {
    const resultat = [];
    const debut = new Date(ref.getFullYear(), ref.getMonth() - 2, 1);
    const fin = new Date(ref.getFullYear(), ref.getMonth() + 3, 0);
    for (const e of bruts) {
      if (!e.recurrence) { resultat.push(e); continue; }
      const deb0 = debutDe(e);
      const fin0 = finDe(e);
      const duree = fin0 - deb0;
      let d = new Date(deb0);
      // Aligner le premier jour sur la récurrence (début de la série).
      while (d < debut) {
        if (e.recurrence === "daily") d.setDate(d.getDate() + 1);
        else if (e.recurrence === "weekly") d.setDate(d.getDate() + 7);
        else if (e.recurrence === "monthly") d.setMonth(d.getMonth() + 1);
        else if (e.recurrence === "yearly") d.setFullYear(d.getFullYear() + 1);
        else break;
        if (d > fin) break;
      }
      while (d <= fin) {
        if (d >= debut) {
          const copie = structuredClone(e);
          copie.debut = isoMinute(d);
          copie.fin = isoMinute(new Date(d.getTime() + duree));
          copie._virtuel = true;
          copie._serie = e.id;
          resultat.push(copie);
        }
        if (e.recurrence === "daily") d.setDate(d.getDate() + 1);
        else if (e.recurrence === "weekly") d.setDate(d.getDate() + 7);
        else if (e.recurrence === "monthly") d.setMonth(d.getMonth() + 1);
        else if (e.recurrence === "yearly") d.setFullYear(d.getFullYear() + 1);
        else break;
        if (d > fin) break;
      }
    }
    return resultat;
  }

  async function charger() {
    A.bruts = await api("/api/agenda");
    A.evenements = etendreRecurrences(A.bruts, A.ref);
    dessiner();
  }

  function barre() {
    const lun = lundi(A.ref), dim = plusJours(lun, 6);
    const titre = A.mode === "jour"
      ? A.ref.toLocaleDateString(I18N.locale(), { weekday: "long", day: "numeric", month: "long", year: "numeric" })
      : A.mode === "semaine"
      ? (lun.getMonth() === dim.getMonth()
        ? `${lun.getDate()} – ${dim.getDate()} ${dim.toLocaleDateString(I18N.locale(), { month: "long", year: "numeric" })}`
        : `${lun.toLocaleDateString(I18N.locale(), { day: "numeric", month: "short" })} – ${dim.toLocaleDateString(I18N.locale(), { day: "numeric", month: "short", year: "numeric" })}`)
      : A.ref.toLocaleDateString(I18N.locale(), { month: "long", year: "numeric" });
    const decaler = sens => {
      if (A.mode === "jour") A.ref = plusJours(A.ref, sens);
      else if (A.mode === "semaine") A.ref = plusJours(A.ref, 7 * sens);
      else A.ref = new Date(A.ref.getFullYear(), A.ref.getMonth() + sens, 1);
      A.evenements = etendreRecurrences(A.bruts, A.ref);
      dessiner();
    };
    return el("div", { class: "barre-vue" },
      el("h2", {}, icone("calendar"), t("Agenda")),
      el("button", { class: "btn", onclick: () => { A.ref = new Date(); dessiner(); } }, "Aujourd'hui"),
      el("button", { class: "btn discret", title: "Précédent", onclick: () => decaler(-1) }, "‹"),
      el("button", { class: "btn discret", title: "Suivant", onclick: () => decaler(1) }, "›"),
      el("span", { class: "titre-periode" }, titre.charAt(0).toUpperCase() + titre.slice(1)),
      el("div", { class: "espace" }),
      el("div", { class: "puces" }, [["jour", "Jour"], ["semaine", "Semaine"], ["mois", "Mois"]].map(([m, libelle]) =>
        el("button", { class: "puce " + (A.mode === m ? " actif" : ""), onclick: () => { A.mode = m; dessiner(); } }, libelle))),
      el("button", { class: "btn principal", onclick: () => editer(nouveau(new Date())) }, "＋ Rendez-vous"));
  }

  function nouveau(jour, heure) {
    const d = new Date(jour);
    if (heure === undefined) { const h = new Date().getHours() + 1; d.setHours(Math.min(Math.max(h, 8), 20), 0, 0, 0); }
    else d.setHours(heure, 0, 0, 0);
    return { titre: "", debut: isoMinute(d), fin: isoMinute(new Date(d.getTime() + 3600e3)), journee: false, couleur: COULEURS_RDV[0], rappel_minutes: Number(S.config?.rappel_agenda ?? 15), lieu: "", notes: "", recurrence: "" };
  }

  // -- déplacer, dupliquer ------------------------------------------------------
  /** Déplacer (ou copier) un rendez-vous à une nouvelle date de début, en
   *  gardant sa durée. Un rendez-vous déplacé retrouve son rappel. */
  async function deplacerVers(e, nouveauDebut, copier) {
    // Un rendez-vous récurrent est déplacé comme sa série.
    if (e._virtuel && e._serie) {
      const original = A.bruts.find(x => x.id === e._serie);
      if (original) e = original;
    }
    const duree = finDe(e) - debutDe(e);
    const x = structuredClone(e);
    x.debut = isoMinute(nouveauDebut);
    x.fin = isoMinute(new Date(nouveauDebut.getTime() + duree));
    if (copier) { delete x.id; delete x.cree; x.rappel_fait = false; }
    if (!copier && x.debut === e.debut) return;
    try {
      await api("/api/agenda/enregistrer", { element: x });
      await charger();
      const quand = nouveauDebut.toLocaleDateString(I18N.locale(), { weekday: "short", day: "numeric", month: "short" }) + (x.journee ? "" : t("à {heure}", { heure: x.debut.slice(11, 16) }));
      toast(t(copier ? "⧉ Copié au {quand}" : " Déplacé au {quand}", { quand }), "succes");
    } catch (err) { toast(err.message, "erreur"); await charger(); }
  }

  /** Glisser-déposer d'un jour à l'autre (vue mois, journée entière).
   *  Ctrl enfoncé au moment de lâcher : copie. */
  function deplacable(e) {
    return { draggable: "true", ondragstart: ev => { ev.dataTransfer.setData("text/plain", e.id); ev.dataTransfer.effectAllowed = "copyMove"; ev.stopPropagation(); } };
  }
  function zoneDepot(jour) {
    return {
      ondragover: ev => { ev.preventDefault(); ev.dataTransfer.dropEffect = ev.ctrlKey ? "copy" : "move"; ev.currentTarget.classList.add("survol"); },
      ondragleave: ev => ev.currentTarget.classList.remove("survol"),
      ondrop: ev => {
        ev.preventDefault(); ev.currentTarget.classList.remove("survol");
        const e = A.evenements.find(x => x.id === ev.dataTransfer.getData("text/plain"));
        if (!e) return;
        const d = new Date(jour); const deb = debutDe(e);
        d.setHours(deb.getHours(), deb.getMinutes(), 0, 0);
        deplacerVers(e, d, ev.ctrlKey);
      },
    };
  }

  /** Vue semaine : attraper un rendez-vous et le glisser vers une autre heure
   *  (pas de 15 min) ou un autre jour. Un simple clic l'ouvre. */
  function glisserRdv(ev, e, bloc, jours) {
    if (ev.button !== 0) return;
    ev.preventDefault(); ev.stopPropagation();
    const x0 = ev.clientX, y0 = ev.clientY, deb0 = debutDe(e), duree = finDe(e) - deb0;
    const colonnes = [...$("#vue-agenda").querySelectorAll(".colonne")];
    const depart = bloc.parentNode, top0 = parseFloat(bloc.style.top);
    let bouge = false, cible = depart, minutes = 0;
    const etiquette = bloc.querySelector("span");
    const nouveauDebut = () => {
      const d = new Date(jours[colonnes.indexOf(cible)]);
      d.setHours(deb0.getHours(), deb0.getMinutes() + minutes, 0, 0);
      return d;
    };
    const suivre = mv => {
      if (!bouge && Math.abs(mv.clientX - x0) + Math.abs(mv.clientY - y0) < 5) return;
      bouge = true;
      bloc.classList.add("glisse");
      bloc.classList.toggle("copie", mv.ctrlKey);
      minutes = Math.round((mv.clientY - y0) / PX * 4) * 15;
      // Rester dans la journée affichée.
      const min = (H0 - deb0.getHours()) * 60 - deb0.getMinutes();
      const max = (H1 - deb0.getHours()) * 60 - deb0.getMinutes() - Math.round(duree / 60e3);
      minutes = Math.max(min, Math.min(max, minutes));
      const col = colonnes.find(c => { const r = c.getBoundingClientRect(); return mv.clientX >= r.left && mv.clientX < r.right; });
      if (col && col !== cible) { cible = col; col.append(bloc); }
      bloc.style.top = `${top0 + minutes / 60 * PX}px`;
      bloc.style.left = "3px"; bloc.style.width = "calc(100% - 6px)";
      const d = nouveauDebut();
      etiquette.textContent = `${isoMinute(d).slice(11, 16)} – ${isoMinute(new Date(d.getTime() + duree)).slice(11, 16)}${mv.ctrlKey ? "· " + t("copie") : ""}`;
    };
    const lacher = up => {
      document.removeEventListener("mousemove", suivre);
      document.removeEventListener("mouseup", lacher);
      if (!bouge) { editer(e); return; }
      deplacerVers(e, nouveauDebut(), up.ctrlKey);
    };
    document.addEventListener("mousemove", suivre);
    document.addEventListener("mouseup", lacher);
  }

  function puce(e) {
    return el("div", { class: "puce-rdv", style: `background:${e.couleur || "#6c4cf5"}`, title: astuce(e),
      ...deplacable(e), onclick: ev => { ev.stopPropagation(); editer(e); } },
      e.recurrence ? icone("arrow-left-right") : null,
      brut((e.journee ? "" : e.debut.slice(11, 16) + " ") + (e.titre || t("Rendez-vous"))));
  }

  // -- vue semaine (ou journée unique avec nbJours = 1) -----------------------
  function vueSemaine(nbJours = 7) {
    const debut = nbJours === 1 ? new Date(A.ref) : lundi(A.ref);
    debut.setHours(0, 0, 0, 0);
    const jours = [...Array(nbJours)].map((_, i) => plusJours(debut, i));
    const noms = nomsJours();
    const auj = new Date();
    const cols = `54px repeat(${nbJours}, minmax(0, 1fr))`;
    const grille = el("div", { class: "semaine" },
      el("div", { class: "entete-semaine", style: `grid-template-columns: ${cols}; padding-right: 8px;` },
        el("div", { class: "tete-jour" }),
        jours.map((d, i) => el("div", { class: "tete-jour " + (memeJourA(d, auj) ? " auj" : "") },
          noms[nbJours === 1 ? (d.getDay() === 0 ? 6 : d.getDay() - 1) : i],
          el("b", {}, String(d.getDate()))))));
    // Rendez-vous de la journée entière
    grille.append(el("div", { class: "bande-jour", style: `grid-template-columns: ${cols}; padding-right: 8px;` },
      el("div", { class: "etiquette-h" }, "jour"),
      jours.map(d => el("div", { class: "case", ...zoneDepot(d) }, A.evenements.filter(e => e.journee && memeJourA(debutDe(e), d)).map(e =>
        el("div", { class: "rdv jour", style: `background:${e.couleur || "#6c4cf5"}`, ...deplacable(e), onclick: () => editer(e) }, el("b", {}, titreDe(e))))))));
    const corps = el("div", { class: "corps-semaine", style: `grid-template-columns: ${cols};` },
      el("div", { class: "heures" }, [...Array(H1 - H0)].map((_, i) => el("div", {}, i ? `${H0 + i}:00` : ""))));
    jours.forEach(d => {
      const col = el("div", { class: "colonne " + (memeJourA(d, auj) ? " auj" : ""), style: `height:${(H1 - H0) * PX}px`,
        onclick: ev => { if (ev.target !== col) return; editer(nouveau(d, H0 + Math.floor(ev.offsetY / PX))); } });
      const duJour = A.evenements.filter(e => !e.journee && memeJourA(debutDe(e), d)).sort((a, b) => a.debut.localeCompare(b.debut));
      placer(duJour).forEach(({ e, voie, voies }) => {
        const deb = debutDe(e), fin = finDe(e);
        const haut = Math.max(0, (deb.getHours() + deb.getMinutes() / 60 - H0) * PX);
        const hauteur = Math.max(22, (fin - deb) / 3600e3 * PX - 2);
        const bloc = el("div", { class: "rdv", style: `top:${haut}px;height:${hauteur}px;background:${e.couleur || "#6c4cf5"};left:calc(${voie * 100 / voies}% + 3px);width:calc(${100 / voies}% - 6px);right:auto`,
          title: astuce(e),
          onmousedown: ev => glisserRdv(ev, e, bloc, jours), onclick: ev => ev.stopPropagation() },
          el("b", {}, e.recurrence ? icone("arrow-left-right") : null, titreDe(e)),
          el("span", {}, brut(`${e.debut.slice(11, 16)} – ${isoMinute(fin).slice(11, 16)}${e.lieu ? "· " + e.lieu : ""}`)));
        col.append(bloc);
      });
      if (memeJourA(d, auj)) {
        const h = auj.getHours() + auj.getMinutes() / 60;
        if (h >= H0 && h <= H1) col.append(el("div", { class: "maintenant", style: `top:${(h - H0) * PX}px` }));
      }
      corps.append(col);
    });
    const defil = el("div", { class: "defilement" }, corps);
    grille.append(defil);
    setTimeout(() => { defil.scrollTop = Math.max(0, (Math.min(auj.getHours(), 18) - H0 - 1) * PX); }, 0);
    return el("div", { class: "agenda-carte" }, grille);
  }

  /** Rendez-vous qui se chevauchent : côte à côte, chacun sur sa « voie ». */
  function placer(liste) {
    const resultat = [];
    let groupe = [], finGroupe = 0;
    const clore = () => {
      const voies = [];
      groupe.forEach(item => {
        let v = voies.findIndex(f => f <= debutDe(item.e).getTime());
        if (v < 0) { v = voies.length; voies.push(0); }
        voies[v] = finDe(item.e).getTime();
        item.voie = v;
      });
      groupe.forEach(item => { item.voies = voies.length; resultat.push(item); });
      groupe = [];
    };
    liste.forEach(e => {
      if (groupe.length && debutDe(e).getTime() >= finGroupe) clore();
      groupe.push({ e });
      finGroupe = Math.max(finGroupe, finDe(e).getTime());
    });
    if (groupe.length) clore();
    return resultat;
  }

  // -- vue mois --------------------------------------------------------------
  function vueMois() {
    const premier = new Date(A.ref.getFullYear(), A.ref.getMonth(), 1);
    const debut = lundi(premier);
    const auj = new Date();
    const grille = el("div", { class: "mois" }, nomsJours().map(j => el("div", { class: "nom-jour" }, j)));
    for (let i = 0; i < 42; i++) {
      const d = plusJours(debut, i);
      const duJour = A.evenements.filter(e => memeJourA(debutDe(e), d)).sort((a, b) => (b.journee ? 1 : 0) - (a.journee ? 1 : 0) || a.debut.localeCompare(b.debut));
      grille.append(el("div", { class: "jour " + (d.getMonth() !== premier.getMonth() ? " autre" : "") + (memeJourA(d, auj) ? " auj" : ""),
        onclick: () => editer(nouveau(d)), ...zoneDepot(d) },
        el("span", { class: "num" }, String(d.getDate())),
        duJour.slice(0, 3).map(puce),
        duJour.length > 3 ? el("div", { class: "plus-rdv", onclick: ev => { ev.stopPropagation(); A.mode = "semaine"; A.ref = d; dessiner(); } }, t( " + {n} autres", { n: duJour.length - 3 })) : null));
    }
    return el("div", { class: "agenda-carte" }, grille);
  }

  function dessiner() {
    $("#vue-agenda").replaceChildren(barre(),
      el("div", { class: "astuce-agenda" }, icone("lightbulb"), " Glissez un rendez-vous pour le déplacer · Ctrl + glisser pour le dupliquer"),
      A.mode === "mois" ? vueMois() : vueSemaine(A.mode === "jour" ? 1 : 7));
  }

  // -- formulaire --------------------------------------------------------------
  function editer(source, estCopie = false) {
    // Un rendez-vous récurrent est édité comme sa série (l'original).
    if (source._virtuel && source._serie) {
      const original = A.bruts.find(x => x.id === source._serie);
      if (original) source = structuredClone(original);
    }
    const e = structuredClone(source);
    const champ = (libelle, controle) => el("label", { class: "champ" }, libelle, controle);
    const jour = el("input", { type: "date", value: e.debut.slice(0, 10) });
    const hDebut = el("input", { type: "time", value: e.debut.slice(11, 16) });
    const hFin = el("input", { type: "time", value: (e.fin || e.debut).slice(11, 16) });
    const journee = el("input", { type: "checkbox", checked: e.journee ? "" : null, style: "width:18px;height:18px;accent-color:var(--violet)" });
    const heures = el("div", { class: "grille-form" }, champ("Début", hDebut), champ("Fin", hFin));
    const majJournee = () => { heures.hidden = journee.checked; };
    journee.addEventListener("change", majJournee);
    hDebut.addEventListener("change", () => {
      // Garder la durée quand on déplace le début.
      const duree = finDe(e) - debutDe(e);
      const nd = new Date(`${jour.value}T${hDebut.value}`);
      if (!isNaN(nd)) hFin.value = isoMinute(new Date(nd.getTime() + Math.max(duree, 15 * 60e3))).slice(11, 16);
    });
    const couleurs = el("div", { class: "couleurs" }, COULEURS_RDV.map(c => el("button", { type: "button", style: `background:${c}`, class: (e.couleur || COULEURS_RDV[0]) === c ? "choisi" : "",
      onclick: ev => { e.couleur = c; [...couleurs.children].forEach(b => b.classList.toggle("choisi", b === ev.currentTarget)); } })));
    const titre = el("input", { value: e.titre || "", placeholder: "ex. Réunion client" });
    const lieu = el("input", { value: e.lieu || "", placeholder: "ex. Bureau, Teams…" });
    const rappel = el("select", {}, RAPPELS.map(([v, libelle]) => el("option", { value: v, selected: String(e.rappel_minutes ?? "") === v ? "" : null }, libelle)));
    const recurrences = [["", "Aucune"], ["daily", "Chaque jour"], ["weekly", "Chaque semaine"], ["monthly", "Chaque mois"], ["yearly", "Chaque année"]];
    const recurrence = el("select", {}, recurrences.map(([v, libelle]) => el("option", { value: v, selected: (e.recurrence || "") === v ? "" : null }, libelle)));
    const notes = el("textarea", { rows: 3, value: e.notes || "", placeholder: "Détails, ordre du jour…" });

    fenetre([
      el("h3", {}, e.id ? [icone("pencil"), " Rendez-vous"] : estCopie ? [icone("copy"), " Copie du rendez-vous"] : [icone("sparkles"), " Nouveau rendez-vous"]),
      champ("Titre", titre),
      el("div", { class: "grille-form" }, champ("Jour", jour),
        el("label", { class: "champ", style: "flex-direction:row;align-items:center;gap:8px;margin-top:22px" }, journee, "Toute la journée")),
      heures,
      el("div", { class: "grille-form" }, champ("Lieu", lieu), champ("Rappel (par la bulle)", rappel)),
      el("div", { class: "grille-form" }, champ("Répétition", recurrence)),
      champ("Couleur", couleurs),
      champ("Notes", notes),
      el("div", { class: "actions" },
        e.id ? el("button", { class: "btn discret", style: "margin-right:auto;color:var(--rouge)", onclick: async () => {
          if (!(await confirmer(icone("trash-2"), "Supprimer ce rendez-vous ?", e.titre ? "« " + e.titre + " »" : "", "Supprimer"))) { editer(e); return; }
          await api("/api/agenda/supprimer", { id: e.id });
          await charger(); toast("Rendez-vous supprimé");
        } }, icone("trash-2"), " Supprimer") : null,
        e.id ? el("button", { class: "btn discret", title: "Créer une copie (choisissez ensuite le jour)", onclick: () => {
          // La copie reprend tout, sauf l'identifiant : elle s'ouvre comme un
          // nouveau rendez-vous, pour choisir le jour avant d'ajouter.
          const copie = structuredClone(source);
          delete copie.id; delete copie.cree; copie.rappel_fait = false;
          fermer(); editer(copie, true);
          toast("Copie prête : changez le jour si besoin, puis « Ajouter »");
        } }, icone("copy"), " Dupliquer") : null,
        el("button", { class: "btn", onclick: fermer }, "Annuler"),
        el("button", { class: "btn principal", onclick: async () => {
          if (!titre.value.trim()) { toast("Indiquez un titre", "erreur"); return; }
          e.titre = titre.value.trim(); e.lieu = lieu.value.trim(); e.notes = notes.value;
          e.recurrence = recurrence.value;
          e.journee = journee.checked;
          e.debut = `${jour.value}T${e.journee ? "08:00" : hDebut.value}`;
          e.fin = `${jour.value}T${e.journee ? "09:00" : hFin.value}`;
          if (!e.journee && e.fin <= e.debut) { toast("La fin doit être après le début", "erreur"); return; }
          e.rappel_minutes = rappel.value === "" ? null : Number(rappel.value);
          try {
            await api("/api/agenda/enregistrer", { element: e });
            fermer(); A.ref = new Date(e.debut); await charger();
            toast(source.id ? "Rendez-vous modifié" : "Rendez-vous ajouté", "succes");
          } catch (err) { toast(err.message, "erreur"); }
        } }, e.id ? "Enregistrer" : "Ajouter"))]);
    majJournee();
    setTimeout(() => titre.focus(), 60);
  }

  // La ligne « maintenant » avance toute seule.
  setInterval(() => { if (S.vue === "agenda" && A.mode === "semaine" && !$("#voile").classList.contains("visible")) dessiner(); }, 300000);

  VUES.agenda = { afficher: () => charger().catch(err => toast(err.message, "erreur")),
    titre: "Agenda", icone: icone("calendar"), groupe: "quotidien", ordre: 30 };
})();
