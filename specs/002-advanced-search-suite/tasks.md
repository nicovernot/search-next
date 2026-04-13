# Implementation Tasks: Advanced Search Suite

## Phase 1: Infrastructure Backend & Base de données
- [x] Ajouter `postgres` dans le docker-compose.
- [x] Installer les dépendances dans `search_api_solr` (SQLAlchemy, psycopg, PyJWT, passlib, bcrypt).
- [x] Modèles : `User` et `SavedSearch`. Migrations avec Alembic.
- [x] Endpoints `/auth/register` et `/auth/login`.

## Phase 2: Autocomplétion
- [x] Endpoint `/suggest` côté backend (FastAPI -> Solr).
- [x] Composant React `AutocompleteInput` avec debounce et gestion du clavier.
- [x] Intégration dans la barre de recherche principale.

## Phase 3: Construction Avancée de Requête
- [x] Backend : parser récursif `query_logic_parser.py` qui convertit la structure JSON de la requête logique en chaîne Solr valide (AND/OR/NOT récursif, opérateurs contains/begins_with/ends_with).
- [x] Frontend : Installation de `react-querybuilder` (v8.14.4).
- [x] Frontend : Composant `AdvancedQueryBuilder.tsx` avec toggle simple/avancé et champs configurés.

## Phase 4: Traductions
- [x] Migration vers `next-intl` v4 avec routing `[locale]` (URLs `/fr/`, `/en/`, etc.).
- [x] Fichiers messages ICU dans `/messages/{fr,en,es,it,pt,de}.json` — 6 langues complètes.
- [x] Suppression de `I18nContext` custom et du hook `useTranslations` maison.
- [x] `LanguageSelector` utilise `useLocale()` + `useRouter()` de `next-intl/navigation`.
- [x] Tous les composants migrent vers `useTranslations()` de `next-intl`.
- [x] Middleware `middleware.ts` + `i18n/routing.ts` + `i18n/request.ts` + `i18n/navigation.ts`.

## Phase 5: Recherches Sauvegardées
- [x] Backend : `app/api/v1/saved_searches.py` — GET/POST/DELETE `/saved-searches` avec auth JWT.
- [x] Backend : `app/core/dependencies.py` — `get_current_user` (décodage JWT Bearer).
- [x] Backend : router enregistré dans `main.py`.
- [x] Frontend : `AuthContext.tsx` — login/register/logout avec `localStorage`.
- [x] Frontend : `AuthModal.tsx` — deux boutons header distincts (Connexion/S'inscrire), modal avec onglets, show/hide password, lien switch mode, data-testid.
- [x] Frontend : `SavedSearchesPanel.tsx` — dropdown Mes Recherches + bouton Sauvegarder + data-testid.
- [x] Frontend : intégration dans le header (`[locale]/page.tsx`).

## Tests E2E (Playwright)
- [x] `tests/auth.spec.ts` — 10 tests : inscription, connexion, déconnexion, erreurs, persistance session.
- [x] `tests/saved-searches.spec.ts` — 8 tests : sauvegarder, charger, supprimer, persistance après reload.

## Correctifs post-livraison (2026-04-13)

### CORS
- [x] Ajout de `http://localhost:3003` et `http://127.0.0.1:3003` dans `CORS_ORIGINS` (`search_api_solr/.env` et `.env.development`).
- [x] Correction de `API_BASE_URL` (8000→8003) et `FRONTEND_URL` (3000→3003) dans `.env.shared`.

### Pagination & Filtres — auto-refresh
- [x] `useEffect` dans `SearchContext` qui re-déclenche la recherche quand `filters` ou `pagination.from/size` changent (si recherche active).

### SearchContext — refactor "latest ref" (stale closure)
- [x] `latestRef` (useRef) synchronisé après chaque render — `executeSearch` / `runSearch` lisent toujours les valeurs à jour.
- [x] `executeSearch` a des deps vides (référence stable) — plus de problème de stale closure.
- [x] Ajout de `loadSearch(data: SavedSearchData)` dans le context : restaure l'état ET lance la recherche de façon atomique en patchant `latestRef` immédiatement.

### Recherches sauvegardées — rechargement
- [x] `SavedSearchesPanel.handleLoad` remplacé par `loadSearch(s.query_json)` + `setOpen(false)` — plus de `setTimeout`, plus de stale closure.
- [x] `AdvancedQueryBuilder.handleSearch` simplifié : `setLogicalQuery` déjà synced via `onQueryChange`, `executeSearch()` lit depuis `latestRef`.

### i18n — chaînes hardcodées extraites
- [x] `heroTitle`, `heroSubtitle` extraits de `page.tsx`.
- [x] `removeFilter`, `noResultsHint`, `searchHint` extraits de `ResultsList.tsx`.
- [x] `qb_fieldTitle`, `qb_fieldAuthor`, `qb_fieldFullText`, `qb_fieldKeywords` extraits de `AdvancedQueryBuilder.tsx`.
- [x] `qb_addGroup`, `qb_addRule`, `qb_remove`, `qb_logic`, `qb_field`, `qb_operator`, `qb_value` extraits des `translations` du QueryBuilder.
- [x] `noFacetResults`, `showMore`, `showLess` utilisés dans `FacetGroup.tsx`.
- [x] 67 clés synchronisées dans les 6 fichiers (FR/EN/ES/DE/IT/PT).

### Correctifs UI/Auth/i18n (2026-04-13 — round 2)
- [x] **Tailwind v4 colors** : ajout d'un bloc `@theme inline` dans `globals.css` mappant `--card`, `--background`, `--border`, etc. vers `--color-*` → `bg-card`, `bg-secondary`, `text-foreground`, `border-border` fonctionnent enfin.
- [x] **JWT expiry** : `ACCESS_TOKEN_EXPIRE_MINUTES=1440` ajouté dans `search_api_solr/.env` et `.env.development` (évite les 401 après 30 min).
- [x] **Warnings traductions facettes** : remplacement de `t(key as any)` par une table de mapping `FACET_I18N` dans `Facets.tsx` et `ResultsList.tsx`; ajout de `facet_date` et `facet_subscribers` (69 clés × 6 langues).

### Correctifs recherches sauvegardées — exécution réelle (2026-04-13 — round 3)
- [x] **AdvancedQueryBuilder sync** : ajout d'un `useEffect` qui synchronise l'état local `query` (RuleGroupType) avec `logicalQuery` du context quand `loadSearch` restaure une recherche avancée.
- [x] **data-testid** : `data-testid="results-list"` ajouté sur le container dans `ResultsList.tsx`; `data-testid="result-item"` ajouté sur `<article>` dans `ResultItem.tsx`.
- [x] **Tests Playwright** : `waitForResults()` helper vérifiant la présence d'au moins un `result-item`; test "charger" étendu pour vérifier que les résultats s'affichent; nouveau test "charger depuis reload" vérifiant la persistance + exécution après rechargement de page.
