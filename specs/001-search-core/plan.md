# Plan 001 — Search Core

## Architecture

```
docker-compose.yml
├── search_api_solr (FastAPI :8007)
│   └── POST /search, GET /suggest, GET /permissions
├── openedition_redis (Redis :6379)
└── search_next (Next.js :3009)
    └── SearchContext → fetch POST /search → résultats + facettes
```

## Data Flow

1. Utilisateur tape dans `SearchBar`
2. Debounce 500 ms → `executeSearch()` dans `SearchContext`
3. `fetch POST /search` avec `{ query, filters, facets, pagination }`
4. Réponse Solr → transformation facettes → `setResults`, `setFacets`, `setTotal`
5. `ResultsList` re-render avec les nouveaux résultats
6. `Facets` re-render avec les nouvelles facettes

## Key Files

| Fichier | Rôle |
|---------|------|
| `front-next/app/context/SearchContext.tsx` | État + appels API |
| `front-next/app/hooks/useTranslations.ts` | i18n |
| `front-next/app/components/SearchBar.tsx` | Input debounce |
| `front-next/app/components/ResultsList.tsx` | Liste + skeleton |
| `front-next/app/components/ResultItem.tsx` | Carte résultat |
| `front-next/app/components/Facets.tsx` | Sidebar |
| `front-next/app/components/FacetGroup.tsx` | Groupe facette |
| `front-next/app/components/Pagination.tsx` | Pages |
| `front-next/app/components/LanguageSelector.tsx` | Langue |
| `front-next/app/page.tsx` | Layout |
| `front-next/app/layout.tsx` | Root layout + providers |
| `front-next/app/types.ts` | Types TypeScript |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | URL du backend FastAPI | `http://localhost:8007` |
