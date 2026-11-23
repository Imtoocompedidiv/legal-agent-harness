"""Plan de négociation et de persuasion : validation, contrôle avant acte, squelette.

Usage (depuis un dossier d'affaire) :
  python negociation.py valider                  structure et règles de strategie/negociation.json
  python negociation.py controle <brouillon>     constats que gate.py émettrait pour cet acte
  python negociation.py squelette                structure vide du fichier, à remplir (skill negociation-et-persuasion)

La structure est décrite par references/schemas/negociation.v1.schema.json et validée par le validateur de pieces.py.
Ce module ajoute les règles qui croisent les champs ; chacune renvoie à une règle sourcée du skill
(references/droit_amiable.md D, levier_limites.md L, negociation_litterature.md N, persuasion_litterature.md P).
Bibliothèque standard seulement, aucun appel réseau.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib_affaire as L  # noqa: E402
import pieces as PIECES  # noqa: E402

FICHIER = "strategie/negociation.json"
SCHEMA = "negociation.v1.schema.json"
LUS = ("en_entier", "extraits")
SEUIL_COMITE_ETAT = 500_000  # CRPA, art. R. 423-3 (avis obligatoire du comité ministériel de transaction, art. L. 423-2)

# Effets permis de chaque voie amiable sur les délais (droit_amiable.md, D1). Une voie absente de la table n'est pas contrôlée.
EFFETS = {
    "negociation_directe": ({"aucun", "sans_objet"}, "aucun texte n'attache d'effet aux pourparlers directs"),
    "correspondance_avocats": ({"aucun", "sans_objet"}, "aucun texte n'attache d'effet aux pourparlers entre avocats"),
    "transaction": ({"aucun", "sans_objet"}, "l'offre de transaction n'a aucun effet sur les délais avant sa signature"),
    "demande_prealable": ({"aucun", "sans_objet", "interrompt"}, "CJA, art. R. 421-1"),
    "recours_administratif": ({"interrompt", "aucun", "sans_objet"}, "CRPA, art. L. 411-2 ; CJA, art. R. 213-13"),
    "mediation_administrative": ({"interrompt", "sans_objet"}, "CJA, art. L. 213-6 ; CRPA, art. L. 421-3"),
    "mediation_prealable_obligatoire": ({"interrompt"}, "CJA, art. L. 213-13"),
    "mediation_conventionnelle": ({"suspend", "sans_objet"}, "C. civ., art. 2238 : suspension de la prescription seulement"),
    "mediation_judiciaire": ({"suspend", "interrompt", "sans_objet"}, "C. civ., art. 2238 ; CPC, art. 915-3"),
    "conciliation_conciliateur": ({"suspend", "sans_objet"}, "C. civ., art. 2238 : suspension de la prescription seulement"),
    "audience_reglement_amiable": ({"interrompt_peremption", "sans_objet"}, "CPC, art. 1532, al. 3 : interruption de la péremption"),
    "procedure_participative": ({"suspend"}, "C. civ., art. 2238 et 2065"),
    "mediateur_consommation": ({"suspend", "sans_objet"}, "C. civ., art. 2238"),
    "defenseur_des_droits": ({"aucun", "interrompt", "sans_objet"}, "loi organique n° 2011-333, art. 6 ; CJA, art. L. 213-14 ; CRPA, art. L. 424-2"),
    "mesure_alternative_penale": ({"suspend", "sans_objet"}, "CPP, art. 41-1, avant-dernier alinéa"),
}
DELAIS = {"delai_contentieux", "forclusion", "prescription"}
FAMILLE_JUGE = {"juge", "juge_du_tri", "juge_des_referes", "formation_collegiale", "rapporteur_public", "juge_homologation"}

RE_PROBA = re.compile(r"(chances?|probabilit\w*)[^.;\n]{0,50}?\d+(?:[,.]\d+)?\s?%|\d+(?:[,.]\d+)?\s?%[^.;\n]{0,50}?(chances?|probabilit\w*)", re.I)
# Ce qui s'adresse à l'adversaire, au médiateur ou au juge ne reconnaît aucune faiblesse (levier_limites.md, L10).
RE_AVEU = re.compile(
    r"\b(notre|nos) (faiblesses?|points? faibles?)\b|\b(notre|son|ce) dossier (est|serait|reste|demeure) (fragile|faible|incertain)"
    r"|\bnous (reconnaissons|admettons|concédons)\b|\ble client (reconna[iî]t|admet|concède)\b"
    r"|\brisque (réel |sérieux |important )?de perdre\b|\bnous craignons\b|\bchances? (sont|restent|paraissent) (faibles|minces|limitées)"
    r"|\bpas (certains|sûrs) de (gagner|l'emporter)\b|\bmal fondée?s? sur ce point\b", re.I)
# Plainte, signalement, presse, révélation : jamais échangés contre un paiement ou une signature (C. pén., art. 312-10 ; L3, L4).
RE_MENACE = re.compile(
    r"\bplaintes?\b|\bsignalements?\b|\bparquet\b|\bprocureur\b|\bpresse\b|\bjournalis\w*|\bmédias?\b"
    r"|\bréseaux sociaux\b|\brévél(er|ation|ations|erons|erions|erait|eront)\b|\bdivulgu\w*|\brendre public\w*"
    r"|\bordre des (avocats|médecins|architectes|experts)"
    r"|\bconseil de l'ordre\b|\bpoursuites? (pénales?|disciplinaires?)\b", re.I)
RE_SANS_CONTREPARTIE = re.compile(r"^\s*(rien|aucune?|néant|sans contrepartie|à voir|-)\s*\.?\s*$", re.I)
RE_EVOCATION = re.compile(r"propositions? (transactionnelle|amiable)s?|offres? (transactionnelle|amiable)s?|\bpourparlers\b"
                          r"|(au cours|lors) de la (médiation|conciliation)|\bserait prête? à accepter\b|\baccepterait\b", re.I)
RE_DILIGENCES = re.compile(r"concili|médiat|procédure participative|dispens|750-1|L\.\s?213-11", re.I)


def _k(code: str, message: str, gravite: str = "BLOQUANT") -> dict:
    return {"code": code, "gravite": gravite, "message": message}


def _textes(v, chemin="$"):
    if isinstance(v, dict):
        for k, x in v.items():
            yield from _textes(x, f"{chemin}.{k}")
    elif isinstance(v, list):
        for i, x in enumerate(v):
            yield from _textes(x, f"{chemin}[{i}]")
    elif isinstance(v, str):
        yield chemin, v


def _adresse_a_l_exterieur(doc: dict):
    """Champs que l'adversaire, le médiateur ou le juge liront : formulation de l'offre et des contreparties, message clé."""
    f = ((doc.get("offre") or {}).get("premiere_offre") or {}).get("formulation")
    if f:
        yield "$.offre.premiere_offre.formulation", f
    for i, c in enumerate(doc.get("contreparties", [])):
        if c.get("formulation"):
            yield f"$.contreparties[{i}].formulation", c["formulation"]
    for i, p in enumerate(doc.get("persuasion", [])):
        if p.get("message_cle"):
            yield f"$.persuasion[{i}].message_cle", p["message_cle"]


def _montant(x):
    return x if isinstance(x, (int, float)) and not isinstance(x, bool) else None


def valider(doc) -> list[dict]:
    """Constats de structure et de fond sur un plan ; liste vide si le plan est exploitable."""
    if not isinstance(doc, dict):
        return [_k("NEGOCIATION_INVALIDE", f"{FICHIER} doit contenir un objet JSON.")]
    schema = PIECES.charger_schema(SCHEMA)
    out = [_k("NEGOCIATION_INVALIDE", f"{FICHIER} : {e}") for e in PIECES.valider_schema(doc, schema, schema)]
    if out:
        return out

    # Identifiants et renvois.
    vus = {}
    for col in ("parties", "voies_amiables", "options", "contreparties", "interlocuteurs", "risques", "persuasion", "sources", "objets"):
        for x in doc.get(col, []):
            if x["id"] in vus:
                out.append(_k("ID_DOUBLE", f"Identifiant {x['id']} déclaré deux fois ({vus[x['id']]} et {col})."))
            vus[x["id"]] = col
    nommes = [a for a in doc["actes_couverts"] + [a for p in doc["persuasion"] for a in p.get("actes", [])] + [a for v in doc["voies_amiables"]
              for a in v.get("actes", [])] if re.search(r"\s", a)]
    if nommes:
        out.append(_k("ACTES_NON_NOMMES", f"« {nommes[0][:80]} » : les actes se désignent par le nom de leur brouillon sans suffixe de version "
                      "(ecritures/brouillons/<nom>_vN.md), ou « * » ; une description ne permet pas au contrôle de reconnaître l'acte.", "ALERTE"))
    parties = {p["id"]: p for p in doc["parties"]}
    sources = {s["id"]: s for s in doc["sources"]}
    objets = {o["id"] for o in doc.get("objets", [])}
    for r in doc["repli"]:
        if r["partie"] not in parties:
            out.append(_k("PARTIE_INCONNUE", f"Solution de repli rattachée à {r['partie']}, absent des parties."))
    for i in doc["interlocuteurs"]:
        if i["partie"] not in parties:
            out.append(_k("PARTIE_INCONNUE", f"Interlocuteur {i['id']} rattaché à {i['partie']}, absent des parties."))
    for o in doc["options"]:
        for b in o.get("objets", []):
            if b not in objets:
                out.append(_k("OBJET_INCONNU", f"Option {o['id']} : objet {b} absent de « objets »."))

    def refs(chemin, ids):
        for sid in ids:
            if sid not in sources:
                out.append(_k("SOURCE_INCONNUE", f"{chemin} renvoie à {sid}, absente du registre des sources du plan."))

    for p in doc["parties"]:
        for j, it in enumerate(p["interets"]):
            refs(f"{p['id']}.interets[{j}]", it.get("sources", []))
    for r in doc["repli"]:
        refs(f"repli de {r['partie']}", r["sources"])
        if not any(sources.get(s, {}).get("lu") in LUS for s in r["sources"]):
            out.append(_k("SOURCE_NON_LUE", f"Solution de repli de {r['partie']} : aucune source lue en entier ou par extraits ; "
                          "le jugement probable se fonde sur des textes et des décisions lus (N6)."))
    po = doc["offre"]["premiere_offre"]
    refs("offre.premiere_offre", po["sources"])
    if not any(sources.get(s, {}).get("lu") in LUS for s in po["sources"]):
        out.append(_k("SOURCE_NON_LUE", "Première offre : aucune source lue ; le chiffre doit rester défendable devant le juge (N12, decideurs C2)."))

    # Parties : un client, un adversaire, la face de l'adversaire, la solution de repli de chacun.
    clients = [p for p in doc["parties"] if p["role"] == "client"]
    adversaires = [p for p in doc["parties"] if p["role"] == "adversaire"]
    if not clients:
        out.append(_k("CLIENT_ABSENT", "Aucune partie de rôle « client »."))
    if not adversaires:
        out.append(_k("ADVERSAIRE_ABSENT", "Aucune partie de rôle « adversaire »."))
    avec_repli = {r["partie"] for r in doc["repli"]}
    for p in clients + adversaires:
        if p["id"] not in avec_repli:
            out.append(_k("REPLI_ABSENT", f"{p['id']} ({p['designation']}) : aucune meilleure solution de repli estimée (N6, N8)."))
    for p in adversaires:
        if not p.get("sans_perdre_la_face"):
            out.append(_k("FACE_ADVERSAIRE_NON_ETUDIEE", f"{p['id']} ({p['designation']}) : ce qu'il peut accorder sans perdre la face "
                          "n'est pas écrit (N37) ; sans cela, aucune option ne lui laisse de sortie."))

    # Voies amiables : préalables obligatoires, effet sur les délais, délais protégés.
    delais_ouverts = [j for j in doc["calendrier"] if j["type"] in DELAIS and j.get("statut", "a_venir") == "a_venir" and not j.get("protege_par")]
    for v in doc["voies_amiables"]:
        nom = f"{v['id']} ({v['voie']})"
        if v["obligatoire"] and v["ouverte"] and not v["retenue"] and not v.get("dispense"):
            out.append(_k("PREALABLE_AMIABLE_NON_TENTE", f"{nom} : préalable amiable obligatoire ({v['fondement']}) ni retenu ni écarté par une "
                          "dispense motivée et sourcée ; l'acte serait irrecevable (CPC, art. 750-1 ; CJA, art. L. 213-11)."))
        permis = EFFETS.get(v["voie"])
        if permis and v["effet_sur_delais"] not in permis[0]:
            out.append(_k("EFFET_DELAI_INEXACT", f"{nom} : effet déclaré « {v['effet_sur_delais']} », effets permis {sorted(permis[0])} ({permis[1]})."))
        if v["voie"] == "defenseur_des_droits" and v["effet_sur_delais"] == "interrompt":
            out.append(_k("EFFET_DELAI_A_JUSTIFIER", f"{nom} : la saisine du Défenseur des droits n'interrompt rien par elle-même (loi organique "
                          "n° 2011-333, art. 6) ; l'interruption suppose une médiation préalable obligatoire (CJA, art. L. 213-14) ou une "
                          "médiation engagée (CRPA, art. L. 424-2). Protéger le délai par un acte conservatoire.", "ALERTE"))
        if v["retenue"] and v["effet_sur_delais"] == "aucun" and delais_ouverts and not v.get("acte_conservatoire", "").strip():
            out.append(_k("DELAI_NON_PROTEGE", f"{nom} : la voie retenue n'a aucun effet sur les délais et « {delais_ouverts[0]['evenement']} » "
                          f"({delais_ouverts[0]['date']}) court sans protection ; nommer l'acte conservatoire et sa date (D2)."))

    # Offre ordonnée, motivée, défendable.
    o = doc["offre"]
    m_po, m_cible, m_res = _montant(po.get("montant")), _montant(o["cible"].get("montant")), _montant(o["point_de_reservation"].get("montant"))
    suite = [(n, m) for n, m in (("première offre", m_po), ("cible", m_cible), ("point de réservation", m_res)) if m is not None]
    for (n1, a), (n2, b) in zip(suite, suite[1:]):
        if (o["sens"] == "nous_recevons" and a < b) or (o["sens"] == "nous_payons" and a > b):
            out.append(_k("OFFRE_INCOHERENTE", f"{n1} ({a}) et {n2} ({b}) dans le mauvais ordre pour une partie qui "
                          f"{'reçoit' if o['sens'] == 'nous_recevons' else 'paie'} (N7, N12)."))
    dao = _montant((o.get("derniere_offre_adverse") or {}).get("montant"))
    if dao is not None and m_res is not None and ((o["sens"] == "nous_recevons" and dao >= m_res) or (o["sens"] == "nous_payons" and dao <= m_res)):
        out.append(_k("OFFRE_ADVERSE_DANS_LA_ZONE", f"La dernière offre adverse ({dao}) franchit déjà le point de réservation ({m_res}) : "
                      "dire au client pourquoi poursuivre plutôt qu'accepter, ou lui soumettre l'offre (N7).", "ALERTE"))

    # Concessions : chacune contre une contrepartie, conditionnelle, décroissante.
    precedent = None
    for c in sorted(doc["contreparties"], key=lambda x: x["ordre"]):
        if RE_SANS_CONTREPARTIE.match(c["en_echange_de"]):
            out.append(_k("CONCESSION_SANS_CONTREPARTIE", f"{c['id']} : « {c['nous_cedons']} » sans contrepartie ; une concession répond "
                          "à un mouvement adverse (N18)."))
        m = _montant(c.get("montant"))
        if m is not None and precedent is not None and m > precedent:
            out.append(_k("CONCESSIONS_NON_DECROISSANTES", f"{c['id']} ({m}) dépasse la concession précédente ({precedent}) : les "
                          "concessions décroissent (N18).", "ALERTE"))
        precedent = m if m is not None else precedent

    # Accord avec une personne publique qui paie : fondement de la dette, signataire, comité, échec de l'homologation.
    types = {c["type"] for c in doc.get("conditions_de_forme", [])}
    publics = [p for p in adversaires if p["nature"] in ("personne_publique", "organisme_social")]
    if publics and o["sens"] == "nous_recevons":
        manque = {"absence_de_liberalite", "habilitation_signataire"} - types
        if manque:
            out.append(_k("ACCORD_PUBLIC_SANS_FONDEMENT", f"Une personne publique paierait : conditions de forme absentes {sorted(manque)}. "
                          "L'accord écrit le fondement de la dette, le calcul par chef et la renonciation à l'instance, et nomme qui "
                          "peut signer (D9, D10 ; CE, Section, 17 juin 2026, n° 489764)."))
        plus_haut = max([m for m in (m_po, m_cible) if m is not None], default=0)
        if any(p.get("personne_publique") == "etat" for p in publics) and plus_haut > SEUIL_COMITE_ETAT and "comite_transaction" not in types:
            out.append(_k("COMITE_TRANSACTION_REQUIS", f"Transaction avec l'État dont le montant dépasse {SEUIL_COMITE_ETAT} euros : l'avis du "
                          "comité ministériel de transaction est obligatoire (CRPA, art. L. 423-2 et R. 423-3)."))
        if "homologation" in types and "desistement" not in types:
            out.append(_k("ECHEC_HOMOLOGATION_NON_PREVU", "L'accord sera soumis à homologation sans clause qui règle son refus : le refus "
                          "annule la transaction et le juge statue au fond (CE, Ass., 11 juillet 2008, Krupp Hazemag, n° 287354 ; D11).", "ALERTE"))
    if doc["etat"] == "accord_conclu" and "ecrit" not in types:
        out.append(_k("ACCORD_SANS_ECRIT", "Accord conclu sans condition « ecrit » : la transaction se rédige par écrit (C. civ., art. 2044 ; "
                      "CRPA, art. L. 423-1).", "ALERTE"))

    # Interlocuteurs : qui signe pour l'adversaire.
    for p in adversaires:
        siens = [i for i in doc["interlocuteurs"] if i["partie"] == p["id"]]
        if not any(i["pouvoir"] == "signe" or (i.get("chaine_de_validation") or "").strip() for i in siens):
            out.append(_k("SIGNATAIRE_NON_IDENTIFIE", f"{p['id']} ({p['designation']}) : ni signataire ni chaîne de validation identifiés (N27).", "ALERTE"))

    # Aucun chiffre de chance ; aucun aveu ni menace dans ce qui sort ; leviers licites.
    for chemin, t in _textes(doc):
        if RE_PROBA.search(t):
            out.append(_k("PROBABILITE_INTERDITE", f"{chemin} : probabilité chiffrée de succès ; le client reçoit une fourchette d'issues "
                          "et de montants, jamais un pourcentage de chance."))
    for chemin, t in _adresse_a_l_exterieur(doc):
        m = RE_AVEU.search(t)
        if m:
            out.append(_k("AVEU_DE_FAIBLESSE", f"{chemin} : « {m.group(0)} ». En négociation, on parle de contreparties et d'échanges, "
                          "jamais de faiblesse avouée (L10)."))
        m = RE_MENACE.search(t)
        if m:
            out.append(_k("MENACE_ILLICITE", f"{chemin} : « {m.group(0)} ». Seule la voie de droit liée à la demande s'annonce ; une "
                          "plainte, un signalement ou une révélation ne s'échange contre rien (C. pén., art. 312-10 ; L3, L4)."))
    for i, lv in enumerate(doc.get("leviers", [])):
        m = RE_MENACE.search(lv["levier"])
        if m:
            out.append(_k("MENACE_ILLICITE", f"$.leviers[{i}] : « {m.group(0)} » n'est pas un levier de négociation (L3, L4)."))
    return out


def charger(racine: Path) -> tuple[dict | None, list[dict]]:
    chemin = racine / FICHIER
    if not chemin.is_file():
        return None, []
    try:
        doc = json.loads(chemin.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return None, [_k("NEGOCIATION_INVALIDE", f"{FICHIER} n'est pas un JSON valide (ligne {e.lineno}, colonne {e.colno}) : {e.msg}.")]
    constats = valider(doc)
    return (doc if not any(k["code"] == "NEGOCIATION_INVALIDE" for k in constats) else None), constats


def date_declaree(valeur):
    """Une date sans heure compte du début du jour."""
    v = str(valeur or "")
    return L.parse_date(v + "T00:00" if len(v) == 10 else v)


def _nombres(texte: str) -> set[int]:
    res = set()
    for brut in re.findall(r"\d{1,3}(?:[   .]\d{3})+(?:,\d+)?|\d+(?:,\d+)?", texte):
        try:
            res.add(int(float(re.sub(r"[   .]", "", brut).replace(",", "."))))
        except ValueError:
            continue
    return res


def _seuils_secrets(doc: dict) -> list[tuple[str, int]]:
    """Montants qui ne sortent jamais : point de réservation, cible et concessions, quand ils diffèrent de la première offre."""
    o = doc.get("offre") or {}
    po = _montant((o.get("premiere_offre") or {}).get("montant"))
    res = [("du point de réservation", _montant((o.get("point_de_reservation") or {}).get("montant"))),
           ("de la cible", _montant((o.get("cible") or {}).get("montant")))]
    res += [(f"de la concession {c.get('id')}", _montant(c.get("montant"))) for c in doc.get("contreparties", [])]
    return [(n, int(m)) for n, m in res if m is not None and m >= 100 and (po is None or int(m) != int(po))]


def controler(racine: Path, ecriture: Path, fiche: dict | None, c, juridictionnel: bool = True, texte: str | None = None) -> None:
    """Contrôle avant un acte, au format de gate.py : c(code, gravite, message)."""
    fiche = fiche or {}
    acte = ecriture.stem
    racine_acte = acte.split("_v")[0]
    doc, constats = charger(racine)
    if doc is None and not constats:
        if not juridictionnel:
            return
        u = fiche.get("urgence_amiable") or {}
        if str(u.get("motif") or "").strip() and str(u.get("source") or "").strip():
            c("NEGOCIATION_DIFFEREE_URGENCE", "ALERTE", f"Aucun plan de négociation ; urgence motivée dans la fiche : {str(u['motif'])[:200]}. "
              "Le plan s'écrit dès l'acte déposé (skill negociation-et-persuasion).")
        else:
            c("NEGOCIATION_ABSENTE", "BLOQUANT", f"{FICHIER} absent : aucune voie amiable n'a été examinée avec la solution de repli de chaque "
              "partie avant cet acte juridictionnel (skill negociation-et-persuasion, sous-agent negociateur). Seule une urgence motivée "
              "dans la fiche (urgence_amiable : motif et source) permet de déposer d'abord.")
        return
    for k in constats:
        c(k["code"], k["gravite"], k["message"])
    if doc is None:
        return
    couverts = [str(x) for x in doc.get("actes_couverts", [])]
    if juridictionnel and "*" not in couverts and not any(racine_acte in x or x in acte for x in couverts):
        c("NEGOCIATION_HORS_ACTE", "BLOQUANT", f"Le plan de négociation ne couvre pas l'acte {acte} (actes_couverts) : l'acte est un tournant, "
          "le plan se révise avant lui.")
    lg = L.lire_json(racine / "strategie/ligne.json") or {}
    dl, dn = date_declaree(lg.get("date")), date_declaree(doc.get("date"))
    if juridictionnel and dl and dn and dn < dl and doc.get("ligne_examinee") != lg.get("date"):
        c("NEGOCIATION_PERIMEE", "BLOQUANT", "La ligne stratégique a été révisée après le plan de négociation : relire le plan à sa lumière, "
          "puis le redater ou y inscrire ligne_examinee.")
    if juridictionnel and not any(p["decideur"] in FAMILLE_JUGE and (not p.get("actes") or any(racine_acte in a or a in acte for a in p["actes"]))
                                  for p in doc["persuasion"]):
        c("PERSUASION_JUGE_ABSENTE", "ALERTE", "Aucun plan de persuasion du juge pour cet acte : ce qu'il doit croire, sa raison et son "
          "moyen de décider, l'ordre, les faits défavorables et leur traitement (skill negociation-et-persuasion, section 4).")
    if texte is None:
        return
    nombres = _nombres(texte)
    for nom, m in _seuils_secrets(doc):
        if m in nombres:
            c("SEUIL_REVELE" if not juridictionnel else "NEGOCIATION_DANS_L_ECRIT", "BLOQUANT",
              f"Le texte contient le montant {nom} ({m}) : ce chiffre ne sort jamais, ni vers le juge ni vers l'adversaire (N4, L9).")
    if juridictionnel:
        m = RE_EVOCATION.search(texte)
        if m:
            c("NEGOCIATION_EVOQUEE", "ALERTE", f"« {m.group(0)} » : l'écrit au juge ne rapporte ni offre ni propos de la négociation ; il mentionne "
              "seulement les diligences amiables que la loi exige (CPC, art. 54, 5° ; L9).")
        for v in doc["voies_amiables"]:
            if v["obligatoire"] and (not v.get("actes") or any(racine_acte in a or a in acte for a in v["actes"])) and not RE_DILIGENCES.search(texte):
                c("DILIGENCES_AMIABLES_NON_MENTIONNEES", "BLOQUANT", f"Préalable amiable obligatoire ({v['fondement']}) : l'acte doit mentionner les "
                  "diligences accomplies ou la dispense (CPC, art. 54, 5° ; CJA, art. R. 213-12).")
                break
    else:
        m = RE_AVEU.search(texte)
        if m:
            c("AVEU_DE_FAIBLESSE", "BLOQUANT", f"« {m.group(0)} » dans un écrit adressé à l'extérieur : aucune faiblesse avouée (L10).")
        m = RE_MENACE.search(texte)
        if m:
            c("MENACE_ILLICITE", "ALERTE", f"« {m.group(0)} » dans un écrit adressé à l'extérieur : vérifier qu'aucune plainte, aucun signalement "
              "ni aucune révélation n'est proposé en échange d'un paiement ou d'une signature (C. pén., art. 312-10 ; L3).")


SQUELETTE = {
    "schema": "negociation/1", "date": "", "ligne_examinee": "", "actes_couverts": [""], "etat": "a_ouvrir", "etat_motif": "",
    "parties": [
        {"id": "P1", "role": "client", "nature": "", "designation": "", "position_affichee": "",
         "interets": [{"interet": "", "priorite": "", "statut": "", "sources": [""]}], "contraintes": [""]},
        {"id": "P2", "role": "adversaire", "nature": "", "personne_publique": "", "designation": "", "position_affichee": "",
         "interets": [{"interet": "", "priorite": "", "statut": "", "sources": [""]}], "sans_perdre_la_face": [""], "contraintes": [""]}],
    "repli": [{"partie": p, "alternative": "", "issue_probable": "", "montant_bas": None, "montant_haut": None, "delai": "", "couts": "",
               "alea": "", "valeur_nette": "", "sources": [""]} for p in ("P1", "P2")],
    "voies_amiables": [{"id": "V1", "voie": "", "ouverte": True, "obligatoire": False, "actes": [""], "fondement": "", "effet_sur_delais": "",
                        "acte_conservatoire": "", "repli_compare": "", "retenue": False, "raison": ""}],
    "objets": [{"id": "B1", "objet": "", "valeur_client": "", "valeur_adversaire_estimee": ""}],
    "options": [{"id": "O1", "description": "", "objets": ["B1"], "acceptable_client": True, "acceptable_adversaire": "", "fondement": ""}],
    "offre": {"sens": "", "premier_a_ouvrir": "", "raison": "",
              "premiere_offre": {"contenu": "", "montant": None, "calcul": "", "sources": [""], "formulation": ""},
              "cible": {"contenu": "", "montant": None, "justification": ""},
              "point_de_reservation": {"contenu": "", "montant": None, "justification": ""}},
    "contreparties": [{"id": "C1", "nous_cedons": "", "montant": None, "en_echange_de": "", "condition": "", "ordre": 1,
                       "raison_exterieure": "", "formulation": ""}],
    "interlocuteurs": [{"id": "I1", "partie": "P2", "fonction": "", "pouvoir": "", "habilitation": "", "chaine_de_validation": "", "canal": ""}],
    "calendrier": [{"date": "", "evenement": "", "type": "", "protege_par": "", "source": "", "statut": "a_venir"}],
    "conditions_de_forme": [{"type": "", "exigence": "", "source": ""}],
    "leviers": [{"levier": "", "nature": "", "source": ""}],
    "risques": [{"id": "R1", "risque": "", "parade": "", "gravite": ""}],
    "persuasion": [{"id": "PS1", "decideur": "", "ref_decideur": "", "actes": [""], "ce_qu_il_doit_croire": "", "raison_de_decider": "",
                    "moyen_de_decider": "", "ordre": [""], "faits_defavorables": [{"fait": "", "traitement": "", "comment": ""}],
                    "forme": "", "ton": "", "a_ne_pas_dire": [""], "message_cle": ""}],
    "revisions": [{"date": "", "tournant": "", "changement": ""}],
    "sources": [{"id": "S1", "type": "", "reference": "", "url": "", "lu": "", "public": True}],
}


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--racine", help="dossier d'affaire (par défaut : celui qui contient le répertoire courant)")
    sp = p.add_subparsers(dest="cmd", required=True)
    sp.add_parser("valider")
    pc = sp.add_parser("controle")
    pc.add_argument("brouillon")
    pc.add_argument("--non-juridictionnel", action="store_true", help="écrit adressé à l'adversaire ou à une autorité, non au juge")
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
        if doc is None and not constats:
            print(f"{FICHIER} absent.")
            return 1
        for k in constats:
            print(f"- {k['gravite']} {k['code']} : {k['message']}")
        bloquants = sum(1 for k in constats if k["gravite"] == "BLOQUANT")
        print(f"{FICHIER} : {'valide' if not bloquants else 'à reprendre'} ({bloquants} bloquant(s), {len(constats) - bloquants} alerte(s)).")
        return 1 if bloquants else 0
    ecriture = Path(a.brouillon).resolve()
    fiche = L.lire_json(racine / "ecritures/controle" / f"{ecriture.stem}.fiche.json", {}) or {}
    texte = ecriture.read_text(encoding="utf-8") if ecriture.is_file() else None
    constats = []
    controler(racine, ecriture, fiche, lambda code, gravite, message, **_: constats.append((gravite, code, message)),
              juridictionnel=not a.non_juridictionnel, texte=texte)
    for g, code, m in constats:
        print(f"- {g} {code} : {m}")
    print(f"{sum(1 for g, _, _ in constats if g == 'BLOQUANT')} bloquant(s).")
    return 1 if any(g == "BLOQUANT" for g, _, _ in constats) else 0


if __name__ == "__main__":
    sys.exit(main())
