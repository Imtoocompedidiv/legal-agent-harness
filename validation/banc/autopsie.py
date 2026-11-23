"""Autopsie des passages du banc : traits de chaque session, profil de coût, différentiel réussites/échecs, classes de causes.

    python autopsie.py profil <run>                coût par poste (taille x appels qui la relisent), parallélisme, sondes chères
    python autopsie.py differentiel <sonde> [--plugin plugin_v9]
                                                   traits présents dans les réussites et absents des échecs de la même sonde
    python autopsie.py classes [--depuis AAAAMMJJ] [--plugin ...]
                                                   chaque échec rangé dans une classe de cause, puis le décompte par classe

Les traits d'une session se calculent une fois depuis _brut.jsonl et se gardent dans _traits.json, à côté.
Classes : aiguillage (skill chargé par les réussites de la sonde, absent de l'échec), source (outils en erreur ou refusés),
execution (session non terminée), puis raisonnement (le reste, à lire). Une classe n'est qu'une hypothèse à vérifier sur la réponse.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

BANC = Path(__file__).resolve().parent
RACINE = BANC.parent.parent
RESULTATS = BANC / "resultats"
VERSION_TRAITS = 2


def _texte(contenu) -> str:
    if isinstance(contenu, str):
        return contenu
    return "".join(x.get("text", "") for x in contenu or [] if isinstance(x, dict))


def traits(brut: Path) -> dict:
    """Traits d'une session, calculés une fois et gardés dans _traits.json."""
    cache = brut.with_name("_traits.json")
    if cache.is_file() and cache.stat().st_mtime >= brut.stat().st_mtime:
        t = json.loads(cache.read_text(encoding="utf-8"))
        if t.get("version") == VERSION_TRAITS:
            return t
    ev = [json.loads(l) for l in brut.open(encoding="utf-8", errors="replace") if l.startswith("{")]
    appels, noms, ordre = {}, {}, []
    t = {"version": VERSION_TRAITS, "skills": [], "lectures_plugin": [], "sources": [], "outils": collections.Counter(),
         "erreurs_outils": 0, "refus": 0, "blocages_fin": 0, "outils_par_appel": collections.Counter(), "poids": collections.Counter()}
    for i, e in enumerate(ev):
        if e.get("type") == "assistant" and not e.get("parent_tool_use_id"):
            m = e["message"]
            if m.get("id") not in appels:
                appels[m["id"]] = {"i": i, "u": m.get("usage", {}), "n": 0}; ordre.append(m["id"])
            for c in m.get("content", []):
                if c.get("type") != "tool_use":
                    continue
                appels[m["id"]]["n"] += 1
                n, inp = c["name"], c.get("input") or {}
                t["outils"][n] += 1
                if n == "Skill":
                    t["skills"].append(str(inp.get("skill", "")).split(":")[-1]); noms[c["id"]] = "skill"
                    continue
                cle = n
                f = str(inp.get("file_path", "")).replace("\\", "/")
                mp = re.search(r"plugin(?:_v\d+|s/contentieux)/(.+)$", f)
                if n == "Read" and mp:
                    t["lectures_plugin"].append(mp.group(1)); cle = "Read:" + re.sub(r"/[^/]+$", "", mp.group(1))
                if n.startswith("mcp__librejustice__get_") and inp.get("url"):
                    t["sources"].append(inp["url"])
                noms[c["id"]] = cle
        elif e.get("type") == "system" and e.get("subtype") == "notification" and e.get("key") == "stop-hook-error":
            t["blocages_fin"] += 1
        elif e.get("type") == "result":
            u = e.get("usage", {})
            t.update(cout=e.get("total_cost_usd", 0), fin=e.get("stop_reason"), reponse=(e.get("result") or "")[:4000],
                     sortie=u.get("output_tokens", 0), reflexion=(u.get("output_tokens_details") or {}).get("thinking_tokens", 0))
    t["appels"] = len(ordre)
    pos = [appels[k]["i"] for k in ordre]
    for k in ordre:
        t["outils_par_appel"][min(appels[k]["n"], 3)] += 1
    if ordre:
        u = appels[ordre[0]]["u"]
        t["socle"] = u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
        t["contexte_relu"] = sum(a["u"].get("input_tokens", 0) + a["u"].get("cache_creation_input_tokens", 0) + a["u"].get("cache_read_input_tokens", 0) for a in appels.values())
        t["poids"]["socle"] = t["socle"] * len(ordre)
    for i, e in enumerate(ev):
        if e.get("type") != "user" or e.get("parent_tool_use_id"):
            continue
        reste = sum(1 for p in pos if p > i)
        contenu = e["message"].get("content")
        for c in contenu if isinstance(contenu, list) else [{"type": "text", "text": contenu or ""}]:
            if c.get("type") == "tool_result":
                v = _texte(c.get("content"))
                if c.get("is_error"):
                    t["erreurs_outils"] += 1
                    if "hook error" in v or "refus" in v.lower():
                        t["refus"] += 1
                t["poids"][noms.get(c.get("tool_use_id"), "?")] += len(v) / 3.5 * reste
            elif c.get("type") == "text":
                t["poids"]["texte injecté"] += len(c.get("text", "")) / 3.5 * reste
    for k in ("outils", "outils_par_appel", "poids"):
        t[k] = dict(t[k])
    cache.write_text(json.dumps(t, ensure_ascii=False), encoding="utf-8")
    return t


def sessions(plugin: str | None = None, depuis: str | None = None, sonde: str | None = None):
    """Chaque session notée : (passage, plugin, résultat, traits). Le dernier passage noté fait foi pour un même dossier."""
    vus = {}
    for f in sorted(RESULTATS.glob("*.json")):
        if depuis and f.stem[:8] < depuis:
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        nom_plugin = Path(str(d.get("plugin", ""))).name
        if plugin and nom_plugin != plugin:
            continue
        for r in d.get("resultats", []):
            if sonde and r.get("id") != sonde:
                continue
            brut = Path(str(r.get("dossier", ""))) / "_brut.jsonl"
            if brut.is_file():
                vus[str(brut)] = (d.get("run"), nom_plugin, r, brut)
    for run, nom_plugin, r, brut in vus.values():
        yield run, nom_plugin, r, traits(brut)


def profil(run: str) -> None:
    d = json.loads((RESULTATS / f"{run}.json").read_text(encoding="utf-8"))
    lignes = [(r, traits(Path(r["dossier"]) / "_brut.jsonl")) for r in d["resultats"] if (Path(str(r.get("dossier", ""))) / "_brut.jsonl").is_file()]
    cout = sum(t.get("cout", 0) for _, t in lignes); appels = sum(t["appels"] for _, t in lignes)
    ctx = sum(t.get("contexte_relu", 0) for _, t in lignes) or 1
    poids = collections.Counter()
    par_appel = collections.Counter()
    for _, t in lignes:
        poids.update(t["poids"]); par_appel.update({int(k): v for k, v in t["outils_par_appel"].items()})
    print(f"{run} : {len(lignes)} sessions, {cout:.1f} $, {appels} appels modèle, contexte relu {ctx / 1e6:.1f} Mtok, "
          f"socle moyen {sum(t.get('socle', 0) for _, t in lignes) / max(1, len(lignes)) / 1e3:.1f} ktok, "
          f"sortie {sum(t.get('sortie', 0) for _, t in lignes) / 1e6:.2f} Mtok dont réflexion {sum(t.get('reflexion', 0) for _, t in lignes) / 1e6:.2f}")
    print("postes (part du contexte relu) :", ", ".join(f"{k} {v / ctx:.0%}" for k, v in poids.most_common(8)))
    print("outils par appel (0, 1, 2, 3+) :", [par_appel.get(i, 0) for i in range(4)])
    print("sondes les plus chères :", ", ".join(f"{r['id']} {t.get('cout', 0):.2f} $ ({t['appels']} appels)" for r, t in sorted(lignes, key=lambda x: -x[1].get("cout", 0))[:6]))


def _ensembles(t: dict) -> set[str]:
    s = {f"skill:{x}" for x in t["skills"]} | {f"lit:{x}" for x in t["lectures_plugin"]} | {f"outil:{x}" for x in t["outils"]}
    s |= {f"source:{x.rsplit('/', 1)[-1]}" for x in t["sources"]}
    if t["blocages_fin"]:
        s.add("blocage_fin")
    return s


def differentiel(sonde: str, plugin: str | None) -> None:
    ok, ko = [], []
    for run, nom_plugin, r, t in sessions(plugin=plugin, sonde=sonde):
        (ok if r.get("reussi") else ko).append((run, nom_plugin, r, t))
    print(f"{sonde} : {len(ok)} réussite(s), {len(ko)} échec(s)" + (f" sous {plugin}" if plugin else ""))
    if not ok or not ko:
        return
    fo = collections.Counter(x for *_, t in ok for x in _ensembles(t)); fk = collections.Counter(x for *_, t in ko for x in _ensembles(t))
    ecarts = sorted({*fo, *fk}, key=lambda x: -abs(fo[x] / len(ok) - fk[x] / len(ko)))
    print("traits qui séparent (part des réussites / part des échecs) :")
    for x in ecarts[:10]:
        a, b = fo[x] / len(ok), fk[x] / len(ko)
        if abs(a - b) >= 0.5:
            print(f"  {a:4.0%} / {b:4.0%}  {x}")
    for run, nom_plugin, r, t in ko[:3]:
        print(f"-- échec {run} [{nom_plugin}] : {str(r.get('details', ''))[:300]}\n   {t.get('reponse', '')[:300]!r}")


def classer(r: dict, t: dict, skills_reussites: collections.Counter, n_reussites: int) -> str:
    if r.get("statut_execution") != "termine" or t.get("fin") not in (None, "end_turn"):
        return "execution"
    manque = [s for s, n in skills_reussites.items() if n_reussites and n / n_reussites >= 0.67 and s not in t["skills"]]
    if manque:
        return "aiguillage (" + ", ".join(manque) + ")"
    if t["refus"] + t["erreurs_outils"] >= 3:
        return "source"
    return "raisonnement"


def classes(depuis: str | None, plugin: str | None) -> None:
    tout = list(sessions(plugin=plugin, depuis=depuis))
    par_sonde = collections.defaultdict(list)
    for x in tout:
        par_sonde[x[2]["id"]].append(x)
    decompte = collections.Counter(); exemples = collections.defaultdict(list)
    for sonde, xs in par_sonde.items():
        reussites = [t for _, _, r, t in xs if r.get("reussi")]
        sk = collections.Counter(s for t in reussites for s in set(t["skills"]))
        for run, nom_plugin, r, t in xs:
            if r.get("reussi"):
                continue
            c = classer(r, t, sk, len(reussites)); racine = c.split(" (")[0]
            decompte[racine] += 1; exemples[racine].append(f"{sonde} [{nom_plugin}] {c[len(racine):]}".strip())
    n = sum(decompte.values())
    print(f"{n} échec(s) sur {len(tout)} sessions notées")
    for c, k in decompte.most_common():
        print(f"  {c} : {k} ({k / max(1, n):.0%}) ; ex. " + " ; ".join(exemples[c][:4]))


def calibration(depuis: str | None) -> None:
    """Sondes générées par l'usine : taux de bonnes réponses et sens des erreurs, par plugin et par famille."""
    sondes = {json.loads(f.read_text(encoding="utf-8"))["id"]: json.loads(f.read_text(encoding="utf-8")) for f in (BANC / "sondes").glob("GEN-*.json")}
    tab = collections.defaultdict(lambda: collections.Counter())
    for run, nom_plugin, r, t in sessions(depuis=depuis):
        s = sondes.get(r.get("id"))
        if not s:
            continue
        attendu = "oui" if "oui" in s["verifications"][0]["motif"] else "non"
        m = re.match(r"\W*(oui|non)\b", t.get("reponse", ""), re.I)
        dit = m.group(1).lower() if m else "?"
        c = tab[(nom_plugin, s.get("famille"))]
        c["n"] += 1; c["juste"] += dit == attendu
        if dit != attendu:
            c[f"{dit}_au_lieu_de_{attendu}"] += 1
        c["cout"] += t.get("cout", 0)
    for (p, fam), c in sorted(tab.items()):
        erreurs = ", ".join(f"{k} {v}" for k, v in c.items() if "_au_lieu_de_" in k)
        print(f"{p:<12} {fam:<16} {c['juste']}/{c['n']} justes ({c['juste'] / c['n']:.0%}) ; {erreurs or 'aucune erreur'} ; {c['cout'] / c['n']:.2f} $ par session")


QUESTION_MANQUE = """Un avocat a rendu un pronostic faux. Compare sa réponse au raisonnement réel de la juridiction et dis ce qui lui a manqué.
Classe la cause principale dans une seule catégorie :
- "mal_pese" : l'élément décisif était dans le dossier remis, et la réponse l'a ignoré ou mal pesé ;
- "public_trouvable" : l'élément décisif n'était pas dans le dossier, mais il était public et trouvable avant la décision (texte, décision antérieure, jurisprudence, pièce publiée) ;
- "non_public" : l'élément décisif relève de pièces ou d'échanges que seul le juge avait (mémoire, pièces, audience) ;
- "appreciation" : aucune information ne manquait ; le juge a apprécié autrement.
Réponds uniquement par un objet JSON : {"categorie": "...", "element": "l'élément décisif, en vingt mots au plus", "comment_l_obtenir": "si public_trouvable, où et comment l'obtenir, en vingt mots au plus, sinon vide"}

## Dossier remis à l'avocat (extrait)
{dossier}

## Réponse de l'avocat
{reponse}

## Raisonnement réel de la juridiction
{motifs}
"""


def manques(maximum: int) -> None:
    """Sur chaque sonde de pronostic ratée, ce qui a manqué, par catégorie : la catégorie « public_trouvable » désigne la primitive suivante."""
    import correcteur
    import usine
    sys.path.insert(0, str(BANC))
    caps = {}
    for fam in ("urgence-l521-1", "refere-liberte", "cassation-civile"):
        for d in usine._captures(usine.USINE / fam).values():
            caps[re.sub(r"\W", "", (d.get("docket_numbers") or [""])[0])] = (fam, d)
    sondes = {json.loads(f.read_text(encoding="utf-8"))["id"]: json.loads(f.read_text(encoding="utf-8")) for f in (BANC / "sondes").glob("GENP-*.json")}
    vus, lignes, cout = set(), [], 0.0
    for run, p, r, t in sessions():
        s = sondes.get(r.get("id"))
        if not s or r.get("reussi") or s["id"] in vus or len(vus) >= maximum:
            continue
        fam, d = caps.get(s["id"].split("-")[-1], (None, None))
        if not d:
            continue
        coupe = usine.FAMILLES["cassation-civile" if fam == "cassation-civile" else fam]["coupe"]
        m = re.search(coupe, d["text"])
        motifs = d["text"][m.start():m.start() + 6000] if m else ""
        dossier = (BANC / "fixtures" / s["fixture"] / "dossier_remis.md").read_text(encoding="utf-8")[:9000]
        texte = QUESTION_MANQUE.replace("{dossier}", dossier).replace("{reponse}", t.get("reponse", "")[:4000]).replace("{motifs}", motifs)
        try:
            rep, c = correcteur.demander(texte); cout += c
            v = json.loads(re.search(r"\{.*\}", rep, re.S).group(0))
        except Exception as e:  # noqa: BLE001
            v = {"categorie": "?", "element": f"analyse en erreur : {type(e).__name__}", "comment_l_obtenir": ""}
        vus.add(s["id"]); lignes.append((s["id"], p, v))
        print(f"{s['id']:<24} [{p}] {v.get('categorie')} : {v.get('element')}" + (f" -> {v['comment_l_obtenir']}" if v.get("comment_l_obtenir") else ""), flush=True)
    dec = collections.Counter(v.get("categorie") for _, _, v in lignes)
    print(f"\n{len(lignes)} échecs analysés, {cout:.2f} $ : " + ", ".join(f"{k} {n}" for k, n in dec.most_common()))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("profil").add_argument("run")
    d = s.add_parser("differentiel"); d.add_argument("sonde"); d.add_argument("--plugin")
    c = s.add_parser("classes"); c.add_argument("--depuis"); c.add_argument("--plugin")
    s.add_parser("calibration").add_argument("--depuis")
    s.add_parser("manques").add_argument("--max", type=int, default=24)
    a = p.parse_args()
    if a.cmd == "manques":
        manques(a.max)
        return
    if a.cmd == "profil":
        profil(a.run)
    elif a.cmd == "calibration":
        calibration(a.depuis)
    elif a.cmd == "differentiel":
        differentiel(a.sonde, a.plugin)
    else:
        classes(a.depuis, a.plugin)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
