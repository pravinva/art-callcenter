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

### 5. **Streamlit Dashboard**
- **Location**: `app/agent_dashboard.py`
- **Port**: 8520
- **Features**:
  - Live transcript display with sentiment indicators
  - AI-generated suggestions
  - Member 360 view
  - Knowledge base search
  - Real-time compliance alerts
  - Call metrics (sentiment distribution, top intents)

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

6. **Run Streamlit Dashboard**:
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
│   ├── agent_dashboard.py      # Main Streamlit dashboard
│   └── README.md                # Dashboard documentation
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

The system has been optimized for speed:

- **SQL Timeouts**: Reduced from 30s to 10s
- **Polling Frequency**: Increased from 0.5s to 0.2s
- **Response Caching**: 30-second cache for AI suggestions
- **LLM Settings**: `max_tokens=500`, `timeout=15s`
- **Agent Prompt**: Optimized to use only necessary tools

**Typical Response Times**:
- Cached AI suggestion: <0.1s
- Fresh AI suggestion: 5-10s
- Compliance alert update: <5s (DLT processing)
- Transcript update: Real-time (as data arrives)

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
3. **Member History Stub**: Member history returns sample data (requires `member_data.interaction_history` table)
4. **Streamlit Single-Threaded**: UI may briefly freeze during AI processing (mitigated with placeholders)

## Future Enhancements

- [ ] Connect to real Genesys Cloud API
- [ ] Populate knowledge base with real ART policies
- [ ] Integrate member history from CRM system
- [ ] Add multi-language support
- [ ] Implement agent performance analytics
- [ ] Add supervisor dashboard for call monitoring

## License

MIT

## Contributors

- Pravin Varma (@pravinva)

## Support

For issues or questions, please open an issue on GitHub or contact the development team.
