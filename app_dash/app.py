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
from app_dash.utils.data_fetchers import get_active_calls, get_live_transcript
from app_dash.utils.ai_suggestions import get_heuristic_suggestion, get_ai_suggestion_async
from app_dash.components.common import StatusIndicator, ErrorAlert
from app_dash.components.transcript import TranscriptContainer
from app_dash.components.ai_suggestions import create_suggestion_card

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
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
    ],
    suppress_callback_exceptions=True  # Allow dynamic callbacks
)

# App title
app.title = "ART Live Agent Assist"

# Initialize state manager
state_manager = StateManager()

# Custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            :root {
                --art-primary-blue: #0051FF;
                --art-dark-blue: #0033CC;
                --art-light-blue: #E6F0FF;
                --art-accent-blue: #3385FF;
                --art-text-dark: #1A1A1A;
                --art-text-gray: #666666;
                --art-bg-light: #F8F9FA;
                --art-border: #E0E0E0;
                --art-white: #FFFFFF;
                --art-success: #00A651;
                --art-warning: #FF6B35;
                --art-error: #DC3545;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background-color: var(--art-bg-light);
            }
            
            .header-container {
                background: linear-gradient(135deg, #0051FF 0%, #3385FF 100%);
                padding: 2rem 2.5rem;
                color: white;
                margin-bottom: 2rem;
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
    logo_exists = logo_path.exists()
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Img(
                    src=f"/assets/{logo_path.name}" if logo_exists else "",
                    style={"height": "50px", "marginRight": "1rem"} if logo_exists else {"display": "none"}
                ),
                html.H2("ART Live Agent Assist", style={"color": "white", "margin": 0})
            ], width="auto"),
            dbc.Col([
                StatusIndicator(is_online=True)
            ], width="auto", className="ms-auto")
        ], align="center")
    ], className="header-container")

# Sidebar component
def create_sidebar():
    """Create sidebar with call selection"""
    return dbc.Offcanvas([
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
    ], id="sidebar", title="Call Selection", is_open=True, placement="start")

# Main layout
app.layout = html.Div([
    # State stores
    *state_manager.create_stores(),
    
    # Header
    create_header(),
    
    # Main content area
    dbc.Container([
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
    ], fluid=True),
    
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
    """Update main content area when call is selected"""
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
                        html.Div(id="ai-suggestions-content")
                    ], label="💡 Suggestions", tab_id="suggestions"),
                    dbc.Tab([
                        html.Div(id="member-info-content")
                    ], label="👤 Member Info", tab_id="member-info"),
                    dbc.Tab([
                        html.Div(id="kb-content")
                    ], label="📚 Knowledge Base", tab_id="kb")
                ], id="ai-tabs", active_tab="suggestions"),
                
                # AI Suggestions button
                dbc.Button(
                    "🔄 Get AI Suggestion",
                    id="btn-get-suggestion",
                    color="primary",
                    className="mt-3",
                    n_clicks=0
                ),
                html.Div(id="suggestion-display"),
                html.Div(id="suggestion-loading", style={"display": "none"})
            ], width=5)
        ])
    ])

# Callback: Fetch and display transcript
@app.callback(
    Output('transcript-display', 'children'),
    Output('store-transcript-data', 'data'),
    Input('store-selected-call-id', 'data'),
    Input('interval-component', 'n_intervals'),
    State('store-last-rendered-call-id', 'data'),
    State('store-kb-interaction', 'data'),
    prevent_initial_call=True
)
def update_transcript(selected_call_id, n_intervals, last_call_id, kb_interaction):
    """Fetch and display transcript"""
    if not selected_call_id:
        return html.Div(), None
    
    # Check if we should use cache
    call_id_changed = (selected_call_id != last_call_id)
    should_fetch = call_id_changed or not kb_interaction
    
    try:
        if should_fetch:
            transcript_df = get_live_transcript(selected_call_id)
            transcript_data = transcript_df.to_dict('records') if not transcript_df.empty else []
            
            display = TranscriptContainer(transcript_df)
            
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

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
