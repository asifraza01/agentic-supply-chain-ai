"""
Seed the database with realistic mock supply chain data.
Includes an intentional 'problem scenario' for the agent to detect.
"""
from faker import Faker
from datetime import datetime, timedelta
import random
from src.database import init_db, get_session, Inventory, SalesHistory, PurchaseOrder

fake = Faker()
Faker.seed(42)
random.seed(42)

# Realistic product catalog for a grocery retailer
PRODUCTS = [
    ("SKU-100", "Organic Whole Milk 1L"),
    ("SKU-101", "Free Range Eggs (12 pack)"),
    ("SKU-102", "Sourdough Bread Loaf"),
    ("SKU-103", "Atlantic Salmon Fillet 200g"),
    ("SKU-104", "Avocado (each)"),
    ("SKU-105", "Greek Yogurt 500g"),
    ("SKU-106", "Chicken Breast 500g"),
    ("SKU-107", "Basmati Rice 1kg"),
    ("SKU-108", "Extra Virgin Olive Oil 500ml"),
    ("SKU-109", "Almond Milk Unsweetened 1L"),
]

STORES = list(range(1, 11))  # Stores 1-10


def seed_inventory(session):
    """Create inventory records for every store + product combo."""
    print("📦 Seeding inventory...")
    for store_id in STORES:
        for sku, name in PRODUCTS:
            # Normal stock levels: between 30 and 150 units
            stock = random.randint(30, 150)
            reorder_point = random.randint(15, 30)
            
            inventory = Inventory(
                store_id=store_id,
                sku=sku,
                product_name=name,
                current_stock=stock,
                reorder_point=reorder_point,
                location=f"Aisle {random.randint(1, 12)}"
            )
            session.add(inventory)
    
    # 🚨 THE PROBLEM SCENARIO: Store #42 doesn't exist in our 1-10 range,
    # so let's use Store #4 instead. Make it critically low on Organic Milk.
    problem_item = session.query(Inventory).filter_by(
        store_id=4, sku="SKU-100"
    ).first()
    problem_item.current_stock = 5  # Critically low!
    problem_item.reorder_point = 20
    print("   ⚠️  Created problem scenario: Store 4, SKU-100 (Organic Milk) = 5 units")
    
    session.commit()


def seed_sales_history(session):
    """Create 30 days of sales history for every store + product."""
    print("📊 Seeding sales history (30 days)...")
    today = datetime.utcnow()
    
    for store_id in STORES:
        for sku, name in PRODUCTS:
            # Base daily sales: 5-20 units per day
            base_sales = random.randint(5, 20)
            
            for days_ago in range(30):
                sale_date = today - timedelta(days=days_ago)
                
                # 🚨 PROBLEM SCENARIO: Organic Milk at Store 4 has had 
                # a massive demand spike in the last 3 days
                if store_id == 4 and sku == "SKU-100" and days_ago <= 2:
                    units_sold = base_sales * 4  # 4x normal demand!
                else:
                    # Add some random variance
                    units_sold = max(0, base_sales + random.randint(-3, 5))
                
                sale = SalesHistory(
                    store_id=store_id,
                    sku=sku,
                    sale_date=sale_date,
                    units_sold=units_sold
                )
                session.add(sale)
    
    session.commit()
    print("   ✅ Sales history seeded.")


def main():
    print("🌱 Starting database seeding...\n")
    init_db()
    session = get_session()
    
    # Clear existing data (for re-runs)
    session.query(PurchaseOrder).delete()
    session.query(SalesHistory).delete()
    session.query(Inventory).delete()
    session.commit()
    
    seed_inventory(session)
    seed_sales_history(session)
    
    # Print summary
    inv_count = session.query(Inventory).count()
    sales_count = session.query(SalesHistory).count()
    print(f"\n🎉 Seeding complete!")
    print(f"   • {inv_count} inventory records")
    print(f"   • {sales_count} sales history records")
    print(f"   • Database ready at: data/mock_erp.db")
    
    session.close()


if __name__ == "__main__":
    main()