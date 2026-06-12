# Checklist de Mise en Place

## 1. Sauvegarde

Avant modification, sauvegarder :

- `schema.xml`
- `solrconfig.xml`
- le nom exact du core ;
- la version Solr/Lucene.

Commandes de lecture :

```bash
curl "https://solrslave-sec.labocleo.org/solr/documents/admin/file?file=schema.xml" > schema.xml
curl "https://solrslave-sec.labocleo.org/solr/documents/admin/file?file=solrconfig.xml" > solrconfig.xml
```

## 2. Suggestions

Option rapide :

- remplacer le suggester d'exemple `mySuggester` par `default` ;
- utiliser `naked_titre`.

Option recommandee :

- ajouter `suggest_text` dans le schema ;
- ajouter les `copyField` ;
- configurer le suggester sur `suggest_text` ;
- reindexer.

Validation :

```bash
curl "https://solrslave-sec.labocleo.org/solr/documents/suggest?suggest=true&suggest.dictionary=default&suggest.build=true&wt=json"
curl "https://solrslave-sec.labocleo.org/solr/documents/suggest?suggest=true&suggest.dictionary=default&suggest.q=hist&suggest.count=10&wt=json"
```

Resultat attendu :

- HTTP 200 ;
- presence de `suggest.default` ;
- `suggestions` non vide pour des prefixes courants.

## 3. More Like This

Ajouter un handler `/mlt` ou valider l'usage de `/select?mlt=true`.

Validation :

```bash
curl "https://solrslave-sec.labocleo.org/solr/documents/mlt?q=id:OB.etnograficapress.10478&wt=json"
```

Resultat attendu :

- HTTP 200 ;
- documents similaires ;
- champs `id`, `url`, `titre`, `score`.

## 4. Highlight

Activer `hl=true` sur les champs `naked_*` et `parts_*`.

Validation :

```bash
curl "https://solrslave-sec.labocleo.org/solr/documents/select?q=science%20ouverte&hl=true&hl.fl=naked_titre,naked_resume,naked_texte&rows=3&wt=json"
```

Resultat attendu :

- bloc `highlighting` dans la reponse ;
- snippets par `id`.

## 5. Disciplines

Court terme applicatif :

- ajouter `id` dans `fl` cote application ;
- alimenter `document_enrichment` ;
- verifier que l'API renvoie `disciplines: [...]`.

Si Solr porte les disciplines :

- ajouter les champs `disciplines`, `discipline_source`, `discipline_confidence` ;
- alimenter ces champs par reindex ou update partiel ;
- ajouter `disciplines` aux facettes.

Validation API :

```bash
curl "http://localhost:8003/api/v1/search?q=science%20ouverte"
```

Resultat attendu :

```json
{
  "disciplines": ["..."],
  "discipline_source": "source_metadata",
  "discipline_confidence": 0.9
}
```

## 6. Redemarrage et rechargement

Selon le mode d'exploitation Solr :

- recharger le core apres modification de `solrconfig.xml` ;
- reindexer si `schema.xml` ajoute des champs ou des `copyField` ;
- reconstruire le suggester apres reindex.

## 7. Points d'attention

- `copyField` ne remplit pas les documents deja indexes sans reindex.
- `buildOnStartup=true` peut ralentir le demarrage si le dictionnaire est gros.
- `FuzzyLookupFactory` est confortable pour l'utilisateur, mais peut consommer plus de memoire.
- Les champs `string` ne sont pas analyses ; pour une autocompletion textuelle, preferer `text_fr` ou un type dedie.
- Si les suggestions retournent trop de variantes bruitees, limiter la source a `naked_titre` puis elargir progressivement.

