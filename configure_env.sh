#!/bin/bash

# configure_env.sh
# Script pour configurer l'environnement backend et frontend

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher l'aide
show_help() {
    echo -e "${BLUE}Usage:${NC} $0 [OPTIONS]"
    echo ""
    echo -e "${BLUE}Options:${NC}"
    echo -e "  ${GREEN}-e, --env ENV${NC}		Spécifier l'environnement (development, staging, production, test)"
    echo -e "  ${GREEN}-f, --frontend-env ENV${NC}	Spécifier l'environnement frontend"
    echo -e "  ${GREEN}-h, --help${NC}			Afficher cette aide"
    echo ""
    echo -e "${BLUE}Exemples:${NC}"
    echo -e "  ${YELLOW}$0 --env development${NC}			Configurer pour le développement"
    echo -e "  ${YELLOW}$0 --env production --frontend-env production${NC}	Configurer pour la production"
    echo -e "  ${YELLOW}$0 -e staging -f staging${NC}			Configurer pour le staging"
    exit 0
}

# Vérifier les dépendances
check_dependencies() {
    if [ ! -d "search_api_solr" ]; then
        echo -e "${RED}Erreur:${NC} Le dossier search_api_solr est introuvable"
        exit 1
    fi
    
    if [ ! -d "front" ]; then
        echo -e "${RED}Erreur:${NC} Le dossier front est introuvable"
        exit 1
    fi
}

# Valider l'environnement
validate_environment() {
    local env=$1
    local valid_envs=("development" "staging" "production" "test")
    
    for valid_env in "${valid_envs[@]}"; do
        if [ "$env" = "$valid_env" ]; then
            return 0
        fi
    done
    
    echo -e "${RED}Erreur:${NC} Environnement invalide: $env"
    echo -e "Environnements valides: ${valid_envs[*]}"
    exit 1
}

# Configurer l'environnement backend
configure_backend() {
    local env=$1
    local backend_dir="search_api_solr"
    local env_file="${backend_dir}/.env.${env}"
    local target_file="${backend_dir}/.env"
    
    echo -e "${BLUE}Configuration du backend pour l'environnement: ${YELLOW}${env}${NC}"
    
    if [ ! -f "$env_file" ]; then
        echo -e "${RED}Erreur:${NC} Fichier $env_file introuvable"
        exit 1
    fi
    
    # Sauvegarder l'ancien .env si nécessaire
    if [ -f "$target_file" ]; then
        echo -e "${YELLOW}Sauvegarde de l'ancien .env en .env.bak${NC}"
        cp "$target_file" "${target_file}.bak"
    fi
    
    # Copier le fichier de configuration
    cp "$env_file" "$target_file"
    echo -e "${GREEN}✓${NC} Backend configuré avec ${YELLOW}${env}${NC}"
    
    # Afficher les paramètres clés
    echo -e "${BLUE}Paramètres backend:${NC}"
    grep -v "^#" "$target_file" | grep -v "^$" | while read line; do
        if echo "$line" | grep -q "^"; then
            echo "  $line"
        fi
    done | head -5
}

# Configurer l'environnement frontend
configure_frontend() {
    local env=$1
    local frontend_dir="front"
    local env_file="${frontend_dir}/.env.${env}"
    local target_file="${frontend_dir}/.env"
    
    echo -e "${BLUE}Configuration du frontend pour l'environnement: ${YELLOW}${env}${NC}"
    
    if [ ! -f "$env_file" ]; then
        echo -e "${RED}Erreur:${NC} Fichier $env_file introuvable"
        exit 1
    fi
    
    # Sauvegarder l'ancien .env si nécessaire
    if [ -f "$target_file" ]; then
        echo -e "${YELLOW}Sauvegarde de l'ancien .env en .env.bak${NC}"
        cp "$target_file" "${target_file}.bak"
    fi
    
    # Copier le fichier de configuration
    cp "$env_file" "$target_file"
    echo -e "${GREEN}✓${NC} Frontend configuré avec ${YELLOW}${env}${NC}"
    
    # Afficher les paramètres clés
    echo -e "${BLUE}Paramètres frontend:${NC}"
    grep -v "^#" "$target_file" | grep -v "^$" | while read line; do
        if echo "$line" | grep -q "^"; then
            echo "  $line"
        fi
    done | head -5
}

# Vérifier la configuration
verify_configuration() {
    local backend_env=$1
    local frontend_env=$2
    
    echo -e "${BLUE}Vérification de la configuration...${NC}"
    
    # Vérifier le backend
    if [ -f "search_api_solr/.env" ]; then
        backend_actual=$(grep -E "^ENVIRONMENT=" search_api_solr/.env | cut -d'=' -f2)
        if [ "$backend_actual" = "$backend_env" ]; then
            echo -e "${GREEN}✓${NC} Backend: ${YELLOW}${backend_env}${NC}"
        else
            echo -e "${RED}✗${NC} Backend: Attendu ${YELLOW}${backend_env}${NC}, trouvé ${YELLOW}${backend_actual}${NC}"
        fi
    else
        echo -e "${RED}✗${NC} Backend: Fichier .env introuvable"
    fi
    
    # Vérifier le frontend
    if [ -f "front/.env" ]; then
        frontend_actual=$(grep -E "^ENVIRONMENT=" front/.env | cut -d'=' -f2)
        if [ "$frontend_actual" = "$frontend_env" ]; then
            echo -e "${GREEN}✓${NC} Frontend: ${YELLOW}${frontend_env}${NC}"
        else
            echo -e "${RED}✗${NC} Frontend: Attendu ${YELLOW}${frontend_env}${NC}, trouvé ${YELLOW}${frontend_actual}${NC}"
        fi
    else
        echo -e "${RED}✗${NC} Frontend: Fichier .env introuvable"
    fi
}

# Main script
main() {
    # Variables par défaut
    local backend_env="development"
    local frontend_env="development"
    
    # Parser les arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -e|--env)
                backend_env="$2"
                shift 2
                ;;
            -f|--frontend-env)
                frontend_env="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                ;;
            *)
                echo -e "${RED}Erreur:${NC} Argument invalide: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Vérifier les dépendances
    check_dependencies
    
    # Valider les environnements
    validate_environment "$backend_env"
    validate_environment "$frontend_env"
    
    # Afficher la configuration
    echo -e "${BLUE}===========================================${NC}"
    echo -e "${BLUE}Configuration des Environnements${NC}"
    echo -e "${BLUE}===========================================${NC}"
    echo -e "Backend:    ${YELLOW}${backend_env}${NC}"
    echo -e "Frontend:   ${YELLOW}${frontend_env}${NC}"
    echo ""
    
    # Configurer les environnements
    configure_backend "$backend_env"
    echo ""
    configure_frontend "$frontend_env"
    echo ""
    
    # Vérifier la configuration
    verify_configuration "$backend_env" "$frontend_env"
    echo ""
    
    # Message de succès
    echo -e "${GREEN}===========================================${NC}"
    echo -e "${GREEN}✓ Configuration terminée avec succès !${NC}"
    echo -e "${GREEN}===========================================${NC}"
    echo ""
    echo -e "${BLUE}Commandes utiles:${NC}"
    echo -e "  ${YELLOW}make dev${NC}			Lancer en développement"
    echo -e "  ${YELLOW}make prod${NC}			Lancer en production"
    echo -e "  ${YELLOW}make test${NC}			Lancer les tests"
    echo ""
}

# Exécuter le script principal
main "$@"
