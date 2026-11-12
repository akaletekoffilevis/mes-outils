"use strict";
/* Onglet « QR code » : génération de QR codes (tout dans la page). */
(() => {
  I18N.ajouter({
    "QR code": "QR code",
    "Générateur de QR code": "QR code generator",
    "Contenu": "Content",
    "Taille": "Size",
    "Correction d'erreur": "Error correction",
    "Générer": "Generate",
    "Télécharger (SVG)": "Download (SVG)",
    "Copier le SVG": "Copy the SVG",
    "SVG copié": "SVG copied",
    "Le contenu est vide.": "The content is empty.",
  });

  const Q = { texte: "", ecl: "M", taille: 4, svg: "" };

  const style = document.createElement("style");
  style.textContent = `
    .qrcode { display: flex; flex-direction: column; gap: 16px; align-items: center; }
    .qrcode-carte { background: var(--carte); border: 1px solid var(--ligne); border-radius: var(--rayon); box-shadow: var(--ombre); padding: 20px; width: 100%; max-width: 520px; }
    .qrcode-apercu { display: flex; justify-content: center; padding: 16px; background: #ffffff; border-radius: 8px; border: 1px solid var(--ligne); min-height: 120px; align-items: center; }
    .qrcode-apercu svg { max-width: 100%; height: auto; }
    .qrcode-actions { display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; margin-top: 12px; }
    .qrcode-vide { padding: 32px 20px; text-align: center; color: var(--doux); }
  `;
  document.head.append(style);

  function generer() {
    const texte = Q.texte.trim();
    if (!texte) { toast(t("Le contenu est vide."), "erreur"); return; }
    try {
      const qr = qrcode(0, Q.ecl);
      qr.addData(texte, "Byte");
      qr.make();
      Q.svg = qr.createSvgTag(Q.taille, 4);
      dessiner();
    } catch (e) { toast("Probleme :" + e.message, "erreur"); }
  }

  function dessiner() {
    const zone = $("#vue-qrcode");
    if (!zone) return;

    const apercu = el("div", { class: "qrcode-apercu", id: "qrcode-apercu" });
    if (Q.svg) apercu.innerHTML = Q.svg;
    else apercu.append(el("div", { style: "color:var(--gris);font-size:13px" }, t("Le contenu est vide.")));

    const boutons = el("div", { class: "qrcode-actions" },
      el("button", { class: "btn principal", onclick: generer }, icone("square"), " " + t("Générer")),
      Q.svg ? el("button", { class: "btn", onclick: () => telechargerSvg() }, icone("download"), " " + t("Télécharger (SVG)")) : null,
      Q.svg ? el("button", { class: "btn discret", onclick: () => copier(Q.svg, t("SVG copié")) }, icone("copy"), " " + t("Copier le SVG")) : null);

    const carte = el("div", { class: "qrcode-carte" });
    const labelContenu = el("label", { class: "champ" }, t("Contenu"),
      el("textarea", { rows: 3, value: Q.texte, placeholder: "https://... ou tout texte", oninput: e => { Q.texte = e.target.value; } }));
    const ligneTaille = el("div", { style: "display:flex;gap:12px;flex-wrap:wrap" });
    const labelTaille = el("label", { class: "champ" }, t("Taille"),
      el("select", { onchange: e => { Q.taille = Number(e.target.value); generer(); } },
        [2, 3, 4, 5, 6, 8].map(n => el("option", { value: n, selected: n === Q.taille ? "" : null }, String(n)))));
    const labelEcl = el("label", { class: "champ" }, t("Correction d'erreur"),
      el("select", { onchange: e => { Q.ecl = e.target.value; generer(); } },
        [["L", "L (7%)"], ["M", "M (15%)"], ["Q", "Q (25%)"], ["H", "H (30%)"]].map(([v, l]) => el("option", { value: v, selected: v === Q.ecl ? "" : null }, l))));
    ligneTaille.append(labelTaille, labelEcl);
    carte.append(labelContenu, ligneTaille, boutons);

    const qrcodeDiv = el("div", { class: "qrcode" }, carte, apercu);

    zone.replaceChildren(
      el("div", { class: "barre-vue" }, el("h2", {}, icone("square"), " " + t("QR code")), el("span", { class: "espace" })),
      qrcodeDiv);

    if (Q.svg) apercu.innerHTML = Q.svg;
    else apercu.append(el("div", { style: "color:var(--gris);font-size:13px" }, t("Le contenu est vide.")));
  }

  function telechargerSvg() {
    if (!Q.svg) return;
    const blob = new Blob([Q.svg], { type: "image/svg+xml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "qrcode.svg";
    document.body.append(a); a.click(); a.remove();
    URL.revokeObjectURL(url);
  }

  VUES.qrcode = { afficher: () => dessiner(), titre: "QR code", icone: "square", groupe: "outils", ordre: 50,
    description: "Générer un QR code (texte, URL, Wi-Fi, contact) et le télécharger en SVG.",
    profils: ["freelance", "assistant_virtuel", "assistant_direction", "developpeur", "comptable", "redacteur", "designer", "consultant", "commercial"] };
})();
EOF