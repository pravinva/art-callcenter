"""
Knowledge Base Utilities for Dash App
"""
from typing import List, Optional
from app_dash.utils.data_fetchers import get_live_transcript
from app_dash.utils.databricks_client import execute_sql
from config.config import (
    ENRICHED_TABLE, SQL_WAREHOUSE_ID,
    FUNCTION_SEARCH_KB, VECTOR_SEARCH_ENDPOINT, KB_INDEX_NAME
)

def get_suggested_kb_questions(call_id: str) -> List[str]:
    """Get suggested KB questions STRICTLY based on call scenario - returns scenario-specific questions only"""
    try:
        # Get the primary scenario for this call
        query = f"""
        SELECT 
            scenario,
            COUNT(*) as count
        FROM {ENRICHED_TABLE}
        WHERE call_id = '{call_id}'
        GROUP BY scenario
        ORDER BY count DESC
        LIMIT 1
        """
        results = execute_sql(query, SQL_WAREHOUSE_ID, return_dataframe=True)
        
        # Map scenarios to specific questions - STRICT scenario-based mapping
        scenario_question_map = {
            'contribution_inquiry': [
                "What are the contribution caps?",
                "How do employer contributions work?",
                "What are non-concessional contributions?",
                "What are concessional contributions?",
                "How do I make additional contributions?",
                "What are the catch-up contribution rules?",
                "What is the superannuation guarantee rate?",
                "How do salary sacrifice contributions work?"
            ],
            'withdrawal_compassionate': [
                "What are the requirements for compassionate grounds withdrawal?",
                "How do I apply for financial hardship withdrawal?",
                "What is early access super?",
                "What documents do I need for compassionate withdrawal?",
                "How long does withdrawal approval take?",
                "What are the withdrawal conditions?",
                "What are the eligibility criteria for early release?",
                "How do I apply for early access due to financial hardship?"
            ],
            'insurance_inquiry': [
                "What insurance coverage do I have?",
                "How do I make an insurance claim?",
                "What is TPD insurance?",
                "What is death insurance coverage?",
                "How do I update my insurance beneficiaries?",
                "What are the insurance premiums?",
                "What is income protection insurance?",
                "How do I cancel my insurance?"
            ],
            'performance_inquiry': [
                "What investment options are available?",
                "How is investment performance calculated?",
                "How do I switch investments?",
                "What are the historical returns?",
                "What are the investment fees?",
                "How do I check my investment performance?",
                "What is the default investment option?",
                "How do I change my investment strategy?"
            ],
            'beneficiary_update': [
                "How do I update my beneficiaries?",
                "What information do I need to update beneficiaries?",
                "Can I have multiple beneficiaries?",
                "How do I remove a beneficiary?",
                "What happens if I don't have a beneficiary?",
                "What percentage can I allocate to each beneficiary?",
                "How do I add a new beneficiary?"
            ],
            'complaint_handling': [
                "What's the complaint process?",
                "What's the dispute resolution mechanism?",
                "How do I file a formal complaint?",
                "What are my rights if I'm not satisfied with service?",
                "How long does complaint resolution take?",
                "What happens after I submit a complaint?",
                "Can I escalate my complaint if I'm not satisfied?",
                "What is the internal dispute resolution process?"
            ],
            'compliance_violations': [
                "What are the compliance requirements?",
                "What happens if there's a compliance issue?",
                "How are compliance violations handled?",
                "What are my rights regarding compliance?",
                "How do I report a compliance concern?",
                "What are the consequences of non-compliance?",
                "How is compliance monitored?"
            ],
            'general_inquiry': [
                "How do I check my account balance?",
                "How do I update my personal details?",
                "What are the superannuation rules?",
                "How do I access my account online?",
                "What are the fees and charges?",
                "How do I contact customer service?",
                "What is my member number?",
                "How do I reset my password?"
            ]
        }
        
        # Get primary scenario
        primary_scenario = None
        if results is not None and not results.empty:
            primary_scenario = str(results.iloc[0].get('scenario', '')).strip()
        
        # Return questions STRICTLY for the detected scenario
        if primary_scenario and primary_scenario in scenario_question_map:
            questions = scenario_question_map[primary_scenario]
            # Return top 5-7 questions for the scenario
            return questions[:7] if len(questions) > 7 else questions
        
        # If scenario not found or not mapped, return general questions
        print(f"⚠️ Scenario '{primary_scenario}' not found in map, using general_inquiry questions")
        return scenario_question_map.get('general_inquiry', [])[:7]
        
    except Exception as e:
        print(f"Error getting suggested KB questions: {e}")
        import traceback
        traceback.print_exc()
        # Return general questions on error
        return [
            "How do I check my account balance?",
            "How do I update my personal details?",
            "What are the superannuation rules?",
            "How do I access my account online?",
            "What are the fees and charges?"
        ]

def search_kb_vector_search(query: str, num_results: int = 5) -> List[dict]:
    """
    Search knowledge base using vector search (semantic similarity).
    Falls back to SQL function if vector search is not available.
    """
    import time
    start_time = time.time()
    
    try:
        # Try standard import first, then fallback to databricks-vectorsearch package
        try:
            from databricks.vector_search.client import VectorSearchClient
        except ImportError:
            from databricks_vectorsearch.client import VectorSearchClient
        
        # Initialize vector search client
        vsc = VectorSearchClient(disable_notice=True)
        
        # Get the vector search index
        try:
            index = vsc.get_index(
                endpoint_name=VECTOR_SEARCH_ENDPOINT,
                index_name=KB_INDEX_NAME
            )
        except Exception as e:
            # Index doesn't exist yet, fallback to SQL
            elapsed = time.time() - start_time
            print(f"⚠️ Vector search index not found (took {elapsed:.2f}s), falling back to SQL: {e}")
            return search_kb_sql_fallback(query)
        
        # Perform vector search
        search_start = time.time()
        results = index.similarity_search(
            query_text=query,
            columns=["article_id", "title", "content", "category"],
            num_results=num_results
        )
        search_elapsed = time.time() - search_start
        
        # Convert results to list of dicts
        articles = []
        if results and 'result' in results and 'data_array' in results['result']:
            for hit in results['result']['data_array']:
                articles.append({
                    'article_id': hit[0] if len(hit) > 0 else 'N/A',
                    'title': hit[1] if len(hit) > 1 else 'N/A',
                    'content': hit[2] if len(hit) > 2 else 'N/A',
                    'category': hit[3] if len(hit) > 3 else 'N/A'
                })
        
        total_elapsed = time.time() - start_time
        print(f"✅ Vector search completed: {len(articles)} results in {total_elapsed:.2f}s (search: {search_elapsed:.2f}s)")
        return articles
        
    except Exception as e:
        # Fallback to SQL keyword search if vector search fails
        elapsed = time.time() - start_time
        print(f"⚠️ Vector search failed (took {elapsed:.2f}s), falling back to SQL: {e}")
        import traceback
        traceback.print_exc()
        return search_kb_sql_fallback(query)

def search_kb_sql_fallback(query: str) -> List[dict]:
    """Fallback to SQL keyword search if vector search is not available"""
    import time
    start_time = time.time()
    
    try:
        query_sql = f"SELECT * FROM {FUNCTION_SEARCH_KB}('{query}')"
        articles_df = execute_sql(query_sql, SQL_WAREHOUSE_ID, return_dataframe=True)
        
        elapsed = time.time() - start_time
        
        if articles_df is not None and not articles_df.empty:
            print(f"✅ SQL search completed: {len(articles_df)} results in {elapsed:.2f}s")
            return articles_df.to_dict('records')
        else:
            print(f"⚠️ SQL search returned no results in {elapsed:.2f}s")
            return []
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Error in SQL KB search (took {elapsed:.2f}s): {e}")
        return []

