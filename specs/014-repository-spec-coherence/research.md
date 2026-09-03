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

## Décision 2bis — Valeurs de statut canoniques et règles d'exception

- **Valeurs canoniques** (vocabulaire partagé, cf. `spec.md` Key Entities) : `livré`, `partiel`, `en cours`, `backlog`.
- **Règle d'exception** : un identifiant de spec peut porter un statut composite par phase (ex. « Phase 1 ✅ livrée — Phase 0 ~80 % — Phases 2-5 backlog ») uniquement lorsque le plan de la spec définit explicitement des phases numérotées ; sinon un seul statut canonique s'applique à l'ensemble de la spec.
- **Règle d'exception secondaire** : un statut « livré » au niveau fonctionnel n'implique pas que toutes les cases de `tasks.md` sont cochées. Une case peut rester ouverte avec une raison de blocage documentaire (ex. tâche de vérification historique non ré-exécutée) sans remettre en cause le statut livré, dès lors qu'une preuve de livraison (commit, CHANGELOG, code présent) est identifiable.

## Exceptions historiques documentées (T027)

- **Numérotation `012` → `013` (logging)** : l'ancien draft `012-logging-strategy` a été renuméroté en `013-logging-strategy` le 2026-05-05 pour libérer le numéro `012` au profit de `012-semantic-search-api-platform` (initiative prioritaire). Les mentions de `012-logging-strategy` restantes dans `specs/CHANGELOG.md`, `specs/PLANNING.md` (ligne de contexte historique), `specs/README.md` (note historique) et `docs/LOGGING.md` (mention de provenance) sont volontairement conservées car datées et contextualisées — conformément à la Décision 3. Seules les mentions non datées et non contextualisées (catalogue `README.md`, statut `docs/ARCHITECTURE.md`) ont été corrigées par cette feature (T010, T012).
- **Branche `011-auth-ldap-sso`** : la spec documente `feature/002-advanced-search-suite (livré sur la branche principale)` comme branche d'origine. Ce n'est pas une erreur : LDAP/SSO a été développé et livré sur la branche `feature/002-advanced-search-suite` avant d'être fusionné sur `main`, et la spec le précise explicitement. Aucune correction n'était nécessaire (T013, vérifié).
- **`scripts/check_spec_coherence.sh` — faux positifs `STALE_REF` acceptés** : le contrôle ne peut pas distinguer automatiquement une mention historique datée d'une mention encore active (Décision 4 : rester non destructif et ne pas juger automatiquement). Les lignes de `PLANNING.md`, `README.md`, `docs/LOGGING.md` et de ce `quickstart.md` qui mentionnent encore `012-logging-strategy` dans un contexte de migration datée sont des faux positifs attendus de la Section E du contrôle — voir le résultat consigné dans `quickstart.md` (T026/T030).

## Décision 5 — Contrats de cette feature

- **Decision**: Aucun contrat API ou contrat d'intégration n'est créé pour cette feature ; le livrable est un ensemble de documents et de contrôles de dépôt.
- **Rationale**: La feature ne change aucun protocole consommé par le frontend, le backend ou une application tierce.
- **Alternatives considered**: Exposer un endpoint d'audit ; rejeté car cela élargirait inutilement le périmètre et créerait un nouveau contrat à maintenir.
