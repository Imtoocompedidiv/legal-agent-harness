# Dossier d'affaire

Arborescence fixe. Chaque répertoire a un rôle unique ; rien ne se range ailleurs.

| Répertoire | Contenu | Qui écrit |
| --- | --- | --- |
| `etat/` | identité de l'affaire, échéances, objections, registre des sources, canaux de notification, consignes, passation | Claude, contrôlé par les hooks |
| `pieces/originaux/` | pièces cotées, immuables, avec empreinte | `affaire.py piece ajouter` seulement |
| `pieces/texte/` | transcriptions des pièces ; extractions page par page `*.extraction.txt` | Claude ; extractions par `pieces.py inventaire` seulement |
| `pieces/inventaire.json` | empreinte, format, pages, métadonnées, formulaires, signatures, repérages, indices de chaque pièce | `pieces.py inventaire` seulement |
| `pieces/rendus/` | pages rendues en image, versions antérieures des PDF | `pieces.py rendre`, `pieces.py inventaire` |
| `pieces/analyses/<cote>.json` | fiche d'analyse de chaque pièce, extraits littéraux et leur page | `analyste-documentaire` seulement |
| `pieces/manques.json` | pièces citées hors bordereau, pièces non analysées, faits sans pièce, documents absents | `pieces.py manques` |
| `pieces/bordereau.json` | cote, fichier, empreinte, date, description | `affaire.py` |
| `chronologie/chronologie.json` | faits datés, pièces, statut prouvé, allégué ou contesté | Claude |
| `chronologie/depuis_pieces.json` | dates lues dans les fiches d'analyse, avec pièce et extrait | `pieces.py chronologie` |
| `preuves/matrice.json` | faits à prouver (format 2), charge, pièces, extraits littéraux, état de la preuve, poids, lacune, action de terrain | Claude |
| `procedure/cartographie.md` | instances, voies, recevabilité, délais, ce qui ferme chaque voie | Claude |
| `recherche/notes/` | notes de recherche par question, sources lues | Claude, `chercheur-juridique` |
| `recherche/lectures/` | registre des lectures : chaque appel LibreJustice et read_document, avec son entrée, son heure et sa réponse brute ; empreintes dans `registre.jsonl` ; écriture à la main refusée | hook PostToolUse (`lectures.py`) |
| `recherche/fiches/` | fiches de lecture des normes et décisions décisives, extraits vérifiés dans le registre | `lecteur-de-texte` |
| `strategie/journal_strategique.md` | décisions de ligne et leurs raisons | Claude |
| `strategie/ligne.json` | ligne en vigueur, exigée par le contrôle avant dépôt | Claude |
| `strategie/negociation.json` | plan de négociation et de persuasion : intérêts, solutions de repli, voies amiables et délais, offre, contreparties, interlocuteurs, calendrier, conditions de forme, persuasion de chaque décideur ; exigé par le contrôle avant dépôt | `negociateur`, `negociation.py` |
| `strategie/positions.json` | recommandations données au client : position, date, fondement, ce qui la ferait changer, révisions avec l'élément nouveau nommé, désaccords examinés, instructions contraires du client | Claude, `positions.py` |
| `terrain/audit.json` | audit du réel daté, exigé par le contrôle avant dépôt | Claude, `stratege-terrain` |
| `adverse/declarations.json` | déclarations de l'adversaire avec leur contexte, contradictions, silences | `analyste-adverse` |
| `procedure/profil_<code>.md` | pratique publiée de la juridiction et exemples de tri | `juridiction.py` |
| `procedure/calibrage_<code>.md` | calibrage équilibré du juge simulé : refus et accueils, taux publiés, borné avant le dépôt | `juridiction.py calibrage` |
| `procedure/conditions_<type>.md` | conditions du régime remises au rapporteur simulé | `juridiction.py conditions` |
| `terrain/actions.json` | actions sur le réel proposées, validées, faites | Claude, `stratege-terrain` |
| `ecritures/brouillons/` | versions de travail des actes | Claude, `plume` |
| `ecritures/controle/` | fiche de l'acte, lecture à froid, contradiction, verdict | sous-agents et `gate.py` |
| `ecritures/FINAL/` | versions finales contrôlées | `affaire.py finaliser` seulement |
| `journal/journal.md` | journal horodaté | `affaire.py journal` seulement |

## Commandes

`P` désigne `python "<racine du plugin>/scripts/affaire.py"`, `D` désigne `python "<racine du plugin>/scripts/pieces.py"` et `R` désigne `python "<racine du plugin>/scripts/positions.py"`, lancés depuis ce dossier.

```
P etat
R squelette
R valider
P journal "texte" --type fait|acte|strategie|decision_client|note
P piece ajouter <fichier> --cote 12 --date 2026-10-09 --description "Lettre de mise en demeure"
P piece verifier
D inventaire
D rendre --a-examiner
D verifier
D chronologie
D manques
D controle ecritures/brouillons/refere_v3.md
P echeance ajouter --objet "Dépôt du référé" --date 2026-11-19T15:00 --regle "..." --depart "..." --source "..."
P canal controle courrier --resultat "deux avis de passage retirés"
P objection ajouter --acte refere_v3 --enonce "..." --gravite dirimante --auteur contradicteur
P objection clore O004 --statut traitee --resolution "..." --ou "§ 7"
P verifier
P controle ecritures/brouillons/refere_v3.md
P finaliser ecritures/brouillons/refere_v3.md
P depot ecritures/FINAL/refere_v3__ab12cd34ef.md --accord "mots exacts du client" --canal Télérecours
```

## Verrous actifs

- Au démarrage, à la reprise et après compaction : briefing d'état injecté (objectif, instances, échéances, canaux non contrôlés, objections dirimantes, consignes, passation, journal).
- À chaque message : échéances à moins de 72 heures, canaux en retard, objections dirimantes ; quand le client conteste une recommandation, propose un levier ou demande un écrit à l'adversaire, la règle qui s'applique et les positions en vigueur.
- Écriture refusée sur les pièces originales, le journal, la constitution (`AGENTS.md`, importé par `CLAUDE.md`), `ecritures/FINAL/` et les verdicts `*.gate.json`.
- Après chaque modification d'une écriture : lecture mécanique et liste des défauts bloquants au dépôt.
- Après chaque modification d'un fichier d'état : validation de structure, correction exigée.
- Fin de session refusée tant que la passation n'est pas réécrite si le dossier a changé.
- Finalisation impossible sans contrôle PASS sur l'empreinte exacte du texte.
