"""
LangGraph State definition.
This is the shared memory that flows between all agents in the workflow.
"""
from typing import TypedDict, Optional, Dict, Any, Annotated
from langgraph.graph.message import add_messages


class SupplyChainState(TypedDict):
    contract_context: Optional[str]
    """
    The state that flows through the supply chain agent graph.
    
    Each agent reads from this state, performs its task, and updates it.
    """
    # Initial input
    alert: str  # The natural language alert (e.g., "Store 4 is low on Organic Milk")
    store_id: int
    sku: str
    
    # Data gathered by Investigator Agent
    inventory_data: Optional[Dict[str, Any]]
    sales_velocity_data: Optional[Dict[str, Any]]
    
    # Calculations by Optimizer Agent
    reorder_calculation: Optional[Dict[str, Any]]
    
    # Proposal by Explainer Agent
    proposal: Optional[str]
    confidence: Optional[float]
    
    # Human-in-the-Loop
    human_approved: Optional[bool]
    human_feedback: Optional[str]
    
    # Execution result
    purchase_order: Optional[Dict[str, Any]]
    
    # Error tracking
    error: Optional[str]