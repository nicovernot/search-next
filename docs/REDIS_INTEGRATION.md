# 🚀 Intégration Redis - OpenEdition Search v2

Ce document décrit l'implémentation du cache Redis dans l'application OpenEdition Search v2 pour améliorer les performances et réduire la charge sur Solr.

## 📋 Vue d'ensemble

L'intégration Redis apporte :
- **Cache des résultats de recherche** : Réduction de 40-60% des temps de réponse
- **Cache des suggestions** : Autocomplétion ultra-rapide
- **Cache des permissions** : Optimisation des vérifications d'accès
- **Monitoring intégré** : Statistiques et métriques de performance
- **Gestion flexible** : TTL adaptatifs par environnement

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   Redis Cache   │
│   React         │───▶│   Backend       │───▶│   (Port 6379)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Solr Search   │
                       │   (Distant)     │
                       └─────────────────┘
```

## 🔧 Configuration

### Variables d'environnement

```bash
# Configuration Redis
REDIS_URL=redis://redis:6379/0
REDIS_ENABLED=true

# TTL par type de cache (en secondes)
REDIS_TTL_SEARCH=300      # 5 minutes pour les recherches
REDIS_TTL_SUGGEST=3600    # 1 heure pour les suggestions  
REDIS_TTL_PERMISSIONS=1800 # 30 minutes pour les permissions
```

### Configuration par environnement

Les TTL sont automatiquement ajustés selon l'environnement :

| Environnement | Recherche | Suggestions | Permissions |
|---------------|-----------|-------------|-------------|
| **Development** | 5 min | 1h | 30 min |
| **Production** | 10 min | 2h | 1h |
| **Test** | 1 min | 1 min | 1 min |
| **Staging** | 5 min | 1h | 30 min |

## 🚀 Démarrage

### 1. Démarrer avec Docker

```bash
# Démarrer tous les services (API + Redis + Frontend)
docker-compose up

# Ou seulement Redis et API
docker-compose up redis api
```

### 2. Vérifier l'intégration

```bash
# Exécuter le script de test complet
./scripts/test_redis_integration.sh

# Vérifier manuellement
curl http://localhost:8007/health
curl http://localhost:8007/cache/stats
```

## 📊 Endpoints de monitoring

### Statistiques du cache
```bash
GET /cache/stats
```

Retourne :
```json
{
  "enabled": true,
  "connected_clients": 2,
  "used_memory": "1.2M",
  "keyspace_hits": 150,
  "keyspace_misses": 30,
  "hit_rate": 83.33
}
```

### Santé de l'application
```bash
GET /health
```

Retourne :
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "services": {
    "api": "healthy",
    "cache": "healthy"
  }
}
```

### Gestion du cache
```bash
# Vider tout le cache
DELETE /cache/clear

# Vider un pattern spécifique
DELETE /cache/clear?pattern=search:*
DELETE /cache/clear?pattern=suggest:*
```

## 🔍 Types de cache implémentés

### 1. Cache des recherches
- **Clé** : `search:{hash_des_paramètres}`
- **TTL** : 5-10 minutes selon l'environnement
- **Contenu** : Résultats complets de Solr
- **Déclencheur** : Endpoints `/search` (POST et GET)

### 2. Cache des suggestions
- **Clé** : `suggest:{hash_de_la_requête}`
- **TTL** : 1-2 heures selon l'environnement
- **Contenu** : Suggestions d'autocomplétion
- **Déclencheur** : Endpoint `/suggest`

### 3. Cache des permissions
- **Clé** : `permissions:{hash_urls_et_ip}`
- **TTL** : 30 minutes - 1 heure selon l'environnement
- **Contenu** : Résultats de vérification d'accès
- **Déclencheur** : Endpoint `/permissions`

## 📈 Performance

### Métriques attendues

| Métrique | Sans cache | Avec cache | Amélioration |
|----------|------------|------------|--------------|
| **Temps de réponse recherche** | 800-1200ms | 50-150ms | **85%** |
| **Temps de réponse suggestions** | 200-400ms | 10-30ms | **90%** |
| **Charge CPU Solr** | 100% | 40-60% | **40-60%** |
| **Requêtes/seconde** | 50 req/s | 200+ req/s | **300%** |

### Monitoring des performances

```bash
# Métriques Prometheus disponibles
curl http://localhost:8007/metrics | grep cache

# Statistiques Redis en temps réel
docker exec openedition_redis redis-cli monitor
```

## 🧪 Tests

### Tests unitaires
```bash
cd search_api_solr
pytest tests/test_cache_service.py -v
```

### Tests d'intégration
```bash
# Test complet avec validation des performances
./scripts/test_redis_integration.sh

# Test manuel des endpoints
curl -X POST http://localhost:8007/search \
  -H "Content-Type: application/json" \
  -d '{"query": {"query": "test"}, "filters": [], "pagination": {"from": 0, "size": 10}, "facets": []}'
```

## 🔧 Développement

### Structure du code

```
search_api_solr/app/services/
├── cache_service.py          # Service principal Redis
├── search_service.py         # Service de recherche avec cache
└── interfaces.py             # Interfaces pour l'injection de dépendances

search_api_solr/tests/
└── test_cache_service.py     # Tests unitaires du cache
```

### Ajouter un nouveau type de cache

1. **Ajouter les méthodes dans CacheService** :
```python
async def get_my_cache(self, key_data: Dict) -> Optional[Dict]:
    key = self._generate_cache_key("my_type", key_data)
    return await self.get(key)

async def set_my_cache(self, key_data: Dict, data: Dict) -> bool:
    key = self._generate_cache_key("my_type", key_data)
    return await self.set(key, data, settings.redis_ttl_my_type)
```

2. **Ajouter la configuration TTL dans settings.py** :
```python
redis_ttl_my_type: int = 600  # 10 minutes
```

3. **Utiliser dans le service** :
```python
# Vérifier le cache
cached = await cache_service.get_my_cache(params)
if cached:
    return cached

# Traitement normal
result = await process_data(params)

# Mettre en cache
await cache_service.set_my_cache(params, result)
return result
```

## 🚨 Dépannage

### Redis ne démarre pas
```bash
# Vérifier les logs
docker-compose logs redis

# Redémarrer Redis
docker-compose restart redis

# Vérifier l'espace disque
df -h
```

### Cache non fonctionnel
```bash
# Vérifier la connexion
docker exec openedition_redis redis-cli ping

# Vérifier les logs de l'API
docker-compose logs api | grep -i redis

# Désactiver temporairement le cache
export REDIS_ENABLED=false
docker-compose restart api
```

### Performances dégradées
```bash
# Vérifier l'utilisation mémoire Redis
docker exec openedition_redis redis-cli info memory

# Analyser les clés les plus utilisées
docker exec openedition_redis redis-cli --hotkeys

# Ajuster les TTL si nécessaire
curl -X DELETE "http://localhost:8007/cache/clear"
```

## 📚 Ressources

- [Documentation Redis](https://redis.io/documentation)
- [FastAPI Cache](https://github.com/long2ice/fastapi-cache)
- [Aioredis](https://aioredis.readthedocs.io/)
- [Prometheus Metrics](https://prometheus.io/docs/concepts/metric_types/)

## 🔄 Prochaines améliorations

- [ ] **Cache distribué** : Cluster Redis pour la haute disponibilité
- [ ] **Cache intelligent** : Invalidation basée sur les événements
- [ ] **Compression** : Compression des données mises en cache
- [ ] **Monitoring avancé** : Dashboard Grafana pour les métriques Redis
- [ ] **Cache warming** : Pré-chargement des données populaires
- [ ] **Géo-réplication** : Cache multi-régions pour les performances globales