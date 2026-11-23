# Sécurité et confidentialité

Le harness travaille sur des dossiers couverts par le secret professionnel. Trois règles le gouvernent.

1. **Rien de privé dans le dépôt.** Les dossiers d'affaire, les pièces, les profils de cabinet et les coffres de pseudonymisation
   vivent hors du dépôt ; `.gitignore` les exclut. Le banc de validation n'utilise que des pièces synthétiques et des décisions
   publiques, dont les noms de magistrats sont occultés.
2. **Rien de privé dans une requête publique.** Les hooks refusent qu'une donnée du client parte vers un service public de
   recherche juridique (LibreJustice, HAL, bases savantes).
3. **Ce que voit le modèle.** Sans pseudonymisation, le contenu des pièces est transmis au fournisseur du modèle. Le mode
   pseudonymisé (`docs/PSEUDONYMISATION.md`) ne lui transmet que des jetons ; la table de correspondance reste chiffrée sur le poste.
   Une pseudonymisation n'est pas une anonymisation : le cabinet reste responsable de son analyse de risque et du choix de son
   fournisseur.

Signaler une faille : ouvrir un ticket sans y joindre aucune donnée de dossier, ou écrire aux mainteneurs du dépôt.
