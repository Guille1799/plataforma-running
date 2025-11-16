"""Add form metrics columns to workouts table"""
from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    try:
        conn.execute(text('ALTER TABLE workouts ADD COLUMN avg_cadence REAL'))
        print('✅ Added avg_cadence')
    except Exception as e:
        print(f'⚠️  avg_cadence: {e}')
    
    try:
        conn.execute(text('ALTER TABLE workouts ADD COLUMN max_cadence REAL'))
        print('✅ Added max_cadence')
    except Exception as e:
        print(f'⚠️  max_cadence: {e}')
    
    try:
        conn.execute(text('ALTER TABLE workouts ADD COLUMN avg_stance_time REAL'))
        print('✅ Added avg_stance_time')
    except Exception as e:
        print(f'⚠️  avg_stance_time: {e}')
    
    try:
        conn.execute(text('ALTER TABLE workouts ADD COLUMN avg_vertical_oscillation REAL'))
        print('✅ Added avg_vertical_oscillation')
    except Exception as e:
        print(f'⚠️  avg_vertical_oscillation: {e}')
    
    try:
        conn.execute(text('ALTER TABLE workouts ADD COLUMN avg_leg_spring_stiffness REAL'))
        print('✅ Added avg_leg_spring_stiffness')
    except Exception as e:
        print(f'⚠️  avg_leg_spring_stiffness: {e}')
    
    try:
        conn.execute(text('ALTER TABLE workouts ADD COLUMN left_right_balance REAL'))
        print('✅ Added left_right_balance')
    except Exception as e:
        print(f'⚠️  left_right_balance: {e}')
    
    conn.commit()
    print('\n✅ Migration completed!')
