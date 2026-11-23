---
name: action-sur-le-reel
description: "Démarches licites qui créent des preuves, provoquent une décision attaquable, figent un fait ou exposent la mauvaise foi adverse. À la prise en main, à chaque reprise et avant toute écriture importante."
---

# Action sur le réel

Un dossier se construit avant de se plaider. Le juge statue sur les pièces qu'on lui donne ; la plupart des pièces décisives se fabriquent loyalement avant l'audience. Ce protocole s'applique avant de figer une stratégie d'écriture et chaque fois que la matrice probatoire montre une lacune.

## 1. Audit du réel

Partir de `preuves/matrice.json` et de la chronologie. Pour chaque condition de la voie envisagée (urgence, doute sérieux, trouble manifestement illicite, obligation non sérieusement contestable, faute, préjudice, lien de causalité, recevabilité), écrire ce que le juge verra sur pièces aujourd'hui, ce qui manque, et ce que l'adversaire peut produire contre nous. Vérifier les évidences : l'acte existe-t-il, est-il signé, par qui, a-t-il été notifié, à quelle adresse, le pli a-t-il été présenté, retiré, renvoyé ; la demande a-t-elle bien été reçue (accusé, preuve de distribution) ; le dernier contrôle de chaque canal de notification date-t-il d'hier.

## 2. Catalogue des actions

Choisir l'action selon l'effet recherché sur le juge, pas selon sa disponibilité.

- **Provoquer une décision attaquable.** Quand l'adversaire se tait ou répond par des courriels de service, adresser une demande précise à l'autorité compétente, par un moyen qui prouve la réception et la date. Le silence fait naître une décision implicite à une date calculable ; une demande de motifs ouvre un délai de communication (CRPA, art. L. 232-4, à lire). En droit civil, une mise en demeure fixe le point de départ des intérêts, caractérise le refus et prépare le référé-provision.
- **Figer un fait.** Constat de commissaire de justice (lieux, pages web, messages, état d'un bien), captures datées avec URL et horodatage, attestations conformes à l'article 202 du CPC, relevés et accusés de réception conservés en original.
- **Obtenir les pièces détenues par l'adversaire.** Demandes de communication de documents administratifs (CRPA, livre III) puis CADA, droit d'accès aux données personnelles, sommation de communiquer entre avocats, demande d'injonction de produire au juge (CPC, art. 11 et 138 à 142), mesure d'instruction avant tout procès (CPC, art. 145). Chaque demande écrit d'avance la conséquence du refus : production forcée, inférence défavorable, moyen d'instruction devant le juge.
- **Faire parler l'adversaire.** Une question écrite précise, fermée, adressée au bon décideur, dont toute réponse sert : la réponse affirmative est un aveu utile, la négative une contradiction avec une pièce, le silence un fait daté. Ne jamais lui rappeler une obligation déjà violée sans la faire sanctionner par qui en a le pouvoir.
- **Régulariser.** Corriger nos propres failles avant que l'adversaire les relève : pouvoir, qualité, intérêt, délai, mention obligatoire, pièce manquante, attestation non conforme.
- **Expertise.** Expertise amiable contradictoire, ou non contradictoire soumise ensuite au débat, quand la preuve technique décide l'affaire. Un avis médical ou technique s'obtient par des questions neutres et précises adressées au professionnel, sans lui dicter de conclusion.
- **Créer la situation.** Accomplir la démarche dont l'absence serait opposée (demande d'aménagement, candidature, réclamation préalable, saisine d'un médiateur ou d'une autorité indépendante quand elle produit un acte utile au juge dans le temps utile).
- **Réorganiser.** Modifier ce qui dépend du client et pèse sur l'appréciation du juge (calendrier, suivi, démarches parallèles), sans jamais fabriquer d'apparence.

## 3. Limites

Les preuves restent loyales et licites. En matière civile, une preuve obtenue de façon déloyale peut être admise si elle est indispensable à l'exercice du droit à la preuve et si l'atteinte est proportionnée (Cass., ass. plén., 22 décembre 2023, n° 20-20.648 et n° 21-11.330, à relire avant usage). En matière administrative, la preuve est libre sous le contrôle du juge, avec l'exigence de loyauté. Avant d'opposer un risque pénal à une démarche du client, lire la jurisprudence sur l'élément constitutif en cause, pas seulement l'article. Aucune pression illicite, aucun faux, aucune manœuvre envers un témoin, aucune usurpation.

## 4. Sortie

L'audit s'écrit dans `terrain/audit.json` : `date` (lue sur le poste), `evidences_verifiees` (chaque évidence contrôlée, avec la preuve et le canal), `lacunes`, `actions_decidees` (identifiants de `terrain/actions.json`). Le contrôle avant dépôt refuse une écriture juridictionnelle sans audit récent et sans canaux relevés.

Chaque action entre dans `terrain/actions.json` : objectif probatoire, action, destinataire, effet attendu sur le juge, meilleur coup adverse et parade, délai, fondement de sa licéité, statut. Une action extérieure (envoi, appel, dépôt, achat) attend l'accord exprès du client pour cet acte précis. Le sous-agent `stratege-terrain` peut proposer le plan ; il est relu et tranché ici avant d'arriver au client, et seules les actions qui changent l'issue dans le temps utile lui sont présentées.
