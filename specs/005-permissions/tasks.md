# Tasks: Permissions & Accès aux Résultats

## Phase 1 — Backend et flux IP

- [ ] T001 Vérifier le contrat `GET /permissions` côté backend et la logique de forwarding IP
- [ ] T002 Ajuster la route Next.js `front/app/api/permissions/route.ts` pour proxyfier les demandes correctement
- [ ] T003 Assurer la transmission de `X-Forwarded-For` et la priorité des valeurs d'IP
- [ ] T004 Vérifier la compatibilité avec les environnements local / staging / prod
- [ ] T005 Valider le comportement en cas de réponse vide ou de timeout

## Phase 2 — Frontend permissions batch

- [ ] T006 Créer ou finaliser `front/app/hooks/usePermissions.ts`
- [ ] T007 Rassembler les URLs visibles pour l'appel batch `/permissions`
- [ ] T008 Ajouter la gestion de `loadingPermissions`, `organization` et `permissionInfo`
- [ ] T009 Vérifier le comportement non bloquant pendant l'affichage des résultats
- [ ] T010 S'assurer que les erreurs et réponses partielles restent sûres et silencieuses

## Phase 3 — Rendu visuel

- [ ] T011 Mettre à jour `ResultItem.tsx` avec le badge d'accès et les états visuels
- [ ] T012 Ajouter les statuts `open`, `restricted`, `institutional`, `unknown`
- [ ] T013 Afficher les labels et tooltips dans les 6 langues
- [ ] T014 Vérifier la cohérence du rendu lorsque certaines URLs sont absentes ou incomplètes
- [ ] T015 Renforcer la stabilité du layout sans flash ni déplacement brutal

## Phase 4 — Intégration contexte

- [ ] T016 Brancher les permissions dans `SearchContext.tsx` sans casser l'interface publique
- [ ] T017 Faire passer les données au composant `ResultsList.tsx`
- [ ] T018 Vérifier le fallback visuel quand le service de permissions est indisponible
- [ ] T019 assurer le bon mapping entre `PermissionInfo` et `AccessBadge`

## Phase 5 — Tests E2E

- [ ] T020 Créer ou compléter `front/tests/permissions.spec.ts`
- [ ] T021 Tester le badge `open` et `restricted`
- [ ] T022 Tester le badge `institutional` et le cas `unknown`
- [ ] T023 Vérifier le comportement non bloquant et le rendu complet des résultats
- [ ] T024 Lancer les tests ciblés et corriger les écarts signalés
