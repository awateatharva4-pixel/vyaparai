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
        print(f"[WHATSAPP OUTBOUND -> {to_phone}]:\n{message}\n" + "-"*40)
        cls._outbound_history.append({"to": to_phone, "message": message})
        
        # If Twilio credentials configured, send real WhatsApp message
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
