"""Index des sondes de l'échantillon neuf équilibré jouées par une version : issue réelle, réussite, réponse finale de l'agent.

    python indexer.py RUN[,RUN...] > index.json
"""
import json, re, sys
from pathlib import Path
BANC = Path(__file__).resolve().parents[2] / "banc"
sys.path.insert(0, str(BANC)); import banc
sys.stdout.reconfigure(encoding="utf-8")
out = []
for r in sys.argv[1].split(","):
    for d in sorted((banc.EXECUTIONS / r).iterdir()):
        b = d / "_brut.jsonl"
        if not b.exists() or '"type":"result"' not in b.read_text(encoding="utf-8", errors="ignore"): continue
        sonde = json.loads((BANC / "sondes" / f"{d.name}.json").read_text(encoding="utf-8"))
        motif = sonde["verifications"][0].get("motif", "")
        msgs = banc.messages_principaux(d)
        rep = next((m for m in reversed(msgs) if re.match(r"\W*(oui|non)\b", m.strip(), re.I)), "")
        url = re.search(r"https://librejustice\.fr/decision/[\w-]+", sonde.get("origine", ""))
        out.append({"id": d.name, "famille": d.name.split("-")[1], "issue_reelle": "oui" if "oui" in motif.lower() else "non",
                    "reussi": banc.verifier(sonde["verifications"][0], d, "", [])[0], "dossier": str(d / "dossier_remis.md"),
                    "decision_url": url.group(0) if url else None, "reponse_agent": rep[:2500], "premiere_reponse": next((m for m in msgs if re.match(r"\W*(oui|non)", m.strip(), re.I)), "")[:300]})
print(json.dumps(out, ensure_ascii=False, indent=1))
