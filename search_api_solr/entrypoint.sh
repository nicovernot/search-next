#!/bin/bash
set -e

# entrypoint.sh for the FastAPI application

# 1. Attendre que la base de données PostgreSQL soit prête.
# Le service s'appelle 'postgres' dans docker-compose.yml.
echo "⏳ Waiting for PostgreSQL to be ready..."
# La variable DATABASE_URL est injectée par Docker Compose.
# Nous extrayons les composants pour pg_isready.
# Example: postgresql://search_user:search_password@postgres:5432/search_db
DB_USER="${DATABASE_URL#*://}"
DB_USER="${DB_USER%%:*}"
DB_AUTHORITY="${DATABASE_URL#*@}"
DB_HOST="${DB_AUTHORITY%%:*}"
DB_PORT_AND_PATH="${DB_AUTHORITY#*:}"
DB_PORT="${DB_PORT_AND_PATH%%/*}"

# Boucle jusqu'à ce que la base de données réponde
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done
>&2 echo "✅ PostgreSQL is up and running"

# 2. Appliquer les migrations de la base de données avec Alembic.
echo "🚀 Applying database migrations..."
alembic upgrade head
echo "✅ Database migrations applied successfully."

# 3. Lancer le serveur Uvicorn.
# Le `exec "$@"` permet de passer la main au processus Uvicorn,
# ce qui assure une gestion correcte des signaux (comme l'arrêt du conteneur).
echo "🚀 Starting Uvicorn server..."
exec "$@"
