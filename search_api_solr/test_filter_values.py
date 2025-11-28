#!/usr/bin/env python3
"""Test script to verify get_filter_values helper function"""

from app.services.facet_config import get_filter_values

print("=== get_filter_values() Test ===\n")

test_cases = [
    ('type', 'livre'),
    ('type', 'article'),
    ('type', 'chapitre'),
    ('type', 'compterendu'),
    ('type', 'evenements'),
    ('platform', 'OB'),
    ('author', 'John Doe'),
]

for facet, value in test_cases:
    result = get_filter_values(facet, value)
    print(f"get_filter_values('{facet}', '{value}')")
    print(f"  → {result}")
    print()
