# Intégration du bloc d'analyse documentaire

Module livré sans toucher aux fichiers partagés : `scripts/pieces.py`, `skills/analyse-documentaire/SKILL.md`, `agents/analyste-documentaire.md`, `references/schemas/analyse_piece.v1.schema.json`, `references/schemas/matrice.v2.schema.json`, `tests/test_documentaire.py`, le gabarit `templates/affaire/preuves/matrice.json` passé au format 2 et `templates/affaire/pieces/analyses/.gitkeep`. Ce document donne le correctif à appliquer aux fichiers que d'autres modules touchent aussi.

## Application

Le correctif complet est dans `integration/documentaire.patch` (diff unifié, chemins relatifs à la racine du plugin). Depuis `plugins/contentieux` :

```
patch -p1 --binary --dry-run < integration/documentaire.patch
patch -p1 --binary < integration/documentaire.patch
python -m pytest -q plugins/contentieux/tests      (depuis la racine du dépôt)
```

`--binary` garde les fins de ligne CRLF de `gate.py`, `hook.py`, `lib_affaire.py` et `affaire.py`. Le 18 novembre 2026 à 17 h 11, le correctif s'appliquait sans décalage au plugin courant (`--dry-run`), et la suite complète passait sur une copie corrigée : 56 tests, dont `test_gate_integre` et `test_hook_valide_les_fiches`, qui restent ignorés tant que le correctif n'est pas appliqué et deviennent actifs ensuite. Si un autre module a modifié entre-temps les mêmes lignes, appliquer à la main les changements décrits ci-dessous ; chaque emplacement est donné par la ligne qui le précède.

## 1. `scripts/gate.py` : le contrôle documentaire

Dans `controler`, juste après le bloc « Pièces décisives de la matrice probatoire laissées hors du texte » (constat `PIECE_DECISIVE_OMISE`) et avant « Objections dirimantes encore ouvertes pour cet acte » :

```python
    # Analyse documentaire : un fait que l'écriture présente comme décisif renvoie, dans la matrice, à un extrait
    # littéral d'une pièce analysée ; une pièce citée sans fiche d'analyse donne une alerte (skill analyse-documentaire).
    import pieces as PIECES
    constats.extend(PIECES.controle_documentaire(racine, ecriture, fiche, texte))
```

`controle_documentaire(racine, ecriture, fiche_acte, texte)` renvoie des constats au format de `gate.py` (`code`, `gravite`, `message`, et `fait` ou `cote`). Il vaut pour tout acte qui a une fiche, courrier précontentieux compris. Il n'importe pas PyMuPDF : il lit les extractions écrites par `pieces.py inventaire`.

Codes de constat :

| Code | Gravité | Cause |
| --- | --- | --- |
| `FAIT_DECISIF_NON_RATTACHE` | BLOQUANT | la fiche nomme un `fait_decisif` sans `faits_decisifs` (identifiants de la matrice) ; le message propose les entrées proches |
| `FAIT_DECISIF_HORS_MATRICE` | BLOQUANT | un identifiant de `faits_decisifs`, ou le champ `matrice` d'un fait de condition ou de moyen, n'existe pas dans `preuves/matrice.json` |
| `FAIT_DECISIF_SANS_EXTRAIT` | BLOQUANT | aucun extrait de la matrice n'est conforme : pièce jamais analysée, fiche périmée (autre empreinte), extrait absent de la fiche, citation ou page différentes de la fiche, extrait non retrouvé sur sa page ; ou fait dit corroboré sur une seule pièce, ou état absent |
| `FAIT_DECISIF_ALLEGUE` | BLOQUANT | le fait n'est qu'allégué selon la matrice |
| `FAIT_DECISIF_CONTREDIT` | BLOQUANT | une pièce analysée le contredit (`contre_extraits`) |
| `FAIT_DECISIF_CONTESTE` | ALERTE | contesté par l'adversaire : l'écriture doit répondre par pièce |
| `EXTRAIT_VISUEL_SEUL` | ALERTE | tous ses extraits sont lus sur image, sans vérification par le texte |
| `PIECE_DECISIVE_ANOMALIE` | ALERTE | une pièce qui le prouve porte une anomalie majeure dans sa fiche |
| `FAIT_DECISIF_PIECE_NON_CITEE` | ALERTE | aucune des pièces qui le prouvent n'est citée dans l'écriture |
| `FAIT_HORS_MATRICE` | ALERTE | des faits de conditions ou de moyens n'ont pas de champ `matrice` (un seul constat, avec le nombre) |
| `PIECE_CITEE_NON_ANALYSEE` | ALERTE | pièce citée sans `pieces/analyses/<cote>.json` |
| `PIECE_CITEE_ANALYSE_PERIMEE` | ALERTE | pièce citée dont la fiche porte sur une autre empreinte |
| `ANALYSE_INVALIDE` | ALERTE | pièce citée dont la fiche a des défauts (`pieces.py verifier`) |

Faits décisifs pour une écriture : les identifiants de `faits_decisifs` de la fiche de l'acte, les entrées de la matrice marquées `decisif: true` dont `actes` contient l'acte, et les faits de conditions et de moyens qui portent le champ `matrice`.

## 2. `scripts/hook.py`

Quatre changements.

**Protection de l'inventaire et des extractions** (les citations des fiches sont vérifiées contre eux ; les écrire à la main permettrait de faire passer une citation inventée). Dans `PROTEGES`, avant l'entrée `\.gate\.json$` :

```python
    (re.compile(r"^pieces/inventaire\.json$|^pieces/texte/.+\.extraction\.txt$"), "L'inventaire et les extractions ne s'écrivent que par pieces.py inventaire : les citations des fiches d'analyse sont vérifiées contre eux. Relancer : python <plugin>/scripts/pieces.py inventaire."),
```

et dans `CHEMINS_SENSIBLES`, ajouter `pieces[\\/]+inventaire\.json|\.extraction\.txt|` après `pieces[\\/]+originaux|` ; dans `pre_tool`, l'exception des commandes destructives devient `re.search(r"affaire\.py|gate\.py|pieces\.py", cmd)`.

**Fiches réservées au sous-agent.** Dans `pre_tool`, branche `Write|Edit|...`, juste après `agent = str(ev.get("agent_type") or "")` :

```python
        if rel_l.startswith("pieces/analyses/") and not agent.endswith("analyste-documentaire"):
            refuser("Les fiches d'analyse ne s'écrivent que par le sous-agent analyste-documentaire, qui lit la pièce en entier sans le récit du client. "
                    "Le relancer sur la cote (skill analyse-documentaire) ; une fiche en erreur se refait, elle ne se corrige pas à la main.")
```

Write et Edit sont refusés tous deux : la session principale n'a aucun champ à porter dans une fiche, et les liens vers les actions de terrain vivent dans `terrain/actions.json`.

**Validation après écriture.** Dans `post_tool`, juste avant `if rel in L.SCHEMAS:`, et dans ce bloc pour la matrice :

```python
    if re.fullmatch(r"pieces/analyses/[^/]+\.json", rel):
        import pieces as PIECES
        erreurs, alertes, _ = PIECES.valider_fiche(racine, Path(rel).stem)
        if erreurs:
            sortie({"decision": "block", "reason": "Fiche d'analyse invalide, à reprendre maintenant :\n- " + "\n- ".join(erreurs[:20])})
        if alertes:
            contexte("PostToolUse", "Fiche d'analyse écrite, avec des alertes :\n- " + "\n- ".join(alertes[:10]))
        sys.exit(0)
    if rel in L.SCHEMAS:
        erreurs = L.valider_fichier(racine, rel)
        if rel == "preuves/matrice.json" and not erreurs:
            import pieces as PIECES
            erreurs, problemes, alertes = PIECES.valider_matrice(racine)
            if not erreurs and (problemes or alertes):
                contexte("PostToolUse", "Matrice des preuves enregistrée ; faits encore sans preuve conforme :\n- " + "\n- ".join((problemes + alertes)[:15]))
        if erreurs:
```

La structure de la matrice (format 2) bloque ; un fait encore sans preuve conforme n'est qu'une information, parce que la matrice se construit pas à pas et que le blocage porte sur l'écriture, au contrôle avant dépôt.

## 3. `scripts/lib_affaire.py`

Dans `VALEURS`, après l'entrée `("preuves/matrice.json", "force")` :

```python
    ("preuves/matrice.json", "force_probante"): {"prouve", "corrobore", "allegue", "conteste", "contredit"},
```

`SCHEMAS` ne change pas : le format 2 garde les champs exigés du format 1 (`id`, `fait`, `charge`, `pieces`, `force`). `force` y devient le poids de la source pour le juge ; `force_probante` dit l'état de la preuve. Une matrice au format 1 reste valide, mais aucun de ses faits ne peut porter une écriture comme décisif : `FAIT_DECISIF_SANS_EXTRAIT`.

## 4. `scripts/affaire.py`

Dans `cmd_verifier`, après la boucle sur `L.SCHEMAS` :

```python
    import pieces as PIECES
    ctx = PIECES.Contexte(r)
    for cote in ctx.bordereau:
        if ctx.fiche(cote) is not None:
            for e in ctx.validation(cote)[0]:
                print(e)
                total += 1
    for e in PIECES.valider_matrice(r, ctx)[0]:
        print(e)
        total += 1
```

## 5. `skills/controle-avant-depot/SKILL.md`

Section 1, après la puce `fait_decisif`, une puce `faits_decisifs` ; et une section « 1 ter. Preuve documentaire » avant « 2. Registres », qui énonce les blocages et les alertes ci-dessus et la commande `pieces.py controle <brouillon>`. Texte exact dans le correctif.

## 6. Documentation et gabarit (texte exact dans le correctif)

- `skills/prise-en-main-affaire/SKILL.md`, passes 1, 2 et 6 : chaque pièce passe par le skill `analyse-documentaire` ; la chronologie se bâtit depuis les dates des fiches (`pieces.py chronologie`), jamais du seul récit du client ; la matrice est au format 2, et `pieces.py manques` alimente `terrain/actions.json`.
- `README.md` : skill et sous-agent ajoutés aux listes, puce `scripts/pieces.py` dans les outils.
- `templates/affaire/LISEZMOI.md` : lignes `pieces/inventaire.json`, extractions, `pieces/rendus/`, `pieces/analyses/`, `pieces/manques.json`, `chronologie/depuis_pieces.json`, matrice au format 2, et les commandes `D` (`pieces.py`).

## 7. `tests/test_contentieux.py`

Une fois `gate.py` corrigé, `TestGate.test_refere_conforme_puis_finalisation` ne passe plus : sa fiche nomme un `fait_decisif` sans rattachement, ce que le contrôle bloque désormais (`FAIT_DECISIF_NON_RATTACHE`). Le correctif ajoute une fonction `preuve_documentaire(r, cote, texte, citation, fid, fait)` qui fabrique une pièce texte réelle, l'inventorie, écrit sa fiche et l'entrée `F1` de la matrice ; la fiche de l'acte reçoit `"faits_decisifs": ["F1"]` ; le premier contrôle attend en plus `FAIT_DECISIF_HORS_MATRICE` ; la preuve est posée avant que la théorie, la séquence et la ligne soient datées. La fiche d'analyse est antidatée de deux minutes par `os.utime` : `controles_campagne.dernier_apport` compte une fiche d'analyse comme un apport au dossier, et la théorie du test est datée à la minute.

## Interactions avec les autres modules

- `controles_campagne.py` (théorie et séquence) tient déjà une fiche d'analyse pour un apport au dossier : une analyse nouvelle rend la théorie et la séquence périmées tant qu'elles ne sont pas redatées. C'est voulu : une pièce relue peut changer la théorie.
- Le juge simulé lit `pieces/texte/` (un fichier par pièce, préfixé par la cote) : les extractions `*.extraction.txt` y sont, avec un en-tête qui rappelle qu'elles ne valent pas lecture visuelle.
- Le hook Stop compte comme ouverte une pièce dont l'extraction a été lue (préfixe de cote).
- Le sous-agent `analyste-documentaire` démarre sans la constitution du dossier (`omitClaudeMd`) et ne lit ni la stratégie, ni les écritures, ni la chronologie, ni la matrice.
