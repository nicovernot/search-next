# Skills opérationnels — OpenEdition Search

**Statut**: référence de pilotage IA
**Mise à jour**: 2026-05-05
**But**: découper les travaux futurs en compétences indépendantes, assignables à un agent IA sans réouvrir tout le contexte projet.

Les specs 001–013 décrivent les fonctionnalités livrées, en cours ou cadrées. Ce fichier décrit les skills à mobiliser pour maintenir, vérifier et étendre le projet.

---

## Règle transversale — Commit uniquement vert

Un commit de code ne doit être créé que si les vérifications requises pour son périmètre passent.

**Gate minimal avant tout commit :**

1. `git diff --check`
2. `cd front && corepack pnpm run lint` si le frontend, les specs frontend ou l'environnement front changent
3. `make test` si le backend, Docker, les contrats API, les modèles ou les specs backend changent
4. `make test-front-ci` si un flux utilisateur, l'auth, la recherche, les facettes, les permissions, les saved searches, l'URL sync, Docker front/API ou `NEXT_PUBLIC_API_URL` changent

**Règle de blocage :**

- Si une commande requise échoue, corriger avant de commit.
- Si l'échec vient d'un prérequis local manquant, utiliser la commande containerisée de référence (`make test`, `make test-front-ci`) avant de conclure.
- Si la suite reste rouge, ne pas commit tant que l'utilisateur n'a pas explicitement demandé un commit malgré tests rouges.
- En cas d'override explicite, le commit doit être annoncé comme dégradé dans la réponse finale avec la commande, le nombre d'échecs et les fichiers/tests concernés.

**État connu au 2026-05-05 :**

- `make test` passe : 98 tests backend.
- `make test-front-ci` est rouge : 40 passed, 26 failed, 2 skipped. Les échecs touchent surtout auth/saved-searches/session, plus quelques scénarios search/url-sync. Tout commit touchant le frontend critique doit d'abord stabiliser cette suite ou obtenir un override explicite.

---

## SKILL 1 — VerifierCohérenceSpecsCodeRésultat

- **Intention** : vérifier que les specs, le planning, le README et `docs/ARCHITECTURE.md` décrivent l'état réel du code.
- **Résultat** : documents synchronisés, statuts cohérents, dette restante planifiée dans `PLANNING.md`.
- **Dépendances** : aucune.
- **Entrées** : `specs/**`, `README.md`, `docs/ARCHITECTURE.md`, structure `front/` et `search_api_solr/`.
- **Sorties** : patch documentaire + liste des écarts code/specs.
- **Tests/vérifications** : `git diff --check`, `rg` ciblés sur les anciens statuts (`P0`, `à faire`, anciens comptes de tests).
- **Points d'attention récurrents** : comptes de tests Playwright (`grep -P "^\s+test\b" front/tests/*.spec.ts | wc -l`), branch active dans `ARCHITECTURE.md`, commit types conventionnels (un commit `docs:` ne doit pas modifier du code ou des tests).

## SKILL 2 — DurcirSécuritéProductionRésultat

- **Intention** : empêcher les configurations dangereuses en production.
- **Résultat** : secrets placeholder refusés, endpoints sensibles neutralisés ou protégés, SSO sans JWT en URL.
- **Dépendances** : specs 006 et 011.
- **Entrées** : `search_api_solr/app/settings.py`, `search_api_solr/app/main.py`, `search_api_solr/app/api/auth.py`, `.env.example`.
- **Sorties** : validations production + tests backend.
- **Tests/vérifications** : tests `Settings` production, tests endpoint `/cache/clear`, tests échange `sso_code`.

## SKILL 3 — VerifierContratsBackendRésultat

- **Intention** : garantir que les endpoints FastAPI exposent des contrats typés et délèguent la logique aux services.
- **Résultat** : `response_model` publics, erreurs Solr typées, services mockables.
- **Dépendances** : spec 006, `TECHNICAL_REQUIREMENTS.md`.
- **Entrées** : `search_api_solr/app/main.py`, `models/search_models.py`, `services/search_service.py`, `services/search_builder.py`.
- **Sorties** : contrats Pydantic stables et tests backend.
- **Tests/vérifications** : `make test`, tests d'erreur Solr, tests `/suggest`.

## SKILL 4 — MaintenirRechercheFrontendRésultat

- **Intention** : préserver la cohérence de la recherche côté UI : état, URL, facettes, permissions, suggestions.
- **Résultat** : hooks ciblés, `SearchContext` assembleur, composants testables.
- **Dépendances** : specs 004, 005, 007.
- **Entrées** : `front/app/context/SearchContext.tsx`, `front/app/hooks/**`, `front/app/lib/search-payload.ts`, `front/app/lib/url-search-state.ts`.
- **Sorties** : patch frontend + tests Playwright ciblés.
- **Tests/vérifications** : `front/tests/search.spec.ts`, `url-sync.spec.ts`, `permissions.spec.ts`.

## SKILL 5 — MaintenirAuthentificationRésultat

- **Intention** : maintenir les trois modes d'authentification sans casser les comptes existants : local, LDAP, SSO.
- **Résultat** : session stable, erreurs traduites, provisioning fédéré fiable.
- **Dépendances** : specs 002 et 011.
- **Entrées** : `front/app/context/AuthContext.tsx`, `front/app/components/AuthModal.tsx`, `front/app/components/LdapLoginForm.tsx`, `search_api_solr/app/api/auth.py`.
- **Sorties** : patch auth + tests auth/LDAP/SSO.
- **Tests/vérifications** : `auth.spec.ts`, `auth-ldap-sso.spec.ts`, tests backend auth si contrat modifié.

## SKILL 6 — NettoyerDetteTechniqueRésultat

- **Intention** : supprimer duplication, code mort, dépendances inutiles et lockfiles concurrents sans changer le comportement.
- **Résultat** : code plus petit, dépendances justifiées, docs mises à jour.
- **Dépendances** : specs 008, 009, 010.
- **Entrées** : `front/package.json`, `front/pnpm-lock.yaml`, `front/app/**`, `search_api_solr/app/**`.
- **Sorties** : patch de nettoyage + note de vérification.
- **Tests/vérifications** : `pnpm run lint`, `make test`, `rg` anti-régression listés dans les specs 008/009/010.

## SKILL 7 — PlanifierReleaseRésultat

- **Intention** : transformer l'état du repo en checklist de release actionnable.
- **Résultat** : `PLANNING.md` à jour avec vérifications, risques acceptés et prochaines actions.
- **Dépendances** : tous les skills de vérification.
- **Entrées** : `git status`, résultats lint/tests, specs et docs.
- **Sorties** : planning de release court, ordonné par priorité.
- **Tests/vérifications** : toutes les commandes de référence documentées ; les impossibilités expliquées ne suffisent pas pour un commit de code sans override explicite.

## SKILL 8 — CadrerRechercheSemantiqueRésultat

- **Intention** : cadrer et préparer la spec 012 (recherche sémantique, catégorisation disciplinaire, API mutualisable) en lien avec les équipes métier et techniques.
- **Résultat** : taxonomie disciplinaire validée, périmètre endpoints publics décidé, prérequis infra identifiés, découpage `Lot 1 / Lot 2` documenté, `tasks.md` maintenu à jour.
- **Dépendances** : spec 012 (`spec.md` + `plan.md`), `TECHNICAL_REQUIREMENTS.md`, specs 001 et 002.
- **Entrées** : `specs/012-semantic-search-api-platform/spec.md`, `plan.md`, `search_api_solr/app/main.py`, `search_api_solr/app/models/search_models.py`, `search_api_solr/app/api/v1/`.
- **Sorties** : `specs/012-semantic-search-api-platform/tasks.md` réaligné, décisions de cadrage enrichissant la section "Decisions Already Recommended" de `plan.md`, priorités de livraison clarifiées.
- **Tests/vérifications** : les documents n'impliquent pas à tort que `/api/v1` ou la sémantique sont déjà livrés ; le Lot 1 est clairement identifié comme prérequis du Lot 2.

## SKILL 9 — VersionnerAPIPubliqueRésultat

- **Intention** : consolider le namespace `/api/v1` partiel et publier un contrat OpenAPI stable pour les usages externes.
- **Résultat** : `/search`, `/suggest`, `/facets/config` déplacés sous `app/api/v1/` avec compatibilité ascendante ; contrat OpenAPI versionné et exportable ; champs documentaires futurs préparés côté contrat.
- **Dépendances** : SKILL 8 (cadrage 012), spec 012 Phase 1, `TECHNICAL_REQUIREMENTS.md` § 3.
- **Entrées** : `search_api_solr/app/main.py`, `search_api_solr/app/api/v1/`, `search_api_solr/app/models/search_models.py`.
- **Sorties** : router `v1` complet, alias de compatibilité, `openapi.json` exporté, tests backend mis à jour, contrat documentaire prêt pour les phases disciplines/sémantique.
- **Tests/vérifications** : `make test`, vérification que les routes racine retournent toujours les bonnes réponses pendant la transition, contrat OpenAPI générable sans erreur.

## SKILL 10 — PréparerContratDisciplinesRésultat

- **Intention** : figer le contrat backend/frontend des disciplines avant l'implémentation de la pipeline d'enrichissement.
- **Résultat** : champs `disciplines`, `discipline_source`, `discipline_confidence`, `semantic_score` ajoutés comme champs optionnels et rétrocompatibles dans les modèles et types.
- **Dépendances** : SKILL 9, spec 012 Phase 1 et Phase 2.
- **Entrées** : `search_api_solr/app/models/document.py`, `search_api_solr/app/models/search_models.py`, `front/app/types.ts`, `front/app/components/ResultItem.tsx`.
- **Sorties** : contrat documentaire stable, frontend compatible, aucune activation prématurée de la sémantique.
- **Tests/vérifications** : tests backend sur les schémas API, vérification que le frontend tolère l'absence de valeurs enrichies.

## SKILL 11 — GarderCommitVertRésultat

- **Intention** : empêcher les commits avec tests requis rouges et rendre le statut qualité vérifiable.
- **Résultat** : commit créé seulement après gate vert, ou absence de commit avec diagnostic court des échecs.
- **Dépendances** : tous les skills touchés par le changement.
- **Entrées** : `git status`, `git diff --stat`, périmètre des fichiers modifiés, résultats des commandes de test.
- **Sorties** : commit propre si gate vert ; sinon liste d'échecs priorisée et prochaines corrections.
- **Tests/vérifications** :
  - Toujours : `git diff --check`
  - Front touché : `cd front && corepack pnpm run lint`
  - Backend/API/Docker touché : `make test`
  - Flux utilisateur critique ou env front/API touché : `make test-front-ci`
- **Règle stricte** : ne pas lancer `git commit` si une vérification requise échoue, sauf demande explicite de l'utilisateur de committer malgré l'échec.
- **Points d'attention récurrents** : distinguer `pnpm run test:e2e` local bloqué par navigateur absent de `make test-front-ci`, qui est la référence containerisée pour Playwright.

## SKILL 12 — StabiliserE2EAuthRechercheRésultat

- **Intention** : remettre la suite Playwright containerisée au vert, en priorité sur les régressions auth/session/saved-searches/search/url-sync.
- **Résultat** : `make test-front-ci` passe, ou les tests réellement externes sont isolés/skippés avec justification stable.
- **Dépendances** : SKILL 4, SKILL 5, SKILL 11.
- **Entrées** : `front/tests/*.spec.ts`, `front/app/context/AuthContext.tsx`, `front/app/components/AuthModal.tsx`, `front/app/components/SavedSearchesPanel.tsx`, `front/app/hooks/useSearchApi.ts`, `front/app/lib/api.ts`, `docker-compose*.yml`, `Makefile`, logs API/frontend.
- **Sorties** : correctifs frontend/backend/env + tests Playwright fiables.
- **Tests/vérifications** : `make test-front-ci` vert ; si auth backend est en cause, `make test` doit rester vert.
- **Points d'attention récurrents** : `NEXT_PUBLIC_API_URL` est figé au build Next.js ; en Docker E2E, le navigateur doit pouvoir appeler une URL publique atteignable, tandis que les route handlers Next.js utilisent `INTERNAL_API_URL`.

## SKILL 14 — AuditerCouvertureTestsRésultat

- **Intention** : s'assurer que chaque spec a une couverture pytest ET Playwright proportionnelle à son risque.
- **Résultat** : table de couverture à jour, tests manquants créés ou planifiés, `make test` vert.
- **Dépendances** : tous les skills de feature (SKILL 1–13).
- **Entrées** : `search_api_solr/tests/`, `front/tests/`, specs `001–014`.
- **Sorties** : nouveaux fichiers de test, table dans `PLANNING.md` § Couverture tests.
- **Tests/vérifications** : `make test` vert, grep `test_` et `test(` pour valider le compte.

### Table de couverture par spec (état 2026-05-20)

| Spec | Pytest | Playwright | Dette |
|---|---|---|---|
| 001 search-core | ✅ Complet (search, builder, suggest, sort, qf) | ⚠ Minimal (2 tests) | Playwright : facettes UI, pagination |
| 002 advanced-search | ⚠ Partiel (config facettes seulement) | ❌ Aucun | Pytest : QueryBuilder logique ; Playwright : mode avancé, AND/OR |
| 004 url-sync | ❌ Aucun | ✅ Complet (18 tests, back/forward, QB restore) | Pytest : helpers `url-search-state.ts` (purs, testables) |
| 005 permissions | ⚠ Basique (4 tests API) | ✅ Complet (4 tests badges) | Pytest : IP proxy, cache permissions |
| 011 auth-ldap-sso | ❌ Aucun | ✅ Complet (41 tests) | Pytest : endpoints auth backend |
| 012 api-platform Ph.1 | ✅ Contrats v1 (test_api_v1.py + test_api_v1_contracts.py) | ⚠ Basique (via hypermedia) | Playwright dédié /api/v1 (dette acceptée) |
| 013 logging | ⚠ Partiel (config env) | ❌ Aucun | Pytest : handlers, format JSON, redaction |
| 014 hypermedia | ✅ Core (9 tests pytest) | ✅ Core (6 tests Playwright) | Playwright : facettes, auth cookie |

### Prompt — AuditerCouvertureTestsRésultat

> Audite la couverture de tests du projet : liste les fichiers `test_*.py` et `*.spec.ts`, déduis les specs couvertes et les lacunes. Mets à jour la table de couverture dans `PLANNING.md` § "Couverture tests". Pour chaque lacune P0 (comportement sans aucun test), crée le fichier de test minimal. Pour les lacunes P1/P2, ajoute une tâche dans le `tasks.md` de la spec concernée.

## Skills complémentaires à créer si le projet grandit

Ces skills ne sont pas encore formalisés en détail, mais deviennent utiles à court terme :

- **StabiliserCIPlaywrightRésultat** : factoriser les commandes E2E, traces, screenshots, variables réseau Docker et prérequis navigateur.
- **MaintenirContratEnvDockerRésultat** : garder cohérents `.env*`, `sync_env.sh`, `docker-compose*.yml`, `Makefile`, ports publics/internes et CORS.
- **AuditerContratsOpenAPIClientRésultat** : comparer `/api/v1/openapi.json`, types frontend et futurs SDKs avant release.
- **GérerMigrationsDonnéesRésultat** : encadrer Alembic/PostgreSQL/pgvector quand les phases disciplines et enrichissements démarrent.

---

## Prompts prêts à l'emploi

### Prompt — VerifierCohérenceSpecsCodeRésultat

> Vérifie la cohérence entre le code actuel, `specs/**`, `README.md`, `docs/ARCHITECTURE.md` et `specs/PLANNING.md`. Corrige les statuts obsolètes, les comptes de tests, les chemins de fichiers, les ports et la dette restante. Ne touche pas au comportement produit sauf si une exigence de sécurité documentée est fausse dans le code. Termine par `git diff --check` et un résumé des écarts corrigés.

### Prompt — DurcirSécuritéProductionRésultat

> Vérifie les exigences de sécurité production : secrets placeholder refusés, `/cache/clear` désactivé en production, SSO sans JWT en query string, route handlers proxy minimaux. Écris ou ajuste les tests avant le code. Mets à jour `specs/PLANNING.md`, `TECHNICAL_REQUIREMENTS.md` et la spec concernée si l'état change.

### Prompt — VerifierContratsBackendRésultat

> Audite les endpoints FastAPI publics. Ajoute ou corrige les `response_model`, les erreurs HTTP stables, et la délégation aux services. Évite `Dict[str, Any]` sur les contrats publics. Ajoute les tests backend ciblés et documente toute commande impossible à lancer.

### Prompt — MaintenirRechercheFrontendRésultat

> Interviens sur la recherche frontend en respectant `SearchContext` assembleur, hooks spécialisés et helpers purs. Toute modification de recherche doit préserver URL sync, permissions, suggestions et facettes. Ajoute ou adapte les tests Playwright ciblés.

### Prompt — MaintenirAuthentificationRésultat

> Interviens sur l'auth locale/LDAP/SSO sans casser les comptes existants. Les erreurs visibles doivent être traduites, les tokens ne doivent pas fuiter dans l'URL, et les tests `auth.spec.ts` + `auth-ldap-sso.spec.ts` doivent couvrir le flux modifié.

### Prompt — NettoyerDetteTechniqueRésultat

> Réduis la dette technique sans changer le comportement : duplication, code mort, dépendances inutiles, lockfiles concurrents, noms opaques. Respecte les specs 008/009/010 et lance les greps de succès associés.

### Prompt — PlanifierReleaseRésultat

> Prépare une checklist release depuis l'état courant du repo. Classe les actions restantes en Release/P1/P2 optionnel, indique les commandes à lancer, les risques acceptés et les fichiers de specs/docs à synchroniser.

### Prompt — CadrerRechercheSemantiqueRésultat

> Prépare le cadrage de la spec 012 : audite les métadonnées disciplinaires disponibles dans les documents Solr, propose une taxonomie restreinte et validable, décide du périmètre des endpoints destinés aux applications tierces (`/api/v1/search`, `/suggest`, `/facets/config`, `/permissions`) et des endpoints à usage interne uniquement. Réaligne `spec.md`, `plan.md` et `tasks.md` autour d'un découpage `Lot 1 = contrat/API` puis `Lot 2 = disciplines + sémantique`. Enrichis la section "Decisions Already Recommended" de `plan.md` avec les décisions de cadrage. Ne commence pas l'implémentation.

### Prompt — VersionnerAPIPubliqueRésultat

> Consolide le namespace `/api/v1` partiel : déplace `/search`, `/suggest` et `/facets/config` depuis `main.py` vers `search_api_solr/app/api/v1/`, en conservant des alias de compatibilité sur les routes racine pendant la transition du frontend. Exporte le contrat OpenAPI (`/api/v1/openapi.json`). Mets à jour les tests backend et vérifie avec `make test`. Ne touche pas à la logique métier ni aux services.

### Prompt — PréparerContratDisciplinesRésultat

> Fige le contrat documentaire cible de la spec 012 avant la pipeline d'enrichissement : ajoute les champs optionnels `disciplines`, `discipline_source`, `discipline_confidence`, `semantic_score` aux modèles backend et aux types frontend, sans activer encore la sémantique ni la facette discipline. Vérifie que l'OpenAPI expose bien ces champs et que le frontend reste rétrocompatible.

### Prompt — GarderCommitVertRésultat

> Avant de committer, déduis les tests requis depuis les fichiers modifiés. Lance `git diff --check`, puis `pnpm run lint`, `make test` et/ou `make test-front-ci` selon le périmètre. Si une vérification requise échoue, ne commit pas : diagnostique les échecs et corrige-les. Ne fais un commit avec tests rouges que si je le demande explicitement.

### Prompt — StabiliserE2EAuthRechercheRésultat

> Remets `make test-front-ci` au vert. Commence par identifier pourquoi les tests auth/session/saved-searches/search/url-sync échouent en Docker : URL API publique embarquée dans Next.js, CORS, appels auth, persistance localStorage, mocks Playwright, ou timing UI. Corrige le plus petit périmètre possible, puis relance `make test-front-ci` et `make test`.

## SKILL 13 — DevelopperFrontendHypermediaHTMX

- **Intention** : construire des interfaces performantes avec HTMX, Alpine.js et Tailwind CSS.
- **Résultat** : rendu côté serveur de fragments HTML, interactivité locale légère, bundle minimal.
- **Dépendances** : spec 014.
- **Entrées** : `search_api_solr/app/templates/hypermedia/`, `search_api_solr/app/api/v1/hypermedia/`.
- **Sorties** : templates Jinja2, fragments HTML, router `hypermedia`.
- **Tests/vérifications** : `make test` (pytest `test_hypermedia.py`), réponses HTML pas JSON, zéro duplication logique Solr.

### Conventions de nommage — module hypermedia

| Élément | Nom |
|---|---|
| Module Python | `app/api/v1/hypermedia/` |
| Templates Jinja2 | `app/templates/hypermedia/` |
| Assets statiques | `app/static/hypermedia/` |
| Route prefix | `/api/v1/hypermedia/` |
| StaticFiles mount | `/static/hypermedia` |
| Tag OpenAPI | `hypermedia` |
| Tests pytest | `tests/test_hypermedia.py` |
| Tests Playwright | `front/tests/hypermedia.spec.ts` |
| IDs HTML | Convention intention→résultat : `#search-results`, `#search-form`, `#loading` |

### Prompt — DevelopperFrontendHypermediaHTMX

> Implémente la vue HTMX pour [fonctionnalité] dans `search_api_solr/app/api/v1/hypermedia/` et `search_api_solr/app/templates/hypermedia/`. Utilise Jinja2 pour les fragments et Alpine.js pour l'état local. Vérifie que les endpoints retournent du HTML (pas du JSON) et que `make test` reste vert (pytest `test_hypermedia.py`). Zéro logique Solr hors des `Services` Python existants. Ajoute les tests Playwright dans `front/tests/hypermedia.spec.ts`.
