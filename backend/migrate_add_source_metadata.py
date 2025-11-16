"""
Migration: Add source_type and data_quality columns to workouts table

This migration adds metadata to track the source and quality of workout data:
- source_type: Where the data came from (garmin_fit, gpx_upload, etc.)
- data_quality: Quality level of the data (high, medium, basic)
"""
import sqlite3
from datetime import datetime

DB_PATH = "runcoach.db"

def migrate():
    """Add source_type and data_quality columns to workouts table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(workouts)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'source_type' not in columns:
            print("Adding source_type column...")
            cursor.execute("""
                ALTER TABLE workouts 
                ADD COLUMN source_type TEXT DEFAULT 'garmin_fit'
            """)
            print("✓ source_type column added")
        else:
            print("✓ source_type column already exists")
        
        if 'data_quality' not in columns:
            print("Adding data_quality column...")
            cursor.execute("""
                ALTER TABLE workouts 
                ADD COLUMN data_quality TEXT DEFAULT 'high'
            """)
            print("✓ data_quality column added")
        else:
            print("✓ data_quality column already exists")
        
        # Update existing workouts based on available metrics
        print("\nUpdating existing workout metadata...")
        cursor.execute("""
            UPDATE workouts 
            SET source_type = CASE
                WHEN file_name LIKE '%.fit' THEN 'garmin_fit'
                WHEN file_name LIKE '%.gpx' THEN 'gpx_upload'
                WHEN file_name LIKE '%.tcx' THEN 'tcx_upload'
                ELSE 'garmin_oauth'
            END,
            data_quality = CASE
                WHEN avg_cadence IS NOT NULL OR avg_stance_time IS NOT NULL THEN 'high'
                WHEN avg_heart_rate IS NOT NULL THEN 'medium'
                ELSE 'basic'
            END
            WHERE source_type IS NULL OR data_quality IS NULL
        """)
        
        updated = cursor.rowcount
        print(f"✓ Updated {updated} existing workouts")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRATION: Add source metadata to workouts")
    print("=" * 60)
    migrate()
