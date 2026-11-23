"""Pseudonymisation : validateurs, détection, propagation, et parcours complet d'un dossier (coffre hors du dossier, relecture
obligatoire, hooks, ré-identification). Données entièrement fictives.
Lancer : python -m pytest -q tests/test_pseudonymisation.py -p no:cacheprovider"""
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import pseudonymisation as P  # noqa: E402


class Validateurs(unittest.TestCase):
    def test_cles(self):
        self.assertTrue(P.iban_valide("FR76 3000 6000 0112 3456 7890 189"))
        self.assertFalse(P.iban_valide("FR76 3000 6000 0112 3456 7890 188"))
        self.assertTrue(P.luhn("4111111111111111"))
        self.assertFalse(P.luhn("4111111111111112"))
        self.assertTrue(P.siret_valide("732 829 320 00074"))
        corps = "2710369123456"
        self.assertTrue(P.nir_valide(corps + f"{97 - int(corps) % 97:02d}"))


class Detection(unittest.TestCase):
    def pseudo(self, texte, parties=()):
        t = P.Table(Path("."), memoire=True)
        for x in parties:
            t.jeton(x, "PERSONNE", source="avocat")
        return P.pseudonymiser(texte, t, avec_modele=False)[0], t

    def test_personnes_et_propagation(self):
        sortie, t = self.pseudo("Mme Marie-Claire DURAND, assistée de Me Paul Lefèvre. Plus loin, Mme Durand signe. Sa fille Oumou est là.")
        for reel in ("Marie-Claire", "DURAND", "Durand", "Lefèvre", "Oumou"):
            self.assertNotIn(reel, sortie)
        self.assertIn("Mme [PERSONNE_1]", sortie)

    def test_texte_juridique_intact(self):
        texte = ("Au cours de l'instruction, par voie de conséquence, le préfet du Rhône invoque l'article L. 521-1 du code de justice "
                 "administrative et CE, Sect., 14 mars 2001, n° 229773, devant le tribunal administratif de Lyon le 13 octobre 2026.")
        self.assertEqual(self.pseudo(texte)[0], texte)

    def test_nom_commun_homonyme(self):
        sortie, _ = self.pseudo("M. Blanc est présent. Le mur blanc est fissuré.")
        self.assertIn("mur blanc", sortie)
        self.assertNotIn("M. Blanc", sortie)

    def test_identifiants(self):
        sortie, _ = self.pseudo("Contact : marie.durand@exemple.fr, 06 12 34 56 78, IBAN FR76 3000 6000 0112 3456 7890 189, RG n° 24/01234, "
                                "titre de séjour n° 6901234567, véhicule AB-123-CD, compte @marie_d.")
        for reel in ("marie.durand@exemple.fr", "06 12 34 56 78", "FR76", "24/01234", "6901234567", "AB-123-CD", "@marie_d"):
            self.assertNotIn(reel, sortie)

    def test_reidentification(self):
        sortie, t = self.pseudo("Mme Marie Durand demeure 12 rue des Lilas, 69003 Lyon.")
        self.assertEqual(P.reidentifier_texte(sortie, t), "Mme Marie Durand demeure 12 rue des Lilas, 69003 Lyon.")


def hook(ev: dict, env: dict) -> dict:
    r = subprocess.run([sys.executable, str(SCRIPTS / "pseudonymisation.py"), "hook"], input=json.dumps(ev), capture_output=True,
                       text=True, encoding="utf-8", env=env)
    return json.loads(r.stdout) if r.stdout.strip() else {}


@unittest.skipUnless(__import__("importlib").util.find_spec("cryptography"), "cryptography absent")
class Parcours(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.r = self.tmp / "affaire"
        (self.r / "etat").mkdir(parents=True)
        (self.r / "journal").mkdir()
        (self.r / "etat" / "affaire.json").write_text(json.dumps({"id": "t", "intitule": "Recours de Marie Durand", "client": "Marie Durand",
                                                                 "adversaires": ["Société Alpha Conseil"]}), encoding="utf-8")
        (self.r / "journal" / "journal.md").write_text("Ouverture du dossier de Marie Durand.\n", encoding="utf-8")
        self.originaux = self.tmp / "originaux_du_cabinet"
        self.originaux.mkdir()
        (self.originaux / "attestation_durand.txt").write_text(
            "Je soussigné Paul Martin atteste que Mme Marie Durand, née le 3 mars 1971, s'occupe de sa fille Léa. Tél. 06 12 34 56 78.",
            encoding="utf-8")
        self.env = {**os.environ, P.COFFRE_ENV: str(self.tmp / "coffre"), "PYTHONIOENCODING": "utf-8"}

    def cmd(self, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / "pseudonymisation.py"), *args], cwd=self.r, capture_output=True, text=True,
                              encoding="utf-8", env=self.env)

    def test_parcours_complet(self):
        self.assertEqual(self.cmd("init").returncode, 0)
        aff = json.loads((self.r / "etat" / "affaire.json").read_text(encoding="utf-8"))
        self.assertTrue(aff["client"].startswith("[PERSONNE_"))
        self.assertNotIn("Durand", (self.r / "journal" / "journal.md").read_text(encoding="utf-8"))
        coffre = Path(json.loads((self.r / ".pseudonymisation" / "actif.json").read_text(encoding="utf-8"))["coffre"])
        self.assertFalse(coffre.resolve().is_relative_to(self.r.resolve()))
        self.assertEqual(self.cmd("importer", str(self.originaux / "attestation_durand.txt")).returncode, 0)
        copies = list((self.r / "pieces" / "pseudonymisees").glob("*.txt"))
        self.assertEqual(len(copies), 1)
        self.assertNotIn("Durand", copies[0].name)
        texte = copies[0].read_text(encoding="utf-8")
        for reel in ("Paul Martin", "Marie Durand", "Léa", "06 12 34 56 78", "3 mars 1971"):
            self.assertNotIn(reel, texte)
        # Copie non validée : refusée ; validée : permise ; coffre et originaux : refusés.
        ev = {"hook_event_name": "PreToolUse", "cwd": str(self.r), "tool_name": "Read", "tool_input": {"file_path": str(copies[0])}}
        self.assertEqual(hook(ev, self.env)["hookSpecificOutput"]["permissionDecision"], "deny")
        self.cmd("valider")
        self.assertEqual(hook(ev, self.env), {})
        ev_coffre = {**ev, "tool_input": {"file_path": str(coffre / "rapport.md")}}
        self.assertEqual(hook(ev_coffre, self.env)["hookSpecificOutput"]["permissionDecision"], "deny")
        ev_bash = {**ev, "tool_name": "Bash", "tool_input": {"command": f"type \"{coffre}\\table.chiffree\""}}
        self.assertEqual(hook(ev_bash, self.env)["hookSpecificOutput"]["permissionDecision"], "deny")
        # Un vrai nom tapé par l'avocat est bloqué ; un jeton passe.
        self.assertEqual(hook({"hook_event_name": "UserPromptSubmit", "cwd": str(self.r), "prompt": "Que pense Marie Durand ?"}, self.env)["decision"], "block")
        self.assertEqual(hook({"hook_event_name": "UserPromptSubmit", "cwd": str(self.r), "prompt": "Que pense [PERSONNE_1] ?"}, self.env), {})
        # Un acte qui contiendrait une donnée réelle est signalé à l'écriture.
        acte = self.r / "ecritures" / "brouillons" / "requete.md"
        acte.parent.mkdir(parents=True)
        acte.write_text("Mme Durand demande la suspension.", encoding="utf-8")
        self.assertEqual(hook({"hook_event_name": "PostToolUse", "cwd": str(self.r), "tool_name": "Write",
                               "tool_input": {"file_path": str(acte)}}, self.env)["decision"], "block")
        acte.write_text("Mme [PERSONNE_1] demande la suspension.", encoding="utf-8")
        self.assertEqual(self.cmd("verifier").returncode, 0)
        self.assertEqual(self.cmd("reidentifier", str(acte)).returncode, 0)
        self.assertIn("Marie Durand", (coffre / "sorties" / "requete.md").read_text(encoding="utf-8"))

    def test_original_dans_le_dossier_refuse(self):
        self.cmd("init")
        dedans = self.r / "piece.txt"
        dedans.write_text("Mme Marie Durand", encoding="utf-8")
        self.assertNotEqual(self.cmd("importer", str(dedans)).returncode, 0)


if __name__ == "__main__":
    unittest.main()
