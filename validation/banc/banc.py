"""Banc d'évaluation rapide du harness contentieux : sondes ciblées, notées automatiquement, lancées en parallèle.

Une sonde reproduit un défaut réel (ou une capacité exigée) dans une situation minimale, avec une réponse attendue
vérifiable mécaniquement. Chaque correctif commence par une sonde qui échoue et finit quand elle passe sans faire
régresser les autres. Les épreuves complètes ne viennent qu'aux jalons.

Usage :
  python banc.py lister
  python banc.py lancer [--ids A,B] [--capacite X] [--parallele 2] [--plugin CHEMIN] [--etiquette TEXTE]
                        (sessions lancées en priorité inférieure à la normale ; au plus 2 en parallèle quand le poste est partagé)
  python banc.py noter <run>            renote un passage à partir des sorties brutes (après correction d'une vérification)
  python banc.py comparer <run_a> <run_b>
  python banc.py tableau                régénère TABLEAU.md
  python banc.py instantanes [--enregistrer]   rejoue le contrôle sur les écritures des épreuves et compare à l'instantané
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path

BANC = Path(__file__).resolve().parent
DEPOT = BANC.parents[1]
PLUGIN = DEPOT / "plugins" / "contentieux"
SONDES = BANC / "sondes"
FIXTURES = BANC / "fixtures"
RESULTATS = BANC / "resultats"
# Les dossiers de sonde vivent hors du dépôt (22 novembre) : sous le dépôt, Claude Code chargeait dans chaque sonde la mémoire
# automatique du projet (notes de développement, pointeurs vers un dossier privé). Le nom final « banc_runs » est gardé : le
# bornage (borne_banc.py) reconnaît les dossiers des autres sondes à ce segment.
EXECUTIONS = Path(os.environ.get("BANC_EXECUTIONS") or Path.home() / ".harness-banc" / "banc_runs")
OUTILS = ("Agent,Task,Read,Write,Edit,Glob,Grep,Bash,PowerShell,TodoWrite,mcp__librejustice__search_decisions,mcp__librejustice__get_decision,"
          "mcp__librejustice__search_norms,mcp__librejustice__get_norm,mcp__hal__search_hal,mcp__shs_fr__theses_search,mcp__shs_fr__isidore_search,"
          "mcp__shs_fr__sudoc_search,mcp__academic_papers__search_openalex,mcp__academic_papers__search_crossref")


def norm(t: str) -> str:
    t = unicodedata.normalize("NFKC", t or "").replace(" ", " ").replace(" ", " ").replace("’", "'")
    # Pas de mise en minuscules : elle inverserait les classes \S, \W et \D des motifs. La casse est ignorée à la recherche.
    return re.sub(r"\s+", " ", t)


def cherche(motif: str, texte: str) -> bool:
    return re.search(norm(motif), texte, re.IGNORECASE) is not None


def empreinte_plugin(racine: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(p for p in racine.rglob("*") if p.is_file() and "__pycache__" not in p.parts and ".pytest_cache" not in p.parts):
        h.update(f.relative_to(racine).as_posix().encode())
        h.update(f.read_bytes())
    return h.hexdigest()[:12]


def charger_sondes() -> list[dict]:
    res = []
    for f in sorted(SONDES.glob("*.json")):
        s = json.loads(f.read_text(encoding="utf-8"))
        s.setdefault("id", f.stem)
        res.append(s)
    return res


def preparer(sonde: dict, dossier: Path, plugin: Path = PLUGIN) -> None:
    if dossier.exists():
        shutil.rmtree(dossier)
    if sonde.get("affaire", True):
        # Le dossier se crée avec le gabarit du plugin mesuré (constitution comprise), pas avec celui du plugin courant.
        subprocess.run([sys.executable, str(plugin / "scripts" / "affaire.py"), "init", str(dossier), "--intitule", sonde.get("intitule", "Sonde"),
                        "--client", "Client", "--objectif", sonde.get("objectif", "Gagner")], check=True, capture_output=True)
    else:
        dossier.mkdir(parents=True)
    src = FIXTURES / sonde["fixture"] if sonde.get("fixture") else None
    if src and src.is_dir():
        shutil.copytree(src, dossier, dirs_exist_ok=True)
    for nom, contenu in (sonde.get("fichiers") or {}).items():
        p = dossier / nom
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(contenu if isinstance(contenu, str) else json.dumps(contenu, ensure_ascii=False, indent=2), encoding="utf-8")


# Serveurs MCP dont le harness se sert. Les autres serveurs de l'utilisateur (serena et son pyright, biomcp...) démarraient avec
# chaque session du banc et chargeaient le poste partagé pour rien (20 novembre).
MCP_DU_HARNESS = ("librejustice", "legal_harness", "hal", "shs_fr", "academic_papers", "asta")
_CONFIG_MCP: list[str] = []


def config_mcp() -> list[str]:
    """Arguments --strict-mcp-config et --mcp-config limités aux serveurs du harness, tirés de la configuration de l'utilisateur
    dans un fichier temporaire hors du dépôt (aucune clé n'est copiée dans le projet), supprimé à la sortie."""
    if _CONFIG_MCP:
        return _CONFIG_MCP
    import atexit
    import tempfile
    conf = json.loads((Path.home() / ".claude.json").read_text(encoding="utf-8")).get("mcpServers") or {}
    garde = {k: v for k, v in conf.items() if k in MCP_DU_HARNESS}
    fd, chemin = tempfile.mkstemp(prefix="banc_mcp_", suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump({"mcpServers": garde}, f)
    atexit.register(lambda: os.path.exists(chemin) and os.remove(chemin))
    _CONFIG_MCP.extend(["--strict-mcp-config", "--mcp-config", chemin])
    return _CONFIG_MCP


def executer(sonde: dict, run: str, plugin: Path) -> dict:
    dossier = EXECUTIONS / run / sonde["id"]
    preparer(sonde, dossier, plugin)
    env = dict(os.environ)
    env["BANC_PLUGIN"] = str(plugin.resolve()).replace("\\", "/")
    env["CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS"] = "0"
    env["BANC_DOSSIER"] = sonde["id"].lower()
    env["BANC_COUPE"] = sonde.get("coupe", "9999-12-31")
    if sonde.get("horloge"):
        env["CONTENTIEUX_MAINTENANT"] = sonde["horloge"]
    else:
        env.pop("CONTENTIEUX_MAINTENANT", None)
    # Chaque essai part d'un environnement propre (Anthropic, « Demystifying evals for AI agents ») : le profil et les positions
    # personnels de ~/.harness-juridique ne doivent pas entrer dans une sonde, qui ne lit que le cabinet/ de son dossier.
    env["HARNESS_JURIDIQUE_CONFIG"] = str(dossier / ".profil_banc_absent")
    reglages = BANC / "reglages_banc.json"
    texte = reglages.read_text(encoding="utf-8")
    if "{{RACINE}}" in texte:
        # Distribution publique : le chemin du hook de bornage se résout ici, à partir de l'emplacement du banc.
        reglages = dossier / ".reglages_banc.json"
        reglages.write_text(texte.replace("{{RACINE}}", str(BANC.parents[1]).replace("\\", "/")), encoding="utf-8")
    cmd = [shutil.which("claude") or "claude", "-p", sonde["consigne"], "--plugin-dir", str(plugin), "--settings", str(reglages),
           "--model", os.environ.get("BANC_MODELE") or sonde.get("modele", "opus"), "--permission-mode", "acceptEdits", "--allowedTools", sonde.get("outils", OUTILS),
           "--disallowedTools", "WebFetch,WebSearch", "--output-format", "stream-json", "--verbose",
           # Ni skills, ni plugins, ni CLAUDE.md de niveau utilisateur : 99 skills et 65 000 signes de liste dans chaque sonde,
           # sans rapport avec le dossier (22 novembre). Permissions, outils et MCP sont fixés ici, pas par l'utilisateur.
           "--setting-sources", "project,local",
           # Plafond de dépense appliqué par Claude Code : une sonde emballée s'arrête au lieu de brûler le budget du banc.
           "--max-budget-usd", str(sonde.get("budget_usd", 8)), *config_mcp()]
    if sonde.get("agent"):
        cmd += ["--agent", sonde["agent"]]
    # Niveau d'effort de raisonnement (23 novembre : 866 tokens de réflexion en médiane par pronostic au réglage par défaut).
    if os.environ.get("BANC_EFFORT"):
        cmd += ["--effort", os.environ["BANC_EFFORT"]]
    debut = time.time()
    statut = "termine"
    try:
        # Le banc partage le poste avec d'autres sessions, dont des tests chronométrés : priorité inférieure à la normale.
        priorite = {"creationflags": subprocess.BELOW_NORMAL_PRIORITY_CLASS} if os.name == "nt" else {}
        p = subprocess.run(cmd, cwd=dossier, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=int(sonde.get("budget_minutes", 10)) * 60, **priorite)
        brut = p.stdout
    except subprocess.TimeoutExpired as e:
        statut = "delai_depasse"
        brut = (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
    (dossier / "_brut.jsonl").write_text(brut, encoding="utf-8")
    return {"id": sonde["id"], "statut_execution": statut, "duree_s": round(time.time() - debut), "dossier": str(dossier)}


def lire_brut(dossier: Path) -> tuple[str, list[dict], float]:
    texte, outils, cout, messages = "", [], 0.0, []
    f = dossier / "_brut.jsonl"
    if not f.exists():
        return texte, outils, cout
    for ligne in f.read_text(encoding="utf-8").splitlines():
        try:
            e = json.loads(ligne)
        except json.JSONDecodeError:
            continue
        if e.get("type") == "assistant":
            for b in (e.get("message") or {}).get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    outils.append({"outil": b.get("name"), "entree": b.get("input"), "sous_agent": e.get("parent_tool_use_id")})
                if isinstance(b, dict) and b.get("type") == "text" and not e.get("parent_tool_use_id"):
                    messages.append(str(b.get("text") or ""))
        if e.get("type") == "result":
            texte = str(e.get("result") or "")
            cout = float(e.get("total_cost_usd") or 0)
    # Toute la réponse de la session principale : le hook de fin peut imposer une passation qui devient le dernier message.
    complet = "\n\n".join(m for m in messages if m.strip())
    if texte and texte not in complet:
        complet = (complet + "\n\n" + texte).strip()
    return complet or texte, outils, cout


def messages_principaux(dossier: Path) -> list[str]:
    res = []
    f = dossier / "_brut.jsonl"
    if not f.exists():
        return res
    for ligne in f.read_text(encoding="utf-8").splitlines():
        try:
            e = json.loads(ligne)
        except json.JSONDecodeError:
            continue
        if e.get("type") == "assistant" and not e.get("parent_tool_use_id"):
            res += [str(b.get("text") or "") for b in (e.get("message") or {}).get("content") or [] if isinstance(b, dict) and b.get("type") == "text"]
        if e.get("type") == "result" and e.get("result"):
            res.append(str(e["result"]))
    return [m for m in res if m.strip()]


def chemin_json(obj, chemin: str):
    for k in chemin.split("."):
        if isinstance(obj, list):
            try:
                obj = obj[int(k)]
            except (ValueError, IndexError):
                return None
        elif isinstance(obj, dict):
            obj = obj.get(k)
        else:
            return None
    return obj


def verifier(v: dict, dossier: Path, reponse: str, outils: list[dict]) -> tuple[bool, str]:
    cible = reponse
    if v.get("fichier"):
        # Un motif ou une liste : un délai se lit aussi dans l'échéancier où l'agent l'a inscrit.
        motifs = v["fichier"] if isinstance(v["fichier"], list) else [v["fichier"]]
        fichiers = sorted({f for m in motifs for f in dossier.glob(m)})
        cible = "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in fichiers if f.is_file())
        if v.get("avec_reponse"):
            # Le point décisif peut sortir de l'acte demandé comme de la réponse qui l'accompagne.
            cible = reponse + "\n\n" + cible
        elif not fichiers:
            return False, f"fichier absent : {v['fichier']}"
    t = norm(cible)
    typ = v["type"]
    if typ in ("contient", "absent"):
        trouve = cherche(v["motif"], t)
        return (trouve if typ == "contient" else not trouve), v["motif"]
    if typ == "contient_un":
        ok = [m for m in v["motifs"] if cherche(m, t)]
        return bool(ok), f"un de {v['motifs']}"
    if typ == "contient_tous":
        manq = [m for m in v["motifs"] if not cherche(m, t)]
        return not manq, f"manquent {manq}" if manq else "tous"
    if typ == "json":
        try:
            obj = json.loads(cible)
        except json.JSONDecodeError:
            return False, "JSON illisible"
        val = chemin_json(obj, v["chemin"])
        if "egal" in v:
            return val == v["egal"], f"{v['chemin']} = {val!r}"
        if "dans" in v:
            return val in v["dans"], f"{v['chemin']} = {val!r}"
        if "contient" in v:
            return cherche(v["contient"], norm(json.dumps(val, ensure_ascii=False))), f"{v['chemin']} contient {v['contient']}"
        return val not in (None, "", [], {}), f"{v['chemin']} présent"
    if typ == "outil":
        for o in outils:
            if str(o["outil"]).startswith(v["outil"]) and (not v.get("entree_contient") or
                                                          cherche(v["entree_contient"], norm(json.dumps(o["entree"], ensure_ascii=False)))):
                return True, f"{v['outil']} appelé"
        return False, f"{v['outil']} {v.get('entree_contient', '')} non appelé"
    if typ == "message_commence":
        # La réponse finale commence par le motif (verdict demandé en tête de réponse). Seul compte le dernier message qui ouvre sur
        # un verdict : jusqu'au 23 novembre 2026, n'importe quel message suffisait, et une session qui changeait d'avis après le
        # hook Stop était créditée dans les deux sens (v50 : 34 changements sur 280, 72,9 % comptés pour 66,1 % en réponse finale).
        msgs = [norm(m).strip() for m in messages_principaux(dossier)]
        verdicts = [m for m in msgs if re.match(r"\W*(oui|non)\b", m, re.I)] or msgs
        return bool(verdicts) and cherche("^" + v["motif"], verdicts[-1]), f"la réponse finale commence par {v['motif']}"
    if typ == "outil_absent":
        return not any(str(o["outil"]).startswith(v["outil"]) for o in outils), f"{v['outil']} non appelé"
    return False, f"type inconnu {typ}"


def noter(sonde: dict, execution: dict) -> dict:
    dossier = Path(execution["dossier"])
    reponse, outils, cout = lire_brut(dossier)
    details, critiques_ok, points, total = [], True, 0.0, 0.0
    # Les critères jugés au sens partent ensemble au correcteur : un seul appel par sonde.
    # Un critère peut porter sur un fichier du dossier (l'acte rédigé) plutôt que sur la réponse finale.
    criteres = [v for v in sonde.get("verifications", []) if v["type"] == "critere"]
    jugements = {}
    if criteres and reponse:
        import correcteur
        groupes: dict[str, list] = {}
        for v in criteres:
            cible = reponse
            if v.get("fichier"):
                motifs = v["fichier"] if isinstance(v["fichier"], list) else [v["fichier"]]
                fichiers = sorted({f for m in motifs for f in dossier.glob(m)}, key=lambda f: f.stat().st_mtime)
                cible = (fichiers[-1].read_text(encoding="utf-8", errors="replace") if fichiers else "") + "\n\n[Réponse finale]\n" + reponse
            groupes.setdefault(cible, []).append(v)
        for cible, vs in groupes.items():
            for v, j in zip(vs, correcteur.juger(sonde.get("consigne", ""), cible, [v["critere"] for v in vs], dossier)):
                jugements[id(v)] = j
    for v in sonde.get("verifications", []):
        ok, info = jugements.get(id(v), (False, "réponse absente")) if v["type"] == "critere" else verifier(v, dossier, reponse, outils)
        poids = float(v.get("poids", 1))
        total += poids
        points += poids if ok else 0
        if not ok and v.get("critique", True):
            critiques_ok = False
        details.append({"verification": v.get("description") or info, "ok": ok, "info": info})
    reussi = critiques_ok and execution["statut_execution"] == "termine" and bool(reponse or sonde.get("sortie_fichier_seule"))
    return {**execution, "capacite": sonde.get("capacite"), "reussi": reussi, "score": round(points / total, 2) if total else 0,
            "details": details, "cout_usd": round(cout, 3), "nb_outils": len(outils)}


def historique(plugin_nom: str) -> dict[str, list[bool]]:
    """Réussites passées de chaque sonde sous un plugin donné (nom du dossier), le dernier passage noté faisant foi par dossier."""
    vus: dict[str, tuple[str, bool]] = {}
    for f in sorted(RESULTATS.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        if Path(str(d.get("plugin", ""))).name != plugin_nom:
            continue
        for r in d.get("resultats", []):
            vus[str(r.get("dossier") or f"{f.stem}/{r['id']}")] = (r["id"], bool(r.get("reussi")))
    h: dict[str, list[bool]] = {}
    for i, ok in vus.values():
        h.setdefault(i, []).append(ok)
    return h


def cmd_lancer(a) -> None:
    if getattr(a, "modele", None):
        os.environ["BANC_MODELE"] = a.modele
    """Un passage, ou un passage adaptatif : chaque sonde tourne une fois, puis de nouveau, jusqu'à --adaptatif fois, seulement
    si elle échoue, si elle est nouvelle ou si elle est instable sous le plugin de référence. Les tours vont à la variance."""
    sondes = charger_sondes()
    if a.ids:
        motifs = a.ids.split(",")
        sondes = [s for s in sondes if any(fnmatch.fnmatchcase(s["id"], m) for m in motifs)]
    if a.capacite:
        sondes = [s for s in sondes if s.get("capacite") == a.capacite]
    if not getattr(a, "adaptatif", 0):
        passage(a, sondes)
        return
    ref = historique(a.reference) if a.reference else {}
    issues: dict[str, list[bool]] = {}
    a_lancer = sondes
    for tour in range(1, a.adaptatif + 1):
        if not a_lancer:
            break
        print(f"Tour adaptatif {tour} : {len(a_lancer)} sonde(s).", flush=True)
        for r in passage(a, a_lancer, suffixe=f"-t{tour}"):
            issues.setdefault(r["id"], []).append(bool(r["reussi"]))
        def stable(i: str) -> bool:
            h = ref.get(i, [])
            return len(h) >= 2 and all(h)
        a_lancer = [s for s in sondes if not (all(issues.get(s["id"], [False])) and stable(s["id"]))]
    print("Bilan adaptatif (réussites / tours ; référence) :")
    for s in sondes:
        x, h = issues.get(s["id"], []), ref.get(s["id"], [])
        print(f"  {s['id']:<36} {sum(x)}/{len(x)}" + (f"   réf. {sum(h)}/{len(h)}" if h else "   réf. aucune"))
    n = sum(len(x) for x in issues.values())
    print(f"{n} sessions au lieu de {len(sondes) * a.adaptatif} pour {a.adaptatif} tours partout.")


def passage(a, sondes: list[dict], suffixe: str = "") -> list[dict]:
    plugin = Path(a.plugin).resolve() if a.plugin else PLUGIN
    run = datetime.now().strftime("%Y%m%d-%H%M%S") + f"-{os.getpid() % 10000:04d}"
    a = argparse.Namespace(**{**vars(a), "etiquette": (a.etiquette or "") + suffixe})
    print(f"Passage {run} : {len(sondes)} sonde(s), plugin {plugin} [{empreinte_plugin(plugin)}], {a.parallele} en parallèle.", flush=True)
    resultats = []
    with cf.ThreadPoolExecutor(max_workers=a.parallele) as ex:
        futurs = {ex.submit(executer, s, run, plugin): s for s in sondes}
        for fu in cf.as_completed(futurs):
            s = futurs[fu]
            try:
                r = noter(s, fu.result())
            except Exception as e:  # noqa: BLE001
                r = {"id": s["id"], "capacite": s.get("capacite"), "reussi": False, "score": 0, "statut_execution": f"erreur {e}"}
            resultats.append(r)
            print(f"  {'OK ' if r['reussi'] else 'KO '} {r['id']:<34} {r.get('score', 0):.2f}  {r.get('duree_s', '?')} s", flush=True)
    sortie = {"run": run, "etiquette": a.etiquette or "", "plugin": str(plugin), "empreinte_plugin": empreinte_plugin(plugin),
              "date": datetime.now().isoformat(timespec="seconds"), "resultats": sorted(resultats, key=lambda r: r["id"])}
    RESULTATS.mkdir(exist_ok=True)
    (RESULTATS / f"{run}.json").write_text(json.dumps(sortie, ensure_ascii=False, indent=2), encoding="utf-8")
    ok = sum(1 for r in resultats if r["reussi"])
    print(f"Réussies : {ok}/{len(resultats)}. Résultats : {RESULTATS / (run + '.json')}")
    cmd_tableau(a)
    return resultats


DEFAUTS = BANC / "defauts.json"


def cmd_defauts(a) -> int:
    """Registre des défauts corrigés : chaque classe garde ses sondes (la sonde d'origine et des variantes tirées d'autres décisions)
    et son exigence. Chaque sonde tourne k fois ; une classe ne passe que si chacune de ses sondes réussit ses k essais (pass^k). Une
    version ne se fige que si toutes les classes passent : un défaut corrigé ne peut plus revenir sans être vu."""
    reg = json.loads(DEFAUTS.read_text(encoding="utf-8"))
    classes = [c for c in reg["classes"] if not a.classes or c["id"] in a.classes.split(",")]
    connues = {s["id"]: s for s in charger_sondes()}
    manquantes = sorted({i for c in classes for i in c["sondes"] if i not in connues})
    if manquantes:
        raise SystemExit(f"Sondes du registre introuvables : {', '.join(manquantes)}")
    k = a.k or max(int(c.get("k", 3)) for c in classes)
    ids = sorted({i for c in classes for i in c["sondes"]})
    issues: dict[str, list[bool]] = {}
    for tour in range(1, k + 1):
        for r in passage(argparse.Namespace(**{**vars(a), "etiquette": (a.etiquette or "defauts")}), [connues[i] for i in ids], suffixe=f"-t{tour}"):
            issues.setdefault(r["id"], []).append(bool(r["reussi"]))
    bilan, echec = [], False
    for c in classes:
        kc = int(c.get("k", 3))
        lignes = {i: issues.get(i, [])[:kc] for i in c["sondes"]}
        ok = all(len(x) == kc and all(x) for x in lignes.values())
        echec |= not ok
        bilan.append({"classe": c["id"], "passe": ok, "k": kc, "sondes": {i: f"{sum(x)}/{len(x)}" for i, x in lignes.items()}})
        print(f"{'PASSE' if ok else 'ÉCHOUE'}  {c['id']:<42} " + "  ".join(f"{i} {sum(x)}/{len(x)}" for i, x in lignes.items()))
    (RESULTATS / "defauts" / f"defauts-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json").write_text(
        json.dumps({"plugin": str(Path(a.plugin).resolve() if a.plugin else PLUGIN), "k": k, "bilan": bilan}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print("Registre des défauts : " + ("ÉCHEC, version à ne pas figer." if echec else "toutes les classes passent."))
    return 1 if echec else 0


def cmd_noter(a) -> None:
    f = RESULTATS / f"{a.run}.json"
    d = json.loads(f.read_text(encoding="utf-8"))
    sondes = {s["id"]: s for s in charger_sondes()}
    d["resultats"] = [noter(sondes[r["id"]], r) if r["id"] in sondes and r.get("dossier") else r for r in d["resultats"]]
    f.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Renoté : {sum(1 for r in d['resultats'] if r['reussi'])}/{len(d['resultats'])}")
    cmd_tableau(a)


def charger_runs() -> list[dict]:
    # Les rapports du registre (resultats/defauts/) n'ont pas de « resultats » : seuls les passages comptent.
    return [d for d in (json.loads(f.read_text(encoding="utf-8")) for f in sorted(RESULTATS.glob("*.json"))) if "resultats" in d]


def cmd_comparer(a) -> None:
    ra, rb = (json.loads((RESULTATS / f"{x}.json").read_text(encoding="utf-8")) for x in (a.run_a, a.run_b))
    ia, ib = ({r["id"]: r for r in x["resultats"]} for x in (ra, rb))
    for sid in sorted(set(ia) | set(ib)):
        x, y = ia.get(sid), ib.get(sid)
        if x and y and x["reussi"] != y["reussi"]:
            print(f"{'GAIN     ' if y['reussi'] else 'RÉGRESSION'} {sid}")
        elif not x or not y:
            print(f"{'nouvelle  ' if y else 'retirée   '} {sid}")
    print(f"{ra['run']} : {sum(r['reussi'] for r in ra['resultats'])}/{len(ra['resultats'])} ; {rb['run']} : {sum(r['reussi'] for r in rb['resultats'])}/{len(rb['resultats'])}")


def cmd_tableau(a=None) -> None:
    runs = charger_runs()
    lignes = ["# Tableau du banc", "", "Généré par `banc.py tableau`. Une ligne par passage, puis l'historique de chaque sonde (O réussie, x échouée).", "",
              "| Passage | Étiquette | Plugin | Réussies | Par capacité |", "| --- | --- | --- | --- | --- |"]
    for r in runs:
        caps = {}
        for x in r["resultats"]:
            c = caps.setdefault(x.get("capacite") or "?", [0, 0])
            c[0] += 1 if x["reussi"] else 0
            c[1] += 1
        lignes.append(f"| {r['run']} | {r.get('etiquette', '')} | {r.get('empreinte_plugin', '')} | {sum(x['reussi'] for x in r['resultats'])}/{len(r['resultats'])} | "
                      + ", ".join(f"{k} {v[0]}/{v[1]}" for k, v in sorted(caps.items())) + " |")
    lignes += ["", "| Sonde | Capacité | Historique (du plus ancien au plus récent) |", "| --- | --- | --- |"]
    for s in charger_sondes():
        hist = "".join(next(("O" if x["reussi"] else "x" for x in r["resultats"] if x["id"] == s["id"]), "·") for r in runs)
        lignes.append(f"| {s['id']} | {s.get('capacite', '')} | `{hist}` |")
    (BANC / "TABLEAU.md").write_text("\n".join(lignes) + "\n", encoding="utf-8")


def cmd_instantanes(a) -> None:
    """Contrôle mécanique rejoué sur les écritures des épreuves : détecte en secondes une régression des verrous."""
    sys.path.insert(0, str(PLUGIN / "scripts"))
    essais = DEPOT / "essais-contentieux"
    obtenu = {}
    for gate_json in sorted(essais.glob("epreuve-sequence-*/ecritures/controle/*.gate.json")):
        v = json.loads(gate_json.read_text(encoding="utf-8"))
        ecriture = gate_json.parents[2] / v["ecriture"]
        if not ecriture.exists():
            continue
        env = dict(os.environ)
        if v.get("horloge_fixee"):
            env["CONTENTIEUX_MAINTENANT"] = v["horloge_fixee"]
        p = subprocess.run([sys.executable, str(PLUGIN / "scripts" / "gate.py"), str(ecriture), "--json"], capture_output=True, text=True,
                           encoding="utf-8", env=env, timeout=120)
        try:
            res = json.loads(p.stdout)
        except json.JSONDecodeError:
            continue
        obtenu[ecriture.relative_to(essais).as_posix()] = {"verdict": res["verdict"], "bloquants": sorted({k["code"] for k in res["constats"] if k["gravite"] == "BLOQUANT"})}
    f = BANC / "instantanes.json"
    if a.enregistrer or not f.exists():
        f.write_text(json.dumps(obtenu, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Instantané enregistré : {len(obtenu)} écritures.")
        return
    ref = json.loads(f.read_text(encoding="utf-8"))
    ecarts = 0
    for k in sorted(set(ref) | set(obtenu)):
        if ref.get(k) != obtenu.get(k):
            ecarts += 1
            a_, b_ = ref.get(k) or {}, obtenu.get(k) or {}
            print(f"{k} : {a_.get('verdict')} -> {b_.get('verdict')} ; apparus {sorted(set(b_.get('bloquants', [])) - set(a_.get('bloquants', [])))} ; "
                  f"disparus {sorted(set(a_.get('bloquants', [])) - set(b_.get('bloquants', [])))}")
    print(f"{len(obtenu)} écritures rejouées, {ecarts} écart(s) avec l'instantané.")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("lister")
    l = s.add_parser("lancer")
    l.add_argument("--ids")
    l.add_argument("--capacite")
    l.add_argument("--parallele", type=int, default=2)
    l.add_argument("--plugin")
    l.add_argument("--etiquette")
    l.add_argument("--adaptatif", type=int, default=0, help="nombre maximal de tours par sonde ; les tours vont aux sondes qui échouent, nouvelles ou instables")
    l.add_argument("--modele", help="modèle de toutes les sessions (ex. fable) ; défaut : celui de la sonde, sinon opus")
    l.add_argument("--reference", help="nom du plugin de référence pour l'instabilité (ex. plugin_v9)")
    n = s.add_parser("noter")
    n.add_argument("run")
    c = s.add_parser("comparer")
    c.add_argument("run_a")
    c.add_argument("run_b")
    s.add_parser("tableau")
    i = s.add_parser("instantanes")
    i.add_argument("--enregistrer", action="store_true")
    d = s.add_parser("defauts", help="registre des défauts corrigés, chaque sonde k fois (pass^k)")
    d.add_argument("--plugin")
    d.add_argument("--classes", help="identifiants de classes, séparés par des virgules ; défaut : toutes")
    d.add_argument("--k", type=int, default=0, help="essais par sonde ; défaut : le k de chaque classe")
    d.add_argument("--parallele", type=int, default=2)
    d.add_argument("--etiquette")
    d.add_argument("--modele")
    a = p.parse_args()
    if a.cmd == "lister":
        for x in charger_sondes():
            print(f"{x['id']:<34} {x.get('capacite', ''):<14} {x.get('origine', '')}")
    elif a.cmd == "lancer":
        cmd_lancer(a)
    elif a.cmd == "noter":
        cmd_noter(a)
    elif a.cmd == "comparer":
        cmd_comparer(a)
    elif a.cmd == "tableau":
        cmd_tableau(a)
    elif a.cmd == "instantanes":
        cmd_instantanes(a)
    elif a.cmd == "defauts":
        if getattr(a, "modele", None):
            os.environ["BANC_MODELE"] = a.modele
        sys.exit(cmd_defauts(a))


if __name__ == "__main__":
    main()
