"use strict";
/* Onglet « Notes » : notes en cartes, listes à cocher, épingles, rappels.
   Enregistrement automatique pendant la frappe (donnees/notes.json). */
(() => {
  I18N.ajouter({
    "Notes": "Notes",
    "Mes notes": "My notes",
    "Toutes": "All",
    "Listes": "Lists",
    "Avec rappel": "With reminder",
    "Chercher dans les notes…": "Search notes…",
    "＋ Note": "＋ Note",
    "☑️ Liste": "☑️ List",
    "Aucune note ne correspond.": "No matching note.",
    "Pas encore de note. Une idée ? Notez-la ! ✍️": "No notes yet. Got an idea? Write it down! ✍️",
    "+ {n} autres": "+ {n} more",
    "Épinglée": "Pinned",
    "Enregistré": "Saved",
    "✓ Enregistré": "✓ Saved",
    "Écrivez ici…": "Write here…",
    "Élément…": "Item…",
    "Retirer": "Remove",
    "＋ Ajouter un élément": "＋ Add an item",
    "Couleur": "Colour",
    "Épingler en haut et sur l'accueil": "Pin to the top and to the home page",
    "Rappel par la bulle": "Reminder from the bubble",
    "Rappel": "Reminder",
    "Passer en liste à cocher / en texte": "Switch to checklist / text",
    "📄 En texte": "📄 As text",
    "☑️ En liste": "☑️ As list",
    "Titre": "Title",
    "Supprimer cette note ?": "Delete this note?",
    "Elle disparaît définitivement.": "It is removed for good.",
    "Supprimer": "Delete",
    "🗑 Supprimer": "🗑 Delete",
    "🗑️ Note supprimée": "🗑️ Note deleted",
    "Terminé": "Done",
  });

  const COULEURS_NOTE = ["#ffffff", "#fff4c2", "#ffe1d6", "#dcf7f0", "#e6f0ff", "#efeaff", "#fde2ef", "#e9ecef"];
  const ACCENTS = { "#ffffff": "#a7a3bd", "#fff4c2": "#ffb020", "#ffe1d6": "#ff7a59", "#dcf7f0": "#18b597", "#e6f0ff": "#2f8cff", "#efeaff": "#6c4cf5", "#fde2ef": "#e5488d", "#e9ecef": "#475569" };
  const N = { notes: [], recherche: "", filtre: "toutes", timer: null };

  const style = document.createElement("style");
  style.textContent = `
    .notes-grille { columns: 4 240px; column-gap: 16px; }
    .note { background: var(--note, #fff); break-inside: avoid; margin: 0 0 16px; border-radius: var(--rayon); padding: 14px 16px 12px; box-shadow: var(--ombre);
            cursor: pointer; position: relative; transition: transform .2s, box-shadow .2s; animation: apparait .35s both; border: 1.5px solid rgba(0,0,0,.04); color: #1f1a3a; color-scheme: light; }
    .note:hover { transform: none; }
    .note .titre { font-weight: 600; font-size: 15.5px; margin: 0 22px 6px 0; word-break: break-word; }
    .note .texte { white-space: pre-wrap; font-size: 14px; color: #3b3657; line-height: 1.45; max-height: 230px; overflow: hidden; word-break: break-word; }
    .note .epingle { position: absolute; top: 10px; right: 10px; font-size: 15px; }
    .note .bas { display: flex; gap: 6px; margin-top: 10px; flex-wrap: wrap; align-items: center; }
    .chip { font-size: 11.5px; font-weight: 700; border-radius: 99px; padding: 2px 9px; background: rgba(255,255,255,.75); color: #6b6790; }
    .chip.passe { color: #a7a3bd; text-decoration: line-through; }
    .coche { display: flex; gap: 8px; align-items: flex-start; font-size: 14px; padding: 2px 0; }
    .coche input { margin-top: 3px; accent-color: var(--menthe); width: 16px; height: 16px; flex: none; cursor: pointer; }
    .coche.fait span { text-decoration: line-through; color: #a7a3bd; }
    .notes-vide { text-align: center; padding: 50px 20px; color: var(--doux); }
    .notes-vide div { font-size: 60px;  }
    @keyframes flotte { 50% { transform: none; } }
    .editeur-note { border-radius: var(--rayon); padding: 6px 4px; color: #1f1a3a; color-scheme: light; }
    /* Posés sur la couleur de la note (claire, choisie par l'utilisateur) : texte
       sombre et fond transparent, même en thème sombre (!important : le style
       commun des champs de hub.html est plus précis). */
    .editeur-note input.titre-note, .editeur-note textarea.texte-note, .liste-edition .element input[type=text] {
      background: transparent !important; border-color: transparent !important; box-shadow: none !important; color: #1f1a3a !important; padding-left: 2px !important; }
    .editeur-note .liste-edition .element input[type=text]:focus { border-bottom-color: #6c4cf5 !important; }
    .editeur-note input::placeholder, .editeur-note textarea::placeholder { color: #8d89a8 !important; }
    .editeur-note input.titre-note { width: 100%; border: 0; background: transparent; font-size: 20px; font-weight: 600; outline: none; margin-bottom: 8px; }
    .editeur-note textarea.texte-note { width: 100%; border: 0; background: transparent; outline: none; resize: vertical; min-height: 170px; font-size: 15px; line-height: 1.5; }
    .liste-edition .element { display: flex; gap: 8px; align-items: center; padding: 3px 0; }
    .liste-edition .element input[type=text] { flex: 1; border: 0; border-bottom: 1.5px dashed transparent; background: transparent; outline: none; font-size: 15px; padding: 4px 0; }
    .liste-edition .element input[type=text]:focus { border-bottom-color: var(--violet); }
    .liste-edition .element.fait input[type=text] { text-decoration: line-through; color: #a7a3bd; }
    .liste-edition .element button { border: 0; background: transparent; cursor: pointer; opacity: .45; font-size: 14px; }
    .liste-edition .element button:hover { opacity: 1; }
    .outils-note { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; border-top: 1px solid rgba(0,0,0,.06); padding-top: 12px; margin-top: 10px; }
    .outils-note .pastilles-c { display: flex; gap: 6px; }
    .outils-note .pastilles-c button { width: 24px; height: 24px; border-radius: 50%; border: 2px solid #fff; box-shadow: 0 0 0 1.5px #d9d5ea; cursor: pointer; }
    .outils-note .pastilles-c button.choisi { box-shadow: 0 0 0 2.5px var(--encre); }
    .outils-note input[type=datetime-local] { border: 1.5px solid #e7e3fb !important; border-radius: 10px !important; padding: 5px 8px !important; background: #fff !important; color: #1f1a3a !important; color-scheme: light; }
    .editeur-note .outils-note .btn.discret { color: #6b6790; }
    .sauve { font-size: 12px; color: #6b6790; margin-left: auto; }
  
    /* L'éditeur prend la couleur de la note. */
    .fenetre:has(.editeur-note) { background: var(--note, var(--carte)); }
    /* Mode nuit : la couleur de la note devient une teinte sombre, texte clair. */
    :root[data-theme="sombre"] .note { background: color-mix(in srgb, var(--note, #fff) 13%, var(--carte)); color: var(--encre); color-scheme: dark; border-color: var(--ligne); }
    :root[data-theme="sombre"] .note .texte { color: var(--doux); }
    :root[data-theme="sombre"] .note .chip { background: rgba(255,255,255,.07); color: var(--doux); }
    :root[data-theme="sombre"] .fenetre:has(.editeur-note) { background: color-mix(in srgb, var(--note, #fff) 13%, var(--carte)); }
    :root[data-theme="sombre"] .editeur-note { color: var(--encre); color-scheme: dark; }
    :root[data-theme="sombre"] .editeur-note input, :root[data-theme="sombre"] .editeur-note textarea,
    :root[data-theme="sombre"] .editeur-note .liste-edition .element input[type=text] { color: var(--encre) !important; }
    :root[data-theme="sombre"] .editeur-note input::placeholder, :root[data-theme="sombre"] .editeur-note textarea::placeholder { color: var(--gris) !important; }
    :root[data-theme="sombre"] .outils-note input[type=datetime-local] { background: var(--champ) !important; color: var(--encre) !important; border-color: var(--ligne) !important; color-scheme: dark; }
  `;
  document.head.append(style);

  const racine = () => $("#vue-notes");
  // Données de l'utilisateur (titres, textes) : jamais traduites.
  const brut = s => document.createTextNode(s ?? "");

  function rappelTexte(n) {
    if (!n.rappel) return null;
    const d = new Date(n.rappel);
    const passe = d < new Date();
    return el("span", { class: "chip" + (passe && n.rappel_fait ? " passe" : "") },
      "⏰ " + d.toLocaleString(I18N.locale(), { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }));
  }

  async function charger() {
    N.notes = await api("/api/notes");
    dessiner();
  }

  function filtrees() {
    const q = N.recherche.toLowerCase();
    return N.notes
      .filter(n => N.filtre === "toutes" || (N.filtre === "listes" ? n.genre === "liste" : N.filtre === "rappels" ? n.rappel : true))
      .filter(n => !q || [n.titre, n.texte, ...(n.elements || []).map(e => e.texte)].join(" ").toLowerCase().includes(q))
      .sort((a, b) => (b.epinglee ? 1 : 0) - (a.epinglee ? 1 : 0) || (b.modifie || "").localeCompare(a.modifie || ""));
  }

  function carte(n, i) {
    const fond = n.couleur || "#ffffff";
    const corps = n.genre === "liste"
      ? el("div", {}, (n.elements || []).slice(0, 8).map((e, j) => el("label", { class: "coche" + (e.fait ? " fait" : ""), onclick: ev => ev.stopPropagation() },
          el("input", { type: "checkbox", checked: e.fait ? "" : null, onchange: async ev => {
            n.elements[j].fait = ev.target.checked; await sauver(n); dessiner();
          } }), el("span", {}, brut(e.texte)))),
          (n.elements || []).length > 8 ? el("div", { class: "chip" }, t("+ {n} autres", { n: n.elements.length - 8 })) : null)
      : el("div", { class: "texte" }, brut(n.texte));
    const faits = (n.elements || []).filter(e => e.fait).length;
    return el("div", { class: "note", style: `--note:${fond}`, onclick: () => editer(n) },
      n.epinglee ? el("span", { class: "epingle", title: "Épinglée" }, "📌") : null,
      n.titre ? el("div", { class: "titre" }, brut(n.titre)) : null,
      corps,
      el("div", { class: "bas" },
        n.genre === "liste" && n.elements?.length ? el("span", { class: "chip" }, `✅ ${faits}/${n.elements.length}`) : null,
        rappelTexte(n)));
  }

  function dessiner() {
    const r = racine();
    const liste = filtrees();
    const recherche = el("input", { placeholder: "Chercher dans les notes…", value: N.recherche,
      oninput: e => { N.recherche = e.target.value; dessinerGrille(); } });
    r.replaceChildren(
      el("div", { class: "barre-vue" },
        el("h2", {}, "📝 " + t("Mes notes") + " ", el("span", { class: "compte" }, String(N.notes.length))),
        el("div", { class: "puces" }, [["toutes", "Toutes"], ["listes", "Listes"], ["rappels", "Avec rappel"]].map(([v, libelle]) =>
          el("button", { class: "puce" + (N.filtre === v ? " actif" : ""), onclick: () => { N.filtre = v; dessiner(); } }, libelle))),
        el("div", { class: "espace" }),
        el("div", { class: "champ-recherche" }, el("span", {}, "🔎"), recherche),
        el("button", { class: "btn principal", onclick: () => nouvelle("texte") }, "＋ Note"),
        el("button", { class: "btn", onclick: () => nouvelle("liste") }, "☑️ Liste")),
      el("div", { id: "grille-notes" }));
    dessinerGrille(liste);
  }

  function dessinerGrille(liste = filtrees()) {
    const g = $("#grille-notes");
    if (!g) return;
    if (!liste.length) {
      g.replaceChildren(el("div", { class: "notes-vide" }, el("div", {}, N.notes.length ? "🔍" : "🗒️"),
        N.notes.length ? "Aucune note ne correspond." : "Pas encore de note. Une idée ? Notez-la ! ✍️"));
      return;
    }
    g.replaceChildren(el("div", { class: "notes-grille" }, liste.map(carte)));
  }

  async function sauver(n) {
    const enregistree = await api("/api/notes/enregistrer", { element: n });
    Object.assign(n, enregistree);
    const i = N.notes.findIndex(x => x.id === n.id);
    if (i >= 0) N.notes[i] = n; else N.notes.push(n);
    return n;
  }

  function nouvelle(genre) {
    editer({ genre, titre: "", texte: "", elements: genre === "liste" ? [{ texte: "", fait: false }] : [], couleur: genre === "liste" ? "#dcf7f0" : "#fff4c2" }, true);
  }

  function editer(note, nouvelleNote = false) {
    const n = structuredClone(note);
    const etat = el("span", { class: "sauve" }, nouvelleNote ? "" : "Enregistré");
    let timer = null;
    const planifier = () => {
      etat.textContent = "…";
      clearTimeout(timer);
      timer = setTimeout(async () => {
        if (!n.titre && !n.texte && !(n.elements || []).some(e => e.texte)) { etat.textContent = ""; return; }
        try { await sauver(n); etat.textContent = t("✓ Enregistré"); } catch (e) { etat.textContent = "⚠️ " + e.message; }
      }, 500);
    };
    const boite = el("div", { class: "editeur-note" });
    const fenetreNote = () => $("#fenetre");

    const zoneCorps = el("div");
    const dessinerCorps = () => {
      if (n.genre !== "liste") {
        const zone = el("textarea", { class: "texte-note", placeholder: "Écrivez ici…", value: n.texte || "", oninput: e => { n.texte = e.target.value; planifier(); } });
        zoneCorps.replaceChildren(zone);
        return;
      }
      const liste = el("div", { class: "liste-edition" });
      (n.elements || []).forEach((e, i) => {
        const champ = el("input", { type: "text", value: e.texte, placeholder: "Élément…",
          oninput: ev => { e.texte = ev.target.value; planifier(); },
          onkeydown: ev => {
            if (ev.key === "Enter") { ev.preventDefault(); n.elements.splice(i + 1, 0, { texte: "", fait: false }); dessinerCorps(); planifier(); setTimeout(() => zoneCorps.querySelectorAll("input[type=text]")[i + 1]?.focus(), 10); }
            if (ev.key === "Backspace" && !e.texte && n.elements.length > 1) { ev.preventDefault(); n.elements.splice(i, 1); dessinerCorps(); planifier(); setTimeout(() => zoneCorps.querySelectorAll("input[type=text]")[Math.max(0, i - 1)]?.focus(), 10); }
          } });
        liste.append(el("div", { class: "element" + (e.fait ? " fait" : "") },
          el("input", { type: "checkbox", tabindex: "-1", checked: e.fait ? "" : null, style: "accent-color:var(--menthe);width:17px;height:17px",
            onchange: ev => { e.fait = ev.target.checked; dessinerCorps(); planifier(); } }),
          champ,
          el("button", { title: "Retirer", tabindex: "-1", onclick: () => { n.elements.splice(i, 1); if (!n.elements.length) n.elements.push({ texte: "", fait: false }); dessinerCorps(); planifier(); } }, "✕")));
      });
      liste.append(el("button", { class: "btn discret", onclick: () => { n.elements.push({ texte: "", fait: false }); dessinerCorps(); setTimeout(() => [...zoneCorps.querySelectorAll("input[type=text]")].at(-1)?.focus(), 10); } }, "＋ Ajouter un élément"));
      zoneCorps.replaceChildren(liste);
    };

    const pastilles = el("div", { class: "pastilles-c" }, COULEURS_NOTE.map(c => el("button", { style: `background:${c}`, class: (n.couleur || "#ffffff") === c ? "choisi" : "", title: "Couleur",
      onclick: ev => { n.couleur = c; fenetreNote().style.setProperty("--note", c); [...pastilles.children].forEach(b => b.classList.toggle("choisi", b === ev.currentTarget)); planifier(); } })));
    const epingle = el("button", { class: "btn" + (n.epinglee ? " actif" : ""), title: "Épingler en haut et sur l'accueil",
      onclick: ev => { n.epinglee = !n.epinglee; ev.currentTarget.classList.toggle("actif", n.epinglee); planifier(); } }, "📌");
    const rappel = el("input", { type: "datetime-local", value: n.rappel || "", title: "Rappel par la bulle",
      onchange: ev => { n.rappel = ev.target.value || null; n.rappel_fait = false; planifier(); } });
    const genre = el("button", { class: "btn discret", title: "Passer en liste à cocher / en texte", onclick: () => {
      if (n.genre === "liste") { n.texte = (n.elements || []).map(e => (e.fait ? "✓ " : "") + e.texte).filter(Boolean).join("\n"); n.genre = "texte"; }
      else { n.elements = (n.texte || "").split("\n").filter(l => l.trim()).map(l => ({ texte: l.replace(/^[-•*✓]\s*/, ""), fait: l.startsWith("✓") })); if (!n.elements.length) n.elements = [{ texte: "", fait: false }]; n.genre = "liste"; }
      dessinerCorps(); planifier();
    } }, n.genre === "liste" ? "📄 En texte" : "☑️ En liste");

    boite.append(
      el("input", { class: "titre-note", placeholder: "Titre", value: n.titre || "", oninput: e => { n.titre = e.target.value; planifier(); },
        // Entrée ou Tab dans le titre : on passe au texte, ou au 1er élément de la liste.
        onkeydown: e => { if (e.key === "Enter" || (e.key === "Tab" && !e.shiftKey)) { e.preventDefault(); zoneCorps.querySelector("textarea, input[type=text]")?.focus(); } } }),
      zoneCorps,
      el("div", { class: "outils-note" }, pastilles, epingle, el("span", { title: "Rappel" }, "⏰"), rappel, genre, etat),
      el("div", { class: "actions" },
        !nouvelleNote || n.id ? el("button", { class: "btn discret", style: "margin-right:auto;color:var(--rouge)", onclick: async () => {
          if (!n.id) { fermer(); return; }
          if (!(await confirmer("🗑️", "Supprimer cette note ?", "Elle disparaît définitivement.", "Supprimer"))) { editer(n); return; }
          await api("/api/notes/supprimer", { id: n.id });
          N.notes = N.notes.filter(x => x.id !== n.id);
          dessiner(); toast("🗑️ Note supprimée");
        } }, "🗑 Supprimer") : null,
        el("button", { class: "btn principal", onclick: async () => {
          clearTimeout(timer);
          if (n.titre || n.texte || (n.elements || []).some(e => e.texte)) {
            if (n.genre === "liste") n.elements = n.elements.filter(e => e.texte.trim());
            await sauver(n);
          }
          fermer(); dessiner();
        } }, "Terminé")));
    dessinerCorps();
    fenetre([boite]);
    fenetreNote().style.setProperty("--note", n.couleur || "#ffffff");
    setTimeout(() => (n.titre ? zoneCorps.querySelector("textarea, input") : boite.querySelector(".titre-note"))?.focus(), 60);
    // La fenêtre se ferme aussi par Échap ou un clic à côté : on redessine
    // pour montrer la note telle qu'elle a été enregistrée.
    const observateur = new MutationObserver(() => {
      if (!$("#voile").classList.contains("visible")) { fenetreNote().style.background = ""; observateur.disconnect(); dessiner(); }
    });
    observateur.observe($("#voile"), { attributes: true, attributeFilter: ["class"] });
  }

  VUES.notes = { afficher: () => charger().catch(e => toast("😕 " + e.message, "erreur")), nouvelle,
    titre: "Notes", icone: "📝", groupe: "quotidien", ordre: 20 };
})();
