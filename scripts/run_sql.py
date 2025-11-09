#!/usr/bin/env python3
"""
SQL Execution Helper
Executes SQL files using the configured SQL Warehouse ID.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks import sql
from databricks.sdk import WorkspaceClient
from config.config import get_workspace_url, SQL_WAREHOUSE_ID

def execute_sql_file(sql_file_path):
    """Execute a SQL file using the configured warehouse"""
    print(f"📄 Executing SQL file: {sql_file_path}")
    print(f"🔌 Using SQL Warehouse ID: {SQL_WAREHOUSE_ID}")
    
    # Read SQL file
    with open(sql_file_path, 'r') as f:
        sql_content = f.read()
    
    # Remove comments and split by semicolons
    statements = []
    current_statement = ""
    
    for line in sql_content.split('\n'):
        # Skip comment-only lines
        stripped = line.strip()
        if stripped.startswith('--') or not stripped:
            continue
        
        current_statement += line + '\n'
        
        # If line ends with semicolon, it's a complete statement
        if stripped.endswith(';'):
            statements.append(current_statement.strip())
            current_statement = ""
    
    # Add any remaining statement
    if current_statement.strip():
        statements.append(current_statement.strip())
    
    # Get workspace URL
    workspace_url = get_workspace_url().rstrip('/')
    
    # Get HTTP path for warehouse
    w = WorkspaceClient()
    
    try:
        # Get warehouse HTTP path
        warehouse = w.warehouses.get(SQL_WAREHOUSE_ID)
        http_path = f"/sql/1.0/warehouses/{SQL_WAREHOUSE_ID}"
        
        print(f"✅ Found warehouse: {warehouse.name}")
        print(f"🔗 HTTP Path: {http_path}")
        
    except Exception as e:
        print(f"⚠️  Could not get warehouse details: {e}")
        print(f"   Using default HTTP path")
        http_path = f"/sql/1.0/warehouses/{SQL_WAREHOUSE_ID}"
    
    # Execute statements
    print(f"\n📊 Executing {len(statements)} SQL statement(s)...\n")
    
    try:
        # Connect using Databricks CLI token
        import subprocess
        token_result = subprocess.run(
            ['databricks', 'auth', 'token'],
            capture_output=True,
            text=True
        )
        
        if token_result.returncode != 0:
            # Try getting token from config
            from databricks.sdk.core import Config
            config = Config()
            token = config.token
        else:
            token = token_result.stdout.strip()
        
        # Connect to SQL warehouse
        connection = sql.connect(
            server_hostname=workspace_url.replace('https://', ''),
            http_path=http_path,
            access_token=token
        )
        
        cursor = connection.cursor()
        
        for i, statement in enumerate(statements, 1):
            if not statement.strip():
                continue
                
            print(f"  [{i}/{len(statements)}] Executing statement...")
            try:
                cursor.execute(statement)
                print(f"  ✅ Statement {i} completed")
            except Exception as e:
                print(f"  ⚠️  Statement {i} error: {e}")
                # Continue with next statement
                continue
        
        cursor.close()
        connection.close()
        
        print(f"\n✅ SQL execution completed!")
        
    except Exception as e:
        print(f"\n❌ Error executing SQL: {e}")
        print(f"\n💡 Alternative: Run SQL manually in Databricks SQL Editor")
        print(f"   Warehouse ID: {SQL_WAREHOUSE_ID}")
        raise

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_sql.py <sql_file>")
        sys.exit(1)
    
    sql_file = sys.argv[1]
    if not os.path.exists(sql_file):
        print(f"❌ SQL file not found: {sql_file}")
        sys.exit(1)
    
    execute_sql_file(sql_file)

