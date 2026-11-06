# Phase 1 Data Model: Simplification de la configuration d'environnement

Ce chantier ne manipule pas de données applicatives persistées ; les "entités" ci-dessous sont les objets de configuration que la feature introduit ou fait évoluer.

## Environment (Environnement)

Représente l'une des trois valeurs possibles de la variable sélectrice.

| Champ | Type | Contrainte |
|---|---|---|
| `name` | enum | `development` \| `test` \| `production` — **exactement ces trois valeurs, aucune autre** (FR-001, FR-009) |
| `template_file` | chemin | `.env.development`, `.env.test`, `.env.production` (versionnés, racine du dépôt) |
| `compose_override` | chemin | `docker-compose.dev.yml`, `docker-compose.dev.yml` (test réutilise dev), `docker-compose.prod.yml` — `docker-compose.staging.yml` supprimé |
| `allows_placeholder_secrets` | booléen | `true` pour development/test, `false` pour production (FR-014) |

**Règle de validation** : au démarrage, si la variable `ENVIRONMENT` ne correspond à aucun `name` connu, l'application backend refuse de démarrer avec une erreur explicite (FR-009).

## ConfigVariable (Variable de configuration)

Une ligne de la documentation de référence (FR-006) et du schéma de contrat (`contracts/env-schema.md`).

| Champ | Type | Description |
|---|---|---|
| `key` | string | Nom de la variable, ex. `CORS_ORIGINS` |
| `description` | string | Rôle fonctionnel |
| `consumed_by` | enum[] | `api` \| `frontend` \| `docker-compose` \| `scripts` (un ou plusieurs) |
| `is_public` | booléen | `true` si préfixée `NEXT_PUBLIC_` (exposée au navigateur, inlinée au build en prod) |
| `is_secret` | booléen | `true` pour les identifiants/clés (ex. `SECRET_KEY`, `LDAP_BIND_PASSWORD`, `SSO_OIDC_CLIENT_SECRET`) |
| `required` | booléen | `true` si son absence doit bloquer le démarrage (FR-009) |
| `default_by_environment` | map(Environment → valeur) | Valeur attendue par environnement, y compris pour `CORS_ORIGINS` et `NEXT_PUBLIC_API_URL` |
| `placeholder_value` | string \| null | Pour les variables `is_secret = true` en production, valeur sentinelle détectable (ex. `change-me-in-production`) |

**Inventaire actuel** (53 variables distinctes recensées dans les fichiers existants — liste complète dans `contracts/env-schema.md`), incluant notamment : `ENVIRONMENT`, `NODE_ENV`, `CORS_ORIGINS`, `NEXT_PUBLIC_API_URL`, `API_BASE_URL`, `FRONTEND_URL`, `SOLR_URL`, `SOLR_BASE_URL`, `SOLR_COLLECTION`, `REDIS_URL`, `REDIS_ENABLED`, `DATABASE_URL`, `SECRET_KEY`, `DISABLE_AUTH`, `LDAP_*` (8 variables), `SSO_OIDC_*` (6 variables), `LOG_LEVEL`, `DEBUG`, `AUTO_RELOAD`.

## ActivationState (État d'activation)

Représente le fichier actif à un instant donné sur une machine (poste dev, runner CI, serveur).

| Champ | Type | Description |
|---|---|---|
| `active_environment` | Environment.name | Environnement actuellement activé sur cette machine |
| `root_env_file` | chemin | `.env` (racine, non versionné) — copie du `template_file` de l'environnement actif |
| `front_symlink` | chemin | `front/.env` → `../.env` |
| `api_symlink` | chemin | `search_api_solr/.env` → `../.env` |

**Invariant** : à tout instant, `front_symlink` et `api_symlink` pointent vers le même fichier réel que `root_env_file` — il ne peut pas exister de divergence entre ce que voit le frontend et ce que voit l'API (contrainte qui a été violée dans l'incident de debug ayant motivé cette feature).

**Transition** : l'activation d'un nouvel environnement (via `scripts/use-env.sh <environment>`) remplace intégralement le contenu de `root_env_file` par celui du `template_file` correspondant ; elle ne fusionne pas l'ancien et le nouveau contenu (évite les résidus de configuration d'un environnement précédent).

## DockerServiceCheck (Résultat de vérification Docker)

Sortie du script `scripts/verify_env_docker.sh` (FR-008), un enregistrement par (service, variable critique).

| Champ | Type | Description |
|---|---|---|
| `service` | string | Nom du conteneur Docker (ex. `search-next_api`, `search-next_frontend_dev`) |
| `variable` | string | Nom de la variable vérifiée (sous-ensemble critique : `ENVIRONMENT`, `CORS_ORIGINS`, `NEXT_PUBLIC_API_URL`, `SOLR_URL`/`SOLR_BASE_URL`, `SOLR_COLLECTION`) |
| `expected_value` | string | Valeur lue dans `ActivationState.root_env_file` |
| `actual_value` | string | Valeur lue via `docker exec <service> printenv <variable>` |
| `status` | enum | `MATCH` \| `MISMATCH` \| `MISSING` |

**Règle de sortie** : le script retourne un code de sortie non-nul si au moins un `DockerServiceCheck.status != MATCH`, avec un résumé lisible listant les écarts (SC-004).
