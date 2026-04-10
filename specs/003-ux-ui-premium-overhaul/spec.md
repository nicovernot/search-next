# Feature Specification: UX/UI Premium Overhaul

**Feature Branch**: `feature/003-ux-ui-premium-overhaul`  
**Created**: 2026-04-10  
**Status**: Planning  

## Overview
L'objectif de cette spécification est d'amener l'application frontend (Next.js) à un standard de design Premium, moderne et dynamique ("WOW effect"), en remplaçant l'esthétisme basique actuel hérité de templates, par une identité visuelle harmonieuse et interactive.

## User Scenarios & Testing (Playwright)

### User Story 1 - Interface Premium (Priority: P0)
En tant qu'utilisateur, lors de mon arrivée sur le site, je suis marqué par la qualité du design (typographie Google moderne comme Inter/Outfit, palettes de couleurs harmonieuses, dark mode complet, glassmorphism), rendant mon expérience de recherche plus agréable et engageante.
**Independent Test**: La page d'accueil et les résultats utilisent les nouvelles variables CSS, le dark mode fonctionne via le basculement système, et les gradients d'arrière-plan sont rendus sans rupture.

### User Story 2 - Micro-Animations et Réactivité (Priority: P1)
En tant qu'utilisateur, chaque interaction (survol de cartes de résultats, ouverture de facettes, sélection de requêtes avancées) est accompagnée de transitions fluides et de micro-animations qui récompensent mon action.
**Independent Test**: Les éléments de type `ResultItem` ou `FacetGroup` possèdent des états de `:hover` et `:active` testables visuellement (changement de transform/scale ou box-shadow).

### User Story 3 - Dark Mode Global & Toggle (Priority: P2)
En tant qu'utilisateur, je veux pouvoir forcer l'interface en mode clair ou sombre selon ma convenance, ou suivre mon thème système.
**Independent Test**: Un "Theme Switcher" dans la navbar permet de persister la préférence de thème localement.

## Requirements

### Design Aesthetics & Technology
- **REQ-1**: Intégration avancée de TailwindCSS v4 ou Vanilla CSS structuré avec des tokens de thèmes (`hsl()`).
- **REQ-2**: Implémentation du Dark Mode first-class.
- **REQ-3**: Utilisation d'effets visuels comme le Glassmorphism (blur backdrops) sur la barre de recherche ou les modales.
- **REQ-4**: Utilisation d'une typographie propre (Inter, Roboto, ou Outfit) via `next/font`.
- **REQ-5**: Refonte du `ResultItem.tsx` pour afficher les cartes de résultats sous forme de "rich cards" avec hiérarchie claire (Titre, Auteurs, Type, Extrait).

## Success Criteria
- **SC-001**: L'interface répond parfaitement aux critères "Rich Aesthetics" et "Dynamic Design".
- **SC-002**: L'application est fully responsive avec des animations non bloquantes.
- **SC-003**: Le score Lighthouse d'accessibilité et best-practices reste au-dessus de 95, même avec l'ajout d'animations.
