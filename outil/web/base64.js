"use strict";
/* Onglet « Base64 » : encodage/décodage Base64 côté client. */
(() => {
  I18N.ajouter({
    "Base64": "Base64",
    "Encodeur / décodeur Base64": "Base64 encoder / decoder",
    "Texte": "Text",
    "Base64": "Base64",
    "Encoder": "Encode",
    "Décoder": "Decode",
    "Copier": "Copy",
    "Effacer": "Clear",
    "Erreur de décodage": "Decoding error",
  });

  const B = { texte: "", base64: "", mode: "encode" };

  const style = document.createElement("style");
  style.textContent = `
    .b64 { display: flex; flex-direction: column; gap: 16px; max-width: 640px; }
    .b64-carte { background: var(--carte); border: 1px solid var(--ligne); border-radius: var(--rayon); box-shadow: var(--ombre); padding: 20px; }
    .b64-zone { width: 100%; min-height: 120px; font-family: "SF Mono", "Consolas", monospace; font-size: 13px; resize: vertical; }
    .b64-puces { display: flex; gap: 4px; }
    .b64-puce { border: 0; height: 28px; padding: 0 11px; border-radius: 6px; background: var(--surface); color: var(--doux); cursor: pointer; font-size: 12.5px; font-weight: 500; transition: background .12s, color .12s; }
    .b64-puce:hover { color: var(--encre); }
    .b64-puce.actif { background: var(--violet-clair); color: var(--violet); }
  `;
  document.head.append(style);

  function encoder() {
    try {
      B.base64 = btoa(unescape(encodeURIComponent(B.texte)));
    } catch (e) {
      B.base64 = "Erreur : " + e.message;
    }
  }

  function decoder() {
    try {
      B.texte = decodeURIComponent(escape(atob(B.base64.trim())));
    } catch (e) {
      B.texte = t("Erreur de décodage");
    }
  }

  function dessiner() {
    $("#vue-base64").replaceChildren(
      el("div", { class: "barre-vue" }, el("h2", {}, icone("code"), " " + t("Base64")), el("span", { class: "espace" })),
      el("div", { class: "b64" },
        el("div", { class: "b64-carte" },
          el("div", { class: "b64-puces" },
            el("button", { class: "b64-puce" + (B.mode === "encode" ? " actif" : ""), onclick: () => { B.mode = "encode"; encoder(); dessiner(); } }, t("Encoder")),
            el("button", { class: "b64-puce" + (B.mode === "decode" ? " actif" : ""), onclick: () => { B.mode = "decode"; decoder(); dessiner(); } }, t("Décoder"))),
          el("label", { class: "champ" }, t("Texte"), el("textarea", { class: "b64-zone zone", oninput: e => { B.texte = e.target.value; if (B.mode === "encode") encoder(); dessiner(); } }, B.texte)),
          el("label", { class: "champ" }, "Base64", el("textarea", { class: "b64-zone zone", oninput: e => { B.base64 = e.target.value; if (B.mode === "decode") decoder(); dessiner(); } }, B.base64)),
          el("div", { style: "display:flex;gap:8px" },
            el("button", { class: "btn discret", onclick: () => copier(B.mode === "encode" ? B.base64 : B.texte) }, icone("copy"), " " + t("Copier")),
            el("button", { class: "btn discret", onclick: () => { B.texte = ""; B.base64 = ""; dessiner(); } }, icone("trash-2"), " " + t("Effacer"))))));
  }

  VUES.base64 = { afficher: () => dessiner(), titre: "Base64", icone: "code", groupe: "outils", ordre: 75,
    description: "Encodage et décodage Base64 côté client.",
    profils: ["freelance", "assistant_virtuel", "assistant_direction", "developpeur", "comptable", "redacteur", "designer", "consultant", "commercial", "pharmacien", "avocat", "architecte", "enseignant", "medecin"] };
})();
EOF