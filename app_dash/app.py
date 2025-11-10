#!/usr/bin/env python3
"""
ART Call Center - Dash Application
Main application entry point

Run: python app_dash/app.py
"""
import dash
from dash import html, dcc, Input, Output, State, callback_context
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
            
            /* Header styling - ART Brand */
            .header-container {
                background: linear-gradient(135deg, #0051FF 0%, #3385FF 100%);
                padding: 2rem 2.5rem;
                color: white;
                margin-bottom: 0;
                box-shadow: 0 2px 8px rgba(0, 81, 255, 0.15);
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
            
            /* Dropdowns - ART Style */
            .Select-control, .Select-menu-outer {
                font-family: 'Montserrat', sans-serif;
                font-size: 0.95rem;
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
            
            /* Transcript bubbles - ART Style */
            .transcript-bubble {
                font-family: 'Montserrat', sans-serif;
                font-size: 0.95rem;
                line-height: 1.6;
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
    """Create application header"""
    logo_path = Path(__file__).parent.parent / "logo.svg"
    assets_logo_path = Path(__file__).parent / "assets" / "logo.svg"
    
    # Ensure assets folder exists and logo is copied
    assets_dir = Path(__file__).parent / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    # Copy logo to assets if not already there or if root logo is newer
    if logo_path.exists():
        if not assets_logo_path.exists() or logo_path.stat().st_mtime > assets_logo_path.stat().st_mtime:
            import shutil
            shutil.copy(logo_path, assets_logo_path)
    
    # Check if logo exists
    logo_exists = assets_logo_path.exists()
    
    # Try multiple approaches for logo display
    logo_img = None
    if logo_exists:
        # Method 1: Use assets folder (Dash default)
        logo_src = "/assets/logo.svg"
        
        # Also try embedding as data URI as fallback
        try:
            import base64
            with open(assets_logo_path, 'rb') as f:
                svg_data = f.read()
            svg_base64 = base64.b64encode(svg_data).decode('utf-8')
            data_uri = f'data:image/svg+xml;base64,{svg_base64}'
            # Use data URI for more reliable display
            logo_img = html.Img(
                src=data_uri,
                style={
                    "height": "50px", 
                    "marginRight": "1rem",
                    "maxWidth": "200px",
                    "objectFit": "contain"
                },
                alt="ART Logo"
            )
        except Exception as e:
            print(f"Error creating data URI logo: {e}")
            # Fallback to regular path
            logo_img = html.Img(
                src=logo_src,
                style={
                    "height": "50px", 
                    "marginRight": "1rem",
                    "maxWidth": "200px",
                    "objectFit": "contain"
                },
                alt="ART Logo"
            )
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                logo_img if logo_img else html.Div(),
                html.H2("ART Live Agent Assist", style={
                    "color": "white", 
                    "margin": 0,
                    "fontFamily": "'Montserrat', sans-serif",
                    "fontWeight": "700",
                    "fontSize": "1.75rem",
                    "letterSpacing": "-0.01em"
                })
            ], width="auto"),
            dbc.Col([
                StatusIndicator(is_online=True)
            ], width="auto", className="ms-auto")
        ], align="center")
    ], className="header-container")

# Sidebar component
def create_sidebar():
    """Create sidebar with call selection - persistent sidebar (not Offcanvas)"""
    return html.Div([
        html.H3("📞 Active Calls", className="mb-3"),
        
        # Call selection dropdown
        dcc.Dropdown(
            id="call-selector",
            placeholder="Select a call to monitor...",
            style={"marginBottom": "1rem"}
        ),
        
        # Call info display
        html.Div(id="call-info-display"),
        
        html.Hr(),
        
        StatusIndicator(is_online=True),
        
        html.Hr(),
        
        html.Div([
            html.P("System Online", style={"margin": 0})
        ])
    ], style={
        "padding": "1.5rem",
        "backgroundColor": "#FFFFFF",
        "borderRight": "1px solid #E0E0E0",
        "height": "100%",
        "minHeight": "calc(100vh - 200px)"
    })

# Main layout
app.layout = html.Div([
    # URL routing
    dcc.Location(id='url', refresh=False),
    
    # State stores
    *state_manager.create_stores(),
    
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
    prevent_initial_call=False
)
def update_active_calls(n_intervals):
    """Update active calls dropdown"""
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
        
        return options, calls_data
    except Exception as e:
        print(f"Error fetching active calls: {e}")
        return [], []

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
    prevent_initial_call=True
)
def update_main_content(selected_call_id):
    """Update main content area when call is selected - sidebar stays visible"""
    if not selected_call_id:
        return html.H4("Select a call from the sidebar to begin")
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H4(f"📞 Live Call: {selected_call_id[-8:]}"),
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
                        html.Div(id="suggestion-display")
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
    State('store-kb-interaction', 'data'),
    prevent_initial_call=True
)
def update_transcript(pathname, selected_call_id, n_intervals, last_call_id, kb_interaction):
    """Fetch and display transcript"""
    if pathname != '/' and pathname != '/agent':
        return html.Div(), None
    
    if not selected_call_id:
        return html.Div(), None
    
    # Check if we should use cache
    call_id_changed = (selected_call_id != last_call_id)
    should_fetch = call_id_changed or not kb_interaction
    
    try:
        if should_fetch:
            transcript_df = get_live_transcript(selected_call_id)
            transcript_data = transcript_df.to_dict('records') if transcript_df is not None and not transcript_df.empty else []
            
            display = TranscriptContainer(transcript_df) if transcript_df is not None and not transcript_df.empty else html.Div("No transcript available")
            
            return display, transcript_data
        else:
            # Use cached data
            return html.Div("Loading transcript..."), None
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

# Callback: Get AI suggestion
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
    """Get AI suggestion when button is clicked"""
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
    
    try:
        # Get heuristic suggestion first (instant)
        heuristic = get_heuristic_suggestion(selected_call_id)
        
        if heuristic:
            # Show heuristic immediately
            suggestion_state['suggestion_text'] = heuristic
            suggestion_state['call_id'] = selected_call_id
            suggestion_state['loading'] = False
            
            card = create_suggestion_card(heuristic, is_heuristic=True)
            return card, suggestion_state, heuristic
        
        # Get full AI suggestion (async - placeholder for now)
        suggestion, response_time, timing = get_ai_suggestion_async(selected_call_id)
        
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
            dcc.Input(
                id="kb-manual-search",
                type="text",
                placeholder="Type your question here...",
                style={"width": "100%"}
            ),
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
    State('kb-manual-search', 'value'),
    State('store-kb-selected-question', 'data'),
    prevent_initial_call=True
)
def search_kb(radio_value, n_submit, manual_query, last_selected):
    """Search KB when question selected or manual search"""
    # Determine which triggered
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    search_query = None
    
    if triggered_id == 'kb-question-radio' and radio_value:
        search_query = radio_value
    elif triggered_id == 'kb-manual-search' and manual_query:
        search_query = manual_query
    
    if not search_query:
        return html.Div(), [], None, None, False
    
    try:
        # Mark KB interaction
        kb_interaction = True
        
        # Search KB
        articles = search_kb_vector_search(search_query, num_results=5)
        
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
        return ErrorAlert(f"Error searching KB: {e}"), [], None, None, False

# Callback: Update Compliance alerts (Phase 7)
@app.callback(
    Output('compliance-display', 'children'),
    Input('store-selected-call-id', 'data'),
    Input('interval-component', 'n_intervals'),
    prevent_initial_call=True
)
def update_compliance_alerts(selected_call_id, n_intervals):
    """Update compliance alerts display"""
    if not selected_call_id:
        return html.Div()
    
    try:
        alerts = get_compliance_alerts(selected_call_id)
        return create_compliance_alerts_display(alerts)
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
                # Sidebar column
                dbc.Col([
                    create_sidebar()
                ], width=3),
                
                # Main content column
                dbc.Col([
                    html.Div(id="main-content", children=[
                        html.H4("Select a call from the sidebar to begin")
                    ])
                ], width=9)
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
