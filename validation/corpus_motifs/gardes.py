"""Garde de domaine des lignes minées : une ligne ne vaut que si le dossier relève de son sous-domaine (champ « exige »), en plus de
ses marqueurs. Audit du 22 novembre 2026 : sans garde, la ligne des contrats à durée déterminée d'agents publics se déclenchait sur
14 des 34 dossiers de droit des étrangers du banc (« refus de renouvel »), celle du permis de construire sur 9.

    python gardes.py              audit des déclenchements hors domaine sur les dossiers du banc
    python gardes.py --appliquer  écrit « exige » sur les lignes minées des fiches
"""
from __future__ import annotations

import glob
import json
import re
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
REFS = ICI.parents[1] / "plugins" / "contentieux" / "skills" / "mecanique-des-exercices" / "references"
BLOC = re.compile(r"(## Données de contrôle\s*```json\s*)(.*?)(```)", re.S)

ETRANGER = r"titre de séjour|carte de (?:séjour|résident)|étrang|ceseda|récépissé|préfet de police|obligation de quitter|\boqtf\b"
GARDES = [  # (motif du sous-domaine, domaine exigé dans le dossier)
    (r"^fonction publique", r"\bagents? publics?|fonctionnaire|privation de traitement|disciplin|contractuel|collectivit|centre hospitalier|employeur public|\bagent\b"),
    (r"^urbanisme", r"permis de construire|permis d'aménager|urbanisme|plan local|\bplu\b|déclaration préalable"),
    (r"^environnement", r"espèces? protégées?|autorisation environnementale|\bicpe\b|installation classée|dérogation|éolien|carrière"),
    (r"revenu de solidarité|^aide et action sociale : revenu", r"\brsa\b|revenu de solidarité"),
    (r"aide sociale à l'enfance|jeune majeur", r"aide sociale à l'enfance|jeune majeur|contrat jeune|\base\b"),
    (r"^agréments", r"agrément|assistant(?:e)? (?:familial|maternel)"),
    (r"permis de conduire", r"permis de conduire|\b48 ?si\b|solde de points|points"),
    (r"débit de boissons|fermeture", r"fermeture|débit de boissons|restaurant|établissement"),
    (r"^décisions scolaires", r"élève|collège|lycée|établissement scolaire|obligation scolaire"),
    (r"^décisions universitaires", r"universit|master|section disciplinaire|enseignement supérieur"),
    (r"^execution_oqtf", r"obligation de quitter|\boqtf\b|éloign|rétention"),
    (r"^mayotte", r"mayotte"),
    (r"conditions_materielles_accueil|enregistrement_demande_asile", r"asile|\bofii\b|demandeur d'asile|conditions matérielles"),
    (r"^mineurs_non_accompagnes", r"mineur|aide sociale à l'enfance|évaluation"),
    (r"^detention", r"détenu|détention|pénitentiaire|maison d'arrêt|centre pénitentiaire|prison"),
    (r"^libertes_publiques", r"manifestation|rassemblement|réunion|cortège|culte"),
    (r"^rendez_vous_titre_sejour|^recepisse_document_sejour", ETRANGER),
    (r"^hebergement_urgence", r"hébergement|115|sans abri|à la rue"),
    # Requête en annulation, référé-provision, prud'hommes (sous-domaines imposés aux sous-agents ; « général » sans garde).
    (r"^étrangers", ETRANGER),
    (r"^police", r"police|permis de conduire|fermeture|arrêté du maire|préfet"),
    (r"^enseignement", r"élève|étudiant|universit|établissement scolaire|académie|recteur"),
    (r"^aide sociale", r"rsa|aide sociale|allocation|prestation|département|caisse d'allocations"),
    (r"^bail", r"bail|loyer|locataire|bailleur"),
    (r"^commercial", r"facture|commande|fournisseur|client|société"),
    (r"^prêt", r"prêt|crédit|banque|emprunteur|échéances"),
    (r"^assurance", r"assur|sinistre|police d'assurance|garantie"),
    (r"^copropriété", r"copropriét|syndic|syndicat des copropriétaires|charges de copropriété"),
    (r"^responsabilité", r"préjudice|responsabilit|accident|dommage"),
    (r"^travaux", r"travaux|entrepreneur|malfaçon|réception|maître d'ouvrage"),
    (r"^licenciement|^inaptitude|^économique|^rupture conventionnelle|^prise d'acte|^harcèlement|^heures supplémentaires|^cdd",
     r"salari|employeur|licenci|contrat de travail|prud"),
]


def exige_pour(fichier: str, motif: dict) -> str | None:
    if fichier == "suspension-etrangers.json":
        return ETRANGER
    sd = str(motif.get("sous_domaine") or "")
    return next((g for m, g in GARDES if re.search(m, sd, re.I)), None)


def table() -> dict[str, str]:
    """Préfixe du texte de chaque ligne minée -> garde de domaine."""
    t = {}
    for f in ("suspension-etrangers.json", "suspension-autres.json", "liberte-etrangers.json", "annulation-tribunal.json",
              "refere-provision.json", "prudhommes.json"):
        if not (ICI / f).exists():
            continue
        for m in json.loads((ICI / f).read_text(encoding="utf-8")):
            g = exige_pour(f, m)
            if g:
                t[m["texte"].strip()[:80]] = g
    return t


def appliquer() -> None:
    gardes = table()
    for fiche in ("refere-suspension.md", "refere-liberte.md", "requete-annulation.md", "refere-civil-835-provision.md",
                  "conseil-de-prud-hommes.md"):
        p = REFS / fiche
        t = p.read_text(encoding="utf-8")
        mb = BLOC.search(t)
        d = json.loads(mb.group(2))
        n = 0
        for c in d.get("conditions_decisives") or []:
            for cle in ("ce_qui_la_remplit", "ce_qui_la_fait_tomber", "points_disputes"):
                for x in c.get(cle) or []:
                    if isinstance(x, dict) and str(x.get("origine", "")).startswith("minage"):
                        g = gardes.get(x["texte"].strip()[:80])
                        if g:
                            x["exige"] = [g]
                            n += 1
        p.write_text(t[:mb.start(2)] + json.dumps(d, ensure_ascii=False, indent=2) + "\n" + t[mb.end(2):], encoding="utf-8")
        print(f"{fiche} : garde posée sur {n} ligne(s)")


def audit() -> None:
    banc = ICI.parent / "banc" / "fixtures"
    etr = [Path(f).read_text(encoding="utf-8") for f in glob.glob(str(banc / "gen_urg[td]_*/dossier_remis.md")) + glob.glob(str(banc / "gen_libe_*/dossier_remis.md"))]
    for f, cible in (("suspension-autres.json", etr),):
        for m in json.loads((ICI / f).read_text(encoding="utf-8")):
            g = exige_pour(f, m)
            n = sum(1 for t in cible if any(re.search(x, t, re.I) for x in m["marqueurs"]) and (not g or re.search(g, t, re.I)))
            if n:
                print(f"{n:3d} déclenchements hors domaine | {m.get('sous_domaine', '')[:40]} | {m['texte'][:60]}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    appliquer() if "--appliquer" in sys.argv else audit()
