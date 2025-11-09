#!/usr/bin/env python3
"""
Phase 3: GenAI Agent Development
Build ChatAgent with system prompt and tool integration using Agent Framework.

Run: python scripts/07_genai_agent.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks import agents
from databricks.sdk import WorkspaceClient
from config.config import (
    get_workspace_client,
    LLM_ENDPOINT_NAME,
    FUNCTION_GET_CALL_CONTEXT, FUNCTION_SEARCH_KB,
    FUNCTION_CHECK_COMPLIANCE, FUNCTION_GET_MEMBER_HISTORY,
    AGENT_MODEL_NAME, AGENT_ENDPOINT_NAME
)

# System prompt - defines agent behavior
SYSTEM_PROMPT = """You are an AI assistant helping Australian Retirement Trust (ART) member service representatives during LIVE phone calls.

**Your Role:**
You have access to real-time call transcripts via Online Tables and can provide instant assistance to agents by:
1. Analyzing the current conversation context
2. Suggesting appropriate responses based on the knowledge base
3. Flagging compliance issues immediately
4. Providing relevant member information

**Available Tools:**
- `get_live_call_context(call_id)` - Get current call details from Online Tables
- `search_knowledge_base(query)` - Find relevant KB articles
- `check_compliance_realtime(call_id)` - Check for violations
- `get_member_history(member_id)` - Recent member interactions

**Critical Rules:**
1. NEVER guarantee investment returns or performance
2. NEVER provide personal financial advice (general information only)
3. ALWAYS flag compliance issues with [COMPLIANCE WARNING] prefix
4. Keep suggestions concise (2-3 sentences max)
5. Cite KB article IDs when providing policy information

**Response Format:**
When asked to assist with a call:
1. Call get_live_call_context() to understand the situation
2. Check for compliance issues
3. Search KB if needed for accurate information
4. Provide a suggested response the agent can use

**Example Output:**
"Member is asking about contribution caps. [KB-002 reference] Suggested response: 'The concessional contribution cap for 2024-25 is $30,000. This includes employer and any salary sacrifice contributions. Would you like information about catch-up contributions?'"

Remember: You're assisting the human agent, not replacing them. Provide helpful suggestions, they make final decisions.
"""

def create_agent():
    """Create GenAI Agent with UC Functions as tools"""
    print("🚀 Phase 3: GenAI Agent Development")
    print("="*80)
    
    print(f"\n📋 Creating agent with LLM: {LLM_ENDPOINT_NAME}")
    print(f"   Tools:")
    print(f"   - {FUNCTION_GET_CALL_CONTEXT}")
    print(f"   - {FUNCTION_SEARCH_KB}")
    print(f"   - {FUNCTION_CHECK_COMPLIANCE}")
    print(f"   - {FUNCTION_GET_MEMBER_HISTORY}")
    
    # Create Agent
    agent = agents.ChatAgent(
        llm_endpoint_name=LLM_ENDPOINT_NAME,  # Databricks Sonnet 4-5
        tools=[
            FUNCTION_GET_CALL_CONTEXT,
            FUNCTION_SEARCH_KB,
            FUNCTION_CHECK_COMPLIANCE,
            FUNCTION_GET_MEMBER_HISTORY
        ],
        system_prompt=SYSTEM_PROMPT
    )
    
    print("\n✅ Agent created successfully")
    
    # Test the agent
    print("\n🧪 Testing agent...")
    test_query = {
        "messages": [{
            "role": "user",
            "content": "I'm on a call where the member is asking about early withdrawal for medical treatment. Call ID: CALL-20251109-12345. What should I tell them?"
        }]
    }
    
    try:
        response = agent.invoke(test_query)
        print("Agent Response:")
        print(response['content'])
        print("\n✅ Agent test successful")
    except Exception as e:
        print(f"⚠️  Agent test failed (this is expected if UC Functions don't exist yet): {e}")
        print("   Create UC Functions first, then test again")
    
    return agent

def log_agent_to_mlflow(agent):
    """Log agent to MLflow"""
    import mlflow
    
    print("\n📦 Logging agent to MLflow...")
    
    mlflow.set_experiment("/Shared/ART_Live_Agent_Assist")
    
    with mlflow.start_run(run_name="live_agent_v1"):
        logged_agent = mlflow.langchain.log_model(
            lc_model=agent,
            artifact_path="agent",
            input_example={
                "messages": [{
                    "role": "user",
                    "content": "Help me with call CALL-12345"
                }]
            },
            registered_model_name=AGENT_MODEL_NAME
        )
    
    print(f"✅ Agent logged to MLflow")
    print(f"   Model: {AGENT_MODEL_NAME}")

def main():
    try:
        agent = create_agent()
        
        # Log to MLflow
        log_agent_to_mlflow(agent)
        
        print("\n✅ Phase 3 Complete!")
        print("   Next: Deploy agent to Model Serving endpoint")
        print(f"   Endpoint name: {AGENT_ENDPOINT_NAME}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

