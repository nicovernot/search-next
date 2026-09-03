# Tasks: Permissions & Accès aux Résultats

> **Preuve de livraison** (reconciliation feature 014, T019) : spec statut `✅ Livré` (voir `specs/CHANGELOG.md` 2026-04-16, `specs/PLANNING.md`). Code présent : `front/app/hooks/usePermissions.ts`, `front/app/api/permissions/route.ts`, `front/tests/permissions.spec.ts` (commits `992fdfe`, `76d4c1d`). Les tâches ci-dessous étaient restées non cochées malgré la livraison ; elles sont réconciliées avec cette preuve.

## Phase 1 — Backend et flux IP

- [x] T001 Vérifier le contrat `GET /permissions` côté backend et la logique de forwarding IP
- [x] T002 Ajuster la route Next.js `front/app/api/permissions/route.ts` pour proxyfier les demandes correctement
- [x] T003 Assurer la transmission de `X-Forwarded-For` et la priorité des valeurs d'IP
- [x] T004 Vérifier la compatibilité avec les environnements local / staging / prod
- [x] T005 Valider le comportement en cas de réponse vide ou de timeout

## Phase 2 — Frontend permissions batch

- [x] T006 Créer ou finaliser `front/app/hooks/usePermissions.ts`
- [x] T007 Rassembler les URLs visibles pour l'appel batch `/permissions`
- [x] T008 Ajouter la gestion de `loadingPermissions`, `organization` et `permissionInfo`
- [x] T009 Vérifier le comportement non bloquant pendant l'affichage des résultats
- [x] T010 S'assurer que les erreurs et réponses partielles restent sûres et silencieuses

## Phase 3 — Rendu visuel

- [x] T011 Mettre à jour `ResultItem.tsx` avec le badge d'accès et les états visuels
- [x] T012 Ajouter les statuts `open`, `restricted`, `institutional`, `unknown`
- [x] T013 Afficher les labels et tooltips dans les 6 langues
- [x] T014 Vérifier la cohérence du rendu lorsque certaines URLs sont absentes ou incomplètes
- [x] T015 Renforcer la stabilité du layout sans flash ni déplacement brutal

## Phase 4 — Intégration contexte

- [x] T016 Brancher les permissions dans `SearchContext.tsx` sans casser l'interface publique
- [x] T017 Faire passer les données au composant `ResultsList.tsx`
- [x] T018 Vérifier le fallback visuel quand le service de permissions est indisponible
- [x] T019 assurer le bon mapping entre `PermissionInfo` et `AccessBadge`

## Phase 5 — Tests E2E

- [x] T020 Créer ou compléter `front/tests/permissions.spec.ts`
- [x] T021 Tester le badge `open` et `restricted`
- [x] T022 Tester le badge `institutional` et le cas `unknown`
- [x] T023 Vérifier le comportement non bloquant et le rendu complet des résultats
- [x] T024 Lancer les tests ciblés et corriger les écarts signalés
