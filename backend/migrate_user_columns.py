"""Add new columns to users table"""
from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    try:
        # Add User columns
        conn.execute(text('ALTER TABLE users ADD COLUMN height_cm REAL'))
        print('✅ Added height_cm')
    except Exception as e:
        print(f'⚠️  height_cm: {e}')
    
    try:
        conn.execute(text('ALTER TABLE users ADD COLUMN weight_kg REAL'))
        print('✅ Added weight_kg')
    except Exception as e:
        print(f'⚠️  weight_kg: {e}')
    
    try:
        conn.execute(text('ALTER TABLE users ADD COLUMN hr_zones TEXT'))
        print('✅ Added hr_zones')
    except Exception as e:
        print(f'⚠️  hr_zones: {e}')
    
    try:
        conn.execute(text('ALTER TABLE users ADD COLUMN power_zones TEXT'))
        print('✅ Added power_zones')
    except Exception as e:
        print(f'⚠️  power_zones: {e}')
    
    conn.commit()
    print('\n✅ Migration completed!')
