"""
Tools for querying inventory and sales data from the database.
These are deterministic functions - the LLM calls them, but doesn't do the logic.
"""
from typing import Dict, Any
from sqlalchemy import func
from datetime import datetime, timedelta
from src.database import get_session, Inventory, SalesHistory
from src.schemas.tool_schemas import (
    InventoryQuery, InventoryData,
    SalesVelocityQuery, SalesVelocityData
)


def get_current_inventory(store_id: int, sku: str) -> Dict[str, Any]:
    """
    Get current inventory levels for a specific store and SKU.
    
    Args:
        store_id: The store ID (1-10)
        sku: The product SKU (e.g., 'SKU-100')
    
    Returns:
        Dictionary with inventory data
    """
    # Validate input with Pydantic
    query = InventoryQuery(store_id=store_id, sku=sku)
    
    session = get_session()
    try:
        inventory = session.query(Inventory).filter_by(
            store_id=query.store_id,
            sku=query.sku
        ).first()
        
        if not inventory:
            return {
                "error": f"No inventory found for store {store_id}, SKU {sku}",
                "found": False
            }
        
        # Build response using Pydantic schema
        data = InventoryData(
            store_id=inventory.store_id,
            sku=inventory.sku,
            product_name=inventory.product_name,
            current_stock=inventory.current_stock,
            reorder_point=inventory.reorder_point,
            location=inventory.location,
            is_below_reorder_point=inventory.current_stock < inventory.reorder_point
        )
        
        return data.model_dump()
    
    finally:
        session.close()


def get_sales_velocity(store_id: int, sku: str, days: int = 7) -> Dict[str, Any]:
    """
    Calculate sales velocity (average units sold per day) over a time period.
    
    Args:
        store_id: The store ID
        sku: The product SKU
        days: Number of days to analyze (default 7)
    
    Returns:
        Dictionary with sales velocity data
    """
    # Validate input
    query = SalesVelocityQuery(store_id=store_id, sku=sku, days=days)
    
    session = get_session()
    try:
        # Get the product name from inventory
        inventory = session.query(Inventory).filter_by(
            store_id=query.store_id,
            sku=query.sku
        ).first()
        
        if not inventory:
            return {
                "error": f"No inventory found for store {store_id}, SKU {sku}",
                "found": False
            }
        
        product_name = inventory.product_name
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=query.days)
        
        # Query sales in date range
        sales = session.query(SalesHistory).filter(
            SalesHistory.store_id == query.store_id,
            SalesHistory.sku == query.sku,
            SalesHistory.sale_date >= start_date,
            SalesHistory.sale_date <= end_date
        ).all()
        
        if not sales:
            return SalesVelocityData(
                store_id=query.store_id,
                sku=query.sku,
                product_name=product_name,
                days_analyzed=query.days,
                total_units_sold=0,
                daily_velocity=0.0,
                trend="no_data"
            ).model_dump()
        
        # Calculate metrics
        total_units = sum(sale.units_sold for sale in sales)
        daily_velocity = total_units / query.days
        
        # Determine trend (compare first half vs second half)
        midpoint = len(sales) // 2
        first_half_avg = sum(s.units_sold for s in sales[:midpoint]) / max(midpoint, 1)
        second_half_avg = sum(s.units_sold for s in sales[midpoint:]) / max(len(sales) - midpoint, 1)
        
        if second_half_avg > first_half_avg * 1.1:
            trend = "increasing"
        elif second_half_avg < first_half_avg * 0.9:
            trend = "decreasing"
        else:
            trend = "stable"
        
        data = SalesVelocityData(
            store_id=query.store_id,
            sku=query.sku,
            product_name=product_name,
            days_analyzed=query.days,
            total_units_sold=total_units,
            daily_velocity=round(daily_velocity, 2),
            trend=trend
        )
        
        return data.model_dump()
    
    finally:
        session.close()