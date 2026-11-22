# ===================================================================
# handlers/_helpers.py - Umumiy yordamchi funksiyalar
# Obuna tekshirish, user formati, moderator xabarlari va h.k.
# ===================================================================

from __future__ import annotations

import asyncio
import logging
import time

from aiogram import Bot
from aiogram.types import CallbackQuery, Message

from src.config import Settings
from src.i18n import t

_log = logging.getLogger("stars.notify")

# Obuna tekshiruvi keshi: (ts, subscribed). Telegram rate-limitidan
# qochish uchun natija qisqa muddat (SUB_TTL) saqlanadi.
SUB_TTL = 90.0
_sub_cache: dict[int, tuple[float, bool]] = {}


def _cached_sub(user_id: int) -> bool | None:
    entry = _sub_cache.get(user_id)
    if not entry:
        return None
    ts, ok = entry
    if time.monotonic() - ts > SUB_TTL:
        return None
    return ok


async def _check_channel(bot: Bot, user_id: int, chat_id: str) -> bool:
    """Bitta kanalga obunani tekshiradi. Xato bo'lsa bloklamaydi (True)."""
    if not chat_id:
        return True
    try:
        member = await bot.get_chat_member(chat_id, user_id)
    except Exception:  # noqa: BLE001
        # Kanal topilmasa yoki botga ruxsat bo'lmasa - bloklamaymiz
        return True
    return member.status in ("member", "administrator", "creator")


async def is_subscribed(bot: Bot, user_id: int, channel: str, channel_id: str | None) -> bool:
    """Foydalanuvchi majburiy kanalga obuna bo'lganini tekshiradi (bitta kanal)."""
    if not channel:
        return True
    chat_id = channel_id if channel_id else f"@{channel}"
    return await _check_channel(bot, user_id, chat_id)


async def is_subscribed_all(
    bot: Bot,
    user_id: int,
    channels: list[tuple[str, str]],
    force: bool = False,
) -> bool:
    """Foydalanuvchi HAMMA majburiy kanallarga obuna ekanini tekshiradi.

    - channels: [(username, chat_id), ...]
    - force=True bo'lsa kesh o'qilmaydi (masalan '✅ Tekshirish' tugmasi).
    - Natija SUB_TTL (90s) keshlanadi — flooddan himoya.
    """
    if not channels:
        return True
    if not force:
        cached = _cached_sub(user_id)
        if cached is not None:
            return cached
    tags = [
        (ch_id or f"@{username}")
        for username, ch_id in channels
        if username
    ]
    if not tags:
        return True
    results = await asyncio.gather(
        *(_check_channel(bot, user_id, tag) for tag in tags)
    )
    ok = all(results)
    _sub_cache[user_id] = (time.monotonic(), ok)
    return ok


async def send_subscribe_prompt(bot: Bot, app, user_id: int, lang: str,
                               channels: list[tuple[str, str]]) -> None:
    """Obuna ko'rsatmasi: kanal(lar) + 'Obuna bo'lish' + '✅ Tekshirish' tugmalari."""
    from src.keyboards import check_subscribe_kb
    text = t(lang, "start_not_subscribed")
    joined = "\n".join(f"  📢 @{username}" for username, _ch in channels if username) or "—"
    text = text.format(channels=joined)
    kb = check_subscribe_kb(lang, channels)
    try:
        await bot.send_message(user_id, text, reply_markup=kb, disable_web_page_preview=True)
    except Exception:  # noqa: BLE001
        pass


def user_ref(user: dict) -> str:
    """Foydalanuvchini telegramda ko'rsatiladigan formatga o'tkazadi."""
    username = user.get("username") or ""
    first = user.get("first_name") or str(user.get("id", ""))
    return f"@{username}" if username else f"[{first}](tg://user?id={user['id']})"


async def notify_admins(bot: Bot, text: str, cfg: Settings, kb=None) -> None:
    """Barcha adminlarga xabar jo'natadi (.env ADMIN_IDS + super admin)."""
    for admin_id in cfg.admin_ids:
        try:
            await bot.send_message(admin_id, text, reply_markup=kb, disable_web_page_preview=True)
        except Exception:  # noqa: BLE001
            continue
    if cfg.super_admin_id and cfg.super_admin_id not in cfg.admin_ids:
        try:
            await bot.send_message(cfg.super_admin_id, text, reply_markup=kb,
                                   disable_web_page_preview=True)
        except Exception:  # noqa: BLE001
            pass


async def notify_all_admins(bot: Bot, text: str, app, kb=None) -> None:
    """Barcha adminlarga xabar jo'natadi — .env adminlari + DB'da qo'shilganlar."""
    extra = await app.settings.get_extra_admins()
    seen = set()
    ids = list(app.cfg.admin_ids)
    if app.cfg.super_admin_id:
        ids.append(app.cfg.super_admin_id)
    for admin_id in ids + extra:
        if admin_id in seen:
            continue
        seen.add(admin_id)
        try:
            await bot.send_message(admin_id, text, reply_markup=kb, disable_web_page_preview=True)
        except Exception:  # noqa: BLE001
            continue


async def notify_admins_content(bot: Bot, media_kind: str, file_id: str, caption: str,
                               app, kb=None) -> None:
    """Chekni media TURIGA qarab barcha adminlarga yetkazadi.

    Endi chek rasm/video/fayl(png-skrinshot)/animatsiya qilib yuborilganiga
    qarab mos holyalik usulda (retry + log bilan) adminga boradi.

    Retry: DNS vaqtincha uzilganda, flood limitida va boshqa tarmoq xatolarida
    har bir adminga alohida 3 marta qayta urinadi; hammasi ham ishlamasa
    `ERROR` log'ga yoziladi — chek hech qachon izsiz yo'qolmaydi.
    """
    kind_sender = {
        "photo": bot.send_photo,
        "video": bot.send_video,
        "document": bot.send_document,
        "animation": bot.send_animation,
    }
    sender = kind_sender.get(media_kind)
    if not sender:
        _log.warning("noma'lum chek media turi: %s", media_kind)
        return

    extra = await app.settings.get_extra_admins()
    seen: set[int] = set()
    ids: list[int] = list(app.cfg.admin_ids)
    if app.cfg.super_admin_id:
        ids.append(app.cfg.super_admin_id)
    for admin_id in ids + extra:
        if admin_id in seen:
            continue
        seen.add(admin_id)
        try:
            # Tarmoq vaqtinchalik uzilganda ham chek yetkazilishi uchun retry
            for attempt in range(3):
                try:
                    await sender(
                        admin_id, file_id, caption=caption, reply_markup=kb,
                        disable_web_page_preview=True)
                    break
                except Exception as exc:  # noqa: BLE001
                    if attempt == 2:
                        raise
                    _log.warning("chek retry %d media=%s admin=%s: %s",
                                 attempt + 1, media_kind, admin_id, exc)
                    await asyncio.sleep(1.5)
        except Exception as exc:  # noqa: BLE001
            _log.error("chek adminga yetkazilmadi admin=%s media=%s: %s",
                       admin_id, media_kind, exc)


async def notify_admins_media(bot: Bot, photo_id: str, caption: str, app, kb=None) -> None:
    """ESKI imzo (rasm) — yangi universal `notify_admins_content` ga yo'naltiradi.

    Chek yuborilganda endi media TURIGA qarab (rasm/video/fayl/animatsiya)
    mos usulda adminga yetkaziladi — `notify_admins_content` ga qarang.
    """
    await notify_admins_content(bot, "photo", photo_id, caption, app, kb)
    extra = await app.settings.get_extra_admins()
    seen = set()
    ids = list(app.cfg.admin_ids)
    if app.cfg.super_admin_id:
        ids.append(app.cfg.super_admin_id)
    for admin_id in ids + extra:
        if admin_id in seen:
            continue
        seen.add(admin_id)
        try:
            # Tarmoq vaqtincha uzilganda ham chek yetkazilishi uchun retry
            for attempt in range(3):
                try:
                    await bot.send_photo(admin_id, photo_id, caption=caption,
                                         reply_markup=kb,
                                         disable_web_page_preview=True)
                    break
                except Exception as exc:  # noqa: BLE001
                    if attempt == 2:
                        raise
                    _log.warning("send_photo chek retry %d admin=%s: %s",
                                 attempt + 1, admin_id, exc)
                    await asyncio.sleep(1.5)
        except Exception as exc:  # noqa: BLE001
            _log.error("chek adminga yuborilmadi admin=%s: %s", admin_id, exc)


async def notify_payments_channel(bot: Bot, app, order_id: int) -> None:
    """Yangi zakaz haqida to'lovlar kanaliga xabar jo'natadi (sozlangan bo'lsa).

    Admin panel: Sozlamalar -> To'lovlar kanali sozlash.
    """
    order = await app.orders.get(order_id)
    if not order:
        return
    username, chat_id = await app.settings.get_payment_channel()
    if not username and not chat_id:
        return
    target = chat_id or f"@{username}"
    try:
        user = await app.users.get(order["user_id"]) or {}
        uid = order["user_id"]
        uname = user.get("username") or user.get("first_name") or str(uid)
        if user and not user.get("username"):
            uname = f"[{uname}](tg://user?id={uid})"
        else:
            uname = "@" + uname
        type_map = {
            "buy": "🛒 Sotib olish",
            "gift": "🎁 Gift",
            "post_stars": "📝 Postga stars",
            "topup": "💰 Hisob to'ldirish (so'm)",
        }
        stars = float(order["stars_amount"])
        bio = (f"<b>{int(stars)} ⭐</b>" if stars else
               f"<b>{float(order['price_amount']):,.0f} so'm</b>")
        text = (
            f"🛒 <b>YANGI ZAKAZ №{order['id']}</b>\n"
            f"👤 <b>{uname}</b> (id: <code>{uid}</code>)\n"
            f"📦 Tur: {type_map.get(order['type'], order['type'])} — {bio}\n"
            f"💰 Narx: <b>{float(order['price_amount']):,.0f}</b> so'm\n"
            f"💳 Usul: <code>{order['payment_method']}</code>\n"
            f"🕓 Vaqt: <code>{order['created_at']}</code>\n"
        )
        if order.get("note"):
            text += f"📝 {str(order['note'])[:120]}\n"
        text += f"📌 Status: <b>{order['status']}</b>"
        await bot.send_message(target, text, disable_web_page_preview=True)
    except Exception:  # noqa: BLE001
        pass


async def answer(msg: Message, key: str, lang: str, kb=None, **kwargs) -> None:
    """Xabar yuborish yordamchisi."""
    text = t(lang, key, **kwargs)
    await msg.answer(text, reply_markup=kb, disable_web_page_preview=True)


async def edit_ok(cb: CallbackQuery, key: str, lang: str, kb=None, **kwargs) -> None:
    """Mavjud xabarni yangilash yordamchisi."""
    text = t(lang, key, **kwargs)
    try:
        await cb.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
    except Exception:  # noqa: BLE001
        await cb.answer()


async def edit_or_send(cb: CallbackQuery, text: str, reply_markup=None,
                       disable_web_page_preview: bool = True) -> None:
    """
    Xabarni tahrirlaydi. Agar xabar media (rasm) bo'lsa, edit qilib
    bo'lmaydi — eski xabarni o'chirib yangi (matn) xabar jo'natadi.
    Bu bannerli menyular va bosqichli jarayonlar uchun zarur.
    """
    try:
        await cb.message.edit_text(text, reply_markup=reply_markup,
                                   disable_web_page_preview=disable_web_page_preview)
        return
    except Exception:  # noqa: BLE001
        pass
    try:
        await cb.message.delete()
    except Exception:  # noqa: BLE001
        pass
    try:
        await cb.message.answer(text, reply_markup=reply_markup,
                                disable_web_page_preview=disable_web_page_preview)
    except Exception:  # noqa: BLE001
        pass