#!/usr/bin/env python3
"""
Test de vérification des requêtes Solr générées avec les sous-catégories
Vérifie que les filtres avec sous-catégories sont correctement expansés
"""

from app.services.search_builder import SearchBuilder
from app.models.search_models import SearchRequest, QueryModel, FilterModel
from app.services.facet_config import get_filter_values, COMMON_FACETS_MAPPING
from app.settings import settings

print("=== Test de Génération des Requêtes Solr avec Sous-Catégories ===\n")

# Créer une instance de SearchBuilder
builder = SearchBuilder(solr_base_url=settings.solr_base_url)

test_cases = [
    {
        "name": "Filtre simple: platform=OB",
        "filters": [FilterModel(identifier="platform", value="OB")]
    },
    {
        "name": "Sous-catégorie simple: type=livre",
        "filters": [FilterModel(identifier="type", value="livre")]
    },
    {
        "name": "Sous-catégorie multiple: type=article",
        "filters": [FilterModel(identifier="type", value="article")]
    },
    {
        "name": "Sous-catégorie complexe: type=compterendu (7 valeurs)",
        "filters": [FilterModel(identifier="type", value="compterendu")]
    },
    {
        "name": "Combinaison: platform=OB + type=article",
        "filters": [
            FilterModel(identifier="platform", value="OB"),
            FilterModel(identifier="type", value="article")
        ]
    }
]

for test in test_cases:
    print(f"{test['name']}")
    print("-" * 60)
    
    # Créer une requête de recherche
    request = SearchRequest(
        query=QueryModel(query="test"),
        filters=test['filters'],
        pagination={"from": 0, "size": 10},
        facets=[]
    )
    
    # Générer l'URL Solr
    solr_url = builder.build_search_url(request)
    
    # Extraire les paramètres fq de l'URL
    if 'fq=' in solr_url:
        # Afficher l'URL complète
        print(f"URL: {solr_url}\n")
        
        # Analyser les filtres
        print("Analyse des filtres:")
        for f in test['filters']:
            solr_field = COMMON_FACETS_MAPPING.get(f.identifier, f.identifier)
            values = get_filter_values(f.identifier, f.value)
            
            print(f"  {f.identifier}={f.value}")
            print(f"    → Champ Solr: {solr_field}")
            print(f"    → Valeurs: {values}")
            
            if len(values) > 1:
                print(f"    → Expansion: {solr_field}:({' OR '.join(values)})")
            else:
                print(f"    → Filtre: {solr_field}:{values[0]}")
    
    print()

print("\n=== Vérification Manuelle ===")
print("Vérifiez que les URLs générées contiennent les bons paramètres fq")
print("Pour type=article, on devrait voir: type:(article OR articlepdf)")
print("Pour type=compterendu, on devrait voir 7 valeurs dans le OR")
