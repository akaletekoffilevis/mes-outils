# -*- coding: utf-8 -*-
"""Lance les tests et, sur GitHub Actions, écrit chaque échec dans une
annotation (lisible sur la page du travail, même sans ouvrir le journal)."""
import os
import sys
import unittest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def echapper(texte):
    return texte.replace("%", "%25").replace("\r", "").replace("\n", "%0A")


def main():
    os.chdir(ICI)
    suite = unittest.defaultTestLoader.discover("tests")
    resultat = unittest.TextTestRunner(verbosity=1).run(suite)
    problemes = [("ERREUR", t, tb) for t, tb in resultat.errors] + [("ÉCHEC", t, tb) for t, tb in resultat.failures]
    if os.environ.get("GITHUB_ACTIONS"):
        noms = ", ".join(t.id() for _, t, _ in problemes)
        if problemes:
            print(f"::error title={len(problemes)} test(s) en échec::{echapper(noms)[:3000]}")
        # GitHub garde 10 annotations d'erreur par étape : les 9 premiers détails.
        for genre, test, trace in problemes[:9]:
            lignes = trace.strip().splitlines()
            print(f"::error title={genre} {test.id()}::{echapper(chr(10).join(lignes[-25:]))[:6000]}")
    sys.exit(0 if resultat.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
