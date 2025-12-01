-- ============================================================================
-- Phase 1: Smart Fish Pond Database Schema
-- PostgreSQL 15+ Compatible
-- ============================================================================

-- Drop existing tables if they exist (for clean reinstall)
DROP TABLE IF EXISTS pump_log CASCADE;
DROP TABLE IF EXISTS alerts CASCADE;
DROP TABLE IF EXISTS sensor_readings CASCADE;
DROP TABLE IF EXISTS pond_config CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================================================
-- SENSOR READINGS TABLE
-- Stores all sensor data from the monitoring system
-- ============================================================================
CREATE TABLE sensor_readings (
    id SERIAL PRIMARY KEY,
    temperature DECIMAL(5,2),              -- Temperature in Celsius
    ph DECIMAL(4,2),                       -- pH level (0-14)
    ec DECIMAL(7,2),                       -- Electrical Conductivity (μS/cm)
    nitrogen DECIMAL(6,2),                 -- Nitrogen (mg/kg)
    phosphorus DECIMAL(6,2),               -- Phosphorus (mg/kg)
    potassium DECIMAL(6,2),                -- Potassium (mg/kg)
    turbidity DECIMAL(3,2),                -- Turbidity (0=clear, 1=turbid)
    quality_status VARCHAR(20),            -- GOOD, WARNING, CRITICAL
    quality_score INTEGER,                 -- Risk score (0-100+)
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_temperature CHECK (temperature BETWEEN -40 AND 80),
    CONSTRAINT chk_ph CHECK (ph BETWEEN 0 AND 14),
    CONSTRAINT chk_ec CHECK (ec >= 0),
    CONSTRAINT chk_quality_status CHECK (quality_status IN ('GOOD', 'WARNING', 'CRITICAL'))
);

-- Index for fast time-based queries
CREATE INDEX idx_readings_timestamp ON sensor_readings(timestamp DESC);
CREATE INDEX idx_readings_status ON sensor_readings(quality_status);

-- ============================================================================
-- USERS TABLE
-- Authentication and user management
-- ============================================================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,   -- Hashed password (never store plain text)
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',       -- 'admin' or 'user'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_role CHECK (role IN ('admin', 'user'))
);

-- Default admin user (password: admin123 - CHANGE THIS IN PRODUCTION!)
INSERT INTO users (username, password_hash, email, role) 
VALUES ('admin', 'scrypt:32768:8:1$salt$hashedpassword', 'admin@pond.local', 'admin');

-- ============================================================================
-- ALERTS TABLE
-- System alerts and notifications
-- ============================================================================
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(50) NOT NULL,       -- 'pH_CRITICAL', 'TEMP_HIGH', etc.
    severity VARCHAR(20) NOT NULL,         -- 'INFO', 'WARNING', 'CRITICAL'
    message TEXT NOT NULL,
    parameter VARCHAR(50),                 -- Which parameter triggered alert
    value DECIMAL(10,2),                   -- Value that triggered alert
    threshold DECIMAL(10,2),               -- Threshold that was exceeded
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by INTEGER REFERENCES users(id),
    acknowledged_at TIMESTAMP,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_severity CHECK (severity IN ('INFO', 'WARNING', 'CRITICAL'))
);

-- Index for fast alert queries
CREATE INDEX idx_alerts_timestamp ON alerts(timestamp DESC);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_acknowledged ON alerts(acknowledged);

-- ============================================================================
-- POND CONFIGURATION TABLE
-- System settings and thresholds
-- ============================================================================
CREATE TABLE pond_config (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    data_type VARCHAR(20) DEFAULT 'string',  -- 'string', 'number', 'boolean', 'json'
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES users(id)
);

-- Default configuration values
INSERT INTO pond_config (key, value, description, data_type) VALUES
('ph_min', '6.5', 'Minimum safe pH level', 'number'),
('ph_max', '8.5', 'Maximum safe pH level', 'number'),
('temp_min', '18', 'Minimum safe temperature (°C)', 'number'),
('temp_max', '30', 'Maximum safe temperature (°C)', 'number'),
('ec_max', '2000', 'Maximum EC level (μS/cm)', 'number'),
('nitrogen_max', '150', 'Maximum nitrogen level (mg/kg)', 'number'),
('phosphorus_max', '150', 'Maximum phosphorus level (mg/kg)', 'number'),
('sms_enabled', 'true', 'Enable SMS notifications', 'boolean'),
('sms_cooldown', '300', 'Minimum seconds between SMS alerts', 'number'),
('pump_run_short', '120', 'Short pump cycle duration (seconds)', 'number'),
('pump_run_normal', '180', 'Normal pump cycle duration (seconds)', 'number'),
('pump_run_long', '240', 'Long pump cycle duration (seconds)', 'number');

-- ============================================================================
-- PUMP LOG TABLE
-- Track pump activations for maintenance and analysis
-- ============================================================================
CREATE TABLE pump_log (
    id SERIAL PRIMARY KEY,
    mode VARCHAR(20) NOT NULL,             -- 'SHORT', 'NORMAL', 'LONG'
    duration INTEGER,                      -- Actual runtime in seconds
    trigger_reason TEXT,                   -- Why pump was activated
    quality_status VARCHAR(20),            -- Status when activated
    started_at TIMESTAMP NOT NULL,
    stopped_at TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_pump_mode CHECK (mode IN ('SHORT', 'NORMAL', 'LONG', 'MANUAL'))
);

-- Index for pump analysis
CREATE INDEX idx_pump_started ON pump_log(started_at DESC);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Latest sensor reading
CREATE OR REPLACE VIEW latest_reading AS
SELECT * FROM sensor_readings
ORDER BY timestamp DESC
LIMIT 1;

-- Recent alerts (last 24 hours)
CREATE OR REPLACE VIEW recent_alerts AS
SELECT * FROM alerts
WHERE timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;

-- Active (unacknowledged) alerts
CREATE OR REPLACE VIEW active_alerts AS
SELECT * FROM alerts
WHERE acknowledged = FALSE
ORDER BY timestamp DESC;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to clean old data (keep last 30 days)
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM sensor_readings
    WHERE timestamp < NOW() - INTERVAL '30 days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get statistics for a parameter
CREATE OR REPLACE FUNCTION get_parameter_stats(
    param_name VARCHAR,
    hours INTEGER DEFAULT 24
)
RETURNS TABLE(
    avg_value DECIMAL,
    min_value DECIMAL,
    max_value DECIMAL,
    reading_count BIGINT
) AS $$
BEGIN
    RETURN QUERY EXECUTE format(
        'SELECT 
            AVG(%I)::DECIMAL(10,2), 
            MIN(%I)::DECIMAL(10,2), 
            MAX(%I)::DECIMAL(10,2), 
            COUNT(*)::BIGINT
         FROM sensor_readings 
         WHERE timestamp > NOW() - INTERVAL ''%s hours''
         AND %I IS NOT NULL',
        param_name, param_name, param_name, hours, param_name
    );
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- GRANT PERMISSIONS TO USER 'km'
-- ============================================================================
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO km;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO km;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO km;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO km;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO km;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT EXECUTE ON FUNCTIONS TO km;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Show all tables
SELECT 'Tables created successfully:' as status;
\dt

-- Show all views
SELECT 'Views created successfully:' as status;
\dv

-- Show row counts
SELECT 'sensor_readings' as table_name, COUNT(*) as row_count FROM sensor_readings
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'alerts', COUNT(*) FROM alerts
UNION ALL
SELECT 'pond_config', COUNT(*) FROM pond_config
UNION ALL
SELECT 'pump_log', COUNT(*) FROM pump_log;

-- Success message
SELECT '✅ Database schema setup complete!' as status;