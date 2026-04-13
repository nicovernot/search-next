# Specs — OpenEdition Search

Ce dossier contient les spécifications Spec Kit du projet.

## Structure

```
specs/
├── 001-search-core/           ✅ Implémenté — Recherche de base, facettes, pagination, i18n
│   ├── spec.md
│   ├── plan.md
│   ├── tasks.md
│   └── checklists/
│       └── requirements.md
├── 002-advanced-search-suite/ ✅ Implémenté — Recherche avancée, autocomplétion, comptes, recherches sauvegardées (29 tests E2E verts)
│   ├── spec.md
│   ├── plan.md
│   ├── tasks.md
│   └── checklists/
│       └── requirements.md
├── 003-ux-ui-premium-overhaul/ ✅ Implémenté — Refonte visuelle, dark mode, glassmorphism, animations
│   └── spec.md
├── 004-url-sync/              🔲 Backlog — Sync état ↔ URL, liens partageables, back/forward
│   └── spec.md
├── 005-permissions/           🔲 Backlog — Badges d'accès sur résultats (endpoint existant, intégration incomplète)
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

## Features à spécifier (backlog)

- `004-url-sync` — [Spec](004-url-sync/spec.md) — Synchronisation de l'état de recherche avec l'URL (query params, back/forward, liens partageables)
- `005-permissions` — [Spec](005-permissions/spec.md) — Affichage des droits d'accès sur les résultats (badges open/restricted/institutional via `GET /permissions` — endpoint existant mais service encore partiel)
