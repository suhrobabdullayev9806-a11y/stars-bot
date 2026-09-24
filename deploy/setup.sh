#!/usr/bin/env bash
# ===================================================================
# setup.sh - Oracle Cloud Free Tier VPS'da botni ishga tushirish
#
# Bo'lishi kerak:
#   - Ubuntu 22.04/24.04 ARM yoki x86 (Oracle Free Tier: ARM A1 bepul)
#   - SSH orqali kirilgan
#   - Loyiha papkasi ~/stars-bot ga yuklangan (scp orqali)
#
# Ishga tushirish:
#   cd ~/stars-bot/deploy && sudo bash setup.sh
# ===================================================================
set -euo pipefail

LOG_TAG="[stars-bot]"
say()  { echo "$LOG_TAG $*"; }
fail() { echo "$LOG_TAG XATO: $*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || fail "sudo bilan ishga tushiring: sudo bash setup.sh"

cd "$(dirname "$0")/.."
say "Loyiha papkasi: $(pwd)"

# ---------------------------------------------------------------
# 1) Muhit fayli
# ---------------------------------------------------------------
if [ ! -f .env ]; then
  cp .env.example .env
  say "⚠  .env fayli .env.example dan yaratildi — BOT_TOKEN, ADMIN_IDS ni sozlang!"
  say "    keyin:  nano .env  (saqlash: Ctrl+O, chiqish: Ctrl+X)"
  fail ".env faylini to'ldirib qayta ishga tushiring"
fi
grep -qE '^BOT_TOKEN=.+:.+' .env || fail "BOT_TOKEN .env da noto'g'ri"

# ---------------------------------------------------------------
# 2) Docker o'rnatish (agar yo'q bo'lsa)
# ---------------------------------------------------------------
if ! command -v docker >/dev/null 2>&1; then
  say "Docker o'rnatilmoqda..."
  apt-get update -y
  apt-get install -y ca-certificates curl gnupg
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
    > /etc/apt/sources.list.d/docker.list
  apt-get update -y
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
fi
docker --version

# ---------------------------------------------------------------
# 3) cloudflared (HTTPS tunnel — mini-app uchun)
# ---------------------------------------------------------------
if ! command -v cloudflared >/dev/null 2>&1; then
  say "cloudflared o'rnatilmoqda..."
  curl -fsSL -o /usr/local/bin/cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-$(dpkg --print-architecture)
  chmod +x /usr/local/bin/cloudflared
fi
cloudflared --version

# ---------------------------------------------------------------
# 4) Botni docker compose orqali ishga tushirish
# ---------------------------------------------------------------
say "Bot ishga tushyapti (docker compose)..."
docker compose up -d --build

sleep 5
if docker compose ps bot --format '{{.State}}' | grep -q running; then
  say "✅ Bot kontayneri ishlamoqda!"
else
  say "⚠  Bot kontayner xato bilan chiqdi. Loglarni ko'ring:"
  say "    docker compose logs --tail 50 bot"
fi

say "──────────────────────────────────────────────"
say "Endi 24/7 va avtomatik URL uchun systemd yoqing:"
say "    sudo cp deploy/stars-bot.service /etc/systemd/system/"
say "    sudo systemctl daemon-reload"
say "    sudo systemctl enable --now stars-bot"
say ""
say "systemd (deploy/run_bot.sh): tunnel ochadi, WEBAPP_BASE_URL ni"
say "avtomatik yangilab botni restart qiladi."
say "──────────────────────────────────────────────"