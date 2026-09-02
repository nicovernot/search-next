# Plan 003 — UX/UI Premium Overhaul

## Architecture

```
front/
├── app/
│   ├── globals.css                 # tokens, palette, gradients, dark mode, motion
│   ├── [locale]/layout.tsx         # layout de page + providers de thème
│   ├── components/
│   │   ├── SearchBar.tsx           # barre de recherche premium
│   │   ├── ResultItem.tsx          # cartes de résultats richement stylées
│   │   ├── Facets.tsx              # panneau de filtres avec visual design
│   │   ├── ThemeToggle.tsx         # bascule clair/sombre
│   │   └── AuthModal.tsx           # modales avec glassmorphism
│   ├── context/
│   │   └── SearchContext.tsx       # contexte de recherche, injecte les states visuels
│   └── lib/
│       └── theme.ts                # helpers de thème et tokens
├── messages/
│   └── *.json                      # libellés et variantes de thème
└── package.json                    # dépendances de styles / fontes
```

## Data Flow

1. Le layout charge les variables CSS globales et la préférence de thème.
2. `SearchContext` fournit les données de recherche et le current locale.
3. Les composants UI lisent le thème actif et appliquent les tokens de couleur, spacing et motion.
4. Les cartes de résultats et les filtres rendent des états hover/focus/active avec micro-animations.
5. Le thème est synchronisé avec le système ou avec le stockage local selon la préférence utilisateur.

## Key Files

| Fichier | Rôle |
|---------|------|
| `front/app/globals.css` | Design system, palette, modes clair/sombre, animations globales |
| `front/app/[locale]/layout.tsx` | Root layout + config d'UI |
| `front/app/components/ResultItem.tsx` | Cartes de résultats visuellement premium |
| `front/app/components/SearchBar.tsx` | Composant d'entrée et CTA visuelle |
| `front/app/components/Facets.tsx` | Panier de filtres / sidebar |
| `front/app/components/AuthModal.tsx` | Modales, transitions et glassmorphism |
| `front/app/context/SearchContext.tsx` | Apporte l'état de recherche au rendu UI |
| `front/messages/*.json` | Traductions liées au thème et aux éléments UI |
| `front/package.json` | Dépendances de fontes, design system et scripts |

## UX & Design Constraints

- Respecter un design cohérent sur les 6 locales du projet.
- Maintenir un contraste lisible dans le mode sombre et le mode clair.
- Les animations doivent rester légères pour ne pas gêner l'usage de recherche.
- Les effets visuels doivent compléter la fonction, pas la masquer.

## Risks / Follow-up

- Risque d'incohérence visuelle si les composants hérités gardent des styles locaux.
- Risque de régression d'accessibilité si les effets visuels sont trop agressifs.
- La migration technique doit rester compatible avec la suite de specs de recherche et d'URL sync.
