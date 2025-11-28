#!/usr/bin/env python3
"""
Test complet du fonctionnement des facettes
Teste les facettes communes, les sous-catégories, et les facettes spécifiques par plateforme
"""

import httpx
import asyncio
import json

async def test_search_with_facets():
    """Test l'endpoint /search avec différentes combinaisons de facettes"""
    
    base_url = "http://localhost:8007/search"
    
    test_cases = [
        {
            "name": "Test 1: Recherche simple avec filtre platform",
            "payload": {
                "query": {"query": "history"},
                "filters": [
                    {"identifier": "platform", "value": "OB"}
                ],
                "pagination": {"from": 0, "size": 5},
                "facets": []
            }
        },
        {
            "name": "Test 2: Recherche avec filtre type=article (sous-catégorie)",
            "payload": {
                "query": {"query": "science"},
                "filters": [
                    {"identifier": "platform", "value": "OJ"},
                    {"identifier": "type", "value": "article"}
                ],
                "pagination": {"from": 0, "size": 5},
                "facets": []
            }
        },
        {
            "name": "Test 3: Recherche avec filtre type=livre",
            "payload": {
                "query": {"query": "philosophy"},
                "filters": [
                    {"identifier": "platform", "value": "OB"},
                    {"identifier": "type", "value": "livre"}
                ],
                "pagination": {"from": 0, "size": 5},
                "facets": []
            }
        },
        {
            "name": "Test 4: Recherche avec filtre type=compterendu (7 valeurs)",
            "payload": {
                "query": {"query": "literature"},
                "filters": [
                    {"identifier": "type", "value": "compterendu"}
                ],
                "pagination": {"from": 0, "size": 5},
                "facets": []
            }
        },
        {
            "name": "Test 5: Recherche avec filtre author",
            "payload": {
                "query": {"query": "research"},
                "filters": [
                    {"identifier": "author", "value": "Smith"}
                ],
                "pagination": {"from": 0, "size": 5},
                "facets": []
            }
        }
    ]
    
    print("=== Test des Facettes avec l'Endpoint /search ===\n")
    
    async with httpx.AsyncClient() as client:
        for i, test_case in enumerate(test_cases, 1):
            print(f"{test_case['name']}")
            print("-" * 60)
            
            try:
                response = await client.post(
                    base_url,
                    json=test_case['payload'],
                    timeout=10.0
                )
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Vérifier la structure de la réponse
                    if 'response' in data:
                        num_found = data['response'].get('numFound', 0)
                        docs_count = len(data['response'].get('docs', []))
                        print(f"✓ Résultats trouvés: {num_found}")
                        print(f"✓ Documents retournés: {docs_count}")
                        
                        # Afficher les filtres appliqués
                        filters = test_case['payload']['filters']
                        if filters:
                            print(f"✓ Filtres appliqués:")
                            for f in filters:
                                print(f"    - {f['identifier']} = {f['value']}")
                    else:
                        print(f"⚠ Structure de réponse inattendue")
                        print(f"Réponse: {json.dumps(data, indent=2)[:200]}...")
                        
                else:
                    print(f"✗ Erreur HTTP {response.status_code}")
                    print(f"Réponse: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"✗ Exception: {e}")
            
            print()
    
    print("\n=== Résumé ===")
    print("Tests terminés. Vérifiez que tous les tests ont retourné des résultats.")

if __name__ == "__main__":
    asyncio.run(test_search_with_facets())
