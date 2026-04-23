# Spec 001 — Search Core

**Status**: ✅ Implemented  
**Branch**: `main`  
**Version**: 1.1.0

## Overview

Moteur de recherche OpenEdition : interface Next.js qui interroge le backend
FastAPI/Solr et affiche les résultats avec facettes et pagination.

## User Stories

- En tant qu'utilisateur, je peux saisir une requête et obtenir des résultats
  paginés depuis le corpus OpenEdition.
- En tant qu'utilisateur, je peux filtrer les résultats via les filtres
  exposés dynamiquement par le backend (`platform`, `access`, `translations`,
  `type`, `author`, `date`, `subscribers`), avec extension possible via la
  configuration des facettes sans remise en cause du socle existant.
- En tant qu'utilisateur, je peux naviguer entre les pages de résultats.
- En tant qu'utilisateur, je peux changer la langue de l'interface (fr, en,
  es, de, it, pt).

## Acceptance Criteria

- [ ] La barre de recherche propose des suggestions après 300 ms de debounce
- [ ] Les résultats affichent titre, auteurs, description tronquée, plateforme, type
- [ ] Les facettes communes configurées côté backend (`platform`, `access`,
  `translations`, `type`, `author`, `date`, `subscribers`) s'affichent si non
  vides
- [ ] Les facettes spécifiques à la plateforme active sont ajoutées quand un
  filtre `platform` est sélectionné
- [ ] Les filtres actifs sont visibles sous forme de tags supprimables
- [ ] La pagination s'affiche dès que `total > 10`
- [ ] Le sélecteur de langue recharge les traductions sans rechargement de page
- [ ] Un skeleton loading s'affiche pendant la requête
- [ ] Les erreurs API sont affichées à l'utilisateur

## Module Boundaries

```
front/app/
├── context/SearchContext.tsx   # État global, appels API
├── hooks/useFacetConfig.ts     # Charge /facets/config au démarrage
├── lib/search-payload.ts       # Construit le payload dynamique POST /search
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
search_api_solr/app/services/
├── facet_config.py             # Mapping facettes frontend <-> champs Solr
└── facets_json/*.json          # Configuration déclarative des filtres/facettes
```

## API Contract

**POST** `/search`
```json
{
  "query": { "query": "string" },
  "filters": [
    { "identifier": "platform", "value": "OB" },
    { "identifier": "author", "value": "Pierre Bourdieu" }
  ],
  "facets": [
    { "identifier": "platform", "type": "list" },
    { "identifier": "author", "type": "list" },
    { "identifier": "date", "type": "list" }
  ],
  "pagination": { "from": 0, "size": 10 }
}
```

**GET** `/facets/config`
```json
{
  "common": {
    "platform": { "": { "name": "platform", "type": "match", "list": ["platformID"] } },
    "author": { "": { "name": "author", "type": "match", "list": ["contributeurFacetR_auteur"] } },
    "date": { "OB": { "name": "date", "type": "date", "list": ["anneedatepubli"] } }
  },
  "search_fields": ["titre", "author", "naked_texte"]
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
    },
    "author": {
      "buckets": [{ "key": "Pierre Bourdieu", "doc_count": 4 }]
    }
  }
}
```

## Design Decisions

- `SearchContext` gère tout l'état de recherche (query, filters, pagination,
  results, facets). Pas de state management externe (Redux, Zustand).
- Le frontend charge `GET /facets/config` au démarrage, puis construit
  dynamiquement les facettes demandées à `POST /search` à partir de
  `facetConfig.common`.
- i18n via `next-intl` avec routing `[locale]` et fichiers `messages/*.json`.
- Le champ principal utilise l'autocomplétion backend (`GET /suggest`) avec
  debounce 300 ms, puis soumission explicite de la recherche.
- Les facettes consommées par le frontend sont déjà normalisées au format
  `{ buckets: [{ key, doc_count }] }`.
- Les filtres communs de référence sont `platform`, `access`, `translations`,
  `type`, `author`, `date` et `subscribers`.
- Le backend convertit les identifiants de filtres conviviaux vers les champs
  Solr via `facet_config.py`, et étend automatiquement les facettes avec les
  champs spécifiques à une plateforme active.
- Certaines valeurs de filtres sont expansées côté backend avant envoi à Solr
  (ex: `type=article` devient `article OR articlepdf`).
- Tailwind CSS 4 avec `front/app/globals.css` pour les tokens et styles globaux.

## Test Cases (Playwright End-to-End)

*Note: All End-to-End tests and User Scenarios verifications will be handled by **Playwright** framework as standard for UI/UX integration.*

### SearchContext
- `executeSearch()` avec query vide et sans filtres → ne fait pas d'appel API
- `executeSearch()` avec query → appelle `POST /search` avec le bon body
- `addFilter('platform', 'OpenBooks')` → ajoute le filtre et remet `from` à 0
- `removeFilter` sur dernier filtre d'un champ → supprime la clé du champ
- `setPage(3)` avec `size=10` → `from = 20`
- chargement de `facetConfig` → re-déclenche une recherche active pour inclure
  toutes les facettes disponibles

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

### Filtres dynamiques
- `GET /facets/config` expose les facettes communes `platform`, `access`,
  `translations`, `type`, `author`, `date`, `subscribers`
- `type=article` → expansion backend vers plusieurs valeurs Solr
- filtre `platform=OB` actif → ajout des facettes spécifiques de plateforme
  dans la requête Solr
