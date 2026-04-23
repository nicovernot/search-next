# Feature Specification: URL State Sync

**Feature Branch**: `feature/002-advanced-search-suite`  
**Created**: 2026-04-13  
**Status**: Livré — 2026-04-19

## Overview

Synchroniser l'état complet de la recherche (query, filtres actifs, page courante, mode simple/avancé) avec les paramètres d'URL, afin de permettre le partage de liens et la navigation back/forward du navigateur. Le mécanisme doit couvrir les filtres actuellement disponibles et rester compatible avec l'ajout futur de nouveaux filtres.

## Implémentation

Hook `front/app/hooks/useUrlSync.ts` intégré dans `SearchContext` via `front/app/context/SearchContext.tsx`.

- **Hydratation au montage** : lit l'URL et restaure l'état via `loadSearch`
- **Sync état → URL** : `router.push` sur changement de query (nouvelle recherche), `router.replace` pour les changements de page/filtre/mode (raffinements)
- **Back/forward (FR-003)** : détecte les changements de `useSearchParams` non provoqués par l'application et ré-hydrate l'état depuis l'URL
- **QB (P2)** : paramètre `lq=` en JSON encodé, parsing robuste avec fallback silencieux si malformé

`front/app/[locale]/layout.tsx` enveloppé dans `<Suspense>` (requis par `useSearchParams` dans Next.js App Router).

## User Scenarios & Testing (Playwright)

*Note: All End-to-End tests must be implemented using **Playwright** framework.*

### User Story 1 - Lien partageable (Priority: P0)
En tant qu'utilisateur, je veux pouvoir copier l'URL de ma page de résultats et l'envoyer à un collègue qui obtiendra exactement la même recherche (même query, mêmes filtres, même page), sans avoir à re-construire manuellement la requête.  
**Why this priority**: C'est le use-case le plus demandé — partage d'une recherche précise entre collaborateurs.  
**Independent Test**: Après une recherche avec filtres et pagination, l'URL contient les paramètres encodés. Ouvrir cette URL dans un nouvel onglet restitue fidèlement l'état (résultats identiques, filtres actifs visibles, bonne page).

### User Story 2 - Navigation back/forward (Priority: P1)
En tant qu'utilisateur, je veux pouvoir utiliser les boutons Précédent / Suivant du navigateur pour revenir à une recherche précédente ou avancer dans mon historique de navigation.  
**Why this priority**: Comportement attendu de tout site web — son absence crée de la frustration.  
**Independent Test**: Depuis une recherche A, lancer une recherche B, cliquer Précédent → revenir à A (query, filtres, page corrects). Cliquer Suivant → revenir à B.

### User Story 3 - Permalien de recherche avancée (Priority: P2)
En tant qu'utilisateur avancé, je veux que ma requête logique (AND/OR/NOT construite via le QueryBuilder) soit encodée dans l'URL afin de pouvoir la sauvegarder dans mes favoris ou la partager.  
**Why this priority**: Complément naturel de la recherche avancée (spec 002). Complexité supérieure car le payload JSON doit être encodé de façon lisible et robuste.  
**Independent Test**: Après une requête logique complexe en mode avancé, l'URL contient un paramètre encodé. Copier-coller l'URL dans un nouvel onglet restitue le QueryBuilder dans le même état et affiche les résultats.

### Edge Cases
- URL avec paramètres invalides (filtre inexistant, page hors limites) → la recherche se lance avec les paramètres valides, les invalides sont ignorés silencieusement.
- Recherche vide avec filtres → l'URL reflète les filtres mais aucun résultat n'est affiché (comportement actuel conservé).
- QueryBuilder JSON malformé dans l'URL → fallback vers la recherche simple, sans crash.
- Changement de locale (`/fr/` → `/en/`) → les paramètres de recherche sont conservés dans l'URL.

## Requirements

### Functional Requirements
- **FR-001** ✅ : L'URL DOIT refléter en temps réel la query (`q=`), les filtres actifs (`f_[field]=value`), la page (`page=`) et le mode de recherche (`mode=simple|advanced`), en conservant les filtres actuels comme référence tout en permettant l'ajout ultérieur de nouveaux champs de filtre.
- **FR-002** ✅ : Le chargement d'une URL avec paramètres DOIT restaurer l'état de recherche et lancer la recherche automatiquement.
- **FR-003** ✅ : La navigation back/forward DOIT mettre à jour l'état de recherche en cohérence avec l'URL visitée.
- **FR-004** ✅ : La mise à jour de l'URL DOIT utiliser `router.push` (nouvelle entrée d'historique) pour les nouvelles recherches, et `router.replace` (remplacement silencieux) pour les changements de page/filtre/mode.
- **FR-005** ✅ : Le payload de requête logique avancée DOIT être encodé dans l'URL via un paramètre dédié (`lq=`) et décodé sans perte à la restauration.

### Key Entities
- **useUrlSync** : hook autonome, branché dans `SearchContext`. Expose aucune API — effet de bord pur.
- **parseSavedSearchData** : fonction pure (interne au hook) qui lit un `URLSearchParams` et produit un `SavedSearchData`.

## Success Criteria

### Measurable Outcomes
- **SC-001** ✅ : L'URL est mise à jour dans les 50 ms suivant chaque interaction utilisateur (frappe, filtre, page).
- **SC-002** ✅ : La restauration depuis URL aboutit à un état de recherche identique à celui qui a produit l'URL (résultats, filtres, page visibles).
- **SC-003** ✅ : La navigation back/forward fonctionne sur au moins 5 étapes d'historique consécutives sans désynchronisation.
- **SC-004** ✅ : L'encodage du payload QueryBuilder dans l'URL est lisible (JSON non obfusqué) et tient dans une URL < 2 000 caractères pour les cas courants (≤ 3 niveaux, ≤ 5 règles).

### Tests Playwright
| Fichier | Cas couverts |
|---|---|
| `tests/url-sync.spec.ts` | URL mise à jour après recherche simple, filtre, changement de page, bascule mode avancé/simple, rechargement de page, hydratation depuis URL (query, mode, filtre, page), back/forward (2 directions, avec filtre), changements de page en replaceState, paramètres invalides (page négative, size non numérique, lq malformé, champ inexistant), restauration QB simple, QB imbriqué (AND/OR), vérification longueur URL < 2000 |
