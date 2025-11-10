#!/usr/bin/env python3
"""
ART Call Center - Unified Dash Application
Main application entry point with multi-page routing

Run: python app_dash/app.py
"""
import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import utilities and components
from app_dash.utils.data_fetchers import get_active_calls
from app_dash.components.common import ErrorAlert

# Import pages
from app_dash.pages.analytics import create_analytics_layout, register_analytics_callbacks
from app_dash.pages.supervisor import create_supervisor_layout, register_supervisor_callbacks

# ART Brand Colors
ART_PRIMARY_BLUE = "#0051FF"

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

app.title = "ART Call Center - Live Agent Assist"

def create_agent_dashboard_layout():
    """Create agent dashboard layout (main page)"""
    from app_dash.utils.state_manager import StateManager
    from app_dash.components.common import StatusIndicator
    
    state_manager = StateManager()
    
    return html.Div([
        # State stores
        *state_manager.create_stores(),
        
        html.H1("Live Agent Assist", className="mb-4"),
        html.P("Real-time AI assistance for Australian Retirement Trust member service representatives", className="text-muted mb-4"),
        
        dbc.Row([
            dbc.Col([
                html.H4("📞 Active Calls"),
                dcc.Dropdown(
                    id="call-selector",
                    placeholder="Select a call to monitor...",
                    style={"marginBottom": "1rem"}
                ),
                html.Div(id="call-info-display"),
                html.Div(id="sidebar-calls")
            ], width=3),
            dbc.Col([
                html.Div(id="main-content")
            ], width=9)
        ]),
        
        # Global stores
        dcc.Store(id='store-selected-call-id'),
        dcc.Store(id='store-transcript-data'),
        dcc.Store(id='store-suggestion-state'),
        dcc.Store(id='store-heuristic-suggestion'),
        dcc.Store(id='store-last-rendered-call-id'),
        dcc.Store(id='store-kb-results'),
        dcc.Store(id='store-kb-query'),
        dcc.Store(id='store-kb-selected-question'),
        dcc.Store(id='store-kb-interaction'),
        dcc.Store(id='store-active-tab'),
        dcc.Store(id='store-active-calls'),
        
        # Global interval
        dcc.Interval(id='interval-component', interval=5000, n_intervals=0)
    ])

# Main layout with navigation
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    
    # Navigation bar
    dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H4("ART Call Center", className="mb-0", style={"color": "white"})
                ], width="auto"),
                dbc.Col([
                    dbc.Nav([
                        dbc.NavItem(dbc.NavLink("Live Agent Assist", href="/", id="nav-agent")),
                        dbc.NavItem(dbc.NavLink("Analytics", href="/analytics", id="nav-analytics")),
                        dbc.NavItem(dbc.NavLink("Supervisor", href="/supervisor", id="nav-supervisor"))
                    ], navbar=True, className="ms-auto")
                ], width="auto")
            ], align="center")
        ], fluid=True),
        color="primary",
        dark=True,
        className="mb-4"
    ),
    
    # Page content
    html.Div(id='page-content')
])

# Register page callbacks
register_analytics_callbacks(app)
register_supervisor_callbacks(app)

# Import agent dashboard callbacks
from app_dash.app import (
    update_active_calls, update_call_info, update_selected_call_id,
    update_main_content, update_transcript, update_last_rendered_call_id,
    get_ai_suggestion, update_member_info, update_kb_tab_content,
    search_kb, update_compliance_alerts, update_active_tab
)

# Re-register agent callbacks with URL routing
@app.callback(
    Output('call-selector', 'options'),
    Output('store-active-calls', 'data'),
    Input('url', 'pathname'),
    Input('interval-component', 'n_intervals'),
    prevent_initial_call=False
)
def update_active_calls_routed(pathname, n_intervals):
    """Update active calls dropdown (only on agent page)"""
    if pathname != '/' and pathname != '/agent':
        return [], []
    return update_active_calls(n_intervals)

@app.callback(
    Output('call-info-display', 'children'),
    Input('url', 'pathname'),
    Input('call-selector', 'value'),
    State('store-active-calls', 'data')
)
def update_call_info_routed(pathname, selected_call_id, calls_data):
    """Update call info display (only on agent page)"""
    if pathname != '/' and pathname != '/agent':
        return html.Div()
    return update_call_info(selected_call_id, calls_data)

@app.callback(
    Output('store-selected-call-id', 'data'),
    Input('url', 'pathname'),
    Input('call-selector', 'value')
)
def update_selected_call_id_routed(pathname, selected_call_id):
    """Update selected call ID (only on agent page)"""
    if pathname != '/' and pathname != '/agent':
        return None
    return update_selected_call_id(selected_call_id)

@app.callback(
    Output('main-content', 'children'),
    Input('url', 'pathname'),
    Input('store-selected-call-id', 'data'),
    prevent_initial_call=True
)
def update_main_content_routed(pathname, selected_call_id):
    """Update main content (only on agent page)"""
    if pathname != '/' and pathname != '/agent':
        return html.Div()
    return update_main_content(selected_call_id)

# Callback: Route pages
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    """Route to different pages based on URL"""
    if pathname == '/analytics':
        return create_analytics_layout()
    elif pathname == '/supervisor':
        return create_supervisor_layout()
    else:
        # Default: Agent dashboard
        return create_agent_dashboard_layout()

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)

