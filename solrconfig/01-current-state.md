# Etat Actuel

## Ce qui existe dans `schema.xml`

Le schema du core `documents` contient bien les champs nécessaires pour construire une autocompletion et les futures fonctions de recherche avancée.

Champs pertinents :

```xml
<field name="id" type="string" indexed="true" stored="true" required="true"/>
<field name="titre" type="text_fr" indexed="true" stored="true"/>
<field name="soustitre" type="text_fr" indexed="true" stored="true"/>
<field name="titretraduit" type="text_fr" indexed="true" stored="true" multiValued="true"/>
<dynamicField name="naked_*" type="text_fr" indexed="true" stored="true"/>
<dynamicField name="parts_*" type="text_fr" indexed="true" stored="true" multiValued="true"/>
<dynamicField name="contributeur_*" type="text_fr" indexed="true" stored="true" multiValued="true"/>
<dynamicField name="contributeurFacetR_*" type="string" indexed="true" stored="true" multiValued="true"/>
<field name="site" type="text_fr" indexed="true" stored="true"/>
```

`text_fr` applique actuellement :

- `StandardTokenizerFactory`
- `ElisionFilterFactory`
- `LowerCaseFilterFactory`
- `StopFilterFactory`
- `FrenchLightStemFilterFactory`

## Probleme actuel des suggestions

Dans `solrconfig.xml`, le `SuggestComponent` est encore une configuration d'exemple :

```xml
<str name="name">mySuggester</str>
<str name="field">cat</str>
<str name="weightField">price</str>
```

Or `cat` et `price` ne sont pas des champs du schema `documents`.

En plus, l'application appelle implicitement un dictionnaire nommé `default`, mais le seul nom configuré est `mySuggester`.

Symptome observe :

```text
No suggester named default was configured
```

## Probleme actuel des disciplines

Le backend applicatif est pret a enrichir les documents depuis PostgreSQL, mais il a besoin de l'identifiant Solr `id`.

Dans l'application, le fichier `search_api_solr/app/services/fields_json/common.json` ne demande pas encore `id` dans `fl`. Sans `id`, le backend ne peut pas faire le lien avec `document_enrichment.doc_id`.

Les disciplines ne sont pas un champ natif du Solr distant aujourd'hui. Elles doivent etre :

- soit ajoutees a Solr via un champ indexe dedie ;
- soit gerees dans PostgreSQL par l'application, avec une facette calculee cote backend ;
- soit synchronisees dans les deux systemes si on veut filtrer directement dans Solr.

