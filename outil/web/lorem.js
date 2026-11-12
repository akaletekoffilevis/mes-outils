"use strict";
/* Onglet « Lorem » : générateur de texte de remplissage (Lorem ipsum). */
(() => {
  I18N.ajouter({
    "Lorem": "Lorem",
    "Générateur de texte de remplissage": "Lorem ipsum generator",
    "Paragraphes": "Paragraphs",
    "Mots par paragraphe": "Words per paragraph",
    "Générer": "Generate",
    "Copier": "Copy",
    "Avec ponctuation": "With punctuation",
  });

  const L = { paragraphes: 3, mots: 40, ponctuation: true, texte: "" };

  const MOTS = "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur excepteur sint occaecat cupidatat non proident sunt in culpa qui officia deserunt mollit anim id est laborum".split(" ");

  const style = document.createElement("style");
  style.textContent = `
    .lorem { display: flex; flex-direction: column; gap: 16px; max-width: 680px; }
    .lorem-carte { background: var(--carte); border: 1px solid var(--ligne); border-radius: var(--rayon); box-shadow: var(--ombre); padding: 20px; }
    .lorem-texte { white-space: pre-wrap; font-size: 14px; line-height: 1.6; max-height: 400px; overflow: auto; padding: 12px; border-radius: 8px; background: var(--surface); }
    .lorem-ligne { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
    .lorem-ligne label { font-size: 12.5px; font-weight: 500; color: var(--doux); min-width: 120px; }
    .lorem-ligne input[type=number] { width: 80px; }
  `;
  document.head.append(style);

  function mot() { return MOTS[Math.floor(Math.random() * MOTS.length)]; }

  function phrase(nb) {
    const n = Math.max(3, nb);
    const mots = [];
    for (let i = 0; i < n; i++) mots.push(mot());
    mots[0] = mots[0].charAt(0).toUpperCase() + mots[0].slice(1);
    if (L.ponctuation) {
      // Insérer une virgule au milieu.
      if (n > 6) mots[Math.floor(n / 2)] += ",";
      mots[mots.length - 1] += ".";
    }
    return mots.join(" ");
  }

  function generer() {
    const paras = [];
    for (let p = 0; p < L.paragraphes; p++) {
      const nbPhrases = 2 + Math.floor(Math.random() * 3);
      const phrases = [];
      for (let s = 0; s < nbPhrases; s++) phrases.push(phrase(L.mots));
      paras.push(phrases.join(" "));
    }
    L.texte = paras.join("\n\n");
  }

  function dessiner() {
    if (!L.texte) generer();
    $("#vue-lorem").replaceChildren(
      el("div", { class: "barre-vue" }, el("h2", {}, icone("type"), " " + t("Lorem")), el("span", { class: "espace" })),
      el("div", { class: "lorem" },
        el("div", { class: "lorem-carte" },
          el("div", { class: "lorem-ligne" }, el("label", {}, t("Paragraphes")), el("input", { type: "number", min: 1, max: 20, value: L.paragraphes, oninput: e => { L.paragraphes = Math.max(1, Number(e.target.value) || 1); generer(); dessiner(); } })),
          el("div", { class: "lorem-ligne" }, el("label", {}, t("Mots par paragraphe")), el("input", { type: "number", min: 5, max: 100, value: L.mots, oninput: e => { L.mots = Math.max(5, Number(e.target.value) || 5); generer(); dessiner(); } })),
          el("div", { class: "lorem-ligne" }, el("label", {}, ""), el("label", { class: "mdp-option" }, el("input", { type: "checkbox", checked: L.ponctuation ? "" : null, onchange: e => { L.ponctuation = e.target.checked; generer(); dessiner(); } }), t("Avec ponctuation"))),
          el("div", { style: "display:flex;gap:8px" },
            el("button", { class: "btn", onclick: () => { generer(); dessiner(); } }, icone("refresh-cw"), " " + t("Générer")),
            el("button", { class: "btn discret", onclick: () => copier(L.texte) }, icone("copy"), " " + t("Copier")))),
        el("div", { class: "lorem-carte" }, el("div", { class: "lorem-texte" }, L.texte))));
  }

  VUES.lorem = { afficher: () => dessiner(), titre: "Lorem", icone: "type", groupe: "outils", ordre: 65,
    description: "Générateur de texte de remplissage (Lorem ipsum) pour maquettes.",
    profils: ["freelance", "assistant_virtuel", "assistant_direction", "developpeur", "comptable", "redacteur", "designer", "consultant", "commercial", "pharmacien", "avocat", "architecte", "enseignant", "medecin"] };
})();
EOF