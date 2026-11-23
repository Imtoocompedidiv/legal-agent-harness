---
name: profil-et-positions
description: "Profil du cabinet ou de l'entreprise et positions de négociation par pôle : entretien d'ouverture, réglage, registres et échéancier. À la première mission de conseil, quand le client veut régler ses positions, ou quand une position manque."
---

# Profil et positions

Le conseil applique au dossier les positions du client : ce qu'il accepte, ce qu'il négocie, ce qu'il refuse, qui signe et qui valide. Ce skill les recueille, les enregistre et les tient à jour. Il remplace l'entretien d'ouverture et le réglage des treize plugins de la suite d'origine, avec un seul profil commun et une fiche de positions par pôle.

## 1. Où vivent le profil, les positions et les registres

- Base : `cabinet/` à la racine du dossier de travail quand il existe ; sinon la variable HARNESS_JURIDIQUE_CONFIG ; sinon `~/.harness-juridique/`. Un dossier d'affaire peut ainsi porter ses propres positions, qui l'emportent sur celles du cabinet.
- `profil.md` : qui est le client, qui écrit, où il opère, quelles autorités le contrôlent, son appétit au risque, ses signataires et circuits de validation, ses outils.
- `positions/<pôle>.md` : les positions du pôle, au format de `skills/<pôle>/references/positions.md`.
- `registres/<nom>.json` : contrats, sociétés, pi, social, procédures, et le journal des écarts signés `ecarts.json`. Structure : `python "${CLAUDE_PLUGIN_ROOT}/scripts/echeancier.py" squelette <registre>`.
- `veille/` : les rapports du sous-agent `veilleur`.

## 2. Le travail n'attend pas le profil

Une mission de conseil se fait sans profil complet. Quand une position manque, appliquer la position par défaut de la fiche de mission, l'annoncer dans le livrable avec son fondement, et proposer en fin de livrable de l'enregistrer. L'entretien complet se propose à la première mission de conseil, une fois, et se fait quand le client le veut.

## 3. L'entretien

Lire `references/entretien.md`. L'entretien commun dure quelques questions ; les modules de pôle se posent seulement pour les pôles que le client emploie, à partir de `skills/<pôle>/references/positions.md`. Une question à la fois quand le client répond de vive voix ; un questionnaire écrit d'un bloc quand il préfère remplir. Chaque réponse s'écrit aussitôt dans le fichier, avec sa date. Quand une réponse du client contredit une règle d'ordre public, le dire, citer la règle lue à la source, et enregistrer la position dans sa forme licite.

## 4. Le réglage

À la demande du client, ou quand le veilleur signale une dérive : relire la position, montrer les écarts signés qui la contredisent (`registres/ecarts.json`), proposer la révision, l'enregistrer seulement sur décision du client, avec la date et la raison.

## 5. Le journal des écarts

Chaque fois qu'un contrat est signé avec une clause qui s'écarte d'une position, l'inscrire dans `registres/ecarts.json` : date, contrat, clause, position, écart accepté, contrepartie obtenue, qui l'a accepté. Ce journal remplace le retour sur les écarts et le suivi de la dérive de la suite d'origine ; le veilleur le relit.

## 6. Garde-fous

- Le profil et les positions sont des données du client : ils ne sortent jamais dans une requête publique.
- Le profil dit le statut de celui qui écrit, parce qu'il change la protection des livrables (`docs/CONSEIL.md`, section 5) : avocat, juriste d'entreprise (et, à compter du 1er janvier 2027, s'il remplit les conditions de l'article 58-1 de la loi n° 71-1130), particulier pour lui-même, clinique juridique.
- Aucune tâche programmée ne se crée sans décision du client ; le skill dit comment programmer la veille (planificateur de tâches du poste ou tâches programmées de Claude), le client décide.
