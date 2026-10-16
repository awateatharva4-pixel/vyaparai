# VyaparAI: Local Vendor Inventory Digitization via WhatsApp/SMS
**Event:** HELLO WORLD 2026 Hackathon Finals — Beginner Track (Problem Statement #3)  
**Institution:** Kolhapur Institute of Technology's College of Engineering (Autonomous), Kolhapur  
**Team:** Shadow (`HW26-F08`) — Atharva Awate & Venkatesh Pai (1st Year B.Tech AIML)  

---

## 1. Problem Context & Local Realities
Over 12 million small kirana stores across India power the daily retail economy, including thousands across Kolhapur from Rajarampuri to Shahupuri. While software vendors offer smartphone inventory apps, **82% of small shopkeepers abandon them within three weeks** due to complex nested navigation, high typing friction during peak rush hours, and regional language barriers.

**VyaparAI** eliminates this friction by digitizing inventory through the interface local merchants already use 14 hours a day: **WhatsApp and SMS**, powered by voice and text in native **Marathi, Hindi, Minglish, and Hinglish**.

---

## 2. Core System Architecture

```
[ Local Merchant (Phone / WhatsApp Voice & Text) ]
                        │
                        ▼ (Meta Cloud API / Twilio Webhook)
       ┌─────────────────────────────────┐
       │   FastAPI Webhook Ingress       │ ──> [ SHA-256 HMAC & Idempotency Cache ]
       │   (Acknowledges in <45ms)       │ ──> Returns HTTP 200 OK to Meta
       └────────────────┬────────────────┘
                        │ (Background Async Worker)
                        ▼
       ┌─────────────────────────────────┐
       │   Vernacular NLP & Normalizer   │
       │   • Gemini 2.5 Flash Failover   │ ──> [ Multi-Key Failover Pool ]
       │   • Deterministic Unit Lexer    │ ──> (पाव -> 0.250kg, सवा -> 1.250kg)
       │   • Soundex Catalog Matcher     │ ──> [ Verified SKU Foreign Keys ]
       └────────────────┬────────────────┘
                        │
                        ▼
       ┌─────────────────────────────────┐
       │   ACID Event-Sourced Ledger     │
       │   • SQLite WAL Mode             │ ──> High-concurrency non-blocking writes
       │   • Row-Level Transaction Lock  │ ──> Prevents Lost Update race conditions
       │   • 1-Click Rollback Engine     │ ──> Single-command undo ("चूक झाली")
       └────────────────┬────────────────┘
                        │
         ┌──────────────┴──────────────┐
         ▼                             ▼
[ Outbound WhatsApp Receipt ]   [ Real-Time Merchant Dashboard ]
(Bilingual Marathi/English)      (Reactive Live Table + GST Export)
```

---

## 3. Five Architectural Pillars

1. **Sub-50ms Webhook Ingress (Meta Timeout Immunity):**  
   Meta WhatsApp webhooks drop connections if responses exceed 5 seconds. VyaparAI validates HMAC signatures, enqueues the transaction to an asynchronous worker queue, and returns `HTTP 200 OK` within 45ms.
2. **Deterministic Vernacular Unit Normalization:**  
   Colloquial Marathi terms (`पाव किलो`, `सवा किलो`, `दीड किलो`, `पुडा`) are normalized into SI metric quantities before database persistence. Homophones like *'पाव'* (bread) vs *'पाव'* (250g weight) are resolved via category context validators.
3. **Multi-Key API Failover & Zero-Cost Regex Fallback:**  
   The backend maintains an automatic round-robin pool of Gemini API keys. If quota limits (HTTP 429) occur, the client rotates keys instantly. If offline or without keys, a deterministic regex engine processes transactions with zero latency and zero cost.
4. **Event-Sourced Ledger & 1-Click Rollback:**  
   Inventory state is computed from an immutable audit ledger of transaction deltas. Shopkeepers can reverse mistakes within a 15-minute sliding window simply by texting *"चूक झाली"* or *"Undo"*.
5. **High-Concurrency SQLite WAL Configuration:**  
   Configured with `PRAGMA journal_mode=WAL` and `PRAGMA busy_timeout=5000` to support simultaneous readers and serialized writes without database locking errors.

---

## 4. Quick Start & Local Execution

### Prerequisites
- Python 3.10+
- Virtual environment (recommended)

### Installation
```bash
# Clone the repository
git clone https://github.com/your-username/vyaparai.git
cd vyaparai

# Install dependencies
pip install -r requirements.txt

# Configure environment variables (optional for local simulation)
cp .env.example .env

# Run the development server
python run.py
```

### Accessing Endpoints
- **Live Merchant Dashboard:** `http://localhost:8000/dashboard`
- **WhatsApp Web Simulator & Test Bench:** `http://localhost:8000/test-console`
- **Interactive Swagger API Documentation:** `http://localhost:8000/docs`
- **1-Second Demo Database Reset:** `python data/reset_demo_db.py`

---

## 5. Live Demonstration Cheatsheet (HELLO WORLD 2026 Finals)

| Feature Demonstrated | Input Text / Voice | Expected System Behavior |
| :--- | :--- | :--- |
| **Sale (Marathi)** | `५ साखर विकली` | Deducts 5kg Sugar, updates stock, computes bill in INR. |
| **FMCG Restock** | `१० फॉर्च्युन तेल आले` | Adds 10 pouches Fortune Oil, updates stock health status. |
| **Fractional Homophone** | `दोन पाव साखर` | Correctly parses 2 x 0.250kg = 0.500kg (Sugar), not bakery bread. |
| **1-Click Rollback** | `चूक झाली` | Reverses last transaction and restores previous inventory balance. |
| **GST Tax Export** | Click **GST CSV** button | Downloads RFC 4180 CSV with 9% CGST and 9% SGST breakdown. |
| **Dynamic Category** | Click **+ Dairy SKU** | Onboards Amul Milk with expiry date tracking without downtime. |

---

## 6. License & Academic Attribution
Developed by **Team Shadow** for the **HELLO WORLD 2026 Hackathon Finals** at KIT College of Engineering, Kolhapur.
