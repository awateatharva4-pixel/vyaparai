import os
from typing import List

# Safe dotenv loading from explicit project root
ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
try:
    from dotenv import load_dotenv
    if os.path.exists(ENV_PATH):
        load_dotenv(dotenv_path=ENV_PATH, override=False)
except ImportError:
    pass

# Always perform native fallback parsing to guarantee keys in .env are loaded into os.environ if not already present
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                key = k.strip()
                if key not in os.environ:
                    os.environ[key] = v.strip().strip("'\"")


class Settings:
    """
    Central Application Settings & Multi-Key API Rotation Pool.
    Designed for zero-downtime failover during high-load live demonstrations.
    """
    APP_NAME: str = "VyaparAI"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./vyaparai.db")
    
    # Meta / Twilio WhatsApp Credentials
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_NUMBER: str = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
    MERCHANT_WHATSAPP_NUMBER: str = os.getenv("MERCHANT_WHATSAPP_NUMBER", "")
    META_WEBHOOK_VERIFY_TOKEN: str = os.getenv("META_WEBHOOK_VERIFY_TOKEN", "vyaparai_hw2026_secret")
    
    # Green-API WhatsApp Gateway Credentials
    GREEN_API_HOST: str = os.getenv("GREEN_API_HOST", "https://7107.api.greenapi.com")
    GREEN_API_INSTANCE_ID: str = os.getenv("GREEN_API_INSTANCE_ID", "710722771470")
    GREEN_API_TOKEN: str = os.getenv("GREEN_API_TOKEN", "f92d0b38d8e948c494f420a4abc45493380f7657a03f445eb7")
    
    # State Persistence & Admin Security
    ADMIN_TOKEN: str = os.getenv("ADMIN_TOKEN", "vyaparai_admin_2026")
    
    # Supabase Cloud Database & Gateway
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://cxyaaffdvvsnitmyzrow.supabase.co")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "sb_publishable_eFxVztNVgKeytabZxqQ52Q_PDyq3_z0")
    
    # Dedicated Gemini Video API Key (Quota Isolation Invariant)
    GEMINI_VIDEO_API_KEY: str = os.getenv("GEMINI_VIDEO_API_KEY", "")

    # Multi-Key Rotation Pool for Google Gemini API
    _api_keys: List[str] = []
    _current_key_index: int = 0

    @classmethod
    def get_video_gemini_key(cls) -> str:
        """
        Returns dedicated video API key if configured;
        gracefully falls back to active general key pool to guarantee zero-crash execution.
        """
        key = ""
        try:
            from app.core.config import settings as _inst
            key = getattr(_inst, "GEMINI_VIDEO_API_KEY", "").strip()
        except Exception:
            pass
        if not key:
            key = getattr(cls, "GEMINI_VIDEO_API_KEY", "").strip() or os.getenv("GEMINI_VIDEO_API_KEY", "").strip()
        if key and not key.startswith("your_"):
            return key
        return cls.get_active_gemini_key()

    @classmethod
    def get_gemini_keys(cls) -> List[str]:
        if not cls._api_keys:
            keys = []
            for env_var in ["GEMINI_API_KEY", "GEMINI_API_KEY_1", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3"]:
                val = os.getenv(env_var, "").strip()
                if val and val not in keys and not val.startswith("your_"):
                    keys.append(val)
            bulk = os.getenv("GEMINI_API_KEYS", "")
            if bulk:
                for k in bulk.split(","):
                    k = k.strip()
                    if k and k not in keys:
                        keys.append(k)
            cls._api_keys = keys
        return cls._api_keys

    @classmethod
    def get_active_gemini_key(cls) -> str:
        keys = cls.get_gemini_keys()
        if not keys:
            return ""
        return keys[cls._current_key_index % len(keys)]

    @classmethod
    def rotate_gemini_key(cls) -> str:
        """Rotates to next available API key when rate limit (HTTP 429) is encountered."""
        keys = cls.get_gemini_keys()
        if not keys:
            return ""
        cls._current_key_index = (cls._current_key_index + 1) % len(keys)
        new_key = keys[cls._current_key_index]
        masked = new_key[:6] + "..." + new_key[-4:] if len(new_key) > 10 else "***"
        print(f"[FAILOVER POOL] Quota/error hit. Rotated to Gemini Key #{cls._current_key_index + 1} ({masked})")
        return new_key

    # Dual-Role Security Firewall (Specification 03)
    AUTHORIZED_MERCHANT_PHONES: set = {
        "919579869506",
        "917558455021",
        "9579869506",
        "7558455021"
    }

    @classmethod
    def is_merchant_sender(cls, sender_phone: str) -> bool:
        """
        Dual-Role Security Firewall:
        Validates whether incoming WhatsApp message originates from an authorized merchant administrator.
        Zero Privilege Escalation Invariant: Any other number is classified as Customer.
        """
        if not sender_phone:
            return False
        clean = (
            str(sender_phone)
            .replace("+", "")
            .replace("@c.us", "")
            .replace("@g.us", "")
            .replace("whatsapp:", "")
            .replace("-", "")
            .replace(" ", "")
            .strip()
        )
        return clean in cls.AUTHORIZED_MERCHANT_PHONES

settings = Settings()

# Module-level aliases for backward compatibility and clean imports
AUTHORIZED_MERCHANT_PHONES = settings.AUTHORIZED_MERCHANT_PHONES
is_merchant_sender = settings.is_merchant_sender

