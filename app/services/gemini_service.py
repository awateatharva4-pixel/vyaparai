import json
import re
from typing import Dict, Any, List, Optional
from app.core.config import settings

# Optional Google GenAI SDK import
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


SYSTEM_PROMPT = """
You are VyaparAI, an expert retail NLP parser for Indian Kirana shopkeepers in Maharashtra.
Your task is to parse informal voice/text transcripts in Marathi, Hindi, Hinglish, or Minglish into a structured JSON payload.

Supported Intents:
1. "SALE": Vendor sold items (e.g., '5 साखर विकली', '2 packet parle-g dukanatun gela', 'dili', 'sold')
2. "RESTOCK": Vendor received stock from wholesale (e.g., '10 tel aale', 'aala', 'restock', 'kharidi')
3. "QUERY": Vendor asks about stock level (e.g., 'kiti sakhar ahe?', 'saatha dakhva', 'stock check')
4. "UNDO": Vendor made a mistake and wants to cancel last entry (e.g., 'chook jhali', 'radd kara', 'undo')
5. "THRESHOLD": Setting dynamic alert limits (e.g., 'sakhar threshold 25 kara')

Return ONLY valid JSON matching this schema:
{
  "intent": "SALE" | "RESTOCK" | "QUERY" | "UNDO" | "THRESHOLD",
  "items": [
    {
      "name_raw": "string (the raw vernacular item name)",
      "quantity": float (standard numeric scalar),
      "unit_raw": "string (e.g., pav, kilo, packet, pouch, ladi)",
      "normalized_unit": "kg" | "packet" | "pouch" | "ladi" | "bag" | "piece",
      "price_raw": float (optional price mentioned, or 0.0)
    }
  ],
  "vendor_note": "string (brief summary in clean Marathi/English)"
}
"""

class GeminiService:
    """
    Intelligent Vernacular Parser with:
    1. Multi-Key Round-Robin & Failover Pool.
    2. Zero-Downtime Local Rule-Based Regex Fallback Engine (runs offline & with 0 quota).
    """

    @classmethod
    def parse_transcript(cls, text: str, catalog_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        text_clean = text.strip()
        
        # Immediate check for Undo / Rollback trigger
        if any(w in text_clean.lower() for w in ["undo", "cancel", "चूक झाली", "रद्द करा", "मागे घ्या", "chuk zali", "galat"]):
            return {"intent": "UNDO", "items": [], "vendor_note": "व्यवहार रद्द करण्याची विनंती (Rollback Request)"}

        # Immediate check for Query trigger
        if any(w in text_clean.lower() for w in ["stock", "साठा", "शिल्लक", "kiti ahe", "kitna hai", "check"]):
            return {"intent": "QUERY", "items": [], "vendor_note": "साठा तपासणी विनंती (Stock Query)"}

        # Try Google Gemini API if keys and SDK are present
        active_key = settings.get_active_gemini_key()
        if GENAI_AVAILABLE and active_key:
            keys_pool = settings.get_gemini_keys()
            for attempt in range(len(keys_pool)):
                try:
                    client = genai.Client(api_key=settings.get_active_gemini_key())
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=f"Catalog Items: {[c.get('name_en') for c in catalog_items]}\nInput: {text_clean}",
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT,
                            response_mime_type="application/json",
                            temperature=0.1,
                            max_output_tokens=256
                        )
                    )
                    if response.text:
                        parsed = json.loads(response.text)
                        parsed["source"] = "gemini-2.5-flash"
                        return parsed
                except Exception as e:
                    print(f"[GEMINI FAILOVER] Attempt {attempt + 1} error: {str(e)[:100]}")
                    settings.rotate_gemini_key()

        # Deterministic Tier-0 Local Fallback Engine (Zero latency, ₹0.00 cost, works 100% offline)
        print("[AI FALLBACK] Running Deterministic Vernacular Regex Engine")
        return cls._local_regex_parser(text_clean, catalog_items)

    @classmethod
    def _local_regex_parser(cls, text: str, catalog: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sub-2ms Deterministic Indian Kirana Vernacular Parser.
        Supports Marathi, Hindi, and Minglish quantities, units, and action verbs.
        """
        lower = text.lower()
        intent = "SALE"
        if any(w in lower for w in ["aali", "aale", "aala", "aaya", "restock", "add", "bharmit", "ghetla", "ghya"]):
            intent = "RESTOCK"

        extracted_items = []
        
        # Unit and Quantity regex mapping
        unit_multipliers = {
            "पाव किलो": (0.25, "kg"),
            "पाव": (0.25, "kg"),
            "अर्धा किलो": (0.5, "kg"),
            "आधा किलो": (0.5, "kg"),
            "पाऊण किलो": (0.75, "kg"),
            "सवा किलो": (1.25, "kg"),
            "दीड किलो": (1.5, "kg"),
            "अडीच किलो": (2.5, "kg"),
            "kilo": (1.0, "kg"),
            "kg": (1.0, "kg"),
            "किलो": (1.0, "kg"),
            "packet": (1.0, "packet"),
            "पुडा": (1.0, "packet"),
            "पुडे": (1.0, "packet"),
            "पॅकेट": (1.0, "packet"),
            "pouch": (1.0, "pouch"),
            "पॉऊच": (1.0, "pouch"),
            "ladi": (1.0, "ladi"),
            "लादी": (1.0, "ladi"),
            "bag": (1.0, "bag"),
            "गोणी": (1.0, "bag"),
            "नग": (1.0, "piece")
        }

        # Check catalog matches against text
        for p in catalog:
            aliases = p.get("aliases", []) + [p.get("name_en", "").lower(), p.get("name_mr", "").lower()]
            matched = False
            for alias in aliases:
                if alias.lower() in lower:
                    matched = True
                    break
            
            if matched:
                # Find number associated with this item
                qty = 1.0
                detected_unit = p.get("unit", "kg")
                
                # Check for fractional Marathi terms first
                fraction_found = False
                word_to_num = {
                    "एक": 1.0, "दोन": 2.0, "तीन": 3.0, "चार": 4.0, "पाच": 5.0,
                    "don": 2.0, "tin": 3.0, "char": 4.0
                }
                for frac_name, (multiplier, norm_unit) in unit_multipliers.items():
                    if frac_name in text:
                        # Ensure 'पाव' as bakery item isn't confused with 'पाव' (250g)
                        if frac_name == "पाव" and p.get("sku") == "BAK-PAV-LADI":
                            continue # It's bakery pav, not 250g!
                        
                        # Check if a multiplier prefix exists (e.g. 'दोन पाव', '2 पाव')
                        prefix_match = re.search(r"(\d+(?:\.\d+)?|एक|दोन|तीन|चार|पाच|don|tin|char)\s*" + re.escape(frac_name), text, re.IGNORECASE)
                        if prefix_match:
                            pref = prefix_match.group(1).lower()
                            num_scalar = float(pref) if pref.replace('.', '', 1).isdigit() else word_to_num.get(pref, 1.0)
                            qty = num_scalar * multiplier
                        else:
                            qty = multiplier
                            
                        detected_unit = norm_unit
                        fraction_found = True
                        break


                if not fraction_found:
                    # Look for numerical digits (e.g., '5', '10.5')
                    nums = re.findall(r"(\d+(?:\.\d+)?)", text)
                    if nums:
                        qty = float(nums[0])
                
                extracted_items.append({
                    "name_raw": p.get("name_mr"),
                    "sku_matched": p.get("sku"),
                    "quantity": qty,
                    "unit_raw": detected_unit,
                    "normalized_unit": detected_unit,
                    "price_raw": p.get("unit_price", 0.0)
                })

        # If no specific catalog item was matched, extract generic numbers
        if not extracted_items:
            nums = re.findall(r"(\d+(?:\.\d+)?)", text)
            qty = float(nums[0]) if nums else 1.0
            extracted_items.append({
                "name_raw": text[:30],
                "quantity": qty,
                "unit_raw": "item",
                "normalized_unit": "item",
                "price_raw": 0.0
            })

        return {
            "intent": intent,
            "items": extracted_items,
            "source": "deterministic-vernacular-engine",
            "vendor_note": f"{intent} process completed via local vernacular pipeline"
        }
