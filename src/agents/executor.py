# src/agents/executor_node.py
import json
from datetime import datetime
from src.tools.po_tools import create_purchase_order, record_decision
from src.state import SupplyChainState
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig  # ✅ Add this import

def executor_node(state: SupplyChainState, config: RunnableConfig) -> Dict[str, Any]:
    """Execute the purchase order and record the full decision audit."""
    
    print("\n⚡ [EXECUTOR] Processing order...")
    
    # 1. Get thread_id from config (Best Practice)
    thread_id = config["configurable"].get("thread_id")
    human_approved = state.get("human_approved")
    
    # 2. ✅ Extract the CORRECT keys from your SupplyChainState
    investigator_context = state.get('contract_context', 'No RAG context available')
    explainer_proposal = state.get('proposal', 'No proposal available')
    optimizer_calculation = state.get('reorder_calculation', {})
    confidence_score = state.get('confidence', 0.0)
    
    print(f"   → Thread ID: {thread_id}")
    print(f"   → Human Approved: {human_approved}")

    # 3. Check if we have the calculation
    if not optimizer_calculation:
        return {
            "error": "Cannot execute: Missing reorder calculation"
        }
        
    # 4. Determine status and create PO
    po_status = "APPROVED" if human_approved else "REJECTED"
    print(f"   → Creating PO with status: {po_status}")
    
    po_result = create_purchase_order(
        store_id=state.get('store_id'),
        status=po_status,
        sku=state.get('sku'),
        quantity=optimizer_calculation.get('recommended_order_quantity', 0),
        approved_by="Human Manager (via AI Assistant)" 
    )
    
    # 5. ✅ Record the decision audit with the CORRECT variables
    if po_result.get('success'):
        print(f"   ✓ Purchase order created: {po_result.get('po_number')}")
        
        # Call your record_decision function
        record_decision(
            thread_id=thread_id,
            po_number=po_result.get('po_number'),
            sku=state.get('sku'),
            store_id=state.get('store_id'),
            quantity=optimizer_calculation.get('recommended_order_quantity', 0),
            decision=po_status,
            decided_by="Human Manager (via AI Assistant)",
            rejection_reason=state.get('rejection_reason', 'N/A'),
            
            # ✅ Now passing the correctly extracted state data!
            investigator_context=investigator_context,
            optimizer_calculation=json.dumps(optimizer_calculation, default=str),
            explainer_proposal=explainer_proposal,
            confidence_score=confidence_score,
            
            # Keep the full snapshot for ultimate debugging safety
            full_state_snapshot=json.dumps({
                k: v for k, v in state.items() 
                if k != 'inventory_data' and k != 'sales_velocity_data' # Trim large dicts if needed
            }, default=str)
        )
    else:
        print(f"   ✗ Failed to create PO: {po_result.get('message')}")
        
    return {
        "purchase_order": po_result,
        "decision_recorded": True
    }