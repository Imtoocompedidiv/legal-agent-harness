# Le conseil dans le harness : intégration de Claude for Legal en droit français

Ce document fixe l'architecture et le cahier des charges du conseil. Il s'impose à toute fiche, tout skill et tout script de conseil.

## 1. Origine et licence

La suite `anthropics/claude-for-legal` (licence Apache 2.0, clone du 21 novembre 2026, commit `4a6c651`, dans `un clone local de la suite`) compte treize plugins écrits pour le droit américain : privilège de l'avocat et *work product*, règle fédérale 408, DMCA, FMLA, critères propres à chaque État, recherche Westlaw. Ses hooks sont des coquilles vides et elle ne contient aucun contrôle déterministe. Le harness en reprend les méthodes de travail, adaptées, et en remplace tout le droit par le droit français et européen en vigueur, lu à la source. La copie de la licence et la mention des modifications figurent dans `docs/conseil/LICENCE-claude-for-legal.txt` et `docs/conseil/NOTICE.md`.

## 2. Architecture

Un seul moteur. Le conseil vit dans le même plugin que le contentieux, et il en emploie les mécanismes : registre des lectures et contrôle des citations, contrat compact injecté par le hook quand une réponse traite une mission sans en avoir lu la fiche, sous-agents (contradicteur, avocat-adverse, négociateur, vérificateur de sources, plume), dossier d'affaire quand il existe.

Pôles, un skill chacun. Le skill porte les procédés d'origine adaptés (étapes, grilles, livrables, garde-fous) et les textes à lire à la source ; il ne recopie pas la doctrine, que l'agent lit sur LibreJustice comme dans le contentieux. Mesure du 21 novembre : sur neuf sondes de droit du conseil, la v33, sans aucun pôle, en réussit huit et frôle la neuvième ; elle échoue en revanche quand il faut appliquer les positions du client. Une fiche de mission avec bloc de données ne s'écrit donc que lorsque le banc montre que le modèle se trompe sur le point, ou lorsqu'une mission a besoin d'un contrat compact injecté. Cinq fiches existent à ce jour (licenciement pour motif personnel, mise en demeure émise, réclamation reçue, examen d'accès au CRFPA, CAPA), leurs lignes injectées contrôlées par sondage à la source le 21 novembre 2026 (C. trav., art. L. 1225-4 ; CPC, art. 750-1 ; C. com., art. L. 145-41 dans sa version issue de la loi n° 2026-403 ; arrêté du 17 octobre 2016, art. 5), sans erreur trouvée.

| Pôle (skill) | Plugins d'origine |
| --- | --- |
| `contrats-d-affaires` | commercial-legal |
| `societes-et-operations` | corporate-legal, recette diligence-grid |
| `droit-social` | employment-legal |
| `donnees-personnelles` | privacy-legal |
| `intelligence-artificielle` | ai-governance-legal |
| `propriete-intellectuelle` | ip-legal |
| `conformite-et-produits` | product-legal, regulatory-legal, recettes reg-monitor et launch-radar |
| `precontentieux-et-portefeuille` | litigation-legal (ce que le contentieux ne couvre pas déjà), recette docket-watcher |
| `formation-juridique` | law-student |
| `acces-au-droit` | legal-clinic |

Composants communs :
- `profil-et-positions` : l'entretien d'ouverture et le réglage (cold-start-interview, customize, company-profile des treize plugins). Il écrit le profil et les positions dans `~/.harness-juridique/` (`profil.md`, `positions/<pôle>.md`, `registres/`), ou dans `cabinet/` à la racine du dossier de travail quand ce dossier existe, qui l'emporte alors.
- `veilleur` (sous-agent) et `scripts/echeancier.py` : les veilles programmées des recettes d'agents gérés et des agents de surveillance (renouvellements, échéances de propriété intellectuelle, vie sociale, absences, procédures, veille réglementaire), calculées sur les registres.
- `scripts/registres_publics.py` : la fiche d'une société à partir des sources publiques (API Recherche d'entreprises, BODACC), pour la vérification d'une contrepartie, une diligence ou la titularité d'un droit.
- `scripts/missions.py` : le catalogue des missions et le validateur des fiches.

## 3. La fiche de mission

Une mission par fiche : un travail que le client confie (revoir un accord de confidentialité, qualifier un traitement, préparer un licenciement, répondre à une mise en demeure). Plan imposé, titres exacts pour les sections 10 et 11 :

1. Qui décide, qui contrôle, sur quoi : le signataire, l'organe qui valide, l'autorité de contrôle ou le juge qui pourra en connaître, et la question qu'ils trancheront.
2. Le droit applicable et son office : textes en vigueur au 21 novembre 2026, ordre public et liberté contractuelle, régime spécial de la matière, droit transitoire.
3. Ce qui fait échouer l'opération et sa preuve : nullité, requalification, inopposabilité, sanction administrative ou pénale, responsabilité, perte d'un droit. Chaque point avec sa source lue.
4. L'objet : le document ou la situation, ce qui le qualifie, ce qu'il faut avoir en main.
5. Ce que le travail produit et sous quelle forme : note, grille, tableau, projet, contre-proposition, lettre ; mentions et formalisme obligatoires.
6. Exigences implicites : formalités, consultations (CSE, autorité), notifications, registres, délais et leur computation.
7. Ce qui fait réussir : la méthode d'origine adaptée, les positions par défaut et la grille VERT, ORANGE, ROUGE quand elle a un sens. ROUGE se fonde en droit (illicite, nul, réputé non écrit, sanctionné) ; ORANGE sur un risque établi par une source ; une position de place se dit position de place, jamais règle.
8. Erreurs hors sujet typiques.
9. Missions voisines (et exercices contentieux voisins).
10. Statistiques publiées : chiffres officiels lus à la source, avec leur périmètre, ou la mention de ce qui a été cherché sans résultat.
11. Points non vérifiés.

Puis `## Sources` (chaque texte et décision lus, avec lien LibreJustice ou officiel et date de lecture) et `## Données de contrôle`, un bloc JSON au schéma des fiches d'exercice :

- `id` (minuscules et soulignés, unique parmi missions et exercices), `intitule` (avec les articles principaux), `famille` : `"conseil"`, `juridictionnel` : `false`, `types_acte` (livrables), `cible` (`document`, `situation`, `pretention`, `norme`, `faits` ou `acte`), `condition_principale` (le point qui décide le plus souvent), `conditions_decisives` (liste d'objets `condition`, `ce_qui_la_fait_tomber`, `preuve`, `source`), `exigences_implicites` (objets `cle`, `exigence`, `source`), `voisins` (objets `exercice`, `quand_il_convient_mieux` ; `exercice` désigne une mission, un exercice ou `autre:<libellé>`), `erreurs_hors_sujet`, `marqueurs_texte`, `sources_principales`, et facultativement `a_lire`.

Le hook injecte, sans que l'agent lise la fiche, l'intitulé, la condition principale, les cinq premières lignes `ce_qui_la_fait_tomber` des deux premières conditions et trois puces de la section 10. L'audit du 21 novembre a trouvé 81 lignes de ce type trompeuses ou fausses sur 212. Règles :
- Chaque ligne reste vraie lue seule, comme une règle générale, devant un rédacteur qui ne lit pas la fiche : son champ d'application est dans la ligne (matière, qualité des parties, date, seuil). Une règle qui ne vaut que pour un sous-cas le dit.
- Chaque condition porte sa source dans `source`, lue à la source, et la même règle se retrouve, dans les mêmes termes de fond, dans la prose. Une inférence non sourcée ne figure pas dans le bloc.
- `marqueurs_texte` : expressions régulières en français, propres à la mission, qui reconnaissent une réponse qui la traite, sans attraper les missions voisines ni les exercices contentieux. Deux au moins.
- Pas de tiret cadratin, ni dans le bloc ni dans la fiche.

## 4. Le SKILL.md du pôle

En-tête `name` (le nom du dossier) puis `description` en une phrase qui dit ce que le pôle couvre et quand le charger. Corps : le périmètre et ce qui relève d'un autre pôle ou du contentieux ; le profil et les positions à lire (`~/.harness-juridique/positions/<pôle>.md` ou `cabinet/positions/<pôle>.md`) et ce qui se fait quand ils manquent (appliquer les positions par défaut de la fiche, les annoncer, proposer de les enregistrer, sans bloquer le travail) ; la liste des fiches, chacune avec son fichier ; la méthode commune du pôle ; les garde-fous ; le format des livrables ; les décisions qui reviennent au client.

`references/positions.md` : les questions d'entretien du pôle et, pour chaque position, la valeur par défaut, son fondement (règle d'ordre public, jurisprudence, usage de place dit comme tel) et ce qu'elle change dans la grille. Pas de bloc de données.

## 5. Garde-fous communs

- Secret et destination : l'avocat est tenu au secret professionnel, qui couvre ses consultations et ses correspondances avec son client ou un confrère, sauf mention « officielle » entre avocats (loi n° 71-1130, art. 66-5). Les consultations du juriste d'entreprise ne deviennent confidentielles qu'à compter du 1er janvier 2027, aux conditions de l'article 58-1 de la même loi (loi n° 2026-122 du 23 février 2026 ; décret n° 2026-1054 du 17 novembre 2026) : diplôme, formation éthique, destinataires limités aux organes de l'entreprise ou du groupe, mention « confidentiel - consultation juridique - juriste d'entreprise », classement isolé et non modifiable ; cette confidentialité n'est opposable ni dans une procédure pénale ou fiscale, ni au contrôle des autorités de l'Union. Hors de ces cas, une analyse interne peut être saisie ou communiquée (CNIL, Autorité de la concurrence, DGCCRF, inspection du travail, juge), et une mention « confidentiel » seule ne protège rien. Avant tout envoi hors du cercle du client, le livrable le dit et propose une version épurée.
- Statut de l'auteur : le profil dit qui écrit (avocat, juriste d'entreprise, particulier pour lui-même, clinique). Les règles de la consultation juridique (loi n° 71-1130, art. 54 et suivants) s'énoncent quand le livrable est destiné à un tiers ; elles ne servent pas de frein au travail du client pour lui-même.
- Aucun envoi, aucune signature, aucun dépôt, aucune notification sans décision du client ; le livrable s'arrête au projet et dit la décision attendue.
- Aucune donnée du client dans une requête publique ni un en-tête.
- Tout texte qui sort du cabinet se tient sans concession ni aveu de faiblesse ; les positions de négociation sont offensives et licites, chaque concession contre une contrepartie (`negociation-et-persuasion`, `rapport-de-force`).
- Toute règle employée se lit à la source à la date utile ; la fiche dit la date de sa lecture.

## 6. Correspondance avec l'origine

`docs/conseil/correspondance_<pôle>.md` : pour chaque skill et agent d'origine, ce qu'il devient (fiche, section, composant commun, exercice contentieux existant), ou pourquoi il n'est pas transposé, raison de droit à l'appui.

## 7. Contrôles

`python scripts/missions.py verifier` doit finir sans défaut bloquant. Les lignes injectées de toute fiche nouvelle passent un audit à la source indépendant de leur auteur avant d'être retenues.
