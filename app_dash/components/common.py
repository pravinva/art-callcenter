"""
Common Reusable Components for Dash App
"""
from dash import html, dcc
import dash_bootstrap_components as dbc

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

def StatusIndicator(is_online: bool = True) -> html.Div:
    """Status indicator component"""
    color = ART_SUCCESS_GREEN if is_online else ART_ERROR_RED
    status_text = "Online" if is_online else "Offline"
    
    return html.Div([
        html.Span(
            "●",
            style={
                "color": color,
                "fontSize": "1.2rem",
                "marginRight": "0.5rem"
            }
        ),
        html.Strong(status_text)
    ], style={"display": "flex", "alignItems": "center"})

def LoadingSpinner(message: str = "Loading...") -> dbc.Spinner:
    """Loading spinner component"""
    return dbc.Spinner(
        html.Div(message),
        fullscreen=False,
        spinner_style={"width": "3rem", "height": "3rem"}
    )

def ErrorAlert(message: str) -> dbc.Alert:
    """Error alert component"""
    return dbc.Alert(
        message,
        color="danger",
        dismissable=True,
        is_open=True
    )

def CallCard(call_id: str, member_name: str, scenario: str, utterances: int) -> dbc.Card:
    """Call card component"""
    return dbc.Card([
        dbc.CardBody([
            html.H6(f"Call: {call_id[-8:]}", className="card-title"),
            html.P([
                html.Strong("Member: "),
                member_name
            ]),
            html.P([
                html.Strong("Scenario: "),
                scenario
            ]),
            html.P([
                html.Strong("Utterances: "),
                str(utterances)
            ])
        ])
    ], className="mb-3")

