# Procédure pénale, requête à la Cour européenne des droits de l'homme et question prioritaire de constitutionnalité

Ce référentiel sert au contrôle avant dépôt des actes de la victime et de la défense en matière pénale, des requêtes devant la Cour européenne des droits de l'homme et des questions prioritaires de constitutionnalité. Pour chaque procédure, il indique la juridiction, l'acte introductif, les préalables, les délais, la représentation, les conditions de recevabilité, les motifs fréquents de rejet sans examen au fond et les voies de recours.

Vérification arrêtée le 18 novembre 2026. Les articles du code de procédure pénale (CPP), du code de procédure civile (CPC), du code de justice administrative (CJA), de la Constitution, de l'ordonnance n° 58-1067 du 7 novembre 1958 et de la loi du 29 juillet 1881 ont été lus sur LibreJustice dans leur version en vigueur à cette date, chaque fiche renvoyant à sa source Légifrance. La Convention européenne des droits de l'homme a été lue sur LibreJustice et dans l'édition officielle publiée par la Cour ; le Protocole n° 15 et le Règlement de la Cour (édition du 15 septembre 2025) ont été lus dans les documents officiels publiés sur echr.coe.int. Une décision n'est citée qu'après lecture de son texte intégral ; son statut de publication est indiqué. Ce qui n'a pas pu être vérifié est signalé « non vérifié ».

Les fichiers associés sont `penal_cedh_qpc_regimes.json` (conditions par type d'acte) et `penal_cedh_qpc_voies.json` (règles de délai).

## 1. Versions applicables

Le code de procédure pénale est en cours de recodification. L'article 1er de l'ordonnance n° 2025-1091 du 19 novembre 2025 remplace le titre préliminaire et les livres I à VI de la partie législative du code par un texte annexé. Les fiches Légifrance des articles cités ici portent le statut « abrogation différée » avec effet au 1er janvier 2029. Jusqu'au 31 décembre 2028, les numéros d'articles ci-dessous restent ceux du droit positif ; au-delà, chaque référence devra être reprise dans la nouvelle numérotation, qui n'a pas été vérifiée.

Plusieurs textes ont changé récemment. La version applicable est celle en vigueur à la date de l'acte ; elle se vérifie avec `get_norm` et le paramètre `as_of`.

- Loi n° 2026-651 du 23 juillet 2026, entrée en vigueur sur ces points le 23 octobre 2026 : le délai de forclusion de l'article 173-1 passe de six à quatre mois pour les requêtes formées à compter de cette date ; l'article 385 impose le dépôt des conclusions écrites de nullité au greffe trois jours avant l'audience ; le délai minimal de citation de l'article 552 passe de dix à quinze jours.
- Loi n° 2023-1059 du 20 novembre 2023 : depuis le 30 septembre 2024, le délai de pourvoi de l'article 568 est de dix jours francs ; il était de cinq jours francs dans la version antérieure, lue au 1er septembre 2024.
- L'article 10 dispose d'une nouvelle rédaction annoncée au 1er janvier 2027, dont le texte n'a pas été lu.
- Le délai de requête devant la Cour européenne est de quatre mois pour les décisions internes définitives prises à compter du 1er février 2022 et de six mois pour les décisions antérieures (section 11).

## 2. Computation des délais en matière pénale

L'article 801 du CPP dispose que tout délai prévu pour l'accomplissement d'un acte ou d'une formalité expire le dernier jour à vingt-quatre heures, et que le délai qui expirerait un samedi, un dimanche ou un jour férié ou chômé est prorogé jusqu'au premier jour ouvrable suivant.

Le jour qui fait courir le délai n'est pas compté. La chambre criminelle l'a jugé pour le délai d'appel de dix jours de l'article 498 : le jour du jugement ou de la signification est écarté et le délai prend fin le dixième jour à minuit, de sorte que l'appel formé le onzième jour est tardif (Crim., 30 janvier 1973, n° 72-92.400, publié au Bulletin, lu en entier ; https://librejustice.fr/decision/ool-72bzWNWx). Pour l'appel d'une ordonnance du juge d'instruction notifiée par lettre recommandée, le délai court du lendemain de l'expédition de la lettre (Crim., 27 mars 1995, n° 94-82.758, publié au Bulletin, lu en entier ; https://librejustice.fr/decision/tczGvjLzoAaI). Cet arrêt situe la fin du délai « à la fermeture des services du greffe », alors que l'article 801 vise vingt-quatre heures ; la déclaration doit donc être faite pendant les heures d'ouverture du greffe.

Le mode de calcul des « jours francs » de l'article 568 n'est précisé par aucun des textes lus ; la date prudente est le dixième jour suivant le prononcé, et la date qui ajouterait un jour au titre du caractère franc n'a pas été vérifiée.

## 3. Plainte simple et recours contre le classement sans suite

Autorité saisie. Le procureur de la République reçoit les plaintes et apprécie la suite à leur donner (CPP, art. 40, al. 1). Les officiers et agents de police judiciaire sont tenus de recevoir les plaintes des victimes, même lorsque le service est territorialement incompétent ; tout dépôt de plainte fait l'objet d'un procès-verbal et donne lieu à la délivrance immédiate d'un récépissé qui mentionne les délais de prescription de l'action publique et la possibilité de les interrompre par une plainte avec constitution de partie civile (CPP, art. 15-3, version du 20 août 2026).

Acte. Aucune mention obligatoire de la plainte simple n'est fixée par les textes lus. Lorsque la plainte doit préparer une plainte avec constitution de partie civile, elle doit être déposée devant le procureur contre récépissé ou par lettre recommandée avec demande d'avis de réception, ou, si elle est déposée devant un service de police judiciaire, sa copie doit être adressée au procureur selon les mêmes modalités (CPP, art. 85, al. 2 ; section 4).

Suites. Le procureur décide d'engager des poursuites, de mettre en œuvre une procédure alternative ou de classer sans suite (CPP, art. 40-1).

Recours. Toute personne ayant dénoncé des faits au procureur peut former un recours auprès du procureur général contre la décision de classement sans suite ; le procureur général peut enjoindre d'engager des poursuites ou informe l'intéressé que le recours est infondé (CPP, art. 40-3). L'article 40-3 ne fixe pas de délai.

Prescription. La plainte simple ne figure pas parmi les actes de la partie civile énumérés au 1° de l'article 9-2 et n'interrompt donc pas la prescription. Elle la suspend au profit de la victime, du dépôt de la plainte jusqu'à la réponse du procureur ou, au plus tard, jusqu'à l'expiration du délai de trois mois de l'article 85, alinéa 2, ce préalable constituant un obstacle de droit au sens de l'article 9-3 (Crim., 23 juin 2026, n° 25-87.950, publié au Bulletin, lu en entier le 20 novembre 2026). La suspension tient à ce préalable ; elle ne peut donc jouer là où l'article 85 ne l'exige pas (crimes, délits de presse, délits électoraux énumérés), déduction qu'aucune décision lue n'énonce.

## 4. Plainte avec constitution de partie civile

Juridiction. Le juge d'instruction compétent en application des articles 52, 52-1 et 706-42 du CPP (art. 85, al. 1). Ces trois articles de compétence n'ont pas été lus.

Acte et contenu. Toute personne qui se prétend lésée par un crime ou un délit peut, en portant plainte, se constituer partie civile (art. 85, al. 1). L'action civile appartient à ceux qui ont personnellement souffert du dommage directement causé par l'infraction (art. 2). La plainte vise donc des faits qualifiables de crime ou de délit et un préjudice personnel et direct. La partie civile doit déclarer au juge d'instruction une adresse personnelle ou celle d'un tiers qui l'accepte ; à défaut, elle ne peut opposer le défaut de notification des actes (art. 89).

Préalable obligatoire. La plainte n'est recevable que si la personne justifie soit que le procureur lui a fait connaître, à la suite d'une plainte déposée devant lui ou devant un service de police judiciaire, qu'il n'engagera pas lui-même de poursuites, soit qu'un délai de trois mois s'est écoulé depuis qu'elle a déposé plainte devant ce magistrat contre récépissé ou par lettre recommandée avec avis de réception, ou depuis qu'elle lui a adressé selon les mêmes modalités copie de sa plainte déposée devant un service de police judiciaire (art. 85, al. 2). Cette condition n'est pas requise pour un crime, pour un délit prévu par la loi du 29 juillet 1881 ou pour certains délits du code électoral énumérés par le texte.

Option de voie. La partie qui a exercé son action devant la juridiction civile ne peut la porter devant la juridiction répressive, sauf saisine de celle-ci par le ministère public avant le jugement civil au fond (art. 5). Par dérogation, la victime qui a agi au civil pendant le délai de trois mois peut se constituer partie civile après s'être désistée de l'instance civile (art. 85, al. 3).

Personne morale à but lucratif. Sa plainte n'est recevable que si elle justifie de ses ressources en joignant bilan et compte de résultat (art. 85, al. 4).

Consignation. Le juge d'instruction constate le dépôt de la plainte par ordonnance, fixe en fonction des ressources le montant de la consignation que la partie civile doit déposer au greffe, sauf aide juridictionnelle, et le délai dans lequel elle doit être faite sous peine de non-recevabilité de la plainte ; il peut l'en dispenser (art. 88). La consignation garantit le paiement de l'amende civile de l'article 177-2 (art. 88-1). Un complément peut être ordonné en cas de demande d'expertise (art. 88-2).

Suite de la plainte. Le juge communique la plainte au procureur pour réquisitions (art. 86, al. 1). Le procureur ne peut requérir un refus d'informer que si, pour des causes affectant l'action publique elle-même, les faits ne peuvent légalement comporter une poursuite ou ne peuvent admettre aucune qualification pénale ; il peut requérir un non-lieu s'il est établi de façon manifeste que les faits n'ont pas été commis, ou un refus d'informer avec invitation à la citation directe dans le cas prévu par le texte (art. 86, al. 4). La constitution peut être contestée par le procureur ou une partie ; le juge statue par ordonnance motivée dont l'intéressé peut faire appel (art. 87).

Délais. Le délai de trois mois de l'article 85, alinéa 2, court du dépôt de la plainte simple contre récépissé ou de l'envoi recommandé. Le délai de consignation est celui fixé par l'ordonnance. La plainte doit être déposée avant l'expiration de la prescription de l'action publique (section 7). Son dépôt n'interrompt la prescription que si la consignation est versée dans le délai imparti ; la prescription est suspendue entre le dépôt de la plainte et le réquisitoire du procureur, la partie civile n'ayant aucun moyen de droit d'obliger le juge d'instruction à accomplir un acte interruptif (Crim., 8 mars 2022, n° 21-83.037, publié au Bulletin, lu en entier le 20 novembre 2026 ; art. 9-2, 1°, et 9-3).

Représentation. Aucun des articles lus n'impose le ministère d'avocat pour la plainte avec constitution de partie civile.

Motifs fréquents de rejet sans examen au fond. Absence de plainte préalable régulière ou délai de trois mois non écoulé (art. 85, al. 2) ; consignation non versée dans le délai (art. 88) ; prescription de l'action publique (art. 86, al. 4) ; faits de nature contraventionnelle (art. 85 vise le crime ou le délit) ; défaut de justification des ressources d'une personne morale à but lucratif (art. 85, al. 4).

Voies de recours. Appel par la partie civile des ordonnances de non-informer, de non-lieu et des ordonnances faisant grief à ses intérêts civils, ainsi que de l'ordonnance statuant sur la compétence, dans les dix jours de la notification ou de la signification, selon les formes des articles 502 et 503 ; le président de la chambre de l'instruction rend une ordonnance de non-admission, sans recours, si l'appel vise une ordonnance non mentionnée, s'il est tardif ou sans objet (art. 186). L'ordonnance d'irrecevabilité de la constitution est susceptible d'appel (art. 87, al. 3). Pourvoi contre l'arrêt de la chambre de l'instruction (art. 567 ; section 10).

## 5. Citation directe et consignation

Juridiction. Le tribunal correctionnel est saisi notamment par la citation (art. 388) ; la citation peut viser le tribunal de police (art. 551 et 552).

Acte et mentions. La citation est délivrée à la requête de la partie civile par huissier, qui doit déférer sans délai à la réquisition. Elle énonce le fait poursuivi et vise le texte de loi qui le réprime ; elle indique le tribunal saisi, le lieu, l'heure et la date de l'audience et la qualité de la personne citée ; délivrée à la requête de la partie civile, elle mentionne, pour une personne physique, ses nom, prénoms, profession et domicile réel ou élu, et pour une personne morale sa forme, sa dénomination, son siège et l'organe qui la représente (art. 551). La partie civile fait élection de domicile dans le ressort du tribunal saisi, sauf si elle y est domiciliée (art. 392). Le terme « huissier » est celui du texte en vigueur lu ; la terminologie de commissaire de justice n'a pas été vérifiée dans ce code.

Délai de citation. Entre la délivrance de la citation et la comparution devant le tribunal correctionnel ou de police, le délai est d'au moins quinze jours (art. 552, version en vigueur depuis le 23 octobre 2026 ; dix jours auparavant), augmenté d'un mois ou de deux mois selon les cas d'outre-mer ou de résidence à l'étranger prévus par le texte.

Consignation. Lorsque l'action de la partie civile n'est pas jointe à celle du ministère public, le tribunal fixe, en fonction des ressources, le montant de la consignation que la partie civile doit, sauf aide juridictionnelle, déposer au greffe, et le délai dans lequel elle doit être faite sous peine de non-recevabilité de la citation ; une personne morale à but lucratif doit produire son bilan et son compte de résultat, sous la même sanction ; la consignation versée sur une plainte ayant donné lieu au refus d'informer prévu à l'article 86 vaut consignation ; en cas de relaxe, le tribunal peut, sur réquisitions, prononcer une amende civile d'au plus 15 000 euros si la citation était abusive ou dilatoire (art. 392-1).

Le tribunal ne peut modifier ultérieurement les dispositions de son jugement fixant la consignation devenues définitives, et le défaut de versement avant l'expiration du délai initialement fixé rend la poursuite irrecevable, de sorte qu'un jugement accordant un nouveau délai n'interrompt pas la prescription (Crim., 18 décembre 2007, n° 07-82.106, publié au Bulletin, lu en entier ; https://librejustice.fr/decision/RIWuY98U-8rX). En raison de la tardiveté de la consignation, la citation directe est irrecevable et privée d'effet tant sur l'action publique que sur l'action civile (Crim., 10 mai 2000, n° 99-84.157, inédit, lu en entier ; https://librejustice.fr/decision/KS0an9Cx5FYg).

Représentation. L'article 418 dispense de l'avocat la constitution de partie civile à l'audience ; aucun des textes lus n'impose l'avocat pour la citation directe.

Motifs fréquents de rejet sans examen au fond. Consignation non versée dans le délai ; défaut de production du bilan d'une personne morale à but lucratif ; prescription, notamment en matière de presse (trois mois, loi du 29 juillet 1881, art. 65) ; mentions de l'article 551 manquantes ; délai de citation non respecté (art. 552).

Voies de recours. La partie civile ne peut faire appel du jugement que quant à ses intérêts civils (art. 497, 3°).

## 6. Constitution de partie civile à l'audience

Toute personne qui prétend avoir été lésée par un délit peut, si elle ne l'a déjà fait, se constituer partie civile à l'audience même ; le ministère d'un avocat n'est pas obligatoire ; elle peut demander des dommages-intérêts correspondant à son préjudice (art. 418). La recevabilité suppose le préjudice personnel et direct de l'article 2.

## 7. Prescription de l'action publique

Durées et points de départ. Crimes : vingt années révolues à compter du jour de l'infraction ; trente ans pour les crimes énumérés au deuxième alinéa ; trente ans à compter de la majorité pour les crimes de l'article 706-47 commis sur mineurs ; imprescriptibilité des crimes des articles 211-1 à 212-3 du code pénal (CPP, art. 7). Délits : six années révolues à compter du jour de l'infraction ; dix ou vingt ans à compter de la majorité pour les délits sur mineurs visés par le texte ; vingt ans pour les délits terroristes et assimilés énumérés (art. 8). Contraventions : une année révolue (art. 9). Infractions de presse : trois mois révolus à compter du jour de la commission ou du dernier acte d'instruction ou de poursuite ; avant l'engagement des poursuites, seules les réquisitions aux fins d'enquête, qui doivent articuler et qualifier les propos, sont interruptives (loi du 29 juillet 1881, art. 65).

Infraction occulte ou dissimulée. Le délai court du jour où l'infraction est apparue et a pu être constatée dans des conditions permettant l'exercice de l'action publique, sans pouvoir excéder douze ans pour les délits et trente ans pour les crimes à compter de la commission (art. 9-1).

Interruption. Interrompent la prescription les actes du ministère public ou de la partie civile tendant à la mise en mouvement de l'action publique prévus aux articles 80, 82, 87, 88, 388, 531 et 532 et à l'article 65 de la loi de 1881, les actes d'enquête du ministère public et procès-verbaux tendant effectivement à la recherche et à la poursuite des auteurs, les actes d'instruction de même nature, et tout jugement ou arrêt non entaché de nullité ; chaque acte fait courir un délai égal au délai initial (art. 9-2).

Suspension. Tout obstacle de droit prévu par la loi ou tout obstacle de fait insurmontable et assimilable à la force majeure qui rend impossible la mise en mouvement ou l'exercice de l'action publique suspend la prescription (art. 9-3).

Action civile. Exercée devant la juridiction répressive, elle se prescrit selon les règles de l'action publique (art. 10, al. 1).

## 8. Nullités et exceptions

### 8.1 Pendant l'instruction

Principe. Il y a nullité lorsque la méconnaissance d'une formalité substantielle a porté atteinte aux intérêts de la partie concernée (art. 171) ; toute juridiction, y compris la Cour de cassation, ne peut prononcer la nullité que si l'irrégularité a porté atteinte aux intérêts de la partie (art. 802).

Juridiction et acte. La partie ou le témoin assisté saisit la chambre de l'instruction par requête motivée ; à peine d'irrecevabilité, il en adresse copie au juge d'instruction et la requête fait l'objet d'une déclaration au greffe de la chambre de l'instruction, constatée, datée et signée ; la déclaration peut être faite par lettre recommandée si le demandeur ou son avocat ne réside pas dans le ressort, ou auprès du chef d'établissement pour une personne détenue (art. 173, al. 3). Ces règles ne s'appliquent pas aux actes susceptibles d'appel, notamment en matière de détention provisoire ou de contrôle judiciaire (art. 173, al. 4). Dans les huit jours de la réception du dossier, le président peut constater par ordonnance non susceptible de recours l'irrecevabilité de la requête pour les causes prévues, y compris le défaut de motivation (art. 173, al. 5).

Délais de forclusion. Pour les requêtes formées depuis le 23 octobre 2026, la personne mise en examen doit faire état des moyens de nullité des actes antérieurs à son interrogatoire de première comparution, ou de cet interrogatoire, dans un délai de quatre mois à compter de la délivrance de la première copie du dossier lorsqu'elle l'a demandée dans les sept jours francs de la mise en examen, ou à défaut dans les quatre mois de la notification de la mise en examen ; pour les actes postérieurs, le délai est de quatre mois à compter de chaque interrogatoire ultérieur ou de la notification des actes ; il en est de même pour le témoin assisté et la partie civile à compter de leurs auditions ; l'irrecevabilité est écartée lorsque la personne n'aurait pu connaître les moyens (art. 173-1). Dans la version antérieure, en vigueur jusqu'au 22 octobre 2026, le délai était de six mois à compter de la notification de la mise en examen.

Purge. Lorsque la chambre de l'instruction est saisie sur le fondement de l'article 173, tous les moyens de nullité de la procédure transmise doivent lui être proposés ; à défaut, les parties ne sont plus recevables à en faire état, sauf s'ils ne pouvaient être connus (art. 174). Après l'avis de fin d'information, les requêtes en nullité doivent être présentées dans le délai d'un mois si la personne est détenue, de trois mois dans les autres cas, à compter de l'envoi de l'avis ; elles ne sont plus recevables ensuite (art. 175, al. 3 et 4). Devenue définitive, l'ordonnance de renvoi devant le tribunal correctionnel couvre les vices de la procédure, sauf ceux que les parties n'auraient pu connaître (art. 179, dernier al.).

### 8.2 Devant le tribunal correctionnel

Saisi par renvoi de la juridiction d'instruction, le tribunal ne connaît que des moyens de nullité qui n'ont pu être connus avant la clôture de l'instruction ; si l'ordonnance ou l'arrêt de renvoi n'a pas été porté à la connaissance des parties dans les conditions prévues ou si l'ordonnance n'a pas été rendue conformément à l'article 184, il renvoie la procédure au ministère public aux fins de régularisation, sauf manœuvre ou négligence de la partie ; si l'ordonnance de renvoi a été rendue sans respect de l'article 175, les parties demeurent recevables à soulever les nullités ; saisi autrement que par renvoi, il statue sur les exceptions tirées de la nullité de la procédure antérieure ; dans tous les cas, les exceptions de nullité doivent être présentées avant toute défense au fond ; hors comparution immédiate, les conclusions écrites de nullité sont déposées au greffe trois jours avant la date prévue de l'audience, sous peine d'irrecevabilité, sauf si la partie n'aurait pu connaître ces nullités ou a été citée ou convoquée moins de vingt jours avant l'audience ; les parties sont avisées de la date d'audience au moins quinze jours avant (art. 385, version du 23 octobre 2026). La nullité de la citation relève de l'article 565, qui n'a pas été lu.

Représentation. L'article 173 admet la signature du demandeur ou de son avocat ; aucun des textes lus n'impose un avocat pour les conclusions de nullité devant le tribunal.

Motifs fréquents de rejet sans examen au fond. Forclusion de l'article 173-1 ; requête sans copie au juge d'instruction ou sans déclaration au greffe (art. 173) ; moyens non proposés lors d'une précédente saisine (art. 174) ; requête après l'expiration du délai de l'article 175 ; nullités purgées par l'ordonnance de renvoi (art. 179 et 385, al. 1) ; exception présentée après la défense au fond ou conclusions déposées hors délai (art. 385) ; absence de grief (art. 171 et 802).

Voies de recours. Pourvoi contre l'arrêt de la chambre de l'instruction statuant sur la nullité ; une requête tendant à faire déclarer le pourvoi immédiatement recevable peut être présentée au président de la chambre criminelle (art. 570 ; l'article 571, qui régit l'examen immédiat pour la chambre de l'instruction, n'a pas été lu).

## 9. Appel

### 9.1 Ordonnances du juge d'instruction

Appel de la partie civile contre les ordonnances de non-informer, de non-lieu et faisant grief à ses intérêts civils, à l'exclusion des dispositions relatives à la détention ou au contrôle judiciaire ; appel des parties contre l'ordonnance statuant sur la compétence ; délai de dix jours à compter de la notification ou de la signification ; formes des articles 502 et 503 ; non-admission d'office par le président de la chambre de l'instruction en cas d'ordonnance non visée, de tardiveté ou d'absence d'objet, sans recours (art. 186). Le délai court du lendemain de l'expédition de la lettre recommandée (Crim., 27 mars 1995, section 2).

### 9.2 Jugements correctionnels

Juridiction. La cour d'appel (art. 496).

Qualité. Peuvent appeler le prévenu, la personne civilement responsable et la partie civile quant à leurs intérêts civils seulement, le procureur de la République, les administrations exerçant l'action publique et le procureur général (art. 497).

Délai et point de départ. Dix jours à compter du prononcé du jugement contradictoire ; à compter de la signification pour la partie absente non informée de la date du prononcé après débat contradictoire, pour le prévenu jugé en son absence après audition d'un avocat sans mandat de représentation, pour le prévenu non comparant dans le cas de l'article 411, alinéa 5, sans avocat présent, et dans les cas des articles 410 et 494-1 sous réserve de l'article 498-1 (art. 498). Pour un jugement de condamnation à l'emprisonnement ferme ou avec sursis partiel rendu dans les conditions de l'article 410 et non signifié à personne, l'appel reste recevable jusqu'à la prescription de la peine si la connaissance de la signification n'est pas établie (art. 498-1). En cas d'appel d'une partie dans ces délais, les autres disposent de cinq jours supplémentaires (art. 500), ce qui ouvre un délai global de quinze jours après le prononcé du jugement contradictoire, prorogeable selon l'article 801 (Crim., 6 janvier 2009, n° 08-84.141, publié au Bulletin, lu en entier ; https://librejustice.fr/decision/8xvk1BZz9S9m). En cas de condamnation, le procureur général dispose de vingt jours à compter du prononcé et les autres parties de cinq jours pour un appel incident (art. 505).

Acte. Déclaration au greffier de la juridiction qui a rendu la décision ; elle indique si l'appel porte sur l'action publique, l'action civile ou les deux, et précise, pour l'action publique, l'éventuelle limitation aux peines ou à certaines infractions ; à défaut de précision, l'appel porte sur l'intégralité de la décision ; elle est signée par le greffier et par l'appelant, un avocat ou un fondé de pouvoir spécial dont le pouvoir est annexé (art. 502). L'appelant détenu peut déclarer l'appel auprès du chef d'établissement (art. 503).

Motifs fréquents de rejet sans examen au fond. Tardiveté (art. 498) ; défaut de qualité ou appel de la partie civile portant sur l'action publique (art. 497) ; déclaration irrégulière en la forme (art. 502).

### 9.3 Arrêts de cour d'assises

Les arrêts de condamnation rendus en premier ressort peuvent faire l'objet d'un appel porté devant une autre cour d'assises ou la même cour autrement composée (art. 380-1, version du 25 juillet 2026). L'appel appartient à l'accusé, au ministère public, à la personne civilement responsable et à la partie civile quant à leurs intérêts civils ; le procureur général peut faire appel des arrêts d'acquittement (art. 380-2). Délai de dix jours à compter du prononcé, ou de la signification pour la partie absente non informée de la date du prononcé (art. 380-9). Déclaration au greffe de la cour d'assises, signée par le greffier et l'appelant, un avocat ou un fondé de pouvoir spécial (art. 380-12).

### 9.4 Jugements de police

La faculté d'appel dépend de la classe de la contravention et de la peine prononcée ; la partie civile peut toujours appeler quant à ses intérêts civils (art. 546). Le délai d'appel des jugements de police (art. 547) n'a pas été lu : non vérifié.

## 10. Pourvoi en cassation en matière pénale

Juridiction et décisions attaquables. Les arrêts de la chambre de l'instruction et les arrêts et jugements rendus en dernier ressort en matière criminelle, correctionnelle et de police peuvent être annulés pour violation de la loi, sur pourvoi du ministère public ou de la partie à laquelle il est fait grief, devant la chambre criminelle (art. 567). Ils ne peuvent être cassés que pour violation de la loi (art. 591). L'arrêt de la chambre de l'instruction portant renvoi devant le tribunal correctionnel ou de police ne peut être attaqué que lorsqu'il statue sur la compétence ou présente des dispositions définitives que le tribunal n'a pas le pouvoir de modifier (art. 574). Une décision distincte de la décision au fond n'est immédiatement attaquable que si elle met fin à la procédure ; à défaut, le demandeur peut déposer au greffe, avant l'expiration du délai, une requête au président de la chambre criminelle tendant à faire déclarer son pourvoi immédiatement recevable (art. 570).

Pourvoi de la partie civile. L'article 567 ouvre le pourvoi à la partie à laquelle la décision fait grief. L'article 575, qui ne permettait à la partie civile de se pourvoir seule contre un arrêt de la chambre de l'instruction que dans sept cas, a été déclaré contraire à la Constitution ; son abrogation, effective le 24 juillet 2010, s'applique à toutes les instructions auxquelles il n'avait pas été mis fin par une décision définitive à la date de publication (Cons. const., 23 juillet 2010, n° 2010-15/23 QPC, lu en entier le 20 novembre 2026 ; CPP, art. 575, version abrogée).

Délai. Dix jours francs après celui où la décision a été prononcée ; à compter de la signification pour la partie absente non informée de la date du prononcé, pour le prévenu jugé en son absence après audition d'un avocat sans mandat, pour le prévenu non comparant dans les cas des articles 410 et 411, alinéa 5, et pour le prévenu jugé par itératif défaut ; contre les décisions par défaut, à l'égard du prévenu, du jour où elles ne sont plus susceptibles d'opposition (art. 568, version du 30 septembre 2024 ; cinq jours francs auparavant).

Acte. Déclaration au greffier de la juridiction qui a rendu la décision, signée par le greffier et par le demandeur, un avocat près la juridiction qui a statué ou un fondé de pouvoir spécial (art. 576).

Mémoire et représentation. Le demandeur peut déposer un mémoire signé par lui au greffe de la juridiction qui a rendu la décision, en faisant sa déclaration ou dans les dix jours suivants (art. 584). Après ce délai, le demandeur condamné pénalement peut transmettre son mémoire directement au greffe de la Cour de cassation ; les autres parties ne le peuvent que par le ministère d'un avocat à la Cour de cassation ; le mémoire est accompagné d'autant de copies que de parties (art. 585). Sauf dérogation, le mémoire du demandeur condamné pénalement doit parvenir au greffe de la Cour de cassation un mois au plus tard après la date du pourvoi, de même que la déclaration de l'avocat qui se constitue (art. 585-1). Les mémoires contiennent les moyens et visent les textes dont la violation est invoquée ; aucun mémoire additionnel ne peut être joint après le dépôt du rapport ; un mémoire tardif peut être déclaré irrecevable (art. 590). Le demandeur sans avocat qui n'a pas déposé son mémoire dans le délai de l'article 584 est déchu de son pourvoi ; il en va de même, sauf dérogation du président de la chambre criminelle, du condamné sans avocat et du ministère public dont le mémoire n'est pas parvenu à la Cour dans le mois du pourvoi ; le condamné à une peine non prévue par la loi n'est jamais déchu (art. 590-1, lu en entier le 20 novembre 2026).

Motifs fréquents de rejet sans examen au fond. Pourvoi tardif (art. 568) ; décision non attaquable (art. 570 et 574) ; défaut de grief (art. 567) ; déchéance faute de mémoire dans le délai (art. 590-1) ; mémoire tardif ou présenté sans avocat aux Conseils quand il est requis (art. 585, 585-1 et 590).

## 11. Requête devant la Cour européenne des droits de l'homme

Juridiction et qualité. La Cour peut être saisie par toute personne physique, organisation non gouvernementale ou groupe de particuliers qui se prétend victime d'une violation par une Haute Partie contractante des droits reconnus dans la Convention ou ses protocoles (Convention, art. 34).

Conditions de recevabilité. La Cour ne peut être saisie qu'après l'épuisement des voies de recours internes et dans un délai de quatre mois à partir de la date de la décision interne définitive (art. 35, § 1). Elle ne retient pas la requête anonyme, ni celle qui est essentiellement la même qu'une requête déjà examinée ou soumise à une autre instance internationale, sans faits nouveaux (art. 35, § 2). Elle déclare irrecevable la requête incompatible avec la Convention, manifestement mal fondée ou abusive, ou celle dont l'auteur n'a subi aucun préjudice important, sauf si le respect des droits de l'homme exige un examen au fond (art. 35, § 3). Elle peut rejeter à tout stade (art. 35, § 4).

Délai de quatre ou six mois. L'article 4 du Protocole n° 15 a remplacé les mots « six mois » par « quatre mois » ; selon son article 8, § 3, cet article entre en vigueur six mois après l'entrée en vigueur du Protocole et ne s'applique pas aux requêtes dont la décision définitive a été prise avant cette date. L'édition officielle de la Convention indique l'entrée en vigueur du Protocole n° 15 le 1er août 2021, et la note finale du Règlement de la Cour mentionne des amendements entrés en vigueur le 1er août 2021 et le 1er février 2022. Le délai est donc de quatre mois pour les décisions définitives prises à compter du 1er février 2022, et de six mois pour les décisions antérieures. Dans une décision de comité lue en entier, la Cour a retenu comme point de départ la date à laquelle le requérant avait pris connaissance de l'arrêt de la Cour de cassation et a appliqué la prorogation de trois mois liée à la crise sanitaire (N.Z. c. France, déc., 15 septembre 2022, n° 40401/20, § 14 ; https://hudoc.echr.coe.int/fre?i=001-220042) ; les dates énoncées dans ce paragraphe sont incohérentes entre elles, et la décision ne permet pas d'en tirer une règle de calcul. La date prudente reste celle de la décision interne définitive. La requête est réputée introduite à la date d'envoi d'un formulaire satisfaisant aux exigences de l'article 47, le cachet de la poste faisant foi, la Cour pouvant retenir une autre date (Règlement, art. 47, § 6).

Épuisement. La règle de l'épuisement des voies de recours internes (art. 35, § 1) impose d'avoir saisi les juridictions internes du grief présenté à la Cour, au moins en substance ; cette formulation jurisprudentielle n'a pas été relue dans une décision de principe pour cette fiche : non vérifié.

Acte et mentions. La requête est présentée sur le formulaire du greffe et indique notamment l'identité du requérant, le cas échéant celle du représentant et le pouvoir signé, l'État défendeur, un exposé concis et lisible des faits, des violations alléguées et du respect des critères de l'article 35, § 1 ; ces informations doivent figurer dans le formulaire et peuvent être complétées par un document de vingt pages au plus ; le formulaire est assorti des copies des décisions dénoncées et des documents montrant l'épuisement et le respect du délai, classés par ordre chronologique et numérotés ; le requérant qui ne veut pas que son identité soit révélée doit le demander en motivant sa demande (Règlement, art. 47, §§ 1 à 4). En cas de non-respect de ces obligations, la requête n'est pas examinée, sauf explication satisfaisante, demande de mesure provisoire ou décision contraire de la Cour (art. 47, § 5.1). La requête est écrite et signée par le requérant ou son représentant, qui produit un pouvoir (art. 45).

Représentation. Le requérant peut d'abord agir lui-même ou par un représentant ; après la communication de la requête au gouvernement défendeur, il doit être représenté par un conseil habilité à exercer dans une Partie contractante, sauf décision contraire du président de la chambre (Règlement, art. 36, §§ 1, 2 et 4).

Motifs fréquents de rejet sans examen au fond. Tardiveté (art. 35, § 1) ; non-épuisement des voies de recours internes (art. 35, § 1) ; formulaire incomplet (Règlement, art. 47, § 5.1) ; défaut manifeste de fondement (art. 35, § 3, a).

Voies de recours. La décision d'irrecevabilité d'un juge unique est définitive (art. 27, § 2). Dans un délai de trois mois à compter de l'arrêt d'une chambre, toute partie peut demander le renvoi devant la Grande Chambre, dans des cas exceptionnels (art. 43) ; l'arrêt de chambre devient définitif dans les conditions de l'article 44. Le régime des décisions de comité (art. 28) n'a pas été lu : non vérifié.

## 12. Question prioritaire de constitutionnalité

### 12.1 Règles communes

Fondement. Lorsqu'il est soutenu, à l'occasion d'une instance, qu'une disposition législative porte atteinte aux droits et libertés que la Constitution garantit, le Conseil constitutionnel peut être saisi sur renvoi du Conseil d'État ou de la Cour de cassation (Constitution, art. 61-1). Une disposition déclarée inconstitutionnelle est abrogée à compter de la publication de la décision ou d'une date ultérieure qu'elle fixe ; les décisions du Conseil ne sont susceptibles d'aucun recours (art. 62).

Devant les juridictions du fond. Le moyen est présenté, à peine d'irrecevabilité, dans un écrit distinct et motivé ; il peut être soulevé pour la première fois en appel ; il ne peut être relevé d'office ; au cours de l'instruction pénale, la juridiction d'instruction du second degré en est saisie ; il ne peut être soulevé devant la cour d'assises, mais peut l'être dans un écrit accompagnant la déclaration d'appel d'un arrêt d'assises, transmis immédiatement à la Cour de cassation (ordonnance n° 58-1067, art. 23-1). La juridiction transmet si la disposition est applicable au litige ou à la procédure ou constitue le fondement des poursuites, si elle n'a pas déjà été déclarée conforme dans les motifs et le dispositif d'une décision du Conseil constitutionnel, sauf changement des circonstances, et si la question n'est pas dépourvue de caractère sérieux ; elle se prononce par priorité sur la question de constitutionnalité ; la décision de transmettre est adressée dans les huit jours et n'est susceptible d'aucun recours ; le refus de transmettre ne peut être contesté qu'à l'occasion d'un recours contre la décision réglant tout ou partie du litige (art. 23-2). La juridiction sursoit à statuer, sauf privation de liberté, délai imposé ou urgence, dans les conditions de l'article 23-3.

Devant la Cour de cassation et le Conseil d'État. Le moyen peut être soulevé pour la première fois en cassation, dans un mémoire distinct et motivé, à peine d'irrecevabilité (art. 23-5). La juridiction suprême se prononce dans les trois mois de la réception de la transmission ou de la présentation du moyen ; elle renvoie si les conditions des 1° et 2° de l'article 23-2 sont remplies et si la question est nouvelle ou présente un caractère sérieux (art. 23-4 et 23-5). À défaut de décision dans ces délais, la question est transmise au Conseil constitutionnel (art. 23-7). Le Conseil constitutionnel statue dans les trois mois de sa saisine (art. 23-10).

### 12.2 Juridictions judiciaires

En matière pénale, l'irrecevabilité du moyen non présenté dans un écrit distinct et motivé doit être relevée d'office (CPP, art. R*49-21). Au cours de l'instruction, l'écrit est déposé au greffe de la chambre de l'instruction ou à celui du juge d'instruction, du juge des libertés ou du juge des enfants, qui le transmet (art. R*49-22) ; la personne détenue peut le remettre au chef d'établissement (art. R*49-24). La juridiction statue sans délai après observations, ou sans elles s'il apparaît de façon certaine qu'il n'y a pas lieu à transmission ; les observations écrites des autres parties doivent figurer dans un écrit distinct (art. R*49-25). La juridiction n'est pas tenue de transmettre une question portant, par les mêmes motifs, sur une disposition dont la Cour de cassation ou le Conseil est déjà saisi, et sursoit alors à statuer (art. R*49-26). Le refus de transmettre dessaisit la juridiction du moyen, sauf rétractation lorsque le refus reposait sur la seule inapplicabilité (art. R*49-27). En appel, et pour contester un refus de transmission à l'occasion d'un recours, le moyen est présenté dans un écrit distinct et motivé (art. R*49-29). Devant la Cour de cassation, le refus ne se conteste qu'en posant de nouveau la question, par un écrit distinct et motivé, devant la juridiction saisie du litige ; le mémoire qui se borne à contester le refus est irrecevable (Cass. 1re civ., 18 décembre 2014, n° 14-18.944, publié au Bulletin), comme le pourvoi formé contre la seule décision de non-transmission, distinct du pourvoi au fond (Crim., 7 juin 2011, n° 11-81.826, publié au Bulletin). Décisions lues en entier le 20 novembre 2026. Devant la Cour de cassation, les parties ont un mois à compter de la décision de transmission pour présenter des observations, signées par un avocat aux Conseils sauf exceptions prévues (art. R*49-30) ; le mémoire distinct présenté à l'occasion d'un pourvoi porte la mention « question prioritaire de constitutionnalité », et les autres parties disposent d'un mois pour répondre (art. R*49-31).

En matière civile, le moyen est présenté à peine d'irrecevabilité dans un écrit distinct et motivé, y compris à l'occasion d'un recours contre une décision réglant le litige après un refus de transmission, et le juge relève d'office cette irrecevabilité (CPC, art. 126-2).

### 12.3 Juridictions administratives

Le moyen est soulevé, à peine d'irrecevabilité, dans un mémoire distinct et motivé ; ce mémoire et son enveloppe portent la mention « question prioritaire de constitutionnalité » (CJA, art. R*771-3). L'irrecevabilité peut être opposée sans invitation à régulariser (art. R*771-4). La notification d'un refus de transmission rappelle qu'il ne peut être contesté qu'à l'occasion d'un recours contre la décision réglant le litige, par mémoire distinct et motivé accompagné d'une copie du refus (art. R*771-9). Pour contester en appel le refus du premier juge, la partie présente, à peine d'irrecevabilité, cette contestation avant l'expiration du délai d'appel dans un mémoire distinct et motivé accompagné d'une copie de la décision de refus (art. R*771-12) ; la même règle vaut devant le Conseil d'État, avant l'expiration du délai de recours (art. R*771-16). Le régime est inverse de celui de la Cour de cassation : c'est le refus lui-même qui se conteste, dans le délai de recours, y compris lorsqu'il figure dans l'arrêt attaqué, et reposer la même question sur le fondement de l'article 23-5 de l'ordonnance ne permet pas d'échapper à cette condition (CE, 1er février 2011, SARL Prototype Technique Industrie, n° 342536, publié au Recueil, lu en entier le 20 novembre 2026, où une contestation présentée seulement avec le mémoire complémentaire, après le délai, a été rejetée). Devant le Conseil d'État, le mémoire distinct porte la même mention (art. R*771-13). Les observations sur une question transmise sont produites dans le mois de la notification de la transmission, par un avocat aux Conseils sauf dispense applicable devant la juridiction de renvoi (art. R*771-20).

Motifs fréquents de rejet sans examen au fond. Absence d'écrit ou de mémoire distinct et motivé ; disposition non applicable au litige ; disposition déjà déclarée conforme sans changement des circonstances (art. 23-2, 2°) ; question dépourvue de caractère sérieux ; contestation du refus de transmission hors du délai de recours ou sans mémoire distinct (CJA, art. R*771-12 et R*771-16) ; question soulevée devant la cour d'assises (art. 23-1).

Voies de recours. Aucune contre la décision de transmettre (art. 23-2) ni contre la décision du Conseil constitutionnel (Constitution, art. 62) ; le refus de transmettre se conteste avec le recours contre la décision au fond (art. 23-2 ; CPP, art. R*49-28 et R*49-29 ; CJA, art. R*771-12 et R*771-16).

## 13. Correspondance avec les catégories de motifs

| Défaut constaté | Catégorie |
| --- | --- |
| Plainte préalable irrégulière ou délai de trois mois non écoulé (CPP, art. 85, al. 2) | `prealable_obligatoire_absent` |
| Consignation non versée dans le délai (art. 88 et 392-1), écrit distinct absent (art. 23-1), formulaire CEDH incomplet | `formalite_substantielle` |
| Appel, pourvoi ou requête CEDH hors délai | `delai_tardivete` |
| Forclusion des nullités (art. 173-1, 174, 175) et prescription de l'action publique (art. 7 à 9-3) | `prescription_forclusion` |
| Arrêt de renvoi non attaquable (art. 574), décision avant dire droit (art. 570), disposition déjà déclarée conforme | `acte_non_attaquable` |
| Partie civile sans préjudice personnel et direct, appel de la partie civile sur l'action publique (art. 2 et 497) | `interet_qualite` |
| Grief non soulevé en substance devant les juridictions internes (Convention, art. 35, § 1) | `non_epuisement` |
| Requête CEDH manifestement mal fondée, question dépourvue de caractère sérieux | `mal_fonde` |

## 14. Décisions lues

| Décision | Statut | Lien |
| --- | --- | --- |
| Crim., 30 janvier 1973, n° 72-92.400 | publié au Bulletin | https://librejustice.fr/decision/ool-72bzWNWx |
| Crim., 27 mars 1995, n° 94-82.758 | publié au Bulletin | https://librejustice.fr/decision/tczGvjLzoAaI |
| Crim., 10 mai 2000, n° 99-84.157 | inédit | https://librejustice.fr/decision/KS0an9Cx5FYg |
| Crim., 18 décembre 2007, n° 07-82.106 | publié au Bulletin | https://librejustice.fr/decision/RIWuY98U-8rX |
| Crim., 6 janvier 2009, n° 08-84.141 | publié au Bulletin | https://librejustice.fr/decision/8xvk1BZz9S9m |
| CEDH, N.Z. c. France, 15 septembre 2022, n° 40401/20 | décision de comité | https://hudoc.echr.coe.int/fre?i=001-220042 |
| Cons. const., 23 juillet 2010, n° 2010-15/23 QPC | Journal officiel | https://librejustice.fr/norm/fr/decision-n-2010-15-23-qpc-du-23-juillet-2010 |
| CE, 1er février 2011, n° 342536 | publié au Recueil | https://librejustice.fr/decision/tXc6Fybth2vn |
| Crim., 7 juin 2011, n° 11-81.826 | publié au Bulletin | https://librejustice.fr/decision/-PPVOEvSJNcv |
| Cass. 1re civ., 18 décembre 2014, n° 14-18.944 | publié au Bulletin | https://librejustice.fr/decision/hk5xXeqVcSZC |
| Crim., 8 mars 2022, n° 21-83.037 | publié au Bulletin | https://librejustice.fr/decision/O3DcPnMtGcYX |
| Crim., 23 juin 2026, n° 25-87.950 | publié au Bulletin | https://librejustice.fr/decision/4rK82xyOTbhT |

## 15. Points non vérifiés

- Articles 52, 52-1 et 706-42 du CPP (compétence territoriale du juge d'instruction).
- Article 547 du CPP (délai d'appel des jugements de police).
- Articles 567-1-1, 571, 574-1 et 574-2 du CPP (non-admission, examen immédiat, pourvois spéciaux).
- Article 565 du CPP (nullité de la citation).
- Mode de calcul des jours francs de l'article 568.
- Article 28 de la Convention (décisions de comité) et voies de recours contre ces décisions.
- Nouvelle rédaction de l'article 10 du CPP annoncée au 1er janvier 2027.
- Numérotation du code de procédure pénale réécrit, applicable à compter du 1er janvier 2029.
