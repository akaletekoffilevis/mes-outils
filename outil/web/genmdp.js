"use strict";
/* Onglet « Mot de passe » : générateur de mots de passe sécurisés (client-side). */
(() => {
  I18N.ajouter({
    "Mot de passe": "Password",
    "Générateur de mots de passe": "Password generator",
    "Longueur": "Length",
    "Majuscules": "Uppercase",
    "Minuscules": "Lowercase",
    "Chiffres": "Digits",
    "Symboles": "Symbols",
    "Générer": "Generate",
    "Copier": "Copy",
    "Mot de passe généré": "Generated password",
    "Force": "Strength",
    "Très faible": "Very weak",
    "Faible": "Weak",
    "Moyen": "Medium",
    "Fort": "Strong",
    "Très fort": "Very strong",
    "Exclure les caractères ambigus": "Exclude ambiguous characters",
  });

  const P = { longueur: 16, maj: true, min: true, chiffres: true, symboles: true, exclure: true, valeur: "" };

  const style = document.createElement("style");
  style.textContent = `
    .mdp { display: flex; flex-direction: column; gap: 16px; max-width: 560px; }
    .mdp-carte { background: var(--carte); border: 1px solid var(--ligne); border-radius: var(--rayon); box-shadow: var(--ombre); padding: 20px; }
    .mdp-resultat { font-family: "SF Mono", "Consolas", monospace; font-size: 22px; font-weight: 600; letter-spacing: .04em; text-align: center; padding: 16px; border-radius: 8px; background: var(--surface); word-break: break-all; min-height: 60px; display: flex; align-items: center; justify-content: center; }
    .mdp-force { height: 6px; border-radius: 3px; background: var(--surface); overflow: hidden; margin-top: 8px; }
    .mdp-force > div { height: 100%; transition: width .2s, background .2s; }
    .mdp-options { display: grid; grid-template-columns: 1fr 1fr; gap: 8px 16px; }
    .mdp-option { display: flex; align-items: center; gap: 8px; font-size: 13px; }
    .mdp-option input[type=checkbox] { width: 16px; height: 16px; accent-color: var(--violet); }
    .mdp-ligne { display: flex; align-items: center; gap: 12px; }
    .mdp-ligne label { font-size: 12.5px; font-weight: 500; color: var(--doux); min-width: 70px; }
    .mdp-ligne input[type=range] { flex: 1; accent-color: var(--violet); }
    .mdp-ligne span { font-variant-numeric: tabular-nums; min-width: 28px; text-align: right; font-weight: 600; }
  `;
  document.head.append(style);

  function generer() {
    const MAJ = "ABCDEFGHJKLMNPQRSTUVWXYZ";
    const MIN = "abcdefghijkmnpqrstuvwxyz";
    const CHI = "23456789";
    const SYM = "!@#$%&*+-=?";
    const AMB = "O0Il1";
    let pool = "";
    if (P.maj) pool += P.exclure ? MAJ : MAJ + "OIL";
    if (P.min) pool += P.exclure ? MIN : MIN + "oil";
    if (P.chiffres) pool += P.exclure ? CHI : CHI + "01";
    if (P.symboles) pool += SYM;
    if (!pool) { P.valeur = ""; return; }
    let v = "";
    const arr = new Uint32Array(P.longueur);
    crypto.getRandomValues(arr);
    for (let i = 0; i < P.longueur; i++) v += pool[arr[i] % pool.length];
    P.valeur = v;
  }

  function force(p) {
    if (!p) return 0;
    let score = 0;
    if (p.length >= 8) score += 1;
    if (p.length >= 12) score += 1;
    if (p.length >= 16) score += 1;
    if (/[A-Z]/.test(p)) score += 1;
    if (/[a-z]/.test(p)) score += 1;
    if (/[0-9]/.test(p)) score += 1;
    if (/[^A-Za-z0-9]/.test(p)) score += 1;
    return Math.min(4, Math.floor(score / 2));
  }

  const FORCES = ["Très faible", "Faible", "Moyen", "Fort", "Très fort"];
  const COULEURS = ["#ef4444", "#f97316", "#eab308", "#22c55e", "#16a34a"];

  function dessiner() {
    if (!P.valeur) generer();
    const f = force(P.valeur);
    $("#vue-genmdp").replaceChildren(
      el("div", { class: "barre-vue" }, el("h2", {}, icone("key"), " " + t("Mot de passe")), el("span", { class: "espace" })),
      el("div", { class: "mdp" },
        el("div", { class: "mdp-carte" },
          el("div", { class: "mdp-resultat" }, P.valeur || "—"),
          el("div", { class: "mdp-force" }, el("div", { style: `width:${(f + 1) * 20}%;background:${COULEURS[f]}` })),
          el("div", { style: "text-align:center;font-size:12.5px;color:var(--doux);margin-top:6px" }, t(FORCES[f]))),
        el("div", { class: "mdp-carte" },
          el("div", { class: "mdp-ligne" }, el("label", {}, t("Longueur")), el("input", { type: "range", min: 8, max: 64, value: P.longueur, oninput: e => { P.longueur = Number(e.target.value); generer(); dessiner(); } }), el("span", {}, String(P.longueur))),
          el("div", { class: "mdp-options" },
            el("label", { class: "mdp-option" }, el("input", { type: "checkbox", checked: P.maj ? "" : null, onchange: e => { P.maj = e.target.checked; generer(); dessiner(); } }), t("Majuscules")),
            el("label", { class: "mdp-option" }, el("input", { type: "checkbox", checked: P.min ? "" : null, onchange: e => { P.min = e.target.checked; generer(); dessiner(); } }), t("Minuscules")),
            el("label", { class: "mdp-option" }, el("input", { type: "checkbox", checked: P.chiffres ? "" : null, onchange: e => { P.chiffres = e.target.checked; generer(); dessiner(); } }), t("Chiffres")),
            el("label", { class: "mdp-option" }, el("input", { type: "checkbox", checked: P.symboles ? "" : null, onchange: e => { P.symboles = e.target.checked; generer(); dessiner(); } }), t("Symboles")),
            el("label", { class: "mdp-option", style: "grid-column:1/-1" }, el("input", { type: "checkbox", checked: P.exclure ? "" : null, onchange: e => { P.exclure = e.target.checked; generer(); dessiner(); } }), t("Exclure les caractères ambigus"))),
          el("div", { style: "display:flex;gap:8px;margin-top:12px" },
            el("button", { class: "btn", onclick: () => { generer(); dessiner(); } }, icone("refresh-cw"), " " + t("Générer")),
            el("button", { class: "btn discret", onclick: () => copier(P.valeur) }, icone("copy"), " " + t("Copier"))))));
  }

  VUES.genmdp = { afficher: () => dessiner(), titre: "Mot de passe", icone: "key", groupe: "outils", ordre: 35,
    description: "Générateur de mots de passe sécurisés (longueur, types de caractères, force).",
    profils: ["freelance", "assistant_virtuel", "assistant_direction", "developpeur", "comptable", "redacteur", "designer", "consultant", "commercial", "pharmacien", "avocat", "architecte", "enseignant", "medecin"] };
})();
EOF