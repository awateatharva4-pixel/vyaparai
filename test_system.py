import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


sys.path.append(os.path.dirname(__file__))

from app.core.config import settings
from app.core.database import Base, engine, SessionLocal, init_db
from app.models.product import Product
from app.models.transaction import Transaction
from app.services.inventory_service import InventoryService, STATE_FILE_PATH

def run_tests():
    print("=== TEST 1: Initialize Database & Tables ===")
    init_db()
    db = SessionLocal()

    print("=== TEST 2: Seed Initial Catalog ===")
    InventoryService.seed_initial_catalog(db, force=True)
    m1 = InventoryService.get_dashboard_metrics(db)
    print(f"Total SKUs: {m1['total_skus']}, Total Valuation: Rs {m1['total_valuation']}")
    assert m1['total_skus'] == 10, "Expected 10 SKUs"

    print("=== TEST 3: Process Sale ('5 साखर विकली') ===")
    res1 = InventoryService.process_transaction_event("DEMO_KIRANA_KOP", "5 साखर विकली", db)
    print("Sale Result:", res1["intent"], "| Updates:", res1["updates"])
    sugar = db.query(Product).filter_by(sku="GROC-SUG-001").first()
    print(f"Sugar Stock after sale: {sugar.stock} kg (Expected: 45.0 kg)")
    assert sugar.stock == 45.0, "Expected 45.0 kg sugar"

    print("=== TEST 4: Process Undo / Rollback ('चूक झाली') ===")
    res2 = InventoryService.process_transaction_event("DEMO_KIRANA_KOP", "चूक झाली", db)
    print("Undo Result:", res2["reply_message"].split("\n")[0])
    sugar = db.query(Product).filter_by(sku="GROC-SUG-001").first()
    print(f"Sugar Stock after undo: {sugar.stock} kg (Expected: 50.0 kg)")
    assert sugar.stock == 50.0, "Expected 50.0 kg restored"

    print("=== TEST 5: Homophone Parsing ('दोन पाव साखर') ===")
    res3 = InventoryService.process_transaction_event("DEMO_KIRANA_KOP", "दोन पाव साखर विकली", db)
    sugar = db.query(Product).filter_by(sku="GROC-SUG-001").first()
    print(f"Sugar Stock after 2 pav sale: {sugar.stock} kg (Expected: 49.5 kg)")
    assert sugar.stock == 49.5, "Expected 49.5 kg (2 * 0.250kg deducted)"

    print("=== TEST 6: Zero-Delta Invariant (Out of Stock Item) ===")
    salt = db.query(Product).filter_by(sku="GROC-SALT-1K").first()
    salt.stock = 0.0
    db.commit()
    tx_count_before = db.query(Transaction).count()
    res6 = InventoryService.process_transaction_event("DEMO_KIRANA_KOP", "१ टाटा मीठ विकले", db)
    tx_count_after = db.query(Transaction).count()
    salt_after = db.query(Product).filter_by(sku="GROC-SALT-1K").first()
    print(f"Salt stock: {salt_after.stock}, Tx count before: {tx_count_before}, after: {tx_count_after}")
    assert tx_count_after == tx_count_before, "Invariant violated: Zero-delta transaction row was created!"
    assert salt_after.stock == 0.0, "Invariant violated: Stock went below zero!"
    assert "कोणतीही नोंद झाली नाही" in res6["reply_message"] or "अपुरा साठा" in res6["reply_message"], "Expected alert message"

    print("=== TEST 7: Batch ID Rollback Isolation ===")
    res_b1 = InventoryService.process_transaction_event("DEMO_KIRANA_KOP", "१ साखर विकली", db)
    tx_b1 = db.query(Transaction).filter_by(vendor_id="DEMO_KIRANA_KOP", transaction_type="SALE", is_reversed=False)\
              .order_by(Transaction.id.desc()).first()
    batch_1_id = tx_b1.batch_id
    assert batch_1_id is not None, "Transaction missing batch_id"

    res_b2 = InventoryService.process_transaction_event("DEMO_KIRANA_KOP", "१ साखर विकली", db)
    tx_b2 = db.query(Transaction).filter_by(vendor_id="DEMO_KIRANA_KOP", transaction_type="SALE", is_reversed=False)\
              .order_by(Transaction.id.desc()).first()
    batch_2_id = tx_b2.batch_id
    assert batch_2_id != batch_1_id, "Different transaction events must have unique batch_ids"

    # Rollback latest transaction
    res_undo = InventoryService.process_transaction_event("DEMO_KIRANA_KOP", "चूक झाली", db)
    tx_b1_check = db.query(Transaction).filter_by(id=tx_b1.id).first()
    tx_b2_check = db.query(Transaction).filter_by(id=tx_b2.id).first()
    print(f"Batch 1 (ID #{tx_b1.id}) reversed: {tx_b1_check.is_reversed} (Expected: False)")
    print(f"Batch 2 (ID #{tx_b2.id}) reversed: {tx_b2_check.is_reversed} (Expected: True)")
    assert tx_b1_check.is_reversed is False, "Invariant violated: Older batch was accidentally rolled back!"
    assert tx_b2_check.is_reversed is True, "Latest batch was not reversed!"

    print("=== TEST 8: State Snapshot & Auto-Restore ===")
    assert os.path.exists(STATE_FILE_PATH), "vyaparai_state.json was not created"
    prod_count_expected = db.query(Product).count()
    tx_count_expected = db.query(Transaction).count()

    # Simulate Render container reboot wiping SQLite
    db.query(Transaction).delete()
    db.query(Product).delete()
    db.commit()
    assert db.query(Product).count() == 0, "Database should be empty"

    # Auto-restore on startup from snapshot
    InventoryService.seed_initial_catalog(db, force=False)
    prod_count_restored = db.query(Product).count()
    tx_count_restored = db.query(Transaction).count()
    print(f"Products Restored: {prod_count_restored}/{prod_count_expected}, Transactions Restored: {tx_count_restored}/{tx_count_expected}")
    assert prod_count_restored == prod_count_expected, "Failed to restore products from snapshot"
    assert tx_count_restored == tx_count_expected, "Failed to restore transactions from snapshot"

    print("=== TEST 9: Today's Sales Filter Invariant (IST UTC+5:30) ===")
    from datetime import datetime, timedelta
    old_tx = Transaction(
        batch_id="batch_old_test",
        vendor_id="DEMO_KIRANA_KOP",
        product_id=1,
        sku="GROC-SUG-001",
        item_name="साखर (Sugar)",
        transaction_type="SALE",
        quantity_delta=-10.0,
        stock_after=40.0,
        unit_price=42.0,
        total_amount=420.0,
        raw_message="Old Sale from 2 days ago",
        is_reversed=False,
        created_at=datetime.utcnow() - timedelta(days=2)
    )
    db.add(old_tx)
    db.commit()

    m_now = InventoryService.get_dashboard_metrics(db)
    all_sales = db.query(Transaction).filter_by(vendor_id="DEMO_KIRANA_KOP", transaction_type="SALE", is_reversed=False).all()
    all_sales_revenue = sum(t.total_amount for t in all_sales)
    print(f"All-time Sales Revenue: Rs {all_sales_revenue}, Today's Filtered Revenue: Rs {m_now['today_revenue']}")
    assert m_now['today_revenue'] < all_sales_revenue, "Today's sales filter failed to exclude historical transactions!"

    print("\n>>> ALL 9 INVARIANT & STATE RESILIENCE TESTS PASSED 100% PERFECTLY! <<<")
    db.close()

if __name__ == "__main__":
    run_tests()
