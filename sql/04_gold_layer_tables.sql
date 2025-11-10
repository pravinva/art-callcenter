-- Gold Layer Tables Setup
-- These tables are created by the Gold Layer DLT pipeline
-- This SQL script is for reference/documentation purposes

-- ============================================================================
-- Gold Layer Tables (Created by DLT Pipeline)
-- ============================================================================

-- Table 1: Call Summaries
-- Aggregates enriched transcripts into post-call summaries
-- Created by: dlt_gold_layer_pipeline.py -> call_summaries()
CREATE TABLE IF NOT EXISTS member_analytics.call_center.call_summaries (
    call_id STRING NOT NULL,
    member_id STRING,
    member_name STRING,
    agent_id STRING,
    scenario STRING,
    complexity STRING,
    channel STRING,
    call_start_time TIMESTAMP,
    call_end_time TIMESTAMP,
    call_date DATE,
    total_segments INT,
    speakers_count INT,
    positive_count INT,
    negative_count INT,
    neutral_count INT,
    sentiment_sequence ARRAY<STRING>,
    intents_detected ARRAY<STRING>,
    intent_count INT,
    compliance_violations_count INT,
    compliance_violations ARRAY<STRING>,
    max_compliance_severity INT,
    full_transcript STRING,
    member_balance DOUBLE,
    member_life_stage STRING,
    avg_confidence DOUBLE,
    min_confidence DOUBLE,
    max_confidence DOUBLE,
    call_duration_seconds INT,
    call_duration_minutes DOUBLE,
    overall_sentiment STRING,
    primary_intent STRING,
    has_compliance_issues BOOLEAN,
    compliance_severity_level STRING,
    call_summary STRING,
    summary_created_at TIMESTAMP
)
USING DELTA
TBLPROPERTIES (
    "quality" = "gold",
    "delta.autoOptimize.optimizeWrite" = "true",
    "delta.autoOptimize.autoCompact" = "true"
);

-- Table 2: Agent Performance
-- Daily agent performance metrics and KPIs
-- Created by: dlt_gold_layer_pipeline.py -> agent_performance()
CREATE TABLE IF NOT EXISTS member_analytics.call_center.agent_performance (
    agent_id STRING NOT NULL,
    call_date DATE NOT NULL,
    total_calls INT,
    avg_call_duration_minutes DOUBLE,
    min_call_duration_minutes DOUBLE,
    max_call_duration_minutes DOUBLE,
    total_call_time_minutes DOUBLE,
    avg_positive_segments DOUBLE,
    avg_negative_segments DOUBLE,
    avg_neutral_segments DOUBLE,
    positive_calls INT,
    negative_calls INT,
    neutral_calls INT,
    calls_with_compliance_issues INT,
    total_compliance_violations INT,
    avg_compliance_violations_per_call DOUBLE,
    critical_compliance_issues INT,
    high_compliance_issues INT,
    unique_intents_handled INT,
    intents_handled ARRAY<STRING>,
    unique_scenarios_handled INT,
    unique_members_served INT,
    avg_transcript_confidence DOUBLE,
    min_transcript_confidence DOUBLE,
    compliance_rate DOUBLE,
    positive_sentiment_rate DOUBLE,
    negative_sentiment_rate DOUBLE,
    calls_per_hour DOUBLE,
    performance_score DOUBLE,
    metrics_calculated_at TIMESTAMP
)
USING DELTA
TBLPROPERTIES (
    "quality" = "gold",
    "delta.autoOptimize.optimizeWrite" = "true",
    "delta.autoOptimize.autoCompact" = "true"
);

-- Table 3: Member Interaction History
-- Historical interaction records for members
-- Created by: dlt_gold_layer_pipeline.py -> member_interaction_history()
CREATE TABLE IF NOT EXISTS member_analytics.call_center.member_interaction_history (
    interaction_id STRING NOT NULL,
    member_id STRING NOT NULL,
    member_name STRING,
    interaction_date TIMESTAMP,
    call_date DATE,
    interaction_type STRING,
    interaction_topic STRING,
    summary STRING,
    channel STRING,
    agent_id STRING,
    overall_sentiment STRING,
    primary_intent STRING,
    has_compliance_issues BOOLEAN,
    compliance_severity_level STRING,
    call_duration_minutes DOUBLE,
    total_segments INT,
    member_balance DOUBLE,
    member_life_stage STRING,
    complexity STRING,
    interaction_created_at TIMESTAMP
)
USING DELTA
TBLPROPERTIES (
    "quality" = "gold",
    "delta.autoOptimize.optimizeWrite" = "true",
    "delta.autoOptimize.autoCompact" = "true"
);

-- Table 4: Daily Call Statistics
-- Daily aggregated call center statistics
-- Created by: dlt_gold_layer_pipeline.py -> daily_call_statistics()
CREATE TABLE IF NOT EXISTS member_analytics.call_center.daily_call_statistics (
    call_date DATE NOT NULL,
    total_calls INT,
    active_agents INT,
    unique_members INT,
    avg_call_duration_minutes DOUBLE,
    total_call_time_minutes DOUBLE,
    positive_calls INT,
    negative_calls INT,
    neutral_calls INT,
    calls_with_compliance_issues INT,
    total_compliance_violations INT,
    critical_issues INT,
    high_issues INT,
    unique_intents INT,
    intents_handled ARRAY<STRING>,
    unique_scenarios INT,
    high_complexity_calls INT,
    medium_complexity_calls INT,
    low_complexity_calls INT,
    positive_sentiment_rate DOUBLE,
    compliance_rate DOUBLE,
    avg_calls_per_agent DOUBLE,
    stats_calculated_at TIMESTAMP
)
USING DELTA
TBLPROPERTIES (
    "quality" = "gold",
    "delta.autoOptimize.optimizeWrite" = "true",
    "delta.autoOptimize.autoCompact" = "true"
);

-- ============================================================================
-- Indexes and Optimizations
-- ============================================================================

-- Note: Delta tables automatically optimize, but you can create Z-ORDER indexes
-- for better query performance on common filters

-- Optimize call_summaries for date and member queries
-- ALTER TABLE member_analytics.call_center.call_summaries OPTIMIZE ZORDER BY (call_date, member_id);

-- Optimize agent_performance for date and agent queries
-- ALTER TABLE member_analytics.call_center.agent_performance OPTIMIZE ZORDER BY (call_date, agent_id);

-- Optimize member_interaction_history for member and date queries
-- ALTER TABLE member_analytics.call_center.member_interaction_history OPTIMIZE ZORDER BY (member_id, interaction_date);

-- ============================================================================
-- Sample Queries
-- ============================================================================

-- Get call summary for a specific call
-- SELECT * FROM member_analytics.call_center.call_summaries WHERE call_id = 'CALL-...';

-- Get agent performance for today
-- SELECT * FROM member_analytics.call_center.agent_performance WHERE call_date = CURRENT_DATE();

-- Get member's recent interaction history
-- SELECT * FROM member_analytics.call_center.member_interaction_history WHERE member_id = 'MEMBER-...' ORDER BY interaction_date DESC LIMIT 10;

-- Get daily statistics
-- SELECT * FROM member_analytics.call_center.daily_call_statistics ORDER BY call_date DESC LIMIT 7;

