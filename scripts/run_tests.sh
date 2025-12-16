#!/bin/bash
# Script pour exécuter les tests avec la configuration d'environnement appropriée

set -e

echo "=== Running Tests with Environment Configuration ==="

# Synchroniser l'environnement de test
./scripts/sync_env.sh development

echo "Environment synchronized for testing"

echo "Running backend tests..."
cd search_api_solr
python -m pytest tests/ -v --tb=short --color=yes
echo "Backend tests completed"

cd ..

echo "Running frontend tests..."
cd front
npm test -- --watchAll=false --colors
echo "Frontend tests completed"

cd ..

echo "=== All Tests Completed ==="