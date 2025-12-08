# Configuration Docker - Utilisation de Solr distant

## ✅ Changements appliqués

### Solr distant utilisé
- **URL** : https://solrslave-sec.labocleo.org/solr/documents
- **Pas besoin d'image Solr locale** : configuration simplifiée

### Architecture mise à jour

```
┌─────────────┐
│  Frontend   │  Port 3000 (dev) / 80 (prod)
│   React     │  
└──────┬──────┘
       │
       ▼
┌─────────────┐
│     API     │  Port 8007
│   FastAPI   │
└──────┬──────┘
       │
       │ HTTPS
       ▼
┌─────────────────────────────────┐
│  Solr Distant (labocleo.org)   │
│  https://solrslave-sec.lab...   │
└─────────────────────────────────┘
```

## 📦 Services Docker

### 1. API Backend (Port 8007)
- FastAPI
- Se connecte à Solr distant
- Hot reload en mode dev

### 2. Frontend (Port 3000/80)
- React + SearchKit
- Interface de recherche

**Note** : Pas de conteneur Solr local, utilisation du serveur distant.

## 🚀 Démarrage

```bash
cd search_api_solr

# Démarrage rapide
./start.sh dev

# Ou avec Make
make dev

# Ou Docker Compose
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## 🌐 URLs

### En développement :
- **Frontend** : http://localhost:3000
- **API** : http://localhost:8007
- **API Docs** : http://localhost:8007/docs
- **Solr** : https://solrslave-sec.labocleo.org/solr/documents (distant)

## ⚙️ Configuration

### `.env` (Backend)
```env
# Solr distant
SOLR_BASE_URL=https://solrslave-sec.labocleo.org/solr/documents

# API
API_HOST=0.0.0.0
API_PORT=8007
API_RELOAD=True
DEV=true
LOG_LEVEL=DEBUG
```

### `front/.env` (Frontend)
```env
REACT_APP_API_URL=http://localhost:8007
```

## 🔧 Commandes

```bash
# Développement
make dev              # Démarrer (sans Solr local)
make logs             # Voir les logs
make logs-api         # Logs API uniquement
make logs-frontend    # Logs frontend uniquement

# Tests
make test             # Lancer les tests

# Santé
make health           # Vérifier API, Frontend et Solr distant

# Nettoyage
make down             # Arrêter
make clean            # Nettoyer
```

## 📋 Vérification

```bash
# Vérifier la configuration
./check-config.sh

# Vérifier l'accès à Solr distant
curl https://solrslave-sec.labocleo.org/solr/documents/admin/ping
```

## ⚠️ Note importante

Si vous n'avez pas accès à Solr distant (erreur de connexion) :
1. Vérifiez que vous êtes sur le réseau approprié (VPN si nécessaire)
2. Vérifiez que l'URL est correcte
3. Testez manuellement : `curl https://solrslave-sec.labocleo.org/solr/documents/admin/ping`

## 🎯 Avantages de cette configuration

✅ **Plus simple** : Pas besoin de gérer Solr localement  
✅ **Plus léger** : Moins de conteneurs Docker  
✅ **Données réelles** : Utilise les vraies données de production  
✅ **Démarrage rapide** : Moins de services à lancer  

## 🔄 Fichiers mis à jour

- `docker-compose.yml` - Suppression du service Solr
- `docker-compose.dev.yml` - URL Solr distante
- `docker-compose.prod.yml` - URL Solr distante
- `.env` - SOLR_BASE_URL mis à jour
- `.env.example` - SOLR_BASE_URL mis à jour
- `Makefile` - Suppression commandes Solr locales
- `check-config.sh` - Vérification Solr distant

## 🚦 Démarrage maintenant

```bash
cd search_api_solr
./start.sh dev
```

Puis ouvrez http://localhost:3000 dans votre navigateur !
