"""Évaluation de la pseudonymisation sur un corpus synthétique annoté, sans aucune donnée réelle.

Chaque pièce est générée avec la position exacte de chaque donnée personnelle (l'or) et des références juridiques qui doivent
rester intactes (articles, juridictions, numéros de décisions publiées, dates de procédure). Mesures :
  - rappel par catégorie : part des mentions entièrement couvertes par un jeton ;
  - fuites : mentions dont la forme réelle reste lisible dans le texte pseudonymisé (la mesure qui compte pour le secret) ;
  - dégâts : références juridiques altérées (la mesure qui compte pour le travail juridique) ;
  - faux positifs : remplacements hors de l'or et hors des références.
Deux scénarios : à froid (aucune partie déclarée) et dossier (client, adversaire et conjoint déclarés, comme le prescrit la
procédure). Sortie : tableau et evaluation/resultats.json.

    python evaluer.py [--n 400] [--graine 7]
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI.parents[1] / "scripts"))
import pseudonymisation as P  # noqa: E402

PRENOMS_F = ["Marie", "Nadia", "Sophie", "Fatoumata", "Léa", "Claire", "Aminata", "Hélène", "Inès", "Rose", "Chloé", "Svetlana",
             "Thi Hoa", "Oumou", "Gwenaëlle", "Anne-Sophie", "Yasmina", "Mélodie", "Brigitte", "Zeynep"]
PRENOMS_M = ["Paul", "Mamadou", "Jean", "Karim", "Kévin", "Thomas", "Ahmed", "Pierre-Yves", "Kwame", "Mehdi", "Lucas", "Olivier",
             "Abdelhakim", "Dragan", "Yanis", "Bernard", "Tiago", "Martin", "Rémi", "Ousmane"]
NOMS = ["Durand", "Benali", "N'Diaye", "Le Goff", "Nguyen", "Kowalski", "Da Silva", "Ould Cheikh", "de La Fontaine", "Martin",
        "Blanc", "Roux", "Petit", "Lefèvre", "Ben Salah", "Traoré", "Moreau-Vasseur", "Okonkwo", "Garcia", "Haddad", "Fontaine",
        "Mercier", "Bouchard", "Diallo", "Lambert", "Rousseau", "Kaya", "Yilmaz", "Popescu", "Ferreira"]
VOIES = ["rue des Lilas", "avenue Jean Jaurès", "boulevard de la République", "impasse du Moulin", "allée des Peupliers",
         "chemin de la Croix Blanche", "place du Marché", "rue Victor Hugo", "quai de la Loire", "route de Grenoble"]
VILLES = [("69003", "Lyon"), ("13008", "Marseille"), ("35000", "Rennes"), ("59000", "Lille"), ("31400", "Toulouse"),
          ("44100", "Nantes"), ("63000", "Clermont-Ferrand"), ("76000", "Rouen"), ("67000", "Strasbourg"), ("29200", "Brest")]
NAISSANCE = ["Douala", "Bamako", "Alger", "Porto", "Lyon", "Brest", "Hanoï", "Cracovie", "Dakar", "Istanbul"]
SOCIETES = ["Alpha Conseil", "Les Tilleuls", "Bâtir Ouest", "Transports Ménard", "Agro Delta", "Clinique du Parc"]
# Références qui doivent survivre intactes.
JURIDIQUE = ["article L. 521-1 du code de justice administrative", "CE, Sect., 14 mars 2001, n° 229773",
             "tribunal administratif de Lyon", "article L. 1232-2 du code du travail", "CASF, art. L. 423-8",
             "Cass. soc., 30 octobre 2013, n° 12-22.962", "le préfet du Rhône", "le 13 octobre 2026", "la cour administrative d'appel de Nantes",
             "article 8 de la convention européenne des droits de l'homme", "CE, 9 novembre 2023, n° 474932", "délai de deux mois"]


def cle_nir(corps: str) -> str:
    return f"{97 - int(corps.replace('2A', '19').replace('2B', '18')) % 97:02d}"


def iban_fr(rng: random.Random) -> str:
    bban = f"{rng.randint(10000, 99999)}{rng.randint(10000, 99999)}{rng.randint(10**10, 10**11 - 1)}{rng.randint(10, 99)}"
    num = int("".join(str(int(c, 36)) for c in bban + "FR00"))
    iban = f"FR{98 - num % 97:02d}{bban}"
    return " ".join(iban[i:i + 4] for i in range(0, len(iban), 4))


def siret(rng: random.Random) -> str:
    while True:
        n = "".join(str(rng.randint(0, 9)) for _ in range(14))
        if P.luhn(n):
            return f"{n[:3]} {n[3:6]} {n[6:9]} {n[9:]}"


class Piece:
    def __init__(self):
        self.parts: list[str] = []
        self.or_: list[tuple[int, int, str, str]] = []
        self.garder: list[tuple[int, int, str]] = []
        self.n = 0

    def t(self, s: str):
        self.parts.append(s)
        self.n += len(s)
        return self

    def pii(self, s: str, cat: str):
        self.or_.append((self.n, self.n + len(s), cat, s))
        return self.t(s)

    def droit(self, s: str):
        self.garder.append((self.n, self.n + len(s), s))
        return self.t(s)

    @property
    def texte(self) -> str:
        return "".join(self.parts)


def personne(rng: random.Random, femme: bool | None = None) -> dict:
    femme = rng.random() < 0.5 if femme is None else femme
    return {"prenom": rng.choice(PRENOMS_F if femme else PRENOMS_M), "nom": rng.choice(NOMS), "civ": "Mme" if femme else "M.",
            "femme": femme}


def generer(rng: random.Random) -> tuple[Piece, list[str]]:
    """Une pièce d'un genre tiré au sort ; renvoie aussi les noms complets que l'avocat déclarerait (client, adversaire, conjoint)."""
    cli, conj, adv, tem, med, enfant = (personne(rng), personne(rng), personne(rng), personne(rng), personne(rng),
                                        rng.choice(PRENOMS_F + PRENOMS_M))
    cp, ville = rng.choice(VILLES)
    adresse = f"{rng.randint(1, 180)}{rng.choice(['', ' bis', ''])} {rng.choice(VOIES)}"
    d_naiss = f"{rng.randint(1, 28)} {rng.choice(['janvier', 'mars', 'juin', 'octobre', 'décembre'])} {rng.randint(1950, 2004)}"
    sexe = "2" if cli["femme"] else "1"
    corps = f"{sexe}{rng.randint(50, 99):02d}{rng.randint(1, 12):02d}{rng.choice(['69', '13', '2A', '35'])}{rng.randint(100, 999)}{rng.randint(100, 999)}"
    nir = f"{corps[0]} {corps[1:3]} {corps[3:5]} {corps[5:7]} {corps[7:10]} {corps[10:13]} {cle_nir(corps)}"
    tel = rng.choice([f"06 {rng.randint(10, 99)} {rng.randint(10, 99)} {rng.randint(10, 99)} {rng.randint(10, 99)}",
                      f"+33 7 {rng.randint(10, 99)} {rng.randint(10, 99)} {rng.randint(10, 99)} {rng.randint(10, 99)}",
                      f"04.{rng.randint(10, 99)}.{rng.randint(10, 99)}.{rng.randint(10, 99)}.{rng.randint(10, 99)}"])
    mail = f"{P.plier(cli['prenom']).replace(' ', '')}.{P.plier(cli['nom']).replace(' ', '').replace(chr(39), '')}@exemple.fr"
    soc = rng.choice(SOCIETES)
    p = Piece()
    genre = rng.choice(["arrete", "requete", "licenciement", "attestation", "courriel", "paie", "pv", "bail"])
    nomcomplet = lambda x: f"{x['prenom']} {x['nom']}"  # noqa: E731
    if genre == "arrete":
        p.t("ARRÊTÉ portant suspension d'agrément\n\nLe président du conseil départemental,\nVu le ").droit("CASF, art. L. 423-8").t(" ;\n")
        p.t("Considérant l'information préoccupante concernant ").t(cli["civ"] + " ").pii(f"{cli['nom'].upper()} {cli['prenom']}", "PERSONNE")
        p.t(", née le " if cli["femme"] else ", né le ").pii(d_naiss, "DATE_NAISSANCE").t(" à ").pii(rng.choice(NAISSANCE), "LIEU_NAISSANCE")
        p.t(", domiciliée " if cli["femme"] else ", domicilié ").pii(adresse, "ADRESSE").t(", ").pii(f"{cp} {ville}", "ADRESSE").t(" ;\n")
        p.t("Considérant que l'enfant ").pii(enfant, "PERSONNE").t(" est accueilli au domicile, que ").t(conj["civ"] + " ").pii(conj["nom"], "PERSONNE")
        p.t(" y réside ;\nARRÊTE : l'agrément est suspendu. Délai de recours : ").droit("délai de deux mois").t(" devant le ")
        p.droit("tribunal administratif de Lyon").t(".\n")
    elif genre == "requete":
        p.t("REQUÊTE EN RÉFÉRÉ-SUSPENSION\n\nPOUR : ").t(cli["civ"] + " ").pii(nomcomplet(cli), "PERSONNE").t(", demeurant ").pii(adresse, "ADRESSE")
        p.t(" à ").pii(f"{cp} {ville}", "ADRESSE").t(", représentée par Me " if cli["femme"] else ", représenté par Me ").pii(nomcomplet(adv), "PERSONNE")
        p.t("\nCONTRE : ").droit("le préfet du Rhône").t("\n\nSur le fondement de l'").droit("article L. 521-1 du code de justice administrative")
        p.t(", ").t(cli["civ"] + " ").pii(cli["nom"], "PERSONNE").t(" demande la suspension. Son titre de séjour n° ").pii(f"{rng.randint(10**9, 10**10 - 1)}", "IDENTIFIANT")
        p.t(" expire. L'urgence est présumée (").droit("CE, Sect., 14 mars 2001, n° 229773").t("). Sa fille ").pii(enfant, "PERSONNE")
        p.t(" est scolarisée. Requête enregistrée ").droit("le 13 octobre 2026").t(".\n")
    elif genre == "licenciement":
        p.pii(soc.upper(), "ORGANISATION").t("\nLettre recommandée avec accusé de réception\n\n").t(cli["civ"] + " ").pii(f"{cli['prenom']} {cli['nom'].upper()}", "PERSONNE")
        p.t("\n").pii(adresse, "ADRESSE").t("\n").pii(f"{cp} {ville}", "ADRESSE").t("\n\nNous vous avons convoqué conformément à l'").droit("article L. 1232-2 du code du travail")
        p.t(". Lors de l'entretien, assisté de ").pii(nomcomplet(tem), "PERSONNE").t(", vous avez reconnu les faits. ")
        p.t("Votre salaire sera versé sur le compte ").pii(iban_fr(rng), "IBAN").t(". Sur la jurisprudence (").droit("Cass. soc., 30 octobre 2013, n° 12-22.962")
        p.t("), la société ").pii(soc, "ORGANISATION").t(" (SIRET ").pii(siret(rng), "SIRET").t(") vous notifie votre licenciement.\nLe gérant, ").pii(nomcomplet(adv), "PERSONNE").t("\n")
    elif genre == "attestation":
        p.t("ATTESTATION (article 202 du code de procédure civile)\n\nJe soussigné" + ("e " if tem["femme"] else " ")).pii(nomcomplet(tem), "PERSONNE")
        p.t(", né" + ("e" if tem["femme"] else "") + " le ").pii(d_naiss, "DATE_NAISSANCE").t(", demeurant ").pii(adresse, "ADRESSE").t(", ")
        p.pii(f"{cp} {ville}", "ADRESSE").t(", atteste que ").pii(cli["nom"], "PERSONNE").t(" s'occupe de ").pii(enfant, "PERSONNE")
        p.t(" avec attention. J'ai vu ").t(cli["civ"] + " ").pii(cli["nom"], "PERSONNE").t(" le ").droit("le 13 octobre 2026").t(".\n")
        p.t("Fait à ").t(ville).t(", signature : ").pii(f"{tem['prenom'][0]}. {tem['nom']}", "PERSONNE").t("\nTél. ").pii(tel, "TELEPHONE").t("\n")
    elif genre == "courriel":
        p.t("De : ").pii(mail, "EMAIL").t("\nÀ : ").pii(f"contact@{P.plier(soc).replace(' ', '-')}.fr", "EMAIL").t("\nObjet : mon dossier\n\nBonjour Maître,\n\n")
        p.t("Je vous transmets l'avis du docteur ").pii(nomcomplet(med), "PERSONNE").t(". Mon numéro allocataire est ").pii(f"{rng.randint(1000000, 9999999)}", "IDENTIFIANT")
        p.t(" et mon numéro de sécurité sociale ").pii(nir, "NIR").t(". Mon mari, ").pii(nomcomplet(conj), "PERSONNE").t(", vous appellera au ").pii(tel, "TELEPHONE")
        p.t(".\n\nCordialement,\n").pii(f"{cli['prenom']} {cli['nom']}", "PERSONNE").t("\n")
    elif genre == "paie":
        p.t(f"BULLETIN DE PAIE\nEmployeur : ").pii(soc, "ORGANISATION").t(" SIRET ").pii(siret(rng), "SIRET").t("\nSalarié : ")
        p.pii(f"{cli['nom'].upper()} {cli['prenom']}", "PERSONNE").t("\nN° SS : ").pii(nir, "NIR").t("\nAdresse : ").pii(adresse, "ADRESSE").t(" ").pii(f"{cp} {ville}", "ADRESSE")
        p.t("\nSalaire de base 2 140,00 ; net à payer 1 690,12\nVirement : ").pii(iban_fr(rng), "IBAN").t("\n")
    elif genre == "pv":
        p.t("PROCÈS-VERBAL D'AUDITION\n\nL'an deux mille vingt-six, ").droit("le 13 octobre 2026").t(", devant nous, a comparu ").t(cli["civ"] + " ")
        p.pii(nomcomplet(cli), "PERSONNE").t(", épouse " if cli["femme"] else ", époux ").pii(conj["nom"], "PERSONNE").t(", qui déclare : « Mon voisin ")
        p.pii(tem["prenom"], "PERSONNE").t(" a vu la scène. Le véhicule immatriculé ").pii(f"{rng.choice('ABCDEFGH')}{rng.choice('KLMNPRS')}-{rng.randint(100, 999)}-{rng.choice('TVWXYZ')}{rng.choice('ABCDE')}", "IMMATRICULATION")
        p.t(" était garé devant chez ").pii(adv["nom"].upper(), "PERSONNE").t(". » Lecture faite, ").pii(cli["nom"], "PERSONNE").t(" signe.\n")
        p.t("Conformément à l'").droit("article 8 de la convention européenne des droits de l'homme").t(", ses droits lui ont été rappelés.\n")
    else:
        p.t("CONTRAT DE BAIL\n\nENTRE ").pii(nomcomplet(adv), "PERSONNE").t(", bailleur, et ").t(cli["civ"] + " ").pii(nomcomplet(cli), "PERSONNE")
        p.t(", locataire, joignable à ").pii(mail, "EMAIL").t(". Le logement situé ").pii(adresse, "ADRESSE").t(", ").pii(f"{cp} {ville}", "ADRESSE")
        p.t(" est loué à compter du 1er juillet. Le dépôt de garantie est versé sur le compte ").pii(iban_fr(rng), "IBAN").t(". Garant : ")
        p.pii(nomcomplet(conj), "PERSONNE").t(". En cas de litige, la ").droit("la cour administrative d'appel de Nantes").t(" n'est pas compétente.\n")
    return p, [(nomcomplet(cli), "PERSONNE"), (nomcomplet(conj), "PERSONNE"), (nomcomplet(adv), "PERSONNE"), (soc, "ORGANISATION")]


def couverts(spans: list[tuple[int, int]], d: int, f: int) -> bool:
    pos = d
    for a, b in sorted(spans):
        if a <= pos < b:
            pos = b
        if pos >= f:
            return True
    return pos >= f


def evaluer(n: int, graine: int, dictionnaire: bool) -> dict:
    rng = random.Random(graine)
    tot, ok, fuite, revu = Counter(), Counter(), Counter(), Counter()
    degats, faux, total_droit, exemples = 0, 0, 0, defaultdict(list)
    for _ in range(n):
        piece, parties = generer(rng)
        table = P.Table(Path("."), memoire=True)
        if dictionnaire:
            for x, cat in parties:
                table.jeton(x, cat, source="avocat")
        sortie, finales = P.pseudonymiser(piece.texte, table, avec_modele=False)
        spans = [(t.debut, t.fin) for t in finales]
        signales = set(P.suspects(sortie, {P.plier(x) for e in table.entites for x in e["formes"]}))
        for d, f, cat, s in piece.or_:
            tot[cat] += 1
            if couverts(spans, d, f):
                ok[cat] += 1
                revu[cat] += 1
            else:
                if all(w in signales for w in s.replace("'", " ").split() if w[:1].isupper() and len(w) > 2):
                    revu[cat] += 1
                if len(exemples[cat]) < 4:
                    exemples[cat].append(s)
            if len(s) >= 3 and s in sortie:
                fuite[cat] += 1
        for d, f, s in piece.garder:
            total_droit += 1
            if any(not (b <= d or a >= f) for a, b in spans):
                degats += 1
                exemples["DEGAT"].append(s) if len(exemples["DEGAT"]) < 6 else None
        for a, b in spans:
            if not any(not (b <= d or a >= f) for d, f, *_ in piece.or_) and not any(not (b <= d or a >= f) for d, f, _ in piece.garder):
                faux += 1
                if len(exemples["FAUX"]) < 8:
                    exemples["FAUX"].append(piece.texte[a:b])
    return {"scenario": "dossier" if dictionnaire else "froid", "pieces": n,
            "rappel": {c: round(ok[c] / tot[c], 4) for c in sorted(tot)}, "mentions": dict(tot),
            "rappel_global": round(sum(ok.values()) / sum(tot.values()), 4),
            "rappel_avec_relecture": round(sum(revu.values()) / sum(tot.values()), 4),
            "fuites": dict(fuite), "fuites_total": sum(fuite.values()),
            "degats_juridiques": f"{degats}/{total_droit}", "faux_positifs": faux, "exemples_manques": dict(exemples)}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    a = argparse.ArgumentParser()
    a.add_argument("--n", type=int, default=400)
    a.add_argument("--graine", type=int, default=7)
    args = a.parse_args()
    res = [evaluer(args.n, args.graine, d) for d in (False, True)]
    for r in res:
        print(f"\n== {r['scenario']} ({r['pieces']} pièces) : rappel global {r['rappel_global']}, avec relecture des signalés "
              f"{r['rappel_avec_relecture']}, fuites {r['fuites_total']}, "
              f"dégâts juridiques {r['degats_juridiques']}, faux positifs {r['faux_positifs']}")
        for c, v in r["rappel"].items():
            print(f"   {c:16} {v:.4f}  ({r['mentions'][c]} mentions, {r['fuites'].get(c, 0)} fuites)")
        for c, ex in r["exemples_manques"].items():
            print(f"   manqués {c}: {ex}")
    (ICI / "resultats.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
