"""Tests du registre des lectures (scripts/lectures.py) : capture, intégrité, couverture, citations, portée, fiches de lecture,
contrôle avant dépôt. Réponses synthétiques à la forme de celles de LibreJustice (chaîne JSON dans tool_response, forme
relevée sur un événement PostToolUse réel), aucun appel réseau.

Les tests d'intégration au hook et au contrôle avant dépôt ne s'exécutent qu'une fois appliqué integration/recherche.patch.

Lancer : python -m pytest -q plugins/contentieux/tests/test_recherche.py
"""
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import lectures as LE  # noqa: E402
import lib_affaire as L  # noqa: E402
import pieces as P  # noqa: E402

PY = sys.executable
HOTE = "https://librejustice.fr"
CJA = "code-de-justice-administrative"

R421_1_2016 = ("Sauf en matière de travaux publics, la juridiction ne peut être saisie que par voie de recours formé contre une décision, "
               "et ce, dans les deux mois à partir de la notification ou de la publication de la décision attaquée.")
R421_1_2017 = ("La juridiction ne peut être saisie que par voie de recours formé contre une décision, et ce, dans les deux mois à partir "
               "de la notification ou de la publication de la décision attaquée.\n\nLorsque la requête tend au paiement d'une somme d'argent, "
               "elle n'est recevable qu'après l'intervention de la décision prise par l'administration sur une demande préalablement formée devant elle.")
R421_7 = "Ce même délai est augmenté de deux mois pour les personnes qui demeurent à l'étranger."
VERSIONS_R421_1 = [{"status": "MODIFIE", "valid_from": "2016-01-01", "valid_to": "2016-12-31"},
                   {"status": "MODIFIE", "valid_from": "2017-01-01", "valid_to": "2019-02-09"},
                   {"status": "VIGUEUR", "valid_from": "2020-01-01"}]
SECTION_DELAIS = f"{HOTE}/norm/fr/{CJA}/partie-reglementaire-decrets-en-conseil/livre-iv/titre-ii"


def norme(numero, texte, valid_from, valid_to=None, versions=None, section=SECTION_DELAIS, note=None, code=CJA):
    r = {"code": code, "number": numero, "section": {"label": "Titre II : Les délais", "url": section}, "status": "VIGUEUR" if not valid_to else "MODIFIE",
         "text": texte, "title": f"Article {numero}", "url": f"{HOTE}/norm/fr/{code}/{LE.cle_article(numero)}", "valid_from": valid_from,
         "versions": versions or [{"status": "VIGUEUR", "valid_from": valid_from}]}
    if valid_to:
        r["valid_to"] = valid_to
    if note:
        r["note"] = note
    return r


CE_505796 = {
    "case_chronology": [
        {"current": True, "link_to_next": "POURVOI_CONTRE", "ruling": "Cassation", "solution": "GRANTED", "title": "Conseil d'État, 2 juillet 2026, 505796", "url": f"{HOTE}/decision/AAA"},
        {"current": False, "link_to_next": "APPEL_DE", "ruling": "Rejet", "solution": "DISMISSED", "title": "Cour administrative d'appel de Marseille, 6 mai 2025, 24MA00153", "url": f"{HOTE}/decision/BBB"}],
    "date": "2026-07-02", "docket_numbers": ["505796"], "publication": ["INEDIT_LEBON"], "ruling": "Cassation", "seat": "FR.CE.C2", "solution": "GRANTED",
    "standing": "FINAL", "commentaries": [{"date": "2026-07-02", "kind": "conclusions", "publisher": "ArianeWeb", "url": "https://exemple.invalid/conclusions"}],
    "text": ("Considérant ce qui suit :\n\nAux termes de l'article [R. 811-1-1](https://librejustice.fr/norm/fr/code-de-justice-administrative/r811-1-1/2026-07-02) "
             "du code de justice administrative : « Les tribunaux administratifs statuent en premier et dernier ressort ». Ces dispositions s'appliquent aux recours "
             "introduits entre le 1er décembre 2013 et le 31 août 2022 contre les décisions relatives à l'occupation des sols qu'elles mentionnent portant en tout ou "
             "partie sur le territoire d'une commune lorsque celle-ci figure, à la date du jugement statuant sur le recours, sur la liste annexée au "
             "[décret du 10 mai 2013](https://librejustice.fr/norm/fr/decret-n-2013-392-du-10-mai-2013-relatif-au-champ-d-application-de-la-taxe).\n\n"
             "Aux termes de l'article [L. 822-1](https://librejustice.fr/norm/fr/code-de-justice-administrative/l822-1/2026-07-02) du code de justice administrative, "
             "le pourvoi fait l'objet d'une procédure préalable d'admission.\n\nD E C I D E :\n\nArticle 1er : L'arrêt du 6 mai 2025 de la cour administrative d'appel est annulé."),
    "title": "Conseil d'État, 2e chambre jugeant seule, 2 juillet 2026, 505796", "url": f"{HOTE}/decision/AAA"}
CAA_24MA00153 = {
    "case_chronology": [
        {"current": False, "link_to_next": "POURVOI_CONTRE", "ruling": "Cassation", "solution": "GRANTED", "title": "Conseil d'État, 2 juillet 2026, 505796", "url": f"{HOTE}/decision/AAA"},
        {"current": True, "link_to_next": "APPEL_DE", "ruling": "Rejet", "solution": "DISMISSED", "title": "Cour administrative d'appel de Marseille, 6 mai 2025, 24MA00153", "url": f"{HOTE}/decision/BBB"},
        {"current": False, "ruling": "Rejet", "solution": "DISMISSED", "title": "Tribunal administratif de Marseille, 27 novembre 2023, 2103931", "url": f"{HOTE}/decision/CCC"}],
    "date": "2025-05-06", "docket_numbers": ["24MA00153"], "publication": ["INEDIT_LEBON"], "ruling": "Rejet", "seat": "FR.CAA.MARSEILLE.C1", "solution": "DISMISSED",
    "standing": "QUASHED",
    "text": ("Les règles de distance instaurées par ces dispositions et qui s'imposent tant aux bâtiments d'élevage qu'aux constructions alentours, en application "
             "du principe de réciprocité, ne s'appliquent qu'en présence de bâtiments agricoles régulièrement édifiés et exploités.\n\nD É C I D E :\n\nArticle 1er : La requête est rejetée."),
    "title": "Cour administrative d'appel de Marseille, 1re chambre, 6 mai 2025, 24MA00153", "url": f"{HOTE}/decision/BBB"}
RECHERCHE_ARTICLE = {"hits": [{"docket_numbers": ["499142"], "title": "Conseil d'État, 25 mars 2025, 499142", "url": f"{HOTE}/decision/DDD", "publication": ["INEDIT_LEBON"],
                               "seat": "FR.CE.C1", "ai_summary": "Les permis modificatifs suivent le régime contentieux du permis initial auquel ils se rattachent."},
                              {"docket_numbers": ["505796"], "title": "Conseil d'État, 2 juillet 2026, 505796", "url": f"{HOTE}/decision/AAA"}],
                     "query": "premier et dernier ressort", "total": 2}


def evenement(outil, entree, reponse, en_chaine=True):
    return {"hook_event_name": "PostToolUse", "tool_name": outil, "tool_input": entree, "session_id": "s1", "tool_use_id": "t1",
            "tool_response": json.dumps(reponse, ensure_ascii=False) if en_chaine else reponse}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="recherche-"))
        self.r = self.tmp / "affaire"
        subprocess.run([PY, str(SCRIPTS / "affaire.py"), "init", str(self.r), "--intitule", "Essai", "--client", "Client", "--objectif", "Gagner"],
                       check=True, capture_output=True)
        os.environ["CONTENTIEUX_MAINTENANT"] = "2026-11-19T10:00"

    def tearDown(self):
        os.environ.pop("CONTENTIEUX_MAINTENANT", None)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def capter(self, outil, entree, reponse, **k):
        return LE.capturer(self.r, evenement(outil, entree, reponse, **k))

    def lire_norme(self, numero_, texte, valid_from, valid_to=None, as_of=None, **k):
        e = {"code": k.get("code", CJA), "article": LE.cle_article(numero_)}
        if as_of:
            e["as_of"] = as_of
        return self.capter("mcp__librejustice__get_norm", e, norme(numero_, texte, valid_from, valid_to, **k))

    def ecrire(self, rel, texte):
        p = self.r / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texte, encoding="utf-8")
        return p

    def constats(self, texte, fiche=None, nom="ecritures/brouillons/requete.md"):
        e = self.ecrire(nom, texte)
        res = []
        LE.controler(self.r, e, fiche or {}, texte, lambda code, gravite, message, **x: res.append({"code": code, "gravite": gravite, "message": message, **x}))
        return res


class Capture(Base):
    def test_capture_complete(self):
        os.environ["CONTENTIEUX_MAINTENANT"] = "2017-09-15T10:00"
        chemin = self.lire_norme("R421-1", R421_1_2016, "2016-01-01", "2016-12-31", as_of="2016-12-12", versions=VERSIONS_R421_1)
        doc = json.loads(chemin.read_text(encoding="utf-8"))
        self.assertEqual(chemin.parent, self.r / "recherche" / "lectures")
        self.assertEqual(doc["outil"], "mcp__librejustice__get_norm")
        self.assertEqual(doc["entree"], {"code": CJA, "article": "r421-1", "as_of": "2016-12-12"})
        self.assertTrue(doc["horodatage"].startswith("2017-09-15 10:00"))
        self.assertEqual(doc["horloge_fixee"], "2017-09-15T10:00")
        self.assertEqual(json.loads(doc["reponse_brute"])["text"], R421_1_2016)
        ligne = json.loads((self.r / "recherche/lectures/registre.jsonl").read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(ligne["fichier"], chemin.name)
        self.assertEqual(ligne["sha256"], L.sha256_fichier(chemin))

    def test_outils_non_suivis_ignores(self):
        self.assertIsNone(LE.capturer(self.r, evenement("Read", {"file_path": "x"}, "texte")))
        self.assertIsNone(LE.capturer(self.r, evenement("mcp__hal__search_hal", {"q": "x"}, {})))
        self.assertIsNotNone(LE.capturer(self.r, evenement("mcp__legal_harness__read_document", {"document_id": "d1"}, {"text": "Contenu du document lu."})))

    def test_formes_de_reponse(self):
        blocs = [{"type": "text", "text": json.dumps(norme("R421-7", R421_7, "2015-09-18"))}]
        self.capter("mcp__librejustice__get_norm", {"code": CJA, "article": "r421-7"}, blocs, en_chaine=False)
        reg = LE.Registre(self.r)
        self.assertTrue(reg.article_lu(CJA, "r421-7"))

    def test_capture_modifiee_ou_ecrite_a_la_main(self):
        chemin = self.lire_norme("R421-7", R421_7, "2015-09-18")
        doc = json.loads(chemin.read_text(encoding="utf-8"))
        doc["reponse_brute"] = doc["reponse_brute"].replace("deux mois", "six mois")
        chemin.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        faux = dict(doc, reponse_brute=json.dumps(norme("R421-9", "Texte inventé.", "2015-09-18")))
        (chemin.parent / "20261119T100000_00099_get_norm_fabrique.json").write_text(json.dumps(faux, ensure_ascii=False), encoding="utf-8")
        reg = LE.Registre(self.r)
        self.assertEqual(len(reg.alterations), 2)
        self.assertFalse(reg.article_lu(CJA, "r421-7"))
        self.assertFalse(reg.article_lu(CJA, "r421-9"))
        codes = {k["code"]: k["gravite"] for k in self.constats("Rien à citer.")}
        self.assertEqual(codes.get("REGISTRE_LECTURES_ALTERE"), "BLOQUANT")

    def test_capture_supprimee(self):
        chemin = self.lire_norme("R421-7", R421_7, "2015-09-18")
        chemin.unlink()
        self.assertEqual(LE.Registre(self.r).suppressions, [chemin.name])


class Reperage(unittest.TestCase):
    def test_articles_et_textes(self):
        t = ("Vu l'article R. 421-1 du code de justice administrative et les articles L. 242-1 et L. 242-2 du code des relations entre le public "
             "et l'administration. CJA, art. R. 421-7. L'article 35 du décret n° 2016-1480 du 2 novembre 2016. Les articles 561, 562, 915-2, 954, "
             "alinéas 2 et 3, du code de procédure civile. Article L. 111-3 du code rural et de la pêche maritime. "
             "« L'article R. 600-1 du code de l'urbanisme » est cité seulement entre guillemets.")
        arts = {(a["instrument"], a["article"]) for a in LE.articles_cites(t)}
        attendus = {(CJA, "r421-1"), ("code-des-relations-entre-le-public-et-l-administration", "l242-1"),
                    ("code-des-relations-entre-le-public-et-l-administration", "l242-2"), (CJA, "r421-7"),
                    ("decret-n-2016-1480", "35"), ("code-de-procedure-civile", "561"), ("code-de-procedure-civile", "915-2"),
                    ("code-de-procedure-civile", "954"), ("code-rural", "l111-3")}
        self.assertTrue(attendus <= arts, attendus - arts)
        self.assertNotIn("r600-1", {a for _, a in arts})
        self.assertNotIn("2", {a for _, a in arts})
        arts = {(a["instrument"], a["article"]) for a in LE.articles_cites("Le texte vise ces permis (CJA, art. R. 811-1-1, 1°).")}
        self.assertEqual(arts, {(CJA, "r811-1-1")})

    def test_texte_source_sans_liens(self):
        t = "l'article [L. 822-1](https://librejustice.fr/norm/fr/cja/l822-1) et [L. 441-1 et suivants](https://x/l441-1) (+ [L441-2 — Code](https://x/l441-2), [L441-3 — Code](https://x/l441-3)) du code"
        self.assertEqual(LE.texte_source(t), "l'article L. 822-1 et L. 441-1 et suivants du code")

    def test_compatibilite_des_textes(self):
        self.assertTrue(LE.compatibles("code-rural", "code-rural-et-de-la-peche-maritime"))
        self.assertTrue(LE.compatibles("decret-n-2016-1480-du-2-novembre-2016-portant-modification", "decret-n-2016-1480"))
        self.assertFalse(LE.compatibles("code-civil", "code-de-commerce"))
        self.assertEqual(LE.numero("25-70.017"), LE.numero("2570017"))


class Couverture(Base):
    def test_article_lu_a_la_date_utile(self):
        self.lire_norme("R421-1", R421_1_2016, "2016-01-01", "2016-12-31", as_of="2016-12-12", versions=VERSIONS_R421_1)
        texte = "Date utile : 2016-12-12\n\nL'article R. 421-1 du code de justice administrative n'exigeait pas de décision préalable en matière de travaux publics."
        cv = LE.couverture(self.r, texte)
        a = cv["articles"][0]
        self.assertTrue(a["lu_a_la_date"])
        self.assertTrue(a["date_declaree"])
        self.assertFalse(a["section_lue"])
        self.assertFalse(a["jurisprudence_par_article"])

    def test_article_lu_dans_une_autre_version_bloque(self):
        self.lire_norme("R421-1", R421_1_2017, "2017-01-01", "2019-02-09", versions=VERSIONS_R421_1,
                        note="applicables aux requêtes enregistrées à compter du 1er janvier 2017")
        texte = "L'article R. 421-1 du code de justice administrative impose une décision préalable."
        k = {x["code"]: x for x in self.constats(texte, {"date_droit_applicable": "2016-12-12"})}
        self.assertEqual(k["ARTICLE_NON_LU_A_DATE"]["gravite"], "BLOQUANT")
        cv = LE.couverture(self.r, texte, {"date_droit_applicable": "2016-12-12"})
        self.assertIn("1er janvier 2017", cv["articles"][0]["disposition_transitoire"])

    def test_article_jamais_lu(self):
        k = {x["code"]: x["gravite"] for x in self.constats("Selon l'article L. 242-2 du code des relations entre le public et l'administration, le retrait est possible.")}
        self.assertEqual(k["ARTICLE_NON_LU_A_DATE"], "BLOQUANT")
        k = {x["code"]: x["gravite"] for x in self.constats("Selon l'article 1240, le retrait est possible.")}
        self.assertEqual(k["ARTICLE_NON_LU"], "ALERTE")

    def test_section_renvois_et_jurisprudence_par_article(self):
        texte_811 = ("A l'exception des opérations mentionnées au 5° du I de l'article [R. 311-5](https://librejustice.fr/norm/fr/code-de-justice-administrative/r311-5), "
                     "les tribunaux administratifs statuent en premier et dernier ressort, sur le territoire des communes de l'article "
                     "[232](https://librejustice.fr/norm/fr/code-general-des-impots/232) du code général des impôts.")
        self.lire_norme("R811-1-1", texte_811, "2026-07-01", section=f"{HOTE}/norm/fr/{CJA}/partie-reglementaire/livre-viii/titre-i")
        texte = "L'article R. 811-1-1 du code de justice administrative prive d'appel le jugement."
        a = LE.couverture(self.r, texte)["articles"][0]
        self.assertEqual(a["renvois_non_suivis"], [f"{CJA}|r311-5", "code-general-des-impots|232"])
        codes = {x["code"] for x in self.constats(texte)}
        self.assertTrue({"ARTICLE_SECTION_NON_LUE", "ARTICLE_RENVOIS_NON_SUIVIS", "JURISPRUDENCE_PAR_ARTICLE_NON_CHERCHEE"} <= codes)
        self.capter("mcp__librejustice__get_norm", {"url": f"{HOTE}/norm/fr/{CJA}/partie-reglementaire/livre-viii/titre-i"},
                    {"article_count": 1, "articles": [{"number": "R811-1-1", "text": texte_811, "url": f"{HOTE}/norm/fr/{CJA}/r811-1-1"}],
                     "code": CJA, "title": "Titre Ier : L'appel", "url": f"{HOTE}/norm/fr/{CJA}/partie-reglementaire/livre-viii/titre-i", "versions": []})
        self.lire_norme("R311-5", "Les cours administratives d'appel sont compétentes en premier et dernier ressort.", "2026-07-01")
        self.capter("mcp__librejustice__search_decisions", {"query": "premier et dernier ressort", "legal_article": ["code-de-justice-administrative|R811-1-1"],
                                                           "publication": ["PUBLIE_LEBON", "MENTIONNE_LEBON"]}, RECHERCHE_ARTICLE)
        a = LE.couverture(self.r, texte)["articles"][0]
        self.assertTrue(a["section_lue"])
        self.assertEqual(a["renvois_non_suivis"], ["code-general-des-impots|232"])
        self.assertTrue(a["jurisprudence_publiee"])
        self.assertFalse(a["jurisprudence_toutes"])
        codes = {x["code"] for x in self.constats(texte)}
        self.assertNotIn("ARTICLE_SECTION_NON_LUE", codes)
        self.assertNotIn("JURISPRUDENCE_PAR_ARTICLE_NON_CHERCHEE", codes)
        self.assertNotIn("ARTICLE_NON_LU_A_DATE", codes)

    def test_lecture_par_section_seule(self):
        self.capter("mcp__librejustice__get_norm", {"url": SECTION_DELAIS, "as_of": "2026-11-19"},
                    {"article_count": 2, "articles": [{"number": "R421-1", "text": R421_1_2017, "url": f"{HOTE}/norm/fr/{CJA}/r421-1"},
                                                      {"number": "R421-7", "text": R421_7, "url": f"{HOTE}/norm/fr/{CJA}/r421-7"}],
                     "code": CJA, "title": "Titre II : Les délais", "url": SECTION_DELAIS, "versions": []})
        a = LE.couverture(self.r, "Le délai de l'article R. 421-7 du code de justice administrative s'applique.")["articles"][0]
        self.assertTrue(a["lu"])
        self.assertTrue(a["section_lue"])
        self.assertTrue(a["lu_a_la_date"])


class Decisions(Base):
    def test_decision_non_lue_vue_en_apercu(self):
        self.capter("mcp__librejustice__search_decisions", {"query": "permis modificatif"}, RECHERCHE_ARTICLE)
        k = {x["code"]: x for x in self.constats("Le Conseil d'État l'a jugé (CE, 25 mars 2025, n° 499142).")}
        self.assertEqual(k["DECISION_CITEE_NON_LUE"]["gravite"], "BLOQUANT")
        self.assertIn("aperçu", k["DECISION_CITEE_NON_LUE"]["message"])

    def test_decision_cassee_non_dite_bloque(self):
        self.capter("mcp__librejustice__get_decision", {"url": f"{HOTE}/decision/BBB"}, CAA_24MA00153)
        texte = "La cour administrative d'appel de Marseille juge que la réciprocité suppose un élevage régulier (CAA Marseille, 6 mai 2025, 24MA00153)."
        k = {x["code"]: x for x in self.constats(texte)}
        self.assertEqual(k["DECISION_CITEE_DEFAITE"]["gravite"], "BLOQUANT")
        self.assertIn("505796", k["DECISION_CITEE_DEFAITE"]["message"])
        res = LE.portee(self.r)
        self.assertEqual(res[0]["suite"][0], {"source": "standing", "valeur": "QUASHED"})
        self.assertEqual(res[0]["suite"][1]["numero"], "505796")

    def test_decision_cassee_dite_alerte(self):
        self.capter("mcp__librejustice__get_decision", {"url": f"{HOTE}/decision/BBB"}, CAA_24MA00153)
        self.capter("mcp__librejustice__get_decision", {"url": f"{HOTE}/decision/AAA"}, CE_505796)
        texte = "L'arrêt de la cour (CAA Marseille, 6 mai 2025, 24MA00153) a été annulé par le Conseil d'État (CE, 2 juillet 2026, n° 505796)."
        k = {x["code"]: x["gravite"] for x in self.constats(texte)}
        self.assertEqual(k["DECISION_DEFAITE_SIGNALEE"], "ALERTE")
        self.assertNotIn("DECISION_CITEE_DEFAITE", k)
        self.assertNotIn("DECISION_CITEE_NON_LUE", k)

    def test_numero_de_la_decision_ulterieure_cite_ailleurs_ne_suffit_pas(self):
        self.capter("mcp__librejustice__get_decision", {"url": f"{HOTE}/decision/BBB"}, CAA_24MA00153)
        self.capter("mcp__librejustice__get_decision", {"url": f"{HOTE}/decision/AAA"}, CE_505796)
        texte = ("La liste s'apprécie au jour du jugement (CE, 2 juillet 2026, n° 505796, point 2).\n\n"
                 "La réciprocité cède devant un élevage irrégulier (CAA Marseille, 6 mai 2025, 24MA00153, point 14).")
        self.assertFalse(LE.portee(self.r, texte)[0]["dit_dans_l_ecriture"])
        self.assertEqual({x["code"]: x["gravite"] for x in self.constats(texte)}["DECISION_CITEE_DEFAITE"], "BLOQUANT")

    def test_suite_du_premier_juge_non_defaite_par_un_rejet(self):
        ta = dict(CAA_24MA00153, docket_numbers=["2103931"], standing="NO_KNOWN_REVIEW",
                  case_chronology=[dict(x, current=(i == 2)) for i, x in enumerate(CAA_24MA00153["case_chronology"])])
        self.capter("mcp__librejustice__get_decision", {"url": f"{HOTE}/decision/CCC"}, ta)
        self.assertEqual(LE.suite_defavorable(LE.Registre(self.r).decision("2103931")), [])

    def test_decision_sans_suite_connue(self):
        sans = {k: v for k, v in CE_505796.items() if k not in ("standing", "case_chronology")}
        self.capter("mcp__librejustice__get_decision", {"url": f"{HOTE}/decision/AAA"}, sans)
        k = {x["code"]: x["gravite"] for x in self.constats("Voir CE, 2 juillet 2026, n° 505796.")}
        self.assertEqual(k["DECISION_SUITE_INCONNUE"], "ALERTE")

    def test_numero_propre_ignore(self):
        a = L.lire_json(self.r / "etat/affaire.json")
        a["instances"] = [{"juridiction": "TA", "numero": "2601234", "nature": "fond", "statut": "en_cours"}]
        L.ecrire_json(self.r / "etat/affaire.json", a)
        codes = {x["code"] for x in self.constats("Requête n° 2601234.")}
        self.assertNotIn("DECISION_CITEE_NON_LUE", codes)


class Citations(Base):
    def setUp(self):
        super().setUp()
        self.capter("mcp__librejustice__get_decision", {"url": f"{HOTE}/decision/AAA"}, CE_505796)
        self.capter("mcp__librejustice__search_decisions", {"query": "permis modificatif"}, RECHERCHE_ARTICLE)

    def statuts(self, texte, fiche=None):
        return [x["statut"] for x in LE.verifier_citations(self.r, texte, fiche) if x["statut"] != "trop_courte"]

    def test_exacte_inexacte_introuvable(self):
        texte = ("Le Conseil d'État juge : « Ces dispositions s'appliquent aux recours introduits entre le 1er décembre 2013 et le 31 août 2022 contre les décisions "
                 "relatives à l’occupation des sols qu’elles mentionnent » (CE, 2 juillet 2026, n° 505796, point 2).\n\n"
                 "Il précise : « lorsque celle-ci figure, à la date de délivrance de l'autorisation, sur la liste annexée au décret du 10 mai 2013 » "
                 "(CE, 2 juillet 2026, n° 505796, point 2).\n\n"
                 "Il ajoute : « le permis modificatif relève toujours du droit commun de l'appel » (CE, 2 juillet 2026, n° 505796).")
        res = LE.verifier_citations(self.r, texte)
        self.assertEqual([x["statut"] for x in res], ["exacte", "inexacte", "introuvable"])
        self.assertIn("à la date du jugement statuant sur le recours", res[1]["texte_source"])
        k = {x["code"] for x in self.constats(texte) if x["gravite"] == "BLOQUANT"}
        self.assertIn("CITATION_INTROUVABLE", k)

    def test_liens_et_points_de_suspension(self):
        texte = "« Aux termes de l'article L. 822-1 du code de justice administrative, le pourvoi fait l'objet [...] d'admission. » (CE, 2 juillet 2026, n° 505796)"
        self.assertEqual(self.statuts(texte), ["exacte"])

    def test_apercu_de_recherche_refuse(self):
        texte = "« Les permis modificatifs suivent le régime contentieux du permis initial auquel ils se rattachent » (CE, 25 mars 2025, n° 499142)."
        self.assertEqual(self.statuts(texte), ["apercu"])
        k = {x["code"]: x["gravite"] for x in self.constats(texte)}
        self.assertEqual(k["CITATION_APERCU"], "BLOQUANT")

    def test_source_jamais_lue(self):
        res = LE.verifier_citations(self.r, "« la réciprocité suppose une exploitation régulière et déclarée » (CAA Marseille, 6 mai 2025, 24MA00153).")
        self.assertEqual(res[0]["statut"], "introuvable")
        self.assertIn("jamais été lue", res[0]["detail"])

    def test_mal_attribuee_et_non_attribuee(self):
        self.lire_norme("R421-7", R421_7, "2015-09-18")
        texte = ("Le délai « est augmenté de deux mois pour les personnes qui demeurent à l'étranger » (CE, 2 juillet 2026, n° 505796).\n\n"
                 "Le texte prévoit que « ce même délai est augmenté de deux mois ».\n\nUn auteur écrit que « la réforme a tout changé pour les plaideurs ».")
        self.assertEqual(self.statuts(texte), ["mal_attribuee", "non_attribuee_trouvee", "non_attribuee_introuvable"])
        k = {x["code"]: x["gravite"] for x in self.constats(texte)}
        self.assertEqual(k["CITATION_MAL_ATTRIBUEE"], "ALERTE")
        self.assertEqual(k["CITATION_NON_ATTRIBUEE"], "ALERTE")

    def test_article_cite_dans_une_autre_version(self):
        self.lire_norme("R421-1", R421_1_2016, "2016-01-01", "2016-12-31", as_of="2016-12-12", versions=VERSIONS_R421_1)
        texte = "L'article R. 421-1 du code de justice administrative dispose : « Sauf en matière de travaux publics, la juridiction ne peut être saisie ».\n"
        self.assertEqual(self.statuts(texte, {"date_droit_applicable": "2016-12-12"}), ["exacte"])
        self.assertEqual(self.statuts(texte, {"date_droit_applicable": "2026-11-19"}), ["autre_version"])

    def test_citation_d_une_piece(self):
        (self.r / "pieces/bordereau.json").write_text(json.dumps({"pieces": [{"cote": 3, "fichier": "pieces/originaux/003_lettre.pdf", "sha256": "abc",
                                                                               "description": "lettre"}]}), encoding="utf-8")
        P.ecrire_extraction(P.chemin_extraction(self.r, "3", "pieces/originaux/003_lettre.pdf"), "3", "003_lettre.pdf", "abc",
                            [{"n": 1, "mode": "texte_natif", "texte": "Nous refusons votre demande de rendez-vous\nsans autre motif."}])
        texte = "Le maire écrit : « nous refusons votre demande de rendez-vous sans autre motif » (pièce n° 3).\n\nIl ajoute : « nous accordons le rendez-vous demandé » (pièce n° 3)."
        self.assertEqual(self.statuts(texte), ["exacte", "introuvable"])


class Fiches(Base):
    def setUp(self):
        super().setUp()
        self.l1 = self.lire_norme("R421-1", R421_1_2016, "2016-01-01", "2016-12-31", as_of="2016-12-12", versions=VERSIONS_R421_1).name
        self.capter("mcp__librejustice__get_norm", {"url": SECTION_DELAIS, "as_of": "2016-12-12"},
                    {"article_count": 2, "articles": [{"number": "R421-1", "text": R421_1_2016, "url": f"{HOTE}/norm/fr/{CJA}/r421-1"},
                                                      {"number": "R421-7", "text": R421_7, "url": f"{HOTE}/norm/fr/{CJA}/r421-7"}],
                     "code": CJA, "title": "Titre II : Les délais", "url": SECTION_DELAIS, "versions": []})
        self.d1 = self.capter("mcp__librejustice__get_decision", {"url": f"{HOTE}/decision/BBB"}, CAA_24MA00153).name

    def fiche_norme(self):
        f = LE.squelette(self.r, f"{CJA}|R421-1", "2016-12-12")
        f.update({"lettre": [{"alinea": "1", "extrait": "Sauf en matière de travaux publics, la juridiction ne peut être saisie que par voie de recours formé contre une décision"}],
                  "champ_application": "Toute saisine de la juridiction administrative.",
                  "conditions": {"articulation": "cumulatives", "liste": [{"id": "C1", "enonce": "Une décision préalable.", "extrait": "par voie de recours formé contre une décision"},
                                                                         {"id": "C2", "enonce": "Le délai de deux mois.", "extrait": "dans les deux mois"}]},
                  "effets": "Irrecevabilité de la requête sans décision, hors travaux publics.", "portee_limites": "Version de 2016 seulement."})
        f["exceptions"]["liste"] = [{"article": f"{CJA}|R421-7", "enonce": "Délai augmenté pour l'étranger.", "extrait": "augmenté de deux mois pour les personnes qui demeurent à l'étranger"}]
        return f

    def test_squelette_norme_prerempli(self):
        f = LE.squelette(self.r, f"{CJA}|R421-1", "2016-12-12")
        self.assertEqual(f["id"], f"{CJA}__r421-1__2016-12-12")
        self.assertEqual(f["version"]["valid_from"], "2016-01-01")
        self.assertIn(self.l1, f["lectures"])
        self.assertEqual(LE.chemin_url(f["exceptions"]["section_lue"]), LE.chemin_url(SECTION_DELAIS))

    def test_fiche_norme_exacte_valide(self):
        f = self.fiche_norme()
        erreurs, alertes = LE.valider_fiche(self.r, f["id"], f)
        self.assertEqual(erreurs, [])
        self.assertTrue(any("legal_article" in a for a in alertes))

    def test_paraphrase_refusee(self):
        f = self.fiche_norme()
        f["lettre"][0]["extrait"] = "Hors travaux publics, le juge n'est saisi que contre une décision"
        erreurs, _ = LE.valider_fiche(self.r, f["id"], f)
        self.assertTrue(any("mot pour mot" in e for e in erreurs))

    def test_lecture_inventee_et_version_fausse(self):
        f = self.fiche_norme()
        f["lectures"].append("20261119T100000_00042_get_norm_inexist.json")
        self.assertTrue(any("capture intègre" in e for e in LE.valider_fiche(self.r, f["id"], f)[0]))
        f = self.fiche_norme()
        f["version"]["valid_from"] = "2017-01-01"
        self.assertTrue(any("valid_from" in e for e in LE.valider_fiche(self.r, f["id"], f)[0]))

    def test_fiche_decision(self):
        f = LE.squelette(self.r, "24MA00153")
        self.assertEqual(f["id"], "24ma00153")
        self.assertEqual(f["suite"]["standing"], "QUASHED")
        f.update({"question": "La réciprocité joue-t-elle pour un élevage non déclaré ?",
                  "motif_decisif": {"point": "14", "extrait": "ne s'appliquent qu'en présence de bâtiments agricoles régulièrement édifiés et exploités"},
                  "portee": {"nature": "espece", "raisons": "Arrêt inédit, annulé."}, "limites": "Annulé pour incompétence de la cour."})
        erreurs, _ = LE.valider_fiche(self.r, "24ma00153", f)
        self.assertTrue(any("decisions_contraires" in e for e in erreurs))
        f["suite"]["decisions_contraires"] = ["CE, 2 juillet 2026, n° 505796 : annulation"]
        self.assertEqual(LE.valider_fiche(self.r, "24ma00153", f)[0], [])
        f["suite"]["standing"] = "FINAL"
        self.assertTrue(any("standing" in e for e in LE.valider_fiche(self.r, "24ma00153", f)[0]))


class LigneDeCommande(Base):
    def lancer(self, *args):
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        return subprocess.run([PY, str(SCRIPTS / "lectures.py"), *args], cwd=self.r, capture_output=True, text=True, encoding="utf-8", env=env)

    def test_commandes(self):
        self.capter("mcp__librejustice__get_decision", {"url": f"{HOTE}/decision/BBB"}, CAA_24MA00153)
        self.capter("mcp__librejustice__search_decisions", {"query": "réciprocité élevage", "seat": ["FR.CAA.MARSEILLE"]}, {"hits": [], "total": 0})
        note = self.ecrire("recherche/notes/reciprocite.md", "La cour juge que « ne s'appliquent qu'en présence de bâtiments agricoles "
                                                             "régulièrement édifiés et exploités » (CAA Marseille, 6 mai 2025, 24MA00153).\n")
        p = self.lancer("couverture", str(note))
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertIn("DÉFAITE", p.stdout)
        p = self.lancer("citations", str(note))
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("EXACTE", p.stdout)
        p = self.lancer("portee", str(note))
        self.assertEqual(p.returncode, 1)
        self.assertIn("NE LE DIT PAS", p.stdout)
        p = self.lancer("requetes", "--vides")
        self.assertIn("réciprocité élevage", p.stdout)
        self.assertIn("0 résultat", p.stdout)
        p = self.lancer("fiche", "24MA00153")
        self.assertEqual(json.loads(p.stdout)["nature"], "decision")

    def test_capturer_par_entree_standard(self):
        ev = evenement("mcp__librejustice__get_norm", {"code": CJA, "article": "r421-7"}, norme("R421-7", R421_7, "2015-09-18"))
        ev["cwd"] = str(self.r)
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        p = subprocess.run([PY, str(SCRIPTS / "lectures.py"), "capturer"], input=json.dumps(ev, ensure_ascii=False), capture_output=True, text=True,
                           encoding="utf-8", env=env, cwd=self.tmp)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(LE.Registre(self.r).article_lu(CJA, "r421-7"))


class SansReseau(Base):
    def test_aucun_appel_reseau(self):
        source = (SCRIPTS / "lectures.py").read_text(encoding="utf-8")
        for module in ("socket", "urllib", "http.client", "requests", "httpx", "ftplib", "smtplib"):
            self.assertNotRegex(source, rf"^\s*(import|from)\s+{module}\b", module)
        origine = socket.socket

        def interdit(*a, **k):
            raise AssertionError("connexion réseau tentée")
        socket.socket = interdit
        try:
            self.capter("mcp__librejustice__get_decision", {"url": f"{HOTE}/decision/BBB"}, CAA_24MA00153)
            texte = "« ne s'appliquent qu'en présence de bâtiments agricoles » (24MA00153). Article R. 421-1 du code de justice administrative."
            self.constats(texte)
            LE.squelette(self.r, "24MA00153")
        finally:
            socket.socket = origine


HOOK = (SCRIPTS / "hook.py").read_text(encoding="utf-8")
GATE = (SCRIPTS / "gate.py").read_text(encoding="utf-8")


@unittest.skipUnless("lectures as LECTURES" in HOOK, "integration/recherche.patch non appliqué à hook.py")
class IntegrationHook(Base):
    def hook(self, ev):
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        return subprocess.run([PY, str(SCRIPTS / "hook.py")], input=json.dumps(ev, ensure_ascii=False), capture_output=True, text=True,
                              encoding="utf-8", env=env, cwd=self.r)

    def test_post_tool_capture(self):
        ev = evenement("mcp__librejustice__get_norm", {"code": CJA, "article": "r421-7"}, norme("R421-7", R421_7, "2015-09-18"))
        ev.update({"hook_event_name": "PostToolUse", "cwd": str(self.r)})
        p = self.hook(ev)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(LE.Registre(self.r).article_lu(CJA, "r421-7"))

    def test_conclusions_signalees_et_methode_savante(self):
        """Banc du 20 novembre : conclusions signalées par commentaries mais jamais lues ; études citées sans la méthode de doctrine."""
        dec = {**CE_505796, "commentaries": [{"date": "2026-07-02", "kind": "conclusions", "publisher": "ArianeWeb",
                                              "url": "https://www.conseil-etat.fr/fr/arianeweb/CRP/conclusion/2026-07-02/505796"}]}
        ev = {**evenement("mcp__librejustice__get_decision", {"url": f"{HOTE}/decision/AAA"}, dec), "cwd": str(self.r)}
        texte = json.loads(self.hook(ev).stdout or "{}").get("hookSpecificOutput", {}).get("additionalContext", "")
        self.assertIn("CRP/conclusion/2026-07-02/505796", texte)
        self.assertIn("?download_pdf", texte)
        self.assertTrue(LE.Registre(self.r).decision("505796"))
        sans = {**CE_505796, "commentaries": []}
        self.assertEqual(self.hook({**evenement("mcp__librejustice__get_decision", {"url": f"{HOTE}/decision/AAA"}, sans), "cwd": str(self.r)}).stdout.strip(), "")
        tr = self.tmp / "t.jsonl"
        tr.write_text(json.dumps({"type": "user", "message": {"content": "Contester l'identification"}}), encoding="utf-8")
        savant = {**evenement("mcp__academic_papers__search_crossref", {"query": "eyewitness confidence"}, {"results": []}), "cwd": str(self.r),
                  "transcript_path": str(tr)}
        self.assertIn("recherche-doctrinale", self.hook(savant).stdout)
        tr.write_text("\n".join(json.dumps(x) for x in [{"type": "user", "message": {"content": "Contester"}},
                      {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Skill", "input": {"skill": "contentieux:recherche-doctrinale"}}]}}]),
                      encoding="utf-8")
        self.assertEqual(self.hook(savant).stdout.strip(), "")

    def test_articles_modificatifs_caches_signales(self):
        """Banc du 20 novembre : la vue d'un décret modificatif affiche 3 articles sur 9 ; R. 77-16-1, créé par l'article 5, restait ignoré."""
        url = f"{HOTE}/norm/fr/decret-n-2026-302-du-21-avril-2026-relatif-a-la-simplification-de-la-procedure"
        vue = {"article_count": 9, "title": "Décret n° 2026-302 du 21 avril 2026", "url": url, "versions": [],
               "articles": [{"kind": "article", "number": n, "text": "x", "url": f"{url}/{n}"} for n in ("1", "8", "9")]}
        ev = {**evenement("mcp__librejustice__get_norm", {"url": url}, vue), "cwd": str(self.r)}
        texte = json.loads(self.hook(ev).stdout or "{}").get("hookSpecificOutput", {}).get("additionalContext", "")
        self.assertIn("compte 9 articles", texte)
        for n in ("2", "5", "7"):
            self.assertIn(f"{url}/{n}", texte)
        self.assertNotIn(f"{url}/8", texte)
        complet = {**vue, "article_count": 3}
        self.assertEqual(self.hook({**evenement("mcp__librejustice__get_norm", {"url": url}, complet), "cwd": str(self.r)}).stdout.strip(), "")

    def test_aiguillage_exige_le_skill_de_l_exercice(self):
        """Banc du 20 novembre : les deux pronostics d'urgence faux venaient de sessions sans skill chargé."""
        tr = self.tmp / "aiguillage.jsonl"
        texte = "Oui, très probablement : la condition d'urgence du référé-suspension est remplie."
        lignes = [{"type": "user", "message": {"content": "Urgence ?"}}, {"type": "assistant", "message": {"content": [{"type": "text", "text": texte}]}}]
        tr.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in lignes), encoding="utf-8")
        stop = {"hook_event_name": "Stop", "cwd": str(self.r), "stop_hook_active": False, "transcript_path": str(tr), "last_assistant_message": texte}
        sortie = json.loads(self.hook(stop).stdout or "{}")
        self.assertEqual(sortie.get("decision"), "block")
        self.assertIn("Référé-suspension", sortie.get("reason", ""))
        self.assertIn("Condition principale : urgence", sortie.get("reason", ""))
        self.assertLess(len(sortie.get("reason", "")), 4000)
        lignes.insert(1, {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Skill", "input": {"skill": "contentieux:refere-administratif"}}]}})
        tr.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in lignes), encoding="utf-8")
        # Audit du 23 novembre : le skill de l'exercice ne contient pas le contrat de la fiche ; le charger n'en dispense plus.
        self.assertIn("Référé-suspension", json.loads(self.hook(stop).stdout or "{}").get("reason", ""))
        civil = "Oui. Un référé-provision devant le juge judiciaire (art. 835, alinéa 2, du code de procédure civile) est la voie."
        self.assertIn("Référé-provision et exécution", json.loads(self.hook({**stop, "last_assistant_message": civil}).stdout or "{}").get("reason", ""))
        # Un exercice sans skill propre exige sa fiche, que l'aiguillage nomme.
        cada = "Oui. Saisir la CADA : la demande de communication d'un document administratif (CRPA, art. L. 311-1), puis la formation de jugement."
        plainte = "Non. Porter plainte simple auprès du procureur de la République, puis le recours auprès du procureur général."
        raison = json.loads(self.hook({**stop, "last_assistant_message": plainte}).stdout or "{}").get("reason", "")
        self.assertIn("Plainte simple", raison)
        lignes.insert(1, {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read",
                          "input": {"file_path": "C:/x/skills/mecanique-des-exercices/references/plainte-simple.md"}}]}})
        tr.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in lignes), encoding="utf-8")
        self.assertNotIn("Plainte simple", json.loads(self.hook({**stop, "last_assistant_message": plainte}).stdout or "{}").get("reason", ""))
        self.assertIn("CADA", json.loads(self.hook({**stop, "last_assistant_message": cada}).stdout or "{}").get("reason", ""))
        neutre = "Le délai d'appel est d'un mois à compter de la notification."
        self.assertNotIn("mécanique", json.loads(self.hook({**stop, "last_assistant_message": neutre}).stdout or "{}").get("reason", ""))

    def test_pronostic_de_recours_exige_la_decision_attaquee(self):
        tr = self.tmp / "recours.jsonl"
        texte = "Oui. Le pourvoi en cassation doit aboutir : le moyen de cassation est fondé."
        lignes = [{"type": "user", "message": {"content": "Cassation ?"}},
                  {"type": "assistant", "message": {"content": [{"type": "text", "text": texte}]}}]
        tr.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in lignes), encoding="utf-8")
        stop = {"hook_event_name": "Stop", "cwd": str(self.r), "stop_hook_active": False, "transcript_path": str(tr), "last_assistant_message": texte}
        self.assertIn("la décision attaquée, lue en entier", json.loads(self.hook(stop).stdout or "{}").get("reason", ""))
        lignes.insert(1, {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "mcp__librejustice__get_decision",
                                                                         "input": {"url": f"{HOTE}/decision/CA"}}]}})
        tr.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in lignes), encoding="utf-8")
        self.assertNotIn("Pronostic rendu sans avoir lu", json.loads(self.hook(stop).stdout or "{}").get("reason", ""))

    def test_negociation_exige_la_fiche_du_negociateur(self):
        tr = self.tmp / "nego.jsonl"
        lignes = [{"type": "user", "message": {"content": "Rédige la lettre qui ouvre la négociation avec le GAEC."}},
                  {"type": "user", "isMeta": True, "message": {"content": "voie amiable : negociation-et-persuasion"}},
                  {"type": "assistant", "message": {"content": [{"type": "text", "text": "Monsieur, nous vous proposons..."}]}}]
        tr.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in lignes), encoding="utf-8")
        stop = {"hook_event_name": "Stop", "cwd": str(self.r), "stop_hook_active": False, "transcript_path": str(tr),
                "last_assistant_message": "Monsieur, nous vous proposons..."}
        self.assertIn("contentieux:negociateur", json.loads(self.hook(stop).stdout or "{}").get("reason", ""))
        (self.r / "strategie").mkdir(exist_ok=True)
        (self.r / "strategie" / "negociation_fiche.md").write_text("Fiche.", encoding="utf-8")
        self.assertNotIn("contentieux:negociateur", json.loads(self.hook(stop).stdout or "{}").get("reason", ""))
        # Le seul briefing, qui parle de voie amiable, ne déclenche rien.
        lignes[0] = {"type": "user", "message": {"content": "Quel est le délai d'appel ?"}}
        tr.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in lignes), encoding="utf-8")
        (self.r / "strategie" / "negociation_fiche.md").unlink()
        self.assertNotIn("contentieux:negociateur", json.loads(self.hook(stop).stdout or "{}").get("reason", ""))

    def test_fiche_de_negociation_a_titres_exiges(self):
        """Banc du 21 novembre : une fiche sur deux omettait les relations qui survivront au litige."""
        (self.r / "strategie").mkdir(exist_ok=True)
        fiche = self.r / "strategie" / "negociation_fiche.md"
        ev = {"hook_event_name": "PostToolUse", "tool_name": "Write", "cwd": str(self.r), "tool_input": {"file_path": str(fiche)}}
        fiche.write_text("## La directrice\n- Repli : maintenir la mesure.\n## Ce qui ne sort jamais\n", encoding="utf-8")
        raison = json.loads(self.hook(ev).stdout or "{}").get("reason", "")
        for titre in ("Relations qui survivront", "de son coût", "À reprendre dans la réponse"):
            self.assertIn(titre, raison)
        fiche.write_text("## La directrice\n## Relations qui survivront au litige\n## Ce que l'écrit fait voir à l'adversaire de son coût\n"
                         "## À reprendre dans la réponse\n", encoding="utf-8")
        self.assertNotEqual(json.loads(self.hook(ev).stdout or "{}").get("decision"), "block")

    def test_presomptions_rappelees_a_l_ecriture_du_refere(self):
        """Banc du 21 novembre : une requête sur trois plaidait la privation de traitement sans la présomption d'urgence."""
        acte = self.r / "ecritures" / "brouillons" / "refere_v1.md"
        acte.parent.mkdir(parents=True, exist_ok=True)
        ev = {"hook_event_name": "PostToolUse", "tool_name": "Write", "cwd": str(self.r), "tool_input": {"file_path": str(acte)}}
        acte.write_text("# Requête en référé-suspension (art. L. 521-1 du CJA)\n\nL'agent est privé de tout traitement depuis deux mois.\n",
                        encoding="utf-8")
        self.assertIn("492519", self.hook(ev).stdout)
        acte.write_text("# Requête en référé-suspension (art. L. 521-1 du CJA)\n\nL'urgence est présumée (CE, réf., 27 sept. 2022, n° 467617).\n",
                        encoding="utf-8")
        self.assertNotIn("Présomptions de l'exercice", self.hook(ev).stdout)
        # Un pourvoi contre une ordonnance de tri qui cite l'article L. 521-1 au passage n'engage pas le référé-suspension.
        acte.write_text("# Pourvoi en cassation devant le Conseil d'État (CJA, art. L. 821-1 et R. 821-1)\n\nL'ordonnance de tri rendue "
                        "sur une demande de l'article L. 521-1 n'est susceptible que d'un pourvoi en cassation, par un avocat au Conseil "
                        "d'État.\n", encoding="utf-8")
        self.assertNotIn("Présomptions de l'exercice", self.hook(ev).stdout)

    def test_conclusions_signalees_non_reportables(self):
        """Banc du 20 novembre : « Pas lu : les conclusions… il faut les lire avant de rédiger », alors qu'elles sont à une requête."""
        lien = "https://www.conseil-etat.fr/fr/arianeweb/CRP/conclusion/2026-07-02/505796"
        dec = {**CE_505796, "commentaries": [{"date": "2026-07-02", "kind": "conclusions", "publisher": "ArianeWeb", "url": lien}]}
        self.hook({**evenement("mcp__librejustice__get_decision", {"url": f"{HOTE}/decision/AAA"}, dec), "cwd": str(self.r)})
        tr = self.tmp / "stop.jsonl"
        texte = "Moyen : erreur de droit (CE, n° 505796). Pas lu : les conclusions du rapporteur public, à lire avant de rédiger."
        lignes = [{"type": "user", "message": {"content": "Quel moyen ?"}},
                  {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "mcp__librejustice__get_decision",
                                                                  "input": {"url": f"{HOTE}/decision/AAA"}}]}},
                  {"type": "assistant", "message": {"content": [{"type": "text", "text": texte}]}}]
        tr.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in lignes), encoding="utf-8")
        stop = {"hook_event_name": "Stop", "cwd": str(self.r), "stop_hook_active": False, "transcript_path": str(tr), "last_assistant_message": texte}
        sortie = json.loads(self.hook(stop).stdout or "{}")
        self.assertEqual(sortie.get("decision"), "block")
        self.assertIn(lien + "?download_pdf", sortie.get("reason", ""))
        lignes.insert(2, {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Bash",
                          "input": {"command": f"curl -sL -o c.pdf \"{lien}?download_pdf\""}}]}})
        tr.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in lignes), encoding="utf-8")
        self.assertNotEqual(json.loads(self.hook(stop).stdout or "{}").get("decision"), "block")
        autre = "Moyen : erreur de droit, sur le fondement de l'article L. 112-1. Pas lu : les conclusions d'une autre affaire."
        self.assertNotEqual(json.loads(self.hook({**stop, "last_assistant_message": autre}).stdout or "{}").get("decision"), "block")
        # Formulation réelle, et alertes réunies : un seul blocage par fin de tour, la relance n'étant plus contrôlée.
        del lignes[2]
        tr.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in lignes), encoding="utf-8")
        reel = ("Moyen : erreur de droit (CE, 30 juin 2025, n° 505796), au vu de la pièce 42. À lire : les conclusions des rapporteurs "
                "publics, publiées sur ArianeWeb. Elles diront si l'abandon est formulé expressément. Il faut les lire avant de signer.")
        raison = json.loads(self.hook({**stop, "last_assistant_message": reel}).stdout or "{}").get("reason", "")
        self.assertIn("conclusion/2026-07-02/505796", raison)
        self.assertIn("pièce 42", raison)

    def test_pre_tool_protege_le_registre(self):
        for cible in ("recherche/lectures/20261119T100000_00001_get_norm_x.json", "recherche/lectures/registre.jsonl"):
            ev = {"hook_event_name": "PreToolUse", "tool_name": "Write", "tool_input": {"file_path": str(self.r / cible), "content": "{}"}, "cwd": str(self.r)}
            sortie = json.loads(self.hook(ev).stdout or "{}")
            self.assertEqual(sortie.get("hookSpecificOutput", {}).get("permissionDecision"), "deny", cible)
        ev = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "echo x > recherche/lectures/registre.jsonl"}, "cwd": str(self.r)}
        self.assertEqual(json.loads(self.hook(ev).stdout or "{}").get("hookSpecificOutput", {}).get("permissionDecision"), "deny")

    def test_rappel_du_protocole_au_briefing(self):
        ev = {"hook_event_name": "SessionStart", "source": "startup", "session_id": "s1", "cwd": str(self.r)}
        texte = json.loads(self.hook(ev).stdout or "{}").get("hookSpecificOutput", {}).get("additionalContext", "")
        self.assertIn("recherche-juridique", texte)
        self.assertIn("lectures.py", texte)

    def test_rappel_du_protocole_sur_une_question(self):
        ev = {"hook_event_name": "UserPromptSubmit", "prompt": "Peut-on encore agir ?", "cwd": str(self.r)}
        sortie = json.loads(self.hook(ev).stdout or "{}")
        texte = sortie.get("hookSpecificOutput", {}).get("additionalContext", "")
        self.assertIn("recherche-juridique", texte)
        self.assertIn("legal_article", texte)
        ev["prompt"] = "Rédige le paragraphe du mémoire en défense."
        texte = json.loads(self.hook(ev).stdout or "{}").get("hookSpecificOutput", {}).get("additionalContext", "")
        self.assertIn("prémisses", texte)
        ev["prompt"] = "Merci, à demain."
        self.assertNotIn("recherche-juridique", self.hook(ev).stdout)

    def test_fiche_de_lecture_reservee_au_lecteur(self):
        ev = {"hook_event_name": "PreToolUse", "tool_name": "Write", "tool_input": {"file_path": str(self.r / "recherche/fiches/x.json"), "content": "{}"},
              "cwd": str(self.r)}
        self.assertEqual(json.loads(self.hook(ev).stdout or "{}").get("hookSpecificOutput", {}).get("permissionDecision"), "deny")
        ev["agent_type"] = "contentieux:lecteur-de-texte"
        self.assertNotIn("deny", self.hook(ev).stdout)


@unittest.skipUnless("lectures as LECTURES" in GATE, "integration/recherche.patch non appliqué à gate.py")
class IntegrationGate(Base):
    def test_gate_rapporte_les_constats_de_lecture(self):
        e = self.ecrire("ecritures/brouillons/requete.md", "# Requête\n\nVoir CAA Marseille, 6 mai 2025, 24MA00153, et l'article R. 421-1 du code de justice administrative.\n")
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        p = subprocess.run([PY, str(SCRIPTS / "gate.py"), str(e), "--json"], capture_output=True, text=True, encoding="utf-8", env=env)
        codes = {k["code"] for k in json.loads(p.stdout)["constats"]}
        self.assertTrue({"DECISION_CITEE_NON_LUE", "ARTICLE_NON_LU_A_DATE"} <= codes, codes)


if __name__ == "__main__":
    unittest.main()
