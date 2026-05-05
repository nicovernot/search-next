# OpenEdition Search

Application de recherche OpenEdition composée d'un frontend Next.js et d'un backend FastAPI connecté à Solr. Le dépôt contient aussi l'authentification JWT, les recherches sauvegardées, l'i18n, et les specs fonctionnelles du projet.

## Structure

```text
search-next/
├── front/              # Frontend Next.js 16 / React 19 / next-intl
├── search_api_solr/    # API FastAPI / Solr / Redis / PostgreSQL
├── specs/              # Specs fonctionnelles et backlog
├── docs/               # Documentation technique historique
├── scripts/            # Scripts d'automatisation et de vérification
├── docker-compose.yml
└── Makefile
```

## Stack

- Frontend: Next.js 16, React 19, TypeScript, Tailwind CSS 4, Playwright
- Backend: FastAPI, Pydantic v2, SQLAlchemy, Redis, PostgreSQL
- Search: Apache Solr distant
- Infra locale: Docker Compose

## Démarrage rapide

### Avec Docker

```bash
make dev
```

Services exposés par défaut:

- Frontend: `http://localhost:3003`
- API: `http://localhost:8003`
- Swagger: `http://localhost:8003/docs`
- PostgreSQL: `localhost:5435`
- Redis: `localhost:6376`

### Sans Docker

Backend:

```bash
cd search_api_solr
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload --port 8007
```

Frontend:

```bash
cd front
# Créer un .env.local qui pointe sur uvicorn directement (port 8007)
echo "NEXT_PUBLIC_API_URL=http://localhost:8007" > .env.local
corepack enable
pnpm install --frozen-lockfile
pnpm dev
```

### Production Sans Docker

Le déploiement sans Docker est supporté si PostgreSQL, Redis et le reverse proxy sont fournis par l'hôte:

```bash
ENVIRONMENT=production RUN_MIGRATIONS=true ./scripts/install_no_docker.sh
```

Voir [docs/INSTALL_PROD_NO_DOCKER.md](./docs/INSTALL_PROD_NO_DOCKER.md).

### Architecture des ports

| Service | Port hôte | Port interne | Note |
|---|---|---|---|
| API FastAPI | 8003 | 8007 | Docker mappe `8003:8007` |
| Frontend Next.js | 3003 | 3000 | Docker mappe `3003:3000` |
| PostgreSQL | 5435 | 5432 | Docker mappe `5435:5432` |
| Redis | 6376 | 6379 | Docker mappe `6376:6379` |

**Mode Docker** (`make dev`) : `NEXT_PUBLIC_API_URL=http://localhost:8003`
**Mode direct** (uvicorn + npm) : `NEXT_PUBLIC_API_URL=http://localhost:8007`

`front/.env` contient la valeur mode Docker (committée). `front/.env.local` (git-ignoré) contient l'override mode direct.

## Commandes utiles

```bash
make dev           # Démarrage dev complet
make dev-down      # Arrêt des services dev
make test          # Tests backend dans Docker
make test-front    # Tests Playwright headless
make sync-env ENV=test
```

## État fonctionnel

Implémenté côté produit :

- Recherche simple avec facettes et pagination
- Recherche avancée avec constructeur logique
- Autocomplétion
- Authentification email / mot de passe
- Authentification LDAP institutionnelle
- Authentification SSO OIDC avec transport JWT sécurisé par code court à usage unique
- Recherches sauvegardées
- Badges d'accès sur les résultats (permissions)
- Synchronisation état ↔ URL (liens partageables, back/forward)
- i18n `fr`, `en`, `es`, `de`, `it`, `pt`
- UI premium avec thème clair / sombre

## Notes de cohérence

- Ce dépôt a été dérivé d'anciens templates et de docs plus anciennes. Les fichiers de `docs/` peuvent contenir des références historiques à d'anciens ports ou à d'anciennes briques frontend.
- La source de vérité actuelle pour le comportement produit est le code de `front/` et `search_api_solr/`, plus les specs dans `specs/`.

## Specs

- Vue d'ensemble : [specs/README.md](./specs/README.md)
- Exigences techniques : [specs/TECHNICAL_REQUIREMENTS.md](./specs/TECHNICAL_REQUIREMENTS.md)
- Planning global et dette : [specs/PLANNING.md](./specs/PLANNING.md)

| Spec | Titre | État |
|------|-------|------|
| [001](./specs/001-search-core/spec.md) | Recherche core — facettes, pagination, i18n | ✅ Livré |
| [002](./specs/002-advanced-search-suite/spec.md) | Recherche avancée — QB, auth, recherches sauvegardées | ✅ Livré |
| [003](./specs/003-ux-ui-premium-overhaul/spec.md) | UX/UI premium — dark mode, glassmorphism | ✅ Livré |
| [004](./specs/004-url-sync/spec.md) | URL sync — liens partageables, back/forward | ✅ Livré |
| [005](./specs/005-permissions/spec.md) | Permissions — badges d'accès sur les résultats | ✅ Livré |
| [006](./specs/006-tech-debt/spec.md) | Tech debt — fondations techniques | ✅ Livré |
| [007](./specs/007-refactor-search-context/spec.md) | Refactor SearchContext — hooks SOLID | ✅ Livré |
| [008](./specs/008-code-quality-solid/spec.md) | Code quality SOLID | ✅ Livré |
| [009](./specs/009-dry-kiss-yagni/spec.md) | DRY/KISS/YAGNI | ✅ Livré |
| [010](./specs/010-naming-intention-result/spec.md) | Naming intention→résultat | ✅ Livré |
| [011](./specs/011-auth-ldap-sso/spec.md) | Auth LDAP/SSO institutionnel | ✅ Livré |
