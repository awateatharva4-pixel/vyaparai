from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from app.core.database import Base

class CustomerCredit(Base):
    """
    Customer Udhar (Credit) Ledger Model (Slide 5).
    Tracks customer receivables, due dates, and automated polite WhatsApp reminder status.
    """
    __tablename__ = "customer_credits"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(String(50), default="DEMO_KIRANA_KOP", index=True)
    customer_name = Column(String(100), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    amount_due = Column(Float, nullable=False, default=0.0)
    status = Column(String(20), default="PENDING", index=True)  # PENDING, PAID, PARTIAL
    due_date = Column(String(20), nullable=True)                 # e.g., "2026-10-20"
    notes = Column(Text, nullable=True)
    last_reminder_sent = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "vendor_id": self.vendor_id,
            "customer_name": self.customer_name,
            "customer_phone": self.customer_phone,
            "amount_due": round(self.amount_due, 2),
            "status": self.status,
            "due_date": self.due_date or "तात्काळ (Immediate)",
            "notes": self.notes or "",
            "last_reminder_sent": self.last_reminder_sent.strftime("%Y-%m-%d %H:%M:%S") if self.last_reminder_sent else None,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
        }
