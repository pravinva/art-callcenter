"""
Testing Utilities for Dash Application
"""
import sys
from pathlib import Path

# Add parent directory to path (go up two levels from tests/)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_imports():
    """Test that all imports work correctly"""
    try:
        # Test utility imports
        from app_dash.utils.data_fetchers import get_active_calls
        from app_dash.utils.analytics_data import get_overview_metrics
        from app_dash.utils.supervisor_data import get_all_active_calls
        from app_dash.utils.kb_search import get_suggested_kb_questions
        from app_dash.utils.ai_suggestions import get_heuristic_suggestion
        
        # Test component imports
        from app_dash.components.common import ErrorAlert, StatusIndicator
        from app_dash.components.transcript import TranscriptContainer
        from app_dash.components.ai_suggestions import create_suggestion_card
        from app_dash.components.member_info import create_member_info_display
        from app_dash.components.kb_search import create_kb_results_display
        from app_dash.components.compliance import create_compliance_alerts_display
        from app_dash.components.analytics import create_overview_metrics
        from app_dash.components.supervisor import create_active_calls_list
        
        # Test page imports
        from app_dash.pages.analytics import create_analytics_layout, register_analytics_callbacks
        from app_dash.pages.supervisor import create_supervisor_layout, register_supervisor_callbacks
        
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_creation():
    """Test that the Dash app can be created"""
    try:
        import dash
        import dash_bootstrap_components as dbc
        from dash import html
        
        app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            suppress_callback_exceptions=True
        )
        
        app.layout = html.Div([html.H1("Test")])
        
        print("✅ App creation successful")
        return True
    except Exception as e:
        print(f"❌ App creation error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("Running Dash application tests...")
    print("\n1. Testing imports...")
    imports_ok = test_imports()
    
    print("\n2. Testing app creation...")
    app_ok = test_app_creation()
    
    if imports_ok and app_ok:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)

