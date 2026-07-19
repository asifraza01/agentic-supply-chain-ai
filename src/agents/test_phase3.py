import os
from typing import TypedDict, Optional, List, Dict, Any, Annotated
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

# Import the core logic functions from your repository file
from text_query import check_data_presence_guardrail, final_ai_reply

load_dotenv()

# Initialize Llama 3.3 for the final synthesis layer
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    max_tokens=250,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# Shared State Definition mapping to your exact configuration
class TextToQueryState(TypedDict):
    messages: Annotated[list, list]  # Standard array placeholder for testing
    intent_route: str
    schemas_info: Optional[List[str]]
    sql_query_from_ai: Optional[str]
    raw_rows: Optional[List[Dict[str, Any]]]
    raw_cols: Optional[List[str]]
    contract_context: Optional[str]
    data_found: bool
    final_ai_reply: Optional[str]

def run_phase3_extended_test():
    print("=" * 75)
    print("STARTING PHASE 3 FIREWALL AND COMPILER EVALUATION LOGS")
    print("=" * 75)

    # -------------------------------------------------------------------------
    # TEST CASE 1: Valid Data Pass-Through (The scenario you just logged)
    # -------------------------------------------------------------------------
    print("\n\033[92m[TEST CASE #1: Valid Data Present - Testing Synthesis Layer]\033[0m")
    state_valid: TextToQueryState = {
        "messages": [HumanMessage(content="Show me total stock levels for SKU-100 in all stores group by each store")],
        "intent_route": "INVENTORY_LOOKUP",
        "schemas_info": None,
        "sql_query_from_ai": "SELECT current_stock FROM inventory WHERE sku = 'SKU-100' AND store_id = 1",
        "raw_rows": [{"current_stock": 111}], # The exact data your SQLite engine returned
        "raw_cols": ["current_stock"],
        "contract_context": None,
        "data_found": True,
        "final_ai_reply": None
    }

    # 1. Run through the Guardrail to verify it passes valid arrays
    state_valid.update(check_data_presence_guardrail(state_valid))
    # 2. Compile response using the custom inventory prompt factory
    state_valid.update(final_ai_reply(state_valid))
    
    print("\033[1m-> AI Response to Executive:\033[0m")
    print(f"   \"{state_valid['final_ai_reply']}\"")


    # -------------------------------------------------------------------------
    # TEST CASE 2: The Empty-Set Firewall (Testing Hallucination Lock)
    # -------------------------------------------------------------------------
    print("\n\033[91m[TEST CASE #2: Missing Records [] - Testing Anti-Hallucination Firewall]\033[0m")
    state_empty: TextToQueryState = {
        "messages": [HumanMessage(content="Show me current stock levels for SKU-NONEXISTENT at store 99")],
        "intent_route": "INVENTORY_LOOKUP",
        "schemas_info": None,
        "sql_query_from_ai": "SELECT current_stock FROM inventory WHERE sku = 'SKU-NONEXISTENT' AND store_id = 99",
        "raw_rows": [], # Simulating a search query that returns zero rows from SQLite
        "raw_cols": ["current_stock"],
        "contract_context": None,
        "data_found": True,
        "final_ai_reply": None
    }

    # 1. Run through the Guardrail to verify it catches the empty set
    state_empty.update(check_data_presence_guardrail(state_empty))
    # 2. Compile response to verify it triggers the protective lockdown text
    state_empty.update(final_ai_reply(state_empty))

    print("\033[1m-> AI Response to Executive:\033[0m")
    print(f"   \"{state_empty['final_ai_reply']}\"")
    print("\n" + "=" * 75)

if __name__ == "__main__":
    # Inject variables into global scope so phase2_nodes can invoke them during test cycles
    import text_query
    text_query.llm = llm
    text_query.TextToQueryState = TextToQueryState

    run_phase3_extended_test()
