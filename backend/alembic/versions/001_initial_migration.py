"""Initial migration - Create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2025-01-27 12:00:00.000000

IMPORTANT: This is a placeholder migration file.

For EXISTING databases (tables already created via create_all()):
    1. Mark current state as migrated: `cd backend && alembic stamp head`
    2. Generate actual migration: `cd backend && alembic revision --autogenerate -m "Initial migration from models"`
    3. Review the generated migration in alembic/versions/
    4. Apply if needed: `cd backend && alembic upgrade head`

For NEW databases:
    1. Generate initial migration: `cd backend && alembic revision --autogenerate -m "Initial migration"`
    2. Review the generated migration
    3. Apply: `cd backend && alembic upgrade head`

See backend/alembic/README.md for detailed migration documentation.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create all initial tables.
    
    This migration creates all tables defined in app.models:
    - users (with role column)
    - workouts
    - chat_messages
    - health_metrics
    - events
    - training_plans (stored in user preferences JSON)
    
    NOTE: This is a placeholder. To generate the actual migration:
    1. If database is empty: `alembic revision --autogenerate -m "Initial migration"`
    2. If tables already exist: `alembic stamp head` then generate new migrations for future changes
    
    See backend/alembic/README.md for instructions.
    """
    # Placeholder - actual migration code should be generated with autogenerate
    # DO NOT manually add CREATE TABLE statements here
    # Use: alembic revision --autogenerate -m "Initial migration"
    pass


def downgrade() -> None:
    """
    Drop all tables.
    
    WARNING: This will delete all data! Only use in development.
    
    This is a placeholder. Actual downgrade code will be generated
    when you run `alembic revision --autogenerate` after creating the upgrade() function.
    """
    # Placeholder - actual downgrade code should be generated with autogenerate
    pass
