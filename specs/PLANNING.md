# Planning global des specs

**Audit**: 2026-04-19  
**But**: centraliser l'ordre de traitement, les dépendances et les points de cohérence entre specs.

---

## Synthèse de cohérence

| Sujet | Constat | Action |
|---|---|---|
| Specs livrées | `001`–`010` toutes livrées + `004` URL sync | Audit code confirmé 2026-04-19 |
| Permissions | `005` complète : badges, proxy IP, fallback `unknown`, tests Playwright verts | ✅ Terminé |
| URL sync | `004` livré : hook useUrlSync, back/forward, QB restore, 19 tests E2E | ✅ Terminé |
| Refactor SearchContext | `007` livré : assembleur 115 lignes, 5 hooks SOLID | ✅ Terminé |
| Qualité code | `008` P0+P1+P2 livrés, `009` P0+P1+P2 livrés, `010` livré | ✅ Terminé |
| Tech debt `006` | searchFields depuis `/facets/config` livré via `useFacetConfig` | ✅ Terminé |
| Auth LDAP/SSO | `011` ✅ livré — backend, frontend, i18n, tests E2E | Terminé |
| Architecture doc | `docs/ARCHITECTURE.md` à synchroniser | À faire lors du démarrage de `011` |

### Écarts mineurs connus (non bloquants)

- `useSearchApi.ts` : 197 lignes (SC-003 spec 007 prévoyait max 120 — complexité inhérente aux stale closures)
- `useUrlSync.ts` : 143 lignes (idem — logique de restauration QB + history)

---

## État des specs

### ✅ Lots 1, 2, 3 terminés

| Ordre | Spec | Statut | Livraison |
|---|---|---|---|
| 1 | `010-naming-intention-result` | ✅ Livré | commit d5f4946 |
| 2 | `009-dry-kiss-yagni` | ✅ Livré complet P0+P1+P2 | — |
| 3 | `005-permissions` | ✅ Livré | commit 34cf91e |
| 4 | `007-refactor-search-context` | ✅ Livré | assembleur 115L, 5 hooks |
| 5 | `008-code-quality-solid` | ✅ Livré complet P0+P1+P2 | — |
| 6 | `004-url-sync` | ✅ Livré | commit b0342b8 |
| 7 | `006-tech-debt` | ✅ Livré complet | searchFields API inclus |
| — | `001/002/003` | ✅ Livré | fonctionnalités core |

### ✅ Lot 4 — Feature auth institutionnelle

| Ordre | Spec | Objectif | Effort | Dépendance |
|---|---|---|---|---|
| 8 | `011-auth-ldap-sso` | ✅ Livré — backend + frontend + tests E2E | ~5j | `002` livrée ✅ |

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
