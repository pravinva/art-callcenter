#!/bin/bash
# Run the Unified Streamlit Dashboard
# Combines Agent, Supervisor, and Analytics dashboards in one app

# Activate the virtual environment
source venv/bin/activate

echo "🚀 Launching ART Unified Dashboard..."
echo "Access it at: http://localhost:8520"
echo ""
echo "Available Dashboards:"
echo "  🔴 Live Agent Assist"
echo "  👔 Supervisor Dashboard"
echo "  📈 Analytics Dashboard"
echo ""
echo "Press Ctrl+C to stop the dashboard."

streamlit run app/unified_dashboard.py --server.port 8520

