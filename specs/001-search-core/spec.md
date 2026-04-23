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
- En tant qu'utilisateur, je peux filtrer les résultats via les filtres
  actuellement disponibles (plateforme, type de document, accès et langue),
  avec une structure prévue pour accueillir d'autres filtres plus tard sans
  remise en cause du socle existant.
- En tant qu'utilisateur, je peux naviguer entre les pages de résultats.
- En tant qu'utilisateur, je peux changer la langue de l'interface (fr, en,
  es, de, it, pt).

## Acceptance Criteria

- [ ] La barre de recherche propose des suggestions après 300 ms de debounce
- [ ] Les résultats affichent titre, auteurs, description tronquée, plateforme, type
- [ ] Les facettes actuelles (platform, type, access, translations)
  s'affichent si non vides
- [ ] Les filtres actifs sont visibles sous forme de tags supprimables
- [ ] La pagination s'affiche dès que `total > 10`
- [ ] Le sélecteur de langue recharge les traductions sans rechargement de page
- [ ] Un skeleton loading s'affiche pendant la requête
- [ ] Les erreurs API sont affichées à l'utilisateur

## Module Boundaries

```
front/app/
├── context/SearchContext.tsx   # État global, appels API
├── [locale]/                   # Routing localisé next-intl
├── components/
│   ├── SearchBar.tsx           # Input + autocomplétion
│   ├── ResultsList.tsx         # Liste + skeleton
│   ├── ResultItem.tsx          # Carte résultat
│   ├── Facets.tsx              # Sidebar filtres
│   ├── FacetGroup.tsx          # Groupe expand/collapse
│   ├── Pagination.tsx          # Navigation pages
│   └── LanguageSelector.tsx    # Sélecteur langue
├── globals.css                 # Tokens CSS/Tailwind v4 et styles globaux
└── [locale]/page.tsx           # Layout principal
front/
├── messages/                   # Traductions next-intl
└── i18n/                       # Routing et navigation
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
  "results": [...],
  "total": 0,
  "facets": {
    "platform": {
      "buckets": [{ "key": "OpenEdition Books", "doc_count": 12 }]
    }
  }
}
```

## Design Decisions

- `SearchContext` gère tout l'état de recherche (query, filters, pagination,
  results, facets). Pas de state management externe (Redux, Zustand).
- i18n via `next-intl` avec routing `[locale]` et fichiers `messages/*.json`.
- Le champ principal utilise l'autocomplétion backend (`GET /suggest`) avec
  debounce 300 ms, puis soumission explicite de la recherche.
- Les facettes consommées par le frontend sont déjà normalisées au format
  `{ buckets: [{ key, doc_count }] }`.
- Les filtres actuellement exposés constituent le périmètre de référence du
  produit ; de nouveaux filtres pourront être ajoutés ultérieurement sans
  invalider ce comportement de base.
- Tailwind CSS 4 avec `front/app/globals.css` pour les tokens et styles globaux.

## Test Cases (Playwright End-to-End)

*Note: All End-to-End tests and User Scenarios verifications will be handled by **Playwright** framework as standard for UI/UX integration.*

### SearchContext
- `executeSearch()` avec query vide et sans filtres → ne fait pas d'appel API
- `executeSearch()` avec query → appelle `POST /search` avec le bon body
- `addFilter('platform', 'OpenBooks')` → ajoute le filtre et remet `from` à 0
- `removeFilter` sur dernier filtre d'un champ → supprime la clé du champ
- `setPage(3)` avec `size=10` → `from = 20`

### SearchBar
- Saisie de 2 caractères ou plus → déclenche la récupération des suggestions après 300 ms
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
