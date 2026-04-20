# Feature Specification: Qualité de Code & Principes SOLID

**Feature Branch**: `feature/008-code-quality-solid` (à créer depuis `main`)
**Created**: 2026-04-16
**Status**: ✅ Livré — corrections frontend/backend principales appliquées, règles transverses actives.

> Les écarts bloquants P0/P1/P2 identifiés le 2026-04-19 ont été traités le 2026-04-20. Les éléments restants sont des améliorations opportunistes, pas des bloqueurs de production.

## Overview

Cette spec formalise les piliers de qualité logicielle du projet. Elle repose sur l'application stricte des principes **Clean Code**, **SOLID**, **DRY**, **KISS** et **YAGNI**. 

L'objectif est double :
1. **Robustesse technique** : Minimiser la dette technique et faciliter les évolutions.
2. **Accessibilité IA/Dev** : Rendre le code auto-explicatif pour qu'un développeur humain ou un assistant IA puisse comprendre immédiatement la logique sans ambiguïté.

### Piliers de Qualité (Core Principles)
- **Clean Code** : Code lisible, typage exhaustif, pas de code mort.
- **SOLID** : Responsabilité unique, extensibilité sans modification, inversion des dépendances.
- **DRY/KISS/YAGNI** (voir [spec 009](../009-dry-kiss-yagni/spec.md)) : Pas de duplication, simplicité maximale, pas de sur-ingénierie.
- **Intention → Résultat** (voir [spec 010](../010-naming-intention-result/spec.md)) : Le nommage et la documentation doivent exprimer "Pourquoi ?" et "Quoi ?".

L'objectif n'est pas la perfection académique mais la **maintenabilité pratique** : chaque violation listée ici a un impact mesurable sur la capacité à faire évoluer le code sans régression.

---

## État réel au 2026-04-20

Les corrections prévues par cette spec sont livrées : logique déplacée dans des hooks/services, styles globaux sortis des composants, helpers réutilisables créés, état modal auth sorti d'`AuthContext`, contrats backend typés et endpoints sensibles durcis.

Écarts restants acceptés :

| Domaine | Écart restant | Décision |
|---|---|---|
| Frontend hooks | `useSearchApi` reste >120 lignes | Accepté : orchestration sensible à stale closures, helpers extraits |
| Interface segregation | Certains composants consomment encore `useSearch()` global | Hooks selectors disponibles ; migration opportuniste lors des prochaines touches |
| Vérification locale | `pytest` indisponible dans l'environnement Codex courant | Utiliser `make test` ou installer l'env Python projet |

## Audit historique des violations

Cette section conserve l'audit initial. Elle décrit les problèmes qui ont motivé la spec ; plusieurs lignes sont maintenant résolues ou partiellement résolues.

### S — Single Responsibility Principle

| Fichier | Violation | Impact |
|---|---|---|
| `SearchContext.tsx` | Gère search + permissions + suggestions + config + saved-search restore | Impossible à tester unitairement, tout changement risque de casser une autre responsabilité |
| `SavedSearchesPanel.tsx` | Mélange UI, CRUD API, gestion de position du dropdown portal | Un bug de positionnement oblige à lire la logique CRUD et vice-versa |
| `AdvancedQueryBuilder.tsx` | Contient le style CSS global (`<style jsx global>`) en plus de la logique UI | Les styles devraient être dans `globals.css` ou un fichier dédié |

### O — Open/Closed Principle

| Fichier | Violation | Impact |
|---|---|---|
| `Facets.tsx` / `FacetGroup.tsx` | Ajouter un nouveau type de facette (ex: range, date picker) nécessite modifier les composants existants | Chaque nouvelle facette = risque de régression sur les facettes existantes |
| `ResultItem.tsx` | `FORMAT_STYLES` est un Record statique — ajouter un format nécessite modifier le composant | Devrait être configurable depuis l'extérieur |

### L — Liskov Substitution Principle

Pas de violation identifiée — pas d'héritage de classes dans le codebase React/TypeScript.

### I — Interface Segregation Principle

| Fichier | Violation | Impact |
|---|---|---|
| `SearchContextValue` (interface) | Les composants qui n'ont besoin que de `query` et `results` reçoivent aussi `permissions`, `organization`, `facetConfig`, etc. | Couplage fort — un composant simple dépend de l'interface entière |
| `ResultItem` props | Reçoit `permissionInfo` et `loadingPermissions` même si les permissions sont désactivées | Devrait accepter ces props comme optionnelles avec un comportement par défaut |

### D — Dependency Inversion Principle

| Fichier | Violation | Impact |
|---|---|---|
| `SearchContext.tsx` | Importe directement `api` depuis `../lib/api` — dépend d'une implémentation concrète | Impossible de mocker les appels API dans des tests unitaires sans intercepter `fetch` |
| `SavedSearchesPanel.tsx` | Même problème — `api.getSavedSearches`, `api.createSavedSearch`, `api.deleteSavedSearch` appelés directement | Tests unitaires du composant nécessitent un mock global de `fetch` |

---

## Requirements

### Functional Requirements

- **FR-001**: Chaque hook et composant DOIT avoir une responsabilité unique, documentée en une phrase dans un commentaire JSDoc en tête de fichier.
- **FR-002**: Les composants UI DOIT recevoir leurs données via props ou contexte — aucun appel `api.*` direct dans un composant de présentation.
- **FR-003**: Les appels API DOIVENT être isolés dans des hooks (`useSearchApi`, `useSuggestions`, etc.) ou des services — jamais dans des composants feuilles.
- **FR-004**: Les interfaces TypeScript DOIVENT être segmentées par domaine d'usage — un composant ne doit pas dépendre d'une interface plus large que ce qu'il consomme.
- **FR-005**: Tout nouveau composant DOIT être fermé à la modification pour l'ajout de variantes — utiliser des props de configuration ou des slots React plutôt que des conditions `if/switch` internes.
- **FR-006**: Les styles globaux DOIVENT être dans `globals.css` — aucun `<style jsx global>` dans les composants.

### Non-Functional Requirements

- **NFR-001**: Chaque hook extrait (spec 007) DOIT être testable via `renderHook` sans dépendance à `fetch` réel.
- **NFR-002**: La couverture de types TypeScript DOIT être exhaustive — `any` interdit sauf dans les adaptateurs de librairies tierces (ex: `react-querybuilder` schema).
- **NFR-003**: Aucune duplication de logique entre `SearchContext` et les composants — la logique métier vit dans les hooks, les composants ne font que l'afficher.

---

## Règles de contribution (à appliquer dès maintenant)

### Règle 1 — Un hook = une responsabilité

Chaque hook doit pouvoir être décrit en une seule phrase. Si la description contient "et", c'est un signal de découpage.

```
✅ usePermissions.ts  → uniquement : fetch /permissions, mapper la réponse, exposer l'état
❌ usePermissions.ts  → fetch /permissions + gérer le cache + déclencher la recherche
```

### Règle 2 — Composants de présentation sans appels API

```
✅ SavedSearchesPanel reçoit { searches, onSave, onDelete, onLoad } en props
❌ SavedSearchesPanel appelle api.getSavedSearches() directement
```

### Règle 3 — Interfaces segmentées

```typescript
// ✅ Interfaces ciblées
interface SearchResultsProps { results: SearchDoc[]; total: number; loading: boolean; }
interface SearchFiltersProps { filters: Filters; addFilter: ...; removeFilter: ...; }

// ❌ Interface monolithique passée partout
interface SearchContextValue { /* 20 propriétés */ }
```

### Règle 4 — Extension par configuration, pas par modification

```typescript
// ✅ Ouvert à l'extension
<AccessBadge status={status} config={BADGE_CONFIG[status]} />

// ❌ Fermé — ajouter un statut = modifier le composant
if (status === 'open') return <LockOpen />
else if (status === 'institutional') return <Building2 />
// ...
```

### Règle 5 — Pas de `any` sauf adaptateurs tiers

```typescript
// ✅ Acceptable — adaptateur react-querybuilder
function ValueEditor(props: ValueEditorProps) { ... }

// ❌ Interdit
const data = await res.json() as any;
```

### Règle 6 — Documentation par l'Intention et le Résultat

Tout nouveau bloc de logique complexe ou composant doit être introduit (en commentaire JSDoc ou dans la PR) par une explication suivant le schéma :
- **Intention** : Ce que le code essaie d'accomplir (ex: "Synchroniser l'état local avec l'URL").
- **Résultat** : L'effet concret attendu (ex: "L'URL est mise à jour avec les filtres encodés sans recharger la page").

---

## Backlog de corrections (code existant)

| Priorité | Fichier | Correction | État |
|---|---|---|---|
| P0 | `SearchContext.tsx` | Découper en hooks | ✅ Livré fonctionnellement via spec `007` |
| P1 | `SavedSearchesPanel.tsx` | Extraire la logique CRUD dans `useSavedSearches.ts` | ✅ Livré |
| P1 | `AdvancedQueryBuilder.tsx` | Déplacer `<style jsx global>` dans `globals.css` | ✅ Livré |
| P2 | `Facets.tsx` / `FacetGroup.tsx` | Rendre les variantes de facette plus extensibles si nouveau type ajouté | À traiter seulement si nouveau type de facette |
| P2 | `SearchContextValue` | Segmenter les interfaces et réduire la consommation globale | ✅ Interfaces + hooks selectors livrés ; adoption composants opportuniste |
| P3 | `ResultItem.tsx` | Externaliser/clarifier les configs de rendu si extension fréquente | À traiter si ajout de formats |

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: `grep -rn "await api\." front/app/components/` retourne 0 résultat (aucun appel API dans les composants de présentation).
- **SC-002**: Aucun fichier dans `front/app/hooks/` ne dépasse 120 lignes. **Atteint sauf exception acceptée `useSearchApi` (orchestration recherche).**
- **SC-003**: `grep -rn ": any" front/app/` (hors `node_modules`) retourne 0 résultat hors adaptateurs tiers documentés.
- **SC-004**: `grep -rn "style jsx global" front/app/components/` retourne 0 résultat.
- **SC-005**: Chaque fichier dans `front/app/hooks/` commence par un commentaire JSDoc décrivant sa responsabilité unique.
- **SC-006**: Les tests Playwright existants restent verts après toutes les corrections. **66 tests à relancer dans l'environnement cible avant release.**

### Checklist de revue de code

> Checklist canonique dans [`../TECHNICAL_REQUIREMENTS.md` — section 4](../TECHNICAL_REQUIREMENTS.md#4-qualité-de-code).

---

## Lien avec spec 009

Les principes DRY, KISS et YAGNI sont couverts dans la spec `009-dry-kiss-yagni` qui liste les violations concrètes et le plan de correction. Les deux specs partagent la même checklist de revue de code et doivent être traitées ensemble.

---

## Outils recommandés

| Outil | Usage | Config |
|---|---|---|
| ESLint `@typescript-eslint/no-explicit-any` | Bloquer les `any` | Inclus via `eslint-config-next/typescript` — à passer en `"error"` dans `eslint.config.js` pour enforcement strict |
| ESLint `react-hooks/exhaustive-deps` | Détecter les stale closures | Actif en `warn` via `eslint-config-next` (pas de config supplémentaire nécessaire) |
| `madge` | Visualiser les dépendances circulaires entre hooks | `npx madge --circular front/app/hooks/` (non installé — via npx) |
| Playwright | Vérifier les régressions après refactorisation | `pnpm run test:e2e` |
