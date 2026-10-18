import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
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
    status = Column(String(32), default="PENDING", index=True)  # PENDING, CONFIRMED, PACKED, CANCELLED, EXPIRED_AUTO_CANCELLED
    is_stock_reserved = Column(Boolean, default=True)  # Immediate stock reservation invariant
    confirmed_by_customer = Column(Boolean, default=False)  # Two-way confirmation loop flag
    reminder_sent = Column(Boolean, default=False)  # 25-min warning flag
    expires_at = Column(DateTime, nullable=True, index=True)  # 30-minute auto-rollback timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        try:
            items_list = json.loads(self.items_json) if self.items_json else []
        except Exception:
            items_list = []

        clean_p = str(self.customer_phone or "").replace("+", "").replace("@c.us", "").strip()
        if "7019259321" in clean_p:
            known_name = "व्यंकटेश पै (Venkatesh Pai)"
        elif "9822012345" in clean_p:
            known_name = "तानाजी शेठ"
        elif "9822067890" in clean_p:
            known_name = "आनंदराव"
        elif "9822054321" in clean_p:
            known_name = "बबनराव जाधव"
        elif "9579869506" in clean_p:
            known_name = "अथर्व आवाटे (Atharva Awate)"
        else:
            short_p = clean_p[-10:] if len(clean_p) >= 10 else clean_p
            known_name = f"ग्राहक (+{short_p})"

        return {
            "id": self.id,
            "order_id": self.order_id,
            "vendor_id": self.vendor_id,
            "customer_name": known_name,
            "customerName": known_name,
            "phone": self.customer_phone,
            "customer_phone": self.customer_phone,
            "rawText": self.raw_message or "",
            "raw_message": self.raw_message or "",
            "image_url": self.image_url or "",
            "items": items_list,
            "totalEstimated": round(self.total_amount, 2),
            "total_amount": round(self.total_amount, 2),
            "status": self.status,
            "is_stock_reserved": bool(self.is_stock_reserved),
            "confirmed_by_customer": bool(self.confirmed_by_customer),
            "expires_at": self.expires_at.strftime("%Y-%m-%d %H:%M:%S") if self.expires_at else "",
            "remaining_seconds": max(0, int((self.expires_at - datetime.utcnow()).total_seconds())) if (self.expires_at and self.status in ("PENDING", "CONFIRMED")) else 0,
            "timestamp": self.created_at.strftime("%I:%M %p") if self.created_at else "Just now",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
        }
