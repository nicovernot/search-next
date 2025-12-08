# Corrections des facettes - Résumé

## Problème résolu

**Erreur initiale :** `Search failed: Bad Request`

**Cause :** Les facettes `language` et `year` n'existent pas dans le schéma Solr.

## Facettes disponibles dans l'API

Selon les fichiers de configuration (`app/services/facets_json/*.json`), voici les facettes disponibles :

| Identifiant | Champ Solr | Description |
|-------------|------------|-------------|
| `platform` | `platformID` | Plateforme (OJ, OB, HO, CO) |
| `type` | `type` | Type de document (article, livre, chapitre, etc.) |
| `access` | `accessRights_openAireV3` | Droits d'accès |
| `translations` | `autodetect_lang` | **Langue** du document |
| `date` | `anneedatepubli` | **Année** de publication |
| `author` | `contributeurFacetR_auteur` ou `contributeurFacet_auteur` | Auteur |
| `subscribers` | `subscribers` | Abonnés |

## Modifications apportées

### 1. SearchContext.jsx

#### Ajout du mapping des facettes
```javascript
const FACET_FIELD_MAPPING = {
  'platform': 'platformID',
  'type': 'type',
  'access': 'accessRights_openAireV3',
  'translations': 'autodetect_lang',  // LANGUE
  'date': 'anneedatepubli',          // ANNÉE
  'author': 'contributeurFacetR_auteur'
};
```

#### Correction des facettes demandées
```javascript
facets: [
  { identifier: 'platform', type: 'list' },
  { identifier: 'type', type: 'list' },
  { identifier: 'access', type: 'list' },
  { identifier: 'translations', type: 'list' },  // Au lieu de 'language'
  { identifier: 'date', type: 'list' },          // Au lieu de 'year'
  { identifier: 'author', type: 'list' }
]
```

#### Transformation du format de réponse Solr
Solr retourne les facettes au format :
```javascript
{
  "platformID": ["HO", 16904, "OJ", 14988, "OB", 9354, "CO", 3075]
}
```

Transformation en :
```javascript
{
  "platform": {
    "buckets": [
      { "key": "HO", "doc_count": 16904 },
      { "key": "OJ", "doc_count": 14988 },
      { "key": "OB", "doc_count": 9354 },
      { "key": "CO", "doc_count": 3075 }
    ]
  }
}
```

### 2. Facets.jsx

Mise à jour de la configuration des facettes affichées :
```javascript
const facetConfigs = [
  { key: 'platform', label: 'Plateforme', field: 'platform' },
  { key: 'type', label: 'Type de document', field: 'type' },
  { key: 'access', label: 'Accès', field: 'access' },
  { key: 'translations', label: 'Langue', field: 'translations' },  // CORRIGÉ
  { key: 'date', label: 'Année', field: 'date' },                   // CORRIGÉ
  { key: 'author', label: 'Auteur', field: 'author' }              // AJOUTÉ
];
```

## Validation

### Test API
```bash
curl -s -X POST http://localhost:8007/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": {"query": "histoire"},
    "filters": [],
    "facets": [
      {"identifier": "platform", "type": "list"},
      {"identifier": "type", "type": "list"},
      {"identifier": "translations", "type": "list"},
      {"identifier": "date", "type": "list"}
    ],
    "pagination": {"from": 0, "size": 5}
  }'
```

**Résultat attendu :** Status 200, avec facettes dans `facet_counts.facet_fields`

### Test Frontend
1. Accéder à `http://localhost:3009`
2. Taper une recherche (ex: "histoire")
3. Observer les facettes dans la barre latérale :
   - ✅ Plateforme
   - ✅ Type de document
   - ✅ Accès
   - ✅ Langue (translations)
   - ✅ Année (date)
   - ✅ Auteur

## Notes importantes

### Différences entre plateformes
Certaines facettes peuvent avoir des champs différents selon la plateforme :
- **author** : `contributeurFacetR_auteur` (OJ, OB) ou `contributeurFacet_auteur` (HO)
- **date** : Format varie selon la plateforme (Y pour OJ/OB, autre pour CO)

### Facettes spécifiques par plateforme
- **journals-publication** : Uniquement pour OJ
- **books-publication** : Uniquement pour OB
- **hypotheses-publication** : Uniquement pour HO

### Configuration type.options
La facette `type` a des sous-catégories définies dans `options` qui regroupent plusieurs valeurs Solr sous un même label.

## Services redémarrés

```bash
cd /home/nvernot/projets/searchv2/search_api_solr
docker compose ps
```

**État actuel :**
- ✅ API (port 8007) : Running avec CORS activé
- ✅ Frontend (port 3009) : Running avec facettes corrigées

---

**Date de correction :** 8 décembre 2025  
**Fichiers modifiés :**
- `front/src/contexts/SearchContext.jsx`
- `front/src/components/Facets.jsx`
- `search_api_solr/app/main.py` (CORS)
