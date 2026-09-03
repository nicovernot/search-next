# Quickstart — Valider le support multi-core Solr

## Prérequis

- Backend `search_api_solr` démarré (`make dev` ou équivalent).
- `curl`, `jq` (optionnel), `pytest` disponibles.

## 1. Vérifier la migration du core existant

```bash
cat search_api_solr/app/services/solr_cores/documents.json
```

Résultat attendu : `{"base_url": "https://solrslave-sec.labocleo.org/solr/documents", "default": true}` — la même URL que l'ancien `settings.solr_base_url` (FR-005).

## 2. Ajouter un second core sans toucher au code

```bash
cat > search_api_solr/app/services/solr_cores/example_core.json <<'EOF'
{"base_url": "https://solrslave-sec.labocleo.org/solr/example_core"}
EOF
```

Redémarrer le service (cycle de configuration existant, pas de modification de fichier `.py`). Résultat attendu : aucune erreur au démarrage ; le registre expose désormais 2 cores (SC-001).

## 3. Recherche sans paramètre `core` (non-régression)

```bash
curl -s -X POST "<API_BASE_URL>/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"query": {"query": "histoire"}, "filters": [], "pagination": {"from": 0, "size": 1}, "facets": []}'
```

Résultat attendu : réponse identique (mêmes résultats) à celle obtenue avant l'introduction de la feature — le core par défaut (`documents`) est utilisé (FR-005/SC-002).

## 4. Recherche ciblant explicitement le core par défaut

```bash
curl -s -X POST "<API_BASE_URL>/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"query": {"query": "histoire"}, "core": "documents", "filters": [], "pagination": {"from": 0, "size": 1}, "facets": []}'
```

Résultat attendu : résultats identiques à l'étape 3 (FR-003/SC-003).

## 5. Recherche ciblant un core inconnu

```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST "<API_BASE_URL>/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"query": {"query": "histoire"}, "core": "core_qui_nexiste_pas", "filters": [], "pagination": {"from": 0, "size": 1}, "facets": []}'
```

Résultat attendu : `404` (FR-004/SC-004), jamais un fallback silencieux vers un autre core.

## 6. Vérifier `/suggest` et `/permissions`

```bash
curl -s "<API_BASE_URL>/api/v1/suggest?q=hist&core=documents"
curl -s "<API_BASE_URL>/api/v1/permissions?urls=https://example.org/example-document&core=documents"
```

Résultat attendu : mêmes réponses qu'un appel sans `core` (comportement par défaut préservé, FR-006).

## 7. Vérifier la configuration invalide au démarrage

```bash
# Cas : registre vide
mv search_api_solr/app/services/solr_cores search_api_solr/app/services/solr_cores.bak
mkdir search_api_solr/app/services/solr_cores
# démarrer le service → attendu : échec explicite au démarrage (FR-007/SC-006)
mv search_api_solr/app/services/solr_cores.bak/* search_api_solr/app/services/solr_cores/
rmdir search_api_solr/app/services/solr_cores.bak
```

## 8. Vérifier la convergence des 3 points de résolution (FR-006)

```bash
cd search_api_solr
grep -n "SOLR_CONFIG\[.base_url.\]" app/services/search_service.py app/api/dependencies.py
```

Résultat attendu : plus aucune lecture directe de `SOLR_CONFIG["base_url"]` en dehors de la construction du `SolrCoreRegistry` lui-même — `PermissionsService` ne contourne plus la DI (voir `research.md`, audit initial).

## 9. Lancer les tests

```bash
cd search_api_solr
pytest tests/test_solr_core_registry.py tests/test_search_builder.py -v
```

Résultat attendu : tous verts, incluant les cas registre vide, doublon de `default`, core inconnu (`SolrCoreNotFoundError` → 404), et non-régression du comportement par défaut.

## Résultat de la dernière exécution (2026-09-03)

Les étapes 3 à 7 nécessitent une instance Solr distante joignable pour un test manuel `curl` complet ; elles ont été validées via la suite `pytest` (mêmes scénarios, exécutés en conditions reproductibles et sans dépendance réseau externe pour les cas d'erreur). Les étapes 1, 8 et 9 ont été exécutées telles quelles.

```text
$ cat search_api_solr/app/services/solr_cores/documents.json
{ "base_url": "https://solrslave-sec.labocleo.org/solr/documents", "default": true }
# Étape 1 : OK — identique à l'ancien settings.solr_base_url (FR-005)

$ grep -n 'SOLR_CONFIG\["base_url"\]' search_api_solr/app/services/search_service.py search_api_solr/app/api/dependencies.py
(aucune sortie)
# Étape 8 : OK — plus aucune lecture directe hors construction du registre

$ cd search_api_solr && pytest -v
128 passed, 33 warnings in 13.08s
# Étape 9 : OK — inclut les équivalents automatisés des étapes 2 à 7 :
#   - test_search_builder.py::test_build_search_url_targets_added_core (étape 2)
#   - test_regression_default_core.py::TestDefaultCoreEquivalence::* (étapes 3-4, 6)
#   - test_search_service.py::TestUnknownCoreReturns404::* (étape 5, sur /search, /suggest, /permissions)
#   - test_solr_core_registry.py::TestSolrCoreRegistry::test_empty_registry_fails_to_load,
#     test_two_default_cores_fails_to_load (étape 7)
```

## Critère de fin

L'implémentation est validée quand les étapes 1 à 9 produisent les résultats attendus, sans qu'aucune n'ait nécessité de modification de fichier `.py` pour les étapes 2 et 7 (seule la configuration a changé). C'est l'état atteint ci-dessus — 128/128 tests verts, aucune régression détectée.
