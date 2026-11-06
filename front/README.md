# Frontend OpenEdition Search

Frontend Next.js du projet OpenEdition Search.

## Stack

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS 4
- next-intl
- Playwright

## Démarrage

```bash
corepack enable
pnpm install --frozen-lockfile
pnpm dev
```

Le frontend écoute sur `http://localhost:3000` en local simple, et sur `http://localhost:3003` quand il est lancé via Docker Compose.

## Variables d'environnement

```env
NEXT_PUBLIC_API_URL=http://localhost:8003
```

Via Docker (`make dev`, `make prod`) ou en dehors, `front/.env` est un symlink vers le `.env` racine activé par `scripts/use-env.sh <development|test|production>` (voir [docs/ENVIRONMENTS.md](../docs/ENVIRONMENTS.md)) — un seul fichier à éditer, jamais `front/.env` directement.

Pour un démarrage manuel sans Docker avec une URL d'API différente (ex: uvicorn direct sur le port 8007), éditez directement le `.env` actif à la racine du dépôt après activation, plutôt que `front/.env` (qui n'est qu'un symlink).

## Scripts

```bash
pnpm dev
pnpm build
pnpm start
pnpm lint
pnpm test:e2e
```

## Fonctionnalités UI

- Recherche simple
- Recherche avancée
- Facettes et pagination
- Authentification
- Recherches sauvegardées
- i18n
- Thème clair / sombre

## Tests

Les tests E2E vivent dans `front/tests` et utilisent Playwright.
