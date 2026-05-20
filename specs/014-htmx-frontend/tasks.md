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

## Phase 5 — URL sync + CSS production ✅

- [x] URL sync HTMX : `hx-push-url="true"` + SSR lit les params → URLs partageables et bookmarkables
- [x] Historique navigateur : `hx-history-elt` sur `<main>`, `htmx.config.historyCacheSize = 20`, `refreshOnHistoryMiss = true`
- [x] Dark mode sans Alpine.js — JS vanilla, persist `localStorage`, pas de flash FOUC
- [x] Migration CSS Tailwind v3 → v4 (`@import "tailwindcss"`, `@source`, `@theme inline`)
- [x] Design tokens alignés avec `front/app/globals.css` (variables HSL, dark mode, fonts)
- [x] CDN Tailwind remplacé par CSS buildé servi depuis `/static/hypermedia/styles.css` (15 Ko minifié)
- [x] `make build-hypermedia-css` / `make watch-hypermedia-css` opérationnels
- [ ] Tests Playwright : back/forward ≥ 5 étapes, URL partageable restaure l'état

## Phase 6 — Alignement visuel React ✅

- [x] **P1 — Design system (classes sémantiques)** : classes hardcodées migrées vers tokens (`bg-background`, `text-foreground`, `border-border`, `bg-card`, `text-muted-foreground`, `bg-muted`, `bg-primary`, `text-primary`, `bg-primary/10`)
- [x] **P2 — Header glassmorphique** : `glass premium-shadow rounded-2xl mx-2 mt-2 sticky top-2 z-10`, logo `Open`+`Edition` bicolore
- [x] **P3 — Formulaire premium** : `glass rounded-3xl premium-shadow p-2`, bouton `bg-highlight text-white`, input transparent
- [x] **P4 — Panel facettes premium** : `bg-card border-border rounded-3xl p-6 sticky top-24 premium-shadow`
- [x] **P5 — Cartes résultats** : `bg-card border-border rounded-xl hover:border-primary/50`
- [x] **P6 — Empty state** : 🔍 + `border-dashed border-border rounded-xl p-12 text-center`
- [x] **Fix double facettes** : OOB conditionnel (`oob=True` fragment, `oob=False` SSR) — plus de double rendu `id="facets"`
- [x] **Autocomplete dans facettes** : input de filtre JS inline (`filterFacet`) affiché si > 8 buckets, `max-h-60 overflow-y-auto` sur la liste, `data-facet-value` sur chaque `<li>`
- [x] **Build CSS** : `@utility glass/premium-shadow/animate-fade-in` + `@custom-variant dark` — 15.3 Ko
- [ ] Vérifier que `make test` reste vert après migration

## Vérification qualité

- [ ] `grep -r "solr\|SolrClient\|SearchBuilder" app/api/v1/hypermedia/` → zéro résultat (logique dans les Services)
- [ ] `make test` vert après ajout des tests hypermedia
- [ ] `front/tests/hypermedia.spec.ts` vert en CI (navigateur Playwright requis)
- [x] CSS buildé < 20 Ko minifié (actuellement 15 Ko)
