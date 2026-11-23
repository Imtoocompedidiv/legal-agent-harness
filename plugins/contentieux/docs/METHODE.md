# Méthode d'ingénierie du harness

Arrêtée le 19 novembre 2026. Elle remplace la boucle précédente, où chaque correctif attendait une épreuve complète d'une à deux heures, ne prouvait rien sur les autres capacités et laissait passer des régressions.

## 1. Quatre niveaux d'évaluation, du plus rapide au plus coûteux

| Niveau | Ce qu'il vérifie | Outil | Durée |
| --- | --- | --- | --- |
| L0, tests | les verrous et scripts déterministes | `python -m pytest -q plugins/contentieux/tests -p no:cacheprovider -n 4` | moins d'une minute |
| L1, instantanés | que le contrôle rend les mêmes verdicts sur les écritures réelles des épreuves | `python validation/banc/banc.py instantanes` | moins d'une minute |
| L2, banc de sondes | chaque capacité sur une situation minimale, avec une réponse attendue vérifiable mécaniquement | `python validation/banc/banc.py lancer` | une à trois minutes par sonde, en parallèle |
| L3, épreuves | la campagne entière sur une affaire réelle neuve, à l'aveugle | `docs/epreuves/sequence.md` | une à deux heures |

Une épreuve L3 ne se lance que si L0, L1 et L2 sont au vert. Elle sert à découvrir des défauts, pas à mettre au point un correctif.

## 2. Boucle de correction

1. **Observer.** Un défaut est un écart constaté entre ce que le harness a produit et ce qu'exigeait l'affaire : une décision réelle, un texte lu, une épreuve, une remarque du client vérifiée.
2. **Classer la cause racine**, une seule, la plus profonde :

   | Cause | Définition |
   | --- | --- |
   | `connaissance` | le texte ou la décision n'était pas connu |
   | `recherche` | il existait mais n'a pas été trouvé |
   | `lecture` | il a été trouvé mais mal lu : condition, exception, date, portée |
   | `exercice` | la mécanique de la procédure a été mal comprise |
   | `strategie` | la voie, la cible, l'ordre ou le coup adverse ont été mal choisis ou mal prévus |
   | `posture` | concession, complaisance, revirement sans élément nouveau |
   | `controle` | le verrou est trop lâche ou trop strict |
   | `outillage` | hook, délai, format, environnement |

3. **Écrire la sonde qui échoue.** Elle reproduit le défaut dans la situation la plus petite possible, sans laisser deviner la réponse, avec des vérifications mécaniques. Elle se range dans `validation/banc/sondes/` avec son `origine` et sa `capacite`.
4. **Corriger à la couche de la cause.**
   - Une cause de `lecture` se corrige par une méthode de lecture et un contrôle de citation, pas par une règle de droit ajoutée à la main.
   - Une cause de `strategie` se corrige par une exigence de la séquence que le contrôle vérifie, pas par un paragraphe de plus.
5. **Vérifier.** La sonde passe, le banc entier ne régresse pas (`banc.py comparer`), L0 et L1 restent au vert.
6. **Consigner** dans `docs/CHANTIER.md` : la cause, la sonde, le correctif et le gain mesuré.

Un correctif sans sonde n'est pas livré. Une sonde qui passe sur la ligne de base ne mesure rien : elle se durcit ou se retire.

## 3. Mesure

Chaque passage du banc s'enregistre dans `validation/banc/resultats/` avec l'empreinte exacte du plugin. `TABLEAU.md` montre le taux de réussite par capacité et l'historique de chaque sonde. La ligne de base se mesure sur une copie figée du plugin (`banc_runs/plugin_base`) : elle ne bouge pas pendant les travaux. Un gain se rapporte sur les sondes qui ont été écrites avant le correctif. Les sondes écrites après sont rapportées à part.

## 4. Règles de rigueur

- Les sondes ne contiennent ni la réponse ni un indice de la réponse. Leur vérité vient d'un texte ou d'une décision lus à la source.
- Les sondes tirées d'une épreuve sont des sondes de régression. Elles ne mesurent pas la généralisation : seule une affaire neuve le fait.
- Aucune mesure ne se relance pour franchir un seuil. Une sonde instable se relance trois fois, et son taux est rapporté.
- Le banc tourne à l'aveugle : un hook borne la jurisprudence et les textes à la date de la sonde, et interdit la lecture de la validation et des épreuves.

## 5. Ce que le banc a appris (19 et 20 novembre)

1. **Une question posée de front ne mesure presque rien.** Le modèle sait répondre quand on lui pose la question décisive. Les défauts réels naissent quand il ne la pose pas lui-même au milieu d'un vrai travail. Les sondes utiles demandent donc un travail réel et vérifient que le point décisif en sort sans avoir été demandé.
2. **Les skills ne se chargent pas d'eux-mêmes.** Aucun agent n'a chargé spontanément le skill de doctrine. Celui des exercices ne pouvait pas l'être, faute d'en-tête valide (point 11). Le briefing de démarrage porte donc une table de routage, et c'est elle qui produit le gain : sur l'urgence vue du juge, la base réussit 0 passage sur 4, la version routée 3 sur 4.
3. **En mode non interactif, le hook UserPromptSubmit ne se déclenche pas.** Seuls le briefing de démarrage, les hooks d'outils et le contrôle agissent dans le banc. Un rappel placé seulement dans UserPromptSubmit n'y est pas mesuré.
4. **La variance compte.** Une sonde décisive se passe au moins trois fois sur chaque version, et l'on rapporte le taux. Les identifiants de passage sont uniques, pour que des passages simultanés ne se mélangent pas.
5. **Un contrôle mécanique vaut mieux qu'un rappel**, quand le défaut se laisse décrire. La compétence en premier ressort non lue, l'arrêt cité puis cassé, la citation introuvable et la voie adverse non recensée se bloquent. Ce qui relève du jugement se mesure au banc.
6. **Un contrôle qui ne voit que les fichiers laisse passer l'acte rendu ailleurs.** Prié de « répondre par la requête », l'agent l'écrit dans le chat ou dans son répertoire temporaire : aucun contrôle de `ecritures/` ne s'applique. Les contrôles décisifs portent donc aussi sur la réponse elle-même (hook de fin), et l'écriture d'un acte hors du dossier est refusée.
7. **Un échec se lit sur la réponse brute avant d'être compté.** Sur le premier banc complet, cinq des onze échecs de la base et quatre des huit échecs de la version finale venaient du banc : motif trop littéral pour une paraphrase exacte, ou acte demandé non lu par la vérification. Une vérification corrigée se rejoue sur tous les passages comparés, jamais sur un seul.
8. **Une source peut taire une partie d'elle-même.** La vue d'ensemble d'un décret modificatif, telle que LibreJustice la sert, annonce neuf articles et n'en affiche que trois : l'article qui crée la formalité nouvelle n'y figure pas. Le hook compare ce que la source annonce à ce qu'elle montre, et nomme les articles absents. Avant d'imputer un échec à l'agent, regarder ce que l'outil lui a réellement rendu.
9. **Un contrôle peut en faire taire un autre.** Une fin de tour ne se bloque qu'une fois : la relance arrive marquée et n'est plus contrôlée. Les contrôles de fin rendent donc leurs alertes ensemble. Un contrôle qui ne déclenche jamais sur le banc se vérifie en le rejouant sur les réponses brutes des passages où il aurait dû jouer.
10. **Le banc borne les outils, pas le savoir du plugin.** Un skill qui cite une décision postérieure à la date de coupe d'une sonde peut fausser sa mesure. Le remède n'est jamais de retirer le droit actuel du plugin : on mesure la capacité en cause sur une sonde postérieure à toute autorité que le plugin cite sur la question, et l'on garde une sonde de contrepoids dont la bonne réponse est inverse. Avant d'imputer un échec à cet anachronisme, vérifier que le skill a été chargé (point 12). Le hook d'aveugle refuse en outre toute décision postérieure à la coupe et arrête la chronologie de l'affaire à cette date.
11. **Un module qui ne se charge pas ne se mesure pas.** Le skill `mecanique-des-exercices` et l'agent `rapporteur-simule` avaient un en-tête YAML invalide (« : » dans une description non citée). Claude Code listait la commande mais ne proposait pas le skill au modèle : aucun agent ne l'a chargé de toute la journée, et le banc concluait à tort que le module n'apportait rien. Un test valide désormais tous les en-têtes. Avant de conclure qu'un module est sans effet, vérifier dans l'événement `init` d'une session du banc qu'il figure parmi les skills et les agents proposés, puis qu'il est chargé.
12. **Un aiguillage se contrôle.** La table de routage du briefing ne fait pas charger un skill à coup sûr. Sur l'urgence vue du juge, les deux pronostics faux de la v9 venaient de sessions qui n'avaient chargé aucun skill ; le seul juste, de la session qui avait chargé `refere-administratif`. La règle n'était pas en défaut, l'aiguillage l'était. Une réponse qui tranche un exercice sans avoir chargé son skill est renvoyée en fin de tour (`AIGUILLAGE` dans `hook.py`), et chaque exercice dont une sonde montre ce défaut y entre.
13. **Le coût se lit par poste, multiplié par le nombre d'appels qui le relisent.** Au banc complet de la v9, le socle de chaque session, c'est-à-dire les outils, les listes de skills et d'agents, la constitution et le briefing, faisait 59,5 ktok relus à chaque appel, soit 53 % du contexte consommé. Les outils natifs sans usage pour le contentieux en pesaient 17,7 k, désormais refusés par le gabarit du dossier (`.claude/settings.json`), et les descriptions des skills et des agents ont été réduites de moitié. Les sorties de LibreJustice ne pesaient que 15 % du contexte et les fiches d'exercice 2 % : elles ne viennent qu'après. Chaque réduction se mesure gratuitement par `/context`, puis sur un appel réel, avant d'être adoptée. Elle ne s'adopte que si la qualité se maintient au banc.
14. **Un contrôle de fin de tour impose une procédure, jamais un jugement.** De la v11 à la v17, sept correctifs agissaient en fin de tour ou par une règle du briefing : aucun n'a déplacé le pronostic au test apparié. Sur l'agent privé de tout traitement, la présomption d'urgence injectée en fin de tour a été lue, puis la réponse « non » maintenue : le modèle défend le jugement qu'il a déjà formé. Le savoir qui décide d'un jugement doit arriver avant lui, à la lecture de la pièce (`contrats_a_la_lecture`, v18). Les contrôles de fin gardent ce qu'ils savent faire : exiger une lecture, un fichier, une forme.
15. **On ne décide pas sur du bruit.** Avec dix à vingt sondes par famille et une réponse oui ou non, un écart de quelques points est indiscernable du hasard. Les sondes générées demandent une probabilité, notée par le score de Brier, et les versions se comparent sonde par sonde (`cycle.py`). Un correctif dont l'écart reste compatible avec le hasard n'est pas adopté, même s'il paraît meilleur.
16. **Une primitive se déduit des échecs, jamais d'une intuition.** `autopsie.py manques` confronte chaque pronostic raté au motif réel de la juridiction et range ce qui a manqué : mal pesé, public et trouvable, non public, appréciation. Seule la catégorie « public et trouvable » appelle une primitive d'acquisition. La jurisprudence de la formation, construite sur une intuition, n'a rien apporté. La décision attaquée, que les échecs désignaient, a payé.
17. **Un cycle se paie par paliers, plafond annoncé.** Les textes se diagnostiquent sur ce que le harness a déjà produit (`recit.py diagnostic`), sans session nouvelle. Les versions se comparent deux à deux, dans les deux ordres (`recit.py comparer`). Un vote qui change avec l'ordre ne départage pas : le juge suit la position. Seules quelques sessions confirment l'intégration, et le banc complet ne tourne qu'à la livraison. Un instrument qui tronque les textes fait naître des défauts qui n'existent pas, comme une « phrase coupée » à 3 500 caractères.
18. **On optimise ce qu'on mesure, et le reste dépérit.** Le banc est né des échecs passés en recherche et en procédure : toute la journée du 20 novembre a amélioré ces dimensions, pendant que la psychologie des décideurs, la sociologie des institutions, la négociation, la persuasion, la théorie de l'affaire et le récit, soit plus de 600 Ko de savoir, n'étaient ni chargés dans une seule session ni visés par une seule sonde. Rien ne le signalait. La couverture se vérifie désormais avant toute déclaration de version finale (`couverture.py`) : savoir, routage, contrôles, activation réelle et mesure, dimension par dimension. Une dimension qui ne peut pas être mesurée par oui ou non l'est par la grille du récit et la comparaison deux à deux (`recit.py`).
19. **Ce qu'on place devant l'agent doit être vrai à la source.** Le rappel des présomptions du référé renvoyait à l'ordonnance n° 467617, qui ne pose pas la présomption d'urgence : l'agent l'a lue, l'a écartée à bon droit et a demandé au juge simulé de ne pas la présumer (0/2). La source corrigée (n° 492519), le même rappel donne 2/2. La prose de la fiche était juste ; seul le bloc structuré, celui qu'un hook injecte, était faux. Tout bloc injecté se vérifie à la source comme une écriture, car son erreur se propage à chaque session. L'audit des 212 lignes injectées (21 novembre) en a trouvé 81 trompeuses ou inexactes : le banc ne les voyait pas, parce qu'une sonde n'éprouve qu'un point, et seule la lecture à la source les a révélées. Une ligne comprimée doit rester vraie lue seule, devant un rédacteur qui ne lira pas la fiche.
20. **Une analyse qui reste dans la fiche ne pèse pas.** Le négociateur relevait le coût d'un échec pour le GAEC et le retour de Mme X sous la même directrice, mais la lettre et la réponse les perdaient (une réussite sur deux). Ce qui a tenu : des titres fixes, dont « À reprendre dans la réponse », vérifiés dès l'écriture de la fiche. Le passage de l'analyse au texte se construit, il ne se suppose pas.
21. **Mesurer la base avant d'écrire.** Avant d'intégrer la suite Claude for Legal, la v33 a passé neuf sondes de droit du conseil : huit réussies, réformes de 2026 comprises, parce que le harness fait lire les sources. Le gain de l'intégration n'était donc pas dans le droit recopié mais dans les procédés que la base n'a pas : les positions du client (0,33 puis 1,00), les registres, la vérification de la contrepartie. Une couche nouvelle se justifie par l'échec qu'elle corrige au banc, non par l'étendue de ce qu'elle couvre.
22. **Mesurer la constance, pas seulement la réussite.** Une sonde passée une fois ne dit pas si elle passera la suivante. Trois essais sur huit sondes fragiles ont donné 22 réussites sur 24 et une constance de 6 sondes sur 8 ; la lecture des trois échecs a montré qu'un des trois venait de la correction, non de l'agent. Avant de corriger le harness sur un échec, lire la transcription : il faut savoir qui s'est trompé.
23. **Une sonde se juge au droit de sa date.** Le recours gracieux posté le dernier jour est un dossier daté du 6 juin 2023 : la date de réception décidait alors (CE, 21 mars 2003, n° 240511), et la date d'expédition ne fait foi que depuis CE, 30 juin 2025, n° 494573. Lu sans sa date, le critère de la sonde paraissait dépassé et un échec paraissait une bonne réponse ; corrigé, il a fait échouer les réponses justes en 2023. Avant de toucher à une sonde, lire son `horloge` et sa `coupe`, et vérifier la règle à cette date. Une réponse qui applique de mémoire une règle postérieure au dossier se trompe sur le dossier, même si elle a raison aujourd'hui.
24. **Une consigne qui interdit une forme peut faire taire le fond.** « Aucun pourcentage sans méthode défendable » a été lu comme une interdiction de dire l'issue : sur 17 réponses qui l'invoquent, 9 taisent l'issue la plus probable, et deux échecs en viennent. L'interdiction porte désormais sa limite (« mais l'issue la plus probable se dit toujours, en mots »). Une règle négative se relit avec la question : que fera l'agent qui l'applique à la lettre ?
25. **Un échec sur une décision réelle se confronte à cette décision.** Du 20 au 22 novembre, les pronostics de référé faux ont été
    classés « serrés » ou « propres à l'espèce » sans que personne lise ce que le juge avait réellement retenu. La lecture des
    motifs, le 22 novembre, a montré à chaque fois un point précis que le harness ne tenait pas : des récépissés qui ne renversent
    pas la présomption d'urgence d'un refus de renouvellement (CE, 18 févr. 2022, n° 457933), des allégations non contestées tenues
    pour établies à l'instruction close, la limite de la présomption de l'article L. 600-3 quand le jugement au fond est imminent
    (CJA, art. R. 311-6), le référé-liberté contre l'exécution d'une obligation de quitter le territoire après un changement de
    circonstances. Un échec qui se répète n'est jamais de la variance tant que les motifs du juge n'ont pas été lus.
26. **La règle tirée d'un échec s'établit sans la décision de la sonde.** Inscrire dans une fiche la décision que la sonde fait
    prédire ferait mesurer au banc la mémoire du harness, non son raisonnement. Chaque ligne nouvelle s'établit par d'autres
    sources, lues en entier, avec la meilleure autorité contraire ; `tests/test_integrite_banc.py` échoue si une décision prédite par
    une sonde apparaît dans ce que l'agent lit.
27. **Une correction se vérifie hors de l'échantillon qui l'a fait naître.** Le banc de l'anonymiseur l'a montré : 0,99 de rappel sur
    le générateur qui avait servi à le régler, 0,85 sur un jeu écrit ensuite et jamais corrigé. Une correction se mesure donc sur
    des cas neufs (décisions tirées par l'usine sur le même point, pièces écrites après coup), et le chiffre publié est celui-là.
28. **Un défaut corrigé entre au registre et n'en sort plus.** `validation/banc/defauts.json` garde, pour chaque classe de défaut
    corrigée, sa cause, son mécanisme et ses sondes (celle d'origine et ses variantes). `banc.py defauts` rejoue chaque sonde k fois
    et échoue si une classe perd un essai ; aucune version ne se fige sans ce passage. Le progrès devient cumulatif : une correction
    ne peut plus se défaire en silence par la correction suivante.
29. **Avant la règle, vérifier que le fait décisif était sous les yeux de l'agent.** L'usine ne remet que la procédure et les
    prétentions ; le juge décide souvent sur des faits qu'il lit dans les pièces et n'expose que dans ses motifs. Sur les cinq échecs
    des variantes du 22 novembre, aucun dossier remis ne contenait le fait décisif : ni les dates de dépôt et d'expiration du titre
    pour les trois refus de renouvellement, ni la grossesse de la compagne française et la reconnaissance anticipée, ni l'avis
    défavorable de la commission d'expulsion et la peine réduite en appel. L'agent qui conditionne alors son pronostic au fait
    manquant a bien raisonné ; la sonde mesure la chance, et l'échec se rapporte à part au lieu d'être corrigé par une ligne qui
    apprendrait au harness à deviner. La v44 l'a montré à ses dépens : elle tenait l'absence d'attestation de prolongation
    (CESEDA, art. R. 431-15-1) pour l'indice d'un dépôt tardif et le dépôt tardif pour une cause d'échec. Sur les deux premières
    sondes neuves, l'agent a conclu au rejet là où le juge avait accordé malgré un retard, et la recherche a montré des juges du
    fond partagés sur ce point. La règle de la v45 dit ce partage et fait du retard un argument de la défense à peser ; l'indice,
    qui ne distinguait pas les cas, est retiré.
30. **Une règle tirée de trois échecs de même sens se cherche aussi dans l'autre sens.** Les trois refus de renouvellement faux de
    la v43 étaient tous des rejets ; la recherche de la règle n'a d'abord porté que sur les décisions qui rejetaient. Avant
    d'inscrire une cause d'échec, chercher les décisions qui accordent malgré elle, et écrire la règle à la mesure de leur part.
31. **Couvrir une famille d'un coup, pas un échec à la fois.** Corriger échec par échec plafonne : chaque sonde ratée donne une
    ligne, et la suivante échoue sur un autre point. Le 22 novembre, quatre sous-agents ont miné en parallèle la jurisprudence
    publique de quatre familles (référé-suspension en droit des étrangers et hors étrangers, référé-liberté, pourvoi civil) :
    plusieurs centaines de décisions vues par famille, de 27 à 41 lues en entier, les motifs comptés de chaque côté et sourcés
    hors des épreuves. `validation/corpus_motifs/integrer.py` les verse dans les fiches sous trois gardes : un marqueur que le
    dossier doit montrer, un domaine dont il doit relever (`gardes.py` ; sans lui, la ligne des contrats d'agents publics se
    déclenchait sur 14 des 34 dossiers d'étrangers), une date d'entrée en vigueur. L'usine ne tire plus de sonde d'une décision
    citée par une fiche, si bien que les sondes fabriquées ensuite mesurent les lignes minées hors échantillon.
32. **Chercher les indices mal lus, puis vérifier s'ils viennent du banc.** `validation/banc/indices.py` croise chaque indice de
    procédure présent au dossier avec l'issue réelle et la justesse de l'agent. Le 22 novembre, il a montré qu'en requête en
    annulation la dispense de conclusions du rapporteur public figurait dans 32 dossiers, tous annulés, et que l'agent qui
    l'invoquait la lisait comme l'annonce d'un rejet. Le texte (CJA, art. R. 732-1-1) dit qu'elle tient à la matière ; la fiche
    le dit désormais, sans en faire un signe d'annulation, car l'inégalité venait aussi du tirage : l'usine cherchait chaque issue
    par une requête différente, et la requête des rejets ramenait surtout des ordonnances de tri. Une famille se tire désormais
    par une seule requête, la solution seule changeant (`COMMUNES` dans `usine.py`).
33. **Avant de juger une connaissance ajoutée, vérifier qu'elle atteint l'agent.** Le 22 novembre, 22 lignes minées pour la
    requête en annulation et 16 pour le pourvoi civil n'ont rien changé ; la cause n'était pas leur contenu. L'aiguillage ne
    reconnaissait pas l'exercice dans les réponses réelles (« le tribunal annulera », « la Cour cassera l'arrêt attaqué ») : le
    contrat n'a été injecté que dans 9 sessions sur 58 en annulation, et la cassation recevait souvent celui de l'appel civil.
    `indices.py` affiche désormais la part des sessions où le contrat ou la fiche est devant l'agent ; un test vérifie la
    reconnaissance sur des réponses rédigées comme l'agent les rédige ; à défaut de la réponse et de la demande, l'aiguillage
    reconnaît l'exercice dans le dossier lu.
34. **Le harness pilote l'agent ; il n'attend pas qu'il vienne chercher.** Profil des sessions du 22 novembre : sur une question
    de pronostic, l'agent lit le dossier et répond (2 appels d'outils en moyenne en référé, 1,3 en annulation) ; il a chargé le
    skill de l'exercice dans 5 sessions de référé sur 76 et 0 sur 58 en annulation, et n'a jamais ouvert la fiche, malgré la
    consigne de routage injectée au démarrage. La méthode des skills et la prose des fiches ne comptent donc que si un hook les
    pousse, au bon moment et sous une forme compacte. Deux conséquences : le contrat se donne à la première lecture du dossier,
    avant le jugement (v51), et le choix des outils se décide par le harness (recherche contradictoire quand l'issue est serrée)
    au lieu d'être laissé à l'agent.
35. **Le banc mesure le harness, pas la configuration du poste.** Les sondes tournaient sous le dépôt et avec les réglages de
    l'utilisateur : mémoire automatique du projet (avec des pointeurs vers un dossier privé), 99 skills dont la liste pesait
    65 000 signes, plugins sans rapport. Elles tournent désormais hors du dépôt (`~/.harness-banc/banc_runs`) avec
    `--setting-sources project,local` : 48 skills, 18 700 signes, aucune mémoire étrangère.
36. **La réponse se juge à la réponse finale.** Jusqu'au 23 novembre 2026, la vérification `message_commence` créditait une sonde
    dès qu'un message quelconque de la session commençait par la bonne issue : la session qui changeait d'avis après le hook Stop
    était comptée juste dans les deux sens. Sur 280 sondes neuves, v50 était notée 72,9 % pour 66,1 % en réponse finale ; sur ses
    512 sondes, 78,7 % pour 73,3 %. Le banc juge désormais le dernier message qui ouvre sur un verdict, et `comparer.py` comme
    `partiel.py` rejugent les anciens passages sur leur dossier de session. Le classement des versions passées n'en est pas changé.
37. **Une étiquette se lit dans le dispositif, pas dans un champ de la base.** En appel, le champ `solution` dit si l'appel
    réussit, non si la provision est allouée : 10 étiquettes fausses sur 40 dans la famille PROV, 5 sur 40 dans un second lot
    (dispositifs relus le 23 novembre). L'usine ne tire plus la provision que des ordonnances du tribunal dont le dispositif dit
    la même issue que le champ ; les sondes corrigées portent `etiquette_corrigee`, les ambiguës `etiquette_ambigue` et sortent
    des comparaisons.
38. **Le contexte des marqueurs est le dossier, pas le harness.** Les lectures de fiches et de skills entraient dans le texte où
    les marqueurs cherchent leurs déclencheurs : une fiche lue portait les mots de ses propres gardes, et toutes ses lignes
    marquées devenaient applicables (la garde « renouvel » s'ouvrait sur les 120 dossiers de séjour). `lectures_de_la_session`
    écarte désormais les fichiers du plugin et des skills, sauf pour le contrôle des citations.
39. **Lire la procédure visible avant le fond.** En référé administratif, le juge ne prononce une mesure qu'après avoir annoncé
    l'audience (CJA, art. L. 522-1) et peut rejeter sans audience une demande sans urgence ou manifestement mal fondée
    (art. L. 522-3). Dans les échantillons du 23 novembre, toutes les ordonnances rendues sans communication ni audience étaient
    des rejets, et la plupart des ordonnances rendues après audience accueillaient la demande. L'agent lisait le résumé des
    visas comme le dossier entier et jugeait « allégation générale, donc rejet ». Les lignes du tri et de l'audience tenue
    (référé-liberté, référé-suspension) disent ce que la procédure suivie révèle ; elles ne valent pas pour le référé « mesures
    utiles » (L. 521-3), que l'audience obligatoire ne concerne pas.
40. **Vérifier l'aiguillage sur chaque famille, pas en moyenne.** Le contrat remis à la première lecture n'atteignait le référé-provision
    que dans 6 dossiers sur 40 : la demande dit « la provision demandée », aucun marqueur ne le reconnaissait, et 9 dossiers recevaient
    le contrat d'un autre exercice, qui bloquait ensuite le bon. Les autres familles étaient reconnues partout. Un contrôle par famille
    (`reconnaitre_exercice` sur la consigne et le dossier) se fait avant toute mesure d'une ligne nouvelle.
41. **Une expression régulière écrite dans du JSON double ses barres obliques inverses.** « \bbail\b » écrit tel quel devient un
    retour arrière, et la garde ne joue jamais : cinq gardes étaient inertes (bail, RSA). Un test refuse désormais tout caractère de
    contrôle dans les données des fiches.
42. **Séparer ce que la décision rendue révèle de ce que le jugement apporte.** Les visas d'une ordonnance disent si une audience
    a eu lieu ; sans audience, une suspension ou une mesure de référé-liberté n'a pas pu être prononcée (CJA, art. L. 522-1). Cette
    lecture est exacte, mais l'indice n'existe qu'après la décision. Les gains se rapportent donc à part : dossiers jugés après
    audience (jugement au fond) et ordonnances de tri (lecture de la procédure).
