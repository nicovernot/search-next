# Contrat — Paramètre `core` sur les endpoints publics `/api/v1`

Extension additive (rétrocompatible) des endpoints existants documentés dans [`docs/API_V1.md`](../../../docs/API_V1.md). Aucun champ existant n'est renommé ni supprimé.

## `POST /api/v1/search`

`SearchRequest` gagne un champ optionnel :

```json
{
  "query": { "query": "histoire" },
  "core": "documents",
  "filters": [],
  "pagination": { "from": 0, "size": 10 },
  "facets": []
}
```

- `core` (string, optionnel) — nom d'un core présent dans le registre. Absent ou `null` → core par défaut (identique au comportement actuel).

## `GET /api/v1/search`

Paramètre de requête optionnel `core` (string), même sémantique que ci-dessus.

## `GET /api/v1/suggest`

Paramètre de requête optionnel `core` (string), même sémantique.

```
GET /api/v1/suggest?q=hist&core=documents
```

## `GET /api/v1/permissions`

Paramètre de requête optionnel `core` (string), même sémantique.

```
GET /api/v1/permissions?urls=<...>&core=documents
```

## `GET /api/v1/facets/config`

**Non modifié.** Aucun paramètre `core` — cet endpoint ne dépend d'aucun core (voir `research.md` Décision 4).

## Nouvelle réponse d'erreur : core inconnu

Quand `core` référence un nom absent du registre, sur `/search`, `/suggest` et `/permissions` — ce cas est traité comme une exception au comportement de dégradation gracieuse existant sur `/suggest` et `/permissions` (voir `research.md` Décision 3bis) :

```http
HTTP/1.1 404 Not Found
Content-Type: application/json

{ "detail": "Unknown Solr core: '<core>'" }
```

> Toute autre erreur Solr (ex. core injoignable) continue de suivre le comportement existant de chaque endpoint : `/search` renvoie `503`, `/suggest` et `/permissions` dégradent gracieusement (liste vide / `info.error` en 200) — comportement préexistant, non modifié par cette feature.

Distinct du cas existant « Solr injoignable » (`503 Search service unavailable` sur `/search`, inchangé) — voir `data-model.md` § SolrCoreNotFoundError.

## Compatibilité ascendante

| Appelant | Comportement |
|---|---|
| N'envoie pas `core` | Identique au comportement actuel (core par défaut = ancien core unique `documents`) — FR-005/SC-002 |
| Envoie `core` = nom valide | Résultats exclusivement issus de ce core — FR-003/SC-003 |
| Envoie `core` = nom absent du registre | `404` explicite, jamais de repli silencieux — FR-004/SC-004 |

`GET /api/v1/openapi.json` reflète automatiquement le nouveau champ/paramètre une fois `SearchRequest` et les signatures d'endpoint mis à jour (FastAPI génère le schéma depuis les types Pydantic et les `Query()`).
