#!/usr/bin/env python3
"""
ART Call Center - Unified Dashboard
Combines Live Agent Assist, Supervisor Dashboard, and Analytics in a single app
using modern Streamlit navigation (st.navigation with st.Page)

Run: streamlit run app/main_dashboard.py --server.port 8520
"""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Page config (must be first Streamlit command)
st.set_page_config(
    page_title="ART Call Center Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create Page objects from dashboard files
agent_page = st.Page(
    page=Path(__file__).parent / "agent_dashboard.py",
    title="🔴 Live Agent Assist",
    icon="📞"
)

supervisor_page = st.Page(
    page=Path(__file__).parent / "supervisor_dashboard.py",
    title="👔 Supervisor Dashboard",
    icon="👔"
)

analytics_page = st.Page(
    page=Path(__file__).parent / "analytics_dashboard.py",
    title="📈 Analytics Dashboard",
    icon="📊"
)

# Create navigation with pages
pg = st.navigation({
    "Agent Tools": [agent_page],
    "Supervisor Tools": [supervisor_page],
    "Analytics": [analytics_page],
})

# Run the selected page
pg.run()
