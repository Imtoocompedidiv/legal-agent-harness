"""Lecture mécanique d'une écriture : défauts de structure constatés dans des écritures triées.

Chaque règle provient d'une cause d'échec documentée (docs/AUTOPSIE.md). Le linter mesure ;
il ne juge pas la portée juridique. Les longueurs sont rapportées à titre d'information,
jamais comme seuil.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field, asdict

# Formules qui présentent le moyen comme une hypothèse de travail au lieu de l'affirmer.
FORMULES_ATTENUEES = [
    r"\ble requérant soutient\b", r"\bla requérante soutient\b", r"\bselon le requérant\b",
    r"\bselon la requérante\b", r"\bsi telle est (sa|la) portée\b", r"\bil pourrait être soutenu\b",
    r"\bil pourrait être considéré\b", r"\bpourrait être regardée? comme\b", r"\bil n'est pas exclu\b",
    r"\bà toutes fins utiles\b", r"\bsemble(rait)? pouvoir\b", r"\bil nous semble\b",
    r"\bsous toutes réserves\b", r"\ble cas échéant, et sous réserve\b",
]
FORMULES_CONCESSION = [
    r"je reconnais", r"j.admets", r"il est vrai que", r"certes", r"je ne conteste pas",
    r"je ne remets pas en cause", r"ne remet pas en cause", r"force est de reconna[iî]tre", r"je regrette",
    r"malheureusement", r"je me permets", r"respectueusement", r"humblement", r"bienveillance",
    r"indulgence", r"j.ai conscience", r"n.exige pas une r[ée]ponse favorable", r"je sais ce que",
]
SUBSIDIAIRE = r"\b(à titre )?(infiniment |plus )?subsidiaire(ment)?\b"
BRANCHES_CONDITIONNELLES = [
    r"\bsi (le|la|l'|les) (refus|décision|suspension|juge|ordonnance|accès|mesure)[^.]{0,140}?\b(est|sont|était|devait|implique|nécessite)\b",
    r"\bdans l'hypothèse où\b", r"\bà défaut\b", r"\ben tant que de besoin\b", r"\bdans la mesure (nécessaire|où)\b",
]
TITRES_CONCLUSIONS = re.compile(
    r"^(#+\s*)?(par ces motifs|conclusions|demandes?|dispositif|il est demandé|m\. .{0,40} demande|.{0,60}demande au juge)",
    re.I | re.M,
)

RE_DECISIONS = [
    ("caa", re.compile(r"\b(\d{2}[A-Z]{2}\d{5})\b")),
    ("cass", re.compile(r"\b(\d{2}-\d{2}\.\d{3})\b")),
    ("cedh", re.compile(r"n[°o]s?\s?(\d{3,6}/\d{2})\b")),
    ("ce_ta", re.compile(r"n°\s?(\d{5,7})\b(?!/)")),
]
RE_ARTICLE = re.compile(r"\barticles?\s+((?:[LRDA]\.?\s?\*?)\d+(?:[-–]\d+)*)", re.I)
RE_PIECE = re.compile(r"\bpièces?\s+(?:n[°o]s?\s*)?((?:\d+(?:\s*(?:,|et|à|-)\s*)?)+)", re.I)


@dataclass
class Constat:
    code: str
    gravite: str  # BLOQUANT, ALERTE, INFO
    message: str
    extrait: str = ""
    ligne: int = 0


@dataclass
class Rapport:
    constats: list = field(default_factory=list)
    mesures: dict = field(default_factory=dict)
    decisions_citees: list = field(default_factory=list)
    articles_cites: list = field(default_factory=list)
    pieces_citees: list = field(default_factory=list)

    def ajouter(self, *a, **k):
        self.constats.append(Constat(*a, **k))

    def as_dict(self):
        d = asdict(self)
        return d


def _ligne(texte: str, pos: int) -> int:
    return texte.count("\n", 0, pos) + 1


def _extrait(texte: str, pos: int, n: int = 90) -> str:
    debut = max(0, pos - 30)
    return texte[debut:debut + n].replace("\n", " ").strip()


def _hors_citations(texte: str) -> str:
    """Masque les passages entre guillemets français ou droits, et les blocs cités."""
    t = re.sub(r"«[^»]{0,2000}»", lambda m: " " * len(m.group(0)), texte)
    t = re.sub(r"\"[^\"\n]{0,600}\"", lambda m: " " * len(m.group(0)), t)
    t = "\n".join(" " * len(l) if l.lstrip().startswith(">") else l for l in t.split("\n"))
    return t


def _nombres_pieces(groupe: str) -> list[int]:
    nombres = []
    for a, b in re.findall(r"(\d+)\s*(?:à|-)\s*(\d+)", groupe):
        a, b = int(a), int(b)
        if 0 < b - a < 200:
            nombres.extend(range(a, b + 1))
    nombres.extend(int(n) for n in re.findall(r"\d+", groupe))
    return sorted(set(nombres))


def section_conclusions(texte: str) -> tuple[int, str]:
    """Début du dispositif : « Par ces motifs » s'il existe, sinon le dernier titre court de demandes."""
    positions, pcm = [], None
    pos = 0
    for ligne in texte.split("\n"):
        nette = ligne.strip()
        if nette and len(nette) <= 90 and TITRES_CONCLUSIONS.match(nette):
            positions.append(pos)
            if pcm is None and re.match(r"(#+\s*)?par ces motifs", nette, re.I):
                pcm = pos
        pos += len(ligne) + 1
    if not positions:
        return -1, ""
    debut = pcm if pcm is not None else positions[-1]
    return debut, texte[debut:]


def analyser(texte: str, *, refere: bool = False, texte_client: bool = False,
             ponctuation_interdite: list[str] | None = None,
             numeros_propres: set[str] | None = None) -> Rapport:
    r = Rapport()
    corps_lignes = _hors_citations(texte)
    # Les textes extraits de PDF coupent les phrases en fin de ligne : on recherche sur un texte
    # aplati de même longueur, pour que les positions restent celles de l'original.
    corps = corps_lignes.replace("\n", " ")
    mots = len(re.findall(r"\w+", texte))
    r.mesures = {"mots": mots, "pages_estimees": round(mots / 450, 1)}

    for motif in FORMULES_ATTENUEES:
        for m in re.finditer(motif, corps, re.I):
            r.ajouter("ATTENUATION", "BLOQUANT" if refere else "ALERTE",
                      "Le moyen est présenté comme une hypothèse ; il doit être affirmé (règle, fait prouvé, conséquence).",
                      _extrait(texte, m.start()), _ligne(texte, m.start()))

    for motif in FORMULES_CONCESSION:
        for m in re.finditer(motif, corps, re.I):
            r.ajouter("CONCESSION", "BLOQUANT" if texte_client or refere else "ALERTE",
                      "Formule de concession ou de déférence : l'écrit ne plaide jamais contre son auteur ; neutraliser le fait adverse par la question posée.",
                      _extrait(texte, m.start()), _ligne(texte, m.start()))

    subs = list(re.finditer(SUBSIDIAIRE, corps, re.I))
    r.mesures["subsidiaires"] = len(subs)
    if refere and len(subs) > 1:
        lignes = ", ".join(str(_ligne(texte, m.start())) for m in subs)
        r.ajouter("SUBSIDIAIRES", "BLOQUANT",
                  f"{len(subs)} occurrences de subsidiaire dans un référé (lignes {lignes}) : une cascade de subsidiaires dit au juge du tri que le requérant hésite.",
                  _extrait(texte, subs[0].start()), _ligne(texte, subs[0].start()))

    debut_concl, _ = section_conclusions(corps_lignes)
    concl = corps[debut_concl:] if debut_concl >= 0 else ""
    r.mesures["section_conclusions"] = debut_concl >= 0
    if debut_concl < 0:
        r.ajouter("CONCLUSIONS_ABSENTES", "ALERTE", "Aucune section de conclusions repérée (« Par ces motifs », « demande au juge »).")
    else:
        dispositif = re.split(r"\n\s*(?:#+\s*)?(?:pièces jointes|bordereau|inventaire|liste des pièces)", corps_lignes[debut_concl:], maxsplit=1, flags=re.I)[0]
        chefs = re.findall(r"^\s*(\d+)(?:\s?bis)?\s?[°º)\.]", dispositif, re.M)
        r.mesures["chefs_de_conclusions"] = len(set(chefs))
        for motif in BRANCHES_CONDITIONNELLES:
            for m in re.finditer(motif, concl, re.I):
                pos = debut_concl + m.start()
                r.ajouter("BRANCHE_CONDITIONNELLE", "BLOQUANT" if refere else "ALERTE",
                          "Conclusion conditionnelle : choisir la lecture juste de l'acte et la défendre, sans dispositif à branches.",
                          _extrait(texte, pos), _ligne(texte, pos))

    if refere and re.search(r"L\.\s?521-1\b", corps) and re.search(r"L\.\s?521-2\b", corps):
        r.ajouter("PROCEDURES_MELEES", "ALERTE",
                  "L. 521-1 et L. 521-2 cités ensemble : une requête par procédure ; vérifier que l'un n'est pas un fondement.")

    if "—" in texte:
        pos = texte.index("—")
        r.ajouter("TIRET_CADRATIN", "ALERTE", "Tiret cadratin présent (charte de rédaction).", _extrait(texte, pos), _ligne(texte, pos))

    if texte_client and ponctuation_interdite:
        for signe in ponctuation_interdite:
            occ = [m.start() for m in re.finditer(re.escape(signe), corps)]
            occ = [p for p in occ if not re.search(r"https?$", corps[max(0, p - 5):p])
                   and not re.match(r"\d", corps[p + 1:p + 2] or " ")]
            if occ:
                r.ajouter("PONCTUATION_CLIENT", "ALERTE",
                          f"« {signe} » apparaît {len(occ)} fois hors citations dans un texte au nom du client.",
                          _extrait(texte, occ[0]), _ligne(texte, occ[0]))

    propres = {n.replace(" ", "") for n in (numeros_propres or set())}
    vus = set()
    for genre, motif in RE_DECISIONS:
        for m in motif.finditer(texte):
            num = m.group(1)
            if num in propres or num in vus:
                continue
            vus.add(num)
            r.decisions_citees.append({"numero": num, "genre": genre, "ligne": _ligne(texte, m.start())})
    arts = sorted({re.sub(r"\s+", " ", a.replace("–", "-")).strip() for a in RE_ARTICLE.findall(texte)})
    r.articles_cites = arts
    pieces = set()
    for m in RE_PIECE.finditer(texte):
        pieces.update(_nombres_pieces(m.group(1)))
    r.pieces_citees = sorted(pieces)
    r.mesures.update({"decisions_citees": len(r.decisions_citees), "articles_cites": len(arts), "pieces_citees": len(pieces)})
    return r


def premiere_page(texte: str, caracteres: int = 2600) -> str:
    """Ce que voit un lecteur pressé : l'en-tête et les premiers paragraphes, environ une page."""
    return texte[:caracteres]


def recouvrement(a: str, b: str) -> float:
    """Part des mots significatifs de a présents dans b."""
    vide = {"de", "la", "le", "les", "des", "du", "en", "et", "à", "a", "un", "une", "que", "qui", "sur",
            "par", "pour", "au", "aux", "l", "d", "il", "elle", "ce", "cette", "son", "sa", "ses", "est", "sans"}
    ma = {w for w in re.findall(r"\w+", a.lower()) if len(w) > 2 and w not in vide}
    mb = set(re.findall(r"\w+", b.lower()))
    return 1.0 if not ma else len(ma & mb) / len(ma)


if __name__ == "__main__":
    import json
    chemin = sys.argv[1]
    refere = "--refere" in sys.argv
    with open(chemin, encoding="utf-8") as f:
        rap = analyser(f.read(), refere=refere)
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(rap.as_dict(), ensure_ascii=False, indent=2))
