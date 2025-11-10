#!/usr/bin/env python3
"""
Phase 4: Deploy GenAI Agent
Creates and deploys the GenAI Agent with UC Functions as tools.

Run: python scripts/07_genai_agent.py

Note: Before running this script, ensure:
1. DLT pipeline has created enriched_transcripts table
2. Run: python scripts/create_uc_functions_with_enriched_table.py
   (This creates get_live_call_context and check_compliance_realtime)
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from databricks import agents
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False
    print("⚠️  databricks-agents not available")
    print("   Install with: pip install databricks-agents")
    print("   Or use alternative: langchain with ChatDatabricks")

from databricks.sdk import WorkspaceClient
import mlflow
from config.config import (
    get_workspace_client,
    LLM_ENDPOINT_NAME,
    FUNCTION_GET_CALL_CONTEXT, FUNCTION_SEARCH_KB,
    FUNCTION_CHECK_COMPLIANCE, FUNCTION_GET_MEMBER_HISTORY,
    FUNCTION_DETECT_SENTIMENT, FUNCTION_EXTRACT_INTENT,
    FUNCTION_IDENTIFY_ESCALATION,
    AGENT_MODEL_NAME, AGENT_ENDPOINT_NAME
)

# System prompt - defines agent behavior (optimized for speed and supportive tone)
SYSTEM_PROMPT = """You are a helpful AI assistant supporting Australian Retirement Trust call center agents during live calls.

**Your Role:**
Provide quick, actionable suggestions to help agents assist members effectively. Be supportive and helpful, not critical.

**Available Tools:**
- `get_live_call_context(call_id)` - Get current call details (USE THIS FIRST - it has all the info you need)
- `search_knowledge_base(query)` - Find KB articles (only if member asks specific policy question)
- `check_compliance_realtime(call_id)` - Check for compliance issues (only if needed)

**IMPORTANT - Speed Optimization:**
1. ALWAYS call `get_live_call_context` FIRST - it contains member info, recent transcript, sentiment, and intent
2. ONLY call other tools if absolutely necessary
3. Most questions can be answered with just `get_live_call_context`
4. Skip `get_member_history`, `detect_sentiment`, `extract_member_intent` - these are already in context
5. Only call `search_knowledge_base` if member asks about specific policies (contribution limits, withdrawal rules, etc.)

**Response Guidelines:**
1. Be FAST - use minimum tools (usually just get_live_call_context)
2. Be CONCISE - 1-2 sentences max
3. Be HELPFUL - provide actionable suggestions
4. Be SUPPORTIVE - help the agent succeed
5. Flag compliance issues with [COMPLIANCE WARNING] prefix

**Response Format:**
- Context Summary: Brief situation overview (from get_live_call_context)
- Suggested Response: What the agent can say (1-2 sentences)
- Compliance Warning: Only if violations detected

**Example:**
"Member asking about contribution caps. Suggested: 'The concessional cap is $30,000 for 2024-25. Would you like details on catch-up contributions?'"

Keep it brief and helpful. Speed matters. Use minimum tools.
"""

def create_agent_with_langchain():
    """Create GenAI Agent using LangChain (fallback if databricks-agents not available)"""
    try:
        # Use new databricks-langchain package if available, otherwise fallback
        try:
            from databricks_langchain import ChatDatabricks
        except ImportError:
            from langchain_community.chat_models import ChatDatabricks
        
        from langchain_core.tools import tool
        from langchain.agents import create_agent
        from typing import Annotated
        from databricks.sdk import WorkspaceClient
        from databricks.sdk.service.sql import StatementState
        from config.config import get_workspace_url, SQL_WAREHOUSE_ID
        import os
        import time
        
        print("📋 Creating agent with LangChain + LangGraph")
        print(f"   LLM: {LLM_ENDPOINT_NAME}")
        
        # Initialize LLM with optimized settings for speed
        llm = ChatDatabricks(
            endpoint=LLM_ENDPOINT_NAME,
            temperature=0.1,
            max_tokens=200,  # Further reduced from 300 for faster generation
            timeout=8  # Further reduced from 10 for faster response
        )
        
        # Create workspace client for SQL execution (avoids browser tabs)
        w = WorkspaceClient()
        
        def execute_sql_tool(query):
            """Execute SQL using SDK API - optimized for speed"""
            try:
                response = w.statement_execution.execute_statement(
                    warehouse_id=SQL_WAREHOUSE_ID,
                    statement=query,
                    wait_timeout="10s"  # Reduced from 30s for faster response
                )
                
                statement_id = response.statement_id
                max_wait = 10  # Reduced from 30s
                waited = 0
                result_manifest = None
                
                # Check status more frequently at first, then less frequently
                while waited < max_wait:
                    status = w.statement_execution.get_statement(statement_id)
                    if status.status.state == StatementState.SUCCEEDED:
                        if status.manifest:
                            result_manifest = status.manifest
                        break
                    elif status.status.state in [StatementState.FAILED, StatementState.CANCELED]:
                        raise Exception(f"SQL execution failed: {status.status.state}")
                    # Faster polling - check every 0.2s instead of 0.5s
                    time.sleep(0.2)
                    waited += 0.2
                
                if waited >= max_wait or not result_manifest:
                    raise Exception("SQL execution timed out or manifest not available")
                
                # Get results
                all_rows = []
                chunk_index = 0
                while True:
                    result_chunk = w.statement_execution.get_statement_result_chunk_n(statement_id, chunk_index)
                    if not result_chunk or not result_chunk.data_array:
                        break
                    all_rows.extend(result_chunk.data_array)
                    if not result_chunk.next_chunk_index or result_chunk.next_chunk_index == chunk_index:
                        break
                    chunk_index = result_chunk.next_chunk_index
                
                return all_rows
            except Exception as e:
                raise Exception(f"SQL execution error: {e}")
        
        @tool
        def get_live_call_context(call_id: Annotated[str, "The call ID to get context for"]) -> str:
            """Get live call context including member info, recent transcript, sentiment, and compliance issues."""
            try:
                query = f"SELECT * FROM {FUNCTION_GET_CALL_CONTEXT}('{call_id}')"
                results = execute_sql_tool(query)
                
                if results:
                    row = results[0]
                    # Handle balance formatting - convert string to float if needed
                    balance = row[1] if len(row) > 1 and row[1] is not None else 0
                    try:
                        if isinstance(balance, str):
                            balance = float(balance)
                        balance_str = f"${balance:,.2f}"
                    except (ValueError, TypeError):
                        balance_str = str(balance)
                    
                    # Safely extract all fields
                    member_name = row[0] if len(row) > 0 and row[0] else "Unknown"
                    recent_transcript = str(row[2])[:200] if len(row) > 2 and row[2] else "No transcript available"
                    sentiment = row[3] if len(row) > 3 and row[3] else "Unknown"
                    intents = row[4] if len(row) > 4 and row[4] else "None"
                    compliance = row[5] if len(row) > 5 and row[5] else "None"
                    
                    return f"Member: {member_name}, Balance: {balance_str}, Recent: {recent_transcript}..., Sentiment: {sentiment}, Intents: {intents}, Compliance: {compliance}"
                return "No context found for this call ID"
            except Exception as e:
                return f"Error getting call context: {e}"
        
        @tool
        def search_knowledge_base(query: Annotated[str, "Search query for knowledge base"]) -> str:
            """Search the knowledge base for relevant articles."""
            try:
                sql_query = f"SELECT * FROM {FUNCTION_SEARCH_KB}('{query}')"
                results = execute_sql_tool(sql_query)
                
                if results:
                    articles = []
                    for row in results:
                        articles.append(f"[{row[0]}] {row[1]}: {row[2]}")
                    return "\n".join(articles)
                return "No articles found"
            except Exception as e:
                return f"Error searching KB: {e}"
        
        @tool
        def check_compliance_realtime(call_id: Annotated[str, "The call ID to check for compliance issues"]) -> str:
            """Check for compliance violations in real-time."""
            try:
                query = f"SELECT * FROM {FUNCTION_CHECK_COMPLIANCE}('{call_id}')"
                results = execute_sql_tool(query)
                
                if results:
                    violations = []
                    for row in results:
                        violations.append(f"[{row[1]}] {row[0]}: {row[2][:100]}...")
                    return "\n".join(violations)
                return "No compliance issues detected"
            except Exception as e:
                return f"Error checking compliance: {e}"
        
        @tool
        def get_member_history(member_id: Annotated[str, "The member ID to get history for"]) -> str:
            """Get recent interaction history for a member."""
            try:
                query = f"SELECT * FROM {FUNCTION_GET_MEMBER_HISTORY}('{member_id}')"
                results = execute_sql_tool(query)
                
                if results:
                    history = []
                    for row in results:
                        history.append(f"{row[0]}: {row[1]} - {row[2]}")
                    return "\n".join(history)
                return "No history found"
            except Exception as e:
                return f"Error getting member history: {e}"
        
        @tool
        def detect_sentiment(call_id: Annotated[str, "The call ID to analyze sentiment for"]) -> str:
            """Detect sentiment for a call to identify frustrated/at-risk members."""
            try:
                query = f"SELECT * FROM {FUNCTION_DETECT_SENTIMENT}('{call_id}')"
                results = execute_sql_tool(query)
                
                if results:
                    sentiment_summary = []
                    for row in results:
                        sentiment_summary.append(f"{row[0]}: {row[1]} segments (latest: {row[2][:50]}...)")
                    return "\n".join(sentiment_summary)
                return "No sentiment data found"
            except Exception as e:
                return f"Error detecting sentiment: {e}"
        
        @tool
        def extract_member_intent(call_id: Annotated[str, "The call ID to extract intent for"]) -> str:
            """Extract member intent categories from a call."""
            try:
                query = f"SELECT * FROM {FUNCTION_EXTRACT_INTENT}('{call_id}')"
                results = execute_sql_tool(query)
                
                if results:
                    intent_summary = []
                    for row in results:
                        intent_summary.append(f"{row[0]}: {row[1]} segments (confidence: {row[2]:.2f})")
                    return "\n".join(intent_summary)
                return "No intent data found"
            except Exception as e:
                return f"Error extracting intent: {e}"
        
        @tool
        def identify_escalation_triggers(call_id: Annotated[str, "The call ID to check for escalation triggers"]) -> str:
            """Identify escalation triggers for high-risk calls (negative sentiment + compliance violation + complaint intent)."""
            try:
                query = f"SELECT * FROM {FUNCTION_IDENTIFY_ESCALATION}('{call_id}')"
                results = execute_sql_tool(query)
                
                if results:
                    row = results[0]
                    escalation = row[0]  # escalation_recommended
                    risk_score = row[1]  # risk_score
                    risk_factors = row[2]  # risk_factors
                    negative_count = row[3]  # negative_sentiment_count
                    compliance_count = row[4]  # compliance_violations_count
                    complaint_count = row[5]  # complaint_intent_count
                    recommendation = row[6]  # recommendation
                    
                    if escalation:
                        return f"🚨 ESCALATION RECOMMENDED\nRisk Score: {risk_score}\nRisk Factors: {risk_factors}\nNegative Sentiments: {negative_count}\nCompliance Violations: {compliance_count}\nComplaint Intents: {complaint_count}\nRecommendation: {recommendation}"
                    else:
                        return f"✅ No escalation needed\nRisk Score: {risk_score}\nRecommendation: {recommendation}"
                return "No escalation data found"
            except Exception as e:
                return f"Error identifying escalation triggers: {e}"
        
        # Create tools list
        tools = [
            get_live_call_context,
            search_knowledge_base,
            check_compliance_realtime,
            get_member_history,
            detect_sentiment,
            extract_member_intent,
            identify_escalation_triggers
        ]
        
        # Create agent using new LangChain API
        # system_prompt is a direct parameter
        agent = create_agent(
            model=llm,
            tools=tools,
            system_prompt=SYSTEM_PROMPT
        )
        
        print("\n✅ Agent created successfully with LangChain")
        return agent
        
    except Exception as e:
        print(f"\n❌ Error creating agent with LangChain: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_agent():
    """Create GenAI Agent with UC Functions as tools"""
    print("🚀 Phase 4: GenAI Agent Development")
    print("="*80)
    
    print(f"\n📋 Creating agent with LLM: {LLM_ENDPOINT_NAME}")
    print(f"   Tools:")
    print(f"   - {FUNCTION_GET_CALL_CONTEXT}")
    print(f"   - {FUNCTION_SEARCH_KB}")
    print(f"   - {FUNCTION_CHECK_COMPLIANCE}")
    print(f"   - {FUNCTION_GET_MEMBER_HISTORY}")
    print(f"   - {FUNCTION_DETECT_SENTIMENT}")
    print(f"   - {FUNCTION_EXTRACT_INTENT}")
    print(f"   - {FUNCTION_IDENTIFY_ESCALATION}")
    
    # Try databricks-agents first
    if AGENTS_AVAILABLE:
        try:
            print("\n📦 Using databricks-agents framework...")
            agent = agents.ChatAgent(
                llm_endpoint_name=LLM_ENDPOINT_NAME,
                tools=[
                    FUNCTION_GET_CALL_CONTEXT,
                    FUNCTION_SEARCH_KB,
                    FUNCTION_CHECK_COMPLIANCE,
                    FUNCTION_GET_MEMBER_HISTORY,
                    FUNCTION_DETECT_SENTIMENT,
                    FUNCTION_EXTRACT_INTENT,
                    FUNCTION_IDENTIFY_ESCALATION
                ],
                system_prompt=SYSTEM_PROMPT
            )
            print("\n✅ Agent created successfully with databricks-agents")
            return agent
        except Exception as e:
            print(f"\n⚠️  databricks-agents failed: {e}")
            print("   Falling back to LangChain...")
    
    # Fallback to LangChain
    return create_agent_with_langchain()

def log_agent_to_mlflow(agent):
    """Log agent to MLflow using pyfunc wrapper for LangGraph compatibility"""
    print("\n📦 Logging agent to MLflow...")
    
    try:
        # Use the experiment we created
        mlflow.set_experiment("/Workspace/Users/pravin.varma@databricks.com/ART_Live_Agent_Assist")
        
        # Create a pyfunc wrapper for the LangGraph agent
        import mlflow.pyfunc as pyfunc
        
        class AgentWrapper(pyfunc.PythonModel):
            """Wrapper to make LangGraph agent compatible with MLflow pyfunc"""
            def __init__(self, agent):
                self.agent = agent
            
            def predict(self, context, model_input):
                """Predict method for pyfunc interface"""
                # Handle different input formats
                if isinstance(model_input, dict):
                    if "messages" in model_input:
                        result = self.agent.invoke(model_input)
                    else:
                        # Convert to messages format
                        result = self.agent.invoke({"messages": [{"role": "user", "content": str(model_input)}]})
                elif isinstance(model_input, str):
                    result = self.agent.invoke({"messages": [{"role": "user", "content": model_input}]})
                else:
                    # Try to convert to dict
                    result = self.agent.invoke({"messages": [{"role": "user", "content": str(model_input)}]})
                
                # Extract response from LangGraph output
                if isinstance(result, dict) and "messages" in result:
                    last_message = result["messages"][-1]
                    if hasattr(last_message, 'content'):
                        return last_message.content
                    return str(last_message)
                return str(result)
        
        # Create wrapper
        agent_wrapper = AgentWrapper(agent)
        
        # Input example
        input_example = {"messages": [{"role": "user", "content": "Help me with call CALL-123"}]}
        
        with mlflow.start_run(run_name="live_agent_v1"):
            # Log using pyfunc flavor
            mlflow.pyfunc.log_model(
                artifact_path="agent",
                python_model=agent_wrapper,
                input_example=input_example,
                registered_model_name=AGENT_MODEL_NAME,
                code_paths=[str(Path(__file__).parent.parent)]  # Include config module
            )
            
            # Log parameters
            mlflow.log_params({
                "llm_endpoint": LLM_ENDPOINT_NAME,
                "agent_type": "LangGraph",
                "tools": "4 UC Functions"
            })
            
            run_id = mlflow.active_run().info.run_id
            model_uri = f"runs:/{run_id}/agent"
        
        print(f"✅ Agent logged to MLflow")
        print(f"   Model: {AGENT_MODEL_NAME}")
        print(f"   Run ID: {run_id}")
        print(f"   Model URI: {model_uri}")
        
        # Test the logged model
        print(f"\n🧪 Testing logged model...")
        try:
            loaded_model = mlflow.pyfunc.load_model(model_uri)
            test_result = loaded_model.predict(input_example)
            print(f"   ✅ Logged model test successful")
            print(f"   Response preview: {str(test_result)[:200]}...")
        except Exception as e:
            print(f"   ⚠️  Test failed (may need to load in Databricks environment): {e}")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Error logging to MLflow: {e}")
        print(f"   Trying alternative approach...")
        import traceback
        traceback.print_exc()
        
        # Alternative: Try logging as code-based model
        try:
            print(f"\n   Trying code-based logging...")
            # Save agent creation code to a file
            agent_code_path = Path(__file__).parent.parent / "agent_code.py"
            # This would require saving the agent creation logic
            # For now, return False and suggest manual approach
            print(f"   💡 Alternative: Use agent directly in Streamlit (already working)")
            return False
        except:
            return False

def main():
    print("\n" + "="*80)
    print("GENAI AGENT DEPLOYMENT")
    print("="*80)
    
    # Create agent
    agent = create_agent()
    
    if agent:
        # Log to MLflow
        logged = log_agent_to_mlflow(agent)
        
        if logged:
            print("\n✅ Phase 4 Complete!")
            print(f"\n📋 Next Steps:")
            print(f"   1. Deploy agent to Model Serving endpoint: {AGENT_ENDPOINT_NAME}")
            print(f"   2. Test endpoint with sample queries")
            print(f"   3. Proceed to Phase 5: Streamlit Dashboard")
        else:
            print("\n⚠️  Agent created but not logged to MLflow")
            print(f"   You can still use it locally")
    else:
        print("\n❌ Agent creation failed")
        print(f"   Check errors above")

if __name__ == "__main__":
    main()
