from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
from app.core.database import get_db
from app.services.inventory_service import InventoryService

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(tags=["Simulator"])

class SimulatorMessage(BaseModel):
    text: str
    vendor_id: str = "DEMO_KIRANA_KOP"

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
