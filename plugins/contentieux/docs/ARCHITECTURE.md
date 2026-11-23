# Note d'architecture du plugin contentieux

## Objet

Le moteur `legal_harness` existant (serveur MCP, miroir DILA, analyses relues par deux familles de modèles) produit des consultations sourcées. Il ne contrôle ni la conduite d'un contentieux, ni la construction d'une écriture, ni la mémoire d'un dossier sur plusieurs mois. L'audit interne a montré que la plupart des échecs se produisent en amont des références : choix de la cible, lecture des pièces, autorisations, délais, canaux de notification, composition des écritures. Le plugin couvre cet amont et réutilise le moteur pour les sources.

## Principe directeur

Une règle écrite en prose ne tient pas au moment où le modèle répond : la règle de recherche personnelle existait depuis le 6 novembre et l'audit relève quinze récidives en dix jours. Les règles dont la violation a coûté une instance deviennent donc des contrôles exécutés par le harnais, hors du bon vouloir du modèle. Le jugement juridique reste au modèle et au client ; les verrous empêchent de déposer, de conclure ou de terminer sans l'avoir exercé.

## Couches

| Couche | Rôle | Fichiers |
| --- | --- | --- |
| Constitution du dossier | une page de règles stables, chargée à chaque session, non modifiable par le modèle | `templates/affaire/CLAUDE.md` |
| Skills | protocoles métier chargés à la demande selon l'acte | `skills/*/SKILL.md` |
| Sous-agents | contextes isolés pour la contradiction, la lecture à froid, la défense adverse, la recherche, la vérification, le terrain et la plume | `agents/*.md` |
| Hooks | briefing d'état, protections, contrôles mécaniques, passation | `hooks/hooks.json`, `scripts/hook.py` |
| Contrôle avant dépôt | verdict lié à l'empreinte exacte du texte | `scripts/gate.py`, `scripts/lint_ecriture.py` |
| Mémoire sur fichiers | état, registres, journal horodaté, passation | `templates/affaire/` et `scripts/affaire.py` |
| Sources | LibreJustice, miroir DILA par `legal_harness`, bases ouvertes, doctrine | serveurs MCP existants |

## Flux d'une affaire

1. **Ouverture ou reprise** (`prise-en-main-affaire`). `affaire.py init` crée l'arborescence. Au démarrage, à la reprise et après chaque compaction, le hook SessionStart injecte l'objectif, les instances, les échéances avec le temps restant, les canaux de notification en retard, les objections dirimantes, les consignes du client, la passation et la fin du journal. Le résumé de compaction ne remplace plus la relecture : l'état revient de lui-même.
2. **Réel** (`action-sur-le-reel`, `stratege-terrain`). Audit des évidences (actes, notifications, plis, réceptions), puis actions licites qui créent la preuve ou provoquent la décision attaquable, chacune validée par le client avant tout acte extérieur.
3. **Ligne** (`strategie-contentieuse`). Écrite avant toute mission : adversaire, autorité qui décide, temps réel, meilleur coup adverse, parade. Chaque acte passe le filtre en trois questions.
4. **Recherche** (`recherche-juridique`, `chercheur-juridique`, `lecteur-de-texte`, `verificateur-sources`). Ratissage par passes obligatoires (proposition et contraire, texte à la date utile, section, renvois et texte modificatif, texte spécial, dispositions transitoires, jurisprudence par article, conclusions, suite de chaque décision, meilleure autorité contraire). Le hook PostToolUse capture chaque lecture LibreJustice dans `recherche/lectures/`, signale les conclusions publiées d'une décision lue et nomme les articles qu'une vue de texte annonce sans les afficher ; `lectures.py` confronte notes et écritures à ce registre (couverture, citations mot pour mot, portée), et le contrôle avant dépôt bloque la décision jamais lue, la citation introuvable, la décision défaite tue et l'article non lu à sa date utile.
5. **Écriture** (`ecriture-juridictionnelle`, `refere-administratif`, `refere-civil`, `cassation`, `plume`). Théorie du cas, question, première page, faits datés et cotés, moyens affirmés, conclusions accordables. À chaque enregistrement, le hook PostToolUse signale les défauts mécaniques.
6. **Contrôle avant dépôt** (`controle-avant-depot`). Fiche de l'acte, extrait de tri lu par `juge-simule`, contradiction tranchée, registre des sources, `gate.py` jusqu'au PASS, `affaire.py finaliser`, accord exprès du client, `affaire.py depot`.
7. **Fin de session**. Le hook Stop refuse de terminer si le dernier message cite une pièce ou une décision ni ouverte ni inscrite comme lue, évoque les conclusions publiées d'une décision citée sans les avoir ouvertes, rend un acte destiné au juge administratif sans lecture de la compétence en premier ressort, ou si le dossier a changé sans passation réécrite (les captures du registre des lectures ne comptent pas). Une fin de tour ne se bloque qu'une fois : toutes les alertes partent ensemble.

## Choix et raisons

- **Plugin plutôt que configuration par projet.** Un seul exemplaire des skills, agents et scripts, mis à jour pour toutes les affaires ; les hooks ne s'activent que dans un dossier qui contient `etat/affaire.json`, et restent sans effet ailleurs.
- **Python, bibliothèque standard.** Les hooks démarrent en quelques dizaines de millisecondes sans environnement virtuel ; le moteur `legal_harness` garde ses dépendances.
- **Verdict lié à l'empreinte.** Une version modifiée après contrôle perd son PASS ; la lecture à froid doit porter sur l'empreinte exacte. Le verdict ne s'écrit que par `gate.py` (écriture manuelle refusée).
- **Aucun quota de longueur.** La charte de rédaction interdit d'imposer des longueurs. Les mesures (mots, pages, chefs) sont affichées pour information ; les blocages portent sur des défauts de structure constatés dans l'écriture triée.
- **Le juge simulé ne valide rien.** Au rejeu, un juge simulé non calibré a prédit une audience que la vraie juge a refusée. Il est recalibré et limité à l'extrait de tri ; son issue défavorable bloque, son issue favorable ne lève aucun bloquant.
- **Contradiction qui tranche.** Chaque point du contradicteur porte une décision ; une objection n'ajoute jamais de branche subsidiaire de précaution. Un consensus obtenu en empilant des précautions est l'échec de méthode du 12 novembre.
- **Sous-agents frais, contexte isolé.** Le contradicteur et le juge simulé ne reçoivent ni les notes ni la conclusion espérée ; le juge simulé n'a que la lecture et l'écriture de sa sortie.
- **Garde-fous fermés.** Les hooks de protection s'exécutent sans shell et avec `onFailure: block` : un script qui plante, expire ou ne démarre pas bloque l'action au lieu de la laisser passer.
- **Rapports indépendants inviolables.** Seul le sous-agent `juge-simule` peut écrire la lecture à froid, seul le `contradicteur` peut créer la contradiction ; la session principale ne peut qu'y porter le statut des points tranchés. Le juge simulé et l'avocat adverse démarrent sans la constitution de l'affaire (`omitClaudeMd`), qui leur donnerait la posture du conseil.
- **Contradictoire tranché, passes bornées.** La recherche montre que le débat entre agents jusqu'au consensus fait converger vers l'erreur par conformité et que l'autocorrection sans signal externe dégrade ; les relecteurs travaillent isolés, un arbitrage applique des règles écrites, et une nouvelle passe exige une source ou une pièce nouvelle (`docs/recherche/01`, décisions 8 et 9).
- **Complaisance traitée par la forme.** Thèse présentée aux relecteurs à la troisième personne et avec la thèse adverse, briefs sans marque d'auteur, contre-citation vérifiée avant concession (décision 11).
- **Compaction pilotée.** Le hook PreCompact dicte ce que le résumé doit garder (délais, accords du client, lectures faites et non faites) ; SessionStart réinjecte l'état calculé depuis les fichiers.
- **Confidentialité déterministe.** Les identifiants privés déclarés dans `etat/affaire.json` bloquent toute requête web ou toute recherche publique qui les contiendrait.

## Couche offensive (mise au niveau du 18 novembre)

La première version contrôlait l'erreur. La couche offensive transforme en obligations exécutées ce que la demande exigeait de proactivité et de malice :

- **Le réel obligatoire.** Aucun dépôt avec un canal de notification non relevé ou sans audit de terrain récent ; le rejeu du 12 novembre est désormais bloqué sur le courrier postal jamais relevé.
- **La ligne avant l'acte.** `strategie/ligne.json` (décideur, levier, lecture de l'adversaire, meilleur coup adverse, parade, temps réel, chemin de victoire) doit exister et être postérieure à la dernière pièce citée ; le briefing la rappelle à chaque session.
- **L'adversaire lu contre lui-même.** L'analyste adverse dresse le registre des déclarations, contradictions vérifiées dans leur contexte, silences et aveux ; un moyen qui s'appuie sur une déclaration adverse sans son contexte est bloqué, ce qui aurait empêché l'erreur de la version 2 de l'essai.
- **Le récit éprouvé.** Théorie du cas, fil, neutralisation de l'argument adverse, raison pour laquelle accorder est sûr, puis lecture d'un profane qui doit restituer le fait décisif et la demande. Aucune concession ni reconnaissance de faiblesse dans un écrit destiné au juge : le contrôle les bloque.
- **Le juge réel comme étalon.** Le profileur de juridiction extrait des décisions publiées le seuil de tri de la juridiction, jamais celui d'un magistrat, dont l'analyse des pratiques est interdite (CJA, art. L. 10, al. 4) ; le juge simulé lit ces ordonnances avant la requête.
- **La carte des délais.** Calculée depuis la chronologie et réinjectée à chaque session, avec la date prudente quand le caractère franc d'un délai est incertain.
- **La profondeur juridique.** Skills du fond (recevabilité, cause juridique, hiérarchie des demandes, concentration des moyens, exceptions et fins de non-recevoir, preuve, exécution) et du contrôle de la norme (exception d'illégalité, QPC, conventionnalité, renvoi préjudiciel), références vérifiées et marquées.

## Généralisation et mesure (18 novembre, après-midi)

- **Tout type d'affaire.** Soixante-cinq régimes, dont cinquante et un livrés par domaine (`references/domaines/*_regimes.json` : civil et référés, voies de recours, travail, commercial, procédures collectives, exécution, consommation, pénal, CEDH, QPC, administratif général, fiscal, urbanisme, étrangers, commande publique, fonction publique, responsabilité), chacun rattaché à ses textes lus. Les régimes de domaine complètent les régimes intégrés sans en retirer aucune condition. `gate.py --regimes` les liste.
- **La sanction de chaque condition.** Chaque condition porte la catégorie de rejet qu'entraîne son défaut (délai, préalable, formalité, compétence, acte non attaquable, intérêt, prescription, urgence, doute sérieux, contestation sérieuse, motif légitime, épuisement, mal-fondé) : le contrôle dit non seulement ce qui manque, mais comment l'acte serait perdu. Une condition fragile assortie de son objection donne une alerte, absente ou non traitée un blocage.
- **Le délai recalculé.** La fiche désigne l'événement de la chronologie qui fait courir le délai ; le contrôle recalcule l'échéance par `voies.py` (cent cinquante-deux règles, dont celles des domaines, bornées dans le temps quand le texte a changé, sans report au jour ouvrable pour une prescription ou devant la Cour européenne) et bloque une échéance déclarée trop tardive ou dépassée.
- **Le juge simulé délibère en deux temps.** Le `rapporteur-simule` instruit condition par condition (texte lu à la source à la date utile, standard de contrôle, charge de la preuve, pièces telles que l'acte les décrit, défense) et propose un projet et son contre-projet ; le `juge-simule` délibère en formation sur ce rapport, après la défense écrite par l'avocat adverse quand son stade la comporte. Tous deux se calibrent sur des décisions de la juridiction qui montrent autant de refus que d'accueils, avec les taux publiés (`juridiction.py calibrage`, borné avant le dépôt, la décision de l'affaire exclue), et ne lisent que des textes, jamais des décisions. Une issue défavorable bloque le dépôt, quel que soit l'acte.
- **La mesure.** Le protocole `validation/PROTOCOLE.md`, ses avenants horodatés et la chaîne `validation/outils/pipeline.py` mesurent le harness sur des décisions réelles reconstituées à l'aveugle ; les résultats sont dans `docs/ESSAIS.md`.

## La campagne avant l'acte (seconde mise au niveau, 18 novembre)

La première version jugeait la charpente autour d'un acte déjà choisi. Un avocat de premier rang prend l'affaire autrement : il établit la vérité sur pièces, éprouve sa théorie contre celle de l'adversaire et contre la lecture banale qu'en fera le juge, puis conçoit la campagne entière depuis le premier acte adverse, avant de choisir un acte. Le diagnostic est dans `docs/MISE_AU_NIVEAU_2.md`.

- **Théorie de l'affaire** (`theorie-de-l-affaire`, `strategie/theorie.json`). Les hypothèses sont générées avant d'être jugées : la nôtre, la meilleure de l'adversaire, la lecture par défaut du juge. Chacune est éprouvée contre chaque pièce, et la théorie retenue est celle que le moins de pièces contredisent. Chaque fait défavorable reçoit un traitement sans concession : intégration, dépassement, indifférence ou retournement. La qualification et la question sont choisies pour donner au juge un contrôle entier. Une théorie adverse est écrite par l'avocat adverse à partir des seules pièces ; seul ce sous-agent peut l'écrire. Méthode tirée de l'analyse des hypothèses concurrentes (Heuer) et du modèle du récit (Pennington et Hastie), avec leur statut de lecture.
- **Séquence** (`conduite-de-la-sequence`, `strategie/sequence.json`). Elle comprend :
  - l'inventaire des actes depuis le premier acte adverse, avec leurs vices et leur chaîne ;
  - la carte des autorités ;
  - onze familles de voies, chacune examinée ;
  - les effets des voies les unes sur les autres, lus à la source ;
  - la cible ;
  - l'ordre des coups, chacun avec les réponses adverses prévues et notre coup suivant ;
  - les actes refusés, avec ce qui les rendrait forts.

  Le briefing de chaque session rappelle le prochain coup.
- **Architecte refondé.** Il reprend la séquence depuis le premier acte adverse, refait l'épreuve des hypothèses, juge chaque famille de voies et la négociation. Si la campagne est mal conçue, il rend la campagne complète à mettre à sa place.
- **Contrôle** (`scripts/controles_campagne.py`, appelé par `gate.py`). Une écriture juridictionnelle est refusée dans les cas suivants :
  - la théorie est absente ou antérieure au dernier apport du dossier ;
  - elle n'a pas été éprouvée contre ses concurrentes ;
  - un fait défavorable n'a pas de traitement ;
  - la théorie adverse n'a pas été écrite ;
  - la séquence est absente ou périmée ;
  - une famille de voies n'a pas été examinée ;
  - l'acte n'est rattaché à aucune voie retenue ni à aucun coup ordonné ;
  - un coup n'a pas de réponse adverse prévue ;
  - la fiche de récit projette une autre version de la théorie ;
  - la revue de charpente n'a pas examiné la théorie et la séquence en vigueur.

- **La négociation en même temps que le procès.** Le `negociateur` établit et révise à chaque tournant le plan de négociation et de persuasion (`strategie/negociation.json`) : solution de repli de chaque partie, ce que l'adversaire peut accorder sans perdre la face, effet de chaque voie amiable sur les délais, première offre, contreparties conditionnelles, conditions de forme d'un accord avec une personne publique, persuasion de chaque décideur. Le contrôle bloque l'acte juridictionnel sans voie amiable examinée, sauf urgence motivée, et l'écrit qui laisserait passer un chiffre de la négociation. Règles sourcées dans `skills/negociation-et-persuasion/references/`, épreuve dans `docs/epreuves/negociation.md`.

## Rupture de méthode et refonte (19 et 20 novembre)

- **Méthode** (`docs/METHODE.md`). Quatre niveaux d'évaluation : tests en parallèle, instantanés du contrôle sur les écritures des épreuves, banc de sondes notées mécaniquement, épreuves sur affaires neuves. Chaque défaut passe par la même boucle : cause racine, sonde qui échoue, correctif à la couche de la cause, vérification sans régression.
- **Routage.** Le briefing de démarrage dit quel skill charger dans chaque situation. Les agents ne les chargent pas d'eux-mêmes, et c'est ce routage qui fait passer les sondes de jugement.
- **Recherche et lecture exacte** (`recherche-juridique`, `lecteur-de-texte`, `scripts/lectures.py`).
  - Chaque appel LibreJustice est capturé.
  - Les citations sont confrontées mot pour mot aux textes lus.
  - La suite des décisions citées est vérifiée.
  - Les articles doivent être lus à la date utile, et la compétence en premier ressort est lue avant tout acte porté devant le juge administratif.
  - Le protocole compte dix passes, notamment la section de l'article, la jurisprudence par article, les conclusions et rapports.
- **Doctrine et autres disciplines** (`recherche-doctrinale`, `chercheur-doctrine`). Chaque travail cité porte une fiche qui dit ce qui en a été lu. Les conclusions des rapporteurs publics et les rapports se trouvent par le champ `commentaries`.
- **Mécanique des exercices** (`mecanique-des-exercices`). Trente fiches d'exercice lues à la source. Chaque acte porte le diagnostic de son exercice : la condition qui le fait échouer, ses exigences implicites, la cible, l'exercice voisin écarté.
- **Rapport de force** (`rapport-de-force`, `strategie/positions.json`).
  - Un arsenal de leviers licites, chacun avec sa limite légale.
  - Les écrits qui sortent ne livrent rien à l'adversaire.
  - Chaque position tenue devant le client ne change que sur un élément nouveau nommé.
  - Une limite ne figure dans le harness que si la loi applicable à l'affaire ou la déontologie de l'avocat la fonde.

## Limites

Les contrôles sont mécaniques : la détection de la première page, des citations et des formules atténuées repose sur des motifs, avec des faux positifs et des oublis possibles. Un PASS n'atteste ni la justesse juridique ni l'issue. Les hooks n'existent que dans Claude Code ; dans Codex, les mêmes scripts doivent être appelés par consigne. Les sorties des sous-agents peuvent être recopiées par la session principale quand leur écriture est refusée, ce qui suppose une copie fidèle. Le plugin ne remplace ni l'avocat aux Conseils, ni la décision du client.

Les recherches préalables sont dans `docs/recherche/` : état de l'art agentique et formats de Claude Code (01), décideurs, récit et procédure (02), audit interne des réussites et échecs (03). La recherche 02 alimente les références des skills (`refere-administratif/references/arrets.md`, `refere-civil/references/arrets.md`, `strategie-contentieuse/references/decideurs.md`) : cinquante décisions vérifiées sur LibreJustice avec leur statut de lecture, cinquante règles par décideur, et vingt-trois résultats de psychologie judiciaire à ne pas croire, dont le « juge affamé ». Les règles psychologiques y restent des inférences : aucune étude publiée ne teste un style d'acte sur des magistrats français.
