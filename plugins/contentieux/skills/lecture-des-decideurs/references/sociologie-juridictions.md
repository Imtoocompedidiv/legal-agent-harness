# Juridictions françaises et européennes : sociologie, standards de contrôle et règles d'action

Note de recherche du 18 novembre 2026, destinée au plugin `contentieux`. Elle complète `docs/recherche/02_juge_recit_procedure.md` (désigné « 02 » ci-dessous) sans reprendre ce que 02 établit correctement. Chaque résultat donne sa source, ce qui en a été lu, ce qu'il établit, sa solidité, puis la règle qu'un acte contentieux peut en tirer, ou la raison pour laquelle on ne peut rien en tirer.

## Conventions

Statut de lecture : « lu en entier » ; « extraits lus » (avec les passages) ; « résumé lu » (résumé d'auteur, analyse officielle d'une décision ou compte rendu) ; « outil de synthèse » (page lue à travers un outil qui la résume ; chiffres non recoupés sur le texte brut) ; « non vérifié ». Les décisions dont seule l'analyse officielle (sommaire Légifrance repris par LibreJustice) a été lue sont marquées « analyse officielle lue ». Les résumés générés par LibreJustice n'ont jamais servi de source.

Statut des résultats : droit positif ; pratique institutionnelle ; statistique officielle ; empirique solide ; empirique limité ; théorique ; inférence ; contesté.

Limite de méthode. Les textes intégraux de Cairn, Lextenso et OpenEdition sont protégés par des dispositifs anti-robots (DataDome, Cloudflare, Anubis). Aucun de ces dispositifs n'a été contourné. Les textes déposés sur HAL ont été obtenus par l'API de HAL quand le site les bloquait. Aucun magistrat n'est nommé ni profilé dans cette note ; les noms de juges présents dans les décisions lues ne sont pas repris.

Provenance et contrôle. La lecture a été confiée à un lecteur délégué. La session qui a intégré cette note a relu directement sur LibreJustice l'article L. 10 du code de justice administrative (version en vigueur depuis le 25 mars 2019, quatrième alinéa : texte conforme à celui cité en section 4) et la décision CE, 10 octobre 2025, n° 493118 (deux motifs, contrôle entier sur l'ordre public, contrôle restreint sur l'article L. 435-3, rejet parce que le préfet aurait pris la même décision : conforme à la section 3.2), ainsi que l'article R. 612-5-2 du même code (section 2.5, ajoutée). Aucun écart n'a été constaté.

## Les trois résultats qui changent le plus la pratique

1. **Le profilage des juges est un délit, et la loi vise expressément la stratégie de choix de juridiction.** L'article L. 10 du CJA et l'article L. 111-13 du COJ interdisent toute réutilisation des données d'identité des magistrats ayant pour objet ou pour effet d'évaluer, d'analyser, de comparer ou de prédire leurs pratiques, sous les peines de l'article 226-18 du code pénal (cinq ans et 300 000 euros). Le Conseil constitutionnel a précisé que le législateur entendait éviter « des pressions ou des stratégies de choix de juridiction ». Un outil qui extrait le nom du juge et calcule son taux de rejet tombe dans l'interdiction. Le harness doit raisonner sur des distributions anonymes (la dispersion entre juges existe et a été mesurée sans nommer personne : environ deux mois de salaire d'écart entre les déciles extrêmes des présidents de chambres sociales, section 5.7).
2. **Le standard de contrôle décide de la preuve utile et des moyens opérants avant tout travail de rédaction.** Devant un jury, la seule preuve utile porte sur des faits extérieurs à la valeur des prestations ; en admission exceptionnelle au séjour, il faut attaquer chaque motif, car le motif soumis à un contrôle restreint suffit à maintenir la décision ; en discipline, le contrôle entier n'existe que si le moyen est soulevé, et la comparaison avec d'autres agents est inopérante (section 3).
3. **Des démarches dont l'effet a été mesuré restent très peu pratiquées.** Devant la Cour de cassation, les observations de l'avocat aux Conseils sur un dossier orienté en non-admission sont associées à 18 % de réorientations contre moins de 7 % sans observations, mais elles n'ont été produites que dans 6,2 % de ces dossiers de 2004 à 2012 (section 6). Devant le tribunal correctionnel, l'absence du prévenu à l'audience et l'absence de garanties de représentation pèsent plus que la plupart des variables sociales (section 5.1). Le rejet abusif d'un référé par ordonnance de tri est un moyen de cassation (section 2.3).

---

## 1. Juge administratif et culture du Conseil d'État

### 1.1 Latour (2002), *La fabrique du droit*, chapitre 5, version anglaise revue par l'auteur

Référence. Bruno Latour, *La fabrique du droit. Une ethnographie du Conseil d'État*, La Découverte, 2002. Chapitre 5 traduit par Alain Pottage et revu par l'auteur : « Scientific Objects and Legal Objectivity », paru dans A. Pottage et M. Mundy (dir.), *Law, Anthropology, and the Constitution of the Social*, Cambridge University Press, 2004. Texte : https://www.bruno-latour.fr/sites/default/files/88-SCIENCE-LAW-GB.pdf (page https://www.bruno-latour.fr/node/213.html).

Lecture. Extraits lus sur le texte brut (environ 117 000 caractères) : passages sur le réviseur, sur les « faits », sur le commissaire du gouvernement, sur le doute et la clôture, notes 14 à 21. Le livre complet n'a pas été lu.

Ce que la source établit. Observation ethnographique de la section du contentieux, antérieure à la publication de 2002 et donc aux réformes de 2006 et 2009 (les dates exactes du terrain ne figurent pas dans les passages lus) :
- Les faits d'un dossier forment « un ensemble clos », vite rendu incontestable par l'accumulation des pièces, dont les juges cherchent à se débarrasser pour passer au point de droit ; on n'y revient plus.
- À chaque étage, la part des faits recule : le requérant parle surtout des faits, l'avocat un peu moins, le rapporteur moins encore, le réviseur déplace l'affaire vers les questions de droit. Une fois jugée, l'affaire se résume en une phrase : la fiche que le texte anglais appelle « green slip » ne garde que la question de droit.
- Le commissaire du gouvernement, silencieux en séance d'instruction, sert à faire douter la formation et à empêcher un consensus acquis trop vite ; Latour compte environ 20 commissaires pour 200 conseillers (note 19).

Solidité. Empirique limité : une ethnographie d'une seule institution, ancienne, centrée sur le Conseil d'État statuant en premier ressort et en cassation. Les mécanismes décrits (réduction des faits, sélection d'une question de droit) restent cohérents avec la procédure actuelle d'admission des pourvois.

Règle opérationnelle. Devant le Conseil d'État, et plus encore en cassation, la requête ou le pourvoi doit stabiliser les faits dès le premier mémoire, pièces numérotées à l'appui, puis formuler l'affaire comme une question de droit qui tient en une phrase. Les faits non fixés au dossier à ce moment ne seront pas rouverts par les étages suivants. Statut de la règle : inférence appuyée sur une observation empirique limitée.

### 1.2 Pougnet (2026), rapporteurs publics et déchéance de nationalité

Référence. Rachel Pougnet, « Récits de la construction d'une machine jurisprudentielle : les conclusions des rapporteurs publics dans le contentieux de la déchéance de nationalité », *La Revue des droits de l'homme*, n° 29, mis en ligne le 17 février 2026. DOI 10.4000/15qfp ; https://journals.openedition.org/revdh/25441.

Lecture. Outil de synthèse : la page est protégée par un défi anti-robot (Anubis), non contourné ; le contenu a été obtenu par un outil qui résume et refuse les citations longues. Métadonnées et méthode recoupées sur deux lectures.

Ce que la source établit. Analyse qualitative des décisions du Conseil d'État et quatre entretiens semi-directifs menés en septembre et octobre 2025 avec des rapporteurs publics ayant conclu en matière de déchéance (entretiens de 45 minutes à 1 h 20, note 14). L'article ne donne aucune fréquence de suivi des conclusions. Il décrit : l'accord entre le rapporteur public et la chambre d'instruction perçu comme positif parce qu'il donne une issue « quasi certaine » au délibéré ; des conclusions contraires à la chambre évitées autant que possible, tous les interrogés ayant pourtant conclu à contre-courant plusieurs fois ; une influence exercée surtout en amont, dans les échanges avec la chambre et son président ; la « Troïka » (président de la section et présidents adjoints) qui peut faire rejuger ou renvoyer une affaire. Données de contexte : deux rapporteurs publics par chambre et dix chambres (note 17) ; le Conseil d'État n'a jamais annulé un décret de déchéance (§ 1).

Solidité. Empirique limité (quatre entretiens, un seul contentieux, une seule juridiction).

Règle opérationnelle. Au Conseil d'État, le sens des conclusions reflète le plus souvent une position déjà discutée avec la chambre ; une note en délibéré qui ne fait que contester le raisonnement du rapporteur public a peu de chances de déplacer la formation. Elle doit apporter ce que la séance d'instruction n'a pas pu voir : une pièce, une décision, une conséquence non examinée. Statut : inférence ; aucune transposition aux tribunaux administratifs n'est permise par cette source.

### 1.3 Cohen et Pasquino (2013), motivation et organisation interne des cours souveraines

Référence. Mathilde Cohen, Pasquale Pasquino, *La motivation des décisions de justice, entre épistémologie sociale et théorie du droit. Le cas des Cours souveraines et des Cours constitutionnelles*, rapport final pour la Mission de recherche Droit et Justice, avril 2013 (rapport n° 09.38), 164 p. https://hal.science/hal-05216566.

Lecture. Extraits lus : méthodologie (p. 12-14), double contrôle de qualité et rôle du rapporteur public et de l'avocat général (p. 54-58), filtrage et aiguillage des dossiers (p. 105-107).

Ce que la source établit. Dix-sept entretiens semi-directifs et des journées d'observation au Conseil d'État et à la CEDH (2010-2011).
- Au Conseil d'État, le rapporteur public assiste à la séance d'instruction, entend le rapporteur, le réviseur et la discussion, peut y poser des questions sans voter, puis rédige ses conclusions après l'adoption d'un projet par la sous-section. Un maître des requêtes décrit une « chaîne de contrôle qualité » à trois étages.
- À la Cour de cassation, l'avocat général se borne dans la majorité des affaires simples à exprimer son accord avec le rapporteur ; il intervient surtout par écrit ; son avis peut discuter les conséquences économiques ou sociales d'une solution, ce que l'arrêt ne fait pas.
- À la Cour de cassation, le conseiller rapporteur rédige un rapport même pour une non-admission, remis au président de chambre, au doyen, au parquet général et aux parties ; au Conseil d'État, les présidents de sous-section trient à l'entrée et aiguillent vers ordonnance, refus d'admission ou formation de jugement.

Solidité. Empirique limité (entretiens, représentations des acteurs).

Règle opérationnelle. Devant la Cour de cassation, les conséquences pratiques d'une solution (économiques, sociales, de sécurité juridique) se plaident d'abord à l'adresse de l'avocat général, qui peut les discuter, et se traduisent dans le mémoire par un moyen de droit que l'arrêt pourra reprendre. Devant le Conseil d'État, le moment utile pour influer est l'écriture, avant la séance d'instruction : la formation et le rapporteur public y forment leur position. Statut : inférence.

### 1.4 Le rapporteur public : textes et discours institutionnels relus

- Jean-Marc Sauvé, « Le rapporteur public dans la juridiction administrative », discours du 28 juin 2016, https://www.conseil-etat.fr/publications-colloques/discours-et-interventions/le-rapporteur-public-dans-la-juridiction-administrative. Lu en entier sur le texte brut. Aucun chiffre de suivi des conclusions. Il rappelle la fonction (« exposer les questions », « son opinion sur les solutions »), le décret du 1er août 2006 (le rapporteur public n'assiste plus au délibéré dans les tribunaux et cours ; les parties peuvent le demander au Conseil d'État), la parole donnée aux parties après les conclusions depuis le décret du 7 janvier 2009, CEDH, *Marc-Antoine c. France*, 4 juin 2013, n° 59484/09. Statut : pratique institutionnelle.
- CE, Sect., 21 juin 2013, *Communauté d'agglomération du pays de Martigues*, n° 352427, https://librejustice.fr/decision/WvfzqJhoQvXc. Analyse officielle lue : les conclusions n'ont pas à être communiquées avant l'audience ; la communication du sens sert à décider d'assister à l'audience, à préparer les observations orales et une note en délibéré. Statut : droit positif.
- CE, Sect., 21 décembre 2018, *Société Eden*, n° 409678, https://librejustice.fr/decision/bMtH-BamLfaN. Lu en entier. Le point 2 cité par 02 est exact. Le point 3 ajoute une règle que 02 ne relève pas : les conclusions à fin d'injonction ne sont pas accessoires, mais le sens communiqué ne doit indiquer explicitement le sort proposé que si le rapporteur public propose de faire droit, au moins partiellement, aux conclusions principales ; un sens « rejet au fond » couvre l'injonction. Statut : droit positif.

Règle opérationnelle. Quand le sens communiqué est « rejet » et que la requête comportait une injonction, le harness ne tire aucun grief de l'absence de mention de l'injonction. Quand le sens propose une satisfaction partielle sans dire ce qu'il advient de l'injonction, l'irrégularité est un moyen d'appel ou de cassation.

### 1.5 Existe-t-il une mesure publique du suivi du rapporteur public ?

Recherches menées : rapport public 2025 du Conseil d'État (texte brut, recherche plein texte), discours de 2016, Pougnet 2026, theses.fr (49 thèses sur le rapporteur public ou le commissaire du gouvernement, dont Guillaume Leroy, *La pratique du précédent en droit français*, Aix-Marseille, 2021, résumé lu : étude de plus de 360 conclusions et avis, sans mesure du suivi), HAL, OpenAlex, deux moteurs de recherche en français et en anglais.

Résultat. Aucune mesure publique de la fréquence à laquelle les formations suivent leur rapporteur public n'a été trouvée. Les affirmations rencontrées (« suivi dans la quasi-totalité des cas ») viennent de blogs d'avocats ou de propos de praticiens, sans chiffre ni méthode. Statut : constat de recherche, conforme à 02 (C.19).

Règle opérationnelle. Le harness ne prête aucun taux de suivi au rapporteur public et ne présente aucun chiffre de ce type au client. Il raisonne sur le sens communiqué comme sur la meilleure information disponible, sans probabilité chiffrée.

### 1.6 Contamin, Saada, Spire, Weidenfeld (2007) et l'annexe de 2010 sur le tribunal administratif de Paris

Références.
- Jean-Gabriel Contamin, Emmanuelle Saada, Alexis Spire, Katia Weidenfeld, *Le recours à la justice administrative. Pratiques des usagers et usages des institutions*, rapport pour la Mission de recherche Droit et Justice, novembre 2007 (publié par La Documentation française en 2008). Rapport complet avec annexe : https://ierdj.fra1.digitaloceanspaces.com/media_library/2024/08/08.09.pdf ; synthèse : https://ierdj.fra1.digitaloceanspaces.com/media_library/2023/03/04-15-NS.pdf.
- Annexe de février 2010 : Alexis Spire, Katia Weidenfeld et al., « Le tribunal administratif : une affaire d'initiés ? Enquêtes sur les usagers du tribunal administratif de Paris », incluse dans le rapport complet. L'article publié sous ce titre dans *Droit et Société*, n° 79, 2011, p. 689-713, n'a pas été lu (Cairn bloqué).

Lecture. Synthèse lue en entier. Rapport complet : extraits lus (méthodologie et résultats de l'annexe de 2010, p. 3-12 et 16-17 de l'annexe ; passages sur le logement p. 177 et 193 du rapport).

Ce que la source établit.
- Terrains : tribunaux administratifs de Cergy-Pontoise et de Lille ; contentieux des étrangers, fiscal et du logement ; ethnographies en préfecture et en centre des impôts ; questionnaire aux requérants présents aux audiences collégiales de Cergy, avec un biais d'échantillonnage reconnu par les auteurs.
- La saisine du juge dépend moins des qualités propres du requérant que de la rencontre d'« intermédiaires du droit » (associations, travailleurs sociaux, avocats), très inégalement répartis selon les matières : présents en droit des étrangers, quasi absents en matière fiscale.
- Les pratiques de l'administration font varier les flux : en préfecture, les agents observés suivent le nombre de mesures d'éloignement et ignorent le taux d'annulation ; en matière fiscale, le taux de recours au tribunal (requêtes rapportées aux réclamations rejetées) passe de 11,3 % en 2001 à 8,3 % en 2006 ; le conciliateur fiscal éteint environ un litige sur cinq (20,8 %) dans la série étudiée.
- Annexe de 2010 (tribunal administratif de Paris) : échantillon aléatoire de jugements rendus de 2003 à 2009 sur des requêtes de 2000 à 2002, 1 504 requérants en fonction publique et 704 en fiscal ; les rejets par ordonnance pour irrecevabilité manifeste et les désistements précoces échappent à l'échantillon. Le « succès » inclut la satisfaction obtenue en cours d'instance (retrait, dégrèvement). Taux de succès : 32 % en fonction publique, 37 % en fiscal. En fonction publique, 22 % obtiennent une annulation totale ; en fiscal, la décharge totale par le juge ne concerne que 9 % des requêtes, et l'administration accorde un dégrèvement en cours d'instance dans 17 % des requêtes. En fonction publique, 42 % de succès avec avocat contre 26 % sans ; 36 % pour les cadres, 24 % pour les professions intermédiaires, 23 % pour les employés, 7 % pour les ouvriers ; le requérant défendu par un avocat gagne 1,7 fois plus souvent. En fiscal, aucune relation significative (18 % de dégrèvements en cours d'instance avec avocat contre 16 % sans).
- Un requérant interrogé décrit le commissaire du gouvernement comme favorable aux requérants « quand ça ne gênera pas l'administration ». Il s'agit d'une perception de profane, rapportée comme telle par les auteurs ; elle ne mesure rien.

Solidité. Empirique limité : une juridiction, deux matières, cohorte ancienne, corrélations sous contrôle de quelques variables seulement ; l'effet de l'avocat mêle l'apport du conseil et la sélection des dossiers confiés à un avocat.

Règles opérationnelles.
- En fonction publique devant le tribunal administratif, le conseil donné au client sur l'intérêt d'être représenté s'appuie sur l'écart observé avec et sans avocat, présenté comme une association et non comme un effet garanti, et jamais converti en chance du dossier. Statut : empirique limité.
- En matière fiscale, la voie utile passe souvent par l'administration avant le juge : le harness prépare la réclamation et la saisine du conciliateur avec le même soin que la requête, et traite le dégrèvement en cours d'instance comme un résultat probable à négocier. Statut : empirique limité.
- Le harness ne simule pas un juge administratif soucieux de « ne pas gêner l'administration » : aucune des sources lues ne l'établit. Statut : constat de recherche.

### 1.7 Spire et Weidenfeld (2019), le capital procédural

Référence. Alexis Spire, Katia Weidenfeld, « Obtenir justice : une affaire de capital ? », *Délibérée*, 2019, https://hal.science/hal-02267006.

Lecture. Lu en entier (texte obtenu par l'API de HAL).

Ce que la source établit. Définition du « capital procédural » : capacité à transformer un litige en contentieux formulé en termes juridiques susceptibles de convaincre le juge, combinant capital économique (supporter le coût et la durée), culturel (produire les bons justificatifs, adopter la posture attendue) et social (choisir ses conseils). Les auteurs indiquent que l'étude statistique des requérants montre que le savoir juridique n'est ni nécessaire au dépôt d'un recours ni déterminant pour l'emporter. Chiffres repris de l'annuaire statistique de la justice : affaires nouvelles aux prud'hommes passées de 154 340 à 106 537 entre 2014 et 2017, avec une baisse plus faible pour les cadres (26 515 à 21 824) que pour les ouvriers (36 389 à 21 706) ou les employés (57 151 à 38 430). Face à un plaideur habituel comme l'administration, la gratuité et la dispense d'avocat ne suffisent pas à rétablir l'égalité.

Solidité. Théorique, appuyé sur des données citées. Les chiffres prud'homaux sont de seconde main.

Règle opérationnelle. Le harness évalue le capital procédural du client au moment de la prise en charge (capacité à produire des pièces, à tenir des délais, à supporter la durée) et compense ce qui manque par la préparation : inventaire des pièces, calendrier, rédaction des attestations. Statut : inférence.

### 1.8 Travaux de science politique sur le Conseil d'État, connus par leur résumé

- Danièle Lochak, « Le Conseil d'État en politique », *Pouvoirs*, n° 123, 2007, p. 19-32, DOI 10.3917/pouv.123.0019. Résumé lu : l'hypothèse que les choix politiques du Conseil d'État restent présents mais moins visibles lorsqu'ils ne s'écartent pas du consensus dominant. Statut : théorique.
- Olivia Bui-Xuan, « Le Conseil d'État : quelle composition réelle ? », *Pouvoirs*, n° 123, 2007, p. 89 et s., DOI 10.3917/pouv.123.0089. Résumé lu : profil des membres très homogène et largement prédéterminé. Statut : empirique limité.
- Esteban Renaud, « Les conclusions des rapporteurs publics comme légitimation du pouvoir jurisprudentiel du Conseil d'État », *Droit et Société*, n° 121, 2026, p. 569 et s., DOI 10.3917/drs1.121.0569. Résumé lu : les conclusions réinterprètent sans cesse le passé jurisprudentiel et fonctionnent comme un supplément de motivation. Statut : théorique.
- Danièle Lochak, *Le rôle politique du juge administratif français*, LGDJ, 1972 : non vérifié.

Règle opérationnelle. Aucune règle propre ne peut être tirée de ces résumés. Ils confirment seulement qu'une demande qui heurte le consensus dominant de l'institution doit être portée par un appui jurisprudentiel ou conventionnel explicite, ce que la pratique de la rédaction impose déjà.

### 1.9 Collégialité et juge unique : données lues

Rapport public 2025 du Conseil d'État (section 3.6) : en 2025, 47,1 % des décisions de la section du contentieux ont été rendues par des formations collégiales, 39,6 % par ordonnance et 13,3 % au titre des compétences propres du président de la section ; parmi les seules décisions contentieuses, 54,3 % collégiales et 45,7 % par ordonnance. Aucune donnée nationale lue sur la part du juge unique dans les tribunaux administratifs. L'annexe Contamin de 2010 relève à Paris 79 % de jugements collégiaux pour les agents non titulaires contre 66 % pour les titulaires. Statut : statistique officielle pour le Conseil d'État ; empirique limité pour Paris.

Règle opérationnelle. Devant le Conseil d'État, près d'une décision sur deux est rendue sans formation collégiale : l'acte doit être compréhensible par un lecteur unique qui décide de l'orientation. Statut : inférence.

---

## 2. Juge des référés et tri

### 2.1 Ce qui est mesuré, et par qui

- Rapport public 2025 du Conseil d'État, tableau 18 : pourvois contre les ordonnances de référé des tribunaux administratifs ; tableau 15 : taux d'admission (14,5 % en 2025 pour les référés, chiffre repris correctement par 02). Statut : statistique officielle.
- Bilans d'activité de cinq tribunaux administratifs consultés en texte brut : Montpellier 2023 et 2024, Pau 2024, Bordeaux 2024, Châlons-en-Champagne 2024. Aucun ne donne la part des ordonnances de l'article L. 522-3. Montpellier détaille les référés par type (en 2024 : 243 référés mesures utiles, 129 référés-libertés, 628 référés-suspension) sans dire comment ils ont été jugés.
- Le seul chiffre de tri reste celui du contentieux Covid devant le Conseil d'État, déjà relevé par 02.

Statut. Constat de recherche : aucune série publique sur le tri hors du contentieux Covid, conforme à 02 (T1, C.20).

### 2.2 Qui rédige les ordonnances de tri : une pratique documentée

Référence. Tribunal administratif de Pau, *Rapport annuel 2024*, https://pau.tribunal-administratif.fr/content/download/236878/document/Rapport%20annuel%202024%20TA%20de%20Pau.pdf. Extraits lus (partie « pôle d'aide à la décision »).

Ce que la source établit. L'assistante de justice et le pôle d'aide à la décision (vacataires et stagiaires) préparent les projets d'ordonnances de tri, soumis à la signature du chef de juridiction et des vice-présidents.

Solidité. Pratique institutionnelle d'un seul tribunal.

Règle opérationnelle. Le premier lecteur d'une requête en référé peut être un juriste non magistrat qui prépare une ordonnance de rejet. La requête doit donc rendre visibles, dès sa première page, l'urgence datée et le moyen sérieux, avec la pièce qui le démontre, pour qu'un lecteur pressé ne puisse pas conclure à l'évidence du rejet. Cela renforce la règle T1 de 02. Statut : inférence appuyée sur une pratique institutionnelle.

### 2.3 Le tri abusif est contrôlé en cassation

Références.
- CE, 10 novembre 2023, *Société Free Mobile*, n° 470808 (inédit), https://librejustice.fr/decision/IwvWeZqkDPGc. Lu en entier.
- Conclusions de la rapporteure publique sur cette affaire, https://www.conseil-etat.fr/fr/arianeweb/CRP/conclusion/2023-11-10/470808. Extraits lus (p. 1 et 7 à 10).
- CE, 17 juillet 2023, *Ligue des droits de l'homme*, n° 475636 (aux Tables sur un autre point), https://librejustice.fr/decision/nv59nsDitZIz : analyse officielle lue, qui porte sur le fond ; le point relatif au tri n'est connu que par les conclusions précitées.
- CE, Sect., 5 octobre 2018, *SA Finamur*, n° 412560 : connu par les mêmes conclusions, non relu.

Ce que la source établit. Le juge des référés qui rejette une demande de suspension comme manifestement mal fondée, sans instruction contradictoire, alors qu'il ne dispose d'aucun élément lui permettant de se prononcer sur les moyens soulevés, « a méconnu son office » (point 8). Les moyens restés sans réponse portaient sur la compétence du signataire et sur l'appréciation des lieux, que seule la défense pouvait documenter. Les conclusions rattachent cette solution à la ligne ouverte par *Finamur* (usage abusif de l'article R. 222-1) et à la décision LDH de 2023 rendue pour un référé-liberté.

Solidité. Droit positif pour la décision lue (inédite, chambre jugeant seule) ; inférence pour la portée générale, que les conclusions présentent comme acquise.

Règles opérationnelles.
- Contre une ordonnance de tri, le pourvoi peut soutenir que le juge a méconnu son office lorsque les moyens soulevés supposaient des éléments que seul le défendeur détenait (délégation de signature, caractéristiques de fait). Ce grief complète la règle K2 de 02, qui retient à juste titre que l'appréciation du doute sérieux elle-même échappe au contrôle.
- En amont, la requête en référé signale expressément les éléments que l'administration détient et que le juge ne peut apprécier sans instruction, ce qui rend le tri plus risqué pour le juge et prépare le moyen de cassation. Statut : inférence.

### 2.4 Rouillier (2018), *RDP*

Référence attribuée par 02 : « Référé-suspension et juge du fond, approche statistique », *Revue du droit public*, 2018, n° 1, p. 141 (référence éditeur RDP2018-1-010), https://www.labase-lextenso.fr/revue-du-droit-public/2018-n1/refere-suspension-et-juge-du-fond-approche-statistique-RDP2018-1-010.

Lecture. Non vérifié. La notice de l'éditeur est protégée par Cloudflare (403). Un moteur de recherche a restitué le plan (outil de synthèse) : « Une identité statistique : quand le fond suit le référé-suspension », distinguant le rejet pour défaut d'urgence et l'examen de la légalité en référé. Le nom de l'auteur n'a pas pu être confirmé.

Règle opérationnelle. Aucune : sans le texte, ni le périmètre ni les chiffres ne sont connus. Le harness ne cite pas cette source.

### 2.5 Après un rejet pour défaut de doute sérieux : confirmer le maintien de la requête au fond

Texte relu. CJA, art. R. 612-5-2, version en vigueur depuis le 19 juillet 2018 (décret n° 2018-617), applicable aux requêtes au fond enregistrées depuis le 1er octobre 2018, https://librejustice.fr/norm/fr/code-de-justice-administrative/r612-5-2. Lu en entier.

Ce que le texte établit. Quand une demande de suspension est rejetée parce qu'aucun moyen n'est propre à créer un doute sérieux, le requérant doit confirmer le maintien de sa requête au fond dans le mois de la notification, sauf pourvoi contre l'ordonnance ; à défaut, il est réputé s'être désisté. La notification de l'ordonnance le mentionne. Le texte ne joue pas pour un rejet fondé sur le seul défaut d'urgence.

Statut. Droit positif. L'épreuve du module (`docs/epreuves/decideurs.md`) en a relevé l'application dans des ordonnances publiées d'un tribunal administratif.

Règle opérationnelle. Après un rejet de suspension, le motif se lit d'abord : s'il porte sur le doute sérieux, la confirmation du maintien de la requête au fond s'inscrit aux échéances le jour même, avec sa date limite. Le motif de rejet renseigne aussi la stratégie au fond : un rejet pour défaut de doute sérieux est une première lecture du fond par un magistrat du tribunal.

---

## 3. Standards de contrôle et déférence envers l'administration

### 3.1 Jury de concours ou d'examen

Décisions relues.
- CE, 10 avril 2009, *El Haddioui*, n° 311888, Lebon, https://librejustice.fr/decision/8JGZWF-tyaE_. Lu en entier : « s'il n'appartient pas au juge de l'excès de pouvoir de contrôler l'appréciation faite par un jury de la valeur des candidats, il lui appartient en revanche de vérifier que le jury a formé cette appréciation sans méconnaître les normes qui s'imposent à lui ». Annulation de la délibération d'admission : questions sur l'origine et la pratique religieuse du candidat et de son épouse, « dont il n'est pas sérieusement contesté par l'administration qu'elles aient été posées ».
- CE, 3 mars 2000, n° 157621. Lu en entier : pas de contrôle de l'appréciation du jury « sauf si les notes attribuées sont fondées sur des considérations autres que la seule valeur de ces prestations ».
- CE, 23 mai 2001, n° 225827. Lu en entier : aucun texte n'impose de motiver les délibérations du jury ; l'expertise demandée sur la valeur des copies est inutile ; des allégations de bruit et d'agressivité du jury, sans élément, n'établissent pas une rupture d'égalité « de nature à exercer une influence sur les résultats ».
- CE, 26 septembre 2018, n° 405473, Tables, https://librejustice.fr/decision/GSiYu5Sxe_iV. Analyse officielle lue : contrôle du choix du sujet (erreur matérielle, sujet traitable avec le programme, questions orales permettant d'apprécier les connaissances).
- CE, 17 octobre 2016, *Université de Nice-Sophia Antipolis*, n° 386400, Tables, https://librejustice.fr/decision/p1erZSyCGutq. Analyse officielle lue : connaître un candidat ne suffit pas ; des liens de nature à influer sur l'appréciation imposent au membre du jury de s'abstenir pour l'ensemble des candidats du concours.
- CE, 9 février 2011, *Piazza*, n° 317314, Tables, https://librejustice.fr/decision/_xKAtibJdlHm. Analyse officielle lue : contrôle de l'erreur manifeste sur l'adéquation d'une candidature au profil du poste ; aucun contrôle sur les mérites scientifiques.
- CE, 14 novembre 2008, n° 303821, Tables, https://librejustice.fr/decision/7o1IoRY4sFbe. Analyse officielle lue : une cour a pu juger, sans erreur de droit, que la présence dans le jury d'un examen professionnel de l'employeur de l'un des deux seuls candidats ne garantissait pas l'égalité de traitement entre eux.
- CE, 2 octobre 2026, n° 510367, Tables, https://librejustice.fr/decision/9cJ4MeAgIo9S. Analyse officielle lue : la délibération d'un jury qui arrête la liste des admis est indivisible ; dans des circonstances particulières, elle peut être annulée en tant seulement que le nom du requérant n'y figure pas.

Statut. Droit positif.

Règles opérationnelles.
- Preuve utile : seulement des faits extérieurs à la valeur des prestations (questions posées, composition du jury, liens personnels, sujet hors programme, conditions matérielles avec leur incidence sur les résultats). Une expertise ou une comparaison de copies est inutile et signale au juge une contestation de la note.
- Moyens opérants : erreur de droit dans les critères, considération étrangère au mérite, discrimination, impartialité, composition, égalité de traitement, régularité du sujet. Le défaut de motivation de la délibération est inopérant.
- Établissement des faits : quand le candidat allègue des faits précis survenus à huis clos (une question posée à l'oral), le silence ou la contestation vague de l'administration suffit (*El Haddioui*). La requête formule donc les faits avec précision, datés, avec attestations si possible, et demande au juge d'inviter l'administration à produire les fiches d'évaluation et les procès-verbaux.
- Demande : l'annulation de la délibération, indivisible en principe ; une annulation limitée à l'absence du nom du requérant se demande à titre principal seulement si les circonstances de l'espèce la justifient (n° 510367). Le juge ne réattribue pas de note.

### 3.2 Erreur manifeste d'appréciation : l'admission exceptionnelle au séjour

Décisions relues.
- CE, 10 octobre 2025, n° 493118, Tables, https://librejustice.fr/decision/s85eJvLG_lue. Lu en entier. Un même refus de titre reposait sur deux motifs. Sur le premier (menace pour l'ordre public, article L. 412-5 du CESEDA), le juge exerce un « entier contrôle » et le préfet s'est trompé : deux rappels à la loi pour vol à l'étalage et usage de stupéfiants ne caractérisent pas une menace. Sur le second (article L. 435-3, jeune majeur confié à l'aide sociale à l'enfance), le préfet dispose d'un « large pouvoir » d'appréciation globale et le juge ne vérifie que l'erreur manifeste, ici absente. Le préfet « aurait pris la même décision » sur ce seul motif : la requête est rejetée.
- CE, 11 décembre 2019, n° 424336, Tables, https://librejustice.fr/decision/uOzkDGXWQ5z6. Analyse officielle lue : même sous contrôle restreint, le juge du fond commet une erreur de droit s'il érige un critère (l'isolement familial) en critère prépondérant d'une appréciation que la loi veut globale.
- CE, 28 novembre 2007, *Zhu*, n° 307036, Lebon, https://librejustice.fr/decision/cYLRJQHLDDd3, et CE, 29 juillet 2020, n° 428231, Tables, https://librejustice.fr/decision/MeacvUuN1o-S. Analyses officielles lues : l'admission exceptionnelle n'est pas examinée d'office ; le moyen tiré de l'ancien article L. 313-14 est inopérant contre un refus ou une obligation de quitter le territoire si aucune demande n'a été présentée sur ce fondement.

Statut. Droit positif.

Règles opérationnelles.
- Avant tout recours, la demande à l'administration vise expressément chaque fondement envisageable, y compris l'admission exceptionnelle ; un fondement absent de la demande ne pourra pas être invoqué devant le juge.
- Quand la décision repose sur plusieurs motifs soumis à des contrôles d'intensité différente, la requête attaque chacun d'eux ; gagner sur le motif contrôlé entièrement ne suffit pas si le motif soumis au contrôle restreint subsiste et que l'administration aurait pris la même décision.
- Sous contrôle restreint, la preuve utile est le dossier présenté à l'administration : formation suivie, liens familiaux, avis de la structure d'accueil, chacun daté et antérieur à la décision. La requête montre que l'appréciation globale a ignoré un élément ou en a surpondéré un, ce qui ouvre l'erreur de droit en plus de l'erreur manifeste.
- Demande : en contrôle restreint, l'injonction réaliste est le réexamen (article L. 911-2) ; l'injonction de délivrer un titre suppose que le motif d'annulation impose une décision déterminée.

### 3.3 Contrôle normal de la proportionnalité des sanctions disciplinaires

Décisions relues.
- CE, Ass., 13 novembre 2013, *M. Dahan*, n° 347704, Lebon, https://librejustice.fr/decision/Km5AApT9uh8g. Lu en entier. Il appartient au juge, « saisi de moyens en ce sens », de rechercher si les faits constituent des fautes de nature à justifier une sanction et si la sanction est proportionnée à leur gravité. La mise à la retraite d'office est maintenue. La circonstance que d'autres agents auraient été moins sévèrement sanctionnés « est sans incidence ». Le dispositif rejette la requête (les métadonnées de LibreJustice indiquent à tort « Réformation »).
- CE, 27 février 2015, *La Poste*, n° 376598, Lebon, https://librejustice.fr/decision/dIdmof4VUjuk. Analyse officielle lue : en cassation, la proportionnalité n'est contrôlée que si la solution retenue est « hors de proportion » avec les fautes (rapprochement avec CE, Ass., 30 décembre 2014, *Bonnemaison*, n° 381245, non relu).

Statut. Droit positif.

Règles opérationnelles.
- Le contrôle de proportionnalité ne s'exerce que si le moyen est soulevé : la requête le formule expressément, distinct de la contestation de la matérialité des faits et de leur qualification.
- La comparaison avec la sanction d'autres agents est inopérante ; la preuve utile porte sur la gravité propre des faits, le contexte, l'ancienneté, le comportement de l'agent après les faits.
- En appel, la discussion de la proportionnalité reste entière ; en cassation, elle n'est utile que si la sanction est manifestement hors de proportion. Le harness en informe le client avant l'appel.

### 3.4 Le bilan coûts-avantages

Décision relue. CE, Ass., 28 mai 1971, *Ville Nouvelle-Est*, n° 78825, Lebon, https://librejustice.fr/decision/tJFrXuZNmTDl. Lu en entier. Une opération ne peut être déclarée d'utilité publique que si les atteintes à la propriété privée, le coût financier et les inconvénients d'ordre social ne sont pas excessifs eu égard à son intérêt. En l'espèce, la démolition d'une centaine de maisons ne retire pas à l'opération son utilité publique ; la déclaration d'utilité publique est maintenue.

Statut. Droit positif.

Règle opérationnelle. Le requérant qui invoque le bilan chiffre chaque plateau de la balance (surfaces et logements touchés, coût, atteintes aux autres intérêts publics) et montre l'existence d'une alternative moins coûteuse documentée. L'arrêt fondateur a lui-même validé l'opération : le bilan protège rarement à lui seul, et le harness le présente comme un moyen subsidiaire derrière les vices de procédure de l'enquête. Statut : droit positif pour la règle ; inférence pour la stratégie.

### 3.5 Synthèse : ce que fait le standard

| Standard | Preuve utile | Moyens opérants | Demande réaliste |
| --- | --- | --- | --- |
| Appréciation souveraine (jury) | Faits extérieurs à la valeur des prestations, précis et datés | Erreur de droit, considération étrangère, discrimination, impartialité, composition, égalité, sujet | Annulation de la délibération et réexamen |
| Erreur manifeste (admission exceptionnelle, adéquation au profil) | Dossier présenté à l'administration avant la décision | Erreur manifeste, erreur de droit sur les critères, critère érigé en condition, fondement visé dans la demande | Réexamen |
| Contrôle normal (sanction, ordre public) | Gravité propre des faits, contexte, pièces de l'agent | Qualification, proportionnalité si le moyen est soulevé ; comparaison avec d'autres agents inopérante | Annulation ; sanction moindre à reprendre par l'administration |
| Bilan (utilité publique) | Chiffrage des atteintes et des coûts, alternatives | Excès des inconvénients, vices de l'enquête | Annulation de la déclaration |
| Cassation | Pièces déjà au dossier des juges du fond | Erreur de droit, dénaturation, qualification ; proportionnalité seulement « hors de proportion » | Cassation et renvoi ou règlement au fond |

### 3.6 Données sur la déférence

- Rapport public 2025 du Conseil d'État (https://conseil-etat.fr/Media/actualites/documents/2026/mai-2026/rapport-public-2025). Extraits lus sur le texte brut (tableaux 10, 15, 16 et 18 ; pages sur les tribunaux administratifs, la CNDA et l'exécution). Le Conseil d'État en premier ressort, hors référés, donne satisfaction totale ou partielle dans 13,1 % des affaires réglées en 2025 (19,8 % en 2021 et 2022, 14,5 % en 2023, 10,4 % en 2024 ; tableau 10). Les tribunaux administratifs ont 283 136 sorties nettes en 2025 et 66 064 décisions favorables au moins partiellement aux requérants, soit environ 23 % par calcul ; le dénominateur comprend ordonnances, désistements et non-lieux. La CNDA accorde une protection à 23,3 % des requérants en 2025. Aucun taux d'annulation par matière n'est publié dans ce rapport. Statut : statistique officielle.
- Aucune autre série officielle de taux d'annulation par matière n'a été trouvée (recherches sur le contentieux des étrangers comprises). Statut : constat de recherche.
- Contamin et al., section 1.6 : en fonction publique à Paris, 32 % de succès dont 22 % d'annulation totale. Statut : empirique limité.

Règle opérationnelle. Le harness donne au client des ordres de grandeur par juridiction et non par juge : environ un requérant sur quatre obtient au moins partiellement satisfaction devant les tribunaux administratifs, en comptant les satisfactions obtenues de l'administration en cours d'instance. Il ne présente aucun taux par matière comme officiel.

---

## 4. Interdiction du profilage des magistrats

Textes relus.
- Article L. 10 du CJA, quatrième alinéa, version en vigueur depuis le 25 mars 2019 (issue de l'article 33 de la loi n° 2019-222 du 23 mars 2019), LEGIARTI000038311171, https://librejustice.fr/norm/fr/code-de-justice-administrative/l10. Lu en entier.
- Article L. 111-13 du COJ, troisième alinéa, même version, LEGIARTI000038311162, https://librejustice.fr/norm/fr/code-de-l-organisation-judiciaire/l111-13. Lu en entier.
- Articles 226-18 (version du 7 août 2004), 226-24 (version du 14 mai 2009) et 226-31 du code pénal. Lus en entier.
- Cons. const., 21 mars 2019, n° 2019-778 DC, §§ 85 à 95 et dispositif, https://www.conseil-constitutionnel.fr/decision/2019/2019778DC.htm. Extraits lus sur le texte brut.

Texte exact de l'interdiction (identique dans les deux codes) : « Les données d'identité des magistrats et des membres du greffe ne peuvent faire l'objet d'une réutilisation ayant pour objet ou pour effet d'évaluer, d'analyser, de comparer ou de prédire leurs pratiques professionnelles réelles ou supposées. La violation de cette interdiction est punie des peines prévues aux articles 226-18, 226-24 et 226-31 du code pénal, sans préjudice des mesures et sanctions prévues par la loi n° 78-17 du 6 janvier 1978 relative à l'informatique, aux fichiers et aux libertés. »

Peines. Article 226-18 : cinq ans d'emprisonnement et 300 000 euros d'amende. Article 226-24 : pour les personnes morales, l'amende de l'article 131-38 (quintuple) et les peines des 2° à 5° et 7° à 9° de l'article 131-39, l'interdiction d'activité portant sur l'activité à l'occasion de laquelle l'infraction a été commise. Article 226-31 : peines complémentaires pour les personnes physiques, dont l'interdiction d'exercer l'activité professionnelle et l'affichage de la décision.

Décision du Conseil constitutionnel. Les députés requérants soutenaient qu'une meilleure connaissance des juges favoriserait l'égalité des justiciables (§ 89). Le Conseil répond que le législateur « a entendu éviter qu'une telle réutilisation permette, par des traitements de données à caractère personnel, de réaliser un profilage des professionnels de justice à partir des décisions rendues, pouvant conduire à des pressions ou des stratégies de choix de juridiction de nature à altérer le fonctionnement de la justice » (§ 93) ; aucune distinction injustifiée ni atteinte au procès équitable (§ 94) ; conformité de la première phrase des deux alinéas (§ 95 et dispositif).

Statut. Droit positif.

Ce que l'interdiction fait à un outil qui extrait des décisions publiées le nom du juge et ses taux de rejet. L'extraction du nom aux fins de calculer un taux de rejet, de classer des juges ou de prédire leur décision est une réutilisation des données d'identité ayant pour objet d'analyser, de comparer et de prédire leurs pratiques : elle est interdite et pénalement sanctionnée, que l'outil soit vendu ou utilisé en interne. Le texte vise aussi l'effet : un traitement conçu à d'autres fins qui produit de tels classements tombe sous l'interdiction. Le rapporteur public est un magistrat ; les membres du greffe sont expressément couverts.

Points ouverts, à traiter avec prudence. Des statistiques par juridiction ou par chambre sans données d'identité ne sont pas visées par la lettre du texte ; elles le deviennent en pratique si la formation se réduit à un juge identifiable (juge unique, président de chambre) : inférence. La qualité de « magistrat » des conseillers prud'hommes et des juges des tribunaux des activités économiques n'a pas été vérifiée ; le harness les traite comme couverts. Les juges de la CEDH ne relèvent pas de ces textes, mais la consigne du plugin interdit tout profilage nominatif.

Règles opérationnelles.
- Le plugin n'extrait, ne stocke et ne croise jamais le nom des magistrats, rapporteurs publics ou greffiers présents dans les décisions, sauf pour citer une décision par sa référence officielle. Les noms sont retirés des corpus d'apprentissage et des bases de recherche internes.
- Le choix de forum se fonde sur des critères de droit et de procédure (compétence, délais, voies d'urgence, standard de contrôle, statistiques officielles par juridiction), jamais sur la personne du juge.
- Le juge simulé reçoit le standard de contrôle, les pièces, la jurisprudence applicable et des ordres de grandeur par juridiction ; il ne reçoit aucune donnée sur l'identité ou les habitudes d'un juge réel. La variabilité entre juges se modélise comme une marge d'incertitude anonyme (section 5.7).

---

## 5. Juge judiciaire

### 5.1 Gautron et Retière (2013), la décision pénale dans cinq tribunaux correctionnels

Référence. Virginie Gautron, Jean-Noël Retière, « La justice pénale est-elle discriminatoire ? Une étude empirique des pratiques décisionnelles dans cinq tribunaux correctionnels », colloque de l'ARDIS, décembre 2013, https://shs.hal.science/halshs-01075666. Résultats complets dans « Des destinées judiciaires pénalement et socialement marquées », in J. Danet (dir.), *La réponse pénale. Dix ans de traitement des délits*, PUR, 2013, p. 211-251 (https://shs.hal.science/halshs-01076712, téléchargé, non lu).

Lecture. Lu en entier.

Ce que la source établit. Environ 7 500 dossiers délictuels de majeurs traités en 2000, 2003, 2006 et 2009 dans cinq juridictions de l'ouest, dont 3 537 affaires poursuivies analysées par régression logistique ; une soixantaine d'entretiens avec vignettes soumises aux magistrats.
- Les marqueurs pénaux dominent : une mention au bulletin n° 1 du casier multiplie le risque d'emprisonnement ferme par 3,7, deux par 8,4, trois ou plus par 37,3.
- L'absence à l'audience pèse lourd : jugement contradictoire à signifier, risque d'emprisonnement ferme multiplié par 7,4 ; jugement par défaut, par 2,1.
- Le « pré-jugement » compte : la comparution immédiate multiplie ce risque par 8,4, la détention provisoire dans l'affaire par 8,1.
- Les garanties de représentation orientent la procédure : être né à l'étranger multiplie le risque de comparution immédiate par 3,1 et de détention provisoire par 4,8 ; être sans domicile, par 2,85 et 6. À marqueurs pénaux égaux, les personnes sans domicile ont un risque d'emprisonnement ferme multiplié par 2,5 ; le fait d'être sans emploi par 1,47 ; un revenu inférieur à 300 euros, par 3,3 par rapport à plus de 1 500 euros.
- Présence à l'audience : 78,2 % des prévenus ayant un emploi contre 64,3 % des sans-emploi et 34,9 % des sans-domicile. Les magistrats interrogés disent ménager ceux dont la prison « casserait » une insertion.

Solidité. Empirique solide pour une étude française (échantillon important, régressions, triangulation qualitative), limitée au grand ouest et à la décennie 2000.

Règles opérationnelles.
- Défense correctionnelle : la priorité est la présence du prévenu à l'audience et la preuve documentée des garanties de représentation et d'insertion (domicile, contrat de travail, bulletins de salaire, attestation d'hébergement, suivi de soins), produites avant l'orientation par le parquet et au plus tard à l'audience.
- Devant le juge des libertés et de la détention et en comparution immédiate, la défense apporte des garanties concrètes de représentation : elles commandent l'orientation, qui commande ensuite la peine.
- Le récit de la personnalité ne compense pas un casier : l'argument porte sur l'ancienneté des mentions, leur nature et l'effet d'une peine ferme sur une insertion démontrée.

### 5.2 Bastard, Mouhanna, Delvaux et Schoenaers (2019), l'accélération

Référence. Benoit Bastard, Christian Mouhanna, David Delvaux, Frédéric Schoenaers, *L'esprit du temps. L'accélération dans l'institution judiciaire en France et en Belgique*, rapport pour la Mission de recherche Droit et Justice, n° 08.30, https://hal.science/hal-05216483. Bastard et Mouhanna, *Une justice dans l'urgence. Le traitement en temps réel des affaires pénales*, PUF, 2007 : non vérifié.

Lecture. Extraits lus : introduction (p. 8-9), passage sur les barèmes du parquet (p. 59-62), plan détaillé.

Ce que la source établit. Observations et entretiens dans trois tribunaux de grande instance français et deux tribunaux belges, sur le traitement en temps réel, le divorce et les assises. Au parquet observé, les substituts de permanence utilisent, sans base légale et malgré la réticence du procureur, des tableaux d'orientation : en circulation routière (composition pénale, ordonnance pénale, CRPC ou convocation selon le taux d'alcoolémie et l'existence d'un accident) et en vol à l'étalage (seuils de 50, 100 et 300 euros, restitution, réitération). Les auteurs y voient une standardisation destinée à aller vite et à répondre de façon uniforme.

Solidité. Empirique limité (sites pseudonymisés, un barème observé).

Règle opérationnelle. Au stade de l'orientation pénale, la défense agit sur les variables du barème avant la décision : restitution ou indemnisation immédiate, montant, absence de réitération, justificatifs. Une fois l'orientation prise, la marge se réduit. Statut : inférence.

### 5.3 Collectif Onze (2013), *Au tribunal des couples*

Référence. Le Collectif Onze, *Au tribunal des couples. Enquête sur des affaires familiales*, Odile Jacob, 2013. Compte rendu : Sandrine Dauphin, *Politiques sociales et familiales*, n° 117, 2014, p. 89-91, https://www.persee.fr/doc/caf_2101-8081_2014_num_117_1_3015.

Lecture. Le livre n'a pas été lu. Compte rendu lu pour sa première page (p. 89).

Ce que la source établit (selon le compte rendu). Enquête de 2009-2010 dans quatre tribunaux de grande instance : 122 heures d'audiences observées (330 affaires), 400 dossiers tirés au sort, entretiens avec 21 juges aux affaires familiales. Neuf affaires par demi-journée, dix-huit minutes en moyenne ; la présence d'avocats allonge l'audience ; les classes populaires sont moins souvent assistées ; les juges s'en remettent largement aux accords des parties et consacrent leur temps aux conflits de résidence plus qu'aux pensions alimentaires, traitées comme une « histoire de calcul ». Spire et Weidenfeld (2019) en retiennent que les classes moyennes et supérieures cantonnent le juge à l'homologation.

Solidité. Empirique limité, connu de seconde main.

Règle opérationnelle. Devant le juge aux affaires familiales, l'acte arrive avec un accord le plus complet possible ou, à défaut, avec un calcul de pension déjà fait et justifié, que le juge peut reprendre en dix-huit minutes ; l'argumentation se concentre sur la résidence et l'intérêt de l'enfant. Statut : inférence.

### 5.4 Travail et charge des magistrats

Référence. IERDJ, *Le travail en juridiction : analyse pluridisciplinaire*, 2024, https://hal.science/hal-05193555 (groupe de réflexion dont Cécile Vigour).

Lecture. Extraits lus (synthèse, p. 7-13).

Ce que la source établit. Synthèse de travaux existants : débordement temporel (jugements rédigés pendant les congés), intensification et fragmentation des tâches, poids du reporting, effets ambivalents du numérique. Elle ne mesure pas le temps passé par dossier.

Solidité. Synthèse institutionnelle, sans donnée nouvelle.

Règle opérationnelle. Aucune règle mesurable. L'acte court, structuré et autoportant que 02 recommande déjà reste la seule conséquence raisonnable ; cette source ne la démontre pas.

### 5.5 Appel civil : confirmation et infirmation

Référence. Ministère de la Justice, *Références statistiques Justice*, édition 2026, fiche 4.7 « Les cours d'appel », https://www.justice.gouv.fr/sites/default/files/2026-06/RSJ2026%204_7.pdf. Lu en entier (une page ; tableau reconstruit, totaux vérifiés par addition).

Ce que la source établit. En 2025, 144 255 affaires au fond terminées en appel civil : 79 514 confirmations totales ou partielles (55,1 %), 17 945 infirmations (12,4 %), 46 796 autres décisions (32,4 %, radiations, caducités, désistements notamment). Parmi les seules décisions de confirmation ou d'infirmation, l'infirmation représente environ 18,4 % (calcul). Une réformation partielle est comptée parmi les confirmations partielles. Taux d'appel des jugements au fond en 2024 : 13,3 % pour les tribunaux judiciaires, 61 % pour les conseils de prud'hommes, 9,8 % pour les juridictions commerciales. Délai moyen en 2025 : 13,5 mois.

Solidité. Statistique officielle.

Règle opérationnelle. Avant tout appel, le client reçoit l'ordre de grandeur : un appel tranché au fond aboutit à une infirmation totale dans moins d'un cas sur cinq, et près d'une affaire sur trois se termine sans arrêt au fond. Le harness vise une réformation partielle chiffrée plutôt qu'une infirmation totale quand le dossier s'y prête.

### 5.6 Conseil de prud'hommes : départage

Référence. *Références statistiques Justice*, édition 2026, fiche 4.4 « Les conseils de prud'hommes », https://www.justice.gouv.fr/sites/default/files/2026-06/RSJ2026%204_4.pdf. Extraits lus (texte et tableau principal).

Ce que la source établit. En 2025, 132 000 affaires nouvelles (113 000 au fond) et 107 000 affaires terminées ; 7 100 affaires terminées par un départage ; taux de départage (affaires terminées par départage rapportées aux affaires terminées avec délibéré) de 14 %, en baisse de deux points ; délai moyen de 15,4 mois pour les affaires au fond.

Solidité. Statistique officielle.

Règle opérationnelle. Devant le bureau de jugement paritaire, l'acte s'adresse à des juges non professionnels issus des deux camps ; environ une affaire délibérée sur sept finit devant le juge départiteur, qui statue avec les conseillers. Le harness prépare dès le départ des conclusions lisibles par un magistrat professionnel. Statut : inférence pour la stratégie.

### 5.7 Barème et dispersion entre juges en matière de licenciement

Références.
- Raphaël Dalmasso, Camille Signoretto et al., *Relations de travail et d'emploi et comportements des acteurs dans un contexte de réformes législatives*, rapport pour la DARES, 2023, https://hal.science/hal-04180302. Extraits lus (sommaire, p. 154-155, conclusion p. 182-183, synthèse p. 220). Article lié : Dalmasso et Signoretto, *Droit social*, 2022, https://shs.hal.science/halshs-03574803, résumé lu.
- Pierre Cahuc, Stéphane Carcillo, Bérengère Patault, Flavien Moreau, « Judge Bias in Labor Courts and Firm Performance », IZA DP n° 13794, octobre 2020, https://docs.iza.org/dp13794.pdf ; version publiée au *Journal of the European Economic Association*, 22(3), 2024, p. 1319-1366 (non lue). Extraits lus (résumé, introduction p. 1-3).

Ce que les sources établissent.
- Dalmasso et Signoretto : sur des arrêts de cours d'appel tirés de JuriCA, le barème de 2017 a réduit les indemnités moyennes et médianes et resserré leur dispersion ; la baisse est la plus forte pour les salariés de deux à cinq ans d'ancienneté dans les entreprises de onze salariés et plus, plus faible pour les anciennetés élevées. Avant le barème, les femmes obtenaient en moyenne 9 mois de salaire contre 7,2 pour les hommes, écart expliqué surtout par l'ancienneté. Les auteurs anticipent que le contentieux devienne celui des salariés anciens et mieux payés. Empirique limité (effectifs réduits dans certaines analyses).
- Cahuc et al. : environ 145 000 arrêts de chambres sociales de cours d'appel de 2006 à 2016, données d'entreprises appariées dans un centre d'accès sécurisé ; l'attribution quasi aléatoire des affaires aux présidents de chambre permet d'isoler un effet propre au juge. Passer du décile le plus favorable aux employeurs au décile le plus favorable aux salariés augmente l'indemnité attendue d'environ deux mois de salaire, soit 20 % de l'indemnité moyenne. La prime de risque liée à cette dispersion ne dépasse pas 1,5 % de l'indemnité attendue. Empirique solide (publication revue, identification quasi expérimentale), antérieur au barème.

Règles opérationnelles.
- Le harness chiffre l'indemnité d'un licenciement sans cause réelle et sérieuse par la fourchette légale du barème, puis indique une marge d'incertitude liée au juge sans jamais l'attribuer à une personne ; avant 2017, cette marge était de l'ordre de deux mois de salaire entre extrêmes.
- Pour un salarié de faible ancienneté, le conseil compare le gain plafonné au coût et à la durée de la procédure, et examine les fondements qui écartent le barème (nullité du licenciement notamment), dont l'existence est connue mais dont les textes n'ont pas été relus ici. Statut : inférence.

### 5.8 Ce qui n'a pas été trouvé

Juge de la mise en état et juge des contentieux de la protection : aucune étude empirique trouvée en dehors des fiches statistiques déjà lues par 02. Évelyne Serverin, *Les affaires prud'homales dans la chaîne judiciaire de 2004 à 2018*, DACS, 2019 : non vérifié (connu par la bibliographie de Dalmasso et Signoretto).

---

## 6. Cour de cassation

### 6.1 Sommer et Munoz-Perez (2014), dix ans de non-admission

Référence. Jean-Michel Sommer, Brigitte Munoz-Perez, *Dix ans de non-admission devant les chambres civiles de la Cour de cassation, 2002-2012*, Cour de cassation, février 2014, 82 p., https://shs.hal.science/halshs-01068834.

Lecture. Extraits lus sur le texte intégral obtenu par l'API de HAL : résumé des principaux résultats (p. 3-4), introduction (p. 5-6), section V sur la gestion de la non-admission par les chambres (p. 53-58).

Ce que la source établit.
- De 2002 à 2012, les décisions des juges du fond sont cassées dans 36,2 % des cas ; les rejets se répartissent en 52,5 % de rejets motivés et 47,5 % de non-admissions (chiffre de 02 confirmé).
- La part des non-admissions parmi les rejets varie de 25 % en droit international privé à 60 % pour les relations avec les personnes publiques et les professionnels du droit ; environ 48 % en droit du travail, protection sociale et contrats.
- Depuis 2004, le conseiller rapporteur rédige un rapport en vue de la non-admission qui répond à chaque moyen et chaque branche ; il est mis à disposition des avocats par voie électronique.
- Les avocats aux Conseils n'ont produit d'observations que dans 6,2 % des dossiers orientés en non-admission sur 2004-2012 (8,5 % devant la chambre commerciale, 4,7 % devant la chambre sociale), avec une hausse nette à partir de 2010 (environ 13 %). En leur présence, 18 % des dossiers sont réorientés vers une formation de jugement, contre moins de 7 % sans ; la réorientation totale reste autour de 8 % par an.
- Il n'existe plus de cellule de tri préalable à la distribution des dossiers aux rapporteurs.

Solidité. Statistique officielle pour les flux (données NOMOS) ; empirique limité pour l'effet des observations, qui est une association : les avocats choisissent d'intervenir dans les dossiers qu'ils jugent les plus défendables.

Règles opérationnelles.
- Quand un pourvoi est orienté en non-admission, le harness prépare systématiquement, pour l'avocat aux Conseils, des observations qui répondent au rapport moyen par moyen et montrent ce qu'il n'a pas vu.
- Le client est informé des ordres de grandeur par matière avant de former un pourvoi.

### 6.2 Munoz Perez et Serverin (2020), la chaîne documentaire du pourvoi civil

Référence. Brigitte Munoz Perez, Evelyne Serverin, *Éléments pour une statistique qualitative des affaires civiles traitées par la Cour de cassation*, rapport pour le SDER de la Cour de cassation, 28 décembre 2020, 87 p., https://shs.hal.science/halshs-03549654.

Lecture. Extraits lus (sommaire, chapitre 1 section 2, chapitre préliminaire et passages sur les études statistiques p. 7-18).

Ce que la source établit. Le dossier numérique d'un pourvoi civil (NOMOS) réunit le mémoire ampliatif, le mémoire en défense, la fiche d'orientation du service de documentation, des études et du rapport, le rapport et l'avis du conseiller rapporteur ou la fiche de non-admission, l'avis de l'avocat général et les projets d'arrêt. L'orientation se fait à partir d'une table des matières. Le rapport présente un exemple de répartition des décisions de la première chambre civile (rejets non spécialement motivés 46,9 %, rejets 27,9 %, cassations 17,4 %, cassations sans renvoi 7,7 %) dont l'année et la nature exacte (donnée réelle ou maquette de tableau proposé) ne sont pas certaines à la lecture.

Solidité. Pratique institutionnelle pour la chaîne documentaire ; chiffre de la première chambre civile non utilisable.

Règle opérationnelle. Le mémoire ampliatif est lu d'abord par le service qui établit la fiche d'orientation : son premier paragraphe nomme la matière et la question de droit en termes qui permettent un classement exact. Statut : inférence.

### 6.3 Ce qui manque

Aucune étude sociologique récente sur les conseillers référendaires ou les avocats aux Conseils n'a été trouvée sur theses.fr et HAL. Une thèse doctrinale existe : Cathie-Sophie Pinat, *Le discours de l'avocat devant la Cour de cassation : étude de théorie du droit*, Montpellier, 2015 (notice lue). Ana Maria Falconi et Claire Lemercier, « L'intéressé est un réclamant d'habitude. Porter un litige devant les hautes cours en France, 1945-2015 », communication, 2023, https://shs.hal.science/halshs-05320184 : non vérifié (pas de texte déposé). Rapports annuels de la Cour de cassation : non lus.

---

## 7. Cour européenne des droits de l'homme

### 7.1 Statistiques officielles 2025

Références. CEDH, *Analysis of Statistics 2025*, janvier 2026, https://www.echr.coe.int/documents/d/echr/stats-analysis-2025-eng (extraits lus : p. 3-4 et tableaux) ; *Statistics 2025* (une page, lue en entier), https://www.echr.coe.int/documents/d/echr/stats-annual-2025-eng ; fiche pays France, mise à jour de juillet 2026, https://www.echr.coe.int/documents/d/echr/cp_france_fra (p. 1 lue) ; *Violations by Article and by State 2025*, https://www.echr.coe.int/documents/d/echr/stats-violation-2025-eng (ligne France lue).

Ce que les sources établissent.
- En 2025, 31 800 requêtes attribuées à une formation judiciaire, dont 22 750 identifiées d'emblée comme relevant du juge unique et probablement irrecevables.
- 38 573 requêtes tranchées : 31 562 déclarées irrecevables ou rayées (environ 82 %, calcul), dont 27 488 par un juge unique ; 7 011 par arrêt.
- 8 300 dossiers ont été clôturés administrativement, sans décision juridictionnelle, dont 93 % pour non-respect de l'article 47 du règlement.
- France, 2025 : 863 requêtes attribuées, 69 communiquées au Gouvernement, 646 terminées, dont 545 par juge unique, 70 par un comité et 4 par une chambre déclarées irrecevables ou rayées, 27 tranchées par 20 arrêts, dont 10 concluent à au moins une violation. Environ 96 % des requêtes françaises terminées en 2025 l'ont été sans arrêt (calcul : 619 sur 646). Au 1er juillet 2026, 681 requêtes pendantes, dont 396 devant un juge unique.

Solidité. Statistique officielle pour les effectifs, relus le 20 novembre 2026 dans l'analyse statistique 2025 et la fiche pays de juillet 2026. Les parts d'environ 82 %, 96 % et 4 % sont calculées à partir de ces effectifs : la Cour ne les publie pas.

### 7.2 Exigences formelles

Textes relus. Règlement de la Cour, version du 15 septembre 2025, article 47 (lu en entier) et article 49 § 1, https://www.echr.coe.int/documents/d/echr/rules_court_eng. Article 35 § 1 de la Convention, version en vigueur (délai de quatre mois), https://librejustice.fr/norm/intl/convention-de-sauvegarde-des-droits-de-l-homme-et-des-libertes-fondamentales/35.

Ce que les textes établissent. La requête est présentée sur le formulaire de la Cour et contient tous les renseignements demandés, dont un exposé concis et lisible des faits, des violations alléguées et des arguments, et du respect des conditions de recevabilité de l'article 35 § 1 (art. 47 § 1). Ces renseignements doivent permettre à la Cour de déterminer la nature et l'objet de la requête sans recourir à un autre document ; un complément est possible, limité à 20 pages (art. 47 § 2). Doivent être joints les copies des décisions attaquées et des pièces établissant l'épuisement des voies de recours et le respect du délai, classées par date, numérotées et identifiées (art. 47 § 3). À défaut, la requête n'est pas examinée, sauf explication adéquate, mesure provisoire ou décision contraire de la Cour (art. 47 § 5.1). La date d'introduction est celle de l'envoi d'un formulaire conforme (art. 47 § 6). Une requête dont les éléments suffisent à révéler l'irrecevabilité est confiée à un juge unique (art. 49 § 1). Le délai est de quatre mois à compter de la décision interne définitive (art. 35 § 1).

Statut. Droit positif.

Règles opérationnelles.
- Le formulaire se suffit à lui-même : les faits, les griefs et la recevabilité y sont exposés en entier, l'annexe ne faisant qu'approfondir. Le harness vérifie chaque case et chaque pièce avant l'envoi ; un formulaire incomplet n'interrompt pas le délai de quatre mois.
- La rubrique sur l'épuisement montre, pièce par pièce, que chaque grief a été soulevé au moins en substance devant la juridiction interne la plus élevée. Une requête qui laisse un juge unique déduire l'irrecevabilité de ses seuls éléments sera rejetée sans motivation développée.
- Le client est informé qu'une requête contre la France aboutit à un arrêt dans environ 4 % des cas, proportion calculée sur les requêtes terminées en 2025 (27 sur 646) et non publiée par la Cour.

### 7.3 Culture et impartialité de la Cour

- Erik Voeten, « The Impartiality of International Judges: Evidence from the European Court of Human Rights », *American Political Science Review*, 102(4), 2008, p. 417-433, DOI 10.1017/S0003055408080398. Résumé lu. Sur un jeu de données d'opinions dissidentes : pas de biais culturel ou géopolitique systématique ; un certain biais en faveur du gouvernement national quand le juge est dans une situation de carrière précaire ; une variation forte de l'inclination des juges à laisser une marge aux États ; les juges issus d'anciens États socialistes plus enclins à constater des violations contre leur propre gouvernement. Statut : empirique solide selon la revue et le résumé ; le texte, la période couverte et les effectifs n'ont pas été lus.
- Mikael Rask Madsen, « The Challenging Authority of the European Court of Human Rights: From Cold War Legal Diplomacy to the Brighton Declaration and Backlash », 2015, DOI 10.2139/ssrn.2588471. Résumé lu : autorité devenue « inégale et partielle » depuis la déclaration de Brighton de 2012. Statut : théorique.

Règle opérationnelle. Ces travaux mesurent des inclinations de juges nommés. Le plugin n'en tire aucun profil individuel. Il retient seulement que la marge d'appréciation laissée aux États est l'axe principal de désaccord entre juges : la requête démontre pourquoi la marge doit être étroite dans l'espèce (droit en cause, consensus européen, qualité du contrôle interne). Statut : inférence.

---

## 8. Conseil constitutionnel et filtrage des QPC

Référence. Rapport public 2025 du Conseil d'État, partie statistique, p. 47-48 et 49-56. Extraits lus sur le texte brut ; tableaux reconstruits et vérifiés par addition.

Ce que la source établit.
- Tribunaux administratifs en 2025 : 365 QPC traitées, 22 transmises au Conseil d'État, soit 6 %. Cours administratives d'appel : 124 traitées, 7 transmises, 5,6 %.
- Conseil d'État en 2025 : 209 QPC enregistrées (178 par saisine directe, 29 transmises par les tribunaux et cours, 2 par les juridictions spécialisées) ; 205 traitées, dont 35 renvois au Conseil constitutionnel. Deux fichiers du rapport sont en ligne et se contredisent sur la suite (tableau p. 48 et texte de présentation p. 59) : celui modifié le 1er septembre 2026 (https://conseil-etat.fr/content/download/239232/file/Rapport%20public%202025.pdf) donne 111 non-renvois, 59 autres issues (irrecevabilité, non-lieu, désistement) et un taux de renvoi de 24 % hors ces autres issues ; celui modifié le 11 mai 2026 (https://www.conseil-etat.fr/content/download/239421/document/Rapport%20public_2025.pdf) donne 59 non-renvois, 111 autres issues et 37,2 %. Les deux concordent pour les années antérieures (23 % en 2024, 14,7 % en 2023, 28,9 % en 2022, 27,3 % en 2021). Les deux fichiers ont été relus le 20 novembre 2026 ; aucun ne dit lequel corrige l'autre.
- Le tableau que le Conseil d'État consacre au sens des décisions du Conseil constitutionnel, dans sa rubrique sur les QPC dont il est saisi, compte pour 2025 37 décisions : 17 de conformité (45,9 %), 19 de non-conformité (51,4 %) et un non-lieu. Le périmètre exact (QPC renvoyées par le seul Conseil d'État) n'est pas précisé dans le passage lu.

Solidité. Statistique officielle, sauf pour la répartition 2025 entre non-renvois et autres issues, que les deux versions du rapport donnent en sens contraire. Les données de la Cour de cassation n'ont pas été lues.

Règle opérationnelle. Une QPC soulevée devant un tribunal administratif passe le premier filtre dans environ 6 % des cas ; posée directement devant le Conseil d'État, elle est renvoyée dans environ un quart des cas examinés au fond selon la série 2021 à 2024 et la version la plus récente du rapport (24 % en 2025), l'autre version donnant 37,2 %. Le harness réserve la QPC aux questions nouvelles ou sérieuses au sens strict et la pose, quand la voie existe, directement devant la juridiction suprême saisie.

---

## Corrections à 02

1. **Pougnet 2026 (A.4, P2 ; D.4).** L'autrice est Rachel Pougnet. L'article repose sur quatre entretiens avec des rapporteurs publics du Conseil d'État, dans le seul contentieux de la déchéance de nationalité. Il ne mesure aucune fréquence ; il décrit une norme d'accord avec la chambre et l'évitement des conclusions contraires, que chacun des quatre interrogés a pourtant pratiquées plusieurs fois. La phrase de 02 sur « des rapporteurs qui s'alignent le plus souvent sur la chambre avant de rédiger » doit préciser ce périmètre et porter le statut « empirique limité ». Elle ne peut pas fonder une règle applicable aux tribunaux administratifs, auxquels se rapporte le reste de P2. La lecture reste à travers un outil de synthèse, le site étant protégé par un défi anti-robot.
2. **Mesure du suivi du rapporteur public (P2 ; C.19).** L'affirmation de 02 est confirmée après une recherche plus large (rapport public 2025, discours de 2016 relu en entier, theses.fr, HAL, OpenAlex, moteurs de recherche) : aucune mesure publique n'existe.
3. **Latour 2002 (D.4).** Le chapitre 5 est accessible en version anglaise revue par l'auteur sur son site ; il a été lu par extraits. Le statut « non vérifié ; compte rendu par outil de synthèse » doit devenir « extraits lus (chapitre 5) », avec l'apport décrit en 1.1.
4. **Contamin et al. (D.4).** Le rapport complet de 2007 et sa synthèse sont en accès libre sur le stockage de l'IERDJ ; ils incluent l'annexe de 2010 sur le tribunal administratif de Paris, base de l'article de *Droit et Société* de 2011. Le statut « non vérifié ; connu par Morri (outil de synthèse) » est inexact. 02 ne contient aucune donnée sur l'effet de l'avocat et l'inégalité des requérants devant le juge administratif ; la section 1.6 comble ce manque.
5. **Sommer et Munoz-Perez 2014 (A.5, K3 ; D.4).** Le texte intégral est accessible par l'API de HAL ; « résumé lu, texte intégral inaccessible » doit devenir « extraits lus ». Les chiffres de 02 (47,5 % ; 18 % contre moins de 7 %) sont exacts. Il manque à 02 que les observations n'étaient produites que dans 6,2 % des dossiers orientés en non-admission, que la réorientation totale reste autour de 8 %, et que l'effet mesuré est une association exposée à un biais de sélection.
6. **Contrôle du tri (A.5, K2).** La règle selon laquelle le pourvoi ne discute pas l'appréciation du doute sérieux est exacte, mais incomplète : le rejet par ordonnance de tri d'une demande dont le juge ne pouvait apprécier les moyens sans instruction est censuré comme méconnaissance de son office (CE, 10 novembre 2023, n° 470808 ; LDH, n° 475636, pour le référé-liberté). K2 et T1 doivent intégrer ce moyen.
7. **Taux de cassation par type (A.5, K1).** Le calcul « environ 16 % » pour un pourvoi contre un arrêt de cour administrative d'appel applique le taux de cassation après admission de 61,4 %, qui est global (tableau 16) et non ventilé par type de décision attaquée. Le chiffre est une approximation fondée sur une hypothèse d'uniformité ; 02 doit le dire.
8. **Sauvé 2016 (D.4).** Lu en entier sur le texte brut : le statut « outil de synthèse » peut être relevé ; le discours ne contient aucun chiffre de suivi. La règle P1 gagnerait à citer CE, Sect., 21 juin 2013, *Communauté d'agglomération du pays de Martigues*, n° 352427, décision de principe sur la fonction du sens des conclusions, et le point 3 d'*Eden* sur les conclusions à fin d'injonction.
9. **Rouillier 2018 (D.4).** Toujours non vérifié ; le nom de l'auteur n'a pas pu être confirmé sur la notice de l'éditeur. 02 ne doit pas lui attribuer de contenu.
10. **Interdiction du profilage.** Les sections lues de 02 ne mentionnent pas les articles L. 10 du CJA et L. 111-13 du COJ. Toute règle de 02 qui ferait dépendre l'acte d'un « profil » du juge doit être relue à leur lumière ; les règles lues (A.1 à A.5) n'en contiennent pas.

---

## Sources non lues et obstacles

- Spire et Weidenfeld, « Le tribunal administratif : une affaire d'initiés ? », *Droit et Société*, n° 79, 2011 : Cairn protégé par un captcha (DataDome), non contourné ; son contenu chiffré est connu par l'annexe de 2010 du rapport Contamin.
- Pougnet 2026 et les comptes rendus OpenEdition (Belorgey 2004 sur Latour, Lapeyre 2016 sur le Collectif Onze) : défi anti-robot Anubis, non contourné ; Pougnet lu par outil de synthèse.
- Lochak 2007, Bui-Xuan 2007, Renaud 2026 : PDF Cairn bloqués ; résumés lus par OpenAlex.
- Rouillier 2018 (*RDP*), notice Lextenso : Cloudflare, erreur 403.
- France Stratégie, rapport final d'évaluation des ordonnances de 2017 (février 2024) : le serveur renvoie une page HTML au lieu du PDF.
- Latour 2002 (livre complet), Lochak 1972, Bastard et Mouhanna 2007, Collectif Onze 2013 (livre), Serverin 2019 (DACS) : ouvrages ou rapports non disponibles en accès libre par les outils employés.
- Cour de cassation (rapports annuels, données QPC) : non lus ; 02 signale déjà le site comme inaccessible aux outils.
- Conseil constitutionnel, page de statistiques QPC : adresse introuvable (page d'erreur).
- Statistiques des tribunaux administratifs sur l'article L. 522-3 : absentes des cinq bilans consultés.
- Aucune adresse électronique ni aucune donnée personnelle n'a été employée ; aucun service exigeant une adresse n'a été utilisé ; aucun site de copies illicites n'a été consulté.

---

## Annexe : inventaire des sources par statut de lecture

Lu en entier (21) : discours Sauvé 2016 ; CE *Eden* n° 409678 ; CE *El Haddioui* n° 311888 ; CE n° 157621 ; CE n° 225827 ; CE n° 493118 ; CE *Dahan* n° 347704 ; CE *Ville Nouvelle-Est* n° 78825 ; CE n° 470808 ; art. L. 10 CJA ; art. L. 111-13 COJ ; art. 226-18, 226-24 et 226-31 du code pénal (trois) ; art. 35 de la Convention européenne ; synthèse Contamin et al. 2007 ; Spire et Weidenfeld 2019 ; Gautron et Retière 2013 ; CEDH *Statistics 2025* (une page) ; RSJ 2026 fiche 4.7 ; règle 47 du règlement de la CEDH.

Extraits lus (21) : Latour, chapitre 5 en anglais ; Cohen et Pasquino 2013 ; rapport complet Contamin et al. et annexe 2010 ; rapport public 2025 du Conseil d'État ; cinq bilans de tribunaux administratifs interrogés en plein texte (Montpellier 2023 et 2024, Pau 2024, Bordeaux 2024, Châlons-en-Champagne 2024) ; conclusions sur CE n° 470808 ; Cons. const. n° 2019-778 DC ; Bastard, Mouhanna et al. 2019 ; IERDJ 2024 ; RSJ 2026 fiche 4.4 ; Dalmasso, Signoretto et al. 2023 ; Cahuc et al. 2020 ; Sommer et Munoz-Perez 2014 ; Munoz Perez et Serverin 2020 ; CEDH *Analysis of Statistics 2025* ; fiche pays France ; tableau des violations 2025.

Résumé lu ou analyse officielle lue (20) : analyses officielles de CE n° 352427, n° 405473, n° 386400, n° 317314, n° 303821, n° 510367, n° 424336, n° 307036, n° 428231, n° 376598, n° 475636 ; compte rendu Dauphin 2014 (Collectif Onze, première page) ; résumés de Voeten 2008, Madsen 2015, Lochak 2007, Bui-Xuan 2007, Renaud 2026, Dalmasso et Signoretto 2022, Leroy 2021 (thèse) ; notice de Pinat 2015.

Outil de synthèse (3) : Pougnet 2026 ; plan de l'article de la *RDP* 2018 attribué à Rouillier ; version publiée de Cahuc et al. (*JEEA*, 2024), connue par moteur de recherche.

Non vérifié (12) : Latour 2002 (livre) ; Spire et Weidenfeld 2011 (*Droit et Société*) ; Lochak 1972 ; Bastard et Mouhanna 2007 ; Collectif Onze 2013 (livre) ; Serverin 2019 ; France Stratégie 2024 ; Rouillier 2018 (texte) ; CE, Sect., *Finamur*, n° 412560 ; CE, Ass., *Bonnemaison*, n° 381245 ; Falconi et Lemercier 2023 ; rapports annuels de la Cour de cassation.
