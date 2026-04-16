# Feature Specification: Advanced Search Suite

**Feature Branch**: `feature/002-advanced-search-suite`  
**Created**: 2026-04-03  
**Updated**: 2026-04-13  
**Status**: Complete — toutes les phases livrées + correctifs post-livraison intégrés  

## User Scenarios & Testing (Playwright) *(mandatory)*

*Note: All End-to-End tests must be implemented using **Playwright** framework.*

### User Story 1 - Recherche Avancée et Éditeur Logique (Priority: P1)
En tant qu'utilisateur, je veux pouvoir basculer vers un mode de recherche avancé, et utiliser un constructeur de requête logique (blocs AND, OR, NOT), afin de formuler des recherches complexes précises.
**Why this priority**: C'est le coeur du besoin de requêtage précis.
**Independent Test**: L'utilisateur peut ouvrir la recherche avancée, composer plusieurs groupes/règles, ajouter des filtres lexicaux (y compris par auteur) et lancer la requête avec un payload correct.

### User Story 2 - Facettes Auteurs & Autocomplétion (Priority: P1)
En tant qu'utilisateur, je veux pouvoir filtrer les résultats par "Auteur" (à la fois en recherche simple et avancée), et bénéficier d'une autocomplétion dynamique sur les champs textuels de recherche afin de trouver rapidement les bonnes valeurs sans fautes de frappe.
**Why this priority**: L'auteur est une demande métier forte et l'autocomplétion évite le zero-result. 
**Independent Test**: La saisie dans la barre de recherche simple et dans les champs de valeur du query builder propose des suggestions pertinentes au fur et à mesure de la frappe.

### User Story 3 - Compte Utilisateur et Sauvegarde de Recherches (Priority: P2)
En tant qu'utilisateur, je veux pouvoir me créer un compte avec email/mot de passe, me connecter, et sauvegarder mes recherches pour les rejouer plus tard sans avoir à re-construire mon arbre logique.
**Why this priority**: Indispensable pour fidéliser l'utilisateur, mais nécessite une infrastructure SQL. Les autres features peuvent exister sans.
**Independent Test**: Création d'un compte, connexion JWT réussie, bouton "Sauvegarder", et menu affichant l'historique des requêtes enregistrées.

### User Story 4 - Traductions I18n (Priority: P2)
En tant qu'utilisateur international, je veux que l'interface soit traduite dans les principales langues européennes supportées par le projet (FR, EN, ES, DE, IT, PT) afin de naviguer avec précision.
**Why this priority**: Permet à OpenEdition Search d'étendre son aura.
**Independent Test**: Un sélecteur de langue permet de changer dynamiquement la langue de l'interface complète (y compris les libellés de l'éditeur logique `react-querybuilder`).

### Edge Cases
- Que se passe-t-il si un utilisateur tente de sauvegarder une requête vide ?
- Comment gère-t-on une recherche logique invalide (ex: un bloc `AND` sans termes) ? L'UI doit le bloquer.
- Que faire si le token d'authentification expire pendant l'édition d'une requête complexe ?

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: Le système DOIT fournir un mode bascule pour la recherche avancée.
- **FR-002**: Le système DOIT inclure la facette "Auteur" partout où des filtres existent.
- **FR-003**: Le système DOIT intégrer un compositeur visuel pour créer une requête AND, OR, NOT.
- **FR-004**: Les champs textuels de recherche DOIVENT bénéficier de l'autocomplétion (endpoint unifié).
- **FR-005**: Le système BACKEND DOIT supporter une base PostgreSQL pour les utilisateurs et l'authentification.
- **FR-006**: Le système DOIT permettre de sauvegarder un payload JSON de requête lié au profil de l'utilisateur.
- **FR-007**: L'interface Next.js DOIT intégrer `next-intl` avec FR, EN, ES, DE, IT, PT.

### Key Entities
- **User**: Utilisateur du système (PostgreSQL).
- **SavedSearch**: Lien entre un User et un objet JSON (la configuration QueryBuilder).
- **Author**: Concept de métadonnée indexée sur Solr.

## Success Criteria *(mandatory)*

### Measurable Outcomes
- **SC-001**: L'interface de recherche avancée permet la soumission d'au moins 3 niveaux d'embranchements `AND/OR`.
- **SC-002**: L'autocomplétion répond à la frappe de l'utilisateur en moins de 300ms.
- **SC-003**: Le pipeline de traduction ne laisse aucune clé non traduite sur le build principal Next.js (6 langues : FR, EN, ES, IT, PT, DE).
- **SC-004**: Le header expose deux points d'entrée visuellement distincts — "Connexion" (secondaire) et "S'inscrire" (bouton highlight) — accessibles sans scroll.
- **SC-005**: La suite Playwright couvre : inscription, connexion réussie, connexion échouée (mauvais mdp, email inexistant, mots de passe non concordants), déconnexion, persistance de session, sauvegarde/chargement/suppression de recherche.

### Edge Cases couverts par les tests
- Inscription avec email déjà utilisé → message d'erreur visible, modal reste ouverte.
- Mots de passe non concordants → validation côté client avant appel API.
- Token JWT expiré → l'API retourne 401, les boutons auth reviennent (le `localStorage` est nettoyé par `logout()`). Token durée de vie configurée à 1440 min (24h) via `ACCESS_TOKEN_EXPIRE_MINUTES`.
- Sauvegarde de recherche vide → bouton "Sauvegarder" absent si aucune requête active.
- Nom de sauvegarde vide → bouton confirmation désactivé.
- Chargement d'une recherche sauvegardée → restitue le terme ET déclenche la recherche (résultats visibles) via `loadSearch()` atomique.
- Rechargement de page → session JWT persistée via `localStorage`, recherches sauvegardées rechargées depuis l'API.

### Correctifs post-livraison intégrés (2026-04-13)

| Problème | Solution |
|---|---|
| CORS 8003/3003 manquant | Ajout des origines dans `.env` et `.env.development` |
| Pagination/filtres sans refresh | `useEffect` dans `SearchContext` sur `filters` / `pagination.from` |
| Stale closure dans `executeSearch` | Pattern `latestRef` (useRef synchronisé après chaque render) |
| Chargement de recherche sans exécution | `loadSearch()` patche `latestRef` avant d'appeler `executeSearch()` |
| Couleurs Tailwind v4 cassées | Bloc `@theme inline` dans `globals.css` mappant les variables CSS |
| Token JWT expirant après 30 min | `ACCESS_TOKEN_EXPIRE_MINUTES=1440` dans les `.env` |
| Clés i18n hardcodées | 75 clés × 6 langues synchronisées (facettes, permissions, QB, hero, hints) |
| data-testid manquants pour les tests | Ajout sur `results-list`, `result-item`, `btn-load-search-*`, `btn-delete-search-*` |

### Tests Playwright
| Fichier | Cas couverts |
|---|---|
| `tests/auth.spec.ts` | **15 tests** — header buttons (1), modal tabs / fermeture / bascule (6), inscription ok/mdp≠/email dupliqué (3), connexion ok/mauvais mdp/email inexistant (3), déconnexion + persistance session (2) |
| `tests/saved-searches.spec.ts` | **12 tests** — panneau visible/ouverture/fermeture/vide (3), sauvegarder ok/via Enter/bouton désactivé si nom vide/absent si pas de recherche active (4+1), charger + résultats visibles / charger après reload (2), supprimer (1), persistance après reload (1) |
| `tests/search.spec.ts` | **2 tests** — chargement page, recherche simple |

**Total : 29 tests E2E verts** (suite au 2026-04-13)
