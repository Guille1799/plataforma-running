#!/usr/bin/env python3
"""
Test script to debug race search
"""
import sys
sys.path.insert(0, '/Users/guill/Desktop/plataforma-running/backend')

from app.services.events_service import events_service

print("=" * 70)
print("🔍 TESTING RACE SEARCH")
print("=" * 70)

# Test 1: Search for "marat"
print("\n1️⃣ SEARCH: 'marat'")
results = events_service.search_races(query="marat", limit=50)
print(f"Results found: {len(results)}")
for i, r in enumerate(results, 1):
    print(f"  {i}. {r['name']} ({r['date']})")

# Test 2: Search for "maraton"
print("\n2️⃣ SEARCH: 'maraton'")
results = events_service.search_races(query="maraton", limit=50)
print(f"Results found: {len(results)}")
for i, r in enumerate(results[:5], 1):
    print(f"  {i}. {r['name']} ({r['date']})")

# Test 3: Check normalization
print("\n3️⃣ TESTING NORMALIZATION")
test_strings = ["Marató", "Maratón", "marat", "MARATON"]
for s in test_strings:
    normalized = events_service.EventsService._normalize_search(s)
    print(f"  '{s}' → '{normalized}'")

print("\n" + "=" * 70)
