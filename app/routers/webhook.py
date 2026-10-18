import os
import hmac
import hashlib
import xml.sax.saxutils
import httpx
from typing import Optional
from fastapi import APIRouter, Request, Response, Depends, BackgroundTasks, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db, SessionLocal
from app.core.config import settings, is_merchant_sender
from app.services.inventory_service import InventoryService
from app.services.whatsapp_service import WhatsAppService
from app.services.gemini_service import GeminiService
from app.services.audio_service import AudioNormalizer
from app.models.product import IdempotencyRecord, Product

router = APIRouter(prefix="/api/v1/webhook", tags=["WhatsApp Webhook"])


def background_process_message(
    vendor_id: str,
    message_body: str,
    message_id: str,
    to_phone: Optional[str] = None,
    transcription: Optional[str] = None,
    parsed_payload: Optional[dict] = None
):
    """
    Asynchronous background worker for WhatsApp Ingress (Meta Cloud API, Green-API, Twilio).
    Decoupled from HTTP response to guarantee sub-50ms ingress and avoid webhook timeouts.
    """
    db: Session = SessionLocal()
    try:
        # 1. Thread-Safe Idempotency Check: Prevent duplicate processing if gateway retries
        if message_id:
            try:
                db.add(IdempotencyRecord(message_id=message_id, vendor_id=vendor_id))
                db.commit()
            except IntegrityError:
                db.rollback()
                print(f"[IDEMPOTENCY DUPLICATE] Safely discarded duplicate delivery for {message_id}")
                return

        # 2. Process Transaction with pre-parsed audio payload if available
        result = InventoryService.process_transaction_event(
            vendor_id=vendor_id,
            raw_text=message_body,
            db=db,
            parsed_payload=parsed_payload
        )

        # 3. Send WhatsApp Outbound Confirmation
        reply_text = result.get("reply_message", "नोंद झाली (Recorded).")
        if transcription:
            reply_text = f"🎙️ *ऑडिओ ऐकले:* \"{transcription}\"\n\n{reply_text}"
        target = to_phone or vendor_id
        WhatsAppService.send_message(to_phone=target, message=reply_text)
    except Exception as e:
        print(f"[WORKER ERROR]: {e}")
    finally:
        db.close()


def background_process_video(
    vendor_id: str,
    message_id: str,
    download_url: Optional[str] = None,
    video_bytes: Optional[bytes] = None,
    mime_type: str = "video/mp4",
    to_phone: Optional[str] = None
):
    """
    Asynchronous background worker for WhatsApp Video Ingress (Green-API / Meta).
    Follows HTTP 302 redirects to stream video bytes, runs multimodal catalog ingestion,
    and dispatches formatted Marathi WhatsApp confirmation receipt.
    """
    db: Session = SessionLocal()
    try:
        if message_id:
            try:
                db.add(IdempotencyRecord(message_id=message_id, vendor_id=vendor_id))
                db.commit()
            except IntegrityError:
                db.rollback()
                print(f"[IDEMPOTENCY DUPLICATE] Safely discarded duplicate video delivery for {message_id}")
                return

        # Download with redirect handling
        if not video_bytes and download_url:
            try:
                with httpx.Client(timeout=60.0, follow_redirects=True) as client:
                    resp = client.get(download_url)
                    if resp.status_code == 200:
                        video_bytes = resp.content
                    else:
                        print(f"[VIDEO DOWNLOAD WARN]: Status {resp.status_code} for URL {download_url}")
            except Exception as e:
                print(f"[VIDEO DOWNLOAD ERROR]: {e}")

        # Fallback to Green-API downloadFile endpoint if downloadUrl was expired or missing
        if not video_bytes and message_id and settings.GREEN_API_HOST and settings.GREEN_API_INSTANCE_ID and settings.GREEN_API_TOKEN:
            try:
                api_url = f"{settings.GREEN_API_HOST}/waInstance{settings.GREEN_API_INSTANCE_ID}/downloadFile/{settings.GREEN_API_TOKEN}"
                chat_id = to_phone if ("@c.us" in (to_phone or "") or "@g.us" in (to_phone or "")) else f"{to_phone}@c.us"
                with httpx.Client(timeout=60.0, follow_redirects=True) as client:
                    res_api = client.post(api_url, json={"chatId": chat_id, "idMessage": message_id})
                    if res_api.status_code == 200:
                        fresh_url = res_api.json().get("downloadUrl")
                        if fresh_url:
                            resp2 = client.get(fresh_url)
                            if resp2.status_code == 200:
                                video_bytes = resp2.content
            except Exception as e:
                print(f"[GREEN-API VIDEO FALLBACK ERROR]: {e}")

        if not video_bytes:
            print("[VIDEO WORKER ERROR]: No video bytes could be retrieved.")
            if to_phone:
                WhatsAppService.send_message(to_phone=to_phone, message="⚠️ व्हिडिओ डाउनलोड करण्यात अडचण आली. कृपया पुन्हा पाठवा.")
            return

        result = InventoryService.ingest_catalog_from_video(
            video_bytes=video_bytes,
            mime_type=mime_type,
            vendor_id=vendor_id,
            db=db
        )
        reply_text = result.get("reply_message", "🎉 दुकान डिजिटायझेशन यशस्वी!")
        target = to_phone or vendor_id
        WhatsAppService.send_message(to_phone=target, message=reply_text)
    except Exception as e:
        print(f"[VIDEO WORKER ERROR]: {e}")
    finally:
        db.close()


def background_process_customer_yaadi_image(
    vendor_id: str,
    customer_phone: str,
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
    caption: str = ""
):
    """
    Background worker for WhatsApp Photo Ingress:
    1. If caption indicates restock (e.g. 'restock', 'माल आला', 'भरले', 'आले', 'आणले', 'supplier', 'inward'),
       it parses the items and directly INCREMENTS stock (restocks the store).
    2. Otherwise, treats as Customer Handwritten Yaadi Photo Ingress (Specification 03):
       Grounds handwritten slip against active catalog, creates CustomerOrder in PENDING status,
       stages in Merchant UI, and dispatches itemized Marathi confirmation receipt to customer.
    """
    db: Session = SessionLocal()
    try:
        prods = db.query(Product).filter_by(vendor_id=vendor_id).all()
        catalog_items = [p.to_dict() for p in prods]
        parsed = GeminiService.parse_handwritten_yaadi(
            image_bytes=image_bytes,
            mime_type=mime_type,
            catalog_items=catalog_items
        )
        order_items = parsed.get("order_items", [])

        # Check for Restock Photo Inward
        clean_caption = (caption or "").lower().strip()
        is_restock = any(w in clean_caption for w in ["restock", "माल आला", "भरले", "आले", "आणले", "supplier", "inward", "invoice", "पावती"])

        if is_restock and order_items:
            from app.core.websocket import ws_manager
            restocked_lines = []
            for item in order_items:
                sku = item.get("sku_matched")
                qty = float(item.get("quantity", 0.0))
                if sku and qty > 0:
                    p = db.query(Product).filter_by(vendor_id=vendor_id, sku=sku).first()
                    if p:
                        p.stock += qty
                        restocked_lines.append(f"• {p.name_mr}: +{qty:g} {p.unit} (सद्य साठा: {p.stock:g} {p.unit})")
            db.commit()
            InventoryService.save_state_snapshot(db, vendor_id=vendor_id)
            metrics = InventoryService.get_dashboard_metrics(db, vendor_id=vendor_id)
            try:
                ws_manager.broadcast_sync({"type": "METRICS_UPDATE", "vendor_id": vendor_id, "metrics": metrics})
            except Exception:
                pass
            receipt = "🚚 *फोटोवरून माल भरला (Restock Success)!* 📦\n━━━━━━━━━━━━━━━━━━━━\n" + "\n".join(restocked_lines) + "\n━━━━━━━━━━━━━━━━━━━━\nदुकान साठा यशस्वीरित्या अपडेट झाला."
            WhatsAppService.send_message(to_phone=customer_phone, message=receipt)
            return

        order = InventoryService.create_customer_yaadi_order(
            customer_phone=customer_phone,
            items=order_items,
            raw_message=f"Handwritten Chit / किराणा यादी (Photo){': ' + caption if caption else ''}",
            vendor_id=vendor_id,
            db=db
        )
        receipt = InventoryService.format_customer_yaadi_receipt(order)
        WhatsAppService.send_message(to_phone=customer_phone, message=receipt)

        # Notify Merchant Admin Phone (9579869506) with instant WhatsApp alert
        cust_display = "व्यंकटेश पै (Venkatesh Pai)" if ("7019259321" in str(customer_phone)) else str(customer_phone)
        items_summary = ", ".join([f"{i.get('quantity', 1):g} {i.get('unit', '')} {i.get('name_mr', i.get('name_raw', ''))}" for i in order_items])
        merchant_alert = (
            f"🔔 *नवीन ग्राहक यादी (Photo Order)!* 📸\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *ग्राहक:* {cust_display}\n"
            f"📞 *फोन:* {customer_phone}\n"
            f"📝 *सामान:* {items_summary or 'फोटो पावती'}\n"
            f"💰 *अंदाजे बिल:* ₹{order.total_amount:g}\n"
            f"📦 *ऑर्डर आयडी:* `{order.order_id}`\n\n"
            f"⚡ *स्थिती:* PENDING (पॅक करण्यासाठी डॅशबोर्ड तपासा)"
        )
        WhatsAppService.send_message(to_phone="919579869506", message=merchant_alert)
    except Exception as e:
        print(f"[YAADI IMAGE WORKER ERROR]: {e}")
    finally:
        db.close()


def background_process_customer_yaadi_text(
    vendor_id: str,
    customer_phone: str,
    text_message: str
):
    """
    Background worker for Customer Text Yaadi Ingress (Specification 03).
    Implements Two-Way Confirmation Loop & Stock Reservation:
    1. If customer replies 'हो' / 'Confirm': confirms order and notifies merchant (9579869506).
    2. If customer replies 'cancel' / 'रद्द करा': rolls back reserved stock immediately.
    3. Otherwise: parses items, reserves stock immediately, sends confirmation to customer,
       and alerts merchant on 9579869506 with 30m window.
    """
    db: Session = SessionLocal()
    try:
        norm_txt = (text_message or "").strip().lower()

        # 1. Customer Confirmation Loop
        if norm_txt in ["हो", "ho", "yes", "confirm", "nakkie", "नक्की", "theek ahe", "chalel", "चालेल", "करा", "पाठवा", "done", "ok", "okay"]:
            confirmed_order = InventoryService.confirm_customer_order(
                customer_phone=customer_phone,
                vendor_id=vendor_id,
                db=db
            )
            if confirmed_order:
                print(f"[CUSTOMER CONFIRMATION SUCCESS]: Order {confirmed_order.order_id} confirmed by customer {customer_phone}")
                return

        # 2. Customer Cancellation Loop
        if any(w in norm_txt for w in ["cancel", "रद्द करा", "नको", "nako", "मागे घ्या"]):
            clean_p = customer_phone.replace("+", "").replace("@c.us", "").strip()
            pending_order = db.query(CustomerOrder).filter(
                CustomerOrder.vendor_id == vendor_id,
                CustomerOrder.status.in_(["PENDING", "CONFIRMED"]),
                CustomerOrder.customer_phone.ilike(f"%{clean_p[-10:]}%")
            ).order_by(CustomerOrder.created_at.desc()).first()
            if pending_order:
                InventoryService.restitute_expired_order_stock(pending_order.order_id, vendor_id=vendor_id, db=db)
                WhatsAppService.send_message(to_phone=customer_phone, message=f"❌ आपली ऑर्डर `{pending_order.order_id}` रद्द केली आहे व साठा पूर्ववत केला आहे.")
                return

        # 3. New Order Placement with Immediate Stock Reservation
        prods = db.query(Product).filter_by(vendor_id=vendor_id).all()
        catalog_items = [p.to_dict() for p in prods]
        parsed = GeminiService.parse_yaadi_from_text(
            text=text_message,
            catalog_items=catalog_items
        )
        order = InventoryService.create_customer_yaadi_order(
            customer_phone=customer_phone,
            items=parsed.get("order_items", []),
            raw_message=text_message,
            vendor_id=vendor_id,
            reservation_minutes=30,
            db=db
        )
        receipt = InventoryService.format_customer_yaadi_receipt(order)
        WhatsAppService.send_message(to_phone=customer_phone, message=receipt)

        # Notify Merchant Admin Phone (9579869506) with instant WhatsApp alert
        cust_display = "व्यंकटेश पै (Venkatesh Pai)" if ("7019259321" in str(customer_phone)) else str(customer_phone)
        items_summary = ", ".join([f"{i.get('quantity', 1):g} {i.get('unit', '')} {i.get('name_mr', i.get('name_raw', ''))}" for i in parsed.get("order_items", [])])
        merchant_alert = (
            f"🔔 *नवीन ग्राहक ऑर्डर (WhatsApp Order)!* 🏪\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *ग्राहक:* {cust_display}\n"
            f"📞 *फोन:* {customer_phone}\n"
            f"📝 *सामान:* {items_summary or text_message}\n"
            f"💰 *अंदाजे बिल:* ₹{order.total_amount:g}\n"
            f"📦 *ऑर्डर आयडी:* `{order.order_id}`\n"
            f"✅ *साठा तात्काळ आरक्षित (Reserved) केला आहे!*\n\n"
            f"⏳ *३० मिनिटांचा कालावधी:* अर्ध्या तासात डॅशबोर्डवर 'Pack & Fulfill' करा अन्यथा साठा पुन्हा जमा (Auto-Undo) होईल."
        )
        WhatsAppService.send_message(to_phone="919579869506", message=merchant_alert)
    except Exception as e:
        print(f"[YAADI TEXT WORKER ERROR]: {e}")
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
    if meta_app_secret:
        if not meta_sig:
            return Response(content="Forbidden: Missing Signature", status_code=403)
        expected_sig = "sha256=" + hmac.new(meta_app_secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(meta_sig, expected_sig):
            return Response(content="Forbidden: Invalid Signature", status_code=403)

    # 1. TWILIO Ingress (Form URL-encoded)
    if "application/x-www-form-urlencoded" in content_type:
        form_data = await request.form()
        sender_phone = str(form_data.get("From", ""))
        message_body = str(form_data.get("Body", "")).strip()
        message_id = str(form_data.get("MessageSid", ""))
        media_url = str(form_data.get("MediaUrl0", "")).strip()
        audio_transcription = None

        # Handle Twilio incoming voice/audio notes
        if not message_body and media_url:
            raw_audio_bytes = b""
            try:
                auth = None
                if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
                    auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                async with httpx.AsyncClient(timeout=20.0, auth=auth, follow_redirects=True) as http_client:
                    resp = await http_client.get(media_url)
                    if resp.status_code == 200:
                        raw_audio_bytes = resp.content
            except Exception as e:
                print(f"[TWILIO AUDIO DOWNLOAD ERROR]: {e}")

            if raw_audio_bytes:
                norm_bytes, detected_mime = AudioNormalizer.normalize_audio(raw_audio_bytes, input_format="ogg")
                parsed_audio = GeminiService.transcribe_and_parse_audio(norm_bytes, mime_type=detected_mime)
                transcription = (parsed_audio.get("transcription") or "").strip()
                if transcription:
                    message_body = transcription
                    audio_transcription = transcription

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

            # Dual-Role Security Firewall: Check if sender is Merchant Admin
            is_merchant = is_merchant_sender(sender_phone)
            if not is_merchant:
                # Customer Ingress Flow: Check if customer sent an image
                media_type = str(form_data.get("MediaContentType0", "")).lower()
                if "image" in media_type and media_url:
                    raw_img_bytes = b""
                    try:
                        auth = None
                        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
                            auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                        with httpx.Client(timeout=20.0, auth=auth, follow_redirects=True) as http_client:
                            resp = http_client.get(media_url)
                            if resp.status_code == 200:
                                raw_img_bytes = resp.content
                    except Exception as img_err:
                        print(f"[TWILIO YAADI IMAGE ERROR]: {img_err}")
                    if raw_img_bytes:
                        prods = db.query(Product).filter_by(vendor_id=vendor_id).all()
                        catalog_items = [p.to_dict() for p in prods]
                        parsed = GeminiService.parse_handwritten_yaadi(raw_img_bytes, mime_type=media_type, catalog_items=catalog_items)
                        order = InventoryService.create_customer_yaadi_order(
                            customer_phone=sender_phone,
                            items=parsed.get("order_items", []),
                            raw_message="Handwritten Chit / किराणा यादी (Photo)",
                            vendor_id=vendor_id,
                            db=db
                        )
                        receipt = InventoryService.format_customer_yaadi_receipt(order)
                        escaped = xml.sax.saxutils.escape(receipt)
                        return Response(content=f'<?xml version="1.0" encoding="UTF-8"?>\n<Response>\n    <Message>{escaped}</Message>\n</Response>', media_type="application/xml")

                # Immediate Stock Query Check (Accessible to both Merchant and Customer)
                query_triggers = [
                    "satha dakhva", "saatha dakhva", "satha dakva", "sata dakhva", "sata dakva",
                    "satha dakhav", "sata dakhav", "satha sanga", "saatha sanga", "sata sanga",
                    "satha kiti", "saatha kiti", "satha", "saatha", "sata",
                    "stock dakhva", "stock dakva", "stock dakhwa", "stock dakwa",
                    "stock sanga", "stock saanga", "stock kiti", "stock kiti ahe", "stock kitna hai",
                    "stock check", "check stock", "view stock", "show stock", "stock summary", "stock list",
                    "shilak kiti", "shillak kiti", "kiti shillak", "kiti shilak",
                    "kiti ahe", "kitna hai", "shilak", "shillak", "dakhva", "dakva", "dakhav",
                    "साठा दाखवा", "स्टॉक दाखवा", "साठा सांगा", "स्टॉक सांगा", "साठा किती", "स्टॉक किती",
                    "साठा", "स्टॉक", "शिल्लक किती", "किती शिल्लक", "किती आहे", "शिल्लक आहे का", "आहे का",
                    "यादी दाखवा", "माल दाखवा", "शिल्लक माल", "शिल्लक साठा",
                    "stock batao", "stock dikhao", "kitna bacha hai", "kitna stock hai", "kya stock hai"
                ]
                msg_body_lower = message_body.lower().strip()
                if any(w in msg_body_lower for w in query_triggers) or msg_body_lower in ["stock", "stock?", "stock list", "satha", "saatha"]:
                    stock_res = InventoryService.process_transaction_event(vendor_id, message_body, db)
                    reply_text = stock_res.get("reply_message", "")
                    escaped_reply = xml.sax.saxutils.escape(reply_text)
                    return Response(content=f'<?xml version="1.0" encoding="UTF-8"?>\n<Response>\n    <Message>{escaped_reply}</Message>\n</Response>', media_type="application/xml")

                # Customer Sandboxed Command Check (Prevent Unauthorized Rollbacks)
                if any(w in msg_body_lower for w in ["undo", "cancel", "चूक झाली", "रद्द करा", "मागे घ्या"]):
                    sandbox_msg = "🙏 *नमस्कार! बाबुराव किराणा स्टोअर्स* 🏪\nआपण ग्राहक सेवेशी जोडलेले आहात. केवळ अधिकृत दुकानदार व्यवहार रद्द करू शकतात."
                    escaped = xml.sax.saxutils.escape(sandbox_msg)
                    return Response(content=f'<?xml version="1.0" encoding="UTF-8"?>\n<Response>\n    <Message>{escaped}</Message>\n</Response>', media_type="application/xml")

                # Customer Text Yaadi
                prods = db.query(Product).filter_by(vendor_id=vendor_id).all()
                catalog_items = [p.to_dict() for p in prods]
                parsed = GeminiService.parse_yaadi_from_text(message_body, catalog_items=catalog_items)
                order = InventoryService.create_customer_yaadi_order(
                    customer_phone=sender_phone,
                    items=parsed.get("order_items", []),
                    raw_message=message_body,
                    vendor_id=vendor_id,
                    db=db
                )
                receipt = InventoryService.format_customer_yaadi_receipt(order)
                escaped = xml.sax.saxutils.escape(receipt)
                return Response(content=f'<?xml version="1.0" encoding="UTF-8"?>\n<Response>\n    <Message>{escaped}</Message>\n</Response>', media_type="application/xml")

            # Authorized Merchant Flow: Process transaction with pre-parsed audio payload if available
            parsed_payload = parsed_audio if "parsed_audio" in locals() else None
            result = InventoryService.process_transaction_event(vendor_id, message_body, db, parsed_payload=parsed_payload)
            reply_text = result.get("reply_message", "नोंद झाली (Recorded).")
            if audio_transcription:
                reply_text = f"🎙️ *ऑडिओ ऐकले:* \"{audio_transcription}\"\n\n{reply_text}"
            escaped_reply = xml.sax.saxutils.escape(reply_text)
            twiml = f'<?xml version="1.0" encoding="UTF-8"?>\n<Response>\n    <Message>{escaped_reply}</Message>\n</Response>'
            return Response(content=twiml, media_type="application/xml")
        except Exception as e:
            print(f"[TWILIO WEBHOOK ERROR]: {e}")
            err_msg = xml.sax.saxutils.escape("⚠️ क्षमस्व! नोंद करताना त्रुटी आली. कृपया पुन्हा प्रयत्न करा.")
            return Response(content=f'<?xml version="1.0" encoding="UTF-8"?>\n<Response>\n    <Message>{err_msg}</Message>\n</Response>', media_type="application/xml")
        finally:
            db.close()

    # 2. GREEN-API & META JSON Ingress
    elif "application/json" in content_type:
        vendor_id = "DEMO_KIRANA_KOP"
        message_body = ""
        message_id = ""
        sender_phone = ""
        audio_transcription = None

        try:
            body_json = await request.json()
        except Exception:
            return Response(status_code=200)

        # A. Green-API Ingress (Direct WhatsApp Gateway)
        if body_json.get("typeWebhook") == "incomingMessageReceived":
            message_id = body_json.get("idMessage", "")
            sender_data = body_json.get("senderData", {})
            sender_phone = sender_data.get("chatId", "")
            msg_data = body_json.get("messageData", {})
            type_msg = msg_data.get("typeMessage", "")

            if type_msg == "textMessage":
                message_body = msg_data.get("textMessageData", {}).get("textMessage", "")
            elif type_msg == "extendedTextMessage":
                message_body = msg_data.get("extendedTextMessageData", {}).get("text", "")
            elif type_msg in ["audioMessage", "voiceMessage"]:
                download_url = (
                    msg_data.get("fileMessageData", {}).get("downloadUrl")
                    or msg_data.get("downloadUrl")
                    or body_json.get("downloadUrl")
                )
                mime_type = (
                    msg_data.get("fileMessageData", {}).get("mimeType")
                    or msg_data.get("mimeType")
                    or body_json.get("mimeType")
                    or "audio/ogg"
                )
                raw_audio_bytes = b""
                if download_url:
                    try:
                        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as http_client:
                            resp = await http_client.get(download_url)
                            if resp.status_code == 200:
                                raw_audio_bytes = resp.content
                            else:
                                print(f"[GREEN-API AUDIO DOWNLOAD WARN]: Status {resp.status_code} for URL {download_url}")
                    except Exception as e:
                        print(f"[GREEN-API AUDIO DOWNLOAD ERROR]: {e}")

                # Fallback: Call Green-API downloadFile endpoint if direct link failed
                if not raw_audio_bytes and message_id and settings.GREEN_API_HOST and settings.GREEN_API_INSTANCE_ID and settings.GREEN_API_TOKEN:
                    try:
                        api_url = f"{settings.GREEN_API_HOST}/waInstance{settings.GREEN_API_INSTANCE_ID}/downloadFile/{settings.GREEN_API_TOKEN}"
                        chat_id = sender_phone if ("@c.us" in sender_phone or "@g.us" in sender_phone) else f"{sender_phone}@c.us"
                        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as http_client:
                            res_api = await http_client.post(api_url, json={"chatId": chat_id, "idMessage": message_id})
                            if res_api.status_code == 200:
                                fresh_url = res_api.json().get("downloadUrl")
                                if fresh_url:
                                    resp2 = await http_client.get(fresh_url)
                                    if resp2.status_code == 200:
                                        raw_audio_bytes = resp2.content
                    except Exception as e:
                        print(f"[GREEN-API DOWNLOADFILE FALLBACK ERROR]: {e}")

                if raw_audio_bytes:
                    norm_bytes, detected_mime = AudioNormalizer.normalize_audio(
                        raw_audio_bytes,
                        input_format="ogg" if "ogg" in mime_type.lower() else "wav"
                    )
                    db_temp: Session = SessionLocal()
                    try:
                        prods = db_temp.query(Product).filter_by(vendor_id=vendor_id).all()
                        catalog_data = [
                            {"sku": p.sku, "name_mr": p.name_mr, "name_en": p.name_en, "aliases": p.aliases, "unit": p.unit}
                            for p in prods
                        ]
                    finally:
                        db_temp.close()

                    parsed_audio = GeminiService.transcribe_and_parse_audio(
                        audio_bytes=norm_bytes,
                        mime_type=detected_mime,
                        catalog=catalog_data
                    )
                    parsed_audio_payload = parsed_audio
                    transcription = (parsed_audio.get("transcription") or "").strip()
                    message_body = transcription if transcription else "ऑडिओ नोंद"
                    audio_transcription = transcription
                else:
                    message_body = "ऑडिओ नोंद"

            elif type_msg in ("videoMessage",):
                download_url = (
                    msg_data.get("fileMessageData", {}).get("downloadUrl")
                    or msg_data.get("downloadUrl")
                    or body_json.get("downloadUrl")
                )
                mime_type = (
                    msg_data.get("fileMessageData", {}).get("mimeType")
                    or msg_data.get("mimeType")
                    or body_json.get("mimeType")
                    or "video/mp4"
                )
                if sender_phone:
                    WhatsAppService.send_message(
                        to_phone=sender_phone,
                        message="🎥 *व्हिडिओ प्राप्त झाला! दुकान स्कॅन करत आहे...*"
                    )
                background_tasks.add_task(
                    background_process_video,
                    vendor_id=vendor_id,
                    message_id=message_id,
                    download_url=download_url,
                    mime_type=mime_type,
                    to_phone=sender_phone
                )
                return Response(content="EVENT_RECEIVED", status_code=200)

            elif type_msg in ("imageMessage",):
                # Customer Handwritten Yaadi Image Ingress (Specification 03)
                download_url = (
                    msg_data.get("fileMessageData", {}).get("downloadUrl")
                    or msg_data.get("downloadUrl")
                    or body_json.get("downloadUrl")
                )
                mime_type = (
                    msg_data.get("fileMessageData", {}).get("mimeType")
                    or msg_data.get("mimeType")
                    or body_json.get("mimeType")
                    or "image/jpeg"
                )
                raw_img_bytes = b""
                if download_url:
                    try:
                        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as http_client:
                            resp = await http_client.get(download_url)
                            if resp.status_code == 200:
                                raw_img_bytes = resp.content
                    except Exception as e:
                        print(f"[GREEN-API YAADI IMAGE DOWNLOAD ERROR]: {e}")

                if not raw_img_bytes and message_id and settings.GREEN_API_HOST and settings.GREEN_API_INSTANCE_ID and settings.GREEN_API_TOKEN:
                    try:
                        api_url = f"{settings.GREEN_API_HOST}/waInstance{settings.GREEN_API_INSTANCE_ID}/downloadFile/{settings.GREEN_API_TOKEN}"
                        chat_id = sender_phone if ("@c.us" in sender_phone or "@g.us" in sender_phone) else f"{sender_phone}@c.us"
                        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as http_client:
                            res_api = await http_client.post(api_url, json={"chatId": chat_id, "idMessage": message_id})
                            if res_api.status_code == 200:
                                fresh_url = res_api.json().get("downloadUrl")
                                if fresh_url:
                                    resp2 = await http_client.get(fresh_url)
                                    if resp2.status_code == 200:
                                        raw_img_bytes = resp2.content
                    except Exception as e:
                        print(f"[GREEN-API YAADI DOWNLOADFILE ERROR]: {e}")

                caption = (
                    msg_data.get("caption")
                    or msg_data.get("fileMessageData", {}).get("caption")
                    or body_json.get("caption")
                    or ""
                ).strip()

                if raw_img_bytes:
                    background_tasks.add_task(
                        background_process_customer_yaadi_image,
                        vendor_id=vendor_id,
                        customer_phone=sender_phone,
                        image_bytes=raw_img_bytes,
                        mime_type=mime_type,
                        caption=caption
                    )
                return Response(content="EVENT_RECEIVED", status_code=200)

        # B. Meta Cloud API Ingress
        elif "entry" in body_json:
            try:
                entry = body_json["entry"][0]["changes"][0]["value"]
                message = entry["messages"][0]
                sender_phone = message.get("from", "")
                message_id = message.get("id", "")
                if message.get("type") == "text":
                    message_body = message["text"]["body"]
                elif message.get("type") == "audio":
                    audio_info = message.get("audio", {})
                    audio_id = audio_info.get("id")
                    audio_mime = audio_info.get("mime_type", "audio/ogg")
                    raw_audio_bytes = b""
                    meta_token = os.getenv("META_ACCESS_TOKEN", "") or os.getenv("WHATSAPP_TOKEN", "")
                    if audio_id and meta_token:
                        try:
                            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as http_client:
                                media_meta_res = await http_client.get(
                                    f"https://graph.facebook.com/v21.0/{audio_id}",
                                    headers={"Authorization": f"Bearer {meta_token}"}
                                )
                                if media_meta_res.status_code == 200:
                                    media_url = media_meta_res.json().get("url")
                                    if media_url:
                                        media_res = await http_client.get(
                                            media_url,
                                            headers={"Authorization": f"Bearer {meta_token}"}
                                        )
                                        if media_res.status_code == 200:
                                            raw_audio_bytes = media_res.content
                        except Exception as e:
                            print(f"[META AUDIO DOWNLOAD ERROR]: {e}")

                    if raw_audio_bytes:
                        norm_bytes, detected_mime = AudioNormalizer.normalize_audio(
                            raw_audio_bytes,
                            input_format="ogg" if "ogg" in audio_mime.lower() else "wav"
                        )
                        db_temp: Session = SessionLocal()
                        try:
                            prods = db_temp.query(Product).filter_by(vendor_id=vendor_id).all()
                            catalog_data = [
                                {"sku": p.sku, "name_mr": p.name_mr, "name_en": p.name_en, "aliases": p.aliases, "unit": p.unit}
                                for p in prods
                            ]
                        finally:
                            db_temp.close()

                        parsed_audio = GeminiService.transcribe_and_parse_audio(
                            audio_bytes=norm_bytes,
                            mime_type=detected_mime,
                            catalog=catalog_data
                        )
                        parsed_audio_payload = parsed_audio
                        transcription = (parsed_audio.get("transcription") or "").strip()
                        message_body = transcription if transcription else "ऑडिओ नोंद"
                        audio_transcription = transcription
                    else:
                        message_body = "ऑडिओ नोंद"
            except (KeyError, IndexError, ValueError):
                return Response(status_code=200)

        if message_body:
            # Immediate Stock Query Check (Accessible to both Merchant and Customer)
            query_triggers = [
                "satha dakhva", "saatha dakhva", "satha dakva", "sata dakhva", "sata dakva",
                "satha dakhav", "sata dakhav", "satha sanga", "saatha sanga", "sata sanga",
                "satha kiti", "saatha kiti", "satha", "saatha", "sata",
                "stock dakhva", "stock dakva", "stock dakhwa", "stock dakwa",
                "stock sanga", "stock saanga", "stock kiti", "stock kiti ahe", "stock kitna hai",
                "stock check", "check stock", "view stock", "show stock", "stock summary", "stock list",
                "shilak kiti", "shillak kiti", "kiti shillak", "kiti shilak",
                "kiti ahe", "kitna hai", "shilak", "shillak", "dakhva", "dakva", "dakhav",
                "साठा दाखवा", "स्टॉक दाखवा", "साठा सांगा", "स्टॉक सांगा", "साठा किती", "स्टॉक किती",
                "साठा", "स्टॉक", "शिल्लक किती", "किती शिल्लक", "किती आहे", "शिल्लक आहे का", "आहे का",
                "यादी दाखवा", "माल दाखवा", "शिल्लक माल", "शिल्लक साठा",
                "stock batao", "stock dikhao", "kitna bacha hai", "kitna stock hai", "kya stock hai"
            ]
            msg_body_lower = message_body.lower().strip()
            if any(w in msg_body_lower for w in query_triggers) or msg_body_lower in ["stock", "stock?", "stock list", "satha", "saatha"]:
                background_tasks.add_task(
                    background_process_message,
                    vendor_id=vendor_id,
                    message_body=message_body,
                    message_id=message_id,
                    to_phone=sender_phone,
                    transcription=audio_transcription,
                    parsed_payload={"intent": "QUERY", "items": [], "vendor_note": "साठा तपासणी विनंती (Stock Query)"}
                )
                return Response(content="EVENT_RECEIVED", status_code=200)

            # Dual-Role Security Firewall (Specification 03)
            is_merchant = is_merchant_sender(sender_phone)
            if not is_merchant:
                # Customer Ingress Flow: Sandboxed rejection for admin commands
                if any(w in msg_body_lower for w in ["undo", "cancel", "चूक झाली", "रद्द करा", "मागे घ्या"]):
                    sandbox_msg = "🙏 *नमस्कार! बाबुराव किराणा स्टोअर्स* 🏪\nआपण ग्राहक सेवेशी जोडलेले आहात. केवळ अधिकृत दुकानदार व्यवहार रद्द करू शकतात."
                    WhatsAppService.send_message(to_phone=sender_phone, message=sandbox_msg)
                    return Response(content="EVENT_RECEIVED", status_code=200)

                # Process Customer Text Yaadi Order
                background_tasks.add_task(
                    background_process_customer_yaadi_text,
                    vendor_id=vendor_id,
                    customer_phone=sender_phone,
                    text_message=message_body
                )
                return Response(content="EVENT_RECEIVED", status_code=200)

            # Authorized Merchant Flow
            background_tasks.add_task(
                background_process_message,
                vendor_id=vendor_id,
                message_body=message_body,
                message_id=message_id,
                to_phone=sender_phone,
                transcription=audio_transcription,
                parsed_payload=parsed_audio_payload if "parsed_audio_payload" in locals() else None
            )
        return Response(content="EVENT_RECEIVED", status_code=200)

    return Response(content="EVENT_RECEIVED", status_code=200)
