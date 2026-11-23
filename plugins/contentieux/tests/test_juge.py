"""Tests de la simulation du juge : calibrage équilibré, bornes de date, exclusion de la décision de l'affaire,
conditions du régime remises au rapporteur, accès des simulateurs aux seuls textes. Sans réseau.

Lancer : python -m pytest -q plugins/contentieux/tests/test_juge.py
"""
import json
import os
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
import juridiction as J  # noqa: E402

PY = sys.executable


def dec(date, numero, stade, issue, motif="motif"):
    return {"date": date, "juridiction": "Tribunal X", "numero": numero, "url": f"https://exemple.invalid/{numero}",
            "stade": stade, "issue": issue, "motif": motif}


# Échantillon déséquilibré, comme la pratique publiée : beaucoup de tris, peu d'accueils.
ECHANTILLON = (
    [dec(f"2026-0{m}-1{j}", f"T{m}{j}", "filtrage", "refus", "tri") for m in range(1, 4) for j in range(3)]
    + [dec(f"2026-0{m}-2{j}", f"R{m}{j}", "instruction", "refus", "rejet après audience") for m in range(1, 4) for j in range(2)]
    + [dec("2026-02-05", "A1", "instruction", "accueil", "suspension"), dec("2025-12-01", "A2", "instruction", "accueil", "injonction")]
)


class TestCalibrageEquilibre(unittest.TestCase):
    def test_autant_de_refus_que_d_accueils(self):
        ex = J.equilibrer(ECHANTILLON, par_cote=4)
        self.assertEqual(len(ex["accueils_apres_instruction"]), 2)
        self.assertEqual(len(ex["refus_apres_instruction"]), len(ex["accueils_apres_instruction"]))
        self.assertEqual(len(ex["refus_au_filtre"]), 4)
        # Les plus récents de chaque côté.
        self.assertEqual([d["numero"] for d in ex["accueils_apres_instruction"]], ["A1", "A2"])

    def test_taux_sur_tout_l_echantillon(self):
        tx = J.taux(ECHANTILLON)
        self.assertEqual(tx["decisions_classees"], 17)
        self.assertEqual(tx["refus_au_filtre"], 9)
        self.assertEqual(tx["instruites"], 8)
        self.assertEqual(tx["accueillies_apres_instruction"], 2)
        self.assertEqual(tx["part_accueillie_apres_instruction"], 0.25)

    def test_rendu_montre_refus_accueils_et_taux(self):
        md = J.rendre_calibrage("Tribunal X", "référé-suspension", "2026-06-01", ECHANTILLON, {},
                                [{"query": "q", "decompte_par_solution": {"GRANTED": 3, "DISMISSED": 40}}])
        for titre in ("Refus au filtre", "Refus après instruction : 2", "Accueils après instruction : 2", "Taux observés"):
            self.assertIn(titre, md)
        self.assertIn("GRANTED 3", md)
        self.assertIn("suspension", md)
        self.assertNotIn("\u2014", md)

    def test_un_seul_cote_disponible_est_dit(self):
        refus = [d for d in ECHANTILLON if d["issue"] == "refus"]
        md = J.rendre_calibrage("Tribunal X", "p", "2026-06-01", refus, {})
        self.assertIn("Accueils après instruction : 0", md)
        self.assertIn("Aucune décision publiée de cette sorte", md)


class TestSansIdentiteDeMagistrat(unittest.TestCase):
    """CJA, art. L. 10, al. 4, et COJ, art. L. 111-13 : aucune identité de magistrat ni de greffier dans un calibrage."""

    EXTRAIT = ("Le président du tribunal a désigné Mme Claire Dupont pour statuer sur les demandes de référé. "
               "Rapporteur public : M. Jean Martin. Greffière : Mme Léa Bernard. "
               "4. M. B... ne justifie pas de l'urgence ; M. le préfet n'a pas commis d'erreur.")

    def test_noms_retires_et_droit_intact(self):
        t = J.retirer_noms(self.EXTRAIT)
        for nom in ("Dupont", "Claire", "Martin", "Bernard"):
            self.assertNotIn(nom, t)
        for garde in ("M. B...", "M. le préfet", "ne justifie pas de l'urgence", "Rapporteur public : [nom retiré]"):
            self.assertIn(garde, t)

    def test_calibrage_rendu_sans_nom(self):
        decs = [dec("2026-01-05", "1", "instruction", "refus", self.EXTRAIT), dec("2026-01-06", "2", "instruction", "accueil", self.EXTRAIT)]
        md = J.rendre_calibrage("Tribunal X", "p", "2026-06-01", decs, {})
        self.assertNotIn("Dupont", md)
        self.assertNotIn("par juge", md.lower().replace("aucun décompte par juge", ""))

    def test_profil_sans_decompte_par_juge(self):
        src = (SCRIPTS / "juridiction.py").read_text(encoding="utf-8")
        self.assertNotIn("Par juge désigné", src)
        self.assertNotIn('"juge"', src)

    def test_classe_de_reference_par_procedure(self):
        self.assertTrue(J.cite_procedure("Vu l'article L. 521-1 du code de justice administrative", "L. 521-1"))
        self.assertFalse(J.cite_procedure("Vu l'article L. 521-2 du code de justice administrative", "L. 521-1"))
        self.assertFalse(J.cite_procedure("Vu l'article L. 521-10", "L. 521-1"))


class TestBornes(unittest.TestCase):
    def test_borne_stricte_et_dates_illisibles(self):
        decs = [dec("2026-05-31", "1", "instruction", "refus"), dec("2026-06-01", "2", "instruction", "accueil"),
                dec("2026-07-14", "3", "instruction", "accueil"), dec("", "4", "instruction", "refus"),
                dec("31/05/2026", "5", "instruction", "refus")]
        gardees, ecarts = J.borner(decs, "2026-06-01")
        self.assertEqual([d["numero"] for d in gardees], ["1"])
        self.assertEqual(ecarts["posterieure_ou_egale_a_la_borne"], 2)
        self.assertEqual(ecarts["sans_date"], 2)

    def test_tri_chronologique_inverse_et_doublons(self):
        decs = [dec("2024-01-01", "1", "instruction", "refus"), dec("2025-01-01", "2", "instruction", "refus"),
                dec("2025-01-01", "2", "instruction", "refus")]
        gardees, ecarts = J.borner(decs, "2026-01-01")
        self.assertEqual([d["numero"] for d in gardees], ["2", "1"])
        self.assertEqual(ecarts["doublon"], 1)


class TestExclusionDeLAffaire(unittest.TestCase):
    def test_numero_exclu_sous_toutes_ses_graphies(self):
        decs = [dec("2025-03-01", "24-12.345", "instruction", "accueil"), dec("2025-03-02", "2412346", "instruction", "accueil")]
        for forme in ("24-12.345", "2412345", "24 12.345"):
            gardees, ecarts = J.borner(decs, "2026-01-01", [forme])
            self.assertEqual([d["numero"] for d in gardees], ["2412346"], forme)
            self.assertEqual(ecarts["exclue_decision_de_l_affaire"], 1)

    def test_releve_invalide_refuse(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            f = tmp / "r.json"
            f.write_text(json.dumps({"decisions": [dec("2025-01-01", "1", "fond", "accueil")]}), encoding="utf-8")
            with self.assertRaises(SystemExit):
                J.lire_releve(f)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestCommandeCalibrage(unittest.TestCase):
    """De bout en bout, sur un relevé : rien de postérieur au dépôt ni la décision de l'affaire n'atteint le juge simulé."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.r = self.tmp / "affaire"
        subprocess.run([PY, str(SCRIPTS / "affaire.py"), "init", str(self.r), "--intitule", "Essai", "--client", "X",
                        "--objectif", "Obtenir Z"], check=True, capture_output=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_releve_borne_et_exclusion(self):
        releve = {"juridiction": "Tribunal X, juge des référés", "perimetre": "référé-suspension",
                  "requetes": [{"query": "q", "filtres": {"seat": ["FR.TA.X"]}, "decompte_par_solution": {"GRANTED": 5, "DISMISSED": 50}}],
                  "decisions": [dec("2026-03-01", "2600001", "filtrage", "refus", "MOTIF-TRI"),
                                dec("2026-03-02", "2600002", "instruction", "refus", "MOTIF-REJET"),
                                dec("2026-03-03", "2600003", "instruction", "accueil", "MOTIF-ACCUEIL"),
                                dec("2026-04-10", "2600004", "instruction", "accueil", "MOTIF-POSTERIEUR"),
                                dec("2026-03-04", "2600005", "instruction", "accueil", "MOTIF-AFFAIRE")]}
        (self.r / "procedure").mkdir(exist_ok=True)
        (self.r / "procedure/releve.json").write_text(json.dumps(releve, ensure_ascii=False), encoding="utf-8")
        p = subprocess.run([PY, str(SCRIPTS / "juridiction.py"), "calibrage", "--decisions", "procedure/releve.json",
                            "--avant", "2026-04-10", "--exclure", "2600005", "--code", "TX"],
                           cwd=self.r, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(p.returncode, 0, p.stderr)
        md = (self.r / "procedure/calibrage_TX.md").read_text(encoding="utf-8")
        for present in ("MOTIF-TRI", "MOTIF-REJET", "MOTIF-ACCUEIL", "GRANTED 5", "antérieures au 2026-04-10"):
            self.assertIn(present, md)
        for absent in ("MOTIF-POSTERIEUR", "MOTIF-AFFAIRE", "2600004", "2600005"):
            self.assertNotIn(absent, md)

    def test_conditions_du_regime(self):
        import gate
        gate.charger_regimes_domaines()
        p = subprocess.run([PY, str(SCRIPTS / "juridiction.py"), "conditions", "--type", "refere_suspension"],
                           cwd=self.r, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(p.returncode, 0, p.stderr)
        md = (self.r / "procedure/conditions_refere_suspension.md").read_text(encoding="utf-8")
        for c in gate.REGIMES["refere_suspension"]["conditions"]:
            self.assertIn(c, md)


TRI = """Vu la procédure suivante : M. X demande la suspension de la décision.
Considérant ce qui suit :
1. Aux termes de l'article L. 522-3 du code de justice administrative : « ... ».
2. La requête ne fait état d'aucune circonstance caractérisant une urgence. Il y a lieu de la rejeter en application de l'article L. 522-3 du code de justice administrative, sans instruction.
O R D O N N E :
Article 1er : La requête de M. X est rejetée.
Article 2 : La présente ordonnance sera notifiée à M. X."""

SUSPENSION = """Le juge des référés,
Considérant ce qui suit :
1. Le moyen tiré du défaut d'examen est propre à créer un doute sérieux. L'urgence est caractérisée.
O R D O N N E :
Article 1er : L'exécution de la décision du 2 mars 2026 est suspendue.
Article 2 : L'État versera à M. X la somme de 1 000 euros au titre de l'article L. 761-1 du code de justice administrative.
Article 3 : Le surplus des conclusions est rejeté."""

REJET_AUDIENCE = """Le juge des référés,
Considérant ce qui suit :
1. Aucun des moyens n'est propre à créer, en l'état de l'instruction, un doute sérieux.
O R D O N N E :
Article 1er : La requête est rejetée.
Article 2 : M. X versera à la commune la somme de 800 euros au titre de l'article L. 761-1 du code de justice administrative."""


class TestClassementDesDecisionsPubliees(unittest.TestCase):
    def test_tri(self):
        c = J.classer_decision(TRI)
        self.assertEqual((c["stade"], c["issue"]), ("filtrage", "refus"))

    def test_suspension_avec_surplus_rejete(self):
        c = J.classer_decision(SUSPENSION)
        self.assertEqual((c["stade"], c["issue"]), ("instruction", "accueil"))

    def test_rejet_apres_audience_frais_ignores(self):
        c = J.classer_decision(REJET_AUDIENCE)
        self.assertEqual((c["stade"], c["issue"]), ("instruction", "refus"))


HOOK_INTEGRE = "rapporteur-simule" in (SCRIPTS / "hook.py").read_text(encoding="utf-8")
GATE_INTEGRE = "RAPPORT_RAPPORTEUR_ABSENT" in (SCRIPTS / "gate.py").read_text(encoding="utf-8")


@unittest.skipUnless(HOOK_INTEGRE and GATE_INTEGRE, "correctif integration/juge.patch non appliqué")
class TestIntegration(unittest.TestCase):
    """Actifs une fois integration/juge.patch appliqué : rapport réservé au rapporteur, exigé et lié à l'empreinte."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.r = self.tmp / "affaire"
        subprocess.run([PY, str(SCRIPTS / "affaire.py"), "init", str(self.r), "--intitule", "Essai", "--client", "X",
                        "--objectif", "Obtenir Z"], check=True, capture_output=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def hook(self, ev):
        p = subprocess.run([PY, str(SCRIPTS / "hook.py")], input=json.dumps(ev), capture_output=True, text=True, encoding="utf-8")
        return json.loads(p.stdout) if p.stdout.strip() else {}

    def test_rapport_reserve_au_rapporteur(self):
        ev = {"hook_event_name": "PreToolUse", "cwd": str(self.r), "tool_name": "Write",
              "tool_input": {"file_path": str(self.r / "ecritures/controle/a.rapport_rapporteur.json"), "content": "{}"}}
        self.assertEqual(self.hook(ev)["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertEqual(self.hook({**ev, "agent_type": "contentieux:juge-simule"})["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertEqual(self.hook({**ev, "agent_type": "contentieux:rapporteur-simule"}), {})


class TestSimulateursSansAccesAuxDecisions(unittest.TestCase):
    """Le rapporteur et la formation lisent les textes, jamais les décisions : ils ne peuvent pas retrouver l'affaire."""

    def outils(self, nom):
        t = (PLUGIN / "agents" / f"{nom}.md").read_text(encoding="utf-8")
        m = re.search(r"^tools:\s*(.+)$", t, re.M)
        return {x.strip() for x in m.group(1).split(",")}

    def test_outils(self):
        for nom in ("juge-simule", "rapporteur-simule"):
            o = self.outils(nom)
            self.assertIn("mcp__librejustice__get_norm", o, nom)
            self.assertIn("mcp__librejustice__search_norms", o, nom)
            for interdit in ("mcp__librejustice__search_decisions", "mcp__librejustice__get_decision", "WebFetch", "WebSearch", "Bash"):
                self.assertNotIn(interdit, o, nom)

    def test_consignes(self):
        juge = (PLUGIN / "agents/juge-simule.md").read_text(encoding="utf-8")
        rap = (PLUGIN / "agents/rapporteur-simule.md").read_text(encoding="utf-8")
        self.assertNotIn("position par défaut est le rejet", juge)
        self.assertIn("rapport_rapporteur.json", juge)
        self.assertIn("rapport_rapporteur.json", rap)
        self.assertIn("conditions_<type>.md", rap)
        for t in (juge, rap):
            self.assertNotIn("\u2014", t)


if __name__ == "__main__":
    unittest.main()
