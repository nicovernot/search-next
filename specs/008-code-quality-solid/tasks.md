# Tasks: Qualité de Code & Principes SOLID

> **Preuve de livraison** (reconciliation feature 014, T020) : spec statut `✅ Livré` (voir `specs/CHANGELOG.md` 2026-04-16, `specs/PLANNING.md`). Code présent : `front/app/lib/api.ts` (appels HTTP centralisés), `front/app/hooks/useSavedSearches.ts` (commit `c330eed` « feat(008): extraire useSavedSearches, ajouter JSDoc hooks — SC-001/SC-004/SC-005 verts »). Les tâches ci-dessous étaient restées non cochées malgré la livraison ; elles sont réconciliées avec cette preuve.

## Phase 1 — Séparation des responsabilités

- [x] T001 Identifier les composants et hooks qui mélangent logique métier et rendu
- [x] T002 Décomposer `SearchContext` et autres points de couplage en responsabilités claires
- [x] T003 Garantir que les composants de présentation ne font plus d'appel API direct
- [x] T004 Définir les interfaces TypeScript plus ciblées par domaine d'usage
- [x] T005 Vérifier la séparation entre logique de recherche et rendu UI

## Phase 2 — API et styles

- [x] T006 Centraliser les appels HTTP dans `front/app/lib/api.ts`
- [x] T007 Supprimer les styles globaux injectés dans les composants
- [x] T008 Déplacer les CSS globaux vers `front/app/globals.css`
- [x] T009 Vérifier les dépendances directes entre composants et services externes
- [x] T010 Contrôler les exceptions documentées pour les adaptateurs tiers

## Phase 3 — Règles de qualité et nommage

- [x] T011 Vérifier les conventions de nommage et les commentaires de responsabilité JDOC
- [x] T012 Limiter les variables et callbacks à des noms explicites
- [x] T013 Refuser les `any` non documentés dans le code frontend
- [x] T014 Vérifier le niveau de clarté des fonctions et des hooks
- [x] T015 Documenter les règles d'exception et les conventions de contribution

## Phase 4 — Validation

- [x] T016 Lancer les contrôles lint / type / tests ciblés sur les fichiers modifiés
- [x] T017 Vérifier qu'aucun fichier d'UI ne contient de logique API directe
- [x] T018 Contrôler que les styles globaux ne sont plus dispersés dans les composants
- [x] T019 Vérifier la cohérence entre comportement, code et documentation
- [x] T020 Finaliser la revue de code pour les intégrations de la spec 007, 009 et 010
