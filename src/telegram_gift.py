# ===================================================================
# telegram_gift.py - TELEGRAM USER-SESSION ORQALI GIFT YETKAZISH
# Admin panelga ulangan Telegram akkaunt (Telethon StringSession)
# orqali @username / +telefon raqamiga haqiqiy gift yuboradi.
#   - payments.getStarGifts      -> qiymati (stars) to'g'ri keladigan gift
#   - InputInvoiceStarGift + GetPaymentFormRequest + SendStarsFormRequest
#                               -> gift yuborish (yangi Telegram API)
# Barqarorlik: har qanday xatoda False + asosli xabar qaytadi, bot
# o'zi ishlayveradi. Telethon importi lazy (yuklanish xatosiz).
# ===================================================================

from __future__ import annotations

import asyncio
import random
import re
import time as _time

# Telegram Desktop ommaviy identifikatorlari (API login uchun kerak).
_API_ID: int = 2040
_API_HASH: str = "b18441a1ff607e10a989891a5462e627"
_CONNECT_TIMEOUT: float = 20.0  # ulanish tiqilib qolmasligi uchun

# Post havolasi: t.me/username/123 yoki t.me/c/1234567890/123
_POST_LINK_RE = re.compile(
    r"(?:https?://)?(?:t\.me|telegram\.me)/"
    r"(?:s/)?(?:c/(?P<cid>\d+)|(?P<user>[A-Za-z0-9_]{3,32}))/(?P<mid>\d+)"
)

# Muqobil gift id'lar: agar getStarGifts javobida stars qiymati
# topilmasa, ushbu ma'lum qiymatlar bilan sendStarsGift chaqiriladi.
# Har bir value = giftning stars qiymati. (Kerak bo'lsa o'zingiz
# o'rnatasiz — real gift id lar Telegram serverdan dinamik keladi.)
FALLBACK_GIFT_IDS: dict[int, int] = {}


class TelegramGiftSender:
    """Bitta Telegram user-session orqali gift yetkazadi."""

    # JS Quirk: Telethon StringSession usa to'g'ri; faqatgina
    # generate-session orqali olingan string kutiladi.

    async def send(self, session_string: str, amount: int,
                   recipient: str, kind: str = "phone") -> tuple[bool, str]:
        """
        recipient: "@username" yoki "+998901234567"
        Qaytaradi: (ok, message). message error yoki "ok".
        """
        from telethon import TelegramClient
        from telethon.errors import ForbiddenError
        from telethon.sessions import StringSession
        from telethon.tl import functions as _f
        from telethon.tl import types as _t

        session = (session_string or "").strip()
        if not session:
            return False, "empty_session"
        if len(session) < 40 or " " in session:
            return False, "invalid_session_string"

        try:
            parsed_session = StringSession(session)
        except ValueError:
            return False, "invalid_session_string"

        client = TelegramClient(
            parsed_session,
            _API_ID,
            _API_HASH,
            device_model="StarsBot",
            system_version="Windows 10",
            app_version="stars-bot 1.0",
            lang_code="en",
        )
        try:
            await asyncio.wait_for(client.connect(), timeout=_CONNECT_TIMEOUT)
            if not await client.is_user_authorized():
                return False, "session_not_authorized"

            # 1) Qabul qiluvchini yechish (@username yoki +telefon)
            try:
                peer = await client.get_input_entity(recipient.strip())
            except Exception:  # noqa: BLE001
                return False, f"recipient_not_found ({recipient.strip()})"

            # 2) Qiymatga to'g'ri keladigan gift id ni izlash
            gift_id = await self._find_gift_id(client, amount)
            if gift_id is None:
                return False, f"gift_not_found_for_{amount}_stars"

            # 3) Yangi Telegram API oqimi: form yaratish + to'lash.
            #    Eski SendStarsGiftRequest o'rniga InputInvoiceStarGift +
            #    GetPaymentFormRequest + SendStarsFormRequest ishlatiladi.
            invoice = _t.InputInvoiceStarGift(peer=peer, gift_id=gift_id)
            form = await client(_f.payments.GetPaymentFormRequest(invoice=invoice))
            form_id = getattr(form, "form_id", None)
            if not form_id:
                return False, "no_payment_form_id"
            try:
                await client(_f.payments.SendStarsFormRequest(
                    form_id=form_id, invoice=invoice
                ))
            except (TypeError, ValueError) as exc:  # noqa: BLE001
                return False, f"send_stars_gift_api_not_supported: {type(exc).__name__}: {exc}"
            await client.disconnect()
            return True, "ok"
        except ForbiddenError:
            return False, "gift_restricted_by_telegram"
        except Exception as exc:  # noqa: BLE001
            return False, f"{type(exc).__name__}: {exc}"

    async def _find_gift_id(self, client, amount: int) -> int | None:
        from telethon.tl import functions as _f

        try:
            res = await client(_f.payments.GetStarGiftsRequest(hash=0))
            for g in getattr(res, "gifts", []) or []:
                if getattr(g, "stars", None) == amount:
                    return g.id
        except Exception:  # noqa: BLE001
            pass
        # Zaxira: ma'lum qiymatlar jadvali
        return FALLBACK_GIFT_IDS.get(amount)

    async def send_post_stars(
        self, session_string: str, amount: int, post_link: str
    ) -> tuple[bool, str]:
        """
        Postga stars (paid reaction) qo'yish.
        post_link: "https://t.me/username/123" yoki t.me/c/...
        Qaytaradi: (ok, message).
        """
        from telethon import TelegramClient
        from telethon.errors import ForbiddenError
        from telethon.sessions import StringSession
        from telethon.tl import functions as _f

        session = (session_string or "").strip()
        if not session:
            return False, "empty_session"
        if len(session) < 40 or " " in session:
            return False, "invalid_session_string"

        m = _POST_LINK_RE.search(post_link or "")
        if not m:
            return False, "bad_post_link"
        msg_id = int(m.group("mid"))
        cid = m.group("cid")
        username = m.group("user")

        try:
            parsed_session = StringSession(session)
        except ValueError:
            return False, "invalid_session_string"

        client = TelegramClient(
            parsed_session,
            _API_ID,
            _API_HASH,
            device_model="StarsBot",
            system_version="Windows 10",
            app_version="stars-bot 1.0",
            lang_code="en",
        )
        try:
            await asyncio.wait_for(client.connect(), timeout=_CONNECT_TIMEOUT)
            if not await client.is_user_authorized():
                return False, "session_not_authorized"

            # Peer ni aniqlash: username yoki kanal id
            if cid:
                # t.me/c/<id>/<msg> shakli: id -> negative channel id.
                # Telethon kanalni session keshidan yoki GetChannels orqali topadi.
                peer = await client.get_input_entity(-1000000000000 - int(cid))
            else:
                peer = await client.get_input_entity(username)
            random_id = ((int(_time.time()) << 32) | random.getrandbits(32)) & 0xFFFFFFFFFFFFFFFF
            try:
                await client(_f.messages.SendPaidReactionRequest(
                    peer=peer, msg_id=msg_id, count=int(amount),
                    random_id=random_id,
                ))
            except (TypeError, ValueError) as exc:  # noqa: BLE001
                return False, f"send_post_stars_api_not_supported: {type(exc).__name__}: {exc}"
            await client.disconnect()
            return True, "ok"
        except ForbiddenError:
            return False, "post_stars_restricted"
        except Exception as exc:  # noqa: BLE001
            try:
                await client.disconnect()
            except Exception:  # noqa: BLE001
                pass
            return False, f"{type(exc).__name__}: {exc}"

    async def test_session(self, session_string: str) -> tuple[bool, str]:
        """Akkaunt bunga ulanish + get_me orqali tekshirish."""
        from telethon import TelegramClient
        from telethon.sessions import StringSession

        session = (session_string or "").strip()
        if not session:
            return False, "empty_session"
        # StringSession minimal uzunlik (~3 baz64 token). Qisqa/noto'g'ri
        # qiymat Telethon'da ValueError tashlaydi — oldin ushlab olamiz.
        if len(session) < 40 or " " in session:
            return False, "invalid_session_string"
        client = TelegramClient(
            StringSession(session),
            _API_ID,
            _API_HASH,
            device_model="StarsBot",
            system_version="Windows 10",
            app_version="stars-bot 1.0",
            lang_code="en",
        )
        try:
            # Timeout: ulanish bloklanda (firewall/proxy) hech qachon
            # "tekshirilmoqda" holatida qotib qolmaydi.
            await asyncio.wait_for(client.connect(), timeout=_CONNECT_TIMEOUT)
            if not await client.is_user_authorized():
                return False, "session_not_authorized"
            me = await asyncio.wait_for(client.get_me(), timeout=_CONNECT_TIMEOUT)
            await client.disconnect()
            return True, f"@{me.username or 'no-username'} (id={me.id})"
        except asyncio.TimeoutError:
            try:
                await client.disconnect()
            except Exception:  # noqa: BLE001
                pass
            return False, "timeout: telegram serverga ulanib bo'lmadi (20s)"
        except Exception as exc:  # noqa: BLE001
            try:
                await client.disconnect()
            except Exception:  # noqa: BLE001
                pass
            return False, f"{type(exc).__name__}: {exc}"