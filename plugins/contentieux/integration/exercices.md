# Intégration du module mécanique des exercices

Module livré sans toucher aux fichiers partagés : `skills/mecanique-des-exercices/SKILL.md`, ses trente fiches d'exercice (`skills/mecanique-des-exercices/references/*.md`), `scripts/exercices.py`, `tests/test_exercices.py` et vingt-deux sondes du banc (`validation/banc/sondes/EXO-*.json`). Ce document donne ce que la session principale applique aux fichiers partagés.

## 1. Règle intégrée

Avant toute écriture juridictionnelle, la fiche de l'acte porte le diagnostic de l'exercice (champ `exercice`) : quel juge décide, à quel stade, sur quoi, avec quel standard et quel office ; la condition décisive, sa preuve au bordereau ou à la matrice, ce qui la ferait tomber et la parade ; la cible ; ce qui fait gagner ; chaque exigence implicite de la fiche d'exercice, vérifiée ou dite sans objet ; au moins un voisin de la fiche écarté avec sa raison ; le régime spécial examiné. Le contrôle avant dépôt bloque l'écriture dont le diagnostic manque ou est incomplet, l'acte contrôlé sous un autre régime que celui de l'exercice, le régime spécial déclaré et non appliqué, le texte qui se présente comme l'exercice écarté, le diagnostic antérieur au dernier apport du dossier, l'exercice que la séquence attribue autrement à cette écriture, et la version que le juge simulé tient pour relevant d'un autre exercice.

Pour un courrier (`courrier_precontentieux`), les constats sont des alertes, sauf deux qui restent bloquants parce qu'ils font perdre le délai lui-même : l'envoi destiné à proroger, interrompre ou conserver un délai par un mode qui n'en prouve pas la date ou après l'échéance, et le recours administratif qui compte sur une prorogation que la matière exclut (C. urb., art. L. 600-12-2, en vigueur depuis le 28 novembre 2025, lu le 19 novembre 2026). En mode conservatoire (`conservatoire` dans la fiche), seuls restent bloquants l'exercice, le régime, le régime spécial, la cible et le délai ; le reste est différé au mémoire complémentaire, comme les autres constats que la procédure permet de régulariser.

## 2. Correctif de code : `integration/exercices.patch`

Diff unifié, chemins relatifs à la racine du plugin. Depuis `plugins/contentieux` :

```
patch -p1 --binary --dry-run < integration/exercices.patch
patch -p1 --binary < integration/exercices.patch
python -m pytest -q plugins/contentieux/tests -p no:cacheprovider      (depuis la racine du dépôt)
```

Correctif régénéré le 20 novembre 2026 contre les fichiers partagés du moment (il s'applique sans décalage). Vérification faite sur une copie fraîche du plugin courant : le correctif s'applique à blanc puis réellement, et la suite complète passe sur la copie corrigée (266 tests réussis, 7 ignorés qui appartiennent aux autres modules ; les 27 tests de `test_exercices.py` passent tous), y compris `TestIntegration` de `test_exercices.py`, ignoré tant que le correctif n'est pas appliqué. Sur le plugin non corrigé, la suite passe aussi (265 réussis, 8 ignorés, dont les deux tests d'intégration du module). Si un autre module a modifié entre-temps les mêmes lignes, appliquer à la main les trois changements ci-dessous ; chaque emplacement est donné par la ligne qui le précède.

### 2.1 `scripts/gate.py`

Juste après l'appel `NEGOCIATION.controler(racine, ecriture, fiche, c, juridictionnel=juridictionnel, texte=texte)` et avant le bloc qui le suit (les positions du module posture, déjà présentes dans `gate.py` le 20 novembre 2026, puis le récit) :

```python
    # L'exercice : sa mécanique propre diagnostiquée avant la production (juge et stade, condition décisive et sa preuve,
    # cible, exigences implicites, voisin écarté), et l'envoi qui doit protéger un délai (skill mecanique-des-exercices).
    import exercices as EXERCICES
    EXERCICES.controler(racine, ecriture, fiche, texte, c)
```

L'appel vaut pour tout acte qui a une fiche ; `exercices.controler` décide lui-même de la gravité selon le régime (courrier ou acte porté devant un juge) et selon le mode conservatoire. Il est placé avant `CAMPAGNE.appliquer_conservatoire`, qui ne diffère aucun code `EXERCICE_` : la modulation propre au module suffit.

### 2.2 `scripts/hook.py`, validation à l'enregistrement de la fiche

Dans `post_tool`, juste avant la ligne `rl = rel.lower()` :

```python
    if re.fullmatch(r"ecritures/controle/[^/]+\.fiche\.json", rel):
        import exercices as EXERCICES
        fiche = L.lire_json(racine / rel) or {}
        if isinstance(fiche, dict) and fiche.get("type_acte"):
            constats = EXERCICES.valider(fiche.get("exercice"), fiche, contexte=EXERCICES.contexte_dossier(racine))
            if constats:
                contexte("PostToolUse", "Diagnostic d'exercice de la fiche, à compléter avant le dépôt (skill mecanique-des-exercices) :\n- "
                         + "\n- ".join(f"{k['gravite']} {k['code']} : {k['message']}" for k in constats[:12]))
        sys.exit(0)
```

Le hook n'interrompt rien : il dit, dès l'enregistrement de la fiche, ce que le contrôle bloquera au dépôt.

### 2.3 `tests/test_contentieux.py`

Le référé conforme porte un diagnostic d'exercice complet. Juste après `maintenant = L.maintenant().isoformat(timespec="minutes")` dans `test_refere_conforme_puis_finalisation` :

```python
        from test_exercices import bloc_refere_suspension
        fiche["exercice"] = bloc_refere_suspension(maintenant)
        ecrire(self.r / "ecritures/controle/ref.fiche.json", fiche)
```

## 3. Codes et messages

Constats de `exercices.controler`, au format de `gate.py` (les gravités sont celles d'un acte porté devant un juge) :

| Code | Gravité | Cause |
| --- | --- | --- |
| `EXERCICE_ABSENT` | BLOQUANT | fiche de l'acte sans bloc `exercice` |
| `EXERCICE_INCONNU` | BLOQUANT | identifiant hors catalogue et sans préfixe `autre:` |
| `EXERCICE_REGIME_DISCORDANT` | BLOQUANT | `type_acte` étranger aux régimes de l'exercice |
| `EXERCICE_SANS_REGIME` | ALERTE | exercice sans régime de `gate.py` (appel administratif) |
| `EXERCICE_JUGE_STADE_INCOMPLET` | BLOQUANT | juge, stade, standard ou office non renseigné |
| `EXERCICE_DECISION_ABSENTE`, `EXERCICE_GAIN_ABSENT` | BLOQUANT | question tranchée ou ce qui fait gagner non écrits |
| `EXERCICE_CONDITION_ABSENTE`, `EXERCICE_CONDITION_HORS_EXERCICE` | BLOQUANT | condition décisive non nommée, ou étrangère à l'exercice et à la fiche |
| `EXERCICE_PREUVE_ABSENTE`, `EXERCICE_PREUVE_HORS_DOSSIER` | BLOQUANT | condition décisive sans pièce ni fait de la matrice, ou pièce et fait absents du dossier |
| `EXERCICE_SOURCE_NON_LUE` | BLOQUANT | source citée absente du registre ou non lue en entier |
| `EXERCICE_CONDITION_NON_EPROUVEE` | BLOQUANT | aucune situation qui ferait tomber la condition, ou situation sans parade |
| `EXERCICE_CONDITION_PRINCIPALE_NON_TRAITEE` | BLOQUANT | la condition qui fait le plus souvent échouer l'exercice n'est ni retenue ni établie |
| `EXERCICE_CONDITION_DECISIVE_ECARTEE` | BLOQUANT | la condition décisive est déclarée absente dans la fiche |
| `EXERCICE_CONDITION_DECISIVE_FRAGILE` | ALERTE | la condition décisive est fragile |
| `EXERCICE_CIBLE_INCOMPLETE`, `EXERCICE_CIBLE_DISCORDANTE` | BLOQUANT | cible sans nature ou désignation, décision non datée, nature étrangère à l'exercice, acte hors `actes_attaques` |
| `EXERCICE_EXIGENCE_NON_VERIFIEE` | BLOQUANT | exigence implicite de la fiche ni vérifiée avec preuve ou source, ni dite sans objet avec sa raison |
| `EXERCICE_VOISIN_NON_EXAMINE` | BLOQUANT | aucun voisin de la fiche écarté avec sa raison |
| `EXERCICE_VOISIN_INCONNU` | ALERTE | voisin hors catalogue sans préfixe `autre:` |
| `EXERCICE_REGIME_SPECIAL_NON_EXAMINE`, `EXERCICE_REGIME_SPECIAL_IGNORE` | BLOQUANT | régime spécial non examiné, ou déclaré et non appliqué au contrôle |
| `EXERCICE_DELAI_NON_PROTEGE` | BLOQUANT, même pour un courrier | envoi qui doit protéger un délai par un mode qui n'en prouve pas la date, sans date, après l'échéance, ou recours administratif à échéance sans `envoi` |
| `EXERCICE_PROROGATION_EXCLUE` | BLOQUANT, même pour un courrier | recours destiné à proroger un délai que la matière ne laisse pas proroger |
| `EXERCICE_DIAGNOSTIC_PERIME` | BLOQUANT | diagnostic sans date ou antérieur au dernier apport du dossier |
| `EXERCICE_HORS_SEQUENCE` | BLOQUANT | la voie retenue qui porte l'écriture désigne un autre exercice |
| `EXERCICE_TEXTE_DISCORDANT` | BLOQUANT | la première page se présente comme un voisin écarté et ne nomme pas l'exercice |
| `EXERCICE_TEXTE_SANS_MARQUEUR` | ALERTE | la première page ne nomme pas l'exercice ni son texte fondateur |
| `EXERCICE_JUGE_SIMULE_AUTRE_EXERCICE` | BLOQUANT | la lecture à froid de la version contrôlée porte `exercice_adapte` à faux |
| `EXERCICE_CONSERVATOIRE_A_EXAMINER` | ALERTE | requête au fond dont le délai expire dans les 72 heures, sans mode conservatoire |

Aucun de ces constats ne porte de catégorie de rejet : ils ne changent pas la mesure du protocole de validation.

## 4. Texte à ajouter à la fiche de l'acte

**`skills/controle-avant-depot/SKILL.md`, section 1**, après la puce `urgence_amiable` :

> - `exercice` : le diagnostic de l'exercice fait avant la production (skill `mecanique-des-exercices`, `exercices.py squelette <identifiant>`) : `exercice` (identifiant de la fiche d'exercice, ou `autre:<libellé>`), `date`, `juge_et_stade` (`juge`, `stade`, `standard`, `office`), `ce_qu_il_decide`, `condition_decisive` (`condition`, `pourquoi_decisive`, `preuve` avec `pieces`, `faits` et `sources`, `ce_qui_la_ferait_tomber` avec pour chaque situation sa `parade`), `condition_principale` quand la condition décisive retenue n'est pas celle que la fiche désigne, `cible` (`nature`, `designation`, `acte`, `date`), `ce_qui_fait_gagner`, `exigences_implicites` (une entrée par exigence de la fiche, vérifiée avec sa preuve ou sa source, ou sans objet avec sa raison), `voisins_ecartes` (`exercice`, `raison`), `regime_special` (`applicable`, `texte`, `type_acte`, `proroge_par_recours_administratif`) et, pour un acte qui doit protéger un délai, `envoi` (`mode`, `date_prevue`, `but`). Sans diagnostic complet, le contrôle bloque l'écriture juridictionnelle ; pour un courrier, il bloque l'envoi qui ne prouve pas sa date ou qui compte sur une prorogation exclue.

**Même fichier, section 1 bis**, à la fin de la phrase qui énumère les préalables, avant le point :

> ; le diagnostic de l'exercice dans la fiche de l'acte (`exercice`, skill `mecanique-des-exercices`), complet, postérieur au dernier apport du dossier et conforme à l'exercice de la voie retenue dans la séquence

## 5. Ajouts proposés aux skills et aux agents

À ajouter mot pour mot, par remplacement de passage : ces fichiers bougent sous d'autres modules.

### 5.1 `skills/conduite-de-la-sequence/SKILL.md`

**Section 3, liste « Pour chaque voie, indiquer »**, après la puce `- la cible et le décideur ;` :

> - l'exercice au sens du skill `mecanique-des-exercices` (identifiant de sa fiche), sa condition décisive, la preuve qui l'établit, ce qui la ferait tomber dans ce dossier et le voisin écarté ;

**Section 5, puce « Conserver d'abord »**, à la fin :

> Le mode d'envoi et la matière se vérifient sur la fiche `mecanique-des-exercices/references/recours-administratifs-prealables.md` : un recours administratif posté est regardé comme formé à la date de son expédition, cachet de la poste faisant foi (CE, 30 juin 2025, n° 494573, publié au Recueil, analyse lue le 19 novembre 2026), mais il ne proroge plus le délai de recours contre une décision relative à une autorisation d'urbanisme intervenue après le 28 novembre 2025 (C. urb., art. L. 600-12-2, lu le 19 novembre 2026).

**Section 5, puce « Éprouver le coup d'urgence avant de le retenir »**, à la fin :

> Avant l'épreuve, le diagnostic de l'exercice nomme ce qui ferait tomber l'urgence dans ce dossier, en particulier l'intérêt que le juge attribuera à la mesure attaquée et la situation de fait qui ôte l'urgence (traitement maintenu, ressources suffisantes, recours suspensif qui protège déjà, effets épuisés), et la pièce qui y répond ; sans cette pièce, la voie reste en réserve.

**Section 6**, à la fin du paragraphe :

> Le refus nomme la condition de la fiche d'exercice qui fait échouer l'acte et la pièce qui le montre.

**Section « Sortie », puce `voies`**, après `type_acte (régime de gate.py s'il y en a un)` :

> , `exercice` (identifiant de `mecanique-des-exercices`)

**Même section, liste des refus**, nouvelle puce à la fin :

> - l'écriture porte un diagnostic d'exercice différent de l'exercice de sa voie.

### 5.2 `skills/ecriture-juridictionnelle/SKILL.md`

**Section 1 « Avant d'écrire »**, nouvelle première puce :

> - **L'exercice.** Le diagnostic du skill `mecanique-des-exercices` est fait et écrit dans la fiche de l'acte avant la première ligne : juge et stade, ce qu'il décide, standard et office, condition décisive et sa preuve, cible, exigences implicites, voisin écarté. La première page nomme l'exercice et son texte fondateur ; les conclusions ne demandent que ce que ce juge peut accorder à ce stade. Si le diagnostic ne tient pas, le problème est d'exercice, pas de rédaction.

**Section 7, étape 2**, remplacer « Fiche de l'acte dans `ecritures/controle/<acte>_vN.fiche.json` (skill `controle-avant-depot`). » par :

> Fiche de l'acte dans `ecritures/controle/<acte>_vN.fiche.json` (skill `controle-avant-depot`), avec le diagnostic de l'exercice (`exercice`, skill `mecanique-des-exercices`) écrit avant le brouillon.

### 5.3 `agents/architecte-strategique.md`

**Section « Matériaux »**, nouvelle puce après `- le journal.` :

> - les fiches d'exercice de `skills/mecanique-des-exercices/references/` pour chaque voie examinée et chaque acte en projet.

**Section « Examen », point 9 « L'acte en projet »**, à la fin :

> Confronte le diagnostic d'exercice de la fiche de l'acte (`exercice`) à la fiche de l'exercice : la condition qui le fait le plus souvent échouer, les situations qui la font tomber dans ce dossier, les exigences implicites, le régime spécial de la matière, les voisins. Un exercice dont la condition décisive tombe sur un fait que la défense opposera, ou dont un voisin convient mieux, est un point dirimant.

**Section « Sortie », puce `voies_comparees`**, après `famille` :

> , `exercice` (identifiant de `mecanique-des-exercices`)

### 5.4 `agents/juge-simule.md`

Le juge simulé ne lit pas les fiches d'exercice : elles citent des décisions jusqu'au 19 novembre 2026 et pourraient lui faire retrouver une affaire de validation. Il identifie lui-même l'exercice à partir de l'acte et des textes.

**Section « Le délibéré », point 1 « Première lecture »**, à la fin :

> Identifie l'exercice dont tu es saisi : le fondement invoqué, le critère légal de ton éventuel filtre, le standard, ce que tu peux ordonner à ce stade. Si l'acte relève d'un autre exercice que celui qu'il invoque, devant toi ou devant un autre juge, ou demande ce que tu ne peux pas accorder à ce stade, note-le : c'est un motif de ta décision.

**Section « Sortie »**, dans la liste des champs, après `demande_identifiee` :

> , `exercice_identifie` (le fondement et le stade tels que tu les as compris), `exercice_adapte` (vrai si l'exercice invoqué est celui qui permet d'obtenir ce que l'acte demande, faux sinon), `exercice_qui_conviendrait` (quand `exercice_adapte` est faux, l'exercice et le juge qui conviendraient, en une phrase)

Le contrôle bloque la version dont la lecture à froid porte `exercice_adapte` à faux (`EXERCICE_JUGE_SIMULE_AUTRE_EXERCICE`).

### 5.5 `README.md`

Liste des skills : ajouter `mecanique-des-exercices` après `conduite-de-la-sequence`. Outils : ajouter « `scripts/exercices.py` (liste, fiche, squelette, valider, controle) lit les trente fiches d'exercice et contrôle le diagnostic que porte la fiche de l'acte. »

## 6. Compatibilité

- Le module lit `etat/sources.json`, `pieces/bordereau.json`, `preuves/matrice.json`, `strategie/sequence.json` et la lecture à froid de l'écriture ; il réutilise `controles_campagne.dernier_apport` et `lint_ecriture.premiere_page`. Il ne dépend d'aucun autre module.
- Les dates acceptent le décalage horaire écrit par `affaire.py` et `lib_affaire.maintenant()`.
- Le catalogue se lit dans les fiches elles-mêmes (section « Données de contrôle ») : corriger une fiche corrige le contrôle, sans autre fichier à tenir à jour. `test_exercices.py` vérifie le plan de chaque fiche, ses données, leurs renvois aux régimes de `gate.py` et l'absence de tiret cadratin.
- Le champ `exercice` de la séquence (`voies[].exercice`) est facultatif : quand il est présent, il doit concorder avec le diagnostic.

## 7. Divergences relevées par les fiches dans les fichiers partagés

Les rédacteurs des fiches ont relu à la source, le 19 novembre 2026, des règles que d'autres fichiers du plugin énoncent autrement ou laissent non vérifiées. À corriger par la session principale, chaque fois sur la source indiquée (détails dans la fiche citée, sections 2, 3, 6 et 11) :

1. `skills/conduite-de-la-sequence/references/interactions.md` attribue la règle de la date d'expédition du recours administratif à CE, 13 novembre 2026, n° 506435 ; elle a été posée par CE, 30 juin 2025, n° 494573, publié au Recueil (analyse officielle relue pour ce document), que la décision de 2026 réitère (fiche `recours-administratifs-prealables.md`).
2. `references/domaines/civil_et_administratif_general.md` (section 10) et `civil_et_administratif_general_voies.json` (`"franc": false`) tiennent pour non vérifié le caractère franc du délai de l'article R. 421-1 du CJA ; CE, 19 septembre 2014, n° 362568, lu en entier, le juge franc, comme le dit déjà `administratif_special.md` (fiche `requete-annulation.md`).
3. `skills/cassation/SKILL.md`, section 1 : la non-admission de l'article 1014 du CPC vise le pourvoi irrecevable ou qui « n'est manifestement pas de nature à entraîner la cassation », et le délai de l'article 612 court selon les articles 528 et 675 (fiche `pourvoi-cassation-civile.md`) ; le même skill ne dit rien du pourvoi pénal (articles 568, 584, 585 et 590-1 du CPP ; la déchéance faute de mémoire en est la première cause d'échec, fiche `pourvoi-penal.md`). L'article 575 du CPP, que `penal_cedh_qpc.md` invite à relire, est abrogé depuis le 24 juillet 2010 (décision n° 2010-15/23 QPC).
4. `skills/refere-administratif/SKILL.md` : le juge de cassation ne contrôle pas l'appréciation du doute sérieux sauf dénaturation (n° 230268 et n° 238198, fiche `refere-suspension.md`) ; l'interdiction de fonder une même requête sur L. 521-1 et L. 521-2 n'a été lue dans aucune décision, les décisions lues la posent pour L. 521-2 et L. 521-3 (n° 241534) et pour L. 521-3 et R. 541-1 (n° 306461). Le référé-provision exige une décision de l'administration sur une demande préalable, qui peut intervenir en cours d'instance (CE, avis, 7 juillet 2023, n° 471401 ; fiche `refere-provision-administratif.md`).
5. `references/domaines/civil_et_administratif_general.md` : un refus antérieur ne rend pas la demande de mesures utiles « irrecevable », il impose son rejet, y compris pour un refus implicite né pendant l'instance (n° 383189) ; l'article L. 511-2 du CJA a changé le 28 mai 2026 (loi n° 2026-403) ; l'article L. 600-3-1 du code de l'urbanisme, marqué non vérifié dans `administratif_special.md`, est lu (présomption d'urgence contre un refus de permis).
6. `skills/refere-civil/SKILL.md`, régimes `refere_civil_834`, `refere_civil_835_1`, `refere_civil_835_2` et `refere_145` : la caducité de l'article 754 du CPC vaut en référé (Cass. 2e civ., 21 décembre 2023, n° 21-25.162, Bulletin ; 15 janvier 2026, n° 23-14.171), et la représentation par avocat des articles 760 et 761 s'applique sans dispense propre au référé (fiches `refere-civil-*.md`).
7. `skills/contentieux-du-fond/SKILL.md`, section 2 : les fins de non-recevoir relèvent du seul juge de la mise en état dès sa désignation (art. 789, 6°) et, après la clôture, ne sont recevables que si leur cause est survenue ou révélée ensuite (art. 802, al. 4) ; l'article 132 exige une communication spontanée et l'article 15 une communication en temps utile ; la hiérarchie des demandes doit être fixée avant l'expiration du délai de recours, pas nécessairement dans la requête (Société Eden) (fiches `conclusions-et-mise-en-etat.md` et `requete-annulation.md`).
8. `references/domaines/penal_cedh_qpc.md` : la plainte simple suspend la prescription au profit de la victime jusqu'à la réponse du procureur et au plus trois mois, sauf en matière de presse (Crim., 23 juin 2026, n° 25-87.950, Bulletin) ; l'effet interruptif de la plainte avec constitution de partie civile est subordonné à la consignation dans le délai (Crim., 8 mars 2022, n° 21-83.037) ; la contestation du refus de transmettre une QPC suit deux régimes opposés devant la Cour de cassation et devant le Conseil d'État (fiches `plainte-simple.md`, `plainte-avec-constitution-de-partie-civile.md`, `qpc.md`).
9. `references/domaines/travail_commercial_execution.md` : le décret n° 2026-683 modifie aussi les articles R. 1452-2 à R. 1452-4 du code du travail (pièces, communication avant la séance) ; le délai du harcèlement est établi (cinq ans, deux ans pour l'obligation de prévention, Cass. soc., 7 octobre 2026, n° 25-11.362) (fiche `conseil-de-prud-hommes.md`).
10. `skills/refere-administratif/SKILL.md`, section « Urgence » : la règle selon laquelle le juge attribue d'ordinaire à la mesure l'intérêt de l'enfant invoqué par la requérante vaut quand le dossier ne montre pas que la mesure ne protège rien. Le juge des référés a pu suspendre une suspension d'agrément d'assistant familial lorsque le département ne justifiait d'aucun élément vraisemblable et grave et que les indemnités ne couvraient pas les charges fixes (CE, 9 novembre 2023, n° 474932, mentionné aux tables, lu en entier le 20 novembre 2026) ; depuis le 1er septembre 2022, l'assistant familial suspendu conserve sa rémunération (CASF, art. L. 423-8), ce qui affaiblit l'urgence financière. La fiche `refere-suspension.md` porte désormais les deux règles.
11. `skills/lecture-des-decideurs/references/sociologie-juridictions.md` et `institutions-adverses.md` : certains taux sont calculés et non publiés (part des requêtes françaises terminées sans arrêt à Strasbourg), deux versions du rapport public 2026 du Conseil d'État se contredisent sur les QPC, et l'indicateur de suivi des observations du Défenseur des droits est déclaré non déterminé pour 2024 par le rapport annuel de performances (fiches `requete-cedh.md`, `qpc.md`, `defenseur-des-droits.md`).

## 8. Banc

Vingt-deux sondes `EXO-` (`validation/banc/sondes/`), lancées une à une.

**Questions de choix (onze sondes `EXO-` sans « TRAVAIL »).** Chacune présente une situation où un exercice gagne et où le voisin que le client propose ou que le réflexe désigne échoue, et vérifie le choix, la condition décisive et une exigence implicite. Plugin figé avant le module (`banc_runs/plugin_base`, passages 20261119-232643 et 20261119-234355, étiquette « base exercices ») : 11 sur 11. Plugin courant sans le correctif (passage 20261119-235222, « apres exercices ») : 11 sur 11. Le skill n'a été chargé dans aucun des deux passages. Une vérification de la sonde 145 était trop étroite (fenêtre de 120 caractères) ; elle a été élargie et les deux passages renotés.

**Travail réel (onze sondes `EXO-TRAVAIL-`).** La consigne demande de préparer l'acte (requête, assignation, plainte, lettre) et sa fiche ; le point décisif doit sortir sans être demandé. Plugin figé (passages 20261120-002606, 20261120-003330, 20261120-005636, 20261120-012028, « base exercices durcies ») : 10 sur 11. Seule échoue `EXO-TRAVAIL-REFERE-AGREMENT-ENFANT`, reprise de l'épreuve 1 : la requête est préparée et l'urgence est plaidée sur l'enfant sans voir que le juge range son intérêt du côté de la mesure (0,33 sur la première version du dossier, 0,67 sur la seconde, qui retire les pièces à décharge pour reproduire l'épreuve). Trois vérifications trop étroites (diffamation, provision, Cour européenne) ont été élargies et les passages renotés : les réponses étaient justes sur le fond.

**Après le module, sur une copie corrigée** (`banc_runs/plugin_exercices`, plugin courant plus `exercices.patch`, passage 20261120-013358) : 3 sur 4. Les trois sondes réussies sur la base le restent (placement de l'assignation, mesures utiles contre un refus implicite, agent suspendu). `EXO-TRAVAIL-REFERE-AGREMENT-ENFANT` échoue encore (0,67, même vérification) : l'agent a rempli le diagnostic d'exercice sous l'effet du hook (cinq appels à `exercices.py`, bloc validé sans constat `EXERCICE_`) et sa fiche nomme l'intérêt des enfants comme celui « que la requérante invoque » et que la défense opposera, mais son message final ne le dit pas.
