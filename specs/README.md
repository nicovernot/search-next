# Specs — OpenEdition Search

Ce dossier contient les spécifications Spec Kit du projet.

## Structure

```
specs/
├── 001-search-core/        ✅ Implémenté — Recherche de base, facettes, pagination, i18n
│   ├── spec.md
│   ├── plan.md
│   ├── tasks.md
│   └── checklists/
│       └── requirements.md
├── 002-advanced-search-suite/ ✅ Implémenté — Recherche avancée, autocomplétion, comptes, recherches sauvegardées
│   ├── spec.md
│   ├── plan.md
│   ├── tasks.md
│   └── checklists/
│       └── requirements.md
├── 003-ux-ui-premium-overhaul/ ✅ Implémenté — Refonte visuelle, dark mode, animations
│   ├── spec.md
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

- `004-url-sync` — Synchronisation de l'état de recherche avec l'URL (query params)
- `005-permissions` — Affichage des droits d'accès sur les résultats (`GET /permissions`)
