"""Mécanique des exercices : catalogue des fiches et contrôle du diagnostic porté par la fiche de l'acte.

Usage :
  python exercices.py liste
  python exercices.py fiche <identifiant>        chemin et données de contrôle d'un exercice
  python exercices.py squelette <identifiant>    bloc « exercice » à remplir pour cet exercice
  python exercices.py valider <fiche.json>       contrôle du bloc d'une fiche de l'acte
  python exercices.py controle <ecriture.md>     constats du module pour une écriture, seuls

Les fiches d'exercice sont dans skills/mecanique-des-exercices/references/ ; chacune se termine par une section
« Données de contrôle » qui contient un objet JSON (identifiant, régimes de gate.py, condition principale, conditions
décisives, exigences implicites, voisins, marqueurs du texte). Le bloc « exercice » de la fiche de l'acte
(ecritures/controle/<nom>.fiche.json) dit le diagnostic fait avant la production : juge et stade, ce qu'il décide,
condition décisive et sa preuve, cible, ce qui fait gagner, exigences implicites vérifiées, voisins écartés.

Le contrôle est mécanique : il vérifie que chaque question du diagnostic a reçu une réponse rattachée à une pièce
du bordereau, à un fait de la matrice ou à une source lue du registre. Il n'atteste pas que la réponse est juste.
Bibliothèque standard seulement.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib_affaire as L  # noqa: E402

REFERENCES = Path(__file__).resolve().parents[1] / "skills" / "mecanique-des-exercices" / "references"
CLES_DONNEES = {"id", "intitule", "famille", "juridictionnel", "types_acte", "cible", "condition_principale", "conditions_decisives",
                "exigences_implicites", "voisins", "erreurs_hors_sujet", "marqueurs_texte", "sources_principales"}
# Clés facultatives du contrat : une présomption renverse la charge de la condition (hook.py, contrat compact).
CLES_FACULTATIVES = {"presomptions", "a_lire", "indices_neutres"}
FAMILLES = {"amiable", "administrative", "autorite_independante", "urgence", "fond", "indemnitaire", "penal", "europeen",
            "constitutionnel", "voie_de_recours"}
CIBLES = {"acte", "decision_juridictionnelle", "pretention", "faits", "norme", "document", "situation"}
NON_JURIDICTIONNELS = {"courrier_precontentieux"}
# Modes d'envoi qui prouvent la date d'expédition ou de dépôt (CE, 30 juin 2025, n° 494573 ; CRPA, art. L. 112-1).
MODES_DATES = {"depot_contre_recepisse", "lettre_recommandee", "envoi_postal_avec_preuve_de_depot", "teleservice", "telerecours",
               "rpva", "courrier_electronique_avec_accuse", "signification"}
BUTS_DELAI = {"proroger", "interrompre", "conserver"}
# Constats qui restent bloquants pour un courrier : ils font perdre le délai lui-même.
TOUJOURS_BLOQUANTS = {"EXERCICE_DELAI_NON_PROTEGE", "EXERCICE_PROROGATION_EXCLUE"}
# Constats qui restent bloquants en mode conservatoire : ils touchent l'exercice, le régime et l'acte, pas la preuve.
NON_DIFFERABLES = {"EXERCICE_ABSENT", "EXERCICE_INCONNU", "EXERCICE_REGIME_DISCORDANT", "EXERCICE_REGIME_SPECIAL_NON_EXAMINE",
                   "EXERCICE_REGIME_SPECIAL_IGNORE", "EXERCICE_CIBLE_DISCORDANTE", "EXERCICE_DELAI_NON_PROTEGE",
                   "EXERCICE_PROROGATION_EXCLUE"}
FICHIER_CATALOGUE = re.compile(r"## Données de contrôle\s*```json\s*(.*?)```", re.S)


def _texte(v) -> str:
    if isinstance(v, (list, tuple)):
        return " ".join(_texte(x) for x in v).strip()
    if isinstance(v, dict):
        return " ".join(_texte(x) for x in v.values()).strip()
    return str(v or "").strip()


def charger_catalogue(dossier: Path = REFERENCES) -> dict[str, dict]:
    """Identifiant -> données de contrôle de sa fiche, plus le chemin de la fiche (clé « fichier »)."""
    catalogue: dict[str, dict] = {}
    for f in sorted(dossier.glob("*.md")) if dossier.is_dir() else []:
        m = FICHIER_CATALOGUE.search(f.read_text(encoding="utf-8"))
        if not m:
            continue
        try:
            d = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(d, dict) and d.get("id"):
            catalogue[d["id"]] = {**d, "fichier": f.name}
    return catalogue


def conditions_connues(entree: dict) -> set[str]:
    noms = {str(entree.get("condition_principale") or "")}
    noms |= {str(c.get("condition")) for c in entree.get("conditions_decisives") or [] if isinstance(c, dict)}
    return {n for n in noms if n}


def voisins_catalogue(entree: dict) -> list[str]:
    return [str(v.get("exercice")) for v in entree.get("voisins") or [] if isinstance(v, dict) and v.get("exercice")]


def squelette(identifiant: str, catalogue: dict | None = None) -> dict:
    """Bloc « exercice » vide pour un exercice du catalogue : la structure, les exigences et les voisins à examiner."""
    catalogue = charger_catalogue() if catalogue is None else catalogue
    e = catalogue.get(identifiant)
    if e is None:
        raise KeyError(identifiant)
    return {
        "exercice": identifiant,
        "date": "AAAA-MM-JJTHH:MM",
        "juge_et_stade": {"juge": "", "stade": "", "standard": "", "office": ""},
        "ce_qu_il_decide": "",
        "condition_decisive": {"condition": e.get("condition_principale"), "pourquoi_decisive": "",
                               "preuve": {"pieces": [], "faits": [], "sources": []},
                               "ce_qui_la_ferait_tomber": [{"situation": s, "parade": "", "pieces": []}
                                                           for c in e.get("conditions_decisives") or []
                                                           if c.get("condition") == e.get("condition_principale")
                                                           for s in [x["texte"] if isinstance(x, dict) else x
                                                                     for x in c.get("ce_qui_la_fait_tomber") or []]]},
        "cible": {"nature": e.get("cible"), "designation": "", "acte": "", "date": ""},
        "ce_qui_fait_gagner": "",
        "exigences_implicites": [{"cle": x.get("cle"), "exigence": x.get("exigence"), "verifiee": False, "preuve": "", "source": ""}
                                 for x in e.get("exigences_implicites") or []],
        "voisins_ecartes": [{"exercice": v, "raison": ""} for v in voisins_catalogue(e)],
        "regime_special": {"applicable": False, "texte": "", "type_acte": ""},
    }


def contexte_dossier(racine: Path | None) -> dict:
    if racine is None:
        return {"sources": None, "bordereau": None, "matrice": None, "evenements": None}
    reg = L.lire_json(racine / "etat/sources.json")
    bord = L.lire_json(racine / "pieces/bordereau.json")
    mat = L.lire_json(racine / "preuves/matrice.json")
    return {"sources": {s.get("id"): s for s in (reg or {}).get("sources", []) if isinstance(s, dict)} if reg else None,
            "bordereau": {str(p.get("cote")) for p in (bord or {}).get("pieces", []) if isinstance(p, dict)} if bord else None,
            "matrice": {str(f.get("id")) for f in (mat or {}).get("faits_a_prouver", []) if isinstance(f, dict)} if mat else None}


def valider(bloc, fiche: dict | None = None, catalogue: dict | None = None, contexte: dict | None = None) -> list[dict]:
    """Constats sur le bloc « exercice » d'une fiche de l'acte, au format de gate.py, avant toute modulation de gravité.

    `fiche` est la fiche de l'acte entière (type_acte, actes_attaques, conditions, delai) ; `contexte` porte le registre
    des sources, le bordereau et les identifiants de la matrice (None quand le fichier manque).
    """
    fiche = fiche or {}
    catalogue = charger_catalogue() if catalogue is None else catalogue
    ctx = contexte or {"sources": None, "bordereau": None, "matrice": None}
    out: list[dict] = []

    def c(code, gravite, message, **extra):
        out.append({"code": code, "gravite": gravite, "message": message, **extra})

    if not isinstance(bloc, dict) or not _texte(bloc.get("exercice")):
        c("EXERCICE_ABSENT", "BLOQUANT", "La fiche de l'acte ne porte pas le diagnostic de l'exercice (champ « exercice ») : qui décide, à quel "
          "stade, sur quoi, avec quel standard, la condition qui fait échouer et sa preuve, la cible, les exigences implicites, "
          "l'exercice voisin (skill mecanique-des-exercices ; exercices.py squelette <identifiant>).")
        return out
    ident = str(bloc["exercice"]).strip()
    hors_catalogue = ident.startswith("autre:")
    e = catalogue.get(ident)
    if e is None and not hors_catalogue:
        c("EXERCICE_INCONNU", "BLOQUANT", f"Exercice « {ident} » inconnu ; identifiants : {', '.join(sorted(catalogue))}, ou « autre:<libellé> » "
          "pour un exercice sans fiche.")
        e = {}
    e = e or {}
    type_acte = fiche.get("type_acte")

    # Le régime sous lequel l'acte est contrôlé doit être celui de l'exercice : sinon ses conditions ne sont pas vérifiées.
    types = e.get("types_acte") or []
    if e and types and type_acte and type_acte not in types:
        c("EXERCICE_REGIME_DISCORDANT", "BLOQUANT", f"L'acte est contrôlé sous le régime « {type_acte} » alors que l'exercice « {ident} » "
          f"relève de {', '.join(types)} : ses conditions et ses sanctions ne seraient pas vérifiées. Corriger type_acte ou l'exercice.")
    elif e and not types:
        c("EXERCICE_SANS_REGIME", "ALERTE", f"Aucun régime de gate.py ne correspond à l'exercice « {ident} » : ses conditions propres "
          f"(fiche {e.get('fichier')}) ne sont vérifiées que par le présent diagnostic.")

    js = bloc.get("juge_et_stade") if isinstance(bloc.get("juge_et_stade"), dict) else {}
    manq = [k for k in ("juge", "stade", "standard", "office") if not _texte(js.get(k))]
    if manq:
        c("EXERCICE_JUGE_STADE_INCOMPLET", "BLOQUANT", f"Diagnostic : {', '.join(manq)} non renseigné(s) dans juge_et_stade. Le juge, le stade "
          "(filtre, tri, audience, admission), le standard de contrôle et ce que ce juge peut ordonner à ce stade commandent l'acte entier.")
    if not _texte(bloc.get("ce_qu_il_decide")):
        c("EXERCICE_DECISION_ABSENTE", "BLOQUANT", "Diagnostic : la question exacte que le décideur tranchera n'est pas écrite (ce_qu_il_decide).")
    if not _texte(bloc.get("ce_qui_fait_gagner")):
        c("EXERCICE_GAIN_ABSENT", "BLOQUANT", "Diagnostic : ce qui fait gagner devant ce décideur n'est pas écrit (ce_qui_fait_gagner).")

    # Condition décisive, sa preuve, et ce qui la ferait tomber.
    cd = bloc.get("condition_decisive") if isinstance(bloc.get("condition_decisive"), dict) else {}
    nom = _texte(cd.get("condition"))
    noms_fiche = {str(x.get("condition")) for x in fiche.get("conditions") or [] if isinstance(x, dict)}
    if not nom:
        c("EXERCICE_CONDITION_ABSENTE", "BLOQUANT", "Diagnostic : la condition qui décide du sort de l'exercice n'est pas nommée (condition_decisive).")
    elif e and nom not in conditions_connues(e) | noms_fiche:
        c("EXERCICE_CONDITION_HORS_EXERCICE", "BLOQUANT", f"Condition décisive « {nom} » étrangère à l'exercice « {ident} » et aux conditions "
          f"de la fiche de l'acte ; conditions de l'exercice : {', '.join(sorted(conditions_connues(e)))}.")
    _verifier_preuve(cd.get("preuve"), ctx, c, "EXERCICE_PREUVE", f"Condition décisive « {nom or '?'} »")
    chutes = [x for x in cd.get("ce_qui_la_ferait_tomber") or [] if isinstance(x, dict)]
    sans_parade = [x for x in chutes if not (_texte(x.get("situation")) and _texte(x.get("parade")))]
    if not chutes or sans_parade:
        c("EXERCICE_CONDITION_NON_EPROUVEE", "BLOQUANT", f"Condition décisive « {nom or '?'} » : "
          + ("aucune situation qui la ferait tomber n'est examinée" if not chutes else
             f"{len(sans_parade)} situation(s) sans parade : « {_texte(sans_parade[0].get('situation'))[:120]} »")
          + ". Prendre l'argument de la défense dans sa meilleure version (intérêt invoqué que le juge attribuera à la mesure, situation qui ôte "
          "l'urgence, décision qui fait obstacle, retard du demandeur) et écrire la parade, pièce à l'appui ; sans parade, l'exercice va en réserve.")
    for x in chutes:
        if x.get("pieces") and ctx.get("bordereau") is not None:
            hors = [str(p) for p in x["pieces"] if str(p) not in ctx["bordereau"]]
            if hors:
                c("EXERCICE_PREUVE_HORS_DOSSIER", "BLOQUANT", f"Parade « {_texte(x.get('situation'))[:80]} » : pièces {hors} absentes du bordereau.")
    etat_fiche = {str(x.get("condition")): x for x in fiche.get("conditions") or [] if isinstance(x, dict)}
    if nom in etat_fiche:
        etat = etat_fiche[nom].get("etat")
        if etat == "absente":
            c("EXERCICE_CONDITION_DECISIVE_ECARTEE", "BLOQUANT", f"La condition décisive « {nom} » est déclarée absente dans la fiche : "
              "l'exercice échoue sur elle ; construire la preuve ou retenir le voisin.")
        elif etat == "fragile":
            c("EXERCICE_CONDITION_DECISIVE_FRAGILE", "ALERTE", f"La condition décisive « {nom} » est fragile : l'exercice se perd si elle tombe. "
              "Dire pourquoi aucun voisin ne convient mieux.")
    principale = _texte(e.get("condition_principale"))
    if principale and nom and nom != principale:
        cp = bloc.get("condition_principale") if isinstance(bloc.get("condition_principale"), dict) else {}
        dans_fiche = etat_fiche.get(principale) or {}
        etablie_fiche = dans_fiche.get("etat") == "etablie" and all((f_ or {}).get("pieces") for f_ in dans_fiche.get("faits") or [{}])
        etablie_bloc = _texte(cp.get("condition")) == principale and cp.get("etat") == "etablie" and _a_une_preuve(cp.get("preuve"))
        if not (etablie_fiche or etablie_bloc):
            c("EXERCICE_CONDITION_PRINCIPALE_NON_TRAITEE", "BLOQUANT", f"La condition qui fait le plus souvent échouer « {ident} » est "
              f"« {principale} » (fiche {e.get('fichier')}) ; le diagnostic en retient une autre sans établir celle-ci (condition_principale, "
              "état « etablie » et preuve, ou entrée établie sur pièces dans les conditions de la fiche).")
        elif etablie_bloc:
            _verifier_preuve(cp.get("preuve"), ctx, c, "EXERCICE_PREUVE", f"Condition principale « {principale} »")

    # Cible.
    cible = bloc.get("cible") if isinstance(bloc.get("cible"), dict) else {}
    nature = _texte(cible.get("nature"))
    if nature not in CIBLES or not _texte(cible.get("designation")):
        c("EXERCICE_CIBLE_INCOMPLETE", "BLOQUANT", f"Cible : nature ({', '.join(sorted(CIBLES))}) et désignation exactes exigées.")
    attendue = _texte(e.get("cible"))
    if attendue and nature and nature in CIBLES and nature != attendue:
        c("EXERCICE_CIBLE_DISCORDANTE", "BLOQUANT", f"La cible de l'exercice « {ident} » est de nature « {attendue} » ; le diagnostic vise "
          f"« {nature} ». Une cible étrangère à l'exercice le fait échouer quelle que soit la qualité de l'acte.")
    actes = [a for a in (fiche.get("actes_attaques") or ([fiche["acte_attaque"]] if fiche.get("acte_attaque") else [])) if isinstance(a, dict)]
    if nature == "acte" and actes:
        ids = {str(a.get("id")) for a in actes} | {str(a.get("designation")) for a in actes}
        if _texte(cible.get("acte")) not in ids:
            c("EXERCICE_CIBLE_DISCORDANTE", "BLOQUANT", f"La cible du diagnostic (acte « {_texte(cible.get('acte')) or '?'} ») ne correspond à aucun "
              "acte attaqué de la fiche (champ cible.acte : identifiant de actes_attaques).")
    if nature == "decision_juridictionnelle" and not L.date_simple(_texte(cible.get("date"))):
        c("EXERCICE_CIBLE_INCOMPLETE", "BLOQUANT", "Cible : la décision juridictionnelle attaquée doit être datée (cible.date, AAAA-MM-JJ).")

    # Exigences implicites de la fiche, une par une.
    donnees = {str(x.get("cle")): x for x in bloc.get("exigences_implicites") or [] if isinstance(x, dict) and x.get("cle")}
    non_verifiees = []
    for x in e.get("exigences_implicites") or []:
        cle = str(x.get("cle"))
        d = donnees.get(cle) or {}
        ok = (d.get("verifiee") is True and (_texte(d.get("preuve")) or _texte(d.get("source")))) or len(_texte(d.get("sans_objet"))) >= 10
        if not ok:
            non_verifiees.append(cle)
    if non_verifiees:
        c("EXERCICE_EXIGENCE_NON_VERIFIEE", "BLOQUANT", f"Exigences implicites de « {ident} » non vérifiées ({len(non_verifiees)}) : "
          f"{', '.join(non_verifiees[:12])}{' …' if len(non_verifiees) > 12 else ''}. Chacune se dit vérifiée avec sa preuve ou sa source lue, "
          f"ou sans objet avec sa raison (fiche {e.get('fichier')}, section 6).", exigences=non_verifiees)
    registre = ctx.get("sources")
    for cle, d in donnees.items():
        s = _texte(d.get("source"))
        if not s or registre is None:
            continue
        if s in registre:
            if registre[s].get("lu_en_entier") is not True:
                c("EXERCICE_SOURCE_NON_LUE", "BLOQUANT", f"Exigence « {cle} » : la source {s} est inscrite au registre sans avoir été lue en entier.")
        elif len(s) <= 12 and " " not in s:
            c("EXERCICE_SOURCE_NON_LUE", "BLOQUANT", f"Exigence « {cle} » : la source {s} n'est pas inscrite au registre des sources.")

    # Voisins écartés.
    vois = [v for v in bloc.get("voisins_ecartes") or [] if isinstance(v, dict) and _texte(v.get("exercice"))]
    attendus = voisins_catalogue(e)
    examines = {_texte(v.get("exercice")) for v in vois if len(_texte(v.get("raison"))) >= 15}
    if not vois or not examines or (attendus and not examines & set(attendus)):
        c("EXERCICE_VOISIN_NON_EXAMINE", "BLOQUANT", "Aucun exercice voisin de la fiche n'est écarté avec sa raison "
          f"(voisins à examiner : {', '.join(attendus) or 'à identifier'}). Dire pour chacun le critère qui ferait basculer vers lui.")
    for v in vois:
        vid = _texte(v.get("exercice"))
        if vid not in catalogue and not vid.startswith("autre:"):
            c("EXERCICE_VOISIN_INCONNU", "ALERTE", f"Voisin « {vid} » : identifiant inconnu du catalogue (ou « autre:<libellé> »).")

    # Régime spécial : examiné, et appliqué quand il est déclaré.
    rs = bloc.get("regime_special")
    if not isinstance(rs, dict) or not isinstance(rs.get("applicable"), bool) or not _texte(rs.get("texte")):
        c("EXERCICE_REGIME_SPECIAL_NON_EXAMINE", "BLOQUANT", "Régime spécial non examiné (regime_special : applicable vrai ou faux, et texte lu, "
          "ou « droit commun » avec sa source). Un régime propre à la matière peut fixer une autre juridiction, un délai plus bref, "
          "un délai que le recours administratif ne proroge pas, une notification du recours ou une cristallisation.")
    elif rs.get("applicable") and _texte(rs.get("type_acte")) and type_acte and _texte(rs.get("type_acte")) != type_acte:
        c("EXERCICE_REGIME_SPECIAL_IGNORE", "BLOQUANT", f"Le régime spécial « {rs.get('type_acte')} » est déclaré applicable, mais l'acte est "
          f"contrôlé sous « {type_acte} » : ses conditions propres ne sont pas vérifiées.")

    # Acte destiné à protéger un délai : mode qui prouve la date, envoi avant l'échéance, matière où le recours proroge.
    envoi = bloc.get("envoi") if isinstance(bloc.get("envoi"), dict) else None
    protege = envoi is not None and _texte(envoi.get("but")) in BUTS_DELAI
    if ident == "recours_administratif_prealable" and envoi is None and (fiche.get("delai") or {}).get("echeance"):
        c("EXERCICE_DELAI_NON_PROTEGE", "BLOQUANT", "Recours administratif dont la fiche porte une échéance : le mode d'envoi, sa date et son but "
          "(champ envoi) ne sont pas fixés. Le recours ne protège le délai que s'il est expédié ou déposé avant l'échéance par un mode qui "
          "en prouve la date (CE, 30 juin 2025, n° 494573 ; fiche recours-administratifs-prealables.md).")
    if protege:
        mode = _texte(envoi.get("mode"))
        if mode not in MODES_DATES:
            c("EXERCICE_DELAI_NON_PROTEGE", "BLOQUANT", f"Envoi par « {mode or 'mode non dit'} » : il ne prouve pas la date d'expédition ou de dépôt. "
              f"Modes admis : {', '.join(sorted(MODES_DATES))}.")
        dp = L.date_simple(_texte(envoi.get("date_prevue")))
        ech = L.parse_date((fiche.get("delai") or {}).get("echeance"))
        if dp is None:
            c("EXERCICE_DELAI_NON_PROTEGE", "BLOQUANT", "Envoi sans date prévue (envoi.date_prevue, AAAA-MM-JJ).")
        elif ech is not None and dp > ech.date():
            c("EXERCICE_DELAI_NON_PROTEGE", "BLOQUANT", f"Envoi prévu le {dp}, après l'échéance du {ech.date()}.")
        if _texte(envoi.get("but")) == "proroger" and isinstance(rs, dict) and rs.get("proroge_par_recours_administratif") is False:
            c("EXERCICE_PROROGATION_EXCLUE", "BLOQUANT", "Le régime de la matière exclut la prorogation du délai par un recours administratif : "
              "seule la requête déposée dans le délai initial le protège.")
    return out


def _a_une_preuve(preuve) -> bool:
    p = preuve if isinstance(preuve, dict) else {}
    return bool(p.get("pieces") or p.get("faits") or p.get("sources"))


def _verifier_preuve(preuve, ctx: dict, c, prefixe: str, quoi: str) -> None:
    p = preuve if isinstance(preuve, dict) else {}
    pieces, faits, sources = [str(x) for x in p.get("pieces") or []], [str(x) for x in p.get("faits") or []], [str(x) for x in p.get("sources") or []]
    if not pieces and not faits:
        c(prefixe + "_ABSENTE", "BLOQUANT", f"{quoi} : aucune pièce du bordereau ni aucun fait de la matrice ne la prouve (preuve.pieces, "
          "preuve.faits). Une condition décisive se prouve sur pièces, datées de la date où le décideur statuera.")
    if ctx.get("bordereau") is not None:
        hors = [x for x in pieces if x not in ctx["bordereau"]]
        if hors:
            c(prefixe + "_HORS_DOSSIER", "BLOQUANT", f"{quoi} : pièces {hors} absentes du bordereau.")
    if ctx.get("matrice") is not None:
        hors = [x for x in faits if x not in ctx["matrice"]]
        if hors:
            c(prefixe + "_HORS_DOSSIER", "BLOQUANT", f"{quoi} : faits {hors} absents de preuves/matrice.json.")
    registre = ctx.get("sources")
    if registre is not None:
        for s in sources:
            if s not in registre or registre[s].get("lu_en_entier") is not True:
                c("EXERCICE_SOURCE_NON_LUE", "BLOQUANT", f"{quoi} : source {s} absente du registre ou non lue en entier.")


def premiere_page(texte: str) -> str:
    try:
        import lint_ecriture as LINT
        return LINT.premiere_page(texte)
    except ImportError:  # pragma: no cover
        return texte[:2600]


def _marque(motifs, texte: str) -> bool:
    for m in motifs or []:
        try:
            if re.search(m, texte, re.I):
                return True
        except re.error:
            continue
    return False


def controler(racine: Path, ecriture: Path, fiche: dict, texte: str, c) -> None:
    """Contrôle du diagnostic d'exercice d'une écriture, au format de gate.py (c(code, gravite, message, **extra)).

    Bloque une écriture juridictionnelle sans diagnostic complet ; pour un courrier, n'émet que des alertes, sauf l'envoi
    destiné à protéger un délai qui n'en prouve pas la date ou qui compte sur une prorogation exclue. En mode
    conservatoire (fiche.conservatoire), seuls restent bloquants l'exercice, le régime, la cible et le délai.
    """
    if not fiche:
        return
    catalogue = charger_catalogue()
    type_acte = fiche.get("type_acte")
    juridictionnel = bool(type_acte) and type_acte not in NON_JURIDICTIONNELS
    bloc = fiche.get("exercice")
    constats = valider(bloc, fiche, catalogue, contexte_dossier(racine))
    ident = _texte((bloc or {}).get("exercice")) if isinstance(bloc, dict) else ""
    e = catalogue.get(ident) or {}

    if isinstance(bloc, dict) and ident:
        # Diagnostic daté, postérieur au dernier apport du dossier.
        import controles_campagne as CAMPAGNE
        dt = CAMPAGNE.date_declaree(bloc.get("date"))
        apport, quoi = CAMPAGNE.dernier_apport(racine)
        if dt is None:
            constats.append({"code": "EXERCICE_DIAGNOSTIC_PERIME", "gravite": "BLOQUANT",
                             "message": "Diagnostic d'exercice sans date lisible (exercice.date, AAAA-MM-JJTHH:MM)."})
        elif apport and apport > dt:
            constats.append({"code": "EXERCICE_DIAGNOSTIC_PERIME", "gravite": "BLOQUANT",
                             "message": f"Diagnostic d'exercice antérieur au dernier apport du dossier ({quoi}) : le refaire à sa lumière et le redater."})
        # Cohérence avec la séquence : la voie retenue qui porte cette écriture désigne le même exercice.
        sq = L.lire_json(racine / "strategie/sequence.json") or {}
        racine_acte = ecriture.stem.split("_v")[0]
        for v in sq.get("voies", []) or []:
            if not isinstance(v, dict) or v.get("statut") != "retenue" or not _texte(v.get("exercice")):
                continue
            if any(racine_acte == str(x).split("_v")[0] for x in v.get("ecritures", []) or []) and _texte(v.get("exercice")) != ident:
                constats.append({"code": "EXERCICE_HORS_SEQUENCE", "gravite": "BLOQUANT",
                                 "message": f"La voie {v.get('id')} de la séquence porte cette écriture comme « {v.get('exercice')} » ; la fiche la "
                                            f"diagnostique comme « {ident} »."})
        # Le texte se présente comme l'exercice choisi, pas comme un voisin écarté.
        if juridictionnel and texte and e.get("marqueurs_texte"):
            page = premiere_page(texte)
            if not _marque(e["marqueurs_texte"], page):
                ecartes = [_texte(v.get("exercice")) for v in bloc.get("voisins_ecartes") or [] if isinstance(v, dict)]
                discordant = next((x for x in ecartes if _marque((catalogue.get(x) or {}).get("marqueurs_texte"), page)), None)
                if discordant:
                    constats.append({"code": "EXERCICE_TEXTE_DISCORDANT", "gravite": "BLOQUANT",
                                     "message": f"La première page se présente comme « {discordant} », exercice que le diagnostic écarte, et ne nomme "
                                                f"pas « {ident} » ni son texte fondateur."})
                else:
                    constats.append({"code": "EXERCICE_TEXTE_SANS_MARQUEUR", "gravite": "ALERTE",
                                     "message": f"La première page ne nomme pas l'exercice « {ident} » ni son texte fondateur : le juge doit savoir "
                                                "dès l'en-tête sur quel fondement il est saisi."})
        # Le juge simulé, qui identifie lui-même l'exercice dont il est saisi, le tient pour inadapté sur cette version.
        lf = L.lire_json(racine / "ecritures" / "controle" / f"{ecriture.stem}.lecture_froid.json")
        if (isinstance(lf, dict) and lf.get("exercice_adapte") is False and ecriture.is_file()
                and lf.get("sha256") == L.sha256_fichier(ecriture)):
            constats.append({"code": "EXERCICE_JUGE_SIMULE_AUTRE_EXERCICE", "gravite": "BLOQUANT",
                             "message": "Le juge simulé tient l'acte pour relevant d'un autre exercice ("
                                        f"{_texte(lf.get('exercice_qui_conviendrait'))[:160] or 'non précisé'}) : reprendre le diagnostic."})
        # Requête au fond dont le délai expire : le mode conservatoire évite de perdre le délai pour une pièce.
        delai = L.parse_date((fiche.get("delai") or {}).get("echeance"))
        if (juridictionnel and e.get("famille") in ("fond", "indemnitaire") and delai is not None and not isinstance(fiche.get("conservatoire"), dict)
                and timedelta(0) <= delai - L.maintenant() <= timedelta(hours=72)):
            constats.append({"code": "EXERCICE_CONSERVATOIRE_A_EXAMINER", "gravite": "ALERTE",
                             "message": f"Le délai expire le {(fiche.get('delai') or {}).get('echeance')} : si une pièce ou une lecture manque, déposer en "
                                        "mode conservatoire avec au moins un moyen plutôt que perdre le délai (skill controle-avant-depot, section 1 quater)."})

    conservatoire = isinstance(fiche.get("conservatoire"), dict)
    for k in constats:
        g = k["gravite"]
        if g == "BLOQUANT" and not juridictionnel and k["code"] not in TOUJOURS_BLOQUANTS:
            g = "ALERTE"
            k["message"] += " (alerte seulement : l'écrit n'est pas porté devant un juge)"
        elif g == "BLOQUANT" and conservatoire and k["code"] not in NON_DIFFERABLES:
            g = "ALERTE"
            k["message"] += " (différé : requête conservatoire, à traiter dans le mémoire complémentaire)"
        extra = {x: y for x, y in k.items() if x not in ("code", "gravite", "message")}
        c(k["code"], g, k["message"], **extra)


def _fiche_et_racine(chemin: Path) -> tuple[dict, Path | None]:
    fiche = L.lire_json(chemin)
    if not isinstance(fiche, dict):
        raise SystemExit(f"{chemin} : fiche illisible.")
    return fiche, L.trouver_racine(chemin)


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    cmd, args = argv[0], argv[1:]
    catalogue = charger_catalogue()
    if cmd == "liste":
        for i, e in sorted(catalogue.items()):
            print(f"{i:<34} {e.get('famille', ''):<22} {e.get('fichier')}  [{', '.join(e.get('types_acte') or []) or 'aucun régime'}]")
        return 0
    if cmd in ("fiche", "squelette") and args:
        if args[0] not in catalogue:
            print(f"Exercice inconnu : {args[0]}. Identifiants : {', '.join(sorted(catalogue))}.")
            return 1
        if cmd == "fiche":
            e = catalogue[args[0]]
            print(f"Fiche : {REFERENCES / e['fichier']}")
            print(json.dumps({k: v for k, v in e.items() if k != "fichier"}, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(squelette(args[0], catalogue), ensure_ascii=False, indent=2))
        return 0
    if cmd == "valider" and args:
        chemin = Path(args[0]).resolve()
        fiche, racine = _fiche_et_racine(chemin)
        constats = valider(fiche.get("exercice"), fiche, catalogue, contexte_dossier(racine))
    elif cmd == "controle" and args:
        ecriture = Path(args[0]).resolve()
        racine = L.trouver_racine(ecriture)
        if racine is None:
            raise SystemExit(f"{ecriture} n'est pas dans un dossier d'affaire.")
        fiche = L.lire_json(racine / "ecritures" / "controle" / f"{ecriture.stem}.fiche.json") or {}
        constats = []
        controler(racine, ecriture, fiche, ecriture.read_text(encoding="utf-8") if ecriture.is_file() else "",
                  lambda code, gravite, message, **extra: constats.append({"code": code, "gravite": gravite, "message": message}))
    else:
        print(__doc__)
        return 2
    for k in constats:
        print(f"- {k['gravite']} {k['code']} : {k['message']}")
    bloquants = sum(1 for k in constats if k["gravite"] == "BLOQUANT")
    print(f"Diagnostic d'exercice : {bloquants} bloquant(s), {len(constats) - bloquants} alerte(s).")
    return 1 if bloquants else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
