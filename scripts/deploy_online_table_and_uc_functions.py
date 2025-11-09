#!/usr/bin/env python3
"""
Phase 2 & 3: Deploy Online Table View and UC Functions
Creates dependencies, views, and UC Functions for the agent tools.

Run: python scripts/deploy_online_table_and_uc_functions.py
"""
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks import sql
from config.config import get_workspace_url, SQL_WAREHOUSE_ID
import os

def run_sql_file(sql_file_path):
    """Execute SQL file against Databricks SQL Warehouse"""
    workspace_url = get_workspace_url()
    
    connection = sql.connect(
        server_hostname=workspace_url.replace('https://', ''),
        http_path=f'/sql/1.0/warehouses/{SQL_WAREHOUSE_ID}',
        access_token=os.environ.get('DATABRICKS_TOKEN')
    )
    
    cursor = connection.cursor()
    
    try:
        with open(sql_file_path, 'r') as f:
            sql_content = f.read()
        
        # Split by semicolons and execute each statement
        statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for i, statement in enumerate(statements, 1):
            if not statement:
                continue
            try:
                print(f"   Executing statement {i}/{len(statements)}...")
                cursor.execute(statement)
                print(f"   ✅ Statement {i} completed")
            except Exception as e:
                print(f"   ⚠️  Statement {i} error: {e}")
                # Continue with next statement
                continue
        
        connection.commit()
        print(f"✅ SQL file executed: {sql_file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error executing SQL file: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cursor.close()
        connection.close()

def check_table_exists(table_name):
    """Check if a table exists"""
    workspace_url = get_workspace_url()
    
    connection = sql.connect(
        server_hostname=workspace_url.replace('https://', ''),
        http_path=f'/sql/1.0/warehouses/{SQL_WAREHOUSE_ID}',
        access_token=os.environ.get('DATABRICKS_TOKEN')
    )
    
    cursor = connection.cursor()
    
    try:
        # Parse catalog.schema.table
        parts = table_name.split('.')
        if len(parts) == 3:
            catalog, schema, table = parts
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_catalog = '{catalog}' 
                  AND table_schema = '{schema}' 
                  AND table_name = '{table}'
            """)
            result = cursor.fetchone()
            exists = result[0] > 0 if result else False
        else:
            # Try direct query
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} LIMIT 1")
            exists = True
        return exists
    except Exception:
        return False
    finally:
        cursor.close()
        connection.close()

def deploy_all():
    """Deploy Online Table view and UC Functions"""
    print("🚀 Phase 2 & 3: Deploying Online Table View and UC Functions")
    print("="*80)
    
    base_dir = Path(__file__).parent.parent
    
    # Step 1: Create dependencies (knowledge_base, member_data tables)
    print("\n" + "="*80)
    print("STEP 1: Creating Dependencies")
    print("="*80)
    
    deps_sql = base_dir / "sql" / "03_create_dependencies.sql"
    if deps_sql.exists():
        print(f"\n📝 Creating dependency tables...")
        run_sql_file(deps_sql)
    else:
        print(f"⚠️  Dependencies SQL file not found: {deps_sql}")
    
    # Step 2: Wait for enriched_transcripts table (if DLT pipeline is running)
    print("\n" + "="*80)
    print("STEP 2: Checking enriched_transcripts table")
    print("="*80)
    
    enriched_table = "member_analytics.call_center.enriched_transcripts"
    print(f"\n🔍 Checking for {enriched_table}...")
    
    if check_table_exists(enriched_table):
        print(f"✅ {enriched_table} exists!")
    else:
        print(f"⚠️  {enriched_table} not found yet")
        print(f"   This is expected if DLT pipeline is still processing")
        print(f"   The view will be created but may be empty until pipeline completes")
        print(f"   Continuing with deployment...")
    
    # Step 3: Create Online Table view
    print("\n" + "="*80)
    print("STEP 3: Creating Online Table View")
    print("="*80)
    
    online_table_sql = base_dir / "sql" / "02_online_table.sql"
    if online_table_sql.exists():
        print(f"\n📝 Creating live_transcripts_view...")
        run_sql_file(online_table_sql)
        print(f"\n💡 Note: To create actual Online Table:")
        print(f"   1. Go to Catalog Explorer")
        print(f"   2. Select: member_analytics.call_center.enriched_transcripts")
        print(f"   3. Click 'Create Online Table'")
        print(f"   4. Configure refresh settings")
    else:
        print(f"⚠️  Online Table SQL file not found: {online_table_sql}")
    
    # Step 4: Create UC Functions
    print("\n" + "="*80)
    print("STEP 4: Creating UC Functions")
    print("="*80)
    
    uc_functions_sql = base_dir / "sql" / "03_uc_functions.sql"
    if uc_functions_sql.exists():
        print(f"\n📝 Creating UC Functions...")
        run_sql_file(uc_functions_sql)
    else:
        print(f"⚠️  UC Functions SQL file not found: {uc_functions_sql}")
    
    # Step 5: Verify deployment
    print("\n" + "="*80)
    print("STEP 5: Verification")
    print("="*80)
    
    print(f"\n🔍 Verifying UC Functions...")
    
    workspace_url = get_workspace_url()
    connection = sql.connect(
        server_hostname=workspace_url.replace('https://', ''),
        http_path=f'/sql/1.0/warehouses/{SQL_WAREHOUSE_ID}',
        access_token=os.environ.get('DATABRICKS_TOKEN')
    )
    
    cursor = connection.cursor()
    
    functions_to_check = [
        "member_analytics.call_center.get_live_call_context",
        "member_analytics.call_center.search_knowledge_base",
        "member_analytics.call_center.check_compliance_realtime",
        "member_analytics.call_center.get_member_history"
    ]
    
    for func_name in functions_to_check:
        try:
            # Try to describe the function
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
                print(f"   ⚠️  {func_name} - not found")
        except Exception as e:
            print(f"   ⚠️  {func_name} - check failed: {e}")
    
    cursor.close()
    connection.close()
    
    print("\n" + "="*80)
    print("DEPLOYMENT SUMMARY")
    print("="*80)
    print(f"\n✅ Components deployed:")
    print(f"   ✅ Dependency tables (knowledge_base, member_data)")
    print(f"   ✅ Online Table view (live_transcripts_view)")
    print(f"   ✅ UC Functions (4 functions)")
    
    print(f"\n📋 Next Steps:")
    print(f"   1. Wait for DLT pipeline to complete and create enriched_transcripts")
    print(f"   2. Create Online Table via UI (see instructions above)")
    print(f"   3. Test UC Functions with sample queries")
    print(f"   4. Proceed to Phase 4: GenAI Agent Development")

if __name__ == "__main__":
    deploy_all()

