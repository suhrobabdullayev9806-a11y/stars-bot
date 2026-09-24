#!/usr/bin/env bash
# ===================================================================
# run_bot.sh - botni 24/7 avtomatik ushlab turadi (systemd/olalar uchun)
#
# Loop:
#   1. cloudflared tunnel ochadi (http://127.0.0.1:8080 -> https)
#   2. URL ni .env dagi WEBAPP_BASE_URL ga yozadi
#   3. WEBAPP_BASE_URL o'zgarsa botni docker compose restart qiladi
#   4. Tunnel tushsa qayta ochadi
#
# Ushbu skriptni systemd yoki crontab (stdout) orqali yurgazing.
# ===================================================================
set -uo pipefail
cd "$(dirname "$0")/.."

TUNNEL_LOG="$(mktemp)"
TUNNEL_PID=""
BOT_READY_URL=""

cleanup() {
  [ -n "$TUNNEL_PID" ] && kill "$TUNNEL_PID" 2>/dev/null || true
}
trap cleanup EXIT

start_tunnel() {
  nohup cloudflared tunnel --url http://127.0.0.1:8080 >"$TUNNEL_LOG" 2>&1 &
  TUNNEL_PID=$!
}

wait_url() {
  for _ in $(seq 1 30); do
    URL="$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$TUNNEL_LOG" | head -n1 || true)"
    [ -n "$URL" ] && { echo "$URL"; return 0; }
    if ! kill -0 "$TUNNEL_PID" 2>/dev/null; then
      echo ""; return 1
    fi
    sleep 1
  done
  echo ""; return 1
}

while true; do
  # Bot ishlamayotgan bo'lsa ham tunnel birinchi ochiladi
  start_tunnel
  URL="$(wait_url)"
  if [ -n "$URL" ]; then
    echo "[run_bot] Tunnel: $URL"

    # .env dagi WEBAPP_BASE_URL ni yangilash
    if grep -qE '^WEBAPP_BASE_URL=' .env; then
      sed -i "s|^WEBAPP_BASE_URL=.*|WEBAPP_BASE_URL=$URL|" .env
    else
      echo "WEBAPP_BASE_URL=$URL" >> .env
    fi

    # URL o'zgarsa botni qayta ishga tushirish (tugma endi to'g'ri URL da)
    if [ "$URL" != "$BOT_READY_URL" ]; then
      BOT_READY_URL="$URL"
      echo "[run_bot] WEBAPP_BASE_URL o'zgardi ($URL) -> bot recreate"
      # Image yo'q bo'lsa avtomatik build, mavjud bo'lsa faqat recreate
      docker compose up -d 2>&1 | tail -n 3 || true
    fi
  else
    echo "[run_bot] Tunnel URL olinmadi, qayta urinish 5s..."
  fi

  # Tunnel tushguncha kutamiz
  while kill -0 "$TUNNEL_PID" 2>/dev/null; do sleep 3; done
  echo "[run_bot] Tunnel tushdi, qayta ochilmoqda..."
  sleep 3
done