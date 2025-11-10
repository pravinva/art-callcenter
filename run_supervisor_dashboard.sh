#!/bin/bash
# Run the Streamlit Supervisor Dashboard
# This script ensures the virtual environment is active and runs the dashboard on port 8522

# Activate the virtual environment
source venv/bin/activate

echo "🚀 Launching ART Supervisor Dashboard..."
echo "Access it at: http://localhost:8522"
echo "Press Ctrl+C to stop the dashboard."

streamlit run app/supervisor_dashboard.py --server.port 8522

