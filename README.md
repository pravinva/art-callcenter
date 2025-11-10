# ART Call Center - Real-Time AI Agent Assist System

A complete end-to-end solution for providing AI-powered assistance to call center agents during live customer calls, built on Databricks Zerobus, Delta Live Tables, and GenAI Agent Framework.

## Overview

This system provides real-time AI assistance to Australian Retirement Trust (ART) call center agents by:
- **Streaming call transcripts** in real-time via Zerobus
- **Enriching data** with sentiment analysis, intent detection, and compliance checking
- **Providing AI suggestions** through a GenAI agent with access to knowledge base and member history
- **Alerting on compliance issues** in real-time as they occur

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Call Flow Architecture                        │
└─────────────────────────────────────────────────────────────────┘

Genesys Cloud / Call Center
    │
    │ (Real-time audio → transcript)
    ▼
Zerobus SDK (Ingestion)
    │
    │ (Streaming to Delta)
    ▼
member_analytics.call_center.zerobus_transcripts (Bronze)
    │
    │ (DLT Pipeline - Continuous Processing)
    ▼
member_analytics.call_center.enriched_transcripts (Silver)
    │
    │ ├─ Sentiment Analysis (positive/negative/neutral)
    │ ├─ Intent Detection (general_inquiry, contribution, withdrawal, etc.)
    │ └─ Compliance Detection (financial_advice, guarantee, etc.)
    │
    │ (Gold Layer DLT Pipeline - Batch Processing)
    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Gold Layer (Batch Post-Call)                 │
├─────────────────────────────────────────────────────────────────┤
│  • call_summaries - Post-call summaries with metrics          │
│  • agent_performance - Daily agent KPIs                         │
│  • member_interaction_history - Historical member records       │
│  • daily_call_statistics - Daily aggregated statistics         │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Real-Time Access Layer                        │
├─────────────────────────────────────────────────────────────────┤
│  • Synced Tables (for low-latency reads)                         │
│  • UC Functions (agent tools)                                   │
│    - get_live_call_context()                                    │
│    - check_compliance_realtime()                               │
│    - search_knowledge_base()                                    │
│    - get_member_history()                                      │
└─────────────────────────────────────────────────────────────────┘
    │
    │ (Streamlit Dashboard)
    ▼
┌─────────────────────────────────────────────────────────────────┐
│              Streamlit Agent Dashboard                          │
├─────────────────────────────────────────────────────────────────┤
│  Column 1: Live Transcript                                      │
│  Column 2: AI Assistant (Suggestions, Member Info, KB)         │
│  Column 3: Compliance Alerts                                   │
└─────────────────────────────────────────────────────────────────┘
    │
    │ (GenAI Agent - LangGraph)
    ▼
Databricks Claude Sonnet 4.5 (LLM)
    │
    └─ Uses UC Functions as tools
```

## Databricks Components

### 1. **Zerobus Ingestion** (Bronze Layer)
- **Table**: `member_analytics.call_center.zerobus_transcripts`
- **Purpose**: Raw call transcript data from Genesys Cloud
- **Schema**: `call_id`, `member_id`, `member_name`, `timestamp`, `speaker`, `transcript_segment`
- **Update Frequency**: Real-time streaming (as transcripts arrive)

### 2. **DLT Pipeline** (Silver Layer)
- **Pipeline Name**: `art-callcenter-enrichment-serverless`
- **Notebook**: `/Workspace/Users/pravin.varma@databricks.com/art-callcenter/dlt_enrichment_pipeline`
- **Output Table**: `member_analytics.call_center.enriched_transcripts`
- **Update Frequency**: Continuous (processes new transcripts as they arrive via streaming)

### 3. **Gold Layer DLT Pipeline** (Batch Post-Call Processing)
- **Pipeline Name**: `art-callcenter-gold-layer`
- **Notebook**: `/Workspace/Users/pravin.varma@databricks.com/art-callcenter/dlt_gold_layer_pipeline`
- **Output Tables**:
  - `member_analytics.call_center.call_summaries` - Post-call summaries with key metrics
  - `member_analytics.call_center.agent_performance` - Daily agent performance KPIs
  - `member_analytics.call_center.member_interaction_history` - Historical member interaction records
  - `member_analytics.call_center.daily_call_statistics` - Daily aggregated call center statistics
- **Update Frequency**: Batch (runs hourly via scheduled job)
- **Purpose**: Process completed calls and generate analytics, summaries, and historical records

#### Processing Logic

The DLT pipeline reads from the Bronze layer (`zerobus_transcripts`) and applies real-time enrichment using Spark SQL transformations. Each transcript segment is analyzed independently as it arrives.

##### Sentiment Detection

Sentiment is detected using pattern matching on the transcript text:

- **Positive Sentiment**: Detected when transcript contains keywords like `thank`, `appreciate`, `great`, `perfect`
  - Example: "Thank you so much for your help" → `sentiment = 'positive'`
  
- **Negative Sentiment**: Detected when transcript contains keywords like `frustrated`, `angry`, `disappointed`, `terrible`
  - Example: "I'm frustrated with this process" → `sentiment = 'negative'`
  
- **Neutral Sentiment**: Default classification when no positive or negative keywords are found
  - Example: "What is my account balance?" → `sentiment = 'neutral'`

The detection uses case-insensitive regex pattern matching: `lower(transcript_segment).rlike("pattern")`

##### Intent Detection

Intent is categorized using keyword-based pattern matching to identify the primary topic of the conversation:

- **contribution_inquiry**: Keywords like `contribution`, `cap`
  - Example: "What are the contribution limits?" → `intent_category = 'contribution_inquiry'`
  
- **withdrawal_inquiry**: Keywords like `withdraw`, `access`, `medical`
  - Example: "How do I access my funds?" → `intent_category = 'withdrawal_inquiry'`
  
- **insurance_inquiry**: Keywords like `insurance`, `cover`
  - Example: "What insurance coverage do I have?" → `intent_category = 'insurance_inquiry'`
  
- **performance_inquiry**: Keywords like `performance`, `return`
  - Example: "How has my fund performed?" → `intent_category = 'performance_inquiry'`
  
- **beneficiary_update**: Keywords like `beneficiary`
  - Example: "I need to update my beneficiary" → `intent_category = 'beneficiary_update'`
  
- **complaint**: Keywords like `complaint`, `frustrated`
  - Example: "I want to file a complaint" → `intent_category = 'complaint'`
  
- **general_inquiry**: Default category when no specific intent keywords are matched
  - Example: "Hello, how can I help?" → `intent_category = 'general_inquiry'`

The detection checks for keyword patterns in order, and the first match determines the intent category.

##### Compliance Detection

Compliance violations are detected using a combination of keyword patterns and speaker identification (agent vs. customer):

- **guarantee_language**: Detected when transcript contains `guarantee`, `promise`, or combinations like `definitely` + `return`/`grow`
  - Example: "I guarantee you'll get great returns" → `compliance_flag = 'guarantee_language'`
  - Severity: `CRITICAL`
  
- **personal_advice**: Detected when speaker is `agent` AND transcript contains `should`, `recommend`, or `best option`
  - Example: Agent says "You should invest in this fund" → `compliance_flag = 'personal_advice'`
  - Severity: `HIGH`
  
- **privacy_breach**: Detected when speaker is `agent` AND transcript mentions `balance` but NOT `your` (indicating potential disclosure of another member's information)
  - Example: Agent says "The balance is $50,000" (without "your") → `compliance_flag = 'privacy_breach'`
  - Severity: `HIGH`
  
- **ok**: Default when no compliance violations are detected
  - Example: "Thank you for calling" → `compliance_flag = 'ok'`
  - Severity: `LOW`

The compliance detection logic uses conditional checks:
- First checks for guarantee language (highest priority)
- Then checks for personal advice (only for agent utterances)
- Then checks for privacy breaches (only for agent utterances)
- Defaults to `ok` if no violations detected

##### Severity Assignment

Compliance severity is assigned based on the violation type:
- **CRITICAL**: Guarantee language detected
- **HIGH**: Personal advice or privacy breach detected
- **LOW**: Default for all other cases (including `ok`)

##### Processing Flow

1. **Stream Ingestion**: DLT reads new records from `zerobus_transcripts` table using `spark.readStream.table()`
2. **Transformation**: Each record is enriched with sentiment, intent, and compliance flags using Spark SQL `withColumn()` transformations
3. **Quality Checks**: Data quality expectations ensure valid timestamps and speaker values (`expect_or_drop`)
4. **Write to Silver**: Enriched records are written to `enriched_transcripts` table with auto-optimization enabled
5. **Real-time Availability**: New enriched records are immediately available for querying via UC Functions and the Streamlit dashboard

The pipeline processes records incrementally as they arrive, ensuring low latency (typically <5 seconds from ingestion to availability).

### 3. **Unity Catalog Functions** (Agent Tools)
Located in `member_analytics.call_center` schema:

#### `get_live_call_context(call_id)`
- Returns: Member name, balance, recent transcript (last 500 chars), sentiment, intents, compliance issues
- Used by: GenAI agent to understand current call context
- Update Frequency: Real-time (queries enriched_transcripts table)

#### `check_compliance_realtime(call_id)`
- Returns: List of compliance violations with severity and transcript segments
- Used by: Compliance alerts panel in Streamlit dashboard
- Update Frequency: Real-time (queries enriched_transcripts table)

#### `search_knowledge_base(query)`
- Returns: Relevant KB articles matching search query
- Used by: GenAI agent to find policy information
- Update Frequency: On-demand (when agent searches KB)

#### `get_member_history(member_id)`
- Returns: Recent interaction history for a member
- Used by: GenAI agent to understand member context
- Update Frequency: On-demand (when agent needs history)

### 4. **GenAI Agent** (LangGraph)
- **Model**: Databricks Claude Sonnet 4.5
- **Framework**: LangChain + LangGraph
- **Tools**: All 4 UC Functions above
- **Purpose**: Provides real-time suggestions to agents during calls
- **Response Time**: Optimized to <10 seconds (with caching)

### 5. **Dash Dashboard** (Primary UI)
- **Location**: `app_dash/app.py`
- **Port**: 8050
- **Features**:
  - Live transcript display with sentiment indicators
  - AI-generated suggestions with response time display
  - Member 360 view (Member Info tab)
  - Knowledge base search with suggested questions
  - Real-time compliance alerts
  - Call selection dropdown (shows calls from last 24 hours)
  - Optimized refresh logic (only updates when data changes)
  - Supervisor dashboard (port 8050/supervisor)
  - Analytics dashboard (port 8050/analytics)
- **Performance**: Optimized callbacks prevent unnecessary refreshes

### 6. **Streamlit Dashboard** (Legacy/Alternative)
- **Location**: `app/agent_dashboard.py`
- **Port**: 8520
- **Features**: Same as Dash dashboard (alternative implementation)

## Typical Agent Scenario

### Scenario: Member calls asking about contribution limits

1. **Call Starts** (00:00)
   - Call center system sends transcript to Zerobus
   - Zerobus ingests into `zerobus_transcripts` table
   - DLT pipeline processes first utterance

2. **First Utterance** (00:05)
   - Member: "Hi, I want to know about contribution limits"
   - DLT enriches:
     - Sentiment: `neutral`
     - Intent: `contribution`
     - Compliance: `ok`
   - Streamlit dashboard shows transcript in Column 1

3. **Agent Needs Help** (00:30)
   - Agent clicks "Get AI Suggestion" button
   - GenAI agent:
     - Calls `get_live_call_context()` → Gets call context
     - Calls `search_knowledge_base("contribution limits")` → Finds KB articles
     - Generates suggestion: "Member asking about contribution limits. Suggested response: 'The concessional cap for 2024-25 is $30,000, including employer contributions. Would you like catch-up contribution details?'"
   - Response time: ~5-8 seconds
   - Suggestion appears in Column 2

4. **Compliance Alert** (01:15)
   - Agent says: "I guarantee you'll get great returns"
   - DLT detects compliance violation:
     - Compliance Flag: `guarantee`
     - Severity: `CRITICAL`
   - `check_compliance_realtime()` function returns violation
   - Streamlit dashboard shows **CRITICAL** alert in Column 3 (red banner)
   - Alert includes: Severity, violation type, transcript segment

5. **Agent Corrects** (01:30)
   - Agent sees compliance alert
   - Agent corrects statement
   - Next utterance has compliance: `ok`
   - Alert remains visible but new violations are highlighted

6. **Call Continues** (02:00+)
   - Transcript updates in real-time
   - Compliance alerts update as new violations occur
   - AI suggestions available on-demand
   - Member info updates as more context is gathered

## Compliance Alerts (Right Column)

### What Are Compliance Alerts?

Compliance alerts flag potential regulatory violations in real-time during calls. They help agents:
- **Avoid violations** before they escalate
- **Correct mistakes** immediately
- **Maintain compliance** with financial services regulations

### When Do Compliance Alerts Update?

Compliance alerts update **in real-time** as the DLT pipeline processes new transcript segments:

1. **New Transcript Segment Arrives**
   - Zerobus ingests new utterance
   - DLT pipeline processes it (typically <5 seconds)

2. **Compliance Detection Logic**
   - DLT checks transcript segment against compliance rules:
     - Keywords/phrases indicating financial advice
     - Guarantees or promises of returns
     - Pressure tactics
     - Misinformation patterns

3. **Alert Display**
   - If violation detected (`compliance_flag != 'ok'`):
     - Alert appears in Column 3
     - Color-coded by severity:
       - **CRITICAL** (red): Immediate action required
       - **HIGH** (orange): Significant concern
       - **MEDIUM** (yellow): Moderate concern
       - **LOW** (blue): Minor issue
   - Alert shows: Severity, violation type, transcript segment

4. **Update Frequency**
   - Alerts refresh when:
     - New transcript segments arrive (every few seconds)
     - User manually refreshes dashboard
     - New call is selected

### Compliance Detection Rules

The DLT pipeline uses pattern matching and keyword detection:

- **Financial Advice**: Phrases like "you should invest in", "I recommend", "best option for you"
- **Guarantee**: Phrases like "guaranteed returns", "I guarantee", "promised performance"
- **Pressure**: Phrases like "act now", "limited time", "don't miss out"
- **Misinformation**: Contradicts known policies or provides incorrect information

## Quick Start

### Prerequisites

- Python 3.9+
- Databricks CLI configured (`~/.databrickscfg`)
- Access to Databricks workspace
- SQL Warehouse ID: `4b9b953939869799`

### Installation

```bash
# Clone repository
git clone https://github.com/pravinva/art-callcenter.git
cd art-callcenter

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Setup Steps

1. **Configure Databricks CLI** (`~/.databrickscfg`):
```ini
[DEFAULT]
host = https://your-workspace.cloud.databricks.com/
token = your-token
```

2. **Create Secrets Scope** (for Zerobus credentials):
```bash
# Follow instructions in ZEROBUS_CREDENTIALS.md
```

3. **Run Setup SQL**:
```bash
python scripts/run_sql.py sql/01_setup.sql
```

4. **Deploy DLT Pipeline**:
```bash
python scripts/05_deploy_dlt_pipeline.py
```

5. **Create UC Functions**:
```bash
python scripts/06_create_uc_functions.py
```

6. **Run Dash Dashboard** (Recommended):
```bash
cd app_dash
source ../venv/bin/activate
python app.py
# Dashboard available at http://localhost:8050
```

**Or Run Streamlit Dashboard** (Alternative):
```bash
./run_dashboard.sh
# Or: streamlit run app/agent_dashboard.py --server.port 8520
```

### Generate Mock Data

```bash
# Generate sample calls
python scripts/02_mock_data_generator.py

# Ingest into Zerobus (or use SQL fallback)
python scripts/03_zerobus_ingestion.py
# Or: python scripts/03_zerobus_ingestion_sql.py
```

## Project Structure

```
art-callcenter/
├── app/
│   ├── agent_dashboard.py      # Streamlit dashboard (legacy)
│   ├── analytics_dashboard.py   # Streamlit analytics dashboard
│   ├── supervisor_dashboard.py # Streamlit supervisor dashboard
│   └── README.md                # Dashboard documentation
├── app_dash/
│   ├── app.py                   # Main Dash application
│   ├── components/              # Reusable Dash components
│   │   ├── common.py
│   │   ├── transcript.py
│   │   ├── ai_suggestions.py
│   │   ├── member_info.py
│   │   ├── kb_search.py
│   │   ├── compliance.py
│   │   ├── analytics.py
│   │   └── supervisor.py
│   ├── pages/                   # Page modules
│   │   ├── analytics.py
│   │   └── supervisor.py
│   ├── utils/                   # Utility functions
│   │   ├── state_manager.py
│   │   ├── data_fetchers.py
│   │   ├── databricks_client.py
│   │   ├── ai_suggestions.py
│   │   ├── kb_search.py
│   │   ├── analytics_data.py
│   │   └── supervisor_data.py
│   └── assets/                  # Static assets (logo, etc.)
├── config/
│   └── config.py                # Centralized configuration
├── notebooks/
│   └── dlt_enrichment_pipeline.py  # DLT pipeline logic
├── scripts/
│   ├── 01_setup_zerobus.py     # Setup verification
│   ├── 02_mock_data_generator.py  # Mock data generation
│   ├── 03_zerobus_ingestion.py    # Zerobus ingestion
│   ├── 05_deploy_dlt_pipeline.py  # DLT deployment
│   ├── 06_create_uc_functions.py   # UC Functions creation
│   ├── 07_genai_agent.py          # GenAI agent development
│   └── 08_deploy_streamlit_app.py # Streamlit deployment
├── sql/
│   ├── 01_setup.sql            # Catalog, schema, tables
│   ├── 02_dlt_enrichment.sql   # DLT pipeline SQL (legacy)
│   ├── 03_uc_functions.sql     # UC Functions definitions
│   └── 03_create_dependencies.sql  # Dependency tables
├── docs/                        # Documentation
│   ├── DEMO_FLOW.md            # Demo flow guide
│   └── DEMO_QUICK_REFERENCE.md # Quick reference
├── requirements.txt            # Python dependencies
├── run_dashboard.sh           # Dashboard launcher
└── README.md                  # This file
```

## Configuration

All configuration is centralized in `config/config.py`:

- **Workspace**: Databricks workspace URL
- **Catalog/Schema**: `member_analytics.call_center`
- **SQL Warehouse**: `4b9b953939869799`
- **LLM Endpoint**: `databricks-claude-sonnet-4-5`
- **Tables**: `zerobus_transcripts`, `enriched_transcripts`
- **UC Functions**: All 4 function names

## Performance Optimizations

The system has been optimized for speed and efficiency:

### Data Fetching
- **SQL Timeouts**: Reduced from 30s to 10s
- **Polling Frequency**: Increased from 0.5s to 0.2s
- **Response Caching**: 30-second cache for AI suggestions
- **LLM Settings**: `max_tokens=500`, `timeout=15s`
- **Agent Prompt**: Optimized to use only necessary tools

### Dashboard Optimizations
- **Smart Refresh Logic**: Callbacks only update when data actually changes
  - Transcript refreshes only when call changes or new data arrives
  - Active calls dropdown updates only when call list changes
  - Compliance alerts update only when call changes or transcript updates
- **PreventUpdate Pattern**: Uses Dash `PreventUpdate` to avoid unnecessary renders
- **Data Comparison**: Compares current vs previous data before refreshing

### Knowledge Base
- **Vector Search**: Uses Databricks Vector Search for semantic similarity
- **Performance**: ~2 seconds per search (vector search overhead)
- **Fallback**: SQL keyword search if vector search unavailable
- **Suggested Questions**: Always returns 5 context-aware questions
  - Detects negative sentiment and shows complaint/dispute questions
  - Falls back to default questions if no context found

**Typical Response Times**:
- Cached AI suggestion: <0.1s
- Fresh AI suggestion: 5-10s
- KB Vector Search: ~2s
- KB SQL Fallback: <1s
- Compliance alert update: <5s (DLT processing)
- Transcript update: Real-time (as data arrives, no unnecessary refreshes)

## Testing

See `TESTING_GUIDE.md` for comprehensive testing checklist.

Quick test:
1. Generate mock data: `python scripts/02_mock_data_generator.py`
2. Ingest data: `python scripts/03_zerobus_ingestion_sql.py`
3. Open dashboard: `./run_dashboard.sh`
4. Select a call from sidebar
5. Click "Get AI Suggestion"
6. Observe compliance alerts (if any violations in mock data)

## Documentation

- **Quick Start**: `QUICK_START.md`
- **Pipeline Architecture**: `PIPELINE_ARCHITECTURE.md`
- **Zerobus Setup**: `ZEROBUS_CREDENTIALS.md`
- **Troubleshooting**: `TROUBLESHOOTING_GUIDE.md`
- **Testing Guide**: `TESTING_GUIDE.md`

## Security & Compliance

- **Authentication**: Uses Databricks CLI credentials (`~/.databrickscfg`)
- **Secrets**: Stored in Databricks Secrets Scope
- **Unity Catalog**: All tables and functions use Unity Catalog for access control
- **Compliance Detection**: Real-time flagging of potential violations
- **Audit Trail**: All transcript data stored in Delta tables for audit

## Known Limitations

1. **Mock Data Only**: Currently uses generated mock data (not connected to real Genesys Cloud)
2. **KB Stub**: Knowledge base search returns sample data (requires `knowledge_base.kb_articles` table)
3. **Streamlit Single-Threaded**: UI may briefly freeze during AI processing (mitigated with placeholders)

## Batch Post-Call Processing (Gold Layer)

The system includes comprehensive batch post-call processing that runs on a schedule to process completed calls:

### Gold Layer Tables

1. **`call_summaries`** - Post-call summaries with:
   - Call duration, sentiment breakdown, intent categories
   - Compliance violations and severity
   - Full transcript and call summary text
   - Member information and call metadata

2. **`agent_performance`** - Daily agent KPIs:
   - Total calls, average call duration
   - Sentiment rates (positive/negative/neutral)
   - Compliance rates and violation counts
   - Performance score (weighted composite metric)
   - Calls per hour, unique intents handled

3. **`member_interaction_history`** - Historical member records:
   - One record per completed call
   - Interaction date, topic, sentiment
   - Call duration, compliance status
   - Used by `get_member_history()` UC function

4. **`daily_call_statistics`** - Daily aggregated statistics:
   - Total calls, active agents, unique members
   - Sentiment distribution, compliance rates
   - Intent and scenario distributions
   - Complexity breakdown

### Scheduled Batch Job

- **Job Name**: `art-callcenter-gold-layer-batch`
- **Schedule**: Runs hourly (configurable)
- **Pipeline**: `art-callcenter-gold-layer`
- **Purpose**: Process completed calls and generate analytics

### Deployment

1. **Deploy Gold Layer Pipeline**:
   ```bash
   python scripts/09_deploy_gold_layer_pipeline.py
   ```

2. **Create Scheduled Job**:
   ```bash
   python scripts/10_create_batch_job.py
   ```

3. **Monitor**: Check pipeline runs in Databricks UI under Workflows → Delta Live Tables

### Use Cases

- **Agent Performance Monitoring**: Track agent KPIs and identify training needs
- **Member History**: View complete interaction history for members
- **Call Analytics**: Analyze call patterns, sentiment trends, compliance rates
- **Reporting**: Generate daily/weekly/monthly reports from Gold layer tables
- **Historical Analysis**: Query historical data for trends and insights

## Knowledge Base

The system includes a comprehensive knowledge base with 20 ART-specific articles covering:
- Contribution limits and caps
- Withdrawal options (compassionate grounds, financial hardship)
- Insurance coverage and claims
- Investment options and performance
- Account management
- Fees and charges
- Retirement options
- Tax implications
- Complaints and dispute resolution
- And more...

### Populate Knowledge Base

```bash
# Populate with comprehensive ART articles
python scripts/populate_kb_articles.py
```

### KB Search Features

- **Vector Search**: Uses Databricks Vector Search for semantic similarity matching
- **SQL Fallback**: Falls back to keyword search if vector search unavailable
- **Suggested Questions**: Always provides 5 context-aware questions per call
  - Detects negative sentiment and prioritizes complaint/dispute questions
  - Context-aware suggestions based on call scenario and intent
  - Default questions if no context available
- **Performance**: ~2 seconds per vector search query

The knowledge base is searchable via the `search_knowledge_base()` UC function and integrated into both Dash and Streamlit dashboards.

## Dashboards

### Dash Dashboard (Primary - Port 8050)

Unified dashboard application with three main views:

1. **Agent Dashboard** (`http://localhost:8050/agent`):
   - Live transcript display
   - AI suggestions with response time
   - Member info tab
   - Knowledge base search with suggested questions
   - Compliance alerts
   - Call selection dropdown (24-hour window)

2. **Supervisor Dashboard** (`http://localhost:8050/supervisor`):
   - Real-time call monitoring
   - Escalation tracking with risk scores
   - Clickable tabs for filtering (All Calls, Negative Sentiment, Compliance Issues, Complaints)
   - Escalation cards arranged horizontally
   - Active call statistics

3. **Analytics Dashboard** (`http://localhost:8050/analytics`):
   - Overview: Key metrics and recent call summaries
   - Agent Performance: Top performers with charts
   - Call Summaries: Filterable by sentiment and compliance
   - Daily Statistics: Trends and aggregated metrics

**Running Dash Dashboard**:
```bash
cd app_dash
source ../venv/bin/activate
python app.py
```

### Streamlit Dashboards (Alternative)

1. **Agent Dashboard** (`http://localhost:8520`):
   - Same features as Dash agent dashboard
   - Streamlit implementation

2. **Analytics Dashboard** (`http://localhost:8521`):
   - Gold layer analytics visualization
   - Same features as Dash analytics dashboard

3. **Supervisor Dashboard** (`http://localhost:8522`):
   - Call monitoring and escalation management

**Running Streamlit Dashboards**:
```bash
# Agent Dashboard
streamlit run app/agent_dashboard.py --server.port 8520

# Analytics Dashboard
streamlit run app/analytics_dashboard.py --server.port 8521

# Supervisor Dashboard
streamlit run app/supervisor_dashboard.py --server.port 8522
```

### Dashboard Features

- **Real-time Data**: Queries Gold layer tables directly (5-minute cache for analytics)
- **Smart Refresh**: Only updates when data actually changes
- **Interactive Filters**: Filter by date range, sentiment, compliance status, and intent
- **Visualizations**: Charts for call volume, sentiment trends, and performance metrics
- **Agent Search**: Look up specific agent performance metrics
- **Summary Statistics**: Key metrics and KPIs at a glance

## Future Enhancements

- [ ] Connect to real Genesys Cloud API
- [x] Populate knowledge base with real ART policies ✅ (20 comprehensive KB articles)
- [ ] Add multi-language support
- [x] Add supervisor dashboard for call monitoring ✅ (Supervisor Dashboard implemented)
- [x] Add real-time dashboards for Gold layer analytics ✅ (Analytics Dashboard implemented)

## Demo Guide

For a complete demonstration of the system, see the [Demo Flow Guide](docs/DEMO_FLOW.md) which includes:
- End-to-end data flow from ingestion to dashboards
- Step-by-step walkthrough of all 3 dashboards
- SQL queries and scripts for each phase
- Troubleshooting tips

Quick reference: [Demo Quick Reference](docs/DEMO_QUICK_REFERENCE.md)

### Demo Flow Summary

1. **Data Ingestion** (2 min) - Show Zerobus/SQL ingestion into Bronze layer
2. **Silver Processing** (2 min) - Show DLT pipeline enrichment
3. **Live Agent Dashboard** (5 min) - Real-time AI assistance
4. **Supervisor Dashboard** (4 min) - Escalation monitoring
5. **Analytics Dashboard** (3 min) - Historical analytics

Total demo duration: 15-20 minutes

## License

MIT

## Contributors

- Pravin Varma (@pravinva)

## Support

For issues or questions, please open an issue on GitHub or contact the development team.
