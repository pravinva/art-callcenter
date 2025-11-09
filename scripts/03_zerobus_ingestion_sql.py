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

def ingest_call_sql(call_data, connection, agent_id=None):
    """Ingest realistic call via SQL INSERT with batching for better performance"""
    
    call_id = f"CALL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(10000, 99999)}"
    start_time = datetime.now()
    agent_id = agent_id or f"AGENT-{random.randint(100, 999)}"
    
    cursor = connection.cursor()
    
    try:
        # Batch INSERT for better performance (insert all utterances in one query)
        values_list = []
        
        for idx, (speaker, utterance) in enumerate(call_data["dialogue"]):
            timestamp = start_time + timedelta(seconds=idx * 5)
            
            # Escape single quotes in SQL
            utterance_escaped = utterance.replace("'", "''")
            member_name_escaped = call_data["member"]["name"].replace("'", "''")
            
            values_list.append(f"""(
                '{call_id}',
                '{call_data["member"]["member_id"]}',
                '{member_name_escaped}',
                '{agent_id}',
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
            )""")
        
        # Single INSERT with multiple VALUES (much faster than individual INSERTs)
        insert_sql = f"""
        INSERT INTO {ZEROBUS_TABLE} (
            call_id, member_id, member_name, agent_id, timestamp,
            transcript_segment, speaker, confidence, queue, scenario,
            complexity, channel, member_balance, member_life_stage
        ) VALUES {','.join(values_list)}
        """
        
        cursor.execute(insert_sql)
        connection.commit()
        
        print(f"✅ Call #{call_id}: {len(call_data['dialogue'])} utterances inserted (batched)")
        
    except Exception as e:
        connection.rollback()
        print(f"❌ Error ingesting call: {e}")
        raise
    finally:
        cursor.close()
    
    return call_id

def simulate_call_center_sql(num_calls=10, member_pool=None, throughput=None):
    """Simulate realistic call center volume using SQL with batching"""
    
    print(f"\n🏢 CALL CENTER SIMULATION (SQL Mode - Batched)")
    print(f"Generating {num_calls} realistic calls...")
    if throughput:
        print(f"Target throughput: {throughput} calls/minute")
    print(f"{'='*80}\n")
    
    print(f"🔌 Connecting to SQL Warehouse {SQL_WAREHOUSE_ID}...")
    connection = get_sql_connection()
    print("✅ Connected\n")
    
    # Generate agent pool for realistic distribution
    num_agents = random.randint(5, 15)
    agent_pool = [f"AGENT-{random.randint(100, 999)}" for _ in range(num_agents)]
    print(f"👥 Agent pool: {len(agent_pool)} agents\n")
    
    call_ids = []
    start_time = datetime.now()
    
    try:
        # Calculate inter-call delay based on throughput
        if throughput:
            inter_call_delay = 60.0 / throughput
        else:
            inter_call_delay = 1.0  # Default: 1 second between calls
        
        for i in range(num_calls):
            agent_id = random.choice(agent_pool)
            call_data = generate_realistic_call(member_pool)
            call_id = ingest_call_sql(call_data, connection, agent_id=agent_id)
            call_ids.append(call_id)
            
            if i < num_calls - 1:
                import time
                time.sleep(inter_call_delay)
        
        duration = (datetime.now() - start_time).total_seconds()
        calls_per_sec = len(call_ids) / duration if duration > 0 else 0
        
        print(f"\n{'='*80}")
        print(f"✅ SIMULATION COMPLETE")
        print(f"{'='*80}")
        print(f"📊 Statistics:")
        print(f"   Total calls: {len(call_ids)}")
        print(f"   Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"   Throughput: {calls_per_sec:.2f} calls/second ({calls_per_sec*60:.1f} calls/minute)")
        print(f"   Table: {ZEROBUS_TABLE}")
        print(f"{'='*80}\n")
        
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
    print("🚀 Phase 1.3: Zerobus Ingestion (SQL Fallback - Optimized)")
    print("="*80)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Simulate Genesys Cloud call center with SQL fallback')
    parser.add_argument('num_calls', type=int, nargs='?', default=10, 
                       help='Number of calls to generate (default: 10)')
    parser.add_argument('--throughput', type=float,
                       help='Calls per minute (default: 60 calls/min)')
    parser.add_argument('--members', type=int, default=50,
                       help='Number of members in pool (default: 50)')
    
    args = parser.parse_args()
    
    # Generate member pool
    print(f"\n📊 Generating member pool ({args.members} members)...")
    member_pool = generate_member_pool(args.members)
    print(f"✅ Generated {len(member_pool)} members")
    
    # Run simulation
    try:
        print(f"\n🎯 Generating {args.num_calls} calls via batched SQL INSERT...")
        if args.throughput:
            print(f"   Target throughput: {args.throughput} calls/minute")
        
        simulate_call_center_sql(args.num_calls, member_pool, throughput=args.throughput)
        
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

