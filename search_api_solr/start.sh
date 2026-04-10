#!/bin/bash

# Script de démarrage pour OpenEdition Search
# Usage: ./start.sh [dev|prod|test]

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'affichage
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Vérifier que Docker est installé
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker n'est pas installé. Veuillez l'installer : https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Détecter si docker compose ou docker-compose doit être utilisé
    if docker compose version &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker compose"
    elif command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker-compose"
    else
        print_error "Docker Compose n'est pas installé (ni 'docker compose' ni 'docker-compose')."
        print_info "Veuillez l'installer : https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    print_success "Docker est installé et $(echo $DOCKER_COMPOSE_CMD | sed 's/./\U&/') est disponible"
}

# Vérifier les fichiers .env
check_env_files() {
    if [ ! -f .env ]; then
        print_warning "Fichier .env non trouvé pour l'API"
        if [ -f .env.example ]; then
            print_info "Copie de .env.example vers .env"
            cp .env.example .env
        else
            print_error "Veuillez créer un fichier .env"
            exit 1
        fi
    fi
    
    if [ ! -f ../front/.env ]; then
        print_warning "Fichier .env non trouvé pour le frontend"
        if [ -f ../front/.env.example ]; then
            print_info "Copie de ../front/.env.example vers ../front/.env"
            cp ../front/.env.example ../front/.env
        fi
    fi
    
    print_success "Fichiers de configuration vérifiés"
}

# Mode développement
start_dev() {
    print_info "Démarrage en mode développement..."
    $DOCKER_COMPOSE_CMD -f docker-compose.yml -f docker-compose.dev.yml up --build
}

# Mode production
start_prod() {
    print_info "Démarrage en mode production..."
    $DOCKER_COMPOSE_CMD -f docker-compose.yml -f docker-compose.prod.yml up -d --build
    
    print_success "Services démarrés en arrière-plan"
    echo ""
    print_info "Services disponibles :"
    echo "  - Application : http://localhost"
    echo "  - API : http://localhost:8007"
    echo "  - Solr Admin : http://localhost:8983/solr"
    echo ""
    print_info "Voir les logs : $DOCKER_COMPOSE_CMD logs -f"
    print_info "Arrêter : $DOCKER_COMPOSE_CMD -f docker-compose.yml -f docker-compose.prod.yml down"
}

# Mode test
start_test() {
    print_info "Lancement des tests..."
    $DOCKER_COMPOSE_CMD up -d
    sleep 5  # Attendre que les services démarrent
    $DOCKER_COMPOSE_CMD exec api pytest
    $DOCKER_COMPOSE_CMD down
}

# Arrêt des services
stop_services() {
    print_info "Arrêt des services..."
    $DOCKER_COMPOSE_CMD down
    print_success "Services arrêtés"
}

# Afficher l'aide
show_help() {
    echo "Usage: ./start.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  dev       Démarrer en mode développement (avec hot reload)"
    echo "  prod      Démarrer en mode production"
    echo "  test      Lancer les tests"
    echo "  stop      Arrêter tous les services"
    echo "  clean     Nettoyer les conteneurs et volumes"
    echo "  logs      Voir les logs"
    echo "  help      Afficher cette aide"
    echo ""
    echo "Exemples:"
    echo "  ./start.sh dev"
    echo "  ./start.sh prod"
    echo "  ./start.sh test"
}

# Point d'entrée principal
main() {
    echo ""
    echo "╔══════════════════════════════════════╗"
    echo "║   OpenEdition Search - Launcher     ║"
    echo "╚══════════════════════════════════════╝"
    echo ""
    
    check_docker
    check_env_files
    
    case "${1:-help}" in
        dev)
            start_dev
            ;;
        prod)
            start_prod
            ;;
        test)
            start_test
            ;;
        stop)
            stop_services
            ;;
        clean)
            print_info "Nettoyage..."
            $DOCKER_COMPOSE_CMD down -v
            docker system prune -f
            print_success "Nettoyage terminé"
            ;;
        logs)
            $DOCKER_COMPOSE_CMD logs -f
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Commande inconnue : $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
