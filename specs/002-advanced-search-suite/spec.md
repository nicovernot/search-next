# Feature Specification: Advanced Search Suite

**Feature Branch**: `feature/002-advanced-search-suite`  
**Created**: 2026-04-03  
**Updated**: 2026-04-11  
**Status**: Complete — toutes les phases livrées  

## User Scenarios & Testing (Playwright) *(mandatory)*

*Note: All End-to-End tests must be implemented using **Playwright** framework.*

### User Story 1 - Recherche Avancée et Éditeur Logique (Priority: P1)
En tant qu'utilisateur, je veux pouvoir basculer vers un mode de recherche avancé, et utiliser un constructeur de requête logique (drag and drop de blocs AND, OR, NOT), afin de formuler des recherches complexes précises.
**Why this priority**: C'est le coeur du besoin de requêtage précis.
**Independent Test**: L'utilisateur peut ouvrir la recherche avancée, glisser/déposer des opérateurs logiques, ajouter des filtres lexicaux (y compris par auteur) et lancer la requête avec un payload correct généré par `react-querybuilder`.

### User Story 2 - Facettes Auteurs & Autocomplétion Globale (Priority: P1)
En tant qu'utilisateur, je veux pouvoir filtrer les résultats par "Auteur" (à la fois en recherche simple et avancée), et bénéficier d'une autocomplétion dynamique pour TOUS les filtres pour trouver rapidement les bonnes valeurs sans fautes de frappe.
**Why this priority**: L'auteur est une demande métier forte et l'autocomplétion évite le zero-result. 
**Independent Test**: La saisie dans un champ de filtre (ex: Auteur) propose des suggestions pertinentes au fur et à mesure de la frappe.

### User Story 3 - Compté Utilisateur et Sauvegarde de Recherches (Priority: P2)
En tant qu'utilisateur, je veux pouvoir me créer un compte avec email/mot de passe, me connecter, et sauvegarder mes recherches pour les rejouer plus tard sans avoir à re-construire mon arbre logique.
**Why this priority**: Indispensable pour fidéliser l'utilisateur, mais nécessite une infrastructure SQL. Les autres features peuvent exister sans.
**Independent Test**: Création d'un compte, connexion JWT réussie, bouton "Sauvegarder", et menu affichant l'historique des requêtes enregistrées.

### User Story 4 - Traductions I18n (Priority: P2)
En tant qu'utilisateur international, je veux que l'interface soit traduite dans les principales langues européennes (FR, EN, ES, DE, IT) afin de naviguer avec précision.
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
- **FR-003**: Le système DOIT intégrer un compositeur visuel `react-querybuilder` pour créer une requête AND, OR, NOT.
- **FR-004**: Chaque champ texte ou filtre supporté DOIT bénéficier de l'autocomplétion (endpoint unifié).
- **FR-005**: Le système BACKEND DOIT supporter un DB PostgreSQL pour les utilisateurs et l'authentification (basée JWT via FastAPI).
- **FR-006**: Le système DOIT permettre de sauvegarder un payload JSON de requête lié au profil de l'utilisateur.
- **FR-007**: L'interface Next.js DOIT intégrer `next-intl` avec FR, EN, ES, DE, IT.

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
- Token JWT expiré → l'API retourne 401, les boutons auth reviennent (le `localStorage` est nettoyé par `logout()`).
- Sauvegarde de recherche vide → bouton "Sauvegarder" absent si aucune requête active.
- Nom de sauvegarde vide → bouton confirmation désactivé.

### Tests Playwright
| Fichier | Cas couverts |
|---|---|
| `tests/auth.spec.ts` | 10 tests — header buttons, modal tabs, inscription, connexion, déconnexion, persistance session |
| `tests/saved-searches.spec.ts` | 8 tests — panneau, sauvegarder, charger, supprimer, persistance après reload |
| `tests/search.spec.ts` | 2 tests — chargement page, recherche simple |
