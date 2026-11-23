"""Tests des verrous du plugin contentieux, sur une affaire synthétique sans donnée réelle.

Lancer : python -m unittest discover -s plugins/contentieux/tests -v
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import gate  # noqa: E402
import lib_affaire as L  # noqa: E402

PY = sys.executable

REFERE_MAUVAIS = """TRIBUNAL ADMINISTRATIF DE NULLEPART

Juge des référés

Requête en référé-suspension (article L. 521-1 du code de justice administrative)

1. Le requérant soutient que la décision du 1er mars 2026 est illégale, si telle est sa portée.
2. L'avis médical du 10 mars 2026 constate une situation nouvelle (pièce 3).
3. CE, 1er janvier 2020, n° 999999, juge le contraire.

Par ces motifs
M. X demande au juge des référés
1. De suspendre la décision du 1er mars 2026 ou, subsidiairement, le courriel du 2 mars 2026.
2. Si la décision est suspendue, d'enjoindre un réexamen en deux jours, et à titre subsidiaire de l'inscrire.
"""

REFERE_BON = """TRIBUNAL ADMINISTRATIF DE NULLEPART

Juge des référés

Requête en référé-suspension (article L. 521-1 du code de justice administrative)

Décision attaquée. Décision du directeur du 20 mars 2026 rejetant la demande du 12 mars 2026 (pièce 1).

1. La question est de savoir si le directeur pouvait rejeter sans l'examiner la demande fondée sur l'avis médical du 10 mars 2026.
2. L'avis médical du 10 mars 2026 préconise un aménagement (pièce 2). La demande du 12 mars le joint (pièce 1).
3. Le directeur n'a pas examiné l'avis. CE, 1er janvier 2020, n° 123456, point 3, impose cet examen.
4. L'urgence tient aux examens du 1er mai 2026, que l'aménagement doit précéder.

Par ces motifs
M. X demande au juge des référés
1. De suspendre la décision du 20 mars 2026.
2. D'enjoindre au directeur de statuer de nouveau dans un délai de huit jours.
"""


def ecrire(p: Path, contenu):
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(contenu, (dict, list)):
        p.write_text(json.dumps(contenu, ensure_ascii=False), encoding="utf-8")
    else:
        p.write_text(contenu, encoding="utf-8")


FAMILLES = ("amiable", "administrative", "autorite_independante", "urgence", "fond", "indemnitaire",
            "penal", "disciplinaire", "europeen", "constitutionnel", "hors_pretoire")


def theorie_conforme(date: str) -> dict:
    """Théorie de l'affaire minimale qui satisfait les contrôles mécaniques."""
    return {"date": date, "recit_du_client": "récit allégué",
            "hypotheses": [
                {"id": "H1", "porteur": "nous", "enonce": "e", "pieces_compatibles": ["2"], "pieces_incompatibles": [], "statut": "retenue", "raison": "r"},
                {"id": "H2", "porteur": "adversaire", "enonce": "e", "pieces_compatibles": [], "pieces_incompatibles": [{"piece": "2", "extrait": "x"}],
                 "statut": "ecartee", "raison": "r"},
                {"id": "H3", "porteur": "lecture_par_defaut", "enonce": "e", "pieces_compatibles": [], "pieces_incompatibles": [], "statut": "ecartee", "raison": "r"}],
            "pieces_diagnostiques": [{"piece": "2", "extrait": "x", "departage": ["H1", "H2"]}],
            "theorie_retenue": {"hypothese": "H1", "recit": "r", "qualification": "q", "qualifications_ecartees": [], "question": "q", "theme": "t", "surete": "s"},
            "faits_defavorables": [{"fait": "f", "pieces": ["1"], "traitement": "depassement", "explication": "un fait postérieur le prive d'effet"}],
            "reponses_theorie_adverse": [{"argument": "A1", "traitement": "retournement", "explication": "la pièce 2 contredit l'argument adverse",
                                          "appui": ["2"]}],
            "maillons_manquants": [], "point_de_rupture": {"piece_ou_fait": "p", "detenu_par": "d", "parade": "p"},
            "epreuves": {e: "vérifiée" for e in ("couverture", "coherence", "completude", "unicite", "stabilite", "verite", "contradiction")}}


def sequence_conforme(date: str, ecriture: str, type_acte: str, theorie_date: str) -> dict:
    """Séquence minimale qui place l'écriture dans une voie retenue et dans l'ordre des coups."""
    return {"date": date, "premier_acte_adverse": {"date": "2026-03-20", "acte": "décision", "piece": "1"}, "autorites": [],
            "familles_examinees": [{"famille": "urgence", "voies": ["V1"]}] + [{"famille": f, "sans_objet": "raison"} for f in FAMILLES if f != "urgence"],
            "actes": [{"id": "A1", "date": "2026-03-20", "regime_contentieux": "droit commun (CJA, R. 421-1)"}],
            "voies_adversaires": [{"voie": "nouvelle décision sur d'autres motifs", "parade": "p", "preuves_a_constituer": ["p"]}],
            "voies": [{"id": "V1", "famille": "urgence", "voie": "v", "type_acte": type_acte, "ecritures": [ecriture], "statut": "retenue",
                       "epreuve_juge": "ecritures/controle/trame.lecture_froid.json",
                       "delai": {"evenement": "E1", "regle": "r"}, "raison": "r"}],
            "cible": {"acte": "décision", "raison": "r"},
            "ordre_des_coups": [{"rang": 1, "coup": "c", "voie": "V1", "reponses_adverses": [{"reponse": "refus", "coup_suivant": "fond"},
                                                                               {"reponse": "rejet pour absence de doute sérieux", "coup_suivant": "confirmer le maintien du fond dans le mois (CJA, R. 612-5-2)"}]}],
            "coherence": {"theorie_date": theorie_date}}


def preuve_documentaire(r: Path, cote: int, texte: str, citation: str, fid: str, fait: str) -> None:
    """Pièce texte réelle, inventoriée et analysée, et l'entrée de la matrice qui cite son extrait (skill analyse-documentaire)."""
    import pieces as PIECES
    rel = f"pieces/originaux/{cote:03d}_x.txt"
    (r / rel).parent.mkdir(parents=True, exist_ok=True)
    (r / rel).write_text(texte, encoding="utf-8")
    b = L.lire_json(r / "pieces/bordereau.json")
    for p in b["pieces"]:
        if p["cote"] == str(cote):
            p.update({"fichier": rel, "sha256": L.sha256_fichier(r / rel)})
    L.ecrire_json(r / "pieces/bordereau.json", b)
    PIECES.cmd_inventaire(r, [str(cote)])
    fiche = PIECES.squelette(r, str(cote))
    fiche["lecture"].update({"pages_lues": [1], "limites": "aucune"})
    fiche["nature"] = {"type": "certificat", "intitule": "Avis médical", "forme": "copie"}
    fiche["auteur"]["fondement"] = "en-tête"
    fiche["objet"] = fait
    fiche["extraits"] = [{"id": "E1", "page": 1, "citation": citation, "lu_sur": "texte"}]
    fiche["prouve"] = [{"fait": fait, "extraits": ["E1"], "portee": "préconisation datée"}]
    fiche["ne_prouve_pas"] = [{"point": "la suite donnée à l'avis", "raison": "l'avis ne la relate pas"}]
    for i in fiche["indices_examines"]:
        i["conclusion"] = "ecarte"
    ecrire(r / f"pieces/analyses/{cote}.json", fiche)
    # L'analyse précède la théorie et la ligne datées à la minute dans le test : elle ne doit pas les rendre périmées.
    avant = L.maintenant().timestamp() - 120
    os.utime(r / f"pieces/analyses/{cote}.json", (avant, avant))
    m = L.lire_json(r / "preuves/matrice.json") or {}
    m["version"] = 2
    m.setdefault("faits_a_prouver", []).append({"id": fid, "fait": fait, "charge": "nous", "pieces": [str(cote)], "force": "forte",
                                                "force_probante": "prouve", "extraits": [{"cote": str(cote), "extrait": "E1", "page": 1, "citation": citation}]})
    L.ecrire_json(r / "preuves/matrice.json", m)


THEORIE_ADVERSE = {"date": "2026-11-18T09:00", "arguments": [{"id": "A1", "sur": "urgence", "argument": "pas d'urgence", "force": "decisive",
                                                               "pieces": [], "autorites": []}], "meilleur_coup": "A1"}
LECTURE_TRAME = {"sha256": "trame", "issue": "audience", "issue_binaire": "succes", "motifs": []}


def hook(ev: dict) -> dict:
    r = subprocess.run([PY, str(SCRIPTS / "hook.py")], input=json.dumps(ev), capture_output=True, text=True, encoding="utf-8")
    return json.loads(r.stdout) if r.stdout.strip() else {}


class TestEnTetes(unittest.TestCase):
    """Banc du 20 novembre : une description non citée contenant « : » rend l'en-tête invalide. Claude Code liste alors la
    commande mais retire le skill de ceux que le modèle peut charger : mecanique-des-exercices et rapporteur-simule ne l'ont jamais été."""

    def test_en_tetes_yaml_valides(self):
        import re
        import yaml
        racine = SCRIPTS.parent
        fichiers = sorted(racine.glob("skills/*/SKILL.md")) + sorted(racine.glob("agents/*.md"))
        self.assertTrue(fichiers)
        for f in fichiers:
            m = re.match(r"---\n(.*?)\n---", f.read_text(encoding="utf-8"), re.S)
            self.assertIsNotNone(m, f.name)
            y = yaml.safe_load(m.group(1))
            self.assertIsInstance(y, dict, f)
            self.assertTrue(y.get("name") and y.get("description"), f)
            self.assertLessEqual(len(y["description"]), 1024, f)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.r = self.tmp / "affaire"
        subprocess.run([PY, str(SCRIPTS / "affaire.py"), "init", str(self.r), "--intitule", "Essai", "--client", "X",
                        "--objectif", "Obtenir Z"], check=True, capture_output=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


class TestProtections(Base):
    def test_constitution_pointe_vers_ce_plugin(self):
        texte = (self.r / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn(str(SCRIPTS.resolve()), texte)
        self.assertNotIn("{{SCRIPTS}}", texte)

    def test_ecritures_protegees(self):
        for rel in ["pieces/originaux/001_a.pdf", "journal/journal.md", "CLAUDE.md", "AGENTS.md", "ecritures/FINAL/x.md", "ecritures/controle/x.gate.json"]:
            out = hook({"hook_event_name": "PreToolUse", "cwd": str(self.r), "tool_name": "Write",
                        "tool_input": {"file_path": str(self.r / rel), "content": "x"}})
            self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny", rel)
        out = hook({"hook_event_name": "PreToolUse", "cwd": str(self.r), "tool_name": "Write",
                    "tool_input": {"file_path": str(self.r / "ecritures/brouillons/a.md"), "content": "x"}})
        self.assertEqual(out, {})

    def test_rapports_independants_reserves_aux_sous_agents(self):
        cible = str(self.r / "ecritures/controle/ref.lecture_froid.json")
        base = {"hook_event_name": "PreToolUse", "cwd": str(self.r), "tool_name": "Write", "tool_input": {"file_path": cible, "content": "{}"}}
        self.assertEqual(hook(base)["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertEqual(hook({**base, "agent_type": "contentieux:juge-simule"}), {})
        rap = {**base, "tool_input": {"file_path": str(self.r / "ecritures/controle/ref.rapport_rapporteur.json"), "content": "{}"}}
        self.assertEqual(hook(rap)["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertEqual(hook({**rap, "agent_type": "contentieux:rapporteur-simule"}), {})
        self.assertEqual(hook({**rap, "agent_type": "contentieux:juge-simule"})["hookSpecificOutput"]["permissionDecision"], "deny")
        contra = {**base, "tool_input": {"file_path": str(self.r / "ecritures/controle/ref.contradiction.json"), "content": "{}"}}
        self.assertEqual(hook(contra)["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertEqual(hook({**contra, "tool_name": "Edit"}), {})

    def test_commandes_destructives(self):
        out = hook({"hook_event_name": "PreToolUse", "cwd": str(self.r), "tool_name": "Bash", "tool_input": {"command": "rm pieces/originaux/001_a.pdf"}})
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")
        out = hook({"hook_event_name": "PreToolUse", "cwd": str(self.r), "tool_name": "Bash", "tool_input": {"command": "cat pieces/originaux/001_a.pdf"}})
        self.assertEqual(out, {})

    def test_requete_publique_avec_identifiant_prive(self):
        a = L.lire_json(self.r / "etat/affaire.json")
        a["consignes"]["identifiants_prives"] = ["Dupontel", "dupontel@example.org"]
        L.ecrire_json(self.r / "etat/affaire.json", a)
        out = hook({"hook_event_name": "PreToolUse", "cwd": str(self.r), "tool_name": "WebSearch", "tool_input": {"query": "référé Dupontel université"}})
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")
        out = hook({"hook_event_name": "PreToolUse", "cwd": str(self.r), "tool_name": "mcp__librejustice__search_decisions", "tool_input": {"query": "redoublement handicap"}})
        self.assertEqual(out, {})

    def test_etat_invalide(self):
        ecrire(self.r / "etat/sources.json", {"sources": "pas une liste"})
        out = hook({"hook_event_name": "PostToolUse", "cwd": str(self.r), "tool_name": "Write", "tool_input": {"file_path": str(self.r / "etat/sources.json")}})
        self.assertEqual(out["decision"], "block")


class TestSessions(Base):
    def test_briefing_canaux_et_echeance(self):
        subprocess.run([PY, str(SCRIPTS / "affaire.py"), "echeance", "ajouter", "--objet", "Dépôt", "--date", "2099-01-01",
                        "--regle", "R", "--depart", "D", "--source", "S"], cwd=self.r, check=True, capture_output=True)
        out = hook({"hook_event_name": "SessionStart", "cwd": str(self.r), "source": "compact", "session_id": "s"})
        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertIn("REPRISE APRÈS COMPACTION", ctx)
        self.assertIn("Courrier postal", ctx)
        self.assertIn("Dépôt", ctx)

    def test_passation_exigee(self):
        hook({"hook_event_name": "SessionStart", "cwd": str(self.r), "source": "startup", "session_id": "s"})
        # Les captures du registre des lectures, écrites par le hook, ne changent pas l'état de l'affaire.
        ecrire(self.r / "recherche/lectures/20261120T041500_00001_get_norm_x.json", "{}")
        self.assertEqual(hook({"hook_event_name": "Stop", "cwd": str(self.r), "stop_hook_active": False}), {})
        ecrire(self.r / "recherche/notes/n.md", "note")
        out = hook({"hook_event_name": "Stop", "cwd": str(self.r), "stop_hook_active": False})
        self.assertEqual(out.get("decision"), "block")
        self.assertIn("en français", out.get("reason", ""))
        ecrire(self.r / "etat/passation.md", "# Passation\nfait")
        self.assertEqual(hook({"hook_event_name": "Stop", "cwd": str(self.r), "stop_hook_active": False}), {})

    def test_piece_citee_sans_lecture(self):
        hook({"hook_event_name": "SessionStart", "cwd": str(self.r), "source": "startup", "session_id": "s"})
        ecrire(self.r / "etat/passation.md", "# Passation\nfait")
        tr = self.tmp / "t.jsonl"
        lignes = [{"type": "user", "message": {"content": "Que dit la lettre ?"}},
                  {"type": "assistant", "message": {"content": [{"type": "text", "text": "La pièce 42 refuse tout examen."}]}}]
        tr.write_text("\n".join(json.dumps(l, ensure_ascii=False) for l in lignes), encoding="utf-8")
        out = hook({"hook_event_name": "Stop", "cwd": str(self.r), "stop_hook_active": False, "transcript_path": str(tr)})
        self.assertEqual(out.get("decision"), "block")
        lignes.insert(1, {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read",
                          "input": {"file_path": str(self.r / "pieces/texte/042_demande.txt")}}]}})
        tr.write_text("\n".join(json.dumps(l, ensure_ascii=False) for l in lignes), encoding="utf-8")
        self.assertEqual(hook({"hook_event_name": "Stop", "cwd": str(self.r), "stop_hook_active": False, "transcript_path": str(tr)}), {})

    def test_acte_hors_dossier_et_competence(self):
        """Banc du 20 novembre : requête rédigée hors du dossier ou dans la réponse, juridiction reprise sans lire R. 311-1 et suivants."""
        acte = "# Requête\n\nDevant le tribunal administratif de Rennes.\n\n## IV. Conclusions\n\nLes requérants demandent au tribunal d'annuler le permis."
        hors = hook({"hook_event_name": "PreToolUse", "cwd": str(self.r), "tool_name": "Write",
                     "tool_input": {"file_path": str(self.tmp / "scratchpad/requete.md"), "content": acte}})
        self.assertEqual(hors["hookSpecificOutput"]["permissionDecision"], "deny")
        note = hook({"hook_event_name": "PreToolUse", "cwd": str(self.r), "tool_name": "Write",
                     "tool_input": {"file_path": str(self.tmp / "scratchpad/note.md"), "content": "Relevé des textes à lire."}})
        self.assertEqual(note, {})
        ecrire(self.r / "ecritures/brouillons/requete.md", acte)
        post = hook({"hook_event_name": "PostToolUse", "cwd": str(self.r), "tool_name": "Write",
                     "tool_input": {"file_path": str(self.r / "ecritures/brouillons/requete.md")}})
        self.assertIn("COMPETENCE_PREMIER_RESSORT_NON_LUE", post["hookSpecificOutput"]["additionalContext"])
        ecrire(self.r / "etat/passation.md", "# Passation\nfait")
        tr = self.tmp / "t.jsonl"
        tr.write_text("\n".join(json.dumps(l, ensure_ascii=False) for l in [
            {"type": "user", "message": {"content": "Rédige la requête."}},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": acte}]}}]), encoding="utf-8")
        stop = {"hook_event_name": "Stop", "cwd": str(self.r), "stop_hook_active": False, "transcript_path": str(tr)}
        self.assertIn("R. 311-1", hook(stop).get("reason", ""))
        import lectures as LECTURES
        LECTURES.capturer(self.r, {"tool_name": "mcp__librejustice__get_norm", "tool_input": {"code": "code-de-justice-administrative", "article": "r311-5"},
                                   "tool_response": json.dumps({"code": "code-de-justice-administrative", "number": "R311-5", "text": "Texte synthétique.",
                                                                "valid_from": "2026-07-01", "versions": [{"valid_from": "2026-07-01", "status": "VIGUEUR"}]})})
        self.assertEqual(hook(stop), {})

    def test_depot_exige_accord_recent(self):
        tr = self.tmp / "t.jsonl"
        cmd = 'python affaire.py depot ecritures/FINAL/a.md --accord "Je valide, déposez" --canal Télérecours'

        def avec(messages):
            tr.write_text("\n".join(json.dumps({"type": "user", "message": {"content": m}}, ensure_ascii=False) for m in messages), encoding="utf-8")
            return hook({"hook_event_name": "PreToolUse", "cwd": str(self.r), "tool_name": "Bash", "tool_input": {"command": cmd}, "transcript_path": str(tr)})

        self.assertEqual(avec(["Je valide, déposez"]), {})
        self.assertEqual(avec(["Je valide, déposez", "Ne déposez pas encore"])["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertEqual(avec(["autre chose"])["hookSpecificOutput"]["permissionDecision"], "deny")
        # Un mot isolé ne vaut pas accord, même présent dans un message.
        cmd_oui = 'python affaire.py depot ecritures/FINAL/a.md --accord "oui" --canal Télérecours'
        tr.write_text(json.dumps({"type": "user", "message": {"content": "oui, lance l'épreuve"}}, ensure_ascii=False), encoding="utf-8")
        r = hook({"hook_event_name": "PreToolUse", "cwd": str(self.r), "tool_name": "Bash", "tool_input": {"command": cmd_oui}, "transcript_path": str(tr)})
        self.assertEqual(r["hookSpecificOutput"]["permissionDecision"], "deny")
        # Citer la commande dans une note n'est pas déposer.
        cite = 'python affaire.py journal "préparer ensuite affaire.py depot avec accord du client"'
        self.assertEqual(hook({"hook_event_name": "PreToolUse", "cwd": str(self.r), "tool_name": "Bash", "tool_input": {"command": cite},
                               "transcript_path": str(tr)}), {})
        # Un accord antérieur à la version finale ne vaut pas pour elle.
        ecrire(self.r / "ecritures/FINAL/a.md", "Acte final.")
        tr.write_text(json.dumps({"type": "user", "timestamp": "2020-01-01T00:00:00Z", "message": {"content": "Je valide, déposez"}}, ensure_ascii=False), encoding="utf-8")
        r = hook({"hook_event_name": "PreToolUse", "cwd": str(self.r), "tool_name": "Bash", "tool_input": {"command": cmd}, "transcript_path": str(tr)})
        self.assertEqual(r["hookSpecificOutput"]["permissionDecision"], "deny")


class TestGate(Base):
    def preparer(self, texte, fiche, sources, cotes):
        ecrire(self.r / "ecritures/brouillons/ref.md", texte)
        ecrire(self.r / "ecritures/controle/ref.fiche.json", fiche)
        ecrire(self.r / "etat/sources.json", {"sources": sources})
        ecrire(self.r / "pieces/bordereau.json", {"pieces": [{"cote": str(c), "fichier": f"pieces/originaux/{c:03d}_x", "sha256": "x", "description": "x"} for c in cotes]})
        return self.r / "ecritures/brouillons/ref.md"

    def codes(self, v):
        return {c["code"] for c in v["constats"] if c["gravite"] == "BLOQUANT"}

    def test_refere_mal_construit(self):
        fiche = {"type_acte": "refere_suspension", "question": "Le directeur pouvait-il rejeter sans examen ?", "fait_decisif": "avis médical du 10 mars",
                 "actes_attaques": [
                     {"id": "A", "designation": "décision du 1er mars", "date": "2026-03-01", "qualification": "decision_expresse", "justification": "j", "sources": ["T"]},
                     {"id": "B", "designation": "courriel du 2 mars", "date": "2026-03-02", "qualification": "refus_de_rendez_vous", "justification": "j", "sources": ["T"]}],
                 "conditions": [{"condition": "urgence", "etat": "fragile", "faits": [{"fait": "f", "date": "2026-04-01", "pieces": [3]}], "sources": ["T"]}],
                 "moyens": [{"intitule": "Défaut d'examen de l'avis", "actes_vises": ["A"], "sources": ["T"],
                             "faits": [{"fait": "avis médical", "date": "2026-03-10", "pieces": [3]}]}],
                 "conclusions": [{"texte": "1", "pouvoir_du_juge": ""}],
                 "delai": {"echeance": "2099-01-01T12:00", "regle": "r", "point_de_depart": "p"}}
        f = self.preparer(REFERE_MAUVAIS, fiche, [{"id": "T", "type": "texte", "reference": "CJA L. 521-1", "lu_en_entier": True}], [3])
        v = gate.controler(f)
        self.assertEqual(v["verdict"], "FAIL")
        attendus = {"ACTE_NON_DECISOIRE", "PLURALITE_ACTES", "MOYEN_INOPERANT_DATE", "CONDITION_NON_TRAITEE", "CONDITION_FRAGILE",
                    "REQUETE_FOND_DISTINCTE", "CONCLUSION_SANS_POUVOIR", "ATTENUATION", "SUBSIDIAIRES", "BRANCHE_CONDITIONNELLE",
                    "CITATION_HORS_REGISTRE", "LECTURE_FROID_ABSENTE", "CONTRADICTION_ABSENTE"}
        self.assertTrue(attendus <= self.codes(v), attendus - self.codes(v))

    def test_delai_recalcule_depuis_la_chronologie(self):
        # Décision notifiée le 2 mars 2026 : deux mois mènent au 4 mai (2 mai samedi, 3 mai dimanche) ; la fiche déclare le 30 mai.
        ecrire(self.r / "chronologie/chronologie.json", {"evenements": [
            {"id": "E1", "date": "2026-03-02", "type": "decision_admin", "fait": "décision notifiée", "pieces": [1]}]})
        fiche = {"type_acte": "requete_fond_admin", "actes_attaques": [], "conditions": [],
                 "delai": {"echeance": "2026-05-30T12:00", "regle": "R. 421-1", "point_de_depart": "2 mars", "evenement": "E1"}}
        f = self.preparer("Requête.\n", fiche, [], [1])
        os.environ["CONTENTIEUX_MAINTENANT"] = "2026-05-20T12:00"
        try:
            v = gate.controler(f)
        finally:
            del os.environ["CONTENTIEUX_MAINTENANT"]
        k = {c["code"]: c for c in v["constats"]}
        self.assertIn("DELAI_MAL_CALCULE", k)
        self.assertIn("2026-05-04", k["DELAI_MAL_CALCULE"]["message"])
        depasse = [c for c in v["constats"] if c["code"] == "DELAI_DEPASSE"]
        self.assertTrue(depasse and depasse[0]["categorie"] == "delai_tardivete")
        self.assertTrue(all(c.get("categorie") for c in v["constats"] if c["code"] == "CONDITION_NON_TRAITEE"))

    def test_refere_conforme_puis_finalisation(self):
        fiche = {"type_acte": "refere_suspension", "au_nom_du_client": False,
                 "question": "Le directeur pouvait-il rejeter sans l'examiner la demande fondée sur l'avis médical du 10 mars ?",
                 "fait_decisif": "avis médical du 10 mars 2026 préconise un aménagement",
                 "faits_decisifs": ["F1"],
                 "urgence_premiere_page": "urgence examens du 1er mai 2026 que l'aménagement doit précéder",
                 "actes_attaques": [{"id": "A", "designation": "décision du 20 mars 2026", "date": "2026-03-20", "qualification": "decision_expresse",
                                     "justification": "décision de l'autorité compétente sur la demande du 12 mars", "sources": ["T"]}],
                 "conditions": [{"condition": "urgence", "etat": "etablie", "faits": [{"fait": "examens", "date": "2026-05-01", "pieces": [2]}], "sources": ["T"],
                                 "interet_public_adverse": "égalité entre candidats aux examens",
                                 "bilan": "l'aménagement préconisé ne retire rien aux autres candidats et ne peut plus être accordé après le 1er mai"},
                                {"condition": "doute_serieux", "etat": "etablie", "faits": [{"fait": "avis", "date": "2026-03-10", "pieces": [2]}], "sources": ["D"]},
                                {"condition": "requete_au_fond_distincte_et_copie", "etat": "etablie", "faits": [{"fait": "requête au fond enregistrée", "date": "2026-03-25", "pieces": [3]}], "sources": ["T"]},
                                {"condition": "decision_administrative_susceptible_de_recours", "etat": "etablie", "faits": [{"fait": "décision expresse", "date": "2026-03-20", "pieces": [1]}], "sources": ["T"]},
                                {"condition": "requete_au_fond_recevable_et_dans_le_delai", "etat": "etablie", "faits": [{"fait": "notification", "date": "2026-03-21", "pieces": [1]}], "sources": ["T"]}],
                 "moyens": [{"intitule": "Défaut d'examen", "actes_vises": ["A"], "sources": ["D"], "faits": [{"fait": "avis", "date": "2026-03-10", "pieces": [2]}]}],
                 "conclusions": [{"texte": "1", "pouvoir_du_juge": "CJA L. 521-1"}, {"texte": "2", "pouvoir_du_juge": "CJA L. 511-1"}],
                 "requete_fond_distincte": {"reference": "requête au fond", "piece": "3"},
                 "delai": {"echeance": "2099-01-01T12:00", "regle": "r", "point_de_depart": "p"}}
        sources = [{"id": "T", "type": "texte", "reference": "CJA L. 521-1", "lu_en_entier": True},
                   {"id": "D", "type": "decision", "reference": "CE n° 123456", "numero": "123456", "lu_en_entier": True}]
        f = self.preparer(REFERE_BON, fiche, sources, [1, 2, 3])
        v = gate.controler(f)
        self.assertTrue({"CANAL_NON_CONTROLE", "AUDIT_TERRAIN_PERIME", "LIGNE_INCOMPLETE", "RECIT_ABSENT", "LECTURE_PROFANE_ABSENTE",
                         "FAIT_DECISIF_HORS_MATRICE"} <= self.codes(v))
        preuve_documentaire(self.r, 2, "Avis médical du 10 mars 2026.\nUn aménagement des épreuves est préconisé.\n",
                            "Un aménagement des épreuves est préconisé.", "F1", "L'avis médical du 10 mars 2026 préconise un aménagement.")
        maintenant = L.maintenant().isoformat(timespec="minutes")
        from test_exercices import bloc_refere_suspension
        fiche["exercice"] = bloc_refere_suspension(maintenant)
        ecrire(self.r / "ecritures/controle/ref.fiche.json", fiche)
        canaux = L.lire_json(self.r / "etat/canaux.json")
        for c in canaux["canaux"]:
            c["dernier_controle"] = maintenant
        ecrire(self.r / "etat/canaux.json", canaux)
        ecrire(self.r / "terrain/audit.json", {"date": maintenant, "evidences_verifiees": ["boîte aux lettres relevée"], "lacunes": [], "actions_decidees": []})
        ecrire(self.r / "strategie/ligne.json", {"date": maintenant, "objectif": "o", "decideur": "d", "lecture_adversaire": "l", "levier": "l",
                                                  "meilleur_coup_adverse": "m", "parade": "p", "temps_reel": "t", "chemin_de_victoire": ["e"]})
        ecrire(self.r / "strategie/revue_charpente.json", {"date": maintenant, "theorie_date": maintenant, "sequence_date": maintenant,
                                                            "actes_couverts": ["ref"], "points": [
            {"id": "P1", "gravite": "dirimante", "constat": "c", "statut": "applique"}]})
        ecrire(self.r / "strategie/theorie.json", theorie_conforme(maintenant))
        ecrire(self.r / "strategie/theorie_adverse.json", THEORIE_ADVERSE)
        ecrire(self.r / "ecritures/controle/trame.lecture_froid.json", LECTURE_TRAME)
        ecrire(self.r / "strategie/sequence.json", sequence_conforme(maintenant, "ref", "refere_suspension", maintenant))
        ecrire(self.r / "ecritures/controle/ref.recit.json", {"theorie_du_cas": "t", "fil": ["f"], "neutralisation_adverse": "n",
                                                             "pourquoi_accorder_est_sur": "p", "theorie_date": maintenant})
        import decideurs as DEC
        from test_decideurs import profil_complet
        profil = profil_complet()
        profil.update({"date": maintenant, "actes_couverts": ["ref"]})
        ecrire(self.r / "strategie/decideurs.json", profil)
        from test_negociation import plan_complet
        plan = plan_complet()
        plan.update({"date": maintenant, "actes_couverts": ["ref"]})
        ecrire(self.r / "strategie/negociation.json", plan)
        # Lectures capturées des sources citées : l'article L. 521-1 du CJA et la décision n° 123456 (réponses synthétiques).
        import lectures as LECTURES
        for outil, entree, reponse in (
                ("mcp__librejustice__get_norm", {"code": "code-de-justice-administrative", "article": "l521-1"},
                 {"code": "code-de-justice-administrative", "number": "L521-1", "text": "Texte synthétique de l'article.", "valid_from": "2001-01-01",
                  "versions": [{"status": "VIGUEUR", "valid_from": "2001-01-01"}]}),
                ("mcp__librejustice__get_norm", {"code": "code-de-justice-administrative", "article": "r311-1"},
                 {"code": "code-de-justice-administrative", "number": "R311-1", "text": "Texte synthétique de la compétence en premier ressort.",
                  "valid_from": "2001-01-01", "versions": [{"valid_from": "2001-01-01", "status": "VIGUEUR"}]}),
                ("mcp__librejustice__get_decision", {"url": "https://librejustice.fr/decision/synthetique"},
                 {"docket_numbers": ["123456"], "title": "Conseil d'État, 1er janvier 2020, 123456", "text": "Texte synthétique de la décision.",
                  "standing": "FINAL"})):
            LECTURES.capturer(self.r, {"tool_name": outil, "tool_input": entree, "tool_response": json.dumps(reponse, ensure_ascii=False)})
        v = gate.controler(f)
        self.assertEqual(self.codes(v), {"LECTURE_PROFANE_ABSENTE", "LECTURE_FROID_ABSENTE", "RAPPORT_RAPPORTEUR_ABSENT", "CONTRADICTION_ABSENTE"})
        sha = L.sha256_fichier(f)
        ecrire(self.r / "ecritures/controle/ref.lecture_profane.json", {"sha256": sha, "a_compris_la_demande": True,
               "restitution": "Un avis médical du 10 mars 2026 préconise un aménagement que le directeur n'a pas examiné."})
        ecrire(self.r / "ecritures/controle/ref.lecture_froid.json", {"sha256": sha, "decision_claire": True, "question_claire": True,
                                                                      "demande_claire": True, "issue": "audience", "motifs": [],
                                                                      "profil_decideur_sha256": DEC.empreinte_fiche(profil, profil["decideurs"][0])})
        ecrire(self.r / "ecritures/controle/ref.rapport_rapporteur.json", {"sha256": sha, "conditions": [], "projet": {"issue": "audience"}})
        ecrire(self.r / "ecritures/controle/ref.contradiction.json", {"points": [{"id": 1, "objection": "o", "statut": "applique"}]})
        v = gate.controler(f)
        self.assertEqual(v["verdict"], "PASS", v["constats"])
        r = subprocess.run([PY, str(SCRIPTS / "affaire.py"), "finaliser", str(f)], cwd=self.r, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(any((self.r / "ecritures/FINAL").glob("ref__*.md")))
        ecrire(f, REFERE_BON + "\n3. Ajout après lecture.\n")
        self.assertEqual(gate.controler(f)["verdict"], "FAIL")


class TestObjectionsVersions(unittest.TestCase):
    def test_objection_suit_les_versions(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            ecrire(tmp / "etat/objections.json", {"objections": [
                {"id": "O1", "acte": "assignation_fond", "gravite": "dirimante", "statut": "ouverte"},
                {"id": "O2", "acte": "autre", "gravite": "dirimante", "statut": "ouverte"}]})
            ids = {o["id"] for o in L.objections_bloquantes(tmp, "assignation_fond_v2")}
            self.assertEqual(ids, {"O1"})
            self.assertEqual(L.objections_bloquantes(tmp, "assignation_fondamentale"), [])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestDomaines(unittest.TestCase):
    """Régimes et délais livrés par domaine : chargement, rattachement aux textes, sanction de chaque condition, calculs."""
    DOM = SCRIPTS.parent / "references" / "domaines"

    def test_regimes_charges_et_sources(self):
        import gate
        fichiers = sorted(self.DOM.glob("*_regimes.json"))
        self.assertGreaterEqual(len(fichiers), 4)
        self.assertGreater(gate.charger_regimes_domaines(), 40)
        cats = gate.categories_conditions()
        permises = {"delai_tardivete", "prealable_obligatoire_absent", "formalite_substantielle", "incompetence", "acte_non_attaquable",
                    "interet_qualite", "prescription_forclusion", "urgence_absente", "doute_serieux_absent", "contestation_serieuse",
                    "motif_legitime_absent", "non_epuisement", "mal_fonde"}
        domaines = set()
        for f in fichiers:
            for e in json.loads(f.read_text(encoding="utf-8")):
                self.assertTrue(e.get("type_acte") and e.get("conditions") and e.get("texte"), (f.name, e.get("type_acte")))
                domaines.add(e.get("domaine"))
                for nom in e["conditions"]:
                    self.assertIn(cats.get(nom), permises, (f.name, e["type_acte"], nom))
        self.assertGreaterEqual(len(domaines), 10, domaines)

    def test_voies_par_domaine(self):
        import voies
        from datetime import date
        regles = voies.regles_domaines()
        self.assertTrue(all(r.get("texte") and ("mois" in r or "jours" in r) for r in regles))

        def fin(evt, mot):
            res = [r for r in voies.calculer_evenement(evt) if mot in r["libelle"].lower()]
            self.assertTrue(res, (evt, mot))
            return res[0]["date"]

        # Obligation de quitter le territoire, procédure de L. 911-1 : un mois ; 15 février 2026 est un dimanche, report au lundi.
        self.assertEqual(fin({"type": "notification_oqtf", "procedure": "L911-1", "notification": "2026-01-15"}, "quitter"), "2026-02-16")
        # Prescription d'un délit, six ans, sans report au jour ouvrable (samedi 14 mars 2026).
        self.assertEqual(fin({"type": "infraction", "nature": "delit", "date": "2020-03-14"}, "prescription"), "2026-03-14")
        # Opposition à injonction de payer signifiée à personne : un mois.
        self.assertEqual(fin({"type": "signification_ordonnance_injonction_payer", "a_personne": True, "signification": "2026-10-05"},
                             "opposition"), "2026-11-05")
        # Appel d'un jugement prud'homal : un mois depuis la notification.
        self.assertEqual(fin({"type": "jugement_prudhomal", "ressort": "premier", "notification": "2026-06-10"}, "appel"), "2026-07-10")


class TestVoies(unittest.TestCase):
    def test_delais(self):
        import voies
        from datetime import date
        # Notification le 17 novembre 2026 : deux mois mènent au dimanche 17 janvier 2027, reporté au lundi 18.
        self.assertEqual(voies.echeance(date(2026, 11, 17), 2, 0, False), date(2027, 1, 18))
        self.assertEqual(voies.echeance(date(2026, 11, 16), 0, 15, False), date(2026, 12, 1))
        self.assertIn(date(2027, 5, 17), voies.feries(2027))  # lundi de Pentecôte 2027


if __name__ == "__main__":
    unittest.main()
