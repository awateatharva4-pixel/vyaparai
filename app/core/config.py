import os
from typing import List

# Safe dotenv loading without hard dependency
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Minimal native parser for .env
    env_file = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip("'\""))

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
    META_WEBHOOK_VERIFY_TOKEN: str = os.getenv("META_WEBHOOK_VERIFY_TOKEN", "vyaparai_hw2026_secret")
    
    # Multi-Key Rotation Pool for Google Gemini API
    _api_keys: List[str] = []
    _current_key_index: int = 0

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

settings = Settings()
