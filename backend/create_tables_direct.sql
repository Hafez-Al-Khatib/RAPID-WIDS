-- Ensure PostGIS is enabled
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create tables directly with SQL

CREATE TABLE IF NOT EXISTS damage_reports (
    id SERIAL PRIMARY KEY,
    image_path VARCHAR(500) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    location geometry(POINT,4326) NOT NULL,
    damage_severity INTEGER NOT NULL CHECK (damage_severity >= 0 AND damage_severity <= 4),
    confidence FLOAT CHECK (confidence >= 0.0 AND confidence <= 1.0),
    verified BOOLEAN DEFAULT FALSE,
    description TEXT,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    source VARCHAR(50) CHECK (source IN ('user_upload', 'satellite', 'simulation', 'crowdsourced')) DEFAULT 'user_upload'
);

CREATE INDEX IF NOT EXISTS idx_damage_location ON damage_reports USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_damage_severity ON damage_reports(damage_severity);
CREATE INDEX IF NOT EXISTS idx_damage_timestamp ON damage_reports(timestamp);

CREATE TABLE IF NOT EXISTS road_status (
    id SERIAL PRIMARY KEY,
    road_id VARCHAR(100) UNIQUE NOT NULL,
    start_lat FLOAT NOT NULL,
    start_lon FLOAT NOT NULL,
    end_lat FLOAT NOT NULL,
    end_lon FLOAT NOT NULL,
    geometry geometry(LINESTRING,4326) NOT NULL,
    status VARCHAR(20) CHECK (status IN ('open', 'blocked', 'damaged', 'under_repair')) DEFAULT 'open',
    severity INTEGER CHECK (severity >= 0 AND severity <= 5) DEFAULT 0,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    source VARCHAR(50) CHECK (source IN ('crowdsourced', 'official', 'satellite', 'sensor')) DEFAULT 'crowdsourced'
);

CREATE INDEX IF NOT EXISTS idx_road_geometry ON road_status USING GIST(geometry);
CREATE INDEX IF NOT EXISTS idx_road_status ON road_status(status);

CREATE TABLE IF NOT EXISTS supply_points (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    location geometry(POINT,4326) NOT NULL,
    type VARCHAR(50) CHECK (type IN ('warehouse', 'hospital', 'shelter', 'affected_area', 'distribution_center')) NOT NULL,
    demand INTEGER CHECK (demand >= 0) DEFAULT 0,
    capacity INTEGER CHECK (capacity >= 0) DEFAULT 0,
    priority INTEGER CHECK (priority >= 1 AND priority <= 5) DEFAULT 1,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_supply_location ON supply_points USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_supply_type ON supply_points(type);
CREATE INDEX IF NOT EXISTS idx_supply_priority ON supply_points(priority);

-- Verify tables created
SELECT tablename FROM pg_tables WHERE schemaname = 'public';
