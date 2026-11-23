"""Fiche d'une société tirée des sources publiques : API Recherche d'entreprises (INSEE et RNE) et BODACC.

Usage :
  python registres_publics.py fiche <siren ou dénomination> [--json] [--annonces N]
  python registres_publics.py recherche <dénomination> [--json]

Sert à la vérification d'une contrepartie, à une diligence ou à la titularité d'un droit. Les requêtes partent vers des services
publics : n'y mettre que l'identité d'une personne morale ou d'un entrepreneur tiers, jamais le nom d'un client personne physique ni
une donnée de son dossier. La fiche dit la date de consultation et ses sources ; elle ne remplace pas un extrait Kbis ni l'état des
inscriptions, qui se demandent au greffe.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime

API_ENTREPRISES = "https://recherche-entreprises.api.gouv.fr/search"
API_BODACC = "https://bodacc-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/annonces-commerciales/records"
EN_TETES = {"User-Agent": "harness-juridique/1.0", "Accept": "application/json"}
# Catégories juridiques INSEE les plus fréquentes (nomenclature des catégories juridiques, niveau III).
FORMES = {"1000": "entrepreneur individuel", "5410": "SARL nationale", "5422": "SARL immobilière de gestion", "5426": "SARL immobilière",
          "5430": "SARL d'économie mixte", "5485": "société d'exercice libéral à responsabilité limitée", "5498": "SARL unipersonnelle",
          "5499": "SARL", "5505": "SA à participation ouvrière à conseil d'administration", "5510": "SA nationale à conseil d'administration",
          "5599": "SA à conseil d'administration", "5699": "SA à directoire", "5710": "SAS", "5720": "SAS à associé unique",
          "5785": "société d'exercice libéral par actions simplifiée", "6540": "société civile immobilière", "6599": "autre société civile",
          "9220": "association déclarée", "5202": "société en nom collectif", "5306": "société en commandite simple",
          "5308": "société en commandite par actions"}
ALERTES_BODACC = ("collective", "radiation")


def _get(url: str, params: dict) -> dict:
    req = urllib.request.Request(url + "?" + urllib.parse.urlencode(params), headers=EN_TETES)
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))


def rechercher(texte: str, n: int = 5) -> list[dict]:
    return _get(API_ENTREPRISES, {"q": texte, "per_page": n, "page": 1}).get("results") or []


def annonces_bodacc(siren: str, n: int = 15) -> tuple[int, list[dict]]:
    d = _get(API_BODACC, {"where": f'registre like "{siren}"', "limit": n, "order_by": "dateparution desc"})
    return int(d.get("total_count") or 0), d.get("results") or []


def _jugement(a: dict) -> str:
    j = a.get("jugement")
    if isinstance(j, str):
        try:
            j = json.loads(j)
        except ValueError:
            return j[:200]
    if isinstance(j, dict):
        return " ".join(str(j.get(k) or "") for k in ("nature", "date", "complementJugement")).strip()[:300]
    return ""


def fiche(identifiant: str, n_annonces: int = 15) -> dict:
    texte = re.sub(r"\s", "", identifiant) if re.fullmatch(r"[\d\s]{9,17}", identifiant) else identifiant
    resultats = rechercher(texte, 5)
    if not resultats:
        return {"trouve": False, "requete": identifiant, "consulte_le": datetime.now().strftime("%Y-%m-%d %H:%M")}
    r = resultats[0]
    siren = r.get("siren")
    total, annonces = annonces_bodacc(siren, n_annonces) if siren else (0, [])
    siege = r.get("siege") or {}
    comp = r.get("complements") or {}
    nature = str(r.get("nature_juridique") or "")
    return {
        "trouve": True,
        "consulte_le": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "ambiguite": [{"siren": x.get("siren"), "nom": x.get("nom_complet")} for x in resultats[1:]] if not re.fullmatch(r"\d{9,14}", texte) else [],
        "siren": siren,
        "denomination": r.get("nom_complet"),
        "forme": f"{FORMES.get(nature, 'catégorie juridique INSEE')} ({nature})",
        "date_creation": r.get("date_creation"),
        "etat": {"A": "active", "C": "cessée"}.get(r.get("etat_administratif"), r.get("etat_administratif")),
        "date_fermeture": r.get("date_fermeture"),
        "siege": {"adresse": siege.get("adresse"), "siret": siege.get("siret"), "date_creation": siege.get("date_creation")},
        "activite": {"naf": r.get("activite_principale"), "section": r.get("section_activite_principale")},
        "effectif": r.get("tranche_effectif_salarie"), "categorie": r.get("categorie_entreprise"),
        "conventions_collectives": comp.get("liste_idcc") or siege.get("liste_idcc") or [],
        "dirigeants": [{"qualite": d.get("qualite"),
                        "identite": d.get("denomination") or " ".join(x for x in (d.get("prenoms"), d.get("nom")) if x),
                        "type": d.get("type_dirigeant")} for d in r.get("dirigeants") or []],
        "finances": r.get("finances") or {},
        "qualites": sorted(k for k, v in comp.items() if k.startswith("est_") and v is True),
        "bodacc": {"total": total,
                   "alertes": [{"date": a.get("dateparution"), "famille": a.get("familleavis_lib"), "jugement": _jugement(a),
                                "tribunal": a.get("tribunal")} for a in annonces if a.get("familleavis") in ALERTES_BODACC],
                   "dernieres": [{"date": a.get("dateparution"), "famille": a.get("familleavis_lib"), "type": a.get("typeavis_lib"),
                                  "tribunal": a.get("tribunal"), "url": a.get("url_complete")} for a in annonces]},
        "sources": [f"{API_ENTREPRISES}?q={urllib.parse.quote(texte)}", f"{API_BODACC}?where=registre like \"{siren}\""],
    }


def imprimer(f: dict) -> str:
    if not f.get("trouve"):
        return f"Aucune entreprise trouvée pour « {f['requete']} » (consulté le {f['consulte_le']})."
    l = [f"{f['denomination']}, SIREN {f['siren']}, {f['forme']}, créée le {f['date_creation']}, {f['etat']}"
         + (f" depuis le {f['date_fermeture']}" if f.get("date_fermeture") else "") + ".",
         f"Siège : {f['siege']['adresse']} (SIRET {f['siege']['siret']}). Activité {f['activite']['naf']}, effectif {f['effectif']}, catégorie {f['categorie']}."]
    if f["conventions_collectives"]:
        l.append("Conventions collectives déclarées (IDCC) : " + ", ".join(map(str, f["conventions_collectives"])) + ".")
    if f["dirigeants"]:
        l.append("Dirigeants : " + " ; ".join(f"{d['qualite']} : {d['identite']}" for d in f["dirigeants"][:12]) + ".")
    if f["finances"]:
        l.append("Comptes publiés : " + " ; ".join(f"{a} : CA {v.get('ca')}, résultat {v.get('resultat_net')}" for a, v in sorted(f["finances"].items())) + ".")
    b = f["bodacc"]
    if b["alertes"]:
        l.append("ALERTE BODACC : " + " ; ".join(f"{a['date']} {a['famille']} {a['jugement']} ({a['tribunal']})" for a in b["alertes"]) + ".")
    l.append(f"BODACC : {b['total']} annonce(s) ; dernières : " + " ; ".join(f"{a['date']} {a['famille']}" for a in b["dernieres"][:8]) + ".")
    if f["ambiguite"]:
        l.append("Autres résultats de la recherche, à écarter ou à vérifier : " + " ; ".join(f"{a['nom']} ({a['siren']})" for a in f["ambiguite"]) + ".")
    l.append(f"Consulté le {f['consulte_le']} : API Recherche d'entreprises et BODACC. Un extrait Kbis et l'état des inscriptions se demandent au greffe.")
    return "\n".join(l)


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[0] not in ("fiche", "recherche"):
        print(__doc__)
        return 1
    en_json = "--json" in argv
    n = int(argv[argv.index("--annonces") + 1]) if "--annonces" in argv else 15
    mots = [a for i, a in enumerate(argv[1:], 1) if not a.startswith("--") and argv[i - 1] != "--annonces"]
    requete = " ".join(mots)
    try:
        if argv[0] == "recherche":
            res = [{"siren": r.get("siren"), "nom": r.get("nom_complet"), "commune": (r.get("siege") or {}).get("libelle_commune"),
                    "etat": r.get("etat_administratif")} for r in rechercher(requete, 10)]
            print(json.dumps(res, ensure_ascii=False, indent=1) if en_json else "\n".join(f"{x['siren']} {x['nom']} ({x['commune']}, {x['etat']})" for x in res))
            return 0
        f = fiche(requete, n)
    except OSError as e:
        print(f"Service public injoignable : {e}. Réessayer, ou consulter annuaire-entreprises.data.gouv.fr et bodacc.fr.")
        return 2
    print(json.dumps(f, ensure_ascii=False, indent=1) if en_json else imprimer(f))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
