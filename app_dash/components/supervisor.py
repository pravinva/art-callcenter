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
    ], className="mb-2", style={"borderLeft": f"4px solid {border_color}", "height": "100%"})

def create_active_calls_list(df: pd.DataFrame, escalation_dict: dict) -> html.Div:
    """Create list of active calls with escalation info arranged horizontally"""
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
    
    # Arrange cards horizontally in rows (responsive: 3 on large, 2 on medium, 1 on small)
    rows = []
    for i in range(0, len(cards), 3):
        row_cards = cards[i:i + 3]
        cols = []
        for card in row_cards:
            # Responsive columns: 4 cols on large (3 per row), 6 cols on medium (2 per row), 12 cols on small (1 per row)
            cols.append(dbc.Col(card, width=4, md=6, xs=12, className="mb-3"))
        
        rows.append(dbc.Row(cols, className="mb-2"))
    
    return html.Div(rows)

def create_escalation_summary(summary: dict) -> html.Div:
    """Create escalation summary metrics (legacy - kept for compatibility)"""
    return create_escalation_summary_tabs(summary)

def create_escalation_summary_tabs(summary: dict) -> html.Div:
    """Create escalation summary as clickable tabs"""
    total_calls = summary.get('total_active_calls', 0)
    negative_sentiments = summary.get('total_negative_sentiments', 0)
    compliance_issues = summary.get('total_compliance_issues', 0)
    complaints = summary.get('total_complaints', 0)
    
    return dbc.Tabs([
        dbc.Tab(
            label=f"📞 All Calls ({total_calls})",
            tab_id="all-calls",
            tab_style={"marginRight": "0.5rem"},
            active_tab_style={"fontWeight": "bold"}
        ),
        dbc.Tab(
            label=f"😟 Negative Sentiment ({negative_sentiments})",
            tab_id="negative-sentiment",
            tab_style={"marginRight": "0.5rem"},
            active_tab_style={"fontWeight": "bold", "color": ART_WARNING_ORANGE}
        ),
        dbc.Tab(
            label=f"⚠️ Compliance Issues ({compliance_issues})",
            tab_id="compliance-issues",
            tab_style={"marginRight": "0.5rem"},
            active_tab_style={"fontWeight": "bold", "color": ART_ERROR_RED}
        ),
        dbc.Tab(
            label=f"📢 Complaints ({complaints})",
            tab_id="complaints",
            tab_style={"marginRight": "0.5rem"},
            active_tab_style={"fontWeight": "bold", "color": ART_ERROR_RED}
        )
    ], id="supervisor-tabs", active_tab="all-calls", className="mb-4")

