# Gestion des Environnements — OpenEdition Search

## Structure des fichiers d'environnement

Le projet utilise une approche centralisée avec héritage :

```
.
├── .env.shared              # Variables communes à tous les environnements
├── .env.development         # Surcharge développement
├── .env.production          # Surcharge production
├── .env.staging             # Surcharge staging
├── .env.test                # Surcharge tests
├── scripts/sync_env.sh      # Génère {service}/.env.local à partir de shared + env cible
├── scripts/run_tests.sh     # Lint + tests E2E
└── search_api_solr/app/core/env_validation.py  # Validation Pydantic au démarrage backend
```

> `front/src/utils/envValidation.js` a été supprimé — Next.js n'a pas de validation
> d'environnement côté client dans ce projet. La validation se fait uniquement backend.

## Hiérarchie de chargement

1. **`.env.shared`** — valeurs communes (chargé en premier)
2. **`.env.{environment}`** — surcharges spécifiques (development / production / staging / test)
3. **`search_api_solr/.env.local`** — généré par `sync_env.sh`, git-ignoré, ne pas éditer
4. **`front/.env`** — valeur committée (`NEXT_PUBLIC_API_URL=http://localhost:8003`, mode Docker)
5. **`front/.env.local`** — généré par `sync_env.sh` ou créé manuellement, git-ignoré

## Architecture des ports

| Service | Port hôte | Port interne | Note |
|---|---|---|---|
| API FastAPI | 8003 | 8007 | Docker mappe `8003:8007` |
| Frontend Next.js | 3003 | 3000 | Docker mappe `3003:3000` |
| PostgreSQL | 5435 | 5432 | Docker mappe `5435:5432` |
| Redis | 6376 | 6379 | Docker mappe `6376:6379` |

**Mode Docker** (`make dev`) : `NEXT_PUBLIC_API_URL=http://localhost:8003`  
**Mode direct** (uvicorn + pnpm sans Docker) : `NEXT_PUBLIC_API_URL=http://localhost:8007`

`front/.env` contient la valeur mode Docker (committée). `front/.env.local` (git-ignoré) contient l'override pour le mode direct.

## Utilisation

### Développement Docker

```bash
./scripts/sync_env.sh development
docker compose up
```

### Développement sans Docker

```bash
cd front
echo "NEXT_PUBLIC_API_URL=http://localhost:8007" > .env.local
corepack enable && pnpm install --frozen-lockfile
pnpm dev
```

### Tests

```bash
./scripts/sync_env.sh test
./scripts/run_tests.sh
```

### Staging

```bash
./scripts/sync_env.sh staging
docker compose -f docker-compose.yml -f docker-compose.staging.yml up --build
```

### Production

```bash
./scripts/sync_env.sh production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build
```

### Production sans Docker

```bash
ENVIRONMENT=production RUN_MIGRATIONS=true ./scripts/install_no_docker.sh
```

Voir [INSTALL_PROD_NO_DOCKER.md](./INSTALL_PROD_NO_DOCKER.md) pour le détail.

## Variables d'environnement

### Frontend (Next.js)

Les variables exposées côté navigateur **doivent** être préfixées `NEXT_PUBLIC_` :

| Variable | Description | Exemple |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | URL publique de l'API backend | `http://localhost:8003` (Docker) / `/api` (prod) |

> `REACT_APP_API_URL` est obsolète (Create React App) — non lue par Next.js.

### Backend (FastAPI)

| Variable | Description |
|---|---|
| `SOLR_BASE_URL` | URL du cluster Solr distant |
| `SOLR_URL` | URL Solr interne (Docker) |
| `SOLR_COLLECTION` | Collection Solr |
| `API_HOST` / `API_PORT` | Bind de l'API (interne : 8007) |
| `DEBUG` / `AUTO_RELOAD` | Mode debug et rechargement |
| `SECRET_KEY` / `JWT_SECRET` | Secret JWT (requis si `DISABLE_AUTH=false`) |
| `DATABASE_URL` | Connexion PostgreSQL |
| `REDIS_URL` | Connexion Redis |

### Variables communes

| Variable | Description |
|---|---|
| `ENVIRONMENT` | `development` / `staging` / `production` / `test` |
| `NODE_ENV` | Passé à Next.js (`development` / `production` / `test`) |
| `CORS_ORIGINS` | Origines CORS autorisées, séparées par des virgules |
| `LOG_LEVEL` | `debug` / `info` / `warning` / `error` |
| `API_BASE_URL` | URL base de l'API (lue par `sync_env.sh` pour générer `front/.env.local`) |
| `FRONTEND_URL` | URL publique du frontend |

> **Nom officiel** : `CORS_ORIGINS` (anciennement `CORS_ALLOWED_ORIGINS`, renommé en avril 2026).  
> Le backend (`settings.py`) lit `CORS_ORIGINS` via `os.getenv("CORS_ORIGINS")`.

## Validation des environnements

### Backend

```python
# app/core/env_validation.py — appelé automatiquement dans main.py
from app.core.env_validation import validate_environment
config = validate_environment()
```

Pydantic-settings valide au démarrage : URLs Solr, niveau de log, secrets JWT.  
Si la validation échoue, l'application **ne démarre pas** (code de sortie non-zéro).

### Docker — entrypoint

Le `Dockerfile` utilise `entrypoint.sh` qui, avant de lancer uvicorn :
1. Attend que PostgreSQL soit prêt (`pg_isready`)
2. Applique les migrations Alembic (`alembic upgrade head`)

## Ordre de priorité des variables

1. Section `environment:` de `docker-compose.yml` / `docker-compose.*.yml`
2. `.env.{environment}` (surcharges spécifiques)
3. `.env.shared` (valeurs communes)

## Bonnes pratiques

1. Ne jamais commiter les fichiers `*.env.local` ni les secrets
2. Toujours définir `ENVIRONMENT` et `NODE_ENV` dans chaque `.env.{env}`
3. Utiliser `NEXT_PUBLIC_API_URL` (pas `REACT_APP_*`) pour les variables frontend
4. Toute nouvelle variable doit être ajoutée dans `.env.shared` avec une valeur par défaut safe, puis surchargée si nécessaire
5. Exécuter `./scripts/check_env_setup.sh` après tout changement de configuration Docker/env

## Résolution des problèmes

### Variables non chargées

- Vérifier que `docker-compose.yml` référence `.env.shared` dans `env_file:`
- Redémarrer les containers après modification : `docker compose down && docker compose up`

### CORS bloqué

- Vérifier que l'origine du navigateur est dans `CORS_ORIGINS` de `search_api_solr/.env.local`
- En développement : `http://localhost:3003`, `http://127.0.0.1:3003` et `http://0.0.0.0:3003` doivent être présents si ces URLs peuvent être utilisées dans le navigateur
- Après modification d'une variable CORS Docker, recréer le conteneur API pour relire l'environnement : `docker compose up -d --force-recreate --no-deps api`

### Conflits de variables

L'ordre de priorité (du plus fort au plus faible) :
1. Variables dans `environment:` du docker-compose
2. `.env.{environment}`
3. `.env.shared`
