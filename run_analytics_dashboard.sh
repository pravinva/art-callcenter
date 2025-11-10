#!/bin/bash
# Run Analytics Dashboard
# Usage: ./run_analytics_dashboard.sh

cd "$(dirname "$0")/.."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run Streamlit dashboard
streamlit run app/analytics_dashboard.py --server.port 8521

