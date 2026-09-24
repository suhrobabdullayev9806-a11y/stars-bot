# ===================================================================
# config.py - Bot konfiguratsiyasi
# .env faylidan (yoki muhit o'zgaruvchilaridan) barcha sozlamalarni
# yuklaydi. Pydantic orqali tiplar va qiymatlar tekshiriladi.
# ===================================================================

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

# .env faylini loyiha ildizidan yuklash
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class Settings(BaseModel):
    """Barcha bot sozlamalari bitta joyda to'plangan."""

    # --- Asosiy ---
    bot_token: str = Field(min_length=5)
    admin_ids: list[int]
    super_admin_id: int

    # --- Majburiy obuna kanali ---
    required_channel: str = ""
    required_channel_id: int | None = None

    # --- To'lovlar ---
    payments_provider_token: str = ""
    payment_card: str = ""

    # --- API (@Apilarimbot) ---
    stars_api_base_url: str = ""
    stars_api_key: str = ""
    api_callback_secret: str = ""

    # --- Ma'lumotlar bazasi ---
    db_path: str = "data/stars.db"

    # --- WebApp ---
    webapp_host: str = "0.0.0.0"
    webapp_port: int = 8080
    # Mini-App/Buy WebApp ochiladigan OMMAVIY https URL (mijozlarga
    # web_app tugmasi orqali beriladi). Masalan: https://bot.example.com
    webapp_base_url: str = ""

    # Dastlabki narxlar (adminga ularni o'zgartirishga ruxsat bor)
    default_prices: dict[int, float] = Field(
        default_factory=lambda: {15: 3.0, 30: 5.0, 50: 8.0, 100: 15.0}
    )
    # Vositachi foizi (baholash/foiz: narxni hisoblashda)
    default_percent: float = 0.0

    def is_super_admin(self, user_id: int) -> bool:
        """Super admin (barcha huquqlar) ekanligini tekshiradi."""
        return user_id == self.super_admin_id

    def is_admin(self, user_id: int) -> bool:
        """Foydalanuvchi adminlar ro'yxatida ekanligini tekshiradi."""
        return user_id in self.admin_ids or self.is_super_admin(user_id)

    @field_validator("admin_ids", mode="before")
    @classmethod
    def _parse_admin_ids(cls, value: object) -> list[int]:
        """ADMIN_IDS='u1,u2' kabi stringni listga aylantiradi."""
        if isinstance(value, str):
            return [int(x.strip()) for x in value.split(",") if x.strip()]
        if isinstance(value, (list, tuple)):
            return [int(x) for x in value]
        return []

    @classmethod
    def from_env(cls) -> "Settings":
        """Muhit o'zgaruvchilaridan Settings obyektini quradi."""
        token = os.getenv("BOT_TOKEN", "")
        if not token:
            raise RuntimeError("BOT_TOKEN muhit o'zgaruvchisi belgilanmagan!")
        admin_ids = os.getenv("ADMIN_IDS", "")
        super_admin = os.getenv("SUPER_ADMIN_ID", "")
        if not admin_ids:
            raise RuntimeError("ADMIN_IDS muhit o'zgaruvchisi bo'sh!")

        channel = os.getenv("REQUIRED_CHANNEL", "").lstrip("@").strip()
        channel_id = os.getenv("REQUIRED_CHANNEL_ID", "").strip()
        return cls(
            bot_token=token,
            admin_ids=[int(x) for x in admin_ids.split(",") if x.strip()],
            super_admin_id=int(super_admin) if super_admin else 0,
            required_channel=channel,
            required_channel_id=int(channel_id) if channel_id else None,
            payments_provider_token=os.getenv("PAYMENTS_PROVIDER_TOKEN", ""),
            payment_card=os.getenv("PAYMENT_CARD", ""),
            stars_api_base_url=os.getenv("STARS_API_BASE_URL", ""),
            stars_api_key=os.getenv("STARS_API_KEY", ""),
            api_callback_secret=os.getenv("API_CALLBACK_SECRET", ""),
            db_path=os.getenv("DB_PATH", "data/stars.db"),
            webapp_host=os.getenv("WEBAPP_HOST", "0.0.0.0"),
            webapp_port=int(os.getenv("WEBAPP_PORT", "8080")),
            webapp_base_url=os.getenv("WEBAPP_BASE_URL", "").rstrip("/"),
            default_percent=float(os.getenv("DEFAULT_PERCENT", "0")),
        )


def load_settings() -> Settings:
    """Yagona Settings instansiyasini qaytaradi (singleton)."""
    if not hasattr(load_settings, "_cache"):
        load_settings._cache = Settings.from_env()
    return load_settings._cache