# Tasks: Principes DRY, KISS & YAGNI

## Phase 1 — Dédoublonnage des patterns

- [ ] T001 Centraliser le mapping des libellés de facettes dans `front/app/lib/facet-i18n.ts`
- [ ] T002 Extraire la logique `activeFilters` et éviter les calculs dupliqués
- [ ] T003 Centraliser le pattern de portal et de positionnement dans un hook partagé
- [ ] T004 Centraliser la logique `click outside` dans un hook réutilisable
- [ ] T005 Extraire les clés `localStorage` dans `front/app/lib/storage-keys.ts`

## Phase 2 — Simplification des composants

- [ ] T006 Remplacer le spinner dupliqué par un composant réutilisable
- [ ] T007 Centraliser le guard SSR dans `useIsClient` ou un composant dédié
- [ ] T008 Simplifier l'état d'une recherche active pour un calcul unique `hasActiveSearch`
- [ ] T009 Vérifier les composants et hooks qui gardent trop de responsabilités
- [ ] T010 Supprimer les valeurs de couleur hardcodées au profit des tokens de thème

## Phase 3 — Backend et clarté

- [ ] T011 Identifier les fonctions du backend avec des noms ambiguës ou trop génériques
- [ ] T012 Remplacer les noms vagues par des noms expressifs `Intention -> Résultat`
- [ ] T013 Vérifier le code mort et les commentaires inutiles dans le backend
- [ ] T014 Nettoyer les dépendances et lockfiles obsolètes
- [ ] T015 Documenter les principes KISS/YAGNI dans les conventions de contribution

## Phase 4 — Validation

- [ ] T016 Lancer les tests ciblés sur le frontend et le backend après nettoyage
- [ ] T017 Contrôler les `grep` clés sur le code pour détecter les doublons restants
- [ ] T018 Vérifier la cohérence des composants simplifiés avec le design system
- [ ] T019 Faire une revue de code sur les fichiers nettoyés
- [ ] T020 finaliser la checklist de prévention de la dette technique
