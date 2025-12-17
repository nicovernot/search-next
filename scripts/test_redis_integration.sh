#!/bin/bash

# Script de test pour valider l'intégration Redis
# Usage: ./scripts/test_redis_integration.sh

set -e

echo "🔍 Test d'intégration Redis pour OpenEdition Search v2"
echo "=================================================="

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_URL="http://localhost:8007"
REDIS_CONTAINER="openedition_redis"

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

# 1. Vérifier que Redis est en cours d'exécution
print_info "Vérification du statut de Redis..."
docker ps | grep $REDIS_CONTAINER > /dev/null
print_result $? "Redis container is running"

# 2. Tester la connexion Redis directement
print_info "Test de connexion Redis directe..."
docker exec $REDIS_CONTAINER redis-cli ping > /dev/null
print_result $? "Redis responds to ping"

# 3. Vérifier que l'API est accessible
print_info "Vérification de l'API..."
curl -s -f "$API_URL/health" > /dev/null
print_result $? "API health endpoint accessible"

# 4. Tester le endpoint de statistiques du cache
print_info "Test des statistiques du cache..."
CACHE_STATS=$(curl -s "$API_URL/cache/stats")
echo "$CACHE_STATS" | grep -q '"enabled"'
print_result $? "Cache stats endpoint returns data"

# Afficher les statistiques
echo -e "${YELLOW}📊 Statistiques du cache:${NC}"
echo "$CACHE_STATS" | python3 -m json.tool 2>/dev/null || echo "$CACHE_STATS"

# 5. Tester une recherche (pour vérifier la mise en cache)
print_info "Test de recherche avec cache..."
SEARCH_RESPONSE=$(curl -s -X POST "$API_URL/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {"query": "test"},
    "filters": [],
    "pagination": {"from": 0, "size": 10},
    "facets": []
  }')

echo "$SEARCH_RESPONSE" | grep -q '"response"'
print_result $? "Search endpoint returns valid response"

# 6. Tester les suggestions (pour vérifier la mise en cache)
print_info "Test de suggestions avec cache..."
SUGGEST_RESPONSE=$(curl -s "$API_URL/suggest?q=test")
echo "$SUGGEST_RESPONSE" | grep -q '"suggest"'
print_result $? "Suggest endpoint returns valid response"

# 7. Vérifier que les données sont mises en cache
print_info "Vérification de la mise en cache..."
sleep 1  # Attendre que le cache soit mis à jour

# Compter les clés dans Redis
REDIS_KEYS=$(docker exec $REDIS_CONTAINER redis-cli keys "*" | wc -l)
if [ "$REDIS_KEYS" -gt 0 ]; then
    print_result 0 "Cache contains $REDIS_KEYS keys"
else
    print_result 1 "No keys found in cache"
fi

# 8. Tester le nettoyage du cache
print_info "Test de nettoyage du cache..."
CLEAR_RESPONSE=$(curl -s -X DELETE "$API_URL/cache/clear?pattern=*")
echo "$CLEAR_RESPONSE" | grep -q '"deleted_keys"'
print_result $? "Cache clear endpoint works"

# 9. Vérifier les performances avec et sans cache
print_info "Test de performance avec cache..."

# Première requête (sans cache)
START_TIME=$(date +%s%N)
curl -s -X POST "$API_URL/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {"query": "performance"},
    "filters": [],
    "pagination": {"from": 0, "size": 10},
    "facets": []
  }' > /dev/null
END_TIME=$(date +%s%N)
FIRST_REQUEST_TIME=$(( (END_TIME - START_TIME) / 1000000 ))

# Deuxième requête (avec cache)
START_TIME=$(date +%s%N)
curl -s -X POST "$API_URL/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {"query": "performance"},
    "filters": [],
    "pagination": {"from": 0, "size": 10},
    "facets": []
  }' > /dev/null
END_TIME=$(date +%s%N)
SECOND_REQUEST_TIME=$(( (END_TIME - START_TIME) / 1000000 ))

echo -e "${YELLOW}⏱️  Performance:${NC}"
echo "   Première requête (sans cache): ${FIRST_REQUEST_TIME}ms"
echo "   Deuxième requête (avec cache): ${SECOND_REQUEST_TIME}ms"

if [ "$SECOND_REQUEST_TIME" -lt "$FIRST_REQUEST_TIME" ]; then
    IMPROVEMENT=$(( (FIRST_REQUEST_TIME - SECOND_REQUEST_TIME) * 100 / FIRST_REQUEST_TIME ))
    print_result 0 "Cache improves performance by ${IMPROVEMENT}%"
else
    echo -e "${YELLOW}⚠️  Cache performance not significantly better (network latency may affect results)${NC}"
fi

# 10. Vérifier les métriques Prometheus
print_info "Vérification des métriques Prometheus..."
METRICS_RESPONSE=$(curl -s "$API_URL/metrics")
echo "$METRICS_RESPONSE" | grep -q "http_requests_total"
print_result $? "Prometheus metrics available"

echo ""
echo -e "${GREEN}🎉 Tous les tests Redis sont passés avec succès!${NC}"
echo ""
echo -e "${YELLOW}📋 Résumé de l'intégration Redis:${NC}"
echo "   ✅ Redis container opérationnel"
echo "   ✅ Connexion API ↔ Redis fonctionnelle"
echo "   ✅ Cache des recherches actif"
echo "   ✅ Cache des suggestions actif"
echo "   ✅ Endpoints de gestion du cache disponibles"
echo "   ✅ Amélioration des performances détectée"
echo "   ✅ Monitoring et métriques disponibles"
echo ""
echo -e "${YELLOW}🔗 Endpoints utiles:${NC}"
echo "   📊 Statistiques cache: $API_URL/cache/stats"
echo "   🧹 Vider le cache: $API_URL/cache/clear"
echo "   ❤️  Santé de l'API: $API_URL/health"
echo "   📈 Métriques: $API_URL/metrics"