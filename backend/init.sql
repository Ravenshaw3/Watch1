-- Watch1 Media Server Database Initialization
-- This script creates the initial database structure

-- Create database if it doesn't exist
-- (This is handled by the Docker environment variables)

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create indexes for better performance
-- These will be created by SQLAlchemy, but we can add custom ones here if needed

-- Insert initial data (if any)
-- For example, default admin user, default playlists, etc.

-- Note: The actual table creation is handled by SQLAlchemy models
-- This file is mainly for any custom database setup that needs to happen
-- before the application starts
