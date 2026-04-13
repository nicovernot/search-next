#!/bin/bash

set -euo pipefail

echo "=== Running Project Checks ==="

echo "Synchronizing test environment..."
./scripts/sync_env.sh test

echo "Backend checks..."
(
  cd search_api_solr
  python3 -m pytest tests/ -v --tb=short --color=yes
)

echo "Frontend checks..."
(
  cd front
  npm run lint
  npm run test:e2e
)

echo "=== All Checks Completed ==="
