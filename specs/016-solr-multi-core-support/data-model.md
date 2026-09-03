# Modèle de données — Configuration Solr multi-core

## SolrCoreDefinition

Une entrée de configuration pour un core Solr interrogeable (correspond à l'entité spec « Core Solr »).

| Champ | Description | Règle |
|---|---|---|
| `name` | Identifiant logique du core | Dérivé du nom de fichier (`<name>.json`) ; unique par construction du système de fichiers |
| `base_url` | Cible de connexion Solr pour ce core | Requis, non vide (FR-007) |
| `is_default` | Ce core est-il le core par défaut ? | Champ JSON `default` (bool, absent = `false`) ; exactement une `SolrCoreDefinition` du registre DOIT avoir `is_default = true` (FR-007) |

## SolrCoreRegistry

L'ensemble résolu, chargé une fois au démarrage, des `SolrCoreDefinition` actuellement configurées (correspond à l'entité spec « Registre des cores actifs »).

| Propriété/Méthode | Description | Règle |
|---|---|---|
| `cores` | Dict `name → SolrCoreDefinition` | Chargé depuis `app/services/solr_cores/*.json` au démarrage |
| `default_core_name` | Nom du core par défaut | Dérivé de la `SolrCoreDefinition` avec `is_default = true` |
| `resolve(core: str \| None) -> SolrCoreDefinition` | Résout un nom de core explicite, ou retourne le core par défaut si `core` est `None` | Lève `SolrCoreNotFoundError` si `core` est fourni mais absent de `cores` (FR-004) |
| *(validation au chargement)* | — | Échoue au démarrage si `cores` est vide, ou si le nombre de `SolrCoreDefinition` avec `is_default = true` est différent de 1 (FR-007) |

## SearchRequest (extension)

Le modèle Pydantic existant (`app/models/search_models.py::SearchRequest`) gagne un champ.

| Champ ajouté | Type | Description |
|---|---|---|
| `core` | `str \| None` | Nom du core ciblé pour cette recherche ; `None` = core par défaut du registre (FR-003) |

`/suggest` et `/permissions` (endpoints sans corps JSON) reçoivent l'équivalent sous forme de paramètre de requête `core: str | None`, porté par le même contrat sémantique.

## SolrCoreNotFoundError (extension des exceptions existantes)

Ajoutée à `app/core/exceptions.py`, aux côtés de `SolrTimeoutError`, `SolrInvalidQueryError`, `SolrUnavailableError` déjà présentes.

| Champ/Comportement | Description |
|---|---|
| Levée par | `SolrCoreRegistry.resolve()` quand le nom de core demandé n'existe pas dans la configuration |
| Mappée vers | HTTP 404, dans la même chaîne `isinstance` que les exceptions Solr existantes de chaque endpoint concerné |
| Distincte de | `SolrUnavailableError` (HTTP 503) — core connu de la configuration mais Solr distant injoignable (FR-010) |

## Relationships

- Un `SolrCoreRegistry` possède une ou plusieurs `SolrCoreDefinition`, dont exactement une est le core par défaut.
- Une `SearchRequest` (ou l'équivalent paramètre `core` pour `/suggest`/`/permissions`) référence au plus un nom de core ; sa résolution passe toujours par `SolrCoreRegistry.resolve()`.
- `SearchBuilder`, `SuggestService` et `PermissionsService` détiennent chacun une référence au même `SolrCoreRegistry` (injecté une fois, partagé) — aucun de ces trois services ne construit sa propre résolution de core indépendante (FR-006).
