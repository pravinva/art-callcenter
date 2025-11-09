#!/usr/bin/env python3
"""
Phase 4: Test GenAI Agent Locally
Test the agent before deploying to MLflow/Model Serving.

Run: python scripts/test_agent_local.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from the actual script file
import importlib.util
spec = importlib.util.spec_from_file_location("genai_agent", "scripts/07_genai_agent.py")
genai_agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(genai_agent)

create_agent = genai_agent.create_agent
SYSTEM_PROMPT = genai_agent.SYSTEM_PROMPT

def test_agent():
    """Test the agent with sample queries"""
    print("🧪 Testing GenAI Agent Locally")
    print("="*80)
    
    # Create agent
    agent = create_agent()
    
    if not agent:
        print("\n❌ Could not create agent")
        return
    
    print("\n✅ Agent created successfully")
    print("\n📋 Test Queries:")
    print("="*80)
    
    # Test queries
    test_queries = [
        "Help me with call CALL-20251109212956-57811",
        "What are the contribution caps for 2024-25?",
        "Check compliance for call CALL-20251109212956-57811",
        "Get member history for MEMBER-001"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        print("-" * 80)
        
        try:
            # Invoke agent
            if hasattr(agent, 'invoke'):
                # LangGraph agent
                response = agent.invoke({
                    "messages": [{"role": "user", "content": query}]
                })
                if isinstance(response, dict) and "messages" in response:
                    last_message = response["messages"][-1]
                    print(f"✅ Response: {last_message.content}")
                else:
                    print(f"✅ Response: {response}")
            elif hasattr(agent, 'run'):
                # ChatAgent
                response = agent.run(query)
                print(f"✅ Response: {response}")
            else:
                print("⚠️  Unknown agent type")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("✅ Testing Complete!")

if __name__ == "__main__":
    test_agent()

