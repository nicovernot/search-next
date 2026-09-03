# Architecture — OpenEdition Search

**Dernière vérification** : 2026-09-03 — vue d'ensemble de l'architecture technique (frontend, backend, flux de données, dette technique). La branche active se vérifie via `git branch --show-current` (Git reste la référence, pas cette doc).

**État global**: Specs 001–013 livrées ; spec 012 (recherche sémantique + API platform) Phase 1 livrée, Phase 0 ~80 %, Phases 2–5 backlog ; spec 014 (cohérence dépôt) livrée. Détail complet dans `specs/PLANNING.md` et `specs/CHANGELOG.md`.

---

## Stack

| Couche | Technologie | Version |
|--------|-------------|---------|
| Frontend | Next.js (App Router) | 16 |
| UI | React + TypeScript + Tailwind CSS | 19 / 5 / 4 |
| i18n | next-intl | 4 |
| Query builder | react-querybuilder | 8 |
| Backend | FastAPI + Pydantic v2 | — |
| Auth | JWT (HS256) + bcrypt + LDAP3 + OIDC (python-jose) | — |
| Base de données | PostgreSQL 15 | — |
| Cache | Redis 7 | — |
| Moteur de recherche | Apache Solr (distant) | — |
| Tests E2E | Playwright | 1.40 |
| Infra | Docker Compose | — |

---

## Carte de l'architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js 16)                      │
│                                                              │
│  App Router: /[locale]/page.tsx (6 locales)                 │
│                                                              │
│  Contextes (assembleurs — logique dans les hooks):           │
│  ├── AuthProvider    — JWT, session, LDAP, SSO callback     │
│  └── SearchProvider  — assemble 6 hooks SOLID               │
│       ├── useFacetConfig  /facets/config + searchFields     │
│       ├── useSuggestions  /suggest                          │
│       ├── usePermissions  /permissions                      │
│       ├── useSearchState  état local (query/filters/page)   │
│       ├── useSearchApi    executeSearch, loadSearch         │
│       └── useUrlSync      URL ↔ état (back/forward, QB)    │
│                                                              │
│  Hooks utilitaires:                                         │
│  ├── useAuthModal      état modal auth (open/tab)           │
│  ├── useSavedSearches  CRUD recherches sauvegardées         │
│  ├── useClickOutside   fermeture dropdown générique         │
│  ├── useAnchoredPortal positionnement dropdown via portal   │
│  └── useIsClient       SSR guard                            │
│                                                              │
│  Composants:                                                 │
│  ├── SearchBar / AutocompleteInput                          │
│  ├── AdvancedQueryBuilder (react-querybuilder)              │
│  ├── Facets / FacetGroup                                    │
│  ├── ResultsList / ResultItem / Pagination                  │
│  ├── AuthModal (local + LDAP + SSO) / AuthButtons           │
│  └── SavedSearchesPanel                                     │
│                                                              │
│  Lib:                                                        │
│  ├── lib/api.ts        — client API centralisé              │
│  ├── lib/qb-fields.ts  — champs QB depuis /facets/config    │
│  ├── lib/facet-i18n.ts — labels facettes (FACET_I18N)      │
│  ├── lib/platforms.ts  — constantes plateformes OpenEdition │
│  └── lib/storage-keys.ts — clés localStorage centralisées  │
└─────────────────────┬────────────────────────────────────────┘
                      │ fetch() via lib/api.ts — REST JSON
                      │ http://localhost:8003
┌─────────────────────▼────────────────────────────────────────┐
│                    BACKEND (FastAPI)                          │
│                                                              │
│  Endpoints publics versionnés:                              │
│  ├── POST /api/v1/search, GET /api/v1/search                │
│  ├── GET /api/v1/suggest                                    │
│  ├── GET /api/v1/facets/config                              │
│  ├── GET /api/v1/permissions                                │
│  ├── GET /api/v1/openapi.json                               │
│  ├── GET/POST/DELETE /api/v1/saved-searches (JWT)           │
│  │   Aliases racine conservés pendant la transition          │
│  │   (/search, /suggest, /facets/config, /permissions,       │
│  │    /saved-searches)                                      │
│  ├── POST /auth/login, POST /auth/register                  │
│  ├── POST /auth/ldap/login                                  │
│  ├── GET  /auth/sso/login  (redirect → IdP)                │
│  ├── GET  /auth/sso/callback  (émet sso_code court)       │
│  └── GET  /auth/sso/exchange   (échange code → JWT)        │
│                                                              │
│  Services (DI via Depends()):                               │
│  ├── SearchService → SearchBuilder → SolrClient            │
│  ├── QueryLogicParser (requête avancée → Solr syntax)      │
│  ├── CacheService (Redis)                                   │
│  ├── PermissionsService → DocsPermissionsClient            │
│  ├── LdapService (ldap3 — bind service + bind user)        │
│  ├── OidcService (httpx + python-jose — JWKS, state CSRF)  │
│  └── Auth: JWT + bcrypt (core/security.py)                 │
└──────────┬───────────────┬───────────────────┬──────────────┘
           │               │                   │
    ┌──────▼──────┐  ┌─────▼─────┐   ┌────────▼──────────────┐
    │ PostgreSQL  │  │   Redis   │   │ Solr distant           │
    │ Users       │  │ Search 5m │   │ solrslave-sec.labocleo │
    │ SavedSearch │  │ Suggest 1h│   │ .org/solr/documents    │
    └─────────────┘  │ Perms 30m │   └────────────────────────┘
                     │ OIDC state│
                     │  10 min   │
                     └───────────┘
```

---

## Flux de données principaux

Le contrat public versionné et des exemples `curl` sont documentés dans [`API_V1.md`](./API_V1.md).

### Recherche simple
```
SearchBar → useSearchApi.executeSearch()
  → POST /api/v1/search { query, filters, pagination, facets }
  → SearchBuilder.build_search_url()
  → SolrClient.search() [+ Redis cache 5 min]
  → Normalisation facettes
  → setResults() / setFacets() / setTotal()
  → ResultsList + Facets
```

### Recherche avancée
```
AdvancedQueryBuilder → useSearchState.setLogicalQuery(RuleGroupType)
  opérateurs : =, contains, beginsWith, endsWith, !=, notContains…
  → POST /api/v1/search { logical_query: {...}, query: { query: "*" } }
  → QueryLogicParser.convert_to_solr_query_string()
     ex: { combinator:"and", rules:[{field:"titre", op:"contains", value:"histoire"}] }
     →   fq=naked_titre:histoire
  → [suite identique à recherche simple]
```

### Synchronisation URL ↔ état
```
useUrlSync (monte dans SearchProvider)
  → lecture URL au démarrage → loadSearch() si params présents
  → écoute useSearchState → pushState / replaceState (debounce 300ms)
  → popstate (back/forward) → loadSearch() + restauration QB
  → paramètres : q=, f[field]=value, page=, mode=, lq= (QB encodé JSON)
```

### Authentification locale
```
AuthModal → api.login(email, password) → POST /auth/login
  → JWT (HS256, sub=user_id, email claim, TTL=1440 min)
  → localStorage[auth_token] + localStorage[auth_user]
  → AuthProvider.setUser() / setToken()
```

### Authentification LDAP
```
AuthModal (ldap-form) → api.ldapLogin(username, password)
  → POST /auth/ldap/login
  → LdapService.authenticate() : bind service → search DN → bind user
  → _provision_federated_user() : upsert User(hashed_password=null, auth_provider='ldap')
  → JWT → localStorage (même chemin que local)
```

### Authentification SSO (OIDC)
```
AuthModal (btn-sso-login) → redirect GET /auth/sso/login
  → OidcService.build_authorization_url() : state → Redis (TTL 10min)
  → 302 → IdP authorization_endpoint

IdP callback → GET /auth/sso/callback?code=...&state=...
  → OidcService.exchange_code() : validation state + échange code → ID token
  → Validation JWKS (RS256/ES256), issuer, audience
  → _provision_federated_user() : upsert User(auth_provider='oidc')
  → génère code court hex32 → Redis[sso_code:<code>] TTL 60s
  → 302 → frontend/?sso_code=<code>  [JWT ne transite pas dans l'URL]

Frontend AuthContext (useEffect) → détecte ?sso_code=
  → supprime param de l'URL (replaceState) immédiatement
  → GET /auth/sso/exchange?code=<code>
  → backend valide + supprime le code (usage unique)
  → retourne {access_token} en JSON → loginWithToken() → session active
```

---

## Logging

Socle documenté dans [`docs/LOGGING.md`](./LOGGING.md). La spec transverse `specs/013-logging-strategy` est livrée : configuration JSON backend, wrapper frontend et durcissement (redaction, `extra={"context"}`, règle ESLint `no-console`) livrés le 2026-05-10.

| Zone | Mécanisme | Config |
|------|-----------|--------|
| Backend | `python-json-logger`, root logger, JSON stdout | `LOG_LEVEL` via Docker Compose |
| Frontend | `lib/logger.ts` (wrapper niveaux debug/info/warn/error) | `NODE_ENV` |

---

## État des features

| Feature | Statut | Tests |
|---------|--------|-------|
| Recherche simple + facettes + pagination | ✅ Complet | search.spec.ts |
| Autocomplétion | ✅ Complet | — |
| Recherche avancée (QB, 8+ opérateurs) | ✅ Complet | — |
| i18n 6 langues (FR/EN/ES/DE/IT/PT) | ✅ Complet | — |
| Thème clair/sombre | ✅ Complet | — |
| Authentification locale JWT (1440 min) | ✅ Complet | auth.spec.ts (15) |
| Recherches sauvegardées | ✅ Complet | saved-searches.spec.ts (12) |
| Client API centralisé (`lib/api.ts`) | ✅ Complet | — |
| Badges d'accès (permissions) | ✅ Complet | permissions.spec.ts (4) |
| Champs QB depuis `/facets/config` | ✅ Complet | — |
| SearchContext découpé en 6 hooks SOLID | ✅ Complet | — |
| Synchronisation état ↔ URL (back/forward) | ✅ Complet | url-sync.spec.ts (21) |
| Authentification LDAP institutionnelle | ✅ Complet | auth-ldap-sso.spec.ts (14 déclarés, 12 exécutables + 2 skip) |
| Authentification SSO OIDC | ✅ Complet — transport JWT via code court à usage unique | auth-ldap-sso.spec.ts (14 déclarés, 12 exécutables + 2 skip) |

---

## Maintenabilité

### Points forts
- **DI backend** : Services injectés via `Depends()`, interfaces définies (`ISearchService`, `ISearchBuilder`). Recherche et suggestion passent par les services.
- **Config JSON** : Facettes et champs Solr en JSON (`facets_json/`, `fields_json/`). Pas de recompilation pour modifier une facette.
- **Hooks SOLID** : `SearchContext` est un assembleur — logique dans 6 hooks spécialisés. `useUrlSync` est réduit via helpers purs ; `useSearchApi` reste volontairement orchestrateur.
- **latestRef pattern** : Évite les stale closures dans `executeSearch` sans useCallback instable.
- **Client API centralisé** : `lib/api.ts` — base URL, headers, auth en un seul endroit.
- **Types centralisés** : `front/app/types.ts` — interfaces partagées entre composants et contextes.
- **Auth fédérée sans friction** : just-in-time provisioning LDAP/SSO — aucun formulaire d'inscription pour les comptes institutionnels.
- **Tests E2E** : tests Playwright couvrant les flux critiques. Dernière vérification complète à relancer dans l'environnement cible.
- **i18n** : 6 langues, gérées via next-intl. Ajout d'une langue = 1 fichier JSON.

### Dette technique résiduelle

La dette bloquante ci-dessous est résolue. Les suites restantes sont listées dans `specs/PLANNING.md` comme vérification release ou amélioration opportuniste.

| Priorité | Problème | Impact | Plan |
|---|---|---|---|
| ✅ | `DELETE /cache/clear` exposé sans garde production | Résolu : HTTP 403 en production | — |
| ✅ | JWT SSO transmis via query string | Résolu : code court hex32 → Redis TTL 60s → échange `/auth/sso/exchange` | — |
| ✅ | Secrets par défaut acceptables si production mal configurée | Résolu : `Settings` bloque les placeholders connus en production | — |
| ✅ | `/suggest` contient parsing/cache dans l'endpoint | Résolu : `SuggestService.fetch_autocomplete_suggestions` | — |
| ✅ | `SearchService`/`SearchBuilder` utilisent encore `Dict[str, Any]` | Résolu : `SearchRequest` circule jusqu'au builder | — |
| ✅ | Réponses API publiques partiellement non typées | Résolu : `response_model` sur `/search`, `/suggest`, `/facets/config` | — |
| ✅ | Hooks recherche/URL trop longs | Résolu/accepté : helpers extraits, `useUrlSync` réduit, `useSearchApi` orchestration conservée | — |
| P2 optionnel | Composants consommant encore `useSearch()` global | Couplage UI résiduel | Migrer vers selectors lors des prochaines touches |

### Dettes résolues conservées comme historique

| # | Problème | Résolution |
|---|---------|------------|
| D2 | `logical_query: Optional[Any]` | → `Optional[QueryGroup]` (Pydantic typé) |
| D3 | Timestamp hardcodé dans `/health` | → `datetime.now(timezone.utc).isoformat()` |
| D4 | `solr_connector.py` / `document_mapper.py` orphelins | → supprimés |
| D5 | `disciplinary_field` invalide dans QB | → retiré de `SEARCH_FIELDS_MAPPING`, 3 champs valides : `titre`, `author`, `naked_texte` |

### Vérification récente

| Commande | Résultat (voir `specs/PLANNING.md` § Bloc 0, vérifié 2026-05-05) |
|---|---|
| `cd front && pnpm run lint` | ✅ ESLint sans warning |
| `cd front && pnpm run test:e2e` | ✅ 68 tests déclarés, 66 exécutables + 2 skip LDAP/OIDC ; navigateur Playwright absent localement, couverture indirecte confirmée |
| `make test` | ✅ Suite pytest verte (Docker) — commande backend de référence |
| `python3 -m pytest ...` hors Docker | Non pertinent : dépendances absentes sans virtualenv dédié — `make test` reste la référence |
