# Plan 001 — Search Core

## Architecture

```
docker-compose.yml
├── search_api_solr (FastAPI :8007)
│   └── POST /search, GET /suggest, GET /permissions, GET /facets/config
├── openedition_redis (Redis :6379)
└── search_next (Next.js)
    └── SearchContext → fetch POST /search → résultats + facettes
```

## Data Flow

1. Utilisateur tape dans `SearchBar`
2. Debounce 300 ms pour `GET /suggest`, puis soumission → `executeSearch()` dans `SearchContext`
3. `fetch POST /search` avec `{ query, filters, facets, pagination, logical_query? }`
4. Réponse backend normalisée → `setResults`, `setFacets`, `setTotal`
5. `ResultsList` re-render avec les nouveaux résultats
6. `Facets` re-render avec les nouvelles facettes

## Key Files

| Fichier | Rôle |
|---------|------|
| `front/app/context/SearchContext.tsx` | État + appels API |
| `front/app/components/SearchBar.tsx` | Input principal |
| `front/app/components/AutocompleteInput.tsx` | Autocomplétion |
| `front/app/components/ResultsList.tsx` | Liste + skeleton |
| `front/app/components/ResultItem.tsx` | Carte résultat |
| `front/app/components/Facets.tsx` | Sidebar |
| `front/app/components/FacetGroup.tsx` | Groupe facette |
| `front/app/components/Pagination.tsx` | Pages |
| `front/app/components/LanguageSelector.tsx` | Langue |
| `front/app/[locale]/page.tsx` | Écran principal |
| `front/app/[locale]/layout.tsx` | Root layout + providers |
| `front/messages/*.json` | Traductions |
| `front/app/types.ts` | Types TypeScript |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | URL du backend FastAPI | `http://localhost:8007` |
