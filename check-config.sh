#!/bin/bash

# Script de vérification de la configuration
# Vérifie que tous les fichiers nécessaires sont présents et configurés

set -e

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║   OpenEdition Search - Vérification Config   ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# Compteurs
CHECKS_TOTAL=0
CHECKS_PASSED=0
CHECKS_FAILED=0
WARNINGS=0

check_file() {
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $2"
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
        return 1
    fi
}

check_dir() {
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $2"
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
        return 1
    fi
}

check_command() {
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $2"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $2"
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
        return 1
    fi
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# 1. Vérifier les commandes
echo "=== Commandes requises ==="
check_command "docker" "Docker installé"
check_command "docker-compose" "Docker Compose installé"
check_command "make" "Make installé"
echo ""

# 2. Vérifier la structure Backend
echo "=== Structure Backend ==="
check_dir "search_api_solr" "Répertoire search_api_solr"
check_file "search_api_solr/docker-compose.yml" "docker-compose.yml"
check_file "search_api_solr/docker-compose.dev.yml" "docker-compose.dev.yml"
check_file "search_api_solr/docker-compose.prod.yml" "docker-compose.prod.yml"
check_file "search_api_solr/Dockerfile" "Dockerfile backend"
check_file "search_api_solr/Makefile" "Makefile"
check_file "search_api_solr/start.sh" "Script start.sh"
check_file "search_api_solr/requirements.txt" "requirements.txt"
echo ""

# 3. Vérifier la configuration Backend
echo "=== Configuration Backend ==="
check_file "search_api_solr/.env.example" "Fichier .env.example"

if check_file "search_api_solr/.env" "Fichier .env configuré"; then
    # Vérifier le contenu du .env
    if grep -q "SOLR_BASE_URL" search_api_solr/.env; then
        echo -e "  ${GREEN}→${NC} SOLR_BASE_URL configuré"
    else
        warn "  SOLR_BASE_URL non trouvé dans .env"
    fi
    
    if grep -q "API_PORT=8007" search_api_solr/.env; then
        echo -e "  ${GREEN}→${NC} API_PORT configuré (8007)"
    else
        warn "  API_PORT devrait être 8007"
    fi
else
    warn "Créez le fichier .env depuis .env.example : cp .env.example .env"
fi
echo ""

# 4. Vérifier la structure Frontend
echo "=== Structure Frontend ==="
check_dir "front" "Répertoire front"
check_file "front/Dockerfile" "Dockerfile frontend"
check_file "front/nginx.conf" "Configuration Nginx"
check_file "front/package.json" "package.json"
check_dir "front/src" "Répertoire src/"
check_dir "front/public" "Répertoire public/"
echo ""

# 5. Vérifier les composants Frontend
echo "=== Composants Frontend ==="
check_dir "front/src/components" "Répertoire components/"
check_file "front/src/components/SearchBar.jsx" "SearchBar.jsx"
check_file "front/src/components/ResultsList.jsx" "ResultsList.jsx"
check_file "front/src/components/Facets.jsx" "Facets.jsx"
check_file "front/src/components/Pagination.jsx" "Pagination.jsx"
check_dir "front/src/services" "Répertoire services/"
check_file "front/src/services/api.js" "api.js"
check_dir "front/src/utils" "Répertoire utils/"
check_file "front/src/utils/searchkit.js" "searchkit.js"
echo ""

# 6. Vérifier la configuration Frontend
echo "=== Configuration Frontend ==="
check_file "front/.env.example" "Fichier .env.example"

if check_file "front/.env" "Fichier .env configuré"; then
    if grep -q "REACT_APP_API_URL" front/.env; then
        echo -e "  ${GREEN}→${NC} REACT_APP_API_URL configuré"
    else
        warn "  REACT_APP_API_URL non trouvé dans .env"
    fi
else
    warn "Créez le fichier .env depuis .env.example : cp .env.example .env"
fi
echo ""

# 7. Vérifier les fichiers Nginx
echo "=== Configuration Nginx (Production) ==="
check_dir "search_api_solr/nginx" "Répertoire nginx/"
check_file "search_api_solr/nginx/nginx.conf" "nginx.conf"
check_file "search_api_solr/nginx/conf.d/default.conf" "default.conf"
echo ""

# 8. Vérifier la documentation
echo "=== Documentation ==="
check_file "README.md" "README.md principal"
check_file "search_api_solr/DOCKER.md" "DOCKER.md"
check_file "search_api_solr/DOCKER_SETUP.md" "DOCKER_SETUP.md"
check_file "front/README.md" "README.md frontend"
echo ""

# 9. Vérifier les permissions
echo "=== Permissions ==="
if [ -x "search_api_solr/start.sh" ]; then
    echo -e "${GREEN}✓${NC} start.sh est exécutable"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${RED}✗${NC} start.sh n'est pas exécutable"
    info "Exécutez : chmod +x search_api_solr/start.sh"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
echo ""

# 10. Vérifier Docker
echo "=== Docker ==="
if docker ps &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker daemon en cours d'exécution"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${RED}✗${NC} Docker daemon non accessible"
    info "Démarrez Docker et réessayez"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))

# Vérifier si des conteneurs sont déjà en cours
RUNNING_CONTAINERS=$(docker ps --filter "name=openedition" --filter "name=search_api_solr" -q | wc -l)
if [ "$RUNNING_CONTAINERS" -gt 0 ]; then
    warn "Des conteneurs OpenEdition sont déjà en cours d'exécution ($RUNNING_CONTAINERS)"
    info "Arrêtez-les avec : cd search_api_solr && make down"
fi

# Vérifier l'accès à Solr distant
echo ""
echo "=== Solr distant ==="
if curl -f -s https://solrslave-sec.labocleo.org/solr/documents/admin/ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Solr distant accessible (https://solrslave-sec.labocleo.org)"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${YELLOW}⚠${NC} Solr distant non accessible (peut nécessiter VPN)"
    info "URL: https://solrslave-sec.labocleo.org/solr/documents"
    WARNINGS=$((WARNINGS + 1))
fi
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
echo ""

# Résumé
echo "═══════════════════════════════════════════════"
echo "RÉSUMÉ"
echo "═══════════════════════════════════════════════"
echo -e "Total de vérifications : ${CHECKS_TOTAL}"
echo -e "${GREEN}Réussites : ${CHECKS_PASSED}${NC}"
if [ $CHECKS_FAILED -gt 0 ]; then
    echo -e "${RED}Échecs : ${CHECKS_FAILED}${NC}"
fi
if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}Avertissements : ${WARNINGS}${NC}"
fi
echo ""

# Conclusion
if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ Configuration complète !${NC}"
    echo ""
    echo "Pour démarrer :"
    echo "  cd search_api_solr"
    echo "  ./start.sh dev"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Configuration incomplète${NC}"
    echo ""
    echo "Corrigez les erreurs ci-dessus avant de démarrer."
    echo ""
    exit 1
fi
