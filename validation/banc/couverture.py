"""Matrice de couverture du harness : chaque dimension reçoit-elle un traitement à sa mesure ? Aucun appel au modèle.

    python couverture.py [--run <passage complet>]

Pour chaque skill du plugin : savoir (taille du skill et de ses références), routage (mentions dans le briefing et dans la constitution),
contrôles (mentions dans les scripts hors briefing), activation réelle (part des sessions d'un passage complet qui chargent le skill ou lisent
ses références), mesure (sondes qui le visent). Une dimension pourvue de savoir mais peu activée, ou jamais mesurée, est sous-pondérée.
Ce garde-fou existe parce qu'une dimension entière (le récit) est restée négligée sans que rien ne le signale (20 novembre 2026).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

BANC = Path(__file__).resolve().parent
RACINE = BANC.parent.parent
PLUGIN = RACINE / "plugins" / "contentieux"
sys.path.insert(0, str(BANC))
import autopsie  # noqa: E402

# Ce qui, dans une sonde, montre qu'elle mesure la dimension : mots de sa consigne, de son origine ou de ses vérifications.
INDICES = {
    "analyse-documentaire": r"pièce|analyse documentaire|métadonn|bordereau",
    "theorie-de-l-affaire": r"théorie de l.affaire|hypothèse concurrente|vérité",
    "recit-judiciaire": r"récit|lecteur|clarté|raconte",
    "lecture-des-decideurs": r"décideur|sociolog|institution|psycholog|formation de jugement",
    "negociation-et-persuasion": r"négoci|transaction|médiation|offre|persuasion",
    "rapport-de-force": r"adversaire|rapport de force|lettre|levier|position tenue|désaccord",
    "conduite-de-la-sequence": r"séquence|ordre des coups|voies? de l.adversaire",
    "strategie-contentieuse": r"stratégie|ligne stratégique|chances",
    "mecanique-des-exercices": r"exercice|mécanique",
    "recherche-juridique": r"jurisprudence|texte à la date|recherche|article",
    "recherche-doctrinale": r"doctrine|conclusions du rapporteur|thèse|empirique",
    "refere-administratif": r"référé[- ](?:suspension|liberté|mesures|provision)|urgence",
    "refere-civil": r"834|835|145",
    "cassation": r"cassation|pourvoi",
    "contentieux-du-fond": r"requête au fond|assignation|annulation|conclusions",
    "controle-de-la-norme": r"QPC|exception d.illégalité|conventionnalité",
    "controle-avant-depot": r"dépôt|contrôle avant",
    "ecriture-juridictionnelle": r"rédige|requête|écriture|mémoire",
    "action-sur-le-reel": r"terrain|constat|preuve à créer",
    "prise-en-main-affaire": r"prise en main|reprise",
}


def taille(d: Path) -> int:
    return sum(f.stat().st_size for f in d.rglob("*.md")) // 1024


def main() -> None:
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--run", default=None)
    x = a.parse_args()
    hook = (PLUGIN / "scripts" / "hook.py").read_text(encoding="utf-8")
    debut, fin = hook.find("def briefing("), hook.find("def session_start(")
    brief, reste = hook[debut:fin], hook[:debut] + hook[fin:]
    scripts = reste + "".join((PLUGIN / "scripts" / f).read_text(encoding="utf-8") for f in ("gate.py", "controles_campagne.py", "exercices.py"))
    constitution = (PLUGIN / "templates" / "affaire" / "AGENTS.md").read_text(encoding="utf-8")
    sondes = [json.loads(f.read_text(encoding="utf-8")) for f in (BANC / "sondes").glob("*.json") if not f.stem.startswith("GEN")]
    run = x.run or sorted(f.stem for f in (BANC / "resultats").glob("*.json") if len(json.loads(f.read_text(encoding="utf-8")).get("resultats", [])) >= 70)[-1]
    d = json.loads((BANC / "resultats" / f"{run}.json").read_text(encoding="utf-8"))
    traits = [autopsie.traits(Path(r["dossier"]) / "_brut.jsonl") for r in d["resultats"] if (Path(r["dossier"]) / "_brut.jsonl").is_file()]
    n = len(traits)
    print(f"Passage de référence {run} ({n} sessions). Colonnes : savoir (Ko), briefing, constitution, scripts, activation, sondes.")
    lignes = []
    for s in sorted(p.name for p in (PLUGIN / "skills").iterdir() if p.is_dir()):
        act = sum(1 for t in traits if s in t["skills"] or any(l.startswith(f"skills/{s}/") for l in t["lectures_plugin"]))
        motif = INDICES.get(s, re.escape(s))
        mes = sum(1 for p in sondes if re.search(motif, json.dumps(p, ensure_ascii=False), re.I))
        lignes.append((s, taille(PLUGIN / "skills" / s), brief.count(s), constitution.count(s), scripts.count(s), act, mes))
    for s, k, b, c, sc, act, mes in sorted(lignes, key=lambda l: l[5] / max(1, n)):
        alerte = " <- sous-pondéré" if (k >= 20 and act / max(1, n) < 0.1) or mes == 0 else ""
        print(f"{s:<28} {k:>5} Ko  briefing {b}  constitution {c}  scripts {sc:>3}  activé {act:>2}/{n} ({act / max(1, n):4.0%})  sondes {mes:>2}{alerte}")
    agents = {}
    for t in traits:
        for o, nb in t["outils"].items():
            if o in ("Task", "Agent"):
                agents["sessions avec sous-agent"] = agents.get("sessions avec sous-agent", 0) + 1
    print("sous-agents :", agents or "aucun lancé dans ce passage")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
