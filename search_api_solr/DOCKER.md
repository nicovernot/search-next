# OpenEdition Search - Guide Docker

## Architecture

4 services Docker (pas de Solr local — Solr est distant) :

```
┌──────────────┐     ┌──────────────┐
│  Frontend    │     │     API      │
│  Next.js 16  │────▶│   FastAPI    │
│  :3003       │     │  :8003/:8007 │
└──────────────┘     └──────┬───────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
        ┌──────────┐  ┌──────────┐  ┌─────────────────────────┐
        │PostgreSQL│  │  Redis   │  │ Solr distant             │
        │  :5435   │  │  :6376   │  │ solrslave-sec.labocleo.org│
        └──────────┘  └──────────┘  └─────────────────────────┘
```

Ports exposés sur l'hôte (défauts Makefile) :

| Service    | Hôte  | Conteneur |
|------------|-------|-----------|
| Frontend   | 3003  | 3000      |
| API        | 8003  | 8007      |
| PostgreSQL | 5435  | 5432      |
| Redis      | 6376  | 6379      |

## Démarrage rapide

```bash
# Développement (avec hot-reload)
make dev

# Production
make prod
```

Ces commandes appellent `make sync-env` en premier, ce qui génère automatiquement `front/.env` et `front/.env.local`.

### Sans Make

```bash
# Développement
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Commandes disponibles

```bash
# Environnements
make dev              # Lancer en développement
make dev-build        # Build + lancer en dev
make dev-down         # Arrêter le dev
make prod             # Lancer en production
make prod-build       # Build + lancer en prod
make prod-down        # Arrêter la prod

# Logs
make logs             # Tous les logs
make logs-api         # Logs de l'API
make logs-frontend    # Logs du frontend

# Shell
make shell-api        # Shell dans le conteneur API
make shell-frontend   # Shell dans le conteneur frontend

# Monitoring
make health           # Vérifier la santé des services
make ps               # Liste des conteneurs
make stats            # Statistiques ressources

# Nettoyage
make clean            # Conteneurs + volumes
make clean-all        # Conteneurs + volumes + images
```

## Configuration

### Environnements

Les variables d'environnement sont gérées de façon centralisée depuis la racine du projet :

```bash
make sync-env ENV=development   # ou staging / production / test
```

Cela génère `front/.env`, `front/.env.local` et `search_api_solr/.env.local`.

### Variables frontend clés

```env
NEXT_PUBLIC_API_URL=http://localhost:8003
```

### Variables backend clés

```env
SOLR_BASE_URL=https://solrslave-sec.labocleo.org/solr/documents
API_PORT=8007
DEV=true
LOG_LEVEL=DEBUG
```

## Accès aux services

### Développement

- Frontend : http://localhost:3003
- API : http://localhost:8003
- Swagger UI : http://localhost:8003/docs

### Production

- Frontend : http://localhost (port 80)
- API : http://localhost/api

## Réseau

Tous les services communiquent via le réseau `search-next_network`.

## Volumes persistants

```
postgres_data   — données PostgreSQL
redis_data      — données Redis
```

Les données Solr sont distantes — aucun volume local pour Solr.

## Débogage

```bash
# Logs en temps réel
docker compose logs -f api
docker compose logs -f frontend

# Shell dans un conteneur
make shell-api

# Vérifier la santé
make health

# Tester l'API directement
curl http://localhost:8003/docs
```

## Résolution de problèmes

### Le frontend ne peut pas contacter l'API

Vérifier que `front/.env` contient `NEXT_PUBLIC_API_URL=http://localhost:8003`.
Ce fichier est généré par `make sync-env` / `make dev`. En cas d'absence, relancer `make dev`.

### L'API retourne une erreur 503

Vérifier la connectivité vers le Solr distant :

```bash
curl https://solrslave-sec.labocleo.org/solr/documents/admin/ping
```

### Port déjà utilisé

```bash
# Voir quel processus utilise le port
lsof -i :3003
lsof -i :8003
```

## Production HTTPS

Pour activer HTTPS, décommenter dans `docker-compose.prod.yml` :

```yaml
# volumes:
#   - ./certs:/etc/nginx/certs:ro
```

Et fournir les certificats dans `./certs/`.
