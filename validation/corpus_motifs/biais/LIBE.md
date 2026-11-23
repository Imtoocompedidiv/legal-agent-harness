```json
{
  "audit": "LIBE, version v50, échantillon neuf équilibré (20 admissions, 20 rejets), 23 novembre 2026",
  "fiche": "plugins/contentieux/skills/mecanique-des-exercices/references/refere-liberte.md",
  "regles": [
    {
      "id": "LIBE-1",
      "condition": "urgence_particuliere",
      "tableau": "ce_qui_la_fait_tomber",
      "position": "en tête de la liste (ligne marquée, retenue avant les lignes générales)",
      "ligne": {
        "texte": "Ordonnance rendue sans communication, défense ni audience : c'est une ordonnance de tri, qui ne fait pas droit à la demande. Le juge ne prononce une mesure du référé-liberté qu'après avoir informé les parties de l'audience publique ; il ne s'en dispense que pour rejeter une demande sans urgence, ou manifestement étrangère à la juridiction administrative, irrecevable ou mal fondée au vu de la seule requête, et des visas qui ne font état ni d'instruction contradictoire ni d'audience révèlent ce rejet. L'urgence acquise et le régime local de l'éloignement n'y changent rien. Ne vaut que pour les visas d'une ordonnance rendue, non pour une requête qui attend son instruction (CJA, art. L. 522-1, al. 2, et L. 522-3 ; CE, 28 oct. 2021, n° 448171 ; CE, réf., 25 mars 2026, n° 513685).",
        "marqueurs": [
          "\\A(?![\\s\\S]*(?:audience|en défense|conclu\\w* (?:au rejet|au non-lieu)|observations (?:en défense|présentées|enregistrées)))[\\s\\S]*(?:quitter le territoire|\\bOQTF\\b|éloign|titre de séjour|autorisation provisoire de séjour|droit d'asile|code de l'entrée et du séjour)"
        ],
        "exige": [
          "Vu la procédure suivante",
          "désign\\w*[^.]{0,160}(?:juge des référés|demandes de référé)"
        ],
        "origine": "audit LIBE du 23 novembre 2026, textes et décisions lus le 23 novembre 2026"
      },
      "corrige": [
        "GENP-LIBE-2303503",
        "GENP-LIBE-2301967"
      ],
      "risque": [],
      "consolide": "les 15 autres rejets rendus sans défense ni audience",
      "sources_lues": [
        "CJA, art. L. 522-1 (version du 1er févr. 2009)",
        "CJA, art. L. 522-3 (texte cité par les décisions lues)",
        "CE, 28 oct. 2021, n° 448171",
        "CE, réf., 25 mars 2026, n° 513685"
      ]
    },
    {
      "id": "LIBE-2",
      "condition": "atteinte_grave_manifestement_illegale",
      "tableau": "ce_qui_la_remplit",
      "position": 1,
      "ligne": {
        "texte": "Les visas d'une ordonnance résument les conclusions et les moyens ; ils ne reproduisent ni les pièces (« Vu les autres pièces du dossier ») ni ce qui a été dit à l'audience, où se prouvent la durée du séjour, la vie commune, les enfants et leur entretien. Un résumé général des moyens n'est donc pas une allégation générale et ne fonde pas un rejet ; une défense qui se borne à dire les moyens non fondés ne conteste aucun fait précis. Quand la requête a été communiquée et l'audience tenue, le juge ne l'a pas rejetée au vu de la seule demande, comme l'article L. 522-3 le lui permettait ; l'issue se joue sur les pièces et l'audience. Pèsent alors les éléments que les visas montrent : moyens de seule légalité (incompétence, motivation, erreur de droit), qui ne caractérisent pas par eux-mêmes une atteinte grave et manifestement illégale ; recours au fond suspensif qui rend la demande irrecevable ; demande d'asile déjà rejetée (CJA, art. L. 522-1 et L. 522-3 ; CE, réf., 12 déc. 2016, n° 405475 ; CE, réf., 5 août 2026, n° 518408).",
        "marqueurs": [
          "audience publique (?:qui a eu lieu|du|tenue)",
          "après avoir entendu",
          "ont été entendus",
          "au cours de l'audience",
          "entendu les observations"
        ],
        "exige": [
          "quitter le territoire|\\bOQTF\\b|éloign|titre de séjour|autorisation provisoire de séjour|droit d'asile|code de l'entrée et du séjour"
        ],
        "origine": "audit LIBE du 23 novembre 2026"
      },
      "corrige": [
        "GENP-LIBE-2304370",
        "GENP-LIBE-2304623",
        "GENP-LIBE-2401417",
        "GENP-LIBE-2303918",
        "GENP-LIBE-2400977",
        "GENP-LIBE-2401038",
        "GENP-LIBE-2401284",
        "GENP-LIBE-2301008",
        "GENP-LIBE-2401061",
        "GENP-LIBE-2401433",
        "GENP-LIBE-2206443"
      ],
      "corrige_note": "avec LIBE-3, affichée sur les mêmes onze dossiers (dix référés-liberté et un référé-suspension, tous de Mayotte)",
      "consolide": [
        "GENP-LIBE-2302957",
        "GENP-LIBE-2400513",
        "GENP-LIBE-2303414"
      ],
      "risque": [
        {
          "sonde": "GENP-LIBE-2300998",
          "niveau": "élevé",
          "raison": "audience tenue, rien de visible ne la distingue des admissions"
        },
        {
          "sonde": "GENP-LIBE-2206448",
          "niveau": "moyen",
          "raison": "audience tenue ; moyens d'incompétence et de motivation, asile invoqué : contrepoids de la ligne"
        },
        {
          "sonde": "GENP-LIBE-2306163",
          "niveau": "faible",
          "raison": "référé-suspension en métropole, recours au fond suspensif invoqué en défense : contrepoids de la ligne ; LIBE-3 non affichée"
        }
      ],
      "sources_lues": [
        "CJA, art. L. 522-1 et L. 522-3",
        "CE, réf., 12 déc. 2016, n° 405475",
        "CE, réf., 5 août 2026, n° 518408",
        "les 40 décisions réelles de l'échantillon"
      ]
    },
    {
      "id": "LIBE-3",
      "condition": "atteinte_grave_manifestement_illegale",
      "tableau": "ce_qui_la_remplit",
      "position": 2,
      "remplace": "la ligne « À Mayotte, l'éloignement effectif est interdit dès la saisine du juge du référé-liberté... » (CESEDA, art. L. 761-9, 2°), dont elle reprend le contenu",
      "ligne": {
        "texte": "À Mayotte et en Guadeloupe, le recours contre l'obligation de quitter le territoire ne suspend pas l'éloignement (CESEDA, art. L. 761-8, 1°, et L. 761-2, qui écartent l'article L. 722-7) : le référé-liberté y est la voie ouverte contre la mesure elle-même, sans changement de circonstances à prouver, et l'obligation sans délai exécutoire crée l'urgence particulière. Le juge recherche, au vu des pièces et de l'audience, si l'éloignement porte une atteinte manifestement disproportionnée à la vie privée et familiale ou à l'intérêt supérieur de l'enfant : résidence habituelle ancienne, scolarité sur place, vie commune avec un conjoint ou un parent français ou en situation régulière, enfant français ou scolarisé dont l'intéressé assure l'entretien (CE, réf., 12 déc. 2016, n° 405475 ; CE, réf., 5 août 2026, n° 518408). L'éloignement y est interdit dès la saisine du juge du référé-liberté, jusqu'à ce qu'il informe les parties de la tenue ou non d'une audience et, s'il en tient une, jusqu'à son ordonnance ; l'exécuter après avoir été informé de la saisine porte une atteinte grave et manifestement illégale au droit au recours effectif et justifie l'injonction d'organiser le retour, sauf si la requête n'a atteint l'administration qu'après l'embarquement ; la chronologie décide, et ne se déduit pas du silence du préfet (CESEDA, art. L. 761-9, 2°, et L. 761-3, 2° ; CE, réf., 15 juill. 2025, n° 505559 ; CE, réf., 18 juill. 2024, n° 495939).",
        "marqueurs": [
          "Mayotte",
          "Guadeloupe"
        ],
        "exige": [
          "quitter le territoire|\\bOQTF\\b|éloign"
        ],
        "origine": "audit LIBE du 23 novembre 2026 ; remplace la ligne « À Mayotte, l'éloignement effectif est interdit dès la saisine... »"
      },
      "corrige": "les onze dossiers de LIBE-2, avec elle",
      "risque": "les mêmes que LIBE-2 pour GENP-LIBE-2300998 et GENP-LIBE-2206448 ; elle s'affiche aussi sur les 11 rejets de tri de Mayotte, où LIBE-1 la contrebalance (voir la section 5)",
      "sources_lues": [
        "CESEDA, art. L. 761-2 (Guadeloupe), L. 761-3, L. 761-8 (versions du 22 nov. 2023 et du 11 nov. 2025), L. 761-9, L. 722-7 (version du 1er mai 2021)",
        "CE, réf., 12 déc. 2016, n° 405475",
        "CE, réf., 5 août 2026, n° 518408",
        "CE, 21 déc. 2022, n° 466934 (portée de l'exclusivité de la procédure spéciale)"
      ],
      "sources_non_relues": [
        "CE, réf., 15 juill. 2025, n° 505559",
        "CE, réf., 18 juill. 2024, n° 495939 (reprises de la ligne remplacée)"
      ]
    },
    {
      "id": "LIBE-4",
      "condition": "atteinte_grave_manifestement_illegale",
      "tableau": "ce_qui_la_remplit",
      "position": 3,
      "ligne": {
        "texte": "Hors de Mayotte et de Guadeloupe, le recours en annulation contre l'obligation de quitter le territoire suspend l'éloignement jusqu'au jugement, sans interdire l'assignation à résidence ni la rétention (CESEDA, art. L. 722-7). Éloigner l'étranger tant que ce recours est pendant, ou organiser son départ avant le jugement (convocation pour un départ, vol, « routing »), porte au droit au recours effectif, qui comprend le droit de ne pas être éloigné avant le jugement, une atteinte grave et manifestement illégale à laquelle il doit être mis fin en urgence, même si le préfet ignorait le recours ; le juge suspend l'exécution ou ordonne le retour (CE, réf., 2 juin 2023, n° 474063 ; l'extension au départ organisé est une inférence du texte).",
        "marqueurs": [
          "recours[^.;]{0,80}(?:est |demeure )?pendant",
          "(?:requête|recours) (?:en annulation|au fond)[^.;]{0,80}(?:pendante?|en cours d'instruction)",
          "en cours d'instruction[^.;]{0,120}obligation de quitter"
        ],
        "exige": [
          "quitter le territoire|\\bOQTF\\b"
        ],
        "origine": "audit LIBE du 23 novembre 2026"
      },
      "corrige": [
        "GENP-LIBE-2305031"
      ],
      "risque": [],
      "sources_lues": [
        "CESEDA, art. L. 722-7 (version du 1er mai 2021, seule version)",
        "CE, réf., 2 juin 2023, n° 474063"
      ]
    }
  ],
  "lignes_existantes": [
    {
      "ligne": "Contre une obligation de quitter le territoire devenue définitive, le référé-liberté est ouvert lorsque des changements de droit ou de fait...",
      "condition": "atteinte_grave_manifestement_illegale",
      "tableau": "ce_qui_la_remplit",
      "action": "ajouter une garde exige, la placer en position 4",
      "exige": [
        "définitiv",
        "jugement (?:du|n°|rendu)|par (?:un|son) jugement|a rejeté (?:sa|la|leur) (?:requête|demande)",
        "circonstances? (?:nouvelles?|de (?:fait|droit))",
        "éléments? nouveaux|élément nouveau|circonstance nouvelle",
        "survenu\\w* (?:depuis|postérieurement)|postérieurement à"
      ],
      "motif": "affichée sur les 40 dossiers par le marqueur « obligation de quitter », elle cadre une OQTF prise la veille à Mayotte comme une mesure définitive à contester par un fait nouveau ; avec la garde, elle reste sur les 4 dossiers qui invoquent un fait nouveau (2412185, 2400873, 2402623, 2405696)"
    },
    {
      "ligne": "À Mayotte, l'éloignement effectif est interdit dès la saisine du juge du référé-liberté...",
      "action": "remplacer par LIBE-3",
      "motif": "exacte mais étroite : l'agent en déduit que la seule issue favorable à Mayotte est un éloignement exécuté après la saisine"
    },
    {
      "ligne": "Section 10, puce « Tableau 15, p. 69 : taux d'admission des pourvois contre les décisions des tribunaux administratifs statuant en référé, tous référés confondus, 14,5 % en 2025 »",
      "action": "la retirer du contrat (la déplacer vers l'exigence 6 sur le pourvoi contre l'ordonnance de tri, sans pourcentage dans la section 10)",
      "motif": "seule puce retenue par contrat_compact au titre des taux publiés ; elle mesure l'admission des pourvois en cassation et se lit comme un taux de succès du référé-liberté de première instance"
    },
    {
      "ligne": "Instruction close seulement (défense produite ou absente, audience tenue)...",
      "action": "conserver",
      "motif": "règle générale exacte ; son incise sur les allégations générales ou sérieusement contestées est celle que l'agent applique au résumé des visas dans 11 échecs sur 12 ; LIBE-2, affichée à côté dans le domaine des étrangers, en borne la lecture sans toucher les autres domaines"
    }
  ],
  "ordre_propose_atteinte_ce_qui_la_remplit": [
    "LIBE-2",
    "LIBE-3",
    "LIBE-4",
    "ligne OQTF devenue définitive (gardée)",
    "ligne retrait d'un titre de séjour"
  ],
  "decompte_v50": {
    "base": "8/20 admissions, 18/20 rejets (réponses finales)",
    "corrections_visées": 14,
    "basculements_possibles": "1 à 3 (2300998, 2206448, 2306163)",
    "plafond_si_suivies": "37 à 40 sur 40 ; non mesuré : la simulation ne vérifie que les lignes remises"
  }
}
```

# Référés-liberté contre l'exécution d'une OQTF : pourquoi v50 sous-estime les admissions

Audit du 23 novembre 2026, famille LIBE de l'échantillon neuf équilibré. Chiffres sur les réponses finales (index régénéré) : 8 admissions justes sur 20, 18 rejets justes sur 20. Le hook Stop a corrigé 3 réponses de « non » à « oui » (2302957, 2400513, 2303414) et en a abîmé une (2303918, « oui » puis « non »).

## Ce qui a été lu

- Les 40 dossiers remis, les 40 réponses finales et la suite des réponses de chaque session (première réponse, puis revue après le hook Stop).
- Les 40 décisions réelles, en texte intégral, par le client LibreJustice du banc.
- Textes, sur LibreJustice : CJA, art. L. 522-1 (version du 1er février 2009) ; L. 522-3, dans la citation qu'en font les décisions lues ; CESEDA, art. L. 722-7 (seule version, depuis le 1er mai 2021), L. 761-2 et L. 761-3 (Guadeloupe), L. 761-8 (versions du 22 novembre 2023 et du 11 novembre 2025 : le 1° écarte L. 722-7 à Mayotte dans les deux), L. 761-9.
- Décisions du Conseil d'État, texte intégral : CE, réf., 12 déc. 2016, n° 405475 ; CE, 21 déc. 2022, n° 466934 ; CE, réf., 2 juin 2023, n° 474063 ; CE, 28 oct. 2021, n° 448171 ; CE, réf., 25 mars 2026, n° 513685 ; CE, réf., 5 août 2026, n° 518408.
- Non relues : CE, réf., 15 juill. 2025, n° 505559, et CE, réf., 18 juill. 2024, n° 495939, reprises telles quelles de la ligne Mayotte existante.
- Le contrat réellement remis, recalculé par `hook.contrat_compact` sur chaque dossier, avant et après les règles (script `simul.py` dans le dossier de travail de l'audit). Aucune session `claude` n'a été lancée : l'effet sur les réponses n'est pas mesuré.

## 1. Ce qui distinguait l'issue dans le dossier remis

Trente et un des quarante dossiers viennent du tribunal administratif de Mayotte, où le recours contre l'OQTF ne suspend pas l'éloignement (CESEDA, art. L. 761-8, 1°) et où le référé-liberté est la seule voie suspensive (L. 761-9, 2° ; CE, réf., 5 août 2026, n° 518408, point 5).

### Le seul signal visible qui sépare les deux issues : la procédure suivie

| Ce que montrent les visas | Admissions | Rejets |
|---|---|---|
| Requête communiquée, défense ou préfet convoqué, audience tenue | 20 | 3 (2206448, 2300998, 2306163) |
| Ni défense, ni audience | 0 | 17 |

Ce partage a une cause légale. Le juge ne prononce une mesure du référé-liberté qu'après avoir informé les parties de l'audience publique (CJA, art. L. 522-1, al. 2) ; il ne s'en dispense que pour rejeter (L. 522-3), et des visas sans instruction contradictoire ni audience révèlent ce rejet (CE, 28 oct. 2021, n° 448171, point 2). Les 17 décisions de rejet sans audience citent toutes l'article L. 522-3. À Mayotte, la décision de tenir audience est en outre le pivot du régime : l'éloignement reste interdit jusqu'à ce que le juge dise s'il tient audience et, s'il en tient une, jusqu'à son ordonnance (L. 761-9, 2°).

### Ce qui a décidé les admissions : des faits que les visas ne reproduisent pas

Dans quinze admissions sur vingt, les visas ne résument que des moyens généraux (article 8 de la Convention, article 3-1 de la convention relative aux droits de l'enfant, caractère exécutoire de l'OQTF). Les ordonnances accordent pourtant sur des faits précis : résidence depuis 2010 ou 2012, scolarité jusqu'au baccalauréat, enfants nés à Mayotte dont un français, conjoint en situation régulière, contribution à l'entretien. Treize des vingt ordonnances citent expressément les pièces produites ou les déclarations à l'audience. Les cinq autres admissions montraient leur ressort dans les visas : faits de vie familiale résumés dans la requête (2304264 : 26 ans de présence, 11 enfants français ; 2401097 : arrivée en 2019, scolarité, oncle titulaire d'une carte de résident), éloignement exécuté après l'enregistrement du référé (2302957, 2303414), recours suspensif pendant (2305031).

Les douze admissions manquées et ce qui les a fait gagner :

| Sonde | Ce qui a fait gagner (motifs) | Visible dans le dossier |
|---|---|---|
| 2304370 | à Mayotte depuis 2012, six enfants dont un français, conjointe en séjour régulier | audience, requérant présent |
| 2304623 | mère d'un enfant français de 20 mois, père absent, déclaré à l'audience | audience ; « elle vit à Mayotte avec son enfant » |
| 2401417 | arrivé à 11 ans, scolarité et bac à Mayotte, mère et sœurs sur place | audience, requérant présent |
| 2303918 | à Mayotte depuis 2013, sept enfants scolarisés, fils cardiaque | audience |
| 2400977 | mère d'un enfant protégé au titre de l'asile | audience, requérante présente |
| 2401038 | vie maritale avec un Français, fille au lycée, enseignante | audience, requérante présente |
| 2401284 | né et scolarisé à Mayotte, fille française ; une première OQTF suspendue deux semaines plus tôt | audience ; « a rappelé son parcours de vie » |
| 2301008 | à Mayotte depuis l'âge de 9 ans, bac, compagne en séjour régulier, deux enfants | audience |
| 2401061 | résidence prouvée depuis 2014, frères français, entreprise créée | audience, rétention |
| 2401433 | arrivé mineur, confié à l'aide sociale à l'enfance, sans attache aux Comores | audience, rétention |
| 2206443 | référé-suspension : enfant né à Mayotte, compagne réfugiée malade | audience, clôture différée |
| 2305031 (Tarn) | convocation pour un départ vers le Portugal alors que le recours suspensif contre l'OQTF est pendant | recours pendant et convocation, préfet absent à l'audience |

Les trois rejets prononcés après audience : 2206448 (demande d'asile rejetée par l'OFPRA sans recours, aucune pièce, arrivée en 2022 ; les visas montrent des moyens d'incompétence et de motivation), 2300998 (ne vit pas avec son enfant ; rien de visible ne le distingue des admissions), 2306163 (référé-suspension à Lille : recours au fond suspensif, donc conclusions contre l'OQTF irrecevables ; la défense le dit dans les visas).

### Les autres pistes, éprouvées sur les deux issues

- Changement de circonstances après l'OQTF ou le jugement : invoqué dans quatre dossiers de métropole (2412185, 2400873, 2402623, 2405696 : mariage, naissance, santé), tous rejetés au tri. Aucune admission ne repose sur lui.
- Éloignement déjà exécuté et demande de retour : décisif dans 2302957 et 2303414 (éloignement le lendemain, après l'enregistrement du référé), que l'agent a jugés justes. Les conclusions « le cas échéant, organiser le retour » figurent aussi dans sept rejets de tri : formule de style, sans valeur discriminante.
- Injonction d'organiser le retour après annulation de l'OQTF : absente de l'échantillon.
- Rétention ou assignation : cinq admissions, quatre rejets. Elle fonde l'urgence, pas l'issue.
- Mariage ou enfant : décisifs dans les motifs des admissions, rarement visibles ; visibles dans deux rejets de tri en métropole sur OQTF ancienne.
- Santé : 2402623 rejeté au tri ; la pathologie d'un enfant a compté dans 2303918 sans apparaître au dossier.
- Asile : 2206448 et 2303541 rejetés.
- Pays de renvoi et article 3 : 2303503 (Soudan) rejeté au tri ; 2401097 (Haïti) admis sur l'article 8.
- Défense absente ou préfet absent à l'audience : 2401097, 2301752 et 2305031 admis ; 2300998 et 2306163 rejetés. Sans valeur propre.
- Audience tenue : le seul partage net, pour la raison légale exposée plus haut.

## 2. L'erreur de raisonnement de l'agent

L'agent lit le résumé des moyens dans les visas comme le dossier entier. Onze de ses douze « non » sur des admissions reposent sur le même enchaînement : la requête invoque l'article 8 « en termes généraux », sans durée de séjour ni enfant ; le préfet conteste ; une allégation générale et contestée n'est pas tenue pour établie ; rejet. Il emprunte ce dernier pas à la ligne « Instruction close seulement » du contrat, juste en droit, et l'applique à un résumé que le juge rédige toujours en termes généraux. Il tient aussi pour une contestation sérieuse une défense qui se borne à dire les moyens non fondés.

Deux erreurs s'y ajoutent.

- Le cadre de l'OQTF définitive : la ligne « Contre une obligation de quitter le territoire devenue définitive » s'affiche sur les 40 dossiers. Sur une OQTF prise la veille à Mayotte, l'agent cherche un fait nouveau postérieur au jugement et conclut qu'il n'y en a pas (2401061). Dans 2401284, il écrit que ce contrôle « relève du recours au fond ». À Mayotte, le recours au fond ne suspend rien, et le Conseil d'État examine le référé-liberté contre l'OQTF elle-même (CE, réf., 12 déc. 2016, n° 405475) ; il y voit la voie qui permet d'en obtenir la suspension à très bref délai (CE, réf., 5 août 2026, n° 518408, point 5).
- 2305031 : l'agent tient pour acquise la dénégation du préfet (« aucune décision de remise ») et ignore que le recours suspensif contre l'OQTF était pendant (CESEDA, art. L. 722-7).

L'urgence n'est pas en cause : l'agent l'admet dans presque tous les dossiers de Mayotte. L'erreur inverse existe aussi : 2303503 et 2301967, rendus sans défense ni audience, ont reçu un « oui ».

Ce que font les juges : le tribunal de Mayotte suspend quand les pièces et l'audience établissent une présence ancienne, des enfants ou un conjoint ; il rejette, au tri ou après audience, quand elles ne le font pas (2300998 ; CE, réf., 25 mars 2026, n° 513685). Le Conseil d'État raisonne de même en appel (n° 405475, point 7 : résidence et vie commune établies « par les documents qu'il produit »).

## 3. Les règles proposées

Le bloc JSON en tête donne le texte prêt à insérer, la condition, le tableau, la position, les marqueurs et la garde de chaque règle. Leur logique :

- **LIBE-1 (tri)**, en tête de « ce qui fait tomber » l'urgence particulière. Marqueur : une expression qui ne correspond que si le texte ne contient ni « audience » ni défense, et relève des étrangers. Garde `exige` : les visas d'une ordonnance rendue (« Vu la procédure suivante », désignation du juge des référés), pour ne jamais s'appliquer à une requête qui attend son instruction.
- **LIBE-2 (visas)**, première ligne de « ce qui remplit » l'atteinte grave et manifestement illégale. Marqueurs : audience tenue. Garde : domaine des étrangers. Elle dit ce que les visas ne contiennent pas, ce que signifie l'audience, et garde les contrepoids visibles (moyens de seule légalité, recours suspensif, asile rejeté).
- **LIBE-3 (Mayotte et Guadeloupe)**, deuxième ligne du même tableau, en remplacement de la ligne Mayotte existante, dont elle reprend le contenu. Marqueurs : Mayotte, Guadeloupe ; garde : OQTF ou éloignement. Les marqueurs désignent le droit territorial applicable (CESEDA, art. L. 761-2 et L. 761-8), non une juridiction ni un magistrat.
- **LIBE-4 (recours suspensif pendant)**, troisième ligne. Marqueurs : recours ou requête en annulation pendant ou en cours d'instruction ; garde : OQTF. L'extension de l'arrêt n° 474063 au départ organisé avant le jugement est signalée dans la ligne comme une inférence.

Budget du contrat : « ce qui remplit » est limité à quatre lignes pour toutes les conditions. Dans un dossier avec audience, l'urgence en prend deux (instruction close, éloignement) ; LIBE-2 et LIBE-3 occupent les deux autres. La garde posée sur la ligne de l'OQTF définitive libère la place.

## 4. Lignes existantes qui poussent à tort vers « non »

1. **« Contre une obligation de quitter le territoire devenue définitive... »** : affichée sur les 40 dossiers, utile pour 4. Ajouter la garde `exige` du bloc JSON (définitive, jugement, circonstance ou élément nouveau, survenance postérieure). Simulation : elle ne reste que sur 2412185, 2400873, 2402623 et 2405696, quatre rejets.
2. **« À Mayotte, l'éloignement effectif est interdit... »** : exacte, mais seule ligne Mayotte, elle laisse croire que l'unique issue favorable est un éloignement exécuté après la saisine (« Le dossier ne montre ni l'un ni l'autre », 2304370). Remplacer par LIBE-3.
3. **Taux publiés, « Tableau 15... 14,5 % »** : seule puce de la section 10 que le hook retient ; elle mesure l'admission des pourvois en cassation contre toutes les ordonnances de référé et se lit comme un taux de succès en première instance. La sortir de la section 10 (sa place est l'exigence 6, pourvoi contre l'ordonnance de tri) ou la réécrire sans pourcentage.
4. **« Instruction close seulement... »** : à conserver. Son incise sur les allégations générales est la phrase que l'agent retourne contre les requérants, mais elle est juste et sert tous les domaines ; LIBE-2, affichée à côté pour les étrangers, en borne la lecture.

## 5. Décompte, sonde par sonde

Contrat recalculé sur les 40 dossiers (simulation des lignes remises, pas des réponses) :

| Groupe | Lignes nouvelles affichées | Effet attendu |
|---|---|---|
| 12 admissions manquées | LIBE-2 et LIBE-3 (10 dossiers de Mayotte et 2206443) ; LIBE-2 et LIBE-4 (2305031) | 12 corrections visées |
| 8 admissions justes | LIBE-2 et LIBE-3 | consolidées, dont les 3 corrigées seulement par le hook Stop |
| 2 rejets manqués (2303503, 2301967) | LIBE-1 et LIBE-3 | 2 corrections visées |
| 15 rejets de tri justes | LIBE-1 (et LIBE-3 pour les 9 de Mayotte) | consolidés ; risque de bascule faible tant que LIBE-1 précède LIBE-3 |
| 3 rejets après audience | LIBE-2 (et LIBE-3 pour 2206448 et 2300998) | 2300998 basculera probablement ; 2206448 peut basculer ; 2306163 peu exposé |

Par règle :

| Règle | Corrigerait | Risquerait de faire basculer |
|---|---|---|
| LIBE-1 | 2303503, 2301967 | aucune : les 20 admissions ont eu une audience, comme l'exige L. 522-1 |
| LIBE-2 et LIBE-3 | 2304370, 2304623, 2401417, 2303918, 2400977, 2401038, 2401284, 2301008, 2401061, 2401433, 2206443 | 2300998 (élevé), 2206448 (moyen), 2306163 (faible) |
| LIBE-4 | 2305031 | aucune dans l'échantillon : son marqueur ne s'allume que sur ce dossier |

Si les règles sont suivies : de 26 sur 40 à un plafond de 37 à 40 sur 40. Avec la part d'aléa observée sur des dossiers presque identiques (2400976 et 2400977, même audience du 3 juin 2024, visas de même facture, issues prédites opposées), une estimation prudente se situe vers 34 à 37. Seul un passage au banc le dira.

## 6. Limites

- La simulation vérifie quelles lignes atteignent l'agent, non ce qu'il en fait.
- Trente et un dossiers sur quarante viennent de Mayotte. Le lien entre audience et issue est structurel (L. 522-1 et L. 522-3), mais la part des admissions parmi les affaires jugées après audience n'est pas connue hors de l'échantillon ; aucune règle n'énonce de taux.
- 2300998 est indiscernable des admissions sur le dossier remis : toute règle qui corrige les onze admissions de Mayotte l'expose.
- Le contrat s'allonge : au plus 4,5 milliers de caractères au lieu de 3,3.
- Aucune règle ne repose sur l'identité d'une juridiction ou d'un magistrat (CJA, art. L. 10) : les marqueurs territoriaux renvoient aux articles L. 761-2 et L. 761-8 du CESEDA.
