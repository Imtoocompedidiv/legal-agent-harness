"""Rassemble les échecs récents du banc, un dossier par échec : dossier remis, réponse finale de l'agent, décision réelle en texte
intégral (client LibreJustice autorisé), pour qu'un lecteur dise si le fait décisif était au dossier ou si l'agent a mal raisonné.

    python echecs.py SORTIE ETIQUETTE [ETIQUETTE ...]
"""
from __future__ import annotations

import glob
import json
import re
import sys
from pathlib import Path

BANC = Path(__file__).resolve().parent
sys.path.insert(0, str(BANC))
sys.path.insert(0, str(BANC.parent / "corpus_motifs"))
import banc  # noqa: E402


def dossier_de_run(run: str) -> Path | None:
    for r in (banc.EXECUTIONS, BANC.parents[1] / "banc_runs"):
        if (r / run).is_dir():
            return r / run
    return None


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sortie = Path(sys.argv[1])
    sortie.mkdir(parents=True, exist_ok=True)
    from lj import Client
    client = Client()
    vus = set()
    for etiquette in sys.argv[2:]:
        for f in glob.glob(str(BANC / "resultats" / "*.json")):
            d = json.loads(Path(f).read_text(encoding="utf-8"))
            if d.get("etiquette") != etiquette:
                continue
            run = dossier_de_run(d["run"])
            for x in d["resultats"]:
                if x["reussi"] or not (x.get("cout_usd") or 0) or x["id"] in vus or not run:
                    continue
                sonde = json.loads((BANC / "sondes" / f"{x['id']}.json").read_text(encoding="utf-8"))
                url = re.search(r"https://librejustice\.fr/decision/[\w-]+", sonde.get("origine", ""))
                if not url:
                    continue
                msgs = banc.messages_principaux(run / x["id"])
                reponse = next((m for m in reversed(msgs) if re.match(r"\W*(oui|non)\b", m.strip(), re.I)), "")
                try:
                    dec = client.appel("get_decision", {"url": url.group(0)})
                except Exception as e:  # noqa: BLE001
                    print("décision illisible", x["id"], e)
                    continue
                cible = sortie / x["id"]
                cible.mkdir(exist_ok=True)
                (cible / "dossier_remis.md").write_text((run / x["id"] / "dossier_remis.md").read_text(encoding="utf-8"), encoding="utf-8")
                (cible / "reponse_agent.md").write_text(f"Version : {etiquette}\nIssue réelle : {sonde['origine'].strip()[-3:]}\n\n{reponse}",
                                                         encoding="utf-8")
                (cible / "decision_reelle.md").write_text(f"# {dec.get('title')}\n\n{dec.get('text', '')}", encoding="utf-8")
                vus.add(x["id"])
    print(f"{len(vus)} échecs rassemblés dans {sortie}")


if __name__ == "__main__":
    main()
