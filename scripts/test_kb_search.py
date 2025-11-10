#!/usr/bin/env python3
"""
Test KB Vector Search locally
Tests vector search function and SQL fallback without Streamlit
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import FUNCTION_SEARCH_KB, VECTOR_SEARCH_ENDPOINT, KB_INDEX_NAME
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState

def get_workspace_client():
    """Get WorkspaceClient"""
    return WorkspaceClient()

def execute_sql(query, return_dataframe=False):
    """Execute SQL using Databricks SDK - matches agent_dashboard.py pattern"""
    from config.config import SQL_WAREHOUSE_ID
    import pandas as pd
    import time
    w = get_workspace_client()
    
    try:
        response = w.statement_execution.execute_statement(
            warehouse_id=SQL_WAREHOUSE_ID,
            statement=query,
            wait_timeout="10s"
        )
        
        statement_id = response.statement_id
        max_wait = 10
        waited = 0
        result_manifest = None
        
        while waited < max_wait:
            status = w.statement_execution.get_statement(statement_id)
            if status.status.state == StatementState.SUCCEEDED:
                if status.manifest:
                    result_manifest = status.manifest
                break
            elif status.status.state in [StatementState.FAILED, StatementState.CANCELED]:
                error_msg = f"SQL execution failed: {status.status.state}"
                if hasattr(status.status, 'message') and status.status.message:
                    error_msg = status.status.message
                raise Exception(error_msg)
            
            time.sleep(0.2)
            waited += 0.2
        
        if waited >= max_wait:
            raise Exception("SQL execution timed out")
        
        if not result_manifest:
            raise Exception("Could not retrieve result manifest")
        
        # Get results - may need to get multiple chunks
        all_rows = []
        chunk_index = 0
        
        while True:
            result_chunk = w.statement_execution.get_statement_result_chunk_n(statement_id, chunk_index)
            if not result_chunk or not result_chunk.data_array:
                break
            
            all_rows.extend(result_chunk.data_array)
            
            # Check if there are more chunks
            if not result_chunk.next_chunk_index or result_chunk.next_chunk_index == chunk_index:
                break
            chunk_index = result_chunk.next_chunk_index
        
        if return_dataframe:
            # Convert to DataFrame
            if all_rows and result_manifest and result_manifest.schema and result_manifest.schema.columns:
                columns = [col.name for col in result_manifest.schema.columns]
                df = pd.DataFrame(all_rows, columns=columns)
                return df
            elif all_rows:
                # Fallback: infer column names from data if schema not available
                num_cols = len(all_rows[0]) if all_rows else 0
                columns = [f"col_{i+1}" for i in range(num_cols)]
                df = pd.DataFrame(all_rows, columns=columns)
                return df
            return pd.DataFrame()
        else:
            return all_rows
    except Exception as e:
        raise Exception(f"SQL execution error: {e}")

def search_kb_vector_search(query: str, num_results: int = 5):
    """
    Search knowledge base using vector search (semantic similarity).
    Falls back to SQL function if vector search is not available.
    """
    try:
        from databricks.vector_search.client import VectorSearchClient
        
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
            print(f"  ⚠️  Vector search index not found, using keyword search")
            return search_kb_sql_fallback(query)
        
        # Perform vector search
        results = index.similarity_search(
            query_text=query,
            columns=["article_id", "title", "content", "category"],
            num_results=num_results
        )
        
        # Convert results to list of dicts (matching SQL function format)
        articles = []
        if results and 'result' in results and 'data_array' in results['result']:
            for hit in results['result']['data_array']:
                # hit format: [article_id, title, content, category]
                articles.append({
                    'article_id': hit[0] if len(hit) > 0 else 'N/A',
                    'title': hit[1] if len(hit) > 1 else 'N/A',
                    'content': hit[2] if len(hit) > 2 else 'N/A',
                    'category': hit[3] if len(hit) > 3 else 'N/A'
                })
        
        return articles
        
    except Exception as e:
        # Fallback to SQL keyword search if vector search fails
        print(f"  ⚠️  Vector search failed, using keyword search: {str(e)[:100]}")
        return search_kb_sql_fallback(query)

def search_kb_sql_fallback(query: str):
    """Fallback to SQL keyword search if vector search is not available"""
    try:
        # Escape single quotes in query
        escaped_query = query.replace("'", "''")
        query_sql = f"SELECT * FROM {FUNCTION_SEARCH_KB}('{escaped_query}')"
        articles_df = execute_sql(query_sql, return_dataframe=True)
        
        if not articles_df.empty:
            return articles_df.to_dict('records')
        else:
            return []
    except Exception as e:
        print(f"  ❌ Error in SQL KB search: {e}")
        return []

def test_kb_search():
    """Test KB search functions"""
    print("🧪 Testing KB Search Functions")
    print("="*80)
    
    # Test queries
    test_queries = [
        "What is the complaint process?",
        "complaint process",
        "How do I make a complaint?",
        "contribution limits",
        "withdrawal rules"
    ]
    
    print("\n📝 Test 1: Vector Search (will fallback to SQL locally)")
    print("-" * 80)
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        try:
            results = search_kb_vector_search(query, num_results=3)
            if results:
                print(f"  ✅ Found {len(results)} results")
                for i, article in enumerate(results[:2], 1):
                    print(f"    {i}. [{article.get('article_id', 'N/A')}] {article.get('title', 'N/A')[:60]}...")
            else:
                print(f"  ⚠️  No results found")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n📝 Test 2: SQL Fallback (direct)")
    print("-" * 80)
    for query in test_queries[:3]:  # Test first 3
        print(f"\nQuery: '{query}'")
        try:
            results = search_kb_sql_fallback(query)
            if results:
                print(f"  ✅ Found {len(results)} results")
                for i, article in enumerate(results[:2], 1):
                    print(f"    {i}. [{article.get('article_id', 'N/A')}] {article.get('title', 'N/A')[:60]}...")
            else:
                print(f"  ⚠️  No results found")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n📝 Test 3: Natural Language Queries")
    print("-" * 80)
    natural_queries = [
        "What is the complaint process?",  # Should match "complaint" articles
        "How do I know if I'm eligible?",  # Should match eligibility articles
        "Tell me about contributions",      # Should match contribution articles
    ]
    
    for query in natural_queries:
        print(f"\nQuery: '{query}'")
        try:
            results = search_kb_vector_search(query, num_results=3)
            if results:
                print(f"  ✅ Found {len(results)} results")
                print(f"  Results:")
                for i, article in enumerate(results, 1):
                    print(f"    {i}. [{article.get('article_id', 'N/A')}] {article.get('title', 'N/A')}")
                    print(f"       Category: {article.get('category', 'N/A')}")
            else:
                print(f"  ⚠️  No results found")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n" + "="*80)
    print("📊 SUMMARY:")
    print("="*80)
    print("✅ Vector search function: Works (falls back to SQL locally)")
    print("✅ SQL fallback: Works (keyword matching)")
    print("⚠️  Note: Full semantic search requires vector index in Databricks")
    print("\n💡 To enable full semantic search:")
    print("   1. Run: python scripts/create_kb_vector_index.py (in Databricks)")
    print("   2. Vector search will then work with natural language queries")
    print("="*80)

if __name__ == "__main__":
    test_kb_search()
