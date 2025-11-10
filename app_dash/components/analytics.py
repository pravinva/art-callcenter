"""
Analytics Dashboard Components
Dash components for analytics visualizations
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

ART_PRIMARY = "#003366"
ART_SECONDARY = "#0066CC"
ART_ACCENT = "#FF6600"

def create_metric_card(title: str, value: str, subtitle: str = None) -> dbc.Card:
    """Create a metric card"""
    return dbc.Card([
        dbc.CardBody([
            html.H6(title, className="text-muted mb-2"),
            html.H3(value, className="mb-0", style={"color": ART_PRIMARY, "fontWeight": "bold"}),
            html.Small(subtitle, className="text-muted") if subtitle else None
        ])
    ], className="mb-3")

def create_overview_metrics(metrics: dict) -> html.Div:
    """Create overview metrics display"""
    return dbc.Row([
        dbc.Col([
            create_metric_card(
                "Total Calls (7 days)",
                f"{metrics.get('total_calls', 0):,}"
            )
        ], width=3),
        dbc.Col([
            create_metric_card(
                "Active Agents",
                f"{metrics.get('active_agents', 0):,}"
            )
        ], width=3),
        dbc.Col([
            create_metric_card(
                "Unique Members",
                f"{metrics.get('unique_members', 0):,}"
            )
        ], width=3),
        dbc.Col([
            create_metric_card(
                "Avg Positive Sentiment",
                f"{metrics.get('avg_positive_rate', 0):.1f}%"
            )
        ], width=3)
    ])

def create_call_summaries_table(df: pd.DataFrame) -> html.Div:
    """Create call summaries data table"""
    if df is None or df.empty:
        return dbc.Alert("No call summaries available", color="info")
    
    # Convert DataFrame to HTML table
    table_header = [html.Thead([html.Tr([html.Th(col) for col in df.columns])])]
    table_body = [html.Tbody([
        html.Tr([html.Td(str(df.iloc[i][col])) for col in df.columns])
        for i in range(min(len(df), 20))  # Limit to 20 rows
    ])]
    
    return dbc.Table(table_header + table_body, bordered=True, hover=True, responsive=True)

def create_agent_performance_table(df: pd.DataFrame) -> html.Div:
    """Create agent performance table"""
    if df is None or df.empty:
        return dbc.Alert("No agent performance data available", color="info")
    
    table_header = [html.Thead([html.Tr([html.Th(col) for col in df.columns])])]
    table_body = [html.Tbody([
        html.Tr([html.Td(str(df.iloc[i][col])) for col in df.columns])
        for i in range(min(len(df), 20))
    ])]
    
    return dbc.Table(table_header + table_body, bordered=True, hover=True, responsive=True)

def create_performance_chart(df: pd.DataFrame, column: str) -> dcc.Graph:
    """Create performance bar chart"""
    if df is None or df.empty or column not in df.columns:
        return dcc.Graph(figure={})
    
    top_10 = df.head(10)
    fig = go.Figure(data=[
        go.Bar(
            x=top_10['agent_id'],
            y=top_10[column],
            marker_color=ART_SECONDARY
        )
    ])
    fig.update_layout(
        title=f"{column.replace('_', ' ').title()}",
        xaxis_title="Agent ID",
        yaxis_title=column.replace('_', ' ').title(),
        height=400
    )
    return dcc.Graph(figure=fig)

def create_daily_stats_chart(df: pd.DataFrame) -> dcc.Graph:
    """Create daily statistics line chart"""
    if df is None or df.empty:
        return dcc.Graph(figure={})
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['call_date'],
        y=df['total_calls'],
        mode='lines+markers',
        name='Total Calls',
        line=dict(color=ART_PRIMARY)
    ))
    fig.add_trace(go.Scatter(
        x=df['call_date'],
        y=df['unique_members'],
        mode='lines+markers',
        name='Unique Members',
        line=dict(color=ART_SECONDARY)
    ))
    fig.update_layout(
        title="Daily Call Statistics",
        xaxis_title="Date",
        yaxis_title="Count",
        height=400,
        hovermode='x unified'
    )
    return dcc.Graph(figure=fig)

