# OpenEdition Search - Guide Docker

Ce guide explique comment utiliser Docker pour déployer l'application de recherche OpenEdition.

## 🏗️ Architecture

L'infrastructure Docker comprend 3 services principaux :

- **Solr** : Moteur de recherche (port 8983)
- **API** : Backend FastAPI (port 8007)
- **Frontend** : Interface React (port 3009 en dev (host) / 3000 en conteneur, 80 en prod)

## 🚀 Démarrage rapide

### Avec Make (recommandé)

```bash
# Installation complète
make install

# Développement
make dev

# Production
make prod
```

### Sans Make

```bash
# Développement
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📋 Commandes disponibles

### Développement

```bash
make dev              # Lancer l'environnement de développement
make dev-build        # Build et lancer en mode dev
make dev-down         # Arrêter l'environnement de dev
```

### Production

```bash
make prod             # Lancer l'environnement de production
make prod-build       # Build et lancer en mode prod
make prod-down        # Arrêter l'environnement de prod
```

### Logs

```bash
make logs             # Tous les logs
make logs-api         # Logs de l'API
make logs-frontend    # Logs du frontend
make logs-solr        # Logs de Solr
```

### Tests

```bash
make test             # Lancer les tests
make test-cov         # Tests avec couverture
```

### Shell

```bash
make shell-api        # Accéder au conteneur API
make shell-frontend   # Accéder au conteneur frontend
make shell-solr       # Accéder au conteneur Solr
```

### Santé et monitoring

```bash
make health           # Vérifier la santé de tous les services
make stats            # Statistiques des conteneurs
make ps               # Liste des conteneurs
```

### Nettoyage

```bash
make clean            # Nettoyer conteneurs et volumes
make clean-all        # Nettoyage complet (avec images)
```

## 🔧 Configuration

### Variables d'environnement

Créez un fichier `.env` dans `search_api_solr/` :

```env
# API Settings
API_HOST=0.0.0.0
API_PORT=8007
API_RELOAD=true

# Solr Settings
SOLR_BASE_URL=http://solr:8983/solr/openedition

# Development
DEV=true
TEST_IP=195.221.21.146
LOG_LEVEL=DEBUG
```

### Frontend

Créez un fichier `.env` dans `front/` :

```env
REACT_APP_API_URL=http://localhost:8007
```

## 🏭 Environnements

### Développement

- Hot reload activé pour l'API et le frontend
- Volumes montés pour modification en temps réel
- Logs détaillés
- - Port 3009 pour le frontend (host)

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Production

- Build optimisé
- Plusieurs workers pour l'API
- Frontend servi par Nginx
- Reverse proxy optionnel
- Port 80 pour le frontend

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 🌐 Accès aux services

-### Développement
-
- Frontend : http://localhost:3009
- API : http://localhost:8007
- API Docs : http://localhost:8007/docs
- Solr Admin : http://localhost:8983/solr

### Production

- Application : http://localhost
- API : http://localhost/api
- API Docs : http://localhost/docs

## 📦 Volumes

```yaml
volumes:
  solr_data:          # Données Solr persistantes
```

Les données Solr sont persistées dans un volume Docker nommé.

## 🔌 Réseau

Tous les services communiquent via le réseau `openedition_network`.

## 🐛 Debugging

### Voir les logs en temps réel

```bash
docker-compose logs -f api
```

### Accéder au conteneur

```bash
docker-compose exec api bash
```

### Vérifier la santé

```bash
# API
curl http://localhost:8007/docs

# Frontend
curl http://localhost:3009

# Solr
curl http://localhost:8983/solr/openedition/admin/ping
```

### Redémarrer un service

```bash
docker-compose restart api
```

## 🔒 Sécurité (Production)

### HTTPS avec Let's Encrypt

Ajoutez à `docker-compose.prod.yml` :

```yaml
nginx:
  volumes:
    - ./certs:/etc/nginx/certs:ro
    - ./certbot/www:/var/www/certbot:ro
```

### Rate Limiting

Configuré dans `nginx/nginx.conf` :

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
```

## 📊 Performance

### Scaler l'API

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale api=3
```

### Optimiser Solr

Modifiez dans `docker-compose.yml` :

```yaml
environment:
  - SOLR_HEAP=2g  # Augmenter la mémoire
```

## 🔄 Mise à jour

```bash
# 1. Sauvegarder les données
docker-compose exec solr solr-backup

# 2. Arrêter les services
docker-compose down

# 3. Mettre à jour le code
git pull

# 4. Rebuilder et redémarrer
make prod-build
```

## ❓ Résolution de problèmes

### Le frontend ne peut pas contacter l'API

Vérifiez que `REACT_APP_API_URL` pointe vers la bonne URL.

### Solr ne démarre pas

```bash
# Vérifier les logs
docker-compose logs solr

# Nettoyer et redémarrer
docker-compose down -v
docker-compose up solr
```

### L'API retourne une erreur 503

Vérifiez que Solr est accessible :

```bash
docker-compose exec api curl http://solr:8983/solr/openedition/admin/ping
```

## 📚 Ressources

- [Documentation Docker Compose](https://docs.docker.com/compose/)
- [Documentation Solr](https://solr.apache.org/guide/)
- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Documentation React](https://react.dev/)
