---
name: ecriture-juridictionnelle
description: "Rédiger une écriture destinée à un juge ou un courrier précontentieux décisif : théorie du cas, première page, récit, moyens, conclusions, passe de style."
---

# Écriture juridictionnelle

Le lecteur est un magistrat qui a d'autres dossiers ouverts. Il doit savoir après une page ce qu'on lui demande, sur quel acte ou quelle prétention, et pourquoi y faire droit est la solution sûre. Tout le reste sert cette page.

## 1. Avant d'écrire

- **Le brief du texte et le récit.** Lecteur, ce qu'il doit faire, enjeu, message central, objection, puis l'histoire en quatre temps : skill `recit-judiciaire`, sections 1 à 4. L'écriture n'en est que la mise en forme.
- **Théorie du cas.** Un paragraphe : ce qui s'est passé, la règle qui commande, pourquoi l'adversaire l'a méconnue, ce que le juge doit faire et pourquoi c'est sans risque pour lui. Si ce paragraphe ne tient pas, le problème est stratégique, pas rédactionnel (skill `strategie-contentieuse`).
- **La question.** Une phrase, dans les termes où le juge la tranchera. Elle figure en première page.
- **Le lecteur.** Juge du tri, juge des référés à l'audience, formation collégiale avec rapporteur public, conseiller rapporteur : la densité, l'ordre et les autorités se choisissent pour lui (`strategie-contentieuse`, section des décideurs).
- **Le tri des matériaux.** Ce qui ne sert pas la question reste dehors et va dans la feuille d'audience, avec sa réponse préparée. Une objection que le juge ne se posera pas à la lecture n'a pas à être réfutée dans le texte.

## 2. Première page

En-tête exact (juridiction, formation, procédure et texte qui la fonde, parties, numéro de l'instance liée). Puis l'acte ou la prétention, désigné par son auteur, sa date et son objet. Puis la demande, en une phrase. Puis la question. Puis les quelques faits datés qui décident. Le fait que l'adversaire mettra en avant est neutralisé dès ce stade par la question posée ou par le fait qui le dépasse, sans jamais être concédé : le juge ne doit pas pouvoir écrire son premier considérant avec le récit de l'adversaire.

## 3. Faits

Ordre chronologique, chaque fait daté et suivi de sa pièce, sans qualificatif. Les citations de pièces sont courtes, exactes, entre guillemets. Avant de bâtir un moyen sur une phrase de l'adversaire, lire son paragraphe entier et les autres pièces du même auteur : une citation exacte sortie de son contexte fait tomber le moyen et la crédibilité du reste. Les faits humains se disent par leurs effets concrets et datés, sans pathos. Aucune concession, aucune excuse, aucune formule de déférence envers le juge ou l'adversaire.

## 4. Discussion

Le moyen qui gagne vient en premier. Chaque moyen suit l'ordre règle citée (texte lu, version applicable), fait prouvé (pièce), conséquence. Il s'affirme ; la voix du requérant n'est pas celle d'un commentateur qui rapporte ses propres thèses. L'objection la plus forte de l'adversaire est prise dans sa meilleure version et réfutée immédiatement après le moyen qu'elle vise. Une autorité par règle, choisie pour ce juge : la décision de la juridiction suprême qui porte la règle, et la décision locale quand elle existe, chacune avec son point. Les comparaisons, garanties conventionnelles et moyens qui exigent une instruction vont au fond, pas au référé.

## 5. Conclusions

Courtes, numérotées, accordables par ce juge à ce stade, avec des délais qu'il ordonne d'ordinaire. Devant le juge administratif, la hiérarchie des demandes fixée avant l'expiration du délai de recours lie le juge, qui examine d'abord les moyens justifiant l'injonction demandée (CE, Section, 21 décembre 2018, Société Eden, n° 409678, texte lu) : hiérarchiser dans la requête elle-même. La forme suit la charte des écritures devant les tribunaux et cours administratives du 15 décembre 2025 (références de `strategie-contentieuse`). Une conclusion sans pouvoir du juge identifié se retire. Aucune branche conditionnelle en référé. Une conclusion subsidiaire n'existe que si elle répond à une lecture que le juge peut réellement adopter et qu'on ne peut pas réfuter dans le texte.

## 6. Style

Mots simples, verbes d'action, paragraphes numérotés, une idée par paragraphe. Pas de jargon décoratif, d'adverbes d'insistance, de majuscules ou de gras pour crier. Respecter la charte de rédaction de l'utilisateur et les consignes de style propres au client (`etat/affaire.json`, `consignes.ponctuation_interdite_textes_client`). Chaque affirmation de fait porte sa pièce, chaque affirmation de droit sa source inscrite au registre.

## 7. Chaîne de production

1. Brouillon dans `ecritures/brouillons/<acte>_vN.md` ; le hook PostToolUse signale à chaque enregistrement les défauts mécaniques bloquants au dépôt.
2. Fiche de l'acte dans `ecritures/controle/<acte>_vN.fiche.json` (skill `controle-avant-depot`).
3. Passe de style par le sous-agent `plume`, qui ne change ni les faits, ni les pièces, ni les moyens, ni les conclusions.
4. Lecture à froid par `juge-simule`, contradiction par `contradicteur`, vérification des sources par `verificateur-sources`.
5. Corrections, nouvelle version, contrôle PASS, `affaire.py finaliser`, accord exprès du client, dépôt, `affaire.py depot`.

La relecture finale se fait sur la version assemblée, de la première à la dernière ligne : un assemblage peut réintroduire un passage retiré.
