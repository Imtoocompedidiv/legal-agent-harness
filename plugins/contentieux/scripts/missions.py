"""Catalogue des missions de conseil et validateur de leurs fiches.

Chaque pôle de conseil est un skill (`skills/<pôle>/SKILL.md`) dont les fiches de mission (`skills/<pôle>/references/*.md`) portent un
bloc « Données de contrôle » au même schéma que les fiches d'exercice (`exercices.py`) : le hook en tire le même contrat compact.

Commandes :
  python missions.py liste                  identifiants, pôle et fiche de chaque mission
  python missions.py verifier [pôle]        contrôle du gabarit, du bloc et des marqueurs ; code 1 si un défaut bloque
  python missions.py contrat <identifiant>  contrat compact que le hook injectera pour cette mission
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exercices as E  # noqa: E402

SKILLS = Path(__file__).resolve().parents[1] / "skills"
POLES = ("contrats-d-affaires", "societes-et-operations", "droit-social", "donnees-personnelles", "intelligence-artificielle",
         "propriete-intellectuelle", "conformite-et-produits", "precontentieux-et-portefeuille", "formation-juridique", "acces-au-droit")
SECTIONS = ("## 1. ", "## 2. ", "## 3. ", "## 4. ", "## 5. ", "## 6. ", "## 7. ", "## 8. ", "## 9. ", "## 10. Statistiques publiées",
            "## 11. Points non vérifiés", "## Sources", "## Données de contrôle")
TIRET_CADRATIN = "—"


def charger_missions(poles: tuple[str, ...] = POLES) -> dict[str, dict]:
    """Identifiant -> données de contrôle de la fiche, avec « fichier » (nom) et « pole » (skill)."""
    missions: dict[str, dict] = {}
    for p in poles:
        for i, d in E.charger_catalogue(SKILLS / p / "references").items():
            missions[i] = {**d, "pole": p}
    return missions


def _textes(v) -> list[str]:
    if isinstance(v, str):
        return [v]
    if isinstance(v, dict):
        return [t for x in v.values() for t in _textes(x)]
    if isinstance(v, list):
        return [t for x in v for t in _textes(x)]
    return []


def verifier(pole: str | None = None) -> list[tuple[str, str, str]]:
    """Liste de (gravité, fiche, message). Gravité BLOQUANT ou ALERTE."""
    defauts: list[tuple[str, str, str]] = []
    exercices = E.charger_catalogue()
    tous = charger_missions()
    poles = (pole,) if pole else POLES
    vus_marqueurs: dict[str, str] = {m: i for i, d in exercices.items() for m in d.get("marqueurs_texte") or []}
    noms_exercices = {d["fichier"] for d in exercices.values()}
    noms_vus: dict[str, str] = {d["fichier"]: d["pole"] for d in tous.values()}
    for p in poles:
        dossier = SKILLS / p / "references"
        skill = SKILLS / p / "SKILL.md"
        if not skill.exists():
            defauts.append(("BLOQUANT", p, "SKILL.md absent"))
            continue
        texte_skill = skill.read_text(encoding="utf-8")
        if TIRET_CADRATIN in texte_skill:
            defauts.append(("BLOQUANT", f"{p}/SKILL.md", "tiret cadratin"))
        if not re.match(r"---\s*\nname:\s*" + re.escape(p) + r"\s*\ndescription:", texte_skill):
            defauts.append(("BLOQUANT", f"{p}/SKILL.md", "en-tête attendu : name puis description"))
        for f in sorted(dossier.glob("*.md")) if dossier.is_dir() else []:
            t = f.read_text(encoding="utf-8")
            nom = f"{p}/{f.name}"
            if TIRET_CADRATIN in t:
                defauts.append(("BLOQUANT", nom, "tiret cadratin"))
            if "## Données de contrôle" not in t:
                continue  # fiche de positions ou d'annexe
            if f.name not in texte_skill:
                defauts.append(("BLOQUANT", nom, "fiche non citée par le SKILL.md du pôle"))
            # Le hook reconnaît une fiche lue à son nom de fichier : il doit être unique parmi exercices et missions.
            if f.name in noms_exercices or noms_vus.setdefault(f.name, p) != p:
                defauts.append(("BLOQUANT", nom, "nom de fichier déjà employé par un exercice ou un autre pôle"))
            manque = [s for s in SECTIONS if s not in t]
            if manque:
                defauts.append(("BLOQUANT", nom, "sections absentes : " + ", ".join(manque)))
            d = next((x for x in tous.values() if x["fichier"] == f.name and x["pole"] == p), None)
            if d is None:
                defauts.append(("BLOQUANT", nom, "bloc « Données de contrôle » illisible (JSON invalide ou sans id)"))
                continue
            i = d["id"]
            cles = set(d) - {"fichier", "pole"}
            if E.CLES_DONNEES - cles:
                defauts.append(("BLOQUANT", nom, "clés absentes : " + ", ".join(sorted(E.CLES_DONNEES - cles))))
            if cles - E.CLES_DONNEES - E.CLES_FACULTATIVES:
                defauts.append(("BLOQUANT", nom, "clés inconnues : " + ", ".join(sorted(cles - E.CLES_DONNEES - E.CLES_FACULTATIVES))))
            if i in exercices:
                defauts.append(("BLOQUANT", nom, f"identifiant {i} déjà pris par un exercice"))
            if d.get("famille") != "conseil" or d.get("juridictionnel") is not False:
                defauts.append(("BLOQUANT", nom, "famille « conseil » et juridictionnel false attendus"))
            conds = [c for c in d.get("conditions_decisives") or [] if isinstance(c, dict)]
            if d.get("condition_principale") not in {c.get("condition") for c in conds}:
                defauts.append(("BLOQUANT", nom, "condition_principale absente de conditions_decisives"))
            for c in conds:
                lignes = c.get("ce_qui_la_fait_tomber") or []
                if not lignes or not all(isinstance(x, str) and x.strip() for x in lignes):
                    defauts.append(("BLOQUANT", nom, f"« {c.get('condition')} » : ce_qui_la_fait_tomber vide ou mal formé"))
                if not str(c.get("source") or "").strip():
                    defauts.append(("BLOQUANT", nom, f"« {c.get('condition')} » : source absente"))
            for x in d.get("exigences_implicites") or []:
                if not (isinstance(x, dict) and x.get("cle") and x.get("exigence") and str(x.get("source") or "").strip()):
                    defauts.append(("BLOQUANT", nom, f"exigence implicite incomplète (cle, exigence, source) : {x}"))
            for v in d.get("voisins") or []:
                cible = str((v or {}).get("exercice") or "")
                if not (cible in tous or cible in exercices or cible.startswith("autre:")):
                    defauts.append(("ALERTE", nom, f"voisin inconnu : {cible}"))
            marqueurs = d.get("marqueurs_texte") or []
            if len(marqueurs) < 2:
                defauts.append(("BLOQUANT", nom, "deux marqueurs_texte au moins"))
            for m in marqueurs:
                try:
                    re.compile(m)
                except re.error as e:
                    defauts.append(("BLOQUANT", nom, f"marqueur invalide {m!r} : {e}"))
                    continue
                if m in vus_marqueurs and vus_marqueurs[m] != i:
                    defauts.append(("ALERTE", nom, f"marqueur {m!r} déjà employé par {vus_marqueurs[m]}"))
                vus_marqueurs.setdefault(m, i)
                if re.search(m, "Bonjour, pouvez-vous me rappeler demain matin ? Merci.", re.I):
                    defauts.append(("BLOQUANT", nom, f"marqueur {m!r} trop large"))
            if any(TIRET_CADRATIN in s for s in _textes(d)):
                defauts.append(("BLOQUANT", nom, "tiret cadratin dans le bloc"))
    return defauts


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd, args = argv[0], argv[1:]
    if cmd == "liste":
        for i, d in sorted(charger_missions().items(), key=lambda x: (x[1]["pole"], x[0])):
            print(f"{d['pole']:32} {i:44} {d['fichier']}")
        return 0
    if cmd == "verifier":
        defauts = verifier(args[0] if args else None)
        for g, f, m in defauts:
            print(f"{g:8} {f} : {m}")
        n = sum(1 for g, _, _ in defauts if g == "BLOQUANT")
        print(f"{len(charger_missions())} mission(s), {n} défaut(s) bloquant(s), {len(defauts) - n} alerte(s).")
        return 1 if n else 0
    if cmd == "contrat" and args:
        import hook as H
        d = charger_missions().get(args[0])
        if not d:
            print(f"mission inconnue : {args[0]}")
            return 1
        print(H.contrat_compact(d, SKILLS / d["pole"] / "references" / d["fichier"]))
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
