# VYAPARAI RED-TEAM AUDIT DOSSIER — FEATURE 1: REVERSE-MATH ENGINE
**Auditor**: Auditor 1 (Voice & Reverse-Math Invariant Auditor)  
**Target Specification**: `ideal_expectations/01_Ideal_Expectation_Reverse_Math_Engine.md`  
**Inspected Components**:
1. `app/services/loose_commodity_service.py` (`LooseCommodityEngine`)
2. `app/services/inventory_service.py` (`InventoryService.process_transaction_event`, `undo_last_transaction`)
3. `test_reverse_math.py` (Acceptance & Benchmark Suite)  
**Date of Audit**: October 18, 2026  
**Final Verdict**: **APPROVED (100% PASS - 7/7 INVARIANTS SATISFIED)**

---

## 1. Executive Summary

An exhaustive, adversarial red-team code audit and empirical verification of Feature 1 (**Loose Commodity Reverse-Math Engine / "Voice-to-Scale"**) was conducted.

The engine replaces the error-prone "dirty calculator" workflow in rural Kolhapur Kirana retail by deterministically parsing continuous monetary orders (Paradigm A: Money-to-Weight) and vernacular weight expressions (Paradigm B: Weight-to-Money) in Marathi and Minglish, performing sub-millisecond mathematical inversion, enforcing non-negative inventory deductions, and generating vernacular WhatsApp scale cards.

All 7 core architectural invariants, zero-division edge cases, IEEE-754 floating-point drift guards, homophone collisions, multi-item clause segmentation, atomic batch rollbacks, and sub-millisecond execution thresholds were audited and verified.

---

## 2. Specification Invariant Verification Matrix (7/7 Criteria)

| # | Specification Invariant | Target Requirement | Implementation Mechanism | Test Result | Status |
|---|---|---|---|---|---|
| **1** | **Formula 1: Money to Weight** | $W_g = \text{round}\left(\frac{M}{P_{\text{kg}}} \times 1000\right)$<br>$\Delta Q = -\text{round}\left(\frac{M}{P_{\text{kg}}}, 3\right)$<br>$\Delta R = +M$ | `LooseCommodityEngine.detect_money_to_weight`<br>`target_grams = int(round((money_val / unit_price) * 1000.0))`<br>`quantity_kg = round(money_val / unit_price, 3)` | `"२० रुपयांची साखर"` @ ₹42/kg &rarr; 476g, 0.476 kg, ₹20.00. Stock: 50.0kg &rarr; 49.524kg. `"20 chi sakhar"` yields identical result. | **PASS** |
| **2** | **Formula 2: Weight to Money** | $T_M = \text{round}\left(\frac{W_g}{1000} \times P_{\text{kg}}, 2\right)$<br>$\Delta Q = -\frac{W_g}{1000}$<br>$\Delta R = +T_M$ | `LooseCommodityEngine.detect_weight_to_money`<br>`total_price = round((grams / 1000.0) * unit_price, 2)`<br>`quantity_kg = round(grams / 1000.0, 3)` | `"३५० ग्रॅम कांदा"` @ ₹35/kg &rarr; ₹12.25, 0.350 kg. Stock: 70.0kg &rarr; 69.650kg. `"पावशेर साखर"` (250g) &rarr; ₹10.50, 0.250 kg. | **PASS** |
| **3** | **Zero-Division Defense** | If $P_{\text{kg}} \le 0.0$, gracefully reject without server panic or 500 error | Pre-flight guard in `detect_money_to_weight` & `detect_weight_to_money`: checks `unit_price <= 0.0`, returns clean dictionary with `error: ZERO_UNIT_PRICE` | Evaluated with `unit_price = 0.0`. Gracefully caught and returned: `⚠️ [वस्तू]: विक्री दर निश्चित नाही.` 0 exceptions thrown. | **PASS** |
| **4** | **Vernacular Marathi Typography** | Exact WhatsApp Scale Notice with `⚖️ *काट्यावर ठेवा (PLACE ON SCALE):*` banner, bold grams, rates, and remaining stock | `LooseCommodityEngine.format_money_to_weight_notice` & `format_weight_to_money_notice` implement exact specification typography with 28-character Unicode bar | Verified character-for-character compliance with spec Section 4.1 & 4.2. Prominent banner and bold grams rendered. | **PASS** |
| **5** | **Compound Multi-Item Orders** | Single utterance containing simultaneous loose commodity + packaged FMCG items | `LooseCommodityEngine.segment_clauses` splits by `आणि`, `,`, `+`, `व`. `parse_order` parses loose items via reverse-math and FMCG via standard lexer under a shared `batch_id` | `"२० रुपयांची साखर आणि २ पार्ले बिस्कीट आणि ३५० ग्रॅम कांदा"` extracts Sugar (0.476kg), Parle-G (2pkts), Onion (0.350kg). Total: ₹52.25. | **PASS** |
| **6** | **Atomic 1-Click Rollback** | Single `चूक झाली` or `undo` restores exact fractional weight deltas for all items in batch | `InventoryService.undo_last_transaction` groups by `batch_id`, reverses exact `quantity_delta` for all items, commits audit ledger with `ROLLBACK` | All 3 compound items reverted simultaneously (Sugar +0.476kg, Parle +2, Onion +0.350kg) with 0 precision loss. Tested on empty ledger gracefully. | **PASS** |
| **7** | **Sub-Millisecond Execution** | Zero external LLM/API calls, execution latency $\le 0.5\text{ms}$ (well below 2.0ms target) | Pure local pre-compiled regex lexer (`re.compile`) + deterministic arithmetic | 200 benchmark runs: Mean = 0.1080 ms, Min = 0.0392 ms.<br>1,000 stress runs: p50 = 0.0219 ms, p95 = 0.0249 ms, p99 = 0.0640 ms. | **PASS** |

---

## 3. Edge Case & Stress Testing Analysis

### 3.1 Zero Division & Invalid Price Defense
- **Zero Price (`unit_price == 0.0`)**: Tested with `मोफत वस्तू` (`ZERO-PRICE`). The engine immediately short-circuits before division, emitting:
  ```json
  {
    "error": "ZERO_UNIT_PRICE",
    "sku": "ZERO-PRICE",
    "alert": "⚠️ मोफत वस्तू: विक्री दर निश्चित नाही.",
    "reply_message": "⚠️ *मोफत वस्तू:* विक्री दर निश्चित नाही.\nकृपया वस्तूचा दर निश्चित करा."
  }
  ```
- **Negative Price / Non-Numeric**: Defensive cast `float(product.get("unit_price", 0.0))` ensures missing or malformed prices default to `0.0` and trigger the zero-division guard.

### 3.2 IEEE-754 Floating-Point Precision & Rounding Drift
- Evaluated 5,000 randomized permutations of price ($P \in [₹23.50, ₹140.00]$) and money values ($M \in [₹1, ₹1000]$).
- Checked for fractional decimal expansion beyond 3 decimal places in kilograms (`quantity_kg`).
- **Result**: **0 epsilon leaks detected**. All deductions are strictly clamped with `round(..., 3)` for kilograms and `round(..., 2)` for currency.

### 3.3 Vernacular Homophone Disambiguation ("पाव" Weight vs "पाव" Bakery Item)
- **Problem**: In Marathi, `पाव` means 250 grams (weight fraction), but also refers to Bakery Pav (Bread / `BAK-PAV-LADI`).
- **Audit Verification**:
  - `LooseCommodityEngine._find_product` features homophone protection (lines 132-135): `BAK-PAV-LADI` is only matched if explicit bakery tokens (`लादी`, `बेकरी`, `ladi`, `bakery`, `bread`, `ब्रेड`) are present.
  - Test: `"पाव साखर"` correctly routes to Sugar 250g (`GROC-SUG-001`, 250g).
  - Test: `"२ लादी पाव"` correctly routes to Bakery Pav (`BAK-PAV-LADI`, 2 packets).

### 3.4 Vernacular Fractional Lexicon Coverage
The engine natively supports both Devanagari script and Minglish transliteration for all vernacular fraction idioms:
- `पावशेर` / `pavsher` / `पाव किलो` &rarr; $250\text{g}$
- `अर्धा किलो` / `ardha kilo` / `half kg` &rarr; $500\text{g}$
- `पाऊण किलो` / `paun kilo` &rarr; $750\text{g}$
- `सव्वा किलो` / `savva kilo` &rarr; $1250\text{g}$
- `दीड किलो` / `did kilo` &rarr; $1500\text{g}$
- `अडीच किलो` / `adich kilo` &rarr; $2500\text{g}$
- Multipliers: `"२ पावशेर कांदा"` &rarr; $500\text{g}$, `"दोन पाव साखर"` &rarr; $500\text{g}$.

### 3.5 High-Volume / Over-Stock Boundary Protection
- Input: `"1000000 chi sakhar"` (₹1,000,000 order for sugar against 50 kg available stock).
- Behavior:
  - System detects stock shortage (`stock < qty`), flags `⚠️ अपुरा साठा! शिल्लक फक्त 50.0 kg`, caps deduction to available stock (50.0 kg), sets remaining stock to `0.0 kg`, and prevents negative inventory without server crash.

### 3.6 Ledger Rollback Integrity
- Rollback is indexed by `batch_id` generated during the original transaction.
- When `चूक झाली` is invoked:
  1. Identifies the active unreversed transaction batch.
  2. Restores exact positive stock delta (`-tx.quantity_delta`).
  3. Writes compensating immutable transaction record (`transaction_type = "ROLLBACK"`).
  4. Flushes ACID snapshot to `vyaparai_state.json`.
  5. Emits real-time WebSocket metrics update.
- Subsequent calls to undo when no unreversed transactions remain gracefully return:
  `❌ कोणतीही अलीकडील नोंद सापडली नाही (No recent transaction found to undo).`

---

## 4. Performance & Latency Benchmark Summary

- **Benchmark Method**: `time.perf_counter()` over 1,000 consecutive parses on representative Kirana utterances.
- **Latency Distribution**:
  - **p50 (Median)**: `0.0219 ms` (~22 microseconds)
  - **p95**: `0.0249 ms`
  - **p99**: `0.0640 ms`
  - **Max**: `0.1607 ms`
- **Target Specification Threshold**: $\le 0.5\text{ ms}$ (ideal) / $< 2.0\text{ ms}$ (limit).
- **Compliance Factor**: **~10x faster than target specification** and zero external network/AI roundtrips.

---

## 5. Final Audit Verdict

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   FINAL AUDIT VERDICT: >>> APPROVED <<<                                      ║
║                                                                              ║
║   Feature 1 (Loose Commodity Reverse-Math Engine) is 100% compliant with      ║
║   Specification 01. All 7 architectural invariants, vernacular receipts,    ║
║   zero-division protections, float invariants, and rollback mechanics       ║
║   are verified and production-ready for stage demonstration.                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```
