```json
{
  "famille": "ANNT",
  "version_analysee": "v54 (80 sondes, index_v54.json) et v50 (40 sondes, index_v50.json)",
  "corpus_controle": "300 sondes ANNT du banc (150 annulations, 150 rejets), qui contiennent les 120",
  "fiche": "plugins/contentieux/skills/mecanique-des-exercices/references/requete-annulation.md",
  "regles": [
    {
      "id": "ANNT2-R1-auteur-sans-defense",
      "condition": "bien_fonde",
      "tableau": "ce_qui_la_remplit",
      "position": "premier élément du tableau, à la place de la ligne « Auteur de la décision sans défense » (ANNT-R1), qu'elle remplace",
      "texte": "Auteur de la décision sans défense : quand l'autorité qui a pris la décision n'a produit aucun mémoire avant la clôture (requête communiquée restée sans réponse, mise en demeure sans effet, simples pièces sans mémoire, aucune défense visée), l'annulation est probable, sauf obstacle que le dossier montre lui-même. Faute de mise en demeure, l'autorité n'est pas réputée acquiescer aux faits (CJA, art. R. 612-6 ; CE, 26 juin 2023, n° 467714) ; après une mise en demeure restée sans effet, ils sont admis sauf pièce contraire (CE, 30 décembre 2009, n° 314972). Le juge de l'excès de pouvoir ne peut exiger du requérant la preuve des faits qu'il avance et, devant des allégations sérieuses que l'administration ne dément pas, il use de ses pouvoirs d'instruction (CE, 26 novembre 2012, Cordière, n° 354108) ; l'administration qui ne lui donne pas alors les motifs de sa décision laisse regarder comme établies les allégations du requérant (CE, 12 février 2003, n° 218983). Le dossier remis ne reproduit pas la décision : ne pas supposer qu'elle est motivée ou qu'elle répond aux moyens, ni prêter à l'auteur une délégation, un avis ou une pièce qu'il n'a pas produits ; la défense d'un tiers bénéficiaire (employeur ou liquidateur, pétitionnaire) ne supplée pas l'auteur sur la motivation, l'examen de la situation et la procédure suivie. Le rejet ne reste probable que devant un obstacle visible au dossier : moyen relevé d'office annoncé aux parties (CJA, art. R. 611-7) et tiré d'une irrecevabilité, de l'inopérance, de la compétence liée (CE, Sect., 3 février 1999, Montaignac, n° 149722) ou d'une substitution de base légale (CE, Sect., 3 décembre 2003, El Bahi, n° 240267) ; refus d'abroger un acte non réglementaire sans changement de circonstances (CRPA, art. L. 243-2) ; cause juridique nouvelle invoquée après le délai de recours (CE, 31 mars 2017, n° 399123). Une règle de fond qui écarte un moyen n'écarte que celui-là : un seul moyen fondé suffit à annuler.",
      "marqueurs": [
        "(?:communiqu|transmis)[ée]e?s? (?:au|à la|à l['’]|aux) ?(?:préfet|préfète|ministre|maire|directeur|directrice|président|présidente|recteur|rectrice|commune|département|région|agence|caisse|centre hospitalier|ehpad|office|ofii|inspect\\w*|garde des sceaux|administration|établissement|université|conseil|chambre|ville|communauté|métropole|[ée]tat|institut|autorité)[^.]{0,220}?n['’](?:a|ont) (?:pas produit|produit aucun|présenté aucun)",
        "réputée? avoir acquiescé",
        "\\b(?:préfet|préfète|ministre|maire|directeur|directrice|président|présidente|recteur|rectrice|commune|département|région|agence|caisse|centre hospitalier|ehpad|office|ofii|inspect\\w*|garde des sceaux|administration|établissement|université|conseil|chambre|ville|communauté|métropole|[ée]tat|institut|autorité)[^.]{0,120}?(?:a|ont) été mise?s? en demeure|mise en demeure (?:a été )?adressée (?:au|à la|à l['’]|aux) ?(?:préfet|préfète|ministre|maire|directeur|directrice|président|présidente|recteur|rectrice|commune|département|région|agence|caisse|centre hospitalier|ehpad|office|ofii|inspect\\w*|garde des sceaux|administration|établissement|université|conseil|chambre|ville|communauté|métropole|[ée]tat|institut|autorité)|(?:préfet|préfète|ministre|maire|directeur|directrice|président|présidente|recteur|rectrice|commune|département|région|agence|caisse|centre hospitalier|ehpad|office|ofii|inspect\\w*|garde des sceaux|administration|établissement|université|conseil|chambre|ville|communauté|métropole|[ée]tat|institut|autorité)[^.]{0,60}mise? en demeure de (?:produire|conclure)",
        "a produit (?:des|une) pièces? sans (?:présenter|produire) de (?:mémoire|défense|observations)|(?:préfet|préfète|ministre|maire|directeur|directrice|président|présidente|recteur|rectrice|commune|département|région|agence|caisse|centre hospitalier|ehpad|office|ofii|inspect\\w*|garde des sceaux|administration|établissement|université|conseil|chambre|ville|communauté|métropole|[ée]tat|institut|autorité)[^.]{0,60}? a produit une pièce, enregistrée",
        "demand\\w* au tribunal(?: administratif)?(?:, dans le dernier état de ses écritures,)?\\s*(?::|d['’]annuler)(?:(?!conclu|en défense|font valoir|fait valoir|observations|rejet|mémoire|produit|mise? en demeure|communiqué)[\\s\\S]){0,6000}?Vu les autres pièces du dossier"
      ],
      "exige": null,
      "origine": "second tour d'analyse ANNT du 23 novembre 2026 (validation/corpus_motifs/biais/ANNT2.md)",
      "simulation": {
        "methode": "hook.contrat_compact sur la fiche actuelle, horloge fixée à celle de chaque sonde (CONTENTIEUX_MAINTENANT). Sessions : contexte du blocage de fin de tour reconstitué depuis _brut.jsonl (première réponse, demande, lectures du dossier). Corpus : consigne et dossier numéroté comme le rend l'outil Read. Contrôle : les 80 contrats remis dans v54 sont reproduits à l'identique.",
        "sessions_120": "ligne remise dans les 16 sessions qui reçoivent aujourd'hui ANNT-R1, en tête de « Ce qui remplit « bien_fonde » », sans déplacer d'autre ligne",
        "corpus_300": "ligne remise dans 62 dossiers : 59 annulations, 3 rejets (ANNT-R1 actuelle : 46 et 2)"
      },
      "decompte": {
        "annulations_manquees_corrigibles_120": [
          "GENP-ANNT-2000743",
          "GENP-ANNT-2000745",
          "GENP-ANNT-2000746",
          "GENP-ANNT-2000747",
          "GENP-ANNT-2000750",
          "GENP-ANNT-2000732",
          "GENP-ANNT-2000736",
          "GENP-ANNT-2000740"
        ],
        "remarque": "une seule série de jugements jumeaux (autorisations de licencier, auteur muet, liquidateurs en défense) ; ANNT-R1 était remise dans les 5 sessions v54 sans changer la réponse ; la nouvelle rédaction répond aux objections que l'agent y a opposées ; effet non mesuré",
        "rejet_manque_vise": {
          "GENP-ANNT-2200135": "passé de non à oui sous ANNT-R1 alors que le juge avait annoncé (R. 611-7) l'irrecevabilité du moyen de motivation ; l'exception est désormais écrite"
        },
        "rejets_bien_predits_a_risque_120": [],
        "annulations_reussies_qui_recoivent_la_ligne_120": [
          "GENP-ANNT-2211202",
          "GENP-ANNT-2105986",
          "GENP-ANNT-2311944",
          "GENP-ANNT-2101375",
          "GENP-ANNT-2200711",
          "GENP-ANNT-2400247",
          "GENP-ANNT-2401011"
        ],
        "corpus_300": {
          "declenchee": 62,
          "annulations": 59,
          "rejets": 3,
          "hors_series_jumelles": "24 annulations, 3 rejets",
          "nouveaux_declenchements": {
            "annulations": [
              "2101375",
              "2106179",
              "2203882",
              "2204709",
              "2206785",
              "2207365",
              "2207369",
              "2304208",
              "2403312",
              "2404827",
              "2411462",
              "2422039",
              "2504990"
            ],
            "rejets": [
              "2300087"
            ]
          },
          "rejets_expliques": {
            "GENP-ANNT-2200135": "R. 611-7 : irrecevabilité du moyen de motivation soulevé après le délai ; autres moyens écartés",
            "GENP-ANNT-2202586": "refus d'abroger sans circonstance nouvelle, moyens inopérants (CRPA, art. L. 243-2) ; R. 611-7 annoncé",
            "GENP-ANNT-2300087": "R. 611-7 : substitution de base légale relevée d'office ; refus de titre étudiant confirmé au fond"
          }
        }
      },
      "sources_lues": [
        "CJA, art. R. 611-7, version en vigueur depuis le 10 février 2019, texte lu (LibreJustice)",
        "CE, Sect., 3 décembre 2003, El Bahi, n° 240267, Recueil, analyse lue",
        "CE, 12 février 2003, n° 218983, tables, analyse lue",
        "CE, 26 novembre 2012, Cordière, n° 354108, Recueil, analyse lue",
        "CE, Sect., 3 février 1999, Montaignac, n° 149722, Recueil, analyse lue",
        "repris d'ANNT.md sans relecture : CJA, art. R. 612-3 et R. 612-6 ; CRPA, art. L. 243-2 ; CE, 26 juin 2023, n° 467714 ; CE, 30 décembre 2009, n° 314972 ; CE, 31 mars 2017, n° 399123 (analyse seule)"
      ]
    }
  ],
  "corrections_existantes": [
    {
      "element": "ligne « Décision implicite : le défaut de motivation... » de bien_fonde.ce_qui_la_remplit",
      "action": "retirer « la requête qui soulève ce moyen s'appuie d'ordinaire sur cette demande, et quand la défense ne conteste ni la demande ni le silence gardé, le moyen est fondé et suffit à l'annulation » ; écrire à la place « Le moyen n'aboutit que si la demande de motifs ressort du dossier : quand l'auteur défend, elle ne se présume pas ; quand il se tait, voir la ligne de l'auteur sans défense. »",
      "motif": "La présomption n'est juste que lorsque l'auteur se tait (décision implicite et moyen de motivation : 23 annulations, 1 rejet), cas que couvre ANNT2-R1. Quand l'auteur défend : 17 annulations, 31 rejets. Dans v54, deux rejets sont passés de non à oui en reprenant la formule (2104190 « ce qui suppose d'ordinaire une telle demande », 2205147 « repose d'ordinaire sur une telle demande »).",
      "decompte_120": "2 rejets corrigibles (2104190, 2205147) ; 1 annulation à risque (2300296, dont le mémoire du ministre, arrivé après la clôture, n'a pas été communiqué) ; 2312723 et 2311831 ne s'appuyaient pas sur la formule"
    },
    {
      "element": "ligne « L'arrêté de dessaisissement, mesure de police... » de bien_fonde.ce_qui_la_remplit",
      "action": "remplacer sa garde exige par [\"\\\\barmes?\\\\b|dessaisissement|munitions\"]",
      "motif": "La garde actuelle (« préfet », « police »...) et le marqueur « insuffisamment motiv » la font remettre dans 49 des 300 dossiers, dont un seul concerne des armes, et dans 15 des 80 sessions v54. Elle occupe l'une des quatre places « ce qui la remplit ». Effet sur l'issue non mesuré."
    }
  ]
}
```

# Second tour ANNT : les annulations que l'agent ne prédit pas

Analyse du 23 novembre 2026. Échantillons jugés : 80 sondes ANNT de v54 (40 annulations, 40 rejets) et les 40 sondes de v50 déjà vues au premier tour, soit 120 sessions dont la première réponse, le contrat remis et la réponse finale ont été relus dans les `_brut.jsonl`. Contrôle élargi : les 300 sondes ANNT du banc (150 annulations, 150 rejets), qui contiennent les 120 ; aucune autre sonde ANNT n'existe au banc. Une vérification sur un corpus LibreJustice plus large n'a pas pu se faire : le serveur a répondu « rate_limited » et 429 pendant la séance. Jugements relus dans leurs motifs décisifs : les 18 annulations manquées et les 5 rejets manqués de v54, et 11 jugements du corpus qui éprouvent les marqueurs. Aucune session de l'agent n'a été lancée : l'effet des propositions sur ses réponses n'est pas mesuré.

## 1. Résultat

Un seul indice visible sépare nettement les annulations des rejets : l'autorité qui a pris la décision ne produit aucun mémoire avant la clôture. Sous toutes ses formes, il accompagne 59 annulations et 3 rejets sur 300 ; hors des deux séries de jugements jumeaux, 24 annulations et 3 rejets, et les 3 rejets portent tous une information R. 611-7 sur un obstacle relevé d'office. La ligne actuelle (ANNT-R1) ne le saisit que dans 46 annulations et 2 rejets : son marqueur ne reconnaît pas « à l'Office », « à l'EHPAD », ni la mise en demeure, les simples pièces ou l'absence de toute défense dans les visas.

Ce signal ne manquait pourtant pas à l'agent dans l'échantillon. ANNT-R1 a été remise dans les 5 sessions v54 de la série des autorisations de licencier, et l'agent a maintenu le rejet cinq fois. Il a écarté la règle avec des arguments que le dossier ne porte pas, décrits en section 3. La règle ANNT2-R1 remplace ANNT-R1 : elle élargit la détection, répond à ces arguments et écrit l'exception que l'agent a manquée sur le seul rejet où la règle l'a fait basculer à tort.

Les 22 autres annulations manquées (13 en v54, 9 en v50) n'ont aucun indice visible commun. Le juge a annulé sur le texte de la décision ou sur des pièces que le dossier remis ne reproduit pas : motivation en fait ou en droit, relevés de notes, jugement du tribunal paritaire, chèques non signés, attestations. Le premier tour l'avait conclu sur 12 échecs ; l'échantillon plus grand le confirme. Aucun autre signe de procédure ne dépasse 66 % d'annulations sur un effectif utile, et ceux qui sont nets désignent le rejet, que l'agent lit déjà bien.

## 2. Indices visibles

Comptes sur les 300 dossiers remis (annulations / rejets), puis sur les 120 sessions, avec entre parenthèses les annulations manquées. Relevés par expressions régulières, relus à la main pour les lignes de l'auteur sans défense, de R. 611-7, du mémoire tardif, de la note en délibéré, du référé et des mesures d'instruction.

| Indice visible | 300 | 120 (manquées) | Lecture |
| --- | --- | --- | --- |
| Auteur sans mémoire avant la clôture, toutes formes (marqueurs d'ANNT2-R1) | 59 / 3 | 15 / 1 (8) | Discriminant. Règle ANNT2-R1 |
| dont requête communiquée restée sans production (marqueur actuel, apostrophe corrigée) | 48 / 2 | 14 / 1 | Le marqueur actuel en manque 2 (« à l'Office », « à l'EHPAD ») |
| dont mise en demeure de l'auteur restée sans effet (R. 612-3) | 3 / 0 | 1 / 0 | |
| dont pièces produites sans mémoire | 3 / 0 | 0 | |
| dont aucune défense visée dans la procédure | 5 / 1 | 0 | Le rejet porte une information R. 611-7 |
| même indice hors des deux séries jumelles | 24 / 3 | 6 / 1 (0) | Les 3 rejets : obstacle annoncé par R. 611-7 |
| Seul mémoire de l'auteur arrivé après la clôture, non communiqué | 5 / 2 | 3 / 1 (0) | Trop mince ; l'agent juste 3 fois sur 4 ; écarté des marqueurs |
| R. 611-7 : moyen d'annulation relevé d'office (incompétence, champ d'application de la loi, voie de conséquence) ou injonction d'office (R. 611-7-3) | 6 / 1 | 4 / 1 (0) | Net, déjà bien lu (4 sur 5) |
| R. 611-7 : irrecevabilité, défaut d'intérêt, tardiveté, inopérance, compétence liée, substitution de base légale | 2 / 16 | 2 / 6 (1) | Net vers le rejet, déjà bien lu ; repris en exception d'ANNT2-R1 |
| R. 611-7 sans objet précisé | 0 / 1 | 0 | |
| Ordonnance du juge des référés visée | 1 / 0 | 1 / 0 | Aucune donnée |
| Jugement avant dire droit (sursis de l'article L. 600-5-1) | 1 / 0 | 0 | Aucune donnée |
| Mesure ou supplément d'instruction, réouverture | 0 / 0 | 0 | Absents du corpus |
| Invitation à confirmer le maintien des conclusions | 0 / 1 | 0 | |
| Clôture fixée par ordonnance | 37 / 36 | 18 / 14 (7) | Neutre |
| Information R. 611-11-1 (date d'audience, clôture) | 2 / 3 | 2 / 1 | Neutre |
| Mémoire non communiqué, toute partie | 6 / 13 | 4 / 5 (1) | Penche vers le rejet quand il vient du requérant ; mince |
| Note en délibéré | 4 / 4 | 1 / 2 (1) | Neutre ; lue à tort comme l'annonce d'un rejet (2100533) |
| Rapporteur public dispensé (R. 732-1-1) | 64 / 54 | 18 / 22 (6) | Neutre ; la ligne « indices sans valeur pronostique » est juste |
| Décision implicite attaquée | 48 / 53 | 18 / 17 (4) | Neutre |
| implicite et moyen de motivation, auteur muet | 23 / 1 | 2 / 1 | Couvert par ANNT2-R1 |
| implicite et moyen de motivation, auteur en défense | 17 / 31 | 14 / 11 (4) | Penche vers le rejet ; voir la correction de la ligne « Décision implicite » |
| Demande de communication des motifs visible au dossier | 5 / 4 | 4 / 1 (1) | Neutre |
| Substitution de motifs ou de base légale demandée en défense | 12 / 20 | 6 / 8 (4) | Penche faiblement vers le rejet |
| Fin de non-recevoir opposée en défense | 18 / 58 | 12 / 22 (7) | Vers le rejet, déjà lu |
| Défense d'une phrase (« les moyens ne sont pas fondés ») | 77 / 52 | 27 / 24 (12) | Hors auteur muet 50 / 51 : neutre |
| Non-lieu demandé en défense (abrogation) | 1 / 0 | 1 / 0 (1) | Aucune donnée |
| Conclusions d'injonction | 82 / 74 | 26 / 31 (10) | Neutre |
| Astreinte demandée | 53 / 38 | 20 / 15 (10) | Faible, porté par le séjour |
| Frais de l'article L. 761-1 demandés | 127 / 117 | 49 / 48 (24) | Neutre |
| Jonction, requêtes jointes | 5 / 8 | 3 / 4 (1) | Mince |
| Requérant représenté par un avocat | 126 / 120 | 47 / 49 (22) | Neutre |
| Aide juridictionnelle | 19 / 26 | 7 / 14 (1) | Faible vers le rejet |
| Moyen de motivation soulevé | 99 / 65 | 39 / 29 (20) | Faible |
| Moyen d'incompétence soulevé | 39 / 37 | 16 / 14 (6) | Neutre |
| Titre de séjour, OQTF | 41 / 8 | 7 / 3 (4) | 29 / 2 quand l'auteur se tait ; 12 / 6 sinon. Fréquence de matière, sans règle de droit |
| Visa | 18 / 22 | 12 / 11 (4) | Neutre |
| Naturalisation | 1 / 25 | 0 / 11 (0) | Vers le rejet, déjà lu |
| Urbanisme | 10 / 25 | 7 / 7 (3) | Vers le rejet, déjà lu |
| Autorisation de licencier un salarié protégé | 16 / 3 | 8 / 1 (8) | Les 16 annulations forment la série où l'auteur se tait ; hors série 0 / 3 |
| Sanction disciplinaire | 11 / 11 | 4 / 5 (2) | Neutre |
| Admission ou inscription dans l'enseignement | 13 / 7 | 6 / 3 (3) | Mince |
| Autorisation attaquée par un tiers | 21 / 20 | 12 / 6 (11) | Hors auteur muet 5 / 20, vers le rejet |

Aucune combinaison de deux indices hors de l'auteur muet n'atteint 78 % d'annulations sur 15 dossiers ou plus, sauf les matières du séjour (14 / 3 avec astreinte), qui sont des fréquences de contentieux et non des règles. Une analyse par n-grammes des dossiers sans auteur muet ne fait ressortir que des matières (naturalisation, séjour) et des formules d'injonction.

## 3. L'erreur de raisonnement récurrente

**L'agent complète le dossier au profit de l'administration.** Le dossier remis dit lui-même qu'il ne reproduit que la procédure et les prétentions. L'agent prête pourtant un contenu à la décision qu'il n'a pas lue, et à la défense des pièces qu'elle n'a pas produites. Sur les 30 annulations manquées, 11 tiennent à un défaut de motivation ou de communication des motifs, et c'est précisément le moyen que l'agent déclare voué à l'échec sur la foi d'un texte qu'il ne voit pas.

- Contenu prêté à la décision : « la décision attaquée expose elle-même ses motifs » (2000745) ; « Le juge statuera pourtant sur la décision elle-même, versée au dossier » (2000747) ; « Une décision qui vise la liquidation, la cessation d'activité, le reclassement et l'absence de lien avec le mandat est suffisamment motivée » (2000746) ; « Un blâme qui énonce les faits reprochés et leur qualification est d'ordinaire suffisamment motivé » (2201698, annulé pour motivation insuffisante en fait). Formules de ce type : 6 annulations manquées, 2 rejets bien prédits.
- Défense prêtée à l'auteur : « les liquidateurs y répondent pièces en main » (2000746) ; « La meilleure réponse du CSHLD est simple : produire l'acte de nomination » (2201698) ; « Le préfet n'aura qu'à la produire, et ce moyen échouera » (2101739) ; « La défense produira l'avis du conseil et le procès-verbal de la séance » (2308621) ; « Le centre hospitalier n'aura qu'à l'opposer » (2201767). Formules de ce type : 7 annulations manquées, 5 rejets bien prédits, 1 annulation réussie.

Cette manière de conclure se retrouve aussi dans les rejets justes : hors de l'auteur muet, la corriger seule déplacerait des rejets autant que des annulations. Elle devient décisive là où l'auteur ne défend pas, car l'agent y fabrique la défense absente.

**L'exception retournée contre la règle.** ANNT-R1 réserve le rejet à « un obstacle que le juge relève lui-même ». L'agent y a rangé un argument de fond sur un seul moyen : « Le moyen principal [...] se heurte à un obstacle de droit que le juge relève lui-même » (2000743), « Le juge relèvera cette règle de lui-même » (2000750), au sujet du périmètre de reclassement fixé par le plan de sauvegarde. Le tribunal a annulé sur la motivation, autre moyen, sans examiner celui-là (jugement 2000746 lu). L'agent a aussi lu le silence de l'auteur comme sans portée : « rien dans ce dossier ne fait de ce silence le motif qui décide » (2000746), « Le silence de l'administration ne fait pas gagner M. B » (2000745).

**Le sens inverse, une fois.** Dans 2200135, la règle a fait passer une bonne réponse (« Non, 75 % ») à « Oui, 60 % ». Le juge avait annoncé, au titre de l'article R. 611-7, l'irrecevabilité du moyen de motivation soulevé après le délai ; l'exception de la « cause juridique nouvelle » figurait dans ANNT-R1, l'agent ne l'a pas rapprochée de l'information donnée aux parties.

**Les indices de procédure mal lus.** La note en délibéré tenue pour le signe de conclusions défavorables (2100533, « Ce qui le fait perdre » ; 4 / 4 au corpus) ; l'instruction rouverte lue comme un doute du tribunal (2000746) ; l'information R. 611-7 sur la tardiveté tenue pour acquise (2206091, que le tribunal a annulé sans retenir la tardiveté ; 2 annulations sur 18 dossiers où un tel obstacle est annoncé). Ces lectures sont isolées et, pour R. 611-7, juste en moyenne.

**La ligne « Décision implicite » reprise mot pour mot.** Deux rejets sont passés de non à oui après le contrat en recopiant sa présomption : « ce qui suppose d'ordinaire une telle demande » (2104190), « repose d'ordinaire sur une telle demande » (2205147). Le contrat a changé six issues dans v54, trois dans le bon sens et trois dans le mauvais ; deux des trois mauvaises viennent de cette phrase, la troisième d'ANNT-R1.

## 4. Les annulations manquées par v54

| Sonde | v54 | Motif décisif du jugement | Élément visible |
| --- | --- | --- | --- |
| 2000743, 2000745, 2000746, 2000747, 2000750 | non 75, 70, 60, 65, 80 | Autorisation de licencier insuffisamment motivée sur le reclassement (C. trav., art. R. 2421-12), lu dans 2000746 ; même série que 2000732, 2000736, 2000740 de v50 | Auteur muet, liquidateurs en défense. ANNT-R1 remise, écartée |
| 2201698 | non 60 | Blâme insuffisamment motivé en fait | Défense d'une phrase |
| 2201767 | non 75 | Motifs demandés après le refus d'inscription en IFSI et non communiqués | Conclusions tendant à la communication des motifs ; défense d'une phrase |
| 2010061 | non 60 | Permis d'aménager incompatible avec l'OAP (densité) | Aucun |
| 2206091 | non 85 | Refus d'enregistrer une demande de titre : caractère dilatoire non établi | R. 611-7 sur la tardiveté, non retenue : contraire |
| 2208539 | non 55 | Visa de retour : erreur d'appréciation sur des faits « non contestés » | Défense : tardiveté et substitution ; aucun |
| 2402133 | non 88 | Refus d'admission en licence : notes de mathématiques produites | Aucun (pièces) |
| 2002686 | non 75 | Refus d'aide insuffisamment motivé en droit | Défense d'une phrase |
| 2008294 | non 85 | Remise gracieuse partielle : erreur d'appréciation au vu des chèques | Aucun (pièces) |
| 2006773 | non 70 | Allègement de service : aucun motif légal, substitution refusée | Fins de non-recevoir écartées ; aucun |
| 2100533 | non 60 | Menace à l'ordre public non caractérisée | Note en délibéré, lue à contresens |
| 2101739 | non 55 | Autorisation d'exploiter : parcelles libres, jugement du tribunal paritaire | Aucun (pièces) |
| 2300284 | non 85 | Non-lieu écarté (abrogation non définitive, exécution commencée), puis annulation | Non-lieu demandé en défense, seul cas du corpus |
| 2308621 | non 60 | Exclusion de 30 jours : faits rapportés par un seul agent | Aucun ; ligne « sanction » remise sans effet |

Les 9 annulations manquées de v50 hors de la série sont décrites dans ANNT.md (section 2) ; aucune n'a d'élément visible commun avec celles-ci. Les 5 rejets manqués de v54 : 2200135 (ANNT-R1, section 3), 2104190 et 2205147 (ligne « Décision implicite »), 2107936 (requête irrecevable faute de produire la décision attaquée, R. 412-1, malgré une demande du tribunal), 2006427 (moyen relevé d'office sur le champ d'application de la loi, finalement non retenu).

## 5. La règle ANNT2-R1

**Texte, condition, tableau, marqueurs** : bloc JSON en tête. Condition `bien_fonde`, tableau `ce_qui_la_remplit`, en première place, à la place d'ANNT-R1. Pas de garde `exige` : les marqueurs exigent déjà une autorité publique (le GAEC mis en demeure de 2101064 et le GAEC muet de 2208475 ne déclenchent pas).

**Ce qui change par rapport à ANNT-R1.**
- Détection. Le premier marqueur accepte « à l'Office », « à l'EHPAD » (l'espace après l'apostrophe était exigé) et « n'ont pas produit ». Trois marqueurs nouveaux : mise en demeure adressée à l'autorité ; pièces produites sans mémoire ; aucune défense visée entre « demande au tribunal » et « Vu les autres pièces du dossier ». Le mémoire de l'auteur arrivé après la clôture n'est pas retenu (5 / 2).
- Les objections de l'agent. Le texte dit que le dossier ne reproduit pas la décision, interdit de la supposer motivée ou de prêter à l'auteur une pièce qu'il n'a pas produite, et précise qu'une règle de fond qui écarte un moyen laisse les autres.
- L'exception. Elle devient « un obstacle visible au dossier », dont l'information R. 611-7 sur une irrecevabilité, une inopérance, la compétence liée ou une substitution de base légale. L'article R. 611-7 n'impose cette information que lorsque « la décision lui paraît susceptible d'être fondée sur un moyen relevé d'office » : c'est l'annonce d'un motif envisagé, et le corpus le confirme (2 annulations sur 18).
- L'exactitude. La portée de CE, 12 février 2003, n° 218983 est resserrée sur son analyse : les allégations sont tenues pour établies quand l'administration ne donne pas ses motifs au juge qui les lui demande. La substitution de base légale relevée d'office est rattachée à CE, Sect., 3 décembre 2003, El Bahi (analyse : le juge peut y procéder de sa propre initiative après avoir mis les parties à même de présenter leurs observations).

**Preuve que la ligne atteint l'agent.** `contrat_compact` a été rejoué avec la fiche actuelle, l'horloge de chaque sonde et, pour les 120 sessions, le contexte du blocage de fin de tour reconstitué depuis `_brut.jsonl`. Contrôle préalable : la simulation reproduit à l'identique les 80 contrats remis dans v54 (les 12 écarts concernent v50, dont la fiche a changé depuis). Résultats :
- 120 sessions : la ligne arrive dans les 16 sessions qui reçoivent aujourd'hui ANNT-R1, en tête de « Ce qui remplit « bien_fonde » », sans déplacer d'autre ligne ; elle n'arrive dans aucune autre.
- 300 dossiers (consigne et dossier lu) : 62 déclenchements, 59 annulations et 3 rejets. Dans les 14 dossiers nouveaux, la ligne prend l'une des quatre places « ce qui la remplit » et n'en déplace une autre que dans 2 cas ; contrat le plus long 5 607 caractères (5 213 aujourd'hui).

**Décompte.**
- Annulations manquées corrigibles : 8 sur 30 (2000743, 2000745, 2000746, 2000747, 2000750 en v54 ; 2000732, 2000736, 2000740 en v50). Une seule série, un seul cas indépendant. Le gain dépend de la rédaction : ANNT-R1 a déjà échoué cinq fois sur ces dossiers.
- Rejet manqué visé : 2200135, que l'exception R. 611-7 doit ramener au rejet ; incertain, car les autres moyens restaient en débat.
- Rejets bien prédits à risque : aucun dans les 120 (0 sur 53 reçoit la ligne). Les 7 annulations réussies qui la reçoivent l'ont déjà dans le même sens.
- Corpus : 59 annulations et 3 rejets, dont 19 et 16 annulations dans les deux séries jumelles (refus implicites de titre de séjour annulés faute de communication des motifs, CRPA, art. L. 232-4 ; autorisations de licencier) ; hors séries, 24 annulations et 3 rejets. Les trois rejets portent une information R. 611-7 : irrecevabilité du moyen de motivation (2200135), refus d'abroger aux moyens inopérants (2202586), substitution de base légale (2300087). Sur une distribution réelle où l'annulation est minoritaire, la précision serait plus basse que 59 sur 62.

**Ce que la règle ne dit pas.** Elle ne fait pas du silence un acquiescement sans mise en demeure. Elle vise la conduite procédurale d'une partie, visible dans les visas, et ne nomme ni juridiction ni magistrat (CJA, art. L. 10).

## 6. Éléments existants à corriger

- **Ligne « Décision implicite »** : retirer la présomption « la requête qui soulève ce moyen s'appuie d'ordinaire sur cette demande [...] le moyen est fondé et suffit à l'annulation ». Elle n'est vraie que lorsque l'auteur se tait (23 / 1), cas que couvre ANNT2-R1 ; quand il défend, 17 / 31. Décompte sur les 120 : 2 rejets corrigibles (2104190, 2205147), 1 annulation à risque (2300296, dont l'agent a recopié la formule et dont la défense est arrivée après la clôture). Texte de remplacement dans le bloc JSON. Ce n'est pas une règle nouvelle : la correction retire une affirmation inexacte.
- **Ligne du dessaisissement d'armes** : sa garde (« préfet », « police »...) et son marqueur « insuffisamment motiv » la font remettre dans 49 dossiers sur 300, dont un seul concerne des armes, et dans 15 sessions v54. Elle occupe une des quatre places « ce qui la remplit ». Garde proposée dans le bloc JSON ; effet sur l'issue non mesuré.
- **Observation sans proposition** : dans les 120 sessions, le contrat n'est arrivé qu'au blocage de fin de tour, après une première réponse déjà chiffrée ; `contrat_a_la_lecture` n'a laissé aucun drapeau `etat/.contrat_donne`. La cause n'a pas été recherchée. Dans la série des licenciements, les premières réponses donnaient le rejet à 70-85 %, et la consigne de révision (« garder l'issue si elle tient ») a joué en faveur du maintien.

## 7. Limites

- Les 120 sondes font partie des 300 : le corpus élargit le contrôle sans le rendre indépendant. Huit des 30 annulations manquées appartiennent à une même série, ce qui pèse sur tout décompte.
- Les échantillons sont équilibrés à 50 %. Les proportions par matière (séjour, naturalisation, urbanisme) reflètent l'échantillonnage du banc et ne sont pas des taux d'annulation.
- Les comptes du tableau reposent sur des expressions régulières. Ceux de l'auteur muet, de R. 611-7, du mémoire tardif, de la note en délibéré et des mesures d'instruction ont été relus dossier par dossier ; les autres non.
- L'effet de la nouvelle rédaction sur les réponses de l'agent n'est pas mesuré ; seul le banc le dira.

## 8. Sources lues

- CJA, art. R. 611-7, version en vigueur depuis le 10 février 2019 (LibreJustice, texte lu).
- CE, Sect., 3 décembre 2003, El Bahi, n° 240267, Recueil (analyse lue).
- CE, 12 février 2003, n° 218983, tables (analyse lue).
- CE, 26 novembre 2012, Cordière, n° 354108, Recueil (analyse lue).
- CE, Sect., 3 février 1999, Montaignac, n° 149722, Recueil (analyse lue).
- Repris d'ANNT.md sans relecture : CJA, art. R. 612-3 et R. 612-6 ; CRPA, art. L. 243-2 ; CE, 26 juin 2023, n° 467714 ; CE, 30 décembre 2009, n° 314972 ; CE, 31 mars 2017, n° 399123 (analyse seule).
- Jugements relus dans leurs motifs décisifs : 2000746 en entier ; 2201698, 2201767, 2010061, 2206091, 2208539, 2402133, 2002686, 2008294, 2006773, 2100533, 2101739, 2300284, 2308621 ; rejets 2107936, 2006427, 2104190, 2205147 ; corpus : 2403312, 2422039, 2304208, 2206785, 2207365, 2401842, 2102805, 2300087, 2203882, 2404827. Les jugements 2000743, 2000745, 2000747 et 2000750 ont été téléchargés, non relus.
- Les 120 sessions (`_brut.jsonl` : première réponse, contrat remis, réponse finale), `index_v54.json`, `index_v50.json`, ANNT.md, `hook.py` (`contrat_compact`, `_applicable`, `contrat_a_la_lecture`, `aiguillage`) et le bloc « Données de contrôle » de la fiche.
