"""Point d'entrée unique des hooks du plugin contentieux.

Lit l'événement JSON sur l'entrée standard. Ne fait rien hors d'un dossier d'affaire.
SessionStart        briefing d'état (au démarrage, à la reprise et après compaction).
UserPromptSubmit    rappel des échéances proches, des canaux non contrôlés et des objections dirimantes.
PreToolUse          protège pièces originales, journal, constitution, versions finales et verdicts.
PostToolUse         valide les fichiers d'état et les fiches de lecture, passe le linter sur les écritures modifiées,
                    capture chaque lecture LibreJustice et read_document dans le registre des lectures.
Stop                exige une passation à jour quand le dossier a changé pendant la session.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib_affaire as L  # noqa: E402

PROTEGES = [
    (re.compile(r"^pieces/originaux/"), "Les pièces originales sont immuables. Ajouter une pièce : python <plugin>/scripts/affaire.py piece ajouter <fichier> --cote N --date AAAA-MM-JJ --description \"...\"."),
    (re.compile(r"^journal/journal\.md$"), "Le journal s'écrit par script, avec l'heure lue sur le poste : python <plugin>/scripts/affaire.py journal \"texte\" --type fait|acte|strategie|decision_client."),
    (re.compile(r"^(claude|agents)\.md$"), "La constitution du dossier (AGENTS.md, importé par CLAUDE.md) ne se modifie que par le client. Les consignes propres à l'affaire vont dans etat/consignes_affaire.md."),
    (re.compile(r"^ecritures/final/"), "Les versions finales s'obtiennent seulement par : python <plugin>/scripts/affaire.py finaliser <brouillon.md>, qui exige un contrôle PASS sur l'empreinte exacte."),
    (re.compile(r"^pieces/inventaire\.json$|^pieces/texte/.+\.extraction\.txt$"), "L'inventaire et les extractions ne s'écrivent que par pieces.py inventaire : les citations des fiches d'analyse sont vérifiées contre eux. Relancer : python <plugin>/scripts/pieces.py inventaire."),
    (re.compile(r"\.gate\.json$"), "Le verdict du contrôle avant dépôt n'est écrit que par gate.py. Relancer : python <plugin>/scripts/gate.py <brouillon.md>."),
    (re.compile(r"^recherche/lectures/"), "Le registre des lectures ne s'écrit que par le hook PostToolUse, qui capture chaque appel LibreJustice et read_document. "
     "Relire la source pour créer une capture ; consulter le registre par python <plugin>/scripts/lectures.py couverture|citations|portee|requetes."),
]
DESTRUCTIF = re.compile(r"\b(rm|del|erase|rmdir|mv|move|cp|copy|Remove-Item|Move-Item|Copy-Item|Rename-Item|Set-Content|Add-Content|Out-File|Clear-Content|truncate|sed\s+-i)\b|(?<![0-9&])>(?!\s*&|\s*/dev/null|\s*\$null|\s*nul\b)", re.I)
CHEMINS_SENSIBLES = re.compile(r"pieces[\\/]+originaux|pieces[\\/]+inventaire\.json|\.extraction\.txt|journal[\\/]+journal\.md|ecritures[\\/]+final|\.gate\.json|"
                               r"recherche[\\/]+lectures|(^|[\\/\s\"'])(claude|agents)\.md", re.I)


def sortie(obj: dict) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False))
    sys.exit(0)


def contexte(evenement: str, texte: str) -> None:
    sortie({"hookSpecificOutput": {"hookEventName": evenement, "additionalContext": texte}})


def refuser(raison: str) -> None:
    sortie({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": raison}})


def racine_evenement(ev: dict) -> Path | None:
    ti = ev.get("tool_input") or {}
    for cle in ("file_path", "notebook_path", "path"):
        if ti.get(cle):
            r = L.trouver_racine(ti[cle])
            if r:
                return r
    return L.trouver_racine(ev.get("cwd") or os.getcwd())


def briefing(racine: Path, source: str) -> str:
    a = L.lire_json(racine / "etat/affaire.json", {}) or {}
    lignes = []
    if source == "compact":
        lignes.append("REPRISE APRÈS COMPACTION. Le résumé ne vaut pas lecture : relire etat/passation.md, les échéances et les objections avant toute position.")
    # Routage : les agents ne chargent pas les skills d'eux-mêmes ; le savoir est là quand on le leur demande, pas quand
    # le point décisif n'est pas posé (banc du 19 et 20 novembre). La table vient en tête, avant toute troncature.
    lignes.append("ROUTAGE, avant de répondre ou d'écrire, charger le skill qui commande la situation (outil Skill) et appliquer sa méthode "
                  "jusqu'au point décisif, puis le dire dans la réponse elle-même :")
    lignes.append("- toute question ou tout acte devant un juge ou une autorité : mecanique-des-exercices (fiche de l'exercice : condition qui le fait "
                  "échouer, exigences implicites, exercice voisin), puis le skill de l'exercice (refere-administratif, refere-civil, contentieux-du-fond, cassation) ;")
    lignes.append("- urgence d'un référé : bilan avec l'intérêt que la défense opposera, même quand le client invoque le même (refere-administratif) ;")
    lignes.append("- toute règle de droit affirmée : recherche-juridique (texte à la date, section, renvois, texte spécial, jurisprudence par article, suite des "
                  "décisions) ; portée discutée ou fait d'expérience : recherche-doctrinale ;")
    lignes.append("- stratégie, choix de voie, ordre des coups, délai qui court : conduite-de-la-sequence, dont l'offensive de fond (contre-attaque, "
                  "demande entière, charge de la preuve retournée, second front, chacun joué s'il sert le résultat) ;")
    lignes.append("- pronostic d'un recours (appel, pourvoi, opposition) : lire d'abord en entier la décision attaquée, au dossier ou sur LibreJustice "
                  "(son lien, ou sa juridiction et sa date), avant toute issue ; le juge du recours juge cette décision, pas le seul moyen ;")
    lignes.append("- pronostic d'une issue (urgence, moyen, pourvoi, demande) : mecanique-des-exercices, règle « Le pronostic se forme au siège » "
                  "(taux de base de la fiche, meilleure réponse adverse, standard de contrôle ; en tête, l'issue la plus probable) ;")
    lignes.append("- lettre à l'adversaire, coup contre lui, désaccord du client : rapport-de-force (rien de gratuit, position tenue sauf élément nouveau nommé) ;")
    lignes.append("- pièce nouvelle : analyse-documentaire ; décideur ou institution : lecture-des-decideurs ; voie amiable : negociation-et-persuasion, "
                  "et pour toute stratégie, lettre ou réponse de négociation, d'abord le sous-agent negociateur en fiche rapide ;")
    lignes.append("- tout texte, réponse au client comprise : recit-judiciaire. Écrire d'abord pour soi le lecteur, ce qu'il doit faire, l'enjeu concret, "
                  "le message central en une phrase, son objection, et les acteurs avec le pouvoir que chacun tient sur l'autre (rôles cumulés, relations "
                  "qui survivront au litige) ; puis le message en tête, deux à quatre raisons d'un paragraphe chacune, "
                  "une histoire et non une chronologie, l'objection traitée là où le lecteur la rencontre ; dates et montants exacts ; la longueur "
                  "demandée tenue, aucune annexe non demandée, rien d'inachevé, "
                  "aucun journal de travail (registres, outils, versions lues) ; ce qui a été lu se dit en fin, en une ligne ;")
    lignes.append("- tout texte et toute stratégie : penser le lecteur dans son monde (recit-judiciaire, section 4) : ce qu'il craint, qui décide derrière "
                  "lui, ce qu'il peut accorder sans perdre la face, sa solution de repli et la nôtre, ce que l'issue change dans les relations et dans "
                  "la situation sociale du client.")
    lignes.append(f"Dossier : {a.get('intitule')} (id {a.get('id')}). Client : {a.get('client')}. Adversaire(s) : {', '.join(a.get('adversaires', [])) or 'non renseigné'}.")
    lignes.append(f"Objectif du client : {a.get('objectif')}")
    # Le briefing est le seul contexte que reçoit à coup sûr une session lancée en mode non interactif (claude -p) : le protocole
    # de recherche s'y rappelle, comme dans user_prompt.
    lignes.append("Recherche : toute question de droit et toute rédaction suivent les passes de la skill recherche-juridique (texte décisif lu "
                  "à la date utile avec sa section, ses renvois et son texte modificatif ; jurisprudence par legal_article, et sans filtre "
                  "d'article pour une règle prétorienne ; suite de chaque décision citée, même reprise d'une note, y compris les décisions "
                  "postérieures sur la même question ; conclusions signalées lues, non reportées ; meilleure autorité contraire ; prémisses de la demande vérifiées à la source). "
                  "Les lectures LibreJustice sont capturées dans recherche/lectures/ et les citations se contrôlent par python "
                  f"\"{os.environ.get('CLAUDE_PLUGIN_ROOT', '<plugin>')}/scripts/lectures.py\" citations <note>.")
    lignes.append("Économie : les appels indépendants (textes, décisions, fichiers, commandes) partent ensemble dans un même message ; "
                  "un appel ne part seul que s'il dépend du résultat du précédent.")
    for inst in a.get("instances", []):
        lignes.append(f"Instance : {inst.get('juridiction')} n° {inst.get('numero')} ({inst.get('nature')}), {inst.get('statut')}.")
    ech = L.echeances_ouvertes(racine)
    if ech:
        lignes.append("Échéances ouvertes :")
        for h, e in ech[:12]:
            lignes.append(f"- {e.get('date')} ({L.fmt_heures(h)}) {e.get('objet')} [règle : {e.get('regle')} ; certitude : {e.get('certitude', 'non précisée')}]")
    else:
        lignes.append("Aucune échéance ouverte enregistrée dans etat/echeances.json : si une procédure est en cours, c'est un défaut à corriger.")
    try:
        import voies
        calc = [v for v in voies.calculer(racine) if v["date"] >= L.maintenant().date().isoformat()]
        connus = {(e.get("objet"), e.get("date")) for _, e in ech}
        calc = [v for v in calc if (v["objet"], v["date"]) not in connus]
        if calc:
            lignes.append("Délais calculés depuis la chronologie et non inscrits (scénarios à vérifier, voies.py --inscrire) :")
            lignes.extend(f"- {v['date']} {v['objet']} [{v['regle']}]" for v in calc[:8])
    except Exception:  # noqa: BLE001
        pass
    ligne = L.lire_json(racine / "strategie/ligne.json") or {}
    if ligne.get("objectif"):
        lignes.append(f"Ligne en vigueur ({ligne.get('date')}) : levier « {ligne.get('levier')} » ; meilleur coup adverse « {ligne.get('meilleur_coup_adverse')} » ; parade « {ligne.get('parade')} ».")
    else:
        lignes.append("Aucune ligne stratégique écrite (strategie/ligne.json) : l'écrire avant tout acte.")
    theorie = L.lire_json(racine / "strategie/theorie.json") or {}
    retenue = theorie.get("theorie_retenue") or {}
    if retenue.get("question"):
        lignes.append(f"Théorie de l'affaire ({theorie.get('date')}) : question « {retenue.get('question')} » ; qualification « {retenue.get('qualification')} ».")
    else:
        lignes.append("Aucune théorie de l'affaire (strategie/theorie.json) : l'établir sur pièces avant la séquence et toute écriture.")
    profil = L.lire_json(racine / "strategie/decideurs.json") or {}
    if isinstance(profil.get("decideurs"), list) and profil["decideurs"]:
        d0 = next((d for d in profil["decideurs"] if isinstance(d, dict) and d.get("nature") == "juridiction"), profil["decideurs"][0])
        lignes.append(f"Profil des décideurs ({profil.get('date')}) : {d0.get('institution')}, {d0.get('formation')} ; contrôle "
                      f"{(d0.get('standard_de_controle') or {}).get('niveau')} ; adversaire « {(profil.get('adversaire') or {}).get('designation')} ».")
    else:
        lignes.append("Aucun profil des décideurs (strategie/decideurs.json) : l'établir avant tout acte juridictionnel (skill lecture-des-decideurs).")
    fiches_doctrine = sorted((racine / "recherche/doctrine").glob("*.json")) if (racine / "recherche/doctrine").is_dir() else []
    if fiches_doctrine:
        lus = sum(1 for f in fiches_doctrine if ((L.lire_json(f) or {}).get("lecture") or {}).get("statut") in ("texte_integral", "extraits"))
        lignes.append(f"Doctrine : {len(fiches_doctrine)} fiche(s) de lecture dans recherche/doctrine/, dont {lus} sur texte lu ; "
                      "les autres ne se citent pas entre guillemets (skill recherche-doctrinale).")
    nego = L.lire_json(racine / "strategie/negociation.json") or {}
    if isinstance(nego, dict) and nego.get("etat"):
        jour = L.maintenant().date().isoformat()
        prochain = sorted((j for j in nego.get("calendrier") or [] if isinstance(j, dict) and str(j.get("date", "")) >= jour),
                          key=lambda j: str(j.get("date")))
        suite = f" ; prochaine étape {prochain[0].get('date')} : {prochain[0].get('evenement')}" if prochain else ""
        lignes.append(f"Négociation ({nego.get('date')}) : état « {nego.get('etat')} »{suite}. Aucun chiffre de la négociation "
                      "dans un écrit au juge.")
    else:
        lignes.append("Aucun plan de négociation (strategie/negociation.json) : examiner les voies amiables et la solution de repli "
                      "de chaque partie avant tout acte juridictionnel (skill negociation-et-persuasion).")
    try:
        import positions as POSITIONS
        tenues = POSITIONS.en_vigueur(racine)
    except Exception:  # noqa: BLE001
        tenues = []
    if tenues:
        lignes.append("Positions tenues devant le client (strategie/positions.json) ; chacune ne change que sur un élément nouveau nommé :")
        lignes.extend(f"- {p.get('id')} ({p.get('date')}) {str(p.get('objet'))[:80]} : « {str(p.get('position'))[:160]} »" for p in tenues[:6])
    sequence = L.lire_json(racine / "strategie/sequence.json") or {}
    coups = [k for k in sequence.get("ordre_des_coups", []) or [] if isinstance(k, dict) and k.get("statut") not in ("joue", "abandonne")]
    if coups:
        k = coups[0]
        lignes.append(f"Séquence ({sequence.get('date')}) : prochain coup « {k.get('coup')} », au plus tard {k.get('au_plus_tard')}.")
    elif not sequence:
        lignes.append("Aucune séquence (strategie/sequence.json) : concevoir la campagne depuis le premier acte adverse avant tout acte.")
    per = L.canaux_perimes(racine)
    if per:
        lignes.append("Canaux de notification non contrôlés dans le délai prévu (une décision peut y attendre) :")
        for c, age in per:
            lignes.append(f"- {c.get('nom')} ({c.get('adresse', '')}) : {'jamais contrôlé' if age is None else f'dernier contrôle il y a {age / 24:.1f} j'} ; fréquence prévue {c.get('frequence_heures')} h.")
    obj = L.objections_bloquantes(racine)
    if obj:
        lignes.append(f"Objections dirimantes ouvertes : {len(obj)}.")
        for o in obj[:8]:
            lignes.append(f"- {o.get('id')} [{o.get('acte')}] {o.get('enonce', '')[:200]}")
    consignes = racine / "etat/consignes_affaire.md"
    if consignes.is_file():
        lignes.append("Consignes propres à l'affaire (etat/consignes_affaire.md) :")
        lignes.append(consignes.read_text(encoding="utf-8").strip())
    pas = racine / "etat/passation.md"
    jour_f = racine / "journal/journal.md"
    if pas.is_file() and jour_f.is_file() and jour_f.stat().st_mtime - pas.stat().st_mtime > 3600:
        lignes.append("La passation est antérieure de plus d'une heure aux dernières entrées du journal : elle peut décrire un état dépassé ; la vérifier contre le journal.")
    if pas.is_file():
        lignes.append("Passation de la dernière session (etat/passation.md) :")
        lignes.append(pas.read_text(encoding="utf-8").strip())
    jour = racine / "journal/journal.md"
    if jour.is_file():
        entrees = [l for l in jour.read_text(encoding="utf-8").splitlines() if l.startswith("- ")]
        if entrees:
            lignes.append("Dernières entrées du journal :")
            lignes.extend(entrees[-10:])
    lignes.append(f"Heure du poste à l'ouverture : {L.horodatage()}.")
    texte = "\n".join(lignes)
    # Le contexte injecté est plafonné à 10 000 caractères ; l'essentiel vient en tête.
    if len(texte) > 9500:
        texte = texte[:9200] + "\n[Briefing tronqué : lire etat/passation.md, etat/consignes_affaire.md et la fin du journal en entier.]"
    return texte


def session_start(ev: dict) -> None:
    racine = L.trouver_racine(ev.get("cwd") or os.getcwd())
    if racine is None:
        sys.exit(0)
    L.ecrire_json(racine / "etat/.session.json", {"session_id": ev.get("session_id"), "debut": L.horodatage(),
                                                   "debut_epoch": time.time(), "source": ev.get("source")})
    contexte("SessionStart", briefing(racine, ev.get("source", "")))


def user_prompt(ev: dict) -> None:
    racine = L.trouver_racine(ev.get("cwd") or os.getcwd())
    if racine is None:
        sys.exit(0)
    lignes = []
    for h, e in L.echeances_ouvertes(racine):
        if h <= 72:
            lignes.append(f"Échéance {L.fmt_heures(h)} : {e.get('objet')} ({e.get('date')}).")
    per = L.canaux_perimes(racine)
    if per:
        lignes.append("Canaux non contrôlés : " + ", ".join(c.get("nom", "?") for c, _ in per) + ".")
    n = len(L.objections_bloquantes(racine))
    if n:
        lignes.append(f"{n} objection(s) dirimante(s) ouverte(s).")
    demande = ev.get("prompt") or ""
    if "?" in demande or re.search(r"\b(r[ée]dig|pr[ée]par|v[ée]rifi|note|m[ée]moire|requ[êe]te|r[ée]plique|conclusions|courriel|lettre|moyen|"
                                   r"pourvoi|assignation|recours)", demande, re.I):
        # Les sondes du banc montrent que la skill de recherche n'est pas chargée pour une question directe ni pour une rédaction :
        # le protocole se rappelle donc ici, en deux phrases.
        lignes.append("Une question de droit ou une rédaction se traite par les passes de la skill recherche-juridique : chaque texte décisif lu "
                      "à la date utile avec sa section (exceptions voisines), ses renvois et son texte modificatif ; la jurisprudence cherchée par "
                      "l'article (filtre legal_article), publiée puis inédite ; la suite de chaque décision citée, même reprise d'une note "
                      "(standing, case_chronology) ; la meilleure autorité contraire ; les prémisses de la demande (délai, juridiction, autorité "
                      "d'une décision) vérifiées à la source comme le reste. Les citations se recopient depuis la source lue et se contrôlent par "
                      f"python \"{os.environ.get('CLAUDE_PLUGIN_ROOT', '<plugin>')}/scripts/lectures.py\" citations <note>.")
    prompt = ev.get("prompt") or ""
    if "?" in prompt:
        lignes.append("Une question du client appelle une réponse argumentée sur le fond, sources lues à l'appui. Reprendre le "
                      "raisonnement depuis le fondement, pas depuis la question. Maintenir la recommandation sauf élément nouveau "
                      "nommé (pièce cotée, source lue en entier, décision, fait daté) ; un désaccord n'en est pas un. "
                      "Une décision qui commande la réponse se lit avec ses conclusions ou son rapport (champ commentaries de get_decision) ; "
                      "quand la portée d'un texte, une jurisprudence en mouvement, la fiabilité d'une preuve, un fait d'expérience ou une "
                      "technique décide, chercher et lire les travaux savants qui l'établissent (skill recherche-doctrinale).")
    try:
        import positions as POSITIONS
        lignes.extend(POSITIONS.rappel(racine, prompt))
    except Exception:  # noqa: BLE001
        pass
    lignes.extend(positions_du_client(racine))
    if lignes:
        contexte("UserPromptSubmit", "\n".join(lignes))
    sys.exit(0)


def positions_du_client(racine: Path) -> list[str]:
    """Profil et positions de conseil enregistrés (skill profil-et-positions). Banc du 21 novembre : sans ce rappel, une revue de contrat
    exigeait du fournisseur ce que les positions du client acceptaient, et oubliait le circuit de validation qu'elles désignaient."""
    bases = [racine / "cabinet"]
    env = os.environ.get("HARNESS_JURIDIQUE_CONFIG")
    bases.append(Path(env) if env else Path.home() / ".harness-juridique")
    trouves = []
    for b in bases:
        if b.is_dir():
            trouves += [p for p in [b / "profil.md", *sorted((b / "positions").glob("*.md"))] if p.is_file()]
        if trouves:
            break
    if not trouves:
        return []
    noms = ", ".join(p.relative_to(racine).as_posix() if p.is_relative_to(racine) else str(p) for p in trouves)
    return [f"Profil et positions du client enregistrés : {noms}. Ils gouvernent toute revue, négociation ou conseil du pôle concerné : "
            "ce qu'ils acceptent ne se redemande pas, ce qu'ils refusent se demande, et la validation suit le circuit qu'ils désignent."]


RETENUE = re.compile(r"\b(ne (le |la |les )?(d[ée]pose|d[ée]posez|envoie|envoyez|signe|signez)|pas encore|attends|attendez|stop|suspend)", re.I)


def transcript(ev: dict) -> list[dict]:
    chemin = ev.get("transcript_path")
    if not chemin or not Path(chemin).is_file():
        return []
    lignes = []
    with open(chemin, encoding="utf-8", errors="replace") as f:
        for l in f:
            try:
                lignes.append(json.loads(l))
            except json.JSONDecodeError:
                continue
    return lignes


def messages_utilisateur(entrees: list[dict]) -> list[tuple[str, str]]:
    """Messages du client avec leur horodatage, dans l'ordre du fil."""
    res = []
    for e in entrees:
        if e.get("type") != "user":
            continue
        contenu = (e.get("message") or {}).get("content")
        if isinstance(contenu, str):
            res.append((e.get("timestamp"), contenu))
        elif isinstance(contenu, list):
            res.extend((e.get("timestamp"), b.get("text", "")) for b in contenu if isinstance(b, dict) and b.get("type") == "text")
    return res


def commande_depot(cmd: str) -> str | None:
    """Chemin de l'acte si la commande lance réellement `affaire.py depot <acte>` ; None si elle ne fait que citer ces mots."""
    for segment in re.split(r"&&|\|\||;|\n|\|", cmd):
        try:
            jetons = shlex.split(segment, posix=True)
        except ValueError:
            jetons = segment.split()
        for i, j in enumerate(jetons[:-1]):
            if j.replace("\\", "/").endswith("affaire.py") and jetons[i + 1] == "depot":
                return jetons[i + 2] if len(jetons) > i + 2 else ""
    return None


def lectures(entrees: list[dict]) -> list[str]:
    """Chemins lus (Read, Grep, get_decision…) depuis le début du fil ou la dernière compaction."""
    vus = []
    for e in entrees:
        if e.get("type") == "system" and "compact" in json.dumps(e, ensure_ascii=False).lower()[:400]:
            vus = []
        contenu = (e.get("message") or {}).get("content")
        if e.get("type") != "assistant" or not isinstance(contenu, list):
            continue
        for b in contenu:
            if isinstance(b, dict) and b.get("type") == "tool_use":
                vus.append(json.dumps(b.get("input", {}), ensure_ascii=False))
    return vus


def identifiants_prives(racine: Path) -> list[str]:
    a = L.lire_json(racine / "etat/affaire.json", {}) or {}
    ids = [str(x).strip() for x in (a.get("consignes") or {}).get("identifiants_prives", []) if str(x).strip()]
    return [i for i in ids if len(i) >= 4]


def pre_tool(ev: dict) -> None:
    racine = racine_evenement(ev)
    if racine is None:
        sys.exit(0)
    outil = ev.get("tool_name", "")
    ti = ev.get("tool_input") or {}
    plugin = os.environ.get("CLAUDE_PLUGIN_ROOT", "<plugin>")
    if outil in ("WebFetch", "WebSearch") or outil.startswith(("mcp__librejustice__", "mcp__hal__", "mcp__shs_fr__", "mcp__academic_papers__", "mcp__asta__")):
        brut = json.dumps(ti, ensure_ascii=False).lower()
        fuites = [i for i in identifiants_prives(racine) if i.lower() in brut]
        if fuites:
            refuser(f"Requête publique refusée : elle contient {len(fuites)} identifiant(s) privé(s) du client (etat/affaire.json, consignes.identifiants_prives). "
                    "Reformuler avec des termes juridiques et des identifiants publics seulement.")
        sys.exit(0)
    if outil in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        cible = ti.get("file_path") or ti.get("notebook_path")
        rel = L.relatif(racine, cible) if cible else None
        if rel is None:
            # Un acte rédigé hors du dossier (répertoire temporaire de la session...) échappe à la lecture mécanique et au contrôle.
            import controles_campagne as CAMPAGNE
            if cible and outil == "Write" and CAMPAGNE.est_acte(str(ti.get("content") or "")):
                refuser(f"Un acte de l'affaire s'écrit dans le dossier, sous {racine.as_posix()}/ecritures/brouillons/, où la lecture mécanique "
                        "et le contrôle avant dépôt s'appliquent. L'écrire à ce chemin, même pour un simple projet.")
            sys.exit(0)
        rel_l = rel.lower()
        for motif, message in PROTEGES:
            if motif.search(rel_l):
                refuser(message.replace("<plugin>", plugin))
        # Les rapports des lecteurs indépendants ne s'écrivent que par eux : la session principale
        # ne peut pas fabriquer une lecture à froid favorable ni clore une contradiction à leur place.
        agent = str(ev.get("agent_type") or "")
        if rel_l.startswith("pieces/analyses/") and not agent.endswith("analyste-documentaire"):
            refuser("Les fiches d'analyse ne s'écrivent que par le sous-agent analyste-documentaire, qui lit la pièce en entier sans le récit du client. "
                    "Le relancer sur la cote (skill analyse-documentaire) ; une fiche en erreur se refait, elle ne se corrige pas à la main.")
        if rel_l.startswith("recherche/fiches/") and not agent.endswith("lecteur-de-texte"):
            refuser("Les fiches de lecture ne s'écrivent que par le sous-agent lecteur-de-texte, qui lit la source dans l'outil et recopie ses extraits "
                    "depuis le registre des lectures. Le lancer sur la source (skill recherche-juridique, section 5).")
        if rel_l == "strategie/revue_charpente.json" and outil == "Write" and not agent.endswith("architecte-strategique"):
            refuser("La revue de charpente ne s'écrit que par le sous-agent architecte-strategique ; la session principale peut seulement porter le statut des points par Edit.")
        if rel_l in ("strategie/theorie_adverse.md", "strategie/theorie_adverse.json") and not agent.endswith("avocat-adverse"):
            refuser("La théorie adverse ne s'écrit que par le sous-agent avocat-adverse, à partir des seules pièces : "
                    "elle sert d'épreuve à notre théorie et ne peut pas être ajustée par la session principale.")
        for suffixe, auteur in ((".lecture_froid", "juge-simule"), (".rapport_rapporteur", "rapporteur-simule"), (".contradiction", "contradicteur"),
                                (".lecture_profane", "lecteur-profane")):
            # Le rapport et ses variantes (seconde lecture, collège : .lecture_froid_2.json, .lecture_froid_c3.json).
            if rel_l.startswith("ecritures/controle/") and re.search(re.escape(suffixe) + r"(_[a-z0-9]+)?\.json$", rel_l) and not agent.endswith(auteur):
                if outil == "Write" or auteur != "contradicteur":
                    refuser(f"Ce rapport ne s'écrit que par le sous-agent {auteur}. Le lancer ; la session principale peut seulement "
                            "porter le statut des points de contradiction (applique, rejete_motive) par Edit.")
        sys.exit(0)
    if outil in ("Bash", "PowerShell"):
        cmd = ti.get("command") or ""
        final = commande_depot(cmd)
        if final is not None:
            m = re.search(r"--accord\s+(\"([^\"]+)\"|'([^']+)')", cmd)
            accord = (m.group(2) or m.group(3)).strip() if m else ""
            if len(accord) < 12 or len(accord.split()) < 3:
                refuser("Dépôt non consigné : l'accord passé à --accord doit recopier la phrase du client qui autorise cet acte (trois mots au moins), "
                        "pas un mot isolé comme « oui » qu'un message quelconque peut contenir.")
            entrees = messages_utilisateur(transcript(ev))
            messages = [t for _, t in entrees]
            idx = next((i for i in range(len(messages) - 1, -1, -1) if accord in messages[i]), None)
            if idx is None:
                refuser("Dépôt non consigné : les mots d'accord passés à --accord ne figurent dans aucun message du client de cette conversation. "
                        "Recopier exactement son accord pour cet acte, ou le lui demander.")
            chemin_final = (racine / final) if not Path(final).is_absolute() else Path(final)
            quand = L.parse_date(str(entrees[idx][0] or "").replace("Z", "+00:00"))
            if chemin_final.is_file() and quand is not None:
                cree = datetime.fromtimestamp(chemin_final.stat().st_mtime, tz=quand.tzinfo or timezone.utc)
                if quand < cree:
                    refuser("Dépôt non consigné : l'accord cité précède la version finale de l'acte. Montrer au client la version finalisée "
                            "et recueillir son accord sur celle-ci.")
            posterieurs = [t for t in messages[idx + 1:] if RETENUE.search(t)]
            if posterieurs:
                refuser("Dépôt suspendu : un message du client postérieur à son accord demande d'attendre ou de ne pas déposer "
                        f"(« {posterieurs[-1][:160]} »). Lui reposer la question en clair.")
        if CHEMINS_SENSIBLES.search(cmd) and DESTRUCTIF.search(cmd) and not re.search(r"affaire\.py|gate\.py|pieces\.py", cmd):
            refuser("Commande refusée : elle peut modifier une pièce originale, le journal, la constitution, une version finale ou un verdict de contrôle. "
                    "Passer par affaire.py ou gate.py ; une lecture (cat, Get-Content, rg) reste permise si elle n'écrit rien.")
    sys.exit(0)


OUTILS_SAVANTS = ("mcp__academic_papers__", "mcp__hal__", "mcp__shs_fr__", "mcp__asta__")


def skill_charge(entrees: list[dict], nom: str) -> bool:
    for e in entrees:
        for b in ((e.get("message") or {}).get("content") or []) if e.get("type") == "assistant" else []:
            if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "Skill" and nom in str((b.get("input") or {}).get("skill")):
                return True
    return False


# Aiguillage contrôlé, dérivé des contrats d'exercice. La règle qui décide d'un exercice est dans sa fiche et dans son skill, et
# la table de routage du briefing ne suffit pas : au banc du 20 novembre, les pronostics d'urgence faux venaient de sessions qui
# n'avaient chargé aucun skill. Les marqueurs de chaque fiche (`marqueurs_texte`) reconnaissent l'exercice dans la réponse ;
# une réponse qui en traite sans avoir lu sa fiche ni chargé son skill est renvoyée une fois. Une fiche nouvelle est couverte
# d'office, sans code nouveau.
SKILL_DE_L_EXERCICE = {
    **dict.fromkeys(("refere_suspension", "refere_liberte", "refere_mesures_utiles", "refere_provision_admin", "refere_instruction_admin"),
                    "refere-administratif"),
    **dict.fromkeys(("refere_civil_834", "refere_civil_835_provision", "refere_civil_835_trouble", "mesure_instruction_145", "refere_prudhommal"),
                    "refere-civil"),
    **dict.fromkeys(("pourvoi_civil", "pourvoi_penal", "cassation_conseil_etat"), "cassation"),
    **dict.fromkeys(("requete_annulation", "plein_contentieux_indemnitaire", "assignation_fond", "conclusions_mise_en_etat",
                     "appel_administratif", "appel_civil"), "contentieux-du-fond"),
    "qpc": "controle-de-la-norme",
}


def skill_lu(entrees: list[dict], nom: str) -> bool:
    if skill_charge(entrees, nom):
        return True
    for e in entrees:
        for b in ((e.get("message") or {}).get("content") or []) if e.get("type") == "assistant" else []:
            if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "Read" and \
                    f"skills/{nom}/" in str((b.get("input") or {}).get("file_path", "")).replace("\\", "/"):
                return True
    return False


def fiche_lue(entrees: list[dict], fichier: str) -> bool:
    for e in entrees:
        for b in ((e.get("message") or {}).get("content") or []) if e.get("type") == "assistant" else []:
            if isinstance(b, dict) and b.get("type") == "tool_use" and str((b.get("input") or {}).get("file_path", "")).replace("\\", "/").endswith(
                    "references/" + fichier):
                return True
    return False


def _applicable(element, contexte: str) -> bool:
    """Une ligne sans marqueurs vaut toujours ; une ligne marquée, seulement si le dossier en montre un."""
    marqueurs = element.get("marqueurs") if isinstance(element, dict) else None
    # Une règle postérieure à la date du dossier ne s'y applique pas (horloge du poste, ou CONTENTIEUX_MAINTENANT pour un rejeu).
    depuis = str(element.get("depuis") or "")[:10] if isinstance(element, dict) else ""
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", depuis) and depuis > L.maintenant().date().isoformat():
        return False
    # Garde de domaine : une ligne propre à un sous-domaine (agent public, permis, titre de séjour...) exige que le dossier en relève.
    exige = element.get("exige") if isinstance(element, dict) else None
    if exige and not any(re.search(g, contexte, re.I) for g in exige):
        return False
    return not marqueurs or any(re.search(m, contexte, re.I) for m in marqueurs)


def contrat_compact(d: dict, fiche: Path, contexte: str = "") -> str:
    """Ce qui décide de l'exercice, en quelques lignes : condition principale, ce qui la fait tomber et ce qui la remplit, présomptions
    et leur renversement, taux publiés. Les deux côtés : un contrat qui ne montrait que les causes d'échec laissait l'agent juger
    contre le requérant ce que le juge accordait (banc du 22 novembre : sur les référés accordés, un « non » sur quatre). Les lignes
    marquées ne viennent que si la demande, la réponse ou les pièces lues les rendent applicables : le contrat reste compact."""
    lignes = [f"« {d.get('intitule')} ». Condition principale : {d.get('condition_principale')}."]
    conditions = d.get("conditions_decisives") or []
    for c in conditions[:2]:
        # Cinq lignes au plus : d'abord celles que le dossier déclenche par un marqueur (trois au plus), plus précises, puis les
        # lignes générales.
        items = [x for x in c.get("ce_qui_la_fait_tomber") or [] if _applicable(x, contexte)]
        marquees = [x for x in items if isinstance(x, dict) and x.get("marqueurs")]
        choix = (marquees[:3] + [x for x in items if x not in marquees])[:5]
        tombe = "; ".join(x["texte"] if isinstance(x, dict) else str(x) for x in choix)
        lignes.append(f"Ce qui fait tomber « {c.get('condition')} » : {tombe}")
    # Ce qui remplit chaque condition, quatre lignes applicables au plus : les cas accordés tiennent souvent à une condition qui n'est
    # pas la première (l'atteinte manifestement illégale du référé-liberté).
    reste = 4
    for c in conditions:
        remplit = [x["texte"] if isinstance(x, dict) else str(x) for x in c.get("ce_qui_la_remplit") or [] if _applicable(x, contexte)][:reste]
        if remplit:
            lignes.append(f"Ce qui remplit « {c.get('condition')} » : " + " ; ".join(remplit))
            reste -= len(remplit)
    # Points où les juges se partagent : ni cause d'échec ni cause de succès, un argument à peser (deux au plus).
    disputes = [(c.get("condition"), x["texte"]) for c in conditions for x in c.get("points_disputes") or []
                if isinstance(x, dict) and _applicable(x, contexte)][:2]
    if disputes:
        lignes.append("Juges partagés : " + " ; ".join(f"« {n} » : {t}" for n, t in disputes))
    # Indices de procédure que l'agent lisait comme un pronostic (banc du 22 novembre : la dispense de conclusions lue comme
    # l'annonce d'un rejet, 12 réponses justes sur 27 qui l'invoquaient) : rappeler qu'ils n'en sont pas un.
    neutres = [x["texte"] for x in d.get("indices_neutres") or [] if isinstance(x, dict) and _applicable(x, contexte)][:2]
    if neutres:
        lignes.append("Indices sans valeur pronostique : " + " ; ".join(neutres))
    presomptions = [p for p in d.get("presomptions") or [] if isinstance(p, dict) and _applicable(p, contexte)]
    if presomptions:
        # La source ne s'ajoute que si le renversement ne cite pas déjà ses textes et ses arrêts (présomption du séjour réécrite le
        # 23 novembre 2026 : 700 caractères de sources répétées).
        lignes.append("Présomptions : " + " ".join(
            f"{p.get('cas')} Renversement : {p.get('renversement')}"
            + ("." if re.search(r"\((?:CE|Cass|CJA|CESEDA|CRPA|C\. ?civ)", str(p.get('renversement') or "")) else f" ({p.get('source')}).")
            for p in presomptions[:5]))
    try:
        stats = re.search(r"## 10\. Statistiques publiées\s*(.*?)(?=\n## )", fiche.read_text(encoding="utf-8"), re.S).group(1)
        # Seules les puces qui portent un taux : les volumes d'affaires n'éclairent pas l'issue et occupaient le budget du contrat.
        # Hors des exercices de cassation, ni l'admission des pourvois, ni le taux de couverture (jugées sur enregistrées), ni le
        # premier ressort d'une autre juridiction : l'agent les lisait comme le taux de succès de sa demande (audit du 23 novembre
        # 2026 : « 14,5 % » des pourvois contre les référés remis pour chaque référé-liberté).
        hors_sujet = None if "cassation" in str(d.get("id") or "") else re.compile(
            r"pourvoi|admission des|taux de couverture|premier ressort", re.I)
        puces = [l[2:] for l in stats.splitlines() if l.startswith("- ") and "%" in l
                 and re.search(r"taux|rejet|annul|admis|admission|accueil|succès|satisfaction|cassation", l, re.I)
                 and not (hors_sujet and hors_sujet.search(l))][:3]
        if puces:
            lignes.append("Taux publiés : " + " ; ".join(puces))
    except (AttributeError, OSError):
        pass
    # Les numéros des décisions de la fiche ne passent pas au contrat : l'agent les citait sans les avoir lues (audit du
    # 23 novembre : 240 réponses finales sur 904 sessions bloquées). La règle reste, avec sa juridiction et sa date.
    return re.sub(r"\s*,?\s*n°\s*[\w][\w.\-/]*", "", " ".join(lignes))


def candidats_d_exercice() -> list[tuple]:
    import exercices as EXERCICES
    import missions as MISSIONS
    candidats = [(i, d, EXERCICES.REFERENCES / d["fichier"], SKILL_DE_L_EXERCICE.get(i), False)
                 for i, d in EXERCICES.charger_catalogue().items()]
    candidats += [(i, d, MISSIONS.SKILLS / d["pole"] / "references" / d["fichier"], d["pole"], True)
                  for i, d in MISSIONS.charger_missions().items()]
    return candidats


def reconnaitre_exercice(*textes: str):
    """Premier texte qui nomme un exercice : (identifiant, données, chemin de la fiche, skill, mission) ou None."""
    candidats = candidats_d_exercice()
    for texte in textes:
        if not texte:
            continue
        rang = sorted(((sum(1 for m in d.get("marqueurs_texte") or [] if re.search(m, texte, re.I)), i in RECOURS[:3], mission, i, d,
                        chemin, skill) for i, d, chemin, skill, mission in candidats), key=lambda x: (-x[0], not x[1], x[2]))
        if rang and rang[0][0]:
            _, _, mission, i, d, chemin, skill = rang[0]
            return i, d, chemin, skill, mission
    return None


ENTETE_CONTRAT_PREALABLE = "Ce qui décide de cet exercice, tiré de sa fiche, à prendre en compte avant de juger :"


def contrat_deja_donne(entrees: list[dict]) -> bool:
    return any(ENTETE_CONTRAT_PREALABLE in json.dumps(e.get("attachment") or {}, ensure_ascii=False) for e in entrees
               if e.get("type") == "attachment" or e.get("attachment"))


def contrat_a_la_lecture(racine: Path, ev: dict) -> None:
    """Banc du 22 novembre : le contrat n'arrivait qu'après la première réponse, par le blocage de fin de tour, et la révision
    changeait l'issue dans les deux sens (référés : 2 fois vers la bonne, 5 vers la mauvaise). Il est donné désormais à la
    première lecture d'une pièce du dossier, avant tout jugement, une fois par session."""
    drapeau = racine / "etat" / ".contrat_donne"
    session = str(ev.get("session_id") or "")
    if drapeau.is_file() and drapeau.read_text(encoding="utf-8").strip() == session:
        return
    cible = str((ev.get("tool_input") or {}).get("file_path") or "").replace("\\", "/")
    if not cible or "/plugins/" in cible or "/skills/" in cible or not L.relatif(racine, cible):
        return
    entrees = transcript(ev)
    lu = ev.get("tool_response")
    lu = lu if isinstance(lu, str) else json.dumps(lu, ensure_ascii=False)
    demande = " ".join(demande_du_client(entrees))
    trouve = reconnaitre_exercice(demande, lu[:20000])
    if not trouve:
        return
    i, d, chemin, skill, mission = trouve
    contrat = contrat_compact(d, chemin, demande + "\n" + lu)
    drapeau.parent.mkdir(parents=True, exist_ok=True)
    drapeau.write_text(session, encoding="utf-8")
    contexte("PostToolUse", f"{ENTETE_CONTRAT_PREALABLE}\n{contrat}\nJuger au siège du juge, des deux côtés : ce qui fait tomber "
             "la condition ne vaut que si le dossier en montre les faits, et l'absence d'une cause d'échec ne vaut pas succès.")


def aiguillage(msg: str, entrees: list[dict]) -> list[str]:
    """Une réponse qui traite d'un exercice sans avoir lu sa mécanique reçoit son contrat compact, au lieu d'être renvoyée à la
    lecture de la fiche entière (banc du 20 novembre : la lecture forcée coûtait 26 % de plus sans changer une réponse)."""
    import exercices as EXERCICES
    # Un seul exercice : le mieux reconnu, le recours l'emportant à égalité. Une réponse sur un pourvoi qui cite les articles 908
    # à 910 recevait aussi le contrat de l'appel civil (pilote du 20 novembre) : un tour de plus pour l'écarter.
    import missions as MISSIONS
    # Les missions de conseil (pôles de skills/, docs/CONSEIL.md) passent par le même aiguillage ; à égalité, l'exercice l'emporte,
    # pour que les réponses contentieuses reçoivent le contrat qu'elles recevaient avant l'intégration du conseil.
    candidats = [(i, d, EXERCICES.REFERENCES / d["fichier"], SKILL_DE_L_EXERCICE.get(i), False)
                 for i, d in EXERCICES.charger_catalogue().items()]
    candidats += [(i, d, MISSIONS.SKILLS / d["pole"] / "references" / d["fichier"], d["pole"], True)
                  for i, d in MISSIONS.charger_missions().items()]
    def classer(texte: str):
        return sorted(((sum(1 for m in d.get("marqueurs_texte") or [] if re.search(m, texte, re.I)), i in RECOURS[:3], mission, i, d,
                        chemin, skill) for i, d, chemin, skill, mission in candidats), key=lambda x: (-x[0], not x[1], x[2]))
    # La demande d'abord (audit du 23 novembre : en partant de la réponse, 73 exercices mal reconnus sur 1 108 ; 4 en partant de la
    # demande), puis la réponse, puis le dossier lu.
    reconnus = classer(" ".join(demande_du_client(entrees)))
    if reconnus and not reconnus[0][0]:
        reconnus = classer(msg)
    if reconnus and not reconnus[0][0]:
        # Ni la réponse ni la demande ne nomment l'exercice (« le tribunal annulera-t-il ? ») : le dossier lu le nomme (banc du
        # 22 novembre : requête en annulation reconnue dans 9 sessions sur 58, contrat et lignes de la fiche jamais transmis).
        reconnus = classer(lectures_de_la_session(entrees))
    if not reconnus or not reconnus[0][0]:
        return []
    _, _, mission, i, d, chemin, skill = reconnus[0]
    # Le skill chargé ne contient pas le contrat de la fiche (audit : référé-suspension juste à 67 % sans contrat, 76 % avec).
    if fiche_lue(entrees, d["fichier"]) or contrat_deja_donne(entrees):
        return []
    contrats = contrat_compact(d, chemin, msg + "\n" + "\n".join(demande_du_client(entrees)) + "\n" + lectures_de_la_session(entrees))
    if mission:
        return [f"La réponse traite une mission de conseil sans en avoir lu la fiche. Voici ce qui en décide, tiré de "
                f"skills/{d['pole']}/references/{d['fichier']} :\n" + contrats +
                "\nRevoir la réponse au regard de ces points, de la meilleure position de l'autre partie et de l'autorité qui pourra en "
                "connaître : la changer si l'un d'eux s'applique au dossier, la maintenir sinon en une ligne qui dit pourquoi. Commencer "
                "la réponse revue par la conclusion demandée."]
    return ["La réponse tranche un exercice sans en avoir lu la mécanique. Voici ce qui en décide, tiré de sa fiche :\n" + contrats +
            "\nRevoir la réponse au siège du juge, au regard de ces points, des deux côtés, et de la meilleure réponse adverse : "
            "l'absence d'une cause d'échec ne vaut pas succès, il faut encore ce qui remplit la condition, et une cause d'échec ne vaut "
            "rien si le dossier n'en montre pas les faits. Garder l'issue si elle tient alors, la changer sinon, en une ligne qui dit "
            "pourquoi. Commencer la réponse revue par l'issue demandée."]


RECOURS = ("pourvoi_civil", "pourvoi_penal", "cassation_conseil_etat", "appel_civil", "appel_administratif", "appel_penal")


# Lire avant de juger. Seule l'information devant l'agent a déplacé son jugement au banc du 20 novembre : arrêt attaqué joint, la
# cassation gagne 15 points ; décision attaquée exigée (v21), Brier de 0,168 à 0,124, 16 pourvois sur 18 améliorés. Chaque fiche
# déclare dans `a_lire` ce qui s'acquiert avant tout pronostic ; une primitive dit comment le vérifier et quoi faire sinon. La jurisprudence de
# la formation, éprouvée sur les pourvois (v22), n'a rien apporté (p = 0,71, coût + 24 %) et a été retirée. Ajouter
# une information revient à écrire une primitive, mesurée sur une famille de l'usine où elle est retirée mais trouvable.
def _appels(entrees: list[dict]):
    for e in entrees:
        for b in ((e.get("message") or {}).get("content") or []) if e.get("type") == "assistant" else []:
            if isinstance(b, dict) and b.get("type") == "tool_use":
                yield b.get("name"), (b.get("input") or {})


def _decision_attaquee_lue(entrees: list[dict]) -> bool:
    return any(n == "mcp__librejustice__get_decision" or (n == "Read" and "/pieces/" in str(i.get("file_path", "")).replace("\\", "/"))
               for n, i in _appels(entrees))


PRIMITIVES = {
    "decision_attaquee": (_decision_attaquee_lue,
                          "la décision attaquée, lue en entier (lien donné par le dossier, ou recherche par juridiction et date) : le juge "
                          "du recours juge ce qu'elle constate et décide, non la présentation qu'en fait le moyen"),
}


def informations_a_acquerir(msg: str, entrees: list[dict]) -> str | None:
    """Filet procédural : un pronostic d'issue sur un exercice exige ce que son contrat déclare à lire."""
    if not re.match(r"\W*(?:oui|non)\b", msg, re.I):
        return None
    import exercices as EXERCICES
    exiges = []
    for i, d in EXERCICES.charger_catalogue().items():
        if d.get("a_lire") and any(re.search(m, msg + "\n" + " ".join(demande_du_client(entrees)), re.I)
                                   for m in d.get("marqueurs_texte") or []):
            exiges += [p for p in d["a_lire"] if p in PRIMITIVES and p not in exiges]
    manque = [PRIMITIVES[p][1] for p in exiges if not PRIMITIVES[p][0](entrees)]
    if not manque:
        return None
    return ("Pronostic rendu sans avoir lu ce que le juge lira : " + " ; ".join(manque) + ". L'acquérir maintenant, puis revoir l'issue "
            "sur ce qui a été lu. Commencer la réponse revue par l'issue.")


def presomptions_a_plaider(texte: str) -> str | None:
    """Un acte qui engage un exercice doté de présomptions les reçoit à l'écriture, tant qu'il ne les plaide pas. Banc du 21 novembre :
    une requête en référé sur trois, rédigée sans lire la fiche, plaidait la privation de traitement sans la présomption d'urgence."""
    if re.search(r"pr[ée]sum", texte, re.I):
        return None
    import exercices as EXERCICES
    # Seulement pour l'exercice que le texte engage : un recours contre une ordonnance de tri citait l'article L. 521-1 au passage et
    # aurait reçu les présomptions du référé-suspension (contrôle des traces du banc de livraison, 21 novembre).
    scores = {i: sum(1 for m in d.get("marqueurs_texte") or [] if re.search(m, texte, re.I)) for i, d in EXERCICES.charger_catalogue().items()}
    haut = max(scores.values(), default=0)
    for i, d in EXERCICES.charger_catalogue().items():
        if d.get("presomptions") and haut and scores[i] == haut:
            p = [f"{x.get('cas')} Renversement : {x.get('renversement')} ({x.get('source')})" for x in d["presomptions"]]
            return (f"Présomptions de l'exercice « {d.get('intitule')} » (fiche {d.get('fichier')}) : à plaider expressément si le dossier "
                    "entre dans l'une d'elles, car elles reportent la charge sur l'adversaire.\n- " + "\n- ".join(p))
    return None


# Titres exigés de la fiche rapide du négociateur (agents/negociateur.md). Banc du 21 novembre : une fiche sur deux omettait les
# relations qui survivront au litige, et la réponse au client les perdait avec elle.
SECTIONS_FICHE_NEGOCIATION = (("Relations qui survivront au litige", r"relations?\s+qui\s+surviv"),
                              ("Ce que l'écrit fait voir à l'adversaire de son coût", r"co[uû]t"),
                              ("À reprendre dans la réponse", r"reprendre\s+dans\s+la\s+r[ée]ponse"))


def sections_manquantes_negociation(texte: str) -> list[str]:
    titres = " ".join(l for l in texte.splitlines() if l.lstrip().startswith("#"))
    return [n for n, m in SECTIONS_FICHE_NEGOCIATION if not re.search(m, titres, re.I)]


DEMANDE_DE_NEGOCIATION = re.compile(r"n[ée]goci|transaction|amiable|m[ée]diation|sans proc[èe]s|conc[ée]d|contrepartie|proposition d.accord", re.I)


def demande_du_client(entrees: list[dict]) -> list[str]:
    """Les messages du client dans la session, sans les messages techniques (retours de hook, skills chargés, balises)."""
    demande = []
    for e in entrees:
        if e.get("type") != "user" or e.get("isMeta"):
            continue
        c = (e.get("message") or {}).get("content")
        textes = [c] if isinstance(c, str) else [b.get("text", "") for b in c or [] if isinstance(b, dict) and b.get("type") == "text"]
        demande += [t for t in textes if t and not re.match(r"\s*(?:Stop hook|<|Base directory for this skill)", t)]
    return demande


def negociation_sans_fiche(racine: Path, entrees: list[dict]) -> str | None:
    """Une demande de négociation exige l'analyse des parties par le négociateur, en fiche rapide, avant la réponse. Les consignes du
    briefing n'ont pas suffi (dernier cycle du 20 novembre : contraintes de l'EHPAD omises, coût d'un échec de l'accord non montré au GAEC)."""
    # La demande du client seule : ni les skills chargés, ni le briefing (« voie amiable »), ni le retour d'un contrôle.
    demande = []
    for e in entrees:
        if e.get("type") != "user" or e.get("isMeta"):
            continue
        c = (e.get("message") or {}).get("content")
        textes = [c] if isinstance(c, str) else [b.get("text", "") for b in c or [] if isinstance(b, dict) and b.get("type") == "text"]
        demande += [t for t in textes if t and not re.match(r"\s*(?:Stop hook|<|Base directory for this skill)", t)]
    if not DEMANDE_DE_NEGOCIATION.search(" ".join(demande)):
        return None
    fiche = racine / "strategie" / "negociation_fiche.md"
    debut = float((L.lire_json(racine / "etat/.session.json", {}) or {}).get("debut_epoch") or 0)
    if fiche.is_file() and fiche.stat().st_mtime >= debut:
        return None
    return ("Réponse de négociation sans analyse des parties. Lancer d'abord, au premier plan, le sous-agent contentieux:negociateur en fiche "
            "rapide sur le dossier (strategie/negociation_fiche.md), puis rendre la réponse à partir de sa fiche : ce qui contraint chaque "
            "institution, la solution de repli de chacun et ce que l'échec de l'accord coûterait à l'adversaire, que l'écrit lui fait voir "
            "comme un fait, ce qu'il peut accorder sans perdre la face, les relations qui survivront au litige et ce qu'elles imposent.")


def aide_doctrine(ev: dict, outil: str, LECTURES) -> str | None:
    if outil == "mcp__librejustice__get_decision":
        doc = LECTURES.decoder(ev.get("tool_response"))
        concl = [c for c in (doc.get("commentaries") or []) if isinstance(c, dict) and c.get("kind") == "conclusions"] if isinstance(doc, dict) else []
        if not concl:
            return None
        lien = concl[0].get("url") or ""
        return (f"Conclusions publiées pour {doc.get('title') or 'cette décision'} : {lien}"
                + (" (PDF : même adresse suivie de ?download_pdf)" if "arianeweb" in lien.lower() else "")
                + ". Si la décision commande la réponse, opère un revirement ou fonde la thèse adverse, lire ces conclusions avant de s'y fonder : "
                "elles donnent le fondement exact de la solution et sa portée voulue (skill recherche-doctrinale).")
    if outil.startswith(OUTILS_SAVANTS) and not skill_charge(transcript(ev), "recherche-doctrinale"):
        return ("Recherche savante engagée sans la méthode de doctrine : charger le skill recherche-doctrinale. Chaque travail cité porte "
                "sa référence vérifiée avec un identifiant (DOI, HAL, NNT), et pour une étude empirique sa population, sa méthode et ses "
                "limites, avant que l'adversaire ne les oppose. Un fait d'expérience se prouve aussi par une voie probatoire (expertise, "
                "consultation d'un technicien, audition), à proposer.")
    return None


def aide_texte(outil: str, doc) -> str | None:
    """Banc du 20 novembre : la vue d'ensemble d'un décret modificatif n'affiche pas ses articles modificatifs
    (le décret n° 2026-302 annonce 9 articles et n'en montre que 1, 8 et 9). L'article qui crée la formalité nouvelle
    (notification du recours à peine d'irrecevabilité) restait donc ignoré."""
    if outil != "mcp__librejustice__get_norm" or not isinstance(doc, dict):
        return None
    arts, total = doc.get("articles"), doc.get("article_count")
    if not isinstance(arts, list) or not isinstance(total, int) or len(arts) >= total:
        return None
    vus = {str(a.get("number")) for a in arts if isinstance(a, dict)}
    base = str(doc.get("url") or "").rstrip("/")
    manquants = [str(n) for n in range(1, total + 1) if str(n) not in vus] if all(v.isdigit() for v in vus) else []
    liste = (", ".join(f"{base}/{n}" for n in manquants) if manquants and base
             else "chaque article absent, par son numéro, à l'adresse du texte suivie de /<numéro>")
    return (f"{doc.get('title') or 'Ce texte'} compte {total} articles ; cette vue n'en affiche que {len(arts)}. Les articles absents sont "
            "d'ordinaire les articles modificatifs : ce sont eux qui créent ou réécrivent les dispositions du code (formalité, délai, "
            "irrecevabilité, compétence). Les lire tous, en appels parallèles dans un même message, avant de conclure sur ce que le texte prévoit : " + liste
            + ". Puis lire dans le code, à la date de l'acte, chaque article qu'ils créent ou modifient.")


def post_tool(ev: dict) -> None:
    racine = racine_evenement(ev)
    if racine is None:
        sys.exit(0)
    outil = str(ev.get("tool_name") or "")
    if outil == "Read":
        try:
            contrat_a_la_lecture(racine, ev)
        except Exception:  # noqa: BLE001
            pass  # le contrat de fin de tour reste le filet
        sys.exit(0)
    if outil.startswith("mcp__"):
        # Registre des lectures : chaque appel LibreJustice et read_document est capturé avec sa réponse brute.
        import lectures as LECTURES
        if LECTURES.est_capturable(outil):
            try:
                LECTURES.capturer(racine, ev)
            except Exception as e:  # noqa: BLE001
                contexte("PostToolUse", f"Lecture non capturée ({type(e).__name__} : {e}) : elle ne figure pas au registre des lectures ; la refaire.")
        # Banc du 20 novembre : sans le skill de doctrine, l'agent ne lit pas les conclusions qu'on lui signale
        # et cite des études sans identifiant, sans population ni limites, sans voie probatoire.
        aides = [aide_doctrine(ev, outil, LECTURES), aide_texte(outil, LECTURES.decoder(ev.get("tool_response")))]
        if any(aides):
            contexte("PostToolUse", "\n\n".join(a for a in aides if a))
        sys.exit(0)
    ti = ev.get("tool_input") or {}
    cible = ti.get("file_path")
    rel = L.relatif(racine, cible) if cible else None
    if rel is None:
        sys.exit(0)
    if re.fullmatch(r"recherche/fiches/[^/]+\.json", rel):
        import lectures as LECTURES
        erreurs, alertes = LECTURES.valider_fiche(racine, Path(rel).stem)
        if erreurs:
            sortie({"decision": "block", "reason": "Fiche de lecture invalide, à reprendre sur la source :\n- " + "\n- ".join(erreurs[:20])})
        if alertes:
            contexte("PostToolUse", "Fiche de lecture écrite, avec des alertes :\n- " + "\n- ".join(alertes[:10]))
        sys.exit(0)
    if re.fullmatch(r"pieces/analyses/[^/]+\.json", rel):
        import pieces as PIECES
        erreurs, alertes, _ = PIECES.valider_fiche(racine, Path(rel).stem)
        if erreurs:
            sortie({"decision": "block", "reason": "Fiche d'analyse invalide, à reprendre maintenant :\n- " + "\n- ".join(erreurs[:20])})
        if alertes:
            contexte("PostToolUse", "Fiche d'analyse écrite, avec des alertes :\n- " + "\n- ".join(alertes[:10]))
        sys.exit(0)
    if rel == "strategie/decideurs.json":
        import decideurs as DECIDEURS
        _, constats = DECIDEURS.charger(racine)
        bloquants = [f"{k['code']} : {k['message']}" for k in constats if k["gravite"] == "BLOQUANT"]
        alertes = [f"{k['code']} : {k['message']}" for k in constats if k["gravite"] == "ALERTE"]
        if bloquants:
            sortie({"decision": "block", "reason": "Profil des décideurs invalide, à reprendre maintenant :\n- " + "\n- ".join(bloquants[:20])})
        if alertes:
            contexte("PostToolUse", "Profil des décideurs enregistré, avec des alertes :\n- " + "\n- ".join(alertes[:10]))
        sys.exit(0)
    if rel == "strategie/negociation.json":
        import negociation as NEGOCIATION
        _, constats = NEGOCIATION.charger(racine)
        bloquants = [f"{k['code']} : {k['message']}" for k in constats if k["gravite"] == "BLOQUANT"]
        alertes = [f"{k['code']} : {k['message']}" for k in constats if k["gravite"] == "ALERTE"]
        if bloquants:
            sortie({"decision": "block", "reason": "Plan de négociation invalide, à reprendre maintenant :\n- " + "\n- ".join(bloquants[:20])})
        if alertes:
            contexte("PostToolUse", "Plan de négociation enregistré, avec des alertes :\n- " + "\n- ".join(alertes[:10]))
        sys.exit(0)
    if rel == "strategie/negociation_fiche.md":
        manque = sections_manquantes_negociation((racine / rel).read_text(encoding="utf-8"))
        if manque:
            sortie({"decision": "block", "reason": "Fiche de négociation incomplète : ajouter les sections " + ", ".join(f"« ## {n} »" for n in manque)
                    + " (agents/negociateur.md), puis la rendre."})
        sys.exit(0)
    if rel == "strategie/positions.json":
        import positions as POSITIONS
        _, constats = POSITIONS.charger(racine)
        bloquants = [f"{k['code']} : {k['message']}" for k in constats if k["gravite"] == "BLOQUANT"]
        alertes = [f"{k['code']} : {k['message']}" for k in constats if k["gravite"] == "ALERTE"]
        if bloquants:
            sortie({"decision": "block", "reason": "Registre des positions invalide, à reprendre maintenant :\n- " + "\n- ".join(bloquants[:20])})
        if alertes:
            contexte("PostToolUse", "Registre des positions enregistré, avec des alertes :\n- " + "\n- ".join(alertes[:10]))
        sys.exit(0)
    if re.fullmatch(r"recherche/doctrine/[^/]+\.json", rel):
        import doctrine as DOCTRINE
        constats = DOCTRINE.valider(L.lire_json(racine / rel), Path(rel).stem)
        bloquants = [f"{k['code']} : {k['message']}" for k in constats if k["gravite"] == "BLOQUANT"]
        if bloquants:
            sortie({"decision": "block", "reason": "Fiche de lecture doctrinale invalide, à reprendre maintenant :\n- " + "\n- ".join(bloquants[:20])})
        sys.exit(0)
    if rel in L.SCHEMAS:
        erreurs = L.valider_fichier(racine, rel)
        if rel == "preuves/matrice.json" and not erreurs:
            import pieces as PIECES
            erreurs, problemes, alertes = PIECES.valider_matrice(racine)
            if not erreurs and (problemes or alertes):
                contexte("PostToolUse", "Matrice des preuves enregistrée ; faits encore sans preuve conforme :\n- " + "\n- ".join((problemes + alertes)[:15]))
        if erreurs:
            sortie({"decision": "block", "reason": "Fichier d'état invalide, à corriger maintenant :\n- " + "\n- ".join(erreurs[:20])})
        sys.exit(0)
    if re.fullmatch(r"ecritures/controle/[^/]+\.fiche\.json", rel):
        import exercices as EXERCICES
        fiche = L.lire_json(racine / rel) or {}
        if isinstance(fiche, dict) and fiche.get("type_acte"):
            constats = EXERCICES.valider(fiche.get("exercice"), fiche, contexte=EXERCICES.contexte_dossier(racine))
            if constats:
                contexte("PostToolUse", "Diagnostic d'exercice de la fiche, à compléter avant le dépôt (skill mecanique-des-exercices) :\n- "
                         + "\n- ".join(f"{k['gravite']} {k['code']} : {k['message']}" for k in constats[:12]))
        sys.exit(0)
    rl = rel.lower()
    if rl.startswith("ecritures/") and rl.endswith(".md") and "/final/" not in rl and "/controle/" not in rl:
        import lint_ecriture as LINT
        fiche = L.lire_json(racine / "ecritures/controle" / (Path(rel).stem + ".fiche.json"), {}) or {}
        import gate as G
        regime = G.REGIMES.get(fiche.get("type_acte") or "", {})
        affaire = L.lire_json(racine / "etat/affaire.json", {}) or {}
        texte = (racine / rel).read_text(encoding="utf-8")
        rap = LINT.analyser(texte, refere=bool(regime.get("refere")), texte_client=bool(fiche.get("au_nom_du_client", True)),
                            ponctuation_interdite=(affaire.get("consignes") or {}).get("ponctuation_interdite_textes_client"),
                            numeros_propres={str(i.get("numero")) for i in affaire.get("instances", [])})
        graves = [k for k in rap.constats if k.gravite in ("BLOQUANT", "ALERTE")]
        import controles_campagne as CAMPAGNE
        if CAMPAGNE.acte_devant_juge_admin(texte) and not CAMPAGNE.competence_admin_lue(racine):
            graves.insert(0, LINT.Constat("COMPETENCE_PREMIER_RESSORT_NON_LUE", "BLOQUANT", CAMPAGNE.MESSAGE_COMPETENCE))
        if not fiche:
            graves.insert(0, LINT.Constat("FICHE_ABSENTE", "ALERTE", f"Pas encore de fiche ecritures/controle/{Path(rel).stem}.fiche.json (skill controle-avant-depot)."))
        lignes = []
        if graves:
            lignes = [f"Lecture mécanique de {rel} : {sum(1 for k in graves if k.gravite == 'BLOQUANT')} défaut(s) bloquant(s) au dépôt, "
                      f"{sum(1 for k in graves if k.gravite == 'ALERTE')} alerte(s)."]
            for k in graves[:15]:
                lignes.append(f"- {k.gravite} {k.code} (l. {k.ligne}) : {k.message}" + (f" « {k.extrait} »" if k.extrait else ""))
        presomptions = presomptions_a_plaider(texte)
        if presomptions:
            lignes.append(presomptions)
        if lignes:
            contexte("PostToolUse", "\n".join(lignes))
    sys.exit(0)


RE_PIECE_CITEE = re.compile(r"\bpièces?\s+(?:n[°o]\s*)?(\d{1,3})\b", re.I)
RE_DECISION_CITEE = re.compile(r"\b(\d{2}[A-Z]{2}\d{5}|\d{2}-\d{2}\.\d{3}|\d{3,6}/\d{2})\b|n°\s?(\d{5,7})\b(?!/)")


def dernier_message(entrees: list[dict]) -> str:
    for e in reversed(entrees):
        if e.get("type") != "assistant":
            continue
        contenu = (e.get("message") or {}).get("content")
        if isinstance(contenu, list):
            txt = "\n".join(b.get("text", "") for b in contenu if isinstance(b, dict) and b.get("type") == "text")
            if txt.strip():
                return txt
    return ""


def controle_lectures(racine: Path, ev: dict) -> str | None:
    """Pièces et décisions évoquées dans le dernier message sans avoir été ouvertes dans ce fil."""
    entrees = transcript(ev)
    msg = ev.get("last_assistant_message") or dernier_message(entrees)
    if isinstance(msg, dict):
        msg = json.dumps(msg, ensure_ascii=False)
    if not msg:
        return None
    lus = "\n".join(lectures(entrees)).replace("\\\\", "/").replace("\\", "/").lower()
    bordereau = {str(p.get("cote")): p.get("fichier", "") for p in (L.lire_json(racine / "pieces/bordereau.json", {}) or {}).get("pieces", [])}
    sources = {str(s.get("numero")): s for s in (L.lire_json(racine / "etat/sources.json", {}) or {}).get("sources", []) if s.get("numero")}
    propres = {str(i.get("numero")) for i in (L.lire_json(racine / "etat/affaire.json", {}) or {}).get("instances", [])}
    import lectures as LECTURES
    lues_registre = LECTURES.Registre(racine).decisions
    contenu_lu = lectures_de_la_session(entrees, limite=200000, dossier_seul=False)
    manquants = []
    for m in RE_PIECE_CITEE.finditer(msg):
        voisinage = msg[m.start():m.end() + 60].lower()
        if "non relu" in voisinage:
            continue
        cote = m.group(1)
        fichier = bordereau.get(cote, "")
        nom = Path(fichier).name.lower() if fichier else ""
        motifs = [f"{int(cote):03d}_", nom] if nom else [f"{int(cote):03d}_"]
        if not any(x and x in lus for x in motifs):
            manquants.append(f"pièce {cote}")
    for m in RE_DECISION_CITEE.finditer(msg):
        num = m.group(1) or m.group(2)
        if num in propres or "non relu" in msg[m.start():m.end() + 60].lower() or num in contenu_lu:
            continue
        s = sources.get(num)
        if not (s and s.get("lu_en_entier")) and num.lower() not in lus and LECTURES.numero(num) not in lues_registre:
            manquants.append(f"décision n° {num}")
    manquants = sorted(set(manquants))
    if not manquants:
        return None
    return ("Le message évoque des éléments qui n'ont été ni ouverts dans ce fil ni inscrits comme lus au registre : "
            + ", ".join(manquants[:15]) + ". Les ouvrir et vérifier ce qui en est dit, ou écrire « non relu » à côté de chaque mention, "
            "puis reformuler le message.")


# Toute mention des conclusions d'un rapporteur public : qu'elle les dise non lues ou en annonce le contenu, elle les tient pour
# pertinentes (banc du 20 novembre : « Elles diront si l'abandon de la décision de 2003 est formulé expressément. Il faut les lire »).
RE_CONCLUSIONS_RP = re.compile(r"conclusions[^\n]{0,80}(?:rapporteur|arianeweb)|rapporteurs? publics?[^\n]{0,80}conclusions|arianeweb", re.I)


def conclusions_reportees(racine: Path, ev: dict) -> str | None:
    """Banc du 20 novembre : l'agent voit que LibreJustice signale les conclusions de la décision qui fonde sa réponse, écrit
    qu'il faudrait les lire, et rend la réponse sans les ouvrir. Elles sont à une requête : la lecture n'est pas reportable."""
    entrees = transcript(ev)
    msg = ev.get("last_assistant_message") or dernier_message(entrees)
    if not isinstance(msg, str) or not RE_CONCLUSIONS_RP.search(msg):
        return None
    import lectures as LECTURES
    reg = LECTURES.Registre(racine)
    citees = {}
    for lues in reg.decisions.values():
        for d in lues:
            if not any(re.search(rf"\b{re.escape(str(n))}\b", msg) for n in d["numeros"]):
                continue
            for c in d["commentaires"]:
                if isinstance(c, dict) and c.get("kind") == "conclusions" and c.get("url"):
                    citees[str(c["url"])] = d["titre"]
    if not citees:
        return None
    appels = json.dumps([b.get("input") for e in entrees if e.get("type") == "assistant"
                         for b in ((e.get("message") or {}).get("content") or []) if isinstance(b, dict) and b.get("type") == "tool_use"],
                        ensure_ascii=False).lower()
    manquantes = [(u, t) for u, t in citees.items() if u.lower().rstrip("/").split("/conclusion/")[-1] not in appels]
    if not manquantes:
        return None
    return ("La réponse évoque les conclusions publiées de décisions qu'elle cite, sans les avoir ouvertes : "
            + " ; ".join(f"{t} : {u}" + ("?download_pdf" if "arianeweb" in u.lower() else "") for u, t in manquantes[:4])
            + ". Elles se lisent maintenant (téléchargement du PDF, puis extraction du texte), avant toute position qui s'appuie sur ces "
            "décisions : elles donnent le fondement exact de la solution et la portée voulue. Reprendre ensuite la réponse sur ce qu'elles disent, en français.")


# Pronostic serré rendu sans recherche. Banc du 22 novembre, 296 pronostics de référé : 96 % de réponses justes au-delà de 80 %,
# 73 % à 79 % entre 60 et 79 % ; la recherche de jurisprudence n'était faite que dans un dixième des sessions. Le harness décide
# alors seul de l'outil : une recherche contradictoire sur le point qui décide, avant de conclure.
def especes_hors_dossier(msg: str, entrees: list[dict]) -> bool:
    """Une espèce citée qui figure déjà au dossier lu (requête au fond, ordonnance visée) n'est pas une transposition."""
    lu = lectures_de_la_session(entrees, limite=200000)
    numeros = re.findall(r"n°\s*([\d][\d .\-]*\d)", msg)
    return not numeros or any(re.sub(r"\D", "", n) not in re.sub(r"\D", "", lu) for n in numeros)


def pronostic_serre(msg: str) -> int | None:
    m = re.match(r"\W*(?:oui|non)\W*,?\s*(?:à\s+|a\s+)?(\d{1,3})\s*%", msg.strip(), re.I)
    return int(m.group(1)) if m and 55 <= int(m.group(1)) <= 79 else None


def recherches_de_jurisprudence(entrees: list[dict]) -> int:
    return sum(1 for e in entrees if e.get("type") == "assistant"
               for b in ((e.get("message") or {}).get("content") or [])
               if isinstance(b, dict) and b.get("type") == "tool_use" and "search_decisions" in str(b.get("name", "")))


MESSAGE_RECHERCHE_CONTRADICTOIRE = (
    "Pronostic serré ({p} %) rendu sans recherche de jurisprudence. Avant de conclure : nommer le point qui décide (la condition "
    "la plus disputée au dossier) ; lancer deux recherches LibreJustice sur ce point, même procédure et même type de juridiction, "
    "l'une limitée aux décisions qui accueillent la demande, l'autre à celles qui la rejettent (filtre de solution), date_to au plus "
    "tard à la date du dossier ; lire en entier au moins deux décisions de chaque côté, les plus proches des faits ; dire le fait "
    "qui sépare les deux séries et de quel côté le dossier se range. Garder l'issue si elle tient, la changer sinon, et ajuster la "
    "probabilité à ce que montrent ces décisions.")


def stop(ev: dict) -> None:
    if ev.get("stop_hook_active"):
        sys.exit(0)
    racine = L.trouver_racine(ev.get("cwd") or os.getcwd())
    if racine is None:
        sys.exit(0)
    # Un seul blocage par fin de tour : la relance arrive avec stop_hook_active et n'est plus contrôlée. Toutes les alertes partent
    # donc ensemble (banc du 20 novembre : le contrôle des lectures bloquait seul, celui des conclusions ne tournait jamais).
    alertes = [a for a in (controle_lectures(racine, ev), conclusions_reportees(racine, ev)) if a]
    # Un acte rendu dans la réponse elle-même n'est passé par aucun contrôle de fichier : la compétence se vérifie ici.
    import controles_campagne as CAMPAGNE
    entrees = transcript(ev)
    msg = ev.get("last_assistant_message") or dernier_message(entrees)
    if isinstance(msg, str) and CAMPAGNE.acte_devant_juge_admin(msg) and not CAMPAGNE.competence_admin_lue(racine):
        alertes.append(CAMPAGNE.MESSAGE_COMPETENCE + " Corriger la juridiction dans l'acte si la lecture le commande, puis rendre l'acte corrigé.")
    if isinstance(msg, str):
        # Le contrat compact ne vaut que pour une réponse qui rend une issue : au banc complet de la v19, il était injecté dans 59
        # sessions sur 75 (recherche, rédaction, lettres), un tour de plus chaque fois, sans bénéfice mesuré hors du pronostic.
        if re.match(r"\W*(?:oui|non)\b", msg, re.I):
            alertes.extend(aiguillage(msg, entrees))
            if PRONOSTIC_CONDITIONNE.search(msg[:400]):
                alertes.append(MESSAGE_PRONOSTIC_CONDITIONNE)
            if ESPECE_CITEE.search(msg) and especes_hors_dossier(msg, entrees):
                alertes.append(MESSAGE_FAIT_DECISIF)
        else:
            refere = re.search(r"référé", msg, re.I)
            if echec_sans_recommandation(msg):
                alertes.append(MESSAGE_SANS_RECOMMANDATION + (COUT_DU_TRI if refere else ""))
            elif refere and ECHEC_ANNONCE.search(msg) and DEMARCHE.search(msg):
                # Recommandation présente, mais l'échec du référé est annoncé : le coût d'un dépôt prématuré doit être pesé
                # (banc du 22 novembre : « dépôt vendredi sous seule réserve de pièces procédurales »).
                alertes.append("La réponse annonce l'échec probable du référé et envisage un dépôt." + COUT_DU_TRI + " Dire si ces "
                               "pièces seront jointes au dépôt ; sinon recommander d'attendre de les avoir, ou dire pourquoi un dépôt "
                               "immédiat vaut mieux malgré ce coût.")
            alertes.extend(mesures_suivantes_oubliees(msg, entrees))
        a_lire = informations_a_acquerir(msg, entrees)
        if a_lire:
            alertes.append(a_lire)
        nego = negociation_sans_fiche(racine, entrees)
        if nego:
            alertes.append(nego)
    retours = retours_non_appliques(entrees)
    if retours:
        alertes.append(retours)
    passation = alerte_passation(racine)
    if passation:
        alertes.append(passation)
    if alertes:
        # La relance produit le texte que le lecteur recevra : il ne doit pas raconter sa correction (diagnostic du 20 novembre :
        # « Voici la réponse corrigée », comptes rendus de lecture en tête de réponse).
        sortie({"decision": "block", "reason": "\n\n".join(alertes) + "\n\nRendre ensuite la réponse entière, autonome et définitive, comme "
                "si c'était la première : ni « réponse corrigée », ni compte rendu du contrôle, ni récit des lectures faites."})
    sys.exit(0)


# Pronostic dont l'issue dépend de ce que l'adversaire produira. Banc du 20 au 22 novembre : sur 1 096 pronostics, ce tour figure en tête
# de 20 réponses, et les erreurs vont dans les deux sens (« oui, à condition que le département ne produise rien » quand il produira les
# faits qui fondent sa mesure ; « non » quand l'employeur n'avait aucune circonstance pour renverser la présomption d'urgence). La règle
# rappelée ne pousse dans aucun sens : elle distingue ce que l'adversaire détient de ce qu'il n'a que si le dossier en montre la trace.
_ADVERSAIRE = (r"(?:l['’]\s*|la\s+|le\s+|les\s+)?(?:administration|département|adversaire|défense|employeur|commune|préfet|préfecture|"
               r"état|ministre|caisse|bailleur|société|défendeur|autorité|établissement|service|partie\s+adverse)")
_VERBE = r"(?:n['’]\s*)?(?:apport|produi|prouv|justifi|établi|démontr|vers|renvers|fourni|rapport)"
PRONOSTIC_CONDITIONNE = re.compile(r"(?:sauf\s+si|à\s+moins\s+qu|à\s+(?:une\s+)?condition|sous\s+(?:une\s+)?réserve|une\s+réserve|si\s+(?:elle|il))"
                                   r"[^.]{0,60}?" + _ADVERSAIRE + r"[^.]{0,40}?" + _VERBE + r"|" + _ADVERSAIRE + r"\s+(?:peut|pourrait)\s+renverser", re.I)
MESSAGE_PRONOSTIC_CONDITIONNE = (
    "L'issue annoncée dépend de ce que l'adversaire produira. D'abord le stade. Avant sa défense, les faits sur lesquels son acte ou sa "
    "position est fondé, il les détient et les produira : refaire le pronostic en les supposant produits, et ne garder l'issue annoncée "
    "que si elle tient alors. Instruction close (défense produite ou absente, audience tenue), il ne produira plus rien : juger sur ce "
    "qui a été produit, une allégation précise et datée du requérant qu'il n'a pas contestée pesant comme établie, et ce qu'il affirme "
    "sans pièce ne l'étant pas. Une circonstance exceptionnelle qui renverserait une présomption, il ne l'a que si le dossier en montre la "
    "trace : sans trace, la supposer absente. Commencer la réponse revue par l'issue la plus probable, la branche contraire venant ensuite.")
# Échec annoncé d'une démarche que le client veut engager, et aucune recommandation. Banc du 22 novembre, exercice de l'agrément
# suspendu : deux essais sur six annonçaient le rejet du référé que la cliente voulait déposer vendredi et le laissaient « visé » ou
# « possible », sans dire s'il fallait déposer ou attendre les pièces qui changeraient l'issue ; les essais réussis le disaient. Rejoué
# sur 2 123 réponses du banc, le contrôle touche 11 réponses hors pronostic, dont ces deux échecs.
ECHEC_ANNONCE = re.compile(r"issue\s+la\s+plus\s+probable[^.]{0,40}?(?:rejet|échec)|(?:rejet|échec)\s+(?:est\s+|reste\s+)?(?:le\s+plus\s+)?"
                           r"probable|probablement\s+(?:un\s+)?rejet|(?:rejet|échec)\s+probable", re.I)
DEMARCHE = re.compile(r"\b(?:dépôt|déposer|déposons|déposerons|déposera|saisir\s+le\s+juge|introduire)\b", re.I)
RECOMMANDATION = re.compile(r"\b(?:je\s+(?:vous\s+|lui\s+)?(?:recommande|conseille|déconseille)|ma\s+recommandation|recommandation\s*:|"
                            r"nous\s+recommandons|je\s+ne\s+déposerai\s+pas|ne\s+déposons\s+pas|ne\s+pas\s+déposer)", re.I)
MESSAGE_SANS_RECOMMANDATION = (
    "La réponse annonce l'échec comme l'issue la plus probable d'une démarche que le client veut engager, sans recommander quoi faire. "
    "Recommander en clair l'une des deux voies, avec sa raison : agir à la date voulue, ou attendre ce qui changerait l'issue, en nommant "
    "les pièces ou les faits à réunir et jusqu'à quand. Dire ce que coûterait un échec immédiat, ce qu'il fermerait ou rendrait plus "
    "difficile ensuite, et ce que coûterait l'attente. Le client décide ; la recommandation reste écrite.")


# Le coût d'un référé déposé trop tôt, que la fiche connaît et que l'agent omettait en recommandant de déposer « preuve ou non »
# (banc du 22 novembre, exercice de l'agrément).
COUT_DU_TRI = (" Pour un référé : au tri, le juge ne lit que la requête et ses pièces et peut rejeter sans audience, notamment faute "
               "d'urgence (CJA, art. L. 522-3) ; une seconde demande n'est utile qu'avec des moyens ou éléments nouveaux. Les pièces qui "
               "établissent l'urgence doivent donc être jointes au dépôt.")


def echec_sans_recommandation(msg: str) -> bool:
    return bool(ECHEC_ANNONCE.search(msg) and DEMARCHE.search(msg) and not RECOMMANDATION.search(msg))


# La mesure que l'adversaire prendra ensuite. Banc du 9 au 22 novembre : la contre-offensive après une suspension d'agrément oubliait
# le retrait qui suit, devant la commission paritaire, une fois sur trois dans toutes les versions ; la troisième affaire neuve du
# 19 novembre avait déjà limité la campagne à la voie disciplinaire. La règle de conduite-de-la-sequence (section 2 bis) ne suffisait
# pas : l'information se place devant l'agent, au moment où il recommande.
TABLE_MESURES = Path(__file__).resolve().parents[1] / "skills" / "conduite-de-la-sequence" / "references" / "mesures-suivantes.json"
RECOMMANDE_DES_ACTES = re.compile(r"\b(?:je (?:vous )?recommande|je conseille|recommand\w+|dans cet ordre|d['’]abord|ensuite|à faire|"
                                  r"prochaines? étapes?|nous (?:déposons|écrivons|demandons)|demander|déposer|saisir)\b", re.I)


def _fichier_du_harness(chemin: str) -> bool:
    """Fichier du plugin ou d'un skill, par opposition aux pièces du dossier."""
    if not chemin:
        return False
    try:
        p = Path(chemin).resolve()
        if p.is_relative_to(Path(__file__).resolve().parents[1]):
            return True
    except (OSError, ValueError):
        pass
    return bool(re.search(r"[\\/](?:skills|plugins)[\\/]|SKILL\.md$", chemin, re.I))


def lectures_de_la_session(entrees: list[dict], limite: int = 40000, dossier_seul: bool = True) -> str:
    """Texte des fichiers du dossier que l'agent a lus (résultats de l'outil Read), dans la limite donnée. Les fichiers du plugin et
    des skills n'en font pas partie : une fiche lue portait elle-même les mots que ses marqueurs cherchent, et toutes ses lignes
    marquées devenaient applicables (audit du 23 novembre 2026 : la garde « renouvel » s'ouvrait sur les 120 dossiers de séjour)."""
    lus = {b.get("id") for e in entrees if e.get("type") == "assistant"
           for b in ((e.get("message") or {}).get("content") or []) if isinstance(b, dict) and b.get("type") == "tool_use"
           and b.get("name") == "Read" and not (dossier_seul and _fichier_du_harness(str((b.get("input") or {}).get("file_path") or "")))}
    morceaux = []
    for e in entrees:
        if e.get("type") != "user":
            continue
        for b in (e.get("message") or {}).get("content") or []:
            if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("tool_use_id") in lus:
                c = b.get("content")
                morceaux.append(c if isinstance(c, str) else " ".join(x.get("text", "") for x in c or [] if isinstance(x, dict)))
    return "\n".join(morceaux)[:limite]


def mesures_suivantes_oubliees(msg: str, entrees: list[dict]) -> list[str]:
    """Lignes de la table pour les mesures provisoires du dossier dont la réponse, qui recommande des actes, ne prépare pas la suite."""
    if not RECOMMANDE_DES_ACTES.search(msg):
        return []
    try:
        table = json.loads(TABLE_MESURES.read_text(encoding="utf-8"))["mesures"]
    except (OSError, ValueError, KeyError):
        return []
    # La mesure se reconnaît dans la réponse, la demande ou ce que l'agent a lu du dossier ; la préparation, dans la réponse seule.
    contexte = msg + "\n" + "\n".join(demande_du_client(entrees)) + "\n" + lectures_de_la_session(entrees)
    lignes = [m["ligne"] for m in table if any(re.search(x, contexte, re.I) for x in m["marqueurs"]) and not re.search(m["suite"], msg, re.I)]
    if not lignes:
        return []
    return ["La réponse recommande des actes sans préparer la mesure qui suivra : " + " ".join(lignes[:2]) +
            " Dire dans la réponse comment s'y préparer dès maintenant, ou pourquoi c'est inutile ici."]


# Espèce transposée sans le fait qui la portait. Banc du 22 novembre : un pronostic sur l'intérêt de l'enfant accueilli s'appuyait
# sur une ordonnance où l'urgence tenait aussi à une forte perte de revenus, absente du dossier ; la v37 avait fait la même erreur
# sur une ligne injectée. Un quart des pronostics du banc citent une décision (257 sur 1 044).
ESPECE_CITEE = re.compile(r"\b(?:TA|CAA|CE|Conseil d['’]État|tribunal administratif|cour administrative d['’]appel|Cass\.|Cour de cassation)\b"
                          r"[^.\n]{0,80}?\b(?:n°\s*)?(?:\d{5,7}|\d{2}-\d{2}\.\d{3})\b|\bn°\s*(?:\d{5,7}|\d{2}-\d{2}\.\d{3})\b|"
                          r"\b(?:TA|tribunal administratif|juge des référés|CAA|cour administrative d['’]appel|cour d['’]appel)\s+(?:de|d['’]|du)\s*"
                          r"[A-ZÉ][\w-]+[^.\n]{0,25}?\b\d{1,2}(?:er)?\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|"
                          r"novembre|décembre)\s+\d{4}", re.I)
MESSAGE_FAIT_DECISIF = (
    "La réponse s'appuie sur des décisions. Pour chaque espèce citée comme comparable : le fait qui l'a décidée, tel que ses motifs le "
    "disent, et s'il se retrouve dans ce dossier. Une espèce dont le fait décisif manque ici ne porte pas l'issue, et une espèce dont "
    "les motifs n'ont pas été lus non plus. Une décision citée pour la règle qu'elle pose n'est pas concernée. Garder l'issue si elle "
    "tient sans ces espèces, la changer sinon, et commencer la réponse revue par l'issue la plus probable.")
RELECTEURS = ("lecteur-profane", "juge-simule", "rapporteur-simule", "contradicteur", "avocat-adverse")
RE_BROUILLON = re.compile(r"ecritures[\\/]+brouillons[\\/]+([^\s\"'`)>\]]+\.md)", re.I)


def retours_non_appliques(entrees: list[dict]) -> str | None:
    """Un brouillon relu par un relecteur indépendant et jamais modifié ensuite : la relecture n'a servi à rien. Banc de constance du
    21 novembre : un essai sur trois de l'acte en chaîne finissait après le lecteur profane et le juge simulé sans toucher au brouillon,
    et l'exposé des faits restait morcelé ; les deux autres réécrivaient une version. Contrôle de fin de tour, comme le recommande
    Claude Code pour ce qui doit arriver chaque fois."""
    relu = {}
    for nom, entree in _appels(entrees):
        if nom in ("Agent", "Task") and str(entree.get("subagent_type") or "").split(":")[-1] in RELECTEURS:
            for f in RE_BROUILLON.findall(str(entree.get("prompt") or "")):
                relu[Path(f).name] = str(entree.get("subagent_type")).split(":")[-1]
        elif nom in ("Write", "Edit", "MultiEdit") and relu and RE_BROUILLON.search(str(entree.get("file_path") or "")):
            # Une écriture d'un brouillon après la relecture, version nouvelle comprise, vaut application des retours.
            relu = {}
    if not relu:
        return None
    noms = ", ".join(f"{f} (relu par {r})" for f, r in relu.items())
    return (f"Brouillon relu et jamais modifié depuis : {noms}. Appliquer au brouillon les retours des relecteurs, ou dire pour chacun "
            "pourquoi il est écarté, puis rendre la réponse.")


def alerte_passation(racine: Path) -> str | None:
    sess = L.lire_json(racine / "etat/.session.json", {}) or {}
    debut = sess.get("debut_epoch")
    if not debut:
        return None
    ignores = {"etat/.session.json", "etat/passation.md", "etat/.contrat_donne"}
    modifies = []
    for p in racine.rglob("*"):
        if p.is_file() and ".git" not in p.parts:
            rel = p.relative_to(racine).as_posix()
            # Les captures du registre des lectures sont écrites par le hook lui-même : elles ne changent pas l'état de l'affaire
            # (banc du 20 novembre : une simple question suivie d'une lecture LibreJustice forçait la réécriture de la passation).
            if (rel not in ignores and not rel.startswith(("ecritures/controle/", "recherche/lectures/"))
                    and p.stat().st_mtime > debut):
                modifies.append(rel)
    if not modifies:
        return None
    pas = racine / "etat/passation.md"
    if pas.is_file() and pas.stat().st_mtime > debut:
        return None
    return (f"Le dossier a changé pendant cette session ({len(modifies)} fichier(s), dont {', '.join(modifies[:5])}) "
            "et etat/passation.md n'a pas été mis à jour. Avant de terminer, réécrire la passation : ce qui est fait et vérifié, "
            "ce qui est en cours, les prochaines actions datées avec leur responsable, les décisions attendues du client, "
            "les sources lues et non lues. Ajouter une entrée au journal par affaire.py si un acte, une décision ou un fait nouveau est intervenu. "
            "Le message qui suit s'écrit en français, comme le reste du dossier, et ne remplace pas la réponse déjà donnée.")


def pre_compact(ev: dict) -> None:
    racine = L.trouver_racine(ev.get("cwd") or os.getcwd())
    if racine is None:
        sys.exit(0)
    a = L.lire_json(racine / "etat/affaire.json", {}) or {}
    prochaine = next((f"{e.get('objet')} le {e.get('date')}" for _, e in L.echeances_ouvertes(racine)), "aucune enregistrée")
    sys.stdout.write(
        f"Résumé d'un dossier contentieux (affaire {a.get('id')}). Conserver exactement : l'objectif du client dans ses mots ; "
        f"la prochaine échéance ({prochaine}) et les autres délais ouverts ; les décisions et accords du client avec leurs mots et leur heure ; "
        "les actes envoyés ou déposés et leurs preuves ; les objections ouvertes ; pour chaque pièce, décision ou texte évoqué, s'il a été ouvert "
        "en entier, en partie ou pas du tout pendant la session ; les chemins des fichiers modifiés ; le travail en cours et sa prochaine étape. "
        "Ne pas résumer une pièce comme lue si elle ne l'a pas été. Après la compaction, l'état sera réinjecté depuis etat/.")
    sys.exit(0)


def main() -> None:
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        ev = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)
    nom = ev.get("hook_event_name")
    {"SessionStart": session_start, "UserPromptSubmit": user_prompt, "PreToolUse": pre_tool,
     "PostToolUse": post_tool, "PreCompact": pre_compact, "Stop": stop}.get(nom, lambda e: sys.exit(0))(ev)


if __name__ == "__main__":
    main()
