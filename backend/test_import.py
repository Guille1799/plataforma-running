#!/usr/bin/env python3
import sys
sys.path.insert(0, '/c/Users/guill/Desktop/plataforma-running/backend')

try:
    from app.services.events_service import events_service
    print(f"✅ Import OK")
    print(f"Total carreras: {len(events_service.races_db)}")
    print("\nPrimeras 5:")
    for race in events_service.races_db[:5]:
        print(f"  • {race['name']} ({race['location']})")
    
    print("\nBuscando 'dos':")
    results = events_service.search_races('dos')
    print(f"  Encontrados: {len(results)}")
    for r in results:
        print(f"    - {r['name']}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
