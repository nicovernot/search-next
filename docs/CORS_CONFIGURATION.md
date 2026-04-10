# 🔒 Configuration CORS - Bonnes pratiques pour OpenEdition Search v2

Ce document détaille comment configurer correctement CORS (Cross-Origin Resource Sharing) pour votre application, avec des solutions adaptées aux environnements de développement et de production.

## 🎯 Problème actuel

La configuration actuelle dans `app/main.py` est trop permissive :

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ Trop permissif - permet toutes les origines
    allow_credentials=True,
    allow_methods=["*"],  # ❌ Trop permissif - permet toutes les méthodes
    allow_headers=["*"],  # ❌ Trop permissif - permet tous les headers
)
```

**Risques associés :**
- Vulnérabilité aux attaques CSRF (Cross-Site Request Forgery)
- Exposition des endpoints sensibles
- Risque de fuite de données
- Non-conformité aux bonnes pratiques de sécurité

## ✅ Solution recommandée

### 1. Configuration via les settings

**a) Créer/modifier le fichier de configuration :**

```python
# app/settings.py
from pydantic import BaseSettings, AnyHttpUrl
from typing import List
import os

class Settings(BaseSettings):
    # ... vos autres settings existantes ...
    
    # Configuration CORS
    cors_origins: List[AnyHttpUrl] = []
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_allow_headers: List[str] = [
        "Accept",
        "Authorization",
        "Content-Type",
        "X-Requested-With",
        "X-CSRF-Token"
    ]
    cors_max_age: int = 86400  # 24 heures
    
    # Environnement
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

**b) Configurer les origines autorisées dans `.env` :**

```env
# Pour le développement
CORS_ORIGINS=http://localhost:3009,http://localhost:3000,http://127.0.0.1:3009

# Pour la production (exemple)
# CORS_ORIGINS=https://search.openedition.org,https://www.openedition.org

# Environnement
ENVIRONMENT=development
```

### 2. Configuration CORS sécurisée

**a) Modifier la configuration dans `app/main.py` :**

```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware
from app.settings import settings

app = FastAPI()

# Configuration CORS sécurisée
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
        expose_headers=["X-Total-Count", "X-Pagination"],
        max_age=settings.cors_max_age,
    )
else:
    # En développement sans CORS_ORIGINS défini, on peut permettre local
    if settings.environment == "development":
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3009", "http://localhost:3000"],
            allow_credentials=True,
            allow_methods=["GET", "POST"],
            allow_headers=["Content-Type", "Authorization"],
        )
```

### 3. Configuration spécifique par environnement

#### 🔧 Environnement de Développement

**Fichier `.env.development` :**
```env
# Développement - plus permissif mais contrôlé
CORS_ORIGINS=http://localhost:3009,http://localhost:3000,http://127.0.0.1:3009,http://127.0.0.1:3000
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_ALLOW_HEADERS=Accept,Authorization,Content-Type,X-Requested-With
CORS_MAX_AGE=86400
ENVIRONMENT=development
```

**Avantages en développement :**
- Permet le travail local avec différents ports
- Facilite le développement frontend/backend séparé
- Toujours contrôlé (pas de `*`)

#### 🏢 Environnement de Production

**Fichier `.env.production` :**
```env
# Production - très restrictif
CORS_ORIGINS=https://search.openedition.org,https://www.openedition.org
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=GET,POST,OPTIONS
CORS_ALLOW_HEADERS=Accept,Authorization,Content-Type
CORS_MAX_AGE=3600
ENVIRONMENT=production
```

**Bonnes pratiques en production :**
- Liste blanche explicite des domaines autorisés
- Méthodes HTTP minimales nécessaires
- Headers strictement nécessaires
- `max_age` plus court pour plus de sécurité

### 4. Gestion dynamique des origines

Pour les environnements où les origines peuvent varier (comme les environnements de staging) :

```python
# app/settings.py
from typing import List, Optional
import os

def get_cors_origins() -> List[str]:
    """Récupère les origines CORS depuis les variables d'environnement"""
    cors_origins = os.getenv("CORS_ORIGINS", "")
    if cors_origins:
        return [origin.strip() for origin in cors_origins.split(",")]
    
    # Valeurs par défaut selon l'environnement
    env = os.getenv("ENVIRONMENT", "development")
    if env == "production":
        return ["https://search.openedition.org"]
    elif env == "staging":
        return ["https://staging.search.openedition.org", "https://search.openedition.org"]
    else:  # développement
        return ["http://localhost:3009", "http://localhost:3000"]

class Settings(BaseSettings):
    cors_origins: List[str] = get_cors_origins()
    # ... reste de la configuration ...
```

### 5. Middleware CORS avancé

Pour une gestion plus fine, vous pouvez créer un middleware personnalisé :

```python
# app/middleware/cors.py
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.settings import settings
import logging

logger = logging.getLogger(__name__)

class CustomCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log des requêtes CORS
        origin = request.headers.get("origin")
        if origin:
            logger.debug(f"CORS request from origin: {origin}")
            
            # Vérification supplémentaire de sécurité
            if origin not in settings.cors_origins and settings.environment != "development":
                logger.warning(f"Blocked CORS request from unauthorized origin: {origin}")
                return Response(
                    content="Not allowed by CORS policy",
                    status_code=403,
                    headers={"Content-Type": "text/plain"}
                )
        
        # Appel au middleware CORS standard
        response = await CORSMiddleware(
            app=call_next.app,
            allow_origins=settings.cors_origins,
            allow_credentials=settings.cors_allow_credentials,
            allow_methods=settings.cors_allow_methods,
            allow_headers=settings.cors_allow_headers,
            expose_headers=["X-Total-Count", "X-Pagination"],
            max_age=settings.cors_max_age,
        ).dispatch(request, call_next)
        
        return response
```

### 6. Configuration pour les tests

**Fichier `.env.test` :**
```env
# Tests - configuration spécifique
CORS_ORIGINS=http://localhost:8007
CORS_ALLOW_CREDENTIALS=false
CORS_ALLOW_METHODS=GET,POST
CORS_ALLOW_HEADERS=Content-Type
CORS_MAX_AGE=60
ENVIRONMENT=test
```

### 7. Vérification et tests

**a) Test de la configuration CORS :**

```python
# tests/test_cors.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.settings import settings

client = TestClient(app)

class TestCORS:
    """Tests pour la configuration CORS"""
    
    def test_cors_allowed_origins(self):
        """Test que les origines autorisées fonctionnent"""
        for origin in settings.cors_origins:
            response = client.get("/search", headers={"Origin": origin})
            assert response.headers["access-control-allow-origin"] == origin
            assert "GET" in response.headers["access-control-allow-methods"]
    
    def test_cors_blocked_origin(self):
        """Test qu'une origine non autorisée est bloquée"""
        if settings.environment != "development":
            response = client.get("/search", headers={"Origin": "https://evil.com"})
            # En production, devrait être bloqué
            assert response.status_code == 403
    
    def test_cors_preflight(self):
        """Test les requêtes OPTIONS (preflight)"""
        response = client.options("/search", headers={
            "Origin": settings.cors_origins[0],
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,authorization"
        })
        assert response.status_code == 200
        assert "POST" in response.headers["access-control-allow-methods"]
        assert "content-type" in response.headers["access-control-allow-headers"]
```

**b) Commandes pour tester manuellement :**

```bash
# Tester les headers CORS
curl -I -H "Origin: http://localhost:3009" http://localhost:8007/search

# Tester une requête OPTIONS (preflight)
curl -X OPTIONS -H "Origin: http://localhost:3009" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: content-type" \
     http://localhost:8007/search
```

### 8. Bonnes pratiques supplémentaires

**a) Gestion des credentials :**
- `allow_credentials=True` doit être utilisé avec prudence
- Ne l'activer que si votre application utilise des cookies ou l'authentification
- En production, assurez-vous que les origines sont HTTPS

**b) Headers de sécurité supplémentaires :**

```python
# Dans app/main.py
from fastapi.middleware import Middleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Redirection HTTPS (pour la production)
if settings.environment == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# Protection contre les attaques DNS rebinding
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["search.openedition.org", "www.openedition.org"]
)
```

**c) Headers de sécurité HTTP :**

```python
# app/middleware/security.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Headers de sécurité recommandés
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Cache control pour les endpoints sensibles
        if request.url.path.startswith("/api"):
            response.headers["Cache-Control"] = "no-store, must-revalidate"
        
        return response
```

### 9. Configuration pour les environnements spécifiques

#### Docker Compose

**Dans `docker-compose.yml` :**

```yaml
services:
  api:
    environment:
      - CORS_ORIGINS=http://localhost:3009,http://frontend:80
      - ENVIRONMENT=development
    # ... reste de la configuration ...
```

#### Kubernetes/Production

**Dans votre configuration Kubernetes :**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: search-api-config
  namespace: openedition
data:
  CORS_ORIGINS: "https://search.openedition.org,https://www.openedition.org"
  ENVIRONMENT: "production"
  CORS_ALLOW_METHODS: "GET,POST,OPTIONS"
  CORS_ALLOW_HEADERS: "Accept,Authorization,Content-Type"
```

### 10. Résolution des problèmes courants

**Problème 1 : CORS bloqué en développement**

**Solution :**
1. Vérifiez que `.env` contient les bonnes origines
2. Assurez-vous que le frontend utilise le bon port
3. Vérifiez que `ENVIRONMENT=development` est bien défini

**Problème 2 : Les credentials ne sont pas envoyés**

**Solution :**
1. Assurez-vous que `allow_credentials=True`
2. Le frontend doit inclure `credentials: 'include'` dans les requêtes
3. L'origine doit être exacte (pas de wildcard)

**Problème 3 : Les requêtes OPTIONS échouent**

**Solution :**
1. Vérifiez que la méthode OPTIONS est autorisée
2. Assurez-vous que les headers demandés sont dans `allow_headers`
3. Vérifiez que `max_age` n'est pas trop court

## 📋 Checklist de mise en œuvre

- [ ] Créer/modifier `app/settings.py` avec la configuration CORS
- [ ] Mettre à jour `.env` avec les origines appropriées
- [ ] Modifier `app/main.py` pour utiliser la configuration sécurisée
- [ ] Créer des fichiers `.env` spécifiques par environnement
- [ ] Ajouter des tests pour la configuration CORS
- [ ] Configurer les headers de sécurité supplémentaires
- [ ] Mettre à jour la documentation avec les nouvelles configurations
- [ ] Tester dans tous les environnements (dev, staging, prod)

## 🎯 Impact attendu

**Avant la correction :**
- ❌ Configuration CORS trop permissive (`allow_origins=["*"]`)
- ❌ Risque de sécurité élevé
- ❌ Non-conformité aux bonnes pratiques

**Après la correction :**
- ✅ Liste blanche explicite des origines autorisées
- ✅ Configuration adaptée à chaque environnement
- ✅ Sécurité renforcée contre les attaques CORS
- ✅ Conformité aux standards de sécurité
- ✅ Meilleure maintenabilité et traçabilité

## 📚 Ressources supplémentaires

- [MDN Web Docs - CORS](https://developer.mozilla.org/fr/docs/Web/HTTP/CORS)
- [OWASP - CORS Security](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html#cross-origin-resource-sharing)
- [FastAPI CORS Documentation](https://fastapi.tiangolo.com/tutorial/cors/)
- [CORS RFC 6454](https://tools.ietf.org/html/rfc6454)

## 🔒 Conclusion

La configuration CORS est un élément crucial de la sécurité de votre application. En passant d'une configuration permissive (`allow_origins=["*"]`) à une configuration sécurisée avec liste blanche, vous :

1. **Réduisez les risques de sécurité** en limitant les origines autorisées
2. **Améliorez la conformité** aux standards de sécurité
3. **Facilitez la maintenance** avec une configuration claire par environnement
4. **Préparez votre application** pour la production

Cette configuration doit être combinée avec d'autres mesures de sécurité comme le rate limiting, la validation des entrées et l'authentification pour une protection complète de votre API.
