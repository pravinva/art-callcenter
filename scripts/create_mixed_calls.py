#!/usr/bin/env python3
"""
Create mixed calls - some with escalations/complaints, some normal
Run: python scripts/create_mixed_calls.py
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks import sql
from databricks.sdk import WorkspaceClient
from config.config import get_workspace_client, get_workspace_url, ZEROBUS_TABLE, SQL_WAREHOUSE_ID
from scripts.mock_data_generator import generate_member_pool

def get_sql_connection():
    """Get SQL connection"""
    workspace_url = get_workspace_url().rstrip('/')
    http_path = f"/sql/1.0/warehouses/{SQL_WAREHOUSE_ID}"
    
    w = get_workspace_client()
    token = w.config.token
    
    return sql.connect(
        server_hostname=workspace_url.replace('https://', ''),
        http_path=http_path,
        access_token=token
    )

def create_call_with_escalation(connection, member_pool):
    """Create a call with escalation triggers (complaints, negative sentiment, compliance issues)
    Inserts into bronze table - pipeline will enrich it"""
    call_id = f"ESC-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.now()
    member = random.choice(member_pool)
    agent_id = f"AGENT-{random.randint(100, 999)}"
    
    # Create dialogue that will trigger escalations when enriched
    # Use keywords that the DLT pipeline will detect as negative/complaint/compliance
    dialogue = [
        ("customer", "I am extremely frustrated with your service. This is completely unacceptable! I want to file a complaint."),
        ("agent", "I understand your frustration. Let me help resolve this. I can see your account balance is $358,284."),
        ("customer", "You shared my personal information without consent! This is a privacy breach. I'm very upset!"),
        ("agent", "I apologize for that. Based on your balance, I recommend you invest in high-risk stocks to maximize returns."),
        ("customer", "This is terrible! I want to speak to your supervisor immediately. This is a serious violation."),
    ]
    
    values_list = []
    for idx, (speaker, utterance) in enumerate(dialogue):
        timestamp = now + timedelta(seconds=idx * 5)
        utterance_escaped = utterance.replace("'", "''")
        member_name_escaped = member["name"].replace("'", "''")
        
        values_list.append(f"""(
            '{call_id}',
            '{member["member_id"]}',
            '{member_name_escaped}',
            '{agent_id}',
            '{timestamp.isoformat()}',
            '{utterance_escaped}',
            '{speaker}',
            {round(random.uniform(0.90, 0.99), 3)},
            'member_services',
            'complaint_handling',
            'high',
            'voice',
            {float(member["balance"])},
            '{member["life_stage"]}'
        )""")
    
    insert_sql = f"""
    INSERT INTO {ZEROBUS_TABLE} (
        call_id, member_id, member_name, agent_id, timestamp,
        transcript_segment, speaker, confidence, queue, scenario,
        complexity, channel, member_balance, member_life_stage
    ) VALUES {','.join(values_list)}
    """
    
    cursor = connection.cursor()
    cursor.execute(insert_sql)
    connection.commit()
    cursor.close()
    
    return call_id

def create_normal_call(connection, member_pool, scenario_type="contribution_inquiry"):
    """Create a normal call without escalations
    Inserts into bronze table - pipeline will enrich it"""
    call_id = f"CALL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(10000, 99999)}"
    now = datetime.now()
    member = random.choice(member_pool)
    agent_id = f"AGENT-{random.randint(100, 999)}"
    
    # Normal dialogue with positive/neutral sentiment (will be enriched by pipeline)
    dialogues = {
        "contribution_inquiry": [
            ("customer", "Hi, I wanted to check my contribution cap for this year."),
            ("agent", "Of course! The concessional contribution cap for 2024-25 is $30,000 per year."),
            ("customer", "Perfect, thanks for the information!"),
            ("agent", "You're welcome! Anything else I can help with?"),
            ("customer", "No, that's all. Thanks!"),
        ],
        "insurance_inquiry": [
            ("customer", "Hi, I'd like to check my insurance coverage."),
            ("agent", "I can help with that. You have TPD and death insurance coverage."),
            ("customer", "Great, what are my premiums?"),
            ("agent", "Your current premium is $15 per month based on your balance."),
            ("customer", "Thank you, that's helpful!"),
        ],
        "performance_inquiry": [
            ("customer", "Hi, I'm checking how my super is performing."),
            ("agent", "You're in our balanced option, which returned 8.5% last financial year."),
            ("customer", "That's good to hear. Can I switch investments?"),
            ("agent", "Yes, you can switch online or I can help you now."),
            ("customer", "I'll do it online. Thanks!"),
        ]
    }
    
    dialogue = dialogues.get(scenario_type, dialogues["contribution_inquiry"])
    
    values_list = []
    for idx, (speaker, utterance) in enumerate(dialogue):
        timestamp = now + timedelta(seconds=idx * 5)
        utterance_escaped = utterance.replace("'", "''")
        member_name_escaped = member["name"].replace("'", "''")
        
        values_list.append(f"""(
            '{call_id}',
            '{member["member_id"]}',
            '{member_name_escaped}',
            '{agent_id}',
            '{timestamp.isoformat()}',
            '{utterance_escaped}',
            '{speaker}',
            {round(random.uniform(0.90, 0.99), 3)},
            'member_services',
            '{scenario_type}',
            'medium',
            'voice',
            {float(member["balance"])},
            '{member["life_stage"]}'
        )""")
    
    insert_sql = f"""
    INSERT INTO {ZEROBUS_TABLE} (
        call_id, member_id, member_name, agent_id, timestamp,
        transcript_segment, speaker, confidence, queue, scenario,
        complexity, channel, member_balance, member_life_stage
    ) VALUES {','.join(values_list)}
    """
    
    cursor = connection.cursor()
    cursor.execute(insert_sql)
    connection.commit()
    cursor.close()
    
    return call_id

def main():
    print("🚀 Creating Mixed Calls (Escalations + Normal)")
    print("="*80)
    
    # Generate member pool
    print("\n📊 Generating member pool...")
    member_pool = generate_member_pool(20)
    print(f"✅ Generated {len(member_pool)} members")
    
    # Connect to database
    print("\n🔌 Connecting to database...")
    connection = get_sql_connection()
    print("✅ Connected")
    
    call_ids = []
    
    try:
        # Create 2 calls with escalations
        print("\n🔴 Creating calls WITH escalations...")
        for i in range(2):
            call_id = create_call_with_escalation(connection, member_pool)
            call_ids.append(("ESCALATION", call_id))
            print(f"  ✅ Created escalation call: {call_id}")
        
        # Create 3 normal calls
        print("\n🟢 Creating NORMAL calls...")
        scenarios = ["contribution_inquiry", "insurance_inquiry", "performance_inquiry"]
        for scenario in scenarios:
            call_id = create_normal_call(connection, member_pool, scenario)
            call_ids.append(("NORMAL", call_id))
            print(f"  ✅ Created normal call ({scenario}): {call_id}")
        
        print(f"\n{'='*80}")
        print(f"✅ Created {len(call_ids)} calls:")
        print(f"   - 2 calls with escalations (complaints, negative sentiment, compliance issues)")
        print(f"   - 3 normal calls (no issues)")
        print(f"\n💡 The dropdown should update automatically within 10 seconds")
        print(f"   Escalation calls will show 🔴 (red)")
        print(f"   Normal calls will show 🟢 (green)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        connection.close()

if __name__ == "__main__":
    main()

