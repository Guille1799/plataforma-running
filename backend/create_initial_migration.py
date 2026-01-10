#!/usr/bin/env python3
"""
Helper script to create the initial Alembic migration.

This script helps create the initial migration from existing models.
It's a wrapper around `alembic revision --autogenerate`.

Usage:
    python create_initial_migration.py

Or manually:
    cd backend
    alembic revision --autogenerate -m "Initial migration - Create all tables"
    alembic upgrade head
"""

import subprocess
import sys
import os

def main():
    """Create initial Alembic migration."""
    # Change to backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    print("🔧 Creating initial Alembic migration...")
    print(f"📁 Working directory: {os.getcwd()}")
    print()
    
    # Check if alembic.ini exists
    if not os.path.exists("alembic.ini"):
        print("❌ Error: alembic.ini not found!")
        print("   Alembic must be initialized first.")
        return 1
    
    # Check if tables already exist (warning)
    print("⚠️  NOTE: If tables already exist (created via create_all):")
    print("   1. Mark migration as applied: alembic stamp head")
    print("   2. Then create new migrations for future changes")
    print()
    
    # Run alembic revision --autogenerate
    try:
        print("🚀 Running: alembic revision --autogenerate -m 'Initial migration - Create all tables'")
        result = subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", "Initial migration - Create all tables"],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        
        print("✅ Migration created successfully!")
        print()
        print("📝 Next steps:")
        print("   1. Review the generated migration file in alembic/versions/")
        print("   2. Edit if necessary (remove operations that already exist)")
        print("   3. Apply migration: alembic upgrade head")
        print()
        print("   Or if tables already exist, mark as applied:")
        print("   alembic stamp head")
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating migration:")
        print(e.stderr)
        return 1
    except FileNotFoundError:
        print("❌ Error: Alembic command not found!")
        print("   Make sure alembic is installed: pip install alembic")
        return 1


if __name__ == "__main__":
    sys.exit(main())
