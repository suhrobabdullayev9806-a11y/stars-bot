# ===================================================================
# database.py - Ma'lumotlar bazasi qatlami
# SQLite + aiosqlite (async). Jadvallar init() da yaratiladi.
# Har xil modullar bu base-dan foydalanadi.
# ===================================================================

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import aiosqlite

SCHEMA = """
-- Foydalanuvchilar
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY,
    username      TEXT    DEFAULT '',
    first_name    TEXT    DEFAULT '',
    language      TEXT    DEFAULT 'uz',
    balance_stars REAL    DEFAULT 0,
    balance_sum   REAL    DEFAULT 0,   -- so'mdagi hisob (naqd pul hamyon)
    referrer_id   INTEGER DEFAULT NULL, -- kimni taklifi (referral) bilan kelgan
    referral_code TEXT    DEFAULT '',  -- referrer kodi (start?start=REFLARI)
    referral_sum  REAL    DEFAULT 0,   -- referral orqali to'plangan bonus (so'm)
    referral_paid INTEGER DEFAULT 0,   -- referrer bonus bir marta to'langani (1/0)
    is_vip        INTEGER DEFAULT 0,
    subscribed    INTEGER DEFAULT 0,
    created_at    TEXT
);

-- Buyurtmalar (sotib olish, gift, post stars)
CREATE TABLE IF NOT EXISTS orders (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                INTEGER NOT NULL,
    type                   TEXT    NOT NULL,
    stars_amount           REAL    DEFAULT 0,
    total_stars_delivered  REAL    DEFAULT 0,
    price_amount           REAL    DEFAULT 0,
    payment_method         TEXT    DEFAULT 'card',
    status                 TEXT    DEFAULT 'pending',
    api_ref                TEXT    DEFAULT '',
    note                   TEXT    DEFAULT '',
    created_at             TEXT,
    updated_at             TEXT
);

-- Hisob harakatlari (transaksiyalar)
CREATE TABLE IF NOT EXISTS transactions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    order_id   INTEGER,
    amount     REAL    DEFAULT 0,
    type       TEXT,              -- credit | debit
    reason     TEXT,
    created_at TEXT
);

-- Sozlamalar (kalit-qiymat)
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT
);

-- Ulangan Telegram akkauntlar (gift yuborish avtomatizatsiyasi)
CREATE TABLE IF NOT EXISTS accounts (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    title         TEXT,
    session_data  TEXT DEFAULT '',      -- Fernet bilan shifrlangan session string
    session_hash  TEXT DEFAULT '',      -- asl qiymatning sha256 hashi (identifikatsiya)
    status        TEXT DEFAULT 'active',
    created_at    TEXT
);

-- Reklama kampaniyalari (broadcast)
CREATE TABLE IF NOT EXISTS campaigns (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    text       TEXT,
    created_at TEXT
);

-- Gift katalogi (admin nomi, narxi (so'm), stars soni bilan qo'shadi)
CREATE TABLE IF NOT EXISTS gifts (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    DEFAULT '',
    price      REAL    DEFAULT 0,
    stars      REAL    DEFAULT 0,
    active     INTEGER DEFAULT 1,
    created_at TEXT
);

-- Tezlik (admin panel): indekslar
CREATE INDEX IF NOT EXISTS idx_orders_status  ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_type    ON orders(type);
CREATE INDEX IF NOT EXISTS idx_orders_user    ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_created ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_tx_user        ON transactions(user_id, id);
"""


def now_iso() -> str:
    """Hozirgi vaqtni ISO formatda qaytaradi."""
    return datetime.now().isoformat(timespec="seconds")


class Database:
    """SQLite bazasi bilan ishlash uchun yordamchi klass."""

    def __init__(self, path: str):
        self.path = path
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        """Ulanish ochadi va jadvallarni yaratadi."""
        self._conn = await aiosqlite.connect(self.path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.executescript(SCHEMA)
        # Migratsiya: eski bazalarda account'ga session_hash kolonkasini qo'shish
        cols = await self._conn.execute("PRAGMA table_info(accounts)")
        col_names = [r[1] for r in await cols.fetchall()]
        if "session_hash" not in col_names:
            await self._conn.execute(
                "ALTER TABLE accounts ADD COLUMN session_hash TEXT DEFAULT ''"
            )
        # Migratsiya: so'mdagi hisob (balance_sum)
        ucols = await self._conn.execute("PRAGMA table_info(users)")
        ucol_names = [r[1] for r in await ucols.fetchall()]
        if "balance_sum" not in ucol_names:
            await self._conn.execute(
                "ALTER TABLE users ADD COLUMN balance_sum REAL DEFAULT 0"
            )
        # Migratsiya: referral tizimi (referrer_id / referral_sum / referral_paid)
        if "referrer_id" not in ucol_names:
            await self._conn.execute(
                "ALTER TABLE users ADD COLUMN referrer_id INTEGER DEFAULT NULL"
            )
        if "referrer_code" not in ucol_names:
            await self._conn.execute(
                "ALTER TABLE users ADD COLUMN referrer_code TEXT DEFAULT ''"
            )
        if "referral_sum" not in ucol_names:
            await self._conn.execute(
                "ALTER TABLE users ADD COLUMN referral_sum REAL DEFAULT 0"
            )
        if "referral_paid" not in ucol_names:
            await self._conn.execute(
                "ALTER TABLE users ADD COLUMN referral_paid INTEGER DEFAULT 0"
            )
        try:
            await self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_users_referrer ON users(referrer_id)"
            )
        except Exception:  # noqa: BLE001
            pass
        # Tezlik: WAL rejimi (o'quv va yozuv bloklanmasin) + busy_timeout
        try:
            await self._conn.execute("PRAGMA journal_mode=WAL")
        except Exception:  # noqa: BLE001
            pass
        try:
            await self._conn.execute("PRAGMA synchronous=NORMAL")
        except Exception:  # noqa: BLE001
            pass
        try:
            await self._conn.execute("PRAGMA busy_timeout=10000")
        except Exception:  # noqa: BLE001
            pass
        await self._conn.commit()

    async def close(self) -> None:
        """Ulanishni yopadi."""
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def execute(self, sql: str, params: tuple[Any, ...] = ()) -> int:
        """Yozish so'rovini bajaradi va oxirgi rowid qaytaradi."""
        assert self._conn is not None, "Database ulanishi ochilmagan"
        cur = await self._conn.execute(sql, params)
        await self._conn.commit()
        return cur.lastrowid

    async def execute_many(self, sql: str, seq: list[tuple]) -> None:
        assert self._conn is not None
        await self._conn.executemany(sql, seq)
        await self._conn.commit()

    async def fetch_one(self, sql: str, params: tuple[Any, ...] = ()) -> dict | None:
        """Bitta qatorni dict ko'rinishida qaytaradi."""
        assert self._conn is not None
        cur = await self._conn.execute(sql, params)
        row = await cur.fetchone()
        return dict(row) if row else None

    async def fetch_all(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict]:
        """Barcha qatorlarni dict listi ko'rinishida qaytaradi."""
        assert self._conn is not None
        cur = await self._conn.execute(sql, params)
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


# ===================================================================
# Sozlamalar repository - admin panelda o'zgartiriladigan qiymatlar
# ===================================================================

class SettingsRepo:
    """DB dagi settings jadvali bilan ishlash."""

    def __init__(self, db: Database):
        self.db = db

    async def get(self, key: str, default: str = "") -> str:
        row = await self.db.fetch_one("SELECT value FROM settings WHERE key = ?", (key,))
        return row["value"] if row else default

    async def set(self, key: str, value: str) -> None:
        await self.db.execute(
            "INSERT INTO settings(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )

    # --- maxsus getter/setter'lar ---

    async def get_prices(self) -> dict[int, float]:
        raw = await self.get("prices", "")
        try:
            data = json.loads(raw) if raw else {}
            return {int(k): float(v) for k, v in data.items()}
        except (json.JSONDecodeError, ValueError):
            return {}

    async def set_prices(self, prices: dict[int, float]) -> None:
        await self.set("prices", json.dumps(prices))

    # --- Referral: har bir referal uchun bonus (SUM) ---
    async def get_referral_price(self) -> float:
        try:
            return float(await self.get("referral_price", "0"))
        except ValueError:
            return 0.0

    async def set_referral_price(self, value: float) -> None:
        await self.set("referral_price", str(round(float(value), 2)))

    async def get_percent(self) -> float:
        try:
            return float(await self.get("percent", "0"))
        except ValueError:
            return 0.0

    async def set_percent(self, value: float) -> None:
        await self.set("percent", str(value))

    # --- 1 STAR NARXI (so'm) va minimal miqdor ---
    # Admin panel: "1 star narxi" mas. 200 so'm. Buy narx = stars * star_price.
    async def get_star_price(self) -> float:
        try:
            return float(await self.get("star_price", "0"))
        except ValueError:
            return 0.0

    async def set_star_price(self, value: float) -> None:
        await self.set("star_price", str(round(float(value), 2)))

    # --- ALOHIDA NARXLAR: gift va post (1⭐, so'm) ---
    # Admin panel: 3 ta alohida 1⭐ narxi — Stars (buy), Gift, Post.
    # Agar gift yoki post narxi o'rnatilmagan bo'lsa, star_price ishlatiladi.

    async def get_gift_price(self) -> float:
        try:
            v = float(await self.get("gift_price", "0"))
        except ValueError:
            v = 0.0
        return v if v > 0 else await self.get_star_price()

    async def set_gift_price(self, value: float) -> None:
        await self.set("gift_price", str(round(float(value), 2)))

    async def get_post_price(self) -> float:
        try:
            v = float(await self.get("post_price", "0"))
        except ValueError:
            v = 0.0
        return v if v > 0 else await self.get_star_price()

    async def set_post_price(self, value: float) -> None:
        await self.set("post_price", str(round(float(value), 2)))

    # --- POSTGA MINIMAL STARS (alohida) ---
    # Agar o'rnatilmagan bo'lsa (0), post oqimida umumiy min_stars ishlatiladi.(self) -> int:
        try:
            v = int(float(await self.get("post_min_stars", "0")))
        except ValueError:
            v = 0
        if v > 0:
            return v
        return await self.get_min_stars()

    async def set_post_min_stars(self, value: int) -> None:
        await self.set("post_min_stars", str(int(value)))

    async def get_min_stars(self) -> int:
        try:
            return int(float(await self.get("min_stars", "50")))
        except ValueError:
            return 50

    async def set_min_stars(self, value: int) -> None:
        await self.set("min_stars", str(int(value)))

    async def bot_active(self) -> bool:
        return (await self.get("bot_active", "1")) == "1"

    async def set_bot_active(self, active: bool) -> None:
        await self.set("bot_active", "1" if active else "0")

    async def get_channel(self) -> tuple[str, str]:
        """(username, chat_id) qaytaradi."""
        ch = await self.get("channel", "")
        ch_id = await self.get("channel_id", "")
        return ch, ch_id

    async def set_channel(self, username: str, chat_id: str) -> None:
        await self.set("channel", username.lstrip("@"))
        await self.set("channel_id", chat_id)

    # --- Majburiy obuna: BIR NECHTA KANAL (JSON ro'yxat) ---
    # settings["channels"] = [{"username": "...", "chat_id": "..."}, ...]
    # Eski bitta kanal ham avtomatik tarzda qo'llab-quvvatlanadi.

    async def get_channels(self) -> list[tuple[str, str]]:
        """Barcha majburiy kanallarni (username, chat_id) ro'yxati sifatida qaytaradi."""
        raw = await self.get("channels", "")
        if raw:
            try:
                data = json.loads(raw)
                if isinstance(data, list):
                    out = []
                    for c in data:
                        if isinstance(c, dict) and c.get("username"):
                            out.append((str(c["username"]).lstrip("@"),
                                        str(c.get("chat_id") or "")))
                    if out:
                        return out
            except (json.JSONDecodeError, AttributeError, ValueError):
                pass
        ch, ch_id = await self.get_channel()
        return [(ch, ch_id)] if ch else []

    async def set_channels(self, channels: list[tuple[str, str]]) -> None:
        """Bir nechta majburiy kanallarni saqlaydi (ro'yxat bo'sh bo'lishi mumkin)."""
        data = [{"username": u.lstrip("@"), "chat_id": (c or "")} for u, c in channels if u]
        await self.set("channels", json.dumps(data))

    # --- Referal dasturi: referrer bonus (so'm, admin panel orqali) ---

    async def get_referral_bonus(self) -> float:
        try:
            return float(await self.get("referral_bonus", "0"))
        except ValueError:
            return 0.0

    async def set_referral_bonus(self, value: float) -> None:
        await self.set("referral_bonus", str(round(float(value), 2)))

    # --- To'lovlar kanali (barcha zakazlar joylashtiriladi) ---

    async def get_payment_channel(self) -> tuple[str, str]:
        """(username, chat_id) qaytaradi."""
        ch = await self.get("pay_channel", "")
        ch_id = await self.get("pay_channel_id", "")
        return ch, ch_id

    async def set_payment_channel(self, username: str, chat_id: str) -> None:
        await self.set("pay_channel", username.lstrip("@"))
        await self.set("pay_channel_id", chat_id)

    async def clear_payment_channel(self) -> None:
        await self.set("pay_channel", "")
        await self.set("pay_channel_id", "")

    async def payment_card(self) -> str:
        return await self.get("payment_card", "")

    async def set_payment_card(self, card: str) -> None:
        await self.set("payment_card", card)

    # --- Adminlar (DB'da saqlanadi, panel orqali boshqariladi) ---

    async def get_extra_admins(self) -> list[int]:
        """Panel orqali qo'shilgan qo'shimcha adminlar ID ro'yxati."""
        raw = await self.get("extra_admins", "")
        try:
            data = json.loads(raw) if raw else []
            return [int(x) for x in data]
        except (json.JSONDecodeError, ValueError):
            return []

    async def add_extra_admin(self, user_id: int) -> bool:
        """Yangi admin qo'shadi. Allaqachon bor bo'lsa False qaytaradi."""
        admins = await self.get_extra_admins()
        if user_id in admins:
            return False
        admins.append(user_id)
        await self.set("extra_admins", json.dumps(admins))
        return True

    async def remove_extra_admin(self, user_id: int) -> bool:
        """Adminni o'chiradi. Topilmasa False qaytaradi."""
        admins = await self.get_extra_admins()
        if user_id not in admins:
            return False
        admins = [x for x in admins if x != user_id]
        await self.set("extra_admins", json.dumps(admins))
        return True

    # --- Stars API (admin panel orqali o'rnatiladi) ---

    async def get_stars_api(self) -> tuple[str, str]:
        """(base_url, api_key) qaytaradi. O'rnatilmagan bo'lsa (\"\", \"\")."""
        url = await self.get("stars_api_base_url", "")
        key = await self.get("stars_api_key", "")
        return url, key

    async def set_stars_api(self, url: str, key: str) -> None:
        await self.set("stars_api_base_url", url.strip().rstrip("/"))
        await self.set("stars_api_key", key.strip())

    async def clear_stars_api(self) -> None:
        await self.set("stars_api_base_url", "")
        await self.set("stars_api_key", "")