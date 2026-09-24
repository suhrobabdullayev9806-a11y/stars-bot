# ⭐ Auto Stars Telegram Bot

Telegram Stars (yulduzlar) sotib olish/gift/postga stars yuborish uchun to'liq, modulli va xavfsiz Telegram bot.

**Texnologiyalar:** Python 3.12 · aiogram 3 · SQLite (aiosqlite) · FastAPI WebApp · Docker · GitHub Actions · Pytest

---

## 📌 Funksiyalar

### Foydalanuvchi
- 🛒 Paketlar orqali Stars sotib olish (**15, 30, 50, 100**)
- 🔗 **API orqali avtomatik sotib olish** (`@Apilarimbot` — `src/api_client.py`)
- 📝 Rasim/matn yuborib **postga stars olish** (admin tasdiqi bilan)
- 🎁 **Gift olish/berish** — akkaunt ulansa avtomatik yetkaziladi
- 👛 **Hisob yuritish** — progress bar, sotilgan/sotib olingan stars, harakatlar tarixi
- 💳 To'lov: **karta** (ruchka) va **online API** (balansdan ham mumkin)
- 📢 **Majburiy obuna** (@channel) — obuna bo'lmasa bot ishlamaydi
- 🌐 **Multilingual** — O'zbekcha / English / Русский

### Admin panel (Telegram ichida + WebApp)
- 📦 Buyurtmalar: qabul qilish, rad etish, status
- 📝 Postga starsni tasdiqlash/bekor qilish
- 🎁 Gift qo'shish / ayirish
- 💲 Narxlar va foizni belgilash
- 🔑 Akkaunt ulash / o'chirish
- 📊 Sotuvlar statistikasi (kunlik / haftalik / oylik)
- 🔋 Botni ON/OFF qilish, kanal sozlash, reklama (broadcast), VIP

### Dizayn
- 🔴🟢🔵 3 rangli inline tugmalar (rangli emoji markerlar)
- Har paket uchun rasm (`assets/images/star_*.png`)
- Step-by-step: Paket → To'lov → Yetkazish · do'kon navigatsiyada orqaga tugmasi

---

## 📁 Tuzilma

```
stars-bot/
├── src/
│   ├── main.py            # ishga tushirish (polling + webapp)
│   ├── config.py          # .env sozlamalari (pydantic)
│   ├── database.py        # SQLite + SettingsRepo
│   ├── models.py          # pydantic modellar (validation)
│   ├── security.py        # admin auth, HMAC, sanitization
│   ├── i18n.py            # Uz/En/Ru tarjimalar
│   ├── keyboards.py       # rangli inline tugmalar
│   ├── utils.py           # progress bar, parse, format
│   ├── api_client.py      # @Apilarimbot API adapter
│   ├── modules/           # ⬅ biznes mantiq
│   │   ├── users.py       #    foydalanuvchilar + balans
│   │   ├── orders.py      #    buyurtmalar + stats
│   │   ├── payments.py    #    to'lovlar (karta/API/balans)
│   │   ├── gifts.py       #    giftlar
│   │   ├── accounts.py    #    akkauntlar (shifrlangan session)
│   │   └── admin.py       #    admin panel mantiqasi
│   ├── handlers/          # Telegram qayta ishlovchilar
│   └── webapp/            # FastAPI admin WebApp + API callback
├── assets/images/         # paket rasmlari (ozingiz almashtirasiz)
├── tools/generate_images.py
├── tests/                 # 31 unit test
├── Dockerfile
├── docker-compose.yml
├── .github/workflows/ci.yml
```

---

## 🚀 Ishga tushirish

### 1. Sozlash
```bash
cp .env.example .env
```
`.env` ichida:
- `BOT_TOKEN` — @BotFather'dan
- `ADMIN_IDS` / `SUPER_ADMIN_ID` — adminlar ID lari
- `REQUIRED_CHANNEL` — majburiy kanal (@belgisiz) + `REQUIRED_CHANNEL_ID` (botni kanalga admin qiling)
- `PAYMENTS_PROVIDER_TOKEN` — Stars (XTR) qabuli uchun (ixtiyoriy)
- `STARS_API_BASE_URL` / `STARS_API_KEY` — `@Apilarimbot` API (ixtiyoriy)

### 2. Lokal (Windows/Linux)
```bash
python -m venv venv
venv\Scripts\activate            # Windows  |  source venv/bin/activate
pip install -r requirements.txt
python tools/generate_images.py  # paket rasmlari
python -m src.main
```

### 3. Docker
```bash
docker compose up -d --build
# WebApp admin panel: http://localhost:8080/admin
```

---

## 📲 Botdan foydalanish

- `/start` → menyu · `/admin` → admin panel · `/lang` → til
- WebApp WebAdmin sahifasini Telegram orqali ochish uchun: BotFather → Menu button → `https://your-host/admin`

---

## 🧪 Testlar

```bash
pytest -q
```
CI (GitHub Actions) har push'da testlarni yuritadi va `ghcr.io` ga Docker tasvirini build qiladi.

---

## 🔌 API integratsiyasi (@Apilarimbot)

`src/api_client.py::StarsApiClient` — avtomatik sotib olish adapteri.

- `purchase()` — buyurtmani APIga yuboradi
- Provider'ingiz `POST /api/callback` ga qayta chaqiradi:
  ```json
  {"order_id": 1, "status": "done", "reference": "stars-1"}
  ```
  Header: `X-API-Signature: HMAC-SHA256(payload)` (kalit: `API_CALLBACK_SECRET`)
- Haqiqiy provider API spetsifikatsiyasiga moslash uchun `_call()` ni sozlang.

---

## 🛡 Xavfsizlik

- Admin huquqlar: `security.is_admin()` — hamma admin amallarda tekshiriladi
- API callback: `verify_callback_signature()` HMAC-SHA256
- WebApp: initData `WebAppData` HMAC tekshiruvi (24 soat)
- Aloqa tashqi API: HTTPX + timeout
- Akkaunt sessionlari: `sha256` bilan shifrlanib saqlanadi
- Kiruvchi matnlar: uzunlik/son cheklovlari, sanitization (`safe_text`, `safe_amount`)
- `.env` va `data/` gitdan himoyalangan (`.gitignore`)

---

## 📝 Eslatmalar

- Gift yetkazish va post ostidagi haqiqiy stars yuborish Telegram user-session (Telethon/Pyrogram) talab qiladi — `accounts.py::deliver_gift` nuqtasini o'z sessiyangiz bilan to'ldiring.
- Paket rasmlari `assets/images/star_{n}.png` — o'zingiznikiga osongina almashtiring.