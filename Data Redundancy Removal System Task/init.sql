-- Initialize database for PostgreSQL
-- This file is automatically executed when the PostgreSQL container starts

-- Create extensions for better text processing
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Create indexes for better performance
-- These will be created by SQLAlchemy, but we can add additional ones here

-- Example: Create trigram index for faster text similarity searches (PostgreSQL specific)
-- CREATE INDEX IF NOT EXISTS idx_content_trgm ON data_entries USING gin (content gin_trgm_ops);

-- Set up logging
-- The application will create its own tables
