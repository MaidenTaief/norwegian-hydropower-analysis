-- Norwegian Dam Health Monitoring System - Basic Database Schema
-- TimescaleDB with PostGIS for spatial time-series data

-- Extensions
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
CREATE EXTENSION IF NOT EXISTS postgis CASCADE;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp" CASCADE;

-- Main dam registry
CREATE TABLE dams (
    dam_id VARCHAR(50) PRIMARY KEY,
    dam_name VARCHAR(200),
    dam_type VARCHAR(50),
    construction_year INTEGER,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    location GEOGRAPHY(POINT, 4326),
    region VARCHAR(50),
    owner VARCHAR(200),
    capacity_mw DECIMAL(10, 2),
    reservoir_area_km2 DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Spatial index
CREATE INDEX idx_dams_location ON dams USING GIST (location);

-- Health scores
CREATE TABLE health_scores (
    time TIMESTAMPTZ NOT NULL,
    dam_id VARCHAR(50) REFERENCES dams(dam_id),
    overall_score DECIMAL(5, 2),
    risk_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Convert to hypertable
SELECT create_hypertable('health_scores', 'time');

-- Weather data
CREATE TABLE weather_data (
    time TIMESTAMPTZ NOT NULL,
    dam_id VARCHAR(50) REFERENCES dams(dam_id),
    temperature_c DECIMAL(5, 2),
    precipitation_mm DECIMAL(8, 2),
    data_source VARCHAR(50) DEFAULT 'met.no'
);

SELECT create_hypertable('weather_data', 'time');

-- Sample view
CREATE OR REPLACE VIEW current_dam_health AS
SELECT DISTINCT ON (dam_id)
    dam_id,
    time,
    overall_score,
    risk_level
FROM health_scores
ORDER BY dam_id, time DESC;

COMMIT;
