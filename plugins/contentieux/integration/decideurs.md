# Intégration du module « lecture des décideurs »

Module livré sans toucher aux fichiers partagés : `skills/lecture-des-decideurs/SKILL.md` et ses trois références (`psychologie-decision.md`, `sociologie-juridictions.md`, `institutions-adverses.md`), `agents/sociologue-institution.md`, `scripts/decideurs.py`, `references/schemas/decideurs.v1.schema.json`, `tests/test_decideurs.py`, l'épreuve `docs/epreuves/decideurs.md` et ses deux annexes. Ce document donne le correctif à appliquer aux fichiers que d'autres modules touchent aussi.

## Application

Le correctif des fichiers de code et de la consigne du contrôle est dans `integration/decideurs.patch` (diff unifié, chemins relatifs à la racine du plugin). Depuis `plugins/contentieux` :

```
patch -p1 --binary --dry-run < integration/decideurs.patch
patch -p1 --binary < integration/decideurs.patch
python -m pytest -q plugins/contentieux/tests      (depuis la racine du dépôt)
```

Le 18 novembre 2026 vers 18 h, le correctif s'appliquait sans décalage au plugin courant (`--dry-run`), et la suite complète passait sur une copie corrigée : 108 tests réussis, 1 ignoré (celui qui l'était déjà). Sans le correctif, `test_decideurs.py` passe seul et ne dépend d'aucun fichier partagé. Si un autre module a modifié entre-temps les mêmes lignes, appliquer à la main les changements décrits ci-dessous ; chaque emplacement est donné par la ligne qui le précède. Les consignes des agents `juge-simule` et `architecte-strategique`, refondues par d'autres modules, ne sont pas dans le diff : leurs ajouts sont donnés en texte (sections 5 et 6).

## 1. `scripts/gate.py` : le blocage

Dans `controler`, juste après le bloc « La campagne » (ligne `CAMPAGNE.controler_sequence(racine, ecriture, fiche, c)`) :

```python
    # Les décideurs : profil de la juridiction qui recevra l'acte et de l'institution adverse, et lecture à froid rendue
    # sur ce profil (skill lecture-des-decideurs ; structure et règles dans decideurs.py).
    if juridictionnel:
        import decideurs as DECIDEURS
        DECIDEURS.controler(racine, ecriture, fiche, c)
```

`decideurs.controler(racine, ecriture, fiche, c)` appelle `c(code, gravite, message)` au format de `gate.py`. Il vaut pour tout acte juridictionnel, pas pour le courrier précontentieux. La fiche de l'acte peut porter `decideur` (identifiant D<n> du profil) ; à défaut, le décideur est celui dont `actes` couvre l'acte, sinon la première juridiction du profil.

Codes de constat :

| Code | Gravité | Cause |
| --- | --- | --- |
| `DECIDEURS_ABSENT` | BLOQUANT | `strategie/decideurs.json` absent |
| `DECIDEURS_INVALIDE` | BLOQUANT | JSON illisible ou structure contraire au schéma (champ manquant, valeur hors liste, date illisible) |
| `DECIDEURS_PERIME` | BLOQUANT | profil de plus de 180 jours |
| `DECIDEURS_HORS_ACTE` | BLOQUANT | `actes_couverts` ne couvre pas l'acte |
| `DECIDEURS_SANS_JURIDICTION` | BLOQUANT | aucun décideur juridictionnel, ou décideur de la fiche introuvable ou non juridictionnel |
| `LIGNE_ANTERIEURE_AU_PROFIL` | BLOQUANT | `strategie/ligne.json` antérieure au profil sans `profil_decideurs_applique` égal à sa date |
| `LECTURE_FROID_SANS_PROFIL` | BLOQUANT | la lecture à froid existe mais `profil_decideur_sha256` ne correspond pas à la fiche actuelle du décideur |
| `CALIBRAGE_DESEQUILIBRE` | BLOQUANT pour la juridiction de l'acte, ALERTE sinon | ce qui passe ou ce qui échoue devant elle est vide |
| `TAUX_DE_BASE_ABSENT` | BLOQUANT pour la juridiction de l'acte, ALERTE sinon | ni taux de base, ni explication dans `taux_de_base_absent` |
| `SOURCE_INCONNUE` | BLOQUANT | un constat renvoie à une source absente du registre du profil |
| `SOURCE_NON_LUE` | BLOQUANT | aucune des sources d'un constat n'est lue en entier ou par extraits |
| `DECIDEUR_SANS_SOURCE_PUBLIQUE` | BLOQUANT | le profil d'une juridiction ne repose sur aucune source publique lue |
| `TAUX_INCOHERENT` | BLOQUANT | numérateur supérieur au dénominateur |
| `MAGISTRAT_NOMME` | BLOQUANT | nom ou champ nominatif d'un magistrat dans le profil d'une juridiction ou dans un levier ou risque qui la vise (CJA, art. L. 10 ; COJ, art. L. 111-13) |
| `PROBABILITE` | BLOQUANT | champ ou phrase qui chiffre la chance du dossier |
| `CIBLE_INCONNUE` | BLOQUANT | levier ou risque dont la cible n'est ni un décideur du profil ni « adversaire » |
| `APPUI_INCONNU` | BLOQUANT | choix appuyé sur un levier ou un risque inexistant |
| `ID_DOUBLE` | BLOQUANT | identifiant déclaré deux fois |
| `QUI_DECIDE_ABSENT`, `CONTRAINTES_ABSENTES`, `CONCESSIONS_ABSENTES`, `ADVERSAIRE_INCOMPLET` | BLOQUANT | institution adverse sans décideur, sans contraintes, sans ce qu'elle peut accorder, ou sans défense, culture juridique et aversion au précédent |
| `PROFIL_PERSONNEL` | BLOQUANT | portrait psychologique ou vie privée d'une personne |
| `PERSONNE_NOMMEE` | ALERTE | agent de l'adversaire désigné par son nom plutôt que par sa fonction |
| `LEVIER_INEMPLOYE` | ALERTE | levier ou risque qui n'appuie aucun choix |

## 2. `scripts/hook.py` : validation à l'écriture et briefing

- `post_tool`, avant `if rel in L.SCHEMAS:` : à l'écriture de `strategie/decideurs.json`, `decideurs.charger(racine)` ; les bloquants renvoient `{"decision": "block"}` avec la liste (« Profil des décideurs invalide, à reprendre maintenant »), les alertes passent en contexte.
- `briefing`, après les lignes de la théorie de l'affaire : une ligne « Profil des décideurs (<date>) : <institution>, <formation> ; contrôle <niveau> ; adversaire « <désignation> » », ou « Aucun profil des décideurs (strategie/decideurs.json) : l'établir avant tout acte juridictionnel (skill lecture-des-decideurs). »

Essai sur la copie corrigée : un `decideurs.json` incomplet est bloqué à l'écriture avec la liste des champs manquants ; le briefing de démarrage signale l'absence de profil.

Rien à changer dans `lib_affaire.py` ni dans `affaire.py` : la validation passe par `decideurs.py`, et aucun gabarit n'est ajouté à `templates/affaire/` (un fichier vide créé à l'ouverture masquerait l'absence de profil).

## 3. `scripts/juridiction.py` : interdiction du profilage des magistrats et classement

- Retirer l'extraction du nom du juge désigné dans `classer`, le décompte « Par juge désigné » et la colonne « Juge » de `procedure/profil_<code>.md`. Raison : l'article L. 10 du code de justice administrative, quatrième alinéa (version en vigueur depuis le 25 mars 2019, relu sur LibreJustice), et l'article L. 111-13 du code de l'organisation judiciaire interdisent toute réutilisation des données d'identité des magistrats et des membres du greffe ayant pour objet ou pour effet d'évaluer, d'analyser, de comparer ou de prédire leurs pratiques, sous les peines de l'article 226-18 du code pénal (cinq ans et 300 000 euros). Le Conseil constitutionnel a précisé que la loi vise les « stratégies de choix de juridiction » (décision n° 2019-778 DC, § 93). Le profil existant compte les issues par juge : c'est exactement l'objet interdit.
- Dans `classer_decision`, ne plus compter comme accueil un article de dispositif qui condamne le requérant à une amende pour recours abusif (CJA, art. R. 741-12). Observé dans l'épreuve : une ordonnance de 2022 du tribunal administratif de Rennes qui rejette la requête et inflige l'amende était classée « accueil » ; avec le correctif, elle est classée « refus », et les suspensions restent des accueils.
- Hors correctif, à traiter par le module de simulation : `calibrage` ne construit pas une classe de référence. Sa requête textuelle mêle référés-suspension, référés-libertés, référés mesures utiles, autres matières et jugements au fond ; dans l'épreuve, il affichait 30 % d'accueils « en tout », quand la classe réelle (ordonnances L. 521-1 contre un refus de titre du même préfet, 2026) comptait 2 suspensions sur 26. Un filtre sur le type de document ne suffit pas : la base ouverte publie une partie des ordonnances de référé sous le type « Décision ». Proposition : séparer les décisions par procédure (article du code visé dans les conclusions), par stade et par auteur de l'acte attaqué avant de calculer un taux, et écrire la règle de classe dans la sortie.

## 4. `skills/controle-avant-depot/SKILL.md`

- § 1 bis, à la fin de la liste des préalables : le profil des décideurs (`strategie/decideurs.json`, skill `lecture-des-decideurs`), valide, de moins de 180 jours, couvrant l'acte, désignant la juridiction qui le recevra avec un calibrage qui montre ce qui passe et ce qui échoue devant elle, et antérieur à la ligne ou inscrit dans `profil_decideurs_applique`.
- § 3, dans la liste de ce qu'on donne au juge simulé : la fiche produite par `decideurs.py fiche-juge` (`procedure/calibrage_decideur_<id>.md`), sans nos leviers ni nos choix, dont il reporte l'empreinte dans `profil_decideur_sha256`.

## 5. Ce que doit recevoir et faire le juge simulé (`agents/juge-simule.md`, à intégrer dans sa refonte)

Le juge simulé doit juger comme la juridiction réelle, ce qui suppose trois choses qu'il ne reçoit pas aujourd'hui : le taux de base de la bonne classe, la culture de la formation, le standard de contrôle de la matière. Texte proposé, à placer avant le paragraphe « Calibrage » :

> Profil du décideur : si l'on te désigne une fiche `procedure/calibrage_decideur_<id>.md`, lis-la en entier avant l'acte. Elle donne la formation qui statue, le standard de contrôle de la matière, les taux de base de la classe de décisions la plus proche (avec leur périmètre et ce qu'ils excluent), ce qui passe et ce qui échoue devant cette formation. Écris d'abord, avant de lire l'acte, le taux de base qui s'applique et ce qu'il signifie pour l'issue ordinaire de cette classe. Lis ensuite l'acte et les pièces, et dis, condition par condition, ce qui écarte ce dossier de la classe et dans quel sens, en appliquant le standard de contrôle indiqué. Le taux est un point de départ, pas une issue par défaut : tu peux t'en écarter dans un sens ou dans l'autre, à condition de dire sur quelle pièce ou quelle règle. Recopie dans ta sortie, sous `profil_decideur_sha256`, l'empreinte inscrite en tête de la fiche, et sous `taux_de_base_retenu` la mesure que tu as prise pour point de départ. Tu ne donnes toujours aucune probabilité.

Ajouter `profil_decideur_sha256` et `taux_de_base_retenu` à la liste des champs de sortie. Cette consigne remplace, pour les stades de filtrage, la position de rejet par défaut que le cahier des charges de la seconde mise au niveau identifie comme une cause de l'erreur mesurée (deux succès sur cinq méconnus) : le rejet devient ce que donne la classe quand elle le donne, pas une posture. Les références du skill fondent ce choix (`psychologie-decision.md`, section 5 : négligence du taux de base, vue extérieure, sélection des affaires ; section 2 : un lecteur qui fixe tôt son orientation réévalue toutes les pièces à sa lumière, d'où l'ordre « taux, puis conditions »). Le juge simulé ne reçoit ni les leviers, ni les risques, ni les choix, ni le profil de l'adversaire : la fiche les exclut, pour qu'il ne statue pas avec la stratégie de l'auteur sous les yeux.

## 6. Ajouts proposés à l'architecte (`agents/architecte-strategique.md`)

L'architecte lit déjà `strategie/decideurs.json`. Ajouts proposés, dans l'examen du résultat et du décideur :

> Vérifie la classe de référence de chaque taux de base : même formation, même procédure, même matière, même type d'acte attaqué ; une classe mal construite est un point dirimant. Vérifie que chaque choix (forum, moment, structure, ton, preuve, demande) découle des leviers et risques qu'il cite, et que le premier risque du profil est traité en première page de l'acte. Un choix de forum fondé sur la personne d'un juge est un point dirimant (CJA, art. L. 10).

## 7. `skills/strategie-contentieuse/SKILL.md` et `docs/ARCHITECTURE.md`

- `strategie-contentieuse`, § 3 « Les décideurs » : ajouter en tête que le profil s'établit par le skill `lecture-des-decideurs` et s'écrit dans `strategie/decideurs.json`, que la ligne en dépend (`profil_decideurs_applique`), et que les portraits de décideurs du paragraphe sont des hypothèses générales que le profil remplace par des constats sourcés sur la juridiction réelle.
- `ARCHITECTURE.md`, section « Couche offensive », puce « Le juge réel comme étalon » : la phrase « extrait des décisions publiées le seuil de tri de la juridiction et de ses juges » décrit un traitement interdit. Proposition : « extrait des décisions publiées le seuil de tri de la juridiction et de la formation, sans aucun décompte par magistrat (CJA, art. L. 10 ; COJ, art. L. 111-13) ». Ajouter le module à la table des couches (skill `lecture-des-decideurs`, sous-agent `sociologue-institution`, `decideurs.py`), et le skill et le sous-agent aux listes du `README.md`.

## 8. Corrections déjà portées dans une référence active

`skills/strategie-contentieuse/references/decideurs.md` reprend les sections A et C de `docs/recherche/02_juge_recit_procedure.md`. Les passages que la recherche du module a trouvés inexacts y sont corrigés sur place, avec renvoi aux références du nouveau skill (liste dans le rapport du module et dans les sections « Corrections à 02 » des références). Le document de recherche 02 lui-même est laissé intact, comme trace datée.
