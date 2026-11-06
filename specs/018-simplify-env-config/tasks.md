---

description: "Task list template for feature implementation"
---

# Tasks: Simplification de la configuration d'environnement

**Input**: Design documents from `/specs/018-simplify-env-config/`

**Prerequisites**: [plan.md](./plan.md) (required), [spec.md](./spec.md) (required for user stories), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

**Tests**: Non explicitement demandés dans la spec (feature d'outillage/configuration) — une seule tâche de couverture pytest ciblée est incluse en Polish pour les nouvelles règles de validation (FR-009, FR-014), en cohérence avec le principe constitutionnel III (Evidence-Driven Delivery).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Dépôt existant (pas de nouveau projet) : racine du dépôt pour les fichiers `.env.*`, `Makefile`, `docker-compose*.yml` ; `scripts/` pour les scripts d'activation/vérification ; `docs/` et `search_api_solr/` pour la documentation ; `search_api_solr/app/core/` pour la validation backend ; `.github/workflows/` pour la CI. Voir la section *Project Structure* de [plan.md](./plan.md) pour le détail complet.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Préparer le terrain avant de créer les nouveaux fichiers de configuration

- [X] T001 [P] Nettoyer `.gitignore` : retirer les entrées devenues obsolètes `.env.local`, `.env.*.local` et `!.env.example` (le modèle de génération par service et `.env.example` disparaissent avec cette feature) ; conserver `.env` et `*.env`.
- [X] T002 Confirmer et consigner les valeurs de production actuellement manquantes ou héritées à tort de staging — `CORS_ORIGINS`, `LOG_LEVEL`, `RATE_LIMIT`, `CACHE_TTL`, `ACCESS_TOKEN_EXPIRE_MINUTES` (marquées ⚠️ dans `specs/018-simplify-env-config/contracts/env-schema.md`) — en ajoutant les valeurs retenues directement dans ce fichier.

**Checkpoint**: Terrain prêt — les valeurs nécessaires à la rédaction de `.env.production` sont connues.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Les 3 fichiers modèles et la validation backend qui conditionnent les trois user stories

**⚠️ CRITICAL**: Aucune user story ne peut être implémentée avant la fin de cette phase

- [X] T003 [P] Créer `.env.development` (racine du dépôt) en fusionnant le contenu actuel de `.env.shared` + `.env.development`, fichier autonome et complet, conforme au tableau `specs/018-simplify-env-config/contracts/env-schema.md`.
- [X] T004 [P] Créer `.env.test` (racine du dépôt) en fusionnant `.env.shared` + `.env.test`, en comblant l'écart `SOLR_BASE_URL` identifié dans `specs/018-simplify-env-config/contracts/env-schema.md`.
- [X] T005 [P] Créer `.env.production` (racine du dépôt) en fusionnant `.env.shared` + `.env.production`, avec des secrets placeholders explicites (`change-me-in-production`) et les valeurs confirmées en T002, conforme à `specs/018-simplify-env-config/contracts/env-schema.md`.
- [X] T006 [P] Mettre à jour `search_api_solr/app/core/env_validation.py` : faire pointer `Config.env_file` sur le seul `.env` (au lieu de `['.env.shared', '.env.local', '.env']`), ajouter un validateur qui rejette toute valeur d'`ENVIRONMENT`/`NODE_ENV` hors `{development, test, production}` (FR-009), et bloquer le démarrage si `ENVIRONMENT=production` alors que `SECRET_KEY`/`JWT_SECRET`/`SESSION_SECRET` vaut encore `change-me-in-production` (FR-010, FR-014).

**Checkpoint**: Les 3 fichiers modèles et la validation existent — l'implémentation des user stories peut commencer.

---

## Phase 3: User Story 1 - Un développeur configure son environnement en un seul endroit (Priority: P1) 🎯 MVP

**Goal**: Un développeur peut configurer et faire basculer n'importe lequel des 3 environnements en ne touchant qu'un seul fichier actif à la fois, sans couche de génération ni source cachée capable de la contredire.

**Independent Test**: Cloner le dépôt, exécuter `scripts/use-env.sh development` puis `make dev` sans autre édition ; répéter avec `test` puis `production` et constater que `.env` reflète intégralement le nouvel environnement à chaque bascule (voir quickstart.md, Scénarios 1 et 2).

### Implementation for User Story 1

- [X] T007 [P] [US1] Créer `scripts/use-env.sh` conforme à `specs/018-simplify-env-config/contracts/cli-contract.md` : valider l'argument contre `{development, test, production}`, copier `.env.<environment>` vers `.env` (racine), créer/vérifier les symlinks `front/.env -> ../.env` et `search_api_solr/.env -> ../.env`, afficher un résumé, codes de sortie conformes au contrat.
- [X] T008 [P] [US1] Mettre à jour `docker-compose.yml` : faire lire directement le `.env` racine activé par les services `api` et `frontend` (au lieu de `search_api_solr/.env.local` généré), supprimer la substitution `${VAR}` dupliquée devenue inutile.
- [X] T009 [P] [US1] Mettre à jour `Makefile` : les cibles `dev`/`test`/`prod`/`set-dev`/`set-test`/`set-prod`/`run-dev`/`run-prod`/`sync-env`/`configure-env` appellent désormais `scripts/use-env.sh <environment>` ; retirer `staging`, `staging-build`, `staging-down`, `set-staging` et la variable `STAGING_COMPOSE`. (dépend de T007)
- [X] T010 [P] [US1] Mettre à jour `.github/workflows/ci.yml` : retirer toute référence à staging, aligner l'étape de configuration d'environnement sur `scripts/use-env.sh test`. (dépend de T007)
- [X] T011 [US1] Supprimer les fichiers devenus obsolètes : `.env.shared`, `.env.staging`, `.env.example`, `docker-compose.staging.yml`, `scripts/sync_env.sh`, `scripts/configure_env.sh`. (dépend de T003-T005, T007-T010)
- [X] T012 [US1] Exécuter et consigner les résultats des Scénarios 1, 2 et 5 de `specs/018-simplify-env-config/quickstart.md` (bootstrap à un seul fichier, bascule d'environnement, rejet d'une valeur invalide). (dépend de T011)

**Checkpoint**: US1 pleinement fonctionnelle et testable indépendamment — MVP livrable : un développeur configure et bascule d'environnement via un seul fichier, staging a disparu.

---

## Phase 4: User Story 2 - Un développeur retrouve toutes les variables et leur rôle dans une documentation unique (Priority: P2)

**Goal**: Un développeur trouve, dans un unique document, la description, le format et la valeur par environnement de chaque variable — y compris `CORS_ORIGINS` — sans lire le code.

**Independent Test**: Chercher dans `docs/ENVIRONMENTS.md` comment configurer les origines CORS et obtenir une réponse complète sans consulter une autre source (voir quickstart.md, Scénario 3).

### Implementation for User Story 2

- [X] T013 [P] [US2] Réécrire `docs/ENVIRONMENTS.md` comme document de référence unique : structure des 3 fichiers modèles, mécanisme d'activation par symlinks, règles de précédence, tableau complet des variables (repris de `specs/018-simplify-env-config/contracts/env-schema.md`), section CORS, dépannage mis à jour pour le nouveau modèle.
- [X] T014 [US2] Supprimer `search_api_solr/ENVIRONMENTS.md` (doublon obsolète de `docs/ENVIRONMENTS.md`). (dépend de T013)
- [X] T015 [P] [US2] Mettre à jour les documents qui référencent l'ancien modèle ou staging : `docs/CORS_CONFIGURATION.md`, `docs/REDIS_INTEGRATION.md`, `docs/LOGGING.md`, `docs/RECOMMENDATIONS.md`, `search_api_solr/DOCKER.md`.
- [X] T016 [P] [US2] Ajouter une entrée dans `docs/CHANGELOG.md` documentant la simplification de la configuration d'environnement.
- [X] T017 [US2] Exécuter et consigner le résultat du Scénario 3 de `specs/018-simplify-env-config/quickstart.md` (réponse CORS trouvée uniquement dans `docs/ENVIRONMENTS.md`). (dépend de T013)

**Checkpoint**: US1 + US2 fonctionnelles — un nouveau développeur est autonome via la seule documentation.

---

## Phase 5: User Story 3 - Un développeur vérifie que Docker applique réellement la configuration attendue (Priority: P3)

**Goal**: Un développeur confirme, service par service, que la configuration effectivement appliquée dans les conteneurs Docker correspond au fichier actif — sans session de debug manuelle.

**Independent Test**: Démarrer les conteneurs pour un environnement donné, exécuter `scripts/verify_env_docker.sh` et obtenir une confirmation explicite ; modifier une variable de shell pour simuler l'incident de debug initial et constater que le script le détecte (voir quickstart.md, Scénarios 4 et 4bis).

### Implementation for User Story 3

- [X] T018 [P] [US3] Créer `scripts/verify_env_docker.sh` conforme à `specs/018-simplify-env-config/contracts/cli-contract.md` : comparer `ENVIRONMENT`, `CORS_ORIGINS`, `NEXT_PUBLIC_API_URL`, `SOLR_URL`, `SOLR_BASE_URL`, `SOLR_COLLECTION` entre le `.env` actif et chaque conteneur via `docker exec <service> printenv`, produire un tableau `DockerServiceCheck`, code de sortie non-nul en cas d'écart, avertissement sur l'inlining Next.js au build pour les `NEXT_PUBLIC_*` en production.
- [X] T019 [US3] Ajouter la cible `env-verify` au `Makefile`, appelant `scripts/verify_env_docker.sh`. (dépend de T018)
- [X] T020 [US3] Documenter la procédure de vérification et la cible `make env-verify` dans `docs/ENVIRONMENTS.md`. (dépend de T013, T018)
- [X] T021 [P] [US3] Exécuter et consigner les résultats des Scénarios 4 et 4bis de `specs/018-simplify-env-config/quickstart.md` (vérification positive, puis détection de la régression rejouée). (dépend de T018)

**Checkpoint**: Les 3 user stories sont fonctionnelles indépendamment — feature complète.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Couverture automatisée, nettoyage des scripts annexes, non-régression globale

- [X] T022 [P] Ajouter une couverture pytest dans `search_api_solr/tests/` pour les nouvelles règles de `env_validation.py` : rejet d'une valeur `ENVIRONMENT` invalide et blocage au démarrage sur un secret placeholder en production (FR-009, FR-014).
- [X] T023 [P] Mettre à jour `scripts/check_env_setup.sh` : remplacer `REQUIRED_FILES` (qui référence encore `.env.shared`, `.env.staging`, `.env.example`, `docker-compose.staging.yml`) par le nouveau modèle à 3 fichiers.
- [X] T024 Exécuter la non-régression complète du Scénario 7 de `specs/018-simplify-env-config/quickstart.md` (`scripts/use-env.sh test && make test && make test-front`) et consigner le résultat.
- [X] T025 [P] Exécuter et consigner le Scénario 6 de `specs/018-simplify-env-config/quickstart.md` (démarrage bloqué tant qu'un secret de production reste au placeholder) contre `docker-compose.prod.yml`.
- [X] T026 [P] Ajouter une note de suivi dans `specs/PLANNING.md` pour l'amendement de gouvernance en attente (retrait de la mention "staging" dans la section *Product Constraints* de `.specify/memory/constitution.md`, signalé comme point de vigilance dans `plan.md`).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Aucune dépendance — démarre immédiatement.
- **Foundational (Phase 2)**: Dépend de la fin du Setup (T002 pour T005) — BLOQUE toutes les user stories.
- **User Stories (Phase 3+)**: Dépendent toutes de la fin de la phase Foundational.
  - US1 (P1) peut démarrer dès la fin de Foundational.
  - US2 (P2) peut démarrer dès la fin de Foundational (peut être rédigée en parallèle de la fin d'US1, mais référence son mécanisme).
  - US3 (P3) peut démarrer dès la fin de Foundational (son script est indépendant ; sa documentation dépend d'US2).
- **Polish (Phase 6)**: Dépend des user stories désirées étant complètes.

### User Story Dependencies

- **User Story 1 (P1)**: Aucune dépendance sur les autres stories — c'est le socle (MVP).
- **User Story 2 (P2)**: Documente le mécanisme livré par US1 ; peut être rédigée en parallèle mais sa validation finale (T017) suppose US1 stable.
- **User Story 3 (P3)**: Le script de vérification (T018) est indépendant d'US1/US2 sur le plan technique, mais compare contre les fichiers livrés en Foundational et s'intègre à la documentation d'US2 (T020).

### Within Each User Story

- Scripts/fichiers de configuration avant intégration Makefile/CI.
- Intégration Makefile/CI avant suppression des anciens fichiers.
- Implémentation avant validation des scénarios quickstart.

### Parallel Opportunities

- T001 et T002 (Setup) sont indépendants.
- T003, T004, T005, T006 (Foundational) touchent 4 fichiers différents — parallélisables.
- T007, T008 (US1) sont indépendants entre eux ; T009, T010 dépendent uniquement de T007 et sont indépendants l'une de l'autre.
- T013, T015, T016 (US2) touchent des fichiers différents — parallélisables.
- T018 (US3) est indépendant de T013-T017 sur le plan technique.
- T022, T023, T025, T026 (Polish) touchent des fichiers différents — parallélisables.

---

## Parallel Example: Phase 2 (Foundational)

```bash
# Lancer en parallèle les 4 tâches fondatrices (fichiers indépendants) :
Task: "Créer .env.development (racine) en fusionnant .env.shared + .env.development"
Task: "Créer .env.test (racine) en fusionnant .env.shared + .env.test"
Task: "Créer .env.production (racine) en fusionnant .env.shared + .env.production"
Task: "Mettre à jour search_api_solr/app/core/env_validation.py (validation ENVIRONMENT + placeholder)"
```

## Parallel Example: User Story 1

```bash
Task: "Créer scripts/use-env.sh conforme au contrat CLI"
Task: "Mettre à jour docker-compose.yml pour lire .env directement"
# Puis, une fois scripts/use-env.sh livré :
Task: "Mettre à jour Makefile pour appeler scripts/use-env.sh"
Task: "Mettre à jour .github/workflows/ci.yml (retrait staging)"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Terminer la Phase 1 (Setup).
2. Terminer la Phase 2 (Foundational — CRITIQUE, bloque tout).
3. Terminer la Phase 3 (US1).
4. **STOP et VALIDER** : rejouer les Scénarios 1, 2, 5 de quickstart.md.
5. À ce stade, le problème initial (fichiers de config dispersés, sources cachées contradictoires) est résolu — livrable démontrable même sans US2/US3.

### Incremental Delivery

1. Setup + Foundational → socle prêt.
2. US1 → validation indépendante → MVP livrable (résout directement l'incident de debug ayant motivé la feature).
3. US2 → validation indépendante → documentation de référence livrée.
4. US3 → validation indépendante → vérification Docker outillée, plus besoin de debug manuel `docker exec printenv`.
5. Polish → couverture automatisée + non-régression globale + suivi de l'amendement constitutionnel.

---

## Notes

- [P] tasks = fichiers différents, aucune dépendance non résolue.
- [Story] label trace chaque tâche vers sa user story.
- Aucun test n'est explicitement demandé dans la spec ; T022 ajoute néanmoins une couverture ciblée sur les nouvelles règles de validation critiques pour la sécurité (FR-009, FR-014), conformément au principe constitutionnel III.
- Committer après chaque tâche ou groupe logique de tâches.
- S'arrêter à chaque checkpoint pour valider la story indépendamment avant de passer à la suivante.

## Correctif post-implémentation

- [X] T027 Corriger `.dockerignore` : `front/.env` (symlink créé par `scripts/use-env.sh`) était copié dans le contexte de build Docker (le pattern `.env` sans `**/` ne matche qu'à la racine, contrairement à `.gitignore`), cassant `next build` avec `ENOENT: stat '/app/.env'` — trouvé en testant `make build` après implémentation. Ajout de `**/.env` dans `.dockerignore`. Revalidé : `make build` et `make dev` passent, `make env-verify` confirme la configuration.
