# API v1 — OpenEdition Search

**Dernière vérification** : 2026-09-03 — endpoints publics `/api/v1` exposés par `search_api_solr/app/api/v1/` (vérifiés contre `search.py`, `suggest.py`, `facets.py`, `permissions.py`, `cores.py`, `main.py`), y compris le paramètre `core` (feature `016-solr-multi-core-support`) et le catalogue des cores (feature `017-solr-core-catalog`).

Le contrat public versionné est exposé via `GET /api/v1/openapi.json`.

Endpoints publics Phase 1 :

- `POST /api/v1/search`
- `GET /api/v1/search`
- `GET /api/v1/suggest`
- `GET /api/v1/facets/config`
- `GET /api/v1/permissions`
- `GET /api/v1/cores`

Les routes racine historiques restent disponibles comme aliases de compatibilité pendant la transition du frontend.

Les exemples ci-dessous utilisent `<API_BASE_URL>` — la variable documentée dans [`ENVIRONMENTS.md`](./ENVIRONMENTS.md) (ex. `http://localhost:8003` en développement Docker).

## Ciblage d'un core Solr (`core`)

`POST/GET /api/v1/search`, `GET /api/v1/suggest` et `GET /api/v1/permissions` acceptent un paramètre optionnel `core` désignant le core Solr interrogé. Omis, il cible le core par défaut configuré (`documents` aujourd'hui). Un nom de core absent de la configuration renvoie `404 Not Found`. Voir [`ARCHITECTURE.md`](./ARCHITECTURE.md#configuration-solr-multi-core) pour le détail de la configuration.

## Lister les cores disponibles (`GET /api/v1/cores`)

Renvoie les cores actuellement configurés et lequel est le défaut, pour choisir une valeur valide du paramètre `core` sans consulter la configuration serveur :

```bash
curl "<API_BASE_URL>/api/v1/cores"
```

```json
{
  "cores": [
    { "name": "documents", "is_default": true },
    { "name": "calenda", "is_default": false }
  ],
  "default_core": "documents"
}
```

## Exemple recherche

```bash
curl -X POST "<API_BASE_URL>/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": { "query": "histoire" },
    "core": "documents",
    "filters": [{ "identifier": "platform", "value": "OB" }],
    "pagination": { "from": 0, "size": 10 },
    "facets": [{ "identifier": "platform", "type": "list" }]
  }'
```

## Exemple suggestion

```bash
curl "<API_BASE_URL>/api/v1/suggest?q=hist&core=documents"
```

## Exemple permissions

```bash
curl "<API_BASE_URL>/api/v1/permissions?urls=https://example.org/example-document&core=documents"
```

`/auth/*` reste réservé au frontend pour la Phase 1. `/api/v1/saved-searches` est disponible pour cohérence de namespace, mais reste protégé par JWT et hors périmètre SDK public initial.
