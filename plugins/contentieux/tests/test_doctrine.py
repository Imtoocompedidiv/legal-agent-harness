"""Tests des fiches de lecture doctrinale (recherche/doctrine/<id>.json) : schéma, règles croisées, contrôle d'une écriture.

Aucun appel réseau. Les conclusions sont synthétiques (décision fictive n° 999999) ; la thèse et la note sont des références publiques
déjà citées par les références du plugin. Aucune référence ne reprend la réponse d'une sonde du banc.
Lancer : python -m pytest -q plugins/contentieux/tests/test_doctrine.py
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN / "scripts"
sys.path.insert(0, str(SCRIPTS))
import doctrine as D  # noqa: E402
import pieces as PIECES  # noqa: E402

PY = sys.executable
DOI_FICTIF = "10.1234/exemple.5678"


def fiche_conclusions() -> dict:
    return {
        "schema": "doctrine/1",
        "id": "concl-exemple-999999",
        "date": "2026-11-19T22:00",
        "question": "La règle nouvelle de computation s'applique-t-elle aux recours administratifs ?",
        "type": "conclusions_rapporteur_public",
        "discipline": "droit",
        "reference": {
            "auteurs": [{"nom": "Exemple", "prenom": "Claire", "qualite": "rapporteure publique (données synthétiques)"}],
            "titre": "Conclusions sur CE, 1er janvier 2030, n° 999999 (décision fictive)",
            "annee": 2030,
            "support": "Conseil d'État, séance fictive",
            "pages": "6 p.",
            "identifiants": {"numero_decision": "CE, 1er janvier 2030, n° 999999",
                             "url": "https://www.conseil-etat.fr/fr/arianeweb/CRP/conclusion/2030-01-01/999999"},
            "verifiee_par": ["librejustice get_decision, champ commentaries", "ArianeWeb, PDF ?download_pdf"],
            "statut_publication": "conclusions_prononcees",
            "version_lue": "PDF ArianeWeb, pagination propre",
        },
        "lecture": {"statut": "texte_integral", "lu_le": "2026-11-19", "acces": "libre", "source_lue": "PDF ArianeWeb converti en texte"},
        "these_de_l_auteur": "La règle nouvelle posée pour le recours contentieux doit s'étendre au recours administratif.",
        "passages": [{"texte": "Nous vous proposons de juger que la règle nouvelle s'applique aux recours administratifs comme aux recours contentieux.",
                      "page": "p. 4"}],
        "solidite": {"niveau": "position_institutionnelle", "autorite": "Rapporteure publique de la formation qui a jugé.",
                     "date_et_actualite": "Conclusions suivies par la décision ; aucune décision contraire postérieure."},
        "usage": {"nature": "lecture_autorisee", "proposition": "Viser le fondement jurisprudentiel retenu par la décision.",
                  "limite": "Les conclusions n'ont pas l'autorité de la décision ; seule la décision fixe la règle."},
        "marqueurs": ["concl. Exemple", "conclusions de Mme Exemple"],
    }


def fiche_these() -> dict:
    return {
        "schema": "doctrine/1",
        "id": "these-leroy-2021",
        "date": "2026-11-19",
        "question": "Quel poids les conclusions et les avis donnent-ils au précédent ?",
        "type": "these",
        "discipline": "droit",
        "reference": {
            "auteurs": [{"nom": "Leroy", "prenom": "Guillaume", "qualite": "docteur en droit privé"}],
            "titre": "La pratique du précédent en droit français : étude à partir des avis de l'avocat général à la Cour de cassation et des "
                     "conclusions du rapporteur public au Conseil d'État",
            "annee": 2021,
            "support": "Thèse de doctorat, Aix-Marseille, dir. F. Rouvière",
            "identifiants": {"nnt": "2021AIXM0456", "ppn": "26206569X", "url": "https://theses.fr/2021AIXM0456"},
            "verifiee_par": ["theses.fr theses_get", "SUDOC nnt=2021AIXM0456"],
            "statut_publication": "these_soutenue",
        },
        "lecture": {"statut": "resume", "lu_le": "2026-11-19", "acces": "non_diffuse", "source_lue": "theses.fr, notice et résumés",
                    "obstacle": "Thèse non diffusée en ligne (theses.fr : accessible non)."},
        "these_de_l_auteur": "Le précédent est une contrainte argumentative omniprésente, qui neutralise la politique jurisprudentielle et la canalise.",
        "solidite": {"niveau": "doctrine_isolee", "autorite": "Thèse soutenue devant un jury de spécialistes.",
                     "date_et_actualite": "Soutenue le 29 novembre 2021."},
        "usage": {"nature": "fondement_theorique", "proposition": "Montrer le poids du précédent dans les écrits des membres des juridictions.",
                  "limite": "Lue sur résumé seulement ; aucune citation du corps de la thèse."},
        "marqueurs": ["Leroy", "2021AIXM0456"],
    }


def fiche_empirique() -> dict:
    return {
        "schema": "doctrine/1",
        "id": "note-ipp-29-prudhommes",
        "date": "2026-11-19",
        "question": "Les décisions des conseils de prud'hommes varient-elles d'une juridiction à l'autre ?",
        "type": "etude_empirique",
        "discipline": "economie",
        "reference": {
            "auteurs": [{"nom": "Breda", "prenom": "Thomas"}, {"nom": "Chevrot-Bianco", "prenom": "Esther"},
                        {"nom": "Desrieux", "prenom": "Claudine"}, {"nom": "Espinosa", "prenom": "Romain"}],
            "titre": "Prud'hommes : peut-on expliquer la disparité des décisions ?",
            "annee": 2017,
            "support": "Les notes de l'IPP, n° 29",
            "pages": "5 p.",
            "identifiants": {"hal": "halshs-02522691"},
            "verifiee_par": ["HAL search_hal", "HAL read_hal_paper"],
            "statut_publication": "publie",
        },
        "lecture": {"statut": "texte_integral", "lu_le": "2026-11-19", "acces": "libre", "source_lue": "PDF HAL halshs-02522691"},
        "these_de_l_auteur": "Les décisions varient fortement entre juridictions ; l'appartenance syndicale des conseillers n'explique pas les issues.",
        "passages": [{"texte": "Les affaires portées devant le bureau de jugement ont en moyenne 72 % de chances d’être résolues par une décision "
                               "favorable au plaignant.", "page": "p. 5"}],
        "solidite": {"niveau": "empirique_limite", "autorite": "Note de l'Institut des politiques publiques, auteurs économistes.",
                     "date_et_actualite": "Données antérieures à la réforme de 2015 et au barème de 2017.",
                     "methode": "Statistiques du ministère de la Justice par juridiction et travaux économétriques des auteurs.",
                     "population": "Les 210 conseils de prud'hommes", "periode": "2004-2014", "taille": "210 juridictions",
                     "replication": "Aucune réplication indépendante recherchée.",
                     "limites": "Statistiques agrégées : l'effet des affaires et celui des juridictions ne sont pas séparés."},
        "usage": {"nature": "donnee_empirique", "proposition": "Situer l'issue habituelle d'une affaire jugée au bureau de jugement.",
                  "limite": "Une moyenne nationale ne dit pas l'issue d'une espèce."},
        "marqueurs": ["note IPP n° 29"],
    }


def codes(doc, nom=None) -> set:
    return {k["code"] for k in D.valider(doc, nom)}


class Schema(unittest.TestCase):
    def test_schema_charge(self):
        s = PIECES.charger_schema(D.SCHEMA)
        self.assertEqual(s["$id"], "doctrine.v1")

    def test_fiches_completes_valides(self):
        for f in (fiche_conclusions(), fiche_these(), fiche_empirique()):
            self.assertEqual(D.valider(f, f["id"]), [], f["id"])

    def test_squelette_suit_la_structure(self):
        sq = D.squelette()
        s = PIECES.charger_schema(D.SCHEMA)
        self.assertEqual(set(s["required"]) - set(sq), set())
        self.assertEqual(set(s["$defs"]["reference"]["required"]) - set(sq["reference"]), set())

    def test_champ_racine_manquant(self):
        f = fiche_these()
        del f["usage"]
        self.assertIn("DOCTRINE_INVALIDE", codes(f))

    def test_statut_de_lecture_hors_enumeration(self):
        f = fiche_these()
        f["lecture"]["statut"] = "survol"
        self.assertIn("DOCTRINE_INVALIDE", codes(f))

    def test_passage_sans_page(self):
        f = fiche_conclusions()
        del f["passages"][0]["page"]
        self.assertIn("DOCTRINE_INVALIDE", codes(f))

    def test_doi_mal_forme(self):
        f = fiche_empirique()
        f["reference"]["identifiants"]["doi"] = "doi:" + DOI_FICTIF
        self.assertIn("DOCTRINE_INVALIDE", codes(f))

    def test_nnt_mal_forme(self):
        f = fiche_these()
        f["reference"]["identifiants"]["nnt"] = "AIXM0456"
        self.assertIn("DOCTRINE_INVALIDE", codes(f))


class Regles(unittest.TestCase):
    def test_id_et_fichier(self):
        self.assertIn("DOCTRINE_ID", codes(fiche_these(), "autre-nom"))

    def test_sans_identifiant(self):
        f = fiche_empirique()
        f["reference"]["identifiants"] = {}
        self.assertIn("DOCTRINE_SANS_IDENTIFIANT", codes(f))

    def test_these_sans_nnt_ni_ppn(self):
        f = fiche_these()
        f["reference"]["identifiants"] = {"url": "https://theses.fr/2021AIXM0456"}
        self.assertIn("DOCTRINE_THESE_SANS_NNT", codes(f))

    def test_conclusions_sans_decision(self):
        f = fiche_conclusions()
        del f["reference"]["identifiants"]["numero_decision"]
        self.assertIn("DOCTRINE_SANS_DECISION", codes(f))

    def test_passage_releve_sur_un_resume(self):
        f = fiche_these()
        f["passages"] = [{"texte": "omniprésence du précédent comme contrainte argumentative", "page": "p. 12"}]
        self.assertIn("DOCTRINE_PASSAGE_NON_LU", codes(f))

    def test_extraits_sans_parties_lues(self):
        f = fiche_conclusions()
        f["lecture"]["statut"] = "extraits"
        f["lecture"]["obstacle"] = "Temps"
        self.assertIn("DOCTRINE_EXTRAITS_NON_PRECISES", codes(f))

    def test_obstacle_non_dit(self):
        f = fiche_these()
        del f["lecture"]["obstacle"]
        self.assertIn("DOCTRINE_OBSTACLE_NON_DIT", codes(f))

    def test_prepublication_sans_recherche_de_la_version_publiee(self):
        f = fiche_empirique()
        f["reference"]["statut_publication"] = "document_de_travail"
        self.assertIn("DOCTRINE_VERSION_PUBLIEE", codes(f))
        f["reference"]["version_publiee"] = {"recherchee": True, "constat": "Recherchée par titre et auteurs, puis par auteurs : aucune."}
        self.assertNotIn("DOCTRINE_VERSION_PUBLIEE", codes(f))

    def test_empirique_sans_population_ni_replication(self):
        f = fiche_empirique()
        del f["solidite"]["population"]
        f["solidite"]["replication"] = " "
        self.assertIn("DOCTRINE_EMPIRIQUE_INCOMPLETE", codes(f))

    def test_expertise_sans_voie_probatoire(self):
        f = fiche_empirique()
        f["type"] = "expertise_technique"
        self.assertIn("DOCTRINE_EXPERTISE_SANS_VOIE", codes(f))
        f["usage"]["voie_probatoire"] = "Demande d'expertise (CPC, art. 232 et s.) avec la mission tirée de la littérature."
        self.assertNotIn("DOCTRINE_EXPERTISE_SANS_VOIE", codes(f))



    def test_marqueur_trop_court(self):
        f = fiche_these()
        f["marqueurs"] = ["Th."]
        self.assertIn("DOCTRINE_MARQUEUR_COURT", codes(f))


class Controle(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.racine = Path(self.tmp.name)
        (self.racine / "etat").mkdir()
        (self.racine / "etat/affaire.json").write_text(json.dumps({"id": "t", "intitule": "t", "client": "c", "objectif": "o"}), encoding="utf-8")
        (self.racine / "ecritures/controle").mkdir(parents=True)
        (self.racine / D.DOSSIER).mkdir(parents=True)
        for f in (fiche_conclusions(), fiche_these(), fiche_empirique()):
            self.poser(f)

    def tearDown(self):
        self.tmp.cleanup()

    def poser(self, f):
        (self.racine / D.DOSSIER / f"{f['id']}.json").write_text(json.dumps(f, ensure_ascii=False), encoding="utf-8")

    def controle(self, texte, fiche=None, juridictionnel=True):
        e = self.racine / "ecritures" / "memoire.md"
        e.write_text(texte, encoding="utf-8")
        out = []
        D.controler(self.racine, e, fiche, lambda code, gravite, message, **x: out.append((code, gravite)), juridictionnel=juridictionnel)
        return out

    def test_citation_lue_et_relevee(self):
        t = ("La rapporteure publique l'a dit sans détour (concl. Exemple sur CE, 1er janvier 2030, n° 999999, p. 4) : « Nous vous proposons "
             "de juger que la règle nouvelle s'applique aux recours administratifs ».")
        self.assertEqual(self.controle(t), [])

    def test_citation_absente_des_passages(self):
        t = "Selon les concl. Exemple, « la règle ancienne demeure applicable aux recours gracieux ».\n"
        self.assertIn(("DOCTRINE_CITATION_INTROUVABLE", "BLOQUANT"), self.controle(t))

    def test_citation_d_une_these_non_lue(self):
        t = "La thèse de M. Leroy établit « l'omniprésence du précédent comme contrainte argumentative » dans les conclusions.\n"
        self.assertIn(("DOCTRINE_CITATION_NON_LUE", "BLOQUANT"), self.controle(t))

    def test_resume_reformule_sans_guillemets(self):
        t = "D'après le résumé de la thèse de M. Leroy (2021AIXM0456), le précédent pèse sur les conclusions et les avis.\n"
        self.assertEqual(self.controle(t), [])

    def test_citation_courte_alerte_seulement(self):
        t = "La thèse de M. Leroy parle de « contrainte argumentative ».\n"
        self.assertIn(("DOCTRINE_CITATION_NON_LUE", "ALERTE"), self.controle(t))

    def test_citation_d_un_texte_dans_une_autre_phrase(self):
        t = ("La thèse de M. Leroy analyse cette pratique. L'article 6 § 1 de la Convention garantit le droit d'être entendu "
             "« dans un délai raisonnable, par un tribunal indépendant et impartial ».\n")
        self.assertEqual(self.controle(t), [])

    def test_citation_trouvee_au_registre_des_sources(self):
        (self.racine / "etat/sources.json").write_text(json.dumps({"sources": [{
            "id": "S1", "type": "decision", "reference": "CE, 1er janvier 2030, n° 999999 (fictive)", "lu_en_entier": True,
            "passages": [{"citation": "Il en va de même pour apprécier si un recours administratif a pour effet de conserver ce délai.",
                          "point": "2"}]}]}, ensure_ascii=False), encoding="utf-8")
        t = ("Suivant les concl. Exemple, le Conseil d'État a jugé qu'« Il en va de même pour apprécier si un recours administratif a pour "
             "effet de conserver ce délai ».\n")
        self.assertEqual(self.controle(t), [])

    def test_doctrine_hors_fiche(self):
        t = "La chronique publiée à la RFDA 2019, p. 100, annonçait la solution.\n"
        self.assertIn(("DOCTRINE_HORS_FICHE", "BLOQUANT"), self.controle(t))

    def test_doi_hors_fiche(self):
        t = f"Une étude l'établit (doi {DOI_FICTIF}).\n"
        self.assertIn("DOCTRINE_HORS_FICHE", {k for k, _ in self.controle(t)})

    def test_abreviations_ne_coupent_pas_la_phrase(self):
        t = "Comme le relève Mme Exemple, rapporteure publique, dans ses conclusions (concl. Exemple, p. 3), la règle ancienne est isolée.\n"
        self.assertEqual(self.controle(t), [])

    def test_doctrine_declaree_sans_fiche(self):
        out = self.controle("Texte sans doctrine.\n", {"doctrine": ["these-inconnue"]})
        self.assertIn(("DOCTRINE_SANS_FICHE", "BLOQUANT"), out)

    def test_fiche_citee_invalide(self):
        f = fiche_these()
        del f["lecture"]["obstacle"]
        self.poser(f)
        out = self.controle("Voir la thèse de M. Leroy.\n")
        self.assertIn(("DOCTRINE_FICHE_INVALIDE", "BLOQUANT"), out)

    def test_doctrine_seule_pour_un_moyen(self):
        (self.racine / "etat/sources.json").write_text(json.dumps({"sources": [
            {"id": "S1", "type": "doctrine", "reference": "Leroy 2021", "lu_en_entier": True},
            {"id": "S2", "type": "decision", "reference": "CE 999999 (fictive)", "lu_en_entier": True}]}), encoding="utf-8")
        fiche = {"moyens": [{"intitule": "Erreur de droit", "sources": ["S1"]}, {"intitule": "Autre", "sources": ["S1", "S2"]}]}
        out = self.controle("Texte.\n", fiche)
        self.assertEqual([k for k in out if k[0] == "DOCTRINE_SEULE_POUR_REGLE"], [("DOCTRINE_SEULE_POUR_REGLE", "BLOQUANT")])

    def test_empirique_sans_periode_dans_la_phrase(self):
        out = self.controle("Les prud'hommes donnent le plus souvent raison au demandeur (note IPP n° 29).\n")
        self.assertIn(("DOCTRINE_EMPIRIQUE_SANS_POPULATION", "ALERTE"), out)
        self.assertIn(("DOCTRINE_EMPIRIQUE_FRAGILE", "ALERTE"), out)
        out = self.controle("Dans les 210 conseils de prud'hommes, de 2004 à 2014, la plupart des affaires jugées ont donné raison au "
                            "demandeur (note IPP n° 29).\n")
        self.assertNotIn(("DOCTRINE_EMPIRIQUE_SANS_POPULATION", "ALERTE"), out)

    def test_courrier_non_juridictionnel_en_alerte(self):
        t = "La chronique publiée à la RFDA 2019, p. 100, annonçait la solution.\n"
        self.assertEqual({g for _, g in self.controle(t, juridictionnel=False)}, {"ALERTE"})

    def test_ligne_de_commande(self):
        p = subprocess.run([PY, str(SCRIPTS / "doctrine.py"), "valider"], cwd=self.racine, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        f = fiche_these()
        del f["lecture"]["obstacle"]
        self.poser(f)
        p = subprocess.run([PY, str(SCRIPTS / "doctrine.py"), "valider"], cwd=self.racine, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(p.returncode, 1)
        self.assertIn("DOCTRINE_OBSTACLE_NON_DIT", p.stdout)
        e = self.racine / "ecritures" / "memoire.md"
        e.write_text("La chronique publiée à la RFDA 2019, p. 100.\n", encoding="utf-8")
        p = subprocess.run([PY, str(SCRIPTS / "doctrine.py"), "controle", str(e)], cwd=self.racine, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(p.returncode, 1)
        self.assertIn("DOCTRINE_HORS_FICHE", p.stdout)


class Module(unittest.TestCase):
    """Invariants des consignes du module : sources licites, sorties attendues, charte de rédaction."""

    FICHIERS = [PLUGIN / "skills/recherche-doctrinale/SKILL.md", PLUGIN / "agents/chercheur-doctrine.md",
                PLUGIN / "integration/doctrine.md"] + sorted((PLUGIN / "skills/recherche-doctrinale/references").glob("*.md"))

    def test_fichiers_presents(self):
        for f in self.FICHIERS:
            self.assertTrue(f.is_file(), f)

    def test_outils_de_l_agent(self):
        t = (PLUGIN / "agents/chercheur-doctrine.md").read_text(encoding="utf-8")
        entete = t.split("---")[1]
        outils = [o.strip() for o in entete.split("tools:")[1].split("\n")[0].split(",")]
        for o in ("mcp__shs_fr__theses_get", "mcp__librejustice__get_decision", "mcp__academic_papers__get_crossref_paper_by_doi"):
            self.assertIn(o, outils)
        self.assertIn("recherche/doctrine/", t)

    def test_pas_de_tiret_cadratin(self):
        for f in self.FICHIERS + [SCRIPTS / "doctrine.py", PLUGIN / "references/schemas/doctrine.v1.schema.json"]:
            self.assertNotIn("—", f.read_text(encoding="utf-8"), f)


if __name__ == "__main__":
    unittest.main()
