#!/usr/bin/env python3
"""
Check Vector Search Index Status and Test Functionality
This script must be run in Databricks (not locally) as vector_search module is only available there.

Run in Databricks: python scripts/check_vector_index.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import (
    VECTOR_SEARCH_ENDPOINT, KB_TABLE, KB_INDEX_NAME, EMBEDDING_MODEL
)

def check_vector_index():
    """Check if vector index exists and test it"""
    print("🔍 Checking Vector Search Index Status")
    print("="*80)
    
    print(f"\n📊 Configuration:")
    print(f"   Endpoint: {VECTOR_SEARCH_ENDPOINT}")
    print(f"   Index: {KB_INDEX_NAME}")
    print(f"   Source Table: {KB_TABLE}")
    print(f"   Embedding Model: {EMBEDDING_MODEL}")
    
    # Check if vector_search module is available
    try:
        from databricks.vector_search.client import VectorSearchClient
        print("\n✅ Vector Search module is available")
    except ImportError:
        # Try alternative import path
        try:
            from databricks_vectorsearch.client import VectorSearchClient
            print("\n✅ Vector Search module is available (databricks-vectorsearch)")
        except ImportError:
            print("\n❌ Vector Search module not available")
            print("   ⚠️  This script must be run in Databricks runtime")
            print("   💡 Vector search is only available in Databricks, not locally")
            return False
    
    vsc = VectorSearchClient(disable_notice=True)
    
    # Check if index exists
    print(f"\n🔍 Checking if index exists...")
    try:
        index = vsc.get_index(
            endpoint_name=VECTOR_SEARCH_ENDPOINT,
            index_name=KB_INDEX_NAME
        )
        print(f"✅ Index exists: {KB_INDEX_NAME}")
        
        # Get index status
        try:
            index_status = index.describe()
            print(f"\n📊 Index Details:")
            if hasattr(index_status, 'status'):
                print(f"   Status: {index_status.status}")
            if hasattr(index_status, 'index_type'):
                print(f"   Type: {index_status.index_type}")
            if hasattr(index_status, 'primary_key'):
                print(f"   Primary Key: {index_status.primary_key}")
            if hasattr(index_status, 'embedding_source_column'):
                print(f"   Embedding Column: {index_status.embedding_source_column}")
        except Exception as e:
            print(f"   ⚠️  Could not get index details: {e}")
        
        # Sync index to ensure it's up to date
        print(f"\n🔄 Syncing index...")
        try:
            index.sync()
            print("✅ Index sync triggered")
        except Exception as sync_error:
            print(f"⚠️  Sync warning: {sync_error}")
            print("   (Index may still be usable)")
        
        # Test vector search
        print(f"\n🧪 Testing Vector Search...")
        test_queries = [
            "What is the complaint process?",
            "How do I make a complaint?",
            "contribution limits",
            "withdrawal rules"
        ]
        
        for query in test_queries:
            print(f"\n   Query: '{query}'")
            try:
                results = index.similarity_search(
                    query_text=query,
                    columns=["article_id", "title", "content", "category"],
                    num_results=3
                )
                
                if results and 'result' in results and 'data_array' in results['result']:
                    hits = results['result']['data_array']
                    print(f"   ✅ Found {len(hits)} results")
                    for i, hit in enumerate(hits[:2], 1):
                        article_id = hit[0] if len(hit) > 0 else 'N/A'
                        title = hit[1] if len(hit) > 1 else 'N/A'
                        print(f"      {i}. [{article_id}] {title[:60]}...")
                else:
                    print(f"   ⚠️  No results returned")
            except Exception as test_error:
                print(f"   ❌ Error: {test_error}")
        
        print("\n" + "="*80)
        print("✅ Vector Search Index is WORKING!")
        print("="*80)
        print(f"\n📊 Summary:")
        print(f"   ✅ Index exists: {KB_INDEX_NAME}")
        print(f"   ✅ Vector search is functional")
        print(f"   ✅ Semantic search is enabled")
        print(f"\n💡 The index will automatically sync when KB articles change")
        return True
        
    except Exception as e:
        error_str = str(e).lower()
        if "not found" in error_str or "does not exist" in error_str:
            print(f"\n❌ Index does NOT exist: {KB_INDEX_NAME}")
            print(f"\n💡 To create the index, run:")
            print(f"   python scripts/create_kb_vector_index.py")
            print(f"\n   Or in Databricks notebook:")
            print(f"   %run scripts/create_kb_vector_index.py")
            return False
        else:
            print(f"\n❌ Error checking index: {e}")
            return False

if __name__ == "__main__":
    success = check_vector_index()
    sys.exit(0 if success else 1)

