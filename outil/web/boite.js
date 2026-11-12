"use strict";
/* Onglet « Boîte à outils » : petits outils de développeur (JWT, Base64,
   JSON, horodatage, UUID, expressions régulières, URL, hachage, couleurs).
   Tout se passe dans la page : rien n'est envoyé au serveur. */
(() => {
  I18N.ajouter({
    "Boîte à outils": "Toolbox",
    "Tout se passe dans cette page : rien n'est envoyé.": "Everything happens in this page: nothing is sent.",
    "Copier": "Copy", "Effacer": "Clear", "Exemple": "Example",
    // JWT
    "Collez un jeton JWT (eyJ…)": "Paste a JWT (eyJ…)",
    " La signature n'est pas vérifiée : ce décodage montre le contenu du jeton, il ne prouve pas qu'il est authentique.":
      " The signature is not verified: this decoding shows the token's content, it does not prove it is genuine.",
    "En-tête": "Header", "Charge utile": "Payload", "Signature": "Signature", "Dates": "Dates",
    "Émis le (iat)": "Issued at (iat)", "Valide à partir du (nbf)": "Not before (nbf)", "Expire le (exp)": "Expires (exp)", "Authentifié le (auth_time)": "Authenticated (auth_time)",
    " Expiré depuis {d}": " Expired {d} ago", " Valide encore {d}": " Still valid for {d}", " Pas encore valide (dans {d})": " Not valid yet (in {d})",
    "Pas de date d'expiration (exp).": "No expiry date (exp).",
    "Un JWT a trois parties séparées par des points.": "A JWT has three parts separated by dots.",
    "Partie illisible (Base64 URL invalide).": "Unreadable part (invalid Base64 URL).",
    "Algorithme : {alg}": "Algorithm: {alg}",
    // Base64
    "Texte à encoder, ou Base64 à décoder": "Text to encode, or Base64 to decode",
    "Encoder": "Encode", "Décoder": "Decode", "Variante URL (- et _, sans =)": "URL-safe variant (- and _, no =)",
    "Résultat": "Result", "Échanger": "Swap", "Mettre le résultat dans l'entrée": "Put the result in the input",
    "Base64 invalide.": "Invalid Base64.",
    "Contenu binaire ({n} octets), affiché en hexadécimal :": "Binary content ({n} bytes), shown as hexadecimal:",
    // JSON
    "Collez du JSON": "Paste JSON", "Mettre en forme": "Format", "Compacter": "Minify", "Valider": "Validate",
    "Trier les clés": "Sort keys", "Indentation": "Indentation", "2 espaces": "2 spaces", "4 espaces": "4 spaces", "Tabulation": "Tab",
    " JSON valide": " Valid JSON", "Ligne {l}, colonne {c}": "Line {l}, column {c}",
    "Fin inattendue : il manque la suite (crochet, accolade ou guillemet fermant ?).": "Unexpected end: something is missing (closing bracket, brace or quote?).",
    "Caractère inattendu : {c}": "Unexpected character: {c}",
    "{n} caractères": "{n} characters",
    // Horodatage
    "Horodatage": "Timestamp", "Maintenant": "Now", "Unix → date": "Unix → date", "Date → Unix": "Date → Unix",
    "Horodatage Unix": "Unix timestamp", "Unité": "Unit", "Automatique": "Automatic", "Secondes": "Seconds", "Millisecondes": "Milliseconds",
    "Date locale": "Local date", "ISO 8601 (UTC)": "ISO 8601 (UTC)", "Par rapport à maintenant": "Relative to now",
    "Unix (secondes)": "Unix (seconds)", "Unix (millisecondes)": "Unix (milliseconds)", "Date et heure locales": "Local date and time",
    "il y a {d}": "{d} ago", "dans {d}": "in {d}", "à l'instant": "just now", "Nombre invalide.": "Invalid number.",
    "{n} j": "{n} d", "{n} h": "{n} h", "{n} min": "{n} min", "{n} s": "{n} s",
    // UUID
    "Nombre": "Count", "Majuscules": "Uppercase", "Sans tirets": "No hyphens", "Générer": "Generate", "Tout copier": "Copy all",
    "UUID v4 aléatoires (crypto.randomUUID).": "Random v4 UUIDs (crypto.randomUUID).",
    // Regex
    "Expressions régulières": "Regular expressions", "Motif": "Pattern", "Texte à tester": "Test text",
    "g : toutes les correspondances": "g: all matches", "i : ignorer la casse": "i: ignore case", "m : ^ et $ à chaque ligne": "m: ^ and $ on each line",
    "s : le point attrape aussi les retours à la ligne": "s: dot also matches line breaks", "u : Unicode": "u: Unicode",
    "Aucune correspondance.": "No match.", "{n} correspondance(s)": "{n} match(es)", "Groupes": "Groups",
    "Correspondances": "Matches", "Arrêt à 1 000 correspondances.": "Stopped at 1,000 matches.",
    "Motif invalide : {m}": "Invalid pattern: {m}", "position {i}": "position {i}", "(vide)": "(empty)",
    // URL
    "Encodage URL": "URL encoding", "Texte ou adresse": "Text or URL",
    "Encoder (composant)": "Encode (component)", "Encoder (adresse entière)": "Encode (whole URL)",
    "Encodage invalide.": "Invalid encoding.", "Détail de l'adresse": "URL breakdown",
    "Protocole": "Protocol", "Hôte": "Host", "Port": "Port", "Chemin": "Path", "Fragment": "Fragment", "Paramètres": "Parameters",
    "Utilisateur": "Username",
    // Hachage
    "Hachage": "Hashing", "Texte à hacher (UTF-8)": "Text to hash (UTF-8)", "…ou un fichier :": "…or a file:",
    "Fichier : {nom} ({taille})": "File: {nom} ({taille})", "Revenir au texte": "Back to text",
    "Comparer avec une empreinte attendue": "Compare with an expected hash", " identique": " match",
    "Calcul…": "Computing…",
    "SHA-1 est cassé pour la sécurité : ne s'en servir que pour comparer des fichiers.": "SHA-1 is broken for security: only use it to compare files.",
    // Couleurs
    "Couleurs": "Colors", "Couleur (hex, rgb(), hsl() ou nom CSS)": "Color (hex, rgb(), hsl() or CSS name)",
    "Couleur non reconnue.": "Unrecognised color.",
    "o": "B", "Ko": "KB", "Mo": "MB",
  });

  const style = document.createElement("style");
  style.textContent = `
    .bo-puces { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 14px; }
    .bo-puces .puce { background: var(--carte); box-shadow: var(--ombre); padding: 8px 14px; font-size: 13.5px; }
    .bo-puces .puce.actif { background: var(--violet); color: var(--sur-violet); }
    .bo-carte { background: var(--carte); border-radius: var(--rayon); box-shadow: var(--ombre); padding: 18px 20px; animation: apparait .3s both; }
    .bo-carte h3 { margin: 0 0 12px; font-size: 17px; display: flex; gap: 8px; align-items: center; }
    .bo-carte h3 + div > .bo-aide:first-child { margin-top: -6px; }
    .bo-champ input, .bo-champ select, .bo-champ textarea, .bo-zone { font-weight: 400; }
    .bo-aide { color: var(--doux); font-size: 13px; }
    .bo-zone, .bo-saisie, .bo-carte select {
      border: 1.5px solid var(--ligne); border-radius: 12px; padding: 9px 12px; background: var(--champ); color: var(--encre);
      outline: none; font-size: 14px; min-width: 0; }
    .bo-zone:focus, .bo-saisie:focus, .bo-carte select:focus { border-color: var(--violet); background: var(--champ-focus); }
    .bo-zone { width: 100%; resize: vertical; font-family: var(--mono); font-size: 13px; min-height: 110px; tab-size: 2; }
    .bo-mono { font-family: var(--mono); font-size: 13px; }
    .bo-actions { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin: 10px 0; }
    .bo-actions .btn { padding: 8px 14px; font-size: 13.5px; }
    .bo-coche { display: inline-flex; gap: 7px; align-items: center; font-size: 13.5px; cursor: pointer; color: var(--encre); }
    .bo-coche input { width: 16px; height: 16px; accent-color: var(--violet); }
    .bo-sortie { margin-top: 12px; min-width: 0; }
    .bo-sortie .bo-tete { display: flex; align-items: center; gap: 8px; font-size: 12.5px; font-weight: 600; color: var(--doux); text-transform: uppercase; letter-spacing: .6px; margin-bottom: 5px; }
    .bo-sortie .bo-tete .espace { flex: 1; }
    .bo-copier { white-space: nowrap; border: 0; background: var(--violet-clair); color: var(--violet); border-radius: 9px; padding: 3px 10px; font-size: 12px; font-weight: 700; cursor: pointer; text-transform: none; letter-spacing: 0; }
    .bo-copier:hover { background: var(--violet); color: var(--sur-violet); }
    .bo-code { background: var(--code); color: var(--code-texte); font-family: var(--mono); font-size: 12.5px; border-radius: 12px; padding: 11px 13px;
      margin: 0; max-height: 420px; overflow: auto; white-space: pre-wrap; word-break: break-all; }
    .bo-cle { color: var(--violet); } .bo-chaine { color: var(--vert-texte); } .bo-nombre { color: var(--bleu-texte); } .bo-mot { color: var(--ambre-texte); }
    .bo-deux { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
    @media (max-width: 900px) { .bo-deux { grid-template-columns: minmax(0, 1fr); } }
    .bo-alerte { border-radius: 12px; padding: 9px 12px; font-size: 13px; margin: 10px 0; }
    .bo-alerte.ambre { background: var(--ambre-clair); color: var(--ambre-texte); }
    .bo-alerte.rouge { background: var(--rouge-clair); color: var(--rouge-texte); }
    .bo-alerte.vert { background: var(--vert-clair); color: var(--vert-texte); }
    .bo-alerte.bleu { background: var(--bleu-clair); color: var(--bleu-texte); }
    .bo-table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
    .bo-table td { border-bottom: 1px solid var(--ligne); padding: 7px 8px; vertical-align: middle; overflow-wrap: anywhere; }
    .bo-table td:first-child { font-weight: 700; color: var(--doux); white-space: nowrap; width: 1%; word-break: normal; }
    .bo-table td.bo-v { font-family: var(--mono); font-size: 12.5px; }
    .bo-table td:last-child { width: 1%; text-align: right; white-space: nowrap; }
    .bo-champ { display: flex; flex-direction: column; gap: 5px; font-size: 12.5px; font-weight: 700; color: var(--doux); }
    .bo-ligne { display: flex; gap: 10px; align-items: flex-end; flex-wrap: wrap; }
    .bo-ligne .bo-champ { flex: 1; min-width: 180px; }
    .bo-regex { display: flex; align-items: center; gap: 4px; border: 1.5px solid var(--ligne); border-radius: 12px; background: var(--champ); padding: 0 10px; }
    .bo-regex:focus-within { border-color: var(--violet); background: var(--champ-focus); }
    .bo-regex span { color: var(--gris); font-family: var(--mono); font-size: 16px; }
    .bo-regex input { flex: 1; border: 0 !important; background: transparent !important; box-shadow: none !important; outline: none; padding: 9px 2px !important; font-weight: 400; font-family: var(--mono); font-size: 14px; color: var(--encre); min-width: 0; }
    .bo-drapeaux { display: flex; gap: 4px; }
    .bo-drapeaux button { border: 1.5px solid var(--ligne); background: var(--surface); color: var(--doux); border-radius: 9px; width: 32px; height: 32px;
      font-family: var(--mono); font-weight: 600; cursor: pointer; }
    .bo-drapeaux button.actif { background: var(--violet); border-color: var(--violet); color: var(--sur-violet); }
    .bo-surligne { background: var(--ambre-clair); color: var(--ambre-texte); border-radius: 3px; box-shadow: 0 0 0 1px var(--ambre); }
    .bo-surligne.vide { box-shadow: 0 0 0 1px var(--ambre); padding: 0 1px; }
    .bo-corresp { display: flex; flex-direction: column; gap: 6px; max-height: 320px; overflow: auto; }
    .bo-corresp > div { background: var(--surface); border-radius: 10px; padding: 7px 10px; font-size: 13px; }
    .bo-corresp code { font-family: var(--mono); background: var(--code); color: var(--code-texte); border-radius: 6px; padding: 1px 5px; word-break: break-all; }
    .bo-corresp small { color: var(--doux); margin-right: 6px; }
    .bo-pastille { width: 100%; height: 90px; border-radius: var(--rayon); border: 1.5px solid var(--ligne);
      background-image: linear-gradient(45deg, var(--surface) 25%, transparent 25%, transparent 75%, var(--surface) 75%),
        linear-gradient(45deg, var(--surface) 25%, transparent 25%, transparent 75%, var(--surface) 75%);
      background-size: 16px 16px; background-position: 0 0, 8px 8px; position: relative; overflow: hidden; }
    .bo-pastille div { position: absolute; inset: 0; }
    .bo-carte input[type=color] { width: 46px; height: 40px; border: 1.5px solid var(--ligne); border-radius: 12px; padding: 3px; background: var(--champ); cursor: pointer; }
    .bo-etat { font-size: 13px; font-weight: 700; }
    .bo-carte input[type=file] { color: var(--doux); font-size: 13px; }
    .bo-carte input[type=file]::file-selector-button { border: 0; background: var(--violet-clair); color: var(--violet); border-radius: 10px;
      padding: 7px 12px; font: inherit; font-weight: 700; cursor: pointer; margin-right: 8px; }
  `;
  document.head.append(style);

  // -- état (gardé quand on passe d'un outil à l'autre) ---------------------------
  const B = {
    outil: lireChoix() || "jwt",
    jwt: "", b64: "", b64url: false, b64sortie: null,
    json: "", jsonIndent: "2", jsonTri: false, jsonSortie: null,
    unix: "", unite: "auto", dateLocale: "",
    nbUuid: 5, uuidMaj: false, uuidSansTirets: false, uuids: [],
    motif: "(\\w+)@(\\w+)\\.com", drapeaux: "g", texteRegex: "contact@example.com, support@example.com",
    url: "", urlSortie: null,
    hache: "", fichier: null, attendu: "",
    couleur: "#6c4cf5",
  };
  function lireChoix() { try { return localStorage.getItem("boite.outil"); } catch { return null; } }
  function garderChoix(v) { try { localStorage.setItem("boite.outil", v); } catch { /* pas de stockage */ } }

  const OUTILS = [
    ["jwt", "", "JWT", outilJwt], ["base64", "", "Base64", outilBase64], ["json", "", "JSON", outilJson],
    ["temps", "", "Horodatage", outilTemps], ["uuid", "", "UUID", outilUuid], ["regex", icone("search"), "Expressions régulières", outilRegex],
    ["url", "", "Encodage URL", outilUrl], ["hachage", "", "Hachage", outilHachage], ["couleur", "", "Couleurs", outilCouleur],
  ];
  const racine = () => $("#vue-boite");

  function afficher() {
    if (!OUTILS.some(o => o[0] === B.outil)) B.outil = "jwt";
    const puces = el("div", { class: "bo-puces" }, OUTILS.map(([cle, icone, titre]) =>
      el("button", { class: "puce " + (B.outil === cle ? " actif" : ""), onclick: () => { B.outil = cle; garderChoix(cle); afficher(); } },
        icone + t(titre))));
    const [, icone, titre, fabrique] = OUTILS.find(o => o[0] === B.outil);
    racine().replaceChildren(
      el("div", { class: "barre-vue" }, el("h2", {}, t("Boîte à outils")), el("div", { class: "espace" }),
        el("span", { class: "bo-aide" }, t("Tout se passe dans cette page : rien n'est envoyé."))),
      puces,
      el("div", { class: "bo-carte" }, el("h3", {}, icone + t(titre)), fabrique()));
  }

  // -- briques communes -----------------------------------------------------------
  const boutonCopier = valeur => el("button", { class: "bo-copier", onclick: () => copier(typeof valeur === "function" ? valeur() : valeur) }, t("Copier"));
  /** Bloc « titre + bouton Copier + texte » ; le texte est posé en textContent. */
  function sortie(titre, valeur, coloration) {
    const pre = el("pre", { class: "bo-code" });
    if (coloration) pre.append(colorerJson(valeur)); else pre.textContent = valeur;
    return el("div", { class: "bo-sortie" },
      el("div", { class: "bo-tete" }, titre, el("span", { class: "espace" }), boutonCopier(valeur)), pre);
  }
  const zone = (valeur, placeholder, oninput, lignes = 5) => el("textarea", { class: "bo-zone", rows: lignes, spellcheck: "false", value: valeur, placeholder, oninput });
  const coche = (titre, actif, onchange) => el("label", { class: "bo-coche" },
    el("input", { type: "checkbox", checked: actif ? "" : null, onchange: e => onchange(e.target.checked) }), titre);
  const alerte = (genre, ...contenu) => el("div", { class: "bo-alerte " + genre }, ...contenu);
  /** Tableau « libellé | valeur | Copier ». */
  const tableau = lignes => el("table", { class: "bo-table" }, lignes.filter(Boolean).map(([lib, val]) =>
    el("tr", {}, el("td", {}, lib), el("td", { class: "bo-v" }, document.createTextNode(String(val))), el("td", {}, boutonCopier(String(val))))));

  function colorerJson(texte) {
    const frag = document.createDocumentFragment();
    if (texte.length > 300000) { frag.append(texte); return frag; }
    const motif = /("(?:\\.|[^"\\])*")(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?/g;
    let i = 0, m;
    while ((m = motif.exec(texte))) {
      if (m.index > i) frag.append(texte.slice(i, m.index));
      const classe = m[1] ? (m[2] ? "bo-cle" : "bo-chaine") : m[3] ? "bo-mot" : "bo-nombre";
      const s = document.createElement("span");
      s.className = classe; s.textContent = m[1] || m[0];
      frag.append(s);
      if (m[2]) frag.append(m[2]);
      i = motif.lastIndex;
    }
    frag.append(texte.slice(i));
    return frag;
  }

  /** Durée lisible : « 2 j 4 h », « 3 h 12 min », « 45 s ». */
  function dureeLisible(secondes) {
    let s = Math.abs(Math.round(secondes));
    const j = Math.floor(s / 86400); s -= j * 86400;
    const h = Math.floor(s / 3600); s -= h * 3600;
    const m = Math.floor(s / 60); s -= m * 60;
    const morceaux = j ? [[j, "{n} j"], [h, "{n} h"]] : h ? [[h, "{n} h"], [m, "{n} min"]] : m ? [[m, "{n} min"], [s, "{n} s"]] : [[s, "{n} s"]];
    return morceaux.filter(([n], i) => n || i === 0).map(([n, cle]) => t(cle, { n })).join(" ");
  }
  function relatif(date) {
    const ecart = (date.getTime() - Date.now()) / 1000;
    if (Math.abs(ecart) < 1) return t("à l'instant");
    return ecart < 0 ? t("il y a {d}", { d: dureeLisible(ecart) }) : t("dans {d}", { d: dureeLisible(ecart) });
  }
  const dateLocale = d => d.toLocaleString(I18N.locale(), { weekday: "short", day: "numeric", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit", second: "2-digit" });
  const taille = n => n < 1024 ? `${n} ${t("o")}` : n < 1048576 ? `${(n / 1024).toFixed(1)} ${t("Ko")}` : `${(n / 1048576).toFixed(1)} ${t("Mo")}`;

  // UTF-8 <-> Base64 sans perdre les accents.
  function octetsVersBase64(octets, urlSure) {
    let bin = "";
    for (let i = 0; i < octets.length; i += 0x8000) bin += String.fromCharCode(...octets.subarray(i, i + 0x8000));
    const b = btoa(bin);
    return urlSure ? b.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "") : b;
  }
  function base64VersOctets(texte) {
    let s = texte.replace(/\s+/g, "").replace(/-/g, " + ").replace(/_/g, "/");
    if (!/^[A-Za-z0-9+/]*={0,2}$/.test(s) || s.replace(/=+$/, "").length % 4 === 1) throw new Error(t("Base64 invalide."));
    s = s.replace(/=+$/, "");
    s += "===".slice((s.length + 3) % 4);
    const bin = atob(s);
    return Uint8Array.from(bin, c => c.charCodeAt(0));
  }
  const hex = octets => Array.from(octets, o => o.toString(16).padStart(2, "0")).join("");
  const hexEspace = octets => Array.from(octets.slice(0, 4096), o => o.toString(16).padStart(2, "0")).join(" ") + (octets.length > 4096 ? " …" : "");

  // -- JWT ------------------------------------------------------------------------
  function outilJwt() {
    const resultat = el("div");
    const dessiner = () => {
      const jeton = B.jwt.trim().replace(/^Bearer\s+/i, "");
      if (!jeton) { resultat.replaceChildren(); return; }
      const parties = jeton.split(".");
      if (parties.length < 2 || parties.length > 5) { resultat.replaceChildren(alerte("rouge", icone("x"), " ", t("Un JWT a trois parties séparées par des points."))); return; }
      const lire = p => {
        try { return new TextDecoder("utf-8", { fatal: true }).decode(base64VersOctets(p)); }
        catch { return null; }
      };
      const blocs = [alerte("ambre", "⚠️ La signature n'est pas vérifiée : ce décodage montre le contenu du jeton, il ne prouve pas qu'il est authentique.")];
      const json = texte => { try { return JSON.parse(texte); } catch { return undefined; } };
      const tete = lire(parties[0]), corps = lire(parties[1]);
      const teteJson = tete !== null ? json(tete) : undefined, corpsJson = corps !== null ? json(corps) : undefined;
      if (teteJson?.alg) blocs.push(el("div", { class: "bo-aide" }, t("Algorithme : {alg}", { alg: String(teteJson.alg) })));
      const colonne = (titre, brut, valeur) => brut === null
        ? el("div", { class: "bo-sortie" }, el("div", { class: "bo-tete" }, titre), alerte("rouge", icone("x"), " ", t("Partie illisible (Base64 URL invalide).")))
        : valeur === undefined ? sortie(titre, brut) : sortie(titre, JSON.stringify(valeur, null, 2), true);
      blocs.push(el("div", { class: "bo-deux" }, colonne(t("En-tête"), tete, teteJson), colonne(t("Charge utile"), corps, corpsJson)));
      if (corpsJson && typeof corpsJson === "object") {
        const maintenant = Date.now() / 1000;
        const lignes = [["iat", "Émis le (iat)"], ["nbf", "Valide à partir du (nbf)"], ["exp", "Expire le (exp)"], ["auth_time", "Authentifié le (auth_time)"]]
          .filter(([k]) => typeof corpsJson[k] === "number")
          .map(([k, lib]) => { const d = new Date(corpsJson[k] * 1000); return [t(lib), `${dateLocale(d)}  ·  ${d.toISOString()}  ·  ${relatif(d)}`]; });
        const etats = [];
        if (typeof corpsJson.nbf === "number" && corpsJson.nbf > maintenant) etats.push(alerte("ambre", t("⏳ Pas encore valide (dans {d})", { d: dureeLisible(corpsJson.nbf - maintenant) })));
        if (typeof corpsJson.exp === "number") {
          etats.push(corpsJson.exp < maintenant
            ? alerte("rouge", t("⛔ Expiré depuis {d}", { d: dureeLisible(maintenant - corpsJson.exp) }))
            : alerte("vert", t("✅ Valide encore {d}", { d: dureeLisible(corpsJson.exp - maintenant) })));
        } else etats.push(alerte("bleu", "Pas de date d'expiration (exp)."));
        blocs.push(el("div", { class: "bo-sortie" }, el("div", { class: "bo-tete" }, t("Dates")), ...etats, lignes.length ? tableau(lignes) : null));
      }
      if (parties[2]) blocs.push(sortie(t("Signature"), parties[2]));
      resultat.replaceChildren(...blocs);
    };
    const exemple = () => {
      const enc = o => octetsVersBase64(new TextEncoder().encode(JSON.stringify(o)), true);
      const n = Math.floor(Date.now() / 1000);
      B.jwt = `${enc({ alg: "HS256", typ: "JWT" })}.${enc({ sub: "1234567890", name: t("Exemple"), iat: n - 3600, exp: n + 7200 })}.signature`;
      afficher();
    };
    dessiner();
    return el("div", {},
      el("p", { class: "bo-aide" }, "Tout se passe dans cette page : rien n'est envoyé."),
      zone(B.jwt, "Collez un jeton JWT (eyJ…)", e => { B.jwt = e.target.value; dessiner(); }, 4),
      el("div", { class: "bo-actions" },
        el("button", { class: "btn discret", onclick: exemple }, icone("sparkles"), " ", t("Exemple")),
        el("button", { class: "btn discret", onclick: () => { B.jwt = ""; afficher(); } }, icone("brush"), " ", t("Effacer"))),
      resultat);
  }

  // -- Base64 ---------------------------------------------------------------------
  function outilBase64() {
    const resultat = el("div");
    const montrer = () => {
      const s = B.b64sortie;
      if (!s) resultat.replaceChildren();
      else if (s.erreur) resultat.replaceChildren(alerte("rouge", icone("x"), " ", s.erreur));
      else if (s.binaire) resultat.replaceChildren(el("div", { class: "bo-aide", style: "margin-top:10px" }, t("Contenu binaire ({n} octets), affiché en hexadécimal :", { n: s.binaire })), sortie(t("Résultat"), s.texte));
      else resultat.replaceChildren(sortie(t("Résultat"), s.texte));
    };
    const encoder = () => { B.b64sortie = { texte: octetsVersBase64(new TextEncoder().encode(B.b64), B.b64url) }; montrer(); };
    const decoder = () => {
      try {
        const octets = base64VersOctets(B.b64);
        try { B.b64sortie = { texte: new TextDecoder("utf-8", { fatal: true }).decode(octets) }; }
        catch { B.b64sortie = { texte: hexEspace(octets), binaire: octets.length }; }
      } catch (e) { B.b64sortie = { erreur: e.message }; }
      montrer();
    };
    montrer();
    return el("div", {},
      zone(B.b64, "Texte à encoder, ou Base64 à décoder", e => { B.b64 = e.target.value; }, 5),
      el("div", { class: "bo-actions" },
        el("button", { class: "btn principal", onclick: encoder }, "⬆ " + t("Encoder")),
        el("button", { class: "btn", onclick: decoder }, "⬇ " + t("Décoder")),
        coche(t("Variante URL (- et _, sans =)"), B.b64url, v => { B.b64url = v; }),
        el("span", { class: "espace", style: "flex:1" }),
        el("button", { class: "btn discret", title: "Mettre le résultat dans l'entrée", onclick: () => {
          if (B.b64sortie?.texte && !B.b64sortie.binaire) { B.b64 = B.b64sortie.texte; B.b64sortie = null; afficher(); }
        } }, t("Échanger"))),
      resultat);
  }

  // -- JSON -----------------------------------------------------------------------
  function trier(v) {
    if (Array.isArray(v)) return v.map(trier);
    if (v && typeof v === "object") return Object.fromEntries(Object.keys(v).sort().map(k => [k, trier(v[k])]));
    return v;
  }
  /** Position de la première erreur de syntaxe JSON (null si rien trouvé).
      Petit analyseur : le message de JSON.parse ne donne pas toujours la position. */
  function positionErreur(s) {
    let i = 0;
    const blancs = () => { while (i < s.length && " \t\n\r".includes(s[i])) i++; };
    const echec = () => { throw i; };
    function chaine() {
      i++;
      while (i < s.length) {
        const c = s[i];
        if (c === '"') { i++; return; }
        if (c === "\\") {
          const suite = s[i + 1] || "";
          if (!suite || !'"\\/bfnrtu'.includes(suite)) { i++; echec(); }
          if (suite === "u" && !/^[0-9a-fA-F]{4}$/.test(s.slice(i + 2, i + 6))) { i += 2; echec(); }
          i += suite === "u" ? 6 : 2;
          continue;
        }
        if (c < " ") echec();
        i++;
      }
      echec();
    }
    function valeur() {
      blancs();
      const c = s[i];
      if (c === "{") {
        i++; blancs();
        if (s[i] === "}") { i++; return; }
        for (;;) {
          blancs();
          if (s[i] !== '"') echec();
          chaine(); blancs();
          if (s[i] !== ":") echec();
          i++; valeur(); blancs();
          if (s[i] === ",") { i++; continue; }
          if (s[i] === "}") { i++; return; }
          echec();
        }
      }
      if (c === "[") {
        i++; blancs();
        if (s[i] === "]") { i++; return; }
        for (;;) {
          valeur(); blancs();
          if (s[i] === ",") { i++; continue; }
          if (s[i] === "]") { i++; return; }
          echec();
        }
      }
      if (c === '"') { chaine(); return; }
      const n = /^-?(0|[1-9]\d*)(\.\d+)?([eE][+-]?\d+)?/.exec(s.slice(i, i + 500));
      if (n) { i += n[0].length; return; }
      for (const mot of ["true", "false", "null"]) if (s.startsWith(mot, i)) { i += mot.length; return; }
      echec();
    }
    try { valeur(); blancs(); if (i < s.length) echec(); return null; }
    catch (p) { return typeof p === "number" ? p : null; }
  }
  /** Erreur JSON.parse → message en clair, ligne, colonne et extrait. */
  function erreurJson(texte, e) {
    const pos = positionErreur(texte);
    if (pos === null) return { message: e.message };
    const message = pos >= texte.length ? t("Fin inattendue : il manque la suite (crochet, accolade ou guillemet fermant ?).")
      : t("Caractère inattendu : {c}", { c: JSON.stringify(texte[pos]) });
    const avant = texte.slice(0, pos);
    const ligne = avant.split("\n").length, colonne = pos - avant.lastIndexOf("\n");
    const texteLigne = texte.split("\n")[ligne - 1] || "";
    const debut = Math.max(0, colonne - 60);
    return { message, ligne, colonne, extrait: texteLigne.slice(debut, debut + 120) + "\n " + " ".repeat(Math.max(0, colonne - 1 - debut)) + "^" };
  }
  function outilJson() {
    const resultat = el("div");
    const montrer = () => {
      const s = B.jsonSortie;
      if (!s) { resultat.replaceChildren(); return; }
      if (s.erreur) {
        const er = s.erreur;
        resultat.replaceChildren(...[alerte("rouge", "❌ ", er.ligne ? el("b", {}, t("Ligne {l}, colonne {c}", { l: er.ligne, c: er.colonne }) + " : ") : null, er.message),
          er.extrait ? el("pre", { class: "bo-code" }, document.createTextNode(er.extrait)) : null].filter(Boolean));
        return;
      }
      resultat.replaceChildren(...[s.valide ? alerte("vert", "✅ JSON valide") : null,
        s.texte !== undefined ? sortie(t("Résultat") + "· " + t("{n} caractères", { n: s.texte.length.toLocaleString(I18N.locale()) }), s.texte, true) : null].filter(Boolean));
    };
    const traiter = mode => {
      let v;
      try { v = JSON.parse(B.json); }
      catch (e) { B.jsonSortie = { erreur: erreurJson(B.json, e) }; montrer(); return; }
      if (B.jsonTri) v = trier(v);
      const indent = B.jsonIndent === "tab" ? "\t" : Number(B.jsonIndent);
      B.jsonSortie = mode === "valider" ? { valide: true } : { valide: true, texte: mode === "compacter" ? JSON.stringify(v) : JSON.stringify(v, null, indent) };
      montrer();
    };
    const indentation = el("select", { title: "Indentation", onchange: e => { B.jsonIndent = e.target.value; } },
      el("option", { value: "2" }, "2 espaces"), el("option", { value: "4" }, "4 espaces"), el("option", { value: "tab" }, "Tabulation"));
    indentation.value = B.jsonIndent;
    montrer();
    return el("div", {},
      zone(B.json, "Collez du JSON", e => { B.json = e.target.value; }, 9),
      el("div", { class: "bo-actions" },
        el("button", { class: "btn principal", onclick: () => traiter("forme") }, icone("sparkles"), " ", t("Mettre en forme")),
        el("button", { class: "btn", onclick: () => traiter("compacter") }, t("Compacter")),
        el("button", { class: "btn", onclick: () => traiter("valider") }, icone("check"), " ", t("Valider")),
        indentation,
        coche(t("Trier les clés"), B.jsonTri, v => { B.jsonTri = v; })),
      resultat);
  }

  // -- Horodatage -----------------------------------------------------------------
  function versDateLocale(d) {
    const p = n => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
  }
  function outilTemps() {
    const versDate = el("div"), versUnix = el("div");
    const dessinerUnix = () => {
      const brut = B.unix.trim();
      if (!brut) { versDate.replaceChildren(); return; }
      const n = Number(brut);
      if (!Number.isFinite(n)) { versDate.replaceChildren(alerte("rouge", icone("x"), " ", t("Nombre invalide."))); return; }
      const ms = B.unite === "ms" || (B.unite === "auto" && Math.abs(n) >= 1e11) ? n : n * 1000;
      const d = new Date(ms);
      if (isNaN(d)) { versDate.replaceChildren(alerte("rouge", icone("x"), " ", t("Nombre invalide."))); return; }
      versDate.replaceChildren(tableau([[t("Date locale"), dateLocale(d)], [t("ISO 8601 (UTC)"), d.toISOString()],
        [t("Par rapport à maintenant"), relatif(d)], [t("Unix (secondes)"), Math.floor(ms / 1000)], [t("Unix (millisecondes)"), Math.round(ms)]]));
    };
    const dessinerDate = () => {
      if (!B.dateLocale) { versUnix.replaceChildren(); return; }
      const d = new Date(B.dateLocale);
      if (isNaN(d)) { versUnix.replaceChildren(); return; }
      versUnix.replaceChildren(tableau([[t("Unix (secondes)"), Math.floor(d.getTime() / 1000)], [t("Unix (millisecondes)"), d.getTime()],
        [t("ISO 8601 (UTC)"), d.toISOString()], [t("Par rapport à maintenant"), relatif(d)]]));
    };
    const unite = el("select", { title: "Unité", onchange: e => { B.unite = e.target.value; dessinerUnix(); } },
      el("option", { value: "auto" }, "Automatique"), el("option", { value: "s" }, "Secondes"), el("option", { value: "ms" }, "Millisecondes"));
    unite.value = B.unite;
    const champUnix = el("input", { class: "bo-saisie bo-mono", value: B.unix, placeholder: "1700000000", inputmode: "numeric",
      oninput: e => { B.unix = e.target.value; dessinerUnix(); } });
    const champDate = el("input", { class: "bo-saisie", type: "datetime-local", step: "1", value: B.dateLocale,
      oninput: e => { B.dateLocale = e.target.value; dessinerDate(); } });
    const maintenant = () => {
      const d = new Date();
      B.unix = String(Math.floor(d.getTime() / 1000)); B.dateLocale = versDateLocale(d);
      champUnix.value = B.unix; champDate.value = B.dateLocale;
      dessinerUnix(); dessinerDate();
    };
    if (!B.unix && !B.dateLocale) maintenant(); else { dessinerUnix(); dessinerDate(); }
    return el("div", {},
      el("div", { class: "bo-actions", style: "margin-top:0" }, el("button", { class: "btn principal", onclick: maintenant }, t("Maintenant"))),
      el("div", { class: "bo-deux" },
        el("div", {}, el("div", { class: "bo-sortie" }, el("div", { class: "bo-tete" }, t("Unix → date"))),
          el("div", { class: "bo-ligne" }, el("label", { class: "bo-champ" }, "Horodatage Unix", champUnix), el("label", { class: "bo-champ", style: "flex:none;min-width:0" }, "Unité", unite)),
          versDate),
        el("div", {}, el("div", { class: "bo-sortie" }, el("div", { class: "bo-tete" }, t("Date → Unix"))),
          el("div", { class: "bo-ligne" }, el("label", { class: "bo-champ" }, "Date et heure locales", champDate)),
          versUnix)));
  }

  // -- UUID -----------------------------------------------------------------------
  function uuid4() {
    if (crypto.randomUUID) return crypto.randomUUID();
    const o = crypto.getRandomValues(new Uint8Array(16));
    o[6] = (o[6] & 0x0f) | 0x40; o[8] = (o[8] & 0x3f) | 0x80;
    const h = hex(o);
    return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`;
  }
  function outilUuid() {
    const resultat = el("div");
    const forme = u => { let s = B.uuidSansTirets ? u.replace(/-/g, "") : u; return B.uuidMaj ? s.toUpperCase() : s; };
    const montrer = () => {
      const lignes = B.uuids.map(forme);
      resultat.replaceChildren(el("div", { class: "bo-sortie" },
        el("div", { class: "bo-tete" }, "UUID v4", el("span", { class: "espace" }),
          el("button", { class: "bo-copier", onclick: () => copier(lignes.join("\n")) }, icone("clipboard"), " ", t("Tout copier"))),
        el("table", { class: "bo-table" }, lignes.map(u => el("tr", {}, el("td", { class: "bo-v", style: "width:auto" }, document.createTextNode(u)), el("td", {}, boutonCopier(u)))))));
    };
    const generer = () => { B.uuids = Array.from({ length: Math.min(Math.max(B.nbUuid, 1), 100) }, uuid4); montrer(); };
    if (!B.uuids.length) generer(); else montrer();
    return el("div", {},
      el("p", { class: "bo-aide" }, "UUID v4 aléatoires (crypto.randomUUID)."),
      el("div", { class: "bo-actions" },
        el("label", { class: "bo-coche" }, "Nombre", el("input", { class: "bo-saisie", type: "number", min: "1", max: "100", value: B.nbUuid, style: "width:80px",
          oninput: e => { B.nbUuid = Number(e.target.value) || 1; } })),
        coche(t("Majuscules"), B.uuidMaj, v => { B.uuidMaj = v; montrer(); }),
        coche(t("Sans tirets"), B.uuidSansTirets, v => { B.uuidSansTirets = v; montrer(); }),
        el("button", { class: "btn principal", onclick: generer }, t("Générer"))),
      resultat);
  }

  // -- Expressions régulières -----------------------------------------------------
  function outilRegex() {
    const resultat = el("div");
    let minuterie = null;
    const plus_tard = () => { clearTimeout(minuterie); minuterie = setTimeout(dessiner, 120); };
    function dessiner() {
      if (!B.motif) { resultat.replaceChildren(); return; }
      let re;
      try { re = new RegExp(B.motif, B.drapeaux.includes("g") ? B.drapeaux : B.drapeaux + "g"); }
      catch (e) { resultat.replaceChildren(alerte("rouge", icone("x"), " ", t("Motif invalide : {m}", { m: e.message }))); return; }
      const texte = B.texteRegex, toutes = B.drapeaux.includes("g");
      const trouvees = [];
      let m, limite = false;
      while ((m = re.exec(texte))) {
        trouvees.push(m);
        if (!toutes) break;
        if (trouvees.length >= 1000) { limite = true; break; }
        if (m[0] === "") re.lastIndex += (B.drapeaux.includes("u") && texte.codePointAt(re.lastIndex) > 0xffff) ? 2 : 1;
      }
      // Texte surligné, construit en nœuds.
      const pre = el("pre", { class: "bo-code", style: "max-height:260px" });
      let i = 0;
      for (const x of trouvees) {
        if (x.index > i) pre.append(texte.slice(i, x.index));
        const marque = document.createElement("mark");
        marque.className = "bo-surligne " + (x[0] === "" ? " vide" : "");
        marque.textContent = x[0];
        pre.append(marque);
        i = x.index + x[0].length;
      }
      pre.append(texte.slice(i));
      const liste = el("div", { class: "bo-corresp" }, trouvees.slice(0, 200).map((x, n) => {
        const groupes = [];
        for (let g = 1; g < x.length; g++) groupes.push(el("span", { style: "margin-right:10px" }, el("small", {}, `$${g}`), el("code", {}, x[g] === undefined ? "∅" : x[g] || t("(vide)"))));
        for (const [nom, v] of Object.entries(x.groups || {})) groupes.push(el("span", { style: "margin-right:10px" }, el("small", {}, `<${nom}>`), el("code", {}, v === undefined ? "∅" : v || t("(vide)"))));
        return el("div", {}, el("small", {}, `#${n + 1} · ${t("position {i}", { i: x.index })}`), el("code", {}, x[0] || t("(vide)")),
          groupes.length ? el("div", { style: "margin-top:5px" }, el("small", {}, t("Groupes") + " :"), groupes) : null);
      }));
      resultat.replaceChildren(...[
        el("div", { class: "bo-sortie" }, el("div", { class: "bo-tete" }, trouvees.length ? t("{n} correspondance(s)", { n: trouvees.length }) : t("Aucune correspondance."))),
        limite ? alerte("ambre", "Arrêt à 1 000 correspondances.") : null,
        pre,
        trouvees.length ? el("div", { class: "bo-sortie" }, el("div", { class: "bo-tete" }, t("Correspondances")), liste) : null].filter(Boolean));
    }
    const drapeaux = el("div", { class: "bo-drapeaux" }, [["g", "g : toutes les correspondances"], ["i", "i : ignorer la casse"],
      ["m", "m : ^ et $ à chaque ligne"], ["s", "s : le point attrape aussi les retours à la ligne"], ["u", "u : Unicode"]].map(([f, aide]) =>
      el("button", { class: B.drapeaux.includes(f) ? "actif" : "", title: aide, onclick: e => {
        B.drapeaux = B.drapeaux.includes(f) ? B.drapeaux.replace(f, "") : B.drapeaux + f;
        e.currentTarget.classList.toggle("actif", B.drapeaux.includes(f)); dessiner();
      } }, f)));
    dessiner();
    return el("div", {},
      el("div", { class: "bo-ligne" },
        el("label", { class: "bo-champ" }, "Motif",
          el("div", { class: "bo-regex" }, el("span", {}, "/"),
            el("input", { value: B.motif, spellcheck: "false", oninput: e => { B.motif = e.target.value; plus_tard(); } }), el("span", {}, "/"))),
        drapeaux),
      el("label", { class: "bo-champ", style: "margin-top:10px" }, "Texte à tester",
        zone(B.texteRegex, "", e => { B.texteRegex = e.target.value; plus_tard(); }, 5)),
      resultat);
  }

  // -- Encodage URL ---------------------------------------------------------------
  function outilUrl() {
    const resultat = el("div"), detail = el("div");
    const montrer = () => {
      const s = B.urlSortie;
      resultat.replaceChildren(...(s ? [s.erreur ? alerte("rouge", icone("x"), " ", s.erreur) : sortie(t("Résultat"), s.texte)] : []));
    };
    const decomposer = () => {
      let u;
      try { u = new URL(B.url.trim()); } catch { detail.replaceChildren(); return; }
      if (!u.host) { detail.replaceChildren(); return; }
      const lignes = [[t("Protocole"), u.protocol.replace(/:$/, "")], u.username ? [t("Utilisateur"), decodeURIComponent(u.username)] : null,
        [t("Hôte"), u.hostname], u.port ? [t("Port"), u.port] : null, [t("Chemin"), decodeURIComponent(u.pathname)],
        ...[...u.searchParams].map(([k, v]) => [`?${k}`, v]), u.hash ? [t("Fragment"), decodeURIComponent(u.hash.slice(1))] : null];
      detail.replaceChildren(el("div", { class: "bo-sortie" }, el("div", { class: "bo-tete" }, t("Détail de l'adresse"))), tableau(lignes));
    };
    const faire = f => {
      try { B.urlSortie = { texte: f(B.url) }; } catch { B.urlSortie = { erreur: t("Encodage invalide.") }; }
      montrer();
    };
    montrer(); decomposer();
    return el("div", {},
      zone(B.url, "Texte ou adresse", e => { B.url = e.target.value; decomposer(); }, 3),
      el("div", { class: "bo-actions" },
        el("button", { class: "btn principal", onclick: () => faire(encodeURIComponent) }, "⬆ " + t("Encoder (composant)")),
        el("button", { class: "btn", onclick: () => faire(encodeURI) }, "⬆ " + t("Encoder (adresse entière)")),
        el("button", { class: "btn", onclick: () => faire(s => decodeURIComponent(s.replace(/\+/g, " "))) }, "⬇ " + t("Décoder"))),
      resultat, detail);
  }

  // -- Hachage --------------------------------------------------------------------
  function outilHachage() {
    const resultat = el("div");
    let numero = 0;
    async function calculer() {
      const n = ++numero;
      const donnees = B.fichier ? await B.fichier.arrayBuffer() : new TextEncoder().encode(B.hache);
      const algos = ["SHA-1", "SHA-256", "SHA-384", "SHA-512"];
      const empreintes = await Promise.all(algos.map(a => crypto.subtle.digest(a, donnees).then(b => hex(new Uint8Array(b)))));
      if (n !== numero) return;  // un calcul plus récent est en cours
      const attendu = B.attendu.trim().toLowerCase();
      resultat.replaceChildren(...[
        B.fichier ? el("div", { class: "bo-actions" }, el("span", { class: "bo-etat" }, icone("file-text"), " ", t("Fichier : {nom} ({taille})", { nom: B.fichier.name, taille: taille(B.fichier.size) })),
          el("button", { class: "btn discret", onclick: () => { B.fichier = null; afficher(); } }, "↩ " + t("Revenir au texte"))) : null,
        tableau(algos.map((a, i) => [attendu && attendu === empreintes[i] ? `${a}  ` : a, empreintes[i]])),
        attendu && !empreintes.includes(attendu) ? alerte("rouge", icone("x"), " ", t("Aucune correspondance.")) : null,
        el("p", { class: "bo-aide" }, "SHA-1 est cassé pour la sécurité : ne s'en servir que pour comparer des fichiers.")].filter(Boolean));
    }
    const lancer = () => calculer().catch(e => resultat.replaceChildren(alerte("rouge", icone("x"), " ", e.message)));
    const fichier = el("input", { type: "file", onchange: e => { B.fichier = e.target.files[0] || null; if (B.fichier) { resultat.replaceChildren(el("p", { class: "bo-aide" }, icone("loader"), " ", t("Calcul…"))); lancer(); } } });
    lancer();
    return el("div", {},
      B.fichier ? null : zone(B.hache, "Texte à hacher (UTF-8)", e => { B.hache = e.target.value; lancer(); }, 4),
      el("div", { class: "bo-actions" }, el("span", { class: "bo-aide" }, "…ou un fichier :"), fichier),
      el("input", { class: "bo-saisie bo-mono", style: "width:100%;margin-bottom:10px", value: B.attendu, placeholder: "Comparer avec une empreinte attendue",
        spellcheck: "false", oninput: e => { B.attendu = e.target.value; lancer(); } }),
      resultat);
  }

  // -- Couleurs -------------------------------------------------------------------
  function lireCouleur(texte) {
    const essai = new Option().style;
    essai.color = texte.trim();
    if (!essai.color) return null;
    const sonde = el("span", { style: "display:none" });
    sonde.style.color = essai.color;
    document.body.append(sonde);
    const calcule = getComputedStyle(sonde).color;
    sonde.remove();
    const m = /^rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\)$/.exec(calcule);
    if (!m) return null;
    return { r: Math.round(+m[1]), g: Math.round(+m[2]), b: Math.round(+m[3]), a: m[4] === undefined ? 1 : +m[4] };
  }
  function versHsl({ r, g, b }) {
    r /= 255; g /= 255; b /= 255;
    const max = Math.max(r, g, b), min = Math.min(r, g, b), l = (max + min) / 2;
    let h = 0, s = 0;
    if (max !== min) {
      const d = max - min;
      s = l > .5 ? d / (2 - max - min) : d / (max + min);
      h = max === r ? (g - b) / d + (g < b ? 6 : 0) : max === g ? (b - r) / d + 2 : (r - g) / d + 4;
      h *= 60;
    }
    return { h: Math.round(h), s: Math.round(s * 100), l: Math.round(l * 100) };
  }
  function outilCouleur() {
    const resultat = el("div");
    const pastille = el("div");
    const selecteur = el("input", { type: "color", title: "Couleurs", oninput: e => { B.couleur = e.target.value; champ.value = B.couleur; dessiner(); } });
    const champ = el("input", { class: "bo-saisie bo-mono", style: "flex:1", value: B.couleur, spellcheck: "false",
      placeholder: "Couleur (hex, rgb(), hsl() ou nom CSS)", oninput: e => { B.couleur = e.target.value; dessiner(); } });
    function dessiner() {
      const c = lireCouleur(B.couleur);
      if (!c) { pastille.style.background = "transparent"; resultat.replaceChildren(...(B.couleur.trim() ? [alerte("rouge", icone("x"), " ", t("Couleur non reconnue."))] : [])); return; }
      const h2 = n => n.toString(16).padStart(2, "0");
      const hexa = `#${h2(c.r)}${h2(c.g)}${h2(c.b)}` + (c.a < 1 ? h2(Math.round(c.a * 255)) : "");
      const { h, s, l } = versHsl(c);
      pastille.style.background = `rgba(${c.r}, ${c.g}, ${c.b}, ${c.a})`;
      selecteur.value = hexa.slice(0, 7);
      resultat.replaceChildren(tableau([
        ["HEX", hexa],
        ["RGB", c.a < 1 ? `rgba(${c.r}, ${c.g}, ${c.b}, ${c.a})` : `rgb(${c.r}, ${c.g}, ${c.b})`],
        ["HSL", c.a < 1 ? `hsla(${h}, ${s}%, ${l}%, ${c.a})` : `hsl(${h}, ${s}%, ${l}%)`],
        ["CSS", `${c.r} ${c.g} ${c.b}`]]));
    }
    dessiner();
    return el("div", { class: "bo-deux" },
      el("div", {}, el("div", { class: "bo-ligne", style: "margin-bottom:12px" }, selecteur, champ), el("div", { class: "bo-pastille" }, pastille)),
      resultat);
  }

  VUES.boite = { afficher, titre: "Boîte à outils", icone: icone("flask-conical"), groupe: "outils", ordre: 10 };
})();
