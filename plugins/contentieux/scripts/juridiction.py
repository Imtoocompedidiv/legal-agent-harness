"""Profil et calibrage d'une juridiction à partir de ses décisions publiées.

Usage :
  python juridiction.py profil --code TA69 --requete 'redoublement ET "522-3"' [--requete ...] [--depuis 2025-01-01] [--jusqu-au AAAA-MM-JJ] [--exclure N°] [--max 120]
  python juridiction.py calibrage --code TA30 --requete 'précontractuel ET "L. 551-1"' --avant AAAA-MM-JJ [--exclure N°] [--par-cote 4]
  python juridiction.py calibrage --decisions procedure/calibrage_decisions.json --avant AAAA-MM-JJ [--exclure N°] [--par-cote 4]
  python juridiction.py conditions --type refere_suspension

Écrit dans le dossier d'affaire courant :
  procedure/profil_<code>.md            issues, motifs de tri, exemples (aucun nom ni taux de magistrat : CJA, art. L. 10)
  procedure/calibrage_<code>.md         calibrage équilibré du juge simulé : taux observés, refus et accueils au filtre et après
                                        instruction, en nombre égal, tous antérieurs à la borne, la décision de l'affaire exclue
  procedure/exemples_tri_<code>.md      motifs littéraux des seules ordonnances de tri (ancien calibrage, conservé pour mémoire)
  procedure/exemples_fond_<code>.md     jugements au fond, annulations et rejets ensemble
  procedure/conditions_<type>.md        conditions du régime, sanction de chacune, textes et pièges, pour le rapporteur simulé
  recherche/opendata/<identifiant>.json textes acquis (cache)

Deux sources pour le calibrage : la base ouverte de la justice administrative (--code et --requete), ou un fichier de
décisions relevées sur LibreJustice pour les autres juridictions (--decisions), au format décrit par `lire_releve`.
La borne --avant est stricte : la décision de l'affaire, toujours postérieure au dépôt, ne peut pas y figurer.

Requêtes génériques seulement : le script refuse toute requête qui contient un identifiant privé déclaré dans
etat/affaire.json. Les nombres décrivent ce que la juridiction a publié ; ils ne disent pas la chance d'un dossier.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib_affaire as L  # noqa: E402

BASE = "https://opendata.justice-administrative.fr/recherche/api"
STADES = ("filtrage", "instruction")
ISSUES = ("accueil", "refus")


def get_json(url: str, essais: int = 3):
    for i in range(essais):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "cabinet-contentieux/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:  # noqa: BLE001
            if i == essais - 1:
                raise
            time.sleep(2 * (i + 1))


def rechercher(requete: str, maxi: int = 9999) -> list[dict]:
    url = f"{BASE}/Simple_Search/openData/{urllib.parse.quote(requete)}/{maxi}"
    d = get_json(url)
    return [h["_source"] for h in d["decisions"]["body"]["hits"]["hits"]]


def texte(code: str, ident: str, cache: Path) -> str:
    cible = cache / f"{ident}.json"
    if cible.is_file():
        return json.loads(cible.read_text(encoding="utf-8"))["texte"]
    d = get_json(f"{BASE}/elastic/decisions/{code}/{ident.replace('.xml', '')}")
    hits = d["decisions"]["body"]["hits"]["hits"]
    src = next((h["_source"] for h in hits if h["_source"].get("Identification") == ident), hits[0]["_source"] if hits else {})
    t = (src.get("paragraph") or "").replace("$$$", "\n")
    cache.mkdir(parents=True, exist_ok=True)
    cible.write_text(json.dumps({"identification": ident, "code": code, "texte": t}, ensure_ascii=False), encoding="utf-8")
    return t


def classer(t: str) -> dict:
    bas = t.lower()
    tri = "522-3" in t and ("sans instruction" in bas or "application de l'article l. 522-3" in bas or "en application de l'article l.522-3" in bas)
    if re.search(r"(est|sont) suspendue?s?", bas) or "est suspendue" in bas:
        issue = "suspension"
    elif "non-lieu" in bas or "n'y a pas lieu de statuer" in bas:
        issue = "non_lieu"
    elif "désistement" in bas:
        issue = "desistement"
    elif tri and "rejet" in bas:
        issue = "tri"
    elif "est rejetée" in bas or "sont rejetées" in bas:
        issue = "rejet_apres_audience" if "audience" in bas else "rejet"
    elif "enjoint" in bas:
        issue = "injonction"
    else:
        issue = "autre"
    # Les motifs se lisent dans les considérants du juge (après « Considérant ce qui suit », avant le dispositif),
    # hors citation des articles et hors résumé des moyens du requérant.
    i = bas.find("considérant ce qui suit")
    j = max(t.find("O R D O N N E"), t.find("ORDONNE"), t.find("D E C I D E"))
    partie = t[i:j] if 0 <= i < j else (t[i:] if i >= 0 else t)
    propres = [p.strip() for p in partie.split("\n")
               if re.match(r"^\s*\d+\.", p) and not re.search(r"aux termes|en vertu de l.article l\. ?522-3|dispose que|«|\"", p.lower())]
    considerants = " ".join(p.lower() for p in propres)
    motifs = []
    if re.search(r"urgence[^.]{0,160}(n.est pas (remplie|satisfaite|caractérisée|établie)|ne (peut|saurait) être regardée|fait défaut)|ne justifie pas (d'une|de l')urgence|défaut d.urgence|absence d.urgence", considerants):
        motifs.append("urgence")
    if re.search(r"doute sérieux", considerants):
        motifs.append("doute_serieux")
    if re.search(r"irrecevab|r\. ?522-1|requête distincte", considerants):
        motifs.append("irrecevabilite")
    decisifs = [p for p in propres if re.search(r"doute sérieux|urgence|irrecevab|522-3|rejet|annul|erreur|examen|illégal|méconn", p.lower())]
    motif_txt = " ".join(decisifs[-2:]) if decisifs else (" ".join(propres[-2:]) if propres else "")
    return {"issue": issue, "motifs": motifs, "motif_texte": motif_txt[:1400]}


def classer_fond(t: str) -> dict:
    """Jugement au fond : l'issue se lit dans le dispositif, les motifs dans les derniers paragraphes numérotés avant lui."""
    k = max(t.find("D E C I D E"), t.find("DÉCIDE"), t.find("DECIDE"))
    dispositif = t[k:] if k >= 0 else t[-1500:]
    d = dispositif.lower()
    if re.search(r"(est|sont) annulée?s?|annulation de la décision", d):
        issue = "annulation"
    elif "enjoint" in d:
        issue = "injonction"
    elif "rejet" in d:
        issue = "rejet"
    else:
        issue = "autre"
    corps = t[:k] if k >= 0 else t
    paras = [p.strip() for p in re.split(r"(?:\$\$\$|\n)+|\s(?=\d{1,2}\.\s+[A-ZÀ-Ý])", corps) if re.match(r"^\d{1,2}\.\s", p.strip())]
    paras = [p for p in paras if not re.search(r"l\. ?761-1|aux termes|dispose que|frais (liés|exposés)", p.lower())]
    return {"issue": issue, "motif_texte": " ".join(paras[-3:])[:1600]}


# ---------------------------------------------------------------------------
# Calibrage équilibré : ce que la juridiction refuse et ce qu'elle accueille, au filtre et après instruction.

MARQUE_DISPOSITIF = re.compile(r"\bO ?R ?D ?O ?N ?N ?E\b|\bD ?[EÉ] ?C ?I ?D ?E\b|\bA ?R ?R ?[EÊ] ?T ?E\b")
ACCUEIL = re.compile(r"(est|sont) suspendue?s?|(est|sont) annulée?s?|annul[ée]+ en tant que|enjoint|(est|sont) condamnée?s? à (payer|verser)|"
                     r"(est|sont) déchargée?s?|décharge (de|des)|(est|sont) réformée?s?|il est ordonné|est ordonnée?|(est|sont) désignée?s? en qualité d.expert|"
                     r"cass(e|é) et annul|(est|sont) cassée?s?|est relevée? de la forclusion|(est|sont) renvoyée?s? (au|à la) conseil constitutionnel")


def articles_dispositif(t: str) -> list[str]:
    """Articles du dispositif, sans ceux qui ne portent que sur les frais, la notification ou les copies."""
    debut = t.lower().find("considérant ce qui suit")
    marques = [m for m in MARQUE_DISPOSITIF.finditer(t) if m.start() > debut]
    if not marques:
        return []
    disp = t[marques[0].end():]
    morceaux = [m.strip() for m in re.split(r"\bArticle\s+(?:\d+|1er)\s*:?", disp) if m.strip()]
    return [m for m in morceaux if not re.search(r"761-1|article 700|frais (liés|exposés|irrépétibles)|sera notifié|copie en sera adressée|dépens", m.lower())]


def classer_decision(t: str) -> dict:
    """Stade (filtrage ou instruction) et issue (accueil, refus, autre) d'une décision administrative publiée.

    L'issue se lit dans les articles du dispositif autres que ceux des frais : un seul article qui suspend, annule,
    enjoint, condamne, décharge, réforme ou ordonne fait un accueil, même si le surplus est rejeté. Le stade est le
    filtrage pour une ordonnance de tri (CJA, L. 522-3) ou de rejet sans instruction (CJA, R. 222-1)."""
    bas = t.lower()
    arts = articles_dispositif(t)
    corps = " ".join(arts).lower()
    if arts and any(ACCUEIL.search(a.lower()) and "amende" not in a.lower() for a in arts):
        issue = "accueil"
    elif arts and re.search(r"rejet|irrecevable|n.est pas admis|non-admission", corps):
        issue = "refus"
    else:
        issue = "autre"
    filtre = issue == "refus" and (
        ("522-3" in t and re.search(r"sans instruction|application de l.article l\. ?522-3|en application de l.article l\.522-3", bas))
        or re.search(r"r\. ?222-1", bas) is not None)
    if issue == "autre" and re.search(r"non-lieu|n.y a pas lieu de statuer|désistement", corps or bas):
        issue = "autre"
    refere = "juge des référés" in bas or re.search(r"l\. ?521-[1-4]|l\. ?551-1|l\. ?541-1", bas) is not None
    motif = (classer(t) if refere else classer_fond(t))["motif_texte"]
    return {"stade": "filtrage" if filtre else "instruction", "issue": issue, "refere": bool(refere), "motif": motif}


def date_iso(x) -> str:
    return str(x or "")[:10]


# Aucune identité de magistrat ni de membre du greffe dans un calibrage (CJA, art. L. 10, al. 4 ; COJ, art. L. 111-13 ;
# sanction de l'article 226-18 du code pénal) : les extraits cités sont purgés des noms de personnes, et rien ne se
# compte par juge. Les parties pseudonymisées par la juridiction (« M. B... ») ne sont pas touchées.
ROLE_NOMME = re.compile(r"\b(Président(?:e)?|Rapporteur(?:e)?(?: public(?:que)?)?|Greffi(?:er|ère)|Avocat(?:e)? général(?:e)?|"
                        r"Conseill(?:er|ère)(?: rapporteu(?:r|se))?|Magistrat(?:e)?(?: désigné(?:e)?)?|Juge(?: des référés)?|Premi(?:er|ère) président(?:e)?)"
                        r"\s*:\s*(?:(?:M\.|Mme|Mlle|Monsieur|Madame)\s+)?[A-ZÀ-Ý][\w'’\-]+(?:\s+[A-ZÀ-Ý][\w'’\-]+){0,3}")
TITRE_NOM = re.compile(r"\b(?:M\.|Mme|Mlle|MM\.|Mmes|Monsieur|Madame)\s+[A-ZÀ-Ý][\w'’\-]+(?:\s+[A-ZÀ-Ý][\w'’\-]+){0,3}")


def retirer_noms(texte: str) -> str:
    t = ROLE_NOMME.sub(lambda m: m.group(1) + " : [nom retiré]", str(texte or ""))
    return TITRE_NOM.sub("[nom retiré]", t)


def cite_procedure(texte: str, article: str) -> bool:
    """La décision vise-t-elle l'article de procédure qui définit la classe de référence (par exemple « L. 521-1 ») ?"""
    m = re.match(r"^\s*([LRD])\.?\s*(\d[\d\-]*)\s*$", article or "", re.I)
    if not m:
        return article.lower() in (texte or "").lower()
    return re.search(rf"\b{m.group(1)}\.?\s?{re.escape(m.group(2))}(?![\d\-])", texte or "", re.I) is not None


def borner(decisions: list[dict], avant: str, exclure: list[str] = ()) -> tuple[list[dict], dict]:
    """Ne garde que les décisions strictement antérieures à `avant` (AAAA-MM-JJ) et étrangères aux numéros exclus.

    Une décision sans date lisible est écartée : on ne peut pas prouver qu'elle précède le dépôt."""
    gardees, ecart = [], collections.Counter()
    vus = set()
    for d in decisions:
        j = date_iso(d.get("date"))
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", j):
            ecart["sans_date"] += 1
            continue
        if j >= avant:
            ecart["posterieure_ou_egale_a_la_borne"] += 1
            continue
        num = str(d.get("numero") or "")
        if any(x and re.sub(r"\W", "", x) and re.sub(r"\W", "", x) in re.sub(r"\W", "", num + " " + str(d.get("url") or "")) for x in exclure):
            ecart["exclue_decision_de_l_affaire"] += 1
            continue
        cle = (num, d.get("url"), j)
        if cle in vus:
            ecart["doublon"] += 1
            continue
        vus.add(cle)
        gardees.append(d)
    gardees.sort(key=lambda d: date_iso(d.get("date")), reverse=True)
    return gardees, dict(ecart)


def taux(decisions: list[dict]) -> dict:
    """Taux observés sur l'échantillon publié : part triée au filtre, part accueillie après instruction, part accueillie en tout."""
    f_refus = sum(1 for d in decisions if d.get("stade") == "filtrage" and d.get("issue") == "refus")
    instr = [d for d in decisions if d.get("stade") == "instruction" and d.get("issue") in ISSUES]
    acc = sum(1 for d in instr if d["issue"] == "accueil")
    total = f_refus + len(instr)
    return {
        "decisions_classees": total,
        "refus_au_filtre": f_refus,
        "instruites": len(instr),
        "accueillies_apres_instruction": acc,
        "part_filtree": round(f_refus / total, 2) if total else None,
        "part_accueillie_apres_instruction": round(acc / len(instr), 2) if instr else None,
        "part_accueillie_en_tout": round(acc / total, 2) if total else None,
    }


def equilibrer(decisions: list[dict], par_cote: int = 4) -> dict:
    """Autant de refus que d'accueils après instruction (les plus récents de chaque côté), et autant de refus au filtre
    que d'affaires qui l'ont franchi. Le déséquilibre de la juridiction se lit dans les taux, pas dans le choix des exemples."""
    instr = [d for d in decisions if d.get("stade") == "instruction"]
    refus_i = [d for d in instr if d.get("issue") == "refus"]
    acc_i = [d for d in instr if d.get("issue") == "accueil"]
    filtre = [d for d in decisions if d.get("stade") == "filtrage" and d.get("issue") == "refus"]
    k = min(par_cote, len(refus_i), len(acc_i)) if refus_i and acc_i else min(par_cote, max(len(refus_i), len(acc_i)))
    kf = min(par_cote, len(filtre), len(instr)) if instr else min(par_cote, len(filtre))
    return {"refus_au_filtre": filtre[:kf], "refus_apres_instruction": refus_i[:k], "accueils_apres_instruction": acc_i[:k]}


def rendre_calibrage(titre: str, perimetre: str, avant: str, decisions: list[dict], ecarts: dict,
                     decomptes_publies: list[dict] | None = None, par_cote: int = 4) -> str:
    tx = taux(decisions)
    ex = equilibrer(decisions, par_cote)
    pct = lambda x: "non mesurable" if x is None else f"{round(100 * x)} %"  # noqa: E731
    out = [f"# Calibrage : {retirer_noms(titre)}", "",
           f"Périmètre : {retirer_noms(perimetre)}. Décisions publiées antérieures au {avant} (borne stricte : la décision de l'affaire n'y figure pas). "
           "Elles ne concernent pas l'affaire. Elles montrent ce que cette juridiction refuse et ce qu'elle accueille, en nombre égal ; "
           "la fréquence réelle de chaque issue se lit dans les taux, jamais dans le nombre d'exemples. Aucun nom de magistrat ni de "
           "greffier, aucun décompte par juge (CJA, art. L. 10 ; COJ, art. L. 111-13).", "",
           "## Taux observés sur l'échantillon publié", "",
           f"- Décisions classées : {tx['decisions_classees']} ; refusées au filtre : {tx['refus_au_filtre']} ({pct(tx['part_filtree'])}) ; "
           f"instruites : {tx['instruites']}, dont accueillies : {tx['accueillies_apres_instruction']} ({pct(tx['part_accueillie_apres_instruction'])}) ; "
           f"accueillies en tout : {pct(tx['part_accueillie_en_tout'])}.",
           "- La publication n'est ni exhaustive ni aléatoire : ces taux décrivent la pratique publiée, pas la chance d'un dossier."]
    if ecarts:
        out.append("- Écartées avant classement : " + ", ".join(f"{k} {v}" for k, v in sorted(ecarts.items())) + ".")
    for dc in decomptes_publies or []:
        cpt = ", ".join(f"{k} {v}" for k, v in (dc.get("decompte_par_solution") or {}).items())
        out.append(f"- Décompte de la base pour la requête « {dc.get('query', '')} »"
                   f"{(' (' + ', '.join(f'{k}={v}' for k, v in (dc.get('filtres') or {}).items()) + ')') if dc.get('filtres') else ''} : {cpt or 'non relevé'}.")
    sections = [("Refus au filtre (tri, rejet sans instruction, non-admission)", "refus_au_filtre"),
                ("Refus après instruction", "refus_apres_instruction"),
                ("Accueils après instruction", "accueils_apres_instruction")]
    for titre_s, cle in sections:
        out += ["", f"## {titre_s} : {len(ex[cle])}", ""]
        if not ex[cle]:
            out.append("Aucune décision publiée de cette sorte dans le périmètre et avant la borne.")
        for d in ex[cle]:
            out += [f"### {date_iso(d.get('date'))}, {retirer_noms(d.get('juridiction') or '')} n° {d.get('numero') or ''}".rstrip(), "",
                    retirer_noms(d.get("motif") or "(motif non repéré)").strip()[:1400], ""]
    return "\n".join(out).rstrip() + "\n"


def lire_releve(chemin: Path) -> dict:
    """Relevé de décisions établi sur LibreJustice par un agent qui ne voit pas l'affaire au-delà de son objet.

    {"juridiction": str, "perimetre": str,
     "requetes": [{"query": str, "filtres": {...}, "decompte_par_solution": {"GRANTED": n, "DISMISSED": n, ...}}],
     "decisions": [{"date": "AAAA-MM-JJ", "juridiction": str, "numero": str, "url": str,
                    "stade": "filtrage" | "instruction", "issue": "accueil" | "refus", "motif": "paragraphe décisif recopié"}]}"""
    d = json.loads(chemin.read_text(encoding="utf-8"))
    decs = []
    for x in d.get("decisions", []):
        if x.get("stade") not in STADES or x.get("issue") not in ISSUES + ("autre",):
            raise SystemExit(f"Relevé invalide : stade ou issue inconnus pour {x.get('numero')} ({x.get('stade')}, {x.get('issue')}).")
        decs.append(x)
    return {**d, "decisions": decs}


def refuser_prives(racine: Path, requetes: list[str]) -> None:
    prives = [str(x).lower() for x in ((L.lire_json(racine / "etat/affaire.json", {}) or {}).get("consignes") or {}).get("identifiants_prives", []) if len(str(x)) >= 4]
    for q in requetes:
        if any(p in q.lower() for p in prives):
            raise SystemExit(f"Requête refusée : elle contient un identifiant privé du client ({q}).")


def decisions_opendata(code: str, requetes: list[str], cache: Path, maxi: int = 60, avant: str = "", exclure: list[str] = (),
                       procedure: str = "") -> list[dict]:
    vus, sources = set(), []
    for q in requetes:
        for s in rechercher(q):
            if s.get("Code_Juridiction") != code or s["Identification"] in vus:
                continue
            vus.add(s["Identification"])
            sources.append(s)
    brutes = [{"date": s.get("Date_Lecture"), "juridiction": s.get("Nom_Juridiction") or code, "numero": s.get("Numero_Dossier"),
               "url": s.get("Identification"), "_ident": s["Identification"]} for s in sources]
    # Borner avant de télécharger : rien de postérieur au dépôt n'est même lu.
    bornees, _ = borner(brutes, avant or date.today().isoformat(), list(exclure))
    out = []
    for b in bornees[:maxi]:
        try:
            t = texte(code, b["_ident"], cache)
        except Exception:  # noqa: BLE001
            continue
        if procedure and not cite_procedure(t, procedure):
            continue  # hors de la classe de référence (autre procédure)
        c = classer_decision(t)
        if c["issue"] in ISSUES:
            out.append({**{k: v for k, v in b.items() if not k.startswith("_")}, **c})
    return out


def cmd_calibrage(a):
    racine = L.trouver_racine(Path.cwd())
    if racine is None:
        raise SystemExit("À lancer depuis un dossier d'affaire.")
    avant = a.avant or date.today().isoformat()
    if a.decisions:
        rel = lire_releve(Path(a.decisions))
        decs, ecarts = borner(rel["decisions"], avant, a.exclure)
        code = a.code or re.sub(r"\W+", "_", rel.get("juridiction", "juridiction")).strip("_")[:40]
        titre, perimetre, decomptes = rel.get("juridiction", code), rel.get("perimetre", ""), rel.get("requetes")
    else:
        if not (a.code and a.requete):
            raise SystemExit("Indiquer --decisions, ou --code et --requete pour la base ouverte de la justice administrative.")
        refuser_prives(racine, a.requete)
        brutes = decisions_opendata(a.code, a.requete, racine / "recherche/opendata", a.max, avant, a.exclure, a.procedure)
        decs, ecarts = borner(brutes, avant, a.exclure)
        code, titre, decomptes = a.code, a.code, None
        perimetre = "requêtes " + ", ".join(repr(q) for q in a.requete) + (f" ; classe : décisions qui visent l'article {a.procedure}" if a.procedure else "")
    md = rendre_calibrage(titre, perimetre, avant, decs, ecarts, decomptes, a.par_cote)
    (racine / "procedure").mkdir(exist_ok=True)
    cible = racine / f"procedure/calibrage_{code}.md"
    cible.write_text(md, encoding="utf-8")
    L.ajouter_journal(racine, f"Calibrage {code} : {len(decs)} décisions antérieures au {avant} ({cible.relative_to(racine).as_posix()}).", "note")
    print(md)


def rendre_conditions(type_acte: str, regime: dict, categories: dict) -> str:
    out = [f"# Conditions du régime `{type_acte}`", "",
           f"Textes de référence du régime : {regime.get('texte') or 'non indiqués'}. Juge : {regime.get('juge')}"
           f"{' ; référé' if regime.get('refere') else ''}.", "",
           "Chaque condition est examinée à part : texte lu à la date des faits, standard de contrôle, charge de la preuve, "
           "faits et pièces, appréciation. La sanction indiquée est celle que le défaut de la condition entraîne.", "",
           "| Condition | Sanction de son défaut |", "| --- | --- |"]
    out += [f"| {c} | {categories.get(c, 'mal_fonde')} |" for c in regime.get("conditions", [])]
    if regime.get("pieges"):
        out += ["", "## Pièges connus du régime", ""] + [f"- {p}" for p in regime["pieges"]]
    return "\n".join(out) + "\n"


def cmd_conditions(a):
    import gate  # noqa: PLC0415  (lecture seule des régimes)
    gate.charger_regimes_domaines()
    if a.type not in gate.REGIMES:
        raise SystemExit(f"Type d'acte inconnu : {a.type}. Liste : python gate.py --regimes")
    md = rendre_conditions(a.type, gate.REGIMES[a.type], gate.categories_conditions())
    racine = L.trouver_racine(Path.cwd())
    if racine is not None:
        (racine / "procedure").mkdir(exist_ok=True)
        (racine / f"procedure/conditions_{a.type}.md").write_text(md, encoding="utf-8")
    print(md)


def cmd_profil(a):
    racine = L.trouver_racine(Path.cwd())
    if racine is None:
        raise SystemExit("À lancer depuis un dossier d'affaire.")
    refuser_prives(racine, a.requete)
    vus, retenues = set(), []
    for q in a.requete:
        for s in rechercher(q):
            if s.get("Code_Juridiction") != a.code or s.get("Date_Lecture", "") < a.depuis:
                continue
            # Rejeu d'un dossier à une date passée : rien de postérieur, et jamais la décision de l'affaire elle-même.
            if a.jusqu_au and s.get("Date_Lecture", "") > a.jusqu_au:
                continue
            if any(x and x in (s.get("Numero_Dossier") or "") for x in a.exclure):
                continue
            if s["Identification"] in vus:
                continue
            vus.add(s["Identification"])
            retenues.append(s)
    retenues.sort(key=lambda s: s.get("Date_Lecture", ""), reverse=True)
    retenues = retenues[: a.max]
    cache = racine / "recherche/opendata"
    lignes = []
    for s in retenues:
        try:
            t = texte(a.code, s["Identification"], cache)
        except Exception as e:  # noqa: BLE001
            lignes.append({**s, "issue": "inaccessible", "motifs": [], "motif_texte": str(e)[:200]})
            continue
        refere = "juge des référés" in t.lower() or "l. 521-" in t.lower()
        lignes.append({**s, **(classer(t) if refere else {**classer(t), **classer_fond(t)}), "refere": refere,
                       "_calibrage": classer_decision(t)})
    refs = [l for l in lignes if l.get("refere")]
    issues = collections.Counter(l["issue"] for l in refs)
    motifs = collections.Counter(m for l in refs if l["issue"] == "tri" for m in l["motifs"])
    # Aucun décompte par magistrat : la réutilisation de son identité pour analyser ou prédire ses pratiques est un délit
    # (CJA, art. L. 10, al. 4 ; COJ, art. L. 111-13 ; C. pén., art. 226-18).
    out = [f"# Profil de {a.code} sur les requêtes {', '.join(repr(q) for q in a.requete)}",
           "", f"Décisions publiées lues depuis le {a.depuis} : {len(lignes)}, dont {len(refs)} en référé. Classement automatique par motifs du texte, à contrôler sur les exemples avant usage. Base ouverte incomplète et diffusée avec retard ; ces nombres décrivent la pratique publiée, pas la chance d'un dossier.",
           "", "## Issues des référés", ""]
    out += [f"- {k} : {v}" for k, v in issues.most_common()]
    out += ["", "## Motifs des ordonnances de tri", ""] + [f"- {k} : {v}" for k, v in motifs.most_common()]
    out += ["", "## Décisions", "", "| Date | N° | Issue | Motifs |", "| --- | --- | --- | --- |"]
    for l in refs:
        out.append(f"| {l.get('Date_Lecture')} | {l.get('Numero_Dossier')} | {l['issue']} | {', '.join(l['motifs'])} |")
    (racine / "procedure").mkdir(exist_ok=True)
    (racine / f"procedure/profil_{a.code}.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    ex = [f"# Comment {a.code} trie : motifs littéraux d'ordonnances de tri publiées", "",
          "Refus seulement : ce fichier ne suffit pas à calibrer le juge simulé. Lui donner `calibrage_<code>.md`, qui montre aussi ce que la juridiction instruit et accorde.", ""]
    for l in [l for l in refs if l["issue"] == "tri"][:25]:
        ex += [f"## {l.get('Date_Lecture')}, n° {l.get('Numero_Dossier')} ({', '.join(l['motifs']) or 'motif non classé'})", "", retirer_noms(l["motif_texte"]) or "(paragraphe non repéré)", ""]
    (racine / f"procedure/exemples_tri_{a.code}.md").write_text("\n".join(ex) + "\n", encoding="utf-8")
    # Calibrage du juge du fond : jugements publiés, annulations et rejets ensemble, pour ne pas biaiser le seuil.
    fond = [l for l in lignes if not l.get("refere") and l.get("issue") not in ("inaccessible", "desistement", "non_lieu", "autre")]
    ann = lambda l: l.get("issue") in ("annulation", "injonction")  # noqa: E731
    ef = [f"# Comment {a.code} juge au fond : jugements publiés sur les mêmes requêtes", "",
          f"Pour le juge simulé d'une instance au fond : {len(fond)} jugements, dont {sum(1 for l in fond if ann(l))} qui annulent ou enjoignent. "
          "Ils fixent le seuil et le style réels de cette juridiction. Ils ne concernent pas l'affaire.", ""]
    for l in fond[:25]:
        ef += [f"## {l.get('Date_Lecture')}, n° {l.get('Numero_Dossier')} ({'annulation ou injonction' if ann(l) else l['issue']})", "",
               retirer_noms(l["motif_texte"]) or "(paragraphe non repéré)", ""]
    (racine / f"procedure/exemples_fond_{a.code}.md").write_text("\n".join(ef) + "\n", encoding="utf-8")
    # Calibrage équilibré sur les mêmes décisions : refus et accueils, au filtre et après instruction.
    borne = (date.fromisoformat(a.jusqu_au).toordinal() + 1) if a.jusqu_au else date.today().toordinal() + 1
    avant = date.fromordinal(borne).isoformat()
    cal = [{"date": l.get("Date_Lecture"), "juridiction": l.get("Nom_Juridiction") or a.code, "numero": l.get("Numero_Dossier"),
            "url": l.get("Identification"), **l["_calibrage"]} for l in lignes if l.get("_calibrage") and l["_calibrage"]["issue"] in ISSUES]
    cal, ecarts = borner(cal, avant, a.exclure)
    (racine / f"procedure/calibrage_{a.code}.md").write_text(
        rendre_calibrage(a.code, "requêtes " + ", ".join(repr(q) for q in a.requete), avant, cal, ecarts), encoding="utf-8")
    L.ajouter_journal(racine, f"Profil {a.code} établi sur {len(refs)} référés et {len(fond)} jugements au fond publiés depuis le {a.depuis} (procedure/).", "note")
    print("\n".join(out[:25]))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    pr = s.add_parser("profil")
    pr.add_argument("--code", required=True, help="Code_Juridiction, par exemple TA69 (Lyon), CAA69, CE")
    pr.add_argument("--requete", action="append", required=True, help="forme mot ET \"expression\"")
    pr.add_argument("--depuis", default="2025-01-01")
    pr.add_argument("--max", type=int, default=120)
    pr.add_argument("--jusqu-au", dest="jusqu_au", default="", help="date AAAA-MM-JJ : ignore les décisions postérieures (rejeu à une date passée)")
    pr.add_argument("--exclure", action="append", default=[], help="numéro de dossier à écarter (la décision de l'affaire elle-même)")
    pr.set_defaults(f=cmd_profil)
    ca = s.add_parser("calibrage", help="calibrage équilibré du juge simulé (refus et accueils, au filtre et après instruction)")
    ca.add_argument("--code", default="", help="Code_Juridiction de la base ouverte administrative, ou nom court du fichier écrit")
    ca.add_argument("--requete", action="append", default=[], help="requête de la base ouverte, forme mot ET \"expression\"")
    ca.add_argument("--decisions", default="", help="relevé JSON de décisions (LibreJustice), voir lire_releve")
    ca.add_argument("--avant", default="", help="borne stricte AAAA-MM-JJ, en principe le jour du dépôt de l'acte")
    ca.add_argument("--exclure", action="append", default=[], help="numéro de la décision de l'affaire, à écarter en tout cas")
    ca.add_argument("--par-cote", dest="par_cote", type=int, default=4)
    ca.add_argument("--max", type=int, default=60, help="décisions téléchargées au plus (base ouverte)")
    ca.add_argument("--procedure", default="", help="article qui définit la classe de référence, par exemple L. 521-1 (base ouverte)")
    ca.set_defaults(f=cmd_calibrage)
    co = s.add_parser("conditions", help="conditions d'un régime, pour le rapporteur simulé")
    co.add_argument("--type", required=True)
    co.set_defaults(f=cmd_conditions)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
