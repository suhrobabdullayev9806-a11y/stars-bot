# Oracle Cloud Free Tier'da botni ishga tushirish — amaliy qo'llanma

Bu qo'llanma `@xamidovgiftbot` (stars-bot) loyihasini Oracle Cloud Free Tier
VPS'ida 24/7 ishga tushirish uchun.

> Narx: **0 so'm.** Oracle Free Tier doimiy bepul (Always Free):
> ARM A1 (4 OCPU / 24 GB RAM) yoki 2 ta AMD Micro VPS.

---

## 1-qadam: Oracle Cloud hisobini ochish

1. `https://cloud.oracle.com` — **Sign up** tugmasi
2. "Sign up for Oracle Cloud" bosqichlarini to'ldiring (Google akkaunti shart emas,
   oddiy e-mail yetarli)
3. Karta kiritish so'raladi — bu **faqat tekshirish** uchun, pul **olinmaydi**
   (faqat qaytarilmaydigan $1 band qilinib qaytariladi)
4. SMS/hisob tasdiqlashdan keyin **Home Region** ni tanlang (masalan: Uae North / Seoul)
5. Kirish: `https://cloud.oracle.com` → **Sign in to Cloud**

---

## 2-qadam: VPS (Compute Instance) yaratish

1. Yuqorida menyu: **☰ → Compute → Instances**
2. **Create instance**
3. Sozlamalar:
   - **Name:** `stars-bot`
   - **Placement/Shape:** default qoldiring, ARM Free tier taklif qilinadi
   - **Image:** Ubuntu 22.04 (yoki 24.04)
   - **SSH keys:** "Generate a key pair" → 2 fayl yuklab olinadi
     (private key = sizda qoladi, public key VPS'ga kiradi)
   - **Boot volume:** default (boot volume har doim bepul)
4. **Create**

5. VPS yaratilgach, ro'yxatda **Public IP address** ko'rinadi (masalan `193.123.45.67`).
   Shu IP'ni va private key (`openssh_key`) fayli qayerdaligini yozib oling.

---

## 3-qadam: Microsoft Windows'da VPS'ga ulanish

Private key `openssh_key` fayli odatda Downloads'da bo'ladi. Uni biror papkaga,
masalan `C:\Users\user\.ssh\oracle_key` deb ko'chiring:

```powershell
mkdir -p $HOME\.ssh
Copy-Item "$HOME\Downloads\openssh_key" "$HOME\.ssh\oracle_key" -Force
```

Keyin ulaning (IP ni o'zingiznikiga almashtring):

```powershell
ssh -i $HOME\.ssh\oracle_key ubuntu@193.123.45.67
```

> ARM'da Ubuntu foydalanuvchisi `ubuntu`; AMD Micro'da ham `ubuntu` bo'ladi.

---

## 4-qadam: Kodni VPS'ga ko'chirish

Loyihani **ikkita yo'l** bilan yuborish mumkin:

### A) scp orqali (localsdan)

Windows PowerShell'da (bot loyihangiz papkasidan):

```powershell
scp -i $HOME\.ssh\oracle_key -r "C:\Users\user\Documents\Default Project\stars-bot" ubuntu@193.123.45.67:~/stars-bot
```

> .env (maxfiy fayl) ham ko'chiriladi — SHUNING uchun bu eng to'g'ri yo'l.
> venv papkasi VPS'da kerak emas, uni istisno qilish uchun:

```powershell
scp -i $HOME\.ssh\oracle_key -r src ubuntu@193.123.45.67:~/stars-bot/
scp -i $HOME\.ssh\oracle_key -r assets ubuntu@193.123.45.67:~/stars-bot/
scp -i $HOME\.ssh\oracle_key .env .env.example Dockerfile docker-compose.yml requirements.txt ubuntu@193.123.45.67:~/stars-bot/
```

### B) GitHub orqali (majburiy emas)

Kod GitHub'da bo'lsa, VPS'da `git clone` qilish yanada qulay.

---

## 5-qadam: VPS'da o'rnatish va ishga tushirish

VPS'ga SSH bilan kirilgan bo'lsangiz:

```bash
cd ~/stars-bot
chmod +x deploy/*.sh
sudo bash deploy/setup.sh
```

Skript avtomatik:
- Docker va cloudflared o'rnatadi
- `.env` dagi tokenlarni tekshiradi
- Botni `docker compose` orqali ishga tushiradi

Keyin **24/7 avtomatik** qilish uchun systemd yozamiz (VPS qayta ishga
tushsa ham bot o'z-o'zidan boshlanadi, tunnel URL o'zgarsa avtomatik
yangilanadi):

```bash
sudo cp deploy/stars-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now stars-bot
```

`stars-bot.service` ichida `deploy/run_bot.sh` ishlaydi — u cloudflared
tunnel ochadi, WEBAPP_BASE_URL ni topadi, `.env` ga yozadi va botni
`docker compose` da ishga tushiradi. Tunnel tushsa qayta ochadi.

---

## 6-qadam: Tekshirish

```bash
sudo systemctl status stars-bot     # active (running) bo'lishi kerak
docker compose ps                   # bot Running bo'lishi kerak
docker compose logs --tail 30 bot
ss -tlnp | grep 8080                # 8080 port quloq solayotgani
journalctl -u stars-bot -f          # run_bot loglari (tunnel URL ko'rinadi)
```

**Muhim:** Quick tunnel URL (trycloudflare.com) — o'z jarayoni qayta
boshlansa URL o'zgaradi. Shuning uchun `deploy/run_bot.sh` (yuqoridagi
systemd) botni avtomatik yangilab turadi.

---

## Eslatmalar

- **Oracle firewall:** Oracle Cloud'da "Security List" ichida 8080 (http)
  portini ochishingiz shart emas — bot chetga chiqadi, kiruvchi 80/443 faqat
  tunnel uchun emas (cloudflared o'zi outbound ulanyapti).
- **Mini-App tugmasi:** `WEBAPP_BASE_URL` o'zgarganda bot avtomatik restart
  bo'ladi, tugma yangi URL'ga ishora qiladi. Telegram WebApp tugmasi yangi
  session boshlanganda ko'rinadi.
- **Ma'lumotlar bazasi:** `data/stars.db` Docker volume orqali `./data` da
  saqlanadi — VPS'da ko'chirilgan bo'lsa davom etadi.
- Muammo bo'lsa: `docker compose logs --tail 100 bot`