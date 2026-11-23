"""Analyse documentaire du dossier d'affaire : inventaire, extraction, rendu, repérages, vérification des fiches
d'analyse et de la matrice des preuves, contrôle des faits décisifs.

Tout reste sur le poste : aucun appel réseau, aucun service distant. PyMuPDF (import fitz) lit les PDF et les
images ; Pillow, s'il est présent, lit l'EXIF des photographies ; l'OCR n'est tenté que si Tesseract est installé.
Le module s'importe sans PyMuPDF : le contrôle et la validation n'en ont pas besoin.

Commandes, lancées depuis le dossier d'affaire :
  inventaire [--cote C]... [--refaire]
      empreinte, format, pages, métadonnées, champs de formulaire, signatures, versions successives,
      texte page par page et repérages (dates, montants, envois recommandés, auteurs, références,
      documents mentionnés) ; écrit pieces/inventaire.json et pieces/texte/<pièce>.extraction.txt
  rendre [--cote C]... [--pages 1,3-5 | --a-examiner] [--dpi N]
      rend les pages en PNG dans pieces/rendus/<pièce>/ pour l'examen visuel (formulaires, signatures,
      cachets, pages numérisées)
  fiche <cote>
      squelette de la fiche d'analyse, prérempli des données mécaniques (sortie standard, rien n'est écrit)
  verifier [--cote C]...
      valide les fiches pieces/analyses/<cote>.json et preuves/matrice.json ; cherche chaque extrait sur sa page
  chronologie
      dates tirées des fiches -> chronologie/depuis_pieces.json, avec les écarts par rapport à la chronologie
  manques
      pièces citées hors bordereau, fichiers hors bordereau, pièces non analysées, faits sans pièce, dates non
      retrouvées dans leurs pièces, documents mentionnés absents, preuves à obtenir ; écrit pieces/manques.json
  controle <ecriture.md>
      fait décisif sans extrait littéral d'une pièce analysée : bloquant ; pièce citée sans fiche : alerte
"""
from __future__ import annotations

import argparse
import difflib
import email
import email.policy
import hashlib
import html
import json
import re
import sys
import unicodedata
import zipfile
from collections import Counter
from datetime import date, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
import lib_affaire as L  # noqa: E402

VERSION_OUTIL = "pieces/3"
SCHEMA_FICHE = "analyse_piece/1"
SCHEMAS_DIR = ICI.parent / "references" / "schemas"
INVENTAIRE = "pieces/inventaire.json"
FORMATS_PAGINES = {"pdf", "png", "jpeg", "tiff", "gif", "bmp", "webp"}
FORMATS_IMAGE = FORMATS_PAGINES - {"pdf"}
FORCES = ("prouve", "corrobore", "allegue", "conteste", "contredit")


# ---------------------------------------------------------------------------------------------------------------
# Cotes, chemins, bordereau

def norm_cote(c) -> str:
    s = str(c).strip()
    return str(int(s)) if s.isdigit() else s


def prefixe(cote) -> str:
    c = norm_cote(cote)
    return f"{int(c):03d}" if c.isdigit() else c


def nom_base(cote, fichier) -> str:
    """Nom des fichiers dérivés d'une pièce : le nom de l'original, déjà préfixé par sa cote par affaire.py."""
    stem = Path(str(fichier)).stem
    pre = prefixe(cote) if cote is not None else ""
    if not pre or stem == pre or stem.startswith(pre + "_"):
        return stem
    return f"{pre}_{stem}"


def lire_bordereau(racine: Path) -> dict[str, dict]:
    return {norm_cote(p.get("cote")): p for p in (L.lire_json(racine / "pieces/bordereau.json", {}) or {}).get("pieces", [])}


def chemin_fiche(racine: Path, cote) -> Path:
    return racine / "pieces" / "analyses" / f"{norm_cote(cote)}.json"


def chemin_rendu(racine: Path, cote, fichier, page: int) -> Path:
    return racine / "pieces" / "rendus" / nom_base(cote, fichier) / f"p{page:03d}.png"


# ---------------------------------------------------------------------------------------------------------------
# Format réel du fichier (signature binaire, pas l'extension)

EXTENSIONS = {"pdf": {".pdf"}, "png": {".png"}, "jpeg": {".jpg", ".jpeg", ".jfif"}, "tiff": {".tif", ".tiff"},
              "gif": {".gif"}, "bmp": {".bmp"}, "webp": {".webp"}, "docx": {".docx", ".docm"}, "odt": {".odt"},
              "eml": {".eml", ".txt", ".mht"}, "texte": {".txt", ".md", ".csv", ".json", ".xml"},
              "html": {".html", ".htm"}, "ole": {".doc", ".msg", ".xls", ".ppt"}, "zip": {".zip"}}


def detecter_format(chemin: Path) -> str:
    with open(chemin, "rb") as f:
        tete = f.read(4096)
    if b"%PDF-" in tete[:1024]:
        return "pdf"
    if tete.startswith(b"\x89PNG"):
        return "png"
    if tete[:3] == b"\xff\xd8\xff":
        return "jpeg"
    if tete[:4] in (b"II*\x00", b"MM\x00*"):
        return "tiff"
    if tete[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    if tete[:2] == b"BM":
        return "bmp"
    if tete[:4] == b"RIFF" and tete[8:12] == b"WEBP":
        return "webp"
    if tete[:4] == b"PK\x03\x04":
        try:
            with zipfile.ZipFile(chemin) as z:
                noms = set(z.namelist())
                if "word/document.xml" in noms:
                    return "docx"
                if "mimetype" in noms and b"opendocument.text" in z.read("mimetype"):
                    return "odt"
        except (zipfile.BadZipFile, OSError):
            pass
        return "zip"
    if tete[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
        return "ole"
    texte = tete.decode("utf-8", "ignore")
    if re.search(r"^(From|Date):", texte, re.M) and re.search(r"^(Received|Message-ID|Subject|To|MIME-Version):", texte, re.M | re.I):
        return "eml"
    if re.search(r"<html|<!doctype html", texte, re.I):
        return "html"
    if tete and b"\x00" not in tete:
        return "texte"
    return "inconnu"


# ---------------------------------------------------------------------------------------------------------------
# Normalisation et recherche des citations

_TRADUCTION = str.maketrans({"\u2019": "'", "\u2018": "'", "\u201b": "'", "\u02bc": "'", "\u00b4": "'", "`": "'",
                             "\u201c": '"', "\u201d": '"', "\u201e": '"', "\u00ab": '"', "\u00bb": '"',
                             "\u2013": "-", "\u2014": "-", "\u2011": "-", "\u2012": "-", "\u2212": "-",
                             "\u00a0": " ", "\u202f": " ", "\u2009": " ", "\u00ad": ""})
RE_ELLIPSE = re.compile(r"\[\s*(?:\.\.\.|\u2026)\s*\]|\(\s*(?:\.\.\.|\u2026)\s*\)|\u2026|\.\.\.")


def normaliser(t: str, joindre_cesures: bool = True) -> str:
    t = unicodedata.normalize("NFKC", t or "").translate(_TRADUCTION)
    t = re.sub(r"(\w)-[ \t]*\n[ \t]*(\w)", r"\1\2" if joindre_cesures else r"\1-\2", t)
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r'\s*"\s*', '"', t)
    return t.strip().lower()


def _approche(segment: str, texte: str, seuil: float = 0.9) -> bool:
    mots, n = texte.split(" "), len(segment.split(" "))
    for taille in sorted({max(1, n - 1), n, n + 1}):
        for i in range(max(1, len(mots) - taille + 1)):
            m = difflib.SequenceMatcher(None, segment, " ".join(mots[i:i + taille]))
            if m.quick_ratio() >= seuil and m.ratio() >= seuil:
                return True
    return False


def trouver(citation: str, texte: str, approx: bool = False) -> str | None:
    """« exact » si la citation (segments séparés par [...]) se lit dans le texte, dans l'ordre ; « approche » en
    tolérance OCR ; None sinon. La casse, les espaces, les guillemets et les césures ne comptent pas."""
    segments = [s for s in (normaliser(x) for x in RE_ELLIPSE.split(citation or "")) if s]
    if not segments:
        return None
    for variante in (normaliser(texte, True), normaliser(texte, False)):
        pos, ok = 0, True
        for s in segments:
            i = variante.find(s, pos)
            if i < 0:
                ok = False
                break
            pos = i + len(s)
        if ok:
            return "exact"
    if approx and all(_approche(s, normaliser(texte)) for s in segments):
        return "approche"
    return None


# ---------------------------------------------------------------------------------------------------------------
# Fichier d'extraction : pieces/texte/<pièce>.extraction.txt, découpé par page

ENTETE = ("# Extraction automatique par pieces.py. Elle ne vaut ni lecture visuelle, ni vérification d'une signature, "
          "d'un cachet, d'une mention manuscrite ou d'une case cochée.")
RE_PAGE = re.compile(r"^=== page (\d+) / (\d+) \[([^\]]*)\] ===$", re.M)


def chemin_extraction(racine: Path, cote, fichier) -> Path:
    return racine / "pieces" / "texte" / f"{nom_base(cote, fichier)}.extraction.txt"


def ecrire_extraction(chemin: Path, cote, fichier: str, sha: str, pages: list[dict]) -> None:
    lignes = [ENTETE, f"# cote: {cote}", f"# fichier: {fichier}", f"# sha256: {sha}", f"# pages: {len(pages)}",
              f"# extrait_le: {L.horodatage()}", ""]
    for pg in pages:
        lignes.append(f"=== page {pg['n']} / {len(pages)} [{pg['mode']}] ===")
        # Une ligne du document qui imiterait un séparateur de page est décalée d'une espace.
        texte = (pg.get("texte") or "").replace("\r\n", "\n").replace("\r", "\n").rstrip()
        lignes.extend((" " + l) if RE_PAGE.match(l) else l for l in texte.split("\n"))
        lignes.append("")
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text("\n".join(lignes) + "\n", encoding="utf-8", newline="\n")


def lire_extraction(chemin: Path) -> tuple[dict, dict[int, tuple[str, str]]] | None:
    try:
        brut = chemin.read_text(encoding="utf-8")
    except OSError:
        return None
    meta = dict(re.findall(r"^# (\w+): (.*)$", brut.split("\n=== page", 1)[0], re.M))
    pages = {}
    marques = list(RE_PAGE.finditer(brut))
    for i, m in enumerate(marques):
        fin = marques[i + 1].start() if i + 1 < len(marques) else len(brut)
        pages[int(m.group(1))] = (brut[m.end():fin].strip("\n"), m.group(3))
    return meta, pages


# ---------------------------------------------------------------------------------------------------------------
# Repérages dans le texte : dates, montants, envois, auteurs, références, documents mentionnés

MOIS = {"janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6, "juillet": 7, "aout": 8,
        "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12}
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
RE_DATE_LETTRES = re.compile(r"\b(?:(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\s+)?(1er|premier|\d{1,2})\s+"
                             r"(janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[uû]t|septembre|octobre|novembre|d[ée]cembre)\s+(\d{4})\b", re.I)
RE_DATE_SANS_ANNEE = re.compile(r"\b(?:(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\s+)?(1er|premier|\d{1,2})\s+"
                                r"(janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[uû]t|septembre|octobre|novembre|d[ée]cembre)\b(?!\s+\d{4})", re.I)
RE_DATE_CHIFFRES = re.compile(r"(?<![\d/.\-])(\d{1,2})/(\d{1,2})/(\d{4}|\d{2})(?![\d/])|(?<![\d/.\-])(\d{1,2})([.\-])(\d{1,2})\5(\d{4})(?![\d.\-])")
RE_DATE_ISO = re.compile(r"(?<![\d\-])(\d{4})-(\d{2})-(\d{2})(?![\d\-])")
RE_EVENEMENT = re.compile(r"(re[çc]ue?|pr[ée]sent[ée]e?|distribu[ée]e?|notifi[ée]e?|remise?|sign[ée]e?|en date du|fait à [^,\n]{1,40},"
                          r"|^\s*[A-ZÉÈ][\w\-' ]{1,40},)\s*(le\s+)?$", re.I | re.M)
RE_MONTANT = re.compile(r"(?<![\w,.])(\d{1,3}(?:[ \u00a0\u202f.]\d{3})+|\d+)(?:,(\d{1,2}))?\s?(€|euros?\b|EUR\b)", re.I)
RE_S10 = re.compile(r"\b([A-Z]{2})((?:\s?\d){9})\s?([A-Z]{2})\b")
RE_LAPOSTE = re.compile(r"\b(\d[A-Z])((?:\s?\d){11})\b")
RE_CIVILITE = re.compile(r"\b(M\.|Mme|Mlle|Me|Ma[îi]tre|Monsieur|Madame|Docteur|Dr|Pr)\s+((?:[A-ZÉÈÀÂÎÔÛÇ][\w'’\-]+|[A-ZÉÈÀÂÎÔÛÇ]\.)(?:\s+(?:[A-ZÉÈÀÂÎÔÛÇ][\w'’\-]+|de|du|d'|le|la)){0,4})")
RE_SIGNATURE = re.compile(r"(?im)^.{0,40}(par d[ée]l[ée]gation|p\.?\s?/\s?o\.?|p\.?\s?/\s?d\.?|pour le .{3,60} et par d[ée]l[ée]gation|signé|l[ae] (?:directeur|directrice|pr[ée]sidente?|maire|pr[ée]f[èe]te?|recteur|rectrice|chef|cheffe|g[ée]rante?|responsable|secr[ée]taire g[ée]n[ée]ral[e]?)\b).{0,100}$")
RE_FAIT_A = re.compile(r"(?m)^\s*(?:[Ff]ait à [^,\n]{2,40}|[A-ZÉÈ][\w\-' ]{2,40}),\s*le\s+(?:[a-z]+\s+)?(?:1er|\d{1,2})\s+\w+\s+\d{4}.{0,20}$")
RE_REFERENCE = re.compile(r"(?i)\b(N/?\s?R[ée]f\.?|V/?\s?R[ée]f\.?|Nos? r[ée]f(?:[ée]rences?)?|Vos? r[ée]f(?:[ée]rences?)?|R[ée]f(?:[ée]rence)?\s?:|Dossier n[°o]|Affaire suivie par|N[°o] de dossier|Num[ée]ro de dossier)\s*:?\s*([^\n]{2,70})")
RE_MENTIONNE = re.compile(r"(?im)(\bvu (?:le|la|les|l')\s[^\n;]{5,160}|\bpi[èe]ces? jointes?\s*:?[^\n]{0,160}|\bci-joint[^\n]{0,160}|\ben annexe[^\n]{0,160}|\bannexe n[°o]\s?\d+[^\n]{0,120}|^\s*PJ\s*:[^\n]{0,160})")
RE_VOIES = re.compile(r"(?i)(voies? et d[ée]lais|recours (?:gracieux|hi[ée]rarchique|contentieux)|d[ée]lai de (?:deux|2) mois|t[ée]l[ée]recours|tribunal administratif de [A-ZÉ][\w\-]+|peut (?:faire|former) l'objet d'un recours)")
CASES_GLYPHES = {"\u2610": "vide", "\u25a1": "vide", "\u25a2": "vide", "\u2611": "cochee", "\u2612": "cochee", "\u25a0": "cochee",
                 "\u25aa": "cochee", "\u2713": "marque", "\u2714": "marque", "\u2717": "marque", "\u2718": "marque"}


def _sans_accent(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


def _contexte(texte: str, debut: int, fin: int, avant: int = 50, apres: int = 30) -> str:
    return re.sub(r"\s+", " ", texte[max(0, debut - avant):fin + apres]).strip()


def _date(a: int, m: int, j: int) -> str | None:
    try:
        return date(a, m, j).isoformat()
    except ValueError:
        return None


def reperer_dates(texte: str, page: int) -> list[dict]:
    res = []
    for m in RE_DATE_LETTRES.finditer(texte):
        jour = 1 if m.group(2).lower() in ("1er", "premier") else int(m.group(2))
        mois, an = MOIS[_sans_accent(m.group(3))], int(m.group(4))
        iso = _date(an, mois, jour)
        e = {"page": page, "brut": m.group(0), "iso": iso, "valide": iso is not None, "contexte": _contexte(texte, m.start(), m.end())}
        if m.group(1):
            e["jour_ecrit"] = m.group(1).lower()
            if iso:
                e["jour_reel"] = JOURS[date.fromisoformat(iso).weekday()]
        e["evenement"] = bool(RE_EVENEMENT.search(texte[max(0, m.start() - 45):m.start()]))
        res.append(e)
    # Dates sans année (« les 30 juin, 16 août et 23 décembre 2021 », « le 30 août ») : l'année est prise de la date complète
    # qui suit de près dans la même énumération, sinon de la dernière date complète qui précède ; elle est marquée déduite.
    completes = [(m.start(), m.end(), int(m.group(4))) for m in RE_DATE_LETTRES.finditer(texte)]
    for m in RE_DATE_SANS_ANNEE.finditer(texte):
        suivante = next((a for d, _, a in completes if 0 <= d - m.end() <= 80), None)
        precedente = next((a for _, f, a in reversed(completes) if 0 <= m.start() - f <= 400), None)
        an = suivante or precedente
        if an is None:
            continue
        jour = 1 if m.group(2).lower() in ("1er", "premier") else int(m.group(2))
        iso = _date(an, MOIS[_sans_accent(m.group(3))], jour)
        e = {"page": page, "brut": m.group(0), "iso": iso, "valide": iso is not None, "annee_deduite": True,
             "contexte": _contexte(texte, m.start(), m.end()),
             "evenement": bool(RE_EVENEMENT.search(texte[max(0, m.start() - 45):m.start()]))}
        if m.group(1) and iso:
            e.update({"jour_ecrit": m.group(1).lower(), "jour_reel": JOURS[date.fromisoformat(iso).weekday()]})
        res.append(e)
    for m in RE_DATE_CHIFFRES.finditer(texte):
        if m.group(1):
            j, mo, a = int(m.group(1)), int(m.group(2)), m.group(3)
        else:
            j, mo, a = int(m.group(4)), int(m.group(6)), m.group(7)
        an = int(a) if len(a) == 4 else (2000 + int(a) if int(a) < 70 else 1900 + int(a))
        iso = _date(an, mo, j)
        res.append({"page": page, "brut": m.group(0), "iso": iso, "valide": iso is not None,
                    "contexte": _contexte(texte, m.start(), m.end()),
                    "evenement": bool(RE_EVENEMENT.search(texte[max(0, m.start() - 45):m.start()]))})
    for m in RE_DATE_ISO.finditer(texte):
        iso = _date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        res.append({"page": page, "brut": m.group(0), "iso": iso, "valide": iso is not None,
                    "contexte": _contexte(texte, m.start(), m.end()), "evenement": False})
    return res


def cle_s10_valide(chiffres: str) -> bool:
    """Clé de contrôle des numéros d'envoi au format international S10 de l'UPU (deux lettres, huit chiffres,
    une clé, deux lettres) : poids 8 6 4 2 3 5 9 7, clé = 11 - somme mod 11, 10 donne 0 et 11 donne 5."""
    d = [int(x) for x in chiffres]
    cle = 11 - sum(a * b for a, b in zip(d[:8], (8, 6, 4, 2, 3, 5, 9, 7))) % 11
    cle = 0 if cle == 10 else 5 if cle == 11 else cle
    return cle == d[8]


def reperer(texte: str, page: int) -> dict:
    r = {"dates": reperer_dates(texte, page), "montants": [], "envois": [], "auteurs": [], "references": [],
         "documents_mentionnes": [], "voies_et_delais": [], "cases_glyphes": []}
    for m in RE_MONTANT.finditer(texte):
        entier = re.sub(r"[ \u00a0\u202f.]", "", m.group(1))
        valeur = float(entier + "." + (m.group(2) or "0"))
        r["montants"].append({"page": page, "brut": m.group(0).strip(), "valeur": valeur, "contexte": _contexte(texte, m.start(), m.end())})
    for m in RE_S10.finditer(texte):
        chiffres = re.sub(r"\s", "", m.group(2))
        r["envois"].append({"page": page, "numero": m.group(1) + chiffres + m.group(3), "format": "S10 (UPU)",
                            "cle_valide": cle_s10_valide(chiffres), "contexte": _contexte(texte, m.start(), m.end())})
    for m in RE_LAPOSTE.finditer(texte):
        r["envois"].append({"page": page, "numero": m.group(1) + re.sub(r"\s", "", m.group(2)), "format": "La Poste, 13 caractères",
                            "cle_valide": None, "contexte": _contexte(texte, m.start(), m.end())})
    for m in RE_CIVILITE.finditer(texte):
        r["auteurs"].append({"page": page, "source": "civilité", "valeur": re.sub(r"\s+", " ", m.group(0)).strip()})
    for m in RE_SIGNATURE.finditer(texte):
        r["auteurs"].append({"page": page, "source": "formule de signature", "valeur": re.sub(r"\s+", " ", m.group(0)).strip()})
    for m in RE_FAIT_A.finditer(texte):
        r["auteurs"].append({"page": page, "source": "lieu et date de signature", "valeur": re.sub(r"\s+", " ", m.group(0)).strip()})
    for m in RE_REFERENCE.finditer(texte):
        r["references"].append({"page": page, "valeur": re.sub(r"\s+", " ", m.group(0)).strip()})
    for m in RE_MENTIONNE.finditer(texte):
        r["documents_mentionnes"].append({"page": page, "valeur": re.sub(r"\s+", " ", m.group(0)).strip()})
    for m in RE_VOIES.finditer(texte):
        r["voies_et_delais"].append({"page": page, "valeur": _contexte(texte, m.start(), m.end(), 40, 60)})
    for i, ch in enumerate(texte):
        if ch in CASES_GLYPHES:
            fin = texte.find("\n", i)
            r["cases_glyphes"].append({"page": page, "glyphe": ch, "etat_probable": CASES_GLYPHES[ch],
                                       "libelle_voisin": texte[i + 1:fin if fin > 0 else i + 80].strip()[:80]})
    return r


def fusionner_reperes(liste: list[dict]) -> dict:
    total: dict[str, list] = {}
    for r in liste:
        for k, v in r.items():
            total.setdefault(k, []).extend(v)
    return total


# ---------------------------------------------------------------------------------------------------------------
# Lecture des formats

def _date_pdf(v: str | None) -> str | None:
    m = re.match(r"D:(\d{4})(\d{2})?(\d{2})?(\d{2})?(\d{2})?(\d{2})?", v or "")
    if not m:
        return None
    try:
        return datetime(int(m[1]), int(m[2] or 1), int(m[3] or 1), int(m[4] or 0), int(m[5] or 0), int(m[6] or 0)).isoformat()
    except ValueError:
        return None


def ocr_disponible() -> bool:
    try:
        import fitz
        fitz.get_tessdata()
        return True
    except Exception:  # noqa: BLE001 - Tesseract absent ou PyMuPDF absent
        return False


def _ocr(page) -> str:
    for langue in ("fra", "fra+eng", "eng"):
        try:
            tp = page.get_textpage_ocr(language=langue, dpi=300, full=True)
            return page.get_text("text", textpage=tp)
        except Exception:  # noqa: BLE001
            continue
    return ""


def _famille(police: str) -> str:
    nom = re.sub(r"^[A-Z]{6}\+", "", police or "")
    nom = re.split(r"[-,]", nom)[0]
    for _ in range(3):
        nom = re.sub(r"(PSMT|PS|MT|Bold|Italic|Oblique|Regular|Light|Medium|Semibold|Black)$", "", nom)
    return nom.lower()


def _polices_isolees(page, n: int) -> list[dict]:
    """Date ou montant composés, au milieu d'une ligne, dans une famille ou une taille de police différente du reste de
    la ligne : signe classique d'un texte remplacé. Un indice à examiner sur l'image, jamais une preuve."""
    res = []
    try:
        d = page.get_text("dict")
    except Exception:  # noqa: BLE001
        return res
    for bloc in d.get("blocks", []):
        for ligne in bloc.get("lines", []):
            spans = [s for s in ligne.get("spans", []) if s.get("text", "").strip()]
            if len(spans) < 2:
                continue
            for s in spans:
                t = s["text"]
                if not (RE_DATE_LETTRES.search(t) or RE_DATE_CHIFFRES.search(t) or RE_MONTANT.search(t)):
                    continue
                poids = Counter()
                for x in spans:
                    if x is not s:
                        poids[(_famille(x["font"]), round(x["size"], 1))] += len(x["text"].strip())
                if not poids:
                    continue
                (fam, taille), _ = poids.most_common(1)[0]
                if _famille(s["font"]) != fam or abs(s["size"] - taille) > 0.6:
                    res.append({"page": n, "texte": t.strip()[:80], "police": s["font"], "taille": round(s["size"], 1),
                                "police_de_la_ligne": fam, "taille_de_la_ligne": taille})
    return res


def _cases_dessinees(page, n: int) -> list[dict]:
    """Petits carrés vectoriels d'un formulaire aplati et ce qu'ils contiennent. État probable seulement."""
    import fitz
    res, vus = [], set()
    try:
        dessins = page.get_drawings()
        mots = page.get_text("words")
        # L'apparence des annotations et des champs PDF n'est pas une case dessinée : elle est relevée à part.
        exclues = [a.rect for a in page.annots() or []] + [w.rect for w in page.widgets() or []]
    except Exception:  # noqa: BLE001
        return res
    def carre(d):
        r = d.get("rect")
        if r is None or not (5 <= r.width <= 20 and 5 <= r.height <= 20 and abs(r.width - r.height) <= 1.5):
            return False
        # Une case a un bord tracé : un cadre, ou quatre traits. Un aplat de traits et de courbes est un glyphe ou un logo.
        items = d.get("items", [])
        cadre = any(it[0] in ("re", "qu") for it in items) or sum(1 for it in items if it[0] == "l") == 4
        return d.get("type") in ("s", "fs") and cadre
    candidats = [d for d in dessins if carre(d) and not any(fitz.Rect(d["rect"]).intersects(x) for x in exclues)]
    # Une rangée de cases jointives sert à écrire un nom ou une date lettre par lettre : ce n'est pas une case à cocher.
    peigne = set()
    for i, a in enumerate(candidats):
        for b in candidats[i + 1:]:
            ra, rb = a["rect"], b["rect"]
            if abs(ra.y0 - rb.y0) <= 1 and (abs(ra.x1 - rb.x0) <= 3 or abs(rb.x1 - ra.x0) <= 3):
                peigne |= {id(a), id(b)}
    for d in candidats:
        if id(d) in peigne:
            continue
        r = d["rect"]
        cle = (round(r.x0), round(r.y0))
        if cle in vus:
            continue
        vus.add(cle)
        dedans = fitz.Rect(r.x0 + 0.8, r.y0 + 0.8, r.x1 - 0.8, r.y1 - 0.8)
        items = d.get("items", [])
        traits = sum(1 for it in items if it[0] == "l")
        cadre = any(it[0] in ("re", "qu") for it in items)
        # Un cadre accompagné de traits, ou plus de quatre traits, dessine une croix dans la case ; un aplat sombre la remplit.
        marque = (cadre and traits >= 1) or traits > 4
        marque = marque or (d.get("fill") is not None and sum(d["fill"]) < 2.4 and d.get("type") in ("f", "fs"))
        for d2 in dessins:
            r2 = d2.get("rect")
            if d2 is d or r2 is None:
                continue
            # Le fond clair d'une case ou un second tracé de son propre cadre ne la marquent pas.
            clair = d2.get("type") == "f" and d2.get("fill") is not None and sum(d2["fill"]) >= 2.4
            # Une diagonale a le même encadrement que la case : seul un second cadre est écarté.
            meme_cadre = all(abs(a - b) <= 1.2 for a, b in zip(r2, r)) and any(it[0] in ("re", "qu") for it in d2.get("items", []))
            if clair or meme_cadre:
                continue
            if r2.width <= r.width + 1 and r2.height <= r.height + 1 and dedans.intersects(r2) and (r2.width > 1 or r2.height > 1):
                marque = True
                break
        if not marque:
            marque = any(fitz.Rect(w[:4]).intersects(dedans) for w in mots)
        voisins = sorted((w for w in mots if abs((w[1] + w[3]) / 2 - (r.y0 + r.y1) / 2) < max(4, r.height) and r.x1 <= w[0] <= r.x1 + 260),
                         key=lambda w: w[0])
        res.append({"page": n, "rect": [round(r.x0, 1), round(r.y0, 1), round(r.x1, 1), round(r.y1, 1)],
                    "etat_probable": "marquee" if marque else "vide", "libelle_voisin": " ".join(w[4] for w in voisins[:10])})
    return res


def _historique_xmp(xmp: str) -> list[dict]:
    hist = []
    for bloc in re.findall(r"<rdf:li[^>]*>(.*?)</rdf:li>", xmp or "", re.S):
        action = re.search(r"stEvt:action>?=?\"?([^<\"]+)", bloc)
        quand = re.search(r"stEvt:when>?=?\"?([^<\"]+)", bloc)
        agent = re.search(r"stEvt:softwareAgent>?=?\"?([^<\"]+)", bloc)
        if action or quand:
            hist.append({"action": action and action.group(1), "date": quand and quand.group(1), "logiciel": agent and agent.group(1)})
    return hist


def _revisions(chemin: Path, dossier: Path, linearise: bool, texte_final: str) -> list[dict]:
    """Versions successives d'un PDF enregistré par ajouts : chaque version antérieure est extraite telle qu'elle
    était, puis son texte est comparé au texte final."""
    import fitz
    data = chemin.read_bytes()
    fins = [m.end() for m in re.finditer(rb"%%EOF[\r\n]*", data)]
    if linearise:
        fins = fins[1:]
    if len(fins) <= 1:
        return []
    res = []
    for i, fin in enumerate(fins[:-1], 1):
        dossier.mkdir(parents=True, exist_ok=True)
        sortie = dossier / f"revision_{i}.pdf"
        sortie.write_bytes(data[:fin])
        entree = {"numero": i, "octets": fin, "fichier": sortie.as_posix(), "lisible": False, "differences": []}
        try:
            with fitz.open(sortie) as d:
                ancien = "\n".join(p.get_text("text") for p in d)
            entree["lisible"] = True
            diff = [l for l in difflib.unified_diff(ancien.splitlines(), texte_final.splitlines(), lineterm="", n=0)
                    if l[:1] in "+-" and not l.startswith(("+++", "---"))]
            entree["texte_identique"] = not diff
            entree["differences"] = diff[:60]
        except Exception as e:  # noqa: BLE001
            entree["erreur"] = str(e)[:200]
        res.append(entree)
    return res


def lire_pdf_ou_image(racine: Path, chemin: Path, fmt: str, base: str, ocr: bool) -> dict:
    import fitz
    info: dict = {"pages": 0, "pages_lues": [], "metadonnees": {}, "formulaire": {"champs": [], "cases_dessinees": []},
                  "signatures": {"champs": 0, "signes": 0, "images_bas_derniere_page": 0}, "annotations": [],
                  "revisions": [], "polices_isolees": [], "formats_de_page": [], "pages_numerisees": [], "fichiers_joints": []}
    with fitz.open(chemin) as doc:
        info["pages"] = doc.page_count
        if doc.needs_pass:
            info["chiffre"] = True
            return info
        if fmt == "pdf":
            meta = {k: v for k, v in (doc.metadata or {}).items() if v}
            meta["creation_iso"] = _date_pdf(meta.get("creationDate"))
            meta["modification_iso"] = _date_pdf(meta.get("modDate"))
            try:
                xmp = doc.get_xml_metadata()
            except Exception:  # noqa: BLE001
                xmp = ""
            if xmp:
                meta["xmp_historique"] = _historique_xmp(xmp)
                for cle in ("CreatorTool", "CreateDate", "ModifyDate", "MetadataDate"):
                    m = re.search(r"xmp:" + cle + r">?=?\"?([^<\"]+)", xmp)
                    if m:
                        meta["xmp_" + cle] = m.group(1)
            meta["linearise"] = bool(getattr(doc, "is_fast_webaccess", False))
            try:
                meta["sigflags"] = doc.get_sigflags()
            except Exception:  # noqa: BLE001
                pass
            info["metadonnees"] = meta
            try:
                info["fichiers_joints"] = list(doc.embfile_names())
            except Exception:  # noqa: BLE001
                pass
            brut = chemin.read_bytes()
            info["javascript"] = bool(re.search(rb"/JavaScript|/JS\s*[(<]", brut))
        tailles = Counter()
        pages = []
        for i, page in enumerate(doc, 1):
            texte = page.get_text("text")
            mode = "texte_natif" if texte.strip() else "sans_texte"
            if texte.strip() and fmt == "pdf":
                try:
                    trace = page.get_texttrace()
                    visibles = sum(len(s.get("chars", ())) for s in trace if s.get("type") != 3 and s.get("opacity", 1) > 0)
                    if trace and visibles == 0:
                        mode = "couche_ocr"
                except Exception:  # noqa: BLE001
                    pass
            if mode == "sans_texte" and ocr:
                texte = _ocr(page)
                mode = "ocr" if texte.strip() else "sans_texte"
            r = page.rect
            # Deux pages dont les dimensions diffèrent de moins de trois points ont le même format (arrondis d'export).
            dims = (min(r.width, r.height), max(r.width, r.height))
            cle = next((k for k in tailles if abs(k[0] - dims[0]) < 3 and abs(k[1] - dims[1]) < 3), (round(dims[0]), round(dims[1])))
            tailles[cle] += 1
            try:
                images = page.get_image_info()
            except Exception:  # noqa: BLE001
                images = []
            surface = r.width * r.height or 1
            couverte = sum(fitz.Rect(im["bbox"]).get_area() for im in images)
            if fmt != "pdf" or couverte / surface > 0.8:
                info["pages_numerisees"].append(i)
                if mode == "texte_natif":
                    # Le texte se lit, mais la page est une image : l'acte lui-même est dans l'image.
                    mode = "texte_partiel_sur_image"
            elif i == doc.page_count:
                info["signatures"]["images_bas_derniere_page"] = sum(
                    1 for im in images if fitz.Rect(im["bbox"]).y0 > r.height * 0.5 and fitz.Rect(im["bbox"]).get_area() < surface * 0.25)
            pages.append({"n": i, "texte": texte, "mode": mode})
            if fmt != "pdf":
                continue
            for w in page.widgets() or []:
                t = w.field_type_string
                v = w.field_value
                champ = {"page": i, "nom": w.field_name, "type": t, "valeur": None if v is None else str(v)}
                if t in ("CheckBox", "RadioButton"):
                    champ["etat"] = "cochee" if v not in (None, False, "", "Off", "off", "0") else "vide"
                if t == "Signature":
                    info["signatures"]["champs"] += 1
                    if getattr(w, "is_signed", False):
                        info["signatures"]["signes"] += 1
                info["formulaire"]["champs"].append(champ)
            for a in page.annots() or []:
                inf = a.info or {}
                info["annotations"].append({"page": i, "type": a.type[1], "auteur": inf.get("title", ""), "contenu": (inf.get("content") or "")[:200],
                                            "date": _date_pdf(inf.get("modDate")) or inf.get("modDate", "")})
            info["formulaire"]["cases_dessinees"].extend(_cases_dessinees(page, i))
            info["polices_isolees"].extend(_polices_isolees(page, i))
        info["formats_de_page"] = [{"points": list(k), "pages": n} for k, n in tailles.items()]
        info["_pages"] = pages
    if fmt == "pdf":
        texte_final = "\n".join(p["texte"] for p in pages)
        info["revisions"] = _revisions(chemin, racine / "pieces" / "rendus" / base, bool(info["metadonnees"].get("linearise")), texte_final)
        for rv in info["revisions"]:
            rv["fichier"] = L.relatif(racine, rv["fichier"]) or rv["fichier"]
    if fmt in FORMATS_IMAGE:
        info["exif"] = lire_exif(chemin)
    return info


def lire_exif(chemin: Path) -> dict | None:
    try:
        from PIL import Image
    except ImportError:
        return None
    try:
        with Image.open(chemin) as im:
            ex = im.getexif()
            sous = ex.get_ifd(0x8769) if ex else {}
            res = {"date_fichier": ex.get(306), "appareil": " ".join(x for x in (ex.get(271), ex.get(272)) if x) or None,
                   "logiciel": ex.get(305), "date_prise_de_vue": sous.get(36867), "date_numerisation": sous.get(36868),
                   "gps": bool(ex.get_ifd(0x8825)) if ex else False}
            return {k: (str(v) if v is not None and not isinstance(v, bool) else v) for k, v in res.items()}
    except Exception:  # noqa: BLE001
        return None


def _xml_texte(fragment: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", fragment))


def lire_docx(chemin: Path) -> dict:
    info: dict = {"metadonnees": {}, "modifications_suivies": {"insertions": [], "suppressions": []}, "commentaires": []}
    with zipfile.ZipFile(chemin) as z:
        def lire(nom):
            if nom not in z.namelist() or z.getinfo(nom).file_size > 50_000_000:
                return ""
            return z.read(nom).decode("utf-8", "ignore")
        core, app, doc = lire("docProps/core.xml"), lire("docProps/app.xml"), lire("word/document.xml")
        for cle, motif in (("auteur", r"<dc:creator>(.*?)</dc:creator>"), ("dernier_modificateur", r"<cp:lastModifiedBy>(.*?)</cp:lastModifiedBy>"),
                           ("creation", r"<dcterms:created[^>]*>(.*?)</dcterms:created>"), ("modification", r"<dcterms:modified[^>]*>(.*?)</dcterms:modified>"),
                           ("revision", r"<cp:revision>(.*?)</cp:revision>"), ("titre", r"<dc:title>(.*?)</dc:title>")):
            m = re.search(motif, core, re.S)
            if m:
                info["metadonnees"][cle] = _xml_texte(m.group(1))
        for cle, motif in (("application", r"<Application>(.*?)</Application>"), ("societe", r"<Company>(.*?)</Company>"),
                           ("modele", r"<Template>(.*?)</Template>"), ("minutes_d_edition", r"<TotalTime>(.*?)</TotalTime>")):
            m = re.search(motif, app, re.S)
            if m:
                info["metadonnees"][cle] = _xml_texte(m.group(1))
        for genre, balise in (("insertions", "w:ins"), ("suppressions", "w:del")):
            for m in re.finditer(r"<" + balise + r"\b([^>]*)>(.*?)</" + balise + ">", doc, re.S):
                auteur = re.search(r'w:author="([^"]*)"', m.group(1))
                quand = re.search(r'w:date="([^"]*)"', m.group(1))
                contenu = "".join(re.findall(r"<w:(?:t|delText)[^>]*>(.*?)</w:(?:t|delText)>", m.group(2), re.S))
                info["modifications_suivies"][genre].append({"auteur": auteur and auteur.group(1), "date": quand and quand.group(1),
                                                             "texte": html.unescape(contenu)[:200]})
        for m in re.finditer(r"<w:comment\b([^>]*)>(.*?)</w:comment>", lire("word/comments.xml"), re.S):
            auteur = re.search(r'w:author="([^"]*)"', m.group(1))
            info["commentaires"].append({"auteur": auteur and auteur.group(1), "texte": _xml_texte(m.group(2))[:200]})
        paragraphes = []
        for p in re.findall(r"<w:p[ >].*?</w:p>", re.sub(r"<w:del\b.*?</w:del>", "", doc, flags=re.S), re.S):
            paragraphes.append(html.unescape("".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", p, re.S))))
        info["_pages"] = [{"n": 1, "texte": "\n".join(paragraphes), "mode": "texte_natif"}]
    return info


def lire_odt(chemin: Path) -> dict:
    info: dict = {"metadonnees": {}}
    with zipfile.ZipFile(chemin) as z:
        meta = z.read("meta.xml").decode("utf-8", "ignore") if "meta.xml" in z.namelist() else ""
        contenu = z.read("content.xml").decode("utf-8", "ignore") if "content.xml" in z.namelist() else ""
    for cle, motif in (("auteur_initial", r"<meta:initial-creator>(.*?)<"), ("dernier_modificateur", r"<dc:creator>(.*?)<"),
                       ("creation", r"<meta:creation-date>(.*?)<"), ("modification", r"<dc:date>(.*?)<"),
                       ("cycles_d_edition", r"<meta:editing-cycles>(.*?)<"), ("generateur", r"<meta:generator>(.*?)<")):
        m = re.search(motif, meta, re.S)
        if m:
            info["metadonnees"][cle] = _xml_texte(m.group(1))
    info["modifications_suivies"] = "<text:tracked-changes" in contenu
    paragraphes = [_xml_texte(p) for p in re.findall(r"<text:(?:p|h)\b[^>]*>(.*?)</text:(?:p|h)>", contenu, re.S)]
    info["_pages"] = [{"n": 1, "texte": "\n".join(paragraphes), "mode": "texte_natif"}]
    return info


def lire_eml(chemin: Path) -> dict:
    msg = email.message_from_bytes(chemin.read_bytes(), policy=email.policy.default)

    def h(k):
        return str(msg.get(k, "") or "")
    recus = []
    for r in msg.get_all("Received") or []:
        m = re.search(r";\s*([^;]+)$", " ".join(str(r).split()))
        try:
            recus.append(parsedate_to_datetime(m.group(1)).isoformat() if m else None)
        except (TypeError, ValueError):
            recus.append(None)
    try:
        date_entete = parsedate_to_datetime(h("Date")).isoformat() if h("Date") else None
    except (TypeError, ValueError):
        date_entete = None
    auth = h("Authentication-Results")
    resultat = {k: (re.search(k + r"=(\w+)", auth, re.I) or [None, None])[1] for k in ("dkim", "spf", "dmarc")}
    jointes = []
    for part in msg.iter_attachments():
        donnees = part.get_payload(decode=True) or b""
        jointes.append({"nom": part.get_filename(), "type": part.get_content_type(), "octets": len(donnees),
                        "sha256": hashlib.sha256(donnees).hexdigest()})
    corps = ""
    try:
        b = msg.get_body(preferencelist=("plain", "html"))
        if b is not None:
            corps = b.get_content()
            if b.get_content_type() == "text/html":
                corps = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<(script|style).*?</\1>", "", corps)))
    except Exception:  # noqa: BLE001
        corps = ""
    entetes = {k: h(k) for k in ("From", "To", "Cc", "Date", "Subject", "Message-ID", "In-Reply-To", "References", "Return-Path", "Reply-To")}
    texte = "\n".join(f"{k}: {v}" for k, v in entetes.items() if v) + "\n\n" + corps
    return {"courriel": {"entetes": entetes, "date_entete_iso": date_entete, "recus": recus, "authentification": resultat,
                         "dkim_signature": bool(msg.get("DKIM-Signature")), "pieces_jointes": jointes},
            "_pages": [{"n": 1, "texte": texte, "mode": "texte_natif"}]}


def lire_texte(chemin: Path, fmt: str) -> dict:
    brut = chemin.read_bytes()
    try:
        texte = brut.decode("utf-8")
    except UnicodeDecodeError:
        texte = brut.decode("cp1252", "replace")
    if fmt == "html":
        texte = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<(script|style).*?</\1>", "", texte)))
    morceaux = texte.split("\f")
    return {"_pages": [{"n": i, "texte": t, "mode": "texte_natif"} for i, t in enumerate(morceaux, 1)]}


# ---------------------------------------------------------------------------------------------------------------
# Indices mécaniques : ce que la lecture de la fiche doit examiner une à une

def indices(entree: dict, reperes: dict) -> list[dict]:
    res = []

    def ajouter(code, page, description):
        res.append({"id": f"M{len(res) + 1}", "code": code, "page": page, "description": description})
    if entree.get("empreinte_conforme") is False:
        ajouter("empreinte_differente", None, "Le fichier n'a plus l'empreinte inscrite au bordereau : il a été modifié depuis sa cotation.")
    if entree.get("extension_conforme") is False:
        ajouter("extension_trompeuse", None, f"L'extension du fichier ne correspond pas à son contenu réel ({entree.get('format')}).")
    if entree.get("chiffre"):
        ajouter("fichier_chiffre", None, "Fichier protégé par mot de passe : contenu non lu.")
    for d in reperes.get("dates", []):
        if not d["valide"]:
            ajouter("date_impossible", d["page"], f"Date inexistante au calendrier : « {d['brut']} » ({d['contexte']}).")
        elif d.get("jour_ecrit") and d.get("jour_reel") and d["jour_ecrit"] != d["jour_reel"]:
            ajouter("jour_de_semaine_incoherent", d["page"], f"« {d['brut']} » : le {d['iso']} était un {d['jour_reel']}.")
    meta = entree.get("metadonnees") or {}
    c, m = meta.get("creation_iso"), meta.get("modification_iso")
    if c and m and m < c:
        ajouter("metadonnees_dates_incoherentes", None, f"Date de modification du fichier ({m}) antérieure à sa date de création ({c}).")
    if m:
        for d in reperes.get("dates", []):
            if d.get("evenement") and d["iso"] and d["iso"] > m[:10]:
                ajouter("date_posterieure_au_fichier", d["page"], f"Le texte relate un événement du {d['iso']} (« {d['contexte']} ») alors que le "
                        f"fichier a été modifié pour la dernière fois le {m[:10]} selon ses métadonnées.")
    for rv in entree.get("revisions") or []:
        etat = "texte identique" if rv.get("texte_identique") else f"{len(rv.get('differences', []))} ligne(s) de texte différente(s)"
        ajouter("version_successive", None, f"Version antérieure n° {rv['numero']} conservée dans le fichier ({rv['fichier']}) : {etat}.")
    for p in entree.get("polices_isolees") or []:
        ajouter("police_differente_dans_la_ligne", p["page"], f"« {p['texte']} » est composé en {p['police']} {p['taille']} pt au milieu "
                f"d'une ligne en {p['police_de_la_ligne']} {p['taille_de_la_ligne']} pt.")
    if len(entree.get("formats_de_page") or []) > 1:
        ajouter("formats_de_page_differents", None, "Pages de formats différents : document possiblement assemblé à partir de sources distinctes.")
    form = entree.get("formulaire") or {}
    cases = [c for c in form.get("champs", []) if c.get("etat")] + form.get("cases_dessinees", []) + reperes.get("cases_glyphes", [])
    if cases:
        lecture = "; ".join(f"p. {c['page']} « {(c.get('libelle_voisin') or c.get('nom') or '')[:40]} » "
                            f"{c.get('etat') or c.get('etat_probable')}" for c in cases[:12])
        ajouter("cases_de_formulaire", cases[0]["page"], f"{len(cases)} case(s) repérée(s), état lu mécaniquement ({lecture}) : "
                "à confirmer sur le rendu de chaque page.")
    sig = entree.get("signatures") or {}
    if sig.get("images_bas_derniere_page"):
        ajouter("images_en_bas_de_derniere_page", entree.get("pages"), f"{sig['images_bas_derniere_page']} image(s) dans le bas de la dernière page "
                "(signature, paraphe ou cachet possibles) : les examiner sur le rendu.")
    if sig.get("champs") and sig.get("signes", 0) < sig["champs"]:
        ajouter("champ_de_signature_vide", None, f"{sig['champs']} champ(s) de signature électronique, {sig.get('signes', 0)} signé(s).")
    elif sig.get("champs"):
        ajouter("signature_electronique", None, "Signature électronique présente : sa validité et l'absence de modification postérieure se vérifient avec un outil de validation, pas ici.")
    if entree.get("annotations"):
        ajouter("annotations", None, f"{len(entree['annotations'])} annotation(s) ajoutée(s) au document (auteurs : "
                f"{', '.join(sorted({a['auteur'] for a in entree['annotations'] if a['auteur']})) or 'non renseignés'}).")
    if entree.get("javascript"):
        ajouter("javascript", None, "Le PDF contient du JavaScript : son affichage peut varier selon le lecteur.")
    if entree.get("fichiers_joints"):
        ajouter("fichiers_joints", None, f"Fichiers incorporés au PDF : {', '.join(entree['fichiers_joints'][:10])}.")
    for e in reperes.get("envois", []):
        if e.get("cle_valide") is False:
            ajouter("numero_d_envoi_invalide", e["page"], f"Numéro d'envoi {e['numero']} : la clé de contrôle S10 ne correspond pas.")
    co = entree.get("courriel") or {}
    if co:
        recus = [r for r in co.get("recus", []) if r]
        if not co.get("recus"):
            ajouter("courriel_sans_trace_de_transport", None, "Aucun en-tête Received : la date d'envoi n'est attestée par aucun serveur (copie, transfert ou impression).")
        elif co.get("date_entete_iso") and recus:
            try:
                ecart = abs((datetime.fromisoformat(recus[-1]) - datetime.fromisoformat(co["date_entete_iso"])).total_seconds()) / 3600
                if ecart > 24:
                    ajouter("courriel_date_incoherente", None, f"Date annoncée {co['date_entete_iso']}, premier serveur {recus[-1]} : écart de {ecart:.0f} h.")
            except (TypeError, ValueError):
                pass
        de = re.search(r"@([\w.\-]+)", co.get("entetes", {}).get("From", ""))
        retour = re.search(r"@([\w.\-]+)", co.get("entetes", {}).get("Return-Path", ""))
        if de and retour and de.group(1).lower() != retour.group(1).lower():
            ajouter("courriel_expediteur_divergent", None, f"Domaine de l'expéditeur affiché ({de.group(1)}) différent de l'adresse de retour ({retour.group(1)}).")
        for k, v in (co.get("authentification") or {}).items():
            if v and v.lower() in ("fail", "softfail", "none", "neutral"):
                ajouter("courriel_authentification", None, f"Authentification {k} : {v}.")
    ms = entree.get("modifications_suivies")
    if isinstance(ms, dict) and (ms.get("insertions") or ms.get("suppressions")):
        ajouter("modifications_suivies", None, f"{len(ms['insertions'])} insertion(s) et {len(ms['suppressions'])} suppression(s) suivies dans le fichier.")
    elif ms is True:
        ajouter("modifications_suivies", None, "Modifications suivies présentes dans le fichier.")
    if entree.get("commentaires"):
        ajouter("commentaires", None, f"{len(entree['commentaires'])} commentaire(s) de relecture dans le fichier.")
    md = entree.get("metadonnees") or {}
    if md.get("auteur") and md.get("dernier_modificateur") and md["auteur"] != md["dernier_modificateur"]:
        ajouter("auteurs_successifs", None, f"Fichier créé par « {md['auteur']} », modifié en dernier par « {md['dernier_modificateur']} ».")
    ex = entree.get("exif") or {}
    if ex.get("logiciel"):
        ajouter("image_traitee", None, f"L'image porte la marque du logiciel « {ex['logiciel']} ».")
    if ex.get("date_prise_de_vue") and ex.get("date_fichier") and ex["date_prise_de_vue"] != ex["date_fichier"]:
        ajouter("image_modifiee_apres_prise_de_vue", None, f"Prise de vue {ex['date_prise_de_vue']}, fichier daté {ex['date_fichier']}.")
    return res


# ---------------------------------------------------------------------------------------------------------------
# Commande inventaire

def inventorier_piece(racine: Path, cote: str | None, rel: str, sha_bordereau: str | None, ocr: bool) -> dict:
    chemin = racine / rel
    fmt = detecter_format(chemin)
    sha = L.sha256_fichier(chemin)
    entree: dict = {"cote": cote, "fichier": rel, "sha256": sha, "taille": chemin.stat().st_size, "format": fmt,
                    "extension_conforme": Path(rel).suffix.lower() in EXTENSIONS.get(fmt, {Path(rel).suffix.lower()}),
                    "empreinte_conforme": None if sha_bordereau is None else sha == sha_bordereau,
                    "date_fichier_systeme": datetime.fromtimestamp(chemin.stat().st_mtime).isoformat(timespec="seconds"),
                    "inventorie_le": L.horodatage(), "version_outil": VERSION_OUTIL}
    base = nom_base(cote, rel)
    try:
        if fmt in FORMATS_PAGINES:
            info = lire_pdf_ou_image(racine, chemin, fmt, base, ocr)
        elif fmt == "docx":
            info = lire_docx(chemin)
        elif fmt == "odt":
            info = lire_odt(chemin)
        elif fmt == "eml":
            info = lire_eml(chemin)
        elif fmt in ("texte", "html"):
            info = lire_texte(chemin, fmt)
        else:
            info = {"_pages": [], "non_lu": f"Format {fmt} non lu par pieces.py : le convertir en PDF (ou en EML pour un message Outlook) et coter la conversion à côté de l'original."}
    except Exception as e:  # noqa: BLE001 - un fichier corrompu ne doit pas arrêter l'inventaire
        cause = "PyMuPDF (fitz) absent de cet interpréteur" if isinstance(e, ModuleNotFoundError) else str(e)[:200]
        info = {"_pages": [], "erreur_lecture": f"{type(e).__name__}: {cause}"}
    pages = info.pop("_pages", [])
    entree.update(info)
    entree["pages"] = entree.get("pages") or len(pages)
    entree["pages_texte"] = [p["n"] for p in pages if p["mode"] == "texte_natif"]
    entree["pages_couche_ocr"] = [p["n"] for p in pages if p["mode"] == "couche_ocr"]
    entree["pages_ocr"] = [p["n"] for p in pages if p["mode"] == "ocr"]
    entree["pages_sans_texte"] = [p["n"] for p in pages if p["mode"] == "sans_texte"]
    entree["pages_image_et_texte_partiel"] = [p["n"] for p in pages if p["mode"] == "texte_partiel_sur_image"]
    if pages and cote is not None:
        ex = chemin_extraction(racine, cote, rel)
        ecrire_extraction(ex, cote, rel, sha, pages)
        entree["texte"] = ex.relative_to(racine).as_posix()
    reperes = fusionner_reperes([reperer(p["texte"], p["n"]) for p in pages])
    entree["reperes"] = reperes
    entree["indices"] = indices(entree, reperes)
    return entree


def cmd_inventaire(racine: Path, cotes: list[str] | None = None, refaire: bool = False) -> dict:
    b = lire_bordereau(racine)
    ancien = L.lire_json(racine / INVENTAIRE, {}) or {}
    anciens = {(norm_cote(p["cote"]) if p.get("cote") is not None else None, p.get("sha256")): p for p in ancien.get("pieces", [])}
    ocr = ocr_disponible()
    choix = {norm_cote(c) for c in cotes} if cotes else None
    pieces, absentes = [], []
    for cote, p in sorted(b.items(), key=lambda x: (not x[0].isdigit(), int(x[0]) if x[0].isdigit() else 0, x[0])):
        rel = str(p.get("fichier", ""))
        if not (racine / rel).is_file():
            absentes.append(cote)
            continue
        precedent = None
        if choix is not None and cote not in choix:
            precedent = next((v for (c, _), v in anciens.items() if c == cote), None)
        else:
            sha = L.sha256_fichier(racine / rel)
            prec = anciens.get((cote, sha))
            if not refaire and prec and prec.get("version_outil") == VERSION_OUTIL and prec.get("texte") and (racine / prec["texte"]).is_file():
                precedent = prec
        pieces.append(precedent or inventorier_piece(racine, cote, rel, p.get("sha256"), ocr))
    connus = {str(p.get("fichier", "")).replace("\\", "/") for p in b.values()}
    hors = []
    dossier = racine / "pieces" / "originaux"
    for f in sorted(dossier.rglob("*")) if dossier.is_dir() else []:
        rel = f.relative_to(racine).as_posix()
        if f.is_file() and f.name != ".gitkeep" and rel not in connus:
            hors.append({"fichier": rel, "sha256": L.sha256_fichier(f), "format": detecter_format(f), "taille": f.stat().st_size})
    inv = {"schema": "inventaire/1", "genere_le": L.horodatage(), "outil": VERSION_OUTIL,
           "ocr": "disponible" if ocr else "indisponible : les pages sans texte se lisent sur leur rendu (pieces.py rendre)",
           "pieces": pieces, "hors_bordereau": hors, "absentes": absentes,
           "alterees": [p["cote"] for p in pieces if p.get("empreinte_conforme") is False]}
    L.ecrire_json(racine / INVENTAIRE, inv)
    return inv


def _plages(pages: list[int]) -> str:
    morceaux, debut = [], None
    for i, n in enumerate(pages):
        if debut is None:
            debut = n
        if i + 1 == len(pages) or pages[i + 1] != n + 1:
            morceaux.append(str(debut) if debut == n else f"{debut}-{n}")
            debut = None
    return ", ".join(morceaux)


def resume_inventaire(inv: dict) -> str:
    lignes = [f"Inventaire : {len(inv['pieces'])} pièce(s) ; OCR {inv['ocr']}."]
    for p in inv["pieces"]:
        sans = sorted(set(p.get("pages_sans_texte", []) + p.get("pages_couche_ocr", []) + p.get("pages_ocr", []) + p.get("pages_image_et_texte_partiel", [])))
        champs = len((p.get("formulaire") or {}).get("champs", [])) + len((p.get("formulaire") or {}).get("cases_dessinees", []))
        lignes.append(f"- cote {p['cote']} : {p['format']}, {p.get('pages', 0)} p."
                      + (f", à lire sur rendu p. {_plages(sans)}" if sans else "")
                      + (f", {champs} case(s) ou champ(s) de formulaire" if champs else "")
                      + (f", {len(p.get('indices', []))} indice(s) à examiner" if p.get("indices") else "")
                      + (f" ; {p['non_lu']}" if p.get("non_lu") else "") + (f" ; ERREUR {p['erreur_lecture']}" if p.get("erreur_lecture") else ""))
    for h in inv["hors_bordereau"]:
        lignes.append(f"- HORS BORDEREAU : {h['fichier']} ({h['format']}) ; le coter par affaire.py piece ajouter ou le retirer.")
    for c in inv["absentes"]:
        lignes.append(f"- ABSENTE : cote {c}, fichier introuvable.")
    for c in inv["alterees"]:
        lignes.append(f"- ALTÉRÉE : cote {c}, empreinte différente de celle du bordereau.")
    lignes.append("Écrit : pieces/inventaire.json et pieces/texte/*.extraction.txt.")
    return "\n".join(lignes)


# ---------------------------------------------------------------------------------------------------------------
# Commande rendre

def pages_a_examiner(entree: dict) -> list[int]:
    n = entree.get("pages") or 0
    pages = set(entree.get("pages_sans_texte", [])) | set(entree.get("pages_couche_ocr", [])) | set(entree.get("pages_ocr", []))         | set(entree.get("pages_image_et_texte_partiel", []))
    form = entree.get("formulaire") or {}
    pages |= {c["page"] for c in form.get("champs", []) + form.get("cases_dessinees", [])}
    pages |= {c["page"] for c in (entree.get("reperes") or {}).get("cases_glyphes", [])}
    pages |= {i["page"] for i in entree.get("indices", []) if i.get("page")}
    pages |= {a["page"] for a in entree.get("annotations") or []}
    pages |= {a["page"] for a in (entree.get("reperes") or {}).get("auteurs", []) if a.get("source") in ("formule de signature", "lieu et date de signature")}
    if n:
        pages |= {1, n}
    return sorted(p for p in pages if 1 <= p <= n)


def _plage(spec: str) -> list[int]:
    res = []
    for morceau in (spec or "").split(","):
        m = re.fullmatch(r"\s*(\d+)\s*(?:-\s*(\d+))?\s*", morceau)
        if m:
            a, b = int(m[1]), int(m[2] or m[1])
            res.extend(range(a, b + 1))
    return sorted(set(res))


def cmd_rendre(racine: Path, cotes: list[str] | None, pages_spec: str | None, a_examiner: bool, dpi: int) -> list[str]:
    import fitz
    b = lire_bordereau(racine)
    inv = {norm_cote(p["cote"]): p for p in (L.lire_json(racine / INVENTAIRE, {}) or {}).get("pieces", []) if p.get("cote") is not None}
    sorties = []
    for cote, p in b.items():
        if cotes and cote not in {norm_cote(c) for c in cotes}:
            continue
        src = racine / str(p.get("fichier", ""))
        if not src.is_file():
            continue
        fmt = detecter_format(src)
        if fmt not in FORMATS_PAGINES:
            sorties.append(f"cote {cote} : rendu sans objet pour le format {fmt} ; pour un traitement de texte, convertir en PDF et coter la conversion.")
            continue
        with fitz.open(src) as doc:
            if a_examiner:
                if cote not in inv:
                    raise SystemExit("--a-examiner exige l'inventaire : lancer d'abord pieces.py inventaire.")
                choix = pages_a_examiner(inv[cote])
            else:
                choix = _plage(pages_spec) if pages_spec else list(range(1, doc.page_count + 1))
            for n in choix:
                if 1 <= n <= doc.page_count:
                    dst = chemin_rendu(racine, cote, p["fichier"], n)
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    doc[n - 1].get_pixmap(dpi=dpi).save(dst)
                    sorties.append(dst.relative_to(racine).as_posix())
    return sorties


# ---------------------------------------------------------------------------------------------------------------
# Validation : sous-ensemble de JSON Schema, puis règles propres aux fiches et à la matrice

def charger_schema(nom: str) -> dict:
    return json.loads((SCHEMAS_DIR / nom).read_text(encoding="utf-8"))


def _est_type(v, t: str) -> bool:
    return {"string": isinstance(v, str), "integer": isinstance(v, int) and not isinstance(v, bool),
            "number": isinstance(v, (int, float)) and not isinstance(v, bool), "boolean": isinstance(v, bool),
            "array": isinstance(v, list), "object": isinstance(v, dict), "null": v is None}[t]


def valider_schema(v, s: dict, racine_schema: dict, chemin: str = "$") -> list[str]:
    """Sous-ensemble de JSON Schema utilisé par references/schemas : $ref, const, enum, type, required, properties,
    items, minItems, minLength, minimum, pattern."""
    if "$ref" in s:
        return valider_schema(v, racine_schema["$defs"][s["$ref"].split("/")[-1]], racine_schema, chemin)
    if "const" in s and v != s["const"]:
        return [f"{chemin} doit valoir {s['const']!r}."]
    if "enum" in s and v not in s["enum"]:
        return [f"{chemin} vaut {v!r} ; valeurs permises : {', '.join(map(str, s['enum']))}."]
    if "type" in s:
        types = s["type"] if isinstance(s["type"], list) else [s["type"]]
        if not any(_est_type(v, t) for t in types):
            return [f"{chemin} : {' ou '.join(types)} attendu, {type(v).__name__} trouvé."]
    err = []
    if isinstance(v, str):
        if len(v.strip()) < s.get("minLength", 0):
            err.append(f"{chemin} est vide.")
        if "pattern" in s and not re.search(s["pattern"], v):
            err.append(f"{chemin} : format attendu {s['pattern']} (valeur {v!r}).")
    if isinstance(v, int) and not isinstance(v, bool) and "minimum" in s and v < s["minimum"]:
        err.append(f"{chemin} doit valoir au moins {s['minimum']}.")
    if isinstance(v, list):
        if len(v) < s.get("minItems", 0):
            err.append(f"{chemin} doit contenir au moins {s['minItems']} élément(s).")
        for i, x in enumerate(v):
            if "items" in s:
                err += valider_schema(x, s["items"], racine_schema, f"{chemin}[{i}]")
    if isinstance(v, dict):
        for k in s.get("required", []):
            if k not in v:
                err.append(f"{chemin}.{k} manquant.")
        for k, sous in s.get("properties", {}).items():
            if k in v:
                err += valider_schema(v[k], sous, racine_schema, f"{chemin}.{k}")
    return err


class Contexte:
    """Bordereau, inventaire, textes extraits et fiches, lus une fois pour une vérification ou un contrôle."""

    def __init__(self, racine: Path):
        self.racine = racine
        self.bordereau = lire_bordereau(racine)
        inv = L.lire_json(racine / INVENTAIRE, {}) or {}
        self.inventaire = {norm_cote(p["cote"]): p for p in inv.get("pieces", []) if p.get("cote") is not None}
        self._textes: dict = {}
        self._fiches: dict = {}
        self._validations: dict = {}

    def textes(self, cote: str) -> dict[int, tuple[str, str]] | None:
        """Pages extraites de la pièce, si l'extraction porte sur la version inscrite au bordereau."""
        cote = norm_cote(cote)
        if cote not in self._textes:
            p = self.bordereau.get(cote)
            res = None
            if p:
                lu = lire_extraction(chemin_extraction(self.racine, cote, p.get("fichier", "")))
                if lu and lu[0].get("sha256") == p.get("sha256"):
                    res = lu[1]
            self._textes[cote] = res
        return self._textes[cote]

    def fiche(self, cote: str) -> dict | None:
        cote = norm_cote(cote)
        if cote not in self._fiches:
            self._fiches[cote] = L.lire_json(chemin_fiche(self.racine, cote))
        return self._fiches[cote]

    def fiche_a_jour(self, cote: str) -> bool:
        f, p = self.fiche(cote), self.bordereau.get(norm_cote(cote))
        return bool(f and p and f.get("sha256") == p.get("sha256"))

    def validation(self, cote: str) -> tuple[list[str], list[str], dict]:
        cote = norm_cote(cote)
        if cote not in self._validations:
            self._validations[cote] = valider_fiche(self.racine, cote, ctx=self)
        return self._validations[cote]


def verifier_extrait(ctx: Contexte, cote: str, page: int, citation: str, lu_sur: str, vues: set[int]) -> tuple[str, str]:
    """Statut d'un extrait : exact, approche (texte d'OCR), visuel (lu sur l'image, non vérifiable par le texte),
    introuvable ou texte_indisponible ; avec une explication."""
    pages = ctx.textes(cote)
    if pages is None:
        return "texte_indisponible", "aucune extraction à jour de la pièce (pieces.py inventaire)"
    if page not in pages:
        return "introuvable", f"la page {page} n'existe pas dans l'extraction"
    texte, mode = pages[page]
    suite = texte + "\n" + pages.get(page + 1, ("", ""))[0]
    if mode != "sans_texte":
        statut = trouver(citation, suite, approx=mode in ("ocr", "couche_ocr", "texte_partiel_sur_image"))
        if statut:
            return statut, ""
    if lu_sur == "rendu" and page in vues:
        return "visuel", "lu sur le rendu de la page ; vérification par le texte impossible"
    if mode == "sans_texte":
        return "introuvable", f"page {page} sans texte : l'extrait se lit sur le rendu (lu_sur « rendu », page examinée en image)"
    return "introuvable", f"la citation ne se lit pas sur la page {page} (ni au début de la suivante)"


def _ids_references(fiche: dict) -> list[tuple[str, str]]:
    refs = []
    for i, x in enumerate(fiche.get("prouve") or []):
        refs += [(f"prouve[{i}]", e) for e in x.get("extraits") or []]
    for i, x in enumerate(fiche.get("contradictions_internes") or []):
        refs += [(f"contradictions_internes[{i}]", e) for e in x.get("extraits") or []]
    for i, x in enumerate(fiche.get("coherence") or []):
        refs += [(f"coherence[{i}]", e) for e in x.get("extraits") or []]
    for i, x in enumerate(fiche.get("anomalies") or []):
        refs += [(f"anomalies[{i}]", e) for e in x.get("extraits") or []]
    for cle in ("mentions", "documents_mentionnes"):
        for i, x in enumerate(fiche.get(cle) or []):
            if x.get("extrait"):
                refs.append((f"{cle}[{i}]", x["extrait"]))
    dates = fiche.get("dates") or {}
    for cle in ("acte", "envoi", "reception", "connaissance"):
        if isinstance(dates.get(cle), dict) and dates[cle].get("extrait"):
            refs.append((f"dates.{cle}", dates[cle]["extrait"]))
    for i, x in enumerate(dates.get("autres") or []):
        if x.get("extrait"):
            refs.append((f"dates.autres[{i}]", x["extrait"]))
    return refs


def valider_fiche(racine: Path, cote: str, fiche: dict | None = None, ctx: Contexte | None = None) -> tuple[list[str], list[str], dict]:
    """Erreurs (bloquantes), alertes et statut de chaque extrait d'une fiche pieces/analyses/<cote>.json."""
    ctx = ctx or Contexte(racine)
    cote = norm_cote(cote)
    fiche = fiche if fiche is not None else ctx.fiche(cote)
    nom = f"pieces/analyses/{cote}.json"
    if fiche is None:
        return [f"{nom} absent ou illisible."], [], {}
    schema = charger_schema("analyse_piece.v1.schema.json")
    erreurs = [f"{nom} : {e}" for e in valider_schema(fiche, schema, schema)]
    if isinstance(fiche, dict) and fiche.get("analyse_le"):
        quand = L.parse_date(str(fiche["analyse_le"]).replace(" ", "T")[:16])
        if quand is not None and (quand - L.maintenant()).total_seconds() > 3600:
            erreurs.append(f"{nom} : analyse_le ({fiche['analyse_le']}) est postérieur à l'horloge du dossier ; reprendre la date du squelette "
                           "(pieces.py fiche), qui suit l'horloge, même fixée pour un rejeu.")
    alertes: list[str] = []
    statuts: dict = {}
    if not isinstance(fiche, dict):
        return erreurs, alertes, statuts
    p = ctx.bordereau.get(cote)
    if norm_cote(fiche.get("cote", "")) != cote:
        erreurs.append(f"{nom} : la fiche porte la cote {fiche.get('cote')!r}, son nom de fichier la cote {cote}.")
    if p is None:
        erreurs.append(f"{nom} : la cote {cote} n'est pas au bordereau.")
        return erreurs, alertes, statuts
    if fiche.get("sha256") != p.get("sha256"):
        erreurs.append(f"{nom} : fiche périmée, elle porte sur une autre version de la pièce (empreinte {str(fiche.get('sha256'))[:12]}, "
                       f"bordereau {str(p.get('sha256'))[:12]}). Refaire l'analyse.")
    if str(fiche.get("fichier", "")).replace("\\", "/") != str(p.get("fichier", "")).replace("\\", "/"):
        erreurs.append(f"{nom} : fichier {fiche.get('fichier')!r} différent du bordereau ({p.get('fichier')}).")
    inv = ctx.inventaire.get(cote)
    if inv is None or inv.get("sha256") != p.get("sha256"):
        erreurs.append(f"{nom} : inventaire absent ou périmé pour cette pièce (pieces.py inventaire).")
        inv = {}
    lecture = fiche.get("lecture") or {}
    total = lecture.get("pages_total") if isinstance(lecture.get("pages_total"), int) else 0
    if inv.get("pages") and total != inv["pages"]:
        erreurs.append(f"{nom} : lecture.pages_total vaut {total}, la pièce compte {inv['pages']} page(s).")
        total = inv["pages"]
    lues = set(x for x in lecture.get("pages_lues") or [] if isinstance(x, int))
    vues = set(x for x in lecture.get("pages_vues_en_image") or [] if isinstance(x, int))
    manquantes = sorted(set(range(1, total + 1)) - lues)
    if manquantes:
        erreurs.append(f"{nom} : lecture incomplète, page(s) non lue(s) : {manquantes}. Une pièce se lit en entier.")
    a_voir = set(inv.get("pages_sans_texte", [])) | set(inv.get("pages_couche_ocr", [])) | set(inv.get("pages_ocr", []))         | set(inv.get("pages_image_et_texte_partiel", []))
    if sorted(a_voir - vues):
        erreurs.append(f"{nom} : page(s) {sorted(a_voir - vues)} sans texte natif non examinée(s) en image (pieces.py rendre, puis lecture du rendu).")
    if inv.get("format") == "pdf":
        sans_rendu = sorted(n for n in vues if not chemin_rendu(racine, cote, p["fichier"], n).is_file())
        if sans_rendu:
            erreurs.append(f"{nom} : page(s) {sans_rendu} déclarée(s) vue(s) en image sans rendu dans pieces/rendus (pieces.py rendre).")
    # Extraits littéraux.
    extraits = {}
    for x in fiche.get("extraits") or []:
        if not isinstance(x, dict):
            continue
        i = x.get("id")
        if i in extraits:
            erreurs.append(f"{nom} : identifiant d'extrait {i} en double.")
        extraits[i] = x
        pg = x.get("page")
        if not isinstance(pg, int) or (total and not 1 <= pg <= total):
            erreurs.append(f"{nom} : extrait {i}, page {pg} hors de la pièce.")
            continue
        statut, detail = verifier_extrait(ctx, cote, pg, str(x.get("citation", "")), x.get("lu_sur"), vues)
        statuts[i] = statut
        if statut in ("introuvable", "texte_indisponible"):
            erreurs.append(f"{nom} : extrait {i} « {str(x.get('citation', ''))[:90]} » : {detail}.")
        elif statut == "approche":
            alertes.append(f"{nom} : extrait {i} retrouvé seulement de façon approchée dans un texte d'OCR ; le vérifier sur le rendu de la page {pg}.")
        elif statut == "visuel":
            alertes.append(f"{nom} : extrait {i} lu sur l'image de la page {pg}, sans vérification par le texte.")
    for ou, ident in _ids_references(fiche):
        if ident not in extraits:
            erreurs.append(f"{nom} : {ou} renvoie à l'extrait {ident}, absent de la liste des extraits.")
    for i, x in enumerate(fiche.get("prouve") or []):
        cv = x.get("constat_visuel")
        if not x.get("extraits") and not cv:
            erreurs.append(f"{nom} : prouve[{i}] ne s'appuie sur aucun extrait ni constat visuel.")
        if cv and cv.get("page") not in vues:
            erreurs.append(f"{nom} : prouve[{i}], constat visuel sur une page non examinée en image.")
    # Dates : une réception ne précède pas l'acte, ni l'envoi.
    dates = fiche.get("dates") or {}

    def val(cle):
        d = dates.get(cle)
        return L.date_simple(d.get("valeur")) if isinstance(d, dict) else None
    a, e, r = val("acte"), val("envoi"), val("reception")
    signale = any(an.get("type") == "date_incoherente" for an in fiche.get("anomalies") or [])
    for n1, d1, n2, d2 in (("acte", a, "réception", r), ("acte", a, "envoi", e), ("envoi", e, "réception", r)):
        if d1 and d2 and d2 < d1 and not signale:
            erreurs.append(f"{nom} : date de {n2} ({d2}) antérieure à la date d'{n1} ({d1}) sans anomalie « date_incoherente » relevée.")
    # Indices mécaniques examinés un à un.
    examines = {x.get("id") for x in fiche.get("indices_examines") or [] if isinstance(x, dict)}
    attendus = {i["id"] for i in inv.get("indices", [])}
    if attendus - examines:
        details = [f"{i['id']} {i['code']}" for i in inv.get("indices", []) if i["id"] in attendus - examines]
        erreurs.append(f"{nom} : indice(s) mécanique(s) de l'inventaire non examiné(s) : {', '.join(details)}.")
    if examines - attendus and inv:
        alertes.append(f"{nom} : indices_examines cite des identifiants inconnus de l'inventaire : {sorted(examines - attendus)}.")
    # Signature et formulaire : ce qui se voit doit avoir été vu.
    sig = fiche.get("signataire") or {}
    sig_inv = inv.get("signatures") or {}
    if sig.get("mode") == "electronique_avec_certificat" and inv and not sig_inv.get("champs"):
        erreurs.append(f"{nom} : signature électronique déclarée, mais le fichier ne contient aucun champ de signature.")
    if sig_inv.get("champs") and sig.get("mode") != "electronique_avec_certificat":
        alertes.append(f"{nom} : le fichier contient {sig_inv['champs']} champ(s) de signature électronique que la fiche ne décrit pas.")
    if sig.get("mode") in ("manuscrite", "image_de_signature", "cachet_seul", "absente", "illisible"):
        if not vues:
            erreurs.append(f"{nom} : signature déclarée « {sig.get('mode')} » sans aucune page examinée en image.")
        elif isinstance(sig.get("page"), int) and sig["page"] not in vues:
            erreurs.append(f"{nom} : signature décrite en page {sig['page']}, page non examinée en image.")
    for i, cs in enumerate((fiche.get("formulaire") or {}).get("cases") or []):
        if cs.get("vu_sur") == "rendu" and cs.get("page") not in vues:
            erreurs.append(f"{nom} : formulaire.cases[{i}] lue sur le rendu de la page {cs.get('page')}, page non examinée en image.")
        if cs.get("vu_sur") == "champ_pdf" and not (inv.get("formulaire") or {}).get("champs"):
            erreurs.append(f"{nom} : formulaire.cases[{i}] dite lue sur un champ PDF, le fichier n'en contient aucun.")
    retenus = {x.get("id") for x in fiche.get("indices_examines") or [] if isinstance(x, dict) and x.get("conclusion") == "retenu"}
    if any(i["code"] == "cases_de_formulaire" and i["id"] in retenus for i in inv.get("indices", [])) and not (fiche.get("formulaire") or {}).get("cases"):
        erreurs.append(f"{nom} : les cases de formulaire repérées sont retenues, mais la fiche ne relève l'état d'aucune (formulaire.cases).")
    # Recoupements.
    for i, co in enumerate(fiche.get("coherence") or []):
        autre = norm_cote(co.get("cote", ""))
        if autre == cote or autre not in ctx.bordereau:
            erreurs.append(f"{nom} : coherence[{i}] renvoie à la cote {co.get('cote')!r}, absente du bordereau ou identique.")
            continue
        if co.get("relation") == "contredit" and not (co.get("extraits") and co.get("extraits_autre")):
            erreurs.append(f"{nom} : coherence[{i}] : une contradiction se démontre par un extrait de chaque pièce.")
        fa = ctx.fiche(autre)
        if fa is None:
            alertes.append(f"{nom} : coherence[{i}] compare avec la cote {autre}, pas encore analysée.")
        else:
            ids_autre = {x.get("id") for x in fa.get("extraits") or []}
            inconnus = [x for x in co.get("extraits_autre") or [] if x not in ids_autre]
            if inconnus:
                erreurs.append(f"{nom} : coherence[{i}] cite les extraits {inconnus} de la cote {autre}, absents de sa fiche.")
    for i, dm in enumerate(fiche.get("documents_mentionnes") or []):
        if dm.get("au_dossier") and norm_cote(dm.get("cote") or "") not in ctx.bordereau:
            erreurs.append(f"{nom} : documents_mentionnes[{i}] dit au dossier sans cote valide.")
    return erreurs, alertes, statuts


def etat_extraits_fait(ctx: Contexte, fait: dict, cle: str = "extraits") -> dict:
    """Pour un fait de la matrice : extraits conformes à une fiche d'analyse à jour, pièces qui les portent,
    extraits seulement visuels, et problèmes."""
    res = {"valides": [], "pieces": set(), "visuels": 0, "problemes": []}
    for x in fait.get(cle) or []:
        if not isinstance(x, dict):
            res["problemes"].append("extrait mal formé")
            continue
        cote = norm_cote(x.get("cote", ""))
        ref = f"cote {cote} {x.get('extrait')}"
        if cote not in ctx.bordereau:
            res["problemes"].append(f"{ref} : pièce absente du bordereau")
            continue
        fiche = ctx.fiche(cote)
        if fiche is None:
            res["problemes"].append(f"{ref} : pièce jamais analysée (pieces/analyses/{cote}.json absent)")
            continue
        if not ctx.fiche_a_jour(cote):
            res["problemes"].append(f"{ref} : fiche d'analyse périmée (autre version de la pièce)")
            continue
        fx = next((e for e in fiche.get("extraits") or [] if e.get("id") == x.get("extrait")), None)
        if fx is None:
            res["problemes"].append(f"{ref} : extrait absent de la fiche d'analyse")
            continue
        if normaliser(str(fx.get("citation", ""))) != normaliser(str(x.get("citation", ""))):
            res["problemes"].append(f"{ref} : la citation de la matrice diffère de celle de la fiche")
            continue
        if fx.get("page") != x.get("page"):
            res["problemes"].append(f"{ref} : page {x.get('page')} dans la matrice, {fx.get('page')} dans la fiche")
            continue
        _, _, statuts = ctx.validation(cote)
        statut = statuts.get(fx.get("id"))
        if statut not in ("exact", "approche", "visuel"):
            res["problemes"].append(f"{ref} : extrait non retrouvé sur sa page ({statut or 'non vérifié'})")
            continue
        res["valides"].append(x)
        res["pieces"].add(cote)
        res["visuels"] += statut == "visuel"
    return res


def valider_matrice(racine: Path, ctx: Contexte | None = None) -> tuple[list[str], list[str], list[str]]:
    """Erreurs de structure (format 2), problèmes de preuve (extraits non conformes, états non justifiés) et alertes."""
    ctx = ctx or Contexte(racine)
    m = L.lire_json(racine / "preuves/matrice.json")
    if m is None:
        return [], [], ["preuves/matrice.json absent ou illisible."]
    if m.get("version") != 2:
        return [], [], ["preuves/matrice.json au format 1 : aucun fait n'y est rattaché à un extrait littéral ; passer au format 2 (references/schemas/matrice.v2.schema.json)."]
    schema = charger_schema("matrice.v2.schema.json")
    structure = [f"preuves/matrice.json : {e}" for e in valider_schema(m, schema, schema)]
    problemes, alertes = [], []
    ids = Counter(str(f.get("id")) for f in m.get("faits_a_prouver", []) if isinstance(f, dict))
    structure += [f"preuves/matrice.json : identifiant de fait {i} en double." for i, n in ids.items() if n > 1]
    for f in m.get("faits_a_prouver", []):
        if not isinstance(f, dict):
            continue
        fid, etat = f.get("id"), f.get("force_probante")
        if etat == "conteste" and not f.get("contestation"):
            structure.append(f"preuves/matrice.json : fait {fid} contesté sans contestation décrite (par, ou, resume).")
        if etat == "contredit" and not f.get("contre_extraits"):
            structure.append(f"preuves/matrice.json : fait {fid} contredit sans contre-extrait.")
        pieces = {norm_cote(c) for c in f.get("pieces") or []}
        hors = sorted({norm_cote(x.get("cote", "")) for x in (f.get("extraits") or []) + (f.get("contre_extraits") or []) if isinstance(x, dict)} - pieces)
        if hors and etat in FORCES:
            alertes.append(f"preuves/matrice.json : fait {fid}, extraits de pièces absentes de sa liste pieces : {hors}.")
        st = etat_extraits_fait(ctx, f)
        problemes += [f"fait {fid} : {p}" for p in st["problemes"]]
        if etat == "prouve" and not st["valides"]:
            problemes.append(f"fait {fid} dit prouvé sans extrait littéral conforme d'une pièce analysée.")
        if etat == "corrobore" and len(st["pieces"]) < 2:
            problemes.append(f"fait {fid} dit corroboré : il faut des extraits conformes d'au moins deux pièces distinctes ({len(st['pieces'])} trouvée(s)).")
        if etat == "contredit":
            ce = etat_extraits_fait(ctx, f, "contre_extraits")
            problemes += [f"fait {fid}, contre-extrait : {p}" for p in ce["problemes"]]
    return structure, problemes, alertes


# ---------------------------------------------------------------------------------------------------------------
# Contrôle d'une écriture : faits décisifs et pièces citées

def controle_documentaire(racine: Path, ecriture: Path, fiche_acte: dict | None = None, texte: str | None = None) -> list[dict]:
    """Constats au format de gate.py (code, gravite, message). Un fait que l'écriture présente comme décisif doit
    renvoyer, dans la matrice, à un extrait littéral conforme d'une pièce analysée ; sinon BLOQUANT. Une pièce citée
    sans fiche d'analyse à jour donne une ALERTE."""
    import lint_ecriture as LINT
    ctx = Contexte(racine)
    if fiche_acte is None:
        fiche_acte = L.lire_json(racine / "ecritures" / "controle" / f"{ecriture.stem}.fiche.json", {}) or {}
    if texte is None:
        texte = ecriture.read_text(encoding="utf-8")
    matrice = L.lire_json(racine / "preuves/matrice.json", {}) or {}
    faits = {str(f.get("id")): f for f in matrice.get("faits_a_prouver", []) if isinstance(f, dict)}
    constats: list[dict] = []

    def c(code, gravite, message, **extra):
        constats.append({"code": code, "gravite": gravite, "message": message, **extra})

    acte = ecriture.stem.split("_v")[0]
    citees = {norm_cote(x) for x in LINT.analyser(texte).pieces_citees}
    decisifs: dict[str, str] = {}
    for i in fiche_acte.get("faits_decisifs") or []:
        decisifs[str(i)] = "fiche de l'acte"
    for f in faits.values():
        if f.get("decisif") is True and (acte in (f.get("actes") or []) or ecriture.stem in (f.get("actes") or [])):
            decisifs.setdefault(str(f.get("id")), "matrice")
    sans_matrice = []
    for bloc in ("conditions", "moyens"):
        for x in fiche_acte.get(bloc) or []:
            for fa in x.get("faits") or []:
                if fa.get("matrice"):
                    decisifs.setdefault(str(fa["matrice"]), f"{bloc} « {x.get('condition') or x.get('intitule')} »")
                else:
                    sans_matrice.append(str(fa.get("fait", "?"))[:60])
    if sans_matrice:
        c("FAIT_HORS_MATRICE", "ALERTE", f"{len(sans_matrice)} fait(s) des conditions ou des moyens sans renvoi à la matrice des preuves "
          f"(champ matrice) : {'; '.join(sans_matrice[:5])}. Un fait sur lequel repose une condition se prouve par un extrait de pièce.")
    fd = (fiche_acte.get("fait_decisif") or "").strip()
    if fd and not fiche_acte.get("faits_decisifs"):
        proches = sorted(faits.values(), key=lambda f: -LINT.recouvrement(fd, str(f.get("fait", ""))))[:3]
        pistes = [f"{f.get('id')} « {str(f.get('fait', ''))[:70]} »" for f in proches if LINT.recouvrement(fd, str(f.get("fait", ""))) >= 0.3]
        c("FAIT_DECISIF_NON_RATTACHE", "BLOQUANT", f"Le fait décisif « {fd[:120]} » n'est rattaché à aucune entrée de preuves/matrice.json "
          "(champ faits_decisifs de la fiche, identifiants de la matrice)." + (f" Entrées proches : {', '.join(pistes)}." if pistes else ""))
    for fid, origine in decisifs.items():
        f = faits.get(fid)
        if f is None:
            c("FAIT_DECISIF_HORS_MATRICE", "BLOQUANT", f"Fait {fid} ({origine}) absent de preuves/matrice.json.", fait=fid)
            continue
        libelle = f"Fait décisif {fid} « {str(f.get('fait', ''))[:100]} »"
        st = etat_extraits_fait(ctx, f)
        if not st["valides"]:
            detail = "; ".join(st["problemes"][:4]) or "aucun extrait dans la matrice"
            c("FAIT_DECISIF_SANS_EXTRAIT", "BLOQUANT", f"{libelle} : aucun extrait littéral conforme d'une pièce analysée ({detail}). "
              "Analyser la pièce (skill analyse-documentaire), puis recopier dans la matrice l'extrait de sa fiche.", fait=fid)
            continue
        etat = f.get("force_probante")
        if etat == "allegue":
            c("FAIT_DECISIF_ALLEGUE", "BLOQUANT", f"{libelle} : seulement allégué selon la matrice. Le juge ne tient pas pour établi ce qu'une partie affirme.", fait=fid)
        elif etat == "contredit":
            contre = ", ".join("cote {} {}".format(x.get("cote"), x.get("extrait")) for x in f.get("contre_extraits") or [] if isinstance(x, dict))
            c("FAIT_DECISIF_CONTREDIT", "BLOQUANT", f"{libelle} : une pièce analysée le contredit ({contre or 'contre-extrait non précisé'}). "
              "Répondre à la contre-pièce par une pièce, ou changer de fait décisif.", fait=fid)
        elif etat == "conteste":
            c("FAIT_DECISIF_CONTESTE", "ALERTE", f"{libelle} : contesté ({(f.get('contestation') or {}).get('par', '?')}, "
              f"{(f.get('contestation') or {}).get('ou', '?')}). L'écriture doit répondre à la contestation par pièce.", fait=fid)
        elif etat == "corrobore" and len(st["pieces"]) < 2:
            c("FAIT_DECISIF_SANS_EXTRAIT", "BLOQUANT", f"{libelle} : dit corroboré, mais les extraits conformes ne viennent que de {len(st['pieces'])} pièce(s).", fait=fid)
        elif etat not in FORCES:
            c("FAIT_DECISIF_SANS_EXTRAIT", "BLOQUANT", f"{libelle} : force probante absente ou inconnue ({etat!r}) ; matrice au format 2 exigée.", fait=fid)
        if st["visuels"] == len(st["valides"]):
            c("EXTRAIT_VISUEL_SEUL", "ALERTE", f"{libelle} : ses extraits sont tous lus sur image, sans vérification par le texte ; les relire sur l'original.", fait=fid)
        for cote in sorted(st["pieces"]):
            graves = [a for a in (ctx.fiche(cote) or {}).get("anomalies") or [] if a.get("gravite") == "majeure"]
            if graves:
                c("PIECE_DECISIVE_ANOMALIE", "ALERTE", f"{libelle} repose sur la pièce {cote}, qui porte une anomalie majeure : "
                  f"{str(graves[0].get('description', ''))[:160]}. Préparer la réponse à l'attaque de cette pièce.", fait=fid, cote=cote)
        if not st["pieces"] & citees:
            c("FAIT_DECISIF_PIECE_NON_CITEE", "ALERTE", f"{libelle} : aucune des pièces qui le prouvent ({', '.join(sorted(st['pieces']))}) n'est citée dans l'écriture.", fait=fid)
    for n in sorted(citees, key=lambda x: (len(x), x)):
        if n not in ctx.bordereau:
            continue
        if ctx.fiche(n) is None:
            c("PIECE_CITEE_NON_ANALYSEE", "ALERTE", f"Pièce {n} citée sans fiche d'analyse (pieces/analyses/{n}.json) : ce qu'elle prouve et ce qu'elle ne prouve pas n'a pas été établi.", cote=n)
        elif not ctx.fiche_a_jour(n):
            c("PIECE_CITEE_ANALYSE_PERIMEE", "ALERTE", f"Pièce {n} citée : sa fiche d'analyse porte sur une autre version du fichier.", cote=n)
        else:
            erreurs, _, _ = ctx.validation(n)
            if erreurs:
                c("ANALYSE_INVALIDE", "ALERTE", f"Pièce {n} citée : sa fiche d'analyse a {len(erreurs)} défaut(s) ({erreurs[0][:160]}).", cote=n)
    return constats


# ---------------------------------------------------------------------------------------------------------------
# Chronologie depuis les pièces, et manques

def dates_des_pieces(ctx: Contexte) -> list[dict]:
    res = []
    for cote in ctx.bordereau:
        f = ctx.fiche(cote)
        if not f or not ctx.fiche_a_jour(cote):
            continue
        dates = f.get("dates") or {}
        for nature in ("acte", "envoi", "reception", "connaissance"):
            d = dates.get(nature) or {}
            if isinstance(d, dict) and d.get("valeur"):
                res.append({"date": d["valeur"], "nature": nature, "cote": cote, "extrait": d.get("extrait"),
                            "objet": f"{(f.get('nature') or {}).get('intitule', '')} : {nature}".strip(" :")})
        for d in dates.get("autres") or []:
            if d.get("valeur"):
                res.append({"date": d["valeur"], "nature": "autre", "cote": cote, "extrait": d.get("extrait"), "objet": d.get("objet", "")})
    return sorted(res, key=lambda x: (x["date"], x["cote"]))


def cmd_chronologie(racine: Path) -> dict:
    ctx = Contexte(racine)
    items = dates_des_pieces(ctx)
    evts = (L.lire_json(racine / "chronologie/chronologie.json", {}) or {}).get("evenements", [])
    couverts = {(str(e.get("date", ""))[:10], norm_cote(p)) for e in evts for p in e.get("pieces") or []}
    absents = [x for x in items if (x["date"], x["cote"]) not in couverts]
    sans_piece = [{"id": e.get("id"), "date": e.get("date"), "fait": str(e.get("fait", ""))[:120]} for e in evts if not e.get("pieces")]
    res = {"genere_le": L.horodatage(), "outil": VERSION_OUTIL,
           "portee": "Dates lues dans les fiches d'analyse à jour, chacune avec sa pièce et son extrait. Elle sert à construire et contrôler chronologie/chronologie.json, qu'elle ne remplace pas.",
           "evenements": items, "absents_de_la_chronologie": absents, "chronologie_sans_piece": sans_piece}
    L.ecrire_json(racine / "chronologie/depuis_pieces.json", res)
    return res


def cmd_manques(racine: Path) -> dict:
    import lint_ecriture as LINT
    ctx = Contexte(racine)
    inv = L.lire_json(racine / INVENTAIRE, {}) or {}
    res: dict = {"genere_le": L.horodatage(), "outil": VERSION_OUTIL}
    # Pièces citées dans les écritures et absentes du bordereau.
    citees = []
    for f in sorted((racine / "ecritures").rglob("*.md")) if (racine / "ecritures").is_dir() else []:
        rel = f.relative_to(racine).as_posix()
        if "/controle/" in rel:
            continue
        cotes = sorted({norm_cote(x) for x in LINT.analyser(f.read_text(encoding="utf-8")).pieces_citees} - set(ctx.bordereau), key=lambda x: (len(x), x))
        if cotes:
            citees.append({"ecriture": rel, "cotes": cotes})
    res["pieces_citees_hors_bordereau"] = citees
    res["fichiers_hors_bordereau"] = inv.get("hors_bordereau", [])
    res["pieces_sans_fichier"] = [c for c, p in ctx.bordereau.items() if not (racine / str(p.get("fichier", ""))).is_file()]
    res["pieces_alterees"] = inv.get("alterees", [])
    res["pieces_non_inventoriees"] = sorted(set(ctx.bordereau) - set(ctx.inventaire) - set(res["pieces_sans_fichier"]), key=lambda x: (len(x), x))
    res["pieces_non_analysees"] = sorted((c for c in ctx.bordereau if ctx.fiche(c) is None), key=lambda x: (len(x), x))
    res["analyses_perimees"] = sorted((c for c in ctx.bordereau if ctx.fiche(c) is not None and not ctx.fiche_a_jour(c)), key=lambda x: (len(x), x))
    res["analyses_invalides"] = []
    for c in ctx.bordereau:
        if ctx.fiche(c) is not None and ctx.fiche_a_jour(c):
            erreurs, _, _ = ctx.validation(c)
            if erreurs:
                res["analyses_invalides"].append({"cote": c, "defauts": len(erreurs), "premier": erreurs[0]})
    # Chronologie : faits sans pièce, pièces inconnues, dates absentes de leurs pièces.
    evts = (L.lire_json(racine / "chronologie/chronologie.json", {}) or {}).get("evenements", [])
    res["faits_chronologie_sans_piece"], res["faits_chronologie_piece_inconnue"], res["dates_non_retrouvees"] = [], [], []
    for e in evts:
        ident = {"id": e.get("id"), "date": e.get("date"), "fait": str(e.get("fait", ""))[:120], "statut": e.get("statut")}
        pieces = [norm_cote(p) for p in e.get("pieces") or []]
        if not pieces:
            res["faits_chronologie_sans_piece"].append(ident)
            continue
        inconnues = [p for p in pieces if p not in ctx.bordereau]
        if inconnues:
            res["faits_chronologie_piece_inconnue"].append({**ident, "pieces": inconnues})
        jour = str(e.get("date", ""))[:10]
        trouvees = set()
        for p in pieces:
            trouvees |= {d.get("iso") for d in ((ctx.inventaire.get(p) or {}).get("reperes") or {}).get("dates", [])}
            f = ctx.fiche(p) or {}
            for cle in ("acte", "envoi", "reception", "connaissance"):
                trouvees.add(((f.get("dates") or {}).get(cle) or {}).get("valeur"))
            trouvees |= {d.get("valeur") for d in (f.get("dates") or {}).get("autres") or []}
        if jour and jour not in trouvees and not inconnues:
            res["dates_non_retrouvees"].append({**ident, "pieces": pieces})
    # Matrice : faits sans extrait conforme.
    res["faits_matrice_sans_extrait"] = []
    for f in (L.lire_json(racine / "preuves/matrice.json", {}) or {}).get("faits_a_prouver", []):
        if isinstance(f, dict) and not etat_extraits_fait(ctx, f)["valides"]:
            res["faits_matrice_sans_extrait"].append({"id": f.get("id"), "fait": str(f.get("fait", ""))[:120], "force_probante": f.get("force_probante")})
    # Documents mentionnés absents, pièces jointes de courriels non cotées, preuves à obtenir.
    shas = {p.get("sha256") for p in ctx.bordereau.values()}
    actions = (L.lire_json(racine / "terrain/actions.json", {}) or {}).get("actions", [])
    texte_actions = " ".join(normaliser(f"{a.get('objectif_probatoire', '')} {a.get('action', '')}") for a in actions)
    res["documents_mentionnes_absents"], res["detenus_par_l_adversaire"], res["preuves_a_obtenir_sans_action"] = [], [], []
    for c in ctx.bordereau:
        f = ctx.fiche(c)
        if not f:
            continue
        for d in f.get("documents_mentionnes") or []:
            if not d.get("au_dossier"):
                entree = {"cote_source": c, "designation": d.get("designation"), "page": d.get("page"), "detenteur": d.get("detenteur")}
                res["documents_mentionnes_absents"].append(entree)
                if d.get("detenteur") == "adversaire":
                    res["detenus_par_l_adversaire"].append(entree)
        for pr in f.get("preuves_a_obtenir") or []:
            mots = [m for m in re.findall(r"\w{5,}", normaliser(str(pr.get("objet", ""))))][:6]
            if not mots or sum(m in texte_actions for m in mots) < max(1, len(mots) // 2):
                res["preuves_a_obtenir_sans_action"].append({"cote_source": c, **pr})
    res["pieces_jointes_non_cotees"] = []
    for p in inv.get("pieces", []):
        for pj in ((p.get("courriel") or {}).get("pieces_jointes") or []):
            if pj.get("sha256") not in shas:
                res["pieces_jointes_non_cotees"].append({"cote_source": p.get("cote"), "nom": pj.get("nom"), "sha256": pj.get("sha256")})
    L.ecrire_json(racine / "pieces/manques.json", res)
    return res


def resume_manques(m: dict) -> str:
    libelles = [("pieces_citees_hors_bordereau", "Pièces citées dans une écriture et absentes du bordereau"),
                ("fichiers_hors_bordereau", "Fichiers de pieces/originaux non cotés"), ("pieces_sans_fichier", "Pièces cotées sans fichier"),
                ("pieces_alterees", "Pièces dont l'empreinte a changé"), ("pieces_non_inventoriees", "Pièces non inventoriées"),
                ("pieces_non_analysees", "Pièces jamais analysées"), ("analyses_perimees", "Fiches d'analyse périmées"),
                ("analyses_invalides", "Fiches d'analyse invalides"), ("faits_chronologie_sans_piece", "Faits de la chronologie sans pièce"),
                ("faits_chronologie_piece_inconnue", "Faits de la chronologie renvoyant à une cote inconnue"),
                ("dates_non_retrouvees", "Faits dont la date ne se retrouve dans aucune de leurs pièces"),
                ("faits_matrice_sans_extrait", "Faits de la matrice sans extrait littéral conforme"),
                ("documents_mentionnes_absents", "Documents mentionnés par une pièce et absents du dossier"),
                ("detenus_par_l_adversaire", "dont détenus par l'adversaire"),
                ("pieces_jointes_non_cotees", "Pièces jointes de courriels non cotées"),
                ("preuves_a_obtenir_sans_action", "Preuves à obtenir sans action inscrite à terrain/actions.json")]
    lignes = []
    for cle, lib in libelles:
        v = m.get(cle) or []
        if v:
            lignes.append(f"{lib} : {len(v)}")
            for x in v[:8]:
                lignes.append(f"  - {json.dumps(x, ensure_ascii=False)[:200]}")
    return "\n".join(lignes) if lignes else "Aucun manque relevé."


# ---------------------------------------------------------------------------------------------------------------
# Squelette de fiche

def squelette(racine: Path, cote: str) -> dict:
    ctx = Contexte(racine)
    cote = norm_cote(cote)
    p = ctx.bordereau.get(cote)
    if p is None:
        raise SystemExit(f"Cote {cote} absente du bordereau.")
    inv = ctx.inventaire.get(cote) or {}
    n = inv.get("pages") or 1
    vide_date = {"valeur": None, "extrait": None, "observation": ""}
    return {"schema": SCHEMA_FICHE, "cote": cote, "fichier": p.get("fichier"), "sha256": p.get("sha256"), "analyste": "analyste-documentaire",
            "analyse_le": L.horodatage(),
            "lecture": {"pages_total": n, "pages_lues": [], "pages_vues_en_image": [], "mode": "texte_natif" if len(inv.get("pages_texte", [])) == n else "mixte", "limites": ""},
            "nature": {"type": "", "intitule": "", "forme": ""},
            "auteur": {"nom": "", "qualite": "", "organisme": "", "fondement": ""},
            "signataire": {"nom": "", "qualite": "", "delegation": "", "mode": "non_examinee", "page": None, "observation": ""},
            "destinataires": [], "dates": {"acte": dict(vide_date), "envoi": dict(vide_date), "reception": dict(vide_date), "connaissance": dict(vide_date), "autres": []},
            "canal": {"mode": "inconnu", "numero_envoi": "", "preuve": "", "observation": ""}, "objet": "",
            "extraits": [], "prouve": [], "ne_prouve_pas": [], "mentions": [], "formulaire": {"cases": []},
            "indices_examines": [{"id": i["id"], "conclusion": "", "raison": f"{i['code']} : {i['description']}"} for i in inv.get("indices", [])],
            "anomalies": [], "contradictions_internes": [], "coherence": [], "documents_mentionnes": [], "preuves_a_obtenir": [], "questions_ouvertes": []}


# ---------------------------------------------------------------------------------------------------------------

def racine_ou_sortie() -> Path:
    r = L.trouver_racine(Path.cwd())
    if r is None:
        raise SystemExit("Pas de dossier d'affaire ici (etat/affaire.json introuvable dans ce dossier ou ses parents).")
    return r


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = ap.add_subparsers(dest="cmd", required=True)
    i = s.add_parser("inventaire")
    i.add_argument("--cote", action="append")
    i.add_argument("--refaire", action="store_true", help="relit toutes les pièces, même inchangées depuis le dernier inventaire")
    r = s.add_parser("rendre")
    r.add_argument("--cote", action="append")
    r.add_argument("--pages")
    r.add_argument("--a-examiner", action="store_true")
    r.add_argument("--dpi", type=int, default=150)
    f = s.add_parser("fiche")
    f.add_argument("cote")
    v = s.add_parser("verifier")
    v.add_argument("--cote", action="append")
    s.add_parser("chronologie")
    s.add_parser("manques")
    k = s.add_parser("controle")
    k.add_argument("ecriture")
    a = ap.parse_args(argv)
    if a.cmd == "controle":
        ecriture = Path(a.ecriture).resolve()
        racine = L.trouver_racine(ecriture)
        if racine is None:
            raise SystemExit(f"{ecriture} n'est pas dans un dossier d'affaire.")
        constats = controle_documentaire(racine, ecriture)
        for x in constats:
            print(f"- {x['gravite']} {x['code']} : {x['message']}")
        bloquants = sum(1 for x in constats if x["gravite"] == "BLOQUANT")
        print(f"Contrôle documentaire : {bloquants} bloquant(s), {len(constats) - bloquants} alerte(s).")
        return 1 if bloquants else 0
    racine = racine_ou_sortie()
    if a.cmd == "inventaire":
        inv = cmd_inventaire(racine, a.cote, a.refaire)
        print(resume_inventaire(inv))
        L.ajouter_journal(racine, f"Inventaire documentaire : {len(inv['pieces'])} pièce(s), {sum(len(p.get('indices', [])) for p in inv['pieces'])} indice(s) "
                          f"mécanique(s), {len(inv['hors_bordereau'])} fichier(s) hors bordereau, {len(inv['alterees'])} pièce(s) altérée(s).", "fait")
        return 1 if inv["alterees"] or inv["absentes"] or any(x.get("erreur_lecture") for x in inv["pieces"]) else 0
    if a.cmd == "rendre":
        for x in cmd_rendre(racine, a.cote, a.pages, a.a_examiner, a.dpi):
            print(x)
        return 0
    if a.cmd == "fiche":
        print(json.dumps(squelette(racine, a.cote), ensure_ascii=False, indent=2))
        return 0
    if a.cmd == "verifier":
        ctx = Contexte(racine)
        cotes = [norm_cote(c) for c in a.cote] if a.cote else sorted((c for c in ctx.bordereau if ctx.fiche(c) is not None), key=lambda x: (len(x), x))
        total = 0
        for c in cotes:
            erreurs, alertes, statuts = ctx.validation(c)
            exacts = sum(1 for x in statuts.values() if x == "exact")
            print(f"cote {c} : {len(erreurs)} erreur(s), {len(alertes)} alerte(s), {exacts}/{len(statuts)} extrait(s) retrouvé(s) mot pour mot.")
            for e in erreurs:
                print(f"  ERREUR {e}")
            for x in alertes:
                print(f"  ALERTE {x}")
            total += len(erreurs)
        structure, problemes, alertes = valider_matrice(racine, ctx)
        for e in structure:
            print(f"ERREUR {e}")
        for e in problemes:
            print(f"PREUVE {e}")
        for x in alertes:
            print(f"ALERTE {x}")
        total += len(structure) + len(problemes)
        print(f"{total} défaut(s).")
        return 1 if total else 0
    if a.cmd == "chronologie":
        res = cmd_chronologie(racine)
        print(f"{len(res['evenements'])} date(s) tirée(s) des fiches ; {len(res['absents_de_la_chronologie'])} absente(s) de la chronologie ; "
              f"{len(res['chronologie_sans_piece'])} fait(s) de la chronologie sans pièce. Écrit : chronologie/depuis_pieces.json.")
        for x in res["absents_de_la_chronologie"][:20]:
            print(f"- {x['date']} cote {x['cote']} {x['nature']} : {x['objet']}")
        return 0
    if a.cmd == "manques":
        m = cmd_manques(racine)
        print(resume_manques(m))
        print("Écrit : pieces/manques.json.")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
