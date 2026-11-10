"use strict";
/* Onglet « Presse-papiers » : les derniers textes copiés (voir presse_papiers.py).
   Gardés seulement en mémoire, effacés à la fermeture de Mes outils. */
(() => {
  I18N.ajouter({
    "Presse-papiers": "Clipboard",
    "Historique du presse-papiers": "Clipboard history",
    "Chercher…": "Search…",
    "⏸ Pause": "⏸ Pause",
    "▶ Reprendre": "▶ Resume",
    "🧹 Tout effacer": "🧹 Clear all",
    "Gardé seulement en mémoire, effacé à la fermeture de Mes outils. Les mots de passe copiés depuis le coffre (et depuis la plupart des gestionnaires de mots de passe) n'y entrent pas.":
      "Kept in memory only, erased when Mes outils closes. Passwords copied from the vault (and from most password managers) never get in.",
    "En pause : les textes copiés ne sont pas gardés.": "Paused: copied texts are not kept.",
    "Rien pour l'instant : copiez un texte (Ctrl + C), il apparaîtra ici.": "Nothing yet: copy some text (Ctrl + C) and it will show up here.",
    "Aucun élément ne correspond.": "No item matches.",
    "Recopier": "Copy again",
    "Épingler": "Pin",
    "Désépingler": "Unpin",
    "Supprimer": "Delete",
    "Épinglé": "Pinned",
    "📋 Recopié": "📋 Copied again",
    "Tout effacer ?": "Clear everything?",
    "Les éléments épinglés sont gardés.": "Pinned items are kept.",
    "Effacer": "Clear",
    "{n} caractères": "{n} characters",
    "{n} lignes": "{n} lines",
    "{n} / {max} éléments": "{n} / {max} items",
    "Élément introuvable (déjà effacé ?).": "Item not found (already cleared?).",
    "50 éléments épinglés au plus : désépinglez-en un d'abord.": "50 pinned items max: unpin one first.",
    "Le presse-papiers est occupé par un autre programme.": "The clipboard is in use by another program.",
    "Copie dans le presse-papiers impossible.": "Could not copy to the clipboard.",
    // Linux sans outil de presse-papiers (MESSAGE_INDISPONIBLE de presse_papiers.py)
    "Presse-papiers indisponible : installez wl-clipboard (Wayland) ou xclip (sudo apt install wl-clipboard xclip).":
      "Clipboard unavailable: install wl-clipboard (Wayland) or xclip (sudo apt install wl-clipboard xclip).",
    "Le presse-papiers ne répond pas.": "The clipboard is not responding.",
  });

  const P = { r: null, recherche: "", empreinte: "" };
  let minuterie = null;

  const style = document.createElement("style");
  style.textContent = `
    .pp-bandeau { display: flex; gap: 10px; align-items: center; background: var(--bleu-clair); color: var(--bleu-texte);
      border-radius: 14px; padding: 10px 14px; font-size: 13.5px; font-weight: 600; margin: -4px 0 14px; }
    .pp-bandeau.pause { background: var(--ambre-clair); color: var(--ambre-texte); }
    .pp-liste { display: flex; flex-direction: column; gap: 10px; }
    .pp-element { display: flex; gap: 14px; align-items: flex-start; padding: 12px 14px; animation: apparait .3s both; }
    .pp-element.epingle { border-color: color-mix(in srgb, var(--ambre) 55%, transparent); }
    .pp-heure { flex: none; width: 58px; font-weight: 600; font-variant-numeric: tabular-nums; font-size: 14px; padding-top: 2px; }
    .pp-heure small { display: block; color: var(--gris); font-weight: 600; font-size: 11.5px; }
    .pp-corps { flex: 1; min-width: 0; cursor: copy; }
    .pp-apercu { margin: 0; font-family: var(--mono); font-size: 12.5px; line-height: 1.5; color: var(--encre); white-space: pre-wrap;
      word-break: break-word; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
    .pp-infos { font-size: 11.5px; color: var(--gris); font-weight: 600; margin-top: 4px; display: flex; gap: 8px; }
    .pp-boutons { display: flex; gap: 4px; flex: none; }
    .pp-boutons .icone-btn { width: 32px; height: 32px; font-size: 14px; }
    .pp-boutons .icone-btn.actif { background: var(--ambre-clair); }
  `;
  document.head.append(style);

  const racine = () => $("#vue-presse_papiers");
  const visible = () => racine()?.classList.contains("actif") && document.visibilityState === "visible";

  async function charger(force = false) {
    const r = await api("/api/presse_papiers/liste", { recherche: P.recherche });
    const empreinte = JSON.stringify(r);
    if (!force && empreinte === P.empreinte && racine().childElementCount) return;
    P.r = r; P.empreinte = empreinte;
    dessiner();
  }
  const recharger = (force = true) => charger(force).catch(e => toast("😕 " + e.message, "erreur"));

  // Les nouveaux textes copiés apparaissent tout seuls tant que l'onglet est ouvert.
  setInterval(() => { if (visible()) charger().catch(() => {}); }, 2000);

  function heure(iso) {
    const d = new Date(iso);
    const auj = new Date().toDateString() === d.toDateString();
    return el("div", { class: "pp-heure" }, d.toLocaleTimeString(I18N.locale(), { hour: "2-digit", minute: "2-digit" }),
      auj ? null : el("small", {}, d.toLocaleDateString(I18N.locale(), { day: "2-digit", month: "2-digit" })));
  }

  function dessiner() {
    const r = P.r;
    const ancienne = racine().querySelector(".pp-recherche");
    const avaitFocus = ancienne && document.activeElement === ancienne;
    const recherche = el("input", { class: "pp-recherche", placeholder: "Chercher…", value: P.recherche,
      oninput: e => { P.recherche = e.target.value; clearTimeout(minuterie); minuterie = setTimeout(() => recharger(), 200); } });
    const elements = [...r.elements].sort((a, b) => (b.epingle ? 1 : 0) - (a.epingle ? 1 : 0));
    const libres = r.elements.filter(e => !e.epingle).length;
    // Aucun moyen de lire le presse-papiers (Linux sans wl-clipboard ni xclip) :
    // un message clair à la place de l'historique.
    const indisponible = r.disponible === false;
    const bandeau = indisponible
      ? el("div", { class: "pp-bandeau pause" }, el("span", {}, "⏸"), el("span", {}, r.message || "Le presse-papiers ne répond pas."))
      : el("div", { class: "pp-bandeau" + (r.actif ? "" : " pause") }, el("span", {}, r.actif ? "🔒" : "⏸"),
        el("span", {}, r.actif
          ? "Gardé seulement en mémoire, effacé à la fermeture de Mes outils. Les mots de passe copiés depuis le coffre (et depuis la plupart des gestionnaires de mots de passe) n'y entrent pas."
          : "En pause : les textes copiés ne sont pas gardés."));
    racine().replaceChildren(
      el("div", { class: "barre-vue" },
        el("h2", {}, "📋 " + t("Historique du presse-papiers") + " ",
          el("span", { class: "compte", title: t("{n} / {max} éléments", { n: libres, max: r.limite }) }, String(r.elements.length))),
        el("div", { class: "espace" }),
        el("div", { class: "champ-recherche" }, el("span", {}, "🔎"), recherche),
        el("button", { class: "btn" + (r.actif ? "" : " actif"), onclick: basculerPause, disabled: indisponible ? "" : null },
          r.actif ? "⏸ Pause" : "▶ Reprendre"),
        el("button", { class: "btn", onclick: toutEffacer, disabled: r.elements.length ? null : "" }, "🧹 Tout effacer")),
      bandeau,
      indisponible && !elements.length ? null
        : elements.length ? el("div", { class: "pp-liste" }, elements.map((e, i) => ligne(e, i)))
        : el("div", { class: "vide" }, P.recherche ? "🔍 " + t("Aucun élément ne correspond.")
          : "📋 " + t("Rien pour l'instant : copiez un texte (Ctrl + C), il apparaîtra ici.")));
    if (avaitFocus) { recherche.focus(); recherche.setSelectionRange(recherche.value.length, recherche.value.length); }
  }

  function ligne(e, i) {
    const nombre = new Intl.NumberFormat(I18N.locale()).format(e.longueur);
    return el("div", { class: "carte pp-element" + (e.epingle ? " epingle" : ""), style: `animation-delay:${Math.min(i, 10) * 20}ms` },
      heure(e.quand),
      el("div", { class: "pp-corps", title: "Recopier", onclick: () => recopier(e) },
        el("pre", { class: "pp-apercu" }, e.apercu),
        el("div", { class: "pp-infos" },
          e.epingle ? el("span", {}, "📌 " + t("Épinglé")) : null,
          el("span", {}, t("{n} caractères", { n: nombre })),
          e.lignes > 1 ? el("span", {}, t("{n} lignes", { n: e.lignes })) : null)),
      el("div", { class: "pp-boutons" },
        el("button", { class: "icone-btn", title: "Recopier", onclick: () => recopier(e) }, "📋"),
        el("button", { class: "icone-btn" + (e.epingle ? " actif" : ""), title: e.epingle ? "Désépingler" : "Épingler",
          onclick: () => action("epingler", { id: e.id, epingle: !e.epingle }) }, "📌"),
        el("button", { class: "icone-btn danger", title: "Supprimer", onclick: () => action("supprimer", { id: e.id }) }, "✕")));
  }

  async function action(nom, donnees) {
    try { await api("/api/presse_papiers/" + nom, donnees); recharger(); }
    catch (e) { toast("😕 " + e.message, "erreur"); recharger(); }
  }

  async function recopier(e) {
    try { await api("/api/presse_papiers/recopier", { id: e.id }); toast("📋 Recopié", "succes", 1400); }
    catch (err) { toast("😕 " + err.message, "erreur"); }
    recharger();
  }

  async function basculerPause() {
    await action("pause", { pause: P.r.actif });
  }

  async function toutEffacer() {
    if (!(await confirmer("🧹", "Tout effacer ?", "Les éléments épinglés sont gardés.", "Effacer"))) return;
    await action("vider", {});
  }

  VUES.presse_papiers = { afficher: () => recharger(true), titre: "Presse-papiers", icone: "📋", groupe: "outils", ordre: 30 };
})();
