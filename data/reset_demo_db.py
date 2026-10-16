"""
1-Click Fast Database Reset for HELLO WORLD 2026 Hackathon Finals.
Run this script to reset the database to clean Kolhapur Kirana seed values before judges arrive.
"""
import sys
import os

# Add root folder to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, Base, engine
from app.services.inventory_service import InventoryService

def main():
    print("[RESET] Recreating database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        InventoryService.seed_initial_catalog(db, force=True)
        print("[RESET] SUCCESS! Catalog restored to clean demo state (10 Kolhapur Kirana SKUs).")
    finally:
        db.close()

if __name__ == "__main__":
    main()
