#!/bin/bash
# Script de test rapide de l'API

echo "🧪 Test de l'API Search Solr"
echo "=============================="
echo ""

# 1. Vérifier que le serveur répond
echo "1️⃣ Test de santé du serveur..."
if curl -s http://localhost:8007/docs > /dev/null 2>&1; then
    echo "   ✅ Serveur accessible sur http://localhost:8007"
else
    echo "   ❌ Serveur non accessible"
    exit 1
fi

# 2. Tester l'endpoint /permissions
echo ""
echo "2️⃣ Test de l'endpoint /permissions..."
RESPONSE=$(curl -s -w "\n%{http_code}" "http://localhost:8007/permissions?urls=https://example.com/doc1" \
    -H "X-Forwarded-For: 127.0.0.1")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ Endpoint /permissions répond (HTTP $HTTP_CODE)"
    echo "   📄 Réponse: $(echo $BODY | jq -c '.' 2>/dev/null || echo $BODY)"
else
    echo "   ⚠️  Endpoint /permissions répond avec HTTP $HTTP_CODE"
    echo "   📄 Réponse: $BODY"
fi

# 3. Tester l'endpoint /search
echo ""
echo "3️⃣ Test de l'endpoint /search..."
SEARCH_DATA='{
  "query": {"query": "test"},
  "filters": [],
  "pagination": {"from": 0, "size": 10},
  "facets": []
}'

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "http://localhost:8007/search" \
    -H "Content-Type: application/json" \
    -d "$SEARCH_DATA")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ Endpoint /search répond (HTTP $HTTP_CODE)"
    echo "   📄 Réponse: $(echo $BODY | jq -c '.' 2>/dev/null || echo $BODY | head -c 100)..."
else
    echo "   ⚠️  Endpoint /search répond avec HTTP $HTTP_CODE"
    echo "   📄 Réponse: $BODY"
fi

# 4. Afficher la documentation
echo ""
echo "📚 Documentation interactive disponible sur:"
echo "   👉 http://localhost:8007/docs"
echo ""
echo "✨ Tests terminés!"
