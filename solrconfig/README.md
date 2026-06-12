# Solr Configuration Notes

Ce dossier regroupe la documentation et les snippets de configuration pour mettre à jour le core Solr `documents`.

Objectifs :

- corriger l'autocompletion `/suggest` ;
- préparer les handlers More Like This et highlight ;
- documenter les changements nécessaires pour les disciplines ;
- fournir des commandes de validation faciles à rejouer.

## Ordre de lecture

1. [Etat actuel](./01-current-state.md)
2. [Suggestions / autocomplete](./02-suggestions.md)
3. [MLT et highlight](./03-mlt-highlight.md)
4. [Disciplines](./04-disciplines.md)
5. [Checklist de mise en place](./05-deployment-checklist.md)

Les snippets prêts à copier sont dans :

- [schema/snippets.xml](./schema/snippets.xml)
- [solrconfig/snippets.xml](./solrconfig/snippets.xml)

## Core cible

```text
https://solrslave-sec.labocleo.org/solr/documents
```

Le schema observé expose déjà des champs utilisables pour la recherche :

- `id`, `url`, `platformID`, `siteid`
- `titre`, `soustitre`, `titretraduit`
- `naked_*`, dont `naked_titre`, `naked_resume`, `naked_texte`
- `parts_*`
- `contributeur_*`, `contributeurFacet_*`, `contributeurFacetR_*`
- `site`, `siteFacet`

La configuration applicative actuelle interroge `/suggest` avec `suggest.q`, et attend une réponse Solr Suggester standard.

