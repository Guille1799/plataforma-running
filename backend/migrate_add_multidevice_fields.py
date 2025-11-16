#!/usr/bin/env python
"""
Migration: Add multi-device sync configuration to users table
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = "runcoach.db"

def migrate():
    """Add multi-device fields to users table."""
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get current columns
        cursor.execute("PRAGMA table_info(users)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        print(f"Existing columns: {len(existing_columns)}")
        
        # Fields to add
        new_columns = [
            ("devices_configured", "JSON"),
            ("device_sync_config", "JSON"),
            ("device_sync_enabled", "BOOLEAN DEFAULT 1"),
        ]
        
        # Add columns if they don't exist
        for col_name, col_type in new_columns:
            if col_name not in existing_columns:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                print(f"[+] Added column: {col_name}")
            else:
                print(f"[~] Column already exists: {col_name}")
        
        conn.commit()
        
        # Verify
        cursor.execute("PRAGMA table_info(users)")
        final_columns = {row[1] for row in cursor.fetchall()}
        print(f"\n[OK] Migration complete!")
        print(f"Final column count: {len(final_columns)}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error during migration: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("[*] Starting migration...\n")
    success = migrate()
    exit(0 if success else 1)
