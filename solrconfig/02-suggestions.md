# Suggestions / Autocomplete

## Objectif

Faire fonctionner :

```http
GET /solr/documents/suggest?suggest.q=hist&wt=json
```

avec une reponse de ce type :

```json
{
  "suggest": {
    "default": {
      "hist": {
        "numFound": 10,
        "suggestions": [
          { "term": "histoire", "weight": 123, "payload": "" }
        ]
      }
    }
  }
}
```

## Version minimale

La version minimale utilise directement `naked_titre`.

Avantages :

- pas besoin de modifier le schema ;
- pas besoin de reindex complet si le champ existe deja dans l'index ;
- compatible rapidement avec l'application actuelle si le dictionnaire s'appelle `default`.

Limites :

- suggestions uniquement basees sur les titres ;
- moins de controle sur la qualite des termes ;
- pas de melange propre titres/auteurs/sites.

Snippet :

```xml
<searchComponent name="suggest" class="solr.SuggestComponent">
  <lst name="suggester">
    <str name="name">default</str>
    <str name="lookupImpl">FuzzyLookupFactory</str>
    <str name="dictionaryImpl">DocumentDictionaryFactory</str>
    <str name="field">naked_titre</str>
    <str name="suggestAnalyzerFieldType">text_fr</str>
    <str name="buildOnStartup">true</str>
    <str name="buildOnCommit">true</str>
  </lst>
</searchComponent>

<requestHandler name="/suggest" class="solr.SearchHandler" startup="lazy">
  <lst name="defaults">
    <str name="suggest">true</str>
    <str name="suggest.dictionary">default</str>
    <str name="suggest.count">10</str>
  </lst>
  <arr name="components">
    <str>suggest</str>
  </arr>
</requestHandler>
```

## Version recommandee

La version recommandee ajoute un champ dedie `suggest_text`, alimente par `copyField`.

Avantages :

- un seul champ pour l'autocomplete ;
- ajout possible de titres, auteurs, sites, mots-cles ;
- configuration plus lisible ;
- evolution plus facile.

Schema :

```xml
<field name="suggest_text" type="text_fr" indexed="true" stored="false" multiValued="true"/>

<copyField source="naked_titre" dest="suggest_text"/>
<copyField source="titre" dest="suggest_text"/>
<copyField source="titretraduit" dest="suggest_text"/>
<copyField source="contributeurFacetR_*" dest="suggest_text"/>
<copyField source="site" dest="suggest_text"/>
```

Solr config :

```xml
<searchComponent name="suggest" class="solr.SuggestComponent">
  <lst name="suggester">
    <str name="name">default</str>
    <str name="lookupImpl">FuzzyLookupFactory</str>
    <str name="dictionaryImpl">DocumentDictionaryFactory</str>
    <str name="field">suggest_text</str>
    <str name="suggestAnalyzerFieldType">text_fr</str>
    <str name="buildOnStartup">true</str>
    <str name="buildOnCommit">true</str>
  </lst>
</searchComponent>
```

Cette version demande un reindex complet pour remplir `suggest_text`.

## Build et test

Construire le dictionnaire :

```bash
curl "https://solrslave-sec.labocleo.org/solr/documents/suggest?suggest=true&suggest.dictionary=default&suggest.build=true&wt=json"
```

Tester :

```bash
curl "https://solrslave-sec.labocleo.org/solr/documents/suggest?suggest=true&suggest.dictionary=default&suggest.q=hist&suggest.count=10&wt=json"
```

Tester le chemin utilise par l'application :

```bash
curl "https://solrslave-sec.labocleo.org/solr/documents/suggest?q=hist&suggest.q=hist&wt=json"
```

## Ajustement recommande cote application

Dans `SearchBuilder.build_suggest_url`, ajouter explicitement le dictionnaire :

```python
params = {
    "q": query_term,
    "wt": "json",
    "suggest": "true",
    "suggest.dictionary": "default",
    "suggest.q": query_term,
}
```

Ce n'est pas obligatoire si le handler Solr declare `suggest.dictionary=default` dans ses defaults, mais c'est plus explicite.

