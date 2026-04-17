# Planning global des specs

**Audit**: 2026-04-16  
**But**: centraliser l'ordre de traitement, les dépendances et les points de cohérence entre specs.

---

## Synthèse de cohérence

| Sujet | Constat | Action |
|---|---|---|
| Specs livrées | `001`, `002`, `003`, `005`, `006`, `007`, `008` P0+P1, `009` P0+P1, `010` livrées | Cohérent côté specs |
| Permissions | `005` complète : badges, proxy IP, fallback `unknown`, tests Playwright verts (commit 34cf91e) | ✅ Terminé |
| URL sync | `004` dépend de `007` car `SearchContext` est trop central | Garder `004` après le refactor |
| Qualité code | `008`, `009`, `010` se recoupent volontairement | Les traiter comme un chantier de maintenabilité coordonné |
| Planning fichier | Seules `001`, `002` avaient historiquement un `plan.md`; `010` en a maintenant un | Ajouter des `plan.md` dédiés aux autres specs seulement au moment de leur démarrage |
| Architecture doc | `docs/ARCHITECTURE.md` semble plus ancien que les specs `005/006` | À synchroniser lors du prochain passage documentation |

---

## Ordre recommandé

### Lot 1 — Stabilisation rapide

| Ordre | Spec | Objectif | Effort | Dépendance |
|---|---|---|---|---|
| 1 | `010-naming-intention-result` | Renommer les symboles opaques et documenter la règle | ~1j | Aucune |
| 2 | `009-dry-kiss-yagni` | Supprimer duplications et complexité basse/moyenne | ~1j | Aucune |
| 3 | `005-permissions` | ✅ Livré — proxy IP, fallback `unknown`, tests Playwright | ~1j | `006` livrée |

Pourquoi cet ordre : ces trois lots réduisent le bruit et les risques avant le gros refactor `007`, sans bloquer l'application.

### Lot 2 — Refactor structurel

| Ordre | Spec | Objectif | Effort | Dépendance |
|---|---|---|---|---|
| 4 | `007-refactor-search-context` | Extraire les hooks spécialisés de `SearchContext` | ~3j | Stabilisation recommandée |
| 5 | `008-code-quality-solid` | Appliquer les règles SOLID restantes et la checklist durable | continu | `007` recommandé |

Pourquoi cet ordre : `007` crée la structure qui rend `008` beaucoup plus facile à appliquer sans multiplier les retouches.

### Lot 3 — Features à risque plus élevé

| Ordre | Spec | Objectif | Effort | Dépendance |
| --- | --- | --- | --- | --- |
| 6 | `004-url-sync` | Synchroniser query/filtres/page/mode avec l'URL | ~4j | `007` livrée |
| 7 | `011-auth-ldap-sso` | Authentification LDAP + SSO institutionnel (OIDC/SAML/CAS) | ~5j | `002` livrée |

Pourquoi cet ordre : `004` touche le cycle de vie de la recherche et l'historique navigateur. `011` est indépendante de `004` mais suppose le modèle User stable (`002` livrée).

---

## Planning détaillé proposé

| Jour | Travail | Sortie attendue |
|---|---|---|
| J1 | Spec `010` | Renommages frontend/backend, règles documentées, lint warning |
| J2 | Spec `009` P0/P1 | Duplications évidentes supprimées, hooks utilitaires simples créés |
| J3 | Spec `005` ✅ | Permissions robustes, proxy IP, fallback `unknown`, tests Playwright — livré |
| J4-J6 | Spec `007` | `SearchContext` réduit à un assembleur, hooks testables |
| J7 | Spec `008` | Checklist qualité appliquée aux points restants |
| J8-J11 | Spec `004` | URL shareable, back/forward, restauration QueryBuilder, tests E2E |

---

## Points de vigilance avant démarrage

- Vérifier l'état réel du code avant chaque spec : certains éléments listés comme backlog peuvent déjà avoir été partiellement livrés.
- Ne pas mélanger `007` et `004` dans une même PR : les risques de régression seraient difficiles à isoler.
- Conserver les 33 tests Playwright comme garde-fou minimal après chaque lot frontend.
- Synchroniser `docs/ARCHITECTURE.md` après `005` et `007`, pas avant, pour éviter de réécrire la doc deux fois.

---

## Définition de terminé

Un lot est terminé quand :

- la spec et son état sont à jour ;
- les tests pertinents ont été lancés ou l'impossibilité est documentée ;
- les points de cohérence dans ce fichier sont mis à jour ;
- aucun changement sans rapport n'a été mélangé au lot.
