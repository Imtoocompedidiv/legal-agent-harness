---
name: negociation-et-persuasion
description: "Plan de négociation (intérêts, solutions de repli, ce que l'adversaire peut accorder, offre, contreparties, calendrier) et de persuasion de chaque décideur, sans affaiblir le contentieux. À l'ouverture, avant tout acte ou lettre à l'adversaire, à toute offre et après toute décision."
---

# Négociation et persuasion

Un associé de premier rang négocie en même temps qu'il plaide. Il connaît la meilleure solution de repli de chaque partie, ce que l'adversaire peut accorder sans se désavouer, l'effet de chaque voie amiable sur les délais, et le moment où la procédure pèse le plus. Il sait aussi ce que chaque décideur doit croire pour décider, et ne laisse jamais la négociation entamer le dossier contentieux. Ce skill transforme ce savoir en un fichier d'état, `strategie/negociation.json`, établi par le sous-agent `negociateur`, validé par `scripts/negociation.py` et exigé par le contrôle avant dépôt.

Références, chaque règle avec sa source lue et son statut :

- `references/droit_amiable.md` (règles D) : textes en vigueur et jurisprudence de l'amiable, effet de chaque voie sur les délais, préalables obligatoires, transaction civile et administrative, libéralités, homologation, confidentialité, médiateurs, Défenseur des droits, amiable pénal et fiscal.
- `references/levier_limites.md` (règles L) : la procédure comme levier, et ce que la loi pénale, la procédure et la déontologie interdisent.
- `references/negociation_litterature.md` (règles N) : négociation raisonnée et ses critiques, solution de repli, première offre, concessions, position de faiblesse, administration, médiation, biais.
- `references/persuasion_litterature.md` (règles P) : rhétorique judiciaire, ordre des moyens, cadrage, crédibilité, ton, faits défavorables, autorité administrative, médiateur.
- `strategie-contentieuse/references/decideurs.md` (règles A, C et section C) : ancrage, cadrage gains et pertes, lecture de l'offre adverse, ce qu'il ne faut pas croire.

Les règles empiriques sont des hypothèses de travail : presque toutes viennent d'étudiants ou de praticiens étrangers, et aucune ne mesure une manière de négocier ou d'écrire sur des magistrats, des avocats ou des agents publics français. Les règles de droit se relisent à la date de l'acte.


## 1. Ce qui prime

1. **Aucune concession dans un écrit destiné au juge.** L'écrit ne reconnaît aucune faiblesse, ne rapporte aucune offre ni aucun propos de la négociation, et ne contient que les diligences amiables que la loi exige (L9, D3).
2. **En négociation, des contreparties et des échanges, jamais de faiblesse avouée.** Chaque concession répond à une contrepartie et s'adosse à une raison extérieure ; l'analyse des faiblesses reste interne au plan (L10, N18, N21).
3. **Aucun pourcentage de chance.** Le client reçoit une fourchette d'issues et de montants motivée, et les taux publiés d'une institution avec leur année, leur périmètre et leur dénominateur (N6, N31).
4. **La procédure est un levier, jamais une menace illicite.** Seule la voie de droit liée à la demande s'annonce ; aucune plainte, aucun signalement, aucune révélation ne s'échange contre un paiement ou une signature (L3, L4, C. pén., art. 312-10).
5. **Rien ne sort sans l'accord exprès du client** : ni offre, ni contre-offre, ni lettre, ni signature, ni acceptation. Le plan propose ; le client décide (constitution du dossier).
6. **Rien de gratuit pour l'adversaire.** On négocie contre lui, pas avec un partenaire. Aucune information, aucune pièce, aucune réunion, aucune médiation, aucun délai ni aucun report ne s'accorde sans contrepartie écrite, sauf ce que la loi ou le juge impose (CPC, art. 750-1 et 1533-3) ; quand il ne conteste qu'une part, la part non contestée s'exige aussitôt ; la marge, la cible, les faiblesses et les arguments gardés en réserve ne sortent jamais (`rapport-de-force`, V29 à V32).


## 2. Quand établir et réviser le plan

Le plan s'écrit à l'ouverture, avant la ligne définitive, puis se révise à chaque tournant : décision ou mesure du juge, pièce nouvelle, défense adverse, offre ou silence de l'adversaire, proposition de médiation ou d'audience de règlement amiable, échéance qui approche, changement d'interlocuteur, révision de la ligne stratégique, avant tout acte juridictionnel et avant toute lettre à l'adversaire. Chaque révision s'inscrit dans `revisions` (date, tournant, changement) et le champ `date` est relu sur le poste. Le contrôle bloque un plan antérieur à la dernière révision de la ligne, sauf si `ligne_examinee` porte la date de cette ligne.


## 3. Le plan de négociation

Établi dans cet ordre, parce que chaque étape dépend de la précédente.

### 3.1 Les délais d'abord

Pour chaque délai qui court (recours contentieux, prescription, forclusion, péremption), inscrire au `calendrier` la date, sa source et ce qui le protège. Pour chaque voie amiable, déclarer son effet sur les délais selon la table de D1 ; `negociation.py` vérifie la déclaration. Une voie sans effet sur un délai ouvert ne se mène qu'avec l'acte conservatoire daté qui le protège (D2). La saisine du Défenseur des droits ne protège aucun délai par elle-même ; la médiation civile ne suspend que la prescription ; la procédure participative ferme le prétoire pendant sa durée (D1, D14, D16).

### 3.2 Parties et intérêts

Pour chaque partie, la position affichée et les intérêts qui la portent : somme, délai, trésorerie, précédent, relation future, réputation, contrainte du signataire (N1). Chaque intérêt porte son statut (pièce, déclaration de l'adversaire, inférence) et sa source. Pour l'adversaire, écrire `sans_perdre_la_face` : ce qu'il peut accorder sans se désavouer, et la raison qu'on lui donnera de changer de position sans aveu d'erreur (pièce nouvelle, décision intervenue, recalcul, proposition du médiateur) (N37). Face à une personne publique, lire ses contraintes réelles avant de lui prêter une crainte : marge réglementaire, égalité de traitement, instance collégiale, comptable public, défense déjà produite, interdiction de payer ce qui n'est pas dû (N28, N30, D10). Si `strategie/decideurs.json` existe, ses champs sur l'adversaire (qui décide, ce qu'il peut accorder, contraintes) s'y reportent sans être recopiés.

### 3.3 Meilleure solution de repli de chaque partie

Pour le client : le jugement probable net, en fourchette d'issues et de montants, avec la durée, les frais non récupérables, l'aléa d'exécution et le risque de recours, fondé sur des textes et des décisions lus (N6, decideurs A1, A2). En tirer par écrit la cible et le point de réservation (N7). Pour l'adversaire : la même estimation, de son point de vue, avec ses coûts, ses délais, son assureur, son budget, son exposition au précédent (N8). La solution de repli se recalcule à chaque tournant ; elle ne se révèle à l'adversaire que si elle est forte et vérifiable, avec sa pièce (N9). La position faible se travaille d'abord sur l'alternative réelle : preuve à créer, acte prêt, coût du conflit pour l'autre (N23, N25, `action-sur-le-reel`).

### 3.4 Voies amiables

Inscrire toutes les voies ouvertes, y compris celles que personne n'a proposées : demande préalable, recours administratif, médiation conventionnelle ou administrative, médiation préalable obligatoire, médiation ou conciliation judiciaire, audience de règlement amiable, conciliateur de justice, procédure participative, médiateur institutionnel ou de la consommation, Défenseur des droits, transaction, conciliation prud'homale, mesures alternatives pénales, transaction fiscale (D3 à D19). Pour chacune : fondement, caractère obligatoire, effet sur les délais, comparaison avec la solution de repli du client (`repli_compare`), décision de la retenir ou non et sa raison. Un préalable obligatoire non tenté rend l'acte irrecevable ; seule une dispense légale, motivée et sourcée, le remplace (D3, D4).

### 3.5 Objets et options

Lister les objets négociables au-delà du montant : échéancier, garanties, exécution, confidentialité, désistements, frais, délais, mesures en nature, rectification d'une décision (N1, N20). Les classer selon leur valeur pour le client et, par estimation, pour l'adversaire. Chaque option porte son fondement vérifiable : barème, jurisprudence topique, décompte, expertise, règle (N2). Quand plusieurs objets sont en jeu, préparer plusieurs combinaisons de même valeur pour le client (N16).

### 3.6 Première offre

Décider qui ouvre : le client quand son évaluation est faite et que le litige porte surtout sur une somme ; l'adversaire quand il est mieux informé de la valeur, avec une contre-ancre motivée immédiate (N11, N13). La partie faible ancre sur sa cible, jamais sur son alternative médiocre (N24). La première offre est le chiffre le plus favorable que le calcul et les pièces justifient, défendable devant le juge, sans révéler les objets sur lesquels les intérêts convergent (N11, N12, decideurs C2). Un chiffre précis sort d'un calcul montré (N14) ; une fourchette n'est proposée que si sa borne la moins favorable convient au client (N15). Devant un médiateur, un conciliateur ou un juge, aucun chiffre lancé pour voir (N17). La formulation destinée à l'adversaire va dans `premiere_offre.formulation` ; `negociation.py` y bloque tout aveu et toute menace.

### 3.7 Contreparties

Préparer la suite des concessions avant la première offre : chacune conditionnelle (« si vous acceptez tel point, nous pouvons consentir tel autre »), en réponse à un mouvement adverse, décroissante, adossée à une raison extérieure, jamais deux de suite sans réponse (N18, N21). La concession importante est portée par le médiateur ou présentée comme la réponse à un intérêt que l'adversaire a lui-même exprimé (N35). Un dernier mot ne s'annonce que s'il est vrai, avec l'acte qui suit et sa date (N22). Aucune excuse qui reconnaisse une faute ; un regret sans reconnaissance relève du client, après analyse de son usage comme preuve (N36).

### 3.8 Canal, interlocuteur, confidentialité

Choisir pour chaque échange son régime : correspondance entre avocats, confidentielle sauf mention « officielle » ; médiation, conciliation ou audience de règlement amiable, confidentielles, sauf les pièces produites ; lettre directe du client, qui est une pièce (D15, L7). Identifier qui peut signer pour l'adversaire, par quelle habilitation, après quelle délibération, quel contrôle et quel comptable ; pour l'État, le comité ministériel de transaction, obligatoire au-delà de 500 000 euros et protecteur du signataire en dessous (D9, N27). Pour une autorité administrative, le plan de persuasion de l'agent qui signe et de son service juridique suit la section 4.

### 3.9 Calendrier

Ouvrir l'amiable avant que l'adversaire ait investi dans sa défense (N26) ; choisir les moments où il a le plus à perdre à ne pas transiger et ceux où l'offre du client perd sa valeur (L2). Annoncer les dates qui pèsent sur les deux parties comme une échéance commune, jamais la contrainte propre du client (N10). Demander une médiation ou une audience de règlement amiable à un moment choisi, jamais pour gagner du temps contre l'intérêt du client (D12, D13).

### 3.10 Conditions de forme de l'accord

Écrit ; objet délimité, puisque la transaction éteint toute action qui a le même objet ; droits disponibles seulement (D8). Avec une personne publique qui paie : fondement de la dette dans son principe (faute établie, décision devenue définitive, règle), calcul par chef de préjudice, exclusion des chefs non indemnisables, renonciation à l'instance et aux actions de même objet écrite comme contrepartie, habilitation du signataire, délibération et transmission au préfet s'il y a lieu (D9, D10). Homologation : décider si elle sert (force exécutoire, sécurité envers le comptable) ou expose (contrôle de la libéralité par le juge du fond), rédiger l'accord pour ce contrôle, et prévoir la clause qui règle son refus, qui annule la transaction ; le refus et le jugement au fond pouvant tomber dans la même décision, le dossier au fond est complet avant la demande, réponse au motif de refus comprise (D11). Formule exécutoire par le greffe pour un acte contresigné par avocats (D11). `negociation.py` bloque un accord payé par une personne publique sans conditions `absence_de_liberalite` et `habilitation_signataire`, et un accord avec l'État de plus de 500 000 euros sans `comite_transaction`.

### 3.11 Risques et leviers

Chaque risque porte sa parade : refus d'homologation, revirement de l'interlocuteur, défense déjà produite, délai qui expire, fuite d'un chiffre, confidentialité mal choisie, accord inexécuté. Les leviers sont des voies de droit liées à la demande, le calendrier, le coût du conflit pour l'adversaire, l'information, le tiers, la réputation de fermeté loyale (L1, L2, N25, N38). Les leviers de contrainte (injonction et astreinte, exécution provisoire et radiation de l'appel, saisie conservatoire, opposition sur le prix du fonds, mise en cause du tiers solvable) sont dans `rapport-de-force` (V19 à V24) ; celui que l'annonce rendrait inutile, comme la saisie conservatoire, se joue sans être annoncé. Aucun acte ne se dépose pour la seule pression qu'il exerce (L5).


## 4. Le plan de persuasion de chaque décideur

Une entrée par décideur qui compte dans la séquence : juge du tri, juge des référés, formation et rapporteur public, juge de l'homologation, autorité administrative et son service juridique, médiateur ou conciliateur, Défenseur des droits, adversaire lui-même. Le profil du décideur (`strategie/decideurs.json`, skill `lecture-des-decideurs`) en est le point de départ et se cite par `ref_decideur` ; la théorie du cas (`recit-judiciaire`) en est la matière pour le juge. Pour chacun :

- **Ce qu'il doit croire** pour décider en faveur du client, et ce qu'il croit déjà (accords préalables : droit applicable, faits prouvés, P1).
- **Sa raison de décider et son moyen de décider** : la règle qui l'y autorise et la mesure qu'il peut prendre sans risque pour lui (`recit-judiciaire`, section 4 ; P18 pour l'agent qui signe).
- **L'ordre** : le moyen ou l'argument le plus fort d'abord, les arguments faibles retirés plutôt qu'ajoutés pour mémoire (P5, P6).
- **Le cadrage** : la question posée en première page choisit le terrain, faits ou droit ; la demande se présente comme la protection d'une situation acquise quand c'est exact (P8, P9).
- **Les faits défavorables et leur traitement**, chacun par l'un des procédés de `recit-judiciaire`, section 3 : la question posée le rend indifférent, un fait postérieur ou une règle supérieure le dépasse, il se retourne contre son auteur, ou il est hors du débat ; présenté d'abord par nous, à sa date, dans notre qualification, jamais comme une faiblesse (P16, P17). Aucun autre traitement n'est accepté par le schéma.
- **La forme et le ton** : exactitude vérifiable, critique des actes et non des personnes, gravité dite par la conséquence datée, ni excuse ni déférence (P10, P12 à P15). Pour le médiateur ou le tiers évaluateur, une note qui chiffre avec sa méthode et lui donne la matière d'une évaluation sans lui demander de chiffre (P21 à P23). Pour l'autorité administrative, un recours préalable rédigé comme le futur dossier contentieux (P20).
- **Ce qu'il ne faut pas dire**, et le **message clé** s'il sort du dossier ; `negociation.py` y bloque tout aveu et toute menace.


## 5. Articuler négociation et contentieux

- **Le contentieux ne s'arrête pas pour négocier.** Les délais restent protégés (3.1) ; l'acte annoncé se dépose à la date annoncée si l'accord ne vient pas (N22, L1).
- **Rien de la négociation dans l'écrit au juge.** Ni offre, ni contre-offre, ni point de réservation, ni cible, ni propos tenu en médiation. L'écrit mentionne seulement les diligences amiables exigées (CPC, art. 54, 5° ; CJA, art. R. 213-12) et, si cela sert, le fait objectif d'une demande restée sans réponse ou d'une médiation refusée, sans son contenu (L9). Le contrôle bloque le montant de réservation, la cible ou une concession dans l'écrit, et signale les formules qui révèlent une proposition.
- **Ce qui est produit en médiation n'est pas confidentiel.** Aucune pièce que le juge ne doit pas voir n'y est produite (D15).
- **Une lettre directe est une pièce.** Elle se rédige comme si le juge la lisait : faits, règle, demande chiffrée, échéance commune, sans aveu ni menace (D15, L7, L10). Elle obtient un effet de droit ou une réponse écrite et ne révèle ni faiblesse, ni marge, ni argument gardé en réserve, ni vice que l'adversaire pourrait encore réparer (`rapport-de-force`, section 3). `negociation.py controle --non-juridictionnel <lettre>` la vérifie avant l'accord du client.
- **Une offre adverse se lit à l'ombre du jugement probable** (decideurs A1) : la comparer au point de réservation et à la fourchette, la soumettre au client avec la recommandation, ne pas la rejeter par réflexe ni l'accepter par lassitude. Si elle franchit déjà le point de réservation, le plan dit pourquoi poursuivre ou recommande de l'accepter (N7).
- **Après l'accord** : conditions de forme (3.10), homologation ou formule exécutoire, désistement réglé, exécution suivie ; le plan passe à l'état `accord_conclu` et la ligne stratégique se révise.


## 6. Parler au client

Le client reçoit, en clair : la fourchette du jugement probable et ce qui la fonde, la solution de repli de l'adversaire telle qu'on l'estime, la cible et le point de réservation recommandés, la première offre recommandée et qui doit ouvrir, la suite des contreparties, la voie amiable retenue et ce qu'elle fait aux délais, les risques. Les décisions qui lui reviennent se posent une à une : ouvrir ou non, chiffres, signature, envoi, acceptation ou refus d'une offre. Une mauvaise nouvelle se dit une fois, avec la réponse déjà préparée. Aucun pourcentage.


## 7. Chaîne de production et contrôle

1. Le sous-agent `negociateur` écrit `strategie/negociation.json` et `strategie/negociation_<date>.md` à partir de l'état de l'affaire ; il les révise à chaque tournant (section 2). `python "${CLAUDE_PLUGIN_ROOT}/scripts/negociation.py" squelette` donne la structure vide. Dans `actes_couverts` et dans les champs `actes`, un acte se désigne par le nom de son brouillon sans suffixe de version (`ecritures/brouillons/<nom>_vN.md` donne `<nom>`), comme dans la revue de charpente, ou par `*` : une description ne permet pas au contrôle de reconnaître l'acte.
2. `negociation.py valider` contrôle la structure (`references/schemas/negociation.v1.schema.json`) et les règles qui croisent les champs. Corriger jusqu'à zéro bloquant.
3. Avant toute lettre à l'adversaire, à une autorité ou à un médiateur : `negociation.py controle --non-juridictionnel <brouillon>`, puis accord exprès du client.
4. Avant tout acte juridictionnel, le contrôle avant dépôt exige le plan : absent, il bloque, sauf urgence motivée dans la fiche de l'acte (`urgence_amiable` : `motif` et `source`) ; il bloque aussi un plan invalide, qui ne couvre pas l'acte ou qui est antérieur à la ligne, un préalable amiable obligatoire non tenté, des diligences obligatoires non mentionnées, et tout chiffre de réservation, de cible ou de concession dans l'écrit (`integration/negociation.md` pour les codes).
5. Le `contradicteur` peut attaquer le plan comme toute ligne ; l'`architecte-strategique` en compare les voies amiables avec les voies contentieuses dans sa revue de charpente.

Codes émis par `negociation.py` : `NEGOCIATION_INVALIDE`, `ID_DOUBLE`, `PARTIE_INCONNUE`, `OBJET_INCONNU`, `SOURCE_INCONNUE`, `SOURCE_NON_LUE`, `CLIENT_ABSENT`, `ADVERSAIRE_ABSENT`, `REPLI_ABSENT`, `FACE_ADVERSAIRE_NON_ETUDIEE`, `PREALABLE_AMIABLE_NON_TENTE`, `EFFET_DELAI_INEXACT`, `DELAI_NON_PROTEGE`, `OFFRE_INCOHERENTE`, `CONCESSION_SANS_CONTREPARTIE`, `ACCORD_PUBLIC_SANS_FONDEMENT`, `COMITE_TRANSACTION_REQUIS`, `PROBABILITE_INTERDITE`, `AVEU_DE_FAIBLESSE`, `MENACE_ILLICITE` (bloquants) ; `EFFET_DELAI_A_JUSTIFIER`, `OFFRE_ADVERSE_DANS_LA_ZONE`, `CONCESSIONS_NON_DECROISSANTES`, `ECHEC_HOMOLOGATION_NON_PREVU`, `ACCORD_SANS_ECRIT`, `SIGNATAIRE_NON_IDENTIFIE`, `ACTES_NON_NOMMES` (alertes). Au contrôle d'un acte : `NEGOCIATION_ABSENTE`, `NEGOCIATION_HORS_ACTE`, `NEGOCIATION_PERIMEE`, `NEGOCIATION_DANS_L_ECRIT`, `SEUIL_REVELE`, `DILIGENCES_AMIABLES_NON_MENTIONNEES` (bloquants) ; `NEGOCIATION_DIFFEREE_URGENCE`, `PERSUASION_JUGE_ABSENTE`, `NEGOCIATION_EVOQUEE` (alertes).


## 8. Limites

Les contrôles sont mécaniques : ils vérifient qu'un plan existe, qu'il est cohérent et que certains chiffres et certaines formules ne sortent pas ; ils ne jugent ni la justesse de l'estimation, ni la qualité de l'offre, ni l'issue. Les motifs de détection des aveux et des menaces ont des faux positifs et des oublis. Les règles empiriques ne sont pas mesurées sur des praticiens français. Le droit de l'amiable a changé en 2025 et 2026 : relire les textes à la date de l'acte.
