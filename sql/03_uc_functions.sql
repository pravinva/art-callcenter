-- Phase 3: UC Functions for Agent Tools
-- These functions are used by the GenAI Agent as tools
-- Run via: databricks-sql-cli -f sql/03_uc_functions.sql

-- Function 1: Get live call context
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
    SUBSTRING(GROUP_CONCAT(transcript_segment ORDER BY timestamp SEPARATOR ' '), 1, 500) as recent_transcript,
    MAX(sentiment) as sentiment,
    GROUP_CONCAT(DISTINCT intent_category SEPARATOR ', ') as intents,
    GROUP_CONCAT(DISTINCT CASE WHEN compliance_flag != 'ok' THEN compliance_flag END SEPARATOR ', ') as compliance_issues
FROM member_analytics.call_center.live_transcripts_online
WHERE call_id = call_id_param
GROUP BY member_name;

-- Function 2: Search knowledge base
-- Note: Requires knowledge_base.kb_articles table to exist
CREATE OR REPLACE FUNCTION member_analytics.call_center.search_knowledge_base(search_query STRING)
RETURNS TABLE (
    article_id STRING,
    title STRING,
    content STRING
)
RETURN SELECT 
    article_id, 
    title, 
    content
FROM member_analytics.knowledge_base.kb_articles
WHERE LOWER(title) LIKE LOWER(CONCAT('%', search_query, '%'))
   OR LOWER(content) LIKE LOWER(CONCAT('%', search_query, '%'))
   OR ARRAY_CONTAINS(tags, LOWER(search_query))
ORDER BY helpful_count DESC
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
FROM member_analytics.call_center.live_transcripts_online
WHERE call_id = call_id_param
  AND compliance_flag != 'ok'
ORDER BY timestamp DESC;

-- Function 4: Get member interaction history
-- Note: Requires member_data.interaction_history table to exist
CREATE OR REPLACE FUNCTION member_analytics.call_center.get_member_history(member_id_param STRING)
RETURNS TABLE (
    interaction_date TIMESTAMP,
    type STRING,
    summary STRING
)
RETURN SELECT 
    interaction_date, 
    interaction_type as type, 
    summary
FROM member_analytics.member_data.interaction_history
WHERE member_id = member_id_param
ORDER BY interaction_date DESC
LIMIT 5;

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION member_analytics.call_center.get_live_call_context TO `account users`;
GRANT EXECUTE ON FUNCTION member_analytics.call_center.search_knowledge_base TO `account users`;
GRANT EXECUTE ON FUNCTION member_analytics.call_center.check_compliance_realtime TO `account users`;
GRANT EXECUTE ON FUNCTION member_analytics.call_center.get_member_history TO `account users`;

