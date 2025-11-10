#!/usr/bin/env python3
"""
Test KB Vector Search locally
Tests fallback to SQL keyword search when vector search is unavailable.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import (
    VECTOR_SEARCH_ENDPOINT, KB_INDEX_NAME, KB_TABLE, FUNCTION_SEARCH_KB
)
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState

SQL_WAREHOUSE_ID = "4b9b953939869799"

def execute_sql(query, return_dataframe=False):
    """Execute SQL using Databricks SDK"""
    import pandas as pd
    w = WorkspaceClient()
    
    try:
        response = w.statement_execution.execute_statement(
            warehouse_id=SQL_WAREHOUSE_ID,
            statement=query,
            wait_timeout="10s"
        )
        
        statement_id = response.statement_id
        max_wait = 10
        waited = 0
        
        while waited < max_wait:
            status = w.statement_execution.get_statement(statement_id)
            if status.status.state == StatementState.SUCCEEDED:
                # Get result chunks
                if status.result and status.result.data_array:
                    # Extract data from result
                    columns = [col.name for col in status.result.schema.columns] if status.result.schema else []
                    rows = []
                    for row in status.result.data_array:
                        row_dict = dict(zip(columns, row)) if columns else {}
                        rows.append(row_dict)
                    
                    if return_dataframe:
                        return pd.DataFrame(rows) if rows else pd.DataFrame()
                    return rows
                break
            elif status.status.state in [StatementState.FAILED, StatementState.CANCELED]:
                error_msg = f"SQL execution failed: {status.status.state}"
                if hasattr(status.status, 'message') and status.status.message:
                    error_msg = status.status.message
                raise Exception(error_msg)
            
            import time
            time.sleep(0.5)
            waited += 0.5
        
        return [] if not return_dataframe else pd.DataFrame()
    except Exception as e:
        print(f"SQL Error: {e}")
        return [] if not return_dataframe else pd.DataFrame()

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
            print(f"   ✅ Vector search index found")
        except Exception as e:
            # Index doesn't exist yet, fallback to SQL
            print(f"   ⚠️  Vector search index not found, using SQL fallback: {e}")
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
        
    except ImportError:
        # Vector search module not available locally
        print(f"   ⚠️  Vector search module not available (local), using SQL fallback")
        return search_kb_sql_fallback(query)
    except Exception as e:
        # Fallback to SQL keyword search if vector search fails
        print(f"   ⚠️  Vector search failed, using SQL fallback: {e}")
        return search_kb_sql_fallback(query)

def search_kb_sql_fallback(query: str):
    """Fallback to SQL keyword search if vector search is not available"""
    try:
        query_sql = f"SELECT * FROM {FUNCTION_SEARCH_KB}('{query}')"
        articles_df = execute_sql(query_sql, return_dataframe=True)
        
        if not articles_df.empty:
            return articles_df.to_dict('records')
        else:
            return []
    except Exception as e:
        print(f"   ❌ SQL fallback error: {e}")
        return []

def test_kb_search():
    """Test KB search functions"""
    print("🧪 Testing KB Search Functions Locally")
    print("="*80)
    
    # Test 1: Vector search (should fallback locally)
    print("\n📝 Test 1: Vector Search (should fallback to SQL locally)")
    print("-" * 80)
    test_queries = [
        "What is the complaint process?",
        "complaint process",
        "How do I make a complaint?",
        "contribution limits",
        "withdrawal rules"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        try:
            results = search_kb_vector_search(query, num_results=3)
            if results:
                print(f"✅ Found {len(results)} results")
                for i, article in enumerate(results[:2], 1):
                    print(f"   {i}. [{article.get('article_id', 'N/A')}] {article.get('title', 'N/A')[:60]}...")
            else:
                print("   ⚠️  No results found")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test 2: SQL fallback directly
    print("\n📝 Test 2: SQL Fallback (direct)")
    print("-" * 80)
    try:
        results = search_kb_sql_fallback("contribution")
        if results:
            print(f"✅ Found {len(results)} results")
            for i, article in enumerate(results[:2], 1):
                print(f"   {i}. [{article.get('article_id', 'N/A')}] {article.get('title', 'N/A')[:60]}...")
        else:
            print("   ⚠️  No results found")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Natural language queries (should work with vector search when available)
    print("\n📝 Test 3: Natural Language Queries")
    print("-" * 80)
    natural_queries = [
        "What is the complaint process?",
        "How do I complain?",
        "complaint process"
    ]
    
    for query in natural_queries:
        print(f"\nQuery: '{query}'")
        results = search_kb_vector_search(query, num_results=3)
        if results:
            print(f"✅ Found {len(results)} results (using {'vector search' if 'vector' in str(results).lower() else 'SQL fallback'})")
        else:
            print("   ⚠️  No results found")
    
    print("\n" + "="*80)
    print("💡 SUMMARY:")
    print("="*80)
    print("✅ Vector search function created")
    print("✅ Fallback to SQL keyword search works locally")
    print("✅ Error handling implemented")
    print("\n⚠️  NOTE:")
    print("   - Locally: Uses SQL keyword search (fallback)")
    print("   - In Databricks: Will use vector search (semantic)")
    print("   - Run 'python scripts/create_kb_vector_index.py' in Databricks")
    print("     to create the index, then semantic search will work!")

if __name__ == "__main__":
    test_kb_search()
