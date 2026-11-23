"""Évaluation sur le jeu de contrôle écrit à la main (controle.md), indépendant du générateur : la mesure qui dit si les règles
généralisent hors des formes sur lesquelles elles ont été mises au point.

    python evaluer_controle.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI.parents[1] / "scripts"))
import pseudonymisation as P  # noqa: E402

JEUX = {}
DOIT_RESTER = ["article L. 1235-3 du code du travail", "Cass. soc., 11 mai 2022, n° 21-14.490", "CHU de Brest", "CPAM du Finistère",
               "ordonnance n° 45-2592 du 2 novembre 1945", "article 373-2-6 du code civil", "tribunal judiciaire de Bordeaux",
               "14 avril 2026", "articles 61 et 62 du code de procédure pénale", "barreau de Bordeaux", "CONSEIL DE PRUD'HOMMES DE BORDEAUX",
               "2 février 2025", "18 400 euros", "3 200 euros", "son chien Brutus"]
# Ce que l'avocat déclarerait pour chaque pièce : les parties et les proches qu'il connaît, pas les tiers.
PARTIES = {"jugement prud'homal": ["Ghislaine Vasseur-Okafor", "Logistique Garonne Express"],
           "expertise médicale": ["Tran Van Long"], "constat de commissaire de justice": ["Firmin Désiré Nkoulou"],
           "transcription de SMS": ["Kévin", "Marjolaine", "Timéo"], "courrier d'avocat": ["Aurélio Ferraz Pinto", "Pélagie Ondoua"],
           "procès-verbal de gendarmerie": ["Océane Brisset"]}


JEUX["controle"] = (DOIT_RESTER, PARTIES)
JEUX["controle2"] = (
    ["article L. 423-23 du code de l'entrée et du séjour des étrangers et du droit d'asile", "tribunal administratif de Toulouse",
     "article 1344 du code civil", "juge des contentieux de la protection", "article L. 533-1 du code général de la fonction publique",
     "article 515-11 du code civil", "tribunal judiciaire de Nanterre", "article 515-12 du code civil", "6 840 euros", "4 juin 2026",
     "12 mai 2026", "PRÉFECTURE DE LA HAUTE-GARONNE"],
    {"refus de titre de séjour": ["Jean-Baptiste Mukendi"], "mise en demeure": ["Gauthier du Plessis", "Les Hauts de Talant"],
     "courriel d'un témoin": ["Ylan Marchetti"], "procès-verbal de conseil de discipline": ["Nathalie Gendron-Ait Ouarab"],
     "ordonnance de protection": ["Clémentine Aubriot", "Teddy Rakotomalala", "Noam"]})
JEUX["controle3"] = (
    ["article L. 3121-28 du code du travail", "conseil de prud'hommes de Lorient", "tribunal correctionnel de Bastia", "article 222-13 du code pénal",
     "CAISSE D'ALLOCATIONS FAMILIALES DU RHÔNE", "article L. 841-1 du code de la sécurité sociale", "commission de recours amiable",
     "article 29 de la loi du 29 juillet 1881", "tribunal des activités économiques de Lyon", "article L. 620-1 du code de commerce",
     "412 000 euros", "1 230 euros", "18 novembre 2026", "Saint-Affrique"],
    {"requête prud'homale": ["Yannick Le Bihan", "Boulangerie Le Fournil d'Antan"], "note d'audience": ["Dominique Agostini"],
     "courrier de la caisse": ["Rania Belkacem"], "constat d'un échange en ligne": ["Mathilde Vernhes"],
     "avis d'expert-comptable": ["Transports Chabert et Fils"]})
ORGANISATIONS = {"Logistique Garonne Express", "Les Hauts de Talant", "Boulangerie Le Fournil d'Antan", "Transports Chabert et Fils"}
# Jeux écrits à l'aveugle le 23 novembre 2026 par un agent sans accès à l'outil, chacun avec ses références et ses parties en JSON.
for _f in sorted(ICI.glob("controle*.json")):
    _spec = json.loads(_f.read_text(encoding="utf-8"))
    JEUX[_f.stem] = (_spec["doit_rester"], _spec["parties"])
    ORGANISATIONS |= set(_spec.get("organisations") or [])


def pieces(jeu: str = "controle") -> list[tuple[str, str, list[tuple[int, int, str]]]]:
    brut = (ICI / f"{jeu}.md").read_text(encoding="utf-8").split("-->", 1)[1]
    out = []
    for bloc in re.split(r"\n=== ", "\n" + brut.strip())[1:]:
        titre, corps = bloc.split("\n", 1)
        texte, gold, pos = "", [], 0
        for m in re.finditer(r"⟦(.*?)⟧", corps, re.S):
            texte += corps[pos:m.start()]
            gold.append((len(texte), len(texte) + len(m.group(1)), m.group(1)))
            texte += m.group(1)
            pos = m.end()
        texte += corps[pos:]
        out.append((titre.strip(), texte, gold))
    return out


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    jeu = sys.argv[1] if len(sys.argv) > 1 else "controle"
    doit_rester, parties = JEUX[jeu]
    for scenario in ("froid", "dossier"):
        tot = ok = revu = degats = 0
        manques, abimes = [], []
        for titre, texte, gold in pieces(jeu):
            table = P.Table(Path("."), memoire=True)
            if scenario == "dossier":
                for x in parties[titre]:
                    table.jeton(x, "ORGANISATION" if x in ORGANISATIONS else "PERSONNE", source="avocat")
            sortie, finales = P.pseudonymiser(texte, table, avec_modele=False)
            spans = sorted((t.debut, t.fin) for t in finales)
            signales = set(P.suspects(sortie, {P.plier(x) for e in table.entites for x in e["formes"]}))
            for d, f, s in gold:
                tot += 1
                pos = d
                for a, b in spans:
                    if a <= pos < b:
                        pos = b
                if pos >= f:
                    ok += 1
                    revu += 1
                else:
                    manques.append(f"{titre} : {s}")
                    if all(w in signales for w in re.findall(r"[A-ZÀ-Ý][\wÀ-ÿ'-]{2,}", s)) and re.search(r"[A-ZÀ-Ý]", s):
                        revu += 1
            for r in doit_rester:
                if r in texte and r not in sortie:
                    degats += 1
                    abimes.append(f"{titre} : {r}")
        print(f"== {jeu}, {scenario} : rappel {ok}/{tot} ({ok / tot:.3f}), avec relecture des signalés {revu}/{tot} ({revu / tot:.3f}), "
              f"références juridiques altérées {degats}")
        for x in manques:
            print("   manqué :", x)
        for x in abimes:
            print("   altéré :", x)


if __name__ == "__main__":
    main()
