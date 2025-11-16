import sqlite3

conn = sqlite3.connect('runcoach.db')
c = conn.cursor()
c.execute('PRAGMA table_info(users)')
cols = c.fetchall()

print(f'\n✅ Columnas totales en users: {len(cols)}')
print('\n📋 Últimas 4 columnas (nuevas):')
for col in cols[-4:]:
    print(f'  - {col[1]}: {col[2]}')

conn.close()
