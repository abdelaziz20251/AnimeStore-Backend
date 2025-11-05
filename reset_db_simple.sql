-- SIMPLE RESET: Drop all tables in public schema
-- Run this in Supabase SQL Editor

-- This will drop ALL tables including Django's django_migrations table
-- After running this, your next deployment will run migrations fresh

DO $$ 
DECLARE 
    r RECORD;
BEGIN
    -- Drop all tables
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') 
    LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;
    
    -- Drop all sequences
    FOR r IN (SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public') 
    LOOP
        EXECUTE 'DROP SEQUENCE IF EXISTS ' || quote_ident(r.sequence_name) || ' CASCADE';
    END LOOP;
END $$;

-- Verify tables are dropped
SELECT 'Database reset complete! All tables dropped.' AS status;

