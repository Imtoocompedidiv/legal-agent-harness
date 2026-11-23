# La procédure comme levier de négociation, et ses limites déontologiques et pénales

Objet. Ce fichier dit comment le module `negociation-et-persuasion` se sert de la procédure pour obtenir un accord, et où s'arrête ce qui est permis. Il complète `droit_amiable.md` (règles D), `negociation_litterature.md` (règles N) et `persuasion_litterature.md` (règles P). Date de lecture : 18 novembre 2026 ; textes et décisions lus sur LibreJustice, avec les mêmes conventions de statut et de lecture que `droit_amiable.md`.

Règle du harness qui prime : la procédure peut servir de levier, jamais de menace illicite ; l'acte juridictionnel garde sa raison d'être propre et passe le filtre de chaque acte (`strategie-contentieuse`, section 2) sans compter sur l'effet qu'il produira sur l'adversaire.


## 1. Ce que la procédure donne au négociateur

**L1. Le levier licite est une alternative réelle, datée et prête, annoncée comme une échéance commune.**

Acte. Le plan désigne l'acte juridictionnel que le client accomplira sans accord (requête, référé, assignation, appel, exécution), sa date, son état de préparation et ce qu'il coûtera à l'adversaire (condamnation probable, intérêts, frais irrépétibles, astreinte, mesures d'exécution, charge de ses services, exposition à un précédent). Il l'annonce sobrement, une fois, avec sa date, comme une conséquence de l'absence d'accord (N3, N9, N10), et l'accomplit à la date annoncée si aucun accord n'est conclu (N22). Une alternative faible ne se révèle pas ; elle se renforce d'abord (preuve à créer, `action-sur-le-reel`).

Preuve. Règles N3, N9, N10, N22, N23 de `negociation_litterature.md` (empirique limité). Les délais et l'effet de chaque voie amiable sur eux : D1 et D2.

Statut. Inférence fondée sur des données limitées.

**L2. Le calendrier de l'instance est lui-même une monnaie d'échange.**

Acte. Le plan identifie les moments où l'adversaire a le plus à perdre à ne pas transiger (avant son mémoire en défense, N26 ; avant la clôture de l'instruction ; avant l'audience ; avant une expertise coûteuse ; après une décision provisoire favorable au client) et ceux où l'offre du client perd de sa valeur (après une décision défavorable). Il demande une médiation ou une audience de règlement amiable à un moment choisi (D12, D13), jamais pour gagner du temps contre l'intérêt du client.

Preuve. N26 (bilan de la médiation préalable obligatoire, pratique institutionnelle) ; CPC, art. 1532 ; CJA, art. L. 213-7.

Statut. Inférence.


## 2. Ce que la loi pénale interdit

**L3. La menace d'une voie de droit liée à ce qui est réclamé est licite ; la menace de révéler des faits déshonorants pour obtenir un paiement ou une signature est un chantage.**

Acte. Une lettre de négociation n'annonce que la voie de droit civile, administrative, commerciale ou sociale qui tend à obtenir ce qui est réclamé, avec son calendrier. Elle ne propose jamais de s'abstenir d'une plainte pénale, d'une révélation à la presse, aux réseaux, à un employeur, à un client, à une autorité de contrôle ou ordinale, en échange d'un paiement, d'une signature ou d'une renonciation. Si une plainte ou un signalement se justifie, il se décide sur son propre fondement, après analyse et accord du client, et ne s'échange contre rien. Le chiffre réclamé reste en rapport avec le dommage et défendable devant un juge (N12).

Preuve. Code pénal, art. 312-10 (version du 23 mai 2024, lu en entier) : le chantage consiste à obtenir, en menaçant de révéler ou d'imputer des faits de nature à porter atteinte à l'honneur ou à la considération, une signature, un engagement, une renonciation, la révélation d'un secret ou une remise de fonds ; cinq ans d'emprisonnement et 75 000 euros d'amende. Cass. crim., 12 mars 1985, n° 84-90.787, publié au Bulletin (texte lu) : si la menace de recourir aux voies légales pour obtenir le paiement d'une dette n'est pas punissable, le délit est caractérisé quand la menace de révéler une irrégularité susceptible de poursuites fiscales ou disciplinaires tend à obtenir l'exécution d'une convention nulle ; l'avocat qui avait prêté son concours à l'échange a été condamné comme complice, à une interdiction d'exercer d'un an. Cass. crim., 30 janvier 2001, n° 99-87.346 (texte lu) : deux avocats avaient adressé une lettre recommandée menaçant de porter plainte pour usage frauduleux des biens d'une société, présentation de bilan inexact et faux si une somme n'était pas réglée sous dix jours ; la chambre d'accusation ne pouvait refuser d'informer en affirmant abstraitement que la menace de plainte n'est jamais un chantage ; elle devait rechercher si les auteurs étaient victimes d'une infraction et si la somme réclamée était en rapport avec le dommage. Cass. crim., 8 mars 2011, n° 10-85901 (texte lu) : la menace de révéler à la presse et aux autorités des pratiques illégales, contre 500 000 euros, oblige le juge à rechercher si les faits révélés étaient ceux dont l'auteur avait été lui-même victime, faute de quoi ils ne peuvent fonder aucune créance.

Statut. Droit positif pour l'incrimination et les critères de la chambre criminelle ; inférence pour la ligne de conduite, plus stricte que le minimum légal, parce qu'elle prive l'adversaire d'un incident pénal qui ruinerait la négociation et la crédibilité du client (P10).

**L4. Une plainte pénale ou une saisine d'autorité n'est jamais un objet de la négociation.**

Acte. Le plan n'inscrit ni plainte, ni signalement, ni saisine d'une autorité disciplinaire ou de contrôle parmi les contreparties ou les leviers. Quand une telle voie est décidée, elle figure dans la ligne stratégique comme une voie autonome, avec son fondement, et la négociation n'y fait pas allusion. Le script `negociation.py` bloque ces termes dans les champs adressés à l'adversaire et dans les leviers.

Preuve. L3.

Statut. Inférence tirée du droit positif ; règle du harness.


## 3. Ce que la procédure interdit

**L5. L'acte qui ne vaut que par la pression qu'il exerce s'expose à l'amende pour procédure abusive.**

Acte. Aucun acte juridictionnel n'est déposé dans le seul but de peser sur la négociation, ni maintenu après qu'il a perdu son objet. Chaque acte se justifie par le résultat qu'il peut obtenir du juge ; la négociation peut en tirer parti, elle n'en est pas la cause.

Preuve. CPC, art. 32-1 (version du 11 mai 2017, lu en entier) : amende civile jusqu'à 10 000 euros pour action dilatoire ou abusive, sans préjudice de dommages-intérêts. CJA, art. R. 741-12 (version du 1er janvier 2017, lu en entier) : amende jusqu'à 10 000 euros pour requête abusive.

Statut. Droit positif pour les sanctions ; inférence pour la règle de conduite.


## 4. Ce que la déontologie et la loyauté imposent

**L6. Loyauté, modération et courtoisie gouvernent le ton de la négociation, y compris quand l'adversaire ne les respecte pas.**

Acte. Les écrits de négociation sont exacts, sans fausse allégation sur les faits, les pièces, le mandat ou des offres concurrentes (N4), sans pression personnelle, sans mépris. Le négociateur ne qualifie pas l'adversaire ; il qualifie ses actes et leurs conséquences (P13).

Preuve. Décret n° 2023-552 du 30 juin 2023 portant code de déontologie des avocats, art. 3 (version du 3 juillet 2023, lu en entier) : dignité, conscience, indépendance, probité, humanité, honneur, loyauté, égalité, non-discrimination, désintéressement, confraternité, délicatesse, modération, courtoisie ; compétence, dévouement, diligence et prudence envers le client.

Statut. Droit positif pour les principes ; inférence pour leur traduction en négociation.

**L7. Le régime de confidentialité se choisit avant d'écrire.**

Acte. Le plan dit, pour chaque échange, s'il passe par une correspondance entre avocats (confidentielle sauf mention « officielle »), par une médiation, une conciliation ou une audience de règlement amiable (confidentielles, pièces produites exceptées), ou par une lettre directe du client (aucune protection). Le contenu suit le régime : une lettre directe se rédige comme une pièce que le juge lira (P20).

Preuve. Loi n° 71-1130 du 31 décembre 1971, art. 66-5 ; CPC, art. 1528-3 ; CJA, art. L. 213-2 ; D15.

Statut. Droit positif.

**L8. On n'enregistre pas une négociation à l'insu de l'adversaire pour s'en servir comme preuve.**

Acte. Le plan exclut l'enregistrement clandestin d'un échange de négociation. Si une preuve détenue par l'adversaire est indispensable, elle s'obtient par les voies du droit (demande de communication, injonction de produire, mesure d'instruction, `strategie-contentieuse`, section 4).

Preuve. Cass., Assemblée plénière, 22 décembre 2023, n° 20-20.648, publié au Bulletin et au Rapport (sommaire lu) : dans un procès civil, une preuve obtenue de manière illicite ou déloyale peut être admise si sa production est indispensable à l'exercice du droit à la preuve et si l'atteinte aux droits antinomiques est strictement proportionnée au but poursuivi ; le juge met en balance. En matière de médiation, ce qui est dit est de surcroît confidentiel (D15).

Statut. Droit positif pour le contrôle de proportionnalité ; inférence pour l'exclusion, la recevabilité restant une mise en balance incertaine et l'enregistrement exposant aussi les propos du client.


## 5. Ce que la négociation ne doit jamais faire au contentieux

**L9. Rien de la négociation n'entre dans l'écrit destiné au juge, sauf ce que la loi exige.**

Acte. L'écrit au juge ne cite ni offre, ni contre-offre, ni point de réservation, ni concession envisagée, ni propos tenu en médiation. Il mentionne seulement, quand la loi l'exige, les diligences amiables accomplies ou la dispense (CPC, art. 54, 5°), et, quand cela sert la demande, le fait objectif d'une demande préalable restée sans réponse ou d'une médiation refusée par l'adversaire, sans son contenu. Le script `negociation.py` bloque l'écrit qui contient le point de réservation, la cible ou le montant d'une contrepartie, et signale les formules qui révèlent une proposition.

Preuve. CPC, art. 54 et 1528-3 ; CJA, art. L. 213-2 ; Wistrich, Guthrie et Rachlinski 2005, cités par decideurs C2 : des juges qui savent devoir ignorer une demande révélée en conciliation en restent influencés (empirique limité).

Statut. Droit positif pour la confidentialité et la mention des diligences ; inférence pour le reste.

**L10. Aucune faiblesse avouée, ni au juge, ni à l'adversaire.**

Acte. En négociation, le plan parle de contreparties et d'échanges : chaque concession répond à une contrepartie et se justifie par une raison extérieure (N18, N21), jamais par un aveu de faiblesse du dossier. L'analyse des faiblesses reste interne (risques, solution de repli). Le script `negociation.py` bloque les formules d'aveu dans l'offre, les contreparties et les messages du plan de persuasion.

Preuve. Règle du harness ; N9, N36 ; P11, P14 ; D15 sur l'absence de protection des lettres directes.

Statut. Règle du harness, cohérente avec la littérature lue.

## Sources lues

| Source | Lecture |
| --- | --- |
| Code pénal, art. 312-10 (version du 23 mai 2024) | lu en entier |
| CPC, art. 32-1 ; CJA, art. R. 741-12 | lus en entier |
| Décret n° 2023-552 du 30 juin 2023, art. 3 | lu en entier |
| Loi n° 71-1130 du 31 décembre 1971, art. 66-5 | lu en entier |
| Cass. crim., 12 mars 1985, n° 84-90.787 | texte lu |
| Cass. crim., 30 janvier 2001, n° 99-87.346 | texte lu |
| Cass. crim., 8 mars 2011, n° 10-85901 | texte lu |
| Cass., Ass. plén., 22 décembre 2023, n° 20-20.648 | sommaire lu |
| Cass. crim., 25 octobre 1973, n° 72-93.485 ; 22 octobre 2008, n° 08-81352 | sommaire ou résumé de l'outil seulement, non utilisés |
