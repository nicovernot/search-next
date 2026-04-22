# Feature Specification: Stratégie de logs applicatifs

**Feature Branch**: `feature/012-logging-strategy`  
**Created**: 2026-04-22  
**Status**: Draft

## Objectif

Établir une stratégie de logs cohérente pour le backend FastAPI, le frontend Next.js et l'exploitation en environnements `development`, `staging` et `production`.

Cette spec couvre :

- l'audit de l'existant ;
- les écarts de maturité entre zones de code ;
- la politique cible de logs ;
- les règles de sécurité et d'observabilité ;
- le plan de mise en œuvre incrémental.

## Audit de l'existant

### 1. Backend FastAPI

Un socle de logging structuré existe déjà dans [`search_api_solr/app/core/logging.py`](/home/nico/projets/search-next/search_api_solr/app/core/logging.py:1) via `python-json-logger`.

Points observés :

- le formatter JSON est défini dans `setup_logging()` ;
- `get_logger(__name__)` est utilisé dans plusieurs services métier (`main.py`, `search_service.py`, `solr_client.py`, `cache_service.py`) ;
- le niveau de log varie déjà selon l'environnement via `settings.log_level` et les fichiers Docker.

### 2. Différenciation dev / staging / prod

La différenciation d'environnement existe partiellement :

- en dev, `uvicorn` est lancé avec `--reload --log-level debug` et `LOG_LEVEL=DEBUG` dans [`docker-compose.dev.yml`](/home/nico/projets/search-next/docker-compose.dev.yml:15) ;
- en staging et prod, `LOG_LEVEL=INFO` est injecté dans [`docker-compose.staging.yml`](/home/nico/projets/search-next/docker-compose.staging.yml:13) et [`docker-compose.prod.yml`](/home/nico/projets/search-next/docker-compose.prod.yml:13) ;
- `Settings.set_default_log_level()` force `DEBUG` hors prod et `INFO` en prod dans [`search_api_solr/app/settings.py`](/home/nico/projets/search-next/search_api_solr/app/settings.py:142).

Conclusion : oui, l'application possède déjà une notion de logs `dev` et `prod`, mais elle n'est pas encore appliquée de manière homogène.

### 3. Frontend Next.js

Le frontend n'a pas de stratégie de logs applicatifs formalisée.

Constat :

- présence de `console.error` ad hoc dans [`front/app/hooks/useSuggestions.ts`](/home/nico/projets/search-next/front/app/hooks/useSuggestions.ts:24) ;
- présence de `console.error` ad hoc dans [`front/app/hooks/useFacetConfig.ts`](/home/nico/projets/search-next/front/app/hooks/useFacetConfig.ts:23) ;
- absence de wrapper dédié (`logger.ts`, instrumentation client, corrélation requête, masquage des données sensibles).

### 4. Points de risque identifiés

#### Risque A — Configuration centrale incomplètement appliquée

Dans [`search_api_solr/app/core/logging.py`](/home/nico/projets/search-next/search_api_solr/app/core/logging.py:19), `setup_logging()` configure le logger `openedition_search`, tandis que `get_logger(name)` retourne un logger de module (`__name__`) sans lui attacher explicitement le handler JSON.  

Conséquence probable : une partie des logs dépend encore du comportement implicite du root logger / d'`uvicorn`, donc le format réel peut varier selon le point d'émission.

#### Risque B — Reconfiguration locale non maîtrisée

[`search_api_solr/app/services/docs_permissions_client.py`](/home/nico/projets/search-next/search_api_solr/app/services/docs_permissions_client.py:18) appelle `logging.basicConfig(level=logging.INFO)` localement.

Conséquence : le module contourne la configuration centrale et peut introduire des formats, niveaux ou doublons différents du reste de l'application.

#### Risque C — Données sensibles ou volumineuses dans les logs

Le module permissions logge actuellement :

- des URLs complètes de requêtes Solr ([`docs_permissions_client.py:28`](/home/nico/projets/search-next/search_api_solr/app/services/docs_permissions_client.py:28)) ;
- l'IP distante ([`docs_permissions_client.py:264`](/home/nico/projets/search-next/search_api_solr/app/services/docs_permissions_client.py:264)) ;
- l'URL d'appel à l'API d'auth ([`docs_permissions_client.py:222`](/home/nico/projets/search-next/search_api_solr/app/services/docs_permissions_client.py:222)) ;
- la réponse JSON complète d'auth ([`docs_permissions_client.py:235`](/home/nico/projets/search-next/search_api_solr/app/services/docs_permissions_client.py:235)).

Ces logs sont utiles en debug, mais trop détaillés pour un fonctionnement nominal en staging/prod.

#### Risque D — Incohérence entre logs backend métier et logs d'infra

Le backend mélange :

- des logs structurés avec `extra={"context": ...}` dans [`search_service.py`](/home/nico/projets/search-next/search_api_solr/app/services/search_service.py:61) et [`solr_client.py`](/home/nico/projets/search-next/search_api_solr/app/services/solr_client.py:37) ;
- des logs texte interpolés (`f"..."`) dans [`main.py`](/home/nico/projets/search-next/search_api_solr/app/main.py:163) et [`env_validation.py`](/home/nico/projets/search-next/search_api_solr/app/core/env_validation.py:91) ;
- des loggers standards non raccordés à la convention applicative (`auth.py`, `ldap_service.py`, `oidc_service.py`).

#### Risque E — Pas de politique frontend explicite

Le frontend utilise `console.error` comme mécanisme de dernier recours mais sans règle :

- quand logger ;
- quoi logger ;
- quoi masquer ;
- quelle différence entre erreur utilisateur, erreur réseau et erreur attendue ;
- comment éviter le bruit en production.

## Décisions de conception

### Décision 1 — Un seul point d'entrée de logging backend

Tout le backend doit passer par une configuration centrale unique :

- initialisation au démarrage de l'application ;
- format JSON sur `stdout` ;
- niveaux pilotés par `settings.log_level` ;
- capture cohérente des loggers applicatifs, `uvicorn`, `fastapi`, `sqlalchemy` et bibliothèques critiques.

`logging.basicConfig()` est interdit dans les modules métier.

### Décision 2 — Politique par environnement

#### Development

- niveau par défaut : `DEBUG` ;
- logs lisibles humainement ou JSON compact acceptable ;
- autorisation de champs de diagnostic supplémentaires ;
- traces d'erreurs complètes ;
- possibilité d'activer explicitement des logs verbeux de dépendances externes.

#### Staging

- niveau par défaut : `INFO` ;
- format identique à la production ;
- traces complètes sur erreurs ;
- pas de données personnelles brutes ;
- utile pour validation de volumétrie et de dashboards.

#### Production

- niveau par défaut : `INFO` ;
- `DEBUG` interdit par défaut ;
- pas de logs contenant IP complète, tokens, credentials, réponses auth complètes, payloads entiers ;
- `WARNING` / `ERROR` orientés action opérateur ;
- logs centrés sur événements métier, erreurs et signaux de santé.

### Décision 3 — Structure minimale obligatoire d'un log backend

Chaque log backend doit pouvoir exposer les champs suivants :

- `timestamp`
- `severity`
- `logger`
- `message`
- `environment`
- `service`
- `request_id` si disponible
- `route` si disponible
- `context` pour les champs métier complémentaires

Les erreurs doivent inclure une stack trace uniquement sur `ERROR` / `CRITICAL`.

### Décision 4 — Politique de redaction

Doivent être masqués, tronqués ou supprimés :

- tokens JWT, sessions, secrets, mots de passe ;
- réponses brutes de l'API d'auth ;
- IP complètes en prod si non indispensables ;
- URLs complètes contenant des paramètres sensibles ;
- payloads complets de recherche si leur taille ou leur sensibilité est élevée.

Bonne pratique :

- préférer `query_length`, `filters_count`, `result_count`, `status_code`, `duration_ms` ;
- préférer un identifiant hashé ou tronqué à une donnée brute.

### Décision 5 — Frontend : logs utilitaires, pas observabilité primaire

Le frontend ne doit pas devenir la source primaire d'observabilité métier.

Politique cible :

- `console.*` interdit dans le code applicatif hors bootstrap/debug explicitement encadré ;
- création d'un wrapper `front/app/lib/logger.ts` ;
- en dev : affichage console autorisé via ce wrapper ;
- en prod : bruit réduit, erreurs normalisées, possibilité de brancher un outil de collecte plus tard ;
- les erreurs API importantes doivent être reflétées côté backend autant que possible.

### Décision 6 — Séparer logs, métriques et traces

Les logs ne remplacent pas :

- les métriques Prometheus déjà exposées via `/metrics` ;
- une future corrélation de traces distribuées.

La stratégie cible est :

- logs pour comprendre un événement ;
- métriques pour mesurer un comportement ;
- traces pour suivre un parcours inter-service.

## Règles à appliquer

### Backend

- utiliser `get_logger(__name__)` ou son successeur unique ;
- bannir `logging.basicConfig()` dans les modules applicatifs ;
- bannir les `f-strings` pour des logs structurés quand le message doit porter du contexte exploitable ;
- privilégier `logger.info("Search completed", extra={...})` à `logger.info(f"...")` ;
- centraliser la gestion des niveaux et handlers ;
- logguer les erreurs au plus près de la frontière technique, éviter le double logging pour une même exception.

### Frontend

- bannir `console.log`, `console.error`, `console.warn` dans les hooks/composants métier ;
- utiliser un wrapper avec niveaux (`debug`, `info`, `warn`, `error`) ;
- ne jamais logger de token, email, réponse auth complète, payload de formulaire sensible ;
- en production, limiter aux erreurs non récupérables ou aux signaux réellement utiles.

## Plan de mise en œuvre

### Phase 1 — Audit durci backend

- recenser tous les points d'émission de logs backend ;
- classer par source : infra, métier, sécurité, debug temporaire ;
- identifier les données sensibles et les doublons.

### Phase 2 — Refactor de la configuration centrale

- rendre la configuration centrale réellement effective pour tous les loggers backend ;
- raccorder `uvicorn` et loggers tiers à la même politique ;
- supprimer les configurations locales (`basicConfig`, handlers locaux).

### Phase 3 — Politique de redaction et de niveaux

- remplacer les logs trop verbeux par des champs dérivés ;
- masquer IP / payloads / réponses auth ;
- réserver `DEBUG` aux diagnostics de développement.

### Phase 4 — Standard frontend

- introduire un wrapper `logger.ts` ;
- remplacer les `console.error` existants ;
- documenter les usages autorisés.

### Phase 5 — Documentation et exploitation

- documenter la stratégie dans `docs/ARCHITECTURE.md` ou une doc dédiée ;
- décrire la table des niveaux et les exemples par environnement ;
- préciser comment lire les logs en Docker et en production.

## Critères d'acceptation

- tous les logs backend applicatifs sortent avec un format homogène ;
- aucun `logging.basicConfig()` ne subsiste dans le code métier ;
- aucun `console.*` non justifié ne subsiste dans le frontend applicatif ;
- les logs prod n'exposent plus de données sensibles brutes ;
- les niveaux `DEBUG` / `INFO` / `WARNING` / `ERROR` sont utilisés de façon cohérente ;
- la stratégie est documentée et exploitable par l'équipe.

## Hors périmètre

- mise en place immédiate d'un collecteur externe type ELK, Loki ou Datadog ;
- traçage distribué complet OpenTelemetry ;
- refonte des métriques Prometheus ;
- dashboards d'exploitation.
