```json
{
  "famille": "ANNT",
  "version_analysee": "v50",
  "fiche": "plugins/contentieux/skills/mecanique-des-exercices/references/requete-annulation.md",
  "regles": [
    {
      "id": "ANNT-R1-auteur-sans-defense",
      "condition": "bien_fonde",
      "tableau": "ce_qui_la_remplit",
      "position": "premier élément du tableau, à la place de la ligne « Administration sans défense », qu'elle remplace",
      "texte": "Auteur de la décision sans défense : quand la requête a été communiquée à l'autorité qui a pris la décision et que celle-ci n'a produit aucun mémoire, l'annulation est probable, sauf obstacle de droit. Faute de mise en demeure, l'autorité n'est pas réputée acquiescer aux faits (CJA, art. R. 612-6 ; CE, 26 juin 2023, n° 467714), mais le juge de l'excès de pouvoir ne peut exiger du requérant la preuve des faits qu'il avance et, devant des allégations sérieuses que l'administration ne dément pas, il use de ses pouvoirs d'instruction (CE, 26 novembre 2012, Cordière, n° 354108) ; l'administration qui ne fait pas connaître au juge les motifs de sa décision laisse regarder comme établies les allégations sérieuses du requérant (CE, 12 février 2003, n° 218983). Les moyens tirés de la motivation, de l'examen de la situation, de la procédure suivie ou de l'exactitude des faits ne rencontrent alors aucune explication de l'auteur, et la défense d'un tiers bénéficiaire (employeur ou liquidateur, pétitionnaire) n'y supplée pas. Après une mise en demeure restée sans effet, les faits exposés sont admis sauf pièce contraire (CE, 30 décembre 2009, n° 314972). Le rejet ne reste probable que devant un obstacle que le juge relève lui-même : irrecevabilité, moyen inopérant (refus d'abroger un acte non réglementaire sans changement de circonstances, CRPA, art. L. 243-2 ; compétence liée, CE, Sect., 3 février 1999, Montaignac, n° 149722), cause juridique nouvelle invoquée après le délai de recours (CE, 31 mars 2017, n° 399123), moyen dépourvu de toute précision.",
      "marqueurs": [
        "(?:communiqu|transmis)[ée]e?s? (?:au|à la|à l['’]|aux) (?:préfet|préfète|ministre|maire|directeur|directrice|président|présidente|recteur|rectrice|commune|département|région|agence|caisse|centre hospitalier|ehpad|office|inspect\\w*|garde des sceaux|administration|établissement|université|conseil|chambre|ville|communauté|métropole|[ée]tat)[^.]{0,220}?n['’]a (?:pas produit|produit aucun)",
        "réputée? avoir acquiescé",
        "mise? en demeure de produire"
      ],
      "exige": null,
      "origine": "analyse ANNT du 23 novembre 2026 : 40 sondes v50 et 300 sondes ANNT du banc, textes lus",
      "echantillon_v50": {
        "annulations_manquees_corrigibles": ["GENP-ANNT-2000736", "GENP-ANNT-2000740", "GENP-ANNT-2000732"],
        "rejets_a_risque": [],
        "annulations_reussies_concernees": [],
        "remarque": "trois affaires jumelles, un seul cas indépendant ; l'ancienne ligne était déjà remise dans deux de ces sessions sans changer la réponse, l'effet de la nouvelle rédaction reste à mesurer au banc"
      },
      "corpus_300": {
        "declenchee": 48,
        "annulations": 46,
        "rejets": 2,
        "hors_series": "16 annulations dans une série d'autorisations de licenciement jumelles, 15 dans une série de refus implicites de titre de séjour ; hors de ces séries, 15 annulations et 2 rejets",
        "rejets_expliques": {
          "GENP-ANNT-2200135": "moyen de motivation invoqué après le délai, cause juridique nouvelle irrecevable ; moyens de fond écartés",
          "GENP-ANNT-2202586": "refus d'abroger un refus sans circonstance nouvelle : moyens inopérants (CRPA, art. L. 243-2)"
        },
        "echecs_anterieurs_couverts": ["GENP-ANNT-2326684", "GENP-ANNT-2406099", "GENP-ANNT-2427751", "GENP-ANNT-2428202"]
      },
      "sources_lues": [
        "CJA, art. R. 612-3 et R. 612-6, versions en vigueur, LibreJustice",
        "CE, 26 juin 2023, n° 467714, texte intégral",
        "CE, 26 novembre 2012, Cordière, n° 354108, Recueil, texte intégral",
        "CE, 12 février 2003, n° 218983, tables, texte intégral",
        "CE, 30 décembre 2009, n° 314972, tables, texte intégral",
        "CE, Sect., 3 février 1999, Montaignac, n° 149722, Recueil, texte intégral",
        "CRPA, art. L. 243-2, version en vigueur",
        "CE, 31 mars 2017, n° 399123, analyse seule"
      ]
    }
  ],
  "corrections_existantes": [
    {
      "element": "ligne « Administration sans défense » de bien_fonde.ce_qui_la_remplit",
      "action": "remplacer par ANNT-R1",
      "motif": "Sa première proposition (« après une mise en demeure... ») a été lue comme la condition de toute portée de l'absence de défense : réponse finale de GENP-ANNT-2000740, « le dossier ne mentionne aucune mise en demeure. Elle n'est donc pas réputée acquiescer aux faits ». Ses marqueurs ignorent l'apostrophe typographique (n’a) et « mise en demeure » se déclenche sur les mises en demeure de police : 44 annulations et 6 rejets contre 46 et 2 pour ANNT-R1."
    },
    {
      "element": "fiche, section 2, paragraphe « Preuve »",
      "action": "remplacer par : « Preuve. Le juge de l'excès de pouvoir forme sa conviction au vu des éléments versés par les parties ; il peut écarter des allégations insuffisamment étayées, mais il ne peut exiger du requérant la preuve des faits qu'il avance et, devant des allégations sérieuses que la défense ne dément pas, il use de ses pouvoirs d'instruction, notamment en exigeant de l'administration la production des documents utiles (CE, 26 novembre 2012, Cordière, n° 354108, Recueil, texte intégral lu). »",
      "motif": "La règle actuellement citée (charge de la preuve sur chaque partie, CE, 6 octobre 2008, n° 283014) vient d'un litige fiscal de plein contentieux ; en excès de pouvoir, elle conforte le raisonnement « sans pièce, le requérant n'a pas prouvé » qui figure dans 10 des 12 annulations manquées."
    },
    {
      "element": "taux publiés remis par contrat_compact (section 10 de la fiche)",
      "action": "ne plus remettre les deux puces actuelles ; remettre à leur place la phrase « aucun taux d'annulation des recours pour excès de pouvoir devant les tribunaux administratifs n'est publié »",
      "motif": "Le filtre de hook.py retient la puce des tribunaux pour son « taux de couverture de 84,6 % », qui mesure le rapport entre affaires jugées et enregistrées, et la puce du Conseil d'État en premier ressort (13,1 % de satisfaction, 73,1 % de rejets), autre juridiction et autre contentieux. Effet mesuré faible : le contrat arrive après la première réponse et une seule réponse finale sur 40 cite un taux."
    }
  ],
  "elements_conserves": [
    "formule du hook Stop : sur ANNT, la relecture a fait passer deux réponses de non à oui (GENP-ANNT-2215631, GENP-ANNT-2300945) et aucune dans l'autre sens",
    "ligne de substitution de motifs : la pratique observée lui donne raison (11 annulations, 13 rejets quand la défense demande une substitution)"
  ]
}
```

# Biais ANNT de la version v50 : annulations sous-estimées

Analyse du 23 novembre 2026. Échantillon jugé : 40 sondes ANNT de `index_v50.json` (20 annulations au moins partielles, 20 rejets). Contrôle élargi : les 300 sondes ANNT du banc (`validation/banc/sondes`, dossiers dans `validation/banc/fixtures`), 150 annulations et 150 rejets, dont les 40 de l'échantillon. Les 40 jugements ont été lus sur LibreJustice dans leurs motifs décisifs, ainsi que deux autres du corpus (n° 2200135 et 2202586). Aucune session de l'agent n'a été relancée : l'effet des propositions sur ses réponses n'est pas mesuré.

## 1. Résultat

Sur les 12 annulations manquées, une seule configuration visible dans le dossier remis distingue réellement l'issue : l'autorité auteur de la décision n'a produit aucune défense. Elle couvre 3 des 12 échecs (une série de trois affaires jumelles) et, sur les 300 sondes, elle accompagne 46 annulations pour 2 rejets, ces deux rejets tenant à un obstacle de droit que le juge relève lui-même. La règle ANNT-R1 en tire la conséquence.

Pour les 9 autres échecs, rien dans le dossier remis ne les sépare des rejets. Le juge a annulé sur le contenu de pièces que l'agent ne voit pas : le texte de la décision attaquée, un contrat de travail, une attestation, le règlement d'un PLUi. Les signes de procédure qu'on pouvait soupçonner se répartissent à parts presque égales dans le corpus (section 4). Une consigne générale d'optimisme gagnerait autant d'annulations qu'elle coûterait de rejets, et davantage de rejets sur une distribution réelle, où l'annulation reste minoritaire.

## 2. Ce qui distinguait l'issue, sonde par sonde

Colonnes : réponse de v50 (première réponse puis réponse finale quand elles diffèrent), motif décisif du jugement, élément visible dans le dossier remis.

### Annulations manquées (12)

| Sonde | v50 | Motif décisif du jugement | Élément visible |
| --- | --- | --- | --- |
| 2000736, 2000740, 2000732 | non 85, 70, 70 | Autorisation de licencier un salarié protégé insuffisamment motivée sur le reclassement (C. trav., art. R. 2421-5) | La DREETS, auteur de l'acte, « n'a pas produit de mémoire en défense » ; seuls les liquidateurs défendent. Couvert par R1 |
| 2004278 | non 55 | Refus du maire fondé sur un simple vœu du conseil municipal, sans portée juridique ; substitution de base légale refusée, le maire n'ayant pas entendu refuser pour ce motif | Substitution demandée « à supposer » l'acte illégal ; non discriminant (section 4) |
| 2203661 | non 65 | Fin de fonctions de chef de service : l'agent avisé d'une décision déjà prise, privé de la garantie de l'article 65 de la loi de 1905 | Défense d'une phrase, déposée 19 mois après la requête ; non discriminant |
| 2209372 | non 85 | Défaut d'examen : le préfet retient une promesse d'embauche alors qu'un CDI et des bulletins de salaire étaient produits | Aucun |
| 2212112 | non 55 | Visa étudiant : erreur d'appréciation « que reconnaît implicitement le ministre » ; substitution (projet non sérieux) refusée | Substitution demandée ; non discriminant |
| 2207180 | non 70 | Révocation disproportionnée : manquement à la probité non caractérisé, autres faits sans antécédent disciplinaire | Aucun ; défense d'une phrase |
| 2214890 | non 60 | Visa salarié : motif consulaire erroné, substitution refusée au vu de l'expérience prouvée | Aucun ; la substitution n'apparaît pas au dossier remis |
| 2215577 | non 55 | Visa étudiant : ressources établies « ainsi que le reconnaît le ministre », substitution refusée | Substitution demandée ; non discriminant |
| 2103775 | non 70 | Annulation partielle (C. urb., art. L. 600-5) : le certificat d'urbanisme ne cristallisait pas le PLU, le lot B méconnaît le cœur d'îlot du PLUi | Aucun |
| 2204230 | non 75 | Refus de prolongation d'activité : situation appréciée à la mauvaise date, erreur d'appréciation sur le temps partiel thérapeutique | Aucun ; défense d'une phrase |

### Annulations bien prédites (8)

| Sonde | v50 | Motif décisif | Élément visible |
| --- | --- | --- | --- |
| 2302770 | oui 88 | Retrait d'un titre en cours de validité sans texte, moyen relevé d'office | Information R. 611-7 sur un moyen favorable au requérant |
| 2005586 | oui 60 | Incompétence du signataire, relevée d'office | Information R. 611-7 |
| 2205292 | oui 88 | Refus d'aide annulé, injonction de verser | Information R. 611-7-3 sur une injonction d'office |
| 2002615 | oui 70 | Le ministre, « qui n'a produit aucun mémoire en défense avant la clôture », ne justifie pas des faits | Défenses enregistrées après la clôture |
| 2003334 | oui 55 | Refus de lever une interdiction d'armes insuffisamment motivé en fait et en droit | Moyen de motivation ; défense limitée à l'opérance contre le recours gracieux |
| 2100235 | oui 65 | Retrait de permis au motif inexact, substitution refusée | Substitution discutée par les requérants |
| 2215631 | non 60 puis oui 55 | Visa étudiant, erreur manifeste, substitution refusée | Aucun |
| 2300945 | non 60 puis oui 55 | Visa, erreur d'appréciation, substitution refusée | Substitution demandée |

### Rejets (20, dont 2 manqués)

Les 18 rejets bien prédits tiennent à des motifs de fond ou de droit que la défense ou le juge opposent : large pouvoir d'appréciation (naturalisation, 2004143 ; ajournement avec neutralisation du motif illégal, 2102855), faits établis par témoignages concordants (2104901), erreurs de fait non démontrées (2115527, 2201345), refus d'abroger sans changement (2004995, 2102805, 2203565), moyens de légalité externe soulevés après le délai (2101095, 2206750), substitution de motif accueillie (2201510, où le tribunal relève pourtant une erreur de droit ; 2217110, où la requérante n'a pas contesté la fausse attestation invoquée), appréciations de l'administration confirmées (2400913, 2109516, 2206286, 2204172), procédure disciplinaire régulière et moyen d'incompétence inopérant (2101128), sanction proportionnée à des faits graves (2211150).

Les deux rejets manqués :
- 2308349 (oui 60) : la commission de recours retient l'inadéquation entre l'expérience et l'emploi ; le moyen dirigé contre la décision consulaire est inopérant. L'agent a lu la défense déposée après la clôture et non communiquée comme une absence de défense. Dans le corpus, l'auteur dont le seul mémoire arrive après la clôture perd 5 fois sur 7 : le signe penche vers l'annulation, trop peu nettement pour une règle.
- 2203549 (oui 55) : la condition objective de formation annuelle n'était pas remplie, et la défense invoquait la compétence liée. Trois sondes du corpus seulement voient la compétence liée opposée en défense ou relevée d'office (2 rejets, 1 annulation) : pas de règle.

## 3. L'erreur de raisonnement récurrente

**Le silence de l'autorité lu comme neutre.** Dans la série des autorisations de licenciement, l'agent écrit (2000740) que l'administration « n'est donc pas réputée acquiescer aux faits » faute de mise en demeure, puis que les liquidateurs « défendent la décision ». Les deux propositions sont exactes, la conclusion ne l'est pas. Sans mise en demeure, l'article R. 612-6 ne joue pas (CE, 26 juin 2023, n° 467714), mais le juge de l'excès de pouvoir ne peut exiger du requérant la preuve de ce qu'il avance (CE, 26 novembre 2012, Cordière, n° 354108), et une administration qui ne donne pas les motifs de sa décision laisse tenir pour établies les allégations sérieuses du requérant (CE, 12 février 2003, n° 218983). Le liquidateur ne peut pas expliquer ce que l'inspectrice a examiné. Les tribunaux en tirent la conséquence : 46 annulations sur 48 sondes du corpus où l'auteur n'a pas défendu. C'est l'erreur que corrige R1, et la seule qui soit à la fois récurrente et discriminante.

**La preuve exigée du requérant.** Dans 10 des 12 annulations manquées, la réponse s'appuie sur une pièce absente : « sans pièce établissant une pression ou un délai trop court » (2203661), « si le requérant ne prouve pas l'existence d'une autre société contrôlée » (2000740), « le dossier ne contient pas les pièces qui le trancheraient » (2212112). Le dossier remis ne reproduit aucune pièce, d'aucune partie : leur absence ne renseigne pas sur l'issue, et la charge de la preuve ainsi posée contredit l'arrêt Cordière. Ce raisonnement figure pourtant aussi dans 16 des 18 rejets bien prédits. Il est la manière ordinaire de l'agent de conclure quand le dossier se tait, et le corriger seul déplacerait autant de rejets que d'annulations. La correction utile porte sur la fiche (section 2), qui l'appuie aujourd'hui sur une règle de preuve tirée du contentieux fiscal.

**Des tendances prêtées au juge.** « Une substitution que le juge accepte souvent » (2212112), « le juge confirme en général la révocation dès que les faits sont prouvés » (2207180), « le standard de motivation est peu exigeant » (2000740), « l'erreur manifeste aboutit rarement » (2203661). Confrontées au corpus, certaines sont justes en moyenne : la substitution demandée en défense se solde par 11 annulations et 13 rejets, les sanctions disciplinaires par 10 et 10. Sur des dossiers muets, elles ne font pas pire que le hasard. La troisième est démentie dans l'espèce, faute pour l'agent d'avoir vu que l'auteur ne défendait pas sa motivation.

**Ni les taux ni la relance du hook.** Une seule réponse finale sur 40 cite un taux, et le contrat n'arrive qu'après la première réponse. La relecture imposée par le hook Stop a corrigé deux réponses (2215631, 2300945) sans en abîmer aucune. Le pessimisme vient de la première réponse, avant tout contrat.

## 4. Pistes contrôlées et écartées

Comptes sur les 300 sondes ANNT (150 annulations, 150 rejets), relevés par expressions régulières sur le dossier remis puis vérifiés à la main pour les signes retenus.

| Signe visible | Annulations | Rejets | Conclusion |
| --- | --- | --- | --- |
| Auteur de l'acte sans aucun mémoire (marqueurs de R1) | 46 | 2 | Règle R1 |
| Ancienne ligne « Administration sans défense » (ses marqueurs) | 44 | 6 | À remplacer |
| Défense d'une phrase (« les moyens ne sont pas fondés ») | 28 | 27 | Sans valeur |
| Substitution de motifs ou de base légale demandée en défense | 11 | 13 | Sans valeur ; la réplique du requérant ne départage pas davantage |
| Seul mémoire de l'auteur arrivé après la clôture, non communiqué | 5 | 2 | Trop mince |
| Mémoire quelconque (y compris du requérant) après la clôture | 5 | 9 | Penche vers le rejet ; l'agent n'en tire rien à tort |
| Délai de la défense supérieur à un an | 26 | 34 | Sans valeur |
| Moyen relevé d'office favorable au requérant (incompétence, champ d'application) | 3 | 1 | Déjà bien lu par l'agent |
| Moyen relevé d'office d'irrecevabilité ou d'inopérance | 1 | 9 | Déjà bien lu |
| Fin de non-recevoir opposée en défense | 17 | 60 | Penche vers le rejet ; déjà bien lu |
| Décision implicite et moyen de motivation (ligne L. 232-4) | 38 | 28 | Faible ; ligne conservée, sans gain attendu |
| Compétence liée opposée en défense ou relevée d'office | 1 | 2 | Trop mince |

Les signes que l'analyse par n-grammes fait ressortir ensuite désignent une autorité ou une matière (une préfecture, la naturalisation). Ils décrivent des séries, et la règle R1 en capte déjà la part juridique (l'absence de défense) ; aucun n'a été retenu.

## 5. La règle ANNT-R1

**Texte, condition, tableau, marqueurs** : bloc JSON en tête. Elle remplace la ligne « Administration sans défense » et doit être le premier élément de `bien_fonde.ce_qui_la_remplit`, car `contrat_compact` ne remet que quatre lignes « ce qui la remplit » toutes conditions confondues et les lignes propres au séjour la précèdent aujourd'hui. Pas de garde `exige` : le marqueur principal exige déjà que la requête ait été communiquée à une autorité publique et que celle-ci n'ait rien produit ; il ne se déclenche pas quand c'est un particulier mis en cause qui se tait (2103710).

**Échantillon v50.**
- Corrigibles : 2000736, 2000740, 2000732, soit 3 des 12 annulations manquées (8/20 pourrait passer à 11/20). Un seul cas indépendant.
- À risque : aucun des 20 rejets ne déclenche la règle ; aucune des 8 annulations réussies non plus.
- Réserve : l'ancienne ligne a été remise dans au moins deux de ces trois sessions sans changer la réponse. Le gain dépend de la nouvelle rédaction, qui place la conséquence en tête et répond aux deux objections que l'agent a opposées (pas de mise en demeure, défense du bénéficiaire). Il reste à mesurer au banc.

**Corpus de 300.** 48 déclenchements : 46 annulations, 2 rejets. Les annulations comprennent deux séries de jugements semblables (16 autorisations de licenciement, 15 refus implicites de titre de séjour) ; hors séries, 15 annulations et 2 rejets. Les deux rejets relèvent des réserves du texte : moyen de motivation soulevé après le délai, donc cause juridique nouvelle irrecevable (2200135), et refus d'abroger sans circonstance nouvelle, moyens inopérants (2202586). Quatre échecs du classement antérieur (2326684, 2406099, 2427751, 2428202) déclenchent la règle ; l'ancienne ligne manquait les dossiers écrits avec l'apostrophe typographique.

**Ce que la règle ne dit pas.** Elle ne fait pas de l'absence de défense un acquiescement : elle rappelle que l'acquiescement suppose la mise en demeure et en distingue les effets. Elle ne vise ni l'identité d'une juridiction ni celle d'un magistrat, seulement la conduite procédurale d'une partie, visible dans les visas.

## 6. Éléments existants à retirer ou corriger

- **Ligne « Administration sans défense »** : à remplacer par R1 (motifs dans le bloc JSON). Son ordre (« après une mise en demeure... ; sans mise en demeure, le juge statue sur les pièces produites ») a été lu comme une neutralisation, et son marqueur « mise en demeure » se déclenche sur les mises en demeure de police administrative.
- **Fiche, section 2, « Preuve »** : la règle de la charge de la preuve tirée de CE, 6 octobre 2008, n° 283014 (vérifié : litige fiscal de plein contentieux, déductibilité de charges) n'est pas la règle de l'excès de pouvoir. Texte de remplacement dans le bloc JSON, fondé sur l'arrêt Cordière. Cette section n'atteint l'agent que s'il lit la fiche, ce qui n'est pas arrivé dans ces 40 sessions : correction d'exactitude, sans gain mesurable attendu ici.
- **Taux publiés** : les deux puces remises ne mesurent pas le succès d'un recours pour excès de pouvoir devant un tribunal administratif (taux de couverture d'un côté, Conseil d'État en premier ressort de l'autre). À retirer du contrat, au profit de la mention qu'aucun taux n'est publié. Effet attendu faible.
- **Formule du hook Stop** (« l'absence d'une cause d'échec ne vaut pas succès ») : aucun effet vers le non observé sur cette famille. À garder.
- **Remarque de structure, sans action proposée** : `contrat_compact` ne remet les lignes « ce qui la fait tomber » que pour les deux premières conditions (délai, décision faisant grief). Les dix causes d'échec de `bien_fonde` n'atteignent donc jamais l'agent ; elles ne sont pour rien dans le biais mesuré ici.

## 7. Limites

- L'échantillon de 40 fait partie du corpus de 300 : les comptes du corpus ne sont pas une validation indépendante de l'échantillon, seulement un contrôle plus large du signe.
- Corpus et échantillon sont équilibrés à 50 %. Dans un contentieux où l'annulation est minoritaire, la proportion d'annulations parmi les affaires sans défense serait plus basse, et le choix de l'agent de répondre non quand le dossier se tait y redeviendrait souvent le bon.
- Les comptes du tableau de la section 4 reposent sur des expressions régulières ; seuls ceux de R1, de la substitution et de la défense tardive ont été relus cas par cas.

## 8. Sources lues

- CJA, art. R. 612-3, R. 612-6 et R. 613-3, versions en vigueur (LibreJustice).
- CRPA, art. L. 243-2, version en vigueur.
- CE, Sect., 6 février 2004, Hallal, n° 240560, Recueil, texte intégral (substitution de motifs ; refusée au vu du mémoire en réplique).
- CE, 26 novembre 2012, Cordière, n° 354108, Recueil, texte intégral.
- CE, 12 février 2003, n° 218983, tables, texte intégral.
- CE, 30 décembre 2009, n° 314972, tables, texte intégral.
- CE, 26 juin 2023, n° 467714, texte intégral.
- CE, Sect., 3 février 1999, Montaignac, n° 149722, Recueil, texte intégral.
- CE, 6 octobre 2008, n° 283014, tables, texte intégral.
- CE, 31 mars 2017, n° 399123, analyse seule.
- Les 40 jugements de l'échantillon (motifs décisifs et dispositif) et les jugements n° 2200135 (TA Nice, 12 juillet 2023) et n° 2202586 (TA Châlons-en-Champagne, 14 mars 2023).
- Réponses finales et premières réponses de v50 (`index_v50.json`, `echecs_ech/*/reponse_agent.md`), contrats remis relevés dans les `_brut.jsonl` des sessions, `classement.json` de l'analyse antérieure.
