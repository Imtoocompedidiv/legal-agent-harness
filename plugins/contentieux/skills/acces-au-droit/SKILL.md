---
name: acces-au-droit
description: "Accès au droit et cliniques juridiques : entretien d'accueil et repérage des questions dans tous les domaines, aide juridictionnelle et son effet sur les délais, orientation vers les points-justice, conciliateurs, médiateurs et Défenseur des droits, lettres en langage clair, formulaires, mémo de cas, piste de recherche, échéances, supervision et passation. Dès qu'une personne sans conseil demande de l'aide ou qu'une clinique traite un dossier."
---

# Accès au droit

Le pôle reprend les procédés du plugin de clinique juridique de la suite Claude for Legal (`docs/conseil/correspondance_acces-au-droit.md`) et les applique à l'accès au droit en France. Toute règle employée se lit à la source, à la date du jour ; les formulaires se lisent sur Service-Public.

## 1. Accueil

1. Écouter le récit, puis le reprendre par écrit : faits datés, personnes, documents en main, ce que la personne veut obtenir.
2. Repérer toutes les questions de droit du récit, dans tous les domaines, et pour chacune le pôle ou l'exercice du harness qui la traite (ligne `description` de chaque skill).
3. Repérer d'abord ce qui court : délai de recours ou d'appel, prescription, forclusion, audience fixée. Chaque délai se calcule à la source (`scripts/voies.py`) et s'inscrit au registre `procedures`.
4. Conflit d'intérêts : la structure ne suit pas une personne dont l'adversaire est déjà suivi.
5. Ce que la structure peut faire : information et orientation, consultation juridique dans les conditions de la loi n° 71-1130 (art. 54 et suivants : qui peut donner une consultation, à quelles conditions), assistance et représentation par un avocat.

## 2. Aide juridictionnelle

- Conditions de ressources et plafonds de l'année, procédure et formulaire : loi n° 91-647 et décret n° 2020-1717, à lire dans leur version en vigueur ; formulaire sur Service-Public.
- Effet sur les délais : quand une action ou un recours doit être intenté dans un délai devant une juridiction de première instance ou d'appel, il est réputé intenté dans le délai si la demande d'aide est adressée ou déposée au bureau d'aide juridictionnelle avant l'expiration du délai et si l'action est introduite dans un nouveau délai de même durée à compter de la notification de la décision sur l'aide ou, plus tard, de la désignation de l'auxiliaire de justice ; une nouvelle demande au même objet après un rejet n'interrompt pas à nouveau le délai (décret n° 2020-1717, art. 43, version du 13 juin 2026, lu le 21 novembre 2026). Les délais de conclusions de l'appel civil suivent le même article.
- La demande se dépose avant l'expiration du délai, et la date de dépôt se prouve.

## 3. Orientation

Points-justice et conseils départementaux de l'accès au droit, conciliateur de justice (tentative préalable obligatoire dans les cas de l'article 750-1 du CPC, lu le 21 novembre 2026), médiateurs de la consommation et des administrations, Défenseur des droits (exercice `defenseur_des_droits`). Chaque orientation dit ce que la personne obtient, comment, et dans quel délai.

## 4. Écrits

- Lettres en langage clair : phrases courtes, mots courants, une idée par paragraphe, la demande et la date limite en tête ; un terme juridique nécessaire s'explique.
- Lettres usuelles (rendez-vous, demande de pièces, point d'étape), formulaires remplis avec la personne, projet d'acte simple.
- Mémo de cas : faits, questions, règles lues à la source, application, réponse, recherches qui restent à faire.
- Piste de recherche : textes à lire, notions, requêtes LibreJustice, sans citation non lue.
- Statut du dossier selon le destinataire : la personne, l'encadrant, la juridiction.

## 5. Supervision et continuité

Tout écrit d'un étudiant destiné à la personne ou à un tiers passe par l'encadrant que désigne la structure ; la file de relecture liste ce qui attend sa validation. En fin de semestre, une note de passation par dossier (faits, actes faits, échéances, prochaine étape) ; en début de semestre, l'intégration des nouveaux (procédures de la structure, outils, dossiers en cours).

## 6. Garde-fous

- Aucune donnée de la personne dans une requête publique.
- Aucun envoi ni dépôt sans l'accord de la personne et de l'encadrant.
