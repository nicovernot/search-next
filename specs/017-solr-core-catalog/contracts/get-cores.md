# Contrat: GET /api/v1/cores

Nouvel endpoint public, aligné sur les conventions de `docs/API_V1.md` et `app/api/v1/*.py` existants.

## Requête

```
GET /api/v1/cores
```

Aucun paramètre de requête, aucun corps, aucune authentification requise (même niveau d'accès que `/facets/config`).

## Réponse — 200 OK

```json
{
  "cores": [
    { "name": "documents", "is_default": true },
    { "name": "calenda", "is_default": false }
  ],
  "default_core": "documents"
}
```

Schéma (`SolrCoresResponse`, voir data-model.md) :

| Champ | Type | Contrainte |
|---|---|---|
| `cores[].name` | string | non vide, correspond à une valeur valide du paramètre `core` sur `/search`, `/suggest`, `/permissions` |
| `cores[].is_default` | boolean | exactement une entrée à `true` |
| `default_core` | string | égal au `name` de l'entrée où `is_default = true` |

## Erreurs

Aucun cas d'erreur métier — l'endpoint lit un registre déjà validé au démarrage (échec de démarrage du service si le registre est invalide, pas une erreur runtime de cet endpoint). Erreurs 5xx génériques uniquement en cas de panne infrastructure, non spécifiques à cet endpoint.

## Exemple

```bash
curl "<API_BASE_URL>/api/v1/cores"
```

## Lien avec les endpoints existants

La valeur de `cores[].name` renvoyée ici est directement utilisable comme valeur du paramètre `core` documenté dans `docs/API_V1.md#ciblage-dun-core-solr-core` :

```bash
curl "<API_BASE_URL>/api/v1/suggest?q=hist&core=calenda"
```
