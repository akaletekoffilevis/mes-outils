"use strict";
/* Onglet « Hash » : hachage cryptographique (MD5, SHA-1, SHA-256, SHA-384,
   SHA-512) côté client, via l'API Web Crypto. */
(() => {
  I18N.ajouter({
    "Hash": "Hash",
    "Hachage cryptographique": "Cryptographic hashing",
    "Texte à hacher": "Text to hash",
    "Résultat": "Result",
    "Copier": "Copy",
    "Algorithme": "Algorithm",
    "Hacher": "Hash",
    "Vide": "Empty",
  });

  const H = { algo: "SHA-256", texte: "", resultat: "" };

  const style = document.createElement("style");
  style.textContent = `
    .hash { display: flex; flex-direction: column; gap: 16px; max-width: 640px; }
    .hash-carte { background: var(--carte); border: 1px solid var(--ligne); border-radius: var(--rayon); box-shadow: var(--ombre); padding: 20px; }
    .hash-resultat { font-family: "SF Mono", "Consolas", monospace; font-size: 13px; word-break: break-all; padding: 12px; border-radius: 8px; background: var(--surface); min-height: 40px; }
    .hash-puces { display: flex; gap: 4px; flex-wrap: wrap; }
    .hash-puce { border: 0; height: 28px; padding: 0 11px; border-radius: 6px; background: var(--surface); color: var(--doux); cursor: pointer; font-size: 12.5px; font-weight: 500; white-space: nowrap; transition: background .12s, color .12s; }
    .hash-puce:hover { color: var(--encre); }
    .hash-puce.actif { background: var(--violet-clair); color: var(--violet); }
  `;
  document.head.append(style);

  async function hacher() {
    const enc = new TextEncoder().encode(H.texte);
    let buf;
    if (H.algo === "MD5") {
      // MD5 n'est pas dans Web Crypto ; on l'approxime via un calcul simple.
      // Pour un vrai MD5, utiliser une librairie. Ici on indique l'indisponibilité.
      H.resultat = "(MD5 non disponible côté navigateur — utilisez SHA-256)";
      dessiner();
      return;
    }
    try {
      buf = await crypto.subtle.digest(H.algo, enc);
      H.resultat = [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, "0")).join("");
    } catch (e) {
      H.resultat = "Erreur : " + e.message;
    }
    dessiner();
  }

  function dessiner() {
    $("#vue-hash").replaceChildren(
      el("div", { class: "barre-vue" }, el("h2", {}, icone("hash"), t("Hash")), el("span", { class: "espace" })),
      el("div", { class: "hash" },
        el("div", { class: "hash-carte" },
          el("div", { class: "hash-puces" }, ["SHA-1", "SHA-256", "SHA-384", "SHA-512"].map(a =>
            el("button", { class: "hash-puce " + (a === H.algo ? " actif" : ""), onclick: () => { H.algo = a; hacher(); } }, a))),
          el("textarea", { class: "zone", rows: 4, placeholder: t("Texte à hacher"), oninput: e => { H.texte = e.target.value; hacher(); } }, H.texte),
          el("div", { class: "hash-resultat" }, H.resultat || t("Vide")),
          el("button", { class: "btn discret", onclick: () => copier(H.resultat) }, icone("copy"), t("Copier")))));
  }

  VUES.hash = { afficher: () => { if (!H.resultat && H.texte) hacher(); dessiner(); }, titre: "Hash", icone: "hash", groupe: "outils", ordre: 60,
    description: "Hachage cryptographique (SHA-1, SHA-256, SHA-384, SHA-512) côté client.",
    profils: ["freelance", "assistant_virtuel", "assistant_direction", "developpeur", "comptable", "redacteur", "designer", "consultant", "commercial", "pharmacien", "avocat", "architecte", "enseignant", "medecin"] };
})();
EOF