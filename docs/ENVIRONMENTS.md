# Gestion des Environnements — OpenEdition Search

**Dernière vérification** : 2026-09-04 — structure `.env.*`, scripts et Docker Compose confirmés contre le dépôt après la simplification de la configuration d'environnement (spec `018-simplify-env-config`).

Ce document est la **référence unique** pour tout ce qui concerne la configuration d'environnement du projet. S'il manque une information ici, c'est un bug de documentation à signaler — ne cherchez pas ailleurs.

## Les 3 environnements

Le projet supporte **exactement 3 environnements**, pilotés par la variable `ENVIRONMENT` : `development`, `test`, `production`. Il n'y a pas de "staging" — cet environnement a été retiré (voir [CHANGELOG.md](./CHANGELOG.md)).

## Structure des fichiers

```text
.
├── .env.development         # Modèle versionné, autonome et complet — environnement dev
├── .env.test                # Modèle versionné, autonome et complet — environnement test
├── .env.production           # Modèle versionné, autonome et complet — environnement prod (secrets en placeholders)
├── .env                       # Fichier ACTIF (non versionné) — copie du modèle activé par scripts/use-env.sh
├── front/.env                 # Symlink -> ../.env (créé par scripts/use-env.sh)
├── search_api_solr/.env       # Symlink -> ../.env (créé par scripts/use-env.sh)
├── scripts/use-env.sh          # Active un environnement (copie + symlinks)
├── scripts/verify_env_docker.sh  # Vérifie que Docker applique bien la config attendue
└── search_api_solr/app/
    ├── settings.py                 # Configuration RÉELLEMENT utilisée par l'application (CORS, DB, Redis, secrets, LDAP, SSO, rate limiting...)
    └── core/env_validation.py      # Validation secondaire au démarrage (ENVIRONMENT valide + détection de secret placeholder en prod)
```

**Chaque fichier `.env.<environnement>` est autonome** : il ne dépend d'aucun autre fichier (l'ancien `.env.shared` a été supprimé, fusionné dans chacun des trois). Un développeur n'a donc jamais besoin d'ouvrir plus d'un fichier à la fois.

## Activation d'un environnement

```bash
scripts/use-env.sh development   # ou: test, production
```

Cette commande :
1. Valide que l'argument est bien `development`, `test` ou `production` (sinon : erreur explicite, rien n'est modifié).
2. Copie `.env.<environnement>` vers `.env` (racine du dépôt, non versionné).
3. Crée/rafraîchit les symlinks `front/.env -> ../.env` et `search_api_solr/.env -> ../.env`.

**Le `Makefile` appelle ce script automatiquement** — vous n'avez normalement jamais besoin de le lancer à la main :

```bash
make dev     # active development, puis docker compose up
make test    # active test, puis lance pytest + Playwright
make prod    # active production, puis docker compose up en mode prod
```

Raccourcis pour activer sans lancer : `make set-dev`, `make set-test`, `make set-prod`.

### Personnalisation propre à votre machine

Besoin d'une valeur différente du modèle versionné (ex: exposer l'API sur votre IP réseau plutôt que `localhost` pour un accès depuis un autre appareil) ? **Éditez `.env` (le fichier actif, non versionné) après activation — jamais `.env.development`/`.env.test`/`.env.production`.** Ces derniers sont les modèles partagés par toute l'équipe ; `.env` est votre copie de travail locale.

## Architecture des ports

| Service | Port hôte | Port interne | Note |
|---|---|---|---|
| API FastAPI | 8003 | 8007 | Docker mappe `8003:8007` |
| Frontend Next.js | 3003 | 3000 | Docker mappe `3003:3000` |
| PostgreSQL | 5435 | 5432 | Docker mappe `5435:5432` |
| Redis | 6376 | 6379 | Docker mappe `6376:6379` |

## Variables d'environnement

Tableau complet, détaillé, avec les valeurs par environnement : [`specs/018-simplify-env-config/contracts/env-schema.md`](../specs/018-simplify-env-config/contracts/env-schema.md). Ci-dessous, les groupes essentiels.

### Sélecteur et CORS

| Variable | Rôle | Format |
|---|---|---|
| `ENVIRONMENT` | Sélectionne le comportement de l'app (`development`/`test`/`production`) | Une des 3 valeurs, sinon le backend refuse de démarrer |
| `CORS_ORIGINS` | Origines navigateur autorisées par le middleware CORS FastAPI (`app/settings.py`, lu par `app/main.py`) | Liste d'URLs séparées par des virgules, sans espace : `http://localhost:3003,http://127.0.0.1:3003` |
| `NEXT_PUBLIC_API_URL` | URL de l'API appelée **depuis le navigateur** (`front/app/lib/api.ts`) | `http://localhost:8003` en dev Docker, `/api` en prod derrière nginx |

⚠️ **Piège Next.js** : `NEXT_PUBLIC_API_URL` (et toute variable `NEXT_PUBLIC_*`) est **inlinée dans le bundle JavaScript au moment du build** en production (`docker-compose.prod.yml` la passe en `build.args`). Changer sa valeur dans `.env` sans relancer `docker compose build` n'a **aucun effet** sur le site déjà construit.

⚠️ **Piège navigateur (Private Network Access)** : si le front est ouvert via une IP réseau (ex: `http://147.94.79.57:3003`) mais que `NEXT_PUBLIC_API_URL` pointe vers `localhost`, Chrome bloque l'appel ("secure context" / "more-private address space"). Faites correspondre l'adresse de l'API à celle utilisée pour ouvrir le front (les deux en `localhost`, ou les deux sur la même IP réseau).

### Solr, Redis, base de données

| Variable | Rôle |
|---|---|
| `SOLR_BASE_URL` | URL Solr distante réellement interrogée par l'API (`app/services/solr_client.py`) |
| `SOLR_URL` | URL Solr "interne" déclarée (usage résiduel à confirmer au besoin — voir `contracts/env-schema.md`) |
| `SOLR_COLLECTION` | Collection Solr ciblée |
| `REDIS_URL` / `REDIS_ENABLED` / `REDIS_TTL_*` | Connexion et TTL du cache |
| `DATABASE_URL` | Connexion PostgreSQL (comptes utilisateurs, recherches sauvegardées) |

### Sécurité — secrets

`SECRET_KEY` / `JWT_SECRET` / `SESSION_SECRET` : en développement et test, une valeur par défaut sûre est appliquée automatiquement si absente. **En production**, `.env.production` contient des placeholders explicites (`change-me-in-production`) — le backend **refuse de démarrer** tant qu'ils n'ont pas été surchargés par de vrais secrets (voir `app/settings.py::validate_production_secrets` et `app/core/env_validation.py::validate_no_placeholder_secret_in_production`).

### LDAP / SSO OIDC

Désactivés par défaut (`LDAP_ENABLED=false`, `SSO_OIDC_ENABLED=false`). Toutes les variables associées existent comme placeholders dans les 3 fichiers modèles — voir `contracts/env-schema.md` pour le détail.

## Deux couches de validation backend

- **`app/settings.py`** : le module **réellement utilisé** par l'application (instancié une fois comme `settings`, consommé par le CORS middleware, le rate limiting, la connexion DB/Redis, etc.). Valide `ENVIRONMENT` (3 valeurs) et bloque le démarrage si un secret de production est resté au placeholder.
- **`app/core/env_validation.py`** : validation **secondaire**, appelée aussi au démarrage (logs de diagnostic), avec les mêmes garde-fous (3 valeurs autorisées, détection de placeholder). Ne pilote pas le comportement de l'app — c'est un filet de sécurité redondant, pas une source de configuration à éditer.

Si vous ajoutez une variable, mettez à jour **`app/settings.py`** (c'est lui qui compte pour le comportement réel), puis les 3 fichiers `.env.*`, puis ce document.

## Vérifier que Docker applique bien la configuration attendue

```bash
make env-verify
# ou directement :
scripts/verify_env_docker.sh [development|test|production]
```

Compare, pour chaque conteneur (`api`, `frontend`), la valeur de `ENVIRONMENT`, `CORS_ORIGINS`, `NEXT_PUBLIC_API_URL`, `SOLR_URL`, `SOLR_BASE_URL`, `SOLR_COLLECTION` réellement appliquée (`docker exec <service> printenv`) à celle du `.env` actif. Sort en erreur au premier écart, avec le détail. **Utilisez cette commande avant de conclure à un bug applicatif** si le front ou l'API se comportent de façon inattendue après un changement de configuration — c'est exactement le réflexe qui aurait raccourci le diagnostic de l'incident ayant motivé cette page.

En production, un avertissement rappelle que la vérification runtime ne garantit pas qu'un `NEXT_PUBLIC_*` a bien été pris en compte au build (voir piège Next.js ci-dessus).

## Tests

```bash
make test          # backend, dans le container
make test-front    # frontend E2E Playwright
make test-all       # les deux
```

Ces cibles activent automatiquement `.env.test` avant de lancer les tests.

## Production sans Docker

Voir [INSTALL_PROD_NO_DOCKER.md](./INSTALL_PROD_NO_DOCKER.md) — le script `scripts/install_no_docker.sh` réutilise `scripts/use-env.sh production` puis ajoute les overrides propres à un hôte sans Docker (adresses `127.0.0.1` plutôt que noms de service Docker).

## Résolution de problèmes

### "Failed to fetch" / API injoignable depuis le navigateur

1. `make env-verify` — confirme que le conteneur a bien la configuration attendue.
2. Vérifiez qu'aucune variable de shell (`CORS_ORIGINS`, `NEXT_PUBLIC_API_URL`, etc.) n'est exportée dans votre terminal et ne prend le pas silencieusement sur `.env` : `env | grep -E "CORS_ORIGINS|NEXT_PUBLIC_API_URL"`. Si oui : `unset CORS_ORIGINS NEXT_PUBLIC_API_URL` puis relancez les conteneurs.
3. Vérifiez la cohérence entre l'URL utilisée pour ouvrir le front et `NEXT_PUBLIC_API_URL` (piège Private Network Access ci-dessus).
4. Après toute modification de `.env`, recréez les conteneurs concernés : `docker compose up -d --force-recreate --no-deps api frontend`.

### Le backend refuse de démarrer avec une erreur sur `ENVIRONMENT`

La valeur active n'est pas `development`, `test` ou `production` (par exemple une variable de shell résiduelle valant `staging`). Relancez `scripts/use-env.sh <environment>` puis vérifiez `cat .env | grep ENVIRONMENT`.

### Le backend refuse de démarrer en production avec une erreur sur un secret

Un des secrets (`SECRET_KEY`/`JWT_SECRET`/`SESSION_SECRET`) est resté à sa valeur placeholder (`change-me-in-production`). Surchargez-le avec une vraie valeur (variable d'environnement système ou gestionnaire de secrets), jamais dans `.env.production` versionné.

### Conflits de variables — ordre de priorité

1. Variable déjà exportée dans le shell / injectée par la CI (prioritaire sur tout le reste — source d'erreurs silencieuses si oubliée, cf. point 2 ci-dessus).
2. `.env` (racine, activé par `scripts/use-env.sh`) — lu directement par Docker Compose (`env_file:`) et par `front/`/`search_api_solr/` via leurs symlinks.
3. Valeurs par défaut codées dans `app/settings.py` (si la variable est absente de `.env`).
