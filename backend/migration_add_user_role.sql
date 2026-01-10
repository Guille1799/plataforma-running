-- Migration: Add role field to users table
-- Run this in PostgreSQL: docker exec -i runcoach_db psql -U runcoach -d runcoach < migration_add_user_role.sql
-- Or for SQLite: sqlite3 runcoach.db < migration_add_user_role.sql

-- Add role column to users table with default value 'user'
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR NOT NULL DEFAULT 'user';

-- Create index on role column for faster queries
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Update existing users to have 'user' role (only if NULL, though default should handle this)
UPDATE users SET role = 'user' WHERE role IS NULL;

-- Optional: Set specific users as admin (replace with actual admin email)
-- UPDATE users SET role = 'admin' WHERE email = 'admin@example.com';
