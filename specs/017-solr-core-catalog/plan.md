# Implementation Plan: Catalogue des cores Solr et intégration du core « calenda »

**Branch**: `017-solr-core-catalog` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/017-solr-core-catalog/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Ajouter un endpoint public `GET /api/v1/cores` qui projette en lecture le `SolrCoreRegistry` existant (feature 016) — noms des cores configurés et lequel est le défaut — pour rendre le paramètre `core` (déjà fonctionnel sur `/search`, `/suggest`, `/permissions`) découvrable sans lecture de la configuration serveur. Étendre `docs/ARCHITECTURE.md` avec la procédure pas-à-pas d'ajout d'un core. Appliquer cette procédure pour enregistrer un second core, `calenda`, pointant vers `https://solrslave-sec.labocleo.org/solr/calenda`, sans changer le core par défaut (`documents`).

## Technical Context

**Language/Version**: Python 3.10, FastAPI (backend `search_api_solr`) — aucun changement de version

**Primary Dependencies**: FastAPI, Pydantic v2 — aucune nouvelle dépendance externe

**Storage**: Fichier JSON supplémentaire sous `app/services/solr_cores/` (`calenda.json`), même mécanisme que la feature 016 ; aucune base de données

**Testing**: pytest (`search_api_solr/tests/`), sur le modèle de `test_solr_core_registry.py` et `test_api_v1.py`

**Target Platform**: Service backend FastAPI existant (Linux, Docker) — aucun changement de plateforme

**Project Type**: Extension d'un service web existant (backend uniquement ; le frontend consomme le nouvel endpoint mais aucun changement frontend n'est requis par cette feature)

**Performance Goals**: Le nouvel endpoint lit un dict déjà en mémoire (`SolrCoreRegistry.cores`) — pas de nouvel appel réseau ni de nouvelle E/S disque par requête

**Constraints**: Aucune modification du comportement des endpoints existants (`/search`, `/suggest`, `/permissions`) ni du core par défaut (FR-006) ; `base_url` ne doit pas être exposée dans la réponse publique (research.md Décision 2)

**Scale/Scope**: Un nouvel endpoint, un nouveau fichier de configuration de core (`calenda.json`), extension de deux fichiers de documentation ; aucun changement de schéma de données existant

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

* **I. Search Quality**: PASS — aucune requête de recherche modifiée ; le nouvel endpoint est un endpoint de configuration, pas de recherche.
* **II. User-Centered Experience**: PASS — améliore la découvrabilité côté API/documentation ; aucune interface utilisateur modifiée par cette feature.
* **III. Evidence-Driven Delivery**: PASS — chaque décision (research.md) référence le fichier:ligne du code déjà audité (`solr_core_registry.py`, `dependencies.py`, `main.py`) ; tests prévus pour l'endpoint et pour le chargement du core `calenda`.
* **IV. Secure Access**: PASS — endpoint en lecture seule sur une configuration non sensible (noms de cores) ; `base_url` explicitement exclue de la réponse (research.md Décision 2) ; aucun changement d'autorisation par core (hérité, inchangé de la feature 016).
* **V. Simplicity and Explicit Change**: PASS — réutilise entièrement le registre et le patron de fichiers JSON déjà en place ; aucun nouveau service ni nouvelle abstraction, un seul routeur de plus sur le modèle des routeurs `v1` existants.

No constitution violations identified. Gate status: PASS.

## Project Structure

### Documentation (this feature)

```text
specs/017-solr-core-catalog/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── get-cores.md
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
search_api_solr/app/
├── services/
│   └── solr_cores/
│       └── calenda.json              # NOUVEAU — second core, default: false
├── models/
│   ├── core_models.py                 # NOUVEAU — SolrCoreInfo, SolrCoresResponse
│   └── __init__.py                    # MODIFIÉ — exporte les nouveaux modèles
├── api/
│   └── v1/
│       └── cores.py                   # NOUVEAU — GET /api/v1/cores
└── main.py                             # MODIFIÉ — inclut cores_router dans les public_router

search_api_solr/tests/
├── test_solr_core_registry.py          # MODIFIÉ — cas avec deux cores (documents + calenda)
└── test_cores_endpoint.py              # NOUVEAU — contrat GET /api/v1/cores

docs/
├── API_V1.md                           # MODIFIÉ — nouvelle entrée d'endpoint + exemple
└── ARCHITECTURE.md                     # MODIFIÉ — procédure pas-à-pas d'ajout d'un core, section existante étendue
```

**Structure Decision**: Toute la feature reste dans `search_api_solr/` (backend existant) plus `docs/` ; aucun nouveau service, aucun changement frontend. Le nouveau routeur `cores.py` est un pair direct de `facets.py`/`permissions.py` déjà présents dans `app/api/v1/`, et `calenda.json` est un pair direct de `documents.json` dans `solr_cores/`.

## Research Summary

Décisions détaillées avec justification (fichier:ligne du code audité) dans [research.md](research.md) :

1. Endpoint dédié `GET /api/v1/cores`, plutôt que de coupler la liste des cores à `/facets/config` ou à un header de réponse.
2. Réponse `{"cores": [{"name", "is_default"}], "default_core"}` — sans `base_url` (information d'infrastructure interne, non exposée).
3. `calenda.json` ajouté au répertoire `solr_cores/` existant, avec `default: false`, sans aucun changement de code (le mécanisme de chargement de la feature 016 le prend en charge tel quel).
4. Procédure d'intégration documentée en étendant la section « Configuration Solr multi-core » déjà présente dans `docs/ARCHITECTURE.md`, plutôt qu'un nouveau document séparé.

## Constitution Check (post-design)

Re-vérifié après la Phase 1 (data-model.md, contracts/, quickstart.md) : la conception ajoute un seul routeur en lecture seule et un seul fichier de configuration, tous deux calqués sur des patrons déjà validés par la feature 016. Aucune nouvelle dépendance externe, aucune nouvelle donnée sensible exposée (`base_url` explicitement exclue), aucun changement de surface d'autorisation. Les 5 principes restent PASS sans changement par rapport à la vérification initiale ci-dessus.

## Complexity Tracking

No constitution violations or additional complexity require justification.
