"""
FastAPI Backend for the Supply Chain Control Tower.
"""
import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys

import os

# Add parent directory to path so we can import src
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.state_manager import get_all_pending, get_pending, remove_pending
#from src.agents.text_to_query_node import answer_question
from src.agents.text_query import answer_question_v2
from src.tools.crud import *
from src.main import build_graph
from src.database import get_session, PurchaseOrder,PODecision

#from src.agents.text_to_query import text_to_query_node,generate_sql
#from src.agents.query_agent import 

app = FastAPI(title="Supply Chain Control Tower API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ], # Added both
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# --- Endpoints ---

@app.get("/api/stats")
async def get_stats():
    """Get dashboard statistics."""
    conn = sqlite3.connect("/home/asifubuntu/Documents/dev/supply-chain-agent/data/mock_erp.db")
    cursor = conn.cursor()
    
    # Count rejected
    cursor.execute("SELECT COUNT(*) FROM purchase_orders WHERE status = 'REJECTED'")
    rejected_count = cursor.fetchone()[0]
    
    # Count approved (from purchase_orders)
    cursor.execute("SELECT COUNT(*) FROM purchase_orders WHERE status = 'APPROVED'")
    approved_count = cursor.fetchone()[0]
    
    return {
        "rejected": rejected_count,
        "approved": approved_count,
        "total_processed": approved_count
    }

@app.get("/api/pending-actions")
async def get_pending_actions():
    """Fetches all paused LangGraph threads for the UI."""
    pending = get_all_pending()
    return pending

class ApproveRequest(BaseModel):
    thread_id: str
    action: str = "approve"  # Default to approve
    reason: str = None  # ← Add this field

# class ChatRequest(BaseModel):
#     message: str

class ChatRequest(BaseModel):
    thread_id: str
    message: str

class ChatResponse(BaseModel):  
    reply: str
 
# --- Pydantic Data Schemas for Dashbaord---
class KpiMetrics(BaseModel):
    totalSold: int
    aiApproved: int
    inTransit: int

class SalesTrendItem(BaseModel):
    date: str
    sales: int

class StorePerformanceItem(BaseModel):
    store: str
    units: int

class ExecutiveDashboardResponse(BaseModel):
    kpis: KpiMetrics
    salesTrend: List[SalesTrendItem]
    storePerformance: List[StorePerformanceItem]    


# 2. Pydantic definitions for retail:
class RetailKpis(BaseModel):
    stockouts: int
    uniqueSkus: int
    draftPos: int

class StockStoreItem(BaseModel):
    store: str
    current: int
    reorder: int

class PoStatusItem(BaseModel):
    name: str
    value: int
    color: str

class RetailDashboardResponse(BaseModel):
    kpis: RetailKpis
    stockByStore: List[StockStoreItem]
    poStatus: List[PoStatusItem]

# 1. Add these Pydantic schema models along with your others:
class WarehouseKpis(BaseModel):
    needsReorder: int
    pendingFulfillment: int
    zones: int

class RunwayItem(BaseModel):
    name: str
    stock: int
    min: int

class ZoneSpreadItem(BaseModel):
    name: str
    value: int

class WarehouseDashboardResponse(BaseModel):
    kpis: WarehouseKpis
    runway: List[RunwayItem]
    zoneSpread: List[ZoneSpreadItem]

# 1. Add this Pydantic validation schema alongside your others:
class AiDecisionItem(BaseModel):
    id: int
    timestamp: str
    poNumber: str
    storeId: int
    sku: str
    productName: str
    quantity: int
    status: str
    reasoning: str

# 1. Add these lightweight data payload schemas alongside your others:
class ThresholdUpdateRequest(BaseModel):
    store_id: int
    sku: str
    new_threshold: int

class PromotionRequest(BaseModel):
    po_number: str
    user_name: str


@app.post("/api/approve-action")
async def approve_action(request: ApproveRequest):
    thread_id = request.thread_id
    action = request.action
    
    state = get_pending(thread_id)
    if not state:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    app_graph = build_graph()
    config = {"configurable": {"thread_id": thread_id}}
    
    if action == "approve":
        print(f"\n✅ API: Resuming thread {thread_id} with APPROVAL...")
        app_graph.update_state(config, {
            "human_approved": True,
            "human_feedback": "Approved via UI"
        })
    elif action == "reject":
        print(f"\n🚫 API: Resuming thread {thread_id} with REJECTION...")
        app_graph.update_state(config, {
            "human_approved": False,
            "human_feedback": "Rejected via UI",
            "rejection_reason": request.reason or "No reason provided",  # ← Capture reason
            "POstatusfromUI": {"status": "Rejected"}
        })
    
    # Resume the graph (executor will run and save the audit)
    for event in app_graph.stream(None, config, stream_mode="updates"):
        print(f"📊 Event: {event}")
    
    # Clean up
    remove_pending(thread_id)
    
    return {
        "status": "success",
        "message": f"Order {action}d",
        "decision_recorded": True
    }


@app.get("/api/decisions")
async def get_decisions(limit: int = 50):
    """Get all decision audit records."""
    session = get_session()
    
    try:
        decisions = session.query(PODecision)\
            .order_by(PODecision.decided_at.desc())\
            .limit(limit)\
            .all()
        
        return [
            {
                "id": d.id,
                "thread_id": d.thread_id,
                "po_number": d.po_number,
                "sku": d.sku,
                "store_id": d.store_id,
                "quantity": d.quantity,
                "decision": d.decision,
                "decided_at": d.decided_at.isoformat() if d.decided_at else None,
                "decided_by": d.decided_by,
                "rejection_reason": d.rejection_reason,
                "investigator_context": d.investigator_context,
                "optimizer_calculation": d.optimizer_calculation,
                "explainer_proposal": d.explainer_proposal,
                "confidence_score": d.confidence_score
            }
            for d in decisions
        ]
    finally:
        session.close()

# POST endpoint to receive the user input and return a message

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Resumes a paused LangGraph thread with human approval."""
    print(f"Received thread_id: {request.thread_id}")
    print(f"Received message: {request.message}")
    config = {"configurable": {"thread_id": request.thread_id}}
    #response_request = answer_question(request.message, config)
    response_request = answer_question_v2(request.message, config)
    
    return {"reply":response_request}

### Dashboard
# --- Executive API Endpoint ---



# --- Endpoint Routes ---
@app.get("/api/dashboard/executive", response_model=ExecutiveDashboardResponse)
def get_executive_dashboard():
    # Call the clean isolated operation from crud.py
    return fetch_executive_dashboard_metrics()

# 3. Endpoint retao; executive dashboard route:
@app.get("/api/dashboard/retail", response_model=RetailDashboardResponse)
def get_retail_dashboard():
    return fetch_retail_dashboard_metrics()


# 2. Add this route below your retail endpoint:
@app.get("/api/dashboard/warehouse", response_model=WarehouseDashboardResponse)
def get_warehouse_dashboard():
    return fetch_warehouse_dashboard_metrics()



# 2. Add this route endpoint below your other dashboard endpoints:
@app.get("/api/dashboard/ai-history", response_model=List[AiDecisionItem])
def get_ai_decision_history():
    return fetch_ai_decision_history()

# def generate_chat(message:str)->str:
#         return f"You asked: '{message}'. This is a dummy response - later, LangGraph will handle this!"




# 2. Add these two POST request handlers below your dashboard routing endpoints:
@app.post("/api/inventory/update-threshold")
def api_update_threshold(payload: ThresholdUpdateRequest):
    success = update_inventory_safety_threshold(
        payload.store_id, payload.sku, payload.new_threshold
    )
    if not success:
        raise HTTPException(status_code=404, detail="Target inventory SKU profile layout not found.")
    return {"status": "success", "message": f"Safety threshold updated to {payload.new_threshold}."}

@app.post("/api/purchase-orders/promote")
def api_promote_order(payload: PromotionRequest):
    success = promote_draft_purchase_order( payload.po_number, payload.user_name)
    if not success:
        raise HTTPException(status_code=404, detail="Target Purchase Order identifier string not found.")
    return {"status": "success", "message": f"Order {payload.po_number} promoted successfully."}
