# Implémentation du Frontend OpenEdition Search

## Vue d'ensemble

Frontend React pour OpenEdition Search intégrant :
- **React 18.2.0** : Framework UI
- **React Router 6.20.0** : Navigation
- **Custom Search Context** : Gestion d'état (remplace SearchKit v4 qui n'existe pas)
- **FastAPI Backend** : API de recherche Solr
- **Docker** : Déploiement conteneurisé
- **Nginx** : Serveur web de production

## Architecture

### Structure du projet

```
front/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/         # Composants réutilisables
│   │   ├── SearchBar.jsx
│   │   ├── ResultsList.jsx
│   │   ├── ResultItem.jsx
│   │   ├── Facets.jsx
│   │   ├── FacetGroup.jsx
│   │   └── Pagination.jsx
│   ├── contexts/           # Gestion d'état
│   │   └── SearchContext.jsx
│   ├── pages/              # Pages de l'application
│   │   └── Home.jsx
│   ├── services/           # Services API
│   │   └── api.js
│   ├── App.jsx
│   └── index.js
├── package.json
├── Dockerfile
├── nginx.conf
└── .env
```

### Flux de données

```
User Input → SearchBar → SearchContext → API Service → FastAPI → Solr
                ↓                                                     ↓
         executeSearch()                                       Results
                ↓                                                     ↓
         useSearch Hook ← SearchContext ← Response Processing ←─────┘
                ↓
    ResultsList + Facets + Pagination
```

## Composants principaux

### SearchContext (contexts/SearchContext.jsx)

Gestion centralisée de l'état de recherche :

**État géré :**
- `query` : Terme de recherche
- `results` : Documents retournés
- `facets` : Facettes disponibles
- `filters` : Filtres actifs (format: `{field: [values]}`)
- `pagination` : `{from, size}`
- `total` : Nombre total de résultats
- `loading` : État de chargement
- `error` : Messages d'erreur

**Fonctions exposées :**
- `setQuery(string)` : Mise à jour du terme de recherche
- `executeSearch()` : Lancement de la recherche
- `addFilter(field, value)` : Ajout d'un filtre
- `removeFilter(field, value)` : Suppression d'un filtre
- `clearFilters()` : Suppression de tous les filtres
- `setPage(pageNumber)` : Navigation de pagination

### API Service (services/api.js)

Communication avec le backend FastAPI :

```javascript
// Format de requête
{
  query: { query: "terme de recherche" },
  filters: [
    { identifier: "platform", value: "OB" },
    { identifier: "type", value: "livre" }
  ],
  facets: [
    { identifier: "platform", type: "list" },
    { identifier: "type", type: "list" }
  ],
  pagination: {
    from: 0,
    size: 10
  }
}
```

### Composants UI

**SearchBar** : Recherche avec auto-completion (debounce 500ms)
**ResultsList** : Affichage des résultats avec gestion des états (loading, empty, error)
**Facets** : Filtres avec tags actifs
**Pagination** : Navigation avec ellipses intelligentes

## Configuration

### Variables d'environnement (.env)

```bash
REACT_APP_API_URL=http://localhost:8007
PORT=3000
```

### Docker Compose (search_api_solr/docker-compose.yml)

```yaml
services:
  api:
    build: .
    ports:
      - "8007:8007"
    environment:
      SOLR_BASE_URL: https://solrslave-sec.labocleo.org/solr/documents

  frontend:
    build: ../front
    ports:
      - "3009:80"
    depends_on:
      - api
```

## Déploiement

### Production (Docker)

```bash
# Depuis search_api_solr/
docker compose build
docker compose up -d
```

**Accès :**
- Frontend : http://localhost:3009
- API : http://localhost:8007
- API Docs : http://localhost:8007/docs

### Développement local

```bash
# Depuis front/
npm install
npm start
```

Frontend disponible sur http://localhost:3000

## Points techniques importants

### 1. Remplacement de SearchKit

SearchKit v4.0.0 n'existant pas dans npm, nous avons créé un contexte React custom (`SearchContext.jsx`) qui :
- Gère l'état de recherche
- Communique avec l'API FastAPI
- Expose un hook `useSearch()` pour les composants

### 2. Format des filtres

**Dans l'UI (SearchContext) :**
```javascript
filters = {
  platform: ["OB", "OJ"],
  type: ["livre"]
}
```

**Envoyé à l'API :**
```javascript
filters = [
  { identifier: "platform", value: "OB" },
  { identifier: "platform", value: "OJ" },
  { identifier: "type", value: "livre" }
]
```

### 3. Pagination

Le backend utilise `from` (offset) et non `from_` :
```javascript
pagination: {
  from: 0,  // Pas from_
  size: 10
}
```

### 4. Auto-search

SearchBar déclenche automatiquement une recherche après 500ms d'inactivité si `query.length > 2`.

## Résolution de problèmes

### Build npm échoue

**Cause** : Package SearchKit v4 introuvable  
**Solution** : Utilisation du SearchContext custom (déjà implémenté)

### Nginx erreur "host not found"

**Cause** : nginx.conf référence un service inexistant  
**Solution** : Section proxy supprimée (frontend appelle directement l'API)

### API retourne 404

**Cause** : Mauvaise URL d'endpoint  
**Solution** : Utiliser `/search` et non `/api/v1/search`

### CORS errors

**Cause** : API et Frontend sur domaines différents  
**Solution** : Backend FastAPI doit avoir les headers CORS configurés

## Endpoints API utilisés

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/search` | Recherche principale |
| GET | `/search?q=...` | Recherche GET (alternative) |
| GET | `/suggest?q=...` | Auto-complétion |
| GET | `/permissions?urls=...` | Vérification accès documents |

## Prochaines étapes

- [ ] Ajouter les tests unitaires (Jest + React Testing Library)
- [ ] Implémenter la suggestion de recherche
- [ ] Ajouter la gestion des permissions de documents
- [ ] Améliorer le responsive design
- [ ] Ajouter l'internationalisation (i18n)
- [ ] Implémenter la sauvegarde de recherches
- [ ] Ajouter les analytics

## Support

Pour toute question sur l'implémentation :
1. Consulter `/docs` de l'API FastAPI
2. Voir `TESTING.md` pour les tests
3. Voir `DOCKER.md` pour Docker

---

**Version** : 0.1.0  
**Dernière mise à jour** : 2025-12-08
