"""Contrôles de la campagne, appelés par gate.py avant tout acte juridictionnel.

Théorie de l'affaire (strategie/theorie.json, skill theorie-de-l-affaire) et séquence
(strategie/sequence.json, skill conduite-de-la-sequence). Les contrôles sont mécaniques :
ils vérifient que le travail existe, qu'il est à jour et qu'il couvre l'acte, pas qu'il est juste.
"""
from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path

import lib_affaire as L

TRAITEMENTS = {"integration", "depassement", "indifference", "retournement"}
EPREUVES = ("couverture", "coherence", "completude", "unicite", "stabilite", "verite", "contradiction")
FAMILLES = ("amiable", "administrative", "autorite_independante", "urgence", "fond", "indemnitaire",
            "penal", "disciplinaire", "europeen", "constitutionnel", "hors_pretoire")


def date_declaree(valeur) -> datetime | None:
    """Une date sans heure compte du début du jour : elle ne vaut pas pour un apport du même jour."""
    v = str(valeur or "")
    return L.parse_date(v + "T00:00" if len(v) == 10 else v)


def dernier_apport(racine: Path) -> tuple[datetime | None, str]:
    """Moment du dernier apport au dossier : pièce cotée ou fiche d'analyse documentaire."""
    candidats: list[tuple[datetime, str]] = []
    for p in (L.lire_json(racine / "pieces/bordereau.json", {}) or {}).get("pieces", []):
        d = L.parse_date(str(p.get("ajoutee_le") or "").replace(" ", "T")[:16])
        if d:
            candidats.append((d, f"pièce {p.get('cote')}"))
    analyses = racine / "pieces" / "analyses"
    if analyses.is_dir():
        # La date d'une fiche est celle qu'elle porte (analyse_le, écrite à l'heure du dossier) ; l'heure du fichier
        # ne sert qu'à défaut, et jamais quand l'horloge du dossier est fixée pour un rejeu.
        rejeu = bool(os.environ.get("CONTENTIEUX_MAINTENANT"))
        for f in analyses.glob("*.json"):
            d = L.parse_date(str((L.lire_json(f, {}) or {}).get("analyse_le") or "").replace(" ", "T")[:16])
            if d is None and not rejeu:
                d = datetime.fromtimestamp(f.stat().st_mtime).astimezone()
            if d:
                candidats.append((d, f"analyse {f.stem}"))
    if not candidats:
        return None, ""
    return max(candidats, key=lambda x: x[0])


def _texte(v) -> str:
    return str(v or "").strip()


def controler_theorie(racine: Path, ecriture: Path, c) -> None:
    th = L.lire_json(racine / "strategie/theorie.json")
    if not th:
        c("THEORIE_ABSENTE", "BLOQUANT", "strategie/theorie.json absent : la vérité de l'affaire et sa théorie s'établissent sur pièces "
          "avant toute écriture (skill theorie-de-l-affaire).")
        return
    dt = date_declaree(th.get("date"))
    apport, quoi = dernier_apport(racine)
    if dt is None:
        c("THEORIE_PERIMEE", "BLOQUANT", "Théorie de l'affaire sans date lisible (AAAA-MM-JJTHH:MM).")
    elif apport and apport > dt:
        c("THEORIE_PERIMEE", "BLOQUANT", f"Théorie antérieure au dernier apport du dossier ({quoi}) : la relire contre ce qui est nouveau et la redater.")

    hyps = [h for h in th.get("hypotheses", []) if isinstance(h, dict)]
    porteurs = {h.get("porteur") for h in hyps}
    if len(hyps) < 3 or not {"adversaire", "lecture_par_defaut"} <= porteurs:
        c("THEORIE_HYPOTHESES", "BLOQUANT", "Moins de trois hypothèses, ou absence de la meilleure hypothèse de l'adversaire ou de la lecture "
          "par défaut du juge : la théorie n'a pas été éprouvée contre ses concurrentes.")
    retenues = [h for h in hyps if h.get("statut") == "retenue"]
    if len(retenues) != 1:
        c("THEORIE_HYPOTHESES", "BLOQUANT", f"{len(retenues)} hypothèse(s) retenue(s) : il en faut exactement une.")
    for h in retenues:
        for inc in h.get("pieces_incompatibles", []) or []:
            if not isinstance(inc, dict) or len(_texte(inc.get("explication"))) < 20:
                piece = inc.get("piece") if isinstance(inc, dict) else inc
                c("THEORIE_PIECE_INCOMPATIBLE", "BLOQUANT", f"Hypothèse retenue {h.get('id')} : la pièce {piece} la contredit sans explication "
                  "tirée de son analyse. L'adversaire la produira.")

    tr = th.get("theorie_retenue") or {}
    for champ in ("recit", "qualification", "question", "theme", "surete"):
        if not _texte(tr.get(champ)):
            c("THEORIE_INCOMPLETE", "BLOQUANT", f"Théorie retenue : champ « {champ} » vide.")
    for f_ in th.get("faits_defavorables", []) or []:
        if not isinstance(f_, dict) or f_.get("traitement") not in TRAITEMENTS or len(_texte(f_.get("explication"))) < 20:
            fait = f_.get("fait") if isinstance(f_, dict) else f_
            c("THEORIE_FAIT_DEFAVORABLE", "BLOQUANT", f"Fait défavorable sans traitement admis ({', '.join(sorted(TRAITEMENTS))}) ni explication : "
              f"« {_texte(fait)[:120]} ». Un fait qu'aucun traitement n'absorbe montre une théorie fausse ou une question mal posée.")
    if "faits_defavorables" not in th:
        c("THEORIE_INCOMPLETE", "BLOQUANT", "Théorie : la liste « faits_defavorables » manque (vide si aucun, après recherche).")
    ep = th.get("epreuves") or {}
    for e in EPREUVES:
        if not _texte(ep.get(e)):
            c("THEORIE_EPREUVE_MANQUANTE", "BLOQUANT", f"Épreuve de la théorie non écrite : {e}.")
    adverse = L.lire_json(racine / "strategie" / "theorie_adverse.json")
    if not adverse or not isinstance(adverse.get("arguments"), list) or not adverse["arguments"]:
        c("THEORIE_CONTRADICTION_ABSENTE", "BLOQUANT", "Aucune théorie adverse structurée écrite par le sous-agent avocat-adverse à partir des seules "
          "pièces (strategie/theorie_adverse.json, liste « arguments ») : la théorie n'a pas affronté la meilleure version de l'adversaire.")
    else:
        reponses = {str(r.get("argument")): r for r in th.get("reponses_theorie_adverse", []) or [] if isinstance(r, dict)}
        for a in adverse["arguments"]:
            if not isinstance(a, dict):
                continue
            aid, r = str(a.get("id")), reponses.get(str(a.get("id")))
            libelle = _texte(a.get("argument") or a.get("enonce"))[:140]
            decisif = _texte(a.get("force")).lower().startswith("decisi") or _texte(a.get("force")).lower().startswith("décisi")
            if r is None:
                c("THEORIE_ARGUMENT_ADVERSE_SANS_REPONSE", "BLOQUANT", f"Argument adverse {aid} sans réponse dans la théorie (reponses_theorie_adverse) : "
                  f"« {libelle} ». Un argument que la théorie ne traite pas est celui que le juge retiendra.")
                continue
            if r.get("traitement") not in TRAITEMENTS | {"decisif_pour_la_voie"} or len(_texte(r.get("explication"))) < 20:
                c("THEORIE_ARGUMENT_ADVERSE_SANS_REPONSE", "BLOQUANT", f"Argument adverse {aid} : traitement non admis ou non expliqué.")
            elif r.get("traitement") == "decisif_pour_la_voie" and not r.get("voies_modifiees"):
                c("THEORIE_ARGUMENT_ADVERSE_SANS_REPONSE", "BLOQUANT", f"Argument adverse {aid} reconnu décisif pour une voie sans que la séquence en "
                  "tire la conséquence (voies_modifiees) : retirer ou refonder la voie qu'il fait tomber.")
            elif decisif and r.get("traitement") != "decisif_pour_la_voie" and not (r.get("appui") or []):
                c("THEORIE_ARGUMENT_ADVERSE_SANS_REPONSE", "BLOQUANT", f"Argument adverse {aid}, jugé décisif par l'adversaire, écarté sans pièce ni "
                  "source (appui) : une réponse verbale ne neutralise pas un argument décisif.")

    recit = L.lire_json(racine / "ecritures/controle" / f"{ecriture.stem}.recit.json")
    if recit and _texte(recit.get("theorie_date")) != _texte(th.get("date")):
        c("THEORIE_NON_SUIVIE", "BLOQUANT", f"La fiche de récit de {ecriture.stem} ne projette pas la théorie en vigueur "
          f"(theorie_date « {_texte(recit.get('theorie_date')) or 'absente'} », théorie du « {_texte(th.get('date'))} »).")


def controler_sequence(racine: Path, ecriture: Path, fiche: dict, c) -> None:
    sq = L.lire_json(racine / "strategie/sequence.json")
    if not sq:
        c("SEQUENCE_ABSENTE", "BLOQUANT", "strategie/sequence.json absent : la campagne se conçoit depuis le premier acte adverse, "
          "toutes voies examinées, avant tout acte (skill conduite-de-la-sequence).")
        return
    dt = date_declaree(sq.get("date"))
    apport, quoi = dernier_apport(racine)
    if dt is None:
        c("SEQUENCE_PERIMEE", "BLOQUANT", "Séquence sans date lisible (AAAA-MM-JJTHH:MM).")
    elif apport and apport > dt:
        c("SEQUENCE_PERIMEE", "BLOQUANT", f"Séquence antérieure au dernier apport du dossier ({quoi}) : la réviser et la redater.")
    for a in sq.get("actes", []) or []:
        if isinstance(a, dict) and not _texte(a.get("regime_contentieux")):
            c("ACTE_REGIME_CONTENTIEUX_NON_EXAMINE", "BLOQUANT", f"Acte {a.get('id')} : régime contentieux non examiné (regime_contentieux). Dire s'il relève "
              "du droit commun ou d'un régime spécial (juridiction de premier ressort, délai non prorogé par un recours administratif, "
              "délai de jugement, notification du recours, cristallisation des moyens, intérêt à agir encadré), avec le texte lu.")
    va = [v for v in sq.get("voies_adversaires", []) or [] if isinstance(v, dict)]
    if not va:
        c("SEQUENCE_VOIES_ADVERSES_ABSENTES", "BLOQUANT", "Séquence : les voies par lesquelles l'adversaire peut atteindre son but si la sienne "
          "échoue ne sont pas recensées (voies_adversaires) : autre qualification, autre procédure, nouvel acte sur d'autres motifs, "
          "substitution de motifs devant le juge. Une campagne qui ne prévoit que la voie choisie par l'adversaire se fait surprendre par la suivante.")
    for v in va:
        if not (_texte(v.get("parade")) and (v.get("preuves_a_constituer") or [])):
            c("SEQUENCE_VOIES_ADVERSES_ABSENTES", "BLOQUANT", f"Voie adverse « {_texte(v.get('voie'))[:100]} » sans parade ni preuves à constituer dès maintenant.")
    pa = sq.get("premier_acte_adverse") or {}
    if not (_texte(pa.get("acte")) and _texte(pa.get("date"))):
        c("SEQUENCE_PREMIER_ACTE", "BLOQUANT", "Séquence : le premier acte adverse n'est pas identifié (acte et date).")

    examinees = {}
    for f_ in sq.get("familles_examinees", []) or []:
        if isinstance(f_, dict) and (f_.get("voies") or _texte(f_.get("sans_objet"))):
            examinees[f_.get("famille")] = f_
    manquantes = [f for f in FAMILLES if f not in examinees]
    if manquantes:
        c("SEQUENCE_FAMILLE_NON_EXAMINEE", "BLOQUANT", f"Familles de voies non examinées : {', '.join(manquantes)}. "
          "Chacune reçoit ses voies ou la raison pour laquelle elle est sans objet.")

    voies = {v.get("id"): v for v in sq.get("voies", []) or [] if isinstance(v, dict)}
    evenements = {e.get("id") for e in (L.lire_json(racine / "chronologie/chronologie.json", {}) or {}).get("evenements", []) if e.get("id")}
    for v in voies.values():
        if v.get("statut") != "retenue":
            continue
        d = v.get("delai") or {}
        if _texte(d.get("sans_delai")):
            continue
        if not (_texte(d.get("evenement")) and _texte(d.get("regle"))) or (evenements and d.get("evenement") not in evenements):
            c("VOIE_SANS_DELAI", "BLOQUANT", f"Voie retenue {v.get('id')} ({_texte(v.get('voie'))[:80]}) : délai sans événement de la chronologie "
              "ni règle, ou « sans_delai » non motivé.")

    coups = [k for k in sq.get("ordre_des_coups", []) or [] if isinstance(k, dict)]
    for v in voies.values():
        if v.get("statut") != "retenue" or v.get("famille") != "urgence":
            continue
        chemin = _texte(v.get("epreuve_juge")).replace("\\", "/")
        lecture = L.lire_json(racine / chemin) if chemin.startswith("ecritures/controle/") and ".lecture_froid" in chemin else None
        if not lecture:
            c("VOIE_URGENCE_NON_EPROUVEE", "BLOQUANT", f"Voie d'urgence retenue {v.get('id')} sans épreuve devant le rapporteur et le juge simulés "
              "calibrés (champ epreuve_juge vers une lecture à froid de sa trame) : un référé se retient après avoir été jugé, pas avant.")
        elif lecture.get("issue_binaire") == "echec" or lecture.get("issue") in ("rejet", "tri", "irrecevable", "non_admission"):
            c("VOIE_URGENCE_REJETEE_EN_SIMULATION", "BLOQUANT", f"Voie d'urgence {v.get('id')} : le juge simulé calibré la rejette "
              f"({lecture.get('categorie_motif') or lecture.get('issue')}). La mettre en réserve, ou la refonder sur la preuve qui manque, avant de la retenir.")
    for k in coups:
        reps = [r for r in k.get("reponses_adverses", []) or [] if isinstance(r, dict) and _texte(r.get("reponse")) and _texte(r.get("coup_suivant"))]
        if not reps:
            c("COUP_SANS_REPONSE_ADVERSE", "BLOQUANT", f"Coup {k.get('rang')} ({_texte(k.get('coup'))[:80]}) : aucune réponse adverse prévue "
              "avec notre coup suivant.")

    # Le rejet d'un référé-suspension pour absence de doute sérieux oblige à confirmer le fond dans le mois (CJA, R. 612-5-2) :
    # faute de l'avoir prévu, un fond est perdu sans être jugé.
    for v in voies.values():
        if v.get("statut") == "retenue" and v.get("type_acte") == "refere_suspension":
            textes = " ".join(str(r) for k in coups if k.get("voie") == v.get("id") for r in k.get("reponses_adverses", []) or [])
            if "612-5-2" not in textes.replace(" ", ""):
                c("SEQUENCE_DESISTEMENT_NON_PREVU", "BLOQUANT", f"Voie {v.get('id')} : la séquence ne prévoit pas, après un rejet du référé "
                  "pour absence de doute sérieux, la confirmation du maintien de la requête au fond dans le mois (CJA, art. R. 612-5-2), "
                  "faute de quoi le requérant est réputé s'être désisté.")

    racine_acte = ecriture.stem.split("_v")[0]
    type_acte = fiche.get("type_acte")
    candidates = [v for v in voies.values() if v.get("statut") == "retenue"
                  and (any(racine_acte == str(e).split("_v")[0] or racine_acte in str(e) for e in v.get("ecritures", []) or [])
                       or (type_acte and v.get("type_acte") == type_acte))]
    if not candidates:
        c("ACTE_HORS_SEQUENCE", "BLOQUANT", f"L'écriture {ecriture.stem} ne correspond à aucune voie retenue de la séquence "
          "(champ « ecritures » ou « type_acte » de la voie). Un acte hors campagne est un coup sans fonction.")
    elif not any(k.get("voie") in {v.get("id") for v in candidates} for k in coups):
        c("ACTE_HORS_SEQUENCE", "BLOQUANT", f"La voie de l'écriture {ecriture.stem} n'a pas de place dans l'ordre des coups.")

    th = L.lire_json(racine / "strategie/theorie.json") or {}
    if th and _texte((sq.get("coherence") or {}).get("theorie_date")) != _texte(th.get("date")):
        c("SEQUENCE_THEORIE", "BLOQUANT", "La séquence repose sur une autre version de la théorie de l'affaire que celle en vigueur.")


def controler_urgence(fiche: dict, c) -> None:
    """Référé administratif : l'urgence s'apprécie objectivement et globalement, l'intérêt public invoqué en défense compris
    (CE, Sect., 28 février 2001, n° 229562). La fiche nomme cet intérêt et dit pourquoi la balance penche de notre côté."""
    for cond in fiche.get("conditions", []) or []:
        if not isinstance(cond, dict) or cond.get("condition") not in ("urgence", "urgence_particuliere"):
            continue
        interet, bilan = _texte(cond.get("interet_public_adverse")), _texte(cond.get("bilan"))
        if not interet or len(bilan) < 40:
            c("URGENCE_BILAN_ABSENT", "BLOQUANT", "Condition d'urgence sans bilan : nommer l'intérêt public ou l'intérêt de tiers que la défense opposera "
              "à la suspension (interet_public_adverse, ou « aucun » avec sa raison) et dire, pièces à l'appui, pourquoi la balance penche "
              "pour la suspension (bilan). L'urgence s'apprécie globalement (CE, Sect., 28 février 2001, n° 229562) ; "
              "quand le même intérêt est invoqué des deux côtés, se demander à qui le juge l'attribuera.")


DIFFERABLES = ("FAIT_DECISIF_", "LECTURE_", "RAPPORT_RAPPORTEUR_", "CONTRADICTION_", "RECIT_", "THEORIE_", "SEQUENCE_", "ACTE_HORS_SEQUENCE",
               "ACTE_REGIME_", "COUP_SANS_", "VOIE_", "DECIDEURS_", "NEGOCIATION_", "LIGNE_", "REVUE_CHARPENTE_", "CHARPENTE_", "AUDIT_TERRAIN_",
               "PIECE_HORS_BORDEREAU", "CONDITION_", "OBJECTION_DIRIMANTE_OUVERTE", "CANAL_NON_CONTROLE", "PIECE_CITEE_")
CATEGORIES_NON_DIFFERABLES = {"delai_tardivete", "incompetence", "acte_non_attaquable", "prealable_obligatoire_absent", "prescription_forclusion"}


def appliquer_conservatoire(constats: list, fiche: dict, refere: bool, c) -> bool:
    """Requête conservatoire : un délai qui expire dans les 72 heures ne se perd pas faute de pièces ou de lectures que la
    procédure permet d'apporter ensuite. La requête doit contenir au moins un moyen (CJA, art. R. 411-1, al. 2) et annoncer
    son mémoire complémentaire ; les irrecevabilités régularisables le restent sur invitation (CJA, art. R. 612-1 ;
    CE, 3 juillet 2020, n° 424293, pour l'article R. 600-4 du code de l'urbanisme). Ce qui fait perdre le délai, la
    compétence ou l'acte reste bloquant. Le mémoire complémentaire passe le contrôle entier."""
    cons = fiche.get("conservatoire")
    if not isinstance(cons, dict):
        return False
    raisons = []
    ech = date_declaree(cons.get("echeance"))
    maintenant = L.maintenant()
    if refere:
        raisons.append("un référé ne se dépose pas en mode conservatoire : il est jugé sur ce qu'il contient")
    if ech is None:
        raisons.append("échéance du délai non datée (conservatoire.echeance)")
    elif not 0 <= (ech - maintenant).total_seconds() <= 72 * 3600:
        raisons.append("l'échéance n'est pas dans les 72 heures : le temps permet l'acte complet")
    if not [m for m in fiche.get("moyens", []) or [] if isinstance(m, dict) and _texte(m.get("intitule"))]:
        raisons.append("aucun moyen : une requête sans moyen ne se régularise que jusqu'à l'expiration du délai (CJA, art. R. 411-1)")
    mc = date_declaree(cons.get("memoire_complementaire"))
    if mc is None or (mc - maintenant).days > 30:
        raisons.append("mémoire complémentaire non daté, ou annoncé à plus de trente jours")
    if raisons:
        c("CONSERVATOIRE_INJUSTIFIE", "BLOQUANT", "Mode conservatoire refusé : " + " ; ".join(raisons) + ".")
        return False
    differes = 0
    for k in constats:
        if k.get("gravite") != "BLOQUANT" or k.get("categorie") in CATEGORIES_NON_DIFFERABLES:
            continue
        if k.get("code", "").startswith(DIFFERABLES):
            k["gravite"] = "ALERTE"
            k["message"] += f" (différé : requête conservatoire, à traiter dans le mémoire complémentaire du {cons.get('memoire_complementaire')})"
            differes += 1
    c("CONSERVATOIRE", "ALERTE", f"Requête conservatoire avant l'échéance du {cons.get('echeance')} : {differes} constat(s) différé(s) au mémoire "
      f"complémentaire du {cons.get('memoire_complementaire')}, qui passera le contrôle entier. Pièces à produire : "
      f"{', '.join(map(str, cons.get('pieces_a_produire') or [])) or 'à lister'}.")
    return True


def controler_competence(racine: Path, regime: dict, c) -> None:
    """Juge administratif : la juridiction compétente en premier ressort se lit dans les articles R. 311-1 et suivants du code
    de justice administrative, à la date de l'acte ; elle ne se reprend ni du client ni de la mention de l'acte. Le banc du
    20 novembre l'a montré : un recours contre une déclaration d'utilité publique préparé pour le tribunal relevait de la cour."""
    if regime.get("juge") != "admin":
        return
    if not competence_admin_lue(racine):
        c("COMPETENCE_PREMIER_RESSORT_NON_LUE", "BLOQUANT", MESSAGE_COMPETENCE)


MESSAGE_COMPETENCE = ("Juridiction compétente en premier ressort non vérifiée : lire à la date de l'acte les articles R. 311-1 à R. 311-6 "
                      "du code de justice administrative (compétence directe du Conseil d'État et des cours, contentieux spéciaux), puis la "
                      "compétence territoriale (R. 312-1 et suivants). La juridiction désignée par le client ou par l'acte ne se reprend pas "
                      "sans cette lecture, même quand le client demande un projet rapide sans la chaîne complète de contrôle.")

RE_JUGE_ADMIN = re.compile(r"tribunal administratif|cour administrative d.appel|conseil d.[ée]tat", re.I)
RE_ACTE = re.compile(r"par ces motifs|plaise au|demande(?:nt)? (?:au|à la) (?:tribunal|cour|juge|conseil)|requ[êe]te (?:introductive|en annulation|aux fins)"
                     r"|^#{1,4} .{0,20}conclusions|l\. ?761-1", re.I | re.M)


def est_acte(texte: str) -> bool:
    """Le texte est un acte destiné à un juge (requête, mémoire, assignation...), pas un échange sur l'affaire."""
    return bool(RE_ACTE.search(texte or ""))


def acte_devant_juge_admin(texte: str) -> bool:
    return est_acte(texte) and bool(RE_JUGE_ADMIN.search(texte or ""))


def competence_admin_lue(racine: Path) -> bool:
    import lectures as LECT
    reg = LECT.Registre(racine)
    return any(re.match(r"r311-\d", k) and any("justice-administrative" in str(x.get("code")) for x in v) for k, v in reg.normes.items())


def controler_revue_campagne(racine: Path, rc: dict, c) -> None:
    """La revue de charpente doit avoir examiné la théorie et la séquence en vigueur."""
    for nom, champ in (("theorie", "theorie_date"), ("sequence", "sequence_date")):
        f = L.lire_json(racine / f"strategie/{nom}.json")
        if f and _texte(rc.get(champ)) != _texte(f.get("date")):
            c("REVUE_CHARPENTE_PERIMEE", "BLOQUANT", f"La revue de charpente n'a pas examiné la {'théorie' if nom == 'theorie' else 'séquence'} "
              f"en vigueur ({champ} « {_texte(rc.get(champ)) or 'absent'} », fichier du « {_texte(f.get('date'))} »).")
