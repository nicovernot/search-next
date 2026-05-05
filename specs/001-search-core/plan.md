# Plan 001 — Search Core

## Architecture

```
docker-compose.yml
├── search_api_solr (FastAPI :8007)
│   └── POST /search, GET /suggest, GET /permissions, GET /facets/config
├── openedition_redis (Redis :6379)
└── search_next (Next.js)
    └── SearchContext → load GET /facets/config → fetch POST /search → résultats + facettes
```

## Data Flow

1. Au démarrage, `useFacetConfig` charge `GET /facets/config`
2. Utilisateur tape dans `SearchBar`
3. Debounce 300 ms pour `GET /suggest`, puis soumission → `executeSearch()` dans `SearchContext`
4. `buildSearchPayload()` construit `filters` et `facets` à partir de `facetConfig`
5. `fetch POST /search` avec `{ query, filters, facets, pagination, logical_query? }`
6. Réponse backend normalisée → `setResults`, `setFacets`, `setTotal`
7. `ResultsList` re-render avec les nouveaux résultats
8. `Facets` re-render avec les nouvelles facettes

## Key Files

| Fichier | Rôle |
|---------|------|
| `front/app/context/SearchContext.tsx` | État + appels API |
| `front/app/hooks/useFacetConfig.ts` | Charge la config de facettes et les champs QB |
| `front/app/lib/search-payload.ts` | Génération du payload dynamique |
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
| `search_api_solr/app/services/facet_config.py` | Mapping facettes / filtres |
| `search_api_solr/app/services/facets_json/common.json` | Déclaration des facettes communes |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | URL publique du backend FastAPI | `http://localhost:8003` |
