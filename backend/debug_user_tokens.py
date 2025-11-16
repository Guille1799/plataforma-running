import sqlite3

conn = sqlite3.connect('runcoach.db')
c = conn.cursor()

c.execute("SELECT id, email, garmin_email, garmin_token IS NOT NULL AS has_garmin_token, garmin_connected_at FROM users")
rows = c.fetchall()
for r in rows:
    print('id:', r[0])
    print('email:', r[1])
    print('garmin_email:', r[2])
    print('has_garmin_token:', bool(r[3]))
    print('garmin_connected_at:', r[4])
    print('---')

conn.close()
