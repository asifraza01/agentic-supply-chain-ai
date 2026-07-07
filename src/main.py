"""
Main entry point for the Supply Chain Agent.
Orchestrates the multi-agent workflow with Human-in-the-Loop.
"""
import uuid
import os
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
# Create a shared SQLite database for the checkpointer

#CHECKPOINT_DB = "langgraph_checkpoints.db"

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CHECKPOINT_DB = PROJECT_ROOT / "langgraph_checkpoints.db"

# Ensure the database file exists
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
import sys

from src.state import SupplyChainState
from src.agents.investigator import investigator_node
from src.agents.optimizer import optimizer_node
from src.agents.explainer import explainer_node
from src.agents.executor import executor_node
from src.state_manager import add_pending

# Load environment variables
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT")



def build_graph():
    """
    Build the LangGraph workflow with persistent SQLite checkpointer.
    """
    workflow = StateGraph(SupplyChainState)
    workflow.add_node("investigator", investigator_node)
    workflow.add_node("optimizer", optimizer_node)
    workflow.add_node("explainer", explainer_node)
    workflow.add_node("executor", executor_node)
    
    workflow.add_edge(START, "investigator")
    workflow.add_edge("investigator", "optimizer")
    workflow.add_edge("optimizer", "explainer")
    workflow.add_edge("explainer", "executor")
    workflow.add_edge("executor", END)

    
    # 🚨 CRITICAL FIX: Use SQLite checkpointer instead of MemorySaver
    conn = sqlite3.connect(CHECKPOINT_DB, check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    
    app = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["executor"]
    )
    
    return app


def run_agent(store_id: int, sku: str, alert: str):
    """
    Run the supply chain agent. 
    Now asynchronous: pauses at Human-in-the-Loop and saves state to API.
    """
    print("=" * 80)
    print(" SUPPLY CHAIN AGENT - STARTING")
    print("=" * 80)
    
    app = build_graph()
    
    thread_id = f"event-{uuid.uuid4().hex[:8]}"
    config = {"configurable": {"thread_id": thread_id}}
    print(f"🧵 Starting LangGraph Thread: {thread_id}")
    
    initial_state = {
        "alert": alert,
        "store_id": store_id,
        "sku": sku,
        "inventory_data": None,
        "sales_velocity_data": None,
        "contract_context": None,
        "reorder_calculation": None,
        "proposal": None,
        "confidence": None,
        "human_approved": None,
        "human_feedback": None,
        "purchase_order": None,
        "error": None
    }
    
    print("\n📋 Running agent workflow...")
    
    # Stream until it hits the interrupt
    for event in app.stream(initial_state, config, stream_mode="updates"):
        for node_name, node_output in event.items():
            if 'error' in node_output:
                print(f"\n❌ ERROR in {node_name}: {node_output['error']}")
                return
    
    # 🚨 CRITICAL CHANGE: Get the paused state and save it to the API bridge
    final_state = app.get_state(config).values
    
    if final_state.get('error'):
        print(f"\n❌ ERROR: {final_state['error']}")
        return

    print("\n⏸️  AGENT PAUSED FOR HUMAN APPROVAL. Saving to API...")
    
    # Save to global state manager so FastAPI can serve it to the UI
    add_pending(thread_id, final_state)
    
    print(f"✅ Thread {thread_id} saved to pending approvals queue.")
    print("=" * 80)
    
    # Function returns here immediately. No more input() blocking!

if __name__ == "__main__":
    # Default: Test with our problem scenario
    # Store 4, SKU-100 (Organic Milk) - critically low stock
    store_id = 4
    sku = "SKU-100"
    alert = f"Store #{store_id} is reporting critically low stock on {sku} (Organic Milk). Investigate and propose a solution."
    
    # Allow command line arguments for testing other scenarios
    if len(sys.argv) >= 3:
        store_id = int(sys.argv[1])
        sku = sys.argv[2]
        alert = f"Store #{store_id} needs inventory review for {sku}."
    
    run_agent(store_id, sku, alert)