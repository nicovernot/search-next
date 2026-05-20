# Plan technique — Spec 014 Frontend hypermedia

## Phase 1 — Socle ✅

1. ✅ Ajouter `jinja2` et `python-multipart` aux dépendances (`requirements.txt`).
2. ✅ Créer `app/templates/hypermedia/` et `app/static/hypermedia/`.
3. ✅ Router `app/api/v1/hypermedia/router.py` avec `Jinja2Templates` monté localement.
4. ✅ `base.j2` : DOCTYPE, Tailwind CDN dev, HTMX, Alpine.js, dark mode, structure commune.
5. [ ] Configurer le build Tailwind autonome (séparé du front Next.js).

## Phase 2 — Recherche de base ✅

6. ✅ Endpoint `GET /api/v1/hypermedia/` — page d'accueil SSR.
7. ✅ Endpoint `GET /api/v1/hypermedia/search` — page complète SSR avec paramètres `q` et `page`.
8. ✅ Endpoint `GET /api/v1/hypermedia/search/results` — fragment HTMX seul.
9. ✅ `pages/search.j2` — formulaire + zone résultats + indicateur de chargement.
10. ✅ `fragments/results.j2` — liste paginée + gestion erreurs + état vide.
11. ✅ Tests pytest `test_hypermedia.py` — HTML, non-JSON, erreurs Solr gracieuses.
12. ✅ Tests Playwright `hypermedia.spec.ts` — recherche, push-url, pagination, dark mode, back/forward.

## Phase 3 — Facettes et interactivité ✅

13. ✅ Fragment `facets.j2` — liste de facettes cliquables, OOB swap depuis `results.j2`.
14. ✅ Middleware de log headers `HX-*` (conditionnel dev).
15. ✅ Endpoint `GET /api/v1/hypermedia/search/facets` — fragment facettes seul.
16. ✅ Support `?filter=id:value` multi-valeur sur tous les endpoints.

## Phase 4 — Sécurité et qualité ✅

17. ✅ `auth.py` — JWT → Cookie HttpOnly (`htmx_session`) : `POST /auth/session`, `DELETE /auth/session`.
18. ✅ `deps.py` — `get_optional_hypermedia_user()` + `htmx_redirect_if_not_htmx()`.
19. ✅ Accessibilité : skip-to-content, `aria-busy` sur résultats, `aria-live`, labels ARIA complets.
20. ✅ Build Tailwind autonome — `search_api_solr/tailwind-hypermedia/` + `make build-hypermedia-css`.
21. ✅ Tests auth session (POST sans token, token invalide, DELETE).

## Phase 5 — URL sync et CSS production ✅

22. ✅ URL sync : `hx-push-url="true"` (SSR lit les params → URLs partageables), `hx-history-elt` sur `<main>`, `htmx.config.historyCacheSize = 20`.
23. ✅ Migration CSS Tailwind v3 → v4 : `@import "tailwindcss"`, `@source`, `@theme inline` dans `input.css`. Plus de `tailwind.config.js`.
24. ✅ Design tokens portés depuis `front/app/globals.css` : variables HSL, dark/light, fonts, glassmorphism, animations.
25. ✅ CDN Tailwind supprimé de `base.j2` → CSS buildé `styles.css` (15 Ko) servi par FastAPI `StaticFiles`.
26. ✅ Dark mode : JS vanilla (localStorage, toggle icône, pas de flash FOUC), Alpine.js retiré du layout.

## Décisions techniques

- **Nommage module** : `hypermedia` (décrit le type de réponse HTTP, indépendant de la lib HTMX).
- **Mount point** : `Jinja2Templates` et `StaticFiles` dans le router, pas dans `main.py`.
- **Erreurs Solr** : attrapées dans `_execute_search()`, retournées comme contexte `error` dans le template — pas de 500.
- **Auth** : cookie `HttpOnly` depuis JWT existant — pas de nouveau système.
- **Tests pytest** : `dependency_overrides` pour mocker `get_search_service`.
