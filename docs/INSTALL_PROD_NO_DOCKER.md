# Installation Production Sans Docker

Ce mode installe l'application directement sur l'hôte. PostgreSQL, Redis et le reverse proxy doivent être fournis par le système ou par des services managés.

## Prérequis

- Python 3.10+ avec `venv`, ou `uv`
- Node.js 20+ avec Corepack
- PostgreSQL accessible depuis l'hôte
- Redis accessible depuis l'hôte
- Un reverse proxy, par exemple nginx ou Apache

Sur Debian/Ubuntu, installer au minimum:

```bash
sudo apt install python3 python3-venv nodejs postgresql-client
corepack enable
```

## Variables Requises

En production, définir au moins:

```bash
export ENVIRONMENT=production
export SECRET_KEY="une-valeur-longue-et-secrete"
export DATABASE_URL="postgresql://search_user:search_password@127.0.0.1:5432/search_db"
export REDIS_URL="redis://127.0.0.1:6379/0"
export NEXT_PUBLIC_API_URL="/api"
export INTERNAL_API_URL="http://127.0.0.1:8007"
```

`NEXT_PUBLIC_API_URL=/api` suppose que le frontend et l'API sont servis par le même domaine via reverse proxy.

## Installation

Depuis la racine du dépôt:

```bash
ENVIRONMENT=production RUN_MIGRATIONS=true ./scripts/install_no_docker.sh
```

Le script:

- génère `search_api_solr/.env.local`
- génère `front/.env.local`
- installe les dépendances backend
- applique les migrations si `RUN_MIGRATIONS=true`
- installe les dépendances frontend avec pnpm
- construit le frontend Next.js

## Démarrage

Backend:

```bash
cd search_api_solr
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8007 --workers 4
```

Frontend:

```bash
cd front
HOSTNAME=127.0.0.1 PORT=3000 node .next/standalone/server.js
```

Reverse proxy:

- `/api/` vers `http://127.0.0.1:8007/`
- `/` vers `http://127.0.0.1:3000/`

## Notes

- Si l'hôte utilise Python 3.12, ne pas installer `aioredis`; le projet utilise `redis.asyncio`.
- Si pnpm ne peut pas écrire dans `$HOME`, définir un store local:

```bash
export PNPM_STORE_DIR=/opt/search-next/.pnpm-store
```

- Si un ancien lancement Docker a créé un dossier `front/.next` avec de mauvaises permissions, le script le nettoie avant le build.
