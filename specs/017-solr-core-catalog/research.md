# Phase 0 Research: Catalogue des cores Solr et intégration du core « calenda »

## Décision 1 — Où exposer la liste des cores

**Decision**: Nouvel endpoint public `GET /api/v1/cores`, sans paramètre, non protégé (même niveau d'accès que `/search`, `/suggest`, `/permissions`, `/facets/config`).

**Rationale**: `SolrCoreRegistry` (`search_api_solr/app/services/solr_core_registry.py:88-94`) expose déjà `cores` (dict nom → `SolrCoreDefinition`) et `default_core_name` en mémoire, chargés une fois au démarrage. Aucun nouvel état à construire — l'endpoint est une simple projection en lecture de ce registre, cohérent avec `/facets/config` qui expose déjà une configuration statique sans toucher Solr.

**Alternatives considered**:
- Ajouter la liste des cores dans la réponse de `/facets/config` : rejeté — `/facets/config` documente une configuration de facettes sans lien avec les cores (research.md de la feature 016, Décision 4, avait déjà exclu ce couplage) ; mélanger les deux romprait la lisibilité du contrat existant.
- Exposer un header `X-Available-Cores` sur chaque réponse : rejeté — invisible dans Swagger/OpenAPI, moins découvrable qu'un endpoint dédié, et redondant sur chaque appel.

## Décision 2 — Forme de la réponse

**Decision**: `{"cores": [{"name": str, "is_default": bool}, ...], "default_core": str}`. Pas d'exposition de `base_url` dans la réponse publique.

**Rationale**: FR-001/FR-002 exigent le nom de chaque core et lequel est le défaut — rien de plus. `base_url` est une adresse d'infrastructure interne (déjà traitée comme telle par la feature 016, jamais renvoyée au client) ; l'exposer élargirait la surface d'information sans bénéfice pour l'appelant, qui n'a besoin que d'une valeur valide pour le paramètre `core`. Le champ `default_core` en plus du booléen par entrée facilite un accès direct côté client sans reparcourir la liste.

**Alternatives considered**:
- Renvoyer uniquement `["documents", "calenda"]` (liste de noms) sans marquer le défaut : rejeté — ne satisfait pas FR-002 (l'appelant doit reconstituer l'info par un second appel ou une supposition).
- Renvoyer aussi `base_url` : rejeté (voir Rationale).

## Décision 3 — Ajout du core `calenda`

**Decision**: Nouveau fichier `search_api_solr/app/services/solr_cores/calenda.json` = `{"base_url": "https://solrslave-sec.labocleo.org/solr/calenda", "default": false}`, au même niveau que `documents.json` existant.

**Rationale**: C'est exactement le mécanisme déjà validé par la feature 016 (`_load_core_definitions`, `solr_core_registry.py:30-52`) — un fichier de plus dans le répertoire suffit, aucun changement de code. `default: false` préserve FR-006 (le comportement par défaut ne doit pas changer).

**Alternatives considered**: Aucune — c'est l'application directe de la procédure que la feature documente elle-même (US2).

## Décision 4 — Documentation d'intégration d'un core

**Decision**: Étendre `docs/ARCHITECTURE.md` (section « Configuration Solr multi-core », déjà présente depuis la feature 016) avec un exemple pas-à-pas complet (fichier JSON, redémarrage, vérification via `GET /api/v1/cores`), plutôt que créer un nouveau document séparé.

**Rationale**: La section existe déjà et documente le mécanisme général ; y ajouter la procédure évite une deuxième source de vérité sur le même sujet. `docs/API_V1.md` reçoit uniquement l'entrée de contrat pour le nouvel endpoint (cohérent avec son rôle de référence de contrat public, pas de tutoriel).

**Alternatives considered**: Nouveau fichier `docs/SOLR_CORES_GUIDE.md` dédié — rejeté, fragmenterait une documentation déjà centralisée sur un sujet encore de taille modeste (une section suffit).

## Résumé des inconnues résolues

Aucun `NEEDS CLARIFICATION` restant dans le Technical Context (voir plan.md) : stack, tests et structure sont hérités tels quels de la feature 016, aucune nouvelle dépendance.
