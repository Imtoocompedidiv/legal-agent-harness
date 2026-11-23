"""Fiches de lecture doctrinale et académique : validation, contrôle d'une écriture qui cite des travaux.

Usage (depuis un dossier d'affaire) :
  python doctrine.py valider [fiche.json ...]     structure et règles des fiches de recherche/doctrine/
  python doctrine.py controle <brouillon>         constats que gate.py émettrait pour cette écriture
  python doctrine.py squelette                    structure vide d'une fiche, à remplir (skill recherche-doctrinale)

La structure est décrite par references/schemas/doctrine.v1.schema.json et validée par le validateur de pieces.py.
Ce module ajoute les règles qui croisent les champs et le contrôle des citations. Bibliothèque standard seulement,
aucun appel réseau.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib_affaire as L  # noqa: E402
import pieces as PIECES  # noqa: E402

DOSSIER = "recherche/doctrine"
SCHEMA = "doctrine.v1.schema.json"
LUS = ("texte_integral", "extraits")
TYPES_DECISION = ("conclusions_rapporteur_public", "avis_avocat_general", "rapport_conseiller", "commentaire_officiel")
IDENTIFIANTS = ("doi", "hal", "nnt", "ppn", "isbn", "numero_decision", "url")




# Une citation de moins de quatre mots est le plus souvent un terme ou une formule reçue : alerte seulement.
MOTS_CITATION = 4

# Marques d'une citation doctrinale dans une écriture. Chacune doit être couverte par le marqueur d'une fiche.
MARQUES = [
    ("DOI", re.compile(r"\b10\.\d{4,9}/[^\s»)\]]+")),
    ("identifiant HAL", re.compile(r"\b(?:hal|halshs|tel|hal-[a-z]+)-\d{8}\b")),
    ("numéro national de thèse", re.compile(r"\b(?:19|20)\d{2}[A-Z]{2,6}[A-Z0-9]{2,7}\b")),
    ("conclusions", re.compile(r"\bconcl\.|\bconclusions\s+(?:du|de\s+(?:son|notre|votre|la))\s+rapporteure?\s+publique?"
                               r"|\bconclusions\s+de\s+(?:M\.|Mme)\s*[\w'’ -]{2,40}?,\s*rapporteure?\s+publique?"
                               r"|\brapporteure?\s+publique?\s+(?:M\.|Mme)?\s*[A-ZÉ][\w'’-]+\s*,?\s*(?:dans\s+ses|en\s+ses|concl)", re.I)),
    ("avis ou rapport", re.compile(r"\bavis\s+(?:écrit\s+)?(?:de\s+l['’]|du\s+)(?:premier\s+)?avocat\s+général|\brapport\s+du\s+conseiller", re.I)),
    ("chronique ou note", re.compile(r"\bchron\.|\bnote\s+sous\b|\bobs\.\s+sous\b|\bop\.\s?cit\.|\bet\s+al\.", re.I)),
    ("thèse", re.compile(r"\bthèse\s+de\s+doctorat\b|\bth\.\s+dactyl", re.I)),
    ("revue", re.compile(r"\b(?:RFDA|AJDA|RDP|RJEP|RFDC|AJCT|RDSS|RDI|RDT|BJCL|LPA|RSC|Gaz\.\s?Pal\.|Dr\.\s?adm\.|Rev\.\s?crit\.|AJ\s?pénal|AJ\s?fam\.?"
                         r"|RTD\s?(?:civ|com|eur)\.?|JCP\s?[GAESN]?|D\.)\s?(?:19|20)\d{2}\b")),
]


def _k(code: str, message: str, gravite: str = "BLOQUANT") -> dict:
    return {"code": code, "gravite": gravite, "message": message}


def norm(t: str) -> str:
    """Forme de comparaison : compatibilité Unicode, apostrophes et espaces unifiés, casse ignorée."""
    t = unicodedata.normalize("NFKC", t or "")
    t = t.replace("’", "'").replace("‘", "'").replace(" ", " ").replace(" ", " ")
    t = re.sub(r"[‐‑‒–]", "-", t)
    return re.sub(r"\s+", " ", t).strip().casefold()


def _textes(v):
    if isinstance(v, dict):
        for x in v.values():
            yield from _textes(x)
    elif isinstance(v, list):
        for x in v:
            yield from _textes(x)
    elif isinstance(v, str):
        yield v


def _vide(x) -> bool:
    return not (isinstance(x, str) and x.strip())


def valider(doc, nom: str | None = None) -> list[dict]:
    """Constats de structure et de fond sur une fiche ; liste vide si elle est exploitable. `nom` : nom du fichier sans .json."""
    if not isinstance(doc, dict):
        return [_k("DOCTRINE_INVALIDE", "La fiche doit contenir un objet JSON.")]
    schema = PIECES.charger_schema(SCHEMA)
    out = [_k("DOCTRINE_INVALIDE", e) for e in PIECES.valider_schema(doc, schema, schema)]
    if out:
        return out
    ref, lec, sol, usage = doc["reference"], doc["lecture"], doc["solidite"], doc["usage"]
    ids = ref["identifiants"]
    if nom is not None and doc["id"] != nom:
        out.append(_k("DOCTRINE_ID", f"L'identifiant « {doc['id']} » diffère du nom du fichier « {nom}.json »."))
    if not any(not _vide(ids.get(k)) for k in IDENTIFIANTS):
        out.append(_k("DOCTRINE_SANS_IDENTIFIANT", "Référence sans identifiant vérifiable : DOI, HAL, NNT, PPN, ISBN, numéro de la décision "
                      "commentée ou adresse officielle."))
    if doc["type"] == "these" and _vide(ids.get("nnt")) and _vide(ids.get("ppn")):
        out.append(_k("DOCTRINE_THESE_SANS_NNT", "Thèse sans numéro national (theses.fr) ni PPN (SUDOC) : la référence n'est pas vérifiée."))
    if doc["type"] in TYPES_DECISION and _vide(ids.get("numero_decision")):
        out.append(_k("DOCTRINE_SANS_DECISION", "Conclusions, avis, rapport ou commentaire officiel sans le numéro de la décision qu'ils accompagnent."))
    lu = lec["statut"] in LUS
    if doc.get("passages") and not lu:
        out.append(_k("DOCTRINE_PASSAGE_NON_LU", f"Lecture « {lec['statut']} » : aucun passage ne se relève mot pour mot d'un texte non lu. "
                      "Retirer les passages ou lire le texte."))
    if lec["statut"] == "extraits" and _vide(lec.get("parties_lues")):
        out.append(_k("DOCTRINE_EXTRAITS_NON_PRECISES", "Lecture par extraits : dire lesquels (pages, sections) dans lecture.parties_lues."))
    if lec["statut"] != "texte_integral" and _vide(lec.get("obstacle")):
        out.append(_k("DOCTRINE_OBSTACLE_NON_DIT", "Texte intégral non lu : dire pourquoi dans lecture.obstacle (non diffusé, payant, accès restreint, "
                      "temps), pour que la lecture partielle soit connue de tous."))
    if ref["statut_publication"] in ("prepublication", "document_de_travail"):
        vp = ref.get("version_publiee") or {}
        if vp.get("recherchee") is not True:
            out.append(_k("DOCTRINE_VERSION_PUBLIEE", "Prépublication ou document de travail : chercher la version publiée (titre et auteurs, puis "
                          "auteurs seuls, le titre change souvent) et l'écrire dans reference.version_publiee."))
    empirique = doc["type"] == "etude_empirique" or usage["nature"] == "donnee_empirique" or sol["niveau"].startswith("empirique")
    if empirique:
        manquants = [k for k in ("methode", "population", "periode", "replication", "limites") if _vide(sol.get(k))]
        if manquants:
            out.append(_k("DOCTRINE_EMPIRIQUE_INCOMPLETE", f"Donnée empirique sans {', '.join(manquants)} : une donnée se cite avec sa population, "
                          "sa période, sa méthode, sa réplication et ses limites."))
    if (doc["type"] == "expertise_technique" or usage["nature"] == "expertise_technique") and _vide(usage.get("voie_probatoire")):
        out.append(_k("DOCTRINE_EXPERTISE_SANS_VOIE", "Expertise technique sans voie probatoire (expertise ou consultation ordonnée, avis technique, "
                      "consultation produite en pièce) : la littérature prépare la preuve, elle ne la remplace pas."))
    for m in doc["marqueurs"]:
        if len(m.strip()) < 4:
            out.append(_k("DOCTRINE_MARQUEUR_COURT", f"Marqueur « {m} » trop court pour repérer la citation dans une écriture."))
    return out


def lire_fiches(racine: Path) -> dict[str, tuple[dict | None, list[dict]]]:
    """Toutes les fiches de recherche/doctrine/ (sans les sous-dossiers) : identifiant -> (fiche ou None, constats)."""
    res = {}
    d = racine / DOSSIER
    for f in sorted(d.glob("*.json")) if d.is_dir() else []:
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            res[f.stem] = (None, [_k("DOCTRINE_INVALIDE", f"{f.name} illisible : {e}")])
            continue
        res[f.stem] = (doc, valider(doc, f.stem))
    return res


def _masquer_citations(texte: str) -> str:
    """Même longueur, contenu des guillemets remplacé par des espaces : les points cités ne coupent pas les phrases."""
    t = re.sub(r"«[^»]{0,4000}»", lambda m: "«" + " " * (len(m.group(0)) - 2) + "»", texte)
    t = re.sub(r"“[^”]{0,2000}”", lambda m: "“" + " " * (len(m.group(0)) - 2) + "”", t)
    return re.sub(r"\"[^\"\n]{0,1200}\"", lambda m: "\"" + " " * (len(m.group(0)) - 2) + "\"", t)


ABREVIATIONS = {"m.", "mm.", "p.", "pp.", "n°", "art.", "cf.", "concl.", "chron.", "obs.", "éd.", "ed.", "t.", "vol.", "al.", "cit.", "op.",
                "v.", "spéc.", "préc.", "s.", "ss.", "coll.", "dir.", "th.", "comm.", "rec.", "leb.", "sect.", "ass.", "req.", "civ.", "crim.",
                "soc.", "com.", "ch.", "ord.", "réf.", "dr.", "rev.", "gaz.", "pal.", "adm.", "d.", "et al.", "not.", "ibid.", "id."}


def phrases(texte: str) -> list[tuple[int, int]]:
    """Bornes des phrases de l'écriture, guillemets compris, coupées aussi aux lignes vides. Les abréviations des références
    (M., p., n°, concl., chron., initiales) ne coupent pas une phrase."""
    masque = _masquer_citations(texte)
    bornes, debut = [], 0
    for m in re.finditer(r"(?<=[.!?])\s+(?=[«\"“(\[A-ZÀ-ÖØ-Þ0-9])|\n\s*\n", masque):
        if not m.group(0).count("\n") >= 2:
            mot = (re.search(r"(\S+)$", masque[:m.start()]) or [""])[0].lstrip("([«\"“'")
            if mot.lower() in ABREVIATIONS or re.fullmatch(r"[A-ZÀ-ÖØ-Þ][a-zà-ÿ]?\.", mot) or masque[:m.start()].lower().endswith("et al."):
                continue
        bornes.append((debut, m.start()))
        debut = m.end()
    bornes.append((debut, len(texte)))
    return [b for b in bornes if texte[b[0]:b[1]].strip()]


def citations(texte: str, debut: int, fin: int) -> list[str]:
    """Passages entre guillemets français, anglais ou droits d'un segment de l'écriture."""
    rx = r"«\s*([^»]{1,4000}?)\s*»|“([^”]{1,2000})”|\"([^\"\n]{1,1200})\""
    return [(m.group(1) or m.group(2) or m.group(3)).strip() for m in re.finditer(rx, texte[debut:fin])]


def _passages_registre(racine: Path) -> list[str]:
    """Passages exacts du registre des sources (textes et décisions lus) : une citation qui s'y trouve n'est pas doctrinale."""
    reg = L.lire_json(racine / "etat/sources.json", {}) or {}
    out = []
    for s in reg.get("sources", []) if isinstance(reg, dict) else []:
        for p in (s.get("passages") or []) if isinstance(s, dict) else []:
            if isinstance(p, str):
                out.append(norm(p))
            elif isinstance(p, dict):
                out += [norm(str(p[k])) for k in ("citation", "texte", "extrait") if p.get(k)]
    return out


def _ligne(texte: str, pos: int) -> int:
    return texte.count("\n", 0, pos) + 1


def controler(racine: Path, ecriture: Path, fiche: dict | None, c, juridictionnel: bool = True) -> None:
    """Contrôle d'une écriture : chaque travail cité a sa fiche valide ; aucune citation entre guillemets d'un travail non lu ;
    aucune règle fondée sur la seule doctrine. `c(code, gravite, message, **extra)` au format de gate.py."""
    texte = ecriture.read_text(encoding="utf-8")
    fiche = fiche or {}
    g = "BLOQUANT" if juridictionnel else "ALERTE"
    fiches = lire_fiches(racine)
    t_norm = norm(texte)

    for did in fiche.get("doctrine", []) or []:
        if did not in fiches:
            c("DOCTRINE_SANS_FICHE", g, f"Travail « {did} » déclaré dans la fiche de l'acte sans fiche {DOSSIER}/{did}.json (skill recherche-doctrinale).")

    # Travaux cités : ceux dont un marqueur figure dans le texte, et ceux que la fiche de l'acte déclare.
    cites = {}
    for did, (doc, constats) in fiches.items():
        marqueurs = [m for m in ((doc or {}).get("marqueurs") or []) if isinstance(m, str) and len(m.strip()) >= 4]
        if any(norm(m) in t_norm for m in marqueurs) or did in (fiche.get("doctrine") or []):
            cites[did] = (doc, constats, marqueurs)
    for did, (doc, constats, _) in cites.items():
        bloq = [k for k in constats if k["gravite"] == "BLOQUANT"]
        if bloq:
            c("DOCTRINE_FICHE_INVALIDE", g, f"Fiche {did} citée mais invalide : " + " ; ".join(f"{k['code']} {k['message']}" for k in bloq[:4]))

    bornes = phrases(texte)

    def couvert(debut: int, fin: int) -> list[str]:
        seg = norm(texte[debut:fin])
        return [did for did, (_, _, ms) in cites.items() if any(norm(m) in seg for m in ms)]

    # Marques de citation doctrinale sans fiche qui les couvre dans la même phrase.
    vues = set()
    for nom, rx in MARQUES:
        for m in rx.finditer(texte):
            b = next(((d, f) for d, f in bornes if d <= m.start() < f), (m.start(), m.end()))
            if b in vues or couvert(*b):
                continue
            vues.add(b)
            c("DOCTRINE_HORS_FICHE", g, f"Citation doctrinale ({nom}, « {m.group(0)[:60]} ») sans fiche de lecture qui la couvre dans la même phrase : "
              f"écrire {DOSSIER}/<id>.json et y porter le marqueur tel qu'il figure dans l'écriture.", ligne=_ligne(texte, m.start()))

    # Citations entre guillemets dans une phrase qui cite un travail.
    registre = None
    for d, f in bornes:
        dids = couvert(d, f)
        if not dids:
            continue
        for q in citations(texte, d, f):
            qn = norm(q)
            if not qn:
                continue
            docs = [cites[x][0] or {} for x in dids]
            lus = [x for x in docs if (x.get("lecture") or {}).get("statut") in LUS]
            if any(qn in norm(p.get("texte", "")) for x in lus for p in (x.get("passages") or []) if isinstance(p, dict)):
                continue
            if registre is None:
                registre = _passages_registre(racine)
            if any(qn in p for p in registre):
                continue
            court = len(qn.split()) < MOTS_CITATION
            if not lus:
                statuts = ", ".join(sorted({(x.get("lecture") or {}).get("statut", "?") for x in docs}))
                c("DOCTRINE_CITATION_NON_LUE", "ALERTE" if court else g,
                  f"Citation « {q[:80]} » attribuée à {', '.join(dids)}, dont le texte n'a pas été lu ({statuts}) : reformuler sans guillemets "
                  "en disant ce qui a été lu, ou lire le texte.", ligne=_ligne(texte, d))
            else:
                c("DOCTRINE_CITATION_INTROUVABLE", "ALERTE" if court else g,
                  f"Citation « {q[:80]} » absente des passages relevés mot pour mot dans {', '.join(dids)} et du registre des sources : "
                  "la relever avec sa page dans la fiche, ou la corriger.", ligne=_ligne(texte, d))

    # Version de travail citée alors qu'une version publiée est connue.
    for did, (doc, _, _) in cites.items():
        ref = (doc or {}).get("reference") or {}
        if ref.get("statut_publication") in ("prepublication", "document_de_travail") and not _vide((ref.get("version_publiee") or {}).get("reference")):
            c("DOCTRINE_VERSION_DE_TRAVAIL_CITEE", "ALERTE", f"{did} est une version de travail alors qu'une version publiée existe : citer la version "
              "publiée, après avoir vérifié que le résultat repris y figure.")

    # Données empiriques : fragilité signalée, période dite dans la phrase qui les cite.
    for did, (doc, _, ms) in cites.items():
        sol = (doc or {}).get("solidite") or {}
        if not str(sol.get("niveau", "")).startswith("empirique") and (doc or {}).get("type") != "etude_empirique":
            continue
        if sol.get("niveau") in ("empirique_limite", "conteste"):
            c("DOCTRINE_EMPIRIQUE_FRAGILE", "ALERTE", f"Donnée empirique {did} de solidité « {sol.get('niveau')} » : l'écriture la présente "
              "comme un élément de fait, avec sa population et sa limite, jamais comme une loi générale.")
        annees = set(re.findall(r"\b(?:19|20)\d{2}\b", str(sol.get("periode", ""))))
        if annees:
            for d, f in bornes:
                seg = texte[d:f]
                if any(norm(m) in norm(seg) for m in ms) and not any(a in seg for a in annees):
                    c("DOCTRINE_EMPIRIQUE_SANS_POPULATION", "ALERTE", f"La phrase qui cite {did} ne donne pas la période étudiée "
                      f"({sol.get('periode')}) : dire la population et la période avec la donnée.", ligne=_ligne(texte, d))
                    break

    # Une opinion doctrinale ne vaut pas règle : un moyen ou une condition ne repose pas sur la seule doctrine.
    reg = L.lire_json(racine / "etat/sources.json", {}) or {}
    types = {s.get("id"): s.get("type") for s in reg.get("sources", []) if isinstance(s, dict)} if isinstance(reg, dict) else {}
    for col, cle in (("moyens", "intitule"), ("conditions", "condition")):
        for x in fiche.get(col, []) or []:
            srcs = [s for s in (x.get("sources") or []) if s in types]
            if srcs and all(types[s] == "doctrine" for s in srcs):
                c("DOCTRINE_SEULE_POUR_REGLE", g, f"{col[:-1].capitalize()} « {x.get(cle, '?')} » ne repose que sur de la doctrine : une opinion "
                  "doctrinale éclaire la portée d'une règle, elle n'en tient pas lieu. Rattacher le texte ou la décision lus.")


def squelette() -> dict:
    return {
        "schema": "doctrine/1", "id": "", "date": "", "question": "", "type": "", "discipline": "",
        "reference": {"auteurs": [{"nom": "", "prenom": "", "qualite": ""}], "titre": "", "annee": 0, "support": "", "volume": "", "numero": "",
                      "pages": "", "identifiants": {"doi": "", "hal": "", "nnt": "", "ppn": "", "isbn": "", "numero_decision": "", "url": ""},
                      "verifiee_par": [""], "statut_publication": "", "version_lue": "",
                      "version_publiee": {"recherchee": False, "constat": "", "reference": ""}},
        "lecture": {"statut": "", "lu_le": "", "acces": "", "source_lue": "", "parties_lues": "", "obstacle": ""},
        "these_de_l_auteur": "", "apports": [], "passages": [{"texte": "", "page": "", "contexte": ""}],
        "solidite": {"niveau": "", "autorite": "", "date_et_actualite": "", "reception": "", "methode": "", "population": "", "periode": "",
                     "taille": "", "replication": "", "limites": ""},
        "usage": {"nature": "", "proposition": "", "limite": "", "ecritures": [], "voie_probatoire": ""},
        "marqueurs": [""], "contre": [],
    }


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    v = s.add_parser("valider")
    v.add_argument("fiches", nargs="*")
    k = s.add_parser("controle")
    k.add_argument("ecriture")
    k.add_argument("--non-juridictionnel", action="store_true")
    s.add_parser("squelette")
    a = p.parse_args(argv)
    if a.cmd == "squelette":
        print(json.dumps(squelette(), ensure_ascii=False, indent=2))
        return 0
    if a.cmd == "valider":
        if a.fiches:
            res = {}
            for f in map(Path, a.fiches):
                try:
                    res[f.stem] = valider(json.loads(f.read_text(encoding="utf-8")), f.stem)
                except (OSError, json.JSONDecodeError) as e:
                    res[f.stem] = [_k("DOCTRINE_INVALIDE", f"{f} illisible : {e}")]
        else:
            racine = L.trouver_racine(Path.cwd()) or Path.cwd()
            res = {did: constats for did, (_, constats) in lire_fiches(racine).items()}
        bloquants = 0
        for did, constats in res.items():
            print(f"{did} : {'valide' if not constats else ''}")
            for x in constats:
                print(f"  {x['gravite']} {x['code']} : {x['message']}")
                bloquants += x["gravite"] == "BLOQUANT"
        if not res:
            print(f"Aucune fiche dans {DOSSIER}/.")
        return 1 if bloquants else 0
    ecriture = Path(a.ecriture).resolve()
    racine = L.trouver_racine(ecriture)
    if racine is None:
        print(f"{ecriture} n'est pas dans un dossier d'affaire (etat/affaire.json introuvable).")
        return 2
    fiche = L.lire_json(racine / "ecritures" / "controle" / f"{ecriture.stem}.fiche.json")
    constats = []
    controler(racine, ecriture, fiche, lambda code, gravite, message, **x: constats.append({"code": code, "gravite": gravite, "message": message, **x}),
              juridictionnel=not a.non_juridictionnel)
    for x in constats:
        print(f"{x['gravite']} {x['code']}{' (ligne ' + str(x['ligne']) + ')' if x.get('ligne') else ''} : {x['message']}")
    if not constats:
        print("Aucun constat doctrinal.")
    return 1 if any(x["gravite"] == "BLOQUANT" for x in constats) else 0


if __name__ == "__main__":
    sys.exit(main())
