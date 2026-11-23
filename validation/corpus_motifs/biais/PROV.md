# Référé-provision civil (famille PROV) : biais de l'agent v50, règles proposées

```json
{
  "fiche": "plugins/contentieux/skills/mecanique-des-exercices/references/refere-civil-835-provision.md",
  "etabli_le": "2026-11-23",
  "base": "index_v50.json, famille PROV, 40 sondes ; issues réelles relues dans le dispositif des 40 décisions",
  "regles": [
    {
      "id": "PROV-R1-expertise-sur-l-execution",
      "condition": "obligation_non_serieusement_contestable",
      "tableau": "ce_qui_la_fait_tomber",
      "position": "première ligne marquée de la liste",
      "texte": "La mauvaise exécution que le débiteur oppose au prix ou aux honoraires réclamés devient une contestation sérieuse lorsqu'une expertise judiciaire, ordonnée et non encore déposée, porte sur la qualité de la prestation, les causes du dommage ou les responsabilités dont dépend l'obligation : le juge des référés ne peut préjuger ni la faute ni l'exception d'inexécution (Cass. 3e civ., 14 mai 2013, n° 12-17.471 ; Cass. 3e civ., 18 mai 2017, n° 16-16.808). Hors ce cas, la preuve de l'inexécution incombe au débiteur, et une allégation sans pièce, des réserves levées ou des défauts mineurs au regard du prix laissent la provision, au besoin réduite (C. civ., art. 1353 ; Cass. com., 14 oct. 2026, n° 25-15.254 ; Cass. 3e civ., 11 avr. 2012, n° 11-11.200).",
      "marqueurs": [
        "mauvaise (?:exécution|réalisation)",
        "malfa[çc]ons?",
        "d[ée]sordres",
        "non[- ]conform",
        "exception d[’']inex[ée]cution",
        "causes? et (?:les )?circonstances",
        "d[ée]terminer les responsabilit"
      ],
      "exige": [
        "ordonn\\w* (?:une |la )?(?:nouvelle )?(?:mesure d[’'])?expertise|expertise (?:judiciaire |médicale |technique )?(?:a été |est |avait été )?ordonnée|désign\\w* en qualité d[’']expert|expertise (?:judiciaire )?(?:en cours|toujours en cours)"
      ],
      "sources_lues": [
        "Cass. 3e civ., 14 mai 2013, n° 12-17.471",
        "Cass. 3e civ., 18 mai 2017, n° 16-16.808",
        "Cass. com., 14 oct. 2026, n° 25-15.254",
        "Cass. 3e civ., 12 nov. 2020, n° 19-21.764",
        "Cass. 3e civ., 11 avr. 2012, n° 11-11.200",
        "Cass. 2e civ., 18 oct. 2007, n° 06-20.938",
        "C. civ., art. 1353"
      ],
      "origine": "analyse des 40 sondes PROV de v50, 23 novembre 2026",
      "frequence": "2 sur 2 sondes où une expertise judiciaire est ordonnée sur l'exécution ou les causes : provision refusée en appel ; 3 sur 3 sondes où la malfaçon est seulement alléguée, les réserves levées ou les défauts mineurs : provision maintenue",
      "depuis": "1976-01-01",
      "contre": "Cass. 2e civ., 18 oct. 2007, n° 06-20.938 : une fois le rapport contradictoire déposé et concluant à la faute, la provision peut être allouée (https://librejustice.fr/decision/HvrXzen08eaR).",
      "corrige": ["GENP-PROV-2204453"],
      "consolide": ["GENP-PROV-2203521"],
      "risque": []
    },
    {
      "id": "PROV-R2-defendeur-defaillant",
      "condition": "obligation_non_serieusement_contestable",
      "tableau": "ce_qui_la_fait_tomber",
      "position": "deuxième ligne marquée de la liste",
      "texte": "Le silence du défendeur défaillant ne vaut pas reconnaissance : le juge n'alloue la provision que si les pièces du demandeur établissent l'acte qui fonde la somme, son exigibilité et son montant (CPC, art. 472, al. 2, hors la faculté de l'alinéa 3 ouverte aux instances introduites depuis le 1er octobre 2026 sur assignation à personne ; C. civ., art. 1353 ; Cass. soc., 4 mars 1987, n° 84-40.704). Il dit n'y avoir lieu à référé quand ni l'acte ni la nature de la dette ne sont identifiés, ou quand l'exigibilité dépend d'un fait (fin d'une mission, réussite d'un recrutement, levée de réserves) que le dossier montre discuté ; un bail, un acte, un protocole, une reconnaissance, un mandat exécuté, des appels de charges du syndicat ou des livraisons du fournisseur, chiffrés par un décompte ou un commandement, suffisent en revanche.",
      "marqueurs": [
        "n[’']a pas (?:constitué avocat|comparu)",
        "n[’']ont pas (?:constitué avocat|comparu)",
        "ni présente?,? ni représentée?",
        "non comparante?",
        "(?:défendeur|défenderesse|débiteur|débitrice) (?:est |était )?défaillante?"
      ],
      "sources_lues": [
        "CPC, art. 472 (version en vigueur depuis le 1er octobre 2026, décret n° 2026-683)",
        "C. civ., art. 1353",
        "Cass. soc., 4 mars 1987, n° 84-40.704",
        "Cass. com., 18 juin 1985, n° 84-12.160"
      ],
      "origine": "analyse des 40 sondes PROV de v50, 23 novembre 2026",
      "frequence": "défendeur défaillant dans 20 sondes sur 40 : 8 refus, 12 provisions ; l'agent répond oui dans 19 des 20",
      "depuis": "1976-01-01",
      "contre": "Dans l'échantillon, 12 provisions allouées contre un défaillant, toutes appuyées sur un bail, un acte authentique, un protocole, une reconnaissance, un mandat exécuté, des appels de charges ou des livraisons.",
      "corrige": ["GENP-PROV-2400589", "GENP-PROV-2458275", "GENP-PROV-2500440"],
      "risque": ["GENP-PROV-2455948", "GENP-PROV-2357764", "GENP-PROV-2451470"]
    },
    {
      "id": "PROV-R3-peine-seule",
      "condition": "obligation_non_serieusement_contestable",
      "tableau": "ce_qui_la_fait_tomber",
      "position": "troisième ligne marquée de la liste ; remplace pour tous domaines la ligne « clause pénale » de la seconde condition, aujourd'hui gardée par le bail",
      "texte": "Le juge des référés ne peut modérer une clause pénale (C. civ., art. 1231-5) et n'alloue sur la peine que la part qui lui paraît justifiée (Cass. 3e civ., 14 déc. 1988, n° 87-14.424) ; quand la provision ne porte que sur une pénalité forfaitaire dont le débiteur, après avoir réglé le principal, conteste le montant comme excessif, les juges des référés la refusent en entier, et l'offre amiable d'une somme moindre ne vaut pas reconnaissance de cette part (pourparlers transactionnels : Cass. 1re civ., 5 févr. 2014, n° 13-10.791, rendu sur la prescription). Seuls restent alors provisionnables, si la demande porte sur des intérêts conventionnels, les intérêts au taux légal depuis la mise en demeure (C. civ., art. 1231-6).",
      "marqueurs": [
        "clause p[ée]nale",
        "p[ée]nalit[ée]s? (?:de retard|contractuelles?|forfaitaires?)",
        "(?:indemnit[ée]|p[ée]nalit[ée]) (?:forfaitaire )?de \\d+ (?:euros|€) par jour",
        "1231-5|article 1152",
        "int[ée]r[êe]ts? (?:de retard )?major[ée]s?"
      ],
      "sources_lues": [
        "C. civ., art. 1231-5 et 1231-6",
        "Cass. 3e civ., 14 déc. 1988, n° 87-14.424",
        "Cass. 2e civ., 10 juill. 1978, n° 77-11.897",
        "Cass. 1re civ., 5 févr. 2014, n° 13-10.791",
        "TJ Paris, référés, 16 déc. 2025, n° 25/54614",
        "TJ Clermont-Ferrand, référés, 19 nov. 2024, n° 24/00296"
      ],
      "origine": "analyse des 40 sondes PROV de v50 et requête dédiée du 23 novembre 2026 (12 décisions de référé 2024-2026 vues par leur résumé, 2 lues)",
      "frequence": "2 sur 2 décisions de référé lues (requête dédiée) refusent la provision sur la peine contestée ; les 10 autres résultats de la requête, vus par leur seul résumé machine, vont dans le même sens sans avoir été lus ; dans l'échantillon, 1 sur 1 demande portant sur la seule peine est rejetée en entier",
      "depuis": "1978-07-10",
      "contre": "Cass. 2e civ., 10 juill. 1978, n° 77-11.897 : le pouvoir du juge du fond de modifier une indemnité conventionnelle n'exclut pas la provision quand la dette n'est pas sérieusement contestable (https://librejustice.fr/decision/XfRJ8TYIiqVq).",
      "corrige": ["GENP-PROV-2359451"],
      "risque": []
    },
    {
      "id": "PROV-R4-paiement-allegue-accord",
      "condition": "obligation_non_serieusement_contestable",
      "tableau": "ce_qui_la_remplit",
      "position": "première ligne de la liste",
      "texte": "Le paiement que le débiteur invoque n'est une contestation sérieuse que s'il le prouve (C. civ., art. 1353, al. 2 ; Cass. com., 20 janv. 1981, n° 79-13.050) ; quand le créancier impute un paiement établi et réduit sa demande, la provision est allouée pour le solde. L'accord du débiteur sur le principe et le montant de la dette, constaté à l'audience, ôte toute contestation : le juge condamne par provision, au besoin avec des délais de paiement (C. civ., art. 1343-5).",
      "marqueurs": [
        "(?<!n.)invoque[\\w ,]{0,25} paiements?",
        "trop[- ]per[çc]u",
        "(?:soutient|affirme|pr[ée]tend) avoir (?:d[ée]j[àa] )?(?:pay[ée]|r[ée]gl[ée]|rembours[ée])",
        "accord des parties",
        "paiements? (?:partiels? )?(?:all[ée]gu[ée]s?|invoqu[ée]s?)"
      ],
      "sources_lues": [
        "C. civ., art. 1353 et 1343-5",
        "Cass. com., 20 janv. 1981, n° 79-13.050"
      ],
      "origine": "analyse des 40 sondes PROV de v50, 23 novembre 2026",
      "frequence": "2 sur 2 sondes (paiement allégué sans preuve, accord constaté à l'audience) : provision allouée ; l'agent répondait non dans les deux",
      "depuis": "1981-01-20",
      "contre": "Aucune décision lue où un paiement prouvé couvre toute la dette ; la ligne existante « Le débiteur oppose un moyen de fond sérieux ou prouve le paiement » couvre ce cas.",
      "corrige": ["GENP-PROV-2402552", "GENP-PROV-2554444"],
      "risque": []
    }
  ],
  "reformulations": [
    {
      "chemin": "conditions_decisives[1].ce_qui_la_fait_tomber[2]",
      "actuel": "Aucune part du montant réclamé n'échappe à une contestation sérieuse, une contestation limitée à l'étendue de l'obligation ne justifiant pas le rejet de toute provision.",
      "propose": "Aucune part du montant réclamé n'échappe à une contestation sérieuse. La provision partielle malgré une contestation suppose que le débiteur admette le principe de son obligation et ne discute que son étendue (Cass. 2e civ., 11 juill. 2013, n° 12-24.722) ; un doute sur l'acte, l'exigibilité ou l'imputabilité, une peine modérable ou une offre faite pour transiger ne font pas apparaître une telle part.",
      "motif": "Ligne non marquée, présente dans chaque contrat remis ; l'agent en tire que tout doute ne fait que réduire la provision (7 des 9 refus manqués)."
    },
    {
      "chemin": "conditions_decisives[1].ce_qui_la_fait_tomber[3] (clause pénale, garde « bail »)",
      "actuel": "… Limite : la provision sur une clause pénale reste possible pour la part qui paraît justifiée, et une pénalité forfaitaire claire et modérée peut être allouée. …",
      "propose": "Retirer la garde « exige » propre au bail ou remplacer la ligne par PROV-R3 ; si la ligne est gardée pour ses précisions locatives, écrire la limite ainsi : « Limite, rare (1 décision sur 12 vues) : une pénalité forfaitaire claire et modérée a été allouée en plus du principal. »",
      "motif": "La garde « bail » a écarté la ligne de la sonde 2359451 (viager) ; la limite actuelle se lit comme l'annonce d'une provision partielle sur la peine."
    },
    {
      "chemin": "conditions_decisives[0].ce_qui_la_remplit[1] (factures)",
      "actuel": "La créance de factures est non sérieusement contestable lorsque chaque facture se rattache à un bon de livraison signé, à un bon de commande signé ou à un écrit du débiteur chiffrant ce qu'il doit ; …",
      "propose": "Ajouter après « ce qu'il doit » : « et que la prestation facturée est établie comme exécutée (livraison, mission achevée, événement d'exigibilité survenu) ».",
      "motif": "Sonde 2500440 : l'agent assimile le mandat signé à un « bon de commande signé » et conclut oui alors que la tranche facturée dépendait d'un recrutement discuté."
    }
  ]
}
```

## 1. Ce qui ressort

Le 4/20 sur les refus mesure en partie l'étiquetage. L'usine (`usine.py`, fonction `issue`) tire l'issue PROV du champ `solution` de LibreJustice. Pour un arrêt d'appel, ce champ dit si l'appel a réussi, et non si la provision a été allouée ; pour deux ordonnances, il a classé « rejet » une décision qui allouait la provision et ne rejetait qu'une demande accessoire. Sur les 40 sondes, 10 ont une étiquette contraire au dispositif :

- 8 étiquetées « non » où la provision a été allouée ou maintenue : 2203185, 2301459, 2300124, 2202637, 2218821, 2304751 (arrêts confirmant, sur appel du débiteur, l'ordonnance qui l'avait condamné), 2501256 (seule la provision pour résistance abusive est rejetée), 2600448 (seuls les délais de paiement sont refusés). L'agent a répondu oui dans les huit, à juste titre.
- 2 étiquetées « oui » où la provision a été refusée : 2203521 et 2204453 (arrêts infirmant l'ordonnance qui l'avait allouée). L'agent a répondu non dans la première, à juste titre, et oui dans la seconde, à tort.

La sonde 2202637 porte deux provisions de sens opposé (la non-concurrence de l'appelante, rejetée ; la rétrocession de l'intimée, allouée et réduite) : elle reste ambiguë et devrait sortir de l'échantillon.

Issues relues dans les dispositifs, l'échantillon compte 26 provisions allouées et 14 refusées. L'agent v50 répond juste sur 24 des 26 et sur 5 des 14. Le biais vers « oui » existe donc, mais il porte sur 9 refus et non sur 16.

Il se concentre sur le défendeur défaillant. Vingt sondes opposent un demandeur à un défendeur qui n'a ni comparu ni constitué avocat : 8 refus, 12 provisions, et l'agent répond oui 19 fois sur 20. Sur les 20 sondes contradictoires (TJ ou appel), il répond juste 16 fois. Sept des neuf refus manqués sont des défauts de comparution.

## 2. Les 40 sondes, issue relue

Légende : réel = issue relue dans le dispositif ; agent = réponse finale v50 ; « visible » dit si l'élément qui a décidé figure dans `dossier_remis.md` ; « règles » = lignes proposées qui se déclenchent (simulation des regex sur le dossier et la réponse finale).

| Sonde | Étiq. | Réel | Agent | Ce qui a décidé | Visible | Règles |
|---|---|---|---|---|---|---|
| 2203185 (CA) | non | oui | oui | devis signé ; non-finitions mineures au regard du prix ; provision partielle de 15 000 € confirmée | oui | |
| 2204453 (CA) | oui | non | oui | honoraires de soins dentaires ; expertise médicale ordonnée sur la qualité des soins ; accord de conciliation contesté | oui | R1 |
| 2205185 (CA) | oui | oui | oui | loyers ; impropriété invoquée sans preuve, clause mettant les autorisations à la charge du preneur | oui | |
| 2301459 (CA) | non | oui | oui | réserves levées par écrit, critiques postérieures à l'assignation | oui | |
| 2358094 | oui | oui | oui | bail commercial, commandement ; défaillant | oui | R2 |
| 2400947 | oui | oui | oui | bail d'habitation, reliquat de 27,36 € ; défaillant | oui | R2 |
| 2401992 | oui | oui | oui | bail ; solde antérieur et taxes non justifiés retranchés, 37 219 € sur 86 946 € ; défaillant | oui | R2, R3 |
| 2450588 | non | non | oui | note d'honoraires d'architecte « solde de tout compte » ; 14 réserves non levées révélées par les pièces ; défaillant | non | R2 |
| 2451470 | oui | oui | oui | promesse authentique, indemnité d'immobilisation ; 15 750 € sur 17 500 € ; défaillant | oui | R2 |
| 2500440 | non | non | oui | mandat de recrutement imprécis sur la nouvelle recherche après l'échec du premier candidat ; défaillant | oui | R2 |
| 2501143 | oui | oui | oui | mandat de vente, vente établie par la déclaration d'achat ; défaillant | oui | R2 |
| 2501256 | non | oui | oui | protocole signé chiffrant l'arriéré ; défaillant | oui | R2 |
| 2600481 | non | non | non | convention où la société rémunère la praticienne, demande de « rétrocession » inverse, montants changeants ; défaillant | oui | R2 |
| 2655171 | non | non | oui | décompte portant 45 902 € d'échéances 2018-2025 injustifiées, supérieures au solde ; défaillant | non | R2, R3 |
| 2203521 (CA) | oui | non | non | expertise ordonnée sur les causes de l'incendie ; garantie et faute contestées | oui | R1 |
| 2211337 (CA) | oui | oui | oui | victime d'accident ; expertise sur le seul préjudice, droit à indemnisation non discuté | oui | |
| 2300124 (CA) | non | oui | oui | malfaçons alléguées sans justification | oui | |
| 2301937 | non | non | non | chantier inachevé, constat et rapport d'expert de partie, facture intermédiaire unilatérale | oui | |
| 2357764 | oui | oui | oui | charges de copropriété ; défaillant | en partie | R2 |
| 2359451 | non | non | oui | provision demandée sur la seule clause pénale d'un viager, rentes réglées, offre amiable de 2 500 € ; peine modérable | oui | R3 |
| 2400589 | non | non | oui | ni acte ni cause dans l'exposé ; facture « bon pour accord » à signature non attribuable ; défaillant | en partie | R2 |
| 2401023 | non | non | oui | approbation des comptes 2023-2024 non produite, dette déjà jugée incluse ; défaillant | non | R2 |
| 2402552 | oui | oui | non | protocole ; paiement de 78 000 € prouvé et imputé, second paiement non prouvé | oui | R4 |
| 2451060 | oui | oui | oui | avenant-protocole de résiliation, commandement ; défaillant | oui | R2 |
| 2458275 | non | non | oui | ni acte ni cause dans l'exposé ; reconnaissance du gérant portant sur une dette déjà jugée contre sa société ; défaillant | en partie | R2 |
| 2554444 | oui | oui | non | accord des parties constaté à l'audience, provision de 50 000 € avec échéancier | oui | R4 |
| 2600448 | non | oui | oui | situation de travaux reconnue par écrit et à l'audience | oui | |
| 2202637 (CA) | non | oui (ambiguë) | oui | rétrocession d'honoraires ramenée à 62 514 € ; l'autre provision rejetée | oui | |
| 2218821 (CA) | non | oui | oui | indemnités d'occupation, appel du preneur | oui | |
| 2301736 | non | non | oui | prêt et reconnaissance établis ; le juge exige du prêteur la preuve du non-remboursement ; défaillant | non | R2 |
| 2304751 (CA) | non | oui | oui | loyers, appel du preneur | oui | |
| 2309013 | non | non | non | retenue de 5 % payable à la levée des réserves ; 60 réserves constatées | oui | |
| 2356746 | oui | oui | oui | loyers ; exception d'incompétence rejetée | oui | |
| 2400558 | oui | oui | oui | loyers ; majoration de 10 % refusée | oui | R2, R3 |
| 2401592 | non | non | non | factures émises au nom d'une autre société après transfert du permis | en partie | |
| 2451668 | oui | oui | oui | loyers ; cessation des paiements alléguée | oui | |
| 2452985 | oui | oui | oui | promesse authentique, exigibilité admise par écrit ; défaillant | oui | R2, R3 |
| 2455948 | oui | oui | oui | factures et bons de livraison tamponnés ; défaillant | en partie | R2 |
| 2550163 | oui | oui | oui | reconnaissance de dette ; défaillant | en partie | R2 |
| 2557499 | oui | oui | oui | loyers alloués malgré une contestation sérieuse sur la qualification du bail | oui | |

Les éléments que l'agent ne pouvait pas voir tiennent aux pièces du demandeur, lues par le juge et absentes de l'exposé : réserves de l'annexe (2450588), ligne injustifiée du décompte (2655171), approbation des comptes manquante (2401023), preuve exigée du non-remboursement (2301736). Ces quatre refus ne sont pas récupérables par une règle tirée du dossier sans faire basculer des provisions identiques en apparence (2401992 pour le bail, 2357764 pour les charges, 2550163 pour le prêt). Le motif de 2301736 va d'ailleurs contre l'article 1353, alinéa 2, du code civil : aucune règle ne doit le reproduire.

## 3. L'erreur de raisonnement récurrente

Deux raisonnements reviennent dans les réponses fausses.

Le premier fait du silence du défendeur une absence de contestation. On le lit dans sept des huit refus manqués sur défaut : « il ne lui permet pas d'imaginer une contestation que rien dans le dossier ne fait apparaître » (2450588), « le dossier ne montre aucune cause d'échec » (2401023), « une créance que personne ne discute » (2400589). Les juges font l'inverse. L'article 472, alinéa 2, du code de procédure civile ne les laisse faire droit à la demande que s'ils l'estiment bien fondée, et la Cour de cassation casse la décision qui accueille la demande au seul motif que le défendeur n'a pas comparu ni contesté (Cass. soc., 4 mars 1987, n° 84-40.704) ou qui vise les pièces sans les analyser (Cass. com., 18 juin 1985, n° 84-12.160, honoraires). Dans l'échantillon, le juge examine les pièces du défaillant absent et refuse 8 fois sur 20 lorsqu'elles n'établissent pas l'acte, l'exigibilité ou le montant. La consigne de revue du hook Stop (« une cause d'échec ne vaut rien si le dossier n'en montre pas les faits ») renforce l'erreur dans ce cas, puisque les faits de l'échec sont dans les pièces que l'agent ne voit pas.

Le second tient tout doute pour une simple réduction du montant. Sept des neuf réponses fausses le formulent : « au moins 2 500 € échappent à toute contestation » (2359451), « si le juge avait un doute sur une partie de la somme, il réduirait la provision, sans la refuser en entier » (2450588), « le juge accorde souvent une provision réduite » (2458275). L'agent tire cette règle de la ligne non marquée de la seconde condition, présente dans chaque contrat. L'arrêt qui la fonde (Cass. 2e civ., 11 juill. 2013, n° 12-24.722) est plus étroit : il casse le refus de toute provision parce que l'assureur « ne contestait ni les dommages ni le principe de son obligation ». Quand le doute porte sur l'acte (2400589, 2458275), sur l'exigibilité (2500440), sur une peine que le juge du fond peut modérer (2359451) ou sur la bonne exécution soumise à expertise (2204453), les juges refusent en entier.

Les refus que l'agent trouve ont un point commun : le dossier montre un défaut précis du titre du demandeur (mécanisme contractuel inversé en 2600481, factures émises au nom d'un tiers en 2401592, chantier inachevé et rapport d'expert en 2301937, réserves constatées en 2309013, expertise ordonnée sur les causes en 2203521). À l'inverse, ses deux faux « non » viennent d'une lecture trop sévère : un paiement invoqué mais non prouvé (2402552), un accord constaté à l'audience lu comme une extinction de l'instance (2554444).

Pour l'appel, l'échantillon contient 10 arrêts. La cour confirme ou ajuste la provision dans 8 (dont 6 sur appel du débiteur) et l'infirme dans 2, chaque fois parce qu'une expertise ordonnée portait sur l'exécution ou les causes. L'agent répond juste sur 9 des 10 ; la difficulté apparente de l'appel venait de l'étiquette.

## 4. Les règles et leurs décomptes

Décomptes sur les issues relues. Une sonde est dite « corrigée » quand la règle se déclenche et que son texte vise l'élément visible qui a décidé ; « risquée » quand elle se déclenche sur une provision allouée et qu'une lecture large de son texte pourrait faire répondre non.

**R1, expertise sur l'exécution.** Corrige 2204453. Consolide 2203521, déjà juste. Risque nul dans l'échantillon : la garde exige une expertise ordonnée, les marqueurs une contestation de l'exécution ou des causes ; 2211337 (expertise sur le seul préjudice) ne la déclenche pas. Sur les étiquettes actuelles, la correction de 2204453 compterait comme un échec nouveau, puisque la sonde est étiquetée oui.

**R2, défendeur défaillant.** Se déclenche sur les 20 défauts de comparution et nulle part ailleurs. Corrige 2400589 et 2458275 (ni acte ni nature de la dette dans l'exposé) et 2500440 (tranche dont l'exigibilité dépend d'un recrutement que le dossier montre discuté). Ne corrige pas 2450588, 2655171, 2401023, 2301736. Risques : 2455948 et 2357764, où la nature de la dette se déduit seulement de la qualité du demandeur (fournisseur, syndicat) que le texte nomme pour cette raison ; 2451470, où l'indemnité d'immobilisation suppose la non-réalisation de la vente du fait du bénéficiaire, alléguée et non discutée. Risque très faible sur 2550163 (la nature de la dette, un prêt, est dite). Les neuf autres provisions sur défaut reposent sur un bail, un acte, un protocole ou un mandat exécuté nommés dans l'exposé. Une variante qui aurait aussi visé la facture ou la note d'honoraires sans écrit du débiteur corrigeait 2450588 mais menaçait 2455948 : elle n'est pas retenue.

**R3, peine seule.** Corrige 2359451. Se déclenche aussi sur 2401992, 2400558, 2452985 et 2655171, où la demande porte sur un principal : le texte vise la demande limitée à la peine, aucun basculement attendu. Dans 2452985, l'agent écrit déjà que l'indemnité d'immobilisation n'est pas une clause pénale. La règle tient compte de l'état du droit : la Cour de cassation permet au juge des référés d'allouer la part de la peine qui lui paraît justifiée (1978, 1988) ; le texte décrit la pratique des juges des référés, qui la refusent quand la peine est contestée comme excessive, et le reste dû au taux légal.

**R4, paiement allégué et accord.** Corrige 2402552 et 2554444, les deux faux « non ». Ne se déclenche sur aucune autre sonde.

Totaux sur les issues relues : refus justes de 5 à 10 sur 14 au plus ; provisions justes de 24 à 26 sur 26, moins 0 à 3 sondes menacées par R2 ; ensemble de 29 à 36 sur 40 au plus. Sur les étiquettes actuelles du banc : de 21 à 26 sur 40 au plus (refusées 4 à 8 sur 20, accordées 17 à 18 sur 20), les 8 sondes mal étiquetées « non » restant comptées en échec quelle que soit la règle.

Ces décomptes viennent d'une simulation des regex sur le dossier et la réponse finale, et de la lecture des réponses. Ils ne remplacent pas un rejeu : la conduite de l'agent face au texte reste à mesurer, R2 en particulier.

## 5. Lignes existantes qui poussent vers « oui »

1. Seconde condition, troisième ligne non marquée : « Aucune part du montant réclamé n'échappe à une contestation sérieuse, une contestation limitée à l'étendue de l'obligation ne justifiant pas le rejet de toute provision. » Elle figure dans chaque contrat et nourrit le raisonnement « tout doute réduit sans supprimer ». Reformulation proposée dans le bloc JSON, avec la condition de l'arrêt de 2013.
2. Seconde condition, ligne marquée « clause pénale » : la garde `exige` limitée au bail l'a écartée de 2359451, et sa limite (« la provision sur une clause pénale reste possible pour la part qui paraît justifiée ») annonce une provision partielle que les juges n'accordent presque jamais.
3. Première condition, ligne « factures » de `ce_qui_la_remplit` : sans exigence d'exécution de la prestation facturée, l'agent l'étend à un mandat signé dont la tranche n'était pas exigible (2500440).
4. Corps de la fiche, hors contrat mais lu par l'agent quand il ouvre la fiche : § 2 (« des contestations qui ne portent que sur l'étendue… ne justifient pas le rejet de toute provision »), § 3, dernière puce sur le montant, et § 7 (« Quand le débiteur ne conteste que l'étendue… ») répètent la règle de 2013 sans sa condition ; § 2, « Charge de la preuve », ne dit rien du défendeur défaillant ni de l'article 472.
5. Hors fiche, dans `hook.py` : la phrase de revue « une cause d'échec ne vaut rien si le dossier n'en montre pas les faits » pousse vers oui quand le défendeur fait défaut.

Le contrat remis à v50 était surtout générique : une ligne marquée ne s'est appliquée que dans 16 sondes sur 40, et aucun contrat n'a été retrouvé dans le journal brut de cinq sondes. Une ligne sans rapport (la caution) s'est affichée pour 2400589. Le champ `premiere_reponse` est vide pour toute la famille PROV : l'effet propre du hook Stop n'a pas pu être mesuré.

## 6. Correction de l'étiquetage

Pour la famille `refere-provision-civil`, l'issue devrait se lire dans le dispositif plutôt que dans `solution` : oui quand la décision condamne « par provision » ou « à titre provisionnel » au profit du demandeur à la provision, ou confirme l'ordonnance qui l'avait fait ; non quand elle dit n'y avoir lieu à référé sur la provision ou en déboute sans aucune condamnation provisionnelle ; aucune issue quand deux provisions de sens contraire sont en cause (2202637). Ni `usine.py` ni les sondes n'ont été modifiés.

## 7. Sources lues

Textes, version en vigueur au 23 novembre 2026, lus sur LibreJustice :
- [CPC, art. 472](https://librejustice.fr/norm/fr/code-de-procedure-civile/472), rédaction issue du décret n° 2026-683, alinéa 3 applicable aux instances introduites depuis le 1er octobre 2026. Son application au référé-provision n'a pas été vérifiée.
- [C. civ., art. 1353](https://librejustice.fr/norm/fr/code-civil/1353), [1231-5](https://librejustice.fr/norm/fr/code-civil/1231-5), [1231-6](https://librejustice.fr/norm/fr/code-civil/1231-6), [1343-5](https://librejustice.fr/norm/fr/code-civil/1343-5).

Décisions de la Cour de cassation, texte intégral lu :
- [Cass. 2e civ., 11 juill. 2013, n° 12-24.722](https://librejustice.fr/decision/I8r47MFf3man), Bulletin : étendue de l'obligation, principe et dommages non contestés.
- [Cass. 3e civ., 14 mai 2013, n° 12-17.471](https://librejustice.fr/decision/N_P5Pa-CHqgC), inédit : expertise toujours en cours, contestation sérieuse.
- [Cass. 3e civ., 18 mai 2017, n° 16-16.808](https://librejustice.fr/decision/ep-d0EDoIxv1), inédit : responsabilité supposant la recherche d'une faute et d'un lien de causalité.
- [Cass. 2e civ., 18 oct. 2007, n° 06-20.938](https://librejustice.fr/decision/HvrXzen08eaR), Bulletin : provision fondée sur un rapport d'expertise contradictoire.
- [Cass. com., 14 oct. 2026, n° 25-15.254](https://librejustice.fr/decision/MM-BvMLCjOy_), Bulletin : preuve de l'inexécution à la charge du débiteur (opposition à injonction de payer).
- [Cass. 3e civ., 12 nov. 2020, n° 19-21.764](https://librejustice.fr/decision/tRSB5HfUpaOW), Bulletin : honoraires d'architecte, inversion de la charge de la preuve.
- [Cass. 3e civ., 11 avr. 2012, n° 11-11.200](https://librejustice.fr/decision/9WpyWdjyFwfx), inédit : réserves levées, solde du marché exigible en référé.
- [Cass. soc., 4 mars 1987, n° 84-40.704](https://librejustice.fr/decision/mtQvnX2s6erv), Bulletin, et [Cass. com., 18 juin 1985, n° 84-12.160](https://librejustice.fr/decision/TOoHjPiU37PW), Bulletin : article 472, examen de la demande du défendeur défaillant.
- [Cass. 3e civ., 14 déc. 1988, n° 87-14.424](https://librejustice.fr/decision/RXXGVv-GD0GJ), Bulletin, et [Cass. 2e civ., 10 juill. 1978, n° 77-11.897](https://librejustice.fr/decision/XfRJ8TYIiqVq), Bulletin : provision et clause pénale.
- [Cass. 1re civ., 5 févr. 2014, n° 13-10.791](https://librejustice.fr/decision/uQKHZF9-DqDY), Bulletin : pourparlers transactionnels non constitutifs de reconnaissance.
- [Cass. com., 20 janv. 1981, n° 79-13.050](https://librejustice.fr/decision/4cUcX3J9MPQh), Bulletin : paiement partiel non prouvé, provision intégrale.

Décisions de référé hors échantillon, texte lu : [TJ Paris, référés, 16 déc. 2025, n° 25/54614](https://librejustice.fr/decision/N52V2akK9NQF) (pénalités de retard seules, n'y avoir lieu) ; [TJ Clermont-Ferrand, référés, 19 nov. 2024, n° 24/00296](https://librejustice.fr/decision/Tpj9Fk0Mn3qV) (intérêts majorés refusés après paiement du principal, intérêts au taux légal alloués). Dix autres décisions de la même requête ont été vues par leur seul résumé machine : elles ne sont citées que comme indice de fréquence, sans fonder aucune affirmation de droit.

Échantillon : dispositif et motifs des 40 décisions lus (15 depuis `echecs_ech`, 25 par `decision.py`), avec les 40 dossiers remis, les 40 réponses finales et, pour chaque sonde, le contrat remis par le hook quand le journal brut le contenait.
