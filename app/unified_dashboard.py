#!/usr/bin/env python3
"""
ART Call Center - Unified Dashboard
Combines Live Agent Assist, Supervisor Dashboard, and Analytics in a single app
using modern Streamlit navigation (st.navigation + st.Page)

Run: streamlit run app/unified_dashboard.py --server.port 8520
"""
import streamlit as st
import sys
from pathlib import Path
import importlib.util
import types

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Page configuration (only set once at top level)
st.set_page_config(
    page_title="ART Call Center Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ART Branding Colors
ART_PRIMARY_BLUE = "#0051FF"
ART_DARK_BLUE = "#0033CC"
ART_LIGHT_BLUE = "#E6F0FF"
ART_ACCENT_BLUE = "#3385FF"
ART_TEXT_DARK = "#1A1A1A"
ART_TEXT_GRAY = "#666666"
ART_BG_LIGHT = "#F8F9FA"
ART_BORDER = "#E0E0E0"
ART_WHITE = "#FFFFFF"
ART_SUCCESS_GREEN = "#00A651"
ART_WARNING_ORANGE = "#FF6B35"
ART_ERROR_RED = "#DC3545"

# Global CSS for unified dashboard
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .main {{
        background-color: {ART_BG_LIGHT};
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        max-width: 100% !important;
        padding: 0 2rem;
    }}
    
    .block-container {{
        max-width: 100% !important;
        padding-left: 2rem;
        padding-right: 2rem;
    }}
    
    /* Hide default Streamlit navigation */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Hide Streamlit's automatic page navigation sidebar */
    [data-testid="stSidebarNav"] {{
        display: none !important;
    }}
    
    /* Hide Streamlit's default page navigation that appears at top */
    section[data-testid="stSidebar"] > div:first-child > div:first-child > div:first-child {{
        display: none !important;
    }}
    
    /* Alternative selector for page navigation */
    div[data-testid="stSidebarNav"] {{
        display: none !important;
    }}
    
    /* Hide any navigation links that Streamlit auto-generates */
    nav[data-testid="stSidebarNav"] {{
        display: none !important;
    }}
    
    /* Hide Streamlit's page navigation that appears when multiple pages detected */
    ul[data-testid="stSidebarNav"] {{
        display: none !important;
    }}
    
    /* Hide any list-based navigation in sidebar */
    section[data-testid="stSidebar"] ul {{
        display: none !important;
    }}
    
    /* Hide navigation links */
    section[data-testid="stSidebar"] a[href*="Live_Agent_Assist"],
    section[data-testid="stSidebar"] a[href*="Analytics"] {{
        display: none !important;
    }}
</style>
""", unsafe_allow_html=True)

# Wrapper functions to load dashboards while patching st.set_page_config
def load_dashboard_module(dashboard_path):
    """Load a dashboard module while patching st.set_page_config to prevent conflicts"""
    # Store original
    original_set_page_config = st.set_page_config
    
    # Create a no-op version
    def noop_set_page_config(*args, **kwargs):
        pass
    
    # Patch it
    st.set_page_config = noop_set_page_config
    
    try:
        # Ensure parent directory is in path for config imports
        parent_dir = str(Path(__file__).parent.parent)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        # Pre-import config to ensure it's available
        import config.config
        
        # Load and execute the module
        spec = importlib.util.spec_from_file_location("dashboard_module", dashboard_path)
        module = types.ModuleType("dashboard_module")
        
        # Set __file__ before executing to avoid NameError
        # Use absolute path to ensure proper resolution
        module.__file__ = str(Path(dashboard_path).absolute())
        module.__name__ = spec.name
        
        # Set __package__ to help with relative imports
        module.__package__ = "app"
        
        spec.loader.exec_module(module)
        return module
    finally:
        # Restore original
        st.set_page_config = original_set_page_config

def agent_page():
    """Agent Dashboard Page"""
    dashboard_path = Path(__file__).parent / "agent_dashboard.py"
    load_dashboard_module(dashboard_path)

def supervisor_page():
    """Supervisor Dashboard Page"""
    dashboard_path = Path(__file__).parent / "supervisor_dashboard.py"
    load_dashboard_module(dashboard_path)

def analytics_page():
    """Analytics Dashboard Page"""
    dashboard_path = Path(__file__).parent / "analytics_dashboard.py"
    load_dashboard_module(dashboard_path)

# Use modern Streamlit navigation
try:
    # Modern approach: st.navigation + st.Page (Streamlit 1.28+)
    pages = {
        "🔴 Live Agent Assist": st.Page(
            agent_page,
            title="Live Agent Assist",
            icon="🔴"
        ),
        "👔 Supervisor Dashboard": st.Page(
            supervisor_page,
            title="Supervisor Dashboard",
            icon="👔"
        ),
        "📈 Analytics Dashboard": st.Page(
            analytics_page,
            title="Analytics Dashboard",
            icon="📈"
        )
    }
    
    # Add header to show this is the unified dashboard
    st.sidebar.markdown("## 📊 ART Call Center")
    st.sidebar.markdown("**Unified Dashboard**")
    st.sidebar.markdown("---")
    
    # Use navigation without showing default Streamlit page navigation
    pg = st.navigation(pages)
    pg.run()
    
except (AttributeError, TypeError) as e:
    # Fallback: Use sidebar selectbox for older Streamlit versions
    st.sidebar.title("📊 ART Call Center")
    st.sidebar.markdown("---")
    
    page = st.sidebar.selectbox(
        "Select Dashboard",
        ["🔴 Live Agent Assist", "👔 Supervisor Dashboard", "📈 Analytics Dashboard"],
        key="dashboard_selector"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    **Data Flow:**
    1. Bronze: Raw transcripts
    2. Silver: Real-time enrichment
    3. Live Assist: Agent dashboard
    4. Gold: Batch analytics
    5. Analytics: Visual insights
    """)
    
    if page == "🔴 Live Agent Assist":
        agent_page()
    elif page == "👔 Supervisor Dashboard":
        supervisor_page()
    elif page == "📈 Analytics Dashboard":
        analytics_page()
