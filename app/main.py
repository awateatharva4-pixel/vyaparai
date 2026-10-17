import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import Base, engine, get_db, SessionLocal, init_db
from app.core.websocket import ws_manager
from app.models import product, transaction, credit
from app.services.inventory_service import InventoryService
from app.routers import webhook, inventory, simulator

# Initialize database schema tables and migrations
init_db()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern ASGI Lifespan: Guarantees self-healing seed on boot."""
    db = SessionLocal()
    try:
        InventoryService.seed_initial_catalog(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Local Vendor Inventory Digitization via WhatsApp/SMS for Kolhapur Retailers",
    lifespan=lifespan
)

# Cross-Origin Resource Sharing (Standard OWASP configuration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global safe exception handler: Obscures internal paths in production
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"[SYSTEM ERROR]: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"status": "ERROR", "message": "An internal service error occurred. The audit team has been notified."}
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


@app.websocket("/ws/inventory")
async def websocket_inventory(websocket: WebSocket):
    """
    [Slide 1 & 3: Real-Time WebSocket Synchronization]
    Provides live reactive streaming of inventory valuation, stock counts, and transactions.
    """
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)

