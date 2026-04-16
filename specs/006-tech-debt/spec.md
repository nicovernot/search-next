# Feature Specification: Corrections & Fondations Techniques

**Feature Branch**: `feature/002-advanced-search-suite` (intégrée dans la branche courante)
**Created**: 2026-04-15
**Updated**: 2026-04-15
**Status**: ✅ Complète — tous les correctifs livrés

## Overview

Série de corrections et d'améliorations techniques identifiées lors de l'audit d'architecture. Ces changements ne modifient pas le comportement visible de l'application mais améliorent la robustesse, la maintenabilité et posent les fondations pour les specs 005 et 004.

## Contexte

L'audit du 2026-04-15 a identifié les problèmes suivants dans le codebase :
- Token JWT expirant après 30 min (spec 002 requiert 1440 min)
- Code HTTP 502 retourné au lieu de 409 en cas d'email déjà utilisé
- Messages d'erreur auth non traduits (rupture i18n)
- 7 appels `fetch()` dispersés dans 4 fichiers sans client API centralisé
- Champs QueryBuilder hardcodés au lieu de venir de la config Solr

Ces corrections sont indépendantes les unes des autres et peuvent être traitées en parallèle.

---

## User Scenarios & Testing (Playwright)

### User Story 1 — Token JWT longue durée (Priority: P0)
En tant qu'utilisateur authentifié, je veux rester connecté pendant au moins 24h sans être déconnecté en plein travail de recherche.
**Why**: Le token expirait après 30 min en dev, forçant une reconnexion non justifiée.
**Independent Test**: Vérifier que le token émis au login a une durée de vie de 1440 min (champ `exp` dans le payload JWT).

### User Story 2 — Message d'erreur email existant (Priority: P1)
En tant qu'utilisateur tentant de s'inscrire avec un email déjà utilisé, je veux recevoir un message d'erreur clair et traduit — pas une erreur 502 serveur.
**Why**: Le frontend interprète un 502 comme une erreur serveur, ce qui masque le vrai problème.
**Independent Test**: POST /auth/register avec un email déjà enregistré → réponse 409, message clair côté UI, traduit dans la langue courante.

### User Story 3 — Erreurs auth traduites (Priority: P1)
En tant qu'utilisateur en mode FR/ES/DE/IT/PT, je veux voir les messages d'erreur d'authentification dans ma langue.
**Why**: Les messages "auth_error" / "register_error" étaient hardcodés en chaînes brutes non passées par next-intl.
**Independent Test**: Tenter une connexion avec mauvais mot de passe en mode ES → message d'erreur en espagnol.

### User Story 4 — Client API centralisé (Priority: P2, fondation)
En tant que développeur, je veux que tous les appels à l'API backend passent par un client unique qui gère automatiquement les headers d'authentification, la base URL et les erreurs réseau.
**Why**: 7 appels `fetch()` dispersés rendent l'ajout d'un header ou le changement de base URL fastidieux et source d'oublis.
**Independent Test**: (pas de test E2E visible, validation par revue de code) — tous les appels fetch passent par `lib/api.ts`.

### User Story 5 — Champs QueryBuilder depuis la config (Priority: P2, fondation)
En tant que développeur, je veux que les champs du QueryBuilder soient chargés depuis la configuration backend plutôt que hardcodés, afin de pouvoir ajouter un champ de recherche avancée sans modifier le code frontend.
**Why**: `AdvancedQueryBuilder.tsx` liste en dur `titre`, `author`, `naked_texte`, `disciplinary_field`. Tout ajout nécessite un commit frontend.
**Independent Test**: Ajouter un champ dans `facets_json/common.json` → il apparaît dans le QueryBuilder sans toucher au code React.

### Edge Cases
- Client API : si `NEXT_PUBLIC_API_URL` est absent, le client doit logger une erreur explicite au démarrage.
- Champs QB depuis config : si `/facets/config` est indisponible au chargement, fallback sur un set minimal de champs hardcodés.
- Token 1440 min : vérifier que les fichiers `.env.staging` et `.env.production` ont des valeurs appropriées (staging : 480 min, prod : 1440 min).

---

## Requirements

### Functional Requirements

- **FR-001**: La durée de vie du token JWT DOIT être de 1440 min en développement et production.
- **FR-002**: `POST /auth/register` avec email existant DOIT retourner `HTTP 409 Conflict` (pas 502).
- **FR-003**: Les messages d'erreur d'authentification DOIT utiliser les clés next-intl (pas de strings hardcodées).
- **FR-004**: Tous les appels à l'API backend DOIVENT passer par un module centralisé `front/app/lib/api.ts`.
- **FR-005**: Le module `api.ts` DOIT injecter automatiquement le header `Authorization: Bearer <token>` si un token est présent en session.
- **FR-006**: Les champs de recherche du QueryBuilder DOIVENT être chargés depuis `GET /facets/config` au démarrage.

### Key Entities

- **`ApiClient`** (`front/app/lib/api.ts`) : module exportant des fonctions typées pour chaque endpoint (`search`, `suggest`, `facetsConfig`, `login`, `register`, `getSavedSearches`, `createSavedSearch`, `deleteSavedSearch`, `permissions`).
- **`searchFields`** : liste de champs chargée depuis `/facets/config` et exposée par `SearchContext`.
- **`QB_FIELDS`** : liste de fallback utilisée si `/facets/config` est indisponible.

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: Le payload JWT émis en dev a `exp - iat = 86400s` (1440 min × 60).
- **SC-002**: `POST /auth/register` avec email existant retourne HTTP 409, et l'UI affiche un message traduit.
- **SC-003**: `AuthContext.tsx` ne renvoie que des codes d'erreur stables (`auth_error`, `email_exists`, `register_error`) ; `AuthModal.tsx` les mappe vers `t()` (next-intl).
- **SC-004**: `grep -r "await fetch(" front/app/` ne retourne aucun résultat hors de `lib/api.ts`.
- **SC-005**: `AdvancedQueryBuilder.tsx` utilise `searchFields` depuis le contexte quand `/facets/config` répond, avec `QB_FIELDS` comme fallback documenté.

### Couverture de test

| Fichier | Cas à couvrir |
|---------|---------------|
| `tests/auth.spec.ts` | Register email existant, login incorrect, persistance session et affichage d'erreur côté UI |
| Test backend ou script de validation env | Token émis avec `exp - iat = 86400s` (1440 min) — à ajouter si on veut automatiser ce contrôle |

---

## État d'avancement (2026-04-15)

| Correctif | FR | Statut |
|-----------|----|----|
| Token JWT 1440 min | FR-001 | ✅ Livré — `settings.py` default=1440, `.env.development` confirmé |
| HTTP 409 email existant | FR-002 | ✅ Livré — `api/auth.py` retourne `HTTP_409_CONFLICT` |
| Erreurs auth traduites | FR-003 | ✅ Livré — codes → `t()` dans AuthModal, 6 langues |
| Client API centralisé | FR-004/005 | ✅ Livré — `lib/api.ts`, tous contextes migrés |
| Champs QB depuis config | FR-006 | ✅ Livré — `GET /facets/config` expose `search_fields`, `SearchContext` le charge dans `searchFields`, fallback sur `QB_FIELDS` si API indisponible |

---

## Plan d'implémentation

### Étape 1 — Corrections backend (< 4h) ✅ FAIT

1. `search_api_solr/app/api/auth.py:25` : `HTTP_400_BAD_GATEWAY` → `HTTP_409_CONFLICT`
2. `search_api_solr/app/settings.py` : valeur par défaut `ACCESS_TOKEN_EXPIRE_MINUTES = 1440`
3. `scripts/sync_env.sh` + `.env.development` : ajouter `ACCESS_TOKEN_EXPIRE_MINUTES=1440`

### Étape 2 — i18n erreurs auth (< 2h) ✅ FAIT

- Clés `authError`, `emailAlreadyExists`, `registerError`, `passwordMismatch` dans les 6 fichiers `front/messages/*.json`
- `AuthContext.tsx` : émet des codes (`"auth_error"`, `"email_exists"`, `"register_error"`)
- `AuthModal.tsx` : mappe codes → `t()` (pattern adapté, fonctionnel)

### Étape 3 — Client API centralisé (< 1 jour) ✅ FAIT

- `front/app/lib/api.ts` créé avec toutes les méthodes typées
- `SearchContext.tsx`, `AuthContext.tsx`, `SavedSearchesPanel.tsx` utilisent tous `api.*`

### Étape 4 — Champs QB depuis config (< 1 jour) ✅ FAIT

1. Backend : `GET /facets/config` expose `search_fields` depuis `SEARCH_FIELDS_MAPPING`
2. Frontend : `SearchContext` charge `search_fields` au montage et expose `searchFields`
3. `AdvancedQueryBuilder` utilise `searchFields` si disponible
4. Fallback si config indisponible : `QB_FIELDS` dans `front/app/lib/qb-fields.ts`

---

## Fichiers à modifier

| Fichier | Modification |
|---------|-------------|
| `search_api_solr/app/api/auth.py` | HTTP 409 pour email existant |
| `search_api_solr/app/settings.py` | Token TTL par défaut 1440 min |
| `scripts/sync_env.sh` | Ajouter ACCESS_TOKEN_EXPIRE_MINUTES |
| `.env.development` | ACCESS_TOKEN_EXPIRE_MINUTES=1440 |
| `front/messages/*.json` (×6) | Clés erreurs auth |
| `front/app/context/AuthContext.tsx` | Codes d'erreur stables |
| `front/app/components/AuthModal.tsx` | Mapping codes d'erreur → `t()` |
| `front/app/lib/api.ts` | Nouveau fichier — client API |
| `front/app/context/SearchContext.tsx` | Remplacer fetch() par api.* |
| `front/app/components/SavedSearchesPanel.tsx` | Remplacer fetch() par api.* |
| `front/app/components/AdvancedQueryBuilder.tsx` | Utilise `searchFields` depuis le contexte, fallback `QB_FIELDS` |
