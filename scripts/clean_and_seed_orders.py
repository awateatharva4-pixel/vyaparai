import sys
import os
import json
from datetime import datetime, timedelta

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, is_sqlite
from app.models.customer_order import CustomerOrder
from app.models.product import Product
from app.services.inventory_service import InventoryService
from sqlalchemy import text


def clean_and_seed_orders():
    print("[1/4] Connecting to Database...")
    db = SessionLocal()
    try:
        # Delete old stale customer orders
        old_count = db.query(CustomerOrder).count()
        print(f"[2/4] Found {old_count} old customer orders in database. Purging...")
        db.query(CustomerOrder).delete()
        db.commit()

        # Reset Postgres sequence for customer_orders if on PostgreSQL
        if not is_sqlite:
            try:
                db.execute(text("SELECT setval(pg_get_serial_sequence('customer_orders', 'id'), 1, false);"))
                db.commit()
                print("  -> PostgreSQL customer_orders sequence reset successfully.")
            except Exception as seq_err:
                db.rollback()
                print(f"  -> Note on sequence reset: {seq_err}")

        # Construct clean order for Venkatesh Pai
        order_items = [
            {
                "sku": "GROC-SUG-001",
                "sku_matched": "GROC-SUG-001",
                "name": "साखर (Madhur Sugar)",
                "name_mr": "साखर",
                "name_en": "Madhur Sugar",
                "qty": 2.0,
                "quantity": 2.0,
                "unit": "kg",
                "price": 42.0,
                "unit_price": 42.0,
                "line_total": 84.0,
                "is_available": True
            },
            {
                "sku": "OIL-FORT-1L",
                "sku_matched": "OIL-FORT-1L",
                "name": "फॉर्च्युन सूर्यफूल तेल (Fortune Oil 1L)",
                "name_mr": "फॉर्च्युन तेल",
                "name_en": "Fortune Sunflower Oil 1L",
                "qty": 1.0,
                "quantity": 1.0,
                "unit": "pouch",
                "price": 135.0,
                "unit_price": 135.0,
                "line_total": 135.0,
                "is_available": True
            },
            {
                "sku": "FMCG-PARLE-100G",
                "sku_matched": "FMCG-PARLE-100G",
                "name": "पार्ले-जी बिस्कीट (Parle-G 100g)",
                "name_mr": "पार्ले-जी",
                "name_en": "Parle-G 100g",
                "qty": 5.0,
                "quantity": 5.0,
                "unit": "packet",
                "price": 10.0,
                "unit_price": 10.0,
                "line_total": 50.0,
                "is_available": True
            },
            {
                "sku": "DAIRY-MILK-500ML",
                "sku_matched": "DAIRY-MILK-500ML",
                "name": "गोकुळ / अमूल ताझा दूध (Fresh Milk 500ml)",
                "name_mr": "गोकुळ दूध",
                "name_en": "Fresh Cow Milk 500ml",
                "qty": 1.0,
                "quantity": 1.0,
                "unit": "pouch",
                "price": 27.0,
                "unit_price": 27.0,
                "line_total": 27.0,
                "is_available": True
            }
        ]

        clean_order = CustomerOrder(
            order_id="ORD-KOP-7019",
            vendor_id="DEMO_KIRANA_KOP",
            customer_phone="+919822012345",
            raw_message="व्हॉट्सॲप किराणा यादी: २ किलो साखर, १ लिटर फॉर्च्युन तेल, ५ पार्ले-जी, १ गोकुळ दूध",
            image_url=None,
            items_json=json.dumps(order_items, ensure_ascii=False),
            total_amount=296.0,
            status="PENDING",
            is_stock_reserved=False,
            confirmed_by_customer=False,
            reminder_sent=False,
            expires_at=datetime.utcnow() + timedelta(minutes=30),
            created_at=datetime.utcnow()
        )

        db.add(clean_order)
        db.commit()
        db.refresh(clean_order)
        print(f"[3/4] Seeded clean Venkatesh Pai order {clean_order.order_id}: Total ₹{clean_order.total_amount}")

        # Update durable state snapshot (data/vyaparai_state.json)
        print("[4/4] Generating durable snapshot in data/vyaparai_state.json...")
        InventoryService.save_state_snapshot(db, vendor_id="DEMO_KIRANA_KOP")
        print("✅ Success! Database and vyaparai_state.json cleaned and synchronized.")

    finally:
        db.close()


if __name__ == "__main__":
    clean_and_seed_orders()
