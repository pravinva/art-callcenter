-- Phase 2.1: DLT Pipeline - SQL-based enrichment
-- Creates streaming table with sentiment, intent, and compliance detection
-- Run via: databricks-sql-cli -f sql/02_dlt_enrichment.sql
-- Or deploy as DLT pipeline in Databricks

CREATE OR REFRESH STREAMING TABLE member_analytics.call_center.enriched_transcripts;

APPLY CHANGES INTO member_analytics.call_center.enriched_transcripts
FROM (
    SELECT 
        call_id,
        member_id,
        member_name,
        agent_id,
        timestamp,
        transcript_segment,
        speaker,
        confidence,
        queue,
        scenario,
        complexity,
        channel,
        member_balance,
        member_life_stage,
        -- Sentiment analysis (simplified - in production use ML model)
        CASE 
            WHEN LOWER(transcript_segment) LIKE '%thank%' OR 
                 LOWER(transcript_segment) LIKE '%appreciate%' OR
                 LOWER(transcript_segment) LIKE '%great%' OR
                 LOWER(transcript_segment) LIKE '%perfect%'
            THEN 'positive'
            WHEN LOWER(transcript_segment) LIKE '%frustrated%' OR
                 LOWER(transcript_segment) LIKE '%angry%' OR
                 LOWER(transcript_segment) LIKE '%disappointed%' OR
                 LOWER(transcript_segment) LIKE '%terrible%'
            THEN 'negative'
            ELSE 'neutral'
        END AS sentiment,
        
        -- Intent detection (simplified)
        CASE 
            WHEN LOWER(transcript_segment) LIKE '%contribution%' OR 
                 LOWER(transcript_segment) LIKE '%cap%'
            THEN 'contribution_inquiry'
            WHEN LOWER(transcript_segment) LIKE '%withdraw%' OR
                 LOWER(transcript_segment) LIKE '%access%' OR
                 LOWER(transcript_segment) LIKE '%medical%'
            THEN 'withdrawal_inquiry'
            WHEN LOWER(transcript_segment) LIKE '%insurance%' OR
                 LOWER(transcript_segment) LIKE '%cover%'
            THEN 'insurance_inquiry'
            WHEN LOWER(transcript_segment) LIKE '%performance%' OR
                 LOWER(transcript_segment) LIKE '%return%'
            THEN 'performance_inquiry'
            WHEN LOWER(transcript_segment) LIKE '%beneficiary%'
            THEN 'beneficiary_update'
            WHEN LOWER(transcript_segment) LIKE '%complaint%' OR
                 LOWER(transcript_segment) LIKE '%frustrated%'
            THEN 'complaint'
            ELSE 'general_inquiry'
        END AS intent_category,
        
        -- Compliance checking
        CASE 
            WHEN LOWER(transcript_segment) LIKE '%guarantee%' OR
                 LOWER(transcript_segment) LIKE '%promise%' OR
                 LOWER(transcript_segment) LIKE '%definitely%' AND 
                 (LOWER(transcript_segment) LIKE '%return%' OR 
                  LOWER(transcript_segment) LIKE '%grow%')
            THEN 'guarantee_language'
            WHEN speaker = 'agent' AND 
                 (LOWER(transcript_segment) LIKE '%should%' OR
                  LOWER(transcript_segment) LIKE '%recommend%' OR
                  LOWER(transcript_segment) LIKE '%best option%')
            THEN 'personal_advice'
            WHEN speaker = 'agent' AND 
                 LOWER(transcript_segment) LIKE '%balance%' AND
                 LOWER(transcript_segment) NOT LIKE '%your%'
            THEN 'privacy_breach'
            ELSE 'ok'
        END AS compliance_flag,
        
        CASE 
            WHEN LOWER(transcript_segment) LIKE '%guarantee%' OR
                 LOWER(transcript_segment) LIKE '%promise%'
            THEN 'CRITICAL'
            WHEN LOWER(transcript_segment) LIKE '%should%' AND speaker = 'agent'
            THEN 'HIGH'
            WHEN LOWER(transcript_segment) LIKE '%balance%' AND speaker = 'agent'
            THEN 'HIGH'
            ELSE 'LOW'
        END AS compliance_severity,
        
        CURRENT_TIMESTAMP() AS enriched_at
        
    FROM STREAM(member_analytics.call_center.zerobus_transcripts)
)
KEYS (call_id, timestamp)
APPLY AS DELETE WHEN timestamp < CURRENT_TIMESTAMP() - INTERVAL 90 DAYS
SEQUENCE BY timestamp
STORED AS SCALAR;

