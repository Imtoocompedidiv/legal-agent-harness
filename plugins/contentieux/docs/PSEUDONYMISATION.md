# Pseudonymisation des dossiers

Ce mode permet à un avocat ou à un cabinet de faire travailler le harness sur un dossier sans transmettre au fournisseur du modèle
l'identité des personnes. Le modèle ne lit que des jetons (`[PERSONNE_3]`, `[ADRESSE_1]`, `[IBAN_2]`). La table qui relie chaque
jeton à la donnée réelle reste chiffrée sur le poste, hors du dossier où travaille l'agent, et seul l'avocat ré-identifie les actes.

Une pseudonymisation n'est pas une anonymisation. Les données pseudonymisées restent des données personnelles (RGPD, art. 4, 5), et
les faits eux-mêmes peuvent identifier une personne : un métier rare, une petite commune, une date. Le mode réduit le risque, il ne
dispense ni du secret professionnel ni de l'analyse de risque du cabinet, ni du choix d'un fournisseur aux garanties suffisantes.

## Parcours

```
python <plugin>/scripts/affaire.py init "D:\Affaires\Dossier 2026-14" --intitule "Recours contre une suspension" --client "Marie Durand" --adversaire "Département"
cd "D:\Affaires\Dossier 2026-14"
python <plugin>/scripts/pseudonymisation.py init
python <plugin>/scripts/pseudonymisation.py ajouter "Paul Martin" --role témoin
python <plugin>/scripts/pseudonymisation.py importer "D:\Pièces cabinet\arrete.pdf" "D:\Pièces cabinet\attestation.docx"
python <plugin>/scripts/pseudonymisation.py valider
```

1. **`init`** active le mode. Il crée le coffre (par défaut `~/.harness-juridique/pseudonymisation/<dossier>/`, ou l'emplacement
   donné par `--coffre`, par exemple un volume chiffré) et sa clé. Il remplace par des jetons le client et les adversaires dans
   `etat/affaire.json`, pseudonymise le journal et les notes existants, et déplace vers le coffre les originaux déjà rangés.
   Le coffre ne peut pas être dans le dossier : l'agent pourrait l'atteindre.
2. **`ajouter`** déclare une personne, une société ou un numéro que l'avocat connaît : témoin, enfant, numéro de dossier propre à
   l'affaire. C'est la couche la plus sûre ; déclarer les personnes connues avant l'import est la règle.
3. **`importer`** lit les originaux là où le cabinet les garde (texte, PDF à couche texte, DOCX ; un scan s'océrise d'abord), écrit
   les copies pseudonymisées dans `pieces/pseudonymisees/` et le rapport de relecture dans le coffre. Un original rangé dans le
   dossier de travail est refusé.
4. **Relecture.** L'avocat lit le rapport : chaque donnée trouvée, avec son jeton, et la liste des mots à majuscule non reconnus.
   Une donnée oubliée s'ajoute par `ajouter`, puis on relance `importer`.
5. **`valider`** atteste la relecture : elle enregistre l'empreinte de chaque copie. L'agent ne peut lire qu'une copie validée et
   inchangée depuis.
6. **`reidentifier <acte>`** produit, dans le coffre, la version de l'acte où chaque jeton redevient la donnée réelle ; l'avocat la
   relit avant tout envoi. **`verifier`** cherche toute donnée réelle dans le dossier de travail.

## Ce que garantissent les hooks

- L'agent ne peut ni lire ni parcourir le coffre, `pieces/originaux` ou une extraction brute de pièce (Read, Grep, Glob, Bash).
- Il ne peut lire une copie pseudonymisée que si l'avocat l'a validée et qu'elle n'a pas changé depuis.
- Un message de l'avocat qui contient une donnée réelle de la table est bloqué avant d'être transmis, avec le jeton à employer.
- Un fichier que l'agent écrit et qui contiendrait une donnée réelle est signalé aussitôt, pour remplacement par son jeton.
- Le contexte de session rappelle à l'agent qu'il écrit avec les jetons et ne cherche jamais à deviner une identité.

## Détection

Les couches s'additionnent, et une forme trouvée une fois est remplacée partout dans le dossier (propagation) :

1. le dictionnaire du dossier (parties et personnes déclarées, avec leurs variantes : capitales, initiales, nom seul) ;
2. les identifiants structurés, validés par leur clé quand elle existe : IBAN (modulo 97), NIR (clé), SIREN et SIRET (Luhn), carte
   bancaire (Luhn), courriel, téléphone, adresse IP, immatriculation, pseudonyme en ligne, numéros RG et Portalis, identifiants
   introduits par leur nom (passeport, titre de séjour, allocataire, matricule) ; un IBAN ou un NIR désigné comme tel est pris même
   si sa clé est fausse ;
3. les personnes reconnues par une civilité, un rôle (signataire, témoin, gérant, « je m'appelle »), un lien (épouse, fille, voisin),
   un prénom connu, un nom en capitales, une signature suivie d'une qualité, un locuteur de transcription ;
4. les sociétés introduites par leur forme ou leur rôle (SARL, SCI, cabinet, employeur) ;
5. les adresses (voie numérotée ou nommée, code postal, boîte postale, résidence, zone d'activité), les dates et lieux de naissance ;
6. un modèle de repérage, facultatif : GLiNER, si le paquet `gliner` est installé et que `HARNESS_PSEUDONYMISATION_MODELE` désigne un
   modèle local (par exemple un modèle multilingue de repérage des données personnelles) ; ses trouvailles s'ajoutent aux autres.

Restent intacts : les juridictions, les autorités publiques, les textes et leurs articles, les décisions publiées et leurs numéros,
les montants et les dates de procédure, sans lesquels aucun raisonnement juridique ne tient. Une commune seule est gardée (elle
commande la compétence) ; elle est pseudonymisée dans une adresse et comme lieu de naissance.

## Mesures

Mesuré le 23 novembre 2026, couches 1 à 5, sans modèle. Trois jeux de huit pièces chacun (`controle4` à `controle6`, 67 à 69
données) ont été écrits à l'aveugle par un agent qui n'avait accès ni au code ni aux jeux précédents, avec des noms de toutes
origines, des surnoms, des adresses en plusieurs morceaux, des commerces sans forme sociale et des numéros de toute sorte. Chaque
jeu a d'abord été mesuré tel quel, puis a servi à corriger les règles. Seule la première mesure de chaque jeu dit ce que l'outil
vaut sur des pièces qu'il n'a jamais vues.

| Jeu, première mesure | Parties non déclarées | Parties déclarées | Avec la relecture des mots signalés | Références altérées |
|---|---|---|---|---|
| `controle4`, outil du 22 novembre | 0,64 | 0,77 | 0,84 | 3 |
| `controle5`, après le premier lot de corrections | 0,81 | 0,84 | 0,90 | 0 |
| `controle6`, après le deuxième lot | 0,75 | 0,79 | 0,87 | 0 |
| `controle6`, outil du 22 novembre, pour comparaison | 0,60 | 0,66 | 0,75 | 0 |

Après le troisième lot, l'outil fait 0,88 et 0,96 sur `controle6` avec les parties déclarées, mais ce jeu a servi à le corriger.
Sur le corpus généré (400 pièces), le rappel est de 0,987 à froid et 0,992 avec les parties déclarées, sans aucune des 668
références juridiques altérée ni aucun faux remplacement. Il faut compter une quinzaine de millisecondes par pièce.

La principale cause d'échec était une classe de lettres limitée aux accents du français : « Szczepańska », « Yıldırım » ou
« Nguyễn » échappaient même après « Mme ». Ce qui manque encore relève surtout du surnom et du diminutif (« Momo », « Nono »), du
nom de famille homonyme d'un mot ou d'une ville (« Fontaine », « Paris ») et des initiales. Trois exigences en découlent. Il faut
déclarer avant l'import toutes les personnes connues du dossier, relire chaque rapport et, quand le cabinet le peut, installer la
couche modèle. Les jeux et les scripts sont dans `evaluation/pseudonymisation/`, et un cabinet devrait mesurer l'outil sur ses
propres pièces types avant de s'y fier.

## Cadre

- RGPD, art. 4, 5 (définition de la pseudonymisation) et art. 32 (sécurité du traitement) ; lignes directrices 01/2025 du Comité
  européen de la protection des données sur la pseudonymisation.
- Secret professionnel de l'avocat (loi n° 71-1130 du 31 décembre 1971, art. 66-5) : le mode limite ce qui sort du cabinet, il ne
  rend pas licite par lui-même l'usage d'un service extérieur.
- La clé du coffre ne se reconstitue pas : sans elle, la table est perdue et les actes ne se ré-identifient plus. La sauvegarder à part.
