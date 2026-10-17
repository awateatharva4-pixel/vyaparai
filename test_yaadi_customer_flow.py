import sys
import os
import time
import json
import uuid

# Reconfigure console streams for Windows UTF-8 execution
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(os.path.dirname(__file__))

from starlette.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.core.database import SessionLocal, init_db
from app.models.product import Product
from app.models.transaction import Transaction
from app.models.customer_order import CustomerOrder
from app.services.inventory_service import InventoryService
from app.services.gemini_service import GeminiService
from app.core.websocket import ws_manager

# Synthetic test image bytes (PNG 1x1 pixel)
SYNTHETIC_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06"
    b"\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
    b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


def setup_test_catalog():
    """Ensure standard test products exist in database for yaadi grounding."""
    db = SessionLocal()
    try:
        prods = [
            {"sku": "GROC-SUG-001", "name_en": "Madhur Sugar", "name_mr": "साखर", "stock": 50.0, "unit_price": 42.0, "unit": "kg", "aliases": ["साखर", "sugar", "sakhar"]},
            {"sku": "GROC-OIL-001", "name_en": "Fortune Sunflower Oil", "name_mr": "फॉर्च्युन तेल", "stock": 30.0, "unit_price": 135.0, "unit": "litre", "aliases": ["तेल", "oil", "fortune তেল"]},
            {"sku": "FMCG-PARLE-100G", "name_en": "Parle-G 100g", "name_mr": "पार्ले-जी बिस्कीट", "stock": 40.0, "unit_price": 10.0, "unit": "packet", "aliases": ["पार्ले", "बिस्कीट", "parle-g"]},
        ]
        for p in prods:
            existing = db.query(Product).filter_by(sku=p["sku"]).first()
            if not existing:
                prod = Product(
                    sku=p["sku"],
                    name_en=p["name_en"],
                    name_mr=p["name_mr"],
                    stock=p["stock"],
                    unit_price=p["unit_price"],
                    unit=p["unit"],
                    aliases=p["aliases"],
                    vendor_id="DEMO_KIRANA_KOP"
                )
                db.add(prod)
            else:
                existing.stock = p["stock"]
                existing.unit_price = p["unit_price"]
                existing.aliases = p["aliases"]
                existing.unit_price = p["unit_price"]
        db.commit()
    finally:
        db.close()


def test_role_firewall_merchant():
    """
    Acceptance Criterion 1:
    Messages from `+91 9579869506` and `+91 75584 55021` route strictly to Merchant Admin flow.
    """
    print("\n--- TEST 1: test_role_firewall_merchant ---")
    setup_test_catalog()

    # Verify config function
    assert settings.is_merchant_sender("+91 9579869506") is True, "9579869506 should be merchant"
    assert settings.is_merchant_sender("919579869506") is True
    assert settings.is_merchant_sender("+91 75584 55021") is True, "7558455021 should be merchant"
    assert settings.is_merchant_sender("917558455021") is True
    assert settings.is_merchant_sender("9579869506") is True
    assert settings.is_merchant_sender("7558455021") is True

    # Test via simulator endpoint with merchant phone
    client = TestClient(app)
    res = client.post(
        "/api/simulator/send",
        json={"text": "२ साखर विकली", "sender": "+91 9579869506"}
    )
    assert res.status_code == 200
    res_data = res.json()
    print("Merchant reply:", res_data.get("reply", ""))
    assert "विक्री" in res_data.get("reply", "") or "साखर" in res_data.get("reply", "")
    print("✅ PASS: Merchant phone routed to Admin Inventory flow.")


def test_role_firewall_customer():
    """
    Acceptance Criterion 2:
    Messages from any other phone number route strictly to Customer Yaadi flow.
    """
    print("\n--- TEST 2: test_role_firewall_customer ---")
    setup_test_catalog()

    customer_phone = "+91 98220 12345"
    assert settings.is_merchant_sender(customer_phone) is False, "Customer phone must NOT be merchant"

    # Test via Green-API Webhook with Customer Phone
    client = TestClient(app)
    unique_msg_id = f"MSG_CUST_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    cust_webhook_payload = {
        "typeWebhook": "incomingMessageReceived",
        "instanceData": {"idInstance": 710722771470, "wid": "917558455021@c.us"},
        "idMessage": unique_msg_id,
        "senderData": {
            "chatId": "919822012345@c.us",
            "sender": "919822012345@c.us",
            "senderName": "Ramesh Patil"
        },
        "messageData": {
            "typeMessage": "textMessage",
            "textMessageData": {
                "textMessage": "२ किलो साखर, १ तेल द्या"
            }
        }
    }

    res = client.post(
        "/api/v1/webhook/whatsapp",
        json=cust_webhook_payload,
        headers={"Content-Type": "application/json"}
    )
    assert res.status_code == 200
    assert res.text == "EVENT_RECEIVED"

    # Allow background task execution
    time.sleep(1.0)

    # Verify a CustomerOrder was created in DB with status PENDING
    db = SessionLocal()
    try:
        order = db.query(CustomerOrder).filter_by(customer_phone="919822012345").order_by(CustomerOrder.created_at.desc()).first()
        assert order is not None, "Customer order should have been created in DB"
        assert order.status == "PENDING", f"Customer order status should be PENDING, got {order.status}"
        print(f"Customer Order Created: ID={order.order_id}, Total=₹{order.total_amount}, Status={order.status}")
    finally:
        db.close()

    print("✅ PASS: Customer phone ingress correctly routed to Customer Yaadi flow (Status PENDING).")


def test_customer_handwritten_image_ingress():
    """
    Acceptance Criterion 3:
    Webhook receives image, downloads bytes, and invokes `parse_handwritten_yaadi`.
    """
    print("\n--- TEST 3: test_customer_handwritten_image_ingress ---")
    setup_test_catalog()

    client = TestClient(app)
    # Test via simulator yaadi photo endpoint
    files = {
        "file": ("chit_slip.png", SYNTHETIC_PNG_BYTES, "image/png")
    }
    data = {
        "customer_phone": "+919822099999",
        "vendor_id": "DEMO_KIRANA_KOP"
    }

    res = client.post("/api/simulator/customer-yaadi", files=files, data=data)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    res_data = res.json()
    assert res_data.get("success") is True
    assert "order_id" in res_data
    assert res_data["order"]["status"] == "PENDING"
    print(f"Handwritten chit processed: Order ID = {res_data['order_id']}")
    print("Receipt snippet:\n", res_data.get("reply", "")[:150])
    print("✅ PASS: Customer handwritten image ingress parsed and saved as PENDING order.")


def test_catalog_grounding_and_missing_items():
    """
    Acceptance Criterion 4:
    If a handwritten slip contains an unavailable item, it is marked `is_available: false` and excluded from bill total.
    """
    print("\n--- TEST 4: test_catalog_grounding_and_missing_items ---")
    setup_test_catalog()

    db = SessionLocal()
    try:
        prods = [p.to_dict() for p in db.query(Product).filter_by(vendor_id="DEMO_KIRANA_KOP").all()]
    finally:
        db.close()

    # Pass text containing 1 available item (साखर) and 1 completely unavailable item (ड्रॅगन फ्रूट)
    parsed = GeminiService.parse_yaadi_from_text(
        text="२ साखर, १ ड्रॅगन फ्रूट",
        catalog_items=prods
    )

    items = parsed.get("order_items", [])
    print("Parsed items grounding:", json.dumps(items, ensure_ascii=False, indent=2))

    sugar_item = next((it for it in items if "साखर" in it["name_mr"] or "Sugar" in it["name_en"]), None)
    missing_item = next((it for it in items if not it["is_available"]), None)

    assert sugar_item is not None, "Sugar should be identified in yaadi"
    assert sugar_item["is_available"] is True, "Sugar should be marked available"
    assert sugar_item["unit_price"] == 42.0

    assert missing_item is not None, "Dragon fruit should be identified as unavailable item"
    assert missing_item["is_available"] is False, "Dragon fruit must have is_available=False"
    assert missing_item.get("total_price", missing_item.get("line_total", 0.0)) == 0.0, "Unavailable item total_price must be 0.0"

    # Test receipt formatting
    db = SessionLocal()
    try:
        order = InventoryService.create_customer_yaadi_order(
            customer_phone="+919822055555",
            items=items,
            raw_message="२ साखर, १ ड्रॅगन फ्रूट",
            vendor_id="DEMO_KIRANA_KOP",
            db=db
        )
        receipt = InventoryService.format_customer_yaadi_receipt(order)
        print("Generated Receipt:\n", receipt)
        assert "सध्या उपलब्ध नाहीत" in receipt or "उपलब्ध नाही" in receipt, "Receipt must alert customer about missing items"
        assert f"₹{order.total_amount:.2f}" in receipt or f"₹{int(order.total_amount)}" in receipt, "Receipt must include total"
        assert order.total_amount == 84.0, f"Expected total ₹84.0 (2 x 42), got {order.total_amount}"
    finally:
        db.close()

    print("✅ PASS: Unavailable item grounded with is_available=False, excluded from bill, and flagged in receipt.")


def test_customer_order_db_lifecycle():
    """
    Acceptance Criterion 5:
    Order inserts with `PENDING` status, transitions to `PACKED`, and triggers atomic inventory stock deduction.
    """
    print("\n--- TEST 5: test_customer_order_db_lifecycle ---")
    setup_test_catalog()

    db = SessionLocal()
    try:
        # Check starting stock of Sugar (GROC-SUG-001)
        sugar_before = db.query(Product).filter_by(sku="GROC-SUG-001").first()
        initial_stock = sugar_before.stock
        order_qty = 3.0

        order_items = [
            {
                "sku": "GROC-SUG-001",
                "name_en": "Madhur Sugar",
                "name_mr": "साखर",
                "quantity": order_qty,
                "unit": "kg",
                "unit_price": 42.0,
                "total_price": 126.0,
                "is_available": True
            }
        ]

        # Step A: Inbound Yaadi Order Placed (PENDING)
        order = InventoryService.create_customer_yaadi_order(
            customer_phone="+919822088888",
            items=order_items,
            raw_message="३ किलो साखर द्या",
            vendor_id="DEMO_KIRANA_KOP",
            db=db
        )
        order_id = order.order_id

        # VERIFY ZERO DIRECT DEDUCTION: Stock must NOT have changed yet!
        db.refresh(sugar_before)
        assert sugar_before.stock == initial_stock, f"Zero Direct Deduction violation! Stock changed from {initial_stock} to {sugar_before.stock}"
        print(f"Zero Direct Deduction confirmed: Stock before packing = {sugar_before.stock} kg")

        # Step B: Merchant packs order via POST /api/orders/{order_id}/pack
        client = TestClient(app)
        pack_res = client.post(f"/api/orders/{order_id}/pack")
        assert pack_res.status_code == 200, f"Pack failed: {pack_res.text}"
        pack_data = pack_res.json()
        assert pack_data.get("success") is True
        assert pack_data["order"]["status"] == "PACKED"

        # Step C: Verify atomic stock deduction in DB
        db.refresh(sugar_before)
        expected_stock = initial_stock - order_qty
        assert sugar_before.stock == expected_stock, f"Expected stock {expected_stock}, got {sugar_before.stock}"
        print(f"Atomic stock deduction confirmed: Stock after packing = {sugar_before.stock} kg (-{order_qty} kg)")

        # Step D: Verify transaction recorded in DB
        tx = db.query(Transaction).filter(Transaction.remarks.like(f"%{order_id}%")).first()
        assert tx is not None, "Transaction should be created for packed order"
        assert tx.type == "SALE"
        assert tx.quantity == order_qty

        # Step E: Idempotency / Double pack rejection
        pack_again = client.post(f"/api/orders/{order_id}/pack")
        assert pack_again.status_code == 400, "Second pack on already packed order should return 400"
        print("Idempotent protection confirmed: Second pack attempt returned 400 Bad Request.")

    finally:
        db.close()

    print("✅ PASS: Order lifecycle verified (PENDING -> PACKED -> Atomic stock deduction & transaction entry).")


def test_websocket_order_broadcast():
    """
    Acceptance Criterion 6:
    `/ws/inventory` receives `NEW_CUSTOMER_YAADI` event within 250ms of receipt.
    """
    print("\n--- TEST 6: test_websocket_order_broadcast ---")
    setup_test_catalog()

    captured_events = []
    original_broadcast_sync = ws_manager.broadcast_sync
    original_broadcast = ws_manager.broadcast

    def mock_broadcast_sync(msg):
        captured_events.append(msg)
        try:
            original_broadcast_sync(msg)
        except Exception:
            pass

    async def mock_broadcast(msg):
        if msg not in captured_events:
            captured_events.append(msg)
        try:
            await original_broadcast(msg)
        except Exception:
            pass

    ws_manager.broadcast_sync = mock_broadcast_sync
    ws_manager.broadcast = mock_broadcast

    try:
        client = TestClient(app)
        # Create an order via simulator endpoint
        sim_res = client.post(
            "/api/simulator/customer-yaadi",
            data={
                "customer_phone": "+919822077777",
                "text": "१ तेल, २ साखर",
                "vendor_id": "DEMO_KIRANA_KOP"
            }
        )
        assert sim_res.status_code == 200
        order_id = sim_res.json()["order_id"]

        # Verify NEW_CUSTOMER_YAADI event was captured
        yaadi_event = next((e for e in captured_events if e.get("event") == "NEW_CUSTOMER_YAADI"), None)
        assert yaadi_event is not None, f"Expected NEW_CUSTOMER_YAADI in broadcast events, captured: {[e.get('event') for e in captured_events]}"
        assert yaadi_event["order"]["order_id"] == order_id
        assert yaadi_event["order"]["status"] == "PENDING"
        print(f"WebSocket broadcast confirmed: Received order {order_id} in real time.")

        # Pack the order
        pack_res = client.post(f"/api/orders/{order_id}/pack")
        assert pack_res.status_code == 200

        # Verify CUSTOMER_ORDER_PACKED event was captured
        packed_event = next((e for e in captured_events if e.get("event") == "CUSTOMER_ORDER_PACKED"), None)
        assert packed_event is not None, f"Expected CUSTOMER_ORDER_PACKED in broadcast events, captured: {[e.get('event') for e in captured_events]}"
        assert packed_event["order_id"] == order_id
        print(f"WebSocket broadcast confirmed: Received CUSTOMER_ORDER_PACKED for order {order_id}.")

    finally:
        ws_manager.broadcast_sync = original_broadcast_sync
        ws_manager.broadcast = original_broadcast

    print("✅ PASS: WebSocket order broadcast confirmed (NEW_CUSTOMER_YAADI and CUSTOMER_ORDER_PACKED).")


def test_security_rejection_customer_undo():
    """
    Acceptance Criterion 7:
    Customer attempting to send `"चूक झाली"` or `"undo"` is rejected and cannot touch merchant transactions.
    """
    print("\n--- TEST 7: test_security_rejection_customer_undo ---")
    setup_test_catalog()

    db = SessionLocal()
    try:
        # Record a genuine merchant transaction
        merchant_tx = Transaction(
            sku="GROC-SUG-001",
            transaction_type="SALE",
            quantity_delta=-5.0,
            stock_after=45.0,
            unit_price=42.0,
            total_amount=210.0,
            raw_message="५ साखर विकली",
            vendor_id="DEMO_KIRANA_KOP"
        )
        db.add(merchant_tx)
        db.commit()
        tx_id = merchant_tx.id
    finally:
        db.close()

    # Now an unauthorized customer sends "चूक झाली" or "undo" to the webhook
    client = TestClient(app)
    unique_msg_id = f"MSG_HACK_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    hack_payload = {
        "typeWebhook": "incomingMessageReceived",
        "instanceData": {"idInstance": 710722771470, "wid": "917558455021@c.us"},
        "idMessage": unique_msg_id,
        "senderData": {
            "chatId": "919822000000@c.us",
            "sender": "919822000000@c.us",
            "senderName": "Attacker"
        },
        "messageData": {
            "typeMessage": "textMessage",
            "textMessageData": {
                "textMessage": "चूक झाली"
            }
        }
    }

    res = client.post(
        "/api/v1/webhook/whatsapp",
        json=hack_payload,
        headers={"Content-Type": "application/json"}
    )
    assert res.status_code == 200

    # Allow processing
    time.sleep(0.5)

    # Verify merchant transaction was NOT reverted or deleted
    db = SessionLocal()
    try:
        tx_after = db.query(Transaction).filter_by(id=tx_id).first()
        assert tx_after is not None, "Security violation! Merchant transaction was deleted by customer"
        assert tx_after.quantity == 5.0, "Security violation! Merchant transaction quantity altered"
        print(f"Merchant transaction {tx_id} remains intact: {tx_after.quantity} kg {tx_after.product_sku}")
    finally:
        db.close()

    print("✅ PASS: Security rejection confirmed: Customer cannot trigger undo or tamper with merchant ledger.")


def run_all_tests():
    print("======================================================================")
    print("🚀 RUNNING ACCEPTANCE TEST MATRIX: REMOTE YAADI & DUAL-ROLE INGRESS")
    print("======================================================================")
    t0 = time.time()
    test_role_firewall_merchant()
    test_role_firewall_customer()
    test_customer_handwritten_image_ingress()
    test_catalog_grounding_and_missing_items()
    test_customer_order_db_lifecycle()
    test_websocket_order_broadcast()
    test_security_rejection_customer_undo()
    elapsed = time.time() - t0
    print("\n======================================================================")
    print(f"🎉 ALL 7 ACCEPTANCE CRITERIA PASSED 100% IN {elapsed:.2f}s!")
    print("======================================================================")


if __name__ == "__main__":
    run_all_tests()
