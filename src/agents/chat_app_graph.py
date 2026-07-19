import os
import sqlite3
from typing import TypedDict, Optional, List, Dict, Any, Annotated
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
CHATCHECKPOINT_DB = "v2_chat_langgraph_chatcheckpoints.db"

from src.agents.text_query import (
    intent_router,
    create_sql_query,
    execute_sql_query,
    run_contract_rag,
    check_data_presence_guardrail,
    final_ai_reply,
    TextToQueryState
)
# Import your validated logic workers from Phase 1, 2, and 3
#from src.agents.text_query import intent_router, create_sql_query, execute_sql_query, run_contract_rag, check_data_presence_guardrail, final_ai_reply,TextToQueryState
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

# Connect to your permanent checkpoint file

#memory_layer = MemorySaver()

load_dotenv()

# =========================================================================
# 1. STATE CLEARING GUARD NODE
# =========================================================================
def input_init_and_flush(state:TextToQueryState):
    print("\n" + "="*50)
    print("🔄 [STARTING NEW GRAPH TURN] Flushed Stale Data Contexts")
    print("="*50)
    
    # We return None for all data slots to clear out variables from the previous turn,
    # preventing old SQL rows from lingering and corrupting new questions.
    return {
        "intent_route": "",
        "sql_query_from_ai": None,
        "raw_rows": None,
        "raw_cols": None,
        "contract_context": None,
        "data_found": True
    }

# =========================================================================
# 2. CONDITIONAL EDGE ROUTER DEFINITIONS
# =========================================================================
def route_by_intent(state: TextToQueryState) -> str:
    """
    Evaluates the intent_route saved by the intent_router node and
    directs the graph engine down the matching architectural pathway.
    """
    route = state.get("intent_route", "INVENTORY_LOOKUP")
    
    if route == "CONTRACT_RAG":
        return "contract_rag_path"
    elif route == "AGENT_AUDIT":
        return "agent_audit_path"
    else:
        return "inventory_lookup_path"

# =========================================================================
# 3. GRAPH COMPILATION WORKSPACE
# =========================================================================
builder = StateGraph(TextToQueryState)

# Add all pipeline action nodes
builder.add_node("input_init", input_init_and_flush)
builder.add_node("router", intent_router)
builder.add_node("createsql", create_sql_query)
builder.add_node("exesql", execute_sql_query)
builder.add_node("contract_rag", run_contract_rag)
builder.add_node("guardrail", check_data_presence_guardrail)
builder.add_node("final_reply", final_ai_reply)

# Define static structural flows
builder.add_edge(START, "input_init")
builder.add_edge("input_init", "router")

# Define the Three-Way Conditional Router routing decisions
builder.add_conditional_edges(
    "router",
    route_by_intent,
    {
        "inventory_lookup_path": "createsql",  # Path A: Standard SQL
        "agent_audit_path": "createsql",       # Path B: po_decisions Audit SQL
        "contract_rag_path": "contract_rag"    # Path C: Qdrant Vector RAG
    }
)

# Connect execution endpoints down to the defensive guardrail firewall

builder.add_edge("createsql", "exesql")
builder.add_edge("exesql", "guardrail")
builder.add_edge("contract_rag", "guardrail")

# Direct the guardrail to compile the final formatted response text
builder.add_edge("guardrail", "final_reply")
builder.add_edge("final_reply", END)


checkpoint_conn = sqlite3.connect(CHATCHECKPOINT_DB, check_same_thread=False)
chatcheckpointer = SqliteSaver(checkpoint_conn)

# Compile your graph using the permanent database checkpointer
supply_chain_agent = builder.compile(checkpointer=chatcheckpointer)
# Initialize an in-memory checkpointer session repository

#supply_chain_agent = builder.compile(checkpointer=memory_layer)

print("🎉 Agentic Supply Chain Graph Compiled Successfully with State Guards.")
