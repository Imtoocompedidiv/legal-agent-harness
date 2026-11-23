"""Tests du bloc d'analyse documentaire (scripts/pieces.py), sur des pièces synthétiques fabriquées ici, sans réseau.

Pièces : une lettre en PDF texte (jour de semaine faux, date inexistante, version antérieure conservée, annotation,
numéro d'envoi S10, montant, document visé et non joint), un PDF image sans couche texte, un formulaire à cases
(champs PDF et cases dessinées), un courriel EML avec pièce jointe, un document Word avec modifications suivies.

Lancer : python -m pytest -q plugins/contentieux/tests/test_documentaire.py
"""
import json
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
import zipfile
from email.message import EmailMessage
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import lib_affaire as L  # noqa: E402
import pieces as P  # noqa: E402

PY = sys.executable

try:
    import fitz  # noqa: F401
    FITZ = True
except ImportError:
    FITZ = False


def ecrire(p: Path, contenu):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(contenu, ensure_ascii=False) if isinstance(contenu, (dict, list)) else contenu, encoding="utf-8")


def fabriquer_pieces(d: Path) -> None:
    import fitz
    d.mkdir(parents=True, exist_ok=True)
    # Lettre : texte natif, métadonnées datées du 10 mars, puis une annotation enregistrée par ajout.
    doc = fitz.open()
    page = doc.new_page()
    lignes = ["COMMUNE DE NULLEPART", "Direction de l'urbanisme", "N/Réf. : URB-2026-114", "",
              "Nullepart, le lundi 12 mars 2026", "", "Objet : refus de permis de construire",
              "Pièce jointe : avis de la commission du 3 mars 2026", "",
              "Votre demande reçue le 31 avril 2026 est rejetée.", "Montant de la taxe : 1 250,00 euros",
              "Envoi recommandé n° RR123456785FR", "",
              "Pour le maire et par délégation,", "Le directeur général des services", "M. Paul Exemple"]
    y = 72
    for ligne in lignes:
        page.insert_text((72, y), ligne, fontname="helv", fontsize=11)
        y += 16
    doc.set_metadata({"author": "Service urbanisme", "creationDate": "D:20260310090000+01'00'", "modDate": "D:20260310090000+01'00'"})
    doc.save(d / "lettre.pdf")
    doc.close()
    doc = fitz.open(d / "lettre.pdf")
    doc[0].add_text_annot((400, 80), "à vérifier")
    doc.saveIncr()
    doc.close()
    # Avis de réception numérisé : une image, aucune couche texte.
    src = fitz.open()
    sp = src.new_page()
    sp.insert_text((72, 100), "AVIS DE RECEPTION - presente le 14/03/2026", fontsize=14)
    png = sp.get_pixmap(dpi=60).tobytes("png")
    img = fitz.open()
    ip = img.new_page(width=sp.rect.width, height=sp.rect.height)
    ip.insert_image(ip.rect, stream=png)
    img.save(d / "scan.pdf")
    img.close()
    src.close()
    # Formulaire : deux cases en champs PDF, deux cases dessinées dont une barrée d'une croix.
    f = fitz.open()
    fp = f.new_page()
    fp.insert_text((72, 72), "Formulaire de demande", fontsize=14)
    for i, (nom, val, lib) in enumerate([("prolongation", True, "Je demande une prolongation"), ("renonciation", False, "Je renonce")]):
        w = fitz.Widget()
        w.field_type = fitz.PDF_WIDGET_TYPE_CHECKBOX
        w.field_name = nom
        w.rect = fitz.Rect(72, 100 + 30 * i, 84, 112 + 30 * i)
        w.field_value = val
        fp.add_widget(w)
        fp.insert_text((92, 110 + 30 * i), lib, fontsize=11)
    for i, (marque, lib) in enumerate([(True, "Recours gracieux exerce"), (False, "Recours hierarchique exerce")]):
        r = fitz.Rect(72, 200 + 30 * i, 82, 210 + 30 * i)
        fp.draw_rect(r, color=(0, 0, 0), width=0.8)
        if marque:
            fp.draw_line(r.tl, r.br, color=(0, 0, 0))
            fp.draw_line(r.tr, r.bl, color=(0, 0, 0))
        fp.insert_text((90, 209 + 30 * i), lib, fontsize=11)
    f.save(d / "formulaire.pdf")
    f.close()
    # Courriel : date annoncée trois jours avant le passage au serveur, adresse de retour d'un autre domaine.
    m = EmailMessage()
    m["Received"] = "from mx.exemple.test by mail.exemple.test; Mon, 16 Mar 2026 10:00:00 +0100"
    m["From"] = "Service <service@exemple.test>"
    m["Return-Path"] = "<rebond@autre-domaine.test>"
    m["To"] = "Destinataire <destinataire@exemple.test>"
    m["Date"] = "Fri, 13 Mar 2026 09:00:00 +0100"
    m["Subject"] = "Convocation"
    m["Message-ID"] = "<abc@exemple.test>"
    m.set_content("Vous êtes convoqué le 20 mars 2026.\nPièce jointe : convocation.\n")
    m.add_attachment(b"%PDF-1.4 convocation synthetique", maintype="application", subtype="pdf", filename="convocation.pdf")
    (d / "message.eml").write_bytes(bytes(m))
    # Document Word : créé par une personne, modifié par une autre, avec une insertion et une suppression suivies.
    with zipfile.ZipFile(d / "note.docx", "w") as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        z.writestr("docProps/core.xml", '<?xml version="1.0"?><cp:coreProperties xmlns:cp="c" xmlns:dc="d" xmlns:dcterms="t">'
                   "<dc:creator>Agent A</dc:creator><cp:lastModifiedBy>Agent B</cp:lastModifiedBy>"
                   '<dcterms:created xsi:type="x">2026-03-01T10:00:00Z</dcterms:created><dcterms:modified xsi:type="x">2026-03-20T10:00:00Z</dcterms:modified>'
                   "<cp:revision>7</cp:revision></cp:coreProperties>")
        z.writestr("word/document.xml", '<?xml version="1.0"?><w:document xmlns:w="w"><w:body>'
                   "<w:p><w:r><w:t>Le dossier est complet depuis le 2 mars 2026.</w:t></w:r></w:p>"
                   '<w:p><w:ins w:author="Agent B" w:date="2026-03-20T09:00:00Z"><w:r><w:t>Il manque une pièce.</w:t></w:r></w:ins>'
                   '<w:del w:author="Agent B" w:date="2026-03-20T09:01:00Z"><w:r><w:delText>Aucune pièce ne manque.</w:delText></w:r></w:del></w:p>'
                   "</w:body></w:document>")


MODELE: dict = {}


def setUpModule():
    """Une affaire synthétique, inventoriée et rendue une seule fois, recopiée ensuite pour chaque test."""
    if not FITZ:
        return
    modele = Path(tempfile.mkdtemp())
    fabriquer_pieces(modele / "source")
    r = modele / "affaire"
    subprocess.run([PY, str(SCRIPTS / "affaire.py"), "init", str(r), "--intitule", "Essai documentaire", "--client", "X",
                    "--objectif", "Obtenir Z"], check=True, capture_output=True)
    for cote, nom, d in ((1, "lettre.pdf", "2026-03-12"), (2, "scan.pdf", "2026-03-14"), (3, "formulaire.pdf", "2026-03-20"),
                         (4, "message.eml", "2026-03-13"), (5, "note.docx", "2026-03-20")):
        subprocess.run([PY, str(SCRIPTS / "affaire.py"), "piece", "ajouter", str(modele / "source" / nom), "--cote", str(cote),
                        "--date", d, "--description", nom], cwd=r, check=True, capture_output=True)
    MODELE["dossier"] = modele
    MODELE["inventaire"] = subprocess.run([PY, str(SCRIPTS / "pieces.py"), "inventaire"], cwd=r, capture_output=True, text=True, encoding="utf-8")
    MODELE["rendu"] = subprocess.run([PY, str(SCRIPTS / "pieces.py"), "rendre", "--a-examiner"], cwd=r, capture_output=True, text=True, encoding="utf-8")


def tearDownModule():
    if MODELE.get("dossier"):
        shutil.rmtree(MODELE["dossier"], ignore_errors=True)


@unittest.skipUnless(FITZ, "PyMuPDF absent")
class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.r = self.tmp / "affaire"
        shutil.copytree(MODELE["dossier"] / "affaire", self.r)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def inv(self, cote):
        return next(p for p in L.lire_json(self.r / "pieces/inventaire.json")["pieces"] if p["cote"] == str(cote))

    def fiche_lettre(self, **modifs) -> dict:
        """Fiche d'analyse complète et exacte de la lettre (cote 1), telle que l'écrirait l'analyste."""
        inv = self.inv(1)
        f = {"schema": "analyse_piece/1", "cote": "1", "fichier": inv["fichier"], "sha256": inv["sha256"], "analyste": "analyste-documentaire",
             "lecture": {"pages_total": 1, "pages_lues": [1], "pages_vues_en_image": [1], "mode": "texte_natif", "limites": "Signature examinée sur le rendu."},
             "nature": {"type": "decision_administrative", "intitule": "Refus de permis de construire", "forme": "numerique_natif"},
             "auteur": {"nom": "", "qualite": "maire", "organisme": "Commune de Nullepart", "fondement": "en-tête, p. 1"},
             "signataire": {"nom": "Paul Exemple", "qualite": "directeur général des services", "delegation": "pour le maire et par délégation ; acte de délégation non produit",
                            "mode": "absente", "page": 1, "observation": "aucune signature ni cachet sur le rendu"},
             "destinataires": [],
             "dates": {"acte": {"valeur": "2026-03-12", "extrait": "E1", "observation": "le 12 mars 2026 était un jeudi"},
                       "envoi": {"valeur": None, "extrait": None, "observation": ""},
                       "reception": {"valeur": None, "extrait": None, "observation": ""},
                       "connaissance": {"valeur": None, "extrait": None, "observation": ""}, "autres": []},
             "canal": {"mode": "lettre_recommandee_avec_ar", "numero_envoi": "RR123456785FR", "preuve": "mention de la lettre", "observation": ""},
             "objet": "Refus de la demande de permis de construire.",
             "extraits": [{"id": "E1", "page": 1, "citation": "Nullepart, le lundi 12 mars 2026", "lu_sur": "texte"},
                          {"id": "E2", "page": 1, "citation": "Votre demande reçue le 31 avril 2026 est rejetée.", "lu_sur": "texte"},
                          {"id": "E3", "page": 1, "citation": "Pièce jointe : avis de la commission […] 2026", "lu_sur": "texte"},
                          {"id": "E4", "page": 1, "citation": "Pour le maire et par délégation,", "lu_sur": "texte"}],
             "prouve": [{"fait": "La commune a rejeté la demande.", "extraits": ["E2"], "portee": "refus exprès"}],
             "ne_prouve_pas": [{"point": "la date de réception de la demande", "raison": "la date écrite n'existe pas"}],
             "indices_examines": [{"id": i["id"], "conclusion": "retenu", "raison": "vu sur la pièce"} for i in inv["indices"]],
             "anomalies": [{"type": "date_impossible", "description": "31 avril 2026", "page": 1, "gravite": "majeure", "origine": "mecanique", "extraits": ["E2"]}],
             "contradictions_internes": [], "coherence": [],
             "documents_mentionnes": [{"designation": "avis de la commission du 3 mars 2026", "page": 1, "extrait": "E3", "au_dossier": False, "cote": None, "detenteur": "adversaire"}],
             "preuves_a_obtenir": [{"objet": "avis de la commission du 3 mars 2026", "detenteur": "adversaire",
                                    "moyens_possibles": ["communication_de_document_administratif"], "raison": "visé par la lettre, non joint"}],
             "questions_ouvertes": []}
        f.update(modifs)
        return f

    def poser_fiche(self, cote, fiche):
        ecrire(self.r / f"pieces/analyses/{cote}.json", fiche)


class TestInventaire(Base):
    def test_inventaire_et_formats(self):
        self.assertEqual(MODELE["inventaire"].returncode, 0, MODELE["inventaire"].stdout + MODELE["inventaire"].stderr)
        self.assertEqual(MODELE["rendu"].returncode, 0, MODELE["rendu"].stderr)
        self.assertEqual([self.inv(c)["format"] for c in range(1, 6)], ["pdf", "pdf", "pdf", "eml", "docx"])
        self.assertTrue(all(self.inv(c)["empreinte_conforme"] for c in range(1, 6)))

    def test_lettre_indices_et_reperes(self):
        p = self.inv(1)
        codes = {i["code"] for i in p["indices"]}
        self.assertTrue({"jour_de_semaine_incoherent", "date_impossible", "date_posterieure_au_fichier", "version_successive", "annotations"} <= codes, codes)
        self.assertNotIn("cases_de_formulaire", codes, "l'icône d'une annotation n'est pas une case de formulaire")
        rp = p["reperes"]
        self.assertEqual([(e["numero"], e["cle_valide"]) for e in rp["envois"]], [("RR123456785FR", True)])
        self.assertIn(1250.0, [m["valeur"] for m in rp["montants"]])
        self.assertTrue(any("par délégation" in a["valeur"] for a in rp["auteurs"]))
        self.assertTrue(any("avis de la commission" in d["valeur"] for d in rp["documents_mentionnes"]))
        rv = p["revisions"]
        self.assertEqual(len(rv), 1)
        self.assertTrue(rv[0]["texte_identique"])
        self.assertTrue((self.r / rv[0]["fichier"]).is_file())

    def test_extraction_par_page(self):
        p = self.inv(1)
        meta, pages = P.lire_extraction(self.r / p["texte"])
        self.assertEqual(meta["sha256"], p["sha256"])
        self.assertIn("31 avril 2026", pages[1][0])
        self.assertEqual(pages[1][1], "texte_natif")

    def test_pdf_image_sans_texte(self):
        p = self.inv(2)
        self.assertEqual(p["pages_sans_texte"], [1])
        self.assertEqual(p["pages_numerisees"], [1])
        self.assertTrue((self.r / "pieces/rendus/002_scan/p001.png").is_file())

    def test_formulaire_a_cases(self):
        form = self.inv(3)["formulaire"]
        self.assertEqual({c["nom"]: c["etat"] for c in form["champs"]}, {"prolongation": "cochee", "renonciation": "vide"})
        etats = {c["libelle_voisin"]: c["etat_probable"] for c in form["cases_dessinees"]}
        self.assertEqual(etats, {"Recours gracieux exerce": "marquee", "Recours hierarchique exerce": "vide"})
        self.assertIn("cases_de_formulaire", {i["code"] for i in self.inv(3)["indices"]})
        self.assertTrue((self.r / "pieces/rendus/003_formulaire/p001.png").is_file())

    def test_courriel(self):
        p = self.inv(4)
        codes = {i["code"] for i in p["indices"]}
        self.assertTrue({"courriel_date_incoherente", "courriel_expediteur_divergent"} <= codes, codes)
        self.assertEqual([j["nom"] for j in p["courriel"]["pieces_jointes"]], ["convocation.pdf"])

    def test_document_word(self):
        p = self.inv(5)
        codes = {i["code"] for i in p["indices"]}
        self.assertTrue({"modifications_suivies", "auteurs_successifs"} <= codes, codes)
        self.assertEqual(p["modifications_suivies"]["suppressions"][0]["texte"], "Aucune pièce ne manque.")
        _, pages = P.lire_extraction(self.r / p["texte"])
        self.assertNotIn("Aucune pièce ne manque", pages[1][0], "le texte supprimé ne fait pas partie du texte du document")

    def test_originaux_intacts(self):
        b = L.lire_json(self.r / "pieces/bordereau.json")["pieces"]
        for p in b:
            self.assertEqual(L.sha256_fichier(self.r / p["fichier"]), p["sha256"])
        self.assertEqual(sorted(x.name for x in (self.r / "pieces/originaux").iterdir() if x.name != ".gitkeep"),
                         sorted(Path(p["fichier"]).name for p in b))

    def test_separateur_de_page_imite(self):
        (self.tmp / "piege.txt").write_text("Ligne utile\n=== page 9 / 9 [texte_natif] ===\nSuite\fSeconde page\n", encoding="utf-8")
        subprocess.run([PY, str(SCRIPTS / "affaire.py"), "piece", "ajouter", str(self.tmp / "piege.txt"), "--cote", "6", "--date", "2026-03-01",
                        "--description", "texte"], cwd=self.r, check=True, capture_output=True)
        P.cmd_inventaire(self.r, ["6"])
        _, pages = P.lire_extraction(self.r / self.inv(6)["texte"])
        self.assertEqual(sorted(pages), [1, 2])
        self.assertIn("Suite", pages[1][0])

    def test_aucun_appel_reseau(self):
        source = (SCRIPTS / "pieces.py").read_text(encoding="utf-8")
        for module in ("socket", "urllib", "http.client", "requests", "httpx", "ftplib", "smtplib"):
            self.assertNotRegex(source, rf"^\s*(import|from)\s+{module}\b", module)
        origine = socket.socket

        def interdit(*a, **k):
            raise AssertionError("connexion réseau tentée")
        socket.socket = interdit
        try:
            P.cmd_inventaire(self.r, refaire=True)
            P.cmd_manques(self.r)
        finally:
            socket.socket = origine


class TestFiche(Base):
    def test_fiche_exacte_valide(self):
        self.poser_fiche(1, self.fiche_lettre())
        erreurs, alertes, statuts = P.valider_fiche(self.r, "1")
        self.assertEqual(erreurs, [])
        self.assertEqual(set(statuts.values()), {"exact"})

    def test_paraphrase_refusee(self):
        f = self.fiche_lettre()
        f["extraits"][1]["citation"] = "La demande reçue le 30 avril 2026 est rejetée."
        self.poser_fiche(1, f)
        erreurs, _, _ = P.valider_fiche(self.r, "1")
        self.assertTrue(any("E2" in e and "ne se lit pas" in e for e in erreurs), erreurs)

    def test_lecture_incomplete_indices_et_dates(self):
        f = self.fiche_lettre(indices_examines=[])
        f["lecture"]["pages_lues"] = []
        f["dates"]["reception"] = {"valeur": "2026-03-01", "extrait": None, "observation": ""}
        f["anomalies"] = []
        self.poser_fiche(1, f)
        texte = " | ".join(P.valider_fiche(self.r, "1")[0])
        self.assertIn("lecture incomplète", texte)
        self.assertIn("non examiné", texte)
        self.assertIn("antérieure à la date d'acte", texte)

    def test_fiche_perimee(self):
        self.poser_fiche(1, self.fiche_lettre(sha256="0" * 64))
        self.assertTrue(any("périmée" in e for e in P.valider_fiche(self.r, "1")[0]))

    def test_page_numerisee_lue_sur_le_rendu(self):
        inv = self.inv(2)
        base = {"schema": "analyse_piece/1", "cote": "2", "fichier": inv["fichier"], "sha256": inv["sha256"],
                "lecture": {"pages_total": 1, "pages_lues": [1], "pages_vues_en_image": [], "mode": "visuel", "limites": "page numérisée"},
                "nature": {"type": "preuve_d_envoi_ou_de_reception", "intitule": "Avis de réception", "forme": "copie"},
                "auteur": {"nom": "", "qualite": "", "organisme": "La Poste", "fondement": "rendu p. 1"},
                "signataire": {"nom": "", "qualite": "", "delegation": "", "mode": "non_examinee", "page": None, "observation": ""},
                "destinataires": [], "dates": {k: {"valeur": None, "extrait": None, "observation": ""} for k in ("acte", "envoi", "reception", "connaissance")},
                "canal": {"mode": "lettre_recommandee_avec_ar", "numero_envoi": "", "preuve": "", "observation": ""},
                "objet": "Avis de réception.", "extraits": [{"id": "E1", "page": 1, "citation": "presente le 14/03/2026", "lu_sur": "texte"}],
                "prouve": [{"fait": "Présentation du pli le 14 mars 2026.", "extraits": ["E1"], "portee": "date de présentation"}],
                "ne_prouve_pas": [{"point": "le contenu du pli", "raison": "un avis de réception ne décrit pas le contenu"}],
                "indices_examines": [], "anomalies": [], "contradictions_internes": [], "coherence": [], "documents_mentionnes": [],
                "preuves_a_obtenir": [], "questions_ouvertes": []}
        base["dates"]["autres"] = []
        self.poser_fiche(2, base)
        erreurs = " | ".join(P.valider_fiche(self.r, "2")[0])
        self.assertIn("non examinée(s) en image", erreurs)
        self.assertIn("sans texte", erreurs)
        base["lecture"]["pages_vues_en_image"] = [1]
        base["extraits"][0]["lu_sur"] = "rendu"
        self.poser_fiche(2, base)
        erreurs, alertes, statuts = P.valider_fiche(self.r, "2")
        self.assertEqual(erreurs, [])
        self.assertEqual(statuts, {"E1": "visuel"})
        self.assertTrue(any("lu sur l'image" in a for a in alertes))

    def test_signature_et_cases_vues(self):
        f = self.fiche_lettre()
        f["lecture"]["pages_vues_en_image"] = []
        self.poser_fiche(1, f)
        self.assertTrue(any("signature déclarée" in e for e in P.valider_fiche(self.r, "1")[0]))

    def test_schema_conforme_a_jsonschema(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema absent")
        schema = P.charger_schema("analyse_piece.v1.schema.json")
        jsonschema.Draft202012Validator.check_schema(schema)
        bonne = self.fiche_lettre()
        mauvaise = self.fiche_lettre(ne_prouve_pas=[])
        mauvaise["signataire"]["mode"] = "inventee"
        for fiche in (bonne, mauvaise):
            ref = sorted(e.message for e in jsonschema.Draft202012Validator(schema).iter_errors(fiche))
            nous = P.valider_schema(fiche, schema, schema)
            self.assertEqual(bool(ref), bool(nous), (ref, nous))
        m = P.charger_schema("matrice.v2.schema.json")
        jsonschema.Draft202012Validator.check_schema(m)


class TestRecherche(unittest.TestCase):
    def test_trouver(self):
        texte = "Le directeur a décidé que la deman-\nde était « irrecevable » ; elle est rejetée.\nVoies et délais : deux mois."
        self.assertEqual(P.trouver("la demande était \"irrecevable\"", texte), "exact")
        self.assertEqual(P.trouver("LE DIRECTEUR a décidé […] elle est rejetée.", texte), "exact")
        self.assertIsNone(P.trouver("elle est acceptée", texte))
        self.assertIsNone(P.trouver("elle est rejetée […] Le directeur", texte), "les segments se lisent dans l'ordre")

    def test_cle_s10(self):
        self.assertTrue(P.cle_s10_valide("123456785"))
        self.assertFalse(P.cle_s10_valide("123456784"))

    def test_dates(self):
        d = {x["brut"]: x for x in P.reperer_dates("le 1er mars 2026, le 29/02/2026, le samedi 14 mars 2026, le 2026-02-30", 1)}
        self.assertEqual(d["1er mars 2026"]["iso"], "2026-03-01")
        self.assertFalse(d["29/02/2026"]["valide"])
        self.assertEqual(d["samedi 14 mars 2026"]["jour_reel"], "samedi")
        self.assertFalse(d["2026-02-30"]["valide"])
        e = {x["brut"]: x for x in P.reperer_dates("infractions des 30 juin, 16 août et 23 décembre 2021 ; pris en charge le 29 août 2022, "
                                                   "reprogrammé le 30 août, puis le jeudi 31 août", 1)}
        self.assertEqual((e["30 juin"]["iso"], e["16 août"]["iso"]), ("2021-06-30", "2021-08-16"))
        self.assertEqual(e["30 août"]["iso"], "2022-08-30")
        self.assertTrue(e["30 août"]["annee_deduite"])
        self.assertEqual(e["jeudi 31 août"]["jour_reel"], "mercredi")


class TestMatriceEtControle(Base):
    ECRITURE = "# Requête\n\n1. La commune a rejeté la demande par la lettre du 12 mars 2026 (pièce 1).\n2. L'avis de réception est produit (pièce 2).\n\nPar ces motifs\n1. Annuler.\n"

    def preparer(self, faits, fiche_acte):
        self.poser_fiche(1, self.fiche_lettre())
        ecrire(self.r / "preuves/matrice.json", {"version": 2, "faits_a_prouver": faits})
        ecrire(self.r / "ecritures/controle/requete.fiche.json", fiche_acte)
        e = self.r / "ecritures/brouillons/requete.md"
        ecrire(e, self.ECRITURE)
        return e

    @staticmethod
    def fait(fid, etat="prouve", citation="Votre demande reçue le 31 avril 2026 est rejetée.", cote="1", extrait="E2", **k):
        f = {"id": fid, "fait": "La commune a rejeté la demande.", "charge": "nous", "pieces": [cote], "force": "forte", "force_probante": etat,
             "extraits": [{"cote": cote, "extrait": extrait, "page": 1, "citation": citation}] if citation else []}
        f.update(k)
        return f

    def codes(self, constats, gravite=None):
        return {c["code"] for c in constats if gravite is None or c["gravite"] == gravite}

    def test_fait_decisif_prouve_par_extrait(self):
        e = self.preparer([self.fait("F1")], {"faits_decisifs": ["F1"]})
        constats = P.controle_documentaire(self.r, e)
        self.assertEqual(self.codes(constats, "BLOQUANT"), set(), constats)
        self.assertIn("PIECE_DECISIVE_ANOMALIE", self.codes(constats), "la lettre porte une anomalie majeure")
        self.assertIn("PIECE_CITEE_NON_ANALYSEE", self.codes(constats), "la pièce 2 est citée sans fiche")
        self.assertEqual(P.valider_matrice(self.r)[:2], ([], []))

    def test_fait_decisif_sans_rattachement_ni_extrait(self):
        e = self.preparer([self.fait("F1"), self.fait("F2", citation=None), self.fait("F3", cote="3", extrait="E1", citation="Je renonce")],
                          {"fait_decisif": "La commune a rejeté la demande"})
        constats = P.controle_documentaire(self.r, e)
        self.assertIn("FAIT_DECISIF_NON_RATTACHE", self.codes(constats, "BLOQUANT"))
        e = self.preparer([self.fait("F1"), self.fait("F2", citation=None), self.fait("F3", cote="3", extrait="E1", citation="Je renonce")],
                          {"faits_decisifs": ["F2", "F3", "F9"]})
        constats = P.controle_documentaire(self.r, e)
        bloquants = [c for c in constats if c["gravite"] == "BLOQUANT"]
        self.assertEqual({(c["code"], c.get("fait")) for c in bloquants},
                         {("FAIT_DECISIF_SANS_EXTRAIT", "F2"), ("FAIT_DECISIF_SANS_EXTRAIT", "F3"), ("FAIT_DECISIF_HORS_MATRICE", "F9")})
        self.assertIn("jamais analysée", next(c["message"] for c in bloquants if c.get("fait") == "F3"))

    def test_citation_de_la_matrice_differente_de_la_fiche(self):
        e = self.preparer([self.fait("F1", citation="Votre demande est rejetée.")], {"faits_decisifs": ["F1"]})
        constats = P.controle_documentaire(self.r, e)
        self.assertIn("FAIT_DECISIF_SANS_EXTRAIT", self.codes(constats, "BLOQUANT"))

    def test_force_probante(self):
        faits = [self.fait("A", "allegue"), self.fait("C", "conteste", contestation={"par": "commune", "ou": "mémoire", "resume": "nie le refus"}),
                 self.fait("D", "contredit", contre_extraits=[{"cote": "1", "extrait": "E1", "page": 1, "citation": "Nullepart, le lundi 12 mars 2026"}]),
                 self.fait("K", "corrobore")]
        e = self.preparer(faits, {"faits_decisifs": ["A", "C", "D", "K"]})
        constats = P.controle_documentaire(self.r, e)
        par_fait = {(c["code"], c.get("fait")) for c in constats}
        self.assertTrue({("FAIT_DECISIF_ALLEGUE", "A"), ("FAIT_DECISIF_CONTESTE", "C"), ("FAIT_DECISIF_CONTREDIT", "D"),
                         ("FAIT_DECISIF_SANS_EXTRAIT", "K")} <= par_fait, par_fait)
        self.assertTrue(any("corroboré" in p for p in P.valider_matrice(self.r)[1]))

    def test_condition_sans_renvoi_a_la_matrice(self):
        e = self.preparer([self.fait("F1")], {"faits_decisifs": ["F1"], "conditions": [{"condition": "urgence", "faits": [{"fait": "examen le 1er mai", "pieces": [1]}]}]})
        self.assertIn("FAIT_HORS_MATRICE", self.codes(P.controle_documentaire(self.r, e), "ALERTE"))

    def test_matrice_format_2_structure(self):
        ecrire(self.r / "preuves/matrice.json", {"version": 2, "faits_a_prouver": [{"id": "X", "fait": "f", "charge": "nous", "pieces": [], "force": "forte", "force_probante": "certain", "extraits": []}]})
        structure, _, _ = P.valider_matrice(self.r)
        self.assertTrue(any("force_probante" in s for s in structure), structure)
        # Le format 2 reste lisible par le contrôle de structure existant (lib_affaire.SCHEMAS).
        ecrire(self.r / "preuves/matrice.json", {"version": 2, "faits_a_prouver": [self.fait_complet()]})
        self.assertEqual(L.valider_fichier(self.r, "preuves/matrice.json"), [])
        self.assertEqual(P.valider_matrice(self.r)[0], [])

    def fait_complet(self):
        return self.fait("F1")

    def test_commande_controle(self):
        e = self.preparer([self.fait("F1", citation=None)], {"faits_decisifs": ["F1"]})
        r = subprocess.run([PY, str(SCRIPTS / "pieces.py"), "controle", str(e)], cwd=self.r, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("FAIT_DECISIF_SANS_EXTRAIT", r.stdout)

    def test_gate_integre(self):
        if "controle_documentaire" not in (SCRIPTS / "gate.py").read_text(encoding="utf-8"):
            self.skipTest("correctif d'intégration non encore appliqué à gate.py (integration/documentaire.md)")
        import gate
        e = self.preparer([self.fait("F1", citation=None)], {"type_acte": "conclusions", "faits_decisifs": ["F1"]})
        codes = {c["code"] for c in gate.controler(e)["constats"] if c["gravite"] == "BLOQUANT"}
        self.assertIn("FAIT_DECISIF_SANS_EXTRAIT", codes)

    def test_hook_valide_les_fiches(self):
        if "pieces/analyses/" not in (SCRIPTS / "hook.py").read_text(encoding="utf-8"):
            self.skipTest("correctif d'intégration non encore appliqué à hook.py (integration/documentaire.md)")
        f = self.fiche_lettre()
        f["extraits"][1]["citation"] = "Texte qui n'est pas dans la pièce."
        self.poser_fiche(1, f)
        ev = {"hook_event_name": "PostToolUse", "cwd": str(self.r), "tool_name": "Write", "tool_input": {"file_path": str(self.r / "pieces/analyses/1.json")}}
        r = subprocess.run([PY, str(SCRIPTS / "hook.py")], input=json.dumps(ev), capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(json.loads(r.stdout)["decision"], "block")

        def avant(rel, agent=""):
            ev = {"hook_event_name": "PreToolUse", "cwd": str(self.r), "tool_name": "Write", "agent_type": agent,
                  "tool_input": {"file_path": str(self.r / rel), "content": "{}"}}
            sortie = subprocess.run([PY, str(SCRIPTS / "hook.py")], input=json.dumps(ev), capture_output=True, text=True, encoding="utf-8").stdout
            return (json.loads(sortie) if sortie.strip() else {}).get("hookSpecificOutput", {}).get("permissionDecision")
        self.assertEqual(avant("pieces/analyses/1.json"), "deny")
        self.assertIsNone(avant("pieces/analyses/1.json", "contentieux:analyste-documentaire"))
        self.assertEqual(avant("pieces/texte/001_lettre.extraction.txt", "contentieux:analyste-documentaire"), "deny")
        self.assertEqual(avant("pieces/inventaire.json"), "deny")


class TestManques(Base):
    def test_manques(self):
        self.poser_fiche(1, self.fiche_lettre())
        ecrire(self.r / "ecritures/brouillons/requete.md", "Voir la pièce 1 et la pièce 9.\n")
        ecrire(self.r / "chronologie/chronologie.json", {"evenements": [
            {"id": "E1", "date": "2026-03-12", "fait": "refus", "pieces": [1], "statut": "prouve"},
            {"id": "E2", "date": "2026-03-15", "fait": "réception du refus", "pieces": [1], "statut": "allegue"},
            {"id": "E3", "date": "2026-03-02", "fait": "dossier complet selon le client", "pieces": [], "statut": "allegue"}]})
        (self.r / "pieces/originaux/099_depose_a_la_main.pdf").write_bytes(b"%PDF-1.4\n%%EOF\n")
        P.cmd_inventaire(self.r)
        m = P.cmd_manques(self.r)
        self.assertEqual(m["pieces_citees_hors_bordereau"], [{"ecriture": "ecritures/brouillons/requete.md", "cotes": ["9"]}])
        self.assertEqual([h["fichier"] for h in m["fichiers_hors_bordereau"]], ["pieces/originaux/099_depose_a_la_main.pdf"])
        self.assertEqual([x["id"] for x in m["faits_chronologie_sans_piece"]], ["E3"])
        self.assertEqual([x["id"] for x in m["dates_non_retrouvees"]], ["E2"])
        self.assertEqual(m["pieces_non_analysees"], ["2", "3", "4", "5"])
        self.assertEqual([d["designation"] for d in m["detenus_par_l_adversaire"]], ["avis de la commission du 3 mars 2026"])
        self.assertEqual([j["nom"] for j in m["pieces_jointes_non_cotees"]], ["convocation.pdf"])
        self.assertEqual(len(m["preuves_a_obtenir_sans_action"]), 1)
        self.assertTrue((self.r / "pieces/manques.json").is_file())
        ch = P.cmd_chronologie(self.r)
        self.assertEqual([(x["date"], x["cote"], x["nature"]) for x in ch["evenements"]], [("2026-03-12", "1", "acte")])
        self.assertEqual(ch["absents_de_la_chronologie"], [])


if __name__ == "__main__":
    unittest.main()
