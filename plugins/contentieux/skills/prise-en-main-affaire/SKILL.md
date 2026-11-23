---
name: prise-en-main-affaire
description: "Ouvrir ou reprendre un dossier (nouvelle affaire, reprise, compaction, échec) : arborescence, pièces, chronologie, échéances, canaux, matrice probatoire."
---

# Prise en main ou reprise d'une affaire

## Ouverture

Si le dossier n'existe pas, le créer par `python "${CLAUDE_PLUGIN_ROOT}/scripts/affaire.py" init <dossier> --intitule ... --client ... --adversaire ... --objectif ...`, puis travailler depuis ce dossier. L'objectif s'écrit dans les mots du client, avec ses conditions (ce qu'il refuse, ce qu'il accepte en repli). S'il existe une affaire du moteur `legal_harness`, noter son identifiant dans `etat/affaire.json`.

## Reprise

Lire, dans cet ordre et jusqu'à leur dernière ligne : `etat/passation.md`, `etat/echeances.json`, `etat/objections.json`, `etat/consignes_affaire.md`, la fin du journal, puis `strategie/journal_strategique.md`. Un résumé de session ou de compaction ne remplace aucune de ces lectures. Chercher ensuite dans le dossier tout ce qui touche la question du moment, y compris ce qui a déjà été dit au client et ce qu'il a écrit. Annoncer ce qui a été lu en entier et ce qui ne l'a pas été.

## Inventaire en six passes

1. **Pièces.** Chaque document reçu devient une pièce cotée par `affaire.py piece ajouter`, avec date, auteur et description neutre, puis passe par le skill `analyse-documentaire` : `pieces.py inventaire`, `pieces.py rendre --a-examiner`, fiche d'analyse par le sous-agent `analyste-documentaire`, `pieces.py verifier`. Une transcription va dans `pieces/texte/`. Une extraction de PDF ne vaut pas vérification visuelle d'une signature, d'un tampon, d'une date manuscrite ou d'une case cochée : le noter. Un formulaire se transcrit avec l'état de chaque case, vu sur l'original rendu en image ; un moyen ne s'appuie jamais sur une rubrique dont l'état n'a pas été vu.
2. **Chronologie.** Chaque fait daté entre dans `chronologie/chronologie.json` avec ses pièces et son statut (prouvé, allégué, contesté), à partir des dates lues dans les fiches d'analyse (`pieces.py chronologie`), jamais du seul récit du client. Les dates de connaissance, de notification et de présentation des plis se distinguent de la date des actes.
3. **Actes et décisions.** Pour chaque acte de l'adversaire ou de la juridiction : auteur, date, objet exact, demande à laquelle il répond, notification (mode, date de première présentation, retrait), voies et délais. Une demande restée sans réponse a une date de naissance de décision implicite à calculer et à inscrire.
4. **Échéances.** Chaque délai s'inscrit par `affaire.py echeance ajouter` avec sa règle lue (article et version), son point de départ prouvé et sa certitude. Un délai calculé sur un point de départ supposé reste un scénario. Les délais de garde postale, de distance, de prorogation par recours administratif et les jours fériés se vérifient.
5. **Canaux de notification.** Recenser toutes les voies par lesquelles une décision peut arriver : chaque adresse postale connue de l'adversaire (y compris l'adresse déclarée dans les écritures), avis de passage et retours à l'expéditeur, messageries et leurs dossiers indésirables, espaces numériques, téléprocédures. Compléter `etat/canaux.json` (adresse, fréquence, responsable). Une décision peut attendre dans un bureau de poste pendant que l'équipe plaide son absence : un canal non relevé est un risque de délai et un risque de stratégie.
6. **Matrice probatoire.** Au format 2 (skill `analyse-documentaire`, étape 7) : pour chaque fait à prouver, qui en a la charge et selon quelle règle, les pièces, les extraits littéraux recopiés des fiches, l'état de la preuve (prouvé, corroboré, allégué, contesté, contredit), le poids de la source, la lacune et l'action qui la comblerait. `pieces.py manques` donne ce qui manque, ce que l'adversaire détient sans l'avoir produit et les preuves à obtenir ; elle alimente `terrain/actions.json`.

## Outils de prise en main

- **Chronologie typée.** Donner un `type` aux demandes, décisions, ordonnances et jugements (voir l'aide de `voies.py`) ; `python "${CLAUDE_PLUGIN_ROOT}/scripts/voies.py" --inscrire` calcule alors les naissances de décisions implicites et les délais de recours, et les inscrit comme scénarios à vérifier.
- **Adversaire.** Lancer le sous-agent `analyste-adverse` sur toutes les pièces émanant de l'adversaire : déclarations, contradictions vérifiées dans leur contexte, silences, aveux.
- **Juridiction.** `python "${CLAUDE_PLUGIN_ROOT}/scripts/juridiction.py" profil --code <TAxx> --requete '<mot> ET "<expression>"'` établit, sur les décisions publiées, ce que la juridiction trie, instruit et accorde, sans aucun décompte par magistrat (CJA, art. L. 10, al. 4), et écrit le calibrage équilibré du juge simulé (`procedure/calibrage_<code>.md` : refus et accueils en nombre égal, au filtre et après instruction, avec les taux publiés). Pour une juridiction judiciaire ou européenne, `juridiction.py calibrage --decisions <relevé> --avant <jour du dépôt>` construit le même calibrage depuis des décisions relevées sur LibreJustice. Requêtes génériques seulement.

## Avant de passer à la stratégie

L'ordre des travaux est fixe, et chacun écrit son fichier d'état que le contrôle lit :
1. `analyse-documentaire` : chaque pièce lue comme un enquêteur, matrice des preuves rattachée aux extraits ;
2. `theorie-de-l-affaire` : hypothèses concurrentes éprouvées sur pièces, théorie retenue (`strategie/theorie.json`) ;
3. `lecture-des-decideurs` : profil du juge et de l'institution adverse (`strategie/decideurs.json`) ;
4. `conduite-de-la-sequence` : campagne entière depuis le premier acte adverse (`strategie/sequence.json`) ;
5. `negociation-et-persuasion` : plan de négociation (`strategie/negociation.json`) ;
6. `action-sur-le-reel` : l'état du dossier se transforme avant de s'écrire ;
7. `strategie-contentieuse` : la ligne, suivie de la revue de la campagne par `architecte-strategique`.

## Fin de session

Réécrire `etat/passation.md` : fait et vérifié (avec preuves), en cours, prochaines actions datées avec leur responsable, décisions attendues du client, sources lues et non lues, points de vigilance. Le hook Stop refuse la fin de session tant que ce n'est pas fait si le dossier a changé.
