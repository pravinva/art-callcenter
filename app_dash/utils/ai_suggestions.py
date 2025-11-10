"""
AI Suggestion Data Fetching Utilities
"""
import time
from typing import Optional, Dict, Tuple
from pathlib import Path
import sys
from app_dash.utils.data_fetchers import get_live_transcript

# Add parent directory to path for agent import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Cache for AI suggestions
_suggestion_cache = {}
_cache_timestamps = {}
_agent_cache = None

def get_agent():
    """Get GenAI agent - cached singleton"""
    global _agent_cache
    if _agent_cache is not None:
        return _agent_cache
    
    try:
        # Import agent creation function directly
        import importlib.util
        agent_script_path = Path(__file__).parent.parent.parent / "scripts" / "07_genai_agent.py"
        
        if not agent_script_path.exists():
            print(f"Agent script not found: {agent_script_path}")
            return None
        
        spec = importlib.util.spec_from_file_location("genai_agent", agent_script_path)
        genai_agent_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(genai_agent_module)
        
        # Get the create_agent function
        if hasattr(genai_agent_module, 'create_agent'):
            _agent_cache = genai_agent_module.create_agent()
            return _agent_cache
        else:
            print("create_agent function not found in agent script")
            return None
            
    except Exception as e:
        print(f"Agent not available: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_heuristic_suggestion(call_id: str) -> Optional[str]:
    """Get instant heuristic suggestion based on call context (no LLM call)"""
    try:
        transcript_df = get_live_transcript(call_id)
        if transcript_df is None or transcript_df.empty:
            return None
        
        if len(transcript_df) > 0:
            latest_intent = transcript_df['intent_category'].iloc[-1] if 'intent_category' in transcript_df.columns else None
            latest_sentiment = transcript_df['sentiment'].iloc[-1] if 'sentiment' in transcript_df.columns else None
            
            # Simple instant suggestions for common intents (no LLM call needed)
            if latest_intent == 'contribution_inquiry':
                return "Member asking about contributions. Suggested: 'The concessional cap is $30,000 for 2024-25. Would you like details on catch-up contributions?'"
            elif latest_intent == 'withdrawal_inquiry':
                return "Member asking about withdrawals. Suggested: 'I can help with withdrawal options. Are you looking for early access or regular withdrawal?'"
            elif latest_sentiment == 'negative':
                return "Member showing negative sentiment. Suggested: 'I understand your concern. Let me help resolve this for you. What specific issue can I address?'"
    except Exception as e:
        print(f"Error getting heuristic suggestion: {e}")
    return None

def get_ai_suggestion_async(call_id: str, use_heuristic: bool = True) -> Tuple[Optional[str], float, Dict]:
    """
    Get AI suggestion for call - returns (suggestion, response_time, timing_breakdown)
    Now includes full LLM integration
    """
    start_time = time.time()
    timing_breakdown = {}
    
    # Check cache first (30 second cache)
    cache_key = f'ai_suggestion_{call_id}'
    if cache_key in _suggestion_cache:
        cached_result, cached_time = _suggestion_cache[cache_key]
        if time.time() - cached_time < 30:
            elapsed = time.time() - start_time
            timing_breakdown['cache_lookup'] = elapsed
            timing_breakdown['total'] = elapsed
            return cached_result, elapsed, timing_breakdown
    
    # Get heuristic suggestion first (instant)
    if use_heuristic:
        heuristic_start = time.time()
        heuristic = get_heuristic_suggestion(call_id)
        timing_breakdown['heuristic'] = time.time() - heuristic_start
        if heuristic:
            elapsed = time.time() - start_time
            timing_breakdown['total'] = elapsed
            _suggestion_cache[cache_key] = (heuristic, time.time())
            return heuristic, elapsed, timing_breakdown
    
    # Fall through to LLM-based suggestion
    agent_start = time.time()
    agent = get_agent()
    timing_breakdown['agent_init'] = time.time() - agent_start
    if not agent:
        elapsed_time = time.time() - start_time
        timing_breakdown['total'] = elapsed_time
        return "Agent not available. Please check configuration.", elapsed_time, timing_breakdown
    
    try:
        # Optimized prompt - supportive and helpful tone, very concise, directs agent to use minimum tools
        prompt = f"""Help me assist with call {call_id}. 

IMPORTANT: Call get_live_call_context FIRST - it has all the info you need (member info, transcript, sentiment, intent).
Only use other tools if absolutely necessary.

Provide:
- Brief context (1 sentence from get_live_call_context)
- Suggested response (1-2 sentences)
- Compliance warnings if any

Be helpful and supportive. Be FAST - use minimum tools."""
        
        # Measure LLM synthesis time separately
        llm_start = time.time()
        result = agent.invoke({
            'messages': [{
                'role': 'user',
                'content': prompt
            }]
        })
        timing_breakdown['llm_synthesis'] = time.time() - llm_start
        
        # Measure response extraction time
        extract_start = time.time()
        if isinstance(result, dict) and 'messages' in result:
            last_message = result['messages'][-1]
            response = last_message.content
        else:
            response = str(result)
        timing_breakdown['response_extraction'] = time.time() - extract_start
        
        elapsed_time = time.time() - start_time
        timing_breakdown['total'] = elapsed_time
        
        # Cache the result
        _suggestion_cache[cache_key] = (response, time.time())
        return response, elapsed_time, timing_breakdown
    except Exception as e:
        elapsed_time = time.time() - start_time
        timing_breakdown['total'] = elapsed_time
        timing_breakdown['error'] = str(e)
        return f"Error getting suggestion: {e}", elapsed_time, timing_breakdown

