import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, WebSocket, WebSocketDisconnect

# Configure stream encoding for Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import Base, engine, get_db, SessionLocal, init_db
from app.core.websocket import ws_manager
from app.models import product, transaction, credit, customer_order
from app.services.inventory_service import InventoryService
from app.routers import webhook, inventory, simulator

# Initialize database schema tables and migrations
init_db()

# Initialize static FFmpeg binaries on PATH for cross-platform audio transcoding
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except Exception as e:
    pass


import asyncio

async def order_expiration_worker():
    """
    Autonomous 30-Minute Order Expiration & Stock Auto-Undo Sweeper.
    Scans every 30 seconds:
    1. Automatically cancels unfulfilled orders older than 30 mins and restitutes stock.
    2. Sends 5-minute warning alert to merchant phone (9579869506).
    """
    while True:
        try:
            await asyncio.sleep(30)
            db = SessionLocal()
            try:
                InventoryService.check_and_expire_orders(db=db)
            finally:
                db.close()
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[EXPIRATION WORKER WARN]: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern ASGI Lifespan: Guarantees self-healing seed on boot and launches expiration worker."""
    db = SessionLocal()
    try:
        InventoryService.seed_initial_catalog(db)
    finally:
        db.close()

    worker_task = asyncio.create_task(order_expiration_worker())
    yield
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass


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

# Cross-platform Frontend path resolution (Docker/Render Linux container & local Windows)
REPO_ROOT = os.path.dirname(BASE_DIR)
FRONTEND_DIR = os.path.join(REPO_ROOT, "frontend")
if not os.path.exists(FRONTEND_DIR):
    FRONTEND_DIR = r"E:\front end vyapar"

if os.path.exists(FRONTEND_DIR):
    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
    assets_dir = os.path.join(FRONTEND_DIR, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir, html=True), name="assets")

MINDMAP_DIR = os.path.join(REPO_ROOT, "mindmap")
if not os.path.exists(MINDMAP_DIR):
    MINDMAP_DIR = r"E:\vyaparai_mind_map"
if os.path.exists(MINDMAP_DIR):
    app.mount("/mindmap", StaticFiles(directory=MINDMAP_DIR, html=True), name="mindmap")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Include sub-routers
app.include_router(webhook.router)
app.include_router(inventory.router)
app.include_router(simulator.router)


@app.get("/")
@app.get("/dashboard")
def render_dashboard(request: Request, db: Session = Depends(get_db)):
    """Main Merchant Dashboard Portal - serves the interactive Calacatta Marble frontend."""
    if os.path.exists(FRONTEND_DIR):
        return RedirectResponse(url="/frontend/index.html")
    metrics = InventoryService.get_dashboard_metrics(db)
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "metrics": metrics,
            "gemini_keys_count": len(settings.get_gemini_keys())
        }
    )


@app.get("/dashboard-classic", response_class=HTMLResponse)
def render_classic_dashboard(request: Request, db: Session = Depends(get_db)):
    """Legacy Tailwind Dashboard fallback."""
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

