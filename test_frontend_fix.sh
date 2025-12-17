#!/bin/bash

echo "🔍 Test de validation du fix frontend OpenEdition Search v2"
echo "========================================================="

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les résultats
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        exit 1
    fi
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# 1. Vérifier la redirection de la racine
print_info "Test de redirection racine vers /search..."
REDIRECT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3009/)
[ "$REDIRECT_STATUS" = "301" ]
print_result $? "Redirection racine (/) vers /search/ fonctionne"

# 2. Vérifier l'accès à la page principale
print_info "Test d'accès à la page principale..."
MAIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3009/search/)
[ "$MAIN_STATUS" = "200" ]
print_result $? "Page principale /search/ accessible"

# 3. Vérifier le chargement des fichiers JS
print_info "Test de chargement des fichiers JavaScript..."
JS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3009/search/static/js/main.8ea54147.js)
[ "$JS_STATUS" = "200" ]
print_result $? "Fichiers JavaScript se chargent correctement"

# 4. Vérifier le chargement des fichiers CSS
print_info "Test de chargement des fichiers CSS..."
CSS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3009/search/static/css/main.6ac36ec5.css)
[ "$CSS_STATUS" = "200" ]
print_result $? "Fichiers CSS se chargent correctement"

# 5. Vérifier que l'API backend fonctionne
print_info "Test de l'API backend..."
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8007/health)
[ "$API_STATUS" = "200" ]
print_result $? "API backend accessible"

# 6. Vérifier que Redis fonctionne
print_info "Test du cache Redis..."
CACHE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8007/cache/stats)
[ "$CACHE_STATUS" = "200" ]
print_result $? "Cache Redis opérationnel"

# 7. Test d'intégration frontend-backend
print_info "Test d'intégration frontend-backend..."
# Simuler une requête depuis le frontend vers l'API
INTEGRATION_TEST=$(curl -s -X POST http://localhost:8007/search \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:3009" \
  -d '{"query": {"query": "test"}, "filters": [], "pagination": {"from": 0, "size": 5}, "facets": []}' \
  -w "%{http_code}")

echo "$INTEGRATION_TEST" | grep -q "200"
print_result $? "Intégration frontend-backend fonctionne"

echo ""
echo -e "${GREEN}🎉 Tous les tests sont passés avec succès!${NC}"
echo ""
echo -e "${YELLOW}📋 Résumé du fix:${NC}"
echo "   ✅ Configuration nginx corrigée pour servir sur /search"
echo "   ✅ Redirection automatique de / vers /search/"
echo "   ✅ Assets statiques (JS/CSS) accessibles"
echo "   ✅ Intégration frontend-backend opérationnelle"
echo "   ✅ Cache Redis fonctionnel"
echo ""
echo -e "${YELLOW}🔗 URLs d'accès:${NC}"
echo "   🌐 Frontend: http://localhost:3009/search/"
echo "   🔧 API: http://localhost:8007/"
echo "   📊 Cache stats: http://localhost:8007/cache/stats"
echo "   ❤️  Health check: http://localhost:8007/health"