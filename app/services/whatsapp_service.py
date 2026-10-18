import requests
from app.core.config import settings

class WhatsAppService:
    """
    Outbound WhatsApp Messaging Service.
    Supports Twilio WhatsApp Sandbox, Meta Cloud API, and local on-screen test bench fallback.
    """
    _outbound_history = []

    @classmethod
    def send_message(cls, to_phone: str, message: str) -> bool:
        try:
            print(f"[WHATSAPP OUTBOUND -> {to_phone}]:\n{message}\n" + "-"*40)
        except Exception:
            pass
        cls._outbound_history.append({"to": to_phone, "message": message})
        
        # 1. Green API Outbound (Direct Native WhatsApp Delivery)
        # Guard: Twilio sandbox number (+1 415 523 8886) is Twilio's system number, not a WhatsApp client.
        # Never route it to Green-API as it wastes free correspondent quotas.
        if "14155238886" in to_phone:
            print(f"[WHATSAPP GUARD]: Skipped routing Twilio Sandbox number {to_phone} to Green-API.")
        elif settings.GREEN_API_HOST and settings.GREEN_API_INSTANCE_ID and settings.GREEN_API_TOKEN:
            try:
                chat_id = to_phone
                if not chat_id.endswith("@c.us") and not chat_id.endswith("@g.us"):
                    clean_num = to_phone.replace("whatsapp:", "").replace("+", "").replace(" ", "").strip()
                    chat_id = f"{clean_num}@c.us"
                url = f"{settings.GREEN_API_HOST}/waInstance{settings.GREEN_API_INSTANCE_ID}/sendMessage/{settings.GREEN_API_TOKEN}"
                payload = {"chatId": chat_id, "message": message}
                r = requests.post(url, json=payload, timeout=5)
                if r.status_code == 200:
                    print(f"[GREEN API SUCCESS]: Delivered directly to {chat_id}")
                    return True
                else:
                    print(f"[GREEN API WARN]: Status {r.status_code} - {r.text}")
                    # If correspondent quota exceeded (Free tier 3-number limit) and recipient is customer,
                    # forward the customer receipt to merchant phone (919579869506) so nothing is lost!
                    if r.status_code == 466 and "9579869506" not in chat_id:
                        fallback_chat = "919579869506@c.us"
                        fallback_msg = (
                            f"📱 *[ग्राहक प्रत - Customer Receipt]*\n"
                            f"👤 *ग्राहक:* {to_phone} (व्यंकटेश पै)\n"
                            f"⚠️ *(Green-API फ्री कोटा मर्यादा: ग्राहक पावती मर्चंटकडे फॉरवर्ड केली आहे)*\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"{message}"
                        )
                        fb_payload = {"chatId": fallback_chat, "message": fallback_msg}
                        try:
                            r_fb = requests.post(url, json=fb_payload, timeout=5)
                            if r_fb.status_code == 200:
                                print(f"[GREEN API FALLBACK SUCCESS]: Forwarded customer copy to {fallback_chat}")
                                return True
                        except Exception as fb_err:
                            print(f"[GREEN API FALLBACK ERROR]: {fb_err}")
            except Exception as e:
                print(f"[GREEN API ERROR]: {e}")

        # 2. Twilio WhatsApp Outbound (Fallback)
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            try:
                url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
                target = to_phone if to_phone.startswith("whatsapp:") else f"whatsapp:{to_phone}"
                data = {
                    "From": settings.TWILIO_WHATSAPP_NUMBER,
                    "To": target,
                    "Body": message
                }
                r = requests.post(url, data=data, auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN), timeout=5)
                return r.status_code in (200, 201)
            except Exception as e:
                print(f"[TWILIO ERROR]: {e}")
                return False
        return True

    @classmethod
    def get_recent_messages(cls, limit: int = 5):
        return cls._outbound_history[-limit:]
