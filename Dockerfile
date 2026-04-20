FROM python:3.10-slim

WORKDIR /app

# Installation des dépendances système minimales
# curl est utile pour les healthchecks
# postgresql-client est nécessaire pour pg_isready dans entrypoint.sh
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de dépendances
COPY search_api_solr/requirements.txt .
COPY search_api_solr/requirements-dev.txt .

# Build argument to optionally install development/test dependencies (useful for CI)
ARG INSTALL_DEV=false

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt
# Installer les dépendances de développement si demandé
RUN if [ "$INSTALL_DEV" = "true" ]; then pip install --no-cache-dir -r requirements-dev.txt; fi

# Copie du code source
COPY search_api_solr/ .

# Copier et rendre exécutable le script d'entrée
COPY search_api_solr/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Exposition du port
EXPOSE 8007

# Point d'entrée pour exécuter les migrations avant de démarrer
ENTRYPOINT ["/entrypoint.sh"]

# Commande de démarrage par défaut (passée à entrypoint.sh)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8007"]
