# Contentieux administratifs spéciaux : régimes avant dépôt

Référence du plugin contentieux pour six familles de recours devant le juge administratif : contentieux fiscal, urbanisme, droit des étrangers (obligation de quitter le territoire et refus de séjour), commande publique, responsabilité administrative et liaison du contentieux, fonction publique. Pour chaque procédure, la fiche indique la juridiction, l'acte introductif, les préalables, les délais, la représentation, les conditions de recevabilité, les motifs de rejet sans examen au fond observés dans les décisions lues et les voies de recours.

Vérification faite le 18 novembre 2026. Les textes ont été lus dans leur version en vigueur à cette date sur LibreJustice (reprise de Légifrance), et la version antérieure a été relue lorsque l'application de la règle dans le temps l'exigeait. Une décision de principe n'est citée qu'avec son statut de lecture : « texte intégral lu » ou « analyse officielle lue ». Les décisions de tribunaux citées comme illustrations proviennent de la base ouverte de la justice administrative et ont été lues en entier. Ce qui n'a pas pu être vérifié porte la mention « non vérifié ».

Les fichiers liés sont `administratif_special_regimes.json` (conditions par type d'acte, lues par `scripts/gate.py`) et `administratif_special_voies.json` (règles de délai, lues par `scripts/voies.py`).

## 0. Règles communes du code de justice administrative

### Saisine et contenu de la requête

La juridiction est saisie par requête, qui indique les nom et domicile des parties, expose les faits et moyens et énonce les conclusions. Une requête sans aucun moyen ne peut être régularisée par un mémoire que jusqu'à l'expiration du délai de recours (CJA, art. R. 411-1).

La requête doit, à peine d'irrecevabilité et sauf impossibilité justifiée, être accompagnée de l'acte attaqué ou, en cas de décision implicite, de la pièce justifiant la date de dépôt de la réclamation ; cet acte ou cette pièce doit lui-même être accompagné d'une copie (CJA, art. R. 412-1, version en vigueur depuis le 9 avril 2018).

Lorsque l'irrecevabilité peut être couverte après l'expiration du délai de recours, le juge ne peut la relever d'office qu'après avoir invité l'auteur à régulariser, dans un délai qui, sauf urgence, ne peut être inférieur à quinze jours (CJA, art. R. 612-1). Les requêtes manifestement irrecevables qui n'exigent pas d'invitation, ou qui n'ont pas été régularisées dans le délai imparti, sont rejetées par ordonnance (CJA, art. R. 222-1, 4°).

### Délai de recours

La juridiction ne peut être saisie que par un recours contre une décision, dans les deux mois de sa notification ou de sa publication. Lorsque la requête tend au paiement d'une somme d'argent, elle n'est recevable qu'après la décision prise par l'administration sur une demande préalable (CJA, art. R. 421-1, version en vigueur depuis le 1er janvier 2020). Ces deux règles ne s'appliquent pas à la contestation des mesures d'exécution d'un contrat (même article, al. 3).

Lorsque le silence vaut rejet, le délai de deux mois court de la naissance de la décision implicite ; une décision explicite intervenue avant la fin de cette période fait courir un nouveau délai. La date de dépôt de la demande doit être établie à l'appui de la requête (CJA, art. R. 421-2). Le silence de deux mois vaut rejet, notamment, pour une demande à caractère financier et dans les relations entre l'administration et ses agents (CRPA, art. L. 231-4, 3° et 5°).

Les délais ne sont opposables que s'ils ont été mentionnés, avec les voies de recours, dans la notification (CJA, art. R. 421-5). Les délais ne sont pas non plus opposables à l'auteur d'une demande qui n'a pas reçu d'accusé de réception conforme, sauf décision expresse notifiée avant la naissance de la décision implicite (CRPA, art. L. 112-6). En l'absence de mention des voies et délais, le destinataire d'une décision individuelle qui en a eu connaissance ne peut, en règle générale et sauf circonstances particulières, la contester au-delà d'un délai raisonnable d'un an (CE, Ass., 13 juillet 2016, Czabaj, n° 387763, publié au Recueil, analyse officielle lue).

Un recours gracieux ou hiérarchique formé dans le délai interrompt le délai contentieux (CRPA, art. L. 411-2), sauf texte contraire. Les textes spéciaux examinés ci-dessous écartent cette prorogation en urbanisme, pour les obligations de quitter le territoire et pour les militaires.

Le délai est augmenté d'un mois pour les personnes qui demeurent outre-mer devant un tribunal de métropole, et de deux mois pour celles qui demeurent à l'étranger (CJA, art. R. 421-7).

Caractère franc et computation. Le délai de deux mois de recours contentieux est un délai franc ; s'il expire un samedi, un dimanche ou un jour férié ou chômé, il est prorogé jusqu'au premier jour ouvrable suivant (CE, 19 septembre 2014, n° 362568, mentionné aux tables, analyse officielle lue). Le fichier des voies retient le caractère franc pour ce délai et pour les délais qui y renvoient, et ne le retient pas ailleurs faute de vérification ; `voies.py` donne alors la date prudente.

Aide juridictionnelle. Une demande d'aide juridictionnelle adressée avant l'expiration du délai de recours fait courir un nouveau délai de même durée à compter des événements énumérés par l'article 43 du décret n° 2020-1717 du 28 décembre 2020 (version en vigueur depuis le 13 juin 2026). Les étrangers visés par la procédure de l'article L. 911-1 du CESEDA obéissent à une règle propre (section 3).

### Représentation

Le ministère d'avocat est obligatoire devant le tribunal lorsque les conclusions tendent au paiement d'une somme d'argent, à la décharge ou à la réduction d'une somme réclamée, ou à la solution d'un litige né de l'exécution d'un contrat (CJA, art. R. 431-2). En sont dispensés notamment les litiges de contributions directes et de taxes sur le chiffre d'affaires (2°), les litiges d'ordre individuel des agents publics (3°), les litiges dans lesquels le défendeur est une collectivité territoriale, un de ses établissements publics ou un établissement public de santé (5°) (CJA, art. R. 431-3, version en vigueur depuis le 1er janvier 2025). En appel, le ministère d'avocat est obligatoire (CJA, art. R. 811-7).

### Voies de recours

Le délai d'appel est de deux mois à compter de la notification du jugement (CJA, art. R. 811-2). Le tribunal statue en premier et dernier ressort, notamment, sur les impôts locaux autres que la contribution économique territoriale (4°), les remises gracieuses en matière fiscale (5°), et, hors commande publique, les actions indemnitaires dont le montant n'excède pas le seuil des articles R. 222-14 et R. 222-15 (8°) (CJA, art. R. 811-1, version en vigueur depuis le 1er novembre 2025) ; l'article R. 222-14 fixe ce seuil à 10 000 euros, l'article R. 222-15 n'a pas été relu. Contre un jugement en dernier ressort, le pourvoi en cassation est ouvert dans un délai de deux mois (CJA, art. R. 821-1). L'obligation du ministère d'avocat au Conseil d'État et à la Cour de cassation en cassation n'a pas été relue dans ses textes (non vérifié).

## 1. Contentieux fiscal : réclamation préalable et saisine du juge de l'impôt

### Juridiction

Les décisions rendues sur les réclamations en matière d'impôts directs et de taxes sur le chiffre d'affaires ou assimilées sont portées devant le tribunal administratif ; les droits d'enregistrement, l'impôt sur la fortune immobilière, la taxe de publicité foncière, les droits de timbre et les contributions indirectes relèvent du tribunal judiciaire (LPF, art. L. 199, version en vigueur jusqu'au 31 décembre 2026). À compter du 1er janvier 2027, l'article pose le principe de la compétence du tribunal administratif et maintient par dérogation celle du tribunal judiciaire pour ces matières et pour les taxes sur les biens et services soumises aux règles contentieuses des douanes ou des contributions indirectes (LPF, art. L. 199, rédaction issue de l'ordonnance n° 2025-1247 du 17 décembre 2025, en vigueur le 1er janvier 2027). La compétence territoriale n'a pas été vérifiée dans ses textes.

Le champ de la juridiction contentieuse couvre les réclamations tendant à la réparation d'erreurs d'assiette ou de calcul ou au bénéfice d'un droit légal ou réglementaire (LPF, art. L. 190, al. 1).

### Préalable obligatoire : la réclamation

Le contribuable qui conteste un impôt doit d'abord adresser une réclamation au service territorial dont dépend le lieu de l'imposition, ou à la direction qui a établi l'imposition lorsqu'elle n'est pas celle du lieu d'imposition (LPF, art. R.* 190-1, version en vigueur depuis le 2 juin 2024). La réclamation donne lieu à un récépissé (même article, dernier al.).

Forme et mentions. La réclamation est individuelle, sauf exceptions (LPF, art. R.* 197-1). Elle doit, à peine d'irrecevabilité, mentionner l'imposition contestée, contenir l'exposé sommaire des moyens et les conclusions, porter la signature manuscrite de son auteur et être accompagnée de l'avis d'imposition, de l'avis de mise en recouvrement ou, à défaut, d'une pièce justifiant le montant de la retenue ou du versement (LPF, art. R.* 197-3). Le défaut de signature appelle une invitation à signer dans les trente jours ; le défaut de pièce est régularisable à tout moment (même article). Les vices des a, b et d peuvent être couverts devant le tribunal lorsqu'ils ont motivé le rejet de la réclamation (LPF, art. R.* 200-2, al. 3).

### Délais

| Étape | Délai | Point de départ | Texte |
| --- | --- | --- | --- |
| Réclamation, impôts autres que les impôts directs locaux | 31 décembre de la deuxième année suivante | Mise en recouvrement du rôle ou notification de l'avis de mise en recouvrement ; à défaut, versement ; ou événement motivant la réclamation | LPF, art. R.* 196-1 (version issue du décret n° 2026-692 du 27 juillet 2026) |
| Réclamation, impôts directs locaux et taxes annexes | 31 décembre de l'année suivante | Mise en recouvrement, avis de mise en recouvrement, titre de perception, versement ou événement | LPF, art. R.* 196-2 (même décret) |
| Réclamation après procédure de reprise ou de rectification | Délai égal à celui dont dispose l'administration | Procédure de reprise ou de rectification | LPF, art. R.* 196-3 |
| Instruction de la réclamation | Six mois, prorogeables de trois mois sur information du contribuable | Présentation de la réclamation | LPF, art. R.* 198-10 |
| Saisine du tribunal | Deux mois | Réception de l'avis notifiant la décision, qu'il intervienne avant ou après les six mois ; saisine possible dès l'expiration des six mois sans décision | LPF, art. R.* 199-1 |

Une décision juridictionnelle ou un avis contentieux révélant la non-conformité d'une règle à une norme supérieure ne constitue pas un événement rouvrant le délai (LPF, art. R.* 196-1, c, et L. 190, al. 3 à 5). Le caractère franc du délai de l'article R.* 199-1 n'a pas été vérifié.

### Représentation

Le tribunal peut être saisi sans avocat pour les contributions directes et les taxes sur le chiffre d'affaires (CJA, art. R. 431-3, 2°), et la requête peut être signée d'un mandataire autre qu'un avocat, sous les conditions de l'article R.* 197-4 (LPF, art. R.* 200-2, al. 1 ; R.* 197-4 non relu). L'appel exige un avocat (CJA, art. R. 811-7).

### Conditions de recevabilité à établir avant dépôt

Réclamation régulière et dans le délai, adressée au service compétent ; décision sur la réclamation, ou expiration du délai de six mois ; requête dans les deux mois de la réception de la décision ; impositions identiques à celles visées dans la réclamation (LPF, art. R.* 200-2, al. 2) ; production de la décision ou, à défaut, de la réclamation et de la preuve de sa date (CJA, art. R. 412-1).

### Rejets sans examen au fond observés

- Réclamations tardives au regard du a) de l'article R.* 196-2, l'absence de notification des délais de réclamation étant jugée inopérante (TA Melun, ord., 30 septembre 2026, n° 2604574).
- Défaut de preuve de la réception de la réclamation malgré deux demandes de régularisation (TA Melun, ord., 20 octobre 2026, n° 2614772).
- Requête non signée et non accompagnée de la décision sur réclamation, non régularisée (TA Rouen, ord., 14 octobre 2026, n° 2603953).

### Voies de recours

Appel dans les deux mois (CJA, art. R. 811-2), sauf impôts locaux hors contribution économique territoriale et remises gracieuses, jugés en dernier ressort (CJA, art. R. 811-1, 4° et 5°).

## 2. Urbanisme : recours contre les autorisations d'occupation du sol

### Juridiction

Tribunal administratif, par recours pour excès de pouvoir. La compétence territoriale n'a pas été vérifiée dans ses textes. Le tribunal statue en premier et dernier ressort, pour les recours introduits entre le 1er septembre 2022 et le 31 décembre 2027, sur les permis de construire ou de démolir un bâtiment de plus de deux logements, les permis d'aménager un lotissement et les décisions assimilées, ainsi que certains actes de zone d'aménagement concerté, lorsque le projet est situé dans une commune mentionnée à l'article 232 du code général des impôts, sauf exceptions (CJA, art. R. 811-1-1, version issue du décret n° 2026-302 du 21 avril 2026, applicable aux actes pris à compter du 1er juillet 2026).

### Acte introductif et pièces

Requête conforme à l'article R. 411-1 du CJA, accompagnée de l'acte attaqué (R. 412-1) et, à peine d'irrecevabilité, du titre de propriété, de la promesse de vente, du bail ou de tout acte établissant l'occupation ou la détention régulière du bien ; pour une association, des statuts et du récépissé de déclaration en préfecture. Cette exigence ne s'applique pas au pétitionnaire (C. urb., art. R.* 600-4).

### Formalité substantielle : notification du recours

L'auteur d'un recours contentieux contre une décision relative à l'occupation ou l'utilisation du sol doit, à peine d'irrecevabilité, le notifier à l'auteur de la décision et au titulaire de l'autorisation, par lettre recommandée avec accusé de réception, dans un délai de quinze jours francs à compter du dépôt du recours. La notification est réputée accomplie à la date d'envoi établie par le certificat de dépôt. L'auteur d'un recours administratif doit aussi le notifier, faute de quoi le recours contentieux formé ensuite est irrecevable. La règle vaut pour l'appel et la cassation contre un jugement portant sur une telle décision ; elle ne s'applique pas à la contestation d'un permis modificatif ou d'une mesure de régularisation dans les conditions de l'article L. 600-5-2 (C. urb., art. R.* 600-1, version en vigueur depuis le 13 avril 2019). Le panneau d'affichage doit rappeler cette obligation (C. urb., art. R.* 424-15, al. 2, et A. 424-17).

### Intérêt à agir

Une personne autre que l'État, une collectivité territoriale, un groupement ou une association n'est recevable que si la construction, l'aménagement ou le projet est de nature à affecter directement les conditions d'occupation, d'utilisation ou de jouissance du bien qu'elle détient ou occupe régulièrement, ou pour lequel elle bénéficie d'une promesse de vente, de bail ou d'un contrat préliminaire (C. urb., art. L. 600-1-2, version en vigueur depuis le 1er janvier 2019). L'intérêt s'apprécie à la date d'affichage en mairie de la demande du pétitionnaire, sauf circonstances particulières (C. urb., art. L. 600-1-3). Une association n'est recevable que si ses statuts ont été déposés au moins un an avant cet affichage (C. urb., art. L. 600-1-1).

Le requérant doit préciser l'atteinte invoquée par des éléments suffisamment précis et étayés ; le défendeur peut établir que ces atteintes sont dépourvues de réalité ; le juge n'exige pas la preuve du caractère certain des atteintes ; le voisin immédiat justifie en principe d'un intérêt lorsqu'il fait état d'éléments relatifs à la nature, à l'importance ou à la localisation du projet (CE, 13 avril 2016, Bartolomei, n° 389798, publié au Recueil, analyse officielle lue).

### Délais

| Étape | Délai | Point de départ | Texte |
| --- | --- | --- | --- |
| Recours contentieux des tiers | Deux mois, délai franc | Premier jour d'une période continue de deux mois d'affichage sur le terrain | C. urb., art. R.* 600-2 ; CJA, art. R. 421-1 |
| Notification du recours contentieux ou administratif | Quinze jours francs | Dépôt du recours | C. urb., art. R.* 600-1 |
| Recours gracieux ou hiérarchique | Un mois ; silence de deux mois vaut rejet ; pas de prorogation du délai contentieux | Non précisé par le texte | C. urb., art. L. 600-12-2 (loi n° 2025-1129 du 26 novembre 2025, en vigueur le 28 novembre 2025) |
| Limite absolue de l'action | Six mois | Achèvement des travaux, présumé à la réception de la déclaration d'achèvement | C. urb., art. R.* 600-3 |
| Cristallisation des moyens | Deux mois | Communication aux parties du premier mémoire en défense | C. urb., art. R. 600-5 |
| Référé suspension contre un permis ou une non-opposition | Jusqu'à la cristallisation | Même date | C. urb., art. L. 600-3 |

L'application de l'article L. 600-12-2 aux décisions antérieures au 28 novembre 2025 n'a pas été vérifiée ; l'article 26 de la loi du 26 novembre 2025 ne fixe de règle transitoire que pour les articles L. 600-2 et L. 600-3-1. La même loi a abrogé l'article L. 600-1 (même article 26, I, 3°).

### Référé suspension

L'urgence est présumée pour le recours contre une non-opposition ou un permis ; le référé n'est recevable que jusqu'à l'expiration du délai de cristallisation devant le juge de première instance ; le juge statue dans un délai d'un mois sur la demande d'un tiers (C. urb., art. L. 600-3). Le doute sérieux reste à établir. Lorsqu'un recours contre une opposition à déclaration préalable ou un refus de permis de construire, d'aménager ou de démolir est assorti d'un référé-suspension, la condition d'urgence est présumée satisfaite (C. urb., art. L. 600-3-1, version du 28 novembre 2025, lu en entier le 20 novembre 2026), pour les référés introduits après la publication de la loi n° 2025-1129 du 26 novembre 2025 (art. 26, IV).

### Représentation

Aucune disposition spéciale relevée ; le ministère d'avocat n'est pas requis pour une demande d'annulation sans conclusions pécuniaires (CJA, art. R. 431-2 a contrario) et l'est en appel (R. 811-7).

### Rejets sans examen au fond observés

- Défaut de notification du recours contentieux dans les conditions de l'article R.* 600-1, opposé à des requérants représentés par avocat contre une non-opposition à déclaration préalable (TA Bordeaux, ord., 10 novembre 2026, n° 2607923).

### Voies de recours

Appel dans les deux mois (CJA, art. R. 811-2), soumis à son tour à la notification de l'article R.* 600-1 ; cassation seulement dans les cas de l'article R. 811-1-1.

## 3. Droit des étrangers : obligation de quitter le territoire et décisions liées

### Juridiction et régime

Le recours contre l'obligation de quitter le territoire français et contre les décisions relatives au séjour, au délai de départ volontaire et à l'interdiction de retour qui l'accompagnent relève du tribunal administratif, selon des règles fixées au livre IX du CESEDA (CJA, art. R. 776-1). La procédure dépend de la situation de l'étranger :

| Situation | Procédure | Délai de recours | Délai de jugement | Textes |
| --- | --- | --- | --- | --- |
| Cas général | Collégiale spéciale | Un mois à compter de la notification | Six mois | CESEDA, art. L. 614-1, L. 911-1, R. 614-3, R. 911-1 |
| Assigné à résidence (L. 731-1) ou détenu | Juge unique | Sept jours à compter de la notification | Quinze jours | CESEDA, art. L. 614-2, al. 1, L. 614-3, L. 921-1 |
| Placé en rétention | Juge unique | Quarante-huit heures à compter de la notification ; cinq jours dans le cas du paragraphe 3 de l'article 68 du règlement (UE) 2024/1348 ; sept jours pour une décision de transfert | Quatre-vingt-seize heures après l'expiration du délai de recours | CESEDA, art. L. 614-2, al. 2, L. 921-2, R. 921-2-1 |

Le délai d'un mois n'est pas prorogé par un recours administratif (CESEDA, art. R. 911-1, al. 2, version en vigueur depuis le 8 juin 2026, et version antérieure du 15 juillet 2024 au 7 juin 2026, qui posait la même règle). L'étranger peut demander l'aide juridictionnelle au plus tard lors de l'introduction de son recours (CESEDA, art. L. 911-1, al. 2). Lorsqu'une assignation à résidence ou un placement en rétention est notifié avant l'expiration du délai, l'administration informe l'étranger que ce délai est interrompu et qu'un nouveau délai, de sept jours ou celui de l'article R. 921-2-1, court à compter de cette information (CESEDA, art. R. 921-1). Pour certaines obligations prises contre des demandeurs d'asile, des règles propres s'appliquent aux décisions notifiées à compter du 12 juin 2026 (CESEDA, R. 614-3, al. 2, et notes des décrets n° 2026-455 et 2026-456 du 6 juin 2026).

Droit transitoire. Les règles issues de la loi n° 2024-42 du 26 janvier 2024 s'appliquent à la contestation des décisions prises à compter du 15 juillet 2024 (note sous CESEDA, art. L. 614-1). Pour les décisions antérieures, l'article R. 776-2 du CJA alors en vigueur prévoyait trente jours pour une obligation avec délai de départ fondée sur les 3°, 5° ou 6° de l'article L. 611-1 ou sur L. 251-1, quinze jours pour les 1°, 2° ou 4°, et quarante-huit heures pour une obligation sans délai notifiée par voie administrative (CJA, art. R. 776-2, version du 1er mai 2021 au 15 juillet 2024) ; ces délais n'étaient pas prorogés par un recours administratif (CJA, art. R. 776-5, même période).

Le délai n'est opposable que s'il figure, avec les voies de recours, dans la notification (CJA, art. R. 421-5). Le caractère franc des délais du livre IX n'a pas été vérifié.

### Acte introductif et représentation

Requête conforme aux articles R. 411-1 et R. 412-1 du CJA, accompagnée de la décision. Le ministère d'avocat n'est pas requis en première instance faute de conclusions pécuniaires (CJA, art. R. 431-2 a contrario) ; il l'est en appel (R. 811-7).

### Rejets sans examen au fond observés

- Requête déposée trente-cinq jours après la notification d'un arrêté mentionnant le délai d'un mois (TA Marseille, ord., 26 août 2026, n° 2612821).

### Voies de recours

Pour les procédures à juge unique, l'appel est ouvert dans un délai d'un mois à compter de la notification du jugement, quinze jours pour le refus d'entrée au titre de l'asile (CESEDA, art. R. 922-27). Pour la procédure collégiale de l'article L. 911-1, aucune disposition dérogatoire n'a été trouvée ; le délai de deux mois de l'article R. 811-2 du CJA s'appliquerait (non vérifié).

## 4. Commande publique

### 4.1 Référé précontractuel

Juridiction. Le président du tribunal administratif ou le magistrat qu'il délègue, saisi d'un manquement aux obligations de publicité et de mise en concurrence dans la passation des contrats administratifs de travaux, fournitures ou services à contrepartie économique, des délégations de service public et de la sélection de l'actionnaire d'une société d'économie mixte à opération unique (CJA, art. L. 551-1, version en vigueur depuis le 1er septembre 2026 ; la version du 19 août 2015 au 31 août 2026 visait aussi les sociétés d'économie mixte hydroélectriques).

Condition temporelle. Le juge est saisi avant la conclusion du contrat (CJA, art. L. 551-1, dernier al., dans les deux versions). Ses pouvoirs ne peuvent plus être exercés après la conclusion (CE, 29 mars 2004, Communauté de communes du centre littoral, n° 258114, publié au Recueil, texte intégral lu). La saisine suspend la signature jusqu'à la notification de la décision juridictionnelle (CJA, art. L. 551-4).

Délai de suspension de la signature. En procédure formalisée, l'acheteur respecte un délai minimal de onze jours entre l'envoi de la notification de rejet et la signature, porté à seize jours sans transmission électronique (CCP, art. R. 2182-1) ; la notification de rejet mentionne les motifs du rejet et, après attribution, le nom de l'attributaire, les motifs du choix et la date à partir de laquelle l'acheteur peut signer (CCP, art. R. 2181-3). L'article R. 2182-1 ne vise que les procédures formalisées : en procédure adaptée, aucun délai minimal de signature ne résulte de ce texte. Le juge ne peut statuer avant le seizième jour suivant l'envoi de la décision d'attribution, ou le onzième en cas de communication électronique, et statue dans les vingt jours (CJA, art. R. 551-5).

Qualité et intérêt. Sont habilités à agir ceux qui ont intérêt à conclure le contrat et sont susceptibles d'être lésés par le manquement invoqué, ainsi que le préfet pour les contrats des collectivités (CJA, art. L. 551-10). Le juge recherche si les manquements invoqués, eu égard à leur portée et au stade de la procédure, sont susceptibles d'avoir lésé le requérant ou risquent de le léser, fût-ce indirectement en avantageant un concurrent (CE, Sect., 3 octobre 2008, SMIRGEOMES, n° 305420, publié au Recueil, analyse officielle lue).

Notification. L'auteur du recours doit le notifier au pouvoir adjudicateur ; la notification est réputée accomplie à sa réception (CJA, art. R. 551-1). Le texte ne précise pas la sanction de l'omission (non vérifié en jurisprudence). Un recours communiqué par Télérecours est réputé reçu dès sa mise à disposition (CE, 17 octobre 2016, Société Tribord, n° 400791, mentionné aux tables, analyse officielle lue).

Représentation. Aucune disposition spéciale relevée ; l'article R. 431-2 du CJA ne vise pas cette demande, qui ne tend ni au paiement d'une somme ni à la solution d'un litige né de l'exécution d'un contrat.

Rejets observés. Contrat signé avant l'enregistrement de la requête : irrecevabilité (TA Toulouse, ord., 12 août 2026, n° 2606256, concession signée dix jours avant la requête).

Voie de recours. L'ordonnance n'est pas susceptible d'appel (CE, 7 mars 2005, Société Grandjouan-Saco, n° 270778, publié au Recueil, analyse officielle lue) ; le délai du pourvoi en cassation n'a pas été relu (non vérifié).

### 4.2 Référé contractuel

Une fois le contrat conclu, le président du tribunal ou son délégué peut être saisi (CJA, art. L. 551-13) par ceux qui avaient intérêt à conclure et sont susceptibles d'être lésés, ou par le préfet (CJA, art. L. 551-14, al. 1). Le recours est fermé au demandeur qui a exercé un référé précontractuel lorsque l'acheteur a respecté la suspension et s'est conformé à la décision (même article, al. 2). Il est exclu pour certains contrats lorsque l'acheteur a publié son intention de conclure et observé onze jours, et pour les contrats fondés sur un accord-cadre lorsque la décision d'attribution a été envoyée seize jours, ou onze jours par voie électronique, avant la conclusion (CJA, art. L. 551-15).

Délai : au plus tard le trente et unième jour suivant la publication au Journal officiel de l'Union européenne d'un avis d'attribution conforme ou, pour les marchés fondés sur un accord-cadre ou un système d'acquisition dynamique, suivant la notification de la conclusion mentionnant le titulaire et les motifs du choix ; à défaut, six mois à compter du lendemain de la conclusion (CJA, art. R. 551-7).

Pouvoirs : nullité obligatoire dans les cas de l'article L. 551-18 (absence de toute publicité requise, omission d'une publication au JOUE prescrite, méconnaissance des règles de remise en concurrence des accords-cadres, signature prématurée ou pendant la suspension ayant privé le demandeur du référé précontractuel et affecté ses chances) ; nullité, résiliation, réduction de durée ou pénalité en cas de signature prématurée (CJA, art. L. 551-20).

### 4.3 Recours des tiers contre le contrat

Tout tiers susceptible d'être lésé dans ses intérêts de façon suffisamment directe et certaine par la passation ou les clauses d'un contrat administratif peut former devant le juge du contrat un recours de pleine juridiction contestant sa validité ou celle de clauses non réglementaires divisibles ; ce recours est ouvert aux membres de l'organe délibérant et au préfet ; il peut être assorti d'un référé suspension et de conclusions indemnitaires ; il doit être exercé dans un délai de deux mois à compter des mesures de publicité appropriées, notamment un avis mentionnant la conclusion du contrat et les modalités de sa consultation ; la légalité du choix du cocontractant, de la délibération autorisant la conclusion et de la décision de signer ne peut être contestée qu'à cette occasion, le préfet conservant le recours pour excès de pouvoir jusqu'à la conclusion. Les tiers autres que le préfet et les élus ne peuvent invoquer que des vices en rapport direct avec l'intérêt lésé ou d'une gravité telle que le juge devrait les relever d'office. Le recours vaut pour les contrats signés à compter du 4 avril 2014 (CE, Ass., 4 avril 2014, Département de Tarn-et-Garonne, n° 358994, publié au Recueil, texte intégral lu, cons. 2 à 5).

Représentation : les conclusions indemnitaires appellent le ministère d'avocat (CJA, art. R. 431-2) ; l'application de cet article aux seules conclusions en contestation de validité n'a pas été vérifiée.

## 5. Responsabilité administrative et liaison du contentieux

### Préalable : la demande et la décision

La requête pécuniaire n'est recevable qu'après la décision de l'administration sur une demande préalable (CJA, art. R. 421-1, al. 2). Le silence gardé deux mois sur une demande à caractère financier vaut rejet (CRPA, art. L. 231-4, 3°). En l'absence de décision, la requête est irrecevable et peut être rejetée pour ce motif même si l'administration n'a défendu qu'au fond ; mais la condition s'apprécie à la date à laquelle le juge statue, de sorte qu'une décision expresse ou implicite intervenue en cours d'instance régularise la requête, même après une fin de non-recevoir (CE, Sect., avis, 27 mars 2019, Rollet, n° 426472, publié au Recueil, texte intégral lu). La règle ne peut être opposée à une requête relative à une créance de travaux publics dirigée contre une personne privée non chargée d'un service public administratif (CE, 27 avril 2021, Communauté de communes du Centre Corse, n° 448467, publié au Recueil, analyse officielle lue).

### Délais et prescription

Contre un rejet exprès mentionnant les voies et délais, le délai est de deux mois (CJA, art. R. 421-1 et R. 421-5). La règle du délai raisonnable d'un an ne s'applique pas aux recours indemnitaires ; la sécurité juridique est assurée par la prescription quadriennale ou, pour les dommages corporels, par l'article L. 1142-28 du code de la santé publique (CE, 17 juin 2019, Centre hospitalier de Vichy, n° 413097, publié au Recueil, analyse officielle lue).

Prescription quadriennale. Sont prescrites au profit de l'État, des départements, des communes et des établissements publics dotés d'un comptable public les créances non payées dans un délai de quatre ans à partir du premier jour de l'année suivant celle de l'acquisition des droits (loi n° 68-1250 du 31 décembre 1968, art. 1er). La prescription est interrompue par toute réclamation écrite relative au fait générateur, à l'existence, au montant ou au paiement de la créance, par tout recours juridictionnel portant sur les mêmes objets, par toute communication écrite de l'administration ayant trait à ces objets et par toute émission d'un moyen de règlement ; un nouveau délai de quatre ans court du 1er janvier suivant l'interruption ou, pour un recours juridictionnel, du 1er janvier suivant le passage en force de chose jugée (art. 2). Elle ne court pas contre le créancier qui ne peut agir ni contre celui qui ignore légitimement sa créance (art. 3). L'administration doit l'invoquer avant que le juge du premier degré se prononce au fond (art. 7).

Responsabilité médicale. Les actions contre les professionnels et établissements de santé publics ou privés au titre d'actes de prévention, de diagnostic ou de soins se prescrivent par dix ans à compter de la consolidation du dommage (CSP, art. L. 1142-28).

### Représentation

Ministère d'avocat obligatoire pour une demande de somme d'argent (CJA, art. R. 431-2), sauf dispenses de l'article R. 431-3, en particulier lorsque le défendeur est une collectivité territoriale, un établissement public local ou un établissement public de santé (5°), et pour les litiges individuels des agents (3°).

### Conditions à établir avant dépôt

Demande préalable reçue par la personne publique et date établie ; décision expresse, ou rejet implicite né du silence de deux mois ; requête dans le délai si le rejet exprès mentionne les voies et délais ; créance non prescrite, avec les actes interruptifs datés ; fait générateur, préjudice et lien de causalité étayés par pièces (condition générale de fond, aucune décision de principe relue pour l'énoncer : non vérifié).

### Rejets observés

- Prescription quadriennale opposée à des demandes de réparation du préjudice d'anxiété lié à l'amiante, le délai courant de l'année de connaissance de l'attestation d'exposition (TA Rennes, 11 juin 2026, n° 2506903).

### Voies de recours

Appel dans les deux mois, sauf actions indemnitaires hors commande publique n'excédant pas 10 000 euros, jugées en dernier ressort (CJA, art. R. 811-1, 8°, et R. 222-14).

## 6. Fonction publique

### Recours administratif préalable obligatoire des militaires

Tout recours contentieux d'un militaire contre un acte relatif à sa situation personnelle est précédé, à peine d'irrecevabilité, d'un recours administratif préalable examiné par la commission des recours des militaires ; ce recours conserve le délai contentieux jusqu'à la décision ; les autres recours administratifs sont sans incidence sur ce délai. Sont exclus les actes concernant le recrutement, l'exercice du pouvoir disciplinaire ou pris en application de l'article L. 4139-15-1, ainsi que les actes pris en application des codes des pensions et de la procédure des articles 112 à 124 du décret n° 2012-1246 (C. défense, art. R. 4125-1, version en vigueur depuis le 1er mars 2018).

La commission est saisie dans les deux mois de la notification ou de la publication de l'acte, ou de la naissance d'un rejet implicite, par tout moyen conférant date certaine, avec la copie de l'acte et l'énoncé des griefs ; à défaut de copie produite dans les deux semaines d'une mise en demeure, l'intéressé est réputé avoir renoncé ; un recours tardif est déclaré forclos (C. défense, art. R. 4125-2). La commission notifie la décision du ministre dans les quatre mois ; cette décision se substitue à la décision initiale ; le silence de quatre mois vaut rejet (C. défense, art. R. 4125-10).

### Médiation préalable obligatoire

Les recours contre certaines décisions individuelles concernant des personnes physiques, dont la liste est fixée par décret, sont précédés à peine d'irrecevabilité d'une tentative de médiation (CJA, art. L. 213-11). Pour les agents publics, sont visées les décisions individuelles défavorables relatives à la rémunération, les refus de détachement, de disponibilité ou de congés non rémunérés des contractuels, la réintégration ou le réemploi, le classement après avancement de grade ou promotion interne, la formation professionnelle, les mesures en faveur des travailleurs handicapés et l'aménagement des conditions de travail (décret n° 2022-433 du 25 mars 2022, art. 2), pour les agents des académies figurant sur une liste arrêtée par les ministres et des collectivités ayant conventionné avec leur centre de gestion (art. 3). La médiation est engagée dans le délai de recours contentieux ; si la notification ne mentionne pas l'obligation et les coordonnées du médiateur, le délai ne court pas (CJA, art. R. 213-10). La requête non précédée de la médiation est rejetée par ordonnance et transmise au médiateur, réputé saisi à la date d'enregistrement (CJA, art. R. 213-12).

### Juridiction, représentation, délais

Les litiges d'ordre individuel des agents relèvent du tribunal du lieu d'affectation ; en cas de nomination ou de changement d'affectation, du lieu de la nouvelle affectation ; en cas de cessation d'activité, de la dernière affectation (CJA, art. R. 312-12). Le ministère d'avocat n'est pas requis (CJA, art. R. 431-3, 3°). Le délai de droit commun est celui de l'article R. 421-1 ; le silence de l'administration dans ses relations avec ses agents vaut rejet (CRPA, art. L. 231-4, 5°).

### Rejets sans examen au fond observés

- Militaire n'ayant pas saisi la commission avant de contester un refus d'engagement dans la gendarmerie (TA Strasbourg, 15 avril 2026, n° 2306651).
- Recours préalable exercé contre un simple avis, acte préparatoire non susceptible de recours (TA Châlons-en-Champagne, ord., 5 octobre 2026, n° 2603276).

### Voies de recours

Appel dans les deux mois (CJA, art. R. 811-2), avec avocat (R. 811-7), sauf litiges de pensions de retraite des agents, jugés en dernier ressort (CJA, art. R. 811-1, 7°).

## 7. Points non vérifiés

- Compétence territoriale en matière fiscale et d'urbanisme.
- Caractère franc des délais de l'article R.* 199-1 du LPF, du livre IX du CESEDA, de l'article R. 4125-2 du code de la défense et du délai du recours Tarn-et-Garonne.
- Point de départ du délai d'un mois de l'article L. 600-12-2 du code de l'urbanisme et son application aux décisions antérieures au 28 novembre 2025.
- Délai d'appel des jugements rendus selon la procédure collégiale de l'article L. 911-1 du CESEDA.
- Sanction du défaut de notification du référé précontractuel (CJA, art. R. 551-1) et délai du pourvoi contre l'ordonnance.
- Ministère d'avocat aux Conseils devant le Conseil d'État.
- Article R. 222-15 du CJA et article R.* 197-4 du LPF.
