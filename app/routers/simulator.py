from fastapi import APIRouter, Request, Depends, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
from app.core.database import get_db
from app.services.inventory_service import InventoryService
from app.services.gemini_service import GeminiService
from app.services.audio_service import AudioNormalizer
from app.models.product import Product

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(tags=["Simulator"])

class SimulatorMessage(BaseModel):
    text: str
    vendor_id: str = "DEMO_KIRANA_KOP"

@router.get("/simulator", response_class=HTMLResponse)
@router.get("/test-console", response_class=HTMLResponse)
def render_simulator(request: Request, db: Session = Depends(get_db)):
    metrics = InventoryService.get_dashboard_metrics(db)
    return templates.TemplateResponse(request=request, name="simulator.html", context={"metrics": metrics})



@router.post("/api/simulator/send")
def process_simulator_message(payload: SimulatorMessage, db: Session = Depends(get_db)):
    """Directly triggers the NLP extraction and inventory mutation pipeline."""
    result = InventoryService.process_transaction_event(
        vendor_id=payload.vendor_id,
        raw_text=payload.text,
        db=db
    )
    metrics = InventoryService.get_dashboard_metrics(db)
    return {
        "reply": result.get("reply_message", "नोंद झाली."),
        "intent": result.get("intent", "UNKNOWN"),
        "metrics": metrics
    }


@router.post("/api/simulator/audio")
def process_simulator_audio(
    file: UploadFile = File(...),
    vendor_id: str = Form("DEMO_KIRANA_KOP"),
    db: Session = Depends(get_db)
):
    """
    Simulated WhatsApp Audio Note Processing Pipeline.
    Receives recorded voice note (Web Speech fallback or direct mic stream),
    normalizes audio format via AudioNormalizer, transcribes with Gemini 2.5 Flash,
    and executes inventory transaction event.
    """
    audio_bytes = file.file.read()
    if not audio_bytes:
        return {
            "reply": "⚠️ ऑडिओ फाइल रिकामी आहे. कृपया पुन्हा बोला.",
            "intent": "ERROR",
            "transcription": "",
            "metrics": InventoryService.get_dashboard_metrics(db)
        }

    # Extract extension & MIME type
    content_type = file.content_type or "audio/ogg"
    filename = file.filename or "audio.ogg"
    ext = "ogg"
    if "." in filename:
        ext = filename.rsplit(".", 1)[-1].lower()
    elif "webm" in content_type:
        ext = "webm"
    elif "wav" in content_type:
        ext = "wav"
    elif "mp3" in content_type:
        ext = "mp3"

    # 1. Normalize audio with bandpass filtering and loudness normalization
    norm_bytes, detected_mime = AudioNormalizer.normalize_audio(audio_bytes, input_format=ext)

    # 2. Get active catalog for vendor (release lock immediately to prevent blocking during Gemini call)
    catalog_products = db.query(Product).filter_by(vendor_id=vendor_id).all()
    catalog_data = [
        {
            "sku": p.sku,
            "name_mr": p.name_mr,
            "name_en": p.name_en,
            "category": p.category,
            "unit": p.unit,
            "unit_price": p.unit_price,
            "aliases": p.aliases
        }
        for p in catalog_products
    ]
    db.commit()

    # 3. Transcribe & parse with Gemini 2.5 Flash with failover rotation
    parsed_audio = GeminiService.transcribe_and_parse_audio(
        audio_bytes=norm_bytes,
        mime_type=detected_mime,
        catalog=catalog_data
    )
    transcription = (parsed_audio.get("transcription") or "").strip() or "ऑडिओ नोंद"

    # 4. Process transaction event through business logic
    result = InventoryService.process_transaction_event(
        vendor_id=vendor_id,
        raw_text=transcription,
        db=db,
        parsed_payload=parsed_audio
    )

    metrics = InventoryService.get_dashboard_metrics(db)
    raw_reply = result.get("reply_message", "नोंद झाली.")
    full_reply = f"🎙️ *ऑडिओ ऐकले:* \"{transcription}\"\n\n{raw_reply}"

    return {
        "reply": full_reply,
        "transcription": transcription,
        "intent": result.get("intent", parsed_audio.get("intent", "UNKNOWN")),
        "parsed_audio": parsed_audio,
        "metrics": metrics
    }


@router.post("/api/simulator/video")
async def process_simulator_video(
    file: UploadFile = File(...),
    vendor_id: str = Form("DEMO_KIRANA_KOP"),
    db: Session = Depends(get_db)
):
    """
    Simulated WhatsApp Video Onboarding Pipeline (Specification 02).
    Receives shop shelf sweep video (.mp4, .mov, .webm),
    invokes Gemini 2.5 Flash Multimodal Video Digitizer,
    inserts newly discovered products with vernacular Marathi aliases into database,
    synchronizes sequence, saves durable snapshot, broadcasts CATALOG_ONBOARDED,
    and returns formatted WhatsApp confirmation receipt.
    """
    video_bytes = await file.read()
    if not video_bytes:
        return {
            "success": False,
            "reply": "⚠️ व्हिडिओ फाइल रिकामी आहे. कृपया योग्य व्हिडिओ निवडा.",
            "count": 0,
            "products": [],
            "metrics": InventoryService.get_dashboard_metrics(db)
        }

    mime_type = file.content_type or "video/mp4"
    filename = file.filename or "video.mp4"
    if "." in filename:
        ext = filename.rsplit(".", 1)[-1].lower()
        if ext in ("mp4", "m4v"):
            mime_type = "video/mp4"
        elif ext in ("mov", "qt"):
            mime_type = "video/quicktime"
        elif ext in ("webm",):
            mime_type = "video/webm"

    result = InventoryService.ingest_catalog_from_video(
        video_bytes=video_bytes,
        mime_type=mime_type,
        vendor_id=vendor_id,
        db=db
    )

    metrics = InventoryService.get_dashboard_metrics(db)
    return {
        "success": result.get("success", True),
        "reply": result.get("reply_message", "🎉 दुकान डिजिटायझेशन यशस्वी!"),
        "confirmation_receipt": result.get("confirmation_receipt", ""),
        "count": result.get("count", len(result.get("products", []))),
        "products": result.get("products", []),
        "metrics": metrics
    }

