"""
Database Migration: Add Health Metrics Support
================================================

This script adds health metrics tracking functionality to the database:
1. Adds health platform integration fields to User model
2. Creates HealthMetric table for daily wellness data

Run this script to upgrade your database schema.
"""
import sqlite3
from datetime import datetime


def migrate_database(db_path: str = "runcoach.db"):
    """Add health metrics support to database."""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"[MIGRATION] Starting health metrics migration on {db_path}")
    
    # ========================================================================
    # 1. Add health platform fields to users table
    # ========================================================================
    
    user_columns_to_add = [
        ("strava_athlete_id", "INTEGER"),
        ("strava_access_token", "TEXT"),
        ("strava_refresh_token", "TEXT"),
        ("strava_token_expires_at", "TIMESTAMP"),
        ("strava_connected_at", "TIMESTAMP"),
        ("last_strava_sync", "TIMESTAMP"),
        ("google_fit_token", "TEXT"),
        ("google_fit_refresh_token", "TEXT"),
        ("google_fit_token_expires_at", "TIMESTAMP"),
        ("google_fit_connected_at", "TIMESTAMP"),
        ("last_google_fit_sync", "TIMESTAMP"),
        ("apple_health_connected_at", "TIMESTAMP"),
        ("last_apple_health_sync", "TIMESTAMP"),
    ]
    
    for column_name, column_type in user_columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")
            print(f"[MIGRATION] ✅ Added users.{column_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"[MIGRATION] ⏭️  Column users.{column_name} already exists, skipping")
            else:
                raise
    
    conn.commit()
    
    # ========================================================================
    # 2. Create health_metrics table
    # ========================================================================
    
    create_health_metrics_table = """
    CREATE TABLE IF NOT EXISTS health_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date DATE NOT NULL,
        
        -- Recovery Metrics
        hrv_ms REAL,
        resting_hr_bpm INTEGER,
        hrv_baseline_ms REAL,
        resting_hr_baseline_bpm INTEGER,
        
        -- Sleep Metrics
        sleep_duration_minutes INTEGER,
        sleep_score INTEGER,
        deep_sleep_minutes INTEGER,
        rem_sleep_minutes INTEGER,
        light_sleep_minutes INTEGER,
        awake_minutes INTEGER,
        
        -- Readiness Metrics
        body_battery INTEGER,
        readiness_score INTEGER,
        stress_level INTEGER,
        recovery_score INTEGER,
        
        -- Activity Metrics
        steps INTEGER,
        calories_burned INTEGER,
        active_calories INTEGER,
        intensity_minutes INTEGER,
        
        -- Respiratory Metrics
        respiration_rate REAL,
        spo2_percentage REAL,
        
        -- Subjective Metrics (Manual Entry)
        energy_level INTEGER,
        soreness_level INTEGER,
        mood INTEGER,
        motivation INTEGER,
        notes TEXT,
        
        -- Metadata
        source TEXT NOT NULL DEFAULT 'manual',
        data_quality TEXT NOT NULL DEFAULT 'basic',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        FOREIGN KEY (user_id) REFERENCES users (id),
        UNIQUE (user_id, date)
    )
    """
    
    try:
        cursor.execute(create_health_metrics_table)
        print("[MIGRATION] ✅ Created health_metrics table")
    except sqlite3.OperationalError as e:
        if "already exists" in str(e).lower():
            print("[MIGRATION] ⏭️  health_metrics table already exists")
        else:
            raise
    
    conn.commit()
    
    # ========================================================================
    # 3. Create indexes for performance
    # ========================================================================
    
    indexes = [
        ("idx_health_metrics_user_date", "health_metrics", "user_id, date"),
        ("idx_health_metrics_date", "health_metrics", "date"),
        ("idx_users_strava_athlete", "users", "strava_athlete_id"),
    ]
    
    for index_name, table_name, columns in indexes:
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({columns})")
            print(f"[MIGRATION] ✅ Created index {index_name}")
        except sqlite3.OperationalError as e:
            print(f"[MIGRATION] ⚠️  Index {index_name}: {e}")
    
    conn.commit()
    
    # ========================================================================
    # 4. Verify migration
    # ========================================================================
    
    # Check users table columns
    cursor.execute("PRAGMA table_info(users)")
    user_columns = {row[1] for row in cursor.fetchall()}
    
    required_user_cols = {col[0] for col in user_columns_to_add}
    missing_user_cols = required_user_cols - user_columns
    
    if missing_user_cols:
        print(f"[MIGRATION] ⚠️  Missing user columns: {missing_user_cols}")
    else:
        print("[MIGRATION] ✅ All user columns present")
    
    # Check health_metrics table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='health_metrics'")
    if cursor.fetchone():
        print("[MIGRATION] ✅ health_metrics table verified")
        
        # Count columns
        cursor.execute("PRAGMA table_info(health_metrics)")
        health_cols = cursor.fetchall()
        print(f"[MIGRATION] ℹ️  health_metrics has {len(health_cols)} columns")
    else:
        print("[MIGRATION] ❌ health_metrics table NOT found")
    
    conn.close()
    
    print("\n" + "="*70)
    print("MIGRATION COMPLETE ✅")
    print("="*70)
    print("\nNext steps:")
    print("1. Restart your backend server")
    print("2. Health metrics endpoints are now available at /health/*")
    print("3. Users can connect Garmin, Google Fit, or Apple Health")
    print("4. AI Coach will use health data for personalized recommendations")
    print("\nAvailable sync methods:")
    print("  - Garmin: POST /health/sync/garmin")
    print("  - Google Fit: GET /health/connect/google-fit → POST /health/sync/google-fit")
    print("  - Apple Health: POST /health/import/apple-health (upload export.xml)")
    print("  - Manual: POST /health/manual (daily check-in)")


if __name__ == "__main__":
    import sys
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else "runcoach.db"
    
    print(f"Running migration on: {db_path}\n")
    migrate_database(db_path)
