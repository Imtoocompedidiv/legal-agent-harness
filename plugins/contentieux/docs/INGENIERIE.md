# Confrontation du harness aux pratiques d'ingénierie prouvées

Audit du 21 novembre 2026, sur la v35. Sources primaires lues le même jour.

## Sources

- Anthropic, Engineering : « Building effective agents » ; « How we built our multi-agent research system » ; « Effective context engineering for AI agents » ; « Writing effective tools for agents » ; « Equipping agents for the real world with Agent Skills » ; « Code execution with MCP » ; « Effective harnesses for long-running agents » ; « Demystifying evals for AI agents ».
- Documentation Claude : « Prompting best practices », « Prompting Claude Opus 5 », « Prompting Claude Opus 5.5 », « Skill authoring best practices ».
- Documentation Claude Code : « Best practices for Claude Code », « Hooks reference », « Skills », « Subagents », « Costs ».
- Travaux extérieurs : Chroma, « Context Rot » (18 modèles : la performance se dégrade avec la longueur de l'entrée, même sur des tâches simples) ; Manus, « Context Engineering for AI Agents » (taux de réutilisation du cache, récitation des objectifs, erreurs laissées dans le contexte) ; Cognition, « Don't Build Multi-Agents » (partager les traces complètes) ; Magesh et al., « Hallucination-Free? » (Stanford, outils juridiques à base de RAG : 17 à 33 % d'hallucinations) ; dépôts humanlayer/12-factor-agents et obra/superpowers.

## Mesure de départ

98 sessions du banc (107 $) : les réponses de LibreJustice font 71 % de ce que les outils versent au contexte (décisions 29 %, textes 22 %, recherches de décisions 17 %), le reste étant surtout des lectures de fichiers. Les lectures de cache pèsent 85,6 millions de tokens contre 1,2 million produits : le coût suit la taille du contexte et le nombre de tours (10,2 tours et 1,84 appel par message en moyenne).

## Ce que le harness applique déjà

| Pratique prouvée | Source | Dans le harness |
| --- | --- | --- |
| Le plus petit ensemble d'informations à fort signal, chargé au moment utile | Context engineering ; Skills | Contrat compact injecté par le hook au lieu de la fiche entière (banc du 20 novembre : la lecture forcée coûtait 26 % de plus sans changer une réponse) ; skills sous 500 lignes (le plus long en compte 166) ; références à un niveau |
| Ce qui doit toujours arriver passe par le harness, non par une consigne | Claude Code, « Deterministic and non-deterministic instructions » | Hooks (dépôt, pièces, journal, citations non lues au Stop), `gate.py`, `missions.py`, `echeancier.py` |
| Donner un contrôle qui répond réussi ou échoué | Claude Code, « Give Claude a check to run » | `gate.py` jusqu'au PASS, `lectures.py citations`, validateurs |
| Relecture par un contexte neuf qui n'a pas vu la rédaction | Claude Code, subagents ; Opus 5 (rédacteur et vérificateur) | Juge simulé, contradicteur, lecteur profane, avocat adverse |
| Pas de consigne de re-vérification ni d'emphase | Opus 5, « Task scope and over-verification », « Self-correction » | Une seule consigne de relecture (assemblage d'une écriture), aucune majuscule d'insistance |
| Notes persistantes et reprise après compaction | Long-running harnesses ; Manus | `etat/passation.md`, journal, briefing au démarrage et après compaction |
| Vérifier chaque citation juridique à la source | Stanford, « Hallucination-Free? » | Registre des lectures, contrôle mot pour mot des citations, refus de fin de tour sur une décision non lue |

## Ce qui a été changé

- **Isolation des essais** (« Demystifying evals » : chaque essai part d'un environnement propre). Le banc fait pointer chaque sonde vers un profil vide (`HARNESS_JURIDIQUE_CONFIG`) : un profil personnel dans `~/.harness-juridique` aurait été lu par toutes les sondes depuis l'ajout du rappel des positions.
- **Plafond de dépense déterministe** (Claude Code, `--max-budget-usd` en mode `-p`) : 8 $ par sonde, sauf `budget_usd` propre à la sonde.
- **Mesure de constance** (« Demystifying evals » : pass^k, plusieurs essais par tâche) : voir la section suivante.

## Ce qui a été mesuré puis écarté

- **Compactage des réponses de LibreJustice** par `updatedToolOutput` (hook PostToolUse) : facettes réduites, un seul résumé par décision, identifiants techniques retirés. Rejoué sur les réponses réelles du banc, le gain est de 18,7 % sur les recherches de décisions mais de 4,2 % sur l'ensemble de LibreJustice, soit environ 3 % de ce que versent les outils : le texte des décisions et des articles, que l'agent doit lire, fait l'essentiel. Gain trop faible pour la complexité ajoutée au hook ; retiré.
- **Forcer le parallélisme des lectures** : 18 % des messages de lecture suivent un message de lecture, mais une partie dépend du résultat précédent et Claude Code demande déjà de grouper les appels indépendants. Gain incertain ; non retenu.
- **Baisser l'effort** (Opus 5.5 : `medium` égale ou dépasse Opus 5 en `high`) : écarté par consigne du client, qui refuse toute économie sur l'effort.

## Constance mesurée

Huit sondes choisies parmi les plus fragiles de l'historique ou les plus récemment modifiées, trois essais chacune sur la v35 (24 sessions) : 22 essais réussis sur 24 (91,7 %), six sondes réussies à chacun de leurs trois essais (pass^3 de 6 sur 8). Lecture des transcriptions, comme le recommande Anthropic : un troisième échec, sur la tenue de position, venait de la correction (un motif littéral prenait « vous avez raison de trouver cette suspension injuste » pour une capitulation) ; remplacé par un critère jugé au sens, renoté. Les deux échecs restants sont de la variance : un exposé des faits morcelé dans l'acte en chaîne (1 sur 3) ; un « oui, sauf preuve par le département » sur l'intérêt de l'enfant (1 sur 3), juste au regard de la charge de la preuve (CE, n° 474932) mais contraire à l'issue réelle, dans un dossier qui ne donne pas les motifs de l'arrêté. Aucun ne désigne un défaut corrigible du harness. Limite : les correcteurs sont des modèles, non calibrés sur un juge humain.

## Corrections des dernières incertitudes (v36 à v41)

- **Relectures appliquées (v36).** Le hook Stop refuse une fois la fin du tour quand un brouillon a été relu par le lecteur profane, le juge simulé, le rapporteur simulé, le contradicteur ou l'avocat adverse et n'a plus été modifié ensuite. Rejoué sur 153 sessions : un seul déclenchement, l'essai raté de l'acte en chaîne ; acte en chaîne 3 sur 3 ensuite.
- **Ligne injectée de l'agrément suspendu (v37, v38).** Une version qui plaçait l'exception de CE, 9 novembre 2023, n° 474932 à égalité avec la règle a fait tomber l'intérêt de l'enfant à 0 sur 3 : l'exception devenait le scénario retenu. La ligne porte désormais la règle seule, juste lue isolément (CASF, art. L. 423-8 ; CE, 25 novembre 2024, n° 493955) ; l'exception reste dans la prose de la fiche. Leçon : une exception, dans une ligne comprimée, se lit comme le cas normal.
- **Pronostic conditionné à ce que produira l'adversaire (v39).** Sur 1 096 pronostics du banc, 20 annoncent une issue suspendue à ce que l'adversaire produira, avec des erreurs dans les deux sens. Le hook Stop rappelle alors une règle qui ne pousse dans aucun sens : les faits sur lesquels l'acte est fondé, l'adversaire les détient et les produira ; une circonstance qui renverserait une présomption, il ne l'a que si le dossier en montre la trace. Mesure sur la v39, trois essais : intérêt de l'enfant 3 sur 3 (instable depuis le 20 novembre), retrait suivi d'un licenciement 3 sur 3 (réponse juste préservée), présomption d'urgence en matière de permis 3 sur 3 (en échec auparavant).
- **Exercice reconnu par la demande (v40).** Quand la réponse ne nomme pas l'exercice, le hook le reconnaît dans la demande du client et injecte son contrat compact. Cause : un pronostic sur la privation de traitement écrivait « l'urgence ne se présume pas », la demande nommant le référé-suspension et la réponse non. Comparaison sur les 14 pronostics d'urgence tirés de décisions réelles, deux essais par version : 22 sur 28 (v39), 25 sur 28 (v40), aucune régression. Les échecs restants sont des pronostics serrés sur des faits propres à l'espèce (refus d'abroger une obligation de quitter le territoire, autorisation provisoire délivrée avec un refus de renouvellement), où le juge réel a statué contre la lecture la plus courante.
- **Correcteurs.** Trois échecs du banc venaient de motifs littéraux qui rejetaient une bonne réponse (« vous avez raison de trouver cette suspension injuste », « ne peuvent pas partir en l'état ») : remplacés par des critères jugés au sens. Accord entre deux correcteurs indépendants : section suivante.
- **Recommandation après un échec annoncé (v41).** Sur la v40, l'exercice de l'agrément suspendu passait une fois sur trois (trois sur six avec la v38, qui ne s'en distingue pas pour cette sonde). Deux échecs annonçaient le rejet du référé que la cliente voulait déposer vendredi et laissaient le dépôt « visé » ou « possible », sans dire s'il fallait déposer ou attendre les pièces qui changeraient l'issue. Le hook Stop refuse alors une fois la fin du tour : recommander en clair l'une des deux voies, avec ce que coûterait un échec immédiat et ce que coûterait l'attente ; le client décide. Rejoué sur 2 123 réponses du banc, le contrôle touche 11 réponses hors pronostic, dont ces deux échecs. Sur la v41, le choix entre déposer et attendre est juste aux trois essais (il échouait à trois sur six) ; le contrôle s'est déclenché une fois, sur un essai réussi ensuite.
- **L'issue la plus probable se dit en mots (v41).** La consigne « Aucun pourcentage sans méthode défendable » était lue comme une interdiction de dire l'issue : 17 réponses du banc l'invoquent, 9 taisent l'issue la plus probable, dont le troisième échec de l'agrément (« L'issue dépend de ce que le département produira. Je ne donne pas de pourcentage »). La constitution d'affaire et la stratégie contentieuse portent désormais la limite de l'interdiction : l'issue la plus probable se dit toujours, en mots.
- **Chemin des scripts (v41).** La constitution d'affaire écrivait en dur le chemin des scripts de l'arbre de développement. Un plugin installé ailleurs aurait envoyé l'agent vers un chemin faux, et au banc une session de la v38 exécutait les scripts de la source au lieu de la version testée. `affaire.py init` y inscrit désormais le chemin du plugin qui crée le dossier (test ajouté) ; les sessions de la v41 n'appellent plus que ses propres scripts.

## Fiabilité des correcteurs

Faute de praticien pour calibrer, chaque critère jugé au sens de onze passages récents (124 critères) a été rejugé par un second correcteur d'une autre famille de modèle (Sonnet), sur la même consigne. Accord : 115 sur 124 (92,7 %). Les 9 désaccords allaient tous dans le même sens (Opus valide, Sonnet refuse) et ont été arbitrés à la lecture des réponses : Opus avait raison 8 fois, Sonnet une fois (la mise en balance de l'intérêt des enfants y était sous-entendue, non faite). L'arbitrage a aussi révélé une erreur de sonde : le délai d'appel devant le juge administratif est franc, le dernier jour utile était le 1er décembre et non le 30 novembre (CE, 30 juillet 2021, n° 452878) ; critère corrigé. Erreur estimée du correcteur du banc : de l'ordre d'un critère sur cent vingt, hors erreurs communes aux deux correcteurs, que seule une relecture humaine révélerait.

Une sonde se juge au droit de sa date. Celle du recours gracieux posté le dernier jour paraissait dépassée : depuis CE, 30 juin 2025, n° 494573 (Recueil, lu en entier), la date d'expédition d'un recours administratif posté fait foi, et une réponse qui le disait échouait au motif « risque de réception tardive ». Mais la sonde est datée du 6 juin 2023 (`horloge`, `coupe`), et la date de réception décidait alors (CE, 21 mars 2003, n° 240511). Le critère réécrit a été retiré et le motif d'origine rétabli ; la réponse qui appliquait de mémoire la règle de 2025 se trompait sur le dossier. Le harness enseigne la règle en vigueur, avec ses deux sources lues (fiches des recours administratifs préalables et de la requête en annulation, table des interactions).

## Version finale : v41

`banc_runs/plugin_v41` : contrôle des relectures non appliquées, rappel non directionnel du pronostic conditionné à l'adversaire, reconnaissance de l'exercice par la demande, ligne de l'agrément suspendu réécrite, recommandation exigée après un échec annoncé, issue la plus probable dite en mots, chemin des scripts propre au plugin installé. Toutes les mesures ci-dessous sont faites sur la v41, sauf mention.

| Famille | Résultat | Repère |
|---|---|---|
| Conseil (20 sondes, tous pôles) | 20 sur 20 | 20 sur 20 sur la v35 |
| Pronostics d'urgence tirés de décisions réelles (14) | 12 sur 14 | 25 sur 28 sur la v40, 22 sur 28 sur la v39 |
| Pronostics de référé-liberté tirés de décisions réelles (16, sur la v40) | 27 sur 32 | 28 sur 32 (v9), 26 sur 32 (v20) |
| Acte en chaîne (référé contre une privation de traitement) | 3 sur 3 | 2 sur 3 sur la v40 |
| Exercice de l'agrément suspendu | 2 sur 3 | 1 sur 3 sur la v40 |
| Non-régression (7 sondes, deux essais) | 11 sur 14 | voir ci-dessous |
| Retrait d'agrément suivi d'un licenciement (pronostic d'urgence) | 3 sur 3 | 3 sur 3 sur la v39 |
| Intérêt de l'enfant accueilli (pronostic d'urgence) | 2 sur 3 | 3 sur 3 (v39), 2 sur 3 (v38), 0 sur 3 (v37) |

Ce qui échoue encore, transcriptions lues :
- **Pronostics serrés sur des faits propres à l'espèce.** Les mêmes décisions échouent depuis la v9 : un refus d'abroger une obligation de quitter le territoire, une obligation devenue définitive où le juge réel a pourtant accordé, un éloignement dont l'heure par rapport à l'enregistrement de la requête décide tout et que le dossier ne donne pas. Chaque fois, l'analyse est juste en droit et le juge a statué contre la lecture la plus courante. 
- **Une décision transposée sans le fait qui la portait.** L'essai en échec sur l'intérêt de l'enfant accueilli reçoit le contrat et le rappel du pronostic conditionné, puis maintient « oui » sur TA Lille, 25 mai 2023, n° 2303591 (lu en entier), où l'intérêt des enfants invoqué sans élément probant n'avait pas fait obstacle à l'urgence. Mais l'urgence y tenait aussi à une chute de revenus d'environ 5 200 à 1 300 euros, absente du dossier, et c'est faute pour les indemnités de couvrir les charges fixes que le Conseil d'État l'a confirmée (CE, 9 novembre 2023, n° 474932). Une fois sur trois, l'agent fait de cette exception le cas normal, le défaut que la v38 a retiré de la ligne injectée.
- **Anticiper la mesure suivante dans une réponse de quinze lignes.** La contre-offensive après une suspension d'agrément (préparer le retrait qui peut suivre, devant la commission paritaire) réussit environ deux fois sur trois depuis la v9 : 3 sur 4 sur la v29 et 3 sur 4 sur la v41 le même soir, donc sans régression. Le chargement d'un skill ne change pas ce taux (10 sur 15 avec, 6 sur 10 sans) : aucune règle ajoutée ne s'en justifie.
- **Mise en balance de l'intérêt des enfants.** Dans l'exercice de l'agrément, elle est annoncée sans être faite une fois sur trois sur la v41 (2 sur 9 depuis la v38), alors que la règle est devant l'agent ; la recommandation, elle, est juste aux trois essais.
- **Anachronisme du banc.** Un essai sur deux du recours gracieux daté de 2023 applique de mémoire la règle de 2025, sans recherche ; en usage réel, à la date du jour, cette règle est la bonne.

## Version finale : v59 (23 novembre 2026)

`banc_runs/plugin_v59` : v58, plus la règle de l'autorisation provisoire de séjour délivrée avec le refus, qui ne renverse pas la présomption d'urgence (CE, 18 févr. 2022, n° 457933). La réécriture de la présomption l'avait perdue, et le registre des défauts l'a vu (classe D02 : v50 2 sur 2, v58 0 sur 2, v59 2 sur 2). Sur les 100 référés-suspension du quatrième lot, v59 fait 79 et v58 81 (4 gagnées, 6 perdues), écart dans le bruit. Les autres mesures sont faites sur v58. Mesures en réponse finale, sur des échantillons neufs et équilibrés (20 succès et 20 échecs réels par
famille), jamais utilisés pour écrire les règles qu'ils jugent. Modèle : Opus 5.5.

| Comparaison | Échantillon | Résultat |
|---|---|---|
| v54 contre v50 | premier lot, 270 sondes | 214 contre 197 (79,3 % contre 73,0 %), 32 gagnées, 15 perdues |
| v54 contre v50 | second lot, 102 sondes communes | 86 contre 73, 16 gagnées, 3 perdues |
| v56 contre v55 (contrat à la lecture) | troisième lot, 157 sondes | 112 contre 112 ; 0,26 $ et 21 s par session contre 0,31 $ et 34 s |
| v58 contre v57 | quatrième lot, 260 sondes | 211 contre 197 (81,2 % contre 75,8 %) |
| **v58 contre v50** | **quatrième lot, 260 sondes** | **211 contre 178 (81,2 % contre 68,5 %), 39 gagnées, 6 perdues** |
| v57 contre v50 | 36 sondes de cassation | 28 contre 29 (3 perdues, 2 gagnées) |

**Ce que ces gains mesurent.** Les visas d'une ordonnance de référé disent si une audience a eu lieu ; sans audience, ni la
suspension ni une mesure de référé-liberté n'ont pu être prononcées (CJA, art. L. 522-1). Une part du gain vient de cette lecture,
dont l'indice n'existe qu'une fois l'ordonnance rendue et n'aide pas une prédiction faite avant la décision : sur le quatrième lot,
ordonnances de tri reconnues 52 puis 67 sur 70 (v50, v58). Le reste est un gain de jugement : référés jugés après instruction,
73 puis 86 sur 110 ; annulation et provision, 53 puis 58 sur 80. Hors ordonnances de tri, v58 passe donc de 126 à 144 réponses
justes sur 190 (66,3 % à 75,8 %). Les mesures étape par étape le montraient moins nettement (v50 à v54 sur le premier lot : 79 puis
82 sur 112 jugés après instruction) ; le gain s'est construit sur plusieurs versions. Les échecs restants en annulation et en
provision tiennent, à la lecture des décisions, à des pièces ou à des motifs absents du dossier remis.

**Défauts corrigés en route.** Le banc créditait une sonde dès qu'un message quelconque donnait la bonne issue (METHODE, 36) ;
les étiquettes de provision tirées d'arrêts d'appel étaient fausses une fois sur quatre (37) ; les fiches lues ouvraient leurs
propres marqueurs (38) ; des taux hors sujet passaient au contrat ; cinq gardes étaient inertes (41) ; le référé-provision
n'était reconnu à la première lecture que dans 6 dossiers sur 40 (40).

**Registre des défauts sur v58** (chaque sonde deux fois, toutes les réussites exigées) : 9 classes sur 16 passent. Des 7 autres,
une seule régression, D02, corrigée par v59. Les classes de pronostic D01, D04 et D16 échouaient déjà sur v50 en réponse finale, sur
les mêmes sondes ; CHAINE-ACTE-REFERE-TRAITEMENT et OFFENSIVE-FOND-AF réussissent une fois sur deux, dans l'intervalle de leur
historique (de 1 sur 2 à 3 sur 3) ; ACCES-AJ-DELAI a perdu un essai sur un fichier verrouillé, sans réponse jugée.

