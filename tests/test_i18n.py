# -*- coding: utf-8 -*-
"""Tests des dictionnaires de traduction (outil/web/*.js) : le dictionnaire
est commun à toute la page, une même phrase ne doit donc pas recevoir deux
traductions différentes, et les {variables} doivent se retrouver dans la
traduction."""
import os
import re
import shutil
import subprocess
import sys
import unittest

WEB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outil", "web")
PAGE = os.path.join(os.path.dirname(WEB), "hub.html")
# Tous les onglets, sauf ceux sans texte d'interface : icones.js (icônes SVG
# générées) et serveurs.js (tout son texte est dans hub.html / i18n.js).
FICHIERS = [n for n in sorted(os.listdir(WEB)) if n.endswith(".js") and n not in ("icones.js", "serveurs.js", "_qrcode_lib.js")]

# Même mot français, sens différent selon le contexte : plusieurs traductions
# anglaises sont voulues, chacune listée ici.
AMBIGUS = {
    "En retard": {"Behind", "Overdue"},      # projet en retard / facture en retard
    "Entreprise": {"Business", "Company"},   # votre entreprise / une société
    "Envoi…": {"Sending…", "Uploading…"},    # envoi d'un mail / envoi d'un dépôt
    "jour": {"all day", "day"},              # rendez-vous « journée » / unité de facturation
}
BLOC = re.compile(r"I18N\.ajouter\(\{(.*?)\}\);", re.S)
PAIRE = re.compile(r'"((?:[^"\\]|\\.)*)"\s*:\s*"((?:[^"\\]|\\.)*)"')


def paires(nom):
    with open(os.path.join(WEB, nom) if not os.path.isabs(nom) else nom, encoding="utf-8") as f:
        texte = f.read()
    for bloc in BLOC.findall(texte):
        # Commentaires « // … » en fin de ligne retirés.
        bloc = re.sub(r"^\s*//.*$", "", bloc, flags=re.M)
        yield from PAIRE.findall(bloc)


def variables(texte):
    """Les variables {var} d'une chaîne, sans les exemples littéraux {{var}}."""
    return set(re.findall(r"(?<!\{)\{(\w+)\}(?!\})", texte))


class TestDictionnaires(unittest.TestCase):
    def test_chaque_fichier_a_un_dictionnaire(self):
        for nom in FICHIERS:
            self.assertTrue(list(paires(nom)), f"{nom} : aucun I18N.ajouter trouvé")

    def test_pas_de_traductions_contradictoires(self):
        vues = {}
        for nom in FICHIERS:
            for cle, valeur in paires(nom):
                if cle in AMBIGUS:
                    self.assertIn(valeur, AMBIGUS[cle],
                                  f"« {cle} » traduit « {valeur} » dans {nom} (hors des traductions voulues)")
                    continue
                if cle in vues and vues[cle][1] != valeur:
                    self.fail(f"« {cle} » traduit « {vues[cle][1]} » dans {vues[cle][0]} et « {valeur} » dans {nom}")
                vues[cle] = (nom, valeur)

    def test_variables_conservees(self):
        for nom in FICHIERS:
            for cle, valeur in paires(nom):
                self.assertEqual(variables(cle), variables(valeur),
                                 f"{nom} : variables différentes entre « {cle} » et « {valeur} »")

    @unittest.skipUnless(shutil.which("node"), "node absent")
    def test_syntaxe_js(self):
        for nom in FICHIERS:
            r = subprocess.run(["node", "--check", os.path.join(WEB, nom)], capture_output=True, text=True,
                               timeout=30, creationflags=0x08000000 if sys.platform == "win32" else 0)
            self.assertEqual(r.returncode, 0, f"{nom} : {r.stderr}")

    def test_textes_selon_le_systeme_traduits(self):
        """Chaque texte de selonSysteme("…Windows…", "…Linux…") a sa traduction
        anglaise, sous Windows comme sous Linux (chemins et séparateurs exceptés)."""
        sources = [os.path.join(WEB, n) for n in sorted(os.listdir(WEB)) if n.endswith(".js")] + [PAGE]
        cles, appels = set(), []
        chaine = r'"((?:[^"\\]|\\.)*)"'
        for chemin in sources:
            cles.update(cle for cle, _ in paires(chemin))
            with open(chemin, encoding="utf-8") as f:
                appels += [(os.path.basename(chemin), a, b) for a, b in
                           re.findall(r"selonSysteme\(\s*" + chaine + r"\s*,\s*" + chaine, f.read())]
        self.assertTrue(appels, "aucun appel à selonSysteme trouvé")
        for nom, *textes in appels:
            for texte in textes:
                if " " in texte and re.search(r"[a-zé]{3}", texte) and "\\" not in texte:
                    self.assertIn(texte, cles, f"{nom} : « {texte} » n'a pas de traduction anglaise")


if __name__ == "__main__":
    unittest.main()
