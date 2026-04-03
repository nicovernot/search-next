# Technical Plan: Advanced Search Suite

## Options retenues
- **Mode avancé** : `react-querybuilder`
- **Langues** : `next-intl`
- **Base de données backend** : PostgreSQL avec SQLAlchemy (via FastAPI)

## 1. Frontend (Next.js - `front-next`)
1. **Intégration next-intl** :
   - Mise en place du `[locale]` dans l'arborescence app (si Next.js App Router) ou configuration `next-intl` classique.
   - Création des dictionnaires JSON (FR, EN, ES, DE, IT).
2. **Interface Avancée** :
   - Composant `AdvancedQueryBuilder` wrappant `react-querybuilder`.
   - Transformation de la requête logique du builder vers le format JSON / Query String supporté par le Backend Python.
3. **Autocomplétion (Facettes/Auteur)** :
   - Custom field component pour `react-querybuilder` qui intègre un appel API de debouncing depuis `/api/suggest`.
   - Ajustement de la sidebar standard pour en bénéficier également.
4. **Auth & Saved Searches** :
   - Contexte React pour l'authentification (`AuthContext`).
   - Store local ou hook pour les recherches enregistrées.

## 2. Backend (FastAPI - `search_api_solr`)
1. **Implémentation de PostgreSQL** :
   - Ajout au `docker-compose.yml` d'un service `postgres:15-alpine`.
   - Dépendances : `sqlalchemy`, `asyncpg`, `alembic` (ou `psycopg2-binary`).
   - Init alembic, et création de 2 tables : `users` et `saved_searches`.
2. **Authentification** :
   - Setup de hachage de mots de passe (`passlib[bcrypt]`).
   - JWT encoding (`PyJWT`).
   - Endpoints `/auth/login`, `/auth/register`.
3. **Endpoint `/suggest`** :
   - Lancement d'une requête spécifique aux Terms Components de Solr et `author_t` / etc.
4. **Endpoint `/search` (mise à jour)** :
   - Étendre l'API pour parser l'arbre logique envoyé par `react-querybuilder`.
   - Conversion en syntaxe Solr native (`q=(field:A AND field:B) OR (NOT field:C)`).
