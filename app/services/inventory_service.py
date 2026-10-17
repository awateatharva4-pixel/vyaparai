import re
import json
import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import checkpoint_wal, is_sqlite
from app.models.product import Product, IdempotencyRecord
from app.models.transaction import Transaction
from app.models.credit import CustomerCredit
from app.models.customer_order import CustomerOrder
from app.core.config import settings
from app.services.whatsapp_service import WhatsAppService
from app.core.websocket import ws_manager
from app.services.gemini_service import GeminiService
from app.services.loose_commodity_service import LooseCommodityEngine

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
            orders = db.query(CustomerOrder).order_by(CustomerOrder.id).all()

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
                    "udhar_total": round(sum(c.amount_due for c in credits if c.status == "PENDING"), 2),
                    "pending_orders_count": sum(1 for o in orders if o.status == "PENDING")
                },
                "products": [p.to_dict() for p in products],
                "transactions": [t.to_dict() for t in transactions],
                "customer_credits": [c.to_dict() for c in credits],
                "customer_orders": [o.to_dict() for o in orders]
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
                db.add(cred)

        orders_data = snapshot_data.get("customer_orders", [])
        if orders_data:
            existing_order_ids = set(r[0] for r in db.query(CustomerOrder.order_id).all())
            for o_data in orders_data:
                oid = o_data.get("order_id")
                if oid and oid in existing_order_ids:
                    continue
                items_val = o_data.get("items", [])
                items_json = json.dumps(items_val, ensure_ascii=False) if isinstance(items_val, list) else o_data.get("items_json", "[]")
                co = CustomerOrder(
                    order_id=oid or f"ORD-{uuid.uuid4().hex[:4].upper()}",
                    vendor_id=o_data.get("vendor_id", "DEMO_KIRANA_KOP"),
                    customer_phone=o_data.get("customer_phone", ""),
                    raw_message=o_data.get("raw_message", ""),
                    image_url=o_data.get("image_url", ""),
                    items_json=items_json,
                    total_amount=float(o_data.get("total_amount", 0.0)),
                    status=o_data.get("status", "PENDING")
                )
                db.add(co)

        db.commit()

        # Resynchronize PostgreSQL SERIAL sequences so explicit primary keys do not collide
        if not is_sqlite:
            from sqlalchemy import text
            try:
                for tbl in ["products", "transactions", "customer_credits", "customer_orders"]:
                    db.execute(text(f"SELECT setval(pg_get_serial_sequence('{tbl}', 'id'), COALESCE((SELECT MAX(id) FROM {tbl}), 1));"))
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"[STATE RESTORE] Sequence sync notice: {e}")

        checkpoint_wal(truncate=True)
        return {
            "restored": True,
            "products_count": restored_products,
            "transactions_count": restored_transactions,
            "orders_count": len(orders_data)
        }

    @classmethod
    def ingest_catalog_from_video(
        cls,
        video_bytes: bytes,
        mime_type: str = "video/mp4",
        vendor_id: str = "DEMO_KIRANA_KOP",
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        End-to-End Zero-Touch Video Onboarding Pipeline (Specification 02).
        1. Invokes Gemini 2.5 Flash Multimodal Video Digitizer.
        2. Generates collision-free SKUs ('AUTO-VID-XXXXXX') and assigns vernacular Marathi aliases.
        3. Persists products ACID-compliantly into PostgreSQL/SQLite.
        4. Re-synchronizes PostgreSQL primary key sequences.
        5. Flushes durable state snapshot to data/vyaparai_state.json.
        6. Emits CATALOG_ONBOARDED and METRICS_UPDATE WebSocket broadcast.
        7. Returns structured confirmation and formatted WhatsApp Marathi receipt.
        """
        close_db = False
        if db is None:
            from app.core.database import SessionLocal
            db = SessionLocal()
            close_db = True

        try:
            # 1. Digitize catalog items from video sweep
            extracted = GeminiService.digitize_catalog_from_video(
                video_bytes=video_bytes,
                mime_type=mime_type
            )

            if not extracted:
                return {
                    "success": False,
                    "count": 0,
                    "products": [],
                    "reply_message": "⚠️ व्हिडिओमधून कोणत्याही वस्तू ओळखता आल्या नाहीत. कृपया चांगल्या प्रकाशात पुन्हा स्कॅन करा.",
                    "confirmation_receipt": "⚠️ व्हिडिओमधून कोणत्याही वस्तू ओळखता आल्या नाहीत."
                }

            created_products: List[Product] = []
            for item in extracted:
                # Generate collision-free SKU
                existing_sku = item.get("sku")
                if not existing_sku or not str(existing_sku).startswith("AUTO-VID-"):
                    sku = f"AUTO-VID-{uuid.uuid4().hex[:6].upper()}"
                else:
                    sku = str(existing_sku).strip()

                while db.query(Product).filter_by(sku=sku).first():
                    sku = f"AUTO-VID-{uuid.uuid4().hex[:6].upper()}"

                name_mr = item.get("name_mr", "")
                name_en = item.get("name_en", "")
                category = item.get("category", "General Store")
                stock = float(item.get("stock", 1.0))
                unit = item.get("unit", "piece")
                unit_price = float(item.get("unit_price", 10.0))
                min_threshold = float(item.get("min_threshold", 1.0))
                aliases = item.get("aliases", [])

                prod = Product(
                    vendor_id=vendor_id,
                    sku=sku,
                    name_mr=name_mr,
                    name_en=name_en,
                    category=category,
                    stock=stock,
                    unit=unit,
                    unit_price=unit_price,
                    min_threshold=min_threshold
                )
                prod.aliases = aliases
                db.add(prod)
                created_products.append(prod)

            db.commit()

            # Sequence sync on PostgreSQL to prevent primary key collision
            if not is_sqlite:
                from sqlalchemy import text
                try:
                    db.execute(text("SELECT setval(pg_get_serial_sequence('products', 'id'), COALESCE((SELECT MAX(id) FROM products), 1));"))
                    db.commit()
                except Exception as seq_err:
                    db.rollback()
                    print(f"[VIDEO INGEST] Sequence sync notice: {seq_err}")

            checkpoint_wal(truncate=True)

            # Persist durable state snapshot
            cls.save_state_snapshot(db, vendor_id=vendor_id)

            products_data = [p.to_dict() for p in created_products]

            # Emit WebSocket broadcast
            ws_payload = {
                "event": "CATALOG_ONBOARDED",
                "type": "CATALOG_ONBOARDED",
                "count": len(created_products),
                "products": products_data
            }
            try:
                ws_manager.broadcast_sync(ws_payload)
                m = cls.get_dashboard_metrics(db, vendor_id=vendor_id)
                ws_manager.broadcast_sync({
                    "type": "METRICS_UPDATE",
                    "vendor_id": vendor_id,
                    "metrics": m
                })
            except Exception as ws_err:
                print(f"[VIDEO INGEST WS WARN]: {ws_err}")

            # Build formatted WhatsApp Marathi confirmation receipt (Section 6 of spec)
            first_alias = ""
            for p in created_products:
                if p.aliases:
                    first_alias = p.aliases[0]
                    break
            if not first_alias and created_products:
                first_alias = created_products[0].name_mr.split()[0]
            if not first_alias:
                first_alias = "पेन"

            item_lines = []
            for i, p in enumerate(created_products, 1):
                stock_str = f"{p.stock:g}"
                item_lines.append(
                    f"{i}. *{p.name_mr}*\n"
                    f"   • साठा: *{stock_str} {p.unit}* | दर: *₹{p.unit_price:.2f}*"
                )
            items_formatted = "\n".join(item_lines)

            receipt = (
                f"🎉 *दुकान डिजिटायझेशन यशस्वी (Store Digitized)!*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🏪 *एकूण नवीन वस्तू:* {len(created_products)} जोडल्या\n\n"
                f"{items_formatted}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👉 *आता आपण थेट व्हॉइस नोट पाठवून यांची विक्री करू शकता!*\n"
                f"(उदा. *'२ {first_alias} दिले'* बोलून पहा)"
            )

            return {
                "success": True,
                "count": len(created_products),
                "products": products_data,
                "reply_message": receipt,
                "confirmation_receipt": receipt
            }
        finally:
            if close_db:
                db.close()

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

        # Loose Commodity Reverse-Math Pre-Flight Check:
        # Detects Money-to-Weight or Weight-to-Money with 0.05ms sub-millisecond local execution
        if not parsed_payload or (not parsed_payload.get("items") and parsed_payload.get("intent") not in ("UNDO", "QUERY", "REFUND")):
            raw_clean = raw_text.strip().lower()
            if not any(w in raw_clean for w in ["undo", "cancel", "चूक झाली", "रद्द करा", "मागे घ्या", "साठा दाखवा", "स्टॉक दाखवा", "पैसे परत", "रिफंड"]):
                loose_parsed = LooseCommodityEngine.parse_order(raw_text, catalog_data)
                if loose_parsed.get("errors"):
                    err = loose_parsed["errors"][0]
                    return {
                        "success": False,
                        "intent": "SALE",
                        "updates": [],
                        "total_amount": 0.0,
                        "alerts": [err["alert"]],
                        "reply_message": err["reply_message"]
                    }
                if loose_parsed.get("has_reverse_math"):
                    parsed_payload = loose_parsed

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
                "आले", "आणले", "आणली", "भरले", "भरली", "जमा", "खरेदी", "stock aala", "stock आला",
                "restock", "purchase", "supplier", "नवा माल", "नवीन माल", "inward"
            ]
            raw_lower = raw_text.lower()
            if not any(w in raw_lower for w in restock_triggers):
                try:
                    print(f"[INTENT RECTIFIED]: Overrode false RESTOCK to SALE for retail phrase: '{raw_text}'")
                except Exception:
                    pass
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
                    try:
                        print(f"[INTENT RECTIFIED]: Overrode false QUERY to SALE for retail phrase: '{raw_text}'")
                    except Exception:
                        pass
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
                    delta = -round(actual_deduction, 3)
                    new_stock = round(max(0.0, product.stock - actual_deduction), 3)
                else:
                    delta = -round(qty, 3)
                    new_stock = round(max(0.0, product.stock - qty), 3)
            else:
                delta = round(qty, 3)
                new_stock = round(product.stock + qty, 3)

            # Zero-Delta Invariant: If stock is 0 and deduction is 0, do not create a zero-delta transaction row
            if is_sale and abs(delta) < 1e-6:
                continue

            product.stock = new_stock

            is_reverse_math = bool(item_data.get("is_reverse_math", False))
            if is_reverse_math and item_data.get("total_amount") is not None:
                line_amount = round(float(item_data["total_amount"]), 2)
            else:
                line_amount = round(abs(delta) * product.unit_price, 2)

            if is_sale:
                total_bill_amount = round(total_bill_amount + line_amount, 2)

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
                "price": product.unit_price,
                "line_amount": line_amount,
                "is_reverse_math": is_reverse_math,
                "reverse_math_type": item_data.get("reverse_math_type"),
                "target_grams": item_data.get("target_grams", int(round(abs(delta) * 1000.0))),
                "money": item_data.get("money", line_amount)
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
            # Check if this transaction is a single Reverse-Math loose item
            if len(updates_applied) == 1 and updates_applied[0].get("is_reverse_math"):
                u = updates_applied[0]
                if u.get("reverse_math_type") == "MONEY_TO_WEIGHT":
                    reply = LooseCommodityEngine.format_money_to_weight_notice(
                        product_name_mr=u["name"],
                        target_grams=u["target_grams"],
                        money=u["line_amount"],
                        unit_price=u["price"],
                        stock_after=u["remaining"]
                    )
                else:  # WEIGHT_TO_MONEY
                    reply = LooseCommodityEngine.format_weight_to_money_notice(
                        product_name_mr=u["name"],
                        total_price=u["line_amount"],
                        grams=u["target_grams"],
                        unit_price=u["price"],
                        stock_after=u["remaining"]
                    )
                if alerts_triggered:
                    reply += "\n\n🚨 *साठा इशारा:*\n" + "\n".join(alerts_triggered)
            else:
                action_verb = "विक्री नोंदवली (Sale Recorded)" if intent == "SALE" else "साठा जमा केला (Stock Added)"
                scale_cards = []
                for u in updates_applied:
                    if u.get("is_reverse_math"):
                        if u.get("reverse_math_type") == "MONEY_TO_WEIGHT":
                            scale_cards.append(f"⚖️ *काट्यावर ठेवा:* *{u['name']} : {u['target_grams']} ग्रॅम* (रक्कम: ₹{u['line_amount']:.2f})")
                        elif u.get("reverse_math_type") == "WEIGHT_TO_MONEY":
                            scale_cards.append(f"⚖️ *काटा प्रमाण:* *{u['name']} : {u['target_grams']} ग्रॅम* (रक्कम: ₹{u['line_amount']:.2f})")

                items_summary = "\n".join([f"• {u['name']}: *{u['qty']} {u['unit']}* (शिल्लक: *{u['remaining']} {u['unit']}*)" for u in updates_applied])

                reply = f"✅ *{action_verb}!*\n\n"
                if scale_cards:
                    reply += "\n".join(scale_cards) + "\n\n"
                reply += items_summary
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
                product.stock = round(max(0.0, product.stock - tx.quantity_delta), 3)
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

    @classmethod
    def create_customer_yaadi_order(
        cls,
        customer_phone: str,
        items: List[Dict[str, Any]],
        raw_message: str = "",
        image_url: str = "",
        vendor_id: str = "DEMO_KIRANA_KOP",
        db: Optional[Session] = None
    ) -> CustomerOrder:
        """
        Creates a customer yaadi order in PENDING status (Specification 03).
        Enforces Zero Direct Ledger Modification Invariant:
        Inventory stock is NOT deducted on order creation.
        Saves durable state snapshot and broadcasts NEW_CUSTOMER_YAADI via WebSocket.
        """
        close_db = False
        if db is None:
            from app.core.database import SessionLocal
            db = SessionLocal()
            close_db = True

        try:
            order_id = f"ORD-{uuid.uuid4().hex[:4].upper()}"
            while db.query(CustomerOrder).filter_by(order_id=order_id).first():
                order_id = f"ORD-{uuid.uuid4().hex[:4].upper()}"

            clean_phone = (
                str(customer_phone or "")
                .replace("@c.us", "")
                .replace("@g.us", "")
                .replace("whatsapp:", "")
                .replace("+", "")
                .replace("-", "")
                .replace(" ", "")
                .strip()
            )

            total_amount = sum(float(i.get("line_total", 0.0)) for i in items if i.get("is_available", True))

            order = CustomerOrder(
                order_id=order_id,
                vendor_id=vendor_id,
                customer_phone=clean_phone or str(customer_phone),
                raw_message=raw_message,
                image_url=image_url,
                items_json=json.dumps(items, ensure_ascii=False),
                total_amount=round(total_amount, 2),
                status="PENDING",
                created_at=datetime.utcnow()
            )
            db.add(order)
            db.commit()
            db.refresh(order)

            # Persist durable snapshot
            cls.save_state_snapshot(db, vendor_id=vendor_id)

            # Emit WebSocket broadcast
            ws_payload = {
                "event": "NEW_CUSTOMER_YAADI",
                "type": "NEW_CUSTOMER_YAADI",
                "order": order.to_dict()
            }
            try:
                ws_manager.broadcast_sync(ws_payload)
            except Exception as ws_err:
                print(f"[YAADI WS ERROR]: {ws_err}")

            return order
        finally:
            if close_db:
                db.close()

    @classmethod
    def pack_and_deduct_customer_order(
        cls,
        order_id: str,
        vendor_id: str = "DEMO_KIRANA_KOP",
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Packs a pending customer order and atomically decrements inventory stock.
        Only Available items in the order decrement stock.
        Transitions status from PENDING to PACKED.
        Saves state snapshot, emits CUSTOMER_ORDER_PACKED & METRICS_UPDATE via WebSocket,
        and returns customer completion receipt.
        """
        close_db = False
        if db is None:
            from app.core.database import SessionLocal
            db = SessionLocal()
            close_db = True

        try:
            order = db.query(CustomerOrder).filter_by(order_id=order_id, vendor_id=vendor_id).first()
            if not order:
                return {"success": False, "message": f"Order {order_id} not found."}

            if order.status != "PENDING":
                return {"success": False, "message": f"Order {order_id} is already {order.status}."}

            try:
                items = json.loads(order.items_json) if order.items_json else []
            except Exception:
                items = []

            deducted_items = []
            batch_id = f"ORD_PACK_{order.order_id}_{int(datetime.utcnow().timestamp())}"

            for item in items:
                if not item.get("is_available", True):
                    continue

                sku = item.get("sku_matched")
                qty = float(item.get("quantity", 0.0))
                prod = None
                if sku:
                    prod = db.query(Product).filter_by(sku=sku, vendor_id=vendor_id).first()
                if not prod and item.get("name_mr"):
                    prod = db.query(Product).filter(
                        Product.vendor_id == vendor_id,
                        Product.name_mr.ilike(f"%{item['name_mr']}%")
                    ).first()

                if prod:
                    stock_before = prod.stock
                    prod.stock = max(0.0, round(prod.stock - qty, 3))
                    tx = Transaction(
                        vendor_id=vendor_id,
                        batch_id=batch_id,
                        product_id=prod.id,
                        sku=prod.sku,
                        item_name=prod.name_mr,
                        transaction_type="SALE",
                        quantity_delta=-qty,
                        stock_after=prod.stock,
                        unit_price=prod.unit_price,
                        total_amount=round(qty * prod.unit_price, 2),
                        raw_message=f"Customer Order {order.order_id} packed"
                    )
                    db.add(tx)
                    deducted_items.append({
                        "name": prod.name_mr,
                        "sku": prod.sku,
                        "qty": qty,
                        "stock_before": stock_before,
                        "stock_after": prod.stock,
                        "unit": prod.unit
                    })

            order.status = "PACKED"
            db.commit()

            # Sequence sync for Postgres
            if not is_sqlite:
                from sqlalchemy import text
                try:
                    for tbl in ["products", "transactions", "customer_orders"]:
                        db.execute(text(f"SELECT setval(pg_get_serial_sequence('{tbl}', 'id'), COALESCE((SELECT MAX(id) FROM {tbl}), 1));"))
                    db.commit()
                except Exception as seq_err:
                    db.rollback()

            checkpoint_wal(truncate=True)
            cls.save_state_snapshot(db, vendor_id=vendor_id)

            # Broadcast WebSocket updates
            try:
                ws_manager.broadcast_sync({
                    "event": "CUSTOMER_ORDER_PACKED",
                    "type": "CUSTOMER_ORDER_PACKED",
                    "order_id": order.order_id,
                    "order": order.to_dict()
                })
                metrics = cls.get_dashboard_metrics(db, vendor_id=vendor_id)
                ws_manager.broadcast_sync({
                    "type": "METRICS_UPDATE",
                    "vendor_id": vendor_id,
                    "metrics": metrics
                })
            except Exception as ws_err:
                print(f"[ORDER PACK WS ERROR]: {ws_err}")

            # WhatsApp receipt to customer
            customer_receipt = (
                f"🎉 *आपले किराणा सामान पॅक झाले आहे!* 🛍️\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📦 *ऑर्डर आयडी:* #{order.order_id}\n"
                f"🏪 *दुकान:* बाबुराव किराणा स्टोअर्स, कोल्हापूर\n"
                f"💰 *देय रक्कम:* *₹{order.total_amount:.2f}* (रोख किंवा Google Pay)\n\n"
                f"👉 कृपया दुकानातून आपले सामान घेऊन जावे ही नम्र विनंती.\n"
                f"🙏 *आपला दिवस शुभ जावो!*"
            )

            if order.customer_phone:
                try:
                    WhatsAppService.send_message(to_phone=order.customer_phone, message=customer_receipt)
                except Exception as wa_err:
                    print(f"[ORDER PACK WA NOTICE]: {wa_err}")

            return {
                "success": True,
                "order_id": order.order_id,
                "order": order.to_dict(),
                "status": "PACKED",
                "deducted_items": deducted_items,
                "customer_receipt": customer_receipt,
                "total_amount": order.total_amount
            }
        finally:
            if close_db:
                db.close()

    @classmethod
    def format_customer_yaadi_receipt(cls, order: CustomerOrder) -> str:
        """
        Formats instant WhatsApp acknowledgment receipt sent to customer upon receiving their yaadi.
        Highlights available items with prices and missing items with polite warning (Section 6.1).
        """
        try:
            items = json.loads(order.items_json) if order.items_json else []
        except Exception:
            items = []

        lines = [
            "🙏 *नमस्कार! बाबुराव किराणा स्टोअर्स* 🏪",
            "आपली किराणा यादी प्राप्त झाली आहे! 📝",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"📦 *ऑर्डर आयडी:* #{order.order_id}\n"
        ]

        for i, it in enumerate(items, 1):
            name = it.get("name_mr") or it.get("name_raw")
            qty = it.get("quantity", 1.0)
            unit = it.get("unit", "")
            if it.get("is_available", True):
                tot = it.get("line_total", 0.0)
                lines.append(f"{i}. ✅ *{name}* ({qty} {unit}) - ₹{tot:.2f}")
            else:
                lines.append(f"{i}. ⚠️ *{name}* - (सध्या उपलब्ध नाही)")

        lines.append("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"💰 *अंदाजे एकूण बिल:* *₹{order.total_amount:.2f}*")
        lines.append("⏱️ *पॅकिंग वेळ:* साधारण १० ते १५ मिनिटांत तयार होईल.")
        lines.append("सामान तयार झाल्यावर आम्ही आपणास लगेच कळवू!")

        return "\n".join(lines)

    @classmethod
    def get_pending_customer_orders(cls, db: Session, vendor_id: str = "DEMO_KIRANA_KOP") -> List[Dict[str, Any]]:
        orders = db.query(CustomerOrder).filter(
            CustomerOrder.vendor_id == vendor_id,
            CustomerOrder.status == "PENDING"
        ).order_by(CustomerOrder.created_at.desc()).all()
        return [o.to_dict() for o in orders]

