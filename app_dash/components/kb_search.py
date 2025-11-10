"""
Knowledge Base Components
"""
from dash import html, dcc
import dash_bootstrap_components as dbc

ART_TEXT_GRAY = "#666666"
ART_PRIMARY_BLUE = "#0051FF"

def create_kb_results_display(kb_results: list, query: str) -> html.Div:
    """Create KB results display component"""
    if not kb_results or len(kb_results) == 0:
        return dbc.Alert("No results found. Try rephrasing your question.", color="info")
    
    cards = []
    for article in kb_results:
        article_id = article.get('article_id', 'N/A')
        title = article.get('title', 'N/A')
        content = article.get('content', 'N/A')
        category = article.get('category', 'N/A')
        
        # Truncate content
        content_display = content[:500] + "..." if len(str(content)) > 500 else content
        
        card = dbc.Card([
            dbc.CardBody([
                html.H6(f"[{article_id}] {title}", className="card-title"),
                html.P([
                    html.Small(f"Category: {category}", className="text-muted")
                ]),
                html.P(
                    content_display,
                    style={"fontSize": "0.9rem", "lineHeight": "1.5", "marginTop": "0.5rem"}
                )
            ])
        ], className="mb-3")
        cards.append(card)
    
    return html.Div([
        html.H6(f"📚 Results for: '{query}'", className="mb-3"),
        html.Div(cards)
    ])

