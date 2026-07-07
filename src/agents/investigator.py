"""
Investigator Agent: Gathers inventory, sales data, AND supplier contract context.
"""
from typing import Dict, Any
from src.state import SupplyChainState
from src.tools.inventory_tools import get_current_inventory, get_sales_velocity
from src.tools.rag_tools import search_supplier_contracts


def investigator_node(state: SupplyChainState) -> Dict[str, Any]:
    """
    Investigate the alert by gathering inventory, sales, and contract data.
    """
    print("\n🔍 [INVESTIGATOR] Gathering data...")
    print(f"   Alert: {state['alert']}")
    print(f"   Store: {state['store_id']}, SKU: {state['sku']}")
    
    try:
        # 1. Get current inventory (SQL)
        print("   → Querying inventory (SQL)...")
        inventory_data = get_current_inventory(
            store_id=state['store_id'],
            sku=state['sku']
        )
        if 'error' in inventory_data:
            return {"error": f"Investigation failed: {inventory_data['error']}"}
        print(f"   ✓ Current stock: {inventory_data['current_stock']} units")
        
        # 2. Get sales velocity (SQL)
        print("   → Calculating sales velocity (SQL)...")
        velocity_data = get_sales_velocity(
            store_id=state['store_id'],
            sku=state['sku'],
            days=7
        )
        if 'error' in velocity_data:
            return {"error": f"Investigation failed: {velocity_data['error']}"}
        print(f"   ✓ Daily velocity: {velocity_data['daily_velocity']} units/day")

        # 3. Search Supplier Contracts (Qdrant RAG) 🚀 NEW!
        print("   → Searching supplier contracts & SLAs (Qdrant RAG)...")
        # We craft a smart query for the vector DB based on the SKU
        rag_query = f"Lead time, minimum order quantity (MOQ), penalties for late delivery, and safety stock requirements for {state['sku']}"
        
        contract_context = search_supplier_contracts(rag_query)
        print(f"   ✓ Retrieved {len(contract_context)} characters of contracinventory_datat context.")
        
        return {
            "inventory_data": inventory_data,
            "sales_velocity_data": velocity_data,
            "contract_context": contract_context
        }
    
    except Exception as e:
        return {"error": f"Investigator failed with exception: {str(e)}"}