"use strict";
/* Onglet « Réglages » : prénom, langue, onglets affichés, dossiers de projets,
   raccourcis (Windows : Bureau et démarrage ; Linux : menu des applications,
   démarrage avec la session, bulle et icône), mise à jour (voir reglages.py). */
(() => {
  const R = { infos: null };

  I18N.ajouter({
    "Réglages": "Settings",
    "Profil": "Profile",
    "Prénom (pour la salutation)": "First name (for the greeting)",
    "ex. Marie": "e.g. Mary",
    "Langue": "Language",
    "Thème": "Theme",
    "Automatique": "Automatic",
    "Clair": "Light",
    "Sombre": "Dark",
    "Sépia": "Sepia",
    "Contrasté": "High contrast",
    "Accent": "Accent",
    "Violet": "Violet", "Bleu": "Blue", "Vert": "Green", "Corail": "Coral", "Rose": "Rose",
    "Densité": "Density", "Confortable": "Comfortable", "Compact": "Compact",
    "Vue par défaut des tâches": "Default task view", "Liste": "List", "Tableau": "Board",
    "Priorité par défaut des tâches": "Default task priority", "Basse": "Low", "Normale": "Normal", "Haute": "High",
    "Rappel par défaut de l'agenda": "Default agenda reminder", "Aucun": "None", "À l'heure": "At the time",
    "5 min": "5 min", "15 min": "15 min", "30 min": "30 min", "1 h": "1 h", "La veille": "The day before",
    "Onglets affichés": "Visible tabs",
    "Choisissez les applications du menu, comme dans un ERP : les autres disparaissent, leurs données restent.":
      "Choose the apps in the menu, like in an ERP: the others leave, their data stays.",
    "Choisir mes applications": "Choose my apps",
    "Décochez les onglets dont vous ne vous servez pas : ils disparaissent du menu (rien n'est effacé).":
      "Untick the tabs you don't use: they disappear from the menu (nothing is deleted).",
    "Dossiers de projets": "Project folders",
    "Les onglets GitHub, Projets et État Git y cherchent vos projets (le dossier et ses sous-dossiers directs).":
      "The GitHub, Projects and Git status tabs look for your projects there (the folder and its direct subfolders).",
    "＋ Ajouter un dossier": "＋ Add a folder",
    "Aucun dossier pour l'instant.": "No folder yet.",
    "Retirer": "Remove",
    "Windows": "Windows",
    "Lancer la bulle au démarrage de Windows": "Start the bubble with Windows",
    "Raccourci « Mes outils » sur le Bureau": "“Mes outils” shortcut on the Desktop",
    "Boîte mail": "Mailbox",
    "La boîte mail se connecte dans l'onglet Mails.": "The mailbox is connected in the Mails tab.",
    "Ouvrir l'onglet Mails": "Open the Mails tab",
    "À propos": "About",
    "Version {v}": "Version {v}",
    " Code source sur GitHub": " Source code on GitHub",
    " Rechercher une mise à jour": " Check for updates",
    "Recherche…": "Checking…",
    " Mis à jour : la page va se recharger": " Updated: the page will reload",
    "Déjà à jour ": "Already up to date ",
    "Enregistré": "Saved",
    "Choisir un dossier de projets": "Choose a projects folder",
    "Version {v} disponible": "Version {v} available",
    "Installer maintenant ? Mes outils se ferme quelques secondes puis redémarre tout seul. Vos réglages et vos données sont gardés.":
      "Install now? Mes outils closes for a few seconds, then restarts by itself. Your settings and data are kept.",
    "Installer": "Install",
    "Téléchargement de la version {v}…": "Downloading version {v}…",
    "Mise à jour de Mes outils": "Updating Mes outils",
    "Installation en cours : Mes outils redémarre tout seul, cette page se rechargera.": "Installing: Mes outils restarts by itself, this page will reload.",
    " Version {v} installée": " Version {v} installed",
    "La mise à jour prend du temps : relancez Mes outils depuis son raccourci.": "The update is taking a while: restart Mes outils from its shortcut.",
    "Téléchargement de la mise à jour impossible (Internet ?).": "Unable to download the update (Internet?).",
    "Installateur introuvable dans la dernière version publiée.": "Installer not found in the latest release.",
    "Le fichier téléchargé n'est pas un installateur valide.": "The downloaded file is not a valid installer.",
    "Télécharger le nouvel installateur ? Fermez la bulle (clic droit › Quitter), puis lancez-le : vos réglages et vos données sont gardés.":
      "Download the new installer? Close the bubble (right-click › Quit), then run it: your settings and data are kept.",
    "Télécharger": "Download",
    "Aucune version publiée pour l'instant.": "No version published yet.",
    "Pas de connexion à GitHub (Internet ?).": "No connection to GitHub (Internet?).",
    "Relancez la bulle (clic droit › Quitter, puis le raccourci) pour finir la mise à jour.":
      "Restart the bubble (right-click › Quit, then the shortcut) to finish the update.",
    // Linux
    "Linux": "Linux",
    "Lancer Mes outils à l'ouverture de session": "Start Mes outils when I log in",
    "Mes outils dans le menu des applications": "Mes outils in the applications menu",
    "Affichage": "Display",
    "Bulle et icône": "Bubble and icon",
    "Bulle seule": "Bubble only",
    "Icône seule": "Icon only",
    "L'icône s'affiche en haut à droite de l'écran ; son menu reprend celui de la bulle.":
      "The icon appears at the top right of the screen; its menu matches the bubble's.",
    "L'icône n'est pas disponible sur ce bureau : la bulle reste affichée.":
      "The icon is not available on this desktop: the bubble stays visible.",
    "Télécharger la nouvelle AppImage ? Quittez la bulle (clic droit › Quitter la bulle), rendez le fichier exécutable (Propriétés › Exécutable comme un programme), puis lancez-le : vos réglages et vos données sont gardés.":
      "Download the new AppImage? Quit the bubble (right-click › Quit the bubble), make the file executable (Properties › Executable as program), then run it: your settings and data are kept.",
    "La mise à jour prend du temps : relancez Mes outils depuis le menu des applications.":
      "The update is taking a while: restart Mes outils from the applications menu.",
    "AppImage introuvable dans la dernière version publiée.": "AppImage not found in the latest release.",
    "Le fichier téléchargé n'est pas une AppImage valide.": "The downloaded file is not a valid AppImage.",
    "Installation automatique réservée au programme installé (AppImage).": "Automatic installation is only for the installed program (AppImage).",
    "Installation automatique réservée au programme installé (Setup.exe).": "Automatic installation is only for the installed program (Setup.exe).",
    "Affichage inconnu.": "Unknown display mode.",
    "Notifications": "Notifications",
    "Raccourcis clavier": "Keyboard shortcuts",
    "Les raccourcis disponibles dans l'application.": "Available shortcuts in the application.",
    "Relances (contacts)": "Follow-ups (contacts)",
    "Budget dépassé": "Budget exceeded",
    "Documents qui expirent": "Expiring documents",
    "Échéances": "Deadlines",
    "Factures en retard": "Overdue invoices",
    "Tâches à l'heure": "Tasks on time",
    "Pomodoro": "Pomodoro",
    "Réunions": "Meetings",
  });

  const style = document.createElement("style");
  style.textContent = `
    .reglages { display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 16px; align-items: start; }
    .carte-reg { background: var(--carte); border: 1px solid var(--bord); border-radius: var(--rayon); box-shadow: var(--ombre); padding: 18px 20px; animation: apparait .35s both; }
    .carte-reg h3 { margin: 0 0 12px; font-size: 16px; display: flex; gap: 8px; align-items: center; }
    .carte-reg p.aide { color: var(--doux); font-size: 13px; margin: -4px 0 12px; }
    .cases-reg { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 4px 12px; }
    .case-reg { display: flex; align-items: center; gap: 8px; padding: 5px 4px; border-radius: 10px; cursor: pointer; font-weight: 600; font-size: 14px; }
    .case-reg:hover { background: var(--surface); }
    .case-reg input { width: 17px; height: 17px; accent-color: var(--violet); flex: none; }
    .liste-reg { display: flex; flex-direction: column; gap: 6px; margin-bottom: 10px; }
    .liste-reg div { display: flex; align-items: center; gap: 8px; background: var(--surface); border-radius: 12px; padding: 7px 10px; font-size: 14px; }
    .liste-reg div span { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .langues-reg { display: flex; gap: 8px; flex-wrap: wrap; }
  `;
  document.head.append(style);

  async function charger() {
    R.infos = await api("/api/reglages/lire", {});
    dessiner();
  }

  async function enregistrer(valeurs, recharger = false) {
    try {
      R.infos = await api("/api/reglages/enregistrer", valeurs);
      toast(t("Enregistré"), "succes", 1400);
      if (recharger) setTimeout(() => location.reload(), 500);
      else {
        S.masques = R.infos.onglets_masques;
        if (S.config && "prenom" in valeurs) { S.config.prenom = R.infos.prenom; horloge(); }
        construireMenu();
      }
    } catch (e) { toast(e.message, "erreur"); }
  }

  function carte(icone, titre, ...contenu) {
    return el("div", { class: "carte-reg" }, el("h3", {}, icone + t(titre)), ...contenu);
  }

  function dessiner() {
    const i = R.infos;
    const prenom = el("input", { value: i.prenom, placeholder: "ex. Marie", maxlength: 40 });
    let minuterie;
    prenom.addEventListener("input", () => { clearTimeout(minuterie); minuterie = setTimeout(() => enregistrer({ prenom: prenom.value }), 700); });

    const langues = el("div", { class: "langues-reg" }, [["fr", "Français"], ["en", "English"]].map(([code, nom]) =>
      el("button", { class: "btn " + (i.langue === code ? " actif" : ""), onclick: () => { if (code !== i.langue) enregistrer({ langue: code }, true); } }, nom)));

    const themes = el("div", { class: "langues-reg" }, [["auto", "Automatique"], ["clair", "Clair"], ["sombre", "Sombre"], ["sepia", "Sépia"], ["contraste", "Contrasté"]].map(([code, nom]) =>
      el("button", { class: "btn " + (S.theme === code ? " actif" : ""), onclick: async () => { await changerTheme(code); dessiner(); } }, icone(ICONES_THEMES[code]), t(nom))));
    const COULEURS_ACCENT = { violet: "#5b5bd6", bleu: "#2f7ae5", vert: "#12a37a", corail: "#e5603e", rose: "#d6457a" };
    const accents = el("div", { class: "langues-reg" }, [["violet", "Violet"], ["bleu", "Bleu"], ["vert", "Vert"], ["corail", "Corail"], ["rose", "Rose"]].map(([code, nom]) =>
      el("button", { class: "btn " + (S.accent === code ? " actif" : ""), onclick: async () => { await changerAccent(code); dessiner(); } },
        el("span", { style: `background:${COULEURS_ACCENT[code]}; width:14px; height:14px; border-radius:50%; display:inline-block; border:2px solid var(--carte); box-shadow:0 0 0 1px var(--ligne)` }),
        t(nom))));
    const densites = el("div", { class: "langues-reg" }, [["confortable", "Confortable"], ["compact", "Compact"]].map(([code, nom]) =>
      el("button", { class: "btn " + (S.densite === code ? " actif" : ""), onclick: async () => { await changerDensite(code); dessiner(); } }, t(nom))));
    const vuesTaches = el("div", { class: "langues-reg" }, [["liste", "Liste"], ["tableau", "Tableau"]].map(([code, nom]) =>
      el("button", { class: "btn " + (S.config?.vue_taches === code ? " actif" : ""), onclick: async () => {
        await enregistrer({ vue_taches: code }); dessiner();
      } }, t(nom))));
    const prioritesTaches = el("div", { class: "langues-reg" }, [["basse", "Basse"], ["normale", "Normale"], ["haute", "Haute"]].map(([code, nom]) =>
      el("button", { class: "btn " + (S.config?.priorite_taches === code ? " actif" : ""), onclick: async () => {
        await enregistrer({ priorite_taches: code }); dessiner();
      } }, t(nom))));
    const rappelsAgenda = el("div", { class: "langues-reg" }, [["", "Aucun"], ["0", "À l'heure"], ["5", "5 min"], ["15", "15 min"], ["30", "30 min"], ["60", "1 h"], ["1440", "La veille"]].map(([code, nom]) =>
      el("button", { class: "btn " + (String(S.config?.rappel_agenda ?? "15") === code ? " actif" : ""), onclick: async () => {
        await enregistrer({ rappel_agenda: code }); dessiner();
      } }, t(nom))));

    const masques = new Set(i.onglets_masques);
    const onglets = listeOnglets().filter(o => o.nom !== "accueil" && o.nom !== "reglages")
      .sort((a, b) => (Object.keys(GROUPES).indexOf(a.groupe) - Object.keys(GROUPES).indexOf(b.groupe)) || ((a.ordre ?? 99) - (b.ordre ?? 99)));
    const cases = el("div", { class: "cases-reg" }, onglets.map(o =>
      el("label", { class: "case-reg" },
        el("input", { type: "checkbox", checked: masques.has(o.nom) ? null : "", onchange: e => {
          if (e.target.checked) masques.delete(o.nom); else masques.add(o.nom);
          enregistrer({ onglets_masques: [...masques] });
        } }), iconeOnglet(o.icone), I18N.traduire(o.titre))));

    const listeDossiers = el("div", { class: "liste-reg" },
      i.dossiers_projets.length ? i.dossiers_projets.map(d => el("div", {}, icone("folder"), el("span", { title: d }, d),
        el("button", { class: "icone-btn", title: "Retirer", onclick: () => majDossiers(i.dossiers_projets.filter(x => x !== d)) }, icone("x"))))
        : el("div", { style: "color:var(--doux)" }, "Aucun dossier pour l'instant."));
    const ajoutDossier = el("button", { class: "btn", onclick: async () => {
      const chemin = await choisirDossier("Choisir un dossier de projets");
      if (chemin) majDossiers([...i.dossiers_projets, chemin]);
    } }, "＋ Ajouter un dossier");

    const interrupteur = (genre, texte) => el("label", { class: "case-reg" },
      el("input", { type: "checkbox", checked: i.raccourcis[genre] ? "" : null, onchange: async e => {
        try { R.infos = await api("/api/reglages/raccourci", { genre, actif: e.target.checked }); toast(t("Enregistré"), "succes", 1400); }
        catch (err) { e.target.checked = !e.target.checked; toast(err.message, "erreur"); }
      } }), texte);

    const majBtn = el("button", { class: "btn", onclick: async () => {
      majBtn.disabled = true; majBtn.textContent = t("Recherche…");
      try {
        const r = await api("/api/reglages/mise_a_jour", {});
        if (r.nouvelle && r.automatique) {
          // Programme installé : téléchargement, installation et redémarrage
          // tout seuls ; réglages et données gardés.
          if (await confirmer("", t("Version {v} disponible", { v: r.nouvelle }),
              t("Installer maintenant ? Mes outils se ferme quelques secondes puis redémarre tout seul. Vos réglages et vos données sont gardés."), "Installer")) {
            await installerMiseAJour(r.nouvelle);
          }
        } else if (r.nouvelle) {
          // Copie sans installateur (ou AppImage lancée autrement) : on ouvre
          // la page de téléchargement.
          const texte = i.systeme === "linux"
            ? "Télécharger la nouvelle AppImage ? Quittez la bulle (clic droit › Quitter la bulle), rendez le fichier exécutable (Propriétés › Exécutable comme un programme), puis lancez-le : vos réglages et vos données sont gardés."
            : "Télécharger le nouvel installateur ? Fermez la bulle (clic droit › Quitter), puis lancez-le : vos réglages et vos données sont gardés.";
          if (await confirmer("", t("Version {v} disponible", { v: r.nouvelle }), t(texte), "Télécharger")) {
            await api("/api/github/ouvrir_page", { url: r.telecharger });
          }
        } else if (r.change) { toast(t(" Mis à jour : la page va se recharger"), "succes", 3000); toast(t("Relancez la bulle (clic droit › Quitter, puis le raccourci) pour finir la mise à jour."), "", 9000); setTimeout(() => location.reload(), 2500); }
        else toast(t("Déjà à jour "), "succes");
      } catch (e) { toast(e.message, "erreur", 7000); }
      finally { majBtn.disabled = false; majBtn.textContent = t(" Rechercher une mise à jour"); }
    } }, " Rechercher une mise à jour");

    $("#vue-reglages").replaceChildren(
      el("div", { class: "barre-vue" }, el("h2", {}, t("Réglages"))),
      el("div", { class: "reglages" },
        carte(icone("user"), "Profil",
          el("label", { class: "champ" }, "Prénom (pour la salutation)", prenom),
          el("label", { class: "champ" }, "Langue", langues),
          el("label", { class: "champ" }, "Thème", themes),
          el("label", { class: "champ" }, "Accent", accents),
          el("label", { class: "champ" }, "Densité", densites),
          el("label", { class: "champ" }, "Vue par défaut des tâches", vuesTaches),
          el("label", { class: "champ" }, "Priorité par défaut des tâches", prioritesTaches),
          el("label", { class: "champ" }, "Rappel par défaut de l'agenda", rappelsAgenda),
          el("label", { class: "champ" }, "Accent", accents)),
        carte("", "Applications", el("p", { class: "aide" }, "Choisissez les applications du menu, comme dans un ERP : les autres disparaissent, leurs données restent."),
          i.profil && PROFILS[i.profil] ? el("p", { class: "aide" }, t("Votre métier : {p}", { p: t(PROFILS[i.profil].titre) })) : null,
          el("button", { class: "btn", onclick: () => montrerVue("applications") }, "Choisir mes applications")),
        carte("", "Notifications", el("p", { class: "aide" }, "Choisissez les applications qui peuvent vous envoyer des rappels par la bulle."),
          el("div", { class: "cases-reg" }, [
            ["contacts", "Relances (contacts)"],
            ["depenses", "Budget dépassé"],
            ["documents", "Documents qui expirent"],
            ["echeances", "Échéances"],
            ["factures", "Factures en retard"],
            ["taches", "Tâches à l'heure"],
            ["temps", "Pomodoro"],
            ["reunions", "Réunions"],
          ].map(([nom, libelle]) => {
            const desactivees = new Set(i.notifications_desactivees || []);
            const actif = !desactivees.has(nom);
            return el("label", { class: "case-reg" },
              el("input", { type: "checkbox", checked: actif ? "" : null, onchange: async e => {
                const desac = new Set(i.notifications_desactivees || []);
                if (e.target.checked) desac.delete(nom); else desac.add(nom);
                await enregistrer({ notifications_desactivees: [...desac] });
              } }), libelle);
          }))),
        carte(icone("folder"), "Dossiers de projets", el("p", { class: "aide" }, "Les onglets GitHub, Projets et État Git y cherchent vos projets (le dossier et ses sous-dossiers directs)."),
          listeDossiers, ajoutDossier),
        i.systeme === "linux" ? carteLinux(i, interrupteur)
          : carte(icone("laptop"), "Windows", interrupteur("demarrage", "Lancer la bulle au démarrage de Windows"),
            interrupteur("bureau", "Raccourci « Mes outils » sur le Bureau")),
        carte(icone("mail"), "Boîte mail", el("p", { class: "aide" }, "La boîte mail se connecte dans l'onglet Mails."),
          el("button", { class: "btn", onclick: () => montrerVue("mails") }, "Ouvrir l'onglet Mails")),
        carte("", "Raccourcis clavier", el("p", { class: "aide" }, "Les raccourcis disponibles dans l'application."),
          el("div", { class: "liste-reg" },
            el("div", {}, el("span", {}, "Ctrl + K"), el("span", {}, "Palette de commandes (aller à un onglet, lancer un outil, une action)")),
            el("div", {}, el("span", {}, "Ctrl + Entrée"), el("span", {}, "Valider dans une fenêtre")),
            el("div", {}, el("span", {}, "Échap"), el("span", {}, "Fermer la fenêtre / la palette")),
            el("div", {}, el("span", {}, "↑ / ↓"), el("span", {}, "Naviguer dans la palette")),
            el("div", {}, el("span", {}, "Entrée"), el("span", {}, "Ouvrir l'élément sélectionné")),
            el("div", {}, el("span", {}, "Ctrl + glisser"), el("span", {}, "Dupliquer un rendez-vous (Agenda)")),
            el("div", {}, el("span", {}, "Glisser-déposer"), el("span", {}, "Réorganiser les tuiles, le menu, les notes, les contacts")))),
        carte(icone("wrench"), "À propos", el("p", { class: "aide" }, t("Version {v}", { v: i.version })),
          el("div", { style: "display:flex;gap:8px;flex-wrap:wrap" },
            el("button", { class: "btn", onclick: () => api("/api/github/ouvrir_page", { url: i.depot }).catch(e => toast(e.message, "erreur")) }, " Code source sur GitHub"),
            majBtn))));
  }

  /** Linux : démarrage avec la session, entrée du menu des applications,
      bulle et icône en haut à droite de l'écran. */
  function carteLinux(i, interrupteur) {
    const presences = el("div", { class: "langues-reg" }, [["bulle_icone", "Bulle et icône"], ["bulle", "Bulle seule"], ["icone", "Icône seule"]]
      .map(([code, nom]) => el("button", {
        class: "btn " + (i.presence === code ? " actif" : ""),
        disabled: !i.icone_possible && code !== "bulle" ? "" : null,
        onclick: async () => { if (code !== i.presence) { await enregistrer({ presence: code }); dessiner(); } },
      }, nom)));
    return carte(icone("laptop"), "Linux",
      interrupteur("demarrage", "Lancer Mes outils à l'ouverture de session"),
      interrupteur("menu", "Mes outils dans le menu des applications"),
      el("label", { class: "champ" }, "Affichage", presences),
      el("p", { class: "aide" }, i.icone_possible
        ? "L'icône s'affiche en haut à droite de l'écran ; son menu reprend celui de la bulle."
        : "L'icône n'est pas disponible sur ce bureau : la bulle reste affichée."));
  }

  /** Lance la mise à jour, puis attend que la nouvelle version réponde. */
  async function installerMiseAJour(version) {
    const etat = el("p", {}, t("Téléchargement de la version {v}…", { v: version }));
    fenetre([el("div", { class: "gros" }, icone("loader")), el("h3", {}, t("Mise à jour de Mes outils")), etat], true);
    let r;
    try { r = await api("/api/reglages/installer_mise_a_jour", {}); }
    catch (e) { fermer(); toast(e.message, "erreur", 8000); return; }
    if (r.a_jour) { fermer(); toast(t("Déjà à jour "), "succes"); return; }
    etat.textContent = t("Installation en cours : Mes outils redémarre tout seul, cette page se rechargera.");
    const debut = Date.now();
    const attendre = async () => {
      try {
        const infos = await api("/api/reglages/lire", {});
        if (infos.version === version) { etat.textContent = t(" Version {v} installée", { v: version }); setTimeout(() => location.reload(), 1200); return; }
      } catch { /* Mes outils est en train de redémarrer */ }
      if (Date.now() - debut > 180000) {
        etat.textContent = t(R.infos && R.infos.systeme === "linux"
          ? "La mise à jour prend du temps : relancez Mes outils depuis le menu des applications."
          : "La mise à jour prend du temps : relancez Mes outils depuis son raccourci.");
        return;
      }
      setTimeout(attendre, 2000);
    };
    setTimeout(attendre, 4000);
  }

  async function majDossiers(liste) {
    try { R.infos = await api("/api/reglages/dossiers", { dossiers: liste }); dessiner(); toast(t("Enregistré"), "succes", 1400); }
    catch (e) { toast(e.message, "erreur"); }
  }

  VUES.reglages = { afficher: () => charger().catch(e => toast(e.message, "erreur")),
    titre: "Réglages", icone: icone("settings"), groupe: "systeme", ordre: 90 };
})();
