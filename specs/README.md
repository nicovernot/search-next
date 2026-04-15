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
├── 004-url-sync/              🔲 Backlog — Sync état ↔ URL, liens partageables, back/forward
│   └── spec.md
├── 005-permissions/           🔲 Backlog — Badges d'accès sur résultats (endpoint backend ✅, UI à créer)
│   └── spec.md
├── 006-tech-debt/             🔲 Backlog — Corrections & fondations : token TTL, client API, champs QB depuis config
│   └── spec.md
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

| Priorité | Spec | Effort | Prérequis |
|----------|------|--------|-----------|
| 1 | [006-tech-debt](006-tech-debt/spec.md) — Token TTL, client API, champs QB depuis config | ~2j | — |
| 2 | [005-permissions](005-permissions/spec.md) — Badges d'accès sur les résultats | ~3j | 006 (client API) |
| 3 | [004-url-sync](004-url-sync/spec.md) — Liens partageables, back/forward | ~4j | 006 (client API) |
