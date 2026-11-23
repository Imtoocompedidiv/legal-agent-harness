# Voies d'accès aux travaux, par type de ressource

Éprouvées le 19 novembre 2026 avec les outils des sessions du plugin. Chaque entrée dit l'outil, la requête qui marche, ce que la réponse contient, comment atteindre le texte intégral et les pièges observés. Les exemples sont des références publiques ; ils servent à reconnaître une réponse juste, pas à remplir une écriture.

## Règles communes

- **Vérifier par l'identifiant.** Une référence n'est tenue pour vérifiée qu'après lecture de sa notice sur une base qui fait autorité : Crossref (`get_crossref_paper_by_doi`) pour un DOI, theses.fr (`theses_get`) pour une thèse, HAL pour un dépôt, SUDOC pour un livre ou une thèse ancienne, la page officielle pour des conclusions, un rapport ou un commentaire.
- **Lire au plus près du texte.** Texte intégral en accès ouvert, sinon extraits, sinon résumé publié, sinon notice. Le statut se note dans la fiche et se dit dans l'écriture.
- **Accès authentifié.** Un lien SUDOC vers un serveur d'université protégé (adresse contenant un proxy, par exemple `lama.univ-amu.fr`) exige un compte de cette université : chercher une autre voie vers le même texte.
- **Requêtes propres.** Termes juridiques ou scientifiques et identifiants publics seulement ; aucune adresse électronique, même demandée en paramètre pour un « accès poli ».
- **Résumés automatiques.** Le champ `ai_summary` de LibreJustice, le `tldr` de Semantic Scholar et toute synthèse d'outil orientent la recherche ; ils ne valent pas lecture et ne se citent pas.

## Conclusions des rapporteurs publics, avis et rapports

| Ressource | Voie | Ce qu'on obtient |
| --- | --- | --- |
| Conclusions au Conseil d'État | `get_decision` puis `commentaries` (kind `conclusions`, publisher ArianeWeb) ; sinon l'adresse `https://www.conseil-etat.fr/fr/arianeweb/CRP/conclusion/<AAAA-MM-JJ>/<numero>` | La page est une coquille sans texte ; le PDF est à la même adresse suivie de `?download_pdf` (200, `application/pdf`). |
| Rapport du conseiller, avis de l'avocat général, communiqué, notice au rapport annuel (Cour de cassation) | `get_decision` puis `commentaries` (publisher Cour de cassation) | Lien direct vers un PDF sur le dépôt des pièces jointes de Judilibre (servi en `application/octet-stream`). |
| Notes et chroniques payantes | `commentaries` (Dalloz Actualité, AJ Pénal, etc.) | Auteur, titre, revue, numéro, pages : statut « notice ». |
| Analyse du Recueil Lebon | Légifrance (`official_url` de la décision) | Abstrats, résumé et renvois « Rappr. », « Comp. », « Ab. jur. ». |
| Commentaire et dossier documentaire du Conseil constitutionnel | site du Conseil constitutionnel, depuis `official_url` | Commentaire officiel, qui n'est pas la décision. |

Observé :
- Une décision de chambres réunies de 2025 : `commentaries` donnait l'adresse ArianeWeb ; le PDF de 6 pages citait des décisions et une chronique qui ne figurent ni dans le texte de la décision ni dans son analyse au Recueil.
- CE, Sect., 22 septembre 2023, n° 472210 : l'adresse ArianeWeb composée par date et numéro rend le PDF des conclusions (200, `application/pdf`).
- Cass., ch. mixte, 25 mars 2022, n° 20-17.072 : `commentaries` donne le rapport du conseiller, le communiqué, la notice au rapport annuel et deux notes payantes.
- CE, Ass., 13 juillet 2016, Czabaj, n° 387763 : aucun `commentaries`, et l'adresse ArianeWeb composée rend 404 ; les conclusions de cette époque se cherchent dans les revues ou le Recueil. L'absence de résultat ne prouve pas l'absence de conclusions ; `case_chronology` signale en revanche la suite européenne de l'affaire.
- Les PDF portent la mention que les conclusions « ne sont pas libres de droits » : courte citation seulement (skill, § 3).
- Lecture : WebFetch quand il est permis ; sinon `curl -sL` vers `recherche/doctrine/sources/`, puis `pdftotext -enc UTF-8 -layout` (installé avec Git pour Windows) ou Python `pypdf` ou `fitz`. La console Windows affiche mal les accents : lire le fichier texte, pas la sortie de la console.
- Homonymie de numéros : 2019-778 DC et 2019-778 QPC sont deux décisions différentes du Conseil constitutionnel ; vérifier la nature de la décision.

## Thèses

| Outil | Requête | Ce qu'on obtient |
| --- | --- | --- |
| `theses_search` (theses.fr) | Champ ciblé : `titrePrincipal:référé`, `titrePrincipal:"expression exacte"`, `auteurs.nom:Dupont`, `directeurs.nom:X` | NNT, titre, auteur, direction, établissement, date de soutenance, DOI theses.fr (préfixe 10.70675). |
| `theses_get` (NNT) | `2021AIXM0456` | Résumés, jury, rapporteurs, `accessible` (oui ou non), cotutelle. |
| `sudoc_search` | `nnt=2021AIXM0456`, `mti=... and aut=...`, `tdo=y` (thèse) | PPN, mention de thèse, liens (parfois derrière un proxy). |
| `search_hal` | `portal="tel"`, `docType_s:THESE`, `nntId_id:...` | Dépôt TEL, avec ou sans fichier. |

Observé :
- Plusieurs mots sans champ ni guillemets ramènent du bruit (« rapporteur public » : 6 529 résultats, dont du traitement d'images). Le moteur exige tous les mots : une requête longue rend zéro résultat. Cibler le titre ou une expression.
- Les filtres `status` et `year_from` combinés ont rendu zéro résultat sur des requêtes qui en avaient ; refaire sans filtre et trier.
- Le tri `dateDesc` place d'abord des thèses en préparation (sans NNT). Une thèse en préparation n'est pas une thèse.
- `accessible : non` (par exemple 2021AIXM0456) : seule la notice et le résumé se lisent. Une notice HAL (TEL) peut exister sans fichier.
- Une thèse soutenue en juillet 2025 n'était pas encore au SUDOC par son NNT ; celle de 2021 (`nnt=2021AIXM0456`) y était, avec son PPN.

## Articles, chroniques et ouvrages juridiques français

| Outil | Usage |
| --- | --- |
| `isidore_search` | Moissonne Persée, OpenEdition, Cairn, HAL-SHS. `discipline="shs.droit"`, expression entre guillemets. Le champ `rights` dit l'accès : `openAccess` ou `Cairn` (payant). |
| `search_hal` | `title_t`, `authLastName_t`, `journalTitle_s`, `docType_s:ART`, `text_fulltext` pour un terme du corps du texte. |
| `read_hal_paper` | Texte intégral d'un dépôt HAL ouvert. |
| `sudoc_search` | Ouvrages, traités, manuels, avec édition et année. |
| `gallica_search` | Traités et revues anciens (XIXe et début du XXe siècle), Recueil Lebon ancien. |

Observé :
- Une requête ISIDORE sur une question de délais de procédure a rendu un chapitre en accès ouvert (OpenEdition Books) et une chronique Cairn réservée aux abonnés.
- L'extraction de `read_hal_paper` colle ou coupe des mots (« researchdocuments », « trè s ») : un passage cité se vérifie sur le PDF, et la page se lit dans le PDF.
- Les grandes revues (AJDA, RFDA, Dalloz, JCP) sont payantes : notice seulement, sauf dépôt de l'auteur sur HAL.

## Littérature scientifique (économie, psychologie, sociologie, médecine, technique)

| Outil | Usage |
| --- | --- |
| `search_openalex` | Recherche large ; donne `is_oa`, `pdf_url`, citations, références. Filtres : `publication_year`, `open_access.is_oa:true`. |
| `search_crossref`, `get_crossref_paper_by_doi` | Notice de référence : revue, volume, numéro, pages, type, résumé quand l'éditeur le dépose. |
| `search_semantic`, `mcp__asta__*` | Résumés, citations, extraits du corps (`snippet_search`). |
| `search_core`, `search_base`, `search_doaj`, `search_zenodo` | Versions ouvertes, revues en accès ouvert, données. |
| `search_pubmed`, `search_pmc`, `search_europepmc` | Médecine et psychologie clinique. |
| `search_arxiv`, `search_ssrn` | Prépublications (technique, droit et économie). |

Observé :
- Semantic Scholar a répondu 429 (trop de requêtes) et Asta a refusé la connexion le 19 novembre 2026 : passer à OpenAlex et Crossref.
- Unpaywall a rendu une réponse vide sur un DOI valide : l'outil n'est pas fiable ici, et il ne faut lui fournir aucune adresse électronique.
- OpenAlex indique les dépôts ouverts (par exemple un dépôt universitaire pour un article payant de l'éditeur).

## Prépublications et versions de travail

Une prépublication ou un document de travail n'a pas été relu par des pairs, et son résultat peut changer avant publication. Avant de le citer, chercher la version publiée : par le titre et les auteurs, puis par les auteurs seuls, car le titre change souvent.

Observé :
- Crossref type parfois « journal-article » des documents de travail : un DOI SSRN de 2022 (10.2139/ssrn.4282678, « SSRN Electronic Journal ») et les IMF Working Papers (10.5089) le sont, d'autres DOI SSRN (10.2139/ssrn.3713635) sont typés « posted-content ». Le type Crossref ne prouve pas une publication à comité de lecture.
- Titre changé : la note IPP n° 29 (2017) cite un document de travail de Desrieux et Espinosa de 2016, « Case selection and self-fulfilling anticipations », dont l'objet et les données (composition syndicale des conseils de prud'hommes, affaires de 1998 à 2012) correspondent à l'article « Case selection and judicial decision-making: evidence from French labor courts », *European Journal of Law and Economics*, vol. 47, n° 1, p. 57-88 (10.1007/s10657-018-9594-7) ; la correspondance se vérifie sur les textes avant de les tenir pour un même travail. Desrieux, Espinosa et Visser, SSRN 2022 « Simultaneous Decision-Making of Juries », devenu le document de travail CREST 2024-09 « Does Exposure to Concurrent Cases Affect Judicial Decisions? ».
- Résultat changé : Cahuc, Carcillo, Patault et Moreau, document de travail (SSRN 2020, FMI 2021) : effet moyen non significatif de l'incertitude ; version publiée au *Journal of the European Economic Association*, vol. 22, n° 3, p. 1319-1366 (10.1093/jeea/jvad046) : le biais pro-salarié réduit les créations d'emplois de toutes les entreprises. On cite la version publiée, et le résultat qu'elle contient.
- HAL : le type `UNDEFINED` désigne une prépublication ou un document de travail ; le même travail peut figurer deux fois (prépublication et article publié, ou version française et anglaise d'une même note).

## Homonymies et autorité réelle de l'auteur

- Un nom d'auteur seul ne suffit pas : le nom d'un économiste du droit, cherché seul en HAL, a rendu des physiciens, des hydrologues et des historiens. Croiser avec le prénom, le domaine, l'idHAL, l'ORCID ou le coauteur.
- Qualité de l'auteur : membre de la juridiction (rapporteur public, conseiller, auditeur, chroniqueur), professeur spécialiste de la matière, praticien, doctorant. La thèse d'un doctorant soutenue devant un jury de spécialistes pèse plus qu'un billet ; une chronique des membres du Conseil d'État dit la lecture de la formation.
- Date : un article antérieur à une réforme ou à un revirement peut décrire un droit disparu. La fiche dit ce qui a changé depuis.

## Résumés trompeurs

- Le résumé d'une thèse ou d'un article dit la question et l'ambition ; il ne dit ni la démonstration, ni les nuances, ni les réserves. Ne pas prêter à l'auteur une conclusion que son résumé ne contient pas.
- Le résumé d'une étude empirique donne un effet moyen ; la population, l'échantillon et les limites sont dans le corps. Une étude sur des étudiants, des jurés américains ou des données anciennes ne décrit pas un juge français d'aujourd'hui.
