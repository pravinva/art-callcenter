"""
Knowledge Base Utilities for Dash App
"""
from typing import List, Optional
from app_dash.utils.data_fetchers import get_live_transcript
from app_dash.utils.databricks_client import execute_sql
from config.config import (
    ENRICHED_TABLE, SQL_WAREHOUSE_ID,
    FUNCTION_SEARCH_KB, VECTOR_SEARCH_ENDPOINT, KB_INDEX_NAME
)

def get_suggested_kb_questions(call_id: str) -> List[str]:
    """Get suggested KB questions based on call context - always returns at least 5 questions"""
    try:
        # Get call context to understand scenario, intent, and sentiment
        query = f"""
        SELECT DISTINCT 
            scenario,
            intent_category,
            sentiment,
            COUNT(*) as count
        FROM {ENRICHED_TABLE}
        WHERE call_id = '{call_id}'
        GROUP BY scenario, intent_category, sentiment
        ORDER BY count DESC
        LIMIT 10
        """
        results = execute_sql(query, SQL_WAREHOUSE_ID, return_dataframe=True)
        
        suggestions = []
        seen = set()
        has_negative_sentiment = False
        has_complaint = False
        
        # Process results if available
        if results is not None and not results.empty:
            for _, row in results.iterrows():
                scenario = str(row.get('scenario', '')).lower()
                intent = str(row.get('intent_category', '')).lower()
                sentiment = str(row.get('sentiment', '')).lower()
                
                # Check for negative sentiment
                if sentiment == 'negative':
                    has_negative_sentiment = True
                
                # Check for complaint intent
                if 'complaint' in intent or 'complaint' in scenario:
                    has_complaint = True
                
                # Scenario-based suggestions
                if 'withdrawal' in scenario or 'withdrawal' in intent:
                    suggestions.extend([
                        "What are the requirements for compassionate grounds withdrawal?",
                        "How do I apply for financial hardship withdrawal?",
                        "What is early access super?"
                    ])
                elif 'contribution' in scenario or 'contribution' in intent:
                    suggestions.extend([
                        "What are the contribution caps?",
                        "How do employer contributions work?",
                        "What are non-concessional contributions?"
                    ])
                elif 'insurance' in scenario or 'insurance' in intent:
                    suggestions.extend([
                        "What insurance coverage do I have?",
                        "How do I make an insurance claim?",
                        "What is TPD insurance?"
                    ])
                elif 'investment' in scenario or 'investment' in intent:
                    suggestions.extend([
                        "What investment options are available?",
                        "How is investment performance calculated?",
                        "How do I switch investments?"
                    ])
        
        # Add negative sentiment/complaint questions if detected (priority)
        if has_negative_sentiment or has_complaint:
            complaint_questions = [
                "What's the complaint process?",
                "What's the dispute resolution mechanism?",
                "How do I file a formal complaint?",
                "What are my rights if I'm not satisfied with service?",
                "How long does complaint resolution take?"
            ]
            for q in complaint_questions:
                if q not in seen:
                    suggestions.insert(0, q)  # Add at beginning for priority
                    seen.add(q)
        
        # Remove duplicates while preserving order
        unique_suggestions = []
        for s in suggestions:
            if s not in seen:
                seen.add(s)
                unique_suggestions.append(s)
        
        # ALWAYS ensure we have at least 5 questions - use defaults if needed
        default_questions = [
            "What are the contribution caps?",
            "How do I make a withdrawal?",
            "What insurance coverage do I have?",
            "How do I update my personal details?",
            "What are my investment options?",
            "What's the complaint process?",
            "What's the dispute resolution mechanism?",
            "How do I check my account balance?",
            "What are the superannuation rules?",
            "How do I change my investment strategy?"
        ]
        
        # Fill remaining slots with defaults if we don't have enough
        for default_q in default_questions:
            if len(unique_suggestions) >= 5:
                break
            if default_q not in seen:
                unique_suggestions.append(default_q)
                seen.add(default_q)
        
        # If still empty (shouldn't happen), return defaults
        if not unique_suggestions:
            unique_suggestions = default_questions[:5]
        
        return unique_suggestions[:5]  # Return top 5
        
    except Exception as e:
        print(f"Error getting suggested KB questions: {e}")
        # Always return default questions on error
        return [
            "What are the contribution caps?",
            "How do I make a withdrawal?",
            "What insurance coverage do I have?",
            "What's the complaint process?",
            "What are my investment options?"
        ]

def search_kb_vector_search(query: str, num_results: int = 5) -> List[dict]:
    """
    Search knowledge base using vector search (semantic similarity).
    Falls back to SQL function if vector search is not available.
    """
    import time
    start_time = time.time()
    
    try:
        # Try standard import first, then fallback to databricks-vectorsearch package
        try:
            from databricks.vector_search.client import VectorSearchClient
        except ImportError:
            from databricks_vectorsearch.client import VectorSearchClient
        
        # Initialize vector search client
        vsc = VectorSearchClient(disable_notice=True)
        
        # Get the vector search index
        try:
            index = vsc.get_index(
                endpoint_name=VECTOR_SEARCH_ENDPOINT,
                index_name=KB_INDEX_NAME
            )
        except Exception as e:
            # Index doesn't exist yet, fallback to SQL
            elapsed = time.time() - start_time
            print(f"⚠️ Vector search index not found (took {elapsed:.2f}s), falling back to SQL: {e}")
            return search_kb_sql_fallback(query)
        
        # Perform vector search
        search_start = time.time()
        results = index.similarity_search(
            query_text=query,
            columns=["article_id", "title", "content", "category"],
            num_results=num_results
        )
        search_elapsed = time.time() - search_start
        
        # Convert results to list of dicts
        articles = []
        if results and 'result' in results and 'data_array' in results['result']:
            for hit in results['result']['data_array']:
                articles.append({
                    'article_id': hit[0] if len(hit) > 0 else 'N/A',
                    'title': hit[1] if len(hit) > 1 else 'N/A',
                    'content': hit[2] if len(hit) > 2 else 'N/A',
                    'category': hit[3] if len(hit) > 3 else 'N/A'
                })
        
        total_elapsed = time.time() - start_time
        print(f"✅ Vector search completed: {len(articles)} results in {total_elapsed:.2f}s (search: {search_elapsed:.2f}s)")
        return articles
        
    except Exception as e:
        # Fallback to SQL keyword search if vector search fails
        elapsed = time.time() - start_time
        print(f"⚠️ Vector search failed (took {elapsed:.2f}s), falling back to SQL: {e}")
        import traceback
        traceback.print_exc()
        return search_kb_sql_fallback(query)

def search_kb_sql_fallback(query: str) -> List[dict]:
    """Fallback to SQL keyword search if vector search is not available"""
    import time
    start_time = time.time()
    
    try:
        query_sql = f"SELECT * FROM {FUNCTION_SEARCH_KB}('{query}')"
        articles_df = execute_sql(query_sql, SQL_WAREHOUSE_ID, return_dataframe=True)
        
        elapsed = time.time() - start_time
        
        if articles_df is not None and not articles_df.empty:
            print(f"✅ SQL search completed: {len(articles_df)} results in {elapsed:.2f}s")
            return articles_df.to_dict('records')
        else:
            print(f"⚠️ SQL search returned no results in {elapsed:.2f}s")
            return []
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Error in SQL KB search (took {elapsed:.2f}s): {e}")
        return []

