"""Échéancier des registres du cabinet : contrats, sociétés, propriété intellectuelle, social, procédures.

Usage :
  python echeancier.py rapport [--horizon JOURS] [--registre NOM] [--au AAAA-MM-JJ] [--json]
  python echeancier.py squelette <contrats|societes|pi|social|procedures>
  python echeancier.py verifier

Les registres sont des listes JSON dans `<base>/registres/<nom>.json`. La base est `cabinet/` dans le dossier courant s'il existe,
sinon la variable HARNESS_JURIDIQUE_CONFIG, sinon `~/.harness-juridique/`. Chaque entrée a un `id`, un `objet` et, facultativement,
des `echeances` explicites ({"date", "nature", "action", "source", "fait"}). Certaines échéances se calculent depuis les champs de
l'entrée, selon une règle dont la source est citée ; tout autre délai s'inscrit en échéance explicite, avec sa source.
"""
from __future__ import annotations

import calendar
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

REGISTRES = ("contrats", "societes", "pi", "social", "procedures")

SQUELETTES = {
    "contrats": {"id": "", "objet": "", "contrepartie": "", "date_effet": "AAAA-MM-JJ", "duree_initiale_mois": 12,
                 "reconduction": "tacite | expresse | aucune", "duree_reconduction_mois": 12,
                 "preavis": {"valeur": 3, "unite": "mois | jours"}, "forme_preavis": "lettre recommandée avec avis de réception",
                 "echeances": []},
    "societes": {"id": "", "objet": "", "siren": "", "forme": "SA | SAS | SASU | SARL | EURL", "date_cloture": "AAAA-MM-JJ",
                 "date_approbation": "", "depot_electronique": True, "echeances": []},
    "pi": {"id": "", "objet": "", "type": "marque | brevet | dessin_modele | nom_de_domaine", "office": "INPI | EUIPO | OMPI | OEB",
           "numero": "", "date_depot": "AAAA-MM-JJ", "echeances": []},
    "social": {"id": "", "objet": "", "salarie": "initiales ou matricule, jamais le nom en clair", "echeances": []},
    "procedures": {"id": "", "objet": "", "juridiction": "", "numero": "", "echeances": []},
}


def base() -> Path:
    local = Path.cwd() / "cabinet"
    if local.is_dir():
        return local
    env = os.environ.get("HARNESS_JURIDIQUE_CONFIG")
    return Path(env) if env else Path.home() / ".harness-juridique"


def lire_date(s) -> date | None:
    try:
        return date.fromisoformat(str(s)[:10])
    except (TypeError, ValueError):
        return None


def ajouter_mois(d: date, n: int) -> date:
    m = d.month - 1 + n
    a, m = d.year + m // 12, m % 12 + 1
    return date(a, m, min(d.day, calendar.monthrange(a, m)[1]))


def _ech(d: date, nature: str, action: str, source: str, entree: dict, registre: str) -> dict:
    return {"date": d.isoformat(), "nature": nature, "action": action, "source": source, "registre": registre,
            "id": entree.get("id"), "objet": entree.get("objet")}


def calculees(registre: str, e: dict, au: date) -> list[dict]:
    """Échéances qui se déduisent des champs de l'entrée."""
    out: list[dict] = []
    if registre == "contrats":
        debut, n0 = lire_date(e.get("date_effet")), int(e.get("duree_initiale_mois") or 0)
        if debut and n0:
            fin, rec = ajouter_mois(debut, n0), str(e.get("reconduction") or "aucune")
            if rec.startswith("tacite"):
                pas = int(e.get("duree_reconduction_mois") or n0)
                while fin < au:
                    fin = ajouter_mois(fin, pas)
            src = "stipulations du contrat (durée, reconduction, préavis)"
            out.append(_ech(fin, "terme de la période en cours", "renouvellement ou fin du contrat", src, e, registre))
            p = e.get("preavis") or {}
            if p.get("valeur") and rec != "aucune":
                v = int(p["valeur"])
                limite = ajouter_mois(fin, -v) if str(p.get("unite", "mois")).startswith("mois") else fin - timedelta(days=v)
                out.append(_ech(limite, "date limite de dénonciation", f"dénoncer avant cette date ({e.get('forme_preavis') or 'forme du contrat'})"
                                + " pour éviter la reconduction", src, e, registre))
    elif registre == "societes":
        clot, forme = lire_date(e.get("date_cloture")), str(e.get("forme") or "").upper()
        if clot:
            sources = {"SA": "C. com., art. L. 225-100, I", "SARL": "C. com., art. L. 223-26", "EURL": "C. com., art. L. 223-26",
                       "SASU": "C. com., art. L. 227-9, al. 3",
                       "SAS": "C. com., art. L. 227-9, al. 2 (conditions statutaires) ; six mois retenus par prudence par analogie avec l'art. L. 225-100"}
            if forme in sources:
                out.append(_ech(ajouter_mois(clot, 6), "approbation des comptes", "réunir l'organe compétent et approuver les comptes"
                                + (" (prolongation possible par décision de justice)" if forme in ("SA", "SARL", "EURL") else ""),
                                sources[forme], e, registre))
                appro = lire_date(e.get("date_approbation")) or ajouter_mois(clot, 6)
                delai = 2 if e.get("depot_electronique", True) else 1
                src = "C. com., art. L. 232-22" if forme in ("SARL", "EURL") else "C. com., art. L. 232-23"
                out.append(_ech(ajouter_mois(appro, delai), "dépôt des comptes au greffe",
                                f"déposer les comptes ({delai} mois après l'approbation{', dépôt électronique' if delai == 2 else ''})", src, e, registre))
    elif registre == "pi" and str(e.get("type")) == "marque" and str(e.get("office") or "INPI").upper() == "INPI":
        dep = lire_date(e.get("date_depot"))
        if dep:
            exp = dep.replace(year=dep.year + 10) if not (dep.month == 2 and dep.day == 29) else date(dep.year + 10, 2, 28)
            while exp < au - timedelta(days=183):
                exp = exp.replace(year=exp.year + 10) if not (exp.month == 2 and exp.day == 29) else date(exp.year + 10, 2, 28)
            src = "CPI, art. L. 712-1 et R. 712-24 ; jour d'expiration à confirmer sur le registre de l'INPI"
            out.append({**_ech(exp - timedelta(days=365), "ouverture du renouvellement", "renouvellement possible pendant l'année qui précède l'expiration", src, e, registre), "information": True})
            out.append(_ech(exp, "expiration de l'enregistrement", "renouveler avant ce jour", src, e, registre))
            out.append(_ech(ajouter_mois(exp, 6), "fin du délai de grâce", "dernier jour pour renouveler, avec supplément de redevance", src, e, registre))
    return out


def charger(nom: str) -> list[dict]:
    p = base() / "registres" / f"{nom}.json"
    if not p.exists():
        return []
    d = json.loads(p.read_text(encoding="utf-8"))
    return d if isinstance(d, list) else d.get("entrees", [])


def rapport(au: date, horizon: int, registres=REGISTRES) -> dict:
    a_venir, depassees = [], []
    for r in registres:
        for e in charger(r):
            liste = calculees(r, e, au) + [{**x, "registre": r, "id": e.get("id"), "objet": e.get("objet")} for x in e.get("echeances") or []]
            for x in liste:
                d = lire_date(x.get("date"))
                if not d or x.get("fait"):
                    continue
                x["jours"] = (d - au).days
                if d < au:
                    if not x.get("information"):
                        depassees.append(x)
                elif x["jours"] <= horizon:
                    a_venir.append(x)
    cle = lambda x: x["date"]
    return {"au": au.isoformat(), "horizon": horizon, "base": str(base()), "depassees": sorted(depassees, key=cle), "a_venir": sorted(a_venir, key=cle)}


def verifier() -> list[str]:
    defauts = []
    for r in REGISTRES:
        try:
            entrees = charger(r)
        except (ValueError, OSError) as e:
            defauts.append(f"{r} : registre illisible ({e})")
            continue
        for e in entrees:
            if not e.get("id"):
                defauts.append(f"{r} : entrée sans id")
            for x in e.get("echeances") or []:
                if not lire_date(x.get("date")) or not x.get("nature"):
                    defauts.append(f"{r}/{e.get('id')} : échéance sans date valide ou sans nature : {x}")
                if not x.get("source"):
                    defauts.append(f"{r}/{e.get('id')} : échéance sans source : {x.get('nature')}")
    return defauts


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "squelette" and len(argv) > 1 and argv[1] in SQUELETTES:
        print(json.dumps(SQUELETTES[argv[1]], ensure_ascii=False, indent=2))
        return 0
    if argv[0] == "verifier":
        d = verifier()
        print("\n".join(d) if d else f"Registres conformes ({base()}).")
        return 1 if d else 0
    if argv[0] == "rapport":
        opt = lambda k, v: argv[argv.index(k) + 1] if k in argv else v
        au = lire_date(opt("--au", date.today().isoformat())) or date.today()
        regs = (opt("--registre", ""),) if "--registre" in argv else REGISTRES
        r = rapport(au, int(opt("--horizon", 90)), regs)
        if "--json" in argv:
            print(json.dumps(r, ensure_ascii=False, indent=1))
            return 0
        lignes = [f"Échéancier au {r['au']}, horizon {r['horizon']} jours, registres de {r['base']}."]
        for titre, cle in (("Dépassées", "depassees"), ("À venir", "a_venir")):
            lignes.append(f"{titre} : {len(r[cle])}")
            for x in r[cle]:
                lignes.append(f"- {x['date']} ({x['jours']:+d} j) [{x['registre']}] {x.get('objet') or x.get('id')} : {x['nature']}. {x.get('action') or ''} Source : {x.get('source')}.")
        print("\n".join(lignes))
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
