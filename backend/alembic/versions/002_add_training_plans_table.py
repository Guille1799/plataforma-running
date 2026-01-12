"""Add training_plans table

Revision ID: 002_add_training_plans
Revises: 001_initial
Create Date: 2025-01-27 15:00:00.000000

This migration adds the training_plans table to store AI-generated training plans
separately from user.preferences JSON column.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_add_training_plans'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create training_plans table."""
    # Create training_plans table
    op.create_table(
        'training_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.String(), nullable=False),
        sa.Column('plan_name', sa.String(), nullable=False),
        sa.Column('goal_type', sa.String(), nullable=False),
        sa.Column('goal_date', sa.DateTime(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('total_weeks', sa.Integer(), nullable=False),
        sa.Column('current_week', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status', sa.String(), nullable=False, server_default='active'),
        sa.Column('plan_data', sa.JSON(), nullable=False),
        sa.Column('metrics', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_training_plans_id'), 'training_plans', ['id'], unique=False)
    op.create_index(op.f('ix_training_plans_user_id'), 'training_plans', ['user_id'], unique=False)
    op.create_index(op.f('ix_training_plans_plan_id'), 'training_plans', ['plan_id'], unique=True)
    op.create_index('ix_training_plans_user_status', 'training_plans', ['user_id', 'status'], unique=False)
    op.create_index('ix_training_plans_start_date', 'training_plans', ['start_date'], unique=False)


def downgrade() -> None:
    """Drop training_plans table."""
    op.drop_index('ix_training_plans_start_date', table_name='training_plans')
    op.drop_index('ix_training_plans_user_status', table_name='training_plans')
    op.drop_index(op.f('ix_training_plans_plan_id'), table_name='training_plans')
    op.drop_index(op.f('ix_training_plans_user_id'), table_name='training_plans')
    op.drop_index(op.f('ix_training_plans_id'), table_name='training_plans')
    op.drop_table('training_plans')
