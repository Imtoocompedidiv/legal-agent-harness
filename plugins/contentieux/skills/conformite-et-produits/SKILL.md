---
name: conformite-et-produits
description: "Conformité des produits et veille réglementaire en droit français et européen : revue d'un lancement, risque d'une fonctionnalité, allégations publicitaires et environnementales, annonces de prix, question rapide, veille des textes et des autorités, analyse d'écart d'une politique interne, suivi des écarts, révision proposée d'une politique, consultations publiques et notification des règles techniques. Dès qu'un produit, une publicité ou une politique doit être confronté au droit en vigueur."
---

# Conformité et produits

Le pôle reprend les procédés des plugins de droit des produits et de veille réglementaire de la suite Claude for Legal (`docs/conseil/correspondance_conformite-et-produits.md`) et les applique au droit français et européen. Toute règle employée se lit à la source, à la date du jour ; une directive se lit avec sa transposition française, dont la date et l'état se vérifient. Les données personnelles et l'IA ont leurs pôles.

## 1. Les procédés

### 1.1 Revue d'un lancement

Confronter le produit, son parcours et ses messages aux règles qui le touchent, chacune lue à la source et seulement si elle s'applique :
- vente aux consommateurs : information précontractuelle (C. conso., art. L. 111-1), contrat à distance et droit de rétractation (art. L. 221-5 et L. 221-18), garanties légales de conformité (art. L. 217-3 et suivants), clauses abusives (art. L. 212-1) ;
- pratiques commerciales trompeuses et agressives (art. L. 121-2 et suivants, L. 121-6), publicité comparative (art. L. 122-1), annonces de réduction de prix (art. L. 112-1-1 : prix antérieur égal au prix le plus bas des trente derniers jours, lu le 21 novembre 2026) ;
- allégations environnementales : neutralité carbone interdite sauf bilan, trajectoire de réduction et compensation publiés (C. env., art. L. 229-68, lu le 21 novembre 2026) ; autres allégations interdites sur les produits et emballages (art. L. 541-9-1, à lire) ; directive (UE) 2024/825 modifiant l'annexe des pratiques réputées trompeuses, applicable depuis le 27 septembre 2026, dont la transposition française se vérifie avant d'écrire ;
- influence commerciale (loi n° 2023-451, à lire), langue française (loi n° 94-665, à lire) ;
- services numériques : obligations du règlement (UE) 2022/2065 selon la taille et la catégorie du service ;
- accessibilité des produits et services (directive (UE) 2019/882 et sa transposition, à lire) ;
- sécurité générale des produits (règlement (UE) 2023/988) ; cyberrésilience des produits comportant des éléments numériques (règlement (UE) 2024/2847, calendrier à lire).
Sortie : lancer, lancer après les changements listés, ou ne pas lancer ; chaque point avec sa règle, sa source et la correction proposée.

### 1.2 Risque d'une fonctionnalité

Ce que fait la fonctionnalité, sur qui, avec quelles données ; les règles touchées (y compris celles des pôles voisins) ; le risque coté VERT, ORANGE, ROUGE selon la grille de `docs/CONSEIL.md` ; les mesures qui ramènent le risque au niveau accepté par le client.

### 1.3 Allégations publicitaires

Chaque allégation : ce qu'elle affirme, la preuve qui l'étaie (essai, donnée, source), le texte qui l'encadre ; à garder, à reformuler (avec la formulation proposée) ou à retirer.

### 1.4 Question rapide

Pour la question posée en passant : réponse fermée quand elle peut l'être, avec la règle et sa source, la réserve qui compte, et le renvoi à une revue complète quand la réponse en dépend.

### 1.5 Veille des textes et des autorités

Sources : Journal officiel et Journal officiel de l'Union, lus sur LibreJustice ; décisions et lignes directrices des autorités du profil (DGCCRF, Arcom, AMF, ACPR, ARCEP, CRE, CNIL, Autorité de la concurrence) sur leurs sites officiels. Pour chaque texte ou décision qui touche le client : ce qui change, à partir de quand, quelle politique ou quel produit, et l'analyse d'écart à mener. Le sous-agent `veilleur` conduit cette veille et en écrit le rapport.

### 1.6 Analyse d'écart d'une politique interne

Délimiter le texte et ses dates ; extraire chaque exigence ; la confronter à la politique et à la pratique ; classer : à faire avant l'application, souhaitable, conforme, écart accepté par le client avec sa raison ; plan de mise en conformité, responsables et dates.

### 1.7 Suivi des écarts

Chaque écart ouvert, son responsable, sa date cible, son état ; les écarts dépassés en tête. Le registre se tient dans `registres/ecarts.json` du profil.

### 1.8 Révision proposée d'une politique

Une proposition en révisions suivies, adressée au propriétaire de la politique, chaque modification reliée à l'exigence qu'elle satisfait ; jamais une modification directe du document source.

### 1.9 Consultations publiques et règles techniques

Consultations de la Commission européenne et des autorités françaises : objet, date limite, intérêt du client, projet de contribution. Un projet de règle technique national se notifie à la Commission avant adoption, avec un délai de statu quo (directive (UE) 2015/1535, à lire) : à surveiller quand une règle française touche les produits du client.

## 2. Garde-fous

- Contrôle de destination (`docs/CONSEIL.md`, section 5) : une revue de lancement peut être saisie lors d'une enquête de la DGCCRF ou d'une visite de l'Autorité de la concurrence.
- Aucune publication, aucun lancement, aucune contribution envoyée sans décision du client.
- Aucune donnée du client dans une requête publique.
