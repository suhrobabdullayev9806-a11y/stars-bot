# ===================================================================
# handlers/referral.py - REFERAL DASTURI (foydalanuvchi bo'limi)
# Foydalanuvchi o'z taklif havolasini ko'radi, nechta referal kelganini
# va qancha bonus (so'm) ishlanganini biladi.
# Referal bonus miqdori ADMIN PANEL orqali boshqariladi (referral_bonus).
# ===================================================================

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from src.app import App
from src.handlers._helpers import edit_or_send
from src.i18n import t
from src.keyboards import referral_kb

router = Router(name="referral")


async def _lang(app: App, user_id: int) -> str:
    return (await app.users.get(user_id) or {}).get("language", "uz")


def _format_ref_line(ref: dict) -> str:
    """Referal satrini chiroyli ko'rsatadi."""
    username = (ref.get("username") or "").lstrip("@")
    name = ref.get("first_name") or str(ref.get("id", ""))
    if username:
        label = f"@{username}"
    else:
        label = f"[{name}](tg://user?id={ref['id']})"
    bonus = float(ref.get("referral_sum", 0) or 0)
    return f"  • {label} — {bonus:,.0f} so'm"


@router.callback_query(F.data == "menu:referral")
async def show_referral(cb: CallbackQuery, app: App) -> None:
    """Referal bo'limini ko'rsatadi: havola + statistika."""
    lang = await _lang(app, cb.from_user.id)
    user_id = cb.from_user.id
    bonus = await app.settings.get_referral_bonus()
    count = await app.users.referral_count(user_id)
    earned = await app.users.referral_sum(user_id)

    link = ""
    try:
        me = await app.bot.get_me() if app.bot else None
        if me and me.username:
            link = f"https://t.me/{me.username}?start=ref{user_id}"
    except Exception:  # noqa: BLE001
        link = ""

    refs_rows = await app.users.referral_list(user_id, 5)
    if refs_rows:
        refs = "\n".join(_format_ref_line(r) for r in refs_rows)
        refs = refs[:900]
    else:
        refs = t(lang, "referral_list_empty")

    text = t(
        lang,
        "referral_info",
        bonus=f"{bonus:,.0f}",
        link=link or "—",
        count=count,
        earned=f"{earned:,.0f}",
        refs=refs,
    )
    await edit_or_send(cb, text, reply_markup=referral_kb(lang))