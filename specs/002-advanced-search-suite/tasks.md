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
- [x] Backend : parser récursif `query_logic_parser.py` qui convertit la structure JSON de la requête logique en chaîne Solr valide (AND/OR/NOT récursif, opérateurs contains/begins_with/ends_with/not_equal/does_not_*).
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
- [x] `tests/auth.spec.ts` — 15 tests : inscription, connexion, déconnexion, erreurs, persistance session.
- [x] `tests/saved-searches.spec.ts` — 12 tests : sauvegarder, charger, supprimer, persistance après reload.
- [x] `tests/search.spec.ts` — 2 tests : chargement page et recherche simple.

## Correctifs post-livraison (2026-04-13)

### CORS
- [x] Ajout de `http://localhost:3003`, `http://127.0.0.1:3003` et `http://0.0.0.0:3003` dans `CORS_ORIGINS` (`.env.shared`, `.env.example`, `search_api_solr/.env.example` et fichiers `.env.local` générés).
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
- [x] 75 clés synchronisées dans les 6 fichiers (FR/EN/ES/DE/IT/PT).

### Correctifs UI/Auth/i18n (2026-04-13 — round 2)
- [x] **Tailwind v4 colors** : ajout d'un bloc `@theme inline` dans `globals.css` mappant `--card`, `--background`, `--border`, etc. vers `--color-*` → `bg-card`, `bg-secondary`, `text-foreground`, `border-border` fonctionnent enfin.
- [x] **JWT expiry** : `ACCESS_TOKEN_EXPIRE_MINUTES=1440` ajouté dans `search_api_solr/.env` et `.env.development` (évite les 401 après 30 min).
- [x] **Warnings traductions facettes** : remplacement de `t(key as any)` par une table de mapping `FACET_I18N` dans `Facets.tsx` et `ResultsList.tsx`; ajout de `facet_date`, `facet_subscribers` et des clés permissions (75 clés × 6 langues).

### Correctifs recherches sauvegardées — exécution réelle (2026-04-13 — round 3)
- [x] **AdvancedQueryBuilder sync** : composant contrôlé par `logicalQuery` du contexte (`query={contextLogicalQuery ?? DEFAULT_QUERY}`), ce qui restaure correctement une recherche avancée chargée.
- [x] **data-testid** : `data-testid="results-list"` ajouté sur le container dans `ResultsList.tsx`; `data-testid="result-item"` ajouté sur `<article>` dans `ResultItem.tsx`.
- [x] **Tests Playwright** : `waitForResults()` helper vérifiant la présence d'au moins un `result-item`; test "charger" étendu pour vérifier que les résultats s'affichent; nouveau test "charger depuis reload" vérifiant la persistance + exécution après rechargement de page.

### Correctifs UX — autocomplete & save (2026-04-13 — round 4)
- [x] **AutocompleteInput portal** : la liste de suggestions est désormais rendue via `createPortal` sur `document.body` avec positionnement `fixed` via `getBoundingClientRect()`. Corrige l'affichage derrière le parent glassmorphism (`backdrop-filter` crée un stacking context qui piège les `z-index` enfants).
- [x] **AutocompleteInput — inputRef** : ajout d'un `ref` sur l'`<input>` + `updateDropdownRect()` appelé sur `onFocus` pour calculer la position dès l'ouverture.
- [x] **SavedSearchesPanel — feedback d'erreur** : ajout d'un état `saveError` + `catch` block dans `handleSave` → message d'erreur rouge visible sous le champ nom si le POST `/saved-searches` échoue (CORS, 401, réseau…). Avant ce correctif, les échecs étaient silencieux.
- [x] **Tests Playwright** : `waitForResults` accepte un paramètre `timeout` (défaut 15 000 ms); `playwright.config.ts` garde `retries: 0` en local et `retries: 2` en CI.
- [x] **search.spec.ts** : `page.goto('/')` → `page.goto('/fr/')` pour contourner la détection Accept-Language de Playwright Chrome qui routait vers `/en/` et ne trouvait pas le texte "Rechercher".

### Correctifs recherche avancée (2026-04-17)
- [x] **query_logic_parser.py — normalisation opérateurs** : table `_OPERATOR_ALIASES` pour mapper camelCase react-querybuilder (`beginsWith`→`begins_with`, `endsWith`→`ends_with`) vers les noms internes.
- [x] **query_logic_parser.py — opérateurs négatifs** : branches `not_equal`, `does_not_contain`, `does_not_begin_with`, `does_not_end_with` produisant des fragments Solr `-field:value`.
- [x] **facet_config.py — champ invalide** : suppression de `"disciplinary_field": "platformIndex_*"` (`platformIndex_*` est un pattern de schéma Solr, non utilisable comme nom de champ dans les requêtes).
- [x] **qb-fields.ts** : suppression de `disciplinary_field` du registre frontend (aligne sur backend).
- [x] **AdvancedQueryBuilder.tsx — opérateurs alignés backend** : prop `operators` expose les 8 opérateurs supportés (`=`, `!=`, `contains`, `doesNotContain`, `beginsWith`, `doesNotBeginWith`, `endsWith`, `doesNotEndWith`); `type="button"` ajouté sur le bouton Rechercher.
- [x] **fields_json/common.json** : `df=naked_titre` (champ tokenisé, boosté à ×8 dans `qf`) au lieu de `df=titre` (champ brut).
- [x] **messages/*.json (6 langues)** : clés `qb_opEquals`, `qb_opContains`, `qb_opBeginsWith`, `qb_opEndsWith` ajoutées ; `qb_fieldKeywords` conservée (clé orpheline inoffensive).

### Correctifs cohérence environnements (2026-04-17)
- [x] **env_validation.py** : renommage `cors_allowed_origins` → `cors_origins` (aligne sur la var `CORS_ORIGINS` de `.env.shared`).
- [x] **settings.py** : suppression du `model_config = SettingsConfigDict(extra='ignore')` doublon (ligne 40 écrasée silencieusement par celui de la fin de classe).
- [x] **.env.test** : remplacement de `REACT_APP_API_URL` (variable CRA, non lue par Next.js) par `NEXT_PUBLIC_API_URL`.
- [x] **entrypoint.sh** : script ajouté — attend PostgreSQL (`pg_isready`) puis applique les migrations Alembic avant de lancer uvicorn ; intégré dans `Dockerfile` et `docker-compose.dev.yml`.
- [x] **CORS_ORIGINS local Docker** : ajout de `http://0.0.0.0:3003` dans la source commune `.env.shared` et les exemples pour couvrir le cas où le navigateur ouvre le frontend via `0.0.0.0`.
