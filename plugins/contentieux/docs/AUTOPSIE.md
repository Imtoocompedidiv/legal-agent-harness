# Autopsie du référé n° 2614024, rejeté au tri le 16 novembre 2026

Document de conception du plugin. Il ne contient ni donnée de santé ni identifiant personnel ; les pièces sont désignées par leur date. Sources lues pour l'écrire : l'ordonnance du 16 novembre (texte intégral), le rapport S7 de la phase 29 (en entier), l'état du dossier au 17 novembre, le journal du 17 novembre, la note d'équipe rouge du 2 novembre (L4), le mémoire du 12 novembre tel que Télérecours le conserve, le texte 23 du 17 novembre et l'audit interne `docs/recherche/03_audit_interne.md`.

## 1. Le cadrage de la demande, corrigé

La demande décrit l'échec comme un défaut de vérification des conditions du référé civil (urgence, trouble manifestement illicite, absence de contestation sérieuse). Le référé rejeté était un référé-suspension administratif (CJA, art. L. 521-1), dont les conditions sont l'urgence et un moyen propre à créer un doute sérieux. La juge l'a rejeté sans instruction ni audience (art. L. 522-3) au seul motif qu'aucun moyen, « tels qu'invoqués », n'était manifestement de nature à créer un doute sérieux. Elle n'a examiné ni l'urgence, ni la recevabilité. Le plugin traite les deux familles de référés, mais l'autopsie porte sur celle qui a échoué.

## 2. Ce qui s'est passé

Le dernier état soumis à la juge est le mémoire du 12 novembre. Il attaquait trois actes (décision notifiée le 28 août, lettre du 22 septembre, courriel de la direction des études du 6 octobre) et, en tant que de besoin, la délibération du jury du 9 juillet. Il comptait huit chefs de conclusions, dont un injonctif à trois branches conditionnelles, neuf occurrences de « subsidiaire », et des demandes d'accès aux cours, d'inscription provisoire et de supports pédagogiques. Selon S7, l'ensemble des écritures au référé représentait 25 pages, environ 15 500 mots et 76 pièces. L'ordonnance a été rédigée sur le fichier d'une ordonnance de tri antérieure de la même juge (son numéro figure en tête des pages 2 à 4).

## 3. Les causes, par ordre de poids

### 3.1 La cible

Deux des actes attaqués précédaient l'avis du service de santé du 24 septembre, qui constate le handicap. La légalité s'apprécie à la date de l'acte : aucun moyen tiré du handicap ne pouvait opérer contre eux. Le troisième acte, un courriel répondant à une demande de rendez-vous, n'était probablement pas une décision ; deux arrêts de la cour administrative d'appel de Paris, lus par l'équipe le 10 novembre, le disaient. La seule demande qui portait la force du dossier, celle du 9 octobre à la directrice, n'était pas devant la juge.

### 3.2 L'angle mort du terrain

La décision sur la demande du 9 octobre existait. Datée du 15 octobre, remise à La Poste le 2 novembre, elle a fait l'objet d'un avis de passage le 5 novembre à l'adresse de Lyon que le requérant déclarait dans ses propres écritures, puis a été mise en instance le 7 novembre et retirée le 17 novembre. Le relevé quotidien couvrait Gmail, Outlook, Télérecours et les publications de l'Institut. Il ne couvrait pas le courrier postal. La note d'équipe rouge du 2 novembre prévoyait pour le 12 novembre « le contrôle direct des deux boîtes […] du courrier postal et de Télérecours » ; le journal note ensuite qu'aucun contrôle du courrier postal n'a été fait. Le 12 novembre, l'équipe plaidait donc qu'aucune décision n'existait (feuille v4, R9) alors que cette décision attendait au bureau de poste depuis une semaine. Relevée le 5 ou le 7 novembre, elle aurait permis de diriger le mémoire du 12 contre l'acte qui portait la question, celui que S7 recommandera le 16 novembre.

Cette cause est la plus élémentaire et la plus coûteuse : une évidence de terrain non vérifiée a commandé la stratégie contentieuse.

### 3.3 Le récit cédé

Le point 1 de l'ordonnance résume l'affaire avec le récit de l'Institut : réinscription accordée pour raison de santé, année non validée, refus. Les écritures le lui offraient : la requête ouvrait ses faits sur les échecs, le mémoire du 12 novembre sur la crise de l'Institut, et le constat du handicap venait au paragraphe 9.

### 3.4 La composition

Neuf chefs, trois branches conditionnelles, une cascade de subsidiaires, des moyens présentés comme des hypothèses (« le requérant soutient que », « si telle est sa portée »), des demandes qui supposent une instruction : un juge qui trie voit un requérant qui hésite sur l'acte et sur ce qu'il demande, et une illégalité qui n'est pas manifeste.

### 3.5 La contradiction faite et non suivie

La feuille de réponses du 10 novembre écrivait les objections fatales (R1 sur la nature du courriel, R2 sur l'interprétation de l'article 8, R9 sur l'absence de décision, R32 sur les mesures que nul juge n'accorde) et la position commune du même jour tenait l'urgence pour le risque prioritaire. Le mémoire du 12 novembre a gardé l'architecture. Rien n'obligeait à trancher. La méthode de consensus a empilé une branche subsidiaire par objection au lieu de couper.

### 3.6 Le droit plaidé comme une faveur

L'article 8 du règlement est une faculté. Le dossier l'a présenté comme une grâce à obtenir, alors que l'obligation de l'article L. 123-4-2 du code de l'éducation et la procédure d'aménagement de l'Institut pouvaient structurer la démonstration.

### 3.7 Ce qui était bien fait

Les faits étaient exacts et sourcés, les références existaient, la requête au fond distincte et sa copie étaient jointes, le programme et les dates répondaient d'avance au motif de tri le plus fréquent. Le travail a échoué sur la cible, sur le terrain et sur la composition.

## 4. Les verrous qui en découlent

| Cause | Verrou | Mécanisme |
| --- | --- | --- |
| Cible antérieure aux faits invoqués | `MOYEN_INOPERANT_DATE` : tout moyen appuyé sur un fait postérieur à l'acte visé bloque le dépôt | `gate.py`, fiche de l'acte |
| Acte non décisoire | qualification obligatoire de chaque acte, sourcée ; `ACTE_NON_DECISOIRE`, `ACTE_QUALIFICATION_NON_SOURCEE` | `gate.py` |
| Pluralité d'actes | `PLURALITE_ACTES` sans justification écrite | `gate.py` |
| Décision restée au bureau de poste | registre des canaux de notification, courrier postal à chaque adresse connue de l'adversaire en tête ; alerte de retard au démarrage et à chaque message | `etat/canaux.json`, hooks SessionStart et UserPromptSubmit, `affaire.py canal controle` |
| Récit cédé | `FAIT_DECISIF_TARDIF`, `QUESTION_HORS_PREMIERE_PAGE` ; lecteur de tri limité à la première page et au dispositif | `gate.py`, `affaire.py extrait-tri`, sous-agent `juge-simule` |
| Composition | `SUBSIDIAIRES`, `BRANCHE_CONDITIONNELLE`, `ATTENUATION`, `CONCLUSION_SANS_POUVOIR` | `lint_ecriture.py`, hook PostToolUse, `gate.py` |
| Contradiction non suivie | toute objection dirimante ouverte bloque ; chaque point du contradicteur exige une décision (couper, garder, reformuler) | `etat/objections.json`, `gate.py`, sous-agent `contradicteur` |
| Droit plaidé comme faveur | recherche de la règle qui oblige l'adversaire, texte spécial, décret d'application | skills `recherche-juridique`, `strategie-contentieuse`, `refere-administratif` |
| Parole sur une pièce non ouverte (échec le plus fréquent selon l'audit interne) | fin de tour bloquée si le message cite une pièce ou une décision ni ouverte dans le fil ni inscrite comme lue | hook Stop |
| Dépôt sur un accord ancien | consignation du dépôt refusée si l'accord n'est pas dans la conversation ou si un message postérieur demande d'attendre | hook PreToolUse sur `affaire.py depot` |
| Fichiers au nom de l'assistant transmis à une autorité | `TERME_INTERNE_TEXTE`, `TERME_INTERNE_PIECE` | `gate.py` |

## 5. Résultat du rejeu

Le mémoire du 12 novembre, rejoué avec l'horloge fixée au 12 novembre à 7 h 45 et en accordant à l'équipe le bénéfice du doute sur toutes les sources et toutes les pièces, est bloqué par 17 constats, dont les deux moyens inopérants par leur date, le fait décisif absent de la première page, la cascade de subsidiaires, les branches conditionnelles du dispositif, deux conclusions sans pouvoir du juge et les quatre objections dirimantes écrites le 10 novembre. Le détail est dans `docs/ESSAIS.md`.

Le même rejeu a montré la limite du lecteur simulé : un premier juge simulé, non calibré, a conclu à une audience que la vraie juge a refusée. Il a été recalibré (lecture de tri limitée, rejet comme position par défaut). Sa réponse favorable ne lève jamais un bloquant.
