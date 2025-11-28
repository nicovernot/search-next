#!/usr/bin/env python3
"""Test script to verify platform-specific facets loading"""

from app.services.facet_config import PLATFORM_SPECIFIC_FACETS, FACET_CONFIG
import json

print("=== Platform-Specific Facets Test ===\n")

print("PLATFORM_SPECIFIC_FACETS:")
print(json.dumps(PLATFORM_SPECIFIC_FACETS, indent=2))

print("\n=== Detailed breakdown ===\n")

platform_names = {
    'OB': 'OpenEdition Books',
    'OJ': 'OpenEdition Journals',
    'HO': 'Hypotheses',
    'CO': 'Calenda'
}

for platform_id, facets in PLATFORM_SPECIFIC_FACETS.items():
    platform_name = platform_names.get(platform_id, platform_id)
    print(f"{platform_name} ({platform_id}):")
    for facet in facets:
        print(f"  - {facet}")
    print()

print("=== Verification against JSON files ===\n")

# Vérifier books.json
if 'books' in FACET_CONFIG:
    books_facets = list(FACET_CONFIG['books'].keys())
    print(f"books.json facets: {books_facets}")
    print(f"  → Specific to OB: {PLATFORM_SPECIFIC_FACETS.get('OB', [])}")
    print()

# Vérifier journals.json  
if 'journals' in FACET_CONFIG:
    journals_facets = list(FACET_CONFIG['journals'].keys())
    print(f"journals.json facets: {journals_facets}")
    print(f"  → Specific to OJ: {PLATFORM_SPECIFIC_FACETS.get('OJ', [])}")
    print()
