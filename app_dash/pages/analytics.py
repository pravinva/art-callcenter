"""
Analytics Dashboard Page
Dash page for analytics and reporting
"""
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
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
    return html.Div([
        html.H1("📊 ART Call Center Analytics Dashboard", className="mb-4"),
        html.Hr(),
        
        # Tabs
        dbc.Tabs([
            dbc.Tab([
                html.Div(id="analytics-overview-content")
            ], label="📈 Overview", tab_id="overview"),
            dbc.Tab([
                html.Div(id="analytics-agent-content")
            ], label="👥 Agent Performance", tab_id="agent"),
            dbc.Tab([
                html.Div(id="analytics-calls-content")
            ], label="📞 Call Summaries", tab_id="calls"),
            dbc.Tab([
                html.Div(id="analytics-daily-content")
            ], label="📊 Daily Statistics", tab_id="daily")
        ], id="analytics-tabs", active_tab="overview"),
        
        # Stores
        dcc.Store(id="store-analytics-metrics"),
        dcc.Store(id="store-analytics-call-summaries"),
        dcc.Store(id="store-analytics-agent-performance"),
        dcc.Store(id="store-analytics-daily-stats"),
        
        # Interval for auto-refresh
        dcc.Interval(id="analytics-interval", interval=300000, n_intervals=0)  # 5 minutes
    ])

def register_analytics_callbacks(app):
    """Register analytics dashboard callbacks"""
    
    @app.callback(
        Output('analytics-overview-content', 'children'),
        Output('store-analytics-metrics', 'data'),
        Input('analytics-tabs', 'active_tab'),
        Input('analytics-interval', 'n_intervals'),
        prevent_initial_call=True
    )
    def update_overview(active_tab, n_intervals):
        """Update overview tab"""
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
            ])
            
            return content, metrics
        except Exception as e:
            return ErrorAlert(f"Error loading overview: {e}"), None
    
    @app.callback(
        Output('analytics-agent-content', 'children'),
        Output('store-analytics-agent-performance', 'data'),
        Input('analytics-tabs', 'active_tab'),
        Input('analytics-interval', 'n_intervals'),
        Input('agent-search-input', 'value'),
        State('agent-search-input', 'value'),
        prevent_initial_call=True
    )
    def update_agent_performance(active_tab, n_intervals, search_value, state_value):
        """Update agent performance tab"""
        if active_tab != 'agent':
            return html.Div(), None
        
        try:
            if search_value:
                # Search specific agent
                agent_df = get_agent_by_id(search_value)
                if agent_df is not None and not agent_df.empty:
                    content = html.Div([
                        html.H3(f"Agent Performance: {search_value}", className="mb-4"),
                        create_agent_performance_table(agent_df)
                    ])
                else:
                    content = dbc.Alert(f"No data found for agent {search_value}", color="warning")
            else:
                # Show top performers
                top_agents_df = get_agent_performance(limit=20)
                content = html.Div([
                    html.H3("Top Performing Agents", className="mb-4"),
                    create_agent_performance_table(top_agents_df),
                    html.Hr(),
                    html.H4("Search Agent Performance", className="mb-3"),
                    dcc.Input(
                        id="agent-search-input",
                        type="text",
                        placeholder="Enter Agent ID (e.g., AGENT-001)",
                        style={"width": "100%", "marginBottom": "1rem"}
                    ),
                    dbc.Row([
                        dbc.Col([
                            create_performance_chart(top_agents_df, 'performance_score')
                        ], width=6),
                        dbc.Col([
                            create_performance_chart(top_agents_df, 'compliance_rate')
                        ], width=6)
                    ])
                ])
            
            return content, None
        except Exception as e:
            return ErrorAlert(f"Error loading agent performance: {e}"), None
    
    @app.callback(
        Output('analytics-calls-content', 'children'),
        Output('store-analytics-call-summaries', 'data'),
        Input('analytics-tabs', 'active_tab'),
        Input('analytics-interval', 'n_intervals'),
        Input('sentiment-filter', 'value'),
        Input('compliance-filter', 'value'),
        prevent_initial_call=True
    )
    def update_call_summaries(active_tab, n_intervals, sentiment_filter, compliance_filter):
        """Update call summaries tab"""
        if active_tab != 'calls':
            return html.Div(), None
        
        try:
            summaries_df = get_call_summaries_filtered(
                sentiment_filter=sentiment_filter or "All",
                compliance_filter=compliance_filter or "All",
                limit=100
            )
            
            content = html.Div([
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
                ], className="mb-4"),
                create_call_summaries_table(summaries_df)
            ])
            
            return content, summaries_df.to_dict('records') if summaries_df is not None and not summaries_df.empty else []
        except Exception as e:
            return ErrorAlert(f"Error loading call summaries: {e}"), None
    
    @app.callback(
        Output('analytics-daily-content', 'children'),
        Output('store-analytics-daily-stats', 'data'),
        Input('analytics-tabs', 'active_tab'),
        Input('analytics-interval', 'n_intervals'),
        prevent_initial_call=True
    )
    def update_daily_statistics(active_tab, n_intervals):
        """Update daily statistics tab"""
        if active_tab != 'daily':
            return html.Div(), None
        
        try:
            daily_df = get_daily_statistics(days=30)
            
            content = html.Div([
                html.H3("Daily Call Statistics", className="mb-4"),
                create_daily_stats_chart(daily_df),
                html.Hr(),
                create_call_summaries_table(daily_df)  # Reuse table component
            ])
            
            return content, daily_df.to_dict('records') if daily_df is not None and not daily_df.empty else []
        except Exception as e:
            return ErrorAlert(f"Error loading daily statistics: {e}"), None

