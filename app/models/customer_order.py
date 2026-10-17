import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from app.core.database import Base


class CustomerOrder(Base):
    """
    Customer Remote Order / Handwritten Yaadi Model (Specification 03).
    Represents customer-initiated grocery orders sent via handwritten slip photo or WhatsApp text.
    Enforces the Zero Direct Ledger Modification Invariant: stock is only decremented when merchant packs.
    """
    __tablename__ = "customer_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(32), unique=True, index=True)  # e.g. "ORD-8402"
    vendor_id = Column(String(64), default="DEMO_KIRANA_KOP", index=True)
    customer_phone = Column(String(32), index=True)
    raw_message = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    items_json = Column(Text, nullable=False, default="[]")  # Serialized JSON of order items
    total_amount = Column(Float, default=0.0)
    status = Column(String(24), default="PENDING", index=True)  # PENDING, PACKED, CANCELLED
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        try:
            items_list = json.loads(self.items_json) if self.items_json else []
        except Exception:
            items_list = []
        return {
            "id": self.id,
            "order_id": self.order_id,
            "vendor_id": self.vendor_id,
            "customer_phone": self.customer_phone,
            "raw_message": self.raw_message or "",
            "image_url": self.image_url or "",
            "items": items_list,
            "total_amount": round(self.total_amount, 2),
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
        }
