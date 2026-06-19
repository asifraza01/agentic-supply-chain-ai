"""
Optimizer Agent: Calculates the reorder quantity using deterministic math.
This agent calls the math tool - the LLM does NOT do the calculation.
"""
from typing import Dict, Any
from src.state import SupplyChainState
from src.tools.math_tools import calculate_reorder_quantity


def optimizer_node(state: SupplyChainState) -> Dict[str, Any]:
    """
    Calculate the optimal reorder quantity based on gathered data.
    """
    print("\n🧮 [OPTIMIZER] Calculating reorder quantity...")
    
    try:
        # Check if we have the data we need
        if not state.get('inventory_data') or not state.get('sales_velocity_data'):
            return {
                "error": "Cannot optimize: Missing inventory or velocity data"
            }
        
        inventory = state['inventory_data']
        velocity = state['sales_velocity_data']
        
        # Extract values
        current_stock = inventory['current_stock']
        daily_velocity = velocity['daily_velocity']
        
        # Handle edge case: no sales
        if daily_velocity == 0:
            print("   ⚠️  No recent sales detected. Setting velocity to 1 unit/day minimum.")
            daily_velocity = 1.0
        
        print(f"   → Current stock: {current_stock} units")
        print(f"   → Daily velocity: {daily_velocity} units/day")
        print(f"   → Lead time: 3 days (default)")
        print(f"   → Safety stock: 5 days (default)")
        
        # Call the deterministic math tool
        print("   → Running calculation...")
        reorder_result = calculate_reorder_quantity(
            current_stock=current_stock,
            daily_velocity=daily_velocity,
            lead_time_days=3,
            safety_stock_days=5
        )
        
        print(f"   ✓ Recommended order: {reorder_result['recommended_order_quantity']} units")
        
        return {
            "reorder_calculation": reorder_result
        }
    
    except Exception as e:
        return {
            "error": f"Optimizer failed with exception: {str(e)}"
        }