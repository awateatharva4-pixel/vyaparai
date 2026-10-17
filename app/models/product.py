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
