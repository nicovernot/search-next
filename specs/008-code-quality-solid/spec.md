# Feature Specification: Qualité de Code & Principes SOLID

**Feature Branch**: `feature/008-code-quality-solid` (à créer depuis `main`)
**Created**: 2026-04-16
**Status**: ✅ Livré P0+P1 — useSavedSearches extrait, JSDoc hooks, SC-001/SC-004/SC-005/SC-006 verts

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

## Audit des violations actuelles

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

### Règle 6 — Documentation par l'Intention et le Résultat

Tout nouveau bloc de logique complexe ou composant doit être introduit (en commentaire JSDoc ou dans la PR) par une explication suivant le schéma :
- **Intention** : Ce que le code essaie d'accomplir (ex: "Synchroniser l'état local avec l'URL").
- **Résultat** : L'effet concret attendu (ex: "L'URL est mise à jour avec les filtres encodés sans recharger la page").

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

---

## Backlog de corrections (code existant)

| Priorité | Fichier | Correction | Spec liée |
|---|---|---|---|
| P0 | `SearchContext.tsx` | Découper en 5 hooks | `007` |
| P1 | `SavedSearchesPanel.tsx` | Extraire la logique CRUD dans `useSavedSearches.ts` | `007` |
| P1 | `AdvancedQueryBuilder.tsx` | Déplacer `<style jsx global>` dans `globals.css` | Cette spec |
| P2 | `Facets.tsx` | Rendre le rendu de facette extensible via un prop `renderFacet` | Cette spec |
| P2 | `SearchContextValue` | Segmenter en sous-interfaces par domaine | Cette spec |
| P3 | `ResultItem.tsx` | Externaliser `FORMAT_STYLES` et `configs` comme constantes de module | Cette spec |

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: `grep -rn "await api\." front/app/components/` retourne 0 résultat (aucun appel API dans les composants de présentation).
- **SC-002**: Aucun fichier dans `front/app/hooks/` ne dépasse 120 lignes.
- **SC-003**: `grep -rn ": any" front/app/` (hors `node_modules`) retourne 0 résultat hors adaptateurs tiers documentés.
- **SC-004**: `grep -rn "style jsx global" front/app/components/` retourne 0 résultat.
- **SC-005**: Chaque fichier dans `front/app/hooks/` commence par un commentaire JSDoc décrivant sa responsabilité unique.
- **SC-006**: Les 29 tests Playwright existants restent verts après toutes les corrections.

### Checklist de revue de code

Pour chaque PR touchant `front/app/` :

- [ ] Le composant/hook modifié a une responsabilité unique (peut être décrite en une phrase)
- [ ] Aucun appel `api.*` dans un composant de présentation
- [ ] Aucun `any` introduit sans commentaire justificatif
- [ ] Les nouvelles interfaces sont segmentées (pas de props inutilisées)
- [ ] Les styles sont dans `globals.css` ou des classes Tailwind — pas de `<style>` inline dans les composants
- [ ] Les tests existants passent

---

## Lien avec spec 009

Les principes DRY, KISS et YAGNI sont couverts dans la spec `009-dry-kiss-yagni` qui liste les violations concrètes et le plan de correction. Les deux specs partagent la même checklist de revue de code et doivent être traitées ensemble.

---

## Outils recommandés

| Outil | Usage | Config |
|---|---|---|
| ESLint `@typescript-eslint/no-explicit-any` | Bloquer les `any` | `"error"` dans `.eslintrc` |
| ESLint `react-hooks/exhaustive-deps` | Détecter les stale closures | `"warn"` |
| `madge` | Visualiser les dépendances circulaires entre hooks | `npx madge --circular front/app/hooks/` |
| Playwright | Vérifier les régressions après refactorisation | `npm run test:e2e` |
