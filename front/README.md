# OpenEdition Search - Frontend

Frontend React pour l'application de recherche OpenEdition, utilisant SearchKit pour l'interface de recherche.

## 🚀 Démarrage rapide

### Prérequis

- Node.js 18+ et npm
- Backend FastAPI en cours d'exécution (par défaut sur http://localhost:8000)

### Installation

```bash
# Installer les dépendances
npm install

# Copier le fichier d'environnement
cp .env.example .env

# Configurer l'URL de l'API dans .env
# REACT_APP_API_URL=http://localhost:8000
```

### Développement

```bash
# Lancer l'application en mode développement
npm start
```

L'application sera accessible sur http://localhost:3000

### Build de production

```bash
# Créer un build optimisé
npm run build
```

Les fichiers de production seront générés dans le dossier `build/`.

## 🐳 Docker

### Build de l'image Docker

```bash
docker build -t openedition-search-frontend \
  --build-arg REACT_APP_API_URL=http://localhost:8000 \
  .
```

### Exécution du conteneur

```bash
docker run -p 80:80 openedition-search-frontend
```

L'application sera accessible sur http://localhost

### Docker Compose (avec le backend)

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./front
      args:
        REACT_APP_API_URL: http://localhost:8000
    ports:
      - "3000:80"
    depends_on:
      - backend
      
  backend:
    build: ./search_api_solr
    ports:
      - "8000:8000"
```

## 📁 Structure du projet

```
front/
├── public/                 # Fichiers publics statiques
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── components/         # Composants React réutilisables
│   │   ├── SearchBar.jsx   # Barre de recherche
│   │   ├── ResultsList.jsx # Liste des résultats
│   │   ├── ResultItem.jsx  # Item de résultat individuel
│   │   ├── Facets.jsx      # Container des facettes
│   │   ├── FacetGroup.jsx  # Groupe de facettes
│   │   └── Pagination.jsx  # Pagination des résultats
│   ├── pages/              # Pages principales
│   │   └── Home.jsx        # Page d'accueil avec recherche
│   ├── services/           # Services d'interaction avec l'API
│   │   └── api.js          # Client API FastAPI
│   ├── utils/              # Utilitaires
│   │   └── searchkit.js    # Configuration SearchKit
│   ├── App.jsx             # Composant principal
│   ├── App.css             # Styles globaux
│   ├── index.jsx           # Point d'entrée React
│   └── index.css           # Styles de base
├── Dockerfile              # Configuration Docker
├── nginx.conf              # Configuration Nginx pour la production
├── package.json            # Dépendances et scripts
└── README.md
```

## 🔧 Configuration

### Variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_SEARCHKIT_API_KEY=
PORT=3000
```

### Configuration de l'API

Le fichier `src/services/api.js` contient les fonctions pour communiquer avec le backend :

- `search(searchRequest)` - Recherche POST avec objet SearchRequest
- `searchGet(params)` - Recherche GET avec paramètres URL
- `suggest(query)` - Autocomplétion
- `getPermissions(urls, ip)` - Vérification des permissions

### Configuration SearchKit

Le fichier `src/utils/searchkit.js` configure SearchKit pour votre application :

- Configuration de la connexion à l'API
- Définition des champs de recherche
- Configuration des facettes
- Transformateurs de données

## 🎨 Personnalisation

### Styles

Les composants utilisent des fichiers CSS modules séparés. Vous pouvez personnaliser :

- `src/index.css` - Styles globaux
- `src/App.css` - Layout principal
- `src/components/*.css` - Styles des composants individuels

### Facettes

Pour ajouter ou modifier des facettes, éditez `src/components/Facets.jsx` :

```javascript
const facetConfigs = [
  { key: 'platform', label: 'Plateforme', field: 'platform' },
  { key: 'type', label: 'Type de document', field: 'type' },
  // Ajoutez vos facettes ici
];
```

### Champs de résultats

Pour modifier l'affichage des résultats, éditez `src/components/ResultItem.jsx`.

## 🧪 Tests

```bash
# Lancer les tests
npm test

# Lancer les tests avec couverture
npm test -- --coverage
```

## 📦 Scripts disponibles

- `npm start` - Lance le serveur de développement
- `npm build` - Crée un build de production
- `npm test` - Lance les tests
- `npm run lint` - Vérifie le code avec ESLint
- `npm run format` - Formate le code avec Prettier

## 🔗 Intégration avec le backend

Le frontend communique avec l'API FastAPI via les endpoints suivants :

- `POST /search` - Recherche principale
- `GET /search` - Recherche avec paramètres URL
- `GET /suggest` - Autocomplétion
- `GET /permissions` - Vérification des permissions

## 🌐 Déploiement

### Nginx (Production)

Le fichier `nginx.conf` est configuré pour :
- Servir les fichiers statiques avec cache
- Gérer le routing SPA
- Proxifier les requêtes API (optionnel)
- Headers de sécurité

### Variables d'environnement de build

Pour configurer l'URL de l'API au moment du build :

```bash
REACT_APP_API_URL=https://api.example.com npm run build
```

## 📝 Licence

Ce projet fait partie de l'écosystème OpenEdition.

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez suivre les conventions de code existantes.
