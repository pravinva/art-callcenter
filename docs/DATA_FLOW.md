# Data Flow Guide: Bronze → Silver → Gold

## Overview

The ART Call Center system uses a three-layer data architecture:

```
Bronze Layer → Silver Layer → Gold Layer
   (Input)      (Enrichment)    (Analytics)
```

## Data Flow Details

### 🔵 Bronze Layer: `zerobus_transcripts`

**Purpose**: Raw call transcript data ingestion  
**Source**: Zerobus SDK ingestion script  
**Current Status**: 358 rows

**How to Populate**:
```bash
# Generate 50 test calls
python scripts/03_zerobus_ingestion.py 50

# Generate 100 calls at specific throughput
python scripts/03_zerobus_ingestion.py 100 --throughput 10

# Continuous mode (generates calls continuously)
python scripts/03_zerobus_ingestion.py --continuous --duration 60

# High throughput simulation
python scripts/03_zerobus_ingestion.py 200 --throughput 20
```

**Script**: `scripts/03_zerobus_ingestion.py`

**What Happens**:
- Script generates mock Genesys Cloud call transcripts
- Streams data to `member_analytics.call_center.zerobus_transcripts` table via Zerobus SDK
- Simulates realistic call patterns (variable lengths, timing, agents)

---

### 🟡 Silver Layer: `enriched_transcripts`

**Purpose**: Real-time enrichment with AI insights  
**Source**: Automatically reads from Bronze layer  
**Current Status**: 358 rows  
**Pipeline**: `art-callcenter-enrichment-serverless` (CONTINUOUS)

**What Happens Automatically**:
1. DLT pipeline continuously monitors Bronze layer
2. New transcripts are processed in real-time
3. Adds enrichment:
   - **Sentiment**: positive/negative/neutral (keyword-based)
   - **Intent**: general_inquiry, complaint, contribution_inquiry, etc.
   - **Compliance**: Flags violations (guarantee returns, personal advice, etc.)
   - **Confidence**: Confidence scores for intent detection

**No Action Required**: Pipeline runs continuously and processes new Bronze data automatically

---

### 🟢 Gold Layer: Analytics Tables

**Purpose**: Batch analytics and summaries  
**Source**: Automatically reads from Silver layer  
**Current Status**: 
- `call_summaries`: 356 rows
- `agent_performance`: 321 rows
- `member_interaction_history`: 356 rows
- `daily_call_statistics`: 2 rows

**Pipeline**: `art-callcenter-gold-layer` (BATCH, hourly)  
**Scheduled Job**: `art-callcenter-gold-layer-batch` (runs every hour)

**What Happens Automatically**:
1. Hourly batch job runs Gold layer pipeline
2. Processes **completed calls** from Silver layer
3. Creates aggregated analytics:
   - Call summaries with metrics
   - Agent performance KPIs
   - Member interaction history
   - Daily call center statistics

**Note**: Gold layer only processes **completed calls** (calls that haven't had new segments for ~10 minutes). This is why Gold (356) < Silver (358) - some calls are still active.

---

## To Get More Data in Gold Layer

### Step 1: Generate More Bronze Layer Data

```bash
# Generate 100 new calls
python scripts/03_zerobus_ingestion.py 100

# Or generate continuously for testing
python scripts/03_zerobus_ingestion.py --continuous --duration 30
```

### Step 2: Wait for Processing

1. **Silver Layer**: Processes automatically (continuous pipeline)
   - Check: Databricks UI → Workflows → Delta Live Tables → `art-callcenter-enrichment-serverless`
   - Status should be "RUNNING"

2. **Gold Layer**: Processes on next hourly run
   - Check: Databricks UI → Workflows → Jobs → `art-callcenter-gold-layer-batch`
   - Or manually trigger: Databricks UI → Workflows → Delta Live Tables → `art-callcenter-gold-layer` → Start

### Step 3: Verify Data Flow

```bash
# Check row counts
python scripts/test_gold_layer.py
```

---

## Data Flow Summary

| Layer | Table | Rows | Source | Update Frequency |
|-------|-------|------|--------|------------------|
| Bronze | `zerobus_transcripts` | 358 | Manual (Zerobus script) | On-demand |
| Silver | `enriched_transcripts` | 358 | Automatic (continuous DLT) | Real-time |
| Gold | `call_summaries` | 356 | Automatic (batch DLT) | Hourly |

---

## Quick Reference

**Generate Test Data**:
```bash
python scripts/03_zerobus_ingestion.py 50
```

**Check Data Flow**:
```bash
python scripts/test_gold_layer.py
```

**View Analytics**:
```bash
streamlit run app/analytics_dashboard.py --server.port 8521
```

**Monitor Pipelines**:
- Silver: Databricks UI → Workflows → Delta Live Tables → `art-callcenter-enrichment-serverless`
- Gold: Databricks UI → Workflows → Delta Live Tables → `art-callcenter-gold-layer`

