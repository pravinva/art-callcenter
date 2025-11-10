"""
AI Suggestion Components and Utilities
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
import re
import html as html_module

ART_PRIMARY_BLUE = "#0051FF"
ART_TEXT_GRAY = "#666666"
ART_LIGHT_BLUE = "#E6F0FF"
ART_WHITE = "#FFFFFF"
ART_WARNING_YELLOW = "#FFF3CD"
ART_BORDER = "#E0E0E0"

def format_suggestion_text(text: str) -> list:
    """
    Format AI suggestion text - return list of Dash components instead of HTML string
    """
    if not text:
        return [html.P("No suggestion available")]
    
    # Decode HTML entities
    text = html_module.unescape(text)
    
    components = []
    
    # Extract Context Summary
    context_match = re.search(r'(?:Context Summary|Context):\s*(.+?)(?=Suggested|Compliance|$)', text, re.DOTALL | re.IGNORECASE)
    if context_match:
        context_text = context_match.group(1).strip()
        # Clean up markdown
        context_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', context_text)
        context_text = re.sub(r'\n+', ' ', context_text)
        components.append(
            html.Div([
                html.Strong("Context Summary: "),
                html.Span(context_text, style={"fontSize": "0.95rem"})
            ], style={
                "backgroundColor": ART_LIGHT_BLUE,
                "padding": "1rem",
                "borderRadius": "8px",
                "marginBottom": "1rem"
            })
        )
    
    # Extract Suggested Response
    response_match = re.search(r'Suggested Response:\s*(.+?)(?=Compliance|$)', text, re.DOTALL | re.IGNORECASE)
    if response_match:
        response_text = response_match.group(1).strip()
        # Clean up markdown
        response_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', response_text)
        response_text = re.sub(r'\n+', ' ', response_text)
        components.append(
            html.Div([
                html.Strong("Suggested Response: "),
                html.Span(response_text, style={"fontSize": "0.95rem"})
            ], style={
                "backgroundColor": "#F0F8FF",
                "padding": "1rem",
                "borderRadius": "8px",
                "marginBottom": "1rem",
                "borderLeft": "4px solid " + ART_PRIMARY_BLUE
            })
        )
    
    # Extract Compliance
    compliance_match = re.search(r'Compliance:\s*(.+?)(?=Suggested|$)', text, re.DOTALL | re.IGNORECASE)
    if compliance_match:
        compliance_text = compliance_match.group(1).strip()
        # Clean up markdown
        compliance_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', compliance_text)
        compliance_text = re.sub(r'\n+', ' ', compliance_text)
        components.append(
            html.Div([
                html.Strong("Compliance: "),
                html.Span(compliance_text, style={"fontSize": "0.95rem"})
            ], style={
                "backgroundColor": ART_WARNING_YELLOW,
                "padding": "1rem",
                "borderRadius": "8px",
                "marginBottom": "1rem",
                "borderLeft": "4px solid #FFC107"
            })
        )
    
    # If no structured sections found, display as plain text
    if not components:
        # Clean up markdown
        clean_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        clean_text = re.sub(r'\n+', '\n', clean_text)
        components.append(html.P(clean_text, style={"fontSize": "0.95rem", "lineHeight": "1.6"}))
    
    return components

def create_suggestion_card(suggestion_text: str, response_time: float = None, is_heuristic: bool = False) -> dbc.Card:
    """Create AI suggestion card component"""
    
    formatted_components = format_suggestion_text(suggestion_text)
    
    header = "⚡ Instant Suggestion (Heuristic)" if is_heuristic else "✨ Enhanced AI Suggestion"
    header_color = ART_PRIMARY_BLUE
    
    time_display = []
    if response_time:
        time_display = [
            html.Hr(),
            html.P([
                html.Span("⏱️ ", style={"marginRight": "0.5rem"}),
                f"Response time: {response_time:.2f}s"
            ], style={"color": ART_TEXT_GRAY, "fontSize": "0.9rem", "margin": 0})
        ]
    
    return dbc.Card([
        dbc.CardBody([
            html.H6(header, style={"color": header_color, "marginBottom": "1rem"}),
            html.Div(
                formatted_components,
                style={"fontSize": "0.95rem", "lineHeight": "1.6"}
            ),
            *time_display
        ])
    ], className="mb-3", style={"boxShadow": "0 2px 4px rgba(0,0,0,0.1)"})

