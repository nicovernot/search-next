# Architecture — OpenEdition Search

**Dernier audit**: 2026-04-17 (mis à jour après commit 87ccb7c)
**Branch active**: `feature/002-advanced-search-suite`
**État global**: Application fonctionnelle, 29 tests E2E verts, specs 001–003/005–010 livrées. Prochaine : 004-url-sync.

---

## Stack

| Couche | Technologie | Version |
|--------|-------------|---------|
| Frontend | Next.js (App Router) | 16 |
| UI | React + TypeScript + Tailwind CSS | 19 / 5 / 4 |
| i18n | next-intl | 4 |
| Query builder | react-querybuilder | 8 |
| Backend | FastAPI + Pydantic v2 | — |
| Auth | JWT (HS256) + bcrypt | — |
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
│  ├── AuthProvider    — JWT, session utilisateur             │
│  └── SearchProvider  — assemble 5 hooks SOLID              │
│       ├── useFacetConfig  /facets/config + searchFields    │
│       ├── useSuggestions  /suggest                         │
│       ├── usePermissions  /permissions                     │
│       ├── useSearchState  état local (query/filters/page)  │
│       └── useSearchApi    executeSearch, loadSearch        │
│                                                              │
│  Hooks utilitaires:                                         │
│  ├── useAuthModal      état modal auth (open/tab)          │
│  ├── useClickOutside   fermeture dropdown générique        │
│  ├── useAnchoredPortal positionnement dropdown via portal  │
│  └── useIsClient       SSR guard                           │
│                                                              │
│  Composants:                                                 │
│  ├── SearchBar / AutocompleteInput                          │
│  ├── AdvancedQueryBuilder (react-querybuilder)              │
│  ├── Facets / FacetGroup                                    │
│  ├── ResultsList / ResultItem / Pagination                  │
│  ├── AuthModal / AuthButtons                                │
│  └── SavedSearchesPanel                                     │
│                                                              │
│  Lib:                                                        │
│  ├── lib/api.ts     — client API centralisé (tous fetch)   │
│  └── lib/qb-fields.ts — champs QB (titre, author, texte)  │
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
│  └── GET/POST/DELETE /saved-searches                        │
│                                                              │
│  Services (DI via Depends()):                               │
│  ├── SearchService → SearchBuilder → SolrClient            │
│  ├── QueryLogicParser (requête avancée → Solr syntax)      │
│  ├── CacheService (Redis)                                   │
│  ├── PermissionsService → DocsPermissionsClient            │
│  └── Auth: JWT + bcrypt (core/security.py)                 │
└──────────┬───────────────┬───────────────────┬──────────────┘
           │               │                   │
    ┌──────▼──────┐  ┌─────▼─────┐   ┌────────▼──────────────┐
    │ PostgreSQL  │  │   Redis   │   │ Solr distant           │
    │ Users       │  │ Search 5m │   │ solrslave-sec.labocleo │
    │ SavedSearch │  │ Suggest 1h│   │ .org/solr/documents    │
    └─────────────┘  │ Perms 30m │   └────────────────────────┘
                     └───────────┘
```

---

## Flux de données principaux

### Recherche simple
```
SearchBar → SearchContext.executeSearch()
  → POST /search { query, filters, pagination, facets }
  → SearchBuilder.build_search_url()
  → SolrClient.search() [+ Redis cache 5 min]
  → Normalisation facettes
  → setResults() / setFacets() / setTotal()
  → ResultsList + Facets
```

### Recherche avancée
```
AdvancedQueryBuilder → setLogicalQuery(RuleGroupType)
  opérateurs supportés : =, contains, beginsWith, endsWith
  (react-querybuilder envoie camelCase → normalisé par _OPERATOR_ALIASES)
  → POST /search { logical_query: {...}, query: { query: "*" } }
  → QueryLogicParser.convert_to_solr_query_string()
     ex: { combinator:"and", rules:[{field:"titre", op:"contains", value:"histoire"}] }
     →   fq=naked_titre:histoire
  → [suite identique à recherche simple]
```

### Authentification
```
AuthModal → api.login(email, password) → POST /auth/login
  → JWT (HS256, sub=user_id, TTL=1440 min)
  → localStorage["auth_token"] + localStorage["auth_user"]
  → AuthProvider.setUser() / setToken()
  → Accès SavedSearchesPanel
```

---

## État des features (2026-04-17)

| Feature | Statut | Tests |
|---------|--------|-------|
| Recherche simple + facettes + pagination | ✅ Complet | 2 E2E |
| Autocomplétion | ✅ Complet | — |
| Recherche avancée (QB AND/OR, opérateurs normalisés) | ✅ Complet | inclus dans 29 |
| i18n 6 langues (FR/EN/ES/DE/IT/PT) | ✅ Complet | — |
| Thème clair/sombre | ✅ Complet | — |
| Authentification JWT (1440 min) | ✅ Complet | 15 E2E |
| Recherches sauvegardées | ✅ Complet | 12 E2E |
| Client API centralisé (`lib/api.ts`) | ✅ Complet | — |
| Badges d'accès (permissions) | ✅ Complet | E2E permissions.spec.ts |
| Champs QB depuis config API (`/facets/config`) | ✅ Complet | — |
| SearchContext découpé en 5 hooks SOLID | ✅ Complet | — |
| Sync état ↔ URL | 🔲 Backlog (spec 004) | — |

---

## Maintenabilité

### Points forts
- **DI backend** : Services injectés via `Depends()`, interfaces définies (`ISearchService`, `ISearchBuilder`). Facile à mocker/tester.
- **Config JSON** : Facettes et champs Solr en JSON (`facets_json/`, `fields_json/`). Pas de recompilation pour modifier une facette.
- **Contextes React** : Logique métier centralisée dans `SearchContext` / `AuthContext`. Composants UI sans état propre (dumb).
- **latestRef pattern** : Évite les stale closures dans `executeSearch` sans useCallback instable. Pattern robuste.
- **Client API centralisé** : `lib/api.ts` — un seul endroit pour changer base URL, headers, auth. Tous les contextes l'utilisent.
- **Types centralisés** : `front/app/types.ts` — interfaces partagées entre composants et contextes.
- **Tests E2E** : 29 tests Playwright couvrent les flux critiques.
- **i18n** : 69 clés × 6 langues, gérées via next-intl. Ajout d'une langue = 1 fichier JSON.

### Dettes techniques restantes

| # | Problème | Fichier | Impact |
|---|---------|---------|--------|
| D2 | `logical_query: Optional[Any]` dans Pydantic | `search_models.py:79` | Pas de validation schema de la requête avancée |
| D3 | Timestamp hardcodé `"2024-01-01T00:00:00Z"` dans `/health` | `main.py` | Health check retourne une date fixe |
| D4 | `solr_connector.py` et `document_mapper.py` potentiellement orphelins | `services/` | Code mort possible |
| D5 | Champ `disciplinary_field` supprimé mais pas encore remplacé | `facet_config.py` | La recherche sur sujet/mots-clés n'est pas supportée |

---

## Problèmes de cohérence résolus depuis l'audit initial

| Problème initial | Solution apportée |
|---|---|
| Token JWT 30 min | `settings.py` default=1440, `.env.development` aussi |
| HTTP 502 pour email existant | `api/auth.py` → `HTTP_409_CONFLICT` |
| Erreurs auth hardcodées (non traduites) | Pattern codes → `t()` dans AuthModal, 6 langues |
| 7 `fetch()` dispersés | `lib/api.ts` centralisé, tous les contextes migrent |
| Champs QB dans le composant | Extraits dans `lib/qb-fields.ts` |

---

## Plan d'action prioritaire (état actuel)

### Priorité 1 — Spec 004 URL Sync (~4 jours)
1. **Sync état ↔ URL** : Encoder `q=`, `f[]=`, `page=`, `mode=` dans les query params, gérer back/forward, restaurer le QueryBuilder depuis l'URL
   - Prérequis : spec 007 ✅ (SearchContext découplé en hooks)

### Corrections mineures à adresser au fil de l'eau
1. **Typer `logical_query`** (D2) — Remplacer `Optional[Any]` par le modèle `QueryGroup` Pydantic déjà défini dans `logical_query.py`
2. **Fix timestamp `/health`** (D3) — `datetime.now(timezone.utc).isoformat()` (déjà utilisé par le reste de l'endpoint)
3. **Vérifier orphelins** (D4) — Confirmer si `solr_connector.py` et `document_mapper.py` sont importés
4. **Champ disciplinary** (D5) — Identifier le champ Solr correct pour les mots-clés et le rajouter dans `SEARCH_FIELDS_MAPPING`

---

## Ordre d'implémentation recommandé

```
[004-url-sync ~4j] → corrections mineures D2-D5 au fil de l'eau
```

La spec 004 est la seule feature majeure restante. Les corrections D2-D5 peuvent être groupées dans un commit de maintenance.
