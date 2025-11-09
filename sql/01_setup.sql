-- Phase 1.1: Setup SQL Script
-- Creates catalog, schema, and Zerobus target table
-- Run via: databricks-sql-cli -f sql/01_setup.sql

-- Create catalog
CREATE CATALOG IF NOT EXISTS member_analytics
COMMENT 'ART Call Center analytics catalog';

-- Grant usage
GRANT USE CATALOG ON CATALOG member_analytics TO `account users`;

-- Create schema
CREATE SCHEMA IF NOT EXISTS member_analytics.call_center
COMMENT 'Call center data schema';

-- Grant usage on schema
GRANT USE SCHEMA ON SCHEMA member_analytics.call_center TO `account users`;

-- Create Zerobus target table
CREATE TABLE IF NOT EXISTS member_analytics.call_center.zerobus_transcripts (
    call_id STRING NOT NULL,
    member_id STRING NOT NULL,
    member_name STRING,
    agent_id STRING,
    timestamp TIMESTAMP NOT NULL,
    transcript_segment STRING NOT NULL,
    speaker STRING NOT NULL,
    confidence DOUBLE,
    queue STRING,
    scenario STRING,
    complexity STRING,
    channel STRING,
    member_balance DOUBLE,
    member_life_stage STRING
)
USING DELTA
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true'
)
COMMENT 'Raw call transcripts ingested via Zerobus';

-- Create partition for better query performance
ALTER TABLE member_analytics.call_center.zerobus_transcripts
SET TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Grant permissions
GRANT SELECT, INSERT ON TABLE member_analytics.call_center.zerobus_transcripts TO `account users`;

