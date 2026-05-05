# Feature Specification: Authentification LDAP et SSO

**Feature Branch**: `feature/002-advanced-search-suite` (livré sur la branche principale)  
**Created**: 2026-04-17  
**Status**: ✅ Livré — backend (ldap_service, oidc_service, endpoints, migration) + frontend (AuthModal, AuthContext, api.ts, i18n 6 langues). Transport JWT SSO sécurisé : code court hex32 via Redis, échangé par `/auth/sso/exchange`.

## Overview

Étendre le système d'authentification actuel (email/password bcrypt + JWT) pour prendre en charge deux modes fédérés : LDAP (annuaire institutionnel) et SSO (Single Sign-On via OIDC/OAuth2, SAML 2.0, ou CAS). L'authentification locale reste disponible en parallèle pour les comptes non fédérés.

L'objectif est de permettre aux membres d'institutions partenaires (universités, laboratoires) de se connecter avec leurs identifiants institutionnels sans créer un compte dédié sur OpenEdition Search.

---

## User Scenarios & Testing (Playwright)

*Note: All End-to-End tests must be implemented using **Playwright** framework.*

### User Story 1 — Connexion LDAP institutionnelle (Priority: P0)

En tant que chercheur d'une université utilisant un annuaire LDAP, je veux pouvoir me connecter à OpenEdition Search avec mon identifiant et mot de passe institutionnel, sans créer un compte séparé.  
**Why this priority**: Cas d'usage le plus fréquent dans les institutions académiques françaises. Évite la multiplication des mots de passe.  
**Independent Test**: Sur l'interface de login, entrer des identifiants LDAP valides → session ouverte, email LDAP affiché. Entrer des identifiants LDAP invalides → message d'erreur explicite. L'utilisateur peut ensuite sauvegarder des recherches.

### User Story 2 — Connexion SSO via bouton institutionnel (Priority: P0)

En tant qu'utilisateur d'une institution partenaire, je veux cliquer sur un bouton "Se connecter avec mon institution" qui me redirige vers le fournisseur d'identité (IdP) de mon institution, sans saisir mes identifiants directement sur OpenEdition.  
**Why this priority**: Standard de sécurité dans l'ESR — les institutions ne veulent pas que leurs mots de passe transitent par des tiers.  
**Independent Test**: Cliquer "Se connecter via SSO" → redirection vers l'IdP configuré. Après authentification réussie sur l'IdP → callback reçu, session JWT créée, retour sur l'application avec session active.

### User Story 3 — Coexistence des modes d'authentification (Priority: P1)

En tant qu'administrateur, je veux que les utilisateurs avec un compte local (créé avant l'intégration LDAP/SSO) puissent continuer à se connecter avec leur email/password, tandis que les nouveaux utilisateurs fédérés se connectent via leur institution.  
**Why this priority**: La migration ne doit pas casser les comptes existants.  
**Independent Test**: Un compte créé localement peut toujours se connecter par email/password. Un compte créé via LDAP n'a pas de `hashed_password` et ne peut pas se connecter par email/password (retour d'une erreur explicite).

### User Story 4 — Provisionnement automatique du compte (Priority: P1)

En tant que nouvel utilisateur se connectant pour la première fois via LDAP ou SSO, je veux qu'un compte soit créé automatiquement avec les attributs récupérés de l'annuaire (email, nom), sans formulaire d'inscription.  
**Why this priority**: Friction zéro à l'onboarding institutionnel.  
**Independent Test**: Un utilisateur LDAP qui n'existe pas encore en base se connecte pour la première fois → un enregistrement `User` est créé avec `hashed_password=null` et `auth_provider='ldap'` (ou `'oidc'` / `'saml'`). La connexion suivante réutilise le même enregistrement.

### Edge Cases

- Annuaire LDAP indisponible → fallback au message d'erreur clair ("Service d'authentification indisponible"), pas de crash.
- Token SSO expiré ou invalide lors du callback → retour sur la page de login avec message d'erreur.
- Conflit d'email : un utilisateur LDAP dont l'email existe déjà comme compte local → fusion des comptes ou refus configurable (paramètre `LDAP_EMAIL_CONFLICT_STRATEGY`).
- Déconnexion SSO (Single Logout) → invalider le JWT local et rediriger vers l'IdP si le protocole le supporte.
- ✅ Transport JWT SSO sécurisé : le callback redirige avec `?sso_code=<hex32>` (TTL 60s, usage unique via Redis). Le frontend échange le code contre le JWT via `GET /auth/sso/exchange`. Le JWT ne transite plus jamais dans une URL.

---

## Requirements

### Functional Requirements

- **FR-001**: Le système DOIT accepter une authentification LDAP bind (identifiant + mot de passe vérifiés contre l'annuaire LDAP configuré).
- **FR-002**: Le système DOIT supporter au moins un protocole SSO parmi : OIDC/OAuth2 (priorité), SAML 2.0, CAS.
- **FR-003**: L'authentification locale email/password DOIT rester fonctionnelle en parallèle des modes fédérés.
- **FR-004**: La colonne `hashed_password` du modèle `User` DOIT être nullable pour les utilisateurs fédérés.
- **FR-005**: Le modèle `User` DOIT inclure un champ `auth_provider` (`'local'`, `'ldap'`, `'oidc'`, `'saml'`, `'cas'`) pour identifier la source d'authentification.
- **FR-006**: Un utilisateur fédéré se connectant pour la première fois DOIT voir son compte créé automatiquement (just-in-time provisioning).
- **FR-007**: L'interface DOIT proposer un bouton "Se connecter avec mon institution" distinct du formulaire email/password.
- **FR-008**: Le JWT retourné après authentification fédérée DOIT avoir le même format et TTL que le JWT local (HS256, TTL configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`).
- **FR-009**: Les attributs récupérés de l'annuaire (email, prénom, nom) DOIVENT être synchronisés à chaque connexion (mise à jour si modifiés dans l'IdP).

### Non-Functional Requirements

- **NFR-001**: Les credentials LDAP (URL, base DN, bind DN, mot de passe de service) DOIVENT être stockés dans des variables d'environnement, jamais en dur.
- **NFR-002**: La communication avec le serveur LDAP DOIT utiliser LDAPS (port 636) ou StartTLS. LDAP non sécurisé (port 389) est interdit en production.
- **NFR-003**: Les tokens OIDC/SAML DOIVENT être validés (signature, expiry, issuer) avant d'émettre un JWT.
- **NFR-004**: Le flux SSO DOIT résister aux attaques CSRF (état `state` dans le flow OIDC, validation du `RelayState` en SAML).
- **NFR-005**: Le JWT applicatif long terme NE DOIT PAS être transmis dans une query string en production.

---

## Technical Design

### Backend — nouvelles variables d'environnement

```env
# LDAP
LDAP_ENABLED=false
LDAP_URL=ldaps://ldap.example.org:636
LDAP_BASE_DN=dc=example,dc=org
LDAP_BIND_DN=cn=service,dc=example,dc=org
LDAP_BIND_PASSWORD=secret
LDAP_USER_FILTER=(uid={username})
LDAP_EMAIL_ATTR=mail
LDAP_FIRSTNAME_ATTR=givenName
LDAP_LASTNAME_ATTR=sn
LDAP_EMAIL_CONFLICT_STRATEGY=reject  # reject | merge

# SSO OIDC (priorité)
SSO_OIDC_ENABLED=false
SSO_OIDC_ISSUER=https://sso.example.org
SSO_OIDC_CLIENT_ID=openedition-search
SSO_OIDC_CLIENT_SECRET=secret
SSO_OIDC_REDIRECT_URI=https://search.openedition.org/api/auth/sso/callback
SSO_OIDC_SCOPES=openid email profile

# SSO SAML (optionnel)
SSO_SAML_ENABLED=false
SSO_SAML_IDP_METADATA_URL=https://idp.example.org/metadata

# SSO CAS (optionnel)
SSO_CAS_ENABLED=false
SSO_CAS_SERVER_URL=https://cas.example.org
```

### Backend — nouveaux endpoints

| Méthode | Path | Description |
|---|---|---|
| `GET` | `/auth/sso/login` | Redirige vers l'IdP (génère le lien OIDC/SAML/CAS) |
| `GET` | `/auth/sso/callback` | Reçoit le token/ticket de l'IdP, crée/met à jour le User, retourne JWT |
| `POST` | `/auth/ldap/login` | Authentifie via LDAP bind, retourne JWT |

### Backend — nouveaux fichiers

```
search_api_solr/app/services/
├── ldap_service.py        # LDAP bind, recherche d'attributs, provisionnement
├── oidc_service.py        # Échange de token, validation, provisionnement
└── saml_service.py        # (optionnel) décodage assertion SAML
```

### Backend — migration du modèle User

```python
# Avant
hashed_password: str

# Après
hashed_password: Optional[str] = None
auth_provider: str = "local"  # local | ldap | oidc | saml | cas
```

### Frontend — modifications

- `AuthModal.tsx` : ajouter un bouton "Se connecter via SSO" sous le formulaire local (visible seulement si `NEXT_PUBLIC_SSO_ENABLED=true`)
- `AuthContext.tsx` : gérer la redirection SSO et la réception du JWT après callback

### Dépendances Python à ajouter

```
ldap3>=2.9          # LDAP bind
authlib>=1.3        # OIDC/OAuth2 (inclut PKCE, JWKS, validation)
python3-saml>=1.16  # SAML 2.0 (optionnel, lourd — uniquement si requis)
```

---

## Success Criteria

- [x] Un utilisateur LDAP peut se connecter avec ses identifiants institutionnels et voir ses recherches sauvegardées.
- [x] Un utilisateur SSO (OIDC) est redirigé vers l'IdP, authentifié, et revient sur l'application avec une session active.
- [x] Un utilisateur local existant peut toujours se connecter par email/password.
- [x] Un utilisateur fédéré sans compte préexistant voit son compte créé automatiquement à la première connexion.
- [x] `hashed_password=null` pour un utilisateur fédéré n'empêche pas l'accès aux fonctionnalités authentifiées.
- [x] Aucune régression attendue sur les 66 tests E2E Playwright documentés.
- [x] Les credentials LDAP et SSO ne sont jamais loggués ni exposés dans les erreurs HTTP.
- [x] Le JWT SSO n'est pas exposé dans l'URL frontend : seul `sso_code` à usage unique transite en query string.

### Tests Playwright

| Fichier | Cas couverts |
|---|---|
| `front/tests/auth-ldap-sso.spec.ts` | 12 tests : UI LDAP, erreurs, champs requis, SSO callback, échange `sso_code`, coexistence compte local/fédéré |

---

## Dépendances inter-specs

- Dépend de `002-advanced-search-suite` (modèle User, JWT, endpoints auth existants).
- Bloquant pour toute spec future nécessitant un SSO institutionnel.
- Compatible avec `004-url-sync` (le mode de connexion n'affecte pas l'URL de recherche).
