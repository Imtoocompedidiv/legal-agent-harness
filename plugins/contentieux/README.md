# Plugin contentieux pour Claude Code

Conduite de contentieux français dans Claude Code : un dossier persistant par affaire, des protocoles par type d'acte, des sous-agents à contexte isolé et des verrous exécutés par le harnais avant les actes critiques. Il complète le moteur `legal_harness` du même dépôt, qui reste la voie d'acquisition des sources officielles.

Pourquoi ces choix : [note d'architecture](docs/ARCHITECTURE.md). D'où viennent les verrous : [autopsie du référé rejeté au tri](docs/AUTOPSIE.md) et [audit interne](docs/recherche/03_audit_interne.md). Ce qui a été éprouvé : [essais](docs/ESSAIS.md).

## Installation

Une fois, depuis un terminal :

```
claude plugin marketplace add "<dépôt>"
claude plugin install contentieux@legal-agent-harness --scope user
```

Pour essayer sans installer, lancer Claude Code avec `--plugin-dir "<dépôt>\plugins\contentieux"`. Les hooks ne font rien hors d'un dossier d'affaire.

## Ouvrir une affaire

```
python "<dépôt>\plugins\contentieux\scripts\affaire.py" init "C:\chemin\Mon affaire" --intitule "..." --client "..." --adversaire "..." --objectif "..."
```

Ouvrir ensuite Claude Code dans ce dossier. Le briefing d'état s'affiche au démarrage. `LISEZMOI.md` du dossier décrit l'arborescence et les commandes ; `etat/affaire.json` reçoit les consignes du client (citations et affirmations interdites, ponctuation de ses textes, identifiants privés à ne jamais envoyer à une base publique, termes internes à ne jamais transmettre).

## Composants

Skills : `prise-en-main-affaire`, `action-sur-le-reel`, `strategie-contentieuse`, `recherche-juridique`, `recit-judiciaire`, `ecriture-juridictionnelle`, `refere-administratif`, `refere-civil`, `contentieux-du-fond`, `controle-de-la-norme`, `cassation`, `controle-avant-depot`, `analyse-documentaire`, `theorie-de-l-affaire`, `conduite-de-la-sequence`, `lecture-des-decideurs`, `negociation-et-persuasion`, `rapport-de-force`, `recherche-doctrinale`, `mecanique-des-exercices`.

Sous-agents : `architecte-strategique`, `contradicteur`, `juge-simule`, `rapporteur-simule`, `lecteur-profane`, `avocat-adverse`, `analyste-adverse`, `chercheur-juridique`, `lecteur-de-texte`, `verificateur-sources`, `stratege-terrain`, `negociateur`, `plume`, `analyste-documentaire`, `sociologue-institution`, `chercheur-doctrine`.

Outils offensifs :
- `scripts/juridiction.py` calibre le juge simulé sur la juridiction réelle. `profil` tire de la base ouverte de la justice administrative les décisions publiées, classe ce qu'elle trie, instruit et accorde, sans aucun décompte par magistrat (CJA, art. L. 10, al. 4) ; `calibrage` écrit `calibrage_<code>.md`, qui montre en nombre égal refus et accueils, au filtre et après instruction, avec les taux publiés, depuis la base ouverte ou depuis un relevé LibreJustice, borné strictement avant le jour du dépôt et la décision de l'affaire exclue ; `conditions` écrit les conditions du régime remises au rapporteur.
- `scripts/voies.py` calcule depuis la chronologie typée les naissances de décisions implicites et les délais de recours, d'appel, de pourvoi, d'opposition, de prescription et de maintien, avec jours fériés et date prudente, pour tous les domaines ; `--types` liste les événements reconnus, `--inscrire` ajoute les délais comme scénarios.
- `scripts/pieces.py` inventorie les pièces sans rien envoyer hors du poste (empreinte, format réel, pages, métadonnées, champs et cases de formulaire, signatures, versions antérieures d'un PDF, texte page par page, dates, montants, numéros d'envoi, auteurs, documents mentionnés), rend les pages en image pour l'examen visuel, vérifie chaque fiche d'analyse (chaque citation retrouvée sur sa page) et la matrice des preuves au format 2, dresse les manques (pièces citées hors bordereau, pièces non analysées, faits sans pièce, documents détenus par l'adversaire) et bloque un fait décisif sans extrait littéral d'une pièce analysée.
- `scripts/decideurs.py` (valider, controle, fiche-juge, squelette) valide le profil du juge et de l'institution adverse et écrit la fiche du décideur que reçoit le juge simulé ; `scripts/negociation.py` (valider, controle, squelette) valide le plan de négociation et bloque tout chiffre de la négociation dans un écrit au juge ; `scripts/controles_campagne.py` contrôle la théorie de l'affaire et la séquence.
- `scripts/lectures.py` tient le registre des lectures : chaque appel LibreJustice est capturé par le hook, avec sa réponse brute et son empreinte. Il confronte mot pour mot les citations d'une écriture aux textes lus (`citations`), vérifie la suite des décisions citées (`portee`) et la couverture de la recherche (`couverture`). `scripts/exercices.py` valide le diagnostic de l'exercice de chaque acte, d'après trente fiches lues à la source. `scripts/doctrine.py` valide les fiches de lecture doctrinale. `scripts/positions.py` tient le registre des positions défendues devant le client.
- `scripts/gate.py --regimes` liste les soixante-cinq régimes et, pour chaque condition, la sanction qu'entraîne son défaut.
- Registre `adverse/declarations.json`, tenu par l'analyste adverse : déclarations de l'adversaire avec leur paragraphe entier, les autres pièces du même auteur lues, les contradictions vérifiées, les silences et les usages proposés.

Hooks :

| Événement | Effet |
| --- | --- |
| SessionStart | briefing d'état au démarrage, à la reprise et après compaction |
| UserPromptSubmit | échéances à moins de 72 heures, canaux de notification en retard, objections dirimantes ; rappel qu'une question du client appelle un argument |
| PreToolUse (bloque aussi si le script échoue) | réserve la lecture à froid et ses variantes au juge simulé, la lecture profane au lecteur profane, la contradiction au contradicteur et la revue de charpente à l'architecte ; refuse l'écriture des pièces originales, du journal, de la constitution, des versions finales et des verdicts ; refuse les commandes destructives sur ces fichiers ; refuse une requête publique qui contient un identifiant privé ; refuse de consigner un dépôt sans accord du client d'au moins trois mots, recopié d'un message postérieur à la version finale, ou malgré un message postérieur de retenue |
| PostToolUse | valide la structure des fichiers d'état ; signale après chaque enregistrement d'une écriture les défauts bloquants au dépôt |
| PreCompact | dicte au résumé ce qu'il doit garder : délais, accords du client avec leurs mots, actes faits, lectures faites et non faites |
| Stop | refuse la fin du tour si le message cite une pièce ou une décision ni ouverte ni inscrite comme lue, ou si le dossier a changé sans passation réécrite |

Contrôle avant dépôt : `scripts/gate.py`, appelé par `affaire.py controle` et `affaire.py finaliser`. Avant toute écriture juridictionnelle il exige, en plus de la fiche de l'acte : les canaux de notification relevés, un audit de terrain récent, une ligne stratégique complète et postérieure à la dernière pièce citée, un récit éprouvé par le lecteur profane sur la version exacte, et le contexte complet de toute déclaration adverse sur laquelle repose un moyen. Régimes connus : soixante-cinq, intégrés (référés administratifs et civils, requête au fond administrative, assignation, conclusions, pourvoi, courrier précontentieux) et livrés par domaine dans `references/domaines/` (procédure civile, voies de recours, travail, commercial, procédures collectives, exécution, consommation, pénal, CEDH, QPC, administratif général, fiscal, urbanisme, étrangers, commande publique, fonction publique, responsabilité). Le contrôle recalcule le délai depuis l'événement de la chronologie que désigne la fiche, et chaque condition manquante est rattachée à la sanction qu'elle entraîne.

## Conseil

La suite Claude for Legal d'Anthropic (licence Apache 2.0, mention d'origine dans `docs/conseil/NOTICE.md`) est intégrée et réécrite pour le droit français et européen en vigueur, lu à la source. Architecture et cahier des charges : `docs/CONSEIL.md` ; correspondance procédé par procédé avec l'origine : `docs/conseil/correspondance_<pôle>.md`.

- Pôles (un skill chacun, une fiche par mission dans `references/`) : `contrats-d-affaires`, `societes-et-operations`, `droit-social`, `donnees-personnelles`, `intelligence-artificielle`, `propriete-intellectuelle`, `conformite-et-produits`, `precontentieux-et-portefeuille`, `formation-juridique`, `acces-au-droit`. Les fiches portent le même bloc de données que les fiches d'exercice : le hook injecte leur contrat compact dans une réponse qui traite une mission sans avoir lu sa fiche.
- `profil-et-positions` : entretien d'ouverture et positions du cabinet par pôle, dans `cabinet/` du dossier de travail ou `~/.harness-juridique/`. Le travail n'attend pas le profil : les positions par défaut des fiches s'appliquent et s'annoncent.
- `scripts/echeancier.py` : échéances calculées des registres (contrats, sociétés, marques) et échéances explicites (social, procédures), chacune avec sa source.
- `scripts/registres_publics.py` : fiche d'une société depuis l'API Recherche d'entreprises et le BODACC, avec alerte sur les procédures collectives et radiations.
- `scripts/missions.py` : catalogue et validateur des fiches de mission (`verifier`, `contrat <id>`).
- Sous-agent `veilleur` : échéances, santé des contreparties, textes et décisions nouveaux, dérive des positions ; il rapporte et n'envoie rien.

## Tests

```
python -m pytest -q plugins/contentieux/tests -p no:cacheprovider -n 4
python plugins/contentieux/scripts/missions.py verifier
python validation/banc/banc.py instantanes
python validation/banc/banc.py lancer --parallele 2
```

Méthode d'ingénierie et banc de sondes : `docs/METHODE.md` et `validation/banc/`.

Un dossier d'affaire ne se range jamais dans le répertoire du plugin : Claude Code y refuse toute écriture, qu'il traite comme sensible.

## Limites

Les verrous sont mécaniques et peuvent produire des faux positifs ; un PASS n'atteste ni la justesse juridique ni l'issue. Le juge simulé est un garde-fou, pas une prévision : après sa refonte (rapporteur puis formation, calibrage équilibré, textes lus à la source), il a prédit l'issue de seize décisions réelles neuves sur vingt, reconstituées à l'aveugle, et reconnu quatre succès sur six ; il se trompe encore sur la pesée des faits sans pièce et sur l'accueil partiel (résultats et limites dans `docs/ESSAIS.md`, section 10). Le harness ne profile aucun magistrat : l'analyse des pratiques d'un juge nommé est interdite (CJA, art. L. 10, al. 4). Les hooks n'existent que dans Claude Code. Rien n'est déposé ni envoyé par le plugin : l'accord exprès du client reste la condition de tout acte extérieur.

Conseil : les pôles portent des procédés et les textes à lire, pas le droit recopié ; leur justesse dépend de la lecture à la source que le harness impose. Au banc du 21 novembre 2026, la v35 a réussi les vingt sondes de conseil (dix-neuf sur la v35, une sur la v34 au même pôle), contre huit sur dix pour la v33 sur les sondes comparées ; l'écart tient aux positions du client, que la v33 n'appliquait pas. La version finale, v41, les a de nouveau toutes réussies le 22 novembre ; deux passages par sonde ne mesurent pas une variance fine. Les mesures de la version finale et ce qui échoue encore sont dans `docs/INGENIERIE.md`. Les connecteurs de la suite d'origine (Ironclad, DocuSign, iManage, Everlaw, CourtListener et les autres) ne sont pas repris ; la fiche publique d'une société ne remplace ni l'extrait Kbis ni l'état des inscriptions.
