# ===================================================================
# handlers - Telegram xabarlarini qayta ishlovchi paket
# Har bir funksional o'z router'iga ega; main.py ularni yig'adi.
# ===================================================================

from __future__ import annotations

from aiogram import Dispatcher

from src.handlers import admin, buy, extras, gift_flow, post_stars, referral, start, wallet


def register_handlers(dp: Dispatcher) -> None:
    """Barcha routerlarni dispatcherga ulaydi."""
    dp.include_router(start.router)
    dp.include_router(buy.router)
    dp.include_router(wallet.router)
    dp.include_router(gift_flow.router)
    dp.include_router(post_stars.router)
    dp.include_router(extras.router)
    dp.include_router(referral.router)
    dp.include_router(admin.router)