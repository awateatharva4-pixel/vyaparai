import os
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import Base, engine, get_db
from app.models import product, transaction
from app.services.inventory_service import InventoryService
from app.routers import webhook, inventory, simulator

# Initialize database schema tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Local Vendor Inventory Digitization via WhatsApp/SMS for Kolhapur Retailers"
)

# Cross-Origin Resource Sharing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Template and static paths
BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Include sub-routers
app.include_router(webhook.router)
app.include_router(inventory.router)
app.include_router(simulator.router)

@app.on_event("startup")
def on_startup():
    """Ensure initial demo catalog is seeded on boot."""
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        InventoryService.seed_initial_catalog(db)
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def render_dashboard(request: Request, db: Session = Depends(get_db)):
    """Main Merchant Dashboard Portal."""
    metrics = InventoryService.get_dashboard_metrics(db)
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "metrics": metrics,
            "gemini_keys_count": len(settings.get_gemini_keys())
        }
    )


@app.get("/health")
def health_check():
    return {
        "status": "HEALTHY",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "active_gemini_keys": len(settings.get_gemini_keys())
    }
