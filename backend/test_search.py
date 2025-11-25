#!/usr/bin/env python3
from app.services.events_service import EventsService

service = EventsService()

# Test normalización
query = 'marat'
print(f'Query: {query}')

# Test búsqueda - count maratones
count = 0
for race in service.races_db:
    name_norm = service._normalize_search(race['name'])
    if 'marat' in name_norm:
        count += 1
        print(f'✅ {race["name"]}: {race["date"]}')

print(f'\nTotal maratones encontradas: {count}')
