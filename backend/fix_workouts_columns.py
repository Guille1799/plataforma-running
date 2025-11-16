import sqlite3

conn = sqlite3.connect('runcoach.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(workouts)")
cols = cursor.fetchall()

print('\n=== Workouts Table Columns ===')
for col in cols:
    name, typ = col[1], col[2]
    print(f'  {name}: {typ}')

print(f'\nTotal: {len(cols)} columns')

missing_source = not any(col[1] == 'source_type' for col in cols)
missing_quality = not any(col[1] == 'data_quality' for col in cols)

print(f'\nMissing source_type: {missing_source}')
print(f'Missing data_quality: {missing_quality}')

if missing_source or missing_quality:
    print('\n=== Adding missing columns ===')
    if missing_source:
        try:
            cursor.execute("ALTER TABLE workouts ADD COLUMN source_type TEXT DEFAULT 'garmin_fit'")
            print('✅ Added source_type')
        except Exception as e:
            print(f'⚠️  source_type: {e}')
    
    if missing_quality:
        try:
            cursor.execute("ALTER TABLE workouts ADD COLUMN data_quality TEXT DEFAULT 'high'")
            print('✅ Added data_quality')
        except Exception as e:
            print(f'⚠️  data_quality: {e}')
    
    conn.commit()
    print('\n✅ Migration completed!')
else:
    print('\n✅ All columns already exist!')

conn.close()
