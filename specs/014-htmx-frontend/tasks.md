# Tasks — Spec 014 Frontend hypermedia

## Phase 1 — Socle ✅

- [x] Ajouter `jinja2` et `python-multipart` à `requirements.txt`
- [x] Créer `app/templates/hypermedia/layouts/base.j2` (HTML5, HTMX, Alpine.js, Tailwind CDN dev, dark mode)
- [x] Créer `app/static/hypermedia/` (placeholder pour assets buildés)
- [x] Créer `app/api/v1/hypermedia/__init__.py` + `router.py`
- [x] Inclure le router dans `main.py` sous `/api/v1/hypermedia` + mount `/static/hypermedia`
- [x] Configurer le build Tailwind CSS autonome pour la production

## Phase 2 — Recherche de base ✅

- [x] Endpoint `GET /api/v1/hypermedia/` — page d'accueil SSR
- [x] Endpoint `GET /api/v1/hypermedia/search` — page complète SSR (`q`, `page`)
- [x] Endpoint `GET /api/v1/hypermedia/search/results` — fragment HTMX seul
- [x] `pages/search.j2` — formulaire + `hx-push-url` + indicateur `htmx-indicator`
- [x] `fragments/results.j2` — liste paginée + erreurs Solr + état vide + aria-labels
- [x] Tests pytest `tests/test_hypermedia.py` (home, search, results, erreur Solr)
- [x] Tests Playwright `front/tests/hypermedia.spec.ts` (recherche, URL sync, pagination, dark mode, back/forward)

## Phase 3 — Facettes et interactivité ✅

- [x] Fragment `fragments/facets.j2` — facettes cliquables, filtre actif/inactif, OOB swap via `results.j2`
- [x] Endpoint `GET /api/v1/hypermedia/search/facets` — fragment facettes seul
- [x] Endpoint `GET /api/v1/hypermedia/search` détecte `HX-Request` → renvoie fragment si HTMX
- [x] Support `?filter=identifier:value` (multi) sur tous les endpoints hypermedia
- [x] `pages/search.j2` — layout 2 colonnes (facettes + résultats), filtres actifs affichés, bug `hx-push-url` corrigé
- [x] `app/core/htmx_middleware.py` — log des headers `HX-*` en dev (conditionnel `settings.environment`)
- [x] Middleware monté dans `main.py` hors production
- [x] Tests pytest : HX-Request detection, filter param, facets endpoint, OOB swap

## Phase 4 — Sécurité et production ✅

- [x] Middleware JWT → Cookie `HttpOnly` pour les endpoints authentifiés (`app/api/v1/hypermedia/auth.py`)
- [x] Vérification `HX-Request` header sur les endpoints fragment-only (`deps.py`)
- [x] Audit accessibilité : aria-labels, rôles ARIA, skip-to-content, `aria-busy` sur résultats
- [x] Build Tailwind autonome — `tailwind-hypermedia/` + `make build-hypermedia-css`
- [x] Tests pytest session auth (POST sans token, token invalide, DELETE)

## Vérification qualité

- [ ] `grep -r "solr\|SolrClient\|SearchBuilder" app/api/v1/hypermedia/` → zéro résultat (logique dans les Services)
- [ ] `make test` vert après ajout des tests hypermedia
- [ ] `front/tests/hypermedia.spec.ts` vert en CI (navigateur Playwright requis)
- [ ] Bundle HTMX + Alpine < 50 kb en production
