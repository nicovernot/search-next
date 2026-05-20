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

## Phase 6 — Alignement visuel React ✅

27. ✅ Migrer les classes Tailwind hardcodées vers les tokens sémantiques du design system (`bg-background`, `text-foreground`, `border-border`, `bg-card`, `text-muted-foreground`, `bg-muted`, `bg-primary`, `text-primary`, `bg-primary/10`, `bg-highlight`) dans les 4 templates.
28. ✅ Header glassmorphique : `glass premium-shadow rounded-2xl mx-2 mt-2 sticky top-2 z-10`, logo bicolore `Open` + `Edition`.
29. ✅ Formulaire premium : wrapper `glass rounded-3xl premium-shadow p-2`, input transparent, bouton `bg-highlight text-white`.
30. ✅ Panel facettes : `bg-card border-border rounded-3xl p-6 sticky top-24 premium-shadow` sur `<aside>`.
31. ✅ Cartes résultats : `bg-card border-border rounded-xl` + hover `hover:border-primary/50 transition-colors`.
32. ✅ Empty state amélioré : emoji 🔍 + `border-dashed border-border rounded-xl p-12 text-center`.
33. ✅ Rebuild CSS : `cd tailwind-hypermedia && npm run build` pour que Tailwind v4 scanne les nouvelles classes et les génère.

## Phase 7 — Parité visuelle totale React ✅

34. ✅ Fix titre : `doc.titre or doc.title or doc.naked_titre` — résout le bug "(sans titre)" systématique (Solr retourne `titre`, pas `title`).
35. ✅ Badges row sur chaque carte : platform (pulse dot animé), type (highlight), year (muted), access rights (openAccess/restrictedAccess/embargoedAccess → couleurs green/orange/blue).
36. ✅ Cartes redesignées : `rounded-2xl p-6 hover:border-highlight/50 hover:shadow-lg hover:shadow-highlight/5 hover:-translate-y-1 group transition-all duration-300`.
37. ✅ Titre avec font-serif, `group-hover:text-highlight`, `decoration-highlight/30 underline-offset-4`.
38. ✅ Auteurs avec séparateur ` · `, max 3 + "et al.".
39. ✅ Description : `naked_resume or overview` tronquée à 280 chars, `text-foreground/80 leading-relaxed`.
40. ✅ Lien "Voir le document" : `text-highlight font-bold` + flèche SVG avec `group-hover:translate-x-1`.
41. ✅ Autocomplete HTMX : endpoint `GET /api/v1/hypermedia/suggest` → `fragments/suggest.j2` (dropdown positionnée) ; input avec `hx-trigger="input changed delay:300ms"` + `aria-autocomplete="list"`.
42. ✅ Animate-fade-in sur chaque `<li>` résultat.
43. ✅ CSS rebuild : 22 Ko (toutes nouvelles classes incluses).

## Décisions techniques

- **Nommage module** : `hypermedia` (décrit le type de réponse HTTP, indépendant de la lib HTMX).
- **Mount point** : `Jinja2Templates` et `StaticFiles` dans le router, pas dans `main.py`.
- **Erreurs Solr** : attrapées dans `_execute_search()`, retournées comme contexte `error` dans le template — pas de 500.
- **Auth** : cookie `HttpOnly` depuis JWT existant — pas de nouveau système.
- **Tests pytest** : `dependency_overrides` pour mocker `get_search_service`.
