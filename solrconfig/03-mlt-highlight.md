# More Like This et Highlight

## More Like This

L'application contient deja une methode `build_mlt_url`, mais il faut que Solr ait un handler coherent avec les champs du schema `documents`.

Champs utiles pour MLT :

- `naked_titre`
- `naked_soustitre`
- `naked_resume`
- `naked_texte`
- `parts_titre`
- `parts_resume`
- `parts_texte`

Handler recommande :

```xml
<requestHandler name="/mlt" class="solr.MoreLikeThisHandler">
  <lst name="defaults">
    <str name="mlt.fl">naked_titre,naked_soustitre,naked_resume,naked_texte,parts_titre,parts_resume,parts_texte</str>
    <str name="mlt.mintf">1</str>
    <str name="mlt.mindf">2</str>
    <str name="mlt.maxdfpct">25</str>
    <str name="mlt.minwl">3</str>
    <str name="mlt.maxwl">40</str>
    <str name="mlt.count">5</str>
    <str name="fl">id,url,titre,naked_titre,naked_resume,type,platformID,site_title,anneedatepubli,score</str>
    <str name="wt">json</str>
  </lst>
</requestHandler>
```

Exemple d'appel :

```bash
curl "https://solrslave-sec.labocleo.org/solr/documents/mlt?q=id:OB.etnograficapress.10478&wt=json"
```

Si l'on garde le handler `/select` avec `mlt=true`, utiliser plutot :

```bash
curl "https://solrslave-sec.labocleo.org/solr/documents/select?q=id:OB.etnograficapress.10478&mlt=true&mlt.fl=naked_titre,naked_resume,naked_texte&mlt.count=5&wt=json"
```

## Highlight

Le highlight doit etre configure sur les champs textuels effectivement indexes.

Champs recommandes :

- `naked_titre`
- `naked_soustitre`
- `naked_resume`
- `naked_texte`
- `parts_titre`
- `parts_resume`
- `parts_texte`

Defaults a ajouter au request handler de recherche, ou a envoyer cote application :

```xml
<str name="hl">true</str>
<str name="hl.fl">naked_titre,naked_soustitre,naked_resume,naked_texte,parts_titre,parts_resume,parts_texte</str>
<str name="hl.simple.pre"><![CDATA[<mark>]]></str>
<str name="hl.simple.post"><![CDATA[</mark>]]></str>
<str name="hl.snippets">3</str>
<str name="hl.fragsize">180</str>
<str name="hl.method">unified</str>
```

Exemple :

```bash
curl "https://solrslave-sec.labocleo.org/solr/documents/select?q=science%20ouverte&defType=edismax&df=naked_titre&qf=naked_titre^8 naked_resume^1 naked_texte^0.5&hl=true&hl.fl=naked_titre,naked_resume,naked_texte&hl.simple.pre=%3Cmark%3E&hl.simple.post=%3C/mark%3E&rows=3&wt=json"
```

## Integration application

Pour exposer le highlight au frontend, il faudra :

- ajouter les params `hl.*` dans `SearchBuilder.build_search_url` ;
- lire `highlighting` dans la reponse Solr ;
- joindre les snippets aux documents par `id` ;
- ajouter un champ optionnel cote frontend, par exemple `highlights?: Record<string, string[]>`.

