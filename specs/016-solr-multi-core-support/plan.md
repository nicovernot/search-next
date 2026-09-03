# Implementation Plan: Configuration Solr multi-core

**Branch**: `016-solr-multi-core-support` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/016-solr-multi-core-support/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Remplacer l'URL Solr unique codée en dur (`settings.solr_base_url`, core `documents`) par un registre de cores nommés, chargé depuis des fichiers JSON (un fichier = un core, sur le modèle déjà utilisé par `facets_json/`), avec un core par défaut désigné. `SearchBuilder`, `SuggestService` et `PermissionsService` — les trois points identifiés comme construisant aujourd'hui une connexion Solr de façon divergente — résolvent le core ciblé (explicite via un paramètre `core`, ou par défaut) à partir de ce registre unique, au lieu de chacun lire `SOLR_CONFIG["base_url"]` indépendamment. Une nouvelle exception `SolrCoreNotFoundError` (HTTP 404) distingue un nom de core inconnu d'un core injoignable (`SolrUnavailableError`, HTTP 503, déjà existant).

## Technical Context

**Language/Version**: Python 3.10, FastAPI (backend `search_api_solr`) — aucun changement de version

**Primary Dependencies**: FastAPI, Pydantic v2, httpx (client Solr existant) — aucune nouvelle dépendance externe requise

**Storage**: Fichiers JSON sous `app/services/solr_cores/` (un fichier par core), sur le modèle de `app/services/facets_json/` déjà en place ; aucune base de données

**Testing**: pytest (`search_api_solr/tests/`), sur le modèle des tests existants de `search_builder.py`/`solr_client.py`/`env_validation.py`

**Target Platform**: Service backend FastAPI existant (Linux, Docker) — aucun changement de plateforme

**Project Type**: Extension d'un service web existant (backend uniquement pour cette feature — voir Assumptions de la spec, le frontend reste hors périmètre)

**Performance Goals**: La résolution du core (lecture d'un dict en mémoire, chargé une fois au démarrage) ne doit ajouter aucune latence perceptible à une recherche — pas de nouvel appel réseau ni de nouvelle E/S disque par requête

**Constraints**: Aucune modification du comportement existant pour les appelants qui ne précisent pas de core (FR-005/SC-002) ; aucune création de core côté Solr ni pipeline d'indexation (FR-009) ; aucun contrôle d'accès par core (FR-011)

**Scale/Scope**: Nombre de cores attendu : de l'ordre de l'unité à quelques dizaines (pas de cas d'usage à grande échelle identifié) ; 3 points de résolution Solr à faire converger (`SearchBuilder`, `SuggestService`, `PermissionsService`) ; 3 endpoints publics à étendre (`/search`, `/suggest`, `/permissions`) ; `/facets/config` explicitement non concerné (voir research.md Décision 4)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

* **I. Search Quality** : PASS — le core par défaut reproduit exactement le comportement de recherche actuel (FR-005) ; aucun changement de pertinence ou de classement.
* **II. User-Centered Experience** : PASS — feature backend/configuration, aucune interface utilisateur modifiée ; le comportement perçu par un appelant existant est inchangé (US3).
* **III. Evidence-Driven Delivery** : PASS — chaque décision technique (research.md) est reliée à un fichier:ligne du code actuel audité ; des tests couvrent la résolution de core, les erreurs (core inconnu/injoignable) et la non-régression du comportement par défaut.
* **IV. Secure Access** : PASS — FR-011 (Clarifications) exclut explicitement tout nouveau périmètre d'autorisation par core ; le contrôle d'accès aux documents (badges de permission) reste inchangé et continue de s'appliquer au niveau document.
* **V. Simplicity and Explicit Change** : PASS — réutilise le patron JSON déjà établi (`facets_json/`) plutôt que d'introduire un nouveau mécanisme de configuration (research.md Décision 1) ; corrige une divergence de résolution Solr déjà présente (`PermissionsService`) au lieu de l'ajouter à la dette.

No constitution violations identified. Gate status: PASS.

## Project Structure

### Documentation (this feature)

```text
specs/016-solr-multi-core-support/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
search_api_solr/app/
├── services/
│   ├── solr_cores/                    # NOUVEAU — un fichier JSON par core (ex. documents.json)
│   ├── solr_core_registry.py          # NOUVEAU — chargement, validation, résolution du core
│   ├── search_builder.py              # MODIFIÉ — résout le core par requête au lieu d'un solr_base_url figé
│   ├── search_service.py              # MODIFIÉ — SuggestService/PermissionsService acceptent core: str | None,
│   │                                   #   PermissionsService cesse de contourner la DI (app/services/search_service.py:233-248)
│   └── docs_permissions_client.py     # MODIFIÉ — reçoit l'URL déjà résolue, ne relit plus SOLR_CONFIG directement
├── core/
│   └── exceptions.py                  # MODIFIÉ — ajout de SolrCoreNotFoundError
├── api/
│   ├── dependencies.py                # MODIFIÉ — construit et injecte SolrCoreRegistry
│   └── v1/
│       ├── search.py                  # MODIFIÉ — mappe SolrCoreNotFoundError → 404
│       ├── suggest.py                 # MODIFIÉ — paramètre de requête `core` optionnel
│       └── permissions.py             # MODIFIÉ — paramètre de requête `core` optionnel
└── models/
    └── search_models.py               # MODIFIÉ — SearchRequest.core: str | None

search_api_solr/tests/
├── test_solr_core_registry.py         # NOUVEAU
├── test_search_builder.py             # MODIFIÉ — cas multi-core ajoutés
└── test_search_service.py             # MODIFIÉ (ou équivalent) — PermissionsService/SuggestService avec core
```

**Structure Decision**: Toute la feature reste dans `search_api_solr/` (backend existant) ; aucun nouveau service, aucun changement frontend. Le nouveau dossier `solr_cores/` est un pair direct de `facets_json/`/`fields_json/` déjà présents dans `app/services/`.

## Research Summary

Les décisions détaillées et leur justification (avec fichier:ligne du code audité) sont dans [research.md](research.md) :

1. Un core = un fichier JSON dans `app/services/solr_cores/`, nommé par le core (`<nom>.json`), exactement un avec `"default": true` — même patron que `facets_json/`.
2. `SearchBuilder` reçoit le registre complet au lieu d'un `solr_base_url` figé ; il résout le core à l'intérieur de `build_search_url(request)` car le corps de la requête n'est pas encore connu au moment où FastAPI construit les dépendances.
3. Nouvelle exception `SolrCoreNotFoundError` (HTTP 404) pour un core inconnu, distincte de `SolrUnavailableError` (HTTP 503, déjà existant) pour un core injoignable.
4. `/search`, `/suggest`, `/permissions` gagnent un `core` optionnel ; `/facets/config` n'est pas concerné (aucune requête Solr, configuration déjà indépendante du core).
5. Migration : un fichier `documents.json` reproduisant l'URL actuelle, marqué par défaut, garantit qu'aucun appelant existant ne voit de changement (US3/FR-005).

## Constitution Check (post-design)

Re-vérifié après la Phase 1 (data-model.md, contracts/, quickstart.md) : la conception introduit un seul nouveau composant (`SolrCoreRegistry`), directement justifié par la correction d'une divergence déjà présente dans le code (`PermissionsService` contournant la DI). Aucune nouvelle dépendance externe, aucune nouvelle donnée sensible, aucun changement de surface d'autorisation. Les 5 principes restent PASS sans changement par rapport à la vérification initiale ci-dessus.

## Complexity Tracking

No constitution violations or additional complexity require justification.
