# 🌐 Gestion des Environnements - OpenEdition Search API

Ce document explique comment configurer et utiliser les différents environnements pour le backend FastAPI.

## 🎯 Environnements disponibles

Le projet supporte quatre environnements principaux, chacun avec sa propre configuration :

| Environnement | Fichier | Description | Utilisation |
|---------------|---------|-------------|-------------|
| **development** | `.env.development` | Développement local | `make dev` |
| **staging** | `.env.staging` | Pré-production/test | `make staging` |
| **production** | `.env.production` | Production | `make prod` |
| **test** | `.env.test` | Tests automatisés | `make test` |

## 🚀 Configuration par Environnement

### 1. Environnement de Développement

**Fichier** : `.env.development`

**Caractéristiques** :
- ✅ Hot-reload activé
- ✅ Logging détaillé (DEBUG)
- ✅ CORS permissif pour le développement local
- ✅ Mode dev activé
- ❌ Pas de redirection HTTPS

**Configuration typique** :
```env
ENVIRONMENT=development
API_PORT=8007
API_RELOAD=true
DEV=true
CORS_ORIGINS=http://localhost:3009,http://localhost:3000
LOG_LEVEL=DEBUG
```

**Utilisation** :
```bash
# Copier la configuration de développement
cp .env.development .env

# Lancer en mode développement
make dev
# ou
./start.sh dev
```

### 2. Environnement de Staging

**Fichier** : `.env.staging`

**Caractéristiques** :
- ❌ Hot-reload désactivé
- ✅ Logging détaillé (DEBUG)
- ✅ CORS restrictif (domaines de staging)
- ✅ Sécurité renforcée
- ✅ Hôtes de confiance configurés

**Configuration typique** :
```env
ENVIRONMENT=staging
API_PORT=8000
API_RELOAD=false
DEV=false
CORS_ORIGINS=https://staging.search.openedition.org,https://search.openedition.org
LOG_LEVEL=DEBUG
TRUSTED_HOSTS=staging.search.openedition.org
```

**Utilisation** :
```bash
# Copier la configuration de staging
cp .env.staging .env

# Lancer en mode staging
make staging
```

### 3. Environnement de Production

**Fichier** : `.env.production`

**Caractéristiques** :
- ❌ Hot-reload désactivé
- ✅ Logging optimisé (INFO)
- ✅ CORS très restrictif
- ✅ HTTPS redirection activée
- ✅ Sécurité maximale
- ✅ Performance optimisée

**Configuration typique** :
```env
ENVIRONMENT=production
API_PORT=8000
API_RELOAD=false
DEV=false
CORS_ORIGINS=https://search.openedition.org,https://www.openedition.org
LOG_LEVEL=INFO
ENABLE_HTTPS_REDIRECT=true
TRUSTED_HOSTS=search.openedition.org,www.openedition.org
```

**Utilisation** :
```bash
# Copier la configuration de production
cp .env.production .env

# Lancer en mode production
make prod
```

### 4. Environnement de Test

**Fichier** : `.env.test`

**Caractéristiques** :
- ❌ Hot-reload désactivé
- ❌ Logging minimal (WARNING)
- ❌ CORS minimal
- ❌ Dev mode désactivé
- ✅ Optimisé pour les tests automatisés

**Configuration typique** :
```env
ENVIRONMENT=test
API_PORT=8007
API_RELOAD=false
DEV=false
CORS_ORIGINS=http://localhost:8007
LOG_LEVEL=WARNING
CORS_ALLOW_CREDENTIALS=false
```

**Utilisation** :
```bash
# Copier la configuration de test
cp .env.test .env

# Lancer les tests
make test
```

## 🔧 Configuration CORS par Environnement

La configuration CORS est automatiquement adaptée selon l'environnement grâce aux validateurs dans `app/settings.py` :

### Développement
```python
# Origines autorisées
cors_origins = ["http://localhost:3009", "http://localhost:3000", "http://127.0.0.1:3009"]

# Méthodes autorisées
cors_allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]

# Headers autorisés
cors_allow_headers = ["Accept", "Authorization", "Content-Type", "X-Requested-With", "X-CSRF-Token"]

# Durée de cache
cors_max_age = 86400  # 24 heures
```

### Production
```python
# Origines autorisées (très restrictif)
cors_origins = ["https://search.openedition.org", "https://www.openedition.org"]

# Méthodes autorisées (minimales)
cors_allow_methods = ["GET", "POST", "OPTIONS"]

# Headers autorisés (minimaux)
cors_allow_headers = ["Accept", "Authorization", "Content-Type"]

# Durée de cache
cors_max_age = 3600  # 1 heure
```

### Tableau comparatif CORS

| Paramètre | Développement | Staging | Production | Test |
|-----------|--------------|---------|------------|------|
| **Origines** | Locales multiples | Staging + Prod | Production uniquement | Locale unique |
| **Méthodes** | Toutes | GET, POST, PUT, OPTIONS | GET, POST, OPTIONS | GET, POST |
| **Headers** | Étendus | Standard | Minimaux | Minimaux |
| **Credentials** | ✅ Oui | ✅ Oui | ✅ Oui | ❌ Non |
| **Max Age** | 24h | 1h | 1h | 1min |

## 🛠️ Gestion des Environnements

### 1. Sélection de l'environnement

**Méthode 1 : Variable d'environnement**
```bash
export ENVIRONMENT=development
# ou
export ENVIRONMENT=production
```

**Méthode 2 : Fichier .env**
```bash
cp .env.development .env
# ou
cp .env.production .env
```

### 2. Vérification de l'environnement actuel

```python
from app.settings import settings

print(f"Environment: {settings.environment}")
print(f"CORS Origins: {settings.cors_origins}")
print(f"Log Level: {settings.log_level}")
```

### 3. Utilisation avec Docker

**Docker Compose avec environnement spécifique** :

```yaml
# docker-compose.override.yml
version: '3.8'

services:
  api:
    env_file:
      - .env.development
    environment:
      - ENVIRONMENT=development
```

**Commandes Docker** :

```bash
# Développement
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## 🔒 Sécurité par Environnement

### Développement
- ⚠️ CORS permissif (mais contrôlé)
- ⚠️ Dev mode activé
- ❌ Pas de redirection HTTPS
- ❌ Pas de hôtes de confiance par défaut

### Production
- ✅ CORS très restrictif
- ✅ HTTPS redirection activée
- ✅ Hôtes de confiance configurés
- ✅ Logging optimisé
- ✅ Timeout réduits

### Configuration de sécurité

**Redirection HTTPS** :
```python
# Activée automatiquement en production
if settings.enable_https_redirect:
    app.add_middleware(HTTPSRedirectMiddleware)
```

**Hôtes de confiance** :
```python
# Configurés selon l'environnement
if settings.trusted_hosts:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)
```

## 📊 Variables d'Environnement Principales

### Variables Obligatoires

| Variable | Description | Exemple |
|----------|-------------|---------|
| `ENVIRONMENT` | Environnement actuel | `development`, `production` |
| `SOLR_BASE_URL` | URL de l'instance Solr | `https://solr.openedition.org/solr/documents` |

### Variables CORS

| Variable | Description | Valeurs possibles |
|----------|-------------|------------------|
| `CORS_ORIGINS` | Origines autorisées | `http://localhost:3009,https://example.com` |
| `CORS_ALLOW_CREDENTIALS` | Autoriser credentials | `true`, `false` |
| `CORS_ALLOW_METHODS` | Méthodes HTTP | `GET,POST,OPTIONS` |
| `CORS_ALLOW_HEADERS` | Headers autorisés | `Accept,Authorization,Content-Type` |
| `CORS_MAX_AGE` | Cache CORS | `3600` (1 heure) |

### Variables de Sécurité

| Variable | Description | Valeurs possibles |
|----------|-------------|------------------|
| `ENABLE_HTTPS_REDIRECT` | Redirection HTTPS | `true`, `false` |
| `TRUSTED_HOSTS` | Hôtes de confiance | `search.openedition.org,www.openedition.org` |
| `DEV` | Mode développement | `true`, `false` |

### Variables de Configuration

| Variable | Description | Valeurs possibles |
|----------|-------------|------------------|
| `API_HOST` | Hôte de l'API | `0.0.0.0` |
| `API_PORT` | Port de l'API | `8000`, `8007` |
| `API_RELOAD` | Hot-reload | `true`, `false` |
| `LOG_LEVEL` | Niveau de logging | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

## 🧪 Tests par Environnement

### Exécuter les tests avec un environnement spécifique

```bash
# Tests en environnement de développement
export ENVIRONMENT=development
pytest

# Tests en environnement de staging
export ENVIRONMENT=staging
pytest

# Tests en environnement de production (simulé)
export ENVIRONMENT=test
pytest
```

### Tests de configuration CORS

```python
# tests/test_cors.py
from fastapi.testclient import TestClient
from app.main import app
from app.settings import settings

def test_cors_configuration():
    client = TestClient(app)
    
    # Test que les origines autorisées fonctionnent
    for origin in settings.cors_origins:
        response = client.get("/search", headers={"Origin": origin})
        assert response.headers["access-control-allow-origin"] == origin
    
    # Test qu'une origine non autorisée est bloquée (en prod/staging)
    if settings.environment in ["production", "staging"]:
        response = client.get("/search", headers={"Origin": "https://evil.com"})
        assert response.status_code == 403
```

## 🚀 Workflow de Déploiement

### 1. Développement → Staging

```bash
# 1. Tester en développement
export ENVIRONMENT=development
make test

# 2. Préparer pour le staging
cp .env.staging .env
docker-compose -f docker-compose.yml -f docker-compose.staging.yml build

# 3. Déployer en staging
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d

# 4. Tester en staging
make test-staging
```

### 2. Staging → Production

```bash
# 1. Valider le staging
make validate-staging

# 2. Préparer pour la production
cp .env.production .env
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# 3. Déployer en production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale api=3

# 4. Vérifier la production
make health-check
```

## 📋 Bonnes Pratiques

### 1. Gestion des Fichiers .env

- ❌ **Ne jamais commiter** les fichiers `.env` (ils sont dans `.gitignore`)
- ✅ **Utiliser des valeurs par défaut sécurisées** dans le code
- ✅ **Documenter** toutes les variables d'environnement
- ✅ **Valider** les configurations avant le déploiement

### 2. Sécurité

- ✅ **Toujours spécifier** l'environnement explicitement
- ✅ **Limiter les permissions** en production
- ✅ **Utiliser HTTPS** en production et staging
- ✅ **Configurer CORS** de manière restrictive

### 3. Développement

- ✅ **Utiliser `.env.development`** pour le développement local
- ✅ **Activer le hot-reload** en développement
- ✅ **Utiliser un niveau de logging élevé** (DEBUG)
- ✅ **Tester** avec différents environnements

### 4. Déploiement

- ✅ **Toujours tester** en staging avant la production
- ✅ **Utiliser des configurations différentes** pour chaque environnement
- ✅ **Monitorer** après le déploiement
- ✅ **Avoir un plan de rollback**

## 🔧 Dépannage

### Problème : CORS bloqué en développement

**Solution** :
1. Vérifiez que `ENVIRONMENT=development` est bien défini
2. Assurez-vous que `.env` contient les bonnes origines locales
3. Vérifiez que le frontend utilise le bon port

### Problème : Configuration non chargée

**Solution** :
1. Vérifiez que le fichier `.env` existe
2. Assurez-vous que les variables sont correctement formatées
3. Redémarrez l'application après modification du `.env`

### Problème : Environnement non reconnu

**Solution** :
1. Vérifiez que `ENVIRONMENT` est défini dans `.env`
2. Utilisez uniquement : `development`, `staging`, `production`, `test`
3. Vérifiez la casse (insensible mais recommandé en minuscules)

## 📚 Documentation Complémentaire

- [FastAPI Environments](https://fastapi.tiangolo.com/advanced/settings/)
- [12 Factor App](https://12factor.net/config)
- [Python Decouple](https://pypi.org/project/python-decouple/)
- [OWASP Security Configuration](https://cheatsheetseries.owasp.org/)

## 🎯 Conclusion

La gestion des environnements est cruciale pour :

1. **Sécurité** : Configurations adaptées à chaque contexte
2. **Maintenabilité** : Code plus facile à gérer
3. **Fiabilité** : Tests dans des conditions réalistes
4. **Flexibilité** : Adaptation aux différents besoins

En utilisant cette structure, vous bénéficiez d'une configuration robuste et sécurisée pour tous vos environnements de développement, test, staging et production.
