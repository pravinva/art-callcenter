#!/usr/bin/env python3
"""
Run the ART Live Agent Assist Dashboard

Usage:
    streamlit run app/agent_dashboard.py

Requirements:
    - DATABRICKS_TOKEN environment variable set
    - Active calls in enriched_transcripts table
    - GenAI agent deployed (optional, for AI suggestions)
"""
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    app_path = Path(__file__).parent / "app" / "agent_dashboard.py"
    if not app_path.exists():
        print(f"Error: {app_path} not found")
        sys.exit(1)
    
    print("🚀 Starting ART Live Agent Assist Dashboard...")
    print(f"   App: {app_path}")
    print("\n💡 Make sure DATABRICKS_TOKEN is set:")
    print("   export DATABRICKS_TOKEN='your-token'")
    print("\n📖 Access the dashboard at: http://localhost:8520")
    print("\n" + "="*60 + "\n")
    
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path), "--server.port", "8520"])

