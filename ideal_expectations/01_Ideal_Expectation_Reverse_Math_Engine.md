# 01. IDEAL EXPECTATION: LOOSE COMMODITY REVERSE-MATH ENGINE ("VOICE-TO-SCALE")
**Project**: VyaparAI — Local Vendor Inventory Digitization via WhatsApp/SMS  
**Track**: HELLO WORLD 2026 (Beginner Track — Problem Statement #3)  
**Authors**: Atharva Awate & Venkatesh Pai (Team Shadow, ID: `HW26-F08`, KIT Kolhapur)  
**Status**: Target Implementation Specification (Sequence #1)  
**Execution Runtime**: Sub-millisecond Local Deterministic Python Engine (Zero External AI Calls, 0.05ms Latency)

---

## 1. Domain Reality & Problem Context: The "Dirty Calculator" Bottleneck

### 1.1 The Kirana Retail Phenomenon
In Indian tier-2/3 retail (Kolhapur Kirana stores), over **45% of daily transactions involve unpackaged loose commodities**:
- Sugar (साखर), Grains (गहू, तांदूळ), Pulses/Dals (तूर डाळ, मूग डाळ), Oil by volume/weight (खुले तेल), and Vegetables (कांदा, बटाटा, आले).

Unlike packaged FMCG goods (e.g., *Parle-G 100g* with a fixed ₹10 barcode), loose commodities operate on **continuous variable weights and arbitrary currency fractions**.

### 1.2 The Two Customer Ordering Paradigms
Customers almost **never** order in clean units. They order in one of two ways:

```
                          ┌────────────────────────────────────────────────────────┐
                          │         VERNACULAR KIRANA CUSTOMER ORDER               │
                          └──────────────────────────┬─────────────────────────────┘
                                                     │
                   ┌─────────────────────────────────┴─────────────────────────────────┐
                   ▼                                                                   ▼
       [ PARADIGM A: MONEY-TO-WEIGHT ]                                     [ PARADIGM B: WEIGHT-TO-MONEY ]
     "रमेश काका, २० रुपयांची साखर द्या"                                     "३५० ग्रॅम शेंगदाणे आणि पावशेर कांदा"
                   │                                                                   │
                   ▼                                                                   ▼
      Customer specifies: Money (₹)                                       Customer specifies: Weight (g)
      Merchant must calculate: Weight (g)                                 Merchant must calculate: Money (₹)
      Formula: Weight = (Money / Rate) * 1000                             Formula: Money = (Weight / 1000) * Rate
      Mental Math: 20 ÷ 42 × 1000 = 476.19g                               Mental Math: 350 ÷ 1000 × 140 = ₹49.00
```

### 1.3 The Fatal Friction in Current Apps
In Khatabook, Vyapar, or standard POS machines:
1. The shopkeeper must stop what he is doing.
2. Pick up a physical calculator with grease-stained hands.
3. Calculate: $20 \div 42 \times 1000 = 476.19\text{g}$.
4. Place the polythene bag on the mechanical/digital scale until the scale shows `476g`.
5. Manually type `0.476` into the app.

**VyaparAI eliminates all 5 steps in under 0.05 milliseconds using Voice-to-Scale Reverse Math.**

---

## 2. Stage Demonstration Choreography (Second-by-Second)

| Timeline ($T$) | Actor | Action on Stage | Visual / Audio Output on Projector | WhatsApp Feedback |
| :--- | :--- | :--- | :--- | :--- |
| **$T + 0.0\text{s}$** | Atharva | Turns to judges: *"Judges, watch how a Kolhapur shopkeeper handles loose commodities without touching a calculator."* | Clean Merchant Dashboard on Projector. Sugar Stock: `50.000 kg` @ ₹42.00/kg. | — |
| **$T + 2.0\text{s}$** | Venkatesh | Sends voice note on WhatsApp: **"२० रुपयांची साखर दिली"** (or types `20 chi sakhar`). | — | Green check on WhatsApp. |
| **$T + 2.1\text{s}$** | VyaparAI Engine | Sub-1ms regex lexer matches Money-to-Weight, fetches `GROC-SUG-001` unit price (₹42/kg), computes $476\text{g}$. | Live WebSocket Chime! Sugar card animates: stock updates to **`49.524 kg`** (-0.476 kg). Today's Sales updates: **+₹20.00**. | WhatsApp Bot sends instant Scale Receipt with Scale Placement Card. |
| **$T + 3.0\text{s}$** | Atharva | Points to phone: *"Look at the instruction on screen: **'काट्यावर ठेवा: ४७६ ग्रॅम'**. The shopkeeper fills the bag to 476g. No calculator. Stock is already deducted."* | Dashboard displays Transaction #108: `SALE - Sugar (476g) - ₹20.00`. | — |
| **$T + 5.0\text{s}$** | Venkatesh | Speaks second order: **"३५० ग्रॅम कांदा"** | Onion stock drops from `70.000 kg` to **`69.650 kg`**. Revenue: **+₹12.25**. | 💰 *कांदा बिल: ₹१२.२५ (३५० ग्रॅम)* |

---

## 3. Mathematical Formulations & Precision Invariants

### 3.1 Money-to-Weight Formulation
Given a monetary amount $M \in \mathbb{R}^+$ and a product catalog unit price $P_{\text{kg}} \in \mathbb{R}^+$ (Price per kilogram):

$$\text{Target Weight in Grams } (W_g) = \text{round}\left(\frac{M}{P_{\text{kg}}} \times 1000\right)$$

$$\text{Ledger Deduction in Kilograms } (\Delta Q) = -\frac{W_g}{1000.0} = -\text{round}\left(\frac{M}{P_{\text{kg}}}, 3\right)$$

$$\text{Ledger Revenue Delta } (\Delta R) = +M$$

#### Example: Sugar @ ₹42.00/kg with $M = ₹20.00$:
$$W_g = \text{round}\left(\frac{20.0}{42.0} \times 1000\right) = \text{round}(476.1904) = 476\text{ grams}$$
$$\Delta Q = -\frac{476}{1000.0} = -0.476\text{ kg}$$
$$\text{Stock After} = 50.000 - 0.476 = 49.524\text{ kg}$$
$$\text{Revenue} = +₹20.00$$

### 3.2 Weight-to-Money Formulation
Given requested grams $W_g \in \mathbb{R}^+$ and catalog price per kg $P_{\text{kg}} \in \mathbb{R}^+$:

$$\text{Total Price in Rupees } (T_M) = \text{round}\left(\frac{W_g}{1000.0} \times P_{\text{kg}}, 2\right)$$

$$\text{Ledger Deduction in Kilograms } (\Delta Q) = -\frac{W_g}{1000.0}$$

$$\text{Ledger Revenue Delta } (\Delta R) = +T_M$$

#### Example: Onion @ ₹35.00/kg with $W_g = 350\text{ grams}$:
$$T_M = \text{round}\left(\frac{350}{1000.0} \times 35.0, 2\right) = \text{round}(12.25, 2) = ₹12.25$$
$$\Delta Q = -0.350\text{ kg}$$
$$\text{Stock After} = 70.000 - 0.350 = 69.650\text{ kg}$$
$$\text{Revenue} = +₹12.25$$

### 3.3 Float Invariance & Rounding Guards
- **Zero IEEE-754 Epsilon Leaks**: All floating-point operations are explicitly rounded using `round(val, 3)` for kilograms and `round(val, 2)` for currency. Never store `49.52399999999999 kg`.
- **Zero-Division Defense**: If catalog $P_{\text{kg}} \le 0.0$, the engine rejects computation with an explicit merchant alert: `⚠️ [वस्तू]: विक्री दर निश्चित नाही.`

---

## 4. WhatsApp Receipt Typography & Formatting Specification

### 4.1 Money-to-Weight WhatsApp Template
```text
⚖️ *काट्यावर ठेवा (PLACE ON SCALE):*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👉 *{product_name_mr} : {target_grams} ग्रॅम*
💰 *रक्कम:* ₹{money:.2f} (दर: ₹{unit_price:.2f}/किलो)
📦 *उर्वरित साठा:* {stock_after:.3f} किलो
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ *विक्री नोंदवली (Sale Recorded)!*
```

### 4.2 Weight-to-Money WhatsApp Template
```text
💰 *किराणा बिल (LOOSE ITEM BILL):*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👉 *{product_name_mr} : ₹{total_price:.2f}*
⚖️ *प्रमाण:* {grams} ग्रॅम (दर: ₹{unit_price:.2f}/किलो)
📦 *उर्वरित साठा:* {stock_after:.3f} किलो
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ *विक्री नोंदवली (Sale Recorded)!*
```

---

## 5. Architectural Code Specification

```
[ Inbound Text / Google STT Output ]
                │
                ▼
  [ `LooseCommodityEngine.detect_and_compute()` ]
                │
        ┌───────┴───────┐
        ▼               ▼
[ Money-to-Weight ]  [ Weight-to-Money ]
  (e.g., "20 chi")     (e.g., "350 gm")
        │               │
        └───────┬───────┘
                ▼
   [ Match Catalog Unit Price ]
                │
                ▼
 [ Compute Wg / TM & Build ParsedItem ]
                │
                ▼
 [ Hand Over to `InventoryService.process_transaction_event()` ]
                │
        ┌───────┴───────┐
        ▼               ▼
[ ACID PostgreSQL DB ]  [ WebSocket Broadcast (`/ws/inventory`) ]
```

### 5.1 Linguistic Suffix & Token Matrix

| Type | Language | Regex Pattern Tokens | Examples |
| :--- | :--- | :--- | :--- |
| **Money Suffixes** | Marathi | `रुपयांची`, `रुपयांचे`, `रुपयांचा`, `रुपयाचे`, `रुपयाची`, `ची`, `चे`, `चा` | `"२० रुपयांची साखर"`, `"५० चे तेल"`, `"१० चा कांदा"` |
| **Money Suffixes** | Minglish / Eng | `rupayachi`, `rupayache`, `rupaye`, `rs`, `inr`, `₹`, `chi`, `che`, `ka`, `ki` | `"20 chi sakhar"`, `"50 rs sugar"`, `"10 rupaye kanda"` |
| **Weight Suffixes**| Marathi | `ग्रॅम`, `ग्राम`, `ग्रॅ`, `पावशेर` (250g), `अर्धा किलो` (500g) | `"३५० ग्रॅम साखर"`, `"पावशेर कांदा"` |
| **Weight Suffixes**| Minglish / Eng | `gm`, `g`, `gram`, `grams`, `gms` | `"350 gm shengdana"`, `"750 g aloo"` |

---

## 6. Multi-Item Clause Segmentation Isolation

When a merchant speaks a compound order:
> *"२० रुपयांची साखर आणि २ पार्ले बिस्कीट आणि ३५० ग्रॅम कांदा"*

1. **Clause Segmenter** splits by `आणि`, `,`, `+`:
   - Clause 1: `"२० रुपयांची साखर"` ➔ Identified by `LooseCommodityEngine` as Money-to-Weight (Sugar, 476g, ₹20.00).
   - Clause 2: `"२ पार्ले बिस्कीट"` ➔ Identified by standard Kirana Lexer as Fixed FMCG Unit (Parle-G, 2 packets, ₹20.00).
   - Clause 3: `"३५० ग्रॅम कांदा"` ➔ Identified by `LooseCommodityEngine` as Weight-to-Money (Onion, 0.350kg, ₹12.25).
2. **Consolidated Atomic Transaction**:
   - Total Order Value: $₹20.00 + ₹20.00 + ₹12.25 = ₹52.25$.
   - Deductions: Sugar (-0.476 kg), Parle-G (-2 pkt), Onion (-0.350 kg).
   - Single atomic commit under one `batch_id`. If `चूक झाली` (undo) is issued, all 3 items reverse simultaneously.

---

## 7. Acceptance Criteria & Test Matrix

- [ ] `test_money_to_weight_standard`: `"२० रुपयांची साखर"` resolves to `GROC-SUG-001`, `0.476 kg`, `₹20.00`.
- [ ] `test_money_to_weight_minglish`: `"20 chi sakhar"` resolves to `GROC-SUG-001`, `0.476 kg`, `₹20.00`.
- [ ] `test_weight_to_money_grams`: `"३५० ग्रॅम कांदा"` resolves to `VEG-KANDA-001`, `0.350 kg`, `₹12.25`.
- [ ] `test_fractional_pavsher`: `"पावशेर साखर"` resolves to `GROC-SUG-001`, `0.250 kg`, `₹10.50`.
- [ ] `test_multi_item_compound`: Compound sentence extracts both loose commodity scale item and fixed packet item.
- [ ] `test_zero_division_guard`: Product with price ₹0 raises clean error without server panic.
- [ ] `test_sub_millisecond_latency`: Total execution time from raw string to scale card $\le 0.5\text{ms}$.
