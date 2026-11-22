# ===================================================================
# src/webapp/server.py - WebApp ADMIN PANEL + API CALLBACK SERVERI
# FastAPI asosida:
#   /admin              - Telegram WebApp sahifasi
#   /api/callback       - @Apilarimbot API qayta chaqiruvi (HMAC tekshiruvi)
#   /api/stats, orders... - admin WebApp REST API (initData auth)
# ===================================================================

from __future__ import annotations

import hashlib
import hmac
import json
import time
import urllib.parse
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.app import App

STATIC_DIR = Path(__file__).parent / "static"


def verify_init_data(init_data: str, bot_token: str) -> dict | None:
    """
    Telegram WebApp initData ni tekshiradi.
    Hujjat: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    """
    if not init_data:
        return None
    pairs = {}
    for chunk in init_data.split("&"):
        if "=" not in chunk:
            continue
        k, v = chunk.split("=", 1)
        pairs[k] = urllib.parse.unquote_plus(v)
    received_hash = pairs.pop("hash", "")
    if not received_hash:
        return None

    data_check_string = "\n".join(
        f"{k}={pairs[k]}" for k in sorted(pairs)
    )
    secret_key = hmac.new(
        b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256
    ).digest()
    calc = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calc, received_hash):
        return None
    try:
        user = json.loads(pairs.get("user", "{}"))
    except json.JSONDecodeError:
        user = {}
    auth_date = pairs.get("auth_date", "0")
    # 24 soatdan eski bo'lsa o'tkazmaymiz
    if int(auth_date) < int(__import__("time").time()) - 86400:
        return None
    return {"id": user.get("id"), "username": user.get("username"), "auth_date": auth_date}


def make_server(app: App) -> FastAPI:
    cfg = app.cfg

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield

    server = FastAPI(title="Auto Stars Admin", lifespan=lifespan)

    # Buyurtmalar keshi (admin panel 2 sekund ichida javob beradi)
    orders_cache: dict = {"ts": 0.0, "data": None}

    # ---------------------------------------------------------------
    # API CALLBACK (@Apilarimbot tomonidan chaqiriladi)
    # Headers: X-API-Signature: HMAC-SHA256(payload)
    # ---------------------------------------------------------------
    @server.post("/api/callback")
    async def api_callback(request: Request):
        body = await request.body()
        payload = body.decode("utf-8")
        sig = request.headers.get("X-API-Signature", "")
        if not app.api.verify_callback(payload, sig, cfg):
            return JSONResponse({"ok": False, "error": "bad signature"}, status_code=403)
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            return JSONResponse({"ok": False, "error": "invalid json"}, status_code=400)

        order_id = data.get("order_id")
        status = data.get("status", "done")
        order = await app.orders.get(int(order_id)) if order_id else None
        if not order:
            return JSONResponse({"ok": False, "error": "order not found"}, status_code=404)

        if status == "done":
            await app.payments.complete_successful(int(order_id), order["user_id"],
                                                   float(order["stars_amount"]))
        elif status in ("rejected", "canceled"):
            await app.orders.update_status(int(order_id), "rejected",
                                           data.get("note", "api rejected"))
        else:
            await app.orders.update_status(int(order_id), "processing")
        return JSONResponse({"ok": True})

    # ---------------------------------------------------------------
    # ADMIN WebApp API (initData auth)
    # ---------------------------------------------------------------
    async def admin_user(request: Request) -> int | None:
        init = request.headers.get("X-Telegram-Init-Data", "")
        info = verify_init_data(init, cfg.bot_token)
        if not info or not cfg.is_admin(info.get("id", 0)):
            return None
        return int(info["id"])

    @server.get("/api/stats")
    async def api_stats(request: Request):
        if not await admin_user(request):
            return JSONResponse({"ok": False}, status_code=401)
        stats = await app.admin.stats()
        return {"ok": True, **stats}

    @server.get("/api/orders")
    async def api_orders(request: Request):
        if not await admin_user(request):
            return JSONResponse({"ok": False}, status_code=401)
        now = time.monotonic()
        if orders_cache["data"] is not None and now - orders_cache["ts"] < 2:
            return {"ok": True, "orders": orders_cache["data"]}
        rows = await app.orders.all_orders(100)
        orders_cache.update(ts=now, data=rows)
        return {"ok": True, "orders": rows}

    @server.post("/api/orders/{order_id}/approve")
    async def api_approve(order_id: int, request: Request):
        if not await admin_user(request):
            return JSONResponse({"ok": False}, status_code=401)
        order = await app.orders.get(order_id)
        if not order:
            return JSONResponse({"ok": False}, status_code=404)
        if order["type"] == "post_stars":
            ok, reason = await app.admin.confirm_post_stars(
                order_id, float(order["stars_amount"])
            )
            return {"ok": ok, "reason": reason}
        await app.payments.approve_card_order(order_id, order["user_id"],
                                              float(order["stars_amount"]))
        orders_cache["ts"] = 0.0  # keshni yangilash
        return {"ok": True}

    @server.post("/api/orders/{order_id}/reject")
    async def api_reject(order_id: int, request: Request):
        if not await admin_user(request):
            return JSONResponse({"ok": False}, status_code=401)
        await app.admin.reject_order(order_id)
        orders_cache["ts"] = 0.0  # keshni yangilash
        return {"ok": True}

    @server.get("/api/settings")
    async def api_settings(request: Request):
        if not await admin_user(request):
            return JSONResponse({"ok": False}, status_code=401)
        return {"ok": True,
                "prices": await app.settings.get_prices(),
                "star_price": await app.settings.get_star_price(),
                "min_stars": await app.settings.get_min_stars(),
                "post_min_stars": await app.settings.get_post_min_stars(),
                "percent": await app.settings.get_percent(),
                "active": await app.settings.bot_active(),
                "card": await app.settings.payment_card(),
                "referral_bonus": await app.settings.get_referral_bonus(),
                "api_enabled": await app.api.enabled()}

    @server.post("/api/settings/prices")
    async def api_set_prices(request: Request):
        if not await admin_user(request):
            return JSONResponse({"ok": False}, status_code=401)
        body = await request.json()
        prices = body.get("prices")
        if isinstance(prices, dict):
            await app.admin.set_prices({int(k): float(v) for k, v in prices.items()})
        return {"ok": True}

    @server.post("/api/settings/referral_bonus")
    async def api_set_referral_bonus(request: Request):
        if not await admin_user(request):
            return JSONResponse({"ok": False}, status_code=401)
        body = await request.json()
        try:
            val = float(body.get("amount", 0))
        except (TypeError, ValueError):
            return {"ok": False, "error": "bad_amount"}
        if val < 0:
            return {"ok": False, "error": "bad_amount"}
        await app.settings.set_referral_bonus(val)
        return {"ok": True, "referral_bonus": val}

    # ---------------------------------------------------------------
    # MINI-APP (buy) — oddiy foydalanuvchi auth, admin shart emas
    # Sotib olish mini-app sahifasi /app, ma'lumot /api/me, buy /api/buy
    # ---------------------------------------------------------------
    async def any_user(request: Request) -> dict | None:
        """Har qanday tasdiqlangan Telegram foydalanuvchi (admin shart emas)."""
        init = request.headers.get("X-Telegram-Init-Data", "")
        info = verify_init_data(init, cfg.bot_token)
        return info if info and info.get("id") else None

    @server.get("/app", response_class=HTMLResponse)
    async def buy_page():
        html = (STATIC_DIR / "app.html").read_text(encoding="utf-8")
        return HTMLResponse(html)

    @server.get("/api/me")
    async def api_me(request: Request):
        info = await any_user(request)
        if not info:
            return JSONResponse({"ok": False, "error": "auth"}, status_code=401)
        user_id = int(info["id"])
        user = await app.users.get(user_id) or {}
        star_price = await app.settings.get_star_price()
        min_stars = await app.settings.get_min_stars()
        api_enabled = await app.api.enabled()
        username = (user.get("username") or "") or (info.get("username") or "")
        return {
            "ok": True,
            "user": user_id,
            "username": username,
            "first_name": user.get("first_name") or "",
            "balance_sum": float(user.get("balance_sum", 0)),
            "balance_stars": float(user.get("balance_stars", 0)),
            "star_price": star_price,
            "min_stars": min_stars,
            "api_enabled": api_enabled,
        }

    @server.get("/api/buy/prices")
    async def api_buy_prices(request: Request):
        info = await any_user(request)
        if not info:
            return JSONResponse({"ok": False, "error": "auth"}, status_code=401)
        star_price = await app.settings.get_star_price()
        min_stars = await app.settings.get_min_stars()
        pkg = {}
        if star_price > 0:
            for mult in (1, 2, 3, 5, 10):
                a = min_stars * mult
                if a <= 100000:
                    pkg[a] = round(star_price * a, 2)
        else:
            from src.utils import prices_text  # noqa: F401
            defaults = await app.settings.get_prices() or app.cfg.default_prices
            pkg = {int(k): float(v) for k, v in defaults.items()}
        return {"ok": True, "packages": pkg, "star_price": star_price, "min_stars": min_stars}

    @server.post("/api/buy")
    async def api_buy(request: Request):
        info = await any_user(request)
        if not info:
            return JSONResponse({"ok": False, "error": "auth"}, status_code=401)
        user_id = int(info["id"])
        try:
            body = await request.json()
            stars = int(body.get("stars", 0))
            username = str(body.get("username", "") or "").strip().lstrip("@")
        except Exception:  # noqa: BLE001
            return JSONResponse({"ok": False, "error": "bad_request"}, status_code=400)
        star_price = await app.settings.get_star_price()
        min_stars = await app.settings.get_min_stars()
        if star_price <= 0:
            return {"ok": False, "error": "no_price"}
        if stars < min_stars:
            return {"ok": False, "error": "min_stars", "min_stars": min_stars}
        if stars > 100000:
            return {"ok": False, "error": "too_much"}
        if not username:
            return {"ok": False, "error": "need_username"}
        price = round(star_price * stars, 2)
        result = await app.payments.demand(user_id, stars, price, username)
        if not result.ok:
            return {"ok": False, "error": result.error,
                    "balance_sum": await app.users.balance_sum(user_id)}
        try:
            from src.handlers._helpers import notify_payments_channel
            if app.bot:
                await notify_payments_channel(app.bot, app, result.order_id)
        except Exception:  # noqa: BLE001
            pass
        return {
            "ok": True,
            "order_id": result.order_id,
            "stars": stars,
            "username": username,
            "price": price,
            "balance_stars": result.balance,
            "balance_sum": await app.users.balance_sum(user_id),
        }

    # Sahifa va statika
    server.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @server.get("/", response_class=HTMLResponse)
    @server.get("/admin", response_class=HTMLResponse)
    async def admin_page():
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
        return HTMLResponse(html)

    return server


async def serve(host: str, port: int, app: App) -> None:
    """FastAPI serverni uvicorn bilan (async task) ishga tushiradi."""
    import uvicorn

    server = make_server(app)
    config = uvicorn.Config(server, host=host, port=port, log_level="warning", log_config=None)
    await uvicorn.Server(config).serve()