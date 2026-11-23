# Droit français de l'amiable : textes en vigueur et règles opérationnelles

Objet. Ce fichier donne le droit positif que le module `negociation-et-persuasion` applique : effet de chaque voie amiable sur les délais, préalables amiables obligatoires, transaction civile et administrative, interdiction des libéralités, homologation, médiation et conciliation, audience de règlement amiable, procédure participative, confidentialité, médiateurs institutionnels et Défenseur des droits, amiable pénal et fiscal. Les limites déontologiques et pénales de l'usage de la procédure comme levier sont dans `levier_limites.md` ; la littérature de négociation dans `negociation_litterature.md` (règles N) ; la persuasion dans `persuasion_litterature.md` (règles P).

Date de lecture : 18 novembre 2026 (date du poste). Tous les textes ont été lus sur LibreJustice dans leur version en vigueur ce jour, sauf mention d'une autre date ; le lien Légifrance de chaque version est celui que LibreJustice donne pour l'article. Un texte qui change après cette date se relit avant usage : `get_norm` avec la date utile.

Statut. Chaque règle de droit est de **droit positif** (texte ou décision lus à la source). L'acte qui en est tiré est une **inférence** quand il dépasse ce que le texte dit ; c'est alors écrit. Statut de lecture des décisions : « texte lu » (décision intégrale), « analyse lue » (analyse officielle du recueil Lebon ou sommaire du Bulletin, avec les métadonnées), « non lu ».

Changements récents qu'une mémoire d'entraînement ignore, vérifiés ici :

- Le décret n° 2025-660 du 18 juillet 2025 a recodifié les modes amiables civils au livre V du code de procédure civile (articles 1528 et suivants), applicables aux instances en cours au 1er septembre 2025. Les anciens articles 127 à 131-15 et 774-1 et suivants ne sont plus les bons renvois : l'audience de règlement amiable est aux articles 1532 à 1532-3, la confidentialité à l'article 1528-3, l'homologation aux articles 1543 à 1545-1.
- Le décret n° 2026-683 du 27 juillet 2026 a modifié l'article 1533 (injonction de rencontrer un conciliateur ou un médiateur) à compter du 1er octobre 2026.
- La loi n° 2026-403 du 26 mai 2026 de simplification de la vie économique (article 25) a réécrit le chapitre Ier du titre II du livre IV du CRPA : l'article L. 421-1 ne vise plus que la médiation, l'article L. 421-2 oblige l'administration de l'État à mettre un médiateur à disposition dans des domaines fixés par décret, l'article L. 421-3 attache aux médiations engagées à compter de la promulgation l'interruption des délais de recours de l'article L. 213-6 du CJA, et l'article L. 424-2 donne le même effet à la médiation menée par le Défenseur des droits.
- L'article L. 247 du livre des procédures fiscales change de version au 1er janvier 2027 ; l'article 41-1 du code de procédure pénale est réécrit par l'ordonnance n° 2025-1091 du 19 novembre 2025 avec effet au 1er janvier 2029. Pour un acte postérieur à ces dates, relire la version applicable.


## 1. Ce que chaque voie amiable fait aux délais

Destinataires : `negociateur`, `architecte-strategique`, skill `strategie-contentieuse`. C'est la première question avant toute démarche amiable : une négociation qui laisse expirer un délai de recours fait perdre l'alternative, donc tout pouvoir de négocier (N23).

**D1. Écrire, avant toute démarche, l'effet de la voie amiable choisie sur chaque délai qui court.**

Acte. Pour chaque voie amiable envisagée, le plan inscrit le délai qui court (recours contentieux, prescription, forclusion, péremption), l'effet de la voie sur ce délai et le texte qui le prévoit, puis la date à laquelle le délai reprend. Si la voie n'a aucun effet, le plan prévoit l'acte conservatoire (recours administratif, requête, assignation, mesure conservatoire) qui protège le délai pendant la négociation. Le script `negociation.py` contrôle l'effet déclaré contre la table ci-dessous.

| Voie | Effet | Texte |
| --- | --- | --- |
| Recours gracieux ou hiérarchique formé dans le délai | interrompt le délai de recours contentieux ; les deux recours exercés dans le délai initial le prorogent jusqu'au rejet de l'un et de l'autre | CRPA, art. L. 411-2 |
| Recours gracieux ou hiérarchique après une médiation préalable obligatoire | n'interrompt pas de nouveau le délai | CJA, art. R. 213-13 |
| Médiation administrative à l'initiative des parties, hors juridiction | interrompt les délais de recours contentieux et suspend les prescriptions, du jour où les parties conviennent de recourir à la médiation ou, sans écrit, de la première réunion ; reprise à la déclaration de fin ; prescription reprise pour six mois au moins | CJA, art. L. 213-6 ; CRPA, art. L. 421-3 (médiations engagées depuis le 26 mai 2026, loi n° 2026-403, art. 25, VII) |
| Médiation préalable obligatoire | la saisine du médiateur compétent interrompt le délai de recours et suspend la prescription jusqu'à la déclaration non équivoque de fin | CJA, art. L. 213-13, R. 213-11 |
| Saisine du Défenseur des droits | n'interrompt ni ne suspend par elle-même aucun délai, civil, administratif ou pénal, ni ceux des recours administratifs ou contentieux | loi organique n° 2011-333, art. 6, al. 3 |
| Saisine du Défenseur des droits sur une décision soumise à médiation préalable obligatoire | mêmes effets que la saisine du médiateur compétent | CJA, art. L. 213-14, R. 213-11 |
| Médiation menée par le Défenseur des droits | mêmes effets que la médiation hors juridiction (interruption des délais de recours) | CRPA, art. L. 424-2, depuis le 28 mai 2026 |
| Médiation ou conciliation civile | suspend la prescription du jour de l'accord de recourir à la médiation ou à la conciliation ou, sans écrit, de la première réunion ; reprise pour six mois au moins | C. civ., art. 2238 |
| Convention de procédure participative | suspend la prescription jusqu'au terme de la convention ; tant qu'elle est en cours, rend irrecevable la saisine du juge sur le litige, sauf inexécution et sauf mesures provisoires ou conservatoires en cas d'urgence | C. civ., art. 2238, 2065 |
| Convocation à une audience de règlement amiable | interrompt le délai de péremption de l'instance | CPC, art. 1532, al. 3 |
| Pourparlers directs, échange de lettres, offre de transaction | aucun texte ne leur attache d'effet sur un délai | absence de texte (inférence) |

Preuve. Textes lus en entier dans leur version en vigueur : CRPA, art. L. 411-2 (version du 1er janvier 2016), L. 421-3 et L. 424-2 (version du 28 mai 2026) ; CJA, art. L. 213-6 (version du 20 novembre 2016), L. 213-13 et L. 213-14 (24 décembre 2021), R. 213-10 à R. 213-13 (28 mars 2022) ; loi organique n° 2011-333, art. 6 (version du 23 mars 2022) ; C. civ., art. 2238 (version du 1er octobre 2016) et 2065 (20 novembre 2016) ; CPC, art. 1532 (1er septembre 2025) ; loi n° 2026-403, art. 25.

Statut. Droit positif. Deux points restent fragiles et se traitent par prudence : l'article 2238 du code civil vise la prescription, pas les délais de forclusion ni les délais de recours, qu'aucune médiation civile ne suspend ; la date à laquelle le Défenseur des droits « procède » à une médiation au sens de l'article L. 424-2 n'est fixée par aucun texte lu, de sorte que sa saisine ne protège jamais à elle seule un délai.

**D2. Une voie amiable sans effet sur le délai ne se mène jamais seule quand un délai court.**

Acte. Si le client négocie directement, saisit le Défenseur des droits ou un médiateur dont la saisine n'a pas d'effet légal sur le délai, le plan date l'acte conservatoire au plus tard la veille de l'échéance recalculée par `voies.py`, et la négociation continue en parallèle. Le négociateur ne laisse jamais l'adversaire ou un tiers fixer un calendrier qui passe l'échéance.

Preuve. Règle D1 et ses textes.

Statut. Inférence tirée du droit positif.


## 2. Préalables amiables obligatoires

**D3. Devant le tribunal judiciaire, certaines demandes sont irrecevables sans tentative préalable de conciliation, de médiation ou de procédure participative.**

Acte. Avant toute assignation ou requête devant le tribunal judiciaire, le plan vérifie si la demande tend au paiement d'une somme n'excédant pas 5 000 euros, relève des actions des articles R. 211-3-4 et R. 211-3-8 du code de l'organisation judiciaire ou porte sur un trouble anormal de voisinage. Si oui, il retient une tentative (conciliateur de justice, médiation ou procédure participative) ou il établit, pièce à l'appui, l'une des cinq dispenses : demande d'homologation d'un accord ; recours préalable imposé auprès de l'auteur de la décision ; motif légitime (urgence manifeste, circonstances rendant la tentative impossible ou exigeant une décision non contradictoire, indisponibilité des conciliateurs portant la première réunion au-delà de trois mois de la saisine, justifiée par tout moyen) ; tentative préalable de conciliation imposée au juge ou à l'autorité administrative ; échec de la procédure simplifiée de recouvrement des petites créances. L'acte introductif mentionne, à peine de nullité, les diligences entreprises en vue d'une résolution amiable ou la justification de la dispense.

Preuve. CPC, art. 750-1 (version issue du décret n° 2023-357 du 11 mai 2023, applicable aux instances introduites depuis le 1er octobre 2023, lu en entier ; l'irrecevabilité peut être prononcée d'office) ; CPC, art. 54, 5° (version du 1er janvier 2021, lu en entier).

Statut. Droit positif. Le juge simulé se trompait sur cet article lors des mesures (`docs/MISE_AU_NIVEAU_2.md`).

**D4. Certains recours administratifs individuels sont irrecevables sans médiation préalable.**

Acte. Avant toute requête d'un agent public ou d'un demandeur d'emploi contre une décision individuelle, le plan vérifie si la décision figure sur les listes réglementaires. Pour les agents publics (décret n° 2022-433 du 25 mars 2022, art. 2 à 4) : éléments de rémunération, refus de détachement, de disponibilité ou de congé non rémunéré, réintégration, classement après avancement ou promotion interne, formation professionnelle, mesures appropriées pour les travailleurs handicapés, aménagement des conditions de travail ; dans les académies listées par arrêté et dans les collectivités qui ont conventionné avec leur centre de gestion. Pour France Travail (C. trav., art. R. 5312-47 et R. 5312-48, créés par l'article 5 du même décret) : décisions de cessation d'inscription, de radiation, de suppression du revenu de remplacement, de pénalité administrative, de remboursement d'indus et certaines allocations versées pour l'État. La médiation s'engage dans le délai de recours contentieux, avec la décision ou, si elle est implicite, la demande et son accusé de réception. Si la notification ne mentionne pas l'obligation et les coordonnées du médiateur, le délai ne court pas. Une requête qui saute la médiation est rejetée par ordonnance et transmise au médiateur, réputé saisi à la date d'enregistrement : le délai est sauf, le temps est perdu.

Preuve. CJA, art. L. 213-11 à L. 213-14, R. 213-10 à R. 213-13 (lus en entier) ; décret n° 2022-433 du 25 mars 2022, art. 2, 3, 4, 5 et 6 (lus en entier).

Statut. Droit positif. La liste des académies concernées (arrêté) et celle des collectivités conventionnées n'ont pas été lues : à vérifier pour chaque affaire.

**D5. En plein contentieux pécuniaire, la demande préalable est le premier écrit de la négociation.**

Acte. Quand la requête tendra au paiement d'une somme, la demande préalable à l'administration est obligatoire. Le plan la rédige comme une offre motivée (N11, N12, P18 à P20) : fondement, calcul par chef de préjudice, pièces, demande chiffrée défendable devant le juge, délai de réponse, et suite contentieuse annoncée sobrement (N3). Son silence pendant deux mois fait naître la décision qui lie le contentieux.

Preuve. CJA, art. R. 421-1, al. 2 (version du 1er janvier 2020, lu en entier).

Statut. Droit positif pour l'obligation ; inférence pour la manière de la rédiger.

**D6. Consommation : pas de médiateur de la consommation sans réclamation écrite préalable, ni plus d'un an après elle.**

Acte. Le plan date la réclamation écrite au professionnel ; il saisit le médiateur moins d'un an après. Il sait que le médiateur refuse un litige déjà examiné par un autre médiateur ou par un tribunal.

Preuve. C. consom., art. L. 612-2 (version du 1er juillet 2016, lu en entier).

Statut. Droit positif.

**D7. Prud'hommes : l'accord de conciliation sur le barème vaut renonciation à toutes les réclamations relatives à la rupture.**

Acte. Devant le bureau de conciliation et d'orientation, l'indemnité forfaitaire du barème s'ajoute aux indemnités légales, conventionnelles ou contractuelles ; le procès-verbal d'accord vaut renonciation des parties à toutes réclamations et indemnités relatives à la rupture prévues au chapitre V du titre III du livre II de la première partie du code du travail. Le plan chiffre cette renonciation comme une contrepartie et vérifie qu'aucune demande étrangère à la rupture (rappel de salaire, heures supplémentaires) n'est abandonnée sans prix.

Preuve. C. trav., art. L. 1235-1 (version du 24 septembre 2017, lu en entier). Le barème réglementaire n'a pas été lu.

Statut. Droit positif ; inférence pour l'acte.


## 3. Transaction, accord et homologation

**D8. La transaction exige des concessions réciproques et un écrit ; elle éteint l'action qui a le même objet.**

Acte. Tout accord qui termine ou prévient une contestation est rédigé par écrit, nomme ce que chaque partie abandonne et ce qu'elle reçoit, et délimite l'objet couvert : la transaction fera obstacle à toute action ayant le même objet. L'accord issu d'une médiation, d'une conciliation ou d'une procédure participative obéit au droit commun des contrats et peut être homologué même s'il n'est pas une transaction ; un accord né d'une négociation directe ne s'homologue que s'il est une transaction. Il ne porte que sur des droits dont les parties ont la libre disposition.

Preuve. C. civ., art. 2044 et 2052 (version du 20 novembre 2016, lus en entier) ; CPC, art. 1528-2, 1541, 1541-1 (version du 1er septembre 2025, lus en entier) ; CJA, art. L. 213-3.

Statut. Droit positif.

**D9. Avec une administration, la transaction est licite sous condition d'objet licite et de concessions réciproques et équilibrées ; au-delà de 500 000 euros, l'État doit recueillir l'avis d'un comité.**

Acte. Le plan identifie qui peut engager la personne publique, par quelle délégation, après quelle délibération ou approbation. Pour une administration de l'État, il demande si le principe et le montant de la transaction ont été soumis au comité ministériel de transaction : l'avis est obligatoire au-delà de 500 000 euros et, quand le signataire l'a suivi, sa responsabilité personnelle ne peut être recherchée à raison du principe et du montant, sauf responsabilité pénale. En dessous du seuil, proposer la saisine du comité donne au signataire la couverture qui lui permet de signer (N27, N37).

Preuve. CRPA, art. L. 423-1 (version du 1er janvier 2016) et L. 423-2 (version du 12 août 2018), R. 423-3 (version du 1er février 2019, seuil de 500 000 euros), lus en entier.

Statut. Droit positif ; inférence pour l'usage du comité sous le seuil.

**D10. Une personne publique ne paie jamais ce qu'elle ne doit pas : chaque somme d'un accord porte son fondement et son calcul.**

Acte. Dans tout accord où une personne publique verse une somme ou renonce à la percevoir, le plan fait écrire : la règle ou la décision qui rend la somme due dans son principe (faute établie, décision juridictionnelle devenue définitive, texte), le calcul par chef de préjudice avec ses pièces, l'exclusion des chefs non indemnisables, et la contrepartie que constitue la renonciation à l'instance en cours et à toute action ayant le même objet. Les concessions s'apprécient globalement : un seul chef non indemnisable payé peut faire de l'ensemble une libéralité.

Preuve. CE, Section, 19 mars 1971, Mergui, n° 79962 (analyse lue) : les personnes publiques ne peuvent jamais être condamnées à payer une somme qu'elles ne doivent pas ; la règle est d'ordre public et relevée d'office ; le juge ne donne acte d'un accord que s'il ne méconnaît aucune règle d'ordre public. CE, 9 décembre 2016, Société Foncière Europe, n° 391840, mentionné aux tables (analyse lue) : appréciation globale des concessions ; 300 000 euros versés au titre d'un manque à gagner non indemnisable rendent la transaction constitutive d'une libéralité dans son ensemble. CE, Section, 17 juin 2026, n° 489764, publié au recueil (texte lu) : le juge de l'homologation d'un accord issu d'une médiation contrôle la capacité, le consentement effectif, l'absence d'atteinte à des droits indisponibles et le respect de l'ordre public ; il tient compte des intérêts des parties et de l'intérêt général, y compris celui de mettre fin à l'instance et de renoncer à de nouvelles actions ; une somme versée par la personne publique n'est une libéralité qu'en cas de disproportion manifeste au regard de l'objet du litige et des contreparties, parmi lesquelles la renonciation à la procédure.

Statut. Droit positif.

**D11. L'homologation se prépare comme un contrôle juridictionnel ; son refus annule la transaction et renvoie au fond.**

Acte. Le plan décide si l'accord sera soumis à homologation, à quel juge et à quel moment, au regard de ce qu'elle apporte (force exécutoire, sécurité contre le comptable public, fin de l'instance) et de ce qu'elle expose (contrôle de la libéralité par un juge qui connaît le fond et peut ne pas partager l'analyse de la dette). Il rédige l'accord pour ce contrôle (D10). Il prévoit la clause qui règle l'échec de l'homologation : désistement subordonné à l'homologation, maintien des conclusions au fond, ou nouvel accord. Le refus d'homologation et le jugement au fond peuvent tomber dans la même décision : avant de demander l'homologation, le dossier au fond est complet, y compris la réponse écrite au motif qui fonderait le refus (en matière de responsabilité, la décision juridictionnelle qui établit l'illégalité et l'autorité de chose jugée de ses motifs). Devant le juge administratif, une transaction est exécutoire de plein droit, même au regard des règles de la comptabilité publique ; l'homologation est recevable en cours d'instance, y compris en cassation, et hors instance seulement dans les cas où l'intérêt général l'exige (illégalité non régularisable, difficulté particulière d'exécution) ; le contrat soumis à l'approbation d'une assemblée délibérante ou à la transmission au préfet ne s'homologue qu'après. Devant le juge judiciaire, la requête va au juge déjà saisi ou à celui qui aurait été compétent ; il vérifie la licéité de l'objet et l'ordre public et ne peut modifier l'accord ; son refus est motivé et susceptible d'appel. L'acte d'accord contresigné par les avocats de chaque partie peut recevoir la formule exécutoire du greffe.

Preuve. CE, Assemblée, avis, 6 décembre 2002, Syndicat intercommunal des établissements du second cycle du second degré du district de L'Haÿ-les-Roses, n° 249153, publié (analyse lue) ; CE, Assemblée, 11 juillet 2008, Krupp Hazemag, n° 287354, publié (analyse lue : homologation possible en cassation ; homologation, puis non-lieu ou acte du désistement subordonné ; le refus d'homologation entraîne la nullité de la transaction et le juge statue sur la requête) ; CE, 10 février 2014, SA Gecina, n° 350265, mentionné aux tables (analyse lue : le consentement à la transaction s'établit par tout élément, y compris la signature de la lettre qui transmettait le protocole, ce qui impose de ne rien signer qui vaille acceptation avant la décision du client) ; CJA, art. L. 213-4 ; CPC, art. 1542, 1543, 1544, 1545, 1545-1, 1546 (version du 1er septembre 2025, lus en entier).

Statut. Droit positif. L'épreuve du module (`docs/epreuves/negociation.md`) porte sur une affaire où l'homologation a été refusée en première instance puis prononcée par le Conseil d'État.


## 4. Médiation, conciliation, audience de règlement amiable, procédure participative

**D12. Le juge civil a pour mission de concilier ; il peut convoquer à une audience de règlement amiable ou enjoindre de rencontrer un médiateur.**

Acte. Le plan dit, à chaque tournant de l'instance civile, s'il faut demander une audience de règlement amiable ou une médiation, et pourquoi. L'audience de règlement amiable est tenue par un juge qui ne siège pas dans la formation de jugement ; elle est décidée à la demande d'une partie ou d'office, par mesure d'administration judiciaire, ne dessaisit pas le juge et n'existe pas devant le conseil de prud'hommes ; elle vise la confrontation équilibrée des points de vue, l'évaluation des besoins, positions et intérêts, et la compréhension des principes juridiques applicables ; ses extraits de procès-verbal d'accord valent titre exécutoire. Depuis le 1er octobre 2026, la décision qui enjoint de rencontrer un conciliateur ou un médiateur peut aussi ordonner la mesure, sous réserve du consentement recueilli par lui. Demander une audience de règlement amiable sert quand l'évaluation du droit par un juge peut déplacer l'adversaire (N33, P22) ; la refuser ou la laisser ordonner sans préparation coûte une ancre (N17).

Preuve. CPC, art. 21 (version du 1er septembre 2025), 1528, 1528-1, 1532 à 1532-3 (1er septembre 2025), 1533 (version du 1er octobre 2026, décret n° 2026-683 du 27 juillet 2026), lus en entier ou dans les passages cités par LibreJustice pour 1532-1 à 1532-3.

Statut. Droit positif ; inférence pour l'usage tactique.

**D13. Le juge administratif peut ordonner une médiation avec l'accord des parties, et ses frais se partagent.**

Acte. Saisi, le tribunal ou la cour peut ordonner une médiation après accord des parties ; les décisions sur la médiation et ses frais sont insusceptibles de recours ; à défaut d'accord, les frais se partagent par moitié sauf iniquité ; la désignation devient caduque faute de consignation de la provision et l'instance reprend ; le médiateur informe seulement le juge de l'existence ou non d'un accord. Hors instance, les parties peuvent organiser la médiation ou demander au président du tribunal administratif ou de la cour de l'organiser. Le plan prévoit, avant d'accepter, qui paie, qui signe pour l'administration (D9) et ce qui sera demandé au juge à l'issue (D11).

Preuve. CJA, art. L. 213-1 à L. 213-10 (lus en entier).

Statut. Droit positif.

**D14. La procédure participative ferme le prétoire pendant sa durée.**

Acte. Une convention de procédure participative conclue avant la saisine du juge rend irrecevable toute action au fond pendant sa durée, sauf inexécution par l'autre partie ; seules des mesures provisoires ou conservatoires restent possibles en urgence. Le plan ne la propose pas quand un délai de forclusion court ou quand une mesure autre que provisoire peut devenir nécessaire.

Preuve. C. civ., art. 2062 et 2065 (version du 20 novembre 2016, lus en entier) ; art. 2238 pour la suspension de la prescription.

Statut. Droit positif ; inférence pour l'acte.


## 5. Confidentialité

**D15. Ce qui se dit en médiation, en conciliation et en audience de règlement amiable est confidentiel ; les pièces qu'on y produit ne le sont pas.**

Acte. Le plan classe chaque échange selon son régime. En médiation et en conciliation par un conciliateur, en audience de règlement amiable, tout ce qui est dit, écrit ou fait est confidentiel sauf accord contraire, ainsi que les pièces élaborées pour le processus ; les pièces produites ne sont pas couvertes. Devant le juge administratif, les constatations du médiateur et les déclarations recueillies ne peuvent être produites sans l'accord des parties. Les correspondances entre avocats sont couvertes par le secret, sauf celles qui portent la mention « officielle ». Une lettre d'une partie elle-même à son adversaire ou à une administration n'a aucune protection : elle est une pièce. Conséquences : aucune pièce que le juge ne doit pas voir n'est produite en médiation ; aucune lettre directe ne contient un aveu, une faiblesse ou un chiffre de repli (N4, N36) ; la mention « officielle » se décide lettre par lettre ; une proposition faite en médiation n'est jamais citée dans un écrit au juge.

Preuve. CPC, art. 1528-3 (version du 1er septembre 2025, lu en entier) ; loi n° 95-125 du 8 février 1995, art. 21-3 (version du 18 novembre 2011, lu en entier) ; CJA, art. L. 213-2 (lu en entier) ; loi organique n° 2011-333, art. 26 (lu en entier) pour la médiation du Défenseur des droits ; loi n° 71-1130 du 31 décembre 1971, art. 66-5 (version du 30 mars 2011, lu en entier).

Statut. Droit positif ; aucune règle générale lue ne rend confidentiels les pourparlers directs hors de ces cadres (inférence tirée de l'absence de texte).


## 6. Médiateurs institutionnels et Défenseur des droits

**D16. Le Défenseur des droits est un levier de persuasion et de médiation, jamais une protection des délais.**

Acte. Le plan distingue trois usages. La médiation du Défenseur des droits, confidentielle, qui depuis le 28 mai 2026 interrompt les délais de recours comme une médiation administrative (D1), à condition qu'elle soit engagée ; la transaction qu'il peut proposer et recommander, et, en matière de discrimination, l'amende transactionnelle homologuée par le procureur de la République ; ses observations devant les juridictions, qu'il peut demander à présenter et qui sont alors de droit, et que le juge peut solliciter : c'est un instrument de persuasion du juge, à prévoir dans le plan de persuasion. Sa saisine exige des démarches préalables auprès de l'organisme mis en cause, sauf pour certaines compétences, et ne protège aucun délai par elle-même.

Preuve. Loi organique n° 2011-333 du 29 mars 2011, art. 6 (version du 23 mars 2022), 26, 28 et 33 (version du 31 mars 2011), lus en entier ; CRPA, art. L. 424-2.

Statut. Droit positif. L'article 4 (compétences) n'a pas été relu.

**D17. L'administration de l'État doit offrir un médiateur dans des domaines fixés par décret.**

Acte. Avant de négocier avec une administration de l'État, le plan vérifie si elle dispose d'un médiateur au sens de l'article L. 421-2 du CRPA, soumis aux règles d'impartialité et de confidentialité du CJA, et si sa saisine relève de l'article L. 421-3. Les collectivités territoriales et leurs groupements relèvent d'un autre régime (CGCT, art. L. 1112-24, non lu).

Preuve. CRPA, art. L. 421-1 à L. 421-3 (version du 28 mai 2026, lus en entier). Le décret d'application de l'article L. 421-2 n'a pas été trouvé ni lu : non vérifié.

Statut. Droit positif pour le principe ; domaines non vérifiés.


## 7. Amiable pénal et fiscal

**D18. En pénal, le procureur peut faire réparer ou proposer une médiation avant de décider ; ces mesures suspendent la prescription de l'action publique.**

Acte. Pour une victime, le plan considère la demande de réparation ou de médiation au procureur (procès-verbal signé ; l'engagement de payer se recouvre par injonction de payer), et sait qu'aucune médiation n'est possible pour des violences au sein du couple. Pour un mis en cause, il compare ces mesures avec la suite probable. La composition pénale, la convention judiciaire d'intérêt public et la comparution sur reconnaissance préalable de culpabilité n'ont pas été lues pour ce module : aucune règle sans lecture préalable.

Preuve. CPP, art. 41-1 (version du 28 novembre 2023, lu en entier ; réécrit par l'ordonnance n° 2025-1091 du 19 novembre 2025 à compter du 1er janvier 2029).

Statut. Droit positif.

**D19. En fiscal, l'administration transige sur les pénalités non définitives, pas sur l'impôt.**

Acte. Le plan distingue remise gracieuse (gêne ou indigence pour les impôts directs, pénalités définitives) et transaction (atténuation d'amendes ou de majorations non définitives). Il sait que certaines impositions ne peuvent faire l'objet d'aucune remise et que l'administration ne transige pas en présence de manœuvres dilatoires. La transaction se négocie avant que les pénalités deviennent définitives.

Preuve. LPF, art. L. 247 (version du 2 juin 2024, en vigueur jusqu'au 31 décembre 2026, lu en entier ; nouvelle version au 1er janvier 2027, non lue).

Statut. Droit positif.


## 8. Non lu, à lire avant usage

- Décret d'application de l'article L. 421-2 du CRPA (domaines des médiateurs de l'État).
- Article L. 1112-24 du CGCT (médiation territoriale).
- Barème de l'article L. 1235-1 du code du travail (article D. 1235-21).
- Composition pénale (CPP, art. 41-2), convention judiciaire d'intérêt public (art. 41-1-2), comparution sur reconnaissance préalable de culpabilité (art. 495-7 et suivants).
- Comités consultatifs de règlement amiable de la commande publique ; commissions de recours amiable de la sécurité sociale ; conciliation et mandat ad hoc du code de commerce.
- Circulaires du Premier ministre du 6 février 1995 et du 6 avril 2011 sur la transaction : connues par les lecteurs délégués des fichiers N et P, vigueur non confirmée.
- Conclusions du rapporteur public sur CE, Section, 17 juin 2026, n° 489764 (ArianeWeb).

## 9. Sources lues

| Source | Version ou date | Lecture |
| --- | --- | --- |
| CRPA, art. L. 411-2, L. 421-1 à L. 421-3, L. 422-1, L. 422-2, L. 423-1, L. 423-2, L. 424-2, R. 423-3 | en vigueur au 18 novembre 2026 | lus en entier |
| CJA, art. L. 213-1 à L. 213-14, R. 213-10 à R. 213-13, R. 421-1, R. 741-12 | idem | lus en entier |
| Décret n° 2022-433 du 25 mars 2022, art. 2 à 6 | idem | lus en entier |
| Loi n° 2026-403 du 26 mai 2026, art. 25 | idem | lu en entier |
| C. civ., art. 2044, 2052, 2062, 2065, 2238 | idem | lus en entier |
| CPC, art. 21, 32-1, 54, 750-1, 1528 à 1529, 1532, 1533, 1541 à 1548 | idem | lus en entier |
| CPC, art. 1532-1 à 1532-3, 1534-1, 1534-2, 1530-2, 1535-6 | idem | extraits lus |
| Loi n° 95-125 du 8 février 1995, art. 21-3 | idem | lu en entier |
| Loi organique n° 2011-333, art. 6, 26, 28, 33 | idem | lus en entier |
| Loi n° 71-1130 du 31 décembre 1971, art. 66-5 | idem | lu en entier |
| C. consom., art. L. 612-2 ; C. trav., art. L. 1235-1 | idem | lus en entier |
| CPP, art. 41-1 ; LPF, art. L. 247 | versions citées | lus en entier |
| CE, Section, 19 mars 1971, Mergui, n° 79962 | | analyse lue |
| CE, Assemblée, avis, 6 décembre 2002, n° 249153 | | analyse lue |
| CE, Assemblée, 11 juillet 2008, Krupp Hazemag, n° 287354 | | analyse lue |
| CE, 10 février 2014, SA Gecina, n° 350265 | | analyse lue |
| CE, 9 décembre 2016, Société Foncière Europe, n° 391840 | | analyse lue |
| CE, Section, 17 juin 2026, n° 489764 | | texte lu |
| TA Nice, 27 septembre 2023, n° 2104672 | | texte lu |
