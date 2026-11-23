"""Usine à sondes : des décisions publiques, la vérité de l'issue, des sondes de pronostic sans anachronisme, équilibrées.

    python usine.py collecter <famille> [--n 16] [--depuis AAAA-MM-JJ]   session sans rédaction : recherches et lectures,
                                                                          captées par le hook du plugin dans banc_runs/usine/<famille>/
    python usine.py fabriquer <famille> [--max 12]                       dossiers et sondes GEN-<code>-<numéro>, autant de oui que de non
    python usine.py familles

Chaque famille dit où couper la décision (avant le raisonnement du juge) et comment lire son issue. Le dossier ne garde que
la procédure et les prétentions des parties ; la sonde est datée de la veille de la décision, et le hook d'aveugle borne
les outils à cette date. Une décision dont l'issue ne se lit pas sans ambiguïté est écartée.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from nettoyer_cassation import nettoyer

BANC = Path(__file__).resolve().parent
RACINE = BANC.parent.parent
PLUGIN = RACINE / "plugins" / "contentieux"
USINE = RACINE / "banc_runs" / "usine"
URG_NON = re.compile(r"(?:condition (?:tenant à l.|d.)urgence|l.urgence)[^.]{0,160}(?:n.est pas (?:remplie|satisfaite|caractérisée|établie|justifiée)|"
                     r"fait défaut|ne (?:peut|saurait) (?:être regardée|être considérée)|pas regardée comme (?:remplie|satisfaite))|"
                     r"défaut d.urgence|absence d.urgence|faute d.urgence", re.I)
URG_OUI = re.compile(r"(?:condition d.urgence|l.urgence|situation d.urgence)[^.]{0,120}(?:est (?:remplie|satisfaite|caractérisée|établie)|"
                     r"doit (?:donc )?être regardée comme (?:remplie|satisfaite))", re.I)

# Garde-fou permanent (20 novembre) : l'en-tête d'un arrêt de la Cour de cassation annonce son issue (« Rejet », « Cassation
# partielle ») ; ces lignes se retirent, et un dossier où une issue reste lisible est écarté.
LIGNE_ISSUE = re.compile(r"(?im)^\s*(?:cassation(?: partielle| sans renvoi)?|rejet|non-admission|irrecevabilité|déchéance|désistement|"
                         r"ordonne|o r d o n n e|d[ée]cide)\s*:?\s*$")
# La Cour écarte d'avance, avant sa réponse, les moyens « manifestement pas de nature à entraîner la cassation » (CPC, art. 1014) :
# c'est déjà son jugement, il se retire du dossier.
PHRASE_ISSUE = re.compile(r"[^.\n]*(?:pas lieu de statuer par une décision spécialement motivée|n.est manifestement pas de nature à entraîner la cassation)[^.\n]*\.?", re.I)
FUITE = re.compile(r"(?i)\b(?:casse et annule|rejette le pourvoi|ordonne la suspension|est suspendue|par ces motifs)\b")

FAMILLES = {
    "urgence-l521-1": {
        "code": "URG",
        "recherches": [
            {"query": "référé-suspension condition d'urgence remplie atteinte grave et immédiate", "legal_article": ["code-de-justice-administrative|L521-1"],
             "seat": ["FR.TA"], "solution": ["GRANTED", "PARTLY_GRANTED"]},
            {"query": "référé-suspension défaut d'urgence la condition d'urgence n'est pas remplie", "legal_article": ["code-de-justice-administrative|L521-1"],
             "seat": ["FR.TA"], "solution": ["DISMISSED"]},
            {"query": "suspension sanction disciplinaire agent public, la condition d'urgence n'est pas remplie, traitement", "legal_article": ["code-de-justice-administrative|L521-1"],
             "seat": ["FR.TA"], "solution": ["DISMISSED"]},
            {"query": "permis de construire ou autorisation d'urbanisme, référé-suspension, l'urgence n'est pas établie", "legal_article": ["code-de-justice-administrative|L521-1"],
             "seat": ["FR.TA"], "solution": ["DISMISSED"]},
            {"query": "refus de titre de séjour, référé-suspension, la condition d'urgence n'est pas satisfaite", "legal_article": ["code-de-justice-administrative|L521-1"],
             "seat": ["FR.TA"], "solution": ["DISMISSED"]},
        ],
        "coupe": r"\n\s*Considérant ce qui suit\s*:",
        "question": "En te plaçant comme le juge des référés, dis si la condition d'urgence de ce référé-suspension est remplie. "
                    "Réponds d'abord par oui ou par non, puis motive en dix lignes au plus. Réponds directement, de façon précise et motivée, "
                    "sans dérouler la chaîne complète de prise en main du dossier.",
    },
    "refere-liberte": {
        "code": "LIB",
        "recherches": [
            {"query": "référé-liberté atteinte grave et manifestement illégale à une liberté fondamentale, injonction", "legal_article": ["code-de-justice-administrative|L521-2"],
             "seat": ["FR.TA"], "solution": ["GRANTED", "PARTLY_GRANTED"]},
            {"query": "référé-liberté rejet, pas d'atteinte grave et manifestement illégale ou urgence particulière non établie", "legal_article": ["code-de-justice-administrative|L521-2"],
             "seat": ["FR.TA"], "solution": ["DISMISSED"]},
        ],
        "coupe": r"\n\s*Considérant ce qui suit\s*:",
        "question": "En te plaçant comme le juge des référés, dis s'il fera droit, au moins en partie, à cette demande de référé-liberté. "
                    "Réponds d'abord par oui ou par non, puis motive en dix lignes au plus. Réponds directement, de façon précise et motivée, "
                    "sans dérouler la chaîne complète de prise en main du dossier.",
    },
    # Variantes hors échantillon des défauts corrigés le 22 novembre (METHODE, point 27) : d'autres décisions sur les mêmes points.
    "urgence-titre-renouvellement": {
        "code": "URGT",
        "recherches": [
            {"query": "référé-suspension refus de renouvellement du titre de séjour ou de la carte de résident, récépissé ou autorisation provisoire de séjour, urgence présumée remplie",
             "legal_article": ["code-de-justice-administrative|L521-1"], "seat": ["FR.TA"], "solution": ["GRANTED", "PARTLY_GRANTED"]},
            {"query": "référé-suspension refus de renouvellement du titre de séjour, la condition d'urgence n'est pas remplie, circonstances particulières",
             "legal_article": ["code-de-justice-administrative|L521-1"], "seat": ["FR.TA"], "solution": ["DISMISSED"]},
        ],
        "coupe": r"\n\s*Considérant ce qui suit\s*:",
        "question": "En te plaçant comme le juge des référés, dis si la condition d'urgence de ce référé-suspension est remplie. "
                    "Réponds d'abord par oui ou par non, puis motive en dix lignes au plus. Réponds directement, de façon précise et motivée, "
                    "sans dérouler la chaîne complète de prise en main du dossier.",
    },
    # Hors échantillon de la règle du renouvellement tardif (fiche du 22 novembre, CESEDA, art. R. 431-5), fixée avant la collecte :
    # des refus jugés sur la date de la demande, dans les deux sens. Les décisions déjà sondées sous un autre code sont écartées.
    "titre-renouvellement-delai": {
        "code": "URGD",
        "recherches": [
            {"query": "référé-suspension refus de renouvellement du titre de séjour, demande de renouvellement présentée dans le délai, présomption d'urgence, suspension",
             "legal_article": ["code-de-l-entree-et-du-sejour-des-etrangers-et-du-droit-d-asile|R431-5"], "seat": ["FR.TA"],
             "solution": ["GRANTED", "PARTLY_GRANTED"]},
            {"query": "référé-suspension refus de renouvellement du titre de séjour, demande présentée après le délai, première demande, pas de présomption d'urgence",
             "legal_article": ["code-de-l-entree-et-du-sejour-des-etrangers-et-du-droit-d-asile|R431-5"], "seat": ["FR.TA"],
             "solution": ["DISMISSED"]},
        ],
        "coupe": r"\n\s*Considérant ce qui suit\s*:",
        "question": "En te plaçant comme le juge des référés, dis si la condition d'urgence de ce référé-suspension est remplie. "
                    "Réponds d'abord par oui ou par non, puis motive en dix lignes au plus. Réponds directement, de façon précise et motivée, "
                    "sans dérouler la chaîne complète de prise en main du dossier.",
    },
    # Familles nouvelles du 22 novembre (minage de la requête en annulation et du référé-provision) : mesure hors échantillon.
    "annulation-ta": {
        "code": "ANNT",
        "recherches": [
            {"query": "recours pour excès de pouvoir, annulation de la décision attaquée, illégalité, injonction de réexaminer",
             "seat": ["FR.TA"], "formation": ["FR.TA.A_TROIS"], "solution": ["GRANTED", "PARTLY_GRANTED"]},
            {"query": "recours pour excès de pouvoir, aucun des moyens n'est fondé, rejet de la requête",
             "seat": ["FR.TA"], "formation": ["FR.TA.A_TROIS"], "solution": ["DISMISSED"]},
        ],
        "coupe": r"\n\s*Considérant ce qui suit\s*:",
        "question": "En te plaçant comme le tribunal administratif, dis s'il annulera, au moins en partie, la décision attaquée. "
                    "Réponds d'abord par oui ou par non, puis motive en dix lignes au plus. Réponds directement, de façon précise et motivée, "
                    "sans dérouler la chaîne complète de prise en main du dossier.",
    },
    "refere-provision-civil": {
        "code": "PROV",
        "recherches": [
            {"query": "référé provision obligation non sérieusement contestable, condamnation au paiement d'une provision",
             "legal_article": ["code-de-procedure-civile|835"], "seat": ["FR.TJ"], "solution": ["GRANTED", "PARTLY_GRANTED"]},
            {"query": "référé provision contestation sérieuse, n'y a pas lieu à référé, demande de provision rejetée",
             "legal_article": ["code-de-procedure-civile|835"], "seat": ["FR.TJ"], "solution": ["DISMISSED"]},
        ],
        "coupe": r"\n\s*(?:MOTIFS DE LA DÉCISION|MOTIFS|SUR CE|Sur ce|Motifs de la décision|EXPOSÉ DES MOTIFS)\s*[:,]?\s*\n",
        "question": "En te plaçant comme le juge des référés, dis s'il allouera, au moins en partie, la provision demandée. "
                    "Réponds d'abord par oui ou par non, puis motive en dix lignes au plus. Réponds directement, de façon précise et motivée, "
                    "sans dérouler la chaîne complète de prise en main du dossier.",
    },
    "liberte-eloignement": {
        "code": "LIBE",
        "recherches": [
            {"query": "référé-liberté exécution de l'obligation de quitter le territoire, changement de circonstances, injonction d'organiser le retour en France",
             "legal_article": ["code-de-justice-administrative|L521-2"], "seat": ["FR.TA"], "solution": ["GRANTED", "PARTLY_GRANTED"]},
            {"query": "référé-liberté contre l'exécution d'une obligation de quitter le territoire définitive, absence de changement de circonstances, rejet",
             "legal_article": ["code-de-justice-administrative|L521-2"], "seat": ["FR.TA"], "solution": ["DISMISSED"]},
        ],
        "coupe": r"\n\s*Considérant ce qui suit\s*:",
        "question": "En te plaçant comme le juge des référés, dis s'il fera droit, au moins en partie, à cette demande de référé-liberté. "
                    "Réponds d'abord par oui ou par non, puis motive en dix lignes au plus. Réponds directement, de façon précise et motivée, "
                    "sans dérouler la chaîne complète de prise en main du dossier.",
    },
    # Même collection, sans l'arrêt attaqué : il reste trouvable sur LibreJustice (cour et date dans « Faits et procédure »).
    # La famille mesure si le plugin fait chercher et lire la décision attaquée avant le pronostic.
    "cassation-a-chercher": {
        "code": "CASSN",
        "source": "cassation-civile",
        "attaquee_requise": True,
        "recherches": [],
        "coupe": r"\n\s*Réponse de la Cour",
        "question": "En te plaçant comme la chambre de la Cour de cassation, dis si l'arrêt attaqué doit être cassé, au moins en partie. "
                    "Réponds d'abord par oui ou par non, puis motive en dix lignes au plus. Réponds directement, de façon précise et motivée, "
                    "sans dérouler la chaîne complète de prise en main du dossier.",
    },
    "cassation-civile": {
        "code": "CASSA",
        "recherches": [
            {"query": "cassation violation de la loi manque de base légale", "seat": ["FR.CC"], "solution": ["GRANTED", "PARTLY_GRANTED"],
             "publication": ["PUBLIE_BULLETIN"]},
            {"query": "rejet du pourvoi le moyen n'est pas fondé", "seat": ["FR.CC"], "solution": ["DISMISSED"], "publication": ["PUBLIE_BULLETIN"]},
        ],
        "coupe": r"\n\s*Réponse de la Cour",
        "attaquee": True,
        "question": "En te plaçant comme la chambre de la Cour de cassation, dis si l'arrêt attaqué doit être cassé, au moins en partie. "
                    "Réponds d'abord par oui ou par non, puis motive en dix lignes au plus. Réponds directement, de façon précise et motivée, "
                    "sans dérouler la chaîne complète de prise en main du dossier.",
    },
}



def _sources_minees() -> set[str]:
    """Numéros (chiffres seuls) des décisions citées par les motifs minés (validation/corpus_motifs) et par les fiches."""
    if _SOURCES_MINEES:
        return _SOURCES_MINEES
    for f in (BANC.parent / "corpus_motifs").glob("*.json"):
        for m in json.loads(f.read_text(encoding="utf-8")):
            for s in m.get("sources") or []:
                _SOURCES_MINEES.add(re.sub(r"\D", "", str(s.get("numero", ""))))
    for f in (PLUGIN / "skills").rglob("*.md"):
        _SOURCES_MINEES.update(re.findall(r"\d{6,}", re.sub(r"(?<=\d)[.\- ](?=\d)", "", f.read_text(encoding="utf-8"))))
    _SOURCES_MINEES.discard("")
    return _SOURCES_MINEES


_SOURCES_MINEES: set[str] = set()

PROV_OUI = re.compile(r"condamn\w*[^;]{0,500}?(?:(?:à|a) titre (?:de )?provision\w*|par provision|provisionnel\w*|(?:une|de la|la) provision|à valoir sur)", re.I)
PROV_NON = re.compile(r"(?:dis(?:ons)?|dit) n.y avoir (?:pas )?lieu à (?:référé|statuer en référé)|n.y a pas lieu à référé|(?:rejet\w*|débout\w*)[^.;]{0,200}?(?:demande\w*|prétention\w*)? ?(?:de |en )?(?:paiement )?(?:d.une |de )?provision", re.I)


def provision_au_dispositif(texte: str) -> str | None:
    """Issue de la provision lue dans le dispositif : oui (condamnation par provision), non (n'y avoir lieu, rejet), None sinon."""
    i = texte.upper().rfind("PAR CES MOTIFS")
    disp = texte[i:] if i >= 0 else texte[-4000:]
    oui, non = PROV_OUI.search(disp), PROV_NON.search(disp)
    return "oui" if oui and not non else "non" if non and not oui else None


def issue(famille: str, d: dict, motifs: str) -> str | None:
    """oui / non, ou None quand l'issue ne se lit pas sans ambiguïté."""
    sol, texte = d.get("solution"), d.get("text", "")
    if re.search(r"désistement|non-lieu|n.y a (?:plus |pas )?lieu de statuer sur (?:la|les|le) (?:requête|conclusions|pourvoi|demande)", texte[:3000] + motifs[-3000:], re.I):
        return None
    if famille in ("urgence-l521-1", "urgence-titre-renouvellement", "titre-renouvellement-delai"):
        if sol in ("GRANTED", "PARTLY_GRANTED"):
            return "oui"
        if sol == "DISMISSED" and URG_NON.search(motifs) and not URG_OUI.search(motifs):
            return "non"
        return None
    if famille == "refere-provision-civil":
        # En appel, le champ solution dit si l'appel réussit, non si la provision est allouée (relecture du 23 novembre 2026 :
        # 10 étiquettes fausses sur 40, 5 sur 40 dans un second lot) : ordonnances du tribunal seules, dont le dispositif dit la
        # même issue que le champ solution.
        if re.search(r"cour d.appel", str(d.get("title")) + texte[:1500], re.I):
            return None
        attendu = {"GRANTED": "oui", "PARTLY_GRANTED": "oui", "DISMISSED": "non"}.get(sol)
        return attendu if attendu and provision_au_dispositif(texte) == attendu else None
    if famille in ("refere-liberte", "liberte-eloignement", "annulation-ta"):
        return {"GRANTED": "oui", "PARTLY_GRANTED": "oui", "DISMISSED": "non"}.get(sol)
    if famille in ("cassation-civile", "cassation-a-chercher"):
        r = str(d.get("ruling", "")).lower()
        if "cassation" in r:
            return "oui"
        if r.startswith("rejet"):
            return "non"
    return None



COMMUNES = {
    "urgence-l521-1": "référé-suspension, condition d'urgence et doute sérieux sur la légalité de la décision",
    "refere-liberte": "référé-liberté, urgence et atteinte grave et manifestement illégale à une liberté fondamentale",
    "urgence-titre-renouvellement": "référé-suspension contre un refus de renouvellement de titre de séjour, condition d'urgence",
    "titre-renouvellement-delai": "référé-suspension contre un refus de renouvellement de titre de séjour, délai de dépôt de la demande, présomption d'urgence",
    "liberte-eloignement": "référé-liberté contre l'exécution d'une obligation de quitter le territoire français",
    "annulation-ta": "recours pour excès de pouvoir, légalité de la décision attaquée",
    "refere-provision-civil": "référé provision, obligation non sérieusement contestable",
}

def collecter(famille: str, n: int, depuis: str) -> None:
    f = FAMILLES[famille]; dossier = USINE / famille
    if not (dossier / "etat" / "affaire.json").is_file():
        subprocess.run([sys.executable, str(PLUGIN / "scripts" / "affaire.py"), "init", str(dossier), "--intitule", f"Usine {famille}",
                        "--client", "banc", "--objectif", "collecte de décisions publiques"], check=True, capture_output=True)
    # Même texte de requête pour les deux issues (seul le filtre de solution change) : deux requêtes rédigées différemment tiraient
    # des échantillons dont les indices de procédure annonçaient l'issue (banc du 22 novembre, indices.py).
    commune = COMMUNES.get(famille)
    appels = [json.dumps({**r, **({"query": commune} if commune else {}), "date_from": depuis, "limit": n // 2}, ensure_ascii=False)
              for r in f["recherches"]]
    consigne = ("Tâche mécanique de collecte, sans analyse ni écriture. 1. Lance ensemble, dans un même message, ces appels à "
                "mcp__librejustice__search_decisions, avec exactement ces arguments : " + " ; ".join(appels) +
                ". 2. Puis, dans un seul message, appelle mcp__librejustice__get_decision sur chaque résultat obtenu (toutes les url). "
                "3. Réponds seulement : fini.")
    sys.path.insert(0, str(BANC))
    from banc import config_mcp
    cmd = [shutil.which("claude"), "-p", consigne, "--plugin-dir", str(PLUGIN), "--model", "opus", "--output-format", "json",
           "--allowedTools", "mcp__librejustice__search_decisions,mcp__librejustice__get_decision", *config_mcp()]
    r = subprocess.run(cmd, cwd=dossier, capture_output=True, text=True, encoding="utf-8",
                       creationflags=getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0))
    try:
        res = json.loads(r.stdout)
        print(f"collecte {famille} : {res.get('result')!r}, {res.get('total_cost_usd', 0):.2f} $")
    except json.JSONDecodeError:
        print(r.stdout[-500:], r.stderr[-500:])
    print(len(list((dossier / "recherche" / "lectures").glob("*get_decision*.json"))), "décisions captées")


def _captures(dossier: Path) -> dict[str, dict]:
    """url -> décision captée."""
    out = {}
    for cap in (dossier / "recherche" / "lectures").glob("*get_decision*.json"):
        c = json.loads(cap.read_text(encoding="utf-8"))
        try:
            out[c["entree"]["url"]] = json.loads(c["reponse_brute"])
        except (KeyError, json.JSONDecodeError):
            continue
    return out


def attaquee(d: dict) -> str | None:
    """url de la décision attaquée : l'entrée de la chronologie, antérieure, rendue par une cour d'appel ou un tribunal."""
    for c in d.get("case_chronology") or []:
        if not c.get("current") and c.get("url") and re.search(r"cour d.appel|tribunal|conseil de prud", str(c.get("title")), re.I):
            return c["url"]
    return None


def completer(famille: str) -> None:
    """Capte la décision attaquée de chaque décision de la famille : le juge de cassation juge l'arrêt, pas seulement le moyen."""
    dossier = USINE / famille; caps = _captures(dossier)
    urls = sorted({u for d in caps.values() if (u := attaquee(d)) and u not in caps})
    if not urls:
        print("aucune décision attaquée à capter"); return
    sys.path.insert(0, str(BANC))
    from banc import config_mcp
    consigne = ("Tâche mécanique de collecte, sans analyse ni écriture. Appelle mcp__librejustice__get_decision sur chacune de ces url, "
                "toutes dans un seul message : " + " ".join(urls) + ". Réponds seulement : fini.")
    r = subprocess.run([shutil.which("claude"), "-p", consigne, "--plugin-dir", str(PLUGIN), "--model", "opus", "--output-format", "json",
                        "--allowedTools", "mcp__librejustice__get_decision", *config_mcp()], cwd=dossier, capture_output=True, text=True,
                       encoding="utf-8", creationflags=getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0))
    try:
        print(f"décisions attaquées : {len(urls)} demandées, {json.loads(r.stdout).get('total_cost_usd', 0):.2f} $")
    except json.JSONDecodeError:
        print(r.stdout[-300:], r.stderr[-300:])


def fabriquer(famille: str, maximum: int) -> None:
    f = FAMILLES[famille]; dossier = USINE / f.get("source", famille)
    caps = _captures(dossier)
    par_issue: dict[str, list] = {"oui": [], "non": []}; vus = set()
    for cap in sorted((dossier / "recherche" / "lectures").glob("*get_decision*.json")):
        try:
            d = json.loads(json.loads(cap.read_text(encoding="utf-8"))["reponse_brute"])
        except (json.JSONDecodeError, KeyError):
            continue  # capture d'une erreur du serveur
        if not isinstance(d, dict):
            continue
        num = (d.get("docket_numbers") or [""])[0]
        if not d.get("text") or num in vus or "Cour de cassation" not in str(d.get("title")) and famille.startswith("cassation"):
            continue
        cle = re.sub(r"\W", "", num)
        if any(not p.stem.startswith(f"GENP-{f['code']}-") for p in (BANC / "sondes").glob(f"GEN*-{cle}.json")):
            continue  # décision déjà sondée sous un autre code : elle ne serait plus hors échantillon
        if cle in _sources_minees():
            continue  # décision qui fonde une ligne de fiche : une sonde tirée d'elle mesurerait la mémoire du harness
        m = re.search(f["coupe"], d["text"])
        if not m:
            continue
        procedure, motifs = PHRASE_ISSUE.sub("", LIGNE_ISSUE.sub("", d["text"][:m.start()])).strip(), d["text"][m.start():]
        lu = issue(famille, d, motifs)
        if not lu or len(procedure) < 800 or FUITE.search(procedure) or LIGNE_ISSUE.search(procedure):
            continue
        if f.get("attaquee_requise") and not caps.get(attaquee(d) or ""):
            continue  # même échantillon que la famille avec arrêt joint
        if f.get("attaquee"):
            # La décision attaquée est antérieure : son dispositif n'annonce rien de l'issue du pourvoi.
            att = caps.get(attaquee(d) or "")
            if not att or not att.get("text"):
                continue
            procedure += f"\n\n## Décision attaquée : {att.get('title')}\n\n{att['text']}"
        if lu:
            vus.add(num); par_issue[lu].append((d, procedure, lu))
    k = min(len(par_issue["oui"]), len(par_issue["non"]), maximum // 2)
    ecrites = 0
    for d, procedure, lu in par_issue["oui"][:k] + par_issue["non"][:k]:
        num = re.sub(r"\W", "", (d.get("docket_numbers") or ["x"])[0])
        # GENP : la sonde demande aussi la probabilité de l'issue, notée par le score de Brier (cycle.py) ; un correctif se juge sur
        # un signal continu, bien plus puissant qu'un oui ou non à effectif égal.
        sid = f"GENP-{f['code']}-{num}"; fx = f"gen_{f['code'].lower()}_{num}"
        if famille.startswith("cassation"):
            procedure = nettoyer(procedure)  # mention de publication et phrases de l'article 1014 : décidées par la Cour
        veille = (dt.date.fromisoformat(d["date"][:10]) - dt.timedelta(days=1)).isoformat()
        (BANC / "fixtures" / fx).mkdir(parents=True, exist_ok=True)
        (BANC / "fixtures" / fx / "dossier_remis.md").write_text(
            f"# Dossier soumis à la juridiction\n\nDate du dossier : {veille}. Décision publique, noms déjà anonymisés ; "
            f"seules la procédure et les prétentions des parties sont reproduites.\n\n{procedure}\n", encoding="utf-8")
        sonde = {"id": sid, "capacite": "pronostic", "famille": famille, "genere": True,
                 "origine": f"usine.py, {d.get('title')} ({d.get('url')}), issue réelle : {lu}", "fixture": fx,
                 "consigne": "Lis dossier_remis.md. " + f["question"].replace(
                     "Réponds d'abord par oui ou par non,", "Réponds d'abord par oui ou par non, suivi de la probabilité que tu donnes à "
                     "cette issue, en pourcentage (par exemple « Non, 70 % »),"), "horloge": f"{veille}T18:00", "coupe": veille,
                 "verifications": [{"type": "message_commence", "motif": rf"\W*{lu}\b", "description": f"répond {lu}, comme la juridiction"}]}
        (BANC / "sondes" / f"{sid}.json").write_text(json.dumps(sonde, ensure_ascii=False, indent=2), encoding="utf-8")
        ecrites += 1
    print(f"{famille} : {len(par_issue['oui'])} oui et {len(par_issue['non'])} non lisibles ; {ecrites} sondes écrites, équilibrées")


CONSIGNE_MOYENS = ("Lis dossier_remis.md. Tu es avocat aux Conseils, chargé du pourvoi décrit en tête du dossier contre l'arrêt qui suit. "
                   "Propose au plus trois moyens de cassation, du plus fort au plus faible : pour chacun, le texte ou le principe invoqué, "
                   "le cas d'ouverture et le chef de l'arrêt critiqué, en cinq lignes au plus. Réponds directement, sans dérouler la chaîne "
                   "complète de prise en main du dossier.")


def _sans_liens(t: str) -> str:
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)


def fabriquer_moyens(maximum: int) -> None:
    """Famille « moyen gagnant » : l'arrêt attaqué et l'identité du demandeur, sans le moyen ni les faits rédigés par la Cour ;
    la vérité est le grief que la Cour a retenu pour casser (visa, principe, application), jugé au sens par le correcteur."""
    caps = _captures(USINE / "cassation-civile"); n = 0
    for d in caps.values():
        if n >= maximum:
            break
        if "Cour de cassation" not in str(d.get("title")) or d.get("solution") not in ("GRANTED", "PARTLY_GRANTED"):
            continue
        att = caps.get(attaquee(d) or "")
        t = d.get("text", "")
        pourvoi = re.search(r"[^\n]*a formé le pourvoi n°[^\n]*?contre l.arrêt rendu[^\n]*", _sans_liens(t))
        fin = t.find("PAR CES MOTIFS")
        reponses = [m.start() for m in re.finditer(r"\n\s*Réponse de la Cour", t) if fin < 0 or m.start() < fin]
        grief = next((t[i:fin if fin > i else i + 1800] for i in reversed(reponses) if re.search(r"Vu l", t[i:i + 600])), None)
        if not (att and att.get("text") and pourvoi and grief):
            continue
        num = re.sub(r"\W", "", (d.get("docket_numbers") or ["x"])[0])
        sid, fx = f"GENM-MOY-{num}", f"gen_moy_{num}"
        veille = (dt.date.fromisoformat(d["date"][:10]) - dt.timedelta(days=1)).isoformat()
        (BANC / "fixtures" / fx).mkdir(parents=True, exist_ok=True)
        (BANC / "fixtures" / fx / "dossier_remis.md").write_text(
            f"# Dossier du pourvoi\n\nDate du dossier : {veille}. Décision publique, noms déjà anonymisés.\n\n"
            f"{nettoyer(_sans_liens(pourvoi.group(0)).strip())}\n\n## Décision attaquée : {att.get('title')}\n\n{att['text']}\n", encoding="utf-8")
        grief_txt = re.sub(r"\s+", " ", _sans_liens(grief)).replace("Réponse de la Cour", "").strip()[:1800]
        sonde = {"id": sid, "capacite": "moyen", "famille": "moyen-gagnant", "genere": False,
                 "origine": f"usine.py, {d.get('title')} ({d.get('url')}), grief retenu par la Cour", "fixture": fx,
                 "consigne": CONSIGNE_MOYENS, "horloge": f"{veille}T18:00", "coupe": veille,
                 "verifications": [
                     {"type": "critere", "description": "trouve le grief que la Cour a retenu",
                      "critere": "Au moins un des moyens proposés correspond au grief que la Cour de cassation a retenu pour casser l'arrêt : "
                                 "même texte ou même principe, appliqué au même point de l'arrêt. Grief retenu par la Cour : « " + grief_txt + " »"},
                     {"type": "critere", "critique": False, "description": "le place en premier",
                      "critere": "Le premier moyen proposé est ce grief retenu par la Cour (même texte ou même principe, même point de l'arrêt)."}]}
        (BANC / "sondes" / f"{sid}.json").write_text(json.dumps(sonde, ensure_ascii=False, indent=2), encoding="utf-8")
        n += 1
    print(f"moyen-gagnant : {n} sondes écrites")


def collecter_direct(famille: str, depuis: str, pas_mois: int = 3) -> None:
    """Collecte sans modèle, par le client LibreJustice autorisé (validation/corpus_motifs/auth_lj.py) : la période est découpée
    en fenêtres de quelques mois, chaque fenêtre interrogée pour chaque issue avec la même requête (COMMUNES), 20 résultats au
    plus par appel ; chaque décision lue est capturée au format des lectures du harness, que `fabriquer` relit."""
    import hashlib
    import time
    sys.path.insert(0, str(BANC.parent / "corpus_motifs"))
    from lj import Client
    f = FAMILLES[famille]
    dossier = USINE / famille / "recherche" / "lectures"
    dossier.mkdir(parents=True, exist_ok=True)
    deja = set()
    for cap in dossier.glob("*get_decision*.json"):
        try:
            deja.add(json.loads(json.loads(cap.read_text(encoding="utf-8"))["entree"].replace("'", '"'))["url"])
        except Exception:  # noqa: BLE001
            pass
    c = Client()
    debut = dt.date.fromisoformat(depuis)
    fin = dt.date.today()
    n_lues = 0
    while debut < fin:
        m = debut.month - 1 + pas_mois
        borne = min(dt.date(debut.year + m // 12, m % 12 + 1, 1), fin)
        for r in f["recherches"]:
            args = {**r, **({"query": COMMUNES[famille]} if famille in COMMUNES else {}), "date_from": debut.isoformat(),
                    "date_to": (borne - dt.timedelta(days=1)).isoformat(), "limit": 20}
            try:
                hits = (c.appel("search_decisions", args) or {}).get("hits", [])
            except Exception as e:  # noqa: BLE001
                print(f"  recherche en échec ({e}) : {debut}")
                continue
            for h in hits:
                url = h.get("url")
                if not url or url in deja:
                    continue
                try:
                    brut = c.appel("get_decision", {"url": url})
                except Exception as e:  # noqa: BLE001
                    print(f"  lecture en échec ({e}) : {url}")
                    continue
                texte = json.dumps(brut, ensure_ascii=False)
                empreinte = hashlib.sha256(texte.encode("utf-8")).hexdigest()
                n_lues += 1
                (dossier / f"{dt.datetime.now():%Y%m%dT%H%M%S}_{n_lues:05d}_get_decision_{empreinte[:8]}.json").write_text(json.dumps({
                    "schema": "lecture/1", "outil": "mcp__librejustice__get_decision", "entree": {"url": url},
                    "horodatage": dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z"), "horloge_fixee": "None",
                    "session_id": "collecte-directe", "agent": "", "tool_use_id": "", "sha256_reponse": empreinte,
                    "reponse_brute": texte}, ensure_ascii=False), encoding="utf-8")
                deja.add(url)
                time.sleep(0.2)
        debut = borne
    print(f"collecte directe {famille} : {n_lues} décisions nouvelles ; {len(deja)} au total")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    c = s.add_parser("collecter"); c.add_argument("famille", choices=FAMILLES); c.add_argument("--n", type=int, default=16)
    c.add_argument("--depuis", default="2025-01-01")
    c.add_argument("--direct", action="store_true", help="sans modèle, par le client LibreJustice autorisé (auth_lj.py)")
    fb = s.add_parser("fabriquer"); fb.add_argument("famille", choices=FAMILLES); fb.add_argument("--max", type=int, default=12)
    s.add_parser("familles")
    s.add_parser("completer").add_argument("famille", choices=FAMILLES)
    s.add_parser("moyens").add_argument("--max", type=int, default=10)
    a = p.parse_args()
    if a.cmd == "collecter":
        collecter_direct(a.famille, a.depuis) if a.direct else collecter(a.famille, a.n, a.depuis)
    elif a.cmd == "completer":
        completer(a.famille)
    elif a.cmd == "moyens":
        fabriquer_moyens(a.max)
    elif a.cmd == "fabriquer":
        fabriquer(a.famille, a.max)
    else:
        print("\n".join(f"{k} ({v['code']})" for k, v in FAMILLES.items()))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
