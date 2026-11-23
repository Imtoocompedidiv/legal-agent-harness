"""Qualité des textes du harness : clarté, enjeux, psychologie du lecteur, récit. Évaluation sobre, sans session d'agent.

    python recit.py diagnostic <run> [--ids A,B]         note les textes d'un passage en un seul appel et dit les défauts dominants
    python recit.py comparer <run_a> <run_b> [--ids ...]  compare deux à deux, dans les deux ordres, les textes des mêmes sondes

Les textes sont la réponse finale de chaque sonde et, quand il existe, le dernier brouillon de `ecritures/brouillons/`.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

BANC = Path(__file__).resolve().parent
RACINE = BANC.parent.parent
sys.path.insert(0, str(BANC))
import correcteur  # noqa: E402

GRILLE = """1. Clarté intellectuelle : le message central se saisit dans les premières lignes ; une idée par paragraphe ; l'enchaînement logique est explicite.
2. Enjeux : le texte dit ce qui se joue, pour qui, à quelle date, combien, et pourquoi cela compte.
3. Psychologie du lecteur : le texte est écrit pour ce lecteur précis (ce qu'il sait, craint, attend, doit faire après lecture) ; il anticipe son objection.
4. Récit : les faits forment une histoire qui sert la thèse (situation, rupture, conséquence, issue), et non une chronologie ou une liste ; le fait décisif vient tôt.
5. Dimension sociale : le texte tient compte du monde du lecteur et des parties (qui décide derrière lui, ce que chacun craint, rapports de pouvoir, relations qui survivent au litige, situation sociale du client) quand cela pèse sur la décision."""

TEXTES_SONDES = ("OFFENSIVE-FOND-AF", "POST2-LETTRE-NE-LIVRE-RIEN", "POST2-REPONSE-AVOCAT-ADVERSE", "POSTURE-TENIR-SA-LIGNE",
                 "POST2-DESACCORD-SANS-ELEMENT", "SEQ2-AF-SEQUENCE", "EXO-TRAVAIL-REFERE-AGENT-SUSPENDU", "URGENCE-RETRAIT-AGREMENT",
                 "POSTURE-FAIRE-PARLER-L-ADVERSAIRE", "EXO-TRAVAIL-LETTRE-RECOURS-PERMIS")


def texte_de(dossier: Path) -> str:
    rep = next((json.loads(l).get("result", "") for l in (dossier / "_brut.jsonl").open(encoding="utf-8", errors="replace")
                if '"type":"result"' in l), "")
    brouillons = sorted((dossier / "ecritures" / "brouillons").glob("*.md"), key=lambda f: f.stat().st_mtime) if (dossier / "ecritures" / "brouillons").is_dir() else []
    acte = brouillons[-1].read_text(encoding="utf-8", errors="replace") if brouillons else ""
    return (f"[Réponse donnée]\n{rep[:12000]}" + (f"\n\n[Écrit rédigé : {brouillons[-1].name}]\n{acte[:12000]}" if acte else "")).strip()


def consigne_de(sonde: str) -> str:
    f = BANC / "sondes" / f"{sonde}.json"
    return json.loads(f.read_text(encoding="utf-8")).get("consigne", "") if f.is_file() else ""


def diagnostic(run: str, ids: list[str]) -> None:
    for k in range(0, len(ids), 5):
        _diagnostic(run, ids[k:k + 5])


def _diagnostic(run: str, ids: list[str]) -> None:
    blocs = []
    for i in ids:
        d = RACINE / "banc_runs" / run / i
        if (d / "_brut.jsonl").is_file():
            blocs.append(f"### Texte {i}\nConsigne : {consigne_de(i)}\n{texte_de(d)}")
    q = ("Tu es associé d'un cabinet de contentieux de premier rang et tu relis les textes d'un collaborateur. Note chaque texte de 1 à 5 sur "
         "chaque critère de la grille, puis donne ses deux défauts principaux, chacun avec une citation courte du texte. Termine par les trois "
         "défauts qui reviennent le plus, en une ligne chacun. Réponds par un objet JSON : {\"textes\": [{\"id\": ..., \"notes\": [c1, c2, c3, c4, c5], "
         "\"defauts\": [\"...\", \"...\"]}], \"defauts_dominants\": [\"...\", \"...\", \"...\"]}\n\n## Grille\n" + GRILLE + "\n\n" + "\n\n".join(blocs))
    rep, cout = correcteur.demander(q, delai=1500)
    v = json.loads(re.search(r"\{.*\}", rep, re.S).group(0))
    for t in v["textes"]:
        print(f"{t['id']:<36} {t['notes']}  {' | '.join(t['defauts'])[:260]}")
    moy = [sum(t["notes"][k] for t in v["textes"]) / len(v["textes"]) for k in range(5)]
    print("moyennes (clarté, enjeux, psychologie, récit, social) :", [round(x, 1) for x in moy])
    print("défauts dominants :", *v["defauts_dominants"], sep="\n  - ")
    print(f"coût {cout:.2f} $")


def comparer(run_a: str, run_b: str, ids: list[str]) -> None:
    """Préférence deux à deux, dans les deux ordres pour neutraliser la position : B l'emporte, A l'emporte ou partage."""
    n_crit = GRILLE.count("\n") + 1
    par_critere = [[0, 0, 0] for _ in range(n_crit)]  # B, A, partage
    cout = 0.0
    for i in ids:
        ta, tb = (texte_de(RACINE / "banc_runs" / r / i) for r in (run_a, run_b))
        if not ta or not tb:
            continue
        votes = []
        for premier, second, sens in ((ta, tb, 1), (tb, ta, -1)):
            q = ("Deux collaborateurs ont répondu à la même consigne. Pour chaque critère de la grille, dis lequel des deux textes est le "
                 "meilleur. Réponds par un objet JSON {\"criteres\": [\"1\" ou \"2\" ou \"egal\", ... un par critère, dans l'ordre], "
                 "\"pourquoi\": \"vingt mots au plus\"}.\n\n## Grille\n" + GRILLE + f"\n\n## Consigne\n{consigne_de(i)}\n\n## Texte 1\n{premier}\n\n## Texte 2\n{second}")
            rep, c = correcteur.demander(q, delai=1500); cout += c
            ms = json.loads(re.search(r"\{.*\}", rep, re.S).group(0)).get("criteres", [])
            votes.append([0 if m == "egal" else (1 if (m == "2") == (sens == 1) else -1) for m in ms[:n_crit]])
        par = [a + b for a, b in zip(*votes)] if len(votes) == 2 else []
        for k, s in enumerate(par):
            par_critere[k][0 if s > 0 else 1 if s < 0 else 2] += 1
        print(f"{i:<36} " + " ".join("B" if s > 0 else "A" if s < 0 else "=" for s in par))
    noms = ["clarté", "enjeux", "psychologie", "récit", "social"][:n_crit]
    for nom, (b, a_, e) in zip(noms, par_critere):
        print(f"  {nom:<12} B l'emporte {b}, A {a_}, partage ou indécis {e}")
    print(f"coût {cout:.2f} $ (« = » : égalité, ou vote qui change avec l'ordre de lecture)")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    d = s.add_parser("diagnostic"); d.add_argument("run"); d.add_argument("--ids")
    c = s.add_parser("comparer"); c.add_argument("run_a"); c.add_argument("run_b"); c.add_argument("--ids")
    a = p.parse_args()
    ids = a.ids.split(",") if a.ids else list(TEXTES_SONDES)
    if a.cmd == "diagnostic":
        diagnostic(a.run, ids)
    else:
        comparer(a.run_a, a.run_b, ids)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
