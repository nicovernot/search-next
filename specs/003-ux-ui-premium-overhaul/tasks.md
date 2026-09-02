# Tasks: UX/UI Premium Overhaul

## Phase 1 — Fondations visuelles

- [ ] T001 Auditer les composants d'interface existants et identifier les styles hérités à remplacer
- [ ] T002 Définir les tokens de thème (`colors`, `spacing`, `radius`, `shadow`, `motion`) dans `front/app/globals.css`
- [ ] T003 Mettre en place le mode clair / sombre global avec variables CSS cohérentes
- [ ] T004 Vérifier la compatibilité avec la palette de branding et la typographie de l'application
- [ ] T005 Ajouter les animations globales et les transitions de fond d'écran sans perturber l'accessibilité

## Phase 2 — Layout et structure UI

- [ ] T006 Refonte du layout principal dans `front/app/[locale]/layout.tsx` pour intégrer le design premium
- [ ] T007 Mettre à jour la barre de recherche et les états hover/focus dans `SearchBar.tsx`
- [ ] T008 Harmoniser les composants de sidebar/filtres (`Facets.tsx`, `FacetGroup.tsx`) avec le nouveau design system
- [ ] T009 Adapter les composants d'auth et de modales (`AuthModal.tsx`) au glassmorphism et aux états visuels
- [ ] T010 Vérifier la cohérence des composants de résultats sur mobile, tablette et desktop

## Phase 3 — Cartes de résultats

- [ ] T011 Rework de `ResultItem.tsx` en cartes premium avec hiérarchie visuelle claire
- [ ] T012 Ajouter les états hover, focus, active et micro-animations sur les cartes
- [ ] T013 Assurer la lisibilité des métadonnées (auteur, type, langue, texte d'extrait)
- [ ] T014 Vérifier les composants iconographiques et badges sans rupture de contrastes

## Phase 4 — Thème et accessibilité

- [ ] T015 Implémenter la bascule de thème utilisateur avec persistance locale
- [ ] T016 Vérifier le support du thème système au chargement initial
- [ ] T017 Valider l'accessibilité clavier, contrastes et lectures des états d'erreur
- [ ] T018 Tester les animations pour éviter les effets trop lourds sur les performances

## Phase 5 — Vérification

- [ ] T019 Lancer les tests front unitaires et de rendu nécessaires à l'UI
- [ ] T020 Vérifier la régression visuelle sur les écrans clés via Playwright
- [ ] T021 Corriger les écarts visuels reportés après validation
- [ ] T022 Finaliser la revue de cohérence entre design system, composants et i18n
