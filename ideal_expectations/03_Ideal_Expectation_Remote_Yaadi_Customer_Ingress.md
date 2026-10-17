# 03. IDEAL EXPECTATION: REMOTE "YAADI" (HANDWRITTEN CHIT OCR) & DUAL-ROLE INGRESS
**Project**: VyaparAI — Local Vendor Inventory Digitization via WhatsApp/SMS  
**Track**: HELLO WORLD 2026 (Beginner Track — Problem Statement #3)  
**Authors**: Atharva Awate & Venkatesh Pai (Team Shadow, ID: `HW26-F08`, KIT Kolhapur)  
**Status**: Target Implementation Specification (Sequence #3)  
**Execution Runtime**: Gemini 2.5 Flash Vision + Dual-Role Phone Firewall + Real-Time Order Queue

---

## 1. Domain Reality & Problem Context: The Two-Sided Kirana Network

### 1.1 From Back-Office Tool to a Two-Sided Commerce Platform
Every competing hackathon submission treats WhatsApp purely as an **internal admin remote control** for the merchant.

In reality, **millions of Indian households already send WhatsApp photos of handwritten grocery lists ("कच्ची पर्ची" / किराणा यादी) to their local neighborhood Kirana stores every morning**:
- A housewife writes on a paper slip: *"२ साखर, १ फॉर्च्युन तेल, ३ पार्ले बिस्कीट, अर्धा किलो कांदा"*.
- She snaps a photo and sends it to the shopkeeper's WhatsApp.
- The shopkeeper receives 25 such messy photo slips every morning. He has to manually read the cursive handwriting, walk the aisles to check what is in stock, write a manual bill, and call back.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    THE VYAPARAI TWO-SIDED WHATSAPP INGRESS                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                     SINGLE WHATSAPP NUMBER (+91 75584 55021)                    │
│                                       │                                         │
│                   ┌───────────────────┴───────────────────┐                     │
│                   ▼                                       ▼                     │
│        [ SENDER == MERCHANT ]                  [ SENDER != MERCHANT ]           │
│        (9579869506, 7558455021)                (Any Customer / Judge Phone)     │
│                   │                                       │                     │
│                   ▼                                       ▼                     │
│       👑 ADMIN MERCHANT FLOW                  🛒 CUSTOMER ORDER / YAADI FLOW    │
│       - Voice note stock deduction            - Handwritten slip OCR            │
│       - Daily closing ledger (8 PM)           - Live catalog availability check │
│       - Stock queries & undo rollback         - Automated estimated bill        │
│       - Customer credit reminders             - Instant packing queue card      │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Stage Demonstration Choreography: The "Judge's Handwritten Slip"

This beats any theoretical presentation because **the judges participate directly in the test.**

```
[ $T+0s: Judge writes on paper ] ──► [ $T+8s: Photo sent on WhatsApp ] ──► [ $T+12s: Gemini Vision ]
                                                                                   │
                                                                                   ▼
[ $T+18s: Merchant Packs & Deducts ] ◄── [ $T+15s: Dashboard Chime ] ◄── [ $T+13s: Customer Receipt ]
```

| Timeline ($T$) | Actor | Stage Action | Projector Screen Display | Customer Phone Feedback |
| :--- | :--- | :--- | :--- | :--- |
| **$T + 0\text{s}$** | Atharva | Hands a paper notepad & pen to Judge 1: *"Sir, pretend you are sitting at home and sending your morning grocery list to Baburao Kirana. Please write 3 items in Marathi or English (e.g., २ साखर, १ तेल, ५ बिस्कीट)."* | Live Merchant Dashboard on display. | — |
| **$T + 8\text{s}$** | Venkatesh | Takes a photo of the judge's handwritten slip from a non-merchant phone (e.g., customer demo phone) and sends it to the VyaparAI WhatsApp number. | — | Photo dispatched. |
| **$T + 12\text{s}$** | Backend | System identifies sender as non-merchant ➔ triggers Customer Yaadi Vision pipeline. Gemini 2.5 Flash reads handwriting, cross-references active catalog, calculates bill. | Audio Chime rings! A flashing amber card mounts on the dashboard: **"🔔 नवीन ग्राहक ऑर्डर (New Customer Order)!"** | Customer receives instant WhatsApp confirmation with itemized bill and packing time. |
| **$T + 14\text{s}$** | Atharva | Points to the customer's phone: *"The customer instantly received an itemized digital bill (₹289.00) and packing time without the shopkeeper typing a word."* | Dashboard displays the Pending Order card with customer phone, items, and a glowing green button: **[✅ पॅक करा व स्टॉक वजा करा]**. | Formatted Marathi receipt displayed on customer screen. |
| **$T + 17\text{s}$** | Atharva | Clicks **[Pack Order & Deduct Stock]** on the dashboard. | Sugar (-2kg), Oil (-1 pouch), Parle-G (-5 pkt) instantly decrement from stock. Card transitions to **"PACKED"**. | Customer WhatsApp receives: `📦 आपली ऑर्डर पॅक झाली आहे! दुकानातून घेऊन जावे.` |

---

## 3. Strict Dual-Role Security Firewall (Code Invariant)

To protect the business ledger, the webhook ingress enforces a cryptographic-level role firewall:

```python
AUTHORIZED_MERCHANT_PHONES = {
    "919579869506",
    "917558455021",
    "9579869506",
    "7558455021"
}

def is_merchant_sender(sender_phone: str) -> bool:
    clean = sender_phone.replace("+", "").replace("@c.us", "").replace("@g.us", "").strip()
    return clean in AUTHORIZED_MERCHANT_PHONES
```

### Security Invariants:
1. **Zero Privilege Escalation**: A customer can **never** execute an `UNDO` (rollback), trigger an 8:00 PM closing ledger dump, or view wholesale profit margins.
2. **Intent Sandboxing**: If a customer types *"साठा दाखवा"* (show stock), they receive a polite public customer catalog view—**not** the confidential internal merchant ledger with wholesale costs or low-stock alerts.
3. **No Direct Ledger Modification**: Inbound customer orders do **NOT** directly decrement inventory stock upon arrival. They enter a `PENDING` queue. Stock is only deducted when the merchant confirms packing by clicking the dashboard button or replying *"होय, पॅक केले"* (Yes, packed). This prevents inventory corruption if the customer cancels.

---

## 4. Gemini Vision Handwritten "Yaadi" Extraction Specification

```python
YAADI_VISION_PROMPT = """
You are an expert Indian retail document analyst specializing in handwritten Kirana grocery lists ("किराणा यादी" / "कच्ची पर्ची").
The provided image contains a handwritten shopping list in Marathi, Hindi, English, or mixed vernacular script.

Grounding Catalog:
{catalog_json}

Your task:
1. Read every handwritten line item and decipher the quantity, unit, and commodity name.
2. Cross-reference each detected item against the Grounding Catalog:
   - If an item matches a catalog SKU, link "sku_matched" and fetch standard "unit_price".
   - If an item is NOT in the catalog (e.g. 'Dettol Soap' when store only sells groceries), set "sku_matched": null and "is_available": false.
3. Compute line item totals (quantity * unit_price).

Return ONLY a valid JSON object matching this schema:
{
  "order_items": [
    {
      "name_raw": "string",
      "sku_matched": "string or null",
      "is_available": boolean,
      "quantity": float,
      "unit": "string",
      "unit_price": float,
      "line_total": float
    }
  ],
  "estimated_total": float,
  "all_items_available": boolean,
  "missing_items_count": integer
}
"""
```

---

## 5. Database Schema & State Resilience (`CustomerOrder`)

```python
class CustomerOrder(Base):
    __tablename__ = "customer_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(32), unique=True, index=True)  # e.g. "ORD-8402"
    vendor_id = Column(String(64), default="DEMO_KIRANA_KOP", index=True)
    customer_phone = Column(String(32), index=True)
    raw_message = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    items_json = Column(Text, nullable=False)  # Serialized JSON of line items
    total_amount = Column(Float, default=0.0)
    status = Column(String(24), default="PENDING", index=True)  # PENDING, PACKED, CANCELLED
    created_at = Column(DateTime, default=datetime.utcnow)
```

### State Snapshot Integration:
Whenever a `CustomerOrder` is created or transitions to `PACKED`, `InventoryService.save_state_snapshot()` serializes active orders into `data/vyaparai_state.json`. If Render restarts, all pending customer orders auto-restore seamlessly.

---

## 6. WhatsApp Customer Receipts & Typography

### 6.1 Instant Order Acknowledgment (To Customer)
```text
🙏 *नमस्कार! बाबुराव किराणा स्टोअर्स* 🏪
आपली किराणा यादी प्राप्त झाली आहे! 📝
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 *ऑर्डर आयडी:* #{order_id}

{for i, item in enumerate(items, 1)}
{if item.is_available}
{i}. ✅ *{item.name_mr}* ({item.quantity} {item.unit}) - ₹{item.line_total:.2f}
{else}
{i}. ⚠️ *{item.name_raw}* - (सध्या उपलब्ध नाही)
{endif}
{endfor}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 *अंदाजे एकूण बिल:* *₹{total_amount:.2f}*
⏱️ *पॅकिंग वेळ:* साधारण १० ते १५ मिनिटांत तयार होईल.
सामान तयार झाल्यावर आम्ही आपणास लगेच कळवू!
```

### 6.2 Order Packed Notification (To Customer)
```text
🎉 *आपले किराणा सामान पॅक झाले आहे!* 🛍️
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 *ऑर्डर आयडी:* #{order_id}
🏪 *दुकान:* बाबुराव किराणा स्टोअर्स, कोल्हापूर
💰 *देय रक्कम:* *₹{total_amount:.2f}* (रोख किंवा Google Pay)

👉 कृपया दुकानातून आपले सामान घेऊन जावे ही नम्र विनंती.
🙏 *आपला दिवस शुभ जावो!*
```

---

## 7. Acceptance Criteria & Test Matrix

- [ ] `test_role_firewall_merchant`: Messages from `+91 9579869506` and `+91 75584 55021` route strictly to Merchant Admin flow.
- [ ] `test_role_firewall_customer`: Messages from any other phone number route strictly to Customer Yaadi flow.
- [ ] `test_customer_handwritten_image_ingress`: Webhook receives image, downloads bytes, and invokes `parse_handwritten_yaadi`.
- [ ] `test_catalog_grounding_and_missing_items`: If a handwritten slip contains an unavailable item, it is marked `is_available: false` and excluded from bill total.
- [ ] `test_customer_order_db_lifecycle`: Order inserts with `PENDING` status, transitions to `PACKED`, and triggers atomic inventory stock deduction.
- [ ] `test_websocket_order_broadcast`: `/ws/inventory` receives `NEW_CUSTOMER_YAADI` event within 250ms of receipt.
- [ ] `test_security_rejection_customer_undo`: Customer attempting to send `"चूक झाली"` or `"undo"` is rejected and cannot touch merchant transactions.
