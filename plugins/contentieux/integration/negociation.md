# Intégration du module négociation et persuasion

Module livré sans toucher aux fichiers partagés : `skills/negociation-et-persuasion/SKILL.md` et ses quatre références (`droit_amiable.md`, `levier_limites.md`, `negociation_litterature.md`, `persuasion_litterature.md`), `agents/negociateur.md`, `scripts/negociation.py`, `references/schemas/negociation.v1.schema.json`, `tests/test_negociation.py`, `docs/epreuves/negociation.md` et ses pièces (`docs/epreuves/negociation/`). Ce document donne ce que la session principale applique aux fichiers partagés.

## 1. Règle intégrée

Avant tout acte juridictionnel, le contrôle avant dépôt exige `strategie/negociation.json` : au moins une voie amiable examinée, comparée à la meilleure solution de repli du client, avec la solution de repli de chaque adversaire (le schéma l'impose). Seule une urgence motivée dans la fiche de l'acte permet de déposer d'abord : champ `urgence_amiable`, objet `motif` (pourquoi l'amiable ne peut pas précéder l'acte) et `source` (texte ou pièce) ; le contrôle émet alors une alerte, pas un blocage. Le plan doit aussi être valide, couvrir l'acte, être postérieur à la dernière révision de la ligne (ou porter `ligne_examinee`), ne laisser aucun préalable amiable obligatoire non tenté, et aucun de ses chiffres secrets ne doit apparaître dans l'écrit.

## 2. Correctif de code : `integration/negociation.patch`

Diff unifié, chemins relatifs à la racine du plugin. Depuis `plugins/contentieux` :

```
patch -p1 --binary --dry-run < integration/negociation.patch
patch -p1 --binary < integration/negociation.patch
python -m pytest -q plugins/contentieux/tests      (depuis la racine du dépôt)
```

`--binary` garde les fins de ligne CRLF de `hook.py`. Vérification faite le 18 novembre 2026 : le correctif s'applique à blanc au plugin courant, et la suite complète passe sur une copie corrigée (138 tests, dont `TestIntegration` de `test_negociation.py`, ignorés tant que le correctif n'est pas appliqué). Si un autre module a modifié entre-temps les mêmes lignes, appliquer à la main les quatre changements ci-dessous ; chaque emplacement est donné par la ligne qui le précède.

### 2.1 `scripts/gate.py`

Juste après le bloc des décideurs (`DECIDEURS.controler(racine, ecriture, fiche, c)`) et avant le commentaire `# Le récit : théorie du cas…` :

```python
    # La négociation : une voie amiable examinée avec la solution de repli de chaque partie avant tout acte juridictionnel,
    # sauf urgence motivée dans la fiche ; aucun chiffre de la négociation dans l'écrit (skill negociation-et-persuasion).
    import negociation as NEGOCIATION
    NEGOCIATION.controler(racine, ecriture, fiche, c, juridictionnel=juridictionnel, texte=texte)
```

L'appel vaut pour tout acte qui a une fiche. Pour un acte non juridictionnel (courrier précontentieux), il ne vérifie que la lettre (chiffres secrets, aveu, menace) et seulement si le plan existe.

### 2.2 `scripts/hook.py`, briefing

Dans `briefing`, juste après la ligne `lignes.append("Aucun profil des décideurs (strategie/decideurs.json) : …")` :

```python
    nego = L.lire_json(racine / "strategie/negociation.json") or {}
    if isinstance(nego, dict) and nego.get("etat"):
        jour = L.maintenant().date().isoformat()
        prochain = sorted((j for j in nego.get("calendrier") or [] if isinstance(j, dict) and str(j.get("date", "")) >= jour),
                          key=lambda j: str(j.get("date")))
        suite = f" ; prochaine étape {prochain[0].get('date')} : {prochain[0].get('evenement')}" if prochain else ""
        lignes.append(f"Négociation ({nego.get('date')}) : état « {nego.get('etat')} »{suite}. Aucun chiffre de la négociation "
                      "dans un écrit au juge.")
    else:
        lignes.append("Aucun plan de négociation (strategie/negociation.json) : examiner les voies amiables et la solution de repli "
                      "de chaque partie avant tout acte juridictionnel (skill negociation-et-persuasion).")
```

Le briefing ne réinjecte ni le point de réservation ni la cible : ils restent dans le fichier.

### 2.3 `scripts/hook.py`, validation à l'enregistrement

Dans `post_tool`, juste après le bloc `if rel == "strategie/decideurs.json": … sys.exit(0)` et avant `if rel in L.SCHEMAS:` :

```python
    if rel == "strategie/negociation.json":
        import negociation as NEGOCIATION
        _, constats = NEGOCIATION.charger(racine)
        bloquants = [f"{k['code']} : {k['message']}" for k in constats if k["gravite"] == "BLOQUANT"]
        alertes = [f"{k['code']} : {k['message']}" for k in constats if k["gravite"] == "ALERTE"]
        if bloquants:
            sortie({"decision": "block", "reason": "Plan de négociation invalide, à reprendre maintenant :\n- " + "\n- ".join(bloquants[:20])})
        if alertes:
            contexte("PostToolUse", "Plan de négociation enregistré, avec des alertes :\n- " + "\n- ".join(alertes[:10]))
        sys.exit(0)
```

### 2.4 `tests/test_contentieux.py`

Le référé conforme écrit un plan de négociation couvrant l'acte. Juste après `ecrire(self.r / "strategie/decideurs.json", profil)` :

```python
        from test_negociation import plan_complet
        plan = plan_complet()
        plan.update({"date": maintenant, "actes_couverts": ["ref"]})
        ecrire(self.r / "strategie/negociation.json", plan)
```

Le plan ne couvre pas le juge de ce référé dans sa partie persuasion : le contrôle émet l'alerte `PERSUASION_JUGE_ABSENTE`, sans effet sur le PASS.

## 3. Codes et messages

Constats de `negociation.controler` (contrôle d'un acte), au format de `gate.py` :

| Code | Gravité | Cause |
| --- | --- | --- |
| `NEGOCIATION_ABSENTE` | BLOQUANT | acte juridictionnel sans `strategie/negociation.json` ni `urgence_amiable` motivée et sourcée dans la fiche |
| `NEGOCIATION_DIFFEREE_URGENCE` | ALERTE | pas de plan, urgence motivée dans la fiche : le plan s'écrit dès l'acte déposé |
| `NEGOCIATION_INVALIDE` et tout code bloquant de la validation | BLOQUANT | plan qui ne respecte pas le schéma ou une règle croisée (liste ci-dessous) |
| `NEGOCIATION_HORS_ACTE` | BLOQUANT | `actes_couverts` ne nomme pas l'acte (nom du brouillon sans `_vN`) ni `*` |
| `NEGOCIATION_PERIMEE` | BLOQUANT | la ligne a été révisée après le plan, sans `ligne_examinee` égale à sa date |
| `PERSUASION_JUGE_ABSENTE` | ALERTE | aucun plan de persuasion d'un juge pour cet acte |
| `NEGOCIATION_DANS_L_ECRIT` | BLOQUANT | l'écrit au juge contient le montant du point de réservation, de la cible ou d'une concession |
| `NEGOCIATION_EVOQUEE` | ALERTE | l'écrit au juge rapporte une proposition ou un propos de médiation |
| `DILIGENCES_AMIABLES_NON_MENTIONNEES` | BLOQUANT | un préalable amiable obligatoire vaut pour l'acte et l'écrit ne mentionne ni les diligences ni la dispense (CPC, art. 54, 5° ; CJA, art. R. 213-12) |
| `SEUIL_REVELE` | BLOQUANT | courrier à l'adversaire qui contient un chiffre secret |
| `AVEU_DE_FAIBLESSE` | BLOQUANT | courrier à l'adversaire qui reconnaît une faiblesse |
| `MENACE_ILLICITE` | ALERTE | courrier à l'adversaire qui évoque plainte, signalement, presse ou révélation |

Validation du plan (`negociation.valider`, aussi lancée par le hook à l'enregistrement) : bloquants `NEGOCIATION_INVALIDE`, `ID_DOUBLE`, `PARTIE_INCONNUE`, `OBJET_INCONNU`, `SOURCE_INCONNUE`, `SOURCE_NON_LUE`, `CLIENT_ABSENT`, `ADVERSAIRE_ABSENT`, `REPLI_ABSENT`, `FACE_ADVERSAIRE_NON_ETUDIEE`, `PREALABLE_AMIABLE_NON_TENTE`, `EFFET_DELAI_INEXACT`, `DELAI_NON_PROTEGE`, `OFFRE_INCOHERENTE`, `CONCESSION_SANS_CONTREPARTIE`, `ACCORD_PUBLIC_SANS_FONDEMENT`, `COMITE_TRANSACTION_REQUIS`, `PROBABILITE_INTERDITE`, `AVEU_DE_FAIBLESSE`, `MENACE_ILLICITE` ; alertes `EFFET_DELAI_A_JUSTIFIER`, `OFFRE_ADVERSE_DANS_LA_ZONE`, `CONCESSIONS_NON_DECROISSANTES`, `ECHEC_HOMOLOGATION_NON_PREVU`, `ACCORD_SANS_ECRIT`, `SIGNATAIRE_NON_IDENTIFIE`, `ACTES_NON_NOMMES`. Chaque message cite la règle sourcée (D, L, N, P) ou le texte.

Aucun de ces constats ne porte de catégorie de rejet : ils ne changent pas la mesure V2 du protocole de validation.

## 4. Schéma

`references/schemas/negociation.v1.schema.json` (`schema` : `negociation/1`), validé par `pieces.valider_schema`. Champs obligatoires : `date`, `actes_couverts`, `etat` (a_ouvrir, en_cours, suspendue, accord_conclu, echec, ecartee), `parties` (rôle, nature, intérêts avec statut et sources, position affichée, `sans_perdre_la_face` pour l'adversaire), `repli` (une entrée par client et par adversaire : alternative, issue probable, fourchette, délai, coûts, valeur nette, sources), `voies_amiables` (voie, ouverte, obligatoire, fondement, effet sur les délais, acte conservatoire, comparaison avec le repli, retenue et raison, dispense), `options`, `offre` (sens, qui ouvre, première offre avec calcul et sources et formulation, cible, point de réservation, dernière offre adverse), `contreparties` (ce que nous cédons, contre quoi, condition, ordre, raison extérieure), `interlocuteurs` (pouvoir, habilitation, chaîne de validation, canal), `calendrier`, `risques`, `persuasion` (par décideur : ce qu'il doit croire, raison et moyen de décider, ordre, faits défavorables avec l'un des quatre traitements admis, forme, ton, ce qu'il ne faut pas dire, message clé), `sources`. Facultatifs : `ligne_examinee`, `objets`, `conditions_de_forme`, `leviers`, `urgence`, `revisions`. `negociation.py squelette` imprime la structure vide.

Dans la fiche de l'acte (`skills/controle-avant-depot`, section 1), un champ nouveau : `urgence_amiable` (`motif`, `source`).

## 5. Textes des skills, agents et documentation

À ajouter mot pour mot (remplacement par passage, ces fichiers bougent sous d'autres modules).

**`skills/controle-avant-depot/SKILL.md`, section 1**, après la puce `numeros_non_jurisprudentiels` :

> - `urgence_amiable` : `motif` et `source`, quand l'acte doit partir avant que les voies amiables aient été examinées (skill `negociation-et-persuasion`) ; le contrôle n'émet alors qu'une alerte, et le plan s'écrit dès l'acte déposé.

**Même fichier, section 1 bis**, à la fin de la phrase qui énumère les préalables (après « … ou inscrit dans `profil_decideurs_applique` »), avant le point :

> ; le plan de négociation (`strategie/negociation.json`, skill `negociation-et-persuasion`, sous-agent `negociateur`), valide, couvrant l'acte, postérieur à la ligne ou inscrit dans `ligne_examinee`, sans préalable amiable obligatoire non tenté, sauf urgence motivée dans la fiche (`urgence_amiable`) ; l'écrit ne contient aucun chiffre de la négociation (point de réservation, cible, concession) et mentionne les diligences amiables que la loi exige

**`agents/architecte-strategique.md`, point 6 « La négociation »**, ajouter à la liste :

> - l'effet de chaque voie amiable sur les délais et l'acte conservatoire qui les protège (`negociation-et-persuasion/references/droit_amiable.md`, D1, D2) ;
> - les préalables amiables obligatoires (CPC, art. 750-1 ; CJA, art. L. 213-11) : un préalable non tenté sans dispense motivée est un point dirimant ;
> - avec une personne publique qui paierait, les conditions de forme de l'accord (fondement de la dette, calcul par chef, signataire, comité ministériel de transaction, homologation et clause qui règle son refus, D9 à D11).

**Même fichier, section « Sortie »**, puce `voies_comparees`, ajouter à la fin : « ; les voies amiables du plan de négociation y figurent, avec leur effet sur les délais ».

**`agents/plume.md`, paragraphe « Limites strictes »**, ajouter à la fin :

> Tu n'introduis aucun élément de la négociation dans une écriture destinée au juge : ni offre, ni contre-offre, ni montant de réservation, de cible ou de concession, ni propos tenu en médiation ; seules restent les diligences amiables que la loi exige. Dans une lettre à l'adversaire, à une autorité ou à un médiateur, tu parles de contreparties et d'échanges, jamais de faiblesse, et tu ne laisses passer aucune allusion à une plainte, un signalement ou une révélation ; tu signales le passage au lieu de le réécrire si le fond est en cause.

**`skills/strategie-contentieuse/SKILL.md`, section 4, puce « Limites »**, ajouter : « ; aucune plainte, aucun signalement ni aucune révélation ne s'échange contre un paiement ou une signature (C. pén., art. 312-10 ; Cass. crim., 30 janvier 2001, n° 99-87.346 ; `negociation-et-persuasion/references/levier_limites.md`) ».

**`README.md`**, liste des sous-agents : ajouter `negociateur` après `stratege-terrain` ; liste des skills et des scripts : `negociation-et-persuasion` et `scripts/negociation.py` (valider, controle, squelette).

**`templates/affaire/LISEZMOI.md`**, après la ligne `strategie/ligne.json` :

> | `strategie/negociation.json` | plan de négociation et de persuasion : intérêts, solutions de repli, voies amiables et délais, offre, contreparties, interlocuteurs, calendrier, conditions de forme, persuasion de chaque décideur ; exigé par le contrôle avant dépôt | `negociateur`, `negociation.py` |

**`docs/ARCHITECTURE.md`**, section « La campagne avant l'acte », puce à ajouter :

> - **La négociation en même temps que le procès.** Le `negociateur` établit et révise à chaque tournant le plan de négociation et de persuasion (`strategie/negociation.json`) : solution de repli de chaque partie, ce que l'adversaire peut accorder sans perdre la face, effet de chaque voie amiable sur les délais, première offre, contreparties conditionnelles, conditions de forme d'un accord avec une personne publique, persuasion de chaque décideur. Le contrôle bloque l'acte juridictionnel sans voie amiable examinée, sauf urgence motivée, et l'écrit qui laisserait passer un chiffre de la négociation. Règles sourcées dans `skills/negociation-et-persuasion/references/`, épreuve dans `docs/epreuves/negociation.md`.

## 6. Compatibilité

- Le module lit `strategie/ligne.json` (date) et, s'il existe, `strategie/decideurs.json` par renvoi (`ref_decideur`) sans le valider ; il ne dépend d'aucun autre module que `pieces.py` (validateur de schéma) et `lib_affaire.py`.
- Les dates acceptent le décalage horaire écrit par `affaire.py` et `lib_affaire.maintenant()`.
- Les champs `actes_couverts` et `actes` désignent les écritures par le nom de leur brouillon sans suffixe de version, comme la revue de charpente et le profil des décideurs.
