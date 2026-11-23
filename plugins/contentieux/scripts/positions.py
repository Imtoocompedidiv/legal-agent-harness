"""Registre des positions tenues devant le client : validation, contrôle avant acte, rappel, squelette.

Usage (depuis un dossier d'affaire) :
  python positions.py valider       structure et règles de strategie/positions.json
  python positions.py squelette     structure vide du fichier, à remplir (skill rapport-de-force, section 5)

Une position est une recommandation qui engage le dossier, inscrite avec sa date, son fondement et ce qui la
ferait changer. Une révision nomme l'élément nouveau qui la renverse : une pièce cotée, une source lue en entier,
une décision ou un fait daté, entré au dossier après la position. Un désaccord, une insistance ou l'avis d'un proche
du client n'en sont pas. Les contre-mesures et leur appui sont dans skills/rapport-de-force/references/complaisance.md.
Bibliothèque standard seulement, aucun appel réseau.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib_affaire as L  # noqa: E402

FICHIER = "strategie/positions.json"
TYPES = {"piece", "source", "decision", "fait"}
STATUTS = {"en_vigueur", "close"}
ISSUES = {"maintenue", "revisee"}
TYPES_REFUSES = {"desaccord", "client", "instruction", "avis", "insistance", "demande_client"}

# Ce qui, dans un élément invoqué, n'est que la volonté, l'insistance ou l'entourage du client (M2).
RE_DESACCORD = re.compile(
    r"d[ée]saccord|insist\w*|\b(à|a|sur) (la )?demande (du|de la) client|instructions? (du|de la) client"
    r"|\b(le|la) client(e)? (n'est pas d'accord|veut|souhaite|préfère|exige|maintient|conteste|refuse)"
    r"|trop prudent|avis (d'un|d'une|de son|de sa|du|de la) (proche|comptable|beau-frère|belle-sœur|ami|amie|cousin|juriste|collègue|autre avocat)"
    r"|pression (du|de la) client|le client y tient|la cliente y tient", re.I)
# Message du client qui conteste, presse ou demande de changer d'avis (M3).
RE_PRESSION = re.compile(
    r"pas d'accord|d[ée]saccord|pas convaincue?s?|(es-tu|êtes-vous|tu es|vous êtes) (bien )?s[ûu]re?s?\b|s[ûu]re? de (toi|vous)"
    r"|revo(is|yez|ir) (ta|votre|cette) (position|recommandation|analyse|copie)|chang(e|ez|er) d'avis|trop prudente?s?"
    r"|tu te trompes|vous vous trompez|je veux qu'on|je veux que (tu|vous)|j'exige|j'insiste|je maintiens"
    r"|c'est moi (le client|la cliente|qui décide|qui paie)|fai(s|tes)-le quand même|mon (avocat|comptable|beau-frère|ami|cousin|associé)"
    r"|d'autres (avocats|juristes) (disent|pensent)", re.I)
# Levier que le client propose et qui peut franchir la frontière (skill rapport-de-force, section 4).
RE_LEVIER = re.compile(
    r"menac\w*|dénonc\w*|signal(er|ons|erons|erai|ement)\b|plainte|\bpresse\b|journalis\w*|réseaux sociaux|faire peur|chantage"
    r"|en cachette|à son insu|à leur insu|enregistr\w* (la|le|les|notre|nos) (conversation|appel|réunion|échange)|antidat\w*"
    r"|(le|les|un|ce) témoins?|fausse attestation|faire pression|inonder|épuiser", re.I)
# Demande d'écrire à l'adversaire, à son avocat ou à une autorité (skill rapport-de-force, section 3).
RE_ECRIT = re.compile(
    r"(rédige|rédigez|rédiger|écris|écrivez|prépare|préparez) (la|une|notre|cette) (lettre|réponse|mise en demeure|courrier|relance|sommation)"
    r"|(écris|écrivez|écrire|répondre|réponds|répondez) (à|au|aux) (l'adversaire|l'avocat|maître|me |la société|l'administration|la partie|leur|son)"
    r"|(lettre|courrier|courriel|mail|mise en demeure|réponse) (à|au|aux) (l'adversaire|l'avocat|maître|la société|l'administration|la partie)", re.I)
MOT = re.compile(r"[a-zàâäçéèêëîïôöûùüÿœ]{5,}", re.I)


def _k(code: str, message: str, gravite: str = "BLOQUANT") -> dict:
    return {"code": code, "gravite": gravite, "message": message}


def _texte(x) -> str:
    return x.strip() if isinstance(x, str) else ""


def _jour(valeur):
    """Date d'un champ AAAA-MM-JJ ou AAAA-MM-JJTHH:MM ; None si illisible."""
    return L.date_simple(valeur) if L.parse_date(str(valeur or "")) else None


def _mots(*textes) -> set[str]:
    return {m.lower() for t in textes for m in MOT.findall(t or "")}


def _sources_lues(racine: Path | None) -> set[str] | None:
    if racine is None:
        return None
    lues = set()
    for s in (L.lire_json(racine / "etat/sources.json", {}) or {}).get("sources", []):
        if isinstance(s, dict) and s.get("lu_en_entier") is True:
            lues.update(str(s.get(k)).strip() for k in ("id", "reference") if s.get(k))
    return lues


def _cotes(racine: Path | None) -> set[str] | None:
    if racine is None:
        return None
    return {str(p.get("cote")) for p in (L.lire_json(racine / "pieces/bordereau.json", {}) or {}).get("pieces", []) if isinstance(p, dict)}


def _controle_reference(e: dict, ou: str, lues, cotes) -> list[dict]:
    """Une source invoquée est lue en entier ; une pièce invoquée est au bordereau."""
    out = []
    ref = _texte(e.get("ref"))
    if e.get("type") == "source" and lues is not None and ref not in lues:
        out.append(_k("SOURCE_NON_LUE", f"{ou} : la source « {ref[:80]} » n'est pas inscrite comme lue en entier dans etat/sources.json. "
                      "Une source se lit à la source avant de fonder ou de renverser une position (M5)."))
    if e.get("type") == "piece" and cotes is not None:
        m = re.search(r"\d+", ref)
        if not m or m.group(0) not in cotes:
            out.append(_k("PIECE_HORS_BORDEREAU", f"{ou} : la pièce « {ref[:80]} » n'est pas au bordereau (pieces/bordereau.json). "
                          "La coter avant de s'en servir.", "ALERTE"))
    return out


def valider(doc, racine: Path | None = None) -> list[dict]:
    """Constats sur le registre ; liste vide si le registre est exploitable. Avec racine, vérifie sources et pièces."""
    if not isinstance(doc, dict) or not isinstance(doc.get("positions"), list):
        return [_k("POSITIONS_INVALIDE", f"{FICHIER} doit contenir un objet avec une liste « positions ».")]
    lues, cotes = _sources_lues(racine), _cotes(racine)
    out, vus = [], set()
    for i, p in enumerate(doc["positions"]):
        ou = f"positions[{i}]"
        if not isinstance(p, dict):
            out.append(_k("POSITIONS_INVALIDE", f"{ou} n'est pas un objet."))
            continue
        pid = _texte(p.get("id")) or ou
        ou = f"position {pid}"
        manque = [c for c in ("id", "objet", "position", "date") if not _texte(p.get(c))]
        if manque:
            out.append(_k("POSITIONS_INVALIDE", f"{ou} : champ(s) {', '.join(manque)} absent(s) ou vide(s)."))
        if pid in vus:
            out.append(_k("ID_DOUBLE", f"Identifiant {pid} déclaré deux fois."))
        vus.add(pid)
        statut = p.get("statut", "en_vigueur")
        if statut not in STATUTS:
            out.append(_k("POSITIONS_INVALIDE", f"{ou} : statut « {statut} » ; valeurs permises {sorted(STATUTS)}."))
        elif statut == "close" and not _texte(p.get("motif_cloture")):
            out.append(_k("POSITIONS_INVALIDE", f"{ou} : une position close dit pourquoi (motif_cloture)."))
        debut = _jour(p.get("date"))
        if _texte(p.get("date")) and debut is None:
            out.append(_k("DATE_INVALIDE", f"{ou} : date « {p.get('date')} » illisible (AAAA-MM-JJ ou AAAA-MM-JJTHH:MM)."))
        fondement = p.get("fondement")
        if not isinstance(fondement, list) or not fondement:
            out.append(_k("FONDEMENT_ABSENT", f"{ou} : aucun fondement. Une position s'appuie sur des pièces cotées, des sources lues, "
                          "des décisions ou des faits datés (type, ref)."))
        else:
            for j, f in enumerate(fondement):
                if not isinstance(f, dict) or f.get("type") not in TYPES or not _texte(f.get("ref")):
                    out.append(_k("FONDEMENT_ABSENT", f"{ou}, fondement {j + 1} : objet attendu avec type parmi {sorted(TYPES)} et ref."))
                else:
                    out += _controle_reference(f, f"{ou}, fondement {j + 1}", lues, cotes)
        declencheurs = [d for d in p.get("ferait_changer") or [] if _texte(d)] if isinstance(p.get("ferait_changer"), list) else []
        if not declencheurs:
            out.append(_k("DECLENCHEURS_ABSENTS", f"{ou} : ferait_changer vide. Écrire, avant toute contestation, les éléments qui "
                          "renverseraient la position (M1)."))
        out += _revisions(p, ou, debut, declencheurs, lues, cotes)
        out += _desaccords(p, ou)
        for j, ins in enumerate(p.get("instructions") or []):
            if not isinstance(ins, dict) or not all(_texte(ins.get(c)) for c in ("date", "instruction", "risque_dit")) or _jour(ins.get("date")) is None:
                out.append(_k("INSTRUCTION_INCOMPLETE", f"{ou}, instruction {j + 1} : date lisible, instruction du client et risque_dit "
                              "(le risque dit au client, une fois) sont requis. L'instruction ne change pas la position (M6)."))
    return out


def _revisions(p: dict, ou: str, debut, declencheurs: list[str], lues, cotes) -> list[dict]:
    out = []
    revisions = p.get("revisions") or []
    if not isinstance(revisions, list):
        return [_k("POSITIONS_INVALIDE", f"{ou} : revisions doit être une liste.")]
    precedent = debut
    for j, r in enumerate(sorted((r for r in revisions if isinstance(r, dict)), key=lambda r: str(r.get("date") or ""))):
        rou = f"{ou}, révision du {r.get('date') or '?'}"
        jour = _jour(r.get("date"))
        if jour is None:
            out.append(_k("DATE_INVALIDE", f"{rou} : date illisible."))
        if not _texte(r.get("motif")):
            out.append(_k("REVISION_SANS_MOTIF", f"{rou} : dire en quoi l'élément renverse la position (motif)."))
        e = r.get("element")
        if not isinstance(e, dict) or not _texte(e.get("ref")):
            out.append(_k("REVISION_SANS_ELEMENT", f"{rou} : aucun élément nouveau nommé. Une position ne change que sur une pièce cotée, "
                          "une source lue, une décision ou un fait daté, nommé dans la révision (élément : type, ref, connu_le)."))
            precedent = jour or precedent
            continue
        decrit = f"{_texte(e.get('ref'))} {_texte(e.get('description'))}"
        if str(e.get("type")) in TYPES_REFUSES or RE_DESACCORD.search(decrit):
            out.append(_k("DESACCORD_N_EST_PAS_UN_ELEMENT", f"{rou} : « {decrit.strip()[:120]} » n'est qu'un désaccord, une insistance ou "
                          "l'avis d'un tiers. Sans élément nouveau, la position est maintenue ; si le client maintient sa demande, "
                          "l'inscrire dans instructions (M2, M6)."))
        elif e.get("type") not in TYPES:
            out.append(_k("ELEMENT_TYPE_INCONNU", f"{rou} : type « {e.get('type')} » ; types admis {sorted(TYPES)}."))
        connu = _jour(e.get("connu_le")) or _jour(e.get("date"))
        if connu is None:
            out.append(_k("REVISION_SANS_ELEMENT", f"{rou} : l'élément n'est pas daté (connu_le : date de son entrée au dossier)."))
        elif precedent is not None and connu < precedent and not _texte(r.get("erreur")):
            out.append(_k("ELEMENT_DEJA_CONNU", f"{rou} : l'élément était au dossier le {connu.isoformat()}, avant la position du "
                          f"{precedent.isoformat()} ; il ne peut pas la renverser, sauf erreur d'analyse nommée (champ erreur)."))
        if e.get("type") in TYPES:
            out += _controle_reference(e, rou, lues, cotes)
            if declencheurs and not (_mots(decrit, r.get("motif")) & _mots(*declencheurs)):
                out.append(_k("REVISION_HORS_DECLENCHEURS", f"{rou} : l'élément ne correspond à aucun déclencheur inscrit "
                              f"({'; '.join(declencheurs)[:160]}). Le motif doit dire pourquoi il décide quand même.", "ALERTE"))
        precedent = jour or precedent
    return out


def _desaccords(p: dict, ou: str) -> list[dict]:
    out = []
    dates_revisions = [_jour(r.get("date")) for r in p.get("revisions") or [] if isinstance(r, dict)]
    for j, d in enumerate(p.get("desaccords") or []):
        dou = f"{ou}, désaccord {j + 1}"
        if not isinstance(d, dict) or not all(_texte(d.get(c)) for c in ("date", "objection", "examen")) or d.get("issue") not in ISSUES:
            out.append(_k("DESACCORD_SANS_EXAMEN", f"{dou} : date, objection du client, examen (la position et l'objection jugées côte à côte) "
                          f"et issue parmi {sorted(ISSUES)} sont requis (M4)."))
            continue
        jour = _jour(d.get("date"))
        if d["issue"] == "revisee" and not any(x and jour and x >= jour for x in dates_revisions):
            out.append(_k("DESACCORD_SANS_EXAMEN", f"{dou} : issue « revisee » sans révision inscrite à cette date ou après, avec son élément."))
    return out


def charger(racine: Path) -> tuple[dict | None, list[dict]]:
    chemin = racine / FICHIER
    if not chemin.is_file():
        return None, []
    try:
        doc = json.loads(chemin.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return None, [_k("POSITIONS_INVALIDE", f"{FICHIER} n'est pas un JSON valide (ligne {e.lineno}, colonne {e.colno}) : {e.msg}.")]
    constats = valider(doc, racine)
    return (doc if not any(k["code"] == "POSITIONS_INVALIDE" for k in constats) else None), constats


def controler(racine: Path, c) -> None:
    """Contrôle avant un acte, au format de gate.py : c(code, gravite, message)."""
    doc, constats = charger(racine)
    if doc is None and not constats:
        c("POSITIONS_ABSENTES", "ALERTE", f"{FICHIER} absent : les recommandations données au client ne sont pas inscrites avec leur "
          "fondement et ce qui les ferait changer (skill rapport-de-force, section 5).")
        return
    for k in constats:
        c(k["code"], k["gravite"], k["message"])


def en_vigueur(racine: Path) -> list[dict]:
    doc = L.lire_json(racine / FICHIER) or {}
    return [p for p in doc.get("positions", []) if isinstance(p, dict) and p.get("statut", "en_vigueur") == "en_vigueur"] \
        if isinstance(doc, dict) and isinstance(doc.get("positions"), list) else []


def rappel(racine: Path, prompt: str) -> list[str]:
    """Lignes que le hook UserPromptSubmit injecte au tour même où le client conteste, propose un levier ou demande un écrit (M3)."""
    lignes = []
    if RE_PRESSION.search(prompt or ""):
        lignes.append("Désaccord ou pression du client. Relire strategie/positions.json, puis juger côte à côte la position et l'objection, "
                      "comme un associé extérieur au dossier. La position ne change que sur un élément nouveau nommé : pièce cotée, "
                      "source lue en entier, décision, fait daté, entré au dossier après elle. Un désaccord, une insistance, l'avis d'un "
                      "proche ou un précédent non lu n'en sont pas. Sans élément, maintenir, dire pourquoi et ce qui la ferait changer. "
                      "Avec l'élément, réviser tout de suite en le nommant. Si le client maintient une instruction contraire, la consigner "
                      "sans renier l'analyse (skill rapport-de-force, section 5).")
        for p in en_vigueur(racine)[:5]:
            fc = "; ".join(str(x) for x in p.get("ferait_changer") or [])
            lignes.append(f"Position {p.get('id')} ({p.get('date')}) : « {str(p.get('position'))[:160]} » ; ferait changer : {fc[:200]}.")
    if RE_LEVIER.search(prompt or ""):
        lignes.append("Levier proposé : le confronter à la frontière (rapport-de-force, references/limites.md). Refuser ce qui la franchit "
                      "en nommant le texte, puis rédiger le coup licite le plus dur qui vise le même résultat.")
    if RE_ECRIT.search(prompt or ""):
        lignes.append("Écrit destiné à l'adversaire : il obtient un effet de droit ou une réponse, et ne révèle ni faiblesse, ni marge, "
                      "ni argument gardé en réserve, ni vice qu'il peut encore réparer ; aucune concession ni main tendue sans contrepartie ; "
                      "le fichier ne contient que l'écrit, sans note de travail ni commentaire (rapport-de-force, section 3).")
    return lignes


SQUELETTE = {
    "schema": "positions/1",
    "positions": [{
        "id": "P1", "objet": "", "position": "", "date": "", "statut": "en_vigueur", "actes": [""],
        "fondement": [{"type": "piece", "ref": "pièce 4"}, {"type": "source", "ref": "S1"}],
        "ferait_changer": [""],
        "revisions": [{"date": "", "ancienne_position": "", "nouvelle_position": "",
                       "element": {"type": "piece", "ref": "", "date": "", "connu_le": "", "description": ""},
                       "erreur": "", "motif": ""}],
        "desaccords": [{"date": "", "objection": "", "examen": "", "issue": "maintenue"}],
        "instructions": [{"date": "", "instruction": "", "risque_dit": ""}],
    }],
}


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--racine", help="dossier d'affaire (par défaut : celui qui contient le répertoire courant)")
    sp = p.add_subparsers(dest="cmd", required=True)
    sp.add_parser("valider")
    sp.add_parser("squelette")
    a = p.parse_args(argv)
    if a.cmd == "squelette":
        print(json.dumps(SQUELETTE, ensure_ascii=False, indent=2))
        return 0
    racine = L.trouver_racine(a.racine or Path.cwd())
    if racine is None:
        print("Hors d'un dossier d'affaire (etat/affaire.json introuvable).", file=sys.stderr)
        return 2
    doc, constats = charger(racine)
    if doc is None and not constats:
        print(f"{FICHIER} absent.")
        return 1
    for k in constats:
        print(f"- {k['gravite']} {k['code']} : {k['message']}")
    bloquants = sum(1 for k in constats if k["gravite"] == "BLOQUANT")
    print(f"{FICHIER} : {'valide' if not bloquants else 'à reprendre'} ({bloquants} bloquant(s), {len(constats) - bloquants} alerte(s)).")
    return 1 if bloquants else 0


if __name__ == "__main__":
    sys.exit(main())
