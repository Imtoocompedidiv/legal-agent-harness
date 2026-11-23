# legal-agent-harness

Harness juridique français pour [Claude Code](https://docs.claude.com/en/docs/claude-code) : un plugin (`contentieux`) qui encadre
le modèle dans le travail d'un cabinet, du premier rendez-vous au dépôt. *A French-law harness for Claude Code: persistent case files,
deterministic pre-filing checks, adversarial reviewers, source-checked legal research, and optional pseudonymisation of case files.*

Ce n'est pas un avocat. C'est un ensemble de méthodes, de verrous et de contrôles qui obligent le modèle à travailler comme un
praticien exigeant : lire la source à la date utile, se placer au siège du juge, éprouver l'acte avant de le déposer, ne jamais
transmettre une donnée du client à un service public, ne rien envoyer sans l'accord exprès du client. Les actes restent des projets
qu'un avocat relit et signe.

## Ce qu'il fait

- **Un dossier d'affaire persistant** : pièces inventoriées, chronologie, échéances calculées, matrice des preuves, journal, état
  de passation entre sessions (`scripts/affaire.py`, `scripts/pieces.py`).
- **La mécanique de trente exercices** (référés administratifs et civils, annulation, indemnitaire, appel, cassation, recours
  préalables, QPC, CEDH, prud'hommes, plainte...) : la condition qui fait échouer chaque exercice, ce qui la remplit, ce qui la fait
  tomber, les présomptions et leur renversement, établis sur les textes et la jurisprudence lus à la source.
- **Des relecteurs indépendants** en sous-agents : juge et rapporteur simulés, contradicteur, avocat adverse, lecteur profane.
- **Un contrôle avant dépôt** (`scripts/gate.py`) qui bloque un acte tant que la fiche, les sources, la compétence, les délais et les
  relectures ne passent pas.
- **Des hooks Claude Code** qui verrouillent les pièces originales, capturent chaque lecture de source, refusent une donnée du client
  dans une requête publique, et contrôlent la fin de chaque tour (pronostic suspendu à l'adversaire, échec annoncé sans
  recommandation, mesure adverse suivante non préparée, relecture non appliquée).
- **Dix pôles de conseil** (contrats, sociétés, social, données personnelles, IA, propriété intellectuelle, conformité,
  précontentieux, formation, accès au droit), adaptés de [Claude for Legal](https://github.com/anthropics/claude-for-legal) au droit
  français.
- **Une pseudonymisation des dossiers** pour travailler sans transmettre l'identité des personnes au fournisseur du modèle
  ([docs/PSEUDONYMISATION.md](plugins/contentieux/docs/PSEUDONYMISATION.md)).

## Installer

```
git clone <url du dépôt> legal-agent-harness
claude plugin marketplace add ./legal-agent-harness
claude plugin install contentieux@legal-agent-harness --scope user
```

Pour essayer sans installer : `claude --plugin-dir ./legal-agent-harness/plugins/contentieux`. Les hooks ne font rien hors d'un
dossier d'affaire. Python 3.12 ou plus ; `cryptography` pour la pseudonymisation, `pypdf` ou PyMuPDF pour lire les PDF. La recherche
juridique s'appuie sur le serveur MCP [LibreJustice](https://librejustice.fr) ; les recherches savantes, sur HAL et les bases ouvertes.

```
python plugins/contentieux/scripts/affaire.py init "D:\Affaires\Dossier 2026-14" --intitule "..." --client "..." --adversaire "..." --objectif "..."
cd "D:\Affaires\Dossier 2026-14"
claude
```

Un dossier d'affaire ne se range jamais dans le dépôt ni dans le répertoire du plugin.

## Comment il est vérifié

Le banc de validation (`validation/banc/`) fait tourner le harness sur des sondes et note chaque réponse, par motif ou par un
correcteur qui juge au sens. Les sondes de pronostic sont des décisions réelles et publiques, coupées avant le raisonnement du
juge ; la sonde est datée de la veille de la décision, et un hook interdit à l'agent de lire quoi que ce soit de postérieur. Aucune
décision prédite par une sonde ne peut figurer dans ce que l'agent lit (`tests/test_integrite_banc.py`). Chaque défaut corrigé entre
dans un registre rejoué plusieurs fois avant toute version (`banc.py defauts`). La méthode, les mesures et ce qui échoue encore sont
dans [docs/INGENIERIE.md](plugins/contentieux/docs/INGENIERIE.md) et [docs/METHODE.md](plugins/contentieux/docs/METHODE.md).

```
python -m pytest -q plugins/contentieux/tests
python validation/banc/banc.py lister
```

## Limites

- Un pronostic n'est pas une prévision certaine ; les taux mesurés sont donnés avec leur protocole, sur un banc équilibré qui ne
  reproduit pas les taux de succès réels des juridictions.
- Le contrôle avant dépôt est mécanique : un PASS n'atteste ni la justesse juridique ni l'issue.
- Les correcteurs du banc sont des modèles, non calibrés sur un jury de praticiens.
- Le harness ne profile aucun magistrat : l'analyse des pratiques d'un juge nommé est interdite (CJA, art. L. 10 ; COJ, art.
  L. 111-13), et les noms de magistrats sont occultés des décisions du banc.
- Sans pseudonymisation, le contenu des pièces est transmis au fournisseur du modèle ; voir [SECURITY.md](SECURITY.md).

## Licence

Apache 2.0 (voir `LICENSE` et `NOTICE`). Les méthodes des pôles de conseil sont adaptées de Claude for Legal, publiée sous la même
licence ; les modifications sont décrites dans `plugins/contentieux/docs/conseil/NOTICE.md`.
