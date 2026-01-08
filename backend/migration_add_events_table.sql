-- Migration: Add events table for race management
-- Run this in PostgreSQL: docker exec -i runcoach_db psql -U runcoach_user -d runcoach < migration_add_events_table.sql

-- Enable unaccent extension for accent-insensitive search
CREATE EXTENSION IF NOT EXISTS unaccent;

-- Create events table
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    location VARCHAR(100) NOT NULL,
    region VARCHAR(100),
    country VARCHAR(100) NOT NULL DEFAULT 'España',
    date DATE NOT NULL,
    distance_km FLOAT NOT NULL CHECK (distance_km > 0),
    elevation_m INTEGER CHECK (elevation_m >= 0),
    participants_estimate INTEGER CHECK (participants_estimate >= 0),
    registration_url TEXT,
    website_url TEXT,
    description TEXT,
    price_eur FLOAT CHECK (price_eur >= 0),
    source VARCHAR(50) NOT NULL DEFAULT 'official',
    verified BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better search performance
CREATE INDEX IF NOT EXISTS idx_events_date ON events(date);
CREATE INDEX IF NOT EXISTS idx_events_external_id ON events(external_id);
CREATE INDEX IF NOT EXISTS idx_events_name ON events(name);
CREATE INDEX IF NOT EXISTS idx_events_location ON events(location);
CREATE INDEX IF NOT EXISTS idx_events_verified ON events(verified);
CREATE INDEX IF NOT EXISTS idx_events_distance ON events(distance_km);

-- Create index for text search (using gin for better performance)
CREATE INDEX IF NOT EXISTS idx_events_name_trgm ON events USING gin (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_events_location_trgm ON events USING gin (location gin_trgm_ops);

-- Enable pg_trgm for fuzzy text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_events_updated_at BEFORE UPDATE ON events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;
