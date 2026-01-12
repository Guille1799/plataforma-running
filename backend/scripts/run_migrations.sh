#!/bin/bash
# Script to run Alembic migrations before starting the server
# This ensures the database schema is up to date

set -e  # Exit on error

echo "🔄 Running database migrations..."

# Change to backend directory (where alembic.ini is located)
cd /app

# Run migrations
python -m alembic upgrade head

echo "✅ Migrations completed successfully"
