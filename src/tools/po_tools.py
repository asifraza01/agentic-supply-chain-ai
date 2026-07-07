"""
Tools for creating and managing purchase orders in the database.
"""
from typing import Dict, Any
from datetime import datetime
import uuid
from src.database import get_session, PurchaseOrder
from src.schemas.tool_schemas import PurchaseOrderCreate, PurchaseOrderResult


def create_purchase_order(
    store_id: int,
    sku: str,
    quantity: int,
    approved_by: str = "AI Agent"
) -> Dict[str, Any]:
    """
    Create a new purchase order in the database.
    """
    print(f"   🔧 [PO TOOL] Creating PO with:")
    print(f"      Store: {store_id}")
    print(f"      SKU: {sku}")
    print(f"      Quantity: {quantity}")
    print(f"      Approved by: {approved_by}")
    
    # Validate input
    try:
        po_input = PurchaseOrderCreate(
            store_id=store_id,
            sku=sku,
            quantity=quantity,
            approved_by=approved_by
        )
        print("   ✓ Input validation passed")
    except Exception as e:
        print(f"   ❌ Input validation failed: {e}")
        return {
            "success": False,
            "store_id": store_id,
            "sku": sku,
            "quantity": quantity,
            "status": "VALIDATION_FAILED",
            "message": f"Input validation failed: {str(e)}"
        }
    
    session = get_session()
    try:
        # Generate unique PO number
        po_number = f"PO-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        print(f"   → Generated PO number: {po_number}")
        
        # Create PO record
        new_po = PurchaseOrder(
            po_number=po_number,
            store_id=po_input.store_id,
            sku=po_input.sku,
            quantity=po_input.quantity,
            status="APPROVED",
            approved_by=po_input.approved_by,
            created_at=datetime.utcnow()
        )
        
        print("   → Adding toschema database session...")
        session.add(new_po)
        
        print("   → Committing to database...")
        session.commit()
        print("   ✓ Database commit successful")
        
        result = PurchaseOrderResult(
            success=True,
            po_number=po_number,
            store_id=po_input.store_id,
            sku=po_input.sku,
            quantity=po_input.quantity,
            status="APPROVED",
            message=f"Purchase order {po_number} created successfully"
        )
        
        return result.model_dump()
    
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        session.rollback()
        result = PurchaseOrderResult(
            success=False,
            store_id=po_input.store_id,
            sku=po_input.sku,
            quantity=po_input.quantity,
            status="FAILED",
            message=f"Failed to create PO: {str(e)}"
        )
        return result.model_dump()
    
    finally:
        session.close()