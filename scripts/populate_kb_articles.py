#!/usr/bin/env python3
"""
Populate Knowledge Base with comprehensive ART (Australian Retirement Trust) articles.
Replaces any sample/placeholder content with real, useful KB articles.

Run: python scripts/populate_kb_articles.py
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

def populate_kb_articles():
    """Populate KB articles with comprehensive ART content"""
    print("🚀 Populating Knowledge Base with ART Articles")
    print("="*80)
    
    # Read the SQL file
    sql_file = Path(__file__).parent.parent / "sql" / "populate_kb_articles.sql"
    
    if not sql_file.exists():
        print(f"❌ SQL file not found: {sql_file}")
        return False
    
    print(f"\n📖 Reading SQL file: {sql_file}")
    with open(sql_file, 'r') as f:
        sql_content = f.read()
    
    # Split by semicolons and execute each statement
    statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
    
    print(f"\n💾 Executing SQL statements...")
    
    try:
        # First, ensure we're using the correct catalog
        execute_sql("USE CATALOG member_analytics")
        # Don't use USE SCHEMA - just use fully qualified names
        
        # Clear existing articles
        print("   Clearing existing articles...")
        execute_sql("DELETE FROM member_analytics.knowledge_base.kb_articles")
        
        # Extract the INSERT statement from the SQL file
        # Find the INSERT INTO line and everything until the final semicolon
        lines = sql_content.split('\n')
        insert_start = None
        insert_end = None
        
        for i, line in enumerate(lines):
            if line.strip().upper().startswith('INSERT INTO'):
                insert_start = i
            elif insert_start is not None and line.strip().endswith(');'):
                insert_end = i + 1
                break
        
        if insert_start is None:
            print("❌ Could not find INSERT statement in SQL file")
            return False
        
        # Build the INSERT statement
        insert_statement = '\n'.join(lines[insert_start:insert_end])
        
        # Execute the INSERT statement
        print(f"   Inserting KB articles...")
        execute_sql(insert_statement)
        
        print(f"✅ Successfully inserted KB articles")
        
        # Verify the data
        print(f"\n🔍 Verifying KB articles...")
        verify_query = """
        SELECT 
            article_id,
            title,
            category,
            LENGTH(content) as content_length,
            SIZE(tags) as tag_count
        FROM member_analytics.knowledge_base.kb_articles
        ORDER BY article_id
        """
        
        results = execute_sql(verify_query, return_dataframe=True)
        
        if not results.empty:
            print(f"\n📊 Knowledge Base Articles:")
            print("="*80)
            for _, row in results.iterrows():
                print(f"\n  {row['article_id']}: {row['title']}")
                print(f"     Category: {row['category']}")
                print(f"     Content Length: {row['content_length']} characters")
                print(f"     Tags: {row['tag_count']} tags")
            
            print(f"\n✅ Total Articles: {len(results)}")
            print(f"✅ Categories: {results['category'].nunique()}")
            
            # Show summary
            summary_query = """
            SELECT 
                COUNT(*) as total_articles, 
                COUNT(DISTINCT category) as categories,
                COLLECT_SET(category) as category_list
            FROM member_analytics.knowledge_base.kb_articles
            """
            
            summary = execute_sql(summary_query, return_dataframe=True)
            if not summary.empty:
                print(f"\n📋 Summary:")
                print(f"   Total Articles: {summary.iloc[0]['total_articles']}")
                print(f"   Categories: {summary.iloc[0]['categories']}")
                print(f"   Category List: {', '.join(summary.iloc[0]['category_list'])}")
        
        print(f"\n✅ Knowledge Base populated successfully!")
        print(f"\n💡 Next Steps:")
        print(f"   1. Refresh the Streamlit dashboard")
        print(f"   2. Search KB in the dashboard - you should see real ART articles")
        print(f"   3. Articles cover: contributions, withdrawals, insurance, investments, etc.")
        
    except Exception as e:
        print(f"❌ Error populating KB articles: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    populate_kb_articles()

