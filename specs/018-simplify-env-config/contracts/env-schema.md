# Contrat : schéma des variables d'environnement

Inventaire complet des 53 variables actuellement dispersées sur `.env.shared` / `.env.development` / `.env.test` / `.env.staging` / `.env.production` / `.env.example`, à redistribuer dans les trois nouveaux fichiers modèles autonomes (`.env.development`, `.env.test`, `.env.production`). Ce contrat sert de base à la documentation finale (`docs/ENVIRONMENTS.md`, FR-006) et à la validation backend (FR-009, FR-014).

Légende : 🔒 = secret (jamais de vraie valeur committée) · 🌐 = `NEXT_PUBLIC_*` (exposé navigateur, inliné au build Next.js) · ⚠️ = écart ou incertitude constatée dans l'état actuel, à trancher explicitement pendant l'implémentation (ne pas reconduire silencieusement).

## Sélecteur et cœur applicatif

| Variable | Rôle | Consommé par | dev | test | prod |
|---|---|---|---|---|---|
| `ENVIRONMENT` | Sélecteur d'environnement (FR-001) | api, scripts | `development` | `test` | `production` |
| `NODE_ENV` | Mode Next.js / conventions Node | frontend, api | `development` | `test` | `production` |
| `DEBUG` | Mode debug backend | api | `true` | `true` | `false` |
| `AUTO_RELOAD` | Rechargement auto uvicorn | api | `true` | `false` | `false` |
| `LOG_LEVEL` | Verbosité logs | api | `debug` | `debug` | `info` ⚠️ *(actuellement fixé à `INFO` uniquement au niveau `docker-compose.prod.yml`, pas dans un `.env.*` — à rapatrier dans `.env.production`)* |
| `DISABLE_AUTH` | Désactive l'auth (jamais en prod) | api | `false` | `true` | `false` |
| `DEV` | Active des aides de dev (IP de test) | api | `true` | — | — |

## URLs de service et CORS

| Variable | Rôle | Consommé par | dev | test | prod |
|---|---|---|---|---|---|
| `API_BASE_URL` | URL base API (génération interne) | scripts, api | `http://localhost:8003` | `http://localhost:8007` | `/api` |
| `NEXT_PUBLIC_API_URL` 🌐 | URL API appelée depuis le navigateur | frontend (client) | `http://localhost:8003` | `http://localhost:8007` | `/api` |
| `FRONTEND_URL` | URL publique du front | api (CORS, liens) | `http://localhost:3003` | `http://localhost:3003` | `https://search.openedition.org` |
| `CORS_ORIGINS` | Origines autorisées par le middleware CORS backend | api | `http://localhost:3000,http://localhost:3003,http://127.0.0.1:3000,http://127.0.0.1:3003,http://0.0.0.0:3000,http://0.0.0.0:3003,http://localhost:8003` | *(idem dev)* | ⚠️ **absent de `.env.production` actuel** — hérite aujourd'hui par erreur des origines localhost de `.env.shared` ; DOIT être explicitement défini à `https://search.openedition.org` (et toute autre origine de prod légitime) dans le nouveau `.env.production` |
| `API_PORT` | Port hôte Docker de l'API | docker-compose | `8003` | `8003` | *(non exposé, derrière nginx)* |
| `FRONTEND_PORT` | Port hôte Docker du front | docker-compose | `3003` | `3003` | *(non exposé, derrière nginx)* |
| `POSTGRES_PORT` | Port hôte Docker Postgres | docker-compose | `5435` | `5435` | *(interne)* |
| `REDIS_PORT` | Port hôte Docker Redis | docker-compose | `6376` | `6376` | *(interne)* |

## Solr

| Variable | Rôle | Consommé par | dev | test | prod |
|---|---|---|---|---|---|
| `SOLR_URL` | URL Solr "interne" déclarée | api | `http://localhost:8983/solr` | `http://solr-test:8983/solr` | `http://solr-prod:8983/solr` |
| `SOLR_BASE_URL` | URL Solr distante réellement interrogée par `solr_client.py` (observé en runtime pendant le debug de cette session) | api | `https://solrslave-sec.labocleo.org/solr/documents` | ⚠️ absent de `.env.test` actuel | `https://solrslave-sec.labocleo.org/solr/documents` |
| `SOLR_COLLECTION` | Collection Solr ciblée | api | `searchv2_dev` | `searchv2_test` | `searchv2_prod` |

⚠️ **À vérifier pendant l'implémentation** : le code (`search_api_solr/app/services/solr_client.py`) doit être lu pour confirmer si `SOLR_URL` est réellement utilisé ailleurs (ex. health checks) ou s'il s'agit d'une variable orpheline à documenter comme telle plutôt que reconduire une confusion.

## Redis

| Variable | Rôle | dev / test / prod |
|---|---|---|
| `REDIS_URL` | Connexion Redis | `redis://redis:6379/0` (identique dans les 3 environnements) |
| `REDIS_ENABLED` | Active le cache | `true` |
| `REDIS_TTL_SEARCH` / `REDIS_TTL_SUGGEST` / `REDIS_TTL_PERMISSIONS` | Durées de cache (s) | `300` / `3600` / `1800` |

## Base de données

| Variable | Rôle | dev | test | prod |
|---|---|---|---|---|
| `DATABASE_URL` | Connexion PostgreSQL | `postgresql://search_user:search_password@postgres:5432/search_db` | *(idem dev, ou `TEST_DATABASE_URL` selon le mode de test)* | à définir explicitement (mot de passe réel via secret manager) |
| `TEST_DATABASE_URL` | Base en mémoire pour tests unitaires | — | `sqlite:///:memory:` | — |

## Sécurité / secrets applicatifs 🔒

| Variable | Rôle | dev | test | prod |
|---|---|---|---|---|
| `SECRET_KEY` / `JWT_SECRET` | Signature JWT | valeur par défaut auto-générée si absente (`env_validation.py`, uniquement si `NODE_ENV=development`) | idem dev (auth désactivée) | **placeholder committé** (`change-me-in-production`) → doit être surchargé au déploiement ; détection au démarrage si non surchargé (FR-014) |
| `SESSION_SECRET` | Signature session | *(non requis si auth désactivée)* | *(non requis)* | placeholder committé, mêmes règles que `SECRET_KEY` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Durée de vie du token | `1440` | `1440` | à définir (valeur prod actuelle non documentée — à fixer explicitement) |

## LDAP (désactivé par défaut)

| Variable | Rôle |
|---|---|
| `LDAP_ENABLED` | `false` sauf activation explicite |
| `LDAP_URL`, `LDAP_BASE_DN`, `LDAP_BIND_DN`, `LDAP_BIND_PASSWORD` 🔒, `LDAP_USER_FILTER`, `LDAP_EMAIL_ATTR`, `LDAP_FIRSTNAME_ATTR`, `LDAP_LASTNAME_ATTR`, `LDAP_EMAIL_CONFLICT_STRATEGY` | Valeurs d'exemple dans `.env.example` actuel, à reconduire telles quelles comme placeholders dans les 3 nouveaux fichiers (non secrets par défaut car désactivé) |
| `NEXT_PUBLIC_LDAP_ENABLED` 🌐 | Affichage conditionnel de l'UI LDAP côté front | `true` en test (pour tester l'UI même si le backend renvoie 503), sinon aligné sur `LDAP_ENABLED` |

## SSO OIDC (désactivé par défaut)

| Variable | Rôle |
|---|---|
| `SSO_OIDC_ENABLED` | `false` sauf activation explicite |
| `SSO_OIDC_ISSUER`, `SSO_OIDC_CLIENT_ID`, `SSO_OIDC_CLIENT_SECRET` 🔒, `SSO_OIDC_REDIRECT_URI`, `SSO_OIDC_SCOPES` | Valeurs d'exemple dans `.env.example` actuel, à reconduire comme placeholders |
| `NEXT_PUBLIC_SSO_ENABLED` 🌐 | Affichage conditionnel de l'UI SSO côté front | aligné sur `SSO_OIDC_ENABLED` |

## Divers / tests / performance

| Variable | Rôle | dev | test | prod |
|---|---|---|---|---|
| `TEST_IP` | IP simulée pour les permissions en dev | valeur d'exemple | — | — |
| `TEST_TIMEOUT` / `TEST_RETRIES` | Paramètres des suites de tests | `30000` / `3` | `10000` / `2` | — |
| `RATE_LIMIT` | Limite de requêtes | *(non défini actuellement)* | `10000` (désactivé) | à définir explicitement (valeur "staging" actuelle de `1000` à réévaluer pour la vraie prod) |
| `CACHE_TTL` | TTL cache générique | *(non défini)* | — | à définir explicitement (valeur "staging" actuelle de `1800`/`3600` à confirmer) |
| `WORKER_COUNT` | Nombre de workers uvicorn prod | — | — | `4` |
| `REACT_APP_DEBUG` / `REACT_APP_MOCK_API` | Obsolètes (Create React App) | à retirer ou documenter explicitement comme legacy sans effet sous Next.js |
| `AUTH_API_URL` | URL du service d'auth OpenEdition externe | `https://auth.openedition.org/auth_by_url/` (identique dans les 3 environnements) |

## Note sur les variables dont la valeur "prod" n'existe pas encore

Plusieurs lignes ci-dessus sont marquées ⚠️ parce que la valeur de production actuelle vient en réalité de `.env.staging` (jamais vérifiée en vraie prod) ou est absente. L'implémentation de cette feature DOIT lever ces ambiguïtés avec le mainteneur de l'infrastructure de production avant de finaliser `.env.production`, plutôt que de reconduire silencieusement une valeur de staging comme valeur de prod.

## Valeurs retenues pour `.env.production` (T002)

**Aucun mainteneur infra n'était disponible pendant cette implémentation.** Les valeurs ci-dessous sont des valeurs par défaut sûres et documentées comme telles — **à faire valider explicitement par l'équipe infra avant tout déploiement réel en production** (ce n'est pas une confirmation opérationnelle, seulement un point de départ raisonnable qui ne bloque pas le reste du chantier) :

| Variable | Valeur retenue | Justification |
|---|---|---|
| `CORS_ORIGINS` | `https://search.openedition.org` | Correspond à `FRONTEND_URL` déjà défini pour la production ; corrige l'absence actuelle (héritage involontaire des origines localhost). |
| `LOG_LEVEL` | `info` | Reprend la valeur déjà appliquée par `docker-compose.prod.yml` (`LOG_LEVEL=INFO`), désormais rapatriée dans le fichier d'environnement plutôt que dans le compose. |
| `RATE_LIMIT` | `1000` | Reprend la valeur actuelle de `.env.staging`, seule référence connue supérieure au mode "désactivé" des tests ; **à réévaluer par l'équipe infra selon la charge réelle attendue.** |
| `CACHE_TTL` | `3600` | Reprend la valeur `.env.production` actuelle (la valeur `1800` provient en réalité de `.env.staging`) ; **à confirmer.** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Reprend la valeur commune actuelle (dev/test) faute de valeur de production distincte documentée ; **à réévaluer par l'équipe sécurité pour la prod réelle.**|

Ces cinq valeurs sont reportées dans `.env.production` (T005) avec un commentaire les signalant comme "valeur par défaut à valider par l'infra".
