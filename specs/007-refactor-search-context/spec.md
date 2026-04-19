# Feature Specification: Refactorisation SearchContext

**Feature Branch**: `feature/007-refactor-search-context` (à créer depuis `main`)
**Created**: 2026-04-16
**Status**: ✅ Livré — 5 hooks SOLID + assembler 115 lignes (useUrlSync intégré), 33+ tests Playwright existants

## Overview

`SearchContext.tsx` est actuellement un God Object de ~306 lignes qui cumule 5 responsabilités distinctes : état de recherche, appels API Solr, gestion des suggestions, chargement des permissions, et configuration des facettes. Cette concentration viole le Single Responsibility Principle et rend le contexte difficile à tester, à faire évoluer, et à déboguer.

Cette spec décrit le découpage en hooks spécialisés sans modifier l'interface publique du contexte (aucune régression sur les 33 tests E2E existants).

## Contraintes

- **Aucune régression** : les 33 tests Playwright (auth, saved-searches, search, permissions) doivent rester verts après refactorisation.
- **Interface publique inchangée** : `useSearch()` expose exactement les mêmes propriétés et fonctions — les composants consommateurs ne sont pas modifiés.
- **Pas de nouvelle dépendance** : uniquement React hooks natifs.

## Découpage cible

```
front/app/
├── context/
│   └── SearchContext.tsx        # Assembleur — compose les hooks, expose le contexte
├── hooks/
│   ├── useSearchState.ts        # État brut : query, filters, pagination, mode, logicalQuery
│   ├── useSearchApi.ts          # runSearch, executeSearch, loadSearch, latestRef, skipEffectRef
│   ├── useSuggestions.ts        # fetchSuggestions, suggestions, loadingSuggestions
│   ├── usePermissions.ts        # fetchPermissions, permissions, loadingPermissions, organization
│   └── useFacetConfig.ts        # Chargement /facets/config → facetConfig, searchFields
```

### Responsabilités par hook

| Hook | Responsabilité unique | Dépendances |
|---|---|---|
| `useSearchState` | Détenir et muter l'état de recherche (query, filters, pagination, mode, logicalQuery) | aucune |
| `useSearchApi` | Exécuter les recherches, gérer `latestRef`, exposer `executeSearch` / `loadSearch` | `useSearchState`, `useFacetConfig`, `api.search` |
| `useSuggestions` | Debounce + appel `/suggest`, gérer l'état des suggestions | `api.suggest` |
| `usePermissions` | Batch `/permissions` après chaque page, mapper la réponse en `PermissionsMap` | `api.permissions` |
| `useFacetConfig` | Charger `/facets/config` au montage, exposer `facetConfig` et `searchFields` | `api.facetsConfig` |

## Requirements

### Functional Requirements
- **FR-001**: Chaque hook DOIT avoir une responsabilité unique et ne pas importer d'autres hooks du même dossier (pas de couplage horizontal).
- **FR-002**: `SearchContext.tsx` DOIT se limiter à composer les hooks et alimenter le `Provider` — aucune logique métier directe.
- **FR-003**: L'interface publique de `useSearch()` DOIT rester identique (mêmes noms, mêmes types).
- **FR-004**: Chaque hook DOIT être testable unitairement via `renderHook` sans monter le contexte complet.
- **FR-005**: Le pattern `latestRef` / `skipEffectRef` DOIT rester dans `useSearchApi` — c'est la logique la plus sensible aux stale closures.

### Key Entities
- **`useSearchState`** : source de vérité pour l'état mutable de recherche.
- **`useSearchApi`** : seul hook autorisé à appeler `api.search` et à muter les résultats.
- **`latestRef`** : ref synchronisée après chaque render, lue par `runSearch` pour éviter les stale closures.

## Success Criteria

### Measurable Outcomes
- **SC-001**: Les 33 tests Playwright existants passent sans modification après refactorisation.
- **SC-002**: `SearchContext.tsx` fait moins de 60 lignes après refactorisation.
- **SC-003**: Aucun hook individuel ne dépasse 120 lignes.
- **SC-004**: `grep -n "useState\|useCallback\|useRef\|useEffect" front/app/context/SearchContext.tsx` retourne 0 résultat (toute la logique est dans les hooks).
- **SC-005**: `usePermissions` peut être importé et testé indépendamment de `SearchContext`.

## Plan d'implémentation

### Étape 1 — Extraire `useFacetConfig` (< 1h, risque zéro)

Déplacer le `useEffect` de chargement `/facets/config` et les états `facetConfig` / `searchFields` dans `hooks/useFacetConfig.ts`. C'est le hook le plus isolé — aucune dépendance vers les autres états.

### Étape 2 — Extraire `useSuggestions` (< 1h, risque zéro)

Déplacer `fetchSuggestions`, `suggestions`, `loadingSuggestions` dans `hooks/useSuggestions.ts`. Aucune dépendance vers l'état de recherche.

### Étape 3 — Extraire `usePermissions` (< 1h, risque faible)

Déplacer `fetchPermissions`, `permissions`, `loadingPermissions`, `organization` dans `hooks/usePermissions.ts`. `fetchPermissions` est appelé depuis `runSearch` — passer la fonction en callback ou exposer un setter.

### Étape 4 — Extraire `useSearchState` (< 2h, risque moyen)

Déplacer tous les `useState` de recherche (query, filters, pagination, mode, logicalQuery) et les mutateurs (addFilter, removeFilter, clearFilters, setPage) dans `hooks/useSearchState.ts`.

### Étape 5 — Extraire `useSearchApi` (< 3h, risque élevé)

Déplacer `runSearch`, `executeSearch`, `loadSearch`, `latestRef`, `skipEffectRef` et le `useEffect` de re-déclenchement dans `hooks/useSearchApi.ts`. Ce hook reçoit en paramètre le state de `useSearchState` et les callbacks de `usePermissions`.

### Étape 6 — Simplifier `SearchContext` (< 1h)

`SearchContext.tsx` ne fait plus que composer les 5 hooks et alimenter le `Provider`.

### Étape 7 — Vérification (obligatoire)

```bash
npm run test:e2e   # 33 tests doivent passer
```

## Fichiers à créer / modifier

| Fichier | Action |
|---|---|
| `front/app/hooks/useFacetConfig.ts` | Créer |
| `front/app/hooks/useSuggestions.ts` | Créer |
| `front/app/hooks/usePermissions.ts` | Créer |
| `front/app/hooks/useSearchState.ts` | Créer |
| `front/app/hooks/useSearchApi.ts` | Créer |
| `front/app/context/SearchContext.tsx` | Simplifier (assembleur uniquement) |

## Prérequis pour `004-url-sync`

Une fois cette spec livrée, `004-url-sync` pourra ajouter un hook `useUrlSync.ts` qui s'abonne à `useSearchState` sans toucher à `SearchContext` — le couplage sera minimal et le risque de régression faible.
