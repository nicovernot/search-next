# Quickstart: Catalogue des cores Solr et intégration du core « calenda »

## Prérequis

- Backend `search_api_solr` lancé localement (voir `docs/ENVIRONMENTS.md`), `<API_BASE_URL>` par ex. `http://localhost:8003`.
- Aucune migration, aucune nouvelle variable d'environnement.

## Scénario 1 — Lister les cores disponibles (US1)

```bash
curl "<API_BASE_URL>/api/v1/cores"
```

**Attendu** : réponse `200` contenant `documents` (avec `is_default: true`) et, une fois le Scénario 3 appliqué, `calenda` (avec `is_default: false`) ; `default_core` vaut `"documents"`. Voir [contracts/get-cores.md](contracts/get-cores.md) pour le schéma complet.

## Scénario 2 — Ajouter un core par configuration (US2, non-régression de la procédure documentée)

1. Créer `search_api_solr/app/services/solr_cores/test-core.json` :
   ```json
   { "base_url": "https://example.org/solr/test-core", "default": false }
   ```
2. Redémarrer le service backend (le registre se charge une fois au démarrage — `app/api/dependencies.py:16`).
3. Vérifier :
   ```bash
   curl "<API_BASE_URL>/api/v1/cores"
   ```
   `test-core` doit apparaître dans la liste, `default_core` doit rester `"documents"`.
4. Nettoyer : supprimer `test-core.json` et redémarrer — ce fichier ne doit pas être commité, il sert uniquement à valider la procédure.

## Scénario 3 — Enregistrer le core `calenda` (US3)

1. Fichier livré par cette feature : `search_api_solr/app/services/solr_cores/calenda.json` :
   ```json
   { "base_url": "https://solrslave-sec.labocleo.org/solr/calenda", "default": false }
   ```
2. Après redémarrage du service :
   ```bash
   curl "<API_BASE_URL>/api/v1/cores"
   ```
   → `calenda` présent, `is_default: false`, `default_core` toujours `"documents"`.
3. Recherche ciblée sur le nouveau core :
   ```bash
   curl "<API_BASE_URL>/api/v1/suggest?q=janvier&core=calenda"
   ```
   → la requête est envoyée à `https://solrslave-sec.labocleo.org/solr/calenda`, pas à la collection `documents`.
4. Non-régression du comportement par défaut :
   ```bash
   curl "<API_BASE_URL>/api/v1/suggest?q=janvier"
   ```
   → continue de cibler `documents`, comportement inchangé (FR-006/SC-003).

## Validation croisée avec les tests automatisés

Les scénarios ci-dessus sont couverts par (voir tasks.md pour le détail) :
- `search_api_solr/tests/test_solr_core_registry.py` — chargement de `calenda.json` en plus de `documents.json`.
- `search_api_solr/tests/test_cores_endpoint.py` — contrat `GET /api/v1/cores`.
- `search_api_solr/tests/test_regression_default_core.py` — non-régression du core par défaut après ajout de `calenda`.

## Résultat d'exécution (2026-09-03)

Les 3 scénarios ont été rejoués contre le serveur de développement réel (`search-next_api`, hot-reload) :

- **Scénario 1** : `curl <API_BASE_URL>/api/v1/cores` → `{"cores":[{"name":"calenda","is_default":false},{"name":"documents","is_default":true}],"default_core":"documents"}`. Conforme.
- **Scénario 2** : `test-core.json` créé, apparu dans le listage, interrogeable via `/suggest?core=test-core` (200), puis supprimé et disparu du listage après redémarrage. Conforme.
- **Scénario 3** : `calenda.json` livré, `calenda` présent avec `is_default: false`, `/suggest?q=janvier&core=calenda` → `200`, `/suggest?q=janvier` (sans `core`) → `200` et continue de cibler `documents`. Conforme.

Suite pytest complète (`search_api_solr/`) : 134 tests passés.
