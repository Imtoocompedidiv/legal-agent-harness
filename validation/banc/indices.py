"""Audit des indices de procédure : pour chaque indice présent au dossier remis, issue réelle et justesse de l'agent.

    python indices.py ETIQUETTE [ETIQUETTE ...]

Un indice dont l'issue est très inégale dans l'échantillon et sur lequel l'agent se trompe souvent est un indice mal lu : à
vérifier sur le texte (souvent, comme la dispense de conclusions, il tient à la matière et ne dit rien de l'issue). Prudence :
l'usine tire chaque issue par une recherche distincte, si bien qu'un indice peut être inégal par construction de l'échantillon ;
la correction se fonde sur le texte, jamais sur la corrélation observée.
"""
from __future__ import annotations

import collections
import glob
import json
import re
import sys
from pathlib import Path

BANC = Path(__file__).resolve().parent
sys.path.insert(0, str(BANC))
from banc import EXECUTIONS  # noqa: E402
INDICES = {
    "dispense de conclusions": r"dispens\w* (?:la |le )?rapporteu|dispens\w* de (?:prononcer des )?conclu",
    "conclusions du rapporteur public": r"conclusions de (?:m\.|mme|monsieur|madame)? ?\S* ?,? ?rapporteu",
    "défense absente": r"n'a pas produit|aucun mémoire en défense|pas produit de (?:mémoire|défense|observations)",
    "mise en demeure (R. 612-3)": r"mise en demeure",
    "mémoire en défense": r"mémoire en défense|conclut au rejet",
    "mémoire en réplique": r"mémoire en réplique|réplique",
    "note en délibéré": r"note en délibéré",
    "aide juridictionnelle": r"aide juridictionnelle",
    "partie absente à l'audience": r"n'était ni présent ni représenté|ni présente? ni représentée?|n'a pas constitué avocat",
    "audience tenue": r"audience publique",
    "ordonnance de tri (L. 522-3)": r"l\.? ?522-3",
    "clôture d'instruction": r"clôture (?:de l'|d')instruction",
    "moyen relevé d'office": r"relev\w* d'office|susceptible d'être fondée? sur un moyen",
}


def charger(etiquette: str) -> list[dict]:
    out = []
    for f in glob.glob(str(BANC / "resultats" / "*.json")):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        if d.get("etiquette") == etiquette:
            out.extend(d["resultats"])
    return out


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    # Une session à coût nul n'a pas tourné (limite d'usage, erreur d'API) : elle ne dit rien de l'agent.
    lignes = [x for e in sys.argv[1:] for x in charger(e) if x.get("statut_execution") == "termine" and (x.get("cout_usd") or 0) > 0]
    tab: dict[str, list[int]] = collections.defaultdict(lambda: [0, 0, 0, 0])  # oui, non, justes, total
    for x in lignes:
        s = BANC / "sondes" / f"{x['id']}.json"
        if not s.exists():
            continue
        sonde = json.loads(s.read_text(encoding="utf-8"))
        issue = sonde.get("origine", "").strip()[-3:]
        if issue not in ("oui", "non"):
            continue
        fx = BANC / "fixtures" / sonde.get("fixture", "") / "dossier_remis.md"
        if not fx.exists():
            continue
        t = fx.read_text(encoding="utf-8")
        for nom, rx in INDICES.items():
            if re.search(rx, t, re.I | re.M):
                v = tab[nom]
                v[0 if issue == "oui" else 1] += 1
                v[2] += 1 if x["reussi"] else 0
                v[3] += 1
    # Livraison : une ligne de fiche ne compte que si elle atteint l'agent (contrat injecté ou fiche lue). Banc du 22 novembre :
    # requête en annulation, contrat dans 9 sessions sur 58 ; les lignes ajoutées ne pouvaient rien changer.
    livrees = 0
    for e in sys.argv[1:]:
        for f in glob.glob(str(BANC / "resultats" / "*.json")):
            d = json.loads(Path(f).read_text(encoding="utf-8"))
            if d.get("etiquette") != e:
                continue
            for x in d["resultats"]:
                b = next((r / d["run"] / x["id"] / "_brut.jsonl" for r in (EXECUTIONS, BANC.parents[1] / "banc_runs")
                          if (r / d["run"] / x["id"] / "_brut.jsonl").exists()), None)
                if b:
                    t = b.read_text(encoding="utf-8", errors="ignore")
                    livrees += "Condition principale" in t or "mecanique-des-exercices/references/" in t
    print(f"livraison : contrat ou fiche devant l'agent dans {livrees} session(s) sur {len(lignes)}")
    print(f"{len(lignes)} réponses ; indice : issue réelle (oui/non) ; justesse de l'agent quand l'indice est au dossier")
    for nom, (o, n, j, tot) in sorted(tab.items(), key=lambda kv: kv[1][2] / max(kv[1][3], 1)):
        alerte = "  <- à vérifier" if tot >= 6 and j / tot < 0.75 and max(o, n) / max(o + n, 1) >= 0.75 else ""
        print(f"  {nom:34s} {o:3d}/{n:<3d} justes {j}/{tot} ({100 * j // max(tot, 1)} %){alerte}")


if __name__ == "__main__":
    main()
