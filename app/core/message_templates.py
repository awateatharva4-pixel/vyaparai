"""
Pre-defined Vernacular Message Template Catalog (Slide 3 & Security Specification).
Strict Zero-Hallucination Invariant:
Gemini API ONLY performs extraction and outputs structured JSON schemas.
All customer-facing and merchant-facing messages are rendered through these
deterministic, hardened templates. Gemini NEVER crafts free-form messages.
"""

from typing import List, Dict, Any, Optional

class MessageTemplates:
    """Deterministic message rendering engine for VyaparAI."""

    @staticmethod
    def customer_confirmation_request(
        customer_name: str,
        items: List[Dict[str, Any]],
        total_amount: float,
        order_id: str,
        reservation_mins: int = 30
    ) -> str:
        """Sent to customer upon initial order receipt to confirm items and hold stock."""
        available_lines = []
        missing_lines = []
        for it in items:
            name = it.get("name_mr") or it.get("name") or it.get("name_raw") or "सामान"
            qty = it.get("quantity") or it.get("qty") or 1.0
            unit = it.get("unit") or "piece"
            price = it.get("unit_price") or it.get("price") or 0.0
            tot = it.get("line_total") or it.get("total") or (qty * price)
            if it.get("is_available", True):
                available_lines.append(f"  • {name}: {qty:g} {unit} (₹{tot:g})")
            else:
                missing_lines.append(f"  • {name}: {qty:g} {unit} (सध्या उपलब्ध नाही / Out of stock)")

        items_str = "\n".join(available_lines) if available_lines else "  • सर्व किराणा सामान"
        missing_str = ""
        if missing_lines:
            missing_str = "\n\n⚠️ *खालील वस्तू सध्या उपलब्ध नाहीत:*\n" + "\n".join(missing_lines)

        return (
            f"🙏 *नमस्कार {customer_name}! बाबुराव किराणा स्टोअर्स* 🏪\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"आपली ऑर्डर नोंदवली असून *{reservation_mins} मिनिटांसाठी साठा आरक्षित (Reserved)* केला आहे:\n\n"
            f"{items_str}{missing_str}\n\n"
            f"💰 *एकूण अंदाजे रक्कम:* ₹{total_amount:g}\n"
            f"📦 *ऑर्डर क्रमांक:* `{order_id}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👉 *ऑर्डर नक्की करण्यासाठी 'हो' किंवा 'Confirm' पाठवा.*\n"
            f"काही बदल असल्यास मेसेज पाठवा."
        )

    @staticmethod
    def customer_order_confirmed(
        customer_name: str,
        order_id: str,
        total_amount: float
    ) -> str:
        """Sent to customer after they confirm their order."""
        return (
            f"✅ *ऑर्डर निश्चित झाली (Order Confirmed)!* 🏪\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"प्रिय {customer_name}, आपली ऑर्डर `{order_id}` (₹{total_amount:g}) दुकानदाराकडे पाठवली आहे.\n"
            f"सामान पॅक झाल्यावर आपणास लगेच कळवले जाईल. धन्यवाद!"
        )

    @staticmethod
    def merchant_new_order_alert(
        customer_name: str,
        customer_phone: str,
        items: List[Dict[str, Any]],
        total_amount: float,
        order_id: str,
        stock_already_reserved: bool = True
    ) -> str:
        """High-priority alert sent directly to Merchant Phone (9579869506)."""
        item_lines = []
        for it in items:
            name = it.get("name_mr") or it.get("name") or it.get("name_raw") or "सामान"
            qty = it.get("quantity") or it.get("qty") or 1.0
            unit = it.get("unit") or "piece"
            item_lines.append(f"  • {name}: {qty:g} {unit}")

        items_str = "\n".join(item_lines) if item_lines else "  • किराणा यादी"
        res_note = "✅ *साठा तात्काळ डॅशबोर्डवरून वजा (Reserved) केला आहे!*" if stock_already_reserved else ""

        return (
            f"🔔 *नवीन ग्राहक ऑर्डर आली आहे!* 🏪\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *ग्राहक:* {customer_name}\n"
            f"📞 *फोन:* {customer_phone}\n"
            f"📝 *सामान यादी:*\n{items_str}\n\n"
            f"💰 *एकूण बिल:* ₹{total_amount:g}\n"
            f"📦 *ऑर्डर आयडी:* `{order_id}`\n"
            f"{res_note}\n\n"
            f"⏳ *३० मिनिटांचा कालावधी:* अर्ध्या तासात डॅशबोर्डवर 'Pack & Fulfill' करा अन्यथा साठा पुन्हा जमा (Auto-Undo) होईल."
        )

    @staticmethod
    def merchant_half_hour_warning(
        customer_name: str,
        order_id: str,
        remaining_mins: int = 5
    ) -> str:
        """Sent to merchant when order is nearing 30-min expiration."""
        return (
            f"⚠️ *ऑर्डर मुदत संपत आली आहे (Reminder)!* ⏳\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"ग्राहक: *{customer_name}* (ऑर्डर `{order_id}`)\n"
            f"अजूनही प्रलंबित आहे. पुढील *{remaining_mins} मिनिटांत* पॅक न केल्यास ऑर्डर रद्द होऊन माल पुन्हा उपलब्ध साठ्यात जोडला जाईल."
        )

    @staticmethod
    def merchant_auto_cancel_rollback_alert(
        customer_name: str,
        order_id: str,
        restored_items: List[Dict[str, Any]]
    ) -> str:
        """Sent to merchant when 30 minutes expire without response, confirming stock restitution."""
        restored_lines = []
        for it in restored_items:
            name = it.get("name_mr") or it.get("name") or "सामान"
            qty = it.get("quantity") or it.get("qty") or 1.0
            unit = it.get("unit") or "piece"
            restored_lines.append(f"  • {name}: +{qty:g} {unit} साठ्यात पुन्हा जोडले")

        restored_str = "\n".join(restored_lines) if restored_lines else "  • साठा पूर्ववत केला"

        return (
            f"🔄 *३० मिनिटे पूर्ण: ऑर्डर रद्द व साठा पूर्ववत (Auto-Undo)!* 📦\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"ग्राहक *{customer_name}* यांची ऑर्डर `{order_id}` ३० मिनिटांत पूर्ण न झाल्याने रद्द केली आहे.\n\n"
            f"🔄 *पुन्हा जोडलेला साठा:*\n{restored_str}\n\n"
            f"डॅशबोर्डवर उपलब्ध साठा पूर्ववत अद्ययावत झाला आहे."
        )

    @staticmethod
    def merchant_low_stock_quota_alert(
        product_name: str,
        current_stock: float,
        threshold: float,
        unit: str,
        category: str = "GROCERY"
    ) -> str:
        """Sent to merchant whenever stock reaches or drops below low-stock quota (e.g. Sugar <= 15kg)."""
        icon = "🥛" if "dairy" in category.lower() else "🚨"
        return (
            f"{icon} *कमी साठा इशारा (Low Stock Alert)!* ⚠️\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"वस्तू: *{product_name}*\n"
            f"सद्य शिल्लक साठा: *{current_stock:g} {unit}*\n"
            f"किमान मर्यादा (Quota): *{threshold:g} {unit}*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"कृपया तात्काळ नवीन साठा मागवा (Restock Required)."
        )

    @staticmethod
    def merchant_dairy_alert(
        product_name: str,
        current_stock: float,
        unit: str,
        reason: str = "LOW_STOCK"
    ) -> str:
        """Specialized alert for perishable dairy products (Amul Taaza milk, Curd, Paneer)."""
        return (
            f"🥛 *डेअरी उत्पादन इशारा (Dairy Stock Alert)!* ❄️\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"वस्तू: *{product_name}*\n"
            f"शिल्लक पाकिटे: *{current_stock:g} {unit}*\n"
            f"टीप: नाशवंत डेअरी साठ्यावर लक्ष ठेवा. संपत आल्यास नवीन सप्लाय मागवा."
        )
