#!/bin/bash

echo "🌐 Test de compatibilité Chrome - OpenEdition Search v2"
echo "====================================================="

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

# 1. Test de la redirection avec User-Agent Chrome
print_info "Test de redirection avec User-Agent Chrome..."
CHROME_REDIRECT=$(curl -s -I -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" http://localhost:3009/ | grep "Location:")
echo "$CHROME_REDIRECT" | grep -q "localhost:3009/search/"
print_result $? "Redirection Chrome vers localhost:3009/search/"

# 2. Test du contenu HTML complet
print_info "Test du contenu HTML complet..."
HTML_CONTENT=$(curl -s -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" http://localhost:3009/search/)
echo "$HTML_CONTENT" | grep -q "<div id=\"root\"></div>"
print_result $? "Div root React présent"

echo "$HTML_CONTENT" | grep -q "defer.*main.*js"
print_result $? "Script principal avec defer présent"

echo "$HTML_CONTENT" | grep -q "main.*css.*stylesheet"
print_result $? "Feuille de style principale présente"

# 3. Test des headers de sécurité
print_info "Test des headers de sécurité..."
SECURITY_HEADERS=$(curl -s -I http://localhost:3009/search/)
echo "$SECURITY_HEADERS" | grep -q "X-Frame-Options"
print_result $? "Header X-Frame-Options présent"

echo "$SECURITY_HEADERS" | grep -q "X-Content-Type-Options"
print_result $? "Header X-Content-Type-Options présent"

# 4. Test des assets avec différents User-Agents
print_info "Test des assets avec User-Agent Chrome..."
JS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" http://localhost:3009/search/static/js/main.8ea54147.js)
[ "$JS_STATUS" = "200" ]
print_result $? "JavaScript accessible avec Chrome User-Agent"

CSS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" http://localhost:3009/search/static/css/main.6ac36ec5.css)
[ "$CSS_STATUS" = "200" ]
print_result $? "CSS accessible avec Chrome User-Agent"

# 5. Test CORS pour les requêtes depuis le frontend
print_info "Test CORS pour les requêtes API..."
CORS_TEST=$(curl -s -I -H "Origin: http://localhost:3009" -H "Access-Control-Request-Method: POST" -X OPTIONS http://localhost:8007/search)
echo "$CORS_TEST" | grep -q "access-control-allow-origin"
print_result $? "CORS configuré pour les requêtes API"

# 6. Test de la configuration nginx
print_info "Test de la configuration nginx..."
NGINX_CONFIG=$(docker exec openedition_frontend cat /etc/nginx/conf.d/default.conf)
echo "$NGINX_CONFIG" | grep -q "\$scheme://\$http_host/search/"
print_result $? "Configuration nginx utilise les variables dynamiques"

# 7. Test des différents chemins d'accès
print_info "Test des différents chemins d'accès..."

# Test racine
ROOT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3009/)
[ "$ROOT_STATUS" = "301" ]
print_result $? "Racine (/) redirige correctement"

# Test /search
SEARCH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3009/search)
[ "$SEARCH_STATUS" = "301" ]
print_result $? "/search redirige vers /search/"

# Test /search/
SEARCH_SLASH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3009/search/)
[ "$SEARCH_SLASH_STATUS" = "200" ]
print_result $? "/search/ accessible"

# 8. Test de performance et cache
print_info "Test de performance et cache..."
CACHE_HEADERS=$(curl -s -I http://localhost:3009/search/static/js/main.8ea54147.js)
echo "$CACHE_HEADERS" | grep -q "Cache-Control.*immutable"
print_result $? "Cache headers optimisés pour les assets"

echo "$CACHE_HEADERS" | grep -qi "expires.*202[6-9]"
print_result $? "Expiration longue durée configurée"

echo ""
echo -e "${GREEN}🎉 Tous les tests de compatibilité Chrome sont passés!${NC}"
echo ""
echo -e "${YELLOW}📋 Diagnostic pour Chrome:${NC}"
echo "   ✅ Redirection dynamique avec \$scheme://\$host"
echo "   ✅ Headers de sécurité présents"
echo "   ✅ Assets statiques accessibles"
echo "   ✅ CORS configuré correctement"
echo "   ✅ Cache optimisé"
echo ""
echo -e "${YELLOW}🔧 Si Chrome ne s'affiche toujours pas:${NC}"
echo "   1. Vider le cache Chrome (Ctrl+Shift+R)"
echo "   2. Vérifier la console développeur (F12)"
echo "   3. Tester en navigation privée"
echo "   4. Vérifier les extensions Chrome qui bloquent"
echo ""
echo -e "${YELLOW}🔗 URLs à tester dans Chrome:${NC}"
echo "   🌐 http://localhost:3009/ (redirige vers /search/)"
echo "   🌐 http://localhost:3009/search/"
echo "   🔧 http://localhost:3007/ (version dev si disponible)"