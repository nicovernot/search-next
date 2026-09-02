# Tasks: URL State Sync

## Phase 1 — Couche de synchronisation URL

- [ ] T001 Créer le hook `front/app/hooks/useUrlSync.ts` avec la logique de lecture des paramètres URL
- [ ] T002 Définir les helpers de parsing / encoding dans `front/app/hooks/url-search-state.ts`
- [ ] T003 Renseigner la stratégie `router.push` vs `router.replace` selon le type d'événement
- [ ] T004 Assurer la restauration d'état depuis l'URL au montage de l'application
- [ ] T005 Gérer les cas invalides et les valeurs absentes sans crash de l'UI

## Phase 2 — Intégration dans le contexte

- [ ] T006 Brancher le hook `useUrlSync` dans `front/app/context/SearchContext.tsx`
- [ ] T007 Synchroniser query, filtres, pagination et mode recherche avec l'URL
- [ ] T008 Assurer la compatibilité entre mode simple / mode avancé et les paramètres encodés
- [ ] T009 Vérifier le fonctionnement sur les changements de locale (`/fr/`, `/en/`, etc.)
- [ ] T010 Maintenir le comportement actuel de recherche lors d'un chargement URL incomplet

## Phase 3 — QueryBuilder et historique

- [ ] T011 Implémenter le paramètre dédié au QueryBuilder (`lq=`) avec encodage robuste
- [ ] T012 Ajouter le décodage et le fallback sécurisé en cas de JSON invalide
- [ ] T013 Vérifier la navigation back / forward avec des recherches successives
- [ ] T014 Tester le comportement avec filtres, pages et historique multiple

## Phase 4 — Tests E2E

- [ ] T015 Créer le fichier `front/tests/url-sync.spec.ts` pour les scénarios de recherche simple
- [ ] T016 Ajouter les cas de filtre, pagination et rechargement de page
- [ ] T017 Ajouter les cas de QueryBuilder complexe et d'URL malformée
- [ ] T018 Vérifier les scénarios de retour arrière / avant sur plusieurs étapes
- [ ] T019 Contrôler la longueur d'URL et l'encodage des paramètres

## Phase 5 — Validation

- [ ] T020 Lancer les tests Playwright ciblés sur le sync d'URL
- [ ] T021 Corriger les écarts de synchronisation signalés
- [ ] T022 Vérifier la cohérence entre URL, état de recherche et rendu visuel
- [ ] T023 Finaliser la documentation de la compatibilité des filtres et paramètres
