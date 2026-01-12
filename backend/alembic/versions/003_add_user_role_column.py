"""Add role column to users table

Revision ID: 003_add_user_role
Revises: 002_add_training_plans
Create Date: 2026-01-12 16:00:00.000000

This migration adds the 'role' column to the users table.
NOTE: This change was already applied manually to the database.
This migration documents the change for version control.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '003_add_user_role'
down_revision: Union[str, None] = '002_add_training_plans'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add role column to users table."""
    # Add role column with default value 'user'
    op.add_column('users', sa.Column('role', sa.String(), nullable=False, server_default='user'))
    
    # Create index on role column for faster queries
    op.create_index('idx_users_role', 'users', ['role'], unique=False)


def downgrade() -> None:
    """Remove role column from users table."""
    op.drop_index('idx_users_role', table_name='users')
    op.drop_column('users', 'role')
