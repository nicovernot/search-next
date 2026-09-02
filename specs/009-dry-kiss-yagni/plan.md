# Plan 009 — DRY, KISS & YAGNI

## Architecture

```
front/
├── app/
│   ├── components/
│   │   ├── AuthModal.tsx          # logique auth + UI
│   │   ├── AutocompleteInput.tsx  # suggestions + dropdown
│   │   ├── SavedSearchesPanel.tsx # CRUD / portal / positionnement
│   │   ├── Facets.tsx            # filtres et labels
│   │   └── Pagination.tsx        # pagination
│   ├── hooks/
│   │   ├── useAnchoredPortal.ts   # logique partagée de portal
│   │   ├── useClickOutside.ts    # logique partagée de fermeture
│   │   ├── useActiveFilters.ts   # calcul unifié des filtres actifs
│   │   └── useIsClient.ts        # guard SSR centralisé
│   ├── lib/
│   │   ├── facet-i18n.ts         # mapping unique pour labels de facettes
│   │   ├── storage-keys.ts       # clés localStorage centralisées
│   │   └── theme.ts              # tokens de style
│   └── globals.css               # styles globaux et tokens
search_api_solr/
├── app/
│   └── services/
│       └── ...                   # logique backend dédupliquée / nommage clarifié
```

## Data Flow

1. Les patterns récurrents comme les portails, le click outside et les filtres actifs sont centralisés dans des hooks partagés.
2. Les libellés de facettes sont calculés dans un seul point pour éviter les divergences entre composants.
3. Les clés de stockage et les valeurs de thème sont traitées via des fichiers de configuration partagés.
4. Les composants de présentation deviennent plus simples et lisibles, sans logique de calcul dupliquée.
5. Le backend garde des fonctions avec des noms explicites et des responsabilités bien délimitées.

## Key Files

| Fichier | Rôle |
|---------|------|
| `front/app/hooks/useAnchoredPortal.ts` | Pattern partagé portal / position |
| `front/app/hooks/useClickOutside.ts` | Pattern partagé de fermeture |
| `front/app/hooks/useActiveFilters.ts` | Calcul de filtres actifs centralisé |
| `front/app/lib/facet-i18n.ts` | Mapping unique de facettes / libellés |
| `front/app/lib/storage-keys.ts` | Clés persistées centralisées |
| `front/app/globals.css` | Style global, tokens et composants réutilisables |
| `search_api_solr/app/services/...` | Nettoyage et clarification des noms backend |

## Rules to Sustain

- Ne pas dupliquer la même logique dans plusieurs composants.
- Les composants doivent rester simples et lisibles : KISS.
- Ne pas ajouter d'abstractions tant qu'un besoin concret n'a pas été validé : YAGNI.
- Les noms doivent refléter l'intention et le résultat, pas la complétude technique.

## Risks / Follow-up

- Risque de sur-abstraction si les helpers partagés sont généralisés trop tôt.
- Nécessite un esprit de discipline: toute duplication détectée doit être centralisée avant d'ajouter de nouvelles features.
- Idéalement validé par l'analyse de cohérence et la revue de code du prochain cycle.
