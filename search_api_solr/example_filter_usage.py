#!/usr/bin/env python3
"""
Exemple d'utilisation de get_filter_values() dans SearchBuilder

Ce fichier montre comment utiliser la fonction get_filter_values() pour gérer
les sous-catégories de facettes lors de la construction des filtres Solr.
"""

from app.services.facet_config import get_filter_values, COMMON_FACETS_MAPPING

def build_filter_query_example(facet_name: str, filter_value: str) -> str:
    """
    Exemple de construction d'une requête de filtre Solr avec support des sous-catégories.
    
    Args:
        facet_name: Nom de la facette (ex: 'type', 'platform')
        filter_value: Valeur du filtre (ex: 'article', 'OB')
    
    Returns:
        Requête de filtre Solr (fq parameter)
    """
    # 1. Obtenir le champ Solr pour cette facette
    solr_field = COMMON_FACETS_MAPPING.get(facet_name, facet_name)
    
    # 2. Obtenir les valeurs Solr (avec expansion des sous-catégories si applicable)
    solr_values = get_filter_values(facet_name, filter_value)
    
    # 3. Construire la requête
    if len(solr_values) == 1:
        # Une seule valeur: type:livre
        return f'{solr_field}:{solr_values[0]}'
    else:
        # Plusieurs valeurs: type:(article OR articlepdf)
        values_str = ' OR '.join(solr_values)
        return f'{solr_field}:({values_str})'


# === Exemples d'utilisation ===

print("=== Exemples de construction de filtres Solr ===\n")

examples = [
    ('type', 'livre'),
    ('type', 'article'),
    ('type', 'chapitre'),
    ('type', 'compterendu'),
    ('platform', 'OB'),
    ('author', 'John Doe'),
]

for facet, value in examples:
    fq = build_filter_query_example(facet, value)
    print(f"Filtre: {facet}={value}")
    print(f"  → fq={fq}")
    print()

print("\n=== Exemple complet de requête Solr ===\n")

# Simuler une requête avec plusieurs filtres
filters = [
    ('platform', 'OB'),
    ('type', 'article'),
]

fq_params = [build_filter_query_example(f, v) for f, v in filters]

print("Filtres demandés:")
for f, v in filters:
    print(f"  - {f} = {v}")

print("\nParamètres fq générés:")
for fq in fq_params:
    print(f"  fq={fq}")

print("\nURL Solr complète:")
base_url = "https://solrslave-sec.labocleo.org/solr/documents/select"
fq_str = '&'.join([f'fq={fq}' for fq in fq_params])
print(f"{base_url}?q=history&{fq_str}")
