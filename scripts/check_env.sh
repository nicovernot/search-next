#!/bin/bash
# Script de vérification de l'environnement OpenEdition Search v2
# Vérifie que tous les services sont correctement configurés et fonctionnels

set -e

echo "🔍 Vérification de l'environnement OpenEdition Search v2"
echo "=========================================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les résultats
check_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
        return 1
    fi
}

# 1. Vérifier Docker
echo "1️⃣  Vérification de Docker..."
if command -v docker &> /dev/null; then
    check_status 0 "Docker est installé"
    docker --version
else
    check_status 1 "Docker n'est pas installé"
    exit 1
fi
echo ""

# 2. Vérifier Docker Compose
echo "2️⃣  Vérification de Docker Compose..."
if command -v docker-compose &> /dev/null; then
    check_status 0 "Docker Compose est installé"
    docker-compose --version
else
    check_status 1 "Docker Compose n'est pas installé"
    exit 1
fi
echo ""

# 3. Vérifier les fichiers .env
echo "3️⃣  Vérification des fichiers de configuration..."
if [ -f "search_api_solr/.env" ]; then
    check_status 0 "Fichier search_api_solr/.env existe"
    
    # Vérifier le format CSV
    if grep -q "types_needing_parents=article,chapter" search_api_solr/.env; then
        check_status 0 "Format CSV correct pour types_needing_parents"
    else
        check_status 1 "Format CSV incorrect pour types_needing_parents (doit être: article,chapter)"
    fi
    
    # Vérifier CORS
    if grep -q "CORS_ORIGINS=" search_api_solr/.env; then
        check_status 0 "Configuration CORS présente"
        echo "   Origines CORS configurées:"
        grep "CORS_ORIGINS=" search_api_solr/.env | sed 's/CORS_ORIGINS=/   - /' | tr ',' '\n'
    else
        check_status 1 "Configuration CORS manquante"
    fi
else
    check_status 1 "Fichier search_api_solr/.env manquant"
    echo -e "${YELLOW}ℹ${NC}  Exécutez: cp search_api_solr/.env.development search_api_solr/.env"
fi
echo ""

# 4. Vérifier les containers Docker
echo "4️⃣  Vérification des containers Docker..."
if docker ps &> /dev/null; then
    # API Backend
    if docker ps --format '{{.Names}}' | grep -q "search_api_solr"; then
        STATUS=$(docker inspect search_api_solr --format='{{.State.Health.Status}}' 2>/dev/null || echo "no-health")
        if [ "$STATUS" = "healthy" ]; then
            check_status 0 "Container API (search_api_solr) - healthy"
        else
            check_status 1 "Container API (search_api_solr) - $STATUS"
        fi
    else
        check_status 1 "Container API (search_api_solr) non démarré"
    fi
    
    # Frontend Production
    if docker ps --format '{{.Names}}' | grep -q "openedition_frontend"; then
        STATUS=$(docker inspect openedition_frontend --format='{{.State.Health.Status}}' 2>/dev/null || echo "no-health")
        if [ "$STATUS" = "healthy" ]; then
            check_status 0 "Container Frontend Prod (openedition_frontend) - healthy"
        else
            check_status 1 "Container Frontend Prod (openedition_frontend) - $STATUS"
        fi
    else
        echo -e "${YELLOW}⚠${NC}  Container Frontend Prod (openedition_frontend) non démarré"
    fi
    
    # Frontend Dev
    if docker ps --format '{{.Names}}' | grep -q "openedition_frontend_dev"; then
        check_status 0 "Container Frontend Dev (openedition_frontend_dev) - running"
    else
        echo -e "${YELLOW}⚠${NC}  Container Frontend Dev (openedition_frontend_dev) non démarré"
    fi
else
    check_status 1 "Impossible de vérifier les containers Docker"
fi
echo ""

# 5. Vérifier les ports
echo "5️⃣  Vérification des ports..."
check_port() {
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$1" | grep -q "$2"; then
        check_status 0 "Port $1 accessible"
        return 0
    else
        check_status 1 "Port $1 non accessible"
        return 1
    fi
}

# API (port 8007)
if check_port 8007 "200"; then
    echo "   API: http://localhost:8007/docs"
fi

# Frontend Prod (port 3009)
if check_port 3009 "200"; then
    echo "   Frontend Production: http://localhost:3009"
fi

# Frontend Dev (port 3007)
if check_port 3007 "200"; then
    echo "   Frontend Dev: http://localhost:3007"
fi
echo ""

# 6. Vérifier Solr distant
echo "6️⃣  Vérification de Solr distant..."
if curl -s -f "https://solrslave-sec.labocleo.org/solr/documents/admin/ping" > /dev/null 2>&1; then
    check_status 0 "Solr distant accessible"
else
    check_status 1 "Solr distant non accessible"
fi
echo ""

# 7. Résumé
echo "=========================================================="
echo "📊 Résumé"
echo "=========================================================="
echo ""
echo "Services disponibles:"
echo "  • API Backend:         http://localhost:8007/docs"
echo "  • Frontend Production: http://localhost:3009"
echo "  • Frontend Dev:        http://localhost:3007"
echo ""
echo "Pour démarrer les services:"
echo "  make dev              # Environnement de développement"
echo "  make dev-build        # Rebuild et démarrer"
echo ""
echo "Pour voir les logs:"
echo "  make logs             # Tous les services"
echo "  make logs-api         # API seulement"
echo "  make logs-frontend    # Frontend seulement"
echo ""
echo "Pour plus d'aide:"
echo "  make help"
echo ""
