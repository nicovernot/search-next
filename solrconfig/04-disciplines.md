# Disciplines

## Etat actuel

Le contrat applicatif est deja prepare :

- `disciplines?: string[]`
- `discipline_source?: "source_metadata" | "inferred" | "manual_override" | null`
- `discipline_confidence?: number | null`

Le backend peut fusionner les enrichissements depuis PostgreSQL via la table `document_enrichment`.

Mais deux points bloquent l'affichage reel :

1. Le champ Solr `id` doit etre demande dans `fl`, sinon l'application ne peut pas retrouver `document_enrichment.doc_id`.
2. La table `document_enrichment` doit etre alimentee par un job d'enrichissement.

## Correction minimale cote application

Ajouter `id` a `search_api_solr/app/services/fields_json/common.json` :

```json
"fl": [
  "id",
  "titre",
  "naked_soustitre",
  "url"
]
```

Sans `id`, aucune discipline PostgreSQL ne peut etre rattachee au document Solr.

## Strategie A : disciplines dans PostgreSQL uniquement

Cette strategie garde Solr en lecture seule pour les disciplines.

Avantages :

- pas besoin de modifier Solr ;
- coherent avec la table `document_enrichment` existante ;
- permet `manual_override` facilement.

Limites :

- facette discipline a calculer cote backend ;
- filtrage par discipline moins direct qu'un `fq` Solr ;
- necessite une logique applicative supplementaire pour combiner recherche Solr et filtre PG.

Approche :

1. Solr renvoie les resultats avec `id`.
2. Backend interroge `document_enrichment` pour ces ids.
3. Backend ajoute `disciplines` dans chaque document.
4. Pour les facettes, backend calcule les buckets depuis PostgreSQL ou depuis un index dedie.

## Strategie B : disciplines synchronisees dans Solr

Ajouter des champs discipline dans `schema.xml` :

```xml
<field name="disciplines" type="string" indexed="true" stored="true" multiValued="true"/>
<field name="discipline_source" type="string" indexed="true" stored="true"/>
<field name="discipline_confidence" type="float" indexed="true" stored="true"/>
```

Ajouter la facette :

```xml
<str name="facet">true</str>
<str name="facet.field">disciplines</str>
<str name="facet.mincount">1</str>
```

Avantages :

- filtrage simple avec `fq=disciplines:histoire` ;
- facettes natives Solr ;
- meilleur alignement avec les autres facettes.

Limites :

- il faut synchroniser les enrichissements vers Solr ;
- chaque correction manuelle doit etre repercutee dans Solr ;
- reindex ou update partiel necessaire.

## Strategie recommandee

Court terme :

- ajouter `id` dans les champs retournes par l'application ;
- alimenter `document_enrichment` ;
- afficher les badges discipline.

Moyen terme :

- si le filtre/facette discipline devient central, synchroniser `disciplines` dans Solr ;
- ajouter `disciplines` comme `facet.field` ;
- utiliser `fq=disciplines:<code>` pour les filtres.

## Taxonomie

Utiliser des codes stables et courts, par exemple :

```text
histoire
sociologie
anthropologie
geographie
science-politique
economie
philosophie
litterature
linguistique
droit
education
arts
archeologie
religions
information-communication
```

Les labels humains doivent rester dans la table de reference `discipline` :

```sql
discipline(code, label_fr, label_en, parent_code)
```

Les documents ne stockent que les codes.

