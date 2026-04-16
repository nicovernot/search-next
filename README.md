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
echo "NEXT_PUBLIC_API_URL=http://localhost:8003" > .env
npm install
npm run dev
```

Le fichier `front/.env` est généré automatiquement par `make dev` / `make sync-env`. En démarrage manuel, il faut le créer. Le frontend s'attend à une API sur `NEXT_PUBLIC_API_URL`, avec repli local sur `http://localhost:8003`.

## Commandes utiles

```bash
make dev           # Démarrage dev complet
make dev-down      # Arrêt des services dev
make test          # Tests backend dans Docker
make test-front    # Tests Playwright headless
make sync-env ENV=test
```

## État fonctionnel

Implémenté côté produit:

- Recherche simple avec facettes et pagination
- Recherche avancée avec constructeur logique
- Autocomplétion
- Authentification email / mot de passe
- Recherches sauvegardées
- i18n `fr`, `en`, `es`, `de`, `it`, `pt`
- UI premium avec thème clair / sombre

Backlog encore ouvert:

- `004-url-sync`: synchronisation état de recherche <-> URL
- `005-permissions`: badges d'accès sur les résultats

## Notes de cohérence

- Ce dépôt a été dérivé d'anciens templates et de docs plus anciennes. Les fichiers de `docs/` peuvent contenir des références historiques à d'anciens ports ou à d'anciennes briques frontend.
- La source de vérité actuelle pour le comportement produit est le code de `front/` et `search_api_solr/`, plus les specs dans `specs/`.

## Specs

- Vue d'ensemble: [specs/README.md](./specs/README.md)
- Exigences techniques: [specs/TECHNICAL_REQUIREMENTS.md](./specs/TECHNICAL_REQUIREMENTS.md)
- Planning global: [specs/PLANNING.md](./specs/PLANNING.md)
- Recherche coeur: [specs/001-search-core/spec.md](./specs/001-search-core/spec.md)
- Recherche avancée: [specs/002-advanced-search-suite/spec.md](./specs/002-advanced-search-suite/spec.md)
- Refonte UI: [specs/003-ux-ui-premium-overhaul/spec.md](./specs/003-ux-ui-premium-overhaul/spec.md)
- Backlog URL sync: [specs/004-url-sync/spec.md](./specs/004-url-sync/spec.md)
- Backlog permissions: [specs/005-permissions/spec.md](./specs/005-permissions/spec.md)
