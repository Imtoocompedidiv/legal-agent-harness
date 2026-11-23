"""Fonctions communes du dossier d'affaire : racine, état, schémas, heure, empreintes.

Bibliothèque standard seulement : les hooks doivent démarrer vite et sans environnement virtuel.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import date, datetime
from pathlib import Path

MARQUEUR = Path("etat") / "affaire.json"

# Fichiers d'état et champs obligatoires de chaque entrée. Le contrôle reste volontairement
# minimal : il empêche un état illisible ou incomplet, il ne remplace pas la relecture.
SCHEMAS = {
    "etat/affaire.json": {"racine": ["id", "intitule", "client", "objectif"]},
    "etat/echeances.json": {"liste": "echeances", "champs": ["id", "objet", "date", "regle", "source", "statut"]},
    "etat/objections.json": {"liste": "objections", "champs": ["id", "acte", "enonce", "gravite", "statut"]},
    "etat/sources.json": {"liste": "sources", "champs": ["id", "type", "reference", "lu_en_entier"]},
    "etat/canaux.json": {"liste": "canaux", "champs": ["id", "nom", "frequence_heures"]},
    "pieces/bordereau.json": {"liste": "pieces", "champs": ["cote", "fichier", "sha256", "description"]},
    "chronologie/chronologie.json": {"liste": "evenements", "champs": ["date", "fait", "pieces", "statut"]},
    "preuves/matrice.json": {"liste": "faits_a_prouver", "champs": ["id", "fait", "charge", "pieces", "force"]},
    "terrain/actions.json": {"liste": "actions", "champs": ["id", "objectif_probatoire", "action", "statut"]},
    "adverse/declarations.json": {"liste": "declarations", "champs": ["id", "auteur", "piece", "citation", "paragraphe_complet", "pieces_meme_auteur_lues"]},
    "strategie/ligne.json": {"racine": ["date", "objectif", "decideur", "lecture_adversaire", "levier", "meilleur_coup_adverse", "parade", "temps_reel", "chemin_de_victoire"]},
    "terrain/audit.json": {"racine": ["date", "evidences_verifiees", "lacunes", "actions_decidees"]},
    "strategie/theorie.json": {"racine": ["date", "recit_du_client", "hypotheses", "theorie_retenue", "faits_defavorables", "epreuves"]},
    "strategie/theorie_adverse.json": {"racine": ["date", "arguments", "meilleur_coup"]},
    "strategie/sequence.json": {"racine": ["date", "premier_acte_adverse", "actes", "autorites", "familles_examinees", "voies", "cible", "ordre_des_coups"]},
}

VALEURS = {
    ("etat/echeances.json", "statut"): {"a_venir", "faite", "abandonnee"},
    ("etat/objections.json", "gravite"): {"dirimante", "serieuse", "mineure"},
    ("etat/objections.json", "statut"): {"ouverte", "traitee", "acceptee_client", "rejetee_motivee"},
    ("etat/sources.json", "type"): {"texte", "norme", "decision", "doctrine", "travaux", "rapport", "autre"},
    ("chronologie/chronologie.json", "statut"): {"prouve", "allegue", "conteste"},
    ("preuves/matrice.json", "charge"): {"nous", "adversaire", "partagee", "juge"},
    ("preuves/matrice.json", "force"): {"forte", "moyenne", "faible", "nulle"},
    ("preuves/matrice.json", "force_probante"): {"prouve", "corrobore", "allegue", "conteste", "contredit"},
    ("terrain/actions.json", "statut"): {"proposee", "validee_client", "faite", "abandonnee"},
}


def maintenant() -> datetime:
    """Heure locale du poste, lue au moment de l'appel. Jamais une heure estimée.

    CONTENTIEUX_MAINTENANT (AAAA-MM-JJTHH:MM) fixe l'horloge pour rejouer un dossier à une date passée ;
    réservé aux essais, il est signalé dans chaque verdict.
    """
    fixe = os.environ.get("CONTENTIEUX_MAINTENANT")
    if fixe:
        return datetime.fromisoformat(fixe).astimezone()
    return datetime.now().astimezone()


def horodatage() -> str:
    return maintenant().strftime("%Y-%m-%d %H:%M:%S %z")


def trouver_racine(depart: str | os.PathLike | None) -> Path | None:
    if not depart:
        return None
    p = Path(depart)
    try:
        p = p.resolve()
    except OSError:
        return None
    if p.is_file() or not p.exists():
        p = p.parent
    for candidat in [p, *p.parents]:
        if (candidat / MARQUEUR).is_file():
            return candidat
    return None


def relatif(racine: Path, chemin: str | os.PathLike) -> str | None:
    """Chemin relatif à la racine, en barres obliques et minuscules ; None s'il est hors du dossier."""
    try:
        r = Path(chemin).resolve().relative_to(racine.resolve())
    except (ValueError, OSError):
        return None
    return r.as_posix()


def lire_json(chemin: Path, defaut=None):
    try:
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return defaut
    except json.JSONDecodeError:
        return defaut


def ecrire_json(chemin: Path, donnees) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=chemin.parent, prefix=".tmp-", suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, chemin)


def sha256_fichier(chemin: Path) -> str:
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def valider_fichier(racine: Path, rel: str) -> list[str]:
    """Erreurs de structure d'un fichier d'état connu ; liste vide si valide ou non suivi."""
    schema = SCHEMAS.get(rel)
    if schema is None:
        return []
    chemin = racine / rel
    try:
        with open(chemin, encoding="utf-8") as f:
            donnees = json.load(f)
    except FileNotFoundError:
        return [f"{rel} est absent."]
    except json.JSONDecodeError as e:
        return [f"{rel} n'est pas un JSON valide (ligne {e.lineno}, colonne {e.colno}) : {e.msg}."]
    erreurs = []
    if "racine" in schema:
        for champ in schema["racine"]:
            if champ not in donnees or donnees[champ] in (None, ""):
                erreurs.append(f"{rel} : champ obligatoire « {champ} » absent ou vide.")
        return erreurs
    cle = schema["liste"]
    entrees = donnees.get(cle) if isinstance(donnees, dict) else None
    if not isinstance(entrees, list):
        return [f"{rel} : la clé « {cle} » doit contenir une liste."]
    for i, e in enumerate(entrees):
        if not isinstance(e, dict):
            erreurs.append(f"{rel} : l'entrée {i + 1} n'est pas un objet.")
            continue
        ident = e.get("id") or e.get("cote") or e.get("date") or i + 1
        for champ in schema["champs"]:
            if champ not in e:
                erreurs.append(f"{rel} : entrée {ident}, champ « {champ} » absent.")
        for (fichier, champ), permis in VALEURS.items():
            if fichier == rel and champ in e and e[champ] not in permis:
                erreurs.append(f"{rel} : entrée {ident}, « {champ} » vaut « {e[champ]} », valeurs permises {sorted(permis)}.")
    return erreurs


def parse_date(valeur: str | None) -> datetime | None:
    """Accepte AAAA-MM-JJ ou AAAA-MM-JJTHH:MM ; une date seule vaut fin de journée."""
    if not valeur:
        return None
    v = str(valeur).strip()
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
            d = date.fromisoformat(v)
            return datetime(d.year, d.month, d.day, 23, 59).astimezone()
        dt = datetime.fromisoformat(v.replace(" ", "T"))
        return dt if dt.tzinfo else dt.astimezone()
    except ValueError:
        return None


def date_simple(valeur: str | None) -> date | None:
    if not valeur:
        return None
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", str(valeur))
    if not m:
        return None
    try:
        return date(int(m[1]), int(m[2]), int(m[3]))
    except ValueError:
        return None


def echeances_ouvertes(racine: Path) -> list[tuple[float, dict]]:
    """Échéances à venir triées, avec le nombre d'heures restantes (négatif si dépassée)."""
    donnees = lire_json(racine / "etat/echeances.json", {}) or {}
    resultat = []
    now = maintenant()
    for e in donnees.get("echeances", []):
        if e.get("statut") != "a_venir":
            continue
        dt = parse_date(e.get("date"))
        if dt is None:
            continue
        resultat.append(((dt - now).total_seconds() / 3600, e))
    resultat.sort(key=lambda x: x[0])
    return resultat


def canaux_perimes(racine: Path) -> list[tuple[dict, float | None]]:
    """Canaux de notification dont le dernier contrôle dépasse la fréquence prévue."""
    donnees = lire_json(racine / "etat/canaux.json", {}) or {}
    now = maintenant()
    resultat = []
    for c in donnees.get("canaux", []):
        freq = float(c.get("frequence_heures") or 24)
        dernier = parse_date(c.get("dernier_controle"))
        age = None if dernier is None else (now - dernier).total_seconds() / 3600
        if age is None or age > freq:
            resultat.append((c, age))
    return resultat


def objections_bloquantes(racine: Path, acte: str | None = None) -> list[dict]:
    donnees = lire_json(racine / "etat/objections.json", {}) or {}
    res = []
    for o in donnees.get("objections", []):
        if o.get("gravite") == "dirimante" and o.get("statut") == "ouverte":
            # Une objection inscrite pour un acte vaut pour ses versions successives (acte, acte_v2, acte_v3...).
            cible = str(o.get("acte") or "")
            if acte is None or cible == "*" or acte == cible or acte.startswith(cible + "_"):
                res.append(o)
    return res


def ajouter_journal(racine: Path, texte: str, type_: str = "note") -> str:
    ligne = f"- {horodatage()} [{type_}] {texte.strip()}\n"
    chemin = racine / "journal" / "journal.md"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    if not chemin.exists():
        chemin.write_text("# Journal de l'affaire\n\nEntrées ajoutées par `affaire.py journal`, heure lue sur le poste.\n\n", encoding="utf-8")
    with open(chemin, "a", encoding="utf-8", newline="\n") as f:
        f.write(ligne)
    return ligne


def fmt_heures(h: float) -> str:
    if h < 0:
        return f"DÉPASSÉE depuis {(-h) / 24:.1f} j"
    if h < 48:
        return f"dans {h:.0f} h"
    return f"dans {h / 24:.0f} j"
