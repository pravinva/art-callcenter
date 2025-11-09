# ART Live Agent Assist Dashboard

A real-time Streamlit dashboard for Australian Retirement Trust call center agents, providing AI-powered assistance during live calls.

## Features

- **3-Column Layout:**
  - **Live Transcript**: Real-time call transcript with sentiment analysis
  - **AI Assistant**: Context-aware suggestions, member info, and knowledge base search
  - **Compliance Alerts**: Real-time compliance monitoring and alerts

- **Australian Retirement Trust Branding:**
  - Professional blue color scheme (#0051FF)
  - ART logo integration
  - Clean, modern UI matching ART website design

## Prerequisites

1. **Environment Setup:**
   ```bash
   export DATABRICKS_TOKEN='your-databricks-token'
   ```

2. **Dependencies:**
   ```bash
   pip install streamlit databricks-sql-connector databricks-sdk pandas
   ```

3. **Data Requirements:**
   - DLT pipeline running and creating `enriched_transcripts` table
   - Active calls in the last 10 minutes

## Running the Dashboard

### Option 1: Direct Streamlit
```bash
cd /Users/pravin.varma/Documents/Demo/art-callcenter
streamlit run app/agent_dashboard.py --server.port 8520
```

### Option 2: Using Script
```bash
./run_dashboard.sh
```

The dashboard will be available at: `http://localhost:8520`

## Usage

1. **Select Active Call**: Choose a call from the sidebar (shows calls from last 10 minutes)
2. **View Transcript**: See real-time transcript with sentiment indicators
3. **Get AI Suggestions**: Click "Get AI Suggestion" for context-aware assistance
4. **Monitor Compliance**: View compliance alerts in the right column
5. **Auto-refresh**: Enable auto-refresh to update every 5 seconds

## Configuration

The dashboard uses settings from `config/config.py`:
- SQL Warehouse ID
- Catalog and Schema names
- UC Function names
- Table names

## Troubleshooting

### "No active calls" message
- Ensure DLT pipeline is running
- Check that `enriched_transcripts` table has recent data
- Verify SQL Warehouse is running

### "Agent not available"
- GenAI agent is optional for suggestions
- Member info and compliance alerts work independently
- Check `scripts/07_genai_agent.py` for agent setup

### Connection errors
- Verify `DATABRICKS_TOKEN` is set correctly
- Check SQL Warehouse is accessible
- Ensure Unity Catalog permissions are correct

## Architecture

```
┌─────────────────────────────────────────────────┐
│         ART Live Agent Assist Dashboard         │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────┐ │
│  │   Transcript │  │ AI Assistant │  │Alerts│ │
│  │              │  │              │  │      │ │
│  │ • Live text  │  │ • Suggestions│  │• Comp│ │
│  │ • Sentiment  │  │ • Member Info│  │• Crit│ │
│  │ • Intents    │  │ • KB Search  │  │• High│ │
│  └──────────────┘  └──────────────┘  └──────┘ │
│                                                 │
└─────────────────────────────────────────────────┘
         │                    │              │
         ▼                    ▼              ▼
    enriched_transcripts  UC Functions  GenAI Agent
```

## Next Steps

- Deploy as Databricks App for production access
- Add real-time WebSocket updates for instant transcript refresh
- Integrate with call routing system for automatic call selection
- Add agent performance metrics and analytics

