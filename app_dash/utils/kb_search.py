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
    """Get suggested KB questions based on call context"""
    try:
        # Get call context to understand scenario and intent
        query = f"""
        SELECT DISTINCT 
            scenario,
            intent_category,
            COUNT(*) as count
        FROM {ENRICHED_TABLE}
        WHERE call_id = '{call_id}'
        GROUP BY scenario, intent_category
        ORDER BY count DESC
        LIMIT 5
        """
        results = execute_sql(query, SQL_WAREHOUSE_ID, return_dataframe=True)
        
        if results is None or results.empty:
            return []
        
        # Map scenarios/intents to KB questions
        suggestions = []
        seen = set()
        
        for _, row in results.iterrows():
            scenario = str(row.get('scenario', '')).lower()
            intent = str(row.get('intent_category', '')).lower()
            
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
        
        # Remove duplicates while preserving order
        unique_suggestions = []
        for s in suggestions:
            if s not in seen:
                seen.add(s)
                unique_suggestions.append(s)
        
        return unique_suggestions[:5]  # Return top 5
        
    except Exception as e:
        print(f"Error getting suggested KB questions: {e}")
        return []

def search_kb_vector_search(query: str, num_results: int = 5) -> List[dict]:
    """
    Search knowledge base using vector search (semantic similarity).
    Falls back to SQL function if vector search is not available.
    """
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
            print(f"Vector search index not found, using keyword search: {e}")
            return search_kb_sql_fallback(query)
        
        # Perform vector search
        results = index.similarity_search(
            query_text=query,
            columns=["article_id", "title", "content", "category"],
            num_results=num_results
        )
        
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
        
        return articles
        
    except Exception as e:
        # Fallback to SQL keyword search if vector search fails
        print(f"Vector search failed, using keyword search: {e}")
        return search_kb_sql_fallback(query)

def search_kb_sql_fallback(query: str) -> List[dict]:
    """Fallback to SQL keyword search if vector search is not available"""
    try:
        query_sql = f"SELECT * FROM {FUNCTION_SEARCH_KB}('{query}')"
        articles_df = execute_sql(query_sql, SQL_WAREHOUSE_ID, return_dataframe=True)
        
        if articles_df is not None and not articles_df.empty:
            return articles_df.to_dict('records')
        else:
            return []
    except Exception as e:
        print(f"Error in SQL KB search: {e}")
        return []

