# Correspondance : commercial-legal vers contrats-d-affaires

| Procédé d'origine | Transposition dans le harness |
| --- | --- |
| `cold-start-interview`, `customize` | Skill commun `profil-et-positions` ; questions du pôle dans `references/positions.md` |
| `matter-workspace` | Dossier d'affaire du harness (`etat/affaire.json`) ou `cabinet/` du dossier de travail |
| `review` (aiguillage vers le bon procédé) | `SKILL.md`, section 1 (orientation, côté, contrôle de portée) |
| `nda-review` | `SKILL.md`, 2.1 : grille VERT, ORANGE, ROUGE ; durée lue au regard de l'article 1210 du code civil, clause pénale au regard de l'article 1231-5 |
| `vendor-agreement-review` | `SKILL.md`, 2.2 : point rédhibitoire, comparaison clause par clause, limitation de responsabilité en quatre dimensions, écart de droit applicable, circuit de validation |
| `saas-msa-review` | `SKILL.md`, 2.2, point 4 : reconduction, indexation, niveaux de service, réversibilité, sous-traitants ultérieurs (RGPD, art. 28), droits sur les données |
| `review-proposals` | `SKILL.md`, 2.3 |
| `amendment-history` | `SKILL.md`, 2.4 |
| `renewal-tracker`, agent `renewal-watcher` | `SKILL.md`, 2.5 ; registre `contrats` et `scripts/echeancier.py` ; sous-agent `veilleur` |
| `escalation-flagger` | `SKILL.md`, 2.6 ; journal des écarts `registres/ecarts.json` |
| `stakeholder-summary` | `SKILL.md`, 2.7 et contrôle de destination |
| Agents `deal-debrief`, `playbook-monitor` | `SKILL.md`, 2.8 ; journal des écarts relu par le `veilleur` |
| Connecteurs Ironclad, DocuSign, iManage, TopCounsel, Definely | Non transposés : aucun de ces outils n'est raccordé au poste. Le registre local et `echeancier.py` tiennent lieu de gestion des contrats ; la signature reste une décision du client hors du harness. |
| Vérification de la contrepartie (absente de l'origine) | Ajoutée : `scripts/registres_publics.py` (API Recherche d'entreprises, BODACC) |
| Garde-fous propres au droit américain (*attorney work product*, règle fédérale 408, lois des États sur la non-concurrence et la reconduction) | Remplacés par le contrôle de destination du droit français (`docs/CONSEIL.md`, section 5) et par les règles citées dans `SKILL.md` et `positions.md` |
