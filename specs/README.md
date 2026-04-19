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
├── 002-advanced-search-suite/ ✅ Livré — Recherche avancée, autocomplétion, comptes, recherches sauvegardées (33 tests E2E documentés)
│   ├── spec.md
│   ├── plan.md
│   ├── tasks.md
│   └── checklists/
│       └── requirements.md
├── 003-ux-ui-premium-overhaul/ ✅ Livré — Refonte visuelle, dark mode, glassmorphism, animations
│   └── spec.md
├── 004-url-sync/              ✅ Livré — Sync état ↔ URL, liens partageables, back/forward
│   └── spec.md
├── 005-permissions/           ✅ Livré — Badges, proxy IP, fallback unknown, tests Playwright (4 tests dédiés, 33 tests E2E au total)
│   └── spec.md
├── 006-tech-debt/             ✅ Livré — tous les correctifs intégrés (token JWT, HTTP 409, i18n, client API, QB fields depuis config)
│   └── spec.md
├── 007-refactor-search-context/ ✅ Livré fonctionnellement — hooks SOLID, dette P2 sur seuils de taille
│   └── spec.md
├── 008-code-quality-solid/    ✅ Livré fonctionnellement — dette résiduelle suivie dans PLANNING
│   └── spec.md
├── 009-dry-kiss-yagni/        ✅ Livré fonctionnellement — nettoyage restant P2/P3
│   └── spec.md
├── 010-naming-intention-result/ ✅ Livré — renommages frontend + backend appliqués
│   ├── spec.md
│   ├── plan.md
│   └── tasks.md
├── 011-auth-ldap-sso/         ✅ Livré fonctionnellement — durcissement SSO/JWT restant P0
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

> Voir [`PLANNING.md`](PLANNING.md) pour le planning opérationnel courant. Il est la source de vérité pour la dette restante P0/P1/P2/P3.
> Voir `docs/ARCHITECTURE.md` pour le bilan d'audit complet.
> Voir [`TECHNICAL_REQUIREMENTS.md`](TECHNICAL_REQUIREMENTS.md) pour les exigences techniques applicables à toutes les specs.

| Priorité | Spec | Effort | Prérequis | État |
|----------|------|--------|-----------|------|
| P0 | Sécurité production — cache clear, JWT SSO, secrets prod, `.env` front | court | — | 🔥 À faire |
| P1 | Contrats API/backend — `/suggest`, `SearchRequest`, response models, erreurs Solr | moyen | P0 | 🔶 À faire |
| P1 | Cohérence docs/tests — architecture, pytest backend, lint warnings | court | P0/P1 backend | 🔶 À faire |
| P2 | Maintenabilité frontend — `useSearchApi`, `useUrlSync`, selectors SearchContext, `AuthModal` | moyen | P1 | 🔵 À faire |
| P3 | Nettoyage — dépendances, lockfiles, code mort/commentaires | court | P2 ou indépendant | ⚪ À faire |
