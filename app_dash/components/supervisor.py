"""
Supervisor Dashboard Components
Dash components for supervisor monitoring
"""
from dash import html
import dash_bootstrap_components as dbc
import pandas as pd

ART_ERROR_RED = "#DC3545"
ART_WARNING_ORANGE = "#FF6B35"
ART_SUCCESS_GREEN = "#00A651"
ART_PRIMARY_BLUE = "#0051FF"

def create_escalation_card(call_id: str, escalation_data: dict) -> dbc.Card:
    """Create escalation card for a call"""
    risk_score = escalation_data.get('risk_score', 0)
    escalation_recommended = escalation_data.get('escalation_recommended', False)
    
    # Determine severity color
    if risk_score >= 10 or escalation_recommended:
        color = "danger"
        border_color = ART_ERROR_RED
    elif risk_score >= 5:
        color = "warning"
        border_color = ART_WARNING_ORANGE
    else:
        color = "success"
        border_color = ART_SUCCESS_GREEN
    
    return dbc.Card([
        dbc.CardBody([
            html.H6(f"Call: {call_id[-8:]}", className="mb-2"),
            html.Div([
                html.Strong("Risk Score: "),
                html.Span(str(risk_score), style={"color": border_color, "fontWeight": "bold"})
            ], className="mb-2"),
            html.Div([
                html.Small(f"Negative Sentiments: {escalation_data.get('negative_sentiment_count', 0)}"),
                html.Br(),
                html.Small(f"Compliance Issues: {escalation_data.get('compliance_violations_count', 0)}"),
                html.Br(),
                html.Small(f"Complaints: {escalation_data.get('complaint_intent_count', 0)}")
            ], className="text-muted"),
            dbc.Badge(
                "Escalation Recommended" if escalation_recommended else "Monitor",
                color=color,
                className="mt-2"
            )
        ])
    ], className="mb-3", style={"borderLeft": f"4px solid {border_color}"})

def create_active_calls_list(df: pd.DataFrame, escalation_dict: dict) -> html.Div:
    """Create list of active calls with escalation info"""
    if df is None or df.empty:
        return dbc.Alert("No active calls", color="info")
    
    cards = []
    for _, row in df.iterrows():
        call_id = row.get('call_id', 'N/A')
        escalation_data = escalation_dict.get(call_id, {
            'risk_score': 0,
            'escalation_recommended': False,
            'negative_sentiment_count': 0,
            'compliance_violations_count': 0,
            'complaint_intent_count': 0
        })
        
        cards.append(create_escalation_card(call_id, escalation_data))
    
    return html.Div(cards)

def create_escalation_summary(summary: dict) -> html.Div:
    """Create escalation summary metrics"""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Active Calls", className="text-muted"),
                    html.H3(summary.get('total_active_calls', 0), style={"color": ART_PRIMARY_BLUE})
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Negative Sentiments", className="text-muted"),
                    html.H3(summary.get('total_negative_sentiments', 0), style={"color": ART_WARNING_ORANGE})
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Compliance Issues", className="text-muted"),
                    html.H3(summary.get('total_compliance_issues', 0), style={"color": ART_ERROR_RED})
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Complaints", className="text-muted"),
                    html.H3(summary.get('total_complaints', 0), style={"color": ART_ERROR_RED})
                ])
            ])
        ], width=3)
    ], className="mb-4")

