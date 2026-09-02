# Plan 004 — URL State Sync

## Architecture

```
front/
├── app/
│   ├── [locale]/layout.tsx        # Suspense root pour useSearchParams
│   ├── context/
│   │   └── SearchContext.tsx      # état global + hydratation + sync URL
│   ├── hooks/
│   │   ├── useUrlSync.ts          # lecture / écriture d'URL
│   │   └── url-search-state.ts    # helpers de parsing / encoding
│   └── lib/
│       └── search-payload.ts      # logique commune payload + serialisation
└── tests/
    └── url-sync.spec.ts           # validations E2E Playwright
```

## Data Flow

1. `useUrlSync` se branche sur `useSearchParams` pour écouter les changements d'URL.
2. Au montage, l'état de la recherche est restauré depuis les paramètres de requête.
3. `SearchContext` applique l'état hydraté et déclenche la recherche correspondante.
4. Après chaque changement de query, filtre, page ou mode, l'URL est synchronisée avec `router.push` ou `router.replace` selon le type de mutation.
5. Les changements d'historique navigateur réhydratent les filtres et le QueryBuilder depuis l'URL.
6. Les paramètres invalides sont ignorés sans casser l'UI.

## Key Files

| Fichier | Rôle |
|---------|------|
| `front/app/hooks/useUrlSync.ts` | Synchronise l'état React avec l'URL |
| `front/app/hooks/url-search-state.ts` | Parse/encode les paramètres URL |
| `front/app/context/SearchContext.tsx` | Orchestration de la recherche et du contexte |
| `front/app/lib/search-payload.ts` | Construit le payload de requête |
| `front/app/[locale]/layout.tsx` | Fournit le contexte `Suspense` nécessaire |
| `front/tests/url-sync.spec.ts` | Vérification Playwright des cas URL / history |

## Behaviors to Preserve

- `q`, filtres, page, mode simple/avancé doivent rester cohérents.
- Les liens partagés doivent restaurer exactement le même état.
- Les changements de page et de filtres ne doivent pas générer de bruit historique inutile.
- L'URL doit rester lisible et stable même avec un QueryBuilder complexe.

## Risks / Follow-up

- Risque de régression sur le navigateur back/forward si plusieurs états partagent un même paramètre.
- Risque d'URL trop longue avec logique avancée, nécessitant un encodage robuste.
- Les transformations de payload doivent rester compatibles avec les futures extensions de filtres.
