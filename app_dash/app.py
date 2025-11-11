#!/usr/bin/env python3
"""
ART Call Center - Dash Application
Main application entry point

Run: python app_dash/app.py
"""
import dash
from dash import html, dcc, Input, Output, State
from dash import callback_context
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import utilities
from app_dash.utils.state_manager import StateManager
from app_dash.utils.data_fetchers import get_active_calls, get_live_transcript, get_call_context, get_compliance_alerts
from app_dash.utils.ai_suggestions import get_heuristic_suggestion, get_ai_suggestion_async
from app_dash.utils.kb_search import get_suggested_kb_questions, search_kb_vector_search
from app_dash.components.common import StatusIndicator, ErrorAlert
from app_dash.components.transcript import TranscriptContainer
from app_dash.components.ai_suggestions import create_suggestion_card
from app_dash.components.member_info import create_member_info_display
from app_dash.components.kb_search import create_kb_results_display
from app_dash.components.compliance import create_compliance_alerts_display

# Import page layouts
from app_dash.pages.supervisor import create_supervisor_layout, register_supervisor_callbacks
from app_dash.pages.analytics import create_analytics_layout, register_analytics_callbacks

# ART Brand Colors
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

# Initialize Dash app with Bootstrap theme
# Using Montserrat (ART website style) - available on Google Fonts
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap"
    ],
    suppress_callback_exceptions=True  # Allow dynamic callbacks
)

# App title
app.title = "ART Live Agent Assist"

# Initialize state manager
state_manager = StateManager()

# Custom CSS - Australian Retirement Trust Branding
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Australian Retirement Trust Brand Colors */
            :root {
                --art-primary-blue: #0051FF;
                --art-dark-blue: #0033CC;
                --art-light-blue: #E6F0FF;
                --art-accent-blue: #3385FF;
                --art-text-dark: #1A1A1A;
                --art-text-gray: #666666;
                --art-text-light-gray: #999999;
                --art-bg-light: #F8F9FA;
                --art-bg-white: #FFFFFF;
                --art-border: #E0E0E0;
                --art-white: #FFFFFF;
                --art-success: #00A651;
                --art-warning: #FF6B35;
                --art-error: #DC3545;
            }
            
            /* Typography - ART Website Style */
            * {
                font-family: 'Montserrat', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }
            
            body {
                font-family: 'Montserrat', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                font-weight: 400;
                font-size: 16px;
                line-height: 1.6;
                color: var(--art-text-dark);
                background-color: var(--art-bg-light);
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }
            
            /* Headings - Montserrat with proper weights */
            h1, h2, h3, h4, h5, h6 {
                font-family: 'Montserrat', 'Inter', sans-serif;
                font-weight: 700;
                color: var(--art-text-dark);
                line-height: 1.3;
                margin-bottom: 1rem;
            }
            
            h1 {
                font-size: 2.5rem;
                font-weight: 800;
                letter-spacing: -0.02em;
            }
            
            h2 {
                font-size: 2rem;
                font-weight: 700;
                letter-spacing: -0.01em;
            }
            
            h3 {
                font-size: 1.5rem;
                font-weight: 600;
            }
            
            h4 {
                font-size: 1.25rem;
                font-weight: 600;
            }
            
            /* Dropdown menu styling - show more options */
            .Select-menu-outer {
                max-height: 600px !important;
                z-index: 9999 !important;
            }
            
            .Select-menu {
                max-height: 600px !important;
            }
            
            .Select-option {
                padding: 8px 12px !important;
            }
            
            /* Header styling - ART Brand */
            .header-container {
                background: linear-gradient(135deg, #0051FF 0%, #3385FF 100%);
                padding: 1.5rem 2.5rem;
                color: white;
                margin-bottom: 0;
                box-shadow: 0 2px 8px rgba(0, 81, 255, 0.15);
                width: 100%;
            }
            
            .header-container img {
                display: inline-block !important;
                visibility: visible !important;
                opacity: 1 !important;
                height: 50px !important;
                max-height: 50px !important;
                max-width: 200px !important;
                width: auto !important;
                object-fit: contain !important;
            }
            
            .header-container h2 {
                color: white;
                font-weight: 700;
                font-size: 1.75rem;
                letter-spacing: -0.01em;
            }
            
            /* Navigation - ART Style */
            .navbar {
                font-family: 'Montserrat', sans-serif;
                font-weight: 500;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
            }
            
            .navbar-brand {
                font-weight: 700;
                font-size: 1.25rem;
            }
            
            .nav-link {
                font-weight: 500;
                font-size: 0.95rem;
            }
            
            /* Buttons - ART Style */
            .btn {
                font-family: 'Montserrat', sans-serif;
                font-weight: 600;
                border-radius: 8px;
                padding: 0.625rem 1.5rem;
                font-size: 0.95rem;
                transition: all 0.2s ease;
            }
            
            .btn-primary {
                background-color: var(--art-primary-blue);
                border-color: var(--art-primary-blue);
            }
            
            .btn-primary:hover {
                background-color: var(--art-dark-blue);
                border-color: var(--art-dark-blue);
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(0, 81, 255, 0.2);
            }
            
            /* Cards - ART Style */
            .card {
                border-radius: 12px;
                border: 1px solid var(--art-border);
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                font-family: 'Montserrat', sans-serif;
            }
            
            .card-header {
                font-weight: 600;
                font-size: 1.1rem;
                background-color: var(--art-bg-white);
                border-bottom: 1px solid var(--art-border);
            }
            
            /* Tables - ART Style */
            table {
                font-family: 'Montserrat', sans-serif;
                font-size: 0.95rem;
            }
            
            th {
                font-weight: 600;
                color: var(--art-text-dark);
            }
            
            /* Form elements - ART Style */
            .form-control, .form-select {
                font-family: 'Montserrat', sans-serif;
                border-radius: 8px;
                border: 1.5px solid var(--art-border);
                padding: 0.625rem 1rem;
                font-size: 0.95rem;
            }
            
            .form-control:focus, .form-select:focus {
                border-color: var(--art-primary-blue);
                box-shadow: 0 0 0 3px rgba(0, 81, 255, 0.1);
            }
            
            /* Dropdowns - ART Style - Reduced font size */
            .Select-control, .Select-menu-outer {
                font-family: 'Montserrat', sans-serif;
                font-size: 0.8rem !important;
            }
            
            /* Dropdown options - prevent overlap */
            .Select-option {
                font-size: 0.8rem !important;
                padding: 0.4rem 0.6rem !important;
                white-space: nowrap !important;
                overflow: hidden !important;
                text-overflow: ellipsis !important;
            }
            
            /* Color dropdown options - styled via JavaScript and CSS */
            /* CSS fallback for react-select options */
            .Select-option {
                position: relative;
            }
            
            /* Try to style based on text content using CSS (limited support) */
            .Select-option:not([style*="color"]) {
                /* Default styling - will be overridden by JS */
            }
            
            /* Selected value in dropdown */
            .Select-value-label {
                font-size: 0.8rem !important;
                white-space: nowrap !important;
                overflow: hidden !important;
                text-overflow: ellipsis !important;
            }
            
            /* Dropdown input */
            .Select-input {
                font-size: 0.8rem !important;
            }
            
            /* Alerts - ART Style */
            .alert {
                border-radius: 8px;
                font-family: 'Montserrat', sans-serif;
                font-weight: 500;
            }
            
            /* Sidebar - ART Style */
            .sidebar {
                font-family: 'Montserrat', sans-serif;
            }
            
            /* Sidebar logo styling */
            .sidebar img {
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
                height: 60px !important;
                max-width: 100% !important;
                width: auto !important;
                object-fit: contain !important;
                background-color: #FFFFFF !important;
            }
            
            /* Sidebar logo container */
            .sidebar-logo-container {
                background-color: #FFFFFF !important;
                padding: 0.5rem !important;
                border-radius: 4px !important;
                margin-top: 1rem !important;
            }
            
            /* Links - ART Style */
            a {
                color: var(--art-primary-blue);
                text-decoration: none;
                font-weight: 500;
                transition: color 0.2s ease;
            }
            
            a:hover {
                color: var(--art-dark-blue);
                text-decoration: underline;
            }
            
            /* Text styles */
            .text-muted {
                color: var(--art-text-gray) !important;
                font-weight: 400;
            }
            
            strong {
                font-weight: 600;
            }
            
            /* Spacing adjustments */
            .mb-3 {
                margin-bottom: 1.5rem !important;
            }
            
            .mb-4 {
                margin-bottom: 2rem !important;
            }
            
            /* Responsive typography */
            @media (max-width: 768px) {
                h1 {
                    font-size: 2rem;
                }
                
                h2 {
                    font-size: 1.75rem;
                }
                
                body {
                    font-size: 15px;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Header component
def create_header():
    """Create application header with logo prominently displayed"""
    # Use logo.png instead of logo.svg
    import os
    project_root = Path(__file__).parent.parent.absolute()
    logo_path = project_root / "logo.png"
    assets_logo_path = Path(__file__).parent / "assets" / "logo.png"
    
    # Also try absolute path directly
    absolute_logo_path = Path("/Users/pravin.varma/Documents/Demo/art-callcenter/logo.png")
    
    # Use absolute path if it exists, otherwise use relative
    if absolute_logo_path.exists():
        logo_path = absolute_logo_path
        print(f"✅ Using absolute logo path: {logo_path}")
    elif logo_path.exists():
        print(f"✅ Using relative logo path: {logo_path}")
    else:
        print(f"⚠️ Logo not found at: {logo_path}")
        print(f"⚠️ Absolute path also not found: {absolute_logo_path}")
    
    # Ensure assets folder exists and logo is copied
    assets_dir = Path(__file__).parent / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    # Copy logo to assets if not already there or if root logo is newer
    if logo_path.exists():
        if not assets_logo_path.exists() or logo_path.stat().st_mtime > assets_logo_path.stat().st_mtime:
            import shutil
            shutil.copy(logo_path, assets_logo_path)
            print(f"✅ Copied logo.png to assets: {assets_logo_path}")
    
    # Check if logo exists
    logo_exists = assets_logo_path.exists()
    
    # Debug: Print logo status
    if logo_exists:
        print(f"✅ Logo found: {assets_logo_path} ({assets_logo_path.stat().st_size} bytes)")
    else:
        print(f"⚠️ Logo not found at: {assets_logo_path}")
        if logo_path.exists():
            print(f"   Root logo exists: {logo_path}")
    
    # Create logo image - use direct assets path (Dash serves /assets/ automatically)
    logo_img = None
    if logo_exists:
        logo_src = "/assets/logo.png"
        logo_img = html.Img(
            src=logo_src,
            style={
                "height": "50px", 
                "width": "auto",
                "maxHeight": "50px",
                "maxWidth": "200px",
                "objectFit": "contain",
                "display": "inline-block",
                "verticalAlign": "middle",
                "marginRight": "1.5rem"
            },
            alt="Australian Retirement Trust Logo"
        )
        print(f"✅ Logo image created using: {logo_src} (sized: 50px height, max 200px width)")
    
    # Header content - no logo, just title
    header_content = [
        html.H2("ART Live Agent Assist", style={
            "color": "white", 
            "margin": 0,
            "fontFamily": "'Montserrat', sans-serif",
            "fontWeight": "700",
            "fontSize": "1.75rem",
            "letterSpacing": "-0.01em",
            "display": "inline-block",
            "verticalAlign": "middle"
        })
    ]
    
    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div(
                        header_content,
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "flexWrap": "wrap"
                        }
                    )
                ], width="auto"),
                dbc.Col([
                    StatusIndicator(is_online=True)
                ], width="auto", className="ms-auto")
            ], align="center", className="g-0")
        ], fluid=True)
    ], className="header-container", style={"width": "100%"})

# Sidebar component
def create_sidebar():
    """Create sidebar with call selection - persistent sidebar (not Offcanvas)"""
    # Get logo for sidebar - use SVG
    logo_path = Path(__file__).parent.parent / "logo.svg"
    assets_logo_path = Path(__file__).parent / "assets" / "logo.svg"
    absolute_logo_path = Path("/Users/pravin.varma/Documents/Demo/art-callcenter/logo.svg")
    
    # Use absolute path if it exists, otherwise use relative
    if absolute_logo_path.exists():
        logo_path = absolute_logo_path
    elif not logo_path.exists():
        logo_path = None
    
    # Ensure assets folder exists and logo is copied
    assets_dir = Path(__file__).parent / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    if logo_path and logo_path.exists():
        if not assets_logo_path.exists() or logo_path.stat().st_mtime > assets_logo_path.stat().st_mtime:
            import shutil
            shutil.copy(logo_path, assets_logo_path)
    
    # Create logo image for sidebar - left aligned, smaller
    sidebar_logo = None
    if assets_logo_path.exists():
        sidebar_logo = html.Div([
            html.Img(
                src="/assets/logo.svg",
                style={
                    "height": "60px",
                    "width": "auto",
                    "maxWidth": "100%",
                    "objectFit": "contain",
                    "display": "block",
                    "margin": "0 0 1rem 0",
                    "visibility": "visible",
                    "opacity": "1",
                    "backgroundColor": "#FFFFFF"
                },
                alt="ART Logo"
            )
        ], style={
            "backgroundColor": "#FFFFFF",
            "marginBottom": "1rem"
        })
        print(f"✅ Sidebar logo created: /assets/logo.svg (60px height, left-aligned)")
    else:
        print(f"⚠️ Sidebar logo not found at: {assets_logo_path}")
    
    return html.Div([
        # Toggle button at the top
        html.Div([
            dbc.Button(
                id="sidebar-toggle",
                children="☰" if True else "✕",  # Will be updated by callback
                color="light",
                size="sm",
                className="mb-2",
                style={
                    "width": "100%",
                    "textAlign": "center",
                    "border": "1px solid #E0E0E0"
                }
            )
        ], style={"marginBottom": "0.5rem"}),
        
        # Logo at the top, left-aligned
        html.Div(id="sidebar-content", children=[
            sidebar_logo if sidebar_logo else html.Div(),
            
            html.H3("📞 Active Calls", className="mb-3", style={"marginTop": "0"}),
            
            # Compliance legend
            html.Div([
                html.Small([
                    html.Span("🟢", style={"marginRight": "0.3rem"}),
                    html.Span("No compliance issues", style={"marginRight": "1rem", "color": "#00A651"}),
                    html.Span("🔴", style={"marginRight": "0.3rem"}),
                    html.Span("Compliance issues detected", style={"color": "#DC3545"})
                ], style={"fontSize": "0.75rem", "color": "#666666", "marginBottom": "0.5rem"})
            ], style={"marginBottom": "0.5rem", "padding": "0.5rem", "backgroundColor": "#F8F9FA", "borderRadius": "4px"}),
            
            # Call selection dropdown
            dcc.Dropdown(
                id="call-selector",
                placeholder="Select a call to monitor...",
                style={
                    "marginBottom": "1rem",
                    "fontSize": "0.8rem",
                    "zIndex": 1000
                },
                searchable=True,  # Enable search functionality
                clearable=True,  # Allow clearing selection
                multi=False
            ),
            
            # Call info display
            html.Div(id="call-info-display"),
            
            html.Hr(),
            
            StatusIndicator(is_online=True),
            
            html.Hr(),
            
            html.Div([
                html.P("System Online", style={"margin": 0})
            ])
        ])
    ], className="sidebar", style={
        "padding": "1rem",
        "backgroundColor": "#FFFFFF",
        "borderRight": "1px solid #E0E0E0",
        "height": "100%",
        "transition": "all 0.3s ease"
    })

# Main layout
app.layout = html.Div([
    # URL routing
    dcc.Location(id='url', refresh=False),
    
    # State stores
    *state_manager.create_stores(),
    dcc.Store(id='store-sidebar-expanded', data=True),  # Sidebar expanded by default
    
    # Header
    create_header(),
    
    # Navigation bar
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("📞 Live Agent", href="/", active="exact")),
            dbc.NavItem(dbc.NavLink("👔 Supervisor", href="/supervisor", active="exact")),
            dbc.NavItem(dbc.NavLink("📊 Analytics", href="/analytics", active="exact")),
        ],
        brand="ART Call Center",
        brand_href="/",
        color="primary",
        dark=True,
        className="mb-3"
    ),
    
    # Main content area - will be updated by routing callback
    html.Div(id="page-content"),
    
    # Interval for auto-refresh
    dcc.Interval(
        id='interval-component',
        interval=10*1000,  # 10 seconds
        n_intervals=0
    ),
    # Fast interval for enhanced AI suggestion fetching (2 seconds)
    dcc.Interval(
        id='enhanced-suggestion-interval',
        interval=2*1000,  # 2 seconds - faster check for enhanced suggestions
        n_intervals=0
    )
])

# Callback: Update active calls dropdown
@app.callback(
    Output('call-selector', 'options'),
    Output('store-active-calls', 'data'),
    Input('interval-component', 'n_intervals'),
    Input('url', 'pathname'),  # Add pathname to check if on agent page
    State('store-active-calls', 'data'),
    prevent_initial_call=False
)
def update_active_calls(n_intervals, pathname, previous_calls_data):
    """Update active calls dropdown - refresh when returning to agent page or on interval"""
    # Check which input triggered
    ctx = callback_context
    triggered_id = None
    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # If returning to agent page (pathname changed), always load calls
    if triggered_id == 'url' and pathname in ('/', '/agent'):
        # Force refresh when returning to agent page
        previous_calls_data = None
    
    # Only update if on agent page (where call-selector exists)
    if pathname != '/' and pathname != '/agent':
        raise PreventUpdate
    
    try:
        calls = get_active_calls()
        
        # Get compliance data for all calls efficiently
        call_ids = [call[0] for call in calls] if calls else []
        compliance_data = {}
        if call_ids:
            # Query compliance status for all calls at once
            from app_dash.utils.databricks_client import execute_sql
            from config.config import SQL_WAREHOUSE_ID, ENRICHED_TABLE
            call_ids_str = "', '".join(call_ids)
            compliance_query = f"""
            SELECT 
                call_id,
                SUM(CASE WHEN compliance_flag != 'ok' THEN 1 ELSE 0 END) as compliance_issues_count,
                SUM(CASE WHEN compliance_severity = 'CRITICAL' THEN 1 ELSE 0 END) as critical_count,
                SUM(CASE WHEN compliance_severity = 'HIGH' THEN 1 ELSE 0 END) as high_count
            FROM {ENRICHED_TABLE}
            WHERE call_id IN ('{call_ids_str}')
            GROUP BY call_id
            """
            compliance_results = execute_sql(compliance_query, SQL_WAREHOUSE_ID, return_dataframe=True)
            
            if compliance_results is not None and not compliance_results.empty:
                for _, row in compliance_results.iterrows():
                    call_id = row.get('call_id')
                    issues_count = int(row.get('compliance_issues_count', 0) or 0)
                    critical_count = int(row.get('critical_count', 0) or 0)
                    high_count = int(row.get('high_count', 0) or 0)
                    compliance_data[call_id] = {
                        'issues_count': issues_count,
                        'critical_count': critical_count,
                        'high_count': high_count,
                        'has_high_compliance': (issues_count > 0) or (critical_count > 0) or (high_count > 0)
                    }
        
        # Format options for dropdown with compliance indicators
        options = []
        calls_data = []
        
        for call in calls:
            call_id = call[0]
            member_name = call[1]
            scenario = call[3]
            # utterances is now at index 6 (after call_start and last_activity)
            utterances = call[6] if len(call) > 6 else (call[5] if len(call) > 5 else 0)
            
            # Get compliance status for this call
            compliance_info = compliance_data.get(call_id, {'has_high_compliance': False, 'issues_count': 0})
            has_compliance_issues = compliance_info.get('has_high_compliance', False)
            
            # Add visual indicator based on compliance status
            # Use HTML with inline styles for colored text
            if has_compliance_issues:
                # High compliance issues - use red indicator with colored text
                indicator = "🔴"
                # Use HTML span for colored text (Dash supports HTML in labels)
                label = html.Span([
                    html.Span("🔴 ", style={"color": "#DC3545", "fontWeight": "bold"}),
                    html.Span(f"{member_name} ({call_id[-8:]})", style={"color": "#DC3545"})
                ])
            else:
                # No compliance issues - use green indicator
                indicator = "🟢"
                # Use HTML span for colored text
                label = html.Span([
                    html.Span("🟢 ", style={"color": "#00A651", "fontWeight": "bold"}),
                    html.Span(f"{member_name} ({call_id[-8:]})", style={"color": "#00A651"})
                ])
            
            # Use plain text with emoji - JavaScript will add colors
            label_text = f"{indicator} {member_name} ({call_id[-8:]})"
            options.append({"label": label_text, "value": call_id})
            calls_data.append({
                "call_id": call_id,
                "member_name": member_name,
                "scenario": scenario,
                "utterances": utterances,
                "has_compliance_issues": has_compliance_issues,
                "compliance_issues_count": compliance_info.get('issues_count', 0)
            })
        
        # Compare with previous data - only update if changed
        # But always update if returning to agent page (triggered by pathname change)
        # Skip comparison if we're forcing a refresh (returning to page)
        if previous_calls_data and triggered_id != 'url':
            previous_call_ids = {c.get('call_id') for c in previous_calls_data}
            current_call_ids = {c.get('call_id') for c in calls_data}
            
            # If call IDs are the same and not returning to page, prevent update
            if previous_call_ids == current_call_ids:
                raise PreventUpdate
        
        # Always return options and data, even if empty (so restore callback can work)
        return options, calls_data
    except PreventUpdate:
        raise
    except Exception as e:
        print(f"Error fetching active calls: {e}")
        import traceback
        traceback.print_exc()
        return [], []

# Callback: Restore selected call when returning to agent page
@app.callback(
    Output('call-selector', 'value', allow_duplicate=True),
    Output('store-selected-call-id', 'data', allow_duplicate=True),
    Input('url', 'pathname'),
    Input('store-active-calls', 'data'),  # Also trigger when calls are loaded
    State('store-selected-call-id', 'data'),
    prevent_initial_call='initial_duplicate'  # Required for allow_duplicate
)
def restore_selected_call(pathname, calls_data, stored_call_id):
    """Restore selected call when returning to agent page"""
    # Only restore on agent page (home page) where call-selector exists
    if pathname == '/' or pathname == '/agent':
        # If calls_data is None or empty list, wait for calls to load
        # But if it's an empty list (not None), that means calls were loaded but empty
        if calls_data is None:
            # Calls not loaded yet, don't update dropdown
            raise PreventUpdate
        
        # Check if the stored call_id is still in the active calls list
        if stored_call_id:
            # If calls_data is empty list, check if stored call should still be valid
            if not calls_data:  # Empty list
                # No active calls, clear selection
                return None, None
            
            call_ids = [c.get('call_id') for c in calls_data]
            if stored_call_id in call_ids:
                # Restore both dropdown and store
                return stored_call_id, stored_call_id
            # Call not found in active list, clear selection
            return None, None
        
        # No stored call, don't update (let user select)
        raise PreventUpdate
    
    # Don't update dropdown on other pages - prevent update
    raise PreventUpdate

# Callback: Update call info display
@app.callback(
    Output('call-info-display', 'children'),
    Input('call-selector', 'value'),
    Input('url', 'pathname'),  # Add pathname to check if on agent page
    State('store-active-calls', 'data')
)
def update_call_info(selected_call_id, pathname, calls_data):
    """Update call info display - only on agent page"""
    # Only update if on agent page where call-info-display exists
    if pathname != '/' and pathname != '/agent':
        raise PreventUpdate
    
    if not selected_call_id or not calls_data:
        return html.Div()
    
    # Find selected call
    call_info = next((c for c in calls_data if c['call_id'] == selected_call_id), None)
    
    if not call_info:
        return html.Div()
    
    return html.Div([
        html.P([
            html.Strong("Member: "),
            call_info['member_name']
        ]),
        html.P([
            html.Strong("Scenario: "),
            call_info['scenario']
        ]),
        html.P([
            html.Strong("Utterances: "),
            str(call_info['utterances'])
        ])
    ])

# Callback: Update selected call ID store
@app.callback(
    Output('store-selected-call-id', 'data'),
    Input('call-selector', 'value'),
    Input('url', 'pathname'),  # Also listen to pathname
    State('store-selected-call-id', 'data'),  # Keep current value if dropdown is empty
    prevent_initial_call=False
)
def update_selected_call_id(selected_call_id, pathname, current_stored_id):
    """Update selected call ID in store - only when on agent page"""
    # Only update if on agent page where call-selector exists
    # Use callback_context to check which input triggered
    ctx = callback_context
    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        # If pathname changed and we're not on agent page, clear store
        if triggered_id == 'url' and pathname != '/' and pathname != '/agent':
            return None
        # If pathname changed to agent page, keep current stored value until dropdown restores
        if triggered_id == 'url' and pathname in ('/', '/agent'):
            # Don't clear the store when returning - let restore callback handle it
            return current_stored_id
        # If call-selector triggered but we're not on agent page, prevent update
        if triggered_id == 'call-selector' and pathname != '/' and pathname != '/agent':
            raise PreventUpdate
    
    # Update with new selection (or None if cleared)
    return selected_call_id

# Callback: Update main content when call selected
@app.callback(
    Output('main-content', 'children'),
    Input('store-selected-call-id', 'data'),
    Input('url', 'pathname')
)
def update_main_content(selected_call_id, pathname):
    """Update main content area when call is selected - sidebar stays visible"""
    # Check which input triggered
    ctx = callback_context
    triggered_id = None
    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Only update on agent page
    if pathname != '/' and pathname != '/agent':
        # If pathname changed away from agent page, prevent update
        if triggered_id == 'url':
            raise PreventUpdate
        return html.Div()
    
    # If returning to agent page, preserve the selected call
    # The transcript callback will handle restoring the transcript
    if not selected_call_id:
        return html.H4("Select a call from the sidebar to begin")
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H4(f"Call {selected_call_id[-8:]}"),
                dcc.Loading(
                    id="transcript-loading",
                    type="default",
                    children=html.Div(id="transcript-display"),
                    style={"minHeight": "200px"}
                )
            ], width=7),
            dbc.Col([
                html.H4("🤖 AI Assistant"),
                dbc.Tabs([
                    dbc.Tab([
                        html.Div(id="ai-suggestions-content"),
                        dbc.Button(
                            "🔄 Get AI Suggestion",
                            id="btn-get-suggestion",
                            color="primary",
                            className="mt-3 mb-3",
                            n_clicks=0
                        ),
                        dcc.Loading(
                            id="suggestion-loading",
                            type="default",
                            children=html.Div(id="suggestion-display"),
                            style={"minHeight": "100px"}
                        )
                    ], label="💡 Suggestions", tab_id="suggestions"),
                    dbc.Tab([
                        html.Div(id="member-info-content")
                    ], label="👤 Member Info", tab_id="member-info"),
                    dbc.Tab([
                        html.Div(id="kb-content")
                    ], label="📚 Knowledge Base", tab_id="kb")
                ], id="ai-tabs", active_tab="suggestions"),  # Will be updated by callback
                
                html.Hr(),
                
                html.H5("⚖️ Compliance Status"),
                html.Div(id="compliance-display")
            ], width=5)
        ])
    ])

# Callback: Fetch and display transcript (only on agent page)
@app.callback(
    Output('transcript-display', 'children'),
    Output('store-transcript-data', 'data'),
    Output('store-last-rendered-call-id', 'data'),  # Update this here to avoid race condition
    Input('url', 'pathname'),
    Input('store-selected-call-id', 'data'),
    Input('interval-component', 'n_intervals'),
    State('store-last-rendered-call-id', 'data'),
    State('store-transcript-data', 'data'),
    prevent_initial_call=False  # Changed to False so it loads immediately when call is selected
)
def update_transcript(pathname, selected_call_id, n_intervals, last_call_id, previous_transcript_data):
    """Fetch and display transcript - only refresh when call changes or new data detected"""
    if pathname != '/' and pathname != '/agent':
        raise PreventUpdate
    
    if not selected_call_id:
        # Show placeholder when no call selected
        return html.Div("Select a call to view transcript"), None, None
    
    # Check which input triggered the callback
    ctx = callback_context
    triggered_id = None
    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # If returning to agent page (pathname changed), restore transcript from store if available
    if triggered_id == 'url' and pathname in ('/', '/agent'):
        # Wait a moment for selected_call_id to be restored from dropdown
        # If we have stored transcript data, try to restore it
        if previous_transcript_data and selected_call_id and selected_call_id == last_call_id:
            # Restore from stored data
            # TranscriptContainer is imported at top level
            import pandas as pd
            try:
                transcript_df = pd.DataFrame(previous_transcript_data)
                display = TranscriptContainer(transcript_df) if transcript_df is not None and not transcript_df.empty else html.Div("No transcript available")
                return display, previous_transcript_data, last_call_id
            except Exception as e:
                # If restore fails, continue to fetch fresh data below
                print(f"Failed to restore transcript from store: {e}")
                pass
        
        # If we have a selected call but no stored data (or restore failed), fetch fresh data
        if selected_call_id:
            try:
                # TranscriptContainer is imported at top level
                transcript_df = get_live_transcript(selected_call_id)
                transcript_data = transcript_df.to_dict('records') if transcript_df is not None and not transcript_df.empty else []
                display = TranscriptContainer(transcript_df) if transcript_df is not None and not transcript_df.empty else html.Div("No transcript available")
                return display, transcript_data, selected_call_id
            except Exception as e:
                return ErrorAlert(f"Error loading transcript: {e}"), None, selected_call_id
        
        # If no call selected yet, check if we have a stored call_id that might be restored soon
        # Don't show placeholder immediately - wait for restore callback
        if not selected_call_id and last_call_id:
            # Call might be restoring, wait for it
            raise PreventUpdate
        
        # If no call selected and no last_call_id, show placeholder
        return html.Div("Select a call to view transcript"), None, None
    
    # Normal flow: Check if call ID changed (including initial load when last_call_id is None)
    call_id_changed = (selected_call_id != last_call_id) or (last_call_id is None)
    
    # If call ID changed, always fetch immediately
    if call_id_changed:
        try:
            # Clear cache for this call to ensure fresh data
            from app_dash.utils.data_fetchers import _cache_data, _cache_timestamps
            cache_key = f"transcript_{selected_call_id}"
            if cache_key in _cache_data:
                del _cache_data[cache_key]
            if cache_key in _cache_timestamps:
                del _cache_timestamps[cache_key]
            
            transcript_df = get_live_transcript(selected_call_id)
            transcript_data = transcript_df.to_dict('records') if transcript_df is not None and not transcript_df.empty else []
            # TranscriptContainer is imported at top level, use it directly
            display = TranscriptContainer(transcript_df) if transcript_df is not None and not transcript_df.empty else html.Div("No transcript available")
            # Update last_call_id immediately to prevent duplicate fetches
            return display, transcript_data, selected_call_id
        except Exception as e:
            return ErrorAlert(f"Error loading transcript: {e}"), None, selected_call_id
    
    # If call ID hasn't changed, check if transcript data has changed
    # Compare current transcript count with previous
    try:
        current_transcript_df = get_live_transcript(selected_call_id)
        current_count = len(current_transcript_df) if current_transcript_df is not None and not current_transcript_df.empty else 0
        previous_count = len(previous_transcript_data) if previous_transcript_data else 0
        
        # Only update if transcript has new data (more rows)
        if current_count > previous_count:
            transcript_data = current_transcript_df.to_dict('records') if current_transcript_df is not None and not current_transcript_df.empty else []
            # TranscriptContainer is imported at top level, use it directly
            display = TranscriptContainer(current_transcript_df) if current_transcript_df is not None and not current_transcript_df.empty else html.Div("No transcript available")
            return display, transcript_data, selected_call_id
        else:
            # No new data - prevent update to avoid refreshing
            raise PreventUpdate
    except PreventUpdate:
        raise
    except Exception as e:
        return ErrorAlert(f"Error loading transcript: {e}"), None, selected_call_id

# Callback: Update last rendered call ID (now handled in update_transcript to avoid race conditions)
# Keeping this for backward compatibility but it's now redundant
@app.callback(
    Output('store-last-rendered-call-id', 'data', allow_duplicate=True),
    Input('store-selected-call-id', 'data'),
    prevent_initial_call=True
)
def update_last_rendered_call_id(selected_call_id):
    """Track last rendered call ID for caching - now handled in update_transcript"""
    return selected_call_id

# Callback: Restore AI suggestion when returning to agent page
@app.callback(
    Output('suggestion-display', 'children', allow_duplicate=True),
    Input('url', 'pathname'),
    State('store-suggestion-state', 'data'),
    State('store-heuristic-suggestion', 'data'),
    prevent_initial_call=True
)
def restore_ai_suggestion(pathname, suggestion_state, heuristic_suggestion):
    """Restore AI suggestion when returning to agent page"""
    # Only restore on agent page
    if pathname not in ('/', '/agent'):
        raise PreventUpdate
    
    # Restore suggestion if available
    if suggestion_state and suggestion_state.get('suggestion_text'):
        from app_dash.components.ai_suggestions import create_suggestion_card
        suggestion_text = suggestion_state.get('suggestion_text')
        response_time = suggestion_state.get('response_time')
        is_heuristic = (heuristic_suggestion == suggestion_text)
        card = create_suggestion_card(suggestion_text, is_heuristic=is_heuristic, response_time=response_time)
        return card
    
    # Try heuristic if available
    if heuristic_suggestion:
        from app_dash.components.ai_suggestions import create_suggestion_card
        card = create_suggestion_card(heuristic_suggestion, is_heuristic=True)
        return card
    
    raise PreventUpdate

# Callback: Get AI suggestion with loading indicator
@app.callback(
    Output('suggestion-display', 'children'),
    Output('store-suggestion-state', 'data'),
    Output('store-heuristic-suggestion', 'data'),
    Input('btn-get-suggestion', 'n_clicks'),
    State('store-selected-call-id', 'data'),
    State('store-suggestion-state', 'data'),
    prevent_initial_call=True
)
def get_ai_suggestion(n_clicks, selected_call_id, suggestion_state):
    """Get AI suggestion when button is clicked - shows loading indicator"""
    print(f"\n{'='*60}")
    print(f"🔵 [CALLBACK TRIGGERED] get_ai_suggestion")
    print(f"   n_clicks: {n_clicks}")
    print(f"   selected_call_id: {selected_call_id}")
    print(f"   suggestion_state: {suggestion_state}")
    print(f"{'='*60}\n")
    
    if not selected_call_id or n_clicks == 0:
        print("⚠️ [CALLBACK] No call selected or button not clicked, returning empty")
        return html.Div(), suggestion_state, None
    
    if suggestion_state is None:
        suggestion_state = {
            'loading': False,
            'error': None,
            'suggestion_text': None,
            'formatted_html': None,
            'response_time': None,
            'call_id': None,
            'fetching_enhanced': False
        }
    
    # Set loading state immediately
    suggestion_state['loading'] = True
    
    try:
        # Show loading message immediately
        loading_display = dbc.Alert([
            html.Div([
                dbc.Spinner(size="sm", color="primary", spinner_class_name="me-2"),
                html.Span("Analyzing call context and generating AI suggestion...", style={"fontSize": "0.95rem"})
            ], style={"display": "flex", "alignItems": "center"})
        ], color="info", className="mb-3")
        
        # Get heuristic suggestion first (instant)
        heuristic = get_heuristic_suggestion(selected_call_id)
        print(f"🔍 [CALLBACK] Heuristic result: {heuristic[:100] if heuristic else 'None'}...")
        
        if heuristic:
            print(f"⚡ [CALLBACK] Heuristic found! Showing it and fetching enhanced...")
            # Show heuristic immediately, but also fetch enhanced AI suggestion
            suggestion_state['suggestion_text'] = heuristic
            suggestion_state['call_id'] = selected_call_id
            suggestion_state['loading'] = False
            suggestion_state['fetching_enhanced'] = True  # Flag to trigger enhanced fetch
            
            print(f"⚡ Showing heuristic suggestion, setting fetching_enhanced=True for call {selected_call_id}")
            
            # Create card with heuristic and add note that enhanced is loading
            card = create_suggestion_card(heuristic, is_heuristic=True)
            
            # Add a MORE VISIBLE note that enhanced suggestion is being fetched
            from dash import html as html_comp
            enhanced_loading_note = html_comp.Div([
                html_comp.Hr(),
                dbc.Alert([
                    html_comp.Div([
                        dbc.Spinner(size="sm", color="primary", spinner_class_name="me-2"),
                        html_comp.Strong("Fetching enhanced AI suggestion...", style={"fontSize": "1rem", "color": "#0051FF"})
                    ], style={"display": "flex", "alignItems": "center"}),
                    html_comp.Small("This may take a few seconds", className="text-muted mt-1")
                ], color="info", className="mt-2")
            ])
            
            # Combine card with loading note
            card_with_loading = html_comp.Div([card, enhanced_loading_note])
            
            # IMPORTANT: Fetch enhanced suggestion immediately in this callback
            # This ensures it happens right away, not waiting for another callback
            print(f"🔄 [CALLBACK] Starting enhanced AI suggestion fetch for call {selected_call_id}...")
            print(f"🔄 [CALLBACK] Current suggestion_state keys: {list(suggestion_state.keys())}")
            try:
                # Fetch enhanced AI suggestion (force LLM call, don't use heuristic)
                enhanced_suggestion, response_time, timing = get_ai_suggestion_async(selected_call_id, use_heuristic=False)
                
                print(f"✅ [CALLBACK] Enhanced AI suggestion received: {enhanced_suggestion[:100]}...")
                print(f"✅ [CALLBACK] Response time: {response_time}s")
                
                # Update suggestion state with enhanced suggestion
                suggestion_state['suggestion_text'] = enhanced_suggestion
                suggestion_state['response_time'] = response_time
                suggestion_state['fetching_enhanced'] = False
                
                # Create card with enhanced suggestion
                enhanced_card = create_suggestion_card(enhanced_suggestion, is_heuristic=False, response_time=response_time)
                
                print(f"✅ [CALLBACK] Returning enhanced card, replacing heuristic")
                # Return enhanced suggestion immediately
                return enhanced_card, suggestion_state, heuristic
            except Exception as e:
                # If enhanced fetch fails, return heuristic with error note
                print(f"❌ [CALLBACK] ERROR fetching enhanced suggestion: {e}")
                import traceback
                traceback.print_exc()
                suggestion_state['fetching_enhanced'] = False
                # Return heuristic card with loading note (enhanced failed)
                error_note = html_comp.Div([
                    html_comp.Hr(),
                    dbc.Alert([
                        html_comp.Strong("⚠️ Enhanced suggestion unavailable"),
                        html_comp.Br(),
                        html_comp.Small(f"Error: {str(e)[:100]}", className="text-muted")
                    ], color="warning", className="mt-2")
                ])
                card_with_error = html_comp.Div([card, error_note])
                return card_with_error, suggestion_state, heuristic
        
        # No heuristic available, get full AI suggestion (force LLM call)
        # This will take time, so loading indicator will show
        suggestion, response_time, timing = get_ai_suggestion_async(selected_call_id, use_heuristic=False)
        
        suggestion_state['suggestion_text'] = suggestion
        suggestion_state['response_time'] = response_time
        suggestion_state['call_id'] = selected_call_id
        suggestion_state['loading'] = False
        suggestion_state['fetching_enhanced'] = False
        
        card = create_suggestion_card(suggestion, response_time=response_time)
        return card, suggestion_state, None
        
    except Exception as e:
        suggestion_state['error'] = str(e)
        suggestion_state['loading'] = False
        suggestion_state['fetching_enhanced'] = False
        return ErrorAlert(f"Error getting suggestion: {e}"), suggestion_state, None

# Callback: Fetch enhanced AI suggestion after heuristic is shown
@app.callback(
    Output('suggestion-display', 'children', allow_duplicate=True),
    Output('store-suggestion-state', 'data', allow_duplicate=True),
    Input('store-suggestion-state', 'data'),
    Input('interval-component', 'n_intervals'),  # Also check on interval
    Input('enhanced-suggestion-interval', 'n_intervals'),  # Fast interval for enhanced suggestions
    State('store-selected-call-id', 'data'),
    prevent_initial_call=True
)
def fetch_enhanced_suggestion(suggestion_state, n_intervals, enhanced_n_intervals, selected_call_id):
    """Fetch enhanced AI suggestion when heuristic is shown"""
    # Check which input triggered
    ctx = callback_context
    triggered_id = None
    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if not suggestion_state or not selected_call_id:
        raise PreventUpdate
    
    # Only fetch if we're in the fetching_enhanced state
    if not suggestion_state.get('fetching_enhanced', False):
        raise PreventUpdate
    
    # Check if we already have an enhanced suggestion (not heuristic)
    # We can tell if it's heuristic by checking if response_time exists (enhanced suggestions have response_time)
    if suggestion_state.get('suggestion_text') and suggestion_state.get('response_time'):
        # Already have enhanced suggestion (has response_time from LLM)
        # Clear the fetching flag
        if suggestion_state.get('fetching_enhanced', False):
            suggestion_state['fetching_enhanced'] = False
        raise PreventUpdate
    
    try:
        print(f"🔄 Fetching enhanced AI suggestion for call {selected_call_id}... (triggered by {triggered_id})")
        # Fetch enhanced AI suggestion (force LLM call, don't use heuristic)
        suggestion, response_time, timing = get_ai_suggestion_async(selected_call_id, use_heuristic=False)
        
        print(f"✅ Enhanced AI suggestion received: {suggestion[:100]}...")
        
        # Update suggestion state with enhanced suggestion
        suggestion_state['suggestion_text'] = suggestion
        suggestion_state['response_time'] = response_time
        suggestion_state['fetching_enhanced'] = False
        
        # Create card with enhanced suggestion
        card = create_suggestion_card(suggestion, is_heuristic=False, response_time=response_time)
        
        return card, suggestion_state
        
    except Exception as e:
        # If enhanced fetch fails, keep heuristic and clear flag
        suggestion_state['fetching_enhanced'] = False
        print(f"❌ Error fetching enhanced suggestion: {e}")
        import traceback
        traceback.print_exc()
        # Don't update display, keep heuristic
        raise PreventUpdate

# Callback: Update Member Info tab (Phase 5)
@app.callback(
    Output('member-info-content', 'children'),
    Input('store-selected-call-id', 'data'),
    Input('ai-tabs', 'active_tab'),
    prevent_initial_call=True
)
def update_member_info(selected_call_id, active_tab):
    """Update member info when tab is active and call is selected"""
    if active_tab != 'member-info' or not selected_call_id:
        return html.Div()
    
    try:
        member_context = get_call_context(selected_call_id)
        if member_context:
            return create_member_info_display(member_context)
        else:
            return dbc.Alert("No member context available", color="info")
    except Exception as e:
        return ErrorAlert(f"Error loading member info: {e}")

# Callback: Update KB tab content (Phase 6)
@app.callback(
    Output('kb-content', 'children'),
    Input('store-selected-call-id', 'data'),
    Input('ai-tabs', 'active_tab'),
    Input('url', 'pathname'),  # Add pathname to restore when returning
    State('store-kb-selected-question', 'data'),
    prevent_initial_call=True
)
def update_kb_tab_content(selected_call_id, active_tab, pathname, stored_selected_question):
    """Update KB tab content when tab is active"""
    # Only on agent page
    if pathname != '/' and pathname != '/agent':
        raise PreventUpdate
    
    if active_tab != 'kb' or not selected_call_id:
        return html.Div()
    
    try:
        # Get suggested questions
        suggested_questions = get_suggested_kb_questions(selected_call_id)
        
        # Radio options
        radio_options = []
        for q in suggested_questions:
            radio_options.append({"label": q, "value": q})
        
        # Get sample question for placeholder (first suggested question)
        sample_question = suggested_questions[0] if suggested_questions else "Type your question here..."
        
        # Restore selected question if available
        radio_value = stored_selected_question if stored_selected_question in [q for q in suggested_questions] else None
        
        return html.Div([
            html.H6("💡 Suggested Questions:", className="mb-2"),
            dbc.RadioItems(
                id="kb-question-radio",
                options=radio_options,
                value=radio_value,  # Restore selected question
                className="mb-3"
            ) if radio_options else html.P("No suggestions available", className="text-muted"),
            html.Hr(),
            html.Label("Or search manually:", className="mb-2"),
            html.Small(
                f"💡 Sample question: \"{sample_question}\"",
                className="text-muted d-block mb-2",
                style={"fontStyle": "italic"}
            ),
            dbc.InputGroup([
                dcc.Input(
                    id="kb-manual-search",
                    type="text",
                    placeholder=sample_question if suggested_questions else "Type your question here...",
                    style={"width": "100%"}
                ),
                dbc.Button(
                    "🔍 Search",
                    id="kb-search-button",
                    color="primary",
                    n_clicks=0
                )
            ], className="mb-2"),
            dcc.Loading(
                id="kb-search-loading",
                type="default",
                children=html.Div(id="kb-results-display", className="mt-3"),
                style={"minHeight": "100px"}
            )
        ])
    except Exception as e:
        return ErrorAlert(f"Error loading KB: {e}")

# Callback: Restore KB results when returning to agent page
@app.callback(
    Output('kb-results-display', 'children', allow_duplicate=True),
    Input('url', 'pathname'),
    Input('ai-tabs', 'active_tab'),
    State('store-kb-results', 'data'),
    State('store-kb-query', 'data'),
    prevent_initial_call=True
)
def restore_kb_results(pathname, active_tab, stored_kb_results, stored_kb_query):
    """Restore KB results when returning to agent page and KB tab is active"""
    # Only restore on agent page when KB tab is active
    if pathname not in ('/', '/agent') or active_tab != 'kb':
        raise PreventUpdate
    
    # Restore results if available
    if stored_kb_results and stored_kb_query:
        from app_dash.components.kb_search import create_kb_results_display
        display = create_kb_results_display(stored_kb_results, stored_kb_query)
        return display
    
    raise PreventUpdate

# Callback: KB search when radio selected or manual search (Phase 6)
@app.callback(
    Output('kb-results-display', 'children'),
    Output('store-kb-results', 'data'),
    Output('store-kb-query', 'data'),
    Output('store-kb-selected-question', 'data'),
    Output('store-kb-interaction', 'data'),
    Input('kb-question-radio', 'value'),
    Input('kb-manual-search', 'n_submit'),
    Input('kb-search-button', 'n_clicks'),
    State('kb-manual-search', 'value'),
    State('store-kb-selected-question', 'data')
)
def search_kb(radio_value, n_submit, search_button_clicks, manual_query, last_selected):
    """Search KB when question selected or manual search"""
    # Determine which triggered
    try:
        ctx = callback_context
        if not ctx.triggered:
            return html.Div(), [], None, None, False
        
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        search_query = None
        
        # Check radio button selection
        if triggered_id == 'kb-question-radio' and radio_value:
            search_query = radio_value
        # Check manual search input
        elif triggered_id == 'kb-manual-search' and manual_query:
            search_query = manual_query
        # Check search button click
        elif triggered_id == 'kb-search-button' and manual_query:
            search_query = manual_query
        
        if not search_query:
            return html.Div(), [], None, None, False
        
        # Mark KB interaction
        kb_interaction = True
        
        print(f"🔍 Searching KB with query: {search_query}")
        
        # Search KB
        articles = search_kb_vector_search(search_query, num_results=5)
        
        print(f"✅ KB search returned {len(articles) if articles else 0} results")
        
        # Update stores
        results_data = articles
        query_data = search_query
        selected_question = search_query if triggered_id == 'kb-question-radio' else None
        
        # Display results
        if articles:
            display = create_kb_results_display(articles, search_query)
        else:
            display = dbc.Alert("No results found. Try rephrasing your question.", color="info")
        
        return display, results_data, query_data, selected_question, kb_interaction
    except Exception as e:
        print(f"❌ Error searching KB: {e}")
        import traceback
        traceback.print_exc()
        return ErrorAlert(f"Error searching KB: {str(e)}"), [], None, None, False

# Callback: Update Compliance alerts (Phase 7)
@app.callback(
    Output('compliance-display', 'children'),
    Input('store-selected-call-id', 'data'),
    Input('interval-component', 'n_intervals'),
    State('store-last-rendered-call-id', 'data'),
    State('store-transcript-data', 'data'),
    prevent_initial_call=True
)
def update_compliance_alerts(selected_call_id, n_intervals, last_call_id, transcript_data):
    """Update compliance alerts display - only refresh when call changes or transcript updates"""
    if not selected_call_id:
        raise PreventUpdate
    
    # Only refresh if call changed or transcript was updated (transcript_data indicates new data)
    call_id_changed = (selected_call_id != last_call_id)
    
    # If call hasn't changed and no transcript data (meaning transcript didn't update), prevent refresh
    if not call_id_changed and not transcript_data:
        raise PreventUpdate
    
    try:
        alerts = get_compliance_alerts(selected_call_id)
        return create_compliance_alerts_display(alerts)
    except PreventUpdate:
        raise
    except Exception as e:
        return ErrorAlert(f"Error loading compliance alerts: {e}")

# Callback: Track active tab
@app.callback(
    Output('store-active-tab', 'data'),
    Input('ai-tabs', 'active_tab')
)
def update_active_tab(active_tab):
    """Track which tab is active"""
    return active_tab

# Callback: Restore active tab when returning to agent page
@app.callback(
    Output('ai-tabs', 'active_tab', allow_duplicate=True),
    Input('url', 'pathname'),
    State('store-active-tab', 'data'),
    prevent_initial_call='initial_duplicate'
)
def restore_active_tab(pathname, stored_active_tab):
    """Restore active tab when returning to agent page"""
    # If returning to agent page, restore the stored tab
    if pathname in ('/', '/agent') and stored_active_tab:
        return stored_active_tab
    raise PreventUpdate

# Callback: Toggle sidebar expand/collapse
@app.callback(
    Output('store-sidebar-expanded', 'data'),
    Output('sidebar-toggle', 'children'),
    Output('sidebar-content', 'style'),
    Output('sidebar-col', 'width'),
    Output('main-content-col', 'width'),
    Input('sidebar-toggle', 'n_clicks'),
    State('store-sidebar-expanded', 'data'),
    prevent_initial_call=True
)
def toggle_sidebar(n_clicks, is_expanded):
    """Toggle sidebar expanded/collapsed state"""
    if n_clicks is None:
        is_expanded = True  # Default expanded
    else:
        is_expanded = not is_expanded
    
    if is_expanded:
        # Expanded state
        return (
            True,
            "☰",  # Hamburger icon
            {"display": "block"},  # Show content
            2,  # Sidebar width
            10  # Main content width
        )
    else:
        # Collapsed state
        return (
            False,
            "→",  # Arrow icon
            {"display": "none"},  # Hide content
            1,  # Narrow sidebar (just for toggle button)
            11  # Expanded main content
        )

# Callback: Update sidebar toggle button on page load
@app.callback(
    Output('sidebar-toggle', 'children', allow_duplicate=True),
    Output('sidebar-content', 'style', allow_duplicate=True),
    Output('sidebar-col', 'width', allow_duplicate=True),
    Output('main-content-col', 'width', allow_duplicate=True),
    Input('store-sidebar-expanded', 'data'),
    prevent_initial_call=True
)
def update_sidebar_on_load(is_expanded):
    """Update sidebar state on page load"""
    if is_expanded:
        return "☰", {"display": "block"}, 2, 10
    else:
        return "→", {"display": "none"}, 1, 11

# Routing callback - display different pages based on URL
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    """Route to different pages based on URL"""
    if pathname == '/supervisor':
        return create_supervisor_layout()
    elif pathname == '/analytics':
        return create_analytics_layout()
    else:
        # Default: Agent dashboard
        return dbc.Container([
            dbc.Row([
                # Sidebar column - dynamic width based on expanded state
                dbc.Col([
                    create_sidebar()
                ], id="sidebar-col", width=2),
                
                # Main content column - dynamic width based on sidebar state
                dbc.Col([
                    html.Div(id="main-content", children=[
                        html.H4("Select a call from the sidebar to begin")
                    ])
                ], id="main-content-col", width=10)
            ])
        ], fluid=True)

# Add JavaScript to color dropdown options (injected into the page)
# Get the original index_string first
original_index_string = app.index_string

app.index_string = original_index_string.replace(
    '</body>',
    '''
    <script>
    (function() {
        'use strict';
        
        // Function to color dropdown options - try multiple selectors
        function colorDropdownOptions() {
            try {
                // Try different selectors for Dash dropdown (react-select)
                var selectors = [
                    '.Select-option',
                    '.Select-menu-outer .Select-option',
                    '[class*="Select-option"]',
                    '[id="call-selector"] .Select-option',
                    '.dash-dropdown .Select-option',
                    'div[role="option"]'
                ];
                
                var options = [];
                selectors.forEach(function(selector) {
                    try {
                        var found = document.querySelectorAll(selector);
                        if (found && found.length > 0) {
                            for (var i = 0; i < found.length; i++) {
                                var opt = found[i];
                                // Check if already added
                                var alreadyAdded = false;
                                for (var j = 0; j < options.length; j++) {
                                    if (options[j] === opt) {
                                        alreadyAdded = true;
                                        break;
                                    }
                                }
                                if (!alreadyAdded) {
                                    options.push(opt);
                                }
                            }
                        }
                    } catch (e) {
                        // Silently skip invalid selectors
                    }
                });
                
                // Color each option
                options.forEach(function(option) {
                    try {
                        var text = (option.textContent || option.innerText || '').toString();
                        
                        if (text.indexOf('🔴') !== -1) {
                            option.style.color = '#DC3545';
                            option.style.borderLeft = '4px solid #DC3545';
                            option.style.backgroundColor = '#fff5f5';
                            option.style.fontWeight = '600';
                            option.style.paddingLeft = '0.5rem';
                        } else if (text.indexOf('🟢') !== -1) {
                            option.style.color = '#00A651';
                            option.style.borderLeft = '4px solid #00A651';
                            option.style.backgroundColor = '#f0fff4';
                            option.style.paddingLeft = '0.5rem';
                        }
                    } catch (e) {
                        // Skip options that can't be styled
                    }
                });
                
                // Color selected value - try multiple selectors
                var selectedSelectors = [
                    '.Select-value-label',
                    '[class*="Select-value-label"]',
                    '[id="call-selector"] .Select-value-label',
                    '.Select-value .Select-value-label'
                ];
                
                selectedSelectors.forEach(function(selector) {
                    try {
                        var selectedLabel = document.querySelector(selector);
                        if (selectedLabel) {
                            var selectedText = (selectedLabel.textContent || selectedLabel.innerText || '').toString();
                            if (selectedText.indexOf('🔴') !== -1) {
                                selectedLabel.style.color = '#DC3545';
                                selectedLabel.style.fontWeight = '600';
                            } else if (selectedText.indexOf('🟢') !== -1) {
                                selectedLabel.style.color = '#00A651';
                            }
                        }
                    } catch (e) {
                        // Skip if selector fails
                    }
                });
            } catch (e) {
                // Silently handle errors
            }
        }
        
        // Run on page load
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                setTimeout(colorDropdownOptions, 500);
                setTimeout(colorDropdownOptions, 1500);
            });
        } else {
            setTimeout(colorDropdownOptions, 500);
            setTimeout(colorDropdownOptions, 1500);
        }
        
        // Run when dropdown opens - observe the entire document
        try {
            var observer = new MutationObserver(function(mutations) {
                var shouldRun = false;
                mutations.forEach(function(mutation) {
                    if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                        for (var i = 0; i < mutation.addedNodes.length; i++) {
                            var node = mutation.addedNodes[i];
                            if (node && node.nodeType === 1) { // Element node
                                if (node.classList && (
                                    node.classList.contains('Select-menu-outer') ||
                                    node.classList.contains('Select-menu')
                                )) {
                                    shouldRun = true;
                                } else if (node.querySelector && node.querySelector('.Select-option')) {
                                    shouldRun = true;
                                }
                            }
                        }
                    }
                });
                if (shouldRun) {
                    setTimeout(colorDropdownOptions, 50);
                }
            });
            
            // Observe the entire body for dropdown menu additions
            setTimeout(function() {
                if (document.body) {
                    observer.observe(document.body, { 
                        childList: true, 
                        subtree: true 
                    });
                }
            }, 1000);
        } catch (e) {
            // MutationObserver not supported, use fallback
        }
        
        // Also run periodically to catch updates
        setInterval(colorDropdownOptions, 2000);
        
        // Listen for click events on dropdown
        document.addEventListener('click', function(e) {
            try {
                var target = e.target;
                if (target && (
                    (target.id === 'call-selector') ||
                    (target.closest && (target.closest('#call-selector') || target.closest('.Select-control')))
                )) {
                    setTimeout(colorDropdownOptions, 200);
                }
            } catch (e) {
                // Ignore errors
            }
        });
    })();
    </script>
    </body>
    '''
)

# Register page callbacks (only if pages are imported successfully)
try:
    register_supervisor_callbacks(app)
    register_analytics_callbacks(app)
except NameError:
    # Pages not imported - skip callback registration
    pass

if __name__ == '__main__':
    app.run(debug=False, port=8050, host='127.0.0.1')
