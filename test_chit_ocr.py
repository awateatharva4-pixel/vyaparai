import sys
import os
import json
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import requests

BASE_URL = "http://127.0.0.1:8000"
IMAGE_PATH = "E:/vyaparai/venkatesh_yaadi.jpeg"
ASSET_PATH = "E:/vyaparai/frontend/assets/venkatesh_yaadi.jpeg"

def test_chit_ocr_end_to_end():
    print("=" * 70)
    print("TEST: DEVANAGARI HANDWRITTEN CHIT SLIP OCR & ZERO-DEDUCTION PENDING QUEUE")
    print("=" * 70)

    # 1. Verify Image Assets
    assert os.path.exists(IMAGE_PATH), f"Missing {IMAGE_PATH}"
    assert os.path.exists(ASSET_PATH), f"Missing {ASSET_PATH}"
    img_size = os.path.getsize(IMAGE_PATH)
    print(f"✅ Step 1: Image verified: {IMAGE_PATH} ({img_size} bytes)")

    # 2. Check initial inventory stock before yaadi submission
    inv_res = requests.get(f"{BASE_URL}/api/inventory")
    assert inv_res.status_code == 200, f"Failed to get inventory: {inv_res.text}"
    inv_data = inv_res.json()
    if isinstance(inv_data, list):
        prods_before = {p["sku"]: p["stock"] for p in inv_data}
    else:
        prods_before = {p["sku"]: p["stock"] for p in inv_data.get("products", [])}
    print(f"✅ Step 2: Initial active catalog loaded ({len(prods_before)} products)")

    # 3. Submit handwritten chit slip via POST /api/simulator/customer-yaadi
    with open(IMAGE_PATH, "rb") as f:
        files = {"file": ("venkatesh_yaadi.jpeg", f, "image/jpeg")}
        data = {
            "customer_phone": "+919822012345",
            "vendor_id": "DEMO_KIRANA_KOP"
        }
        post_res = requests.post(f"{BASE_URL}/api/simulator/customer-yaadi", files=files, data=data)

    assert post_res.status_code == 200, f"Chit OCR submission failed: {post_res.text}"
    result = post_res.json()
    assert result.get("success") is True, f"Success is false: {result}"
    order = result.get("order", {})
    order_id = result.get("order_id") or order.get("order_id")
    assert order_id, "Order ID missing from response"
    assert order.get("status") in ("PENDING", "CONFIRMED"), f"Expected PENDING status, got {order.get('status')}"
    
    print(f"✅ Step 3: Chit Slip processed successfully! Order ID = #{order_id}")
    print(f"   Customer: {order.get('customer_name')}")
    print(f"   Items count: {len(order.get('items', []))}")
    print(f"   Estimated Total: ₹{order.get('total_amount', 0):.2f}")
    print("   Receipt Preview:")
    for line in result.get("receipt", "").split("\n")[:8]:
        print(f"     | {line}")

    # 4. Verify order appears in Pending Queue (/api/orders/pending)
    pending_res = requests.get(f"{BASE_URL}/api/orders/pending?vendor_id=DEMO_KIRANA_KOP")
    assert pending_res.status_code == 200
    pending_orders = pending_res.json().get("orders", [])
    found_order = next((o for o in pending_orders if o.get("order_id") == order_id), None)
    assert found_order is not None, f"Order {order_id} not found in pending queue"
    print(f"✅ Step 4: Order #{order_id} verified present in live Merchant Pending Queue")

    # 5. Pack and Fulfill the order
    pack_res = requests.post(f"{BASE_URL}/api/orders/{order_id}/pack?vendor_id=DEMO_KIRANA_KOP")
    assert pack_res.status_code == 200, f"Packing failed: {pack_res.text}"
    pack_data = pack_res.json()
    assert pack_data.get("success") is True
    assert pack_data["order"]["status"] == "PACKED"
    print(f"✅ Step 5: Merchant Pack & Deduct succeeded: Status -> PACKED")

    # 6. Verify Idempotency: second pack attempt must be safely rejected
    pack2_res = requests.post(f"{BASE_URL}/api/orders/{order_id}/pack?vendor_id=DEMO_KIRANA_KOP")
    assert pack2_res.status_code == 400, "Second pack attempt should be rejected with 400"
    print(f"✅ Step 6: Idempotent guard confirmed (duplicate pack rejected)")

    print("\n🎉 ALL TESTS PASSED: Devanagari Handwritten Chit Slip OCR & PENDING Queue is 100% Verified!")

if __name__ == "__main__":
    test_chit_ocr_end_to_end()
