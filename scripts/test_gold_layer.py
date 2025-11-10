#!/usr/bin/env python3
"""
Test Gold Layer Tables and UC Functions
Tests the Gold layer tables and UC functions that use them

Run: python scripts/test_gold_layer.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
from config.config import get_workspace_client
import time
from datetime import datetime

def test_gold_layer_tables():
    """Test Gold layer tables"""
    print("="*80)
    print("Testing Gold Layer Tables")
    print("="*80)
    
    w = get_workspace_client()
    
    # Test queries
    test_queries = [
        ("call_summaries", """
            SELECT 
                call_id,
                member_name,
                agent_id,
                call_duration_minutes,
                overall_sentiment,
                primary_intent,
                has_compliance_issues,
                compliance_severity_level,
                summary_created_at
            FROM member_analytics.call_center.call_summaries
            ORDER BY summary_created_at DESC
            LIMIT 5
        """),
        ("agent_performance", """
            SELECT 
                agent_id,
                call_date,
                total_calls,
                avg_call_duration_minutes,
                positive_sentiment_rate,
                compliance_rate,
                performance_score,
                metrics_calculated_at
            FROM member_analytics.call_center.agent_performance
            ORDER BY performance_score DESC
            LIMIT 5
        """),
        ("member_interaction_history", """
            SELECT 
                member_id,
                interaction_id,
                interaction_date,
                interaction_topic,
                overall_sentiment,
                call_duration_minutes,
                has_compliance_issues,
                interaction_created_at
            FROM member_analytics.call_center.member_interaction_history
            ORDER BY interaction_date DESC
            LIMIT 5
        """),
        ("daily_call_statistics", """
            SELECT 
                call_date,
                total_calls,
                active_agents,
                unique_members,
                avg_call_duration_minutes,
                positive_sentiment_rate,
                compliance_rate,
                stats_calculated_at
            FROM member_analytics.call_center.daily_call_statistics
            ORDER BY call_date DESC
        """)
    ]
    
    for table_name, query in test_queries:
        print(f"\n📊 Testing {table_name}:")
        print("-" * 80)
        
        try:
            response = w.statement_execution.execute_statement(
                warehouse_id='4b9b953939869799',
                statement=query,
                wait_timeout='30s'
            )
            
            statement_id = response.statement_id
            max_attempts = 30
            
            for attempt in range(max_attempts):
                status = w.statement_execution.get_statement(statement_id)
                
                if status.status.state == StatementState.SUCCEEDED:
                    if status.result and status.result.data_array:
                        # Get column names
                        columns = []
                        if status.manifest and status.manifest.schema and status.manifest.schema.columns:
                            columns = [col.name for col in status.manifest.schema.columns]
                        elif status.result.manifest and status.result.manifest.schema and status.result.manifest.schema.columns:
                            columns = [col.name for col in status.result.manifest.schema.columns]
                        else:
                            # Fallback: use column indices
                            columns = [f"col_{i}" for i in range(len(status.result.data_array[0]))]
                        
                        # Print header
                        print(f"Columns: {', '.join(columns)}")
                        print("-" * 80)
                        
                        # Print data
                        for row in status.result.data_array[:5]:
                            row_str = []
                            for i, val in enumerate(row):
                                if isinstance(val, (int, float)):
                                    if isinstance(val, float):
                                        row_str.append(f"{val:.2f}")
                                    else:
                                        row_str.append(str(val))
                                elif isinstance(val, datetime):
                                    row_str.append(val.strftime("%Y-%m-%d %H:%M:%S"))
                                else:
                                    row_str.append(str(val) if val is not None else "NULL")
                            print(" | ".join(row_str))
                        
                        print(f"\n✅ {table_name} query successful!")
                    else:
                        print(f"⚠️  Query succeeded but no data returned")
                    break
                elif status.status.state == StatementState.FAILED:
                    print(f"❌ Query failed: {status.status.state_message}")
                    break
                
                time.sleep(1)
            else:
                print(f"⏳ Query timed out after {max_attempts} seconds")
        
        except Exception as e:
            print(f"❌ Error: {str(e)[:300]}")

def test_uc_functions():
    """Test UC Functions that use Gold layer"""
    print("\n" + "="*80)
    print("Testing UC Functions (Gold Layer)")
    print("="*80)
    
    w = get_workspace_client()
    
    # First, get a member_id from call_summaries
    print("\n📋 Step 1: Getting a member_id from call_summaries...")
    member_query = """
        SELECT DISTINCT member_id 
        FROM member_analytics.call_center.call_summaries 
        LIMIT 1
    """
    
    try:
        response = w.statement_execution.execute_statement(
            warehouse_id='4b9b953939869799',
            statement=member_query,
            wait_timeout='30s'
        )
        
        statement_id = response.statement_id
        max_attempts = 30
        
        for attempt in range(max_attempts):
            status = w.statement_execution.get_statement(statement_id)
            
            if status.status.state == StatementState.SUCCEEDED:
                if status.result and status.result.data_array:
                    member_id = status.result.data_array[0][0]
                    print(f"✅ Found member_id: {member_id}")
                    
                    # Test get_member_history UC function
                    print(f"\n📋 Step 2: Testing get_member_history('{member_id}')...")
                    history_query = f"""
                        SELECT * FROM member_analytics.call_center.get_member_history('{member_id}')
                    """
                    
                    response2 = w.statement_execution.execute_statement(
                        warehouse_id='4b9b953939869799',
                        statement=history_query,
                        wait_timeout='30s'
                    )
                    
                    statement_id2 = response2.statement_id
                    
                    for attempt2 in range(max_attempts):
                        status2 = w.statement_execution.get_statement(statement_id2)
                        
                        if status2.status.state == StatementState.SUCCEEDED:
                            if status2.result and status2.result.data_array:
                                # Get column names
                                columns = []
                                if status2.manifest and status2.manifest.schema and status2.manifest.schema.columns:
                                    columns = [col.name for col in status2.manifest.schema.columns]
                                elif status2.result.manifest and status2.result.manifest.schema and status2.result.manifest.schema.columns:
                                    columns = [col.name for col in status2.result.manifest.schema.columns]
                                else:
                                    # Fallback: use column indices
                                    columns = [f"col_{i}" for i in range(len(status2.result.data_array[0]))]
                                
                                print(f"Columns: {', '.join(columns)}")
                                print("-" * 80)
                                
                                for row in status2.result.data_array:
                                    row_str = []
                                    for i, val in enumerate(row):
                                        if isinstance(val, (int, float)):
                                            if isinstance(val, float):
                                                row_str.append(f"{val:.2f}")
                                            else:
                                                row_str.append(str(val))
                                        elif isinstance(val, datetime):
                                            row_str.append(val.strftime("%Y-%m-%d %H:%M:%S"))
                                        else:
                                            row_str.append(str(val) if val is not None else "NULL")
                                    print(" | ".join(row_str))
                                
                                print(f"\n✅ get_member_history() UC function works!")
                            else:
                                print(f"⚠️  Function returned no data")
                            break
                        elif status2.status.state == StatementState.FAILED:
                            print(f"❌ Function failed: {status2.status.state_message}")
                            break
                        
                        time.sleep(1)
                    else:
                        print(f"⏳ Function call timed out")
                    
                    break
                else:
                    print(f"⚠️  No members found in call_summaries")
                    break
            elif status.status.state == StatementState.FAILED:
                print(f"❌ Query failed: {status.status.state_message}")
                break
            
            time.sleep(1)
        else:
            print(f"⏳ Query timed out")
    
    except Exception as e:
        print(f"❌ Error: {str(e)[:300]}")

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("Gold Layer & UC Functions Test Suite")
    print("="*80)
    
    test_gold_layer_tables()
    test_uc_functions()
    
    print("\n" + "="*80)
    print("✅ Testing Complete!")
    print("="*80)

if __name__ == "__main__":
    main()

