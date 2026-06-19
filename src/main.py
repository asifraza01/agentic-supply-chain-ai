"""
Main entry point for the Supply Chain Agent.
Orchestrates the multi-agent workflow with Human-in-the-Loop.
"""
import uuid
import os

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
import sys

from src.state import SupplyChainState
from src.agents.investigator import investigator_node
from src.agents.optimizer import optimizer_node
from src.agents.explainer import explainer_node
from src.agents.executor import executor_node

# Load environment variables
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT")


def build_graph():
    """
    Build the LangGraph workflow.
    
    Flow:
    START -> Investigator -> Optimizer -> Explainer -> [HUMAN APPROVAL] -> Executor -> END
    """
    
    # Initialize the graph
    workflow = StateGraph(SupplyChainState)
    
    # Add nodes
    workflow.add_node("investigator", investigator_node)
    workflow.add_node("optimizer", optimizer_node)
    workflow.add_node("explainer", explainer_node)
    workflow.add_node("executor", executor_node)
    
    # Define edges
    workflow.add_edge(START, "investigator")
    workflow.add_edge("investigator", "optimizer")
    workflow.add_edge("optimizer", "explainer")
    workflow.add_edge("explainer", "executor")
    workflow.add_edge("executor", END)
    
    # Add Human-in-the-Loop interrupt BEFORE the executor
    # This pauses the graph and waits for human approval
    app = workflow.compile(
        checkpointer=MemorySaver(),
        interrupt_before=["executor"]
    )
    
    return app


def run_agent(store_id: int, sku: str, alert: str):
    """
    Run the supply chain agent with a specific alert.
    """
    print("=" * 80)
    print("🚀 SUPPLY CHAIN AGENT - STARTING")
    print("=" * 80)
    
    # Build the graph
    app = build_graph()
    
    # Initial state
    initial_state = {
        "alert": alert,
        "store_id": store_id,
        "sku": sku,
        "inventory_data": None,
        "sales_velocity_data": None,
        "reorder_calculation": None,
        "proposal": None,
        "confidence": None,
        "human_approved": None,
        "human_feedback": None,
        "purchase_order": None,
        "error": None
    }
    
    # Configuration with thread_id for checkpointing
    #config = {"configurable": {"thread_id": "supply-chain-001"}}
    thread_id = f"kafka-event-{uuid.uuid4().hex[:8]}"
    config = {"configurable": {"thread_id": thread_id}}
    print(f"🧵 Starting LangGraph Thread: {thread_id}")
    # Run the graph until it hits the interrupt
    print("\n📋 Running agent workflow...")
    
    # Stream through the graph to see progress
    for event in app.stream(initial_state, config, stream_mode="updates"):
        # Check if we hit an error
        for node_name, node_output in event.items():
            if 'error' in node_output:
                print(f"\n❌ ERROR in {node_name}: {node_output['error']}")
                return
    
    # Get the final state after the interrupt
    final_state = app.get_state(config).values
    
    # Check for errors
    if final_state.get('error'):
        print(f"\n❌ ERROR: {final_state['error']}")
        return
    
    # Display the proposal
    print("\n" + "=" * 80)
    print("📝 AI PROPOSAL FOR HUMAN REVIEW")
    print("=" * 80)
    print(final_state['proposal'])
    print(f"\nConfidence: {final_state['confidence']:.0%}")
    print("=" * 80)
    
    # Human-in-the-Loop: Ask for approval
    print("\n👤 HUMAN APPROVAL REQUIRED")
    print("-" * 80)
    
    while True:
        response = input("\nDo you approve this purchase order? (yes/no/edit): ").strip().lower()
        
        if response in ['yes', 'y']:
            print("\n✅ Approved! Resuming workflow...")
            # Update the state with human approval
            app.update_state(
                config,
                {"human_approved": True, "human_feedback": "Approved"}
            )
            break
        
        elif response in ['no', 'n']:
            print("\n❌ Rejected. Workflow terminated.")
            app.update_state(
                config,
                {"human_approved": False, "human_feedback": "Rejected"}
            )
            return
        
        elif response in ['edit', 'e']:
            print("\n✏️  Edit mode not implemented in Phase 1.")
            print("   (This would allow the human to modify the quantity before approving)")
            continue
        
        else:
            print("   Please enter 'yes', 'no', or 'edit'")
    
    # Resume the graph from the checkpoint (pass None, not the full state!)
    print("\n⚡ Executing purchase order...")
    
    # Stream the remaining execution
    for event in app.stream(None, config, stream_mode="updates"):
        for node_name, node_output in event.items():
            print(f"   → {node_name} completed")
            if 'error' in node_output:
                print(f"   ❌ ERROR: {node_output['error']}")
                return
    
    # Get the final state
    final_state = app.get_state(config).values
    
    # Display final result
    print("\n" + "=" * 80)
    print("✅ WORKFLOW COMPLETE")
    print("=" * 80)
    
    if final_state.get('purchase_order'):
        po = final_state['purchase_order']
        if po['success']:
            print(f"\n🎉 SUCCESS!")
            print(f"   PO Number: {po['po_number']}")
            print(f"   Store: {po['store_id']}")
            print(f"   SKU: {po['sku']}")
            print(f"   Quantity: {po['quantity']} units")
            print(f"   Status: {po['status']}")
        else:
            print(f"\n❌ FAILED: {po['message']}")
    else:
        print("\n⚠️  No purchase order was created.")
    
    print("\n" + "=" * 80)

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