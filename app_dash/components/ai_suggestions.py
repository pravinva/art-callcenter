"""
AI Suggestion Components and Utilities
"""
from dash import html
import dash_bootstrap_components as dbc
import re
import html as html_module

ART_PRIMARY_BLUE = "#0051FF"
ART_TEXT_GRAY = "#666666"

def format_suggestion_text(text: str) -> str:
    """
    Format AI suggestion text - clean HTML and add proper styling
    Simplified version for Dash
    """
    if not text:
        return text
    
    # Decode HTML entities
    text = html_module.unescape(text)
    
    # Convert markdown to HTML
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    
    # Wrap sections in divs
    # Context Summary
    if 'Context Summary:' in text or 'Context:' in text:
        text = re.sub(
            r'(?:Context Summary|Context):\s*(.+?)(?=Suggested|Compliance|$)',
            r'<div class="context-summary" style="background-color: #E6F0FF; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;"><strong>Context Summary:</strong> \1</div>',
            text,
            flags=re.DOTALL | re.IGNORECASE,
            count=1
        )
    
    # Suggested Response
    if 'Suggested Response:' in text:
        text = re.sub(
            r'Suggested Response:\s*(.+?)(?=Compliance|$)',
            r'<div class="suggested-response" style="background-color: #F0F8FF; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #0051FF;"><strong>Suggested Response:</strong> \1</div>',
            text,
            flags=re.DOTALL | re.IGNORECASE,
            count=1
        )
    
    # Compliance
    if 'Compliance:' in text:
        text = re.sub(
            r'Compliance:\s*(.+?)(?=Suggested|$)',
            r'<div class="compliance-info" style="background-color: #FFF3CD; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #FFC107;"><strong>Compliance:</strong> \1</div>',
            text,
            flags=re.DOTALL | re.IGNORECASE,
            count=1
        )
    
    # Convert line breaks
    text = text.replace('\n\n', '<br><br>').replace('\n', '<br>')
    
    return text

def create_suggestion_card(suggestion_text: str, response_time: float = None, is_heuristic: bool = False) -> dbc.Card:
    """Create AI suggestion card component"""
    
    formatted_html = format_suggestion_text(suggestion_text)
    
    header = "⚡ Instant Suggestion (Heuristic)" if is_heuristic else "✨ Enhanced AI Suggestion"
    header_color = ART_PRIMARY_BLUE
    
    time_display = ""
    if response_time:
        time_display = html.Div([
            html.Hr(),
            html.P([
                html.Span("⏱️ ", style={"marginRight": "0.5rem"}),
                f"Response time: {response_time:.2f}s"
            ], style={"color": ART_TEXT_GRAY, "fontSize": "0.9rem", "margin": 0})
        ])
    
    return dbc.Card([
        dbc.CardBody([
            html.H6(header, style={"color": header_color, "marginBottom": "1rem"}),
            html.Div(
                formatted_html,
                dangerously_allow_html=True,
                style={"fontSize": "0.95rem", "lineHeight": "1.6"}
            ),
            time_display
        ])
    ], className="mb-3", style={"boxShadow": "0 2px 4px rgba(0,0,0,0.1)"})

