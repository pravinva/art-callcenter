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
    )
])

# Callback: Update active calls dropdown
@app.callback(
    Output('call-selector', 'options'),
    Output('store-active-calls', 'data'),
    Input('interval-component', 'n_intervals'),
    State('store-active-calls', 'data'),
    prevent_initial_call=False
)
def update_active_calls(n_intervals, previous_calls_data):
    """Update active calls dropdown - only refresh if call list changed"""
    try:
        calls = get_active_calls()
        
        # Format options for dropdown
        options = []
        calls_data = []
        
        for call in calls:
            call_id = call[0]
            member_name = call[1]
            scenario = call[3]
            utterances = call[5] if len(call) > 5 else 0
            
            label = f"{member_name} ({call_id[-8:]})"
            options.append({"label": label, "value": call_id})
            calls_data.append({
                "call_id": call_id,
                "member_name": member_name,
                "scenario": scenario,
                "utterances": utterances
            })
        
        # Compare with previous data - only update if changed
        if previous_calls_data:
            previous_call_ids = {c.get('call_id') for c in previous_calls_data}
            current_call_ids = {c.get('call_id') for c in calls_data}
            
            # If call IDs are the same, prevent update
            if previous_call_ids == current_call_ids:
                raise PreventUpdate
        
        return options, calls_data
    except PreventUpdate:
        raise
    except Exception as e:
        print(f"Error fetching active calls: {e}")
        return [], []

# Callback: Restore selected call when returning to agent page
@app.callback(
    Output('call-selector', 'value'),
    Input('url', 'pathname'),
    State('store-selected-call-id', 'data'),
    prevent_initial_call=False
)
def restore_selected_call(pathname, stored_call_id):
    """Restore selected call when returning to agent page"""
    # Only restore on agent page (home page)
    if pathname == '/' or pathname == '/agent':
        if stored_call_id:
            return stored_call_id
    # Don't update dropdown on other pages - prevent update
    raise PreventUpdate

# Callback: Update call info display
@app.callback(
    Output('call-info-display', 'children'),
    Input('call-selector', 'value'),
    State('store-active-calls', 'data')
)
def update_call_info(selected_call_id, calls_data):
    """Update call info display"""
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
    Input('call-selector', 'value')
)
def update_selected_call_id(selected_call_id):
    """Update selected call ID in store"""
    return selected_call_id

# Callback: Update main content when call selected
@app.callback(
    Output('main-content', 'children'),
    Input('store-selected-call-id', 'data'),
    Input('url', 'pathname')
)
def update_main_content(selected_call_id, pathname):
    """Update main content area when call is selected - sidebar stays visible"""
    # Only update on agent page
    if pathname != '/' and pathname != '/agent':
        return html.Div()
    
    if not selected_call_id:
        return html.H4("Select a call from the sidebar to begin")
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H4(f"Call {selected_call_id[-8:]}"),
                html.Div(id="transcript-display")
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
                ], id="ai-tabs", active_tab="suggestions"),
                
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
    Input('url', 'pathname'),
    Input('store-selected-call-id', 'data'),
    Input('interval-component', 'n_intervals'),
    State('store-last-rendered-call-id', 'data'),
    State('store-transcript-data', 'data'),
    prevent_initial_call=True
)
def update_transcript(pathname, selected_call_id, n_intervals, last_call_id, previous_transcript_data):
    """Fetch and display transcript - only refresh when call changes or new data detected"""
    if pathname != '/' and pathname != '/agent':
        raise PreventUpdate
    
    if not selected_call_id:
        raise PreventUpdate
    
    # Check if call ID changed
    call_id_changed = (selected_call_id != last_call_id)
    
    # If call ID changed, always fetch
    if call_id_changed:
        try:
            transcript_df = get_live_transcript(selected_call_id)
            transcript_data = transcript_df.to_dict('records') if transcript_df is not None and not transcript_df.empty else []
            display = TranscriptContainer(transcript_df) if transcript_df is not None and not transcript_df.empty else html.Div("No transcript available")
            return display, transcript_data
        except Exception as e:
            return ErrorAlert(f"Error loading transcript: {e}"), None
    
    # If call ID hasn't changed, check if transcript data has changed
    # Compare current transcript count with previous
    try:
        current_transcript_df = get_live_transcript(selected_call_id)
        current_count = len(current_transcript_df) if current_transcript_df is not None and not current_transcript_df.empty else 0
        previous_count = len(previous_transcript_data) if previous_transcript_data else 0
        
        # Only update if transcript has new data (more rows)
        if current_count > previous_count:
            transcript_data = current_transcript_df.to_dict('records') if current_transcript_df is not None and not current_transcript_df.empty else []
            display = TranscriptContainer(current_transcript_df) if current_transcript_df is not None and not current_transcript_df.empty else html.Div("No transcript available")
            return display, transcript_data
        else:
            # No new data - prevent update to avoid refreshing
            raise PreventUpdate
    except PreventUpdate:
        raise
    except Exception as e:
        return ErrorAlert(f"Error loading transcript: {e}"), None

# Callback: Update last rendered call ID
@app.callback(
    Output('store-last-rendered-call-id', 'data'),
    Input('store-selected-call-id', 'data')
)
def update_last_rendered_call_id(selected_call_id):
    """Track last rendered call ID for caching"""
    return selected_call_id

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
    if not selected_call_id or n_clicks == 0:
        return html.Div(), suggestion_state, None
    
    if suggestion_state is None:
        suggestion_state = {
            'loading': False,
            'error': None,
            'suggestion_text': None,
            'formatted_html': None,
            'response_time': None,
            'call_id': None
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
        
        if heuristic:
            # Show heuristic immediately
            suggestion_state['suggestion_text'] = heuristic
            suggestion_state['call_id'] = selected_call_id
            suggestion_state['loading'] = False
            
            card = create_suggestion_card(heuristic, is_heuristic=True)
            return card, suggestion_state, heuristic
        
        # Get full AI suggestion (force LLM call, don't use heuristic)
        # This will take time, so loading indicator will show
        suggestion, response_time, timing = get_ai_suggestion_async(selected_call_id, use_heuristic=False)
        
        suggestion_state['suggestion_text'] = suggestion
        suggestion_state['response_time'] = response_time
        suggestion_state['call_id'] = selected_call_id
        suggestion_state['loading'] = False
        
        card = create_suggestion_card(suggestion, response_time=response_time)
        return card, suggestion_state, None
        
    except Exception as e:
        suggestion_state['error'] = str(e)
        suggestion_state['loading'] = False
        return ErrorAlert(f"Error getting suggestion: {e}"), suggestion_state, None

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
    prevent_initial_call=True
)
def update_kb_tab_content(selected_call_id, active_tab):
    """Update KB tab content when tab is active"""
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
        
        return html.Div([
            html.H6("💡 Suggested Questions:", className="mb-2"),
            dbc.RadioItems(
                id="kb-question-radio",
                options=radio_options,
                value=None,
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
            html.Div(id="kb-results-display", className="mt-3")
        ])
    except Exception as e:
        return ErrorAlert(f"Error loading KB: {e}")

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

# Callback: Track active tab (Phase 8)
@app.callback(
    Output('store-active-tab', 'data'),
    Input('ai-tabs', 'active_tab')
)
def update_active_tab(active_tab):
    """Track which tab is active"""
    return active_tab

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

# Register page callbacks (only if pages are imported successfully)
try:
    register_supervisor_callbacks(app)
    register_analytics_callbacks(app)
except NameError:
    # Pages not imported - skip callback registration
    pass

if __name__ == '__main__':
    app.run(debug=False, port=8050, host='127.0.0.1')
