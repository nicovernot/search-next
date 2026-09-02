# Tasks: Auth LDAP / SSO

## Phase 1 — Backend Auth

- [x] T001 Vérifier les endpoints `auth` existants et leur couverture LDAP / email / SSO
- [x] T002 Finaliser la logique de validation LDAP et l'intégration avec les identités institutionnelles
- [x] T003 Vérifier le flux SSO avec code court à usage unique et gestion des erreurs
- [x] T004 Contrôler les TTL de session et les tokens JWT selon les règles de sécurité
- [x] T005 Valider que les réponses backend restent cohérentes et traduisibles côté frontend

## Phase 2 — Frontend Auth

- [x] T006 Vérifier `AuthContext.tsx` et la persistance de session côté client
- [x] T007 Mettre à jour `AuthModal.tsx` avec les modes d'auth disponibles et les erreurs traduites
- [x] T008 Ajouter l'expérience utilisateur pour le mode LDAP et le mode SSO
- [x] T009 Vérifier les libellés d'interface dans les 6 langues
- [x] T010 Contrôler les cas d'erreur et la reprise sur échec de connexion

## Phase 3 — Sécurité et permissions

- [x] T011 Vérifier que les droits d'accès restent appliqués côté backend et non seulement frontend
- [x] T012 Confirmer le mapping entre session, token JWT et statut d'accès de l'utilisateur
- [x] T013 Contrôler les scénarios d'institutions / access rules / organisation
- [x] T014 Valider les réponses 401, 403 et 409 en cohérence avec le contrat API
- [x] T015 Vérifier les pratiques de sécurité sur les codes court à usage unique

## Phase 4 — Validation

- [x] T016 Lancer les tests d'auth et les tests Playwright ciblés sur l'authentification
- [x] T017 Vérifier la non-régression sur les parcours de recherche protégée
- [x] T018 Contrôler le comportement en environnement local et de staging
- [x] T019 Finaliser la revue des flux de sécurité et de permissions
- [x] T020 Documenter les derniers écarts ou actions de support métier à traiter
