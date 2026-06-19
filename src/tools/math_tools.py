"""
Deterministic mathematical tools for supply chain calculations.
The LLM calls these tools but does NOT do the math itself.
This prevents hallucinations and ensures 100% accuracy.
"""
from typing import Dict, Any
from src.schemas.tool_schemas import ReorderCalculation, ReorderResult


def calculate_reorder_quantity(
    current_stock: int,
    daily_velocity: float,
    lead_time_days: int = 3,
    safety_stock_days: int = 5
) -> Dict[str, Any]:
    """
    Calculate how many units to reorder based on current stock, sales velocity,
    lead time, and desired safety stock.
    
    Formula:
    - Stock needed during lead time = daily_velocity * lead_time_days
    - Safety stock = daily_velocity * safety_stock_days
    - Total needed = stock_during_lead_time + safety_stock
    - Order quantity = max(0, total_needed - current_stock)
    
    Args:
        current_stock: Current inventory units
        daily_velocity: Average units sold per day
        lead_time_days: How many days until supplier delivers
        safety_stock_days: How many days of buffer stock to maintain
    
    Returns:
        Dictionary with calculation details and recommended order quantity
    """
    # Validate input
    calc_input = ReorderCalculation(
        current_stock=current_stock,
        daily_velocity=daily_velocity,
        lead_time_days=lead_time_days,
        safety_stock_days=safety_stock_days
    )
    
    # Perform deterministic calculations
    stock_during_lead_time = int(calc_input.daily_velocity * calc_input.lead_time_days)
    safety_stock = int(calc_input.daily_velocity * calc_input.safety_stock_days)
    total_needed = stock_during_lead_time + safety_stock
    
    # Order quantity (never negative)
    recommended_order = max(0, total_needed - calc_input.current_stock)
    
    # Round up to nearest batch size (e.g., boxes of 10)
    batch_size = 10
    recommended_order = ((recommended_order + batch_size - 1) // batch_size) * batch_size
    
    # Build reasoning
    reasoning = (
        f"Current stock ({calc_input.current_stock}) will last "
        f"{calc_input.current_stock / calc_input.daily_velocity:.1f} days at current velocity. "
        f"Need {stock_during_lead_time} units to cover {calc_input.lead_time_days}-day lead time, "
        f"plus {safety_stock} units for {calc_input.safety_stock_days}-day safety stock. "
        f"Total needed: {total_needed}. "
        f"Recommended order: {recommended_order} units (rounded to batch size of {batch_size})."
    )
    
    result = ReorderResult(
        current_stock=calc_input.current_stock,
        daily_velocity=calc_input.daily_velocity,
        lead_time_days=calc_input.lead_time_days,
        safety_stock_days=calc_input.safety_stock_days,
        stock_during_lead_time=stock_during_lead_time,
        recommended_order_quantity=recommended_order,
        reasoning=reasoning
    )
    
    return result.model_dump()