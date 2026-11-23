# État de l'art des systèmes agentiques pour le harness de contentieux

Note de recherche du 18 novembre 2026. Elle répond à une question précise : quelles décisions d'architecture prendre pour un harness Claude Code destiné au contentieux français (rédaction d'actes, référés, stratégie, recherche juridique), au vu des travaux publiés entre 2023 et 2026 et de la documentation actuelle de Claude Code.

Méthode. Les billets d'ingénierie et la documentation ont été téléchargés et lus dans leur texte. Les articles scientifiques ont été téléchargés depuis arXiv, convertis en texte et lus sur leur résumé et sur les passages qui portent les résultats cités ; aucun n'a été relu en entier. Les dépôts GitHub ont été examinés par l'API publique (sans authentification) et par la lecture de leurs fichiers principaux. Les formats Claude Code ont été vérifiés sur la documentation, puis, pour une partie, par exécution locale avec Claude Code 2.1.317 (section B.9). Chaque source porte un statut en section D : « lu » (texte ou passages pertinents lus), « résumé lu » (synthèse obtenue par un outil de lecture, texte non lu directement), « non vérifié » (connu par un résultat de recherche seulement). Les identifiants entre crochets renvoient à cette section.

Le plugin `contentieux` existe déjà dans ce dépôt (agents `contradicteur`, `avocat-adverse`, `juge-simule`, `verificateur-sources`, `chercheur-juridique`, `plume`, `stratege-terrain`, hooks sur `scripts/hook.py`, fichiers `etat/`). Les décisions ci-dessous s'appuient sur ces composants chaque fois que c'est possible.

## A. Décisions d'architecture

### 1. Les fichiers d'état portent la mémoire du dossier

Décision. Tout ce qui doit survivre à une compaction, à un `/clear` ou à une nouvelle session est écrit dans les fichiers du dossier et relu au début de chaque session : `etat/affaire.json`, `etat/passation.md`, `etat/sources.json`, la chronologie et la liste des obligations (décision 2). Les statuts qui ne doivent pas être réécrits librement vont en JSON ; le récit de progression va en Markdown ; l'historique va dans un journal en ajout seul ou dans git. Une consigne donnée seulement dans la conversation est considérée comme perdue à la prochaine compaction.

Preuve. Anthropic a observé, sans artefacts de passation, deux échecs récurrents d'un agent travaillant sur plusieurs fenêtres de contexte : il tente de tout faire d'un coup et laisse à la session suivante un travail à moitié fait et non documenté ; plus tard, une instance voit que du travail existe et déclare le projet terminé. La réponse retenue combine un fichier de progression, l'historique git et une liste de fonctionnalités en JSON, ce format ayant été choisi parce que le modèle modifie ou écrase moins volontiers un JSON qu'un Markdown [A4]. Le billet de mars 2026 garde les artefacts structurés de passation et fait communiquer les agents par fichiers [A5]. Sur une évaluation interne de recherche agentique, la mémoire sur fichiers combinée au nettoyage des anciens résultats d'outils améliore la performance de 39 % (chiffre interne, non reproductible de l'extérieur) [A8]. Letta rapporte qu'un agent doté de simples outils de fichiers atteint 74,0 % sur LoCoMo, mais ce test mesure le rappel d'information et non la mémoire agentique [P4]. La documentation précise que le `CLAUDE.md` racine du projet est relu sur disque après compaction, que les fichiers imbriqués et les règles à chemin se rechargent à la demande, et qu'une instruction donnée seulement en conversation peut disparaître [D6].

Composant. Fichiers d'état existants ; hook `SessionStart` qui produit le briefing à partir d'eux (décision 15) ; hook `Stop` qui vérifie que `etat/passation.md` a été mis à jour quand des fichiers du dossier ont changé.

### 2. Une liste fermée d'obligations définit l'achèvement

Décision. Pour chaque acte, le harness établit avant la rédaction une liste d'obligations, toutes à l'état « non satisfaite » : conditions du régime invoqué, recevabilité, délais, acte attaqué, pièces requises, conclusions que le juge peut accorder. Seul le champ de statut se modifie, et seulement avec une référence à la source ou à la pièce qui le justifie. Le hook `Stop` refuse la fin de tour tant qu'une obligation bloquante reste ouverte dans la phase en cours.

Preuve. La liste de fonctionnalités d'Anthropic, environ 200 entrées marquées `"passes": false` et modifiables seulement sur ce champ, répond aux deux échecs observés : la victoire déclarée trop tôt et la fonctionnalité marquée faite sans test de bout en bout [A4]. Dans la taxonomie MAST, construite sur plus de 1 600 traces de sept cadres multi-agents, la catégorie « vérification de la tâche » représente 23,5 % des défaillances annotées : terminaison prématurée 6,2 %, vérification absente ou incomplète 8,2 %, vérification incorrecte 9,1 % [V12]. La documentation de Claude Code indique qu'une règle écrite dans `CLAUDE.md` est suivie la plupart du temps, et qu'un hook `Stop` est appliqué par le harness lui-même [A9].

Composant. Fichier d'obligations par acte (dans `ecritures/controle/` ou `etat/`) ; hook `Stop` existant, qui doit tenir compte de `stop_hook_active` et du plafond de huit continuations consécutives (sections B.3 et B.4).

### 3. Les règles sans exception passent par la configuration, les consignes par des fichiers courts

Décision. Ce qui doit se produire à chaque fois (pas d'écriture dans `pieces/`, pas d'export d'un acte sans contrôle des sources, pas de requête publique contenant un fait du dossier) est confié à un hook, à une règle de permission ou à un outil déterministe. `CLAUDE.md` de l'affaire et les skills portent les méthodes et les conventions. Chaque `CLAUDE.md` reste sous 200 lignes ; les procédures longues (référé-suspension, cassation) vivent dans des skills, chargées seulement quand la tâche les demande.

Preuve. La page de bonnes pratiques recommande de transformer en hook, règle de refus ou paramètre géré ce qui doit arriver à chaque fois, `CLAUDE.md` restant le lieu des lignes directrices que Claude peut juger inapplicables ; elle déconseille l'emphase (IMPORTANT, majuscules), qui fait surappliquer une règle [A9]. La page sur la mémoire fixe la cible de moins de 200 lignes et note que les imports ne réduisent pas le coût en contexte [D6]. Les skills ne placent que leur nom et leur description dans le contexte de départ et chargent leur corps à la demande [A7, D4].

Composant. `hooks/hooks.json` ; `CLAUDE.md` par affaire ; skills du plugin.

### 4. Les garde-fous échouent fermés

Décision. Les hooks de politique sur `PreToolUse` et `UserPromptSubmit` utilisent la forme exec (`command` et `args`), le champ `"onFailure": "block"`, et signalent un refus par le code de sortie 2 ou par un objet JSON de refus, jamais par le code 1. Ils n'impriment sur la sortie standard qu'un seul objet JSON. Un hook qui expire n'est pas compté comme un verrou. Les hooks actuels du plugin sont en forme shell (`python "${CLAUDE_PLUGIN_ROOT}/scripts/hook.py"`) sans `onFailure` : un plantage du script ou un mauvais chemin laisse passer l'action.

Preuve. La référence des hooks précise que le code 1 sans JSON valide est une erreur non bloquante, qu'un hook `PreToolUse` qui atteint son délai ne bloque pas l'appel, qu'un script introuvable laisse passer l'action, et que `onFailure: "block"` (Claude Code 2.1.295 ou plus récent ; 2.1.317 est installé) transforme ces échecs en blocage. Elle recommande la forme exec pour toute commande qui contient une variable de chemin et décrit des comportements propres à Windows sans Git Bash. Elle précise aussi que le filtre `if` est approximatif et qu'une interdiction stricte relève du système de permissions [D1].

Composant. `plugins/contentieux/hooks/hooks.json`.

### 5. La vérification des sources se fait en deux temps : contrôle mécanique, puis lecture de portée

Décision. Un script, sans modèle, contrôle d'abord chaque référence extraite d'une écriture : résolution vers un identifiant officiel (ECLI, numéro de requête ou de pourvoi, identifiant LEGIARTI ou NOR, CELEX), concordance du triplet juridiction, date et numéro, présence à l'identique de chaque passage entre guillemets dans le texte acquis, version de l'article applicable à la date retenue. Un sous-agent séparé lit ensuite la source pour juger la portée : la décision porte-t-elle la proposition, à quel titre (motif décisif, motif surabondant, simple rappel d'un moyen de partie), a-t-elle été censurée ou contredite depuis. Une écriture ne peut être exportée pour dépôt que si le rapport mécanique ne signale aucune référence non résolue.

Preuve. Les outils commerciaux de recherche juridique fondés sur la recherche documentaire (Lexis+ AI, Westlaw AI-Assisted Research, Ask Practical Law AI) produisent une hallucination dans 17 à 33 % des réponses ; l'étude distingue la réponse fausse de la réponse « mal fondée », qui cite une source réelle ne soutenant pas l'affirmation, et attribue les erreurs à une recherche naïve (20 à 47 % des réponses hallucinées selon l'outil), à une autorité inapplicable (mauvaise juridiction, texte ou décision dépassée ; 23 à 38 %) et à des erreurs de raisonnement (28 à 61 %), dont un cas où le modèle prête à la juridiction ce qu'elle rapportait des déclarations d'une partie [L1]. Les modèles généralistes hallucinent dans 58 à 88 % des réponses à des questions vérifiables sur des décisions fédérales américaines [L2]. En France, le tribunal administratif d'Orléans (29 décembre 2025, n° 2506461) relève quinze décisions citées par un conseil qui n'existent pas, soit que le numéro n'existe pas, soit qu'il ne correspond pas à la date indiquée, et une décision réelle sans rapport avec la question ; plusieurs numéros existent bien, mais pour d'autres dates [L14]. Le recensement de Damien Charlotin compte 2 306 décisions de ce type au 16 novembre 2026, dont 14 en France, classées en références fabriquées, dénaturées, fausses citations et conseils périmés [L13]. Les travaux sur l'autocorrection concluent qu'elle fonctionne quand elle s'appuie sur un retour externe fiable, comme un outil de recherche [V2, V7]. Le plugin memoforge applique cette séparation : un contrôle déterministe (référence résolue, citation identique au texte enregistré, source exclue ou dépassée) précède l'auditeur sémantique [G2].

Composant. Outil déterministe (serveur `legal_harness` ou script du plugin) ; hook `PostToolUse` sur `Write|Edit` des écritures qui renvoie à Claude la liste des références non résolues ; sous-agent `verificateur-sources` pour la portée ; verrou `PreToolUse` sur l'export ou la copie d'un acte vers `depot/`.

### 6. Le droit applicable se cite avec sa date

Décision. Chaque entrée de `etat/sources.json` porte la date de référence (faits, acte attaqué, date à laquelle le juge statue), la version appliquée, son intervalle de vigueur et la date de consultation. La recherche d'un article se fait à date (consultation versionnée), jamais sur la seule version en vigueur. Les délais et dates de procédure sont calculés par l'outil prévu (`calculate_civil_deadline` du serveur `legal_harness`) ou par un calcul écrit et vérifiable, jamais de mémoire.

Preuve. Sur 209 questions de droit fiscal français indexées dans le temps, la connaissance paramétrique donne 3,0 % de réponses strictement exactes et une recherche sur un corpus statique de la version en vigueur 2,7 % ; cette recherche statique ne retrouve jamais la version applicable et cite avec assurance une version réelle mais inapplicable, alors qu'un index de 32 436 versions d'articles atteint 98,3 %. Les auteurs notent par ailleurs qu'un juge LLM hériterait du biais temporel qu'il doit mesurer et notent les réponses de façon déterministe [L11]. La taxonomie de praticien du dépôt droit-francais-skill isole les mêmes risques (effet de date de coupure, confusion de versions, oubli des dispositions transitoires), sans mesure publiée [G3]. Pour le calcul des délais, aucune étude lue ici ne mesure directement l'erreur des modèles ; la décision repose sur le principe général de retour externe fiable [V7] et sur l'existence d'un outil déjà écrit.

Composant. Registre des sources ; outils `get_norm` à date (LibreJustice) et `acquire_source` (`legal_harness`) ; chronologie du dossier.

### 7. Le vérificateur part de la source, sans le raisonnement de l'auteur

Décision. Le brief d'un sous-agent de vérification ou de relecture à froid contient les propositions à contrôler et leurs références, et les fichiers à lire ; il ne contient ni l'argumentation interne de l'équipe ni les échanges qui ont produit l'écriture. Le `juge-simule` garde des outils limités à la lecture et à l'écriture de son rapport et démarre avec `omitClaudeMd: true` lorsque le `CLAUDE.md` de l'affaire contient des notes stratégiques, faute de quoi il les reçoit à son démarrage.

Preuve. Dans Chain-of-Verification, la variante « factorisée », qui répond aux questions de vérification sans voir le brouillon, fait mieux que la variante jointe, parce qu'un modèle qui lit ses propres hallucinations tend à les répéter [V1]. La documentation de Claude Code note que confier la même tâche à un sous-agent n'améliore pas la réponse, alors qu'un relecteur neuf aide parce qu'il n'a pas vu le raisonnement [A9]. Un modèle évaluateur favorise ses propres productions, et cette préférence croît avec sa capacité à les reconnaître [V13] ; le biais d'autovalorisation figure parmi les biais documentés des juges LLM [V14]. Anthropic constate que les agents notent généreusement leur propre travail [A5]. Le champ `omitClaudeMd` existe depuis Claude Code 2.1.271 [D5].

Composant. Frontmatter de `juge-simule` et `verificateur-sources` ; gabarit de brief dans le skill `controle-avant-depot`.

### 8. La revue contradictoire tranche selon une règle écrite, sans débat jusqu'au consensus

Décision. Les relecteurs (`contradicteur`, `avocat-adverse`, `juge-simule`, `verificateur-sources`) travaillent en parallèle et sans échange entre eux. Chaque objection est rendue avec une gravité (bloquante, à corriger, mineure), sa preuve (source ou pièce et passage) et une proposition (couper, garder, reformuler). Une étape d'arbitrage applique ensuite des règles fixées à l'avance : une objection appuyée sur un passage lu et touchant la recevabilité, une condition du régime ou une source est retenue sauf réfutation par une autre source ; une objection sans preuve est écartée avec mention ; le fond prime la forme ; deux objections de fond contraires sont consignées avec la solution retenue. Les décisions sont inscrites dans un fichier de décisions de l'écriture. Un second tour n'a lieu que si une source ou une pièce nouvelle est apparue.

Preuve. Le débat multi-agents améliore des tâches de raisonnement et de factualité dans l'étude de Du et al. [V5]. Comparé à nombre de réponses égal, il ne fait pas mieux que l'auto-cohérence [V6]. Il ne surpasse pas de façon fiable d'autres stratégies et reste très sensible à ses réglages [V8]. Le vote majoritaire explique l'essentiel du gain attribué au débat ; le débat seul ne fait pas progresser l'exactitude attendue (processus de martingale), et ce sont les interventions qui favorisent la correction qui l'améliorent [V9]. Des agents passent d'une réponse juste à une réponse fausse sous l'influence de leurs pairs, et l'exactitude du groupe baisse au fil des tours, y compris quand les modèles forts sont majoritaires [V10]. À l'inverse, deux experts plaidant des réponses opposées devant un juge non expert font monter l'exactitude du juge à 76 % (modèle) et 88 % (humains), contre 48 % et 60 % sans débat [V11]. Le dispositif qui aide est donc un contradictoire tranché par un décideur. Un modèle cède plus à une contre-argumentation présentée après coup qu'à deux positions présentées ensemble [Y5]. La documentation de Claude Code avertit qu'un relecteur à qui l'on demande des problèmes en trouvera toujours, et qu'appliquer chaque remarque produit des précautions inutiles [A9]. Le médiateur de memoforge consolide les remarques par section avec la règle du fond avant la forme [G2].

Composant. Agents existants ; skill `controle-avant-depot` pour l'arbitrage ; fichier de décisions dans `ecritures/controle/`.

### 9. Pas d'autocorrection sans signal externe, et un nombre de passes borné

Décision. Une nouvelle passe de révision juridique n'est lancée que sur un signal externe : objection appuyée sur une source, résultat d'un outil, pièce nouvelle. Le nombre de cycles de révision d'une écriture est plafonné (deux, par exemple), après quoi les points ouverts sont présentés à l'utilisateur avec leur état. Les passes de style (`plume`) restent permises, une fois, sur un texte dont le fond est arrêté.

Preuve. Sans retour externe, les modèles ne corrigent pas leur raisonnement et le dégradent parfois ; les gains rapportés par plusieurs travaux tenaient à des étiquettes de vérité connues d'avance ou à une invite initiale médiocre [V6]. Aucune étude passée en revue ne montre d'autocorrection réussie fondée sur le retour d'un modèle sollicité par invite, sauf pour des tâches exceptionnellement adaptées ; elle fonctionne avec un retour externe fiable [V7]. CRITIC obtient ses gains avec des outils et note que l'autocorrection sans retour externe apporte peu ou dégrade [V2]. Self-Refine améliore en moyenne de 20 points sept tâches allant du dialogue au raisonnement mathématique, mesurées par préférence humaine et métriques automatiques [V3], mais une partie de ce gain disparaît face à une meilleure invite initiale [V6] ; Reflexion s'appuie sur des signaux de tâche comme des tests unitaires [V4]. Anthropic décrit un évaluateur qui repère de vrais défauts puis se persuade qu'ils sont mineurs, et conclut que l'évaluateur ne vaut son coût que pour les tâches à la limite de ce que le modèle réussit seul [A5].

Composant. Skill `controle-avant-depot` ; compteur de cycles dans le fichier de décisions ; hook `Stop`.

### 10. L'évaluateur est séparé, sceptique par construction, et sa grille est fixée avant la rédaction

Décision. Avant de rédiger, l'agent et le `juge-simule` arrêtent un « contrat d'écriture » : ce que le juge doit pouvoir accorder, les conditions à établir, la pièce qui prouve chacune, les critères vérifiables (par exemple une urgence datée et personnelle établie par pièce). Le `juge-simule` note chaque critère réussi ou échoué ; un seul échec sur un critère bloquant fait échouer l'écriture. La grille est calibrée sur quelques exemples annotés et révisée quand ses verdicts divergent de ceux de l'utilisateur.

Preuve. Séparer l'agent qui produit de l'agent qui juge et régler ce dernier vers le scepticisme est plus facile que rendre le producteur critique envers son travail ; les critères à seuil dur, le contrat négocié avant chaque étape et la calibration par exemples ont permis au harnais d'Anthropic de dépasser une exécution simple, pour un coût de 200 dollars et six heures contre 9 dollars et vingt minutes [A5]. Pour l'évaluation de recherches, un seul appel de juge avec une grille donnait les notes les plus cohérentes avec celles des humains, et les tests humains repéraient ce que l'automatisation manquait [A3]. LEXam valide un jugement par modèles des étapes de raisonnement juridique contre des experts humains [L6].

Composant. `juge-simule` ; grilles par procédure dans les références des skills (`refere-administratif`, `refere-civil`, `cassation`).

### 11. La complaisance se traite par la forme des échanges

Décision. Les briefs et les règles du plugin appliquent six mesures. Les positions concurrentes sont présentées ensemble au relecteur, jamais sous forme de contestation après coup. La thèse du client est formulée à la troisième personne (« le requérant soutient que »). Les marques d'auteur et de préférence (« j'ai rédigé », « cet argument me paraît fort ») sont retirées de ce que reçoivent les relecteurs. Quand l'utilisateur conteste une conclusion sourcée sans fait ni source nouvelle, l'agent la maintient et dit quel élément la ferait changer. Une contre-citation apportée par l'utilisateur est vérifiée à la source avant toute concession. Une question à prémisse (« quel arrêt dit que ») est reformulée en proposition à établir et en proposition contraire.

Preuve. Cinq assistants donnent un avis plus favorable sur un texte quand l'utilisateur dit l'avoir écrit ou l'apprécier, et renoncent à une réponse juste après un simple « en êtes-vous sûr ? » ; humains et modèles de préférence préfèrent parfois une réponse complaisante bien écrite à une réponse exacte [Y1]. Après un tel défi, dix modèles changent leur réponse dans 46 % des cas en moyenne et perdent 17 % d'exactitude [Y2]. Formuler la position à la troisième personne améliore la résistance jusqu'à 63,8 % dans les débats, et une consigne explicite contre la complaisance jusqu'à 28 % sur les requêtes contraires à l'éthique ; le réglage d'alignement accroît la complaisance, la taille et l'optimisation du raisonnement la réduisent [Y4]. Les modèles cèdent davantage à une contestation présentée après coup, à une contestation longuement argumentée même fausse, et à un retour familier plus qu'à une critique formelle [Y5]. Les contestations appuyées sur une citation produisent le plus de revirements vers une réponse fausse [Y3]. Les invites d'atténuation ont un effet limité et aveugle au contexte sur la complaisance sociale [Y6]. En droit, les modèles généralistes acceptent souvent des prémisses juridiques erronées [L2], alors que les outils spécialisés testés par Magesh et al. les corrigent assez bien [L1]. La documentation de Claude Code demande que le contexte injecté par un hook soit écrit comme un constat, un texte présenté comme une consigne système pouvant être traité comme une injection [D1].

Composant. Gabarit de brief des sous-agents (skills) ; règle dans les instructions du plugin ; éventuellement un constat injecté par `UserPromptSubmit` quand le message conteste une conclusion inscrite dans le fichier de décisions.

### 12. Sous-agents isolés pour la recherche en largeur et la relecture, un seul rédacteur pour l'acte

Décision. Les questions de droit indépendantes sont confiées en parallèle à `chercheur-juridique`, chacune avec un brief complet : objectif, format de sortie, sources à interroger, limites de la tâche, budget d'effort. La rédaction d'un acte reste dans un seul fil qui dispose de tout le dossier ; elle n'est pas découpée entre agents parallèles.

Preuve. Le système de recherche multi-agents d'Anthropic (Opus 4 coordinateur, Sonnet 4 en sous-agents) dépasse l'agent unique de 90,2 % sur une évaluation interne de recherche en largeur ; la quantité de tokens dépensée explique 80 % de la variance sur BrowseComp ; ces systèmes consomment environ quinze fois plus de tokens qu'une conversation et conviennent mal aux tâches à contexte partagé et à fortes dépendances. Des briefs vagues ont produit des recherches dupliquées et des lacunes [A3]. Cognition montre que des sous-agents qui ne partagent pas tout le contexte prennent des décisions implicites contradictoires et produisent des pièces incohérentes entre elles [P2]. La documentation de Claude Code rappelle qu'un sous-agent coûte des tokens et peut être plus lent, faute du contexte déjà réuni [A9]. Un sous-agent rend en général un résumé de 1 000 à 2 000 tokens [A2].

Composant. `chercheur-juridique` ; gabarit de délégation dans le skill `recherche-juridique` ; rédaction dans le fil principal.

### 13. Les sous-agents écrivent sur disque et rendent une référence

Décision. Chaque sous-agent écrit son résultat dans un fichier du dossier (`recherche/<question>.md`, `ecritures/controle/<nom>.<controle>.md`) et ses entrées de sources dans `etat/sources.json`, puis rend un message court : chemin, conclusion, points ouverts. Un hook `SubagentStop` du plugin vérifie que le fichier attendu existe et, sinon, bloque l'arrêt du sous-agent avec la raison.

Preuve. Anthropic recommande que les sous-agents stockent leurs productions dans des systèmes externes et ne transmettent au coordinateur qu'une référence légère, pour limiter les pertes de transmission et le coût en tokens [A3] ; le harnais de 2026 fait communiquer ses agents par fichiers [A5]. Un `SubagentStop` en `decision: "block"` maintient le sous-agent en activité et lui transmet `reason` comme instruction suivante ; le type d'un agent de plugin est de la forme `contentieux:verificateur-sources`, d'où un matcher ancré `^contentieux:verificateur-sources$` [D1]. Les agents de plugin ignorent `hooks`, `mcpServers` et `permissionMode` dans leur frontmatter : ces hooks doivent figurer dans `hooks/hooks.json` [D5].

Composant. `hooks/hooks.json` ; prompts des agents.

### 14. Compaction et reprise sont pilotées par des hooks

Décision. Un hook `PreCompact` imprime les éléments que le résumé doit conserver : phase, prochain délai, obligations ouvertes, décisions prises, identifiants des sources en cours d'usage. Un hook `SessionStart` (sources `startup`, `resume`, `clear`, `compact`) réinjecte un briefing calculé depuis les fichiers. Quand un contenu est retiré du contexte, son identifiant ou son chemin reste (compression restaurable). Pour un travail très long, une nouvelle session ouverte sur `etat/passation.md` est préférée à des compactions répétées.

Preuve. Anthropic conseille de régler un prompt de compaction d'abord pour le rappel puis pour la précision, et décrit le nettoyage des résultats d'outils comme la forme la plus légère [A2]. Manus ne compresse que de façon restaurable (l'adresse d'une page ou le chemin d'un document restent) et traite le système de fichiers comme la mémoire de l'agent [P1]. Anthropic distingue compaction et remise à zéro avec passation : la remise à zéro donnait une page blanche à un modèle (Sonnet 4.5) qui écourtait son travail à l'approche de la limite qu'il percevait, comportement largement disparu avec Opus 4.5 [A5]. Dans Claude Code, la sortie standard d'un hook `PreCompact` devient l'instruction de résumé (10 000 caractères au plus) ; le contexte injecté en cours de session est rejoué tel quel lors d'une reprise, alors que `SessionStart` s'exécute de nouveau et peut le rafraîchir [D1].

Composant. Hooks `PreCompact` et `SessionStart` (ce dernier existe déjà).

### 15. Le rappel injecté est court, factuel et calculé depuis les fichiers

Décision. Le briefing injecté par `SessionStart` et `UserPromptSubmit` tient en quelques lignes : date du jour, prochain délai et son fondement, obligations bloquantes, phase, dernière décision. Il est généré par le script à partir des fichiers d'état, écrit comme une suite de constats, et ne reprend pas le dossier.

Preuve. Manus fait réécrire à l'agent une liste de tâches tout au long des quelque cinquante appels d'outils d'une tâche, pour ramener le plan dans la partie récente du contexte et réduire la dérive d'objectif [P1]. Le rapport de Chroma sur 18 modèles montre une dégradation non uniforme avec la longueur du contexte et un effet croissant des distracteurs proches du sujet [P3], situation ordinaire en droit (articles voisins, décisions de même espèce). Le contexte injecté par hook est plafonné à 10 000 caractères ; au-delà, il est déposé dans un fichier dont seul un aperçu de 2 000 caractères est montré. Un hook `UserPromptSubmit` a un délai par défaut de 30 secondes et retarde chaque message [D1].

Composant. `scripts/hook.py` (événements `SessionStart` et `UserPromptSubmit`).

### 16. Peu d'outils, consolidés, aux identifiants lisibles et à sortie bornée

Décision. Les outils exposés font chacun une opération juridique complète : acquérir une décision par son numéro et rendre juridiction, date, formation, solution, ECLI, adresse officielle et texte ; rendre un article à une date avec son intervalle de vigueur. Ils renvoient des identifiants lisibles (ECLI, numéro de requête, LEGIARTI), paginent ou tronquent avec une indication de suite, et rendent des erreurs qui disent comment corriger l'appel. Chaque sous-agent reçoit la liste minimale d'outils utile à son rôle. L'ensemble des outils ne change pas en cours de session.

Preuve. Anthropic recommande peu d'outils ciblant des opérations à fort enjeu, la consolidation d'opérations enchaînées et le retour des seules informations qui servent l'action suivante, sans identifiants techniques ; remplacer des identifiants opaques par des noms ou des identifiants signifiants améliore la précision et réduit les hallucinations ; Claude Code limite par défaut une réponse d'outil à 25 000 tokens [A6]. Des descriptions d'outils réécrites après test ont réduit de 40 % la durée des tâches suivantes [A3]. Un ensemble d'outils trop large est l'un des échecs les plus fréquents [A2]. Manus déconseille d'ajouter ou retirer des outils en cours d'itération (cache invalidé, références à des outils disparus) [P1]. Le serveur fr-eli-mcp associe à chaque réponse un `eli_uri`, une citation lisible et une adresse source [G5] ; LibreJustice renvoie l'adresse officielle et la chronologie de l'affaire, constaté pendant cette recherche [L14].

Composant. Serveurs `legal_harness` et LibreJustice ; champ `tools:` des agents.

### 17. Les briques externes reprises sont des connecteurs officiels et des motifs de conception

Décision. Le harness garde LibreJustice et `legal_harness` comme sources principales et prévoit un connecteur officiel de secours sur l'API Légifrance (PISTE), qui exige un compte et des identifiants : fr-eli-mcp en premier choix, droit-francais-mcp en second. Pour l'Union, eur-lex-mcp-server de cyanheads est à évaluer. Le plugin juridique d'Anthropic n'est pas repris. La taxonomie des dix-huit modes d'erreur de droit-francais-skill sert de liste de contrôle au `verificateur-sources`. De memoforge, le harness reprend des motifs, sans le code : audit mécanique des citations avant l'audit sémantique, relecteurs qui ne voient ni les autres relecteurs ni les verdicts antérieurs, médiateur, garde d'arrêt optionnelle avec compteur. Si un serveur MCP est un jour embarqué dans le plugin, ses outils changeront de nom (`mcp__plugin_contentieux_<serveur>__<outil>`), ce qui impose de mettre à jour les listes `tools:` des agents et les matchers des hooks.

Preuve. Maturité constatée le 18 novembre 2026 en section C.2 et en D (G1 à G9). Le plugin d'Anthropic vise les juristes d'entreprise, repose sur des positions américaines par défaut et ne contient que des skills, sans hook ni contrôle des sources [G1]. droit-francais-skill n'a publié aucun résultat de sa campagne de mesure [G3]. Le nommage des outils de serveurs embarqués est documenté [D1].

Composant. Configuration MCP ; agents ; liste de contrôle du `verificateur-sources`.

### 18. Évaluer tôt, sur peu de cas, avec notation déterministe quand elle est possible, et retirer les composants un par un

Décision. Le harness dispose d'une vingtaine de cas tirés de procédures réelles anonymisées (référés, fond, cassation), évalués sur l'état final : citations résolues, versions correctes, délais exacts, obligations satisfaites, ce qui se note par programme ; la portée et la stratégie sont notées par un appel unique de juge avec grille, et périodiquement en aveugle par un humain. Chaque composant du harness (évaluateur, arbitrage, rappel injecté) est testé par retrait, un à la fois, et retesté à chaque changement de modèle.

Preuve. Anthropic a commencé avec une vingtaine de requêtes, les effets précoces étant grands, et privilégie l'évaluation de l'état final pour les agents qui modifient un état [A3]. Chaque composant d'un harnais encode une hypothèse sur ce que le modèle ne sait pas faire seul ; ces hypothèses vieillissent, et seul le retrait méthodique d'un composant à la fois a permis d'identifier ce qui portait la performance [A5]. Les jeux de test réservés évitent le surajustement [A6]. Le juge LLM est à proscrire pour la justesse temporelle [L11]. PRBench, 1 100 tâches rédigées par 182 professionnels, plafonne à 0,37 sur son sous-ensemble juridique difficile et relève des jugements inexacts, un manque de transparence du raisonnement et des raisonnements incomplets [L10] ; LEXam montre la difficulté des questions ouvertes qui demandent un raisonnement en plusieurs étapes [L6]. Le README du projet déclare 199 réponses conformes sur 209 questions fiscales datées et aucune tâche PRBench sur 19 satisfaisant le contrôle strict ; ces chiffres n'ont pas été revérifiés ici.

Composant. Dossier `evaluation/` du dépôt ; Claude Code offre aussi `claude plugin eval` et le champ `experimental.evals`, non testés ici [D2].

### 19. Les requêtes sortantes sont filtrées par hook

Décision. Un hook `PreToolUse` sur `WebSearch`, `WebFetch` et les serveurs juridiques publics compare `tool_input` à la liste des noms, numéros et faits propres au dossier (tirée de `etat/affaire.json`) et refuse l'appel qui en contient, avec une raison qui indique la reformulation générique attendue. Les numéros de décisions publiées restent permis.

Preuve. Cette décision relève de la conformité ; aucune étude empirique lue ici ne la fonde. Un hook `PreToolUse` reçoit les arguments de l'appel, peut le refuser avec une raison montrée à Claude ou en réécrire les arguments (`updatedInput`) ; les outils MCP se filtrent par expression régulière (`mcp__librejustice__.*`) [D1]. Le serveur `legal_harness` pose la même règle dans ses instructions. Le matcher `PreToolUse` actuel du plugin couvre déjà ces outils.

Composant. `hooks/hooks.json` et `scripts/hook.py`.

## B. Formats Claude Code

Sources : référence des hooks [D1], manifeste de plugin [D2], création d'une marketplace [D3], skills [D4], sous-agents [D5], mémoire [D6], pages téléchargées en Markdown le 18 novembre 2026. La documentation renvoie aussi à des chemins plus récents (par exemple `https://code.claude.com/docs/en/plugins/manifest-reference`) ; les adresses citées ici répondent toutes. Les exemples marqués « exécuté » ont été vérifiés le 18 novembre 2026 avec Claude Code 2.1.317 (section B.9) ; les autres sont recopiés de la documentation.

### B.1 Où se déclarent les hooks

Les hooks se déclarent dans `~/.claude/settings.json`, `.claude/settings.json`, `.claude/settings.local.json`, les paramètres gérés, le fichier `hooks/hooks.json` d'un plugin activé, le frontmatter d'un skill (actifs jusqu'à la fin de la session une fois le skill invoqué ; `once: true` possible) et le frontmatter d'un sous-agent (actifs pendant son exécution ; un `Stop` y devient `SubagentStop`). Les hooks des fichiers de paramètres et des plugins s'exécutent aussi dans les sous-agents, avec `agent_id` et `agent_type` dans l'entrée. Les agents fournis par un plugin ignorent les champs `hooks`, `mcpServers` et `permissionMode` [D1, D5].

Structure à trois niveaux : événement, groupe filtré par `matcher`, gestionnaires. Le matcher `"*"`, `""` ou absent vaut tout ; une valeur composée seulement de lettres, chiffres, `_`, `-`, espaces, `,` et `|` est une liste de noms exacts ; toute autre valeur est une expression régulière JavaScript non ancrée (`^Edit$` pour un nom exact) [D1].

Champs communs d'un gestionnaire : `type` (`command`, `http`, `mcp_tool`, `prompt`, `agent`), `if` (une règle de permission, seulement sur les événements d'outils), `timeout` en secondes (600 par défaut pour `command`, `http`, `mcp_tool` ; 30 pour `prompt` ; 60 pour `agent` ; ramené à 30 sur `UserPromptSubmit` ; budget commun de 1,5 seconde sur `SessionEnd`), `statusMessage`, `once`. Champs propres à `command` : `command`, `args` (forme exec, sans shell), `async`, `asyncRewake`, `shell` (`bash` ou `powershell`), `onFailure` (`continue` ou `block`, depuis 2.1.295) [D1].

Variables de chemin : `${CLAUDE_PROJECT_DIR}` (racine du projet de départ), `${CLAUDE_PLUGIN_ROOT}` (répertoire installé du plugin, qui change à chaque mise à jour, donc à ne pas utiliser pour l'état), `${CLAUDE_PLUGIN_DATA}` (`~/.claude/plugins/data/<id>/`, conservé entre mises à jour). Elles sont substituées dans `command` et `args` et exportées au processus du hook, mais absentes de l'environnement des commandes que Claude lance par l'outil Bash. Sous Windows, les chemins substitués utilisent des barres obliques, sauf en forme exec et dans un hook exécuté par PowerShell [D1, D2].

### B.2 Codes de sortie

| Sortie standard | Code 0 | Code 2 | Autre code |
| :- | :- | :- | :- |
| Un objet JSON valide | Succès, champs appliqués | Blocage ; un `PreToolUse` reste bloqué même avec `"allow"` | Succès, le code est ignoré et les champs décident (échec si `onFailure: "block"`) |
| JSON illisible ou invalide | Erreur non bloquante | Blocage, stderr sert de raison | Erreur non bloquante |
| Texte brut ou rien | Succès | Blocage, stderr sert de raison | Erreur non bloquante |

Le code 1 n'est pas bloquant. La sortie standard n'est lue comme JSON que si elle contient un seul objet, rien d'autre que des espaces autour. Le texte brut d'un code 0 devient du contexte pour Claude sur `UserPromptSubmit`, `UserPromptExpansion`, `SessionStart` et `PostModelSwitch`, et l'instruction de résumé sur `PreCompact`. Claude ne voit jamais le stderr d'un hook qui sort en 0 [D1].

`onFailure: "block"` fait d'un hook qui ne démarre pas, sort avec un autre code que 0 ou 2, expire ou rend un JSON invalide l'équivalent d'un code 2 sur l'événement (refus sur `PermissionRequest`). Il est sans effet sur `Stop`, `SubagentStop`, `TaskCompleted`, `TeammateIdle` et sur les hooks asynchrones [D1].

### B.3 Événements et capacité de blocage

| Événement | Moment | Matcher | Peut bloquer | Moyen | Remarques |
| :- | :- | :- | :- | :- | :- |
| `SessionStart` | Début ou reprise de session | `startup`, `resume`, `clear`, `compact`, `fork` | Non | `additionalContext` ou texte brut | Types `command` et `mcp_tool` seulement ; aussi `sessionTitle`, `watchPaths`, `reloadSkills`, `initialUserMessage` (mode `-p`) |
| `UserPromptSubmit` | Avant traitement du message | Aucun | Oui | Code 2 ou `decision: "block"` | Ne remplace pas le message ; `additionalContext` ; délai de 30 s ; se déclenche aussi sur les retours de sous-agents en arrière-plan et les tâches planifiées |
| `PreToolUse` | Avant un appel d'outil | Nom d'outil | Oui | Code 2 ou `permissionDecision: "deny"` | `allow`, `deny`, `ask`, `defer` ; `updatedInput` ; priorité `deny` > `defer` > `ask` > `allow` ; les règles de refus et de demande restent évaluées |
| `PermissionRequest` | Demande de permission | Nom d'outil | Par JSON seulement | `decision.behavior: "deny"` | Le code 2 n'y est pas pris en compte |
| `PostToolUse` | Après un appel réussi | Nom d'outil | Non (l'outil a déjà agi) | `decision: "block"` ajoute `reason` au résultat ; code 2 montre stderr à Claude | `additionalContext`, `updatedToolOutput` |
| `PostToolBatch` | Après un lot d'appels parallèles | Aucun | Oui | Code 2 ou `decision: "block"` | Arrête la boucle avant l'appel de modèle suivant |
| `SubagentStart` | Lancement d'un sous-agent | Type d'agent | Non | `additionalContext` injecté dans le sous-agent | |
| `SubagentStop` | Fin d'un sous-agent | Type d'agent | Oui | Code 2 ou `decision: "block"` | `reason` devient l'instruction suivante du sous-agent ; `last_assistant_message` ; un rapport livré par `SubagentHandback` se lit dans `tool_input.message` d'un hook sur cet outil |
| `Stop` | Fin de réponse de l'agent principal | Aucun | Oui | Code 2 ou `decision: "block"` avec `reason` obligatoire | Pas déclenché sur interruption de l'utilisateur ; `stop_hook_active` ; plafond de huit continuations consécutives (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`) |
| `PreCompact` | Avant compaction | `manual`, `auto` | Oui | Code 2 ou `decision: "block"` | Le texte de sortie (code 0) devient l'instruction de résumé, 10 000 caractères au plus |
| `PostCompact` | Après compaction | `manual`, `auto` | Non | | Reçoit `compact_summary` |
| `SessionEnd` | Fin de session | `clear`, `resume`, `logout`, `prompt_input_exit`, `other` | Non | | Sortie JSON ignorée ; budget de 1,5 s par défaut (`CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS`) |
| `TaskCompleted`, `TeammateIdle`, `TaskCreated`, `ConfigChange`, `PreModelSwitch`, `UserPromptExpansion`, `Elicitation` | Voir [D1] | Variable | Oui | Code 2 ou JSON propre à l'événement | Utiles hors du cœur de ce harness |

Ne peuvent rien bloquer : `Notification`, `InstructionsLoaded`, `CwdChanged`, `FileChanged`, `DirectoryAdded`, `StopFailure`, `Setup`, `PostModelSwitch` et `MessageDisplay` (affichage seulement). `PostToolUseFailure` renvoie un retour à Claude sans annuler l'échec, `PermissionDenied` ne lit que `hookSpecificOutput.retry`, et `WorktreeCreate` ou `WorktreeRemove` échouent sur tout code non nul [D1].

Les gestionnaires `prompt` et `agent` sont acceptés sur `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `PermissionDenied`, `Stop`, `SubagentStop`, `TaskCompleted`, `TaskCreated`, `TeammateIdle`, `UserPromptExpansion`, `UserPromptSubmit` ; `PermissionRequest` accepte `prompt` sans `agent` ; `SessionStart` n'accepte que `command` et `mcp_tool`. Les hooks `agent` sont expérimentaux (jusqu'à 50 tours, outils de lecture) [D1].

### B.4 Sortie JSON

Champs universels :

```json
{ "continue": false, "stopReason": "Message montré à l'utilisateur", "systemMessage": "Avertissement montré à l'utilisateur" }
```

`continue: false` arrête tout traitement mais ne bloque pas à lui seul un appel `PreToolUse`. `suppressOutput` n'a plus d'effet. `terminalSequence` émet une séquence de terminal autorisée. `hookSpecificOutput` exige `hookEventName`. Les chaînes `additionalContext`, `systemMessage` et `initialUserMessage` sont plafonnées à 10 000 caractères chacune [D1].

`PreToolUse`, refus (exécuté) :

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Refus d'essai : commande bloquee par le hook du plugin."
  }
}
```

`PreToolUse`, autorisation avec réécriture et contexte (documentation) :

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "Motif écrit au journal de débogage",
    "updatedInput": { "command": "npm run lint" },
    "additionalContext": "L'environnement courant est la production."
  }
}
```

`updatedInput` remplace l'objet d'entrée entier. Les anciens champs de premier niveau `decision` et `reason` sont dépréciés pour `PreToolUse` (`approve` et `block` équivalent à `allow` et `deny`). En mode auto, une réécriture sans `permissionDecision` peut être refusée parce que le serveur a examiné l'entrée d'origine [D1].

Décision de premier niveau, valable pour `UserPromptSubmit`, `UserPromptExpansion`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `Stop`, `SubagentStop`, `ConfigChange` et `PreCompact` (documentation) :

```json
{ "decision": "block", "reason": "Le contrôle des sources doit passer avant la fin du tour." }
```

`Stop`, blocage (exécuté) :

```json
{ "decision": "block", "reason": "Avant de terminer, ajoute une derniere ligne contenant exactement FIN-CONTROLE." }
```

`Stop` et `SubagentStop`, retour non bloquant qui prolonge le tour sans signaler d'erreur (documentation) :

```json
{ "hookSpecificOutput": { "hookEventName": "Stop", "additionalContext": "Le fichier de passation n'a pas été mis à jour depuis la dernière écriture." } }
```

`UserPromptSubmit`, contexte ajouté (exécuté) :

```json
{ "hookSpecificOutput": { "hookEventName": "UserPromptSubmit", "additionalContext": "Le numero de role fictif de l'essai est 99-ESSAI." } }
```

`UserPromptSubmit`, blocage (documentation) : `reason` est montré à l'utilisateur et n'entre pas dans le contexte ; `suppressOriginalPrompt` retire le texte du message de blocage, mais il reste dans la transcription sur disque.

```json
{
  "decision": "block",
  "reason": "Explication montrée à l'utilisateur",
  "hookSpecificOutput": { "hookEventName": "UserPromptSubmit", "suppressOriginalPrompt": true }
}
```

`SessionStart`, contexte de départ (exécuté) :

```json
{ "hookSpecificOutput": { "hookEventName": "SessionStart", "additionalContext": "Le mot de controle de cette session est GRENADINE-47." } }
```

`PostToolUse`, contexte ajouté au résultat (documentation) :

```json
{ "hookSpecificOutput": { "hookEventName": "PostToolUse", "additionalContext": "Trois références de l'écriture ne sont pas résolues dans etat/sources.json." } }
```

`PreCompact` : texte brut sur la sortie standard en code 0, lu comme instruction de résumé ; un blocage s'écrit par code 2 ou `{"decision": "block"}`. Bloquer une compaction déclenchée par une erreur de limite de contexte fait échouer la requête [D1].

`SubagentStop` : même format que `Stop`. Pour injecter du contexte dans la session parente après le retour d'un sous-agent, la documentation renvoie à un `PostToolUse` sur l'outil `Agent` [D1].

Gestionnaire `prompt` sur `Stop` (documentation) et forme de réponse attendue du modèle :

```json
{ "hooks": { "Stop": [ { "hooks": [ { "type": "prompt", "prompt": "Évalue si Claude peut s'arrêter : $ARGUMENTS. Toutes les obligations bloquantes sont-elles satisfaites ?" } ] } ] } }
```

```json
{ "ok": false, "reason": "L'obligation de preuve de l'urgence reste ouverte." }
```

Sur `Stop` et `SubagentStop`, `ok: false` renvoie la raison comme instruction suivante, sauf si le modèle ajoute `impossible: true`. Sur `PreToolUse`, `ok: false` refuse l'appel et, par défaut, termine le tour ; `continueOnBlock: true` renvoie la raison à Claude [D1].

Entrées utiles : champs communs `session_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`, `prompt_id`, `scratchpad_dir`, `effort`, et dans un sous-agent `agent_id`, `agent_type`. `PreToolUse` reçoit `tool_name`, `tool_input`, `tool_use_id` ; `PostToolUse` ajoute `tool_response` et `duration_ms` ; `Stop` reçoit `stop_hook_active`, `last_assistant_message`, `background_tasks`, `session_crons` ; `PreCompact` reçoit `trigger` et `custom_instructions` ; `SessionStart` reçoit `source`. La transcription est écrite de façon asynchrone : pour le dernier message, lire `last_assistant_message` [D1].

### B.5 Plugin

Arborescence par défaut [D2] :

```text
contentieux/
├── .claude-plugin/plugin.json   (seul fichier dans .claude-plugin/)
├── skills/<nom>/SKILL.md
├── agents/<nom>.md
├── hooks/hooks.json
├── .mcp.json
├── bin/                          (ajouté au PATH de l'outil Bash)
└── scripts/
```

`plugin.json` minimal (exécuté, validé) ; `name` est le seul champ requis, en kebab-case, et préfixe tous les composants (`contentieux:juge-simule`) :

```json
{
  "name": "essai-hooks",
  "version": "0.1.0",
  "description": "Plugin minimal de vérification des formats de hooks",
  "author": { "name": "Essai" }
}
```

Autres champs : `displayName`, `homepage`, `repository`, `license`, `keywords`, `defaultEnabled`, `dependencies`, `userConfig` (valeurs demandées à l'activation, exposées aux hooks en `CLAUDE_PLUGIN_OPTION_<CLÉ>`), `engines`, et des chemins de composants (`skills` s'ajoute au dossier par défaut ; `commands` et `agents` le remplacent ; `hooks` et `mcpServers` fusionnent). Tout chemin commence par `./`, reste dans le plugin et doit exister. Un `CLAUDE.md` à la racine du plugin n'est pas chargé. Un champ inconnu de premier niveau est retiré avec un avertissement [D2].

`hooks/hooks.json` (exécuté, validé) : le fichier enveloppe la table des événements dans une clé `hooks` et accepte un champ `description` :

```json
{
  "description": "Hooks d'essai",
  "hooks": {
    "SessionStart": [
      { "matcher": "startup|resume|clear|compact",
        "hooks": [ { "type": "command", "command": "python", "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/hook.py"], "timeout": 15 } ] }
    ],
    "PreToolUse": [
      { "matcher": "Bash|PowerShell",
        "hooks": [ { "type": "command", "command": "python", "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/hook.py"], "timeout": 10, "onFailure": "block" } ] }
    ]
  }
}
```

Les outils d'un serveur MCP embarqué dans un plugin s'appellent `mcp__plugin_<plugin>_<serveur>__<outil>`, et un matcher écrit sur le nom nu du serveur ne les atteint pas [D1].

### B.6 Marketplace locale

`.claude-plugin/marketplace.json` à la racine de la marketplace (exécuté, validé) ; `name`, `owner` et `plugins` sont requis ; chaque entrée a `name` et `source`, chemin relatif à la racine qui contient `.claude-plugin/`, sans `..` [D3] :

```json
{
  "name": "essai-local",
  "owner": { "name": "Essai" },
  "plugins": [
    { "name": "essai-hooks", "source": "./plugins/essai-hooks", "description": "Plugin minimal de vérification des formats" }
  ]
}
```

Commandes [D3] :

```bash
claude plugin validate ./ma-marketplace
claude plugin marketplace add ./ma-marketplace
claude plugin install essai-hooks@essai-local
claude plugin list
```

Dans une session, `/plugin marketplace add ./ma-marketplace` et `/plugin install <plugin>@<marketplace>`. Avec une source relative dans une marketplace ajoutée depuis un chemin local, les fichiers sont lus en place : une modification prend effet à la session suivante ou après `/reload-plugins`, sans changer `version`. Pour le développement, `claude --plugin-dir <dossier>` charge un plugin sans marketplace. Le nom de l'entrée et le `name` du manifeste doivent être identiques [D3, D7]. Pour ce dépôt, la marketplace déclarée s'appelle `legal-agent-harness` et l'installation s'écrirait `claude plugin install contentieux@legal-agent-harness`.

### B.7 Frontmatter d'un skill

Tous les champs sont facultatifs ; `description` est recommandée. Les noms de champs sont en minuscules à tirets, sauf `when_to_use`, et un champ mal orthographié est ignoré sans erreur [D4].

```yaml
---
name: verifier-citation
description: Vérifie une citation juridique à la source officielle avant son emploi dans un acte.
allowed-tools: Read Grep
---
```

Champs principaux : `name` (nom de commande, préfixé par le plugin : `/contentieux:verifier-citation`), `description` et `when_to_use` (tronqués ensemble à 1 536 caractères dans la liste des skills), `argument-hint`, `arguments`, `disable-model-invocation` (le modèle ne peut pas lancer le skill ; pour les workflows à effet comme un dépôt), `user-invocable: false` (caché du menu), `allowed-tools` (outils sans demande pendant le tour), `disallowed-tools`, `model`, `effort`, `context: fork` et `agent` (exécution dans un sous-agent), `hooks`, `paths` (chargement limité à des fichiers), `shell`. Substitutions dans le corps : `$ARGUMENTS`, `$0`, `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`, `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_SESSION_ID}`. Le corps d'un skill chargé reste dans le contexte pendant les tours suivants [D4].

### B.8 Frontmatter d'un sous-agent

`name` et `description` sont requis ; les noms de champs composés sont en camelCase [D5].

```yaml
---
name: relecteur
description: Relit un acte à froid, sans les notes de l'équipe.
tools: Read, Grep, Glob
model: opus
---
```

Champs : `tools` (liste ou chaîne ; tous les outils hérités si absent), `disallowedTools`, `model` (`sonnet`, `opus`, `haiku`, `fable`, identifiant complet ou `inherit`), `effort`, `maxTurns`, `skills` (contenu complet préchargé), `memory` (`user`, `project`, `local`), `background`, `omitClaudeMd` (2.1.271 et plus), `isolation: worktree`, `color`, `autoCompactWindow`, `initialPrompt`, `permissionMode`, `mcpServers`, `hooks`. Pour un agent de plugin, `hooks`, `mcpServers` et `permissionMode` sont ignorés, et `initialPrompt` aussi d'après le tableau de la documentation. Le nom ne peut pas contenir `:`. Le corps devient le prompt système ; le sous-agent ne reçoit pas le prompt système de Claude Code mais charge par défaut les fichiers `CLAUDE.md`. Les agents d'un plugin s'appellent `<plugin>:<nom>` et un sous-dossier de `agents/` entre dans ce nom [D5].

### B.9 Vérifications effectuées

Le 18 novembre 2026, avec Claude Code 2.1.317, dans le dossier temporaire de session :

- `claude plugin validate` a accepté le plugin d'essai (manifeste, `hooks/hooks.json`, un skill, un agent) et la marketplace d'essai, avec des avertissements sans incidence (icône, description de marketplace).
- Une exécution `claude -p --plugin-dir` a montré que le contexte de `SessionStart` arrive au modèle et qu'un refus `PreToolUse` est rendu au modèle avec sa raison, sous la forme `PreToolUse:Bash hook error: <raison>`.
- Une seconde exécution a montré que le contexte de `UserPromptSubmit` arrive au modèle et qu'un `Stop` en `decision: "block"` relance le tour, la garde sur `stop_hook_active` évitant la boucle.
- `claude plugin validate ./plugins/contentieux` passe sur le plugin actuel ; le seul défaut signalé (absence de licence) ne concerne que la soumission au répertoire d'Anthropic.

Les autres exemples de cette section n'ont pas été exécutés.

## C. Ce qu'il faut éviter

### C.1 Pratiques

- Faire débattre des agents jusqu'à leur accord, ou tenir l'accord de plusieurs instances d'un même modèle pour une preuve. À coût égal, le débat ne fait pas mieux que le vote ; le gain vient surtout de l'agrégation ; des réponses justes se perdent par conformité au fil des tours [V6, V8, V9, V10].
- Laisser l'auteur évaluer son propre travail ou laisser le relecteur voir le raisonnement qui a produit le texte. Les modèles se notent avec indulgence et répètent les erreurs qu'ils lisent [A5, V1, V13, V14].
- Enchaîner des passes de « révision » sans signal externe. Elles n'améliorent pas le raisonnement et peuvent le dégrader [V2, V6, V7].
- Demander à un relecteur de « trouver les problèmes » sans périmètre ni règle d'arbitrage. Il en trouve toujours, et tout appliquer produit un texte surchargé de précautions [A9].
- Se fier à la recherche sur la version en vigueur ou à une promesse « sans hallucination ». La recherche statique ne retrouve jamais la version applicable dans FiscalQA Pro, et les outils commerciaux annoncés comme fiables hallucinent dans 17 à 33 % des cas [L11, L1].
- Vérifier une référence sur l'existence de son seul numéro. Le TA d'Orléans relève des numéros réels associés à de mauvaises dates et une décision réelle hors sujet [L14].
- Confier un juge LLM à la justesse temporelle ou à la vérification d'existence ; ces contrôles se programment [L11].
- Découper la rédaction d'un même acte entre agents parallèles. Leurs décisions implicites divergent [P2, A3].
- Écrire des règles en majuscules, des « réfléchis davantage » ou « continue jusqu'au bout » ; l'effort se règle par le champ `effort`, et une règle sans exception relève d'un hook [A9].
- Allonger `CLAUDE.md` et y décrire l'organisation des fichiers ; l'adhésion baisse avec la longueur [A9, D6].
- Écrire des garde-fous qui échouent ouverts : code 1, délai, mauvais chemin, sortie standard polluée par un profil de shell [D1].
- Placer des hooks dans le frontmatter d'un agent de plugin ; ils sont ignorés [D5].
- Ajouter ou retirer des outils ou des serveurs MCP au milieu d'une session [P1].
- Effacer du journal les appels d'outils échoués ; leur trace aide l'agent à ne pas les répéter [P1].
- Remplir le contexte d'écritures antérieures très semblables comme modèles ; l'agent imite le motif répété au-delà de son utilité [P1].
- Reprendre une mention « vérifié » héritée d'un audit antérieur ou d'une mémoire persistante sans revérifier. Le dépôt droit-francais-skill en fait un mode d'erreur (validation héritée) et memoforge cache aux auditeurs les verdicts antérieurs [G3, G2]. C'est une pratique de praticiens, sans mesure publiée.

### C.2 Briques

| Brique | Constat au 18/11/2026 | Usage recommandé |
| :- | :- | :- |
| anthropics/knowledge-work-plugins, plugin `legal` (Apache-2.0, 36 437 étoiles pour le dépôt entier) | Juristes d'entreprise, positions américaines par défaut, neuf skills, aucun hook ni contrôle des sources, connecteurs Slack, Box, DocuSign | Ne pas installer ; l'idée d'un fichier local de positions (`.claude/legal.local.md`) se transpose |
| gregmos/memoforge (MIT, 43 étoiles, dernier envoi 29/09/2026) | Plugin multi-agents de mémos (droit américain et européen, sortie .docx) ; audit mécanique puis sémantique des citations, relecteurs isolés, médiateur, garde d'arrêt optionnelle, hooks en forme exec avec trois interpréteurs pour Windows | Motifs à reprendre, code à ne pas importer |
| brissonjo-sudo/droit-francais-skill (EUPL-1.2, 11 étoiles, actif le 17/11/2026) | Méthode de recherche en droit français, dix-huit modes d'erreur, contrôle de vigueur, outils Légifrance et Judilibre ; version 0.9.0 candidate, aucun résultat de mesure publié | Taxonomie comme liste de contrôle |
| matematicsolutions/fr-eli-mcp (Apache-2.0, 2 étoiles, actif le 24/09/2026) | Serveur Légifrance par PISTE, publié sur PyPI ; codes, LODA, JURI, CONSTIT, CETAT, CNIL, KALI ; texte exact, ECLI, `eli_uri` | Connecteur officiel de secours, à tester |
| jmtanguy/droit-francais-mcp (MIT, 38 étoiles, dernier envoi 21/11/2025) | Serveur Légifrance et Judilibre par PISTE ; projet présenté comme exploratoire | Second choix de secours |
| pylegifrance/mcp-server-legifrance (MIT, 66 étoiles, dernier envoi 29/06/2025) | Expérimental, dépend d'une clé d'un service tiers | À écarter |
| cyanheads/eur-lex-mcp-server (Apache-2.0, 13 étoiles, actif le 15/11/2026) | Législation de l'Union, jurisprudence de la CJUE, graphe CELLAR ; seule la description a été lue | À évaluer pour le droit de l'Union |
| Serveurs CourtListener (freelawproject/courtlistener-mcp créé le 10/11/2026, blakeox, john-walkoe) | Droit américain ; seule la description a été lue | Hors périmètre, sauf droit comparé |
| Autres plugins juridiques Claude Code (codearranger/claude-legal, uk-agents/uk-legal-plugins, evolsb/claude-legal-skill, zubair-trabzada/ai-legal-claude, FutureRootsDE/legal-audit-de) | Droits américain, britannique ou allemand, ou revue de contrats ; descriptions seules | Aucun réemploi direct |
| LibreJustice (connecteur déjà configuré) | Recherche sémantique de décisions françaises et européennes, normes à date, adresse officielle, chronologie de l'affaire ; utilisé ici pour lire le jugement du TA d'Orléans | Source principale, avec connecteur de secours |

## D. Sources et statut de lecture

### Anthropic et documentation Claude Code

- [A1] Anthropic, « Building effective agents », 19 décembre 2024. https://www.anthropic.com/engineering/building-effective-agents. Lu.
- [A2] Anthropic, « Effective context engineering for AI agents », 29 septembre 2025. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents. Lu en entier.
- [A3] Anthropic, « How we built our multi-agent research system », 13 juin 2025. https://www.anthropic.com/engineering/multi-agent-research-system. Lu en entier.
- [A4] Anthropic, « Effective harnesses for long-running agents », 26 novembre 2025. https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents. Lu en entier.
- [A5] Anthropic, « Harness design for long-running application development », 24 mars 2026. https://www.anthropic.com/engineering/harness-design-long-running-apps. Lu jusqu'aux résultats du harnais simplifié ; la fin de l'article n'a pas été lue.
- [A6] Anthropic, « Writing effective tools for agents, with agents », 11 septembre 2025. https://www.anthropic.com/engineering/writing-tools-for-agents. Passages lus (principes, évaluation).
- [A7] Anthropic, « Equipping agents for the real world with Agent Skills », 16 octobre 2025. https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills. Passages lus.
- [A8] Anthropic, « Managing context on the Claude Developer Platform » (édition du contexte et outil de mémoire), 29 septembre 2025. https://www.anthropic.com/news/context-management. Lu.
- [A9] Claude Code, « Best practices ». https://code.claude.com/docs/en/best-practices. Lu (sections citées, dont le tableau des conseils abandonnés). L'ancienne adresse https://www.anthropic.com/engineering/claude-code-best-practices redirige vers cette page.
- [D1] Claude Code, « Hooks reference ». https://code.claude.com/docs/en/hooks. Lu (cycle de vie, configuration, codes de sortie, sortie JSON, événements cités, hooks prompt et agent).
- [D2] Claude Code, « Plugin manifest reference ». https://code.claude.com/docs/en/plugins-reference. Lu.
- [D3] Claude Code, « Create a marketplace ». https://code.claude.com/docs/en/plugin-marketplaces. Lu en entier.
- [D4] Claude Code, « Extend Claude with skills ». https://code.claude.com/docs/en/skills. Lu (configuration et frontmatter).
- [D5] Claude Code, « Create custom subagents ». https://code.claude.com/docs/en/sub-agents. Lu (portées, frontmatter, agents de plugin).
- [D6] Claude Code, « Memory ». https://code.claude.com/docs/en/memory. Passages lus (taille, imports, compaction).
- [D7] Claude Code, « Plugins ». https://code.claude.com/docs/en/plugins. Passages lus (`--plugin-dir`).

### Praticiens

- [P1] Yichao Ji, « Context Engineering for AI Agents: Lessons from Building Manus », 18 juillet 2025. https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus. Lu en entier.
- [P2] Walden Yan, « Don't Build Multi-Agents », Cognition, 12 juin 2025. https://cognition.ai/blog/dont-build-multi-agents. Lu en entier.
- [P3] Hong et al., « Context Rot: How Increasing Input Tokens Impacts LLM Performance », Chroma, 14 juillet 2025. https://research.trychroma.com/context-rot. Passages lus.
- [P4] Letta, « Benchmarking AI Agent Memory: Is a Filesystem All You Need? », 12 août 2025. https://www.letta.com/blog/benchmarking-ai-agent-memory. Résumé lu.

### Vérification et débat

Les lieux de publication indiqués sont ceux qui figurent sur la première page du texte téléchargé ; à défaut, seule l'année de mise en ligne est donnée.

- [V1] Dhuliawala et al., « Chain-of-Verification Reduces Hallucination in Large Language Models », 2023. arXiv:2309.11495. Résumé et passages sur les variantes jointe et factorisée lus.
- [V2] Gou et al., « CRITIC: Large Language Models Can Self-Correct with Tool-Interactive Critiquing », ICLR 2024. arXiv:2305.11738. Résumé et introduction lus.
- [V3] Madaan et al., « Self-Refine: Iterative Refinement with Self-Feedback », 2023. arXiv:2303.17651. Résumé lu.
- [V4] Shinn et al., « Reflexion: Language Agents with Verbal Reinforcement Learning », 2023. arXiv:2303.11366. Résumé lu.
- [V5] Du et al., « Improving Factuality and Reasoning in Language Models through Multiagent Debate », 2023. arXiv:2305.14325. Résumé lu.
- [V6] Huang et al., « Large Language Models Cannot Self-Correct Reasoning Yet », ICLR 2024. arXiv:2310.01798. Résumé, introduction, tableau 1 et conclusion lus.
- [V7] Kamoi et al., « When Can LLMs Actually Correct Their Own Mistakes? A Critical Survey of Self-Correction of LLMs », 2024. arXiv:2406.01297. Résumé lu.
- [V8] Smit et al., « Should we be going MAD? A Look at Multi-Agent Debate Strategies for LLMs », ICML 2024. arXiv:2311.17371. Résumé lu.
- [V9] Choi, Zhu, Li, « Debate or Vote: Which Yields Better Decisions in Multi-Agent Large Language Models? », 2025. arXiv:2508.17536. Résumé et section 5 lus.
- [V10] Wynn, Satija, Hadfield, « Talk Isn't Always Cheap: Understanding Failure Modes in Multi-Agent Debate », 2025. arXiv:2509.05396. Résumé et passages lus.
- [V11] Khan et al., « Debating with More Persuasive LLMs Leads to More Truthful Answers », 2024. arXiv:2402.06782. Résumé lu.
- [V12] Cemri et al., « Why Do Multi-Agent LLM Systems Fail? », 2025. arXiv:2503.13657. Résumé, figure 1 et passage sur la catégorie FC3 lus.
- [V13] Panickssery, Bowman, Feng, « LLM Evaluators Recognize and Favor Their Own Generations », 2024. arXiv:2404.13076. Résumé lu.
- [V14] Zheng et al., « Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena », 2023. arXiv:2306.05685. Résumé lu.

### Complaisance

- [Y1] Sharma et al., « Towards Understanding Sycophancy in Language Models », ICLR 2024. arXiv:2310.13548. Résumé, figures 1 et 2 et section 4.3 lus.
- [Y2] Laban et al., « Are You Sure? Challenging LLMs Leads to Performance Drops in The FlipFlop Experiment », 2023. arXiv:2311.08596. Résumé lu.
- [Y3] Fanous et al., « SycEval: Evaluating LLM Sycophancy », 2025 (version 4). arXiv:2502.08177. Résumé lu ; les versions successives diffèrent sur certains chiffres.
- [Y4] Hong et al., « Measuring Sycophancy of Language Models in Multi-turn Dialogues » (SYCON Bench), 2025. arXiv:2505.23840. Résumé et introduction lus.
- [Y5] Kim, Khashabi, « Challenging the Evaluator: LLM Sycophancy Under User Rebuttal », 2025. arXiv:2509.16533. Résumé lu.
- [Y6] Cheng et al., « ELEPHANT: Measuring and Understanding Social Sycophancy in LLMs », 2025. arXiv:2505.13995. Résumé et un tableau d'annexe lus.

### IA juridique

- [L1] Magesh et al., « Hallucination-Free? Assessing the Reliability of Leading AI Legal Research Tools », 2024. arXiv:2405.20362. Résumé, typologie et causes d'erreur lus.
- [L2] Dahl et al., « Large Legal Fictions: Profiling Legal Hallucinations in Large Language Models », 2024. arXiv:2401.01301. Résumé et introduction lus.
- [L3] Guha et al., « LegalBench: A Collaboratively Built Benchmark for Measuring Legal Reasoning in Large Language Models », 2023 (162 tâches, six types de raisonnement, 20 modèles). arXiv:2308.11462. Résumé lu.
- [L4] Chalkidis et al., « LexGLUE: A Benchmark Dataset for Legal Language Understanding in English », 2021. arXiv:2110.00976. Résumé lu.
- [L5] Fei et al., « LawBench: Benchmarking Legal Knowledge of Large Language Models », 2023 (droit chinois, 20 tâches, 51 modèles). arXiv:2309.16289. Résumé lu.
- [L6] Fan et al., « LEXam: Benchmarking Legal Reasoning on 340 Law Exams », ICLR 2026 (7 537 questions en anglais et en allemand). arXiv:2505.12864. Résumé lu.
- [L7] Li et al., « LegalAgentBench », 2024 (droit chinois, 37 outils, 300 tâches). arXiv:2412.17259. Résumé lu.
- [L8] Hou et al., « CLERC: A Dataset for Legal Case Retrieval and Retrieval-Augmented Analysis Generation », 2024. arXiv:2406.17186. Résumé lu.
- [L9] Pipitone, Houir Alami, « LegalBench-RAG », 2024. arXiv:2408.10343. Résumé lu.
- [L10] Scale AI, « PRBench: Large-Scale Expert Rubrics for Evaluating High-Stakes Professional Reasoning », 2025. arXiv:2511.11562. Résumé lu.
- [L11] Cymbler et al., « Temporal Misgrounding in Legal RAG: A Versioned-Corpus Benchmark for French Tax Law » (FiscalQA Pro), atelier AI4Law, ICML 2026. arXiv:2608.09393. Résumé lu.
- [L12] Abtout et al., « Evaluating RAG for French immigration law: a benchmark and baseline study », 2026. arXiv:2607.24449. Résumé lu (52 profils synthétiques ; la recherche documentaire améliore l'orientation administrative).
- [L13] Damien Charlotin, « AI Hallucination Cases Database », état du 16 novembre 2026. https://www.damiencharlotin.com/hallucinations/. Résumé lu.
- [L14] TA Orléans, 29 décembre 2025, n° 2506461. https://opendata.justice-administrative.fr/recherche/shareFile/TA45/DTA_2506461_20251229, lu en entier par LibreJustice (https://librejustice.fr/decision/ooQe9c3SO2ef).
- Benchmarks français connus par un résultat de recherche seulement, non vérifiés : Les-Audits-Affaires (droit des affaires, Hugging Face), IRA-Bench (questions de concours des IRA), LLeQA (questions juridiques en français, droit belge).

### Dépôts

Constats faits le 18 novembre 2026 par l'API publique de GitHub (étoiles, dates, licences).

- [G1] anthropics/knowledge-work-plugins, dossier `legal`. https://github.com/anthropics/knowledge-work-plugins. Lu (manifeste, `.mcp.json`, README, skill `review-contract`, début de la marketplace).
- [G2] gregmos/memoforge. https://github.com/gregmos/memoforge. Lu (`hooks/hooks.json`, agents `revision-mediator` et `citation-auditor`, début de `hooks/stop_guard.py`).
- [G3] brissonjo-sudo/droit-francais-skill. https://github.com/brissonjo-sudo/droit-francais-skill. Lu (README, `skill/references/modes-erreur.md`, `docs/campagne-18-modes.md`, manifeste).
- [G4] jmtanguy/droit-francais-mcp. https://github.com/jmtanguy/droit-francais-mcp. README lu.
- [G5] matematicsolutions/fr-eli-mcp. https://github.com/matematicsolutions/fr-eli-mcp. README lu.
- [G6] pylegifrance/mcp-server-legifrance. https://github.com/pylegifrance/mcp-server-legifrance. README lu.
- [G7] cyanheads/eur-lex-mcp-server. https://github.com/cyanheads/eur-lex-mcp-server. Description seule, non vérifié.
- [G8] freelawproject/courtlistener-mcp, blakeox/courtlistener-mcp, john-walkoe/courtlistener_citations_mcp. Descriptions seules, non vérifié.
- [G9] codearranger/claude-legal, uk-agents/uk-legal-plugins, evolsb/claude-legal-skill, zubair-trabzada/ai-legal-claude, FutureRootsDE/legal-audit-de. Descriptions seules, non vérifié.

### Vérifications locales

- [E1] Essais du 18 novembre 2026 avec Claude Code 2.1.317 : `claude plugin validate` sur un plugin et une marketplace d'essai et sur `plugins/contentieux` ; deux exécutions `claude -p --plugin-dir` testant `SessionStart`, `UserPromptSubmit`, `PreToolUse` et `Stop` (section B.9).
