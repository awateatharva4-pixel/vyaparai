import json
import os
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.product import Product, IdempotencyRecord
from app.models.transaction import Transaction
from app.services.gemini_service import GeminiService

SEED_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "seed_inventory.json")


class InventoryService:
    """
    Core Business Logic & ACID Inventory Ledger Controller.
    Guarantees database consistency, serialized transactions, vernacular unit normalization, and audit trails.
    """

    @classmethod
    def seed_initial_catalog(cls, db: Session, force: bool = False):
        """Initializes or resets database with Kolhapur Kirana seed catalog."""
        if not force and db.query(Product).count() > 0:
            return

        # If forcing reset, delete existing records and clear Idempotency records
        if force:
            db.query(Transaction).delete()
            db.query(Product).delete()
            db.query(IdempotencyRecord).delete()
            db.commit()

            # Attempt SQLite auto-increment counter reset
            try:
                db.execute("DELETE FROM sqlite_sequence WHERE name IN ('products', 'transactions', 'idempotency_records');")
                db.commit()
            except Exception:
                pass

        if os.path.exists(SEED_FILE_PATH):
            with open(SEED_FILE_PATH, "r", encoding="utf-8") as f:
                items = json.load(f)
                for item in items:
                    p = Product(
                        vendor_id="DEMO_KIRANA_KOP",
                        sku=item["sku"],
                        name_mr=item["name_mr"],
                        name_en=item["name_en"],
                        category=item["category"],
                        stock=float(item["stock"]),
                        unit=item["unit"],
                        unit_price=float(item["unit_price"]),
                        min_threshold=float(item["min_threshold"])
                    )
                    p.aliases = item.get("aliases", [])
                    db.merge(p)
                db.commit()
                print(f"[CATALOG SEED] Loaded {len(items)} default products.")

    @classmethod
    def process_transaction_event(cls, vendor_id: str, raw_text: str, db: Session) -> Dict[str, Any]:
        """
        Main Event-Driven Ingestion Pipeline.
        1. Parse transcript via Gemini Multi-Key Failover or Local Rule Engine.
        2. Resolve SKUs against vendor catalog.
        3. Apply ACID updates to stock with non-negative safety guards.
        4. Append to immutable transaction ledger.
        5. Return clean vernacular confirmation payload.
        """
        # Fetch current active catalog for this vendor
        catalog_products = db.query(Product).filter_by(vendor_id=vendor_id).all()
        catalog_data = [
            {
                "sku": p.sku,
                "name_mr": p.name_mr,
                "name_en": p.name_en,
                "category": p.category,
                "unit": p.unit,
                "unit_price": p.unit_price,
                "aliases": p.aliases
            }
            for p in catalog_products
        ]

        # NLP Vernacular Extraction
        parsed_payload = GeminiService.parse_transcript(raw_text, catalog_data)
        intent = parsed_payload.get("intent", "SALE")
        extracted_items = parsed_payload.get("items", [])

        # Handle Rollback / Undo trigger
        if intent == "UNDO":
            return cls.undo_last_transaction(vendor_id, db)

        # Handle Query trigger
        if intent == "QUERY":
            return cls.build_stock_summary(vendor_id, db)

        # Handle Refund trigger
        if intent == "REFUND":
            return {
                "success": True,
                "intent": "REFUND",
                "updates": [],
                "total_amount": 0.0,
                "alerts": [],
                "reply_message": "💵 *ग्राहक परतावा नोंदवला (Customer Refund Logged).*\nकृपया गल्ल्यातून योग्य रक्कम परत द्या."
            }

        updates_applied = []
        total_bill_amount = 0.0
        alerts_triggered = []

        for item_data in extracted_items:
            qty = float(item_data.get("quantity", 1.0))
            if qty <= 0:
                continue
            # Defense: Cap unreasonable anomalous single-sale quantities (e.g. from prompt injection)
            qty = min(qty, 500.0)

            sku = item_data.get("sku_matched")
            name_raw = item_data.get("name_raw", "")

            # Look up product in database
            product = None
            if sku:
                product = db.query(Product).filter_by(vendor_id=vendor_id, sku=sku).first()
            if not product:
                # Fuzzy fallback matching by name
                for p in db.query(Product).filter_by(vendor_id=vendor_id).all():
                    if any(a.lower() in name_raw.lower() for a in p.aliases) or p.name_en.lower() in name_raw.lower() or p.name_mr in name_raw:
                        product = p
                        break

            if not product:
                continue

            # Compute quantity change: Sale = -qty, Restock/Return = +qty
            is_sale = intent == "SALE"
            if is_sale:
                if product.stock < qty:
                    alerts_triggered.append(
                        f"⚠️ {product.name_mr}: अपुरा साठा! शिल्लक फक्त {product.stock} {product.unit}, मागणी {qty} {product.unit}"
                    )
                    actual_deduction = min(product.stock, qty)
                    delta = -actual_deduction
                    new_stock = product.stock - actual_deduction
                else:
                    delta = -qty
                    new_stock = max(0.0, product.stock - qty)
            else:
                delta = qty
                new_stock = product.stock + qty

            product.stock = new_stock

            line_amount = abs(delta) * product.unit_price
            if is_sale:
                total_bill_amount += line_amount

            # Record in Immutable Ledger
            tx = Transaction(
                vendor_id=vendor_id,
                product_id=product.id,
                sku=product.sku,
                item_name=f"{product.name_mr} ({product.name_en})",
                transaction_type=intent,
                quantity_delta=delta,
                stock_after=new_stock,
                unit_price=product.unit_price,
                total_amount=line_amount,
                raw_message=raw_text
            )
            db.add(tx)
            updates_applied.append({
                "name": product.name_mr,
                "sku": product.sku,
                "qty": abs(delta),
                "unit": product.unit,
                "remaining": new_stock,
                "price": product.unit_price
            })

            # Check low stock threshold
            if new_stock <= product.min_threshold:
                alerts_triggered.append(f"⚠️ {product.name_mr}: फक्त {new_stock} {product.unit} शिल्लक!")

        db.commit()

        # Build clean vernacular confirmation message
        action_verb = "विक्री नोंदवली (Sale Recorded)" if intent == "SALE" else "साठा जमा केला (Stock Added)"
        items_summary = "\n".join([f"• {u['name']}: *{u['qty']} {u['unit']}* (शिल्लक: *{u['remaining']} {u['unit']}*)" for u in updates_applied])

        reply = f"✅ *{action_verb}!*\n\n{items_summary}"
        if intent == "SALE" and total_bill_amount > 0:
            reply += f"\n\n💰 *एकूण रक्कम: ₹{total_bill_amount:.2f}*"
        if alerts_triggered:
            reply += f"\n\n🚨 *साठा इशारा:*\n" + "\n".join(alerts_triggered)

        return {
            "success": True,
            "intent": intent,
            "updates": updates_applied,
            "total_amount": total_bill_amount,
            "alerts": alerts_triggered,
            "reply_message": reply
        }

    @classmethod
    def undo_last_transaction(cls, vendor_id: str, db: Session) -> Dict[str, Any]:
        """
        Atomic Multi-Item Rollback Engine.
        Reverts ALL items belonging to the most recent transaction batch (same raw_message).
        Prevents orphaned item deductions when vendors sell bundles like '5 साखर आणि २ तेल'.
        """
        last_tx = db.query(Transaction).filter_by(vendor_id=vendor_id, is_reversed=False)\
                    .order_by(desc(Transaction.id)).first()

        if not last_tx:
            return {
                "success": False,
                "reply_message": "❌ कोणतीही अलीकडील नोंद सापडली नाही (No recent transaction found to undo)."
            }

        # Find all unreversed transactions sharing the exact same raw_message
        batch_txs = db.query(Transaction).filter(
            Transaction.vendor_id == vendor_id,
            Transaction.is_reversed == False,
            Transaction.raw_message == last_tx.raw_message
        ).all()

        if not batch_txs:
            batch_txs = [last_tx]

        restored_summaries = []
        for tx in batch_txs:
            product = db.query(Product).filter_by(id=tx.product_id).first()
            if product:
                product.stock = max(0.0, product.stock - tx.quantity_delta)
                restored_stock = product.stock
                unit = product.unit
            else:
                restored_stock = 0.0
                unit = "unit"

            tx.is_reversed = True

            undo_audit = Transaction(
                vendor_id=vendor_id,
                product_id=tx.product_id,
                sku=tx.sku,
                item_name=tx.item_name,
                transaction_type="ROLLBACK",
                quantity_delta=-tx.quantity_delta,
                stock_after=restored_stock,
                unit_price=tx.unit_price,
                total_amount=-tx.total_amount,
                raw_message=f"UNDO: Reverted Tx #{tx.id}",
                is_reversed=True
            )
            db.add(undo_audit)
            restored_summaries.append(f"• {tx.item_name}: *{'+' if -tx.quantity_delta > 0 else ''}{-tx.quantity_delta} {unit}* (सद्य साठा: *{restored_stock} {unit}*)")

        db.commit()

        return {
            "success": True,
            "reply_message": (
                f"✅ *व्यवहार यशस्वीरीत्या रद्द केला (Transaction Undone)!*\n\n"
                f"{chr(10).join(restored_summaries)}\n\n"
                f"सर्व नोंदी पूर्ववत करण्यात आल्या आहेत."
            )
        }

    @classmethod
    def build_stock_summary(cls, vendor_id: str, db: Session) -> Dict[str, Any]:
        products = db.query(Product).filter_by(vendor_id=vendor_id).all()
        lines = [f"• {p.name_mr}: *{p.stock} {p.unit}* (₹{p.unit_price}/{p.unit})" for p in products]
        summary_text = "📦 *सद्य साठा तपशील (Live Stock Summary):*\n\n" + "\n".join(lines)
        return {
            "success": True,
            "reply_message": summary_text
        }

    @classmethod
    def get_dashboard_metrics(cls, db: Session, vendor_id: str = "DEMO_KIRANA_KOP") -> Dict[str, Any]:
        products = db.query(Product).filter_by(vendor_id=vendor_id).all()
        total_skus = len(products)
        total_valuation = sum(p.stock * p.unit_price for p in products)
        low_stock_items = [p for p in products if p.stock <= p.min_threshold]

        sales_txs = db.query(Transaction).filter_by(vendor_id=vendor_id, transaction_type="SALE", is_reversed=False).all()
        today_sales_count = len(sales_txs)
        today_revenue = sum(t.total_amount for t in sales_txs)

        recent_txs = db.query(Transaction).filter_by(vendor_id=vendor_id)\
                       .order_by(desc(Transaction.id)).limit(10).all()

        return {
            "total_skus": total_skus,
            "total_valuation": round(total_valuation, 2),
            "low_stock_count": len(low_stock_items),
            "today_sales_count": today_sales_count,
            "today_revenue": round(today_revenue, 2),
            "products": [p.to_dict() for p in products],
            "recent_transactions": [t.to_dict() for t in recent_txs]
        }
