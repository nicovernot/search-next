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
npm install
npm run dev
```

Le frontend écoute sur `http://localhost:3000` en local simple, et sur `http://localhost:3003` quand il est lancé via Docker Compose.

## Variables d'environnement

```env
NEXT_PUBLIC_API_URL=http://localhost:8003
```

## Scripts

```bash
npm run dev
npm run build
npm run start
npm run lint
npm run test:e2e
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
