# legal-agent-harness

**Le contentieux français dans Claude Code, avec la rigueur d'un cabinet.**

`contentieux` est un plugin pour [Claude Code](https://docs.claude.com/en/docs/claude-code). Il tient le dossier d'une affaire d'une session à l'autre, connaît la mécanique de trente exercices, des référés à la cassation, et contrôle chaque acte avant qu'il parte. Claude travaille alors comme un collaborateur exigeant. Il lit ses sources à la date utile, raisonne au siège du juge et vous remet des projets que vous relisez et signez.

## Une séance de travail

Vous ouvrez un dossier et y déposez les pièces. Le harness les inventorie, en tire la chronologie et calcule les échéances.

Vous demandez si le juge des référés suspendra la décision. Dès que l'agent lit le dossier, un hook reconnaît l'exercice et place devant lui ce qui en décide. Il y trouve la condition qui fait échouer la demande, ce qui la remplit, ce qui la fait tomber et les présomptions applicables, avec leurs sources. La réponse commence par l'issue la plus probable, puis en donne les raisons et ce que l'adversaire peut y opposer.

Vous demandez la requête. Des sous-agents la relisent comme le feraient le rapporteur, le juge, l'avocat adverse et un lecteur profane. Le contrôle avant dépôt la bloque tant que la compétence, le délai, les sources citées et ces relectures ne passent pas. Rien n'est déposé ni envoyé sans votre accord exprès.

## Ce que le plugin apporte

- **Trente exercices** couverts, des référés administratifs et civils à la cassation, en passant par l'annulation, l'indemnitaire, l'appel, la QPC, la CEDH et les prud'hommes. Chaque fiche est établie sur les textes et la jurisprudence lus à la source.
- **Dix-sept sous-agents**, parmi lesquels un juge et un rapporteur simulés, un contradicteur, l'avocat adverse, un vérificateur de sources et un négociateur.
- **Des hooks** qui verrouillent les pièces originales, enregistrent chaque source lue, empêchent qu'une donnée du client parte dans une recherche publique et relisent la fin de chaque réponse.
- **Dix pôles de conseil** (contrats, sociétés, social, données personnelles, IA, propriété intellectuelle, conformité, précontentieux, formation, accès au droit), adaptés au droit français à partir de [Claude for Legal](https://github.com/anthropics/claude-for-legal).
- **La recherche juridique** par [LibreJustice](https://librejustice.fr) pour la jurisprudence et les textes à une date donnée, par HAL et les bases ouvertes pour la doctrine.
- **La pseudonymisation des dossiers**, pour faire travailler le modèle sans lui transmettre l'identité des personnes.

## Des résultats mesurés sur de vraies décisions

Le banc de validation soumet au harness des décisions de justice réelles et publiques. Chacune est coupée avant le raisonnement du juge et datée de la veille, l'agent ne peut rien lire de postérieur, et seule sa réponse finale est notée. Les échantillons comptent autant de demandes accueillies que rejetées.

Sur 260 décisions qui n'ont servi à écrire aucune règle (référés administratifs, référé-provision, annulation), le harness retrouve l'issue réelle dans 81,2 % des cas. La version d'où partaient les derniers travaux en était à 68,5 %. Une partie de l'écart tient aux ordonnances de tri, dont l'issue se lit dans les visas une fois l'ordonnance rendue. Sans elles, le taux passe de 66 % à 76 %.

Chaque défaut corrigé entre dans un registre rejoué avant toute nouvelle version, et le dépôt compte plus de trois cents tests. La méthode, le détail des mesures et les échecs qui restent sont dans [INGENIERIE.md](plugins/contentieux/docs/INGENIERIE.md) et [METHODE.md](plugins/contentieux/docs/METHODE.md).

## Pseudonymisation

Activée sur un dossier, elle remplace dans les copies de travail chaque personne, adresse, numéro et société par un jeton (`[PERSONNE_3]`, `[IBAN_2]`). La table de correspondance reste chiffrée sur le poste, hors de portée de l'agent, et seul l'avocat ré-identifie les actes avant de les envoyer. Les hooks interdisent à l'agent de lire un original ou une copie que l'avocat n'a pas validée.

Sur trois jeux de pièces écrits à l'aveugle, avec des noms de toutes origines, des surnoms, des adresses en plusieurs morceaux et des numéros de toute sorte, l'outil retrouve seul environ 80 % des données quand l'avocat a déclaré les parties, et près de 90 % après la relecture des mots qu'il signale. Aucune référence juridique n'en sort altérée. Les surnoms et les noms homonymes d'un mot courant restent les cas difficiles. C'est pourquoi chaque import passe par la relecture de l'avocat, et une couche de repérage par un modèle local peut s'y ajouter.

Le détail et les commandes sont dans [PSEUDONYMISATION.md](plugins/contentieux/docs/PSEUDONYMISATION.md).

## Installer

```
git clone https://github.com/Imtoocompedidiv/legal-agent-harness.git
claude plugin marketplace add ./legal-agent-harness
claude plugin install contentieux@legal-agent-harness --scope user
```

Pour l'essayer sans l'installer, lancez Claude Code avec le dossier du plugin.

```
claude --plugin-dir ./legal-agent-harness/plugins/contentieux
```

Il faut Python 3.12 ou plus récent. Le paquet `cryptography` sert à la pseudonymisation, `pypdf` ou PyMuPDF à la lecture des PDF. Les hooks restent inactifs hors d'un dossier d'affaire.

## Ouvrir un dossier

```
python plugins/contentieux/scripts/affaire.py init "D:\Affaires\2026-14" --intitule "Recours contre une suspension" --client "..." --adversaire "..." --objectif "..."
cd "D:\Affaires\2026-14"
claude
```

Le dossier d'affaire vit hors du dépôt et hors du répertoire du plugin.

## Avant de s'en servir pour un client

Les actes sont des projets qu'un avocat relit et signe. Sans pseudonymisation, le contenu des pièces part chez le fournisseur du modèle, et [SECURITY.md](SECURITY.md) dit comment s'en prémunir. Le harness n'établit aucun profil de magistrat (CJA, art. L. 10), et les noms des magistrats sont occultés dans les décisions du banc.

## Licence

Apache 2.0, voir `LICENSE` et `NOTICE`. Les méthodes des pôles de conseil sont adaptées de Claude for Legal, publiée sous la même licence, et les modifications sont décrites dans `plugins/contentieux/docs/conseil/NOTICE.md`.

## In English

`contentieux` is a Claude Code plugin for French litigation. It keeps a persistent case file, knows the mechanics of thirty procedures from interim relief to the supreme courts, puts what decides each procedure in front of the agent as soon as it reads the file, and blocks a filing until jurisdiction, deadlines, cited sources and independent reviews pass. On 260 unseen public court decisions, it predicts the actual outcome in 81 % of cases. An optional mode pseudonymises case files so that the model never sees who the parties are.
