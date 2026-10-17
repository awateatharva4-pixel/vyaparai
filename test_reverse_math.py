import sys
import os
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(os.path.dirname(__file__))

from app.core.database import SessionLocal, init_db
from app.models.product import Product
from app.models.transaction import Transaction
from app.services.inventory_service import InventoryService
from app.services.loose_commodity_service import LooseCommodityEngine


def run_tests():
    print("=== INITIALIZE DATABASE & SEED CATALOG ===")
    init_db()
    db = SessionLocal()
    InventoryService.seed_initial_catalog(db, force=True)

    vendor_id = "DEMO_KIRANA_KOP"

    # ---------------------------------------------------------
    # Acceptance Test 1: test_money_to_weight_standard
    # "२० रुपयांची साखर" resolves to GROC-SUG-001, 0.476 kg, ₹20.00
    # ---------------------------------------------------------
    print("\n--- TEST 1: test_money_to_weight_standard ---")
    sugar_before = db.query(Product).filter_by(vendor_id=vendor_id, sku="GROC-SUG-001").first()
    assert sugar_before.stock == 50.0, f"Expected 50.0 kg sugar, got {sugar_before.stock}"
    
    res1 = InventoryService.process_transaction_event(vendor_id, "२० रुपयांची साखर", db)
    print("Reply:\n" + res1["reply_message"])
    assert res1["success"] is True
    assert len(res1["updates"]) == 1
    u1 = res1["updates"][0]
    assert u1["sku"] == "GROC-SUG-001"
    assert u1["qty"] == 0.476, f"Expected 0.476 kg, got {u1['qty']}"
    assert u1["remaining"] == 49.524, f"Expected 49.524 kg remaining, got {u1['remaining']}"
    assert res1["total_amount"] == 20.0, f"Expected ₹20.00, got {res1['total_amount']}"
    assert "⚖️ *काट्यावर ठेवा (PLACE ON SCALE):*" in res1["reply_message"]
    assert "476 ग्रॅम" in res1["reply_message"]
    assert "₹20.00" in res1["reply_message"]

    # ---------------------------------------------------------
    # Acceptance Test 2: test_money_to_weight_minglish
    # "20 chi sakhar" resolves to GROC-SUG-001, 0.476 kg, ₹20.00
    # ---------------------------------------------------------
    print("\n--- TEST 2: test_money_to_weight_minglish ---")
    res2 = InventoryService.process_transaction_event(vendor_id, "20 chi sakhar", db)
    print("Reply:\n" + res2["reply_message"])
    assert res2["success"] is True
    assert len(res2["updates"]) == 1
    u2 = res2["updates"][0]
    assert u2["sku"] == "GROC-SUG-001"
    assert u2["qty"] == 0.476
    assert u2["remaining"] == round(49.524 - 0.476, 3)
    assert res2["total_amount"] == 20.0
    assert "476 ग्रॅम" in res2["reply_message"]

    # ---------------------------------------------------------
    # Acceptance Test 3: test_weight_to_money_grams
    # "३५० ग्रॅम कांदा" resolves to VEG-KANDA-001, 0.350 kg, ₹12.25
    # ---------------------------------------------------------
    print("\n--- TEST 3: test_weight_to_money_grams ---")
    onion_before = db.query(Product).filter_by(vendor_id=vendor_id, sku="VEG-KANDA-001").first()
    assert onion_before.stock == 70.0
    
    res3 = InventoryService.process_transaction_event(vendor_id, "३५० ग्रॅम कांदा", db)
    print("Reply:\n" + res3["reply_message"])
    assert res3["success"] is True
    assert len(res3["updates"]) == 1
    u3 = res3["updates"][0]
    assert u3["sku"] == "VEG-KANDA-001"
    assert u3["qty"] == 0.350, f"Expected 0.350 kg, got {u3['qty']}"
    assert u3["remaining"] == 69.650, f"Expected 69.650 kg, got {u3['remaining']}"
    assert res3["total_amount"] == 12.25, f"Expected ₹12.25, got {res3['total_amount']}"
    assert "💰 *किराणा बिल (LOOSE ITEM BILL):*" in res3["reply_message"]
    assert "₹12.25" in res3["reply_message"]
    assert "350 ग्रॅम" in res3["reply_message"]

    # ---------------------------------------------------------
    # Acceptance Test 4: test_fractional_pavsher
    # "पावशेर साखर" resolves to GROC-SUG-001, 0.250 kg, ₹10.50
    # ---------------------------------------------------------
    print("\n--- TEST 4: test_fractional_pavsher ---")
    res4 = InventoryService.process_transaction_event(vendor_id, "पावशेर साखर", db)
    print("Reply:\n" + res4["reply_message"])
    assert res4["success"] is True
    assert len(res4["updates"]) == 1
    u4 = res4["updates"][0]
    assert u4["sku"] == "GROC-SUG-001"
    assert u4["qty"] == 0.250, f"Expected 0.250 kg, got {u4['qty']}"
    assert res4["total_amount"] == 10.50, f"Expected ₹10.50, got {res4['total_amount']}"
    assert "250 ग्रॅम" in res4["reply_message"]

    # ---------------------------------------------------------
    # Acceptance Test 5: test_multi_item_compound
    # "२० रुपयांची साखर आणि २ पार्ले बिस्कीट आणि ३५० ग्रॅम कांदा"
    # ---------------------------------------------------------
    print("\n--- TEST 5: test_multi_item_compound ---")
    res5 = InventoryService.process_transaction_event(
        vendor_id,
        "२० रुपयांची साखर आणि २ पार्ले बिस्कीट आणि ३५० ग्रॅम कांदा",
        db
    )
    print("Reply:\n" + res5["reply_message"])
    assert res5["success"] is True
    assert len(res5["updates"]) == 3, f"Expected 3 items updated, got {len(res5['updates'])}"
    
    # Check item 1: Sugar (0.476 kg, ₹20.00)
    assert res5["updates"][0]["sku"] == "GROC-SUG-001"
    assert res5["updates"][0]["qty"] == 0.476
    assert res5["updates"][0]["line_amount"] == 20.0
    
    # Check item 2: Parle-G (2 packets, ₹20.00)
    assert res5["updates"][1]["sku"] == "FMCG-PARLE-100G"
    assert res5["updates"][1]["qty"] == 2.0
    assert res5["updates"][1]["line_amount"] == 20.0
    
    # Check item 3: Onion (0.350 kg, ₹12.25)
    assert res5["updates"][2]["sku"] == "VEG-KANDA-001"
    assert res5["updates"][2]["qty"] == 0.350
    assert res5["updates"][2]["line_amount"] == 12.25
    
    expected_total = round(20.0 + 20.0 + 12.25, 2)
    assert res5["total_amount"] == expected_total, f"Expected ₹{expected_total}, got {res5['total_amount']}"
    assert "काट्यावर ठेवा" in res5["reply_message"] or "काटा प्रमाण" in res5["reply_message"]

    # Verify atomic rollback of compound multi-item order
    print("\n--- TEST 5b: Atomic Undo of Compound Order ---")
    sugar_mid = db.query(Product).filter_by(vendor_id=vendor_id, sku="GROC-SUG-001").first().stock
    parle_mid = db.query(Product).filter_by(vendor_id=vendor_id, sku="FMCG-PARLE-100G").first().stock
    onion_mid = db.query(Product).filter_by(vendor_id=vendor_id, sku="VEG-KANDA-001").first().stock

    res_undo = InventoryService.process_transaction_event(vendor_id, "चूक झाली", db)
    print("Undo Reply:\n" + res_undo["reply_message"])
    assert res_undo["success"] is True

    sugar_post = db.query(Product).filter_by(vendor_id=vendor_id, sku="GROC-SUG-001").first().stock
    parle_post = db.query(Product).filter_by(vendor_id=vendor_id, sku="FMCG-PARLE-100G").first().stock
    onion_post = db.query(Product).filter_by(vendor_id=vendor_id, sku="VEG-KANDA-001").first().stock

    assert round(sugar_post, 3) == round(sugar_mid + 0.476, 3), "Sugar not restored correctly"
    assert round(parle_post, 3) == round(parle_mid + 2.0, 3), "Parle-G not restored correctly"
    assert round(onion_post, 3) == round(onion_mid + 0.350, 3), "Onion not restored correctly"

    # ---------------------------------------------------------
    # Acceptance Test 6: test_zero_division_guard
    # Product with price ₹0 raises clean error without server panic
    # ---------------------------------------------------------
    print("\n--- TEST 6: test_zero_division_guard ---")
    sugar_prod = db.query(Product).filter_by(vendor_id=vendor_id, sku="GROC-SUG-001").first()
    orig_price = sugar_prod.unit_price
    sugar_prod.unit_price = 0.0
    db.commit()

    res6 = InventoryService.process_transaction_event(vendor_id, "२० रुपयांची साखर", db)
    print("Zero division response:", res6)
    assert res6["success"] is False
    assert "विक्री दर निश्चित नाही" in res6["reply_message"]

    # Restore price
    sugar_prod.unit_price = orig_price
    db.commit()

    # ---------------------------------------------------------
    # Acceptance Test 7: test_sub_millisecond_latency
    # Total execution time from raw string to scale card <= 0.5ms
    # ---------------------------------------------------------
    print("\n--- TEST 7: test_sub_millisecond_latency ---")
    catalog_products = db.query(Product).filter_by(vendor_id=vendor_id).all()
    catalog_data = [
        {"sku": p.sku, "name_mr": p.name_mr, "name_en": p.name_en, "unit": p.unit, "unit_price": p.unit_price, "aliases": p.aliases}
        for p in catalog_products
    ]

    # Warmup
    LooseCommodityEngine.detect_and_compute("२० रुपयांची साखर", catalog_data)

    latencies = []
    for _ in range(200):
        t_start = time.perf_counter()
        res = LooseCommodityEngine.detect_and_compute("२० रुपयांची साखर", catalog_data)
        card = LooseCommodityEngine.format_money_to_weight_notice(
            res["product_name_mr"], res["target_grams"], res["money"], res["unit_price"], 49.524
        )
        t_end = time.perf_counter()
        latencies.append(t_end - t_start)

    avg_latency_ms = (sum(latencies) / len(latencies)) * 1000.0
    max_latency_ms = max(latencies) * 1000.0
    min_latency_ms = min(latencies) * 1000.0

    print(f"Latency Results over 200 runs:")
    print(f"  • Average: {avg_latency_ms:.4f} ms")
    print(f"  • Minimum: {min_latency_ms:.4f} ms")
    print(f"  • Maximum: {max_latency_ms:.4f} ms")
    assert avg_latency_ms < 0.5, f"Expected average latency < 0.5ms, got {avg_latency_ms:.4f}ms"

    print("\n" + "="*60)
    print(">>> ALL 7 REVERSE-MATH ACCEPTANCE CRITERIA PASSED 100%! <<<")
    print("="*60)


if __name__ == "__main__":
    run_tests()
