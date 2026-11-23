"""Conseil : échéancier, registres publics (sans réseau), catalogue des missions et aiguillage du hook vers une fiche de mission.
Lancer : python -m pytest -q plugins/contentieux/tests/test_conseil.py -p no:cacheprovider"""
import json
import os
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import echeancier as EC  # noqa: E402
import missions as MI  # noqa: E402
import registres_publics as RP  # noqa: E402


class Echeancier(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "cabinet" / "registres").mkdir(parents=True)
        self.ancien = os.getcwd()
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self.ancien)

    def ecrire(self, nom, entrees):
        (self.tmp / "cabinet" / "registres" / f"{nom}.json").write_text(json.dumps(entrees), encoding="utf-8")

    def test_contrat_tacite_et_preavis(self):
        self.ecrire("contrats", [{"id": "C1", "objet": "SaaS", "date_effet": "2024-01-15", "duree_initiale_mois": 12,
                                  "reconduction": "tacite", "duree_reconduction_mois": 12, "preavis": {"valeur": 3, "unite": "mois"}}])
        r = EC.rapport(date(2026, 11, 21), 400, ("contrats",))
        dates = {x["nature"]: x["date"] for x in r["a_venir"] + r["depassees"]}
        self.assertEqual(dates["terme de la période en cours"], "2027-01-15")
        self.assertEqual(dates["date limite de dénonciation"], "2026-10-15")
        self.assertEqual([x["nature"] for x in r["depassees"]], ["date limite de dénonciation"])

    def test_societe_approbation_et_depot(self):
        self.ecrire("societes", [{"id": "S1", "objet": "SASU", "forme": "SASU", "date_cloture": "2026-06-30", "depot_electronique": False}])
        r = EC.rapport(date(2026, 11, 21), 200, ("societes",))
        dates = {x["nature"]: (x["date"], x["source"]) for x in r["a_venir"]}
        self.assertEqual(dates["approbation des comptes"][0], "2026-12-30")
        self.assertIn("L. 227-9", dates["approbation des comptes"][1])
        self.assertEqual(dates["dépôt des comptes au greffe"][0], "2027-01-30")

    def test_marque_renouvellement_et_grace(self):
        self.ecrire("pi", [{"id": "M1", "objet": "Marque", "type": "marque", "office": "INPI", "date_depot": "2017-03-15"}])
        r = EC.rapport(date(2026, 11, 21), 400, ("pi",))
        natures = {x["nature"]: x["date"] for x in r["a_venir"]}
        self.assertEqual(natures["expiration de l'enregistrement"], "2027-03-15")
        self.assertEqual(natures["fin du délai de grâce"], "2027-09-15")
        self.assertEqual(r["depassees"], [], "l'ouverture du renouvellement est une information, pas une échéance dépassée")

    def test_echeance_explicite_sans_source_signalee(self):
        self.ecrire("procedures", [{"id": "P1", "objet": "Appel", "echeances": [{"date": "2026-12-01", "nature": "conclusions"}]}])
        self.assertTrue(any("sans source" in d for d in EC.verifier()))


class RegistresPublics(unittest.TestCase):
    def test_alerte_procedure_collective(self):
        f = {"trouve": True, "denomination": "SOCIETE X", "siren": "123456789", "forme": "SAS (5710)", "date_creation": "2010-01-01",
             "etat": "active", "date_fermeture": None, "siege": {"adresse": "1 rue A", "siret": "12345678900011"},
             "activite": {"naf": "62.01Z"}, "effectif": "12", "categorie": "PME", "conventions_collectives": [], "dirigeants": [],
             "finances": {}, "ambiguite": [], "consulte_le": "2026-11-21 10:00",
             "bodacc": {"total": 2, "alertes": [{"date": "2026-10-01", "famille": "Procédures collectives",
                                                 "jugement": "Jugement d'ouverture de liquidation judiciaire", "tribunal": "TAE Paris"}],
                        "dernieres": [{"date": "2026-10-01", "famille": "Procédures collectives"}]}}
        texte = RP.imprimer(f)
        self.assertIn("ALERTE BODACC", texte)
        self.assertIn("liquidation judiciaire", texte)
        self.assertIn("Kbis", texte)

    def test_jugement_en_texte_json(self):
        self.assertIn("redressement", RP._jugement({"jugement": json.dumps({"nature": "Jugement d'ouverture de redressement judiciaire"})}))


class Missions(unittest.TestCase):
    def test_catalogue_sans_defaut_bloquant(self):
        bloquants = [d for d in MI.verifier() if d[0] == "BLOQUANT"]
        self.assertEqual(bloquants, [])

    def test_identifiants_distincts_des_exercices(self):
        import exercices as E
        self.assertFalse(set(MI.charger_missions()) & set(E.charger_catalogue()))

    def test_aiguillage_vers_une_mission(self):
        import hook as H
        sortie = H.aiguillage("Je vous propose ce projet de lettre de mise en demeure, à envoyer en recommandé.", [])
        self.assertTrue(sortie and "mission de conseil" in sortie[0] and "mise-en-demeure-emise.md" in sortie[0], sortie)
        # Une fiche déjà lue n'est pas réinjectée.
        lue = [{"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read", "input": {
            "file_path": "skills/precontentieux-et-portefeuille/references/mise-en-demeure-emise.md"}}]}}]
        self.assertEqual(H.aiguillage("Je vous propose ce projet de lettre de mise en demeure.", lue), [])

    def test_rappel_des_positions_du_client(self):
        import hook as H
        r = Path(tempfile.mkdtemp())
        self.assertEqual(H.positions_du_client(r), []) if not (Path.home() / ".harness-juridique").is_dir() else None
        (r / "cabinet" / "positions").mkdir(parents=True)
        (r / "cabinet" / "positions" / "contrats-d-affaires.md").write_text("# positions", encoding="utf-8")
        lignes = H.positions_du_client(r)
        self.assertTrue(lignes and "cabinet/positions/contrats-d-affaires.md" in lignes[0], lignes)

    def test_retours_des_relecteurs_appliques(self):
        import hook as H
        def appel(nom, **entree):
            return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": nom, "input": entree}]}}
        ecrit = appel("Write", file_path="C:/aff/ecritures/brouillons/requete_v1.md")
        relu = appel("Agent", subagent_type="contentieux:juge-simule", prompt="Lis C:/aff/ecritures/brouillons/requete_v1.md en entier.")
        self.assertIn("requete_v1.md", H.retours_non_appliques([ecrit, relu]) or "")
        self.assertIsNone(H.retours_non_appliques([ecrit, relu, appel("Write", file_path="C:/aff/ecritures/brouillons/requete_v2.md")]))
        self.assertIsNone(H.retours_non_appliques([ecrit, appel("Agent", subagent_type="contentieux:chercheur-juridique",
                                                                   prompt="Cherche pour ecritures/brouillons/requete_v1.md")]))

    def test_pronostic_conditionne_a_l_adversaire(self):
        import hook as H
        self.assertTrue(H.PRONOSTIC_CONDITIONNE.search("**Oui**, à une condition : que le département n'apporte pas d'éléments graves."))
        self.assertTrue(H.PRONOSTIC_CONDITIONNE.search("Non, 60 %. Urgence présumée sauf si l'employeur justifie de circonstances."))
        self.assertFalse(H.PRONOSTIC_CONDITIONNE.search("Oui. L'urgence est présumée et rien au dossier ne la renverse."))
        self.assertIn("en les supposant produits", H.MESSAGE_PRONOSTIC_CONDITIONNE)

    def test_contrat_equilibre(self):
        import hook as H
        import exercices as E
        cat = E.charger_catalogue()
        f = E.REFERENCES / cat["refere_suspension"]["fichier"]
        avant = H.contrat_compact(cat["refere_suspension"], f, "Refus de renouvellement de sa carte de résident ; un récépissé lui a été remis.")
        self.assertNotIn("Instruction close seulement", avant, "la ligne de l'instruction close ne vient pas avant la défense")
        susp = H.contrat_compact(cat["refere_suspension"], f, "Refus de renouvellement de sa carte de résident ; un récépissé lui a été "
                                 "remis. Par un mémoire en défense, le préfet conclut au rejet de la requête.")
        self.assertIn("Présomptions :", susp)
        self.assertIn("Ce qui remplit « urgence » : Instruction close seulement", susp)
        self.assertIn("18 févr. 2022", susp)
        self.assertIn("R. 431-5", susp, "la présomption suppose une demande de renouvellement déposée dans les délais")
        self.assertNotRegex(susp, r"n°\s*\d", "les numéros des décisions de la fiche ne passent pas au contrat (audit du 23 novembre)")
        self.assertNotIn("L. 600-3", susp, "la présomption du permis ne vient que pour un permis")
        # Budget relevé à 6 500 le 23 novembre 2026 : présomption du séjour réécrite et lignes du tri, issues de l'audit des biais.
        self.assertLess(len(susp), 6500)
        self.assertNotIn("Taux publiés : Tableau 15", susp, "l'admission des pourvois n'est pas le taux de succès du référé")
        lib = H.contrat_compact(cat["refere_liberte"], E.REFERENCES / cat["refere_liberte"]["fichier"], "Éloigné vers Mayotte malgré la saisine.")
        self.assertIn("Ce qui remplit « atteinte_grave_manifestement_illegale »", lib)
        self.assertIn("L. 761-9", lib)
        self.assertLess(len(lib), 6500)
        self.assertNotIn("14,5 %", lib)

    def test_regex_des_fiches_sans_caractere_de_controle(self):
        # « \b » mal échappé dans le JSON devient un retour arrière : la garde « bail » ne jouait jamais (23 novembre 2026).
        import re
        bloc = re.compile(r"## Données de contrôle\s*```json\s*(.*?)```", re.S)
        racine = Path(__file__).resolve().parents[1] / "skills"
        for f in racine.glob("**/references/*.md"):
            m = bloc.search(f.read_text(encoding="utf-8"))
            if m:
                pile = [json.loads(m.group(1))]
                while pile:
                    o = pile.pop()
                    if isinstance(o, dict):
                        pile.extend(o.values())
                    elif isinstance(o, list):
                        pile.extend(o)
                    elif isinstance(o, str):
                        self.assertFalse(any(ord(c) in (7, 8, 11, 12) for c in o), f"{f.name} : {o[:60]!r}")

    def test_fiche_lue_n_ouvre_pas_les_marqueurs(self):
        import hook as H
        fiche = str(Path(H.__file__).resolve().parents[1] / "skills" / "mecanique-des-exercices" / "references" / "refere-suspension.md")
        entrees = [{"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "a", "name": "Read", "input": {"file_path": fiche}},
                                                                 {"type": "tool_use", "id": "b", "name": "Read", "input": {"file_path": "C:/affaire/dossier.md"}}]}},
                   {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "a", "content": "renouvellement de son titre"},
                                                            {"type": "tool_result", "tool_use_id": "b", "content": "pièce du dossier"}]}}]
        self.assertEqual(H.lectures_de_la_session(entrees), "pièce du dossier")
        self.assertIn("renouvellement de son titre", H.lectures_de_la_session(entrees, dossier_seul=False))

    def test_pronostic_serre_appelle_la_recherche(self):
        import hook as H
        self.assertEqual(H.pronostic_serre("**Non, 65 %.** Le juge rejettera."), 65)
        self.assertIsNone(H.pronostic_serre("Oui, 85 %. L'urgence est présumée."))
        self.assertIsNone(H.pronostic_serre("Non, 50 %."))
        recherche = [{"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "mcp__librejustice__search_decisions",
                                                                    "input": {"query": "x"}}]}}]
        self.assertEqual(H.recherches_de_jurisprudence(recherche), 1)
        self.assertEqual(H.recherches_de_jurisprudence([]), 0)
        self.assertIn("accueillent", H.MESSAGE_RECHERCHE_CONTRADICTOIRE)

    def test_aiguillage_reconnait_les_reponses_reelles(self):
        # Banc du 22 novembre : les réponses disent « le tribunal annulera », « la Cour cassera l'arrêt attaqué » ; reconnues 9 fois
        # sur 58 et 18 sur 36, le contrat et les lignes de la fiche n'atteignaient pas l'agent.
        import re
        import exercices as E
        cat = E.charger_catalogue()
        def premier(texte):
            return sorted(((sum(1 for m in v.get("marqueurs_texte") or [] if re.search(m, texte, re.I)), k) for k, v in cat.items()),
                          reverse=True)[0]
        cas = {"requete_annulation": "Oui, 70 %. Le tribunal administratif annulera la décision du préfet, insuffisamment motivée.",
               "pourvoi_civil": "Non, 65 %. La Cour de cassation ne cassera pas l'arrêt attaqué : le grief manque en fait.",
               "refere_suspension": "Oui. Le juge des référés suspendra l'exécution : l'urgence est présumée (CJA, art. L. 521-1).",
               "refere_liberte": "Non. Le référé-liberté échouera faute d'atteinte grave et manifestement illégale (art. L. 521-2).",
               "refere_civil_835_provision": "Oui, 60 %. Le juge du référé-provision (CPC, art. 835, al. 2) allouera une provision."}
        for attendu, texte in cas.items():
            with self.subTest(attendu=attendu):
                score, ident = premier(texte)
                self.assertGreater(score, 0)
                self.assertEqual(ident, attendu)

    def test_lignes_minees(self):
        import os
        from pathlib import Path
        import hook as H
        d = {"intitule": "Essai", "condition_principale": "urgence", "conditions_decisives": [{
            "condition": "urgence",
            "ce_qui_la_fait_tomber": ["g1", "g2", "g3", "g4", "g5",
                                      {"texte": "marquée", "marqueurs": ["permis"]},
                                      {"texte": "future", "marqueurs": ["permis"], "depuis": "2026-06-01"}],
            "points_disputes": [{"texte": "retard limité", "marqueurs": ["retard"]}]}]}
        ancien = os.environ.get("CONTENTIEUX_MAINTENANT")
        os.environ["CONTENTIEUX_MAINTENANT"] = "2025-01-15T10:00"
        try:
            s = H.contrat_compact(d, Path("absente.md"), "permis de construire ; dépôt en retard")
        finally:
            if ancien is None:
                os.environ.pop("CONTENTIEUX_MAINTENANT", None)
            else:
                os.environ["CONTENTIEUX_MAINTENANT"] = ancien
        self.assertIn("Ce qui fait tomber « urgence » : marquée; g1", s, "la ligne que le dossier déclenche passe en tête")
        self.assertNotIn("future", s, "une règle postérieure à la date du dossier ne s'y applique pas")
        self.assertIn("Juges partagés : « urgence » : retard limité", s)
        self.assertNotIn("marquée", H.contrat_compact(d, Path("absente.md"), "refus de titre"))

    def test_espece_citee_et_stade(self):
        import hook as H
        self.assertTrue(H.ESPECE_CITEE.search("comme l'a jugé le TA de Lille le 25 mai 2023 (n° 2303591)"))
        self.assertTrue(H.ESPECE_CITEE.search("Cass. soc., 3 févr. 2010, n° 07-44.491"))
        self.assertTrue(H.ESPECE_CITEE.search("comme devant le juge des référés de Lille le 25 mai 2023"))
        self.assertFalse(H.ESPECE_CITEE.search("au sens de l'article L. 521-1 du code de justice administrative"))
        self.assertIn("Instruction close", H.MESSAGE_PRONOSTIC_CONDITIONNE)

    def test_mesure_suivante_oubliee(self):
        import hook as H
        demande = [{"type": "user", "message": {"content": "La suspension de son agrément d'assistante familiale a été prononcée. Que faire ?"}}]
        sans = H.mesures_suivantes_oubliees("Je recommande d'abord d'obtenir les motifs, puis de saisir le juge des référés.", demande)
        self.assertTrue(sans and "commission consultative paritaire" in sans[0], sans)
        avec = H.mesures_suivantes_oubliees("Je recommande d'obtenir les motifs ; en vue du retrait, nous préparons dès maintenant les "
                                            "observations et les attestations pour la commission.", demande)
        self.assertEqual(avec, [])
        self.assertEqual(H.mesures_suivantes_oubliees("Je recommande de saisir le juge.", [{"type": "user", "message": {"content": "Un bail."}}]), [])

    def test_cout_du_tri_signale(self):
        import hook as H
        msg = "L'issue la plus probable est un rejet du référé. Je recommande le dépôt vendredi, une fois les pièces procédurales réunies."
        self.assertFalse(H.echec_sans_recommandation(msg))
        self.assertTrue(H.ECHEC_ANNONCE.search(msg) and H.DEMARCHE.search(msg))
        self.assertIn("L. 522-3", H.COUT_DU_TRI)

    def test_echec_annonce_sans_recommandation(self):
        import hook as H
        self.assertTrue(H.echec_sans_recommandation("Pronostic. L'issue la plus probable est un rejet. Le dépôt est visé vendredi 20."))
        self.assertFalse(H.echec_sans_recommandation("L'issue la plus probable est un rejet. Je vous recommande d'attendre les pièces : "
                                                     "déposer lundi coûte moins qu'un rejet au tri."))
        self.assertFalse(H.echec_sans_recommandation("L'issue la plus probable est la suspension. Dépôt vendredi."))
        self.assertIn("attendre ce qui changerait l'issue", H.MESSAGE_SANS_RECOMMANDATION)

    def test_exercice_reconnu_par_la_demande(self):
        import hook as H
        demande = [{"type": "user", "message": {"content": "Dis si la condition d'urgence de ce référé-suspension est remplie."}}]
        sortie = H.aiguillage("Non, 65 %. L'urgence ne se présume pas.", demande)
        self.assertTrue(sortie and "18 décembre 2024" in sortie[0], sortie)
        self.assertEqual(H.aiguillage("Non, 65 %. L'urgence ne se présume pas.", []), [])

    def test_exercice_garde_la_priorite(self):
        import hook as H
        sortie = H.aiguillage("Requête en référé-suspension (CJA, art. L. 521-1) : l'urgence est remplie.", [])
        self.assertTrue(sortie and "exercice" in sortie[0] and "Référé-suspension" in sortie[0], sortie)


if __name__ == "__main__":
    unittest.main()
