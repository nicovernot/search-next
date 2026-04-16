# Architecture — OpenEdition Search

**Dernier audit**: 2026-04-15 (mis à jour après commit f5297ac)
**Branch active**: `feature/002-advanced-search-suite`
**État global**: Application fonctionnelle, 29 tests E2E verts, spec 006 quasi-complète.

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
│  Contextes:                                                  │
│  ├── AuthProvider    — JWT, session utilisateur             │
│  └── SearchProvider  — état de recherche, executeSearch()   │
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
│  └── lib/qb-fields.ts — définition des champs QueryBuilder │
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
  → POST /search { logical_query: {...} }
  → QueryLogicParser.to_solr_query()
     ex: { AND: [titre:histoire, OR: [author:Smith, author:Dupont]] }
     →   titre:*histoire* AND (author:"Smith" OR author:"Dupont")
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

## État des features (2026-04-15)

| Feature | Statut | Tests |
|---------|--------|-------|
| Recherche simple + facettes + pagination | ✅ Complet | 2 E2E |
| Autocomplétion | ✅ Complet | — |
| Recherche avancée (QueryBuilder AND/OR/NOT) | ✅ Complet | inclus dans 29 |
| i18n 6 langues (FR/EN/ES/DE/IT/PT) | ✅ Complet | — |
| Thème clair/sombre | ✅ Complet | — |
| Authentification JWT (1440 min) | ✅ Complet | 15 E2E |
| Recherches sauvegardées | ✅ Complet | 12 E2E |
| Client API centralisé (`lib/api.ts`) | ✅ Complet | — |
| HTTP 409 pour email existant | ✅ Complet | — |
| Erreurs auth traduites (6 langues) | ✅ Complet | — |
| Badges d'accès (permissions) | ⚠️ Partiel — endpoint OK, UI absente | — |
| Champs QB depuis config API | ⚠️ Partiel — fichier dédié, mais toujours hardcodé | — |
| Sync état ↔ URL | 🔲 Absent | — |

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
| D1 | Champs QB encore hardcodés dans `qb-fields.ts` (pas depuis `/facets/config`) | `lib/qb-fields.ts` | Ajout d'un champ nécessite un commit frontend |
| D2 | `logical_query: Optional[Any]` dans Pydantic | `search_models.py:79` | Pas de validation schema de la requête avancée |
| D3 | Timestamp hardcodé `"2024-01-01T00:00:00Z"` dans `/health` | `main.py:342` | Health check retourne une date fixe |
| D4 | `solr_connector.py` et `document_mapper.py` potentiellement orphelins | `services/` | Code mort possible |

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

### Priorité 1 — Compléter spec 006 (< 1 jour)
1. **Champs QB depuis config** (D1) : Charger les champs depuis `GET /facets/config` dans `SearchContext`, passer en prop à `AdvancedQueryBuilder`, fallback sur `QB_FIELDS` si config indisponible
2. **Typer `logical_query`** (D2) : Remplacer `Optional[Any]` par un modèle Pydantic récursif
3. **Fix timestamp `/health`** (D3) : `datetime.utcnow().isoformat()` au lieu de la string fixe
4. **Vérifier orphelins** (D4) : Confirmer si `solr_connector.py` et `document_mapper.py` sont importés quelque part

### Priorité 2 — Spec 005 Permissions (~3 jours)
5. **Badges d'accès** : Appeler `GET /permissions?urls=...` depuis `ResultsList`, afficher badges sur `ResultItem`

### Priorité 3 — Spec 004 URL Sync (~4 jours)
6. **Sync état ↔ URL** : Encoder query/filters/page dans les query params, gérer back/forward, générer des liens partageables

---

## Ordre d'implémentation recommandé

```
[006 restant] → [005-permissions] → [004-url-sync]
     <1j              ~3j                ~4j
```

La spec 005 bénéficie du client API centralisé (déjà en place).
La spec 004 est la plus complexe (touche `SearchContext` en profondeur) — à faire en dernier.
