from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
# Assuming models are imported from your local setup
#from main import SalesHistory, PurchaseOrder 
from src.database import get_session, PurchaseOrder, SalesHistory, Inventory

def fetch_executive_dashboard_metrics():
    """
    Queries and aggregates metrics from SQLite for the Strategic Executive View.
    """

    session = get_session()


    # 1. Total Volume Sold across all nodes
    total_sold = session.query(func.sum(SalesHistory.units_sold)).scalar() or 0
    
    # 2. Autonomous Purchase Orders built by LangGraph agents
    ai_approved = session.query(func.count(PurchaseOrder.id)).filter(
        PurchaseOrder.approved_by == "Human Manager (via AI Assistant)"
    ).scalar() or 0
    
    # 3. Capital in transit via approved workflows
    in_transit = session.query(func.sum(PurchaseOrder.quantity)).filter(
        PurchaseOrder.status == "APPROVED"
    ).scalar() or 0

    # 4. Daily Sales Run Rate distribution
    trend_results = session.query(
        func.strftime('%m-%d', SalesHistory.sale_date).label('day'),
        func.sum(SalesHistory.units_sold).label('total')
    ).group_by('day').order_by('day').limit(10).all()
    
    sales_trend = [{"date": item.day, "sales": item.total} for item in trend_results]

    # 5. Store Performance metrics split by ID node
    store_results = session.query(
        SalesHistory.store_id,
        func.sum(SalesHistory.units_sold).label('total')
    ).group_by(SalesHistory.store_id).all()
    
    store_performance = [
        {"store": f"Store #{item.store_id}", "units": item.total} for item in store_results
    ]

    # Return unified payload mapping to the Pydantic schema structure
    return {
        "kpis": {
            "totalSold": total_sold,
            "aiApproved": ai_approved,
            "inTransit": in_transit
        },
        "salesTrend": sales_trend,
        "storePerformance": store_performance
    }
# ... keep your existing fetch_executive_dashboard_metrics function above ...

def fetch_ai_decision_history( limit: int = 10):
    """
    Queries the latest purchase orders generated or processed by the AI Agent 
    to provide an auditable decision trail for supply chain executives.
    """
    session = get_session()
    # Join PurchaseOrder with Inventory on SKU to fetch product names alongside agent actions
    results = session.query(
        PurchaseOrder.id,
        PurchaseOrder.po_number,
        PurchaseOrder.store_id,
        PurchaseOrder.sku,
        PurchaseOrder.quantity,
        PurchaseOrder.status,
        PurchaseOrder.created_at,
        PurchaseOrder.approved_by,
        Inventory.product_name,
        Inventory.reorder_point,
        Inventory.current_stock
    ).join(
        Inventory, 
        (PurchaseOrder.sku == Inventory.sku) & (PurchaseOrder.store_id == Inventory.store_id),
        isouter=True
    ).filter(
        PurchaseOrder.approved_by == "Human Manager (via AI Assistant)"
    ).order_by(
        PurchaseOrder.created_at.desc()
    ).limit(limit).all()

    decision_history = []
    for item in results:
        # Generate automated reasoning strings based on database state context
        stock = item.current_stock if item.current_stock is not None else 0
        rop = item.reorder_point if item.reorder_point is not None else 20
        
        if item.status.upper() == "APPROVED":
            reasoning = f"Current stock ({stock}) dropped below safety threshold ({rop}). Autonomous pipeline triggered replenishment order for {item.quantity} units."
        elif item.status.upper() == "DRAFT":
            reasoning = f"Inventory check flagged optimization window. Draft generated for {item.quantity} units. Awaiting human validation loop."
        else:
            reasoning = f"Anomaly detected in seasonal sales trend calculations. Order flagged and rejected by internal validation node."

        decision_history.append({
            "id": item.id,
            "timestamp": item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else "Just Now",
            "poNumber": item.po_number,
            "storeId": item.store_id,
            "sku": item.sku,
            "productName": item.product_name or "Unknown Item",
            "quantity": item.quantity,
            "status": item.status,
            "reasoning": reasoning
        })

    return decision_history



def fetch_retail_dashboard_metrics():
    """
    Queries and aggregates metrics from SQLite for the Commercial Retail Owner View.
    """
    session = get_session()

    # 1. Count of unique SKUs out of stock entirely across all nodes
    stockouts = session.query(func.count(Inventory.id)).filter(
        Inventory.current_stock == 0
    ).scalar() or 0
    
    # 2. Total unique product listings currently active across the system
    unique_skus = session.query(func.count(func.distinct(Inventory.sku))).scalar() or 0
    
    # 3. Open purchase orders waiting for executive/manager confirmation
    draft_pos = session.query(func.count(PurchaseOrder.id)).filter(
        PurchaseOrder.status == "DRAFT"
    ).scalar() or 0

    # 4. Aggregating Stock Levels vs Reorder Caps grouped by Store Nodes
    store_stock_results = session.query(
        Inventory.store_id,
        func.sum(Inventory.current_stock).label('current'),
        func.sum(Inventory.reorder_point).label('reorder')
    ).group_by(Inventory.store_id).all()
    
    stock_by_store = [
        {
            "store": f"Store #{item.store_id}", 
            "current": item.current, 
            "reorder": item.reorder
        } for item in store_stock_results
    ]

    # 5. Distributing Purchase Order Lifecycle metrics for the Donut/Pie Chart
    po_status_results = session.query(
        PurchaseOrder.status,
        func.count(PurchaseOrder.id).label('count')
    ).group_by(PurchaseOrder.status).all()
    
    # Map strict color schemas to statuses directly from backend metadata
    status_color_map = {
        "DRAFT": "#eab308",     # Amber
        "APPROVED": "#22c55e",  # Green
        "REJECTED": "#ef4444"   # Red
    }
    
    po_status = [
        {
            "name": item.status,
            "value": item.count,
            "color": status_color_map.get(item.status.upper(), "#64748b")
        } for item in po_status_results
    ]

    return {
        "kpis": {
            "stockouts": stockouts,
            "uniqueSkus": unique_skus,
            "draftPos": draft_pos
        },
        "stockByStore": stock_by_store,
        "poStatus": po_status
    }


def fetch_warehouse_dashboard_metrics():
    """
    Queries and aggregates metrics from SQLite for the Operational Warehouse Manager View.
    """

    session = get_session()
    # 1. KPI: Items currently operating below or equal to their safety reorder point
    needs_reorder = session.query(func.count(Inventory.id)).filter(
        Inventory.current_stock <= Inventory.reorder_point
    ).scalar() or 0
    
    # 2. KPI: Incoming fulfillment backlog (Orders approved by AI/Execs that need receiving)
    pending_fulfillment = session.query(func.count(PurchaseOrder.id)).filter(
        PurchaseOrder.status == "APPROVED"
    ).scalar() or 0
    
    # 3. KPI: Unique physical layouts / active shelf codes configured in inventory
    active_zones = session.query(func.count(func.distinct(Inventory.location))).scalar() or 0

    # 4. Graph Data: Critical Replenishment Runway (Find items furthest below reorder thresholds)
    # Calculates deficit: (current_stock - reorder_point). Lowest numbers are the most severe bottlenecks.
    runway_results = session.query(
        Inventory.product_name,
        Inventory.sku,
        Inventory.current_stock,
        Inventory.reorder_point
    ).filter(Inventory.current_stock <= Inventory.reorder_point)\
     .order_by((Inventory.current_stock - Inventory.reorder_point).asc())\
     .limit(5).all()
     
    runway = [
        {
            "name": f"{item.sku} ({item.product_name[:10]}...)" if len(item.product_name) > 10 else item.sku,
            "stock": item.current_stock,
            "min": item.reorder_point
        } for item in runway_results
    ]

    # 5. Graph Data: Physical Stock Spread across storage sectors/locations
    zone_results = session.query(
        Inventory.location,
        func.sum(Inventory.current_stock).label('total_stock')
    ).group_by(Inventory.location).all()
    
    zone_spread = [
        {
            "name": item.location if item.location else "Unassigned",
            "value": item.total_stock
        } for item in zone_results
    ]

    return {
        "kpis": {
            "needsReorder": needs_reorder,
            "pendingFulfillment": pending_fulfillment,
            "zones": active_zones
        },
        "runway": runway,
        "zoneSpread": zone_spread
    }    

def update_inventory_safety_threshold( store_id: int, sku: str, new_threshold: int):
    """
    Mutates the reorder point of a specific item SKU across a target store node.
    """
    session = get_session()

    item = session.query(Inventory).filter(
        Inventory.store_id == store_id,
        Inventory.sku == sku
    ).first()
    
    if not item:
        return False
        
    item.reorder_point = new_threshold
    session.commit()
    return True

def promote_draft_purchase_order(po_number: str, manual_user: str):
    """
    Promotes an automated LangGraph DRAFT order to APPROVED status,
    tracking the user who performed the human override.
    """
    session = get_session()

    po = session.query(PurchaseOrder).filter(PurchaseOrder.po_number == po_number).first()
    
    if not po:
        return False
        
    po.status = "APPROVED"
    po.approved_by = manual_user  # Overwrites 'AI Agent' flag with the human reviewer name
    session.commit()
    return True

