---
name: contentieux-du-fond
description: "Instance au fond, administrative ou judiciaire (excès de pouvoir, plein contentieux, assignation, conclusions, appel, exécution) : recevabilité, exceptions, preuve, hiérarchie des demandes. Pour toute requête, assignation, mémoire ou conclusions au fond."
---

# Contentieux du fond

Textes à lire dans leur version applicable avant usage, décisions à inscrire au registre après lecture. Les références ci-dessous marquées « vérifié » ont été contrôlées sur LibreJustice le 18 novembre 2026 (analyse ou sommaire officiel) ; les autres sont à relire.

## 1. Juge administratif

- **Recevabilité.** Décision faisant grief, intérêt et qualité, délai (CJA, R. 421-1 et R. 421-2 ; prorogation par recours administratif, CRPA, L. 411-2), mentions des voies et délais ; sans elles, délai raisonnable d'un an à compter de la connaissance (CE, Ass., 13 juillet 2016, Czabaj, n° 387763, vérifié). En matière indemnitaire, liaison du contentieux par une demande préalable (R. 421-1). Représentation selon R. 431-2 et R. 431-3.
- **Moyens.** Légalité externe (compétence, forme, procédure, motivation) et interne (erreur de droit, erreur de fait, qualification, erreur manifeste, détournement de pouvoir). Après l'expiration du délai de recours, un moyen relevant d'une cause juridique non invoquée dans le délai est irrecevable, sauf ordre public : soulever au moins un moyen de chaque cause dans le délai. Exception d'illégalité d'un règlement : ses règles, la compétence de son auteur et le détournement de pouvoir sont invocables, ses vices de forme et de procédure ne le sont plus après le délai (CE, Ass., 18 mai 2018, Fédération des finances et des affaires économiques de la CFDT, n° 414583, vérifié).
- **Hiérarchie des demandes.** Le requérant qui hiérarchise ses prétentions selon la cause juridique de ses conclusions principales à fin d'annulation, avant l'expiration du délai de recours, et pas nécessairement dans la requête, lie le juge, qui examine d'abord les moyens de cette cause ; des conclusions à fin d'injonction dans un sens déterminé l'obligent de même à examiner d'abord les moyens qui la justifieraient (CE, Sect., 21 décembre 2018, Société Eden, n° 409678, publié au Recueil, lu en entier le 20 novembre 2026).
- **Preuve.** Le juge dirige l'instruction ; demander qu'il use de ses pouvoirs quand l'administration détient la preuve, et tirer les conséquences de son silence ou de son refus de produire (références dans `refere-administratif/references/arrets.md`, section preuve).
- **Injonction, astreinte, exécution.** Conclusions à fin d'injonction et d'astreinte dès la requête (CJA, L. 911-1 à L. 911-3) ; en cas d'inexécution, demande d'exécution (L. 911-4) et procédure d'exécution du livre IX.
- **Instruction et clôture.** L'administration mise en demeure qui ne produit pas peut être réputée avoir acquiescé aux faits (R. 612-6, à relire) : demander la mise en demeure quand son délai de défense est expiré ; le requérant qui ne produit pas le mémoire complémentaire annoncé peut être réputé désisté (R. 612-5) ; mémoire récapitulatif seulement sur invitation (R. 611-8-1), qui répute abandonnés les moyens non repris ; après un rejet de référé-suspension faute de moyen sérieux, confirmer le maintien dans le mois (R. 612-5-2).

## 2. Juge judiciaire

- **Introduction.** Assignation ou requête selon la matière, mentions des articles 54 et 56 du CPC, tentative préalable de règlement amiable lorsque l'article 750-1 l'exige, représentation (art. 760 et 761).
- **Concentration des moyens.** Tous les moyens au soutien d'une demande se présentent dès la première instance qui la concerne, sous peine de se heurter à la chose jugée (Cass., ass. plén., 7 juillet 2006, Cesareo, n° 04-10.672, vérifié).
- **Défense procédurale.** Exceptions de procédure (art. 73 à 121) soulevées simultanément et avant toute défense au fond ; fins de non-recevoir (art. 122 à 126) en tout état de cause, sauf disposition contraire, avec possible condamnation à des dommages-intérêts pour abstention dilatoire (art. 123). Dès sa désignation et jusqu'à son dessaisissement, le juge de la mise en état est seul compétent pour les exceptions de procédure, les incidents mettant fin à l'instance et les fins de non-recevoir (art. 789, 1° et 6°), sauf renvoi d'une fin de non-recevoir à la formation de jugement, à reprendre alors dans les conclusions au fond. Après l'ordonnance de clôture, exceptions, incidents et fins de non-recevoir ne sont recevables que si leur cause survient ou est révélée ensuite (art. 802, al. 4).
- **Preuve.** Charge selon l'article 1353 du code civil et l'article 9 du CPC ; production forcée (art. 11, 138 à 142) ; mesures d'instruction (art. 143 et s.) ; preuve déloyale admise si indispensable et proportionnée (Cass., ass. plén., 22 décembre 2023, n° 20-20.648, à relire).
- **Conclusions.** Prétentions et moyens formulés expressément, récapitulation exigée (art. 768 devant le tribunal judiciaire ; art. 954 en appel) ; la partie qui fait état d'une pièce la communique spontanément à toute autre partie (art. 132), et moyens et preuves se font connaître en temps utile pour que chacun organise sa défense (art. 15).
- **Appel.** Délai d'un mois en matière contentieuse (art. 538), procédure et délais de la procédure avec représentation obligatoire dans leur version applicable (à relire à chaque dossier), effet dévolutif limité aux chefs critiqués.
- **Exécution.** Signification, titre exécutoire, astreinte et juge de l'exécution (code des procédures civiles d'exécution).

## 3. Méthode

Fiche de l'acte et contrôle avant dépôt comme pour un référé (`type_acte` `requete_fond_admin`, `assignation` ou `conclusions`). Les délais se calculent par `voies.py` depuis la chronologie typée, puis se vérifient sur leur texte. Les écritures successives se coordonnent avec l'instance de référé : ce qui se plaide au référé (un moyen fort, une demande accordable) n'épuise pas ce qui se garde au fond (tous les moyens de chaque cause, les conclusions indemnitaires, l'exception d'illégalité développée).
