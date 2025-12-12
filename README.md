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
└── front/                  # Frontend React + SearchKit
    ├── public/             # Fichiers statiques
    ├── src/                # Code source React
    ├── Dockerfile          # Image Docker du frontend
    └── package.json        # Dépendances npm
```

## 🚀 Démarrage rapide

### Avec Docker (Recommandé)

```bash
# Utiliser le script de configuration d'environnement
./configure_env.sh --env development

# Ou avec Make (automatique)
make dev
```

### Sélection de l'environnement

Le projet supporte plusieurs environnements avec des configurations spécifiques :

**Méthode 1 : Utiliser le script de configuration**

```bash
# Développement local avec hot-reload
./configure_env.sh --env development

# Environnement de test/pré-production
./configure_env.sh --env staging

# Environnement de production sécurisé
./configure_env.sh --env production

# Configuration optimisée pour les tests
./configure_env.sh --env test
```

**Méthode 2 : Utiliser Make (recommandé)**

```bash
# Développement (configure automatiquement l'environnement)
make dev

# Staging
make staging

# Production
make prod

# Tests
make test
```

**Méthode 3 : Configuration manuelle**

```bash
# Développement
cp search_api_solr/.env.development search_api_solr/.env
cp front/.env.development front/.env

# Production
cp search_api_solr/.env.production search_api_solr/.env
cp front/.env.production front/.env
```

### Environnements personnalisés

Vous pouvez spécifier des environnements différents pour le backend et le frontend :

```bash
# Backend en staging, frontend en développement
./configure_env.sh --env staging --frontend-env development

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

Voir [ENVIRONMENTS.md](search_api_solr/ENVIRONMENTS.md) pour plus de détails sur la gestion des environnements.

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

## 🔧 Configuration

### Variables d'environnement Backend

```env
# Configuration Solr
SOLR_BASE_URL=https://solrslave-sec.labocleo.org/solr/documents

# Configuration API
API_HOST=0.0.0.0
API_PORT=8007
API_RELOAD=true

# Configuration CORS (développement)
CORS_ORIGINS=http://localhost:3009,http://localhost:3000,http://localhost:3007,http://127.0.0.1:3009,http://127.0.0.1:3000,http://127.0.0.1:3007,http://0.0.0.0:3009,http://0.0.0.0:3007

# Dev mode
DEV=true
LOG_LEVEL=DEBUG

# Types de documents (format CSV)
types_needing_parents=article,chapter
default_fields=id,url,title,idparent,container_url
```

> **Important** : Les champs de type liste (comme `types_needing_parents`, `CORS_ORIGINS`) doivent être au format CSV (valeurs séparées par des virgules) et non JSON.

### Variables d'environnement Frontend

```env
REACT_APP_API_URL=http://localhost:8007

# Ports Docker
FRONTEND_PORT=3009          # Port production (nginx)
FRONTEND_DEV_PORT=3007      # Port développement (hot-reload)
```

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

## 🐛 Résolution de problèmes

### Le frontend ne peut pas contacter l'API

Vérifiez que `REACT_APP_API_URL` dans `front/.env` pointe vers la bonne URL (par défaut `http://localhost:8007`).

### Erreur de CORS

**Symptôme** : `Access to fetch at 'http://localhost:8007/search' from origin 'http://0.0.0.0:3009' has been blocked by CORS policy`

**Solution** : Ajoutez toutes les origines nécessaires dans `CORS_ORIGINS` dans le fichier `.env` du backend :

```bash
# Développement
CORS_ORIGINS=http://localhost:3009,http://localhost:3007,http://127.0.0.1:3009,http://127.0.0.1:3007,http://0.0.0.0:3009,http://0.0.0.0:3007

# Production
CORS_ORIGINS=https://search.openedition.org,https://www.openedition.org
```

Puis redémarrez l'API : `docker-compose restart api`

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
