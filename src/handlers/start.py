# ===================================================================
# handlers/start.py - START / TIL / ASOSIY MENYU / OBUNA
# ===================================================================

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import CallbackQuery, Message

from src.app import App
from src.assets import menu_banner, send_smart_photo
from src.handlers._helpers import edit_or_send, is_subscribed_all, send_subscribe_prompt
from src.i18n import t
from src.keyboards import language_kb, main_menu_kb

router = Router(name="start")


async def render_main_menu(target, app: App, lang: str, user: dict) -> None:
    """
    Bosh menyuni chiroyli ko'rsatadi:
    - banner rasm (mavjud bo'lsa) + caption + yonma-yon tugmalar
    - rasm yetishmasa oddiy matn
    Rasm file_id keshlanadi — birinchi marta upload, keyingilari instant.
    """
    text = t(lang, "start", first=(user.get("first_name") or "friend"))
    kb = main_menu_kb(lang)
    banner = menu_banner()
    if banner:
        sent = await send_smart_photo(target, banner, text, kb)
        if sent is not None:
            return

    sends_new = isinstance(target, CallbackQuery)
    if sends_new:
        try:
            await target.message.delete()
        except Exception:  # noqa: BLE001
            pass
        try:
            await target.message.answer(text, reply_markup=kb)
        except Exception:  # noqa: BLE001
            pass
    else:
        await target.answer(text, reply_markup=kb)


@router.message(CommandStart())
async def cmd_start(message: Message, app: App, command: CommandObject) -> None:
    """Botga 'Start' berilganda ishlaydi. Referal havola ham qabul qiladi."""
    bot_active = await app.settings.bot_active()

    user, created = await app.users.get_or_create(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.first_name or "",
        "uz",
    )

    # Referal bog'lash: /start?start=ref<user_id>
    if created:
        args = (command.args or "").strip()
        if args.lower().startswith("ref") and args[3:].isdigit():
            ref_uid = int(args[3:])
            if ref_uid != message.from_user.id:
                await app.users.set_referrer(message.from_user.id, ref_uid, args)

    # Bot o'chirilgan bo'lsa (admin tomonidan) — admin o'zi kirsa ko'radi
    if not bot_active and not app.cfg.is_admin(message.from_user.id):
        await message.answer(t(user.get("language", "uz"), "start_bot_inactive"))
        return

    lang = user.get("language") or "uz"

    # Obuna tekshiruvi (agar kanal(lar) sozlangan bo'lsa)
    channels = await app.settings.get_channels()
    if channels and not await is_subscribed_all(
        message.bot, message.from_user.id, channels
    ):
        await send_subscribe_prompt(
            message.bot, app, message.from_user.id, lang, channels
        )
        return

    await render_main_menu(message, app, lang, user)


@router.callback_query(F.data == "check:sub")
async def check_subscription(cb: CallbackQuery, app: App) -> None:
    """Obunani tekshirish tugmasi (keshni yangilab)."""
    lang = (await app.users.get(cb.from_user.id) or {}).get("language", "uz")
    channels = await app.settings.get_channels()
    if channels and not await is_subscribed_all(
        cb.bot, cb.from_user.id, channels, force=True
    ):
        await cb.answer(t(lang, "subscribe_alert"), show_alert=True)
        return
    user = await app.users.get(cb.from_user.id) or {}
    await app.users.set_subscribed(cb.from_user.id, True)
    await render_main_menu(cb, app, lang, user)


@router.callback_query(F.data == "menu:main")
async def go_main_menu(cb: CallbackQuery, app: App) -> None:
    """Asosiy menyuga qaytish."""
    lang = (await app.users.get(cb.from_user.id) or {}).get("language", "uz")
    user = await app.users.get(cb.from_user.id) or {}
    await render_main_menu(cb, app, lang, user)


@router.callback_query(F.data == "lang:change")
async def change_lang(cb: CallbackQuery) -> None:
    """Tilni o'zgartirish menyusi."""
    await edit_or_send(cb, "🌐 <b>Select language / Tilni tanlang</b>",
                               reply_markup=language_kb())


@router.callback_query(F.data.startswith("lang:"))
async def set_lang(cb: CallbackQuery, app: App) -> None:
    """Tanlangan tilni saqlash."""
    lang = cb.data.split(":")[1]
    if lang not in ("uz", "en", "ru"):
        return
    await app.users.set_language(cb.from_user.id, lang)
    user = await app.users.get(cb.from_user.id) or {}
    await cb.answer("✅ OK")
    await render_main_menu(cb, app, lang, user)


# /lang qo'shimcha buyruq
@router.message(Command("lang"))
async def cmd_lang(message: Message) -> None:
    await message.answer("🌐 <b>Select language / Tilni tanlang</b>",
                         reply_markup=language_kb())