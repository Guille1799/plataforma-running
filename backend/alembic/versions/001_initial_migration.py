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
    
    This migration creates the base tables:
    - users (without role column - added in migration 003)
    - workouts
    - chat_messages
    - health_metrics
    
    NOTE: This migration documents the initial schema.
    The tables events and training_plans are created in separate migrations.
    """
    # Create users table (without role column - that's added in 003)
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        # Garmin fields
        sa.Column('garmin_email', sa.String(), nullable=True),
        sa.Column('garmin_token', sa.String(), nullable=True),
        sa.Column('garmin_connected_at', sa.DateTime(), nullable=True),
        sa.Column('last_garmin_sync', sa.DateTime(), nullable=True),
        # Athlete physical data
        sa.Column('height_cm', sa.Float(), nullable=True),
        sa.Column('weight_kg', sa.Float(), nullable=True),
        sa.Column('resting_heart_rate', sa.Integer(), nullable=True),
        sa.Column('vo2_max', sa.Float(), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('gender', sa.String(), nullable=True),
        sa.Column('hr_zones', sa.JSON(), nullable=True),
        sa.Column('power_zones', sa.JSON(), nullable=True),
        # Athlete profile
        sa.Column('running_level', sa.String(), nullable=True, server_default='intermediate'),
        sa.Column('max_heart_rate', sa.Integer(), nullable=True),
        sa.Column('goals', sa.JSON(), nullable=True),
        sa.Column('coaching_style', sa.String(), nullable=True, server_default='balanced'),
        sa.Column('injuries', sa.JSON(), nullable=True),
        sa.Column('preferences', sa.JSON(), nullable=True),
        # Strava fields
        sa.Column('strava_athlete_id', sa.Integer(), nullable=True),
        sa.Column('strava_access_token', sa.String(), nullable=True),
        sa.Column('strava_refresh_token', sa.String(), nullable=True),
        sa.Column('strava_token_expires_at', sa.DateTime(), nullable=True),
        sa.Column('strava_connected_at', sa.DateTime(), nullable=True),
        sa.Column('last_strava_sync', sa.DateTime(), nullable=True),
        # Google Fit fields
        sa.Column('google_fit_token', sa.String(), nullable=True),
        sa.Column('google_fit_refresh_token', sa.String(), nullable=True),
        sa.Column('google_fit_token_expires_at', sa.DateTime(), nullable=True),
        sa.Column('google_fit_connected_at', sa.DateTime(), nullable=True),
        sa.Column('last_google_fit_sync', sa.DateTime(), nullable=True),
        # Apple Health fields
        sa.Column('apple_health_connected_at', sa.DateTime(), nullable=True),
        sa.Column('last_apple_health_sync', sa.DateTime(), nullable=True),
        # Onboarding fields
        sa.Column('onboarding_completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('primary_device', sa.String(), nullable=True),
        sa.Column('use_case', sa.String(), nullable=True),
        sa.Column('coach_style_preference', sa.String(), nullable=True),
        sa.Column('language', sa.String(), nullable=False, server_default='es'),
        sa.Column('enable_notifications', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('integration_sources', sa.JSON(), nullable=True),
        sa.Column('onboarding_completed_at', sa.DateTime(), nullable=True),
        sa.Column('devices_configured', sa.JSON(), nullable=True),
        sa.Column('device_sync_config', sa.JSON(), nullable=True),
        sa.Column('device_sync_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # Create workouts table
    op.create_table(
        'workouts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('sport_type', sa.String(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('duration_seconds', sa.Integer(), nullable=False),
        sa.Column('distance_meters', sa.Float(), nullable=False),
        sa.Column('avg_heart_rate', sa.Integer(), nullable=True),
        sa.Column('max_heart_rate', sa.Integer(), nullable=True),
        sa.Column('avg_pace', sa.Float(), nullable=True),
        sa.Column('max_speed', sa.Float(), nullable=True),
        sa.Column('calories', sa.Float(), nullable=True),
        sa.Column('elevation_gain', sa.Float(), nullable=True),
        sa.Column('avg_cadence', sa.Float(), nullable=True),
        sa.Column('max_cadence', sa.Float(), nullable=True),
        sa.Column('avg_stance_time', sa.Float(), nullable=True),
        sa.Column('avg_vertical_oscillation', sa.Float(), nullable=True),
        sa.Column('avg_stride_length', sa.Float(), nullable=True),
        sa.Column('avg_leg_spring_stiffness', sa.Float(), nullable=True),
        sa.Column('left_right_balance', sa.Float(), nullable=True),
        sa.Column('source_type', sa.String(), nullable=True, server_default='garmin_fit'),
        sa.Column('data_quality', sa.String(), nullable=True, server_default='high'),
        sa.Column('file_name', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workouts_id'), 'workouts', ['id'], unique=False)
    op.create_index(op.f('ix_workouts_user_id'), 'workouts', ['user_id'], unique=False)
    op.create_index('ix_workouts_user_id_start_time', 'workouts', ['user_id', 'start_time'], unique=False)
    op.create_index('ix_workouts_start_time', 'workouts', ['start_time'], unique=False)
    
    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_messages_id'), 'chat_messages', ['id'], unique=False)
    op.create_index(op.f('ix_chat_messages_user_id'), 'chat_messages', ['user_id'], unique=False)
    op.create_index('ix_chat_messages_user_id_created_at', 'chat_messages', ['user_id', 'created_at'], unique=False)
    
    # Create health_metrics table
    op.create_table(
        'health_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        # Recovery metrics
        sa.Column('hrv_ms', sa.Float(), nullable=True),
        sa.Column('resting_hr_bpm', sa.Integer(), nullable=True),
        sa.Column('hrv_baseline_ms', sa.Float(), nullable=True),
        sa.Column('resting_hr_baseline_bpm', sa.Integer(), nullable=True),
        # Sleep metrics
        sa.Column('sleep_duration_minutes', sa.Integer(), nullable=True),
        sa.Column('sleep_score', sa.Integer(), nullable=True),
        sa.Column('deep_sleep_minutes', sa.Integer(), nullable=True),
        sa.Column('rem_sleep_minutes', sa.Integer(), nullable=True),
        sa.Column('light_sleep_minutes', sa.Integer(), nullable=True),
        sa.Column('awake_minutes', sa.Integer(), nullable=True),
        # Readiness metrics
        sa.Column('body_battery', sa.Integer(), nullable=True),
        sa.Column('readiness_score', sa.Integer(), nullable=True),
        sa.Column('stress_level', sa.Integer(), nullable=True),
        sa.Column('recovery_score', sa.Integer(), nullable=True),
        # Activity metrics
        sa.Column('steps', sa.Integer(), nullable=True),
        sa.Column('calories_burned', sa.Integer(), nullable=True),
        sa.Column('active_calories', sa.Integer(), nullable=True),
        sa.Column('intensity_minutes', sa.Integer(), nullable=True),
        # Respiratory metrics
        sa.Column('respiration_rate', sa.Float(), nullable=True),
        sa.Column('spo2_percentage', sa.Float(), nullable=True),
        # Subjective metrics
        sa.Column('energy_level', sa.Integer(), nullable=True),
        sa.Column('soreness_level', sa.Integer(), nullable=True),
        sa.Column('mood', sa.Integer(), nullable=True),
        sa.Column('motivation', sa.Integer(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        # Metadata
        sa.Column('source', sa.String(), nullable=False, server_default='manual'),
        sa.Column('data_quality', sa.String(), nullable=False, server_default='basic'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'date', name='uix_user_date_health')
    )
    op.create_index(op.f('ix_health_metrics_id'), 'health_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_health_metrics_user_id'), 'health_metrics', ['user_id'], unique=False)
    op.create_index('ix_health_metrics_user_id_date', 'health_metrics', ['user_id', 'date'], unique=False)


def downgrade() -> None:
    """
    Drop all initial tables.
    
    WARNING: This will delete all data! Only use in development.
    """
    op.drop_index('ix_health_metrics_user_id_date', table_name='health_metrics')
    op.drop_index(op.f('ix_health_metrics_user_id'), table_name='health_metrics')
    op.drop_index(op.f('ix_health_metrics_id'), table_name='health_metrics')
    op.drop_table('health_metrics')
    
    op.drop_index('ix_chat_messages_user_id_created_at', table_name='chat_messages')
    op.drop_index(op.f('ix_chat_messages_user_id'), table_name='chat_messages')
    op.drop_index(op.f('ix_chat_messages_id'), table_name='chat_messages')
    op.drop_table('chat_messages')
    
    op.drop_index('ix_workouts_start_time', table_name='workouts')
    op.drop_index('ix_workouts_user_id_start_time', table_name='workouts')
    op.drop_index(op.f('ix_workouts_user_id'), table_name='workouts')
    op.drop_index(op.f('ix_workouts_id'), table_name='workouts')
    op.drop_table('workouts')
    
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
