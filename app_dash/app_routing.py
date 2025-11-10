#!/usr/bin/env python3
"""
ART Call Center - Dash Application with Routing
Main application entry point with multi-page routing

Run: python app_dash/app_routing.py
"""
import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import pages
from app_dash.pages.analytics import create_analytics_layout, register_analytics_callbacks
from app_dash.pages.supervisor import create_supervisor_layout, register_supervisor_callbacks

# Import agent dashboard (main page)
from app_dash.app import app as agent_app_base, create_agent_dashboard_layout

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

app.title = "ART Call Center - Live Agent Assist"

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
