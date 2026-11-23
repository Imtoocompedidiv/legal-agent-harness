"""Posture : registre des positions, rappel du hook, références du skill rapport-de-force, sondes POST2, correctif d'intégration.

Sans réseau. Les tests d'intégration appliquent integration/posture.patch à une copie du plugin, sauf si le correctif
est déjà appliqué au plugin courant, auquel cas ils portent sur lui.
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
SKILL = PLUGIN / "skills" / "rapport-de-force"
BANC = PLUGIN.parents[1] / "validation" / "banc"
sys.path.insert(0, str(SCRIPTS))
import lib_affaire as L  # noqa: E402
import positions as P  # noqa: E402

PY = sys.executable


def registre() -> dict:
    """Registre conforme : une position révisée sur une pièce, un désaccord examiné, une instruction consignée."""
    return {"schema": "positions/1", "positions": [{
        "id": "P1", "objet": "Assigner en référé-provision pour la facture 052", "statut": "en_vigueur", "date": "2026-11-10T18:00",
        "position": "Assigner en référé-provision pour les trois factures.",
        "fondement": [{"type": "piece", "ref": "pièce 8"}, {"type": "source", "ref": "S1"}],
        "ferait_changer": ["une contestation écrite et motivée de la livraison par Hexagone", "un paiement partiel"],
        "revisions": [{"date": "2026-11-19T09:00", "ancienne_position": "Ne pas assigner pour la facture 052.",
                       "nouvelle_position": "Assigner en référé-provision pour les trois factures.",
                       "element": {"type": "piece", "ref": "pièce 8", "date": "2026-11-18", "connu_le": "2026-11-18",
                                   "description": "courriel du président d'Hexagone qui reconnaît la livraison et la dette"},
                       "motif": "La reconnaissance écrite de la livraison rend l'obligation non sérieusement contestable."}],
        "desaccords": [{"date": "2026-11-12", "objection": "Le gérant veut assigner tout de suite.", "examen": "Aucun élément nouveau.",
                        "issue": "maintenue"}],
        "instructions": [{"date": "2026-11-12", "instruction": "Envoyer une relance amiable.", "risque_dit": "Elle prévient l'adversaire."}],
    }]}


def codes(constats, gravite=None):
    return {k["code"] for k in constats if gravite is None or k["gravite"] == gravite}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.r = self.tmp / "affaire"
        subprocess.run([PY, str(SCRIPTS / "affaire.py"), "init", str(self.r), "--intitule", "Essai", "--client", "X", "--objectif", "Être payé"],
                       check=True, capture_output=True)
        L.ecrire_json(self.r / "etat/sources.json", {"sources": [{"id": "S1", "type": "texte", "reference": "CPC, art. 835", "lu_en_entier": True}]})
        L.ecrire_json(self.r / "pieces/bordereau.json", {"pieces": [{"cote": "8", "fichier": "p8.pdf", "sha256": "x", "description": "courriel"}]})

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def poser(self, doc):
        L.ecrire_json(self.r / P.FICHIER, doc)


class TestValidation(Base):
    def test_registre_conforme(self):
        self.assertEqual(P.valider(registre(), self.r), [])
        self.assertEqual(P.valider(registre()), [])

    def test_structure(self):
        self.assertEqual(codes(P.valider([])), {"POSITIONS_INVALIDE"})
        doc = registre()
        doc["positions"].append(copy.deepcopy(doc["positions"][0]))
        self.assertIn("ID_DOUBLE", codes(P.valider(doc)))
        doc = registre()
        doc["positions"][0]["date"] = "hier soir"
        self.assertIn("DATE_INVALIDE", codes(P.valider(doc)))
        doc = registre()
        doc["positions"][0]["statut"] = "close"
        self.assertIn("POSITIONS_INVALIDE", codes(P.valider(doc)))

    def test_fondement_et_declencheurs_requis(self):
        doc = registre()
        doc["positions"][0]["fondement"] = []
        doc["positions"][0]["ferait_changer"] = [""]
        self.assertEqual(codes(P.valider(doc)), {"FONDEMENT_ABSENT", "DECLENCHEURS_ABSENTS"})

    def test_revision_sans_element(self):
        doc = registre()
        del doc["positions"][0]["revisions"][0]["element"]
        self.assertIn("REVISION_SANS_ELEMENT", codes(P.valider(doc), "BLOQUANT"))
        doc = registre()
        doc["positions"][0]["revisions"][0]["motif"] = ""
        self.assertIn("REVISION_SANS_MOTIF", codes(P.valider(doc), "BLOQUANT"))

    def test_un_desaccord_n_est_pas_un_element(self):
        for element in ({"type": "desaccord", "ref": "message de la cliente", "connu_le": "2026-11-19"},
                        {"type": "fait", "ref": "La cliente n'est pas d'accord et insiste", "connu_le": "2026-11-19"},
                        {"type": "fait", "ref": "avis du comptable du client", "description": "il me trouve trop prudent", "connu_le": "2026-11-19"}):
            doc = registre()
            doc["positions"][0]["revisions"][0]["element"] = element
            self.assertIn("DESACCORD_N_EST_PAS_UN_ELEMENT", codes(P.valider(doc), "BLOQUANT"), element)

    def test_element_deja_connu(self):
        doc = registre()
        doc["positions"][0]["revisions"][0]["element"]["connu_le"] = "2026-11-02"
        self.assertIn("ELEMENT_DEJA_CONNU", codes(P.valider(doc), "BLOQUANT"))
        doc["positions"][0]["revisions"][0]["erreur"] = "La pièce 8 avait été mal lue : elle reconnaît la livraison."
        self.assertNotIn("ELEMENT_DEJA_CONNU", codes(P.valider(doc)))
        doc = registre()
        doc["positions"][0]["revisions"][0]["element"] = {"type": "rumeur", "ref": "on dit que", "connu_le": "2026-11-19"}
        self.assertIn("ELEMENT_TYPE_INCONNU", codes(P.valider(doc)))

    def test_sources_et_pieces_du_dossier(self):
        doc = registre()
        doc["positions"][0]["revisions"][0]["element"] = {"type": "source", "ref": "S9", "connu_le": "2026-11-19", "description": "arrêt invoqué par la cliente"}
        self.assertIn("SOURCE_NON_LUE", codes(P.valider(doc, self.r), "BLOQUANT"))
        self.assertNotIn("SOURCE_NON_LUE", codes(P.valider(doc)))
        doc = registre()
        doc["positions"][0]["fondement"] = [{"type": "piece", "ref": "pièce 12"}]
        self.assertIn("PIECE_HORS_BORDEREAU", codes(P.valider(doc, self.r), "ALERTE"))

    def test_revision_hors_declencheurs_signalee(self):
        doc = registre()
        doc["positions"][0]["ferait_changer"] = ["perte de rémunération prouvée"]
        self.assertEqual(codes(P.valider(doc)), {"REVISION_HORS_DECLENCHEURS"})
        self.assertEqual({k["gravite"] for k in P.valider(doc)}, {"ALERTE"})

    def test_desaccords_et_instructions(self):
        doc = registre()
        doc["positions"][0]["desaccords"][0]["examen"] = ""
        self.assertIn("DESACCORD_SANS_EXAMEN", codes(P.valider(doc)))
        doc = registre()
        doc["positions"][0]["desaccords"][0].update({"issue": "revisee", "date": "2026-11-25"})
        self.assertIn("DESACCORD_SANS_EXAMEN", codes(P.valider(doc)))
        doc = registre()
        doc["positions"][0]["instructions"][0]["risque_dit"] = ""
        self.assertIn("INSTRUCTION_INCOMPLETE", codes(P.valider(doc)))


class TestControleEtRappel(Base):
    def controle(self):
        out = []
        P.controler(self.r, lambda code, gravite, message, **_: out.append({"code": code, "gravite": gravite}))
        return out

    def test_controle_avant_acte(self):
        self.assertEqual(self.controle(), [{"code": "POSITIONS_ABSENTES", "gravite": "ALERTE"}])
        self.poser(registre())
        self.assertEqual(self.controle(), [])
        doc = registre()
        doc["positions"][0]["revisions"][0]["element"] = {"type": "desaccord", "ref": "le client insiste", "connu_le": "2026-11-19"}
        self.poser(doc)
        self.assertIn("DESACCORD_N_EST_PAS_UN_ELEMENT", codes(self.controle(), "BLOQUANT"))
        (self.r / P.FICHIER).write_text("{", encoding="utf-8")
        self.assertEqual(codes(self.controle()), {"POSITIONS_INVALIDE"})

    def test_rappel_au_tour_de_la_contestation(self):
        self.poser(registre())
        lignes = P.rappel(self.r, "Je ne suis pas d'accord. Revoyez votre position, mon comptable vous trouve trop prudent.")
        self.assertTrue(any("élément nouveau" in l for l in lignes), lignes)
        self.assertTrue(any(l.startswith("Position P1") and "ferait changer" in l for l in lignes), lignes)
        self.assertEqual(P.rappel(self.r, "Lis dossier_remis.md et résume la chronologie."), [])
        self.assertTrue(any("frontière" in l for l in P.rappel(self.r, "Écris-lui qu'on le dénoncera à l'URSSAF s'il ne paie pas.")))
        self.assertTrue(any("adversaire" in l for l in P.rappel(self.r, "Rédige la lettre de mise en demeure à la société Hexagone.")))


class TestLigneDeCommande(Base):
    def test_valider_et_squelette(self):
        r = subprocess.run([PY, str(SCRIPTS / "positions.py"), "valider"], cwd=self.r, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 1)
        self.poser(registre())
        r = subprocess.run([PY, str(SCRIPTS / "positions.py"), "valider"], cwd=self.r, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = subprocess.run([PY, str(SCRIPTS / "positions.py"), "squelette"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(json.loads(r.stdout)["schema"], "positions/1")


class TestReferences(unittest.TestCase):
    """Les règles citées existent, les codes annoncés sont ceux du script, la charte est tenue."""

    REFS = {"V": "arsenal.md", "X": "limites.md", "S": "complaisance.md", "M": "complaisance.md"}

    def test_regles_citees_existent(self):
        definies = {}
        for prefixe, nom in self.REFS.items():
            definies[prefixe] = set(re.findall(r"^\*\*" + prefixe + r"(\d+)\.", (SKILL / "references" / nom).read_text(encoding="utf-8"), re.M))
            self.assertTrue(definies[prefixe], prefixe)
        self.assertEqual(definies["V"], {str(i) for i in range(1, 33)})
        textes = [SKILL / "SKILL.md", *sorted((SKILL / "references").glob("*.md")), PLUGIN / "integration" / "posture.md"]
        for f in textes:
            for prefixe, num in re.findall(r"(?<![A-Za-z\-.])([VXSM])(\d+)\b", f.read_text(encoding="utf-8")):
                self.assertIn(num, definies[prefixe], f"{f.name} cite {prefixe}{num}")

    def test_codes_annonces_emis(self):
        source = (SCRIPTS / "positions.py").read_text(encoding="utf-8")
        emis = set(re.findall(r'_k\("([A-Z_]+)"', source)) | set(re.findall(r'c\("([A-Z_]+)"', source))
        annonces = set(re.findall(r"`([A-Z][A-Z_]{5,})`", (SKILL / "SKILL.md").read_text(encoding="utf-8")))
        self.assertEqual(annonces, emis)

    def test_charte(self):
        fichiers = [SKILL / "SKILL.md", *sorted((SKILL / "references").glob("*.md")), SCRIPTS / "positions.py", Path(__file__),
                    PLUGIN / "integration" / "posture.md", PLUGIN / "integration" / "posture.patch", *sorted((BANC / "sondes").glob("POST2-*.json"))]
        for f in fichiers:
            if f.exists():
                self.assertNotIn(chr(0x2014), f.read_text(encoding="utf-8"), f.name)
        entete = (SKILL / "SKILL.md").read_text(encoding="utf-8").split("---")[1]
        self.assertIn("name: rapport-de-force", entete)


@unittest.skipUnless((BANC / "banc.py").exists(), "banc absent")
class TestSondes(unittest.TestCase):
    """Les sondes POST2 sont valides et leur consigne ne contient pas la réponse attendue."""

    def test_sondes(self):
        sys.path.insert(0, str(BANC))
        import banc
        sondes = sorted((BANC / "sondes").glob("POST2-*.json"))
        self.assertGreaterEqual(len(sondes), 5)
        for f in sondes:
            s = json.loads(f.read_text(encoding="utf-8"))
            self.assertEqual(s["id"], f.stem)
            self.assertEqual(s["capacite"], "posture")
            self.assertTrue(any(v.get("critique", True) for v in s["verifications"]), f.name)
            for v in s["verifications"]:
                self.assertIn(v["type"], ("contient", "absent", "contient_un", "contient_tous", "critere"))
                if v["type"] == "critere":  # jugé au sens par correcteur.py
                    self.assertTrue(v["critere"].strip(), f.name)
                    continue
                motifs = [v["motif"]] if "motif" in v else v["motifs"]
                for m in motifs:
                    self.assertNotIn("\x08", m)
                    re.compile(banc.norm(m))
                    if v["type"] in ("contient", "contient_un") and not v.get("fichier"):
                        self.assertFalse(banc.cherche(m, banc.norm(s["consigne"])), f"{f.name} : la consigne contient « {m} »")


class TestIntegration(unittest.TestCase):
    """Le correctif s'applique ; le hook et le contrôle avant dépôt corrigés appliquent la règle de révision."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        if "positions" in (SCRIPTS / "hook.py").read_text(encoding="utf-8"):
            cls.plugin = PLUGIN
            return
        cls.plugin = cls.tmp / "plugin"
        shutil.copytree(PLUGIN, cls.plugin, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "tests"))
        correctif = PLUGIN / "integration" / "posture.patch"
        if shutil.which("patch"):
            cmd = ["patch", "-p1", "--binary", "-s", "-i", str(correctif)]
        elif shutil.which("git"):
            cmd = ["git", "apply", "-p1", str(correctif)]
        else:
            raise unittest.SkipTest("ni patch ni git pour appliquer le correctif")
        r = subprocess.run(cmd, cwd=cls.plugin, capture_output=True, text=True)
        if r.returncode != 0:
            raise AssertionError(f"le correctif ne s'applique pas : {r.stdout}{r.stderr}")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def setUp(self):
        self.r = Path(tempfile.mkdtemp()) / "affaire"
        subprocess.run([PY, str(self.plugin / "scripts" / "affaire.py"), "init", str(self.r), "--intitule", "Essai", "--client", "X",
                        "--objectif", "Être payé"], check=True, capture_output=True)

    def tearDown(self):
        shutil.rmtree(self.r.parent, ignore_errors=True)

    def hook(self, ev):
        r = subprocess.run([PY, str(self.plugin / "scripts" / "hook.py")], input=json.dumps(ev), capture_output=True, text=True, encoding="utf-8")
        return json.loads(r.stdout) if r.stdout.strip() else {}

    def test_constitution_et_skills_corriges(self):
        constitution = (self.r / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("strategie/positions.json", constitution)
        self.assertIn("rapport-de-force", constitution)
        for rel in ("skills/strategie-contentieuse/SKILL.md", "skills/negociation-et-persuasion/SKILL.md", "agents/plume.md",
                    "agents/negociateur.md", "agents/architecte-strategique.md", "agents/contradicteur.md"):
            self.assertIn("rapport-de-force", (self.plugin / rel).read_text(encoding="utf-8"), rel)

    def test_rappel_user_prompt(self):
        L.ecrire_json(self.r / "strategie/positions.json", registre())
        out = self.hook({"hook_event_name": "UserPromptSubmit", "cwd": str(self.r),
                         "prompt": "Je ne suis pas d'accord, je veux qu'on dépose demain. Vous êtes trop prudent."})
        texte = out.get("hookSpecificOutput", {}).get("additionalContext", "")
        self.assertIn("élément nouveau", texte)
        self.assertIn("Position P1", texte)

    def test_hook_bloque_une_capitulation(self):
        doc = registre()
        doc["positions"][0]["revisions"][0]["element"] = {"type": "desaccord", "ref": "la cliente insiste", "connu_le": "2026-11-19"}
        L.ecrire_json(self.r / "strategie/positions.json", doc)
        out = self.hook({"hook_event_name": "PostToolUse", "cwd": str(self.r), "tool_name": "Write",
                         "tool_input": {"file_path": str(self.r / "strategie/positions.json")}})
        self.assertEqual(out.get("decision"), "block")
        self.assertIn("DESACCORD_N_EST_PAS_UN_ELEMENT", out.get("reason", ""))

    def test_gate_signale_le_registre(self):
        brouillon = self.r / "ecritures/brouillons/lettre_v1.md"
        brouillon.parent.mkdir(parents=True, exist_ok=True)
        brouillon.write_text("Lettre.\n", encoding="utf-8")
        L.ecrire_json(self.r / "ecritures/controle/lettre_v1.fiche.json", {"type_acte": "courrier_precontentieux"})
        r = subprocess.run([PY, str(self.plugin / "scripts" / "gate.py"), str(brouillon), "--json"], capture_output=True, text=True, encoding="utf-8")
        constats = {k["code"]: k["gravite"] for k in json.loads(r.stdout)["constats"]}
        self.assertEqual(constats.get("POSITIONS_ABSENTES"), "ALERTE")


if __name__ == "__main__":
    unittest.main()
