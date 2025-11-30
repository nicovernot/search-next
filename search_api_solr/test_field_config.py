#!/usr/bin/env python3
"""Test script to verify field configuration loading"""

from app.services.field_config import get_default_fields, get_default_search_field, get_highlight_fields, FIELD_CONFIG
import json

print("=== Field Configuration Test ===\n")

print("FIELD_CONFIG loaded:")
print(json.dumps(FIELD_CONFIG, indent=2))

print("\n=== Accessor Functions ===\n")

print(f"Default Fields (fl): {get_default_fields()}")
print(f"Default Search Field (df): {get_default_search_field()}")
print(f"Highlight Fields (hl.fl): {get_highlight_fields()}")

# Verification
assert "titre" in get_default_fields()
assert get_default_search_field() == "titre"
assert "resume" in get_highlight_fields()

print("\n=== SUCCESS: All checks passed ===")
