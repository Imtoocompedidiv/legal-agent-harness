"""Correcteur du banc : juge au sens, non aux mots, si une réponse satisfait des critères écrits en clair.

Une vérification de type « critere » remplace le motif littéral là où la bonne réponse peut se formuler de mille façons.
Le correcteur est Opus, sans outils ni contexte de dossier ; ses jugements se gardent dans _correcteur.json, à côté de la
réponse, et ne se recalculent que si la réponse, la consigne ou le critère changent.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

VERSION = 1
CONSIGNE = """Tu corriges la réponse d'un avocat à la consigne ci-dessous. Pour chaque critère numéroté, dis s'il est satisfait.
Juge au sens, jamais aux mots : un critère rempli par une autre formulation est satisfait. Un critère seulement évoqué, écarté,
ou présenté comme une simple possibilité sans être recommandé ni appliqué, n'est pas satisfait. N'ajoute aucun critère.
Réponds uniquement par un tableau JSON, sans texte autour : [{"n": 1, "ok": true, "pourquoi": "quinze mots au plus"}, ...]

## Consigne donnée à l'avocat
{consigne}

## Réponse de l'avocat
{reponse}

## Critères
{criteres}
"""


def demander(texte: str, delai: int = 600) -> tuple[str, float]:
    """Une question à Opus, sans outils ni contexte de dossier : (réponse, coût)."""
    with tempfile.TemporaryDirectory() as vide:
        r = subprocess.run([shutil.which("claude"), "-p", "--model", "opus", "--tools", "", "--strict-mcp-config", "--output-format", "json"],
                           input=texte, cwd=vide, capture_output=True, text=True, encoding="utf-8", timeout=delai,
                           creationflags=getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0))
    sortie = json.loads(r.stdout)
    return sortie.get("result", ""), float(sortie.get("total_cost_usd") or 0)


def juger(consigne: str, reponse: str, criteres: list[str], dossier: Path) -> list[tuple[bool, str]]:
    cle = hashlib.sha256(json.dumps([VERSION, consigne, reponse, criteres], ensure_ascii=False).encode()).hexdigest()
    cache_f = dossier / "_correcteur.json"
    cache = json.loads(cache_f.read_text(encoding="utf-8")) if cache_f.is_file() else {}
    if cle in cache:
        return [tuple(x) for x in cache[cle]]
    texte = CONSIGNE.replace("{consigne}", consigne).replace("{reponse}", reponse[:20000]).replace(
        "{criteres}", "\n".join(f"{i}. {c}" for i, c in enumerate(criteres, 1)))
    with tempfile.TemporaryDirectory() as vide:
        r = subprocess.run([shutil.which("claude"), "-p", "--model", "opus", "--tools", "", "--strict-mcp-config", "--output-format", "json"],
                           input=texte, cwd=vide, capture_output=True, text=True, encoding="utf-8", timeout=1500,
                           creationflags=getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0))
    try:
        sortie = json.loads(r.stdout)
        m = re.search(r"\[.*\]", sortie.get("result", ""), re.S)
        lus = {int(x["n"]): (bool(x["ok"]), str(x.get("pourquoi", ""))) for x in json.loads(m.group(0))}
        res = [lus.get(i, (False, "critère non jugé")) for i in range(1, len(criteres) + 1)]
    except Exception as e:  # noqa: BLE001
        return [(False, f"correcteur en erreur : {type(e).__name__}")] * len(criteres)
    cache[cle] = res
    cache["_cout_usd"] = round(float(cache.get("_cout_usd", 0)) + float(sortie.get("total_cost_usd") or 0), 4)
    cache_f.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    return res
