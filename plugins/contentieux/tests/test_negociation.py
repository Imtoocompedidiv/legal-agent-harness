"""Tests du plan de négociation et de persuasion (strategie/negociation.json) : schéma, règles croisées, contrôle avant acte.

Données synthétiques, aucun appel réseau. Lancer : python -m pytest -q plugins/contentieux/tests/test_negociation.py
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
import lib_affaire as L  # noqa: E402
import negociation as N  # noqa: E402

PY = sys.executable
SKILL = PLUGIN / "skills" / "negociation-et-persuasion"


def plan_complet() -> dict:
    return {
        "schema": "negociation/1", "date": "2026-11-10T10:00", "actes_couverts": ["requete_indemnitaire"], "etat": "en_cours",
        "parties": [
            {"id": "P1", "role": "client", "nature": "personne_physique", "designation": "Requérant",
             "position_affichee": "Réparation intégrale des préjudices nés de la décision annulée.",
             "interets": [{"interet": "Être indemnisé vite", "priorite": "haute", "statut": "piece_du_dossier", "sources": ["S1"]}]},
            {"id": "P2", "role": "adversaire", "nature": "personne_publique", "personne_publique": "etat", "designation": "Préfecture de Nullepart",
             "position_affichee": "Rejet de la demande.",
             "interets": [{"interet": "Ne pas payer ce qui n'est pas dû", "priorite": "haute", "statut": "droit_positif", "sources": ["S2"]}],
             "sans_perdre_la_face": ["Payer en exécution d'un jugement d'annulation devenu définitif, sans reconnaître d'autre faute."]}],
        "repli": [
            {"partie": "P1", "alternative": "Jugement au fond", "issue_probable": "Condamnation limitée aux troubles", "montant_bas": 0,
             "montant_haut": 4000, "delai": "plusieurs mois", "couts": "honoraires non couverts", "valeur_nette": "faible au regard des frais",
             "sources": ["S2"]},
            {"partie": "P2", "alternative": "Défense au fond", "issue_probable": "Risque de condamnation et de frais", "delai": "plusieurs mois",
             "couts": "charge du service", "valeur_nette": "coût probable supérieur à la cible du client", "sources": ["S2"]}],
        "voies_amiables": [
            {"id": "V1", "voie": "mediation_judiciaire", "ouverte": True, "obligatoire": False, "actes": ["requete_indemnitaire"],
             "fondement": "CJA, art. L. 213-7", "effet_sur_delais": "sans_objet", "repli_compare": "Accord possible au-dessus de la fourchette nette",
             "retenue": True, "raison": "Tiers qui évalue, confidentialité"},
            {"id": "V2", "voie": "defenseur_des_droits", "ouverte": True, "obligatoire": False, "fondement": "loi organique n° 2011-333",
             "effet_sur_delais": "aucun", "repli_compare": "Aucun gain sur le jugement probable", "retenue": False, "raison": "Redondant"}],
        "options": [{"id": "O1", "description": "Somme globale pour solde de tout compte", "acceptable_client": True, "fondement": "Calcul par chef"}],
        "offre": {"sens": "nous_recevons", "premier_a_ouvrir": "nous", "raison": "Évaluation faite, litige portant sur une somme (N11)",
                  "premiere_offre": {"contenu": "Somme globale", "montant": 8000, "calcul": "Troubles, frais, intérêts", "sources": ["S2"],
                                     "formulation": "Le requérant propose de régler le litige pour une somme calculée chef par chef."},
                  "cible": {"contenu": "Somme globale", "montant": 5200, "justification": "Haut de la fourchette nette"},
                  "point_de_reservation": {"contenu": "Somme globale", "montant": 3100, "justification": "Jugement probable net"}},
        "contreparties": [
            {"id": "C1", "nous_cedons": "Réduction des troubles", "montant": 1500, "en_echange_de": "Chiffrage du chef sur toute la durée",
             "condition": "Si la préfecture chiffre ce chef", "ordre": 1, "raison_exterieure": "Barème des décisions lues"},
            {"id": "C2", "nous_cedons": "Réduction des frais", "montant": 1000, "en_echange_de": "Paiement dans les deux mois",
             "condition": "Si l'engagement de paiement est écrit", "ordre": 2}],
        "interlocuteurs": [{"id": "I1", "partie": "P2", "fonction": "Préfet ou délégataire", "pouvoir": "signe", "canal": "mediateur"}],
        "calendrier": [{"date": "2026-12-15", "evenement": "Réunion de médiation", "type": "reunion"}],
        "conditions_de_forme": [
            {"type": "ecrit", "exigence": "Protocole écrit", "source": "C. civ., art. 2044"},
            {"type": "absence_de_liberalite", "exigence": "Fondement de la dette et calcul par chef", "source": "CE, Sect., 19 mars 1971, Mergui"},
            {"type": "habilitation_signataire", "exigence": "Délégation visée", "source": "CRPA, art. L. 423-1"},
            {"type": "homologation", "exigence": "Conclusions d'homologation", "source": "CJA, art. L. 213-4"},
            {"type": "desistement", "exigence": "Désistement subordonné à l'homologation", "source": "CE, Ass., 11 juillet 2008, n° 287354"}],
        "leviers": [{"levier": "Mémoire au fond prêt et daté", "nature": "voie_de_droit_liee", "source": "CJA, art. R. 213-9"}],
        "risques": [{"id": "R1", "risque": "Refus d'homologation", "parade": "Rédaction chef par chef", "gravite": "serieuse"}],
        "persuasion": [
            {"id": "PS1", "decideur": "mediateur", "ce_qu_il_doit_croire": "Le principe de la dette est acquis", "raison_de_decider": "Jugement définitif",
             "moyen_de_decider": "Proposer une somme dans la fourchette", "faits_defavorables": [
                 {"fait": "Relaxe pour nullité seulement", "traitement": "fait_posterieur_ou_regle_superieure"}], "forme": "Note chiffrée"},
            {"id": "PS2", "decideur": "juge", "actes": ["requete_indemnitaire"], "ce_qu_il_doit_croire": "L'illégalité est jugée",
             "raison_de_decider": "Autorité de la chose jugée", "moyen_de_decider": "Condamnation chiffrée", "faits_defavorables": [],
             "forme": "Mémoire court"}],
        "sources": [{"id": "S1", "reference": "Pièce 5", "lu": "en_entier"}, {"id": "S2", "reference": "Décision de principe synthétique", "lu": "en_entier"}],
    }


def codes(constats, gravite=None):
    return {k["code"] for k in constats if gravite is None or k["gravite"] == gravite}


class TestValidation(unittest.TestCase):
    def test_plan_complet_valide(self):
        self.assertEqual(N.valider(plan_complet()), [])
        p = plan_complet()
        p["date"] = L.maintenant().isoformat(timespec="minutes")  # heure du poste avec son décalage, comme l'écrit affaire.py
        self.assertEqual(N.valider(p), [])

    def test_squelette_invalide_et_schema_coherent(self):
        r = N.valider(copy.deepcopy(N.SQUELETTE))
        self.assertTrue(r and codes(r) == {"NEGOCIATION_INVALIDE"})
        schema = json.loads((PLUGIN / "references/schemas/negociation.v1.schema.json").read_text(encoding="utf-8"))
        refs = set(re.findall(r'"#/\$defs/([a-z_]+)"', json.dumps(schema)))
        self.assertTrue(refs <= set(schema["$defs"]), refs - set(schema["$defs"]))
        self.assertEqual(set(schema["required"]) - set(schema["properties"]), set())

    def test_identifiants_et_sources(self):
        p = plan_complet()
        p["risques"].append({"id": "P1", "risque": "x", "parade": "y"})
        self.assertIn("NEGOCIATION_INVALIDE", codes(N.valider(p)))  # motif d'identifiant du schéma
        p = plan_complet()
        p["options"].append({"id": "O1", "description": "d", "acceptable_client": False, "fondement": "f"})
        p["repli"][0]["sources"] = ["S9"]
        p["offre"]["premiere_offre"]["sources"] = ["S1"]
        p["sources"][0]["lu"] = "resume"
        r = codes(N.valider(p))
        self.assertTrue({"ID_DOUBLE", "SOURCE_INCONNUE", "SOURCE_NON_LUE"} <= r, r)

    def test_parties_repli_et_face(self):
        p = plan_complet()
        p["repli"][1]["partie"] = "P1"
        del p["parties"][1]["sans_perdre_la_face"]
        r = codes(N.valider(p), "BLOQUANT")
        self.assertTrue({"REPLI_ABSENT", "FACE_ADVERSAIRE_NON_ETUDIEE"} <= r, r)

    def test_effet_des_voies_sur_les_delais(self):
        p = plan_complet()
        p["voies_amiables"][1]["effet_sur_delais"] = "suspend"
        p["voies_amiables"].append({"id": "V3", "voie": "mediation_conventionnelle", "ouverte": True, "obligatoire": False, "fondement": "C. civ., art. 2238",
                                    "effet_sur_delais": "interrompt", "repli_compare": "r", "retenue": False, "raison": "r"})
        r = N.valider(p)
        self.assertEqual(sum(1 for k in r if k["code"] == "EFFET_DELAI_INEXACT"), 2, r)
        p = plan_complet()
        p["voies_amiables"][1]["effet_sur_delais"] = "interrompt"
        self.assertEqual(codes(N.valider(p)), {"EFFET_DELAI_A_JUSTIFIER"})

    def test_delai_non_protege(self):
        p = plan_complet()
        p["voies_amiables"][1]["retenue"] = True
        p["calendrier"].append({"date": "2027-01-18", "evenement": "Fin du délai de recours", "type": "delai_contentieux"})
        self.assertIn("DELAI_NON_PROTEGE", codes(N.valider(p), "BLOQUANT"))
        p["voies_amiables"][1]["acte_conservatoire"] = "Recours gracieux le 10 janvier 2027"
        self.assertNotIn("DELAI_NON_PROTEGE", codes(N.valider(p)))
        p["voies_amiables"][1]["acte_conservatoire"] = ""
        p["calendrier"][-1]["protege_par"] = "Requête déposée"
        self.assertNotIn("DELAI_NON_PROTEGE", codes(N.valider(p)))

    def test_prealable_obligatoire(self):
        p = plan_complet()
        p["voies_amiables"].append({"id": "V3", "voie": "conciliation_conciliateur", "ouverte": True, "obligatoire": True, "fondement": "CPC, art. 750-1",
                                    "effet_sur_delais": "suspend", "repli_compare": "r", "retenue": False, "raison": "r"})
        self.assertIn("PREALABLE_AMIABLE_NON_TENTE", codes(N.valider(p), "BLOQUANT"))
        p["voies_amiables"][-1]["dispense"] = {"motif": "Urgence manifeste", "source": "CPC, art. 750-1, 3°"}
        self.assertNotIn("PREALABLE_AMIABLE_NON_TENTE", codes(N.valider(p)))

    def test_offre_ordonnee_selon_le_sens(self):
        p = plan_complet()
        p["offre"]["point_de_reservation"]["montant"] = 6000
        self.assertIn("OFFRE_INCOHERENTE", codes(N.valider(p), "BLOQUANT"))
        p = plan_complet()
        p["offre"]["sens"] = "nous_payons"
        p["parties"][1]["nature"] = "personne_morale_privee"
        self.assertIn("OFFRE_INCOHERENTE", codes(N.valider(p)))
        p["offre"]["premiere_offre"]["montant"], p["offre"]["point_de_reservation"]["montant"] = 3100, 8000
        p["contreparties"] = []
        self.assertNotIn("OFFRE_INCOHERENTE", codes(N.valider(p)))
        p = plan_complet()
        p["offre"]["derniere_offre_adverse"] = {"contenu": "Offre de la préfecture", "montant": 3500, "date": "2026-11-12"}
        self.assertEqual(codes(N.valider(p)), {"OFFRE_ADVERSE_DANS_LA_ZONE"})

    def test_concessions(self):
        p = plan_complet()
        p["contreparties"][1]["en_echange_de"] = "rien"
        p["contreparties"][1]["montant"] = 2000
        r = N.valider(p)
        self.assertIn("CONCESSION_SANS_CONTREPARTIE", codes(r, "BLOQUANT"))
        self.assertIn("CONCESSIONS_NON_DECROISSANTES", codes(r, "ALERTE"))

    def test_accord_avec_une_personne_publique(self):
        p = plan_complet()
        p["conditions_de_forme"] = [c for c in p["conditions_de_forme"] if c["type"] not in ("absence_de_liberalite", "desistement")]
        r = N.valider(p)
        self.assertIn("ACCORD_PUBLIC_SANS_FONDEMENT", codes(r, "BLOQUANT"))
        self.assertIn("ECHEC_HOMOLOGATION_NON_PREVU", codes(r, "ALERTE"))
        p = plan_complet()
        p["offre"]["premiere_offre"]["montant"], p["offre"]["cible"]["montant"], p["offre"]["point_de_reservation"]["montant"] = 600000, 520000, 400000
        p["contreparties"] = []
        self.assertIn("COMITE_TRANSACTION_REQUIS", codes(N.valider(p), "BLOQUANT"))
        q = copy.deepcopy(p)
        q["offre"]["premiere_offre"]["montant"], q["offre"]["cible"]["montant"] = 500000, 500000  # le seuil doit être dépassé
        self.assertNotIn("COMITE_TRANSACTION_REQUIS", codes(N.valider(q)))
        p["conditions_de_forme"].append({"type": "comite_transaction", "exigence": "Avis du comité", "source": "CRPA, art. R. 423-3"})
        self.assertEqual(N.valider(p), [])
        p["parties"][1]["personne_publique"] = "collectivite"
        p["conditions_de_forme"].pop()
        self.assertNotIn("COMITE_TRANSACTION_REQUIS", codes(N.valider(p)))

    def test_signataire_et_accord_ecrit(self):
        p = plan_complet()
        p["interlocuteurs"][0]["pouvoir"] = "propose"
        p["etat"] = "accord_conclu"
        p["conditions_de_forme"] = [c for c in p["conditions_de_forme"] if c["type"] != "ecrit"]
        self.assertEqual(codes(N.valider(p)), {"SIGNATAIRE_NON_IDENTIFIE", "ACCORD_SANS_ECRIT"})
        p["interlocuteurs"][0]["chaine_de_validation"] = "Projet visé par le service juridique, signé par le délégataire"
        self.assertNotIn("SIGNATAIRE_NON_IDENTIFIE", codes(N.valider(p)))

    def test_probabilite_aveu_menace(self):
        p = plan_complet()
        p["repli"][0]["issue_probable"] = "Nos chances sont de 60 % devant le tribunal"
        p["offre"]["premiere_offre"]["formulation"] = "Notre dossier est fragile, nous admettons une part de responsabilité."
        p["contreparties"][0]["formulation"] = "Sans accord, nous saisirons la presse de ces pratiques."
        p["leviers"].append({"levier": "Plainte pénale si refus", "nature": "voie_de_droit_liee", "source": "x"})
        r = N.valider(p)
        self.assertTrue({"PROBABILITE_INTERDITE", "AVEU_DE_FAIBLESSE", "MENACE_ILLICITE"} <= codes(r, "BLOQUANT"), r)
        self.assertEqual(sum(1 for k in r if k["code"] == "MENACE_ILLICITE"), 2)

    def test_pas_de_faux_positif_sur_les_formules_courantes(self):
        p = plan_complet()
        p["offre"]["premiere_offre"]["formulation"] = ("Nous vous signalons que le décompte révèle une erreur ; la faiblesse de l'argument "
                                                       "adverse tient à la date de l'acte. Le contrat a été dénoncé le 3 mars.")
        p["persuasion"][0]["message_cle"] = "L'illégalité est jugée ; seul le montant reste à fixer."
        self.assertEqual(N.valider(p), [])

    def test_actes_designes_par_description(self):
        p = plan_complet()
        p["actes_couverts"] = ["Note au médiateur avant la réunion"]
        self.assertEqual(codes(N.valider(p)), {"ACTES_NON_NOMMES"})


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.r = self.tmp / "affaire"
        subprocess.run([PY, str(SCRIPTS / "affaire.py"), "init", str(self.r), "--intitule", "Essai", "--client", "X", "--objectif", "Obtenir Z"],
                       check=True, capture_output=True)
        self.brouillon = self.r / "ecritures/brouillons/requete_indemnitaire_v2.md"
        self.brouillon.parent.mkdir(parents=True, exist_ok=True)
        self.brouillon.write_text("Requête.\n1. L'arrêté a été annulé par un jugement définitif.\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def controle(self, fiche=None, juridictionnel=True, texte=None, brouillon=None):
        out = []
        N.controler(self.r, brouillon or self.brouillon, fiche or {}, lambda code, gravite, message, **_: out.append({"code": code, "gravite": gravite}),
                    juridictionnel=juridictionnel, texte=texte)
        return out

    def poser(self, plan):
        L.ecrire_json(self.r / N.FICHIER, plan)


class TestControleActe(Base):
    def test_absent_bloque_sauf_urgence_motivee(self):
        self.assertEqual(codes(self.controle()), {"NEGOCIATION_ABSENTE"})
        u = {"urgence_amiable": {"motif": "La décision s'exécute le 20 novembre ; seul le juge des référés peut l'arrêter avant.",
                                 "source": "CJA, art. L. 521-1"}}
        self.assertEqual([k["gravite"] for k in self.controle(u)], ["ALERTE"])
        self.assertEqual(codes(self.controle({"urgence_amiable": {"motif": "urgent", "source": ""}})), {"NEGOCIATION_ABSENTE"})
        self.assertEqual(self.controle(juridictionnel=False), [])

    def test_plan_conforme_puis_tournants(self):
        self.poser(plan_complet())
        self.assertEqual(self.controle(), [])
        autre = self.r / "ecritures/brouillons/appel_v1.md"
        self.assertEqual(codes(self.controle(brouillon=autre)), {"NEGOCIATION_HORS_ACTE", "PERSUASION_JUGE_ABSENTE"})
        L.ecrire_json(self.r / "strategie/ligne.json", {"date": "2026-11-15T09:00", "objectif": "o"})
        self.assertEqual(codes(self.controle()), {"NEGOCIATION_PERIMEE"})
        p = plan_complet()
        p["ligne_examinee"] = "2026-11-15T09:00"
        self.poser(p)
        self.assertEqual(self.controle(), [])

    def test_plan_invalide_remonte(self):
        p = plan_complet()
        p["etat"] = "inconnu"
        self.poser(p)
        self.assertEqual(codes(self.controle()), {"NEGOCIATION_INVALIDE"})
        (self.r / N.FICHIER).write_text("{", encoding="utf-8")
        self.assertEqual(codes(self.controle()), {"NEGOCIATION_INVALIDE"})

    def test_chiffres_de_la_negociation_hors_de_l_ecrit(self):
        self.poser(plan_complet())
        r = self.controle(texte="2. En médiation, le requérant accepterait 5 200 euros.\n")
        self.assertIn("NEGOCIATION_DANS_L_ECRIT", codes(r, "BLOQUANT"))
        self.assertIn("NEGOCIATION_EVOQUEE", codes(r, "ALERTE"))
        # La première offre, qui peut être la demande, n'est pas un chiffre secret.
        self.assertEqual(self.controle(texte="Le requérant demande 8 000 euros.\n"), [])

    def test_lettre_a_l_adversaire(self):
        self.poser(plan_complet())
        lettre = self.r / "ecritures/brouillons/lettre_prefet_v1.md"
        r = self.controle(juridictionnel=False, brouillon=lettre,
                          texte="Notre dossier est fragile ; nous accepterions 3 100 euros, faute de quoi la presse sera informée.")
        self.assertTrue({"SEUIL_REVELE", "AVEU_DE_FAIBLESSE"} <= codes(r, "BLOQUANT"), r)
        self.assertIn("MENACE_ILLICITE", codes(r, "ALERTE"))

    def test_diligences_amiables_obligatoires(self):
        p = plan_complet()
        p["voies_amiables"].append({"id": "V3", "voie": "conciliation_conciliateur", "ouverte": True, "obligatoire": True, "actes": ["requete_indemnitaire"],
                                    "fondement": "CPC, art. 750-1", "effet_sur_delais": "suspend", "repli_compare": "r", "retenue": True, "raison": "r"})
        self.poser(p)
        self.assertEqual(codes(self.controle(texte="Assignation.\n")), {"DILIGENCES_AMIABLES_NON_MENTIONNEES"})
        self.assertEqual(self.controle(texte="Assignation. Une tentative de conciliation a échoué le 3 octobre (pièce 4).\n"), [])


class TestLigneDeCommande(Base):
    def test_valider_et_squelette(self):
        r = subprocess.run([PY, str(SCRIPTS / "negociation.py"), "valider"], cwd=self.r, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 1)
        self.poser(plan_complet())
        r = subprocess.run([PY, str(SCRIPTS / "negociation.py"), "valider"], cwd=self.r, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = subprocess.run([PY, str(SCRIPTS / "negociation.py"), "squelette"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(json.loads(r.stdout)["schema"], "negociation/1")
        r = subprocess.run([PY, str(SCRIPTS / "negociation.py"), "controle", str(self.brouillon)], cwd=self.r, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class TestReferences(unittest.TestCase):
    """Le skill ne cite que des règles qui existent, et ses fichiers respectent la charte (pas de tiret cadratin)."""

    def test_regles_citees_existent(self):
        refs = {"D": "droit_amiable.md", "L": "levier_limites.md", "N": "negociation_litterature.md", "P": "persuasion_litterature.md"}
        definies = {}
        for prefixe, nom in refs.items():
            texte = (SKILL / "references" / nom).read_text(encoding="utf-8")
            definies[prefixe] = set(re.findall(r"^\*\*" + prefixe + r"(\d+)\.", texte, re.M))
            self.assertTrue(definies[prefixe], nom)
        for f in [SKILL / "SKILL.md", PLUGIN / "agents/negociateur.md", SKILL / "references/droit_amiable.md", SKILL / "references/levier_limites.md"]:
            for prefixe, num in re.findall(r"(?<![A-Za-z\-])([DLNP])(\d+)\b", f.read_text(encoding="utf-8")):
                self.assertIn(num, definies[prefixe], f"{f.name} cite {prefixe}{num}")

    def test_charte(self):
        fichiers = [SKILL / "SKILL.md", PLUGIN / "agents/negociateur.md", PLUGIN / "scripts/negociation.py",
                    PLUGIN / "references/schemas/negociation.v1.schema.json", *sorted((SKILL / "references").glob("*.md"))]
        for f in fichiers:
            self.assertNotIn("—", f.read_text(encoding="utf-8"), f.name)


class TestIntegration(Base):
    """Actifs une fois `integration/negociation.md` appliqué par la session principale."""

    def setUp(self):
        super().setUp()
        source = (SCRIPTS / "gate.py").read_text(encoding="utf-8")
        if "negociation" not in source:
            self.skipTest("correctif d'intégration non appliqué à gate.py")

    def test_gate_bloque_sans_plan(self):
        import gate
        L.ecrire_json(self.r / "ecritures/controle/requete_indemnitaire_v2.fiche.json", {"type_acte": "requete_fond_admin"})
        v = gate.controler(self.brouillon)
        self.assertIn("NEGOCIATION_ABSENTE", {k["code"] for k in v["constats"] if k["gravite"] == "BLOQUANT"})
        self.poser(plan_complet())
        v = gate.controler(self.brouillon)
        self.assertFalse({k["code"] for k in v["constats"]} & {"NEGOCIATION_ABSENTE", "NEGOCIATION_HORS_ACTE", "NEGOCIATION_INVALIDE"})

    def test_hook_valide_le_plan(self):
        if "negociation" not in (SCRIPTS / "hook.py").read_text(encoding="utf-8"):
            self.skipTest("correctif d'intégration non appliqué à hook.py")
        p = plan_complet()
        p["offre"]["premiere_offre"]["formulation"] = "Notre dossier est fragile."
        self.poser(p)
        ev = {"hook_event_name": "PostToolUse", "cwd": str(self.r), "tool_name": "Write", "tool_input": {"file_path": str(self.r / N.FICHIER)}}
        r = subprocess.run([PY, str(SCRIPTS / "hook.py")], input=json.dumps(ev), capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(json.loads(r.stdout).get("decision"), "block")


if __name__ == "__main__":
    unittest.main()
