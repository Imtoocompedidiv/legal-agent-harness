# URGT : surestimation de l'urgence dans les référés-suspension contre un refus de renouvellement de titre de séjour

```json
{
  "famille": "URGT",
  "version_de_reference": "v50",
  "date": "2026-11-23",
  "fiche": "plugins/contentieux/skills/mecanique-des-exercices/references/refere-suspension.md",
  "regles": [
    {
      "id": "R1_presomption_sejour_reecrite",
      "cible": "presomptions[cas = titre de séjour] : remplacer « cas » et « renversement », garder les marqueurs, compléter la source",
      "cas": "Refus de renouvellement ou retrait d'un titre donnant droit au séjour (carte de séjour temporaire ou pluriannuelle, carte de résident, certificat de résidence algérien).",
      "renversement": "Présomption simple. Le juge l'écarte par des circonstances particulières qu'il expose, qu'elles soient invoquées par l'administration ou tirées de la requête, de ses pièces et de la décision attaquée, y compris au tri (CE, 24 juill. 2024, n° 478463, pt 4 ; CE, 24 juill. 2024, n° 471701, pt 4 ; CE, 27 août 2001, n° 235178). Après communication, le silence de l'administration la laisse jouer : le Conseil d'État casse l'ordonnance qui l'écarte sans exposer de circonstance quand le préfet n'en a fait valoir aucune (CE, 12 déc. 2024, n° 497389, pt 5 ; CE, 17 juin 2025, n° 503085, pt 5 ; CE, 24 oct. 2025, n° 505151, pt 4). Ne l'écartent pas à eux seuls : les récépissés délivrés pendant l'instruction qui a conduit au refus (CE, 18 févr. 2022, n° 457933, pts 4 et 5), l'ancienneté de la décision ou l'impossibilité d'éloigner (n° 503085, pt 5), le défaut de pièce sur la perte d'emploi ou de ressources (CE, 23 juin 2023, n° 472013, pt 4), une menace à l'ordre public alléguée sans être établie (n° 497389, pt 8). Hors renouvellement, l'urgence n'est pas présumée ; la demande déposée hors des délais de l'article R. 431-5 du CESEDA (120e au 60e jour avant l'expiration pour un titre du téléservice, annexe 9 ; sinon les deux mois qui la précèdent, CE, 29 févr. 2024, n° 489196, pt 4) vaut en principe première demande (CE, 12 mai 2022, n° 461894, pt 5) ; quelques juges la gardent pour un retard de quelques jours, et elle joue si un rendez-vous a été demandé à temps. Sans présomption, l'issue tient à la preuve par pièces d'une perte imminente (emploi, ressources, prise en charge) ; des allégations générales mènent au rejet, souvent au tri.",
      "marqueurs": ["titre de séjour", "carte de résident", "carte de séjour", "récépissé", "renouvel"],
      "source": "CE, Sect., 14 mars 2001, n° 229773 ; CE, 27 août 2001, n° 235178 ; CE, 18 févr. 2022, n° 457933 ; CE, 12 mai 2022, n° 461894 ; CE, 23 juin 2023, n° 472013 ; CE, 29 févr. 2024, n° 489196 ; CE, 24 juill. 2024, n° 471701 et n° 478463 ; CE, 12 déc. 2024, n° 497389 ; CE, 17 juin 2025, n° 503085 ; CE, 24 oct. 2025, n° 505151 ; textes intégraux lus le 23 nov. 2026 ; CESEDA, art. R. 431-5, cité par ces décisions ; CAA Nancy, 17 juill. 2026, n° 26NC01556, TA Cergy-Pontoise, 2 déc. 2025, n° 2520924, TA Melun, 23 mai 2024, n° 2404123 (sources actuelles de la nuance sur le retard de quelques jours, non relues)",
      "corrige_probablement": {"URGT": ["2309271 (oui, finale non) si les récépissés antérieurs au refus cessent d'être lus comme une faiblesse"], "URGD": [], "URG": []},
      "risque": {"URGT": [], "URGD": "faible, non mesuré : séjour après communication, le texte dit expressément que le silence du préfet laisse jouer la présomption", "URG": "idem"},
      "role": "retire les trois phrases qui ont fait basculer à tort six réponses justes (voir lignes_a_retirer) ; les corrections viennent surtout de R2, R3 et R4"
    },
    {
      "id": "R2_pas_un_renouvellement",
      "cible": "conditions_decisives[urgence].ce_qui_la_fait_tomber : ligne marquée",
      "texte": "Titre de séjour, demande qui n'est pas un renouvellement : la présomption ne couvre que le renouvellement d'un titre donnant droit au séjour que le requérant détenait. Elle ne joue pas pour un titre sur un autre fondement, ainsi la carte « recherche d'emploi ou création d'entreprise » demandée par un ancien étudiant (CE, 7 févr. 2025, n° 497396, mentionné aux tables, pt 5), ni après de simples autorisations délivrées à titre gracieux (CE, 24 juill. 2024, n° 471701, pt 4), ni pour une demande présentée hors des délais de l'article R. 431-5 du CESEDA (CE, 12 mai 2022, n° 461894, pt 5). Le juge le relève sur les pièces sans que l'administration l'invoque (TA Lyon, 5 nov. 2026, n° 2614132, pt 7 ; TA Melun, 21 août 2026, n° 2613546, ordonnance de tri). Le requérant doit alors prouver par pièces une perte imminente.",
      "marqueurs": ["titre de séjour", "carte de (?:séjour|résident)", "certificat de résidence"],
      "exige": ["renouvel\\w*\\s+(?:de\\s+|d.)?(?:son|sa|ses|du|des|leur|de son|de sa)\\s+(?:titre|carte|certificat|récépissé)|renouvel\\w*\\s+(?:de\\s+|d.)(?:titre|carte|certificat)s?\\s+de\\s+(?:séjour|résident|résidence)|refus de renouvellement(?!\\s+ou\\s+retrait)|refus\\w*\\s+de\\s+(?:lui\\s+)?renouveler"],
      "source": "CE, 7 févr. 2025, n° 497396 ; CE, 24 juill. 2024, n° 471701 ; CE, 12 mai 2022, n° 461894 ; TA Lyon, 5 nov. 2026, n° 2614132 ; TA Melun, 21 août 2026, n° 2613546 ; textes intégraux lus le 23 nov. 2026 (les deux ordonnances de TA ne sont pas des sondes du banc)",
      "declenchee": {"URGT": 36, "URGD": 30, "URG": 14},
      "corrige_probablement": {"URGT": ["2318676 (titre étudiant puis L. 422-8 et L. 422-10 visés)", "2302295 (dépôt après expiration reconnu à l'audience, avec R4)"], "URGD": [], "URG": []},
      "risque": {"URGT": [], "URGD": [], "URG": ["2611360 (oui ; injonction subsidiaire « recherche d'emploi » et moyen tiré de L. 422-10, alors que la décision visée est un refus de renouvellement)"]}
    },
    {
      "id": "R3_requete_au_tri",
      "cible": "conditions_decisives[urgence].ce_qui_la_fait_tomber : ligne marquée, garde de stade (aucune trace de communication)",
      "texte": "Requête au stade du tri, sans communication, défense ni audience (CJA, art. L. 522-3) : le juge statue sur la requête et ses pièces, décision attaquée comprise, sans entendre l'administration ; l'absence de défense n'y prouve donc aucune absence de circonstance particulière. La requête doit justifier de l'urgence (CJA, art. R. 522-1) : pour un refus de séjour, faire apparaître le titre détenu, sa date d'expiration et une demande de renouvellement présentée dans les délais, puis les pièces de la perte qu'elle invoque. Le juge du tri lit ces dates sur les pièces et écarte d'office la présomption si la demande était tardive ou portait sur un autre titre (TA Melun, 21 août 2026, n° 2613546 ; CE, 24 juill. 2024, n° 471701, rejet au tri confirmé). Si le dossier ne donne pas ces dates, la présomption n'est pas acquise : juger aussi l'urgence sans elle, sur les pièces de préjudice ; des allégations générales mènent au rejet sans audience.",
      "marqueurs": ["^(?![\\s\\S]*(?:Ont été entendus|au cours de l.audience publique|audience publique du|a été communiquée? (?:au|à)|mémoire en défense,? enregistré|n.a pas produit (?:de |d.)|régulièrement (?:convoqu|averti)|[Pp]ar un mémoire,? enregistré|a produit (?:des|une) pièces?,? enregistrée))"],
      "exige": ["renouvel\\w*\\s+(?:de\\s+|d.)?(?:son|sa|ses|du|des|leur|de son|de sa)\\s+(?:titre|carte|certificat|récépissé)|renouvel\\w*\\s+(?:de\\s+|d.)(?:titre|carte|certificat)s?\\s+de\\s+(?:séjour|résident|résidence)|refus de renouvellement(?!\\s+ou\\s+retrait)|refus\\w*\\s+de\\s+(?:lui\\s+)?renouveler"],
      "source": "CJA, art. L. 522-3 et R. 522-1 (lus pour la fiche le 19 nov. 2026, cités par TA Melun n° 2613546 et TA Paris n° 2412906, lus le 23 nov. 2026) ; CE, 24 juill. 2024, n° 471701 ; TA Melun, 21 août 2026, n° 2613546 ; l'exigence que la requête montre le titre et la date de la demande est une inférence de R. 522-1 appliquée par les juges du tri, non posée par le Conseil d'État",
      "declenchee": {"URGT": 13, "URGD": 13, "URG": 2},
      "corrige_probablement": {"URGT": ["2307864", "2418458", "2530252", "2318676", "2327246", "2412906", "2428876", "2632022", "2324792 (moins sûr)", "2313195 et 2313375 peu probables : la requête présente bien un refus de renouvellement"], "URGD": ["2412265", "2514411", "2310188", "2311042", "2404540", "2410253", "2500317", "2604330 (déclenchées, issue non, réponse oui ; effet non vérifié une à une)"], "URG": ["2609111", "2508809"]},
      "risque": {"URGT": [], "URGD": [], "URG": []},
      "reserve": "Gain gonflé par la construction du banc : aucune des 48 requêtes sans communication des trois familles n'a été accueillie, puisqu'une suspension ne peut être prononcée qu'après audience (CJA, art. L. 522-1). Le zéro risque mesuré ici ne vaut pas preuve. En usage réel, la ligne apparaîtra pour toute requête avant communication ; son contenu dit ce que la requête doit montrer, sans annoncer de rejet."
    },
    {
      "id": "R4_document_provisoire_juges_partages",
      "cible": "conditions_decisives[urgence].points_disputes (nouvelle clé, lue par contrat_compact sous « Juges partagés »)",
      "texte": "Titre de séjour et document provisoire valable à la date où le juge statue : le Conseil d'État a écarté la présomption devant un récépissé de la demande de renouvellement délivré après la saisine du juge, qui attestait la reprise de son instruction (CE, 17 juin 2025, n° 503085, pt 8), mais l'a maintenue devant une attestation de prolongation d'instruction (CE, 24 oct. 2025, n° 505151, pt 7) et a suspendu malgré un récépissé délivré en cours d'instance (CE, 29 févr. 2024, n° 489196, pts 7 et 10) ; les récépissés de l'instruction qui a précédé le refus ne l'écartent pas (CE, 18 févr. 2022, n° 457933, pt 4). Peser si le document montre que l'administration réexamine la demande (récépissé de cette demande, autorisation délivrée dans l'attente de l'examen, convocation pour le renouveler) ou s'il accompagne seulement le refus, comme une autorisation provisoire de quelques mois laissée après le refus d'une carte de résident.",
      "marqueurs": [
        "(?:dispose|bénéficie|bénéficié|s.est vu délivrer|a été délivrée?|lui a délivré|lui accorde|en possession|convoqu\\w*)[^.;]{0,100}(?:récépissé|autorisation provisoire de séjour|\\bAPS\\b|attestation de prolongation)",
        "(?<!délivrer une )(?:récépissé|autorisation provisoire de séjour|\\bAPS\\b)s?[^.;]{0,20}valable\\s+(?:du|jusqu)"
      ],
      "exige": ["renouvel\\w*\\s+(?:de\\s+|d.)?(?:son|sa|ses|du|des|leur|de son|de sa)\\s+(?:titre|carte|certificat|récépissé)|renouvel\\w*\\s+(?:de\\s+|d.)(?:titre|carte|certificat)s?\\s+de\\s+(?:séjour|résident|résidence)|refus de renouvellement(?!\\s+ou\\s+retrait)|refus\\w*\\s+de\\s+(?:lui\\s+)?renouveler"],
      "source": "CE, 17 juin 2025, n° 503085 ; CE, 24 oct. 2025, n° 505151 ; CE, 29 févr. 2024, n° 489196 ; CE, 18 févr. 2022, n° 457933 ; textes intégraux lus le 23 nov. 2026",
      "declenchee": {"URGT": 6, "URGD": 2, "URG": 0},
      "corrige_probablement": {"URGT": ["2302295 (APS délivrée après le référé, dans l'attente de l'examen)", "2534508 (convocation pour renouveler le récépissé)", "2309271 possible (récépissés antérieurs au refus)"], "URGD": [], "URG": []},
      "risque": {"URGT": ["2608821 et 2602704 (APS laissée après le refus d'une carte de résident ; le texte les range du côté de la présomption)", "2301024 (récépissés antérieurs au refus ; même remarque)"], "URGD": ["2321430 (déclenchement sur une injonction de convoquer, sans effet attendu)"], "URG": []}
    }
  ],
  "lignes_a_retirer": [
    {"ou": "presomptions[titre de séjour].cas", "texte": "même lorsque l'étranger conserve des récépissés ou reçoit une autorisation provisoire de séjour", "motif": "généralise CE n° 457933 ; contredit par CE n° 503085 (récépissé attestant la reprise de l'instruction) et CE n° 471701 (autorisations gracieuses) ; cité par l'agent pour basculer à tort 2302295 et 2534508"},
    {"ou": "presomptions[titre de séjour].renversement", "texte": "L'administration doit invoquer et établir des circonstances particulières, que le juge expose", "motif": "inexact : le juge prend en compte « les circonstances particulières pouvant conduire à renverser cette présomption ou celles mises en avant par l'autorité administrative » (CE n° 478463, pt 4) et peut le faire au tri (CE n° 471701) ; l'agent en déduit qu'au tri, sans défense, rien ne renverse la présomption (2313195, 2327246, 2307864, 2324792, 2632022, 2530252, 2418458)"},
    {"ou": "presomptions[titre de séjour].renversement", "texte": "des récépissés, une autorisation provisoire ou une menace à l'ordre public alléguée sans être établie n'y suffisent pas", "motif": "trop absolu pour le récépissé et l'APS (CE n° 503085) ; la menace non établie reste dans R1"},
    {"ou": "presomptions[titre de séjour].renversement", "texte": "Comparer les dates du dépôt et de l'expiration ; absentes du dossier, les nommer comme le fait à établir.", "motif": "l'agent nomme le fait puis garde la présomption ; R3 dit comment juger sans ces dates au tri"},
    {"ou": "hook.py, l. 640 (revue du hook Stop)", "texte": "une cause d'échec ne vaut rien si le dossier n'en montre pas les faits", "motif": "en séjour, les faits qui renversent la présomption (motifs de la décision, dates du titre et de la demande) sont dans les pièces du juge et absents du dossier remis ; la consigne fait écarter ces causes et garder la présomption. À nuancer plutôt qu'à retirer : « ... sauf quand le juge les tient de pièces que le dossier ne reproduit pas »"},
    {"ou": "conditions_decisives[urgence].ce_qui_la_remplit[0]", "texte": "Avant la défense, au contraire, l'administration produira les éléments qui fondent sa mesure : les supposer produits.", "motif": "phrase juste mais jamais remise au tri, car tous les marqueurs de la ligne supposent une communication ; R3 reprend ce rôle"}
  ],
  "estimation_globale_non_mesuree": "URGT écartée 5/20 vers 10 à 13/20, retenue 18/20 vers 17 à 19/20 ; URGD et URG : jusqu'à 10 réponses non corrigées par R3, risque connu 1 (URG 2611360). À rejouer sur le banc avant toute conclusion."
}
```

## 1. Ce que montrent les chiffres

Les verdicts ont été relus dans les transcriptions (`_brut.jsonl`), le champ `premiere_reponse` de l'index régénéré étant vide pour les 280 sondes. Première réponse URGT, avant le hook Stop : urgence retenue 16/20, écartée 11/20. Réponse finale : 18/20 et 5/20. La relecture déclenchée par le contrat a fait passer six « non » justes à « oui » (2302295, 2530252, 2534508, 2318676, 2307864, 2418458), quatre « non » faux à « oui » (2313993, 2400702, 2300908, 2608821) et deux « oui » justes à « non » (2309271, 2308094).

Le contrat remis pour 2313195 a été relu dans sa transcription. Ses cinq lignes « ce qui fait tomber l'urgence » parlent d'agents publics, de cotisations et d'assistants familiaux ; aucune ne concerne le séjour. Les lignes utiles de la fiche (retard du requérant, recours suspensif) arrivent en septième et neuvième position et ne passent jamais. La seule matière propre au séjour est la présomption, dont le renversement est écrit comme une charge de l'administration, avec récépissés et APS déclarés sans effet. L'agent relit le dossier sous ce texte et conclut que rien ne renverse la présomption.

Le stade de la procédure sépare les issues sans exception. Les 20 urgences retenues ont toutes été jugées après communication et audience. Seize des 20 urgences écartées sont des ordonnances de tri (article L. 522-3), sans communication ni audience, et les quatre autres ont été rendues après audience (2302295, 2523198, 2534508, 2405061). Sur les trois familles, les 48 dossiers sans communication sont tous des rejets. Cette séparation tient à l'article L. 522-1, qui interdit de suspendre sans audience : elle décrit la construction du banc et ne fonde aucune règle à elle seule.

## 2. Ce qui distinguait l'issue, sonde par sonde

Motifs lus dans les 40 ordonnances. « Visible » désigne ce que le dossier remis laisse voir.

| Sonde | Issue | 1re → finale | Stade | Motif réel du juge | Visible dans le dossier | Règle |
|---|---|---|---|---|---|---|
| 2302295 | non | non → oui | audience | APS du 28 mars au 27 juin délivrée pendant l'instance : séjour autorisé pendant l'examen | défense sur l'APS ; dépôt après expiration reconnu à l'audience | R4, R2 |
| 2313195 | non | oui → oui | tri | 18 condamnations lues dans la décision ; intérim récent, contrat conclu après le refus | rien de décisif (saisine 66 jours après la décision) | aucune légitime |
| 2313375 | non | oui → oui | tri | condamnations lues dans la décision ; aucune pièce d'emploi ; saisine trois mois après notification | délai de 95 jours ; emploi déjà perdu | aucune légitime |
| 2523198 | non | oui → oui | audience | seule la présomption est invoquée, aucune atteinte alléguée ; saisine 52 jours après | défense : aucune perte de salaire | aucune (TA contraire à CE n° 472013) |
| 2530252 | non | non → oui | tri | allégations non établies jugées de nature à remettre en cause la présomption | décision du 16 mai, référé du 16 octobre ; OQTF ; aucune date du titre | R3 |
| 2534508 | non | non → oui | audience | convocation pour renouveler le récépissé : séjour régulier à la date de l'ordonnance | défense sur la convocation | R4 |
| 2632022 | non | oui → oui | tri | demande hors délai, première demande ; ARE sans pièces | dernier récépissé expiré, ARE arrêtée ; dates absentes | R3 |
| 2300176 | non | non → non | tri | APS déjà ordonnée par jugement ; CDI non menacé | « délivrance », mesure d'éloignement | |
| 2318676 | non | non → oui | tri | étudiant vers recherche d'emploi : pas un renouvellement ; fond jugé bientôt | L. 422-8 et L. 422-10 visés, « refusé de lui délivrer » | R2, R3 |
| 2327144 | non | non → non | tri | audience collégiale au fond prochaine | urgence fondée sur la seule OQTF | |
| 2327246 | non | oui → oui | tri | fond jugé bientôt ; licencié, sans emploi | présomption non invoquée ; « l'empêche de trouver un emploi » | R3 |
| 2412906 | non | oui → oui | tri | saisine plus d'un an après la décision implicite ; perte d'emploi non établie | décision implicite sans date | R3 |
| 2428876 | non | oui → oui | tri | fond jugé bientôt ; recours suspensif contre l'OQTF | titre expiré le 13 nov. 2023, refus du 30 août 2024 ; OQTF ; contrat rompu | R3 |
| 2601412 | non | non → non | tri | demande hors délai ; référé neuf mois après le fond | carte de résident, dates du fond | |
| 2307864 | non | non → oui | tri | demande reçue après l'expiration : première demande | décision implicite, précarité ancienne | R2, R3 |
| 2324792 | non | oui → oui | tri | fond jugé bientôt ; perte du RSA insuffisante | RSA | R3 (moins sûr) |
| 2402439 | non | non → non | tri | saisine cinq mois après ; fond jugé bientôt | dates visibles | |
| 2405061 | non | oui → oui | audience | demande déposée sept jours après l'expiration, lue dans les pièces | rien (préfet absent) | aucune légitime |
| 2418458 | non | non → oui | tri | enrôlement prochain ; OQTF suspendue par le recours | OQTF, étudiant | R3 |
| 2508415 | non | non → non | tri | demande hors délai ; nouveau récépissé | dates visibles | |
| 2300658 | oui | oui → oui | audience | présomption, préfet muet | OQTF et IRTF, requête mince | |
| 2301024 | oui | oui → oui | audience | présomption ; ordre public allégué sans effet | récépissés antérieurs | |
| 2304861 | oui | oui → oui | audience | présomption, préfet muet | saisine 99 jours après | |
| 2305095 | oui | oui → oui | audience | préfet se borne à nier le licenciement | | |
| 2400705 | oui | oui → oui | audience | aucune circonstance invoquée | saisine près de quatre mois après | |
| 2602704 | oui | oui → oui | audience | APS précaire, allocations CAF suspendues | APS accordée avec le refus d'une carte de résident ; ordre public | R4 (protégée) |
| 2623077 | oui | oui → oui | audience | récépissés successifs, présomption | OQTF, ordre public discuté | |
| 2217404 | oui | oui → oui | audience | présomption, préfet muet | | |
| 2309271 | oui | oui → non | audience | récépissés renouvelés, préfète ne remet pas en cause la présomption | titre expiré en 2019, demande en 2020 ; 40 mois de prison | R1, R4 |
| 2313993 | oui | non → oui | audience | demande de renouvellement déposée | saisine sept mois après | |
| 2315597 | oui | oui → oui | audience | présomption, situation irrégulière | | |
| 2328986 | oui | oui → oui | audience | présomption, préfet muet | étudiant, OQTF | |
| 2400702 | oui | non → oui | audience | aucune circonstance au dossier | saisine neuf mois après | |
| 2300908 | oui | non → oui | audience | présomption malgré récépissés continus | récépissés | |
| 2302059 | oui | oui → oui | audience | présomption, préfet muet | | |
| 2308094 | oui | oui → non | audience | demande dans les deux mois, présomption | « demande de titre de séjour », sans dates | |
| 2309582 | oui | oui → oui | audience | présomption | | |
| 2313929 | oui | oui → oui | audience | refus d'enregistrer, récépissé sur le point d'expirer | | |
| 2401813 | oui | oui → oui | audience | carte de résident ; intérêt public d'éloigner sans incidence | | |
| 2608821 | oui | non → oui | audience | APS de six mois très précaire face à une carte de résident | APS valable jusqu'au 2 oct. 2026 | R4 (protégée) |

Sur les pistes proposées, voici ce que les décisions montrent.

- Première demande ou titre d'une autre nature : motif réel de 2318676, 2307864, 2601412, 2508415, 2632022 et 2405061. Il ne se voit dans le dossier que pour 2318676.
- Titre expiré longtemps avant la demande : même groupe. Les dates manquent presque toujours, et 2623077, accueilli malgré un dépôt après expiration, montre que les juges ne l'appliquent pas tous.
- Récépissé ou APS : décisif quand le document montre une reprise de l'examen (2302295, 2534508), sans effet quand il précède le refus ou l'accompagne (2300908, 2309271, 2602704, 2608821).
- Retard à saisir le juge : retenu dans 2313375, 2412906, 2402439 et 2601412, toujours avec un autre motif ; sans effet dans 2304861, 2400705, 2313993, 2400702 et 2302059. Le Conseil d'État juge que l'ancienneté de la décision ne suffit pas (n° 503085).
- Menace à l'ordre public : décisive dans 2313195 et 2313375, lue dans les motifs de la décision que le dossier ne reproduit pas ; sans effet quand elle est seulement alléguée (2301024, 2309271, 2602704, 2401813).
- Fraude : aucun cas.
- Situation déjà irrégulière, emploi déjà perdu, minima sociaux : présents dans des rejets (2327246, 2428876, 2324792, 2632022) comme dans des admissions (2313993, 2602704). Aucune règle ne s'en dégage.
- Audience au fond prochaine : motif de sept rejets (2327246, 2324792, 2428876, 2418458, 2327144, 2402439, 2318676), invisible dans les dossiers.
- OQTF dont le recours est suspensif : invoquée dans deux rejets et présente dans sept admissions. Elle ne discrimine pas, et aucune décision lue du Conseil d'État n'en fait une cause de renversement pour un refus de renouvellement.

## 3. L'erreur de raisonnement de l'agent

L'agent lit la présomption comme une règle de charge qui ne cède qu'aux circonstances invoquées et établies par l'administration. Il en conclut qu'au tri, faute de défense, rien ne la renverse. Il ajoute que les récépissés et l'APS sont sans effet, puis renvoie au « fait à établir » les dates du titre et de la demande, qu'il ne voit pas. Ce raisonnement correspond à la jurisprudence de cassation rendue après communication : le Conseil d'État casse l'ordonnance qui écarte la présomption sans motif alors que le préfet, mis en cause, n'a rien opposé (n° 497389, n° 503085, n° 505151).

Les juges du tri font autre chose. Ils lisent la requête, la décision et les pièces. Ils y trouvent eux-mêmes les dates d'un dépôt tardif (TA Melun n° 2613546, hors banc), les condamnations qui motivent le refus (2313195, 2313375), un titre d'une autre nature (2318676) ou une audience au fond proche. Ils écartent alors la présomption sans attendre la défense, ce que le Conseil d'État valide (n° 471701 ; n° 478463, pt 4). Le contrat actuel tire l'agent vers le juge de cassation alors que la question le place au siège du juge du tri.

Quatre rejets restent hors d'atteinte d'une règle exacte. Dans 2523198 et 2324792, le juge exige une perte prouvée, ce que le Conseil d'État censure (n° 472013, n° 457933). Dans 2405061 et dans les deux affaires d'ordre public, le motif tient à des pièces absentes du dossier. Les audiences au fond proches sont elles aussi invisibles.

## 4. Les règles et leur portée

R1 corrige le texte de la présomption, qui est la cause directe des six bascules à tort. Elle n'apporte presque aucune correction seule : son rôle est de cesser de pousser vers « oui ».

R2 ajoute ce que le contrat ne disait pas : le changement de fondement (n° 497396, mentionné aux tables) et les autorisations gracieuses (n° 471701) font sortir du renouvellement, et le juge relève lui-même le dépôt tardif. Elle devrait corriger 2318676 et, avec R4, 2302295. Risque connu : URG 2611360.

R3 dit l'office du juge du tri pour une requête en séjour. C'est la règle au plus fort effet sur ce banc, qui en exagère toutefois le gain (voir la réserve du JSON). Sur 11 échecs URGT déclenchés, cinq à neuf corrections paraissent probables, souvent pour une raison qui n'est pas celle du juge : l'absence de dates dans la requête plutôt que l'audience au fond prochaine. 2313195 et 2313375 resteront probablement fausses, la requête y présentant bien un refus de renouvellement.

R4 pose la question du document provisoire comme un point où les juges se partagent, ce qu'elle est au Conseil d'État lui-même (n° 503085 contre n° 505151 et n° 489196). Corrections attendues : 2302295 et 2534508. 2608821 et 2602704 sont protégés par le critère de la reprise de l'examen.

Les garde-fous ont été testés sur les 120 dossiers des trois familles avec la logique de `_applicable`, une fois sur le dossier seul et une fois avec la fiche ajoutée au contexte, puisque le hook y verse les lectures de la session. La garde `exige` ne retient pas le simple mot « renouvel » : la fiche le contient et ouvrait R2 sur les 120 dossiers. Elle exige une tournure de dossier (« renouveler son titre », « refus de renouvellement de titre de séjour »…), absente de la fiche comme des textes proposés. Les comptes sont alors identiques avec ou sans la fiche. La garde négative de R3 n'est pas fermée par la fiche, qui ne contient aucune des formules d'instruction retenues. Elle le serait si l'agent lisait une ordonnance rendue après audience : la ligne ne viendrait pas, ce qui laisse le contrat en l'état.

## 5. Sources lues le 23 novembre 2026 (LibreJustice, texte intégral)

- [CE, Sect., 14 mars 2001, n° 229773](https://librejustice.fr/decision/D0e6AxjE0NZV)
- [CE, 27 août 2001, n° 235178](https://librejustice.fr/decision/raekWWCJOIOC)
- [CE, 18 févr. 2022, n° 457933](https://librejustice.fr/decision/fVJBTR-O8kkr)
- [CE, 12 mai 2022, n° 461894](https://librejustice.fr/decision/VMso9nmm5QYY)
- [CE, 23 juin 2023, n° 472013](https://librejustice.fr/decision/T1JbxlVAUYNh)
- [CE, 29 févr. 2024, n° 489196](https://librejustice.fr/decision/Az98lTcUkPSg)
- [CE, 24 juill. 2024, n° 471701](https://librejustice.fr/decision/Q8F2cEwoxV6-)
- [CE, 24 juill. 2024, n° 478463](https://librejustice.fr/decision/re9ai5wp5ek7)
- [CE, 12 déc. 2024, n° 497389](https://librejustice.fr/decision/5rMX04bbIoQt)
- [CE, 7 févr. 2025, n° 497396, tables](https://librejustice.fr/decision/PUQ66MS0oqBY)
- [CE, 17 juin 2025, n° 503085](https://librejustice.fr/decision/HorulD_C8CGN)
- [CE, 24 oct. 2025, n° 505151](https://librejustice.fr/decision/R9hZ19zFa0XC)
- [TA Melun, 21 août 2026, n° 2613546](https://librejustice.fr/decision/v1O_L7tQABy8) et [TA Lyon, 5 nov. 2026, n° 2614132](https://librejustice.fr/decision/sHP7-geR9DqZ), hors banc
- Les 40 ordonnances URGT de l'index, lues par le client autorisé ; leurs motifs sur l'urgence sont résumés au tableau 2.
- Non relus : CJA, art. L. 522-1, L. 522-3 et R. 522-1, lus pour la fiche le 19 novembre et cités dans les ordonnances lues ; CESEDA, art. R. 431-5, cité par n° 461894 et n° 489196 ; CESEDA, art. L. 722-7, connu seulement par sa citation dans l'ordonnance 2418458.
