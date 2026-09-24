# ===================================================================
# handlers/wallet.py - HISOB (SO'MDA) VA STARS BALANSI
#  - Hisob: naqd pul (so'm) — karta / online orqali to'ldiriladi
#  - Stars: so'm hisobdan sotib olinadi (buy.py)
#  - Sof so'm, stars, statistika va tarix
# ===================================================================

from __future__ import annotations

import asyncio

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.app import App
from src.handlers._helpers import (
    edit_or_send,
    notify_admins_media,
    notify_all_admins,
    notify_payments_channel,
    user_ref,
)
from src.handlers.states import TopupFlow
from src.i18n import t
from src.keyboards import admin_orders_kb, topup_kb, wallet_kb
from src.utils import format_amount, progress_bar

router = Router(name="wallet")

_total_cap = 100.0  # stars progress bar to'lishi uchun shartli me'yor


async def _safe_pay_channel(bot, app, order_id: int) -> None:
    try:
        await notify_payments_channel(bot, app, order_id)
    except Exception:  # noqa: BLE001
        pass


async def _safe_admins(bot, text: str, app, kb=None) -> None:
    try:
        await notify_all_admins(bot, text, app, kb)
    except Exception:  # noqa: BLE001
        pass


async def _safe_admins_media(bot, photo_id: str, caption: str, app, kb=None) -> None:
    try:
        await notify_admins_media(bot, photo_id, caption, app, kb)
    except Exception:  # noqa: BLE001
        pass


async def _lang(app: App, user_id: int) -> str:
    return (await app.users.get(user_id) or {}).get("language", "uz")


def _fmt(value: float) -> str:
    """So'm miqdorini chiroyli formatda yozadi: 100 000"""
    return f"{value:,.0f}"


def _parse_sum(text: str) -> int | None:
    """Matndan faqat sonni oladi (bo'sh joy/kursa belgisi bo'lmaydi)."""
    digits = "".join(ch for ch in (text or "") if ch.isdigit())
    return int(digits) if digits else None


@router.callback_query(F.data == "menu:wallet")
async def show_wallet(cb: CallbackQuery, app: App) -> None:
    """Asosiy hisob ko'rinishi (so'm + stars)."""
    lang = await _lang(app, cb.from_user.id)
    user = await app.users.get(cb.from_user.id) or {}
    sum_bal = float(user.get("balance_sum", 0))
    bal = float(user.get("balance_stars", 0))
    totals = await app.users.totals(cb.from_user.id)
    prog = progress_bar(bal, _total_cap)
    await edit_or_send(cb,
        t(lang, "wallet_title",
          sum=_fmt(sum_bal),
          balance=format_amount(bal), progress=prog,
          bought=format_amount(float(totals.get("bought", 0))),
          sold=format_amount(float(totals.get("sold", 0))),
          gifted=format_amount(float(totals.get("gifted", 0)))),
        reply_markup=wallet_kb(lang),
    )


@router.callback_query(F.data == "topup:choose")
async def topup_choose(cb: CallbackQuery, app: App) -> None:
    """Hisobni so'mda to'ldirish usullari."""
    lang = await _lang(app, cb.from_user.id)
    await edit_or_send(cb,
        t(lang, "wallet_topup"),
        reply_markup=topup_kb(lang),
    )


@router.callback_query(F.data == "topup:card")
async def topup_card_start(cb: CallbackQuery, app: App, state: FSMContext) -> None:
    """Karta orqali so'm to'ldirish."""
    lang = await _lang(app, cb.from_user.id)
    await topup_amount_start(cb, lang, "card", state)


@router.callback_query(F.data == "topup:auto")
async def topup_api_start(cb: CallbackQuery, app: App, state: FSMContext) -> None:
    """Online (API) orqali so'm to'ldirish."""
    lang = await _lang(app, cb.from_user.id)
    await topup_amount_start(cb, lang, "api", state)


async def topup_amount_start(cb: CallbackQuery, lang: str, method: str, state: FSMContext) -> None:
    await state.set_state(TopupFlow.wait_sum)
    await state.update_data(topup_method=method)
    await edit_or_send(cb, t(lang, "topup_sum_prompt"))


@router.message(StateFilter(TopupFlow.wait_sum))
async def topup_sum_received(message: Message, app: App, state: FSMContext) -> None:
    """So'm miqdori kelganda: API -> avtomatik, karta -> tasdiq kutiladi."""
    lang = await _lang(app, message.from_user.id)
    value = _parse_sum(message.text or "")
    if not value or value <= 0:
        await message.answer(t(lang, "topup_sum_prompt"))
        return
    data = await state.get_data()
    method = data.get("topup_method", "card")

    if method == "api":
        order_id = await app.payments.create_intent(
            message.from_user.id, "topup", 0, "api", price=float(value)
        )
        await message.answer(t(lang, "api_order_creating"))
        result = await app.payments.submit_api_payment(order_id, message.from_user.id, value)
        if result.ok:
            new_bal = await app.payments.complete_successful(order_id, message.from_user.id, value)
            asyncio.create_task(_safe_pay_channel(message.bot, app, order_id))
            await message.answer(
                t(lang, "topup_api_success", balance=_fmt(new_bal)),
            )
        else:
            await message.answer(t(lang, "api_order_failed"))
        await state.clear()
        return

    # ---- Karta: to'lov ko'rsatmasi + tasdiq kutamiz ----
    card = await app.settings.payment_card() or app.cfg.payment_card
    await message.answer(
        t(lang, "topup_card_pay", amount=_fmt(value), card=card)
    )
    await state.set_state(TopupFlow.wait_proof)
    await state.update_data(topup_sum=value)


@router.message(StateFilter(TopupFlow.wait_proof))
async def topup_proof_received(message: Message, app: App, state: FSMContext) -> None:
    """Karta to'lov tasdig'i keldi — buyurtma admin tasdig'iga yuboriladi."""
    lang = await _lang(app, message.from_user.id)
    data = await state.get_data()
    value = data.get("topup_sum")
    if not value:
        await message.answer("❌ Buyurtma topilmadi. /start ni bosing.")
        await state.clear()
        return

    user = await app.users.get(message.from_user.id) or {}
    order_id = await app.payments.create_intent(
        message.from_user.id, "topup", 0, "card", price=float(value)
    )
    proof = (
        f"💳 {message.text[:400] if message.text else '[Rasm tasdiq]'}\n\n"
        f"👤 {user_ref(user)}"
    )
    result = await app.payments.submit_card_payment(order_id, message.from_user.id, proof)
    if not result.ok:
        await message.answer(t(lang, "admin_invalid_format"))
        return

    asyncio.create_task(_safe_admins(
        message.bot,
        t(lang, "topup_sent_admin",
          uid=message.from_user.id, user=user_ref(user), amount=_fmt(value),
          proof=(message.text[:150] if message.text else "🖼 rasm")),
        app,
        admin_orders_kb(lang, order_id),
    ))
    if message.photo:
        asyncio.create_task(_safe_admins_media(
            message.bot, message.photo[0].file_id,
            t(lang, "topup_sent_admin",
              uid=message.from_user.id, user=user_ref(user), amount=_fmt(value),
              proof="🖼 isbot"),
            app,
            admin_orders_kb(lang, order_id),
        ))
    await message.answer(t(lang, "topup_sent_user", amount=_fmt(value)))
    await state.clear()


@router.callback_query(F.data == "wallet:history")
async def wallet_history(cb: CallbackQuery, app: App) -> None:
    """Transaksiyalar tarixi."""
    lang = await _lang(app, cb.from_user.id)
    rows = await app.users.history(cb.from_user.id, 12)
    if not rows:
        await edit_or_send(cb,
            t(lang, "wallet_history", history=t(lang, "tx_none")),
            reply_markup=wallet_kb(lang),
        )
        return
    lines = []
    for r in rows:
        sign = "➕" if r["type"] == "credit" else "➖"
        lines.append(f"{sign} <b>{format_amount(float(r['amount']))}</b> · {r['reason']}")
    await edit_or_send(cb,
        t(lang, "wallet_history", history="\n".join(lines)),
        reply_markup=wallet_kb(lang),
    )