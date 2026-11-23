"""Carte des voies et délais calculée depuis la chronologie typée du dossier.

Usage : python voies.py [--inscrire]

Chaque événement de chronologie/chronologie.json peut porter un champ `type` et ses attributs :
  demande_admin            reception (date), regime_silence (rejet|acceptation), accuse_reception_conforme (bool)
  decision_admin           notification (date), voies_delais_mentionnes (bool)
  ordonnance_refere_admin  notification, fondement (L521-1|L521-2|L521-3), instruite (bool), rejet_faute_moyen_serieux (bool)
  jugement_ta              notification
  decision_dernier_ressort notification (arrêt de CAA, jugement rendu en dernier ressort)
  ordonnance_refere_civil  signification
  jugement_civil           signification
  arret_ca                 signification

Les dates produites sont des scénarios : chaque règle cite son texte, à relire dans sa version applicable,
et le point de départ doit être prouvé par une pièce. `--inscrire` ajoute les échéances absentes à
etat/echeances.json avec la certitude « scenario ».
"""
from __future__ import annotations

import argparse
import calendar
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib_affaire as L  # noqa: E402


def paques(annee: int) -> date:
    a, b, c = annee % 19, annee // 100, annee % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l_ = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l_) // 451
    mois = (h + l_ - 7 * m + 114) // 31
    jour = ((h + l_ - 7 * m + 114) % 31) + 1
    return date(annee, mois, jour)


def feries(annee: int) -> set[date]:
    p = paques(annee)
    fixes = [(1, 1), (5, 1), (5, 8), (7, 14), (8, 15), (11, 1), (11, 11), (12, 25)]
    return {date(annee, m, j) for m, j in fixes} | {p + timedelta(days=1), p + timedelta(days=39), p + timedelta(days=50)}


def ouvrable(d: date) -> date:
    while d.weekday() >= 5 or d in feries(d.year):
        d += timedelta(days=1)
    return d


def plus_mois(d: date, n: int) -> date:
    m = d.month - 1 + n
    a, m = d.year + m // 12, m % 12 + 1
    return date(a, m, min(d.day, calendar.monthrange(a, m)[1]))


def echeance(depart: date, mois: int = 0, jours: int = 0, franc: bool = False, report: bool = True) -> date:
    """Fin du délai. Le report au premier jour ouvrable (CPC, art. 642) vaut pour les délais
    de procédure ; une prescription ou une forclusion de fond se calcule sans report, date prudente."""
    fin = plus_mois(depart, mois) + timedelta(days=jours)
    if franc:
        fin += timedelta(days=1)
    return ouvrable(fin) if report else fin


REGLES = [
    # (type, condition, libellé, mois, jours, franc, texte, effet)
    ("demande_admin", lambda e: e.get("regime_silence") == "rejet", "Naissance de la décision implicite de rejet", 2, 0, False,
     "CRPA, art. L. 231-4 et textes spéciaux ; CJA, art. R. 421-2", "la décision attaquable naît ; demander les motifs (CRPA, L. 232-4) dans le délai de recours"),
    ("demande_admin", lambda e: e.get("regime_silence") == "acceptation", "Naissance de la décision implicite d'acceptation", 2, 0, False,
     "CRPA, art. L. 231-1 et L. 232-3", "demander l'attestation de décision implicite ; vérifier les exceptions au principe"),
    ("demande_admin", lambda e: e.get("regime_silence") == "rejet" and e.get("accuse_reception_conforme") is True,
     "Fin du délai de recours contre le rejet implicite", 4, 0, True, "CJA, art. R. 421-2 ; CRPA, art. L. 112-3 et L. 112-6",
     "au-delà, recours tardif ; sans accusé de réception conforme, délai non opposable"),
    ("decision_admin", lambda e: e.get("voies_delais_mentionnes") is not False, "Fin du délai de recours contentieux", 2, 0, True,
     "CJA, art. R. 421-1 et R. 421-5 ; CRPA, art. L. 411-2 (prorogation par recours administratif)", "recours pour excès de pouvoir et référé-suspension avec lui"),
    ("decision_admin", lambda e: e.get("voies_delais_mentionnes") is False, "Délai raisonnable de recours, à défaut de mention des voies et délais", 12, 0, False,
     "CE, Ass., 13 juillet 2016, Czabaj, n° 387763 (à relire)", "point de départ : connaissance acquise de la décision"),
    ("ordonnance_refere_admin", lambda e: e.get("fondement") in ("L521-1", "L521-3") or e.get("instruite") is False,
     "Fin du délai de pourvoi en cassation contre l'ordonnance", 0, 15, True, "CJA, art. L. 523-1 et R. 523-1 ; avocat aux Conseils",
     "ordonnance en dernier ressort ; une nouvelle ordonnance de rejet sur une demande de même objet prive d'objet le pourvoi (CE, Sect., 22 sept. 2023, n° 472210)"),
    ("ordonnance_refere_admin", lambda e: e.get("fondement") == "L521-2" and e.get("instruite") is True,
     "Fin du délai d'appel devant le juge des référés du Conseil d'État", 0, 15, True, "CJA, art. L. 523-1, al. 2", "appel jugé dans les quarante-huit heures"),
    ("ordonnance_refere_admin", lambda e: e.get("fondement") == "L521-1" and e.get("rejet_faute_moyen_serieux") is True,
     "Confirmation du maintien de la requête au fond", 1, 0, False, "CJA, art. R. 612-5-2", "à défaut, désistement réputé de la requête au fond"),
    ("jugement_ta", lambda e: True, "Fin du délai d'appel", 2, 0, True, "CJA, art. R. 811-2", "appel devant la cour administrative d'appel"),
    ("decision_dernier_ressort", lambda e: True, "Fin du délai de pourvoi en cassation", 2, 0, True, "CJA, art. R. 821-1 ; avocat aux Conseils", "procédure d'admission (L. 822-1)"),
    ("ordonnance_refere_civil", lambda e: True, "Fin du délai d'appel de l'ordonnance de référé", 0, 15, False, "CPC, art. 490, 640 à 642", "appel"),
    ("jugement_civil", lambda e: True, "Fin du délai d'appel (matière contentieuse)", 1, 0, False, "CPC, art. 538, 640 à 642", "délais de distance à ajouter le cas échéant (art. 643)"),
    ("arret_ca", lambda e: True, "Fin du délai de pourvoi en cassation", 2, 0, False, "CPC, art. 612, 640 à 642 ; avocat aux Conseils", "mémoire ampliatif dans le délai de l'art. 978"),
]


def regles_domaines() -> list[dict]:
    """Règles de délai vérifiées livrées par domaine (references/domaines/*_voies.json)."""
    import json
    res = []
    dossier = Path(__file__).resolve().parents[1] / "references" / "domaines"
    for f in sorted(dossier.glob("*_voies.json")) if dossier.is_dir() else []:
        try:
            entrees = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        res.extend(e for e in (entrees if isinstance(entrees, list) else []) if e.get("type") and e.get("libelle"))
    return res


def calculer_evenement(e: dict) -> list[dict]:
    """Délais que fait courir un événement typé de la chronologie (règles intégrées et règles de domaine)."""
    res = []
    t = e.get("type")
    for (typ, cond, lib, mois, jours, franc, texte, effet) in REGLES:
        if t != typ or not cond(e):
            continue
        depart = L.date_simple(e.get("reception") or e.get("notification") or e.get("signification") or e.get("date"))
        if depart is None:
            continue
        # La date retenue est toujours la date prudente, sans le jour franc ; la date franche est indiquée à côté.
        fin = echeance(depart, mois, jours, False)
        fin_franc = echeance(depart, mois, jours, True) if franc else None
        res.append({"objet": f"{lib} ({e.get('fait', '')[:70]})", "libelle": lib, "date": fin.isoformat(),
                    "date_si_delai_franc": fin_franc.isoformat() if fin_franc else None, "regle": texte, "effet": effet,
                    "point_de_depart": f"{depart.isoformat()} ({'réception' if e.get('reception') else 'notification ou signification'}), pièces {e.get('pieces', [])}",
                    "franc": franc})
    for r in regles_domaines():
        if t != r["type"] or any(e.get(k) != val for k, val in (r.get("si") or {}).items()):
            continue
        depart = L.date_simple(e.get(r.get("depart") or "date") or e.get("date"))
        if depart is None:
            continue
        # Règle bornée dans le temps (transition entre deux régimes de délai).
        if r.get("depart_a_partir_du") and depart.isoformat() < r["depart_a_partir_du"]:
            continue
        if r.get("depart_avant") and depart.isoformat() >= r["depart_avant"]:
            continue
        mois, jours, franc = int(r.get("mois") or 0), int(r.get("jours") or 0), bool(r.get("franc"))
        report = bool(r.get("report_ouvrable", not any(m in r["libelle"].lower() for m in ("prescription", "forclusion"))))
        fin = echeance(depart, mois, jours, False, report)
        res.append({"objet": f"{r['libelle']} ({e.get('fait', '')[:70]})", "libelle": r["libelle"], "date": fin.isoformat(),
                    "date_si_delai_franc": echeance(depart, mois, jours, True, report).isoformat() if franc else None,
                    "regle": r.get("texte", ""), "effet": r.get("effet", ""),
                    "point_de_depart": f"{depart.isoformat()} ({r.get('depart') or 'date'}), pièces {e.get('pieces', [])}", "franc": franc})
    return res


def calculer(racine: Path) -> list[dict]:
    evts = (L.lire_json(racine / "chronologie/chronologie.json", {}) or {}).get("evenements", [])
    res = [r for e in evts for r in calculer_evenement(e)]
    res.sort(key=lambda x: x["date"])
    return res


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--inscrire", action="store_true")
    p.add_argument("--types", action="store_true", help="liste les types d'événement et les attributs qui déclenchent un délai")
    a = p.parse_args()
    if a.types:
        for (typ, _c, lib, mois, jours, franc, texte, _e) in REGLES:
            print(f"{typ} : {lib} ({mois} mois {jours} j{' francs' if franc else ''}) [{texte}]")
        for r in regles_domaines():
            si = ", ".join(f"{k}={v}" for k, v in (r.get("si") or {}).items())
            print(f"{r['type']}{f' ({si})' if si else ''} : {r['libelle']} ({r.get('mois', 0)} mois {r.get('jours', 0)} j{' francs' if r.get('franc') else ''}) "
                  f"[{r.get('texte', '')}] départ = champ « {r.get('depart') or 'date'} »")
        return
    racine = L.trouver_racine(Path.cwd())
    if racine is None:
        raise SystemExit("À lancer depuis un dossier d'affaire.")
    res = calculer(racine)
    if not res:
        print("Aucun délai calculable : typer les événements de la chronologie (voir l'aide).")
        return
    for r in res:
        print(f"- {r['date']} : {r['objet']} [{r['regle']}] ; {r['effet']} ; départ {r['point_de_depart']}{f" ; si délai franc : {r['date_si_delai_franc']}" if r['date_si_delai_franc'] else ''}")
    if a.inscrire:
        chemin = racine / "etat/echeances.json"
        d = L.lire_json(chemin, {"echeances": []}) or {"echeances": []}
        connus = {(x.get("objet"), x.get("date")) for x in d["echeances"]}
        n = 0
        for r in res:
            if (r["objet"], r["date"]) in connus or r["date"] < L.maintenant().date().isoformat():
                continue
            d["echeances"].append({"id": f"E{len(d['echeances']) + 1:03d}", "objet": r["objet"], "date": r["date"], "regle": r["regle"],
                                   "point_de_depart": r["point_de_depart"], "source": "voies.py, à vérifier", "certitude": "scenario",
                                   "statut": "a_venir", "inscrite_le": L.horodatage()})
            n += 1
        L.ecrire_json(chemin, d)
        L.ajouter_journal(racine, f"{n} échéance(s) calculée(s) par voies.py inscrites comme scénarios.", "note")
        print(f"{n} échéance(s) inscrite(s).")


if __name__ == "__main__":
    main()
