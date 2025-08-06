-- =====================================================================================
-- NORWEGIAN DAM HEALTH MONITORING SYSTEM - DATABASE SCHEMA
-- =====================================================================================
-- Complete TimescaleDB schema for real-time dam health monitoring
-- Designed for Norwegian hydropower infrastructure (4,953 dams)
-- 
-- Data Sources: NVE, met.no, Frost API, Sentinel Hub, VARSOM
-- =====================================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS btree_gist;

-- =====================================================================================
-- CORE INFRASTRUCTURE TABLES
-- =====================================================================================

-- Norwegian dams master table (from NVE data)
CREATE TABLE IF NOT EXISTS dams (
    dam_id SERIAL PRIMARY KEY,
    nve_dam_nr VARCHAR(50) UNIQUE,              -- NVE dam number
    dam_name VARCHAR(255),                      -- Norwegian dam name
    location GEOGRAPHY(POINT, 4326),            -- GPS coordinates
    municipality VARCHAR(100),                  -- Kommune
    county VARCHAR(100),                        -- Fylke
    owner VARCHAR(255),                         -- Dam owner
    construction_year INTEGER,                  -- Construction year
    dam_height_m DECIMAL(8,2),                 -- Height in meters
    reservoir_capacity_m3 DECIMAL(15,2),       -- Capacity in cubic meters
    power_capacity_mw DECIMAL(10,2),           -- Power generation capacity
    dam_type VARCHAR(100),                      -- Type of dam
    status VARCHAR(50) DEFAULT 'active',        -- operational status
    risk_level VARCHAR(20) DEFAULT 'medium',    -- risk assessment
    last_inspection DATE,                       -- Last inspection date
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sensor installations on dams
CREATE TABLE IF NOT EXISTS sensors (
    sensor_id SERIAL PRIMARY KEY,
    dam_id INTEGER REFERENCES dams(dam_id),
    sensor_type VARCHAR(50) NOT NULL,           -- 'water_level', 'seismic', 'weather', 'structural'
    sensor_name VARCHAR(100),                   -- Human readable name
    location GEOGRAPHY(POINT, 4326),            -- Sensor location
    manufacturer VARCHAR(100),                  -- Sensor manufacturer
    model VARCHAR(100),                         -- Sensor model
    installation_date DATE,                     -- When installed
    calibration_date DATE,                      -- Last calibration
    status VARCHAR(20) DEFAULT 'active',        -- 'active', 'maintenance', 'offline'
    metadata JSONB,                             -- Sensor-specific config
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================================================
-- TIME-SERIES DATA TABLES (TimescaleDB Hypertables)
-- =====================================================================================

-- Sensor readings (main time-series table)
CREATE TABLE IF NOT EXISTS sensor_readings (
    time TIMESTAMPTZ NOT NULL,
    sensor_id INTEGER REFERENCES sensors(sensor_id),
    value DECIMAL(15,4),                        -- Sensor reading value
    unit VARCHAR(20),                           -- Unit of measurement
    quality_score DECIMAL(3,2),                 -- Data quality (0-1)
    flags JSONB,                                -- Quality flags, alerts
    PRIMARY KEY (time, sensor_id)
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('sensor_readings', 'time', if_not_exists => true);

-- Weather data from met.no and Frost API
CREATE TABLE IF NOT EXISTS weather_data (
    time TIMESTAMPTZ NOT NULL,
    dam_id INTEGER REFERENCES dams(dam_id),
    temperature_c DECIMAL(5,2),                 -- Temperature in Celsius
    precipitation_mm DECIMAL(8,2),              -- Precipitation in mm
    wind_speed_ms DECIMAL(6,2),                 -- Wind speed m/s
    wind_direction DECIMAL(5,1),                -- Wind direction degrees
    humidity_percent DECIMAL(5,2),              -- Relative humidity
    pressure_hpa DECIMAL(7,2),                  -- Atmospheric pressure
    snow_depth_cm DECIMAL(8,2),                 -- Snow depth
    data_source VARCHAR(50),                    -- 'met.no', 'frost'
    api_response JSONB,                         -- Full API response
    PRIMARY KEY (time, dam_id)
);

SELECT create_hypertable('weather_data', 'time', if_not_exists => true);

-- Water level data from NVE Hydrology API
CREATE TABLE IF NOT EXISTS water_levels (
    time TIMESTAMPTZ NOT NULL,
    dam_id INTEGER REFERENCES dams(dam_id),
    water_level_m DECIMAL(8,3),                 -- Water level in meters
    flow_rate_m3s DECIMAL(10,3),                -- Flow rate cubic meters/second
    reservoir_fill_percent DECIMAL(5,2),        -- Reservoir fill percentage
    inflow_m3s DECIMAL(10,3),                   -- Inflow rate
    outflow_m3s DECIMAL(10,3),                  -- Outflow rate
    data_source VARCHAR(50) DEFAULT 'nve',      -- Data source
    quality VARCHAR(20),                        -- Data quality flag
    PRIMARY KEY (time, dam_id)
);

SELECT create_hypertable('water_levels', 'time', if_not_exists => true);

-- Satellite observations from Sentinel Hub
CREATE TABLE IF NOT EXISTS satellite_observations (
    time TIMESTAMPTZ NOT NULL,
    dam_id INTEGER REFERENCES dams(dam_id),
    satellite VARCHAR(50),                      -- 'Sentinel-1', 'Sentinel-2'
    observation_type VARCHAR(50),               -- 'InSAR', 'optical', 'thermal'
    cloud_cover_percent DECIMAL(5,2),          -- Cloud coverage
    image_quality DECIMAL(3,2),                -- Image quality score
    displacement_mm DECIMAL(8,3),              -- InSAR displacement
    vegetation_index DECIMAL(5,3),             -- NDVI or similar
    water_surface_area_m2 DECIMAL(15,2),       -- Detected water surface
    metadata JSONB,                            -- Additional satellite data
    image_url TEXT,                            -- Link to satellite image
    PRIMARY KEY (time, dam_id)
);

SELECT create_hypertable('satellite_observations', 'time', if_not_exists => true);

-- =====================================================================================
-- MONITORING AND ANALYSIS TABLES
-- =====================================================================================

-- Dam health scores (calculated)
CREATE TABLE IF NOT EXISTS health_scores (
    time TIMESTAMPTZ NOT NULL,
    dam_id INTEGER REFERENCES dams(dam_id),
    overall_score DECIMAL(5,2),                -- Overall health (0-100)
    structural_score DECIMAL(5,2),            -- Structural integrity
    operational_score DECIMAL(5,2),           -- Operational efficiency
    environmental_score DECIMAL(5,2),         -- Environmental impact
    safety_score DECIMAL(5,2),                -- Safety assessment
    calculation_method VARCHAR(100),          -- How score was calculated
    confidence_level DECIMAL(3,2),            -- Confidence in score
    factors JSONB,                             -- Contributing factors
    PRIMARY KEY (time, dam_id)
);

SELECT create_hypertable('health_scores', 'time', if_not_exists => true);

-- Alerts and warnings
CREATE TABLE IF NOT EXISTS alerts (
    alert_id SERIAL PRIMARY KEY,
    dam_id INTEGER REFERENCES dams(dam_id),
    alert_type VARCHAR(50) NOT NULL,           -- 'critical', 'warning', 'info'
    severity VARCHAR(20),                      -- 'low', 'medium', 'high', 'critical'
    title VARCHAR(255),                        -- Alert title
    description TEXT,                          -- Detailed description
    source VARCHAR(100),                       -- Data source that triggered alert
    trigger_value DECIMAL(15,4),               -- Value that triggered alert
    threshold_value DECIMAL(15,4),             -- Threshold that was exceeded
    status VARCHAR(20) DEFAULT 'active',       -- 'active', 'acknowledged', 'resolved'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    acknowledged_by VARCHAR(100),
    resolution_notes TEXT
);

-- VARSOM avalanche/flood warnings
CREATE TABLE IF NOT EXISTS varsom_warnings (
    time TIMESTAMPTZ NOT NULL,
    dam_id INTEGER REFERENCES dams(dam_id),
    warning_type VARCHAR(50),                  -- 'flood', 'avalanche', 'landslide'
    danger_level INTEGER,                      -- 1-5 danger scale
    region_name VARCHAR(100),                  -- Warning region
    valid_from TIMESTAMPTZ,                   -- Warning valid from
    valid_to TIMESTAMPTZ,                     -- Warning valid until
    description TEXT,                          -- Warning description
    advice TEXT,                               -- Recommended actions
    api_response JSONB,                        -- Full VARSOM response
    PRIMARY KEY (time, dam_id, warning_type)
);

SELECT create_hypertable('varsom_warnings', 'time', if_not_exists => true);

-- Seismic events
CREATE TABLE IF NOT EXISTS seismic_events (
    time TIMESTAMPTZ NOT NULL,
    dam_id INTEGER REFERENCES dams(dam_id),
    magnitude DECIMAL(3,1),                    -- Earthquake magnitude
    depth_km DECIMAL(6,2),                     -- Depth in kilometers
    distance_km DECIMAL(8,2),                  -- Distance from dam
    location GEOGRAPHY(POINT, 4326),           -- Earthquake epicenter
    source VARCHAR(50),                        -- Data source
    impact_assessment VARCHAR(100),            -- Potential impact
    PRIMARY KEY (time, dam_id)
);

SELECT create_hypertable('seismic_events', 'time', if_not_exists => true);

-- =====================================================================================
-- OPERATIONAL TABLES
-- =====================================================================================

-- Dam inspections
CREATE TABLE IF NOT EXISTS inspections (
    inspection_id SERIAL PRIMARY KEY,
    dam_id INTEGER REFERENCES dams(dam_id),
    inspection_date DATE NOT NULL,
    inspector_name VARCHAR(100),
    inspection_type VARCHAR(50),               -- 'routine', 'emergency', 'annual'
    overall_condition VARCHAR(50),             -- 'excellent', 'good', 'fair', 'poor'
    structural_condition VARCHAR(50),
    mechanical_condition VARCHAR(50),
    electrical_condition VARCHAR(50),
    safety_systems_condition VARCHAR(50),
    recommendations TEXT,                      -- Inspector recommendations
    priority VARCHAR(20),                      -- 'low', 'medium', 'high', 'urgent'
    photos JSONB,                             -- Photo URLs and metadata
    report_url TEXT,                          -- Link to full report
    next_inspection_due DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Maintenance predictions (ML-generated)
CREATE TABLE IF NOT EXISTS maintenance_predictions (
    prediction_id SERIAL PRIMARY KEY,
    dam_id INTEGER REFERENCES dams(dam_id),
    component VARCHAR(100),                    -- Component needing maintenance
    predicted_failure_date DATE,              -- When failure is predicted
    confidence_score DECIMAL(3,2),            -- ML model confidence
    maintenance_type VARCHAR(100),             -- Type of maintenance needed
    estimated_cost DECIMAL(12,2),             -- Estimated maintenance cost
    priority_score DECIMAL(5,2),              -- Priority ranking
    ml_model_version VARCHAR(50),             -- Version of ML model used
    input_features JSONB,                     -- Features used for prediction
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Operations log
CREATE TABLE IF NOT EXISTS operations_log (
    log_id SERIAL PRIMARY KEY,
    dam_id INTEGER REFERENCES dams(dam_id),
    operation_type VARCHAR(100),              -- 'gate_operation', 'turbine_start', etc.
    operator_name VARCHAR(100),
    description TEXT,
    parameters JSONB,                         -- Operation parameters
    result VARCHAR(50),                       -- 'success', 'failure', 'partial'
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================================================

-- Latest health scores for all dams
CREATE OR REPLACE VIEW latest_dam_health AS
SELECT DISTINCT ON (dam_id) 
    dam_id,
    time,
    overall_score,
    structural_score,
    operational_score,
    environmental_score,
    safety_score,
    confidence_level
FROM health_scores 
ORDER BY dam_id, time DESC;

-- Active alerts summary
CREATE OR REPLACE VIEW active_alerts AS
SELECT 
    a.alert_id,
    d.dam_name,
    d.municipality,
    a.alert_type,
    a.severity,
    a.title,
    a.created_at,
    EXTRACT(HOURS FROM NOW() - a.created_at) as hours_active
FROM alerts a
JOIN dams d ON a.dam_id = d.dam_id
WHERE a.status = 'active'
ORDER BY a.severity DESC, a.created_at DESC;

-- Dam overview with latest data
CREATE OR REPLACE VIEW dam_overview AS
SELECT 
    d.dam_id,
    d.dam_name,
    d.municipality,
    d.county,
    d.risk_level,
    lh.overall_score as health_score,
    lh.time as last_health_update,
    COUNT(a.alert_id) as active_alerts,
    d.last_inspection,
    CASE 
        WHEN d.last_inspection < NOW() - INTERVAL '1 year' THEN 'overdue'
        WHEN d.last_inspection < NOW() - INTERVAL '6 months' THEN 'due_soon'
        ELSE 'current'
    END as inspection_status
FROM dams d
LEFT JOIN latest_dam_health lh ON d.dam_id = lh.dam_id
LEFT JOIN alerts a ON d.dam_id = a.dam_id AND a.status = 'active'
GROUP BY d.dam_id, d.dam_name, d.municipality, d.county, d.risk_level, 
         lh.overall_score, lh.time, d.last_inspection;

-- =====================================================================================
-- FUNCTIONS
-- =====================================================================================

-- Function to calculate dam health score
CREATE OR REPLACE FUNCTION calculate_dam_health_score(p_dam_id INTEGER)
RETURNS DECIMAL(5,2) AS $$
DECLARE
    structural_score DECIMAL(5,2) := 0;
    operational_score DECIMAL(5,2) := 0;
    environmental_score DECIMAL(5,2) := 0;
    safety_score DECIMAL(5,2) := 0;
    overall_score DECIMAL(5,2) := 0;
BEGIN
    -- Structural score based on sensor readings and inspections
    SELECT COALESCE(AVG(
        CASE 
            WHEN sr.value BETWEEN -2 AND 2 THEN 100  -- Normal displacement
            WHEN sr.value BETWEEN -5 AND 5 THEN 75   -- Moderate
            WHEN sr.value BETWEEN -10 AND 10 THEN 50 -- Concerning
            ELSE 25                                   -- Critical
        END
    ), 75) INTO structural_score
    FROM sensor_readings sr
    JOIN sensors s ON sr.sensor_id = s.sensor_id
    WHERE s.dam_id = p_dam_id 
    AND s.sensor_type = 'structural'
    AND sr.time > NOW() - INTERVAL '7 days';
    
    -- Operational score based on water levels and power generation
    SELECT COALESCE(AVG(
        CASE 
            WHEN wl.reservoir_fill_percent BETWEEN 30 AND 90 THEN 100
            WHEN wl.reservoir_fill_percent BETWEEN 20 AND 95 THEN 80
            WHEN wl.reservoir_fill_percent BETWEEN 10 AND 98 THEN 60
            ELSE 40
        END
    ), 80) INTO operational_score
    FROM water_levels wl
    WHERE wl.dam_id = p_dam_id
    AND wl.time > NOW() - INTERVAL '1 day';
    
    -- Safety score based on alerts and inspections
    SELECT 
        CASE 
            WHEN COUNT(*) = 0 THEN 95                    -- No active alerts
            WHEN COUNT(*) FILTER (WHERE severity = 'critical') > 0 THEN 30
            WHEN COUNT(*) FILTER (WHERE severity = 'high') > 0 THEN 60
            WHEN COUNT(*) FILTER (WHERE severity = 'medium') > 0 THEN 80
            ELSE 90
        END INTO safety_score
    FROM alerts
    WHERE dam_id = p_dam_id AND status = 'active';
    
    -- Environmental score (simplified)
    environmental_score := 85;
    
    -- Calculate weighted overall score
    overall_score := (
        structural_score * 0.3 + 
        operational_score * 0.25 + 
        safety_score * 0.35 + 
        environmental_score * 0.1
    );
    
    RETURN overall_score;
END;
$$ LANGUAGE plpgsql;

-- Function to update dam health scores
CREATE OR REPLACE FUNCTION update_all_dam_health_scores()
RETURNS INTEGER AS $$
DECLARE
    dam_record RECORD;
    score DECIMAL(5,2);
    updated_count INTEGER := 0;
BEGIN
    FOR dam_record IN SELECT dam_id FROM dams WHERE status = 'active' LOOP
        score := calculate_dam_health_score(dam_record.dam_id);
        
        INSERT INTO health_scores (time, dam_id, overall_score, calculation_method)
        VALUES (NOW(), dam_record.dam_id, score, 'automated_calculation');
        
        updated_count := updated_count + 1;
    END LOOP;
    
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

-- =====================================================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================================================

-- Spatial indexes
CREATE INDEX IF NOT EXISTS idx_dams_location ON dams USING GIST (location);
CREATE INDEX IF NOT EXISTS idx_sensors_location ON sensors USING GIST (location);

-- Time-series indexes
CREATE INDEX IF NOT EXISTS idx_sensor_readings_sensor_time ON sensor_readings (sensor_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_weather_data_dam_time ON weather_data (dam_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_water_levels_dam_time ON water_levels (dam_id, time DESC);

-- Alert indexes
CREATE INDEX IF NOT EXISTS idx_alerts_dam_status ON alerts (dam_id, status);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts (severity, created_at DESC);

-- =====================================================================================
-- DATA RETENTION POLICIES
-- =====================================================================================

-- Keep detailed sensor data for 2 years, then compress
SELECT add_retention_policy('sensor_readings', INTERVAL '2 years', if_not_exists => true);
SELECT add_retention_policy('weather_data', INTERVAL '5 years', if_not_exists => true);
SELECT add_retention_policy('water_levels', INTERVAL '10 years', if_not_exists => true);
SELECT add_retention_policy('satellite_observations', INTERVAL '3 years', if_not_exists => true);

-- Compress old data for better performance
SELECT add_compression_policy('sensor_readings', INTERVAL '7 days', if_not_exists => true);
SELECT add_compression_policy('weather_data', INTERVAL '30 days', if_not_exists => true);

-- =====================================================================================
-- USER MANAGEMENT
-- =====================================================================================

-- Create application user
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'dam_monitor_app') THEN
        CREATE USER dam_monitor_app WITH PASSWORD 'dam_monitor_2024';
    END IF;
END
$$;

-- Grant permissions
GRANT USAGE ON SCHEMA public TO dam_monitor_app;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO dam_monitor_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO dam_monitor_app;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO dam_monitor_app;

-- =====================================================================================
-- INITIAL DATA POPULATION
-- =====================================================================================

-- This will be populated by the data import script
-- Norwegian dam data from NVE will be imported into the dams table

-- =====================================================================================
-- MONITORING SETUP COMPLETE
-- =====================================================================================

-- Enable row-level security (optional, for multi-tenant setups)
-- ALTER TABLE dams ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;

COMMENT ON DATABASE postgres IS 'Norwegian Dam Health Monitoring System - TimescaleDB'; 