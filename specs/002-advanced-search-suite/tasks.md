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
- [ ] Backend : parser récursif qui convertit la structure JSON de la requête logique en une chaîne de filtrage Solr valide.
- [ ] Frontend : Installation de `react-querybuilder`.
- [ ] Frontend : Créer le composant de vue avancée et injecter nos custom inputs (ex: Autocomplétion) dedans.

## Phase 4: Traductions
- [ ] Setup global de `next-intl`.
- [ ] Extraire les textes existants dans des fichiers JSON (au minimum en).
- [ ] Fournir les traductions EN, ES, DE, IT.
- [ ] Câbler le `LocaleSwitcher`.

## Phase 5: Recherches Sauvegardées
- [ ] Backend : Endpoint CRUD pour`/api/saved-searches`.
- [ ] Frontend : Lier l'interface à ces routes (Bouton "Sauvegarder", Panel "Mes Recherches").
