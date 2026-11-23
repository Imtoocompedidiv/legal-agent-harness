---
name: recherche-doctrinale
description: "Trouver, lire et mobiliser les meilleurs travaux (doctrine, conclusions, rapports, sciences sociales et techniques) avec fiche de lecture vérifiée. Quand la portée d'un texte, une jurisprudence en mouvement ou un fait d'expérience décide d'un moyen, et avant de citer un auteur."
---

# Recherche doctrinale et académique

Le droit se trouve dans les textes et les décisions (skill `recherche-juridique`). Les travaux savants disent ce que ces sources veulent dire, où elles vont, ce qu'elles coûtent dans les faits et sur quoi elles reposent. Bien choisis et lus à la source, ils font gagner un moyen ; cités de mémoire ou sur un résumé, ils le font perdre. Ce skill dit quand les chercher, où, comment les lire et comment s'en servir.

## 1. Quand chercher

Chercher dès que l'une de ces situations se présente, sans attendre qu'on le demande.

- **Portée d'un texte.** Texte récent, obscur ou rarement appliqué : thèses et articles sur la notion, commentaires de la loi au moment de son adoption, rapport annuel ou étude qui l'éclaire.
- **Jurisprudence en mouvement.** Une décision sur laquelle l'affaire repose a pu être abandonnée, nuancée ou contredite : lire les conclusions du rapporteur public ou l'avis de l'avocat général, le rapport du conseiller, la chronique des membres de la juridiction et l'analyse du Recueil (« Rappr. », « Comp. », « Ab. jur. »). Les conclusions disent souvent ce que la décision tait : la jurisprudence abandonnée, celle qui survit, le fondement retenu et celui qui a été écarté. Une décision ancienne peut rester valable sur un point et être dépassée sur un autre : seules les conclusions le disent parfois, et le moyen doit viser le fondement que la juridiction a réellement retenu. La suite d'une affaire compte aussi : sur CE, Ass., 13 juillet 2016, Czabaj, n° 387763, `get_decision` ne joint aucun document, mais la chronologie signale un arrêt de violation de la Cour européenne des droits de l'homme du 13 février 2025 (n° 48145/19), rendu sur une requête dirigée contre la France dans cette affaire.
- **Revirement à obtenir.** Devant une juridiction suprême, réunir les signes : conclusions contraires, divergences entre cours, question pendante, critique doctrinale convergente d'auteurs indépendants et autorisés, droit comparé, condamnation européenne.
- **Fait à établir par la science.** Effet d'une mesure, pratique réelle d'une juridiction, fiabilité d'un témoignage, préjudice, proportionnalité, urgence : une étude empirique publiée sert la preuve d'un fait, jamais une règle.
- **Question technique.** Médecine, ingénierie, informatique, comptabilité, environnement : la littérature sert à formuler la mission d'expertise, à contester un rapport, à choisir le technicien. La preuve passe par la voie probatoire.
- **Sens d'un acte.** La linguistique (modalité, actes de langage, ambiguïté, lisibilité) aide à qualifier un écrit : décision ou simple information, menace, promesse, mention claire ou trompeuse des voies de recours.
- **Fondement d'un principe.** Philosophie du droit, histoire, théorie : utiles devant une juridiction suprême pour justifier une évolution ou l'interprétation d'un principe (sécurité juridique, dignité, loyauté), rarement devant le juge du provisoire.

Ne pas en mettre quand un texte clair et une jurisprudence constante règlent la question, ni pour masquer l'absence de règle. Devant le juge des référés, une référence brève et décisive vaut mieux qu'une démonstration savante.

## 2. Méthode

1. **Écrire la question** que le travail doit éclairer, ce qu'il doit établir (portée, mouvement, fait, technique, sens, fondement) et la proposition contraire.
2. **Choisir les voies** par type de ressource : `references/voies-d-acces.md` donne les outils, la syntaxe, les pièges observés et les réponses à attendre.
3. **Vérifier la référence** sur une base qui fait autorité : Crossref pour un DOI, theses.fr pour une thèse (NNT), SUDOC (PPN), HAL, page officielle de la juridiction. Une référence donnée par un moteur de synthèse, un résumé automatique ou la mémoire n'est pas vérifiée.
4. **Lire.** Le texte intégral d'abord, par toutes les voies disponibles dans la session (HAL, OpenEdition, Persée, dépôt de l'auteur, PDF officiel et les autres outils de recherche installés). À défaut, des extraits, en disant lesquels. À défaut, la notice et le résumé, en le disant.
5. **Juger la solidité.** Pour la doctrine : qui est l'auteur (membre de la juridiction, professeur spécialiste, doctorant), quand il écrit, si le droit a changé depuis, si la juridiction l'a suivi. Pour l'empirique : méthode, population, période, taille, réplication, limites, et ce que l'étude ne permet pas de dire.
6. **Chercher le contre** : l'auteur qui soutient l'inverse, la décision postérieure, la réforme qui a changé la donne, la critique de l'étude.
7. **Écrire la fiche** `recherche/doctrine/<id>.json` (section 4) et la valider depuis le dossier d'affaire : `python "${CLAUDE_PLUGIN_ROOT}/scripts/doctrine.py" valider`.
8. **Mobiliser** selon `references/mobiliser-dans-l-ecriture.md`.

## 3. Conclusions, avis et rapports : la voie `commentaries`

1. Trouver la décision (`search_decisions`, mode `reference` sur le numéro), puis `get_decision`. Le champ `commentaries` liste les documents qui l'entourent : conclusions (ArianeWeb), rapport du conseiller, avis de l'avocat général, communiqué, notice au rapport annuel (Cour de cassation), notes d'auteurs (Dalloz, Lexis).
2. Conseil d'État : la page ArianeWeb `https://www.conseil-etat.fr/fr/arianeweb/CRP/conclusion/<AAAA-MM-JJ>/<numero>` est une coquille ; le texte est le PDF servi à la même adresse suivie de `?download_pdf`. Cour de cassation : les PDF sont sur le dépôt des pièces jointes de Judilibre, dont `commentaries` donne l'adresse.
3. Lire le PDF : WebFetch quand il est disponible ; sinon `curl -sL "<adresse>" -o recherche/doctrine/sources/<id>.pdf`, puis `pdftotext -enc UTF-8 -layout` ou Python (`pypdf`, `fitz`). Relever les passages avec la page imprimée en bas du PDF.
4. Le nom du rapporteur public figure dans les visas de la décision (« les conclusions de M. X, rapporteur public »). Les notes Dalloz ou Lexis listées dans `commentaries` sont payantes : statut « notice », aucune citation.
5. L'absence de `commentaries` ne prouve pas l'absence de conclusions : essayer l'adresse ArianeWeb par date et numéro, l'analyse du Recueil sur Légifrance, la chronique de l'AJDA (notice ISIDORE ou Cairn), la Revue française de droit administratif.
6. Les conclusions portent la mention qu'elles « ne sont pas libres de droits » et que leur rediffusion est subordonnée à l'accord du rapporteur public. Dans une écriture, une courte citation avec le nom de l'auteur et la source est permise (code de la propriété intellectuelle, art. L. 122-5, 3°, a), et le droit d'auteur ne fait pas échec aux actes nécessaires à une procédure juridictionnelle (art. L. 331-4). On ne recopie pas le texte entier, on ne le diffuse pas hors du dossier.
7. Les conclusions ne lient personne. Toujours dire ce que la décision a retenu, et vérifier sa chronologie (`case_chronology`) : une décision suivie de conclusions brillantes peut avoir été désavouée ensuite, y compris par la Cour européenne des droits de l'homme.

## 4. La fiche de lecture

Chaque travail utilisé a sa fiche `recherche/doctrine/<id>.json` (schéma `references/schemas/doctrine.v1.schema.json`, squelette par `doctrine.py squelette`). L'identifiant, en minuscules et tirets, est le nom du fichier. La fiche porte :

- `question`, `type` et `discipline` ;
- `reference` complète et vérifiée : auteurs avec leur qualité, titre, année, support, volume, numéro, pages, au moins un identifiant (DOI, HAL, NNT ou PPN pour une thèse, ISBN, numéro de la décision pour des conclusions ou un rapport, adresse officielle), les bases qui l'ont confirmée (`verifiee_par`), le statut de publication, la version lue et, pour une prépublication ou un document de travail, le résultat de la recherche de la version publiée ;
- `lecture` : statut (`texte_integral`, `extraits`, `resume`, `notice`), date, accès, source lue, parties lues pour des extraits, obstacle quand le texte n'a pas été lu en entier ;
- `these_de_l_auteur`, dans ses mots, sans l'arranger pour l'affaire ;
- `passages` relevés mot pour mot avec leur page, seulement pour un texte lu ;
- `solidite` : niveau, autorité, date et actualité, réception ; pour l'empirique, méthode, population, période, taille, réplication et limites ;
- `usage` : la nature de l'apport, la proposition qu'il sert dans l'affaire, sa limite, les écritures qui l'emploient, et pour une expertise la voie probatoire ;
- `marqueurs` : les formes exactes sous lesquelles l'écriture cite le travail (« concl. Dupont », « note IPP n° 29 »), qui permettent au contrôle de le retrouver ;
- `contre` : les travaux ou décisions qui disent l'inverse.

Une fiche ne contient aucune donnée du client.

## 5. Ce que le contrôle vérifie

`python "${CLAUDE_PLUGIN_ROOT}/scripts/doctrine.py" controle ecritures/brouillons/<acte>.md` (et le contrôle avant dépôt, une fois le module intégré) bloque un acte juridictionnel quand :
- un travail cité n'a pas de fiche, ou que sa fiche est invalide ;
- une marque de citation savante (DOI, identifiant HAL, numéro de thèse, « concl. », « chron. », « note sous », revue suivie d'une année, « et al. ») n'est couverte par aucune fiche dans la même phrase ;
- un passage entre guillemets attribué à un travail n'a pas été lu (statut résumé ou notice), ou ne figure ni dans les passages de la fiche ni au registre des sources ;
- un moyen ou une condition ne repose que sur des sources de type doctrine.

Il alerte quand une donnée empirique fragile est citée, quand la phrase qui la cite ne donne pas la période étudiée, et quand une version de travail est citée alors que la version publiée est connue. Ces verrous sont mécaniques : ils ne disent pas si la doctrine est bien comprise ni bien employée.

## 6. Délégation

Une recherche large se confie au sous-agent `chercheur-doctrine`, avec la question, l'utilité dans l'affaire, les pistes et le livrable (les fiches et une note de synthèse, pas un inventaire). Relire soi-même à la source les passages décisifs avant de les citer.

## 7. Confidentialité

Les requêtes ne contiennent que des termes juridiques ou scientifiques et des identifiants publics. Aucun nom, aucune adresse, aucune adresse électronique, aucun fait privé du client, ni dans une requête, ni dans un en-tête, ni dans un paramètre (« polite pool » de Crossref, Unpaywall, OpenAlex compris). Un service qui exige une adresse de contact est abandonné pour une autre voie.
