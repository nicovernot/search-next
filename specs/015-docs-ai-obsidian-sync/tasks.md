---

description: "Task list for reliable, Obsidian-viewable, AI-usable technical documentation"
---

# Tasks: Documentation technique fiable, lisible dans Obsidian et exploitable par l'IA

**Input**: Design documents from `specs/015-docs-ai-obsidian-sync/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`

**Scope**: Uniquement les 12 fichiers de `docs/` et les scripts de contrôle associés ; aucun code applicatif n'est modifié.

## Phase 1: Setup

**Purpose**: Confirmer que l'audit de `research.md` reflète toujours l'état actuel de `docs/` avant d'éditer.

- [x] T001 [P] Confirmer que l'audit des 12 fichiers de `docs/` dans `specs/015-docs-ai-obsidian-sync/research.md` reflète toujours l'état actuel (aucune dérive depuis la planification)
- [x] T002 [P] Confirmer que la convention d'entête de fraîcheur (Décision 1) et la convention d'espace réservé générique (Décision 4) de `research.md` sont prêtes à être appliquées, en cohérence avec `docs/LOGGING.md` déjà daté
- [x] T003 [P] Vérifier qu'aucun marqueur de conflit Git ni fichier historique non étiqueté supplémentaire n'a été introduit dans `docs/` depuis l'audit de `research.md`

## Phase 2: Foundational

**Purpose**: Mettre en place le contrôle automatisé partagé avant les corrections de contenu par user story.

- [x] T004 Créer `scripts/check_docs_coherence.sh` (option `--root`, helpers `note`/`finding`, codes de sortie 0/1/2), limité au périmètre `docs/`, sur le modèle de `scripts/check_spec_coherence.sh`
- [x] T005 [P] Créer `scripts/test_check_docs_coherence.sh` avec le harnais de fixtures temporaires (`mktemp`, `assert_exit_code`, `assert_contains`) et les tests d'usage (`--root` invalide, option inconnue), sur le modèle de `scripts/test_check_spec_coherence.sh`

**Checkpoint**: Le script et son harnais de test s'exécutent (même sans détection de contenu encore) avant de commencer les user stories.

## Phase 3: User Story 1 - Se fier à une documentation exacte (Priority: P1) 🎯 MVP

**Goal**: Chaque fichier de `docs/` reflète l'état actuel du code, sans marqueur de conflit, avec une date de fraîcheur explicite.

**Independent Test**: Ouvrir chaque fichier de `docs/`, vérifier qu'aucun marqueur de conflit Git ne subsiste, et comparer un échantillon d'affirmations avec le code et la configuration actuels.

### Tests for User Story 1

- [x] T006 [US1] Ajouter la détection `CONFLICT_MARKER` et ses tests à `scripts/check_docs_coherence.sh` / `scripts/test_check_docs_coherence.sh`
- [x] T007 [US1] Ajouter la détection `MISSING_FRESHNESS_DATE` et ses tests à `scripts/check_docs_coherence.sh` / `scripts/test_check_docs_coherence.sh`

### Implementation for User Story 1

- [x] T008 [P] [US1] Résoudre les 3 blocs de conflit Git non résolus dans `docs/ARCHITECTURE.md` (lignes 3-9, 216-222, 265-269 — conserver la version la plus récente et vérifiable) et ajouter l'entête de fraîcheur
- [x] T009 [P] [US1] Ajouter l'entête de fraîcheur à `docs/API_V1.md` et vérifier les endpoints cités contre `search_api_solr/app/api/v1/`
- [x] T010 [P] [US1] Vérifier et confirmer l'entête de fraîcheur existant de `docs/LOGGING.md` (déjà daté en feature 014) contre l'état actuel du code de logging
- [x] T011 [P] [US1] Ajouter l'entête de fraîcheur à `docs/ENVIRONMENTS.md` et vérifier la structure contre les fichiers `.env.*` et `scripts/sync_env.sh` actuels
- [x] T012 [P] [US1] Ajouter l'entête de fraîcheur à `docs/CORS_CONFIGURATION.md` et vérifier la configuration contre `search_api_solr/app/settings.py` et `app/main.py`
- [x] T013 [P] [US1] Ajouter l'entête de fraîcheur à `docs/INSTALL_PROD_NO_DOCKER.md` et vérifier les commandes contre les scripts actuels
- [x] T014 [P] [US1] Ajouter une date de vérification à `docs/RECOMMENDATIONS.md` (déjà étiqueté ARCHIVE)
- [x] T015 [P] [US1] Ajouter l'entête de fraîcheur à `docs/REDIS_INTEGRATION.md` et vérifier l'implémentation contre le cache Redis actuel du backend
- [x] T016 [P] [US1] Ajouter une date de vérification à `docs/SETUP_COMPLETE.md` (déjà étiqueté ARCHIVE)
- [x] T017 [P] [US1] Ajouter un bandeau de rôle et une date de vérification à `docs/CHANGELOG.md` distinguant son périmètre de `specs/CHANGELOG.md` (Décision 6)

**Checkpoint**: Tous les fichiers de `docs/` ont un contenu exact et daté ; aucun marqueur de conflit ne subsiste — livrable MVP indépendant.

## Phase 4: User Story 2 - Naviguer la documentation comme un vault Obsidian (Priority: P2)

**Goal**: Un point d'entrée unique et des liens internes qui se résolvent correctement, sans doublon de contenu.

**Independent Test**: Ouvrir `docs/` comme vault Obsidian, vérifier que `docs/README.md` liste chaque document, que les liens internes s'ouvrent sur la bonne cible, et qu'aucune syntaxe brisée n'apparaît.

### Tests for User Story 2

- [x] T018 [US2] Ajouter la détection `BROKEN_LINK` (résolution de tous les liens Markdown relatifs `[texte](chemin)` trouvés dans chaque fichier `docs/*.md`, pas seulement `docs/README.md`) et ses tests à `scripts/check_docs_coherence.sh` / `scripts/test_check_docs_coherence.sh`

### Implementation for User Story 2

- [x] T019 [US2] Fusionner le contenu vérifiable de `docs/CORS_IMPLEMENTATION_SUMMARY.md` dans `docs/CORS_CONFIGURATION.md` puis supprimer `docs/CORS_IMPLEMENTATION_SUMMARY.md`
- [x] T020 [US2] Fusionner le contenu vérifiable de `docs/ENVIRONMENT_MANAGEMENT_SUMMARY.md` dans `docs/ENVIRONMENTS.md` puis supprimer `docs/ENVIRONMENT_MANAGEMENT_SUMMARY.md`
- [x] T021 [US2] Créer `docs/README.md` listant chaque fichier restant de `docs/` avec une description d'une ligne, groupé par rôle (référence vivante / historique-archive / log continu) et des liens relatifs
- [x] T022 [US2] Ajouter des références croisées pertinentes en liens relatifs entre fichiers de `docs/` (ex. `ARCHITECTURE.md` ↔ `LOGGING.md`, `ENVIRONMENTS.md` ↔ `CORS_CONFIGURATION.md`)

**Checkpoint**: Point d'entrée unique, doublons supprimés, liens internes résolus — livrable indépendant testable dans Obsidian.

## Phase 5: User Story 3 - Vérifier un comportement via un exemple concret (Priority: P3)

**Goal**: Chaque document décrivant un comportement exécutable contient un exemple concret anonymisé.

**Independent Test**: Pour chaque document décrivant un comportement exécutable, vérifier qu'il contient au moins un exemple concret et que cet exemple est cohérent avec le code actuel, sans valeur réelle d'environnement.

### Implementation for User Story 3

> Pas de détection automatisée dédiée : l'anonymisation des exemples est hors périmètre de FR-011 (script), vérifiée manuellement via l'étape 7 du `quickstart.md`.

- [x] T023 [P] [US3] Anonymiser les exemples `curl` de `docs/API_V1.md` (remplacer `localhost:8003` par `<API_BASE_URL>`, l'URL de document réelle par un identifiant générique)
- [x] T024 [P] [US3] Ajouter/vérifier un exemple concret anonymisé dans `docs/ENVIRONMENTS.md` (valeurs `.env` d'exemple avec espaces réservés)
- [x] T025 [P] [US3] Ajouter/vérifier un exemple concret anonymisé dans `docs/CORS_CONFIGURATION.md` (configuration d'origines autorisées avec domaine générique)
- [x] T026 [P] [US3] Ajouter/vérifier un exemple concret anonymisé dans `docs/INSTALL_PROD_NO_DOCKER.md` (commandes sans nom d'hôte réel)
- [x] T027 [P] [US3] Ajouter/vérifier un exemple concret anonymisé dans `docs/REDIS_INTEGRATION.md` (exemple de connexion avec hôte/port génériques)
- [x] T028 [P] [US3] Confirmer que les exemples déjà présents dans `docs/LOGGING.md` respectent FR-012 (motifs génériques, aucune valeur réelle)

**Checkpoint**: Chaque document décrivant un comportement exécutable contient au moins un exemple concret anonymisé — livrable indépendant testable.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Vérifier la conformité finale et consigner les résultats.

- [x] T029 [P] Exécuter `scripts/check_docs_coherence.sh` en intégralité et consigner le résultat dans `specs/015-docs-ai-obsidian-sync/quickstart.md`
- [x] T030 [P] Vérifier que `scripts/check_docs_coherence.sh` ne modifie aucun fichier (`git status` identique avant/après)
- [x] T031 Vérifier l'intégralité des liens Markdown internes de `docs/` (étapes 3 et 6 du quickstart)
- [x] T032 Ajouter une entrée dans `specs/CHANGELOG.md` consignant cette réconciliation documentaire (date, résumé, référence)
- [x] T033 Exécuter `scripts/test_check_docs_coherence.sh` et confirmer que tous les tests passent
- [x] T034 Vérifier via `git status` que les fichiers modifiés se limitent à `docs/`, `scripts/check_docs_coherence.sh`, `scripts/test_check_docs_coherence.sh`, `specs/CHANGELOG.md` (T032) et `specs/015-docs-ai-obsidian-sync/` — aucun changement de code applicatif (FR-009)

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Aucun prérequis ; T001-T003 peuvent être réalisés en parallèle.
- **Foundational (Phase 2)**: Dépend de la Phase 1 et bloque les user stories.
- **User Story 1 (Phase 3)**: Dépend de la Phase 2 ; constitue le MVP.
- **User Story 2 (Phase 4)**: Dépend de la Phase 2. Ses tâches de fusion (T019-T020) touchent les mêmes fichiers que les entêtes de fraîcheur ajoutées en US1 (T011-T012) — exécuter après US1 pour éviter un conflit d'édition sur `docs/ENVIRONMENTS.md` et `docs/CORS_CONFIGURATION.md`.
- **User Story 3 (Phase 5)**: Dépend de la Phase 2. Ses tâches d'anonymisation (T023-T028) touchent les mêmes fichiers que US1 (entêtes) et parfois US2 (fusion) — exécuter après US1 et US2 pour les fichiers concernés (`API_V1.md`, `ENVIRONMENTS.md`, `CORS_CONFIGURATION.md`, `INSTALL_PROD_NO_DOCKER.md`, `REDIS_INTEGRATION.md`, `LOGGING.md`).
- **Polish (Phase 6)**: Dépend de toutes les user stories retenues.

### User Story Dependencies

- **US1 (P1)**: Peut démarrer après la fondation ; aucune dépendance à US2 ou US3.
- **US2 (P2)**: Indépendant fonctionnellement de US1, mais séquencé après pour éviter un conflit d'édition sur les fichiers partagés (`ENVIRONMENTS.md`, `CORS_CONFIGURATION.md`).
- **US3 (P3)**: Indépendant fonctionnellement de US1/US2, mais séquencé après pour la même raison (fichiers partagés).

### Parallel Opportunities

- T001-T003 peuvent être réalisés en parallèle.
- T004-T005 peuvent être réalisés en parallèle (fichiers distincts).
- T008-T017 (implémentation US1) peuvent être réalisés en parallèle — 10 fichiers `docs/` distincts, aucune dépendance entre eux.
- T023-T028 (implémentation US3) peuvent être réalisés en parallèle — fichiers distincts.
- T029-T030 peuvent être réalisés en parallèle pendant la finalisation.
- T034 s'exécute en dernier, après T032 (entrée `specs/CHANGELOG.md`), pour que la vérification `git status` reflète l'état final des fichiers modifiés.

## Implementation Strategy

1. **MVP**: terminer US1 pour que chaque fichier de `docs/` soit exact, daté et sans conflit Git.
2. **Incrément 2**: terminer US2 pour un point d'entrée unique et des liens internes fiables, sans doublon.
3. **Incrément 3**: terminer US3 pour que chaque comportement documenté ait un exemple concret anonymisé.
4. Ne pas modifier le code applicatif dans cette feature ; toute correction runtime découverte doit devenir une feature séparée.
