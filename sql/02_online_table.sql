-- Phase 2.2: Create Online Table for real-time access
-- Online Tables provide sub-second query latency
-- Note: Online Tables must be created via UI or REST API, not SQL
-- This creates a regular table that can be converted to Online Table

-- First, create a regular table/view from enriched data
CREATE OR REPLACE VIEW member_analytics.call_center.live_transcripts_view
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

-- Note: To create Online Table, use Databricks UI:
-- 1. Go to Catalog Explorer
-- 2. Select table: member_analytics.call_center.enriched_transcripts
-- 3. Click "Create Online Table"
-- 4. Configure refresh settings

