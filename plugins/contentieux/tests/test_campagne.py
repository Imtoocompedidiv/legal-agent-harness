"""Contrôles de la campagne : théorie de l'affaire et séquence, sur une affaire synthétique.

Lancer : python -m pytest -q plugins/contentieux/tests/test_campagne.py
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import controles_campagne as CC  # noqa: E402
import lib_affaire as L  # noqa: E402
from test_contentieux import LECTURE_TRAME, THEORIE_ADVERSE, ecrire, sequence_conforme, theorie_conforme  # noqa: E402

PY = sys.executable


class Campagne(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.r = self.tmp / "affaire"
        subprocess.run([PY, str(SCRIPTS / "affaire.py"), "init", str(self.r), "--intitule", "Essai", "--client", "X",
                        "--objectif", "Obtenir Z"], check=True, capture_output=True)
        self.ecriture = self.r / "ecritures/brouillons/ref_v2.md"
        ecrire(self.ecriture, "Requête.\n")
        self.date = "2026-11-18T10:00"
        self.constats = []

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def c(self, code, gravite, message, **extra):
        self.constats.append(code)

    def lancer(self, fiche=None):
        self.constats = []
        CC.controler_theorie(self.r, self.ecriture, self.c)
        CC.controler_sequence(self.r, self.ecriture, fiche or {"type_acte": "refere_suspension"}, self.c)
        return set(self.constats)

    def conforme(self):
        ecrire(self.r / "strategie/theorie.json", theorie_conforme(self.date))
        ecrire(self.r / "strategie/theorie_adverse.json", THEORIE_ADVERSE)
        ecrire(self.r / "ecritures/controle/trame.lecture_froid.json", LECTURE_TRAME)
        ecrire(self.r / "strategie/sequence.json", sequence_conforme(self.date, "ref", "refere_suspension", self.date))
        ecrire(self.r / "ecritures/controle/ref_v2.recit.json", {"theorie_date": self.date})

    def test_absence(self):
        self.assertEqual(self.lancer(), {"THEORIE_ABSENTE", "SEQUENCE_ABSENTE"})

    def test_theorie_adverse_reservee_et_exigee(self):
        self.conforme()
        (self.r / "strategie/theorie_adverse.json").unlink()
        self.assertEqual(self.lancer(), {"THEORIE_CONTRADICTION_ABSENTE"})
        import json
        ev = {"hook_event_name": "PreToolUse", "cwd": str(self.r), "tool_name": "Write",
              "tool_input": {"file_path": str(self.r / "strategie/theorie_adverse.json"), "content": "x"}}
        r = subprocess.run([PY, str(SCRIPTS / "hook.py")], input=json.dumps(ev), capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")
        ev["agent_type"] = "contentieux:avocat-adverse"
        r = subprocess.run([PY, str(SCRIPTS / "hook.py")], input=json.dumps(ev), capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.stdout.strip(), "")

    def test_argument_adverse_sans_reponse(self):
        self.conforme()
        th = theorie_conforme(self.date)
        th["reponses_theorie_adverse"] = []
        ecrire(self.r / "strategie/theorie.json", th)
        self.assertEqual(self.lancer(), {"THEORIE_ARGUMENT_ADVERSE_SANS_REPONSE"})
        th["reponses_theorie_adverse"] = [{"argument": "A1", "traitement": "indifference", "explication": "le juge n'aura pas à trancher ce point"}]
        ecrire(self.r / "strategie/theorie.json", th)
        self.assertEqual(self.lancer(), {"THEORIE_ARGUMENT_ADVERSE_SANS_REPONSE"})
        th["reponses_theorie_adverse"] = [{"argument": "A1", "traitement": "decisif_pour_la_voie", "explication": "l'urgence tombe : le référé passe en réserve",
                                           "voies_modifiees": ["V1"]}]
        ecrire(self.r / "strategie/theorie.json", th)
        self.assertEqual(self.lancer(), set())

    def test_argument_decisif_ecrit_autrement(self):
        self.conforme()
        ecrire(self.r / "strategie/theorie_adverse.json", {"date": "2026-11-18T09:00", "meilleur_coup": "A1",
                                                           "arguments": [{"id": "A1", "enonce": "pas d'urgence", "force": "decisif"}]})
        th = theorie_conforme(self.date)
        th["reponses_theorie_adverse"] = [{"argument": "A1", "traitement": "indifference", "explication": "le juge n'aura pas à trancher ce point"}]
        ecrire(self.r / "strategie/theorie.json", th)
        self.assertEqual(self.lancer(), {"THEORIE_ARGUMENT_ADVERSE_SANS_REPONSE"})

    def test_voie_urgence_eprouvee(self):
        self.conforme()
        (self.r / "ecritures/controle/trame.lecture_froid.json").unlink()
        self.assertEqual(self.lancer(), {"VOIE_URGENCE_NON_EPROUVEE"})
        ecrire(self.r / "ecritures/controle/trame.lecture_froid.json", {"issue": "rejet", "issue_binaire": "echec", "categorie_motif": "urgence_absente"})
        self.assertEqual(self.lancer(), {"VOIE_URGENCE_REJETEE_EN_SIMULATION"})

    def test_voies_de_l_adversaire(self):
        self.conforme()
        sq = sequence_conforme(self.date, "ref", "refere_suspension", self.date)
        sq["voies_adversaires"] = []
        ecrire(self.r / "strategie/sequence.json", sq)
        self.assertEqual(self.lancer(), {"SEQUENCE_VOIES_ADVERSES_ABSENTES"})
        sq["voies_adversaires"] = [{"voie": "licenciement pour insuffisance professionnelle", "parade": "évaluations et accompagnement"}]
        ecrire(self.r / "strategie/sequence.json", sq)
        self.assertEqual(self.lancer(), {"SEQUENCE_VOIES_ADVERSES_ABSENTES"})

    def test_regime_contentieux_de_chaque_acte(self):
        self.conforme()
        sq = sequence_conforme(self.date, "ref", "refere_suspension", self.date)
        sq["actes"] = [{"id": "A1"}]
        ecrire(self.r / "strategie/sequence.json", sq)
        self.assertEqual(self.lancer(), {"ACTE_REGIME_CONTENTIEUX_NON_EXAMINE"})

    def test_requete_conservatoire(self):
        import os
        from datetime import timedelta
        os.environ["CONTENTIEUX_MAINTENANT"] = "2026-11-18T09:00"
        try:
            base = [{"code": "FAIT_DECISIF_ALLEGUE", "gravite": "BLOQUANT", "message": "m"},
                    {"code": "LECTURE_FROID_ABSENTE", "gravite": "BLOQUANT", "message": "m"},
                    {"code": "DELAI_DEPASSE", "gravite": "BLOQUANT", "message": "m", "categorie": "delai_tardivete"},
                    {"code": "CONDITION_ABSENTE", "gravite": "BLOQUANT", "message": "m", "categorie": "interet_qualite"}]
            fiche = {"moyens": [{"intitule": "Défaut d'évaluation environnementale"}],
                     "conservatoire": {"echeance": "2026-11-18T23:59", "memoire_complementaire": "2026-11-25", "pieces_a_produire": ["titre"]}}
            constats = [dict(k) for k in base]
            ajout = []
            self.assertTrue(CC.appliquer_conservatoire(constats, fiche, False, lambda code, *a, **k: ajout.append(code)))
            self.assertEqual([k["gravite"] for k in constats], ["ALERTE", "ALERTE", "BLOQUANT", "ALERTE"])
            self.assertEqual(ajout, ["CONSERVATOIRE"])
            # Sans moyen, ou loin de l'échéance, ou pour un référé : refusé.
            for f, ref in ((dict(fiche, moyens=[]), False), (dict(fiche, conservatoire=dict(fiche["conservatoire"], echeance="2026-12-30")), False), (fiche, True)):
                constats, ajout = [dict(k) for k in base], []
                self.assertFalse(CC.appliquer_conservatoire(constats, f, ref, lambda code, *a, **k: ajout.append(code)))
                self.assertEqual(ajout, ["CONSERVATOIRE_INJUSTIFIE"])
        finally:
            del os.environ["CONTENTIEUX_MAINTENANT"]

    def test_competence_premier_ressort_lue(self):
        import json
        import lectures as LECT
        constats = []
        CC.controler_competence(self.r, {"juge": "admin"}, lambda code, *a, **k: constats.append(code))
        self.assertEqual(constats, ["COMPETENCE_PREMIER_RESSORT_NON_LUE"])
        constats = []
        CC.controler_competence(self.r, {"juge": "judiciaire"}, lambda code, *a, **k: constats.append(code))
        self.assertEqual(constats, [])
        LECT.capturer(self.r, {"tool_name": "mcp__librejustice__get_norm", "tool_input": {"code": "code-de-justice-administrative", "article": "r311-1"},
                               "tool_response": json.dumps({"code": "code-de-justice-administrative", "number": "R311-1", "text": "t"})})
        constats = []
        CC.controler_competence(self.r, {"juge": "admin"}, lambda code, *a, **k: constats.append(code))
        self.assertEqual(constats, [])

    def test_bilan_urgence(self):
        constats = []
        CC.controler_urgence({"conditions": [{"condition": "urgence", "etat": "etablie"}]}, lambda code, *a, **k: constats.append(code))
        self.assertEqual(constats, ["URGENCE_BILAN_ABSENT"])
        constats = []
        CC.controler_urgence({"conditions": [{"condition": "urgence", "interet_public_adverse": "protection de l'enfant",
                                              "bilan": "la mesure ne protège rien que l'éloignement de l'enfant de son unique famille ne compromette"}]},
                             lambda code, *a, **k: constats.append(code))
        self.assertEqual(constats, [])

    def test_conforme(self):
        self.conforme()
        self.assertEqual(self.lancer(), set())

    def test_hypotheses_et_faits_defavorables(self):
        self.conforme()
        th = theorie_conforme(self.date)
        th["hypotheses"] = [h for h in th["hypotheses"] if h["porteur"] != "lecture_par_defaut"]
        th["hypotheses"][0]["pieces_incompatibles"] = [{"piece": "4", "extrait": "x", "explication": ""}]
        th["faits_defavorables"] = [{"fait": "retard", "traitement": "concession", "explication": "nous l'admettons"}]
        del th["epreuves"]["unicite"]
        ecrire(self.r / "strategie/theorie.json", th)
        codes = self.lancer()
        self.assertTrue({"THEORIE_HYPOTHESES", "THEORIE_PIECE_INCOMPATIBLE", "THEORIE_FAIT_DEFAVORABLE", "THEORIE_EPREUVE_MANQUANTE"} <= codes, codes)

    def test_theorie_perimee_par_une_piece_nouvelle(self):
        self.conforme()
        ecrire(self.r / "pieces/bordereau.json", {"pieces": [{"cote": "7", "fichier": "f", "sha256": "x", "description": "d",
                                                              "ajoutee_le": "2026-11-18 11:30:00 +0100"}]})
        codes = self.lancer()
        self.assertIn("THEORIE_PERIMEE", codes)
        self.assertIn("SEQUENCE_PERIMEE", codes)

    def test_rejeu_date_des_fiches_et_non_du_fichier(self):
        import os
        self.conforme()
        ecrire(self.r / "pieces/analyses/3.json", {"cote": "3"})
        os.environ["CONTENTIEUX_MAINTENANT"] = "2026-11-18T12:00"
        try:
            self.assertNotIn("THEORIE_PERIMEE", self.lancer())
            ecrire(self.r / "pieces/analyses/3.json", {"cote": "3", "analyse_le": "2026-11-18 10:30:00 +0100"})
            self.assertIn("THEORIE_PERIMEE", self.lancer())
        finally:
            del os.environ["CONTENTIEUX_MAINTENANT"]

    def test_recit_qui_projette_une_ancienne_theorie(self):
        self.conforme()
        ecrire(self.r / "ecritures/controle/ref_v2.recit.json", {"theorie_date": "2026-11-01T09:00"})
        self.assertEqual(self.lancer(), {"THEORIE_NON_SUIVIE"})

    def test_familles_coups_et_delais(self):
        self.conforme()
        sq = sequence_conforme(self.date, "ref", "refere_suspension", self.date)
        sq["familles_examinees"] = [f for f in sq["familles_examinees"] if f["famille"] not in ("penal", "amiable")]
        sq["ordre_des_coups"][0]["reponses_adverses"] = []
        sq["voies"][0]["delai"] = {}
        ecrire(self.r / "strategie/sequence.json", sq)
        codes = self.lancer()
        self.assertTrue({"SEQUENCE_FAMILLE_NON_EXAMINEE", "COUP_SANS_REPONSE_ADVERSE", "VOIE_SANS_DELAI"} <= codes, codes)

    def test_desistement_du_fond_prevu(self):
        self.conforme()
        sq = sequence_conforme(self.date, "ref", "refere_suspension", self.date)
        sq["ordre_des_coups"][0]["reponses_adverses"] = [{"reponse": "rejet", "coup_suivant": "fond"}]
        ecrire(self.r / "strategie/sequence.json", sq)
        self.assertEqual(self.lancer(), {"SEQUENCE_DESISTEMENT_NON_PREVU"})

    def test_acte_hors_sequence(self):
        self.conforme()
        sq = sequence_conforme(self.date, "autre_acte", "assignation", self.date)
        ecrire(self.r / "strategie/sequence.json", sq)
        self.assertIn("ACTE_HORS_SEQUENCE", self.lancer())
        sq = sequence_conforme(self.date, "ref", "refere_suspension", self.date)
        sq["ordre_des_coups"][0]["voie"] = "V9"
        ecrire(self.r / "strategie/sequence.json", sq)
        self.assertIn("ACTE_HORS_SEQUENCE", self.lancer())

    def test_sequence_sur_ancienne_theorie_et_revue(self):
        self.conforme()
        ecrire(self.r / "strategie/sequence.json", sequence_conforme(self.date, "ref", "refere_suspension", "2026-11-01T09:00"))
        self.assertIn("SEQUENCE_THEORIE", self.lancer())
        constats = []
        CC.controler_revue_campagne(self.r, {"theorie_date": self.date, "sequence_date": "2026-11-01T09:00"},
                                    lambda code, *a, **k: constats.append(code))
        self.assertEqual(constats, ["REVUE_CHARPENTE_PERIMEE"])

    def test_schemas(self):
        self.conforme()
        self.assertEqual(L.valider_fichier(self.r, "strategie/theorie.json"), [])
        self.assertEqual(L.valider_fichier(self.r, "strategie/sequence.json"), [])
        ecrire(self.r / "strategie/sequence.json", {"date": self.date})
        self.assertTrue(L.valider_fichier(self.r, "strategie/sequence.json"))


if __name__ == "__main__":
    unittest.main()
