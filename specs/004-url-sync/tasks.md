# Tasks: URL State Sync

> **Preuve de livraison** (reconciliation feature 014, T018) : spec statut `✅ Livré fonctionnellement` (voir `specs/CHANGELOG.md` 2026-04-20, `specs/PLANNING.md`). Code présent : `front/app/hooks/useUrlSync.ts`, `front/app/lib/url-search-state.ts`, `front/tests/url-sync.spec.ts` (commits `db796b4`, `b0342b8`). Les tâches ci-dessous étaient restées non cochées malgré la livraison ; elles sont réconciliées avec cette preuve.

## Phase 1 — Couche de synchronisation URL

- [x] T001 Créer le hook `front/app/hooks/useUrlSync.ts` avec la logique de lecture des paramètres URL
- [x] T002 Définir les helpers de parsing / encoding dans `front/app/hooks/url-search-state.ts`
- [x] T003 Renseigner la stratégie `router.push` vs `router.replace` selon le type d'événement
- [x] T004 Assurer la restauration d'état depuis l'URL au montage de l'application
- [x] T005 Gérer les cas invalides et les valeurs absentes sans crash de l'UI

## Phase 2 — Intégration dans le contexte

- [x] T006 Brancher le hook `useUrlSync` dans `front/app/context/SearchContext.tsx`
- [x] T007 Synchroniser query, filtres, pagination et mode recherche avec l'URL
- [x] T008 Assurer la compatibilité entre mode simple / mode avancé et les paramètres encodés
- [x] T009 Vérifier le fonctionnement sur les changements de locale (`/fr/`, `/en/`, etc.)
- [x] T010 Maintenir le comportement actuel de recherche lors d'un chargement URL incomplet

## Phase 3 — QueryBuilder et historique

- [x] T011 Implémenter le paramètre dédié au QueryBuilder (`lq=`) avec encodage robuste
- [x] T012 Ajouter le décodage et le fallback sécurisé en cas de JSON invalide
- [x] T013 Vérifier la navigation back / forward avec des recherches successives
- [x] T014 Tester le comportement avec filtres, pages et historique multiple

## Phase 4 — Tests E2E

- [x] T015 Créer le fichier `front/tests/url-sync.spec.ts` pour les scénarios de recherche simple
- [x] T016 Ajouter les cas de filtre, pagination et rechargement de page
- [x] T017 Ajouter les cas de QueryBuilder complexe et d'URL malformée
- [x] T018 Vérifier les scénarios de retour arrière / avant sur plusieurs étapes
- [x] T019 Contrôler la longueur d'URL et l'encodage des paramètres

## Phase 5 — Validation

- [x] T020 Lancer les tests Playwright ciblés sur le sync d'URL
- [x] T021 Corriger les écarts de synchronisation signalés
- [x] T022 Vérifier la cohérence entre URL, état de recherche et rendu visuel
- [x] T023 Finaliser la documentation de la compatibilité des filtres et paramètres
