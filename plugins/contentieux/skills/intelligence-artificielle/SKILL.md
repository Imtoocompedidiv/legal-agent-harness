---
name: intelligence-artificielle
description: "Intelligence artificielle en droit européen et français : inventaire des systèmes et rôle du client, qualification d'un cas d'usage (pratique interdite, haut risque, transparence, modèle à usage général), calendrier d'application du règlement sur l'IA modifié en 2026, analyse d'impact, revue des conditions d'un fournisseur d'IA, charte interne, analyse d'écart. Dès qu'un système d'IA se conçoit, s'achète, se déploie ou se contrôle."
---

# Intelligence artificielle

Le pôle reprend les procédés du plugin de gouvernance de l'IA de la suite Claude for Legal (`docs/conseil/correspondance_intelligence-artificielle.md`) et les applique au règlement (UE) 2024/1689 et au droit français. Le règlement a été modifié par le règlement (UE) 2026/1744 du 8 juillet 2026 (omnibus numérique sur l'IA) : toute obligation se lit dans sa version modifiée, à la date du jour, sur LibreJustice. Le RGPD relève du pôle `donnees-personnelles`, qui s'applique en même temps.

## 1. Calendrier, lu à la source le 21 novembre 2026

- Pratiques interdites de l'article 5, dont l'inférence des émotions d'une personne sur le lieu de travail et dans les établissements d'enseignement sauf raisons médicales ou de sécurité : applicables depuis le 2 février 2025. Interdictions ajoutées par le règlement (UE) 2026/1744 (art. 5, § 1, points b bis et b ter, § 1 bis et 1 ter) : applicables à compter du 2 décembre 2026.
- Obligations des systèmes à haut risque (chapitre III, sections 1 à 3) : à compter du 2 décembre 2027 pour ceux de l'annexe III (dont l'emploi et la gestion des travailleurs), du 2 août 2028 pour ceux de l'article 6, § 1, et de l'annexe I.
- Systèmes qui génèrent des contenus de synthèse mis sur le marché avant le 2 août 2026 : conformité à l'article 50, § 2, d'ici au 2 décembre 2026.
- Toute autre date (modèles à usage général, maîtrise de l'IA de l'article 4, sanctions, autorités nationales désignées) se lit dans l'article 113 modifié et dans les textes français de désignation, à vérifier avant usage.

## 2. Les procédés

### 2.1 Inventaire des systèmes

Pour chaque système : fonction, fournisseur, rôle du client (fournisseur, déployeur, importateur, distributeur, mandataire), données employées, personnes touchées, décision appuyée, catégorie (interdit, haut risque, transparence, usage général, risque minimal) avec l'article qui la fonde et la date d'application. L'inventaire constate ; il ne déduit pas d'obligation sans la lire.

### 2.2 Qualification d'un cas d'usage

1. Comprendre le cas : ce que fait le système, sur qui, pour quelle décision, avec quelle intervention humaine.
2. Lignes rouges : les pratiques de l'article 5 d'abord ; une pratique interdite arrête l'analyse et se dit en tête.
3. Haut risque : article 6 et annexes I et III ; exceptions de l'article 6, § 3, à documenter.
4. Transparence (art. 50) et modèles à usage général (art. 51 et suivants) selon le rôle.
5. Ce qui s'applique déjà indépendamment du calendrier du règlement : RGPD (base légale, information, décision exclusivement automatisée de l'article 22, analyse d'impact), droit du travail (information des salariés et consultation du CSE sur l'introduction de technologies nouvelles, C. trav., art. L. 2312-8, à lire ; dispositif de collecte porté à la connaissance du salarié, art. L. 1222-4), non-discrimination.
6. Sortie : autorisé, autorisé sous conditions listées, interdit ; renvois aux pôles concernés ; mise à jour de l'inventaire.

### 2.3 Analyse d'impact

Quand le règlement l'exige (analyse d'impact sur les droits fondamentaux de l'article 27 pour les déployeurs qu'il vise) et, en tout cas, quand le RGPD l'exige (art. 35) : description du système, personnes touchées, données, décisions et supervision humaine, exactitude et défaillances, déploiement, classification réglementaire, mesures. Une seule analyse peut couvrir les deux exigences si elle remplit chacune.

### 2.4 Revue des conditions d'un fournisseur d'IA

Usage des données du client pour entraîner ou améliorer les modèles, confidentialité et secret des affaires, propriété et droits sur les résultats, garanties sur les contenus tiers, changement de modèle ou de fonction, localisation et sous-traitants, documentation et informations dues au déployeur d'un système à haut risque (art. 13 et 26), répartition des rôles au sens du règlement, responsabilité et plafond. Comparer aux positions ; contre-propositions à la plus petite échelle utile ; le contrat principal relève du pôle `contrats-d-affaires`.

### 2.5 Charte interne

Entretien de périmètre (outils autorisés, données interdites dans les outils, validation humaine, traçabilité, formation), puis projet : usages permis et interdits, données, responsabilités, contrôle, sanctions. Une charte qui prévoit des sanctions ou des obligations générales et permanentes relève du règlement intérieur et de ses formalités (pôle `droit-social`).

### 2.6 Analyse d'écart et cohérence

Même méthode que le pôle `donnees-personnelles` (2.7 et 2.8), appliquée au règlement sur l'IA et à la charte interne.

## 3. Le livrable

En tête, la conclusion (interdit, haut risque et à partir de quand, autorisé sous conditions) avec l'article et la date d'application ; puis l'analyse ; puis les actions, leurs responsables et leurs dates.

## 4. Garde-fous

- Distinguer toujours ce qui est en vigueur de ce qui est seulement adopté pour plus tard ou proposé, avec la date de la source.
- Contrôle de destination (`docs/CONSEIL.md`, section 5).
- Aucune donnée du client dans une requête publique ; aucun document du client versé dans un outil d'IA tiers par le harness.
