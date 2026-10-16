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
from app.core.database import Base, engine, SessionLocal
from app.models.product import Product
from app.models.transaction import Transaction
from app.services.inventory_service import InventoryService

def run_tests():
    print("=== TEST 1: Initialize Database & Tables ===")
    Base.metadata.create_all(bind=engine)
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

    print("\n>>> ALL 5 INVARIANT TESTS PASSED 100% PERFECTLY! <<<")
    db.close()

if __name__ == "__main__":
    run_tests()
