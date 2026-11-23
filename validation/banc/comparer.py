"""Comparaison appariée de versions sur les mêmes sondes : taux par famille et par issue, gains et pertes sonde par sonde.

    python comparer.py ETIQUETTE_A ETIQUETTE_B [ETIQUETTE_C ...]

Une étiquette rassemble tous les passages qui la portent (passages parallèles compris) ; une sonde jouée plusieurs fois compte
pour la moyenne de ses essais. Les sessions à coût nul (limite d'usage, erreur d'API) sont écartées.
"""
from __future__ import annotations

import collections
import glob
import json
import sys
from pathlib import Path

BANC = Path(__file__).resolve().parent
sys.path.insert(0, str(BANC))


def charger(etiquette: str) -> dict[str, list[bool]]:
    out: dict[str, list[bool]] = collections.defaultdict(list)
    for f in glob.glob(str(BANC / "resultats" / "*.json")):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        if d.get("etiquette") != etiquette:
            continue
        for x in d.get("resultats", []):
            if (x.get("cout_usd") or 0) > 0 and x.get("statut_execution") == "termine" and not ambigue(x["id"]):
                out[x["id"]].append(reussite_finale(d.get("run", ""), x))
    return out


def ambigue(sid: str) -> bool:
    """Sonde dont l'issue réelle ne se lit pas sans ambiguïté dans le dispositif (relecture du 23 novembre 2026)."""
    return "etiquette_ambigue" in json.loads((BANC / "sondes" / f"{sid}.json").read_text(encoding="utf-8"))


def reussite_finale(run: str, x: dict) -> bool:
    """Rejuge sur la réponse finale les passages notés avant le 23 novembre 2026, où un message quelconque suffisait."""
    import banc
    for base in (banc.EXECUTIONS, BANC.parents[1] / "banc_runs"):
        dossier = base / run / x["id"]
        if (dossier / "_brut.jsonl").exists():
            sonde = json.loads((BANC / "sondes" / f"{x['id']}.json").read_text(encoding="utf-8"))
            v = next((v for v in sonde.get("verifications", []) if v.get("type") == "message_commence"), None)
            if v:
                return banc.verifier(v, dossier, "", [])[0]
    return bool(x["reussi"])


def issue(sid: str) -> str:
    return json.loads((BANC / "sondes" / f"{sid}.json").read_text(encoding="utf-8")).get("origine", "").strip()[-3:]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    etiquettes = sys.argv[1:]
    donnees = {e: charger(e) for e in etiquettes}
    communes = sorted(set.intersection(*(set(d) for d in donnees.values()))) if donnees else []
    print(f"{len(communes)} sondes jouées par toutes les versions")
    for e, d in donnees.items():
        taux = {s: sum(v) / len(v) for s, v in d.items() if s in communes}
        par = collections.defaultdict(lambda: [0.0, 0])
        for s, t in taux.items():
            k = f"{s.split('-')[1]}-{issue(s)}"
            par[k][0] += t
            par[k][1] += 1
        tot = sum(taux.values())
        print(f"  {e:24s} {tot:5.1f}/{len(taux)} ({100 * tot / max(len(taux), 1):.1f} %)  " +
              "  ".join(f"{k} {v[0]:.1f}/{v[1]}" for k, v in sorted(par.items())))
    if len(etiquettes) >= 2:
        a, b = donnees[etiquettes[0]], donnees[etiquettes[-1]]
        gains = [s for s in communes if sum(b[s]) / len(b[s]) > sum(a[s]) / len(a[s])]
        pertes = [s for s in communes if sum(b[s]) / len(b[s]) < sum(a[s]) / len(a[s])]
        print(f"{etiquettes[-1]} contre {etiquettes[0]} : {len(gains)} sondes gagnées, {len(pertes)} perdues")
        print("  gagnées :", ", ".join(gains[:12]))
        print("  perdues :", ", ".join(pertes[:12]))


if __name__ == "__main__":
    main()
