# API v1 — OpenEdition Search

Le contrat public versionné est exposé via `GET /api/v1/openapi.json`.

Endpoints publics Phase 1 :

- `POST /api/v1/search`
- `GET /api/v1/search`
- `GET /api/v1/suggest`
- `GET /api/v1/facets/config`
- `GET /api/v1/permissions`

Les routes racine historiques restent disponibles comme aliases de compatibilité pendant la transition du frontend.

## Exemple recherche

```bash
curl -X POST "http://localhost:8003/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": { "query": "histoire" },
    "filters": [{ "identifier": "platform", "value": "OB" }],
    "pagination": { "from": 0, "size": 10 },
    "facets": [{ "identifier": "platform", "type": "list" }]
  }'
```

## Exemple suggestion

```bash
curl "http://localhost:8003/api/v1/suggest?q=hist"
```

## Exemple permissions

```bash
curl "http://localhost:8003/api/v1/permissions?urls=https://books.openedition.org/pur/30504"
```

`/auth/*` reste réservé au frontend pour la Phase 1. `/api/v1/saved-searches` est disponible pour cohérence de namespace, mais reste protégé par JWT et hors périmètre SDK public initial.
