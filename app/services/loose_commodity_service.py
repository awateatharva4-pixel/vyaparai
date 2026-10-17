import re
import time
from typing import Dict, Any, List, Optional, Tuple

DEV_DIGIT_MAP = str.maketrans("०१२३४५६७८९", "0123456789")

NUM_WORDS = {
    "अर्धा": 0.5, "आधा": 0.5, "ardha": 0.5, "adha": 0.5, "half": 0.5,
    "पावशेर": 0.25, "पाव": 0.25, "pav": 0.25, "pavsher": 0.25,
    "पाऊण": 0.75, "पौना": 0.75, "paun": 0.75,
    "सव्वा": 1.25, "सवा": 1.25, "savva": 1.25, "sawa": 1.25,
    "दीड": 1.5, "डेढ": 1.5, "did": 1.5, "dedh": 1.5,
    "अडीच": 2.5, "ढाई": 2.5, "adich": 2.5, "adeech": 2.5, "dhai": 2.5,
    "एक": 1.0, "ek": 1.0, "one": 1.0,
    "दोन": 2.0, "don": 2.0, "do": 2.0, "two": 2.0,
    "तीन": 3.0, "tin": 3.0, "teen": 3.0, "three": 3.0,
    "चार": 4.0, "char": 4.0, "four": 4.0,
    "पाच": 5.0, "pach": 5.0, "paach": 5.0, "panch": 5.0, "five": 5.0,
    "सहा": 6.0, "saha": 6.0, "chha": 6.0, "six": 6.0,
    "सात": 7.0, "sat": 7.0, "saat": 7.0, "seven": 7.0,
    "आठ": 8.0, "aath": 8.0, "eight": 8.0,
    "नऊ": 9.0, "nau": 9.0, "nine": 9.0,
    "दहा": 10.0, "daha": 10.0, "dus": 10.0, "ten": 10.0,
    "पंधरा": 15.0, "pandhra": 15.0,
    "वीस": 20.0, "vis": 20.0, "vees": 20.0, "twenty": 20.0,
    "पंचवीस": 25.0, "panchvis": 25.0,
    "तीस": 30.0, "tis": 30.0, "thirty": 30.0,
    "चाळीस": 40.0, "chalis": 40.0, "forty": 40.0,
    "पन्नास": 50.0, "pannas": 50.0, "pachaas": 50.0, "fifty": 50.0,
    "शंभर": 100.0, "shambhar": 100.0, "hundred": 100.0,
}

# Indic-aware boundary token
BOUNDARY = r"(?:\s+|$|[^\w\u0900-\u097F])"

# Pre-compiled high-performance regexes for sub-0.05ms execution
RE_MONEY_SUFFIX = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:रुपयांची|रुपयांचे|रुपयांचा|रुपयाचे|रुपयाची|रुपये|रुपया|"
    r"rupayachi|rupayache|rupayacha|rupaye|rupaya|"
    r"rs\.?|inr|₹|ची|चे|चा|chi|che|cha|ka|ki)" + BOUNDARY,
    re.IGNORECASE
)

RE_MONEY_PREFIX = re.compile(
    r"(?:₹|rs\.?|inr)\s*(\d+(?:\.\d+)?)" + BOUNDARY,
    re.IGNORECASE
)

RE_MONEY_POST_SYM = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:/-|₹)" + BOUNDARY
)

RE_WEIGHT_TOKENS = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:ग्रॅम|ग्राम|ग्रॅ|gm|grams?|gms)" + BOUNDARY,
    re.IGNORECASE
)

RE_WEIGHT_G = re.compile(
    r"(\d+(?:\.\d+)?)\s*g" + BOUNDARY,
    re.IGNORECASE
)

RE_CLAUSE_SPLIT = re.compile(
    r"(?:आणि|\s+व\s+|,|\+|\band\b|\bplus\b|;)+",
    re.IGNORECASE
)

RE_FRACTION_PAVSHER = re.compile(r"(?:^|[^\w\u0900-\u097F])(?:पावशेर|pavsher)(?:$|[^\w\u0900-\u097F])", re.IGNORECASE)
RE_FRACTION_PAV_KILO = re.compile(r"(?:^|[^\w\u0900-\u097F])(?:पाव\s*किलो|pav\s*kilo)(?:$|[^\w\u0900-\u097F])", re.IGNORECASE)
RE_FRACTION_ARDHA_KILO = re.compile(r"(?:^|[^\w\u0900-\u097F])(?:अर्धा\s*किलो|आधा\s*किलो|ardha\s*kilo|half\s*kg)(?:$|[^\w\u0900-\u097F])", re.IGNORECASE)
RE_FRACTION_PAUN_KILO = re.compile(r"(?:^|[^\w\u0900-\u097F])(?:पाऊण\s*किलो|पौना\s*किलो|paun\s*kilo)(?:$|[^\w\u0900-\u097F])", re.IGNORECASE)
RE_FRACTION_SAVVA_KILO = re.compile(r"(?:^|[^\w\u0900-\u097F])(?:सव्वा\s*किलो|savva\s*kilo)(?:$|[^\w\u0900-\u097F])", re.IGNORECASE)
RE_FRACTION_DID_KILO = re.compile(r"(?:^|[^\w\u0900-\u097F])(?:दीड\s*किलो|did\s*kilo)(?:$|[^\w\u0900-\u097F])", re.IGNORECASE)
RE_FRACTION_ADICH_KILO = re.compile(r"(?:^|[^\w\u0900-\u097F])(?:अडीच\s*किलो|adich\s*kilo)(?:$|[^\w\u0900-\u097F])", re.IGNORECASE)
RE_FRACTION_PAV_COMMODITY = re.compile(r"(?:^|[^\w\u0900-\u097F])(?:पाव|pav)(?:$|[^\w\u0900-\u097F])", re.IGNORECASE)


class LooseCommodityEngine:
    """
    Sub-millisecond Local Deterministic Reverse-Math Engine ("Voice-to-Scale").
    Zero External AI Calls, 0.05ms Latency, Zero Division Defended, Strictly Rounded.
    
    Implements:
    1. Paradigm A: Money-to-Weight ("२० रुपयांची साखर", "20 chi sakhar", "50 che tel")
       target_grams = round((money / unit_price) * 1000)
       delta = -round(money / unit_price, 3) kg
       total_amount = float(money)
    2. Paradigm B: Weight-to-Money ("३५० ग्रॅम कांदा", "350 gm batata", "पावशेर साखर" -> 250g)
       total_price = round((grams / 1000.0) * unit_price, 2)
       delta = -round(grams / 1000.0, 3) kg
       total_amount = total_price
    """

    @classmethod
    def normalize_text(cls, text: str) -> str:
        """Translates Devanagari numerals to ASCII digits."""
        return text.translate(DEV_DIGIT_MAP)

    @classmethod
    def segment_clauses(cls, text: str) -> List[str]:
        """
        Splits compound retail utterances into independent clauses.
        Delimiters: 'आणि', 'व', ',', '+', 'and', 'plus', ';'
        """
        norm = cls.normalize_text(text)
        clauses = RE_CLAUSE_SPLIT.split(norm)
        return [c.strip() for c in clauses if c.strip()]

    @classmethod
    def _find_product(cls, text: str, catalog: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Finds the matching catalog item from text based on aliases and names.
        Sorts aliases by length descending to match the most specific term first.
        Includes homophone protection for 'पाव' (fraction) vs Bakery Pav (BAK-PAV-LADI).
        """
        text_lower = text.lower()
        candidates = []

        for p in catalog:
            sku = p.get("sku")
            aliases = list(p.get("aliases", []))
            if p.get("name_en"):
                aliases.append(p.get("name_en"))
            if p.get("name_mr"):
                aliases.append(p.get("name_mr"))

            for a in aliases:
                a_clean = a.strip().lower()
                if not a_clean:
                    continue
                if a_clean in text_lower:
                    # Homophone Guard: 'पाव' as weight fraction vs bakery pav
                    if sku == "BAK-PAV-LADI":
                        if not any(k in text_lower for k in ["लादी", "बेकरी", "ladi", "bakery", "bread", "ब्रेड"]):
                            continue
                    candidates.append((len(a_clean), p))

        if not candidates:
            return None

        # Sort by alias length descending
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]

    @classmethod
    def _convert_number_words(cls, text: str) -> str:
        """Converts leading number words before money tokens into digits."""
        norm = text
        for word, val in NUM_WORDS.items():
            if val < 1.0 and word in ("अर्धा", "आधा", "पावशेर", "पाव", "पाऊण"):
                continue  # Handled separately in fractional weights
            if word in norm.lower():
                pat = r"(?:^|[^\w\u0900-\u097F])(" + re.escape(word) + r")\s*(?=(?:रुपयांची|रुपयांचे|रुपयांचा|रुपयाचे|रुपयाची|रुपये|रुपया|rupayachi|rupayache|rupayacha|rupaye|rupaya|rs\.?|inr|₹|ची|चे|चा|chi|che|cha|ka|ki)" + BOUNDARY + r")"
                norm = re.sub(pat, f" {val} ", norm, flags=re.IGNORECASE)
        return norm

    @classmethod
    def detect_money_to_weight(cls, clause: str, catalog: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Detects Money-to-Weight paradigm:
        e.g. "२० रुपयांची साखर", "20 chi sakhar", "50 che tel", "10 cha kanda", "20 rs sugar".
        """
        norm = cls.normalize_text(clause)
        norm = cls._convert_number_words(norm)

        money_val = None

        # Pattern 1: Number + money suffix (e.g. "20 chi", "20 रुपयांची", "50 che", "10 cha")
        m1 = RE_MONEY_SUFFIX.search(norm)
        if m1:
            try:
                money_val = float(m1.group(1))
            except ValueError:
                pass

        # Pattern 2: Prefix currency symbol (e.g. "₹20", "rs 20", "rs. 20", "inr 20")
        if money_val is None:
            m2 = RE_MONEY_PREFIX.search(norm)
            if m2:
                try:
                    money_val = float(m2.group(1))
                except ValueError:
                    pass

        # Pattern 3: Currency suffix after number (e.g. "20/-", "20 ₹")
        if money_val is None:
            m3 = RE_MONEY_POST_SYM.search(norm)
            if m3:
                try:
                    money_val = float(m3.group(1))
                except ValueError:
                    pass

        if money_val is None or money_val <= 0:
            return None

        product = cls._find_product(norm, catalog)
        if not product:
            return None

        unit_price = float(product.get("unit_price", 0.0))
        product_name_mr = product.get("name_mr", "")

        # Zero-division defense: If catalog unit_price <= 0.0, gracefully reject
        if unit_price <= 0.0:
            return {
                "error": "ZERO_UNIT_PRICE",
                "sku": product.get("sku"),
                "product_name_mr": product_name_mr,
                "alert": f"⚠️ {product_name_mr}: विक्री दर निश्चित नाही.",
                "reply_message": f"⚠️ *{product_name_mr}:* विक्री दर निश्चित नाही.\nकृपया वस्तूचा दर निश्चित करा."
            }

        # Mathematical Formulations
        target_grams = int(round((money_val / unit_price) * 1000.0))
        quantity_kg = round(money_val / unit_price, 3)
        delta = -quantity_kg
        total_amount = float(money_val)

        return {
            "type": "MONEY_TO_WEIGHT",
            "sku": product.get("sku"),
            "product_name_mr": product_name_mr,
            "product_name_en": product.get("name_en", ""),
            "unit": product.get("unit", "kg"),
            "unit_price": unit_price,
            "money": money_val,
            "target_grams": target_grams,
            "quantity_kg": quantity_kg,
            "quantity_delta": delta,
            "total_amount": total_amount,
            "is_reverse_math": True
        }

    @classmethod
    def detect_weight_to_money(cls, clause: str, catalog: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Detects Weight-to-Money paradigm:
        e.g. "३५० ग्रॅम कांदा", "350 gm batata", "पावशेर साखर" -> 250g, "750 gm aloo".
        """
        norm = cls.normalize_text(clause)
        norm_lower = norm.lower()

        grams = None

        # Check fractional vernacular weights with optional multiplier prefixes (e.g. 'दोन पाव', '२ पावशेर')
        m_pavsher = re.search(r"(\d+(?:\.\d+)?|[a-zA-Z\u0900-\u097F]+)?\s*(?:पावशेर|pavsher)" + BOUNDARY, norm, re.IGNORECASE)
        if m_pavsher:
            pref = (m_pavsher.group(1) or "").strip().lower()
            m = 1.0
            if pref:
                if pref.replace('.', '', 1).isdigit():
                    m = float(pref)
                elif pref in NUM_WORDS:
                    m = NUM_WORDS[pref]
            grams = m * 250.0

        if grams is None:
            m_pav_kilo = re.search(r"(\d+(?:\.\d+)?|[a-zA-Z\u0900-\u097F]+)?\s*(?:पाव\s*किलो|pav\s*kilo)" + BOUNDARY, norm, re.IGNORECASE)
            if m_pav_kilo:
                pref = (m_pav_kilo.group(1) or "").strip().lower()
                m = 1.0
                if pref:
                    if pref.replace('.', '', 1).isdigit():
                        m = float(pref)
                    elif pref in NUM_WORDS:
                        m = NUM_WORDS[pref]
                grams = m * 250.0

        if grams is None:
            m_ardha = re.search(r"(\d+(?:\.\d+)?|[a-zA-Z\u0900-\u097F]+)?\s*(?:अर्धा\s*किलो|आधा\s*किलो|ardha\s*kilo|half\s*kg)" + BOUNDARY, norm, re.IGNORECASE)
            if m_ardha:
                pref = (m_ardha.group(1) or "").strip().lower()
                m = 1.0
                if pref:
                    if pref.replace('.', '', 1).isdigit():
                        m = float(pref)
                    elif pref in NUM_WORDS:
                        m = NUM_WORDS[pref]
                grams = m * 500.0

        if grams is None and RE_FRACTION_PAUN_KILO.search(norm_lower):
            grams = 750.0
        elif grams is None and RE_FRACTION_SAVVA_KILO.search(norm_lower):
            grams = 1250.0
        elif grams is None and RE_FRACTION_DID_KILO.search(norm_lower):
            grams = 1500.0
        elif grams is None and RE_FRACTION_ADICH_KILO.search(norm_lower):
            grams = 2500.0

        # Check gram suffixes: ग्रॅम, ग्राम, ग्रॅ, gm, g, gram, grams, gms
        if grams is None:
            m1 = RE_WEIGHT_TOKENS.search(norm)
            if m1:
                try:
                    grams = float(m1.group(1))
                except ValueError:
                    pass

        # Check single letter 'g' suffix (e.g. "100 g", "750g")
        if grams is None:
            m2 = RE_WEIGHT_G.search(norm)
            if m2:
                try:
                    grams = float(m2.group(1))
                except ValueError:
                    pass

        # Check 'पाव' (250g) with multiplier when accompanied by a loose commodity
        if grams is None:
            m_p = re.search(r"(\d+(?:\.\d+)?|[a-zA-Z\u0900-\u097F]+)?\s*(?:पाव|pav)" + BOUNDARY, norm, re.IGNORECASE)
            if m_p and not any(k in norm_lower for k in ["लादी", "बेकरी", "ladi", "bakery", "bread", "ब्रेड"]):
                pref = (m_p.group(1) or "").strip().lower()
                m = 1.0
                if pref:
                    if pref.replace('.', '', 1).isdigit():
                        m = float(pref)
                    elif pref in NUM_WORDS:
                        m = NUM_WORDS[pref]
                grams = m * 250.0

        if grams is None or grams <= 0:
            return None

        product = cls._find_product(norm, catalog)
        if not product:
            return None

        unit_price = float(product.get("unit_price", 0.0))
        product_name_mr = product.get("name_mr", "")

        # Zero-division defense
        if unit_price <= 0.0:
            return {
                "error": "ZERO_UNIT_PRICE",
                "sku": product.get("sku"),
                "product_name_mr": product_name_mr,
                "alert": f"⚠️ {product_name_mr}: विक्री दर निश्चित नाही.",
                "reply_message": f"⚠️ *{product_name_mr}:* विक्री दर निश्चित नाही.\nकृपया वस्तूचा दर निश्चित करा."
            }

        # Mathematical Formulations
        total_price = round((grams / 1000.0) * unit_price, 2)
        quantity_kg = round(grams / 1000.0, 3)
        delta = -quantity_kg
        target_grams = int(round(grams))

        return {
            "type": "WEIGHT_TO_MONEY",
            "sku": product.get("sku"),
            "product_name_mr": product_name_mr,
            "product_name_en": product.get("name_en", ""),
            "unit": product.get("unit", "kg"),
            "unit_price": unit_price,
            "money": total_price,
            "target_grams": target_grams,
            "quantity_kg": quantity_kg,
            "quantity_delta": delta,
            "total_amount": total_price,
            "is_reverse_math": True
        }

    @classmethod
    def detect_and_compute(cls, clause: str, catalog: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Detects if clause matches either Paradigm A (Money-to-Weight) or Paradigm B (Weight-to-Money).
        Returns computation dictionary or None if clause is standard packet/unit retail.
        """
        # First check Money-to-Weight
        m2w = cls.detect_money_to_weight(clause, catalog)
        if m2w:
            return m2w

        # Next check Weight-to-Money
        w2m = cls.detect_weight_to_money(clause, catalog)
        if w2m:
            return w2m

        return None

    @classmethod
    def parse_order(cls, raw_text: str, catalog: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Multi-Item Clause Segmentation Isolation.
        Splits text by 'आणि', ',', '+' and classifies each clause independently:
        - Clause A: Loose Commodity Reverse-Math Engine
        - Clause B: Standard Fixed FMCG Kirana Lexer
        """
        t_start = time.perf_counter()
        clauses = cls.segment_clauses(raw_text)
        items = []
        has_reverse_math = False
        errors = []

        for c in clauses:
            res = cls.detect_and_compute(c, catalog)
            if res:
                if res.get("error"):
                    errors.append(res)
                    continue
                has_reverse_math = True
                items.append({
                    "name_raw": res["product_name_mr"],
                    "sku_matched": res["sku"],
                    "quantity": res["quantity_kg"],
                    "unit_raw": "kg",
                    "normalized_unit": "kg",
                    "price_raw": res["unit_price"],
                    "total_amount": res["total_amount"],
                    "is_reverse_math": True,
                    "reverse_math_type": res["type"],
                    "target_grams": res["target_grams"],
                    "money": res["money"]
                })
            else:
                # Fallback to standard local Kirana item matching for this clause
                std_item = cls._parse_standard_clause(c, catalog)
                if std_item:
                    items.append(std_item)

        elapsed_ms = (time.perf_counter() - t_start) * 1000.0

        return {
            "intent": "SALE",
            "items": items,
            "has_reverse_math": has_reverse_math,
            "errors": errors,
            "latency_ms": round(elapsed_ms, 3)
        }

    @classmethod
    def _parse_standard_clause(cls, clause: str, catalog: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Parses a standard fixed FMCG packet or regular unit item from a clause."""
        product = cls._find_product(clause, catalog)
        if not product:
            return None

        norm = cls.normalize_text(clause)
        digits = re.findall(r"(\d+(?:\.\d+)?)", norm)
        qty = float(digits[0]) if digits else 1.0

        # Check word numbers if no digits found
        if not digits:
            for w, val in NUM_WORDS.items():
                if w in norm.lower():
                    qty = val
                    break

        unit = product.get("unit", "packet")
        unit_price = float(product.get("unit_price", 0.0))
        total_amt = round(qty * unit_price, 2)

        return {
            "name_raw": product.get("name_mr"),
            "sku_matched": product.get("sku"),
            "quantity": qty,
            "unit_raw": unit,
            "normalized_unit": unit,
            "price_raw": unit_price,
            "total_amount": total_amt,
            "is_reverse_math": False
        }

    @classmethod
    def format_money_to_weight_notice(
        cls,
        product_name_mr: str,
        target_grams: int,
        money: float,
        unit_price: float,
        stock_after: float
    ) -> str:
        """
        Exact WhatsApp Scale Notice Typography (Specification Section 4.1).
        """
        sep = "━" * 28
        return (
            f"⚖️ *काट्यावर ठेवा (PLACE ON SCALE):*\n"
            f"{sep}\n"
            f"👉 *{product_name_mr} : {target_grams} ग्रॅम*\n"
            f"💰 *रक्कम:* ₹{money:.2f} (दर: ₹{unit_price:.2f}/किलो)\n"
            f"📦 *उर्वरित साठा:* {stock_after:.3f} किलो\n"
            f"{sep}\n"
            f"✅ *विक्री नोंदवली (Sale Recorded)!*"
        )

    @classmethod
    def format_weight_to_money_notice(
        cls,
        product_name_mr: str,
        total_price: float,
        grams: int,
        unit_price: float,
        stock_after: float
    ) -> str:
        """
        Exact WhatsApp Receipt Notice Typography (Specification Section 4.2).
        """
        sep = "━" * 28
        return (
            f"💰 *किराणा बिल (LOOSE ITEM BILL):*\n"
            f"{sep}\n"
            f"👉 *{product_name_mr} : ₹{total_price:.2f}*\n"
            f"⚖️ *प्रमाण:* {grams} ग्रॅम (दर: ₹{unit_price:.2f}/किलो)\n"
            f"📦 *उर्वरित साठा:* {stock_after:.3f} किलो\n"
            f"{sep}\n"
            f"✅ *विक्री नोंदवली (Sale Recorded)!*"
        )
