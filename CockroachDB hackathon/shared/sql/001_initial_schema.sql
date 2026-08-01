-- LedgerMind Initial Schema for CockroachDB Cloud
-- Enables pgvector for distributed vector search (agentic memory)

-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- SME (Small/Medium Enterprise) accounts
CREATE TABLE IF NOT EXISTS smes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    cognito_sub VARCHAR(255) UNIQUE NOT NULL,
    stripe_customer_id VARCHAR(255),
    stripe_connect_account_id VARCHAR(255),
    subscription_status VARCHAR(50) DEFAULT 'trial',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Customers (end-customers of the SME)
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sme_id UUID NOT NULL REFERENCES smes(id),
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    stripe_customer_id VARCHAR(255),
    last_transaction_at TIMESTAMPTZ,
    total_transactions INT DEFAULT 0,
    total_revenue DECIMAL(12,2) DEFAULT 0.0,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT now(),
    INDEX idx_customers_sme_status (sme_id, status),
    INDEX idx_customers_last_txn (last_transaction_at)
);

-- Payment transactions
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sme_id UUID NOT NULL REFERENCES smes(id),
    stripe_payment_intent_id VARCHAR(255),
    customer_id UUID REFERENCES customers(id),
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) NOT NULL,  -- succeeded, failed, pending, refunded
    failure_reason TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    INDEX idx_transactions_sme_created (sme_id, created_at DESC),
    INDEX idx_transactions_status (status),
    INDEX idx_transactions_customer (customer_id, created_at DESC)
);

-- Agent Memory (structured + semantic via pgvector)
CREATE TABLE IF NOT EXISTS agent_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sme_id UUID NOT NULL REFERENCES smes(id),
    memory_type VARCHAR(50) NOT NULL,  -- observation, decision, outcome, baseline, incident, pattern
    content JSONB NOT NULL,
    embedding VECTOR(1024),  -- Amazon Titan Embeddings V2 dimension
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    INDEX idx_memory_sme_type (sme_id, memory_type),
    INDEX idx_memory_created (created_at DESC)
);

-- Vector index for semantic memory search
CREATE INDEX idx_memory_embedding ON agent_memory
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Agent Decisions (tracks recommendations, approvals, outcomes)
CREATE TABLE IF NOT EXISTS agent_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sme_id UUID NOT NULL REFERENCES smes(id),
    task_type VARCHAR(100) NOT NULL,
    observation TEXT NOT NULL,
    analysis TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    confidence FLOAT DEFAULT 0.0,
    risk_level VARCHAR(20) DEFAULT 'low',
    approval_status VARCHAR(20) DEFAULT 'pending',  -- pending, approved, rejected, expired
    sme_feedback TEXT,
    outcome JSONB,
    outcome_score FLOAT,
    embedding VECTOR(1024),
    created_at TIMESTAMPTZ DEFAULT now(),
    approved_at TIMESTAMPTZ,
    executed_at TIMESTAMPTZ,
    outcome_checked_at TIMESTAMPTZ,
    INDEX idx_decisions_sme_status (sme_id, approval_status),
    INDEX idx_decisions_task_type (task_type)
);

-- Vector index for finding similar past incidents
CREATE INDEX idx_decisions_embedding ON agent_decisions
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Agent Baselines (learned normal behaviour)
CREATE TABLE IF NOT EXISTS agent_baselines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sme_id UUID NOT NULL REFERENCES smes(id),
    metric_name VARCHAR(100) NOT NULL,
    normal_range_low FLOAT NOT NULL,
    normal_range_high FLOAT NOT NULL,
    mean_value FLOAT NOT NULL,
    std_deviation FLOAT NOT NULL,
    sample_size INT NOT NULL,
    confidence FLOAT NOT NULL,
    last_updated TIMESTAMPTZ DEFAULT now(),
    UNIQUE INDEX idx_baselines_sme_metric (sme_id, metric_name)
);

-- Agent Tasks (investigations, monitoring, campaigns)
CREATE TABLE IF NOT EXISTS agent_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sme_id UUID NOT NULL REFERENCES smes(id),
    task_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'queued',  -- queued, in_progress, awaiting_approval, executing, completed, failed
    parameters JSONB,
    result JSONB,
    scheduled_for TIMESTAMPTZ,  -- For scheduled performance checks
    created_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ,
    INDEX idx_tasks_sme_status (sme_id, status),
    INDEX idx_tasks_scheduled (scheduled_for) WHERE scheduled_for IS NOT NULL
);

-- Changefeeds for real-time anomaly detection (CockroachDB-specific)
-- These emit events when transactions are inserted, enabling the agent to observe in real-time
-- Run manually: CREATE CHANGEFEED FOR transactions INTO 'sqs://...' WITH updated;
