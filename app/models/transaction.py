from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from app.core.database import Base

class Transaction(Base):
    """
    Event-Sourced Immutable Ledger.
    Every inventory change is recorded as a discrete event rather than an in-place destructive overwrite.
    Enables audit trails, GST valuation, and 1-click undo/rollback without data corruption.
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(64), index=True)
    vendor_id = Column(String(50), default="DEMO_KIRANA_KOP", index=True)
    product_id = Column(Integer, index=True)
    sku = Column(String(50), index=True)
    item_name = Column(String(100))
    transaction_type = Column(String(20), default="SALE")  # SALE, RESTOCK, ADJUSTMENT, ROLLBACK
    quantity_delta = Column(Float, nullable=False)        # Negative for sales, positive for restock
    stock_after = Column(Float, nullable=False)
    unit_price = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    raw_message = Column(Text)                            # Vernacular Marathi/Hindi original input
    is_reversed = Column(Boolean, default=False, index=True) # Set to True if undone
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "batch_id": self.batch_id,
            "vendor_id": self.vendor_id,
            "product_id": self.product_id,
            "sku": self.sku,
            "item_name": self.item_name,
            "type": self.transaction_type,
            "delta": self.quantity_delta,
            "stock_after": round(self.stock_after, 2),
            "unit_price": round(self.unit_price, 2),
            "amount": round(self.total_amount, 2),
            "raw_message": self.raw_message,
            "is_reversed": self.is_reversed,
            "created_at": self.created_at.isoformat() if self.created_at else "",
            "time": self.created_at.strftime("%H:%M:%S") if self.created_at else ""
        }
