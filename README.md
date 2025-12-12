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
cd search_api_solr

# Utiliser le script de démarrage
./start.sh dev

# Ou avec Make
make dev
```

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
- **Port Dev** : 3009
- **Port Prod** : 80
- **Technologie** : React 18, SearchKit, React Router

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
SOLR_BASE_URL=http://localhost:8983/solr/openedition
API_HOST=0.0.0.0
API_PORT=8007
API_RELOAD=True
DEV=true
LOG_LEVEL=DEBUG
```

### Variables d'environnement Frontend

```env
REACT_APP_API_URL=http://localhost:8007
# Host port used to expose the frontend on the host machine (defaults to 3009)
FRONTEND_PORT=3009
PORT=3000
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

Vérifiez que `REACT_APP_API_URL` dans `front/.env` pointe vers la bonne URL.

### Solr ne répond pas

```bash
# Vérifier les logs
docker-compose logs solr

# Redémarrer Solr
docker-compose restart solr
```

### Erreur de CORS

Ajoutez l'origine du frontend dans `CORS_ORIGINS` dans le `.env` du backend.

## 📄 Licence

Projet OpenEdition.

## 👥 Auteurs

Équipe de développement OpenEdition
