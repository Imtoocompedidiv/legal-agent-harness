---
name: controle-avant-depot
description: "Contrôle obligatoire de toute écriture avant dépôt ou envoi décisif : fiche, lecture à froid, contradiction, sources, gate.py jusqu'au PASS, finalisation, accord exprès du client."
---

# Contrôle avant dépôt

Le contrôle mécanique transforme en blocages les fautes qui font trier une requête ou perdre une instance : mauvais acte attaqué, fait postérieur à l'acte, condition non prouvée, conclusions inaccordables, cascade de subsidiaires, moyen présenté comme une hypothèse, citation non lue, pièce absente, objection dirimante laissée ouverte, lecteur à froid qui ne comprend pas la demande. Il ne remplace pas le jugement ; il empêche de déposer sans l'avoir exercé.

## 1. Fiche de l'acte

Fichier `ecritures/controle/<nom du brouillon sans extension>.fiche.json`. Champs :

- `type_acte` : un régime de `scripts/gate.py` ou des fichiers `references/domaines/*_regimes.json` (civil, référés, travail, commercial, procédures collectives, exécution, pénal, administratif général et spécial). `python gate.py --regimes` les liste avec leurs conditions ; une condition qui manque à la fiche bloque, avec la sanction qu'elle entraîne.
- `question` : la question soumise au juge, en une phrase ; elle doit se retrouver en première page.
- `fait_decisif` : le fait qui fait basculer l'affaire ; il doit se retrouver en première page (référés).
- `faits_decisifs` : identifiants, dans `preuves/matrice.json`, des faits que l'écriture présente comme décisifs. Chacun doit y renvoyer à un extrait littéral d'une pièce analysée (skill `analyse-documentaire`) ; sinon le contrôle bloque. Chaque fait d'une condition ou d'un moyen porte de même le champ `matrice`.
- `au_nom_du_client` : vrai si le texte est signé par le client (contrôle de ses consignes de ponctuation).
- `actes_attaques` : liste d'objets `id`, `designation`, `date` (AAAA-MM-JJ), `auteur`, `auteur_competent`, `qualification` (decision_expresse, decision_implicite, confirmative, preparatoire, information, mesure_ordre_interieur, refus_de_rendez_vous), `justification`, `sources` (identifiants du registre). Plusieurs actes en référé exigent `justification_pluralite_actes`.
- `conditions` : une entrée par condition du régime, avec `condition`, `etat` (etablie, fragile, absente), `faits` (objets `fait`, `date`, `pieces`), `sources`, et `objection` (identifiant au registre) si l'état est fragile.
- pour la condition d'urgence d'un référé administratif : `interet_public_adverse` (l'intérêt que la défense opposera à la suspension, ou « aucun » avec sa raison) et `bilan` (pourquoi la balance penche pour la suspension, pièces à l'appui ; CE, Sect., 28 février 2001, n° 229562) ; sans eux, le contrôle bloque.
- `moyens` : `intitule`, `fondement`, `faits` datés avec pièces, `actes_vises`, `sources`, et si un fait postérieur à l'acte est invoqué, `admet_faits_posterieurs` avec `justification_faits_posterieurs` sourcée.
- `conclusions` : `texte` et `pouvoir_du_juge` (ce qui permet à ce juge de l'ordonner à ce stade, avec sa source).
- `requete_fond_distincte` : `reference` et `piece`, pour un référé-suspension.
- `delai` : `echeance` (AAAA-MM-JJTHH:MM), `regle`, `point_de_depart`, et `evenement`, identifiant de l'événement de `chronologie/chronologie.json` qui fait courir le délai (types et attributs donnés par `voies.py --types`). Le contrôle recalcule alors l'échéance par `voies.py` et bloque si elle tombe plus tôt que l'échéance déclarée ou si elle est dépassée ; `regle_calcul` restreint le recalcul à une règle (mot du libellé ou du texte).
- `numeros_non_jurisprudentiels` : numéros qui ressemblent à des décisions sans en être (numéros de dossier, de recommandé), pour ne pas les confondre avec des citations.
- `date_droit_applicable` (AAAA-MM-JJ) : date à laquelle se lisent les textes cités ; `dates_utiles` : la date propre d'un article quand elle diffère, sous la clé « <code>|<article> » (recevabilité à l'enregistrement de la requête, légalité à la date de l'acte, voie de recours selon la disposition transitoire).
- `urgence_amiable` : `motif` et `source`, quand l'acte doit partir avant que les voies amiables aient été examinées (skill `negociation-et-persuasion`) ; le contrôle n'émet alors qu'une alerte, et le plan s'écrit dès l'acte déposé.

## 1 bis. Préalables exigés par le contrôle

Pour toute écriture juridictionnelle, `gate.py` bloque tant que manquent : les canaux de notification relevés dans leur fréquence (`etat/canaux.json`, `affaire.py canal controle`) ; un audit de terrain récent (`terrain/audit.json`, moins de trois jours pour un référé, quatorze sinon, skill `action-sur-le-reel`) ; une ligne stratégique complète et postérieure à la dernière pièce citée (`strategie/ligne.json`, skill `strategie-contentieuse`) ; une revue de charpente du dossier entier par l'`architecte-strategique`, postérieure à la ligne, couvrant l'acte, sans point dirimant ouvert ; le récit (`<nom>.recit.json`) et sa lecture par le `lecteur-profane` sur l'empreinte exacte (skill `recit-judiciaire`) ; le profil des décideurs (`strategie/decideurs.json`, skill `lecture-des-decideurs`), valide, de moins de 180 jours, couvrant l'acte, désignant la juridiction qui le recevra avec un calibrage qui montre ce qui passe et ce qui échoue devant elle, et antérieur à la ligne ou inscrit dans `profil_decideurs_applique`; le plan de négociation (`strategie/negociation.json`, skill `negociation-et-persuasion`, sous-agent `negociateur`), valide, couvrant l'acte, postérieur à la ligne ou inscrit dans `ligne_examinee`, sans préalable amiable obligatoire non tenté, sauf urgence motivée dans la fiche (`urgence_amiable`) ; l'écrit ne contient aucun chiffre de la négociation (point de réservation, cible, concession) et mentionne les diligences amiables que la loi exige. Un moyen qui s'appuie sur une déclaration de l'adversaire la référence dans la fiche (`declarations_adverses`) ; le registre `adverse/declarations.json`, tenu par l'`analyste-adverse`, doit en donner le paragraphe entier et les autres pièces du même auteur lues, et ne pas la dire contredite.

## 1 ter. Preuve documentaire

Le contrôle documentaire (`pieces.py`, appelé par `gate.py`) bloque un fait décisif non rattaché à la matrice, absent de la matrice, sans extrait littéral conforme d'une pièce analysée et à jour, seulement allégué, contredit par une pièce, ou dit corroboré sur une seule pièce. Il alerte sur un fait décisif contesté, établi seulement par des extraits lus sur image, reposant sur une pièce qui porte une anomalie majeure ou dont aucune pièce n'est citée, sur les faits de conditions et de moyens sans renvoi à la matrice, et sur toute pièce citée sans fiche d'analyse à jour et valide. `python "${CLAUDE_PLUGIN_ROOT}/scripts/pieces.py" controle <brouillon>` donne ces constats seuls.

## 1 quater. Requête conservatoire

Quand le délai d'une requête au fond expire dans les 72 heures, ne pas perdre le délai pour une pièce ou une lecture qui peut suivre. La fiche porte alors `conservatoire` :
- `echeance` (AAAA-MM-JJTHH:MM) ;
- `memoire_complementaire` (date, dans les trente jours) ;
- `pieces_a_produire`.

La requête contient au moins un moyen, puisqu'une requête sans moyen ne se régularise que jusqu'à l'expiration du délai (CJA, art. R. 411-1). Le contrôle diffère alors au mémoire complémentaire les constats que la procédure permet de régulariser ou d'apporter ensuite : pièces, faits encore allégués, lectures indépendantes, campagne, intérêt et qualité. Les irrecevabilités régularisables le restent sur invitation du juge (CJA, art. R. 612-1). Le titre exigé par l'article R. 600-4 du code de l'urbanisme en est un exemple (CE, 3 juillet 2020, n° 424293), mais il ne peut pas être produit pour la première fois en appel (CE, 22 avril 2022, n° 451156).

Restent bloquants le délai, la compétence, l'acte attaquable et le préalable obligatoire. Le mode est refusé pour un référé, qui est jugé sur ce qu'il contient. Le mémoire complémentaire passe le contrôle entier.

## 1 quinquies. Lectures

Le contrôle des lectures (`lectures.py`, appelé par `gate.py`) confronte l'écriture au registre des lectures que le hook tient dans `recherche/lectures/` (skill `recherche-juridique`). Il bloque :
- une décision citée jamais lue par `get_decision` ;
- une décision citée dont la suite connue (`standing`, `case_chronology`) montre une annulation, une cassation ou une infirmation que l'écriture ne dit pas ;
- une citation attribuée à une décision, à un article ou à une pièce qui ne se retrouve pas mot pour mot dans la source lue, ou qui ne se lit que dans un aperçu de recherche ;
- un article dont le texte est nommé et qui n'a pas été lu dans la version applicable à la date utile ;
- une capture du registre altérée ou écrite à la main.

Il alerte sur la section d'un article cité restée non lue, ses renvois non suivis, l'absence de recherche par `legal_article`, une date utile non déclarée pour un texte qui a connu plusieurs versions, une citation non attribuée et introuvable, attribuée à une autre source que celle où elle se lit, prise dans le sommaire ou dans une version inapplicable, une décision sans suite connue, une décision défaite que l'écriture signale, un article dont le texte n'est pas identifié, et une décision déclarée lue dans `etat/sources.json` sans capture au registre. Pour un écrit qui n'est pas porté devant un juge, les blocages deviennent des alertes. `python "${CLAUDE_PLUGIN_ROOT}/scripts/lectures.py" couverture|citations|portee <brouillon>` donne ces constats seuls.

## 2. Registres

Inscrire chaque décision et chaque texte cités dans `etat/sources.json`, lus en entier, avec leur portée exacte ; `lu_en_entier` n'est vrai que si le registre des lectures capture leur texte (sous-agent `verificateur-sources` pour un contrôle indépendant). Coter chaque pièce citée par `affaire.py piece ajouter`. Inscrire les objections dirimantes connues par `affaire.py objection ajouter`.

## 3. Lecture à froid

Produire l'extrait de tri et l'empreinte par `affaire.py extrait-tri <brouillon>`. Préparer le dossier du délibéré : le calibrage équilibré de la juridiction (`juridiction.py calibrage --avant <jour du dépôt>`, depuis la base ouverte pour une juridiction administrative, ou depuis un relevé de décisions LibreJustice antérieures au dépôt pour toute juridiction, selon `lire_releve`), qui montre en nombre égal ce que la juridiction refuse et ce qu'elle accueille, au filtre et après instruction, avec ses taux publiés, sans aucune décision du jour du dépôt ni postérieure ni la décision de l'affaire, sans nom de magistrat ni décompte par juge ; la fiche du décideur (`decideurs.py fiche-juge`, `procedure/calibrage_decideur_<id>.md`), dont le juge simulé reporte l'empreinte ; les conditions du régime (`juridiction.py conditions --type <type_acte>`) ; la défense écrite par le sous-agent `avocat-adverse`, qui ne voit que l'acte et les pièces. Lancer d'abord le sous-agent `rapporteur-simule` : il instruit condition par condition, lit les textes à la source à la date utile, fixe le standard de contrôle et la charge de la preuve, prend les pièces telles que l'acte les décrit quand elles ne sont pas jointes, et écrit `ecritures/controle/<nom>.rapport_rapporteur.json` avec un projet et son contre-projet. Lancer ensuite le sous-agent `juge-simule`, qui délibère en formation sur l'extrait, l'acte, les pièces, la défense (après le filtre quand celui-ci statue sans elle) et le rapport, et écrit `ecritures/controle/<nom>.lecture_froid.json`. Ni l'un ni l'autre ne lit de décision de justice : ils ne peuvent pas retrouver l'affaire. Ne leur donner ni nos notes, ni la fiche, ni notre espoir. Le hook n'autorise que le rapporteur à écrire son rapport, que le juge simulé à écrire la lecture à froid et que le contradicteur à écrire la contradiction ; la session principale peut seulement porter le statut des points tranchés. Si l'écriture d'un sous-agent est refusée, vérifier que le dossier n'est pas rangé dans le répertoire du plugin, que Claude Code protège.

Le juge simulé est un garde-fou, pas un oracle. Sur vingt décisions réelles neuves reconstituées à l'aveugle, il a prédit l'issue dans seize cas et reconnu quatre succès sur six (`validation/PROTOCOLE.md`) ; il se trompe encore sur la pesée des faits et sur la part d'un accueil partiel. Le calibrer toujours par `juridiction.py calibrage`, jamais par les seules ordonnances de tri, qui lui apprennent la sévérité sans lui montrer ce qui passe. Son issue favorable ne lève jamais un bloquant, et son issue défavorable en crée un.

## 4. Contradiction

Lancer le sous-agent `contradicteur` sur le brouillon, les pièces et les textes ; il écrit `ecritures/controle/<nom>.contradiction.json` avec des points numérotés. Pour chaque point, décider : couper, garder, reformuler. Appliquer, puis porter le `statut` à `applique` ou `rejete_motive` avec le motif. Une objection n'ajoute jamais une branche subsidiaire de précaution. Une objection qui peut faire trier ou perdre et qu'on ne sait pas résoudre devient une objection dirimante au registre et une question au client, posée en clair, avec la réponse recommandée.

## 4 bis. Arbitrage et nombre de passes

Les relecteurs (`contradicteur`, `avocat-adverse`, `juge-simule`, `verificateur-sources`) travaillent en parallèle, sans se lire. Leur brief présente la thèse à la troisième personne et ensemble avec la thèse adverse, sans marque d'auteur ni préférence. L'arbitrage suit des règles fixées d'avance : une objection appuyée sur un passage lu et touchant la recevabilité, une condition du régime ou une source est retenue sauf réfutation par une autre source ; une objection sans preuve est écartée avec mention ; le fond prime la forme. Une nouvelle passe de révision n'a lieu que sur un signal externe (source, pièce, résultat d'outil) ; après deux cycles, les points encore ouverts vont au client avec leur état et la recommandation. Les décisions d'arbitrage s'écrivent dans `ecritures/controle/<nom>.decisions.md`.

## 5. Contrôle

`python "${CLAUDE_PLUGIN_ROOT}/scripts/affaire.py" controle ecritures/brouillons/<nom>.md` écrit le verdict lié à l'empreinte. Corriger jusqu'au PASS. Toute correction change l'empreinte : refaire la lecture à froid sur la version finale. Les alertes se lisent une à une ; une alerte acceptée se justifie au journal.

## 6. Finalisation et dépôt

`affaire.py finaliser` copie la version contrôlée dans `ecritures/FINAL/`. Le dépôt, la délivrance ou l'envoi n'a lieu qu'après l'accord exprès du client pour cet acte précis, recueilli dans le message et consigné par `affaire.py depot <final> --accord "ses mots" --canal ...`. La preuve de dépôt devient une pièce. Le verdict PASS atteste des verrous mécaniques ; il ne garantit ni la justesse juridique ni l'issue, et ne se présente jamais au client comme une garantie.
