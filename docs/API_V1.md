# API v1 — OpenEdition Search

**Dernière vérification** : 2026-09-03 — endpoints publics `/api/v1` exposés par `search_api_solr/app/api/v1/` (vérifiés contre `search.py`, `suggest.py`, `facets.py`, `permissions.py`, `main.py`).

Le contrat public versionné est exposé via `GET /api/v1/openapi.json`.

Endpoints publics Phase 1 :

- `POST /api/v1/search`
- `GET /api/v1/search`
- `GET /api/v1/suggest`
- `GET /api/v1/facets/config`
- `GET /api/v1/permissions`

Les routes racine historiques restent disponibles comme aliases de compatibilité pendant la transition du frontend.

Les exemples ci-dessous utilisent `<API_BASE_URL>` — la variable documentée dans [`ENVIRONMENTS.md`](./ENVIRONMENTS.md) (ex. `http://localhost:8003` en développement Docker).

## Exemple recherche

```bash
curl -X POST "<API_BASE_URL>/api/v1/search" \
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
curl "<API_BASE_URL>/api/v1/suggest?q=hist"
```

## Exemple permissions

```bash
curl "<API_BASE_URL>/api/v1/permissions?urls=https://example.org/example-document"
```

`/auth/*` reste réservé au frontend pour la Phase 1. `/api/v1/saved-searches` est disponible pour cohérence de namespace, mais reste protégé par JWT et hors périmètre SDK public initial.
