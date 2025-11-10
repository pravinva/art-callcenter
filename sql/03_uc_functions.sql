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

-- Function 2: Search knowledge base (queries actual kb_articles table)
CREATE OR REPLACE FUNCTION member_analytics.call_center.search_knowledge_base(search_query STRING)
RETURNS TABLE (
    article_id STRING,
    title STRING,
    content STRING,
    category STRING
)
RETURN SELECT 
    article_id,
    title,
    content,
    category
FROM member_analytics.knowledge_base.kb_articles
WHERE 
    LOWER(title) LIKE '%' || LOWER(search_query) || '%'
    OR LOWER(content) LIKE '%' || LOWER(search_query) || '%'
ORDER BY 
    CASE 
        WHEN LOWER(title) LIKE '%' || LOWER(search_query) || '%' THEN 1
        ELSE 2
    END,
    helpful_count DESC
LIMIT 5;

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

-- Function 4: Get member interaction history (now uses Gold layer table)
CREATE OR REPLACE FUNCTION member_analytics.call_center.get_member_history(member_id_param STRING)
RETURNS TABLE (
    interaction_date TIMESTAMP,
    type STRING,
    summary STRING,
    interaction_topic STRING,
    overall_sentiment STRING,
    call_duration_minutes DOUBLE
)
RETURN SELECT 
    interaction_date,
    interaction_type as type,
    summary,
    interaction_topic,
    overall_sentiment,
    call_duration_minutes
FROM member_analytics.call_center.member_interaction_history
WHERE member_id = member_id_param
ORDER BY interaction_date DESC
LIMIT 10;

-- Function 5: Detect sentiment for a call (standalone function)
CREATE OR REPLACE FUNCTION member_analytics.call_center.detect_sentiment(call_id_param STRING)
RETURNS TABLE (
    sentiment STRING,
    sentiment_count INT,
    latest_segment STRING,
    timestamp TIMESTAMP
)
RETURN SELECT 
    sentiment,
    COUNT(*) as sentiment_count,
    MAX(transcript_segment) as latest_segment,
    MAX(timestamp) as timestamp
FROM member_analytics.call_center.enriched_transcripts
WHERE call_id = call_id_param
GROUP BY sentiment
ORDER BY sentiment_count DESC;

-- Function 6: Extract member intent for a call (standalone function)
CREATE OR REPLACE FUNCTION member_analytics.call_center.extract_member_intent(call_id_param STRING)
RETURNS TABLE (
    intent_category STRING,
    intent_count INT,
    confidence_avg DECIMAL(5,3),
    latest_segment STRING,
    timestamp TIMESTAMP
)
RETURN SELECT 
    intent_category,
    COUNT(*) as intent_count,
    AVG(confidence) as confidence_avg,
    MAX(transcript_segment) as latest_segment,
    MAX(timestamp) as timestamp
FROM member_analytics.call_center.enriched_transcripts
WHERE call_id = call_id_param
GROUP BY intent_category
ORDER BY intent_count DESC;

-- Function 7: Identify escalation triggers (high-risk calls)
-- Escalates when: negative sentiment + compliance violation + complaint intent
CREATE OR REPLACE FUNCTION member_analytics.call_center.identify_escalation_triggers(call_id_param STRING)
RETURNS TABLE (
    escalation_recommended BOOLEAN,
    risk_score INT,
    risk_factors STRING,
    negative_sentiment_count INT,
    compliance_violations_count INT,
    complaint_intent_count INT,
    recommendation STRING
)
RETURN SELECT 
    CASE 
        WHEN (
            SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) > 0 AND
            SUM(CASE WHEN compliance_flag != 'ok' THEN 1 ELSE 0 END) > 0 AND
            SUM(CASE WHEN intent_category = 'complaint' THEN 1 ELSE 0 END) > 0
        ) THEN TRUE
        WHEN (
            SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) >= 3 AND
            SUM(CASE WHEN compliance_flag != 'ok' THEN 1 ELSE 0 END) > 0
        ) THEN TRUE
        WHEN (
            SUM(CASE WHEN compliance_severity = 'CRITICAL' THEN 1 ELSE 0 END) > 0
        ) THEN TRUE
        ELSE FALSE
    END as escalation_recommended,
    (
        SUM(CASE WHEN sentiment = 'negative' THEN 2 ELSE 0 END) +
        SUM(CASE WHEN compliance_flag != 'ok' THEN 3 ELSE 0 END) +
        SUM(CASE WHEN intent_category = 'complaint' THEN 2 ELSE 0 END) +
        SUM(CASE WHEN compliance_severity = 'CRITICAL' THEN 5 ELSE 0 END) +
        SUM(CASE WHEN compliance_severity = 'HIGH' THEN 3 ELSE 0 END)
    ) as risk_score,
    ARRAY_JOIN(ARRAY_AGG(DISTINCT 
        CASE 
            WHEN sentiment = 'negative' THEN 'negative_sentiment'
            WHEN compliance_flag != 'ok' THEN CONCAT('compliance_', compliance_flag)
            WHEN intent_category = 'complaint' THEN 'complaint_intent'
            ELSE NULL
        END
    ), ', ') as risk_factors,
    SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) as negative_sentiment_count,
    SUM(CASE WHEN compliance_flag != 'ok' THEN 1 ELSE 0 END) as compliance_violations_count,
    SUM(CASE WHEN intent_category = 'complaint' THEN 1 ELSE 0 END) as complaint_intent_count,
    CASE 
        WHEN (
            SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) > 0 AND
            SUM(CASE WHEN compliance_flag != 'ok' THEN 1 ELSE 0 END) > 0 AND
            SUM(CASE WHEN intent_category = 'complaint' THEN 1 ELSE 0 END) > 0
        ) THEN 'IMMEDIATE ESCALATION: Multiple risk factors detected (negative sentiment + compliance violation + complaint)'
        WHEN (
            SUM(CASE WHEN compliance_severity = 'CRITICAL' THEN 1 ELSE 0 END) > 0
        ) THEN 'IMMEDIATE ESCALATION: Critical compliance violation detected'
        WHEN (
            SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) >= 3 AND
            SUM(CASE WHEN compliance_flag != 'ok' THEN 1 ELSE 0 END) > 0
        ) THEN 'ESCALATION RECOMMENDED: Multiple negative sentiments with compliance issues'
        WHEN (
            SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) >= 5
        ) THEN 'MONITOR CLOSELY: High number of negative sentiment indicators'
        ELSE 'NO ESCALATION: Call proceeding normally'
    END as recommendation
FROM member_analytics.call_center.enriched_transcripts
WHERE call_id = call_id_param;

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION member_analytics.call_center.get_live_call_context TO `account users`;
GRANT EXECUTE ON FUNCTION member_analytics.call_center.search_knowledge_base TO `account users`;
GRANT EXECUTE ON FUNCTION member_analytics.call_center.check_compliance_realtime TO `account users`;
GRANT EXECUTE ON FUNCTION member_analytics.call_center.get_member_history TO `account users`;
GRANT EXECUTE ON FUNCTION member_analytics.call_center.detect_sentiment TO `account users`;
GRANT EXECUTE ON FUNCTION member_analytics.call_center.extract_member_intent TO `account users`;
GRANT EXECUTE ON FUNCTION member_analytics.call_center.identify_escalation_triggers TO `account users`;

