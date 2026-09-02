# Plan 007 — Refactorisation SearchContext

## Architecture

```
front/
├── app/
│   ├── context/
│   │   └── SearchContext.tsx         # assembleur minimal, sans logique métier lourde
│   ├── hooks/
│   │   ├── useSearchState.ts          # état brut de recherche
│   │   ├── useSearchApi.ts            # orchestration recherche + stale closures
│   │   ├── useSuggestions.ts          # suggestions/autocomplete
│   │   ├── usePermissions.ts          # permissions batch
│   │   ├── useFacetConfig.ts          # config facettes et champs
│   │   └── useUrlSync.ts              # sync URL / historique navigateur
│   └── lib/
│       ├── search-payload.ts         # payloads de recherche
│       └── url-search-state.ts       # parse / serialisation URL
```

## Data Flow

1. `useSearchState` centralise les states utilisateur : query, filtres, mode, pagination.
2. `useFacetConfig` charge la configuration backend une fois au montage.
3. `useSuggestions` sur écoute de la query et la locale pour obtenir des suggestions.
4. `useSearchApi` exécute les appels `search` et orchestre les mises à jour des résultats.
5. `usePermissions` s'appuie sur les résultats visibles pour alimenter les badges.
6. `useUrlSync` aligne l'URL avec l'état courant et la restaure sur retour navigateur.
7. `SearchContext` ne fait que composer ces hooks et exposer le provider.

## Key Files

| Fichier | Rôle |
|---------|------|
| `front/app/context/SearchContext.tsx` | Provider + composition du contexte |
| `front/app/hooks/useSearchState.ts` | Source de vérité de la recherche |
| `front/app/hooks/useSearchApi.ts` | Logique de recherche et stale closures |
| `front/app/hooks/useSuggestions.ts` | Suggestions + debounce |
| `front/app/hooks/usePermissions.ts` | Batch permissions |
| `front/app/hooks/useFacetConfig.ts` | Chargement de config /facets |
| `front/app/hooks/useUrlSync.ts` | Synchronisation état ↔ URL |
| `front/app/lib/search-payload.ts` | Construction des payloads de recherche |

## Constraints

- Les composants consommateurs ne doivent pas voir de changement sur l'API publique de `useSearch()`.
- La logique métier doit être déplacée hors du composant context.
- Les stale closures doivent rester maîtrisées dans `useSearchApi`.

## Risks / Follow-up

- Risque de régression si l’état URL est branché trop tôt ou trop tard dans le cycle de vie.
- Risque de couplage entre hooks si `useSearchState` et `useSearchApi` ne sont pas strictement séparés.
- Nécessite une validation Playwright de la recherche complète avant release.
