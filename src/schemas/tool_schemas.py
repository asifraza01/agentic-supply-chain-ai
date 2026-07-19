"""
Pydantic schemas for strict type validation of all tool inputs/outputs.
This prevents LLM hallucinations from breaking the database.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============================================================================
# INVENTORY TOOLS
# ============================================================================

class InventoryQuery(BaseModel):
    """Input schema for querying inventory."""
    store_id: int = Field(..., description="The store ID (1-10)")
    sku: str = Field(..., description="The product SKU (e.g., 'SKU-100')")


class InventoryData(BaseModel):
    """Output schema for inventory data."""
    store_id: int
    sku: str
    product_name: str
    current_stock: int
    reorder_point: int
    location: str
    is_below_reorder_point: bool


class SalesVelocityQuery(BaseModel):
    """Input schema for querying sales velocity."""
    store_id: int = Field(..., description="The store ID")
    sku: str = Field(..., description="The product SKU")
    days: int = Field(default=7, description="Number of days to calculate velocity over", ge=1, le=90)


class SalesVelocityData(BaseModel):
    """Output schema for sales velocity."""
    store_id: int
    sku: str
    product_name: str
    days_analyzed: int
    total_units_sold: int
    daily_velocity: float
    trend: str  # "increasing", "decreasing", "stable"


# ============================================================================
# MATH TOOLS
# ============================================================================

class ReorderCalculation(BaseModel):
    """Input schema for calculating reorder quantity."""
    current_stock: int = Field(..., ge=0, description="Current inventory units")
    daily_velocity: float = Field(..., gt=0, description="Average units sold per day")
    lead_time_days: int = Field(default=3, ge=1, le=30, description="Supplier lead time in days")
    safety_stock_days: int = Field(default=5, ge=1, le=30, description="Days of safety stock to maintain")


class ReorderResult(BaseModel):
    """Output schema for reorder calculation."""
    current_stock: int
    daily_velocity: float
    lead_time_days: int
    safety_stock_days: int
    stock_during_lead_time: int
    recommended_order_quantity: int
    reasoning: str


# ============================================================================
# PURCHASE ORDER TOOLS
# ============================================================================

class PurchaseOrderCreate(BaseModel):
    """Input schema for creating a purchase order."""
    store_id: int = Field(..., description="The store ID")
    sku: str = Field(..., description="The product SKU")
    POUIstatus: str = Field(..., description="The status of the purchase order from UI (e.g., 'APPROVED', 'REJECTED')")
    quantity: int = Field(..., gt=0, description="Quantity to order")
    approved_by: str = Field(default="AI Agent", description="Who approved this order")


class PurchaseOrderResult(BaseModel):
    """Output schema for purchase order creation."""
    success: bool
    po_number: Optional[str] = None
    store_id: int
    sku: str
    quantity: int
    status: str
    message: str


# ============================================================================
# AGENT STATE SCHEMAS
# ============================================================================

class AgentDecision(BaseModel):
    """Schema for agent decision/proposal."""
    action_type: str  # "reorder", "investigate", "alert"
    store_id: int
    sku: str
    product_name: str
    proposed_quantity: Optional[int] = None
    reasoning: str
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    requires_approval: bool = True

    ###
    # Dashbaord
    ###
    # --- Database Schema Setup ---
