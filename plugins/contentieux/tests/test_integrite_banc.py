"""Intégrité du banc : aucune décision dont une sonde prédit l'issue ne figure dans ce que l'agent lit pour travailler.

Une sonde GEN* est une décision réelle coupée avant le raisonnement du juge. Si la fiche, le skill ou le script qui guide l'agent
citait cette décision, le banc mesurerait la mémoire du harness, non son raisonnement. Une règle tirée d'un échec s'établit donc
par d'autres sources (METHODE, point 25). Les sondes d'exercice, qui éprouvent une règle connue, ne sont pas concernées.
Lancer : python -m pytest -q plugins/contentieux/tests/test_integrite_banc.py -p no:cacheprovider"""
import json
import re
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
SONDES = PLUGIN.parents[1] / "validation" / "banc" / "sondes"
LUS_PAR_L_AGENT = ("skills", "references", "agents", "templates", "scripts", "hooks")
NUMERO = re.compile(r"\b(\d{7}|\d{6}|\d{2}-\d{2}\.\d{3})\b")


def decisions_predites() -> dict[str, str]:
    out = {}
    for f in SONDES.glob("GEN*.json"):
        origine = json.loads(f.read_text(encoding="utf-8")).get("origine", "")
        if "issue réelle" not in origine:
            continue
        for n in NUMERO.findall(origine.split("(https")[0]):
            out[n] = f.stem
    return out


@unittest.skipUnless(SONDES.is_dir(), "banc absent (distribution sans validation)")
class Integrite(unittest.TestCase):
    def test_aucune_decision_predite_dans_le_plugin(self):
        predites = decisions_predites()
        self.assertTrue(predites, "aucune sonde tirée d'une décision réelle trouvée")
        fuites = []
        for dossier in LUS_PAR_L_AGENT:
            for p in (PLUGIN / dossier).rglob("*"):
                if not p.is_file() or p.suffix not in (".md", ".json", ".py", ".txt"):
                    continue
                texte = p.read_text(encoding="utf-8", errors="replace")
                fuites += [f"{p.relative_to(PLUGIN)} : n° {n} ({s})" for n, s in predites.items()
                           if re.search(rf"(?<![\d.]){re.escape(n)}(?!\d)", texte)]
        self.assertEqual(fuites, [], "décision prédite par une sonde citée dans le plugin :\n" + "\n".join(fuites))


if __name__ == "__main__":
    unittest.main()
