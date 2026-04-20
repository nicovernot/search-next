# Architecture — OpenEdition Search

**Dernier audit**: 2026-04-19  
**Branch active**: `feature/002-advanced-search-suite`  
**État global**: Specs 001–011 livrées fonctionnellement. Dette résiduelle P0/P1/P2 planifiée dans `specs/PLANNING.md`.

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
│  Endpoints:                                                  │
│  ├── POST /search, GET /search                              │
│  ├── GET /suggest                                           │
│  ├── GET /facets/config                                     │
│  ├── GET /permissions                                       │
│  ├── POST /auth/login, POST /auth/register                  │
│  ├── POST /auth/ldap/login                                  │
│  ├── GET  /auth/sso/login  (redirect → IdP)                │
│  ├── GET  /auth/sso/callback  (JWT en query — à durcir P0) │
│  └── GET/POST/DELETE /saved-searches                        │
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

### Recherche simple
```
SearchBar → useSearchApi.executeSearch()
  → POST /search { query, filters, pagination, facets }
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
  → POST /search { logical_query: {...}, query: { query: "*" } }
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
| Badges d'accès (permissions) | ✅ Complet | permissions.spec.ts |
| Champs QB depuis `/facets/config` | ✅ Complet | — |
| SearchContext découpé en 6 hooks SOLID | ✅ Complet | — |
| Synchronisation état ↔ URL (back/forward) | ✅ Complet | url-sync.spec.ts (19) |
| Authentification LDAP institutionnelle | ✅ Complet | auth-ldap-sso.spec.ts |
| Authentification SSO OIDC | ✅ Fonctionnel, durcissement transport JWT requis | auth-ldap-sso.spec.ts |

---

## Maintenabilité

### Points forts
- **DI backend partielle** : Services injectés via `Depends()`, interfaces définies (`ISearchService`, `ISearchBuilder`). La recherche principale passe par les services ; `/suggest` garde encore de la logique dans l'endpoint.
- **Config JSON** : Facettes et champs Solr en JSON (`facets_json/`, `fields_json/`). Pas de recompilation pour modifier une facette.
- **Hooks SOLID** : `SearchContext` est un assembleur — logique dans 6 hooks spécialisés. `useSearchApi` et `useUrlSync` restent volontairement plus longs que le seuil initial et sont planifiés en P2.
- **latestRef pattern** : Évite les stale closures dans `executeSearch` sans useCallback instable.
- **Client API centralisé** : `lib/api.ts` — base URL, headers, auth en un seul endroit.
- **Types centralisés** : `front/app/types.ts` — interfaces partagées entre composants et contextes.
- **Auth fédérée sans friction** : just-in-time provisioning LDAP/SSO — aucun formulaire d'inscription pour les comptes institutionnels.
- **Tests E2E** : tests Playwright couvrant les flux critiques. Dernière vérification complète à relancer dans l'environnement cible.
- **i18n** : 6 langues, gérées via next-intl. Ajout d'une langue = 1 fichier JSON.

### Dette technique résiduelle

La dette résiduelle ci-dessous est ordonnée dans `specs/PLANNING.md`. Les anciennes dettes D2-D5 sont résolues, mais l'audit 2026-04-19 a rouvert des priorités de stabilisation.

| Priorité | Problème | Impact | Plan |
|---|---|---|---|
| P0 | `DELETE /cache/clear` exposé sans garde production | Purge cache possible si route accessible | Protéger par auth admin ou désactiver hors dev/test |
| ✅ | JWT SSO transmis via query string | Résolu : code court hex32 → Redis TTL 60s → échange `/auth/sso/exchange` | — |
| P0 | Secrets par défaut acceptables si production mal configurée | Risque de déploiement avec secret faible | Validator `Settings` bloquant en production |
| P1 | `/suggest` contient parsing/cache dans l'endpoint | Responsabilité endpoint/service mélangée | Déplacer dans `SuggestService` |
| P1 | `SearchService`/`SearchBuilder` utilisent encore `Dict[str, Any]` | Contrats moins sûrs et duplication dict/Pydantic | Faire circuler `SearchRequest` typé |
| P1 | Réponses API publiques partiellement non typées | Contrat moins stable côté front | Ajouter `response_model` Pydantic |
| P2 | `useSearchApi` 197 lignes, `useUrlSync` 143 lignes | Maintenance plus coûteuse | Extraire helpers testables |
| P2 | `SearchContext` segmenté en interfaces mais consommé via `useSearch()` global | Couplage UI résiduel | Ajouter hooks selectors ou contexts ciblés |

### Dettes résolues conservées comme historique

| # | Problème | Résolution |
|---|---------|------------|
| D2 | `logical_query: Optional[Any]` | → `Optional[QueryGroup]` (Pydantic typé) |
| D3 | Timestamp hardcodé dans `/health` | → `datetime.now(timezone.utc).isoformat()` |
| D4 | `solr_connector.py` / `document_mapper.py` orphelins | → supprimés |
| D5 | `disciplinary_field` invalide dans QB | → retiré de `SEARCH_FIELDS_MAPPING`, 3 champs valides : `titre`, `author`, `naked_texte` |

### Vérification récente

| Commande | Résultat audit 2026-04-19 |
|---|---|
| `cd front && npm run lint` | Passe avec 23 warnings (`id-length`, `react-hooks/exhaustive-deps`, `<img>`) |
| `cd search_api_solr && pytest` | Non validé localement : dépendances Python absentes dans l'environnement courant |
