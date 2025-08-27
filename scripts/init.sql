-- Multi-Armed Bandit API Database Initialization

-- Create extensions for better performance
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: experiments
CREATE TABLE IF NOT EXISTS experiments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: daily_metrics
CREATE TABLE IF NOT EXISTS daily_metrics (
    id SERIAL PRIMARY KEY,
    experiment_id INTEGER REFERENCES experiments(id) ON DELETE CASCADE,
    variant_name VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    impressions INTEGER DEFAULT 0 CHECK (impressions >= 0),
    clicks INTEGER DEFAULT 0 CHECK (clicks >= 0 AND clicks <= impressions),
    conversions INTEGER DEFAULT 0 CHECK (conversions >= 0 AND conversions <= clicks),
    ctr DECIMAL(8,6) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(experiment_id, variant_name, date)
);

-- Table: allocations
CREATE TABLE IF NOT EXISTS allocations (
    id SERIAL PRIMARY KEY,
    experiment_id INTEGER REFERENCES experiments(id) ON DELETE CASCADE,
    target_date DATE NOT NULL,
    algorithm VARCHAR(50) DEFAULT 'thompson_sampling',
    allocations JSONB NOT NULL,
    window_days INTEGER DEFAULT 14,
    total_impressions INTEGER DEFAULT 0,
    total_clicks INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_experiments_status ON experiments(status);
CREATE INDEX IF NOT EXISTS idx_daily_metrics_experiment_date 
    ON daily_metrics(experiment_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_daily_metrics_experiment_variant_date 
    ON daily_metrics(experiment_id, variant_name, date DESC);
CREATE INDEX IF NOT EXISTS idx_daily_metrics_date 
    ON daily_metrics(date DESC);
CREATE INDEX IF NOT EXISTS idx_allocations_experiment_date 
    ON allocations(experiment_id, target_date DESC);

-- Trigger for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_experiments_updated_at ON experiments;
CREATE TRIGGER update_experiments_updated_at 
    BEFORE UPDATE ON experiments 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_daily_metrics_updated_at ON daily_metrics;
CREATE TRIGGER update_daily_metrics_updated_at 
    BEFORE UPDATE ON daily_metrics 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger to automatically calculate CTR
CREATE OR REPLACE FUNCTION calculate_ctr()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.impressions > 0 THEN
        NEW.ctr = NEW.clicks::DECIMAL / NEW.impressions::DECIMAL;
    ELSE
        NEW.ctr = 0;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS calculate_ctr_trigger ON daily_metrics;
CREATE TRIGGER calculate_ctr_trigger 
    BEFORE INSERT OR UPDATE ON daily_metrics
    FOR EACH ROW EXECUTE FUNCTION calculate_ctr();

SELECT 'Multi-Armed Bandit Database Initialized Successfully' as status;