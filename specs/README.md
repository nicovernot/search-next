# Specs — OpenEdition Search

Ce dossier contient les spécifications Spec Kit du projet.

La référence centrale des exigences techniques transverses est [`TECHNICAL_REQUIREMENTS.md`](TECHNICAL_REQUIREMENTS.md). Les specs `008`, `009` et `010` en sont les déclinaisons opérationnelles pour la qualité, la simplicité et le nommage.

L'historique des lots livrés est dans [`CHANGELOG.md`](CHANGELOG.md).

## Structure

```
specs/
├── TECHNICAL_REQUIREMENTS.md  📌 Référence canonique — exigences techniques transverses
├── PLANNING.md                📌 Planning global — ordre, dépendances, cohérence
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
├── 005-permissions/           🔶 Partiel — Proxy IP + fallback livrés, tests Playwright manquants
│   └── spec.md
├── 006-tech-debt/             ✅ Livré — tous les correctifs intégrés (token JWT, HTTP 409, i18n, client API, QB fields depuis config)
│   └── spec.md
├── 007-refactor-search-context/ 🔲 Backlog — Découpage SearchContext en hooks SOLID (prérequis bloquant pour 004)
│   └── spec.md
├── 008-code-quality-solid/    🔲 Backlog — Règles qualité, principes SOLID, checklist de revue de code
│   └── spec.md
├── 009-dry-kiss-yagni/        ✅ Livré P0+P1 — violations corrigées ; P2 après spec 007
│   └── spec.md
├── 010-naming-intention-result/ ✅ Livré — renommages frontend + backend appliqués
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
> Voir [`TECHNICAL_REQUIREMENTS.md`](TECHNICAL_REQUIREMENTS.md) pour les exigences techniques applicables à toutes les specs.

| Priorité | Spec | Effort | Prérequis | État |
|----------|------|--------|-----------|------|
| 1 | [006-tech-debt](006-tech-debt/spec.md) — Corrections & fondations techniques | — | — | ✅ Livré |
| 2 | [005-permissions](005-permissions/spec.md) — Badges d'accès sur les résultats | ~2j | 006 ✅ | 🔶 Partiel |
| 3 | [007-refactor-search-context](007-refactor-search-context/spec.md) — Découpage SearchContext SOLID | ~3j | — | 🔲 Backlog |
| 4 | [008-code-quality-solid](008-code-quality-solid/spec.md) — Règles qualité & principes SOLID | continu | 007 | 🔲 Backlog |
| 4 | [009-dry-kiss-yagni](009-dry-kiss-yagni/spec.md) — Audit DRY/KISS/YAGNI, corrections ciblées | ~1j | — | ✅ Livré P0+P1 |
| 4 | [010-naming-intention-result](010-naming-intention-result/spec.md) — Nommage Intention→Résultat | ~1j | — | ✅ Livré |
| 5 | [004-url-sync](004-url-sync/spec.md) — Liens partageables, back/forward | ~4j | 007 🔲 | 🔲 Backlog |
