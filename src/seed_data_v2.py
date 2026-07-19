import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv


# Import your database elements directly from your main file
# from main import Base, Inventory, SalesHistory, PurchaseOrder
from database import get_session, PurchaseOrder, SalesHistory, Inventory,init_db

# return sqlite3.connect(os.getenv("sqllightlink"))

load_dotenv()

#DATABASE_URL = "/home/asifubuntu/Documents/dev/supply-chain-agent/data/mock_erp.db"
#print("dbvalue", DATABASE_URL)
#engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
#SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def append_seed_data(session):
 #   db = SessionLocal()
    print("Connecting to SQLite database to append seed data...")

    # 1. Define Realistic Core Sample Products
    sample_products = [
        {"sku": "SKU-APP-101", "name": "Premium Organic Apples", "location": "Aisle A"},
        {"sku": "SKU-BAN-202", "name": "Cavendish Bananas Bunch", "location": "Aisle A"},
        {"sku": "SKU-MIL-303", "name": "Whole Milk 1L Carton", "location": "Cold Room"},
        {"sku": "SKU-EGG-404", "name": "Free Range Eggs 12pk", "location": "Main Shelf"},
        {"sku": "SKU-BRD-505", "name": "Whole Wheat Sourdough", "location": "Main Shelf"},
        {"sku": "SKU-COF-606", "name": "Dark Roast Coffee Beans", "location": "Aisle B"},
        {"sku": "SKU-WTR-707", "name": "Spring Water 6-Pack", "location": "Aisle C"},
    ]

    # Target store identifiers mapping to your dashboard components
    target_stores = [101, 102, 103]

    # 2. Populate Inventory (Without overwriting existing SKUs)
    print("\nChecking inventory profiles...")
    for prod in sample_products:
        for store_id in target_stores:
            # Look up if this SKU at this specific store node already exists
            exists = session.query(Inventory).filter(
                Inventory.sku == prod["sku"], 
                Inventory.store_id == store_id
            ).first()
            
            if not exists:
                new_item = Inventory(
                    store_id=store_id,
                    sku=prod["sku"],
                    product_name=prod["name"],
                    current_stock=random.randint(5, 120),  # Random initial stock volumes
                    reorder_point=random.randint(15, 30),  # System threshold trigger points
                    location=prod["location"]
                )
                session.add(new_item)
                print(f" -> Appended new stock item: {prod['sku']} to Store #{store_id}")
            else:
                print(f" -> Skipped {prod['sku']} at Store #{store_id} (Already exists)")
    
    db.commit()

    # 3. Populate Sales History (Appends random sales transactions across the past week)
    print("\nGenerating fresh sales log entries...")
    for _ in range(30):  # Creates 30 random historical sales events
        random_product = random.choice(sample_products)
        random_days_ago = random.randint(0, 7)
        sale_date = datetime.utcnow() - timedelta(days=random_days_ago)
        
        new_sale = SalesHistory(
            store_id=random.choice(target_stores),
            sku=random_product["sku"],
            sale_date=sale_date,
            units_sold=random.randint(1, 12)
        )
        session.add(new_sale)
    print(" -> Added 30 new transaction points to sales_history")

    # 4. Populate Purchase Orders (Appends unique Agentic workflow items)
    print("\nReviewing pipeline purchase logs...")
    statuses = ["DRAFT", "APPROVED", "REJECTED"]
    approvers = ["AI Agent", "Warehouse Manager", "AI Agent"]

    for _ in range(15):  # Appends 15 historical purchase logs
        po_id = random.randint(10000, 99999)
        po_num = f"PO-LNGRPH-{po_id}"
        
        # Verify that this unique PO reference isn't already inside the database
        exists = session.query(PurchaseOrder).filter(PurchaseOrder.po_number == po_num).first()
        
        if not exists:
            random_product = random.choice(sample_products)
            new_po = PurchaseOrder(
                po_number=po_num,
                store_id=random.choice(target_stores),
                sku=random_product["sku"],
                quantity=random.randint(50, 200),
                status=random.choice(statuses),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 5)),
                approved_by=random.choice(approvers)
            )
            session.add(new_po)
            
    session.commit()
    print(" -> Database transaction layers updated successfully.")
    session.close()

if __name__ == "__main__":
    print("🌱 Starting database seeding...\n")
    init_db()
    session = get_session()
    
    append_seed_data(session)