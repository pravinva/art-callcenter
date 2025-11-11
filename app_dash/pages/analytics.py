"""
Analytics Dashboard Page
Dash page for analytics and reporting
"""
from dash import html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app_dash.utils.analytics_data import (
    get_overview_metrics, get_recent_call_summaries, get_agent_performance,
    get_agent_by_id, get_call_summaries_filtered, get_daily_statistics
)
from app_dash.components.analytics import (
    create_overview_metrics, create_call_summaries_table,
    create_agent_performance_table, create_performance_chart, create_daily_stats_chart
)
from app_dash.components.common import ErrorAlert

def create_analytics_layout():
    """Create analytics dashboard layout"""
    return dbc.Container([
        html.H1("📊 ART Call Center Analytics Dashboard", className="mb-4"),
        html.Hr(),
        
        # Tabs
        dbc.Tabs([
            dbc.Tab([
                # Overview content with loading spinner
                dcc.Loading(
                    id="analytics-overview-loading",
                    type="default",
                    children=html.Div(id="analytics-overview-content"),
                    style={"minHeight": "300px"}
                )
            ], label="📈 Overview", tab_id="overview"),
            dbc.Tab([
                # Agent performance content with loading spinner
                dcc.Loading(
                    id="analytics-agent-loading",
                    type="default",
                    children=html.Div(id="analytics-agent-content"),
                    style={"minHeight": "300px"}
                ),
                html.Div([
                    html.Hr(),
                    html.H4("Search Agent Performance", className="mb-3"),
                    dcc.Input(
                        id="agent-search-input",
                        type="text",
                        placeholder="Enter Agent ID (e.g., AGENT-001)",
                        style={"width": "100%", "marginBottom": "1rem"}
                    )
                ], id="agent-search-container", style={"display": "none"})
            ], label="👥 Agent Performance", tab_id="agent"),
            dbc.Tab([
                # Call summaries content with loading spinner
                dcc.Loading(
                    id="analytics-calls-loading",
                    type="default",
                    children=html.Div(id="analytics-calls-content"),
                    style={"minHeight": "300px"}
                ),
                html.Div([
                    html.Hr(),
                    html.H3("Call Summaries", className="mb-4"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Sentiment Filter:", className="mb-2"),
                            dcc.Dropdown(
                                id="sentiment-filter",
                                options=[
                                    {"label": "All", "value": "All"},
                                    {"label": "Positive", "value": "positive"},
                                    {"label": "Negative", "value": "negative"},
                                    {"label": "Neutral", "value": "neutral"}
                                ],
                                value="All"
                            )
                        ], width=4),
                        dbc.Col([
                            html.Label("Compliance Filter:", className="mb-2"),
                            dcc.Dropdown(
                                id="compliance-filter",
                                options=[
                                    {"label": "All", "value": "All"},
                                    {"label": "Has Issues", "value": "Has Issues"},
                                    {"label": "No Issues", "value": "No Issues"}
                                ],
                                value="All"
                            )
                        ], width=4)
                    ], className="mb-4")
                ], id="calls-filter-container", style={"display": "none"})
            ], label="📞 Call Summaries", tab_id="calls"),
            dbc.Tab([
                # Daily statistics content with loading spinner
                dcc.Loading(
                    id="analytics-daily-loading",
                    type="default",
                    children=html.Div(id="analytics-daily-content"),
                    style={"minHeight": "300px"}
                )
            ], label="📊 Daily Statistics", tab_id="daily")
        ], id="analytics-tabs", active_tab="overview"),
        
        # Stores
        dcc.Store(id="store-analytics-metrics"),
        dcc.Store(id="store-analytics-call-summaries"),
        dcc.Store(id="store-analytics-agent-performance"),
        dcc.Store(id="store-analytics-daily-stats"),
        
        # Interval for auto-refresh
        dcc.Interval(id="analytics-interval", interval=300000, n_intervals=0),  # 5 minutes
        
        # Trigger initial load
        html.Div(id="analytics-initial-load", style={"display": "none"})
    ], fluid=True, style={"padding": "2rem"})

def register_analytics_callbacks(app):
    """Register analytics dashboard callbacks"""
    
    @app.callback(
        Output('analytics-overview-content', 'children'),
        Output('store-analytics-metrics', 'data'),
        Input('analytics-tabs', 'active_tab'),
        Input('analytics-interval', 'n_intervals'),
        Input('analytics-initial-load', 'children'),
        Input('url', 'pathname')  # Also trigger when navigating to analytics page
    )
    def update_overview(active_tab, n_intervals, initial_load, pathname):
        """Update overview tab"""
        # Only update when on analytics page
        if pathname != '/analytics':
            raise PreventUpdate
        
        if active_tab != 'overview':
            return html.Div(), None
        
        try:
            metrics = get_overview_metrics(days=7)
            summaries_df = get_recent_call_summaries(limit=20)
            
            content = html.Div([
                html.H3("Call Center Overview", className="mb-4"),
                create_overview_metrics(metrics),
                html.Hr(),
                html.H4("Recent Call Summaries", className="mb-3"),
                create_call_summaries_table(summaries_df)
            ], style={"padding": "1rem 0"})
            
            return content, metrics
        except Exception as e:
            import traceback
            error_msg = f"Error loading overview: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            return ErrorAlert(error_msg), None
    
    @app.callback(
        Output('analytics-agent-content', 'children'),
        Output('store-analytics-agent-performance', 'data'),
        Output('agent-search-container', 'style'),
        Input('analytics-tabs', 'active_tab'),
        Input('analytics-interval', 'n_intervals'),
        Input('analytics-initial-load', 'children'),
        Input('url', 'pathname'),  # Also trigger when navigating to analytics page
        Input('agent-search-input', 'value'),
        prevent_initial_call=False
    )
    def update_agent_performance(active_tab, n_intervals, initial_load, pathname, search_value):
        """Update agent performance tab"""
        # Only update when on analytics page
        if pathname != '/analytics':
            raise PreventUpdate
        
        if active_tab != 'agent':
            return html.Div(), None, {"display": "none"}
        
        try:
            if search_value:
                # Search specific agent
                agent_df = get_agent_by_id(search_value)
                if agent_df is not None and not agent_df.empty:
                    content = html.Div([
                        html.H3(f"Agent Performance: {search_value}", className="mb-4"),
                        create_agent_performance_table(agent_df)
                    ], style={"padding": "1rem 0"})
                else:
                    content = dbc.Alert(f"No data found for agent {search_value}", color="warning")
            else:
                # Show top performers
                top_agents_df = get_agent_performance(limit=20)
                if top_agents_df is None or top_agents_df.empty:
                    content = dbc.Alert("No agent performance data available", color="info")
                else:
                    content = html.Div([
                        html.H3("Top Performing Agents", className="mb-4"),
                        create_agent_performance_table(top_agents_df),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col([
                                create_performance_chart(top_agents_df, 'performance_score')
                            ], width=6),
                            dbc.Col([
                                create_performance_chart(top_agents_df, 'compliance_rate')
                            ], width=6)
                        ])
                    ], style={"padding": "1rem 0"})
            
            return content, None, {"display": "block"}
        except Exception as e:
            import traceback
            error_msg = f"Error loading agent performance: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            return ErrorAlert(error_msg), None, {"display": "block"}
    
    @app.callback(
        Output('analytics-calls-content', 'children'),
        Output('store-analytics-call-summaries', 'data'),
        Output('calls-filter-container', 'style'),
        Input('analytics-tabs', 'active_tab'),
        Input('analytics-interval', 'n_intervals'),
        Input('analytics-initial-load', 'children'),
        Input('url', 'pathname'),  # Also trigger when navigating to analytics page
        Input('sentiment-filter', 'value'),
        Input('compliance-filter', 'value'),
        prevent_initial_call=False
    )
    def update_call_summaries(active_tab, n_intervals, initial_load, pathname, sentiment_filter, compliance_filter):
        """Update call summaries tab"""
        # Only update when on analytics page
        if pathname != '/analytics':
            raise PreventUpdate
        
        if active_tab != 'calls':
            return html.Div(), None, {"display": "none"}
        
        try:
            summaries_df = get_call_summaries_filtered(
                sentiment_filter=sentiment_filter or "All",
                compliance_filter=compliance_filter or "All",
                limit=100
            )
            
            if summaries_df is None or summaries_df.empty:
                return html.Div([
                    dbc.Alert("No call summaries available", color="info")
                ], style={"padding": "1rem 0"}), [], {"display": "block"}
            
            content = html.Div([
                create_call_summaries_table(summaries_df)
            ], style={"padding": "1rem 0"})
            
            return content, summaries_df.to_dict('records') if summaries_df is not None and not summaries_df.empty else [], {"display": "block"}
        except Exception as e:
            import traceback
            error_msg = f"Error loading call summaries: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            return ErrorAlert(error_msg), None, {"display": "block"}
    
    @app.callback(
        Output('analytics-daily-content', 'children'),
        Output('store-analytics-daily-stats', 'data'),
        Input('analytics-tabs', 'active_tab'),
        Input('analytics-interval', 'n_intervals'),
        Input('url', 'pathname')  # Also trigger when navigating to analytics page
    )
    def update_daily_statistics(active_tab, n_intervals, pathname):
        """Update daily statistics tab"""
        # Only update when on analytics page
        if pathname != '/analytics':
            raise PreventUpdate
        
        if active_tab != 'daily':
            return html.Div(), None
        
        try:
            daily_df = get_daily_statistics(days=30)
            
            # Fix DataFrame boolean check
            if daily_df is None or (hasattr(daily_df, 'empty') and daily_df.empty):
                return html.Div([
                    html.H3("Daily Call Statistics", className="mb-4"),
                    dbc.Alert("No daily statistics data available", color="info")
                ]), []
            
            content = html.Div([
                html.H3("Daily Call Statistics", className="mb-4"),
                create_daily_stats_chart(daily_df),
                html.Hr(),
                create_call_summaries_table(daily_df)  # Reuse table component
            ], style={"padding": "1rem 0"})
            
            return content, daily_df.to_dict('records')
        except Exception as e:
            import traceback
            error_msg = f"Error loading daily statistics: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            return ErrorAlert(error_msg), None

