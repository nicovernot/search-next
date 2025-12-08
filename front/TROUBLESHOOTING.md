# Diagnostic des erreurs réseau Frontend

## Problème: "NetworkError when attempting to fetch resource"

### Causes possibles et solutions

#### 1. Problème CORS ✅ RÉSOLU
**Solution appliquée:**
- Ajout du middleware CORS dans `app/main.py`
- Configuration: `allow_origins=["*"]`
- Test: `curl -I -X OPTIONS http://localhost:8007/search` → OK

#### 2. URL incorrecte dans le navigateur
**Symptôme:** Vous accédez via `http://127.0.0.1:3009`
**Solution:** Utilisez `http://localhost:3009`
**Raison:** CORS vérifie strictement le domaine (localhost ≠ 127.0.0.1)

#### 3. API non accessible depuis le navigateur
**Test:**
```bash
# Depuis votre machine hôte
curl http://localhost:8007/search \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"query":{"query":"test"},"filters":[],"facets":[],"pagination":{"from":0,"size":5}}'
```
**Résultat attendu:** JSON avec des résultats

#### 4. Vérifier l'URL de l'API dans le build
**Commande:**
```bash
curl -s http://localhost:3009/static/js/main.*.js | grep -o "localhost:[0-9]*"
```
**Résultat attendu:** `localhost:8007`

### Tests de diagnostic

#### Test 1: Vérifier les services
```bash
cd /home/nvernot/projets/searchv2/search_api_solr
docker compose ps
```
Les deux services doivent être "Up" (healthy)

#### Test 2: Tester l'API directement
```bash
curl http://localhost:8007/search \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"query":{"query":"histoire"},"filters":[],"facets":[{"identifier":"platform","type":"list"}],"pagination":{"from":0,"size":10}}'
```

#### Test 3: Vérifier CORS
```bash
curl -I http://localhost:8007/search \
  -X OPTIONS \
  -H "Origin: http://localhost:3009" \
  -H "Access-Control-Request-Method: POST"
```
Doit retourner: `access-control-allow-origin: http://localhost:3009`

#### Test 4: Logs de l'API
```bash
docker compose logs api --tail=20 --follow
```
Puis faire une recherche dans le navigateur et observer les logs.

### Solution rapide

Si le problème persiste:

1. **Reconstruire le frontend avec la bonne URL:**
```bash
cd /home/nvernot/projets/searchv2/search_api_solr
docker compose build frontend
docker compose up -d frontend
```

2. **Vider le cache du navigateur:**
- Chrome/Firefox: Ctrl+Shift+R (rechargement forcé)
- Ou Ctrl+Shift+Delete → Vider le cache

3. **Tester depuis la console du navigateur:**
```javascript
// Dans la console du navigateur (F12)
fetch('http://localhost:8007/search', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    query: {query: "test"},
    filters: [],
    facets: [],
    pagination: {from: 0, size: 10}
  })
})
.then(r => r.json())
.then(console.log)
.catch(console.error)
```

### Vérifications à faire dans le navigateur

1. **Ouvrir:** `http://localhost:3009` (PAS 127.0.0.1)
2. **Console développeur:** F12 → onglet Console
3. **Réseau:** F12 → onglet Network/Réseau
4. **Taper une recherche**
5. **Observer:**
   - Onglet Console: messages d'erreur JavaScript
   - Onglet Network: requête HTTP vers `localhost:8007/search`
   - Statut HTTP: doit être 200, pas 404 ou CORS error

### État actuel ✅

- [x] CORS activé dans l'API
- [x] API répond correctement (testé avec curl)
- [x] Frontend build avec la bonne URL (localhost:8007)
- [x] Les deux services Docker fonctionnent
- [ ] Test depuis le navigateur en attente

### Prochaines étapes

Si l'erreur persiste après:
1. Accès via `http://localhost:3009`
2. Rechargement forcé (Ctrl+Shift+R)
3. Test de la console JavaScript ci-dessus

Alors fournir:
- Capture d'écran de la console (F12)
- Message d'erreur exact
- Onglet Network: détails de la requête HTTP
