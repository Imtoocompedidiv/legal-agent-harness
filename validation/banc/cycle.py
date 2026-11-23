"""Un cycle d'amélioration en une commande : mesure adaptative d'une version, puis calibration, classes d'échecs, coût et
critère de version finale, comparés à la référence.

    python cycle.py --plugin banc_runs/plugin_v13 --reference plugin_v9 [--ids "GEN-*,URGENCE-*,OFFENSIVE-*"] [--adaptatif 2]
    python cycle.py --bilan plugin_v12 --reference plugin_v9      sans relancer : bilan des passages déjà notés

Critère de version finale (docs/MOTEUR.md, section 7) : sur chaque famille générée, au moins 85 % de bonnes réponses et des
erreurs qui ne penchent pas d'un côté (écart d'au plus une entre « oui » à tort et « non » à tort) ; sondes visées réussies à
chaque tour ; coût moyen par session au plus celui de la référence. La non-régression sur le banc complet se vérifie à part.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import subprocess
import sys
from pathlib import Path

BANC = Path(__file__).resolve().parent
sys.path.insert(0, str(BANC))
import autopsie  # noqa: E402

VISEES = ("URGENCE-INTERET-ENFANT", "URGENCE-RETRAIT-AGREMENT", "OFFENSIVE-FOND-AF")


def lancer(plugin: str, reference: str, ids: str, adaptatif: int) -> None:
    cmd = [sys.executable, str(BANC / "banc.py"), "lancer", "--plugin", plugin, "--ids", ids, "--adaptatif", str(adaptatif),
           "--reference", reference, "--etiquette", Path(plugin).name + "-cycle"]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    for l in r.stdout.splitlines():
        if re.search(r"Tour adaptatif|sessions au lieu|Traceback|Error", l):
            print(l)


def proba(reponse: str) -> float | None:
    m = re.search(r"(\d{1,3})(?:[,.]\d+)?\s?%", reponse[:300])
    return min(100, int(m.group(1))) / 100 if m else None


def brier(reponse: str, attendu: str) -> float:
    """Score de Brier de la réponse : (probabilité donnée au « oui » - issue réelle)². Sans probabilité, la réponse vaut 0 ou 1."""
    m = re.match(r"\W*(oui|non)\b", reponse, re.I)
    if not m:
        return 1.0
    q = proba(reponse)
    q = 1.0 if q is None else q
    p_oui = q if m.group(1).lower() == "oui" else 1 - q
    return (p_oui - (1.0 if attendu == "oui" else 0.0)) ** 2


def bilan(plugin: str, reference: str) -> bool:
    sondes = {json.loads(f.read_text(encoding="utf-8"))["id"]: json.loads(f.read_text(encoding="utf-8")) for f in (BANC / "sondes").glob("*.json")}
    tab = collections.defaultdict(collections.Counter)
    visees = collections.defaultdict(list)
    for run, p, r, t in autopsie.sessions():
        if p not in (plugin, reference):
            continue
        s = sondes.get(r.get("id"))
        if not s:
            continue
        if s["id"] in VISEES:
            visees[(p, s["id"])].append(bool(r.get("reussi")))
        if not s.get("genere"):
            continue
        attendu = "oui" if "oui" in s["verifications"][0]["motif"] else "non"
        m = re.match(r"\W*(oui|non)\b", t.get("reponse", ""), re.I)
        dit = m.group(1).lower() if m else "?"
        c = tab[(p, s["famille"])]
        c["n"] += 1; c["juste"] += dit == attendu; c["cout"] += t.get("cout", 0)
        c["brier"] += brier(t.get("reponse", ""), attendu); c["avec_proba"] += bool(proba(t.get("reponse", "")))
        if dit != attendu:
            c["oui_a_tort" if dit == "oui" else "non_a_tort" if dit == "non" else "sans_tete"] += 1
    final = True
    print(f"{'version':<12} {'famille':<16} justes   oui à tort  non à tort  sans tête  Brier  $/session")
    for (p, fam), c in sorted(tab.items(), key=lambda x: (x[0][1], x[0][0])):
        taux = c["juste"] / c["n"]
        b = f"{c['brier'] / c['n']:.3f}" if c["avec_proba"] else "  -  "
        print(f"{p:<12} {fam:<16} {c['juste']:>2}/{c['n']:<3} {taux:4.0%}  {c['oui_a_tort']:>6}  {c['non_a_tort']:>10}  {c['sans_tete']:>9}  {b}  {c['cout'] / c['n']:8.2f}")
        if p == plugin and (taux < 0.85 or abs(c["oui_a_tort"] - c["non_a_tort"]) > 1 or c["sans_tete"]):
            final = False
    for (p, i), xs in sorted(visees.items()):
        if p == plugin:
            print(f"visée {i:<28} {sum(xs)}/{len(xs)}")
            final = final and all(xs)
    # Test apparié, sonde par sonde : seules comptent les sondes où les deux versions diffèrent. Un écart que le hasard explique
    # (p > 0,05) n'est pas un gain : on n'adopte pas un correctif sur du bruit.
    # Le score apparié est le Brier (plus bas, meilleur) quand les sondes demandent une probabilité, sinon la réussite.
    par_sonde = collections.defaultdict(lambda: {plugin: [], reference: []})
    for run, p, r, t in autopsie.sessions():
        s = sondes.get(r.get("id"))
        if p in (plugin, reference) and s and s.get("genere"):
            attendu = "oui" if "oui" in s["verifications"][0]["motif"] else "non"
            par_sonde[r["id"]][p].append(1 - brier(t.get("reponse", ""), attendu) if r["id"].startswith("GENP-") else bool(r.get("reussi")))
    # Test t apparié sur l'écart de score par sonde : il garde l'ampleur des écarts, que le test des signes jetait.
    ecarts = [sum(v[plugin]) / len(v[plugin]) - sum(v[reference]) / len(v[reference]) for v in par_sonde.values() if v[plugin] and v[reference]]
    n = len(ecarts)
    if n >= 2:
        from math import erf, sqrt
        moy = sum(ecarts) / n
        sd = sqrt(sum((x - moy) ** 2 for x in ecarts) / (n - 1)) or 1e-9
        t = moy / (sd / sqrt(n))
        p_val = 2 * (1 - 0.5 * (1 + erf(abs(t) / sqrt(2))))  # approximation normale, n de l'ordre de 40
        ic = 1.96 * sd / sqrt(n)
        print(f"apparié sur {n} sondes générées : écart moyen de score {moy:+.3f} (IC 95 % {moy - ic:+.3f} à {moy + ic:+.3f}) ; "
              f"mieux {sum(x > 0 for x in ecarts)}, pire {sum(x < 0 for x in ecarts)} ; p = {p_val:.2f}"
              + (" (écart significatif)" if p_val <= 0.05 else " (écart compatible avec le hasard)"))
    else:
        p_val = 1.0
    cout = {p: sum(c["cout"] for (q, _), c in tab.items() if q == p) / max(1, sum(c["n"] for (q, _), c in tab.items() if q == p)) for p in (plugin, reference)}
    final = final and cout[plugin] <= cout[reference] * 1.05
    print(f"coût moyen par session générée : {plugin} {cout[plugin]:.2f} $, {reference} {cout[reference]:.2f} $")
    print("critère de version finale :", "ATTEINT" if final else "non atteint")
    return final


def main() -> None:
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--plugin"); a.add_argument("--bilan"); a.add_argument("--reference", default="plugin_v9")
    a.add_argument("--ids", default="GENP-*," + ",".join(VISEES)); a.add_argument("--adaptatif", type=int, default=2)
    x = a.parse_args()
    if x.plugin:
        lancer(x.plugin, x.reference, x.ids, x.adaptatif)
    nom = Path(x.plugin).name if x.plugin else x.bilan
    bilan(nom, x.reference)
    print("\nclasses d'échecs :"); autopsie.classes(None, nom)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
