# src/database.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import os

"""
Database setup using SQLAlchemy.
Defines the 3 core tables: inventory, sales_history, purchase_orders.
"""
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, 
    DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import os

# Path to SQLite database file
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "mock_erp.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, nullable=False)
    sku = Column(String(50), nullable=False)
    product_name = Column(String(200), nullable=False)
    current_stock = Column(Integer, nullable=False, default=0)
    reorder_point = Column(Integer, nullable=False, default=20)
    location = Column(String(100), default="Main Shelf")
    
    __table_args__ = (
        UniqueConstraint('store_id', 'sku', name='_store_sku_uc'),
    )


class SalesHistory(Base):
    __tablename__ = "sales_history"
    
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, nullable=False)
    sku = Column(String(50), nullable=False)
    sale_date = Column(DateTime, default=datetime.utcnow)
    units_sold = Column(Integer, nullable=False)


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    
    id = Column(Integer, primary_key=True)
    po_number = Column(String(50), unique=True, nullable=False)
    store_id = Column(Integer, nullable=False)
    sku = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String(20), default="DRAFT")  # DRAFT, APPROVED, REJECTED
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_by = Column(String(100), default="AI Agent")


class PODecision(Base):
    __tablename__ = "po_decisions"
    
    id = Column(Integer, primary_key=True)
    thread_id = Column(String(100), nullable=False)
    po_number = Column(String(50))
    
    # Basic PO info
    sku = Column(String(50))
    store_id = Column(Integer)
    quantity = Column(Integer)
    
    # Decision
    decision = Column(String(20), nullable=False)
    decided_at = Column(DateTime)
    decided_by = Column(String(100))
    rejection_reason = Column(Text)
    
    # AI Reasoning
    investigator_context = Column(Text)
    optimizer_calculation = Column(Text)  # JSON string
    explainer_proposal = Column(Text)
    confidence_score = Column(Float)
    
    # Full snapshot
    full_state_snapshot = Column(Text)  # JSON string
    
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    """Create all tables."""
    Base.metadata.create_all(engine)
    print(f"✅ Database initialized at: {DB_PATH}")


def get_session():
    """Get a new database session."""
    return SessionLocal()


if __name__ == "__main__":
    init_db()