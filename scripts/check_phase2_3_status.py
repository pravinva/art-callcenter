#!/usr/bin/env python3
"""
Phase 2 & 3 Summary and Next Steps
Shows what was deployed and what needs to be done next.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks import sql
from config.config import get_workspace_url, SQL_WAREHOUSE_ID
import os

def check_status():
    """Check deployment status"""
    print("📊 Phase 2 & 3 Deployment Status")
    print("="*80)
    
    workspace_url = get_workspace_url()
    connection = sql.connect(
        server_hostname=workspace_url.replace('https://', ''),
        http_path=f'/sql/1.0/warehouses/{SQL_WAREHOUSE_ID}',
        access_token=os.environ.get('DATABRICKS_TOKEN')
    )
    
    cursor = connection.cursor()
    
    # Check tables
    print("\n📋 Tables:")
    tables_to_check = [
        "member_analytics.call_center.zerobus_transcripts",
        "member_analytics.call_center.enriched_transcripts",
        "member_analytics.knowledge_base.kb_articles",
        "member_analytics.member_data.interaction_history"
    ]
    
    for table in tables_to_check:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table} LIMIT 1")
            result = cursor.fetchone()
            count = result[0] if result else 0
            print(f"   ✅ {table} ({count} rows)")
        except Exception as e:
            if "TABLE_OR_VIEW_NOT_FOUND" in str(e):
                print(f"   ⏳ {table} (not created yet)")
            else:
                print(f"   ⚠️  {table} (error: {e})")
    
    # Check views
    print("\n📋 Views:")
    views_to_check = [
        "member_analytics.call_center.live_transcripts_view"
    ]
    
    for view in views_to_check:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {view} LIMIT 1")
            result = cursor.fetchone()
            count = result[0] if result else 0
            print(f"   ✅ {view} ({count} rows)")
        except Exception as e:
            if "TABLE_OR_VIEW_NOT_FOUND" in str(e):
                print(f"   ⏳ {view} (not created yet)")
            else:
                print(f"   ⚠️  {view} (error: {e})")
    
    # Check functions
    print("\n📋 UC Functions:")
    functions_to_check = [
        "member_analytics.call_center.get_live_call_context",
        "member_analytics.call_center.search_knowledge_base",
        "member_analytics.call_center.check_compliance_realtime",
        "member_analytics.call_center.get_member_history"
    ]
    
    for func_name in functions_to_check:
        try:
            # Try to call the function to see if it exists
            parts = func_name.split('.')
            catalog, schema, func = parts
            cursor.execute(f"""
                SELECT routine_name 
                FROM information_schema.routines 
                WHERE routine_catalog = '{catalog}' 
                  AND routine_schema = '{schema}' 
                  AND routine_name = '{func}'
            """)
            result = cursor.fetchone()
            if result:
                print(f"   ✅ {func_name}")
            else:
                print(f"   ⏳ {func_name} (not created yet)")
        except Exception as e:
            print(f"   ⏳ {func_name} (check failed)")
    
    cursor.close()
    connection.close()
    
    print("\n" + "="*80)
    print("📋 Next Steps:")
    print("="*80)
    print("\n1. ✅ Dependencies created (knowledge_base, member_data tables)")
    print("2. ✅ Online Table view created (live_transcripts_view)")
    print("3. ✅ 2 UC Functions created (search_knowledge_base, get_member_history)")
    print("\n4. ⏳ Wait for DLT pipeline to create enriched_transcripts table")
    print("5. ⏳ Run: python scripts/create_uc_functions_with_enriched_table.py")
    print("   (This will create get_live_call_context and check_compliance_realtime)")
    print("\n6. ⏳ Create Online Table via UI:")
    print("   - Go to Catalog Explorer")
    print("   - Select: member_analytics.call_center.enriched_transcripts")
    print("   - Click 'Create Online Table'")
    print("   - Configure refresh settings")
    print("\n7. ✅ Proceed to Phase 4: GenAI Agent Development")

if __name__ == "__main__":
    check_status()

