-- Create stub tables for UC Functions that need them
-- These are placeholders - can be populated with real data later

-- Knowledge Base schema and table (for search_knowledge_base function)
CREATE SCHEMA IF NOT EXISTS member_analytics.knowledge_base;

CREATE TABLE IF NOT EXISTS member_analytics.knowledge_base.kb_articles (
    article_id STRING NOT NULL,
    title STRING NOT NULL,
    content STRING,
    category STRING,
    tags ARRAY<STRING>,
    helpful_count INT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
USING DELTA;

-- Insert sample KB articles
INSERT INTO member_analytics.knowledge_base.kb_articles VALUES
('KB-001', 'Contribution Caps Guide', 'The concessional contribution cap for 2024-25 is $30,000 per year. This includes employer contributions.', 'contributions', ARRAY('contributions', 'cap', 'limits'), 150, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('KB-002', 'Compassionate Grounds Withdrawal', 'Compassionate grounds allow early access to super for medical treatment, mortgage assistance, or funeral expenses.', 'withdrawals', ARRAY('withdrawal', 'compassionate', 'medical'), 200, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('KB-003', 'Insurance Coverage Information', 'Default death and TPD insurance is provided. Premiums are deducted from your super balance.', 'insurance', ARRAY('insurance', 'coverage', 'premiums'), 180, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

-- Member Data schema and table (for get_member_history function)
CREATE SCHEMA IF NOT EXISTS member_analytics.member_data;

CREATE TABLE IF NOT EXISTS member_analytics.member_data.interaction_history (
    interaction_id STRING NOT NULL,
    member_id STRING NOT NULL,
    interaction_date TIMESTAMP NOT NULL,
    interaction_type STRING,
    summary STRING,
    channel STRING
)
USING DELTA;

-- Sample interaction history (can be populated from actual calls)
INSERT INTO member_analytics.member_data.interaction_history
SELECT 
    CONCAT('INT-', call_id, '-', ROW_NUMBER() OVER (PARTITION BY call_id ORDER BY timestamp)) as interaction_id,
    member_id,
    timestamp as interaction_date,
    scenario as interaction_type,
    CONCAT('Call about ', scenario) as summary,
    channel
FROM member_analytics.call_center.zerobus_transcripts
WHERE ROW_NUMBER() OVER (PARTITION BY call_id ORDER BY timestamp) = 1;

