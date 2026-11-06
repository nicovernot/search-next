#!/bin/bash
# Vérifie que la configuration appliquée dans les conteneurs Docker correspond
# au .env actif (racine), pour un sous-ensemble critique de variables.
# Usage: scripts/verify_env_docker.sh [development|test|production]

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$REPO_ROOT/.env"
VARS=(ENVIRONMENT CORS_ORIGINS NEXT_PUBLIC_API_URL SOLR_URL SOLR_BASE_URL SOLR_COLLECTION)

if [ ! -f "$ENV_FILE" ]; then
    echo "Error: $ENV_FILE introuvable. Activez d'abord un environnement : scripts/use-env.sh <development|test|production>" >&2
    exit 1
fi

ENVIRONMENT_ARG="${1:-}"
if [ -z "$ENVIRONMENT_ARG" ]; then
    ENVIRONMENT_ARG="$(grep -E '^ENVIRONMENT=' "$ENV_FILE" | head -1 | cut -d= -f2-)"
fi

get_expected() {
    grep -E "^$1=" "$ENV_FILE" | head -1 | cut -d= -f2-
}

# Détecte le conteneur frontend actif (dev ou prod).
API_CONTAINER="search-next_api"
FRONTEND_CONTAINER=""
for candidate in search-next_frontend_dev search-next_frontend; do
    if docker ps --format '{{.Names}}' | grep -qx "$candidate"; then
        FRONTEND_CONTAINER="$candidate"
        break
    fi
done

MISSING_CONTAINERS=()
if ! docker ps --format '{{.Names}}' | grep -qx "$API_CONTAINER"; then
    MISSING_CONTAINERS+=("$API_CONTAINER")
fi
if [ -z "$FRONTEND_CONTAINER" ]; then
    MISSING_CONTAINERS+=("search-next_frontend_dev|search-next_frontend")
fi

if [ ${#MISSING_CONTAINERS[@]} -gt 0 ]; then
    echo "Error: conteneur(s) introuvable(s) ou arrêté(s) : ${MISSING_CONTAINERS[*]}" >&2
    echo "Démarrez d'abord les conteneurs (ex: make dev) avant de lancer cette vérification." >&2
    exit 1
fi

printf "%-12s %-22s %-45s %-45s %s\n" "Service" "Variable" "Attendu (.env)" "Obtenu (conteneur)" "Statut"
printf '%.0s-' {1..140}; echo

EXIT_CODE=0

check_var() {
    local service="$1" container="$2" var="$3"
    local expected actual status
    expected="$(get_expected "$var")"
    actual="$(docker exec "$container" printenv "$var" 2>/dev/null)"
    if [ -z "$actual" ] && ! docker exec "$container" printenv "$var" > /dev/null 2>&1; then
        status="MISSING"
        EXIT_CODE=1
    elif [ "$expected" = "$actual" ]; then
        status="MATCH"
    else
        status="MISMATCH"
        EXIT_CODE=1
    fi
    printf "%-12s %-22s %-45s %-45s %s\n" "$service" "$var" "${expected:0:45}" "${actual:0:45}" "$status"
}

for var in "${VARS[@]}"; do
    check_var "api" "$API_CONTAINER" "$var"
done
for var in "${VARS[@]}"; do
    check_var "frontend" "$FRONTEND_CONTAINER" "$var"
done

echo
if [ "$ENVIRONMENT_ARG" = "production" ]; then
    echo "⚠️  ENVIRONMENT=production : les variables NEXT_PUBLIC_* sont inlinées dans le bundle Next.js AU BUILD."
    echo "   Une valeur runtime correcte ci-dessus ne garantit pas que le build déployé l'utilise bien —"
    echo "   si vous venez de changer NEXT_PUBLIC_API_URL, relancez : docker compose build frontend"
fi

if [ "$EXIT_CODE" -eq 0 ]; then
    echo "✓ Toutes les variables vérifiées correspondent au .env actif."
else
    echo "✗ Écart(s) détecté(s) — voir le tableau ci-dessus. Recréez les conteneurs concernés :"
    echo "  docker compose up -d --force-recreate --no-deps api frontend"
fi

exit $EXIT_CODE
