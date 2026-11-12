"use strict";
/* Onglet « Minuteur » : chronomètre et compte à rebours (tout dans la page). */
(() => {
  I18N.ajouter({
    "Minuteur": "Timer",
    "Chronomètre": "Stopwatch",
    "Compte à rebours": "Countdown",
    "Démarrer": "Start",
    "Pause": "Pause",
    "Reprendre": "Resume",
    "Arrêter": "Stop",
    "Réinitialiser": "Reset",
    "Tour": "Lap",
    "Aucun tour": "No laps",
    "Minutes": "Minutes",
    "Secondes": "Seconds",
    "Heures": "Hours",
    "Temps écoulé": "Elapsed time",
    "Temps restant": "Time remaining",
    "Terminé !": "Done!",
    "Le compte à rebours est terminé.": "The countdown is over.",
  });

  const T = { mode: "chrono", debut: null, ecoule: 0, enCours: false, intervalle: null, tours: [], cible: 0, restant: 0 };

  const style = document.createElement("style");
  style.textContent = `
    .minuteur { display: flex; flex-direction: column; gap: 16px; align-items: center; }
    .minuteur-affichage { font-size: 64px; font-weight: 300; letter-spacing: -.02em; font-variant-numeric: tabular-nums; color: var(--encre); margin: 8px 0; }
    .minuteur-affichage .ms { font-size: 24px; color: var(--doux); }
    .minuteur-modes { display: flex; gap: 4px; }
    .minuteur-modes button { border: 0; height: 32px; padding: 0 14px; border-radius: 8px; background: var(--surface); color: var(--doux); cursor: pointer; font-weight: 500; font-size: 13.5px; transition: background .12s, color .12s; }
    .minuteur-modes button:hover { color: var(--encre); }
    .minuteur-modes button.actif { background: var(--violet-clair); color: var(--violet); }
    .minuteur-saisie { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; justify-content: center; }
    .minuteur-saisie input { width: 70px; text-align: center; font-size: 18px; font-variant-numeric: tabular-nums; }
    .minuteur-saisie label { font-size: 12px; color: var(--doux); }
    .minuteur-controles { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; }
    .minuteur-controles button { min-width: 90px; }
    .minuteur-tours { width: 100%; max-width: 400px; background: var(--carte); border: 1px solid var(--ligne); border-radius: var(--rayon); box-shadow: var(--ombre); overflow: hidden; max-height: 200px; overflow-y: auto; }
    .minuteur-tour { display: flex; justify-content: space-between; padding: 8px 14px; border-top: 1px solid var(--ligne); font-size: 13px; font-variant-numeric: tabular-nums; }
    .minuteur-tour:first-child { border-top: 0; }
    .minuteur-tour .num { color: var(--gris); font-weight: 600; }
    .minuteur-tour .delta { color: var(--doux); }
    .minuteur-vide { padding: 20px; text-align: center; color: var(--doux); font-size: 13px; }
  `;
  document.head.append(style);

  function formater(ms) {
    const total = Math.max(0, Math.floor(ms / 1000));
    const h = Math.floor(total / 3600), m = Math.floor((total % 3600) / 60), s = total % 60;
    const msRestant = Math.floor((ms % 1000) / 10);
    if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
    return `${m}:${String(s).padStart(2, "0")}`;
  }

  function dessiner() {
    const affichage = T.mode === "chrono" ? T.ecoule : T.restant;
    const ms = T.mode === "chrono" ? T.ecoule : T.restant;
    $("#vue-minuteur").replaceChildren(
      el("div", { class: "barre-vue" }, el("h2", {}, icone("timer"), " " + t("Minuteur")), el("span", { class: "espace" })),
      el("div", { class: "minuteur" },
        el("div", { class: "minuteur-modes" },
          el("button", { class: "btn" + (T.mode === "chrono" ? " actif" : ""), onclick: () => { T.mode = "chrono"; dessiner(); } }, t("Chronomètre")),
          el("button", { class: "btn" + (T.mode === "compte" ? " actif" : ""), onclick: () => { T.mode = "compte"; dessiner(); } }, t("Compte à rebours"))),
        T.mode === "chrono"
          ? el("div", { class: "minuteur-affichage" }, formater(T.ecoule))
          : el("div", { class: "minuteur-affichage" }, formater(T.restant)),
        T.mode === "compte" && !T.enCours && T.restant === 0
          ? el("div", { class: "minuteur-saisie" },
              el("label", {}, t("Heures"), el("input", { type: "number", min: 0, max: 23, value: 0, oninput: e => { T.heures = Number(e.target.value) || 0; } })),
              el("label", {}, t("Minutes"), el("input", { type: "number", min: 0, max: 59, value: 5, oninput: e => { T.minutes = Number(e.target.value) || 0; } })),
              el("label", {}, t("Secondes"), el("input", { type: "number", min: 0, max: 59, value: 0, oninput: e => { T.secondes = Number(e.target.value) || 0; } })))
          : null,
        el("div", { class: "minuteur-controles" },
          !T.enCours
            ? el("button", { class: "btn principal", onclick: demarrer }, icone("play"), " " + t("Démarrer"))
            : el("button", { class: "btn", onclick: pause }, icone("pause"), " " + t("Pause")),
          T.mode === "chrono" ? el("button", { class: "btn", onclick: tour }, icone("flag"), " " + t("Tour")) : null,
          el("button", { class: "btn discret", onclick: reinitialiser }, icone("rotate-ccw"), " " + t("Réinitialiser"))),
        T.mode === "chrono" && T.tours.length
          ? el("div", { class: "minuteur-tours" }, T.tours.map((t, i) =>
              el("div", { class: "minuteur-tour" }, el("span", { class: "num" }, "#" + (i + 1)), el("span", {}, formater(t.temps)), el("span", { class: "delta" }, "+" + formater(t.delta)))))
          : (T.mode === "chrono" ? el("div", { class: "minuteur-vide" }, t("Aucun tour")) : null)));
  }

  function demarrer() {
    if (T.mode === "compte" && T.restant === 0) {
      T.heures = T.heures || 0; T.minutes = T.minutes || 0; T.secondes = T.secondes || 0;
      T.restant = (T.heures * 3600 + T.minutes * 60 + T.secondes) * 1000;
      if (T.restant <= 0) { toast(t("Indiquez une durée"), "erreur"); return; }
    }
    T.debut = Date.now() - (T.mode === "chrono" ? T.ecoule : (T.cible - T.restant));
    T.enCours = true;
    if (T.intervalle) clearInterval(T.intervalle);
    T.intervalle = setInterval(() => {
      const now = Date.now();
      if (T.mode === "chrono") {
        T.ecoule = now - T.debut;
      } else {
        T.restant = Math.max(0, T.cible - (now - T.debut));
        if (T.restant === 0) { terminer(); }
      }
      dessiner();
    }, 100);
    dessiner();
  }

  function pause() {
    if (T.intervalle) { clearInterval(T.intervalle); T.intervalle = null; }
    T.enCours = false;
    if (T.mode === "chrono") T.ecoule = Date.now() - T.debut;
    else T.cible = Date.now() - T.debut + T.restant;
    dessiner();
  }

  function reinitialiser() {
    if (T.intervalle) { clearInterval(T.intervalle); T.intervalle = null; }
    T.enCours = false;
    T.ecoule = 0;
    T.restant = 0;
    T.cible = 0;
    T.tours = [];
    T.heures = 0; T.minutes = 5; T.secondes = 0;
    dessiner();
  }

  function tour() {
    if (!T.enCours || T.mode !== "chrono") return;
    const temps = Date.now() - T.debut;
    const dernier = T.tours.length ? T.tours[T.tours.length - 1].temps : 0;
    T.tours.push({ temps, delta: temps - dernier });
    dessiner();
  }

  function terminer() {
    if (T.intervalle) { clearInterval(T.intervalle); T.intervalle = null; }
    T.enCours = false;
    T.restant = 0;
    dessiner();
    toast(t("Terminé !"), "succes", 3000);
    // Notification sonore (bip).
    try { const ctx = new (window.AudioContext || window.webkitAudioContext)(); const o = ctx.createOscillator(); o.frequency.value = 880; o.connect(ctx.destination); o.start(); setTimeout(() => { o.stop(); ctx.close(); }, 200); } catch {}
  }

  // Initialisation.
  T.heures = 0; T.minutes = 5; T.secondes = 0;
  T.restant = 5 * 60 * 1000;
  T.cible = 5 * 60 * 1000;

  VUES.minuteur = { afficher: () => dessiner(), titre: "Minuteur", icone: "timer", groupe: "outils", ordre: 40,
    description: "Chronomètre et compte à rebours, avec tours et alarme.",
    profils: ["freelance", "assistant_virtuel", "assistant_direction", "developpeur", "comptable", "redacteur", "designer", "consultant", "commercial"] };
})();
EOF