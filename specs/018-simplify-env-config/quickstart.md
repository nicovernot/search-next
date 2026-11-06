# Quickstart : valider la simplification de la configuration d'environnement

Ce guide prouve que la feature fonctionne de bout en bout, une fois implémentée. Détails des scripts et variables : voir [contracts/cli-contract.md](./contracts/cli-contract.md) et [contracts/env-schema.md](./contracts/env-schema.md).

## Prérequis

- Docker et Docker Compose installés
- Dépôt cloné, aucun conteneur `search-next_*` en cours d'exécution avec une configuration d'un chantier antérieur (sinon : `docker compose down`)
- Aucune variable `NEXT_PUBLIC_API_URL` ou `CORS_ORIGINS` exportée dans le shell courant (`unset NEXT_PUBLIC_API_URL CORS_ORIGINS` si un doute, cf. incident de debug ayant motivé cette feature)

## Scénario 1 — Un seul fichier suffit pour démarrer en développement (US1, SC-001, SC-002)

```bash
git clone <repo> && cd search-next
ls .env.development .env.test .env.production   # les 3 modèles existent, aucun .env.shared/.env.example requis
scripts/use-env.sh development
ls -la .env front/.env search_api_solr/.env       # .env est un fichier réel, les deux autres sont des symlinks vers lui
make dev
```

**Résultat attendu** : les conteneurs démarrent, aucune autre commande de synchronisation n'a été nécessaire. Un seul fichier (`.env`) a été édité/consulté.

## Scénario 2 — Bascule d'environnement sans édition manuelle (US1, SC-001)

```bash
scripts/use-env.sh test
cat .env | grep ENVIRONMENT   # ENVIRONMENT=test
scripts/use-env.sh production
cat .env | grep ENVIRONMENT   # ENVIRONMENT=production
```

**Résultat attendu** : à chaque bascule, `.env` reflète intégralement le fichier modèle correspondant (pas de mélange avec l'environnement précédent).

## Scénario 3 — La documentation répond à toute question sur une variable (US2, SC-003)

```bash
grep -A3 "CORS_ORIGINS" docs/ENVIRONMENTS.md
```

**Résultat attendu** : la description, le format et la valeur par environnement de `CORS_ORIGINS` sont trouvés dans ce seul document, sans consulter le code source.

## Scénario 4 — Vérification Docker (US3, SC-004)

```bash
scripts/use-env.sh development
make dev
scripts/verify_env_docker.sh
```

**Résultat attendu** : un tableau confirmant, pour l'API et le frontend, que `CORS_ORIGINS`, `NEXT_PUBLIC_API_URL`, `ENVIRONMENT` et les variables Solr appliquées dans les conteneurs correspondent au `.env` actif. Code de sortie `0`.

### Scénario 4bis — Non-régression de l'incident de debug (SC-005)

```bash
# Rejouer l'ancien bug : une variable de shell obsolète qui, avant cette feature,
# primait silencieusement sur le fichier via la substitution ${CORS_ORIGINS:-...}
# de docker-compose.yml.
export CORS_ORIGINS="http://exemple-obsolete:3003"
docker compose up -d --force-recreate --no-deps api
scripts/verify_env_docker.sh
unset CORS_ORIGINS
```

**Résultat attendu (constaté à l'implémentation)** : `scripts/verify_env_docker.sh` rapporte `MATCH` sur toutes les variables, y compris `CORS_ORIGINS` — la variable de shell exportée n'a **aucun effet** sur le conteneur. C'est un résultat plus fort que "détecter l'écart" : `docker-compose.yml` ne contenant plus aucune substitution `${VAR}` pour ces variables (remplacée par `env_file: .env`), la classe de bug entière (une variable de shell qui prend le pas silencieusement sur le fichier) est structurellement éliminée, pas seulement rendue visible. Si un écart apparaissait malgré tout dans un autre scénario, le script le signalerait en `MISMATCH` avec un code de sortie non-nul.

## Scénario 5 — Rejet d'une valeur d'environnement invalide (FR-009)

```bash
scripts/use-env.sh staging   # ou toute valeur hors development/test/production
```

**Résultat attendu** : le script refuse immédiatement avec un message listant les trois valeurs valides, code de sortie non-nul. Aucun conteneur n'est démarré avec une configuration ambiguë.

## Scénario 6 — Détection d'un secret de production non surchargé (FR-010, FR-014)

```bash
scripts/use-env.sh production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d api
docker logs search-next_api --tail 20
```

**Résultat attendu** : tant que `SECRET_KEY`/`JWT_SECRET`/`SESSION_SECRET` valent encore leur placeholder (`change-me-in-production`), le démarrage de l'API échoue avec un message d'erreur explicite (`env_validation.py`) plutôt que de démarrer silencieusement avec un secret non sécurisé.

## Scénario 7 — Non-régression des suites de tests existantes

```bash
scripts/use-env.sh test
make test
make test-front
```

**Résultat constaté à l'implémentation** :
- `make test` : **148/148 tests passent** (134 existants + 14 nouveaux couvrant FR-009/FR-014 sur `env_validation.py`, cf. T022).
- `make test-front` : **55/68 tests Playwright passent**. Les 13 échecs observés ne sont pas liés à cette feature :
  - Les tests LDAP UI (`auth-ldap-sso.spec.ts`) échouent parce que la cible `make test-front` démarre le service `frontend` (build de type production, `docker-compose.yml` de base) dont les `build.args` ne passent que `NEXT_PUBLIC_API_URL` — `NEXT_PUBLIC_LDAP_ENABLED`/`NEXT_PUBLIC_SSO_ENABLED` n'y sont jamais inlinés, quelle que soit la valeur de `.env.test`. C'est un écart préexistant (indépendant de cette simplification) dans la cible `test-front` du Makefile, à corriger séparément.
  - Les tests dépendant de vrais résultats Solr (`search.spec.ts`, une partie de `saved-searches.spec.ts`) échouent parce que le Solr distant (`solrslave-sec.labocleo.org`) était en panne (503) au moment du test — panne externe déjà diagnostiquée en amont de cette feature (voir historique de la conversation), sans rapport avec la configuration d'environnement.
  - Aucun échec ne concerne CORS, les URLs d'API ou toute variable touchée par cette feature — `make env-verify` confirme une configuration correcte pendant toute la durée du test.
