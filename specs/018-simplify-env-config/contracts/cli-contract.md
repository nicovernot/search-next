# Contrat CLI : scripts d'activation et de vérification d'environnement

Ces deux scripts sont l'interface que le Makefile, la CI, et les développeurs utilisent pour piloter la configuration. Ce document fixe leur contrat d'entrée/sortie afin que `tasks.md` puisse les implémenter sans ambiguïté.

## `scripts/use-env.sh <environment>`

Remplace `scripts/sync_env.sh` et `scripts/configure_env.sh`.

**Entrée**:
- `<environment>` (argument positionnel obligatoire) ∈ `{development, test, production}`

**Comportement**:
1. Si l'argument est absent ou n'appartient pas aux trois valeurs autorisées → afficher l'usage et les valeurs valides, quitter avec un code non-nul (FR-009).
2. Si `.env.<environment>` (à la racine) n'existe pas → erreur explicite, code non-nul.
3. Copier `.env.<environment>` vers `.env` (racine), en écrasant le contenu précédent (pas de fusion).
4. Créer (ou vérifier l'existence de) `front/.env` en tant que symlink vers `../.env`, idempotent.
5. Créer (ou vérifier l'existence de) `search_api_solr/.env` en tant que symlink vers `../.env`, idempotent.
6. Afficher un résumé : environnement activé, chemins des symlinks, rappel de la commande Docker Compose correspondante.

**Sortie**:
- Code `0` en cas de succès.
- Code non-nul + message d'erreur explicite sur stderr en cas d'échec (argument invalide, fichier modèle manquant).

**Exemples d'appel** (utilisés par le Makefile) :
```bash
scripts/use-env.sh development
scripts/use-env.sh test
scripts/use-env.sh production
```

## `scripts/verify_env_docker.sh [environment]`

Nouveau script (FR-008). `[environment]` optionnel — par défaut, déduit de `ENVIRONMENT` dans le `.env` actif.

**Entrée**:
- `[environment]` optionnel ∈ `{development, test, production}` ; si omis, lu depuis `.env` actif.
- Suppose que les conteneurs Docker pertinents sont démarrés (sinon, erreur explicite listant les conteneurs manquants).

**Comportement**:
1. Lire les valeurs attendues depuis `.env` (racine, fichier actif) pour l'ensemble critique de variables : `ENVIRONMENT`, `CORS_ORIGINS`, `NEXT_PUBLIC_API_URL`, `SOLR_URL`, `SOLR_BASE_URL`, `SOLR_COLLECTION`.
2. Pour chaque service Docker concerné (API, frontend), exécuter `docker exec <service> printenv <variable>` et comparer à la valeur attendue.
3. Produire un tableau récapitulatif `DockerServiceCheck` (service, variable, attendu, obtenu, statut) — voir `data-model.md`.
4. Si l'environnement actif est `production` et qu'un `NEXT_PUBLIC_*` est vérifié, afficher un avertissement rappelant que la valeur runtime ne garantit pas que le build a inliné la bonne valeur (cf. research.md §4) et suggérer `docker compose build` si un doute existe.

**Sortie**:
- Code `0` si tous les `DockerServiceCheck.status == MATCH`.
- Code non-nul si au moins un `MISMATCH` ou `MISSING`, avec le détail des écarts affiché (SC-004 : diagnostic en moins de 2 minutes).

**Exemple d'appel**:
```bash
scripts/verify_env_docker.sh
scripts/verify_env_docker.sh production
```

## Intégration Makefile (contrat d'usage)

Les cibles `make dev`, `make test`, `make prod` (et leurs variantes `-build`/`-down`) appellent `scripts/use-env.sh <environment>` avant de lancer `docker compose`. Les cibles `make staging*` sont retirées. Une nouvelle cible `make env-verify` appelle `scripts/verify_env_docker.sh`.
