-- Phase 3: UC Functions for Agent Tools
-- These functions are used by the GenAI Agent as tools
-- Run via: databricks-sql-cli -f sql/03_uc_functions.sql

-- Function 1: Get live call context
-- Fixed: Use ARRAY_AGG instead of GROUP_CONCAT for Databricks SQL
CREATE OR REPLACE FUNCTION member_analytics.call_center.get_live_call_context(call_id_param STRING)
RETURNS TABLE (
    member_name STRING,
    balance DECIMAL(18,2),
    recent_transcript STRING,
    sentiment STRING,
    intents STRING,
    compliance_issues STRING
)
RETURN SELECT 
    MAX(member_name) as member_name,
    MAX(member_balance) as balance,
    SUBSTRING(ARRAY_JOIN(ARRAY_AGG(transcript_segment), ' '), 1, 500) as recent_transcript,
    MAX(sentiment) as sentiment,
    ARRAY_JOIN(ARRAY_AGG(DISTINCT intent_category), ', ') as intents,
    ARRAY_JOIN(ARRAY_AGG(DISTINCT CASE WHEN compliance_flag != 'ok' THEN compliance_flag END), ', ') as compliance_issues
FROM (
    SELECT member_name, member_balance, transcript_segment, sentiment, intent_category, compliance_flag
    FROM member_analytics.call_center.enriched_transcripts
    WHERE call_id = call_id_param
    ORDER BY timestamp
)
GROUP BY member_name;

-- Function 2: Search knowledge base (stub - requires kb_articles table)
-- Note: Create knowledge_base.kb_articles table separately if needed
CREATE OR REPLACE FUNCTION member_analytics.call_center.search_knowledge_base(search_query STRING)
RETURNS TABLE (
    article_id STRING,
    title STRING,
    content STRING
)
RETURN SELECT 
    CAST('KB-001' AS STRING) as article_id,
    CAST('Sample Article' AS STRING) as title,
    CAST('Sample content for ' || search_query AS STRING) as content
LIMIT 3;

-- Function 3: Check compliance in real-time
CREATE OR REPLACE FUNCTION member_analytics.call_center.check_compliance_realtime(call_id_param STRING)
RETURNS TABLE (
    violation_type STRING,
    severity STRING,
    segment STRING,
    timestamp TIMESTAMP
)
RETURN SELECT 
    compliance_flag as violation_type,
    compliance_severity as severity,
    transcript_segment as segment,
    timestamp
FROM member_analytics.call_center.enriched_transcripts
WHERE call_id = call_id_param
  AND compliance_flag != 'ok'
ORDER BY timestamp DESC;

-- Function 4: Get member interaction history (stub - requires interaction_history table)
-- Note: Create member_data.interaction_history table separately if needed
CREATE OR REPLACE FUNCTION member_analytics.call_center.get_member_history(member_id_param STRING)
RETURNS TABLE (
    interaction_date TIMESTAMP,
    type STRING,
    summary STRING
)
RETURN SELECT 
    CURRENT_TIMESTAMP() as interaction_date,
    CAST('call' AS STRING) as type,
    CAST('Recent call interaction' AS STRING) as summary
LIMIT 5;

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION member_analytics.call_center.get_live_call_context TO `account users`;
GRANT EXECUTE ON FUNCTION member_analytics.call_center.search_knowledge_base TO `account users`;
GRANT EXECUTE ON FUNCTION member_analytics.call_center.check_compliance_realtime TO `account users`;
GRANT EXECUTE ON FUNCTION member_analytics.call_center.get_member_history TO `account users`;

