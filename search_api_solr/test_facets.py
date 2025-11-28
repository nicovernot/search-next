#!/usr/bin/env python3
"""Test script to verify facet configuration loading"""

from app.services.facet_config import COMMON_FACETS_MAPPING, FACET_CONFIG
import json

print("=== Facet Configuration Test ===\n")

print("1. Loaded FACET_CONFIG files:")
for config_name in FACET_CONFIG.keys():
    print(f"   - {config_name}.json")

print("\n2. COMMON_FACETS_MAPPING (from common.json):")
print(json.dumps(COMMON_FACETS_MAPPING, indent=2))

print("\n3. Verification:")
expected_facets = ['platform', 'access', 'translations', 'type', 'author', 'subscribers']
for facet in expected_facets:
    if facet in COMMON_FACETS_MAPPING:
        print(f"   ✓ {facet} -> {COMMON_FACETS_MAPPING[facet]}")
    else:
        print(f"   ✗ {facet} NOT FOUND")

print("\n4. Sample common.json structure:")
common = FACET_CONFIG.get('common', {})
if 'platform' in common:
    print(f"   platform config: {json.dumps(common['platform'], indent=4)}")
