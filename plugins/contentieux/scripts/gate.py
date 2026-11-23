"""Contrôle avant dépôt d'une écriture contentieuse.

Usage : python gate.py <ecriture.md> [--json]

Le contrôle lit la fiche de l'acte (ecritures/controle/<nom>.fiche.json), le registre des sources,
le bordereau, les objections, la lecture à froid et la contradiction. Il écrit son verdict dans
ecritures/controle/<nom>.gate.json, lié à l'empreinte exacte du texte contrôlé. Seul ce script
écrit ce fichier ; le hook PreToolUse interdit de le modifier à la main.

Un verdict PASS signifie que les verrous mécaniques sont satisfaits. Il n'atteste ni la justesse
juridique ni l'issue.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib_affaire as L  # noqa: E402
import lint_ecriture as LINT  # noqa: E402
import controles_campagne as CAMPAGNE  # noqa: E402

# Conditions de fond exigées par régime. Chaque condition doit être rattachée à des faits datés,
# à des pièces et à une source lue en entier. Les noms sont ceux qu'emploie la fiche.
REGIMES = {
    "refere_suspension": {"juge": "admin", "refere": True, "acte": True, "fond_distinct": True,
                          "conditions": ["urgence", "doute_serieux"],
                          "texte": "CJA, art. L. 521-1, L. 522-3, R. 522-1"},
    "refere_liberte": {"juge": "admin", "refere": True, "acte": False, "fond_distinct": False,
                       "conditions": ["urgence_particuliere", "liberte_fondamentale", "atteinte_grave_manifestement_illegale"],
                       "texte": "CJA, art. L. 521-2, L. 522-3, L. 523-1"},
    "refere_mesures_utiles": {"juge": "admin", "refere": True, "acte": False, "fond_distinct": False,
                              "conditions": ["urgence", "utilite", "absence_obstacle_a_une_decision"],
                              "texte": "CJA, art. L. 521-3"},
    "refere_provision_admin": {"juge": "admin", "refere": True, "acte": False, "fond_distinct": False,
                               "conditions": ["obligation_non_serieusement_contestable"], "texte": "CJA, art. R. 541-1"},
    "refere_instruction_admin": {"juge": "admin", "refere": True, "acte": False, "fond_distinct": False,
                                 "conditions": ["utilite_de_la_mesure"], "texte": "CJA, art. R. 532-1"},
    "refere_civil_834": {"juge": "judiciaire", "refere": True, "acte": False, "fond_distinct": False,
                         "conditions": ["urgence", "absence_de_contestation_serieuse_ou_differend"],
                         "texte": "CPC, art. 834"},
    "refere_civil_835_1": {"juge": "judiciaire", "refere": True, "acte": False, "fond_distinct": False,
                           "conditions": ["trouble_manifestement_illicite_ou_dommage_imminent"], "texte": "CPC, art. 835, al. 1"},
    "refere_civil_835_2": {"juge": "judiciaire", "refere": True, "acte": False, "fond_distinct": False,
                           "conditions": ["obligation_non_serieusement_contestable"], "texte": "CPC, art. 835, al. 2"},
    "refere_145": {"juge": "judiciaire", "refere": True, "acte": False, "fond_distinct": False,
                   "conditions": ["motif_legitime", "absence_de_proces_au_fond", "mesure_legalement_admissible"],
                   "texte": "CPC, art. 145"},
    "requete_fond_admin": {"juge": "admin", "refere": False, "acte": True, "fond_distinct": False,
                           "conditions": ["recevabilite_et_delai", "interet_a_agir", "decision_faisant_grief"],
                           "texte": "CJA, art. R. 411-1, R. 421-1"},
    "assignation": {"juge": "judiciaire", "refere": False, "acte": False, "fond_distinct": False,
                    "conditions": ["competence", "interet_et_qualite", "fondement_de_la_pretention"],
                    "texte": "CPC, art. 54, 56, 31, 122"},
    "conclusions": {"juge": "variable", "refere": False, "acte": False, "fond_distinct": False, "conditions": [], "texte": ""},
    "pourvoi_cassation": {"juge": "variable", "refere": False, "acte": True, "fond_distinct": False,
                          "conditions": ["recevabilite_et_delai", "representation_obligatoire", "cas_d_ouverture"],
                          "texte": "CPC, art. 973 et s. ; CJA, art. L. 821-1, L. 822-1"},
    "courrier_precontentieux": {"juge": "aucun", "refere": False, "acte": False, "fond_distinct": False, "conditions": [], "texte": ""},
}

def charger_regimes_domaines() -> int:
    """Ajoute les régimes vérifiés livrés par domaine (references/domaines/*_regimes.json)."""
    n = 0
    dossier = Path(__file__).resolve().parents[1] / "references" / "domaines"
    for f in sorted(dossier.glob("*_regimes.json")) if dossier.is_dir() else []:
        try:
            entrees = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for e in entrees if isinstance(entrees, list) else []:
            t = e.get("type_acte")
            if not t or not isinstance(e.get("conditions"), list):
                continue
            base = REGIMES.get(t, {})
            conditions = list(base.get("conditions", [])) + [c for c in e["conditions"] if c not in base.get("conditions", [])]
            REGIMES[t] = {**base, "juge": e.get("juge", base.get("juge", "variable")),
                          "refere": bool(e.get("refere", base.get("refere"))), "acte": bool(e.get("acte", base.get("acte"))),
                          "fond_distinct": bool(e.get("fond_distinct", base.get("fond_distinct"))), "conditions": conditions,
                          "texte": e.get("texte", base.get("texte", "")), "domaine": e.get("domaine", ""),
                          "pieges": e.get("pieges", []), "source_fichier": f.name}
            n += 1
    return n



def categories_conditions() -> dict:
    """Sanction qu'entraîne le défaut de chaque condition (references/domaines/categories_conditions.json)."""
    return L.lire_json(Path(__file__).resolve().parents[1] / "references" / "domaines" / "categories_conditions.json", {}) or {}


QUALIFICATIONS_DECISOIRES = {"decision_expresse", "decision_implicite"}
QUALIFICATIONS_NON_DECISOIRES = {"confirmative", "preparatoire", "information", "mesure_ordre_interieur", "refus_de_rendez_vous"}


def chemins(ecriture: Path, racine: Path) -> dict:
    stem = ecriture.stem
    ctrl = racine / "ecritures" / "controle"
    return {k: ctrl / f"{stem}.{k}.json" for k in ("fiche", "lecture_froid", "rapport_rapporteur", "contradiction", "gate")}


def controler(ecriture: Path) -> dict:
    charger_regimes_domaines()
    racine = L.trouver_racine(ecriture)
    if racine is None:
        raise SystemExit(f"{ecriture} n'est pas dans un dossier d'affaire (etat/affaire.json introuvable).")
    texte = ecriture.read_text(encoding="utf-8")
    empreinte = L.sha256_fichier(ecriture)
    ch = chemins(ecriture, racine)
    affaire = L.lire_json(racine / "etat/affaire.json", {}) or {}
    consignes = affaire.get("consignes", {}) or {}
    sources = {s.get("id"): s for s in (L.lire_json(racine / "etat/sources.json", {}) or {}).get("sources", [])}
    bordereau = {str(p.get("cote")) for p in (L.lire_json(racine / "pieces/bordereau.json", {}) or {}).get("pieces", [])}
    fiche = L.lire_json(ch["fiche"])
    constats: list[dict] = []

    def c(code, gravite, message, **extra):
        constats.append({"code": code, "gravite": gravite, "message": message, **extra})

    if fiche is None:
        c("FICHE_ABSENTE", "BLOQUANT", f"Fiche de l'acte absente ou illisible : {(L.relatif(racine, ch['fiche']) or ch['fiche'].as_posix())}. "
          "Elle fixe le régime, l'acte attaqué, la question, les conditions, les moyens et les conclusions (skill controle-avant-depot).")
        fiche = {}
    type_acte = fiche.get("type_acte")
    regime = REGIMES.get(type_acte or "", None)
    if fiche and regime is None:
        c("REGIME_INCONNU", "BLOQUANT", f"type_acte « {type_acte} » inconnu ; valeurs : {', '.join(sorted(REGIMES))}.")
        regime = {"juge": "variable", "refere": False, "acte": False, "fond_distinct": False, "conditions": [], "texte": ""}
    regime = regime or REGIMES["conclusions"]
    refere = regime["refere"]

    def source_lue(sid) -> bool:
        s = sources.get(sid)
        return bool(s and s.get("lu_en_entier") is True)

    # Question unique et lisible en première page.
    question = (fiche.get("question") or "").strip()
    page1 = LINT.premiere_page(texte)
    if fiche and not question:
        c("QUESTION_ABSENTE", "BLOQUANT", "La fiche ne formule pas la question soumise au juge en une phrase.")
    elif question and LINT.recouvrement(question, page1) < 0.5:
        c("QUESTION_HORS_PREMIERE_PAGE", "BLOQUANT" if refere else "ALERTE",
          "La question de la fiche ne se retrouve pas dans la première page du texte : le lecteur pressé ne la verra pas.")

    fait_decisif = (fiche.get("fait_decisif") or "").strip()
    if refere and fiche and not fait_decisif:
        c("FAIT_DECISIF_ABSENT", "BLOQUANT", "La fiche ne nomme pas le fait décisif (champ fait_decisif), qui doit figurer en première page.")
    elif fait_decisif and LINT.recouvrement(fait_decisif, page1) < 0.5:
        c("FAIT_DECISIF_TARDIF", "BLOQUANT" if refere else "ALERTE",
          "Le fait décisif n'apparaît pas en première page : le juge écrira son premier considérant avec ce qu'il lit d'abord.")

    # Au tri, le juge ne lit souvent que la première page et le dispositif : l'urgence doit y être datée.
    if refere and any(c_ in regime["conditions"] for c_ in ("urgence", "urgence_particuliere")):
        up = (fiche.get("urgence_premiere_page") or "").strip()
        if not up:
            c("URGENCE_PREMIERE_PAGE_ABSENTE", "BLOQUANT", "La fiche ne donne pas la phrase d'urgence datée qui doit figurer en première page (champ urgence_premiere_page).")
        elif LINT.recouvrement(up, page1) < 0.5:
            c("URGENCE_HORS_PREMIERE_PAGE", "BLOQUANT", "L'urgence n'apparaît pas en première page : un juge qui trie sur la première page et le dispositif ne la verra pas.")

    # Termes internes visibles dans le texte ou dans les pièces transmises (noms d'assistants, versions, codes de travail).
    termes = consignes.get("termes_internes") or ["Codex", "Claude", "ChatGPT", "GPT", "brouillon", "draft", "Phase", "huis clos", "ENS"]
    import re as _re
    corps_net = LINT._hors_citations(texte)
    for t in termes:
        m = _re.search(r"\b" + _re.escape(t) + r"\b", corps_net)
        if m:
            c("TERME_INTERNE_TEXTE", "BLOQUANT", f"Terme interne « {t} » dans le texte destiné au juge.", ligne=LINT._ligne(texte, m.start()))
    for p in (L.lire_json(racine / "pieces/bordereau.json", {}) or {}).get("pieces", []):
        if str(p.get("cote")) not in {str(x) for x in LINT.analyser(texte).pieces_citees}:
            continue
        visible = f"{Path(str(p.get('fichier', ''))).name} {p.get('intitule_depot', '')}"
        for t in termes:
            if _re.search(r"\b" + _re.escape(t) + r"\b", visible, _re.I):
                c("TERME_INTERNE_PIECE", "BLOQUANT", f"Pièce {p.get('cote')} : le nom transmis contient « {t} » ({visible.strip()[:80]}).")

    # Acte attaqué : nature décisoire, date, et opérance des faits invoqués.
    actes = fiche.get("actes_attaques") or ([fiche["acte_attaque"]] if fiche.get("acte_attaque") else [])
    if regime["acte"] and fiche and not actes:
        c("ACTE_ABSENT", "BLOQUANT", "Le régime exige un acte attaqué ; la fiche n'en désigne aucun.")
    if refere and len(actes) > 1 and not fiche.get("justification_pluralite_actes"):
        c("PLURALITE_ACTES", "BLOQUANT", f"{len(actes)} actes attaqués dans un référé sans justification écrite de la pluralité "
          "(justification_pluralite_actes). Chaque acte supplémentaire ajoute ses objections propres.")
    dates_actes = {}
    for a in actes:
        ident = a.get("id") or a.get("designation") or "?"
        q = a.get("qualification")
        if q in QUALIFICATIONS_NON_DECISOIRES:
            c("ACTE_NON_DECISOIRE", "BLOQUANT", f"Acte « {ident} » qualifié « {q} » : il ne fait pas grief ou ne fait que confirmer ; "
              "attaquer la décision de l'autorité compétente, ou la provoquer (skill action-sur-le-reel).")
        elif q not in QUALIFICATIONS_DECISOIRES:
            c("ACTE_NON_QUALIFIE", "BLOQUANT", f"Acte « {ident} » : qualification absente ou inconnue (decision_expresse, decision_implicite, "
              f"{', '.join(sorted(QUALIFICATIONS_NON_DECISOIRES))}).")
        if not a.get("justification") or not any(source_lue(s) for s in a.get("sources", [])):
            c("ACTE_QUALIFICATION_NON_SOURCEE", "BLOQUANT", f"Acte « {ident} » : qualification sans justification ni source lue en entier.")
        d = L.date_simple(a.get("date"))
        if d is None:
            c("ACTE_SANS_DATE", "BLOQUANT", f"Acte « {ident} » sans date (AAAA-MM-JJ) ; la légalité s'apprécie à cette date.")
        else:
            dates_actes[ident] = d
        if a.get("auteur_competent") is False:
            c("AUTEUR_INCOMPETENT", "ALERTE", f"Acte « {ident} » émane d'un auteur que la fiche dit incompétent : vérifier que l'acte attaqué est le bon.")

    # Conditions du régime.
    conds = {x.get("condition"): x for x in fiche.get("conditions", [])}
    cats = categories_conditions()
    for nom in regime["conditions"]:
        x = conds.get(nom)
        k = {"condition": nom, "categorie": cats.get(nom, "mal_fonde")}
        if x is None:
            c("CONDITION_NON_TRAITEE", "BLOQUANT", f"Condition « {nom} » ({regime['texte']}) absente de la fiche.", **k)
            continue
        etat = x.get("etat")
        faits = x.get("faits") or []
        if etat == "absente":
            c("CONDITION_ABSENTE", "BLOQUANT", f"Condition « {nom} » déclarée absente : l'acte ne peut pas partir en l'état.", **k)
        elif etat == "fragile" and not x.get("objection"):
            c("CONDITION_FRAGILE", "BLOQUANT", f"Condition « {nom} » fragile sans objection inscrite au registre ni parade (champ objection).", **k)
        elif etat == "fragile":
            c("CONDITION_FRAGILE_ASSUMEE", "ALERTE", f"Condition « {nom} » fragile, objection {x.get('objection')} inscrite : risque de {k['categorie']}.", **k)
        elif etat not in ("etablie", "fragile"):
            c("CONDITION_ETAT", "BLOQUANT", f"Condition « {nom} » : état « {etat} » inconnu (etablie, fragile, absente).", condition=nom)
        if not faits or not all(f.get("pieces") for f in faits):
            c("CONDITION_SANS_PREUVE", "BLOQUANT", f"Condition « {nom} » : chaque fait doit être rattaché à une pièce.", condition=nom)
        if not any(source_lue(s) for s in x.get("sources", [])):
            c("CONDITION_SANS_SOURCE", "BLOQUANT", f"Condition « {nom} » : aucun critère jurisprudentiel ou texte lu en entier n'est rattaché.", condition=nom)

    if regime["fond_distinct"]:
        fd = fiche.get("requete_fond_distincte") or fiche.get("recours_prealable_obligatoire") or {}
        if not (fd.get("reference") and fd.get("piece")):
            c("REQUETE_FOND_DISTINCTE", "BLOQUANT", "Référé-suspension : la requête au fond distincte (référence) et sa copie en pièce sont exigées (R. 522-1 CJA), ou, quand un recours administratif préalable obligatoire précède le juge, la copie de ce recours formé (champ recours_prealable_obligatoire).")

    # Moyens : opérance au regard de la date de l'acte (contentieux de la légalité).
    for mo in fiche.get("moyens", []):
        nom = mo.get("intitule", "?")
        if not any(source_lue(s) for s in mo.get("sources", [])):
            c("MOYEN_SANS_SOURCE", "BLOQUANT", f"Moyen « {nom} » : aucune règle lue en entier n'est rattachée.")
        if regime["juge"] == "admin" and regime["acte"]:
            cibles = mo.get("actes_vises") or list(dates_actes)
            for fa in mo.get("faits", []):
                df = L.date_simple(fa.get("date"))
                if df is None:
                    continue
                for cible in cibles:
                    da = dates_actes.get(cible)
                    if da and df > da and not mo.get("admet_faits_posterieurs"):
                        c("MOYEN_INOPERANT_DATE", "BLOQUANT",
                          f"Moyen « {nom} » : le fait « {fa.get('fait', '')[:80]} » ({df}) est postérieur à l'acte « {cible} » ({da}). "
                          "La légalité s'apprécie à la date de l'acte ; ce fait ne peut rien contre lui. Attaquer l'acte postérieur, "
                          "ou justifier (admet_faits_posterieurs + source).")
            if mo.get("admet_faits_posterieurs") and not mo.get("justification_faits_posterieurs"):
                c("FAITS_POSTERIEURS_NON_JUSTIFIES", "BLOQUANT", f"Moyen « {nom} » : admet_faits_posterieurs sans justification sourcée.")

    # Conclusions accordables.
    for i, cl in enumerate(fiche.get("conclusions", []), 1):
        if not cl.get("pouvoir_du_juge"):
            c("CONCLUSION_SANS_POUVOIR", "BLOQUANT" if refere else "ALERTE",
              f"Conclusion {i} : la fiche ne dit pas sur quel pouvoir du juge elle repose ni pourquoi il peut l'ordonner à ce stade.")

    # Délai.
    delai = fiche.get("delai") or {}
    dt = L.parse_date(delai.get("echeance"))
    if fiche and dt is None and type_acte not in ("conclusions", "courrier_precontentieux"):
        c("DELAI_ABSENT", "BLOQUANT", "Échéance de dépôt absente de la fiche (date, règle, point de départ).")
    elif dt is not None:
        h = (dt - L.maintenant()).total_seconds() / 3600
        if h < 0:
            c("DELAI_DEPASSE", "BLOQUANT", f"Échéance {delai.get('echeance')} dépassée.", categorie="delai_tardivete")
        elif h < 24:
            c("DELAI_IMMINENT", "ALERTE", f"Échéance dans {h:.0f} h ({delai.get('echeance')}).")
        if not delai.get("regle") or not delai.get("point_de_depart"):
            c("DELAI_NON_FONDE", "BLOQUANT", "Échéance sans règle ou sans point de départ vérifié.")
    # Recalcul indépendant : l'échéance déclarée ne vaut que si voies.py, depuis l'événement de la chronologie, ne trouve pas plus tôt.
    if delai.get("evenement"):
        import voies
        evts = {e.get("id"): e for e in (L.lire_json(racine / "chronologie/chronologie.json", {}) or {}).get("evenements", [])}
        ev = evts.get(delai["evenement"])
        if ev is None:
            c("DELAI_EVENEMENT_INCONNU", "BLOQUANT", f"Événement « {delai['evenement']} » absent de chronologie/chronologie.json.")
        else:
            filtre = (delai.get("regle_calcul") or "").lower()
            calc = [r for r in voies.calculer_evenement(ev) if not filtre or filtre in (r["libelle"] + " " + r["regle"]).lower()]
            if not calc:
                c("DELAI_NON_CALCULABLE", "ALERTE", f"Aucune règle de voies.py ne s'applique à l'événement « {delai['evenement']} » "
                  f"(type « {ev.get('type')} ») : échéance déclarée non recoupée.")
            else:
                r = min(calc, key=lambda x: x["date"])
                fin = L.date_simple(r["date"])
                if dt is None or fin < dt.date():
                    c("DELAI_MAL_CALCULE", "BLOQUANT", f"voies.py calcule {fin} ({r['libelle']} ; {r['regle']} ; départ {r['point_de_depart']}), "
                      f"plus tôt que l'échéance déclarée {delai.get('echeance')}.", categorie="delai_tardivete")
                if L.maintenant().date() > fin:
                    c("DELAI_DEPASSE", "BLOQUANT", f"Échéance calculée {fin} dépassée ({r['libelle']} ; {r['regle']}). Effet : {r['effet'][:200]}",
                      categorie="delai_tardivete")

    # Lecture mécanique du texte.
    numeros_propres = {str(i.get("numero", "")) for i in affaire.get("instances", []) if i.get("numero")}
    numeros_propres |= {str(n) for n in fiche.get("numeros_non_jurisprudentiels", [])}
    rap = LINT.analyser(texte, refere=refere, texte_client=bool(fiche.get("au_nom_du_client", True)),
                        ponctuation_interdite=consignes.get("ponctuation_interdite_textes_client"),
                        numeros_propres=numeros_propres)
    for k in rap.constats:
        constats.append({"code": k.code, "gravite": k.gravite, "message": k.message, "extrait": k.extrait, "ligne": k.ligne})

    par_numero = {}
    for s in sources.values():
        if s.get("numero"):
            par_numero[str(s["numero"]).replace(" ", "")] = s
    for dcit in rap.decisions_citees:
        s = par_numero.get(dcit["numero"])
        if s is None:
            c("CITATION_HORS_REGISTRE", "BLOQUANT", f"Décision n° {dcit['numero']} (ligne {dcit['ligne']}) absente du registre des sources.")
        elif s.get("lu_en_entier") is not True:
            c("CITATION_NON_LUE", "BLOQUANT", f"Décision n° {dcit['numero']} inscrite mais non lue en entier.")
    for interdite in consignes.get("citations_interdites", []):
        if interdite and interdite in texte:
            c("CITATION_INTERDITE", "BLOQUANT", f"Citation interdite par les consignes de l'affaire : {interdite}.")
    import re
    for motif in consignes.get("affirmations_interdites", []):
        m = re.search(motif, texte, re.I)
        if m:
            c("AFFIRMATION_INTERDITE", "BLOQUANT", f"Affirmation interdite par les consignes de l'affaire : « {m.group(0)} ».",
              ligne=LINT._ligne(texte, m.start()))
    manquantes = [p for p in rap.pieces_citees if str(p) not in bordereau]
    if manquantes:
        c("PIECE_HORS_BORDEREAU", "BLOQUANT", f"Pièces citées absentes du bordereau : {manquantes[:30]}.")
    articles_registre = " ".join(str(s.get("reference", "")) for s in sources.values() if s.get("lu_en_entier"))
    for art in rap.articles_cites:
        noyau = art.replace(" ", "").replace(".", "")
        if noyau and noyau not in articles_registre.replace(" ", "").replace(".", ""):
            c("ARTICLE_HORS_REGISTRE", "ALERTE", f"Article {art} cité sans entrée lue au registre des sources.")

    # Tout acte porté devant un juge (régimes intégrés et régimes de domaine), sauf le courrier précontentieux.
    juridictionnel = refere or regime.get("juge") not in ("aucun", None)

    # Le réel d'abord : canaux de notification relevés et audit de terrain récent avant toute écriture juridictionnelle.
    if juridictionnel:
        for canal, age in L.canaux_perimes(racine):
            c("CANAL_NON_CONTROLE", "BLOQUANT", f"Canal « {canal.get('nom')} » {'jamais contrôlé' if age is None else f'non contrôlé depuis {age / 24:.1f} j'} : "
              "une décision, une convocation ou une défense peut y attendre, avec un délai qui court déjà. "
              "Relever le canal, puis affaire.py canal controle.")
        audit = L.lire_json(racine / "terrain/audit.json")
        if not audit:
            c("AUDIT_TERRAIN_ABSENT", "BLOQUANT", "terrain/audit.json absent : audit du réel (skill action-sur-le-reel) obligatoire avant une écriture juridictionnelle.")
        else:
            da = L.parse_date(audit.get("date"))
            age_j = None if da is None else (L.maintenant() - da).total_seconds() / 86400
            limite = 3 if refere else 14
            if age_j is None or age_j > limite:
                c("AUDIT_TERRAIN_PERIME", "BLOQUANT", f"Audit de terrain {'sans date' if age_j is None else f'vieux de {age_j:.0f} jours'} (limite {limite} jours pour cet acte).")
            for champ in ("evidences_verifiees", "lacunes", "actions_decidees"):
                if not isinstance(audit.get(champ), list):
                    c("AUDIT_TERRAIN_INCOMPLET", "BLOQUANT", f"terrain/audit.json : champ « {champ} » absent (liste attendue, même vide).")

    # La ligne avant les actes : ligne écrite, complète, postérieure aux pièces les plus récentes utilisées.
    if juridictionnel:
        ligne = L.lire_json(racine / "strategie/ligne.json")
        champs_ligne = ("objectif", "decideur", "lecture_adversaire", "levier", "meilleur_coup_adverse", "parade", "temps_reel", "chemin_de_victoire")
        if not ligne:
            c("LIGNE_ABSENTE", "BLOQUANT", "strategie/ligne.json absent : la ligne s'écrit avant les actes (skill strategie-contentieuse).")
        else:
            for champ in champs_ligne:
                if not ligne.get(champ):
                    c("LIGNE_INCOMPLETE", "BLOQUANT", f"Ligne stratégique : champ « {champ} » vide.")
            dl = L.parse_date(ligne.get("date"))
            pieces_b = {str(p.get("cote")): p for p in (L.lire_json(racine / "pieces/bordereau.json", {}) or {}).get("pieces", [])}
            recentes = [L.parse_date(pieces_b[str(n)].get("ajoutee_le", "").replace(" ", "T")[:16]) for n in LINT.analyser(texte).pieces_citees if str(n) in pieces_b]
            recentes = [d for d in recentes if d]
            if dl and recentes and max(recentes) > dl:
                c("LIGNE_PERIMEE", "BLOQUANT", "Une pièce citée a été ajoutée après la dernière révision de la ligne : relire la ligne à sa lumière et la redater.")

    # La charpente : revue de l'architecture entière du dossier, postérieure à la ligne et couvrant cet acte.
    if juridictionnel:
        rc = L.lire_json(racine / "strategie/revue_charpente.json")
        if not rc:
            c("REVUE_CHARPENTE_ABSENTE", "BLOQUANT", "Aucune revue de charpente (sous-agent architecte-strategique) : l'acte n'a pas été jugé dans l'architecture du dossier.")
        else:
            lg = L.lire_json(racine / "strategie/ligne.json") or {}
            # Une revue datée sans heure compte du début du jour : elle ne vaut pas pour une ligne révisée le même jour.
            drs = str(rc.get("date") or "")
            dl, dr = L.parse_date(lg.get("date")), L.parse_date(drs + "T00:00" if len(drs) == 10 else drs)
            if dl and dr and dr < dl and lg.get("revue_charpente_appliquee") != rc.get("date"):
                c("REVUE_CHARPENTE_PERIMEE", "BLOQUANT", "La ligne a été révisée après la dernière revue de charpente.")
            couverts = [str(x) for x in rc.get("actes_couverts", [])]
            racine_acte = ecriture.stem.split("_v")[0]
            if "*" not in couverts and not any(racine_acte in x or x in ecriture.stem for x in couverts):
                c("REVUE_CHARPENTE_HORS_ACTE", "BLOQUANT", f"La revue de charpente ne couvre pas l'acte {ecriture.stem}.")
            for p in rc.get("points", []):
                if p.get("gravite") == "dirimante" and p.get("statut") not in ("applique", "rejete_motive"):
                    c("CHARPENTE_DIRIMANTE_OUVERTE", "BLOQUANT", f"Point {p.get('id')} de la revue de charpente non tranché : {str(p.get('constat', p.get('objet', '')))[:200]}")
            CAMPAGNE.controler_revue_campagne(racine, rc, c)

    # La campagne : vérité et théorie de l'affaire établies sur pièces, séquence conçue depuis le premier acte adverse.
    if juridictionnel:
        CAMPAGNE.controler_theorie(racine, ecriture, c)
        CAMPAGNE.controler_sequence(racine, ecriture, fiche, c)
        if refere and regime.get("juge") == "admin":
            CAMPAGNE.controler_urgence(fiche, c)
        CAMPAGNE.controler_competence(racine, regime, c)

    # Les décideurs : profil de la juridiction qui recevra l'acte et de l'institution adverse, et lecture à froid rendue
    # sur ce profil (skill lecture-des-decideurs ; structure et règles dans decideurs.py).
    if juridictionnel:
        import decideurs as DECIDEURS
        DECIDEURS.controler(racine, ecriture, fiche, c)

    # La négociation : une voie amiable examinée avec la solution de repli de chaque partie avant tout acte juridictionnel,
    # sauf urgence motivée dans la fiche ; aucun chiffre de la négociation dans l'écrit (skill negociation-et-persuasion).
    import negociation as NEGOCIATION
    NEGOCIATION.controler(racine, ecriture, fiche, c, juridictionnel=juridictionnel, texte=texte)

    # L'exercice : sa mécanique propre diagnostiquée avant la production (juge et stade, condition décisive et sa preuve,
    # cible, exigences implicites, voisin écarté), et l'envoi qui doit protéger un délai (skill mecanique-des-exercices).
    import exercices as EXERCICES
    EXERCICES.controler(racine, ecriture, fiche, texte, c)

    # Les positions tenues devant le client : chacune a son fondement et ce qui la ferait changer, et une révision nomme
    # l'élément nouveau qui la cause, jamais un simple désaccord (skill rapport-de-force, section 5).
    import positions as POSITIONS
    POSITIONS.controler(racine, c)

    # La doctrine : chaque travail cité a sa fiche de lecture valide ; aucune citation entre guillemets d'un travail non lu ;
    # aucune règle fondée sur la seule doctrine (skill recherche-doctrinale ; règles dans doctrine.py). Bloquant devant un juge,
    # alerte pour un courrier.
    import doctrine as DOCTRINE
    DOCTRINE.controler(racine, ecriture, fiche, c, juridictionnel=juridictionnel)

    # Le récit : théorie du cas écrite et éprouvée par un lecteur profane sur la version exacte.
    if juridictionnel:
        recit = L.lire_json(racine / "ecritures/controle" / f"{ecriture.stem}.recit.json")
        if not recit:
            c("RECIT_ABSENT", "BLOQUANT", f"ecritures/controle/{ecriture.stem}.recit.json absent (skill recit-judiciaire).")
        else:
            for champ in ("theorie_du_cas", "fil", "neutralisation_adverse", "pourquoi_accorder_est_sur"):
                if not recit.get(champ):
                    c("RECIT_INCOMPLET", "BLOQUANT", f"Récit : champ « {champ} » vide.")
        lp = L.lire_json(racine / "ecritures/controle" / f"{ecriture.stem}.lecture_profane.json")
        if lp is None:
            c("LECTURE_PROFANE_ABSENTE", "BLOQUANT", "Aucune lecture par le sous-agent lecteur-profane.")
        elif lp.get("sha256") != empreinte:
            c("LECTURE_PROFANE_PERIMEE", "BLOQUANT", "La lecture profane porte sur une autre version du texte.")
        else:
            if lp.get("a_compris_la_demande") is not True:
                c("LECTURE_PROFANE_DEMANDE", "BLOQUANT", "Le lecteur profane n'a pas compris ce qui est demandé.")
            if fait_decisif and LINT.recouvrement(fait_decisif, str(lp.get("restitution", ""))) < 0.3:
                c("LECTURE_PROFANE_FAIT_DECISIF", "BLOQUANT", "La restitution du lecteur profane ne contient pas le fait décisif : le récit ne le porte pas.")

    # Déclarations de l'adversaire : un moyen qui s'en sert exige le paragraphe entier et les autres pièces du même auteur.
    registre_adv = {d.get("id"): d for d in (L.lire_json(racine / "adverse/declarations.json", {}) or {}).get("declarations", [])}
    for mo in fiche.get("moyens", []):
        attaquees = set(mo.get("declarations_attaquees", []))
        for did in list(mo.get("declarations_adverses", [])) + sorted(attaquees):
            d = registre_adv.get(did)
            if d is None:
                c("DECLARATION_ADVERSE_HORS_REGISTRE", "BLOQUANT", f"Moyen « {mo.get('intitule', '?')} » : déclaration {did} absente de adverse/declarations.json.")
                continue
            if len(str(d.get("paragraphe_complet", ""))) < 80 or not d.get("pieces_meme_auteur_lues"):
                c("DECLARATION_ADVERSE_HORS_CONTEXTE", "BLOQUANT", f"Déclaration {did} : paragraphe entier ou autres pièces du même auteur non lus. "
                  "Une citation exacte sortie de son contexte fait tomber le moyen.")
            contra = d.get("contredite_par_pieces_adverses") or []
            contra = [contra] if isinstance(contra, str) else contra
            contra = [x for x in contra if not re.search(r"aucune contradiction|écart", str(x), re.I)]
            if contra and did not in attaquees:
                c("DECLARATION_ADVERSE_CONTREDITE", "BLOQUANT", f"Déclaration {did} : d'autres pièces de l'adversaire la contredisent ({str(contra)[:200]}). Revoir le moyen.")

    # Pièces décisives de la matrice probatoire laissées hors du texte.
    for f_ in (L.lire_json(racine / "preuves/matrice.json", {}) or {}).get("faits_a_prouver", []):
        if f_.get("force") == "forte" and ecriture.stem.split("_v")[0] in (f_.get("actes") or []) and not set(map(str, f_.get("pieces", []))) & {str(p) for p in LINT.analyser(texte).pieces_citees}:
            c("PIECE_DECISIVE_OMISE", "ALERTE", f"Fait à prouver « {f_.get('fait', '')[:80]} » : aucune de ses pièces fortes n'est citée.")

    # Analyse documentaire : un fait que l'écriture présente comme décisif renvoie, dans la matrice, à un extrait
    # littéral d'une pièce analysée ; une pièce citée sans fiche d'analyse donne une alerte (skill analyse-documentaire).
    import pieces as PIECES
    # Un courrier à l'adversaire ou à une autorité n'est pas jugé sur pièces : le défaut de preuve y reste une alerte.
    for k in PIECES.controle_documentaire(racine, ecriture, fiche, texte):
        if not juridictionnel and k.get("gravite") == "BLOQUANT":
            k = {**k, "gravite": "ALERTE", "message": k["message"] + " (alerte seulement : l'écrit n'est pas porté devant un juge)"}
        constats.append(k)

    # Lectures : décision citée jamais lue au registre des lectures, citation introuvable mot pour mot, décision défaite par
    # sa suite sans le dire, article cité sans lecture à la date utile (skill recherche-juridique ; règles dans lectures.py).
    import lectures as LECTURES
    avant = len(constats)
    LECTURES.controler(racine, ecriture, fiche, texte, c)
    if not juridictionnel:
        for k in constats[avant:]:
            if k["gravite"] == "BLOQUANT":
                k["gravite"] = "ALERTE"
                k["message"] += " (alerte seulement : l'écrit n'est pas porté devant un juge)"

    # Objections dirimantes encore ouvertes pour cet acte.
    for o in L.objections_bloquantes(racine, ecriture.stem):
        c("OBJECTION_DIRIMANTE_OUVERTE", "BLOQUANT", f"Objection {o.get('id')} ouverte : {o.get('enonce', '')[:160]}. "
          "La traiter dans le texte, la faire accepter par le client en connaissance de cause, ou la rejeter par écrit motivé.")

    # Lecture à froid sur la version exacte.
    lf = L.lire_json(ch["lecture_froid"])
    if juridictionnel and type_acte != "conclusions":
        if lf is None:
            c("LECTURE_FROID_ABSENTE", "BLOQUANT", "Aucune lecture à froid par le sous-agent juge-simule.")
        elif lf.get("sha256") != empreinte:
            c("LECTURE_FROID_PERIMEE", "BLOQUANT", "La lecture à froid porte sur une autre version du texte (empreinte différente).")
        else:
            for k in ("decision_claire", "question_claire", "demande_claire"):
                if lf.get(k) is not True:
                    c("LECTURE_FROID_" + k.upper(), "BLOQUANT", f"Le lecteur à froid n'a pas pu identifier : {k.replace('_claire', '')}.")
            if refere and (lf.get("issue") in ("tri", "rejet_sans_audience", "irrecevable") or lf.get("issue_au_tri") == "tri"):
                c("LECTURE_FROID_TRI", "BLOQUANT", f"Le juge simulé trierait la requête : {'; '.join(lf.get('motifs', []))[:400]}")
            elif lf.get("issue_binaire") == "echec" or lf.get("issue") in ("rejet", "irrecevable", "tri"):
                c("LECTURE_FROID_DEFAVORABLE", "BLOQUANT", f"Le juge simulé rejetterait l'acte ({lf.get('categorie_motif') or lf.get('issue')}) : "
                  f"{'; '.join(str(m) for m in lf.get('motifs', []))[:400]}", categorie=lf.get("categorie_motif"))
    # Délibéré en deux temps : la lecture à froid ne vaut que précédée du rapport du rapporteur sur la même version.
    rr = L.lire_json(ch["rapport_rapporteur"])
    if juridictionnel and type_acte != "conclusions":
        if rr is None:
            c("RAPPORT_RAPPORTEUR_ABSENT", "BLOQUANT", "Aucun rapport du sous-agent rapporteur-simule : la formation statuerait sans instruction "
              "condition par condition (textes lus, standard, charge de la preuve).")
        elif rr.get("sha256") != empreinte:
            c("RAPPORT_RAPPORTEUR_PERIME", "BLOQUANT", "Le rapport du rapporteur porte sur une autre version du texte (empreinte différente).")
    # Contradiction close.
    ct = L.lire_json(ch["contradiction"])
    if juridictionnel:
        if ct is None:
            c("CONTRADICTION_ABSENTE", "BLOQUANT", "Aucune contradiction écrite par le sous-agent contradicteur.")
        else:
            ouverts = [p for p in ct.get("points", []) if p.get("statut") not in ("applique", "rejete_motive")]
            for p in ouverts:
                c("CONTRADICTION_OUVERTE", "BLOQUANT", f"Point {p.get('id')} du contradicteur non tranché : {str(p.get('objection', ''))[:160]}")

    conservatoire = CAMPAGNE.appliquer_conservatoire(constats, fiche, refere, c) if juridictionnel else False
    bloquants = [k for k in constats if k["gravite"] == "BLOQUANT"]
    verdict = {
        # Chemin court et chemin long d'un même dossier (Windows, « RUNNER~1 ») : la comparaison se fait sur les chemins résolus.
        "ecriture": L.relatif(racine, ecriture) or ecriture.as_posix(),
        "sha256": empreinte,
        "controle_le": L.horodatage(),
        "type_acte": type_acte,
        "verdict": "PASS" if not bloquants else "FAIL",
        "bloquants": len(bloquants),
        "alertes": sum(1 for k in constats if k["gravite"] == "ALERTE"),
        "mesures": rap.mesures,
        "constats": constats,
        "portee": "Verrous mécaniques seulement. Ni la justesse juridique ni l'issue ne sont attestées.",
    }
    if conservatoire:
        verdict["mode"] = "conservatoire"
    import os
    if os.environ.get("CONTENTIEUX_MAINTENANT"):
        verdict["horloge_fixee"] = os.environ["CONTENTIEUX_MAINTENANT"]
    L.ecrire_json(ch["gate"], verdict)
    return verdict


def resume(v: dict) -> str:
    lignes = [f"Contrôle avant dépôt : {v['verdict']} ({v['bloquants']} bloquant(s), {v['alertes']} alerte(s)) sur {v['ecriture']} [{v['sha256'][:12]}]."]
    for k in v["constats"]:
        if k["gravite"] in ("BLOQUANT", "ALERTE"):
            loc = f" (l. {k['ligne']})" if k.get("ligne") else ""
            lignes.append(f"- {k['gravite']} {k['code']}{loc} : {k['message']}" + (f" « {k['extrait']} »" if k.get("extrait") else ""))
    m = v.get("mesures", {})
    lignes.append("Mesures (information) : " + ", ".join(f"{a} {b}" for a, b in m.items()))
    return "\n".join(lignes)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    if sys.argv[1] == "--regimes":
        charger_regimes_domaines()
        cats = categories_conditions()
        for t, r in sorted(REGIMES.items()):
            print(f"{t} [{r.get('domaine') or r.get('juge')}] {r.get('texte', '')}")
            for nom in r["conditions"]:
                print(f"    {nom} ({cats.get(nom, 'mal_fonde')})")
        raise SystemExit(0)
    v = controler(Path(sys.argv[1]).resolve())
    print(json.dumps(v, ensure_ascii=False, indent=2) if "--json" in sys.argv else resume(v))
    raise SystemExit(0 if v["verdict"] == "PASS" else 1)
