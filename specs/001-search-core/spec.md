# Spec 001 — Search Core

**Status**: ✅ Implemented  
**Branch**: `main`  
**Version**: 1.0.0

## Overview

Moteur de recherche OpenEdition : interface Next.js qui interroge le backend
FastAPI/Solr et affiche les résultats avec facettes et pagination.

## User Stories

- En tant qu'utilisateur, je peux saisir une requête et obtenir des résultats
  paginés depuis le corpus OpenEdition.
- En tant qu'utilisateur, je peux filtrer les résultats par plateforme, type
  de document, accès et langue.
- En tant qu'utilisateur, je peux naviguer entre les pages de résultats.
- En tant qu'utilisateur, je peux changer la langue de l'interface (fr, en,
  es, it, pt).

## Acceptance Criteria

- [ ] La barre de recherche déclenche une recherche après 500 ms de debounce
- [ ] Les résultats affichent titre, auteurs, description tronquée, plateforme, type
- [ ] Les facettes (platform, type, access, translations) s'affichent si non vides
- [ ] Les filtres actifs sont visibles sous forme de tags supprimables
- [ ] La pagination s'affiche dès que `total > 10`
- [ ] Le sélecteur de langue recharge les traductions sans rechargement de page
- [ ] Un skeleton loading s'affiche pendant la requête
- [ ] Les erreurs API sont affichées à l'utilisateur

## Module Boundaries

```
front-next/app/
├── context/SearchContext.tsx   # État global, appels API
├── hooks/useTranslations.ts    # i18n léger
├── components/
│   ├── SearchBar.tsx           # Input + debounce
│   ├── ResultsList.tsx         # Liste + skeleton
│   ├── ResultItem.tsx          # Carte résultat
│   ├── Facets.tsx              # Sidebar filtres
│   ├── FacetGroup.tsx          # Groupe expand/collapse
│   ├── Pagination.tsx          # Navigation pages
│   └── LanguageSelector.tsx    # Sélecteur langue
└── page.tsx                    # Layout principal
```

## API Contract

**POST** `/search`
```json
{
  "query": { "query": "string" },
  "filters": [{ "identifier": "string", "value": "string" }],
  "facets": [{ "identifier": "string", "type": "list" }],
  "pagination": { "from": 0, "size": 10 }
}
```

**Response**
```json
{
  "response": { "docs": [...], "numFound": 0 },
  "facet_counts": { "facet_fields": { "platformID": [...] } }
}
```

## Design Decisions

- `SearchContext` gère tout l'état de recherche (query, filters, pagination,
  results, facets). Pas de state management externe (Redux, Zustand).
- i18n sans librairie lourde : hook `useTranslations` qui charge les JSON
  depuis `/public/locales/`.
- Debounce 500 ms dans `SearchBar` via `useRef<setTimeout>`.
- Facettes Solr au format `[key, count, key, count, ...]` transformées en
  `{ buckets: [{ key, doc_count }] }`.
- Tailwind CSS 4 uniquement, pas de fichiers CSS séparés.

## Test Cases (Playwright End-to-End)

*Note: All End-to-End tests and User Scenarios verifications will be handled by **Playwright** framework as standard for UI/UX integration.*

### SearchContext
- `executeSearch()` avec query vide et sans filtres → ne fait pas d'appel API
- `executeSearch()` avec query → appelle `POST /search` avec le bon body
- `addFilter('platform', 'OpenBooks')` → ajoute le filtre et remet `from` à 0
- `removeFilter` sur dernier filtre d'un champ → supprime la clé du champ
- `setPage(3)` avec `size=10` → `from = 20`

### SearchBar
- Saisie de 3 caractères → déclenche `executeSearch` après 500 ms
- Soumission du formulaire → appelle `executeSearch` immédiatement
- Effacement du champ → déclenche `executeSearch` (query vide)

### Pagination
- `total=0` → ne s'affiche pas
- `total=10` → ne s'affiche pas
- `total=11` → s'affiche avec 2 pages
- `totalPages > 7` → affiche des ellipsis

### FacetGroup
- `buckets.length <= 5` → pas de bouton "voir plus"
- `buckets.length > 5` → bouton "voir plus (N)" visible
- Clic sur checkbox → appelle `onFilterChange(field, value, true/false)`
