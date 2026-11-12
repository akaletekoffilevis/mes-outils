"use strict";
/* Onglet « Vidéo » : visionneuse locale (fichiers sur ce PC). */
(() => {
  I18N.ajouter({
    "Vidéo": "Video",
    "Visionneuse locale": "Local video player",
    "Aucune vidéo pour l'instant.": "No videos yet.",
    "Ajoutez des fichiers vidéo (mp4, webm, ogg, mov, avi, mkv, m4v…)": "Add video files (mp4, webm, ogg, mov, avi, mkv, m4v…)",
    "Ajouter des fichiers": "Add files",
    "Lecture": "Play",
    "Pause": "Pause",
    "Précédent": "Previous",
    "Suivant": "Next",
    "Volume": "Volume",
    "Supprimer cette vidéo ?": "Delete this video?",
    "Supprimer": "Delete",
    "Vidéo supprimée": "Video deleted",
    "Aucune vidéo à lire.": "No video to play.",
    "Lecture impossible.": "Cannot play.",
    "Plein écran": "Fullscreen",
  });

  const V = { videos: [], index: -1, enLecture: false, video: null, volume: 0.7 };

  const style = document.createElement("style");
  style.textContent = `
    .video { display: flex; flex-direction: column; gap: 16px; }
    .video-lecture { background: var(--carte); border: 1px solid var(--ligne); border-radius: var(--rayon); box-shadow: var(--ombre); padding: 16px; }
    .video-element { width: 100%; max-height: 60vh; background: #000; border-radius: 8px; display: block; }
    .video-titre { font-size: 16px; font-weight: 600; letter-spacing: -.01em; margin: 12px 0 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .video-chemin { color: var(--doux); font-size: 12px; margin: 0 0 10px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .video-progression { width: 100%; height: 6px; border-radius: 3px; background: var(--surface); overflow: hidden; cursor: pointer; margin-bottom: 6px; }
    .video-progression .barre { height: 100%; background: var(--violet); border-radius: 3px; width: 0%; transition: width .1s linear; }
    .video-temps { display: flex; justify-content: space-between; font-size: 11.5px; color: var(--doux); font-variant-numeric: tabular-nums; margin-bottom: 12px; }
    .video-controles { display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 12px; }
    .video-controles button { width: 40px; height: 40px; border-radius: 50%; border: 0; background: var(--surface); color: var(--encre); cursor: pointer; display: grid; place-items: center; transition: background .12s, transform .12s var(--ressort); }
    .video-controles button:hover { background: var(--ligne); }
    .video-controles button:active { transform: scale(.94); }
    .video-controles button.principal { width: 52px; height: 52px; background: var(--violet); color: var(--sur-violet); }
    .video-controles button.principal:hover { background: var(--violet-2); }
    .video-volume { display: flex; align-items: center; gap: 10px; }
    .video-volume input { flex: 1; }
    .video-liste { background: var(--carte); border: 1px solid var(--ligne); border-radius: var(--rayon); box-shadow: var(--ombre); overflow: hidden; }
    .video-ligne { display: flex; align-items: center; gap: 12px; padding: 10px 14px; border-top: 1px solid var(--ligne); cursor: pointer; transition: background .12s; }
    .video-liste > .video-ligne:first-child { border-top: 0; }
    .video-ligne:hover { background: var(--surface); }
    .video-ligne.actif { background: var(--violet-clair); }
    .video-ligne .numero { width: 22px; text-align: center; color: var(--gris); font-size: 12px; font-variant-numeric: tabular-nums; flex: none; }
    .video-ligne .titre { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-weight: 500; }
    .video-ligne .suppr { opacity: 0; transition: opacity .1s; }
    .video-ligne:hover .suppr { opacity: 1; }
    .video-vide { padding: 32px 20px; text-align: center; color: var(--doux); }
  `;
  document.head.append(style);

  function formaterTemps(s) {
    if (!isFinite(s) || s < 0) return "0:00";
    const m = Math.floor(s / 60), sec = Math.floor(s % 60);
    return `${m}:${String(sec).padStart(2, "0")}`;
  }

  // Élément vidéo unique, persistant (ne pas le recréer à chaque dessin).
  function creerVideo() {
    const v = document.createElement("video");
    v.className = "video-element";
    v.preload = "metadata";
    v.playsInline = true;
    v.addEventListener("timeupdate", () => {
      const pct = v.duration ? (v.currentTime / v.duration * 100) : 0;
      const barre = $("#video-barre");
      if (barre) barre.style.width = pct + "%";
      const t1 = $("#video-temps-courant"), t2 = $("#video-temps-total");
      if (t1) t1.textContent = formaterTemps(v.currentTime);
      if (t2) t2.textContent = formaterTemps(v.duration);
    });
    v.addEventListener("ended", () => suivant());
    v.addEventListener("loadedmetadata", () => {
      const t2 = $("#video-temps-total");
      if (t2) t2.textContent = formaterTemps(v.duration);
    });
    v.addEventListener("click", basculer);
    return v;
  }

  async function charger() {
    try { const r = await api("/api/video/lister", {}); V.videos = r.videos || []; } catch (e) { V.videos = []; toast("😕 " + e.message, "erreur"); }
    if (V.index >= V.videos.length) V.index = V.videos.length ? 0 : -1;
    dessiner();
  }

  function videoCourante() { return V.index >= 0 && V.index < V.videos.length ? V.videos[V.index] : null; }

  function jouer(index) {
    if (index === undefined) index = V.index;
    if (index < 0 || index >= V.videos.length) { toast(t("Aucune vidéo à lire."), "erreur"); return; }
    V.index = index;
    const v = V.videos[index];
    if (V.video) V.video.src = `/fichier/video?chemin=${encodeURIComponent(v.chemin)}`;
    if (V.video) V.video.play().then(() => { V.enLecture = true; dessiner(); }).catch(() => toast(t("Lecture impossible."), "erreur"));
    dessiner();
  }

  function pause() { if (V.video) V.video.pause(); V.enLecture = false; dessiner(); }

  function basculer() {
    if (V.enLecture) pause();
    else {
      if (V.index < 0 && V.videos.length) jouer(0);
      else if (videoCourante() && V.video) { V.video.play().then(() => { V.enLecture = true; dessiner(); }).catch(() => toast(t("Lecture impossible."), "erreur")); }
    }
  }

  function suivant() { if (!V.videos.length) return; jouer((V.index + 1) % V.videos.length); }
  function precedent() { if (!V.videos.length) return; jouer((V.index - 1 + V.videos.length) % V.videos.length); }

  async function ajouter() {
    const chemins = await choisirFichiers("Choisir des fichiers vidéo", "", true, "Vidéo (*.mp4;*.webm;*.ogg;*.mov;*.avi;*.mkv;*.m4v)|*.mp4;*.webm;*.ogg;*.mov;*.avi;*.mkv;*.m4v");
    if (!chemins || !chemins.length) return;
    for (const c of chemins) {
      try { await api("/api/video/ajouter", { chemin: c }); } catch (e) { toast("😕 " + e.message, "erreur"); }
    }
    await charger();
  }

  async function supprimer(id) {
    if (!(await confirmer(icone("trash-2"), t("Supprimer cette vidéo ?"), "", "Supprimer"))) return;
    try { await api("/api/video/supprimer", { id }); toast(t("Vidéo supprimée"), "succes", 1500); } catch (e) { toast("😕 " + e.message, "erreur"); }
    await charger();
  }

  async function vider() {
    if (!V.videos.length) return;
    if (!(await confirmer(icone("trash-2"), "Vider la liste ?", "Toutes les vidéos sont retirées (les fichiers restent sur le PC).", "Vider"))) return;
    try { await api("/api/video/vider", {}); } catch (e) { toast("😕 " + e.message, "erreur"); }
    await charger();
  }

  function pleinEcran() {
    if (!V.video) return;
    if (V.video.requestFullscreen) V.video.requestFullscreen();
    else if (V.video.webkitRequestFullscreen) V.video.webkitRequestFullscreen();
  }

  function dessiner() {
    const v = videoCourante();
    const titre = v ? v.titre : t("Aucune vidéo pour l'instant.");

    // Élément vidéo persistant (créé une fois, déplacé à chaque dessin).
    if (!V.video) {
      V.video = creerVideo();
      V.video.volume = V.volume;
    }
    // Mettre à jour la source si la vidéo courante a changé.
    const url = v ? `/fichier/video?chemin=${encodeURIComponent(v.chemin)}` : "";
    if (url && V.video.src !== new URL(url, location.href).href) {
      V.video.src = url;
    } else if (!url) {
      V.video.removeAttribute("src");
      V.video.load();
    }
    V.video.volume = V.volume;

    const progression = el("div", { class: "video-progression", onclick: e => {
      if (!V.video.duration) return;
      const r = e.currentTarget.getBoundingClientRect();
      V.video.currentTime = (e.clientX - r.left) / r.width * V.video.duration;
    } }, el("div", { class: "barre", id: "video-barre" }));
    const controles = el("div", { class: "video-controles" },
      el("button", { title: t("Précédent"), onclick: precedent }, icone("chevron-left")),
      el("button", { class: "principal", title: V.enLecture ? t("Pause") : t("Lecture"), onclick: basculer }, icone(V.enLecture ? "pause" : "play")),
      el("button", { title: t("Suivant"), onclick: suivant }, icone("skip-forward")),
      el("button", { title: t("Plein écran"), onclick: pleinEcran }, icone("external-link")));
    const volume = el("div", { class: "video-volume" },
      el("input", { type: "range", min: 0, max: 1, step: 0.01, value: V.volume, oninput: e => { V.volume = Number(e.target.value); if (V.video) V.video.volume = V.volume; } }));
    const liste = V.videos.length
      ? el("div", { class: "video-liste" }, V.videos.map((v, i) =>
          el("div", { class: "video-ligne" + (i === V.index ? " actif" : ""), onclick: () => jouer(i) },
            el("span", { class: "numero" }, String(i + 1)),
            el("span", { class: "titre" }, v.titre),
            el("button", { class: "icone-btn suppr", title: "Supprimer", onclick: e => { e.stopPropagation(); supprimer(v.id); } }, icone("trash-2")))))
      : el("div", { class: "video-vide" },
          el("div", {}, icone("video")), el("p", {}, t("Aucune vidéo pour l'instant.")), el("p", { class: "aide" }, t("Ajoutez des fichiers vidéo (mp4, webm, ogg, mov, avi, mkv, m4v…)")));

    const videoContainer = el("div", { class: "video-conteneur" });
    videoContainer.append(V.video);

    $("#vue-video").replaceChildren(
      el("div", { class: "barre-vue" }, el("h2", {}, icone("video"), " " + t("Vidéo")), el("span", { class: "espace" }),
        el("button", { class: "btn", onclick: ajouter }, icone("plus"), " " + t("Ajouter des fichiers")),
        V.videos.length ? el("button", { class: "btn discret", onclick: vider }, "Vider") : null),
      el("div", { class: "video" },
        videoContainer,
        el("h3", { class: "video-titre" }, titre),
        el("p", { class: "video-chemin" }, v ? v.chemin : ""),
        progression,
        el("div", { class: "video-temps" }, el("span", { id: "video-temps-courant" }, "0:00"), el("span", { id: "video-temps-total" }, "0:00")),
        controles,
        volume),
      liste);
  }

  VUES.video = { afficher: () => charger(), titre: "Vidéo", icone: "video", groupe: "outils", ordre: 20,
    description: "Visionneuse vidéo locale : fichiers, playlist, play, pause, volume.",
    profils: ["developpeur", "freelance", "assistant_virtuel", "assistant_direction"] };
})();
EOF