-- Phase 2.2: Create Online Table for real-time access
-- Online Tables provide sub-second query latency
-- Run via: databricks-sql-cli -f sql/02_online_table.sql

CREATE ONLINE TABLE IF NOT EXISTS member_analytics.call_center.live_transcripts_online
AS SELECT 
    call_id,
    member_id,
    member_name,
    agent_id,
    timestamp,
    transcript_segment,
    speaker,
    sentiment,
    intent_category,
    compliance_flag,
    compliance_severity,
    scenario,
    complexity,
    member_balance,
    member_life_stage,
    enriched_at
FROM member_analytics.call_center.enriched_transcripts
WHERE timestamp > CURRENT_TIMESTAMP() - INTERVAL 24 HOURS;

-- Note: Online Tables are automatically refreshed from the source table
-- For production, set up automatic refresh or use streaming

