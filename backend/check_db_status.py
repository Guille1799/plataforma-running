"""Check database status and content."""
import sqlite3

conn = sqlite3.connect('runcoach.db')
cursor = conn.cursor()

# Get all tables
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('📊 Tablas en la base de datos:')
for table in tables:
    print(f'   - {table[0]}')

print('\n📈 Cantidad de registros:')

# Count users
cursor.execute('SELECT COUNT(*) FROM users')
users_count = cursor.fetchone()[0]
print(f'   Users: {users_count}')

# Count workouts
cursor.execute('SELECT COUNT(*) FROM workouts')
workouts_count = cursor.fetchone()[0]
print(f'   Workouts: {workouts_count}')

# Count health_metrics
cursor.execute('SELECT COUNT(*) FROM health_metrics')
health_count = cursor.fetchone()[0]
print(f'   Health Metrics: {health_count}')

# Count chat_messages
cursor.execute('SELECT COUNT(*) FROM chat_messages')
messages_count = cursor.fetchone()[0]
print(f'   Chat Messages: {messages_count}')

# Check health_metrics structure
print('\n🏥 Estructura de health_metrics:')
cursor.execute('PRAGMA table_info(health_metrics)')
columns = cursor.fetchall()
print(f'   Total columnas: {len(columns)}')
print('   Columnas principales:')
for col in columns[:10]:  # Show first 10 columns
    print(f'      - {col[1]} ({col[2]})')
if len(columns) > 10:
    print(f'   ... y {len(columns) - 10} más')

# Check users structure (show new token columns)
print('\n👤 Columnas de tokens en users:')
cursor.execute('PRAGMA table_info(users)')
user_columns = cursor.fetchall()
token_columns = [col for col in user_columns if 'token' in col[1] or 'strava' in col[1] or 'google_fit' in col[1] or 'apple_health' in col[1]]
for col in token_columns:
    print(f'   - {col[1]}')

# Show sample data if exists
if health_count > 0:
    print('\n📋 Últimas 3 métricas de salud:')
    cursor.execute('SELECT date, user_id, hrv_ms, resting_hr_bpm, sleep_duration_minutes, body_battery, source FROM health_metrics ORDER BY date DESC LIMIT 3')
    metrics = cursor.fetchall()
    for metric in metrics:
        print(f'   {metric[0]} - User {metric[1]}: HRV={metric[2]}, HR={metric[3]}, Sleep={metric[4]}min, BB={metric[5]}, Source={metric[6]}')

conn.close()

print('\n✅ Base de datos: backend/runcoach.db')
print(f'📦 Tamaño: ~96KB')
