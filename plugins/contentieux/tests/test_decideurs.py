"""Tests du profil des décideurs (strategie/decideurs.json) : schéma, règles croisées, contrôle avant acte, fiche du juge simulé.

Données synthétiques, aucun appel réseau. Lancer : python -m pytest -q plugins/contentieux/tests/test_decideurs.py
"""
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import decideurs as D  # noqa: E402

PY = sys.executable


def profil_complet() -> dict:
    return {
        "schema": "decideurs/1",
        "date": "2026-11-10T10:00",
        "actes_couverts": ["refere_suspension"],
        "decideurs": [{
            "id": "D1", "nature": "juridiction", "institution": "Tribunal administratif de Nullepart",
            "formation": "juge des référés statuant seul", "stade": "refere", "procedure": "référé-suspension, CJA, art. L. 521-1",
            "matiere": "séjour des étrangers", "actes": ["refere_suspension"],
            "standard_de_controle": {"niveau": "restreint", "enonce": "Erreur manifeste sur l'appréciation globale de la situation.",
                                     "sources": ["S1"]},
            "taux_de_base": [{"mesure": "ordonnances publiées qui suspendent", "numerateur": 9, "denominateur": 60,
                              "perimetre": "référés-suspension publiés, matière séjour", "periode": "2025-01-01 au 2026-09-30",
                              "exclusions": "non-lieux et désistements écartés", "sources": ["S2"]}],
            "premier_lecteur": {"constat": "Les projets d'ordonnances de tri sont préparés par le pôle d'aide à la décision.",
                                "statut": "pratique_institutionnelle", "sources": ["S3"]},
            "culture": [{"constat": "L'urgence est examinée avant le doute sérieux.", "statut": "decisions_publiees", "sources": ["S2"]}],
            "ce_qui_passe": [{"constat": "Suspension quand le refus interrompt un contrat de travail en cours, pièce à l'appui.",
                              "statut": "decisions_publiees", "sources": ["S2"]}],
            "ce_qui_echoue": [{"constat": "Rejet pour défaut d'urgence quand le requérant a attendu plusieurs mois.",
                               "statut": "decisions_publiees", "sources": ["S2"]},
                              {"constat": "Une ordonnance antérieure de ce dossier a rejeté une première demande.",
                               "statut": "piece_du_dossier", "sources": ["S5"]}],
        }],
        "adversaire": {
            "nature": "personne_publique", "designation": "Préfecture de Nullepart",
            "qui_decide": [{"fonction": "secrétaire général de la préfecture", "role": "signataire",
                            "fondement": "arrêté de délégation de signature publié au recueil des actes administratifs", "sources": ["S4"]}],
            "qui_defend": {"constat": "La préfecture se défend seule et produit rarement un mémoire en défense.",
                           "statut": "pratique_institutionnelle", "sources": ["S3"]},
            "culture_juridique": {"constat": "Le recours contentieux est vu comme le seul canal de réexamen.",
                                  "statut": "pratique_institutionnelle", "sources": ["S3"]},
            "aversion_au_precedent": {"constat": "Aucune mesure publiée ; prédiction théorique seulement.", "statut": "inference",
                                      "sources": ["S3"]},
            "contraintes": [{"type": "organisationnelle", "constat": "Défense départementale sans service spécialisé.",
                             "statut": "pratique_institutionnelle", "sources": ["S3"]}],
            "ce_qu_il_peut_accorder": [{"concession": "réexamen sur pièce nouvelle", "couverture": "élément qui n'était pas au dossier",
                                        "statut": "inference", "sources": ["S3"]}],
            "saisines_exterieures": [{"canal": "defenseur_des_droits", "effet_attendu": "recommandation en équité", "retenue": False,
                                      "raison": "délai incompatible avec l'urgence", "sources": ["S3"]}],
        },
        "leviers": [{"id": "L1", "cible": "D1", "constat": "Le juge suspend quand la pièce établit la perte d'un emploi en cours.",
                     "statut": "decisions_publiees", "sources": ["S2"]}],
        "risques": [{"id": "R1", "cible": "D1", "risque": "Tri pour défaut d'urgence.", "parade": "Urgence datée en première page.",
                     "statut": "decisions_publiees", "sources": ["S2"]}],
        "choix": {k: {"decision": f"décision {k}", "raison": f"raison {k}", "appuis": ["L1", "R1"]}
                  for k in ("forum", "moment", "structure", "ton", "preuve", "demande")},
        "inconnu": ["Part des ordonnances de tri dans cette juridiction : non publiée."],
        "sources": [
            {"id": "S1", "type": "decision", "reference": "CE, 10 octobre 2025, n° 493118", "url": "https://example.invalid/1",
             "lu": "en_entier", "public": True},
            {"id": "S2", "type": "decisions_publiees", "reference": "procedure/calibrage_TA99.md", "lu": "en_entier", "public": True},
            {"id": "S3", "type": "rapport", "reference": "Conseil d'État, étude de 2020 sur le contentieux des étrangers", "lu": "extraits",
             "public": True},
            {"id": "S4", "type": "acte_publie", "reference": "Recueil des actes administratifs, arrêté de délégation", "lu": "en_entier",
             "public": True},
            {"id": "S5", "type": "piece_du_dossier", "reference": "pièce 012", "lu": "en_entier", "public": False},
        ],
    }


def codes(doc) -> set:
    return {k["code"] for k in D.valider(doc) if k["gravite"] == "BLOQUANT"}


def alertes(doc) -> set:
    return {k["code"] for k in D.valider(doc) if k["gravite"] == "ALERTE"}


class Schema(unittest.TestCase):
    def test_schema_charge(self):
        s = json.loads((SCRIPTS.parent / "references" / "schemas" / D.SCHEMA).read_text(encoding="utf-8"))
        self.assertEqual(s["properties"]["schema"]["const"], "decideurs/1")

    def test_profil_complet_valide(self):
        self.assertEqual([k for k in D.valider(profil_complet()) if k["gravite"] == "BLOQUANT"], [])

    def test_squelette_suit_la_structure(self):
        # Le squelette a la bonne forme ; il échoue sur les valeurs vides, pas sur des champs inconnus ou manquants.
        msgs = [k["message"] for k in D.valider(copy.deepcopy(D.SQUELETTE))]
        self.assertTrue(msgs)
        self.assertFalse(any("manquant" in m for m in msgs))

    def test_champ_racine_manquant(self):
        for champ in ("decideurs", "adversaire", "choix", "sources", "date"):
            doc = profil_complet()
            del doc[champ]
            self.assertIn("DECIDEURS_INVALIDE", codes(doc), champ)

    def test_choix_incomplet(self):
        doc = profil_complet()
        del doc["choix"]["demande"]
        self.assertIn("DECIDEURS_INVALIDE", codes(doc))

    def test_valeur_hors_enumeration(self):
        doc = profil_complet()
        doc["decideurs"][0]["standard_de_controle"]["niveau"] = "bienveillant"
        self.assertIn("DECIDEURS_INVALIDE", codes(doc))

    def test_date_illisible(self):
        doc = profil_complet()
        doc["date"] = "10 novembre"
        self.assertIn("DECIDEURS_INVALIDE", codes(doc))


class Regles(unittest.TestCase):
    def test_calibrage_desequilibre_alerte_hors_acte(self):
        # Pour une étape ultérieure de la séquence, une alerte ; le contrôle de l'acte bloque pour la juridiction visée (classe Affaire).
        doc = profil_complet()
        doc["decideurs"][0]["ce_qui_passe"] = []
        self.assertIn("CALIBRAGE_DESEQUILIBRE", alertes(doc))
        self.assertNotIn("CALIBRAGE_DESEQUILIBRE", codes(doc))

    def test_taux_absent_sans_explication(self):
        doc = profil_complet()
        doc["decideurs"][0]["taux_de_base"] = []
        self.assertIn("TAUX_DE_BASE_ABSENT", alertes(doc))
        doc["decideurs"][0]["taux_de_base_absent"] = "Aucune série publiée pour cette formation ; recherche du 10 novembre 2026."
        self.assertNotIn("TAUX_DE_BASE_ABSENT", alertes(doc))

    def test_cible_liste(self):
        doc = profil_complet()
        doc["leviers"][0]["cible"] = ["D1", "adversaire"]
        self.assertNotIn("CIBLE_INCONNUE", codes(doc))
        doc["leviers"][0]["cible"] = "Juge des référés (D1)"
        self.assertIn("CIBLE_INCONNUE", codes(doc))

    def test_taux_plusieurs_sources(self):
        doc = profil_complet()
        doc["decideurs"][0]["taux_de_base"][0]["sources"] = ["S2", "S1"]
        self.assertEqual(codes(doc), set())
        doc["decideurs"][0]["taux_de_base"][0]["sources"] = ["S14 (classement propre), S13"]
        self.assertIn("SOURCE_INCONNUE", codes(doc))

    def test_taux_incoherent(self):
        doc = profil_complet()
        doc["decideurs"][0]["taux_de_base"][0]["numerateur"] = 70
        self.assertIn("TAUX_INCOHERENT", codes(doc))

    def test_source_inconnue(self):
        doc = profil_complet()
        doc["leviers"][0]["sources"] = ["S9"]
        self.assertIn("SOURCE_INCONNUE", codes(doc))

    def test_source_non_lue(self):
        doc = profil_complet()
        doc["sources"][2]["lu"] = "resume"
        self.assertIn("SOURCE_NON_LUE", codes(doc))
        doc = profil_complet()
        doc["sources"][1]["lu"] = "non_lu"
        self.assertIn("SOURCE_NON_LUE", codes(doc))

    def test_juridiction_sans_source_publique(self):
        doc = profil_complet()
        for s in doc["sources"]:
            s["public"] = False
        self.assertIn("DECIDEUR_SANS_SOURCE_PUBLIQUE", codes(doc))

    def test_magistrat_nomme(self):
        doc = profil_complet()
        doc["decideurs"][0]["culture"][0]["constat"] = "Mme Durand rejette presque toujours au tri."
        self.assertIn("MAGISTRAT_NOMME", codes(doc))
        doc = profil_complet()
        doc["decideurs"][0]["formation"] = "juge des référés, présidente Durand"
        self.assertIn("MAGISTRAT_NOMME", codes(doc))
        doc = profil_complet()
        doc["decideurs"][0]["juge_nomme"] = "X"
        self.assertIn("MAGISTRAT_NOMME", codes(doc))
        doc = profil_complet()
        doc["risques"][0]["risque"] = "M. Martin trie les requêtes longues."
        self.assertIn("MAGISTRAT_NOMME", codes(doc))

    def test_decision_citee_par_numero_admise(self):
        doc = profil_complet()
        doc["decideurs"][0]["culture"][0]["constat"] = "CE, Sect., 21 décembre 2018, n° 409678 : le juge respecte la hiérarchie des demandes."
        self.assertNotIn("MAGISTRAT_NOMME", codes(doc))

    def test_probabilite_refusee(self):
        doc = profil_complet()
        doc["choix"]["demande"]["raison"] = "La chance de succès est de 40 % environ."
        self.assertIn("PROBABILITE", codes(doc))
        doc = profil_complet()
        doc["decideurs"][0]["probabilite_succes"] = 0.4
        self.assertIn("PROBABILITE", codes(doc))
        doc = profil_complet()
        doc["decideurs"][0]["taux_de_base"][0]["exclusions"] = "15 % des ordonnances publiées, ce qui ne dit pas la chance du dossier"
        self.assertNotIn("PROBABILITE", codes(doc))

    def test_choix_appui_inconnu(self):
        doc = profil_complet()
        doc["choix"]["forum"]["appuis"] = ["L7"]
        self.assertIn("APPUI_INCONNU", codes(doc))

    def test_levier_inemploye_alerte(self):
        doc = profil_complet()
        doc["leviers"].append({"id": "L2", "cible": "adversaire", "constat": "c", "statut": "inference", "sources": ["S3"]})
        alertes = {k["code"] for k in D.valider(doc) if k["gravite"] == "ALERTE"}
        self.assertIn("LEVIER_INEMPLOYE", alertes)
        self.assertNotIn("LEVIER_INEMPLOYE", codes(doc))

    def test_cible_inconnue(self):
        doc = profil_complet()
        doc["leviers"][0]["cible"] = "D4"
        self.assertIn("CIBLE_INCONNUE", codes(doc))

    def test_id_double(self):
        doc = profil_complet()
        doc["sources"].append(dict(doc["sources"][0]))
        self.assertIn("ID_DOUBLE", codes(doc))

    def test_organisation_incomplete(self):
        doc = profil_complet()
        doc["adversaire"]["qui_decide"] = []
        doc["adversaire"]["contraintes"] = []
        del doc["adversaire"]["aversion_au_precedent"]
        c = codes(doc)
        self.assertTrue({"QUI_DECIDE_ABSENT", "CONTRAINTES_ABSENTES", "ADVERSAIRE_INCOMPLET"} <= c, c)

    def test_personne_physique(self):
        doc = profil_complet()
        adv = doc["adversaire"]
        adv.update({"nature": "personne_physique", "designation": "partie adverse", "qui_decide": [], "contraintes": [],
                    "ce_qu_il_peut_accorder": []})
        for k in ("qui_defend", "culture_juridique", "aversion_au_precedent"):
            adv.pop(k)
        self.assertEqual(codes(doc), set())
        adv["profil_psychologique"] = "impulsif"
        self.assertIn("PROFIL_PERSONNEL", codes(doc))

    def test_agent_nomme_alerte(self):
        doc = profil_complet()
        doc["adversaire"]["qui_decide"][0]["fonction"] = "M. Lefort, chef du bureau du séjour"
        alertes = {k["code"] for k in D.valider(doc) if k["gravite"] == "ALERTE"}
        self.assertIn("PERSONNE_NOMMEE", alertes)


class Affaire(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.r = Path(self.tmp.name)
        (self.r / "etat").mkdir()
        (self.r / "etat/affaire.json").write_text(json.dumps({"id": "t", "intitule": "t", "client": "x", "objectif": "y"}), encoding="utf-8")
        (self.r / "ecritures/brouillons").mkdir(parents=True)
        (self.r / "ecritures/controle").mkdir(parents=True)
        self.acte = self.r / "ecritures/brouillons/refere_suspension_v2.md"
        self.acte.write_text("Requête", encoding="utf-8")
        os.environ["CONTENTIEUX_MAINTENANT"] = "2026-11-18T12:00"

    def tearDown(self):
        os.environ.pop("CONTENTIEUX_MAINTENANT", None)
        self.tmp.cleanup()

    def ecrire(self, rel, obj):
        p = self.r / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")

    def constats(self, fiche=None):
        out = []
        D.controler(self.r, self.acte, fiche or {}, lambda code, gravite, message, **_: out.append((code, gravite)))
        return {c for c, g in out if g == "BLOQUANT"}

    def test_absent_bloque(self):
        self.assertEqual(self.constats(), {"DECIDEURS_ABSENT"})

    def test_json_illisible(self):
        (self.r / "strategie").mkdir()
        (self.r / D.FICHIER).write_text("{", encoding="utf-8")
        self.assertEqual(self.constats(), {"DECIDEURS_INVALIDE"})

    def test_complet_passe(self):
        self.ecrire(D.FICHIER, profil_complet())
        self.assertEqual(self.constats(), set())

    def test_incomplet_bloque(self):
        doc = profil_complet()
        doc["decideurs"][0]["ce_qui_echoue"] = []
        self.ecrire(D.FICHIER, doc)
        self.assertIn("CALIBRAGE_DESEQUILIBRE", self.constats())

    def test_calibrage_bloque_seulement_pour_la_juridiction_de_l_acte(self):
        doc = profil_complet()
        autre = copy.deepcopy(doc["decideurs"][0])
        autre.update({"id": "D2", "stade": "cassation", "actes": [], "ce_qui_passe": [], "taux_de_base": []})
        doc["decideurs"].append(autre)
        self.ecrire(D.FICHIER, doc)
        self.assertEqual(self.constats(), set())
        self.assertTrue({"CALIBRAGE_DESEQUILIBRE", "TAUX_DE_BASE_ABSENT"} <= self.constats({"decideur": "D2"}))

    def test_perime(self):
        doc = profil_complet()
        doc["date"] = "2026-03-01"
        self.ecrire(D.FICHIER, doc)
        self.assertIn("DECIDEURS_PERIME", self.constats())

    def test_hors_acte(self):
        doc = profil_complet()
        doc["actes_couverts"] = ["requete_fond"]
        self.ecrire(D.FICHIER, doc)
        self.assertIn("DECIDEURS_HORS_ACTE", self.constats())

    def test_sans_juridiction(self):
        doc = profil_complet()
        doc["decideurs"][0]["nature"] = "autorite_administrative"
        self.ecrire(D.FICHIER, doc)
        self.assertIn("DECIDEURS_SANS_JURIDICTION", self.constats())
        self.ecrire(D.FICHIER, profil_complet())
        self.assertIn("DECIDEURS_SANS_JURIDICTION", self.constats({"decideur": "D8"}))

    def test_ligne_anterieure(self):
        self.ecrire(D.FICHIER, profil_complet())
        self.ecrire("strategie/ligne.json", {"date": "2026-11-09T09:00"})
        self.assertIn("LIGNE_ANTERIEURE_AU_PROFIL", self.constats())
        self.ecrire("strategie/ligne.json", {"date": "2026-11-09T09:00", "profil_decideurs_applique": "2026-11-10T10:00"})
        self.assertNotIn("LIGNE_ANTERIEURE_AU_PROFIL", self.constats())
        self.ecrire("strategie/ligne.json", {"date": "2026-11-11"})
        self.assertNotIn("LIGNE_ANTERIEURE_AU_PROFIL", self.constats())

    def test_lecture_froid_doit_porter_sur_le_profil(self):
        doc = profil_complet()
        self.ecrire(D.FICHIER, doc)
        lf = "ecritures/controle/refere_suspension_v2.lecture_froid.json"
        self.ecrire(lf, {"sha256": "x"})
        self.assertIn("LECTURE_FROID_SANS_PROFIL", self.constats())
        chemin, sha = D.ecrire_fiche_juge(self.r, doc, doc["decideurs"][0])
        self.ecrire(lf, {"sha256": "x", "profil_decideur_sha256": sha})
        self.assertNotIn("LECTURE_FROID_SANS_PROFIL", self.constats())
        doc["decideurs"][0]["culture"][0]["constat"] = "Autre constat."
        self.ecrire(D.FICHIER, doc)
        self.assertIn("LECTURE_FROID_SANS_PROFIL", self.constats())

    def test_fiche_juge_sans_strategie_ni_dossier(self):
        doc = profil_complet()
        chemin, sha = D.ecrire_fiche_juge(self.r, doc, doc["decideurs"][0])
        t = chemin.read_text(encoding="utf-8")
        self.assertTrue(t.startswith(f"Empreinte du profil : {sha}"))
        self.assertIn("9 sur 60 (15 %)", t)
        self.assertIn("restreint", t)
        self.assertIn("Ce qui passe devant ce juge", t)
        self.assertIn("Ce qui échoue devant ce juge", t)
        for absent in ("Préfecture de Nullepart", "décision forum", "Le juge suspend quand la pièce", "pièce 012",
                       "Une ordonnance antérieure de ce dossier"):
            self.assertNotIn(absent, t)
        self.assertIn("1 constat(s) tiré(s) du seul dossier ont été retirés", t)

    def test_cli(self):
        env = dict(os.environ)
        r = subprocess.run([PY, str(SCRIPTS / "decideurs.py"), "--racine", str(self.r), "valider"], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.ecrire(D.FICHIER, profil_complet())
        r = subprocess.run([PY, str(SCRIPTS / "decideurs.py"), "--racine", str(self.r), "valider"], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = subprocess.run([PY, str(SCRIPTS / "decideurs.py"), "--racine", str(self.r), "fiche-juge"], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((self.r / "procedure/calibrage_decideur_D1.md").is_file())
        r = subprocess.run([PY, str(SCRIPTS / "decideurs.py"), "controle", str(self.acte)], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = subprocess.run([PY, str(SCRIPTS / "decideurs.py"), "squelette"], capture_output=True, text=True, env=env)
        self.assertEqual(json.loads(r.stdout)["schema"], "decideurs/1")


if __name__ == "__main__":
    unittest.main()
