# Skills opérationnels — OpenEdition Search

**Statut**: référence de pilotage IA  
**Mise à jour**: 2026-04-21  
**But**: découper les travaux futurs en compétences indépendantes, assignables à un agent IA sans réouvrir tout le contexte projet.

Les specs 001–011 décrivent les fonctionnalités livrées. Ce fichier décrit les skills à mobiliser pour maintenir, vérifier et étendre le projet.

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
- **Tests/vérifications** : toutes les commandes de référence documentées ou impossibilités expliquées.

## SKILL 8 — CadrerRechercheSemantiqueRésultat

- **Intention** : cadrer et préparer la spec 012 (recherche sémantique, catégorisation disciplinaire, API mutualisable) en lien avec les équipes métier et techniques.
- **Résultat** : taxonomie disciplinaire validée, périmètre endpoints publics décidé, prérequis infra identifiés, `tasks.md` créé pour la Phase 1.
- **Dépendances** : spec 012 (`spec.md` + `plan.md`), `TECHNICAL_REQUIREMENTS.md`, specs 001 et 002.
- **Entrées** : `specs/012-semantic-search-api-platform/spec.md`, `plan.md`, `search_api_solr/app/main.py`, `search_api_solr/app/models/search_models.py`, `search_api_solr/app/api/v1/`.
- **Sorties** : `specs/012-semantic-search-api-platform/tasks.md` Phase 1 + décisions de cadrage enrichissant la section "Decisions Already Recommended" de `plan.md`.
- **Tests/vérifications** : le namespace `/api/v1` est consolidé, les `response_model` publics couvrent tous les endpoints exposés aux tiers, le contrat OpenAPI est publié et versionné.

## SKILL 9 — VersionnerAPIPubliqueRésultat

- **Intention** : consolider le namespace `/api/v1` partiel et publier un contrat OpenAPI stable pour les usages externes.
- **Résultat** : `/search`, `/suggest`, `/facets/config` déplacés sous `app/api/v1/` avec compatibilité ascendante ; contrat OpenAPI versionné et exportable.
- **Dépendances** : SKILL 8 (cadrage 012), spec 012 Phase 1, `TECHNICAL_REQUIREMENTS.md` § 3.
- **Entrées** : `search_api_solr/app/main.py`, `search_api_solr/app/api/v1/`, `search_api_solr/app/models/search_models.py`.
- **Sorties** : router `v1` complet, alias de compatibilité, `openapi.json` exporté, tests backend mis à jour.
- **Tests/vérifications** : `make test`, vérification que les routes racine retournent toujours les bonnes réponses pendant la transition, contrat OpenAPI générable sans erreur.

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

> Prépare le cadrage de la spec 012 : audite les métadonnées disciplinaires disponibles dans les documents Solr, propose une taxonomie restreinte et validable, décide du périmètre des endpoints destinés aux applications tierces (`/api/v1/search`, `/suggest`, `/facets/config`, `/permissions`) et des endpoints à usage interne uniquement. Crée `specs/012-semantic-search-api-platform/tasks.md` pour la Phase 1 (stabilisation API). Enrichis la section "Decisions Already Recommended" de `plan.md` avec les décisions de cadrage. Ne commence pas l'implémentation.

### Prompt — VersionnerAPIPubliqueRésultat

> Consolide le namespace `/api/v1` partiel : déplace `/search`, `/suggest` et `/facets/config` depuis `main.py` vers `search_api_solr/app/api/v1/`, en conservant des alias de compatibilité sur les routes racine pendant la transition du frontend. Exporte le contrat OpenAPI (`/api/v1/openapi.json`). Mets à jour les tests backend et vérifie avec `make test`. Ne touche pas à la logique métier ni aux services.
