#!/usr/bin/env python3
"""Direct test of race search"""
from app.services.events_service import EventsService

svc = EventsService()

# Test 1: Search for "marat"
print("\n" + "="*70)
print("TEST 1: Search for 'marat'")
print("="*70)
races = svc.search_races('marat', limit=50)
print(f"\n✅ Found {len(races)} races:\n")
for i, r in enumerate(races[:15], 1):
    print(f"{i}. {r['name']} - {r['date']}")
if len(races) > 15:
    print(f"... and {len(races) - 15} more")

# Test 2: Search for "diciembre"
print("\n" + "="*70)
print("TEST 2: Search for 'diciembre'")
print("="*70)
races = svc.search_races('diciembre', limit=50)
print(f"\n✅ Found {len(races)} races:\n")
for i, r in enumerate(races, 1):
    print(f"{i}. {r['name']} - {r['date']}")

# Test 3: Search for "valencia"
print("\n" + "="*70)
print("TEST 3: Search for 'valencia'")
print("="*70)
races = svc.search_races('valencia', limit=50)
print(f"\n✅ Found {len(races)} races:\n")
for i, r in enumerate(races[:10], 1):
    print(f"{i}. {r['name']} - {r['date']}")
if len(races) > 10:
    print(f"... and {len(races) - 10} more")

print("\n" + "="*70)
print("All tests complete!")
print("="*70)

