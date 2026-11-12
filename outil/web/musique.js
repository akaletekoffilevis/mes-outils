"use strict";
/* Onglet « Musique » : lecteur audio local (fichiers sur ce PC). */
(() => {
  I18N.ajouter({
    "Musique": "Music",
    "Lecteur audio local": "Local audio player",
    "Aucune piste pour l'instant.": "No tracks yet.",
    "Ajoutez des fichiers audio (mp3, wav, ogg, m4a, flac…)": "Add audio files (mp3, wav, ogg, m4a, flac…)",
    "Ajouter des fichiers": "Add files",
    "Lecture": "Play",
    "Pause": "Pause",
    "Précédent": "Previous",
    "Suivant": "Next",
    "Volume": "Volume",
    "Supprimer cette piste ?": "Delete this track?",
    "Supprimer": "Delete",
    "Piste supprimée": "Track deleted",
    "Aucune piste à lire.": "No track to play.",
    "Lecture impossible.": "Cannot play.",
  });

  const M = { pistes: [], index: -1, enLecture: false, audio: null };

  const style = document.createElement("style");
  style.textContent = `
    .musique { display: flex; flex-direction: column; gap: 16px; }
    .musique-lecture { background: var(--carte); border: 1px solid var(--ligne); border-radius: var(--rayon); box-shadow: var(--ombre); padding: 20px; }
    .musique-titre { font-size: 18px; font-weight: 600; letter-spacing: -.01em; margin: 0 0 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .musique-artiste { color: var(--doux); font-size: 13px; margin: 0 0 14px; }
    .musique-progression { width: 100%; height: 6px; border-radius: 3px; background: var(--surface); overflow: hidden; cursor: pointer; margin-bottom: 6px; }
    .musique-progression .barre { height: 100%; background: var(--violet); border-radius: 3px; width: 0%; transition: width .1s linear; }
    .musique-temps { display: flex; justify-content: space-between; font-size: 11.5px; color: var(--doux); font-variant-numeric: tabular-nums; margin-bottom: 14px; }
    .musique-controles { display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 14px; }
    .musique-controles button { width: 40px; height: 40px; border-radius: 50%; border: 0; background: var(--surface); color: var(--encre); cursor: pointer; display: grid; place-items: center; transition: background .12s, transform .12s var(--ressort); }
    .musique-controles button:hover { background: var(--ligne); }
    .musique-controles button:active { transform: scale(.94); }
    .musique-controles button.principal { width: 52px; height: 52px; background: var(--violet); color: var(--sur-violet); }
    .musique-controles button.principal:hover { background: var(--violet-2); }
    .musique-volume { display: flex; align-items: center; gap: 10px; }
    .musique-volume input { flex: 1; }
    .musique-liste { background: var(--carte); border: 1px solid var(--ligne); border-radius: var(--rayon); box-shadow: var(--ombre); overflow: hidden; }
    .musique-ligne { display: flex; align-items: center; gap: 12px; padding: 10px 14px; border-top: 1px solid var(--ligne); cursor: pointer; transition: background .12s; }
    .musique-liste > .musique-ligne:first-child { border-top: 0; }
    .musique-ligne:hover { background: var(--surface); }
    .musique-ligne.actif { background: var(--violet-clair); }
    .musique-ligne .numero { width: 22px; text-align: center; color: var(--gris); font-size: 12px; font-variant-numeric: tabular-nums; flex: none; }
    .musique-ligne .titre { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-weight: 500; }
    .musique-ligne .suppr { opacity: 0; transition: opacity .1s; }
    .musique-ligne:hover .suppr { opacity: 1; }
    .musique-vide { padding: 32px 20px; text-align: center; color: var(--doux); }
  `;
  document.head.append(style);

  // Élément audio unique, caché.
  const audio = document.createElement("audio");
  audio.preload = "metadata";
  audio.style.display = "none";
  document.body.append(audio);
  M.audio = audio;

  function formaterTemps(s) {
    if (!isFinite(s) || s < 0) return "0:00";
    const m = Math.floor(s / 60), sec = Math.floor(s % 60);
    return `${m}:${String(sec).padStart(2, "0")}`;
  }

  async function charger() {
    try { const r = await api("/api/musique/lister", {}); M.pistes = r.pistes || []; } catch (e) { M.pistes = []; toast("😕 " + e.message, "erreur"); }
    if (M.index >= M.pistes.length) M.index = M.pistes.length ? 0 : -1;
    dessiner();
  }

  function pisteCourante() { return M.index >= 0 && M.index < M.pistes.length ? M.pistes[M.index] : null; }

  function jouer(index) {
    if (index === undefined) index = M.index;
    if (index < 0 || index >= M.pistes.length) { toast(t("Aucune piste à lire."), "erreur"); return; }
    M.index = index;
    const p = M.pistes[index];
    audio.src = `/fichier/musique?chemin=${encodeURIComponent(p.chemin)}`;
    audio.play().then(() => { M.enLecture = true; dessiner(); }).catch(() => toast(t("Lecture impossible."), "erreur"));
    dessiner();
  }

  function pause() {
    audio.pause();
    M.enLecture = false;
    dessiner();
  }

  function basculer() {
    if (M.enLecture) pause(); else {
      if (M.index < 0 && M.pistes.length) jouer(0);
      else if (pisteCourante()) { audio.play().then(() => { M.enLecture = true; dessiner(); }).catch(() => toast(t("Lecture impossible."), "erreur")); }
    }
  }

  function suivant() { if (!M.pistes.length) return; jouer((M.index + 1) % M.pistes.length); }
  function precedent() { if (!M.pistes.length) return; jouer((M.index - 1 + M.pistes.length) % M.pistes.length); }

  async function ajouter() {
    const chemins = await choisirFichiers("Choisir des fichiers audio", "", true, "Audio (*.mp3;*.wav;*.ogg;*.m4a;*.flac;*.aac;*.opus)|*.mp3;*.wav;*.ogg;*.m4a;*.flac;*.aac;*.opus");
    if (!chemins || !chemins.length) return;
    for (const c of chemins) {
      try { await api("/api/musique/ajouter", { chemin: c }); } catch (e) { toast("😕 " + e.message, "erreur"); }
    }
    await charger();
  }

  async function supprimer(id) {
    if (!(await confirmer(icone("trash-2"), t("Supprimer cette piste ?"), "", "Supprimer"))) return;
    try { await api("/api/musique/supprimer", { id }); toast(t("Piste supprimée"), "succes", 1500); } catch (e) { toast("😕 " + e.message, "erreur"); }
    await charger();
  }

  async function vider() {
    if (!M.pistes.length) return;
    if (!(await confirmer(icone("trash-2"), "Vider la playlist ?", "Toutes les pistes sont retirées (les fichiers restent sur le PC).", "Vider"))) return;
    try { await api("/api/musique/vider", {}); } catch (e) { toast("😕 " + e.message, "erreur"); }
    await charger();
  }

  audio.addEventListener("timeupdate", () => {
    const p = pisteCourante();
    if (!p) return;
    const pct = audio.duration ? (audio.currentTime / audio.duration * 100) : 0;
    const barre = $("#musique-barre");
    if (barre) barre.style.width = pct + "%";
    const t1 = $("#musique-temps-courant"), t2 = $("#musique-temps-total");
    if (t1) t1.textContent = formaterTemps(audio.currentTime);
    if (t2) t2.textContent = formaterTemps(audio.duration);
  });
  audio.addEventListener("ended", () => suivant());
  audio.addEventListener("loadedmetadata", () => {
    const t2 = $("#musique-temps-total");
    if (t2) t2.textContent = formaterTemps(audio.duration);
  });

  function dessiner() {
    const p = pisteCourante();
    const titre = p ? p.titre : t("Aucune piste pour l'instant.");
    const progression = el("div", { class: "musique-progression", onclick: e => {
      if (!audio.duration) return;
      const r = e.currentTarget.getBoundingClientRect();
      audio.currentTime = (e.clientX - r.left) / r.width * audio.duration;
    } }, el("div", { class: "barre", id: "musique-barre" }));
    const controles = el("div", { class: "musique-controles" },
      el("button", { title: t("Précédent"), onclick: precedent }, icone("chevron-left")),
      el("button", { class: "principal", title: M.enLecture ? t("Pause") : t("Lecture"), onclick: basculer }, icone(M.enLecture ? "pause" : "play")),
      el("button", { title: t("Suivant"), onclick: suivant }, icone("skip-forward")));
    const volume = el("div", { class: "musique-volume" },
      el("span", {}, icone("circle-plus")),  // placeholder icon for volume
      el("input", { type: "range", min: 0, max: 1, step: 0.01, value: audio.volume, oninput: e => { audio.volume = Number(e.target.value); } }));
    const liste = M.pistes.length
      ? el("div", { class: "musique-liste" }, M.pistes.map((p, i) =>
          el("div", { class: "musique-ligne" + (i === M.index ? " actif" : ""), onclick: () => jouer(i) },
            el("span", { class: "numero" }, String(i + 1)),
            el("span", { class: "titre" }, p.titre),
            el("button", { class: "icone-btn suppr", title: "Supprimer", onclick: e => { e.stopPropagation(); supprimer(p.id); } }, icone("trash-2")))))
      : el("div", { class: "musique-vide" },
          el("div", {}, icone("music")), el("p", {}, t("Aucune piste pour l'instant.")), el("p", { class: "aide" }, t("Ajoutez des fichiers audio (mp3, wav, ogg, m4a, flac…)")));

    $("#vue-musique").replaceChildren(
      el("div", { class: "barre-vue" }, el("h2", {}, icone("music"), " " + t("Musique")), el("span", { class: "espace" }),
        el("button", { class: "btn", onclick: ajouter }, icone("plus"), " " + t("Ajouter des fichiers")),
        M.pistes.length ? el("button", { class: "btn discret", onclick: vider }, "Vider") : null),
      el("div", { class: "musique" },
        el("div", { class: "musique-lecture" },
          el("h3", { class: "musique-titre" }, titre),
          el("p", { class: "musique-artiste" }, p ? p.chemin : ""),
          progression,
          el("div", { class: "musique-temps" }, el("span", { id: "musique-temps-courant" }, "0:00"), el("span", { id: "musique-temps-total" }, "0:00")),
          controles,
          volume),
        liste));
  }

  // On démarre sans piste.
  M.audio.volume = 0.7;

  VUES.musique = { afficher: () => charger(), titre: "Musique", icone: "music", groupe: "outils", ordre: 10,
    description: "Lecteur audio local : fichiers, playlist, play, pause, volume.",
    profils: ["developpeur", "freelance", "assistant_virtuel", "assistant_direction"] };
})();
EOF