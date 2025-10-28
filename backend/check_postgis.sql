-- Check if PostGIS extension exists in rapid_db
\c rapid_db
SELECT extname, extversion FROM pg_extension WHERE extname = 'postgis';
SHOW search_path;
