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
from app.services.inventory_service import InventoryService, STATE_FILE_PATH
from app.services.gemini_service import GeminiService
from app.core.websocket import ws_manager


# Synthetic 5-second MP4 video bytes for unit testing & pipeline ingress
SYNTHETIC_MP4_BYTES = (
    b"\x00\x00\x00\x20ftypisom\x00\x00\x02\x00isomiso2avc1mp41"
    b"\x00\x00\x00\x08free\x00\x00\x02\x00mdat" + (b"\xaa\xbb\xcc\xdd" * 200)
)


def test_video_ingress_greenapi():
    """
    Acceptance Criterion 1:
    Webhook parses `typeMessage == "videoMessage"`, extracts `downloadUrl`,
    and processes ingress without 500 error.
    """
    print("\n--- TEST 1: test_video_ingress_greenapi ---")
    client = TestClient(app)

    unique_msg_id = f"MSG_GREEN_VID_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    green_video_payload = {
        "typeWebhook": "incomingMessageReceived",
        "instanceData": {"idInstance": 710722771470, "wid": "917558455021@c.us"},
        "idMessage": unique_msg_id,
        "senderData": {
            "chatId": "917558455021@c.us",
            "sender": "917558455021@c.us",
            "senderName": "Atharva Awate"
        },
        "messageData": {
            "typeMessage": "videoMessage",
            "fileMessageData": {
                "downloadUrl": "https://example.com/test_kirana_shelf_video.mp4",
                "caption": "Store sweep onboarding 15s",
                "fileName": "store_sweep.mp4",
                "mimeType": "video/mp4"
            }
        }
    }

    response = client.post(
        "/api/v1/webhook/whatsapp",
        json=green_video_payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"Webhook Status Code: {response.status_code}")
    print(f"Webhook Response: {response.text}")

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    assert response.text == "EVENT_RECEIVED", f"Expected 'EVENT_RECEIVED', got {response.text}"
    print("✅ PASS: Green-API videoMessage webhook accepted with 200 OK (EVENT_RECEIVED).")


def test_simulator_video_upload():
    """
    Acceptance Criterion 2:
    `POST /api/simulator/video` accepts multipart/form-data video bytes and returns status 200
    with ingested products.
    """
    print("\n--- TEST 2: test_simulator_video_upload ---")
    client = TestClient(app)

    files = {
        "file": ("store_sweep.mp4", SYNTHETIC_MP4_BYTES, "video/mp4")
    }
    data = {
        "vendor_id": "DEMO_KIRANA_KOP"
    }

    response = client.post("/api/simulator/video", files=files, data=data)
    print(f"Simulator Upload Status: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    res_json = response.json()
    print(f"Simulator Response Keys: {list(res_json.keys())}")
    assert "reply" in res_json or "formatted_receipt" in res_json or "message" in res_json
    assert res_json.get("count", 0) > 0 or len(res_json.get("products", [])) > 0 or "दुकान" in str(res_json)
    print(f"Ingested Products Count: {res_json.get('count', len(res_json.get('products', [])))}")
    print("✅ PASS: POST /api/simulator/video accepted multipart bytes and returned 200 OK.")


def test_gemini_video_extraction():
    """
    Acceptance Criterion 3:
    Processes 5s MP4 clip and returns structured JSON with all 8 fields:
    (name_en, name_mr, category, stock, unit_price, unit, min_threshold, aliases).
    """
    print("\n--- TEST 3: test_gemini_video_extraction ---")
    products = GeminiService.digitize_catalog_from_video(
        video_bytes=SYNTHETIC_MP4_BYTES,
        mime_type="video/mp4"
    )

    print(f"Total Products Extracted: {len(products)}")
    assert len(products) >= 1, "Expected at least 1 product extracted from video."

    required_fields = [
        "name_en", "name_mr", "category", "stock",
        "unit_price", "unit", "min_threshold", "aliases"
    ]

    for idx, p in enumerate(products, 1):
        print(f"\nProduct #{idx}: {p.get('name_en')} | {p.get('name_mr')}")
        print(f"  • Category: {p.get('category')} | Unit: {p.get('unit')}")
        print(f"  • Stock: {p.get('stock')} | Unit Price: ₹{p.get('unit_price')}")
        print(f"  • Min Threshold: {p.get('min_threshold')} | Aliases: {p.get('aliases')}")

        for field in required_fields:
            assert field in p, f"Product #{idx} missing required field '{field}'"

        assert isinstance(p["name_en"], str) and len(p["name_en"]) > 0, "name_en must be non-empty string"
        assert isinstance(p["name_mr"], str) and len(p["name_mr"]) > 0, "name_mr must be non-empty string"
        assert isinstance(p["category"], str) and len(p["category"]) > 0, "category must be non-empty string"
        assert isinstance(p["stock"], (int, float)) and p["stock"] > 0, "stock must be positive number"
        assert isinstance(p["unit_price"], (int, float)) and p["unit_price"] >= 0, "unit_price must be >= 0"
        assert isinstance(p["unit"], str) and len(p["unit"]) > 0, "unit must be non-empty string"
        assert isinstance(p["min_threshold"], (int, float)) and p["min_threshold"] > 0, "min_threshold must be positive"
        assert isinstance(p["aliases"], list) and len(p["aliases"]) >= 2, "aliases must be a list with at least 2 terms"

    print("\n✅ PASS: All 8 required catalog fields validated across all extracted products.")


def test_db_persistence_and_snapshot():
    """
    Acceptance Criterion 4:
    Ingested products persist in PostgreSQL/SQLite and survive simulated container
    restart via `vyaparai_state.json`.
    """
    print("\n--- TEST 4: test_db_persistence_and_snapshot ---")
    db = SessionLocal()
    vendor_id = "DEMO_KIRANA_KOP"

    try:
        # Ingest catalog via InventoryService
        res = InventoryService.ingest_catalog_from_video(
            video_bytes=SYNTHETIC_MP4_BYTES,
            mime_type="video/mp4",
            vendor_id=vendor_id,
            db=db
        )
        assert res["success"] is True, f"Ingestion failed: {res}"
        onboarded_count = res["count"]
        print(f"Onboarded {onboarded_count} products via InventoryService.")

        # 1. Verify in DB
        vid_products = db.query(Product).filter(
            Product.vendor_id == vendor_id,
            Product.sku.like("AUTO-VID-%")
        ).all()
        print(f"Found {len(vid_products)} AUTO-VID products in database.")
        assert len(vid_products) >= onboarded_count, "Database does not contain expected AUTO-VID products"

        # 2. Verify state snapshot on disk
        assert os.path.exists(STATE_FILE_PATH), f"State file {STATE_FILE_PATH} does not exist"
        with open(STATE_FILE_PATH, "r", encoding="utf-8") as f:
            snapshot_data = json.load(f)

        snapshot_skus = [p["sku"] for p in snapshot_data.get("products", [])]
        for vp in vid_products:
            assert vp.sku in snapshot_skus, f"SKU {vp.sku} missing from vyaparai_state.json snapshot"
        print(f"Verified all {len(vid_products)} products reflected in data/vyaparai_state.json.")

        # 3. Simulate Render container reboot / wipe and auto-restore
        total_before = db.query(Product).count()
        db.query(Transaction).delete()
        db.query(Product).delete()
        db.commit()
        assert db.query(Product).count() == 0, "Database should be empty before reboot restore"

        # Auto-restore on startup from snapshot
        InventoryService.seed_initial_catalog(db, force=False)
        total_after = db.query(Product).count()
        print(f"Product count after simulated reboot restore: {total_after} (Original was: {total_before})")
        assert total_after >= total_before, "Failed to restore onboarded products from state snapshot"

    finally:
        db.close()

    print("✅ PASS: Ingested products persist in database and survive container reboot via state snapshot.")


def test_voice_continuity_loop():
    """
    Acceptance Criterion 5:
    Immediately after video ingestion of a new item (e.g. Reynolds Pen with alias "पेन"),
    send a voice/text order "२ पेन दिले" and verify that the newly ingested item is found
    and stock is decremented!
    """
    print("\n--- TEST 5: test_voice_continuity_loop ---")
    db = SessionLocal()
    vendor_id = "DEMO_KIRANA_KOP"

    try:
        # Guarantee Reynolds Pen is present in catalog with alias 'पेन'
        pen = db.query(Product).filter(
            Product.vendor_id == vendor_id,
            Product.aliases_json.like("%पेन%")
        ).first()

        if not pen:
            # Re-ingest video to ensure pen is present
            InventoryService.ingest_catalog_from_video(
                video_bytes=SYNTHETIC_MP4_BYTES,
                mime_type="video/mp4",
                vendor_id=vendor_id,
                db=db
            )
            pen = db.query(Product).filter(
                Product.vendor_id == vendor_id,
                Product.aliases_json.like("%पेन%")
            ).first()

        assert pen is not None, "Product with alias 'पेन' not found in catalog after video ingestion."
        initial_stock = pen.stock
        pen_sku = pen.sku
        print(f"Found Pen in catalog: SKU={pen_sku}, Name={pen.name_mr}, Stock Before={initial_stock}")

        # Send vernacular Marathi transaction order: "२ पेन दिले"
        order_text = "२ पेन दिले"
        print(f"Executing voice/text sale order: '{order_text}'")
        res = InventoryService.process_transaction_event(
            vendor_id=vendor_id,
            raw_text=order_text,
            db=db
        )

        print("Sale Result Reply:\n" + res["reply_message"])
        assert res["success"] is True, f"Sale processing failed: {res}"
        assert res["intent"] == "SALE", f"Expected intent SALE, got {res['intent']}"

        # Verify stock was decremented
        pen_after = db.query(Product).filter_by(sku=pen_sku).first()
        expected_stock = max(0.0, initial_stock - 2.0)
        print(f"Pen Stock After Sale: {pen_after.stock} (Expected: {expected_stock})")
        assert pen_after.stock == expected_stock, f"Expected {expected_stock}, got {pen_after.stock}"
        assert "पेन" in res["reply_message"] or "Reynolds" in res["reply_message"] or "विक्री नोंदवली" in res["reply_message"]

    finally:
        db.close()

    print("✅ PASS: Voice Continuity Loop successful — newly onboarded item deducted by voice alias 'पेन'.")


def test_websocket_stream_payload():
    """
    Acceptance Criterion 6:
    Verify WebSocket event `CATALOG_ONBOARDED` is emitted when video ingestion completes.
    """
    print("\n--- TEST 6: test_websocket_stream_payload ---")
    client = TestClient(app)

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
        await original_broadcast(msg)

    ws_manager.broadcast_sync = mock_broadcast_sync
    ws_manager.broadcast = mock_broadcast

    try:
        # Trigger video ingestion
        db = SessionLocal()
        try:
            InventoryService.ingest_catalog_from_video(
                video_bytes=SYNTHETIC_MP4_BYTES,
                mime_type="video/mp4",
                vendor_id="DEMO_KIRANA_KOP",
                db=db
            )
        finally:
            db.close()

        print(f"Captured WebSocket Messages: {len(captured_events)}")
        onboard_events = [e for e in captured_events if e.get("event") == "CATALOG_ONBOARDED"]
        assert len(onboard_events) >= 1, f"Expected CATALOG_ONBOARDED event in websocket messages: {captured_events}"

        ev = onboard_events[0]
        print("Captured CATALOG_ONBOARDED Event Payload:")
        print(json.dumps(ev, ensure_ascii=False, indent=2))

        assert ev.get("event") == "CATALOG_ONBOARDED"
        assert ev.get("count", 0) > 0
        assert "products" in ev and isinstance(ev["products"], list)
        assert len(ev["products"]) > 0

    finally:
        ws_manager.broadcast_sync = original_broadcast_sync
        ws_manager.broadcast = original_broadcast

    print("✅ PASS: WebSocket event 'CATALOG_ONBOARDED' broadcast successfully.")


def test_quota_isolation():
    """
    Acceptance Criterion 7:
    Verify that an invalid or exhausted GEMINI_VIDEO_API_KEY does not crash audio pipeline
    or normal voice sales transactions.
    """
    print("\n--- TEST 7: test_quota_isolation ---")
    old_video_key = os.environ.get("GEMINI_VIDEO_API_KEY", "")
    try:
        # Intentionally inject an invalid / quota-exhausted video key
        os.environ["GEMINI_VIDEO_API_KEY"] = "AIzaSy_EXHAUSTED_VIDEO_KEY_429_RATE_LIMIT"

        # 1. Video ingestion must still operate safely via failover or offline fallback
        prods = GeminiService.digitize_catalog_from_video(
            video_bytes=SYNTHETIC_MP4_BYTES,
            mime_type="video/mp4"
        )
        assert len(prods) > 0, "Video service should gracefully fall back without crashing."
        print(f"Video pipeline resilience OK (returned {len(prods)} products despite invalid video key).")

        # 2. Audio and voice sale pipeline must remain 100% operational
        db = SessionLocal()
        try:
            res_audio_sale = InventoryService.process_transaction_event(
                vendor_id="DEMO_KIRANA_KOP",
                raw_text="१ साखर विकली",
                db=db
            )
            assert res_audio_sale["success"] is True, "Audio/voice sale failed during video quota exhaustion!"
            print(f"Audio/Voice sale succeeded: {res_audio_sale['reply_message'].splitlines()[0]}")
        finally:
            db.close()

    finally:
        if old_video_key:
            os.environ["GEMINI_VIDEO_API_KEY"] = old_video_key
        else:
            os.environ.pop("GEMINI_VIDEO_API_KEY", None)

    print("✅ PASS: Quota isolation verified — exhausted video key did not affect audio pipeline.")


def run_all_tests():
    print("=" * 70)
    print("VYAPARAI ACCEPTANCE TEST SUITE: 15-SECOND VIDEO STORE ONBOARDING")
    print("Specification: 02_Ideal_Expectation_15s_Video_Store_Onboarding.md")
    print("=" * 70)

    init_db()
    db = SessionLocal()
    try:
        InventoryService.seed_initial_catalog(db, force=True)
    finally:
        db.close()

    tests = [
        ("test_video_ingress_greenapi", test_video_ingress_greenapi),
        ("test_simulator_video_upload", test_simulator_video_upload),
        ("test_gemini_video_extraction", test_gemini_video_extraction),
        ("test_db_persistence_and_snapshot", test_db_persistence_and_snapshot),
        ("test_voice_continuity_loop", test_voice_continuity_loop),
        ("test_websocket_stream_payload", test_websocket_stream_payload),
        ("test_quota_isolation", test_quota_isolation)
    ]

    passed = 0
    failed = 0

    for name, test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"\n❌ FAILED: {name}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print(f"SUMMARY: {passed} PASSED, {failed} FAILED (TOTAL: {len(tests)})")
    print("=" * 70)

    if failed > 0:
        sys.exit(1)
    else:
        print("\n>>> ALL 7 VIDEO ONBOARDING ACCEPTANCE CRITERIA PASSED 100%! <<<\n")


if __name__ == "__main__":
    run_all_tests()
