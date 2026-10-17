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

    print("\n>>> ALL API ENDPOINTS VERIFIED 100% OPERATIONAL! <<<")

if __name__ == "__main__":
    test_endpoints()
