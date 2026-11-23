---
name: precontentieux-et-portefeuille
description: "Avant et autour du procès : mise en demeure émise ou réclamation reçue, demandes et contrôles des autorités, conservation des preuves, préparation d'une audition ou d'une expertise, tableau des éléments constitutifs face aux preuves, tri des pièces protégées avant communication, portefeuille des affaires, point d'affaire, suivi des avocats correspondants et clôture. Dès qu'un litige s'annonce, qu'une autorité frappe à la porte ou qu'un portefeuille se pilote."
---

# Précontentieux et portefeuille

Le pôle reprend ce que le plugin de contentieux de la suite Claude for Legal apporte et que le harness ne couvrait pas encore (`docs/conseil/correspondance_precontentieux-et-portefeuille.md`). La prise en main d'une affaire, la chronologie, l'écriture juridictionnelle, la négociation et les exercices juridictionnels restent dans leurs skills : ce pôle y renvoie. Toute règle employée se lit à la source, à la date du jour.

## 1. Les fiches

- `references/mise-en-demeure-emise.md` (mission `mise_en_demeure_emise`) : effets de la mise en demeure (clause résolutoire, résolution par notification, dommages et intérêts, intérêts moratoires), ce qu'elle n'interrompt pas (prescription), tentative préalable de résolution amiable (CPC, art. 750-1), correspondance entre avocats.
- `references/reclamation-recue.md` (mission `reclamation_recue`) : délais qui courent vraiment (clauses résolutoires des baux, assurance, intérêts), réponse sans reconnaissance ni aveu, déclaration à l'assureur, confidentialité de ce qui se dit en médiation ou conciliation.

## 2. Les autres missions, avec les textes à lire

- **Demandes et contrôles des autorités.** Identifier l'autorité, le fondement de son pouvoir et ses limites : réquisitions judiciaires (CPP, art. 60-1, 77-1-1, 99-3), droit de communication de l'administration fiscale (LPF, art. L. 81 et suivants), contrôle URSSAF (CSS, art. L. 243-7), contrôle de la CNIL (loi n° 78-17, art. 19 et suivants), enquêtes de la DGCCRF (C. conso., livre V), inspection du travail (C. trav., art. L. 8113-1 et suivants), visites et saisies de l'Autorité de la concurrence (C. com., art. L. 450-4). Pour chaque demande : ce qui doit être remis, dans quel délai, ce qui peut être refusé (secret professionnel de l'avocat ; à compter du 1er janvier 2027, consultations du juriste d'entreprise aux conditions de l'article 58-1 de la loi n° 71-1130, hors procédure pénale ou fiscale), la sanction d'un refus ou d'une obstruction, et le recours. Répondre dans le délai, par écrit, sans excéder la demande.
- **Conservation des preuves.** Sans procédure de *discovery*, le risque est double : perdre la preuve utile et détruire ce que la loi oblige à conserver. Lister les durées légales de conservation applicables (comptables, sociales, données personnelles), suspendre les purges automatiques sur le périmètre du litige, figer les preuves fragiles (constat de commissaire de justice, captures datées), envisager les mesures conservatoires et la mesure d'instruction de l'article 145 du CPC (exercice `mesure_instruction_145`). La destruction d'un document de nature à faciliter la découverte d'un crime ou d'un délit est réprimée (C. pén., art. 434-4, à lire).
- **Préparation d'une audition ou d'une expertise.** Attestation et témoin en procédure civile (CPC, art. 199 et suivants, mentions de l'art. 202) ; audition libre et garde à vue et leurs droits (CPP, art. 61-1 et 63-1 et suivants) ; expertise judiciaire contradictoire, dires et pré-rapport (CPC, art. 232 et suivants, 276). Préparer le client à dire vrai, à connaître les pièces, à ne pas spéculer ; jamais à dire faux (subornation de témoin, C. pén., art. 434-15).
- **Tableau des éléments constitutifs.** Pour chaque action ou infraction : ses éléments, chacun lu dans le texte et la jurisprudence ; pour chaque élément, la preuve dont on dispose (pièce et extrait), celle qui manque et comment l'obtenir ; la défense prévisible à chaque élément. Le tableau nourrit `theorie-de-l-affaire` et la matrice des preuves.
- **Tri des pièces protégées avant communication.** Avant de communiquer (CPC, art. 132 et suivants) ou de répondre à une autorité : écarter ou signaler ce que couvre le secret professionnel de l'avocat, protéger le secret des affaires devant le juge (C. com., art. L. 153-1 et suivants), minimiser les données personnelles de tiers. Le classement se fait pièce par pièce, avec la raison, et la décision de communiquer revient au client.
- **Portefeuille des affaires.** Pour chaque dossier : enjeu, risque coté, prochaine échéance (registre `procedures` et `scripts/echeancier.py`), dernier acte, prochaine décision du client, dossier sans mouvement depuis longtemps. Tri par risque et par échéance ; ce qui demande une décision vient en tête.
- **Point d'affaire.** Pour un appel du client ou d'un correspondant : où en est l'affaire, ce qui a changé, le risque, les options et la décision attendue, en une page.
- **Suivi des avocats correspondants.** Projet de demande de point périodique à chaque correspondant, à partir du registre : actes faits, prochaines échéances, budget consommé ; le client envoie.
- **Clôture du dossier.** Vérifier que plus rien ne court (voies de recours, exécution, prescription), restituer les originaux, archiver avec la durée de conservation retenue (la responsabilité de l'avocat se prescrit par cinq ans à compter de la fin de sa mission, C. civ., art. 2225, à lire), lettre de fin de mission.

## 3. Garde-fous

- Contrôle de destination (`docs/CONSEIL.md`, section 5).
- Aucune réponse à une autorité, aucune communication de pièce, aucun envoi sans décision du client.
- Aucune donnée du client dans une requête publique.
