# ===================================================================
# main.py - Botni ishga tushiruvchi asosiy fayl
#  - config yuklash
#  - App konteynerni qurish (DB + modullar)
#  - Dispatcher sozlash va polling / webhook
#  - Ixtiyoriy: WebApp admin panel serverni ishga tushirish
# Usage:  python -m src.main  (yoki Docker orqali)
# ===================================================================

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

# Agar Windows bo'lsa va Python eski versiya — loop uchun proaktiv sozlash
if sys.platform.startswith("win") and sys.version_info < (3, 14):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from src.app import App  # noqa: E402
from src.config import load_settings  # noqa: E402
from src.handlers import register_handlers  # noqa: E402
from src.i18n import t  # noqa: E402
from src.middleware import SubscriptionMiddleware  # noqa: E402
from src.singleton import SingleInstance  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("stars.bot")

# Loglarni ham faylga yozish (pythonw oynasiz ishlaganda ham ko'rinadi)
try:
    _data_dir = Path(__file__).resolve().parent.parent / "data"
    _data_dir.mkdir(parents=True, exist_ok=True)
    _fh = logging.FileHandler(_data_dir / "bot.log", encoding="utf-8")
    _fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logging.getLogger().addHandler(_fh)
except Exception:  # noqa: BLE001
    pass


async def start_webapp(app: App) -> None:
    """WebApp admin panel serverni alohida task sifatida ishga tushiradi."""
    try:
        from src.keyboards import set_webapp_url
        set_webapp_url(app.cfg.webapp_base_url)
        from src.webapp.server import serve
        cfg = app.cfg
        asyncio.create_task(
            serve(host=cfg.webapp_host, port=cfg.webapp_port, app=app)
        )
        logger.info("WebApp admin panel: http://%s:%s", cfg.webapp_host, cfg.webapp_port)
        if cfg.webapp_base_url:
            logger.info("Mini-App URL: %s/app (Stars olish tugmasi)", cfg.webapp_base_url)
    except Exception as exc:  # noqa: BLE001
        logger.warning("WebApp ishga tushmadi: %s", exc)


async def main() -> None:
    cfg = load_settings()

    # Yagona nusxa himoyasi: ikkinchi instansiya chiqib ketadi
    guard = SingleInstance()
    if not guard.acquire():
        logger.warning("Bot allaqachon ishlayapti — ikkinchi nusxa chiqab ketdi.")
        return

    app = App(cfg)
    await app.connect()
    logger.info("Ma'lumotlar bazasi ulandi: %s", cfg.db_path)

    bot = Bot(
        cfg.bot_token,
        session=AiohttpSession(timeout=70),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Majburiy obuna (global): har bir xabar/callback tekshiriladi
    dp.message.outer_middleware(SubscriptionMiddleware())
    dp.callback_query.outer_middleware(SubscriptionMiddleware())

    # App konteynerni handlerlarga ulash
    dp["app"] = app
    app.bot = bot

    # Referal bonus hisobga tushganda referrerga xabar (payments.try_referral_bonus chiqaradi)
    async def _referral_notify(referrer_id: int, amount: float, user_id: int) -> None:
        try:
            lang = (await app.users.get(referrer_id) or {}).get("language", "uz")
            await bot.send_message(
                referrer_id,
                t(lang, "referral_bonus_received", amount=f"{amount:,.0f}"),
            )
        except Exception:  # noqa: BLE001
            pass

    app.payments.referral_notify = _referral_notify

    register_handlers(dp)

    await start_webapp(app)

    logger.info("Bot ishga tushmoqda...")
    try:
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            polling_timeout=25,
        )
    finally:
        guard.release()
        await bot.session.close()
        await app.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")