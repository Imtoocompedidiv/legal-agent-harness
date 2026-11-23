"""Tests du module mécanique des exercices : fiches, catalogue, contrôle du bloc « exercice » de la fiche de l'acte.

Données synthétiques, aucun appel réseau. Lancer : python -m pytest -q plugins/contentieux/tests/test_exercices.py
"""
import copy
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN / "scripts"
sys.path.insert(0, str(SCRIPTS))
import exercices as E  # noqa: E402
import lib_affaire as L  # noqa: E402

PY = sys.executable
CADRATIN = chr(0x2014)
SKILL = PLUGIN / "skills" / "mecanique-des-exercices"
ATTENDUS = {
    "refere_suspension", "refere_liberte", "refere_mesures_utiles", "refere_provision_admin", "refere_instruction_admin",
    "requete_annulation", "plein_contentieux_indemnitaire", "appel_administratif", "cassation_conseil_etat",
    "recours_administratif_prealable", "communication_cada", "refere_civil_834", "refere_civil_835_trouble",
    "refere_civil_835_provision", "mesure_instruction_145", "assignation_fond", "conclusions_mise_en_etat", "appel_civil",
    "pourvoi_civil", "saisine_prudhommes", "refere_prudhommal", "plainte_simple", "plainte_partie_civile", "citation_directe",
    "appel_penal", "pourvoi_penal", "qpc", "requete_cedh", "defenseur_des_droits", "transaction_mediation"}
TITRES = ["## 1. Qui décide, à quel stade, sur quoi", "## 2. Standard de contrôle et office", "## 3. La condition qui fait échouer et sa preuve",
          "## 4. La cible", "## 5. Ce que l'auteur produit et sous quelle forme", "## 6. Exigences implicites", "## 7. Ce qui fait gagner",
          "## 8. Erreurs hors sujet typiques", "## 9. Exercices voisins", "## 10. Statistiques publiées", "## 11. Points non vérifiés",
          "## Sources", "## Données de contrôle"]
CATALOGUE = E.charger_catalogue()


def bloc_refere_suspension(date: str = "2026-11-19T09:00") -> dict:
    """Diagnostic complet d'un référé-suspension, cohérent avec la fiche de référé de test_contentieux (acte A, pièces 1 à 3,
    sources T et D)."""
    e = CATALOGUE["refere_suspension"]
    return {
        "exercice": "refere_suspension", "date": date,
        "juge_et_stade": {"juge": "juge des référés du tribunal administratif", "stade": "tri de l'article L. 522-3, puis audience",
                          "standard": "urgence appréciée objectivement et globalement ; doute sérieux en l'état de l'instruction",
                          "office": "suspension et injonction de réexamen dans l'attente du jugement au fond"},
        "ce_qu_il_decide": "S'il suspend la décision du 20 mars 2026 jusqu'au jugement de la requête au fond.",
        "condition_decisive": {
            "condition": "urgence", "pourquoi_decisive": "Elle s'écarte seule au tri, sans examen des moyens.",
            "preuve": {"pieces": ["2"], "faits": [], "sources": ["T"]},
            "ce_qui_la_ferait_tomber": [{"situation": "L'égalité entre candidats opposée par la défense.",
                                         "parade": "L'aménagement préconisé ne retire rien aux autres candidats (pièce 2).", "pieces": ["2"]}]},
        "cible": {"nature": "acte", "designation": "décision du directeur du 20 mars 2026", "acte": "A", "date": "2026-03-20"},
        "ce_qui_fait_gagner": "L'urgence datée par les examens du 1er mai et le défaut d'examen de l'avis médical, visible sur pièces.",
        "exigences_implicites": [{"cle": x["cle"], "verifiee": True, "source": "T", "preuve": "pièce 3"} for x in e["exigences_implicites"]],
        "voisins_ecartes": [{"exercice": "refere_liberte", "raison": "Aucune liberté fondamentale n'appelle une mesure dans les quarante-huit heures."},
                            {"exercice": "requete_annulation", "raison": "Déposée au fond ; seule elle ne donne rien avant les examens du 1er mai."}],
        "regime_special": {"applicable": False, "texte": "Droit commun du référé-suspension (CJA, art. L. 521-1)."},
    }


FICHE_REFERE = {"type_acte": "refere_suspension",
                "actes_attaques": [{"id": "A", "designation": "décision du 20 mars 2026", "date": "2026-03-20", "qualification": "decision_expresse"}],
                "conditions": [{"condition": "urgence", "etat": "etablie", "faits": [{"fait": "examens", "date": "2026-05-01", "pieces": [2]}]}],
                "delai": {"echeance": "2099-01-01T12:00"}}
CONTEXTE = {"sources": {"T": {"id": "T", "lu_en_entier": True}, "N": {"id": "N", "lu_en_entier": False}}, "bordereau": {"1", "2", "3"}, "matrice": {"F1"}}
TEXTE_REFERE = "TRIBUNAL ADMINISTRATIF DE NULLEPART\n\nRequête en référé-suspension (article L. 521-1 du code de justice administrative)\n\n1. ...\n"


def codes(constats, gravite=None):
    return {k["code"] for k in constats if gravite is None or k["gravite"] == gravite}


class TestFiches(unittest.TestCase):
    """Chaque fiche suit le gabarit, se charge, et ses données renvoient à des régimes et à des exercices qui existent."""

    def test_trente_exercices(self):
        self.assertEqual(set(CATALOGUE), ATTENDUS)

    def test_plan_et_donnees(self):
        import gate
        gate.charger_regimes_domaines()
        for ident, e in CATALOGUE.items():
            with self.subTest(ident=ident):
                texte = (SKILL / "references" / e["fichier"]).read_text(encoding="utf-8")
                self.assertEqual(re.findall(r"^## .*$", texte, re.M), TITRES)
                self.assertNotIn(CADRATIN, texte)
                self.assertEqual(set(e) - {"fichier"} - E.CLES_FACULTATIVES, E.CLES_DONNEES)
                self.assertIn(e["famille"], E.FAMILLES)
                self.assertIn(e["cible"], E.CIBLES)
                self.assertIsInstance(e["juridictionnel"], bool)
                for t in e["types_acte"]:
                    self.assertIn(t, gate.REGIMES, f"{ident} : régime {t}")
                self.assertIn(e["condition_principale"], E.conditions_connues(e))
                cles = [x["cle"] for x in e["exigences_implicites"]]
                self.assertTrue(cles)
                self.assertEqual(len(cles), len(set(cles)), ident)
                for x in e["exigences_implicites"]:
                    self.assertRegex(x["cle"], r"^[a-z0-9_]+$")
                    self.assertTrue(x.get("exigence") and x.get("sanction") and x.get("source"), x["cle"])
                for v in E.voisins_catalogue(e):
                    self.assertTrue(v in ATTENDUS or v.startswith("autre:"), f"{ident} : voisin {v}")
                self.assertTrue(set(E.voisins_catalogue(e)) & ATTENDUS, ident)
                for m in e["marqueurs_texte"]:
                    re.compile(m)
                self.assertEqual(bool(e["marqueurs_texte"]), e["juridictionnel"] or bool(e["marqueurs_texte"]))
                sources = texte.split("## Sources", 1)[1].split("## Données de contrôle", 1)[0]
                self.assertIn("librejustice.fr", sources, ident)

    def test_marqueurs_propres(self):
        """L'en-tête d'un référé-suspension n'est pas pris pour un référé-liberté, ni l'inverse."""
        s, l = CATALOGUE["refere_suspension"]["marqueurs_texte"], CATALOGUE["refere_liberte"]["marqueurs_texte"]
        self.assertTrue(E._marque(s, TEXTE_REFERE))
        self.assertFalse(E._marque(l, TEXTE_REFERE))
        self.assertTrue(E._marque(l, "Requête en référé-liberté (article L. 521-2 du code de justice administrative)"))

    def test_skill_et_charte(self):
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for ident, e in CATALOGUE.items():
            self.assertIn(f"`{ident}`", skill)
            self.assertIn(e["fichier"], skill)
        for f in (SKILL / "SKILL.md", SCRIPTS / "exercices.py", Path(__file__)):
            self.assertNotIn(CADRATIN, f.read_text(encoding="utf-8"), f.name)


class TestValidation(unittest.TestCase):
    def valider(self, bloc, fiche=None):
        return E.valider(bloc, copy.deepcopy(fiche or FICHE_REFERE), CATALOGUE, CONTEXTE)

    def test_bloc_conforme(self):
        self.assertEqual(codes(self.valider(bloc_refere_suspension()), "BLOQUANT"), set())

    def test_absent_et_inconnu(self):
        self.assertEqual(codes(self.valider(None)), {"EXERCICE_ABSENT"})
        b = bloc_refere_suspension()
        b["exercice"] = "refere_universel"
        self.assertIn("EXERCICE_INCONNU", codes(self.valider(b)))

    def test_regime_discordant(self):
        f = copy.deepcopy(FICHE_REFERE)
        f["type_acte"] = "refere_liberte"
        self.assertIn("EXERCICE_REGIME_DISCORDANT", codes(self.valider(bloc_refere_suspension(), f), "BLOQUANT"))

    def test_juge_stade_et_question(self):
        b = bloc_refere_suspension()
        b["juge_et_stade"]["standard"] = ""
        b["ce_qu_il_decide"] = ""
        b["ce_qui_fait_gagner"] = " "
        self.assertTrue({"EXERCICE_JUGE_STADE_INCOMPLET", "EXERCICE_DECISION_ABSENTE", "EXERCICE_GAIN_ABSENT"} <= codes(self.valider(b)))

    def test_urgence_qui_tomberait(self):
        """Le défaut de l'épreuve : un référé retenu sans avoir examiné ce qui ferait tomber l'urgence."""
        b = bloc_refere_suspension()
        b["condition_decisive"]["ce_qui_la_ferait_tomber"] = []
        self.assertIn("EXERCICE_CONDITION_NON_EPROUVEE", codes(self.valider(b), "BLOQUANT"))
        b["condition_decisive"]["ce_qui_la_ferait_tomber"] = [{"situation": "Le traitement est maintenu.", "parade": ""}]
        self.assertIn("EXERCICE_CONDITION_NON_EPROUVEE", codes(self.valider(b), "BLOQUANT"))

    def test_preuve_de_la_condition(self):
        b = bloc_refere_suspension()
        b["condition_decisive"]["preuve"] = {"pieces": [], "faits": [], "sources": ["T"]}
        self.assertIn("EXERCICE_PREUVE_ABSENTE", codes(self.valider(b)))
        b["condition_decisive"]["preuve"] = {"pieces": ["9"], "faits": ["F7"], "sources": ["N"]}
        self.assertTrue({"EXERCICE_PREUVE_HORS_DOSSIER", "EXERCICE_SOURCE_NON_LUE"} <= codes(self.valider(b)))

    def test_condition_hors_exercice_et_principale(self):
        b = bloc_refere_suspension()
        b["condition_decisive"]["condition"] = "motif_legitime"
        self.assertIn("EXERCICE_CONDITION_HORS_EXERCICE", codes(self.valider(b)))
        b["condition_decisive"]["condition"] = "doute_serieux"
        f = copy.deepcopy(FICHE_REFERE)
        f["conditions"] = []
        self.assertIn("EXERCICE_CONDITION_PRINCIPALE_NON_TRAITEE", codes(self.valider(b, f)))
        self.assertNotIn("EXERCICE_CONDITION_PRINCIPALE_NON_TRAITEE", codes(self.valider(b)))
        b["condition_principale"] = {"condition": "urgence", "etat": "etablie", "preuve": {"pieces": ["2"]}}
        self.assertNotIn("EXERCICE_CONDITION_PRINCIPALE_NON_TRAITEE", codes(self.valider(b, f)))

    def test_condition_declaree_absente_ou_fragile(self):
        f = copy.deepcopy(FICHE_REFERE)
        f["conditions"][0]["etat"] = "fragile"
        self.assertIn("EXERCICE_CONDITION_DECISIVE_FRAGILE", codes(self.valider(bloc_refere_suspension(), f), "ALERTE"))
        f["conditions"][0]["etat"] = "absente"
        self.assertIn("EXERCICE_CONDITION_DECISIVE_ECARTEE", codes(self.valider(bloc_refere_suspension(), f), "BLOQUANT"))

    def test_cible(self):
        b = bloc_refere_suspension()
        b["cible"]["nature"] = "situation"
        self.assertIn("EXERCICE_CIBLE_DISCORDANTE", codes(self.valider(b)))
        b = bloc_refere_suspension()
        b["cible"]["acte"] = "courriel du 2 mars"
        self.assertIn("EXERCICE_CIBLE_DISCORDANTE", codes(self.valider(b)))
        b["cible"] = {"nature": "acte"}
        self.assertIn("EXERCICE_CIBLE_INCOMPLETE", codes(self.valider(b)))

    def test_exigences_une_par_une(self):
        b = bloc_refere_suspension()
        b["exigences_implicites"] = [x for x in b["exigences_implicites"] if x["cle"] != "confirmation_maintien_fond_r612_5_2"]
        k = [x for x in self.valider(b) if x["code"] == "EXERCICE_EXIGENCE_NON_VERIFIEE"]
        self.assertEqual(k[0]["exigences"], ["confirmation_maintien_fond_r612_5_2"])
        b["exigences_implicites"].append({"cle": "confirmation_maintien_fond_r612_5_2", "verifiee": False})
        self.assertIn("EXERCICE_EXIGENCE_NON_VERIFIEE", codes(self.valider(b)))
        b["exigences_implicites"][-1] = {"cle": "confirmation_maintien_fond_r612_5_2", "sans_objet": "oui"}
        self.assertIn("EXERCICE_EXIGENCE_NON_VERIFIEE", codes(self.valider(b)))
        b["exigences_implicites"][-1] = {"cle": "confirmation_maintien_fond_r612_5_2",
                                         "sans_objet": "La séquence prévoit la confirmation dans le mois de l'ordonnance (coup 2)."}
        self.assertNotIn("EXERCICE_EXIGENCE_NON_VERIFIEE", codes(self.valider(b)))
        b["exigences_implicites"][0]["source"] = "N"
        self.assertIn("EXERCICE_SOURCE_NON_LUE", codes(self.valider(b)))

    def test_voisin(self):
        b = bloc_refere_suspension()
        b["voisins_ecartes"] = [{"exercice": "qpc", "raison": "Aucune disposition législative n'est en cause ici."}]
        self.assertIn("EXERCICE_VOISIN_NON_EXAMINE", codes(self.valider(b), "BLOQUANT"))
        b["voisins_ecartes"] = [{"exercice": "refere_liberte", "raison": "non"}]
        self.assertIn("EXERCICE_VOISIN_NON_EXAMINE", codes(self.valider(b), "BLOQUANT"))
        b["voisins_ecartes"].append({"exercice": "refere_inconnu", "raison": "Il n'existe pas dans le code de justice administrative."})
        self.assertIn("EXERCICE_VOISIN_INCONNU", codes(self.valider(b), "ALERTE"))

    def test_regime_special(self):
        """Le défaut de l'épreuve : une condition de recevabilité propre à un contentieux spécial non vue."""
        b = bloc_refere_suspension()
        del b["regime_special"]
        self.assertIn("EXERCICE_REGIME_SPECIAL_NON_EXAMINE", codes(self.valider(b), "BLOQUANT"))
        b["regime_special"] = {"applicable": True, "texte": "C. urb., art. L. 600-3", "type_acte": "refere_suspension_urbanisme"}
        self.assertIn("EXERCICE_REGIME_SPECIAL_IGNORE", codes(self.valider(b), "BLOQUANT"))
        f = copy.deepcopy(FICHE_REFERE)
        f["type_acte"] = "refere_suspension_urbanisme"
        self.assertNotIn("EXERCICE_REGIME_SPECIAL_IGNORE", codes(self.valider(b, f)))

    def test_squelette_couvre_les_exigences(self):
        for ident in CATALOGUE:
            s = E.squelette(ident, CATALOGUE)
            self.assertEqual([x["cle"] for x in s["exigences_implicites"]], [x["cle"] for x in CATALOGUE[ident]["exigences_implicites"]])
            self.assertIn("EXERCICE_EXIGENCE_NON_VERIFIEE", codes(E.valider(s, {}, CATALOGUE, {})))


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.r = self.tmp / "affaire"
        subprocess.run([PY, str(SCRIPTS / "affaire.py"), "init", str(self.r), "--intitule", "Essai", "--client", "X", "--objectif", "Obtenir Z"],
                       check=True, capture_output=True)
        L.ecrire_json(self.r / "etat/sources.json", {"sources": [{"id": "T", "type": "texte", "reference": "CJA L. 521-1", "lu_en_entier": True}]})
        L.ecrire_json(self.r / "pieces/bordereau.json", {"pieces": [{"cote": str(c), "fichier": f"pieces/originaux/{c:03d}_x", "sha256": "x",
                                                                     "description": "x"} for c in (1, 2, 3)]})
        self.ecriture = self.r / "ecritures/brouillons/ref_v1.md"
        self.ecriture.parent.mkdir(parents=True, exist_ok=True)
        self.ecriture.write_text(TEXTE_REFERE, encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def controle(self, fiche, texte=TEXTE_REFERE, ecriture=None):
        out = []
        E.controler(self.r, ecriture or self.ecriture, fiche, texte,
                    lambda code, gravite, message, **_: out.append({"code": code, "gravite": gravite, "message": message}))
        return out


class TestControle(Base):
    def test_ecriture_juridictionnelle(self):
        f = copy.deepcopy(FICHE_REFERE)
        self.assertEqual(codes(self.controle(f), "BLOQUANT"), {"EXERCICE_ABSENT"})
        f["exercice"] = bloc_refere_suspension(L.maintenant().isoformat(timespec="minutes"))
        self.assertEqual(codes(self.controle(f), "BLOQUANT"), set())
        self.assertEqual(self.controle({}), [])

    def test_texte_qui_se_presente_comme_le_voisin(self):
        f = copy.deepcopy(FICHE_REFERE)
        f["exercice"] = bloc_refere_suspension(L.maintenant().isoformat(timespec="minutes"))
        liberte = "Requête en référé-liberté (article L. 521-2 du code de justice administrative)\n"
        self.assertIn("EXERCICE_TEXTE_DISCORDANT", codes(self.controle(f, liberte), "BLOQUANT"))
        self.assertIn("EXERCICE_TEXTE_SANS_MARQUEUR", codes(self.controle(f, "Requête.\n"), "ALERTE"))

    def test_juge_simule_tient_l_exercice_pour_inadapte(self):
        f = copy.deepcopy(FICHE_REFERE)
        f["exercice"] = bloc_refere_suspension(L.maintenant().isoformat(timespec="minutes"))
        lf = {"sha256": L.sha256_fichier(self.ecriture), "exercice_identifie": "refere_suspension", "exercice_adapte": False,
              "exercice_qui_conviendrait": "requête au fond seule : l'urgence fait défaut"}
        L.ecrire_json(self.r / "ecritures/controle/ref_v1.lecture_froid.json", lf)
        self.assertIn("EXERCICE_JUGE_SIMULE_AUTRE_EXERCICE", codes(self.controle(f), "BLOQUANT"))
        lf["sha256"] = "autre version"
        L.ecrire_json(self.r / "ecritures/controle/ref_v1.lecture_froid.json", lf)
        self.assertNotIn("EXERCICE_JUGE_SIMULE_AUTRE_EXERCICE", codes(self.controle(f)))

    def test_diagnostic_perime_et_sequence(self):
        f = copy.deepcopy(FICHE_REFERE)
        f["exercice"] = bloc_refere_suspension("2026-01-01T09:00")
        b = L.lire_json(self.r / "pieces/bordereau.json")
        b["pieces"][0]["ajoutee_le"] = "2026-02-01T10:00"
        L.ecrire_json(self.r / "pieces/bordereau.json", b)
        self.assertIn("EXERCICE_DIAGNOSTIC_PERIME", codes(self.controle(f), "BLOQUANT"))
        f["exercice"]["date"] = L.maintenant().isoformat(timespec="minutes")
        L.ecrire_json(self.r / "strategie/sequence.json", {"voies": [{"id": "V1", "statut": "retenue", "ecritures": ["ref"], "exercice": "refere_liberte"}]})
        self.assertIn("EXERCICE_HORS_SEQUENCE", codes(self.controle(f), "BLOQUANT"))

    def test_recours_gracieux_et_delai(self):
        """Le défaut de l'épreuve : un recours gracieux posté le dernier jour sans preuve de sa date, ou dans une matière où il ne proroge pas."""
        e = CATALOGUE["recours_administratif_prealable"]
        bloc = E.squelette("recours_administratif_prealable", CATALOGUE)
        bloc.update({"date": L.maintenant().isoformat(timespec="minutes"),
                     "juge_et_stade": {"juge": "le maire", "stade": "recours gracieux", "standard": "réexamen en opportunité et en légalité",
                                       "office": "retrait ou maintien de la décision"},
                     "ce_qu_il_decide": "S'il retire le refus.", "ce_qui_fait_gagner": "Le fait nouveau prouvé.",
                     "cible": {"nature": "acte", "designation": "refus du 2 mars", "acte": "A"},
                     "regime_special": {"applicable": False, "texte": "Droit commun (CRPA, art. L. 411-2)."},
                     "envoi": {"mode": "courrier_simple", "date_prevue": "2099-01-01", "but": "proroger"}})
        bloc["condition_decisive"].update({"preuve": {"pieces": ["1"]}, "ce_qui_la_ferait_tomber": [{"situation": "Envoi le dernier jour.",
                                                                                                    "parade": "Dépôt contre récépissé dès aujourd'hui."}]})
        bloc["exigences_implicites"] = [{"cle": x["cle"], "verifiee": True, "source": "T"} for x in e["exigences_implicites"]]
        bloc["voisins_ecartes"] = [{"exercice": "requete_annulation", "raison": "Le délai court encore ; le recours peut aboutir sans juge."}]
        f = {"type_acte": "courrier_precontentieux", "actes_attaques": [{"id": "A"}], "delai": {"echeance": "2098-12-31T23:59"}, "exercice": bloc}
        k = self.controle(f, "Monsieur le maire,\n")
        self.assertIn("EXERCICE_DELAI_NON_PROTEGE", codes(k, "BLOQUANT"))
        bloc["envoi"] = {"mode": "depot_contre_recepisse", "date_prevue": "2098-12-30", "but": "proroger"}
        self.assertEqual(codes(self.controle(f, "Monsieur le maire,\n"), "BLOQUANT"), set())
        bloc["regime_special"] = {"applicable": True, "texte": "C. urb., art. L. 600-12-2", "proroge_par_recours_administratif": False}
        self.assertIn("EXERCICE_PROROGATION_EXCLUE", codes(self.controle(f, "Monsieur le maire,\n"), "BLOQUANT"))
        del bloc["envoi"]
        self.assertIn("EXERCICE_DELAI_NON_PROTEGE", codes(self.controle(f, "Monsieur le maire,\n"), "BLOQUANT"))

    def test_courrier_sans_diagnostic_et_conservatoire(self):
        self.assertEqual([k["gravite"] for k in self.controle({"type_acte": "courrier_precontentieux"}, "Madame,\n")], ["ALERTE"])
        f = {"type_acte": "requete_fond_admin", "actes_attaques": [{"id": "A"}], "conservatoire": {"echeance": "2026-11-20T23:59"},
             "exercice": {"exercice": "requete_annulation", "date": L.maintenant().isoformat(timespec="minutes"),
                          "regime_special": {"applicable": False, "texte": "Droit commun (CJA, art. R. 421-1)."}}}
        k = self.controle(f, "Requête en annulation.\n")
        self.assertEqual(codes(k, "BLOQUANT"), set(), k)
        self.assertIn("EXERCICE_EXIGENCE_NON_VERIFIEE", codes(k, "ALERTE"))
        del f["exercice"]["regime_special"]
        self.assertIn("EXERCICE_REGIME_SPECIAL_NON_EXAMINE", codes(self.controle(f, "Requête.\n"), "BLOQUANT"))

    def test_delai_proche_sans_conservatoire(self):
        f = {"type_acte": "requete_fond_admin", "actes_attaques": [{"id": "A"}],
             "delai": {"echeance": (L.maintenant() + __import__("datetime").timedelta(hours=20)).strftime("%Y-%m-%dT%H:%M")},
             "exercice": {"exercice": "requete_annulation", "date": L.maintenant().isoformat(timespec="minutes")}}
        self.assertIn("EXERCICE_CONSERVATOIRE_A_EXAMINER", codes(self.controle(f, "Requête.\n"), "ALERTE"))


class TestLigneDeCommande(Base):
    def lancer(self, *args):
        return subprocess.run([PY, str(SCRIPTS / "exercices.py"), *args], cwd=self.r, capture_output=True, text=True, encoding="utf-8")

    def test_commandes(self):
        r = self.lancer("liste")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len(r.stdout.strip().splitlines()), len(ATTENDUS))
        r = self.lancer("squelette", "refere_liberte")
        self.assertEqual(json.loads(r.stdout)["exercice"], "refere_liberte")
        self.assertEqual(self.lancer("fiche", "inconnu").returncode, 1)
        fiche = self.r / "ecritures/controle/ref_v1.fiche.json"
        L.ecrire_json(fiche, FICHE_REFERE)
        self.assertEqual(self.lancer("valider", str(fiche)).returncode, 1)
        L.ecrire_json(fiche, {**FICHE_REFERE, "exercice": bloc_refere_suspension(L.maintenant().isoformat(timespec="minutes"))})
        r = self.lancer("valider", str(fiche))
        self.assertEqual(r.returncode, 0, r.stdout)
        r = self.lancer("controle", str(self.ecriture))
        self.assertEqual(r.returncode, 0, r.stdout)


class TestIntegration(Base):
    """Actifs une fois `integration/exercices.md` appliqué par la session principale."""

    def setUp(self):
        super().setUp()
        if "exercices" not in (SCRIPTS / "gate.py").read_text(encoding="utf-8"):
            self.skipTest("correctif d'intégration non appliqué à gate.py (integration/exercices.md)")

    def test_gate_bloque_sans_diagnostic(self):
        import gate
        L.ecrire_json(self.r / "ecritures/controle/ref_v1.fiche.json", FICHE_REFERE)
        v = gate.controler(self.ecriture)
        self.assertIn("EXERCICE_ABSENT", {k["code"] for k in v["constats"] if k["gravite"] == "BLOQUANT"})
        L.ecrire_json(self.r / "ecritures/controle/ref_v1.fiche.json",
                      {**FICHE_REFERE, "exercice": bloc_refere_suspension(L.maintenant().isoformat(timespec="minutes"))})
        v = gate.controler(self.ecriture)
        self.assertFalse({k["code"] for k in v["constats"] if k["gravite"] == "BLOQUANT" and k["code"].startswith("EXERCICE_")})

    def test_hook_signale_le_diagnostic_incomplet(self):
        if "exercices" not in (SCRIPTS / "hook.py").read_text(encoding="utf-8"):
            self.skipTest("correctif d'intégration non appliqué à hook.py")
        fiche = self.r / "ecritures/controle/ref_v1.fiche.json"
        L.ecrire_json(fiche, FICHE_REFERE)
        ev = {"hook_event_name": "PostToolUse", "cwd": str(self.r), "tool_name": "Write", "tool_input": {"file_path": str(fiche)}}
        r = subprocess.run([PY, str(SCRIPTS / "hook.py")], input=json.dumps(ev), capture_output=True, text=True, encoding="utf-8")
        self.assertIn("EXERCICE_ABSENT", r.stdout)


if __name__ == "__main__":
    unittest.main()
