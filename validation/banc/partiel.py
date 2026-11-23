"""Résultat partiel de passages en cours, lu dans les dossiers des sondes déjà terminées (les résultats ne s'écrivent qu'en fin
de passage). Regroupe par version du plugin ; une sonde jouée deux fois compte pour la moyenne.

    python partiel.py [--depuis AAAAMMJJ-HHMMSS]
"""
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

BANC = Path(__file__).resolve().parent
sys.path.insert(0, str(BANC))
import banc  # noqa: E402


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    depuis = sys.argv[sys.argv.index("--depuis") + 1] if "--depuis" in sys.argv else ""
    par_version: dict[str, dict[str, list[bool]]] = collections.defaultdict(lambda: collections.defaultdict(list))
    for run in sorted(banc.EXECUTIONS.glob("2026*")):
        if run.name < depuis:
            continue
        for d in run.iterdir():
            b = d / "_brut.jsonl"
            if not b.exists():
                continue
            t = b.read_text(encoding="utf-8", errors="ignore")
            if '"type":"result"' not in t:
                continue
            m = re.search(r"plugin_(v\w+)", t)
            version = m.group(1) if m else "?"
            sonde = json.loads((BANC / "sondes" / f"{d.name}.json").read_text(encoding="utf-8"))
            ok = banc.verifier(sonde["verifications"][0], d, "", [])[0]  # réponse finale seule
            par_version[version][d.name].append(ok)
    communes = set.intersection(*(set(v) for v in par_version.values())) if par_version else set()
    for v, s in sorted(par_version.items()):
        tot = sum(sum(x) / len(x) for x in s.values())
        com = sum(sum(s[i]) / len(s[i]) for i in communes)
        print(f"{v:6s} {tot:5.1f}/{len(s)} ({100 * tot / max(len(s), 1):.1f} %) ; sur les {len(communes)} sondes communes : {com:.1f}")


if __name__ == "__main__":
    main()
