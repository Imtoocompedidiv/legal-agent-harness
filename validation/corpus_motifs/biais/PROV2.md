# Référé-provision civil (famille PROV), second tour : ce qui distingue les refus, règles proposées

```json
{
  "fiche": "plugins/contentieux/skills/mecanique-des-exercices/references/refere-civil-835-provision.md",
  "etabli_le": "2026-11-23",
  "base": "index_val3.json, famille PROV : 40 ordonnances de tribunaux judiciaires (20 allocations, 20 refus), jouées en v55 et v56, soit 80 sessions ; motifs et dispositifs des 40 décisions lus ; contrôle sur les 294 sondes GENP-PROV d'origine tribunal judiciaire sans etiquette_ambigue (dont les 40), dispositif relu pour les 26 sondes hors échantillon où une règle se déclenche",
  "regles": [
    {
      "id": "PROV2-R1-subsidiaires-et-moyen-de-fond",
      "condition": "obligation_non_serieusement_contestable",
      "tableau": "ce_qui_la_fait_tomber",
      "position": "rang 3 de la liste, avant la ligne « expertise » du premier tour (première ligne marquée)",
      "texte": "Le défendeur qui conclut à titre principal au rejet ne reconnaît pas la dette par ses demandes subsidiaires : contester le montant à titre subsidiaire ne vaut pas aveu (Cass. ass. plén., 29 mai 2009, n° 07-20.913), demander des délais ne vaut pas acquiescement (Cass. 1re civ., 28 mars 1995, n° 92-21.016), et une réduction, un plafond, la déduction du dépôt de garantie ou le renvoi d'un chef au fond ne font donc pas apparaître la part admise qu'exige une provision partielle (Cass. 2e civ., 11 juill. 2013, n° 12-24.722). Le moyen de fond qu'il articule à titre principal (cause légitime de retard, réserves non levées, désordres signalés, décompte qu'il dit incohérent, faute, préjudice ou causalité discutés) est une contestation dont le juge apprécie le sérieux sans en exiger la preuve à l'évidence, comme pour la cause d'exonération (Cass. 2e civ., 4 juin 2015, n° 14-13.405) ; un exposé qui résume ce moyen sans en reproduire les pièces ne le rend pas vain. Quand le défendeur ne discute pas la dette au fond (rejet sans moyen articulé, seule exception de procédure, paiement allégué sans preuve, obligation reconnue), ses demandes subsidiaires n'empêchent pas la provision (C. civ., art. 1353).",
      "marqueurs": [
        "(?:débout\\w*|rejet\\w*|contestations? sérieuses?|n['’]y avoir lieu|incompéten\\w*|mieux se pourvoir)[\\s\\S]{0,600}?(?:[àa] titre (?:plus |très |infiniment )?subsidiaire|subsidiairement|demande subsidiaire)[\\s\\S]{0,500}?(?:délais? de (?:paiement|grâce)|délai de \\w+ mois|r[ée]dui\\w+|ramener|plus (?:justes|basses) proportions|dédui\\w+|imput\\w+|ne saurait (?:être|excéder)|au-delà de|limit\\w+)"
      ],
      "exige": [],
      "depuis": "2015-06-04",
      "sources_lues": [
        "CPC, art. 835 (version en vigueur depuis le 1er janvier 2021)",
        "C. civ., art. 1353 (version en vigueur depuis le 1er octobre 2016)",
        "Cass. ass. plén., 29 mai 2009, n° 07-20.913, Bulletin",
        "Cass. 1re civ., 28 mars 1995, n° 92-21.016, Bulletin",
        "Cass. 2e civ., 11 juill. 2013, n° 12-24.722, Bulletin",
        "Cass. 2e civ., 4 juin 2015, n° 14-13.405, Bulletin"
      ],
      "origine": "second tour PROV, 23 novembre 2026 : 40 ordonnances de TJ, 80 sessions v55 et v56",
      "frequence": "marqueur présent dans 5 dossiers sur 40, tous des refus ; sur les 294 dossiers TJ, 14 refus et 3 allocations",
      "contre": "Les 3 allocations du corpus où le marqueur se déclenche relèvent des exceptions écrites dans la ligne : rejet sans moyen articulé suivi de délais (2355695, 2555223), paiement allégué sur une reconnaissance de dette admise (2301686). L'arrêt de 2015 statue sur une cause d'exonération d'une responsabilité de plein droit ; son extension aux autres moyens de fond est une inférence, signalée comme telle dans le texte.",
      "corrige": ["GENP-PROV-2400742 (v55)", "GENP-PROV-2400818", "GENP-PROV-2401660", "GENP-PROV-2402266", "GENP-PROV-2654197"],
      "consolide": ["GENP-PROV-2400742 (v56)"],
      "risque": ["GENP-PROV-2301686", "GENP-PROV-2355695", "GENP-PROV-2555223 (corpus, hors échantillon)"]
    },
    {
      "id": "PROV2-R2-provision-sur-prejudice",
      "condition": "obligation_non_serieusement_contestable",
      "tableau": "ce_qui_la_fait_tomber",
      "position": "rang 4 de la liste, juste après PROV2-R1",
      "texte": "La provision à valoir sur la réparation d'un préjudice (perte locative, trouble de jouissance, retard, préjudice moral ou financier) suppose que l'obligation de réparer échappe à la contestation dans chacun de ses éléments. Quand la responsabilité suppose la recherche d'une faute et d'un lien de causalité que le défendeur discute, le juge des référés ne peut les tenir pour acquis (Cass. 3e civ., 18 mai 2017, n° 16-16.808), ni allouer sans désigner le fondement qu'il retient (Cass. ass. plén., 16 nov. 2001, n° 99-20.114) ; contre une responsabilité de plein droit, la cause d'exonération invoquée s'apprécie dans son sérieux, sans devoir être établie (Cass. 2e civ., 4 juin 2015, n° 14-13.405). La provision reste possible quand le débiteur admet le principe et ne discute que l'étendue : offre ou plafond qu'il propose lui-même au juge, transaction, accord chiffré (Cass. 2e civ., 11 juill. 2013, n° 12-24.722). Les autres chefs de la demande (prix, loyers, factures) se jugent à part.",
      "marqueurs": [
        "(?:provision\\w*|provisionnel\\w*|par provision)[^.;\\n]{0,80}(?:sur|valoir sur|au titre d\\w*|en réparation d\\w*)[^.;\\n]{0,40}(?:préjudice|indemnisation|dommages?[- ](?:et[- ])?intérêts|réparation)",
        "(?:préjudice|indemnisation|réparation)[^.;\\n]{0,60}(?:à titre (?:de )?provision\\w*|provisionnel\\w*|par provision)",
        "perte (?:de loyers?|locative|de jouissance)|trouble de jouissance|préjudice (?:de jouissance|moral|financier|matériel)"
      ],
      "exige": [
        "débout\\w*|contestations? sérieuses?|mieux se pourvoir|n['’]y avoir lieu|conclut au rejet|sollicite le rejet|demande(?:nt)? (?:au juge )?de rejeter"
      ],
      "depuis": "2015-06-04",
      "sources_lues": [
        "CPC, art. 835",
        "Cass. 3e civ., 18 mai 2017, n° 16-16.808, inédit",
        "Cass. ass. plén., 16 nov. 2001, n° 99-20.114, Bulletin",
        "Cass. 2e civ., 4 juin 2015, n° 14-13.405, Bulletin",
        "Cass. 2e civ., 11 juill. 2013, n° 12-24.722, Bulletin"
      ],
      "origine": "second tour PROV, 23 novembre 2026 : 40 ordonnances de TJ, 80 sessions v55 et v56",
      "frequence": "marqueur et garde présents dans 5 dossiers sur 40, tous des refus ; sur les 294 dossiers TJ, 17 refus et 3 allocations",
      "contre": "Les 3 allocations du corpus relèvent des exceptions écrites : l'assureur demande lui-même de limiter la provision à un montant (2400927, 2501911), la facture n'est pas discutée et seuls les dommages-intérêts accessoires sont refusés (2402915). L'arrêt de 2017 est inédit ; la règle de fond qu'il approuve (faute et causalité à rechercher par le juge du fond) est celle de l'arrêt d'assemblée plénière de 2001 sur la motivation du fondement.",
      "corrige": ["GENP-PROV-2405742", "GENP-PROV-2400742 (v55)", "GENP-PROV-2400818", "GENP-PROV-2402266"],
      "consolide": ["GENP-PROV-2400449", "GENP-PROV-2400742 (v56)"],
      "risque": ["GENP-PROV-2354373 et GENP-PROV-2301178 (v56), au seul contrat du Stop, la réponse portant les mots de la garde", "GENP-PROV-2400927", "GENP-PROV-2402915", "GENP-PROV-2501911 (corpus, hors échantillon)"]
    }
  ],
  "reformulations": [
    {
      "chemin": "conditions_decisives[0].ce_qui_la_remplit[1] (preneur qui poursuit son activité)",
      "actuel": "Le preneur qui suspend ses loyers en invoquant un manquement du bailleur à son obligation de délivrance n'élève pas de contestation sérieuse lorsque les locaux restent exploitables […] Signal : le preneur a poursuivi son activité dans les lieux […] (Cass. civ. 3e, 6 juill. 2023, n° 22-15.923)",
      "propose": "Au fond, l'exception d'inexécution du preneur suppose des locaux rendus impropres à leur destination (Cass. 3e civ., 6 juill. 2023, n° 22-15.923, arrêt rendu au fond, qui casse faute de cette recherche). En référé, la poursuite de l'activité affaiblit l'exception sans l'écarter : si le preneur fait état de désordres signalés avant le commandement auxquels le bailleur ne répond pas, la contestation reste à peser.",
      "motif": "L'arrêt de 2023 n'est pas une décision de référé. La ligne a conduit l'agent à répondre oui dans 2400211 (v56, « La Cour de cassation juge que, dans ce cas, le preneur n'élève pas de contestation sérieuse ») ; le juge a refusé, retenant l'exception d'inexécution étayée et le décompte inexploitable."
    },
    {
      "chemin": "conditions_decisives[1].ce_qui_la_remplit[0] (délais de l'article 24 de la loi de 1989)",
      "actuel": "exige : [\"\\bbail\\b|loyer|locataire|bailleur\"]",
      "propose": "exige : [\"6 juillet 1989|bail d['’]habitation|logement|contentieux de la protection\"]",
      "motif": "Ligne propre au bail d'habitation, déclenchée par le mot « loyer » sur le bail commercial 2654197 (v55), où elle annonce une provision « pour le montant du décompte actualisé non contesté » alors que le preneur contestait le décompte et que le juge a refusé."
    },
    {
      "chemin": "gardes « exige » de conditions_decisives[0].ce_qui_la_fait_tomber[6], [0].ce_qui_la_remplit[1] et [1].ce_qui_la_remplit[0]",
      "actuel": "\"\\bbail\\b|…\" dans le JSON, lu par Python comme retour arrière + bail + retour arrière",
      "propose": "\"\\\\bbail\\\\b|…\"",
      "motif": "L'alternative « bail » de ces gardes ne peut jamais correspondre ; les autres mots (loyer, locataire, bailleur) les font tenir."
    },
    {
      "chemin": "hook.py, contrat_a_la_lecture et aiguillage (phrase finale du contrat)",
      "actuel": "« ce qui fait tomber la condition ne vaut que si le dossier en montre les faits » ; « une cause d'échec ne vaut rien si le dossier n'en montre pas les faits »",
      "propose": "ajouter : « le moyen que le défendeur articule dans le dossier est un de ces faits, même résumé sans ses pièces »",
      "motif": "Dans 9 des 14 sessions où l'agent manque un refus contradictoire, il écarte la défense faute de pièce (citations au § 4)."
    }
  ],
  "acheminement": {
    "constat": "v56 : contrat PROV remis à la lecture du dossier dans 7 dossiers sur 40 ; contrat d'un autre exercice dans 10 (plein_contentieux_indemnitaire 7, refere_civil_835_trouble, assignation_fond, mise_en_demeure_emise), qui bloque ensuite le contrat PROV au Stop ; contrat PROV après la première réponse seulement dans 23. Sur 80 sessions, la réponse finale reprend la première 78 fois.",
    "proposition": "ajouter aux marqueurs_texte de la fiche : \"^(?![\\\\s\\\\S]*administratif)[\\\\s\\\\S]*\\\\bla provision (?:demandée|sollicitée|réclamée)\\\\b\" ; à défaut, \"provisionnel(?:le)?s?\\\\b\", \"\\\\bpar provision\\\\b\", \"\\\\bprovision (?:à valoir|de \\\\d)\"",
    "simulation": "premier marqueur : exercice PROV reconnu à la lecture dans 40 dossiers sur 40 et 294 sur 294 ; marqueurs de dossier seuls : 31 sur 40 et 209 sur 294 ; aucun changement sur 290 dossiers tirés des familles ANNT, LIB, URGT, URGD, URG, CASSA et CASSN"
  }
}
```

## 1. Ce qui ressort

Les refus que l'agent manque se partagent en deux groupes qui n'appellent pas la même réponse.

Le premier groupe compte six défendeurs défaillants (12 sessions). Les juges y ont refusé pour des faits qui ne sont que dans les pièces : bail signé par une personne qui n'était pas le gérant (2401076), décomptes contradictoires et frais injustifiés (2401875), contrat de jetons et capture d'écran non datée (2450025), aucune preuve d'exécution des travaux (2551597), reconnaissance de dette sans mention manuscrite (2600588), factures signées du seul entrepreneur (2656279). Rien dans l'exposé ne les sépare des 15 allocations rendues contre un défaillant. Répondre oui y reste le meilleur pari, et aucune règle n'est proposée pour eux (§ 6).

Le second groupe tient à une erreur de lecture visible. Quand le défendeur comparaît et oppose un moyen de fond, les juges refusent 12 fois sur 14 dans l'échantillon. L'agent n'en trouve que 10 sur 24 sessions : il tire un aveu des demandes subsidiaires du défendeur et écarte son moyen principal faute de pièce reproduite. Les deux règles proposées visent ce groupe, avec des sources de la Cour de cassation lues ce jour.

Les règles n'auront presque aucun effet sans une correction d'acheminement. En v56, le contrat PROV n'atteint l'agent avant sa réponse que dans 7 dossiers sur 40, et 10 dossiers reçoivent le contrat d'un autre exercice (§ 7).

## 2. Indices visibles et issues

### 2.1 Les 40 ordonnances, codage à la main

Échantillon équilibré : 20 allocations, 20 refus. La dernière colonne donne les sessions où l'agent répond juste.

| Indice visible dans `dossier_remis.md` | Allocations | Refus | Agent juste |
|---|---|---|---|
| Défendeur défaillant, aucune défense exposée | 15 | 8 | allocations 30/30, refus 4/16 |
| Défendeur comparant | 5 | 12 | allocations 8/10, refus 10/24 |
| … qui ne discute pas la dette au fond (accord, offre faite au juge, nullité de l'assignation et délais) | 3 | 0 | 6/6 |
| … qui oppose un moyen de fond articulé | 2 | 12 | allocations 2/4, refus 10/24 |
| … et forme des demandes subsidiaires (réduction, délais, déduction, plafond) | 0 | 5 | refus 1/10 |
| Provision sur la réparation d'un préjudice ou une indemnité d'assurance | 1 | 9 | allocations 2/2, refus 11/18 |
| … contre un défendeur comparant qui la discute | 0 | 7 | refus 7/14 |
| Loyers et indemnités d'occupation | 6 | 4 | |
| Prix de travaux, factures, prestations | 4 | 4 | |
| Prêt, reconnaissance, protocole, transaction, carte, location financière | 7 | 1 | |
| Cause de la dette non dite dans l'exposé | 2 | 1 | |
| Séquestre conventionnel | 0 | 1 | |
| Défaillant et loyers / factures / titre de dette / cause non dite / préjudice | 6 / 3 / 4 / 2 / 0 | 2 / 2 / 1 / 1 / 2 | |
| Demande jointe de constat de clause résolutoire ou d'expulsion | 1 | 1 | |
| Demande jointe de pénalité, majoration ou clause pénale | 2 | 5 | |
| Juge du fond déjà saisi | 0 | 1 | 2/2 |
| Clause compromissoire | 0 | 1 | 2/2 |
| Procédure collective, juge de la mise en état, expertise ordonnée | 0 | 0 | |
| Montant demandé, médiane | 25 000 € | 28 000 € | |

Le montant ne sépare rien. La nature de la créance ne sépare qu'à travers la présence du défendeur : le préjudice discuté par un comparant va 7 fois sur 7 au refus, les titres de dette contre un défaillant 4 fois sur 5 à l'allocation. Les demandes jointes à la provision ne changent pas son issue dans l'échantillon, sauf la clause résolutoire de 2654197, refusée avec la provision parce que le même décompte était en cause.

### 2.2 Les 294 ordonnances du corpus, codage par expressions régulières

157 allocations, 137 refus (47 %). Codage approximatif, utile pour l'ordre de grandeur. Les 26 dispositifs relus hors échantillon confirment l'étiquette dans les 26 cas (2301357 ordonne des travaux et rejette la provision).

| Indice | Allocations | Refus |
|---|---|---|
| Marqueur de défaut, aucune défense écrite | 115 | 76 |
| « contestation sérieuse » dans l'exposé | 9 | 37 |
| Marqueur de PROV2-R1 (rejet principal puis réduction ou délais subsidiaires) | 3 | 14 |
| Marqueur et garde de PROV2-R2 (préjudice discuté) | 3 | 17 |
| PROV2-R1 ou PROV2-R2 | 6 | 27 |
| Exception d'inexécution, désordres ou réserves, défendeur qui conclut au rejet | 2 | 14 |
| Décompte contesté | 0 | 5 |
| Expertise mentionnée | 6 | 16 |
| Clause résolutoire ou expulsion demandée | 40 | 18 |
| Loyers | 71 | 43 |
| Factures ou travaux, défendeur défaillant | 23 | 23 |
| Prêt, reconnaissance ou transaction, défendeur défaillant | 12 | 4 |

L'indice « exception d'inexécution » discrimine fortement au tribunal (2 contre 14), mais il se déclenche aussi sur 4 arrêts d'appel du premier tour qui ont maintenu la provision (2205185, 2301459, 2300124, 2218821). Il n'est donc pas proposé comme règle.

## 3. Ce que les juges ont retenu dans les 20 refus

Légende : C, défendeur comparant ; D, défaillant. « Agent » donne la réponse v55 puis v56.

| Sonde | | Motif du refus, lu dans la décision | Visible | Agent |
|---|---|---|---|---|
| 2304088 | C | ordre de virement à interpréter, faute du notaire discutée | oui | non, non |
| 2355570 | C | préjudice non établi, réparations faites | oui | non, non |
| 2358726 | D | garantie refusée par l'assureur avant l'instance | oui | non, non |
| 2400211 | C | décompte inexploitable, exception d'inexécution étayée (photographies, lettre antérieure au commandement, bailleur taisant), demande non provisionnelle | en partie | oui, oui |
| 2400449 | C | clause compromissoire et manquements | oui | non, non |
| 2400742 | C | causes légitimes de retard discutées ; faute, préjudice et causalité à débattre au fond | oui | oui, non |
| 2400818 | C | même promoteur, mêmes motifs | oui | oui, oui |
| 2400986 | C | convention de séquestre exigeant un exploit non produit | en partie | oui, non |
| 2401076 | D | bail signé par un non-gérant | non | oui, oui |
| 2401660 | C | levée des réserves mise en doute par un courriel du constructeur, exigibilité du solde qui en dépend | moyen oui, pièce non | oui, oui |
| 2401875 | D | décomptes contradictoires, frais injustifiés | non | oui, oui |
| 2402266 | C | impossibilité de relouer et faute du syndicat non établies | oui | oui, oui |
| 2405742 | C | pièces contradictoires sur le relogement, devis validés sans l'expert | en partie | oui, oui |
| 2450025 | D | contrat de jetons, pièces insuffisantes | non | oui, oui |
| 2457733 | C | juge du fond déjà saisi | oui | non, non |
| 2551597 | D | aucune preuve d'exécution des travaux, factures unilatérales | non | oui, oui |
| 2600588 | D | reconnaissance sans mention manuscrite (C. civ., art. 1376) | non | oui, oui |
| 2654197 | C | décompte non justifié (loyer mensuel sans rapport avec le bail) | moyen oui | oui, oui |
| 2656279 | D | factures du seul entrepreneur, ni contrat ni travaux établis | non | oui, oui |
| 2656391 | D | refus de virement de la banque, préjudice moral | oui | non, non |

La seule allocation manquée, 2400890, tient à une lettre où le débiteur reconnaissait devoir 40 000 € ; l'exposé n'en montre que l'ombre, la demande subsidiaire du créancier de ce même montant.

## 4. L'erreur de raisonnement récurrente

Sur les 14 sessions où l'agent manque un refus contradictoire, chacune présente au moins l'une de deux fautes.

Il tire un aveu des demandes subsidiaires ou d'un silence partiel du défendeur (10 sessions). « Ses demandes subsidiaires valent aveu de la dette » (2654197, v56). « Le principe est même concédé. À titre subsidiaire, Prestige Invest 4 demande de « corriger la période » de retard » (2400742, v55). « Leur demande subsidiaire de délais de 24 mois, présentée à l'audience, revient à admettre la dette » (2401660, v56). Dans 2402266 (v55), il écrit lui-même « Un moyen subsidiaire ne vaut pas aveu », puis « Sa demande subsidiaire reste pourtant parlante » et répond oui. Dans 2405742, le mot « solde » et le renvoi au fond limité au préjudice moral lui font conclure que l'assureur « admet que le sinistre est garanti ». De cet aveu supposé, il passe chaque fois à la provision partielle de l'arrêt de 2013.

Il écarte le moyen principal parce que l'exposé n'en reproduit pas les pièces (9 sessions). « Elle conteste ses causes, sans pièce dans le dossier remis » (2400742, v55). « Le dossier ne montre aucune pièce sur ce point, seulement une affirmation générale » (2400818, v56). « Le dossier reproduit ses allégations, pas ces pièces » (2400211, v56). « Un grief aussi vague ne vaut pas contestation sérieuse » (2654197, v56). Le dossier remis ne reproduit les pièces d'aucune partie : ce critère joue toujours contre le défendeur. Les juges, eux, ont statué sur ces pièces et ont retenu la contestation.

Les deux fautes contredisent la Cour de cassation. Une contestation subsidiaire du montant ne vaut pas aveu (Ass. plén., 29 mai 2009) et une demande de délais n'emporte pas reconnaissance (1re civ., 28 mars 1995). Le juge des référés ne peut exiger que le moyen de défense soit établi à l'évidence (2e civ., 4 juin 2015). La provision partielle suppose que le débiteur ne conteste ni le dommage ni le principe (2e civ., 11 juill. 2013).

## 5. Les règles, leur acheminement et leurs décomptes

### 5.1 Simulation du contrat

`contrat_compact` et `_applicable` ont été appelés depuis `hook.py`, fiche actuelle chargée par `exercices.charger_catalogue`, horloge fixée à celle de chaque sonde, avec les deux règles insérées aux rangs 3 et 4. Deux contextes : celui de la lecture (demande et dossier numéroté) et celui du Stop (réponse, demande et dossier).

- Chaque fois que ses marqueurs se déclenchent, la règle figure dans le contrat (63 cas sur 63, échantillon et corpus). Placées en fin de liste, une règle applicable serait coupée par la limite de trois lignes marquées.
- L'insertion évince 18 fois une ligne existante, dont 17 fois la ligne générale « Le débiteur oppose un moyen de fond sérieux ou prouve le paiement », que PROV2-R1 précise, et une fois une ligne marquée.
- Contexte de la lecture, échantillon : PROV2-R1 dans 2400742, 2400818, 2401660, 2402266, 2654197 ; PROV2-R2 dans 2400449, 2400742, 2400818, 2402266, 2405742. Tous des refus, aucune allocation.
- Contexte du Stop : PROV2-R2 s'ajoute dans 2355570 et 2656391 (refus déjà trouvés) et dans les allocations 2354373 (deux sessions) et 2301178 (v56), parce que la réponse de l'agent porte les mots de la garde.

### 5.2 Ce que les règles corrigent

Sessions aujourd'hui fausses que les règles visent : 2400742 (v55), 2400818, 2401660, 2402266, 2654197 et 2405742, soit 11 sessions sur 80. Si l'agent suit les lignes, les refus reconnus passent au plus de 14 à 25 sur 40 ; les allocations restent à 38 sur 40 au contexte de la lecture, aucune allocation de l'échantillon n'y déclenchant de règle.

Restent hors d'atteinte : 2400211 et 2400986 (3 sessions), dont le seul indice sûr est l'exception d'inexécution, écartée pour les arrêts d'appel ; les 12 sessions de défaut du § 6 ; l'allocation 2400890.

### 5.3 Risques

- Au Stop, 3 sessions d'allocation reçoivent PROV2-R2 : 2354373 (dommages-intérêts fixés par un protocole transactionnel, que le texte excepte) et 2301178 (loyers ; le texte dit que les autres chefs se jugent à part).
- Dans le corpus, 6 allocations déclenchent une règle ; chacune répond à une exception écrite dans le texte (rejet sans moyen suivi de délais, paiement allégué sans preuve, montant que l'assureur propose lui-même, facture non discutée).
- Sur les 40 dossiers du premier tour (avec appels), PROV2-R1 se déclenche sur la seule sonde 2202637, déjà déclarée ambiguë ; PROV2-R2 sur 3 allocations d'appel, dont 2211337, où le droit à indemnisation n'était pas discuté, et 2205185, où la provision portait sur des loyers.

Ces chiffres viennent de la simulation et de la lecture des réponses. La conduite de l'agent face aux textes reste à mesurer par un rejeu.

### 5.4 Acheminement, condition préalable

En v56, `contrat_a_la_lecture` ne reconnaît le référé-provision que si le dossier porte « à titre de provision », « 835, alinéa 2 » ou « obligation non sérieusement contestable ». La consigne (« la provision demandée ») n'en porte aucun. Résultat sur les 40 dossiers : 7 reçoivent le contrat PROV avant la réponse, 23 seulement au Stop, et 10 reçoivent le contrat d'un autre exercice, ce qui bloque ensuite le contrat PROV (`contrat_deja_donne`). Sur les 294 dossiers, 48 reconnus, 74 envoyés vers un autre exercice ; le marqueur `condamner\s+.{0,80}\s+[àa]\s+(lui\s+)?verser` de `plein_contentieux_indemnitaire` en capte 37 à lui seul.

Pour les cibles des règles, en v56 : 2405742 reçoit le contrat avant de répondre ; 2400742, 2400818, 2402266 ne le reçoivent qu'au Stop ; 2401660 et 2654197 ne le reçoivent jamais en v56. Au Stop, l'agent a changé de réponse 2 fois sur 63. Sans correction d'acheminement, l'effet attendu des règles se limite donc à 2405742.

Le marqueur de consigne proposé dans le bloc JSON fait reconnaître l'exercice dans 40 dossiers sur 40 et 294 sur 294, sans rien changer sur 290 dossiers des autres familles ; une consigne qui nomme le tribunal administratif n'est pas captée. Les marqueurs de dossier seuls donnent 31 sur 40 et 209 sur 294, mais pourraient rivaliser hors banc avec d'autres référés civils qui citent une somme provisionnelle.

## 6. Les refus qui tiennent à des faits absents du dossier

Six des huit refus contre un défaillant (12 sessions) reposent sur une pièce que seul le juge a vue (§ 1). Leur profil apparent est celui des allocations : contre un défaillant, l'échantillon compte 6 allocations pour 2 refus sur les loyers, 3 pour 2 sur les factures, 4 pour 1 sur les titres de dette, 2 pour 1 quand la cause n'est pas dite ; le corpus, 115 allocations pour 76 refus. Pousser vers non sur ces profils ferait perdre plus d'allocations que de refus gagnés. La ligne du premier tour sur le défendeur défaillant a d'ailleurs atteint 38 sessions sans déplacer une réponse sur ces six sondes. Aucune règle n'est proposée pour elles, et le motif de 2600588 (mention manuscrite manquante) ne se devine pas sans l'acte.

## 7. Lignes existantes qui poussent à tort vers « oui »

1. Première condition, `ce_qui_la_remplit[1]` (preneur qui poursuit son activité). Elle tire d'un arrêt rendu au fond (Cass. 3e civ., 6 juill. 2023, n° 22-15.923, qui casse faute d'avoir recherché si les locaux étaient impropres) une règle de référé. L'agent l'a citée pour répondre oui dans 2400211, refusé. Reformulation dans le bloc JSON.
2. Seconde condition, `ce_qui_la_remplit[0]` (délais de la loi de 1989). Gardée par « loyer », elle s'applique au bail commercial 2654197 et y annonce une provision sur le décompte « non contesté ». Garde proposée dans le bloc JSON.
3. Phrase finale du contrat dans `hook.py` (« une cause d'échec ne vaut rien si le dossier n'en montre pas les faits »). L'agent la lit comme une exigence de pièces ; ajout proposé.
4. Ligne « expertise » du premier tour, dernière phrase (« une allégation sans pièce […] laissent la provision »). Elle n'a atteint aucune session de cet échantillon, sa garde exigeant une expertise ordonnée ; lue sans cette garde, elle contredirait l'arrêt du 4 juin 2015.
5. Gardes JSON écrites `\bbail\b` : décodées en retours arrière, leur alternative « bail » ne joue jamais. Défaut technique sans effet mesuré ici.

À noter, sans effet sur l'issue : la ligne sur la fausse déclaration à l'assureur s'affiche pour 2400211 parce que « réticence abusive » et « assurer une jouissance paisible » remplissent ses marqueurs.

## 8. Sources lues

Textes, version en vigueur le 23 novembre 2026, lus sur LibreJustice : [CPC, art. 835](https://librejustice.fr/norm/fr/code-de-procedure-civile/835) ; [C. civ., art. 1353](https://librejustice.fr/norm/fr/code-civil/1353).

Décisions de la Cour de cassation, texte intégral lu ce jour :
- [Cass. ass. plén., 29 mai 2009, n° 07-20.913](https://librejustice.fr/decision/5G_Q96prD66T), Bulletin : la contestation subsidiaire de l'existence ou du montant d'une créance ne vaut pas aveu.
- [Cass. 1re civ., 28 mars 1995, n° 92-21.016](https://librejustice.fr/decision/hLB3dMeVY2OL), Bulletin : la demande de délais n'emporte pas à elle seule reconnaissance ni acquiescement.
- [Cass. 2e civ., 11 juill. 2013, n° 12-24.722](https://librejustice.fr/decision/I8r47MFf3man), Bulletin : provision partielle quand l'assureur ne conteste ni les dommages ni le principe.
- [Cass. 2e civ., 4 juin 2015, n° 14-13.405](https://librejustice.fr/decision/9lieNA8qmd3h), Bulletin : le sérieux de la cause d'exonération s'examine sans exiger l'évidence de ses conditions.
- [Cass. 3e civ., 18 mai 2017, n° 16-16.808](https://librejustice.fr/decision/ep-d0EDoIxv1), inédit : responsabilité supposant la recherche d'une faute et d'un lien de causalité, contestation sérieuse.
- [Cass. ass. plén., 16 nov. 2001, n° 99-20.114](https://librejustice.fr/decision/ofD32CLzr7se), Bulletin : provision accordée « quel que soit » le fondement, cassation.
- [Cass. 3e civ., 6 juill. 2023, n° 22-15.923](https://librejustice.fr/decision/U1GCx5P9b0uh), Bulletin : arrêt rendu au fond sur l'exception d'inexécution du preneur.

Vu par son seul sommaire, non cité à l'appui d'une règle : Cass. 3e civ., 18 sept. 2025, n° 23-24.005.

Échantillon : 40 dossiers remis, 80 réponses finales et premières réponses, contrats remis relevés dans les journaux bruts, drapeaux `etat/.contrat_donne`, motifs et dispositifs des 40 décisions par `decision.py`. Corpus : 294 dossiers codés par expressions régulières, 26 dispositifs relus. Rapport du premier tour (`PROV.md`) lu. Fichiers de travail dans le dossier temporaire de la session, hors dépôt.
