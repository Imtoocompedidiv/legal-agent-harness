"""Hook PreToolUse des sondes du banc : chaque sonde ne voit que son dossier et le droit à sa date.

Paramètres d'environnement : BANC_DOSSIER (identifiant de la sonde, en minuscules), BANC_COUPE (AAAA-MM-JJ, 9999-12-31 sans borne).
Seuls les chemins et commandes sont examinés, jamais le contenu écrit. Fermé par défaut : une erreur vaut refus.
"""
import json
import os
import re
import sys

COUPE = os.environ.get("BANC_COUPE", "9999-12-31")
DOSSIER = os.environ.get("BANC_DOSSIER", "").lower()
INTERDITS = ("/validation/", "validation\\", "essais-contentieux", "verite", "/corpus")


def refuser(raison: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": raison}}, ensure_ascii=True))
    sys.exit(0)


MOIS = {m: i for i, m in enumerate("janvier février mars avril mai juin juillet août septembre octobre novembre décembre".split(), 1)}


def date_titre(titre: str) -> str | None:
    m = re.search(r"(\d{1,2})(?:er)? (" + "|".join(MOIS) + r") (\d{4})", titre or "")
    return f"{m.group(3)}-{MOIS[m.group(2)]:02d}-{int(m.group(1)):02d}" if m else None


def apres(ev: dict) -> None:
    """PostToolUse : une décision postérieure à la coupe ne se lit pas, et la chronologie de l'affaire s'arrête à la coupe."""
    brut = ev.get("tool_response")
    texte = brut if isinstance(brut, str) else "".join(b.get("text", "") for b in brut if isinstance(b, dict)) if isinstance(brut, list) else None
    doc = json.loads(texte) if texte else brut if isinstance(brut, dict) else None
    if not isinstance(doc, dict):
        sys.exit(0)
    if str(doc.get("date") or "")[:10] > COUPE:
        doc = {"refus": f"Décision du {doc.get('date')} postérieure à la date de la sonde ({COUPE}) : hors champ, ni lue ni citée."}
    else:
        # « standing » dit si la décision a été frappée d'un recours ou cassée : état connu aujourd'hui, non à la date de la sonde.
        doc.pop("standing", None)
        chrono = doc.get("case_chronology")
        if isinstance(chrono, list):
            gardees = [c for c in chrono if not (date_titre(c.get("title", "")) or "0") > COUPE]
            if len(gardees) < len(chrono):
                for c in gardees:
                    c.pop("link_to_next", None)
            doc["case_chronology"] = gardees
    sortie = json.dumps(doc, ensure_ascii=False)
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "updatedMCPToolOutput":
                      sortie if not isinstance(brut, list) else [{"type": "text", "text": sortie}]}}, ensure_ascii=True))
    sys.exit(0)


def main() -> None:
    ev = json.load(sys.stdin)
    outil = ev.get("tool_name", "")
    if ev.get("hook_event_name") == "PostToolUse":
        if COUPE != "9999-12-31" and outil == "mcp__librejustice__get_decision":
            apres(ev)
        sys.exit(0)
    ti = ev.get("tool_input") or {}
    if COUPE != "9999-12-31":
        if outil == "mcp__librejustice__search_decisions":
            d = str(ti.get("date_to") or "")
            if not d or d[:10] > COUPE:
                refuser(f"Sonde datée du {COUPE} : toute recherche de jurisprudence porte date_to au plus tard le {COUPE}.")
        if outil in ("mcp__librejustice__get_norm", "mcp__librejustice__search_norms"):
            d = str(ti.get("as_of") or "")
            if not d or d[:10] > COUPE:
                refuser(f"Sonde datée du {COUPE} : lire le texte dans sa version à cette date (as_of au plus tard le {COUPE}).")
    if outil in ("Read", "Grep", "Glob", "Bash", "PowerShell", "Edit", "Write", "NotebookEdit"):
        cibles = {k: ti.get(k) for k in ("file_path", "path", "pattern", "glob", "command", "notebook_path") if ti.get(k)}
        brut = json.dumps(cibles, ensure_ascii=False).lower().replace("\\\\", "/").replace("\\", "/")
        if any(m.replace("\\", "/") in brut for m in INTERDITS):
            refuser("Sonde à l'aveugle : ce chemin est hors du dossier de la sonde et du plugin.")
        plugin = os.environ.get("BANC_PLUGIN", "").lower().replace("\\", "/")
        for nom in re.findall(r"banc_runs/[^/\"' ]+/([^/\"' ]+)", brut):
            # Le plugin mesuré peut être une copie figée rangée sous banc_runs : il reste lisible en entier.
            if plugin and plugin in brut:
                continue
            if nom != DOSSIER:
                refuser("Sonde à l'aveugle : les dossiers des autres sondes ne se lisent pas.")
        if "/.claude/projects/" in brut and DOSSIER not in brut:
            refuser("Sonde à l'aveugle : les mémoires et transcriptions d'autres sessions ne se lisent pas.")
        if "../" in brut:
            refuser("Sonde à l'aveugle : pas de chemin relatif qui remonte hors du dossier de la sonde.")
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        refuser(f"Hook d'aveugle en erreur ({type(e).__name__}) : action refusée par prudence.")
