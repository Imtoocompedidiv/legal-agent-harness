# Intégration du module « recherche et lecture des textes »

Module livré sans toucher aux fichiers partagés :
- `scripts/lectures.py` : registre mécanique des lectures et contrôles ;
- `references/schemas/fiche_lecture.v1.schema.json` : schéma des fiches de lecture ;
- `agents/lecteur-de-texte.md` : nouveau sous-agent ;
- `skills/recherche-juridique/SKILL.md`, `agents/chercheur-juridique.md`, `agents/verificateur-sources.md` : refondus ;
- `tests/test_recherche.py` : tests, dont quatre qui ne s'exécutent qu'une fois le correctif appliqué ;
- onze sondes du banc `RECH2-*` et `LECT2-*` dans `validation/banc/sondes/`.

Ce document donne le correctif à appliquer aux fichiers que d'autres modules touchent aussi.

## Application

Le correctif est `integration/recherche.patch` (diff unifié, chemins relatifs à la racine du plugin). Depuis `plugins/contentieux` :

```
patch -p1 --binary --dry-run < integration/recherche.patch
patch -p1 --binary < integration/recherche.patch
python -m pytest -q plugins/contentieux/tests -p no:cacheprovider      (depuis la racine du dépôt)
```

Le correctif a été rebasé le 20 novembre 2026 vers 2 h 05 sur les fichiers partagés du plugin courant, qui portaient alors le correctif des positions (`positions.py`) et un `hooks/hooks.json` réécrit en fins de ligne LF, sans l'ajout de `doctrine.patch`. Il s'appliquait sans rejet ni décalage sur une copie de ce plugin, où la suite complète passait : 270 tests réussis, 3 ignorés, dont les six tests d'intégration de `test_recherche.py`. Sur le plugin courant sans le correctif, la suite passait aussi : 265 réussis, 8 ignorés. `test_recherche.py` passe seul (35 tests, 6 ignorés) et ne dépend d'aucun fichier partagé.

Composition avec `doctrine.patch` : le 19 novembre vers 23 h 50, les deux correctifs s'appliquaient dans les deux ordres (225 tests verts). Le 20 novembre à 2 h 10, le plugin courant porte déjà les ajouts de `doctrine.patch` dans `scripts/gate.py` et `scripts/hook.py`, mais pas le filtre `mcp__annas_archive__.*` de `hooks/hooks.json`. Le bloc de `doctrine.patch` pour ce fichier ne s'applique plus, parce qu'il a été pris sur la version CRLF. `recherche.patch` est rebasé sur cet état et s'y applique sans rejet ni décalage.

Appliquer avec `--binary` : `hooks/hooks.json` a changé de fins de ligne pendant l'intégration (CRLF, puis LF), et un diff pris sur l'une ne s'applique pas sur l'autre. Si un autre module a modifié entre-temps les mêmes lignes, appliquer à la main les changements décrits ci-dessous ; chaque emplacement est donné par la ligne qui le précède.

## 1. `hooks/hooks.json` : la capture

Ajouter au tableau `PostToolUse` une seconde entrée, à côté de celle des écritures. Elle porte le filtre `mcp__librejustice__.*|mcp__legal_harness__read_document`, appelle `python ${CLAUDE_PLUGIN_ROOT}/scripts/hook.py` et a un délai de 30 secondes. La description du fichier mentionne le registre des lectures.

Le PreToolUse couvre déjà `mcp__librejustice__.*` pour les identifiants privés ; rien n'y change.

## 2. `scripts/hook.py`

**PostToolUse, au début de `post_tool`**, après le calcul de la racine. Pour un outil `mcp__*` que `lectures.est_capturable` retient, appeler `lectures.capturer(racine, ev)`, qui écrit `recherche/lectures/<horodatage>_<rang>_<outil>_<empreinte>.json` et ajoute une ligne à `recherche/lectures/registre.jsonl`. La capture garde :
- l'outil et l'entrée ;
- `L.horodatage()`, qui suit `CONTENTIEUX_MAINTENANT`, et l'horloge fixée s'il y en a une ;
- la session, l'agent et l'identifiant de l'appel ;
- la réponse brute, telle que Claude Code la transmet.

La forme de `tool_response` a été relevée sur un événement PostToolUse réel d'un appel LibreJustice : une chaîne JSON, accents intacts. `lectures.decoder` accepte aussi les blocs de contenu MCP et un objet. Une exception de capture ne bloque pas l'outil, qui a déjà répondu : elle renvoie un contexte qui dit que la lecture n'est pas au registre.

**PostToolUse, validation des fiches.** À l'écriture de `recherche/fiches/<id>.json`, appeler `lectures.valider_fiche(racine, id)`. Une erreur renvoie `{"decision": "block"}` avec la liste ; une alerte renvoie un contexte.

**PreToolUse, protection du registre.** Ajouter `^recherche/lectures/` à `PROTEGES`, qui refuse Write, Edit, MultiEdit et NotebookEdit. Ajouter `recherche[\\/]+lectures` à `CHEMINS_SENSIBLES`, qui refuse une commande Bash ou PowerShell destructive visant ces chemins. Le hook écrit les captures en Python, hors de ces outils, et n'est donc pas gêné. Une capture modifiée par une autre voie se détecte à son empreinte : `Registre` l'écarte et le contrôle bloque (`REGISTRE_LECTURES_ALTERE`).

**PreToolUse, fiches de lecture.** `recherche/fiches/` ne s'écrit que par un agent dont le type se termine par `lecteur-de-texte`, sur le modèle de `pieces/analyses/` et de l'`analyste-documentaire`.

**UserPromptSubmit, rappel du protocole.** Quand le message contient une question, ou une demande de rédaction ou de vérification (rédige, prépare, vérifie, note, mémoire, requête, réplique, conclusions, courriel, lettre, moyen, pourvoi, assignation, recours), `user_prompt` ajoute un rappel des passes de la skill `recherche-juridique` :
- texte décisif lu à la date utile, avec sa section, ses renvois et son texte modificatif ;
- jurisprudence cherchée par `legal_article`, publiée puis inédite ;
- suite de chaque décision citée, même reprise d'une note ;
- meilleure autorité contraire ;
- prémisses de la demande (délai, juridiction, autorité d'une décision) vérifiées à la source.

Le rappel donne aussi la commande `lectures.py citations`, avec le chemin réel du plugin. Il est inséré avant la ligne `prompt = ev.get("prompt") or ""`.

**SessionStart, même rappel au briefing**, juste après la ligne « Objectif du client ». En mode non interactif (`claude -p`, celui du banc), le flux des sessions montre le hook SessionStart et aucun UserPromptSubmit : le rappel de `user_prompt` n'y arrive pas, et le briefing est le seul contexte reçu à coup sûr. Sa raison est mesurée : dans tous les passages des sondes `RECH2-` et `LECT2-`, avant et après la refonte, aucun agent n'a chargé la skill. Une question directe ou une rédaction reçoit une réponse directe, et la refonte des consignes reste sans effet tant que rien ne la rappelle.

**Stop, `controle_lectures`.** Une décision dont une capture `get_decision` rend le texte compte comme lue. Jusqu'ici, le hook la tenait pour non ouverte quand elle avait été lue par son adresse LibreJustice, qui ne porte pas son numéro.

La documentation en tête de `hook.py` mentionne la capture.

## 3. `scripts/gate.py` : les blocages

Après le contrôle documentaire (`PIECES.controle_documentaire`), avant les objections dirimantes, appeler `lectures.controler(racine, ecriture, fiche, texte, c)`. Pour un écrit qui n'est pas porté devant un juge, ses blocages deviennent des alertes, comme pour le contrôle documentaire.

Bloquent :

| Code | Défaut |
| --- | --- |
| `DECISION_CITEE_NON_LUE` | décision citée qu'aucune capture `get_decision` ne rend ; le message dit si elle n'a été vue qu'en aperçu de recherche |
| `DECISION_CITEE_DEFAITE` | décision citée dont `standing` ou la décision qui la suit dans `case_chronology` montre une annulation, une cassation, une infirmation ou une réformation, sans que l'écriture le dise (mention du numéro de la décision ultérieure, ou d'une annulation ou cassation dans le paragraphe de la citation) |
| `CITATION_INTROUVABLE` | passage entre guillemets attribué à une décision, un article ou une pièce, absent mot pour mot de la source lue ; le message donne le passage le plus proche de la source quand il existe, ou dit que la source n'a jamais été lue |
| `CITATION_APERCU` | passage retrouvé seulement dans un aperçu de recherche (`ai_summary`, `court_summary` ou `snippet` d'une liste) |
| `ARTICLE_NON_LU_A_DATE` | article dont le texte est nommé (code, loi, décret, ordonnance, Constitution) et qui n'a pas été lu dans une version couvrant la date utile |
| `REGISTRE_LECTURES_ALTERE` | capture modifiée, écrite hors du hook ou illisible |

Restent des alertes, parce qu'un examen peut les justifier ou parce que le repérage mécanique y est moins sûr :
- `ARTICLE_SECTION_NON_LUE` ;
- `ARTICLE_RENVOIS_NON_SUIVIS` ;
- `JURISPRUDENCE_PAR_ARTICLE_NON_CHERCHEE` ;
- `DATE_UTILE_NON_DECLAREE`, pour un texte qui a connu plusieurs versions ;
- `ARTICLE_NON_LU`, quand le texte de l'article n'est pas identifié dans l'écriture ;
- `CITATION_MAL_ATTRIBUEE`, quand le passage se lit dans une autre source que celle annoncée ;
- `CITATION_AUTRE_VERSION` ;
- `CITATION_SOMMAIRE`, pour un passage pris dans le sommaire ou l'analyse ;
- `CITATION_NON_ATTRIBUEE`, pour un passage sans source annoncée et introuvable ;
- `DECISION_SUITE_INCONNUE` ;
- `DECISION_DEFAITE_SIGNALEE` ;
- `SOURCE_DECLAREE_SANS_LECTURE`, pour une décision déclarée lue dans `etat/sources.json` sans capture ;
- `REGISTRE_LECTURES_SUPPRESSION`.

Aucun de ces codes ne commence par un préfixe que `controles_campagne.DIFFERABLES` diffère en mode conservatoire (`LECTURE_` en fait partie, d'où le nom `REGISTRE_LECTURES_ALTERE`) : une requête conservatoire ne cite pas non plus une décision annulée ni une citation fausse.

La date utile vient, dans l'ordre :
- de `dates_utiles` dans la fiche de l'acte, par article, sous la clé « <code>|<article> » ;
- de `date_droit_applicable` dans la fiche ;
- d'une ligne « Date utile : AAAA-MM-JJ » du texte ;
- à défaut, des dates des actes attaqués et du jour du contrôle, qui sont admises.

## 4. `skills/controle-avant-depot/SKILL.md`

Le correctif ajoute à la liste des champs de la fiche `date_droit_applicable` et `dates_utiles`, une section « 1 quinquies. Lectures » qui énumère les blocages et les alertes ci-dessus, et, au § 2, la règle selon laquelle `lu_en_entier` n'est vrai que si le registre capture le texte.

## 5. `tests/test_contentieux.py`

`TestGate.test_refere_conforme_puis_finalisation` attend l'ensemble exact des bloquants d'un référé conforme. Ce référé cite l'article L. 521-1 du CJA et la décision n° 123456 : le correctif ajoute, avant le deuxième contrôle, deux captures synthétiques de ces sources. Sans elles, le référé « conforme » serait bloqué, à juste titre, pour une décision jamais lue et un article jamais lu.

## 6. `templates/affaire/LISEZMOI.md`, `README.md`, `docs/ARCHITECTURE.md`

Une ligne pour `recherche/lectures/` et une pour `recherche/fiches/` dans la table du dossier ; `lecteur-de-texte` dans la liste des sous-agents ; l'étape 4 du flux décrit le ratissage, le registre et les blocages.

## 7. Coordination avec le module doctrine

Les ajouts que `integration/doctrine.md` (§ 4 et 5) proposait pour `skills/recherche-juridique/SKILL.md` et `agents/chercheur-juridique.md` sont déjà dans la version refondue :
- renvoi à `recherche-doctrinale` et à `chercheur-doctrine` ;
- conclusions et chronologie de chaque décision retenue ;
- `fiche_doctrine` ;
- doctrine jamais seule à porter un moyen ;
- outils HAL, theses.fr, OpenAlex, Crossref et Bash du chercheur.

Ne pas les appliquer une seconde fois. Les fiches doctrinales restent dans `recherche/doctrine/` et les fiches de normes et de décisions dans `recherche/fiches/`.

## 8. Effets sur les dossiers existants

Une écriture contrôlée après l'intégration doit avoir été précédée de la lecture capturée de chaque décision et de chaque article qu'elle cite. Les dossiers antérieurs n'ont pas de registre : relire leurs sources dans LibreJustice crée les captures. `banc.py instantanes` fera apparaître ces nouveaux bloquants sur les écritures des épreuves ; les examiner, puis réenregistrer l'instantané. Ce module ne l'a pas lancé, puisqu'il lit des dossiers réels, hors du dépôt.

## 9. Épreuve sur des lectures réelles

Sur une copie du plugin portant le correctif, deux sondes du banc ont tourné en session réelle (le passage a ensuite été interrompu pour ne pas tourner en même temps qu'un autre module). Le hook a capturé 7 et 10 lectures, toutes intègres. Sur la note piégée de `LECT2-CITATIONS-SUBTILES`, `lectures.py citations` a rendu, sans aucun jugement de modèle :
- exacte la citation 1 ;
- inexacte la citation 2, avec le texte de la source (« 31 août 2022 ») ;
- aperçu de recherche pour la citation 3 ;
- inexacte la citation 4, avec le texte de l'article (« plus de deux logements ») ;
- exacte la citation 5.

`lectures.py portee` a trouvé l'arrêt n° 24MA00153 annulé par la décision n° 505796. Sur la note de `LECT2-CITATIONS-EXACTES`, il a rendu exacte, inexacte et introuvable, comme attendu.

Ces lectures réelles ont révélé deux défauts, corrigés et couverts par des tests :
- `portee` tenait l'annulation pour dite dès que le numéro de la décision ultérieure figurait n'importe où dans le texte ; il faut désormais qu'il figure, ou qu'une annulation soit nommée, dans un paragraphe qui cite la décision défaite ;
- « art. R. 811-1-1, 1° » produisait un faux article « 1 ».

## 10. Mesure au banc

Chaque sonde a tourné une fois par version, avec le modèle opus, une sonde à la fois. Les trois versions sont :
- la base : `banc_runs/plugin_base`, figé avant la refonte ;
- la refonte seule : le plugin courant, sans le correctif ;
- la copie corrigée : `banc_runs/plugin_recherche_corrige`, plugin courant avec ce correctif.

Une passe unique par sonde ne mesure pas la variance du modèle : un écart d'une sonde peut tenir au hasard.

**Onze sondes posées de front** (questions directes) :
- base : 11 sur 11, score moyen 0,80 ;
- refonte seule : 11 sur 11, 0,79 ;
- copie corrigée : 11 sur 11, 0,86.

Le score monte avec le correctif par les critères de méthode : la recherche par `legal_article` passe de 0 sur 3 à 3 sur 3. La lecture de la section reste à 0 sur 7 dans les trois versions. Ces sondes sont trop faciles : le savoir est là quand on le demande.

**Dix sondes durcies** (rédaction réelle, point de recherche non demandé) :
- base : 7 sur 10 ;
- copie corrigée : 9 sur 10.

Les trois échecs de la base portent sur une règle de compétence et de notification issue du décret n° 2026-302 (R. 311-5 et R. 77-16-1), que rien de ce que l'agent lit d'abord ne désigne :
- `RECH2-REQUETE-METHANISATION` : 0,00 sur la base, réussie à 0,50 sur la copie corrigée ;
- `RECH2-REQUETE-HYDROELECTRIQUE` : 0,00 sur la base, réussie à 0,75 sur la copie corrigée ;
- `RECH2-REQUETE-DUP-ROUTIERE` : échouée dans les deux versions, à 0,00 puis 0,25.

Dans les deux sondes gagnées, l'agent corrigé a ouvert R. 311-5, et pour la centrale le décret n° 2026-302 lui-même ; l'agent de base ne l'a jamais fait. Les sept autres sondes durcies réussissent dans les deux versions : arrêt annulé cité dans une note, délai augmenté pour l'étranger, citation de la rédaction de 2022, avis contraire de la Cour de cassation, décision récente sur le certificat tacite, opération d'intérêt national, réserve d'irrigation. Le correctif y relève le score de deux d'entre elles, par la recherche par article.

## 11. Limites

- Le repérage des articles cités et de leur texte repose sur des motifs : « article X du code Y », abréviations usuelles, « le code Y, en son article ». Un article cité sans texte identifiable donne une alerte, pas un blocage.
- L'attribution d'une citation se fait au paragraphe : la référence qui suit le passage de près (moins de 80 signes), sinon la plus proche qui le précède. Une note qui cite plusieurs sources dans la même phrase peut être mal rattachée ; le statut `mal_attribuee` le signale en alerte.
- La lecture « en entier » d'une décision s'établit par la capture de `get_decision`, qui rend le texte complet. Le registre ne prouve pas que l'agent l'a lue avec attention ; il prouve qu'elle lui a été servie.
- La suite d'une décision s'établit par ce que LibreJustice en sait (`standing`, `case_chronology`). Une décision ultérieure contraire dans une autre affaire, un revirement, ne se détecte pas mécaniquement ; le protocole impose de la chercher et le `lecteur-de-texte` la porte dans la fiche.
- Les sources lues hors de LibreJustice et de `read_document` (navigateur, base ouverte, ArianeWeb, HUDOC, CURIA) ne sont pas capturées : leurs citations sortent introuvables, en blocage si elles sont attribuées à une décision. Les acquérir par `acquire_source` puis `read_document` les rend vérifiables.
