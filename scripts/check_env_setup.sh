#!/bin/bash
# Script pour vérifier que la configuration d'environnement est correcte

set -e

echo "=== Environment Setup Verification ==="

# Vérifier les fichiers de base
REQUIRED_FILES=(
    ".env.shared"
    ".env.development"
    ".env.production"
    ".env.staging"
    ".env.test"
    ".env.example"
    "scripts/sync_env.sh"
    "scripts/run_tests.sh"
    "search_api_solr/app/core/env_validation.py"
    "front/app/lib/api.ts"
    "front/app/api/permissions/route.ts"
    "front/package.json"
    "front/pnpm-lock.yaml"
    "docker-compose.yml"
    "docker-compose.dev.yml"
    "docker-compose.staging.yml"
    "docker-compose.prod.yml"
)

MISSING_FILES=()

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo "ERROR: Missing required files:"
    for file in "${MISSING_FILES[@]}"; do
        echo "  - $file"
    done
    exit 1
fi

echo "✓ All required files are present"

# Vérifier les permissions des scripts
echo "Checking script permissions..."
for script in scripts/sync_env.sh scripts/run_tests.sh scripts/check_env_setup.sh; do
    if [ -f "$script" ] && [ ! -x "$script" ]; then
        echo "WARNING: $script is not executable"
        chmod +x "$script"
        echo "Fixed: Made $script executable"
    fi
done

echo "✓ Script permissions verified"

# Vérifier la structure des fichiers .env
echo "Checking .env file structure..."
for env_file in .env.shared .env.development .env.production .env.staging .env.test; do
    if [ ! -s "$env_file" ]; then
        echo "WARNING: $env_file is empty"
    fi
    
    # Vérifier la syntaxe de base
    if grep -q "^\s*[A-Z_]*=" "$env_file"; then
        echo "✓ $env_file has valid syntax"
    else
        echo "WARNING: $env_file may have syntax issues"
    fi
done

echo "✓ .env files structure verified"

# Vérifier l'intégration avec docker-compose
echo "Checking docker-compose integration..."
if grep -q ".env.shared" docker-compose.yml && grep -q "search_api_solr/.env.local" docker-compose.yml; then
    echo "✓ docker-compose.yml loads shared and generated backend env files"
else
    echo "WARNING: docker-compose.yml may not be using the expected environment files"
fi

if docker compose version >/dev/null 2>&1; then
    docker compose -f docker-compose.yml -f docker-compose.dev.yml config --quiet
    docker compose -f docker-compose.yml -f docker-compose.staging.yml config --quiet
    docker compose -f docker-compose.yml -f docker-compose.prod.yml config --quiet
    echo "✓ docker-compose dev/staging/prod configs are valid"
else
    echo "WARNING: docker compose is not available; skipped compose config validation"
fi

echo ""
echo "=== Environment Setup Verification Complete ==="
echo ""
echo "Next steps:"
echo "1. Run: ./scripts/sync_env.sh development"
echo "2. Start services: docker-compose up"
echo "3. Run tests: ./scripts/run_tests.sh"
