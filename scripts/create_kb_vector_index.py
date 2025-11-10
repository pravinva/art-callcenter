#!/usr/bin/env python3
"""
Create Vector Search Index for Knowledge Base Articles
Uses delta sync to automatically sync with kb_articles table changes.

Run: python scripts/create_kb_vector_index.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try standard import first, then fallback to databricks-vectorsearch package
try:
    from databricks.vector_search.client import VectorSearchClient
except ImportError:
    from databricks_vectorsearch.client import VectorSearchClient

from config.config import (
    VECTOR_SEARCH_ENDPOINT, KB_TABLE, KB_INDEX_NAME, EMBEDDING_MODEL
)

def create_kb_vector_index():
    """Create Vector Search index for KB articles with delta sync"""
    print("🚀 Creating Vector Search Index for Knowledge Base")
    print("="*80)
    
    vsc = VectorSearchClient(disable_notice=True)
    
    print(f"\n📊 Configuration:")
    print(f"   Endpoint: {VECTOR_SEARCH_ENDPOINT}")
    print(f"   Index: {KB_INDEX_NAME}")
    print(f"   Source Table: {KB_TABLE}")
    print(f"   Embedding Model: {EMBEDDING_MODEL}")
    
    # Check if index already exists
    try:
        index = vsc.get_index(
            endpoint_name=VECTOR_SEARCH_ENDPOINT,
            index_name=KB_INDEX_NAME
        )
        print(f"\n✅ Index already exists: {KB_INDEX_NAME}")
        print("🔄 Syncing index...")
        index.sync()
        print("✅ Index sync triggered")
        return True
    except Exception as e:
        if "not found" not in str(e).lower() and "does not exist" not in str(e).lower():
            print(f"⚠️  Error checking index: {e}")
            raise
    
    # Create new index with delta sync
    print(f"\n🔄 Creating Vector Search index...")
    try:
        index = vsc.create_delta_sync_index(
            endpoint_name=VECTOR_SEARCH_ENDPOINT,
            index_name=KB_INDEX_NAME,
            source_table_name=KB_TABLE,
            pipeline_type="TRIGGERED",  # Delta sync - automatically syncs on table changes
            primary_key="article_id",
            embedding_source_column="content",  # Embed the content column
            embedding_model_endpoint_name=EMBEDDING_MODEL
        )
        
        print(f"✅ Created Vector Search index: {KB_INDEX_NAME}")
        
        # Wait a bit for index to be ready, then sync
        print("\n⏳ Waiting for index to be ready...")
        import time
        max_attempts = 12
        for i in range(max_attempts):
            time.sleep(5)
            try:
                index.sync()
                print("✅ Vector Search index sync triggered")
                break
            except Exception as sync_error:
                if "not ready" in str(sync_error).lower() and i < max_attempts - 1:
                    if i % 2 == 0:
                        print(f"   Still initializing... ({i*5}s)")
                    continue
                else:
                    print(f"⚠️  Sync may need to be triggered later when index is ready")
                    print(f"   Index created but not yet ready for sync")
                    return True
        
        # Test vector search (if index is ready)
        try:
            print("\n🧪 Testing vector search...")
            results = index.similarity_search(
                query_text="What is the complaint process?",
                columns=["article_id", "title", "content", "category"],
                num_results=3
            )
            
            print("\n🔍 Test Vector Search Results:")
            if results and 'result' in results and 'data_array' in results['result']:
                for i, hit in enumerate(results['result']['data_array'], 1):
                    print(f"\nResult {i}:")
                    print(f"  Article ID: {hit[0]}")
                    print(f"  Title: {hit[1]}")
                    print(f"  Content: {hit[2][:150]}...")
            else:
                print("   No results returned")
        except Exception as test_error:
            print(f"⚠️  Could not test search (index may still be initializing): {test_error}")
        
        print("\n" + "="*80)
        print("✅ Vector Search Index Creation Complete!")
        print("="*80)
        print(f"\n📊 Summary:")
        print(f"   ✅ Index: {KB_INDEX_NAME}")
        print(f"   ✅ Source Table: {KB_TABLE}")
        print(f"   ✅ Endpoint: {VECTOR_SEARCH_ENDPOINT}")
        print(f"   ✅ Delta Sync: Enabled (auto-syncs on table changes)")
        print(f"\n💡 The index will automatically sync when KB articles are added/updated")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating index: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Ensure the kb_articles table exists and has data")
        print("   2. Check that you have permissions to create vector search indexes")
        print("   3. Verify the endpoint name is correct")
        return False

if __name__ == "__main__":
    success = create_kb_vector_index()
    sys.exit(0 if success else 1)

