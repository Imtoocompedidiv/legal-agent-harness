---
name: analyse-documentaire
description: "Vérité du dossier depuis les pièces : inventaire mécanique, lecture d'enquêteur, extraits vérifiés sur leur page, chronologie et matrice des preuves. À la prise en main, à chaque pièce nouvelle et avant toute écriture qui affirme un fait."
---

# Analyse documentaire

Le juge statue sur les pièces. Un fait que le client raconte et qu'aucune pièce n'établit est une allégation ; un fait qu'une pièce établit mais que l'écriture lui fait dire au-delà de ce qu'elle dit est une faiblesse que l'adversaire exploitera. Cette méthode lit chaque document comme un enquêteur, en tire la chronologie et la matrice des preuves depuis les pièces, puis interdit d'écrire comme décisif un fait qui ne renvoie pas à un extrait littéral d'une pièce analysée.

Commande de base, depuis le dossier d'affaire : `P` désigne `python "${CLAUDE_PLUGIN_ROOT}/scripts/pieces.py"`. Rien ne quitte le poste : le script ne fait aucun appel réseau.

## 1. Coter

Chaque document reçu devient une pièce par `affaire.py piece ajouter`, y compris les pièces de l'adversaire, les avis de réception, les enveloppes, les captures et les courriels exportés en EML (l'export conserve les en-têtes de transport qu'une impression perd). Un message Outlook ou un traitement de texte ancien se convertit en PDF ou en EML, et la conversion se cote à côté de l'original. Une pièce ne se remplace jamais : une version nouvelle reçoit une nouvelle cote.

Écrit : `pieces/originaux/`, `pieces/bordereau.json`, le journal.

## 2. Inventaire mécanique

`P inventaire` lit chaque pièce cotée et écrit `pieces/inventaire.json` et, pour chaque pièce, `pieces/texte/<pièce>.extraction.txt`, découpé par page avec le mode de chaque page :

- empreinte comparée au bordereau (une pièce modifiée depuis sa cotation est signalée), format réel comparé à l'extension, taille, nombre de pages ;
- texte page par page : texte natif, couche d'OCR invisible posée sur un scan, OCR local si Tesseract est installé, page sans texte, page numérisée dont seule une mention ajoutée (en-tête de recueil, tampon numérique) est en texte ;
- métadonnées : auteur, logiciel, dates de création et de modification, historique XMP, version linéarisée ; pour un courriel, en-têtes, serveurs traversés et leurs dates, résultats d'authentification, pièces jointes avec leur empreinte ; pour un document Word, auteurs successifs, modifications suivies et commentaires ; pour une photographie, EXIF ;
- champs de formulaire PDF et leur valeur, cases dessinées d'un formulaire aplati et leur état probable, glyphes de case ;
- champs de signature électronique, images en bas de dernière page ;
- versions antérieures d'un PDF enregistré par ajouts, extraites dans `pieces/rendus/<pièce>/revision_N.pdf` et comparées au texte final ;
- repérages : dates (y compris les dates inexistantes et les jours de semaine faux), montants, numéros d'envoi recommandé (clé de contrôle vérifiée pour le format international S10), formules de signature et de délégation, civilités, références de dossier, documents visés ou joints, mentions de voies et délais ;
- indices numérotés M1, M2… : ce que la lecture devra examiner un par un.

`--refaire` relit tout ; sinon une pièce inchangée n'est pas relue. La commande sort en erreur si une pièce est absente, altérée ou illisible.

L'extraction est une aide de lecture. Elle ne vaut ni lecture visuelle, ni vérification d'une signature, d'un cachet, d'une mention manuscrite ou d'une case.

## 3. Rendu des pages

`P rendre --a-examiner` rend en PNG, dans `pieces/rendus/<pièce>/pNNN.png`, les pages qui exigent l'œil : pages sans texte natif, première et dernière page, pages de formulaire, pages visées par un indice, pages annotées. `P rendre --cote N` rend toutes les pages d'une pièce ; `--pages` et `--dpi` affinent. Toute pièce décisive se rend en entier.

## 4. Lecture d'enquêteur, pièce par pièce

Lancer le sous-agent `analyste-documentaire` par lots cohérents : une décision et la demande à laquelle elle répond, une lettre et son avis de réception, un fil de courriels, les pièces d'un même auteur. Le brief donne la racine du dossier, les cotes à analyser, les cotes déjà analysées à comparer et le chemin du schéma (`${CLAUDE_PLUGIN_ROOT}/references/schemas/analyse_piece.v1.schema.json`), et, quand une mention est imposée par un texte, la règle et son identifiant au registre des sources. Il ne reçoit ni la ligne, ni le récit du client, ni les écritures. Plusieurs lots se lancent en parallèle.

Sans sous-agent, la session principale suit la même grille, dans le même ordre, avec la même interdiction de lire le récit avant d'avoir fini la pièce.

La grille : nature et forme ; auteur et signataire, qualité, délégation invoquée ; destinataires et copies ; date de l'acte, de l'envoi, de la réception ou de la présentation, de la connaissance, chacune rattachée à l'extrait qui la porte ; canal et sa preuve ; objet ; extraits littéraux avec leur page ; ce que la pièce prouve et sa portée ; ce qu'elle ne prouve pas ; mentions imposées par une règle lue ; état de chaque case vu sur le rendu ; examen de chaque indice mécanique ; anomalies ; contradictions internes ; cohérence avec les autres pièces ; documents mentionnés et leur détenteur ; preuves à obtenir et voies possibles ; questions ouvertes.

Règles de lecture :
- La page d'un extrait est son rang dans le fichier, pas le numéro imprimé.
- Une citation se recopie caractère pour caractère, coupures marquées `[…]`. Un passage lu sur l'image porte `lu_sur` « rendu ».
- Une page sans texte natif, une couche d'OCR, une page numérisée sous un en-tête texte se lisent sur leur rendu ; l'acte lui-même est dans l'image.
- Une case cochée, une signature, un cachet, une date manuscrite partiellement lisible se décrivent tels qu'ils se voient. Une date manuscrite en partie masquée se transcrit avec ce qui se lit, et se recoupe avec les autres pièces avant de conclure qu'elle manque.
- Ce qu'une pièce ne prouve pas s'écrit toujours. Nul ne peut se constituer de titre à soi-même (C. civ., art. 1363) : l'écrit qu'une partie a rédigé prouve qu'elle l'a écrit, pas ce qu'elle y affirme. Une copie fiable a la force de l'original, et la présentation de l'original peut toujours être exigée s'il subsiste (C. civ., art. 1379). Une attestation se lit au regard de l'article 202 du code de procédure civile : faits personnellement constatés, identité et liens de l'auteur, mention de sa production en justice et des sanctions, écriture, date et signature de sa main, pièce d'identité jointe. Une signature électronique se présume fiable seulement dans les conditions de l'article 1367 du code civil ; la vérification d'un écrit ou d'une signature déniés appartient au juge (CPC, art. 287).
- Une notification postale a trois dates possibles : l'expédition (cachet du bureau d'émission), la remise (récépissé ou émargement), la réception d'une lettre recommandée avec avis de réception (date apposée par La Poste lors de la remise) (CPC, art. 668 et 669, en matière civile). En matière administrative, les délais de recours ne sont opposables que s'ils ont été mentionnés, avec les voies de recours, dans la notification (CJA, art. R. 421-5) : la fiche relève la présence et le contenu exact de cette mention.
- Un indice mécanique n'est pas une preuve d'altération. Il se conclut, retenu ou écarté, sur ce que montre la pièce.

Écrit : `pieces/analyses/<cote>.json`, au format `analyse_piece/1` (`references/schemas/analyse_piece.v1.schema.json`).

## 5. Vérification

`P verifier` valide chaque fiche et la matrice. Pour chaque fiche : conformité au schéma ; cote, fichier et empreinte identiques au bordereau (une fiche faite sur une autre version est périmée) ; toutes les pages lues ; toutes les pages sans texte natif vues en image, avec un rendu présent ; chaque extrait retrouvé mot pour mot sur sa page (ou au début de la suivante), avec tolérance seulement sur un texte d'OCR ; chaque renvoi à un extrait existant ; dates de réception et d'envoi non antérieures à la date de l'acte, sauf anomalie relevée ; chaque indice de l'inventaire examiné ; signature et cases décrites sur une page vue ; recoupements renvoyant à des cotes et des extraits existants. Une fiche en erreur se refait par le sous-agent ; elle ne se corrige pas à la main pour passer le contrôle.

## 6. Chronologie depuis les pièces

`P chronologie` écrit `chronologie/depuis_pieces.json` : chaque date lue dans les fiches à jour, avec sa nature (acte, envoi, réception, connaissance, autre), sa pièce et son extrait ; puis les dates des pièces absentes de `chronologie/chronologie.json` et les faits de la chronologie sans pièce.

La chronologie de l'affaire se reprend alors à partir de ce fichier : chaque événement cite ses pièces ; le statut « prouve » exige qu'une fiche à jour porte la date et le fait ; un fait qui ne vient que du récit du client reste « allegue » jusqu'à sa pièce ; un fait que l'adversaire discute est « conteste ». Les dates d'acte, d'envoi, de réception et de connaissance sont des événements distincts, typés pour `voies.py`, parce que les délais courent de l'une ou de l'autre.

Écrit : `chronologie/depuis_pieces.json`, puis `chronologie/chronologie.json` par la session principale.

## 7. Matrice des preuves, fait par fait

`preuves/matrice.json` au format 2 (`references/schemas/matrice.v2.schema.json`) : `{"version": 2, "faits_a_prouver": [...]}`. Les faits à prouver sont ceux qu'exigent les conditions de la voie choisie et ceux que l'adversaire devra établir. Pour chacun :

- `fait`, `date_du_fait`, `charge` (`nous`, `adversaire`, `partagee`, `juge`) et `regle_de_charge` : la règle qui fixe la charge, lue (CPC, art. 9 ; C. civ., art. 1353 ; textes du contentieux en cause) ;
- `pieces` et `extraits` : chaque extrait recopié de la fiche, avec `cote`, `extrait` (identifiant dans la fiche), `page` et `citation` identique à celle de la fiche ;
- `force_probante`, l'état de la preuve :
  - `prouve` : une pièce analysée le dit directement, par un extrait vérifié ;
  - `corrobore` : aucune pièce ne le dit seule, des extraits vérifiés d'au moins deux pièces distinctes concordent ;
  - `allegue` : une partie l'affirme, aucune pièce ne l'établit ;
  - `conteste` : établi par nos pièces, discuté par l'adversaire avec ses éléments (champ `contestation` : par qui, où, en quoi) ;
  - `contredit` : une pièce analysée dit le contraire (champ `contre_extraits`) ;
- `force`, le poids de la source pour le juge (`forte`, `moyenne`, `faible`, `nulle`), qui reste distinct de l'état : un fait peut être prouvé par une pièce de faible poids ;
- `decisif` et `actes` quand le fait porte une écriture ; `chronologie` (identifiants d'événements) ; `lacune` et `action` (identifiant de `terrain/actions.json`).

`P verifier` refuse un fait dit prouvé sans extrait conforme, un fait corroboré par une seule pièce, un fait contesté sans contestation décrite, un fait contredit sans contre-extrait, et tout extrait de la matrice qui diffère de la fiche.

## 8. Manques et preuves à obtenir

`P manques` écrit `pieces/manques.json` : pièces citées dans une écriture et absentes du bordereau ; fichiers de `pieces/originaux/` non cotés ; pièces cotées sans fichier ou altérées ; pièces non inventoriées, jamais analysées, à fiche périmée ou invalide ; faits de la chronologie sans pièce, renvoyant à une cote inconnue, ou dont la date ne se lit dans aucune de leurs pièces ; faits de la matrice sans extrait conforme ; documents mentionnés par une pièce et absents du dossier, dont ceux que détient l'adversaire ; pièces jointes de courriels non cotées ; preuves à obtenir sans action inscrite.

Chaque manque utile devient une action de `terrain/actions.json` par le skill `action-sur-le-reel`, qui choisit la voie et écrit d'avance la conséquence du refus : communication d'un document administratif (CRPA, art. L. 311-1, puis saisine de la CADA, préalable obligatoire au recours contentieux, art. L. 342-1) ; demande au juge d'enjoindre à une partie ou à un tiers de produire (CPC, art. 11, 138 et 142) ; mesure d'instruction avant tout procès s'il existe un motif légitime (CPC, art. 145) ; constat de commissaire de justice ; attestation conforme à l'article 202 ; sommation de communiquer ou interpellative ; droit d'accès aux données personnelles ; expertise. Devant le juge administratif, la demande de production passe par ses pouvoirs d'instruction. Le choix de la voie et son moment sont stratégiques : ils reviennent à la session principale et à l'accord du client pour tout acte extérieur.

## 9. Avant d'écrire

La fiche de l'acte (`ecritures/controle/<nom>.fiche.json`) nomme dans `faits_decisifs` les identifiants de la matrice que l'écriture présente comme décisifs, et rattache chaque fait d'une condition ou d'un moyen à son entrée par le champ `matrice`. `P controle ecritures/brouillons/<nom>.md` applique le contrôle documentaire, celui-là même que `gate.py` exécute avant tout dépôt :

- bloquant : fait décisif non rattaché à la matrice, absent de la matrice, sans extrait littéral conforme d'une pièce analysée à jour, seulement allégué, contredit par une pièce, ou dit corroboré sur une seule pièce ;
- alerte : fait décisif contesté, établi seulement par des extraits lus sur image, reposant sur une pièce qui porte une anomalie majeure, ou dont aucune pièce n'est citée dans l'écriture ; faits de conditions ou de moyens sans renvoi à la matrice ; pièce citée sans fiche d'analyse, avec une fiche périmée ou invalide.

## 10. Pièce nouvelle

Une pièce nouvelle, reçue de l'adversaire, d'un tiers ou du client, reprend les étapes 1 à 8 pour elle et pour les pièces qu'elle touche : la lecture des autres pièces change à sa lumière, et les fiches de comparaison se refont si un recoupement change. Toute fiche dont la pièce a changé d'empreinte est périmée.

## Limites

Les repérages et les indices sont mécaniques : des faux positifs et des oublis restent possibles, et leur examen appartient à la lecture. Sans Tesseract, une page numérisée ne se lit que sur son rendu, et ses extraits ne se vérifient pas par le texte. Une signature électronique se constate, elle ne se valide pas ici. Une fiche exacte n'établit pas la portée juridique d'un fait : elle établit ce que la pièce dit.
