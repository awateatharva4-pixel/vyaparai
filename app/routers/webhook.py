import os
import hmac
import hashlib
import xml.sax.saxutils
from typing import Optional
from fastapi import APIRouter, Request, Response, Depends, BackgroundTasks, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db, SessionLocal
from app.core.config import settings
from app.services.inventory_service import InventoryService
from app.services.whatsapp_service import WhatsAppService
from app.models.product import IdempotencyRecord

router = APIRouter(prefix="/api/v1/webhook", tags=["WhatsApp Webhook"])


def background_process_message(vendor_id: str, message_body: str, message_id: str, to_phone: Optional[str] = None):
    """
    Asynchronous background worker for Meta Cloud API.
    Decoupled from HTTP response to guarantee sub-50ms ingress and avoid Meta 5s timeout.
    """
    db: Session = SessionLocal()
    try:
        # 1. Thread-Safe Idempotency Check: Prevent duplicate processing if Meta retries
        if message_id:
            try:
                db.add(IdempotencyRecord(message_id=message_id, vendor_id=vendor_id))
                db.commit()
            except IntegrityError:
                db.rollback()
                print(f"[IDEMPOTENCY DUPLICATE] Safely discarded duplicate delivery for {message_id}")
                return

        # 2. Process Transaction
        result = InventoryService.process_transaction_event(vendor_id, message_body, db)

        # 3. Send WhatsApp Outbound Confirmation
        reply_text = result.get("reply_message", "नोंद झाली (Recorded).")
        target = to_phone or vendor_id
        WhatsAppService.send_message(to_phone=target, message=reply_text)
    except Exception as e:
        print(f"[WORKER ERROR]: {e}")
    finally:
        db.close()


@router.get("/whatsapp")
def verify_meta_webhook(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge")
):
    """
    Meta Cloud API Webhook Handshake Verification.
    Uses timing-safe comparison (hmac.compare_digest) to prevent side-channel timing attacks.
    """
    expected = settings.META_WEBHOOK_VERIFY_TOKEN or ""
    if mode == "subscribe" and hmac.compare_digest(token or "", expected):
        return Response(content=challenge, media_type="text/plain")
    return Response(content="Verification failed", status_code=403)


@router.post("/whatsapp")
async def handle_whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Production Webhook Ingress for Twilio and Meta Cloud API.
    - Twilio: Responds with in-session TwiML XML (<Response><Message>...</Message></Response>)
      so WhatsApp receives the instant vernacular receipt without requiring pre-approved templates.
    - Meta Cloud API: Uses async background queue with immediate 200 OK to meet Meta 5s timeout.
    """
    raw_body = await request.body()
    content_type = request.headers.get("content-type", "")

    # Meta X-Hub-Signature-256 HMAC Validation (if configured)
    meta_sig = request.headers.get("x-hub-signature-256")
    meta_app_secret = os.getenv("META_APP_SECRET", "")
    if meta_sig and meta_app_secret:
        expected_sig = "sha256=" + hmac.new(meta_app_secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(meta_sig, expected_sig):
            return Response(content="Forbidden: Invalid Signature", status_code=403)

    # 1. TWILIO Ingress (Form URL-encoded)
    if "application/x-www-form-urlencoded" in content_type:
        form_data = await request.form()
        sender_phone = str(form_data.get("From", ""))
        message_body = str(form_data.get("Body", "")).strip()
        message_id = str(form_data.get("MessageSid", ""))

        if not message_body:
            # Twilio status ping or empty event
            return Response(content='<?xml version="1.0" encoding="UTF-8"?><Response/>', media_type="application/xml")

        # Map vendor to demo store catalog (so shopkeeper's phone controls DEMO_KIRANA_KOP)
        vendor_id = "DEMO_KIRANA_KOP"
        
        db: Session = SessionLocal()
        try:
            # Idempotency check
            if message_id:
                try:
                    db.add(IdempotencyRecord(message_id=message_id, vendor_id=vendor_id))
                    db.commit()
                except IntegrityError:
                    db.rollback()
                    print(f"[IDEMPOTENCY DUPLICATE] Discarded duplicate delivery for {message_id}")
                    twiml = '<?xml version="1.0" encoding="UTF-8"?><Response><Message>⚠️ ही नोंद आधीच स्वीकारण्यात आली आहे (Duplicate Request).</Message></Response>'
                    return Response(content=twiml, media_type="application/xml")

            # Process transaction
            result = InventoryService.process_transaction_event(vendor_id, message_body, db)
            reply_text = result.get("reply_message", "नोंद झाली (Recorded).")
            escaped_reply = xml.sax.saxutils.escape(reply_text)
            twiml = f'<?xml version="1.0" encoding="UTF-8"?>\n<Response>\n    <Message>{escaped_reply}</Message>\n</Response>'
            return Response(content=twiml, media_type="application/xml")
        except Exception as e:
            print(f"[TWILIO WEBHOOK ERROR]: {e}")
            err_msg = xml.sax.saxutils.escape("⚠️ क्षमस्व! नोंद करताना त्रुटी आली. कृपया पुन्हा प्रयत्न करा.")
            return Response(content=f'<?xml version="1.0" encoding="UTF-8"?>\n<Response>\n    <Message>{err_msg}</Message>\n</Response>', media_type="application/xml")
        finally:
            db.close()

    # 2. META Cloud API Ingress (JSON)
    elif "application/json" in content_type:
        vendor_id = "DEMO_KIRANA_KOP"
        message_body = ""
        message_id = ""
        sender_phone = ""
        try:
            body_json = await request.json()
            entry = body_json["entry"][0]["changes"][0]["value"]
            message = entry["messages"][0]
            sender_phone = message.get("from", "")
            message_id = message.get("id", "")
            if message.get("type") == "text":
                message_body = message["text"]["body"]
            elif message.get("type") == "audio":
                message_body = "ऑडिओ नोंद (Voice note received)"
        except (KeyError, IndexError, ValueError):
            return Response(status_code=200)

        if message_body:
            background_tasks.add_task(
                background_process_message,
                vendor_id=vendor_id,
                message_body=message_body,
                message_id=message_id,
                to_phone=sender_phone
            )
        return Response(content="EVENT_RECEIVED", status_code=200)

    return Response(content="EVENT_RECEIVED", status_code=200)
