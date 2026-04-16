# Specs — OpenEdition Search

Ce dossier contient les spécifications Spec Kit du projet.

## Structure

```
specs/
├── 001-search-core/           ✅ Livré — Recherche de base, facettes, pagination, i18n
│   ├── spec.md
│   ├── plan.md
│   ├── tasks.md
│   └── checklists/
│       └── requirements.md
├── 002-advanced-search-suite/ ✅ Livré — Recherche avancée, autocomplétion, comptes, recherches sauvegardées (29 tests E2E verts)
│   ├── spec.md
│   ├── plan.md
│   ├── tasks.md
│   └── checklists/
│       └── requirements.md
├── 003-ux-ui-premium-overhaul/ ✅ Livré — Refonte visuelle, dark mode, glassmorphism, animations
│   └── spec.md
├── 004-url-sync/              🔲 Backlog — Sync état ↔ URL, liens partageables, back/forward (prérequis : 007)
│   └── spec.md
├── 005-permissions/           🔶 Partiel — Badges frontend livrés, proxy IP fiable, fallback unknown et tests Playwright manquants
│   └── spec.md
├── 006-tech-debt/             ✅ Livré — tous les correctifs intégrés (token JWT, HTTP 409, i18n, client API, QB fields depuis config)
│   └── spec.md
├── 007-refactor-search-context/ 🔲 Backlog — Découpage SearchContext en hooks SOLID (prérequis bloquant pour 004)
│   └── spec.md
├── 008-code-quality-solid/    🔲 Backlog — Règles qualité, principes SOLID, checklist de revue de code
│   └── spec.md
├── 009-dry-kiss-yagni/        🔲 Backlog — Audit DRY/KISS/YAGNI, 10 violations identifiées, plan de correction
│   └── spec.md
├── 010-naming-intention-result/ 🔲 Backlog — Principe Intention→Résultat dans les noms, audit complet frontend + backend
│   ├── spec.md
│   ├── plan.md
│   └── tasks.md
└── README.md
```

## Workflow pour une nouvelle feature

```bash
# 1. Constitution (une seule fois, ou si amendement nécessaire)
/speckit.constitution

# 2. Spécification
/speckit.specify
<description de la feature>

# 3. Clarification (optionnel)
/speckit.clarify

# 4. Plan technique
/speckit.plan

# 5. Tâches
/speckit.tasks

# 6. Analyse de cohérence (optionnel)
/speckit.analyze

# 7. Checklist (optionnel)
/speckit.checklist

# 8. Implémentation
/speckit.implement
```

## Backlog priorisé

> Voir `docs/ARCHITECTURE.md` pour le bilan d'audit complet et l'ordre d'implémentation recommandé.
> Voir aussi [`PLANNING.md`](PLANNING.md) pour le planning global consolidé et les points de cohérence entre specs.

| Priorité | Spec | Effort | Prérequis | État |
|----------|------|--------|-----------|------|
| 1 | [006-tech-debt](006-tech-debt/spec.md) — Corrections & fondations techniques | — | — | ✅ Livré |
| 2 | [005-permissions](005-permissions/spec.md) — Badges d'accès sur les résultats | ~2j | 006 ✅ | 🔶 Partiel |
| 3 | [007-refactor-search-context](007-refactor-search-context/spec.md) — Découpage SearchContext SOLID | ~3j | — | 🔲 Backlog |
| 4 | [008-code-quality-solid](008-code-quality-solid/spec.md) — Règles qualité & principes SOLID | continu | 007 | 🔲 Backlog |
| 4 | [009-dry-kiss-yagni](009-dry-kiss-yagni/spec.md) — Audit DRY/KISS/YAGNI, corrections ciblées | ~1j | — | 🔲 Backlog |
| 4 | [010-naming-intention-result](010-naming-intention-result/spec.md) — Nommage Intention→Résultat | ~1j | — | 🔲 Backlog |
| 5 | [004-url-sync](004-url-sync/spec.md) — Liens partageables, back/forward | ~4j | 007 🔲 | 🔲 Backlog |
