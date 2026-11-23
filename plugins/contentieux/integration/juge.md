# Intégration de la refonte de la simulation des juges

## Diagnostic des erreurs mesurées

Relu pour chaque erreur du juge simulé dans les mesures antérieures à la refonte : l'acte reconstitué, la lecture (motifs, premier considérant, hésitations), la défense, et les textes en cause. La décision réelle n'a pas été lue : la catégorie vient des fichiers de score, et la cause est établie sur ce que le juge simulé a écrit au regard du droit applicable.

| Cas | Erreur | Cause principale | Cause secondaire |
| --- | --- | --- | --- |
| ADS-08 (dev) | succès méconnu, trois lectures sur cinq | standard : en référé précontractuel, procédure inquisitoire, il exige du requérant la preuve du contenu de l'offre de l'attributaire, que seule la commune détient | absence de pièce (notation par sous-critères) |
| ECO-08 (dev) | succès méconnu, constant | standard : la contestation sérieuse est appréciée en faisant peser sur le salarié la preuve de la fourniture du travail, qui pèse sur l'employeur ; demande non chiffrée tenue pour rédhibitoire en procédure orale | absence de pièce |
| PEN-08 (dev) | succès méconnu, quatre lectures sur cinq | droit : suspension de la prescription par le délai de l'article 85 du code de procédure pénale après la loi du 27 février 2017, et calcul refait au stade de la non-admission sans trancher l'article 801 | sévérité du filtre |
| ECO-07 (dev) | faux succès, constant | absence de pièce : la date du premier incident non régularisé est dans l'historique de compte, non joint | standard : forclusion d'ordre public tranchée sur un calcul tiré de l'acte |
| CIV-08 (test) | faux succès | droit : la commission départementale de conciliation assimilée aux modes de règlement amiable de l'article 750-1 du code de procédure civile, liste fermée | |
| PEN-01 (test) | faux succès, une lecture | droit : l'article 85 exige la plainte préalable de la personne qui se constitue partie civile | |
| CIV-06 (test) | faux succès | fait : motif légitime admis sur la seule plausibilité de l'action, les éléments opposés par l'assureur tenus pour inexistants faute de pièce | absence de pièce côté défense |
| ECO-05 (test) | faux succès | absence de pièce côté défense : contestation des factures écartée parce que la défense simulée n'a pas de pièce | standard : seuil de la contestation sérieuse en référé-provision |
| ECO-09 (test) | succès méconnu | absence de pièce : omission de la liste des créanciers exigée en preuve, alors que le juge-commissaire dispose de la liste | standard : dossier de la juridiction |
| CIV-09 (test) | succès méconnu, une lecture | absence de pièce (procès-verbal de constat) | standard : latitude du juge de l'article 835 dans le choix de la mesure |
| IND-P09 (indépendant) | succès méconnu, constant | standard : référé précontractuel rejeté pour insuffisance de la requête alors que l'acheteur détient l'analyse des offres | absence de pièce |
| IND-P10 (indépendant) | succès méconnu, une lecture | sévérité du filtre (référé-liberté) | |
| IND-C08 (indépendant) | succès méconnu, une lecture | fait : transmission de la créance au sein d'un groupe exigée en preuve et irrecevabilité prononcée là où le juge rouvre les débats | absence de pièce |
| CONF-C05 (confirmation 1) | succès méconnu | standard : accueil partiel (deux créances sur trois, résiliation judiciaire subsidiaire) traduit en échec | |
| CONF-C06 (confirmation 1) | faux succès | fait : copie de requête au tampon de 2022 préférée à l'enregistrement du greffe en 2024 | |
| CONF-P02 (confirmation 1) | succès méconnu | sévérité du filtre : second référé-suspension trié malgré une motivation préfectorale fragile et l'urgence présumée | aucun calibrage |
| CONF-P03 (confirmation 1) | succès méconnu | sévérité du filtre : référé mesures utiles (rendez-vous en préfecture) trié pour urgence | aucun calibrage montrant la pratique d'accueil |
| CONF-P09 (confirmation 1) | faux succès | droit : champ d'application dans le temps de l'article 59, VI, de la loi du 22 décembre 2021, non lu (le juge ignorait si le texte disait « sous écrou » ou « incarcérées ») | |
| CONF2-P06 (confirmation 2) | succès méconnu | droit : défaut d'examen d'une procédure de séjour pendante dans un autre État membre | absence de pièce détenue par l'administration (procès-verbal d'audition) |
| CONF2-P08 (confirmation 2) | succès méconnu | standard : proportionnalité de la révocation appréciée comme si tous les griefs étaient établis, alors que la matérialité incombe à l'administration | |
| CONF2-P10 (confirmation 2) | faux succès | droit : articles 371 et 371-1 du code de procédure pénale sur la formation qui statue sur l'action civile, non lus | |

Bilan : droit mal connu 6, standard de contrôle ou charge de la preuve 5, absence de pièce 4, sévérité du filtre 3, fait mal pesé 3 ; l'absence de pièce est cause secondaire de 6 autres. Les erreurs d'une seule lecture sur la part dev (CIV-10, CIV-02, ECO-01) sont des écarts de variance, sans cause constante.

## Conception retenue et écartée

Retenu :
- **Calibrage équilibré** (`juridiction.py calibrage`) : refus au filtre, refus et accueils après instruction en nombre égal, taux observés et décomptes publiés, borne stricte avant le jour du dépôt, décision de l'affaire exclue. Il répond à la sévérité du filtre et à l'absence de repère sur ce qui passe.
- **Délibéré en deux temps** : `rapporteur-simule` instruit condition par condition (conditions du régime données par `juridiction.py conditions`), lit les textes à la date utile, fixe le standard et la charge de la preuve, pèse la défense et propose un projet et un contre-projet ; `juge-simule` délibère en formation, suit ou écarte le rapporteur condition par condition et répond au contre-projet. Sur la part dev, la formation s'est écartée trois fois du projet du rapporteur, deux fois à juste titre (ADS-08, CIV-04) et une fois à tort (PEN-04) : son indépendance est gardée.
- **Textes, jamais décisions** : les deux simulateurs ont `get_norm` et `search_norms`, ni `search_decisions` ni `get_decision`, pour ne pas retrouver l'affaire. Répond au droit mal connu quand la lettre du texte décide (liste fermée, champ dans le temps, formation compétente).
- **Règles de preuve écrites** : procédure inquisitoire (pièce détenue par l'adversaire, allégations précises non contredites, jurisprudence Barel), charge selon la loi en procédure accusatoire, pièce décrite par sa nature, sa date et son auteur présumée dire ce que l'acte lui attribue, silence de l'acte non comblé en faveur du demandeur, registre du greffe et constatations de la décision attaquée au-dessus d'une copie de partie.
- **Filtre au critère légal**, sans position par défaut ; la défense lue après le filtre quand celui-ci statue sans elle ; issue binaire jugée sur l'issue finale, l'accueil partiel substantiel compté comme succès.

Écarté :
- Le collège de lectures : déjà mesuré, il ne corrige pas des erreurs constantes.
- L'assouplissement global du filtre et les pièces tenues pour établies sans distinction (correction de 12 h 47) : plus mauvais sur la part dev ; remplacé par des règles de preuve qui disent qui doit prouver quoi.
- L'obligation pour la formation de suivre le rapporteur : sur la part dev, elle aurait coûté un cas net.
- L'accès aux décisions de justice : il permettrait de retrouver l'affaire.
- Un calibrage par la seule base ouverte administrative : elle ne couvre pas les juridictions judiciaires ni la Cour européenne ; la voie reste dans le script pour l'usage réel, la validation passe par des relevés LibreJustice.
- Une règle qui déduirait la forclusion du silence d'un prêteur sur la date du premier incident (ECO-07) : trop proche du cas pour être un principe.

## Fichiers

Module livré sans toucher aux fichiers partagés : `agents/juge-simule.md` (refondu), `agents/rapporteur-simule.md` (nouveau), `scripts/juridiction.py` (calibrage équilibré et conditions du régime), `tests/test_juge.py`. Côté validation : `validation/outils/lancer_deliberation.sh`, `lancer_defense.sh`, `BRIEF_CALIBRAGE.md`, `BRIEF_TIRAGE_CONF3.md`, `doublon.py`, et dans `pipeline.py` les seuls chemins du troisième corpus de confirmation (la logique de score n'a pas changé). Ce document donne ce que la session principale doit appliquer aux fichiers partagés.

## 1. Correctif de code : `integration/juge.patch`

Diff unifié, chemins relatifs à la racine du plugin. Depuis `plugins/contentieux` :

```
patch -p1 --binary --dry-run < integration/juge.patch
patch -p1 --binary < integration/juge.patch
python -m pytest -q plugins/contentieux/tests      (depuis la racine du dépôt)
```

`--binary` garde les fins de ligne CRLF de `hook.py`. Le correctif fait trois choses.

1. **`scripts/hook.py`** : le rapport du rapporteur ne s'écrit que par son sous-agent. Dans la boucle des rapports réservés, ajouter le couple `(".rapport_rapporteur", "rapporteur-simule")` :

       for suffixe, auteur in ((".lecture_froid", "juge-simule"), (".rapport_rapporteur", "rapporteur-simule"), (".contradiction", "contradicteur"),
                               (".lecture_profane", "lecteur-profane")):

   Sans ce changement, la session principale pourrait écrire elle-même un rapport favorable que la formation lirait.

2. **`scripts/gate.py`** : `chemins()` connaît `rapport_rapporteur`, et `controler()` bloque une lecture à froid qui n'a pas été précédée du rapport sur la même version. Juste avant le commentaire `# Contradiction close.` :

       # Délibéré en deux temps : la lecture à froid ne vaut que précédée du rapport du rapporteur sur la même version.
       rr = L.lire_json(ch["rapport_rapporteur"])
       if juridictionnel and type_acte != "conclusions":
           if rr is None:
               c("RAPPORT_RAPPORTEUR_ABSENT", "BLOQUANT", "Aucun rapport du sous-agent rapporteur-simule : la formation statuerait sans instruction "
                 "condition par condition (textes lus, standard, charge de la preuve).")
           elif rr.get("sha256") != empreinte:
               c("RAPPORT_RAPPORTEUR_PERIME", "BLOQUANT", "Le rapport du rapporteur porte sur une autre version du texte (empreinte différente).")

   Ces constats n'ont pas de catégorie : ils ne changent pas la mesure V2.

3. **`tests/test_contentieux.py`** : le référé conforme écrit aussi un rapport sur la même empreinte, le test des rapports réservés vérifie que seul le rapporteur écrit le sien (le juge simulé non plus). `tests/test_juge.py::TestIntegration`, ignoré tant que le correctif n'est pas appliqué, devient actif ensuite.

Vérification faite le 18 novembre 2026 à 18 h 12 : le correctif s'appliquait sans décalage sur une copie du plugin courant, et la suite complète y passait (113 tests, dont `TestIntegration`). Si un autre module a modifié entre-temps les mêmes lignes, appliquer à la main les changements ci-dessus ; chaque emplacement est donné par la ligne qui le précède.

## 2. Textes des skills et de la documentation

À remplacer mot pour mot (les fichiers bougent sous d'autres modules, d'où un remplacement par passage plutôt qu'un diff).

**`skills/controle-avant-depot/SKILL.md`, section 3, premier paragraphe** (de « Produire l'extrait de tri » à « que Claude Code protège. ») :

> Produire l'extrait de tri et l'empreinte par `affaire.py extrait-tri <brouillon>`. Préparer le dossier du délibéré : le calibrage équilibré de la juridiction (`juridiction.py calibrage --avant <jour du dépôt>`, depuis la base ouverte pour une juridiction administrative, ou depuis un relevé de décisions LibreJustice antérieures au dépôt pour toute juridiction, selon `lire_releve`), qui montre en nombre égal ce que la juridiction refuse et ce qu'elle accueille, au filtre et après instruction, avec ses taux publiés, sans aucune décision du jour du dépôt ni postérieure ni la décision de l'affaire, sans nom de magistrat ni décompte par juge ; la fiche du décideur (`decideurs.py fiche-juge`, `procedure/calibrage_decideur_<id>.md`), dont le juge simulé reporte l'empreinte ; les conditions du régime (`juridiction.py conditions --type <type_acte>`) ; la défense écrite par le sous-agent `avocat-adverse`, qui ne voit que l'acte et les pièces. Lancer d'abord le sous-agent `rapporteur-simule` : il instruit condition par condition, lit les textes à la source à la date utile, fixe le standard de contrôle et la charge de la preuve, prend les pièces telles que l'acte les décrit quand elles ne sont pas jointes, et écrit `ecritures/controle/<nom>.rapport_rapporteur.json` avec un projet et son contre-projet. Lancer ensuite le sous-agent `juge-simule`, qui délibère en formation sur l'extrait, l'acte, les pièces, la défense (après le filtre quand celui-ci statue sans elle) et le rapport, et écrit `ecritures/controle/<nom>.lecture_froid.json`. Ni l'un ni l'autre ne lit de décision de justice : ils ne peuvent pas retrouver l'affaire. Ne leur donner ni nos notes, ni la fiche, ni notre espoir. Le hook n'autorise que le rapporteur à écrire son rapport, que le juge simulé à écrire la lecture à froid et que le contradicteur à écrire la contradiction ; la session principale peut seulement porter le statut des points tranchés. Si l'écriture d'un sous-agent est refusée, vérifier que le dossier n'est pas rangé dans le répertoire du plugin, que Claude Code protège.

**Même section, second paragraphe** (« Le juge simulé est un garde-fou… ») : voir la section 4 ci-dessous pour les chiffres à y porter.

**`skills/recit-judiciaire/SKILL.md`**, la ligne « 3. Lecture de tri par `juge-simule`, calibré par `procedure/exemples_tri_<code>.md`… » devient :

> 3. Lecture de tri par `rapporteur-simule` puis `juge-simule`, calibrés par `procedure/calibrage_<code>.md` (`juridiction.py calibrage`), qui montre ce que la juridiction refuse et ce qu'elle accueille.

**`skills/prise-en-main-affaire/SKILL.md`**, puce « Juridiction », fin de phrase « et extrait les motifs littéraux de ses ordonnances de tri pour calibrer le juge simulé. » devient :

> et écrit le calibrage équilibré du juge simulé (`procedure/calibrage_<code>.md` : refus et accueils en nombre égal, au filtre et après instruction, avec les taux publiés). Pour une juridiction judiciaire ou européenne, `juridiction.py calibrage --decisions <relevé> --avant <jour du dépôt>` construit le même calibrage depuis des décisions relevées sur LibreJustice.

**`README.md`** : ajouter `rapporteur-simule` après `juge-simule` dans la liste des sous-agents ; la puce `scripts/juridiction.py profil` devient :

> - `scripts/juridiction.py` calibre le juge simulé sur la juridiction réelle. `profil` tire de la base ouverte de la justice administrative les décisions publiées, classe ce qu'elle trie, instruit et accorde, par juge désigné ; `calibrage` écrit `calibrage_<code>.md`, qui montre en nombre égal refus et accueils, au filtre et après instruction, avec les taux publiés, depuis la base ouverte ou depuis un relevé LibreJustice, borné strictement avant le jour du dépôt et la décision de l'affaire exclue ; `conditions` écrit les conditions du régime remises au rapporteur.

**`docs/ARCHITECTURE.md`**, puce « Le juge simulé contradictoire et calibré » :

> - **Le juge simulé délibère en deux temps.** Le `rapporteur-simule` instruit condition par condition (texte lu à la source à la date utile, standard de contrôle, charge de la preuve, pièces telles que l'acte les décrit, défense) et propose un projet et son contre-projet ; le `juge-simule` délibère en formation sur ce rapport, après la défense écrite par l'avocat adverse quand son stade la comporte. Tous deux se calibrent sur des décisions de la juridiction qui montrent autant de refus que d'accueils, avec les taux publiés (`juridiction.py calibrage`, borné avant le dépôt, la décision de l'affaire exclue), et ne lisent que des textes, jamais des décisions. Une issue défavorable bloque le dépôt, quel que soit l'acte.

**`templates/affaire/LISEZMOI.md`**, après la ligne `procedure/profil_<code>.md` :

> | `procedure/calibrage_<code>.md` | calibrage équilibré du juge simulé : refus et accueils, taux publiés, borné avant le dépôt | `juridiction.py calibrage` |
> | `procedure/conditions_<type>.md` | conditions du régime remises au rapporteur simulé | `juridiction.py conditions` |

## 3. Compatibilité avec le module des décideurs

`decideurs.py fiche-juge` écrit `procedure/calibrage_decideur_<id>.md` et exige `profil_decideur_sha256` dans la lecture à froid. La section 5 de `integration/decideurs.md` est intégrée à `agents/juge-simule.md`, car elle s'accorde avec la refonte : la fiche se lit en entier avant l'acte, le taux de base retenu s'écrit avant la lecture de l'acte (fiche du décideur, à défaut calibrage), le juge s'en écarte condition par condition en nommant la pièce ou la règle, et la sortie porte `taux_de_base_retenu` et `profil_decideur_sha256`. Le rapporteur lit aussi la fiche. Les deux calibrages se complètent : la fiche donne le standard et la culture de la formation, `calibrage_<code>.md` des décisions réelles des deux issues. Ce qui a été mesuré le 18 novembre ne comportait ni fiche du décideur ni champ `taux_de_base_retenu` (`validation/PROTOCOLE.md`, modifications postérieures à la mesure).

Interdiction légale respectée (CJA, art. L. 10, al. 4 ; COJ, art. L. 111-13) : les suppressions apportées le 18 novembre à 17 h 30 (champ `juge` de `classer`, section « Par juge désigné », colonne « Juge », amende pour recours abusif comptée comme accueil) sont conservées ; `retirer_noms` purge des extraits cités les noms précédés d'une civilité ou d'une qualité ; le rapporteur et le juge simulé ne reçoivent aucune donnée par juge et ont l'interdiction écrite de nommer, évaluer ou comparer un magistrat. La remarque du module des décideurs sur la classe de référence est prise en compte en partie : `calibrage --procedure L. 521-1` ne garde que les décisions qui visent l'article de la procédure, et les taux sont déjà séparés par stade ; la séparation par auteur de l'acte attaqué reste à faire.

## 4. Mesure

Détail dans `validation/PROTOCOLE.md` (avenant de 17 h 52 et résultat de 18 h 04). Part dev, une lecture : 21 issues justes sur 24, 7 succès reconnus sur 8 (avant la refonte : 21 et 6). Troisième corpus de confirmation, vingt cas neufs mesurés une fois : 16 issues justes sur 20 (80 %), 4 succès reconnus sur 6 (67 %), interception 14 sur 14 (stricte 13 sur 14) avec une seule catégorie signalée en plus par échec.

**Second paragraphe de la section 3 de `controle-avant-depot`**, à remplacer par :

> Le juge simulé est un garde-fou, pas un oracle. Sur vingt décisions réelles neuves reconstituées à l'aveugle, il a prédit l'issue dans seize cas et reconnu quatre succès sur six (`validation/PROTOCOLE.md`) ; il se trompe encore sur la pesée des faits et sur la part d'un accueil partiel. Le calibrer toujours par `juridiction.py calibrage`, jamais par les seules ordonnances de tri, qui lui apprennent la sévérité sans lui montrer ce qui passe. Son issue favorable ne lève jamais un bloquant, et son issue défavorable en crée un.

**`docs/ESSAIS.md`**, section à ajouter après la section 9 :

> ## 10. Refonte de la simulation des juges (18 novembre, 16 h à 18 h)
>
> Diagnostic des vingt et une erreurs du juge simulé relevées depuis la première mesure : droit mal connu faute de lire les textes (6), standard de contrôle ou charge de la preuve mal appliqués (5), absence de pièce (4), sévérité du filtre sans exemple de ce qui passe (3), fait mal pesé (3). Réponse : calibrage équilibré de la juridiction, borné avant le dépôt ; rapporteur qui instruit condition par condition, textes lus à la date utile ; formation qui délibère sur son rapport ; règles de preuve écrites ; accès aux textes seuls. Part dev : 21 issues justes sur 24 et 7 succès reconnus sur 8 (auparavant 21 et 6), les deux erreurs constantes ADS-08 et ECO-08 corrigées. Troisième corpus de confirmation, vingt cas neufs tirés et reconstitués à l'aveugle, mesuré une fois : 16 sur 20 et 4 succès sur 6, au-dessus des deux seuils. Restent faibles la pesée des faits sans pièce, la qualification d'un accueil partiel et les questions de droit que la lettre des textes ne tranche pas.

## 5. Ce qui reste faible

- **La pesée des faits sans pièce.** La présomption qu'une pièce décrite dit ce que l'acte lui attribue a corrigé ADS-08 et ECO-08, mais elle a fait accorder CONF3-C06 à un professionnel qui devait prouver les conditions de la protection. La défense simulée n'a jamais de pièce, alors que l'adversaire réel en a : les contestations réelles (ECO-05, CONF3-C09) restent sous-estimées.
- **L'accueil partiel.** La règle binaire (succès si la juridiction accorde une part substantielle) a joué dans les deux sens sur le troisième corpus : une provision réduite comptée comme succès (CONF3-C09), une indemnité partielle comptée comme échec (CONF3-P09).
- **Les questions de droit ouvertes.** Quand la solution tient à une interprétation que la lettre ne donne pas (PEN-08 : suspension de la prescription par le délai de l'article 85 après 2017), lire le texte ne suffit pas ; l'accès aux décisions est refusé par construction.
- **La formation et son rapporteur.** Ils se valent sur l'ensemble (37 issues justes sur 44 chacun) ; la formation corrige le rapporteur deux fois et le dégrade deux fois (PEN-04, CONF3-C09).
- **L'échelle.** Vingt cas, dont six succès : l'intervalle reste large, et le troisième corpus compte six échecs « mal fondé » sur sept en droit public et pénal, ce qui ne teste guère les fins de non-recevoir de ce côté.
- **Le calibrage judiciaire** dépend d'un relevé fait par un agent sur LibreJustice ; les étiquettes de la base se trompent souvent et la première instance publiée est rare avant 2024 (ECO-01, ECO-08, ADS-06 calibrés sur d'autres juridictions ou sur des décisions anciennes).
