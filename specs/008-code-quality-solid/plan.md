# Plan 008 — Qualité de Code & Principes SOLID

## Architecture

```
front/
├── app/
│   ├── components/
│   │   ├── SavedSearchesPanel.tsx   # logique CRUD et présentation
│   │   ├── AdvancedQueryBuilder.tsx # Logic UI + configuration de champs
│   │   ├── Facets.tsx              # logique de filtrage et rendu
│   │   └── ResultItem.tsx          # rendu visuel / status d'accès
│   ├── context/
│   │   └── SearchContext.tsx       # contexte global + hooks composés
│   ├── hooks/
│   │   ├── useSearchApi.ts         # orchestration / recherche
│   │   ├── useSearchState.ts       # source de vérité de search
│   │   ├── useSuggestions.ts       # suggestions / debounce
│   │   ├── usePermissions.ts       # permissions / batch
│   │   └── useFacetConfig.ts       # config backend / facettes
│   └── lib/
│       └── api.ts                  # point d'entrée API unique
search_api_solr/
├── app/
│   ├── services/
│   │   ├── search_service.py
│   │   └── facet_config.py
│   └── api/
│       └── auth.py
```

## Data Flow

1. Les composants de présentation n'appellent pas directement les API.
2. Les hooks spécialisés encapsulent la logique métier et les dépendances externes.
3. Les états sont centralisés dans `useSearchState` et les appels API dans `useSearchApi`.
4. Les composants ne reçoivent que les données nécessaires à leur rendu.
5. Les règles de qualité sont vérifiées via le lint et la revue de code, plutôt que de corriger les symptômes au fil des changements.

## Key Files

| Fichier | Rôle |
|---------|------|
| `front/app/context/SearchContext.tsx` | Composition du contexte sans logique métier lourde |
| `front/app/hooks/useSearchApi.ts` | Appels API et orchestration de recherche |
| `front/app/hooks/usePermissions.ts` | Permissions et mapping des statuts |
| `front/app/components/SavedSearchesPanel.tsx` | UI + callbacks, sans logique API directe |
| `front/app/components/AdvancedQueryBuilder.tsx` | Rendu des règles QB + données injectées |
| `front/app/lib/api.ts` | Point d'entrée unique pour les appels HTTP |
| `front/app/globals.css` | Styles globaux, hors composants |

## Quality Rules

- Un hook = une responsabilité unique.
- Un composant de présentation ne fait pas d'appel réseau direct.
- Les `any` sont interdits hors adaptateurs tiers explicitement documentés.
- Les styles globaux doivent vivre dans les fichiers globaux, pas dans les composants.
- Les variables doivent exposer intention et résultat, pas juste des raccourcis.

## Risks / Follow-up

- Risque de régression importante si `SearchContext` est modifié sans garder l'interface publique stable.
- Risque de dérive technique si les composants récupèrent leur propres appels API sans passer par des hooks dédiés.
- Nécessite un contrôle régulier sur l'application des règles de style et de structure.
