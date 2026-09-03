# Phase 1 Data Model: Catalogue des cores Solr et intégration du core « calenda »

Aucune nouvelle entité persistée. Cette feature ajoute une vue en lecture sur une entité déjà introduite par la feature 016, plus une instance de configuration.

## Entité existante (rappel, non modifiée)

### SolrCoreDefinition (`app/services/solr_core_registry.py:22-27`)

| Champ | Type | Description |
|---|---|---|
| `name` | `str` | Identifiant du core, utilisé comme valeur du paramètre `core` |
| `base_url` | `str` | Adresse Solr du core — information d'infrastructure interne, jamais exposée par l'API |
| `is_default` | `bool` | `true` pour exactement un core du registre |

Chargée depuis `app/services/solr_cores/<name>.json`. Cette feature ajoute une nouvelle instance : `calenda.json` (voir research.md Décision 3).

## Nouveaux modèles de réponse (contrat API)

### SolrCoreInfo

| Champ | Type | Description |
|---|---|---|
| `name` | `str` | Nom du core, valeur valide pour le paramètre `core` des endpoints existants |
| `is_default` | `bool` | `true` si ce core est utilisé quand `core` est omis |

Projection publique de `SolrCoreDefinition`, sans `base_url`.

### SolrCoresResponse

| Champ | Type | Description |
|---|---|---|
| `cores` | `list[SolrCoreInfo]` | Tous les cores actuellement configurés |
| `default_core` | `str` | Nom du core par défaut (redondant avec `is_default` par entrée, exposé aussi au niveau racine pour un accès direct) |

**Validation/Invariants** (hérités du registre, non recréés) :
- `cores` contient au moins un élément (le registre refuse de démarrer sinon — `solr_core_registry.py:76-80`).
- Exactement un élément de `cores` a `is_default = true`, et `default_core` correspond à son `name` (le registre refuse de démarrer sinon — `solr_core_registry.py:82-86`).

Aucune transition d'état : la liste est recalculée à chaque appel à partir du registre en mémoire (pas de cache supplémentaire à invalider).
