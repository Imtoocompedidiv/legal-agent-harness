---
name: donnees-personnelles
description: "Données personnelles en droit français et européen : qualification d'un traitement et nécessité d'une analyse d'impact, revue d'un accord de sous-traitance, réponse à une demande d'exercice des droits, analyse d'impact, gestion d'une violation de données, traceurs, analyse d'écart après un texte nouveau, cohérence des engagements publiés. Dès qu'un traitement se conçoit, se contracte, se contrôle ou dysfonctionne."
---

# Données personnelles

Le pôle reprend les procédés du plugin de protection des données de la suite Claude for Legal (`docs/conseil/correspondance_donnees-personnelles.md`) et les applique au RGPD, à la loi Informatique et Libertés et à la doctrine de la CNIL. Toute règle employée se lit à la source, à la date du jour : RGPD et décisions de la CNIL sur LibreJustice, lignes directrices et recommandations sur cnil.fr. Le règlement sur l'intelligence artificielle relève du pôle `intelligence-artificielle`.

## 1. Avant de commencer

1. **Le rôle du client** pour ce traitement : responsable, responsable conjoint, sous-traitant. Tout le reste en dépend.
2. **Le profil et les positions** (`cabinet/` ou `~/.harness-juridique/`, skill `profil-et-positions`) : délégué à la protection des données, registre des traitements, engagements publiés (politique de confidentialité, mentions), positions contractuelles. À défaut, `references/positions.md`.
3. **Les engagements déjà pris.** Relire la politique de confidentialité et les analyses antérieures du même traitement : un traitement nouveau qui contredit un engagement publié est un écart en soi.

## 2. Les procédés

### 2.1 Qualification d'un traitement

Finalité, données (dont les catégories particulières de l'article 9 et les infractions de l'article 10), personnes concernées, base légale (art. 6), destinataires, transferts hors de l'Union (chapitre V ; décision d'adéquation en vigueur ou garanties appropriées), durée de conservation, sécurité. Puis la question de l'analyse d'impact : critères de l'article 35, liste de la CNIL des opérations qui l'exigent et lignes directrices européennes, à lire. Sortie : traitement à mener tel quel, à mener après les mesures listées, ou analyse d'impact requise ; et le renvoi au pôle `intelligence-artificielle` quand un système d'IA intervient.

### 2.2 Revue d'un accord de sous-traitance

Le sens d'abord : client responsable (revue protectrice) ou sous-traitant (revue défensive). Vérifier les mentions obligatoires de l'article 28, § 3 (objet, durée, nature, finalité, données, personnes, instructions documentées, confidentialité, sécurité, sous-traitants ultérieurs et leur autorisation au § 2, assistance pour les droits et les analyses d'impact, notification des violations, sort des données à la fin, audits), les transferts et leurs garanties, la cohérence avec la politique de confidentialité, puis comparer aux positions. Contre-propositions à la plus petite échelle utile. Le contrat principal relève du pôle `contrats-d-affaires`.

### 2.3 Demande d'exercice des droits

1. Qualifier la demande : accès, rectification, effacement, limitation, portabilité, opposition (art. 15 à 22), et la date de réception.
2. Vérifier l'identité de façon proportionnée, sans exiger plus que nécessaire.
3. Localiser les données, y compris dans les messageries et sauvegardes.
4. Examiner les limites : droits et libertés d'autrui (art. 15, § 4, occultation des tiers), exceptions à l'effacement (art. 17, § 3), motifs impérieux en cas d'opposition (art. 21).
5. Rédiger l'accusé de réception et la réponse. Délai : un mois à compter de la réception, prolongeable de deux mois compte tenu de la complexité ou du nombre de demandes, la personne étant informée de la prolongation et de ses motifs dans le premier mois (art. 12, § 3, lu le 21 novembre 2026). Inscrire l'échéance au dossier.
6. Tenir le journal des demandes.

### 2.4 Analyse d'impact

Description systématique du traitement et de ses finalités, nécessité et proportionnalité, risques pour les droits et libertés, mesures (art. 35, § 7) ; avis du délégué ; consultation préalable de la CNIL quand le risque résiduel reste élevé (art. 36). Au format maison s'il existe, sinon selon la méthode publiée par la CNIL, à lire.

### 2.5 Violation de données

1. Qualifier : atteinte à la confidentialité, à l'intégrité ou à la disponibilité ; données et personnes touchées ; date de prise de connaissance.
2. Notifier à la CNIL dans les meilleurs délais et si possible dans les 72 heures après en avoir pris connaissance, sauf si la violation n'est pas susceptible d'engendrer un risque, avec les motifs du retard au-delà, au besoin par étapes (art. 33, lu le 21 novembre 2026). Le sous-traitant notifie au responsable dans les meilleurs délais.
3. Communiquer la violation aux personnes quand elle est susceptible d'engendrer un risque élevé, sauf exceptions de l'article 34.
4. Documenter toute violation, même non notifiée (art. 33, § 5).
5. Mesures immédiates : contenir, conserver les preuves (pôle `precontentieux-et-portefeuille`), plainte pénale le cas échéant, assureur.

L'heure de prise de connaissance fixe le délai : la dire en tête du livrable avec l'heure limite.

### 2.6 Traceurs

Consentement préalable, sauf traceurs strictement nécessaires ou exemptés (loi n° 78-17, art. 82, à lire) ; refuser aussi simple qu'accepter et preuve du consentement, selon les lignes directrices et la recommandation de la CNIL en vigueur, à lire.

### 2.7 Analyse d'écart après un texte nouveau

Délimiter le texte et ses dates d'application ; extraire chaque exigence ; la confronter à l'état actuel (politique, registre, contrats, mesures) ; classer : à faire avant l'application, souhaitable, déjà conforme, écart accepté par le client avec sa raison ; plan de mise en conformité avec responsables et dates. Le veilleur signale les textes nouveaux.

### 2.8 Cohérence des engagements publiés

Relire les analyses, revues et qualifications récentes contre la politique de confidentialité et les mentions publiées ; lister les mises à jour requises, souhaitables, et ce qui n'appelle rien.

## 3. Le livrable

En tête, la conclusion et, s'il y a lieu, l'heure ou la date limite ; puis l'analyse, chaque règle avec sa source ; puis les actions et leurs responsables. Une réponse destinée à la personne concernée ou à la CNIL ne contient aucune analyse interne.

## 4. Garde-fous

- Contrôle de destination (`docs/CONSEIL.md`, section 5) : une analyse d'impact ou une note interne peut être demandée par la CNIL dans un contrôle.
- Aucune notification, aucune réponse, aucune communication aux personnes sans décision du client ; le délai de 72 heures se protège par un projet prêt.
- Aucune donnée personnelle du client ni des personnes concernées dans une requête publique.
