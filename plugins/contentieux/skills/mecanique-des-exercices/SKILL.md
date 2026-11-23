---
name: mecanique-des-exercices
description: "Mécanique propre de chaque exercice (référés, annulation, indemnitaire, appel, cassation, recours préalables, CADA, assignation, prud'hommes, plainte, QPC, CEDH, Défenseur des droits, transaction) : condition qui le fait échouer, exigences implicites, exercice voisin. Dès qu'il faut choisir ou produire une procédure ou une saisine, et avant tout envoi qui protège un délai."
---

# Mécanique des exercices

Chaque exercice a sa mécanique : un décideur qui ne peut accorder que certaines choses, à un stade précis, au vu d'un standard et d'une preuve donnés, sous des conditions de forme et de délai que les textes n'énoncent pas toujours au même endroit. Une écriture parfaite dans le mauvais exercice perd : référé retenu alors que l'urgence tombera, recours gracieux qui ne protège pas le délai, requête au fond perdue faute d'avoir été déposée à temps sous une forme conservatoire, condition de recevabilité propre à un contentieux spécial non vue. Ces erreurs ne se corrigent pas à la rédaction. Elles se préviennent par un diagnostic fait avant la première ligne, sur la fiche de l'exercice, et vérifié pièce par pièce dans le dossier.

Le skill s'applique à toute production qui engage l'affaire : acte devant un juge, recours ou demande à une autorité, plainte, saisine d'une autorité indépendante, proposition transactionnelle. Il précède `ecriture-juridictionnelle` et nourrit `conduite-de-la-sequence`, qui choisit entre les voies ; le contrôle avant dépôt (`controle-avant-depot`) vérifie ensuite que le diagnostic est complet.

## 1. Quand faire le diagnostic

- À l'ouverture de l'affaire, pour chaque voie que la séquence examine.
- Dès que le client propose un acte : son acte passe le même diagnostic que les autres, et le refus se motive par la condition qui le fait échouer.
- Avant toute écriture, et de nouveau après tout fait qui change la mécanique : décision nouvelle, silence qui devient refus implicite, mesure retirée ou remplacée, date qui approche, pièce produite par l'adversaire.
- Avant tout envoi destiné à interrompre, proroger ou conserver un délai.

## 2. Le diagnostic, dans l'ordre

Ouvrir la fiche de l'exercice envisagé (`references/<fichier>.md`, liste en section 5), puis celles de ses voisins. Les fiches ont été lues à la source le 19 novembre 2026 ; leur section « Points non vérifiés » dit ce qui reste à lire. Toute règle dont l'acte dépend se relit à la source à la date utile de l'affaire et s'inscrit au registre (`etat/sources.json`) avant d'être employée.

1. **Le résultat et son temps.** Ce que le client doit obtenir, et la date à laquelle ce résultat lui sert encore. Un exercice qui donne le bon résultat trop tard est le mauvais exercice.
2. **Qui décide, à quel stade, sur quoi.** L'autorité ou la formation, l'existence d'un filtre (tri des référés, ordonnances de l'article R. 222-1 du code de justice administrative, admission des pourvois, non-admission, juge unique de la Cour européenne, filtrage des QPC, orientation par le bureau de conciliation) et son critère légal exact, puis la question précise que le décideur tranche. Ce qu'il ne lit pas compte autant que ce qu'il lit : le juge du tri ne lit que la requête.
3. **Le standard et l'office.** Doute sérieux, évidence, contestation sérieuse, trouble manifestement illicite, motif légitime, contrôle normal ou restreint, appréciation souveraine ; charge de la preuve et caractère inquisitoire ou accusatoire ; date à laquelle s'apprécient les faits et le droit (la légalité à la date de l'acte, l'urgence au jour où le juge statue) ; ce que le juge peut ordonner à ce stade et ce qu'il ne peut pas ordonner. Toute conclusion se rattache à ce pouvoir.
4. **La condition qui fait échouer.** La fiche donne la condition qui fait le plus souvent échouer l'exercice et les situations qui la font tomber. Les confronter une à une au dossier. Prendre l'argument que la défense opposera dans sa meilleure version, et regarder en particulier :
   - l'intérêt invoqué par le demandeur que le juge attribuera à la mesure attaquée (l'intérêt de l'enfant contre une mesure de protection, la sécurité, la santé publique) ;
   - la situation de fait qui ôte l'urgence ou l'intérêt (traitement maintenu, ressources suffisantes, effets épuisés, satisfaction obtenue, recours suspensif qui protège déjà) ;
   - la décision, même implicite, qui fait obstacle à la mesure demandée ;
   - le retard du demandeur, ou une situation qu'il connaissait.

   Écrire pour chacune la parade, pièce à l'appui, datée de la date où le décideur statuera. Une condition décisive sans parade prouvée met l'exercice en réserve : construire d'abord la preuve, ou passer au voisin.
5. **La cible.** L'acte qui décide (ni préparatoire, ni confirmatif, ni mesure d'ordre intérieur), sa date et son régime ; la décision née du silence et sa date de naissance ; le chef de dispositif critiqué ; la prétention chiffrée ; les faits et leur qualification ; la norme. Une cible qui n'appartient pas à l'exercice (une décision dans un référé mesures utiles, un procès au fond engagé dans une mesure in futurum) le fait échouer quelle que soit la qualité de l'acte.
6. **Ce que l'auteur produit.** Acte, destinataire, mode de saisine ou de dépôt, mentions et pièces obligatoires, une requête par fondement, distincte quand le texte l'exige.
7. **Les exigences implicites.** Reprendre la liste de la fiche, une par une, et vérifier chacune dans le dossier : pièces à joindre ; mentions ; notifications au défendeur, au titulaire ou au ministère public ; délais, leur point de départ, leur computation, ce qui les interrompt ou les proroge et ce qui ne le fait pas ; mode d'envoi qui prouve la date ; représentation ; timbre, consignation ou aide juridictionnelle ; ordre des moyens et causes juridiques ouvertes dans le délai ; cristallisation ; préalables obligatoires ; recevabilité propre au contentieux spécial ; obligations que fera naître la décision (confirmation du maintien de la requête au fond, signification, appel ou pourvoi et leurs délais). Une exigence se dit vérifiée avec sa preuve ou sa source lue, ou sans objet avec sa raison.
8. **Le régime spécial.** Avant de traiter l'acte comme de droit commun, chercher le régime propre à la matière (`python "${CLAUDE_PLUGIN_ROOT}/scripts/gate.py" --regimes`, `references/domaines/*.md`). Un régime spécial peut fixer une autre juridiction, un délai plus bref, un délai que le recours administratif ne proroge pas, une notification du recours, une cristallisation ou un intérêt à agir encadré. Quand il est douteux, raisonner comme s'il s'appliquait, et contrôler l'acte sous ce régime.
9. **Ce qui fait gagner.** L'ordre qui gagne devant ce décideur, le moyen qui se voit sur pièces, la preuve qui emporte la condition décisive, la demande qu'il peut accorder à ce stade.
10. **Les erreurs hors sujet.** Les relire dans la fiche et vérifier que l'acte n'en commet aucune : mauvais juge, mauvais stade, mauvaise cible, mauvais moment, standard confondu, demande que le juge ne peut pas accorder.
11. **L'exercice voisin.** Examiner au moins les voisins que la fiche désigne. Pour chacun, dire le critère qui ferait basculer vers lui et pourquoi il convient moins bien, ou mieux, dans ce dossier ; dire ce que l'exercice retenu ferme ou ouvre aux autres. Quand un voisin convient mieux, il remplace l'exercice envisagé.

## 3. Règles de décision

- **Conserver d'abord.** Un délai qui expire se sauve par l'acte qui le protège réellement. Un recours administratif ne protège le délai que s'il est formé à temps, dans une matière où il proroge, par un mode qui prouve sa date d'expédition ou de dépôt (fiche `recours-administratifs-prealables.md`). Quand le délai d'une requête au fond expire dans les 72 heures, déposer une requête conservatoire avec au moins un moyen (skill `controle-avant-depot`, section 1 quater) plutôt que perdre le délai pour une pièce qui peut suivre.
- **Un exercice par acte.** L'acte relève d'un seul exercice. Des conclusions fondées sur deux référés dans une même requête (CE, 6 mars 2002, n° 241534 ; CE, 17 mars 2008, n° 306461) et une demande de suspension réunie aux conclusions au fond (CE, 26 janvier 2007, n° 297991) se rejettent pour cette seule raison (fiches `refere-mesures-utiles.md` et `refere-suspension.md`).
- **La condition décisive se prouve avant de déposer.** Un exercice dont la condition décisive n'est pas établie aujourd'hui sur pièces ne part pas. La séquence le met en réserve avec la preuve à créer et la date, ou retient le voisin.
- **La demande accordable.** Ne demander que ce que ce décideur peut accorder à ce stade, dans la forme où il l'accorde d'ordinaire ; le reste se plaide ailleurs ou plus tard.
- **La proposition du client.** Elle reçoit une réponse de fond : la condition qui la fait échouer, la pièce qui le montre, l'exercice qui la remplace et ce qu'il faut préparer pour lui. Si un élément nouveau rend la proposition juste, le dire et changer de recommandation.
- **Une saisine, une fonction.** Chaque saisine sert une fonction nommée dans la séquence ; un exercice qui n'en a pas est refusé (`conduite-de-la-sequence`, section 6).
- **Le pronostic se forme au siège.** Une requête, un moyen ou une demande lus seuls paraissent toujours fondés : leur auteur les a écrits pour cela. Avant de dire l'issue, et quelle que soit la partie que l'on défend, faire trois choses :
  1. partir du taux de base que donne la fiche (section 10) pour cet exercice devant ce décideur ;
  2. écrire la meilleure réponse que la décision attaquée, la défense ou l'administration oppose à chaque argument décisif, dans sa forme la plus forte, avec ce qu'elle produira ;
  3. appliquer le standard de contrôle qui protège cette réponse : appréciation souveraine des juges du fond, contrôle restreint, évidence exigée du juge des référés, constatations de fait que le moyen ne peut remettre en cause.

  L'issue annoncée en tête est la plus probable une fois cette réponse pesée. Ce n'est ni l'issue souhaitée ni celle d'une branche improbable. Une condition qui la renverserait se dit ensuite, avec sa probabilité.

## 4. Sortie : le bloc `exercice` de la fiche de l'acte

Le diagnostic s'écrit dans la fiche de l'acte (`ecritures/controle/<nom>.fiche.json`), champ `exercice`. `python "${CLAUDE_PLUGIN_ROOT}/scripts/exercices.py" squelette <identifiant>` en imprime la structure pour l'exercice choisi, avec ses exigences implicites et ses voisins.

- `exercice` : identifiant de la section 5.
- `date` : date du diagnostic (AAAA-MM-JJTHH:MM, lue sur le poste).
- `juge_et_stade` : `juge` (la formation qui décidera), `stade` (filtre, tri, audience, admission, orientation), `standard` (le standard de contrôle et la charge de la preuve), `office` (ce que ce juge peut ordonner à ce stade).
- `ce_qu_il_decide` : la question exacte que le décideur tranchera.
- `condition_decisive` : `condition` (nom de la condition du régime ou de la fiche), `pourquoi_decisive`, `preuve` (`pieces` du bordereau, `faits` de la matrice, `sources` du registre), `ce_qui_la_ferait_tomber` (liste d'objets `situation`, `parade`, et `pieces` quand la parade en a).
- `condition_principale` : quand la condition décisive retenue n'est pas celle que la fiche désigne comme la plus fréquente cause d'échec, objet `condition`, `etat` (etablie), `preuve`, qui dit pourquoi cette dernière est acquise.
- `cible` : `nature` (acte, decision_juridictionnelle, pretention, faits, norme, document, situation), `designation`, `acte` (identifiant de `actes_attaques` quand la cible est un acte), `date`.
- `ce_qui_fait_gagner`.
- `exigences_implicites` : une entrée par exigence de la fiche, `cle`, `verifiee` (vrai), `preuve` ou `source` ; ou `cle` et `sans_objet` avec sa raison.
- `voisins_ecartes` : objets `exercice` (identifiant, ou `autre:<libellé>`), `raison` (la condition ou le critère qui l'écarte dans ce dossier).
- `regime_special` : `applicable` (vrai ou faux), `texte` (le régime lu, ou « droit commun » avec sa source), `type_acte` quand un régime de `gate.py` lui correspond, `proroge_par_recours_administratif` (faux quand la matière exclut la prorogation du délai par un recours administratif).
- `envoi` : pour un acte qui doit protéger un délai, `mode` (depot_contre_recepisse, lettre_recommandee, teleservice, telerecours, rpva, courrier_electronique_avec_accuse, signification, courrier_simple), `date_prevue` (AAAA-MM-JJ) et `but` (proroger, interrompre, conserver).

`python "${CLAUDE_PLUGIN_ROOT}/scripts/exercices.py" valider ecritures/controle/<nom>.fiche.json` contrôle le bloc ; une fois le correctif `integration/exercices.md` appliqué, le contrôle avant dépôt l'exécute aussi et le hook le signale dès l'enregistrement de la fiche. Il bloque une écriture juridictionnelle sans diagnostic complet : exercice inconnu ou contrôlé sous un autre régime, juge, stade, standard ou office absent, condition décisive sans preuve au bordereau ou sans ce qui la ferait tomber et sa parade, condition la plus fréquente ni retenue ni établie, cible étrangère à l'exercice ou à l'acte attaqué, exigence implicite de la fiche non vérifiée, aucun voisin de la fiche examiné, régime spécial déclaré mais non appliqué, texte qui se présente comme l'exercice écarté, diagnostic antérieur au dernier apport du dossier, exercice que la séquence attribue autrement à cette écriture, lecture à froid du juge simulé qui tient l'exercice pour inadapté sur la version contrôlée. Pour un courrier, il bloque l'envoi destiné à protéger un délai par un mode qui n'en prouve pas la date ou dans une matière où le recours administratif ne proroge pas le délai, et n'émet que des alertes pour le reste. Un diagnostic complet n'atteste pas que l'exercice est juste : il atteste que la question a été posée et que la réponse renvoie à des pièces et à des sources lues.

## 5. Les fiches

| Identifiant | Fiche | Famille |
| --- | --- | --- |
| `refere_suspension` | `references/refere-suspension.md` | urgence |
| `refere_liberte` | `references/refere-liberte.md` | urgence |
| `refere_mesures_utiles` | `references/refere-mesures-utiles.md` | urgence |
| `refere_provision_admin` | `references/refere-provision-administratif.md` | urgence |
| `refere_instruction_admin` | `references/refere-instruction-administratif.md` | urgence |
| `requete_annulation` | `references/requete-annulation.md` | fond |
| `plein_contentieux_indemnitaire` | `references/plein-contentieux-indemnitaire.md` | indemnitaire |
| `appel_administratif` | `references/appel-administratif.md` | voie de recours |
| `cassation_conseil_etat` | `references/cassation-conseil-d-etat.md` | voie de recours |
| `recours_administratif_prealable` | `references/recours-administratifs-prealables.md` | administrative |
| `communication_cada` | `references/demande-de-communication-cada.md` | autorité indépendante |
| `refere_civil_834` | `references/refere-civil-834.md` | urgence |
| `refere_civil_835_trouble` | `references/refere-civil-835-trouble.md` | urgence |
| `refere_civil_835_provision` | `references/refere-civil-835-provision.md` | urgence |
| `mesure_instruction_145` | `references/mesure-d-instruction-145.md` | urgence |
| `assignation_fond` | `references/assignation-au-fond.md` | fond |
| `conclusions_mise_en_etat` | `references/conclusions-et-mise-en-etat.md` | fond |
| `appel_civil` | `references/appel-civil.md` | voie de recours |
| `pourvoi_civil` | `references/pourvoi-cassation-civile.md` | voie de recours |
| `saisine_prudhommes` | `references/conseil-de-prud-hommes.md` | fond |
| `refere_prudhommal` | `references/refere-prud-homal.md` | urgence |
| `plainte_simple` | `references/plainte-simple.md` | pénal |
| `plainte_partie_civile` | `references/plainte-avec-constitution-de-partie-civile.md` | pénal |
| `citation_directe` | `references/citation-directe.md` | pénal |
| `appel_penal` | `references/appel-penal.md` | voie de recours |
| `pourvoi_penal` | `references/pourvoi-penal.md` | voie de recours |
| `qpc` | `references/qpc.md` | constitutionnel |
| `requete_cedh` | `references/requete-cedh.md` | européen |
| `defenseur_des_droits` | `references/defenseur-des-droits.md` | autorité indépendante |
| `transaction_mediation` | `references/transaction-et-mediation.md` | amiable |

Chaque fiche suit le même plan : qui décide, standard et office, condition qui fait échouer et sa preuve, cible, forme, exigences implicites, ce qui fait gagner, erreurs hors sujet, voisins, statistiques publiées avec leur statut, points non vérifiés, sources, puis les données de contrôle que lit `exercices.py`. `exercices.py liste` les énumère ; `exercices.py fiche <identifiant>` donne le chemin et les données d'une fiche.

Un exercice absent de la liste (référé précontractuel, injonction de payer, saisie conservatoire, opposition, juge de l'exécution) se diagnostique avec les mêmes questions, sur les régimes de `references/domaines/` et les textes lus, et le bloc porte l'identifiant `autre:<libellé>` : le contrôle exige alors les mêmes champs, sans liste d'exigences propre.

## 6. Limites

Les fiches disent l'état du droit lu au 19 novembre 2026 et leurs lacunes ; elles ne dispensent pas de relire les textes à la date utile de l'affaire. Les conditions présentées comme les plus fréquentes causes d'échec sont, faute de statistique publiée par motif, des inférences tirées des décisions lues, et chaque fiche le dit. Le contrôle est mécanique : il vérifie que chaque question a reçu une réponse rattachée à une pièce ou à une source, pas que la réponse est juste.
