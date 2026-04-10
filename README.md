# OpenEdition Search v2

Application de recherche moderne pour OpenEdition, composée d'un backend FastAPI, d'un moteur de recherche Solr et d'un frontend React avec SearchKit.

## 🏗️ Architecture

```
searchv2/
├── search_api_solr/        # Backend FastAPI + Configuration Docker
│   ├── app/                # Code de l'API
│   ├── tests/              # Tests unitaires et d'intégration
│   ├── docker-compose.yml  # Configuration Docker de base
│   ├── Dockerfile          # Image Docker de l'API
│   └── Makefile            # Commandes simplifiées
│
├── front/                  # Frontend React + SearchKit
│   ├── public/             # Fichiers statiques
│   ├── src/                # Code source React
│   ├── Dockerfile          # Image Docker du frontend
│   └── package.json        # Dépendances npm
│
└── .env.shared            # Variables d'environnement communes
└── .env.development       # Variables spécifiques développement
└── .env.production        # Variables spécifiques production
└── .env.staging           # Variables spécifiques staging
└── .env.test              # Variables spécifiques tests
└── scripts/               # Scripts d'automatisation
```

## 🚀 Premiers Pas

### Installation

```bash
# Cloner le projet
git clone https://github.com/your-repo/searchv2.git
cd searchv2

# Vérifier la configuration
./scripts/check_env_setup.sh

# Synchroniser l'environnement de développement
./scripts/sync_env.sh development
```

### Démarrage

```bash
# Démarrer tous les services
docker-compose up

# Accéder aux services
# - Frontend: http://localhost:3009
# - Backend API: http://localhost:8007
# - Documentation API: http://localhost:8007/docs
```

### Développement

```bash
# Démarrer en mode développement (hot-reload)
make dev

# Le frontend sera disponible sur http://localhost:3007
# Le backend sur http://localhost:8007
```

### Tests

```bash
# Exécuter tous les tests
./scripts/run_tests.sh

# Exécuter des tests spécifiques
cd search_api_solr
python -m pytest tests/test_search_builder.py -v
```

## 🚀 Démarrage rapide

### Avec Docker (Recommandé)

```bash
# 1. Synchroniser la configuration d'environnement
./scripts/sync_env.sh development

# 2. Démarrer les services
make dev

# Ou en une seule commande
docker-compose up
```

### Gestion Centralisée des Environnements

Le projet utilise maintenant une approche centralisée pour la gestion des environnements :

**Nouvelle Méthode (Recommandée)**

```bash
# Synchroniser l'environnement souhaité
./scripts/sync_env.sh development  # Développement
./scripts/sync_env.sh staging      # Staging
./scripts/sync_env.sh production   # Production
./scripts/sync_env.sh test         # Tests

# Puis démarrer les services
docker-compose up
```

**Avec Make**

```bash
# Développement (synchronise et démarre)
make dev

# Staging
make staging

# Production  
make prod

# Tests (avec validation)
make test

# Tests E2E (Playwright UI)
make test-front-ui
make test-front
```

**Fichiers de Configuration**

```
.env.shared      # Variables communes à tous les environnements
.env.development # Variables spécifiques au développement
.env.production  # Variables spécifiques à la production
.env.staging     # Variables spécifiques au staging
.env.test        # Variables spécifiques aux tests
```

**Avantages**
- Pas de duplication des variables communes
- Validation automatique des environnements
- Sécurité améliorée (secrets non versionnés)
- Maintenance simplifiée

### Environnements personnalisés

Vous pouvez spécifier des environnements différents pour le backend et le frontend :

```bash
# Backend en staging, frontend en développement
./scripts/configure_env.sh --env staging --frontend-env development

# Ou avec Make
make run-dev ENV=staging FRONTEND_ENV=development
```

### Commandes avancées

```bash
# Configurer sans lancer (pour inspection)
make set-dev

# Lancer avec une configuration personnalisée
make run-dev ENV=staging

# Installation complète en production
make install-prod
```

Voir [docs/ENVIRONMENTS.md](./docs/ENVIRONMENTS.md) pour plus de détails sur la gestion des environnements.

### Sans Docker

#### Backend

```bash
cd search_api_solr
pip install -r requirements.txt
cp .env.example .env
# Configurer .env avec votre instance Solr
uvicorn app.main:app --reload --port 8007
```

#### Frontend

```bash
cd front
npm install
cp .env.example .env
# Configurer .env avec l'URL de l'API
npm start
```

## 📦 Services

### Backend API (FastAPI)
- **Port** : 8007
- **Documentation** : http://localhost:8007/docs
- **Technologie** : Python 3.10, FastAPI, Pydantic

#### Endpoints principaux
- `POST /search` - Recherche avec objet SearchRequest
- `GET /search` - Recherche avec paramètres URL
- `GET /suggest` - Autocomplétion
- `GET /permissions` - Vérification des permissions d'accès

- ### Frontend (React + SearchKit)
- **Port Dev** : 3007 (hot-reload)
- **Port Prod** : 3009 (nginx)
- **Technologie** : React 18, i18next, Axios

> **Note** : Deux containers frontend sont disponibles :
> - `openedition_frontend_dev` (port 3007) : développement avec hot-reload
> - `openedition_frontend` (port 3009) : production avec nginx

#### Fonctionnalités
- Barre de recherche avec autocomplétion
- Affichage des résultats paginés
- Facettes interactives (plateforme, type, langue, année)
- Interface responsive
- Gestion des permissions

### Solr (Moteur de recherche)
- **Port** : 8983
- **Admin UI** : http://localhost:8983/solr
- **Version** : 9.4

## 🛠️ Développement

### Structure du Backend

```
search_api_solr/app/
├── main.py                 # Point d'entrée FastAPI
├── settings.py             # Configuration
├── api/
│   └── v1/
│       └── search.py       # Routes de recherche
├── core/
│   ├── config.py           # Configuration centralisée
│   └── exception_handlers.py
├── models/
│   ├── search_models.py    # Modèles Pydantic
│   └── document.py         # Modèles de documents
└── services/
    ├── search_builder.py   # Construction des requêtes Solr
    ├── facet_config.py     # Configuration des facettes
    ├── field_config.py     # Configuration des champs
    └── solr_connector.py   # Client Solr
```

### Structure du Frontend

```
front/src/
├── components/             # Composants React réutilisables
│   ├── SearchBar.jsx       # Barre de recherche
│   ├── ResultsList.jsx     # Liste des résultats
│   ├── ResultItem.jsx      # Affichage d'un résultat
│   ├── Facets.jsx          # Conteneur de facettes
│   ├── FacetGroup.jsx      # Groupe de facettes
│   └── Pagination.jsx      # Pagination
├── pages/
│   └── Home.jsx            # Page principale
├── services/
│   └── api.js              # Client API
└── utils/
    └── searchkit.js        # Configuration SearchKit
```

## 🧪 Tests

### Avec la Nouvelle Configuration

```bash
# Synchroniser l'environnement de test
./scripts/sync_env.sh test

# Exécuter tous les tests (backend + frontend)
./scripts/run_tests.sh

# Ou exécuter des tests spécifiques
cd search_api_solr && python -m pytest tests/test_search_builder.py -v
```

### Backend

```bash
cd search_api_solr

# Avec Docker
make test

# Sans Docker
pytest
pytest --cov=app --cov-report=html
```

### Frontend

```bash
cd front
npm test
npm test -- --coverage
```

## 🐳 Docker

### Commandes Docker principales

```bash
# Développement (avec hot reload)
./start.sh dev
make dev

# Production
./start.sh prod
make prod

# Tests
./start.sh test
make test

# Voir les logs
make logs
make logs-api
make logs-frontend

# Nettoyer
./start.sh clean
make clean
```

Voir [DOCKER.md](search_api_solr/DOCKER.md) pour plus de détails.

## 🔧 Configuration Centralisée

Le projet utilise maintenant une gestion centralisée des environnements avec validation automatique.

### Structure des Fichiers

```
.env.shared          # Variables communes à tous les environnements
.env.development     # Variables spécifiques au développement
.env.production      # Variables spécifiques à la production
.env.staging         # Variables spécifiques au staging
.env.test            # Variables spécifiques aux tests
.env.example         # Template avec toutes les variables
```

### Variables Principales

**Backend (FastAPI)** :
- `SOLR_URL` : URL du serveur Solr
- `SOLR_COLLECTION` : Collection Solr à utiliser
- `API_BASE_URL` : URL base de l'API
- `DEBUG` : Mode debug
- `JWT_SECRET` : Secret pour les tokens JWT (production)

**Frontend (React)** :
- `REACT_APP_API_URL` : URL de l'API backend
- `REACT_APP_DEBUG` : Mode debug
- `REACT_APP_MOCK_API` : Utilisation de l'API mock

**Communes** :
- `NODE_ENV` : Environnement (development, production, test)
- `LOG_LEVEL` : Niveau de logging
- `CORS_ALLOWED_ORIGINS` : Origines autorisées pour CORS

### Validation Automatique

Le backend et le frontend valident leurs environnements au démarrage :

**Backend** : `search_api_solr/app/core/env_validation.py`
- Validation des URLs Solr
- Validation des secrets
- Validation des niveaux de log

**Frontend** : `front/src/utils/envValidation.js`
- Validation des URLs API
- Validation des booléens
- Avertissements pour les configurations non optimales

### Exemple de Configuration

**`.env.development`** :
```env
# Développement frontend
REACT_APP_API_URL=http://localhost:8000
REACT_APP_DEBUG=true
REACT_APP_MOCK_API=false

# Développement backend
DEBUG=true
AUTO_RELOAD=true

# Configuration Solr pour dev
SOLR_URL=http://localhost:8983/solr
SOLR_COLLECTION=searchv2_dev
```

**`.env.production`** :
```env
# Production frontend
REACT_APP_API_URL=https://api.searchv2.com
REACT_APP_DEBUG=false

# Production backend
DEBUG=false
AUTO_RELOAD=false

# Sécurité
JWT_SECRET=votre_secret_jwt_secure
SESSION_SECRET=votre_secret_session_secure
```

Voir [ENVIRONMENTS.md](./ENVIRONMENTS.md) pour la documentation complète.

## 📝 API Documentation

L'API est documentée avec OpenAPI/Swagger :
- **Swagger UI** : http://localhost:8007/docs
- **ReDoc** : http://localhost:8007/redoc
- **OpenAPI JSON** : http://localhost:8007/openapi.json

## 🌐 Déploiement

### Production avec Docker

```bash
cd search_api_solr
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### Production avec Nginx

Un reverse proxy Nginx est inclus pour la production. Configuration dans `search_api_solr/nginx/`.

## 🔒 Sécurité

- Validation des entrées avec Pydantic
- Rate limiting configuré dans Nginx
- Sanitization des requêtes Solr
- Headers de sécurité configurés
- CORS configuré pour les origines autorisées

## 🌐 Gestion des Environnements

Le projet utilise une approche centralisée pour la gestion des environnements avec validation automatique.

### Scripts Disponibles

```bash
# Vérifier la configuration
./scripts/check_env_setup.sh

# Synchroniser un environnement
./scripts/sync_env.sh development  # dev
./scripts/sync_env.sh staging      # staging
./scripts/sync_env.sh production   # prod
./scripts/sync_env.sh test         # tests

# Exécuter les tests avec la bonne configuration
./scripts/run_tests.sh
```

### Validation des Environnements

**Backend** : Validation Pydantic au démarrage
- Vérifie les URLs Solr
- Valide les secrets et configurations
- Affiche des erreurs claires en cas de problème

**Frontend** : Validation JavaScript au démarrage
- Vérifie les URLs API
- Valide les configurations
- Affiche un message utilisateur en cas d'erreur

### Bonnes Pratiques

1. **Ne jamais éditer** les fichiers `.env.local` générés
2. **Toujours utiliser** `.env.example` comme template
3. **Valider** avant de démarrer les services
4. **Documenter** les nouvelles variables dans `.env.example`

## 📊 Monitoring

### Health Checks

```bash
# Vérifier tous les services
make health

# Ou manuellement
curl http://localhost:8007/docs
curl http://localhost:3009
curl http://localhost:8983/solr/openedition/admin/ping
```

### Statistiques

```bash
make stats
docker stats
```

## 🤝 Contribution

1. Créer une branche : `git checkout -b feature/ma-fonctionnalite`
2. Commiter les changements : `git commit -am 'Ajout de ma fonctionnalité'`
3. Pousser vers la branche : `git push origin feature/ma-fonctionnalite`
4. Créer une Pull Request

## 📚 Documentation complémentaire

- [Documentation Backend](search_api_solr/README.md)
- [Documentation Frontend](front/README.md)
- [Guide Docker](search_api_solr/DOCKER.md)
- [Guide de tests](search_api_solr/TESTING.md)
- [Gestion des Environnements](./docs/ENVIRONMENTS.md) - **Nouveau!**
- [Résumé de la Configuration](./docs/ENVIRONMENT_MANAGEMENT_SUMMARY.md)

## 🐛 Résolution de problèmes

### Le frontend ne peut pas contacter l'API

Vérifiez que `REACT_APP_API_URL` dans `front/.env` pointe vers la bonne URL (par défaut `http://localhost:8007`).

### Erreur de CORS

**Symptôme** : `Access to fetch at 'http://localhost:8007/search' from origin 'http://0.0.0.0:3009' has been blocked by CORS policy` ou `CORS Missing Allow Origin`

**Causes possibles** :
1. L'origine du frontend n'est pas dans la liste `CORS_ORIGINS`
2. Le header `Accept-Language` n'est pas autorisé dans `CORS_ALLOW_HEADERS`

**Solution** : Ajoutez toutes les origines et headers nécessaires dans le fichier `.env` du backend :

```bash
# Développement - inclure TOUTES les variantes d'origine possibles
CORS_ORIGINS=http://localhost:3009,http://localhost:3000,http://127.0.0.1:3009,http://127.0.0.1:3000,http://127.0.0.1:3007,http://0.0.0.0:3007,http://0.0.0.0:3009,http://localhost:3007
CORS_ALLOW_HEADERS=Accept,Accept-Language,Authorization,Content-Language,Content-Type,X-Requested-With,X-CSRF-Token

# Production
CORS_ORIGINS=https://search.openedition.org,https://www.openedition.org
```

Puis recréez le conteneur API pour charger les nouvelles variables :
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d api --force-recreate
```

**Note Firefox** : Firefox peut mettre en cache les réponses CORS. Videz le cache (Ctrl+Shift+Suppr) ou testez en navigation privée.

### Container frontend "unhealthy"

**Cause** : Le health check utilise `localhost` qui peut se résoudre en IPv6, mais nginx écoute sur IPv4.

**Solution** : Les Dockerfiles ont été mis à jour pour utiliser `127.0.0.1` au lieu de `localhost` dans les health checks.

### Erreur pydantic-settings avec types_needing_parents

**Symptôme** : `SettingsError: error parsing value for field "types_needing_parents"`

**Cause** : Pydantic-settings essaie de parser les valeurs comme du JSON.

**Solution** : Utilisez le format CSV (pas JSON) dans le fichier `.env` :
```bash
# ✅ Correct
types_needing_parents=article,chapter

# ❌ Incorrect
types_needing_parents=["article", "chapter"]
```

### Conflit de ports

**Symptôme** : `Bind for 0.0.0.0:3009 failed: port is already allocated`

**Cause** : Deux containers essaient d'utiliser le même port.

**Solution** : Les ports ont été séparés :
- Frontend dev : port 3007
- Frontend prod : port 3009

### Solr ne répond pas

```bash
# Vérifier les logs
docker-compose logs api

# Redémarrer l'API
docker-compose restart api

# Vérifier la santé de Solr distant
curl https://solrslave-sec.labocleo.org/solr/documents/admin/ping
```

## 📄 Licence

Projet OpenEdition.

## 👥 Auteurs

Équipe de développement OpenEdition
