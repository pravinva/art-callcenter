"""
State Management Utilities for Dash App
Manages dcc.Store components and state updates
"""
from dash import dcc
from typing import Dict, Any, Optional

class StateManager:
    """Manages application state using dcc.Store components"""
    
    def __init__(self):
        self.stores = {}
    
    def create_stores(self) -> list:
        """Create all dcc.Store components"""
        stores = [
            # Call selection
            dcc.Store(id='store-selected-call-id', data=None),
            dcc.Store(id='store-active-calls', data=[]),
            
            # Transcript
            dcc.Store(id='store-transcript-data', data=None),
            dcc.Store(id='store-transcript-cache', data={}),  # Cache by call_id
            
            # AI Suggestions
            dcc.Store(id='store-suggestion-state', data={
                'loading': False,
                'error': None,
                'suggestion_text': None,
                'formatted_html': None,
                'response_time': None,
                'call_id': None
            }),
            dcc.Store(id='store-heuristic-suggestion', data=None),
            
            # Member Info
            dcc.Store(id='store-member-context', data=None),
            dcc.Store(id='store-member-history', data=None),
            
            # Knowledge Base
            dcc.Store(id='store-kb-results', data=[]),
            dcc.Store(id='store-kb-query', data=None),
            dcc.Store(id='store-kb-selected-question', data=None),
            
            # Compliance
            dcc.Store(id='store-compliance-alerts', data=[]),
            
            # UI State
            dcc.Store(id='store-active-tab', data='suggestions'),
            dcc.Store(id='store-kb-interaction', data=False),
            dcc.Store(id='store-last-rendered-call-id', data=None),
        ]
        
        return stores
    
    @staticmethod
    def get_store_data(store_data: Dict[str, Any], key: str, default: Any = None) -> Any:
        """Helper to safely get data from store"""
        if isinstance(store_data, dict):
            return store_data.get(key, default)
        return default
    
    @staticmethod
    def update_store_data(store_data: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to update store data"""
        if not isinstance(store_data, dict):
            store_data = {}
        store_data.update(updates)
        return store_data

