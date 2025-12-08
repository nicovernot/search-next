# 🎉 Mise à jour Docker & Docker Compose - Résumé

## ✅ Fichiers créés/modifiés

### Configuration Docker

#### 1. **docker-compose.yml** (Mise à jour)
Configuration de base avec 3 services :
- **Solr** : Moteur de recherche (port 8983)
- **API** : Backend FastAPI (port 8007)
- **Frontend** : Application React (port 3000 en dev, 80 en prod)

Tous les services sont connectés via le réseau `openedition_network`.

#### 2. **docker-compose.dev.yml** (Nouveau)
Configuration spécifique pour le développement :
- Hot reload activé
- Volumes montés pour modification en temps réel
- Logs détaillés
- Frontend en mode développement avec Node.js

#### 3. **docker-compose.prod.yml** (Nouveau)
Configuration pour la production :
- Build optimisé
- Plusieurs workers pour l'API
- Frontend servi par Nginx
- Reverse proxy Nginx optionnel avec SSL

### Configuration Nginx

#### 4. **nginx/conf.d/default.conf** (Nouveau)
Configuration du reverse proxy :
- Routes `/api/*` vers le backend
- Routes `/` vers le frontend
- Headers de sécurité
- Gestion des timeouts

#### 5. **nginx/nginx.conf** (Nouveau)
Configuration globale Nginx :
- Compression gzip
- Rate limiting
- Logs configurés
- Optimisations de performance

### Scripts et outils

#### 6. **Makefile** (Nouveau)
Commandes simplifiées pour gérer Docker :
```bash
make dev          # Développement
make prod         # Production
make test         # Tests
make logs         # Logs
make clean        # Nettoyage
make health       # Vérifier la santé
```

#### 7. **start.sh** (Nouveau)
Script interactif de démarrage :
```bash
./start.sh dev    # Mode développement
./start.sh prod   # Mode production
./start.sh test   # Lancer les tests
./start.sh clean  # Nettoyer
```

### Documentation

#### 8. **DOCKER.md** (Nouveau)
Documentation complète de Docker :
- Architecture des services
- Commandes disponibles
- Configuration
- Environnements (dev/prod)
- Debugging
- Sécurité
- Performance
- Résolution de problèmes

#### 9. **README.md** (Mis à jour)
README principal du projet avec :
- Architecture globale
- Démarrage rapide
- Structure des projets
- Documentation des endpoints
- Guide de contribution

#### 10. **.env.example** (Mis à jour)
Variables d'environnement à jour avec :
- Port 8007 (au lieu de 8000)
- Configuration Solr
- Mode développement
- CORS configuré

## 🚀 Utilisation

### Démarrage rapide

```bash
cd search_api_solr

# Avec le script (recommandé)
./start.sh dev

# Avec Make
make dev

# Avec Docker Compose directement
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Services disponibles

Une fois démarré, vous aurez accès à :

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Application React |
| API | http://localhost:8007 | Backend FastAPI |
| API Docs | http://localhost:8007/docs | Documentation Swagger |
| Solr Admin | http://localhost:8983/solr | Interface Solr |

### Commandes courantes

```bash
# Voir les logs
make logs
make logs-api
make logs-frontend

# Tests
make test

# Santé des services
make health

# Redémarrer
make restart

# Nettoyer
make clean
```

## 🏗️ Architecture

```
┌─────────────┐
│   Navigateur │
└──────┬──────┘
       │
       │ Port 3000 (dev) / 80 (prod)
       ▼
┌─────────────────┐
│    Frontend     │
│   React + SK    │
└────────┬────────┘
         │
         │ HTTP Requests
         ▼
┌─────────────────┐
│   API FastAPI   │
│   Port 8007     │
└────────┬────────┘
         │
         │ Solr Queries
         ▼
┌─────────────────┐
│   Solr 9.4      │
│   Port 8983     │
└─────────────────┘
```

## 🔧 Configuration

### Développement

Les fichiers `.env` doivent être configurés :

**Backend** (`search_api_solr/.env`) :
```env
SOLR_BASE_URL=http://solr:8983/solr/openedition
API_PORT=8007
DEV=true
LOG_LEVEL=DEBUG
```

**Frontend** (`front/.env`) :
```env
REACT_APP_API_URL=http://localhost:8007
```

### Production

Pour la production, utilisez :
```bash
./start.sh prod
# ou
make prod
```

Cela démarre :
- Frontend optimisé et minifié
- API avec plusieurs workers
- Nginx comme reverse proxy (optionnel)

## 🎯 Avantages de cette configuration

### ✅ Pour le développement

1. **Hot Reload** : Les modifications sont prises en compte immédiatement
2. **Logs détaillés** : Debugging facilité
3. **Isolation** : Chaque service dans son conteneur
4. **Reproductibilité** : Même environnement pour tous les développeurs

### ✅ Pour la production

1. **Performance** : Build optimisé, plusieurs workers
2. **Sécurité** : Headers de sécurité, rate limiting
3. **Scalabilité** : Facile de scaler avec `--scale`
4. **Monitoring** : Health checks intégrés

### ✅ Pour tous

1. **Simplicité** : Commandes make/script simples
2. **Documentation** : Guides complets
3. **Flexibilité** : Configuration modulaire (dev/prod)
4. **Maintenance** : Facile à mettre à jour

## 🐛 Dépannage

### Le frontend ne démarre pas

```bash
# Vérifier les logs
make logs-frontend

# Reconstruire
make dev-build
```

### L'API ne peut pas contacter Solr

Dans Docker, utilisez le nom du service :
```env
SOLR_BASE_URL=http://solr:8983/solr/openedition
```

Pas `localhost` !

### Port déjà utilisé

Modifiez les ports dans `docker-compose.yml` :
```yaml
ports:
  - "8008:8007"  # Au lieu de 8007:8007
```

## 📦 Volumes persistants

Les données Solr sont persistées dans un volume Docker :
```yaml
volumes:
  solr_data:
    driver: local
```

Pour sauvegarder :
```bash
docker run --rm -v solr_data:/data -v $(pwd):/backup alpine tar czf /backup/solr-backup.tar.gz /data
```

## 🔄 Prochaines étapes

1. **Configurer Solr** : Créer les cores et schémas nécessaires
2. **Indexer des données** : Importer les documents dans Solr
3. **Tester le frontend** : Vérifier que la recherche fonctionne
4. **Configurer SSL** : Pour la production (Let's Encrypt)
5. **Monitoring** : Ajouter Prometheus/Grafana si besoin

## 💡 Conseils

- Utilisez **toujours** les scripts ou Make pour démarrer
- Consultez les logs en cas de problème (`make logs`)
- En production, activez SSL et configurez un nom de domaine
- Sauvegardez régulièrement les données Solr
- Utilisez des variables d'environnement pour les secrets

## 📚 Documentation complète

Pour plus de détails, consultez :
- [DOCKER.md](DOCKER.md) - Guide Docker complet
- [README.md](../README.md) - Documentation générale
- [front/README.md](../front/README.md) - Documentation frontend

Bonne utilisation ! 🚀
