---
name: lecture-des-decideurs
description: "Profil du décideur et de l'institution adverse (droit, statistiques, décisions publiées) et choix de forum, moment, structure, ton, preuve et demande ; produit strategie/decideurs.json. Avant tout acte juridictionnel et toute démarche décisive."
---

# Lecture des décideurs

Un acte se gagne devant un décideur précis, qui contrôle avec une intensité donnée, trie selon une pratique observable et statue sur ce qu'on lui apporte ; il se négocie contre une organisation où quelqu'un instruit, quelqu'un signe, quelqu'un paie et chacun craint quelque chose. Ce skill transforme ce savoir en fichier d'état vérifiable et en choix datés. Les sources et leur solidité sont dans `references/` :

- `psychologie-decision.md` : récit, cohérence, ancrage, cadrage, taux de base, raisonnement motivé, charge, première impression, réplications ;
- `sociologie-juridictions.md` : juge administratif et rapporteur public, tri des référés, standards de contrôle, juge judiciaire, Cour de cassation, Cour européenne, QPC, interdiction du profilage des magistrats ;
- `institutions-adverses.md` : qui décide, contraintes juridiques, budgétaires et réputationnelles, défense de l'adversaire, saisines extérieures et leur effet mesuré.

Chaque règle y porte son statut. Pour le magistrat français, une règle psychologique est une inférence, sauf les points mesurés en France que `psychologie-decision.md` énumère.

## 1. Quand

Avant le premier acte juridictionnel, avant tout changement de forum ou de voie, après toute décision rendue dans l'affaire, et dès que le profil a plus de 180 jours. Le profil précède la ligne (`strategie/ligne.json`) : une ligne écrite avant lui doit être relue, puis redatée ou porter `profil_decideurs_applique`.

## 2. Le décideur juridictionnel

Pour chaque étape de la séquence (`strategie/sequence.json`), nommer la juridiction, la formation qui statuera réellement (juge des référés statuant seul, président de chambre par ordonnance, formation collégiale, juge unique, chambre de la Cour de cassation et son circuit, juge unique de la Cour européenne), le stade, la procédure et la matière. Puis établir, sur sources publiques lues :

1. **Le standard de contrôle** de la matière, lu dans la décision de principe : entier, normal, restreint, appréciation souveraine, bilan, évidence du référé, droit seul en cassation. Il fixe la preuve utile, les moyens opérants et la demande que ce juge peut accorder (`sociologie-juridictions.md`, tableau des standards). Quand l'acte attaqué repose sur plusieurs motifs soumis à des contrôles différents, chacun se traite.
2. **Le taux de base** de la classe de référence la plus étroite qui soit mesurée : statistique officielle de l'étape (rapport public, références statistiques de la justice, statistiques de la Cour européenne) ou décisions publiées de la même formation, dans la même procédure et la même matière, relevées par `juridiction.py calibrage` avec une borne de date. Cette sortie se vérifie avant usage : une requête textuelle ramène des référés d'autres sortes, d'autres matières, d'autres autorités et des jugements au fond, et la base ouverte publie une partie des ordonnances de référé sous le type « Décision » ; la classe se reconstruit décision par décision (procédure visée, stade, auteur et nature de l'acte attaqué) et sa règle s'écrit dans le périmètre. Écrire le numérateur, le dénominateur, le périmètre, la période et ce que le dénominateur exclut (non-lieux, désistements, ordonnances de tri absentes de la base, décisions non publiées). Un taux décrit une classe de décisions ; il ne se convertit jamais en chance du dossier, et la jurisprudence choisie pour sa publication au recueil n'en donne aucun. S'il n'existe aucune série, `taux_de_base_absent` dit ce qui a été cherché.
3. **Ce qui passe et ce qui échoue** devant cette formation, tirés de ses décisions publiées, en nombre comparable des deux côtés : motif décisif des refus (urgence, doute sérieux, irrecevabilité, tri), circonstances des accueils. Si aucune décision accueillie n'existe dans la classe, le dire, chercher la classe voisine la plus proche (même juge, autre matière ; même matière, juridiction voisine) et l'indiquer comme telle.
4. **La culture et la charge** de la formation : qui lit en premier (au tri, un juriste qui prépare le projet d'ordonnance), ce que la formation fait des faits (stabilisés au premier mémoire), le rôle du rapporteur public et le sens communiqué, la part des décisions sans formation collégiale, les délais publiés.

Interdit absolu : aucun profil d'un magistrat nommé, aucun taux par juge, aucune recherche par nom de juge, de rapporteur public ou de greffier. La réutilisation de leur identité pour évaluer, analyser, comparer ou prédire leurs pratiques est un délit (CJA, art. L. 10 ; COJ, art. L. 111-13 ; peines de l'article 226-18 du code pénal). Le profil vise la juridiction, la formation et la matière ; la variabilité entre juges se traite comme une marge anonyme. Une décision se cite par sa juridiction, sa date et son numéro.

## 3. Le décideur non juridictionnel

Autorité administrative, autorité indépendante, médiateur, parquet : la règle qui fixe sa compétence et son délai, ce qu'il peut décider ou recommander, la suite effective de ses actes quand elle est publiée (taux de suivi, taux d'accord et ce qu'ils mesurent vraiment), ce qui fonde ses refus dans ses décisions ou avis publiés.

## 4. L'institution adverse

Pour une organisation (personne publique, organisme chargé d'un service public, entreprise, association, parquet) :

1. **Qui décide.** Signataire, instructeur, valideur, organe délibérant, payeur, assureur, tutelle, représentant en justice : chacun par sa fonction et son fondement (bloc de signature, arrêtés de délégation et de subdélégation du recueil des actes administratifs, datés au regard de la décision ; délibération de délégation au maire et seuils de transaction ; statuts ; contrat d'assurance). La personne qui contrôle l'information utile au dossier n'est pas toujours le signataire. Le dossier d'instruction devient communicable une fois la décision prise.
2. **Ses contraintes.** Juridiques (interdiction des libéralités et son contrôle par le juge de l'homologation, prescription quadriennale qui ne se transige pas, retrait limité à quatre mois, responsabilité financière des gestionnaires), budgétaires (provision pour litige, crédits du programme, mandatement), réputationnelles (une fonction centrale où la réputation est fragile réagit, une accusation d'excès appelle la négation), hiérarchiques et politiques, de calendrier (séances du conseil, visa du contrôle financier).
3. **Comment elle se défend.** Service juridique ou avocat, préfecture qui se défend seule, absence fréquente de mémoire en défense et acquiescement aux faits après mise en demeure (CJA, art. R. 612-6), assureur qui dirige le procès. Lire ses mémoires publiés quand ils sont visés dans les décisions.
4. **Ce qu'elle peut accorder sans perdre la face.** Une solution que porte un tiers (juge, médiateur, recommandation en équité du Défenseur des droits, avis d'une autorité), une règle qui la couvre, un élément nouveau qui n'était pas au dossier, un montant rattaché à une responsabilité établie et homologable.
5. **Les saisines extérieures**, avec leur effet documenté et non supposé : déféré du créancier impayé au parquet de la Cour des comptes, Défenseur des droits, médiateur sectoriel, médiation préalable obligatoire (un accord y signifie souvent une décision expliquée et inchangée), CADA, élu, presse. Chacune est retenue ou écartée avec sa raison.
6. **L'aversion au précédent** : aucune mesure française ; une hypothèse à manier comme telle.

Pour une personne physique, seul son comportement procédural établi par pièces (délais, silences, constance de ses écrits) entre au profil. Aucun portrait psychologique, aucun élément de vie privée, pour personne.

## 5. Des constats aux choix

Chaque constat devient un levier ou un risque, avec sa cible, son statut et ses sources. Puis six choix, chacun rattaché aux leviers et risques qui le fondent :

- **Forum.** Entre les voies ouvertes à la même étape, comparer le standard de contrôle, le taux de base et la formation ; préférer le juge qui contrôle entièrement le motif décisif, la voie où la condition décisive est la plus démontrable, et, côté administration, le niveau qui a le pouvoir d'accorder ce qui est demandé (droit au service, arrangement au niveau qui arbitre). Jamais d'après la personne d'un juge.
- **Moment.** Le premier acte de fond contient le récit complet et les pièces décisives ; la formation se fait une opinion à la lecture, avant toute décision. Agir avant que la position ne se fige (sens des conclusions, projet d'ordonnance), au moment où l'institution peut décider (séance, exercice budgétaire, délai de retrait), et interrompre ce qui court (prescription, délai de recours, confirmation du maintien de la requête après un rejet de suspension pour défaut de doute sérieux, CJA, art. R. 612-5-2).
- **Structure.** Ce que lit le premier lecteur décide de la suite : la condition qui fait le plus souvent échouer cette formation se démontre en tête, pièce à l'appui ; la pièce la plus forte de l'adversaire est combattue la première ; chaque motif de l'acte attaqué est traité selon son standard.
- **Ton.** Sobre, sans intensifs. Vers l'administration, la demande se présente comme l'application d'une règle, qui permet de céder, plutôt que comme un appel à l'indulgence, qui expose celui qui cède. Quand la qualification le permet, l'atteinte se décrit comme la perte d'une situation acquise.
- **Preuve.** Celle que le standard rend utile (faits extérieurs à l'appréciation d'un jury, dossier présenté à l'administration sous contrôle restreint, gravité propre des faits en discipline), celle que l'adversaire détient (demande de production, mise en demeure, acquiescement), et les conditions d'obtention de toute pièce qui va contre l'orientation probable du juge.
- **Demande.** Ce que ce juge peut accorder à ce stade (réexamen sous contrôle restreint, mesure provisoire limitée en référé) ; toute somme chiffrée tôt, avec sa méthode, dans l'unité utile, et un contre-chiffre en réponse à tout chiffre adverse ; vers l'administration, une demande qui remplit sa propre grille (responsabilité claire, montant certain, signataire compétent, homologation possible).

Un levier qui n'appuie aucun choix est retiré ou employé. Aucune probabilité chiffrée, aucune chance d'un dossier : le profil donne des fréquences de classes et des raisons.

## 6. Ce que reçoit le juge simulé

`python "${CLAUDE_PLUGIN_ROOT}/scripts/decideurs.py" fiche-juge --decideur <id>` écrit `procedure/calibrage_decideur_<id>.md` : formation, standard de contrôle, taux de base avec leur périmètre, culture, ce qui passe et ce qui échoue, sources publiques, et l'empreinte de la fiche. Les leviers, les risques, les choix, l'adversaire et les constats tirés du seul dossier n'y figurent pas : le juge simulé statue comme la juridiction, sans connaître la stratégie de l'auteur. Il part du taux de base, écrit avant la lecture de l'acte, l'ajuste condition par condition et reporte l'empreinte dans `profil_decideur_sha256` de sa lecture à froid.

## 7. Écrire et contrôler

Le sous-agent `sociologue-institution` établit les profils à partir du dossier et des sources publiques ; la session principale vérifie ses sources, arbitre les choix et les inscrit. Le fichier `strategie/decideurs.json` suit `references/schemas/decideurs.v1.schema.json` (`python decideurs.py squelette` en donne la structure vide). Avant tout acte juridictionnel :

```
python "${CLAUDE_PLUGIN_ROOT}/scripts/decideurs.py" valider
python "${CLAUDE_PLUGIN_ROOT}/scripts/decideurs.py" fiche-juge
python "${CLAUDE_PLUGIN_ROOT}/scripts/decideurs.py" controle ecritures/brouillons/<acte>.md
```

Le contrôle bloque un profil absent, invalide, périmé, qui ne couvre pas l'acte ou ne désigne pas sa juridiction, un constat sans source lue, un calibrage qui ne montre que les refus, un taux incohérent, un magistrat nommé, une probabilité, un choix sans appui, une ligne antérieure au profil et une lecture à froid qui n'a pas statué sur la fiche actuelle. Il ne dit pas si le profil est juste : l'`architecte-strategique` le confronte aux décisions publiées et au dossier.

## 8. Requêtes publiques

Termes juridiques, nom public de la juridiction et de l'institution, numéros de textes et de décisions publiées : rien d'autre. Ni le nom du client, ni les faits, dates, montants ou numéros de l'affaire, ni le nom d'un agent ou d'un magistrat. Les identifiants privés déclarés dans `etat/affaire.json` sont refusés par le hook ; la règle vaut au-delà de cette liste.
