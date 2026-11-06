#!/bin/bash
# Active un environnement applicatif (development, test, production) en copiant
# le fichier modèle correspondant vers .env (racine) et en exposant ce même
# fichier au front et à l'API via des symlinks. Remplace sync_env.sh/configure_env.sh.
#
# Usage: scripts/use-env.sh <development|test|production>

set -euo pipefail

ALLOWED_ENVIRONMENTS=(development test production)
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
    echo "Usage: $0 <development|test|production>" >&2
    echo "Valeurs autorisées : ${ALLOWED_ENVIRONMENTS[*]}" >&2
}

ENVIRONMENT="${1:-}"

if [ -z "$ENVIRONMENT" ]; then
    echo "Error: aucun environnement fourni." >&2
    usage
    exit 1
fi

is_allowed=false
for allowed in "${ALLOWED_ENVIRONMENTS[@]}"; do
    if [ "$ENVIRONMENT" = "$allowed" ]; then
        is_allowed=true
        break
    fi
done

if [ "$is_allowed" != true ]; then
    echo "Error: \"$ENVIRONMENT\" n'est pas un environnement valide." >&2
    usage
    exit 1
fi

TEMPLATE_FILE="$REPO_ROOT/.env.$ENVIRONMENT"

if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "Error: fichier modèle introuvable : $TEMPLATE_FILE" >&2
    exit 1
fi

cp "$TEMPLATE_FILE" "$REPO_ROOT/.env"

link_env() {
    local target="$1"
    # rm -f n'efface pas un répertoire (ex: résidu accidentel) : le supprimer explicitement d'abord.
    if [ -d "$target" ] && [ ! -L "$target" ]; then
        rmdir "$target" 2>/dev/null || rm -rf "$target"
    else
        rm -f "$target"
    fi
    ln -s "../.env" "$target"
}

link_env "$REPO_ROOT/front/.env"
link_env "$REPO_ROOT/search_api_solr/.env"

echo "Environnement activé : $ENVIRONMENT"
echo "  - $REPO_ROOT/.env (copie de .env.$ENVIRONMENT)"
echo "  - front/.env -> ../.env"
echo "  - search_api_solr/.env -> ../.env"
echo ""
case "$ENVIRONMENT" in
    development)
        echo "Prochaine étape : make dev  (ou: docker compose -f docker-compose.yml -f docker-compose.dev.yml up)"
        ;;
    test)
        echo "Prochaine étape : make test  (ou: make test-front)"
        ;;
    production)
        echo "Prochaine étape : docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build"
        echo "⚠️  Vérifiez que les secrets placeholders (\"change-me-in-production\") ont été surchargés avant de déployer réellement."
        ;;
esac
