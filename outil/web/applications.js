"use strict";
/* Applications : le catalogue (activer / désactiver chaque application, comme
   dans un ERP) et l'assistant du premier lancement (prénom, langue, métier,
   applications). Une application désactivée disparaît du menu ; ses données
   restent. Enregistré dans outils.json : apps_actives, profil, assistant_fait. */
(() => {
  I18N.ajouter({
    "Applications": "Apps",
    "Choisissez les applications dont vous vous servez : les autres disparaissent du menu, leurs données restent.":
      "Choose the apps you use: the others leave the menu, their data stays.",
    "Activer et désactiver les applications, comme dans un ERP.": "Turn apps on and off, like in an ERP.",
    "Toutes": "All", "Actives": "On", "Inactives": "Off",
    "Activée": "On", "Activer": "Turn on", "Désactiver": "Turn off",
    "{n} actives": "{n} on", "Repartir d'un métier…": "Start from a role…",
    "Les applications de ce métier remplacent votre sélection actuelle. Vos données ne sont pas touchées.":
      "This role's apps replace your current selection. Your data is not touched.",
    "Appliquer": "Apply", "Application activée": "App turned on", "Application désactivée": "App turned off",
    "Applications mises à jour": "Apps updated",
    "Bienvenue dans Mes outils": "Welcome to Mes outils",
    "Votre tableau de bord de travail, sur ce PC. Trois étapes pour le préparer.":
      "Your work dashboard, on this PC. Three steps to set it up.",
    "Comment vous appelle-t-on ?": "What should we call you?", "Prénom": "First name", "Langue": "Language",
    "Quel est votre métier ?": "What do you do?",
    "Il sert à cocher d'office les applications utiles. Vous pourrez tout changer ensuite.":
      "It pre-selects the useful apps. You can change everything later.",
    "Vos applications": "Your apps",
    "Cochez celles dont vous vous servez. Les autres restent disponibles dans la page Applications.":
      "Tick the ones you use. The others stay available on the Apps page.",
    "Retour": "Back", "Continuer": "Continue", "Commencer": "Get started", "Passer": "Skip",
    "Étape {n} sur 3": "Step {n} of 3", "Tout cocher": "Select all", "Tout décocher": "Clear all",
    "Freelance": "Freelancer", "Clients, devis, factures, temps passé.": "Clients, quotes, invoices, time spent.",
    "Assistant(e) virtuel(le)": "Virtual assistant", "Plusieurs clients, tâches, messages types.": "Several clients, tasks, message templates.",
    "Assistant(e) de direction": "Executive assistant", "Agenda, réunions, déplacements, documents.": "Calendar, meetings, travel, documents.",
    "Développeur": "Developer", "Projets, serveurs, GitHub, outils techniques.": "Projects, servers, GitHub, technical tools.",
    "Je choisis moi-même": "I'll choose myself", "Partir de zéro et cocher ce qui sert.": "Start from scratch and tick what helps.",
    "Clients et ventes": "Clients & sales", "Organisation": "Organisation",
    "Votre métier : {p}": "Your role: {p}",
    "Toujours présentes : Accueil, Applications, Réglages.": "Always there: Home, Apps, Settings.",
  });

  const style = document.createElement("style");
  style.textContent = `
    .ap-groupe { margin: 22px 0 10px; font-size: 13px; font-weight: 600; color: var(--doux); }
    .ap-grille { display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 10px; }
    .ap-carte { display: grid; grid-template-columns: 36px minmax(0, 1fr) auto; gap: 12px; align-items: center;
      background: var(--carte); border: 1px solid var(--ligne); border-radius: var(--rayon); padding: 12px 14px; }
    .ap-carte.off { background: transparent; }
    .ap-carte.off .ap-ic, .ap-carte.off .ap-titre { opacity: .55; }
    .ap-ic { width: 36px; height: 36px; border-radius: 9px; display: grid; place-items: center; background: var(--violet-clair); color: var(--violet); }
    .ap-ic svg.ico { width: 18px; height: 18px; margin: 0; }
    .ap-titre { font-weight: 600; font-size: 14px; }
    .ap-desc { color: var(--doux); font-size: 12.5px; line-height: 1.4; margin-top: 1px; }
    .ap-interrupteur { position: relative; width: 38px; height: 22px; border-radius: 99px; border: 0; cursor: pointer; background: var(--ligne-forte); transition: background .15s; flex: none; }
    .ap-interrupteur::after { content: ""; position: absolute; top: 3px; left: 3px; width: 16px; height: 16px; border-radius: 50%; background: #fff; transition: transform .15s; box-shadow: 0 1px 2px rgba(0,0,0,.25); }
    .ap-interrupteur.on { background: var(--violet); }
    .ap-interrupteur.on::after { transform: translateX(16px); }
    .ap-interrupteur:disabled { opacity: .5; cursor: default; }
    .ap-barre { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
    .ap-barre select { width: auto; }
    .ap-note { color: var(--gris); font-size: 12.5px; margin-top: 18px; }
    /* Assistant du premier lancement */
    .as-voile { position: fixed; inset: 0; z-index: 70; background: var(--fond); display: grid; place-items: center; padding: 24px; overflow: auto; }
    .as-panneau { width: min(760px, 100%); background: var(--carte); border: 1px solid var(--ligne); border-radius: 14px; box-shadow: var(--ombre-forte); padding: 30px 32px 24px; }
    .as-logo { width: 36px; height: 36px; border-radius: 9px; background: var(--violet); color: var(--sur-violet); display: grid; place-items: center; margin-bottom: 16px; }
    .as-logo svg.ico { width: 20px; height: 20px; margin: 0; }
    .as-etape { color: var(--gris); font-size: 12.5px; margin-bottom: 4px; }
    .as-panneau h2 { margin: 0 0 6px; font-size: 22px; letter-spacing: -.02em; }
    .as-panneau > p { color: var(--doux); margin: 0 0 20px; }
    .as-profils { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 10px; }
    .as-profil { text-align: left; border: 1px solid var(--ligne); background: var(--champ); border-radius: 10px; padding: 14px; cursor: pointer; display: grid; gap: 4px; color: var(--encre); }
    .as-profil:hover { border-color: var(--ligne-forte); }
    .as-profil.choisi { border-color: var(--violet); background: var(--violet-clair); }
    .as-profil svg.ico { width: 18px; height: 18px; margin: 0 0 4px; color: var(--violet); }
    .as-profil b { font-weight: 600; }
    .as-profil small { color: var(--doux); font-size: 12.5px; }
    .as-apps { max-height: 46vh; overflow: auto; padding-right: 4px; }
    .as-apps .ap-groupe:first-child { margin-top: 0; }
    .as-app { display: flex; gap: 10px; align-items: flex-start; padding: 7px 4px; border-radius: 8px; cursor: pointer; }
    .as-app:hover { background: var(--surface); }
    .as-app input { margin-top: 3px; width: 16px; height: 16px; flex: none; }
    .as-app .ap-desc { margin-top: 0; }
    .as-pied { display: flex; align-items: center; gap: 8px; margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--ligne); }
    .as-points { display: flex; gap: 6px; flex: 1; }
    .as-points span { width: 7px; height: 7px; border-radius: 50%; background: var(--ligne-forte); }
    .as-points span.actif { background: var(--violet); }
  `;
  document.head.append(style);

  /** Les applications du catalogue (sans Accueil, Applications, Réglages). */
  function catalogue() {
    return listeOnglets().filter(o => !APPS_FIXES.includes(o.nom))
      .sort((a, b) => (Object.keys(GROUPES).indexOf(a.groupe) - Object.keys(GROUPES).indexOf(b.groupe)) || ((a.ordre ?? 99) - (b.ordre ?? 99)));
  }
  /** Les applications cochées d'office pour un métier. */
  function pourProfil(profil) {
    const apps = catalogue();
    if (profil === "personnalise") return apps.filter(o => ["agenda", "notes", "taches", "mails"].includes(o.nom)).map(o => o.nom);
    return apps.filter(o => (o.profils || []).includes(profil)).map(o => o.nom);
  }
  function actives() { return catalogue().filter(o => appActive(o.nom)).map(o => o.nom); }
  async function enregistrer(valeurs) {
    await api("/api/reglages/enregistrer", valeurs);
    if ("apps_actives" in valeurs) S.appsActives = valeurs.apps_actives;
    if ("profil" in valeurs) S.profil = valeurs.profil;
    construireMenu();
  }
  function parGroupe(liste) {
    const groupes = {};
    for (const o of liste) (groupes[o.groupe || "outils"] ||= []).push(o);
    return Object.keys(GROUPES).filter(g => groupes[g]).map(g => [g, groupes[g]]);
  }

  // ---------------------------------------------------------------- catalogue
  const A = { filtre: "toutes" };
  function afficher() {
    const vue = $("#vue-applications");
    const liste = catalogue();
    const on = new Set(actives());
    const visibles = liste.filter(o => A.filtre === "toutes" || (A.filtre === "actives") === on.has(o.nom));
    const choixProfil = el("select", { onchange: async e => {
      const profil = e.target.value;
      e.target.value = "";
      if (!profil || !(await confirmer("", t(PROFILS[profil].titre), "Les applications de ce métier remplacent votre sélection actuelle. Vos données ne sont pas touchées.", "Appliquer"))) return;
      try { await enregistrer({ apps_actives: pourProfil(profil), profil }); toast("Applications mises à jour", "succes"); afficher(); }
      catch (err) { toast(err.message, "erreur"); }
    } }, el("option", { value: "" }, "Repartir d'un métier…"),
      ...Object.entries(PROFILS).map(([cle, p]) => el("option", { value: cle }, t(p.titre))));
    vue.replaceChildren(
      el("div", { class: "barre-vue" },
        el("h2", {}, icone("layout-grid", "av"), t("Applications"), el("span", { class: "compte" }, t("{n} actives", { n: on.size }))),
        el("span", { class: "espace" }),
        el("div", { class: "ap-barre" },
          el("div", { class: "puces" }, [["toutes", "Toutes"], ["actives", "Actives"], ["inactives", "Inactives"]].map(([cle, lib]) =>
            el("button", { class: "puce" + (A.filtre === cle ? " actif" : ""), onclick: () => { A.filtre = cle; afficher(); } }, lib))),
          choixProfil)),
      el("p", { style: "color:var(--doux);margin:-6px 0 0" }, "Choisissez les applications dont vous vous servez : les autres disparaissent du menu, leurs données restent."),
      ...parGroupe(visibles).flatMap(([g, apps]) => [
        el("div", { class: "ap-groupe" }, GROUPES[g]),
        el("div", { class: "ap-grille" }, apps.map(o => carte(o, on.has(o.nom)))),
      ]),
      el("p", { class: "ap-note" }, "Toujours présentes : Accueil, Applications, Réglages."));
  }
  function carte(o, actif) {
    const bouton = el("button", { class: "ap-interrupteur" + (actif ? " on" : ""), role: "switch", "aria-checked": String(actif),
      title: actif ? "Désactiver" : "Activer", onclick: async () => {
        const liste = new Set(actives());
        actif ? liste.delete(o.nom) : liste.add(o.nom);
        bouton.disabled = true;
        try { await enregistrer({ apps_actives: [...liste] }); toast(actif ? "Application désactivée" : "Application activée", "succes", 1400); afficher(); }
        catch (e) { toast(e.message, "erreur"); bouton.disabled = false; }
      } });
    return el("div", { class: "ap-carte" + (actif ? "" : " off") },
      el("div", { class: "ap-ic" }, iconeOnglet(o.icone)),
      el("div", {}, el("div", { class: "ap-titre" }, I18N.traduire(o.titre)), el("div", { class: "ap-desc" }, o.description || "")),
      bouton);
  }

  // ------------------------------------------------- assistant de démarrage
  const W = { etape: 1, prenom: "", profil: "", apps: null };
  function assistantDemarrage() {
    W.prenom = S.config?.prenom || "";
    let voile = $("#assistant-demarrage");
    if (!voile) { voile = el("div", { class: "as-voile", id: "assistant-demarrage" }); document.body.append(voile); }
    dessinerAssistant();
  }
  function dessinerAssistant() {
    const voile = $("#assistant-demarrage");
    const contenu = [];
    if (W.etape === 1) {
      const champ = el("input", { value: W.prenom, placeholder: "Prénom", maxlength: 40, oninput: e => (W.prenom = e.target.value) });
      setTimeout(() => champ.focus(), 50);
      contenu.push(
        el("div", { class: "as-logo" }, icone("layout-grid")),
        el("div", { class: "as-etape" }, t("Étape {n} sur 3", { n: 1 })),
        el("h2", {}, "Bienvenue dans Mes outils"),
        el("p", {}, "Votre tableau de bord de travail, sur ce PC. Trois étapes pour le préparer."),
        el("label", { class: "champ" }, "Comment vous appelle-t-on ?", champ),
        el("label", { class: "champ" }, "Langue", el("div", { style: "display:flex;gap:8px" },
          [["fr", "Français"], ["en", "English"]].map(([code, nom]) => el("button", { class: "btn" + (I18N.langue === code ? " actif" : ""), onclick: async () => {
            if (code === I18N.langue) return;
            await api("/api/reglages/enregistrer", { langue: code, prenom: W.prenom });
            location.reload();
          } }, nom)))));
    } else if (W.etape === 2) {
      contenu.push(
        el("div", { class: "as-etape" }, t("Étape {n} sur 3", { n: 2 })),
        el("h2", {}, "Quel est votre métier ?"),
        el("p", {}, "Il sert à cocher d'office les applications utiles. Vous pourrez tout changer ensuite."),
        el("div", { class: "as-profils" }, Object.entries(PROFILS).map(([cle, p]) =>
          el("button", { class: "as-profil" + (W.profil === cle ? " choisi" : ""), onclick: () => { W.profil = cle; W.apps = pourProfil(cle); W.etape = 3; dessinerAssistant(); } },
            icone(p.icone), el("b", {}, t(p.titre)), el("small", {}, t(p.detail))))));
    } else {
      const choisies = new Set(W.apps || []);
      contenu.push(
        el("div", { class: "as-etape" }, t("Étape {n} sur 3", { n: 3 })),
        el("h2", {}, "Vos applications"),
        el("p", {}, "Cochez celles dont vous vous servez. Les autres restent disponibles dans la page Applications."),
        el("div", { style: "display:flex;gap:6px;margin:-8px 0 12px" },
          el("button", { class: "btn petit", onclick: () => { W.apps = catalogue().map(o => o.nom); dessinerAssistant(); } }, "Tout cocher"),
          el("button", { class: "btn petit", onclick: () => { W.apps = []; dessinerAssistant(); } }, "Tout décocher")),
        el("div", { class: "as-apps" }, parGroupe(catalogue()).flatMap(([g, apps]) => [
          el("div", { class: "ap-groupe" }, GROUPES[g]),
          ...apps.map(o => el("label", { class: "as-app" },
            el("input", { type: "checkbox", checked: choisies.has(o.nom) ? "" : null, onchange: e => {
              e.target.checked ? choisies.add(o.nom) : choisies.delete(o.nom); W.apps = [...choisies];
            } }),
            el("div", {}, el("div", { class: "ap-titre" }, iconeOnglet(o.icone), " " + I18N.traduire(o.titre)), el("div", { class: "ap-desc" }, o.description || "")))),
        ])));
    }
    const points = el("div", { class: "as-points" }, [1, 2, 3].map(n => el("span", { class: n === W.etape ? "actif" : "" })));
    const pied = el("div", { class: "as-pied" }, points,
      W.etape > 1 ? el("button", { class: "btn discret", onclick: () => { W.etape -= 1; dessinerAssistant(); } }, "Retour")
        : el("button", { class: "btn discret", onclick: () => terminer(true) }, "Passer"),
      W.etape === 1 ? el("button", { class: "btn principal", onclick: () => { W.etape = 2; dessinerAssistant(); } }, "Continuer")
        : W.etape === 2 ? null
        : el("button", { class: "btn principal", onclick: () => terminer(false) }, "Commencer"));
    voile.replaceChildren(el("div", { class: "as-panneau" }, ...contenu, pied));
  }
  async function terminer(passer) {
    const valeurs = { prenom: W.prenom.trim(), assistant_fait: true };
    if (!passer) Object.assign(valeurs, { profil: W.profil || "personnalise", apps_actives: W.apps || [] });
    try {
      await enregistrer(valeurs);
      if (S.config) S.config.prenom = valeurs.prenom;
      horloge();
      $("#assistant-demarrage")?.remove();
      montrerVue("accueil");
    } catch (e) { toast(e.message, "erreur"); }
  }

  window.assistantDemarrage = assistantDemarrage;
  VUES.applications = {
    afficher, titre: "Applications", icone: icone("layout-grid"), groupe: "systeme", ordre: 80,
    description: "Activer et désactiver les applications, comme dans un ERP.",
  };
})();
