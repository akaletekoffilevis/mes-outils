# Écrire une application pour « Mes outils »

Une application (un onglet) = jusqu'à trois fichiers, sans toucher au reste :

| Fichier | Rôle |
|---|---|
| `outil/<nom>.py` | le travail côté PC (facultatif) |
| `outil/web/<nom>.js` | l'onglet dans la page |
| `tests/test_<nom>.py` | les tests |

`<nom>` : minuscules, chiffres, `_` (ex. `projets`, `ports`). Le même nom
partout.

## Côté PC : `outil/<nom>.py`

Le serveur (`hub.py`) trouve tout seul le module : chaque fonction listée dans
`ROUTES` répond sur `POST /api/<nom>/<action>`.

```python
import config

def lister(d):          # d = le JSON envoyé par la page (dict)
    return {"elements": config.lire_donnees("<nom>")}

ROUTES = {"liste": lister, "dossier/ouvrir": ouvrir}
```

Règles :

- **Ne jamais importer `hub`** (il peut tourner sous le nom `__main__`).
- Réglages : `config.lire()`, `config.section("<nom>")`,
  `config.modifier_section("<nom>", cle=valeur)`,
  `config.dossiers_projets()`.
- Données : `config.lire_donnees("<nom>", defaut)` et
  `config.ecrire_donnees("<nom>", valeur)` (fichier `donnees/<nom>.json`,
  écriture sûre, copie `.bak`).
- Erreur pour l'utilisateur : `raise ValueError("message en français")`, ou une
  classe `Erreur<Quelque chose>(Exception)` → réponse 400, message affiché.
  Toute autre exception → 500 et `outil/hub.log`.
- Windows et Linux : tout ce qui dépend du système passe par `outil/systeme.py`
  (ouvrir un fichier, fenêtres « Ouvrir » et « Choisir un dossier », terminal,
  navigateur, PDF, arrêt d'un processus, notifications, dossier Documents).
  Jamais `os.startfile`, `ctypes.WinDLL` ni PowerShell directement dans un
  module ; un module doit s'importer sur les deux systèmes.
- Programmes externes : `subprocess.run([...], timeout=..., **systeme.options_sans_fenetre())`
  (pas de fenêtre noire sous Windows ; `creationflags` est refusé sous Linux),
  **jamais `shell=True`** avec une donnée venue de la page, toujours une liste
  d'arguments.
- Secrets (mots de passe, jetons) : jamais dans un fichier en clair.
  `systeme.secret_ecrire/secret_lire/secret_supprimer` (coffre de Windows, ou
  trousseau du bureau sous Linux) ou le coffre chiffré `coffre.py`.
- Un chemin reçu de la page : `os.path.normpath`, vérifier qu'il existe.
- Arrêter un processus, supprimer un fichier : la page demande d'abord une
  confirmation ; le serveur refuse les cibles dangereuses (processus système,
  « Mes outils » lui-même…).
- Docstrings et commentaires en français.

## Dans la page : `outil/web/<nom>.js`

Chargé automatiquement au démarrage, par ordre alphabétique, après `hub.html`.
La section `<section id="vue-<nom>">` est créée pour lui.

```js
"use strict";
(() => {
  I18N.ajouter({ "Mes projets": "My projects", "{n} en marche": "{n} running" });

  const style = document.createElement("style");
  style.textContent = `.pj-carte { ... }`;   // préfixe propre à l'onglet
  document.head.append(style);

  async function afficher() {
    const r = await api("/api/<nom>/liste", {});
    $("#vue-<nom>").replaceChildren(
      el("div", { class: "barre-vue" }, el("h2", {}, "" + t("Mes projets"))),
      ...);
  }

  VUES.<nom> = { afficher, titre: "Mes projets", icone: icone("package"), groupe: "dev", ordre: 30 };
})();
```

- Chaque onglet est une **application** que la personne active ou non (page
  « Applications », assistant du premier lancement). Déclaration complète :

  ```js
  VUES.taches = {
    afficher,                        // appelée à chaque ouverture
    titre: "Tâches", icone: icone("list-checks"),
    groupe: "quotidien",             // quotidien | clients | organisation | dev | outils | systeme
    ordre: 25,
    description: "Une phrase pour le catalogue des applications.",
    profils: ["freelance", "assistant_virtuel", "assistant_direction", "developpeur"],
    carteAccueil: async () => el("div", { class: "carte-jour" }, …) || null,  // facultatif
    commandes: () => [ … ],          // facultatif (palette Ctrl + K)
  };
  ```

  `profils` : les métiers pour lesquels l'application est cochée d'office au
  premier lancement. `carteAccueil` : une petite carte (classe `carte-jour`,
  titre en `h4`) affichée sur l'Accueil quand il y a quelque chose d'utile
  (tâches du jour, factures impayées…), sinon `null`.
- Une application peut être désactivée : ses données restent, son code reste
  chargé, mais elle n'est plus dans le menu. Une application qui en utilise une
  autre (ex. Factures et Contacts) l'appelle par son API (`/api/contacts/liste`)
  dans un `try/catch`, et reste utilisable si l'autre est absente.
- Rappels par la bulle (Python, facultatif) : `alertes_dues()` renvoie
  `[{id, titre, detail}]` et `marquer_alerte(id)` les marque comme vues ; la
  bulle les affiche comme les rappels de l'agenda (toute application qui a
  `alertes_dues()` est lue toute seule, si elle est active).
- Fichiers joints (justificatifs, logos…) : dans `config.DONNEES/<nom>/`.
- Palette de commandes (Ctrl + K) : un onglet peut y proposer des actions,
  `commandes: () => [{ icone: icone("play"), titre: "Démarrer le projet X", detail: "…", action: () => … }]`.
- **Couleurs : uniquement les variables** (thème clair et thème sombre) :
  `--carte` (fond de carte), `--surface` (fond discret), `--champ`,
  `--ligne`, `--encre`, `--doux`, `--gris`, `--violet`, `--violet-2`,
  `--violet-clair`, `--sur-violet`, `--vert-clair`/`--vert-texte`,
  `--rouge-clair`/`--rouge-texte`, `--ambre-clair`/`--ambre-texte`,
  `--bleu-clair`/`--bleu-texte`, `--code`/`--code-texte`, `--mono`,
  `--ombre`, `--ombre-forte`, `--rayon`. Jamais de `#fff` en dur. Vérifier
  en sombre avec `?theme=sombre` dans l'adresse.
- Fonctions disponibles : `api(chemin, donnees)` (POST si `donnees`, sinon
  GET ; lève une erreur avec le message du serveur), `el(tag, attrs, ...enfants)`,
  `$(sélecteur)`, `toast(message, "succes" | "erreur" | "", durée)`,
  `fenetre([éléments], petite)`, `fermer()`,
  `await confirmer(icone, titre, texte, "Oui")`,
  `await choisirDossier(titre)`, `copier(texte)`, `montrerVue(nom)`,
  `t(texte, variables)`, `I18N.locale()` (dates et nombres).
- Classes CSS communes : `.btn`, `.btn.principal`, `.btn.discret`,
  `.icone-btn`, `.barre-vue` (+ `.espace`), `.champ` (label + input),
  `.champ-recherche`, `.puces` / `.puce` / `.puce.actif`, `.vide`,
  `.etiquette`, `.point` (`.marche`, `.demarrage`, `.occupe`).
  Variables : `--carte`, `--encre`, `--doux`, `--ligne`, `--violet`,
  `--violet-clair`, `--corail`, `--menthe`, `--ambre`, `--rouge`, `--ombre`.
- **Langue** : le texte est écrit en français. `el()`, `toast()` et
  `confirmer()` traduisent seuls les textes simples, `title` et `placeholder`
  s'ils figurent dans `I18N.ajouter({...})`. Texte avec une valeur :
  `t("Port {port} libéré", { port })`, et la clé `"Port {port} libéré"` dans le
  dictionnaire. Messages d'erreur du serveur : les ajouter aussi au
  dictionnaire (`I18N.motifs([[/^…$/, "…"]])` pour les messages variables).
- **Listes** : en lignes compactes, classes communes de hub.html : `.lignes` >
  `.ligne` (`.ligne-ic`, `.ligne-corps` > `.ligne-titre` + `.ligne-meta`,
  `.ligne-cote`, `.ligne-actions` visibles au survol), `.ligne-detail` pour un
  contenu déplié, `.tag` (étiquette neutre), `.etat-txt.vert|rouge|ambre|gris`
  (état en texte coloré). La couleur est réservée aux états.
- **Pas d'emoji dans l'interface.** Icônes au trait seulement : `icone("folder")`
  renvoie un `<svg>` (taille du texte, couleur du texte). Les noms sont ceux de
  [Lucide](https://lucide.dev/icons) présents dans `outil/web/icones.js` ; pour
  en ajouter, compléter `packaging/generer_icones.py` et régénérer le fichier.
  (Un emoji oublié dans le code est remplacé à l'affichage par l'icône
  équivalente, ou retiré, mais il vaut mieux écrire l'icône directement.)
- Échapper : `el()` crée du texte, jamais du HTML. Ne pas utiliser `innerHTML`
  avec une donnée.

## Tests : `tests/test_<nom>.py`

```python
from aide import ConfigTemporaire, ServeurTest
import <nom>

class TestRoutes(ServeurTest):
    def test_liste(self):
        with ConfigTemporaire({"dossiers_projets": []}) as cfg:
            statut, r = self.post("/api/<nom>/liste", {})
        self.assertEqual(statut, 200)
```

`ConfigTemporaire` remplace `outils.json` et `donnees/` : les vrais fichiers ne
sont jamais touchés. Simuler les programmes externes et Internet
(`unittest.mock`) ; messages d'assertion en français.

```bat
python -m unittest discover -s tests
```

## Dépôt public

Aucune donnée personnelle dans le code, les exemples ou les tests (noms,
adresses, chemins de votre PC, clients).
