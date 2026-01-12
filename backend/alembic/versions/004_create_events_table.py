"""Create events table for race management

Revision ID: 004_create_events
Revises: 003_add_user_role
Create Date: 2026-01-12 16:00:00.000000

This migration creates the events table for storing running races and events.
NOTE: This change was already applied manually to the database.
This migration documents the change for version control.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004_create_events'
down_revision: Union[str, None] = '003_add_user_role'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create events table."""
    # Enable unaccent extension for accent-insensitive search (PostgreSQL only)
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
    
    # Enable pg_trgm for fuzzy text search (PostgreSQL only)
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    
    # Create events table
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('external_id', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('location', sa.String(length=100), nullable=False),
        sa.Column('region', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=False, server_default='España'),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('distance_km', sa.Float(), nullable=False),
        sa.Column('elevation_m', sa.Integer(), nullable=True),
        sa.Column('participants_estimate', sa.Integer(), nullable=True),
        sa.Column('registration_url', sa.Text(), nullable=True),
        sa.Column('website_url', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price_eur', sa.Float(), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=False, server_default='official'),
        sa.Column('verified', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id')
    )
    
    # Create indexes for better search performance
    op.create_index('idx_events_date', 'events', ['date'], unique=False)
    op.create_index('idx_events_external_id', 'events', ['external_id'], unique=True)
    op.create_index('idx_events_name', 'events', ['name'], unique=False)
    op.create_index('idx_events_location', 'events', ['location'], unique=False)
    op.create_index('idx_events_verified', 'events', ['verified'], unique=False)
    op.create_index('idx_events_distance', 'events', ['distance_km'], unique=False)
    op.create_index('ix_events_date_verified', 'events', ['date', 'verified'], unique=False)
    op.create_index('ix_events_country_date', 'events', ['country', 'date'], unique=False)
    
    # Create trigger function for updated_at (PostgreSQL only)
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    # Create trigger for updated_at
    op.execute("""
        CREATE TRIGGER update_events_updated_at 
        BEFORE UPDATE ON events
        FOR EACH ROW 
        EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    """Drop events table and related objects."""
    op.execute("DROP TRIGGER IF EXISTS update_events_updated_at ON events")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")
    op.drop_index('ix_events_country_date', table_name='events')
    op.drop_index('ix_events_date_verified', table_name='events')
    op.drop_index('idx_events_distance', table_name='events')
    op.drop_index('idx_events_verified', table_name='events')
    op.drop_index('idx_events_location', table_name='events')
    op.drop_index('idx_events_name', table_name='events')
    op.drop_index('idx_events_external_id', table_name='events')
    op.drop_index('idx_events_date', table_name='events')
    op.drop_table('events')
