"""Profil des décideurs et de l'institution adverse : validation, contrôle avant acte, fiche du juge simulé.

Usage (depuis un dossier d'affaire) :
  python decideurs.py valider                      structure et règles de strategie/decideurs.json
  python decideurs.py controle <brouillon>         constats que gate.py émettrait pour cet acte
  python decideurs.py fiche-juge [--decideur D1]   écrit procedure/calibrage_decideur_<id>.md pour juge-simule
  python decideurs.py squelette                    structure vide du fichier, à remplir (skill lecture-des-decideurs)

La structure est décrite par references/schemas/decideurs.v1.schema.json et validée par le validateur de pieces.py.
Ce module ajoute les règles qui croisent les champs. Bibliothèque standard seulement, aucun appel réseau.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib_affaire as L  # noqa: E402
import pieces as PIECES  # noqa: E402

FICHIER = "strategie/decideurs.json"
SCHEMA = "decideurs.v1.schema.json"
# Un profil de juridiction vit plus longtemps qu'un audit de terrain, mais les séries publiées, la composition des formations
# et les pratiques d'une institution bougent : au-delà, le profil se refait avant l'acte.
VALIDITE_JOURS = 180
LUS = ("en_entier", "extraits")

# Profilage des magistrats : CJA, art. L. 10, al. 4, et COJ, art. L. 111-13, al. 3 (loi n° 2019-222, art. 33),
# peines de l'article 226-18 du code pénal. Le profil vise la juridiction, la formation et la matière, jamais une personne.
RE_PERSONNE = re.compile(
    r"\b(?:M\.|MM\.|Mme|Mmes|Mlle|Monsieur|Madame|Ma[iî]tre|Me)\s+[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ'’\-]+"
    r"|\b(?:juge|présidente?|vice-présidente?|conseill(?:er|ère)|rapporteure?(?: publique?)?|magistrate?|greffi(?:er|ère))"
    r"\s+[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ'’\-]{2,}")
CLES_INTERDITES_JUGE = {"juge_nomme", "nom_du_juge", "nom_juge", "magistrat", "magistrats", "juges_nommes", "nom_magistrat"}
CLES_PROFIL_PERSONNEL = {"personnalite", "psychologie", "profil_psychologique", "temperament", "caractere", "vie_privee"}
RE_PROBA = re.compile(r"(chances?|probabilit\w*)[^.;\n]{0,50}?\d+(?:[,.]\d+)?\s?%|\d+(?:[,.]\d+)?\s?%[^.;\n]{0,50}?(chances?|probabilit\w*)", re.I)
RE_NEGATION = re.compile(r"\b(pas|jamais|aucune?|ni)\b", re.I)


def _k(code: str, message: str, gravite: str = "BLOQUANT") -> dict:
    return {"code": code, "gravite": gravite, "message": message}


def _cles_et_textes(v, chemin="$"):
    """Parcourt le document : (chemin, clé ou None, valeur texte ou None)."""
    if isinstance(v, dict):
        for k, x in v.items():
            yield chemin, k, None
            yield from _cles_et_textes(x, f"{chemin}.{k}")
    elif isinstance(v, list):
        for i, x in enumerate(v):
            yield from _cles_et_textes(x, f"{chemin}[{i}]")
    elif isinstance(v, str):
        yield chemin, None, v


def _refs(v, chemin="$"):
    """Toutes les références à des sources (listes `sources`), hors registre des sources."""
    if isinstance(v, dict):
        for k, x in v.items():
            if k == "sources" and isinstance(x, list) and chemin != "$":
                for i, s in enumerate(x):
                    yield f"{chemin}.sources[{i}]", s
            elif not (chemin == "$" and k == "sources"):
                yield from _refs(x, f"{chemin}.{k}")
    elif isinstance(v, list):
        for i, x in enumerate(v):
            yield from _refs(x, f"{chemin}[{i}]")


def _porteurs_de_sources(v, chemin="$"):
    """Objets qui portent une liste `sources` (constats, standard, leviers, risques...), hors registre."""
    if isinstance(v, dict):
        if isinstance(v.get("sources"), list) and chemin != "$":
            yield chemin, v
        for k, x in v.items():
            if not (chemin == "$" and k == "sources"):
                yield from _porteurs_de_sources(x, f"{chemin}.{k}")
    elif isinstance(v, list):
        for i, x in enumerate(v):
            yield from _porteurs_de_sources(x, f"{chemin}[{i}]")


def valider(doc) -> list[dict]:
    """Constats de structure et de fond sur un profil ; liste vide si le profil est exploitable."""
    if not isinstance(doc, dict):
        return [_k("DECIDEURS_INVALIDE", f"{FICHIER} doit contenir un objet JSON.")]
    schema = PIECES.charger_schema(SCHEMA)
    out = [_k("DECIDEURS_INVALIDE", f"{FICHIER} : {e}") for e in PIECES.valider_schema(doc, schema, schema)]
    if out:
        return out

    sources = {}
    for s in doc["sources"]:
        if s["id"] in sources:
            out.append(_k("ID_DOUBLE", f"Source {s['id']} déclarée deux fois."))
        sources[s["id"]] = s
    ids = {}
    for col in ("decideurs", "leviers", "risques"):
        for x in doc[col]:
            if x["id"] in ids:
                out.append(_k("ID_DOUBLE", f"Identifiant {x['id']} déclaré deux fois."))
            ids[x["id"]] = col

    for chemin, sid in _refs(doc):
        if sid not in sources:
            out.append(_k("SOURCE_INCONNUE", f"{chemin} renvoie à « {sid} », absente du registre des sources du profil "
                          "(un identifiant S<n> par élément de la liste)."))
    for chemin, porteur in _porteurs_de_sources(doc):
        connues = [sources[s] for s in porteur["sources"] if s in sources]
        if connues and not any(s["lu"] in LUS for s in connues):
            out.append(_k("SOURCE_NON_LUE", f"{chemin} : aucune de ses sources n'a été lue en entier ou par extraits ; "
                          "un constat se fonde sur une source lue, sinon il va dans « inconnu »."))

    for d in doc["decideurs"]:
        nom = f"{d['id']} ({d['institution']}, {d['formation']})"
        for t in d["taux_de_base"]:
            if t["numerateur"] > t["denominateur"]:
                out.append(_k("TAUX_INCOHERENT", f"{nom} : « {t['mesure']} » compte {t['numerateur']} sur {t['denominateur']}."))
        if d["nature"] == "juridiction":
            # Alertes ici ; le contrôle de l'acte les rend bloquantes pour la juridiction qui recevra l'acte.
            if not d["taux_de_base"] and not str(d.get("taux_de_base_absent") or "").strip():
                out.append({**_k("TAUX_DE_BASE_ABSENT", f"{nom} : aucun taux de base, et taux_de_base_absent ne dit pas ce qui a été cherché "
                                 "et pourquoi aucune série n'existe pour cette formation, cette procédure et cette matière.", "ALERTE"),
                            "decideur": d["id"]})
            if not d["ce_qui_passe"] or not d["ce_qui_echoue"]:
                out.append({**_k("CALIBRAGE_DESEQUILIBRE", f"{nom} : il faut ce qui passe et ce qui échoue devant ce juge, tirés de ses décisions "
                                 "publiées ; un profil qui ne montre que les refus apprend la sévérité sans apprendre ce qui est accordé. "
                                 "Si la classe ne contient aucun accueil, le dire dans un constat et citer la classe voisine.", "ALERTE"),
                            "decideur": d["id"]})
            publiques = {s for x in _porteurs_de_sources(d) for s in x[1]["sources"]}
            if not any(sources.get(s, {}).get("public") and sources.get(s, {}).get("lu") in LUS for s in publiques):
                out.append(_k("DECIDEUR_SANS_SOURCE_PUBLIQUE", f"{nom} : aucun constat ne repose sur une source publique lue (décisions publiées, "
                              "statistiques, textes) ; le profil d'une juridiction ne se tire pas du seul dossier."))
        for chemin, cle, texte in _cles_et_textes(d, f"decideurs[{d['id']}]"):
            if cle and cle.lower() in CLES_INTERDITES_JUGE:
                out.append(_k("MAGISTRAT_NOMME", f"{chemin}.{cle} : champ nominatif sur un magistrat, interdit (CJA, art. L. 10 ; COJ, art. L. 111-13)."))
            if texte and RE_PERSONNE.search(texte):
                out.append(_k("MAGISTRAT_NOMME", f"{chemin} : « {RE_PERSONNE.search(texte).group(0)} ». Le profil vise la juridiction, la formation "
                              "et la matière ; la réutilisation de l'identité d'un magistrat pour analyser ou prédire ses pratiques est pénalement "
                              "sanctionnée (CJA, art. L. 10 ; COJ, art. L. 111-13). Citer une décision par sa juridiction, sa date et son numéro."))

    cibles_juridiction = {d["id"] for d in doc["decideurs"] if d["nature"] == "juridiction"}
    for x in doc["leviers"] + doc["risques"]:
        cibles = x["cible"] if isinstance(x["cible"], list) else [x["cible"]]
        for cible in cibles:
            if cible != "adversaire" and ids.get(cible) != "decideurs":
                out.append(_k("CIBLE_INCONNUE", f"{x['id']} vise « {cible} » : la cible est l'identifiant d'un décideur du profil (D<n>) "
                              "ou « adversaire », ou une liste de ceux-ci."))
        if set(cibles) & cibles_juridiction:
            for chemin, _, texte in _cles_et_textes(x, x["id"]):
                if texte and RE_PERSONNE.search(texte):
                    out.append(_k("MAGISTRAT_NOMME", f"{chemin} : « {RE_PERSONNE.search(texte).group(0)} » dans un levier ou un risque visant une juridiction."))

    adv = doc["adversaire"]
    if adv["nature"] != "personne_physique":
        for champ, code in (("qui_decide", "QUI_DECIDE_ABSENT"), ("contraintes", "CONTRAINTES_ABSENTES"),
                            ("ce_qu_il_peut_accorder", "CONCESSIONS_ABSENTES")):
            if not adv[champ]:
                out.append(_k(code, f"adversaire.{champ} vide : pour une organisation, il faut savoir qui décide, sous quelles contraintes, "
                              "et ce qu'elle peut accorder sans perdre la face."))
        for champ in ("qui_defend", "culture_juridique", "aversion_au_precedent"):
            if champ not in adv:
                out.append(_k("ADVERSAIRE_INCOMPLET", f"adversaire.{champ} absent (constat sourcé, ou inférence déclarée comme telle)."))
    for chemin, cle, texte in _cles_et_textes(adv, "adversaire"):
        if cle and cle.lower() in CLES_PROFIL_PERSONNEL:
            out.append(_k("PROFIL_PERSONNEL", f"{chemin}.{cle} : aucun portrait psychologique ni élément de vie privée d'une personne ; "
                          "on décrit des fonctions, des procédures et des comportements établis par pièces."))
    for q in adv["qui_decide"]:
        m = RE_PERSONNE.search(q["fonction"])
        if m:
            out.append(_k("PERSONNE_NOMMEE", f"adversaire.qui_decide : « {m.group(0)} ». Décrire la fonction et l'acte de délégation ; "
                          "le nom d'un agent n'ajoute rien au profil et n'a rien à faire dans une requête publique.", "ALERTE"))

    appuis = set()
    for nom, ch in doc["choix"].items():
        for a in ch["appuis"]:
            appuis.add(a)
            if ids.get(a) not in ("leviers", "risques"):
                out.append(_k("APPUI_INCONNU", f"choix.{nom} s'appuie sur « {a} », ni levier ni risque du profil."))
    for x in doc["leviers"] + doc["risques"]:
        if x["id"] not in appuis:
            out.append(_k("LEVIER_INEMPLOYE", f"{x['id']} n'appuie aucun choix : l'employer ou le retirer.", "ALERTE"))

    for chemin, cle, texte in _cles_et_textes(doc):
        if cle and ("probabilit" in cle.lower() or cle.lower().startswith("chance")):
            out.append(_k("PROBABILITE", f"{chemin}.{cle} : aucune probabilité ni chance chiffrée d'un dossier dans le profil."))
        if texte:
            m = RE_PROBA.search(texte)
            if m and not RE_NEGATION.search(m.group(0)):
                out.append(_k("PROBABILITE", f"{chemin} : « {m.group(0)} ». Un taux décrit une classe de décisions publiées ; "
                              "il ne se convertit pas en chance du dossier."))
    return out


def charger(racine: Path) -> tuple[dict | None, list[dict]]:
    chemin = racine / FICHIER
    if not chemin.is_file():
        return None, [_k("DECIDEURS_ABSENT", f"{FICHIER} absent : le profil du décideur et de l'institution adverse s'établit avant tout "
                         "acte juridictionnel (skill lecture-des-decideurs, sous-agent sociologue-institution).")]
    try:
        doc = json.loads(chemin.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return None, [_k("DECIDEURS_INVALIDE", f"{FICHIER} n'est pas un JSON valide (ligne {e.lineno}, colonne {e.colno}) : {e.msg}.")]
    constats = valider(doc)
    return (doc if not any(k["code"] == "DECIDEURS_INVALIDE" for k in constats) else None), constats


def date_declaree(valeur):
    """Une date sans heure compte du début du jour, comme dans controles_campagne."""
    v = str(valeur or "")
    return L.parse_date(v + "T00:00" if len(v) == 10 else v)


def decideur_de_l_acte(doc: dict, stem: str, fiche: dict | None = None) -> dict | None:
    """Le décideur juridictionnel visé : celui que la fiche nomme (champ decideur), sinon celui dont `actes` couvre l'acte,
    sinon la première juridiction du profil."""
    juridictions = [d for d in doc.get("decideurs", []) if d.get("nature") == "juridiction"]
    voulu = (fiche or {}).get("decideur")
    if voulu:
        return next((d for d in doc.get("decideurs", []) if d.get("id") == voulu), None)
    racine_acte = stem.split("_v")[0]
    for d in juridictions:
        if any(racine_acte in a or a in stem for a in d.get("actes", [])):
            return d
    return juridictions[0] if juridictions else None


def _constat_public(x: dict, sources: dict) -> bool:
    return any(sources.get(s, {}).get("public") and sources.get(s, {}).get("lu") in LUS for s in x.get("sources", []))


def corps_fiche_juge(doc: dict, d: dict) -> tuple[str, int]:
    """Ce que le juge simulé reçoit du profil : la juridiction seule, jamais les leviers, les choix ni l'adversaire.
    Les constats tirés du seul dossier sont retirés. Renvoie le texte et le nombre de constats retirés."""
    sources = {s["id"]: s for s in doc.get("sources", [])}
    retires = 0
    cites: list[str] = []

    def ref(ids):
        ids = [i for i in ids if sources.get(i, {}).get("public")]
        cites.extend(i for i in ids if i not in cites)
        return f" [{', '.join(ids)}]" if ids else ""

    def bloc(titre, constats):
        nonlocal retires
        gardes = [x for x in constats if _constat_public(x, sources)]
        retires += len(constats) - len(gardes)
        lignes = ["", f"## {titre}", ""]
        lignes += [f"- {x['constat']} ({x['statut'].replace('_', ' ')}){ref(x['sources'])}" for x in gardes] or ["- Aucun constat public."]
        return lignes

    sc = d["standard_de_controle"]
    out = [f"# Profil du décideur pour le juge simulé : {d['institution']}, {d['formation']}", "",
           f"Profil du {doc.get('date')}, décideur {d['id']}. Stade : {d['stade']}. Procédure : {d['procedure']}. Matière : {d['matiere']}.",
           "Ce profil décrit la juridiction, pas l'affaire. Il ne dit rien des parties et ne contient ni la stratégie ni les arguments de l'auteur de l'acte.",
           "", "## Standard de contrôle", "", f"- Niveau : {sc['niveau'].replace('_', ' ')}. {sc['enonce']}{ref(sc['sources'])}",
           "", "## Taux de base", ""]
    if d["taux_de_base"]:
        for t in d["taux_de_base"]:
            pct = round(100 * t["numerateur"] / t["denominateur"])
            out.append(f"- {t['mesure']} : {t['numerateur']} sur {t['denominateur']} ({pct} %). Périmètre : {t['perimetre']}. "
                       f"Période : {t['periode']}. Exclusions : {t['exclusions']}{ref(t['sources'])}")
        out += ["", "Le taux est le point de départ, écrit avant la lecture de l'acte. Le juge simulé l'ajuste ensuite condition par condition, "
                "par les seuls éléments du dossier qui ont une valeur probante ou juridique, et dit dans quel sens et pourquoi. "
                "Il ne le convertit jamais en chance du dossier : la publication et la sélection des affaires portées au juge le déforment."]
    else:
        out.append(f"- Aucune série publiée : {d.get('taux_de_base_absent', '').strip()}")
    for titre, cle in (("Premier lecteur", "premier_lecteur"), ("Charge", "charge")):
        if d.get(cle):
            out += bloc(titre, [d[cle]])
    out += bloc("Culture et pratique de la formation", d["culture"])
    out += bloc("Ce qui passe devant ce juge", d["ce_qui_passe"])
    out += bloc("Ce qui échoue devant ce juge", d["ce_qui_echoue"])
    out += ["", "## Sources publiques", ""]
    out += [f"- {i} : {sources[i]['reference']}" + (f" ({sources[i]['url']})" if sources[i].get("url") else "") for i in cites] or ["- Aucune."]
    if retires:
        out += ["", f"{retires} constat(s) tiré(s) du seul dossier ont été retirés de cette fiche."]
    return "\n".join(out).rstrip() + "\n", retires


def empreinte_fiche(doc: dict, d: dict) -> str:
    return hashlib.sha256(corps_fiche_juge(doc, d)[0].encode("utf-8")).hexdigest()


def ecrire_fiche_juge(racine: Path, doc: dict, d: dict) -> tuple[Path, str]:
    corps, _ = corps_fiche_juge(doc, d)
    sha = hashlib.sha256(corps.encode("utf-8")).hexdigest()
    chemin = racine / "procedure" / f"calibrage_decideur_{d['id']}.md"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(f"Empreinte du profil : {sha}\n\n" + corps, encoding="utf-8", newline="\n")
    return chemin, sha


DURCIS_POUR_L_ACTE = ("TAUX_DE_BASE_ABSENT", "CALIBRAGE_DESEQUILIBRE")


def controler(racine: Path, ecriture: Path, fiche: dict | None, c) -> None:
    """Contrôle avant un acte juridictionnel, au format de gate.py : c(code, gravite, message)."""
    doc, constats = charger(racine)
    vise = decideur_de_l_acte(doc, ecriture.stem, fiche) if doc is not None else None
    for k in constats:
        gravite = "BLOQUANT" if k["code"] in DURCIS_POUR_L_ACTE and vise and k.get("decideur") == vise.get("id") else k["gravite"]
        c(k["code"], gravite, k["message"])
    if doc is None:
        return
    dt = date_declaree(doc.get("date"))
    if dt is not None:
        age = (L.maintenant() - dt).total_seconds() / 86400
        if age > VALIDITE_JOURS:
            c("DECIDEURS_PERIME", "BLOQUANT", f"Profil des décideurs vieux de {age:.0f} jours (limite {VALIDITE_JOURS}) : le refaire sur les séries "
              "et les décisions publiées depuis.")
    couverts = [str(x) for x in doc.get("actes_couverts", [])]
    racine_acte = ecriture.stem.split("_v")[0]
    if "*" not in couverts and not any(racine_acte in x or x in ecriture.stem for x in couverts):
        c("DECIDEURS_HORS_ACTE", "BLOQUANT", f"Le profil des décideurs ne couvre pas l'acte {ecriture.stem} (actes_couverts).")
    d = vise
    if d is None or d.get("nature") != "juridiction":
        c("DECIDEURS_SANS_JURIDICTION", "BLOQUANT", "Le profil ne désigne pas la juridiction qui recevra l'acte "
          f"({'décideur ' + str((fiche or {}).get('decideur')) + ' introuvable ou non juridictionnel' if (fiche or {}).get('decideur') else 'aucun décideur de nature juridiction'}).")
        return
    lg = L.lire_json(racine / "strategie/ligne.json") or {}
    dl = date_declaree(lg.get("date"))
    if lg and dl and dt and dl < dt and lg.get("profil_decideurs_applique") != doc.get("date"):
        c("LIGNE_ANTERIEURE_AU_PROFIL", "BLOQUANT", "La ligne stratégique est antérieure au profil des décideurs : la relire à sa lumière, puis la "
          "redater ou y inscrire profil_decideurs_applique.")
    lf = L.lire_json(racine / "ecritures" / "controle" / f"{ecriture.stem}.lecture_froid.json")
    if lf is not None and lf.get("profil_decideur_sha256") != empreinte_fiche(doc, d):
        c("LECTURE_FROID_SANS_PROFIL", "BLOQUANT", f"Le juge simulé n'a pas statué sur le profil actuel de {d['id']} ({d['institution']}) : "
          f"produire la fiche (decideurs.py fiche-juge --decideur {d['id']}), la lui donner, et reporter son empreinte dans profil_decideur_sha256.")


SQUELETTE = {
    "schema": "decideurs/1", "date": "", "actes_couverts": [""],
    "decideurs": [{
        "id": "D1", "nature": "juridiction", "institution": "", "formation": "", "stade": "", "procedure": "", "matiere": "", "actes": [""],
        "standard_de_controle": {"niveau": "", "enonce": "", "sources": [""]},
        "taux_de_base": [{"mesure": "", "numerateur": 0, "denominateur": 1, "perimetre": "", "periode": "", "exclusions": "", "sources": [""]}],
        "taux_de_base_absent": "",
        "premier_lecteur": {"constat": "", "statut": "", "sources": [""]},
        "charge": {"constat": "", "statut": "", "sources": [""]},
        "culture": [{"constat": "", "statut": "", "sources": [""]}],
        "ce_qui_passe": [{"constat": "", "statut": "", "sources": [""]}],
        "ce_qui_echoue": [{"constat": "", "statut": "", "sources": [""]}]}],
    "adversaire": {
        "nature": "", "designation": "",
        "qui_decide": [{"fonction": "", "role": "", "fondement": "", "sources": [""]}],
        "qui_defend": {"constat": "", "statut": "", "sources": [""]},
        "culture_juridique": {"constat": "", "statut": "", "sources": [""]},
        "aversion_au_precedent": {"constat": "", "statut": "", "sources": [""]},
        "contraintes": [{"type": "", "constat": "", "statut": "", "sources": [""]}],
        "ce_qu_il_peut_accorder": [{"concession": "", "couverture": "", "statut": "", "sources": [""]}],
        "comportement_procedural": [{"constat": "", "statut": "", "sources": [""]}],
        "saisines_exterieures": [{"canal": "", "effet_attendu": "", "retenue": False, "raison": "", "sources": [""]}]},
    "leviers": [{"id": "L1", "cible": "", "constat": "", "statut": "", "sources": [""]}],
    "risques": [{"id": "R1", "cible": "", "risque": "", "parade": "", "statut": "", "sources": [""]}],
    "choix": {k: {"decision": "", "raison": "", "appuis": [""]} for k in ("forum", "moment", "structure", "ton", "preuve", "demande")},
    "inconnu": [""],
    "sources": [{"id": "S1", "type": "", "reference": "", "url": "", "lu": "", "public": True, "consulte_le": ""}],
}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--racine", help="dossier d'affaire (par défaut : celui qui contient le répertoire courant)")
    sp = p.add_subparsers(dest="cmd", required=True)
    sp.add_parser("valider")
    pc = sp.add_parser("controle")
    pc.add_argument("brouillon")
    pf = sp.add_parser("fiche-juge")
    pf.add_argument("--decideur")
    sp.add_parser("squelette")
    a = p.parse_args(argv)
    if a.cmd == "squelette":
        print(json.dumps(SQUELETTE, ensure_ascii=False, indent=2))
        return 0
    racine = L.trouver_racine(a.racine or (a.brouillon if a.cmd == "controle" else Path.cwd()))
    if racine is None:
        print("Hors d'un dossier d'affaire (etat/affaire.json introuvable).", file=sys.stderr)
        return 2
    if a.cmd == "valider":
        doc, constats = charger(racine)
        for k in constats:
            print(f"- {k['gravite']} {k['code']} : {k['message']}")
        bloquants = sum(1 for k in constats if k["gravite"] == "BLOQUANT")
        print(f"{FICHIER} : {'valide' if not bloquants else 'à reprendre'} ({bloquants} bloquant(s), {len(constats) - bloquants} alerte(s)).")
        return 1 if bloquants else 0
    if a.cmd == "controle":
        ecriture = Path(a.brouillon).resolve()
        fiche = L.lire_json(racine / "ecritures/controle" / f"{ecriture.stem}.fiche.json", {}) or {}
        constats = []
        controler(racine, ecriture, fiche, lambda code, gravite, message, **_: constats.append((gravite, code, message)))
        for g, code, m in constats:
            print(f"- {g} {code} : {m}")
        print(f"{sum(1 for g, _, _ in constats if g == 'BLOQUANT')} bloquant(s).")
        return 1 if any(g == "BLOQUANT" for g, _, _ in constats) else 0
    doc, constats = charger(racine)
    if doc is None or any(k["gravite"] == "BLOQUANT" for k in constats):
        for k in constats:
            print(f"- {k['gravite']} {k['code']} : {k['message']}", file=sys.stderr)
        print("Profil invalide : aucune fiche écrite.", file=sys.stderr)
        return 1
    cibles = [d for d in doc["decideurs"] if d["nature"] == "juridiction" and (not a.decideur or d["id"] == a.decideur)]
    if not cibles:
        print(f"Aucun décideur juridictionnel {a.decideur or ''} dans le profil.", file=sys.stderr)
        return 1
    for d in cibles:
        chemin, sha = ecrire_fiche_juge(racine, doc, d)
        print(f"{chemin.relative_to(racine).as_posix()} : empreinte {sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
