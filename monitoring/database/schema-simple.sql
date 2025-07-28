-- Norwegian Dam Health Monitoring System - Simple PostgreSQL Schema
-- Compatible with Apple Silicon and standard PostgreSQL

-- Extensions (PostGIS may not be available, so we'll use basic types)
-- CREATE EXTENSION IF NOT EXISTS postgis CASCADE;

-- Main dam registry
CREATE TABLE dams (
    dam_id VARCHAR(50) PRIMARY KEY,
    dam_name VARCHAR(200),
    dam_type VARCHAR(50),
    construction_year INTEGER,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    region VARCHAR(50),
    owner VARCHAR(200),
    capacity_mw DECIMAL(10, 2),
    reservoir_area_km2 DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_dams_region ON dams (region);
CREATE INDEX idx_dams_construction_year ON dams (construction_year);

-- Health scores
CREATE TABLE health_scores (
    id SERIAL PRIMARY KEY,
    time TIMESTAMPTZ NOT NULL,
    dam_id VARCHAR(50) REFERENCES dams(dam_id),
    overall_score DECIMAL(5, 2),
    risk_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_health_scores_dam_time ON health_scores (dam_id, time DESC);

-- Weather data (from Norwegian APIs)
CREATE TABLE weather_data (
    id SERIAL PRIMARY KEY,
    time TIMESTAMPTZ NOT NULL,
    dam_id VARCHAR(50) REFERENCES dams(dam_id),
    temperature_c DECIMAL(5, 2),
    precipitation_mm DECIMAL(8, 2),
    wind_speed_ms DECIMAL(6, 2),
    humidity_percent DECIMAL(5, 2),
    data_source VARCHAR(50) DEFAULT 'met.no',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_weather_dam_time ON weather_data (dam_id, time DESC);

-- Sample view for current health
CREATE OR REPLACE VIEW current_dam_health AS
SELECT DISTINCT ON (dam_id)
    dam_id,
    time,
    overall_score,
    risk_level
FROM health_scores
ORDER BY dam_id, time DESC;

-- Insert some sample data
INSERT INTO dams (dam_id, dam_name, latitude, longitude, construction_year, region) VALUES 
('DEMO_001', 'Demo Dam 1', 60.1699, 9.9603, 1950, 'Østlandet'),
('DEMO_002', 'Demo Dam 2', 61.2181, 9.4141, 1965, 'Trøndelag'),
('DEMO_003', 'Demo Dam 3', 59.9139, 10.7522, 1970, 'Oslo');

-- Insert sample health scores
INSERT INTO health_scores (time, dam_id, overall_score, risk_level) VALUES 
(NOW(), 'DEMO_001', 85.5, 'low'),
(NOW(), 'DEMO_002', 92.1, 'very_low'),
(NOW(), 'DEMO_003', 78.9, 'medium');

COMMIT;
