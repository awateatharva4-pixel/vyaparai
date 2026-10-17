import re
import json
import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import checkpoint_wal
from app.models.product import Product, IdempotencyRecord
from app.models.transaction import Transaction
from app.models.credit import CustomerCredit
from app.core.config import settings
from app.services.whatsapp_service import WhatsAppService
from app.core.websocket import ws_manager
from app.services.gemini_service import GeminiService

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
SEED_FILE_PATH = os.path.join(DATA_DIR, "seed_inventory.json")
STATE_FILE_PATH = os.path.join(DATA_DIR, "vyaparai_state.json")


class InventoryService:
    """
    Core Business Logic & ACID Inventory Ledger Controller.
    Guarantees database consistency, serialized transactions, vernacular unit normalization, and audit trails.
    """

    @classmethod
    def save_state_snapshot(cls, db: Session, vendor_id: str = "DEMO_KIRANA_KOP") -> str:
        """
        Durable State Snapshot Engine.
        Flushes all products, transactions, and metrics to data/vyaparai_state.json.
        Resilient against Render dyno sleep and ephemeral storage container wipes.
        """
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            products = db.query(Product).all()
            transactions = db.query(Transaction).order_by(Transaction.id).all()
            credits = db.query(CustomerCredit).order_by(CustomerCredit.id).all()

            low_stock_count = sum(1 for p in products if p.stock <= p.min_threshold)
            total_valuation = sum(p.stock * p.unit_price for p in products)

            # IST start of today
            ist_now = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
            start_of_today_ist = ist_now.replace(hour=0, minute=0, second=0, microsecond=0)
            start_of_today_utc = (start_of_today_ist - timedelta(hours=5, minutes=30)).replace(tzinfo=None)

            today_sales = [t for t in transactions if t.transaction_type == "SALE" and not t.is_reversed and t.created_at and t.created_at >= start_of_today_utc]
            today_revenue = sum(t.total_amount for t in today_sales)

            snapshot = {
                "version": "1.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "vendor_id": vendor_id,
                "metrics": {
                    "total_skus": len(products),
                    "total_valuation": round(total_valuation, 2),
                    "low_stock_count": low_stock_count,
                    "today_sales_count": len(today_sales),
                    "today_revenue": round(today_revenue, 2),
                    "udhar_count": sum(1 for c in credits if c.status == "PENDING"),
                    "udhar_total": round(sum(c.amount_due for c in credits if c.status == "PENDING"), 2)
                },
                "products": [p.to_dict() for p in products],
                "transactions": [t.to_dict() for t in transactions],
                "customer_credits": [c.to_dict() for c in credits]
            }

            temp_path = f"{STATE_FILE_PATH}.{uuid.uuid4().hex}.tmp"
            try:
                with open(temp_path, "w", encoding="utf-8") as f:
                    json.dump(snapshot, f, ensure_ascii=False, indent=2)
                os.replace(temp_path, STATE_FILE_PATH)
            finally:
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except OSError:
                        pass
            checkpoint_wal(truncate=True)
            return STATE_FILE_PATH
        except Exception as e:
            print(f"[STATE SNAPSHOT ERROR]: {e}")
            return STATE_FILE_PATH

    @classmethod
    def restore_state_from_snapshot(cls, db: Session, snapshot_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Rehydrates products, transactions, and udhar ledger from state snapshot JSON.
        """
        if snapshot_data is None:
            if not os.path.exists(STATE_FILE_PATH):
                return {"restored": False, "reason": "Snapshot file does not exist"}
            try:
                with open(STATE_FILE_PATH, "r", encoding="utf-8") as f:
                    snapshot_data = json.load(f)
            except Exception as e:
                return {"restored": False, "reason": f"Corrupt snapshot: {e}"}

        if "snapshot" in snapshot_data and isinstance(snapshot_data["snapshot"], dict):
            snapshot_data = snapshot_data["snapshot"]

        products_data = snapshot_data.get("products", [])
        transactions_data = snapshot_data.get("transactions", [])
        credits_data = snapshot_data.get("customer_credits", [])

        if not products_data:
            return {"restored": False, "reason": "No products found in snapshot"}

        restored_products = 0
        for item in products_data:
            sku = item.get("sku")
            if not sku:
                continue
            p = db.query(Product).filter_by(sku=sku).first()
            if not p:
                p = Product(
                    vendor_id=item.get("vendor_id", "DEMO_KIRANA_KOP"),
                    sku=sku,
                    name_mr=item.get("name_mr", ""),
                    name_en=item.get("name_en", ""),
                    category=item.get("category", "Grains & Essentials / किराणा माल"),
                    stock=float(item.get("stock", 0.0)),
                    unit=item.get("unit", "kg"),
                    unit_price=float(item.get("unit_price", 0.0)),
                    min_threshold=float(item.get("min_threshold", 5.0))
                )
                db.add(p)
            else:
                p.name_mr = item.get("name_mr", p.name_mr)
                p.name_en = item.get("name_en", p.name_en)
                p.category = item.get("category", p.category)
                p.stock = float(item.get("stock", p.stock))
                p.unit = item.get("unit", p.unit)
                p.unit_price = float(item.get("unit_price", p.unit_price))
                p.min_threshold = float(item.get("min_threshold", p.min_threshold))

            if "aliases" in item:
                p.aliases = item["aliases"]
            if "extra_meta" in item:
                p.extra_meta = item["extra_meta"]
            restored_products += 1

        db.flush()

        restored_transactions = 0
        existing_tx_ids = set(r[0] for r in db.query(Transaction.id).all())
        for tx_data in transactions_data:
            tx_id = tx_data.get("id")
            if tx_id and tx_id in existing_tx_ids:
                continue

            created_at = None
            if tx_data.get("created_at"):
                try:
                    created_at = datetime.fromisoformat(tx_data["created_at"])
                except Exception:
                    created_at = None

            product = db.query(Product).filter_by(sku=tx_data.get("sku")).first()
            tx = Transaction(
                id=tx_id,
                batch_id=tx_data.get("batch_id"),
                vendor_id=tx_data.get("vendor_id", "DEMO_KIRANA_KOP"),
                product_id=product.id if product else tx_data.get("product_id"),
                sku=tx_data.get("sku"),
                item_name=tx_data.get("item_name"),
                transaction_type=tx_data.get("type", tx_data.get("transaction_type", "SALE")),
                quantity_delta=float(tx_data.get("delta", tx_data.get("quantity_delta", 0.0))),
                stock_after=float(tx_data.get("stock_after", 0.0)),
                unit_price=float(tx_data.get("unit_price", 0.0)),
                total_amount=float(tx_data.get("amount", tx_data.get("total_amount", 0.0))),
                raw_message=tx_data.get("raw_message", ""),
                is_reversed=bool(tx_data.get("is_reversed", False)),
                created_at=created_at or datetime.utcnow()
            )
            db.merge(tx)
            restored_transactions += 1

        if credits_data:
            existing_credit_ids = set(r[0] for r in db.query(CustomerCredit.id).all())
            for c_data in credits_data:
                cid = c_data.get("id")
                if cid and cid in existing_credit_ids:
                    continue
                cred = CustomerCredit(
                    id=cid,
                    vendor_id=c_data.get("vendor_id", "DEMO_KIRANA_KOP"),
                    customer_name=c_data.get("customer_name", ""),
                    customer_phone=c_data.get("customer_phone", ""),
                    amount_due=float(c_data.get("amount_due", 0.0)),
                    status=c_data.get("status", "PENDING"),
                    due_date=c_data.get("due_date", ""),
                    notes=c_data.get("notes", "")
                )
                db.merge(cred)

        db.commit()
        checkpoint_wal(truncate=True)
        return {
            "restored": True,
            "products_count": restored_products,
            "transactions_count": restored_transactions
        }

    @classmethod
    def seed_initial_catalog(cls, db: Session, force: bool = False):
        """Initializes or resets database with Kolhapur Kirana seed catalog."""
        if not force and db.query(Product).count() > 0:
            cls.seed_initial_udhar(db, force=False)
            return

        # If forcing reset, delete existing records and clear Idempotency records
        if force:
            db.query(Transaction).delete()
            db.query(Product).delete()
            db.query(IdempotencyRecord).delete()
            db.query(CustomerCredit).delete()
            db.commit()

            # Attempt SQLite auto-increment counter reset
            try:
                db.execute("DELETE FROM sqlite_sequence WHERE name IN ('products', 'transactions', 'idempotency_records', 'customer_credits');")
                db.commit()
            except Exception:
                pass

        # Case 1: Fresh / empty database on restart (Render dyno reboot)
        if not force and os.path.exists(STATE_FILE_PATH):
            res = cls.restore_state_from_snapshot(db)
            if res.get("restored") and db.query(Product).count() > 0:
                print(f"[CATALOG SEED] Auto-restored {res.get('products_count')} products and {res.get('transactions_count')} transactions from state snapshot.")
                cls.seed_initial_udhar(db, force=False)
                return

        # Case 2: No snapshot or forced reset -> Load default seed catalog
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

        cls.seed_initial_udhar(db, force=force)
        cls.save_state_snapshot(db)

    @classmethod
    def process_transaction_event(
        cls,
        vendor_id: str,
        raw_text: str,
        db: Session,
        parsed_payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main Event-Driven Ingestion Pipeline.
        1. Parse transcript via Gemini Multi-Key Failover or Local Rule Engine (or pre-parsed audio).
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

        # Guard 1: Detect unparseable voice note placeholder or STT noise
        AUDIO_PLACEHOLDERS = [
            "ऑडिओ नोंद",
            "ऑडिओ नोंद (voice note received)",
            "voice note received",
            "audio message",
            "[silence]",
            "[अस्पष्ट]",
            "[noise]",
            "(inaudible)",
            "..."
        ]
        if raw_text.strip().lower() in [p.lower() for p in AUDIO_PLACEHOLDERS] or re.match(r"^\[.*\]$", raw_text.strip()):
            return {
                "success": False,
                "intent": "UNCLEAR_AUDIO",
                "updates": [],
                "total_amount": 0.0,
                "alerts": [],
                "reply_message": "🎙️ *ऑडिओ स्पष्ट ऐकू आला नाही.*\nकृपया पुन्हा स्पष्ट बोला किंवा लिहून पाठवा (उदा. *'२ लिटर तेल आणि ५ साखर'*)."
            }

        # NLP Vernacular Extraction (use pre-parsed payload if valid, otherwise parse transcript)
        if not parsed_payload or (not parsed_payload.get("items") and parsed_payload.get("intent") not in ("UNDO", "QUERY", "REFUND")):
            parsed_payload = GeminiService.parse_transcript(raw_text, catalog_data)
        intent = parsed_payload.get("intent", "SALE")
        extracted_items = parsed_payload.get("items", [])

        # GENERAL RETAIL INVARIANT (Product-Agnostic):
        # In retail inventory management, any utterance stating items and quantities defaults to SALE.
        # Only classify as RESTOCK if explicit inventory intake/supplier keywords are present.
        if intent == "RESTOCK":
            restock_triggers = [
                "आले", "आणले", "भरले", "जमा", "खरेदी", "stock aala", "stock आला",
                "restock", "purchase", "supplier", "नवा माल", "नवीन माल", "inward"
            ]
            raw_lower = raw_text.lower()
            if not any(w in raw_lower for w in restock_triggers):
                print(f"[INTENT RECTIFIED]: Overrode false RESTOCK to SALE for retail phrase: '{raw_text}'")
                intent = "SALE"

        # GENERAL RETAIL INVARIANT FOR QUERY:
        # Check if this is an explicit stock inquiry (either full catalog or specific SKU).
        if intent == "QUERY":
            query_triggers = [
                "साठा दाखवा", "स्टॉक दाखवा", "शिल्लक किती", "किती शिल्लक", "किती आहे",
                "आहे का", "शिल्लक आहे का", "साठा किती", "यादी दाखवा", "stock summary",
                "kiti ahe", "kitna hai", "check stock", "stock check", "show stock", "view stock"
            ]
            raw_lower = raw_text.lower()
            has_explicit_query = any(w in raw_lower for w in query_triggers)

            if has_explicit_query:
                # Check for single-item stock query (e.g. "तेल किती शिल्लक आहे?", "साखर किती आहे?")
                target_sku = None
                if extracted_items and extracted_items[0].get("sku_matched"):
                    target_sku = extracted_items[0].get("sku_matched")
                else:
                    check_parsed = GeminiService._local_regex_parser(raw_text, catalog_data)
                    if check_parsed.get("items") and check_parsed["items"][0].get("sku_matched"):
                        target_sku = check_parsed["items"][0].get("sku_matched")

                if target_sku:
                    p = db.query(Product).filter_by(vendor_id=vendor_id, sku=target_sku).first()
                    if p:
                        status_emoji = "🚨" if p.stock <= p.min_threshold else "📦"
                        return {
                            "success": True,
                            "intent": "QUERY",
                            "updates": [],
                            "total_amount": 0.0,
                            "alerts": [],
                            "reply_message": (
                                f"{status_emoji} *{p.name_mr}:*\n"
                                f"• सद्य शिल्लक: *{p.stock} {p.unit}*\n"
                                f"• किमान साठा मर्यादा: {p.min_threshold} {p.unit}\n"
                                f"• विक्री दर: ₹{p.unit_price:.2f}/{p.unit}"
                            )
                        }
                return cls.build_stock_summary(vendor_id, db)

            else:
                # No explicit query phrase. If numbers or items are present, override to SALE
                if extracted_items or re.search(r"\d", raw_text):
                    print(f"[INTENT RECTIFIED]: Overrode false QUERY to SALE for retail phrase: '{raw_text}'")
                    intent = "SALE"
                    if not extracted_items:
                        fallback_parsed = GeminiService._local_regex_parser(raw_text, catalog_data)
                        extracted_items = fallback_parsed.get("items", [])
                else:
                    # Pure conversational greeting or general text
                    return {
                        "success": False,
                        "intent": "GREETING",
                        "updates": [],
                        "total_amount": 0.0,
                        "alerts": [],
                        "reply_message": "🙏 *नमस्कार! VyaparAI मध्ये आपले स्वागत आहे.*\n\nविक्री नोंदवण्यासाठी वस्तू व प्रमाण सांगा (उदा. *'२ लिटर तेल'* किंवा *'५ किलो साखर'*).\nसद्य साठा पाहण्यासाठी *'साठा दाखवा'* असा मेसेज करा."
                    }

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
        event_batch_id = f"batch_{uuid.uuid4().hex[:12]}"

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

            # Zero-Delta Invariant: If stock is 0 and deduction is 0, do not create a zero-delta transaction row
            if is_sale and abs(delta) < 1e-6:
                continue

            product.stock = new_stock

            line_amount = abs(delta) * product.unit_price
            if is_sale:
                total_bill_amount += line_amount

            # Record in Immutable Ledger with Batch ID
            tx = Transaction(
                batch_id=event_batch_id,
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

        # Broadcast live update to connected WebSocket dashboards
        try:
            m = cls.get_dashboard_metrics(db, vendor_id=vendor_id)
            ws_manager.broadcast_sync({
                "type": "METRICS_UPDATE",
                "vendor_id": vendor_id,
                "metrics": m
            })
        except Exception as e:
            print(f"[WS BROADCAST WARN]: {e}")

        # Durable State Snapshot Persistence
        cls.save_state_snapshot(db, vendor_id=vendor_id)

        # Build clean vernacular confirmation message
        if not updates_applied:
            if parsed_payload and (str(parsed_payload.get("source", "")).startswith("gemini-audio") or "ऑडिओ" in raw_text):
                reply = "🎙️ *ऑडिओ स्पष्ट समजला नाही.*\nकृपया पुन्हा स्पष्ट बोला (उदा. *'२ लिटर तेल आणि ५ साखर'*)."
            else:
                reply = "⚠️ *कोणतीही नोंद झाली नाही (No Transaction Recorded)!*"
                if alerts_triggered:
                    reply += "\n\n🚨 *साठा इशारा:*\n" + "\n".join(alerts_triggered)
                else:
                    reply += "\nमागणी केलेला माल साठ्यात उपलब्ध नाही."
        else:
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

        # Batch ID Rollback Invariant:
        # Filter by batch_id if available to avoid accidentally wiping transactions with identical raw_message from earlier orders
        if last_tx.batch_id:
            batch_txs = db.query(Transaction).filter(
                Transaction.vendor_id == vendor_id,
                Transaction.is_reversed == False,
                Transaction.batch_id == last_tx.batch_id
            ).all()
        else:
            batch_txs = db.query(Transaction).filter(
                Transaction.vendor_id == vendor_id,
                Transaction.is_reversed == False,
                Transaction.raw_message == last_tx.raw_message
            ).all()

        if not batch_txs:
            batch_txs = [last_tx]

        undo_batch_id = f"undo_{last_tx.batch_id or uuid.uuid4().hex[:12]}"
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
                batch_id=undo_batch_id,
                vendor_id=vendor_id,
                product_id=tx.product_id,
                sku=tx.sku,
                item_name=tx.item_name,
                transaction_type="ROLLBACK",
                quantity_delta=-tx.quantity_delta,
                stock_after=restored_stock,
                unit_price=tx.unit_price,
                total_amount=-tx.total_amount,
                raw_message=f"UNDO: Reverted Tx #{tx.id} (Batch {tx.batch_id or 'N/A'})",
                is_reversed=True
            )
            db.add(undo_audit)
            restored_summaries.append(f"• {tx.item_name}: *{'+' if -tx.quantity_delta > 0 else ''}{-tx.quantity_delta} {unit}* (सद्य साठा: *{restored_stock} {unit}*)")

        db.commit()

        # Durable State Snapshot Persistence
        cls.save_state_snapshot(db, vendor_id=vendor_id)

        try:
            m = cls.get_dashboard_metrics(db, vendor_id=vendor_id)
            ws_manager.broadcast_sync({
                "type": "METRICS_UPDATE",
                "vendor_id": vendor_id,
                "metrics": m
            })
        except Exception:
            pass

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
        cls.seed_initial_udhar(db, force=False)
        products = db.query(Product).filter_by(vendor_id=vendor_id).all()
        total_skus = len(products)
        total_valuation = sum(p.stock * p.unit_price for p in products)
        low_stock_items = [p for p in products if p.stock <= p.min_threshold]

        # Today's Sales Filter Invariant: Restrict to current day in IST (UTC+5:30)
        ist_now = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
        start_of_today_ist = ist_now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_today_utc = (start_of_today_ist - timedelta(hours=5, minutes=30)).replace(tzinfo=None)

        sales_txs = db.query(Transaction).filter(
            Transaction.vendor_id == vendor_id,
            Transaction.transaction_type == "SALE",
            Transaction.is_reversed == False,
            Transaction.created_at >= start_of_today_utc
        ).all()
        today_sales_count = len(sales_txs)
        today_revenue = sum(t.total_amount for t in sales_txs)

        recent_txs = db.query(Transaction).filter_by(vendor_id=vendor_id)\
                       .order_by(desc(Transaction.id)).limit(10).all()

        credits = db.query(CustomerCredit).filter_by(vendor_id=vendor_id).order_by(desc(CustomerCredit.id)).all()
        pending_credits = [c for c in credits if c.status == "PENDING"]
        udhar_total = sum(c.amount_due for c in pending_credits)

        return {
            "total_skus": total_skus,
            "total_valuation": round(total_valuation, 2),
            "low_stock_count": len(low_stock_items),
            "today_sales_count": today_sales_count,
            "today_revenue": round(today_revenue, 2),
            "udhar_count": len(pending_credits),
            "udhar_total": round(udhar_total, 2),
            "udhar_ledger": [c.to_dict() for c in credits],
            "products": [p.to_dict() for p in products],
            "recent_transactions": [t.to_dict() for t in recent_txs]
        }

    @classmethod
    def seed_initial_udhar(cls, db: Session, force: bool = False):
        """Initializes Kolhapur Kirana customer credit ledger (Slide 5)."""
        if not force and db.query(CustomerCredit).count() > 0:
            return

        if force:
            db.query(CustomerCredit).delete()
            db.commit()

        sample_credits = [
            CustomerCredit(
                vendor_id="DEMO_KIRANA_KOP",
                customer_name="तानाजी शेठ",
                customer_phone="+919822012345",
                amount_due=450.0,
                status="PENDING",
                due_date="2026-10-18",
                notes="गहू व साखर बिल (Wheat & Sugar)"
            ),
            CustomerCredit(
                vendor_id="DEMO_KIRANA_KOP",
                customer_name="आनंदराव",
                customer_phone="+919822067890",
                amount_due=280.0,
                status="PENDING",
                due_date="2026-10-19",
                notes="शेंगदाणा तेल व साबण (Oil & Soap)"
            ),
            CustomerCredit(
                vendor_id="DEMO_KIRANA_KOP",
                customer_name="बबनराव जाधव",
                customer_phone="+919822054321",
                amount_due=720.0,
                status="PENDING",
                due_date="2026-10-17",
                notes="महिनाअखेर किराणा सामान (Monthly Ration)"
            ),
        ]
        for c in sample_credits:
            db.add(c)
        db.commit()
        print(f"[UDHAR SEED] Initialized {len(sample_credits)} customer credit accounts.")

    @classmethod
    def get_udhar_ledger(cls, db: Session, vendor_id: str = "DEMO_KIRANA_KOP") -> List[Dict[str, Any]]:
        """Retrieves active customer credit ledger records (Slide 5)."""
        cls.seed_initial_udhar(db, force=False)
        credits = db.query(CustomerCredit).filter_by(vendor_id=vendor_id).order_by(desc(CustomerCredit.id)).all()
        return [c.to_dict() for c in credits]

    @classmethod
    def generate_udhar_reminder(cls, credit_id: int, db: Session, send_whatsapp: bool = True) -> Dict[str, Any]:
        """
        Dispatches polite vernacular WhatsApp credit payment reminder (Slide 5).
        Template:
        "🙏 नमस्कार [नाव] शेठ! आपल्या बाबुराव किराणा स्टोअर्समधील ₹[रक्कम] चे उधारी बिल प्रलंबित आहे. कृपया सवडीने Google Pay किंवा रोख भरणा करावा ही नम्र विनंती. - बाबुराव किराणा स्टोअर्स 🏪"
        """
        cls.seed_initial_udhar(db, force=False)
        credit = db.query(CustomerCredit).filter_by(id=credit_id).first()
        if not credit:
            return {"success": False, "message": f"Credit account #{credit_id} not found."}

        clean_name = credit.customer_name.replace(" शेठ", "").replace("शेठ", "").strip()
        recipient_salutation = f"{clean_name} शेठ"

        msg = (
            f"🙏 नमस्कार {recipient_salutation}! आपल्या बाबुराव किराणा स्टोअर्समधील ₹{credit.amount_due:.0f} "
            f"चे उधारी बिल प्रलंबित आहे. कृपया सवडीने Google Pay किंवा रोख भरणा करावा ही नम्र विनंती. "
            f"- बाबुराव किराणा स्टोअर्स 🏪"
        )

        sent = False
        if send_whatsapp:
            sent = WhatsAppService.send_message(credit.customer_phone, msg)

        credit.last_reminder_sent = datetime.utcnow()
        db.commit()

        return {
            "success": True,
            "credit_id": credit.id,
            "customer_name": credit.customer_name,
            "customer_phone": credit.customer_phone,
            "amount_due": credit.amount_due,
            "whatsapp_sent": sent,
            "reminder_message": msg
        }

    @classmethod
    def generate_8pm_closing_summary(cls, vendor_id: str, db: Session, send_whatsapp: bool = True, phone: Optional[str] = None) -> Dict[str, Any]:
        """
        Automated 8:00 PM Daily Ledger Closing & Supplier Reorder Alerts (Slide 2 & 5).
        Tallies today's revenue, transactions count, top sellers, and flags critical stockouts
        with automated supplier reorder quantities.
        """
        products = db.query(Product).filter_by(vendor_id=vendor_id).all()

        # Today's Sales Filter Invariant: Restrict to current day in IST (UTC+5:30)
        ist_now = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
        start_of_today_ist = ist_now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_today_utc = (start_of_today_ist - timedelta(hours=5, minutes=30)).replace(tzinfo=None)

        sales_txs = db.query(Transaction).filter(
            Transaction.vendor_id == vendor_id,
            Transaction.transaction_type == "SALE",
            Transaction.is_reversed == False,
            Transaction.created_at >= start_of_today_utc
        ).all()

        today_sales_count = len(sales_txs)
        today_revenue = sum(t.total_amount for t in sales_txs)

        # Top selling items
        sales_by_item = {}
        for t in sales_txs:
            key = t.item_name or t.sku
            sales_by_item[key] = sales_by_item.get(key, 0.0) + abs(t.quantity_delta)

        sorted_top = sorted(sales_by_item.items(), key=lambda x: x[1], reverse=True)[:3]
        top_selling_items = [{"item": k, "quantity": round(v, 1)} for k, v in sorted_top]

        # Low-stock items with recommended reorder quantities
        low_stock_items = []
        reorder_lines = []
        for p in products:
            if p.stock <= p.min_threshold:
                # Dynamic reorder formula
                reorder_qty = max(round(p.min_threshold * 5 - p.stock, 1), round(p.min_threshold * 4, 1))
                if p.unit == "kg" and reorder_qty < 10:
                    reorder_qty = 25.0
                elif p.unit in ("packet", "pouch", "ladi") and reorder_qty < 10:
                    reorder_qty = 20.0

                item_info = {
                    "sku": p.sku,
                    "name_mr": p.name_mr,
                    "name_en": p.name_en,
                    "current_stock": round(p.stock, 2),
                    "min_threshold": p.min_threshold,
                    "unit": p.unit,
                    "recommended_reorder": reorder_qty
                }
                low_stock_items.append(item_info)
                reorder_lines.append(
                    f"• {p.name_mr}: {p.stock} {p.unit} शिल्लक (किमान: {p.min_threshold} {p.unit}) ➔ पुनर्नोंद: {reorder_qty} {p.unit}"
                )

        reorder_text = "\n".join(reorder_lines) if reorder_lines else "• सर्व साठा समाधानकारक आहे (All stock healthy)."
        top_lines = "\n".join([f"• {item['item']}: {item['quantity']} युनिट्स" for item in top_selling_items]) if top_selling_items else "• आज कोणताही व्यवहार नाही"

        message = (
            f"📊 *दैनिक व्यापार अहवाल (Daily Closing Ledger) - 8:00 PM*\n"
            f"🏪 *दुकान:* बाबुराव किराणा स्टोअर्स, कोल्हापूर\n"
            f"💰 *आजची एकूण विक्री:* ₹{today_revenue:.2f}\n"
            f"🧾 *एकूण व्यवहार:* {today_sales_count}\n\n"
            f"🏆 *सर्वाधिक खपाच्या वस्तू (Top Selling Items):*\n"
            f"{top_lines}\n\n"
            f"🚨 *कमी साठा व पुनर्नोंद शिफारस (Reorder Alerts):*\n"
            f"{reorder_text}\n\n"
            f"💡 _VyaparAI स्वयंचलित 8:00 PM अहवाल • 100% हिशोब स्पष्टता_"
        )

        whatsapp_sent = False
        if send_whatsapp:
            target_phone = phone or settings.MERCHANT_WHATSAPP_NUMBER
            if target_phone and "14155238886" not in target_phone:
                whatsapp_sent = WhatsAppService.send_message(target_phone, message)
            else:
                print(f"[DAILY CLOSING]: WhatsApp dispatch skipped - no valid merchant phone number configured (avoided default sandbox sender number)")

        return {
            "status": "SUCCESS",
            "vendor_id": vendor_id,
            "closing_time": "08:00 PM",
            "today_sales_count": today_sales_count,
            "today_revenue": round(today_revenue, 2),
            "top_selling_items": top_selling_items,
            "low_stock_items": low_stock_items,
            "reorder_alerts": low_stock_items,
            "whatsapp_sent": whatsapp_sent,
            "formatted_message": message
        }
