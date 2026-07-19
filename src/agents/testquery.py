import os
import sqlite3
from typing import TypedDict, Optional, List, Dict, Any, Annotated
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Import the exact execution node functions we mapped out for Phase 2
from text_query import create_sql_query, execute_sql_query, run_contract_rag

load_dotenv()


# Define the State Schema matching Phase 1 & 2 definitions exactly
class TextToQueryState(TypedDict):
    messages: Annotated[list, add_messages] if 'add_messages' in globals() else list
    intent_route: str
    schemas_info: Optional[List[str]]
    sql_query_from_ai: Optional[str]
    raw_rows: Optional[List[Dict[str, Any]]]
    raw_cols: Optional[List[str]]
    contract_context: Optional[str]
    data_found: bool
    final_ai_reply: Optional[str]

def run_phase2_simulation():
    print("=" * 70)
    print("STARTING PHASE 2 INTERACTIVE ENGINE EXECUTIONS LOGS")
    print("=" * 70)

    # Generic schema context mock string to simulate our database table definition layout
    mock_inventory_schemas = [
        "Table: inventory, Columns: [(0, 'id', 'INTEGER'), (1, 'store_id', 'INTEGER'), (2, 'sku', 'VARCHAR(50)'), (3, 'product_name', 'VARCHAR(200)'), (4, 'current_stock', 'INTEGER'), (5, 'reorder_point', 'INTEGER')]"
    ]

    # --- SIMULATION 1: Standard Inventory Route Path ---
    print("\n\033[94m[SIMULATION #1: INVENTORY_LOOKUP PATHWAY]\033[0m")
    state_lookup: TextToQueryState = {
        "messages": [HumanMessage(content="Show me current stock levels for SKU-100 at store 1")],
        "intent_route": "INVENTORY_LOOKUP",
        "schemas_info": mock_inventory_schemas,
        "sql_query_from_ai": None,
        "raw_rows": None,
        "raw_cols": None,
        "contract_context": None,
        "data_found": True,
        "final_ai_reply": None
    }
    
    # Run the SQL generator, then execute it against SQLite instantly
    state_lookup.update(create_sql_query(state_lookup))
    state_lookup.update(execute_sql_query(state_lookup))
    print(f" -> Final Raw Rows Array Collected: {state_lookup['raw_rows']}")

    # --- SIMULATION 2: Agent Decision Audit Route Path ---
    print("\n\033[95m[SIMULATION #2: AGENT_AUDIT PATHWAY]\033[0m")
    state_audit: TextToQueryState = {
        "messages": [HumanMessage(content="Why did you create PO-20260717-C6F610?")],
        "intent_route": "AGENT_AUDIT",
        "schemas_info": mock_inventory_schemas,
        "sql_query_from_ai": None,
        "raw_rows": None,
        "raw_cols": None,
        "contract_context": None,
        "data_found": True,
        "final_ai_reply": None
    }
    
    # Run the generator targeting po_decisions schema specifically, then execute
    state_audit.update(create_sql_query(state_audit))
    state_audit.update(execute_sql_query(state_audit))
    print(f" -> Final Raw Rows Array Collected: {state_audit['raw_rows']}")

    # --- SIMULATION 3: Supplier SLA/Contract Contract RAG Path ---
    print("\n\033[92m[SIMULATION #3: CONTRACT_RAG PATHWAY]\033[0m")
    state_rag: TextToQueryState = {
        "messages": [HumanMessage(content="What is the lead time agreement for whole milk deliveries?")],
        "intent_route": "CONTRACT_RAG",
        "schemas_info": None,
        "sql_query_from_ai": None,
        "raw_rows": None,
        "raw_cols": None,
        "contract_context": None,
        "data_found": True,
        "final_ai_reply": None
    }
    
    # Execute vector index extraction from running local Qdrant collection directly
    try:
        state_rag.update(run_contract_rag(state_rag))
        print(" -> Extracted RAG Context String:")
        print(state_rag["contract_context"] if state_rag["contract_context"] else "   [Empty String Context]")
    except Exception as error:
        print(f" ❌ Qdrant/LlamaIndex verification step skipped or offline: {error}")
        print("    (Ensure your local Qdrant container port 6333 is launched or seeded)")

    print("\n" + "=" * 70)
    print("PHASE 2 COMPONENT ROUTING PIPELINES EXECUTED SUCCESSFULLY")
    print("=" * 70)

if __name__ == "__main__":
    # Troubleshooting check to guide file setup
    if not os.getenv("GROQ_API_KEY"):
        print("❌ Warning: GROQ_API_KEY environment variable is missing from your configuration.")
    run_phase2_simulation()
