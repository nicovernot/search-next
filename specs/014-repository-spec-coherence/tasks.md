---

description: "Task list for repository and specification coherence"
---

# Tasks: Cohérence du dépôt et des artefacts de spécification

**Input**: Design documents from `specs/014-repository-spec-coherence/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`

**Scope**: Documentation et contrôle de cohérence uniquement ; aucun comportement applicatif ne doit être modifié.

## Phase 1: Setup

**Purpose**: Préparer l'inventaire et les références de la feature.

- [x] T001 [P] Documenter la liste des fichiers de référence et leur rôle dans `specs/014-repository-spec-coherence/plan.md`
- [x] T002 [P] Définir les valeurs de statut canoniques et les règles d'exception dans `specs/014-repository-spec-coherence/research.md`
- [x] T003 [P] Vérifier que les fichiers centraux `specs/README.md`, `specs/PLANNING.md`, `specs/CHANGELOG.md` et `docs/ARCHITECTURE.md` sont inclus dans le périmètre d'audit dans `specs/014-repository-spec-coherence/quickstart.md`

## Phase 2: Foundational

**Purpose**: Mettre en place le modèle de contrôle commun avant toute réconciliation documentaire.

- [x] T004 Définir la structure des enregistrements `SpecRecord`, `TaskRecord` et `ValidationEvidence` dans `specs/014-repository-spec-coherence/data-model.md`
- [x] T005 [P] Créer le contrôle non destructif d'inventaire des artefacts dans `scripts/check_spec_coherence.sh`
- [x] T006 [P] Ajouter les cas de sortie et codes d'erreur attendus du contrôle dans `scripts/test_check_spec_coherence.sh`
- [x] T007 Vérifier que le contrôle ne modifie aucun fichier et documenter cette garantie dans `specs/014-repository-spec-coherence/quickstart.md`

**Checkpoint**: L'inventaire des specs, artefacts et tâches peut être exécuté sans modifier le dépôt.

## Phase 3: User Story 1 - Lire un statut fiable (Priority: P1) 🎯 MVP

**Goal**: Fournir un catalogue et un planning dont les statuts correspondent aux specs et aux preuves disponibles.

**Independent Test**: Exécuter le contrôle sur toutes les specs et vérifier qu'un statut livré, partiel ou backlog est identique dans le catalogue, le planning et la spec correspondante.

### Tests for User Story 1

- [x] T008 [P] [US1] Ajouter un test de détection des statuts divergents dans `scripts/test_check_spec_coherence.sh`
- [x] T009 [P] [US1] Ajouter un test de détection des titres différents pour un même identifiant dans `scripts/test_check_spec_coherence.sh`

### Implementation for User Story 1

- [x] T010 [US1] Réconcilier les statuts et titres du catalogue avec les specs courantes dans `specs/README.md`
- [x] T011 [US1] Réconcilier l'ordre, les dépendances et les statuts de livraison dans `specs/PLANNING.md`
- [x] T012 [US1] Corriger les références de numérotation logging obsolètes dans `docs/ARCHITECTURE.md`
- [x] T013 [US1] Corriger les métadonnées de branche et d'état dans `specs/011-auth-ldap-sso/spec.md`
- [x] T014 [US1] Supprimer les prérequis déjà livrés et clarifier les phases restantes dans `specs/012-semantic-search-api-platform/plan.md`

**Checkpoint**: Les statuts courants sont lisibles depuis une source centrale et les écarts historiques sont explicitement contextualisés.

## Phase 4: User Story 2 - Exécuter le workflow Spec Kit (Priority: P1)

**Goal**: Garantir que chaque spec active possède les artefacts nécessaires et que les tâches ouvertes sont actionnables.

**Independent Test**: Exécuter le contrôle de prérequis Spec Kit pour chaque feature active et vérifier que les artefacts manquants sont soit créés, soit documentés comme exception.

### Tests for User Story 2

- [x] T015 [P] [US2] Ajouter un test de détection des artefacts `spec.md`, `plan.md` ou `tasks.md` manquants dans `scripts/test_check_spec_coherence.sh`
- [x] T016 [P] [US2] Ajouter un test de détection des tâches cochées sans preuve dans `scripts/test_check_spec_coherence.sh`

### Implementation for User Story 2

- [x] T017 [US2] Générer la liste de tâches manquante pour la spec logging dans `specs/013-logging-strategy/tasks.md`
- [x] T018 [US2] Réconcilier les cases et les blocages des tâches URL sync dans `specs/004-url-sync/tasks.md`
- [x] T019 [US2] Réconcilier les cases et les blocages des tâches permissions dans `specs/005-permissions/tasks.md`
- [x] T020 [US2] Réconcilier les cases et les blocages des tâches qualité dans `specs/008-code-quality-solid/tasks.md`
- [x] T021 [US2] Réconcilier les cases et les blocages des tâches DRY/KISS/YAGNI dans `specs/009-dry-kiss-yagni/tasks.md`
- [x] T022 [US2] Réconcilier les tâches ouvertes restantes de naming dans `specs/010-naming-intention-result/tasks.md`

**Checkpoint**: Les specs actives sont planifiables et le workflow Spec Kit ne rencontre plus d'artefact manquant non documenté.

## Phase 5: User Story 3 - Suivre les changements documentaires (Priority: P2)

**Goal**: Rendre chaque correction de cohérence traçable par une date, une raison et une preuve.

**Independent Test**: Vérifier que chaque correction importante apparaît dans le changelog avec son ancien contexte, son nouvel état et sa validation.

### Tests for User Story 3

- [x] T023 [P] [US3] Ajouter un test de présence des références de validation dans `scripts/test_check_spec_coherence.sh`
- [x] T024 [P] [US3] Ajouter un test de distinction entre validation échouée, non exécutée et bloquée dans `scripts/test_check_spec_coherence.sh`

### Implementation for User Story 3

- [x] T025 [US3] Enregistrer la réconciliation des statuts et artefacts dans `specs/CHANGELOG.md`
- [x] T026 [US3] Ajouter les commandes et résultats de contrôle reproductibles dans `specs/014-repository-spec-coherence/quickstart.md`
- [x] T027 [US3] Documenter les exceptions historiques de numérotation et de branche dans `specs/014-repository-spec-coherence/research.md`

**Checkpoint**: Les changements documentaires importants sont auditables sans dépendre de la mémoire de l'équipe.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Vérifier la conformité finale et préserver le périmètre documentaire.

- [x] T028 [P] Vérifier les références croisées et les liens Markdown dans `specs/014-repository-spec-coherence/`
- [x] T029 [P] Vérifier l'absence de modification du code applicatif dans `scripts/test_check_spec_coherence.sh`
- [x] T030 Exécuter le contrôle complet et consigner son résultat dans `specs/014-repository-spec-coherence/quickstart.md`
- [x] T031 Vérifier les prérequis Spec Kit sur chaque spec active depuis `scripts/check_spec_coherence.sh`
- [x] T032 Finaliser la checklist de cohérence dans `specs/014-repository-spec-coherence/checklists/requirements.md`

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Aucun prérequis ; T001-T003 peuvent être réalisés en parallèle.
- **Foundational (Phase 2)**: Dépend de la Phase 1 et bloque les user stories.
- **User Story 1 (Phase 3)**: Dépend de la Phase 2 ; constitue le MVP.
- **User Story 2 (Phase 4)**: Dépend de la Phase 2 ; peut commencer après le contrôle d'inventaire, mais ses corrections de tâches doivent suivre US1 pour utiliser les statuts réconciliés.
- **User Story 3 (Phase 5)**: Dépend des corrections US1 et US2 afin de documenter l'état final.
- **Polish (Phase 6)**: Dépend de toutes les user stories retenues.

### User Story Dependencies

- **US1 (P1)**: Peut démarrer après la fondation ; aucune dépendance à US2 ou US3.
- **US2 (P1)**: Dépend de l'inventaire fondamental ; utilise les statuts réconciliés par US1 pour décider quelles tâches restent ouvertes.
- **US3 (P2)**: Dépend de US1 et US2 ; documente leurs décisions et validations.

### Parallel Opportunities

- T001-T003 peuvent être réalisés en parallèle.
- T005-T006 peuvent être réalisés en parallèle après T004.
- T008-T009 peuvent être réalisés en parallèle avant T010-T014.
- T015-T016 peuvent être réalisés en parallèle avant T017-T022.
- T023-T024 peuvent être réalisés en parallèle avant T025-T027.
- T028-T029 peuvent être réalisés en parallèle pendant la finalisation.

## Implementation Strategy

1. **MVP**: terminer US1 pour rétablir des statuts fiables dans le catalogue, le planning et les specs prioritaires.
2. **Incrément 2**: terminer US2 pour rendre le workflow Spec Kit exécutable sur toutes les specs actives.
3. **Incrément 3**: terminer US3 pour rendre les corrections traçables et reproductibles.
4. Ne pas modifier le code applicatif dans cette feature ; toute correction runtime découverte doit devenir une feature séparée.
