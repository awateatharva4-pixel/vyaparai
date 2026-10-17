import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(os.path.dirname(__file__))

from starlette.testclient import TestClient
from app.main import app

def test_endpoints():
    client = TestClient(app)
    
    print("--- 1. Testing GET / (Dashboard) ---")
    r1 = client.get("/")
    assert r1.status_code == 200
    assert "VyaparAI" in r1.text
    print("Dashboard OK! (Status 200)")

    print("--- 2. Testing GET /test-console (Simulator) ---")
    r2 = client.get("/test-console")
    assert r2.status_code == 200
    assert "WhatsApp" in r2.text
    print("Simulator OK! (Status 200)")

    print("--- 3. Testing GET /api/metrics ---")
    r3 = client.get("/api/metrics")
    assert r3.status_code == 200
    data = r3.json()
    assert "total_skus" in data
    print(f"Metrics OK! (Total SKUs: {data['total_skus']}, Valuation: Rs {data['total_valuation']})")

    print("--- 4. Testing POST /api/simulator/send ---")
    r4 = client.post("/api/simulator/send", json={"text": "२ पुडे पार्ले-जी दिले"})
    assert r4.status_code == 200
    reply = r4.json()["reply"]
    print(f"Simulator Bot Reply OK: {reply.splitlines()[0]}")

    print("--- 5. Testing GET /api/export-gst-csv ---")
    r5 = client.get("/api/export-gst-csv")
    assert r5.status_code == 200
    assert "CGST 9%" in r5.text
    print(f"GST CSV Export OK! Length: {len(r5.text)} chars")

    print("--- 6. Testing POST /api/items/quick-add-dairy (Hook 1) ---")
    r6 = client.post("/api/items/quick-add-dairy")
    assert r6.status_code == 200
    print(f"Quick Add Dairy SKU OK! Item: {r6.json()['item']['name_mr']}")

    print("--- 7. Testing POST /api/v1/webhook/whatsapp (Twilio TwiML Ingress) ---")
    r7 = client.post(
        "/api/v1/webhook/whatsapp",
        data={"From": "whatsapp:+919579869506", "Body": "१ साखर विकली", "MessageSid": "SM_TEST_API_001"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert r7.status_code == 200
    assert "application/xml" in r7.headers.get("content-type", "")
    assert "<Response>" in r7.text and "<Message>" in r7.text
    print("Twilio Webhook Ingress OK! (Returned TwiML XML Response)")

    print("--- 8. Testing POST /api/v1/webhook/whatsapp (Green-API Ingress) ---")
    green_payload = {
        "typeWebhook": "incomingMessageReceived",
        "instanceData": {"idInstance": 710722771292, "wid": "917558455021@c.us"},
        "idMessage": "MSG_GREEN_TEST_002",
        "senderData": {"chatId": "917558455021@c.us", "sender": "917558455021@c.us"},
        "messageData": {
            "typeMessage": "textMessage",
            "textMessageData": {"textMessage": "२ साखर विकली"}
        }
    }
    r8 = client.post("/api/v1/webhook/whatsapp", json=green_payload)
    assert r8.status_code == 200
    assert r8.text == "EVENT_RECEIVED"
    print("Green-API Webhook Ingress OK! (Status 200 EVENT_RECEIVED)")

    print("--- 9. Testing GET /api/reports/daily-closing (Slide 2 & 5 Ledger Preview) ---")
    r9 = client.get("/api/reports/daily-closing")
    assert r9.status_code == 200
    d9 = r9.json()
    assert d9["status"] == "SUCCESS"
    assert "formatted_message" in d9
    print(f"8:00 PM Daily Ledger Preview OK! Revenue: Rs {d9['today_revenue']}, Sales Tx: {d9['today_sales_count']}")

    print("--- 10. Testing POST /api/reports/daily-closing (Slide 2 & 5 WhatsApp Push) ---")
    r10 = client.post("/api/reports/daily-closing")
    assert r10.status_code == 200
    d10 = r10.json()
    assert d10["status"] == "SUCCESS"
    print(f"8:00 PM Daily Ledger WhatsApp Push OK! Delivery to Merchant: {d10['whatsapp_sent']}")

    print("--- 11. Testing GET /api/udhar/ledger (Slide 5 Customer Credit Ledger) ---")
    r11 = client.get("/api/udhar/ledger")
    assert r11.status_code == 200
    credits = r11.json()
    assert len(credits) >= 3
    print(f"Udhar Credit Ledger OK! ({len(credits)} customer accounts loaded)")

    print("--- 12. Testing POST /api/udhar/remind/{id} (Slide 5 Polite WhatsApp Reminder) ---")
    first_credit = credits[0]
    r12 = client.post(f"/api/udhar/remind/{first_credit['id']}")
    assert r12.status_code == 200
    d12 = r12.json()
    assert d12["success"] is True
    assert "बाबुराव किराणा स्टोअर्स" in d12["reminder_message"]
    print(f"Polite Udhar Reminder OK! Customer: {d12['customer_name']}, Sent: {d12['whatsapp_sent']}")

    print("--- 13. Testing WebSocket /ws/inventory (Slide 1 & 3 Live Sync Stream) ---")
    with client.websocket_connect("/ws/inventory") as ws:
        ws.send_text("ping")
        pong = ws.receive_text()
        assert pong == "pong"
    print("WebSocket /ws/inventory Ping-Pong OK!")

    print("--- 14. Testing POST /api/simulator/audio (Voice Pipeline Ingress) ---")
    import io, wave, struct
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(b'\x00\x00' * 8000)
    wav_bytes = buf.getvalue()
    r14 = client.post(
        "/api/simulator/audio",
        files={"file": ("test_voice.wav", wav_bytes, "audio/wav")},
        data={"vendor_id": "DEMO_KIRANA_KOP"}
    )
    assert r14.status_code == 200
    d14 = r14.json()
    assert "reply" in d14
    assert "🎙️ *ऑडिओ ऐकले:*" in d14["reply"]
    print(f"Simulator Audio Voice Note Pipeline OK! Reply: {d14['reply'].splitlines()[0]}")

    print("--- 15. Testing GET /api/state/backup (Unauthorized without admin token) ---")
    r15_unauth = client.get("/api/state/backup")
    assert r15_unauth.status_code == 401
    print("State Backup Unauthorized Guard OK! (Status 401)")

    print("--- 16. Testing GET /api/state/backup (Authorized with X-Admin-Token) ---")
    r16 = client.get("/api/state/backup", headers={"X-Admin-Token": "vyaparai_admin_2026"})
    assert r16.status_code == 200
    d16 = r16.json()
    assert d16["status"] == "SUCCESS"
    assert "products" in d16 and "transactions" in d16
    print(f"State Backup OK! Snapshot products: {len(d16['products'])}, transactions: {len(d16['transactions'])}")

    print("--- 17. Testing POST /api/state/restore (Unauthorized without admin token) ---")
    r17_unauth = client.post("/api/state/restore", json={"products": []})
    assert r17_unauth.status_code == 401
    print("State Restore Unauthorized Guard OK! (Status 401)")

    print("--- 18. Testing POST /api/state/restore (Authorized with X-Admin-Token) ---")
    r18 = client.post(
        "/api/state/restore",
        headers={"X-Admin-Token": "vyaparai_admin_2026"},
        json={"snapshot": d16.get("snapshot", d16)}
    )
    assert r18.status_code == 200
    d18 = r18.json()
    assert d18["status"] == "SUCCESS"
    print(f"State Restore OK! Result: {d18['message']}")

    print("\n>>> ALL API & STATE RESILIENCE ENDPOINTS VERIFIED 100% OPERATIONAL! <<<")

if __name__ == "__main__":
    test_endpoints()


