# Intégration du module « recherche doctrinale »

Module livré sans toucher aux fichiers partagés : `skills/recherche-doctrinale/SKILL.md` et ses deux références (`voies-d-acces.md`, `mobiliser-dans-l-ecriture.md`), `agents/chercheur-doctrine.md`, `scripts/doctrine.py`, `references/schemas/doctrine.v1.schema.json`, `tests/test_doctrine.py`, les sondes `validation/banc/sondes/DOCT-*.json`. Ce document donne le correctif à appliquer aux fichiers que d'autres modules refondent, et les ajouts à proposer aux consignes des agents.

## Application

Le correctif de code est dans `integration/doctrine.patch` (diff unifié, chemins relatifs à la racine du plugin) : `scripts/gate.py`, `scripts/hook.py`, `hooks/hooks.json`. Depuis `plugins/contentieux` :

```
patch -p1 --binary --dry-run < integration/doctrine.patch
patch -p1 --binary < integration/doctrine.patch
python -m pytest -q plugins/contentieux/tests -p no:cacheprovider      (depuis la racine du dépôt)
```

Le 19 novembre 2026 vers 23 h 30, le correctif s'appliquait sans décalage à une copie du plugin courant, seul ou avec `integration/recherche.patch` dans les deux ordres ; la suite complète passait sur la copie portant ce seul correctif (221 tests réussis, 4 ignorés) et sur celle qui porte les deux (225 tests réussis). Essai de bout en bout sur la même copie : une écriture qui cite « RFDA 2019, p. 100 » sans fiche reçoit `DOCTRINE_HORS_FICHE` de `gate.py` ; un appel `download_scihub` est refusé par le hook ; une fiche incomplète écrite dans `recherche/doctrine/` est bloquée à l'écriture ; le briefing de démarrage compte les fiches et celles qui portent sur un texte lu. Sans le correctif, `doctrine.py` fonctionne seul (`python doctrine.py controle <écriture>`) et `test_doctrine.py` ne dépend d'aucun fichier partagé. Si un autre module a modifié entre-temps les mêmes lignes, appliquer à la main les changements décrits ci-dessous ; chaque emplacement est donné par la ligne qui le précède.

## 1. Ce que le contrôle doit vérifier (`scripts/gate.py`)

Dans `controler`, juste après l'appel `NEGOCIATION.controler(...)` :

```python
    import doctrine as DOCTRINE
    DOCTRINE.controler(racine, ecriture, fiche, c, juridictionnel=juridictionnel)
```

`doctrine.controler` appelle `c(code, gravite, message, ligne=...)` au format de `gate.py`. Gravité : bloquant pour tout acte porté devant un juge, alerte pour un courrier. Il vérifie :

| Code | Gravité devant un juge | Règle |
| --- | --- | --- |
| `DOCTRINE_SANS_FICHE` | bloquant | Un identifiant de la liste `doctrine` de la fiche de l'acte n'a pas de fiche `recherche/doctrine/<id>.json`. |
| `DOCTRINE_FICHE_INVALIDE` | bloquant | Un travail cité (marqueur trouvé dans le texte ou identifiant déclaré) a une fiche invalide : schéma, identifiant vérifiable, statut de lecture et obstacle, passages réservés au texte lu, version publiée recherchée, solidité de l'empirique, voie probatoire de l'expertise, aucune source illicite. |
| `DOCTRINE_HORS_FICHE` | bloquant | Une marque de citation savante (DOI, identifiant HAL, numéro national de thèse, « concl. », conclusions du rapporteur public, avis de l'avocat général, rapport du conseiller, « chron. », « note sous », « op. cit. », « et al. », thèse de doctorat, revue suivie d'une année) n'est couverte par le marqueur d'aucune fiche dans la même phrase. |
| `DOCTRINE_CITATION_NON_LUE` | bloquant (alerte sous quatre mots) | Un passage entre guillemets, dans une phrase qui cite un travail, provient d'un travail lu seulement sur sa notice ou son résumé. |
| `DOCTRINE_CITATION_INTROUVABLE` | bloquant (alerte sous quatre mots) | Le passage ne figure ni dans les passages relevés mot pour mot dans la fiche, ni au registre des sources (`etat/sources.json`, champ `passages`), qui couvre les citations de textes et de décisions placées dans la même phrase. |
| `DOCTRINE_SEULE_POUR_REGLE` | bloquant | Un moyen ou une condition de la fiche de l'acte ne repose que sur des sources de type `doctrine` du registre. |
| `DOCTRINE_EMPIRIQUE_FRAGILE` | alerte | Donnée empirique de solidité limitée ou contestée citée. |
| `DOCTRINE_EMPIRIQUE_SANS_POPULATION` | alerte | La phrase qui cite une étude empirique ne donne pas la période étudiée. |
| `DOCTRINE_VERSION_DE_TRAVAIL_CITEE` | alerte | Une version de travail est citée alors que la fiche connaît la version publiée. |

La fiche de l'acte (`ecritures/controle/<nom>.fiche.json`) peut porter `doctrine`, la liste des identifiants des fiches que l'acte emploie ; le contrôle les tient pour cités même si leur marqueur manque au texte.

## 2. `scripts/hook.py` et `hooks/hooks.json`

- `pre_tool`, après la ligne `plugin = os.environ.get("CLAUDE_PLUGIN_ROOT", "<plugin>")` : refuser tout appel que `doctrine.outil_illicite(outil, ti)` désigne (outils Sci-Hub et Anna's Archive, option `use_scihub`, adresse de Sci-Hub, Anna's Archive, LibGen ou Z-Library dans une commande Bash, PowerShell ou WebFetch). Dans `hooks.json`, ajouter `mcp__annas_archive__.*` au filtre du PreToolUse qui couvre déjà `mcp__academic_papers__.*` : le serveur est installé sur le poste.
- `post_tool`, avant `if rel in L.SCHEMAS:` : à l'écriture de `recherche/doctrine/<id>.json`, `doctrine.valider(fiche, id)` ; les constats bloquants renvoient `{"decision": "block"}` avec la liste.
- `user_prompt`, dans la ligne ajoutée quand le message contient une question : une décision qui commande la réponse se lit avec ses conclusions ou son rapport (champ `commentaries`) ; quand la portée d'un texte, une jurisprudence en mouvement, la fiabilité d'une preuve, un fait d'expérience ou une technique décide, chercher et lire les travaux savants (skill `recherche-doctrinale`). Raison : sur le banc, aucun agent n'a chargé un skill de lui-même pour une question posée directement ; le rappel au moment de la question est le seul levier qui atteint ces réponses.
- `briefing`, après la ligne du profil des décideurs : « Doctrine : N fiche(s) de lecture dans recherche/doctrine/, dont M sur texte lu ; les autres ne se citent pas entre guillemets. »

Rien à changer dans `lib_affaire.py` ni dans `affaire.py` : la validation passe par `doctrine.py` (bibliothèque standard et validateur de `pieces.py`), et aucun gabarit n'est ajouté à `templates/affaire/`.

## 3. `skills/controle-avant-depot/SKILL.md`

Dans la liste des préalables : chaque travail cité dans l'acte a sa fiche de lecture valide (skill `recherche-doctrinale`), déclarée au besoin dans la liste `doctrine` de la fiche de l'acte ; aucune citation entre guillemets d'un travail lu sur sa seule notice ou son résumé ; aucun moyen ni condition fondé sur la seule doctrine ; une donnée empirique se cite avec sa population, sa période et sa limite, et se produit en pièce quand elle porte un fait.

## 4. `skills/recherche-juridique/SKILL.md`

- § 2, point 5 « Doctrine » : renvoyer au skill `recherche-doctrinale` et au sous-agent `chercheur-doctrine` ; une fiche de lecture par travail employé, dans `recherche/doctrine/`.
- § 2, point 2 « Jurisprudence » : pour chaque décision qui commande la question, lire le champ `commentaries` de `get_decision` (conclusions, rapport du conseiller, avis de l'avocat général, notice au rapport annuel) et la chronologie de l'affaire ; les conclusions du Conseil d'État se lisent dans le PDF ArianeWeb (`?download_pdf`). La sonde `DOCT-SPONTANE-CONCLUSIONS` mesure ce point : sans les conclusions, l'agent ne voit pas quel fondement la juridiction a retenu ni ce qui survit de la jurisprudence antérieure.
- § 4 « Registre des sources » : une entrée de type `doctrine` renvoie à sa fiche (champ proposé `fiche_doctrine`) ; une source de type `doctrine` ne porte jamais seule un moyen.

## 5. Ajouts proposés à `agents/chercheur-juridique.md`

- Outils à ajouter : `mcp__shs_fr__theses_get`, `mcp__hal__lookup_reference`, `mcp__academic_papers__search_openalex`, `mcp__academic_papers__search_crossref`, `mcp__academic_papers__get_crossref_paper_by_doi`, `mcp__academic_papers__read_hal_paper`, `Bash` (téléchargement d'un PDF officiel et extraction du texte). Aujourd'hui il ne peut ni lire le résumé d'une thèse ni vérifier un DOI.
- Méthode, après le point 3 :

> Pour chaque décision retenue, lis le champ `commentaries` et la chronologie de l'affaire : conclusions du rapporteur public, rapport du conseiller, avis de l'avocat général, notice au rapport annuel. Les conclusions disent la jurisprudence abandonnée ou maintenue et le fondement écarté ; lis-les dans le PDF officiel. Quand la question appelle de la doctrine ou une autre discipline au-delà de quelques lectures, dis-le dans ta note et propose de lancer `chercheur-doctrine` ; pour les travaux que tu lis toi-même, écris leur fiche dans `recherche/doctrine/` (skill `recherche-doctrinale`). Aucun passage entre guillemets d'un travail lu sur sa notice ou son résumé.

## 6. Ajouts proposés à `agents/architecte-strategique.md`

Dans l'examen (points 2, 3 et 9), texte proposé :

> Vérifie que chaque décision sur laquelle repose un moyen a été lue avec ses conclusions et sa suite (chronologie, décisions postérieures) : un moyen fondé sur une solution abandonnée, ou sur un fondement que les conclusions ont écarté, est un point dirimant. Vérifie que la doctrine citée a sa fiche, qu'aucune règle ne repose sur elle seule, que les données empiriques sont dites avec leur population et leur limite et produites en pièce, et qu'une question technique passe par une voie probatoire (expertise, consultation, avis technique). Signale le travail savant qui manque : conclusions non lues, critique convergente non exploitée, étude qui contredirait la lecture par défaut du juge.

Outils à ajouter : `mcp__shs_fr__theses_search`, `mcp__hal__search_hal`, `mcp__academic_papers__search_openalex`, pour vérifier une référence sans relancer toute la recherche. Matériaux : ajouter `recherche/doctrine/` à la liste de ce qu'il lit.

## 7. Ajouts proposés à `skills/theorie-de-l-affaire/SKILL.md`

- § 4 « Éprouver chaque hypothèse contre chaque pièce » : la force d'une pièce se juge aussi par ce que la science dit de ce type de preuve (fiabilité d'une identification par témoin selon les conditions de présentation, d'un souvenir tardif, d'une expertise selon sa méthode) ; ces connaissances viennent de fiches `recherche/doctrine/` lues, et ne se plaident que par la voie probatoire.
- § 8 « Choisir la qualification » : lire les thèses et la doctrine autorisée sur la notion en cause ; elles disent comment les juges reçoivent la qualification et où passe sa frontière.
- § 10 « Thème et sûreté » : le fondement d'une valeur que le droit protège peut s'appuyer sur un travail théorique lu, brièvement, devant une juridiction suprême.
- Sortie, champ `lu` : y inclure les fiches doctrinales employées, avec leur statut de lecture.

## 8. `README.md` et `docs/ARCHITECTURE.md`

Ajouter le skill `recherche-doctrinale`, le sous-agent `chercheur-doctrine` et `doctrine.py` aux listes du `README.md` et à la table des couches de `ARCHITECTURE.md`, à côté de la recherche juridique.

## 9. Mesures du banc (19 et 20 novembre 2026)

Six sondes `DOCT-*`, modèle opus, une à la fois, outils de recherche académique ouverts par la sonde (sans Sci-Hub ni Anna's Archive), WebFetch fermé par le banc. Quatre posent une question explicite (retrouver et lire une thèse, des conclusions, une étude empirique, la version publiée d'une prépublication) ; deux mesurent la spontanéité (la question ne nomme aucun travail).

| Sonde | Plugin figé (base) | Plugin courant (module seul) | Copie avec `doctrine.patch` |
| --- | --- | --- | --- |
| DOCT-THESE-PRESCRIPTION-DELAI | réussie | réussie | non relancée |
| DOCT-CONCLUSIONS-RAPPORTEUR-PUBLIC | réussie | réussie | non relancée |
| DOCT-EMPIRIQUE-POPULATION | réussie | réussie | non relancée |
| DOCT-PREPUBLICATION-PUBLIEE | réussie | réussie | non relancée |
| DOCT-SPONTANE-CONCLUSIONS | échouée (0/4) | échouée (2/4) | échouée (3/4) |
| DOCT-SPONTANE-EMPIRIQUE | échouée (1/4) | échouée (0/4) | réussie (3/4) |

Lecture : quand on le lui demande, le modèle sait déjà trouver et lire ces travaux, base comprise. Sans demande, aucun agent n'a chargé le skill de lui-même ; seul le rappel du correctif, au moment de la question, a fait chercher la littérature scientifique (une synthèse de psychologie du témoignage citée avec son DOI, et une demande d'expertise). Aucun agent n'est allé lire des conclusions qu'il savait exister. Une passe par sonde : la variance n'est pas mesurée.

## 10. Limites connues du contrôle

- La détection repose sur des marques et sur des marqueurs déclarés : une citation doctrinale sans marque reconnue (« comme l'écrit un éminent auteur ») et sans marqueur passe inaperçue. La relecture par `verificateur-sources` et le contradicteur reste nécessaire.
- L'attribution d'une citation se fait à la phrase : une citation d'un texte ou d'une décision placée dans la même phrase qu'un marqueur doctrinal doit figurer au registre des sources avec ses `passages`, sinon elle est signalée.
- Le contrôle ne dit pas si la doctrine est bien comprise, bien choisie ni bien placée ; il garantit seulement qu'elle a été lue comme on le dit.
