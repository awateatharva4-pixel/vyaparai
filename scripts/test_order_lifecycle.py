import sys
import os
import json

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from starlette.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.customer_order import CustomerOrder
from app.models.product import Product
from app.models.transaction import Transaction
from app.services.inventory_service import InventoryService
from scripts.clean_and_seed_orders import clean_and_seed_orders


def run_tests():
    print("==================================================")
    print("🧪 RUNNING ORDER QUEUE & FULFILLMENT AUDIT TESTS")
    print("==================================================")

    # 1. Clean and seed clean Venkatesh Pai order
    print("\n--- Phase 1: Clean and Seed Clean Order ---")
    clean_and_seed_orders()

    client = TestClient(app)

    # 2. Test GET /api/orders/pending
    print("\n--- Phase 2: GET /api/orders/pending ---")
    res = client.get("/api/orders/pending")
    assert res.status_code == 200, f"Failed GET /api/orders/pending: {res.text}"
    data = res.json()
    orders = data.get("orders", [])
    print(f"Pending orders returned: {len(orders)}")
    assert len(orders) >= 1, "Expected at least 1 order in queue"
    order = orders[0]
    print(f"Order ID: {order['order_id']}")
    print(f"Customer Name: {order['customer_name']}")
    print(f"Customer Phone: {order['customer_phone']}")
    print(f"Status: {order['status']}")
    print(f"Total Amount: ₹{order['total_amount']}")
    print(f"Items: {len(order['items'])} items")

    assert order["order_id"] == "ORD-KOP-7019"
    assert "व्यंकटेश पै" in order["customer_name"]
    assert order["status"] == "PENDING"
    assert order["total_amount"] == 296.0

    # 3. Test POST /api/orders/{order_id}/pack
    print("\n--- Phase 3: POST /api/orders/ORD-KOP-7019/pack ---")
    db = SessionLocal()
    try:
        sugar = db.query(Product).filter_by(sku="GROC-SUG-001").first()
        sugar_stock_before = sugar.stock if sugar else 0.0
        print(f"Sugar stock before packing: {sugar_stock_before} kg")
    finally:
        db.close()

    pack_res = client.post("/api/orders/ORD-KOP-7019/pack")
    assert pack_res.status_code == 200, f"Pack failed: {pack_res.text}"
    pack_data = pack_res.json()
    print("Pack response status:", pack_data.get("status"))
    print("Pack response success:", pack_data.get("success"))
    assert pack_data.get("success") is True or pack_data.get("status") == "PACKED"

    db = SessionLocal()
    try:
        order_db = db.query(CustomerOrder).filter_by(order_id="ORD-KOP-7019").first()
        assert order_db is not None
        assert order_db.status == "PACKED"
        print(f"Database order status after packing: {order_db.status}")

        sugar = db.query(Product).filter_by(sku="GROC-SUG-001").first()
        sugar_stock_after = sugar.stock if sugar else 0.0
        print(f"Sugar stock after packing: {sugar_stock_after} kg (decremented by 2.0 kg)")
        assert sugar_stock_after == sugar_stock_before - 2.0

        # Verify sale transaction
        tx = db.query(Transaction).filter(Transaction.raw_message.like("%ORD-KOP-7019%")).first()
        assert tx is not None, "Transaction should be created for packed order"
        assert tx.transaction_type == "SALE"
        print(f"Transaction verified: ID={tx.id}, Type={tx.transaction_type}, SKU={tx.sku}")
    finally:
        db.close()

    # 4. Test Undo / Expiration Rollback
    print("\n--- Phase 4: Auto-Undo / Expiration Rollback ---")
    # Reseed order for undo testing
    clean_and_seed_orders()

    undo_res = client.post("/api/orders/ORD-KOP-7019/expire-now")
    assert undo_res.status_code == 200, f"Expire failed: {undo_res.text}"
    undo_data = undo_res.json()
    print("Undo response:", undo_data.get("status"))

    db = SessionLocal()
    try:
        order_db = db.query(CustomerOrder).filter_by(order_id="ORD-KOP-7019").first()
        assert order_db is not None
        assert order_db.status in ("EXPIRED_AUTO_CANCELLED", "CANCELLED")
        print(f"Database order status after undo: {order_db.status}")
    finally:
        db.close()

    # 5. Final Reset: Restore pristine clean order in PENDING state
    print("\n--- Phase 5: Final Reset to Pristine PENDING State ---")
    clean_and_seed_orders()

    # Verify final state
    with open("E:/vyaparai/data/vyaparai_state.json", "r", encoding="utf-8") as f:
        state = json.load(f)
    final_orders = state.get("customer_orders", [])
    assert len(final_orders) == 1
    assert final_orders[0]["order_id"] == "ORD-KOP-7019"
    assert final_orders[0]["status"] == "PENDING"
    assert final_orders[0]["total_amount"] == 296.0
    print(f"Final state JSON verified: {len(final_orders)} order, ID={final_orders[0]['order_id']}, status={final_orders[0]['status']}")

    print("\n🎉 ALL AUDIT VERIFICATION TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    run_tests()
