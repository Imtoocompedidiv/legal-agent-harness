---
name: recherche-juridique
description: "Recherche par passes obligatoires (texte à la date, section, renvois, texte spécial, transitoire, jurisprudence par article, suite des décisions, autorité contraire) tracées au registre des lectures. Avant toute affirmation de droit, tout choix de moyen et toute vérification de citation."
---

# Recherche juridique

La recherche d'un avocat aux Conseils se juge à ce qu'elle n'a pas laissé échapper et à l'exactitude de ce qu'elle cite. Deux défauts reviennent : la règle voisine, l'exception, le texte spécial ou la décision récente qui changent la réponse et qu'on n'a pas cherchés ; la lecture approximative, où l'on cite de mémoire, d'après un aperçu, dans une version inapplicable ou une décision depuis annulée. Le protocole ci-dessous les traite par des passes fixes et par un registre qui garde trace de ce qui a réellement été lu.

`R` désigne `python "${CLAUDE_PLUGIN_ROOT}/scripts/lectures.py"`, lancé depuis le dossier d'affaire.

## 1. Le registre des lectures

Chaque appel à un outil LibreJustice (`search_norms`, `get_norm`, `search_decisions`, `get_decision`) et chaque lecture par `mcp__legal_harness__read_document` est capturé par le hook PostToolUse dans `recherche/lectures/` : outil, entrée, horodatage du dossier, réponse brute, empreinte inscrite dans `recherche/lectures/registre.jsonl`. Le registre ne s'écrit que par le hook ; une capture modifiée, ajoutée ou supprimée à la main est écartée et bloque le contrôle avant dépôt. Si les commandes trouvent le registre vide alors que des lectures ont été faites, le hook de capture n'est pas branché (autre environnement, correctif d'intégration non appliqué) : le dire, et faire à la main, sur les textes lus dans la session, les contrôles que les commandes font d'ordinaire.

Le registre fait foi de la lecture. Un article est lu à une date si une capture de `get_norm` en donne la version applicable à cette date. Une décision est lue si une capture de `get_decision` en rend le texte. Un aperçu de recherche (`ai_summary`, `court_summary` d'une liste de résultats, `snippet`) ne vaut lecture de rien : il oriente la recherche, il ne se cite pas et ne dit pas ce que juge une décision. Une source lue ailleurs que dans ces outils (Légifrance dans le navigateur, base ouverte, ArianeWeb, HUDOC, CURIA, doctrine) n'est pas capturée ; elle s'acquiert, quand c'est possible, par `acquire_source` puis se lit par `read_document`, qui est capturé, et sinon elle se signale comme non vérifiable par le registre.

Commandes :
- `R couverture <note ou écriture> [--date AAAA-MM-JJ]` : pour chaque article cité, lu ou non, à la date utile ou non, section lue, renvois suivis, jurisprudence cherchée par l'article ; pour chaque décision citée, lue ou non, suite vérifiée, suite qui la défait, conclusions et rapports signalés par la source.
- `R citations <note ou écriture>` : chaque passage entre guillemets, rattaché à la source que le paragraphe lui attribue (décision, article, pièce), est cherché mot pour mot dans les captures et dans les extractions de pièces ; une citation inexacte est rendue avec le passage exact de la source.
- `R portee [<note ou écriture>]` : décisions dont `standing` ou `case_chronology` montre une annulation, une cassation ou une infirmation, et, pour une écriture, si elle le dit.
- `R requetes [--vides]` : toutes les recherches faites, avec leurs filtres et leur nombre de résultats ; `--vides` donne celles qui n'ont rien rendu.
- `R fiche <référence> [--date AAAA-MM-JJ]` et `R verifier [<id>]` : squelette et validation des fiches de lecture (section 5).

## 2. Poser la question

Écrire avant toute requête :
- la proposition à établir et la proposition contraire, que la recherche cherche toutes deux ;
- les qualifications concurrentes ;
- la juridiction saisie et celle d'appel ou de cassation ;
- les dates : faits, acte attaqué, saisine, jugement, jour du dépôt.

En tirer la date utile de chaque règle. La légalité d'un acte s'apprécie en principe à sa date. La recevabilité d'une requête se juge selon les textes applicables à son enregistrement. La voie de recours contre un jugement suit les textes applicables à l'introduction du recours ou au jugement, selon ce que dit la disposition transitoire. La date utile se déclare : dans la note, par une ligne « Date utile : AAAA-MM-JJ » ; dans la fiche de l'acte, par `date_droit_applicable` et, article par article quand elles diffèrent, par `dates_utiles` (clé « <code>|<article> »).

## 3. Les passes du ratissage

Chaque passe est obligatoire pour chaque règle qui commande la réponse. Elle laisse sa trace dans le registre, puisque toute requête et toute lecture y sont capturées. Une passe sans résultat se consigne dans la note avec l'outil, la requête et les filtres exacts qui n'ont rien rendu (`R requetes --vides`) ; une base muette ne prouve pas l'absence de règle ou de jurisprudence, et l'on passe à la voie suivante.

1. **Proposition et proposition contraire.** `search_norms` et `search_decisions` sur chacune, en termes juridiques, avec les filtres de juridiction et de date. La contraire se cherche avec le même soin que la nôtre.
2. **Texte à la date.** `get_norm` avec `as_of` à chaque date utile. Lire le statut, la période de validité, la chronologie des versions et la note de version. Quand le texte a changé entre les faits, l'acte, la saisine et le jugement, lire chaque version qui peut s'appliquer et dire laquelle s'applique, en vertu de quelle disposition.
3. **Section.** Ouvrir l'adresse de `section` que rend `get_norm` : elle donne d'un coup tous les articles voisins. Y chercher ce qui déroge, prolonge ou exclut : « par dérogation », « toutefois », « sauf », « à l'exception », augmentation de délai, cas particuliers, alinéas transitoires. Une exception peut se trouver dans le chapitre voisin ou dans un autre livre du même code ; quand le texte renvoie à une liste, à une catégorie ou à un régime, lire l'article qui la définit.
4. **Renvois.** Suivre chaque lien `/norm/` du texte, à la même date. Ouvrir chaque texte modificatif que signale `modified_by` et lire toutes ses dispositions : il crée souvent, ailleurs dans le code, des règles nouvelles qui s'appliquent au même acte (notification à peine d'irrecevabilité, compétence, délai, cristallisation), et il porte son entrée en vigueur. Chercher aussi les textes qui renvoient à l'article étudié (`search_norms` sur son numéro dans son code et hors de lui).
5. **Texte spécial et décret d'application.** Le régime spécial de la matière déroge au général : chercher dans le code de la matière, puis par `search_norms` filtré sur `FR.DECRET`, le décret ou l'arrêté qui donne la règle concrète, la liste, le seuil ou la procédure.
6. **Dispositions transitoires.** La note de version, l'article d'entrée en vigueur du texte modificatif et son champ (actes pris, requêtes enregistrées, instances introduites à compter d'une date) se lisent et s'appliquent aux dates de l'affaire.
7. **Jurisprudence par article.** `search_decisions` avec `legal_article` « <code>|<article> », le code tel que le rend `get_norm` dans `code` et l'article tel qu'il figure dans `number`. Dans cet ordre : décisions publiées (`publication` : `PUBLIE_LEBON`, `MENTIONNE_LEBON` pour l'ordre administratif ; `PUBLIE_RAPPORT`, `PUBLIE_BULLETIN`, `LETTRE_CHAMBRE`, `COMMUNIQUE` pour l'ordre judiciaire) ; puis sans filtre de publication, pour les inédites ; puis restreintes au siège de la juridiction de l'affaire et de sa juridiction d'appel (`seat`) ; puis les plus récentes (`sort` par date). La question de l'affaire va dans `query` ; le filtre `solution` sert à trouver les issues contraires. Les décisions retenues se lisent en entier.
8. **Conclusions et rapports.** Pour chaque décision décisive, `get_decision` signale dans `commentaries` les conclusions du rapporteur public, le rapport du conseiller et l'avis de l'avocat général, et `case_chronology` situe la décision dans l'affaire. Les conclusions disent la jurisprudence abandonnée ou maintenue et le fondement écarté. Les lire par la voie que donne la skill `recherche-doctrinale` (PDF à l'adresse suivie de `?download_pdf`, puis extraction du texte). Elles sont à une requête : quand la décision fonde la réponse, opère un revirement ou porte la thèse adverse, leur lecture ne se reporte pas, et le contrôle de fin bloque une réponse qui les évoque sans les avoir ouvertes. Seule une source inaccessible permet de les porter dans ce qui n'a pas été lu, avec leur adresse et la raison. L'absence de `commentaries` ne prouve pas l'absence de conclusions.
9. **Suite de chaque décision.** `standing` et `case_chronology` se lisent pour chaque décision citée. Une décision annulée, cassée ou infirmée n'est plus une autorité : on ne l'invoque pas, ou l'on dit ce qui en subsiste. `NO_KNOWN_REVIEW` signifie qu'aucune suite n'est connue, pas que la décision est définitive. Chercher par son numéro les décisions ultérieures qui la citent, pour un revirement ou une divergence. Le Conseil d'État ne cite pas ses précédents : son numéro ne renvoie que la décision elle-même. Pour une décision administrative invoquée, surtout par l'adversaire ou le juge du fond, chercher donc aussi les décisions postérieures sur la même question, en mode sémantique, à partir de sa date (`date_from`), au Conseil d'État, sans filtre d'article : une règle prétorienne et son revirement ne citent souvent aucun texte, et le filtre `legal_article` les écarte.
10. **Meilleure autorité contraire.** La décision ou le texte le plus fort contre notre proposition, lu en entier comme les autres, avec la manière de le distinguer ou la raison de changer de proposition.

Ce que la recherche doit trouver sans qu'on le lui désigne : la règle qui oblige l'adversaire, plutôt que la faculté qu'on lui demande d'exercer ; le texte enfoui qui règle le cas particulier ; la décision inédite d'une cour ou d'un tribunal qui a jugé la même configuration ; les signes d'un revirement (conclusions contraires, divergences entre cours, renvoi préjudiciel ou question prioritaire pendante, critique doctrinale convergente).

## 4. Lire et citer

Toute décision citée se lit en entier par `get_decision` : faits, demandes, moyens, motifs, dispositif. Distinguer la règle posée, le raisonnement limité aux faits, l'argument de partie et le commentaire. Tout article cité se lit dans la version applicable. Une citation se recopie depuis le texte capturé, jamais de mémoire ni depuis un résumé ; une coupure se marque par « [...] ». Le texte servi par LibreJustice porte des liens ajoutés (`[...]( ... )`, « (+ [...]) ») qui ne font pas partie du texte et ne se recopient pas.

Pour les sources décisives (la règle qui commande la réponse, la décision sur laquelle repose un moyen, la meilleure autorité contraire), lancer le sous-agent `lecteur-de-texte`, qui écrit la fiche de lecture (section 5).

## 5. Fiches de lecture

`recherche/fiches/<id>.json`, au schéma `references/schemas/fiche_lecture.v1.schema.json`, écrites par le sous-agent `lecteur-de-texte` depuis le squelette `R fiche <référence> [--date]`, qui préremplit version, section, renvois, recherches par article, suite et commentaires depuis les captures. Une fiche de norme donne la lettre en extraits verbatim, la version et sa période, le champ d'application, les conditions et leur articulation, les exceptions lues dans la section, les renvois suivis, les effets, l'interprétation jurisprudentielle et la portée. Une fiche de décision donne la juridiction, la formation, la publication, la question tranchée, le motif décisif littéral, la solution, la portée de principe ou d'espèce, les limites et la suite. Ce qui n'a pas été lu se dit dans `non_lu`. `R verifier <id>` retrouve chaque extrait dans les captures citées et rejette une fiche dont un extrait, une version, une section ou une suite ne correspond pas à ce qui a été lu.

## 6. Avant de s'appuyer sur une note ou une écriture

Lancer `R couverture`, `R citations` et `R portee` sur la note ou l'écriture, et corriger jusqu'à ce qu'aucune décision citée ne soit non lue ou défaite sans le dire, qu'aucune citation ne soit inexacte ou introuvable et que chaque article cité soit lu à sa date utile. Les sections non lues, les renvois non suivis et les articles sans recherche par `legal_article` se reprennent ou se justifient dans la note. Le contrôle avant dépôt bloque ces défauts sur l'écriture (skill `controle-avant-depot`).

## 7. Registre des sources

Chaque source utilisée entre aussi dans `etat/sources.json`, que lit le contrôle avant dépôt : `id`, `type` (texte, decision, doctrine, travaux, rapport, autre), `reference`, `numero` pour une décision, `juridiction`, `date`, `url`, `lu_en_entier`, `lu_le`, `portee` (ce que la source juge exactement et ses limites), `passages` (citations exactes avec leur point), et pour un texte `version` et `date_reference`. `lu_en_entier` n'est vrai que si une capture du registre des lectures en rend le texte ; le contrôle signale une décision déclarée lue sans capture. Une entrée de type `doctrine` renvoie à sa fiche de lecture doctrinale (`fiche_doctrine`) ; une source doctrinale ne porte jamais seule un moyen. Les délais se calculent par l'outil `calculate_civil_deadline` du serveur `legal_harness` ou par un calcul écrit, jamais de mémoire.

## 8. Autres sources

Après LibreJustice : le miroir DILA du serveur `legal_harness` (`acquire_source`, puis `read_document`), Légifrance dans le navigateur quand les scripts sont refusés, Judilibre, la base ouverte de la justice administrative pour les tribunaux et les cours, ArianeWeb pour les analyses et les conclusions du Conseil d'État, HUDOC, CURIA ; les travaux parlementaires (dossiers législatifs, études d'impact, rapports de commission) pour l'intention du texte et ses limites ; la doctrine, qui éclaire la portée sans valoir règle, se cherche et se lit selon la skill `recherche-doctrinale`, au besoin par le sous-agent `chercheur-doctrine`, avec une fiche de lecture par travail employé dans `recherche/doctrine/` ; les rapports (études du Conseil d'État, rapport annuel de la Cour de cassation, décisions-cadres du Défenseur des droits, avis de la CADA et de la CNIL). Quand une source échoue (panne, refus des scripts, anti-robot), passer à la voie officielle suivante et noter l'obstacle.

## 9. Confidentialité

Les requêtes vers les bases publiques ne contiennent que des termes juridiques et des identifiants publics. Aucun nom, aucune adresse, aucune adresse électronique, aucun fait privé du client, ni dans une requête, ni dans un en-tête, ni dans un formulaire. Un site qui exige une adresse de contact est abandonné pour une autre source.

## 10. Délégation

Une recherche large se confie au sous-agent `chercheur-juridique`, avec la question, l'utilité stratégique, les dates utiles, les pistes, le chemin de la note à écrire et le livrable attendu (une réponse et ses sources). La lecture exacte d'une source décisive se confie au `lecteur-de-texte`. La vérification indépendante d'une écriture avant dépôt se confie au `verificateur-sources`. Leur brief donne le chemin du plugin quand la variable `CLAUDE_PLUGIN_ROOT` n'est pas définie dans leur shell. Les passages décisifs qu'ils rapportent se contrôlent par `R citations` avant usage. Une note de recherche, dans `recherche/notes/`, donne la proposition, la réponse, les autorités pour et contre avec leurs limites, la trace des passes, les requêtes restées sans résultat et ce qui n'a pas été lu.
