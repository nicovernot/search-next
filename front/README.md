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

Via Docker (`make dev`, `make prod`), le fichier `front/.env` est généré automatiquement par `scripts/sync_env.sh`.

Pour un démarrage manuel sans Docker, créer `front/.env.local` manuellement :

```bash
echo "NEXT_PUBLIC_API_URL=http://localhost:8007" > .env.local
```

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
