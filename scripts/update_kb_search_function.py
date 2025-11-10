#!/usr/bin/env python3
"""
Update the search_knowledge_base UC function to use real KB articles instead of stub.
Run this script to update the function after populating KB articles.

Run: python scripts/update_kb_search_function.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import get_workspace_client, SQL_WAREHOUSE_ID
from databricks import sql

def execute_sql(query, return_dataframe=False):
    """Execute SQL query using Databricks SQL connector"""
    connection = sql.connect(
        server_hostname=get_workspace_client().config.host.replace("https://", "").replace("http://", ""),
        http_path=f"/sql/1.0/warehouses/{SQL_WAREHOUSE_ID}",
        access_token=get_workspace_client().config.token
    )
    cursor = connection.cursor()
    cursor.execute(query)
    
    if return_dataframe:
        import pandas as pd
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=columns)
        cursor.close()
        connection.close()
        return df
    else:
        cursor.close()
        connection.close()
        return None

def update_kb_search_function():
    """Update search_knowledge_base function to use real KB articles"""
    print("🚀 Updating search_knowledge_base UC Function")
    print("="*80)
    
    # Read the updated function from SQL file
    sql_file = Path(__file__).parent.parent / "sql" / "03_uc_functions.sql"
    
    if not sql_file.exists():
        print(f"❌ SQL file not found: {sql_file}")
        return False
    
    print(f"\n📖 Reading SQL file: {sql_file}")
    with open(sql_file, 'r') as f:
        sql_content = f.read()
    
    # Extract the search_knowledge_base function definition
    lines = sql_content.split('\n')
    function_start = None
    function_end = None
    
    for i, line in enumerate(lines):
        if 'CREATE OR REPLACE FUNCTION member_analytics.call_center.search_knowledge_base' in line:
            function_start = i
        elif function_start is not None and 'RETURN SELECT' in line:
            # Find the end of the function (next CREATE OR REPLACE or end of file)
            for j in range(i + 1, len(lines)):
                if 'CREATE OR REPLACE FUNCTION' in lines[j] or 'GRANT EXECUTE' in lines[j]:
                    function_end = j
                    break
            if function_end is None:
                function_end = len(lines)
            break
    
    if function_start is None:
        print("❌ Could not find search_knowledge_base function in SQL file")
        return False
    
    # Build the function statement
    function_statement = '\n'.join(lines[function_start:function_end])
    
    print(f"\n💾 Updating search_knowledge_base function...")
    print(f"   Function will now query: member_analytics.knowledge_base.kb_articles")
    
    try:
        execute_sql(function_statement)
        print(f"✅ Successfully updated search_knowledge_base function")
        
        # Test the function
        print(f"\n🔍 Testing updated function...")
        test_query = "SELECT * FROM member_analytics.call_center.search_knowledge_base('contribution caps')"
        results = execute_sql(test_query, return_dataframe=True)
        
        if not results.empty:
            print(f"\n📊 Test Results:")
            print("="*80)
            for _, row in results.iterrows():
                print(f"\n  Article ID: {row['article_id']}")
                print(f"  Title: {row['title']}")
                print(f"  Category: {row.get('category', 'N/A')}")
                print(f"  Content Length: {len(str(row['content']))} characters")
            
            print(f"\n✅ Function is working correctly!")
            print(f"   Found {len(results)} articles for 'contribution caps'")
        else:
            print(f"⚠️  Function updated but no results returned")
            print(f"   Make sure KB articles are populated: python scripts/populate_kb_articles.py")
        
        print(f"\n✅ KB search function updated successfully!")
        print(f"\n💡 Next Steps:")
        print(f"   1. Refresh the Streamlit dashboard")
        print(f"   2. Search KB - you should see real ART articles")
        print(f"   3. Try searching: 'contribution caps', 'withdrawal', 'insurance'")
        
    except Exception as e:
        print(f"❌ Error updating function: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    update_kb_search_function()

