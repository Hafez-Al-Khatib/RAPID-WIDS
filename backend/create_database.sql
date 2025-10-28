-- Create RAPID database with PostGIS extension

CREATE DATABASE rapid_db
    WITH 
    ENCODING = 'UTF8'
    LC_COLLATE = 'English_United States.1252'
    LC_CTYPE = 'English_United States.1252';

-- Connect to the database and enable PostGIS
\c rapid_db

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Verify PostGIS is installed
SELECT PostGIS_Version();
