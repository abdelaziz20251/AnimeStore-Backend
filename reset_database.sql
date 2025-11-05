-- Reset Supabase Database - Run this in Supabase SQL Editor
-- WARNING: This will delete ALL data and tables!

-- Drop all Django tables
DROP TABLE IF EXISTS django_migrations CASCADE;
DROP TABLE IF EXISTS django_content_type CASCADE;
DROP TABLE IF EXISTS django_session CASCADE;
DROP TABLE IF EXISTS auth_permission CASCADE;
DROP TABLE IF EXISTS auth_group CASCADE;
DROP TABLE IF EXISTS auth_group_permissions CASCADE;
DROP TABLE IF EXISTS auth_user_groups CASCADE;
DROP TABLE IF EXISTS auth_user_user_permissions CASCADE;

-- Drop all custom app tables
DROP TABLE IF EXISTS users_user CASCADE;
DROP TABLE IF EXISTS products_category CASCADE;
DROP TABLE IF EXISTS products_product CASCADE;
DROP TABLE IF EXISTS products_productimage CASCADE;
DROP TABLE IF EXISTS products_productreview CASCADE;
DROP TABLE IF EXISTS orders_cart CASCADE;
DROP TABLE IF EXISTS orders_cartitem CASCADE;
DROP TABLE IF EXISTS orders_order CASCADE;
DROP TABLE IF EXISTS orders_orderitem CASCADE;
DROP TABLE IF EXISTS orders_orderstatushistory CASCADE;
DROP TABLE IF EXISTS orders_refund CASCADE;
DROP TABLE IF EXISTS sellers_sellerprofile CASCADE;
DROP TABLE IF EXISTS sellers_sellerpayout CASCADE;
DROP TABLE IF EXISTS analytics_productview CASCADE;
DROP TABLE IF EXISTS analytics_searchquery CASCADE;
DROP TABLE IF EXISTS analytics_cartactivitylog CASCADE;
DROP TABLE IF EXISTS token_blacklist_outstandingtoken CASCADE;
DROP TABLE IF EXISTS token_blacklist_blacklistedtoken CASCADE;

-- Drop all sequences (if any)
DO $$ 
DECLARE 
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') 
    LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;
END $$;

-- Drop all sequences
DO $$ 
DECLARE 
    r RECORD;
BEGIN
    FOR r IN (SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public') 
    LOOP
        EXECUTE 'DROP SEQUENCE IF EXISTS ' || quote_ident(r.sequence_name) || ' CASCADE';
    END LOOP;
END $$;

