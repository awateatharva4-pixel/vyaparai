# 02. IDEAL EXPECTATION: 15-SECOND VIDEO STORE ONBOARDING (ZERO-TOUCH CATALOG DIGITIZATION)
**Project**: VyaparAI — Local Vendor Inventory Digitization via WhatsApp/SMS  
**Track**: HELLO WORLD 2026 (Beginner Track — Problem Statement #3)  
**Authors**: Atharva Awate & Venkatesh Pai (Team Shadow, ID: `HW26-F08`, KIT Kolhapur)  
**Status**: Target Implementation Specification (Sequence #2)  
**Execution Runtime**: Gemini 2.5 Flash Multimodal Video Engine + Isolated Key Pool + WebSockets

---

## 1. Domain Reality & Problem Context: The Cold-Start Fatal Flaw

### 1.1 Why 82% of Indian Shopkeepers Delete Retail Software
The entire retail SaaS industry (Khatabook, Vyapar, Bikayi, Dukaan, Zoho Inventory) suffers from an identical fatal assumption: **They assume a 50-year-old Kirana owner will spend 3 weeks doing manual spreadsheet data entry.**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│              THE TRADITIONAL RETAIL APP ONBOARDING NIGHTMARE                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Step 1: Download App (15 MB)                                                   │
│  Step 2: Enter OTP & Store Name                                                 │
│  Step 3: "Add Product 1 of 600" -> Type name, brand, barcode, MRP, stock...   │
│  Step 4: Repeat 599 times...                                                    │
│  RESULT: 82% OF SHOPKEEPERS UNINSTALL WITHIN 14 DAYS. COLD-START FAILURE.      │
└─────────────────────────────────────────────────────────────────────────────────┘
```

When asked why they don't digitize, Kolhapur Kirana owners reply in Marathi:
> *"दुकानात ६०० सामान आहे. डाळ, तांदूळ, साबण, बिस्कीट, तेल... एवढं सगळं टाईप कोण बसून करणार? माझ्याकडे टाईम नाही."*

### 1.2 The VyaparAI Paradigm Shift
The merchant **does not type a single character**. He does not speak 600 voice notes.

On Day 1:
1. He opens WhatsApp, taps the camera icon, and selects Video.
2. He walks down his store aisle for **10 to 15 seconds**, sweeping the phone camera across his shelves.
3. He sends the video to the VyaparAI WhatsApp number.
4. **Gemini 2.5 Flash Video decomposes the frames, reads brand typography & packaging text, estimates shelf stock counts, predicts regional market MRPs, auto-generates vernacular Marathi names, creates collision-free SKUs, and immediately populates the cloud database.**

**From an empty database to a live, price-tagged catalog in ONE WhatsApp video.**

---

## 2. Stage Demonstration Choreography: The "Judges' Desk Live Sweep"

To make this demo **impossible to fake or doubt**, the team executes it live on the judges' own personal belongings.

```
[ $T+0s: The Challenge ] ──► [ $T+3s: 5s Camera Sweep ] ──► [ $T+8s: WhatsApp Ingress ]
                                                                       │
                                                                       ▼
[ $T+15s: Voice Sale Proof ] ◄── [ $T+13s: Projector Lights Up ] ◄── [ $T+10s: Gemini Vision ]
```

| Timeline ($T$) | Actor | Stage Action | Projector Screen Display | WhatsApp Feedback |
| :--- | :--- | :--- | :--- | :--- |
| **$T + 0\text{s}$** | Atharva | Turns to judges: *"Judges, the #1 reason retail apps fail is onboarding. Place 4 random objects on your desk right now—your water bottle, a pen, your notebook, a biscuit packet."* | Dashboard shows current Kirana catalog (11 SKUs). | — |
| **$T + 3\text{s}$** | Venkatesh | Holds up phone, starts WhatsApp video recording, sweeps camera smoothly across the 4 objects for **5 seconds**, and hits Send. | — | Video sent indicator. |
| **$T + 8\text{s}$** | Green-API | Webhook receives `videoMessage`, downloads MP4 bytes via 302 redirect engine, passes to background worker. | — | Instant WhatsApp Ack: `🎥 *व्हिडिओ प्राप्त झाला! दुकान स्कॅन करत आहे...*` |
| **$T + 12\text{s}$** | Gemini Video | Gemini 2.5 Flash processes spatial frames, extracts 4 products with names, counts, prices, and vernacular aliases. | Projector rings audio chime! Screen animates with a glowing badge: **"✨ नवीन वस्तू डिजिटाईझ झाल्या!"** | WhatsApp sends formatted completion receipt. |
| **$T + 13\text{s}$** | Dashboard | 4 brand new product cards mount at the top of the inventory grid with glowing badges. Total SKUs: `11` ➔ `15`. Valuation increments. | - 🏷️ **Kinley Water Bottle 1L** (Qty: 1, ₹20)<br>- 🏷️ **Reynolds Blue Pen** (Qty: 2, ₹10)<br>- 🏷️ **Classmate Notebook** (Qty: 1, ₹65)<br>- 🏷️ **Parle-G 100g** (Qty: 3, ₹10) | — |
| **$T + 16\text{s}$** | Atharva | *"And now, watch the complete lifecycle. The store is digitized. Let's make an immediate sale."* Speaks into WhatsApp: **"२ पेन आणि १ पाण्याची बाटली दिली"** | Pen stock drops from `2` to `0`. Bottle stock drops from `1` to `0`. Sale recorded: ₹40. | 🧾 *पावती: ₹४०.०० (२ पेन, १ बाटली)* |

---

## 3. The Autonomous Voice Alias Bridge (The Secret Weapon)

When Gemini extracts a product from video, **it must not stop at names and prices**. It must autonomously synthesize a dense cluster of **vernacular voice aliases**.

#### Example: Reynolds Ballpen Ingestion
```json
{
  "name_en": "Reynolds Blue Ballpen",
  "name_mr": "रेनॉल्ड्स बॉलपेन (Reynolds Pen)",
  "sku": "AUTO-VID-REY01",
  "category": "Stationery & Office / स्टेशनरी",
  "unit": "piece",
  "unit_price": 10.0,
  "stock": 2.0,
  "min_threshold": 1.0,
  "aliases": [
    "reynolds", "pen", "पेन", "बॉलपेन", "reynolds pen", 
    "blue pen", "निळा पेन", "ballpen", "टाक"
  ]
}
```

### Why This Invariant is Mandatory:
Because `aliases` are populated dynamically on Day-0:
1. When the vendor later sends a voice note in Marathi: *"दोन पेन दिले"*,
2. The vernacular lexer searches `p.aliases` across all database products,
3. Finds `"पेन"` inside `AUTO-VID-REY01`,
4. Deducts 2 units immediately with **zero manual configuration or mapping required**.

---

## 4. Architectural & Code Invariants

```
┌────────────────────────────────────────────────────────────────────────┐
│                        WHATSAPP VIDEO INGRESS                          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Green-API `videoMessage` (MP4)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│      ISOLATED BACKGROUND WORKER (Returns immediate 200 OK to Meta)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│      DEDICATED GEMINI VIDEO ENGINE (`GEMINI_VIDEO_API_KEY`)            │
│      - Model: gemini-2.5-flash                                         │
│      - Temperature: 0.1                                                │
│      - Schema: Strict JSON Mode (name_en, name_mr, price, aliases)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│              ACID INVENTORY INGESTION CONTROLLER                       │
│      - Generate collision-free SKU (`AUTO-VID-XXXX`)                   │
│      - Bulk `db.merge()` to Supabase Cloud PostgreSQL                 │
│      - Sync PostgreSQL sequence: `SELECT setval(...)`                  │
│      - Durable snapshot flush to `data/vyaparai_state.json`            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  ▼                                   ▼
┌──────────────────────────────────┐┌────────────────────────────────────┐
│ REAL-TIME WEBSOCKET BROADCAST    ││ WHATSAPP MERCHANT RECEIPT          │
│ - Channel: `/ws/inventory`       ││ - "🎉 दुकान डिजिटायझेशन यशस्वी!"   │
│ - Event: `CATALOG_ONBOARDED`     ││ - Lists items, prices, and voice   │
│ - Dashboard mounts cards live    ││   note readiness                   │
└──────────────────────────────────┘└────────────────────────────────────┘
```

### 4.1 Strict Quota Isolation Invariant
- **Dedicated Environment Variable**: `GEMINI_VIDEO_API_KEY`.
- If video token consumption hits a temporary rate limit, **the 3 existing voice note keys (`GEMINI_API_KEY_1`, `_2`, `_3`) are completely untouched**.
- Zero risk of voice sales crashing due to video onboarding.

### 4.2 Web Simulator Drag-and-Drop Fallback (The Stage Safety Net)
- In addition to WhatsApp ingress, the web simulator at `/simulator` must feature a dedicated card:  
  **"🎥 Store Video Sweep (ऑनबोर्डिंग व्हिडिओ)"**.
- Supports 1-click file upload (`.mp4`, `.mov`, `.webm`).
- If campus Wi-Fi or cellular data throttles WhatsApp media downloads on stage, Atharva can drag-and-drop a pre-recorded 5-second video file directly into the browser on the projector laptop, yielding the exact same real-time onboarding result!

---

## 5. Gemini Multimodal Video Prompt Specification

```python
VIDEO_DIGITIZATION_PROMPT = """
You are an expert Indian retail inventory digitizer specializing in Kirana and FMCG goods.
Analyze this video sweep of shop shelves or retail items.
Decompose the frames and identify all distinct packaged products and loose items visible.

For every distinct product detected, extract:
1. "name_en": Clear English brand and product name (e.g., 'Reynolds Blue Pen', 'Kinley Water Bottle 1L', 'Classmate Spiral Notebook').
2. "name_mr": Accurate vernacular Marathi name with English in parentheses (e.g., 'रेनॉल्ड्स बॉलपेन (Reynolds Pen)', 'किनले पाण्याची बाटली १L (Kinley Bottle)').
3. "category": One of ['Grains & Sweeteners', 'Edible Oils', 'Packaged Snacks', 'Dairy & Fresh', 'Stationery & Office', 'Beverages', 'Personal Care'].
4. "stock": Estimated visible count on shelf/table (float, default to visible items, min 1.0).
5. "unit_price": Standard Indian retail price / MRP in INR (float, e.g., 10.0, 20.0, 65.0). If printed on packaging, read it directly; otherwise predict standard Indian FMCG market rates.
6. "unit": Standard unit from ['piece', 'bottle', 'packet', 'kg', 'pouch', 'book'].
7. "min_threshold": Reorder warning level (typically 20% of initial stock, min 1.0).
8. "aliases": Array of 5-8 vernacular search terms, transliterations, and colloquial slang for Marathi voice recognition (e.g., ['pen', 'पेन', 'बॉलपेन', 'reynolds']).

Return ONLY a valid JSON object matching this exact schema:
{
  "products": [
    {
      "name_en": "string",
      "name_mr": "string",
      "category": "string",
      "stock": float,
      "unit_price": float,
      "unit": "string",
      "min_threshold": float,
      "aliases": ["string"]
    }
  ]
}
"""
```

---

## 6. WhatsApp Confirmation Typography & Format

```text
🎉 *दुकान डिजिटायझेशन यशस्वी (Store Digitized)!*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏪 *एकूण नवीन वस्तू:* {count} जोडल्या

{for i, item in enumerate(products, 1)}
{i}. *{item.name_mr}*
   • साठा: *{item.stock} {item.unit}* | दर: *₹{item.unit_price:.2f}*
{endfor}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👉 *आता आपण थेट व्हॉइस नोट पाठवून यांची विक्री करू शकता!*
(उदा. *'२ {products[0].aliases[0]} दिले'* बोलून पहा)
```

---

## 7. Acceptance Criteria & Test Matrix

- [ ] `test_video_ingress_greenapi`: Webhook parses `typeMessage == "videoMessage"`, extracts `downloadUrl`, and follows redirects.
- [ ] `test_simulator_video_upload`: `POST /api/simulator/video` accepts `multipart/form-data`, ingests MP4 bytes, and returns JSON.
- [ ] `test_gemini_video_extraction`: Processes 5s MP4 clip and returns structured JSON with all 8 fields.
- [ ] `test_db_persistence_and_snapshot`: Ingested products persist in PostgreSQL and survive simulated container restart via `vyaparai_state.json`.
- [ ] `test_voice_continuity_loop`: Immediately after video ingestion, a voice note containing a synthesized alias successfully deducts stock.
- [ ] `test_websocket_stream_payload`: `/ws/inventory` receives `CATALOG_ONBOARDED` event within 200ms of DB commit.
- [ ] `test_quota_isolation`: Invalid or exhausted `GEMINI_VIDEO_API_KEY` does not affect audio transcription on `GEMINI_API_KEY_1`.
