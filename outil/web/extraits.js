"use strict";
/* Onglet « Extraits » : bouts de code et commandes favoris (voir extraits.py).
   Copie en un clic (comptée), recherche plein texte, filtres par langage et
   par étiquette, épingles. */
(() => {
  I18N.ajouter({
    "Extraits": "Snippets",
    "Mes extraits": "My snippets",
    "Chercher dans les extraits…": "Search snippets…",
    "＋ Extrait": "＋ Snippet",
    "Les plus utilisés": "Most used",
    "A → Z": "A → Z",
    "Récents": "Recent",
    "Tous": "All",
    "Langage": "Language",
    "Étiquette": "Tag",
    "Titre": "Title",
    "Contenu": "Content",
    "Étiquettes": "Tags",
    "séparées par des virgules": "comma-separated",
    "ex. Redémarrer le service": "e.g. Restart the service",
    "ex. bash, sql, python": "e.g. bash, sql, python",
    "ex. serveur, git": "e.g. server, git",
    "Épingler en haut": "Pin to the top",
    "Épinglé": "Pinned",
    "Copier": "Copy",
    "Modifier": "Edit",
    "Supprimer": "Delete",
    "Épingler": "Pin",
    "Désépingler": "Unpin",
    "Cliquer pour copier": "Click to copy",
    "Annuler": "Cancel",
    "Enregistrer": "Save",
    "Ajouter": "Add",
    " Modifier l'extrait": " Edit snippet",
    " Nouvel extrait": " New snippet",
    " Copié": " Copied",
    " Extrait enregistré": " Snippet saved",
    " Extrait supprimé": " Snippet deleted",
    "Supprimer cet extrait ?": "Delete this snippet?",
    "Il disparaît définitivement.": "It will be gone for good.",
    "Pas encore d'extrait. Gardez ici vos commandes et bouts de code favoris ":
      "No snippet yet. Keep your favourite commands and code here ",
    "Aucun extrait ne correspond.": "No snippet matches.",
    "Tab insère deux espaces.": "Tab inserts two spaces.",
    "{n} utilisations": "used {n} times",
    "1 utilisation": "used once",
    "jamais utilisé": "never used",
    "Donnez un titre à l'extrait.": "Give the snippet a title.",
    "L'extrait est vide.": "The snippet is empty.",
    "Titre trop long (120 caractères au plus).": "Title too long (120 characters max).",
    "Extrait trop long (100 000 caractères au plus).": "Snippet too long (100,000 characters max).",
    "Extrait introuvable.": "Snippet not found.",
    "Le presse-papiers est occupé par un autre programme.": "The clipboard is in use by another program.",
  });

  const X = { extraits: [], total: 0, langages: [], etiquettes: [], recherche: "", langage: "", etiquette: "", tri: "usage" };
  let minuterie = null;

  const style = document.createElement("style");
  style.textContent = `
    .ex-filtres { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin: -6px 0 16px; }
    .ex-filtres .lib { font-size: 12px; font-weight: 600; color: var(--gris); text-transform: uppercase; letter-spacing: .8px; }
    .ex-filtres .etiquette { cursor: pointer; border: 0; }
    .ex-filtres .etiquette.actif { background: var(--violet); color: var(--sur-violet); }
    .ex-grille { display: grid; grid-template-columns: repeat(auto-fill, minmax(330px, 1fr)); gap: 14px; align-items: start; }
    .ex-carte { display: flex; flex-direction: column; gap: 8px; animation: apparait .35s both; min-width: 0; }
    .ex-tete { display: flex; align-items: center; gap: 8px; min-width: 0; }
    .ex-tete .titre { font-weight: 600; font-size: 15px; flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .ex-code { margin: 0; background: var(--code); color: var(--code-texte); font-family: var(--mono); font-size: 12.5px; line-height: 1.5;
      border: 1px solid var(--ligne); border-radius: 12px; padding: 10px 12px; max-height: 170px; overflow: hidden; white-space: pre-wrap;
      word-break: break-word; cursor: copy; position: relative; transition: border-color .15s; }
    .ex-code:hover { border-color: var(--violet); }
    .ex-code.long::after { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 36px;
      background: linear-gradient(transparent, var(--code)); }
    .ex-bas { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
    .ex-bas .usage { font-size: 12px; color: var(--gris); font-weight: 600; margin-right: auto; }
    .ex-bas .btn { padding: 6px 12px; font-size: 13px; }
    .ex-bas .icone-btn { width: 30px; height: 30px; font-size: 13px; }
    .ex-epingle { color: var(--ambre-texte); }
    .ex-editeur textarea { font-family: var(--mono); font-size: 13px; line-height: 1.5; min-height: 220px; resize: vertical; tab-size: 2; }
    .ex-case { display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 14px; color: var(--encre); cursor: pointer; }
    .ex-case input { width: 17px; height: 17px; }
  `;
  document.head.append(style);

  async function charger() {
    const r = await api("/api/extraits/liste", { recherche: X.recherche, langage: X.langage, etiquette: X.etiquette, tri: X.tri });
    Object.assign(X, r);
    // Un filtre qui ne correspond plus à rien (dernier extrait supprimé) est retiré.
    if (X.langage && !X.langages.includes(X.langage)) { X.langage = ""; return charger(); }
    if (X.etiquette && !X.etiquettes.includes(X.etiquette)) { X.etiquette = ""; return charger(); }
    dessiner();
  }
  const recharger = () => charger().catch(e => toast(e.message, "erreur"));

  function dessiner() {
    const vue = $("#vue-extraits");
    const ancienne = vue.querySelector(".ex-recherche");
    const avaitFocus = ancienne && document.activeElement === ancienne;
    const recherche = el("input", { class: "ex-recherche", placeholder: "Chercher dans les extraits…", value: X.recherche,
      oninput: e => { X.recherche = e.target.value; clearTimeout(minuterie); minuterie = setTimeout(recharger, 200); } });
    const tris = [["usage", "Les plus utilisés"], ["titre", "A → Z"], ["recent", "Récents"]];
    vue.replaceChildren(
      el("div", { class: "barre-vue" },
        el("h2", {}, t("Mes extraits") + " ", el("span", { class: "compte" }, String(X.total))),
        el("div", { class: "puces" }, tris.map(([v, lib]) =>
          el("button", { class: "puce " + (X.tri === v ? " actif" : ""), onclick: () => { X.tri = v; recharger(); } }, lib))),
        el("div", { class: "espace" }),
        el("div", { class: "champ-recherche" }, el("span", {}, icone("search")), recherche),
        el("button", { class: "btn principal", onclick: () => editer(null) }, "＋ Extrait")),
      ...[filtres(), grille()].filter(Boolean));
    if (avaitFocus) { recherche.focus(); recherche.setSelectionRange(recherche.value.length, recherche.value.length); }
  }

  function filtres() {
    if (!X.langages.length && !X.etiquettes.length) return null;
    const puce = (valeur, actuel, lib, choisir) =>
      el("button", { class: "etiquette " + (valeur === actuel ? " actif" : ""), onclick: () => { choisir(valeur); recharger(); } }, lib);
    return el("div", { class: "ex-filtres" },
      X.langages.length ? [el("span", { class: "lib" }, "Langage"),
        puce("", X.langage, "Tous", v => (X.langage = v)),
        X.langages.map(l => puce(l, X.langage, l, v => (X.langage = v)))] : null,
      X.etiquettes.length ? [el("span", { class: "lib", style: "margin-left:8px" }, "Étiquette"),
        puce("", X.etiquette, "Tous", v => (X.etiquette = v)),
        X.etiquettes.map(l => puce(l, X.etiquette, "# " + l, v => (X.etiquette = v)))] : null);
  }

  function grille() {
    if (!X.extraits.length) {
      return el("div", { class: "vide" }, X.total ? t("Aucun extrait ne correspond.")
        : t("Pas encore d'extrait. Gardez ici vos commandes et bouts de code favoris "));
    }
    return el("div", { class: "ex-grille" }, X.extraits.map((x, i) => carte(x, i)));
  }

  function usage(n) {
    return n === 0 ? t("jamais utilisé") : n === 1 ? t("1 utilisation") : t("{n} utilisations", { n });
  }

  function carte(x, i) {
    const long = x.contenu.split("\n").length > 8 || x.contenu.length > 600;
    return el("div", { class: "carte ex-carte", style: `animation-delay:${Math.min(i, 12) * 25}ms` },
      el("div", { class: "ex-tete" },
        x.epingle ? el("span", { class: "ex-epingle", title: "Épinglé" }, icone("pin")) : null,
        el("span", { class: "titre", title: x.titre }, x.titre),
        x.langage ? el("span", { class: "etiquette violet" }, x.langage) : null),
      el("pre", { class: "ex-code " + (long ? " long" : ""), title: "Cliquer pour copier", onclick: () => copierExtrait(x) },
        x.contenu.length > 2000 ? x.contenu.slice(0, 2000) : x.contenu),
      x.etiquettes.length ? el("div", { class: "ex-bas" }, x.etiquettes.map(e =>
        el("span", { class: "etiquette", style: "cursor:pointer", onclick: () => { X.etiquette = e; recharger(); } }, "# " + e))) : null,
      el("div", { class: "ex-bas" },
        el("span", { class: "usage" }, usage(x.utilisations || 0)),
        el("button", { class: "icone-btn", title: x.epingle ? "Désépingler" : "Épingler", onclick: () => epingler(x) }, x.epingle ? "" : icone("pin")),
        el("button", { class: "icone-btn", title: "Modifier", onclick: () => editer(x) }, icone("pencil")),
        el("button", { class: "icone-btn danger", title: "Supprimer", onclick: () => supprimer(x) }, icone("trash-2")),
        el("button", { class: "btn principal", onclick: () => copierExtrait(x) }, t("Copier"))));
  }

  async function copierExtrait(x) {
    try {
      await api("/api/extraits/copier", { id: x.id });
      toast("Copié", "succes", 1400);
    } catch (e) {
      // Presse-papiers du système occupé (ou absent) : on essaie par le navigateur.
      await copier(x.contenu);
      api("/api/extraits/utiliser", { id: x.id }).catch(() => {});
    }
    recharger();
  }

  async function epingler(x) {
    try { await api("/api/extraits/epingler", { id: x.id, epingle: !x.epingle }); recharger(); }
    catch (e) { toast(e.message, "erreur"); }
  }

  async function supprimer(x) {
    if (!(await confirmer(icone("trash-2"), "Supprimer cet extrait ?", "Il disparaît définitivement.", "Supprimer"))) return;
    try { await api("/api/extraits/supprimer", { id: x.id }); toast("Extrait supprimé"); recharger(); }
    catch (e) { toast(e.message, "erreur"); }
  }

  function editer(x) {
    const b = x ? structuredClone(x) : { titre: "", langage: X.langage || "", contenu: "", etiquettes: X.etiquette ? [X.etiquette] : [], epingle: false };
    const titre = el("input", { value: b.titre, placeholder: "ex. Redémarrer le service", maxlength: 120 });
    const langage = el("input", { value: b.langage, placeholder: "ex. bash, sql, python", maxlength: 30, list: "ex-langages" });
    const etiquettes = el("input", { value: (b.etiquettes || []).join(", "), placeholder: "ex. serveur, git" });
    const contenu = el("textarea", { value: b.contenu, spellcheck: "false", rows: 10 });
    contenu.addEventListener("keydown", e => {
      if (e.key !== "Tab" || e.shiftKey) return;
      e.preventDefault();
      contenu.setRangeText("  ", contenu.selectionStart, contenu.selectionEnd, "end");
    });
    const epingle = el("input", { type: "checkbox", checked: b.epingle ? "" : null });
    const valider = async () => {
      const extrait = { ...b, titre: titre.value, langage: langage.value, contenu: contenu.value,
        etiquettes: etiquettes.value, epingle: epingle.checked };
      try {
        await api("/api/extraits/enregistrer", { extrait });
        fermer(); toast("Extrait enregistré", "succes", 1600); recharger();
      } catch (e) { toast(e.message, "erreur"); }
    };
    fenetre([el("div", { class: "ex-editeur" },
      el("h3", {}, x ? " Modifier l'extrait" : " Nouvel extrait"),
      el("label", { class: "champ" }, "Titre", titre),
      el("div", { style: "display:grid;grid-template-columns:1fr 1.4fr;gap:12px" },
        el("label", { class: "champ" }, "Langage", langage,
          el("datalist", { id: "ex-langages" }, X.langages.map(l => el("option", { value: l })))),
        el("label", { class: "champ" }, el("span", {}, t("Étiquettes") + " ", el("small", {}, "( " + t("séparées par des virgules") + ")")), etiquettes)),
      el("label", { class: "champ" }, "Contenu", contenu, el("small", {}, "Tab insère deux espaces.")),
      el("label", { class: "ex-case" }, epingle, "Épingler en haut"),
      el("div", { class: "actions" },
        el("button", { class: "btn", onclick: fermer }, "Annuler"),
        el("button", { class: "btn principal", onclick: valider }, x ? "Enregistrer" : "Ajouter")))]);
    $("#fenetre").style.width = "min(720px, 94vw)";
    setTimeout(() => (x ? contenu : titre).focus(), 60);
  }

  VUES.extraits = { afficher: recharger, titre: "Extraits", icone: icone("scissors"), groupe: "outils", ordre: 20 };
})();
