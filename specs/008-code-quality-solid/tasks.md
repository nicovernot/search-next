# Tasks: Qualité de Code & Principes SOLID

## Phase 1 — Séparation des responsabilités

- [ ] T001 Identifier les composants et hooks qui mélangent logique métier et rendu
- [ ] T002 Décomposer `SearchContext` et autres points de couplage en responsabilités claires
- [ ] T003 Garantir que les composants de présentation ne font plus d'appel API direct
- [ ] T004 Définir les interfaces TypeScript plus ciblées par domaine d'usage
- [ ] T005 Vérifier la séparation entre logique de recherche et rendu UI

## Phase 2 — API et styles

- [ ] T006 Centraliser les appels HTTP dans `front/app/lib/api.ts`
- [ ] T007 Supprimer les styles globaux injectés dans les composants
- [ ] T008 Déplacer les CSS globaux vers `front/app/globals.css`
- [ ] T009 Vérifier les dépendances directes entre composants et services externes
- [ ] T010 Contrôler les exceptions documentées pour les adaptateurs tiers

## Phase 3 — Règles de qualité et nommage

- [ ] T011 Vérifier les conventions de nommage et les commentaires de responsabilité JDOC
- [ ] T012 Limiter les variables et callbacks à des noms explicites
- [ ] T013 Refuser les `any` non documentés dans le code frontend
- [ ] T014 Vérifier le niveau de clarté des fonctions et des hooks
- [ ] T015 Documenter les règles d'exception et les conventions de contribution

## Phase 4 — Validation

- [ ] T016 Lancer les contrôles lint / type / tests ciblés sur les fichiers modifiés
- [ ] T017 Vérifier qu'aucun fichier d'UI ne contient de logique API directe
- [ ] T018 Contrôler que les styles globaux ne sont plus dispersés dans les composants
- [ ] T019 Vérifier la cohérence entre comportement, code et documentation
- [ ] T020 Finaliser la revue de code pour les intégrations de la spec 007, 009 et 010
