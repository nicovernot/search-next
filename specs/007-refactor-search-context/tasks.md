# Tasks: Refactorisation SearchContext

## Phase 1 — Extraire les responsabilités

- [x] T001 Créer `front/app/hooks/useSearchState.ts` pour l'état de recherche
- [x] T002 Créer `front/app/hooks/useSearchApi.ts` pour la logique de recherche et stale closures
- [x] T003 Créer `front/app/hooks/useSuggestions.ts` pour le chargement des suggestions
- [x] T004 Créer `front/app/hooks/usePermissions.ts` pour le batch de permissions
- [x] T005 Créer `front/app/hooks/useFacetConfig.ts` pour la configuration des facettes

## Phase 2 — Intégration et composition

- [x] T006 Simplifier `front/app/context/SearchContext.tsx` en assembleur
- [x] T007 Préserver la signature publique de `useSearch()` sans changement de contrat
- [x] T008 Déplacer les états mutationnels hors du contexte vers les hooks dédiés
- [x] T009 S'assurer que les hooks ne dépendent pas mutuellement de logique horizontale
- [x] T010 Vérifier les imports et la cohérence de dépendances entre hooks

## Phase 3 — URL sync et handlers

- [x] T011 Intégrer `useUrlSync` dans le nouveau découpage sans régression
- [x] T012 Garder la logique `latestRef` / `skipEffectRef` dans `useSearchApi`
- [x] T013 Assurer le comportement correct après navigation historique / rechargement
- [x] T014 Vérifier les effets de bord de recherche lors des appels rapides successifs

## Phase 4 — Validation

- [x] T015 Lancer les tests Playwright sur les flux de recherche et résultats
- [x] T016 Vérifier les régressions sur l'autocomplétion et les facettes
- [x] T017 Valider la stabilité du contexte sur plusieurs cycles de recherche
- [x] T018 Finaliser la revue de cohérence avec la spec 004 et la suite de recherche
