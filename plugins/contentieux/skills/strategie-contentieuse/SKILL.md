---
name: strategie-contentieuse
description: "Ligne d'un contentieux : adversaire et décideurs modélisés, fronts, tactique licite, réponse au client sur ses chances. Avant tout plan d'actes ou recommandation au client, et après chaque décision ou réponse adverse."
---

# Stratégie contentieuse

## 0. Ce qui précède la ligne

La ligne se tire de quatre travaux, dans cet ordre :
1. la vérité établie sur pièces (`analyse-documentaire`) ;
2. la théorie de l'affaire éprouvée contre ses concurrentes (`theorie-de-l-affaire`) ;
3. le profil des décideurs et de l'institution adverse (`lecture-des-decideurs`) ;
4. la séquence entière, avec le plan de négociation, depuis le premier acte adverse (`conduite-de-la-sequence`, `negociation-et-persuasion`).

La ligne en est le résumé opérationnel : elle ne les remplace pas. Une ligne écrite sans eux ne choisit pas une voie, elle choisit l'acte qui se présente.

## 1. La ligne d'abord

Écrire soi-même, en quelques phrases, avant tout plan et avant toute délégation : ce que veut le client et dans quel délai réel ; ce que fait l'adversaire et ce qu'il y gagne (le temps, la rétention des pièces, l'usure, nos propres démarches) ; l'autorité qui peut donner le résultat et ce qui la conduit ou la contraint à agir ; le temps qu'il lui faut réellement ; le meilleur coup adverse et la parade ; ce qui ferait changer la ligne. Les actes descendent de la ligne. Une liste de propositions classées par date n'est pas une stratégie. La ligne s'écrit dans `strategie/ligne.json` (`date`, `objectif`, `decideur`, `lecture_adversaire`, `levier`, `meilleur_coup_adverse`, `parade`, `temps_reel`, `chemin_de_victoire` comme suite d'étapes datées, `ce_qui_ferait_changer_la_ligne`) et se résume au journal stratégique. Le contrôle avant dépôt refuse une écriture si la ligne manque ou si une pièce citée est plus récente qu'elle.

Pensée latérale, à chaque révision de la ligne : lister les voies que personne n'a proposées (autre autorité compétente, autre acte à provoquer, autre juridiction, autre fondement, action sur un tiers qui contraint l'adversaire), les écarter ou les retenir par écrit avec leur raison. La carte des délais de `voies.py` et le profil de la juridiction (`juridiction.py`) nourrissent ce travail.

## 1 bis. Revue de charpente

Avant tout acte juridictionnel, après toute décision ou pièce nouvelle et après tout échec, le sous-agent `architecte-strategique` juge l'architecture entière du dossier, pas le seul texte : résultat et décideur, voies comparées (y compris celles que personne n'a proposées), enchaînement des instances et effets des décisions déjà rendues, preuve à créer, cohérence de toutes les écritures et image que le dossier donne au juge, stratégie de l'adversaire, leviers hors prétoire, justesse de l'acte en projet. Sa revue (`strategie/revue_charpente.json`) est exigée par le contrôle avant dépôt, doit être postérieure à la ligne et couvrir l'acte, et chacun de ses points dirimants reçoit une décision. Après un échec, l'autopsie se fait à ce niveau : un rejet sanctionne souvent une architecture avant de sanctionner un texte.

## 2. Filtre de chaque acte

Avant qu'un acte ou une proposition n'atteigne le client : qu'est-ce qu'il change pour l'objectif dans le temps utile ; qu'est-ce qu'il coûte à l'adversaire, et qu'est-ce qu'il lui donne (un délai, une excuse, un argument, une pièce, une information, l'occasion de réparer un vice) ; un avocat exigeant le signerait-il. Un acte qui échoue à l'une de ces questions est coupé, pas présenté. Une faute de l'adversaire s'exploite devant qui peut la sanctionner ; on ne la lui rappelle pas. Peu de fronts, chacun avec son décideur et son délai : la dispersion fait perdre du temps et donne des défenses gratuites.

## 3. Les décideurs

Traiter chaque profil comme une hypothèse de travail à confronter aux décisions réelles de la juridiction (base ouverte, Judilibre), jamais comme une psychologie prêtée à une personne nommée.

- **Juge du tri.** Quelques minutes par dossier, lecture de la première page et des conclusions. Il classe l'affaire d'après les premiers faits qu'il lit, reprend volontiers le cadre du récit le plus simple, se méfie des demandes larges, irréversibles ou qui exigent une instruction, et cherche un motif de rejet sûr. Lui donner la question, l'acte, le fait qui décide et une mesure limitée qu'il peut accorder sans risque.
- **Juge des référés à l'audience.** Il cherche la mesure provisoire proportionnée et la réponse de l'administration ou de l'adversaire. Préparer une feuille d'audience : chaque question probable, la réponse en deux phrases, la pièce.
- **Juge du fond et rapporteur public.** Le temps existe ; la cohérence avec la jurisprudence et la portée de la solution pèsent. Lire les conclusions de rapporteurs publics sur des affaires voisines. Offrir une solution qui ne crée pas de précédent inquiétant.
- **Conseiller rapporteur, cassation.** Il contrôle le droit, pas les faits ; la recevabilité et l'admission filtrent d'abord.
- **Autorité administrative ou décideur privé.** Celui qui signe : ses risques personnels (désaveu, précédent, charge de travail), ses supérieurs, son calendrier. Une demande lui laisse une décision facile et motivable.
- **Avocat adverse.** Ses habitudes d'argumentation visibles dans ses écrits publiés, ce qu'il plaidera en premier, ce qu'il ne voit pas parce qu'il défend la position de son client. Le sous-agent `avocat-adverse` écrit sa meilleure défense.

Les biais documentés (ancrage sur le premier chiffre ou le premier récit, effet de primauté, cohérence narrative, aversion pour les mesures irréversibles) commandent l'ordre et la forme ; leurs limites et leurs sources sont dans `references/decideurs.md`.

## 4. Tactique licite

L'arsenal complet est dans le skill `rapport-de-force` : chaque levier (règles V) avec son effet sur l'adversaire, son moment, sa preuve et sa limite lus à la source, et la frontière (règles X). La tactique ne tend pas la main : elle fait parler l'adversaire, le fige, retourne contre lui ses écrits, ses silences et ses délais, et ne lui donne rien qui ne soit payé.

- **Silences adverses.** Un silence se transforme en décision implicite datée, en aveu procédural, en inférence tirée d'un refus de produire, ou en carence devant l'autorité qui peut la sanctionner. Devant le juge administratif, l'administration qui ne produit pas se fait mettre en demeure par le président, puis est réputée avoir acquiescé aux faits (CJA, art. R. 612-3 et R. 612-6 ; V10) ; on ne lui rappelle jamais son délai.
- **Contradictions.** Relever chaque écart entre les écrits de l'adversaire, ses actes et sa défense ; le présenter au juge par citations juxtaposées, sans commentaire.
- **Charge de la preuve.** Identifier la règle de charge et ses aménagements (présomptions légales, faits que seul l'adversaire peut établir, régimes de discrimination, dialectique de la preuve devant le juge administratif) ; demander au juge d'exercer ses pouvoirs d'instruction quand l'adversaire détient la preuve.
- **Dilemmes.** Poser à l'adversaire une question dont chaque réponse sert : il confirme le fait utile ou contredit sa propre pièce.
- **Incidents et sommations.** Exceptions de procédure avant toute défense au fond, fins de non-recevoir, sommation de communiquer, injonction de produire, incident devant le juge de la mise en état : chacun pour un effet décisif, jamais pour gagner du temps contre l'intérêt du client. Le vice régularisable de l'adversaire, notamment le défaut de pouvoir de son représentant, se garde en réserve et se soulève quand il ne peut plus être couvert (CPC, art. 121 et 126 ; C. civ., art. 1156 ; V13 à V15) ; il ne s'annonce jamais dans une lettre.
- **Contrainte.** Injonction et astreinte demandées dès la requête, exécution provisoire et radiation de l'appel adverse non exécuté, saisie conservatoire quand le recouvrement est menacé, demande reconventionnelle, appel incident, mise en cause du tiers qui paiera (V19 à V24).
- **Calendrier.** Déposer tôt ; choisir la date qui oblige l'adversaire à répondre dans un délai court ; éviter les veilles de fermeture ; anticiper la date réelle de la décision par rapport à l'échéance du client. Tenir le calendrier des délais qui courent contre lui (caducité, irrecevabilité, péremption, notification du jugement favorable) et ne jamais les lui rappeler (V28).
- **Rien de gratuit.** Aucune information, aucune pièce, aucune concession, aucune réunion ni aucun délai sans contrepartie écrite, sauf ce que la loi ou le juge impose ; quand l'adversaire ne conteste qu'une part, exiger aussitôt le reste (V29 à V32).
- **Limites.** Amende civile et dommages-intérêts pour procédure abusive (CPC, art. 32-1), amende pour recours abusif (CJA, art. R. 741-12), loyauté de la preuve, secret professionnel, déontologie : la malice reste dans le droit ; aucune plainte, aucun signalement ni aucune révélation ne s'échange contre un paiement ou une signature (C. pén., art. 312-10 ; Cass. crim., 30 janvier 2001, n° 99-87.346 ; `negociation-et-persuasion/references/levier_limites.md`) ; ni signalement d'un fait inexact (art. 226-10), ni faux (art. 441-1), ni pression sur un témoin (art. 434-15). Le levier illicite que propose le client se refuse en nommant le texte, et le coup licite le plus dur se joue à sa place (`rapport-de-force/references/limites.md`, X1 à X10).

## 5. Contradiction et décision

Avant toute recommandation importante, faire attaquer la ligne et ses actes par le sous-agent `contradicteur`, qui reçoit les pièces et les textes, pas la conclusion qu'on espère. Chaque objection reçoit une décision : couper, garder, reformuler. Une objection ne produit jamais une branche subsidiaire de plus par simple précaution. Un consensus obtenu en empilant des précautions est un échec de méthode.

## 6. Parler au client

La mauvaise nouvelle d'abord, une fois, avec la réponse déjà préparée. Une recommandation, ses conditions, ce qui la ferait changer. Aucune probabilité chiffrée sans méthode défendable, mais l'issue la plus probable se dit toujours, en mots ; les taux observés dans une juridiction sont un garde-fou, pas la chance d'un dossier individuel. Une question ou un désaccord du client appellent un argument, jamais un retrait. Chaque recommandation qui engage le dossier s'inscrit dans `strategie/positions.json` avec son fondement et ce qui la ferait changer (`scripts/positions.py`). Face à une contestation, la position et l'objection se jugent côte à côte, comme les jugerait un associé extérieur au dossier ; sans élément nouveau, la position se maintient, avec sa raison et ce que le client peut apporter pour la changer ; un changement de position nomme l'élément nouveau qui le cause (pièce cotée, source lue, décision, fait daté), et un désaccord, une insistance ou l'avis d'un proche n'en sont pas (`rapport-de-force`, section 5). Le client décide des actes : son instruction contraire se consigne, l'analyse reste. Les décisions qui reviennent au client se posent en clair dans le message.
