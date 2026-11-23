---
name: propriete-intellectuelle
description: "Propriété intellectuelle en droit français et européen : disponibilité d'une marque, opposition, mise en demeure de contrefaçon émise ou reçue, retrait de contenus en ligne et contestation, licences libres, liberté d'exploitation d'un brevet, triage d'une contrefaçon, invention de salarié, clauses de cession et de licence, portefeuille et renouvellements. Dès qu'un signe, une œuvre, un logiciel, une invention ou un contenu en ligne est en jeu."
---

# Propriété intellectuelle

Le pôle reprend les procédés du plugin de propriété intellectuelle de la suite Claude for Legal (`docs/conseil/correspondance_propriete-intellectuelle.md`) et les applique au code de la propriété intellectuelle, au droit de l'Union et au règlement sur les services numériques. Toute règle employée se lit à la source, à la date du jour. L'action en justice relève du contentieux : ce pôle fait l'analyse et la lettre, le procès suit ses exercices.

## 1. Avant de commencer

Le titre et son état : marque (numéro, office, classes, date de dépôt, statut), brevet (numéro, office, revendications, annuités), œuvre ou logiciel (auteur, date, contrat), dessin ou modèle. Les registres se consultent à la source (INPI pour les titres français, EUIPO pour les marques et dessins de l'Union, OEB pour les brevets européens) ; un statut ne s'écrit pas de mémoire. Le profil et les positions du client (`cabinet/` ou `~/.harness-juridique/`) disent sa posture de défense : ferme, graduée, conciliante.

## 2. Les procédés

### 2.1 Disponibilité d'une marque

Distinctivité du signe (CPI, art. L. 711-2) ; recherche des antériorités identiques et similaires dans les classes visées et les classes voisines (marques françaises, de l'Union et internationales visant la France, dénominations sociales, noms de domaine, noms commerciaux) ; risque de confusion apprécié globalement ; obstacle rédhibitoire signalé en tête. C'est une première recherche, qui dit ses bases et ses limites, et non un avis de disponibilité.

### 2.2 Opposition

Contre une demande publiée : opposition devant le directeur général de l'INPI dans les deux mois suivant la publication de la demande, sur les droits antérieurs que liste l'article L. 712-4 (lu le 21 novembre 2026) ; pour une marque de l'Union, opposition devant l'EUIPO dans son délai propre, à lire. Calculer la date limite et l'inscrire au registre `pi`.

### 2.3 Mise en demeure de contrefaçon, émise ou reçue

Émise : le droit invoqué et sa preuve, l'acte reproché daté et prouvé (constat), la demande précise (cesser, retirer, détruire, rendre compte), le délai, ce qui suivra ; le ton suit la posture du client, sans menace qui excède le droit ni dénigrement. Reçue : vérifier le titre adverse (existence, étendue, date, usage pour une marque de plus de cinq ans), la réalité de l'acte, les moyens (antériorité, absence de confusion, exception, épuisement, déchéance ou nullité du titre), puis répondre sans reconnaître. Actions et mesures : saisie-contrefaçon (CPI, art. L. 332-1, L. 521-4, L. 615-5, L. 716-4-7, à lire), compétence exclusive des tribunaux judiciaires désignés, prescription à lire pour chaque droit.

### 2.4 Retrait de contenus en ligne et contestation

Notification à un hébergeur ou à une plateforme selon le règlement (UE) 2022/2065 (art. 16 : mécanisme de notification, éléments requis) et la loi n° 2004-575 dans sa version en vigueur ; contestation par le système interne de traitement des réclamations de la plateforme (art. 20) et règlement extrajudiciaire (art. 21). Une notification abusive engage son auteur : n'affirmer que ce qui est établi.

### 2.5 Licences libres

Pour chaque composant : licence (permissive, à réciprocité faible, à réciprocité forte, y compris l'AGPL pour un service en réseau, et les licences CeCILL), mode de distribution du produit du client, obligations déclenchées (mentions, fourniture du code source, compatibilité des licences entre elles). Sortie : composant accepté, accepté sous conditions listées, à remplacer.

### 2.6 Liberté d'exploitation d'un brevet

Triage, non avis : brevets en vigueur dans les pays visés (statut et annuités sur les registres), revendications indépendantes confrontées élément par élément au produit, antériorités visibles, date d'expiration, options (contournement, licence, opposition devant l'OEB dans son délai, action en nullité). Le livrable dit ce qui a été lu et ce qui ne l'a pas été.

### 2.7 Triage d'une contrefaçon

Par droit en cause (marque, droit d'auteur, brevet, dessin ou modèle, secret des affaires) : les éléments de la contrefaçon, les preuves disponibles et à obtenir, les défenses, les mesures urgentes, le coût et la durée d'une action. Facteurs, non conclusion.

### 2.8 Invention de salarié

Classement de l'invention (mission, hors mission attribuable, hors mission non attribuable, CPI, art. L. 611-7, à lire) ; déclaration et délais de la procédure réglementaire, à lire ; rémunération supplémentaire due pour l'invention de mission ; juste prix pour l'invention attribuée ; dépôt avant toute divulgation.

### 2.9 Clauses de cession et de licence

Cession de droits d'auteur : chacun des droits cédés mentionné distinctement, domaine d'exploitation délimité quant à son étendue et à sa destination, au lieu et à la durée (CPI, art. L. 131-3, lu le 21 novembre 2026) ; la cession globale des œuvres futures est nulle (art. L. 131-1, à lire) ; droits patrimoniaux sur le logiciel créé par un salarié dans ses fonctions dévolus à l'employeur (art. L. 113-9, à lire), ce qui ne vaut pas pour un prestataire indépendant. Licences : exclusivité, territoire, durée, redevances, garanties de jouissance paisible et d'éviction, sous-licence. Contre-propositions à la plus petite échelle utile.

### 2.10 Portefeuille et renouvellements

Inscrire chaque titre au registre `pi` (`python "${CLAUDE_PLUGIN_ROOT}/scripts/echeancier.py" squelette pi`). Pour une marque française, l'échéancier calcule l'expiration à dix ans du dépôt, l'ouverture du renouvellement un an avant et le délai de grâce de six mois avec supplément de redevance (CPI, art. L. 712-1 et R. 712-24, lus le 21 novembre 2026). Les annuités de brevet, les marques de l'Union et les dessins et modèles s'inscrivent en échéances explicites, avec leur source.

## 3. Garde-fous

- Contrôle de destination (`docs/CONSEIL.md`, section 5).
- Aucune mise en demeure, aucune notification de retrait, aucun dépôt ni opposition sans décision du client.
- Aucune invention non déposée ni information confidentielle du client dans une requête publique.
