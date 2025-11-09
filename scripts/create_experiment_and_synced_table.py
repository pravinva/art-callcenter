#!/usr/bin/env python3
"""
Create MLflow Experiment and Evaluate Synced Tables
- Creates experiment for ART Live Agent Assist
- Creates Synced Table if useful (replacement for deprecated Online Tables)

Run: python scripts/create_experiment_and_synced_table.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import mlflow
from databricks.sdk import WorkspaceClient
from config.config import get_workspace_client, ENRICHED_TABLE

def create_experiment():
    """Create MLflow experiment"""
    print("🚀 Creating MLflow Experiment")
    print("="*80)
    
    experiment_path = "/Workspace/Users/pravin.varma@databricks.com/ART_Live_Agent_Assist"
    
    try:
        mlflow.set_experiment(experiment_path)
        print(f"✅ Experiment created/found: {experiment_path}")
        
        # Get experiment details
        experiment = mlflow.get_experiment_by_name(experiment_path)
        if experiment:
            print(f"   Experiment ID: {experiment.experiment_id}")
            print(f"   Artifact Location: {experiment.artifact_location}")
        
        return True
    except Exception as e:
        print(f"❌ Error creating experiment: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_synced_table():
    """Create Synced Table (replacement for Online Tables)"""
    print("\n🚀 Creating Synced Table")
    print("="*80)
    
    w = get_workspace_client()
    
    # Synced Tables provide low-latency access to Delta tables
    # They sync data from Delta tables to a high-performance store
    table_name = ENRICHED_TABLE  # member_analytics.call_center.enriched_transcripts
    
    print(f"\n📋 Table: {table_name}")
    print(f"   Synced Tables provide sub-second query latency")
    print(f"   They replace deprecated Online Tables")
    
    try:
        # Check if Synced Tables API is available
        # Note: Synced Tables might use a different API endpoint
        # Let's try using the catalog API to create a synced table
        
        # Parse table name
        parts = table_name.split('.')
        catalog_name = parts[0]
        schema_name = parts[1]
        table_name_only = parts[2]
        
        synced_table_name = f"{catalog_name}.{schema_name}.{table_name_only}_synced"
        
        print(f"\n📝 Creating Synced Table: {synced_table_name}")
        print(f"   Source: {table_name}")
        
        # Try to create synced table using SQL
        from databricks import sql
        from config.config import get_workspace_url, SQL_WAREHOUSE_ID
        import os
        
        workspace_url = get_workspace_url()
        conn = sql.connect(
            server_hostname=workspace_url.replace('https://', ''),
            http_path=f'/sql/1.0/warehouses/{SQL_WAREHOUSE_ID}',
            access_token=os.environ.get('DATABRICKS_TOKEN')
        )
        
        cursor = conn.cursor()
        
        # Create synced table using CREATE TABLE ... AS SELECT
        # Synced tables are created with specific syntax
        # Note: Actual syntax may vary - this is a placeholder approach
        try:
            # First, check if we can create a synced table via SQL
            # Synced Tables might need to be created via UI or REST API
            # Let's try the SQL approach first
            
            create_sql = f"""
            CREATE TABLE IF NOT EXISTS {synced_table_name}
            USING DELTA
            LOCATION '{table_name}'
            """
            
            # Actually, Synced Tables are created differently
            # They use CREATE SYNC TABLE or similar syntax
            # Let's use the proper approach - create via catalog API or UI
            
            print("   ⚠️  Synced Tables may need to be created via UI or REST API")
            print("   💡 Creating view instead for now (can be converted later)")
            
            # Create a view that can serve as the source for synced table
            view_name = f"{catalog_name}.{schema_name}.{table_name_only}_for_sync"
            view_sql = f"""
            CREATE OR REPLACE VIEW {view_name}
            AS SELECT * FROM {table_name}
            """
            
            cursor.execute(view_sql)
            print(f"   ✅ Created view: {view_name}")
            print(f"   💡 This view can be used to create Synced Table via UI")
            
            cursor.close()
            conn.close()
            
            print(f"\n📋 To create Synced Table:")
            print(f"   1. Go to Catalog Explorer")
            print(f"   2. Select: {table_name}")
            print(f"   3. Click 'Create Synced Table' (or 'Sync Table')")
            print(f"   4. Configure sync settings")
            
            return True
            
        except Exception as e:
            print(f"   ⚠️  SQL approach not available: {e}")
            print(f"   💡 Synced Tables must be created via UI or REST API")
            cursor.close()
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Error creating Synced Table: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*80)
    print("MLFLOW EXPERIMENT & SYNCED TABLE SETUP")
    print("="*80)
    
    # Create experiment
    exp_success = create_experiment()
    
    # Create synced table
    sync_success = create_synced_table()
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    if exp_success:
        print("✅ MLflow Experiment: Created")
    else:
        print("❌ MLflow Experiment: Failed")
    
    if sync_success:
        print("✅ Synced Table View: Created (convert to Synced Table via UI)")
    else:
        print("⚠️  Synced Table: Manual creation required via UI")
    
    print("\n📋 Next Steps:")
    print("   1. Use experiment for logging agent runs")
    print("   2. Create Synced Table via UI if low-latency access needed")
    print("   3. Continue with app deployment")

if __name__ == "__main__":
    main()

