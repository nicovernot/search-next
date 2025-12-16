# Gestion des Environnements - SearchV2

## Structure des Fichiers d'Environnement

Le projet utilise une approche centralisée pour la gestion des environnements avec héritage :

```
.
├── .env.shared          # Variables communes à tous les environnements
├── .env.development     # Variables spécifiques au développement
├── .env.production      # Variables spécifiques à la production
├── .env.staging         # Variables spécifiques au staging
├── .env.test            # Variables spécifiques aux tests
├── .env.example         # Template avec toutes les variables possibles
├── scripts/sync_env.sh  # Script de synchronisation
├── scripts/run_tests.sh # Script pour exécuter les tests
└── search_api_solr/app/core/env_validation.py  # Validation backend
└── front/src/utils/envValidation.js           # Validation frontend
```

## Hiérarchie des Environnements

1. **`.env.shared`** - Chargé en premier, contient les variables communes
2. **`.env.{environment}`** - Surcharge les variables spécifiques à l'environnement
3. **`{service}/.env.local`** - Fichiers générés, ne pas éditer manuellement

## Utilisation

### Pour le développement

```bash
# Synchroniser l'environnement de développement
./scripts/sync_env.sh development

# Démarrer les services
docker-compose up
```

### Pour les tests

```bash
# Synchroniser l'environnement de test
./scripts/sync_env.sh test

# Exécuter tous les tests
./scripts/run_tests.sh

# Ou exécuter des tests spécifiques
cd search_api_solr && python -m pytest tests/test_search_builder.py -v
```

### Pour le staging

```bash
# Synchroniser l'environnement de staging
./scripts/sync_env.sh staging

# Démarrer avec la configuration staging
docker-compose -f docker-compose.staging.yml up --build
```

### Pour la production

```bash
# Synchroniser l'environnement de production
./scripts/sync_env.sh production

# Construire et démarrer
docker-compose -f docker-compose.prod.yml up --build
```

## Variables d'Environnement

### Variables Frontend (React)

Toutes les variables frontend doivent être préfixées par `REACT_APP_` :

- `REACT_APP_API_URL` : URL de l'API backend
- `REACT_APP_DEBUG` : Active/désactive le mode debug
- `REACT_APP_MOCK_API` : Utilise des données mockées

### Variables Backend (FastAPI)

- `API_BASE_URL` : URL base de l'API
- `SOLR_URL` : URL du serveur Solr
- `SOLR_COLLECTION` : Collection Solr à utiliser
- `DEBUG` : Mode debug
- `AUTO_RELOAD` : Rechargement automatique du code
- `JWT_SECRET` : Secret pour les tokens JWT
- `SESSION_SECRET` : Secret pour les sessions

### Variables Communes

- `NODE_ENV` : Environnement (development, production, test)
- `LOG_LEVEL` : Niveau de logging (debug, info, warning, error)
- `CORS_ALLOWED_ORIGINS` : Origines autorisées pour CORS

## Bonnes Pratiques

1. **Ne jamais commiter** les fichiers `.env.local` ou les secrets
2. **Toujours** utiliser `.env.example` comme template
3. **Valider** les variables d'environnement au démarrage (backend et frontend)
4. **Documenter** toute nouvelle variable ajoutée
5. **Utiliser** le script `sync_env.sh` pour générer les environnements
6. **Exécuter les tests** avec `./scripts/run_tests.sh` pour une validation complète
7. **Utiliser des noms descriptifs** pour les variables (ex: `SOLR_COLLECTION` plutôt que `COLLECTION`)

## Validation des Environnements

### Backend (FastAPI)

Le backend utilise Pydantic pour valider les variables d'environnement :

```python
# Dans app/core/env_validation.py
from app.core.env_validation import validate_environment

# Appelé automatiquement au démarrage dans main.py
config = validate_environment()
```

### Frontend (React)

Le frontend utilise une validation JavaScript dans `src/utils/envValidation.js` :

```javascript
import { validateFrontendEnvironment } from './utils/envValidation';

// Appelé dans src/index.jsx au démarrage
const envConfig = validateFrontendEnvironment();
```

## Gestion des Erreurs

### Backend

Si la validation échoue au démarrage :
- L'application ne démarre pas
- Un message d'erreur détaillé est affiché
- Code de sortie non-zéro pour les systèmes de monitoring

### Frontend

Si la validation échoue :
- Un message d'erreur utilisateur est affiché
- L'erreur est loguée dans la console
- L'application ne se charge pas

## Résolution des Problèmes

### Variables non chargées

- Vérifier que les fichiers `.env` sont correctement référencés dans `docker-compose.yml`
- Vérifier les permissions des fichiers
- Redémarrer les containers après modification

### Conflits de variables

L'ordre de priorité est :
1. Variables définies dans `docker-compose.yml` (section `environment`)
2. Variables dans `.env.{environment}`
3. Variables dans `.env.shared`

## Exemple de Workflow

```bash
# 1. Créer un nouvel environnement
cp .env.example .env.staging

# 2. Modifier les variables spécifiques
nano .env.staging

# 3. Synchroniser
./scripts/sync_env.sh staging

# 4. Démarrer
docker-compose -f docker-compose.staging.yml up
```