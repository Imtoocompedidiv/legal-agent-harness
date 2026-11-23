"""Pseudonymisation d'un dossier d'affaire avant tout travail du modèle, et ré-identification locale des actes.

Le modèle ne voit que des jetons ([PERSONNE_3], [ADRESSE_1]...). Rien de réel ne vit dans le dossier où il travaille : les
originaux restent où l'avocat les garde ; la clé, la table de correspondance chiffrée, le rapport de relecture et les actes
ré-identifiés vivent dans un coffre hors de l'arbre de travail. L'avocat relit chaque copie avant que l'agent puisse la lire, et
ré-identifie lui-même les actes définitifs.

Une pseudonymisation n'est pas une anonymisation : les données restent personnelles (RGPD, art. 4, 5 ; EDPB, lignes directrices
01/2025). Elle réduit le risque de transmettre des identités au fournisseur du modèle ; elle ne dispense ni du secret professionnel
ni de l'analyse de risque du cabinet, et les faits eux-mêmes peuvent identifier (métier rare, petite commune, dates).

Détection en couches, mesurées sur le corpus d'évaluation (evaluation/evaluer.py) :
  1. dictionnaire du dossier : parties, témoins, numéros propres à l'affaire, déclarés par l'avocat, avec leurs variantes ;
  2. identifiants structurés validés par leur clé : IBAN (modulo 97), NIR (clé), SIREN et SIRET (Luhn), carte bancaire (Luhn),
     courriel, téléphone, adresse IP, immatriculation, numéros Portalis et RG, identifiants introduits par leur nom ;
  3. personnes reconnues par une civilité, un prénom connu, un nom en capitales ou un lien (épouse, née, veuve) ;
  4. adresses postales et dates de naissance reconnues par leur forme et leur contexte ;
  5. modèle de repérage facultatif (GLiNER, si installé et désigné) ;
  6. propagation : toute forme trouvée une fois est remplacée partout ;
  7. mots à majuscule inconnus soumis à la relecture, jamais ignorés en silence.

    python pseudonymisation.py init [--coffre DOSSIER]           active le mode, crée le coffre, pseudonymise l'existant
    python pseudonymisation.py ajouter "Paul Martin" [--categorie PERSONNE] [--role témoin]
    python pseudonymisation.py importer FICHIER...               originaux -> pieces/pseudonymisees/ et rapport dans le coffre
    python pseudonymisation.py valider                           l'avocat atteste avoir relu le rapport et les copies
    python pseudonymisation.py reidentifier FICHIER [--sortie DOSSIER]
    python pseudonymisation.py verifier                          cherche toute donnée réelle dans le dossier de travail
    python pseudonymisation.py hook                              entrée des hooks Claude Code (stdin)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

ETAT = ".pseudonymisation"
MARQUEUR_AFFAIRE = Path("etat") / "affaire.json"
COPIES = Path("pieces") / "pseudonymisees"
COFFRE_ENV = "HARNESS_PSEUDONYMISATION_COFFRE"
TEXTES = (".md", ".txt", ".json", ".csv", ".eml", ".html", ".htm", ".xml")
# Fermés à l'agent en mode pseudonymisé : pieces/originaux (vide dans ce mode), les extractions brutes des pièces, et tout coffre.
PROTEGES = re.compile(r"(?:^|[\\/\s\"'=])pieces[\\/]+originaux(?:[\\/\s\"']|$)|\.extraction\.txt\b|\.harness-juridique[\\/]+pseudonymisation", re.I)

CIVILITES = (r"(?:M\.|MM\.|Mme|Mmes|Mlle|Mlles|Me|Dr|Pr|(?i:monsieur|messieurs|madame|mesdames|mademoiselle|maître|maitre|docteur|"
             r"professeur|le docteur|la docteure))")
FONCTION = r"(?:le|la|les|l['’])\s"
PARTICULE = r"(?:de|du|des|d['’]|le|la|van|von|der|ben|bin|ibn|el|al|da|di|dos|do|ould|ait|aït)"
MAJ = "A-ZÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸÆŒ"
MIN = "a-zàâäçéèêëîïôöùûüÿæœß"
MOT_NOM = (rf"(?:[{MAJ}]['’][{MAJ}][{MIN}]+|[{MAJ}][{MIN}]+(?:[-’'][{MAJ}]?[{MIN}]+)*|[{MAJ}]{{2,}}(?:[-’'][{MAJ}]{{2,}})*|"
           rf"[{MAJ}]['’][{MAJ}]{{2,}}|[{MAJ}]\.)")
SUITE_NOM = rf"(?:{PARTICULE}[ \t]+)?{MOT_NOM}(?:[ \t]+(?:{PARTICULE}[ \t]+)?{MOT_NOM}){{0,3}}"
MOIS = r"(?:janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre)"
DATE = rf"(?:\d{{1,2}}(?:er)?\s+{MOIS}\s+\d{{4}}|\d{{1,2}}[/.-]\d{{1,2}}[/.-](?:\d{{4}}|\d{{2}}))"
# Types de voie. Avec un numéro, tous ; sans numéro, seulement ceux qui ne sont pas aussi des mots courants (« au cours de »,
# « par voie de », « à la place de » restent du texte), et suivis d'un nom à majuscule.
VOIES = (r"(?:rue|avenue|av\.|boulevard|bd|bld|chemin|allée|allee|impasse|place|route|rte|quai|cours|square|passage|sentier|"
         r"rond-point|faubourg|fg|lieu-dit|lieudit|résidence|residence|cité|cite|hameau|lotissement|voie|villa|montée|promenade|"
         r"esplanade|parvis|traverse|chaussée|ruelle|clos|domaine|venelle|carrefour)")
VOIES_SURES = r"(?:rue|avenue|boulevard|impasse|allée|allee|quai|square|lieu-dit|faubourg|hameau|lotissement|ruelle|venelle|esplanade|chaussée)"

NON_NOMS = set("""
abs absence accord acte actes administration affaire agence aide alinéa allocation annexe appel arrêt arrêté article articles
assemblée association attendu attestation audience autorité avenant avis avocat avocats bâtonnier bureau caisse cabinet cassation
centre chambre chapitre cnil code commission commune conclusions conseil considérant constitution contrat convention cour cours
cpam crpa cedh cja ceseda civil date décembre décision déclaration décret défendeur défense délibération demandeur département
direction dispositif document dossier droit état europe européen européenne février france français française gouvernement greffe
greffier haut instance inspection janvier juge juges jugement juillet juin justice lettre livre loi lundi mardi mars mercredi jeudi
vendredi samedi dimanche mai ministère ministre motifs nation nationale novembre objet octobre office ordonnance page paris pièce
pièces police préfecture préfet président présidente procédure procureur protocole rapport recours référé région registre règlement
renvoi requérant requérante requête république réponse rôle section secrétariat septembre service société sommaire statut syndicat
tableau texte titre tribunal union urssaf vu vus total madame monsieur maître docteur avril août aout fevrier decembre mme mlle
oui non selon sauf ainsi enfin puis donc mais car aussi alors elle il ils elles nous vous je tu on le la les un une des du de au aux ce
cet cette ces son sa ses leur leurs notre nos votre vos mon ma mes par pour sur sous dans avec sans entre vers chez dès depuis pendant
après avant contre lors sécurité sociale travail emploi caf pôle bodacc inpi insee cedex tél tel fax mél courriel objet réf
signé signée fait lu approuvé madame monsieur bonjour cordialement salutations destinataire expéditeur pièce jointe annexes
""".split())

PRENOMS = set("""
aaron abdel abdelkader abdellah abdou abdoulaye abel abigaïl adam adama adel adèle adelaïde adeline adil adrien adrienne agathe agnès
ahmed aïcha aimé aimée alain alan albane albert alberte alexandra alexandre alexia alexis alfred ali alice alicia aline alix amadou
amandine amaury ambre amel amélie amina aminata amine amir anaïs andré andrée andréa ange angela angèle angélique anissa anne annette
annick annie anthony antoine antoinette antonin antonio apolline ariane arielle arlette armand armelle arnaud arthur assia astrid
athénaïs aude audrey augustin aurélie aurélien aurore axel axelle aya aymeric aziz baptiste barbara bastien béatrice benjamin benoît
benoit bérangère bernadette bernard bertrand blanche boris brice brigitte bruno camille capucine carine carla carmen carole caroline
cassandra catherine cécile cédric céline chantal charles charlotte chloé christelle christian christiane christine christophe claire
clara clarisse claude claudette claudine claudia clément clémence clémentine coline colette constance corentin corinne cyril cyrielle
damien daniel danielle dany david davy déborah delphine denis denise diane didier dimitri djamel dominique dorian doriane dorothée
dylan edith édith edmond édouard eléonore éléonore elias élie élisa élisabeth élise ella elodie élodie éloïse elsa émile émilie émilien
emma emmanuel emmanuelle enzo éric erica ernest esteban estelle esther ethan étienne eugène eugénie eva evelyne évelyne fabien fabienne
fabrice fanny farid fatima fatou fatoumata félicie félix fernand fernande florence florent florian francis franck françois françoise
frédéric frédérique gabin gabriel gabrielle gaël gaëlle gaëtan gaston geneviève georges georgette gérald gérard germaine ghislaine
gilbert gilberte gilles ginette gisèle grégoire grégory guillaume guy gwenaël gwendoline hakim halima hamid hassan hector hélène
henri henriette hervé hippolyte honorine hortense hugo hugues ibrahim ibrahima inès irène isabelle isaac ismaël jacqueline jacques
jade jamel janine jean jeanne jeannine jérémie jérémy jérôme jessica joël joëlle johan johanna jonathan jordan joseph josette joséphine
josiane judith jules julia julie julien juliette justin justine karim karima karine katia kelly kevin kévin khadija lætitia laetitia
laura laure laurence laurent léa léna léo léon léonie léonard liliane lina lisa lise loïc lola lou louis louise luc luca lucas lucie
lucien lucienne lucile ludovic lydie lysiane madeleine maël maëlle magali maïa malik malika mamadou manon marc marcel marcelle
margaux margot marguerite maria marianne marie mariam marine marion marius marjorie marthe martin martine maryse mathéo mathias
mathieu mathilde mathis matthieu maud maurice max maxence maxime mélanie mélissa mélodie michel michèle micheline mickaël mila
mireille mohamed mohammed monique morgane mounir moussa muriel myriam nadia nadine naïma nathalie nathan nicolas nicole nina noah
noé noémie noël nora océane octave odette odile olivia olivier omar oscar pascal pascale patrice patricia patrick paul paule
paulette pauline perrine philippe pierre pierrette quentin rachel rachid raphaël raphaëlle raymond raymonde rayan régine régis
rémi rémy renée rené richard robert roger roland romain romane rose rosalie roxane ruben ryan sabine sabrina sacha salomé salma
samia samir samuel sandra sandrine sarah sébastien serge sévérine séverine simon simone solange solène sonia sophie stéphane
stéphanie suzanne sylvain sylvie tatiana théa théo théodore thérèse thibault thibaut thierry thomas timothée tom valentin valentine
valérie vanessa véronique victor victoria vincent virginie vivien viviane wassim william xavier yanis yann yannick yasmine yassine
yves yvette yvonne youssef zoé zinedine
""".split())


def plier(t: str) -> str:
    """Forme de comparaison : sans accents, en minuscules, espaces réduits, apostrophes unifiées."""
    t = unicodedata.normalize("NFKD", t.replace("’", "'"))
    return re.sub(r"\s+", " ", "".join(c for c in t if not unicodedata.combining(c))).strip().lower()


PRENOMS_PLIES = {plier(p) for p in PRENOMS}
NON_NOMS_PLIES = {plier(w) for w in NON_NOMS}
MOTS_GRAMMATICAUX = {plier(w) for w in "le la les un une des du de d' et ou qui que dont son sa ses leur leurs mon ma mes ce cette ces".split()}
# Sigles administratifs et juridiques en capitales, qui ne sont jamais des noms de personnes.
SIGLES = set("""CAF CPAM URSSAF SNCF RATP EDF GDF ENGIE ANEF OQTF IRTF OFII OFPRA CNDA CESEDA CRPA CASF CGFP CJA CPC CPP RCS SIRET SIREN TVA
SMIC RSA APL AAH CDI CDD CSE CHSCT CHU CHR SAMU ARS ICPE PLU PLUI SCOT DREAL DDT DDETS DIRECCTE DGFIP INSEE INPI BODACC CNIL CNB CEDH CJUE
TFUE ONU UNESCO OCDE RGPD LCEN AGDREF ASE PMI MDPH CCAS CMU AME CSG CRDS PACS JAF JLD JEX JCP TGI TJ TA CAA CE QPC AJ BAJ RIB IBAN BIC
NIR PDF HTML URL EHPAD IME ESAT CROUS EPCI SDIS SAMU SMUR PJ OPJ APJ GAV TTC HT""".split())


def est_prenom(mot: str) -> bool:
    return all(plier(p) in PRENOMS_PLIES for p in mot.split("-") if p)


# ---------------------------------------------------------------- identifiants validés par leur clé

def _chiffres(t: str) -> str:
    return re.sub(r"\D", "", t)


def luhn(n: str) -> bool:
    if not n.isdigit() or len(n) < 2:
        return False
    s = 0
    for i, c in enumerate(reversed(n)):
        d = int(c) * (2 if i % 2 else 1)
        s += d - 9 if d > 9 else d
    return s % 10 == 0


def iban_valide(t: str) -> bool:
    t = re.sub(r"\s", "", t).upper()
    if not re.fullmatch(r"[A-Z]{2}\d{2}[A-Z0-9]{10,30}", t):
        return False
    r = t[4:] + t[:4]
    return int("".join(str(int(c, 36)) for c in r)) % 97 == 1


def nir_valide(t: str) -> bool:
    t = re.sub(r"[\s.]", "", t).upper()
    m = re.fullmatch(r"([12378])(\d{2})(0[1-9]|1[0-2]|[2-9]\d)(\d{2}|2A|2B)(\d{3})(\d{3})(\d{2})?", t)
    if not m:
        return False
    if m.group(7) is None:
        return True
    corps = t[:13].replace("2A", "19").replace("2B", "18")
    return 97 - int(corps) % 97 == int(m.group(7))


def siret_valide(t: str) -> bool:
    n = _chiffres(t)
    return len(n) == 14 and (luhn(n) or (n.startswith("356000000") and sum(map(int, n)) % 5 == 0))


@dataclass
class Trouvaille:
    debut: int
    fin: int
    categorie: str
    texte: str
    couche: str


MOTIFS = [
    ("EMAIL", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"), None),
    ("PSEUDONYME_EN_LIGNE", re.compile(r"(?<![\w@])@[A-Za-z0-9_.]{3,30}\b"), None),
    ("IBAN", re.compile(r"\b[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]{4}){2,7}(?:[ ]?[A-Z0-9]{1,4})?\b"), iban_valide),
    ("CARTE_BANCAIRE", re.compile(r"\b(?:\d{4}[ -]?){3}\d{1,4}\b"), lambda t: 13 <= len(_chiffres(t)) <= 19 and luhn(_chiffres(t))),
    ("NIR", re.compile(r"\b[12378][ ]?\d{2}[ ]?(?:0[1-9]|1[0-2]|[2-9]\d)[ ]?(?:\d{2}|2[AB])[ ]?\d{3}[ ]?\d{3}(?:[ ]?\d{2})?\b", re.I), nir_valide),
    ("SIRET", re.compile(r"\b\d{3}[ ]?\d{3}[ ]?\d{3}[ ]?\d{5}\b"), siret_valide),
    ("SIREN", re.compile(r"(?i)\b(?:siren|rcs[^\n\d]{0,30}|immatriculée? sous le (?:numéro|n°))\s*:?\s*(\d{3}[ ]?\d{3}[ ]?\d{3})\b"), lambda t: luhn(_chiffres(t))),
    ("TELEPHONE", re.compile(r"(?<![\d+])(?:(?:\+|00)33[ ]?\(?0?\)?[ ]?|0)[1-9](?:[ .-]?\d{2}){4}(?!\d)|(?<![\d+])\+(?!33)\d{1,3}(?:[ .-]?\d{2,4}){3,5}(?!\d)"), None),
    ("IP", re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"), None),
    ("IMMATRICULATION", re.compile(r"\b[A-HJ-NP-TV-Z]{2}[- ]\d{3}[- ][A-HJ-NP-TV-Z]{2}\b"), None),
    ("NUMERO_AFFAIRE", re.compile(r"(?i)\bPortalis\s+[A-Z0-9]{4}-[A-Z]-[A-Z0-9]{3}-[A-Z0-9-]{3,10}\b|\bRG\s*(?:n°|no|:)?\s*([A-Z]?[ ]?\d{2}/\d{3,6})\b"), None),
    ("IDENTIFIANT", re.compile(r"(?i)\b(?:passeport|carte (?:nationale )?d['’]identité|CNI|titre de séjour|carte de (?:séjour|résident)|"
                               r"récépissé|AGDREF|(?:numéro|n°) (?:d['’])?étranger|(?:numéro|n°) (?:d['’])?allocataire|allocataire|"
                               r"(?:numéro|n°) fiscal|identifiant fiscal|SPI|matricule|(?:numéro|n°) de (?:dossier|client|contrat|police|compte|adhérent)|"
                               r"référence (?:client|dossier)|permis de conduire)(?:[^\d\n]{0,60}?)(?:n°|no|numéro|nº)?\s*:?\s*([A-Z0-9][A-Z0-9 ./-]{4,24}[A-Z0-9])"), None),
]


CONTEXTE_NIR = re.compile(r"(?i)(?:NIR|sécurité sociale|n°\s*SS|numéro\s+SS|INSEE|immatriculation)\W{0,12}$")
CONTEXTE_COMPTE = re.compile(r"(?i)(?:IBAN|RIB|compte|virement|prélèvement|coordonnées bancaires)[^\n]{0,30}$")


def identifiants(texte: str) -> list[Trouvaille]:
    out = []
    # Un IBAN désigné comme tel se prend même si sa clé est fausse.
    for m in re.finditer(r"\b[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]{4}){3,7}(?:[ ]?[A-Z0-9]{1,4})?\b", texte):
        if CONTEXTE_COMPTE.search(texte[max(0, m.start() - 40):m.start()]):
            out.append(Trouvaille(m.start(), m.end(), "IBAN", m.group(0), "identifiant"))
    # Un NIR introduit par son nom se prend même si sa clé est fausse : une faute de frappe ne rend pas la donnée anonyme.
    for m in re.finditer(r"\b[12378][ ]?\d{2}[ ]?\d{2}[ ]?(?:\d{2}|2[AB])[ ]?\d{3}[ ]?\d{3}(?:[ ]?\d{2})?\b", texte, re.I):
        if CONTEXTE_NIR.search(texte[max(0, m.start() - 40):m.start()]):
            out.append(Trouvaille(m.start(), m.end(), "NIR", m.group(0), "identifiant"))
    for cat, motif, valide in MOTIFS:
        for m in motif.finditer(texte):
            g = 1 if m.groups() and m.group(1) else 0
            val, d, f = m.group(g), m.start(g), m.end(g)
            if cat == "IDENTIFIANT":
                val = re.sub(r"[ ./-]+$", "", val)
                f = d + len(val)
                if not re.search(r"\d", val) or len(_chiffres(val)) < 4:
                    continue
            if valide and not valide(val):
                continue
            out.append(Trouvaille(d, f, cat, val, "identifiant"))
    return out


# ---------------------------------------------------------------- personnes, adresses, naissances

def _nom_valide(mot: str) -> bool:
    m = mot.strip(".")
    return len(m) >= 2 and plier(m) not in NON_NOMS_PLIES


def personnes(texte: str) -> list[Trouvaille]:
    out = []
    for m in re.finditer(rf"\b{CIVILITES}[ \t]+(?!{FONCTION})({SUITE_NOM})", texte):
        mots = m.group(1).split()
        while mots and not _nom_valide(mots[-1]):
            mots.pop()
        # « M. D... B... » des décisions publiées est déjà pseudonymisé ; une initiale seule ne se remplace pas.
        if not mots or all(re.fullmatch(rf"[{MAJ}]\.", w) for w in mots) or not any(_nom_valide(w) for w in mots):
            continue
        val = " ".join(mots)
        out.append(Trouvaille(m.start(1), m.start(1) + len(val), "PERSONNE", val, "civilite"))
    for m in re.finditer(rf"\b([{MAJ}][{MIN}]+(?:-[{MAJ}][{MIN}]+)?)[ \t]+((?:{PARTICULE}[ \t]+)?{MOT_NOM}(?:[- ]{MOT_NOM})?)", texte):
        nom = m.group(2)
        if est_prenom(m.group(1)) and _nom_valide(nom.split()[-1]) and not re.fullmatch(rf"[{MAJ}]\.", nom):
            out.append(Trouvaille(m.start(), m.end(), "PERSONNE", m.group(0), "prenom"))
    # Un nom en capitales accolé à un mot à majuscule est, dans un acte français, un nom de personne (« Kwame FERREIRA »,
    # « FERREIRA Kwame ») : la forme suffit, sans lexique de prénoms.
    for m in re.finditer(rf"\b((?:[{MAJ}]['’])?[{MAJ}]{{2,}}(?:[-' ’][{MAJ}]{{2,}})*)[ \t]+([{MAJ}][{MIN}]+(?:[- ][{MAJ}][{MIN}]+)?)\b|"
                         rf"\b([{MAJ}][{MIN}]+(?:[- ][{MAJ}][{MIN}]+)?)[ \t]+((?:{PARTICULE}[ \t]+)?(?:[{MAJ}]['’])?[{MAJ}]{{2,}}(?:[-' ’][{MAJ}]{{2,}})*)\b", texte):
        nom, prenom = (m.group(1), m.group(2)) if m.group(1) else (m.group(4), m.group(3))
        if _nom_valide(nom.split()[-1]) and all(_nom_valide(w) for w in prenom.split()) and len(re.sub(r"\W", "", nom)) >= 2:
            out.append(Trouvaille(m.start(), m.end(), "PERSONNE", m.group(0), "capitales"))
    # Rôles qui introduisent un nom dans les pièces : signataire, témoin, assistant, représentant, garant, gérant.
    for m in re.finditer(rf"(?i:\b(?:je soussignée?|signée?|signature|témoin|assistée? (?:de|par)|représentée? par|garant|gérant|gérante|"
                         rf"entre|établi par|rédigé par|ainsi que|devant chez|chez|de la part de|atteste que|salariée?|locataire|bailleur)"
                         rf"[ \t]*[:,]?[ \t]+)"
                         rf"((?:{CIVILITES}[ \t]+)?(?:[{MAJ}]\.[ \t]*)?{SUITE_NOM})", texte):
        mots = m.group(1).split()
        while mots and not _nom_valide(mots[-1]):
            mots.pop()
        if mots and any(_nom_valide(w) for w in mots if not re.fullmatch(rf"[{MAJ}]\.", w)) and not re.fullmatch(CIVILITES, mots[0]):
            val = " ".join(mots)
            out.append(Trouvaille(m.start(1), m.start(1) + len(val), "PERSONNE", val, "role"))
    # Signature suivie d'une qualité (« Bérénice Taillandier, avocate »), et « je m'appelle X », « mon nom est X ».
    for m in re.finditer(rf"(?m)^[ \t]*((?:[{MAJ}][{MIN}]+(?:-[{MAJ}][{MIN}]+)?[ \t]+)+(?:{PARTICULE}[ \t]+)?{MOT_NOM})[ \t]*,[ \t]*(?i:avocate?|gérante?|"
                         rf"directeur|directrice|présidente?|notaire|huissier|commissaire|experte?|médecin|docteure?|mandataire|liquidateur|"
                         rf"conseiller|conseillère|juriste|secrétaire|responsable|chef|cheffe|assistante?|infirmière?)\b", texte):
        if all(_nom_valide(w) for w in m.group(1).split()):
            out.append(Trouvaille(m.start(1), m.end(1), "PERSONNE", m.group(1), "signature"))
    for m in re.finditer(rf"(?i:\b(?:je m['’]appelle|mon nom est|je me nomme|je suis nommée?|prénommée?|surnommée?)[ \t]+)({SUITE_NOM})", texte):
        if any(_nom_valide(w) for w in m.group(1).split()):
            out.append(Trouvaille(m.start(1), m.end(1), "PERSONNE", m.group(1), "role"))
    # Un nom en capitales, seul au milieu d'une phrase (« j'ai vu MOREAU crier »), est un nom de famille ; les sigles connus non.
    for m in re.finditer(rf"(?<=[{MIN},;'’] )((?:[{MAJ}]['’])?[{MAJ}]{{4,}}(?:-[{MAJ}]{{2,}})?)\b(?![ \t]*[:(\[])", texte):
        if plier(m.group(1)) not in NON_NOMS_PLIES and m.group(1) not in SIGLES:
            out.append(Trouvaille(m.start(1), m.end(1), "PERSONNE", m.group(1), "capitales"))
    # Le courriel livre le nom : « marie.durand@... » fait chercher « Marie Durand » et « Durand » partout.
    for m in re.finditer(r"\b([A-Za-z]{2,})[._-]([A-Za-z'-]{2,})@", texte):
        for nom in (m.group(2),):
            for o in re.finditer(rf"\b{re.escape(nom)}\b", texte, re.I):
                w = texte[o.start():o.end()]
                if w[:1].isupper() and _nom_valide(w):
                    out.append(Trouvaille(o.start(), o.end(), "PERSONNE", w, "courriel"))
    for m in re.finditer(rf"\b(?:épouse|époux|veuve|née|dite?|alias)[ \t]+({MOT_NOM}(?:[- ]{MOT_NOM})?)", texte):
        if _nom_valide(m.group(1)):
            out.append(Trouvaille(m.start(1), m.end(1), "PERSONNE", m.group(1), "lien"))
    # Un prénom seul après un lien de parenté ou de proximité désigne une personne (« leur fille Léa », « son fils, Yanis »).
    for m in re.finditer(rf"\b(?:fils|fille|enfant|enfants|bébé|frère|sœur|soeur|mère|père|mari|femme|épouse|époux|compagnon|compagne|"
                         rf"concubin|concubine|conjoint|conjointe|petit-fils|petite-fille|neveu|nièce|cousin|cousine|oncle|tante|ami|amie|"
                         rf"voisin|voisine|collègue|prénommée?|salariée?|employée?|élève|patiente?|mineure?)[ \t,]+((?:[{MAJ}][{MIN}]+(?:-[{MAJ}][{MIN}]+)?)(?:[ \t](?:{PARTICULE}[ \t])?{MOT_NOM}){{0,2}})\b", texte):
        # Après un lien, un mot à majuscule est un prénom, même hors du lexique ou homonyme d'un mot courant (« sa fille Oumou »,
        # « l'enfant Abdelhakim », « sa fille Mai ») ; seuls les mots grammaticaux s'excluent.
        if all(plier(w) not in MOTS_GRAMMATICAUX for w in m.group(1).split()):
            out.append(Trouvaille(m.start(1), m.end(1), "PERSONNE", m.group(1), "lien"))
    # Locuteur d'une transcription : « [03/03 21:20] Marjolaine : », « 21:14 - Kévin : ».
    for m in re.finditer(rf"(?m)^[ \t]*(?:\[[^\]\n]{{3,30}}\]|\d{{1,2}}[:h]\d{{2}}(?:[ \t]*[-–])?)[ \t]*((?:[{MAJ}][{MIN}]+(?:[- ][{MAJ}][{MIN}]+)?|[{MAJ}]{{2,}}))[ \t]*:", texte):
        if plier(m.group(1)) not in MOTS_GRAMMATICAUX and _nom_valide(m.group(1)):
            out.append(Trouvaille(m.start(1), m.end(1), "PERSONNE", m.group(1), "locuteur"))
    # Un prénom connu, seul, désigne une personne, sauf dans un nom de voie ou de lieu (« rue Victor », « Saint-Pierre »).
    for m in re.finditer(rf"(?<![-\w])([{MAJ}][{MIN}]+(?:-[{MAJ}][{MIN}]+)?)\b", texte):
        if est_prenom(m.group(1)) and not re.search(rf"(?i:{VOIES}|saint|sainte|st|ste)[ \t-]*$", texte[max(0, m.start() - 14):m.start()]):
            out.append(Trouvaille(m.start(1), m.end(1), "PERSONNE", m.group(1), "prenom_seul"))
    # Un nom seul suivi d'un verbe d'acte (« N'Diaye signe », « Lambert atteste ») est une personne.
    for m in re.finditer(rf"\b({MOT_NOM})[ \t]+(?:a[ \t]+)?(?:signe|signé|déclare|déclaré|atteste|attesté|indique|indiqué|reconnaît|reconnu|"
                         rf"conteste|contesté|affirme|soutient|explique|précise|ajoute|répond|refuse|accepte|confirme|dénonce|se présente)\b", texte):
        if _nom_valide(m.group(1)) and not re.fullmatch(rf"[{MAJ}]\.", m.group(1)):
            out.append(Trouvaille(m.start(1), m.end(1), "PERSONNE", m.group(1), "verbe"))
    return out


FORMES_SOCIALES = (r"(?:Société|Sté|SARL|SAS|SASU|SA|SCI|SCEA|EARL|GAEC|EURL|SNC|SCP|SELARL|SELAS|SELAFA|AARPI|SCM|Association|"
                   r"Entreprise|Établissements|Ets|Groupe|Fondation|Mutuelle|Cabinet|Étude|Office notarial)")


def organisations(texte: str) -> list[Trouvaille]:
    """Personnes morales de droit privé introduites par leur forme (« la société Alpha Conseil », « SCI Les Tilleuls »)."""
    out = []
    for m in re.finditer(rf"(?:\b(?i:{FORMES_SOCIALES})[ \t]+|(?i:\b(?:employeur|bailleur|cocontractant|prestataire|fournisseur|assureur|"
                         rf"raison sociale|dénomination)\s*:?[ \t]+))((?:(?i:{PARTICULE}|les?|la)[ \t]+)?(?:[{MAJ}0-9][\w{MAJ}{MIN}&'’.-]*)"
                         rf"(?:[ \t]+(?:{PARTICULE}|et|&|[{MAJ}][\w{MAJ}{MIN}&'’.-]*)){{0,4}})", texte):
        mots = m.group(1).split()
        # « Conseil », « Transports », « Clinique » font partie d'une raison sociale : seuls les mots de liaison et SIRET se retirent.
        while mots and (plier(mots[-1]) in ("siret", "siren", "rcs", "et", "&", "sous", "immatriculée", "au") or re.fullmatch(PARTICULE, mots[-1])):
            mots.pop()
        val = " ".join(mots)
        if val and (_nom_valide(mots[0]) or len(mots) > 1):
            out.append(Trouvaille(m.start(1), m.start(1) + len(val), "ORGANISATION", val, "forme_sociale"))
    return out


def adresses(texte: str) -> list[Trouvaille]:
    out = []
    nom_voie = rf"(?:(?:{PARTICULE}|l['’]|d['’])[ \t]*)*[\w{MAJ}{MIN}'’.-]+(?:[ \t]+(?:{PARTICULE}|[{MAJ}][\w{MAJ}{MIN}'’.-]*|\d{{1,4}}\b(?![ \t]*[{MAJ}])))*"
    for motif in (rf"\b\d{{1,4}}(?:[ \t]?(?:bis|ter|quater|[A-D]))?,?[ \t]+(?i:{VOIES})[ \t]+{nom_voie}",
                  rf"\b(?i:{VOIES_SURES})[ \t]+(?:(?:{PARTICULE}|l['’]|d['’])[ \t]*)*[{MAJ}][\w{MAJ}{MIN}'’.-]*(?:[ \t]+(?:{PARTICULE}|[{MAJ}][\w{MAJ}{MIN}'’.-]*))*"):
        for m in re.finditer(motif, texte):
            val = re.sub(rf"(?:[ \t]+(?:{PARTICULE}))+$", "", m.group(0).rstrip(" ,.;"))
            out.append(Trouvaille(m.start(), m.start() + len(val), "ADRESSE", val, "adresse"))
    for m in re.finditer(rf"\b(?:F-)?\d{{5}}[ \t]+[{MAJ}][\w{MAJ}{MIN}'’-]+(?:[ \t-]+(?:sur|sous|en|lès|les|le|la|de|du)?[ \t-]*[{MAJ}][\w{MAJ}{MIN}'’-]+){{0,3}}(?:[ \t]+Cedex(?:[ \t]+\d{{1,2}})?)?", texte):
        out.append(Trouvaille(m.start(), m.end(), "ADRESSE", m.group(0), "code_postal"))
    for m in re.finditer(r"(?i)\b(?:BP|boîte postale|CS)[ \t]*\d{2,6}\b", texte):
        out.append(Trouvaille(m.start(), m.end(), "ADRESSE", m.group(0), "boite_postale"))
    # Immeubles et ensembles nommés, bâtiment, escalier, appartement : « Résidence Les Mimosas, Bât. C, apt 12 ».
    for m in re.finditer(rf"\b(?:(?i:résidence|residence|immeuble|cité|domaine|lotissement|hameau|villa|tour|ZA|ZI|ZAC|ZAE|parc d['’]activités?|"
                         rf"zone d['’]activités?|zone industrielle|zone artisanale)[ \t]+(?:(?:les?|la|l['’]|du|des|de|d['’])[ \t]*)?"
                         rf"[{MAJ}][\w{MAJ}{MIN}'’-]*(?:[ \t]+[{MAJ}][\w{MAJ}{MIN}'’-]*){{0,3}})(?:[ \t]*,?[ \t]*(?i:bât(?:iment)?\.?|esc(?:alier)?\.?|"
                         rf"apt\.?|appartement|porte|étage)[ \t]*[\w]{{1,4}})*", texte):
        out.append(Trouvaille(m.start(), m.end(), "ADRESSE", m.group(0), "immeuble"))
    return out


def naissances(texte: str) -> list[Trouvaille]:
    out = []
    for m in re.finditer(rf"(?i)\b(?:né|née|né\(e\)|nés|nées)[ \t]+le[ \t]+({DATE})(?:[ \t]+à[ \t]+((?-i:{SUITE_NOM})))?|date de naissance\s*:?\s*({DATE})", texte):
        for g, cat in ((1, "DATE_NAISSANCE"), (3, "DATE_NAISSANCE"), (2, "LIEU_NAISSANCE")):
            if m.group(g):
                out.append(Trouvaille(m.start(g), m.end(g), cat, m.group(g), "naissance"))
    for m in re.finditer(r"(?i)\b(?:né|née)[ \t]+en[ \t]+(\d{4})\b", texte):
        out.append(Trouvaille(m.start(1), m.end(1), "DATE_NAISSANCE", m.group(1), "naissance"))
    return out


def suspects(texte: str, connus: set[str]) -> list[str]:
    """Mots à majuscule au milieu d'une phrase, ni connus ni courants, ni jetons : soumis à la relecture."""
    vus = []
    for m in re.finditer(rf"\b([{MAJ}][{MIN}]{{2,}}|[{MAJ}]{{3,}})\b", texte):
        avant = texte[max(0, m.start() - 3):m.start()]
        if m.start() == 0 or re.search(r"[.!?:\n\[]\s*$", avant) or texte[m.end():m.end() + 1] == "_":
            continue
        w, p = m.group(1), plier(m.group(1))
        # Un prénom seul reste suspect : il désigne souvent un enfant ou un proche.
        if p in NON_NOMS_PLIES or p in connus or w in vus:
            continue
        vus.append(w)
    return vus


# ---------------------------------------------------------------- modèle facultatif

def modele(texte: str) -> list[Trouvaille]:
    """GLiNER si installé et désigné par HARNESS_PSEUDONYMISATION_MODELE (nom ou chemin local) ; sinon rien."""
    nom = os.environ.get("HARNESS_PSEUDONYMISATION_MODELE")
    if not nom:
        return []
    try:
        from gliner import GLiNER  # type: ignore
    except ImportError:
        return []
    m = GLiNER.from_pretrained(nom)
    etiquettes = {"person": "PERSONNE", "address": "ADRESSE", "phone number": "TELEPHONE", "email": "EMAIL", "date of birth": "DATE_NAISSANCE",
                  "organization": "ORGANISATION", "passport number": "IDENTIFIANT", "social security number": "NIR", "bank account number": "IBAN"}
    seuil = float(os.environ.get("HARNESS_PSEUDONYMISATION_SEUIL", "0.4"))
    out = []
    for debut in range(0, len(texte), 1500):
        for e in m.predict_entities(texte[debut:debut + 1700], list(etiquettes), threshold=seuil):
            out.append(Trouvaille(debut + e["start"], debut + e["end"], etiquettes[e["label"]], e["text"], "modele"))
    return out


# ---------------------------------------------------------------- coffre, clé, table

def racine_affaire(depart: Path) -> Path | None:
    p = Path(depart).resolve()
    for d in [p, *p.parents]:
        if (d / MARQUEUR_AFFAIRE).is_file():
            return d
    return None


def actif(racine: Path) -> bool:
    return (racine / ETAT / "actif.json").is_file()


def coffre(racine: Path) -> Path:
    """Le coffre du dossier : celui que nomme actif.json, sinon HARNESS_PSEUDONYMISATION_COFFRE, sinon ~/.harness-juridique."""
    f = racine / ETAT / "actif.json"
    if f.is_file():
        return Path(json.loads(f.read_text(encoding="utf-8"))["coffre"])
    base = Path(os.environ[COFFRE_ENV]) if os.environ.get(COFFRE_ENV) else Path.home() / ".harness-juridique" / "pseudonymisation"
    return base / hashlib.sha256(str(racine.resolve()).encode()).hexdigest()[:16]


def _fernet(racine: Path):
    try:
        from cryptography.fernet import Fernet  # type: ignore
    except ImportError:
        raise SystemExit("Le chiffrement de la table exige le paquet « cryptography » (pip install cryptography).")
    return Fernet((coffre(racine) / "cle").read_bytes().strip())


def variantes(valeur: str, categorie: str) -> list[str]:
    """Formes sous lesquelles une même entité apparaît dans les pièces."""
    v = re.sub(r"\s+", " ", valeur).strip()
    formes = {v, v.upper()}
    if categorie == "PERSONNE":
        mots = v.split(" ")
        prenoms = [w for w in mots if est_prenom(w) and not w.isupper()]
        if prenoms and len(prenoms) < len(mots):
            nom = " ".join(w for w in mots if w not in prenoms)
            if _nom_valide(nom.split()[-1]):
                formes |= {nom, nom.upper(), " ".join(w.capitalize() if w.isupper() else w for w in nom.split()),
                           f"{nom.upper()} {' '.join(prenoms)}", f"{' '.join(prenoms)} {nom.upper()}",
                           f"{prenoms[0][0]}. {nom}", f"{prenoms[0][0]}. {nom.upper()}"}
        elif not prenoms:
            formes |= {" ".join(w.capitalize() for w in mots)}
    if categorie in ("TELEPHONE", "IBAN", "NIR", "SIRET", "SIREN", "CARTE_BANCAIRE"):
        brut = re.sub(r"[\s.-]", "", v)
        formes |= {brut, " ".join(brut[i:i + 2] for i in range(0, len(brut), 2)), ".".join(brut[i:i + 2] for i in range(0, len(brut), 2))}
        if categorie == "IBAN":
            formes |= {" ".join(brut[i:i + 4] for i in range(0, len(brut), 4))}
    return sorted(f for f in formes if f)


# Formes de noms : sensibles à la casse (« Blanc » est un nom, « blanc » un mot). Identifiants : insensibles.
NOMMES = ("PERSONNE", "ORGANISATION", "ADRESSE", "LIEU_NAISSANCE", "NOM")
NON_PROPAGES = ("LIEU_NAISSANCE",)


class Table:
    """Correspondance valeur réelle -> jeton, chiffrée dans le coffre. Une entité a un jeton, sa valeur d'origine et ses formes."""

    def __init__(self, racine: Path, memoire: bool = False):
        self.racine, self.memoire = racine, memoire
        self.entites: list[dict] = []
        self.fichier = None if memoire else coffre(racine) / "table.chiffree"
        if self.fichier and self.fichier.is_file():
            self.entites = json.loads(_fernet(racine).decrypt(self.fichier.read_bytes()).decode("utf-8"))["entites"]

    def sauver(self) -> None:
        if self.memoire:
            return
        donnees = json.dumps({"version": 1, "entites": self.entites}, ensure_ascii=False).encode("utf-8")
        self.fichier.write_bytes(_fernet(self.racine).encrypt(donnees))

    def trouver(self, valeur: str) -> dict | None:
        cle = plier(valeur)
        return next((e for e in self.entites if cle in {plier(f) for f in e["formes"]}), None)

    def jeton(self, valeur: str, categorie: str, role: str = "", source: str = "") -> str:
        e = self.trouver(valeur)
        if e:
            return e["jeton"]
        n = 1 + sum(1 for e in self.entites if e["categorie"] == categorie)
        jeton = f"[{categorie}_{n}]"
        self.entites.append({"jeton": jeton, "categorie": categorie, "valeur": re.sub(r"\s+", " ", valeur).strip(), "role": role,
                             "formes": variantes(valeur, categorie), "source": source,
                             "ajoute_le": datetime.now().isoformat(timespec="seconds")})
        return jeton

    def formes(self) -> list[tuple[str, str, str]]:
        """(forme, jeton, catégorie), les plus longues d'abord pour que « Marie Durand » passe avant « Durand ». Un lieu de naissance
        ne se propage pas : remplacé dans son contexte, il resterait sinon effacé de « tribunal administratif de Lyon »."""
        out = [(f, e["jeton"], e["categorie"]) for e in self.entites for f in e["formes"]
               if len(f.strip()) >= 2 and e["categorie"] not in NON_PROPAGES]
        return sorted(out, key=lambda x: -len(x[0]))


def _occurrences(forme: str, categorie: str, texte: str):
    drapeaux = 0 if categorie in NOMMES else re.I
    return re.finditer(rf"(?<![\w]){re.escape(forme)}(?![\w])", texte, drapeaux)


# ---------------------------------------------------------------- pseudonymisation d'un texte

def detecter(texte: str, table: Table | None = None, avec_modele: bool = True) -> list[Trouvaille]:
    trouvees = (identifiants(texte) + personnes(texte) + organisations(texte) + adresses(texte) + naissances(texte)
                + (modele(texte) if avec_modele else []))
    if table:
        for forme, jeton, cat in table.formes():
            for m in _occurrences(forme, cat, texte):
                trouvees.append(Trouvaille(m.start(), m.end(), cat, m.group(0), "dictionnaire"))
    return trouvees


def _fusionner(trouvees: list[Trouvaille]) -> list[Trouvaille]:
    """Spans sans chevauchement : le plus long l'emporte, le dictionnaire puis les identifiants à longueur égale."""
    rang = {"dictionnaire": 0, "identifiant": 1}
    choisies: list[Trouvaille] = []
    for t in sorted(trouvees, key=lambda t: (-(t.fin - t.debut), rang.get(t.couche, 2), t.debut)):
        if all(t.fin <= c.debut or t.debut >= c.fin for c in choisies):
            choisies.append(t)
    return sorted(choisies, key=lambda t: t.debut)


def pseudonymiser(texte: str, table: Table, source: str = "", avec_modele: bool = True) -> tuple[str, list[Trouvaille]]:
    """Deux passes : la première trouve et enregistre, la seconde remplace chaque forme connue partout (propagation)."""
    for t in _fusionner(detecter(texte, table, avec_modele)):
        if t.couche != "dictionnaire":
            table.jeton(t.texte, t.categorie, source=source or t.couche)
    finales = _fusionner(detecter(texte, table, avec_modele=False))
    morceaux, pos = [], 0
    for t in finales:
        morceaux += [texte[pos:t.debut], table.jeton(t.texte, t.categorie, source=source)]
        pos = t.fin
    morceaux.append(texte[pos:])
    return "".join(morceaux), finales


def reidentifier_texte(texte: str, table: Table) -> str:
    valeurs = {e["jeton"]: e.get("valeur") or max(e["formes"], key=len) for e in table.entites}
    return re.sub(r"\[[A-Z_]+_\d+\]", lambda m: valeurs.get(m.group(0), m.group(0)), texte)


def fuites(texte: str, table: Table) -> list[str]:
    """Jetons dont une forme réelle de quatre caractères au moins apparaît dans le texte."""
    out = []
    for forme, jeton, cat in table.formes():
        if len(forme) >= 4 and jeton not in out and next(_occurrences(forme, cat, texte), None):
            out.append(jeton)
    return out


# ---------------------------------------------------------------- extraction du texte des pièces

def texte_de(fichier: Path) -> str:
    suf = fichier.suffix.lower()
    if suf in TEXTES:
        t = fichier.read_text(encoding="utf-8", errors="replace")
        return re.sub(r"<[^>]+>", " ", t) if suf in (".html", ".htm", ".xml") else t
    if suf == ".pdf":
        try:
            import fitz  # type: ignore
            with fitz.open(fichier) as doc:
                return "\n".join(p.get_text() for p in doc)
        except ImportError:
            from pypdf import PdfReader  # type: ignore
            return "\n".join(p.extract_text() or "" for p in PdfReader(str(fichier)).pages)
    if suf == ".docx":
        with zipfile.ZipFile(fichier) as z:
            xml = z.read("word/document.xml").decode("utf-8", errors="replace")
        return re.sub(r"<[^>]+>", "", re.sub(r"</w:p>", "\n", xml))
    raise SystemExit(f"Format non pris en charge : {fichier.name} (texte, PDF à couche texte, DOCX). Un scan s'océrise d'abord.")


# ---------------------------------------------------------------- commandes

def _racine_ou_sortie() -> Path:
    r = racine_affaire(Path.cwd())
    if r is None:
        raise SystemExit("Pas de dossier d'affaire ici (etat/affaire.json introuvable).")
    return r


def _pseudonymiser_fichier(p: Path, table: Table) -> None:
    p.write_text(pseudonymiser(p.read_text(encoding="utf-8", errors="replace"), table, source=p.name, avec_modele=False)[0], encoding="utf-8")


def cmd_init(a) -> None:
    r = _racine_ou_sortie()
    if actif(r):
        raise SystemExit("Mode pseudonymisé déjà actif.")
    if a.coffre:
        os.environ[COFFRE_ENV] = str(Path(a.coffre).resolve())
    c = coffre(r)
    if c.resolve().is_relative_to(r.resolve()):
        raise SystemExit("Le coffre ne peut pas être dans le dossier d'affaire : l'agent pourrait l'atteindre.")
    c.mkdir(parents=True, exist_ok=True)
    from cryptography.fernet import Fernet  # type: ignore
    if not (c / "cle").is_file():
        (c / "cle").write_bytes(Fernet.generate_key())
    (r / ETAT).mkdir(exist_ok=True)
    (r / ETAT / "actif.json").write_text(json.dumps({"coffre": str(c), "depuis": datetime.now().isoformat(timespec="seconds")}), encoding="utf-8")
    table = Table(r)
    aff = json.loads((r / MARQUEUR_AFFAIRE).read_text(encoding="utf-8"))
    for champ, role in (("client", "client"), ("adversaires", "adversaire")):
        v = aff.get(champ)
        if isinstance(v, str) and v and not v.startswith("["):
            aff[champ] = table.jeton(v, "PERSONNE", role=role, source="affaire.json")
        elif isinstance(v, list):
            aff[champ] = [table.jeton(x, "PERSONNE", role=role, source="affaire.json") if x and not str(x).startswith("[") else x for x in v]
    (r / MARQUEUR_AFFAIRE).write_text(json.dumps(aff, ensure_ascii=False, indent=2), encoding="utf-8")
    # L'existant (journal, états, notes) est pseudonymisé à son tour ; les originaux déjà rangés sortent vers le coffre.
    for p in r.rglob("*"):
        if p.is_file() and p.suffix.lower() in TEXTES and ETAT not in p.parts and "originaux" not in p.parts:
            _pseudonymiser_fichier(p, table)
    orig = r / "pieces" / "originaux"
    if orig.is_dir() and any(orig.iterdir()):
        (c / "originaux").mkdir(exist_ok=True)
        for p in orig.iterdir():
            p.replace(c / "originaux" / p.name)
    (r / COPIES).mkdir(parents=True, exist_ok=True)
    table.sauver()
    print(f"Mode pseudonymisé actif. Coffre : {c} (hors du dossier ; à sauvegarder à part, sa clé ne se reconstitue pas).")


def cmd_ajouter(a) -> None:
    r = _racine_ou_sortie()
    table = Table(r)
    j = table.jeton(a.valeur, a.categorie, role=a.role or "", source="avocat")
    table.sauver()
    print(f"{j} enregistré ({len(table.entites)} entités).")


def cmd_importer(a) -> None:
    r = _racine_ou_sortie()
    if not actif(r):
        raise SystemExit("Mode pseudonymisé inactif : lancer d'abord « pseudonymisation.py init ».")
    table = Table(r)
    c = coffre(r)
    rapport = [f"# Rapport de pseudonymisation, {datetime.now().isoformat(timespec='minutes')}", "",
               "À relire avant « valider » : chaque ligne donne la valeur réelle trouvée et son jeton. Une donnée oubliée s'ajoute par "
               "« ajouter », puis on relance « importer ». Ce rapport reste dans le coffre ; l'agent ne le lit jamais.", ""]
    for f in a.fichiers:
        src = Path(f).resolve()
        if src.is_relative_to(r.resolve()):
            raise SystemExit(f"{src.name} est dans le dossier de travail : en mode pseudonymisé, un original reste hors du dossier.")
        pseudo, trouvees = pseudonymiser(texte_de(src), table, source=src.name)
        nom = re.sub(r"[^\w.\[\]-]", "_", pseudonymiser(src.stem, table, avec_modele=False)[0]) + ".txt"
        (r / COPIES / nom).write_text(pseudo, encoding="utf-8")
        rapport += [f"## {src.name} -> {COPIES.as_posix()}/{nom}", ""]
        vus = set()
        for t in trouvees:
            ligne = f"- {t.categorie} « {t.texte} » -> {table.jeton(t.texte, t.categorie)} ({t.couche})"
            if ligne not in vus:
                vus.add(ligne)
                rapport.append(ligne)
        reste = suspects(pseudo, {plier(x) for e in table.entites for x in e["formes"]})
        if reste:
            rapport += ["", "Mots à majuscule non reconnus, à vérifier : " + ", ".join(reste)]
        rapport.append("")
    table.sauver()
    (c / "rapport.md").write_text("\n".join(rapport), encoding="utf-8")
    (r / ETAT / "valide.json").unlink(missing_ok=True)
    print(f"{len(a.fichiers)} pièce(s) pseudonymisée(s) dans {COPIES.as_posix()} ; rapport à relire : {c / 'rapport.md'}, puis « valider ».")


def empreintes(r: Path) -> dict[str, str]:
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((r / COPIES).glob("*")) if p.is_file()}


def cmd_valider(a) -> None:
    r = _racine_ou_sortie()
    e = empreintes(r)
    (r / ETAT / "valide.json").write_text(json.dumps({"valide_le": datetime.now().isoformat(timespec="seconds"), "copies": e},
                                                     ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Relecture attestée pour {len(e)} copie(s). L'agent peut les lire.")


def cmd_reidentifier(a) -> None:
    r = _racine_ou_sortie()
    table = Table(r)
    src = Path(a.fichier).resolve()
    sortie = Path(a.sortie).resolve() if a.sortie else coffre(r) / "sorties"
    if sortie.is_relative_to(r.resolve()):
        raise SystemExit("La version ré-identifiée ne s'écrit pas dans le dossier de travail.")
    sortie.mkdir(parents=True, exist_ok=True)
    (sortie / src.name).write_text(reidentifier_texte(src.read_text(encoding="utf-8"), table), encoding="utf-8")
    print(f"Version ré-identifiée : {sortie / src.name}")


def cmd_verifier(a) -> None:
    r = _racine_ou_sortie()
    table = Table(r)
    trouve = 0
    for p in r.rglob("*"):
        if p.is_file() and p.suffix.lower() in TEXTES and ETAT not in p.parts:
            j = fuites(p.read_text(encoding="utf-8", errors="replace"), table)
            if j:
                trouve += 1
                print(f"FUITE {p.relative_to(r).as_posix()} : formes réelles de {', '.join(j)}")
    print("Aucune donnée réelle dans le dossier de travail." if not trouve else f"{trouve} fichier(s) à corriger.")
    sys.exit(1 if trouve else 0)


# ---------------------------------------------------------------- hooks Claude Code

def _sortie(obj: dict) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False))
    sys.exit(0)


def _refuser(raison: str) -> None:
    _sortie({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": raison}})


def cmd_hook(a) -> None:
    sys.stdin.reconfigure(encoding="utf-8")
    try:
        ev = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)
    ti = ev.get("tool_input") or {}
    cwd = Path(ev.get("cwd") or os.getcwd())
    depart = next((ti[k] for k in ("file_path", "notebook_path", "path") if ti.get(k)), None)
    r = (racine_affaire(Path(depart)) if depart else None) or racine_affaire(cwd)
    if r is None or not actif(r):
        sys.exit(0)
    nom = ev.get("hook_event_name")
    if nom == "SessionStart":
        _sortie({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": (
            "Dossier pseudonymisé. Les pièces se lisent dans pieces/pseudonymisees/ ; chaque jeton entre crochets ([PERSONNE_2], "
            "[ADRESSE_1]...) désigne une personne ou une donnée réelle que tu ne connais pas et ne cherches pas à connaître. Écrire avec "
            "les jetons, tels quels, y compris dans les actes ; ne jamais deviner une identité ni demander la valeur réelle. Les originaux "
            "et la table sont hors du dossier ; l'avocat ré-identifie lui-même les actes définitifs.")}})
    if nom == "PreToolUse":
        cibles = " ".join(str(ti.get(k, "")) for k in ("file_path", "notebook_path", "path", "pattern", "glob", "command"))
        c = str(coffre(r)).replace("\\", "/").lower()
        if PROTEGES.search(" " + cibles.replace("\\", "/") + " ") or c in cibles.replace("\\", "/").lower():
            _refuser("Dossier pseudonymisé : les originaux et le coffre sont fermés à l'agent. Lire la copie dans pieces/pseudonymisees/.")
        if ev.get("tool_name") in ("Read", "NotebookRead") and COPIES.as_posix() in str(ti.get("file_path", "")).replace("\\", "/"):
            f = r / ETAT / "valide.json"
            valide = json.loads(f.read_text(encoding="utf-8")) if f.is_file() else {}
            p = Path(ti["file_path"])
            if not p.is_file() or valide.get("copies", {}).get(p.name) != hashlib.sha256(p.read_bytes()).hexdigest():
                _refuser("Copie pseudonymisée non validée : l'avocat relit le rapport puis lance « pseudonymisation.py valider ».")
        sys.exit(0)
    if nom == "UserPromptSubmit":
        j = fuites(str(ev.get("prompt", "")), Table(r))
        if j:
            _sortie({"decision": "block", "reason": "Le message contient une donnée réelle du dossier pseudonymisé. Écrire plutôt "
                                                   + ", ".join(j) + " ; le message n'a pas été transmis."})
        sys.exit(0)
    if nom == "PostToolUse" and ev.get("tool_name") in ("Write", "Edit", "MultiEdit"):
        p = Path(str(ti.get("file_path", "")))
        if p.is_file() and p.suffix.lower() in TEXTES:
            j = fuites(p.read_text(encoding="utf-8", errors="replace"), Table(r))
            if j:
                _sortie({"decision": "block", "reason": f"{p.name} contient la forme réelle d'une donnée pseudonymisée ({', '.join(j)}) : "
                                                        "la remplacer par son jeton."})
    sys.exit(0)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("init").add_argument("--coffre")
    j = s.add_parser("ajouter")
    j.add_argument("valeur")
    j.add_argument("--categorie", default="PERSONNE")
    j.add_argument("--role")
    s.add_parser("importer").add_argument("fichiers", nargs="+")
    s.add_parser("valider")
    r = s.add_parser("reidentifier")
    r.add_argument("fichier")
    r.add_argument("--sortie")
    s.add_parser("verifier")
    s.add_parser("hook")
    a = p.parse_args()
    {"init": cmd_init, "ajouter": cmd_ajouter, "importer": cmd_importer, "valider": cmd_valider, "reidentifier": cmd_reidentifier,
     "verifier": cmd_verifier, "hook": cmd_hook}[a.cmd](a)


if __name__ == "__main__":
    main()
