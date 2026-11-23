"""Intègre aux fiches d'exercice les motifs minés sur la jurisprudence publique (validation/corpus_motifs/*.json).

    python integrer.py              contrôle et rapport, sans écrire
    python integrer.py --appliquer  écrit les lignes retenues dans les fiches de la source du plugin

Chaque motif retenu devient une ligne marquée : elle n'entre au contrat que si le dossier montre un de ses marqueurs et que la
règle existait à la date du dossier (champ « depuis »). Sont écartés : un motif sans marqueur, une source non lue en entier, une
décision d'épreuve du banc (numeros_exclus.txt), une condition absente de la fiche, une ligne déjà présente.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
REFS = ICI.parents[1] / "plugins" / "contentieux" / "skills" / "mecanique-des-exercices" / "references"
# Les lignes minées des référés ne sont plus intégrées : sur des sondes neuves, elles ont fait perdre de un à deux points par
# famille (v46 contre v43 et v44, 22 novembre), en poussant la révision du contrat vers la mauvaise issue.
FICHES = {"cassation-civile": "pourvoi-cassation-civile.md",
          "annulation-tribunal": "requete-annulation.md", "refere-provision": "refere-civil-835-provision.md",
          "prudhommes": "conseil-de-prud-hommes.md"}
BLOC = re.compile(r"(## Données de contrôle\s*```json\s*)(.*?)(```)", re.S)
CLE = {"remplit": "ce_qui_la_remplit", "tombe": "ce_qui_la_fait_tomber", "partage": "points_disputes"}
MOIS = "janv. févr. mars avr. mai juin juill. août sept. oct. nov. déc.".split()


def _chiffres(x: str) -> str:
    return re.sub(r"\D", "", x or "")


def _date_fr(iso: str) -> str:
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", iso or "")
    return f"{int(m.group(3))} {MOIS[int(m.group(2)) - 1]} {m.group(1)}" if m else (iso or "")


def _source(s: dict) -> str:
    return f"{s.get('juridiction', '').strip()}, {_date_fr(s.get('date', ''))}, n° {s.get('numero', '').strip()}"


_MOIS_LONGS = {"janv": 1, "févr": 2, "fevr": 2, "mars": 3, "avr": 4, "mai": 5, "juin": 6, "juil": 7, "août": 8, "aout": 8,
               "sept": 9, "oct": 10, "nov": 11, "déc": 12, "dec": 12}


def _dates_ecrites(texte: str) -> list[str]:
    """Dates ISO et dates écrites en français (« 1er mai 2021 », « 14 mars 2001 », « 7 févr. 2025 ») d'un texte libre."""
    iso = re.findall(r"\d{4}-\d{2}-\d{2}", texte)
    for j, mois, an in re.findall(r"(\d{1,2})(?:er)?\s+([a-zéû]+)\.?\s+(\d{4})", texte, re.I):
        n = next((v for k, v in _MOIS_LONGS.items() if mois.lower().startswith(k)), None)
        if n:
            iso.append(f"{an}-{n:02d}-{int(j):02d}")
    return iso


def charger_exclus() -> set[str]:
    return {_chiffres(x) for x in (ICI / "numeros_exclus.txt").read_text(encoding="utf-8").split(",") if _chiffres(x)}


def examiner(motif: dict, conditions: set[str], exclus: set[str]) -> tuple[dict | None, str]:
    texte, marqueurs, sources = str(motif.get("texte") or "").strip(), motif.get("marqueurs") or [], motif.get("sources") or []
    if motif.get("sens") not in CLE:
        return None, f"sens inconnu {motif.get('sens')!r}"
    if motif.get("condition") not in conditions:
        return None, f"condition absente de la fiche : {motif.get('condition')!r}"
    if not texte or not marqueurs:
        return None, "texte ou marqueurs manquants"
    try:
        for m in marqueurs:
            re.compile(m)
    except re.error as e:
        return None, f"marqueur invalide : {e}"
    if not sources or not all(s.get("lu_en_entier") is True and s.get("numero") for s in sources):
        return None, "source absente ou non lue en entier"
    numeros = [_chiffres(s.get("numero", "")) for s in sources] + re.findall(r"\d{6,}", _chiffres(texte) and texte)
    if any(n in exclus for n in numeros):
        return None, "décision d'épreuve du banc"
    dates = sorted(s.get("date", "") for s in sources if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s.get("date", "")))
    ecrites = _dates_ecrites(str(motif.get("depuis") or ""))
    depuis = min(ecrites) if ecrites else (dates[0] if dates else "")
    # Une source au contrat, la plus haute (Conseil d'État ou Cour de cassation d'abord) ; toutes restent dans la fiche.
    haute = next((s for s in sources if re.match(r"\s*(CE|Cass|Conseil d)", s.get("juridiction", ""))), sources[0])
    ligne = {"texte": f"{texte} ({_source(haute)})", "marqueurs": marqueurs, "sources_lues": [_source(s) for s in sources],
             "origine": "minage de la jurisprudence publique du 22 novembre 2026", "frequence": motif.get("frequence", "")}
    if depuis:
        ligne["depuis"] = depuis
    if motif.get("contre"):
        ligne["contre"] = motif["contre"]
    return ligne, ""


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    appliquer = "--appliquer" in sys.argv
    exclus = charger_exclus()
    par_fiche: dict[str, list[tuple[str, dict]]] = {}
    for nom, fiche in FICHES.items():
        f = ICI / f"{nom}.json"
        if f.exists():
            par_fiche.setdefault(fiche, []).extend((nom, m) for m in json.loads(f.read_text(encoding="utf-8")))
    for fiche, motifs in par_fiche.items():
        p = REFS / fiche
        t = p.read_text(encoding="utf-8")
        mb = BLOC.search(t)
        d = json.loads(mb.group(2))
        conds = {c["condition"]: c for c in d.get("conditions_decisives") or []}
        retenus = 0
        for nom, motif in motifs:
            ligne, raison = examiner(motif, set(conds), exclus)
            if not ligne:
                print(f"  écarté  [{nom}] {str(motif.get('texte'))[:70]!r} : {raison}")
                continue
            liste = conds[motif["condition"]].setdefault(CLE[motif["sens"]], [])
            if any((x.get("texte") if isinstance(x, dict) else x).startswith(motif["texte"].strip()[:80]) for x in liste):
                print(f"  doublon  [{nom}] {motif['texte'][:70]!r}")
                continue
            liste.append(ligne)
            retenus += 1
        print(f"{fiche} : {retenus} ligne(s) retenue(s) sur {len(motifs)}")
        if appliquer:
            p.write_text(t[:mb.start(2)] + json.dumps(d, ensure_ascii=False, indent=2) + "\n" + t[mb.end(2):], encoding="utf-8")
    if not appliquer:
        print("(contrôle seul : --appliquer pour écrire)")


if __name__ == "__main__":
    main()
