# Implementation Tasks: Advanced Search Suite

## Phase 1: Infrastructure Backend & Base de données
- [x] Ajouter `postgres` dans le docker-compose.
- [x] Installer les dépendances dans `search_api_solr` (SQLAlchemy, psycopg, PyJWT, passlib, bcrypt).
- [x] Modèles : `User` et `SavedSearch`. Migrations avec Alembic.
- [x] Endpoints `/auth/register` et `/auth/login`.

## Phase 2: Autocomplétion
- [x] Endpoint `/suggest` côté backend (FastAPI -> Solr).
- [x] Composant React `AutocompleteInput` avec debounce et gestion du clavier.
- [x] Intégration dans la barre de recherche principale.

## Phase 3: Construction Avancée de Requête
- [x] Backend : parser récursif `query_logic_parser.py` qui convertit la structure JSON de la requête logique en chaîne Solr valide (AND/OR/NOT récursif, opérateurs contains/begins_with/ends_with).
- [x] Frontend : Installation de `react-querybuilder` (v8.14.4).
- [x] Frontend : Composant `AdvancedQueryBuilder.tsx` avec toggle simple/avancé et champs configurés.

## Phase 4: Traductions
- [x] Migration vers `next-intl` v4 avec routing `[locale]` (URLs `/fr/`, `/en/`, etc.).
- [x] Fichiers messages ICU dans `/messages/{fr,en,es,it,pt,de}.json` — 6 langues complètes.
- [x] Suppression de `I18nContext` custom et du hook `useTranslations` maison.
- [x] `LanguageSelector` utilise `useLocale()` + `useRouter()` de `next-intl/navigation`.
- [x] Tous les composants migrent vers `useTranslations()` de `next-intl`.
- [x] Middleware `middleware.ts` + `i18n/routing.ts` + `i18n/request.ts` + `i18n/navigation.ts`.

## Phase 5: Recherches Sauvegardées
- [x] Backend : `app/api/v1/saved_searches.py` — GET/POST/DELETE `/saved-searches` avec auth JWT.
- [x] Backend : `app/core/dependencies.py` — `get_current_user` (décodage JWT Bearer).
- [x] Backend : router enregistré dans `main.py`.
- [x] Frontend : `AuthContext.tsx` — login/register/logout avec `localStorage`.
- [x] Frontend : `AuthModal.tsx` — deux boutons header distincts (Connexion/S'inscrire), modal avec onglets, show/hide password, lien switch mode, data-testid.
- [x] Frontend : `SavedSearchesPanel.tsx` — dropdown Mes Recherches + bouton Sauvegarder + data-testid.
- [x] Frontend : intégration dans le header (`[locale]/page.tsx`).

## Tests E2E (Playwright)
- [x] `tests/auth.spec.ts` — 10 tests : inscription, connexion, déconnexion, erreurs, persistance session.
- [x] `tests/saved-searches.spec.ts` — 8 tests : sauvegarder, charger, supprimer, persistance après reload.
