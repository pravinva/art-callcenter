# Phase 4: GenAI Agent Development

## Overview

Phase 4 involves building the GenAI Agent that will assist call center agents during live calls. The agent uses UC Functions as tools to access real-time call data, knowledge base, and compliance information.

## Components

### 1. Agent Script (`scripts/07_genai_agent.py`)
- Creates ChatAgent using Databricks Agent Framework or LangChain fallback
- Integrates 4 UC Functions as tools
- Logs agent to MLflow for deployment

### 2. System Prompt
Defines agent behavior:
- Role: Assist ART member service representatives
- Tools: 4 UC Functions (call context, KB search, compliance check, member history)
- Rules: Never guarantee returns, flag compliance issues, cite KB articles
- Format: Concise suggestions (2-3 sentences)

### 3. UC Functions Integration
The agent uses these functions as tools:
- `get_live_call_context(call_id)` - Get current call details
- `search_knowledge_base(query)` - Find KB articles
- `check_compliance_realtime(call_id)` - Check violations
- `get_member_history(member_id)` - Recent interactions

## Prerequisites

**IMPORTANT:** Before running Phase 4, ensure:

1. ✅ DLT pipeline has completed and created `enriched_transcripts` table
2. ✅ Run: `python scripts/create_uc_functions_with_enriched_table.py`
   - This creates `get_live_call_context` and `check_compliance_realtime`
3. ✅ All 4 UC Functions exist and are accessible

## Deployment Steps

### Step 1: Verify Prerequisites
```bash
# Check DLT pipeline status
python scripts/check_update_status.py

# Check UC Functions exist
python scripts/check_phase2_3_status.py

# Create remaining UC Functions (if needed)
python scripts/create_uc_functions_with_enriched_table.py
```

### Step 2: Test Agent Locally (Optional)
```bash
python scripts/test_agent_local.py
```

### Step 3: Deploy Agent
```bash
python scripts/07_genai_agent.py
```

This will:
1. Create the agent with UC Functions as tools
2. Log agent to MLflow (`member_analytics.call_center.live_agent_assist`)
3. Prepare for Model Serving deployment

### Step 4: Deploy to Model Serving
After logging to MLflow, deploy the agent as a serving endpoint:
- Use Databricks UI: Serving → Create Endpoint
- Or use SDK: `scripts/08_deploy_model_serving.py` (to be created)

## Testing

Test queries:
- "Help me with call CALL-12345"
- "What are the contribution caps?"
- "Check compliance for call CALL-12345"
- "Get member history for MEMBER-001"

## Next Phase

After Phase 4:
- Phase 5: Streamlit Dashboard (agent-facing interface)
- Phase 6: Deploy Streamlit as Databricks App

## Notes

- Agent uses `databricks-sonnet-4-5` LLM endpoint
- Falls back to LangChain if `databricks-agents` not available
- UC Functions must be accessible from the agent's execution context
- Model is logged to MLflow for versioning and deployment

