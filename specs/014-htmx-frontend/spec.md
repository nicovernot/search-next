# Spec 014 — Frontend hypermedia (HTMX + Alpine.js)

**Feature Branch**: `feat/htmx-alpine-frontend`
**Status**: ⚪ Expérimental / Phase 2 livrée

## Overview

Frontend alternatif basé sur le stack **HATH** (HTMX, Alpine.js, Tailwind, Hypermedia). Interface ultra-rapide sans hydratation React, servie depuis FastAPI via Jinja2. Module nommé `hypermedia` dans le code.

## Contexte

Le stack Next.js est puissant mais complexe. Ce frontend explore la simplicité (KISS) : état géré côté serveur, mises à jour partielles du DOM via HTMX, interactivité locale légère via Alpine.js.

## Conventions de nommage

- **Module Python** : `app/api/v1/hypermedia/` — endpoints retournant du HTML.
- **Templates** : `app/templates/hypermedia/` — Jinja2 organisé en `layouts/`, `pages/`, `fragments/`.
- **Assets** : `app/static/hypermedia/` — CSS buildé, JS minifié.
- **Route prefix** : `/api/v1/hypermedia/`.
- **StaticFiles mount** : `/static/hypermedia`.
- **Tag OpenAPI** : `hypermedia`.
- **IDs HTML** : convention `#search-results`, `#search-form`, `#loading` — nommage intention→résultat (spec 010).
- **Fichiers Playwright** : `front/tests/hypermedia.spec.ts`.

## Requirements

### Functional Requirements

- **FR-001**: Recherche fluide avec mise à jour partielle des résultats via HTMX.
- **FR-002**: Gestion de la pagination via `hx-target` / `hx-push-url`.
- **FR-003**: Feedback immédiat via `htmx-indicator`.
- **FR-004**: Thème visuel avec dark mode Alpine.js.
- **FR-005**: Authentification via cookies sécurisés (JWT → cookie HttpOnly).
- **FR-006**: Gestion des erreurs Solr affichée en HTML (pas de 500).

### Technical Constraints

- **TC-001**: Templates Jinja2 dans `search_api_solr/app/templates/hypermedia/`.
- **TC-002**: Assets statiques dans `search_api_solr/app/static/hypermedia/`.
- **TC-003**: Zéro duplication de logique Solr — utilisation exclusive des `Services` Python.
- **TC-004**: Tailwind via build process (CDN uniquement en dev).
- **TC-005**: Sécurité CSRF via headers HTMX.
- **TC-006**: Nommage IDs/attributs HTMX : convention `#search-results`, `hx-target`, `hx-push-url`.

## Success Criteria

- **SC-001**: FCP < 400ms sur la page de recherche.
- **SC-002**: Bundle JS < 50 kb (HTMX + Alpine.js minifiés).
- **SC-003**: Zéro logique Solr hors des `Services` Python.
- **SC-004**: URL synchronisée avec l'état de recherche (`hx-push-url`).
- **SC-005**: `make test` vert (tests pytest `test_hypermedia.py`).
- **SC-006**: Tests Playwright `hypermedia.spec.ts` verts en CI.

## Architecture

```
search_api_solr/
├── app/
│   ├── api/v1/hypermedia/        # Router — endpoints HTML
│   │   ├── __init__.py
│   │   └── router.py
│   ├── templates/hypermedia/
│   │   ├── layouts/base.j2       # Layout commun
│   │   ├── pages/search.j2       # Page de recherche SSR
│   │   └── fragments/results.j2  # Fragment résultats HTMX
│   └── static/hypermedia/        # CSS buildé, Alpine/HTMX minifiés

front/tests/
└── hypermedia.spec.ts            # Tests Playwright E2E
```

## Outils de débogage

- `htmx.logAll()` activé si `settings.environment != "production"`.
- **Alpine DevTools** : inspection de l'état local.
- **FastAPI Radar** : vue d'ensemble des routes (commenté dans `main.py`).
