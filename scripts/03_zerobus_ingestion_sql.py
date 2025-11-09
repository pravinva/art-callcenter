#!/usr/bin/env python3
"""
Phase 1.3: Zerobus Ingestion (SQL Fallback)
Stream call transcripts to Delta table via SQL INSERT (fallback when Zerobus SDK unavailable).

Run: python scripts/03_zerobus_ingestion_sql.py [num_calls]
"""
import sys
import random
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks import sql
from databricks.sdk import WorkspaceClient
from config.config import (
    get_workspace_client, get_workspace_url,
    ZEROBUS_TABLE, SQL_WAREHOUSE_ID
)

# Import mock data generator
from scripts.mock_data_generator import generate_member_pool, generate_realistic_call

def get_sql_connection():
    """Get SQL connection using warehouse ID"""
    workspace_url = get_workspace_url().rstrip('/')
    http_path = f"/sql/1.0/warehouses/{SQL_WAREHOUSE_ID}"
    
    # Get token
    import subprocess
    token_result = subprocess.run(
        ['databricks', 'auth', 'token'],
        capture_output=True,
        text=True
    )
    
    if token_result.returncode != 0:
        from databricks.sdk.core import Config
        config = Config()
        token = config.token
    else:
        token = token_result.stdout.strip()
    
    return sql.connect(
        server_hostname=workspace_url.replace('https://', ''),
        http_path=http_path,
        access_token=token
    )

def ingest_call_sql(call_data, connection):
    """Ingest realistic call via SQL INSERT"""
    
    call_id = f"CALL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(10000, 99999)}"
    start_time = datetime.now()
    
    print(f"\n{'='*80}")
    print(f"📞 Call #{call_id}")
    print(f"Member: {call_data['member']['name']} ({call_data['member']['member_id']})")
    print(f"Scenario: {call_data['scenario_type']} ({call_data['complexity']})")
    print(f"Balance: ${call_data['member']['balance']:,.0f}")
    print(f"{'='*80}\n")
    
    cursor = connection.cursor()
    
    try:
        for idx, (speaker, utterance) in enumerate(call_data["dialogue"]):
            timestamp = start_time + timedelta(seconds=idx * 5)
            
            # Escape single quotes in SQL
            utterance_escaped = utterance.replace("'", "''")
            
            insert_sql = f"""
            INSERT INTO {ZEROBUS_TABLE} (
                call_id, member_id, member_name, agent_id, timestamp,
                transcript_segment, speaker, confidence, queue, scenario,
                complexity, channel, member_balance, member_life_stage
            ) VALUES (
                '{call_id}',
                '{call_data["member"]["member_id"]}',
                '{call_data["member"]["name"].replace("'", "''")}',
                'AGENT-{random.randint(100, 999)}',
                '{timestamp.isoformat()}',
                '{utterance_escaped}',
                '{speaker}',
                {round(random.uniform(0.90, 0.99), 3)},
                'member_services',
                '{call_data["scenario_type"]}',
                '{call_data["complexity"]}',
                'voice',
                {float(call_data["member"]["balance"])},
                '{call_data["member"]["life_stage"]}'
            )
            """
            
            cursor.execute(insert_sql)
            
            print(f"⚡ [{speaker:8s}] {utterance[:70]}")
        
        connection.commit()
        
    except Exception as e:
        connection.rollback()
        print(f"❌ Error ingesting call: {e}")
        raise
    finally:
        cursor.close()
    
    print(f"\n{'='*80}")
    print(f"✅ Call Complete - {len(call_data['dialogue'])} utterances inserted")
    print(f"{'='*80}\n")
    
    return call_id

def simulate_call_center_sql(num_calls=10, member_pool=None):
    """Simulate realistic call center volume using SQL"""
    
    print(f"\n🏢 CALL CENTER SIMULATION (SQL Mode)")
    print(f"Generating {num_calls} realistic calls...")
    print(f"{'='*80}\n")
    
    print(f"🔌 Connecting to SQL Warehouse {SQL_WAREHOUSE_ID}...")
    connection = get_sql_connection()
    print("✅ Connected\n")
    
    call_ids = []
    
    try:
        for i in range(num_calls):
            print(f"\n📱 Incoming Call {i+1}/{num_calls} - {datetime.now().strftime('%H:%M:%S')}")
            
            call_data = generate_realistic_call(member_pool)
            call_id = ingest_call_sql(call_data, connection)
            call_ids.append(call_id)
            
            if i < num_calls - 1:
                import time
                wait = random.randint(1, 3)  # Faster for demo
                print(f"\n⏳ Next call in {wait} seconds...\n")
                time.sleep(wait)
        
        print(f"\n✅ Successfully ingested {len(call_ids)} calls")
        print(f"   Check table: {ZEROBUS_TABLE}")
        print(f"\n📊 Verify with:")
        print(f"   SELECT COUNT(*) FROM {ZEROBUS_TABLE};")
        print(f"   SELECT DISTINCT call_id FROM {ZEROBUS_TABLE} ORDER BY call_id DESC LIMIT 10;")
        
    except Exception as e:
        print(f"\n❌ Error during simulation: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        connection.close()

def main():
    print("🚀 Phase 1.3: Zerobus Ingestion (SQL Fallback)")
    print("="*80)
    
    # Generate member pool
    print("\n📊 Generating member pool...")
    member_pool = generate_member_pool(50)
    print(f"✅ Generated {len(member_pool)} members")
    
    # Run simulation
    try:
        num_calls = int(sys.argv[1]) if len(sys.argv) > 1 else 10
        print(f"\n🎯 Ingesting {num_calls} calls via SQL INSERT...")
        
        simulate_call_center_sql(num_calls, member_pool)
        
        print("\n✅ Phase 1 Complete!")
        print("   Next: Phase 2 - DLT Pipeline for enrichment")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

