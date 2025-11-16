import sqlite3

conn = sqlite3.connect('runcoach.db')
c = conn.cursor()

c.execute('SELECT COUNT(*) FROM workouts')
total = c.fetchone()[0]
print(f'\nTotal workouts: {total}')

if total > 0:
    c.execute('SELECT id, start_time, distance_meters/1000, sport_type FROM workouts ORDER BY start_time DESC LIMIT 5')
    print('\nÚltimos 5:')
    for w in c.fetchall():
        print(f'  ID {w[0]}: {w[1]} - {w[2]:.2f}km ({w[3]})')

conn.close()
