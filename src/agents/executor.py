"""
Executor Agent: Creates the purchase order after human approval.
This agent only runs if the human approves the proposal.
"""

from typing import Dict, Any
from src.state import SupplyChainState
from src.tools.po_tools import create_purchase_order


def executor_node(state: SupplyChainState) -> Dict[str, Any]:
    """
    Execute the purchase order if approved by human.
    """
    print("\n⚡ [EXECUTOR] Processing order...")
    
    try:
        # Check if human approved
        if not state.get('human_approved'):
            print("   ✗ Order rejected by human")
            return {
                "purchase_order": {
                    "success": False,
                    "message": "Order rejected by human approver"
                }
            }
        
        # Check if we have the calculation
        if not state.get('reorder_calculation'):
            return {
                "error": "Cannot execute: Missing reorder calculation"
            }
        
        reorder = state['reorder_calculation']
        
        print(f"   → Creating PO for {reorder['recommended_order_quantity']} units...")
        
        # Create the purchase order
        po_result = create_purchase_order(
            store_id=state['store_id'],
            sku=state['sku'],
            quantity=reorder['recommended_order_quantity'],
            approved_by="Human Manager (via AI Assistant)"
        )
        
        if po_result['success']:
            print(f"   ✓ Purchase order created: {po_result['po_number']}")
        else:
            print(f"   ✗ Failed to create PO: {po_result['message']}")
        
        return {
            "purchase_order": po_result
        }
    
    except Exception as e:
        return {
            "error": f"Executor failed with exception: {str(e)}"
        }