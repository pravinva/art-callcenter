#!/usr/bin/env python3
"""
Insert test data with escalation triggers into enriched_transcripts table.
Creates 2 calls that will trigger escalation_recommended = TRUE.

Run: python scripts/insert_escalation_test_data.py
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import uuid

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import get_workspace_client, ENRICHED_TABLE, SQL_WAREHOUSE_ID
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

def insert_escalation_test_data():
    """Insert 2 calls with escalation triggers"""
    print("🚀 Inserting Escalation Test Data")
    print("="*80)
    
    # Generate unique call IDs
    call_id_1 = f"ESC-{uuid.uuid4().hex[:8].upper()}"
    call_id_2 = f"ESC-{uuid.uuid4().hex[:8].upper()}"
    
    # Current timestamp
    now = datetime.now()
    
    print(f"\n📞 Creating Call 1: {call_id_1}")
    print("   Scenario: CRITICAL compliance violation")
    print("   Conditions: compliance_severity = 'CRITICAL'")
    
    # Call 1: CRITICAL compliance violation (triggers escalation)
    call1_data = [
        # Utterance 1: CRITICAL compliance violation
        f"('{call_id_1}', 'TR-12345', 'Tracy Robinson', 'AGENT-697', "
        f"'{now - timedelta(minutes=5)}', 'I can see your account balance is $358,284. "
        f"Based on this, I recommend you invest in high-risk stocks to maximize returns.', "
        f"'agent', 0.95, 'general', 'compliance_violations', 'high', 'phone', 358284.0, 'pre_retirement', "
        f"'negative', 'complaint', 'privacy_breach', 'CRITICAL', '{now}')",
        
        # Utterance 2: More negative sentiment
        f"('{call_id_1}', 'TR-12345', 'Tracy Robinson', 'AGENT-697', "
        f"'{now - timedelta(minutes=4)}', 'This is terrible! I want to file a complaint. "
        f"You shared my personal information without consent.', "
        f"'customer', 0.98, 'general', 'compliance_violations', 'high', 'phone', 358284.0, 'pre_retirement', "
        f"'negative', 'complaint', 'privacy_breach', 'CRITICAL', '{now}')",
        
        # Utterance 3: Another compliance violation
        f"('{call_id_1}', 'TR-12345', 'Tracy Robinson', 'AGENT-697', "
        f"'{now - timedelta(minutes=3)}', 'I understand your concern. Let me access your "
        f"account details and provide personalized investment advice.', "
        f"'agent', 0.92, 'general', 'compliance_violations', 'high', 'phone', 358284.0, 'pre_retirement', "
        f"'neutral', 'information_request', 'personal_advice', 'HIGH', '{now}')",
        
        # Utterance 4: More negative sentiment
        f"('{call_id_1}', 'TR-12345', 'Tracy Robinson', 'AGENT-697', "
        f"'{now - timedelta(minutes=2)}', 'I am extremely upset about this privacy breach. "
        f"This is unacceptable behavior.', "
        f"'customer', 0.97, 'general', 'compliance_violations', 'high', 'phone', 358284.0, 'pre_retirement', "
        f"'negative', 'complaint', 'privacy_breach', 'CRITICAL', '{now}')",
        
        # Utterance 5: Final negative sentiment
        f"('{call_id_1}', 'TR-12345', 'Tracy Robinson', 'AGENT-697', "
        f"'{now - timedelta(minutes=1)}', 'I want to speak to your supervisor immediately. "
        f"This is a serious violation.', "
        f"'customer', 0.99, 'general', 'compliance_violations', 'high', 'phone', 358284.0, 'pre_retirement', "
        f"'negative', 'complaint', 'privacy_breach', 'CRITICAL', '{now}')",
    ]
    
    print(f"\n📞 Creating Call 2: {call_id_2}")
    print("   Scenario: Multiple negative sentiments + compliance violations")
    print("   Conditions: negative sentiment >= 3 AND compliance_flag != 'ok'")
    
    # Call 2: Multiple negative sentiments + compliance violations (triggers escalation)
    call2_data = [
        # Utterance 1: Negative sentiment + compliance violation
        f"('{call_id_2}', 'MC-67890', 'Michael Chen', 'AGENT-542', "
        f"'{now - timedelta(minutes=6)}', 'I am very frustrated with the service. "
        f"You gave me incorrect information about my withdrawal options.', "
        f"'customer', 0.94, 'general', 'complaint_handling', 'medium', 'phone', 125000.0, 'mid_career', "
        f"'negative', 'complaint', 'misinformation', 'HIGH', '{now}')",
        
        # Utterance 2: Another negative sentiment
        f"('{call_id_2}', 'MC-67890', 'Michael Chen', 'AGENT-542', "
        f"'{now - timedelta(minutes=5)}', 'This is completely unacceptable. "
        f"I lost money because of your bad advice.', "
        f"'customer', 0.96, 'general', 'complaint_handling', 'medium', 'phone', 125000.0, 'mid_career', "
        f"'negative', 'complaint', 'misinformation', 'HIGH', '{now}')",
        
        # Utterance 3: Third negative sentiment + compliance violation
        f"('{call_id_2}', 'MC-67890', 'Michael Chen', 'AGENT-542', "
        f"'{now - timedelta(minutes=4)}', 'I am extremely disappointed. "
        f"You should have known better than to provide such misleading information.', "
        f"'customer', 0.93, 'general', 'complaint_handling', 'medium', 'phone', 125000.0, 'mid_career', "
        f"'negative', 'complaint', 'misinformation', 'HIGH', '{now}')",
        
        # Utterance 4: Fourth negative sentiment
        f"('{call_id_2}', 'MC-67890', 'Michael Chen', 'AGENT-542', "
        f"'{now - timedelta(minutes=3)}', 'I want to escalate this immediately. "
        f"This is a serious issue.', "
        f"'customer', 0.98, 'general', 'complaint_handling', 'medium', 'phone', 125000.0, 'mid_career', "
        f"'negative', 'complaint', 'misinformation', 'HIGH', '{now}')",
        
        # Utterance 5: Agent response
        f"('{call_id_2}', 'MC-67890', 'Michael Chen', 'AGENT-542', "
        f"'{now - timedelta(minutes=2)}', 'I apologize for the confusion. "
        f"Let me connect you with a supervisor.', "
        f"'agent', 0.91, 'general', 'complaint_handling', 'medium', 'phone', 125000.0, 'mid_career', "
        f"'neutral', 'information_request', 'ok', 'LOW', '{now}')",
    ]
    
    # Combine all data
    all_data = call1_data + call2_data
    
    # Build INSERT statement - enriched_transcripts inherits from zerobus_transcripts + enrichment columns
    # Columns: call_id, member_id, member_name, agent_id, timestamp, transcript_segment, speaker, 
    #          confidence, queue, scenario, complexity, channel, member_balance, member_life_stage,
    #          sentiment, intent_category, compliance_flag, compliance_severity, enriched_at
    # Note: escalation_recommended is computed in queries, not stored
    
    insert_query = f"""
    INSERT INTO {ENRICHED_TABLE} 
    (call_id, member_id, member_name, agent_id, timestamp, transcript_segment, speaker, 
     confidence, queue, scenario, complexity, channel, member_balance, member_life_stage,
     sentiment, intent_category, compliance_flag, compliance_severity, enriched_at)
    VALUES
    {', '.join(all_data)}
    """
    
    print(f"\n💾 Inserting data into {ENRICHED_TABLE}...")
    print(f"   Total records: {len(all_data)}")
    
    try:
        execute_sql(insert_query)
        print(f"✅ Successfully inserted {len(all_data)} records")
        
        # Verify the data
        print(f"\n🔍 Verifying escalation triggers...")
        verify_query = f"""
        SELECT 
            call_id,
            member_name,
            agent_id,
            COUNT(*) as utterance_count,
            SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) as negative_count,
            SUM(CASE WHEN compliance_flag != 'ok' THEN 1 ELSE 0 END) as compliance_count,
            SUM(CASE WHEN intent_category = 'complaint' THEN 1 ELSE 0 END) as complaint_count,
            SUM(CASE WHEN compliance_severity = 'CRITICAL' THEN 1 ELSE 0 END) as critical_count,
            CASE 
                WHEN (
                    SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) > 0 AND
                    SUM(CASE WHEN compliance_flag != 'ok' THEN 1 ELSE 0 END) > 0 AND
                    SUM(CASE WHEN intent_category = 'complaint' THEN 1 ELSE 0 END) > 0
                ) THEN TRUE
                WHEN (
                    SUM(CASE WHEN compliance_severity = 'CRITICAL' THEN 1 ELSE 0 END) > 0
                ) THEN TRUE
                WHEN (
                    SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) >= 3 AND
                    SUM(CASE WHEN compliance_flag != 'ok' THEN 1 ELSE 0 END) > 0
                ) THEN TRUE
                ELSE FALSE
            END as should_escalate
        FROM {ENRICHED_TABLE}
        WHERE call_id IN ('{call_id_1}', '{call_id_2}')
        GROUP BY call_id, member_name, agent_id
        ORDER BY call_id
        """
        
        results = execute_sql(verify_query, return_dataframe=True)
        
        if not results.empty:
            print(f"\n📊 Verification Results:")
            print("="*80)
            for _, row in results.iterrows():
                print(f"\n  Call ID: {row['call_id']}")
                print(f"  Member: {row['member_name']}")
                print(f"  Agent: {row['agent_id']}")
                print(f"  Utterances: {row['utterance_count']}")
                print(f"  Negative Sentiments: {row['negative_count']}")
                print(f"  Compliance Violations: {row['compliance_count']}")
                print(f"  Complaint Intents: {row['complaint_count']}")
                print(f"  CRITICAL Violations: {row['critical_count']}")
                print(f"  Escalation Recommended: {row['should_escalate']}")
                print(f"  ✅ {'WILL TRIGGER ESCALATION' if row['should_escalate'] else 'WILL NOT TRIGGER ESCALATION'}")
        
        print(f"\n✅ Test data inserted successfully!")
        print(f"\n💡 Next Steps:")
        print(f"   1. Refresh the Supervisor Dashboard")
        print(f"   2. You should see 2 escalation alerts")
        print(f"   3. Call IDs: {call_id_1} and {call_id_2}")
        
    except Exception as e:
        print(f"❌ Error inserting data: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    insert_escalation_test_data()

