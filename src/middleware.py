# ===================================================================
# middleware.py - MAJBURIY OBUNA (global enforcement)
# Har bir kiruvchi xabar va callback'da obuna tekshiriladi.
# Obuna bo'lmagan foydalanuvchi faqat /start va /lang ni ko'rishi mumkin;
# qolgan tugmalar/menyular BLOKLANIB obuna ko'rsatmasi yuboriladi.
# Kanal(lar) sozlanmagan bo'lsa (settings["channels"] bo'sh) hech narsa bloklanmaydi.
# ===================================================================

from __future__ import annotations

import time

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from src.handlers._helpers import is_subscribed_all, send_subscribe_prompt
from src.i18n import t

# Obuna ko'rsatmasini yuborish oralig'i (spam oldini olish)
_PROMPT_TTL = 120.0
_last_prompt: dict[int, float] = {}

# Bu buyruqlar obuna TALABQILINMAYDI (natijada obuna ko'rsatmasi chiqadi)
_PASS_MESSAGES = ("/start", "/lang", "/help")
# Bu callback'lar doim o'tadi (o'zlari obuna holatini boshqaradi)
_PASS_CALLBACKS = ("check:sub", "lang:", "menu:main")


def _maybe_prompt(user_id: int) -> bool:
    """Obuna ko'rsatmasi yuborish kerakmi (so'nggi marta ko'rsatilganidan keyin)."""
    now = time.monotonic()
    last = _last_prompt.get(user_id, 0.0)
    if now - last < _PROMPT_TTL:
        return False
    _last_prompt[user_id] = now
    return True


class SubscriptionMiddleware(BaseMiddleware):
    """Majburiy obunani HAR BIR amalda majburlaydi (global)."""

    async def __call__(self, handler, event, data):  # noqa: ANN001
        app = data.get("app")
        user = getattr(event, "from_user", None)

        # App yoki user yo'q bo'lsa (sistem xabarlar) — o'tkazib yuboramiz
        if app is None or user is None:
            return await handler(event, data)

        # Adminlar doim o'tadi
        try:
            if await app.is_admin(user.id):
                return await handler(event, data)
        except Exception:  # noqa: BLE001
            pass

        # /start, /lang, /help — obuna ko'rsatmasi uchun ruxsat
        if isinstance(event, Message):
            text = (event.text or "").strip()
            if text.startswith("/") and any(
                text == cmd or text.startswith(cmd + " ")
                or text.startswith(cmd + "@") for cmd in _PASS_MESSAGES
            ):
                return await handler(event, data)

        # check:sub / lang: / menu:main — o'tkazamiz (o'zlari tekshiradi)
        if isinstance(event, CallbackQuery):
            cb_data = event.data or ""
            if any(cb_data == p or cb_data.startswith(p) for p in _PASS_CALLBACKS):
                return await handler(event, data)

        # Kanal(lar) sozlanmagan bo'lsa — hech narsa bloklanmaydi
        channels = await app.settings.get_channels()
        if not channels:
            return await handler(event, data)

        bot = data.get("bot") or getattr(event, "bot", None)
        if bot is None:
            return await handler(event, data)

        try:
            subscribed = await is_subscribed_all(bot, user.id, channels)
        except Exception:  # noqa: BLE001
            return await handler(event, data)

        if subscribed:
            return await handler(event, data)

        # ---- Obuna yo'q: bloklab, ko'rsatma yuborish ----
        lang = (await app.users.get(user.id) or {}).get("language", "uz")
        if isinstance(event, CallbackQuery):
            try:
                await event.answer(t(lang, "subscribe_alert"), show_alert=True)
            except Exception:  # noqa: BLE001
                pass
        if _maybe_prompt(user.id):
            await send_subscribe_prompt(bot, app, user.id, lang, channels)
        return None
