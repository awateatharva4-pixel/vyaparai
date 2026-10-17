# INCIDENT POST-MORTEM & PERMANENT ENGINEERING INVARIANTS

**Project:** VyaparAI — Local Vendor Inventory Digitization via WhatsApp/SMS  
**Team:** Team Shadow (Atharva Awate & Venkatesh Pai) — HW26-F08  
**Date of Incident:** October 17, 2026  
**Status:** RESOLVED & PERMANENTLY GUARDED  

---

## 1. Executive Summary & Incident Description
During automated test runs of the 8:00 PM Daily Closing Ledger (`POST /api/reports/daily-closing`), the outbound WhatsApp service dispatched a summary message to `+1 415 523 8886` via the primary Green-API gateway (`14155238886@c.us`).

`+1 415 523 8886` is Twilio's public inbound sandbox number from California, USA. Because Green-API Free Tier grants exactly 3 free correspondent phone numbers per month, delivering an outbound message to this sandbox number consumed one of the 3 correspondent slots, contributing to `HTTP 466: CORRESPONDENTS_QUOTA_EXCEEDED`.

---

## 2. Root Cause Analysis (RCA)

1. **Config Semantics Confusion:**
   - In `app/core/config.py`, `TWILIO_WHATSAPP_NUMBER` defaults to `whatsapp:+14155238886`.
   - In Twilio architecture, `TWILIO_WHATSAPP_NUMBER` is the *sender* number (`From:`), never a recipient.
2. **Hardcoded Fallback in Inventory Service:**
   - In `app/services/inventory_service.py` (`generate_8pm_closing_summary`):
     ```python
     target_phone = settings.TWILIO_WHATSAPP_NUMBER or "whatsapp:+919579869506"
     whatsapp_sent = WhatsAppService.send_message(target_phone, message)
     ```
   - When tests triggered this function with `send_whatsapp=True`, `target_phone` resolved to `whatsapp:+14155238886`.
3. **Provider Priority Inversion:**
   - `WhatsAppService.send_message()` checks Green-API first.
   - It stripped the prefix to `14155238886@c.us` and called Green-API's `sendMessage` API.
   - Green-API attempted delivery to a Twilio bot number that cannot receive WhatsApp messages from Green-API, consuming a free correspondent slot.

---

## 3. Engineering Fixes Implemented

1. **Hard Guard in `app/services/whatsapp_service.py`:**
   ```python
   # Guard: Twilio sandbox number (+1 415 523 8886) is Twilio's system number, not a WhatsApp client.
   # Never route it to Green-API as it wastes free correspondent quotas.
   if "14155238886" in to_phone:
       print(f"[WHATSAPP GUARD]: Skipped routing Twilio Sandbox number {to_phone} to Green-API.")
   ```
2. **Recipient Parameter & Dedicated Merchant Config:**
   - `app/services/inventory_service.py` updated to accept `phone: Optional[str] = None`.
   - If not provided, it falls back to `settings.MERCHANT_WHATSAPP_NUMBER`.
   - If no valid non-sandbox number exists, WhatsApp dispatch is cleanly skipped with an explicit warning.
3. **Automated Test Quota Protection:**
   - In `test_api.py`, closing summary and Udhar reminder steps now pass `send_whatsapp=False`.
   - Automated CI/CD runs will **never** consume live WhatsApp carrier / Green-API quotas.

---

## 4. Permanent Invariants (Zero-Tolerance Rules)

- ⛔ **NEVER** route Twilio sandbox numbers (`14155238886`), mock numbers, or test sender numbers to live Green-API or Meta outbound endpoints.
- ⛔ **NEVER** call live outbound messaging services with unmocked numbers inside automated test suites (`test_api.py`, `test_system.py`, `test_red_team.py`).
- ⛔ **NEVER** treat sender credentials (`TWILIO_WHATSAPP_NUMBER`) as customer/merchant recipient numbers.
- ✅ **ALWAYS** verify Green-API correspondent count in the developer console before live judging demonstrations.

---

## 5. Current Active Configuration (Fresh Instance)
- **Host:** `https://7107.api.greenapi.com`
- **Instance ID:** `710722771470`
- **Token:** `f92d0b38d8e948c494f420a4abc45493380f7657a03f445eb7`
- **Render Webhook URL:** `https://vyaparai-oddf.onrender.com/api/v1/webhook/whatsapp`
