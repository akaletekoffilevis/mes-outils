"use strict";
/* Onglet « Temps » : chronomètre de travail par projet, Pomodoro, sessions
   (jour / semaine / mois), totaux par projet, export CSV (voir temps.py).
   L'état du chrono est gardé côté PC : il survit à la fermeture de la page. */
(() => {
  I18N.ajouter({
    "Temps": "Time",
    "Temps de travail": "Work time",
    "Projet": "Project",
    "Note": "Note",
    "Note (facultatif)": "Note (optional)",
    "ex. Site vitrine": "e.g. Company website",
    "ex. maquette de l'accueil": "e.g. home page mock-up",
    "▶ Démarrer": "▶ Start",
    "■ Arrêter": "■ Stop",
    "Pomodoro": "Pomodoro",
    " Pomodoro": " Pomodoro",
    "Aucun chrono en cours": "No timer running",
    "Sur quoi travaillez-vous ?": "What are you working on?",
    "Récents :": "Recent:",
    "depuis {heure}": "since {heure}",
    "Travail": "Work",
    "Pause courte": "Short break",
    "Pause longue": "Long break",
    "n° {n}": "#{n}",
    "Fin à {heure}": "Ends at {heure}",
    "Jour": "Day", "Semaine": "Week", "Mois": "Month",
    "Aujourd'hui": "Today",
    "Précédent": "Previous", "Suivant": "Next",
    "＋ Session oubliée": "＋ Missed session",
    "⬇ Export CSV": "⬇ CSV export",
    "Date": "Date", "Horaires": "Times", "Durée": "Duration",
    "Total": "Total",
    "Par projet": "By project",
    "Pour Excel (séparateur « ; »)": "For Excel (“;” separator)",
    "Aucune session sur cette période.": "No session in this period.",
    "Modifier": "Edit", "Supprimer": "Delete", "Annuler": "Cancel", "Enregistrer": "Save", "Ajouter": "Add",
    "Début": "Start", "Fin": "End",
    " Modifier la session": " Edit session",
    "＋ Session oubliée ": "＋ Missed session",
    "Supprimer cette session ?": "Delete this session?",
    "Elle disparaît des totaux et des exports.": "It disappears from totals and exports.",
    " Session supprimée": " Session deleted",
    " Session enregistrée": " Session saved",
    " C'est parti !": " Off you go!",
    "Moins d'une minute : session non enregistrée.": "Less than a minute: session not saved.",
    " {duree} sur « {projet} »": " {duree} on “{projet}”",
    "Réglages du Pomodoro": "Pomodoro settings",
    "Travail (min)": "Work (min)",
    "Pause courte (min)": "Short break (min)",
    "Pause longue (min)": "Long break (min)",
    "Pause longue toutes les … périodes": "Long break every … periods",
    "Cocher « Pomodoro » par défaut": "Tick “Pomodoro” by default",
    "La bulle vous prévient à la fin de chaque période. Les pauses restent comptées dans le chrono : arrêtez-le pendant la pause si elle ne doit pas être facturée.":
      "The bubble lets you know when each period ends. Breaks are still counted by the timer: stop it during the break if it shouldn't be billed.",
    " Enregistré": " Saved",
    "Pomodoro {t}/{c}": "Pomodoro {t}/{c}",
    "Semaine du {debut} au {fin}": "Week of {debut} to {fin}",
    "Toutes les sessions": "All sessions",
    "Indiquez un projet.": "Enter a project.",
    "Aucun chrono en cours.": "No timer running.",
    "La fin doit être après le début.": "The end must be after the start.",
    "Une session ne peut pas dépasser 24 heures.": "A session cannot exceed 24 hours.",
    "Session introuvable.": "Session not found.",
    "Début invalide.": "Invalid start.",
    "Fin invalide.": "Invalid end.",
    "Date invalide.": "Invalid date.",
    "Période inconnue.": "Unknown period.",
    "Durée invalide.": "Invalid duration.",
  });
  I18N.motifs([
    [/^Un chrono tourne déjà sur « (.*) » : arrêtez-le d'abord\.$/, "A timer is already running on “$1”: stop it first."],
    [/^Valeur hors limites \((\d+) à (\d+)\)\.$/, "Value out of range ($1 to $2)."],
  ]);

  const T = { r: null, periode: "semaine", date: isoJour(new Date()), externes: [], rafraichi: 0, demande: false };
  const PHASES = { travail: "Travail", pause_courte: "Pause courte", pause_longue: "Pause longue" };

  const style = document.createElement("style");
  style.textContent = `
    .tp-haut { display: grid; grid-template-columns: 1fr auto; gap: 18px; align-items: center; padding: 20px 24px; margin-bottom: 22px; }
    .tp-projet { font-size: 20px; font-weight: 600; margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .tp-note { color: var(--doux); font-size: 14px; margin-top: 2px; min-height: 18px; }
    .tp-chrono { font-size: 56px; font-weight: 600; letter-spacing: -1.5px; font-variant-numeric: tabular-nums; line-height: 1.1; margin: 8px 0 4px; }
    .tp-chrono.arrete { color: var(--gris); }
    .tp-depuis { color: var(--doux); font-size: 13px; font-weight: 600; }
    .tp-boutons { display: flex; gap: 8px; margin-top: 14px; flex-wrap: wrap; align-items: center; }
    .tp-boutons .btn.arreter { background: var(--rouge); color: var(--sur-violet); }
    .tp-form { display: grid; grid-template-columns: 1.2fr 1fr; gap: 12px; margin-top: 8px; }
    .tp-form label.champ { margin-bottom: 0; }
    .tp-recents { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 10px; align-items: center; }
    .tp-recents .etiquette { cursor: pointer; border: 0; }
    .tp-recents .etiquette:hover { background: var(--violet-clair); color: var(--violet); }
    .tp-case { display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 14px; cursor: pointer; }
    .tp-case input { width: 17px; height: 17px; }
    .tp-anneau { position: relative; width: 168px; height: 168px; }
    .tp-anneau svg { width: 100%; height: 100%; transform: rotate(-90deg); }
    .tp-anneau .fond { fill: none; stroke: var(--surface); stroke-width: 12; }
    .tp-anneau .jauge { fill: none; stroke-width: 12; stroke-linecap: round; transition: stroke-dashoffset .9s linear, stroke .3s; }
    .tp-anneau .centre { position: absolute; inset: 0; display: grid; place-content: center; text-align: center; }
    .tp-anneau .reste { font-size: 30px; font-weight: 600; font-variant-numeric: tabular-nums; }
    .tp-anneau .phase { font-size: 12px; font-weight: 700; color: var(--doux); text-transform: uppercase; letter-spacing: .6px; }
    .tp-anneau.repos .reste { color: var(--gris); }
    .tp-nav { display: flex; align-items: center; gap: 6px; }
    .tp-nav .lib { font-weight: 700; min-width: 170px; text-align: center; }
    .tp-corps { display: grid; grid-template-columns: minmax(0, 1fr) 290px; gap: 18px; align-items: start; }
    @media (max-width: 1000px) { .tp-corps { grid-template-columns: 1fr; } .tp-haut { grid-template-columns: 1fr; } }
    .tp-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .tp-table th { text-align: left; font-size: 11.5px; text-transform: uppercase; letter-spacing: .7px; color: var(--gris); padding: 0 8px 8px; font-weight: 600; }
    .tp-table td { padding: 8px; border-top: 1px solid var(--ligne); vertical-align: middle; }
    .tp-table td.duree { font-weight: 600; font-variant-numeric: tabular-nums; white-space: nowrap; text-align: right; }
    .tp-table td.heures { font-variant-numeric: tabular-nums; color: var(--doux); white-space: nowrap; }
    .tp-table td.tp-cel-note { color: var(--doux); max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .tp-table td.actions { white-space: nowrap; text-align: right; width: 1%; }
    .tp-table td.actions .icone-btn { width: 28px; height: 28px; font-size: 12.5px; display: inline-grid; }
    .tp-table tr.total td { font-weight: 600; border-top: 2px solid var(--ligne); }
    .tp-pastille { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 7px; vertical-align: 1px; }
    .tp-totaux h3 { margin: 0 0 12px; font-size: 13px; text-transform: uppercase; letter-spacing: .8px; color: var(--doux); }
    .tp-barre { margin-bottom: 12px; }
    .tp-barre .lignes { display: flex; justify-content: space-between; gap: 8px; font-size: 13.5px; font-weight: 700; margin-bottom: 4px; }
    .tp-barre .lignes span:first-child { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .tp-barre .lignes span:last-child { font-variant-numeric: tabular-nums; color: var(--doux); flex: none; }
    .tp-barre .piste { height: 9px; border-radius: 99px; background: var(--surface); overflow: hidden; }
    .tp-barre .piste div { height: 100%; border-radius: 99px; animation: tp-pousse .6s var(--ressort) both; transform-origin: left; }
    @keyframes tp-pousse { from { transform: scaleX(0); } }
    .tp-grille-reg { display: grid; grid-template-columns: 1fr 1fr; gap: 0 12px; }
  `;
  document.head.append(style);

  // --------------------------------------------------------------- outils
  function deux(n) { return String(n).padStart(2, "0"); }
  function isoJour(d) { return `${d.getFullYear()}-${deux(d.getMonth() + 1)}-${deux(d.getDate())}`; }
  function isoMinute(d) { return `${isoJour(d)}T${deux(d.getHours())}:${deux(d.getMinutes())}`; }
  function date(iso) { return new Date(iso.length === 10 ? iso + "T00:00" : iso); }
  function hhmm(iso) { return iso.slice(11, 16); }
  function duree(minutes) {
    if (minutes < 60) return `${minutes} min`;
    return `${Math.floor(minutes / 60)} h ${deux(minutes % 60)}`;
  }
  function horloge(secondes) {
    const s = Math.max(0, Math.floor(secondes));
    return `${deux(Math.floor(s / 3600))}:${deux(Math.floor(s / 60) % 60)}:${deux(s % 60)}`;
  }
  const COULEURS = ["var(--violet)", "var(--menthe)", "var(--corail)", "var(--ambre)", "var(--bleu-texte)", "var(--rouge)"];
  /** Une couleur par projet : l'ordre des totaux, puis des projets récents. */
  function couleur(projet) {
    const ordre = [...new Set([...(T.r?.totaux || []).map(x => x.projet), ...suggestions()])];
    let i = ordre.indexOf(projet);
    if (i < 0) { i = 0; for (const c of projet) i = (i * 31 + c.charCodeAt(0)) >>> 0; }
    return COULEURS[i % COULEURS.length];
  }
  const racine = () => $("#vue-temps");
  const visible = () => racine()?.classList.contains("actif") && document.visibilityState === "visible";

  // -------------------------------------------------------------- données
  async function charger() {
    T.r = await api("/api/temps/liste", { periode: T.periode, date: T.date });
    T.rafraichi = Date.now();
    T.demande = false;
    dessiner();
  }
  const recharger = () => charger().catch(e => toast(e.message, "erreur"));

  /** Noms de projets venant de l'onglet Projets, s'il existe (sinon rien). */
  async function projetsExternes() {
    try {
      const r = await api("/api/projets/liste", {});
      const liste = Array.isArray(r) ? r : (r.projets || r.elements || []);
      T.externes = liste.map(p => typeof p === "string" ? p : (p && (p.nom || p.name || p.titre))).filter(Boolean).slice(0, 60);
    } catch { T.externes = []; }
  }

  function suggestions() {
    return [...new Set([...(T.r?.projets || []), ...T.externes])];
  }

  // Le chrono défile côté page, à partir de l'heure de début.
  setInterval(() => {
    if (!visible() || !T.r) return;
    const e = T.r.etat;
    if (e.en_cours) {
      const c = $(".tp-chrono", racine());
      if (c) c.textContent = horloge((Date.now() - date(e.depuis)) / 1000);
      majAnneau();
      // Fin d'une période Pomodoro : le serveur passe à la suivante.
      if (e.pomodoro && Date.now() >= date(e.pomodoro.fin_prevue).getTime() + 1000 && !T.demande) { T.demande = true; recharger(); }
    }
    if (Date.now() - T.rafraichi > 20000) recharger();   // la bulle a pu arrêter le chrono
  }, 1000);

  // -------------------------------------------------------------- dessin
  function dessiner() {
    racine().replaceChildren(
      el("div", { class: "barre-vue" },
        el("h2", {}, t("Temps de travail")),
        el("div", { class: "espace" }),
        el("button", { class: "btn discret", onclick: reglages, title: "Réglages du Pomodoro" }, t("Pomodoro") + `${T.r.reglages.travail}/${T.r.reglages.pause_courte}`)),
      blocChrono(),
      barrePeriode(),
      el("div", { class: "tp-corps" }, tableau(), totaux()));
    majAnneau();
  }

  function blocChrono() {
    const e = T.r.etat;
    if (!e.en_cours) {
      const projet = el("input", { placeholder: "ex. Site vitrine", list: "tp-projets", maxlength: 80,
        onkeydown: ev => { if (ev.key === "Enter") demarrer(); } });
      const note = el("input", { placeholder: "ex. maquette de l'accueil", maxlength: 300,
        onkeydown: ev => { if (ev.key === "Enter") demarrer(); } });
      const pomo = el("input", { type: "checkbox", checked: T.r.reglages.pomodoro_par_defaut ? "" : null });
      const demarrer = async () => {
        try {
          T.r.etat = await api("/api/temps/demarrer", { projet: projet.value, note: note.value, pomodoro: pomo.checked });
          toast("C'est parti !", "succes", 1500);
          recharger();
        } catch (err) { toast(err.message, "erreur"); projet.focus(); }
      };
      const recents = suggestions().slice(0, 8);
      return el("div", { class: "carte tp-haut" },
        el("div", {},
          el("div", { class: "tp-projet", style: "color:var(--doux)" }, "Sur quoi travaillez-vous ?"),
          el("div", { class: "tp-form" },
            el("label", { class: "champ" }, "Projet", projet,
              el("datalist", { id: "tp-projets" }, suggestions().map(p => el("option", { value: p })))),
            el("label", { class: "champ" }, "Note (facultatif)", note)),
          recents.length ? el("div", { class: "tp-recents" }, el("span", { class: "tp-depuis" }, "Récents :"),
            recents.map(p => el("button", { class: "etiquette", onclick: () => { projet.value = p; note.focus(); } }, p))) : null,
          el("div", { class: "tp-boutons" },
            el("button", { class: "btn principal", onclick: demarrer }, "▶ Démarrer"),
            el("label", { class: "tp-case" }, pomo, " Pomodoro"))),
        anneau());
    }
    const debut = date(e.depuis);
    return el("div", { class: "carte tp-haut" },
      el("div", { style: "min-width:0" },
        el("div", { class: "tp-projet" }, el("span", { class: "tp-pastille", style: `background:${couleur(e.projet)}` }), e.projet),
        el("div", { class: "tp-note" }, e.note || ""),
        el("div", { class: "tp-chrono" }, horloge((Date.now() - debut) / 1000)),
        el("div", { class: "tp-depuis" }, t("depuis {heure}", { heure: debut.toLocaleTimeString(I18N.locale(), { hour: "2-digit", minute: "2-digit" }) })),
        el("div", { class: "tp-boutons" },
          el("button", { class: "btn arreter", onclick: arreter }, "■ Arrêter"),
          el("button", { class: "btn " + (e.pomodoro ? " actif" : ""), onclick: () => modifierEnCours({ pomodoro: !e.pomodoro }) }, " Pomodoro"),
          el("button", { class: "btn discret", onclick: editerEnCours, title: "Modifier" }, icone("pencil")))),
      anneau());
  }

  function anneau() {
    const R = 70, C = 2 * Math.PI * R;
    return el("div", { class: "tp-anneau", id: "tp-anneau" },
      (() => {
        const ns = "http://www.w3.org/2000/svg";
        const svg = document.createElementNS(ns, "svg");
        svg.setAttribute("viewBox", "0 0 168 168");
        for (const [classe, extra] of [["fond", {}], ["jauge", { "stroke-dasharray": C, "stroke-dashoffset": C }]]) {
          const c = document.createElementNS(ns, "circle");
          c.setAttribute("cx", 84); c.setAttribute("cy", 84); c.setAttribute("r", R); c.setAttribute("class", classe);
          for (const [k, v] of Object.entries(extra)) c.setAttribute(k, v);
          svg.append(c);
        }
        return svg;
      })(),
      el("div", { class: "centre" }, el("div", { class: "reste" }, "--:--"), el("div", { class: "phase" }, "")));
  }

  function majAnneau() {
    const a = $("#tp-anneau");
    if (!a || !T.r) return;
    const e = T.r.etat, p = e.pomodoro;
    const jauge = a.querySelector(".jauge"), C = 2 * Math.PI * 70;
    a.classList.toggle("repos", !p);
    if (!p) {
      const r = T.r.reglages;
      jauge.setAttribute("stroke-dashoffset", C);
      a.querySelector(".reste").textContent = `${deux(r.travail)}:00`;
      a.querySelector(".phase").textContent = t("Pomodoro");
      return;
    }
    const debut = date(p.debut_phase).getTime(), fin = date(p.fin_prevue).getTime();
    const part = Math.min(1, Math.max(0, (Date.now() - debut) / (fin - debut)));
    jauge.setAttribute("stroke-dashoffset", C * (1 - part));
    jauge.style.stroke = p.phase === "travail" ? "var(--corail)" : "var(--menthe)";
    a.querySelector(".reste").textContent = horloge((fin - Date.now()) / 1000).slice(3);
    a.querySelector(".phase").textContent = t(PHASES[p.phase]) + "· " + t("n° {n}", { n: p.numero });
    a.title = t("Fin à {heure}", { heure: hhmm(p.fin_prevue) });
  }

  function barrePeriode() {
    const libelle = (() => {
      const r = T.r;
      if (T.periode === "tout") return t("Toutes les sessions");
      const d = date(r.debut), f = date(r.fin);
      const loc = I18N.locale();
      if (T.periode === "jour") return d.toLocaleDateString(loc, { weekday: "long", day: "numeric", month: "long", year: "numeric" });
      if (T.periode === "mois") return d.toLocaleDateString(loc, { month: "long", year: "numeric" });
      return t("Semaine du {debut} au {fin}", { debut: d.toLocaleDateString(loc, { day: "numeric", month: "short" }),
        fin: f.toLocaleDateString(loc, { day: "numeric", month: "short", year: "numeric" }) });
    })();
    return el("div", { class: "barre-vue" },
      el("div", { class: "puces" }, [["jour", "Jour"], ["semaine", "Semaine"], ["mois", "Mois"]].map(([v, lib]) =>
        el("button", { class: "puce " + (T.periode === v ? " actif" : ""), onclick: () => { T.periode = v; recharger(); } }, lib))),
      el("div", { class: "tp-nav" },
        el("button", { class: "icone-btn", title: "Précédent", onclick: () => decaler(-1) }, "‹"),
        el("span", { class: "lib" }, libelle.charAt(0).toUpperCase() + libelle.slice(1)),
        el("button", { class: "icone-btn", title: "Suivant", onclick: () => decaler(1) }, "›"),
        el("button", { class: "btn discret", onclick: () => { T.date = isoJour(new Date()); recharger(); } }, "Aujourd'hui")),
      el("div", { class: "espace" }),
      el("button", { class: "btn", onclick: () => editerSession(null) }, "＋ Session oubliée"));
  }

  function decaler(sens) {
    const d = date(T.date);
    if (T.periode === "jour") d.setDate(d.getDate() + sens);
    else if (T.periode === "semaine") d.setDate(d.getDate() + 7 * sens);
    else { d.setDate(1); d.setMonth(d.getMonth() + sens); }
    T.date = isoJour(d);
    recharger();
  }

  function tableau() {
    const s = T.r.sessions;
    if (!s.length) return el("div", { class: "vide" }, t("Aucune session sur cette période."));
    const loc = I18N.locale();
    return el("div", { class: "carte", style: "padding:14px 12px" },
      el("table", { class: "tp-table" },
        el("thead", {}, el("tr", {}, ["Date", "Horaires", "Projet", "Note", "Durée", ""].map(h =>
          el("th", { style: h === "Durée" ? "text-align:right" : "" }, h)))),
        el("tbody", {},
          s.map(x => el("tr", {},
            el("td", {}, date(x.debut).toLocaleDateString(loc, { weekday: "short", day: "2-digit", month: "2-digit" })),
            el("td", { class: "heures" }, `${hhmm(x.debut)} – ${hhmm(x.fin)}`),
            el("td", {}, el("span", { class: "tp-pastille", style: `background:${couleur(x.projet)}` }), x.projet),
            el("td", { class: "tp-cel-note", title: x.note || "" }, x.note || ""),
            el("td", { class: "duree" }, duree(x.minutes)),
            el("td", { class: "actions" },
              el("button", { class: "icone-btn", title: "Modifier", onclick: () => editerSession(x) }, icone("pencil")),
              el("button", { class: "icone-btn danger", title: "Supprimer", onclick: () => supprimerSession(x) }, icone("trash-2"))))),
          el("tr", { class: "total" }, el("td", { colspan: 4 }, "Total"), el("td", { class: "duree" }, duree(T.r.total)), el("td", {})))));
  }

  function totaux() {
    const liste = T.r.totaux;
    if (!liste.length) return el("div");
    const max = Math.max(...liste.map(x => x.minutes), 1);
    return el("div", { class: "carte tp-totaux" },
      el("div", { style: "display:flex;align-items:center;gap:8px;margin-bottom:12px" },
        el("h3", { style: "margin:0;flex:1" }, "Par projet"),
        el("button", { class: "btn", style: "padding:6px 12px;font-size:13px", title: "Pour Excel (séparateur « ; »)", onclick: exporter }, "⬇ Export CSV")),
      liste.map((x, i) => el("div", { class: "tp-barre" },
        el("div", { class: "lignes" }, el("span", { title: x.projet }, x.projet), el("span", {}, duree(x.minutes))),
        el("div", { class: "piste" }, el("div", { style: `width:${(x.minutes / max) * 100}%;background:${couleur(x.projet)};animation-delay:${i * 60}ms` })))));
  }

  // ------------------------------------------------------------- actions
  async function arreter() {
    try {
      const r = await api("/api/temps/arreter", {});
      if (r.session) toast(t(" {duree} sur « {projet} »", { duree: duree(r.session.minutes), projet: r.session.projet }), "succes");
      else toast("Moins d'une minute : session non enregistrée.");
      recharger();
    } catch (e) { toast(e.message, "erreur"); recharger(); }
  }

  async function modifierEnCours(valeurs) {
    try { T.r.etat = await api("/api/temps/en_cours", valeurs); dessiner(); }
    catch (e) { toast(e.message, "erreur"); recharger(); }
  }

  function editerEnCours() {
    const e = T.r.etat;
    const projet = el("input", { value: e.projet, list: "tp-projets-f", maxlength: 80 });
    const note = el("input", { value: e.note || "", maxlength: 300 });
    fenetre([
      el("h3", {}, t("Modifier")),
      el("label", { class: "champ" }, "Projet", projet, el("datalist", { id: "tp-projets-f" }, suggestions().map(p => el("option", { value: p })))),
      el("label", { class: "champ" }, "Note (facultatif)", note),
      el("div", { class: "actions" },
        el("button", { class: "btn", onclick: fermer }, "Annuler"),
        el("button", { class: "btn principal", onclick: async () => { fermer(); await modifierEnCours({ projet: projet.value, note: note.value }); } }, "Enregistrer"))]);
  }

  function editerSession(x) {
    const maintenant = new Date();
    const b = x ? { ...x } : { projet: "", note: "", debut: isoMinute(new Date(maintenant - 3600e3)), fin: isoMinute(maintenant) };
    const projet = el("input", { value: b.projet, list: "tp-projets-f", maxlength: 80, placeholder: "ex. Site vitrine" });
    const note = el("input", { value: b.note || "", maxlength: 300 });
    const debut = el("input", { type: "datetime-local", value: b.debut });
    const fin = el("input", { type: "datetime-local", value: b.fin });
    const valider = async () => {
      const session = { ...b, projet: projet.value, note: note.value, debut: debut.value, fin: fin.value };
      try {
        await api(x ? "/api/temps/modifier" : "/api/temps/ajouter", { session });
        fermer(); toast("Session enregistrée", "succes", 1600);
        // Une session ajoutée hors de la période affichée : on va la montrer.
        if (!x && debut.value) T.date = debut.value.slice(0, 10);
        recharger();
      } catch (e) { toast(e.message, "erreur"); }
    };
    fenetre([
      el("h3", {}, x ? " Modifier la session" : "＋ Session oubliée"),
      el("label", { class: "champ" }, "Projet", projet, el("datalist", { id: "tp-projets-f" }, suggestions().map(p => el("option", { value: p })))),
      el("label", { class: "champ" }, "Note (facultatif)", note),
      el("div", { style: "display:grid;grid-template-columns:1fr 1fr;gap:12px" },
        el("label", { class: "champ" }, "Début", debut), el("label", { class: "champ" }, "Fin", fin)),
      el("div", { class: "actions" },
        el("button", { class: "btn", onclick: fermer }, "Annuler"),
        el("button", { class: "btn principal", onclick: valider }, x ? "Enregistrer" : "Ajouter"))]);
    setTimeout(() => projet.focus(), 60);
  }

  async function supprimerSession(x) {
    if (!(await confirmer(icone("trash-2"), "Supprimer cette session ?", "Elle disparaît des totaux et des exports.", "Supprimer"))) return;
    try { await api("/api/temps/supprimer", { id: x.id }); toast("Session supprimée"); recharger(); }
    catch (e) { toast(e.message, "erreur"); }
  }

  async function exporter() {
    try {
      const r = await api("/api/temps/export", { periode: T.periode, date: T.date });
      const lien = el("a", { href: URL.createObjectURL(new Blob([r.csv], { type: "text/csv;charset=utf-8" })), download: r.nom });
      document.body.append(lien); lien.click(); lien.remove();
      setTimeout(() => URL.revokeObjectURL(lien.href), 5000);
    } catch (e) { toast(e.message, "erreur"); }
  }

  function reglages() {
    const r = T.r.reglages;
    const champ = (lib, cle, max) => {
      const i = el("input", { type: "number", min: 1, max, value: r[cle], "data-cle": cle });
      return el("label", { class: "champ" }, lib, i);
    };
    const parDefaut = el("input", { type: "checkbox", checked: r.pomodoro_par_defaut ? "" : null });
    const boite = el("div", { class: "tp-grille-reg" },
      champ("Travail (min)", "travail", 180), champ("Pause courte (min)", "pause_courte", 60),
      champ("Pause longue (min)", "pause_longue", 120), champ("Pause longue toutes les … périodes", "cycles", 12));
    fenetre([
      el("h3", {}, t("Réglages du Pomodoro")),
      el("p", {}, "La bulle vous prévient à la fin de chaque période. Les pauses restent comptées dans le chrono : arrêtez-le pendant la pause si elle ne doit pas être facturée."),
      boite,
      el("label", { class: "tp-case" }, parDefaut, "Cocher « Pomodoro » par défaut"),
      el("div", { class: "actions" },
        el("button", { class: "btn", onclick: fermer }, "Annuler"),
        el("button", { class: "btn principal", onclick: async () => {
          const valeurs = { pomodoro_par_defaut: parDefaut.checked };
          boite.querySelectorAll("input").forEach(i => { valeurs[i.dataset.cle] = Number(i.value); });
          try { await api("/api/temps/reglages", valeurs); fermer(); toast("Enregistré", "succes", 1400); recharger(); }
          catch (e) { toast(e.message, "erreur"); }
        } }, "Enregistrer"))]);
  }

  VUES.temps = {
    afficher: async () => { await projetsExternes(); recharger(); },
    titre: "Temps", icone: "", groupe: "outils", ordre: 40,
  };
})();
