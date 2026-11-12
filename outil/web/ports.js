"use strict";
/* Onglet « Ports » : les ports en écoute sur ce PC, le programme qui les
   occupe, et l'arrêt de ce programme (voir ports.py). Le serveur refuse
   d'arrêter les processus système et « Mes outils » lui-même. */
(() => {
  I18N.ajouter({
    "Ports": "Ports",
    "Ports en écoute": "Listening ports",
    "Port ou programme…": "Port or program…",
    "Tous": "All",
    "Développement": "Development",
    "Inclure UDP": "Include UDP",
    "Actualiser": "Refresh",
    "Lecture des ports…": "Reading ports…",
    "Aucun port ne correspond.": "No port matches.",
    "Port": "Port",
    "Adresse": "Address",
    "Programme": "Program",
    "PID": "PID",
    "Mémoire": "Memory",
    "Ce PC seulement": "This PC only",
    "Tout le réseau": "Whole network",
    "Ouvrir dans le navigateur": "Open in browser",
    "Arrêter ce programme": "Stop this program",
    "Arrêter": "Stop",
    "Ouvrir": "Open",
    "Processus système : protégé": "System process: protected",
    "C'est « Mes outils » lui-même": "This is « Mes outils » itself",
    "Arrêter ce programme ?": "Stop this program?",
    "Arrêter aussi les programmes qu'il a lancés": "Also stop the programs it started",
    "Annuler": "Cancel",
    "Les données non enregistrées de ce programme seront perdues.": "Unsaved data in this program will be lost.",
    "Port {port} libre": "Port {port} is free",
    "Port {port} : {nom} (PID {pid})": "Port {port}: {nom} (PID {pid})",
    "{nom} arrêté": "{nom} stopped",
    "{n} Mo": "{n} MB",
    "{n} Ko": "{n} KB",
    "{n} Go": "{n} GB",
    "Ligne de commande copiée": "Command line copied",
    "Cliquer pour copier la ligne de commande": "Click to copy the command line",
    "Processus système : arrêt refusé.": "System process: stop refused.",
    "C'est « Mes outils » lui-même : arrêt refusé.": "This is « Mes outils » itself: stop refused.",
    "Ce processus n'existe plus.": "This process no longer exists.",
    "Ce numéro de processus correspond maintenant à un autre programme : actualisez la liste.":
      "This process number now belongs to another program: refresh the list.",
    "Cet arbre de processus contient « Mes outils » : arrêt refusé.": "This process tree contains « Mes outils »: stop refused.",
    "Numéro de processus invalide.": "Invalid process number.",
    "Numéro de port invalide.": "Invalid port number.",
  });
  I18N.motifs([[/^Arrêt impossible : (.*)$/, "Cannot stop: $1"]]);

  const P = { ports: null, recherche: "", filtre: "tous", udp: false, chargement: false };
  const racine = () => $("#vue-ports");

  const style = document.createElement("style");
  style.textContent = `
    .pt-recherche input { width: 250px; }
    .pt-udp { display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 700; color: var(--doux); cursor: pointer; }
    .pt-reponse { background: var(--carte); border-radius: var(--rayon); box-shadow: var(--ombre); padding: 12px 16px; margin-bottom: 14px;
      font-weight: 700; display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
    .pt-reponse.libre { color: var(--vert-texte); background: var(--vert-clair); box-shadow: none; }
    .pt-reponse.pris { color: var(--ambre-texte); background: var(--ambre-clair); box-shadow: none; }
    .pt-carte { background: var(--carte); border-radius: var(--rayon); box-shadow: var(--ombre); padding: 6px; overflow-x: auto; }
    .pt-table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 13.5px; }
    .pt-table th { text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: .8px; color: var(--gris); font-weight: 600; padding: 8px; }
    .pt-table td { padding: 7px 8px; border-top: 1px solid var(--ligne); vertical-align: middle; color: var(--encre); }
    .pt-table tr:hover td { background: var(--surface); }
    .pt-table tr.dev td:first-child { box-shadow: inset 3px 0 0 var(--violet); }
    .pt-port { font-family: var(--mono); font-weight: 600; font-size: 14.5px; white-space: nowrap; }
    .pt-proto { font-size: 10.5px; font-weight: 600; color: var(--gris); margin-left: 4px; }
    .pt-dev { display: inline-block; margin-top: 2px; background: var(--violet-clair); color: var(--violet); }
    .pt-adr { font-family: var(--mono); font-size: 12.5px; max-width: 190px; overflow-wrap: anywhere; }
    .pt-portee { display: block; font-family: "Segoe UI", system-ui, sans-serif; font-size: 11.5px; color: var(--doux); }
    .pt-portee.reseau { color: var(--ambre-texte); }
    .pt-nom { font-weight: 700; }
    .pt-cmd { display: block; max-width: 330px; font-family: var(--mono); font-size: 11.5px; color: var(--doux); white-space: nowrap;
      overflow: hidden; text-overflow: ellipsis; cursor: pointer; }
    .pt-cmd:hover { color: var(--violet); }
    .pt-num { font-variant-numeric: tabular-nums; white-space: nowrap; color: var(--doux); }
    .pt-actions { display: flex; gap: 4px; justify-content: flex-end; }
    .pt-badge { font-size: 11px; font-weight: 700; border-radius: 99px; padding: 1px 8px; background: var(--surface); color: var(--doux); white-space: nowrap; }
    .pt-choix { display: flex; gap: 8px; align-items: center; font-size: 14px; margin: 4px 0 6px; cursor: pointer; justify-content: center; color: var(--encre); }
    .pt-detail { background: var(--code); color: var(--code-texte); font-family: var(--mono); font-size: 12px; border-radius: 12px; padding: 8px 10px;
      text-align: left; word-break: break-all; max-height: 120px; overflow: auto; margin-bottom: 12px; }
  `;
  document.head.append(style);

  // -- outils -------------------------------------------------------------------
  const nombre = (n, dec = 0) => n.toLocaleString(I18N.locale(), { maximumFractionDigits: dec });
  function memoire(ko) {
    if (ko === null || ko === undefined) return "";
    if (ko < 1024) return t("{n} Ko", { n: nombre(ko) });
    if (ko < 1048576) return t("{n} Mo", { n: nombre(ko / 1024, ko < 10240 ? 1 : 0) });
    return t("{n} Go", { n: nombre(ko / 1048576, 1) });
  }
  const local = a => a === "127.0.0.1" || a === "::1" || a.startsWith("127.");
  const partout = a => a === "0.0.0.0" || a === "::" || a === "*";

  /** Une ligne par (protocole, port, PID) : IPv4 et IPv6 regroupés. */
  function regrouper(ports) {
    const lignes = new Map();
    for (const p of ports) {
      const cle = `${p.proto}|${p.port}|${p.pid}`;
      if (!lignes.has(cle)) lignes.set(cle, { ...p, adresses: [] });
      lignes.get(cle).adresses.push(p.adresse);
    }
    return [...lignes.values()];
  }

  // -- affichage -----------------------------------------------------------------
  async function charger(forcer = false) {
    if (P.chargement) return;
    P.chargement = true;
    try {
      const r = await api("/api/ports/liste", { udp: P.udp, forcer });
      P.ports = r.ports;
    } catch (e) {
      racine().replaceChildren(el("div", { class: "vide" }, "😕 " + e.message));
      return;
    } finally { P.chargement = false; }
    dessinerListe();
  }

  async function afficher() {
    dessiner();
    await charger(true);
  }

  function dessiner() {
    const recherche = el("input", { type: "search", placeholder: "Port ou programme…", value: P.recherche,
      spellcheck: "false", oninput: e => { P.recherche = e.target.value; dessinerListe(); } });
    const puces = el("div", { class: "puces" }, [["tous", "Tous"], ["dev", "Développement"]].map(([v, txt]) =>
      el("button", { class: "puce" + (P.filtre === v ? " actif" : ""), onclick: e => {
        P.filtre = v; e.target.parentNode.querySelectorAll(".puce").forEach(b => b.classList.toggle("actif", b === e.target)); dessinerListe();
      } }, txt)));
    const udp = el("input", { type: "checkbox", ...(P.udp ? { checked: "" } : {}),
      onchange: e => { P.udp = e.target.checked; charger(true); } });
    racine().replaceChildren(
      el("div", { class: "barre-vue" },
        el("h2", {}, "🔌 " + t("Ports en écoute"), " ", el("span", { class: "compte", id: "pt-nombre" }, "…")),
        el("div", { class: "espace" }),
        el("div", { class: "champ-recherche pt-recherche" }, el("span", {}, "🔍"), recherche),
        puces,
        el("label", { class: "pt-udp" }, udp, "Inclure UDP"),
        el("button", { class: "icone-btn", title: "Actualiser", onclick: () => charger(true) }, "🔄")),
      el("div", { id: "pt-reponse" }),
      el("div", { id: "pt-liste" }, el("div", { class: "vide" }, el("span", { class: "attente" }, "⏳"), " Lecture des ports…")));
    recherche.focus();
  }

  function visibles(lignes) {
    const q = P.recherche.trim().toLowerCase();
    const numero = /^:?\d{1,5}$/.test(q) ? Number(q.replace(":", "")) : null;
    return lignes.filter(l => {
      if (P.filtre === "dev" && !(l.dev || l.web)) return false;
      if (!q) return true;
      if (numero !== null) return String(l.port).startsWith(String(numero));
      return `${l.port} ${l.nom} ${l.commande ?? ""} ${l.pid ?? ""} ${l.dev ?? ""}`.toLowerCase().includes(q);
    });
  }

  function dessinerReponse(lignes) {
    const zone = $("#pt-reponse");
    if (!zone) return;
    const q = P.recherche.trim().replace(/^:/, "");
    if (!/^\d{1,5}$/.test(q)) { zone.replaceChildren(); return; }
    const port = Number(q);
    const pris = lignes.filter(l => l.port === port && l.proto === "TCP");
    zone.replaceChildren(pris.length
      ? el("div", { class: "pt-reponse pris" }, "🔌 ", pris.map(l => t("Port {port} : {nom} (PID {pid})", l)).join(" · "))
      : el("div", { class: "pt-reponse libre" }, "✅ ", t("Port {port} libre", { port })));
  }

  function dessinerListe() {
    const zone = $("#pt-liste");
    if (!zone || !P.ports) return;
    const toutes = regrouper(P.ports);
    const lignes = visibles(toutes);
    $("#pt-nombre").textContent = String(toutes.length);
    dessinerReponse(toutes);
    if (!lignes.length) { zone.replaceChildren(el("div", { class: "vide" }, "Aucun port ne correspond.")); return; }
    zone.replaceChildren(el("div", { class: "pt-carte" }, el("table", { class: "pt-table" },
      el("thead", {}, el("tr", {}, ["Port", "Adresse", "Programme", "PID", "Mémoire", ""].map(h => el("th", {}, h)))),
      el("tbody", {}, lignes.map(ligne)))));
  }

  function ligne(l) {
    const adr = l.adresses;
    const portee = adr.some(partout) ? el("span", { class: "pt-portee reseau" }, "Tout le réseau")
      : adr.every(local) ? el("span", { class: "pt-portee" }, "Ce PC seulement") : null;
    const actions = [];
    if (l.web) actions.push(el("button", { class: "icone-btn go", title: "Ouvrir dans le navigateur",
      onclick: () => ouvrir(l.port) }, "🌐"));
    if (l.protege) actions.push(el("span", { class: "pt-badge", title: "Processus système : protégé" }, "🔒"));
    else if (l.soi) actions.push(el("span", { class: "pt-badge", title: "C'est « Mes outils » lui-même" }, "🧰"));
    else actions.push(el("button", { class: "icone-btn stop", title: "Arrêter ce programme", onclick: () => arreter(l) }, "⛔"));
    return el("tr", { class: l.dev ? "dev" : "" },
      el("td", {}, el("span", { class: "pt-port" }, String(l.port)), el("span", { class: "pt-proto" }, l.proto),
        l.dev ? el("div", {}, el("span", { class: "etiquette pt-dev" }, l.dev)) : null),
      el("td", { class: "pt-adr" }, adr.join(", "), portee),
      el("td", {}, el("span", { class: "pt-nom" }, l.nom),
        l.commande ? el("span", { class: "pt-cmd", title: t("Cliquer pour copier la ligne de commande") + "\n" + l.commande,
          onclick: () => copier(l.commande, "📋 " + t("Ligne de commande copiée")) }, l.commande) : null),
      el("td", { class: "pt-num" }, l.pid == null ? "—" : String(l.pid)),
      el("td", { class: "pt-num" }, memoire(l.memoire_ko)),
      el("td", {}, el("div", { class: "pt-actions" }, actions)));
  }

  // -- actions -------------------------------------------------------------------
  async function ouvrir(port) {
    try { await api("/api/ports/ouvrir", { port }); }
    catch (e) { toast(e.message, "erreur", 6000); }
  }

  function arreter(l) {
    const arbre = el("input", { type: "checkbox" });
    const bouton = el("button", { class: "btn principal", onclick: async () => {
      bouton.disabled = true;
      try {
        const r = await api("/api/ports/arreter", { pid: l.pid, nom: l.nom, arbre: arbre.checked });
        fermer();
        toast(t("{nom} arrêté", { nom: r.nom }), "succes");
        await charger(true);
      } catch (e) { fermer(); toast(e.message, "erreur", 8000); charger(true); }
    } }, "⛔ " + t("Arrêter"));
    fenetre([
      el("div", { class: "gros" }, "⛔"),
      el("h3", {}, "Arrêter ce programme ?"),
      el("p", {}, `${l.nom} · PID ${l.pid ?? "—"} · ${t("Port")} ${l.port}`),
      l.commande ? el("div", { class: "pt-detail" }, l.commande) : null,
      el("p", {}, "Les données non enregistrées de ce programme seront perdues."),
      el("label", { class: "pt-choix" }, arbre, "Arrêter aussi les programmes qu'il a lancés"),
      el("div", { class: "actions" }, el("button", { class: "btn", onclick: fermer }, "Annuler"), bouton)].filter(Boolean), true);
  }

  VUES.ports = { afficher, titre: "Ports", icone: "🔌", groupe: "dev", ordre: 30 };
})();
