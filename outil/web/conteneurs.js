"use strict";
/* Onglet « Docker » : les conteneurs de ce PC groupés par projet compose,
   démarrer / arrêter / redémarrer / supprimer, journal, images et place
   occupée (voir conteneurs.py). */
(() => {
  I18N.ajouter({
    "Docker": "Docker",
    "Conteneurs": "Containers",
    "Docker n'est pas installé": "Docker is not installed",
    "Docker sert à faire tourner des bases de données et des applis dans des conteneurs, sans rien installer d'autre sur ce PC.":
      "Docker runs databases and apps in containers, without installing anything else on this PC.",
    "Télécharger Docker Desktop": "Download Docker Desktop",
    "Docker Desktop n'est pas démarré": "Docker Desktop is not running",
    "Démarrez-le pour voir vos conteneurs. Le premier démarrage peut prendre une minute.":
      "Start it to see your containers. The first start can take a minute.",
    "Lancez Docker Desktop depuis le menu Démarrer, puis réessayez.": "Start Docker Desktop from the Start menu, then try again.",
    "Démarrez Docker (sudo systemctl start docker) ou Docker Desktop, puis réessayez.": "Start Docker (sudo systemctl start docker) or Docker Desktop, then try again.",
    "Démarrer Docker Desktop": "Start Docker Desktop",
    "Réessayer": "Try again",
    "Docker Desktop démarre…": "Docker Desktop is starting…",
    "Docker est prêt": "Docker is ready",
    "Docker Desktop met du temps à démarrer : réessayez dans un instant.": "Docker Desktop is slow to start: try again in a moment.",
    "Lecture des conteneurs…": "Reading containers…",
    "Rechercher un conteneur…": "Search a container…",
    "Images et espace disque": "Images and disk space",
    "Actualiser": "Refresh",
    "Aucun conteneur sur ce PC pour l'instant.": "No containers on this PC yet.",
    "Aucun conteneur ne correspond.": "No container matches.",
    "Sans projet": "No project",
    "{n} en marche sur {total}": "{n} running out of {total}",
    "Tout démarrer": "Start all",
    "Tout arrêter": "Stop all",
    "Démarrer": "Start",
    "Arrêter": "Stop",
    "Redémarrer": "Restart",
    "Journal": "Log",
    "Supprimer": "Delete",
    "Supprimer ce conteneur ?": "Delete this container?",
    "Le conteneur est retiré. Ses volumes et son image restent sur ce PC.": "The container is removed. Its volumes and image stay on this PC.",
    "Arrêter ce conteneur ?": "Stop this container?",
    "Arrêter tout le projet ?": "Stop the whole project?",
    "Tous les conteneurs de « {projet} » seront arrêtés.": "All containers of « {projet} » will be stopped.",
    "Le service qu'il fait tourner ne répondra plus.": "The service it runs will stop responding.",
    "Arrêtez d'abord le conteneur": "Stop the container first",
    "Ouvrir dans le navigateur": "Open in browser",
    "Conteneur démarré": "Container started",
    "Conteneur arrêté": "Container stopped",
    "Conteneur redémarré": "Container restarted",
    "Conteneur supprimé": "Container deleted",
    "Projet démarré": "Project started",
    "Projet arrêté": "Project stopped",
    "Journal de {nom}": "Logs of {nom}",
    "300 dernières lignes": "Last 300 lines",
    "Journal vide.": "Empty log.",
    "Copier": "Copy",
    "Fermer": "Close",
    "Lecture…": "Loading…",
    "Images": "Images",
    "Espace occupé": "Disk usage",
    "Aucune image.": "No images.",
    "Type": "Type",
    "Nombre": "Count",
    "Actifs": "Active",
    "Taille": "Size",
    "Récupérable": "Reclaimable",
    "Image": "Image",
    "Tag": "Tag",
    "Créée": "Created",
    "Docker n'est pas installé.": "Docker is not installed.",
    "Docker Desktop n'est pas démarré.": "Docker Desktop is not running.",
    "Docker Desktop est introuvable sur ce PC.": "Docker Desktop was not found on this PC.",
    "Docker ne répond pas (délai dépassé).": "Docker is not responding (timeout).",
    "Identifiant de conteneur invalide.": "Invalid container identifier.",
    "Nom de projet invalide.": "Invalid project name.",
    "Arrêtez d'abord le conteneur.": "Stop the container first.",
    "Aucun conteneur dans ce projet.": "No containers in this project.",
    "Numéro de port invalide.": "Invalid port number.",
  });
  I18N.motifs([[/^Docker : (.*)$/, "Docker: $1"]]);

  const D = { donnees: null, recherche: "", attente: false };
  const racine = () => $("#vue-conteneurs");

  const style = document.createElement("style");
  style.textContent = `
    .dk-ecran { background: var(--carte); border-radius: var(--rayon); box-shadow: var(--ombre); padding: 34px 26px; text-align: center; max-width: 620px; margin: 10px auto; }
    .dk-ecran .gros { font-size: 56px; }
    .dk-ecran h3 { margin: 8px 0; font-size: 21px; color: var(--encre); }
    .dk-ecran p { color: var(--doux); margin: 0 0 18px; }
    .dk-ecran .boutons { display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; }
    .dk-version { font-size: 12px; font-weight: 700; color: var(--doux); }
    .dk-groupes { display: flex; flex-direction: column; gap: 14px; }
    .dk-groupe { background: var(--carte); border-radius: var(--rayon); box-shadow: var(--ombre); padding: 12px 14px; animation: apparait .3s both; }
    .dk-tete { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 6px; }
    .dk-tete .titre { font-weight: 600; font-size: 15.5px; color: var(--encre); }
    .dk-tete .compte-dk { font-size: 12.5px; color: var(--doux); font-weight: 600; }
    .dk-tete .espace { flex: 1; }
    .dk-tete .btn { padding: 6px 12px; font-size: 13px; }
    .dk-ligne { display: flex; align-items: center; gap: 12px; padding: 9px 8px; border-radius: 14px; flex-wrap: wrap; }
    .dk-ligne:hover { background: var(--surface); }
    .dk-ligne + .dk-ligne { border-top: 1px solid var(--ligne); }
    .dk-infos { flex: 1; min-width: 220px; }
    .dk-nom { font-weight: 750; color: var(--encre); display: flex; gap: 8px; align-items: center; }
    .dk-sous { font-size: 12.5px; color: var(--doux); display: flex; gap: 10px; flex-wrap: wrap; margin-top: 2px; }
    .dk-image { font-family: var(--mono); font-size: 12px; }
    .dk-ports { display: flex; gap: 5px; flex-wrap: wrap; }
    .dk-port { border: 0; border-radius: 99px; padding: 2px 9px; font-size: 12px; font-weight: 700; font-family: var(--mono);
      background: var(--surface); color: var(--doux); }
    button.dk-port { background: var(--bleu-clair); color: var(--bleu-texte); cursor: pointer; }
    button.dk-port:hover { background: var(--violet-clair); color: var(--violet); }
    .dk-actions { display: flex; gap: 4px; }
    .dk-etat { font-size: 11.5px; font-weight: 700; border-radius: 99px; padding: 1px 8px; }
    .dk-etat.running { background: var(--vert-clair); color: var(--vert-texte); }
    .dk-etat.exited, .dk-etat.dead { background: var(--surface); color: var(--doux); }
    .dk-etat.paused, .dk-etat.restarting, .dk-etat.created { background: var(--ambre-clair); color: var(--ambre-texte); }
    .dk-journal { background: var(--code); color: var(--code-texte); font-family: var(--mono); font-size: 12px; line-height: 1.45;
      border-radius: 14px; padding: 12px 14px; max-height: 62vh; overflow: auto; white-space: pre-wrap; word-break: break-all; margin: 0; text-align: left; }
    .dk-table { width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 16px; }
    .dk-table th { text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: .7px; color: var(--gris); padding: 6px 8px; }
    .dk-table td { padding: 6px 8px; border-top: 1px solid var(--ligne); color: var(--encre); }
    .dk-table td.mono { font-family: var(--mono); font-size: 12px; }
    .dk-fenetre h4 { margin: 4px 0 8px; color: var(--doux); font-size: 13px; text-transform: uppercase; letter-spacing: .8px; }
  `;
  document.head.append(style);

  // -- statut de docker en français (« Up 2 hours » → « En marche depuis 2 heures ») --
  const UNITES = { second: "seconde", minute: "minute", hour: "heure", day: "jour", week: "semaine", month: "mois", year: "an" };
  function dureeFr(texte) {
    return texte
      .replace(/^Less than a second$/i, "moins d'une seconde")
      .replace(/^About an? (\w+)$/i, (_, u) => "environ une " + (UNITES[u.toLowerCase()] || u))
      .replace(/^An? (\w+)$/i, (_, u) => "une " + (UNITES[u.toLowerCase()] || u))
      .replace(/^(\d+) (\w+?)s?$/i, (_, n, u) => {
        const fr = UNITES[u.toLowerCase()] || u;
        return `${n} ${fr}${Number(n) > 1 && !fr.endsWith("s") ? "s" : ""}`;
      })
      .replace(/^environ une (jour|mois|an)$/, "environ un $1").replace(/^une (jour|mois|an)$/, "un $1");
  }
  function statut(s) {
    if (I18N.langue !== "fr" || !s) return s;
    let m = s.match(/^Up (.+?)(?: \((healthy|unhealthy|Paused|health: starting)\))?$/);
    if (m) {
      const sante = { healthy: " (en bonne santé)", unhealthy: " (en mauvaise santé)", Paused: " (en pause)", "health: starting": " (vérification…)" };
      return "En marche depuis " + dureeFr(m[1]) + (m[2] ? sante[m[2]] : "");
    }
    m = s.match(/^Exited \((-?\d+)\) (.+) ago$/);
    if (m) return `Arrêté (code ${m[1]}) il y a ${dureeFr(m[2])}`;
    if (s === "Created") return "Créé";
    if (/^Restarting/.test(s)) return "Redémarre…";
    return s;
  }

  // -- affichage -----------------------------------------------------------------
  async function afficher() {
    if (!D.donnees) racine().replaceChildren(el("div", { class: "vide" }, el("span", { class: "attente" }, "⏳"), " Lecture des conteneurs…"));
    try { D.donnees = await api("/api/conteneurs/liste", {}); }
    catch (e) { racine().replaceChildren(el("div", { class: "vide" }, "😕 " + e.message)); return; }
    if (!D.donnees.installe) return ecranAbsent();
    if (!D.donnees.demarre) return ecranArrete();
    dessiner();
  }

  function ecranAbsent() {
    racine().replaceChildren(
      el("div", { class: "barre-vue" }, el("h2", {}, "🐳 Docker")),
      el("div", { class: "dk-ecran" },
        el("div", { class: "gros" }, "🐳"),
        el("h3", {}, "Docker n'est pas installé"),
        el("p", {}, "Docker sert à faire tourner des bases de données et des applis dans des conteneurs, sans rien installer d'autre sur ce PC."),
        el("div", { class: "boutons" },
          el("button", { class: "btn principal", onclick: () => api("/api/conteneurs/telecharger", {}).catch(e => toast(e.message, "erreur")) },
            "🌐 " + t("Télécharger Docker Desktop")),
          el("button", { class: "btn", onclick: afficher }, "🔄 " + t("Réessayer")))));
  }

  function ecranArrete() {
    const boutons = [];
    if (D.donnees.desktop) boutons.push(el("button", { class: "btn principal", onclick: e => demarrerDesktop(e.currentTarget) }, "▶️ " + t("Démarrer Docker Desktop")));
    boutons.push(el("button", { class: "btn", onclick: afficher }, "🔄 " + t("Réessayer")));
    racine().replaceChildren(
      el("div", { class: "barre-vue" }, el("h2", {}, "🐳 Docker")),
      el("div", { class: "dk-ecran" },
        el("div", { class: "gros" }, "💤"),
        el("h3", {}, "Docker Desktop n'est pas démarré"),
        el("p", {}, D.donnees.desktop ? "Démarrez-le pour voir vos conteneurs. Le premier démarrage peut prendre une minute."
          : selonSysteme("Lancez Docker Desktop depuis le menu Démarrer, puis réessayez.",
              "Démarrez Docker (sudo systemctl start docker) ou Docker Desktop, puis réessayez.")),
        el("div", { class: "boutons" }, boutons)));
  }

  async function demarrerDesktop(bouton) {
    if (D.attente) return;
    try { await api("/api/conteneurs/desktop", {}); }
    catch (e) { toast(e.message, "erreur", 6000); return; }
    D.attente = true;
    bouton.disabled = true;
    bouton.replaceChildren(el("span", { class: "attente" }, "⏳"), " " + t("Docker Desktop démarre…"));
    const fin = Date.now() + 120000;
    try {
      while (Date.now() < fin) {
        await new Promise(ok => setTimeout(ok, 3000));
        if (!$("#vue-conteneurs").classList.contains("actif")) return;
        let r;
        try { r = await api("/api/conteneurs/liste", {}); } catch { continue; }
        if (r.demarre) { D.donnees = r; toast(t("Docker est prêt"), "succes"); dessiner(); return; }
      }
      toast(t("Docker Desktop met du temps à démarrer : réessayez dans un instant."), "", 6000);
      ecranArrete();
    } finally { D.attente = false; }
  }

  function dessiner() {
    const recherche = el("input", { type: "search", placeholder: "Rechercher un conteneur…", value: D.recherche, spellcheck: "false",
      oninput: e => { D.recherche = e.target.value; dessinerGroupes(); } });
    racine().replaceChildren(
      el("div", { class: "barre-vue" },
        el("h2", {}, "🐳 Docker ", el("span", { class: "compte" }, String(D.donnees.nombre || 0))),
        el("span", { class: "dk-version" }, "v" + D.donnees.version),
        el("div", { class: "espace" }),
        el("div", { class: "champ-recherche" }, el("span", {}, "🔍"), recherche),
        el("button", { class: "btn", onclick: fenetreRessources }, "💽 " + t("Images et espace disque")),
        el("button", { class: "icone-btn", title: "Actualiser", onclick: afficher }, "🔄")),
      el("div", { id: "dk-groupes", class: "dk-groupes" }));
    dessinerGroupes();
  }

  function dessinerGroupes() {
    const zone = $("#dk-groupes");
    if (!zone) return;
    const q = D.recherche.trim().toLowerCase();
    const groupes = D.donnees.groupes
      .map(g => ({ ...g, conteneurs: g.conteneurs.filter(c => !q || `${g.projet} ${c.nom} ${c.image} ${c.service}`.toLowerCase().includes(q)) }))
      .filter(g => g.conteneurs.length);
    if (!groupes.length) {
      zone.replaceChildren(el("div", { class: "vide" }, D.donnees.groupes.length ? "Aucun conteneur ne correspond." : "Aucun conteneur sur ce PC pour l'instant."));
      return;
    }
    zone.replaceChildren(...groupes.map((g, i) => groupe(g, i)));
  }

  function groupe(g, i) {
    const total = D.donnees.groupes.find(x => x.projet === g.projet).conteneurs.length;
    const tete = el("div", { class: "dk-tete" },
      el("span", { class: "titre" }, g.projet ? "📦 " + g.projet : "🧊 " + t("Sans projet")),
      el("span", { class: "compte-dk" }, t("{n} en marche sur {total}", { n: g.en_marche, total })),
      el("span", { class: "espace" }),
      g.projet ? el("button", { class: "btn", disabled: g.en_marche === total ? "" : null,
        onclick: e => actionProjet("demarrer", g.projet, e.currentTarget) }, "▶️ " + t("Tout démarrer")) : null,
      g.projet ? el("button", { class: "btn", disabled: g.en_marche === 0 ? "" : null,
        onclick: e => actionProjet("arreter", g.projet, e.currentTarget) }, "⏹️ " + t("Tout arrêter")) : null);
    return el("div", { class: "dk-groupe", style: `animation-delay:${Math.min(i, 10) * 40}ms` }, tete, g.conteneurs.map(ligne));
  }

  function ligne(c) {
    const marche = c.etat === "running";
    const point = marche ? "marche" : c.etat === "restarting" || c.etat === "paused" ? "demarrage" : "";
    const ports = c.ports.map(p => p.hote
      ? el("button", { class: "dk-port", title: "Ouvrir dans le navigateur", onclick: () => ouvrir(p.hote) }, `${p.hote}→${p.conteneur}`)
      : el("span", { class: "dk-port" }, `${p.conteneur}/${p.proto}`));
    const actions = marche
      ? [el("button", { class: "icone-btn", title: "Redémarrer", onclick: e => action("redemarrer", c, e.currentTarget) }, "🔁"),
         el("button", { class: "icone-btn stop", title: "Arrêter", onclick: e => arreter(c, e.currentTarget) }, "⏹️")]
      : [el("button", { class: "icone-btn go", title: "Démarrer", onclick: e => action("demarrer", c, e.currentTarget) }, "▶️")];
    actions.push(el("button", { class: "icone-btn", title: "Journal", onclick: () => journal(c) }, "📜"));
    actions.push(el("button", { class: "icone-btn stop", title: marche ? "Arrêtez d'abord le conteneur" : "Supprimer",
      disabled: marche ? "" : null, onclick: () => supprimer(c) }, "🗑️"));
    return el("div", { class: "dk-ligne" },
      el("span", { class: "point " + point }),
      el("div", { class: "dk-infos" },
        el("div", { class: "dk-nom" }, c.service || c.nom, c.service && c.service !== c.nom ? el("span", { class: "dk-version" }, c.nom) : null),
        el("div", { class: "dk-sous" }, el("span", { class: "dk-image" }, c.image), el("span", {}, statut(c.statut)))),
      ports.length ? el("div", { class: "dk-ports" }, ports) : null,
      el("div", { class: "dk-actions" }, actions));
  }

  // -- actions -------------------------------------------------------------------
  const MESSAGES = { demarrer: "Conteneur démarré", arreter: "Conteneur arrêté", redemarrer: "Conteneur redémarré" };

  async function action(nom, c, bouton) {
    if (bouton) { bouton.disabled = true; bouton.replaceChildren(el("span", { class: "attente" }, "⏳")); }
    try { await api("/api/conteneurs/" + nom, { id: c.id }); toast(t(MESSAGES[nom]), "succes"); }
    catch (e) { toast(e.message, "erreur", 8000); }
    afficher();
  }

  async function arreter(c, bouton) {
    if (!(await confirmer("⏹️", "Arrêter ce conteneur ?", "Le service qu'il fait tourner ne répondra plus.", "Arrêter"))) return;
    action("arreter", c, bouton);
  }

  async function supprimer(c) {
    if (!(await confirmer("🗑️", "Supprimer ce conteneur ?", "Le conteneur est retiré. Ses volumes et son image restent sur ce PC.", "Supprimer"))) return;
    try { await api("/api/conteneurs/supprimer", { id: c.id }); toast(t("Conteneur supprimé"), "succes"); }
    catch (e) { toast(e.message, "erreur", 8000); }
    afficher();
  }

  async function actionProjet(nom, projet, bouton) {
    if (nom === "arreter" && !(await confirmer("⏹️", "Arrêter tout le projet ?", t("Tous les conteneurs de « {projet} » seront arrêtés.", { projet }), "Tout arrêter"))) return;
    if (bouton) { bouton.disabled = true; bouton.replaceChildren(el("span", { class: "attente" }, "⏳")); }
    try {
      await api("/api/conteneurs/projet/" + nom, { projet });
      toast(t(nom === "demarrer" ? "Projet démarré" : "Projet arrêté"), "succes");
    } catch (e) { toast(e.message, "erreur", 8000); }
    afficher();
  }

  async function ouvrir(port) {
    try { await api("/api/conteneurs/ouvrir", { port }); }
    catch (e) { toast(e.message, "erreur"); }
  }

  function grandeFenetre(contenu) {
    fenetre(contenu);
    $("#fenetre").style.width = "min(980px, 94vw)";
  }

  async function journal(c) {
    const zone = el("pre", { class: "dk-journal" }, t("Lecture…"));
    let texte = "";
    const lire = async () => {
      zone.textContent = t("Lecture…");
      try { texte = (await api("/api/conteneurs/journal", { id: c.id })).texte; zone.textContent = texte || t("Journal vide."); zone.scrollTop = zone.scrollHeight; }
      catch (e) { zone.textContent = "😕 " + e.message; }
    };
    grandeFenetre([
      el("h3", {}, "📜 " + t("Journal de {nom}", { nom: c.nom })),
      el("p", {}, "300 dernières lignes"),
      zone,
      el("div", { class: "actions" },
        el("button", { class: "btn", onclick: () => copier(texte) }, "📋 " + t("Copier")),
        el("button", { class: "btn", onclick: lire }, "🔄 " + t("Actualiser")),
        el("button", { class: "btn principal", onclick: fermer }, "Fermer"))]);
    lire();
  }

  async function fenetreRessources() {
    const zone = el("div", { class: "dk-fenetre" }, el("p", {}, el("span", { class: "attente" }, "⏳"), " " + t("Lecture…")));
    grandeFenetre([el("h3", {}, "💽 " + t("Images et espace disque")), zone,
      el("div", { class: "actions" }, el("button", { class: "btn principal", onclick: fermer }, "Fermer"))]);
    let r;
    try { r = await api("/api/conteneurs/ressources", {}); }
    catch (e) { zone.replaceChildren(el("p", {}, "😕 " + e.message)); return; }
    const tableau = (entetes, lignes, mono = []) => el("table", { class: "dk-table" },
      el("thead", {}, el("tr", {}, entetes.map(h => el("th", {}, h)))),
      el("tbody", {}, lignes.map(l => el("tr", {}, l.map((v, i) => el("td", { class: mono.includes(i) ? "mono" : "" }, document.createTextNode(String(v ?? ""))))))));
    zone.replaceChildren(
      el("h4", {}, "Espace occupé"),
      tableau(["Type", "Nombre", "Actifs", "Taille", "Récupérable"], r.place.map(p => [p.type, p.nombre, p.actifs, p.taille, p.recuperable])),
      el("h4", {}, "Images"),
      r.images.length
        ? tableau(["Image", "Tag", "Taille", "Créée"], r.images.map(i => [i.depot, i.tag, i.taille, i.cree]), [0, 1])
        : el("p", {}, "Aucune image."));
  }

  VUES.conteneurs = { afficher, titre: "Docker", icone: "🐳", groupe: "dev", ordre: 40 };
})();
