# Specs — OpenEdition Search

Ce dossier contient les spécifications Spec Kit du projet.

La référence centrale des exigences techniques transverses est [`TECHNICAL_REQUIREMENTS.md`](TECHNICAL_REQUIREMENTS.md). Les specs `008`, `009` et `010` en sont les déclinaisons opérationnelles pour la qualité, la simplicité et le nommage.

L'historique des lots livrés est dans [`CHANGELOG.md`](CHANGELOG.md).
Les compétences opérationnelles pour piloter les prochaines itérations IA sont dans [`SKILLS.md`](SKILLS.md).

## Structure

```
specs/
├── TECHNICAL_REQUIREMENTS.md  📌 Référence canonique — exigences techniques transverses
├── PLANNING.md                📌 Planning global — ordre, dépendances, cohérence
├── SKILLS.md                  📌 Skills opérationnels IA — vérification, sécurité, release
├── 001-search-core/           ✅ Livré — Recherche de base, facettes, pagination, i18n
│   ├── spec.md
│   ├── plan.md
│   ├── tasks.md
│   └── checklists/
│       └── requirements.md
├── 002-advanced-search-suite/ ✅ Livré — Recherche avancée, autocomplétion, comptes, recherches sauvegardées (68 tests E2E documentés au total)
│   ├── spec.md
│   ├── plan.md
│   ├── tasks.md
│   └── checklists/
│       └── requirements.md
├── 003-ux-ui-premium-overhaul/ ✅ Livré — Refonte visuelle, dark mode, glassmorphism, animations
│   └── spec.md
├── 004-url-sync/              ✅ Livré — Sync état ↔ URL, liens partageables, back/forward
│   └── spec.md
├── 005-permissions/           ✅ Livré — Badges, proxy IP, fallback unknown, tests Playwright (4 tests dédiés)
│   └── spec.md
├── 006-tech-debt/             ✅ Livré — tous les correctifs intégrés (token JWT, HTTP 409, i18n, client API, QB fields depuis config)
│   └── spec.md
├── 007-refactor-search-context/ ✅ Livré — hooks SOLID, helpers extraits, dette de taille acceptée/documentée
│   └── spec.md
├── 008-code-quality-solid/    ✅ Livré — règles qualité appliquées, dette résiduelle optionnelle documentée
│   └── spec.md
├── 009-dry-kiss-yagni/        ✅ Livré — duplications majeures, lockfiles et dépendances nettoyés
│   └── spec.md
├── 010-naming-intention-result/ ✅ Livré — renommages frontend + backend appliqués
│   ├── spec.md
│   ├── plan.md
│   └── tasks.md
├── 011-auth-ldap-sso/         ✅ Livré — LDAP/SSO + échange SSO sécurisé par code court
│   └── spec.md
├── 012-semantic-search-api-platform/ ⚪ Backlog prioritaire — recherche sémantique, catégorisation disciplinaire, API mutualisable + SDK PHP/Python/Node.js
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

> Voir [`PLANNING.md`](PLANNING.md) pour le planning opérationnel courant. Il est la source de vérité pour la dette restante P0/P1/P2/P3.
> Voir `docs/ARCHITECTURE.md` pour le bilan d'audit complet.
> Voir [`TECHNICAL_REQUIREMENTS.md`](TECHNICAL_REQUIREMENTS.md) pour les exigences techniques applicables à toutes les specs.

| Priorité | Spec | Effort | Prérequis | État |
|----------|------|--------|-----------|------|
| Vérification | Relancer `pnpm run lint`, `pnpm run test:e2e`, `make test` dans l'environnement cible | court | services disponibles | 🔁 À faire avant release |
| P1 | 012 — Recherche sémantique, catégorisation disciplinaire, API mutualisable + SDKs | long | validation métier taxonomie + infra embeddings | ⚪ À cadrer |
| P2 optionnel | Migrer progressivement les composants de `useSearch()` vers les hooks selectors | moyen | aucun | ⚪ Opportuniste |
| P2 optionnel | Réduire `AuthModal.tsx` si de nouveaux modes d'auth sont ajoutés | moyen | aucun | ⚪ Opportuniste |
