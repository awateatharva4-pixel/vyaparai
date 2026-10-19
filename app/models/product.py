import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from app.core.database import Base

class Product(Base):
    """
    Inventory Item Model for Kirana & Local Retailers.
    Supports bilingual metadata, vernacular search aliases, and polymorphic attributes.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(String(50), default="DEMO_KIRANA_KOP", index=True)
    sku = Column(String(50), unique=True, index=True, nullable=False)
    name_mr = Column(String(100), nullable=False) # Marathi item name (e.g. साखर)
    name_en = Column(String(100), nullable=False) # English item name (e.g. Sugar)
    category = Column(String(100), index=True)
    stock = Column(Float, default=0.0, nullable=False)
    unit = Column(String(20), default="kg") # kg, packet, pouch, ladi, etc.
    unit_price = Column(Float, default=0.0) # Price in INR (Rs)
    min_threshold = Column(Float, default=5.0) # Low stock alert trigger level
    aliases_json = Column(Text, default="[]") # Vernacular phonetic aliases
    extra_meta_json = Column(Text, default="{}") # Dynamic polymorphic attributes (expiry, perishable)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def aliases(self):
        try:
            return json.loads(self.aliases_json or "[]")
        except Exception:
            return []

    @aliases.setter
    def aliases(self, value):
        if isinstance(value, str):
            try:
                val_obj = json.loads(value)
                if isinstance(val_obj, list):
                    value = val_obj
                else:
                    value = [value] if value else []
            except Exception:
                value = [value] if value else []
        elif not isinstance(value, list):
            value = [value] if value else []
        self.aliases_json = json.dumps(value, ensure_ascii=False)

    @property
    def extra_meta(self):
        try:
            return json.loads(self.extra_meta_json or "{}")
        except Exception:
            return {}

    @extra_meta.setter
    def extra_meta(self, value):
        self.extra_meta_json = json.dumps(value, ensure_ascii=False)

    @property
    def image_url(self):
        import os
        sku_clean = (self.sku or "").strip()
        static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "products"))
        # 1. Check exact SKU filename
        if os.path.exists(os.path.join(static_dir, f"{sku_clean}.jpg")):
            return f"/static/products/{sku_clean}.jpg"
        # 2. Check alias or slug
        slug_map = {
            "DAIRY-MILK-500ML": "amul_milk.jpg",
            "DAIRY-AMUL-500M": "amul_milk.jpg",
            "DAIRY-AMUL-500ML": "amul_milk.jpg",
            "GROC-SUG-001": "sugar.jpg",
            "FMCG-PARLE-100G": "parle_g.jpg",
            "OIL-FORT-1L": "fortune_oil.jpg",
            "BAK-PAV-LADI": "ladi_pav.jpg",
            "DAL-TUR-001": "tur_dal.jpg",
            "GROC-SALT-1K": "tata_salt.jpg",
            "GROC-ATTA-5K": "aashirvaad_atta.jpg",
            "FMCG-MAGGI-70G": "maggi.jpg",
            "VEG-KANDA-001": "red_onion.jpg",
            "VEG-BATATA-001": "potato.jpg",
            "AUTO-VID-NOTEBOOK": "classmate_notebook.jpg",
            "AUTO-VID-PEN": "reynolds_pen.jpg",
            "AUTO-VID-KINLEY": "kinley_water.jpg",
            "KINLEY": "kinley_water.jpg",
            "PEN": "reynolds_pen.jpg",
            "NOTEBOOK": "classmate_notebook.jpg",
            "AMUL": "amul_milk.jpg",
            "MILK": "amul_milk.jpg",
            "DAIRY": "amul_milk.jpg"
        }
        if sku_clean in slug_map and os.path.exists(os.path.join(static_dir, slug_map[sku_clean])):
            return f"/static/products/{slug_map[sku_clean]}"
        for k, v in slug_map.items():
            if k in sku_clean.upper() and os.path.exists(os.path.join(static_dir, v)):
                return f"/static/products/{v}"

        # Category-based heuristic fallback
        cat_lower = (self.category or "").lower()
        name_lower = ((self.name_en or "") + " " + (self.name_mr or "")).lower()
        if "dairy" in cat_lower or "milk" in name_lower or "दूध" in name_lower:
            return "/static/products/amul_milk.jpg"
        if "grain" in cat_lower or "sugar" in name_lower or "साखर" in name_lower:
            return "/static/products/sugar.jpg"
        if "oil" in cat_lower or "तेल" in name_lower:
            return "/static/products/fortune_oil.jpg"
        if "salt" in name_lower or "मीठ" in name_lower:
            return "/static/products/tata_salt.jpg"
        if "atta" in name_lower or "आटा" in name_lower:
            return "/static/products/aashirvaad_atta.jpg"

        # Safe neutral SVG placeholder - NEVER fall back to parle_g for non-biscuit items
        return "/static/products/placeholder.svg"

    def to_dict(self):
        return {
            "id": self.id,
            "vendor_id": self.vendor_id,
            "sku": self.sku,
            "name_mr": self.name_mr,
            "name_en": self.name_en,
            "category": self.category,
            "stock": round(self.stock, 2),
            "unit": self.unit,
            "unit_price": round(self.unit_price, 2),
            "min_threshold": self.min_threshold,
            "is_low_stock": self.stock <= self.min_threshold,
            "aliases": self.aliases,
            "extra_meta": self.extra_meta,
            "image_url": self.image_url,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else ""
        }

class IdempotencyRecord(Base):
    """
    Prevents duplicate webhook processing when WhatsApp / Meta retries deliveries.
    Guarantees at-most-once state execution.
    """
    __tablename__ = "idempotency_records"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(128), unique=True, index=True, nullable=False)
    vendor_id = Column(String(50), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
