"""Registre mécanique des lectures de la recherche juridique, et contrôles qui s'en servent.

Le hook PostToolUse capture chaque appel aux outils LibreJustice (mcp__librejustice__*) et à la lecture de document du
serveur legal_harness : outil, entrée, horodatage du dossier (qui suit CONTENTIEUX_MAINTENANT) et réponse brute. Les
captures sont rangées dans recherche/lectures/ ; l'empreinte de chacune s'inscrit, au moment de la capture, dans
recherche/lectures/registre.jsonl. Une capture modifiée, ajoutée ou supprimée à la main est écartée et signalée. Le
registre dit ce qui a réellement été lu ; les commandes confrontent une écriture ou une note à ce registre.

Commandes, lancées depuis le dossier d'affaire :
  couverture <écriture|note> [--date AAAA-MM-JJ] [--json]
      pour chaque article cité : texte lu à la date utile, section lue, renvois suivis, décisions citant l'article
      cherchées par le filtre legal_article ; pour chaque décision citée : lue en entier, suite vérifiée, conclusions
      et rapports signalés par la source
  citations <écriture|note> [--json]
      chaque passage entre guillemets attribué à un texte, une décision ou une pièce se retrouve mot pour mot dans une
      lecture capturée ou une extraction de pièce ; sinon citation introuvable, avec le passage le plus proche
  portee [<écriture|note>] [--json]
      décisions lues, ou citées, dont la suite connue (standing, case_chronology) montre une annulation, une
      cassation ou une infirmation ; pour une écriture, si elle le dit
  requetes [--vides]
      recherches faites (outil, requête, filtres, nombre de résultats) ; --vides : celles qui n'ont rien rendu
  fiche <référence> [--date AAAA-MM-JJ]
      squelette de fiche de lecture prérempli depuis les captures (sortie standard, rien n'est écrit) ; la
      référence est « code|article » (code-civil|1240), une adresse LibreJustice ou un numéro de décision
  verifier [<id>]...
      valide les fiches recherche/fiches/<id>.json : schéma, captures citées, extraits retrouvés mot pour mot
  capturer
      lit un événement PostToolUse sur l'entrée standard et le capture (usage par hook)

La date utile d'un article se déclare dans la fiche de l'acte (dates_utiles par article, date_droit_applicable), par une
ligne « Date utile : AAAA-MM-JJ » de la note, ou par --date. À défaut, la date des actes attaqués et le jour du contrôle
sont admis, avec une alerte quand le texte a connu plusieurs versions.

Bibliothèque standard seulement. Aucun appel réseau : les contrôles ne lisent que les captures et les extractions.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
import lib_affaire as L  # noqa: E402

DOSSIER = Path("recherche") / "lectures"
REGISTRE = DOSSIER / "registre.jsonl"
FICHES = Path("recherche") / "fiches"
SCHEMA_CAPTURE = "lecture/1"
SCHEMA_FICHE = "fiche_lecture/1"
FICHIER_SCHEMA = ICI.parent / "references" / "schemas" / "fiche_lecture.v1.schema.json"


# ---------------------------------------------------------------------------------------------------------------
# Capture

def est_capturable(outil: str) -> bool:
    outil = str(outil or "")
    return outil.startswith("mcp__") and ("librejustice__" in outil or outil.endswith("legal_harness__read_document"))


def _enveloppe(v) -> bool:
    if isinstance(v, dict):
        return isinstance(v.get("structuredContent"), dict) or isinstance(v.get("content"), list)
    return isinstance(v, list) and bool(v) and all(isinstance(b, dict) and b.get("type") == "text" for b in v)


def decoder(brut, profondeur: int = 0):
    """Réponse d'un outil MCP en objet Python : chaîne JSON (forme observée dans Claude Code), blocs de contenu, ou objet."""
    if isinstance(brut, str):
        try:
            v = json.loads(brut)
        except json.JSONDecodeError:
            return {"_texte": brut}
        return decoder(v, profondeur + 1) if profondeur < 3 and _enveloppe(v) else v
    if isinstance(brut, dict):
        if isinstance(brut.get("structuredContent"), dict):
            return brut["structuredContent"]
        if not isinstance(brut.get("content"), list):
            return brut
        brut = brut["content"]
    if isinstance(brut, list):
        textes = [b.get("text", "") for b in brut if isinstance(b, dict) and b.get("type") == "text"]
        return decoder("\n".join(textes), profondeur + 1) if textes and profondeur < 3 else brut
    return None


def capturer(racine: Path, ev: dict) -> Path | None:
    """Enregistre un appel d'outil de lecture. Rend le chemin de la capture, ou None si l'outil n'est pas suivi."""
    outil = str(ev.get("tool_name") or "")
    if not est_capturable(outil):
        return None
    brut = ev.get("tool_response")
    texte = brut if isinstance(brut, str) else json.dumps(brut, ensure_ascii=False)
    dossier = racine / DOSSIER
    dossier.mkdir(parents=True, exist_ok=True)
    sha = hashlib.sha256(texte.encode("utf-8")).hexdigest()
    rang = sum(1 for f in dossier.glob("*.json") if not f.name.startswith(".")) + 1
    nom = f"{L.maintenant().strftime('%Y%m%dT%H%M%S')}_{rang:05d}_{outil.rsplit('__', 1)[-1]}_{sha[:8]}.json"
    doc = {"schema": SCHEMA_CAPTURE, "outil": outil, "entree": ev.get("tool_input") or {}, "horodatage": L.horodatage(),
           "horloge_fixee": os.environ.get("CONTENTIEUX_MAINTENANT") or None, "session_id": ev.get("session_id"),
           "agent": ev.get("agent_type") or "", "tool_use_id": ev.get("tool_use_id"), "sha256_reponse": sha,
           "reponse_brute": texte}
    chemin = dossier / nom
    L.ecrire_json(chemin, doc)
    ligne = {"fichier": nom, "sha256": L.sha256_fichier(chemin), "outil": outil, "horodatage": doc["horodatage"]}
    with open(racine / REGISTRE, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(ligne, ensure_ascii=False) + "\n")
    return chemin


# ---------------------------------------------------------------------------------------------------------------
# Normalisation des références

def sans_accent(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", sans_accent(str(s or "")).lower()).strip("-")


def cle_article(s) -> str:
    """« R. 811-1-1 », « r811-1-1 », « Article L242-2 » donnent r811-1-1, l242-2."""
    t = unicodedata.normalize("NFKC", str(s or "")).lower()
    t = t.replace("–", "-").replace("‑", "-").replace("‒", "-")
    t = re.sub(r"^\s*(articles?|art\.?)\s*", "", t)
    return re.sub(r"[\s.*]", "", t)


def numero(n) -> str:
    """Numéro de décision comparable : 25-70.017 et 2570017 se rejoignent, 24ma00153 devient 24MA00153."""
    return re.sub(r"[^0-9A-Z]", "", unicodedata.normalize("NFKC", str(n or "")).upper())


def compatibles(a: str | None, b: str | None) -> bool:
    """Deux identifiants de texte désignent le même texte si l'un prolonge l'autre (code-rural, code-rural-et-de-la-peche…)."""
    if not a or not b:
        return True
    a, b = slug(a), slug(b)
    return a.startswith(b) or b.startswith(a)


def chemin_url(u: str) -> str:
    u = re.sub(r"^https?://[^/]+", "", str(u or "")).split("?")[0].split("#")[0]
    return u.rstrip("/")


def date_url(u: str) -> str | None:
    m = re.search(r"[?&]date=(\d{4}-\d{2}-\d{2})", str(u or "")) or re.search(r"/(\d{4}-\d{2}-\d{2})/?(?:$|\?)", str(u or ""))
    return m.group(1) if m else None


def cible_lien(chemin: str) -> tuple[str, str] | None:
    """(code, article) d'un lien /norm/<ordre>/<code>/<article>[/<date>] ; None pour un texte entier ou une section."""
    p = chemin_url(chemin).strip("/").split("/")
    if len(p) < 4 or p[0] != "norm" or not re.match(r"^[lrda]?\d", p[3]):
        return None
    return p[2], cle_article(p[3])


RE_LIEN_NORME = re.compile(r"\]\((?:https?://librejustice\.fr)?(/norm/[^)\s]+)\)")
RE_EXPANSION = re.compile(r"\s?\(\+\s(?:\[[^\]]*\]\([^)]*\)(?:,\s)?)+\)")
RE_LIEN_MD = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def texte_source(t: str) -> str:
    """Texte servi par LibreJustice sans les liens ajoutés : « [L. 242-1](…) » redevient « L. 242-1 »."""
    return RE_LIEN_MD.sub(r"\1", RE_EXPANSION.sub("", str(t or "")))


# ---------------------------------------------------------------------------------------------------------------
# Lecture du registre

class Registre:
    """Captures intègres, indexées : articles lus (par article, avec leur version), sections, décisions, recherches."""

    def __init__(self, racine: Path):
        self.racine = racine
        self.lectures: list[dict] = []
        self.alterations: list[str] = []
        self.suppressions: list[str] = []
        self.normes: dict[str, list[dict]] = {}
        self.sections_lues: set[str] = set()
        self.decisions: dict[str, list[dict]] = {}
        self.apercus: dict[str, list[dict]] = {}
        self.recherches_decisions: list[dict] = []
        self.recherches_normes: list[dict] = []
        self.documents: list[dict] = []
        self._charger()
        for doc in self.lectures:
            self._indexer(doc)

    def _charger(self) -> None:
        dossier = self.racine / DOSSIER
        inscrits: dict[str, str] = {}
        reg = self.racine / REGISTRE
        if reg.is_file():
            for i, ligne in enumerate(reg.read_text(encoding="utf-8").splitlines(), 1):
                if not ligne.strip():
                    continue
                try:
                    x = json.loads(ligne)
                except json.JSONDecodeError:
                    self.alterations.append(f"registre.jsonl, ligne {i} illisible")
                    continue
                inscrits[str(x.get("fichier"))] = str(x.get("sha256"))
        for f in sorted(dossier.glob("*.json")) if dossier.is_dir() else []:
            if f.name.startswith("."):
                continue
            sha = inscrits.get(f.name)
            if sha is None:
                self.alterations.append(f"{f.name} : absente du registre, donc écrite hors du hook de capture")
                continue
            if L.sha256_fichier(f) != sha:
                self.alterations.append(f"{f.name} : modifiée depuis sa capture")
                continue
            doc = L.lire_json(f)
            if not isinstance(doc, dict) or doc.get("schema") != SCHEMA_CAPTURE:
                self.alterations.append(f"{f.name} : capture illisible")
                continue
            doc["fichier"] = f.name
            doc["reponse"] = decoder(doc.get("reponse_brute"))
            self.lectures.append(doc)
        for nom in inscrits:
            if not (dossier / nom).is_file():
                self.suppressions.append(nom)

    def _indexer(self, doc: dict) -> None:
        court = str(doc.get("outil", "")).rsplit("__", 1)[-1]
        r, e = doc.get("reponse"), doc.get("entree") or {}
        if court == "read_document":
            self.documents.append({"lecture": doc["fichier"], "entree": e, "texte": "\n".join(_chaines(r))})
            return
        if not isinstance(r, dict):
            return
        if court == "get_norm":
            self._norme(doc, r, e)
        elif court == "get_decision":
            d = {"lecture": doc["fichier"], "numeros": r.get("docket_numbers") or [], "titre": r.get("title") or "",
                 "url": chemin_url(r.get("url") or e.get("url") or ""), "texte": r.get("text") or "", "standing": r.get("standing"),
                 "chronologie": r.get("case_chronology"), "commentaires": r.get("commentaries") or [],
                 "publication": r.get("publication") or [], "siege": r.get("seat"), "formation": r.get("formation") or [],
                 "date": r.get("date"), "sommaire": r.get("court_summary") or "", "ruling": r.get("ruling"), "solution": r.get("solution")}
            for n in d["numeros"]:
                self.decisions.setdefault(numero(n), []).append(d)
        elif court == "search_decisions":
            hits = [h for h in r.get("hits") or [] if isinstance(h, dict)]
            self.recherches_decisions.append({"lecture": doc["fichier"], "entree": e, "total": r.get("total"), "hits": hits})
            for h in hits:
                for n in h.get("docket_numbers") or []:
                    self.apercus.setdefault(numero(n), []).append({"lecture": doc["fichier"], "ai_summary": h.get("ai_summary") or "",
                                                                    "court_summary": h.get("court_summary") or "", "snippet": h.get("snippet") or ""})
        elif court == "search_norms":
            self.recherches_normes.append({"lecture": doc["fichier"], "entree": e, "total": r.get("total"),
                                           "hits": [h for h in r.get("hits") or [] if isinstance(h, dict)]})

    def _norme(self, doc: dict, r: dict, e: dict) -> None:
        url = chemin_url(r.get("url") or e.get("url") or "")
        as_of = e.get("as_of") or date_url(e.get("url") or "")
        code = r.get("code") or e.get("code") or (url.split("/")[3] if url.count("/") >= 3 else "")
        commun = {"lecture": doc["fichier"], "code": code, "as_of": as_of, "horodatage": doc.get("horodatage")}
        if r.get("number"):
            sec = r.get("section") or {}
            self.normes.setdefault(cle_article(r["number"]), []).append({
                **commun, "mode": "article", "numero": r["number"], "titre": r.get("title") or "", "url": url,
                "valid_from": r.get("valid_from"), "valid_to": r.get("valid_to"), "statut": r.get("status"),
                "texte": r.get("text") or "", "note": r.get("note") or "", "versions": r.get("versions") or [],
                "section": chemin_url(sec.get("url") or ""), "section_titre": sec.get("label") or ""})
        elif isinstance(r.get("articles"), list):
            self.sections_lues.add(url)
            for a in r["articles"]:
                if isinstance(a, dict) and a.get("number"):
                    self.normes.setdefault(cle_article(a["number"]), []).append({
                        **commun, "mode": "section", "numero": a["number"], "titre": r.get("title") or "", "url": chemin_url(a.get("url") or ""),
                        "valid_from": None, "valid_to": None, "statut": None, "texte": a.get("text") or "", "note": "",
                        "versions": [], "section": url, "section_titre": r.get("title") or ""})

    # Requêtes sur l'index

    def entrees_article(self, code: str | None, art: str) -> list[dict]:
        return [x for x in self.normes.get(art, []) if compatibles(x["code"], code)]

    def article_lu(self, code: str | None, art: str) -> bool:
        return bool(self.entrees_article(code, art))

    def recherches_par_article(self, code: str | None, art: str) -> list[dict]:
        res = []
        for s in self.recherches_decisions:
            cles = s["entree"].get("legal_article") or []
            for k in [cles] if isinstance(cles, str) else cles:
                instr, _, a = str(k).partition("|")
                if a and cle_article(a) == art and compatibles(instr, code):
                    res.append(s)
                    break
        return res

    def decision(self, num: str) -> dict | None:
        lues = self.decisions.get(numero(num)) or []
        return max(lues, key=lambda d: len(d["texte"])) if lues else None

    def textes_lus(self) -> list[tuple[str, str]]:
        """(étiquette, texte) de toutes les lectures, pour retrouver une citation ailleurs que dans sa source annoncée."""
        res = []
        for art, entrees in self.normes.items():
            for x in entrees:
                res.append((f"article {x['numero']} ({x['code']}, {x['lecture']})", x["texte"]))
        for ds in self.decisions.values():
            for d in ds:
                res.append((f"décision {d['titre'] or d['lecture']}", d["texte"]))
        for d in self.documents:
            res.append((f"document {d['lecture']}", d["texte"]))
        return res


def _chaines(obj) -> list[str]:
    if isinstance(obj, str):
        return [obj]
    if isinstance(obj, dict):
        return [s for v in obj.values() for s in _chaines(v)]
    if isinstance(obj, list):
        return [s for v in obj for s in _chaines(v)]
    return []


# ---------------------------------------------------------------------------------------------------------------
# Versions et suite d'une décision

def _intervalle(d: str, versions: list[dict]) -> tuple | None:
    for v in versions:
        debut, fin = str(v.get("valid_from") or ""), str(v.get("valid_to") or "")
        if debut and debut <= d and (not fin or d <= fin):
            return (debut, fin)
    return None


def couvre(x: dict, d: str, versions: list[dict]) -> bool:
    """La lecture x donne-t-elle la version applicable à la date d ?"""
    if x.get("valid_from"):
        return str(x["valid_from"]) <= d and (not x.get("valid_to") or d <= str(x["valid_to"]))
    a = x.get("as_of")
    if a and versions:
        iv = _intervalle(d, versions)
        return iv is not None and iv == _intervalle(str(a), versions)
    if a:
        return str(a) == d
    return len(versions) == 1 and str(versions[0].get("valid_from") or "") <= d


RE_STANDING_DEFAVORABLE = re.compile(r"QUASH|ANNUL|REVERS|OVERRUL|SET_ASIDE|VACAT|CASS", re.I)
RE_RULING_DEFAVORABLE = re.compile(r"cassation|annulation|infirmation|r[ée]formation|censure", re.I)
RE_NUMERO_TITRE = re.compile(r"(\d{2}[A-Z]{2}\d{5}|\d{2}-\d{2}\.\d{3}|\d{3,6}/\d{2}|\d{5,7})\s*$")


def suite_defavorable(d: dict) -> list[dict]:
    """Décisions ultérieures connues qui défont la décision lue : selon standing, puis selon la décision qui la suit."""
    res = []
    if d.get("standing") and RE_STANDING_DEFAVORABLE.search(str(d["standing"])):
        res.append({"source": "standing", "valeur": d["standing"]})
    chrono = d.get("chronologie") if isinstance(d.get("chronologie"), list) else []
    cur = next((i for i, x in enumerate(chrono) if isinstance(x, dict) and x.get("current")), None)
    if cur:
        suivante = chrono[cur - 1]
        if RE_RULING_DEFAVORABLE.search(str(suivante.get("ruling") or "")) and suivante.get("solution") in (None, "GRANTED", "PARTLY_GRANTED"):
            m = RE_NUMERO_TITRE.search(str(suivante.get("title") or ""))
            res.append({"source": "case_chronology", "valeur": suivante.get("ruling"), "titre": suivante.get("title"),
                        "url": suivante.get("url"), "numero": m.group(1) if m else ""})
    return res


# ---------------------------------------------------------------------------------------------------------------
# Repérage des articles et des décisions cités dans une écriture ou une note

CODES = {
    "code civil": "code-civil", "code de procédure civile": "code-de-procedure-civile",
    "code de justice administrative": "code-de-justice-administrative", "code de l'urbanisme": "code-de-l-urbanisme",
    "code des relations entre le public et l'administration": "code-des-relations-entre-le-public-et-l-administration",
    "code de l'environnement": "code-de-l-environnement", "code général des collectivités territoriales": "code-general-des-collectivites-territoriales",
    "code du travail": "code-du-travail", "code pénal": "code-penal", "code de procédure pénale": "code-de-procedure-penale",
    "code de commerce": "code-de-commerce", "code de la consommation": "code-de-la-consommation", "code de la santé publique": "code-de-la-sante-publique",
    "code général des impôts": "code-general-des-impots", "livre des procédures fiscales": "livre-des-procedures-fiscales",
    "code rural et de la pêche maritime": "code-rural", "code rural": "code-rural", "code de la sécurité sociale": "code-de-la-securite-sociale",
    "code de la construction et de l'habitation": "code-de-la-construction-et-de-l-habitation",
    "code de l'entrée et du séjour des étrangers et du droit d'asile": "code-de-l-entree-et-du-sejour-des-etrangers-et-du-droit-d-asile",
    "code des procédures civiles d'exécution": "code-des-procedures-civiles-d-execution", "code de l'organisation judiciaire": "code-de-l-organisation-judiciaire",
    "code général de la fonction publique": "code-general-de-la-fonction-publique", "code de la commande publique": "code-de-la-commande-publique",
    "code de l'éducation": "code-de-l-education", "code de la route": "code-de-la-route", "code des assurances": "code-des-assurances",
    "code monétaire et financier": "code-monetaire-et-financier", "code de la propriété intellectuelle": "code-de-la-propriete-intellectuelle",
    "code de l'action sociale et des familles": "code-de-l-action-sociale-et-des-familles", "code de la sécurité intérieure": "code-de-la-securite-interieure",
    "code général de la propriété des personnes publiques": "code-general-de-la-propriete-des-personnes-publiques", "code de l'énergie": "code-de-l-energie",
}
ABREVIATIONS = {
    "cja": "code-de-justice-administrative", "cpc": "code-de-procedure-civile", "crpa": "code-des-relations-entre-le-public-et-l-administration",
    "cgct": "code-general-des-collectivites-territoriales", "csp": "code-de-la-sante-publique", "cpp": "code-de-procedure-penale",
    "cgi": "code-general-des-impots", "lpf": "livre-des-procedures-fiscales", "css": "code-de-la-securite-sociale",
    "cch": "code-de-la-construction-et-de-l-habitation", "ceseda": "code-de-l-entree-et-du-sejour-des-etrangers-et-du-droit-d-asile",
    "cpce": "code-des-procedures-civiles-d-execution", "coj": "code-de-l-organisation-judiciaire", "cgfp": "code-general-de-la-fonction-publique",
    "ccp": "code-de-la-commande-publique", "c. civ.": "code-civil", "c. urb.": "code-de-l-urbanisme", "c. trav.": "code-du-travail",
    "c. pén.": "code-penal", "c. com.": "code-de-commerce", "c. consom.": "code-de-la-consommation", "c. env.": "code-de-l-environnement",
    "c. rur.": "code-rural",
}
_ABREV = r"(CJA|CPC|CRPA|CGCT|CSP|CPP|CGI|LPF|CSS|CCH|CESEDA|CPCE|COJ|CGFP|CCP|C\.\s?civ\.|C\.\s?urb\.|C\.\s?trav\.|C\.\s?p[ée]n\.|C\.\s?com\.|C\.\s?consom\.|C\.\s?env\.|C\.\s?rur\.)"
ITEM = r"(?:[LRDA]\.?\s?\*?\s?)?\d+(?:\s?[-–]\s?\d+)*(?:\s(?:bis|ter|quater|quinquies|sexies)\b)?(?!\s?°)"
RE_ARTICLES = re.compile(rf"\b(?:articles?|art\.)\s+({ITEM}(?:\s*(?:,|et|à|ou)\s*{ITEM})*)", re.I)
RE_ITEM = re.compile(ITEM, re.I)
RE_NU = re.compile(r"(?<![\w.])([LRD])\.\s?(\d+(?:-\d+)+)\b")
RE_INSTRUMENT = re.compile(r"\b(?:du|de la|de l['’]|des)\s+(code\b[^,;()\n]{0,90}|livre des proc[ée]dures fiscales|loi\b[^,;()\n]{0,70}|d[ée]cret\b[^,;()\n]{0,70}|"
                           r"ordonnance\b[^,;()\n]{0,70}|constitution\b|convention\b[^,;()\n]{0,60}|trait[ée]\b[^,;()\n]{0,60}|r[èe]glement\b[^,;()\n]{0,60})", re.I)
RE_ABREV_APRES = re.compile(rf"^\W{{0,4}}(?:du\s+)?{_ABREV}(?!\w)", re.I)
RE_ABREV_AVANT = re.compile(rf"{_ABREV}\s*,?\s*(?:art\.|articles?)?\s*$", re.I)
RE_SON_ARTICLE = re.compile(r"\b(code\b[^,;.()\n]{3,90}?)\s*,?\s*(?:en|à|par) son article\s*$", re.I)
RE_DATE_UTILE = re.compile(r"(?im)^\W*date (?:utile|du droit applicable)\s*:\s*(\d{4}-\d{2}-\d{2})")


def _instrument(phrase: str) -> str | None:
    p = sans_accent(phrase).lower().strip()
    if p.startswith(("code", "livre des procedures")):
        s = slug(p)
        for nom in sorted(CODES, key=len, reverse=True):
            if s.startswith(slug(nom)):
                return CODES[nom]
        return s
    m = re.match(r"(loi|decret|ordonnance)\s+(?:organique\s+)?(n\s*°?\s*[\d-]+|du\s+\d{1,2}(?:er)?\s+\w+\s+\d{4})", p)
    if m:
        return slug(m.group(0))
    if p.startswith("constitution"):
        return "constitution-du-4-octobre-1958"
    return None


def _abrev(s: str) -> str | None:
    k = re.sub(r"\s+", " ", s.lower()).replace("c.civ.", "c. civ.")
    k = re.sub(r"^c\.\s?", "c. ", k)
    return ABREVIATIONS.get(k.replace("pen.", "pén."), ABREVIATIONS.get(k))


def instrument_de(t: str, debut: int, fin: int) -> str | None:
    """Texte auquel appartient l'article cité entre debut et fin : « … du code X », « CJA, art. … », « le code X, en son article »."""
    apres = t[fin:fin + 160]
    coupe = re.search(r";|\n|\b(?:articles?|art\.)\s", apres)
    fenetre = apres[:coupe.start()] if coupe else apres
    m = RE_ABREV_APRES.match(apres)
    if m:
        return _abrev(m.group(1))
    m = RE_INSTRUMENT.search(fenetre)
    if m and m.start() < 60:
        return _instrument(m.group(1))
    avant = t[max(0, debut - 140):debut]
    m = RE_ABREV_AVANT.search(avant)
    if m:
        return _abrev(m.group(1))
    m = RE_SON_ARTICLE.search(avant)
    if m:
        return _instrument(m.group(1))
    return None


def articles_cites(texte: str) -> list[dict]:
    """Articles cités hors des passages entre guillemets, avec le texte auquel ils appartiennent quand il se lit."""
    import lint_ecriture as LINT
    t = LINT._hors_citations(texte)
    res: dict[tuple, dict] = {}
    prises: list[tuple[int, int]] = []

    def ajouter(brut: str, pos: int, instr: str | None) -> None:
        art = cle_article(brut)
        if not re.search(r"\d", art):
            return
        k = (instr, art)
        x = res.setdefault(k, {"article": art, "affichage": re.sub(r"\s+", " ", brut).strip(), "instrument": instr, "lignes": []})
        x["lignes"].append(LINT._ligne(texte, pos))

    for m in RE_ARTICLES.finditer(t):
        prises.append((m.start(), m.end()))
        instr = instrument_de(t, m.start(), m.end())
        for it in RE_ITEM.finditer(m.group(1)):
            ajouter(it.group(0), m.start(1) + it.start(), instr)
    for m in RE_NU.finditer(t):
        if any(a <= m.start() < b for a, b in prises):
            continue
        ajouter(f"{m.group(1)}. {m.group(2)}", m.start(), instrument_de(t, m.start(), m.end()))
    return list(res.values())


def numeros_propres(racine: Path, fiche: dict | None) -> set[str]:
    a = L.lire_json(racine / "etat/affaire.json", {}) or {}
    propres = {str(i.get("numero", "")) for i in a.get("instances", []) if i.get("numero")}
    propres |= {str(n) for n in (fiche or {}).get("numeros_non_jurisprudentiels", [])}
    return {p.replace(" ", "") for p in propres}


def decisions_citees(racine: Path, texte: str, fiche: dict | None = None) -> list[dict]:
    import lint_ecriture as LINT
    return LINT.analyser(LINT._hors_citations(texte), numeros_propres=numeros_propres(racine, fiche)).decisions_citees


# ---------------------------------------------------------------------------------------------------------------
# Dates utiles

def dates_utiles(texte: str, fiche: dict | None, date_option: str | None) -> tuple[dict, list[str], bool]:
    """(dates propres à un article, dates admises par défaut, date déclarée ?)."""
    fiche = fiche or {}
    propres = {}
    for k, v in (fiche.get("dates_utiles") or {}).items():
        instr, _, art = str(k).rpartition("|")
        propres[(slug(instr) or None, cle_article(art))] = str(v)[:10]
    if date_option:
        return propres, [date_option[:10]], True
    if fiche.get("date_droit_applicable"):
        return propres, [str(fiche["date_droit_applicable"])[:10]], True
    m = RE_DATE_UTILE.search(texte or "")
    if m:
        return propres, [m.group(1)], True
    candidates = [str(a.get("date"))[:10] for a in fiche.get("actes_attaques") or [] if isinstance(a, dict) and L.date_simple(a.get("date"))]
    candidates.append(L.maintenant().date().isoformat())
    return propres, sorted(set(candidates)), False


def _date_article(propres: dict, instr: str | None, art: str, defaut: list[str]) -> tuple[list[str], bool]:
    for (i, a), d in propres.items():
        if a == art and compatibles(i, instr):
            return [d], True
    return defaut, None


# ---------------------------------------------------------------------------------------------------------------
# Couverture

def etat_article(reg: Registre, a: dict, dates: list[str]) -> dict:
    entrees = reg.entrees_article(a["instrument"], a["article"])
    versions = next((x["versions"] for x in entrees if x["versions"]), [])
    a_date = {d: any(couvre(x, d, versions) for x in entrees) for d in dates}
    sections = {x["section"] for x in entrees if x["section"]}
    section_lue = any(x["mode"] == "section" for x in entrees) or any(s in reg.sections_lues for s in sections)
    renvois = {}
    for x in entrees:
        if x["mode"] == "article":
            for chemin in RE_LIEN_NORME.findall(x["texte"]):
                c = cible_lien(chemin)
                if c and c[1] != a["article"]:
                    renvois[c] = reg.article_lu(*c)
    recherches = reg.recherches_par_article(a["instrument"], a["article"])
    publiees = [s for s in recherches if any(not str(p).startswith("INEDIT") for p in s["entree"].get("publication") or [])]
    larges = [s for s in recherches if not s["entree"].get("publication") or any(str(p).startswith("INEDIT") for p in s["entree"]["publication"])]
    return {
        "article": a["article"], "affichage": a["affichage"], "instrument": a["instrument"], "lignes": a["lignes"],
        "lu": bool(entrees), "lectures": sorted({x["lecture"] for x in entrees}),
        "versions_lues": sorted({f"version du {x.get('valid_from') or '?'} " + (f"au {x['valid_to']}" if x.get("valid_to") else "en vigueur")
                                 for x in entrees if x["mode"] == "article"}),
        "versions_connues": len(versions), "dates": dates, "a_date": a_date, "lu_a_la_date": any(a_date.values()) if dates else bool(entrees),
        "section": sorted(sections), "section_lue": section_lue,
        "renvois": [f"{c}|{art}" for (c, art) in sorted(renvois)], "renvois_non_suivis": [f"{c}|{art}" for (c, art), lu in sorted(renvois.items()) if not lu],
        "jurisprudence_par_article": [s["lecture"] for s in recherches], "jurisprudence_publiee": bool(publiees), "jurisprudence_toutes": bool(larges),
        "disposition_transitoire": next((x["note"] for x in entrees if x.get("note")), ""),
    }


def etat_decision(reg: Registre, num: str) -> dict:
    d = reg.decision(num)
    if d is None:
        return {"numero": num, "lue": False, "vue_en_apercu": numero(num) in reg.apercus}
    return {"numero": num, "lue": True, "lecture": d["lecture"], "titre": d["titre"], "texte_caracteres": len(d["texte"]),
            "standing": d["standing"], "chronologie": d["chronologie"] is not None, "suite_verifiee": d["standing"] is not None or d["chronologie"] is not None,
            "suite_defavorable": suite_defavorable(d), "commentaires": [f"{c.get('kind', '?')} : {c.get('title') or c.get('publisher') or ''} {c.get('url', '')}".strip()
                                                                         for c in d["commentaires"] if isinstance(c, dict)],
            "publication": d["publication"], "siege": d["siege"], "formation": d["formation"]}


def couverture(racine: Path, texte: str, fiche: dict | None = None, date_option: str | None = None, reg: Registre | None = None) -> dict:
    reg = reg or Registre(racine)
    propres, defaut, declaree = dates_utiles(texte, fiche, date_option)
    arts = []
    for a in articles_cites(texte):
        dates, propre = _date_article(propres, a["instrument"], a["article"], defaut)
        x = etat_article(reg, a, dates)
        x["date_declaree"] = bool(propre) or declaree
        arts.append(x)
    vus, decs = set(), []
    for dc in decisions_citees(racine, texte, fiche):
        if numero(dc["numero"]) in vus:
            continue
        vus.add(numero(dc["numero"]))
        decs.append({**etat_decision(reg, dc["numero"]), "ligne": dc["ligne"]})
    return {"articles": arts, "decisions": decs, "dates_par_defaut": defaut, "date_declaree": declaree,
            "alterations": reg.alterations, "suppressions": reg.suppressions, "captures": len(reg.lectures)}


def resume_couverture(cv: dict, nom: str) -> str:
    l = [f"Couverture de {nom} : {cv['captures']} lecture(s) capturée(s) au registre ; date utile "
         f"{'déclarée ' + ', '.join(cv['dates_par_defaut']) if cv['date_declaree'] else 'non déclarée (admises : ' + ', '.join(cv['dates_par_defaut']) + ')'}."]
    for x in cv["alterations"]:
        l.append(f"  ALTÉRATION {x}")
    l.append(f"Articles cités : {len(cv['articles'])}.")
    for a in cv["articles"]:
        lieu = a["instrument"] or "texte non identifié"
        if not a["lu"]:
            l.append(f"- {a['affichage']} ({lieu}), l. {a['lignes'][0]} : JAMAIS LU.")
            continue
        dates = ", ".join(f"{d} {'oui' if ok else 'NON'}" for d, ok in a["a_date"].items())
        l.append(f"- {a['affichage']} ({lieu}) : lu ({', '.join(a['versions_lues']) or 'par section'}) ; à la date utile : {dates} ; "
                 f"section {'lue' if a['section_lue'] else 'NON LUE'} ; renvois suivis {len(a['renvois']) - len(a['renvois_non_suivis'])}/{len(a['renvois'])}"
                 f"{' (non suivis : ' + ', '.join(a['renvois_non_suivis'][:6]) + ')' if a['renvois_non_suivis'] else ''} ; jurisprudence par article "
                 f"{'cherchée (' + ('publiée' if a['jurisprudence_publiee'] else 'sans filtre de publication') + (', puis toutes' if a['jurisprudence_toutes'] and a['jurisprudence_publiee'] else '') + ')' if a['jurisprudence_par_article'] else 'NON CHERCHÉE'}.")
        if a["disposition_transitoire"]:
            l.append(f"    note de version : {a['disposition_transitoire'][:220]}")
    l.append(f"Décisions citées : {len(cv['decisions'])}.")
    for d in cv["decisions"]:
        if not d["lue"]:
            l.append(f"- n° {d['numero']} (l. {d['ligne']}) : JAMAIS LUE{' (vue seulement en aperçu de recherche)' if d['vue_en_apercu'] else ''}.")
            continue
        suite = "; ".join(f"{s['valeur']}{' par ' + s['titre'] if s.get('titre') else ''}" for s in d["suite_defavorable"])
        l.append(f"- n° {d['numero']} : lue ({d['titre']}, {d['texte_caracteres']} caractères) ; suite "
                 f"{'vérifiée (' + str(d['standing']) + ')' if d['suite_verifiee'] else 'non donnée par la source'}"
                 f"{' ; DÉFAITE : ' + suite if suite else ''} ; conclusions et rapports signalés : {len(d['commentaires'])}.")
    return "\n".join(l)


def manques_couverture(cv: dict) -> int:
    n = len(cv["alterations"])
    n += sum(1 for a in cv["articles"] if not a["lu_a_la_date"])
    n += sum(1 for d in cv["decisions"] if not d["lue"] or d["suite_defavorable"])
    return n


# ---------------------------------------------------------------------------------------------------------------
# Citations

RE_CITATION = re.compile(r"«([^»]{1,4000})»|“([^”]{1,4000})”|\"([^\"\n]{1,1500})\"")


def passages_cites(texte: str) -> list[dict]:
    res = []
    for m in RE_CITATION.finditer(texte):
        contenu = next(g for g in m.groups() if g is not None)
        res.append({"debut": m.start(), "fin": m.end(), "citation": contenu.strip()})
    pos = 0
    bloc, debut = [], None
    for ligne in texte.split("\n") + [""]:
        if ligne.lstrip().startswith(">"):
            if debut is None:
                debut = pos
            bloc.append(ligne.lstrip()[1:].strip())
        elif debut is not None:
            contenu = " ".join(bloc).strip()
            if contenu and not any(r["debut"] >= debut and r["fin"] <= pos for r in res):
                res.append({"debut": debut, "fin": pos, "citation": contenu})
            bloc, debut = [], None
        pos += len(ligne) + 1
    return sorted(res, key=lambda r: r["debut"])


def _references(texte: str, debut: int, fin: int, propres: set[str]) -> list[dict]:
    """Références de décisions, pièces et articles du paragraphe, hors du passage cité lui-même."""
    import lint_ecriture as LINT
    refs = []
    for _, motif in LINT.RE_DECISIONS:
        for m in motif.finditer(texte, debut, fin):
            if m.group(1).replace(" ", "") not in propres:
                refs.append({"genre": "decision", "debut": m.start(), "fin": m.end(), "valeur": m.group(1)})
    for m in LINT.RE_PIECE.finditer(texte, debut, fin):
        cotes = LINT._nombres_pieces(m.group(1))
        if cotes:
            refs.append({"genre": "piece", "debut": m.start(), "fin": m.end(), "valeur": [str(c) for c in cotes]})
    para = texte[debut:fin]
    for a in articles_cites(para):
        for m in re.finditer(re.escape(a["affichage"]).replace(r"\ ", r"\s*"), para):
            refs.append({"genre": "article", "debut": debut + m.start(), "fin": debut + m.end(), "valeur": a})
    return refs


def attribution(texte: str, c: dict, propres: set[str]) -> dict | None:
    debut_p = texte.rfind("\n\n", 0, c["debut"])
    debut_p = 0 if debut_p < 0 else debut_p + 2
    fin_p = texte.find("\n\n", c["fin"])
    fin_p = len(texte) if fin_p < 0 else fin_p
    refs = [r for r in _references(texte, debut_p, fin_p, propres) if r["fin"] <= c["debut"] or r["debut"] >= c["fin"]]
    apres = sorted((r for r in refs if r["debut"] >= c["fin"]), key=lambda r: r["debut"])
    avant = sorted((r for r in refs if r["fin"] <= c["debut"]), key=lambda r: -r["fin"])
    if apres and apres[0]["debut"] - c["fin"] <= 80:
        return apres[0]
    if avant and c["debut"] - avant[0]["fin"] <= 300:
        return avant[0]
    if apres and apres[0]["debut"] - c["fin"] <= 160:
        return apres[0]
    return None


def plus_proche(citation: str, source: str) -> tuple[float, str]:
    """Passage de la source le plus proche de la citation (rapport de similarité, texte exact de la source)."""
    import pieces as P
    segs = [s for s in P.RE_ELLIPSE.split(citation) if s.strip()]
    cible = max(segs, key=len) if segs else citation
    def jeton(w: str) -> str:
        return re.sub(r"[^\w'-]", "", P.normaliser(w))

    mots_c = [jeton(w) for w in cible.split()]
    jetons = [(m.start(), m.end(), jeton(m.group(0))) for m in re.finditer(r"\S+", source)]
    n = len(mots_c)
    if not n or not jetons:
        return 0.0, ""
    meilleur, ou = 0.0, (0, 0)
    sm = difflib.SequenceMatcher(autojunk=False)
    sm.set_seq2(mots_c)
    for taille in range(max(1, n - 2), n + 5):
        for i in range(0, max(1, len(jetons) - taille + 1)):
            sm.set_seq1([j[2] for j in jetons[i:i + taille]])
            if sm.real_quick_ratio() <= meilleur or sm.quick_ratio() <= meilleur:
                continue
            r = sm.ratio()
            if r > meilleur:
                meilleur, ou = r, (jetons[i][0], jetons[min(i + taille, len(jetons)) - 1][1])
    return round(meilleur, 2), source[ou[0]:ou[1]]


def _sources_attribuees(reg: Registre, ref: dict, racine: Path, ctx_pieces) -> tuple[str, list[dict]]:
    """Libellé de la source annoncée et ses textes lus : [{texte, nature, version}]."""
    if ref["genre"] == "decision":
        d = reg.decisions.get(numero(ref["valeur"])) or []
        textes = [{"texte": texte_source(x["texte"]), "nature": "texte", "lecture": x["lecture"]} for x in d]
        textes += [{"texte": texte_source(x["sommaire"]), "nature": "sommaire", "lecture": x["lecture"]} for x in d if x["sommaire"]]
        for ap in reg.apercus.get(numero(ref["valeur"])) or []:
            for k in ("ai_summary", "court_summary", "snippet"):
                if ap[k]:
                    textes.append({"texte": re.sub(r"</?mark>", "", ap[k]), "nature": "apercu", "lecture": ap["lecture"]})
        return f"décision n° {ref['valeur']}", textes
    if ref["genre"] == "article":
        a = ref["valeur"]
        entrees = reg.entrees_article(a["instrument"], a["article"])
        return (f"article {a['affichage']}" + (f" ({a['instrument']})" if a["instrument"] else ""),
                [{"texte": texte_source(x["texte"]), "nature": "texte", "lecture": x["lecture"], "entree": x} for x in entrees])
    textes = []
    for cote in ref["valeur"]:
        pages = ctx_pieces.textes(cote) if ctx_pieces else None
        if pages:
            textes.append({"texte": "\n".join(p[0] for _, p in sorted(pages.items())), "nature": "piece", "lecture": f"extraction de la pièce {cote}"})
    return f"pièce {', '.join(ref['valeur'])}", textes


def verifier_citations(racine: Path, texte: str, fiche: dict | None = None, reg: Registre | None = None, date_option: str | None = None) -> list[dict]:
    """Statut de chaque passage cité : exacte, exacte_sommaire, apercu, mal_attribuee, autre_version, inexacte,
    introuvable, non_attribuee_trouvee, non_attribuee_introuvable, trop_courte."""
    import lint_ecriture as LINT
    import pieces as P
    reg = reg or Registre(racine)
    propres = numeros_propres(racine, fiche)
    ctx = P.Contexte(racine)
    propres_dates, defaut, _ = dates_utiles(texte, fiche, date_option)
    tous = None
    res = []
    for c in passages_cites(texte):
        x = {"citation": c["citation"], "ligne": LINT._ligne(texte, c["debut"])}
        if len(re.findall(r"\w+", c["citation"])) < 4:
            res.append({**x, "statut": "trop_courte"})
            continue
        ref = attribution(texte, c, propres)
        if ref is None:
            if tous is None:
                tous = [(e, texte_source(t)) for e, t in reg.textes_lus()]
                for cote in ctx.bordereau:
                    pages = ctx.textes(cote)
                    if pages:
                        tous.append((f"pièce {cote}", "\n".join(p[0] for _, p in sorted(pages.items()))))
            ou = next((e for e, t in tous if P.trouver(c["citation"], t)), None)
            res.append({**x, "statut": "non_attribuee_trouvee" if ou else "non_attribuee_introuvable", "trouvee_dans": ou})
            continue
        libelle, textes = _sources_attribuees(reg, ref, racine, ctx)
        x["source"] = libelle
        trouves = [t for t in textes if P.trouver(c["citation"], t["texte"])]
        if any(t["nature"] in ("texte", "piece") for t in trouves):
            if ref["genre"] == "article":
                a = ref["valeur"]
                dates, _ = _date_article(propres_dates, a["instrument"], a["article"], defaut)
                entrees = [t["entree"] for t in trouves if t.get("entree")]
                versions = next((e["versions"] for e in entrees if e["versions"]), [])
                if entrees and not any(couvre(e, d, versions) for e in entrees for d in dates):
                    res.append({**x, "statut": "autre_version", "detail": f"lue dans une version qui ne couvre pas {', '.join(dates)}"})
                    continue
            res.append({**x, "statut": "exacte", "lecture": next(t["lecture"] for t in trouves if t["nature"] in ("texte", "piece"))})
            continue
        if any(t["nature"] == "sommaire" for t in trouves):
            res.append({**x, "statut": "exacte_sommaire"})
            continue
        if trouves:
            res.append({**x, "statut": "apercu"})
            continue
        if tous is None:
            tous = [(e, texte_source(t)) for e, t in reg.textes_lus()]
        ailleurs = next((e for e, t in tous if P.trouver(c["citation"], t)), None)
        if ailleurs:
            res.append({**x, "statut": "mal_attribuee", "trouvee_dans": ailleurs})
            continue
        pleins = [t for t in textes if t["nature"] in ("texte", "piece")]
        if not pleins:
            res.append({**x, "statut": "introuvable", "detail": f"la source annoncée ({libelle}) n'a jamais été lue en entier dans le registre"})
            continue
        ratio, passage = max((plus_proche(c["citation"], t["texte"]) for t in pleins), key=lambda r: r[0])
        if ratio >= 0.7:
            res.append({**x, "statut": "inexacte", "ressemblance": ratio, "texte_source": passage})
        else:
            res.append({**x, "statut": "introuvable", "detail": f"aucun passage approchant dans {libelle}", "ressemblance": ratio})
    return res


def resume_citations(res: list[dict], nom: str) -> str:
    l = [f"Citations de {nom} : {len(res)} passage(s) entre guillemets."]
    for x in res:
        cit = x["citation"] if len(x["citation"]) <= 140 else x["citation"][:137] + "..."
        ligne = f"- l. {x['ligne']} {x['statut'].upper()}{' (' + x['source'] + ')' if x.get('source') else ''} « {cit} »"
        if x.get("texte_source"):
            ligne += f"\n    texte de la source : « {x['texte_source']} »"
        if x.get("trouvee_dans"):
            ligne += f"\n    retrouvée dans : {x['trouvee_dans']}"
        if x.get("detail"):
            ligne += f"\n    {x['detail']}"
        l.append(ligne)
    return "\n".join(l)


GRAVES_CITATION = {"inexacte", "introuvable", "apercu"}


# ---------------------------------------------------------------------------------------------------------------
# Portée : décisions défaites par leur suite

RE_DIT_DEFAIT = re.compile(r"annul|cass[ée]|censur|infirm|r[ée]form|revir", re.I)


def _hors_citations(t: str) -> str:
    import lint_ecriture as LINT
    return LINT._hors_citations(t)


def portee(racine: Path, texte: str | None = None, fiche: dict | None = None, reg: Registre | None = None) -> list[dict]:
    reg = reg or Registre(racine)
    res = []
    if texte is None:
        vus = set()
        for ds in reg.decisions.values():
            for d in ds:
                if d["lecture"] in vus:
                    continue
                vus.add(d["lecture"])
                s = suite_defavorable(d)
                if s:
                    res.append({"numero": ", ".join(d["numeros"]), "titre": d["titre"], "suite": s})
        return res
    for dc in decisions_citees(racine, texte, fiche):
        d = reg.decision(dc["numero"])
        if d is None:
            continue
        s = suite_defavorable(d)
        if not s:
            continue
        # L'écriture le dit si, dans un paragraphe qui cite la décision, elle nomme la décision ultérieure ou son annulation.
        # Le numéro de la décision ultérieure cité ailleurs, pour une autre raison, ne suffit pas.
        ulterieurs = [x["numero"] for x in s if x.get("numero")]
        dit = False
        for m in re.finditer(re.escape(dc["numero"]), texte):
            a = texte.rfind("\n\n", 0, m.start())
            b = texte.find("\n\n", m.end())
            para = texte[a + 2 if a >= 0 else 0:b if b >= 0 else len(texte)]
            if RE_DIT_DEFAIT.search(_hors_citations(para)) or any(u in para for u in ulterieurs):
                dit = True
                break
        res.append({"numero": dc["numero"], "ligne": dc["ligne"], "titre": d["titre"], "suite": s, "dit_dans_l_ecriture": dit})
    return res


# ---------------------------------------------------------------------------------------------------------------
# Contrôle avant dépôt (format de gate.py)

def controler(racine: Path, ecriture: Path, fiche: dict | None, texte: str, c) -> None:
    """Appelle c(code, gravite, message, **extra) pour chaque défaut de lecture de l'écriture."""
    fiche = fiche or {}
    reg = Registre(racine)
    if reg.alterations:
        c("REGISTRE_LECTURES_ALTERE", "BLOQUANT", f"{len(reg.alterations)} capture(s) du registre des lectures altérée(s) ou écrite(s) à la main : "
          f"{'; '.join(reg.alterations[:4])}. Le registre ne s'écrit que par le hook ; relire les sources pour recréer des captures.")
    if reg.suppressions:
        c("REGISTRE_LECTURES_SUPPRESSION", "ALERTE", f"{len(reg.suppressions)} capture(s) inscrite(s) au registre puis supprimée(s) : {', '.join(reg.suppressions[:4])}.")
    cv = couverture(racine, texte, fiche, reg=reg)
    for d in cv["decisions"]:
        if not d["lue"]:
            c("DECISION_CITEE_NON_LUE", "BLOQUANT", f"Décision n° {d['numero']} (ligne {d['ligne']}) jamais lue dans le registre des lectures "
              f"(aucun get_decision capturé){' ; elle n’a été vue qu’en aperçu de recherche, qui ne vaut pas lecture' if d['vue_en_apercu'] else ''}. "
              "La lire en entier par LibreJustice avant de la citer.", numero=d["numero"])
        elif not d["suite_verifiee"]:
            c("DECISION_SUITE_INCONNUE", "ALERTE", f"Décision n° {d['numero']} : la source ne donne ni sa suite (standing) ni sa chronologie ; "
              "chercher une décision ultérieure par son numéro avant de s'y appuyer.", numero=d["numero"])
    for p in portee(racine, texte, fiche, reg=reg):
        suite = "; ".join(f"{s['valeur']}{' (' + s['titre'] + ')' if s.get('titre') else ''}" for s in p["suite"])
        if p["dit_dans_l_ecriture"]:
            c("DECISION_DEFAITE_SIGNALEE", "ALERTE", f"Décision n° {p['numero']} défaite par sa suite ({suite}) ; l'écriture le dit : vérifier que la "
              "décision n'est invoquée que pour ce qui subsiste.", numero=p["numero"])
        else:
            c("DECISION_CITEE_DEFAITE", "BLOQUANT", f"Décision n° {p['numero']} (ligne {p['ligne']}) citée alors que sa suite la défait : {suite}. "
              "Ne pas l'invoquer comme autorité, ou dire qu'elle a été annulée ou cassée et ce qui en subsiste.", numero=p["numero"])
    for a in cv["articles"]:
        nom = a["affichage"] + (f" ({a['instrument']})" if a["instrument"] else "")
        if not a["lu_a_la_date"]:
            if a["instrument"]:
                c("ARTICLE_NON_LU_A_DATE", "BLOQUANT", f"Article {nom} (ligne {a['lignes'][0]}) : "
                  + ("jamais lu dans le registre des lectures." if not a["lu"] else
                     f"lu seulement dans une version ({', '.join(a['versions_lues']) or 'section sans date'}) qui ne couvre pas la date utile "
                     f"({', '.join(a['dates'])}).") + " Le lire par get_norm avec as_of à la date utile.", article=a["article"])
            else:
                c("ARTICLE_NON_LU", "ALERTE", f"Article {a['affichage']} (ligne {a['lignes'][0]}) : texte non identifié dans l'écriture et aucune lecture "
                  "capturée de cet article ; nommer le code ou la loi, et le lire à la date utile.", article=a["article"])
            continue
        if not a["date_declaree"] and a["versions_connues"] > 1:
            c("DATE_UTILE_NON_DECLAREE", "ALERTE", f"Article {nom} : {a['versions_connues']} versions connues et aucune date utile déclarée "
              "(fiche : dates_utiles ou date_droit_applicable) ; la version lue est admise par défaut.", article=a["article"])
        if not a["section_lue"]:
            c("ARTICLE_SECTION_NON_LUE", "ALERTE", f"Article {nom} : la section qui le contient n'a pas été lue ; les exceptions et dérogations voisines "
              f"n'ont pas été vues ({', '.join(a['section'][:1]) or 'adresse de section à prendre dans get_norm'}).", article=a["article"])
        if a["renvois_non_suivis"]:
            c("ARTICLE_RENVOIS_NON_SUIVIS", "ALERTE", f"Article {nom} : {len(a['renvois_non_suivis'])} renvoi(s) non suivi(s) : "
              f"{', '.join(a['renvois_non_suivis'][:8])}.", article=a["article"])
        if not a["jurisprudence_par_article"]:
            c("JURISPRUDENCE_PAR_ARTICLE_NON_CHERCHEE", "ALERTE", f"Article {nom} : aucune recherche search_decisions filtrée par legal_article "
              f"« {a['instrument'] or '<code>'}|{a['article'].upper()} » ; les décisions qui l'interprètent n'ont pas été ratissées.", article=a["article"])
    codes = {"inexacte": "CITATION_INTROUVABLE", "introuvable": "CITATION_INTROUVABLE", "apercu": "CITATION_APERCU",
             "mal_attribuee": "CITATION_MAL_ATTRIBUEE", "autre_version": "CITATION_AUTRE_VERSION", "exacte_sommaire": "CITATION_SOMMAIRE",
             "non_attribuee_introuvable": "CITATION_NON_ATTRIBUEE"}
    for x in verifier_citations(racine, texte, fiche, reg=reg):
        code = codes.get(x["statut"])
        if not code:
            continue
        cit = x["citation"][:120] + ("..." if len(x["citation"]) > 120 else "")
        detail = {"inexacte": f"la source porte « {x.get('texte_source', '')[:300]} »", "introuvable": x.get("detail", ""),
                  "apercu": "retrouvée seulement dans un aperçu de recherche, écrit par la machine : lire la décision et citer son texte",
                  "mal_attribuee": f"retrouvée dans {x.get('trouvee_dans')}, pas dans la source annoncée",
                  "autre_version": x.get("detail", ""), "exacte_sommaire": "retrouvée dans le sommaire ou l'analyse, pas dans les motifs : l'attribuer comme tel",
                  "non_attribuee_introuvable": "aucune source annoncée dans le paragraphe, et le passage ne se lit dans aucune lecture ni pièce"}[x["statut"]]
        c(code, "BLOQUANT" if x["statut"] in GRAVES_CITATION else "ALERTE",
          f"Citation l. {x['ligne']} « {cit} »{' attribuée à ' + x['source'] if x.get('source') else ''} : {x['statut'].replace('_', ' ')} ; {detail}.",
          ligne=x["ligne"])
    sources = {s.get("id"): s for s in (L.lire_json(racine / "etat/sources.json", {}) or {}).get("sources", []) if isinstance(s, dict)}
    utilisees = set()
    for bloc in ("conditions", "moyens", "actes_attaques"):
        for x in fiche.get(bloc) or []:
            if isinstance(x, dict):
                utilisees.update(str(s) for s in x.get("sources") or [])
    for sid in sorted(utilisees):
        s = sources.get(sid)
        if s and s.get("type") == "decision" and s.get("lu_en_entier") is True and s.get("numero") and reg.decision(str(s["numero"])) is None:
            c("SOURCE_DECLAREE_SANS_LECTURE", "ALERTE", f"Source {sid} (n° {s['numero']}) déclarée lue en entier dans etat/sources.json sans lecture "
              "capturée au registre : la déclaration n'est pas vérifiable.", source=sid)


# ---------------------------------------------------------------------------------------------------------------
# Fiches de lecture

def id_norme(code: str, art: str, date: str | None = None) -> str:
    return f"{slug(code)}__{cle_article(art)}" + (f"__{date}" if date else "")


def id_decision(num: str) -> str:
    return re.sub(r"[^0-9a-z]+", "-", str(num).lower()).strip("-")


def charger_schema() -> dict:
    return json.loads(FICHIER_SCHEMA.read_text(encoding="utf-8"))


def _reference(ref: str) -> tuple[str, str | None, str | None]:
    """(« norme », code, article) ou (« decision », numéro, None) depuis « code|article », une adresse ou un numéro."""
    r = str(ref).strip()
    if "|" in r:
        code, _, art = r.partition("|")
        return "norme", slug(code), cle_article(art)
    if "/norm/" in r:
        c = cible_lien(r)
        if c:
            return "norme", c[0], c[1]
    return "decision", r.split("/")[-1] if "/decision/" in r else r, None


def squelette(racine: Path, ref: str, date: str | None = None) -> dict:
    reg = Registre(racine)
    nature, a, b = _reference(ref)
    if nature == "norme":
        entrees = reg.entrees_article(a, b)
        art = next((x for x in entrees if x["mode"] == "article" and (not date or couvre(x, date, x["versions"]))), None) or (entrees[0] if entrees else {})
        liens = sorted({cible_lien(ch) for x in entrees if x["mode"] == "article" for ch in RE_LIEN_NORME.findall(x["texte"])} - {None})
        recherches = reg.recherches_par_article(a, b)
        vues = []
        for s in recherches:
            for h in s["hits"]:
                vues.append({"numero": ", ".join(h.get("docket_numbers") or []), "juridiction": h.get("seat") or "", "date": h.get("date") or "",
                             "publication": ", ".join(h.get("publication") or []), "apport": "", "lue": any(reg.decision(n) for n in h.get("docket_numbers") or [])})
        return {"schema": SCHEMA_FICHE, "id": id_norme(art.get("code") or a, b, date), "nature": "norme",
                "reference": art.get("titre") or f"{a}|{b}", "code": art.get("code") or a, "article": art.get("numero") or b,
                "lu_le": L.horodatage(), "lectures": sorted({x["lecture"] for x in entrees}),
                "version": {"date_utile": date or "", "valid_from": art.get("valid_from") or "", "valid_to": art.get("valid_to") or "",
                            "statut": art.get("statut") or "", "versions_connues": art.get("versions") or [], "disposition_transitoire": art.get("note") or ""},
                "lettre": [{"alinea": "", "extrait": ""}], "champ_application": "",
                "conditions": {"articulation": "", "liste": [{"id": "C1", "enonce": "", "extrait": ""}]},
                "exceptions": {"section_lue": art.get("section", "") if art.get("section") in reg.sections_lues else "", "liste": []},
                "renvois": [{"article": f"{c}|{x}", "suivi": reg.article_lu(c, x), "objet": ""} for c, x in liens if x != b],
                "effets": "", "interpretation": {"recherches": [s["lecture"] for s in recherches], "decisions": vues},
                "portee_limites": "", "non_lu": []}
    d = reg.decision(a) or {}
    return {"schema": SCHEMA_FICHE, "id": id_decision(a), "nature": "decision", "reference": d.get("titre") or a, "numero": a,
            "juridiction": d.get("siege") or "", "formation": ", ".join(d.get("formation") or []), "date": d.get("date") or "",
            "publication": ", ".join(d.get("publication") or []), "lu_le": L.horodatage(), "lectures": [d["lecture"]] if d else [],
            "question": "", "motif_decisif": {"point": "", "extrait": ""}, "solution": d.get("ruling") or "",
            "portee": {"nature": "", "raisons": ""}, "limites": "",
            "suite": {"standing": d.get("standing") or "", "chronologie": [f"{x.get('title')} : {x.get('ruling')}" for x in d.get("chronologie") or [] if isinstance(x, dict)],
                      "decisions_contraires": []},
            "commentaires": [{"nature": x.get("kind", ""), "titre": x.get("title") or x.get("publisher") or "", "url": x.get("url", ""), "lu": False}
                             for x in d.get("commentaires") or [] if isinstance(x, dict)],
            "non_lu": []}


def valider_fiche(racine: Path, ident: str, fiche: dict | None = None, reg: Registre | None = None) -> tuple[list[str], list[str]]:
    """Erreurs (bloquantes) et alertes d'une fiche recherche/fiches/<id>.json."""
    import pieces as P
    nom = f"{FICHES.as_posix()}/{ident}.json"
    fiche = fiche if fiche is not None else L.lire_json(racine / FICHES / f"{ident}.json")
    if not isinstance(fiche, dict):
        return [f"{nom} absent ou illisible."], []
    schema = charger_schema()
    nature = fiche.get("nature")
    if nature not in ("norme", "decision"):
        return [f"{nom} : nature « {nature} » inconnue (norme, decision)."], []
    erreurs = [f"{nom} : {e}" for e in P.valider_schema(fiche, schema["$defs"][nature], schema)]
    alertes: list[str] = []
    if fiche.get("id") != ident:
        erreurs.append(f"{nom} : id « {fiche.get('id')} » différent du nom du fichier.")
    quand = L.parse_date(str(fiche.get("lu_le") or "").replace(" ", "T")[:16])
    if quand is not None and (quand - L.maintenant()).total_seconds() > 3600:
        erreurs.append(f"{nom} : lu_le est postérieur à l'horloge du dossier ; reprendre la date du squelette (lectures.py fiche).")
    reg = reg or Registre(racine)
    integres = {d["fichier"] for d in reg.lectures}
    for f in fiche.get("lectures") or []:
        if f not in integres:
            erreurs.append(f"{nom} : la lecture « {f} » n'est pas une capture intègre du registre.")
    if erreurs:
        return erreurs, alertes

    def extrait(chemin: str, ex: str, textes: list[str]) -> None:
        if ex and not any(P.trouver(ex, texte_source(t)) for t in textes):
            erreurs.append(f"{nom} : {chemin} « {ex[:100]} » ne se lit pas mot pour mot dans les lectures capturées de la source.")

    if nature == "norme":
        art, code = cle_article(fiche.get("article")), fiche.get("code")
        entrees = [x for x in reg.entrees_article(code, art) if x["lecture"] in set(fiche.get("lectures") or [])]
        if not entrees:
            erreurs.append(f"{nom} : aucune des lectures citées ne porte sur l'article {fiche.get('article')} ({code}).")
            return erreurs, alertes
        textes = [x["texte"] for x in entrees]
        if not any((l or {}).get("extrait") for l in fiche.get("lettre") or []):
            erreurs.append(f"{nom} : lettre sans aucun extrait verbatim.")
        for i, l in enumerate(fiche.get("lettre") or []):
            extrait(f"lettre[{i}].extrait", (l or {}).get("extrait", ""), textes)
        for i, k in enumerate((fiche.get("conditions") or {}).get("liste") or []):
            extrait(f"conditions.liste[{i}].extrait", (k or {}).get("extrait", ""), textes)
        for i, k in enumerate((fiche.get("exceptions") or {}).get("liste") or []):
            k = k or {}
            cible = cle_article(k.get("article")) if k.get("article") else art
            instr, _, _ = str(k.get("article") or "").rpartition("|")
            extrait(f"exceptions.liste[{i}].extrait", k.get("extrait", ""), [x["texte"] for x in reg.entrees_article(instr or code, cible.split("|")[-1])])
        v = fiche.get("version") or {}
        lues = {str(x.get("valid_from")) for x in entrees if x["mode"] == "article" and x.get("valid_from")}
        if lues and str(v.get("valid_from")) not in lues:
            erreurs.append(f"{nom} : version.valid_from « {v.get('valid_from')} » ne correspond à aucune version lue ({', '.join(sorted(lues))}).")
        if v.get("date_utile") and not any(couvre(x, str(v["date_utile"]), x["versions"]) for x in entrees):
            erreurs.append(f"{nom} : aucune lecture citée ne donne la version applicable à la date utile {v['date_utile']}.")
        for r in fiche.get("renvois") or []:
            instr, _, a = str((r or {}).get("article", "")).rpartition("|")
            if (r or {}).get("suivi") is True and not reg.article_lu(instr or None, cle_article(a)):
                erreurs.append(f"{nom} : renvoi {r.get('article')} déclaré suivi sans lecture capturée.")
            elif (r or {}).get("suivi") is not True:
                alertes.append(f"{nom} : renvoi {r.get('article')} non suivi.")
        sec = (fiche.get("exceptions") or {}).get("section_lue")
        if not sec:
            alertes.append(f"{nom} : section non lue ; les exceptions voisines ne sont pas établies.")
        elif chemin_url(sec) not in reg.sections_lues:
            erreurs.append(f"{nom} : exceptions.section_lue « {sec} » ne correspond à aucune section capturée.")
        if not (fiche.get("interpretation") or {}).get("recherches"):
            alertes.append(f"{nom} : aucune recherche par article (legal_article) citée ; l'interprétation jurisprudentielle n'est pas ratissée.")
        if (fiche.get("conditions") or {}).get("articulation") not in ("cumulatives", "alternatives", "mixtes", "condition_unique", "sans_condition"):
            erreurs.append(f"{nom} : conditions.articulation doit valoir cumulatives, alternatives, mixtes, condition_unique ou sans_condition.")
    else:
        d = next((x for x in reg.decisions.get(numero(fiche.get("numero")), []) if x["lecture"] in set(fiche.get("lectures") or [])), None)
        if d is None:
            erreurs.append(f"{nom} : aucune des lectures citées n'est la décision n° {fiche.get('numero')} lue par get_decision.")
            return erreurs, alertes
        md = fiche.get("motif_decisif") or {}
        if not md.get("extrait"):
            erreurs.append(f"{nom} : motif_decisif.extrait vide ; le motif décisif se recopie mot pour mot.")
        extrait("motif_decisif.extrait", md.get("extrait", ""), [d["texte"]])
        st = (fiche.get("suite") or {}).get("standing")
        if d["standing"] and st != d["standing"]:
            erreurs.append(f"{nom} : suite.standing « {st} » différent de la suite donnée par la source (« {d['standing']} »).")
        if suite_defavorable(d) and not (fiche.get("suite") or {}).get("decisions_contraires"):
            erreurs.append(f"{nom} : la source montre une suite qui défait la décision ({suite_defavorable(d)[0]['valeur']}) ; la porter dans suite.decisions_contraires.")
        if (fiche.get("portee") or {}).get("nature") not in ("principe", "espece"):
            erreurs.append(f"{nom} : portee.nature doit valoir principe ou espece.")
        if d["commentaires"] and not any((x or {}).get("lu") for x in fiche.get("commentaires") or []):
            alertes.append(f"{nom} : {len(d['commentaires'])} conclusion(s) ou rapport(s) signalé(s) par la source, aucun lu.")
    return erreurs, alertes


# ---------------------------------------------------------------------------------------------------------------
# Requêtes faites

def requetes(reg: Registre, vides: bool = False) -> list[str]:
    lignes = []
    for s in sorted(reg.recherches_decisions + reg.recherches_normes, key=lambda s: s["lecture"]):
        e = dict(s["entree"])
        q = e.pop("query", "")
        filtres = {k: v for k, v in e.items() if v not in (None, "", [], True) and k not in ("limit", "ai_rerank", "mode", "sort")}
        n = len(s["hits"])
        if vides and n:
            continue
        outil = "search_norms" if s in reg.recherches_normes else "search_decisions"
        lignes.append(f"{s['lecture']} {outil} « {q} » {json.dumps(filtres, ensure_ascii=False) if filtres else ''} -> {n} résultat(s)"
                      f"{' sur ' + str(s['total']) if s.get('total') is not None else ''}")
    return lignes


# ---------------------------------------------------------------------------------------------------------------
# Ligne de commande

def _cible(chemin: str) -> tuple[Path, Path, str, dict]:
    f = Path(chemin).resolve()
    racine = L.trouver_racine(f)
    if racine is None:
        raise SystemExit(f"{f} n'est pas dans un dossier d'affaire (etat/affaire.json introuvable).")
    fiche = L.lire_json(racine / "ecritures" / "controle" / f"{f.stem}.fiche.json", {}) or {}
    return f, racine, f.read_text(encoding="utf-8"), fiche


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = ap.add_subparsers(dest="cmd", required=True)
    k = s.add_parser("couverture")
    k.add_argument("fichier")
    k.add_argument("--date")
    k.add_argument("--json", action="store_true")
    k = s.add_parser("citations")
    k.add_argument("fichier")
    k.add_argument("--json", action="store_true")
    k = s.add_parser("portee")
    k.add_argument("fichier", nargs="?")
    k.add_argument("--json", action="store_true")
    k = s.add_parser("requetes")
    k.add_argument("--vides", action="store_true")
    k = s.add_parser("fiche")
    k.add_argument("reference")
    k.add_argument("--date")
    k = s.add_parser("verifier")
    k.add_argument("ids", nargs="*")
    s.add_parser("capturer")
    a = ap.parse_args(argv)
    if a.cmd == "capturer":
        sys.stdin.reconfigure(encoding="utf-8")
        ev = json.load(sys.stdin)
        racine = L.trouver_racine(ev.get("cwd") or os.getcwd())
        if racine is not None:
            capturer(racine, ev)
        return 0
    if a.cmd in ("couverture", "citations") or (a.cmd == "portee" and a.fichier):
        f, racine, texte, fiche = _cible(a.fichier)
        nom = L.relatif(racine, f) or f.name
        if a.cmd == "couverture":
            cv = couverture(racine, texte, fiche, a.date)
            print(json.dumps(cv, ensure_ascii=False, indent=2) if a.json else resume_couverture(cv, nom))
            return 1 if manques_couverture(cv) else 0
        if a.cmd == "citations":
            res = verifier_citations(racine, texte, fiche)
            print(json.dumps(res, ensure_ascii=False, indent=2) if a.json else resume_citations(res, nom))
            return 1 if any(x["statut"] in GRAVES_CITATION for x in res) else 0
        res = portee(racine, texte, fiche)
        if a.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(f"Décisions citées dans {nom} et défaites par leur suite : {len(res)}.")
            for p in res:
                print(f"- n° {p['numero']} ({p['titre']}) : " + "; ".join(f"{x['valeur']} {x.get('titre') or ''}".strip() for x in p["suite"])
                      + (" ; l'écriture le dit." if p["dit_dans_l_ecriture"] else " ; L'ÉCRITURE NE LE DIT PAS."))
        return 1 if any(not p["dit_dans_l_ecriture"] for p in res) else 0
    racine = L.trouver_racine(Path.cwd())
    if racine is None:
        raise SystemExit("Pas de dossier d'affaire ici (etat/affaire.json introuvable dans ce dossier ou ses parents).")
    reg = Registre(racine)
    if a.cmd == "portee":
        res = portee(racine, reg=reg)
        if a.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(f"Décisions lues dont la suite connue les défait : {len(res)}.")
            for p in res:
                print(f"- {p['titre']} : " + "; ".join(f"{x['valeur']} {x.get('titre') or ''}".strip() for x in p["suite"]))
        return 0
    if a.cmd == "requetes":
        lignes = requetes(reg, a.vides)
        print("\n".join(lignes) if lignes else "Aucune recherche capturée.")
        return 0
    if a.cmd == "fiche":
        print(json.dumps(squelette(racine, a.reference, a.date), ensure_ascii=False, indent=2))
        return 0
    if a.cmd == "verifier":
        ids = a.ids or sorted(p.stem for p in (racine / FICHES).glob("*.json"))
        total = 0
        for i in ids:
            erreurs, alertes = valider_fiche(racine, i, reg=reg)
            print(f"{i} : {len(erreurs)} erreur(s), {len(alertes)} alerte(s).")
            for e in erreurs:
                print(f"  ERREUR {e}")
            for x in alertes:
                print(f"  ALERTE {x}")
            total += len(erreurs)
        if reg.alterations:
            print("Registre altéré :\n  " + "\n  ".join(reg.alterations))
        return 1 if total or reg.alterations else 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
