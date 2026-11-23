---
name: theorie-de-l-affaire
description: "Vérité sur pièces et théorie qui gouverne la séquence : hypothèses éprouvées, récit, qualification, question au juge, faits défavorables traités. Après l'analyse documentaire, avant séquence, ligne et écriture, et après chaque pièce ou décision."
---

# Théorie de l'affaire

Une affaire se gagne sur une version des faits que le juge peut tenir pour vraie. Cette version appelle une qualification, la qualification appelle une règle et la règle un remède. La théorie de l'affaire est cette chaîne. Elle s'établit une fois pour toute la séquence et chaque écriture en est une projection, adaptée au juge et au stade (skill `recit-judiciaire`). Elle se construit depuis les pièces. Le récit du client n'est qu'une hypothèse parmi d'autres.

Deux questions restent séparées du début à la fin. La première est de savoir si la théorie est vraie sur pièces. La seconde est de savoir si le juge la croira. Un récit cohérent se fait croire mais ne prouve rien, et des juges prennent à tort la cohérence pour un indice de vérité (voir `strategie-contentieuse/references/decideurs.md`, idée fausse n° 17). La théorie doit d'abord être vraie, ensuite seulement persuasive. Les fondements et leur statut de lecture sont dans `references/sources.md`.

## 1. Séparer le récit du client et le dossier

Le récit du client s'écrit comme hypothèse, chaque affirmation marquée « alléguée ». Ce qui lui manque se demande sous forme de pièces, pas de récit supplémentaire. Aucune lacune ne se comble par une inférence plausible non signalée : une inférence est permise, mais elle porte le nom d'inférence et la pièce qui la fonde.

## 2. Partir de la base factuelle

La base est la matrice des preuves tenue par l'analyse documentaire (skill `analyse-documentaire`, fiches `pieces/analyses/`). Chaque fait y renvoie à une pièce, à un extrait littéral et à un statut : prouvé, corroboré, allégué, contesté ou contredit. On y relève aussi ce que l'adversaire détient sans l'avoir produit, et ce qui manque au dossier. Une théorie écrite avant l'analyse des pièces est un brouillon : le contrôle la tient pour périmée dès qu'une pièce ou une fiche d'analyse lui est postérieure.

## 3. Générer les hypothèses concurrentes avant d'en évaluer aucune

Au moins les hypothèses suivantes, écrites chacune dans sa meilleure version :

- **la nôtre** ;
- **la meilleure hypothèse de l'adversaire**, telle que son conseil la bâtirait sur les mêmes pièces ; un épouvantail ne vaut rien, puisque c'est la meilleure version qui sera plaidée. Cette hypothèse inclut l'autre qualification qu'il pourrait donner aux mêmes faits si la sienne échoue, par exemple l'insuffisance professionnelle au lieu de la faute ;
- **la lecture par défaut du juge** : la catégorie banale où un juge chargé range spontanément ce type d'affaire à la première lecture, et l'issue habituelle de cette catégorie dans sa juridiction (profil `juridiction.py`, profil du décideur) ;
- **toute autre hypothèse qui rend compte des pièces**, y compris que le client se trompe, ou que l'adversaire a agi régulièrement pour des raisons que le dossier ne montre pas encore.

On génère d'abord, on évalue ensuite. Une hypothèse non prouvée reste ouverte tant qu'aucune pièce ne la contredit : l'écarter trop tôt revient à cesser de chercher ce qui la soutiendrait, et c'est souvent celle que l'adversaire plaidera.

## 4. Éprouver chaque hypothèse contre chaque pièce

Matrice : les hypothèses en colonnes, les pièces et leurs extraits en lignes. Chaque case porte compatible, incompatible ou neutre.

- **Pièce diagnostique.** Elle ne s'accorde pas de la même façon avec toutes les hypothèses. Une pièce compatible avec toutes ne départage rien, si nombreuses et frappantes que soient les pièces de ce genre. Les pièces diagnostiques décident de l'affaire et prennent la première place dans les écritures.
- **Réfuter plutôt que confirmer.** On garde l'hypothèse que le moins de pièces contredisent, et non celle que le plus de pièces soutiennent.
- **Pièce incompatible avec notre hypothèse.** Elle s'explique par sa fiche d'analyse (auteur, date, portée, authenticité, contexte), ou bien la théorie change. Aucune théorie ne peut exiger d'ignorer une pièce : l'adversaire la produira.

## 5. Sensibilité et point de rupture

Nommer la ou les deux pièces qui portent toute la théorie. Examiner ce qu'il advient si elles sont fausses, contestées, écartées pour déloyauté, tardiveté ou inopposabilité, ou lues autrement. Nommer la pièce ou le fait qui la détruirait, qui la détient, et la parade : production forcée, contre-preuve, action de terrain, autre qualification. Une théorie qui tient à une seule pièce fragile se renforce avant d'être plaidée.

## 6. Traiter chaque fait défavorable sans le concéder

Recenser chaque fait défavorable, prouvé ou que l'adversaire peut prouver. Chacun reçoit l'un de quatre traitements :

- **intégration** : le fait appartient à notre récit et, replacé dans la suite des événements, signifie autre chose que ce qu'en dit l'adversaire ;
- **dépassement** : un fait postérieur ou une règle supérieure le prive d'effet ;
- **indifférence** : il porte sur une question que le juge n'a pas à trancher, telle que nous posons la question ;
- **retournement** : il révèle une contradiction, un silence ou une faute de l'adversaire.

Un fait qui n'admet aucun de ces traitements montre que la théorie est fausse ou que la question est mal posée. On revient alors à l'étape 3 ou à l'étape 9. Dans l'écriture, le traitement se place là où le fait survient dans le récit, sous notre éclairage et avant que l'adversaire ne le produise. Il ne figure pas dans un paragraphe de réponse aux objections, qui annoncerait une faiblesse.

## 7. Compléter la chaîne

Du fait au remède, chaque maillon doit être établi : fait générateur, faute ou illégalité, préjudice ou atteinte, lien de causalité, urgence ou intérêt selon la voie. La facilité avec laquelle le décideur construit un récit complet déplace sa décision (Pennington et Hastie 1992, `references/sources.md`). Un maillon manquant devient une action de terrain ou une demande de pièce datée (skill `action-sur-le-reel`). D'ici là, la théorie reste provisoire et aucune écriture ne présente ce maillon comme établi.

## 8. Choisir la qualification juridique

Les mêmes faits admettent souvent plusieurs qualifications. Pour chacune, établir :
- les pièces qui en prouvent chaque élément ;
- le régime qui en découle : charge de la preuve, intensité du contrôle du juge, remèdes possibles, délai, juge compétent ;
- la manière dont les juges la reçoivent d'ordinaire. Certaines qualifications, comme le détournement de pouvoir, la mauvaise foi ou la fraude, sont rarement retenues et colorent tout le dossier : on ne les avance qu'avec la preuve.

Retenir la qualification qui réunit quatre traits : les pièces la prouvent, elle ouvre le régime le plus favorable, le juge peut l'adopter sans innover, et elle ne contredit aucune autre voie de la séquence. Les qualifications écartées sont consignées avec leur raison.

## 9. Poser la question

Écrire en une phrase la question que le juge doit trancher, posée de façon que notre réponse découle des pièces. Le combat porte d'abord sur la question. L'adversaire proposera une question d'appréciation, sur laquelle le juge s'efface devant l'auteur de l'acte. Il faut la déplacer vers une question de droit ou de fait matériel, sur laquelle le juge exerce un contrôle entier. Si la seule question qui donne raison au client est une question d'appréciation sous contrôle restreint, la théorie doit le dire, et la séquence doit chercher une autre cible ou un autre juge.

## 10. Thème et sûreté de la décision

Le thème est une phrase qui donne au juge une raison de vouloir statuer dans notre sens. Il s'appuie sur une valeur que le droit protège déjà : sécurité juridique, égalité, loyauté, droits de la défense, proportionnalité, parole donnée. Jamais sur l'indignation.

La sûreté explique pourquoi statuer pour nous n'expose pas le juge : l'adversaire garde ce qui lui revient, la mesure est limitée ou réversible, la solution ne crée pas de précédent inquiétant et s'inscrit dans une jurisprudence existante.

## 11. Épreuves

Elles s'écrivent dans `epreuves`, chacune avec ce qui a été vérifié :

- **couverture** : chaque fait de la chronologie, prouvé ou contesté, est placé dans le récit ou montré étranger à la question ;
- **cohérence** : aucune contradiction interne, rien qui heurte l'expérience ordinaire du juge ;
- **complétude** : aucun maillon manquant présenté comme établi ;
- **unicité** : l'hypothèse de l'adversaire et la lecture par défaut sont chacune contredites par au moins une pièce diagnostique nommée ;
- **stabilité** : la même théorie sert toutes les voies de la séquence et s'accorde avec tout ce que le client a déjà écrit ou déclaré (lettres, recours, plaintes, messages publics), lu à cette fin ; une contradiction d'un forum à l'autre sert l'adversaire ;
- **vérité** : aucun élément du récit ne repose sur une inférence non signalée ;
- **contradiction** : le sous-agent `avocat-adverse` reçoit les pièces, sans notre théorie, et écrit la sienne, avec la liste de ses arguments (`strategie/theorie_adverse.json`). Chaque argument reçoit une réponse dans `reponses_theorie_adverse` : l'un des quatre traitements, avec son appui (pièce ou source) quand l'adversaire le juge décisif, ou bien `decisif_pour_la_voie` avec les voies que la séquence retire ou refonde (`voies_modifiees`). L'épreuve porte sur les arguments et pas seulement sur les pièces : quand le dossier compte peu de pièces, c'est par ses arguments de droit et d'appréciation que l'adversaire gagne. Deux pièges :
  - une crainte que l'adversaire exprime n'est pas un aveu, puisqu'il l'écrit pour s'y préparer ;
  - quand le même intérêt est invoqué des deux côtés (celui d'un enfant, la sécurité, la santé publique), il faut se demander à qui le juge l'attribuera. Un juge du provisoire l'attribue d'ordinaire à la mesure qui protège, sauf preuve contraire précise.

## 12. Ce que la théorie commande

La preuve à créer et les pièces à demander ; la cible et l'ordre des coups (skill `conduite-de-la-sequence`) ; la théorie du cas de chaque écriture, dont la fiche de récit note la date de la théorie qu'elle projette (`theorie_date` dans `ecritures/controle/<nom>.recit.json`) ; le plan de négociation, puisque c'est elle qui fait voir son risque à l'adversaire ; ce que le client dit et écrit.

## 13. Révision

Après chaque pièce, défense ou décision nouvelle, la théorie est relue, redatée et, s'il le faut, changée. L'ancienne version est archivée sous `strategie/theorie_<date>.json` et la raison du changement est portée au journal stratégique. Un changement n'est jamais silencieux.

## Sortie

`strategie/theorie.json` :

- `date` (AAAA-MM-JJTHH:MM, lue sur le poste) ;
- `recit_du_client` ;
- `hypotheses` : liste d'objets `id`, `porteur` (nous, adversaire, lecture_par_defaut, autre), `enonce`, `pieces_compatibles`, `pieces_incompatibles` (objets `piece`, `extrait`, `explication`), `statut` (retenue, ecartee, ouverte), `raison` ;
- `pieces_diagnostiques` : objets `piece`, `extrait`, `departage` ;
- `theorie_retenue` : `hypothese`, `recit`, `qualification`, `qualifications_ecartees`, `question`, `theme`, `surete` ;
- `faits_defavorables` : objets `fait`, `pieces`, `traitement` (integration, depassement, indifference, retournement), `explication` ;
- `reponses_theorie_adverse` : un objet par argument de `strategie/theorie_adverse.json`, avec `argument` (son identifiant), `traitement` (l'un des quatre, ou decisif_pour_la_voie), `explication`, `appui` (pièces ou sources) et, pour un argument décisif, `voies_modifiees` ;
- `maillons_manquants` : objets `maillon`, `action` ;
- `point_de_rupture` : `piece_ou_fait`, `detenu_par`, `parade` ;
- `epreuves` : `couverture`, `coherence`, `completude`, `unicite`, `stabilite`, `verite`, `contradiction` ;
- `lu` : ce qui a été lu en entier, en partie, pas du tout.

Le contrôle avant dépôt refuse une écriture juridictionnelle dans huit cas :
- la théorie manque ;
- elle est antérieure à la dernière pièce ou à la dernière fiche d'analyse ;
- elle compte moins de trois hypothèses, ou omet celle de l'adversaire ou la lecture par défaut ;
- l'hypothèse retenue garde une pièce incompatible sans explication ;
- un fait défavorable n'a pas de traitement admis ;
- un argument de la théorie adverse reste sans réponse, ou un argument que l'adversaire juge décisif n'est écarté par aucune pièce ni aucune source ;
- une épreuve n'est pas écrite ;
- la fiche de récit de l'écriture projette une autre version de la théorie.
