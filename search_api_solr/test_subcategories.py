#!/usr/bin/env python3
"""Test script to verify facet subcategories loading"""

from app.services.facet_config import FACET_SUBCATEGORIES
import json

print("=== Facet Subcategories Test ===\n")

print("FACET_SUBCATEGORIES:")
print(json.dumps(FACET_SUBCATEGORIES, indent=2, ensure_ascii=False))

print("\n=== Detailed breakdown ===\n")

for facet_name, subcats in FACET_SUBCATEGORIES.items():
    print(f"{facet_name}:")
    for subcat_name, values in subcats.items():
        print(f"  - {subcat_name}: {values}")
    print()
