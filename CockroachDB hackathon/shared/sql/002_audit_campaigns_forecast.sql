-- LedgerMind Schema Extension: Audit, Campaigns, Forecasts

-- Audit Events (full activity trail)
CREATE TABLE IF NOT EXISTS audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sme_id UUID NOT NULL REFERENCES smes(id),
    event_type VARCHAR(100) NOT NULL,
    actor VARCHAR(255) NOT NULL,  -- 'agent', 'user:<email>', 'system'
    description TEXT NOT NULL,
    details JSONB,
    related_entity_id UUID,
    created_at TIMESTAMPTZ DEFAULT now(),
    INDEX idx_audit_sme_time (sme_id, created_at DESC),
    INDEX idx_audit_event_type (event_type),
    INDEX idx_audit_entity (related_entity_id)
);

-- Campaigns
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sme_id UUID NOT NULL REFERENCES smes(id),
    campaign_type VARCHAR(50) NOT NULL,  -- recovery, win_back, upsell, retention
    status VARCHAR(50) DEFAULT 'draft',
    name VARCHAR(255) NOT NULL,
    description TEXT,
    rationale TEXT,  -- Agent's reasoning
    targets JSONB,  -- Array of target customers
    suggested_message TEXT,
    channel VARCHAR(50) DEFAULT 'email',
    estimated_impact TEXT,
    outcome JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    approved_at TIMESTAMPTZ,
    executed_at TIMESTAMPTZ,
    outcome_checked_at TIMESTAMPTZ,
    INDEX idx_campaigns_sme_status (sme_id, status),
    INDEX idx_campaigns_type (campaign_type)
);

-- Forecasts (stored for comparison with actuals)
CREATE TABLE IF NOT EXISTS forecasts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sme_id UUID NOT NULL REFERENCES smes(id),
    metric VARCHAR(50) NOT NULL,  -- revenue, transactions, failure_rate
    period_days INT NOT NULL,
    data_points JSONB NOT NULL,  -- Array of {date, predicted, lower, upper}
    trend VARCHAR(20),
    summary TEXT,
    risk_factors JSONB,
    opportunities JSONB,
    generated_at TIMESTAMPTZ DEFAULT now(),
    INDEX idx_forecasts_sme_metric (sme_id, metric, generated_at DESC)
);

-- Daily Briefs (stored for history)
CREATE TABLE IF NOT EXISTS daily_briefs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sme_id UUID NOT NULL REFERENCES smes(id),
    headline TEXT NOT NULL,
    health_score INT NOT NULL,
    sections JSONB NOT NULL,
    action_items JSONB,
    forecast_summary TEXT,
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    generated_at TIMESTAMPTZ DEFAULT now(),
    INDEX idx_briefs_sme_date (sme_id, generated_at DESC)
);

-- Data import history
CREATE TABLE IF NOT EXISTS import_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sme_id UUID NOT NULL REFERENCES smes(id),
    source VARCHAR(50) NOT NULL,  -- csv, stripe, synthetic
    file_name VARCHAR(255),
    total_rows INT,
    imported INT,
    skipped INT,
    errors JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    INDEX idx_imports_sme (sme_id, created_at DESC)
);
