# Architecture — OpenEdition Search

**Date d'audit**: 2026-04-15
**Branch active**: `feature/002-advanced-search-suite`
**État global**: Application fonctionnelle, 29 tests E2E verts, 3 specs implémentées sur 5.

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
└─────────────────────┬────────────────────────────────────────┘
                      │ fetch() — REST JSON
                      │ http://localhost:8003
┌─────────────────────▼────────────────────────────────────────┐
│                    BACKEND (FastAPI)                          │
│                                                              │
│  Endpoints:                                                  │
│  ├── POST /search, GET /suggest                             │
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
AuthModal → POST /auth/login { email, password }
  → JWT (HS256, sub=user_id)
  → localStorage["auth_token"] + localStorage["auth_user"]
  → AuthProvider.setUser() / setToken()
  → Accès SavedSearchesPanel
```

---

## Ce qui fonctionne (état réel)

| Feature | Statut | Tests |
|---------|--------|-------|
| Recherche simple + facettes + pagination | ✅ Complet | 2 E2E |
| Autocomplétion | ✅ Complet | — |
| Recherche avancée (QueryBuilder AND/OR/NOT) | ✅ Complet | inclus dans 29 |
| i18n 6 langues (FR/EN/ES/DE/IT/PT) | ✅ Complet | — |
| Thème clair/sombre | ✅ Complet | — |
| Authentification JWT | ✅ Complet | 15 E2E |
| Recherches sauvegardées | ✅ Complet | 12 E2E |
| Badges d'accès (permissions) | ⚠️ Partiel | — |
| Sync état ↔ URL | 🔲 Absent | — |

---

## Problèmes de cohérence identifiés

### Critiques

| # | Problème | Fichier | Impact |
|---|---------|---------|--------|
| C1 | Token JWT expiré en 30 min (doit être 1440 min) | `settings.py:109` | Utilisateurs déconnectés trop tôt |
| C2 | Badges permissions : endpoint `/permissions` existant, UI absente | `ResultItem.tsx` | Spec 005 non livrée |
| C3 | Pas de sync état ↔ URL | `SearchContext.tsx` | Liens non partageables |

### Importants

| # | Problème | Fichier | Impact |
|---|---------|---------|--------|
| I1 | Champs QueryBuilder hardcodés au lieu de venir de la config | `AdvancedQueryBuilder.tsx:47-52` | Maintenance manuelle à chaque ajout de champ |
| I2 | Appels `fetch()` dispersés sans client API centralisé | `SearchContext.tsx`, `AuthContext.tsx`, `SavedSearchesPanel.tsx` | Headers auth manquants, gestion d'erreurs incohérente |
| I3 | Code erreur `HTTP_400_BAD_GATEWAY` (502) au lieu de 409 | `api/auth.py:25` | Erreur email existant mal interprétée par le frontend |
| I4 | Messages d'erreur auth non traduits | `AuthContext.tsx:80,100` | Rupture i18n en cas d'échec login/register |

### Mineurs

| # | Problème | Fichier |
|---|---------|---------|
| M1 | Type `Any` pour `logical_query` dans le modèle Pydantic | `search_models.py:79` |
| M2 | Assertion de type manuelle dans `ResultsList.tsx` pour facet config | `ResultsList.tsx:29-33` |
| M3 | Logs frontend via `console.error()` non structurés | Tous les composants |

---

## Maintenabilité

### Points forts
- **DI backend** : Services injectés via `Depends()`, interfaces définies (`ISearchService`, `ISearchBuilder`). Facile à mocker/tester.
- **Config JSON** : Facettes et champs Solr en JSON (`facets_json/`, `fields_json/`). Pas de recompilation pour ajouter un champ.
- **Contextes React** : Logique métier centralisée dans `SearchContext` / `AuthContext`. Composants UI dumb.
- **Tests E2E** : 29 tests Playwright couvrent les flux critiques.

### Dettes techniques
- **Pas de client API frontend** : 7 appels `fetch()` dispersés dans 4 fichiers différents. Chaque modification (ajout header auth, changement de base URL) nécessite des modifications à plusieurs endroits.
- **Champs QB hardcodés** : Les 4 champs du QueryBuilder (`titre`, `author`, `naked_texte`, `disciplinary_field`) sont dans `AdvancedQueryBuilder.tsx`. Ajouter un champ nécessite de modifier le code.
- **Expiration token** : Valeur par défaut 30 min dans `settings.py`, non compensée dans les fichiers `.env` de dev.

---

## Plan d'action prioritaire

### Priorité 1 — Corrections rapides (< 1 jour)
1. **Fixer le token TTL** : Ajouter `ACCESS_TOKEN_EXPIRE_MINUTES=1440` dans `.env.development` et `sync_env.sh`
2. **Fixer le code HTTP** : `HTTP_400_BAD_GATEWAY` → `HTTP_409_CONFLICT` dans `api/auth.py:25`
3. **i18n erreurs auth** : Utiliser des clés i18n dans `AuthContext.tsx` au lieu de strings hardcodées

### Priorité 2 — Fondations (2-3 jours)
4. **Client API centralisé** : Créer `front/app/lib/api.ts` regroupant tous les appels `fetch()` avec gestion des headers et des erreurs
5. **Champs QB depuis config** : Charger les champs du QueryBuilder depuis `GET /facets/config` au lieu du hardcode

### Priorité 3 — Features backlog
6. **005-permissions** : Badges d'accès sur les résultats (endpoint existant, UI à créer)
7. **004-url-sync** : Synchronisation état ↔ URL (liens partageables, back/forward)

---

## Ordre d'implémentation recommandé

```
[Corrections rapides] → [Client API] → [005-permissions] → [004-url-sync]
       ~1j                   ~2j              ~3j                ~4j
```

La spec 005 bénéficie du client API centralisé (l'appel `/permissions` s'y intègre proprement).
La spec 004 est la plus complexe et doit venir en dernier car elle touche le `SearchContext` en profondeur.
