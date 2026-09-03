---

description: "Task list for Solr multi-core configuration support"
---

# Tasks: Configuration Solr multi-core

**Input**: Design documents from `specs/016-solr-multi-core-support/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/core-parameter.md`, `quickstart.md`

**Scope**: Backend `search_api_solr/` uniquement (voir Assumptions de la spec) ; aucune création de core côté Solr, aucun pipeline d'indexation, aucun contrôle d'accès par core (FR-009, FR-011).

## Phase 1: Setup

**Purpose**: Vérifier que l'audit de `research.md` reflète toujours l'état actuel du code avant de modifier.

- [x] T001 [P] Confirmer que les références fichier:ligne citées dans `specs/016-solr-multi-core-support/research.md` (settings.py:44, dependencies.py, search_service.py:233-248, docs_permissions_client.py) correspondent toujours au code actuel
- [x] T002 [P] Créer le dossier vide `search_api_solr/app/services/solr_cores/`

## Phase 2: Foundational

**Purpose**: Mettre en place le registre de cores partagé, bloquant pour toutes les user stories.

- [x] T003 [P] Ajouter `SolrCoreNotFoundError` à `search_api_solr/app/core/exceptions.py`, aux côtés de `SolrTimeoutError`/`SolrInvalidQueryError`/`SolrUnavailableError`
- [x] T004 Créer `SolrCoreRegistry` dans `search_api_solr/app/services/solr_core_registry.py` : chargement des fichiers `*.json` de `solr_cores/` (sur le modèle de `facet_config.py::load_facet_config_from_json`), validation au chargement (liste vide → échec, nombre de `default: true` ≠ 1 → échec), méthode `resolve(core: str | None) -> SolrCoreDefinition` levant `SolrCoreNotFoundError` si le nom est inconnu
- [x] T005 [P] Créer `search_api_solr/app/services/solr_cores/documents.json` avec `{"base_url": "<valeur actuelle de settings.solr_base_url>", "default": true}` (migration — FR-005)
- [x] T006 Ajouter `get_solr_core_registry()` à `search_api_solr/app/api/dependencies.py` et l'injecter comme source unique de vérité pour la résolution de core
- [x] T007 Tests unitaires du registre dans `search_api_solr/tests/test_solr_core_registry.py` : liste vide échoue au chargement, deux `default: true` échoue, `resolve(None)` retourne le core par défaut, `resolve("documents")` retourne la bonne définition, `resolve("inconnu")` lève `SolrCoreNotFoundError`

**Checkpoint**: Le registre charge la configuration migrée (`documents.json`) et valide correctement avant qu'aucun endpoint ne l'utilise.

## Phase 3: User Story 1 - Ajouter un core Solr par configuration (Priority: P1) 🎯 MVP

**Goal**: Un opérateur peut ajouter un core via un fichier de configuration et le rendre interrogeable sans changement de code.

**Independent Test**: Ajouter un fichier JSON de core dans `solr_cores/`, redémarrer le service, et vérifier qu'une recherche `POST /api/v1/search` avec `"core": "<nom>"` renvoie des résultats issus de ce core.

### Implementation for User Story 1

- [x] T008 [US1] Ajouter le champ optionnel `core: str | None` à `SearchRequest` dans `search_api_solr/app/models/search_models.py`
- [x] T009 [US1] Refactorer `SearchBuilder.__init__` pour recevoir un `SolrCoreRegistry` (au lieu d'un `solr_base_url` figé) et résoudre le core dans `build_search_url(request)` à partir de `request.core` (`search_api_solr/app/services/search_builder.py`)
- [x] T010 [US1] Mettre à jour `get_search_builder()`/`get_solr_client()` dans `search_api_solr/app/api/dependencies.py` pour construire `SearchBuilder` à partir du `SolrCoreRegistry` injecté (T006)
- [x] T011 [US1] Mapper `SolrCoreNotFoundError` → HTTP 404 dans `_raise_public_search_error` de `search_api_solr/app/api/v1/search.py`
- [x] T012 [US1] Ajouter le paramètre de requête optionnel `core` à l'alias `GET /api/v1/search` dans `search_api_solr/app/api/v1/search.py`
- [x] T013 [US1] Tests dans `search_api_solr/tests/test_search_builder.py` (mise à jour de la signature `SearchBuilder`) et un test d'intégration prouvant qu'un core ajouté via un nouveau fichier JSON est interrogeable via `core=<nom>` sur `/search`

**Checkpoint**: Ajouter un fichier de configuration rend un nouveau core réellement interrogeable via `/search` — livrable MVP indépendant.

## Phase 4: User Story 2 - Cibler un core précis pour une recherche (Priority: P1)

**Goal**: Le même mécanisme de ciblage (explicite / défaut / erreur si inconnu) est cohérent sur `/search`, `/suggest` et `/permissions` — plus aucune résolution de core divergente entre services (FR-006).

**Independent Test**: Envoyer des recherches identiques sur `/search`, `/suggest` et `/permissions` en ne faisant varier que `core`, et vérifier que chacune cible le bon core, retombe sur le défaut quand `core` est omis, et échoue en 404 pour un core inconnu — de façon identique sur les trois endpoints.

### Implementation for User Story 2

- [x] T014 [US2] Ajouter le paramètre `core: str | None` à `SuggestService.fetch_autocomplete_suggestions()` (résolution via `SolrCoreRegistry`) ; intercepter `SolrCoreNotFoundError` **avant** le `except Exception` générique existant (qui dégrade vers `{"suggestions": []}`) pour la re-lever ; ajouter le paramètre de requête `core` et un bloc `try/except` (actuellement absent) sur `GET /api/v1/suggest` mappant `SolrCoreNotFoundError` → 404 (`search_api_solr/app/services/search_service.py`, `search_api_solr/app/api/v1/suggest.py`)
- [x] T015 [US2] Corriger `PermissionsService.get_document_permissions()` pour cesser de contourner l'injection de dépendances : utiliser le `SolrCoreRegistry` injecté au lieu de relire `SOLR_CONFIG` et d'instancier son propre client (`search_api_solr/app/services/search_service.py:233-248`)
- [x] T016 [US2] Adapter `search_api_solr/app/services/docs_permissions_client.py` pour recevoir une URL déjà résolue (via T015) plutôt que de lire `SOLR_CONFIG` directement
- [x] T017 [US2] Dans `PermissionsService.get_document_permissions()`, intercepter `SolrCoreNotFoundError` **avant** le `except Exception` générique existant (qui retourne aujourd'hui `DocsPermissionsResponse(..., info={"error": ...})` en HTTP 200) pour la re-lever ; dans `GET /api/v1/permissions`, faire de même avant le `except Exception` de l'endpoint, et mapper vers HTTP 404 — sans modifier la dégradation gracieuse existante pour les autres erreurs (`search_api_solr/app/services/search_service.py:223-256`, `search_api_solr/app/api/v1/permissions.py`)
- [x] T018 [US2] Tests : comportement par défaut et erreur core-inconnu (404) cohérents sur `/search`, `/suggest`, `/permissions` ; test confirmant que `PermissionsService` ne lit plus `SOLR_CONFIG["base_url"]` directement (`search_api_solr/tests/test_search_service.py` ou équivalent existant)

**Checkpoint**: Les trois endpoints qui interrogent Solr résolvent le core de façon strictement identique — livrable indépendant testable.

## Phase 5: User Story 3 - Ne rien casser sur le comportement actuel (Priority: P2)

**Goal**: Prouver que l'introduction du multi-core ne modifie aucun comportement pour les appelants existants.

**Independent Test**: Rejouer des recherches existantes sans `core` avant/après et vérifier des résultats identiques, y compris pour les vérifications de permissions.

### Implementation for User Story 3

- [x] T019 [P] [US3] Test de non-régression : une requête `/search`, `/suggest` et `/permissions` sans `core` produit une réponse strictement identique à la même requête avec `core=documents` explicite (`search_api_solr/tests/test_regression_default_core.py`)
- [x] T020 [P] [US3] Test confirmant que `SearchBuilder`, `SuggestService` et `PermissionsService` reçoivent bien la même instance de `SolrCoreRegistry` injectée (pas de résolution indépendante) — extension de `search_api_solr/tests/test_solr_core_registry.py` ou fichier de test dédié à l'intégration DI

**Checkpoint**: Aucune divergence de comportement par défaut détectée — livrable indépendant, filet de sécurité pour la production.

## Phase 6: User Story 4 - Découvrir les cores configurés (Priority: P3)

**Goal**: Un opérateur peut déterminer la liste des cores configurés sans lire le code source.

**Independent Test**: Consulter les logs de démarrage (ou la configuration elle-même) et vérifier qu'ils listent exactement les cores actifs et celui par défaut.

### Implementation for User Story 4

- [x] T021 [US4] Journaliser, au démarrage, la liste des cores chargés par `SolrCoreRegistry` (noms + core par défaut) via le logger structuré existant (`search_api_solr/app/services/solr_core_registry.py` ou `search_api_solr/app/main.py`)
- [x] T022 [US4] Test vérifiant que le registre expose la liste complète des cores et le nom du core par défaut pour une configuration à plusieurs cores (`search_api_solr/tests/test_solr_core_registry.py`)

**Checkpoint**: La configuration active est diagnostiquable sans lire le code — livrable indépendant.

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Nettoyage, documentation, vérification finale.

- [x] T023 [P] Supprimer la configuration Solr parallèle non utilisée identifiée dans `research.md` (`app/core/config.py::SOLR_CORE_NAME`, export `VALIDATED_SOLR_COLLECTION` de `env_validation.py`) désormais remplacée par `SolrCoreRegistry`
- [x] T024 [P] Mettre à jour `docs/API_V1.md` et `docs/ARCHITECTURE.md` pour documenter le paramètre `core` (cohérent avec la feature 015 — entête « Dernière vérification » à jour)
- [x] T025 Vérifier via `git status`/`git diff` que seuls des fichiers de `search_api_solr/` (et `docs/`, `specs/016-...` pour la documentation) ont été modifiés — aucune création de core ni pipeline d'indexation introduit (FR-009)
- [x] T026 Exécuter `cd search_api_solr && pytest` en intégralité et confirmer une suite verte
- [x] T027 Exécuter les 9 scénarios de `specs/016-solr-multi-core-support/quickstart.md` et consigner le résultat dans ce même fichier

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Aucun prérequis ; T001-T002 peuvent être réalisés en parallèle.
- **Foundational (Phase 2)**: Dépend de la Phase 1 et bloque toutes les user stories.
- **User Story 1 (Phase 3)**: Dépend de la Phase 2 ; constitue le MVP.
- **User Story 2 (Phase 4)**: Dépend de la Phase 2 et réutilise le mécanisme introduit en US1 (`SearchRequest.core`, mapping d'erreur) pour `/suggest` et `/permissions` — exécuter après US1.
- **User Story 3 (Phase 5)**: Dépend des Phases 2-4 (a besoin des trois endpoints déjà branchés sur le registre pour comparer le comportement par défaut).
- **User Story 4 (Phase 6)**: Dépend de la Phase 2 uniquement (le registre suffit) ; peut être fait en parallèle de US2/US3 si nécessaire.
- **Polish (Phase 7)**: Dépend de toutes les user stories retenues.

### User Story Dependencies

- **US1 (P1)**: Dépend de la fondation ; aucune dépendance à US2/US3/US4.
- **US2 (P1)**: Réutilise le mécanisme de résolution de core introduit par US1 (mêmes types `SolrCoreNotFoundError`/`SearchRequest.core`) et l'étend à `/suggest`/`/permissions` — séquencé après US1 par réutilisation directe, pas par contrainte de fichiers partagés.
- **US3 (P2)**: Vérifie le résultat combiné de US1+US2 ; ne peut pas être testée avant qu'elles soient terminées.
- **US4 (P3)**: Indépendante de US2/US3 — ne dépend que du registre (Phase 2).

### Parallel Opportunities

- T001-T002 peuvent être réalisés en parallèle.
- T003 et T005 peuvent être réalisés en parallèle (fichiers distincts, aucune dépendance entre eux).
- T019-T020 (US3) peuvent être réalisés en parallèle.
- T023-T024 peuvent être réalisés en parallèle pendant la finalisation.
- US4 (T021-T022) peut être développée en parallèle de US2/US3 une fois la Phase 2 terminée, si plusieurs personnes travaillent sur la feature.

## Implementation Strategy

1. **MVP**: terminer US1 pour qu'un core ajouté par configuration soit réellement interrogeable via `/search`.
2. **Incrément 2**: terminer US2 pour que `/suggest` et `/permissions` suivent la même règle, et corriger le contournement de DI de `PermissionsService`.
3. **Incrément 3**: terminer US3 pour prouver l'absence de régression avant toute mise en production.
4. **Incrément 4**: terminer US4 pour l'observabilité opérationnelle.
5. Ne pas créer de core côté Solr ni de pipeline d'indexation dans cette feature (FR-009) ; ne pas introduire de contrôle d'accès par core (FR-011).
