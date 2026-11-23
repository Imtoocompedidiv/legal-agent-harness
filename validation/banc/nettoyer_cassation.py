"""Retire des pièces de cassation du banc ce que la Cour a décidé en rendant l'arrêt et que personne ne savait avant : la mention de
publication (F-B, FS-B, FP-B+R...) et les phrases de l'article 1014 du CPC sur les griefs écartés sans motivation spéciale.
Autopsie du 22 novembre 2026 : la mention F-B figurait dans 38 réponses fausses sur 43 et servait à conclure à la cassation, alors que
toutes les sondes de la collection sont publiées (9 cassations, 9 rejets). Idempotent ; appelé par usine.py pour les sondes nouvelles.

    python nettoyer_cassation.py            nettoie validation/banc/fixtures/gen_cass*/
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "fixtures"
PUBLICATION = re.compile(r"(?<![\w-])(?:F|FS|FP)-(?:[BDPRCI])(?:\+[BDPRCI])*(?![\w-])")
PHRASE_1014 = re.compile(r"[^.\n]*(?:article 1014|1014, alinéa 2|décision spécialement motivée|manifestement pas de nature à entraîner la cassation)[^.\n]*\.?",
                         re.I)


def nettoyer(texte: str) -> str:
    texte = PUBLICATION.sub("", texte)
    # Paragraphe entier : la phrase porte souvent un lien Markdown dont l'URL contient des points.
    lignes = [l for l in texte.splitlines() if not (re.search(r"1014", l) and re.search(r"spécialement motivée|manifestement pas de nature", l, re.I))]
    texte = PHRASE_1014.sub("", "\n".join(lignes))
    return re.sub(r"\n{3,}", "\n\n", texte)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    n = 0
    for p in sorted(FIXTURES.glob("gen_cass*/*.md")):
        t = p.read_text(encoding="utf-8")
        t2 = nettoyer(t)
        if t2 != t:
            p.write_text(t2, encoding="utf-8")
            n += 1
    print(f"{n} pièce(s) de cassation nettoyée(s)")


if __name__ == "__main__":
    main()
