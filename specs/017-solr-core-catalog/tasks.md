---

description: "Task list for Solr core catalog endpoint, integration docs, and calenda core"
---

# Tasks: Catalogue des cores Solr et intégration du core « calenda »

**Input**: Design documents from `specs/017-solr-core-catalog/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/get-cores.md`, `quickstart.md`

**Scope**: Backend `search_api_solr/` et `docs/` uniquement. S'appuie sur `SolrCoreRegistry` (feature 016) sans le modifier ; `base_url` ne doit jamais apparaître dans une réponse API (research.md Décision 2).

## Phase 1: Setup

**Purpose**: Vérifier que les références fichier:ligne citées dans `research.md`/`plan.md` reflètent toujours l'état actuel du code avant de modifier.

- [X] T001 [P] Confirmer que `search_api_solr/app/services/solr_core_registry.py:88-104` (propriétés `cores`/`default_core_name`, méthode `resolve`), `search_api_solr/app/api/dependencies.py:16-21` (`get_solr_core_registry`) et `search_api_solr/app/main.py:102-106` (boucle `include_router`) correspondent toujours au code actuel

## Phase 2: Foundational

**Purpose**: Prérequis bloquant partagé par les trois user stories.

Aucune tâche bloquante supplémentaire : le registre `SolrCoreRegistry` et son mécanisme de chargement (feature 016) couvrent déjà le besoin commun aux trois stories. Chacune est additive et indépendante sur cette base existante — passer directement à la Phase 3.

**Checkpoint**: Aucun prérequis à valider — les user stories peuvent démarrer immédiatement après la Phase 1.

## Phase 3: User Story 1 - Lister les cores disponibles (Priority: P1) 🎯 MVP

**Goal**: Un appelant de l'API découvre en un seul appel la liste des cores configurés et lequel est le défaut.

**Independent Test**: Appeler `GET /api/v1/cores` et vérifier que la réponse contient `documents` avec `is_default: true`, sans avoir touché à la configuration.

### Implementation for User Story 1

- [X] T002 [P] [US1] Créer `SolrCoreInfo` (`name: str`, `is_default: bool`) et `SolrCoresResponse` (`cores: list[SolrCoreInfo]`, `default_core: str`) dans `search_api_solr/app/models/core_models.py`, sur le modèle de `search_api_solr/app/models/permissions_models.py` — pas de champ `base_url` (research.md Décision 2)
- [X] T003 [US1] Exporter `SolrCoreInfo` et `SolrCoresResponse` depuis `search_api_solr/app/models/__init__.py` (dépend de T002)
- [X] T004 [US1] Créer `search_api_solr/app/api/v1/cores.py` : `router = APIRouter(tags=["cores"])`, endpoint `GET /cores` sans paramètre, `registry: SolrCoreRegistry = Depends(get_solr_core_registry)`, construit `SolrCoresResponse` à partir de `registry.cores` et `registry.default_core_name`, sur le modèle de `search_api_solr/app/api/v1/facets.py` (dépend de T003)
- [X] T005 [US1] Inclure `cores_router` dans `search_api_solr/app/main.py`, dans la boucle `for public_router in (search_router, suggest_router, facets_router, permissions_router)` (`main.py:104`) — l'ajouter à ce tuple (dépend de T004)
- [X] T006 [US1] Tests dans `search_api_solr/tests/test_cores_endpoint.py` (nouveau, sur le modèle de `search_api_solr/tests/test_api_v1.py`) : `GET /api/v1/cores` renvoie `200`, contient `documents` avec `is_default: true`, `default_core == "documents"`, et la réponse sérialisée ne contient aucune clé `base_url` (dépend de T005)

**Checkpoint**: `GET /api/v1/cores` fonctionne et reflète fidèlement le registre actuel (un seul core, `documents`) — livrable MVP indépendant.

---

## Phase 4: User Story 2 - Documenter l'ajout d'un core Solr (Priority: P2)

**Goal**: Un opérateur ajoute un nouveau core Solr en suivant uniquement la documentation, sans lire le code source.

**Independent Test**: Suivre uniquement `docs/ARCHITECTURE.md` pour ajouter un core de test, vérifier qu'il devient interrogeable via `/suggest?core=<nom>`, puis le retirer.

### Implementation for User Story 2

- [X] T007 [P] [US2] Étendre la section « Configuration Solr multi-core » de `docs/ARCHITECTURE.md` (actuellement lignes 195-204) avec une procédure pas-à-pas : créer `search_api_solr/app/services/solr_cores/<nom>.json` (`{"base_url": "...", "default": true|false}`), redémarrer le service backend, vérifier via `GET /api/v1/cores` (US1) et via une requête `core=<nom>` sur `/search`/`/suggest`/`/permissions`
- [X] T008 [P] [US2] Ajouter `GET /api/v1/cores` à la liste des endpoints publics et à la section « Ciblage d'un core Solr (`core`) » de `docs/API_V1.md`, avec un exemple `curl`, cohérent avec `contracts/get-cores.md`
- [X] T009 [US2] Valider la procédure documentée en T007 : créer temporairement `search_api_solr/app/services/solr_cores/test-core.json`, redémarrer, vérifier son apparition dans `GET /api/v1/cores` et son interrogeabilité via `/suggest?q=test&core=test-core`, puis supprimer ce fichier (validation manuelle — `quickstart.md` Scénario 2, aucun fichier livré) (dépend de T005, T007)

**Checkpoint**: La procédure documentée est prouvée reproductible de bout en bout — livrable indépendant.

---

## Phase 5: User Story 3 - Enregistrer le core « calenda » (Priority: P3)

**Goal**: Le core `calenda` est interrogeable via l'API, sans devenir le core par défaut.

**Independent Test**: Après ajout de `calenda.json`, `GET /api/v1/cores` liste `calenda` avec `is_default: false`, `default_core` reste `"documents"`, et `/suggest?core=calenda` cible la collection calendrier.

### Implementation for User Story 3

- [X] T010 [US3] Créer `search_api_solr/app/services/solr_cores/calenda.json` : `{"base_url": "https://solrslave-sec.labocleo.org/solr/calenda", "default": false}`
- [X] T011 [P] [US3] Étendre `search_api_solr/tests/test_solr_core_registry.py` : avec `documents.json` + `calenda.json` présents, `resolve("calenda")` retourne la bonne `base_url`, `default_core_name` reste `"documents"`, `cores` contient les deux entrées (dépend de T010)
- [X] T012 [P] [US3] Test de non-régression dans `search_api_solr/tests/test_api_v1.py` (ou fichier dédié `test_regression_default_core.py` s'il existe déjà) : une requête `/suggest` ou `/search` sans `core` cible toujours `documents` après l'ajout de `calenda` (dépend de T010)
- [X] T013 [US3] Étendre `search_api_solr/tests/test_cores_endpoint.py` (T006) : `GET /api/v1/cores` liste `calenda` avec `is_default: false` une fois `calenda.json` présent (dépend de T006, T010)

**Checkpoint**: `calenda` enregistré, interrogeable via `core=calenda`, visible dans le catalogue, aucune régression du comportement par défaut.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Cohérence documentaire et vérification finale.

- [X] T014 [P] Mettre à jour l'en-tête « Dernière vérification » de `docs/API_V1.md` et la mention de `docs/ARCHITECTURE.md` (section « Configuration Solr multi-core ») pour référencer la feature `017-solr-core-catalog`
- [X] T015 Exécuter `cd search_api_solr && pytest` en intégralité et confirmer une suite verte
- [X] T016 Exécuter les 3 scénarios de `specs/017-solr-core-catalog/quickstart.md` et consigner le résultat dans ce même fichier

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Aucun prérequis.
- **Foundational (Phase 2)**: Vide pour cette feature (voir note ci-dessus) — ne bloque rien.
- **User Story 1 (Phase 3)**: Dépend de la Phase 1 ; constitue le MVP.
- **User Story 2 (Phase 4)**: Dépend de la Phase 1 ; T007/T008 sont indépendantes de US1, mais T009 (validation) référence `GET /api/v1/cores` — exécuter après T005 (US1).
- **User Story 3 (Phase 5)**: T010 (fichier `calenda.json`) est indépendant de US1/US2 ; T013 dépend de T006 (US1) pour vérifier l'apparition de `calenda` dans le catalogue.
- **Polish (Phase 6)**: Dépend de toutes les user stories retenues.

### User Story Dependencies

- **US1 (P1)**: Aucune dépendance à US2/US3.
- **US2 (P2)**: Indépendante en implémentation (T007/T008) ; sa validation complète (T009) réutilise l'endpoint livré par US1.
- **US3 (P3)**: Le fichier de configuration (T010) est indépendant ; sa vérification complète via le catalogue (T013) dépend de US1.

### Parallel Opportunities

- T002 (US1) peut démarrer immédiatement après T001.
- T007 et T008 (US2) peuvent être réalisées en parallèle (fichiers distincts).
- T011 et T012 (US3) peuvent être réalisés en parallèle une fois T010 fait.
- T014 peut être fait en parallèle de T015/T016 pendant la finalisation.

## Parallel Example: User Story 1

```bash
# T002 (modèles) puis, une fois livré, T003/T004 s'enchaînent séquentiellement (même fichier de dépendances)
Task: "Créer SolrCoreInfo/SolrCoresResponse dans search_api_solr/app/models/core_models.py"
```

## Implementation Strategy

### MVP First (User Story 1)

1. Compléter Phase 1 (vérification des références).
2. Compléter Phase 3 (US1) : `GET /api/v1/cores` fonctionnel sur la configuration actuelle (un seul core).
3. **STOP et VALIDER** : `curl <API_BASE_URL>/api/v1/cores` renvoie `documents` comme défaut.

### Incremental Delivery

1. US1 → catalogue des cores disponible (MVP).
2. US2 → procédure d'ajout d'un core documentée et prouvée reproductible.
3. US3 → `calenda` enregistré et visible dans le catalogue, sans régression du défaut.
4. Polish → documentation à jour, suite de tests verte, `quickstart.md` rejoué.
