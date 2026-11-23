# Seconde mise au niveau : diagnostic et cahier des charges (18 novembre 2026, 16 h)

## Critique du client

1. Le harness a été construit et éprouvé autour d'un dossier particulier, alors qu'il doit valoir pour toute affaire.
2. Son niveau reste loin de celui d'un avocat aux Conseils ou d'un associé d'un cabinet de premier rang : une telle personne n'aurait pas attaqué la séquence ainsi, et le harness ne regarde pas la séquence dans son entier.
3. La simulation des juges a un défaut à régler.
4. La construction du récit, de la vérité et de l'affaire est faible.
5. Rien d'opérant sur la sociologie, la psychologie, la négociation, la persuasion.
6. Aucun bloc d'analyse documentaire, alors qu'il devrait être central.

## Ce que fait un avocat de premier rang et que le harness ne fait pas

- **Il prend l'affaire par la séquence, pas par l'acte.** Dès le premier acte adverse, il cartographie tous les actes, toutes les autorités, toutes les voies (amiable, hiérarchique, médiation, autorités indépendantes, contentieux de la légalité, indemnitaire, pénal, disciplinaire, presse, élus), leurs délais et la manière dont chacune nourrit les autres. Il choisit la cible qui décide vraiment et l'ordre des coups. Le harness actuel examine la charpente autour d'un acte déjà choisi.
- **Il établit la vérité avant d'écrire.** Il lit chaque document comme un enquêteur : qui l'a écrit, quand, pour qui, ce qu'il prouve et ce qu'il ne prouve pas, ce qui manque, ce qui se contredit, ce que l'adversaire détient. Il construit la chronologie et la matrice des preuves depuis les pièces, pas depuis le récit du client. Le harness actuel cote les pièces et tient un registre des déclarations adverses, sans méthode documentaire.
- **Il construit une théorie de l'affaire.** Un récit simple, vrai sur pièces, qui explique tous les faits défavorables sans les concéder, et qui donne au juge une raison de décider et un moyen de le faire. Il distingue ce qui est prouvé, ce qui est allégué, ce qui est contesté.
- **Il lit le décideur.** Le juge, sa formation, sa charge, sa culture, son contrôle (restreint, normal), sa déférence envers l'institution ; l'institution adverse, qui y décide, sous quelles contraintes, quels risques elle redoute. Il ajuste le forum, le moment, le ton.
- **Il négocie en même temps qu'il plaide.** Il connaît la meilleure solution de repli de chaque partie, ce que l'adversaire peut accorder sans perdre la face, et utilise la procédure comme levier, non comme fin.
- **Il refuse l'acte faible** et dit pourquoi, et il construit le terrain probatoire qui le rendra fort.

## Défaut de la simulation des juges, mesuré

Sur cent décisions réelles, le juge simulé prédit juste l'issue dans huit cas sur dix et méconnaît environ deux succès sur cinq. Ses erreurs sont constantes d'une lecture à l'autre. Causes identifiées dans la conception :
- le calibrage par juridiction ne lui montre que des ordonnances de tri (fichier `exemples_tri_<code>.md`), jamais d'ordonnance qui instruit ou accorde : il apprend la sévérité sans apprendre ce qui passe ;
- la consigne fait du rejet sa position par défaut aux stades de filtrage ;
- il statue en une passe, sans rapporteur qui instruit ni contrôle de son raisonnement ;
- il ne peut pas lire les textes qu'il applique, et se trompe sur des points de droit précis (préalable de l'article 85 du code de procédure pénale, conciliation et article 750-1 du code de procédure civile) ;
- en validation, il statue sans les pièces.

## Réponses

| Module | Contenu | Responsable |
| --- | --- | --- |
| Analyse documentaire | skill `analyse-documentaire`, sous-agent `analyste-documentaire`, script `pieces.py` (inventaire, extraction, rendu des pages en image pour les formulaires, métadonnées, dates, auteurs, destinataires, recoupements, manques, pièces détenues par l'adversaire), matrice des preuves rattachée aux extraits littéraux ; le contrôle bloque un fait décisif sans extrait de pièce | agent dédié |
| Psychologie et sociologie | références sourcées (psychologie de la décision, sociologie des juridictions et des institutions), skill `lecture-des-decideurs`, sous-agent `sociologue-institution` ; profil du décideur et de l'institution adverse exigé avant tout acte juridictionnel | agent dédié |
| Négociation et persuasion | références sourcées (négociation raisonnée, médiation, transaction, persuasion et rhétorique judiciaire), skill `negociation-et-persuasion`, sous-agent `negociateur` ; plan de négociation et de persuasion exigé | agent dédié |
| Simulation des juges | calibrage équilibré (refus et accueils, taux de base), délibéré en deux temps (rapporteur puis formation), accès aux textes sans accès aux décisions de l'affaire, protocole de raisonnement par condition ; mesure sur la part de mise au point | agent dédié |
| Théorie de l'affaire et séquence | skills `theorie-de-l-affaire` et `conduite-de-la-sequence`, architecte refondé pour partir du premier acte adverse et concevoir la campagne entière | session principale |
| Intégration | contrôle avant dépôt, hooks, tests, documentation ; épreuve sur une séquence réelle neuve, étrangère au dossier du client | session principale |

Critère d'acceptation commun : chaque module produit un fichier d'état que le contrôle lit et dont l'absence bloque, chaque règle tirée de la littérature cite sa source lue avec son statut, et une épreuve montre le module à l'œuvre sur une affaire réelle neuve.

## État de livraison, 18 novembre 2026, 21 h 24

| Module | Livré | Fichier d'état lu par le contrôle | Épreuve |
| --- | --- | --- | --- |
| Analyse documentaire | skill, sous-agent, `pieces.py`, schémas | fiches `pieces/analyses/`, matrice au format 2 ; fait décisif sans extrait littéral bloquant devant un juge | actes préfectoraux publics, `docs/epreuves/documentaire.md` |
| Lecture des décideurs | skill et trois références sourcées, sous-agent, `decideurs.py` | `strategie/decideurs.json` | TA de Rennes et préfecture, `docs/epreuves/decideurs.md` |
| Négociation et persuasion | skill et quatre références sourcées, sous-agent, `negociation.py` | `strategie/negociation.json` | CE, Section, 17 juin 2026, n° 489764, `docs/epreuves/negociation.md` |
| Simulation des juges | rapporteur puis formation, calibrage équilibré, textes seuls | rapport du rapporteur et lecture à froid sur l'empreinte exacte | part dev 21 sur 24 et 7 succès sur 8 ; troisième corpus de confirmation 16 sur 20 et 4 succès sur 6, mesuré une fois |
| Théorie de l'affaire et séquence | deux skills, architecte refondé, `controles_campagne.py` | `strategie/theorie.json`, `strategie/theorie_adverse.md`, `strategie/sequence.json` | séquence réelle neuve, `docs/epreuves/sequence.md` |

L'analyse des pratiques d'un magistrat nommé, interdite par l'article L. 10 du code de justice administrative, a été retirée du harness et des profils déjà générés.
