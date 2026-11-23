---
name: contrats-d-affaires
description: "Contrats d'affaires en droit français : tri d'un accord de confidentialité, revue d'un contrat de fournisseur, de client, de services ou SaaS au regard des positions du client, contre-propositions de l'autre partie, historique des avenants, échéancier des renouvellements, circuit de validation, note aux opérationnels, vérification de la contrepartie. Dès qu'un contrat se relit, se négocie, se signe ou se renouvelle."
---

# Contrats d'affaires

Le pôle reprend les procédés du plugin commercial de la suite Claude for Legal (`docs/conseil/correspondance_contrats-d-affaires.md`) et les applique au droit français. Il ne recopie pas le droit : il dit quoi lire, dans quel ordre, et comment le livrer. Toute règle employée se lit à la source, sur LibreJustice, à la date du jour, et se cite avec son article ou sa décision.

## 1. Avant toute revue

1. **Les positions du client.** Lire `cabinet/positions/contrats-d-affaires.md` du dossier de travail, sinon `~/.harness-juridique/positions/contrats-d-affaires.md`, et le profil (`profil.md` : qui signe, jusqu'à quel montant, qui valide une dérogation). À défaut, appliquer les positions par défaut de `references/positions.md`, les annoncer dans le livrable avec leur fondement, et proposer en fin de livrable de les enregistrer (skill `profil-et-positions`). Le travail n'attend pas le profil.
2. **Le côté.** Le client vend (son modèle, en général) ou achète (le modèle de l'autre partie, en général). Toute position se lit du côté du client ; une position de vendeur n'est jamais appliquée à un achat.
3. **La contrepartie.** `python "${CLAUDE_PLUGIN_ROOT}/scripts/registres_publics.py" fiche <SIREN ou dénomination>` : existence, forme, siège, dirigeants qui peuvent signer, comptes publiés, et toute annonce du BODACC de procédure collective, de radiation ou de cession. Une procédure collective ouverte change tout (qui a qualité pour contracter, sort du contrat en cours, déclaration de créance) et se dit en tête du livrable. N'interroger que des personnes morales ou des entrepreneurs tiers, jamais un client personne physique.
4. **L'orientation.** Une lecture rapide pour dresser le tableau : nature du contrat, côté du client, contrepartie et son poids, valeur (si le contrat-cadre ne la donne pas, la demander avant d'appliquer un seuil de validation), durée et reconduction, droit applicable et juridiction, accord de traitement des données joint, renvoyé à une adresse ou absent (un accord renvoyé et non lu se dit tel, et se revoit avec le pôle `donnees-personnelles`).
5. **Le contrôle de portée.** Un document intitulé « accord de confidentialité » qui contient une exclusivité, une non-concurrence, une non-sollicitation, une licence, une cession de propriété intellectuelle, un droit de préférence, une clause de la nation la plus favorisée ou une clause de juridiction qui dépasse la confidentialité n'est plus un simple accord de confidentialité : il passe en revue complète, ORANGE au moins.

## 2. Les procédés

### 2.1 Tri d'un accord de confidentialité

Grille VERT, ORANGE, ROUGE appliquée aux positions :
- VERT : toutes les positions respectées, rien que la loi interdise ; s'envoie à la signature selon le circuit du profil. Un VERT sur des positions par défaut se dit tel.
- ORANGE : un ou deux points précis à trancher par la personne que désigne le profil, ou un point que les positions ne couvrent pas.
- ROUGE : un point que la loi interdit ou prive d'effet, ou un point de la liste « jamais » du client. On ne signe pas, on propose.

Points à vérifier, chacun lu à la source quand il sert : réciprocité (un accord unilatéral se justifie quand une seule partie divulgue) ; définition des informations et exigence de marquage ; exceptions usuelles (information publique, déjà connue, développée indépendamment, reçue d'un tiers, divulgation imposée par la loi ou le juge) ; usage des informations retenues en mémoire ; durée et survie, au regard de l'interdiction des engagements perpétuels (C. civ., art. 1210) ; clause pénale et pouvoir de modération du juge (art. 1231-5) ; restrictions annexes ; retour et destruction, avec l'exception des sauvegardes ; loi applicable et juridiction (CPC, art. 48 entre commerçants ; règlements Rome I et Bruxelles I bis) ; secret des affaires (C. com., art. L. 151-1 et suivants) comme protection qui existe sans l'accord.

### 2.2 Revue d'un contrat de fournisseur, de client, de services ou SaaS

1. **Le point rédhibitoire** du profil d'abord. S'il est présent, il ouvre le livrable : proposer la contre-clause, ou ne pas signer.
2. **La comparaison clause par clause** avec chaque position : la position, la clause citée exactement, l'écart (manquante, plus faible que la position, hors de la position de repli, structure inhabituelle, inacceptable), la gravité (bloquant, élevé, moyen, faible), l'effet concret pour le client en une ou deux phrases, la contre-proposition prête à coller, et la position de repli ou la personne à saisir.
3. **La limitation de responsabilité en quatre dimensions**, jamais en une ligne : ce qui est plafonné (dommages directs, indirects, tout) ; l'assiette du plafond, citée mot pour mot (sommes payées sur douze mois, sur la commande en cours, depuis l'origine) ; ce qui échappe au plafond et si le reste plafonné a encore un sens ; la position du client pour chaque dimension. Lire à la source la règle de l'obligation essentielle (C. civ., art. 1170) et le sort des limitations en cas de faute lourde ou dolosive (art. 1231-3 et jurisprudence).
4. **Les clauses propres aux services et au SaaS** : reconduction et résiliation (registre des échéances), révision du prix et indexation (C. mon. fin., art. L. 112-1 et L. 112-2, à lire), niveaux de service et leur sanction, réversibilité et restitution des données en format exploitable, sous-traitants ultérieurs (RGPD, art. 28, § 2), évolution ou suppression des fonctions, droits du prestataire sur les données du client et usage pour entraîner des modèles (pôle `intelligence-artificielle`).
5. **Le droit des relations commerciales** quand il joue : déséquilibre significatif, avantage sans contrepartie, rupture brutale d'une relation établie et préavis écrit (C. com., art. L. 442-1, version en vigueur) ; délais de paiement, pénalités et indemnité forfaitaire (art. L. 441-10) ; contrat d'adhésion et clause abusive (C. civ., art. 1110 et 1171) ; imprévision (art. 1195) et force majeure (art. 1218), selon ce que le contrat aménage.
6. **L'écart de droit applicable.** Une position pensée pour le droit français ne vaut pas sous une autre loi : quand la loi du contrat est étrangère, le dire et marquer ce qui doit être vérifié dans ce droit.
7. **Ce qui joue pour le client et ce qui manque**, en deux courtes listes.
8. **Le circuit de validation** : qui valide quoi d'après le profil, et la demande rédigée pour cette personne.

### 2.3 Contre-propositions de l'autre partie

Sur une version révisée par l'autre partie : chaque modification lue contre la position et contre la version précédente ; acceptée, refusée avec la contre-proposition, ou acceptée contre une contrepartie nommée. Aucune concession sans contrepartie (`negociation-et-persuasion`). Une modification glissée hors des révisions suivies se signale.

### 2.4 Historique des avenants

Ordonner le contrat initial et chaque avenant par date de signature ; pour chaque avenant, ce qui change, article par article, cité ; puis l'état net en vigueur et les points à surveiller. Sur une clause, retracer sa rédaction d'origine, chaque modification et le texte qui gouverne aujourd'hui. Une incohérence entre avenants se tranche par leurs clauses de hiérarchie, ou se signale.

### 2.5 Échéancier des renouvellements

Inscrire chaque contrat au registre `contrats` (`python "${CLAUDE_PLUGIN_ROOT}/scripts/echeancier.py" squelette contrats`) : date d'effet, durée initiale, reconduction (tacite, expresse, aucune), durée de reconduction, préavis et sa forme. `echeancier.py rapport` calcule le terme en cours et la date limite de dénonciation. La tacite reconduction produit les effets du renouvellement (C. civ., art. 1215), qui donne naissance à un nouveau contrat de contenu identique mais à durée indéterminée (art. 1214), sauf stipulation qui fixe la durée de la période reconduite ; envers un consommateur ou un non-professionnel, l'information sur la reconduction est réglementée (C. conso., art. L. 215-1 et suivants, à lire). Quand la date limite tombe un samedi, un dimanche ou un jour férié, ne pas reporter : préparer l'envoi pour le dernier jour ouvré qui précède, sauf stipulation contraire. Accepter ou refuser un renouvellement est une décision du client : le livrable la prépare.

### 2.6 Circuit de validation

Qualifier le point (nature, montant, gravité), le confronter à la matrice du profil, nommer la personne qui valide, rédiger la demande (le point, la clause, le risque, la recommandation, la décision attendue, la date), et l'inscrire au journal des écarts si elle est accordée (`registres/ecarts.json`). Dans le doute, saisir avec une note.

### 2.7 Note aux opérationnels

Pour celui qui n'est pas juriste : ce qu'il peut faire, ce qu'il ne doit pas faire, ce qui reste ouvert et qui le tranche, en langage courant, sans longue citation de clause ni analyse interne. Avant d'envoyer hors de l'équipe juridique, le contrôle de destination (section 4).

### 2.8 Retour sur les écarts signés

Chaque signature qui s'écarte d'une position s'inscrit au journal des écarts ; le sous-agent `veilleur` les compte et propose de réviser une position quand le même écart revient. Le client décide.

## 3. Le livrable

En tête, la conclusion : signer, signer après les modifications listées, ou ne pas signer ; la contrepartie et toute alerte du BODACC ; les positions appliquées (du client ou par défaut). Puis les points par gravité, chacun avec sa contre-proposition. Les contre-propositions se font à la plus petite échelle qui atteint la position : un mot avant une expression, une expression avant une phrase, une phrase avant une clause ; une clause n'est remplacée en entier que lorsque les retouches seraient plus difficiles à lire, et l'envoi le dit. Un accord propre reçoit une conclusion courte. La fin dit les décisions qui reviennent au client et la suite proposée.

## 4. Garde-fous

- Contrôle de destination : `docs/CONSEIL.md`, section 5. Seules les consultations et correspondances de l'avocat sont couvertes par le secret professionnel ; celles du juriste d'entreprise ne le seront qu'à compter du 1er janvier 2027 et aux conditions de l'article 58-1 de la loi n° 71-1130. Une analyse destinée à l'autre partie se réécrit : elle ne laisse voir ni marge, ni position de repli, ni faiblesse.
- Aucune signature, aucun envoi, aucune dénonciation sans décision du client.
- Aucune donnée du client dans une requête publique.
