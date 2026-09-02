# Research — Cohérence du dépôt et des artefacts de spécification

## Décision 1 — Source de vérité de l'état du dépôt

- **Decision**: Git fournit l'état du dépôt et les fichiers présents fournissent l'état documentaire courant.
- **Rationale**: Les métadonnées d'outils peuvent être obsolètes ou afficher une branche différente ; l'état Git est directement vérifiable.
- **Alternatives considered**: Utiliser uniquement les statuts des fichiers Markdown ; rejeté car cela ignore les fichiers manquants et les changements réellement présents dans le dépôt.

## Décision 2 — Statuts séparés de la complétude documentaire

- **Decision**: Un statut fonctionnel livré ne coche une tâche que si une preuve est disponible ; les tâches historiques non réconciliées restent ouvertes ou sont annotées comme dette documentaire.
- **Rationale**: La présence du code ne prouve pas les validations métier, la documentation ou la complétude du workflow.
- **Alternatives considered**: Cocher toutes les tâches d'une feature déclarée livrée ; rejeté car cela masque les validations manquantes.

## Décision 3 — Numérotation des specs

- **Decision**: Un identifiant courant ne porte qu'un titre ; les anciens identifiants ne sont conservés que dans le changelog ou une note de migration datée.
- **Rationale**: Deux titres sous le même numéro rendent les références ambiguës pour les mainteneurs et les outils.
- **Alternatives considered**: Garder les deux numéros 012 comme alias permanents ; rejeté car le catalogue et les commandes Spec Kit ont besoin d'un contexte unique.

## Décision 4 — Nature du contrôle

- **Decision**: Le contrôle de cohérence est non destructif, déterministe et séparable des corrections documentaires.
- **Rationale**: Un audit doit pouvoir être relancé avant et après correction sans altérer les preuves qu'il examine.
- **Alternatives considered**: Corriger automatiquement tous les statuts ; rejeté car une tâche métier ou une validation d'infrastructure ne peut pas être déduite de façon fiable.

## Décision 5 — Contrats de cette feature

- **Decision**: Aucun contrat API ou contrat d'intégration n'est créé pour cette feature ; le livrable est un ensemble de documents et de contrôles de dépôt.
- **Rationale**: La feature ne change aucun protocole consommé par le frontend, le backend ou une application tierce.
- **Alternatives considered**: Exposer un endpoint d'audit ; rejeté car cela élargirait inutilement le périmètre et créerait un nouveau contrat à maintenir.
