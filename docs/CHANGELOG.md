# Changelog

## [2026-04-17] - Correctifs recherche avancée + cohérence multi-environnements

### Recherche avancée (commit `87ccb7c`)

- **Opérateurs QueryBuilder** : `query_logic_parser.py` normalise désormais les opérateurs camelCase envoyés par react-querybuilder (`beginsWith`→`begins_with`, `endsWith`→`ends_with`) via une table `_OPERATOR_ALIASES`. Ajout des branches NOT (`!=`, `doesNotContain`, `doesNotBeginWith`, `doesNotEndWith`).
- **Champ Solr invalide supprimé** : `disciplinary_field → platformIndex_*` retiré de `SEARCH_FIELDS_MAPPING` (backend) et de `QB_LABELS_MAP` / `QB_FIELDS` (frontend) — `platformIndex_*` est un pattern de schéma dynamique Solr, non utilisable comme nom de champ dans les requêtes.
- **Opérateurs UI restreints** : `AdvancedQueryBuilder.tsx` passe désormais `operators={[=, contains, beginsWith, endsWith]}` à react-querybuilder. Avant, ~10 opérateurs non supportés étaient affichés.
- **Champ de recherche par défaut** : `df=naked_titre` (champ tokenisé, boost ×8 dans `qf`) au lieu de `df=titre` (champ brut non analysé) dans `fields_json/common.json`.
- **i18n opérateurs** : clés `qb_opEquals`, `qb_opContains`, `qb_opBeginsWith`, `qb_opEndsWith` ajoutées dans les 6 langues (fr/en/de/es/it/pt).

### Cohérence environnements (commit `87ccb7c`)

- **`CORS_ORIGINS`** : renommage complété dans `env_validation.py` (`cors_allowed_origins` → `cors_origins`), aligné sur `settings.py` et `.env.shared`.
- **`model_config` doublon** : suppression de la déclaration redondante ligne 40 dans `settings.py` (écrasée silencieusement par celle de fin de classe).
- **`.env.test`** : remplacement de `REACT_APP_API_URL` (CRA obsolète) par `NEXT_PUBLIC_API_URL`.
- **`entrypoint.sh`** : nouveau script Docker — attend PostgreSQL (`pg_isready`) puis applique les migrations Alembic avant de démarrer uvicorn. Intégré dans `Dockerfile` et `docker-compose.dev.yml`.
- **Docker Compose** : `docker-compose.prod.yml` et `docker-compose.staging.yml` utilisent `ports: !reset []` / `volumes: !reset []` pour effacer proprement les valeurs héritées ; `docker-compose.yml` ajoute la condition `service_healthy` sur postgres et redis.
- **`sync_env.sh`** : résout `NEXT_PUBLIC_API_URL` depuis les vars chargées plutôt qu'en dur ; ajoute `DATABASE_URL` dans `search_api_solr/.env.local`.

---

## [2026-04-15] - Correction environnement frontend Docker

### Correction

- **Problème** : Le container frontend crashait au démarrage avec `Cannot find module './cjs/react.development.js'`
- **Cause** : Le fichier `front/.env` était absent. Sans lui, Next.js dans le container Docker ne chargeait pas correctement et l'initialisation de node_modules échouait.
- **Solution** : `scripts/sync_env.sh` génère maintenant `front/.env` en plus de `front/.env.local`. Tous les targets `make dev`, `make prod`, `make staging` bénéficient automatiquement de ce fix via `sync-env`.
- **Fichiers modifiés** : `scripts/sync_env.sh`

---

# Changelog - Décembre 2025

## [2025-12-12] - Corrections majeures

### 🔧 Corrections de configuration

#### 1. **Résolution du problème pydantic-settings**
- **Problème** : L'API backend crashait au démarrage avec `SettingsError: error parsing value for field "types_needing_parents"`
- **Cause** : Pydantic-settings tentait de parser les valeurs CSV comme du JSON
- **Solution** : 
  - Changé les types de champs de `List[str]` à `Union[str, List[str]]` dans `settings.py`
  - Mis à jour le validator pour gérer à la fois JSON et CSV
  - Format requis dans `.env` : `types_needing_parents=article,chapter` (CSV, pas JSON)
- **Fichiers modifiés** : 
  - `search_api_solr/app/settings.py`
  - Tous les fichiers `.env*`

#### 2. **Correction des health checks**
- **Problème** : Le container frontend était marqué "unhealthy"
- **Cause** : Le health check utilisait `localhost` qui se résolvait en IPv6, mais nginx écoutait sur IPv4
- **Solution** : Changé `http://localhost/` en `http://127.0.0.1/` dans les health checks
- **Fichiers modifiés** :
  - `docker-compose.yml`
  - `front/Dockerfile`

#### 3. **Résolution du conflit de ports**
- **Problème** : Deux containers frontend essayaient d'utiliser le port 3009
- **Cause** : `openedition_frontend` (prod) et `openedition_frontend_dev` (dev) sur le même port
- **Solution** : Séparation des ports
  - Frontend dev (hot-reload) : **port 3007**
  - Frontend prod (nginx) : **port 3009**
- **Fichiers modifiés** : `docker-compose.dev.yml`

#### 4. **Configuration CORS complète**
- **Problème** : Erreur CORS `Access to fetch from origin 'http://0.0.0.0:3009' has been blocked`
- **Cause** : Origines manquantes dans la configuration CORS
- **Solution** : Ajout de toutes les origines nécessaires
  ```bash
  # Développement
  CORS_ORIGINS=http://localhost:3009,http://localhost:3000,http://localhost:3007,
               http://127.0.0.1:3009,http://127.0.0.1:3000,http://127.0.0.1:3007,
               http://0.0.0.0:3009,http://0.0.0.0:3007
  
  # Test
  CORS_ORIGINS=http://localhost:8007,http://localhost:3009,
               http://127.0.0.1:3009,http://127.0.0.1:8007
  
  # Production (inchangé)
  CORS_ORIGINS=https://search.openedition.org,https://www.openedition.org
  ```
- **Fichiers modifiés** : 
  - `search_api_solr/.env`
  - `search_api_solr/.env.test`

### 📝 Améliorations de la documentation

#### 1. **README.md**
- Mise à jour des ports (3007 pour dev, 3009 pour prod)
- Ajout d'une section détaillée sur la configuration CORS
- Amélioration de la section "Résolution de problèmes" avec :
  - Erreurs CORS
  - Container unhealthy
  - Erreur pydantic-settings
  - Conflit de ports
- Ajout de notes sur le format CSV pour les variables d'environnement

#### 2. **Makefile**
- Suppression de la duplication de la cible `test`
- Vérification que toutes les commandes utilisent des tabulations
- Amélioration des commentaires

### 🏗️ Architecture mise à jour

```
Services disponibles :
├── API Backend (FastAPI)
│   └── Port: 8007 (healthy)
│
├── Frontend Production (nginx)
│   └── Port: 3009 (healthy)
│
└── Frontend Dev (hot-reload)
    └── Port: 3007 (running)
```

### ✅ État des services

Tous les containers sont maintenant **healthy** et fonctionnels :

| Service | Container | Port | Status |
|---------|-----------|------|--------|
| API Backend | `search_api_solr` | 8007 | ✅ healthy |
| Frontend Prod | `openedition_frontend` | 3009 | ✅ healthy |
| Frontend Dev | `openedition_frontend_dev` | 3007 | ✅ running |

### 🔄 Migration

Si vous utilisez une version antérieure, suivez ces étapes :

1. **Mettre à jour les fichiers `.env`**
   ```bash
   # Vérifier que les listes sont au format CSV
   grep "types_needing_parents" search_api_solr/.env
   # Doit afficher: types_needing_parents=article,chapter
   ```

2. **Reconstruire les containers**
   ```bash
   make dev-down
   make dev-build
   ```

3. **Vérifier la santé des services**
   ```bash
   docker ps
   # Tous les containers doivent être "healthy"
   ```

### 📚 Fichiers de configuration

#### Format des variables d'environnement

**✅ Correct (CSV)** :
```bash
types_needing_parents=article,chapter
CORS_ORIGINS=http://localhost:3009,http://localhost:3007
```

**❌ Incorrect (JSON)** :
```bash
types_needing_parents=["article", "chapter"]
CORS_ORIGINS=["http://localhost:3009", "http://localhost:3007"]
```

### 🐛 Bugs corrigés

1. ✅ API backend qui crashait au démarrage (pydantic-settings)
2. ✅ Container frontend marqué "unhealthy"
3. ✅ Conflit de ports entre containers frontend
4. ✅ Erreurs CORS bloquant les requêtes frontend → API
5. ✅ Duplication de cible dans le Makefile

### 🔗 Liens utiles

- API Documentation: http://localhost:8007/docs
- Frontend Production: http://localhost:3009
- Frontend Dev: http://localhost:3007
