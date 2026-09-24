# ===================================================================
# modules/admin.py - ADMIN MODULI
# Admin panelining mantiqiy qismi (telegram va webapp umumiysi):
#  - Buyurtmalar tasdiqlash/rad etish
#  - Narxlar, foiz, karta, kanal sozlash
#  - Akkauntlar va giftlar boshqaruvi
#  - Sotuvlar statistikasi (kunlik / haftalik / oylik)
#  - Bot aktiv/nofaol holati
# ===================================================================

from __future__ import annotations

import time
from datetime import datetime

from src.database import SettingsRepo, now_iso
from src.modules.accounts import AccountsModule
from src.modules.orders import OrdersModule
from src.modules.users import UsersModule
from src.utils import day_start, month_start, week_start


class AdminModule:
    """Admin amallari ro'yxati."""

    def __init__(
        self,
        orders: OrdersModule,
        users: UsersModule,
        accounts: AccountsModule,
        settings: SettingsRepo,
    ):
        self.orders = orders
        self.users = users
        self.accounts = accounts
        self.settings = settings
        # Statistika keshi (admin panel tezligi uchun)
        self._stats_cache: dict = {"ts": 0.0, "data": None}

    # ---------- Buyurtmalar ----------
    async def approve_order(self, order_id: int, deliver: bool = True) -> dict | None:
        """Buyurtmani tasdiqlash. Karta/topup buyurtmasi bo'lsa hisobga yoziladi."""
        order = await self.orders.get(order_id)
        if not order:
            return None
        order_type = order["type"]
        amount = float(order["stars_amount"])

        if deliver and order["status"] not in ("done", "approved"):
            if order_type == "topup":
                # So'm hisobini to'ldirish
                await self.users.add_sum(
                    order["user_id"], float(order["price_amount"]),
                    f"topup deliver order#{order_id}", order_id,
                )
            elif order_type == "buy" and order["payment_method"] == "card":
                await self.users.add_balance(
                    order["user_id"], amount, f"card deliver order#{order_id}", order_id
                )
                await self.orders.add_delivered(order_id, amount)
        await self.orders.update_status(order_id, "approved")
        return order

    async def reject_order(self, order_id: int, reason: str = "") -> dict | None:
        """Buyurtmani rad etish."""
        order = await self.orders.get(order_id)
        if not order:
            return None
        await self.orders.update_status(order_id, "rejected", reason or "admin rejected")
        return order

    async def confirm_post_stars(self, order_id: int, amount: float) -> tuple[bool, str]:
        """Postga stars yetkazish: buyurtmadagi havolaga paid reaction yuboriladi."""
        order = await self.orders.get(order_id)
        if not order:
            return False, "order_not_found"
        link = (order.get("note") or "").strip()
        ok, reason = await self.accounts.deliver_post_stars(amount, link)
        if ok:
            await self.orders.update_status(order_id, "done", "stars sent to post")
        else:
            await self.orders.update_status(order_id, "failed", reason)
        return ok, reason

    # ---------- Sozlamalar ----------
    async def set_prices(self, prices: dict[int, float]) -> None:
        await self.settings.set_prices({int(k): v for k, v in prices.items()})

    async def set_star_price(self, value: float) -> None:
        await self.settings.set_star_price(value)

    async def set_gift_price(self, value: float) -> None:
        await self.settings.set_gift_price(value)

    async def set_post_price(self, value: float) -> None:
        await self.settings.set_post_price(value)

    async def set_post_min_stars(self, value: int) -> None:
        await self.settings.set_post_min_stars(value)

    async def set_percent(self, value: float) -> None:
        await self.settings.set_percent(value)

    async def set_card(self, card: str) -> None:
        await self.settings.set_payment_card(card)

    async def set_channel(self, username: str, chat_id: str) -> None:
        await self.settings.set_channel(username, chat_id)

    async def toggle_bot(self) -> bool:
        """Bot holatini almashtiradi va yangi holat qaytaradi."""
        now_active = await self.settings.bot_active()
        await self.settings.set_bot_active(not now_active)
        return not now_active

    # ---------- Statistika ----------
    async def stats(self, ttl: float = 10.0) -> dict:
        """Statistika (kunlik/haftalik/oylik). Kesh bilan — tez javob.

        ttl: necha sekund ichida qayta hisoblanmaydi (admin panel tezligi).
        """
        now = time.monotonic()
        cached = self._stats_cache
        if cached["data"] is not None and now - cached["ts"] < ttl:
            return cached["data"]
        now_dt = datetime.now()
        daily = await self.orders.stats_range(day_start(now_dt).isoformat())
        weekly = await self.orders.stats_range(week_start(now_dt).isoformat())
        monthly = await self.orders.stats_range(month_start(now_dt).isoformat())
        users = await self.users.count()
        result = {"daily": daily, "weekly": weekly, "monthly": monthly, "users": users}
        cached.update(ts=now, data=result)
        return result

    # ---------- Foydalanuvchi boshqaruvi ----------
    async def adjust_balance(self, user_id: int, amount: float, add: bool) -> float | None:
        """Foydalanuvchi balansini to'ldirish (AUTO/Ruchnoy simulyatsiyasi)."""
        if add:
            return await self.users.add_balance(user_id, amount, "admin balance topup", None)
        return await self.users.sub_balance(user_id, amount, "admin balance withdraw", None)