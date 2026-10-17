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
from app.core.config import settings
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

            # Process transaction with pre-parsed audio payload if available
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
