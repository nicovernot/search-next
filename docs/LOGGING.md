# Stratégie de logs — OpenEdition Search

**Implémentée dans** : `feature/012-logging-strategy`  
**Dernière mise à jour** : 2026-04-22

---

## Vue d'ensemble

Le logging est structuré en deux zones distinctes :

- **Backend FastAPI** : JSON structuré sur stdout via `python-json-logger`, root logger unique, niveaux pilotés par `settings.log_level`.
- **Frontend Next.js** : wrapper `lib/logger.ts`, `console.*` interdit dans le code applicatif.

---

## Backend

### Configuration centrale

Point d'entrée unique : `search_api_solr/app/core/logging.py`.

```python
from app.core.logging import setup_logging, get_logger

setup_logging(settings.log_level)   # appelé une seule fois dans main.py
logger = get_logger(__name__)        # dans chaque module
```

`setup_logging()` configure le **root logger** — tous les modules applicatifs propagent vers lui automatiquement. Il n'est pas nécessaire d'attacher un handler dans chaque fichier.

**Interdit dans les modules métier :**
```python
# ❌ Contourne la configuration centrale
logging.basicConfig(...)
logging.getLogger("uvicorn").error(...)
```

### Format JSON

Chaque ligne de log est un objet JSON :

```json
{
  "timestamp": "2026-04-22T18:46:09Z",
  "severity": "INFO",
  "name": "app.services.search_service",
  "message": "Search completed successfully",
  "context": { "query_length": 12, "result_count": 1420, "duration_ms": 43 }
}
```

Champs systématiques : `timestamp`, `severity`, `name`, `message`.  
Champs métier optionnels : dans `extra={"context": {...}}`.

### Niveaux par environnement

| Niveau | dev | staging | prod |
|--------|-----|---------|------|
| `DEBUG` | ✅ affiché | ❌ silencé | ❌ silencé |
| `INFO` | ✅ | ✅ | ✅ |
| `WARNING` | ✅ | ✅ | ✅ |
| `ERROR` | ✅ | ✅ | ✅ |
| `CRITICAL` | ✅ | ✅ | ✅ |

Le niveau est fixé via `LOG_LEVEL` dans les fichiers Docker Compose :

| Fichier | Valeur |
|---------|--------|
| `docker-compose.dev.yml` | `LOG_LEVEL=DEBUG` |
| `docker-compose.staging.yml` | `LOG_LEVEL=INFO` |
| `docker-compose.prod.yml` | `LOG_LEVEL=INFO` |

Valeur par défaut si absent : `DEBUG` hors prod, `INFO` en prod (via `Settings.set_default_log_level()`).

### Exemples d'usage correct

```python
# Structuré avec contexte métier
logger.info("Search completed", extra={"context": {"result_count": 42, "duration_ms": 38}})

# Erreur avec stack trace
logger.error("Solr HTTP error", extra={"context": {"status_code": 503}}, exc_info=True)

# Debug technique (ne sera pas visible en staging/prod)
logger.debug("Cache HIT for key: %s", cache_key)
```

```python
# ❌ f-string avec donnée sensible
logger.info(f"Auth URL: {url_with_ip_and_token}")

# ✅ endpoint seulement
logger.debug("Calling auth API: %s", settings.auth_api_url)
```

### Données redactées

Les données suivantes ne doivent **jamais** apparaître dans les logs `INFO`/`WARNING`/`ERROR` :

| Donnée | Traitement appliqué |
|--------|---------------------|
| Adresse IP utilisateur | Masquée (`192.168.1.xxx`) via `_mask_ip()`, niveau DEBUG |
| URL auth complète (IP + doc) | Remplacée par l'endpoint seul, niveau DEBUG |
| Réponse JSON de l'API auth | Réduite à `has_username=True/False`, niveau DEBUG |
| URLs des documents utilisateurs | Remplacées par un comptage, niveau DEBUG |
| Réponse token OIDC (`resp.text`) | Remplacée par `resp.status_code` |
| URLs Solr complètes dans les erreurs | Supprimées — seul `status_code` ou `error_type` subsiste |
| URL Redis au démarrage | Supprimée |
| URL Solr complète au démarrage | Remplacée par `hostname/collection` |

Les URLs Solr internes restent visibles au niveau `DEBUG` dans `solr_client.py` (utile en dev, silencées en prod).

---

## Frontend

### Wrapper `lib/logger.ts`

```typescript
import { logger } from "../lib/logger";

logger.debug("message");   // dev uniquement
logger.info("message");    // dev uniquement
logger.warn("message");    // dev + prod
logger.error("message");   // dev + prod
```

**En développement** : tous les niveaux s'affichent dans la console avec le préfixe `[LEVEL]`.  
**En production** : `debug` et `info` sont silencés — seuls `warn` et `error` passent.

### Règles

```typescript
// ❌ Interdit
console.error("Failed", err);              // console.* direct
logger.error("Auth failed", token);        // donnée sensible en argument
logger.error("Error", JSON.stringify(user)); // payload utilisateur

// ✅ Autorisé
logger.error("Failed to load facet config"); // message fixe, pas de données
logger.warn("Retrying after network error"); // signal opérationnel
```

---

## Lire les logs

### En développement (Docker Compose)

```bash
# Logs temps réel de l'API
docker logs search-next_api -f

# Depuis le démarrage, filtrer les erreurs
docker logs search-next_api 2>&1 | grep '"severity":"ERROR"'

# Formater avec jq
docker logs search-next_api 2>&1 | grep '^{' | jq '{t: .timestamp, sev: .severity, name: .name, msg: .message}'
```

### En staging / production

Les logs JSON sont émis sur stdout. L'aggregateur de logs (ELK, Loki, CloudWatch, etc.) les indexe directement.

Requêtes utiles selon l'outil :

```
# Kibana / Elasticsearch
severity: "ERROR" AND name: "app.services.*"

# Loki (LogQL)
{container="search-next_api"} | json | severity="ERROR"

# Grep sur fichier exporté
grep '"severity":"ERROR"' app.log | jq .
```

### Signaux de santé à surveiller

| Signal | Niveau | Logger | Signification |
|--------|--------|--------|---------------|
| `Application startup completed` | INFO | `app.main` | API prête |
| `Redis cache connected successfully` | INFO | `app.services.cache_service` | Cache opérationnel |
| `Solr search timeout` | ERROR | `app.services.solr_client` | Solr lent ou inaccessible |
| `Solr HTTP error` | ERROR | `app.services.solr_client` | Erreur Solr (vérifier `status_code`) |
| `Failed to get organization from auth API` | ERROR | `app.services.docs_permissions_client` | Auth API injoignable |
| `SSO callback error` | WARNING | `app.api.auth` | Échec d'un callback SSO |
