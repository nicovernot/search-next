# Tasks: Auth LDAP / SSO

## Phase 1 — Backend Auth

- [ ] T001 Vérifier les endpoints `auth` existants et leur couverture LDAP / email / SSO
- [ ] T002 Finaliser la logique de validation LDAP et l'intégration avec les identités institutionnelles
- [ ] T003 Vérifier le flux SSO avec code court à usage unique et gestion des erreurs
- [ ] T004 Contrôler les TTL de session et les tokens JWT selon les règles de sécurité
- [ ] T005 Valider que les réponses backend restent cohérentes et traduisibles côté frontend

## Phase 2 — Frontend Auth

- [ ] T006 Vérifier `AuthContext.tsx` et la persistance de session côté client
- [ ] T007 Mettre à jour `AuthModal.tsx` avec les modes d'auth disponibles et les erreurs traduites
- [ ] T008 Ajouter l'expérience utilisateur pour le mode LDAP et le mode SSO
- [ ] T009 Vérifier les libellés d'interface dans les 6 langues
- [ ] T010 Contrôler les cas d'erreur et la reprise sur échec de connexion

## Phase 3 — Sécurité et permissions

- [ ] T011 Vérifier que les droits d'accès restent appliqués côté backend et non seulement frontend
- [ ] T012 Confirmer le mapping entre session, token JWT et statut d'accès de l'utilisateur
- [ ] T013 Contrôler les scénarios d'institutions / access rules / organisation
- [ ] T014 Valider les réponses 401, 403 et 409 en cohérence avec le contrat API
- [ ] T015 Vérifier les pratiques de sécurité sur les codes court à usage unique

## Phase 4 — Validation

- [ ] T016 Lancer les tests d'auth et les tests Playwright ciblés sur l'authentification
- [ ] T017 Vérifier la non-régression sur les parcours de recherche protégée
- [ ] T018 Contrôler le comportement en environnement local et de staging
- [ ] T019 Finaliser la revue des flux de sécurité et de permissions
- [ ] T020 Documenter les derniers écarts ou actions de support métier à traiter
