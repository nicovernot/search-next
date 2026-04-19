# Planning global des specs

**Audit**: 2026-04-19  
**But**: centraliser l'ordre de traitement, les dépendances et les points de cohérence entre specs.

---

## Planning restant — priorités 2026-04-19

Les fonctionnalités principales sont livrées, mais l'audit code/specs du 2026-04-19 a identifié une dette résiduelle à traiter avant de considérer l'architecture comme stabilisée. Les priorités ci-dessous ordonnent le travail du plus urgent au moins urgent.

### P0 — Sécurité et exposition production

| Ordre | Sujet | Action | Fichiers principaux | Critère de sortie |
|---|---|---|---|---|
| 1 | Endpoint cache non protégé | Protéger `DELETE /cache/clear` par auth admin ou le désactiver hors dev/test | `search_api_solr/app/main.py` | Impossible de vider le cache en production sans autorisation explicite |
| 2 | JWT SSO dans l'URL | Remplacer `?auth_token=<JWT>` par cookie `HttpOnly Secure SameSite=Lax` ou code court à usage unique | `search_api_solr/app/api/auth.py`, `front/app/context/AuthContext.tsx` | Aucun JWT long terme ne transite dans query string |
| 3 | Secrets prod | Refuser le démarrage en production avec secrets par défaut ou configuration fédérée incomplète | `search_api_solr/app/settings.py`, `search_api_solr/app/core/env_validation.py` | `ENVIRONMENT=production` échoue si `SECRET_KEY`, LDAP ou SSO sont mal configurés |
| 4 | Configuration front sensible | Vérifier que `front/.env` ne contient aucun secret serveur et que seules les variables `NEXT_PUBLIC_*` nécessaires y sont exposées | `front/.env`, `front/.env.example` | Aucun secret serveur côté frontend |

### P1 — Contrats API et architecture backend

| Ordre | Sujet | Action | Fichiers principaux | Critère de sortie |
|---|---|---|---|---|
| 5 | `/suggest` trop logique dans l'endpoint | Déplacer parsing Solr + cache dans `SuggestService`, garder l'endpoint comme délégation | `search_api_solr/app/main.py`, `search_api_solr/app/services/search_service.py` | L'endpoint `/suggest` ne contient plus de logique métier |
| 6 | Contrat recherche trop libre | Faire circuler `SearchRequest` typé jusqu'au service/builder au lieu de convertir en `dict[str, Any]` | `search_api_solr/app/main.py`, `search_api_solr/app/services/search_service.py`, `search_api_solr/app/services/search_builder.py` | `SearchBuilder.build_search_url()` accepte un contrat unique typé |
| 7 | Réponses API non typées | Ajouter des modèles Pydantic de réponse pour `/search`, `/suggest`, `/facets/config` | `search_api_solr/app/models/search_models.py`, `search_api_solr/app/main.py` | Les endpoints publics déclarent `response_model` |
| 8 | Gestion erreurs Solr | Remonter les erreurs attendues via exceptions métier ou `HTTPException` stable, sans catch-all 503 trop large | `search_api_solr/app/main.py`, `search_api_solr/app/services/search_service.py`, `search_api_solr/app/services/solr_client.py` | Requêtes invalides = 400, timeout = 503, erreurs inattendues logguées proprement |

### P1 — Cohérence specs/code et tests

| Ordre | Sujet | Action | Fichiers principaux | Critère de sortie |
|---|---|---|---|---|
| 9 | Docs alignées | Maintenir `docs/ARCHITECTURE.md` et les specs qualité synchronisées avec la dette restante | `docs/ARCHITECTURE.md`, `specs/PLANNING.md`, specs `007`-`011` | Les docs distinguent livré fonctionnellement et dette résiduelle |
| 10 | Tests backend non vérifiés localement | Installer/figer l'environnement de test backend puis relancer `pytest` | `search_api_solr/requirements*.txt`, `search_api_solr/pyproject.toml` | `pytest` passe ou les échecs sont documentés avec tickets |
| 11 | Lint front avec warnings | Corriger les warnings `id-length`, `react-hooks/exhaustive-deps`, `<img>` si pertinent | `front/app/**`, `front/tests/**` | `npm run lint` sort sans warning, ou exceptions documentées |

### P2 — Qualité frontend et maintenabilité

| Ordre | Sujet | Action | Fichiers principaux | Critère de sortie |
|---|---|---|---|---|
| 12 | `useSearchApi` trop long | Extraire construction payload, application résultat et déclenchement permissions | `front/app/hooks/useSearchApi.ts`, nouveau module possible dans `front/app/lib/` | Hook plus lisible, idéalement < 120 lignes ou dette justifiée |
| 13 | `useUrlSync` trop dense | Séparer parsing/build URL de la logique React effects | `front/app/hooks/useUrlSync.ts`, nouveau `front/app/lib/url-search-state.ts` | Parsing testable sans monter React |
| 14 | Context search encore monolithique côté consommation | Ajouter des hooks selectors (`useSearchQuery`, `useSearchResults`, etc.) ou contexts séparés | `front/app/context/SearchContext.tsx`, composants consommateurs | Les composants ne consomment que le slice nécessaire |
| 15 | `AuthModal` volumineux | Extraire formulaires local/LDAP/SSO et mapping erreurs si besoin | `front/app/components/AuthModal.tsx` | Composants plus petits, responsabilités UI séparées |

### P3 — Nettoyage et optimisation

| Ordre | Sujet | Action | Fichiers principaux | Critère de sortie |
|---|---|---|---|---|
| 16 | Dépendances frontend inutilisées | Retirer les dépendances non utilisées (`@ai-sdk/*`, Browserbase/Stagehand, `react-markdown`, `zod`) si aucun usage prévu court terme | `front/package.json`, lockfile retenu | Bundle/install plus légers, dépendances justifiées |
| 17 | Deux lockfiles front | Choisir `pnpm` ou `npm` comme gestionnaire unique et supprimer l'autre lockfile | `front/package.json`, `front/pnpm-lock.yaml`, `front/package-lock.json` | Un seul lockfile source de vérité |
| 18 | Lockfile Node dans backend Python | Vérifier l'utilité de `search_api_solr/package-lock.json`, supprimer si orphelin | `search_api_solr/package-lock.json` | Backend sans artefact Node inutile |
| 19 | Commentaires et code mort | Supprimer commentaires obsolètes et méthode morte `execute_query_and_format` commentée | `search_api_solr/app/services/search_builder.py` | Pas de code désactivé sans raison documentée |

### Ordre recommandé d'exécution

1. Traiter P0 en premier, sans attendre les refactors.
2. Relancer lint/test ciblés après chaque correction P0.
3. Faire P1 backend en une branche dédiée, car les contrats API peuvent toucher plusieurs tests.
4. Faire P1 docs/tests juste après P1 backend pour éviter que les specs redeviennent obsolètes.
5. Faire P2 frontend en petits lots indépendants.
6. Faire P3 en dernier, avec un commit séparé de nettoyage.

---

## Synthèse de cohérence

| Sujet | Constat | Action |
|---|---|---|
| Specs livrées | `001`–`011` livrées fonctionnellement | Audit code confirmé 2026-04-19, dette résiduelle planifiée ci-dessus |
| Permissions | `005` complète : badges, proxy IP, fallback `unknown`, tests Playwright verts | ✅ Terminé |
| URL sync | `004` livré : hook useUrlSync, back/forward, QB restore, 19 tests E2E | ✅ Terminé |
| Refactor SearchContext | `007` livré : assembleur 115 lignes, 5 hooks SOLID | ✅ Terminé |
| Qualité code | Fonctionnellement livré, mais critères stricts partiellement dépassés (`useSearchApi`, `useUrlSync`, warnings lint, `Any` backend) | Dette résiduelle planifiée ci-dessus |
| Tech debt `006` | searchFields depuis `/facets/config` livré via `useFacetConfig` | ✅ Terminé |
| Auth LDAP/SSO | `011` livré fonctionnellement, durcissement JWT SSO restant | P0 planifié |
| Architecture doc | `docs/ARCHITECTURE.md` synchronisé avec dette résiduelle | ✅ Aligné |

### Écarts connus

- `useSearchApi.ts` : 197 lignes (SC-003 spec 007 prévoyait max 120 — complexité inhérente aux stale closures)
- `useUrlSync.ts` : 143 lignes (idem — logique de restauration QB + history)
- `SearchContext.tsx` : 115 lignes (SC-002 spec 007 prévoyait max 60, principalement à cause des interfaces slice inline)
- Backend : plusieurs `Dict[str, Any]` restent dans les services autour des contrats Solr
- Sécurité : `DELETE /cache/clear` et callback SSO par query string doivent être durcis avant production
- Vérification : `npm run lint` passe avec warnings ; `pytest` n'a pas pu être validé localement sans dépendances Python installées

---

## État des specs

### ✅ Lots 1, 2, 3 terminés

| Ordre | Spec | Statut | Livraison |
|---|---|---|---|
| 1 | `010-naming-intention-result` | ✅ Livré | commit d5f4946 |
| 2 | `009-dry-kiss-yagni` | ✅ Livré fonctionnellement, nettoyage P2/P3 restant | — |
| 3 | `005-permissions` | ✅ Livré | commit 34cf91e |
| 4 | `007-refactor-search-context` | ✅ Livré fonctionnellement | assembleur 115L, hooks longs en P2 |
| 5 | `008-code-quality-solid` | ✅ Livré fonctionnellement, dette résiduelle planifiée | — |
| 6 | `004-url-sync` | ✅ Livré | commit b0342b8 |
| 7 | `006-tech-debt` | ✅ Livré | searchFields API inclus |
| — | `001/002/003` | ✅ Livré | fonctionnalités core |

### ✅ Lot 4 — Feature auth institutionnelle

| Ordre | Spec | Objectif | Effort | Dépendance |
|---|---|---|---|---|
| 8 | `011-auth-ldap-sso` | ✅ Livré fonctionnellement — durcissement JWT SSO en P0 | ~5j | `002` livrée ✅ |

---

## Démarrage `011-auth-ldap-sso`

### Prérequis vérifiés

- Modèle `User` stable (`002` livrée) ✅
- `lib/api.ts` centralisé (appels auth) ✅
- `useAuthModal` extrait d'`AuthContext` ✅ — pas de refactoring auth UI nécessaire avant de commencer

### Points de vigilance

- La migration DB (colonne `hashed_password` nullable + champ `auth_provider`) doit être faite via Alembic — ne pas modifier `models.py` à la main.
- Conserver les 33+ tests Playwright existants comme garde-fou pendant l'implémentation.
- Tester le fallback "LDAP indisponible" dès la Phase 1 — c'est le cas le plus critique en production.
- `011` peut être développée directement sur `feature/002-advanced-search-suite` ou sur une branche dédiée `feature/011-auth-ldap-sso`.
- Synchroniser `docs/ARCHITECTURE.md` après livraison de `011`.

---

## Définition de terminé

Un lot est terminé quand :

- la spec et son état sont à jour ;
- les tests pertinents ont été lancés ou l'impossibilité est documentée ;
- les points de cohérence dans ce fichier sont mis à jour ;
- aucun changement sans rapport n'a été mélangé au lot.
