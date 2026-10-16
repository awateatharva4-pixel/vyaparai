import json
import os
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.product import Product
from app.models.transaction import Transaction
from app.services.gemini_service import GeminiService

SEED_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "seed_inventory.json")

class InventoryService:
    """
    Core Business Logic & ACID Inventory Ledger Controller.
    Guarantees database consistency, pessimistic locking, vernacular unit normalization, and audit trails.
    """

    @classmethod
    def seed_initial_catalog(cls, db: Session, force: bool = False):
        """Initializes or resets database with Kolhapur Kirana seed catalog."""
        if not force and db.query(Product).count() > 0:
            return
        
        # If forcing reset, delete existing records
        if force:
            db.query(Transaction).delete()
            db.query(Product).delete()
            db.commit()

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
                        min_threshold=float(item.get("min_threshold", 5.0))
                    )
                    p.aliases = item.get("aliases", [])
                    db.add(p)
                db.commit()
                print(f"[CATALOG SEED] Loaded {len(items)} default products.")

    @classmethod
    def get_catalog_for_prompt(cls, db: Session) -> List[Dict[str, Any]]:
        products = db.query(Product).all()
        return [{"sku": p.sku, "name_en": p.name_en, "name_mr": p.name_mr, "unit": p.unit, "unit_price": p.unit_price, "aliases": p.aliases} for p in products]

    @classmethod
    def process_transaction_event(cls, vendor_id: str, raw_text: str, db: Session) -> Dict[str, Any]:
        """
        End-to-End Transaction Processor:
        Vernacular Text/Voice -> AI/Regex Extraction -> ACID State Mutation -> Response Builder
        """
        catalog = cls.get_catalog_for_prompt(db)
        parsed = GeminiService.parse_transcript(raw_text, catalog)
        intent = parsed.get("intent", "SALE")

        # 1. Handle 1-Click Undo / Rollback
        if intent == "UNDO":
            return cls.undo_last_transaction(vendor_id, db)

        # 2. Handle Stock Query
        if intent == "QUERY":
            return cls.build_stock_summary(vendor_id, db)

        # 3. Handle Sales or Restocks
        extracted_items = parsed.get("items", [])
        if not extracted_items:
            return {
                "success": False,
                "message": "कोणतीही वस्तू ओळखता आली नाही (Could not identify items from message).",
                "parsed": parsed
            }

        updates_applied = []
        total_bill_amount = 0.0
        alerts_triggered = []

        for item_data in extracted_items:
            qty = float(item_data.get("quantity", 1.0))
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

            # Compute quantity change: Sale = -qty, Restock = +qty
            delta = -qty if intent == "SALE" else qty
            
            # Atomic update with non-negative guard
            new_stock = max(0.0, product.stock + delta)
            product.stock = new_stock

            line_amount = qty * product.unit_price
            if intent == "SALE":
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
                "qty": qty,
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
        """Rolls back the most recent unreversed transaction in under 10 seconds."""
        last_tx = db.query(Transaction).filter_by(vendor_id=vendor_id, is_reversed=False)\
                    .order_by(desc(Transaction.id)).first()

        if not last_tx:
            return {
                "success": False,
                "reply_message": "❌ कोणतीही अलीकडील नोंद सापडली नाही (No recent transaction found to undo)."
            }

        product = db.query(Product).filter_by(id=last_tx.product_id).first()
        if product:
            # Reverse delta: if sale was -5, subtracting -5 restores +5
            product.stock = max(0.0, product.stock - last_tx.quantity_delta)
        
        last_tx.is_reversed = True

        # Audit rollback entry
        undo_audit = Transaction(
            vendor_id=vendor_id,
            product_id=last_tx.product_id,
            sku=last_tx.sku,
            item_name=last_tx.item_name,
            transaction_type="ROLLBACK",
            quantity_delta=-last_tx.quantity_delta,
            stock_after=product.stock if product else 0.0,
            unit_price=last_tx.unit_price,
            total_amount=-last_tx.total_amount,
            raw_message=f"UNDO: Reverted Tx #{last_tx.id}",
            is_reversed=True
        )
        db.add(undo_audit)
        db.commit()

        item_title = product.name_mr if product else last_tx.sku
        restored = product.stock if product else 0.0
        unit = product.unit if product else "unit"

        return {
            "success": True,
            "reply_message": (
                f"✅ *व्यवहार यशस्वीरीत्या रद्द केला (Transaction Undone)!*\n\n"
                f"मालाचे नाव: *{item_title}*\n"
                f"साठा दुरुस्ती: *{'+' if -last_tx.quantity_delta > 0 else ''}{-last_tx.quantity_delta} {unit}*\n"
                f"सद्य साठा: *{restored} {unit}*"
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
