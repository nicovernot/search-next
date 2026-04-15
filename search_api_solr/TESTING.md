# Guide de Test Rapide de l'API

## 🚀 Démarrer le Serveur

```bash
cd /home/nico/projets/search-next/search_api_solr
uvicorn app.main:app --reload --port 8007
```

## ✅ Tests Rapides

### 1. Documentation Interactive (Swagger UI)

Ouvrez dans votre navigateur :
```
http://localhost:8007/docs
```

Vous pouvez tester tous les endpoints directement depuis cette interface ! 🎯

### 2. Test avec curl

#### Endpoint `/permissions`
```bash
curl "http://localhost:8007/permissions?urls=https://example.com/doc1,https://example.com/doc2" \
  -H "X-Forwarded-For: 127.0.0.1"
```

#### Endpoint `/search`
```bash
curl -X POST "http://localhost:8007/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {"query": "openedition"},
    "filters": [
      {"identifier": "platform", "value": "openedition-books"}
    ],
    "pagination": {"from": 0, "size": 10},
    "facets": [
      {"identifier": "author"}
    ]
  }'
```

### 3. Script de Test Automatique

```bash
./test_api.sh
```

## 📊 Vérifier que ça Fonctionne

**Serveur démarré** ✅
- Vous devriez voir : `INFO: Uvicorn running on http://0.0.0.0:8007`

**Swagger UI accessible** ✅
- Ouvrez http://localhost:8007/docs
- Vous devriez voir l'interface interactive

**Endpoints répondent** ✅
- `/permissions` : Retourne les permissions des documents
- `/search` : Construit et exécute une requête Solr

## 🔍 Endpoints Disponibles

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/docs` | GET | Documentation interactive Swagger UI |
| `/openapi.json` | GET | Schéma OpenAPI |
| `/permissions` | GET | Vérifier les permissions d'accès aux documents |
| `/search` | POST | Recherche de documents dans Solr |

## 🐛 Dépannage

**Port déjà utilisé ?**
```bash
lsof -ti:8007 | xargs kill -9
```

**Erreur d'import ?**
```bash
cd /home/nico/projets/search-next/search_api_solr
python3 -c "from app.main import app; print('✅ OK')"
```

**Vérifier les settings ?**
```bash
python3 -c "from app.settings import settings; print(settings.solr_base_url)"
```
