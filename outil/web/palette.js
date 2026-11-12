"use strict";
/* Onglet « Palette » : générateur de palettes de couleurs (harmonies). */
(() => {
  I18N.ajouter({
    "Palette": "Palette",
    "Générateur de palettes": "Color palette generator",
    "Couleur de base": "Base color",
    "Harmonie": "Harmony",
    "Complémentaire": "Complementary",
    "Analogue": "Analogous",
    "Triadique": "Triadic",
    "Tétradique": "Tetradic",
    "Monochromatique": "Monochromatic",
    "Copier": "Copy",
    "Copier tout": "Copy all",
  });

  const PA = { hex: "#6c4cf5", harmonie: "complementaire", couleurs: [] };

  const style = document.createElement("style");
  style.textContent = `
    .pal { display: flex; flex-direction: column; gap: 16px; max-width: 640px; }
    .pal-carte { background: var(--carte); border: 1px solid var(--ligne); border-radius: var(--rayon); box-shadow: var(--ombre); padding: 20px; }
    .pal-puces { display: flex; gap: 4px; flex-wrap: wrap; }
    .pal-puce { border: 0; height: 28px; padding: 0 11px; border-radius: 6px; background: var(--surface); color: var(--doux); cursor: pointer; font-size: 12.5px; font-weight: 500; white-space: nowrap; transition: background .12s, color .12s; }
    .pal-puce:hover { color: var(--encre); }
    .pal-puce.actif { background: var(--violet-clair); color: var(--violet); }
    .pal-couleurs { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
    .pal-couleur { width: 90px; height: 90px; border-radius: 10px; display: flex; align-items: flex-end; justify-content: center; padding: 6px; font-size: 11px; font-family: "SF Mono", monospace; color: #fff; text-shadow: 0 1px 2px rgba(0,0,0,.5); cursor: pointer; transition: transform .12s; }
    .pal-couleur:hover { transform: scale(1.05); }
    .pal-ligne { display: flex; align-items: center; gap: 12px; }
    .pal-ligne label { font-size: 12.5px; font-weight: 500; color: var(--doux); min-width: 100px; }
    .pal-ligne input[type=color] { width: 48px; height: 32px; border: 0; border-radius: 6px; cursor: pointer; }
  `;
  document.head.append(style);

  function hexToHsl(hex) {
    let r = parseInt(hex.slice(1, 3), 16) / 255;
    let g = parseInt(hex.slice(3, 5), 16) / 255;
    let b = parseInt(hex.slice(5, 7), 16) / 255;
    const max = Math.max(r, g, b), min = Math.min(r, g, b);
    let h, s, l = (max + min) / 2;
    if (max === min) { h = s = 0; }
    else {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      switch (max) {
        case r: h = ((g - b) / d + (g < b ? 6 : 0)); break;
        case g: h = ((b - r) / d + 2); break;
        case b: h = ((r - g) / d + 4); break;
      }
      h *= 60;
    }
    return [h, s * 100, l * 100];
  }

  function hslToHex(h, s, l) {
    s /= 100; l /= 100;
    const k = n => (n + h / 30) % 12;
    const a = s * Math.min(l, 1 - l);
    const f = n => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
    const toHex = x => Math.round(x * 255).toString(16).padStart(2, "0");
    return "#" + toHex(f(0)) + toHex(f(8)) + toHex(f(4));
  }

  function generer() {
    const [h, s, l] = hexToHsl(PA.hex);
    let hs = [];
    switch (PA.harmonie) {
      case "complementaire":
        hs = [h, (h + 180) % 360]; break;
      case "analogue":
        hs = [h - 30, h, h + 30].map(x => (x + 360) % 360); break;
      case "triadique":
        hs = [h, (h + 120) % 360, (h + 240) % 360]; break;
      case "tetradique":
        hs = [h, (h + 90) % 360, (h + 180) % 360, (h + 270) % 360]; break;
      case "monochromatique":
        hs = [h, h, h, h, h]; break;
    }
    PA.couleurs = hs.map((hh, i) => {
      if (PA.harmonie === "monochromatique") {
        return hslToHex(hh, s, Math.max(10, Math.min(90, l + (i - 2) * 15)));
      }
      return hslToHex(hh, s, l);
    });
  }

  function dessiner() {
    if (!PA.couleurs.length) generer();
    $("#vue-palette").replaceChildren(
      el("div", { class: "barre-vue" }, el("h2", {}, icone("palette"), " " + t("Palette")), el("span", { class: "espace" })),
      el("div", { class: "pal" },
        el("div", { class: "pal-carte" },
          el("div", { class: "pal-ligne" }, el("label", {}, t("Couleur de base")), el("input", { type: "color", value: PA.hex, oninput: e => { PA.hex = e.target.value; generer(); dessiner(); } }), el("span", {}, PA.hex)),
          el("div", { class: "pal-ligne" }, el("label", {}, t("Harmonie")), el("select", { onchange: e => { PA.harmonie = e.target.value; generer(); dessiner(); } },
            ["complementaire", "analogue", "triadique", "tetradique", "monochromatique"].map(h =>
              el("option", { value: h, selected: h === PA.harmonie ? "" : null }, t({ complementaire: "Complémentaire", analogue: "Analogue", triadique: "Triadique", tetradique: "Tétradique", monochromatique: "Monochromatique" }[h]))))),
          el("div", { class: "pal-couleurs" }, PA.couleurs.map(c =>
            el("div", { class: "pal-couleur", style: `background:${c}`, onclick: () => copier(c) }, c))),
          el("div", { style: "display:flex;gap:8px;margin-top:12px" },
            el("button", { class: "btn discret", onclick: () => copier(PA.couleurs.join(", ")) }, icone("copy"), " " + t("Copier tout"))))));
  }

  VUES.palette = { afficher: () => dessiner(), titre: "Palette", icone: "palette", groupe: "outils", ordre: 70,
    description: "Générateur de palettes de couleurs (harmonies complémentaires, analogues, triadiques…).",
    profils: ["freelance", "assistant_virtuel", "assistant_direction", "developpeur", "comptable", "redacteur", "designer", "consultant", "commercial", "pharmacien", "avocat", "architecte", "enseignant", "medecin"] };
})();
EOF