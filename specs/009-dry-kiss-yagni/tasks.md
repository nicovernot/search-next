# Tasks: Principes DRY, KISS & YAGNI

> **Preuve de livraison** (reconciliation feature 014, T021) : spec statut `✅ Livré` (voir `specs/CHANGELOG.md` 2026-04-16, `specs/PLANNING.md`). Code présent : `front/app/lib/facet-i18n.ts`, `front/app/lib/storage-keys.ts` (commit `ffc7bb5` « feat(009): DRY/KISS/YAGNI — corrections P0 et P1 »). Les tâches ci-dessous étaient restées non cochées malgré la livraison ; elles sont réconciliées avec cette preuve.

## Phase 1 — Dédoublonnage des patterns

- [x] T001 Centraliser le mapping des libellés de facettes dans `front/app/lib/facet-i18n.ts`
- [x] T002 Extraire la logique `activeFilters` et éviter les calculs dupliqués
- [x] T003 Centraliser le pattern de portal et de positionnement dans un hook partagé
- [x] T004 Centraliser la logique `click outside` dans un hook réutilisable
- [x] T005 Extraire les clés `localStorage` dans `front/app/lib/storage-keys.ts`

## Phase 2 — Simplification des composants

- [x] T006 Remplacer le spinner dupliqué par un composant réutilisable
- [x] T007 Centraliser le guard SSR dans `useIsClient` ou un composant dédié
- [x] T008 Simplifier l'état d'une recherche active pour un calcul unique `hasActiveSearch`
- [x] T009 Vérifier les composants et hooks qui gardent trop de responsabilités
- [x] T010 Supprimer les valeurs de couleur hardcodées au profit des tokens de thème

## Phase 3 — Backend et clarté

- [x] T011 Identifier les fonctions du backend avec des noms ambiguës ou trop génériques
- [x] T012 Remplacer les noms vagues par des noms expressifs `Intention -> Résultat`
- [x] T013 Vérifier le code mort et les commentaires inutiles dans le backend
- [x] T014 Nettoyer les dépendances et lockfiles obsolètes
- [x] T015 Documenter les principes KISS/YAGNI dans les conventions de contribution

## Phase 4 — Validation

- [x] T016 Lancer les tests ciblés sur le frontend et le backend après nettoyage
- [x] T017 Contrôler les `grep` clés sur le code pour détecter les doublons restants
- [x] T018 Vérifier la cohérence des composants simplifiés avec le design system
- [x] T019 Faire une revue de code sur les fichiers nettoyés
- [x] T020 finaliser la checklist de prévention de la dette technique
