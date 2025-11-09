# Automated Pipeline Architecture

## Overview
All data processing is automated via pipelines - no manual steps required.

## Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. ZEROBUS INGESTION (Automated)                          │
│     - Python script with Zerobus SDK                       │
│     - Streams transcripts → Delta Table                     │
│     - Runs continuously or on-demand                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  2. DLT PIPELINE (Automated - Continuous)                   │
│     - Delta Live Tables pipeline                            │
│     - Processes streaming data automatically                │
│     - Enriches with sentiment, intent, compliance            │
│     - Runs 24/7, no manual intervention                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  3. ONLINE TABLE (Automated Refresh)                        │
│     - Auto-refreshes from enriched_transcripts             │
│     - Sub-second query latency                             │
│     - Always up-to-date                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  4. UC FUNCTIONS (Available for Agent)                     │
│     - Query live data                                       │
│     - Used by GenAI Agent                                   │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Steps (One-Time Setup)

### Step 1: Upload DLT Notebook
```bash
python scripts/upload_dlt_notebook.py
```

### Step 2: Create DLT Pipeline
- Via UI: Workflows → Delta Live Tables → Create Pipeline
- Select uploaded notebook
- Enable "Continuous" mode
- Target: `member_analytics.call_center`

### Step 3: Start Pipeline
- Pipeline runs automatically after creation
- Processes data continuously
- No manual intervention needed

## Automation Features

✅ **Continuous Processing**: DLT pipeline runs 24/7
✅ **Auto-scaling**: Handles varying data volumes
✅ **Error Handling**: Automatic retries and error recovery
✅ **Data Quality**: Built-in expectations and monitoring
✅ **Zero Manual Steps**: Once deployed, fully automated

## Monitoring

- Pipeline status: Workflows → Delta Live Tables
- Data quality: Pipeline UI shows expectations
- Metrics: Built-in DLT metrics dashboard

