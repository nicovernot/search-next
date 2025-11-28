# Tests

Ce répertoire contient les tests unitaires et d'intégration pour l'API de recherche Solr.

## Structure

```
tests/
├── __init__.py
├── test_facet_config.py      # Tests de configuration des facettes (10 tests)
├── test_search_builder.py    # Tests du SearchBuilder (7 tests)
└── test_endpoints.py          # Tests des endpoints API (6 tests)
```

## Exécution des tests

### Tous les tests
```bash
python3 -m pytest tests/ -v
```

### Tests spécifiques
```bash
# Tests de configuration des facettes
python3 -m pytest tests/test_facet_config.py -v

# Tests du SearchBuilder
python3 -m pytest tests/test_search_builder.py -v

# Tests des endpoints
python3 -m pytest tests/test_endpoints.py -v
```

### Avec couverture de code
```bash
python3 -m pytest tests/ --cov=app --cov-report=html
```

## Résultats

✅ **23 tests passent avec succès**

### test_facet_config.py (10 tests)
- Configuration des facettes communes
- Sous-catégories de facettes
- Facettes spécifiques par plateforme
- Fonction `get_filter_values()`

### test_search_builder.py (7 tests)
- Construction de filtres simples et avec sous-catégories
- Construction d'URLs Solr
- Expansion des sous-catégories avec OR
- Facettes spécifiques par plateforme

### test_endpoints.py (6 tests)
- Endpoint `/search` avec différents filtres
- Endpoint `/permissions` en mode DEV
- Intégration complète de l'API

## Installation des dépendances de test

```bash
pip install -r requirements-dev.txt
```

Ou manuellement :
```bash
pip install pytest pytest-asyncio pytest-cov
```
