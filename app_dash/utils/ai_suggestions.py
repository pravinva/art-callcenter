"""
AI Suggestion Data Fetching Utilities
"""
import time
from typing import Optional, Dict, Tuple
from app_dash.utils.data_fetchers import get_live_transcript

# Cache for AI suggestions
_suggestion_cache = {}
_cache_timestamps = {}

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
    This is a placeholder - actual LLM integration will be added
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
    
    # TODO: Add LLM-based suggestion here
    # For now, return a placeholder
    elapsed_time = time.time() - start_time
    timing_breakdown['total'] = elapsed_time
    
    placeholder = f"AI suggestion for call {call_id[-8:]}. LLM integration pending."
    _suggestion_cache[cache_key] = (placeholder, time.time())
    
    return placeholder, elapsed_time, timing_breakdown

