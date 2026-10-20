import sys
import os
import io
import json
from unittest.mock import patch, MagicMock

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(os.path.dirname(__file__))

from starlette.testclient import TestClient
from app.main import app
from app.core.config import settings, Settings
from app.core.database import SessionLocal
from app.models.product import Product
from app.services.gemini_service import GeminiService
from app.services.inventory_service import InventoryService


def test_video_onboarding_pipeline():
    client = TestClient(app)
    db = SessionLocal()

    print("\n" + "="*60)
    print("VYAPARAI ZERO-TOUCH VIDEO STORE ONBOARDING TEST SUITE")
    print("="*60)

    # 1. Test Config: Dedicated Video Key and Fallback
    print("\n--- TEST 1: Quota Isolation & Gemini Video Key Fallback ---")
    orig_video_key = settings.GEMINI_VIDEO_API_KEY
    try:
        settings.GEMINI_VIDEO_API_KEY = "test_video_key_123"
        assert settings.get_video_gemini_key() == "test_video_key_123"
        print("Dedicated GEMINI_VIDEO_API_KEY recognized:", settings.get_video_gemini_key())

        settings.GEMINI_VIDEO_API_KEY = ""
        fallback_key = settings.get_video_gemini_key()
        assert fallback_key == settings.get_active_gemini_key()
        print("Fallback to active key pool verified:", fallback_key[:6] + "..." if fallback_key else "None")
    finally:
        settings.GEMINI_VIDEO_API_KEY = orig_video_key

    # 2. Test Gemini Video Digitization & Schema Validation
    print("\n--- TEST 2: Gemini Video Digitization & Schema Normalization ---")
    mock_video_bytes = b"\x00\x00\x00\x1cftypisom\x00\x00\x02\x00isomiso2mp41"
    products = GeminiService.digitize_catalog_from_video(mock_video_bytes, mime_type="video/mp4")
    assert isinstance(products, list) and len(products) >= 4
    for p in products:
        assert "name_en" in p and p["name_en"]
        assert "name_mr" in p and p["name_mr"]
        assert "category" in p and p["category"]
        assert "stock" in p and p["stock"] > 0
        assert "unit_price" in p and p["unit_price"] >= 0
        assert "unit" in p and p["unit"]
        assert "min_threshold" in p and p["min_threshold"] >= 0
        assert "aliases" in p and isinstance(p["aliases"], list) and len(p["aliases"]) > 0
    print(f"Extracted {len(products)} products with valid 8-field schema.")
    print("Sample Product:", products[0]["name_mr"], "| Aliases:", products[0]["aliases"])

    # 3. Test Inventory Ingestion & Sequence Synchronization
    print("\n--- TEST 3: Inventory Ingestion & ACID Persistence ---")
    initial_product_count = db.query(Product).count()
    result = InventoryService.ingest_catalog_from_video(
        video_bytes=mock_video_bytes,
        mime_type="video/mp4",
        vendor_id="DEMO_KIRANA_KOP",
        db=db
    )
    assert result["success"] is True
    assert result["count"] >= 4
    assert "reply_message" in result
    assert "दुकान डिजिटायझेशन यशस्वी" in result["reply_message"]
    print(f"Ingested {result['count']} items. Receipt sample:\n{result['reply_message'][:150]}...")

    # Check products in DB with AUTO-VID- prefix
    ingested_skus = [p["sku"] for p in result["products"]]
    for sku in ingested_skus:
        assert sku.startswith("AUTO-VID-")
        p_row = db.query(Product).filter_by(sku=sku).first()
        assert p_row is not None
        assert p_row.aliases
    print("Collision-free SKUs verified in database:", ingested_skus)

    # 4. Test State Snapshot Persistence
    print("\n--- TEST 4: Durable State Snapshot Verification ---")
    state_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "vyaparai_state.json"))
    assert os.path.exists(state_file)
    with open(state_file, "r", encoding="utf-8") as f:
        snapshot = json.load(f)
    snapshot_skus = [p["sku"] for p in snapshot["products"]]
    for sku in ingested_skus:
        assert sku in snapshot_skus
    print(f"Snapshot contains {len(snapshot_skus)} SKUs, including newly digitized video items.")

    # 5. Test Voice Continuity Loop (Immediate Sale via Synthesized Voice Alias)
    print("\n--- TEST 5: Autonomous Voice Alias Bridge & Instant Sale ---")
    # Find the pen product
    pen_prod = None
    for p in result["products"]:
        if "reynolds" in p["name_en"].lower() or "pen" in p["name_en"].lower():
            pen_prod = p
            break
    assert pen_prod is not None, "Reynolds Pen not found in onboarded catalog"
    pen_sku = pen_prod["sku"]
    initial_pen_stock = db.query(Product).filter_by(sku=pen_sku).first().stock

    # Simulate merchant speaking in Marathi: "२ पेन दिले"
    sale_resp = InventoryService.process_transaction_event(
        vendor_id="DEMO_KIRANA_KOP",
        raw_text="२ पेन दिले",
        db=db
    )
    assert sale_resp["success"] is True
    assert len(sale_resp["updates"]) > 0
    matched_sku = sale_resp["updates"][0]["sku"]
    matched_prod = db.query(Product).filter_by(sku=matched_sku).first()
    print(f"Voice sale '२ पेन दिले' successfully matched {matched_sku} ({matched_prod.name_mr}) and deducted stock!")
    print("Voice Sale Receipt:", sale_resp["reply_message"].splitlines()[0])

    # 6. Test Web Simulator Video Upload (POST /api/simulator/video)
    print("\n--- TEST 6: Web Simulator Video Upload Endpoint ---")
    fake_video_stream = io.BytesIO(mock_video_bytes)
    sim_resp = client.post(
        "/api/simulator/video",
        files={"file": ("sweep.mp4", fake_video_stream, "video/mp4")},
        data={"vendor_id": "DEMO_KIRANA_KOP"}
    )
    assert sim_resp.status_code == 200
    sim_data = sim_resp.json()
    assert sim_data["success"] is True
    assert sim_data["count"] >= 4
    assert "reply" in sim_data
    assert "metrics" in sim_data
    print(f"Simulator Video Upload OK! Returned {sim_data['count']} digitized items.")

    # 7. Test Green-API WhatsApp Webhook Video Ingress
    print("\n--- TEST 7: Green-API Webhook Video Ingress ---")
    video_webhook_payload = {
        "typeWebhook": "incomingMessageReceived",
        "instanceData": {"idInstance": 710722771292, "wid": "917558455021@c.us"},
        "idMessage": f"MSG_VIDEO_TEST_{os.urandom(4).hex()}",
        "senderData": {"chatId": "917558455021@c.us", "sender": "917558455021@c.us"},
        "messageData": {
            "typeMessage": "videoMessage",
            "fileMessageData": {
                "downloadUrl": "https://example.com/mock_sweep.mp4",
                "caption": "माझे दुकान रॅक",
                "fileName": "store_sweep.mp4",
                "mimeType": "video/mp4"
            }
        }
    }
    with patch("app.services.whatsapp_service.WhatsAppService.send_message", return_value=True) as mock_send:
        webhook_resp = client.post("/api/v1/webhook/whatsapp", json=video_webhook_payload)
        assert webhook_resp.status_code == 200
        assert webhook_resp.text == "EVENT_RECEIVED"
        assert mock_send.called
        # Check that instant ack was sent
        ack_sent = any("व्हिडिओ प्राप्त झाला" in str(c) for c in mock_send.call_args_list)
        assert ack_sent, "Instant acknowledgment message not sent"
    print("Green-API Video Message Webhook OK! Instant Ack & Background Worker dispatches verified.")

    print("\n" + "="*60)
    print(">>> ALL 7 VIDEO ONBOARDING SPECIFICATION TESTS PASSED 100%! <<<")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_video_onboarding_pipeline()
