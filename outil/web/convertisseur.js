"use strict";
/* Onglet « Convertisseur » : conversions d'unités (longueur, masse, température,
   volume, vitesse, données). Tout se passe dans la page. */
(() => {
  I18N.ajouter({
    "Convertisseur": "Converter",
    "Conversions d'unités": "Unit conversions",
    "De": "From",
    "Vers": "To",
    "Valeur": "Value",
    "Résultat": "Result",
    "Copier": "Copy",
    "Catégorie": "Category",
    "Longueur": "Length",
    "Masse": "Weight",
    "Température": "Temperature",
    "Volume": "Volume",
    "Vitesse": "Speed",
    "Données": "Data",
    "Temps": "Time",
  });

  const CATEGORIES = [
    { nom: "Longueur", unites: {
        "m": v => v, "cm": v => v / 100, "mm": v => v / 1000, "km": v => v * 1000,
        "in": v => v * 0.0254, "ft": v => v * 0.3048, "yd": v => v * 0.9144, "mi": v => v * 1609.344,
      } },
    { nom: "Masse", unites: {
        "g": v => v / 1000, "kg": v => v, "lb": v => v * 0.453592, "oz": v => v * 0.0283495,
        "t": v => v * 1000, "mg": v => v / 1e6,
      } },
    { nom: "Température", unites: {
        "°C": v => v, "°F": v => (v - 32) * 5 / 9, "K": v => v - 273.15,
      } },
    { nom: "Volume", unites: {
        "L": v => v, "mL": v => v / 1000, "gal": v => v * 3.78541, "qt": v => v * 0.946353,
        "cup": v => v * 0.236588, "m³": v => v * 1000, "cm³": v => v / 1000,
      } },
    { nom: "Vitesse", unites: {
        "km/h": v => v / 3.6, "m/s": v => v, "mph": v => v * 0.44704, "nœuds": v => v * 0.514444,
      } },
    { nom: "Données", unites: {
        "B": v => v, "KB": v => v * 1024, "MB": v => v * 1024 ** 2, "GB": v => v * 1024 ** 3,
        "TB": v => v * 1024 ** 4, "bit": v => v / 8,
      } },
    { nom: "Temps", unites: {
        "s": v => v, "min": v => v * 60, "h": v => v * 3600, "jour": v => v * 86400,
        "sem": v => v * 604800, "mois": v => v * 2629800,
      } },
  ];

  const style = document.createElement("style");
  style.textContent = `
    .conv { display: flex; flex-direction: column; gap: 16px; }
    .conv-carte { background: var(--carte); border: 1px solid var(--ligne); border-radius: var(--rayon); box-shadow: var(--ombre); padding: 20px; }
    .conv-ligne { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 12px; }
    .conv-ligne label { font-size: 12.5px; font-weight: 500; color: var(--doux); min-width: 60px; }
    .conv-ligne input, .conv-ligne select { flex: 1; min-width: 120px; }
    .conv-resultat { font-size: 28px; font-weight: 600; letter-spacing: -.02em; color: var(--violet); text-align: center; padding: 12px 0; font-variant-numeric: tabular-nums; }
    .conv-resultat small { font-size: 14px; color: var(--doux); font-weight: 500; }
    .conv-puces { display: flex; gap: 4px; flex-wrap: wrap; }
    .conv-puce { border: 0; height: 28px; padding: 0 11px; border-radius: 6px; background: var(--surface); color: var(--doux); cursor: pointer; font-size: 12.5px; font-weight: 500; white-space: nowrap; transition: background .12s, color .12s; }
    .conv-puce:hover { color: var(--encre); }
    .conv-puce.actif { background: var(--violet-clair); color: var(--violet); }
  `;
  document.head.append(style);

  const C = { categorie: 0, de: "m", vers: "cm", valeur: 1 };

  function convertir() {
    const cat = CATEGORIES[C.categorie];
    const fDe = cat.unites[C.de], fVers = cat.unites[C.vers];
    if (!fDe || !fVers) return 0;
    const base = fDe(Number(C.valeur) || 0);
    return fVers === cat.unites[C.vers] ? (Object.keys(cat.unites).find(k => cat.unites[k] === fVers) ? base / fVers(1) * 1 : base) : base;
  }

  // Conversion correcte : de -> unité de base -> vers
  function calculer() {
    const cat = CATEGORIES[C.categorie];
    const fDe = cat.unites[C.de], fVers = cat.unites[C.vers];
    if (!fDe || !fVers) return 0;
    const base = fDe(Number(C.valeur) || 0);
    // fVers(base) donne la valeur en unité "vers" si fVers convertit vers→base.
    // Donc : valeur_vers = base / fVers(1) ... non. fVers(x) = x en base.
    // On veut : x_vers tel que fVers(x_vers) = base → x_vers = fVers^{-1}(base).
    // Comme fVers est linéaire (fVers(x) = k*x + b pour température), on utilise
    // la formule directe : base / k où k = fVers(1) - fVers(0) ... sauf température.
    // Plus simple : résoudre numériquement.
    let lo = -1e12, hi = 1e12;
    for (let i = 0; i < 60; i++) {
      const mid = (lo + hi) / 2;
      if (fVers(mid) < base) lo = mid; else hi = mid;
    }
    return (lo + hi) / 2;
  }

  function dessiner() {
    const cat = CATEGORIES[C.categorie];
    const unites = Object.keys(cat.unites);
    if (!unites.includes(C.de)) C.de = unites[0];
    if (!unites.includes(C.vers)) C.vers = unites[1] || unites[0];

    const resultat = calculer();
    const valeur = Number(C.valeur) || 0;
    const texte = `${valeur} ${C.de} = ${resultat.toLocaleString(I18N.locale(), { maximumFractionDigits: 6 })} ${C.vers}`;

    $("#vue-convertisseur").replaceChildren(
      el("div", { class: "barre-vue" }, el("h2", {}, icone("repeat"), t("Convertisseur")), el("span", { class: "espace" })),
      el("div", { class: "conv" },
        el("div", { class: "conv-carte" },
          el("div", { class: "conv-puces" }, CATEGORIES.map((c, i) =>
            el("button", { class: "conv-puce " + (i === C.categorie ? " actif" : ""), onclick: () => { C.categorie = i; const u = Object.keys(CATEGORIES[i].unites); C.de = u[0]; C.vers = u[1] || u[0]; dessiner(); } }, t(c.nom)))),
          el("div", { class: "conv-ligne" }, el("label", {}, t("Valeur")), el("input", { type: "number", value: C.valeur, step: "any", oninput: e => { C.valeur = e.target.value; dessiner(); } })),
          el("div", { class: "conv-ligne" }, el("label", {}, t("De")), el("select", { onchange: e => { C.de = e.target.value; dessiner(); } },
            unites.map(u => el("option", { value: u, selected: u === C.de ? "" : null }, u)))),
          el("div", { class: "conv-ligne" }, el("label", {}, t("Vers")), el("select", { onchange: e => { C.vers = e.target.value; dessiner(); } },
            unites.map(u => el("option", { value: u, selected: u === C.vers ? "" : null }, u)))),
          el("div", { class: "conv-resultat" }, `${resultat.toLocaleString(I18N.locale(), { maximumFractionDigits: 6 })} ${C.vers}`, el("small", {}, ` = ${valeur} ${C.de}`)),
          el("button", { class: "btn", onclick: () => copier(texte) }, icone("copy"), t("Copier")))));
  }

  VUES.convertisseur = { afficher: () => dessiner(), titre: "Convertisseur", icone: "repeat", groupe: "outils", ordre: 30,
    description: "Conversions d'unités : longueur, masse, température, volume, vitesse, données, temps.",
    profils: ["freelance", "assistant_virtuel", "assistant_direction", "developpeur", "comptable", "redacteur", "designer", "consultant", "commercial"] };
})();
EOF