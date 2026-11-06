#!/bin/bash
# Script pour vérifier que la configuration d'environnement est correcte

set -e

echo "=== Environment Setup Verification ==="

# Vérifier les fichiers de base
REQUIRED_FILES=(
    ".env.development"
    ".env.production"
    ".env.test"
    "scripts/use-env.sh"
    "scripts/verify_env_docker.sh"
    "scripts/run_tests.sh"
    "search_api_solr/app/settings.py"
    "search_api_solr/app/core/env_validation.py"
    "front/app/lib/api.ts"
    "front/app/api/permissions/route.ts"
    "front/package.json"
    "front/pnpm-lock.yaml"
    "docker-compose.yml"
    "docker-compose.dev.yml"
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
for script in scripts/use-env.sh scripts/verify_env_docker.sh scripts/run_tests.sh scripts/check_env_setup.sh; do
    if [ -f "$script" ] && [ ! -x "$script" ]; then
        echo "WARNING: $script is not executable"
        chmod +x "$script"
        echo "Fixed: Made $script executable"
    fi
done

echo "✓ Script permissions verified"

# Vérifier la structure des fichiers .env (3 modèles versionnés, autonomes)
echo "Checking .env file structure..."
for env_file in .env.development .env.production .env.test; do
    if [ ! -s "$env_file" ]; then
        echo "WARNING: $env_file is empty"
    fi

    if grep -q "^\s*[A-Z_]*=" "$env_file"; then
        echo "✓ $env_file has valid syntax"
    else
        echo "WARNING: $env_file may have syntax issues"
    fi

    if ! grep -q "^ENVIRONMENT=" "$env_file"; then
        echo "WARNING: $env_file is missing ENVIRONMENT="
    fi
done

echo "✓ .env files structure verified"

# Vérifier qu'aucun fichier obsolète (ancien modèle) ne traîne
echo "Checking for obsolete leftover files..."
OBSOLETE_FILES=(.env.shared .env.staging .env.example docker-compose.staging.yml scripts/sync_env.sh scripts/configure_env.sh)
FOUND_OBSOLETE=()
for f in "${OBSOLETE_FILES[@]}"; do
    if [ -e "$f" ]; then
        FOUND_OBSOLETE+=("$f")
    fi
done
if [ ${#FOUND_OBSOLETE[@]} -gt 0 ]; then
    echo "WARNING: fichiers de l'ancien modèle encore présents (à supprimer) :"
    for f in "${FOUND_OBSOLETE[@]}"; do
        echo "  - $f"
    done
else
    echo "✓ No obsolete environment files found"
fi

# Vérifier l'intégration avec docker-compose
echo "Checking docker-compose integration..."
if grep -qE '^\s*-\s*\.env\s*$' docker-compose.yml; then
    echo "✓ docker-compose.yml loads the single active .env file"
else
    echo "WARNING: docker-compose.yml may not be using the expected env_file: .env"
fi

if docker compose version >/dev/null 2>&1; then
    docker compose -f docker-compose.yml -f docker-compose.dev.yml config --quiet
    docker compose -f docker-compose.yml -f docker-compose.prod.yml config --quiet
    echo "✓ docker-compose dev/prod configs are valid"
else
    echo "WARNING: docker compose is not available; skipped compose config validation"
fi

echo ""
echo "=== Environment Setup Verification Complete ==="
echo ""
echo "Next steps:"
echo "1. Run: ./scripts/use-env.sh development"
echo "2. Start services: make dev"
echo "3. Verify Docker picked it up: make env-verify"
echo "4. Run tests: ./scripts/run_tests.sh"
