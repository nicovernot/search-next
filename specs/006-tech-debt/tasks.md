# Tasks: Corrections & Fondations Techniques

## Phase 1 — Auth et sécurité

- [x] T001 Vérifier la durée de vie du JWT et aligner la config sur 1440 minutes
- [x] T002 Corriger `POST /auth/register` pour retourner `409 Conflict` lors d'email déjà utilisé
- [x] T003 Normaliser les messages d'erreur auth via codes stables et i18n
- [x] T004 Vérifier la propagation des erreurs côté frontend sans fuite de contexte technique
- [x] T005 Contrôler les variables d'environnement de staging et production

## Phase 2 — Client API centralisé

- [x] T006 Créer/compléter `front/app/lib/api.ts` avec les méthodes typées du backend
- [x] T007 Remplacer les `fetch()` dispersés par le client API centralisé
- [x] T008 Assurer l'injection automatique du token Bearer quand disponible
- [x] T009 Documenter l'exception de la route interne `/api/permissions` pour la propagation IP
- [x] T010 Vérifier que toutes les requêtes backend passent par le bon point d'entrée

## Phase 3 — QueryBuilder et config dynamique

- [x] T011 Vérifier l'exposition des `search_fields` via `/facets/config`
- [x] T012 Alimenter `SearchContext` avec les champs QB chargés depuis la configuration
- [x] T013 Faire tomber le fallback `QB_FIELDS` si la config est indisponible
- [x] T014 Adapter `AdvancedQueryBuilder.tsx` pour utiliser les champs dynamiques
- [x] T015 Vérifier que l'ajout de champs backend ne casse pas le rendu frontend

## Phase 4 — Tests et revue

- [x] T016 Ajouter les tests backend ou de validation pour le JWT et les codes de retour
- [x] T017 Ajouter ou compléter les tests frontend pour les messages d'erreur auth
- [x] T018 Vérifier la non-régression sur les mécanismes de recherche avancée
- [x] T019 Faire une revue de code sur les anciens appels `fetch()` dispersés
- [x] T020 Documenter les décisions de fondations dans les docs techniques impactées
